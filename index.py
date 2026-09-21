#!/usr/bin/env python3
"""Index the profile tree: one flat line per skill, the mirror's own row joined with ours.

`output/skills.jsonl` is the catalog: every skill the mirror lists, carrying the description read out
of that skill's own `SKILL.md` and the domain this project labelled it with. It is what a consumer
reads instead of walking the tree - and instead of going back to the mirror's own index for the
installs, the url and the hash - and `just index` rewrites it whole.

`output/stats.txt` is the report written beside it: the same tree, said as progress - how much of the
dataset is built, angle by angle. Unlike the catalog it is prose for a reader, and it is a
projection of the tree rather than a second copy of anything: it is derived by the same walk, and
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

MIRROR = Path(gen.UPSTREAM_DIR) / gen.INDEX  # the mirror's own listing: the join's left side
# The mirror's row, forwarded field by field rather than whole, so that every row of the catalog has
# the same shape: one of a skill the mirror has dropped keeps the names with nothing in them, and a
# field upstream adds later is a decision made here rather than a surprise in the file.
MIRROR_FIELDS = ("id", "installs", "url", "hash", "fetchedAt")
STATS = "stats.txt"  # the report: the catalog's companion, and nothing that can drift from the tree


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


def snapshot_lines(config: gen.Config, indexed: list[dict], listed: int) -> list[tuple[str, str]]:
    """Which snapshot this is, and what the mirror last said about itself.

    Read off the tree and never stamped: a wall clock here would make every publish a change, and a
    publish that changes nothing is meant to spend no tag.
    """
    upstream = config.output_dir / gen.UPSTREAM_DIR
    stats = _read_json(upstream / "stats.json")
    fetched = sorted({row["fetchedAt"][:10] for row in indexed if row.get("fetchedAt")})
    scanned = ""
    if stats.get("startedAt") or stats.get("finishedAt"):
        spent = f" ({_minutes(stats['durationMs'])})" if stats.get("durationMs") else ""
        scanned = (f", scanned {_moment(stats.get('startedAt'))} -> "
                   f"{_moment(stats.get('finishedAt'))}{spent}")
    mirror = f"{listed} listed"
    if stats:
        mirror += (f", {stats.get('leaderboardTotal', '?')} on the leaderboard; "
                   f"that scan +{stats.get('added', '?')} -{stats.get('removed', '?')}, "
                   f"{stats.get('dropped', '?')} dropped")
    readable = sum(1 for row in indexed if row["description"])
    return [
        ("snapshot", f"{_read_text(upstream / 'latest').strip() or 'untagged'}{scanned}"),
        ("mirror", mirror),
        ("sources", f"{readable} of {listed} carry a readable description"
                    + (f"; fetched {fetched[0]} .. {fetched[-1]}" if fetched else "")),
    ]


def label_lines(config: gen.Config, indexed: list[dict]) -> list[tuple[str, str]]:
    """The domain labels, and how many skills wear each one first.

    The categories come off the schema, so what shows is also what nothing has been labelled with -
    which is what a balance check is for.
    """
    counted = Counter(row["domain"][0] for row in indexed
                      if isinstance(row.get("domain"), list) and row["domain"])
    schema = _read_json(config.prompts_dir / "domain.json")
    try:
        enum = [name for name in schema["properties"]["domain"]["items"]["enum"]
                if isinstance(name, str)]
    except (KeyError, TypeError):
        enum = []
    worn = sorted(counted, key=lambda name: (-counted[name], name))
    if not worn and not enum:
        return []
    spare = f" ({sum(1 for name in enum if not counted[name])} of {len(enum)} unused)" if enum else ""
    return [("labels", ", ".join(f"{name} {counted[name]}" for name in worn) + spare)]


def status(config: gen.Config, indexed: list[dict]) -> str:
    """The report: how much of the dataset is built, and what the tree it is built from holds.

    The denominator is what can be built rather than what the mirror lists - a skill whose front
    matter yields no description is never built, so counting it would pin the report below 100%
    forever. The installs share is a second reading of the same number: the batch works most
    installed first, so a count says how much is left and the weight says how much that is worth.
    """
    cells = built_cells(config)
    ids = angle_ids(config, cells)
    listed = {gen.skill_dir_name(entry.get("id", "")) for entry in mirror_rows(config)}
    orphan = [row for row in indexed if gen.skill_dir_name(row["id"]) not in listed]
    buildable = [row for row in indexed if row["description"]]
    weight = sum(_installs(row) for row in buildable)
    dirs = {row["id"]: gen.skill_dir_name(row["id"]) for row in buildable}

    table = []
    total = 0
    for angle in ids:
        here = [row for row in buildable if dirs[row["id"]] in cells.get(angle, set())]
        total += len(here)
        table.append([angle, str(len(here)), str(len(buildable)),
                      _percent(len(here), len(buildable)),
                      _percent(sum(_installs(row) for row in here), weight)])
    table.append(["total", str(total), str(len(buildable) * len(ids)),
                  _percent(total, len(buildable) * len(ids)), ""])

    whole = sum(1 for row in buildable  # `ids` empty = nothing to be complete about
                if ids and all(dirs[row["id"]] in cells.get(angle, set()) for angle in ids))
    head = snapshot_lines(config, indexed, len(indexed) - len(orphan))
    tail = label_lines(config, indexed) + [
        ("complete", f"{whole} of {len(buildable)} skills have all {len(ids)} angles"
                     f" ({_percent(whole, len(buildable))})"),
        ("orphans", f"{len(orphan)} profile directories the mirror no longer lists"),
        ("size", ", ".join(f"{what} {_size(_du(config.output_dir / directory))}"
                           for what, directory in (("profiles", gen.PROFILES_DIR),
                                                   ("skills", gen.SKILLS_DIR)))),
    ]

    width = max(len(name) for name, _ in head + tail)
    lines = [f"{name.ljust(width)}  {value}" for name, value in head]
    lines += ["", *_table(["angle", "built", "of", "built%", "installs%"], table), ""]
    lines += [f"{name.ljust(width)}  {value}" for name, value in tail]
    return "\n".join(["skills-profiles: generation status", "", *lines]) + "\n"


def write_stats(config: gen.Config, text: str) -> Path:
    """Write the report, renamed into place for the catalog's own reason."""
    path = config.output_dir / STATS
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name + ".part")
    partial.write_text(text, encoding="utf-8")
    partial.replace(path)
    return path


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


def _table(headers: list[str], rows: list[list[str]]) -> list[str]:
    """Fixed-width columns, the names left and the numbers right."""
    widths = [max(len(headers[i]), *(len(row[i]) for row in rows)) for i in range(len(headers))]

    def render(cells: list[str]) -> str:
        return "  ".join(cell.ljust(widths[i]) if i == 0 else cell.rjust(widths[i])
                         for i, cell in enumerate(cells)).rstrip()

    return [render(headers)] + [render(row) for row in rows]


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
        description="Write output/skills.jsonl and output/stats.txt from the tree."
    ).parse_args(argv)
    config = gen.Config()
    indexed = rows(config)
    path = write(config, indexed)
    report = write_stats(config, status(config, indexed))
    print(f"indexed {len(indexed)} skills -> {path}", file=sys.stderr)
    print(f"status -> {report}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
