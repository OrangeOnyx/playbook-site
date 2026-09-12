import sys, pathlib, io, re
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build as B
from scripts import gates as G

def test_articles_render_clean(tmp_path):
    B.render(tmp_path)
    for sid, slug in (("1.1", "1-starter/1-1-know-me"), ("2.1", "2-intermediate/2-1-know-what-is-true"), ("2.2", "2-intermediate/2-2-remember-my-world"),
                      ("3.1", "3-expert/3-1-know-your-limits"), ("3.2", "3-expert/3-2-help-me-operate"), ("4.2", "4-frontier-operator/4-2-improve-and-survive")):
        s = io.open(tmp_path / slug / "index.html", encoding="utf-8").read()
        assert "<h2>Going deeper.</h2>" in s, sid
        assert s.count('class="fig ico"') >= 3, "glyphs missing on " + sid
        assert not [e for e in G.check_text(s, slug + "/index.html") if "numbering" in e], sid

# The six article partials, the five gw-* front partials, and the document cards carved out
# of the same order-page source all run through import_groundwork's PROSE_FIXES pass, so the
# retired "Order N" / "standing orders" vocabulary must not survive anywhere in the rendered
# site. Two paths are allowlisted on purpose: /lineage/ is the provenance page that explains
# the old arrangement, and curriculum/read/ is the verbatim curriculum repo export.
OLD_NUMBERING = re.compile(r"\bOrders? [0-9]|\borders? [0-9] to|standing orders?")
NUMBERING_ALLOWED = ("lineage/index.html", "curriculum/read/")


def test_old_order_numbering_is_gone_from_the_rendered_site(tmp_path):
    B.render(tmp_path)
    hits = []
    for f in sorted(tmp_path.rglob("*.html")):
        rel = f.relative_to(tmp_path).as_posix()
        if any(a in rel for a in NUMBERING_ALLOWED):
            continue
        m = OLD_NUMBERING.search(io.open(f, encoding="utf-8").read())
        if m:
            hits.append("%s: %r" % (rel, m.group(0)))
    assert not hits, hits
