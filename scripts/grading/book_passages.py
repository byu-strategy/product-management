#!/usr/bin/env python3
"""Map each builder concept to the book passages that teach it, and check the map.

Reads the book's .qmd files for passages tagged `::: {.concept data-c="DE02"}` (see
_extensions/concepts) and writes book-passages.json:

  {"DE02": [{"page": "05-interface-and-flow.html", "anchor": "off-the-happy-path",
             "section": "Off the Happy Path", "tagged": true}], ...}

Also checks the third leg, the exam (private bank, read only, nothing from it is written here): every
question mapped to a tagged concept should cite (its `source`) a section that holds one of that
concept's passages, and a question's own `concept` field should agree with the concept list.

A concept with no tagged passage falls back to the sections named in its `chapter` field, marked
"tagged": false, so its report link still opens the right section. Prints, and exits 1 on, any tag
that names an unknown concept; prints the concepts with no passage at all (book gaps or stale
`chapter` references).

    python3 book_passages.py            # write the map and report
    python3 book_passages.py --check    # report only
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BOOK = HERE.parents[1]
OUT = HERE / "book-passages.json"
BASE = "https://byu-strategy.github.io/product-management/"


def slug(text):
    """Pandoc's auto identifier for a heading."""
    t = re.sub(r"[^\w\s.-]", "", text.lower(), flags=re.UNICODE)
    t = re.sub(r"\s+", "-", t.strip())
    return re.sub(r"^[^a-z]+", "", t) or "section"


def headings(path):
    """Each ##, ### or #### heading's (line, title, anchor), skipping code blocks. Repeated titles
    get pandoc's suffixes (the-building-blocks, the-building-blocks-1, ...)."""
    out, code, seen = [], False, {}
    for i, line in enumerate(path.read_text().split("\n")):
        if line.startswith("```"):
            code = not code
        m = None if code else re.match(r"^(#{2,4})\s+(.*?)\s*(\{[^}]*\})?\s*$", line)
        if m:
            ident = re.search(r"#([\w-]+)", m.group(3) or "")
            a = ident.group(1) if ident else slug(m.group(2))
            if not ident:
                n = seen.get(a, 0)
                seen[a] = n + 1
                a = a if n == 0 else f"{a}-{n}"
            out.append((i, m.group(2), a))
    return out


def concepts():
    C = {}
    for f in sorted((HERE / "concepts").glob("*.json")):
        if f.name == "passages.json":
            continue
        d = json.loads(f.read_text())
        for c in d["concepts"]:
            C[c["id"]] = c
    return C


def book_files():
    """The chapter files in _quarto.yml, in book order. Files not listed there (drafts, slides,
    anything in _archive/) are not part of the book and are never read."""
    out = []
    for line in (BOOK / "_quarto.yml").read_text().split("\n"):
        m = re.match(r"^\s*-\s+([\w.-]+\.qmd)\s*$", line)
        if m and (BOOK / m.group(1)).exists():
            out.append(BOOK / m.group(1))
    return out


def chapter_files():
    """'5' -> 05-interface-and-flow.qmd, '5b' -> 05b-..., '9c' -> 09c-..., 'A1' -> A1-...,
    from the book's file names in _quarto.yml order."""
    out = {}
    for f in book_files():
        m = re.match(r"(\d+[a-z]?|A\d+)-", f.name)
        if m:
            out.setdefault(m.group(1).lstrip("0") or "0", f)
    return out


def title(f):
    m = re.search(r'^title:\s*"?(.*?)"?\s*$', f.read_text(), re.M)
    return m.group(1) if m else f.stem


def norm(text):
    """Heading text for matching: no citations, markup or punctuation, lower case."""
    t = re.sub(r"\[@[^\]]*\]", "", text)
    t = re.sub(r"[^\w\s]", " ", t.lower().replace("\u2019", "").replace("'", ""))
    return " ".join(t.split())


def no_paren(text):
    return re.sub(r"\s*\([^)]*\)\s*$", "", text).strip()


