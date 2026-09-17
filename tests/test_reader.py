import sys, pathlib, io, re
import pytest
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import build_reader as R
import build as B

REPO = ROOT.parent / "ai-playbook-curriculum"

def test_reader_reads_the_four_stage_folders(tmp_path):
    n = R.run(REPO, tmp_path)
    assert n >= 100
    idx = io.open(tmp_path / "index.html", encoding="utf-8").read()
    for name in ("1 Starter", "2 Intermediate", "3 Expert", "4 Frontier Operator"):
        assert name in idx
    for n_ in (1, 2, 3, 4):
        assert (tmp_path / f"{n_}-overview.html").exists()
    assert not list(tmp_path.glob("l[1-5]-*.html")), "old level-prefixed slugs must not be generated"
    assert len(list(tmp_path.glob("3-individual-*.html"))) == 26
    assert len(list(tmp_path.glob("3-company-*.html"))) == 18

def test_reader_output_carries_no_level_numbering(tmp_path):
    R.run(REPO, tmp_path)
    bad = []
    for f in tmp_path.glob("*.html"):
        s = io.open(f, encoding="utf-8").read()
        for m in re.finditer(r"\bLevel [1-5]\b|\blevel-[1-5]-", s):
            start = s.rfind("\n", 0, m.start()) + 1
            end = s.find("\n", m.end())
            if end == -1:
                end = len(s)
            line = s[start:end]
            stripped = re.sub(r"<[^>]+>", "", line).strip()
            if not stripped.startswith("Formerly"):
                bad.append((f.name, line))
    assert not bad, bad[:5]

def test_reader_records_its_source_commit(tmp_path):
    R.run(REPO, tmp_path)
    sha = (tmp_path / "SOURCE").read_text(encoding="utf-8").strip()
    assert re.fullmatch(r"[0-9a-f]{40}", sha)

def test_run_refuses_to_delete_a_foreign_directory(tmp_path):
    keep = tmp_path / "keep.txt"
    keep.write_text("do not touch", encoding="utf-8")
    with pytest.raises(SystemExit):
        R.run(REPO, tmp_path)
    assert keep.exists()

def test_stage_pages_list_modules_without_level_words(tmp_path):
    B.render(tmp_path)
    for st in B.S.load()["stages"]:
        s = io.open(tmp_path / "curriculum" / st["slug"] / "index.html", encoding="utf-8").read()
        assert not re.search(r"Level \d", s), st["slug"]
        assert s.count("<li>") >= 8, st["slug"]
    s3 = io.open(tmp_path / "curriculum" / "3-expert" / "index.html", encoding="utf-8").read()
    assert "26-jargon-stage-3-continued" in s3
