/* Addy Osmani 双语存档 — 交互脚本（零依赖） */
(function () {
  "use strict";

  var root = document.body.getAttribute("data-root") || "";
  var html = document.documentElement;

  /* ------------------------------------------------------------- theme --- */

  var themeBtn = document.getElementById("theme-toggle");
  if (themeBtn) {
    themeBtn.addEventListener("click", function () {
      var next = html.dataset.theme === "dark" ? "light" : "dark";
      html.dataset.theme = next;
      try { localStorage.setItem("ao-theme", next); } catch (e) {}
    });
  }

  /* -------------------------------------------------------------- font --- */

  var fontBtns = [].slice.call(document.querySelectorAll("[data-font]"));
  function syncFont(v) {
    fontBtns.forEach(function (b) {
      b.classList.toggle("is-active", b.getAttribute("data-font") === v);
    });
  }
  var curFont = "m";
  try { curFont = localStorage.getItem("ao-font") || "m"; } catch (e) {}
  if (curFont !== "m") html.dataset.font = curFont;
  syncFont(curFont);

  fontBtns.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var v = btn.getAttribute("data-font");
      html.dataset.font = v;
      try { localStorage.setItem("ao-font", v); } catch (e) {}
      syncFont(v);
    });
  });

  /* ----------------------------------------------------- progress + bar --- */

  var bar = document.getElementById("progress");
  var topbar = document.querySelector(".topbar");

  function onScroll() {
    var h = document.documentElement;
    var max = h.scrollHeight - h.clientHeight;
    if (bar) bar.style.width = (max > 0 ? (h.scrollTop / max) * 100 : 0) + "%";
    if (topbar) topbar.classList.toggle("is-stuck", h.scrollTop > 6);
  }

  var ticking = false;
  window.addEventListener("scroll", function () {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(function () { onScroll(); ticking = false; });
  }, { passive: true });
  onScroll();

  /* ------------------------------------------------------------- toc --- */

  var tocLinks = [].slice.call(document.querySelectorAll('.toc a[href^="#"]'));
  if (tocLinks.length && "IntersectionObserver" in window) {
    var heads = tocLinks
      .map(function (a) { return document.getElementById(a.getAttribute("href").slice(1)); })
      .filter(Boolean);
    var active = null;

    function setActive(id) {
      tocLinks.forEach(function (a) {
        var on = a.getAttribute("href") === "#" + id;
        a.classList.toggle("is-current", on);
        if (on && active !== a) {
          active = a;
          var box = a.closest(".toc");
          if (box) {
            var r = a.getBoundingClientRect(), br = box.getBoundingClientRect();
            if (r.top < br.top + 40 || r.bottom > br.bottom - 40) {
              box.scrollTop = a.offsetTop - box.clientHeight / 2;
            }
          }
        }
      });
    }

    var visible = {};
    var io = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (en) { visible[en.target.id] = en.isIntersecting; });
        for (var i = 0; i < heads.length; i++) {
          if (visible[heads[i].id]) { setActive(heads[i].id); return; }
        }
      },
      { rootMargin: "-88px 0px -68% 0px", threshold: 0 }
    );
    heads.forEach(function (h) { io.observe(h); });
  }

  /* --------------------------------------------------------- lightbox --- */

  var lb = document.getElementById("lightbox");
  if (lb) {
    var lbImg = lb.querySelector("img");
    document.addEventListener("click", function (e) {
      var img = e.target.closest && e.target.closest("img.zoomable");
      if (img) {
        e.preventDefault();
        lbImg.src = img.currentSrc || img.src;
        lbImg.alt = img.alt || "";
        if (lb.showModal) lb.showModal(); else lb.setAttribute("open", "");
        return;
      }
      if (e.target === lb) lb.close ? lb.close() : lb.removeAttribute("open");
    });
    var closeBtn = lb.querySelector(".lightbox-close");
    if (closeBtn) closeBtn.addEventListener("click", function () {
      lb.close ? lb.close() : lb.removeAttribute("open");
    });
    lb.addEventListener("click", function (e) {
      if (e.target === lbImg) lb.close ? lb.close() : lb.removeAttribute("open");
    });
  }

  /* ----------------------------------------------------------- search --- */

  var input = document.getElementById("search-input");
  if (!input) return;

  var resultsBox = document.getElementById("search-results");
  var clearBtn = document.getElementById("search-clear");
  var kbd = document.querySelector(".search-kbd");
  var index = null;
  var timer = null;
  var cursor = -1;

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
    });
  }

  function highlight(text, terms) {
    var safe = esc(text);
    if (!terms.length) return safe;
    var pattern = terms
      .filter(function (t) { return t.length > 1; })
      .map(function (t) { return t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); })
      .join("|");
    if (!pattern) return safe;
    return safe.replace(new RegExp("(" + pattern + ")", "gi"), "<mark>$1</mark>");
  }

  function loadIndex() {
    if (index) return Promise.resolve(index);
    return fetch(root + "search.json")
      .then(function (r) { return r.json(); })
      .then(function (d) { index = d; return d; })
      .catch(function () { index = []; return index; });
  }

  function search(q) {
    var terms = q.toLowerCase().split(/\s+/).filter(Boolean);
    if (!terms.length) return [];
    var out = [];
    (index || []).forEach(function (it) {
      var title = (it.t + " " + it.e).toLowerCase();
      var summary = (it.x || "").toLowerCase();
      var group = (it.g || "").toLowerCase();
      var score = 0;
      var allMatch = true;

      terms.forEach(function (t) {
        var hit = 0;
        if (title.indexOf(t) >= 0) hit += 100;
        if (group.indexOf(t) >= 0) hit += 26;
        if (summary.indexOf(t) >= 0) hit += 38;
        if (!hit) allMatch = false;
        score += hit;
      });

      if (!allMatch) return;
      score -= Math.min(30, it.m || 0) * 0.2;
      out.push({ it: it, score: score });
    });
    return out.sort(function (a, b) { return b.score - a.score; }).slice(0, 14);
  }

  function render(q) {
    var terms = q.toLowerCase().split(/\s+/).filter(Boolean);
    var hits = search(q);
    cursor = -1;

    if (!hits.length) {
      resultsBox.innerHTML = '<div class="sr-empty">没有匹配「' + esc(q) + '」的文章。<br>试试「循环」「自主性」「评审」这类主题词。</div>';
      resultsBox.hidden = false;
      return;
    }

    var htmlStr =
      '<div class="sr-head">' + hits.length + " 个结果 · ↑↓ 选择 · Enter 打开 · Esc 关闭</div>";
    hits.forEach(function (h) {
      var it = h.it;
      htmlStr +=
        '<a class="sr-item" href="articles/' + it.s + '.zh.html">' +
        '<span class="sr-title">' + highlight(it.t, terms) +
        (it.e ? "<small>" + highlight(it.e, terms) + "</small>" : "") +
        "</span>" +
        '<span class="sr-meta">' + esc(it.g || "") + " · " + esc(it.d || "") +
        (it.x ? " — " + highlight(it.x, terms) : "") +
        "</span></a>";
    });
    resultsBox.innerHTML = htmlStr;
    resultsBox.hidden = false;
  }

  function close() {
    resultsBox.hidden = true;
    resultsBox.innerHTML = "";
    clearBtn.hidden = true;
    if (kbd) kbd.hidden = false;
    document.body.classList.remove("is-searching");
  }

  function onInput() {
    var q = input.value.trim();
    clearBtn.hidden = !q;
    if (kbd) kbd.hidden = !!q;
    if (!q) { close(); return; }
    loadIndex().then(function () {
      if (input.value.trim() !== q) return;
      document.body.classList.add("is-searching");
      render(q);
    });
  }

  input.addEventListener("input", function () {
    clearTimeout(timer);
    timer = setTimeout(onInput, 70);
  });

  input.addEventListener("focus", function () {
    if (input.value.trim()) loadIndex().then(function () { render(input.value.trim()); });
  });

  clearBtn.addEventListener("click", function () {
    input.value = "";
    onInput();
    input.focus();
  });

  input.addEventListener("keydown", function (e) {
    var items = [].slice.call(resultsBox.querySelectorAll(".sr-item"));
    if (e.key === "Escape") { input.value = ""; onInput(); input.blur(); return; }
    if (!items.length) return;
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      e.preventDefault();
      cursor = (cursor + (e.key === "ArrowDown" ? 1 : -1) + items.length) % items.length;
      items.forEach(function (el, i) { el.classList.toggle("is-cursor", i === cursor); });
      items[cursor].scrollIntoView({ block: "nearest" });
    } else if (e.key === "Enter") {
      e.preventDefault();
      (items[cursor >= 0 ? cursor : 0]).click();
    }
  });

  document.addEventListener("keydown", function (e) {
    var tag = (document.activeElement && document.activeElement.tagName) || "";
    var typing = /^(INPUT|TEXTAREA|SELECT)$/.test(tag) || document.activeElement.isContentEditable;
    if (e.key === "/" && !typing) {
      e.preventDefault();
      input.focus();
      input.select();
    }
  });

  document.addEventListener("click", function (e) {
    if (!e.target.closest || !e.target.closest(".searchbar")) {
      if (!resultsBox.hidden) close();
    }
  });
})();
