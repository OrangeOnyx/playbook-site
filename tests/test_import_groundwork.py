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

def test_imported_prose_carries_no_old_numbering(tmp_path):
    # HEADING_FIXES only ever touched headings, figcaptions, and kickers; the running
    # PROSE (and drawn SVG labels) of the imported partials still said "Order N" /
    # "standing order" in places. PROSE_FIXES scrubs that old numbering from the two
    # example partials, the six article partials, the document cards carved out of the
    # same order-page source, and the five gw-* front partials.
    G.run(ROOT.parent / "groundwork-site", tmp_path)
    bad = re.compile(r"\bOrder\s+\d+\b|\bLayer\s+\d+\b|\bPhase\s+\d+\b|standing order", re.I)
    scrubbed = ([tmp_path / "content" / "pages" / n for n in ("platform.html", "console.html")]
                + sorted((tmp_path / "content" / "articles").glob("*.html"))
                + sorted((tmp_path / "content" / "docs").glob("*.html"))
                + sorted((tmp_path / "content" / "front").glob("gw-*.html")))
    for f in scrubbed:
        hits = bad.findall(io.open(f, encoding="utf-8").read())
        assert not hits, (f.name, hits)
    plat = io.open(tmp_path / "content" / "pages" / "platform.html", encoding="utf-8").read()
    assert "section 2.1" in plat and "section 3.1" in plat
    cons = io.open(tmp_path / "content" / "pages" / "console.html", encoding="utf-8").read()
    for want in ("SECTION 4.2", "SECTION 3.1", "SECTION 2.1", "Section 3.2", "Section 2.2"):
        assert want in cons, want


def test_ranges_and_the_standing_half_are_renumbered(tmp_path):
    # Lowercase and plural ranges map each end of the range; the FAQ's "standing half"
    # gloss names the two sections it means instead of the retired order names.
    G.run(ROOT.parent / "groundwork-site", tmp_path)
    faq = io.open(tmp_path / "content" / "front" / "gw-faq.html", encoding="utf-8").read()
    assert "sections 1.1 to 3.1" in faq
    assert "The standing half (2.2 Remember my world and 4.2 Improve and survive)" in faq
    assert G._apply_prose_fixes("the standing half (Remember and Improve) runs on") == \
        "the standing half (2.2 Remember my world and 4.2 Improve and survive) runs on"
    assert G._apply_prose_fixes("built on Orders 2 and 3 today") == "built on sections 2.1 and 3.1 today"
    assert G._apply_prose_fixes("built at order 4 only") == "built at section 3.2 only"
    # ... and the word is capitalized back up when it opens a sentence or a link label.
    assert G._apply_prose_fixes("<p>Order 1 is three files.") == "<p>Section 1.1 is three files."
    assert G._apply_prose_fixes("<p>Orders 2 and 3 hold.") == "<p>Sections 2.1 and 3.1 hold."

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


class _FakeGit:
    """Stand-in for the subprocess calls _assert_commit makes, so the guard can be driven
    without a throwaway clone: the pin is an ancestor, HEAD matches the pin, and the
    working tree is dirty in the guarded paths only when `dirty` says so."""
    class CalledProcessError(Exception):
        pass

    def __init__(self, dirty):
        self.dirty = dirty

    def run(self, cmd, **kw):
        class R: pass
        r = R()
        r.returncode = 1 if ("--quiet" in cmd and self.dirty) else 0
        r.stderr = ""
        return r

    def check_output(self, cmd, **kw):
        return "guide/identity.html\n" if "--name-only" in cmd else ""


def test_assert_commit_accepts_a_clean_guarded_tree(monkeypatch):
    monkeypatch.setattr(G, "subprocess", _FakeGit(dirty=False))
    G._assert_commit(ROOT.parent / "groundwork-site")   # no raise


def test_assert_commit_rejects_uncommitted_guarded_changes(monkeypatch):
    monkeypatch.setattr(G, "subprocess", _FakeGit(dirty=True))
    with pytest.raises(SystemExit) as e:
        G._assert_commit(ROOT.parent / "groundwork-site")
    assert "uncommitted changes" in str(e.value) and "guide/identity.html" in str(e.value)


def test_assert_commit_ignores_dirt_outside_the_guarded_paths():
    # The live sibling clone carries an unrelated dirty file (print/build-field-guide.ps1);
    # the guard must not care.
    G._assert_commit(ROOT.parent / "groundwork-site")


def test_run_clears_the_files_it_owns_and_leaves_the_rest(tmp_path):
    stale = []
    for rel in ("content/articles/gone.html", "content/docs/doc-99.html",
                "content/front/gw-gone.html", "content/pages/gone.html"):
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("<p>stale</p>", encoding="utf-8")
        stale.append(p)
    keep = []
    for rel in ("content/front/ch-1.html", "content/cards/s1.html", "content/plates/fig-00.html",
                "content/examples/personal-ai-os.html", "content/generated/curriculum/read/index.html"):
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("<p>not mine</p>", encoding="utf-8")
        keep.append(p)
    G.run(ROOT.parent / "groundwork-site", tmp_path)
    for p in stale:
        assert not p.exists(), p
    for p in keep:
        assert p.read_text(encoding="utf-8") == "<p>not mine</p>", p
