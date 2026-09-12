"""The four plates that changed with the numbering. Line on paper, three inks, Groundwork .fig vocabulary."""
import io, sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import spine as S

def S_(d, cls="", i=0, w=1.2):
    return '<path class="s %s" pathLength="1" style="--i:%d" d="%s" stroke-width="%s"/>' % (cls, i, d, w)
def T(x, y, s, i=0, anchor="middle", cls="", size=10):
    return '<text class="t %s" style="--i:%d" x="%.1f" y="%.1f" text-anchor="%s" font-size="%s">%s</text>' % (cls, i, x, y, anchor, size, s)
def C(cx, cy, r, i=0, cls=""):
    return '<circle class="s %s" pathLength="1" style="--i:%d" cx="%.1f" cy="%.1f" r="%s"/>' % (cls, i, cx, cy, r)
def plate(num, ink, vb, body, caption):
    return ('<figure class="fig plate" id="fig-%s"><span class="plate-label">PLATE %s · %s</span>'
            '<svg viewBox="%s" role="img" aria-label="%s">%s</svg>'
            '<figcaption><span class="fignum">Fig. %s</span><span>%s</span></figcaption>'
            '<button class="replay" type="button">Replay</button></figure>\n') % (num, num, ink, vb, caption, body, num, caption)

def ladder(sp):
    b, i = [], 0
    for st in sp["stages"]:
        k = st["number"] - 1; x = 40 + k * 170; y = 210 - k * 50; w = 150
        b.append(S_("M%d %dh%dv%dh-%dz" % (x, y, w, 300 - y, w), "mus", i, 1.4)); i += 1
        b.append(T(x + 8, y + 18, "%d %s" % (st["number"], st["name"].upper()), i, "start", "", 10)); i += 1
        secs = [s for s in S.sections(sp) if s["stage"] == st["number"]]
        for j, s in enumerate(secs):
            b.append(T(x + 8, y + 36 + j * 14, "%s %s" % (s["id"], s["title"]), i, "start", "lt", 8)); i += 1
        b.append(T(x + 8, 292, st["weeks"].upper(), i, "start", "lt", 7)); i += 1
        if k < 3:
            lx, ly = x + w + 4, y - 50 + 6
            b.append(S_("M%d %dh12v9h-12zM%d %dv-4a3 3 0 0 1 6 0v4" % (lx, ly, lx + 3, ly), "", i, 1)); i += 1
    b.append(S_("M20 300H720", "lt", i, 1)); i += 1
    b.append(T(370, 318, "EACH STAGE COMPLETE IN ITSELF · A GATE BETWEEN EVERY TWO · NOTHING SKIPPED", i, "middle", "lt", 7))
    return plate("02", "MUSTARD", "0 0 740 330", "".join(b), "The ladder: four stages, ten sections, a lock at every gate")

def cover(sp):
    b, i = [], 0
    cx, cy = 300, 200
    for r in (40, 80, 120): b.append(C(cx, cy, r, i, "lt")); i += 1
    for k in range(6):
        a = math.radians(-90 + k * 60)
        b.append(S_("M%d %dL%.1f %.1f" % (cx, cy, cx + 120 * math.cos(a), cy + 120 * math.sin(a)), "lt", i, .8)); i += 1
    pts = [(cx + 95 * math.cos(math.radians(-90 + k * 60)), cy + 95 * math.sin(math.radians(-90 + k * 60))) for k in range(6)]
    b.append(S_("M" + "L".join("%.1f %.1f" % p for p in pts) + "Z", "acc", i, 1.6)); i += 1
    for k, lab in enumerate(["CONTEXT", "TRUTH", "MEMORY", "WORKFLOW", "GOVERNANCE", "OPERATIONS"]):
        a = math.radians(-90 + k * 60); cosv = math.cos(a)
        anchor = "start" if cosv < -0.15 else ("end" if cosv > 0.15 else "middle")
        b.append(T(cx + 140 * math.cos(a), cy + 140 * math.sin(a) + 3, lab, i, anchor, "lt", 8)); i += 1
    secs = S.sections(sp); n = len(secs)
    for j, s in enumerate(secs):
        a = math.radians(-90 + j * (360 / n)); dx, dy = cx + 165 * math.cos(a), cy + 165 * math.sin(a)
        b.append(C(dx, dy, 14, i, "mus")); i += 1
        b.append(S_("M%.1f %.1fL%.1f %.1f" % (dx, dy, dx + 9 * math.cos(a), dy + 9 * math.sin(a)), "mus", i, 1.6)); i += 1
        b.append(T(dx, dy + 26 if dy > cy else dy - 20, s["id"], i, "middle", "", 9)); i += 1
    for st in sp["stages"]:
        k = st["number"] - 1; a0 = math.radians(-90 + k * 90 - 12); a1 = math.radians(-90 + k * 90 + 78)
        b.append(S_("M%.1f %.1fA205 205 0 0 1 %.1f %.1f" % (cx + 205 * math.cos(a0), cy + 205 * math.sin(a0), cx + 205 * math.cos(a1), cy + 205 * math.sin(a1)), "mus", i, 1)); i += 1
    return plate("00", "TERRA", "0 -18 600 436", "".join(b), "Cover: ten section dials in four stage arcs around the readiness radar")

