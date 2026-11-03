(() => {
  "use strict";
  const slides = [...document.querySelectorAll(".slide")];
  const scroller = document.getElementById("slide-scroller");
  const toc = document.getElementById("toc-dialog");
  const stepsDialog = document.getElementById("steps-dialog");
  const imageDialog = document.getElementById("image-dialog");
  const helpDialog = document.getElementById("help-dialog");
  const search = document.getElementById("toc-search");
  const previous = document.getElementById("previous");
  const next = document.getElementById("next");
  let index = 0;
  let imageIndex = 0;
  let images = [];
  let imageScale = null;

  function closeDialogs() {
    document.querySelectorAll("dialog[open]").forEach(dialog => dialog.close());
  }

  function showSlide(nextIndex, focus = false) {
    index = Math.max(0, Math.min(nextIndex, slides.length - 1));
    const active = slides[index];
    slides.forEach(slide => { slide.hidden = slide !== active; });
    document.querySelectorAll("[data-chapter].chapter-link").forEach(link => {
      link.setAttribute("aria-current", String(link.dataset.chapter === active.dataset.lab));
    });
    document.getElementById("position-label").textContent =
      `SECTION ${String(index + 1).padStart(3, "0")} / ${slides.length}`;
    document.getElementById("progress-label").textContent = `${index + 1} / ${slides.length}`;
    document.getElementById("progress-fill").style.width = `${100 * (index + 1) / slides.length}%`;
    document.getElementById("progress-track").setAttribute("aria-valuenow", String(index + 1));
    document.getElementById("current-chapter").textContent =
      active.dataset.lab === "overview" ? "Overview" : active.dataset.lab.replace("lab", "Lab");
    document.getElementById("current-step").textContent = active.dataset.title;
    previous.disabled = index === 0;
    next.disabled = index === slides.length - 1;
    scroller.scrollTop = 0;
    document.title = `${active.dataset.title} — Microsoft Fabric Plan Workshop`;
    if (focus) active.querySelector("h1").focus({preventScroll: true});
  }

  function navigate(id, focus = true) {
    const found = slides.findIndex(slide => slide.id === id);
    if (found < 0) return false;
    closeDialogs();
    showSlide(found, focus);
    if (location.hash !== `#${id}`) history.pushState(null, "", `#${id}`);
    return true;
  }

  function openToc() {
    closeDialogs();
    toc.showModal();
    search.focus();
  }

  function openSteps() {
    const active = slides[index];
    const container = document.getElementById("step-list");
    container.replaceChildren();
    slides.filter(slide => slide.dataset.lab === active.dataset.lab).forEach(slide => {
      const link = document.createElement("a");
      link.href = `#${slide.id}`;
      link.textContent = slide.dataset.title;
      if (slide === active) link.setAttribute("aria-current", "step");
      container.append(link);
    });
    closeDialogs();
    stepsDialog.showModal();
    container.querySelector('[aria-current="step"]')?.scrollIntoView({block: "nearest"});
  }

  function showImage(nextIndex) {
    imageIndex = Math.max(0, Math.min(nextIndex, images.length - 1));
    const image = images[imageIndex];
    const zoom = document.getElementById("zoom-image");
    imageScale = null;
    zoom.onload = applyZoom;
    zoom.src = image.src;
    zoom.alt = image.alt;
    applyZoom();
    document.getElementById("image-caption").textContent = image.alt;
    document.getElementById("image-counter").textContent = `この手順の画像 ${imageIndex + 1} / ${images.length}`;
    document.getElementById("image-previous").disabled = imageIndex === 0;
    document.getElementById("image-next").disabled = imageIndex === images.length - 1;
  }

  function applyZoom() {
    const zoom = document.getElementById("zoom-image");
    const stage = zoom.parentElement;
    stage.classList.toggle("is-zoomed", imageScale !== null);
    if (imageScale === null) {
      zoom.style.removeProperty("width");
      zoom.style.removeProperty("max-width");
      zoom.style.removeProperty("max-height");
    } else {
      zoom.style.width = `${Math.round(zoom.naturalWidth * imageScale)}px`;
      zoom.style.maxWidth = "none";
      zoom.style.maxHeight = "none";
    }
    stage.scrollTop = 0;
    stage.scrollLeft = 0;
    document.getElementById("zoom-label").textContent =
      imageScale === null ? "全体表示" : `${Math.round(imageScale * 100)}% / 縦横にスクロール`;
    document.getElementById("image-fit").setAttribute("aria-pressed", String(imageScale === null));
    document.getElementById("image-actual").setAttribute("aria-pressed", String(imageScale === 1));
  }

  function setZoom(scale) {
    imageScale = scale === null ? null : Math.max(0.25, Math.min(3, scale));
    applyZoom();
  }

  document.addEventListener("click", event => {
    const target = event.target.closest("a, button");
    if (!target) return;
    if (target.matches('a[href^="#"]')) {
      const id = decodeURIComponent(target.getAttribute("href").slice(1));
      if (id === "main") return;
      if (navigate(id)) event.preventDefault();
    } else if (target.matches("[data-close-dialog]")) {
      target.closest("dialog").close();
    } else if (target.matches("[data-open-toc]")) {
      openToc();
    } else if (target.matches(".shot")) {
      images = [...slides[index].querySelectorAll(".shot img")];
      showImage(images.indexOf(target.querySelector("img")));
      imageDialog.showModal();
    }
  });
  previous.addEventListener("click", () => navigate(slides[index - 1]?.id));
  next.addEventListener("click", () => navigate(slides[index + 1]?.id));
  document.getElementById("toc-open").addEventListener("click", openToc);
  document.getElementById("steps-open").addEventListener("click", openSteps);
  document.getElementById("help-open").addEventListener("click", () => helpDialog.showModal());
  document.getElementById("image-previous").addEventListener("click", () => showImage(imageIndex - 1));
  document.getElementById("image-next").addEventListener("click", () => showImage(imageIndex + 1));
  document.getElementById("image-fit").addEventListener("click", () => setZoom(null));
  document.getElementById("image-actual").addEventListener("click", () => setZoom(1));
  document.getElementById("image-plus").addEventListener("click", () => setZoom((imageScale ?? 1) + 0.25));
  document.getElementById("image-minus").addEventListener("click", () => setZoom((imageScale ?? 1) - 0.25));
  document.getElementById("zoom-image").addEventListener("click", () => setZoom(imageScale === null ? 1 : null));
  document.getElementById("focus-toggle").addEventListener("click", event => {
    const focused = document.body.classList.toggle("focused");
    event.currentTarget.setAttribute("aria-pressed", String(focused));
    event.currentTarget.textContent = focused ? "通常表示" : "集中表示";
  });
  document.getElementById("theme-toggle").addEventListener("click", event => {
    const theme = document.documentElement.dataset.theme;
    const nextTheme = theme === "light" ? "dark" : theme === "dark" ? "" : "light";
    if (nextTheme) document.documentElement.dataset.theme = nextTheme;
    else delete document.documentElement.dataset.theme;
    event.currentTarget.textContent = `テーマ: ${{light: "明", dark: "暗", "": "自動"}[nextTheme]}`;
  });
  search.addEventListener("input", () => {
    const term = search.value.trim().toLocaleLowerCase();
    let matches = 0;
    toc.querySelectorAll(".toc-card").forEach(card => {
      const chapterMatch = (card.querySelector("h3").textContent + " " +
        card.querySelector(".toc-chapter").textContent).toLocaleLowerCase().includes(term);
      let stepMatches = 0;
      card.querySelectorAll("li").forEach(item => {
        item.hidden = !chapterMatch && !item.textContent.toLocaleLowerCase().includes(term);
        if (!item.hidden) stepMatches++;
      });
      card.hidden = stepMatches === 0;
      card.querySelector("details").open = Boolean(term) && !card.hidden;
      if (!card.hidden) matches++;
    });
    document.getElementById("toc-empty").hidden = matches > 0;
  });
  document.addEventListener("keydown", event => {
    const editable = event.target.closest('input, textarea, select, [contenteditable="true"]');
    if (event.altKey || event.ctrlKey || event.metaKey || editable) return;
    if (event.target.closest(".table-wrap, pre") &&
        ["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
    if (event.target.closest(".image-stage") && imageScale !== null &&
        ["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
    if (imageDialog.open && ["ArrowLeft", "ArrowRight"].includes(event.key)) {
      event.preventDefault();
      showImage(imageIndex + (event.key === "ArrowRight" ? 1 : -1));
      return;
    }
    if (document.querySelector("dialog[open]")) return;
    const routes = {
      ArrowLeft: index - 1, ArrowRight: index + 1, Home: 0, End: slides.length - 1,
    };
    if (Object.hasOwn(routes, event.key)) {
      event.preventDefault();
      navigate(slides[Math.max(0, Math.min(routes[event.key], slides.length - 1))].id);
    } else if (event.key.toLowerCase() === "t") {
      event.preventDefault();
      openToc();
    } else if (event.key === "?") {
      event.preventDefault();
      helpDialog.showModal();
    }
  });
  window.addEventListener("hashchange", () => {
    const found = slides.findIndex(slide => `#${slide.id}` === location.hash);
    if (found >= 0) { closeDialogs(); showSlide(found, true); }
  });
  document.querySelectorAll(".prose table").forEach(table => {
    const wrapper = document.createElement("div");
    wrapper.className = "table-wrap";
    wrapper.tabIndex = 0;
    wrapper.setAttribute("role", "region");
    wrapper.setAttribute("aria-label", "データ表 / 横スクロール可能");
    table.before(wrapper);
    wrapper.append(table);
  });
  const initial = slides.findIndex(slide => `#${slide.id}` === location.hash);
  showSlide(initial < 0 ? 0 : initial);
  document.documentElement.classList.add("js");
})();
