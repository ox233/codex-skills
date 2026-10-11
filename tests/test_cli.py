import pathlib

from skills.cli import parse_frontmatter, validate


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