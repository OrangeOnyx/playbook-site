"""Write groundwork-site/vercel.json and groundwork-site/redirect-check.json.

Every Groundwork path redirects into The AI Playbook. The retirement runs in two steps:
step 1 publishes the rules as temporary 307s (`--permanent false`), which browsers and
caches do not keep, so the flip can be walked and, if anything is wrong, undone; step 2
promotes the same rules to permanent 308s (`--permanent true`, the default) once the walk
has passed. redirect-check.json is the machine-readable list of literal source ->
destination pairs the deploy script pre-flights and then walks.
"""
import argparse, io, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import spine as S


def build(spine, permanent=True):
    dom = spine["domain"]
    rules = []
    seen_catch_all = False
    for r in spine["redirects"]:
        is_catch_all = "(.*)" in r["source"]
        if is_catch_all:
            seen_catch_all = True
        elif seen_catch_all:
            raise ValueError("literal redirect %r comes after a catch-all" % (r["source"],))
        rules.append({"source": r["source"], "destination": dom + r["destination"], "permanent": bool(permanent)})
    return {"redirects": rules}


def check_rules(rules):
    """The literal rules only, as {"source", "destination"}: a catch-all's destination
    carries a $1 backreference, so there is no single URL to request for it."""
    return [{"source": r["source"], "destination": r["destination"]}
            for r in rules if "(.*)" not in r["source"]]


def merge_config(existing, rules):
    headers = (existing or {}).get("headers")
    out = {}
    if headers:
        out["headers"] = headers
    out["redirects"] = rules
    return out


def parse_args(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--permanent", choices=("true", "false"), default="true",
                    help="308 permanent redirects (default) or 307 temporary ones")
    return ap.parse_args(argv)


if __name__ == "__main__":
    args = parse_args()
    permanent = args.permanent == "true"
    gw = Path(__file__).resolve().parents[2] / "groundwork-site"
    cfg = build(S.load(), permanent=permanent)
    vercel_path = gw / "vercel.json"
    existing = None
    if vercel_path.exists():
        existing = json.loads(io.open(vercel_path, encoding="utf-8").read())
    out = merge_config(existing, cfg["redirects"])
    io.open(vercel_path, "w", encoding="utf-8", newline="\n").write(json.dumps(out, indent=2) + "\n")
    checks = check_rules(out["redirects"])
    io.open(gw / "redirect-check.json", "w", encoding="utf-8", newline="\n").write(json.dumps(checks, indent=2) + "\n")
    print("wrote", len(out["redirects"]), "redirects (%s) and %d literal checks"
          % ("308 permanent" if permanent else "307 temporary", len(checks)))
