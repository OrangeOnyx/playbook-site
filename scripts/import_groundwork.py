"""Import Groundwork (sibling clone, pinned commit) into content partials. Idempotent.

PINNED guards the SOURCE CONTENT this import was built against, not the exact
HEAD of the sibling clone. groundwork-site may move ahead with commits that
don't touch the paths this import reads (guide/, index.html, legal.html,
assets/) -- deploy tooling, config, etc. -- without invalidating the pin.
_assert_commit checks that (1) PINNED is still an ancestor of HEAD and (2)
none of the guarded paths differ between PINNED and HEAD. Only a commit that
actually changes the imported source trips the gate.
"""
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

GUARDED_PATHS = ["guide", "index.html", "legal.html", "assets"]

def _assert_commit(gw):
    """Guard the source paths the import reads, not the exact HEAD.

    PINNED must be an ancestor of HEAD (the clone hasn't been rewound or
    detached onto an unrelated line of history), and none of GUARDED_PATHS
    may differ between PINNED and HEAD (no imported content has drifted out
    from under this script since it was written against PINNED)."""
    try:
        subprocess.run(
            ["git", "-C", str(gw), "merge-base", "--is-ancestor", PINNED, "HEAD"],
            check=True, capture_output=True, text=True,
        )
    except subprocess.CalledProcessError as e:
        raise SystemExit(
            "groundwork-site: pinned commit %s is not an ancestor of HEAD (%s)" % (PINNED, e.stderr.strip())
        )
    diff = subprocess.check_output(
        ["git", "-C", str(gw), "diff", "--stat", PINNED, "HEAD", "--"] + GUARDED_PATHS,
        text=True,
    ).strip()
    if diff:
        raise SystemExit(
            "groundwork-site: source paths (%s) changed between %s and HEAD:\n%s"
            % (", ".join(GUARDED_PATHS), PINNED, diff)
        )

def _main_inner(html):
    m = re.search(r"<main[^>]*>(.*?)</main>", html, re.S)
    return m.group(1)

def _strip_chrome(inner, strip_header=True):
    inner = re.sub(r'<span class="crumb">.*?</span>', "", inner, count=1, flags=re.S)
    inner = re.sub(r'<nav class="vw journeystrip.*?</nav>', "", inner, count=1, flags=re.S)
    if strip_header:
        inner = re.sub(r'<header class="page pagehead">.*?</header>', "", inner, count=1, flags=re.S)
    return inner

def _resolve_url(url, base_dir, table):
    """Resolve one relative URL (from an href/src/srcset/poster) against base_dir,
    through the spine's redirect table. Returns None for URLs that must pass through
    untouched (absolute http(s)/mailto/fragment/data URLs)."""
    if url.startswith(("http", "mailto", "#", "data:")): return None
    path, frag = (url.split("#", 1) + [""])[:2]
    joined = (Path(base_dir) / path).as_posix()
    norm = "/" + posixpath.normpath(joined).lstrip("/")
    dest = table.get(norm)
    if dest is None and norm.startswith("/assets/"): dest = norm
    if dest is None: dest = norm
    if frag and "#" not in dest: dest = dest + "#" + frag
    return dest

def _rewrite_links(inner, base_dir, spine):
    """Rewrite every href, src, poster, and srcset (each candidate) through the
    spine's redirect table so no page-relative or guide-relative reference survives.
    Anything under /assets/ maps to /assets/ unchanged (root-relative)."""
    table = {r["source"]: r["destination"] for r in spine["redirects"] if "(" not in r["source"]}

    def sub_attr(m):
        attr, url = m.group(1), m.group(2)
        dest = _resolve_url(url, base_dir, table)
        if dest is None: return m.group(0)
        return '%s="%s"' % (attr, dest)
    inner = re.sub(r'\b(href|src|poster)="([^"]+)"', sub_attr, inner)

    def sub_srcset(m):
        candidates = []
        for candidate in m.group(1).split(","):
            candidate = candidate.strip()
            if not candidate: continue
            bits = candidate.split(None, 1)
            url = bits[0]
            descriptor = bits[1] if len(bits) > 1 else ""
            dest = _resolve_url(url, base_dir, table)
            if dest is None: dest = url
            candidates.append(dest + ((" " + descriptor) if descriptor else ""))
        return 'srcset="%s"' % ", ".join(candidates)
    inner = re.sub(r'srcset="([^"]+)"', sub_srcset, inner)
    return inner

