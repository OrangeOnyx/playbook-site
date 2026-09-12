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

def test_numbering_gate_catches_contents_list_links():
    bad = '<ol class="contents"><li><a href="/x/">Level 2 Glossary</a></li></ol>'
    f = G.check_text(bad, "y.html")
    assert any("numbering" in e for e in f)

def test_lineage_and_reader_are_allowlisted():
    s = "<h2>Order 1</h2>"
    assert not G.check_text(s, "lineage/index.html")
    assert not G.check_text("<p>—</p>", "curriculum/read/l1-x.html")

def test_link_check(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "a" / "index.html").write_text('<a href="/b/">b</a><a href="../c.html">c</a>', encoding="utf-8")
    errs = G.check_links(tmp_path)
    assert len(errs) == 2

def test_numbering_gate_covers_the_full_heading_ladder_and_plate_labels():
    # h4-h6 carry real sub-headings inside the document cards and the example pages,
    # and a plate's drawn label strip reads as a headline too.
    f = G.check_text("<h4>Order 4: Help me operate</h4>", "y.html")
    assert any("numbering in <h4>" in e for e in f), f
    for tag in ("h5", "h6"):
        assert [e for e in G.check_text("<%s>Level 2 ladder</%s>" % (tag, tag), "y.html") if "numbering" in e], tag
    p = G.check_text('<span class="plate-label">Plate 02 . olive . Layer 1</span>', "y.html")
    assert any("plate-label" in e for e in p), p
    ok = '<h4>3.2 Help me operate</h4><span class="plate-label">PLATE 02 . OLIVE</span>'
    assert not [e for e in G.check_text(ok, "z.html") if "numbering" in e]

def test_fresh_gate_passes_on_this_repo():
    assert G.check_fresh(ROOT) == []

def test_fresh_gate_names_the_stale_artifact_and_how_to_regenerate(tmp_path, monkeypatch):
    stale = {"spine.json": 200, "assets/The-AI-Playbook-Field-Guide.pdf": 100,
             "content/generated/curriculum/read/index.html": 300}
    monkeypatch.setattr(G, "_last_commit_ts", lambda root, rel: stale.get(rel))
    errs = G.check_fresh(tmp_path)
    assert len(errs) == 1
    assert "The-AI-Playbook-Field-Guide.pdf" in errs[0] and "scripts/build_field_guide.py" in errs[0]

def test_fresh_gate_is_silent_without_git_history(tmp_path, monkeypatch):
    monkeypatch.setattr(G, "_last_commit_ts", lambda root, rel: None)
    assert G.check_fresh(tmp_path) == []
