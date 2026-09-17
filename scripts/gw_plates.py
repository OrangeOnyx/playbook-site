# The AI Playbook Curriculum illustration system: the Annual Report world's
# drawing language (flat ink on paper, stars and rules, spot color at device
# scale) as self-contained SVG generators. Canonical copy: playbook-site/scripts/gw_plates.py.
# Used by: scripts/build_reader.py (the /curriculum/read/ pages), curriculum-pdf/build_curriculum_pdf.py
# (the book), and, as a byte-identical vendored copy, ai-playbook-curriculum/shared/graphics/plates.py
# (the repository's own stage plates). Edit here, then copy; tests/test_gw_plates.py checks the twin.

T = {
    "paper": "#F4EFE2", "paper_deep": "#EAE2CD", "ink": "#1E1B16",
    "ink_soft": "#5C554A", "rule": "#C9BFA8", "terra": "#C7681D",
    "terra_deep": "#A44E12", "mustard": "#D9A419", "mustard_deep": "#8F6D0C",
    "olive": "#5A6B4A", "olive_deep": "#49573C",
}
SANS = "Archivo, Arial, 'Helvetica Neue', sans-serif"
SLAB = "Besley, Georgia, 'Times New Roman', serif"

STOP_X = [90, 270, 450, 630]
STOP_Y = [46, 36, 26, 16]
STAGE_NAMES = ["STARTER", "INTERMEDIATE", "EXPERT", "FRONTIER OPERATOR"]


def _txt(x, y, s, size=9, fill=None, anchor="middle", weight=700, ls=1, family=SANS):
    fill = fill or T["ink_soft"]
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" letter-spacing="{ls}" fill="{fill}" '
            f'text-anchor="{anchor}">{s}</text>')


def brand_mark(size=32):
    """The Playbook mark: three terra bars, mustard Operator disc, ink ground."""
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 32 32" '
            f'xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
            f'<rect x="8" y="22" width="16" height="4" fill="{T["terra"]}"/>'
            f'<rect x="8" y="16" width="16" height="4" fill="{T["terra"]}"/>'
            f'<rect x="8" y="10" width="16" height="4" fill="{T["terra"]}"/>'
            f'<circle cx="16" cy="5.5" r="2.6" fill="{T["mustard"]}"/>'
            f'<path d="M5 29 H27" stroke="{T["ink"]}" stroke-width="2" '
            f'stroke-linecap="round"/></svg>')


def climb_line(current=None, w=720, labels=True, numerals=False):
    """The four-stage climb: a rising line of stars. current (1-4) gets the halo."""
    h = 64 if labels else 40
    pts = " ".join(f"{x},{y}" for x, y in zip(STOP_X, STOP_Y))
    out = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
           f'role="img" aria-label="The four stages, climbing.">',
           f'<polyline points="{pts}" fill="none" stroke="{T["terra_deep"]}" '
           f'stroke-width="1" opacity="0.75"/>']
    for i, (x, y) in enumerate(zip(STOP_X, STOP_Y), 1):
        if i == current:
            out.append(f'<circle cx="{x}" cy="{y}" r="9" fill="none" '
                       f'stroke="{T["terra_deep"]}" stroke-width="1.5" opacity="0.5"/>')
        out.append(f'<circle cx="{x}" cy="{y}" r="{5 if i == current else 4}" '
                   f'fill="{T["terra_deep"]}"/>')
        if labels:
            lab = f"{i} {STAGE_NAMES[i-1]}" if numerals else STAGE_NAMES[i - 1]
            out.append(_txt(x, 60, lab, 9))
    out.append("</svg>")
    return "".join(out)


