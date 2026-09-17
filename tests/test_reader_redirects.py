import sys, pathlib, io, json
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import reader_redirects as RR

FM = {"levels": {"level-1-essentials": "1-starter", "level-2-intermediate": "2-intermediate", "level-3-advanced": "3-expert",
                 "level-4-professional": "3-expert", "level-5-frontier": "4-frontier-operator"},
      "paths": {"level-4-professional/individual/01-leading-ai-teams": "3-expert/individual/15-leading-ai-teams",
                "level-4-professional/individual/12-jargon-level-4": "3-expert/individual/26-jargon-stage-3-continued",
                "level-3-advanced/individual/01-shipping-to-production": "3-expert/individual/01-shipping-to-production",
                "level-2-intermediate/individual/12-jargon-level-2": "2-intermediate/individual/12-jargon-stage-2"}}

def test_new_slug_maps_levels_modules_and_groups():
    assert RR.new_slug("l4-individual-01-leading-ai-teams", FM) == "3-individual-15-leading-ai-teams"
    assert RR.new_slug("l4-individual-12-jargon-level-4", FM) == "3-individual-26-jargon-stage-3-continued"
    assert RR.new_slug("l3-individual-01-shipping-to-production", FM) == "3-individual-01-shipping-to-production"
    assert RR.new_slug("l2-individual-12-jargon-level-2", FM) == "2-individual-12-jargon-stage-2"
    assert RR.new_slug("l4-overview", FM) == "3-overview"
    assert RR.new_slug("l5-eli10", FM) == "4-eli10"
    assert RR.new_slug("l1-start-here", FM) == "1-start-here"
    assert RR.new_slug("orientation", FM) == "orientation"

def test_rules_are_permanent_and_relative():
    r = RR.rules({"l4-overview": "3-overview"})
    assert r == [{"source": "/curriculum/read/l4-overview.html", "destination": "/curriculum/read/3-overview.html", "permanent": True}]

def test_derive_skips_unchanged_pages_and_index():
    d = RR.derive(["index.html", "orientation.html", "l4-overview.html", "assets"], FM)
    assert d == {"l4-overview": "3-overview"}

def test_committed_vercel_json_matches_the_generator():
    renames = json.load(io.open(ROOT / "content" / "reader-renames.json", encoding="utf-8"))
    assert len(renames) >= 100
    want = RR.build_config(renames)
    have = json.load(io.open(ROOT / "vercel.json", encoding="utf-8"))
    assert have == want, "regenerate: python scripts/reader_redirects.py"

def test_every_redirect_destination_exists_in_dist(tmp_path):
    import build as B
    B.render(tmp_path)
    cfg = json.load(io.open(ROOT / "vercel.json", encoding="utf-8"))
    missing = [r["destination"] for r in cfg["redirects"] if not (tmp_path / r["destination"].lstrip("/")).exists()]
    assert not missing, missing[:5]
