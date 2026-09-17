# The AI Playbook curriculum reader.
# Compiles the ai-playbook-curriculum repo working tree VERBATIM into
# content/generated/curriculum/read/*.html: one page per module folder, plus
# orientation, shared, per-stage overview / start-here / shared / repos / eli10
# pages and a contents page. Same reading order and the same illustration
# plates (gw_plates.py), with the shell speaking the playbook's four stages
# directly (via spine.json's "curriculum" key, one repository folder per stage).
# CONTENT IS THE REPO'S OWN VOICE: the site copy gate deliberately does not
# run on curriculum/read/ (see scripts/gates.py ALLOW_COPY); the numbering
# gate does run there (ALLOW_NUMBERING no longer exempts this path).
# build.py owns the sitemap; this module does not touch it.
# Usage: python scripts/build_reader.py [repo-path] [out-path]

import io
import re
import shutil
import sys
from pathlib import Path

import markdown
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import spine as S
from scripts.gw_plates import group_device, GROUPS, climb_line

_sp = S.load()
STAGE_NAME = {int(k): "%s %s" % (k, v["name"]) for k, v in _sp["curriculum"].items()}
STAGE_SLUG = {s["number"]: s["slug"] for s in _sp["stages"]}
# (number, repository folder, "N Name"), in climbing order. The folder is the stage slug.
STAGES = [(int(k), v["folder"], STAGE_NAME[int(k)]) for k, v in sorted(_sp["curriculum"].items())]

GH = "https://github.com/OrangeOnyx/ai-playbook-curriculum"
BOOK = GH + "/releases/latest/download/The-AI-Playbook-Curriculum.pdf"
BASE_URL = "https://playbook.adamabdalla.com/curriculum/read/"

MD = markdown.Markdown(extensions=["tables", "fenced_code"])

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} | The AI Playbook Curriculum Reader</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#F4EFE2">
<script>(function(){{var d=document.documentElement;try{{if(localStorage.getItem('gw-theme')==='night')d.setAttribute('data-theme','night')}}catch(e){{}}window.gwTheme=function(){{var n=d.getAttribute('data-theme')==='night';if(n){{d.removeAttribute('data-theme')}}else{{d.setAttribute('data-theme','night')}}try{{localStorage.setItem('gw-theme',n?'day':'night')}}catch(e){{}}s()}};function s(){{var n=d.getAttribute('data-theme')==='night';document.querySelectorAll('.modeswitch').forEach(function(b){{b.textContent=n?'DAY':'NIGHT';b.setAttribute('aria-pressed',n?'true':'false')}});var m=document.querySelector('meta[name="theme-color"]');if(m)m.setAttribute('content',n?'#1B1813':'#F4EFE2')}}window.addEventListener('DOMContentLoaded',s)}})()</script>
<link rel="canonical" href="{base_url}{slug}.html">
<meta property="og:image" content="https://playbook.adamabdalla.com/assets/og-card.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="/favicon.ico">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700;900&family=Besley:ital,wght@0,400;0,700;0,900;1,400;1,600&family=Courier+Prime:wght@400;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/guide.css">
<link rel="stylesheet" href="/assets/playbook-import.css">
<link rel="stylesheet" href="/assets/playbook.css">
</head>
<body class="reader">
<a class="skip" href="#main">Skip to content</a>
<nav class="top" aria-label="Curriculum reader">
  <a class="brand" href="/" aria-label="The AI Playbook home">
    <b>THE AI PLAYBOOK</b>
  </a>
  <button class="modeswitch" onclick="gwTheme()" aria-pressed="false" aria-label="Switch between day and night">NIGHT</button>
  <button class="navtoggle" aria-expanded="false" aria-label="Stages" onclick="var l=this.nextElementSibling,o=l.classList.toggle('open');this.setAttribute('aria-expanded',o)">MENU</button>
  <div class="links">
    {nav}
  </div>
</nav>
<main id="main" tabindex="-1">
  <span class="crumb"><a href="/curriculum/">The Curriculum</a> / <a href="index.html">Reader</a> / {crumbleaf}</span>
