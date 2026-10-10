// Adds a small "Learn" button beside each heading marked data-learn by learn.lua.
// Clicking it copies the /learn command for that section and shows a short note.
(function () {
  var ICON = '<svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/></svg>';

  function copy(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text);
    }
    return new Promise(function (resolve, reject) {
      var ta = document.createElement("textarea");
      ta.value = text; ta.setAttribute("readonly", ""); ta.style.position = "fixed"; ta.style.opacity = "0";
      document.body.appendChild(ta); ta.select();
      try { document.execCommand("copy") ? resolve() : reject(); } catch (e) { reject(e); }
      document.body.removeChild(ta);
    });
  }

  function note(btn, text, ok) {
    var n = btn.querySelector(".learn-note");
    n.textContent = text;
    btn.classList.toggle("learn-failed", !ok);
    btn.classList.add("learn-copied");
    clearTimeout(btn._t);
    btn._t = setTimeout(function () { btn.classList.remove("learn-copied", "learn-failed"); }, 2600);
  }

  function init() {
    document.querySelectorAll("[data-learn]").forEach(function (el) {
      var h = /^H[1-6]$/.test(el.tagName) ? el : el.querySelector("h2");
      if (!h || h.querySelector(".learn-btn")) return;
      var cmd = el.getAttribute("data-learn");
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "learn-btn";
      btn.title = "Copy a /learn command for this section, then paste it into Claude Code";
      btn.setAttribute("aria-label", "Copy the /learn command for this section");
      btn.innerHTML = ICON + '<span class="learn-label">Learn in Claude</span><span class="learn-note" role="status" aria-live="polite"></span>';
      btn.addEventListener("click", function () {
        copy(cmd).then(
          function () { note(btn, "Copied. Paste it into Claude Code.", true); },
          function () { window.prompt("Copy this, then paste it into Claude Code:", cmd); }
        );
      });
      h.appendChild(btn);
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init); else init();
})();
