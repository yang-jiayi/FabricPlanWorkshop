(() => {
  "use strict";
  const $ = id => document.getElementById(id);
  const allSlides = [...document.querySelectorAll(".slide")];
  let language = "ja";
  try { language = localStorage.getItem("fabric-workshop-language") === "en" ? "en" : "ja"; } catch { /* The guide also works without storage. */ }
  if (location.hash) language = location.hash.startsWith("#en-") ? "en" : "ja";
  let slides = allSlides.filter(slide => slide.dataset.language === language);
  const translations = JSON.parse($("ui-translations").textContent);
  const english = () => language === "en";
  const ui = text => english() ? translations[text] || text : text;
  const chapterMarkup = {ja: document.querySelector(".chapter-list").innerHTML,
    en: $("english-chapters").innerHTML};
  const chromeText = [];
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (walker.nextNode()) {
    const node = walker.currentNode;
    if (!node.parentElement.closest(".slide, script, style, .chapter-list, select") &&
        Object.hasOwn(translations, node.textContent.trim())) chromeText.push([node, node.textContent]);
  }
  const chromeAttributes = [];
  document.querySelectorAll("[aria-label], [placeholder], meta[name='description']").forEach(element => {
    if (element.closest(".slide")) return;
    for (const name of ["aria-label", "placeholder", "content"]) {
      const value = element.getAttribute(name);
      if (value && Object.hasOwn(translations, value)) chromeAttributes.push([element, name, value]);
    }
  });
  function applyChrome() {
    document.documentElement.lang = language;
    $("language-select").value = language;
    chromeText.forEach(([node, original]) => {
      node.textContent = original.replace(original.trim(), ui(original.trim()));
    });
    chromeAttributes.forEach(([element, name, original]) => element.setAttribute(name, ui(original)));
    document.querySelectorAll(".utility-nav a, .outline-index, .brand-lockup, .workshop-name, .skip-link").forEach(link => {
      const article = link.getAttribute("href").replace(/^#(?:en-)?/, "");
      if (article !== "main") link.href = `#${english() ? "en-" : ""}${article}`;
    });
  }
  const searchDialog = $("search-dialog");
  const searchInput = $("global-search-input");
  const imageDialog = $("image-dialog");
  const sidebar = $("sidebar");
  const normalize = value => value.normalize("NFKC").toLocaleLowerCase("ja");
  const termsFor = value => [...new Set(normalize(value).trim().split(/\s+/).filter(Boolean))];
  const labName = lab => lab === "overview" ? ui("概要") : lab.replace("lab", "Lab");
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  let index = 0;
  let searchTerms = [];
  let highlightedArticle = null;
  let results = [];
  let selectedResult = -1;
  let imageIndex = 0;
  let images = [];
  let imageScale = null;
  let payloads;
  let payloadError;
  let headings = [];
  let outlineLinks = [];
  let scrollPending = false;
  let searchTimer;

  function reportImageError(image, message) {
    if (!image.dataset.loadError) {
      image.dataset.loadError = message;
      console.error(message, image.dataset.image);
      const notice = document.createElement("span");
      notice.className = "image-load-error";
      notice.setAttribute("role", "alert");
      notice.textContent = message;
      const container = image.closest(".shot-wrap") || image.parentElement;
      container.append(notice);
    }
    return "";
  }

  function imageSource(image) {
    if (image.dataset.image) {
      if (payloadError) return reportImageError(image, payloadError);
      if (payloads === undefined) {
        try {
          const registry = $("image-payloads");
          if (!registry) throw new Error(english() ? "The image registry is missing." : "画像レジストリがありません。");
          payloads = JSON.parse(registry.textContent);
          if (!payloads || typeof payloads !== "object" || Array.isArray(payloads)) {
            throw new Error(english() ? "The image registry format is invalid." : "画像レジストリの形式が正しくありません。");
          }
        } catch (error) {
          payloadError = english() ? `Cannot display the screenshot. The image registry could not be read: ${error.message}` : `画像を表示できません。画像レジストリの読み込みに失敗しました: ${error.message}`;
          return reportImageError(image, payloadError);
        }
      }
      const source = Object.hasOwn(payloads, image.dataset.image) ? payloads[image.dataset.image] : undefined;
      if (typeof source !== "string" || !/^data:image\/[a-z0-9.+-]+[;,]/i.test(source)) {
        return reportImageError(image, english() ? "Cannot display the screenshot. Image data is missing or invalid." : "画像を表示できません。指定された画像データが存在しないか, 形式が正しくありません。");
      }
      return source;
    }
    const source = image.getAttribute("src");
    return source || reportImageError(image, english() ? "Cannot display the screenshot. Its reference is missing." : "画像を表示できません。画像の参照がありません。");
  }

  function loadImage(image) {
    if (image.hasAttribute("src")) return;
    const source = imageSource(image);
    if (source) image.src = source;
  }

  const imageObserver = "IntersectionObserver" in window
    ? new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          loadImage(entry.target);
          imageObserver.unobserve(entry.target);
        }
      });
    }, {rootMargin: "400px 0px"}) : null;
  document.querySelectorAll(".step-image").forEach(image => {
    image.addEventListener("error", () => reportImageError(image, english() ? "Cannot load the image data. Download the HTML file again." : "画像データを読み込めません。HTMLファイルを再取得してください。"));
    if (imageObserver) imageObserver.observe(image);
  });

  function setNav(open, restoreFocus = false) {
    document.body.classList.toggle("nav-open", open);
    $("nav-toggle").setAttribute("aria-expanded", String(open));
    $("nav-scrim").hidden = !open;
    if (open) $("nav-close").focus();
    else if (restoreFocus) $("nav-toggle").focus();
  }

  function closeDialogs() {
    document.querySelectorAll("dialog[open]").forEach(dialog => dialog.close());
  }

  function openDialog(dialog) {
    closeDialogs();
    setNav(false);
    dialog.showModal();
  }

  function buildChapterNavigation() {
    document.querySelector(".chapter-list").innerHTML = chapterMarkup[language];
    document.querySelectorAll(".chapter-list > .chapter-link").forEach((link, ordinal) => {
      const lab = link.dataset.chapter;
      const group = document.createElement("div");
      group.className = "chapter-group";
      group.dataset.lab = lab;
      const row = document.createElement("div");
      row.className = "chapter-row";
      const toggle = document.createElement("button");
      toggle.type = "button";
      toggle.className = "chapter-toggle";
      toggle.textContent = "+";
      toggle.setAttribute("aria-label", english() ? `Show ${labName(lab)} procedures` : `${labName(lab)}の手順を表示`);
      toggle.setAttribute("aria-expanded", "false");
      const sections = document.createElement("div");
      sections.className = "chapter-sections";
      sections.id = `chapter-sections-${ordinal}`;
      sections.hidden = true;
      toggle.setAttribute("aria-controls", sections.id);
      slides.filter(slide => slide.dataset.lab === lab && !["welcome", "workshop-index", "index"].includes(slide.dataset.article)).forEach(slide => {
        const item = document.createElement("a");
        item.className = "section-link";
        item.href = `#${slide.id}`;
        item.textContent = slide.dataset.title;
        sections.append(item);
      });
      link.before(group);
      row.append(link, toggle);
      group.append(row, sections);
      toggle.addEventListener("click", () => {
        sections.hidden = !sections.hidden;
        toggle.setAttribute("aria-expanded", String(!sections.hidden));
        toggle.textContent = sections.hidden ? "+" : "−";
      });
    });
  }

  function updateOutline() {
    const active = slides[index];
    headings = [...active.querySelectorAll(".prose h2, .prose h3")].filter(heading => !heading.closest("details:not([open])"));
    if (!headings.length) headings = [...active.querySelectorAll("h1")];
    const fragment = document.createDocumentFragment();
    outlineLinks = headings.map((heading, ordinal) => {
      if (!heading.id) heading.id = `${active.id}-heading-${ordinal}`;
      const link = document.createElement("a");
      link.href = `#${heading.id}`;
      link.textContent = heading.textContent;
      if (heading.tagName === "H3") link.className = "outline-nested";
      fragment.append(link);
      return link;
    });
    $("article-toc").replaceChildren(fragment);
    updateScrollspy();
  }

  function updateScrollspy() {
    let active = 0;
    headings.forEach((heading, ordinal) => {
      if (heading.getBoundingClientRect().top <= 130) active = ordinal;
    });
    outlineLinks.forEach((link, ordinal) => {
      if (ordinal === active) link.setAttribute("aria-current", "location");
      else link.removeAttribute("aria-current");
    });
  }

  function updateBreadcrumbs(active) {
    const home = document.createElement("a");
    home.href = english() ? "#en-welcome" : "#welcome";
    home.textContent = ui("ホーム");
    const parts = [home];
    if (active.dataset.lab !== "overview") {
      const lab = document.createElement("a");
      lab.href = `#${slides.find(slide => slide.dataset.lab === active.dataset.lab).id}`;
      lab.textContent = labName(active.dataset.lab);
      parts.push(lab);
    }
    const current = document.createElement("span");
    current.textContent = active.dataset.article === "welcome" ? ui("ワークショップ") : active.dataset.title;
    current.setAttribute("aria-current", "page");
    parts.push(current);
    $("breadcrumbs").replaceChildren();
    parts.forEach((part, ordinal) => {
      if (ordinal) {
        const separator = document.createElement("span");
        separator.textContent = "/";
        separator.setAttribute("aria-hidden", "true");
        $("breadcrumbs").append(separator);
      }
      $("breadcrumbs").append(part);
    });
  }

  function showSlide(nextIndex, focus = false) {
    index = Math.max(0, Math.min(nextIndex, slides.length - 1));
    const active = slides[index];
    if (active.id !== highlightedArticle) searchTerms = [];
    allSlides.forEach(slide => { slide.hidden = slide !== active; });
    document.querySelectorAll(".chapter-link").forEach(link => {
      link.setAttribute("aria-current", String(link.dataset.chapter === active.dataset.lab));
    });
    document.querySelectorAll(".section-link, .utility-nav a").forEach(link => {
      if (link.hash === `#${active.id}`) link.setAttribute("aria-current", "page");
      else link.removeAttribute("aria-current");
    });
    const group = [...document.querySelectorAll(".chapter-group")].find(item => item.dataset.lab === active.dataset.lab);
    if (group && active.dataset.lab !== "overview") {
      group.querySelector(".chapter-sections").hidden = false;
      group.querySelector(".chapter-toggle").setAttribute("aria-expanded", "true");
      group.querySelector(".chapter-toggle").textContent = "−";
    }
    $("position-label").textContent = `${labName(active.dataset.lab)} / ${active.dataset.title}`;
    $("progress-label").textContent = `${index + 1} / ${slides.length}`;
    $("progress-fill").style.width = `${100 * (index + 1) / slides.length}%`;
    $("progress-track").setAttribute("aria-valuemax", String(slides.length));
    $("progress-track").setAttribute("aria-valuenow", String(index + 1));
    $("previous").disabled = index === 0;
    $("next").disabled = index === slides.length - 1;
    $("previous-title").textContent = slides[index - 1]?.dataset.title || ui("最初の記事です");
    $("next-title").textContent = slides[index + 1]?.dataset.title || ui("最後の記事です");
    document.title = `${active.dataset.title} — Microsoft Fabric Plan Workshop`;
    updateBreadcrumbs(active);
    updateOutline();
    applyArticleMarks();
    if (!imageObserver) active.querySelectorAll(".step-image").forEach(loadImage);
    window.scrollTo({top: 0, behavior: "instant"});
    if (focus) active.querySelector("h1")?.focus({preventScroll: true});
  }

  function navigate(id, focus = true) {
    if (!id) return false;
    const article = id.replace(/^en-/, "");
    id = (english() ? "en-" : "") + article;
    const target = document.getElementById(id);
    const slide = target?.closest(".slide");
    if (!slide) return false;
    const found = slides.indexOf(slide);
    closeDialogs();
    setNav(false);
    if (found !== index || target === slide) showSlide(found, focus);
    if (location.hash !== `#${id}`) history.pushState(null, "", `#${id}`);
    if (target !== slide) {
      let ancestor = target.parentElement;
      while (ancestor && ancestor !== slide) {
        if (ancestor.tagName === "DETAILS") ancestor.open = true;
        ancestor = ancestor.parentElement;
      }
      target.scrollIntoView({block: "start", behavior: reducedMotion.matches ? "instant" : "smooth"});
      if (focus) {
        if (!target.hasAttribute("tabindex")) target.tabIndex = -1;
        target.focus({preventScroll: true});
      }
    }
    return true;
  }

  function openSearch() {
    openDialog(searchDialog);
    searchInput.focus();
    searchInput.select();
  }

  function openSteps() {
    const container = $("step-list");
    container.replaceChildren();
    slides.filter(slide => slide.dataset.lab === slides[index].dataset.lab).forEach(slide => {
      const link = document.createElement("a");
      link.href = `#${slide.id}`;
      link.textContent = slide.dataset.title;
      if (slide === slides[index]) link.setAttribute("aria-current", "step");
      container.append(link);
    });
    openDialog($("steps-dialog"));
    container.querySelector('[aria-current="step"]')?.scrollIntoView({block: "nearest"});
  }

  // Keep normalized offsets connected to their original characters for full-width search hits.
  function markedText(text, terms, className = "") {
    const fragment = document.createDocumentFragment();
    const offsets = [];
    let folded = "";
    let position = 0;
    const characters = new Intl.Segmenter("ja", {granularity: "grapheme"}).segment(text);
    for (const {segment: character} of characters) {
      const part = normalize(character);
      for (let offset = 0; offset < part.length; offset++) offsets.push([position, position + character.length]);
      folded += part;
      position += character.length;
    }
    const ranges = [];
    terms.forEach(term => {
      let start = folded.indexOf(term);
      while (start !== -1) {
        const end = start + term.length - 1;
        if (offsets[start] && offsets[end]) ranges.push([offsets[start][0], offsets[end][1]]);
        start = folded.indexOf(term, start + Math.max(1, term.length));
      }
    });
    ranges.sort((a, b) => a[0] - b[0]);
    const merged = [];
    ranges.forEach(range => {
      const last = merged[merged.length - 1];
      if (last && range[0] <= last[1]) last[1] = Math.max(last[1], range[1]);
      else merged.push(range);
    });
    let cursor = 0;
    merged.forEach(([start, end]) => {
      fragment.append(text.slice(cursor, start));
      const mark = document.createElement("mark");
      mark.textContent = text.slice(start, end);
      if (className) mark.className = className;
      fragment.append(mark);
      cursor = end;
    });
    fragment.append(text.slice(cursor));
    return fragment;
  }

  function applyArticleMarks() {
    document.querySelectorAll("mark.article-hit").forEach(mark => mark.replaceWith(document.createTextNode(mark.textContent)));
    if (!searchTerms.length) return;
    const content = slides[index].querySelector(".prose") || slides[index];
    content.normalize();
    const walker = document.createTreeWalker(content, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        return node.parentElement.closest("button, script, style, mark, .code-label") ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT;
      },
    });
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach(node => {
      if (searchTerms.some(term => normalize(node.textContent).includes(term))) {
        node.replaceWith(markedText(node.textContent, searchTerms, "article-hit"));
      }
    });
  }

  let corpus = [];
  function rebuildCorpus() {
    corpus = slides.map((slide, ordinal) => {
      const body = (slide.querySelector(".prose") || slide).textContent.replace(/\s+/g, " ").trim();
      const title = slide.dataset.title;
      return {slide, ordinal, title, body, titleFolded: normalize(title), bodyFolded: normalize(body), lab: slide.dataset.lab};
    });
  }

  function setLanguage(nextLanguage, updateHistory = true) {
    if (!["ja", "en"].includes(nextLanguage)) throw new Error("Unsupported guide language");
    const article = slides[index].dataset.article;
    closeDialogs();
    setNav(false);
    language = nextLanguage;
    searchTerms = [];
    highlightedArticle = null;
    clearTimeout(searchTimer);
    searchTimer = null;
    document.querySelectorAll("mark.article-hit").forEach(mark => mark.replaceWith(mark.textContent));
    searchInput.value = "";
    $("search-results").replaceChildren();
    results = [];
    selectedResult = -1;
    searchInput.removeAttribute("aria-activedescendant");
    searchInput.setAttribute("aria-expanded", "false");
    $("nav-filter").value = "";
    $("nav-empty").hidden = true;
    slides = allSlides.filter(slide => slide.dataset.language === language);
    applyChrome();
    applyTheme($("theme-toggle").dataset.mode);
    $("search-status").textContent = ui("手順名または本文の語を入力してください。");
    buildChapterNavigation();
    rebuildCorpus();
    showSlide(Math.max(0, slides.findIndex(slide => slide.dataset.article === article)));
    if (updateHistory && location.hash !== `#${slides[index].id}`) {
      history.pushState(null, "", `#${slides[index].id}`);
    }
    try { localStorage.setItem("fabric-workshop-language", language); } catch { /* The selected language still applies for this visit. */ }
  }

  function selectResult(ordinal, scroll = false) {
    const options = [...$("search-results").querySelectorAll('[role="option"]')];
    selectedResult = options.length ? Math.max(0, Math.min(ordinal, options.length - 1)) : -1;
    options.forEach((option, item) => option.setAttribute("aria-selected", String(item === selectedResult)));
    if (selectedResult >= 0) {
      searchInput.setAttribute("aria-activedescendant", options[selectedResult].id);
      if (scroll) options[selectedResult].scrollIntoView({block: "nearest"});
    } else searchInput.removeAttribute("aria-activedescendant");
  }

  function showResults() {
    clearTimeout(searchTimer);
    searchTimer = null;
    const terms = termsFor(searchInput.value);
    const container = $("search-results");
    container.replaceChildren();
    results = [];
    if (!terms.length) {
      $("search-status").textContent = ui("手順名または本文の語を入力してください。");
      searchInput.setAttribute("aria-expanded", "false");
      selectResult(-1);
      return;
    }
    const matches = corpus.filter(item => terms.every(term => `${item.titleFolded} ${item.bodyFolded} ${normalize(labName(item.lab))}`.includes(term)))
      .map(item => ({...item, score: terms.reduce((score, term) => score + (item.titleFolded === term ? 100 : item.titleFolded.includes(term) ? 30 : 0) + (normalize(labName(item.lab)).includes(term) ? 10 : 0) + Math.min(item.bodyFolded.split(term).length - 1, 5), 0)}))
      .sort((a, b) => b.score - a.score || a.ordinal - b.ordinal);
    const groups = new Map();
    matches.slice(0, 60).forEach(item => {
      if (!groups.has(item.lab)) groups.set(item.lab, []);
      groups.get(item.lab).push(item);
    });
    groups.forEach((items, lab) => {
      const heading = document.createElement("div");
      heading.className = "search-group";
      heading.textContent = `${labName(lab)} / ${items.length}${english() ? " results" : "件"}`;
      heading.setAttribute("role", "presentation");
      container.append(heading);
      items.forEach(item => {
        const option = document.createElement("div");
        const resultIndex = results.length;
        results.push(item);
        option.id = `search-result-${resultIndex}`;
        option.className = "search-result";
        option.setAttribute("role", "option");
        const title = document.createElement("strong");
        title.append(markedText(item.title, terms));
        const chip = item.slide.querySelector(".item-chip");
        if (chip) option.append(chip.cloneNode(true));
        const excerpt = document.createElement("p");
        const firstHit = Math.min(...terms.map(term => item.bodyFolded.indexOf(term)).filter(offset => offset >= 0));
        const offset = Number.isFinite(firstHit) ? Math.max(0, firstHit - 42) : 0;
        const snippet = `${offset ? "…" : ""}${item.body.slice(offset, offset + 160)}${item.body.length > offset + 160 ? "…" : ""}`;
        excerpt.append(markedText(snippet, terms));
        option.append(title, excerpt);
        option.addEventListener("click", () => activateResult(resultIndex));
        option.addEventListener("pointermove", () => selectResult(resultIndex));
        container.append(option);
      });
    });
    $("search-status").textContent = matches.length ? (english() ? `${matches.length} articles${matches.length > 60 ? " / showing the top 60" : ""}` : `${matches.length}件の記事${matches.length > 60 ? " / 上位60件を表示" : ""}`) : ui("一致する記事はありません。別の語で検索してください。");
    searchInput.setAttribute("aria-expanded", String(results.length > 0));
    selectResult(0);
  }

  function activateResult(ordinal) {
    const result = results[ordinal];
    if (!result) return;
    searchTerms = termsFor(searchInput.value);
    highlightedArticle = result.slide.id;
    navigate(result.slide.id);
    const first = result.slide.querySelector("mark.article-hit");
    if (first) {
      let parent = first.parentElement;
      while (parent && parent !== result.slide) {
        if (parent.tagName === "DETAILS") parent.open = true;
        parent = parent.parentElement;
      }
      first.scrollIntoView({block: "center", behavior: reducedMotion.matches ? "instant" : "smooth"});
    }
  }

  function showImage(nextIndex) {
    if (!images.length) return;
    imageIndex = Math.max(0, Math.min(nextIndex, images.length - 1));
    const image = images[imageIndex];
    const zoom = $("zoom-image");
    imageScale = null;
    zoom.onload = applyZoom;
    zoom.onerror = () => {
      reportImageError(image, english() ? "Cannot load the image data. Download the HTML file again." : "画像データを読み込めません。HTMLファイルを再取得してください。");
      $("image-caption").textContent = image.dataset.loadError;
    };
    // A selected screenshot may still be outside the lazy-loading viewport.
    const source = imageSource(image);
    if (source) zoom.src = source;
    else zoom.removeAttribute("src");
    zoom.alt = image.alt;
    $("image-caption").textContent = source ? image.alt || (english() ? "Screenshot" : "操作画像") : image.dataset.loadError;
    $("image-counter").textContent = `${english() ? "Screenshot" : "この記事の画像"} ${imageIndex + 1} / ${images.length}`;
    $("image-previous").disabled = imageIndex === 0;
    $("image-next").disabled = imageIndex === images.length - 1;
    applyZoom();
  }

  function applyZoom() {
    const zoom = $("zoom-image");
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
    $("zoom-label").textContent = imageScale === null ? ui("全体表示") : `${Math.round(imageScale * 100)}%`;
    $("image-fit").setAttribute("aria-pressed", String(imageScale === null));
    $("image-actual").setAttribute("aria-pressed", String(imageScale === 1));
  }

  function setZoom(scale) {
    imageScale = scale === null ? null : Math.max(.25, Math.min(4, scale));
    applyZoom();
  }

  const stage = document.querySelector(".image-stage");
  let drag = null;
  stage.addEventListener("pointerdown", event => {
    if (imageScale === null || event.button !== 0) return;
    drag = {x: event.clientX, y: event.clientY, left: stage.scrollLeft, top: stage.scrollTop};
    stage.setPointerCapture(event.pointerId);
    stage.classList.add("is-dragging");
  });
  stage.addEventListener("pointermove", event => {
    if (!drag) return;
    stage.scrollLeft = drag.left - event.clientX + drag.x;
    stage.scrollTop = drag.top - event.clientY + drag.y;
  });
  const stopDrag = () => { drag = null; stage.classList.remove("is-dragging"); };
  stage.addEventListener("pointerup", stopDrag);
  stage.addEventListener("pointercancel", stopDrag);
  stage.addEventListener("lostpointercapture", stopDrag);

  document.querySelectorAll(".prose table").forEach(table => {
    if (table.parentElement.classList.contains("table-wrap")) return;
    const wrapper = document.createElement("div");
    wrapper.className = "table-wrap";
    wrapper.tabIndex = 0;
    wrapper.setAttribute("role", "region");
    wrapper.setAttribute("aria-label", table.closest(".slide").dataset.language === "en" ? "Data table / scroll horizontally" : "データ表 / 横スクロール可能");
    table.before(wrapper);
    wrapper.append(table);
  });
  document.querySelectorAll(".code-block").forEach(block => {
    let button = block.querySelector(".copy-code");
    if (!button) {
      button = document.createElement("button");
      button.type = "button";
      button.className = "copy-code";
      button.textContent = ui("コピー");
      block.querySelector(".code-label")?.append(button);
    }
    button.addEventListener("click", async () => {
      const copyLabel = button.closest(".slide").dataset.language === "en" ? "Copy" : "コピー";
      const text = block.querySelector("code").textContent;
      let copied = false;
      try {
        if (!navigator.clipboard?.writeText) throw new Error("clipboard unavailable");
        await navigator.clipboard.writeText(text);
        copied = true;
      } catch {
        const field = document.createElement("textarea");
        field.value = text;
        field.style.cssText = "position:fixed;left:-9999px;top:0";
        document.body.append(field);
        field.select();
        try { copied = document.execCommand("copy"); } catch { copied = false; }
        field.remove();
        button.focus({preventScroll: true});
      }
      button.textContent = copied ? ui("コピーしました") : ui("コピーできませんでした");
      button.setAttribute("aria-live", "polite");
      setTimeout(() => { button.textContent = copyLabel; }, 2000);
    });
  });

  document.addEventListener("click", event => {
    const target = event.target.closest("a, button");
    if (!target) return;
    if (target.matches('a[href^="#"]')) {
      let id;
      try { id = decodeURIComponent(target.getAttribute("href").slice(1)); } catch { return; }
      if (id !== "main" && navigate(id)) event.preventDefault();
    } else if (target.matches("[data-close-dialog]")) target.closest("dialog").close();
    else if (target.matches(".shot")) {
      images = [...slides[index].querySelectorAll(".step-image")];
      const selected = target.querySelector(".step-image");
      if (!selected) return;
      openDialog(imageDialog);
      showImage(images.indexOf(selected));
    }
  });
  document.querySelectorAll("dialog").forEach(dialog => {
    dialog.addEventListener("click", event => {
      if (event.target !== dialog) return;
      const bounds = dialog.getBoundingClientRect();
      if (event.clientX < bounds.left || event.clientX > bounds.right || event.clientY < bounds.top || event.clientY > bounds.bottom) dialog.close();
    });
  });
  $("previous").addEventListener("click", () => navigate(slides[index - 1]?.id));
  $("next").addEventListener("click", () => navigate(slides[index + 1]?.id));
  $("search-open").addEventListener("click", openSearch);
  $("steps-open").addEventListener("click", openSteps);
  $("help-open").addEventListener("click", () => openDialog($("help-dialog")));
  $("nav-toggle").addEventListener("click", () => setNav(!document.body.classList.contains("nav-open")));
  $("nav-close").addEventListener("click", () => setNav(false, true));
  $("nav-scrim").addEventListener("click", () => setNav(false, true));
  $("image-previous").addEventListener("click", () => showImage(imageIndex - 1));
  $("image-next").addEventListener("click", () => showImage(imageIndex + 1));
  $("image-fit").addEventListener("click", () => setZoom(null));
  $("image-actual").addEventListener("click", () => setZoom(1));
  $("image-plus").addEventListener("click", () => setZoom((imageScale ?? 1) + .25));
  $("image-minus").addEventListener("click", () => setZoom((imageScale ?? 1) - .25));

  function applyTheme(theme) {
    if (theme === "auto") delete document.documentElement.dataset.theme;
    else document.documentElement.dataset.theme = theme;
    const names = english() ? {light: "Light", dark: "Dark", auto: "Auto"} : {light: "明", dark: "暗", auto: "自動"};
    $("theme-toggle").textContent = `${english() ? "Theme" : "テーマ"}: ${names[theme]}`;
    const next = names[{auto: "light", light: "dark", dark: "auto"}[theme]];
    $("theme-toggle").setAttribute("aria-label", english() ? `Theme: ${names[theme]}. Select to use ${next}` : `表示テーマ: ${names[theme]}。選択すると${next}に変更`);
    $("theme-toggle").dataset.mode = theme;
  }
  let savedTheme = "auto";
  try { savedTheme = localStorage.getItem("fabric-workshop-theme") || "auto"; } catch { /* Local file storage may be disabled. */ }
  applyTheme(["light", "dark", "auto"].includes(savedTheme) ? savedTheme : "auto");
  $("theme-toggle").addEventListener("click", () => {
    const theme = {auto: "light", light: "dark", dark: "auto"}[$("theme-toggle").dataset.mode];
    applyTheme(theme);
    try { localStorage.setItem("fabric-workshop-theme", theme); } catch { /* Theme still applies for this visit. */ }
  });
  $("language-select").addEventListener("change", event => setLanguage(event.target.value));

  searchInput.addEventListener("input", () => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(showResults, 100);
  });
  searchInput.addEventListener("keydown", event => {
    if (event.isComposing) return;
    if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      event.preventDefault();
      if (searchTimer) showResults();
      selectResult(selectedResult + (event.key === "ArrowDown" ? 1 : -1), true);
    } else if (event.key === "Enter") {
      event.preventDefault();
      if (searchTimer) showResults();
      activateResult(selectedResult);
    }
  });
  $("nav-filter").addEventListener("input", event => {
    const terms = termsFor(event.target.value);
    let visible = 0;
    document.querySelectorAll(".chapter-group").forEach(group => {
      const title = normalize(group.querySelector(".chapter-link").textContent);
      const chapterMatch = terms.every(term => title.includes(term));
      let matchingSections = 0;
      group.querySelectorAll(".section-link").forEach(link => {
        link.hidden = !chapterMatch && !terms.every(term => `${title} ${normalize(link.textContent)}`.includes(term));
        if (!link.hidden) matchingSections++;
      });
      group.hidden = !chapterMatch && matchingSections === 0;
      if (!group.hidden) visible++;
      if (terms.length) {
        group.querySelector(".chapter-sections").hidden = false;
        group.querySelector(".chapter-toggle").setAttribute("aria-expanded", "true");
        group.querySelector(".chapter-toggle").textContent = "−";
      }
    });
    $("nav-empty").hidden = visible > 0;
  });

  document.addEventListener("keydown", event => {
    const editable = event.target.closest('input, textarea, select, [contenteditable="true"]');
    if (event.isComposing) return;
    if (((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") || (!editable && !event.ctrlKey && !event.metaKey && !event.altKey && event.key === "/")) {
      event.preventDefault();
      openSearch();
      return;
    }
    if (event.key === "Escape" && document.body.classList.contains("nav-open")) { setNav(false, true); return; }
    if (document.body.classList.contains("nav-open") && event.key === "Tab") {
      const controls = [...sidebar.querySelectorAll('a, button, input')].filter(element => element.getClientRects().length);
      const first = controls[0];
      const last = controls[controls.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
      return;
    }
    if (event.altKey || event.ctrlKey || event.metaKey || editable) return;
    if (event.target.closest(".table-wrap, pre") && ["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
    if (event.target.closest(".image-stage") && imageScale !== null && ["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
    if (imageDialog.open && ["ArrowLeft", "ArrowRight"].includes(event.key)) {
      event.preventDefault();
      showImage(imageIndex + (event.key === "ArrowRight" ? 1 : -1));
      return;
    }
    if (document.querySelector("dialog[open]") || document.body.classList.contains("nav-open")) return;
    const routes = {ArrowLeft: index - 1, ArrowRight: index + 1, Home: 0, End: slides.length - 1};
    if (Object.hasOwn(routes, event.key)) {
      event.preventDefault();
      navigate(slides[Math.max(0, Math.min(routes[event.key], slides.length - 1))].id);
    } else if (event.key === "?") openDialog($("help-dialog"));
  });
  window.addEventListener("scroll", () => {
    if (scrollPending) return;
    scrollPending = true;
    requestAnimationFrame(() => { updateScrollspy(); scrollPending = false; });
  }, {passive: true});
  window.addEventListener("hashchange", () => {
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)) || "welcome"; } catch { return; }
    const requestedLanguage = id.startsWith("en-") ? "en" : "ja";
    if (requestedLanguage !== language) setLanguage(requestedLanguage, false);
    navigate(id, true);
  });
  document.querySelectorAll(".slide details").forEach(details => details.addEventListener("toggle", () => {
    if (details.closest(".slide") === slides[index]) updateOutline();
  }));
  window.matchMedia("(min-width: 53.1875em)").addEventListener("change", event => { if (event.matches) setNav(false); });
  window.addEventListener("beforeprint", () => document.querySelectorAll(".step-image").forEach(loadImage));
  applyChrome();
  buildChapterNavigation();
  rebuildCorpus();
  let initialId;
  try { initialId = decodeURIComponent(location.hash.slice(1)); } catch { initialId = ""; }
  initialId = (english() ? "en-" : "") + (initialId.replace(/^en-/, "") || "welcome");
  const initialTarget = document.getElementById(initialId);
  const initialSlide = initialTarget?.closest(".slide");
  showSlide(initialSlide ? slides.indexOf(initialSlide) : 0);
  if (initialTarget && initialTarget !== initialSlide) navigate(initialId, false);
  document.documentElement.classList.add("js");
})();
