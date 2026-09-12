"""Import the AI Playbook v2.0 site (import/playbook-v2) into content partials.
Idempotent: rerun any time; output is fully regenerated.

Real-markup notes (verified against import/playbook-v2, Sept 2026 export):
- Interview cards nest their six tab panels inside div.body > div > div.inner > div.panel*,
  and panel content can itself contain nested divs (figure wrappers), so panels are located
  by their opening tag position and sliced up to the next panel's opening tag (or, for the
  last panel, up to the card's own four wrapper-closing </div> before </section>).
- Plates are NOT already `<figure class="plate">`; the source wraps them as
  `<figure class="figure" id="..."><div class="plate ..."><svg class="fig ...">...</svg></div>
  <figcaption class="caption">...</figcaption></figure>`. The target site (assets/guide.css +
  assets/motion.js) expects a plain `<figure class="fig plate">` holding just the <svg> and the
  <figcaption> -- guide.css defines `.fig.plate{...}` as a single combined selector and
  motion.js does `querySelectorAll('.fig, [data-ink]')` and toggles `.ink` on that same element,
  so the "plate" class alone (no "fig") would never be picked up by the motion layer.
- playbook.css repeats one ~24KB base64 PNG watermark six times (nav/byline/footer x2 each);
  after slimming to the kept sections that is still ~112KB, over the 90KB budget the gate
  enforces. The five duplicate copies are byte-identical, so they are deduped into one
  `:root` custom property and referenced with `var(...)`, which is a purely mechanical,
  visually-neutral shrink.
"""
import io, re
from pathlib import Path

WORD_FIXES = [
    ("Depth by level", "Depth by stage"),
    ("by level", "by stage"),
    ("Level notes", "Stage notes"),
]

# Em dashes never survive import; the gate would fail them. A plain literal replace of the
# dash character leaves "word — word" as "word ,  word" (double space); collapse the
# surrounding whitespace along with the dash so the comma joins cleanly instead.
EM_DASH_RE = re.compile(r"\s*(?:—|&mdash;)\s*")


def _read(p):
    return io.open(p, encoding="utf-8").read()


def _write(p, s):
    p.parent.mkdir(parents=True, exist_ok=True)
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)


def _fix_words(s):
    s = EM_DASH_RE.sub(", ", s)
    for a, b in WORD_FIXES:
        s = s.replace(a, b)
    return s


def _to_groundwork_fig(svg_html):
    # playbook.js used data-anim + .is-in; motion.js uses .fig + .ink
    return svg_html.replace(" data-anim", "").replace("data-anim ", "").replace("data-anim", "")


CARD_RE = re.compile(r'<section class="icard reveal" id="(s\d+)"')
PANEL_OPEN_RE = re.compile(r'<div class="panel" role="tabpanel"[^>]*data-title="([^"]+)"[^>]*>')
LAST_PANEL_TRAILER_RE = re.compile(r'(?:\s*</div>){4}\s*</section>\s*\Z')


def import_cards(src, out):
    s = _read(src / "playbook" / "interviews.html")
    starts = [(m.start(), m.group(1)) for m in CARD_RE.finditer(s)]
    tail = s.find("</article>")
    if tail == -1:
        tail = len(s)
    n = 0
    for i, (pos, cid) in enumerate(starts):
        card_end = starts[i + 1][0] if i + 1 < len(starts) else tail
        html = s[pos:card_end]

        source = re.search(r'<span class="no"><small>([^<]*)</small>', html).group(1).strip()
        title_m = re.search(r"<h3>(.*?)</h3>", html, re.S)
        title = re.sub(r"<[^>]+>", "", title_m.group(1)).strip() if title_m else ""
        artifact = re.search(r'<p class="artifact">(.*?)</p>', html, re.S)

        panel_opens = list(PANEL_OPEN_RE.finditer(html))
        body = ['<div class="card-body" data-card="%s" data-source="%s" data-title="%s">'
                % (cid, source, _fix_words(title))]
        if artifact:
            body.append('<p class="artifact">%s</p>' % _fix_words(artifact.group(1).strip()))

        for j, pm in enumerate(panel_opens):
            ptitle = _fix_words(pm.group(1))
            content_start = pm.end()
            if j + 1 < len(panel_opens):
                raw = html[content_start:panel_opens[j + 1].start()]
                raw = re.sub(r"\s*</div>\s*\Z", "", raw, count=1)
            else:
                raw = html[content_start:]
                trimmed = LAST_PANEL_TRAILER_RE.sub("", raw)
                raw = trimmed if trimmed != raw else re.sub(r"\s*</section>\s*\Z", "", raw)
            body.append('<section class="panel" data-title="%s"><h3>%s</h3>%s</section>'
                         % (ptitle, ptitle, _fix_words(_to_groundwork_fig(raw.strip()))))
        body.append("</div>")
        _write(out / "content" / "cards" / (cid + ".html"), _fix_words("\n".join(body)))
        n += 1
    return n


