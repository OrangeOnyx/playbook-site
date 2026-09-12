"""Field Guide PDF from the built site. python scripts/build_field_guide.py  (needs dist/ and Edge)"""
import io, re, subprocess, sys, time, uuid, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import spine as S
ROOT = Path(__file__).resolve().parents[1]
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

def assemble():
    sp = S.load()
    css = (io.open(ROOT / "assets" / "guide.css", encoding="utf-8").read()
           + io.open(ROOT / "assets" / "playbook-import.css", encoding="utf-8").read()
           + io.open(ROOT / "assets" / "playbook.css", encoding="utf-8").read())
    parts = ['<!doctype html><html lang="en"><head><meta charset="utf-8"><title>The AI Playbook, Field Guide</title>',
             '<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;700;900&family=Besley:ital,wght@0,400;0,700;1,400&family=Courier+Prime&display=swap" rel="stylesheet">',
             "<style>%s .fig{opacity:1} .s,.f,.t{opacity:1;stroke-dashoffset:0} .fig .s{stroke-dashoffset:0!important;opacity:1!important} h2.sec{page-break-before:always} .card{page-break-before:always;page-break-inside:avoid}</style></head><body><main>" % css,
             "<h1>The AI Playbook</h1><p class='lede'>Field Guide. Four stages, ten sections, fifteen canonical documents. By Cypress Command.</p>",
             io.open(ROOT / "content" / "plates" / "fig-02.html", encoding="utf-8").read().replace('class="fig plate"', 'class="fig plate ink"')]
    for x in S.sections(sp):
        parts.append('<h2 class="sec">%s %s</h2><p>Builds: %s.</p><p class="prov">Source: %s.</p>' % (x["id"], x["title"], "; ".join(x["artifacts"]), x["provenance"]))
        for d in x["docs"]:
            parts.append(io.open(ROOT / "content" / "docs" / ("doc-%02d.html" % d), encoding="utf-8").read())
    parts.append(io.open(ROOT / "content" / "plates" / "fig-07.html", encoding="utf-8").read().replace('class="fig plate"', 'class="fig plate ink"'))
    parts.append("</main></body></html>")
    html = "\n".join(parts)
    (ROOT / "print").mkdir(exist_ok=True)
    p = ROOT / "print" / "field-guide.build.html"; io.open(p, "w", encoding="utf-8", newline="\n").write(html)
    return p, html

def render(src, pdf):
    prof = Path(os.environ["TEMP"]) / ("edge-" + uuid.uuid4().hex)
    subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--user-data-dir=%s" % prof, "--no-pdf-header-footer",
                    "--print-to-pdf=%s" % pdf, src.resolve().as_uri()], check=True, timeout=180)
    # Edge's headless PDF write can finish a beat after the process exits; wait for it to land and settle.
    deadline = time.time() + 15
    last_size = -1
    while time.time() < deadline:
        if pdf.exists():
            size = pdf.stat().st_size
            if size > 0 and size == last_size:
                return
            last_size = size
        time.sleep(0.5)

if __name__ == "__main__":
    src, html = assemble()
    assert len(re.findall(r"<h3>Document \d\d:", html)) == 15, "fifteen documents expected"
    out = ROOT / "assets" / "The-AI-Playbook-Field-Guide.pdf"
    render(src, out)
    print("rendered", out, out.stat().st_size, "bytes")
