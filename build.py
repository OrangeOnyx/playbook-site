"""Render dist/ from spine.json + content/ + templates/. python build.py [out_dir]"""
import io, re, shutil, sys, datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
sys.path.insert(0, str(Path(__file__).resolve().parent))
from scripts import spine as S
from scripts.build_reader import LEVEL_TO_STAGE

ROOT = Path(__file__).resolve().parent
env = Environment(loader=FileSystemLoader(str(ROOT / "templates")), autoescape=select_autoescape([]), trim_blocks=True, lstrip_blocks=True)

READER_PREFIXES = {1: ("l1-",), 2: ("l2-",), 3: ("l3-", "l4-"), 4: ("l5-",)}
READER_GROUP_ORDER = ["overview", "start-here", "individual", "company", "shared", "repos", "eli10"]
READER_LEVEL_WORD = re.compile(r"\bLevel (\d+)\b")
READER_MODULE_FOLDER = re.compile(r"^l\d+-(?:individual|company)-(.+)$")
INDEX_SUFFIX = re.compile(r"index\.html$")

def partial(name):
    p = ROOT / "content" / name
    return io.open(p, encoding="utf-8").read() if p.exists() else ""

def _reader_title(raw_title, stem):
    """Sanitize a title pulled from a generated reader page before it is surfaced on a
    non-allowlisted stage page: the reader's own <title> text is the repo's verbatim
    voice (fine inside curriculum/read/, which is copy-gate allowlisted), but a bare
    "README" heading or a literal "Level N" reference reads as a leak once it is quoted
    on curriculum/<stage>/, so both are rewritten here."""
    title = raw_title.strip()
    if title == "README":
        m = READER_MODULE_FOLDER.match(stem)
        if m:
            title = m.group(1).replace("-", " ").title()
    title = title.replace("—", "-").replace("–", "-")  # this listing sits outside the reader's copy-gate allowlist
    def _stage_label(m):
        return "Stage %d" % LEVEL_TO_STAGE.get(int(m.group(1)), int(m.group(1)))
    title = READER_LEVEL_WORD.sub(_stage_label, title)
    return title

def reader_modules(stage_number):
    """Scan the generated reader pages for the given stage's modules: [(title, href), ...]."""
    prefixes = READER_PREFIXES.get(stage_number, ())
    d = ROOT / "content" / "generated" / "curriculum" / "read"
    if not prefixes or not d.exists():
        return []
    files = [f for f in d.glob("*.html") if f.name.startswith(prefixes)]
    def group_rank(name):
        for i, g in enumerate(READER_GROUP_ORDER):
            if g in name:
                return i
        return len(READER_GROUP_ORDER)
    files.sort(key=lambda f: (next(p for p in prefixes if f.name.startswith(p)), group_rank(f.name), f.name))
    out = []
    for f in files:
        html = io.open(f, encoding="utf-8").read()
        m = re.search(r"<title>(.*?)</title>", html, re.S)
        title = m.group(1).split(" | ")[0].strip() if m else f.stem
        title = _reader_title(title, f.stem)
        out.append((title, "/curriculum/read/" + f.name))
    return out

