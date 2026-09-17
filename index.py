#!/usr/bin/env python3
"""Index the profile tree: one flat line per skill over its `domain`.

`output/skills.jsonl` is the tree's listing in one file, for the consumer that wants to filter
or show the category that labels a skill without walking it. It is derived, not a second
contract: the tree stays the only one, and `just index` regenerates it.

Driven by the justfile - DEVELOPING.md describes the interface it is half of.
"""

import argparse
import json
import os
import sys
from pathlib import Path

import gen

INDEX = "skills.jsonl"


def skill_ids(config: gen.Config) -> list[str]:
    """Every skill the output tree holds, in path order.

    The tree is the source rather than the snapshot: a skill's directory is named with its
    id (`:` and `&` spelled `_`, which is the spelling the batch is handed too), so a walk of
    it lists exactly what was built and needs nothing fetched first. The walk is an `os.walk`
    rather than a glob for the justfile's own reason - a glob drops a leading dot, and
    `.claude` is a repo name people use.
    """
    root = config.output_dir / gen.SKILLS_DIR
    ids = []
    for dirpath, dirnames, _ in os.walk(root):
        path = Path(dirpath)
        if len(path.relative_to(root).parts) == 3:
            dirnames[:] = []  # a skill directory is the leaf
            ids.append(path.relative_to(root).as_posix())
    return sorted(ids)


def rows(config: gen.Config) -> list[dict]:
    """One flat row per skill whose domain has been built.

    A skill without one is left out: an empty line would only restate the tree it was read
    from, and this is a listing of what is there rather than of what is not.
    """
    out = []
    for skill in skill_ids(config):
        path = gen.json_path(config, "domain", skill)
        if not path.is_file():
            continue
        domain = json.loads(path.read_text(encoding="utf-8"))
        out.append({"id": skill, "domain": domain.get("domain"), "reason": domain.get("reason")})
    return out


def write(config: gen.Config, rows: list[dict]) -> Path:
    """Write the index, renamed into place: a half-written one would read as a whole one."""
    path = config.output_dir / INDEX
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(path.name + ".part")
    partial.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
                       encoding="utf-8")
    partial.replace(path)
    return path


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(
        description="Write output/skills.jsonl from the built domains.").parse_args(argv)
    config = gen.Config()
    indexed = rows(config)
    path = write(config, indexed)
    print(f"indexed {len(indexed)} skills -> {path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
