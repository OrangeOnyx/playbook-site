import sys, pathlib, io, re
import pytest
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

def test_no_duplicate_fig_ids(tmp_path):
    B.render(tmp_path)
    for f in tmp_path.rglob("*.html"):
        s = io.open(f, encoding="utf-8").read()
        ids = re.findall(r'id="(fig-\d+)"', s)
        dupes = {i for i in ids if ids.count(i) > 1}
        assert not dupes, f"{f.relative_to(tmp_path)} has duplicate figure ids: {dupes}"

def test_examples(tmp_path):
    B.render(tmp_path)
    p = io.open(tmp_path / "examples" / "personal-ai-os" / "index.html", encoding="utf-8").read()
    assert "Monday" in p and "Friday" in p and 'data-lane-page="personal"' in p
    b = io.open(tmp_path / "examples" / "cypress-command-platform" / "index.html", encoding="utf-8").read()
    assert "formerly Atlas" in b and "otb.cypresscommand.com" in b and "Orange Ocean" not in b
    c = io.open(tmp_path / "examples" / "operator-console" / "index.html", encoding="utf-8").read()
    assert "demonstration" in c.lower() and len(set(re.findall(r'console-od\d[^"]*\.png', c))) == 5

def test_motion_inks_reveal_blocks():
    js = io.open(ROOT / "assets" / "motion.js", encoding="utf-8").read()
    m = re.search(r"querySelectorAll\('([^']*)'\)", js)
    assert m and ".reveal" in m.group(1), \
        "motion.js must ink .reveal blocks (chapter numerals, headings), not just .fig/[data-ink]"

def test_lineage_and_legal(tmp_path):
    B.render(tmp_path)
    l = io.open(tmp_path / "lineage" / "index.html", encoding="utf-8").read()
    assert "published as Groundwork" in l
    g = io.open(tmp_path / "legal" / "index.html", encoding="utf-8").read()
    assert "<h1>" in g

def test_sitemap_lists_every_reader_page(tmp_path):
    B.render(tmp_path)
    sm = io.open(tmp_path / "sitemap.xml", encoding="utf-8").read()
    dom = B.S.load()["domain"]
    read = re.findall(r"<loc>%s(/curriculum/read/[^<]*)</loc>" % re.escape(dom), sm)
    assert len(read) >= 120, len(read)
    assert "/curriculum/read/" in read, "the reader index keeps its directory URL"
    assert not [u for u in read if u.endswith("index.html")]
    for f in (tmp_path / "curriculum" / "read").glob("*.html"):
        want = "/curriculum/read/" + ("" if f.name == "index.html" else f.name)
        assert want in read, want
    assert "<loc>%s/</loc>" % dom in sm and "<loc>%s/start/</loc>" % dom in sm

def test_missing_template_stops_the_build(tmp_path, monkeypatch):
    spine = B.S.load()
    ghost = dict(B.pages(spine)[0]); ghost["template"] = "no-such-template.html"; ghost["out"] = "ghost/index.html"
    monkeypatch.setattr(B, "pages", lambda sp: [ghost])
    with pytest.raises(SystemExit) as e:
        B.render(tmp_path)
    assert "no-such-template.html" in str(e.value) and "ghost/index.html" in str(e.value)
