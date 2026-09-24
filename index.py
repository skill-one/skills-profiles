#!/usr/bin/env python3
"""Index the profile tree: one flat line per skill, the mirror's own row joined with both angles.

`output/skills.jsonl` is the catalog: every skill the mirror lists, carrying the description read
out of that skill's own `SKILL.md`, its Chinese translation, the domain Jev labelled it with, and
how sure the endpoint was of it. It is what a consumer reads instead of walking the tree - and
instead of going back to the mirror's own index for the installs, the url and the hash - and
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
MIRROR_FIELDS = ("id", "installs", "url", "hash", "fetchedAt")
NOTHING = "—"  # an em dash: what the README shows where the tree cannot answer


def mirror_rows(config: Config) -> list[dict]:
    """The mirror's own rows, in its own order - installs, descending."""
    path = config.output_dir / MIRROR
    if not path.is_file():
        raise SystemExit(f"{path}: not found - run `just sync` first")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def skill_ids(config: Config) -> list[str]:
    """Every skill the profile tree holds, in path order.

    A skill the mirror has since dropped is still a population: its profile was paid for, and a
    catalog that left it out would hide work that is on disk. The walk is an `os.walk` rather than
    a glob - a glob drops a leading dot, and `.claude` is a repo name people use.
    """
    root = config.output_dir / common.PROFILES_DIR
    ids = []
    for dirpath, dirnames, _ in os.walk(root):
        path = Path(dirpath)
        if len(path.relative_to(root).parts) == 3:
            dirnames[:] = []  # a skill directory is the leaf
            ids.append(path.relative_to(root).as_posix())
    return sorted(ids)


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
    """One row per skill: the mirror's row, plus what this project read and decided about it.

    The joined fields are `null` while unknown. A skill the mirror no longer lists is a row too,
    named the way the tree spells it, with the mirror's fields left empty.
    """
    out = []
    listed = set()
    for entry in mirror_rows(config):
        skill = common.skill_dir_name(entry.get("id", ""))
        listed.add(skill)
        out.append(_row(entry, config, skill))
    for skill in skill_ids(config):
        if skill not in listed:
            out.append(_row({"id": skill}, config, skill))
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

    Compact, like the mirror's own listing: the justfile matches the `"description":null` spelling
    in it to keep an undescribable skill out of the window.
    """
    text = "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
                   for row in rows)
    return common.write_atomic(config.output_dir / common.INDEX, text)


def built_skills(config: Config) -> set[str]:
    """The skills whose domain.json is on disk, from one walk of the profile tree."""
    root = config.output_dir / common.PROFILES_DIR
    built: set[str] = set()
    for dirpath, _, filenames in os.walk(root):
        path = Path(dirpath)
        if len(path.relative_to(root).parts) == 3 and f"{common.DOMAIN_ANGLE}.json" in filenames:
            built.add(path.relative_to(root).as_posix())
    return built


def facts(config: Config, indexed: list[dict]) -> dict:
    """What the README says: how much of the dataset is labelled, and the tree the numbers come
    from.

    The denominator is what can be labelled rather than what the mirror lists - a skill whose front
    matter yields no description is never built, so counting it would pin the number below 100%
    forever. The installs share is a second reading of the same count: the batch works the most
    installed skills first, so the count says how much is left and the weight says what it is
    worth. Everything here is a string, ready to be dropped into a sentence.
    """
    on_mirror = {common.skill_dir_name(entry.get("id", "")) for entry in mirror_rows(config)}
    orphan = sum(1 for row in indexed if common.skill_dir_name(row["id"]) not in on_mirror)
    buildable = [row for row in indexed if row["description"]]
    weight = sum(_installs(row) for row in buildable)
    dirs = {row["id"]: common.skill_dir_name(row["id"]) for row in buildable}
    done = built_skills(config)

    here = [row for row in buildable if dirs[row["id"]] in done]
    return {
        "tag": _read_text(config.output_dir / common.UPSTREAM_DIR / "latest").strip() or NOTHING,
        "scan": _scan(_read_json(config.output_dir / common.UPSTREAM_DIR / "stats.json")),
        "listed": str(len(indexed) - orphan),
        "buildable": str(len(buildable)),
        "built": str(len(here)),
        "percent": _percent(len(here), len(buildable)),
        "installs": _percent(sum(_installs(row) for row in here), weight),
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
