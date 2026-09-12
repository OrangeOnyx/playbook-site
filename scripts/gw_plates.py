# The Groundwork Curriculum illustration system: the Annual Report world's
# drawing language (flat ink on paper, stars and rules, spot color at device
# scale) as self-contained SVG generators. Used by BOTH renderers so the book
# and the site reader can never drift apart visually:
#   - curriculum-pdf/build_curriculum_pdf.py   (the 600-page book)
#   - print/build-curriculum-reader.py         (the /curriculum/read/ pages)
# Every SVG carries explicit fills/fonts (no CSS vars), so plates render
# identically in headless Edge print and in any browser.
# Design authority: DESIGN.md at the project root. Rules honored here:
# square corners; circles only for stars (plotted points) and the Operator
# disc; oxblood never appears (no prohibitions are drawn in these plates);
# text-carrying fields only ink/terra-deep/olive/olive-deep.

T = {
    "paper": "#F4EFE2", "paper_deep": "#EAE2CD", "ink": "#1E1B16",
    "ink_soft": "#5C554A", "rule": "#C9BFA8", "terra": "#C7681D",
    "terra_deep": "#A44E12", "mustard": "#D9A419", "mustard_deep": "#8F6D0C",
    "olive": "#5A6B4A", "olive_deep": "#49573C",
}
SANS = "Archivo, Arial, 'Helvetica Neue', sans-serif"
SLAB = "Besley, Georgia, 'Times New Roman', serif"

STOP_X = [60, 210, 360, 510, 660]
STOP_Y = [46, 39, 32, 25, 18]
LEVEL_NAMES = ["ESSENTIALS", "INTERMEDIATE", "ADVANCED", "PROFESSIONAL", "FRONTIER"]


def _txt(x, y, s, size=9, fill=None, anchor="middle", weight=700, ls=1, family=SANS):
    fill = fill or T["ink_soft"]
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" letter-spacing="{ls}" fill="{fill}" '
            f'text-anchor="{anchor}">{s}</text>')


def brand_mark(size=32):
    """The Groundwork mark: three terra bars, mustard Operator disc, ink ground."""
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 32 32" '
            f'xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
            f'<rect x="8" y="22" width="16" height="4" fill="{T["terra"]}"/>'
            f'<rect x="8" y="16" width="16" height="4" fill="{T["terra"]}"/>'
            f'<rect x="8" y="10" width="16" height="4" fill="{T["terra"]}"/>'
            f'<circle cx="16" cy="5.5" r="2.6" fill="{T["mustard"]}"/>'
            f'<path d="M5 29 H27" stroke="{T["ink"]}" stroke-width="2" '
            f'stroke-linecap="round"/></svg>')


def climb_line(current=None, w=720, labels=True, numerals=False):
    """The five-level climb: a rising line of stars. current (1-5) gets the halo."""
    h = 64 if labels else 40
    pts = " ".join(f"{x},{y}" for x, y in zip(STOP_X, STOP_Y))
    out = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
           f'role="img" aria-label="The five levels, climbing.">',
           f'<polyline points="{pts}" fill="none" stroke="{T["terra_deep"]}" '
           f'stroke-width="1" opacity="0.75"/>']
    for i, (x, y) in enumerate(zip(STOP_X, STOP_Y), 1):
        if i == current:
            out.append(f'<circle cx="{x}" cy="{y}" r="9" fill="none" '
                       f'stroke="{T["terra_deep"]}" stroke-width="1.5" opacity="0.5"/>')
        out.append(f'<circle cx="{x}" cy="{y}" r="{5 if i == current else 4}" '
                   f'fill="{T["terra_deep"]}"/>')
        if labels:
            lab = f"{i} {LEVEL_NAMES[i-1]}" if numerals else LEVEL_NAMES[i - 1]
            out.append(_txt(x, 60, lab, 9))
    out.append("</svg>")
    return "".join(out)


