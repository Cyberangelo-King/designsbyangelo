import { animate } from "framer-motion";

const reduced = window.matchMedia?.("(prefers-reduced-motion: reduce)").matches ?? false;
if (!reduced) {
  const orbit = document.querySelector(".orbit-one");
  if (orbit) animate(orbit, { rotate: [-24, 336] }, { duration: 48, ease: "linear", repeat: Infinity });
  const core = document.querySelector(".hero-object-core");
  if (core) animate(core, { y: [0, -10, 0], scale: [1, 1.035, 1] }, { duration: 7, ease: "easeInOut", repeat: Infinity });
  const hero = document.querySelector(".hero h1");
  if (hero) animate(hero, { opacity: [0, 1], y: [28, 0], filter: ["blur(8px)", "blur(0px)"] }, { duration: .9, ease: [.22, 1, .36, 1], delay: .12 });
  const reveal = (element, delay = 0) => animate(element, { opacity: [0, 1], y: [22, 0] }, { duration: .68, delay, ease: [.22, 1, .36, 1] });
  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(entries => entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      reveal(entry.target, Math.min(Number(entry.target.dataset.motionDelay || 0), .24));
      observer.unobserve(entry.target);
    }), { threshold: .12 });
    document.querySelectorAll("[data-reveal]").forEach((element, index) => {
      element.dataset.motionDelay = String((index % 5) * .045);
      observer.observe(element);
    });
  }
  document.documentElement.dataset.framerMotion = "ready";
}