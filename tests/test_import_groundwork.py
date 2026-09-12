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

def test_no_relative_asset_paths_survive(tmp_path):
    G.run(ROOT.parent / "groundwork-site", tmp_path)
    files = list((tmp_path / "content").rglob("*.html"))
    assert files
    for f in files:
        text = io.open(f, encoding="utf-8").read()
        assert 'src="../' not in text, f
        assert 'src="assets/' not in text, f
    console = io.open(tmp_path / "content" / "pages" / "console.html", encoding="utf-8").read()
    assert 'src="/assets/console/console-od3-command-brief.png"' in console

def test_atlas_rename_scope(tmp_path):
    G.run(ROOT.parent / "groundwork-site", tmp_path)
    word = re.compile(r"\bAtlas\b|\bATLAS\b")
    allowed = re.compile(r"formerly Atlas|called Atlas until")
    for f in (tmp_path / "content").rglob("*.html"):
        text = io.open(f, encoding="utf-8").read()
        if f.parent.name == "pages" and f.name == "platform.html":
            text = allowed.sub("", text)
        bad = word.findall(text)
        assert not bad, (str(f), bad)

def test_page_kickers_carry_no_old_numbering(tmp_path):
    # Page kickers (<span class="kicker">, the example templates' own headline
    # kickers) are kept as-is, they just may not carry old "six standing
    # orders" numbering (Order N, Layer N, Phase N, "standing orders").
    G.run(ROOT.parent / "groundwork-site", tmp_path)
    kicker = re.compile(r'<span class="kicker">(.*?)</span>', re.S | re.I)
    bad = re.compile(r"\b(Order|Layer|Phase)\s+\d+\b|\bstanding orders\b", re.I)
    hits = []
    for f in (tmp_path / "content").rglob("*.html"):
        text = io.open(f, encoding="utf-8").read()
        for m in kicker.finditer(text):
            if bad.search(m.group(1)): hits.append((str(f), m.group(1)))
    assert not hits, hits
