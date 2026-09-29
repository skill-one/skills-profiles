#!/usr/bin/env python3
"""Index the profile tree: one flat line per skill, the mirror's own row joined with both angles.

`output/skills.jsonl` is the catalog: one row per skill the mirror lists and the tree can still
build, in the mirror's order - the mirror's own `id` and `installs`, then the description read out
of that skill's own `SKILL.md`, its Chinese translation, the domain Jev labelled it with, and how
sure the endpoint was of it. The joined fields are `null` until the skill is fetched and built, so
the catalog is both the dataset and the batch's order - a skill the tree has not reached yet is a
row with `null`s, not a missing row. A listed skill whose repository is already on disk without a
readable description is no row at all: the fetch took the repository and yielded nothing, so no
run can ever build it. It is what a consumer reads instead of walking the tree, and the only place
the mirror's listing survives.

The same run writes the README that goes with it, out of the same walk: the numbers here, said for
a reader by `readme.py`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import common
import readme
from common import Config

# The mirror's row, forwarded field by field rather than whole, so that every row of the catalog
# has the same shape and a field upstream adds later is a decision made here rather than a surprise.
MIRROR_FIELDS = ("id", "installs")


def mirror_rows(config: Config, listing: Path | None) -> list[dict]:
    """The mirror's own rows, in its own order - installs, descending.

    A fresh listing the driver's refresh hands to `build()` is the left side; the offline CLI
    passes none and falls back to the catalog itself: its rows carry `installs` already, in the
    same order, so the numbers and the order survive.
    """
    if listing is not None:
        if not listing.is_file():
            raise SystemExit(f"{listing}: not found - run `just sync` first")
        return common.read_jsonl(listing)
    path = config.output_dir / common.INDEX
    if not path.is_file():
        raise SystemExit(f"{path}: not found - run `just sync` first")
    return [{"id": row["id"], "installs": row.get("installs")}
            for row in common.read_jsonl(path) if isinstance(row.get("id"), str)]


def angle_output(config: Config, skill: str, angle: str) -> dict:
    """One angle's json for one skill, or nothing while it has not been built."""
    path = common.angle_path(config, skill, angle)
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def zh_description(config: Config, skill: str) -> str:
    """The Chinese description out of the zh page's own front matter - there is no second file
    holding it; empty while the page has not been built."""
    path = common.angle_path(config, skill, common.SKILL_ZH_ANGLE)
    if not path.is_file():
        return ""
    return common.skill_description(path.read_text(encoding="utf-8", errors="replace"))


def rows(config: Config, listing: Path | None = None) -> list[dict]:
    """One row per skill the mirror lists and the tree can still build, in the mirror's order: the
    mirror's row, plus what this project has read and decided about it so far.

    Every listed skill is a row, fetched or not - the batch walks the catalog to know what to build
    next, so a skill the tree has not reached is a row whose joined fields are `null` rather than a
    missing row. A skill whose repository is on disk without a readable description, though, is a
    skill no run can ever build - the fetch took the repository and yielded nothing to lead with -
    so it is no row at all, and the mirror's dead rows do not dilute the dataset.
    """
    kept: list[dict] = []
    dropped = 0
    for entry in mirror_rows(config, listing):
        skill = common.skill_dir_name(entry.get("id", ""))
        if sourceless(config, skill):
            dropped += 1
            continue
        kept.append(_row(entry, config, skill))
    if dropped:
        print(f"dropped {dropped} listed skill(s) with no readable source on disk", file=sys.stderr)
    return kept


def sourceless(config: Config, skill: str) -> bool:
    """True when the repository is on disk without a description to build from: the repository was
    fetched and will not be again, so no run can ever produce the skill's angles."""
    if not (config.output_dir / common.SKILLS_DIR / Path(skill).parent).is_dir():
        return False  # not fetched yet - the batch may still reach it
    try:
        source = common.skill_md(config, skill)
    except FileNotFoundError:
        return True
    return not common.skill_description(source)


