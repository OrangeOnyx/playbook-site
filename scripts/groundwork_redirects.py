"""Write groundwork-site/vercel.json: every Groundwork path 308s into the playbook. Run after Wave 2 is live."""
import io, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import spine as S


def build(spine):
    dom = spine["domain"]
    rules = []
    seen_catch_all = False
    for r in spine["redirects"]:
        is_catch_all = "(.*)" in r["source"]
        if is_catch_all:
            seen_catch_all = True
        elif seen_catch_all:
            raise ValueError("literal redirect %r comes after a catch-all" % (r["source"],))
        rules.append({"source": r["source"], "destination": dom + r["destination"], "permanent": True})
    return {"redirects": rules}


if __name__ == "__main__":
    gw = Path(__file__).resolve().parents[2] / "groundwork-site"
    cfg = build(S.load())
    vercel_path = gw / "vercel.json"
    headers = None
    if vercel_path.exists():
        existing = json.loads(io.open(vercel_path, encoding="utf-8").read())
        headers = existing.get("headers")
    out = {}
    if headers:
        out["headers"] = headers
    out["redirects"] = cfg["redirects"]
    io.open(vercel_path, "w", encoding="utf-8", newline="\n").write(json.dumps(out, indent=2) + "\n")
    print("wrote", len(out["redirects"]), "redirects")
