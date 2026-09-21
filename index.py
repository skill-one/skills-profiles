#!/usr/bin/env python3
"""Index the profile tree: one flat line per skill, the mirror's own row joined with ours.

`output/skills.jsonl` is the catalog: every skill the mirror lists, carrying the description read out
of that skill's own `SKILL.md`, the domain this project labelled it with, and how sure the endpoint
was of it. It is what a consumer reads instead of walking the tree - and instead of going back to the
mirror's own index for the installs, the url and the hash - and `just index` rewrites it whole.

The same run writes the README that goes with it, out of the same walk: the numbers here, said for a
reader by `readme.py`. That is the half of the catalog's own question the catalog cannot answer - how
much of the dataset is built - and it is a projection of the tree like everything else here, so
every number in it changes only because the tree did.

Driven by the justfile - DEVELOPING.md describes the interface it is half of.
"""

import argparse
import json
import os
import sys
from pathlib import Path

import gen
import jev
import readme

MIRROR = Path(gen.UPSTREAM_DIR) / gen.INDEX  # the mirror's own listing: the join's left side
# The mirror's row, forwarded field by field rather than whole, so that every row of the catalog has
# the same shape: one of a skill the mirror has dropped keeps the names with nothing in them, and a
# field upstream adds later is a decision made here rather than a surprise in the file.
MIRROR_FIELDS = ("id", "installs", "url", "hash", "fetchedAt")
NOTHING = "\u2014"  # an em dash: what the README shows where the tree cannot answer


def mirror_rows(config: gen.Config) -> list[dict]:
    """The mirror's own rows, in its own order - installs, descending.

    The catalog is built on these rather than on the tree: they are the dataset's definition, their
    order is the order a batch works in, and they are where installs, the url and the content hash
    come from - none of which the tree can know.
    """
    path = config.output_dir / MIRROR
    if not path.is_file():
        raise SystemExit(f"{path}: not found - run `just sync` first")
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def skill_ids(config: gen.Config) -> list[str]:
    """Every skill the profile tree holds, in path order.

    Read as a second population rather than as the listing: a skill the mirror has since dropped
    still has profiles, and a catalog that left them out would hide work that is on disk. The walk is
    an `os.walk` rather than a glob for the justfile's own reason - a glob drops a leading dot, and
    `.claude` is a repo name people use.
    """
    root = config.output_dir / gen.PROFILES_DIR
    ids = []
    for dirpath, dirnames, _ in os.walk(root):
        path = Path(dirpath)
        if len(path.relative_to(root).parts) == 3:
            dirnames[:] = []  # a skill directory is the leaf
            ids.append(path.relative_to(root).as_posix())
    return sorted(ids)


def description(config: gen.Config, skill: str) -> str:
    """The skill's own one line, out of its `SKILL.md`; empty when there is none to read."""
    try:
        return gen.skill_description(gen.skill_source(config, skill))
    except FileNotFoundError:
        return ""


def labelled(config: gen.Config, skill: str) -> dict:
    """The domain angle's answer for one skill, or nothing while it has not been built.

    The profile writes what `jev.py` answered - one category, its confidence, and the distribution
    it was read off. Two of those three belong in a catalog row, and they are taken by name rather
    than forwarded whole, so the row says what a consumer can use and nothing else.
    """
    path = gen.json_path(config, "domain", skill)
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def rows(config: gen.Config) -> list[dict]:
    """One row per skill: the mirror's row, plus what this project read and decided about it.

    `description` and `domain` are `null` while they are unknown - a header nothing can be read from,
    and a profile not built yet - which is also how a consumer asks for the finished part of the
    dataset: `.domain != null`.

    A skill the mirror no longer lists is a row too, named the way the tree spells it, with the
    fields the mirror can no longer supply left empty: its profiles were paid for.
    """
    out = []
    listed = set()
    for entry in mirror_rows(config):
        skill = gen.skill_dir_name(entry.get("id", ""))
        listed.add(skill)
        out.append(_row(entry, config, skill))
    for skill in skill_ids(config):
        if skill not in listed:
            out.append(_row({"id": skill}, config, skill))
    return out


