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
