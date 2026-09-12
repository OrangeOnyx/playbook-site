"""Import Groundwork (sibling clone, pinned commit) into content partials. Idempotent."""
import io, posixpath, re, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import spine as S

PINNED = "c60fb73"
ORDER_PAGES = {"identity": "guide/identity.html", "knowledge": "guide/knowledge.html", "remember": "guide/remember.html",
               "limits": "guide/limits.html", "operator": "guide/operator.html", "improve": "guide/improve.html"}
FRONT = {"sound-familiar": "sound-familiar", "rule": "rule", "authority": "authority", "faq": "faq", "who": "who"}
PAGES = {"lineage": "guide/lineage.html", "platform": "guide/atlas.html", "console": "guide/dashboard.html", "legal": "legal.html"}
DOC_CARD = re.compile(r'<div class="card">\s*(?:<span class="fig ico stamp"[^>]*>.*?</span>\s*)?<h3>(Document (\d+):[^<]*)</h3>.*?</div>', re.S)

def _read(p): return io.open(p, encoding="utf-8").read()
def _write(p, s):
    p.parent.mkdir(parents=True, exist_ok=True)
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)

def _assert_commit(gw):
    head = subprocess.check_output(["git", "-C", str(gw), "rev-parse", "--short", "HEAD"], text=True).strip()
    if not head.startswith(PINNED):
        raise SystemExit("groundwork-site is at %s, expected %s" % (head, PINNED))

def _main_inner(html):
    m = re.search(r"<main[^>]*>(.*?)</main>", html, re.S)
    return m.group(1)

def _strip_chrome(inner, strip_header=True):
    inner = re.sub(r'<span class="crumb">.*?</span>', "", inner, count=1, flags=re.S)
    inner = re.sub(r'<nav class="vw journeystrip.*?</nav>', "", inner, count=1, flags=re.S)
    if strip_header:
        inner = re.sub(r'<header class="page pagehead">.*?</header>', "", inner, count=1, flags=re.S)
    return inner

def _rewrite_links(inner, base_dir, spine):
    table = {r["source"]: r["destination"] for r in spine["redirects"] if "(" not in r["source"]}
    def sub(m):
        href = m.group(1)
        if href.startswith(("http", "mailto", "#", "data:")): return m.group(0)
        path, frag = (href.split("#", 1) + [""])[:2]
        joined = (Path(base_dir) / path).as_posix()
        norm = "/" + posixpath.normpath(joined).lstrip("/")
        dest = table.get(norm)
        if dest is None and norm.startswith("/assets/"): dest = norm
        if dest is None: dest = norm
        return 'href="%s%s"' % (dest, ("#" + frag) if frag and "#" not in dest else "")
    return re.sub(r'href="([^"]+)"', sub, inner)

RENAME = [
    (r"https?://orangeoceanatlas\.com[^\"\s<]*", "https://otb.cypresscommand.com"),
    (r"The Atlas story\.", "The Cypress Command Platform story."),
    (r"\bAtlas\b", "Cypress Command Platform"),
]

def _rename_platform(inner):
    for pat, rep in RENAME: inner = re.sub(pat, rep, inner)
    note = ('<p class="prov">Cypress Command Platform was formerly Atlas, renamed in September 2026. '
            'The screenshots on this page were captured before the rename and still show the old name in frame; '
            'they run on a demonstration dataset.</p>')
    return re.sub(r"(<h1>.*?</h1>)", r"\1" + note, inner, count=1, flags=re.S)

def run(gw, out):
    _assert_commit(gw)
    spine = S.load()
    counts = {"articles": 0, "docs": 0, "front": 0, "pages": 0}
    for slug, rel in ORDER_PAGES.items():
        inner = _strip_chrome(_main_inner(_read(gw / rel)))
        for m in DOC_CARD.finditer(inner):
            _write(out / "content" / "docs" / ("doc-%s.html" % m.group(2).zfill(2)), _rewrite_links(m.group(0), "guide", spine))
            counts["docs"] += 1
        inner = DOC_CARD.sub("", inner)
        _write(out / "content" / "articles" / (slug + ".html"), _rewrite_links(inner, "guide", spine))
        counts["articles"] += 1
    home = _read(gw / "index.html")
    for slug, sid in FRONT.items():
        m = re.search(r'<section[^>]*id="%s"[^>]*>(.*?)</section>' % sid, home, re.S)
        _write(out / "content" / "front" / ("gw-%s.html" % slug), _rewrite_links(m.group(1), ".", spine))
        counts["front"] += 1
    for slug, rel in PAGES.items():
        inner = _strip_chrome(_main_inner(_read(gw / rel)), strip_header=False)
        inner = _rewrite_links(inner, str(Path(rel).parent), spine)
        if slug == "platform": inner = _rename_platform(inner)
        _write(out / "content" / "pages" / (slug + ".html"), inner)
        counts["pages"] += 1
    return counts

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(run(root.parent / "groundwork-site", root))
