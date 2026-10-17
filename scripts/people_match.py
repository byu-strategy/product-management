"""Match a GitHub username, Slack handle, or stray email back to a student on the roster.

Students do not use their BYU identity everywhere. They sign up for Slack with a personal or
law-school address, name a GitHub account after a childhood nickname, and clone a repo without
renaming it. Exact email matching finds most of them and silently loses the rest, and a lost
student looks identical to a student who did nothing, which is the failure that matters: it
sends "you're missing the assignment" to someone who finished it.

Every match carries how it was made, so a weak one can be reviewed rather than trusted:

    email       exact BYU email, certain
    netid       the handle, or the local part of another address, is the NetID itself
                (hure2@student.byu.edu, or a Slack handle of "hure2"), also certain
    handle      the handle contains both name parts (hudsonroney18 -> Hudson Roney),
                including run together with no separator and with the first name shortened
                (alexsisk25 -> Alexander Sisk)
    name        full name matched exactly, and only one student has that name
    none        no match; the caller decides what to do

This file holds no student data.
"""
import re

STOP = {"byu", "msb341", "msb", "341", "builder", "template", "student", "the"}
# Generational suffixes sit where the surname goes in "Wait II, Scott Daniel", so they have to
# come off before anything reads the last name.
SUFFIXES = {"ii", "iii", "iv", "v", "jr", "sr"}


def norm(s):
    """Lowercase, drop punctuation and digits, collapse whitespace."""
    return re.sub(r"\s+", " ", re.sub(r"[^a-z ]+", " ", (s or "").lower())).strip()


def tokens(s):
    return [t for t in norm(s).split() if len(t) > 1 and t not in STOP]


def name_parts(student):
    """Given names and surname, from the roster's "Last, First Middle" field.

    Returns every given name, not just the first, because students go by their middle name
    often enough to matter ("Wait II, Scott Daniel" signs up as danielwait).
    """
    sortable = student.get("sortable_name", "")
    last, _, first = sortable.partition(",")
    surname = [t for t in tokens(last) if t not in SUFFIXES]
    return tokens(first), (surname[-1] if surname else "")


def index(students):
    """Build the lookup tables once, for repeated matching."""
    by_email, by_name, by_netid = {}, {}, {}
    for s in students:
        if s.get("email"):
            by_email[s["email"].strip().lower()] = s
        if s.get("net_id"):
            by_netid[s["net_id"].strip().lower()] = s
        full = " ".join(tokens(s.get("name", "")))
        if full:
            by_name.setdefault(full, []).append(s)
    return {"students": list(students), "by_email": by_email, "by_name": by_name,
            "by_netid": by_netid}


def find(idx, email="", handle="", display=""):
    """Best match for one outside identity. Returns (student or None, how)."""
    if email:
        s = idx["by_email"].get(email.strip().lower())
        if s:
            return s, "email"

    # BYU issues one NetID per person, so it identifies a student exactly wherever it appears:
    # as the local part of a non-byu.edu address (hure2@student.byu.edu) or as a handle chosen
    # to match it. Students sign up for Slack with the student.byu.edu alias often enough that
    # missing this looks like "never joined" for someone sitting in the workspace.
    for candidate in (email.split("@")[0], handle, display):
        s = idx["by_netid"].get((candidate or "").strip().lower())
        if s:
            return s, "netid"

    # A handle or display name that contains both a first and last name is decisive enough:
    # "hudsonroney18", "lauren.warner", "Jaxon-White" all resolve, and a collision needs two
    # students to share both names.
    blob = set(tokens(handle)) | set(tokens(display)) | set(tokens(email.split("@")[0]))
    if blob:
        hits = []
        for s in idx["students"]:
            givens, last = name_parts(s)
            if last and last in blob and any(g in blob for g in givens):
                hits.append(s)
        if len(hits) == 1:
            return hits[0], "handle"

    # Run-together handles have nothing to tokenize on, so fall back to substrings of the
    # squashed handle. The last name must appear in full; the first name may be shortened, as
    # students do ("alexsisk25" for Alexander Sisk). A unique hit is still required, so a
    # shared surname does not produce a wrong match, it produces no match.
    squashed = re.sub(r"[^a-z]", "", f"{handle}{display}".lower())
    if len(squashed) >= 6:
        hits = []
        for s in idx["students"]:
            givens, last = name_parts(s)
            if len(last) < 3:
                continue
            # Only one end of the name may be shortened at a time. Either the surname is
            # present in full and the given name may be a nickname of three characters or more
            # (samttran -> Samuel Tran), or the given name is present in full and the surname
            # may be clipped (nathanfrisch -> Nathan Frischknecht). Allowing both at once
            # matches far too much. Uniqueness is the backstop either way: an ambiguous handle
            # yields no match rather than a wrong one.
            last_full = last in squashed
            last_part = len(last) >= 5 and last[:5] in squashed
            given_full = any(g in squashed for g in givens)
            given_part = any(len(g) >= 3 and g[:3] in squashed for g in givens)
            if (last_full and given_part) or (last_part and given_full):
                hits.append(s)
        if len(hits) == 1:
            return hits[0], "handle"

    for value in (display, handle):
        full = " ".join(tokens(value))
        if full and len(idx["by_name"].get(full, [])) == 1:
            return idx["by_name"][full][0], "name"

    return None, "none"