def _row(entry: dict, config: gen.Config, skill: str) -> dict:
    """The mirror's row plus ours: the description, and the label with the endpoint's confidence.

    Only the two of the label the catalog is asked for. `domain` stays one member of the enum so a
    row filters on it directly, and `confidence` is the number to sort by when the question is which
    labels to look at - the rest of what `jev.py` wrote stays in the profile, where it is the answer.
    """
    row = {name: entry.get(name) for name in MIRROR_FIELDS}
    row["description"] = description(config, skill) or None
    label = labelled(config, skill)
    row["domain"] = label.get("domain")
    row["confidence"] = label.get("confidence")
    return row


def write(config: gen.Config, rows: list[dict]) -> Path:
    """Write the catalog, renamed into place: a half-written one would read as a whole one.

    Compact, like the mirror's own listing: a row is a machine's line, and the justfile matches the
    `"description":null` spelling in it to keep an undescribable skill out of the window.
    """
    path = config.output_dir / gen.INDEX
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name + ".part")
    partial.write_text("".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
                               for row in rows), encoding="utf-8")
    partial.replace(path)
    return path


def built_cells(config: gen.Config) -> dict[str, set[str]]:
    """`angle -> the skills whose profile for it is on disk`, from one walk of the profile tree.

    The json is the unit of work - existence is the whole cache - so the empty directories a
    `just invalidate` leaves behind are counted as nothing.
    """
    root = config.output_dir / gen.PROFILES_DIR
    cells: dict[str, set[str]] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        path = Path(dirpath)
        if len(path.relative_to(root).parts) != 3:
            continue
        dirnames[:] = []  # a skill directory is the leaf
        skill = path.relative_to(root).as_posix()
        for name in filenames:
            if name.endswith(".json"):
                cells.setdefault(name.removesuffix(".json"), set()).add(skill)
    return cells


def angle_ids(config: gen.Config, cells: dict[str, set[str]]) -> list[str]:
    """The angles: a prompt schema for gen.py, a question list in jev.py for the rest.

    Read from the two producers rather than from the profiles a tree happens to hold, so an angle
    with nothing built yet still has a row. A tree with neither falls back to what is on disk, so
    the report describes the profiles there are rather than nothing.
    """
    angles = {path.stem for path in config.prompts_dir.glob("*.json")} | set(jev.QUESTIONS)
    return sorted(angles or cells)


def facts(config: gen.Config, indexed: list[dict]) -> dict:
    """What the README says: how much of the dataset is built, and the tree the numbers come from.

    The denominator is what can be built rather than what the mirror lists - a skill whose front
    matter yields no description is never built, so counting it would pin the number below 100%
    forever. The installs share is a second reading of the same count: the batch works the most
    installed skills first, so the count says how much is left and the weight says what it is worth.

    Everything here is a string, ready to be dropped into a sentence: `readme.py` holds the
    sentences, and one em dash is what a tree that cannot answer shows.
    """
    cells = built_cells(config)
    ids = angle_ids(config, cells)
    on_mirror = {gen.skill_dir_name(entry.get("id", "")) for entry in mirror_rows(config)}
    orphan = sum(1 for row in indexed if gen.skill_dir_name(row["id"]) not in on_mirror)
    buildable = [row for row in indexed if row["description"]]
    weight = sum(_installs(row) for row in buildable)
    dirs = {row["id"]: gen.skill_dir_name(row["id"]) for row in buildable}

    angles = []
    built = 0
    for angle in ids:
        here = [row for row in buildable if dirs[row["id"]] in cells.get(angle, set())]
        built += len(here)
        angles.append({"angle": angle, "built": len(here), "of": len(buildable),
                       "percent": _percent(len(here), len(buildable)),
                       "installs": _percent(sum(_installs(row) for row in here), weight)})
    return {
        "tag": _read_text(config.output_dir / gen.UPSTREAM_DIR / "latest").strip() or NOTHING,
        "scan": _scan(_read_json(config.output_dir / gen.UPSTREAM_DIR / "stats.json")),
        "listed": str(len(indexed) - orphan),
        "buildable": str(len(buildable)),
        "angles": angles,
        "count": str(len(ids)),
        "cells": str(len(buildable) * len(ids)),
        "cells_built": str(built),
        "cells_percent": _percent(built, len(buildable) * len(ids)),
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
    config = gen.Config()
    indexed = rows(config)
    path = write(config, indexed)
    written = readme.write(config, facts(config, indexed))
    print(f"indexed {len(indexed)} skills -> {path}", file=sys.stderr)
    print(f"readme -> {', '.join(str(page) for page in written)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
