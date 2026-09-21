#!/usr/bin/env python3
"""The README published with the dataset: the numbers index.py reads, said for a reader.

`output/README.md` and its Chinese twin are the front page of the published root - the page a reader
lands on - so they carry what the directory is as well as how far the batch has got. `just index`
writes both from the same walk as the catalog, and nothing reads them back.

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
FACTS = ("snapshot", "mirror", "sources", "complete", "labels", "orphans", "size")

# One page per language: the same thing said in the same order, which is the only way a translation
# stays one. `$name` is filled from the numbers index.py reads; the rest is prose and markdown. The
# two hold the same keys - a test says so - since the renderer reads them by name.
TEXT: dict[str, dict[str, Any]] = {
    "en": {
        "intro": "The published dataset: the [agent skills](https://www.skills.sh) that "
                 "[skill-one/skills-sh-mirror](https://github.com/skill-one/skills-sh-mirror) "
                 "collects,\neach profiled from six angles. 中文: [README.zh-CN.md](README.zh-CN.md)",
        "generated": "Written by `just index` from this tree - generated, so the next run "
                     "overwrites it.",
        "where": "| where | is |\n"
                 "| --- | --- |\n"
                 "| `skills/<id>/` | the mirror's own skill directory, complete and unchanged: "
                 "copy one into a skills folder and it is installed |\n"
                 "| `profiles/<id>/` | what this project wrote about it - one json per angle, and "
                 "`md/` to read them |\n"
                 "| `upstream/` | the rest of the mirror: its own index, repos, owners, avatars |\n"
                 "| `skills.jsonl` | the catalog: one flat line per skill, and the way in to "
                 "everything above |",
        "angles": "`<id>` is `{owner}/{repo}/{slug}`. The angles are $angle_names: `domain` is one "
                  "to three English tags, the primary first, and the rest are Chinese.",
        "progress": "Progress",
        "columns": ("angle", "built", "of", "built%", "installs%"),
        "total": "total",
        "note": "`built` is what the batch has written and `of` what it can write - a skill whose "
                "own front matter yields no description is never built, so it is not in the "
                "denominator. `installs%` weighs the same count by installs, which is the number "
                "that says something this early: the batch works the most installed skills first, "
                "so the count says how much is left and the weight says what it is worth.",
        "reading": "Reading it",
        "query_skill": "what a skill is, what it is worth, and what it was labelled",
        "query_profile": "everything written about one of them",
        "bullet": "- **$label**: $value",
        "snapshot_label": "snapshot",
        "mirror_label": "mirror",
        "sources_label": "sources",
        "complete_label": "complete",
        "labels_label": "labels",
        "orphans_label": "orphans",
        "size_label": "size",
        "snapshot": "`$tag`, $scan",
        "mirror": "$listed listed, $board on the leaderboard; that scan +$added -$removed, "
                  "$dropped dropped",
        "sources": "$buildable of $listed carry a readable description; fetched $fetched",
        "complete": "$whole of $buildable skills have all $count angles ($whole_percent)",
        "labels": "$labels_text ($unused of $categories unused)",
        "orphans": "$orphans profile directories the mirror no longer lists",
        "size": "profiles $profiles_size, skills $skills_size",
    },
    "zh": {
        "intro": "已发布的数据集："
                 "[skill-one/skills-sh-mirror](https://github.com/skill-one/skills-sh-mirror) 收集的 "
                 "[agent skills](https://www.skills.sh)，每个都写了六个角度的档案。"
                 "English: [README.md](README.md)",
        "generated": "本文件由 `just index` 从这棵树生成——下一次运行会覆盖它。",
        "where": "| 路径 | 是什么 |\n"
                 "| --- | --- |\n"
                 "| `skills/<id>/` | 镜像自己的 skill 目录，完整未改：拷进 skills 目录就等于装上了 |\n"
                 "| `profiles/<id>/` | 本项目为它写的内容——每个角度一个 json，`md/` 是同内容的可读版 |\n"
                 "| `upstream/` | 镜像的其余部分：它自己的索引、repos、owners、avatars |\n"
                 "| `skills.jsonl` | 清单：每个 skill 一行、扁平，也是进入上面一切的入口 |",
        "angles": "`<id>` 即 `{owner}/{repo}/{slug}`。角度有 $angle_names："
                  "`domain` 是一到三个英文标签、主分类在前，其余五个都是中文。",
        "progress": "进度",
        "columns": ("角度", "已建", "可建", "建成%", "安装量%"),
        "total": "合计",
        "note": "`已建` 是批次已经写出的格数，`可建` 是它能写的格数——front matter 读不出 description "
                "的 skill 永远不会被构建，所以它不在分母里。`安装量%` 是把同一个计数按安装量加权后的"
                "读数，在这个阶段才说明问题：批次按安装量从高到低做，所以计数说的是还剩多少，加权说的"
                "是那份值多少。",
        "reading": "怎么用",
        "query_skill": "一个 skill 是什么、值多少、被归到哪一类",
        "query_profile": "关于它写下的全部内容",
        "bullet": "- **$label**：$value",
        "snapshot_label": "快照",
        "mirror_label": "镜像",
        "sources_label": "来源",
        "complete_label": "完整",
        "labels_label": "标签",
        "orphans_label": "孤儿",
        "size_label": "体积",
        "snapshot": "`$tag`，$scan",
        "mirror": "列出 $listed 个，榜单 $board 个；该次扫描 +$added -$removed，丢弃 $dropped 个",
        "sources": "$listed 个里有 $buildable 个可读出 description；抓取于 $fetched",
        "complete": "$buildable 个 skill 里有 $whole 个凑齐了全部 $count 个角度（$whole_percent）",
        "labels": "$labels_text（$categories 类里有 $unused 类未被使用）",
        "orphans": "$orphans 个档案目录已被镜像下架",
        "size": "profiles $profiles_size，skills $skills_size",
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
        text["generated"],
        "",
        text["where"],
        "",
        Template(text["angles"]).substitute(facts),
        "",
        f"## {text['progress']}",
        "",
        *_angle_table(facts, text),
        "",
        text["note"],
        "",
        *_facts(facts, text),
        "",
        f"## {text['reading']}",
        "",
        "```bash",
        f"# {text['query_skill']}",
        """jq -r '[.id, .installs, (.domain[0] // "-")] | @tsv' skills.jsonl | head""",
        "",
        f"# {text['query_profile']}",
        "cat profiles/mattpocock/skills/grill-me/domain.json",
        "```",
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
    head = "| " + " | ".join(names) + " |"
    rule = "| " + " | ".join(["---"] + ["---:"] * (len(names) - 1)) + " |"
    rows = [head, rule]
    for angle in facts["angles"]:
        cells = (f"`{angle['angle']}`", str(angle["built"]), str(angle["of"]),
                 angle["percent"], angle["installs"])
        rows.append("| " + " | ".join(cells) + " |")
    cells = (f"**{text['total']}**", facts["cells_built"], facts["cells"], facts["cells_percent"], "")
    rows.append("| " + " | ".join(cells) + " |")
    return rows


def _facts(facts: dict, text: dict) -> list[str]:
    """The lines under the table: what the table does not say about the tree it came from."""
    return [Template(text["bullet"]).substitute(
        label=text[f"{name}_label"], value=Template(text[name]).substitute(facts))
        for name in FACTS]