def _row(entry: dict, config: Config, skill: str) -> dict:
    """The mirror's row plus ours: the source's description, its Chinese translation, and the label
    with its confidence - each `null` while the tree has not produced it.

    A skill not yet fetched is a row of `null`s, which is exactly how a reader tells a fetched row
    from an unfetched one. The catalog takes two of the label's fields; the rest of what Jev wrote
    stays in the profile.
    """
    row = {name: entry.get(name) for name in MIRROR_FIELDS}
    try:
        source = common.skill_md(config, skill)
    except FileNotFoundError:
        row["description"] = None
    else:
        row["description"] = common.skill_description(source) or None
    row["description_zh"] = zh_description(config, skill) or None
    label = angle_output(config, skill, common.DOMAIN_ANGLE)
    row["domain"] = label.get("domain")
    row["confidence"] = label.get("confidence")
    return row


def write(config: Config, rows: list[dict]) -> Path:
    """Write the catalog, renamed into place: a half-written one would read as a whole one.

    Compact, like the mirror's own listing.
    """
    text = "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
                   for row in rows)
    return common.write_atomic(config.output_dir / common.INDEX, text)


def built_skills(config: Config, filename: str) -> set[str]:
    """The skills whose angle file of that name is on disk, from one walk of the skills tree."""
    root = config.output_dir / common.SKILLS_DIR
    return {path.parent.relative_to(root).as_posix() for path in root.rglob(filename)
            if len(path.relative_to(root).parts) == 4}


def facts(config: Config, indexed: list[dict]) -> dict:
    """What the README says: how much of the dataset is built for each angle, and the tree the
    numbers come from.

    The denominator is the mirror's own listing: every listed skill is a row, so the counts say how
    much of the whole dataset is done rather than how much of the tree happens to be fetched. The
    installs share is a second reading of the same count: the batch works the most installed skills
    first, so the count says how much is left and the weight says what it is worth. Everything here
    is a string, ready to be dropped into a sentence.
    """
    total = len(indexed)
    weight = sum(_installs(row) for row in indexed)
    dirs = {row["id"]: common.skill_dir_name(row["id"]) for row in indexed}
    domain_done = built_skills(config, common.ANGLE_FILES[common.DOMAIN_ANGLE])
    skill_zh_done = built_skills(config, common.ANGLE_FILES[common.SKILL_ZH_ANGLE])
    domain_here = [row for row in indexed if dirs[row["id"]] in domain_done]
    skill_zh_here = [row for row in indexed if dirs[row["id"]] in skill_zh_done]
    return {
        "total": str(total),
        "described": str(sum(1 for row in indexed if row["description"])),
        "built": str(len(domain_here)),
        "percent": _percent(len(domain_here), total),
        "installs": _percent(sum(_installs(row) for row in domain_here), weight),
        "skillzh": str(len(skill_zh_here)),
        "skillzh_percent": _percent(len(skill_zh_here), total),
        "skillzh_installs": _percent(sum(_installs(row) for row in skill_zh_here), weight),
    }


def _installs(row: dict) -> int:
    """A row's installs as a number: the listing writes them as strings and as numbers."""
    try:
        return int(row.get("installs") or 0)
    except (TypeError, ValueError):
        return 0


def _percent(part: int, whole: int) -> str:
    return f"{part / whole:.1%}" if whole else "-"


def build(config: Config, listing: Path | None) -> tuple[Path, list[Path]]:
    """The whole verb: the catalog and the two READMEs from one walk of one tree. `batch.py`'s
    refresh calls this in-process after it merges the new sources."""
    indexed = rows(config, listing)
    return write(config, indexed), readme.write(config, facts(config, indexed))


def main(argv: list[str] | None = None) -> int:
    """The offline verb: rebuild the catalog and the READMEs from the tree alone. The fresh
    listing is `batch.py sync`'s path - it calls `build()` in-process with it."""
    argparse.ArgumentParser(
        description="Write output/skills.jsonl and the READMEs beside it from the tree.").parse_args(
        argv)
    config = Config()
    path, written = build(config, None)
    print(f"indexed -> {path}", file=sys.stderr)
    print(f"readme -> {', '.join(str(page) for page in written)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
