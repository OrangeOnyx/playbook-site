"""Render dist/ from spine.json + content/ + templates/. python build.py [out_dir]"""
import io, shutil, sys, datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
sys.path.insert(0, str(Path(__file__).resolve().parent))
from scripts import spine as S

ROOT = Path(__file__).resolve().parent
env = Environment(loader=FileSystemLoader(str(ROOT / "templates")), autoescape=select_autoescape([]), trim_blocks=True, lstrip_blocks=True)

def partial(name):
    p = ROOT / "content" / name
    return io.open(p, encoding="utf-8").read() if p.exists() else ""

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
        add("curriculum/%s/index.html" % cs["slug"], "curriculum-stage.html", "/curriculum/%s/" % cs["slug"], "Curriculum %d %s" % (cs["number"], cs["name"]), stage=cs)
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
    return n

if __name__ == "__main__":
    print("rendered", render(sys.argv[1] if len(sys.argv) > 1 else None), "pages")
