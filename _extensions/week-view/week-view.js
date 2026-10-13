// Topics | Weeks switch for the left rail.
// Topics is the sidebar Quarto renders. Weeks is built here from window.PM_WEEK_VIEW
// (_weeks.yml, written into the page by week-view.lua), reusing the chapter titles Quarto
// already put in the sidebar so a title lives in one place.
// New visitors start on Weeks. The reader's choice is remembered; ?view=weeks or ?view=topics
// in a link overrides it.
(function () {
  var KEY = "pm-sidebar-view";

  function load() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function save(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }
  function page(href) { return (href || "").split("/").pop().split("#")[0].replace(/\.html$/, "") || "index"; }
  function esc(s) { return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;"); }

  // Today as YYYY-MM-DD in the reader's own time zone.
  function today() {
    var d = new Date();
    return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" +
           String(d.getDate()).padStart(2, "0");
  }

  // "This week" is the latest week whose start has arrived. None before the first week
  // starts or after the course ends.
  function currentWeek(DATA, WEEKS) {
    var t = today(), cur = null;
    if (DATA["course-end"] && t > DATA["course-end"]) return null;
    WEEKS.forEach(function (w) { if (w.start <= t) cur = w.n; });
    return cur;
  }

  // The data is written into the page after this script loads, so read it once the page is ready.
  document.addEventListener("DOMContentLoaded", function () {
    var DATA = window.PM_WEEK_VIEW;
    if (!DATA || !DATA.weeks) return;
    var WEEKS = DATA.weeks.map(function (w) {
      return { n: Number(w.week), date: w.date, start: w.start, axis: w.axis,
               read: w.read || [], items: w.items || [] };
    });
    var COURSE_INFO = DATA["course-info"] || [];
    var ICON = { due: "bi-flag-fill", assigned: "bi-plus-circle", plan: "bi-pencil-square",
                 exam: "bi-journal-check", task: "bi-check2-square" };
    var menu = document.querySelector("#quarto-sidebar .sidebar-menu-container");
    if (!menu) return;
    var topics = menu.querySelector("ul");
    var here = page(location.pathname);
    var current = currentWeek(DATA, WEEKS);

    // Chapter titles, keyed by page, taken from Quarto's own sidebar.
    var title = {}, topicPages = [];
    topics.querySelectorAll("a.sidebar-link[href]").forEach(function (a) {
      var p = page(a.getAttribute("href"));
      title[p] = a.innerHTML;
      topicPages.push(p);
    });

    function link(p) {
      return '<li class="sidebar-item"><div class="sidebar-item-container"><a href="./' + p +
        '.html" class="sidebar-item-text sidebar-link' + (p === here ? " active" : "") + '">' +
        (title[p] || esc(p)) + "</a></div></li>";
    }
    function group(id, head, sub, body, open, cls) {
      return '<li class="sidebar-item sidebar-item-section wk-group ' + (cls || "") + '">' +
        '<div class="sidebar-item-container"><a class="sidebar-item-text sidebar-link text-start wk-head" ' +
        'data-bs-toggle="collapse" data-bs-target="#' + id + '" aria-expanded="' + open + '">' +
        '<span class="menu-text"><span>' + head + "</span>" +
        (sub ? '<span class="wk-sub">' + esc(sub) + "</span>" : "") + "</span></a>" +
        '<a class="sidebar-item-toggle text-start" data-bs-toggle="collapse" data-bs-target="#' + id +
        '" aria-expanded="' + open + '" aria-label="Toggle section"><i class="bi bi-chevron-right ms-2"></i></a></div>' +
        '<ul id="' + id + '" class="collapse list-unstyled sidebar-section depth1' + (open ? " show" : "") + '">' +
        body + "</ul></li>";
    }
    function item(it) {
      var inner = '<i class="bi ' + (ICON[it.kind] || ICON.task) + '"></i><span>' + esc(it.text) + "</span>";
      return '<li class="wk-item wk-' + esc(it.kind) + '">' +
        (it.href ? '<a href="./' + esc(it.href) + '">' + inner + "</a>" : inner) + "</li>";
    }

    var listed = {};
    COURSE_INFO.forEach(function (p) { listed[p] = 1; });
    WEEKS.forEach(function (w) { w.read.forEach(function (p) { listed[p] = 1; }); });
    var rest = topicPages.filter(function (p) { return !listed[p]; });

    var html = group("wk-info", "Course info", "", COURSE_INFO.map(link).join(""),
                     COURSE_INFO.indexOf(here) >= 0, "wk-meta");
    WEEKS.forEach(function (w) {
      var now = w.n === current;
      var head = "Week " + w.n + (now ? ' <span class="wk-now">This week</span>' : "");
      var cls = (now ? "wk-current" : "") + (current !== null && w.n < current ? " wk-past" : "");
      html += group("wk-" + w.n, head, w.date + " · " + w.axis,
                    w.read.map(link).join("") + w.items.map(item).join(""),
                    now || w.read.indexOf(here) >= 0, cls);
    });
    html += group("wk-ref", "Appendix and references", "", rest.map(link).join(""),
                  rest.indexOf(here) >= 0, "wk-meta");

    var weeks = document.createElement("ul");
    weeks.className = "list-unstyled mt-1 wk-list";
    weeks.innerHTML = html;
    menu.appendChild(weeks);

    // The switch, under the search box.
    var sw = document.createElement("div");
    sw.className = "wk-switch";
    sw.setAttribute("role", "tablist");
    sw.setAttribute("aria-label", "Sidebar view");
    sw.innerHTML = '<button type="button" role="tab" data-view="topics"><i class="bi bi-book"></i> Topics</button>' +
                   '<button type="button" role="tab" data-view="weeks"><i class="bi bi-calendar3"></i> Weeks</button>';
    var search = document.querySelector("#quarto-sidebar .sidebar-search");
    if (search) search.insertAdjacentElement("afterend", sw);
    else menu.parentNode.insertBefore(sw, menu);

    // Prev / next at the foot of a chapter follow the reading order in Weeks mode.
    var order = [];
    WEEKS.forEach(function (w) { w.read.forEach(function (p) { order.push({ p: p, w: w.n }); }); });
    var pos = order.map(function (o) { return o.p; }).indexOf(here);
    var nav = document.querySelector("nav.page-navigation");
    var topicsNav = nav ? nav.innerHTML : "";
    function navLink(o, dir) {
      if (!o) return "";
      var t = '<span class="nav-page-text"><span class="wk-nav-week">Week ' + o.w + "</span>" +
              (title[o.p] || esc(o.p)) + "</span>";
      return '<a href="./' + o.p + '.html" class="pagination-link">' +
        (dir === "prev" ? '<i class="bi bi-arrow-left-short"></i> ' + t
                        : t + ' <i class="bi bi-arrow-right-short"></i>') + "</a>";
    }
    var weeksNav = pos < 0 ? topicsNav :
      '<div class="nav-page nav-page-previous">' + navLink(order[pos - 1], "prev") + "</div>" +
      '<div class="nav-page nav-page-next">' + navLink(order[pos + 1], "next") + "</div>";

    function show(view) {
      var w = view === "weeks";
      topics.hidden = w;
      weeks.hidden = !w;
      sw.querySelectorAll("button").forEach(function (b) {
        var on = b.dataset.view === view;
        b.classList.toggle("on", on);
        b.setAttribute("aria-selected", on);
      });
      if (nav) nav.innerHTML = w ? weeksNav : topicsNav;
    }
    sw.addEventListener("click", function (e) {
      var b = e.target.closest("button");
      if (!b) return;
      show(b.dataset.view);
      save(b.dataset.view);
    });

    var asked = new URLSearchParams(location.search).get("view");
    show(asked === "weeks" || asked === "topics" ? asked : load() === "topics" ? "topics" : "weeks");

    // In Weeks mode, bring this week into view if the rail is taller than the window.
    if (!weeks.hidden) {
      var rail = document.getElementById("quarto-sidebar");
      var cur = weeks.querySelector(".wk-current");
      if (rail && cur && cur.getBoundingClientRect().bottom > window.innerHeight) {
        rail.scrollTop += cur.getBoundingClientRect().top - window.innerHeight / 3;
      }
    }
  });
})();
