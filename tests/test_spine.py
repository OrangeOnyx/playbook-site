import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from scripts import spine as S

def test_loads_and_validates():
    sp = S.load()
    assert S.validate(sp) == []

def test_four_stages_ten_sections():
    sp = S.load()
    assert [s["number"] for s in sp["stages"]] == [1, 2, 3, 4]
    assert [x["id"] for x in S.sections(sp)] == ["1.0","1.1","1.2","2.1","2.2","2.3","3.1","3.2","4.1","4.2"]

def test_slugs_carry_numbers():
    sp = S.load()
    for x in S.sections(sp):
        assert x["slug"].startswith(x["id"].replace(".", "-") + "-")
        assert x["path"] == "/%s/%s/" % (sp["stages"][x["stage"]-1]["slug"], x["slug"])

def test_every_section_has_lanes_and_provenance():
    sp = S.load()
    for x in S.sections(sp):
        assert x["lanes"]["personal"] and x["lanes"]["business"]
        assert x["provenance"]
        assert x["cards"]

def test_redirects_cover_every_groundwork_guide_page():
    sp = S.load()
    srcs = {r["source"] for r in sp["redirects"]}
    for p in ["/guide/identity.html","/guide/knowledge.html","/guide/remember.html","/guide/limits.html",
              "/guide/operator.html","/guide/improve.html","/guide/day-one.html","/guide/scorecard.html",
              "/guide/atlas.html","/guide/dashboard.html","/guide/lineage.html","/guide/foundations.html",
              "/guide/index.html","/legal.html","/curriculum/index.html","/curriculum/level-1.html",
              "/curriculum/level-5.html","/assets/Groundwork-Program-Guide.pdf"]:
        assert p in srcs, p