def pages(spine):
    secs = S.sections(spine)
    base = dict(spine=spine, sections=secs, partial=partial, year=datetime.date.today().year, stage=None, section=None)
    P = []
    def add(out, template, path, title, **ctx):
        c = dict(base); c.update(ctx); c.update(path=path, title=title); P.append({"out": out, "template": template, "ctx": c})
    add("index.html", "cover.html", "/", "The AI Playbook")
    for st in spine["stages"]:
        add("%s/index.html" % st["slug"], "stage.html", S.stage_path(st), "%d %s" % (st["number"], st["name"]), stage=st,
            stage_sections=[x for x in secs if x["stage"] == st["number"]])
    for x in secs:
        st = spine["stages"][x["stage"] - 1]
        add(x["path"].strip("/") + "/index.html", "section.html", x["path"], "%s %s" % (x["id"], x["title"]), stage=st, section=x)
    add("radar/index.html", "radar.html", "/radar/", "Readiness radar")
    add("templates/index.html", "templates.html", "/templates/", "Templates")
    add("plates/index.html", "plates.html", "/plates/", "Plates")
    add("lineage/index.html", "article.html", "/lineage/", "Lineage", body=partial("pages/lineage.html"))
    add("examples/personal-ai-os/index.html", "example.html", "/examples/personal-ai-os/", "Personal AI OS", body=partial("examples/personal-ai-os.html"), lane="personal")
    add("examples/cypress-command-platform/index.html", "example.html", "/examples/cypress-command-platform/", "Cypress Command Platform", body=partial("pages/platform.html"), lane="business")
    add("examples/operator-console/index.html", "example.html", "/examples/operator-console/", "Operator console", body=partial("pages/console.html"), lane="business")
    for cs in spine["stages"]:
        add("curriculum/%s/index.html" % cs["slug"], "curriculum-stage.html", "/curriculum/%s/" % cs["slug"], "Curriculum %d %s" % (cs["number"], cs["name"]), stage=cs,
            modules=reader_modules(cs["number"]))
    add("curriculum/index.html", "curriculum.html", "/curriculum/", "Curriculum")
    add("start/index.html", "start.html", "/start/", "Start")
    add("legal/index.html", "legal.html", "/legal/", "Disclaimer and privacy", body=partial("pages/legal.html"))
    add("404.html", "404.html", "/404.html", "Page not found")
    return P

def render(out_dir=None):
    out = Path(out_dir) if out_dir else ROOT / "dist"
    if out.exists(): shutil.rmtree(out)
    out.mkdir(parents=True)
    spine = S.load()
    errs = S.validate(spine)
    if errs: raise SystemExit("\n".join(errs))
    n = 0
    for p in pages(spine):
        tpl = ROOT / "templates" / p["template"]
        if not tpl.exists(): continue          # a later task adds it; the registry is complete now
        html = env.get_template(p["template"]).render(**p["ctx"])
        dest = out / p["out"]; dest.parent.mkdir(parents=True, exist_ok=True)
        io.open(dest, "w", encoding="utf-8", newline="\n").write(html); n += 1
    shutil.copytree(ROOT / "assets", out / "assets")
    for f in ("vercel.json", "favicon.ico", "apple-touch-icon.png"):
        shutil.copy(ROOT / f, out / f)
    (out / ".vercel").mkdir(); shutil.copy(ROOT / ".vercel" / "project.json", out / ".vercel" / "project.json")
    gen = ROOT / "content" / "generated" / "curriculum" / "read"   # written by scripts/build_reader.py (Wave 2)
    if gen.exists(): shutil.copytree(gen, out / "curriculum" / "read")
    # The registry's own pages, then every copied reader page. INDEX_SUFFIX is anchored to
    # the end of the path so a page whose directory happens to contain "index.html" as a
    # substring keeps its directory intact.
    urls = [spine["domain"] + ("/" if p["out"] == "index.html" else "/" + INDEX_SUFFIX.sub("", p["out"]))
            for p in pages(spine) if p["out"] != "404.html"]
    read_dir = out / "curriculum" / "read"
    if read_dir.exists():
        for f in sorted(read_dir.glob("*.html")):
            urls.append(spine["domain"] + "/curriculum/read/" + ("" if f.name == "index.html" else f.name))
    io.open(out / "sitemap.xml", "w", encoding="utf-8", newline="\n").write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
        "".join("<url><loc>%s</loc></url>\n" % u for u in urls) + "</urlset>\n")
    io.open(out / "robots.txt", "w", encoding="utf-8", newline="\n").write("User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % spine["domain"])
    io.open(out / "llms.txt", "w", encoding="utf-8", newline="\n").write(
        "# The AI Playbook\n\n> Four stages that install an AI operating system into your life and work. By Cypress Command. Free and complete.\n\n" +
        "".join("- [%s %s](%s/%s/)\n" % (s["number"], s["name"], spine["domain"], s["slug"]) for s in spine["stages"]) +
        "".join("- [%s %s](%s%s)\n" % (x["id"], x["title"], spine["domain"], x["path"]) for x in S.sections(spine)))
    return n

if __name__ == "__main__":
    print("rendered", render(sys.argv[1] if len(sys.argv) > 1 else None), "pages")