def level_emblem(n, size=120):
    """One emblem per level, same star-and-rule language, drawn at 120x120.
    1 first light - 2 the build - 3 the network - 4 the lead - 5 the frontier."""
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
        body = (f'<path d="M14 102 H106" stroke="{ink}" stroke-width="2" stroke-linecap="round"/>'
                f'<line x1="60" y1="40" x2="36" y2="72" stroke="{rl}" stroke-width="1.2"/>'
                f'<line x1="60" y1="40" x2="84" y2="72" stroke="{rl}" stroke-width="1.2"/>'
                f'<circle cx="60" cy="40" r="7" fill="{td}"/>'
                f'<circle cx="36" cy="72" r="4" fill="{T["ink_soft"]}"/>'
                f'<circle cx="84" cy="72" r="4" fill="{T["ink_soft"]}"/>'
                f'<circle cx="24" cy="90" r="4" fill="{T["ink_soft"]}"/>'
                f'<circle cx="96" cy="90" r="4" fill="{T["ink_soft"]}"/>')
    elif n == 5:
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
    "overview":   "The level at a glance",
    "start-here": "Start here",
    "individual": "Individual track",
    "company":    "Company track",
    "shared":     "Shared materials",
    "repos":      "Working repositories",
    "eli10":      "ELI10 companions",
}


def group_device(key, size=44):
    """Small recurring mark per group, constant across levels so the book and
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


def axis_bands(w=960, h=330):
    """The doctrine-vs-curriculum map: six layer squares on a ground line above,
    five stars on a rising line below. Ported from the site hub drawing."""
    td, ink, isoft = T["terra_deep"], T["ink"], T["ink_soft"]
    sq = lambda x, fill: f'<rect x="{x}" y="85" width="14" height="14" fill="{fill}"/>'
    o = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" role="img" '
         f'aria-label="Two bands: the doctrine as six squares on a ground line; '
         f'the curriculum as five stars on a rising line.">',
         _txt(60, 28, "THE DOCTRINE &#183; WHAT YOU BUILD &#183; SIX LAYERS", 11.5, ink, "start", ls=1.5),
         _txt(900, 28, "THE GUIDE + THE FIELD GUIDE", 10, isoft, "end"),
         _txt(215, 60, "PHASE 1 &#183; REQUIRED FIRST", 9), _txt(475, 60, "PHASE 2 &#183; ACTIVATION", 9),
         _txt(737, 60, "PHASE 3 &#183; DURABILITY", 9),
         f'<line x1="60" y1="92" x2="900" y2="92" stroke="{ink}" stroke-width="2" opacity="0.85"/>',
         sq(93, td), sq(215, td), sq(337, td),
         f'<circle cx="475" cy="92" r="9" fill="{T["mustard"]}"/>',
         sq(595, T["olive_deep"]), sq(730, T["olive_deep"]), sq(865, T["olive_deep"]),
         _txt(100, 122, "IDENTITY", 9), _txt(222, 122, "KNOWLEDGE", 9), _txt(344, 122, "GOVERNANCE", 9),
         _txt(475, 122, "THE OPERATOR", 9), _txt(602, 122, "CONTINUITY", 9),
         _txt(737, 122, "MEASUREMENT", 9), _txt(872, 122, "OPERATING RHYTHM", 9),
         _txt(60, 150, "BUILT ONCE, FOR THE BUSINESS. STRICT ORDER.", 9.5, anchor="start"),
         _txt(60, 200, "THE CURRICULUM &#183; WHAT YOU LEARN &#183; FIVE LEVELS", 11.5, ink, "start", ls=1.5),
         _txt(900, 200, "THE SITE + GITHUB + THIS BOOK", 10, isoft, "end"),
         f'<polyline points="100,290 300,278 500,264 700,248 880,230" fill="none" '
         f'stroke="{td}" stroke-width="1.2" opacity="0.8"/>']
    for x, y, lab in [(100, 290, "1 ESSENTIALS"), (300, 278, "2 INTERMEDIATE"),
                      (500, 264, "3 ADVANCED"), (700, 248, "4 PROFESSIONAL"),
                      (880, 230, "5 FRONTIER")]:
        o.append(f'<circle cx="{x}" cy="{y}" r="5" fill="{td}"/>')
        o.append(_txt(x, 313, lab, 9))
    o.append("</svg>")
    return "".join(o)
