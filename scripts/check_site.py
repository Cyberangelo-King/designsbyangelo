from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import json
import posixpath
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
errors = []

def fail(message):
    errors.append(message)

required = [
    "index.html", "styles.css", "script.js", "framer-motion.js",
    "favicon.svg", "netlify.toml", "robots.txt", "sitemap.xml",
    "llms.txt", "site.webmanifest", "Angelo_Visual_Portfolio_2026.pdf",
    "assets/motion/angelo-orbit.json", "assets/og/angelo-social-card.svg",
]
for item in required:
    if not (ROOT / item).is_file():
        fail(f"Missing required file: {item}")

class PageParser(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.refs = []
        self.images_without_alt = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "img" and not values.get("alt", "").strip():
            self.images_without_alt.append(self.path)
        for attr in ("src", "href"):
            value = values.get(attr, "")
            if value:
                self.refs.append(value)

html_files = sorted(ROOT.rglob("*.html"))
if len(html_files) != 11:
    fail(f"Expected 11 HTML pages, found {len(html_files)}")

for path in html_files:
    rel = path.relative_to(ROOT).as_posix()
    parser = PageParser(rel)
    try:
        parser.feed(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"HTML parse failed for {rel}: {exc}")
        continue
    for missing in parser.images_without_alt:
        fail(f"Image missing alt text in {missing}")
    for value in parser.refs:
        parts = urlsplit(value)
        if parts.scheme or value.startswith("//") or not parts.path:
            continue
        raw = parts.path.lstrip("/") if parts.path.startswith("/") else posixpath.join(posixpath.dirname(rel), parts.path)
        target = posixpath.normpath(raw)
        if target == "." or target.endswith("/"):
            target = posixpath.join(target, "index.html")
        elif not posixpath.splitext(target)[1]:
            target = posixpath.join(target, "index.html")
        if not (ROOT / target).is_file():
            fail(f"Broken local reference in {rel}: {value} -> {target}")

work_pages = list((ROOT / "work").glob("*/index.html"))
work_art = list((ROOT / "assets/work").glob("*.svg"))
study_art = list((ROOT / "assets/studies").glob("*.svg"))
if len(work_pages) != 10:
    fail(f"Expected 10 case-study pages, found {len(work_pages)}")
if len(work_art) != 10:
    fail(f"Expected 10 selected-work vectors, found {len(work_art)}")
if len(study_art) != 20:
    fail(f"Expected 20 visual-study vectors, found {len(study_art)}")

for path in [*work_art, *study_art, ROOT / "favicon.svg", ROOT / "assets/og/angelo-social-card.svg"]:
    try:
        ET.parse(path)
    except Exception as exc:
        fail(f"Invalid SVG: {path.relative_to(ROOT)} ({exc})")

for rel in ["site.webmanifest", "assets/motion/angelo-orbit.json", "docs/rate-card.json", "docs/portfolio-inventory.json"]:
    path = ROOT / rel
    if path.exists():
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            fail(f"Invalid JSON: {rel} ({exc})")

try:
    ET.parse(ROOT / "sitemap.xml")
except Exception as exc:
    fail(f"Invalid XML: sitemap.xml ({exc})")

index = (ROOT / "index.html").read_text(encoding="utf-8")
styles = (ROOT / "styles.css").read_text(encoding="utf-8")
framer = (ROOT / "framer-motion.js").read_text(encoding="utf-8")
if "framer-motion@12.23.24" not in index:
    fail("Framer Motion version is not pinned in the import map")
if "prefers-reduced-motion" not in styles:
    fail("Missing reduced-motion CSS fallback")
if 'import { animate } from "framer-motion"' not in framer:
    fail("Framer Motion progressive-enhancement module is missing")
if "Terms and conditions apply" not in index:
    fail("Missing terms-and-conditions notice on the website")
if not (ROOT / ".gitignore").is_file() or ".netlify/" not in (ROOT / ".gitignore").read_text(encoding="utf-8"):
    fail("Missing .netlify/ ignore rule")

pdf = (ROOT / "Angelo_Visual_Portfolio_2026.pdf").read_bytes()
if not pdf.startswith(b"%PDF-"):
    fail("Portfolio download is not a PDF")
pdf_text = pdf.decode("latin-1", errors="ignore")
if "/Count 31" not in pdf_text:
    fail("Portfolio PDF should contain 31 pages")
if "TERMS AND CONDITIONS APPLY" not in pdf_text:
    fail("PDF rate card is missing the terms-and-conditions note")

if errors:
    print("Portfolio integrity check FAILED:")
    for error in errors:
        print(f" - {error}")
    sys.exit(1)

print(f"PASS: {len(html_files)} HTML pages; {len(work_pages)} case studies; {len(work_art) + len(study_art)} SVG artworks.")
print("PASS: local references, alt text, JSON, XML, PDF, USD terms, motion and Netlify configuration.")
