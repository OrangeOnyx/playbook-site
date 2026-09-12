import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import gates as G

def test_copy_gate_catches_em_dash_and_banned_words():
    f = G.check_text("<p>We leverage this — really</p>", "x.html")
    assert any("em dash" in e for e in f) and any("leverage" in e for e in f)

def test_numbering_gate_catches_headlines_only():
    bad = '<h2>Interview 4: Capture</h2><title>Order 1 | x</title><nav><a href="/">Level 3</a></nav><figcaption>Fig. 2 The level ladder, Layer 1</figcaption>'
    f = G.check_text(bad, "y.html")
    assert len([e for e in f if "numbering" in e]) == 4
    ok = '<h2>2.3 Capture and commit</h2><p class="prov">Source: Interview 4 and Interview 5.</p>'
    assert not [e for e in G.check_text(ok, "z.html") if "numbering" in e]

def test_lineage_and_reader_are_allowlisted():
    s = "<h2>Order 1</h2>"
    assert not G.check_text(s, "lineage/index.html")
    assert not G.check_text("<p>—</p>", "curriculum/read/l1-x.html")

def test_link_check(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / "index.html").write_text('<a href="/b/">b</a><a href="../c.html">c</a>', encoding="utf-8")
    errs = G.check_links(tmp_path)
    assert len(errs) == 2
