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
