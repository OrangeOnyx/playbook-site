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
