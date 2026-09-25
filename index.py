#!/usr/bin/env python3
"""Index the profile tree: one flat line per skill, the mirror's own row joined with both angles.

`output/skills.jsonl` is the catalog: every skill the mirror lists that has a description of its
own - the rest are not in it, there is nothing to lead a build with - carrying the description
read out of that skill's own `SKILL.md`, its Chinese translation, the domain Jev labelled it
with, and how sure the endpoint was of it. It is what a consumer reads instead of walking the
tree - and instead of going back to the mirror's own index for the installs and the hash - and
`just index` rewrites it whole.

The same run writes the README that goes with it, out of the same walk: the numbers here, said for
a reader by `readme.py`.
"""

import argparse
import json
import os
import sys
from pathlib import Path

import common
import readme
from common import Config

MIRROR = Path(common.UPSTREAM_DIR) / common.INDEX  # the mirror's own listing: the join's left side
# The mirror's row, forwarded field by field rather than whole, so that every row of the catalog
# has the same shape and a field upstream adds later is a decision made here rather than a surprise.
MIRROR_FIELDS = ("id", "installs", "hash", "fetchedAt")
NOTHING = "—"  # an em dash: what the README shows where the tree cannot answer


def mirror_rows(config: Config) -> list[dict]:
    """The mirror's own rows, in its own order - installs, descending."""
    path = config.output_dir / MIRROR
    if not path.is_file():
        raise SystemExit(f"{path}: not found - run `just sync` first")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def description(config: Config, skill: str) -> str:
    """The skill's own one line, out of its `SKILL.md`; empty when there is none to read."""
    try:
        return common.skill_description(common.skill_source(config, skill))
    except FileNotFoundError:
        return ""


def angle_output(config: Config, skill: str, angle: str) -> dict:
    """One angle's json for one skill, or nothing while it has not been built."""
    path = common.profile_path(config, skill, angle)
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def rows(config: Config) -> list[dict]:
    """One row per skill the mirror lists whose own `SKILL.md` yields a description: the mirror's
    row, plus what this project read and decided about it.

    A skill without a description is not in the catalog at all - there is nothing to lead a build
    with, so no row and no batch work. The joined fields are `null` while unknown.
    """
    out = []
    for entry in mirror_rows(config):
        row = _row(entry, config, common.skill_dir_name(entry.get("id", "")))
        if row["description"]:
            out.append(row)
    return out


def _row(entry: dict, config: Config, skill: str) -> dict:
    """The mirror's row plus ours: the description, its Chinese translation, and the label with
    its confidence.

    Only the two of the label the catalog is asked for. The rest of what Jev wrote stays in the
    profile, where it is the answer.
    """
    row = {name: entry.get(name) for name in MIRROR_FIELDS}
    row["description"] = description(config, skill) or None
    row[common.TRANSLATE_ANGLE] = angle_output(
        config, skill, common.TRANSLATE_ANGLE).get(common.TRANSLATE_ANGLE)
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
    """The skills whose angle file of that name is on disk, from one walk of the profile tree."""
    root = config.output_dir / common.PROFILES_DIR
    built: set[str] = set()
    for dirpath, _, filenames in os.walk(root):
        path = Path(dirpath)
        if len(path.relative_to(root).parts) == 3 and filename in filenames:
            built.add(path.relative_to(root).as_posix())
    return built


def facts(config: Config, indexed: list[dict]) -> dict:
    """What the README says: how much of the dataset is built for each angle, and the tree the
    numbers come from.

    The denominator is the catalog itself: every row in it has a description, and the skills the
    mirror lists without one are in neither the catalog nor these numbers. The installs share is a
    second reading of the same count: the batch works the most installed skills first, so the
    count says how much is left and the weight says what it is worth. Everything here is a string,
    ready to be dropped into a sentence.
    """
    weight = sum(_installs(row) for row in indexed)
    dirs = {row["id"]: common.skill_dir_name(row["id"]) for row in indexed}
    domain_done = built_skills(config, f"{common.DOMAIN_ANGLE}.json")
    translate_done = built_skills(config, f"{common.TRANSLATE_ANGLE}.json")
    skill_zh_done = built_skills(config, f"{common.SKILL_ZH_ANGLE}.md")
    domain_here = [row for row in indexed if dirs[row["id"]] in domain_done]
    translate_here = [row for row in indexed if dirs[row["id"]] in translate_done]
    skill_zh_here = [row for row in indexed if dirs[row["id"]] in skill_zh_done]
    return {
        "tag": _read_text(config.output_dir / common.UPSTREAM_DIR / "latest").strip() or NOTHING,
        "scan": _scan(_read_json(config.output_dir / common.UPSTREAM_DIR / "stats.json")),
        "total": str(len(mirror_rows(config))),
        "buildable": str(len(indexed)),
        "built": str(len(domain_here)),
        "percent": _percent(len(domain_here), len(indexed)),
        "installs": _percent(sum(_installs(row) for row in domain_here), weight),
        "translated": str(len(translate_here)),
        "translate_percent": _percent(len(translate_here), len(indexed)),
        "translate_installs": _percent(sum(_installs(row) for row in translate_here), weight),
        "skillzh": str(len(skill_zh_here)),
        "skillzh_percent": _percent(len(skill_zh_here), len(indexed)),
        "skillzh_installs": _percent(sum(_installs(row) for row in skill_zh_here), weight),
    }


def _scan(scan: dict) -> str:
    """The mirror's own scan as one range: `2026-09-19T19:42:24Z -> ... (30m07s)`."""
    if not scan.get("startedAt") and not scan.get("finishedAt"):
        return NOTHING
    spent = f" ({_minutes(scan['durationMs'])})" if scan.get("durationMs") else ""
    return f"{_moment(scan.get('startedAt'))} -> {_moment(scan.get('finishedAt'))}{spent}"


def _installs(row: dict) -> int:
    """A row's installs as a number: the mirror writes them as strings and as numbers."""
    try:
        return int(row.get("installs") or 0)
    except (TypeError, ValueError):
        return 0


def _percent(part: int, whole: int) -> str:
    return f"{part / whole:.1%}" if whole else "-"


def _moment(value: object) -> str:
    """`2026-09-14T21:40:59.596Z` as `2026-09-14T21:40:59Z`: milliseconds are noise in prose."""
    text = str(value or "?")
    return text.split(".")[0] + "Z" if "." in text else text


def _minutes(millis: float) -> str:
    """A millisecond duration as `29m06s`, or `30s` under a minute."""
    seconds = int(millis) // 1000
    return f"{seconds}s" if seconds < 60 else f"{seconds // 60}m{seconds % 60:02d}s"


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _read_json(path: Path) -> dict:
    try:
        loaded = json.loads(_read_text(path))
    except ValueError:
        return {}
    return loaded if isinstance(loaded, dict) else {}


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(
        description="Write output/skills.jsonl and the READMEs beside it from the tree."
    ).parse_args(argv)
    config = Config()
    indexed = rows(config)
    path = write(config, indexed)
    written = readme.write(config, facts(config, indexed))
    print(f"indexed {len(indexed)} skills -> {path}", file=sys.stderr)
    print(f"readme -> {', '.join(str(page) for page in written)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
