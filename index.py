#!/usr/bin/env python3
"""Index the profile tree: one flat line per skill, the mirror's own row joined with ours.

`output/skills.jsonl` is the catalog: every skill the mirror lists, carrying the description read out
of that skill's own `SKILL.md` and the domain this project labelled it with. It is what a consumer
reads instead of walking the tree - and instead of going back to the mirror's own index for the
installs, the url and the hash - and `just index` rewrites it whole.

Driven by the justfile - DEVELOPING.md describes the interface it is half of.
"""

import argparse
import json
import os
import sys
from pathlib import Path

import gen

MIRROR = Path(gen.UPSTREAM_DIR) / gen.INDEX  # the mirror's own listing: the join's left side
# The mirror's row, forwarded field by field rather than whole, so that every row of the catalog has
# the same shape: one of a skill the mirror has dropped keeps the names with nothing in them, and a
# field upstream adds later is a decision made here rather than a surprise in the file.
MIRROR_FIELDS = ("id", "installs", "url", "hash", "fetchedAt")


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


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(
        description="Write output/skills.jsonl from the mirror's rows and the built profiles."
    ).parse_args(argv)
    config = gen.Config()
    indexed = rows(config)
    path = write(config, indexed)
    print(f"indexed {len(indexed)} skills -> {path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
