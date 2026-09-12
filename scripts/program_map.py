"""Relabel the pilot's Day 0 documents from the ten-capability frame to the four-stage spine."""
import io, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import spine as S

CAP_TO_SECTION = {1: "1.1", 2: "2.1", 3: "2.2", 4: "2.3", 5: "2.3", 6: "3.1", 7: "1.2", 8: "3.2", 9: "4.1", 10: "4.2"}

def _label(n):
    x = S.by_id(S.load(), CAP_TO_SECTION[n])
    return "%s %s" % (x["id"], x["title"])

def relabel(text):
    text = re.sub(r"\b[Cc]apability (\d+)\s*\((?:[^)]*)\)", lambda m: _label(int(m.group(1))), text)
    text = re.sub(r"\b[Cc]apability (\d+)\b", lambda m: _label(int(m.group(1))), text)
    text = re.sub(r"\bten capabilities\b", "four stages", text)
    text = re.sub(r"\bper capability\b", "per section", text)
    text = re.sub(r"\bcapabilities\b", "sections", text)
    # The pilot prose sometimes reads "Capability N, Title, ..." — once N is
    # replaced by "x.y Title" the title is left doubled ("x.y Title, Title,
    # ..."). Collapse that back down to a single mention.
    text = re.sub(r"\b(\d\.\d) ([^,\n]+), \2\b", r"\1 \2", text)
    return text

def _row_label(k_text):
    """Map one program-map '<div class="k">' capability label to its new
    stage.section id(s). The pilot's real markup does not always carry a
    single "Capability N" per row: some rows cover more than one old
    capability number ("Capabilities 4 and 5", "Capabilities 7, 8, and 9"),
    and one carries a trailing kicker ("Capability 10 · Measurement").
    This maps every number found, de-duplicates identical destinations
    (several old capabilities can land on the same new section), and
    preserves any trailing "· ..." kicker."""
    body = re.sub(r"^Capabilit(?:y|ies)\s*", "", k_text)
    if "·" in body:
        nums_part, suffix = body.split("·", 1)
        suffix = suffix.strip()
    else:
        nums_part, suffix = body, None
    nums = [int(n) for n in re.findall(r"\d+", nums_part)]
    labels = []
    for n in nums:
        lbl = _label(n)
        if lbl not in labels:
            labels.append(lbl)
    out = " · ".join(labels)
    if suffix:
        out = out + " · " + suffix
    return out

def relabel_html(html):
    def row(m):
        return '<div class="k">%s</div><div class="t">%s</div>' % (_row_label(m.group(1)), m.group(2))
    html = re.sub(r'<div class="k">(Capabilit(?:y|ies)[^<]*)</div><div class="t">([^<]*)</div>', row, html)
    return relabel(html)

def run(pilot_dir):
    # NOTE: the naive one-liner `io.open(p, "w", ...).write(f(io.open(p).read()))`
    # opens the write handle (truncating the file) before Python evaluates the
    # read inside its argument list, so it destroys the file's contents before
    # they are ever read. Read fully to a string first, then write.
    pilot_dir = Path(pilot_dir)
    for name in ("program-map.html",):
        p = pilot_dir / name
        text = io.open(p, encoding="utf-8").read()
        io.open(p, "w", encoding="utf-8", newline="\n").write(relabel_html(text))
    for name in ("01-SESSION-PLAN.md", "02-DAY0-RECORD.md", "starter/README.md"):
        p = pilot_dir / name
        text = io.open(p, encoding="utf-8").read()
        io.open(p, "w", encoding="utf-8", newline="\n").write(relabel(text))

if __name__ == "__main__":
    run(Path(__file__).resolve().parents[2] / "participants" / "dickey-dupuis")
    print("pilot relabeled")
