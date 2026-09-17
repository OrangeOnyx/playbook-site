import sys, pathlib, re
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import gw_plates as P

RETIRED = re.compile(r"\b(LEVEL|LAYER|PHASE|ORDER|INTERVIEW)S?\b|\bLevel\b|\blevel\b", re.I)

def test_climb_line_has_four_stations():
    svg = P.climb_line(3, numerals=True)
    assert svg.count("<circle") == 5            # four stations plus the halo on the current one
    for lab in ("1 STARTER", "2 INTERMEDIATE", "3 EXPERT", "4 FRONTIER OPERATOR"):
        assert lab in svg
    assert 'aria-label="The four stages, climbing."' in svg

def test_stage_emblems_exist_for_four_and_only_four():
    for n in (1, 2, 3, 4):
        assert P.stage_emblem(n).startswith("<svg")
    assert not hasattr(P, "level_emblem") and not hasattr(P, "axis_bands") and not hasattr(P, "LEVEL_NAMES")

def test_library_output_carries_no_retired_vocabulary():
    out = P.climb_line(None) + P.parallel_tracks() + P.cover_plate() + "".join(P.stage_emblem(n) for n in (1, 2, 3, 4)) + " ".join(P.GROUPS.values())
    assert not RETIRED.search(out), RETIRED.search(out).group(0)

def test_parallel_tracks_names_both_programs():
    svg = P.parallel_tracks()
    assert "THE PLAYBOOK" in svg and "THE CURRICULUM" in svg
    assert svg.count("<circle") == 8

def test_curriculum_vendored_copy_is_identical():
    twin = ROOT.parent / "ai-playbook-curriculum" / "shared" / "graphics" / "plates.py"
    assert twin.exists(), "vendor the library: copy scripts/gw_plates.py to the curriculum repo's shared/graphics/plates.py"
    assert twin.read_bytes() == (ROOT / "scripts" / "gw_plates.py").read_bytes()
