#!/usr/bin/env python3
"""The README published with the dataset: the numbers index.py reads, said for a reader.

`output/README.md` and its Chinese twin become the root of the `dist` branch, so they are the page
anyone lands on. It stays small on purpose: what the directory is in two lines, then how much of
the dataset is built for each angle. `just index` writes both from the same walk as the catalog, and
nothing reads them back.
"""

from __future__ import annotations

from pathlib import Path

import common

README = "README.md"
README_ZH = "README.zh-CN.md"
# What the bullets under Progress say, in this order. Each name is a sentence in TEXT below and a
# `<name>_label` beside it, so the two languages cannot drift apart in structure.
FACTS = ("domain", "skill_zh", "catalog")

# One page per language: the same thing said in the same order. `{{ name }}` is filled from the
# numbers index.py reads; the rest is prose and markdown. The two hold the same keys - a test says
# so, and an unknown name fails loudly (strict undefineds).
TEXT: dict[str, dict[str, str]] = {
    "en": {
        "intro": "The agent skills this repository collects, each labelled with one closed-domain\n"
                 "category by the Jev endpoint and described in Chinese by a chat model, plus the\n"
                 "catalog joining it all. Written by `just index` - generated, so do not edit it.\n"
                 "中文: [README.zh-CN.md](README.zh-CN.md)",
        "where": "`skills/<id>/` holds the skill's own `SKILL.md` with what was written about it -\n"
                 "the domain label and the Chinese `SKILL.zh.md` page, whose front matter carries\n"
                 "the Chinese description - and `skills.jsonl` is the catalog joining them. Beside\n"
                 "the skills, `repos.jsonl` holds each repository's GitHub profile, and\n"
                 "`owners/<owner>.png` each owner's avatar.",
        "progress": "Progress",
        "bullet": "- **{{ label }}**: {{ value }}",
        "domain_label": "domain",
        "skill_zh_label": "skill_zh",
        "catalog_label": "catalog",
        "domain": "{{ built }} of {{ total }} labelled ({{ percent }}), covering {{ installs }} of the mirror's installs",
        "skill_zh": "{{ skillzh }} of {{ total }} skill pages translated ({{ skillzh_percent }}), covering {{ skillzh_installs }} of the mirror's installs",
        "catalog": "the catalog lists all {{ total }} of the mirror's skills; {{ described }} carry a description, the rest are null until fetched",
    },
    "zh": {
        "intro": "本仓库收集的那些 agent skills，每个由 Jev 端点标注一个封闭分类、由聊天模型给出\n"
                 "中文描述，外加把这些连起来的清单。由 `just index` 从这棵树生成——不要手改。\n"
                 "English: [README.md](README.md)",
        "where": "`skills/<id>/` 里是 skill 自己的 `SKILL.md` 和为它写的东西：domain 分类与\n"
                 "中文 `SKILL.zh.md` 页面（front matter 里带中文 description）；\n"
                 "`skills.jsonl` 是把它们连起来的清单。skills 旁边，`repos.jsonl` 存每个仓库的 GitHub 资料，\n"
                 "每个 owner 的头像在 `owners/<owner>.png`。",
        "progress": "进度",
        "bullet": "- **{{ label }}**：{{ value }}",
        "domain_label": "domain",
        "skill_zh_label": "skill_zh",
        "catalog_label": "清单",
        "domain": "{{ total }} 个里已标 {{ built }} 个（{{ percent }}），覆盖镜像安装量的 {{ installs }}",
        "skill_zh": "{{ total }} 个里已有 {{ skillzh }} 个中文页面（{{ skillzh_percent }}），覆盖镜像安装量的 {{ skillzh_installs }}",
        "catalog": "清单列出镜像全部 {{ total }} 个 skill；{{ described }} 个已有 description，其余在拉取前为 null",
    },
}


def page(facts: dict, lang: str) -> str:
    """One README, in one language."""
    text = TEXT[lang]
    lines = [
        "# skills-profiles",
        "",
        text["intro"],
        "",
        text["where"],
        "",
        f"## {text['progress']}",
        "",
        *_facts(facts, text),
        "",
    ]
    return "\n".join(lines)


def write(config: common.Config, facts: dict) -> list[Path]:
    """Write both pages, each renamed into place for the catalog's own reason."""
    written = []
    for name, lang in ((README, "en"), (README_ZH, "zh")):
        path = config.output_dir / name
        common.write_atomic(path, page(facts, lang))
        written.append(path)
    return written


def _facts(facts: dict, text: dict) -> list[str]:
    """The progress bullets: what each angle covers, and which tree they describe. Rendered by the
    same strict renderer the producers use, so an unknown name fails instead of printing itself."""
    return [common.render(text["bullet"], label=text[f"{name}_label"],
                          value=common.render(text[name], **facts))
            for name in FACTS]
