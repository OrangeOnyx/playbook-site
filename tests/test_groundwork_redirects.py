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


def test_rules_are_permanent_by_default():
    sp = S.load()
    cfg = GR.build(sp)
    for r in cfg["redirects"]:
        assert r["permanent"] is True


def test_permanent_false_makes_every_rule_temporary():
    # Step 1 of the retirement publishes 307s, which nothing caches permanently, so the
    # flip can be walked and undone before it is promoted to 308.
    sp = S.load()
    cfg = GR.build(sp, permanent=False)
    assert cfg["redirects"]
    for r in cfg["redirects"]:
        assert r["permanent"] is False


def test_permanent_flag_parses_true_false_and_defaults_to_true():
    assert GR.parse_args([]).permanent == "true"
    assert GR.parse_args(["--permanent", "false"]).permanent == "false"
    assert GR.parse_args(["--permanent", "true"]).permanent == "true"
    with pytest.raises(SystemExit):
        GR.parse_args(["--permanent", "maybe"])


def test_check_rules_lists_every_literal_pair_and_no_catch_all():
    sp = S.load()
    rules = GR.build(sp)["redirects"]
    checks = GR.check_rules(rules)
    assert checks, "expected at least one literal rule"
    assert len(checks) == len([r for r in rules if "(.*)" not in r["source"]])
    for c in checks:
        assert set(c) == {"source", "destination"}
        assert "(.*)" not in c["source"] and "$1" not in c["destination"]
        assert c["destination"].startswith(sp["domain"])


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
