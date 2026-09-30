"""Bring Google Docs, Sheets, Slides, and Drive files into sprint packets through the Drive connector.

Python cannot call the Drive connector, so this is two steps around one agent:

    python3 ~/courses/product-management/scripts/drive_fill.py --sprint N --list
        prints every Google file a packet links to that has not been fetched yet, as JSON

    (an agent with the Google Drive connector, signed in as aifoundry.byu@gmail.com, reads each file
     and writes grading/sprint-N/drive/<net_id>.json: {file_id: {title, mime, ok, text or error}})

    python3 ~/courses/product-management/scripts/drive_fill.py --sprint N --merge
        folds those files into each packet as drive_files (text capped), for graders and the appendix

Students are told to set files to "Anyone with the link can view" or share them with
aifoundry.byu@gmail.com. A file shared with neither comes back ok: false.
Student data stays in _data. This file holds none.
"""
import argparse, json
from pathlib import Path

DATA = Path.home() / "hubs/courses/_data/product-management"
CAP = 8_000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sprint", type=int, required=True)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--list", action="store_true")
    g.add_argument("--merge", action="store_true")
    a = ap.parse_args()
    base = DATA / f"grading/sprint-{a.sprint}"
    drive = base / "drive"
    drive.mkdir(exist_ok=True)
    packets = [f for f in sorted(base.glob("*.json")) if not f.name.startswith("_")]

    if a.list:
        todo = []
        for f in packets:
            p = json.loads(f.read_text())
            done = json.loads((drive / f.name).read_text()) if (drive / f.name).exists() else {}
            todo += [{"net_id": p["net_id"], **g} for g in p.get("google_links", []) if g["file_id"] not in done]
        print(json.dumps(todo, indent=1))
        return

    merged = 0
    for f in packets:
        got = drive / f.name
        if not got.exists():
            continue
        p = json.loads(f.read_text())
        files = json.loads(got.read_text())
        p["drive_files"] = [{"file_id": k, "url": next((g["url"] for g in p.get("google_links", []) if g["file_id"] == k), ""),
                             "title": v.get("title"), "mime": v.get("mime"), "ok": bool(v.get("ok")),
                             "text": (v.get("text") or "")[:CAP] + ("\n[... truncated]" if len(v.get("text") or "") > CAP else ""),
                             "error": v.get("error")} for k, v in files.items()]
        f.write_text(json.dumps(p, indent=1))
        f.chmod(0o600)
        merged += 1
    print(f"merged Drive files into {merged} packets")


if __name__ == "__main__":
    main()
