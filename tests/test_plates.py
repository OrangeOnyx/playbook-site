import sys, pathlib, io
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import redraw_plates as R

def test_redraw_writes_four_plates(tmp_path):
    R.run(tmp_path)
    for n in ("00", "02", "14", "15"):
        t = io.open(tmp_path / "content" / "plates" / ("fig-%s.html" % n), encoding="utf-8").read()
        assert '<figure class="fig plate' in t and "<figcaption" in t
    ladder = io.open(tmp_path / "content" / "plates" / "fig-02.html", encoding="utf-8").read()
    for sid in ("1.0", "1.1", "1.2", "2.1", "2.2", "2.3", "3.1", "3.2", "4.1", "4.2"):
        assert sid in ladder
    assert "Level" not in ladder and "Interview" not in ladder
    cover = io.open(tmp_path / "content" / "plates" / "fig-00.html", encoding="utf-8").read()
    assert cover.count("<circle") >= 10
