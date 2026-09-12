import sys, pathlib, re, io
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import import_playbook as I

def test_import_writes_cards_plates_chapters(tmp_path):
    out = I.run(ROOT / "import" / "playbook-v2", tmp_path)
    cards = sorted(p.name for p in (tmp_path / "content" / "cards").glob("s*.html"))
    assert len(cards) == 15 and "s2.html" in cards
    s2 = io.open(tmp_path / "content" / "cards" / "s2.html", encoding="utf-8").read()
    assert 'data-source="Interview 1"' in s2
    assert s2.count('class="panel"') == 6
    assert "Depth by stage" in s2 and "Depth by level" not in s2
    plates = sorted(p.name for p in (tmp_path / "content" / "plates").glob("fig-*.html"))
    assert len(plates) >= 10
    for p in plates:
        t = io.open(tmp_path / "content" / "plates" / p, encoding="utf-8").read()
        assert "data-anim" not in t and 'class="fig' in t
    chapters = sorted(p.name for p in (tmp_path / "content" / "front").glob("ch-*.html"))
    assert len(chapters) == 9
    css = io.open(tmp_path / "assets" / "playbook-import.css", encoding="utf-8").read()
    assert ".plate" in css and ".is-in" not in css and len(css) < 90000


FIG_BLOCK_RE = re.compile(r"<figure\b.*?</figure>", re.S)


def _assert_canonical_plates(text, where):
    """The controller's one canonical plate shape, standalone or embedded: exactly one
    class="fig plate" figure per <figure> found, no leftover source markup (svg still
    carrying class="fig", the old class="figure" wrapper, the div.plate wrapper, or the
    "btn replay" button class), and every figure carries a figcaption/fignum and a Replay
    button in the new class="replay" form. The site convention is an uppercase
    "PLATE NN . INK" label -- every plate-label span's text must equal its own upper() form."""
    fig_opens = re.findall(r"<figure\b[^>]*>", text)
    assert len(fig_opens) == text.count('class="fig plate"'), where
    assert not re.search(r'<svg[^>]*class="[^"]*\bfig\b', text), where
    assert 'class="figure"' not in text, where
    assert 'div class="plate' not in text, where
    assert "btn replay" not in text, where
    for fig in FIG_BLOCK_RE.findall(text):
        assert "<figcaption" in fig and 'class="fignum"' in fig, where
        assert '<button class="replay"' in fig, where
    for m in re.finditer(r'<span class="plate-label">(.*?)</span>', text, re.S):
        assert m.group(1) == m.group(1).upper(), (where, m.group(1))


def test_plates_and_embedded_figures_are_canonical(tmp_path):
    out = I.run(ROOT / "import" / "playbook-v2", tmp_path)
    for p in sorted((tmp_path / "content" / "plates").glob("fig-*.html")):
        _assert_canonical_plates(io.open(p, encoding="utf-8").read(), str(p))
    for p in sorted((tmp_path / "content" / "cards").glob("s*.html")):
        _assert_canonical_plates(io.open(p, encoding="utf-8").read(), str(p))
    for p in sorted((tmp_path / "content" / "front").glob("ch-*.html")):
        _assert_canonical_plates(io.open(p, encoding="utf-8").read(), str(p))


def test_import_never_overwrites_redraw_owned_plates(tmp_path):
    """00, 02, 14, and 15 belong to scripts/redraw_plates.py; the importer must skip writing
    them no matter what's already on disk, since the real build always runs the import before
    the redraw. Pre-seed sentinel content for two of them (fig-00, fig-14) and confirm both
    survive untouched, while an unowned number (fig-01) still gets written for real."""
    plates_dir = tmp_path / "content" / "plates"
    plates_dir.mkdir(parents=True)
    sentinel_00 = "SENTINEL-FIG-00-OWNED-BY-REDRAW"
    sentinel_14 = "SENTINEL-FIG-14-OWNED-BY-REDRAW"
    io.open(plates_dir / "fig-00.html", "w", encoding="utf-8").write(sentinel_00)
    io.open(plates_dir / "fig-14.html", "w", encoding="utf-8").write(sentinel_14)

    I.run(ROOT / "import" / "playbook-v2", tmp_path)

    assert io.open(plates_dir / "fig-00.html", encoding="utf-8").read() == sentinel_00
    assert io.open(plates_dir / "fig-14.html", encoding="utf-8").read() == sentinel_14
    fig01 = io.open(plates_dir / "fig-01.html", encoding="utf-8").read()
    assert sentinel_00 not in fig01 and sentinel_14 not in fig01 and 'class="fig plate"' in fig01


def test_run_clears_the_files_it_owns_and_spares_the_redrawn_plates(tmp_path):
    stale = []
    for rel in ("content/cards/s99.html", "content/front/ch-99.html",
                "content/plates/fig-99.html", "content/plates/fig-c-3.html"):
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("<p>stale</p>", encoding="utf-8")
        stale.append(p)
    keep = []
    for num in sorted(I.OWNED_BY_REDRAW):
        p = tmp_path / "content" / "plates" / ("fig-%s.html" % num)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("<p>redrawn</p>", encoding="utf-8")
        keep.append(p)
    for rel in ("content/articles/identity.html", "content/docs/doc-01.html",
                "content/front/gw-faq.html", "content/pages/lineage.html",
                "content/examples/personal-ai-os.html", "content/generated/curriculum/read/index.html"):
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("<p>not mine</p>", encoding="utf-8")
        keep.append(p)
    I.run(ROOT / "import" / "playbook-v2", tmp_path)
    for p in stale:
        assert not p.exists(), p
    for p in keep:
        assert p.exists() and "stale" not in p.read_text(encoding="utf-8"), p
