import sys, pathlib, io, re, pytest
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import import_groundwork as G

def test_assert_commit_passes_on_real_clone():
    # PINNED must still be an ancestor of the sibling clone's HEAD, and the
    # guarded source paths (guide/, index.html, legal.html, assets/) must be
    # unchanged since PINNED, even if groundwork-site's HEAD has moved on
    # with commits that only touch deploy tooling or config.
    G._assert_commit(ROOT.parent / "groundwork-site")

def test_assert_commit_rejects_bogus_pin(monkeypatch):
    monkeypatch.setattr(G, "PINNED", "0000000")
    with pytest.raises(SystemExit):
        G._assert_commit(ROOT.parent / "groundwork-site")

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

def test_platform_and_console_prose_carries_no_old_numbering(tmp_path):
    # Controller ruling (Task 18): HEADING_FIXES only ever touched headings,
    # figcaptions, and kickers; the platform and console partials' running
    # PROSE (and drawn SVG labels) still said "Order N" / "standing order" in
    # places. PROSE_FIXES must scrub that old numbering from these two
    # partials specifically. Articles and docs are untouched on purpose, and
    # keep their original interview-number references.
    G.run(ROOT.parent / "groundwork-site", tmp_path)
    bad = re.compile(r"\bOrder\s+\d+\b|\bLayer\s+\d+\b|\bPhase\s+\d+\b|standing order", re.I)
    for name in ("platform.html", "console.html"):
        text = io.open(tmp_path / "content" / "pages" / name, encoding="utf-8").read()
        hits = bad.findall(text)
        assert not hits, (name, hits)
    plat = io.open(tmp_path / "content" / "pages" / "platform.html", encoding="utf-8").read()
    assert "section 2.1" in plat and "section 3.1" in plat
    cons = io.open(tmp_path / "content" / "pages" / "console.html", encoding="utf-8").read()
    for want in ("SECTION 4.2", "SECTION 3.1", "SECTION 2.1", "section 3.2", "section 2.2"):
        assert want in cons, want
    # PROSE_FIXES is scoped to platform.html and console.html only: articles
    # keep their original interview-number references in body prose on
    # purpose, so this partial must still say "Order N" somewhere.
    identity = io.open(tmp_path / "content" / "articles" / "identity.html", encoding="utf-8").read()
    assert re.search(r"\bOrder \d\b", identity), "articles must keep their original body-prose numbering"

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
