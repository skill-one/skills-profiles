#!/usr/bin/env python3
"""Index the profile tree: one flat line per skill, the mirror's own row joined with ours.

`output/skills.jsonl` is the catalog: every skill the mirror lists, carrying the description read out
of that skill's own `SKILL.md` and the domain this project labelled it with. It is what a consumer
reads instead of walking the tree - and instead of going back to the mirror's own index for the
installs, the url and the hash - and `just index` rewrites it whole.

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
from collections import Counter
from pathlib import Path

import gen
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
    """The domain angle's answer for one skill, or nothing while it has not been built."""
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
    row = {name: entry.get(name) for name in MIRROR_FIELDS}
    row["description"] = description(config, skill) or None
    domain = labelled(config, skill)
    row["domain"] = domain.get("domain")
    row["reason"] = domain.get("reason")
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
    """The angles, which are the prompt schemas: what a profile is built from.

    A tree without prompts falls back to the angles that are on disk, so the report describes the
    profiles there are rather than nothing.
    """
    return sorted(path.stem for path in config.prompts_dir.glob("*.json")) or sorted(cells)


def facts(config: gen.Config, indexed: list[dict]) -> dict:
    """What the README says: how much of the dataset is built, and the tree the number comes from.

    The denominator is what can be built rather than what the mirror lists - a skill whose front
    matter yields no description is never built, so counting it would pin the number below 100%
    forever. The installs share is a second reading of the same count: the batch works the most
    installed skills first, so the count says how much is left and the weight says what it is worth.

    Everything here is a string, ready to be dropped into a sentence: `readme.py` holds the
    sentences, and one em dash is what a tree that cannot answer shows.
    """
    cells = built_cells(config)
    ids = angle_ids(config, cells)
    listed = {gen.skill_dir_name(entry.get("id", "")) for entry in mirror_rows(config)}
    buildable = [row for row in indexed if row["description"]]
    orphan = [row for row in indexed if gen.skill_dir_name(row["id"]) not in listed]
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
    whole = sum(1 for row in buildable  # `ids` empty = nothing to be complete about
                if ids and all(dirs[row["id"]] in cells.get(angle, set()) for angle in ids))

    upstream = config.output_dir / gen.UPSTREAM_DIR
    scan = _read_json(upstream / "stats.json")
    counted = Counter(row["domain"][0] for row in indexed
                      if isinstance(row.get("domain"), list) and row["domain"])
    categories = _categories(config)
    worn = sorted(counted, key=lambda name: (-counted[name], name))
    return {
        "tag": _read_text(upstream / "latest").strip() or NOTHING,
        "scan": _scan(scan),
        "listed": str(len(indexed) - len(orphan)),
        "board": _number(scan.get("leaderboardTotal")),
        "added": _number(scan.get("added")),
        "removed": _number(scan.get("removed")),
        "dropped": _number(scan.get("dropped")),
        "buildable": str(len(buildable)),
        "fetched": _fetched(indexed),
        "angle_names": " · ".join(f"`{name}`" for name in ids) or NOTHING,
        "angles": angles,
        "count": str(len(ids)),
        "cells": str(len(buildable) * len(ids)),
        "cells_built": str(built),
        "cells_percent": _percent(built, len(buildable) * len(ids)),
        "whole": str(whole),
        "whole_percent": _percent(whole, len(buildable)),
        "orphans": str(len(orphan)),
        "labels_text": ", ".join(f"{name} {counted[name]}" for name in worn) or NOTHING,
        "categories": str(len(categories)) if categories else NOTHING,
        "unused": str(sum(1 for name in categories if not counted[name])) if categories else NOTHING,
        "profiles_size": _size(_du(config.output_dir / gen.PROFILES_DIR)),
        "skills_size": _size(_du(config.output_dir / gen.SKILLS_DIR)),
    }


def _scan(scan: dict) -> str:
    """The mirror's own scan as one range: `2026-09-19T19:42:24Z -> ... (30m07s)`."""
    if not scan.get("startedAt") and not scan.get("finishedAt"):
        return NOTHING
    spent = f" ({_minutes(scan['durationMs'])})" if scan.get("durationMs") else ""
    return f"{_moment(scan.get('startedAt'))} -> {_moment(scan.get('finishedAt'))}{spent}"


def _fetched(indexed: list[dict]) -> str:
    """The days the sources were gathered on, as the range they span."""
    days = sorted({row["fetchedAt"][:10] for row in indexed if row.get("fetchedAt")})
    if not days:
        return NOTHING
    return days[0] if days[0] == days[-1] else f"{days[0]} .. {days[-1]}"


def _number(value: object) -> str:
    return NOTHING if value is None else str(value)


def _categories(config: gen.Config) -> list[str]:
    """The domain angle's closed set, off its schema: what the balance check is against."""
    schema = _read_json(config.prompts_dir / "domain.json")
    try:
        return [name for name in schema["properties"]["domain"]["items"]["enum"]
                if isinstance(name, str)]
    except (KeyError, TypeError):
        return []


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


def _size(count: float) -> str:
    """A byte count as one short string."""
    for unit in ("B", "KB", "MB", "GB"):
        if count < 1024:
            return f"{count:.0f} B" if unit == "B" else f"{count:.1f} {unit}"
        count /= 1024
    return f"{count:.1f} GB"


def _du(path: Path) -> int:
    """The bytes under a directory; a missing one is nothing."""
    total = 0
    stack = [str(path)]
    while stack:
        try:
            entries = list(os.scandir(stack.pop()))
        except OSError:
            continue
        for entry in entries:
            try:
                if entry.is_dir(follow_symlinks=False):
                    stack.append(entry.path)
                else:
                    total += entry.stat().st_size
            except OSError:
                continue
    return total


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
