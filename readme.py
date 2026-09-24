#!/usr/bin/env python3
"""The README published with the dataset: the numbers index.py reads, said for a reader.

`output/README.md` and its Chinese twin become the root of the `dist` branch, so they are the page
anyone lands on. It stays small on purpose: what the directory is in two lines, then how much of
the dataset is labelled. `just index` writes both from the same walk as the catalog, and nothing
reads them back.
"""

from pathlib import Path
from string import Template
from typing import Any

import common

README = "README.md"
README_ZH = "README.zh-CN.md"
# What the bullets under Progress say, in this order. Each name is a sentence in TEXT below and a
# `<name>_label` beside it, so the two languages cannot drift apart in structure.
FACTS = ("domain", "snapshot", "buildable")

# One page per language: the same thing said in the same order. `$name` is filled from the numbers
# index.py reads; the rest is prose and markdown. The two hold the same keys - a test says so.
TEXT: dict[str, dict[str, Any]] = {
    "en": {
        "intro": "The agent skills this repository collects, each labelled with one closed-domain\n"
                 "category by the Jev endpoint and described in Chinese by a chat model, plus the\n"
                 "catalog joining it all. Written by `just index` - generated, so do not edit it.\n"
                 "中文: [README.zh-CN.md](README.zh-CN.md)",
        "where": "`skills/<id>/` is the skill as published: copy one into a skills folder and it is\n"
                 "installed. `profiles/<id>/` holds what is written about it - the domain label and\n"
                 "the Chinese `description_zh` - and `skills.jsonl` is the catalog joining them.",
        "progress": "Progress",
        "bullet": "- **$label**: $value",
        "domain_label": "domain",
        "snapshot_label": "snapshot",
        "buildable_label": "buildable",
        "domain": "$built of $buildable labelled ($percent), covering $installs of the mirror's installs",
        "snapshot": "`$tag`, $scan",
        "buildable": "$buildable of $listed have a readable description; the rest are never built",
    },
    "zh": {
        "intro": "本仓库收集的那些 agent skills，每个由 Jev 端点标注一个封闭分类、由聊天模型给出\n"
                 "中文描述，外加把这些连起来的清单。由 `just index` 从这棵树生成——不要手改。\n"
                 "English: [README.md](README.md)",
        "where": "`skills/<id>/` 是发布的 skill 原件：拷进 skills 目录就等于装上了。\n"
                 "`profiles/<id>/` 里是为它写的东西：domain 分类和中文 `description_zh`；"
                 "`skills.jsonl` 是把它们连起来的清单。",
        "progress": "进度",
        "bullet": "- **$label**：$value",
        "domain_label": "domain",
        "snapshot_label": "快照",
        "buildable_label": "可建",
        "domain": "$buildable 个里已标 $built 个（$percent），覆盖镜像安装量的 $installs",
        "snapshot": "`$tag`，$scan",
        "buildable": "$listed 个里有 $buildable 个可读出 description；其余的永远不会被构建",
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
    """The progress bullets: what the labels cover, and which tree they describe."""
    return [Template(text["bullet"]).substitute(
        label=text[f"{name}_label"], value=Template(text[name]).substitute(facts))
        for name in FACTS]
