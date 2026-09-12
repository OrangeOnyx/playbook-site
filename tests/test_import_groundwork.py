import sys, pathlib, io, re
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import import_groundwork as G

def test_groundwork_import(tmp_path):
    r = G.run(ROOT.parent / "groundwork-site", tmp_path)
    assert r["articles"] == 6 and r["docs"] == 15 and r["front"] == 5 and r["pages"] == 4
    art = io.open(tmp_path / "content" / "articles" / "identity.html", encoding="utf-8").read()
    assert "journeystrip" not in art and "Document 01" not in art and 'class="crumb"' not in art
    assert "guide/" not in art, "links must be rewritten through the redirect table"
    doc = io.open(tmp_path / "content" / "docs" / "doc-01.html", encoding="utf-8").read()
    assert "<h3>Document 01: Identity Charter</h3>" in doc and "<pre>" in doc
    plat = io.open(tmp_path / "content" / "pages" / "platform.html", encoding="utf-8").read()
    assert "Cypress Command Platform" in plat and "orangeoceanatlas" not in plat
    assert "formerly Atlas" in plat
