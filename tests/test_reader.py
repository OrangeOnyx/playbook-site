import sys, pathlib, io, re
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import build_reader as R
import build as B

def test_reader_maps_levels_to_stages(tmp_path):
    n = R.run(ROOT.parent / "groundwork-curriculum", tmp_path)
    assert n >= 100
    idx = io.open(tmp_path / "index.html", encoding="utf-8").read()
    assert "4 Frontier Operator" in idx and "3 Expert" in idx
    assert "Level 4" not in idx.split("<main")[0]          # the shell carries stages, not levels
    assert "level-4-professional" not in idx or "3 Expert" in idx

def test_stage_pages_do_not_leak_level_words(tmp_path):
    # reader_modules() surfaces reader-page titles onto curriculum/<stage>/, which is
    # NOT copy-gate allowlisted (unlike curriculum/read/ itself): a raw "Level N" from
    # the repo's own README headings must never survive onto those pages.
    B.render(tmp_path)
    for st in B.S.load()["stages"]:
        s = io.open(tmp_path / "curriculum" / st["slug"] / "index.html", encoding="utf-8").read()
        assert not re.search(r"Level \d", s), (st["slug"], re.findall(r".{0,20}Level \d.{0,20}", s))