def stage_emblem(n, size=120):
    """One emblem per stage: 1 first light, 2 the build, 3 the network, 4 the frontier."""
    td, ink, pd, rl = T["terra_deep"], T["ink"], T["paper_deep"], T["rule"]
    body = ""
    if n == 1:
        rays = []
        import math
        for k in range(8):
            a = k * math.pi / 4
            x1, y1 = 60 + 16 * math.cos(a), 58 + 16 * math.sin(a)
            x2, y2 = 60 + 30 * math.cos(a), 58 + 30 * math.sin(a)
            rays.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                        f'stroke="{td}" stroke-width="1.6"/>')
        body = (f'<path d="M14 102 H106" stroke="{ink}" stroke-width="2" stroke-linecap="round"/>'
                + "".join(rays) + f'<circle cx="60" cy="58" r="7" fill="{td}"/>')
    elif n == 2:
        body = (f'<path d="M14 102 H106" stroke="{ink}" stroke-width="2" stroke-linecap="round"/>'
                f'<rect x="34" y="86" width="52" height="12" fill="{pd}" stroke="{ink}" stroke-width="1.3"/>'
                f'<rect x="40" y="70" width="40" height="12" fill="{pd}" stroke="{ink}" stroke-width="1.3"/>'
                f'<rect x="46" y="54" width="28" height="12" fill="{pd}" stroke="{ink}" stroke-width="1.3"/>'
                f'<circle cx="60" cy="36" r="6" fill="{td}"/>')
    elif n == 3:
        body = (f'<path d="M14 102 H106" stroke="{ink}" stroke-width="2" stroke-linecap="round"/>'
                f'<polygon points="60,34 34,80 86,80" fill="none" stroke="{td}" stroke-width="1.3"/>'
                f'<line x1="86" y1="80" x2="104" y2="62" stroke="{rl}" stroke-width="1.2"/>'
                f'<circle cx="60" cy="34" r="6" fill="{td}"/>'
                f'<circle cx="34" cy="80" r="6" fill="{td}"/>'
                f'<circle cx="86" cy="80" r="6" fill="{td}"/>'
                f'<circle cx="104" cy="62" r="3" fill="{T["ink_soft"]}"/>')
    elif n == 4:
        body = (f'<path d="M14 102 H72" stroke="{ink}" stroke-width="2" stroke-linecap="round"/>'
                f'<path d="M72 102 L112 96" stroke="{rl}" stroke-width="1.4"/>'
                f'<circle cx="52" cy="84" r="5" fill="{td}"/>'
                f'<circle cx="72" cy="64" r="5" fill="{td}"/>'
                f'<circle cx="90" cy="46" r="5" fill="{td}"/>'
                f'<circle cx="104" cy="30" r="4" fill="{td}"/>'
                f'<circle cx="112" cy="18" r="3" fill="{T["terra"]}"/>'
                f'<polyline points="52,84 72,64 90,46 104,30 112,18" fill="none" '
                f'stroke="{td}" stroke-width="1" opacity="0.7"/>')
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 120 120" '
            f'xmlns="http://www.w3.org/2000/svg" aria-hidden="true">{body}</svg>')


GROUPS = {
    "overview":   "The stage at a glance",
    "start-here": "Start here",
    "individual": "Individual track",
    "company":    "Company track",
    "shared":     "Shared materials",
    "repos":      "Working repositories",
    "eli10":      "ELI10 companions",
}


def group_device(key, size=44):
    """Small recurring mark per group, constant across stages so the book and
    reader rhyme: flag / star / three stars / ledger / fork / paired stars."""
    td, ink, pd, rl = T["terra_deep"], T["ink"], T["paper_deep"], T["rule"]
    g = ""
    if key == "start-here":
        g = (f'<path d="M6 38 H38" stroke="{ink}" stroke-width="2" stroke-linecap="round"/>'
             f'<line x1="14" y1="36" x2="14" y2="8" stroke="{ink}" stroke-width="1.6"/>'
             f'<polygon points="14,8 32,13 14,18" fill="{td}"/>')
    elif key == "overview":
        g = (f'<path d="M6 38 H38" stroke="{ink}" stroke-width="2" stroke-linecap="round"/>'
             f'<circle cx="22" cy="20" r="9" fill="none" stroke="{td}" stroke-width="1.4" opacity="0.5"/>'
             f'<circle cx="22" cy="20" r="5" fill="{td}"/>')
    elif key == "individual":
        g = (f'<path d="M6 38 H38" stroke="{ink}" stroke-width="2" stroke-linecap="round"/>'
             f'<line x1="22" y1="33" x2="22" y2="24" stroke="{rl}" stroke-width="1.2"/>'
             f'<circle cx="22" cy="19" r="5" fill="{td}"/>')
    elif key == "company":
        g = (f'<path d="M6 38 H38" stroke="{ink}" stroke-width="2" stroke-linecap="round"/>'
             f'<circle cx="12" cy="22" r="4" fill="{td}"/>'
             f'<circle cx="22" cy="16" r="5" fill="{td}"/>'
             f'<circle cx="32" cy="22" r="4" fill="{td}"/>')
    elif key == "shared":
        g = (f'<rect x="8" y="10" width="28" height="24" fill="{pd}" stroke="{ink}" stroke-width="1.3"/>'
             f'<line x1="12" y1="17" x2="32" y2="17" stroke="{rl}" stroke-width="1.2"/>'
             f'<line x1="12" y1="22" x2="32" y2="22" stroke="{rl}" stroke-width="1.2"/>'
             f'<line x1="12" y1="27" x2="26" y2="27" stroke="{rl}" stroke-width="1.2"/>')
    elif key == "repos":
        g = (f'<line x1="22" y1="34" x2="22" y2="22" stroke="{ink}" stroke-width="1.6"/>'
             f'<line x1="22" y1="22" x2="12" y2="12" stroke="{ink}" stroke-width="1.4"/>'
             f'<line x1="22" y1="22" x2="32" y2="12" stroke="{ink}" stroke-width="1.4"/>'
             f'<circle cx="22" cy="36" r="4" fill="{td}"/>'
             f'<circle cx="12" cy="10" r="3.4" fill="{td}"/>'
             f'<circle cx="32" cy="10" r="3.4" fill="{td}"/>')
    elif key == "eli10":
        g = (f'<path d="M6 38 H38" stroke="{ink}" stroke-width="2" stroke-linecap="round"/>'
             f'<line x1="16" y1="20" x2="28" y2="26" stroke="{rl}" stroke-width="1.2"/>'
             f'<circle cx="14" cy="18" r="5.5" fill="{td}"/>'
             f'<circle cx="30" cy="27" r="3.4" fill="{T["terra"]}"/>')
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 44 44" '
            f'xmlns="http://www.w3.org/2000/svg" aria-hidden="true">{g}</svg>')


