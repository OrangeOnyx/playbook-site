import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import program_map as P

def test_capability_phrase_mapping():
    assert P.relabel("full governance is capability 6") == "full governance is 3.1 Know your limits"
    assert P.relabel("ten capabilities built in sequence") == "four stages built in sequence"
    assert P.relabel("Capability 8 (Help me operate)") == "3.2 Help me operate"
    assert P.relabel("two per capability") == "two per section"

def test_html_program_column_rows():
    html = '<div class="k">Capability 1</div><div class="t">Know me</div>'
    assert '<div class="k">1.1 Know me</div>' in P.relabel_html(html)

def test_plural_capabilities_and_dedup_to_one_section():
    assert P.relabel("capabilities 4 and 5") == "2.3 Capture and commit"

def test_plural_capabilities_to_range_expands_and_maps_each_number():
    assert P.relabel("capabilities 1 to 3") == "1.1 Know me · 2.1 Know what is true · 2.2 Remember my world"

def test_html_row_with_three_numbers_maps_each_to_its_own_section():
    html = '<div class="k">Capabilities 7, 8, and 9</div><div class="t">X</div>'
    assert '<div class="k">1.2 Learn my work · 3.2 Help me operate · 4.1 Automate the proven work</div>' in P.relabel_html(html)

def test_html_row_with_kicker_suffix_is_preserved():
    html = '<div class="k">Capability 10 · Measurement</div><div class="t">Y</div>'
    assert '<div class="k">4.2 Improve and survive · Measurement</div>' in P.relabel_html(html)

def test_relabel_is_idempotent_on_a_plural_range():
    s = "capabilities 1 to 3"
    assert P.relabel(P.relabel(s)) == P.relabel(s)
