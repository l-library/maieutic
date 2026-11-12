from pathlib import Path

import pytest

from app.agent import skills


@pytest.fixture
def skill_dir(tmp_path, monkeypatch) -> Path:
    """把 SKILL_DIR 指向临时目录，测试不依赖也不污染真实的 skills/"""
    monkeypatch.setattr(skills, "SKILL_DIR", tmp_path)
    return tmp_path


def _write_skill(root: Path, dir_name: str, text: str, encoding="utf-8") -> Path:
    d = root / dir_name
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text(text, encoding=encoding)
    return d


GOOD = """---
name: demo
description: a demo skill
---

# demo

正文不参与提示词生成
"""


# _read_front_matter
def test_front_matter_extracted(tmp_path):
    p = tmp_path / "SKILL.md"
    p.write_text(GOOD, encoding="utf-8")
    assert skills._read_front_matter(p) == "name: demo\ndescription: a demo skill\n"


def test_front_matter_empty_when_no_delimiter(tmp_path):
    p = tmp_path / "SKILL.md"
    p.write_text("name: demo\n", encoding="utf-8")
    assert skills._read_front_matter(p) == ""


def test_front_matter_empty_when_unclosed(tmp_path):
    p = tmp_path / "SKILL.md"
    p.write_text("---\nname: demo\n", encoding="utf-8")
    assert skills._read_front_matter(p) == ""


def test_front_matter_tolerates_bom(tmp_path):
    p = tmp_path / "SKILL.md"
    p.write_text(GOOD, encoding="utf-8-sig")
    assert "name: demo" in skills._read_front_matter(p)


# get_skills_prompt
def test_no_skill_returns_empty_container(skill_dir):
    assert skills.get_skills_prompt() == "<available_skills></available_skills>"


def test_skill_name_description_and_location(skill_dir):
    d = _write_skill(skill_dir, "demo", GOOD)
    out = skills.get_skills_prompt()
    assert "<name>demo</name>" in out
    assert "<description>a demo skill</description>" in out
    assert f"<location>{d}</location>" in out
    assert out.startswith("<available_skills>") and out.endswith("</available_skills>")


def test_body_not_leaked_into_prompt(skill_dir):
    _write_skill(skill_dir, "demo", GOOD)
    assert "正文不参与提示词生成" not in skills.get_skills_prompt()


@pytest.mark.parametrize(
    "text",
    [
        pytest.param("", id="empty_file"),
        pytest.param("只有正文，没有 front matter\n", id="no_front_matter"),
        pytest.param("---\n---\n", id="empty_front_matter"),
        pytest.param("---\njust a scalar\n---\n", id="front_matter_not_mapping"),
        pytest.param("---\nname: [unclosed\n---\n", id="invalid_yaml"),
    ],
)
def test_broken_skill_is_skipped_not_fatal(skill_dir, text):
    """坏文件不能让整个系统提示词生成失败"""
    _write_skill(skill_dir, "broken", text)
    assert skills.get_skills_prompt() == "<available_skills></available_skills>"


def test_nested_fields_are_parsed(skill_dir):
    text = """---
metadata:
  name: nested
  description: from nested block
---
"""
    _write_skill(skill_dir, "nested", text)
    out = skills.get_skills_prompt()
    assert "<name>nested</name>" in out
    assert "<description>from nested block</description>" in out


def test_skill_without_description_is_skipped(skill_dir):
    """缺 description 的 skill 不完整，不进提示词"""
    _write_skill(skill_dir, "half", "---\nname: half\n---\n")
    assert skills.get_skills_prompt() == "<available_skills></available_skills>"


def test_nested_directories_are_scanned(skill_dir):
    _write_skill(skill_dir / "group", "inner", GOOD)
    out = skills.get_skills_prompt()
    assert "<name>demo</name>" in out
    assert str(skill_dir / "group" / "inner") in out


def test_only_skill_md_is_registered(skill_dir):
    d = _write_skill(skill_dir, "demo", GOOD)
    (d / "NOTES.md").write_text("---\nname: notaskill\n---\n", encoding="utf-8")
    out = skills.get_skills_prompt()
    assert "<name>notaskill</name>" not in out
    assert out.count("<skill>") == 1


def test_multiple_skills_all_listed(skill_dir):
    _write_skill(skill_dir, "a", "---\nname: a\ndescription: da\n---\n")
    _write_skill(skill_dir, "b", "---\nname: b\ndescription: db\n---\n")
    out = skills.get_skills_prompt()
    assert "<name>a</name>" in out and "<name>b</name>" in out


def test_real_skill_dir_does_not_crash():
    """真实 skills/ 目录即使为空或有问题也不该抛异常"""
    assert skills.get_skills_prompt().startswith("<available_skills>")
