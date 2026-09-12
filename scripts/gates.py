"""Copy gates, numbering gate, link check. Run: python scripts/gates.py dist"""
import io, re, sys
from pathlib import Path

BANNED = re.compile(r"\bleverage|\bseamless|\bempower|\bunlock\b|\brobust\b|actionable|data-driven|game-changer|synergy|circle back|best practices|dive into|at the end of the day|\bdelve|\belevate\b|testament", re.I)
IDENTITY = re.compile(r"orange ocean|disbar", re.I)
HEADLINE = re.compile(r"\b(Interview|Order|Layer|Phase|Level)\s+\d+\b|\bLayers?\b|\bPhases?\b")
# Every tag a reader scans as a headline: the full h1-h6 ladder (h4-h6 carry real
# sub-headings inside the document cards and the example pages), <title>, <figcaption>,
# and the drawn plates' own <span class="plate-label"> caption strip.
HEADLINE_TAGS = re.compile(
    r'<(h1|h2|h3|h4|h5|h6|title|figcaption)[^>]*>(.*?)</\1>'
    r'|<(span)\s+class="plate-label"[^>]*>(.*?)</\3>',
    re.S | re.I)


def headline_blocks(html):
    """Yield (tag label, inner html) for every headline-ish block in the page."""
    for m in HEADLINE_TAGS.finditer(html):
        if m.group(1):
            yield m.group(1), m.group(2)
        else:
            yield 'span class="plate-label"', m.group(4)
NAV_LINKS = re.compile(r"<nav[^>]*>(.*?)</nav>", re.S | re.I)
CONTENTS_LINKS = re.compile(r'<ol class="contents"[^>]*>(.*?)</ol>', re.S | re.I)
ALLOW_COPY = ("curriculum/read/",)
ALLOW_NUMBERING = ("lineage/", "curriculum/read/")

def _strip(s): return re.sub(r"<[^>]+>", " ", s)

def check_text(html, path):
    p = path.replace("\\", "/")
    out = []
    if not any(a in p for a in ALLOW_COPY):
        if "—" in html: out.append("%s: em dash x%d" % (p, html.count("—")))
        if "&mdash;" in html or "&#8212;" in html: out.append("%s: mdash entity" % p)
        for m in BANNED.finditer(_strip(html)): out.append("%s: banned word %r" % (p, m.group(0)))
        for m in IDENTITY.finditer(_strip(html)): out.append("%s: identity term %r" % (p, m.group(0)))
    if not any(a in p for a in ALLOW_NUMBERING):
        for tag, inner in headline_blocks(html):
            if HEADLINE.search(_strip(inner)): out.append("%s: numbering in <%s>: %r" % (p, tag, _strip(inner).strip()[:60]))
        for nav in NAV_LINKS.findall(html):
            for a in re.findall(r"<a[^>]*>(.*?)</a>", nav, re.S):
                if HEADLINE.search(_strip(a)): out.append("%s: numbering in nav: %r" % (p, _strip(a).strip()))
        for block in CONTENTS_LINKS.findall(html):
            for a in re.findall(r"<a[^>]*>(.*?)</a>", block, re.S):
                if HEADLINE.search(_strip(a)): out.append("%s: numbering in contents: %r" % (p, _strip(a).strip()))
        if HEADLINE.search(p.replace("-", " ")): out.append("%s: numbering in path" % p)
    return out

def check_links(dist):
    dist = Path(dist); errs = []
    for f in dist.rglob("*.html"):
        s = io.open(f, encoding="utf-8").read()
        for href in re.findall(r'href="([^"#]+?)(?:#[^"]*)?"', s):
            if href.startswith(("http", "mailto", "data:", "tel:")): continue
            t = (dist / href.lstrip("/")) if href.startswith("/") else (f.parent / href)
            t = Path(str(t).rstrip("/\\"))
            if t.is_dir(): t = t / "index.html"
            if not t.exists(): errs.append("%s -> %s" % (f.relative_to(dist), href))
    return errs

def run(dist):
    dist = Path(dist); errs = []
    for f in dist.rglob("*.html"):
        errs += check_text(io.open(f, encoding="utf-8").read(), str(f.relative_to(dist)))
    errs += ["broken link " + e for e in check_links(dist)]
    if errs:
        print("GATE FAILURES (%d):" % len(errs)); [print("  ", e) for e in errs]; return 1
    print("gates clean: %d pages" % len(list(dist.rglob("*.html")))); return 0

if __name__ == "__main__":
    sys.exit(run(sys.argv[1] if len(sys.argv) > 1 else "dist"))
