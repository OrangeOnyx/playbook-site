import sys, pathlib, io
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build as B

def test_registry_has_core_pages():
    outs = {p["out"] for p in B.pages(B.S.load())}
    for o in ("index.html", "1-starter/index.html", "1-starter/1-1-know-me/index.html", "4-frontier-operator/4-2-improve-and-survive/index.html",
              "radar/index.html", "templates/index.html", "plates/index.html", "start/index.html", "legal/index.html", "404.html"):
        assert o in outs, o

def test_render_smoke(tmp_path):
    n = B.render(tmp_path)
    assert n >= 3
    s = io.open(tmp_path / "start" / "index.html", encoding="utf-8").read()
    assert "<title>Start | The AI Playbook</title>" in s
    assert s.count("by Cypress Command") == 1
    assert 'class="vw journeystrip ladder' in s and 'data-theme' in s
    assert (tmp_path / "assets" / "guide.css").exists() and (tmp_path / "vercel.json").exists()
    assert (tmp_path / ".vercel" / "project.json").exists()

def test_cover(tmp_path):
    B.render(tmp_path)
    s = io.open(tmp_path / "index.html", encoding="utf-8").read()
    assert "<h1>Four stages.<br>One operating system.</h1>" in s
    for anchor in ('id="why"', 'id="contents"', 'id="compounding"', 'id="why-now"', 'id="lanes"'):
        assert anchor in s, anchor
    assert s.count('class="lane-pick"') == 2
    assert "Ten interviews" not in s.split("<h1>")[0]
    assert s.count("by Cypress Command") == 1
    assert "<title>The AI Playbook</title>" in s

def test_stage_hubs(tmp_path):
    B.render(tmp_path)
    s = io.open(tmp_path / "1-starter" / "index.html", encoding="utf-8").read()
    assert "<h1>1 Starter.</h1>" in s
    for sid in ("1.0", "1.1", "1.2"): assert sid in s
    assert "Gate:" in s and 'class="lanes"' in s
    assert 'data-card="s14"' in s   # the evidence log lives on Stage 1

def test_section_pages(tmp_path):
    B.render(tmp_path)
    s = io.open(tmp_path / "2-intermediate" / "2-3-capture-and-commit" / "index.html", encoding="utf-8").read()
    assert "<h1>2.3 Capture and commit.</h1>" in s
    assert s.count('class="card-body"') == 2
    assert 'class="prov">Source: Interviews 4 and 5' in s
    assert 'class="lanes"' in s and "<h3>Why it exists</h3>" in s
    k = io.open(tmp_path / "1-starter" / "1-1-know-me" / "index.html", encoding="utf-8").read()
    assert 'href="/1-starter/1-2-learn-my-work/"' in k
    assert "<h3>Document 01: Identity Charter</h3>" in k

def test_radar(tmp_path):
    B.render(tmp_path)
    s = io.open(tmp_path / "radar" / "index.html", encoding="utf-8").read()
    assert s.count('<fieldset class="q"') == 18 and 'id="radar-svg"' in s and "radar.js" in s

def test_templates_index(tmp_path):
    B.render(tmp_path)
    s = io.open(tmp_path / "templates" / "index.html", encoding="utf-8").read()
    assert s.count("<h3>Document ") == 15
    for x in B.S.sections(B.S.load()):
        if x["docs"]: assert ("<h2>" + x["id"] + " " + x["title"]) in s
