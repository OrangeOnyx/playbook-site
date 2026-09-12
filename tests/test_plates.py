import sys, pathlib, io
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
from scripts import redraw_plates as R
from test_import_playbook import _assert_canonical_plates

def test_redraw_writes_four_plates(tmp_path):
    R.run(tmp_path)
    for n in ("00", "02", "14", "15"):
        p = tmp_path / "content" / "plates" / ("fig-%s.html" % n)
        t = io.open(p, encoding="utf-8").read()
        _assert_canonical_plates(t, str(p))
    ladder = io.open(tmp_path / "content" / "plates" / "fig-02.html", encoding="utf-8").read()
    for sid in ("1.0", "1.1", "1.2", "2.1", "2.2", "2.3", "3.1", "3.2", "4.1", "4.2"):
        assert sid in ladder
    assert "Level" not in ladder and "Interview" not in ladder
    cover = io.open(tmp_path / "content" / "plates" / "fig-00.html", encoding="utf-8").read()
    assert cover.count("<circle") >= 10
