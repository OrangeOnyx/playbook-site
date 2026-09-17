"""The one source of numbering. Everything reads spine.json through here."""
import io, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPINE = ROOT / "spine.json"
BANNED_HEADLINE = re.compile(r"\b(Interview|Order|Layer|Phase|Level)\s+\d+\b|\bLayers?\b|\bPhases?\b")

def load(path=None):
    p = Path(path) if path else SPINE
    return json.loads(io.open(p, encoding="utf-8").read())

def sections(spine):
    out = []
    for stage in spine["stages"]:
        for x in spine["sections"]:
            if x["stage"] == stage["number"]:
                x = dict(x)
                x["path"] = "/%s/%s/" % (stage["slug"], x["slug"])
                x["stage_slug"] = stage["slug"]
                x["stage_name"] = stage["name"]
                out.append(x)
    return out

def by_id(spine, sid):
    for x in sections(spine):
        if x["id"] == sid:
            return x
    raise KeyError(sid)

def stage_path(stage):
    return "/%s/" % stage["slug"]

def validate(spine):
    errs = []
    nums = [s["number"] for s in spine["stages"]]
    if nums != [1, 2, 3, 4]:
        errs.append("stages must be numbered 1..4, got %r" % nums)
    seen = set()
    for x in spine["sections"]:
        sid = x["id"]
        if sid in seen: errs.append("duplicate section id " + sid)
        seen.add(sid)
        if not re.fullmatch(r"[1-4]\.\d", sid): errs.append("bad id " + sid)
        if int(sid[0]) != x["stage"]: errs.append("stage mismatch " + sid)
        want = sid.replace(".", "-") + "-"
        if not x["slug"].startswith(want): errs.append("slug %s must start with %s" % (x["slug"], want))
        for k in ("title", "provenance", "cards", "lanes", "artifacts"):
            if not x.get(k): errs.append("section %s missing %s" % (sid, k))
        if BANNED_HEADLINE.search(x["title"]): errs.append("title carries old numbering: " + x["title"])
        for lane in ("personal", "business"):
            if not x.get("lanes", {}).get(lane): errs.append("section %s missing %s lane" % (sid, lane))
    ids = [x["id"] for x in sections(spine)]
    if ids != sorted(ids): errs.append("sections out of order: %r" % ids)
    slugs = {str(s["number"]): s["slug"] for s in spine["stages"]}
    cur = spine.get("curriculum", {})
    if sorted(cur) != ["1", "2", "3", "4"]:
        errs.append("curriculum must map stages 1..4, got %r" % sorted(cur))
    for k, v in cur.items():
        if v.get("folder") != slugs.get(k):
            errs.append("curriculum folder for stage %s must be the stage slug %r, got %r" % (k, slugs.get(k), v.get("folder")))
    seen_catch_all = False
    for r in spine["redirects"]:
        if not r["source"].startswith("/") or not r["destination"].startswith("/"):
            errs.append("redirect must be root-relative: %r" % r)
        if "(.*)" in r["source"]:
            seen_catch_all = True
        elif seen_catch_all:
            errs.append("literal redirect %r comes after a catch-all" % r["source"])
    return errs

if __name__ == "__main__":
    e = validate(load())
    print("\n".join(e) if e else "spine valid: %d stages, %d sections" % (4, len(load()["sections"])))
    raise SystemExit(1 if e else 0)
