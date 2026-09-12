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
    css = io.open(tmp_path / "assets" / "playbook.css", encoding="utf-8").read()
    assert ".plate" in css and ".is-in" not in css and len(css) < 90000
