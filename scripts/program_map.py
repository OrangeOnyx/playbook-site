"""Relabel the pilot's Day 0 documents from the ten-capability frame to the four-stage spine."""
import io, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import spine as S

CAP_TO_SECTION = {1: "1.1", 2: "2.1", 3: "2.2", 4: "2.3", 5: "2.3", 6: "3.1", 7: "1.2", 8: "3.2", 9: "4.1", 10: "4.2"}

def _label(n):
    x = S.by_id(S.load(), CAP_TO_SECTION[n])
    return "%s %s" % (x["id"], x["title"])

def _extract_nums(s):
    """Pull the old capability numbers out of a phrase like "4 and 5",
    "1 to 3" (a range, expanded inclusively), or "7, 8, and 9"."""
    m = re.search(r"(\d+)\s+to\s+(\d+)", s)
    if m:
        return list(range(int(m.group(1)), int(m.group(2)) + 1))
    return [int(n) for n in re.findall(r"\d+", s)]

def _labels_for_nums(nums):
    """Map each old capability number to its new "x.y Title" section label,
    de-duplicating (several old capabilities can land on the same new
    section) while preserving first-seen order, then join with " · "."""
    labels = []
    for n in nums:
        lbl = _label(n)
        if lbl not in labels:
            labels.append(lbl)
    return " · ".join(labels)

def relabel(text):
    text = re.sub(r"\b[Cc]apability (\d+)\s*\((?:[^)]*)\)", lambda m: _label(int(m.group(1))), text)
    text = re.sub(r"\b[Cc]apability (\d+)\b", lambda m: _label(int(m.group(1))), text)
    # Plural "capabilities N[, M ...][ and/to L]" covers more than one old
    # capability number in a single mention (e.g. "capabilities 4 and 5",
    # "capabilities 1 to 3", "Capabilities 7, 8, and 9"). Map every number
    # found onto its new section id(s) instead of leaving the old numbers
    # sitting next to the word "sections" (which don't correspond to
    # anything in the new 1.1-4.2 id scheme).
    text = re.sub(
        r"\b[Cc]apabilities (\d+(?:,\s*\d+)*(?:,?\s*(?:and|to)\s+\d+)?)\b",
        lambda m: _labels_for_nums(_extract_nums(m.group(1))),
        text,
    )
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
    out = _labels_for_nums(_extract_nums(nums_part))
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
    #
    # Walk every markdown and html file under pilot_dir recursively (not just
    # the brief's four named files) so any pilot document carrying old
    # "capability N" phrasing gets relabeled, wherever it lives. program-map.html
    # keeps the row-aware relabel_html(); every other .md/.html file gets plain
    # relabel(), which only touches numbered/count phrasing ("Capability N",
    # "ten capabilities", "per capability", plural "capabilities") and leaves
    # generic, unnumbered uses of the word alone. Only rewrite a file when its
    # content actually changes, so untouched files keep their original mtime
    # and no-op diffs don't appear in git status.
    pilot_dir = Path(pilot_dir)
    for p in sorted(pilot_dir.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in (".md", ".html"):
            continue
        text = io.open(p, encoding="utf-8").read()
        new_text = relabel_html(text) if p.name == "program-map.html" else relabel(text)
        if new_text != text:
            io.open(p, "w", encoding="utf-8", newline="\n").write(new_text)

if __name__ == "__main__":
    run(Path(__file__).resolve().parents[2] / "participants" / "dickey-dupuis")
    print("pilot relabeled")
