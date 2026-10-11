import pathlib
import time

from skills.cli import parse_frontmatter, validate, watch


def test_validate_requires_description(tmp_path):
    skill = tmp_path / "demo"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        "---\nname: demo\n---\n\n# Demo\n"
    )
    bad = validate(tmp_path)
    assert [why for _, why in bad] == ["missing required key: description"]


def test_validate_ok(tmp_path):
    skill = tmp_path / "demo"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        "---\nname: demo\ndescription: A demo skill.\n---\n\n# Demo\n"
    )
    assert validate(tmp_path) == []


def test_validate_rejects_missing_frontmatter(tmp_path):
    skill = tmp_path / "demo"
    skill.mkdir()
    (skill / "SKILL.md").write_text("# no frontmatter\n")
    assert validate(tmp_path) == [(skill, "no frontmatter block")]


def test_parse_frontmatter(tmp_path):
    skill = tmp_path / "demo"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        "---\nname: demo\ndescription: d.\n---\nbody\n"
    )
    assert parse_frontmatter((skill / "SKILL.md").read_text()) == {
        "name": "demo",
        "description": "d."
    }

def test_watch_reports_change(tmp_path, monkeypatch, capsys):
    skill = tmp_path / "demo"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        "---\nname: demo\ndescription: d.\n---\nbody\n"
    )
    monkeypatch.setenv("XDG_RUNTIME_DIR", str(tmp_path / "no-bus"))

    import threading

    def mutate():
        time.sleep(0.3)
        (skill / "SKILL.md").write_text(
            "---\nname: demo\ndescription: d2.\n---\nbody\n"
        )

    t = threading.Thread(target=mutate)
    t.start()
    rc = watch(tmp_path, interval=0.2, iterations=4)
    t.join()
    out = capsys.readouterr().out
    assert rc == 0
    assert "changed:" in out
