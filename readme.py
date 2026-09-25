#!/usr/bin/env python3
"""The README published with the dataset: the numbers index.py reads, said for a reader.

`output/README.md` and its Chinese twin become the root of the `dist` branch, so they are the page
anyone lands on. It stays small on purpose: what the directory is in two lines, then how much of
the dataset is built for each angle. `just index` writes both from the same walk as the catalog, and
nothing reads them back.
"""

from pathlib import Path
from string import Template
from typing import Any

import common

README = "README.md"
README_ZH = "README.zh-CN.md"
# What the bullets under Progress say, in this order. Each name is a sentence in TEXT below and a
# `<name>_label` beside it, so the two languages cannot drift apart in structure.
FACTS = ("domain", "translate", "skill_zh", "snapshot", "catalog")

# One page per language: the same thing said in the same order. `$name` is filled from the numbers
# index.py reads; the rest is prose and markdown. The two hold the same keys - a test says so.
TEXT: dict[str, dict[str, Any]] = {
    "en": {
        "intro": "The agent skills this repository collects, each labelled with one closed-domain\n"
                 "category by the Jev endpoint and described in Chinese by a chat model, plus the\n"
                 "catalog joining it all. Written by `just index` - generated, so do not edit it.\n"
                 "中文: [README.zh-CN.md](README.zh-CN.md)",
        "where": "`skills/<id>/` is the source page every angle was built from; the full skill lives\n"
                 "in its own repository. `profiles/<id>/` holds what\n"
                 "is written about it - the domain label, the Chinese `description_zh`, and the\n"
                 "Chinese `skill_zh` page - and `skills.jsonl` is the catalog joining them.",
        "progress": "Progress",
        "bullet": "- **$label**: $value",
        "domain_label": "domain",
        "translate_label": "translate",
        "skill_zh_label": "skill_zh",
        "snapshot_label": "snapshot",
        "catalog_label": "catalog",
        "domain": "$built of $buildable labelled ($percent), covering $installs of the mirror's installs",
        "translate": "$translated of $buildable translated ($translate_percent), covering $translate_installs of the mirror's installs",
        "skill_zh": "$skillzh of $buildable skill pages translated ($skillzh_percent), covering $skillzh_installs of the mirror's installs",
        "snapshot": "`$tag`, $scan",
        "catalog": "$buildable of the mirror's $total listed skills have a description; the rest are left out of the catalog",
    },
    "zh": {
        "intro": "本仓库收集的那些 agent skills，每个由 Jev 端点标注一个封闭分类、由聊天模型给出\n"
                 "中文描述，外加把这些连起来的清单。由 `just index` 从这棵树生成——不要手改。\n"
                 "English: [README.md](README.md)",
        "where": "`skills/<id>/` 是各角度共用的构建源；完整的 skill 在它自己的仓库里。\n"
                 "`profiles/<id>/` 里是为它写的东西：domain 分类、中文 `description_zh` 和\n"
                 "中文 `skill_zh` 页面；`skills.jsonl` 是把它们连起来的清单。",
        "progress": "进度",
        "bullet": "- **$label**：$value",
        "domain_label": "domain",
        "translate_label": "translate",
        "skill_zh_label": "skill_zh",
        "snapshot_label": "快照",
        "catalog_label": "清单",
        "domain": "$buildable 个里已标 $built 个（$percent），覆盖镜像安装量的 $installs",
        "translate": "$buildable 个里已翻译 $translated 个（$translate_percent），覆盖镜像安装量的 $translate_installs",
        "skill_zh": "$buildable 个里已有 $skillzh 个中文页面（$skillzh_percent），覆盖镜像安装量的 $skillzh_installs",
        "snapshot": "`$tag`，$scan",
        "catalog": "镜像列出的 $total 个里 $buildable 个有 description；其余的不进清单",
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
    """The progress bullets: what each angle covers, and which tree they describe."""
    return [Template(text["bullet"]).substitute(
        label=text[f"{name}_label"], value=Template(text[name]).substitute(facts))
        for name in FACTS]