RENAME = [
    (r"https?://orangeoceanatlas\.com[^\"\s<]*", "https://otb.cypresscommand.com"),
    (r"The Atlas story\.", "The Cypress Command Platform story."),
    (r"\bATLAS\b", "PLATFORM"),
    (r"\bAtlas\b", "Cypress Command Platform"),
]

# The Groundwork source still speaks in the old "six standing orders" numbering
# (Order N, Layer N, Phase N). The spine renumbers those onto the ten sections
# (see spine.json: guide/identity.html -> 1.1, knowledge -> 2.1, remember -> 2.2,
# limits -> 3.1, operator -> 3.2, improve -> 4.2). HEADING_FIXES rewrites that old
# language wherever it survives inside a heading, figcaption, or page kicker of
# an imported partial, so the copy gate (scripts/gates.py, banned old numbering
# in <h1>-<h3>/<figcaption>/nav) stays clean. Page kickers (<span class="kicker">,
# the example templates' own headline kickers) are kept, they just may not carry
# old numbering. Never rewrite prose outside these tags here; body copy keeps
# the original interview-number references on purpose.
HEADING_FIXES = [
    (re.compile(r"\bOrder One\b"), "Section 1.1"),
    (re.compile(r"\bOrder 1\b"), "Section 1.1"),
    (re.compile(r"\bOrder Two\b"), "Section 2.1"),
    (re.compile(r"\bOrder 2\b"), "Section 2.1"),
    (re.compile(r"\bOrder Three\b"), "Section 3.1"),
    (re.compile(r"\bOrder 3\b"), "Section 3.1"),
    (re.compile(r"\bOrder Four\b"), "Section 3.2"),
    (re.compile(r"\bOrder 4\b"), "Section 3.2"),
    (re.compile(r"\bOrder Five\b"), "Section 2.2"),
    (re.compile(r"\bOrder 5\b"), "Section 2.2"),
    (re.compile(r"\bOrder Six\b"), "Section 4.2"),
    (re.compile(r"\bOrder 6\b"), "Section 4.2"),
    (re.compile(r"\bstanding orders\b", re.I), "sections"),
    (re.compile(r"\bLayer \d+\b"), "section"),
    (re.compile(r"\bLayers\b"), "sections"),
    (re.compile(r"\bLayer\b"), "section"),
    (re.compile(r"\bPhase \d+\b"), "stage"),
    (re.compile(r"\bPhases\b"), "stages"),
    (re.compile(r"\bPhase\b"), "stage"),
]
HEADING_TAG = re.compile(
    r'<(h1|h2|h3|figcaption)([^>]*)>(.*?)</\1>'
    r'|<(span)( class="kicker"[^>]*)>(.*?)</\4>',
    re.S | re.I)

def _fix_headings(inner):
    """Apply HEADING_FIXES, but only to text inside <h1>-<h3>, <figcaption>, and
    <span class="kicker"> tags, never to surrounding body copy."""
    def sub(m):
        if m.group(1):
            tag, attrs, body = m.group(1), m.group(2), m.group(3)
        else:
            tag, attrs, body = m.group(4), m.group(5), m.group(6)
        for pat, rep in HEADING_FIXES:
            body = pat.sub(rep, body)
        return "<%s%s>%s</%s>" % (tag, attrs, body, tag)
    return HEADING_TAG.sub(sub, inner)

def _apply_rename(inner):
    """Apply the Platform rename rules to any imported partial. Deliberately case-
    sensitive per exact token (Atlas / ATLAS), never a blanket case-insensitive match:
    asset paths and filenames use lowercase 'atlas' (e.g. assets/atlas/atlas-d1-*.png)
    and must not be touched."""
    for pat, rep in RENAME: inner = re.sub(pat, rep, inner)
    return inner

def _add_platform_note(inner):
    note = ('<p class="prov">Cypress Command Platform was formerly Atlas, renamed in September 2026. '
            'The screenshots on this page were captured before the rename and still show the old name in frame; '
            'they run on a demonstration dataset. The live platform answers at '
            '<a href="https://otb.cypresscommand.com">otb.cypresscommand.com</a>, gated to the owner and the operator.</p>')
    return re.sub(r"(<h1>.*?</h1>)", r"\1" + note, inner, count=1, flags=re.S)

