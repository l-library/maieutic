from pathlib import Path

import yaml

SKILL_DIR = Path(__file__).resolve().parent / "skills"


def _read_front_matter(path: Path) -> str:
    """读取指定文件的 front_matter，空表示读取失败"""
    assert path.is_file()
    with path.open(encoding="utf-8-sig") as f:
        first = f.readline()
        if first.strip() != "---":
            return ""
        buf: list[str] = []
        for line in f:
            if line.strip() == "---":
                return "".join(buf)
            buf.append(line)
    return ""


def _yaml_to_dict(y):
    """递归解析 yaml 为 dict"""
    for i, j in y.items():
        if isinstance(j, dict):
            _yaml_to_dict(j)
        else:
            yield i, j


def get_skills_prompt():
    """找到目标目录下所有符合规范的skill，注册并注入提示词"""
    path = SKILL_DIR
    prompt = "<available_skills>"
    for skill_file in path.rglob("SKILL.md"):
        if skill_file.is_file():
            front_matter = _read_front_matter(skill_file)
            fm_yaml = yaml.safe_load(front_matter)
            name = None
            for key, value in _yaml_to_dict(fm_yaml):
                if key == "name":
                    name = value
                elif key == "description" and name is not None:
                    prompt += f"<skill><name>{name}</name><description>{value}</description><location>{skill_file.parent}</location></skill>"
    return prompt + "</available_skills>"
