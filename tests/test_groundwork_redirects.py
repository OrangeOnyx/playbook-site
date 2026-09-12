import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import pytest
from scripts import spine as S
from scripts import groundwork_redirects as GR


def test_destinations_are_absolute_on_the_playbook_domain():
    sp = S.load()
    cfg = GR.build(sp)
    dom = sp["domain"]
    assert cfg["redirects"], "expected at least one rule"
    for r in cfg["redirects"]:
        assert r["destination"].startswith(dom), r


def test_last_rule_is_the_catch_all():
    sp = S.load()
    cfg = GR.build(sp)
    assert cfg["redirects"][-1]["source"] == "/(.*)"


def test_every_rule_is_permanent():
    sp = S.load()
    cfg = GR.build(sp)
    for r in cfg["redirects"]:
        assert r["permanent"] is True


def test_raises_when_a_catch_all_precedes_a_literal():
    sp = S.load()
    bad = dict(sp)
    bad["redirects"] = list(sp["redirects"])
    bad["redirects"].insert(0, {"source": "/(.*)", "destination": "/$1"})
    with pytest.raises(ValueError):
        GR.build(bad)


def test_merge_config_preserves_existing_headers_verbatim():
    rules = [{"source": "/x", "destination": "https://playbook.adamabdalla.com/x", "permanent": True}]
    headers = [{"source": "/(.*)", "headers": [{"key": "X-Frame-Options", "value": "SAMEORIGIN"}]}]
    existing = {"headers": headers, "redirects": [{"source": "/old", "destination": "/old", "permanent": True}]}
    out = GR.merge_config(existing, rules)
    assert out["headers"] == headers
    assert out["redirects"] == rules


def test_merge_config_omits_headers_when_absent():
    rules = [{"source": "/x", "destination": "https://playbook.adamabdalla.com/x", "permanent": True}]
    assert GR.merge_config(None, rules) == {"redirects": rules}
    assert GR.merge_config({}, rules) == {"redirects": rules}
    assert GR.merge_config({"redirects": []}, rules) == {"redirects": rules}