def find_heading(f, part):
    """The heading in f that `part` names, matched without case, punctuation or citations. Tried in
    order: the whole text; with a trailing parenthetical dropped from either side; the heading's
    text before its first colon ("Staging" for "Staging: a copy of production ...")."""
    H = headings(f)
    passes = (lambda h, w: norm(h[1]) == w,
              lambda h, w: norm(no_paren(h[1])) == w,
              lambda h, w: ":" in h[1] and norm(h[1].split(":")[0]) == w)
    for test in passes:
        for want in (norm(part), norm(no_paren(part))):
            h = next((h for h in H if test(h, want)), None)
            if h:
                return h
    return None


def split_top(text):
    """Split on ';' outside parentheses."""
    out, depth, cur = [], 0, ""
    for ch in text:
        depth += (ch == "(") - (ch == ")")
        if ch == ";" and depth <= 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    return [x.strip() for x in out + [cur] if x.strip()]


def parse_refs(field):
    """A concept's `chapter` field as (chapter key or 'Appendix', [section names]) blocks:
    "Ch 9b: What is Technical Debt?; Strategic vs. Accidental Debt. Appendix: Problem Discovery
    Framework (Scoring)". A block starts at "Ch N" or "Appendix" (at the start, or after '.', ';'
    or '('); sections split on ';' outside parentheses, so periods, colons and question marks
    inside a heading are kept."""
    starts = list(re.finditer(r"(?:^|(?<=[.;]\s)|(?<=\())(?:Ch\s+(\d+[a-z]?|A\d+)|(Appendix))\b\s*:?\s*", field))
    out = []
    for i, m in enumerate(starts):
        body = field[m.end(): starts[i + 1].start() if i + 1 < len(starts) else len(field)].strip()
        if body.count(")") > body.count("("):
            body = body[:body.rindex(")")]
        body = re.sub(r"[.;(]\s*$", "", body.strip())
        out.append((m.group(1).lstrip("0") if m.group(1) else "Appendix", split_top(body)))
    return out


def resolve(field, files, unresolved, cid):
    found = []
    for key, parts in parse_refs(field):
        if key == "Appendix":
            for part in parts:
                f = next((f for f in book_files() if norm(title(f)) == norm(no_paren(part))), None)
                sub = re.search(r"\(([^)]*)\)\s*$", part)
                h = find_heading(f, sub.group(1)) if f and sub else None
                if f:
                    found.append((f, h))
                else:
                    unresolved.append(f"{cid}: Appendix: {part}")
            continue
        f = files.get(key)
        if not f:
            unresolved.append(f"{cid}: Ch {key} (no such chapter)")
            continue
        if not parts:
            found.append((f, None))
        for part in parts:
            h = find_heading(f, part)
            if h:
                found.append((f, h))
            else:
                unresolved.append(f"{cid}: Ch {key}: {part}")
    out = []
    for f, h in found:
        e = {"page": f.stem + ".html", "anchor": h[2] if h else "", "section": h[1] if h else title(f), "tagged": False}
        if e not in out:
            out.append(e)
    return out


UNRESOLVED = []


