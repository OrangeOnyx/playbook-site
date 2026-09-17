"""Redirects for the reader's old level-prefixed URLs (Wave 2) to the stage-prefixed ones (Wave 3).

python scripts/reader_redirects.py --derive   reads the old page names from git (the last commit
    before the reader was regenerated) and the curriculum's fold map, writes content/reader-renames.json
python scripts/reader_redirects.py            rewrites vercel.json from content/reader-renames.json,
    headers preserved (same merge as groundwork_redirects.merge_config)
"""
import io, json, re, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.groundwork_redirects import merge_config

ROOT = Path(__file__).resolve().parents[1]
RENAMES = ROOT / "content" / "reader-renames.json"
CONFIG = ROOT / "vercel.json"
FOLD_MAP = ROOT.parent / "ai-playbook-curriculum" / "history" / "fold-map-2026-09.json"
READ = "/curriculum/read/"
OLD = re.compile(r"^l([1-5])-(overview|start-here|shared|repos|eli10|(individual|company)-(.+))$")
LEVEL_DIR = {"1": "level-1-essentials", "2": "level-2-intermediate", "3": "level-3-advanced",
             "4": "level-4-professional", "5": "level-5-frontier"}


def new_slug(old, fold_map):
    m = OLD.match(old)
    if not m:
        return old
    lv, group, track, mod = m.group(1), m.group(2), m.group(3), m.group(4)
    stage = fold_map["levels"][LEVEL_DIR[lv]]
    num = stage.split("-", 1)[0]
    if track:
        new_dir = fold_map["paths"].get("%s/%s/%s" % (LEVEL_DIR[lv], track, mod))
        if not new_dir:
            raise KeyError("fold map has no entry for module %s/%s/%s" % (LEVEL_DIR[lv], track, mod))
        return "%s-%s-%s" % (num, track, new_dir.rsplit("/", 1)[1])
    return "%s-%s" % (num, group)


def derive(old_names, fold_map):
    out = {}
    for name in old_names:
        if not name.endswith(".html") or name == "index.html":
            continue
        slug = name[:-5]
        new = new_slug(slug, fold_map)
        if new != slug:
            out[slug] = new
    return out


def rules(renames):
    return [{"source": READ + old + ".html", "destination": READ + new + ".html", "permanent": True}
            for old, new in sorted(renames.items())]


def build_config(renames):
    existing = json.load(io.open(CONFIG, encoding="utf-8")) if CONFIG.exists() else {}
    return merge_config(existing, rules(renames))


def main(argv):
    if "--derive" in argv:
        rev = argv[argv.index("--derive") + 1] if len(argv) > argv.index("--derive") + 1 else "HEAD"
        listing = subprocess.run(["git", "ls-tree", "--name-only", rev, "content/generated/curriculum/read/"],
                                 cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
        names = [p.rsplit("/", 1)[1] for p in listing]
        fold_map = json.load(io.open(FOLD_MAP, encoding="utf-8"))
        renames = derive(names, fold_map)
        io.open(RENAMES, "w", encoding="utf-8", newline="\n").write(json.dumps(renames, indent=1, sort_keys=True) + "\n")
        print("wrote %d renames" % len(renames))
        return
    renames = json.load(io.open(RENAMES, encoding="utf-8"))
    cfg = build_config(renames)
    io.open(CONFIG, "w", encoding="utf-8", newline="\n").write(json.dumps(cfg, indent=2) + "\n")
    print("wrote vercel.json: %d redirects, headers preserved" % len(cfg["redirects"]))


if __name__ == "__main__":
    main(sys.argv[1:])
