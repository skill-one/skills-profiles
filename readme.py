#!/usr/bin/env python3
"""The README published with the dataset: the numbers index.py reads, said for a reader.

`output/README.md` and its Chinese twin become the root of the `dist` branch, so they are the page
anyone lands on. It stays small on purpose: what the directory is in two lines, then how much of the
dataset is built. `just index` writes both from the same walk as the catalog, and nothing reads them
back.

Generated, and whole or absent like everything else here. No wall clock: the same tree writes the
same bytes, so a publish with nothing new to say spends no version number.
"""

from pathlib import Path
from string import Template
from typing import Any

import gen

README = "README.md"
README_ZH = "README.zh-CN.md"
# What the table cannot say about the tree it came from, in this order. Each name is a sentence in
# TEXT below and a `<name>_label` beside it, so the two languages cannot drift apart in structure.
FACTS = ("snapshot", "buildable")

# One page per language: the same thing said in the same order, which is the only way a translation
# stays one. `$name` is filled from the numbers index.py reads; the rest is prose and markdown. The
# two hold the same keys - a test says so - since the renderer reads them by name.
TEXT: dict[str, dict[str, Any]] = {
    "en": {
        "intro": "The agent skills this repository collects, each profiled from six angles, plus the\n"
                 "catalog joining the two. Written by `just index` - generated, so do not edit it.\n"
                 "中文: [README.zh-CN.md](README.zh-CN.md)",
        "where": "`skills/<id>/` is the skill as published: copy one into a skills folder and it is\n"
                 "installed. `profiles/<id>/` is what was written about it, and `skills.jsonl` is the\n"
                 "catalog of both.",
        "progress": "Progress",
        "columns": ("angle", "built", "of", "built%", "installs%"),
        "total": "total",
        "bullet": "- **$label**: $value",
        "snapshot_label": "snapshot",
        "buildable_label": "buildable",
        "snapshot": "`$tag`, $scan",
        "buildable": "$buildable of $listed have a readable description; the rest are never built",
    },
    "zh": {
        "intro": "本仓库收集的那些 agent skills，每个写了六个角度的档案，外加把两者连起来的清单。\n"
                 "由 `just index` 从这棵树生成——不要手改。\n"
                 "English: [README.md](README.md)",
        "where": "`skills/<id>/` 是发布的 skill 原件：拷进 skills 目录就等于装上了。\n"
                 "`profiles/<id>/` 是为它写的内容，`skills.jsonl` 是这两者的清单。",
        "progress": "进度",
        "columns": ("角度", "已建", "可建", "建成%", "安装量%"),
        "total": "合计",
        "bullet": "- **$label**：$value",
        "snapshot_label": "快照",
        "buildable_label": "可建",
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
        *_angle_table(facts, text),
        "",
        *_facts(facts, text),
        "",
    ]
    return "\n".join(lines)


def write(config: gen.Config, facts: dict) -> list[Path]:
    """Write both pages, each renamed into place for the catalog's own reason."""
    written = []
    for name, lang in ((README, "en"), (README_ZH, "zh")):
        path = config.output_dir / name
        partial = path.with_name(path.name + ".part")
        partial.write_text(page(facts, lang), encoding="utf-8")
        partial.replace(path)
        written.append(path)
    return written


def _angle_table(facts: dict, text: dict) -> list[str]:
    """The angles as a markdown table: a row each, and the whole dataset under them."""
    names = text["columns"]
    rows = ["| " + " | ".join(names) + " |",
            "| " + " | ".join(["---"] + ["---:"] * (len(names) - 1)) + " |"]
    for angle in facts["angles"]:
        cells = (f"`{angle['angle']}`", str(angle["built"]), str(angle["of"]),
                 angle["percent"], angle["installs"])
        rows.append("| " + " | ".join(cells) + " |")
    rows.append("| " + " | ".join((f"**{text['total']}**", facts["cells_built"], facts["cells"],
                                   facts["cells_percent"], "")) + " |")
    return rows


def _facts(facts: dict, text: dict) -> list[str]:
    """The lines under the table: what the table does not say about the tree it came from."""
    return [Template(text["bullet"]).substitute(
        label=text[f"{name}_label"], value=Template(text[name]).substitute(facts))
        for name in FACTS]