FIGURE_RE = re.compile(r'<figure class="figure"[^>]*>.*?</figure>', re.S)


def _plate_partial(fig_html):
    """Reshape a source `<figure class="figure">` (div.plate wrapper + replay button +
    svg + figcaption) into the Groundwork-vocabulary `<figure class="fig plate">` that
    guide.css/motion.js style and animate directly -- just the drawing and its caption."""
    fig_html = _to_groundwork_fig(fig_html)
    svg_m = re.search(r"<svg\b.*?</svg>", fig_html, re.S)
    cap_m = re.search(r"<figcaption.*?</figcaption>", fig_html, re.S)
    svg = svg_m.group(0) if svg_m else ""
    cap = cap_m.group(0) if cap_m else ""
    return '<figure class="fig plate">%s%s</figure>' % (svg, cap)


def import_plates(src, out):
    n = 0
    seen = set()
    for page in ("index.html", "plates.html", "interviews.html"):
        s = _read(src / "playbook" / page)
        for fig in FIGURE_RE.findall(s):
            m = re.search(r"Fig\.\s*(\d+)", fig)
            if not m:
                continue
            num = m.group(1).zfill(2)
            if num in seen:
                continue
            seen.add(num)
            _write(out / "content" / "plates" / ("fig-%s.html" % num), _fix_words(_plate_partial(fig)))
            n += 1
    return n


CHAPTER_RE = re.compile(r'<section class="chapter-sec" id="(ch-\d+)">(.*?)</section>', re.S)


def import_chapters(src, out):
    s = _read(src / "playbook" / "index.html")
    n = 0
    for cid, inner in CHAPTER_RE.findall(s):
        _write(out / "content" / "front" / (cid + ".html"), _fix_words(_to_groundwork_fig(inner.strip())))
        n += 1
    return n


KEEP_BLOCKS = ["---- type ----", "---- cover ----", "---- plate ----", "---- page layout: toc + article ----",
               "chapter with a sticky plate", "---- reveal ----", "---- part-II intro + tools ----",
               "---- interview card ----", "---- part divider + footer ----", "---- gallery ----",
               "---- mobile ----", "---- print"]

DATA_URI_RE = re.compile(r"url\(data:[^)]*\)")


def _dedupe_data_uris(css):
    """playbook.css repeats a handful of large data: URIs (a watermark PNG) verbatim across
    several selectors. Byte-identical repeats are pure bloat; fold each one into a single
    :root custom property the first time it appears and reference it with var(...) after."""
    counts = {}
    for m in DATA_URI_RE.finditer(css):
        counts[m.group(0)] = counts.get(m.group(0), 0) + 1
    var_for, var_defs = {}, []

    def repl(m):
        uri = m.group(0)
        if counts[uri] < 2:
            return uri
        if uri not in var_for:
            var_for[uri] = "--pb-img-%d" % (len(var_for) + 1)
            var_defs.append((var_for[uri], uri))
        return "var(%s)" % var_for[uri]

    out = DATA_URI_RE.sub(repl, css)
    if var_defs:
        out = ":root{%s}\n" % "".join("%s:%s;" % (n, u) for n, u in var_defs) + out
    return out


def import_css(src, out):
    css = _read(src / "assets" / "playbook.css")
    parts = re.split(r"(/\*[^*]{4,90}\*/)", css)
    keep, on = [], False
    for chunk in parts:
        if chunk.startswith("/*"):
            on = any(k in chunk for k in KEEP_BLOCKS)
            if on:
                keep.append(chunk)
        elif on:
            keep.append(chunk)
    slim = "".join(keep).replace(".is-in", ".ink").replace("[data-anim]", ".fig")
    slim = _dedupe_data_uris(slim)
    header = "/* The AI Playbook: page-specific layer on top of guide.css (imported from playbook v2, slimmed). */\n"
    out_css = header + slim
    _write(out / "assets" / "playbook.css", out_css)
    return len(out_css)


def run(src, out):
    return {"cards": import_cards(src, out), "plates": import_plates(src, out),
            "chapters": import_chapters(src, out), "css_bytes": import_css(src, out)}


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    print(run(root / "import" / "playbook-v2", root))