# Controller ruling (Task 18): HEADING_FIXES above only ever touched headings,
# figcaptions, and kickers, per its own docstring. The body PROSE of the two
# example-page partials (platform.html, console.html) still said "Order N" /
# "the six standing orders" in running text and in the drawn SVG labels, which
# a visitor reads just as readily as a heading. PROSE_FIXES rewrites that old
# numbering wherever it survives in those two files specifically; articles and
# docs keep their original interview-number references on purpose. Order
# matters here too: run the multi-word idioms and the plural/uppercase forms
# before the generic singular word-boundary patterns they would otherwise
# overlap or get shadowed by.
PROSE_FIXES = [
    (re.compile(r"\bOrders 2 \+ 3\b"), "Sections 2.1 + 3.1"),
    (re.compile(r"\bORDER 1\b"), "SECTION 1.1"),
    (re.compile(r"\bORDER 2\b"), "SECTION 2.1"),
    (re.compile(r"\bORDER 3\b"), "SECTION 3.1"),
    (re.compile(r"\bORDER 4\b"), "SECTION 3.2"),
    (re.compile(r"\bORDER 5\b"), "SECTION 2.2"),
    (re.compile(r"\bORDER 6\b"), "SECTION 4.2"),
    (re.compile(r"\bOrder One\b"), "section 1.1"),
    (re.compile(r"\bOrder 1\b"), "section 1.1"),
    (re.compile(r"\bOrder Two\b"), "section 2.1"),
    (re.compile(r"\bOrder 2\b"), "section 2.1"),
    (re.compile(r"\bOrder Three\b"), "section 3.1"),
    (re.compile(r"\bOrder 3\b"), "section 3.1"),
    (re.compile(r"\bOrder Four\b"), "section 3.2"),
    (re.compile(r"\bOrder 4\b"), "section 3.2"),
    (re.compile(r"\bOrder Five\b"), "section 2.2"),
    (re.compile(r"\bOrder 5\b"), "section 2.2"),
    (re.compile(r"\bOrder Six\b"), "section 4.2"),
    (re.compile(r"\bOrder 6\b"), "section 4.2"),
    (re.compile(r"\bsix standing orders\b", re.I), "the stages"),
    (re.compile(r"\bstanding orders\b", re.I), "sections"),
    (re.compile(r"\bstanding order\b", re.I), "section"),
    (re.compile(r"\bfifteen documents\b", re.I), "the templates"),
    (re.compile(r"\bLayer \d+\b"), "section"),
    (re.compile(r"\bPhase \d+\b"), "stage"),
]

def _apply_prose_fixes(inner):
    """Apply PROSE_FIXES to a whole partial's body text. Only ever called for
    the platform and console partials (see run())."""
    for pat, rep in PROSE_FIXES: inner = pat.sub(rep, inner)
    return inner

def run(gw, out):
    _assert_commit(gw)
    spine = S.load()
    counts = {"articles": 0, "docs": 0, "front": 0, "pages": 0}
    for slug, rel in ORDER_PAGES.items():
        inner = _strip_chrome(_main_inner(_read(gw / rel)))
        for m in DOC_CARD.finditer(inner):
            doc = _fix_headings(_apply_rename(_rewrite_links(m.group(0), "guide", spine)))
            _write(out / "content" / "docs" / ("doc-%s.html" % m.group(2).zfill(2)), doc)
            counts["docs"] += 1
        inner = DOC_CARD.sub("", inner)
        inner = _fix_headings(_apply_rename(_rewrite_links(inner, "guide", spine)))
        _write(out / "content" / "articles" / (slug + ".html"), inner)
        counts["articles"] += 1
    home = _read(gw / "index.html")
    for slug, sid in FRONT.items():
        m = re.search(r'<section[^>]*id="%s"[^>]*>(.*?)</section>' % sid, home, re.S)
        front = _fix_headings(_apply_rename(_rewrite_links(m.group(1), ".", spine)))
        _write(out / "content" / "front" / ("gw-%s.html" % slug), front)
        counts["front"] += 1
    for slug, rel in PAGES.items():
        inner = _strip_chrome(_main_inner(_read(gw / rel)), strip_header=False)
        inner = _rewrite_links(inner, str(Path(rel).parent), spine)
        inner = _apply_rename(inner)
        if slug == "platform": inner = _add_platform_note(inner)
        inner = _fix_headings(inner)
        if slug in ("platform", "console"): inner = _apply_prose_fixes(inner)
        if slug == "lineage":
            era = ('<p class="prov">Provenance. From August 2026 to September 2026 this program was published as Groundwork, '
                   'arranged as six standing orders producing fifteen documents. The AI Playbook keeps every document and every '
                   'drawing, arranged as four stages and ten sections. The old order pages redirect here, section by section.</p>')
            inner = re.sub(r"(</header>)", r"\1" + era, inner, count=1) if "</header>" in inner else era + inner
        _write(out / "content" / "pages" / (slug + ".html"), inner)
        counts["pages"] += 1
    return counts

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(run(root.parent / "groundwork-site", root))