def parallel_tracks(w=960, h=300):
    """The Playbook (what you build) and the Curriculum (what you learn) as two rising
    lines with the same four stations. Replaces the retired two-axis map."""
    td, ink, isoft, ol = T["terra_deep"], T["ink"], T["ink_soft"], T["olive_deep"]
    xs = [120, 360, 600, 840]
    o = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" '
         f'aria-label="Two rising lines with the same four stations: the Playbook above, the Curriculum below.">',
         _txt(60, 28, "THE PLAYBOOK &#183; WHAT YOU BUILD", 11.5, ink, "start", ls=1.5),
         _txt(900, 28, "TEN SECTIONS IN FOUR STAGES", 10, isoft, "end"),
         f'<polyline points="{xs[0]},110 {xs[1]},98 {xs[2]},86 {xs[3]},74" fill="none" stroke="{td}" stroke-width="1.2" opacity="0.8"/>',
         _txt(60, 175, "THE CURRICULUM &#183; WHAT YOU LEARN", 11.5, ink, "start", ls=1.5),
         _txt(900, 175, "TWO TRACKS AT EVERY STAGE", 10, isoft, "end"),
         f'<polyline points="{xs[0]},262 {xs[1]},250 {xs[2]},238 {xs[3]},226" fill="none" stroke="{ol}" stroke-width="1.2" opacity="0.8"/>']
    for i, (x, name) in enumerate(zip(xs, STAGE_NAMES), 1):
        ya, yb = 110 - 12 * (i - 1), 262 - 12 * (i - 1)
        o.append(f'<circle cx="{x}" cy="{ya}" r="5" fill="{td}"/>')
        o.append(f'<circle cx="{x}" cy="{yb}" r="5" fill="{ol}"/>')
        o.append(_txt(x, 138, f"{i} {name}", 9))
        o.append(_txt(x, 290, f"{i} {name}", 9))
    o.append("</svg>")
    return "".join(o)


def cover_plate(w=960, h=540):
    """The repository cover: mark, title, imprint, the four-station climb."""
    ink, td, isoft = T["ink"], T["terra_deep"], T["ink_soft"]
    climb = climb_line(None, 720, labels=True, numerals=True).replace("<svg ", '<svg x="120" y="380" width="720" height="64" ', 1)
    return (f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" '
            f'aria-label="The AI Playbook Curriculum: four stages, two tracks.">'
            f'<rect width="{w}" height="{h}" fill="{T["paper"]}"/>'
            f'<g transform="translate(120,70)">{brand_mark(44)}</g>'
            + _txt(180, 100, "THE AI PLAYBOOK", 13, ink, "start", 900, 4)
            + f'<line x1="120" y1="126" x2="840" y2="126" stroke="{ink}" stroke-width="2"/>'
            + _txt(120, 176, "THE CURRICULUM", 44, ink, "start", 900, -1)
            + _txt(120, 236, "FOUR STAGES &#183; TWO TRACKS &#183; TWO VOICES", 12, td, "start", 700, 2.5)
            + _txt(120, 290, "Free, ungated, MIT. Curriculum authorship: Jake Van Clief. By Cypress Command.", 13, isoft, "start", 400, 0, SLAB)
            + f'<rect x="120" y="320" width="46" height="3" fill="{td}"/>'
            + climb + "</svg>")
