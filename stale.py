#!/usr/bin/env python3
"""Retire the profiles a new snapshot invalidates: those whose source content hash changed.

`just refresh` is the only caller. It keeps the index of the snapshot it is about to replace,
syncs, and hands that index here; comparing it with the one the new snapshot brought names every
skill whose `SKILL.md` upstream has since changed - the profiles of those were built from text that
is no longer there, so they are deleted and the next batch rebuilds them.

A skill that vanished from the index keeps its profiles: they were paid for, and nothing is left to
rebuild them from. One hash covers a whole directory, because all six angles come from one source.
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

import gen

INDEX = "skills.jsonl"  # the snapshot's own listing, at the root of the unpacked branch


def hashes(path: Path) -> dict[str, str]:
    """`id -> content hash` from a snapshot index; a skill with no hash saved is left out."""
    entries = (json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line)
    return {entry["id"]: entry["hash"] for entry in entries if entry.get("hash")}


def changed(before: dict[str, str], after: dict[str, str]) -> list[str]:
    """The ids both indexes hold whose hash differs, in path order."""
    return sorted(sid for sid, digest in before.items() if sid in after and after[sid] != digest)


def retire(config: gen.Config, ids: list[str]) -> list[str]:
    """Delete those skills' profiles; returns the ones that had any, in path order."""
    dropped = []
    for sid in ids:
        directory = gen.skill_dir(config, sid)
        if directory.is_dir():
            shutil.rmtree(directory)
            dropped.append(sid)
    return dropped


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Delete the profiles whose source changed between two snapshot indexes.")
    parser.add_argument("before", type=Path,
                        help="the index of the snapshot that was just replaced")
    args = parser.parse_args(argv)

    config = gen.Config()
    after = config.data_dir / INDEX
    # a first sync has nothing to compare, and a sync that never completed has nothing to say
    if not args.before.is_file() or not after.is_file():
        print("no previous index - nothing to retire", file=sys.stderr)
        return 0

    retired = retire(config, changed(hashes(args.before), hashes(after)))
    if retired:
        print("\n".join(retired))
    print(f"retired {len(retired)} skill(s) whose source changed", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