def fork(sp):
    b, i = [], 0
    b.append(S_("M20 100H120", "", i, 1.6)); i += 1
    b.append(C(120, 100, 6, i, "")); i += 1
    b.append(T(70, 90, "1.0 INTAKE", i, "middle", "", 8)); i += 1
    b.append(S_("M126 100Q170 100 200 70H700", "acc", i, 1.6)); i += 1
    b.append(S_("M126 100Q170 100 200 130H700", "oli", i, 1.6)); i += 1
    b.append(T(712, 73, "PERSONAL", i, "start", "acc", 8)); i += 1
    b.append(T(712, 133, "BUSINESS", i, "start", "oli", 8)); i += 1
    for st in sp["stages"]:
        x = 260 + (st["number"] - 1) * 130
        b.append(S_("M%d 55V145" % x, "mus", i, 1.2)); i += 1
        b.append(C(x, 70, 4, i, "acc")); i += 1
        b.append(C(x, 130, 4, i, "oli")); i += 1
        b.append(T(x, 45, "%d %s" % (st["number"], st["name"].upper()), i, "middle", "", 8)); i += 1
    b.append(T(400, 175, "ONE CHOICE AT INTAKE · TWO LANES · THE SAME FOUR STATIONS", i, "middle", "lt", 7))
    return plate("14", "TERRA", "0 0 800 190", "".join(b), "The fork: one workflow chosen at Intake, two lanes through the same four stages")

def track(sp):
    b, i = [], 0
    for y, cls, lab in ((60, "acc", "PERSONAL"), (100, "oli", "BUSINESS"), (150, "mus", "CURRICULUM")):
        b.append(S_("M40 %dH700" % y, cls, i, 1.6 if cls != "mus" else 1.2)); i += 1
        b.append(T(712, y + 3, lab, i, "start", cls, 8)); i += 1
    for st in sp["stages"]:
        x = 120 + (st["number"] - 1) * 170
        b.append(S_("M%d 45V165" % x, "lt", i, 1)); i += 1
        # Same inks as fig-14: the personal lane is accent, the business lane olive.
        for y, cls in ((60, "acc"), (100, "oli")): b.append(C(x, y, 4, i, cls)); i += 1
        b.append(S_("M%d 150v-8h-6v8M%d 150v-14h-6v14" % (x, x + 10), "mus", i, 1)); i += 1
        b.append(T(x, 35, "%d %s" % (st["number"], st["name"].upper()), i, "middle", "", 8)); i += 1
        b.append(T(x, 178, "%d.1  %d.2  ...  DEEPER" % (st["number"], st["number"]), i, "middle", "lt", 7)); i += 1
    return plate("15", "MUSTARD", "0 0 800 190", "".join(b), "The parallel track: the Curriculum stops at the same four stations and goes deeper at each")

def run(out):
    sp = S.load(); d = Path(out) / "content" / "plates"; d.mkdir(parents=True, exist_ok=True)
    for num, html in (("02", ladder(sp)), ("00", cover(sp)), ("14", fork(sp)), ("15", track(sp))):
        io.open(d / ("fig-%s.html" % num), "w", encoding="utf-8", newline="\n").write(html)

if __name__ == "__main__":
    run(Path(__file__).resolve().parents[1]); print("plates redrawn")
