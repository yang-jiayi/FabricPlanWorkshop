
(() => {
  "use strict";
  // Visual effects only. The guide works the same without this script.
  const root = document.documentElement;
  try {
    root.dataset.edition = document.querySelector(".slide[data-lab='facilitator']") ? "instructor" : "participant";
  } catch { /* The edition accent is decorative. */ }
  const calm = window.matchMedia("(prefers-reduced-motion: reduce)");
  const finePointer = window.matchMedia("(hover: hover) and (pointer: fine)");
  const bar = document.querySelector(".app-bar");

  // Two decorative elements: a soft light that follows the pointer, and a ring that spreads where the reader presses.
  const decoration = name => {
    const node = document.createElement("div");
    node.className = name;
    node.setAttribute("aria-hidden", "true");
    document.body.append(node);
    return node;
  };
  const spot = decoration("fx-spot");
  const ring = decoration("fx-ripple");

  // The light follows the pointer over the page; the hero, article banners and cards get their own highlight,
  // and the layers of the hero lean a little towards the pointer.
  const surfaces = ".home-hero, .slide-heading, .toc-card, .home-facts > div, .article-navigation button";
  let pointer = null;
  let pointerFrame = 0;
  document.addEventListener("pointermove", event => {
    if (event.pointerType === "touch") return;
    pointer = event;
    if (pointerFrame) return;
    pointerFrame = requestAnimationFrame(() => {
      pointerFrame = 0;
      const moving = !calm.matches;
      if (moving && finePointer.matches) {
        spot.style.translate = `${pointer.clientX}px ${pointer.clientY}px`;
        spot.classList.add("is-on");
      }
      const surface = pointer.target instanceof Element ? pointer.target.closest(surfaces) : null;
      if (!surface) return;
      const box = surface.getBoundingClientRect();
      surface.style.setProperty("--mx", `${Math.round(pointer.clientX - box.left)}px`);
      surface.style.setProperty("--my", `${Math.round(pointer.clientY - box.top)}px`);
      if (moving && box.width && box.height && surface.classList.contains("home-hero")) {
        surface.style.setProperty("--px", ((pointer.clientX - box.left) / box.width).toFixed(3));
        surface.style.setProperty("--py", ((pointer.clientY - box.top) / box.height).toFixed(3));
      }
    });
  }, {passive: true});
  root.addEventListener("pointerleave", () => spot.classList.remove("is-on"));
  document.querySelectorAll(".home-hero").forEach(hero => {
    hero.addEventListener("pointerleave", () => {
      hero.style.removeProperty("--px");
      hero.style.removeProperty("--py");
    });
  });

  // A ring spreads from the point where a link or a button is pressed.
  document.addEventListener("pointerdown", event => {
    if (calm.matches || event.button > 0 || !(event.target instanceof Element)) return;
    if (!event.target.closest("a, button, summary, select") || event.target.closest("dialog")) return;
    ring.classList.remove("is-on");
    ring.style.translate = `${event.clientX}px ${event.clientY}px`;
    void ring.offsetWidth; // Reading the size lets the animation start again.
    ring.classList.add("is-on");
  }, {passive: true});

  // The top bar gains depth once the page has been scrolled, and the line under it shows how far down the reader is.
  let scrollFrame = 0;
  const markScrolled = () => {
    scrollFrame = 0;
    root.classList.toggle("is-scrolled", window.scrollY > 12);
    if (!bar) return;
    const range = root.scrollHeight - window.innerHeight;
    bar.style.setProperty("--read", range > 0 ? Math.min(1, window.scrollY / range).toFixed(4) : "0");
  };
  const queueScrolled = () => {
    if (!scrollFrame) scrollFrame = requestAnimationFrame(markScrolled);
  };
  window.addEventListener("scroll", queueScrolled, {passive: true});
  window.addEventListener("resize", queueScrolled, {passive: true});
  window.addEventListener("hashchange", queueScrolled);
  markScrolled();

  // Articles arrive from the side the reader is heading to: from the right when moving on, from the left when going back.
  const scroller = document.getElementById("slide-scroller");
  if (scroller && "MutationObserver" in window) {
    let shown = scroller.querySelector(".slide:not([hidden])");
    new MutationObserver(() => {
      const next = scroller.querySelector(".slide:not([hidden])");
      if (!next || next === shown) return;
      const onward = !shown || Boolean(shown.compareDocumentPosition(next) & Node.DOCUMENT_POSITION_FOLLOWING);
      root.style.setProperty("--flow", onward ? "1" : "-1");
      shown = next;
    }).observe(scroller, {attributes: true, attributeFilter: ["hidden"], subtree: true});
  }

  // Colours cross-fade when the theme changes.
  let themeTimer = 0;
  if ("MutationObserver" in window) {
    new MutationObserver(() => {
      if (calm.matches) return;
      root.classList.add("is-theming");
      clearTimeout(themeTimer);
      themeTimer = setTimeout(() => root.classList.remove("is-theming"), 520);
    }).observe(root, {attributes: true, attributeFilter: ["data-theme"]});
  }

  // The lights of the hero rest while it is out of sight.
  if ("IntersectionObserver" in window) {
    const watcher = new IntersectionObserver(entries => {
      for (const entry of entries) entry.target.classList.toggle("is-away", !entry.isIntersecting);
    });
    document.querySelectorAll(".home-hero").forEach(hero => watcher.observe(hero));
  }

  // On a device that cannot keep the lights moving smoothly, the large ones rest so that reading and scrolling stay fluid.
  // Two samples of sixty frames must both be slow; frames skipped while the page is in the background do not count.
  const sample = pass => {
    if (calm.matches) return;
    const gaps = [];
    let last = 0;
    const frame = now => {
      if (last) gaps.push(now - last);
      last = now;
      if (gaps.length < 60) return void requestAnimationFrame(frame);
      gaps.sort((a, b) => a - b);
      if (gaps[15] <= 45) return;
      if (pass) root.classList.add("is-lite");
      else setTimeout(sample, 1500, 1);
    };
    requestAnimationFrame(frame);
  };
  window.addEventListener("load", () => setTimeout(sample, 2600, 0), {once: true});

  // Phones show the pressed state of links and cards only when a touch listener exists.
  document.addEventListener("touchstart", () => {}, {passive: true});

  // Keep the sticky side navigation aligned with the top bar when the bar wraps onto two rows.
  if (bar && "ResizeObserver" in window) {
    new ResizeObserver(() => {
      if (bar.offsetHeight) root.style.setProperty("--header", `${bar.offsetHeight}px`);
    }).observe(bar);
  }
})();
