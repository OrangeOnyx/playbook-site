"""Glyph parity verifier (thin runner, not a generator).

Groundwork's article-drawings-wave.py (a sibling script, at
../../scripts/article-drawings-wave.py relative to this repo's parent) draws
the self-inking `data-w2` heading glyphs and document stamps directly into
Groundwork's own pages (guide/identity.html etc). import_groundwork.py then
splits each of those pages into an article partial (content/articles/*.html)
plus its document cards (content/docs/doc-NN.html) -- the glyph markup rides
along inside both halves untouched.

Rather than re-running the generator against the split partials (which would
risk inserting duplicate or mismatched svg blocks), this script checks that
every glyph Groundwork drew is still present somewhere on the playbook side:
for each of the six source pages it sums data-w2 occurrences in the article
partial and the document cards known to have come from that page, and
compares the total to the count on the original page.

Run: python scripts/glyphs.py [path-to-groundwork-site]
Exit 0 when every page's count matches; exit 1 (with a MISMATCH row) when a
glyph or stamp went missing during import, in which case the fix is to check
import_groundwork.py's chrome-stripping and doc-card extraction, never to
hand-edit the partials.
"""
import io, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.import_groundwork import ORDER_PAGES, DOC_CARD

DATA_W2 = re.compile(r"data-w2")


def _count(path):
    if not path.exists(): return 0
    return len(DATA_W2.findall(io.open(path, encoding="utf-8").read()))


def run(gw=None):
    gw = Path(gw) if gw else ROOT.parent / "groundwork-site"
    rows = []
    ok = True
    for slug, rel in ORDER_PAGES.items():
        src = gw / rel
        src_html = io.open(src, encoding="utf-8").read()
        src_count = len(DATA_W2.findall(src_html))
        doc_nums = [m.group(2).zfill(2) for m in DOC_CARD.finditer(src_html)]
        article_count = _count(ROOT / "content" / "articles" / (slug + ".html"))
        docs_count = sum(_count(ROOT / "content" / "docs" / ("doc-%s.html" % n)) for n in doc_nums)
        total = article_count + docs_count
        match = total == src_count
        ok = ok and match
        rows.append((slug, src_count, article_count, docs_count, total, match))
    print("%-10s %8s %8s %8s %8s  %s" % ("slug", "source", "article", "docs", "total", "match"))
    for slug, src_count, article_count, docs_count, total, match in rows:
        print("%-10s %8d %8d %8d %8d  %s" % (slug, src_count, article_count, docs_count, total, "ok" if match else "MISMATCH"))
    if ok:
        print("glyphs intact: %d pages" % len(rows))
    else:
        print("glyph mismatch found; rerun import_groundwork.py or check article-drawings-wave.py's output")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(run(sys.argv[1] if len(sys.argv) > 1 else None))
