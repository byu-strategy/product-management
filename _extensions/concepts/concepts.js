// Highlights the passages that teach one builder concept (see concepts.lua). A sprint report
// links to <page>.html?c=DE02#<section>: the section anchor works without this script, and this
// script then scrolls to the first tagged passage, marks every passage for that concept, and shows
// a bar with the concept's name, "1 of 2" with previous and next when there is more than one, and
// a close button that removes the marks.
(function () {
  function run() {
    var id = new URLSearchParams(location.search).get("c");
    if (!id || !/^[A-Z]{2}\d{2}$/.test(id)) return;
    var all = document.querySelectorAll(".concept[data-c]");
    var hits = Array.prototype.filter.call(all, function (d) {
      return d.getAttribute("data-c").split(/\s+/).indexOf(id) >= 0;
    });
    if (!hits.length) return;
    var name = "";
    (hits[0].getAttribute("data-cn") || "").split(" | ").forEach(function (x) {
      if (x.indexOf(id + " ") === 0) name = x.slice(id.length + 1);
    });
    hits.forEach(function (d) { d.classList.add("concept-on"); });

    var bar = document.createElement("div");
    bar.className = "concept-bar";
    bar.setAttribute("role", "status");
    var label = document.createElement("span");
    label.className = "concept-name";
    label.textContent = name || id;
    var count = document.createElement("span");
    count.className = "concept-count";
    bar.appendChild(label);
    bar.appendChild(count);
    var i = 0;
    function show(n) {
      i = (n + hits.length) % hits.length;
      count.textContent = hits.length > 1 ? (i + 1) + " of " + hits.length : "";
      var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      hits[i].scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "start" });
    }
    function btn(text, title, fn) {
      var b = document.createElement("button");
      b.type = "button"; b.textContent = text; b.title = title; b.setAttribute("aria-label", title);
      b.addEventListener("click", fn);
      bar.appendChild(b);
    }
    if (hits.length > 1) {
      btn("‹", "Previous passage", function () { show(i - 1); });
      btn("›", "Next passage", function () { show(i + 1); });
    }
    btn("×", "Remove highlight", function () {
      hits.forEach(function (d) { d.classList.remove("concept-on"); });
      bar.remove();
    });
    document.body.appendChild(bar);
    setTimeout(function () { show(0); }, 60);
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", run);
  else run();
})();
