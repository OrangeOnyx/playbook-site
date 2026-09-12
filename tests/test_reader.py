import sys, pathlib, io
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import build_reader as R

def test_reader_maps_levels_to_stages(tmp_path):
    n = R.run(ROOT.parent / "groundwork-curriculum", tmp_path)
    assert n >= 100
    idx = io.open(tmp_path / "index.html", encoding="utf-8").read()
    assert "4 Frontier Operator" in idx and "3 Expert" in idx
    assert "Level 4" not in idx.split("<main")[0]          # the shell carries stages, not levels
    assert "level-4-professional" not in idx or "3 Expert" in idx