"""

FOOT = """
  <div class="pnav">
    <a href="{prev_href}">← {prev_label}</a>
    <a href="{next_href}">{next_label} →</a>
  </div>
</main>
<footer class="site"><div class="passiton">Pass it on: <button class="btn btn-ghost pbtn" onclick="navigator.clipboard.writeText(location.href);this.textContent='Copied'">Copy link</button> <a href="mailto:?subject=The%20AI%20Playbook&amp;body=A free, ungated AI readiness system for owners and operators: https://playbook.adamabdalla.com">Send to a fellow owner</a> · <a href="https://github.com/OrangeOnyx/ai-playbook-curriculum">Curriculum on GitHub</a></div>
The AI Playbook. Free, complete, ungated. By Cypress Command. <a href="mailto:adam@adamabdalla.com">adam@adamabdalla.com</a> · <a href="/legal/">Disclaimer &amp; Privacy</a></footer>
<script defer src="/assets/motion.js"></script>
<script defer src="/_vercel/insights/script.js"></script>
</body>
</html>
"""

_GROUP_ORDER = ["overview", "start-here", "individual", "company", "shared", "repos", "eli10"]


def run(repo=None, out=None):
    repo = Path(repo) if repo else ROOT.parent / "ai-playbook-curriculum"
    out = Path(out) if out else ROOT / "content" / "generated" / "curriculum" / "read"
    if out.exists():
        shutil.rmtree(out)   # full regen: a prior run's slugs (e.g. the retired l1-... scheme) must not survive
    out.mkdir(parents=True, exist_ok=True)
    assets = out / "assets"

    def rel_md_files(subdir):
        d = repo / subdir
        if not d.is_dir():
            return []
        files = sorted(d.rglob("*.md"), key=lambda p: (
            tuple(s.lower() for s in p.relative_to(repo).parts[:-1]),
            0 if p.name == "README.md" else 1, p.name.lower()))
        return [str(p.relative_to(repo)).replace("\\", "/") for p in files]

    def humanize(slug):
        s = re.sub(r"^\d+-", "", slug)
        return s.replace("-", " ").title().replace("Eli10", "ELI10").replace("Ai ", "AI ").replace("Mcp", "MCP").replace("Rag", "RAG")

    def first_h1(relpath):
        try:
            for line in (repo / relpath).read_text(encoding="utf-8", errors="replace").splitlines():
                if line.startswith("# "):
                    return re.sub(r"[#*`]", "", line[2:]).strip()
        except OSError:
            pass
        return None

    # ---------- build the ordered page list ----------
    pages = []  # dicts: slug,title,kicker,gkey,files,ghdir,stage

    def add(slug, title, kicker, gkey, files, ghdir, stage=None):
        if files:
            pages.append(dict(slug=slug, title=title, kicker=kicker, gkey=gkey,
                              files=files, ghdir=ghdir, stage=stage))

    add("orientation", "Read this first", "ORIENTATION", "overview",
        [f for f in ["README.md", "PLAYBOOK-AND-CURRICULUM.md", "STAGE-MAP.md"] if (repo / f).exists()],
        GH)
    add("shared-cover-letter", "The cover letters", "SHARED MATERIALS", "shared",
        rel_md_files("shared/cover-letter"), f"{GH}/tree/master/shared/cover-letter")
    add("shared-starter-packs", "The starter packs", "SHARED MATERIALS", "shared",
        rel_md_files("shared/starter-packs"), f"{GH}/tree/master/shared/starter-packs")

    for num, folder, stage_name in STAGES:
        kick = stage_name.upper()
        add(f"{num}-overview", f"{stage_name} at a glance", kick, "overview",
            [f"{folder}/README.md"], f"{GH}/tree/master/{folder}", num)
        add(f"{num}-start-here", "Start here", kick, "start-here",
            rel_md_files(f"{folder}/00-start-here"), f"{GH}/tree/master/{folder}/00-start-here", num)
        for track in ("individual", "company"):
            tdir = repo / folder / track
            if not tdir.is_dir():
                continue
            for mod in sorted(p for p in tdir.iterdir() if p.is_dir()):
                mrel = f"{folder}/{track}/{mod.name}"
                title = first_h1(f"{mrel}/README.md") or humanize(mod.name)
                add(f"{num}-{track}-{mod.name}", title,
                    f"{kick} · {track.upper()} TRACK", track,
                    rel_md_files(mrel), f"{GH}/tree/master/{mrel}", num)
        add(f"{num}-shared", f"{stage_name} shared materials", kick, "shared",
            rel_md_files(f"{folder}/shared"), f"{GH}/tree/master/{folder}/shared", num)
        add(f"{num}-repos", "Working repositories", kick, "repos",
            rel_md_files(f"{folder}/repos"), f"{GH}/tree/master/{folder}/repos", num)
        add(f"{num}-eli10", f"{stage_name} ELI10 companions", kick, "eli10",
            rel_md_files(f"{folder}/eli10"), f"{GH}/tree/master/{folder}/eli10", num)

    add("appendix", "Contributing, and the license", "APPENDIX", "shared",
        [f for f in ["CONTRIBUTING.md"] if (repo / f).exists()], GH)

    FILE_PAGE = {}
    for pg in pages:
        for f in pg["files"]:
            FILE_PAGE.setdefault(f, pg["slug"])

    # ---------- markdown rendering with link/image rewriting ----------
    if assets.exists():
        shutil.rmtree(assets)
    assets.mkdir(parents=True, exist_ok=True)

    def copy_asset(repo_rel):
        src = repo / repo_rel
        if not src.exists():
            return None
        flat = repo_rel.replace("/", "--")
        if src.suffix.lower() in (".svg",):
            dst = assets / flat
            shutil.copyfile(src, dst)
        else:
            flat = re.sub(r"\.(png|jpg|jpeg|webp)$", ".jpg", flat, flags=re.I)
            dst = assets / flat
            im = Image.open(src).convert("RGB")
            if im.width > 1400:
                im = im.resize((1400, int(im.height * 1400 / im.width)), Image.LANCZOS)
            im.save(dst, "JPEG", quality=80)
        return "assets/" + flat

    def resolve(base, href):
        href = re.sub(r"^(\./)+", "", href)
        parts = base.split("/") if base else []
        while href.startswith("../"):
            href = href[3:]
            parts = parts[:-1]
        return "/".join(parts + [href]) if parts else href

    def render_file(relpath, gkey):
        text = (repo / relpath).read_text(encoding="utf-8", errors="replace")
        base = relpath.rsplit("/", 1)[0] if "/" in relpath else ""

        def fix_img(m):
            alt, src = m.group(1), m.group(2)
            if src.startswith("http"):
                return m.group(0)
            rel = resolve(base, src)
            local = copy_asset(rel)
            return f"![{alt}]({local})" if local else f"*[image: {alt}]*"

        def fix_link(m):
            label, href = m.group(1), m.group(2)
            if href.startswith(("http", "mailto:", "#")):
                return m.group(0)
            target, _, anchor = href.partition("#")
            rel = resolve(base, target)
            if rel in FILE_PAGE:
                return f"[{label}]({FILE_PAGE[rel]}.html)"
            if rel.endswith(".md") and (repo / rel).exists():
                return f"[{label}]({GH}/blob/master/{rel})"
            return f"[{label}]({GH}/tree/master/{rel.rstrip('/')})"

        text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", fix_img, text)
        text = re.sub(r"(?<!\!)\[([^\]]+)\]\(([^)]+)\)", fix_link, text)
        MD.reset()
        html = MD.convert(text)
        dev = group_device(gkey, 16)
        return (f'<article class="doc"><p class="fcrumb">{dev}<span>{relpath}</span></p>\n'
                f"{html}\n</article>")

    # ---------- page shell ----------
    def nav_html(stage_num):
        links = ['<a href="/curriculum/">Curriculum</a>']
        for st in _sp["stages"]:
            cur = ' aria-current="page"' if st["number"] == stage_num else ""
            links.append(f'<a href="/curriculum/{st["slug"]}/"{cur}>{st["number"]}</a>')
        links.append('<a href="index.html">Reader</a>')
        links.append('<a class="keep" href="/">Main site</a>')
        return "\n    ".join(links)

    out.mkdir(parents=True, exist_ok=True)

    # ---------- write section pages ----------
    for i, pg in enumerate(pages):
        prev = pages[i - 1] if i > 0 else None
        nxt = pages[i + 1] if i + 1 < len(pages) else None
        body = [HEAD.format(title=pg["title"], slug=pg["slug"], base_url=BASE_URL,
                            desc=f"{pg['kicker'].title()}: {pg['title']}. Compiled verbatim from The AI Playbook Curriculum repository.",
                            nav=nav_html(pg["stage"]), crumbleaf=pg["title"])]
        body.append(f'<div class="gopen">{group_device(pg["gkey"], 44)}'
                    f'<div><span class="kicker" style="margin-bottom:.15rem">{pg["kicker"]}</span>'
                    f'<h1 style="margin:.1rem 0 0">{pg["title"]}</h1></div></div>')
        if pg["gkey"] == "overview" and pg["stage"] is not None:
            body.append(f'<p class="rnote">Deeper on this stage on the main site: '
                        f'<a href="/curriculum/{STAGE_SLUG[pg["stage"]]}/">{STAGE_NAME[pg["stage"]]}</a>.</p>')
        nfiles = len(pg["files"])
        body.append(f'<p class="rnote">This page compiles {nfiles} file{"s" if nfiles != 1 else ""} '
                    f'from the repository, verbatim, in reading order. The living version: '
                    f'<a href="{pg["ghdir"]}">this folder on GitHub</a>.</p>')
        for f in pg["files"]:
            body.append(render_file(f, pg["gkey"]))
        body.append(FOOT.format(
            prev_href=(prev["slug"] + ".html") if prev else "index.html",
            prev_label=prev["title"] if prev else "Reader contents",
            next_href=(nxt["slug"] + ".html") if nxt else "index.html",
            next_label=nxt["title"] if nxt else "Reader contents"))
        (out / (pg["slug"] + ".html")).write_text("\n".join(body), encoding="utf-8", newline="\n")

    # ---------- contents page ----------
    toc = [HEAD.format(title="The Reader", slug="index", base_url=BASE_URL,
                       desc="The whole curriculum, readable on this site: every stage, track, and module, compiled verbatim from the repository.",
                       nav=nav_html(None), crumbleaf="Contents")]
    toc.append('<header class="page"><span class="kicker">THE READER</span>'
               '<h1>The whole curriculum, on this site.</h1>'
               '<p class="lede">Every stage, both tracks, every module and companion, compiled '
               'verbatim from the repository in reading order. Nothing summarized, nothing gated. '
               'Prefer it bound? <a href="' + BOOK + '">The book</a> is the same content. '
               'Prefer the living files? <a href="' + GH + '">The repo</a> is the source of truth.</p></header>')
    toc.append(f'<nav class="vw journeystrip" aria-label="Curriculum stages">{climb_line(None)}</nav>')
    cur_kick = None
    for pg in pages:
        if pg["kicker"] != cur_kick:
            if cur_kick is not None:
                toc.append("</div>")
            cur_kick = pg["kicker"]
            toc.append(f'<h2 style="margin-top:2.4rem">{cur_kick.title().replace("Eli10", "ELI10")}</h2><div>')
        n = len(pg["files"])
        toc.append(f'<div class="trow"><span class="tdev">{group_device(pg["gkey"], 20)}</span>'
                   f'<a href="{pg["slug"]}.html">{pg["title"]}</a>'
                   f'<span class="tcount">{n} file{"s" if n != 1 else ""}</span></div>')
    toc.append("</div>")
    toc.append(FOOT.format(prev_href="/curriculum/", prev_label="The Curriculum",
                           next_href="orientation.html", next_label="Read this first"))
    (out / "index.html").write_text("\n".join(toc), encoding="utf-8", newline="\n")

    import subprocess
    sha = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    (out / "SOURCE").write_text(sha + "\n", encoding="utf-8", newline="\n")

    return len(pages) + 1


if __name__ == "__main__":
    repo_arg = sys.argv[1] if len(sys.argv) > 1 else None
    out_arg = sys.argv[2] if len(sys.argv) > 2 else None
    n = run(repo_arg, out_arg)
    print(f"reader: {n} pages")