def build():
    C, P, unknown = concepts(), {}, []
    for f in book_files():
        H, L = headings(f), f.read_text().split("\n")
        stack, spans, code = [], [], False
        for i, line in enumerate(L):
            if line.startswith("```"):
                code = not code
            if code or not line.startswith(":::"):
                continue
            if "{" in line:
                stack.append((i, line))
            elif stack:
                spans.append((*stack.pop(), i))
        for start, line, end in sorted(spans):
            m = re.match(r'^:{3,}\s*\{[^}]*\.concept\b[^}]*data-c="([^"]+)"', line)
            if not m:
                continue
            inside = [h for h in H if start < h[0] < end]
            above = {}
            for h in H:  # the nearest heading of each level above the passage
                if h[0] < start:
                    above[len(L[h[0]]) - len(L[h[0]].lstrip("#"))] = h
            above = [h for lvl, h in sorted(above.items()) if not any(o[0] > h[0] for k, o in above.items() if k < lvl)]
            first_content = next((x for x in L[start + 1:end] if x.strip()), "")
            land = inside[0] if inside and first_content.startswith("#") else (above[-1] if above else None)
            for cid in m.group(1).split():
                if cid not in C:
                    unknown.append(f"{f.name}:{start + 1} {cid}")
                    continue
                entry = {"page": f.stem + ".html", "anchor": land[2] if land else "", "section": (above + inside)[0][1] if above + inside else "",
                         "tagged": True, "covers": [h[2] for h in above + inside]}
                if entry not in P.setdefault(cid, []):
                    P[cid].append(entry)
    files, missing, unresolved = chapter_files(), [], []
    for cid, c in C.items():
        if cid in P:
            continue
        found = resolve(c.get("chapter", ""), files, unresolved, cid)
        if found:
            P[cid] = found
        else:
            missing.append(f"{cid} {c['name']}: {c.get('chapter', '')}")
    # a field that says "not taught yet" names sections that only partly cover it; not stale
    untaught = {cid for cid, c in C.items() if c.get("chapter", "").lower().startswith("not taught")}
    UNRESOLVED[:] = [x for x in unresolved if x.split(":")[0] not in untaught]
    return P, unknown, missing, C


EXAM = Path.home() / "Library/CloudStorage/OneDrive-BrighamYoungUniversity/3. Teaching/_materials/product-management/builder-exam/items/draft"


def exam_check(P, C):
    """Disagreements among the concept list, the book tags and the exam bank's cited sections."""
    items = {}
    for f in sorted(EXAM.glob("*.json")) if EXAM.exists() else []:
        for x in json.loads(f.read_text()).get("items", []):
            items[x["id"]] = x
    if not items:
        return ["exam bank not reachable; exam check skipped"]
    out, listed = [], {}
    for cid, c in C.items():
        for q in c.get("exam") or []:
            listed.setdefault(q, set()).add(cid)
            if q not in items:
                out.append(f"{cid} lists {q}, which is not in the bank")
    for q, x in items.items():
        if x.get("concept") and x["concept"] not in listed.get(q, set()):
            out.append(f"{q} names {x['concept']}, but that concept does not list it")
    unmapped = [q for q in items if q not in listed]
    if unmapped:
        out.append(f"{len(unmapped)} questions map to no concept: {', '.join(sorted(unmapped))}")
    for q, cids in sorted(listed.items()):
        x = items.get(q)
        if not x:
            continue
        cited = {s.strip().replace("pm/", "").replace(".qmd", ".html") for s in str(x.get("source", "")).split(";")}
        for cid in sorted(cids):
            secs = {f'{e["page"]}#{a}' for e in P.get(cid, []) if e["tagged"] for a in e["covers"]}
            if secs and not (cited & secs):
                out.append(f"{q} ({cid}) cites {', '.join(sorted(cited)) or 'no section'}; the book's {cid} passages are under {', '.join(sorted({f'{e["page"]}#{e["anchor"]}' for e in P[cid] if e["tagged"]}))}")
    return out


def url(entry, cid):
    return f"{BASE}{entry['page']}?c={cid}" + (f"#{entry['anchor']}" if entry.get("anchor") else "")


if __name__ == "__main__":
    P, unknown, missing, C = build()
    tagged = sum(1 for v in P.values() if any(x["tagged"] for x in v))
    print(f"{len(C)} concepts: {tagged} tagged in the book, {len(P) - tagged} by section only, {len(missing)} with no passage")
    for x in unknown:
        print("  unknown concept id in a tag:", x)
    for x in missing:
        print("  no passage:", x)
    for x in UNRESOLVED:
        print("  section not found (stale `chapter` reference):", x)
    ex = exam_check(P, C)
    print(f"exam: {len(ex)} disagreements")
    for x in ex:
        print("  ", x)
    if "--check" not in sys.argv:
        OUT.write_text(json.dumps(dict(sorted(P.items())), indent=1) + "\n")
        print("wrote", OUT)
    sys.exit(1 if unknown else 0)
