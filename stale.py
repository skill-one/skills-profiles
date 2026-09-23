#!/usr/bin/env python3
"""Retire the labels a new snapshot invalidates: those whose source content hash changed.

`just refresh` is the only caller. It keeps the catalog of the tree it is about to replace, syncs,
and hands that copy here; comparing it with the catalog the sync rewrote names every skill whose
`SKILL.md` upstream has since changed - the label of those was built from text that is no longer
there, so it is deleted and the next batch rebuilds it.

A skill that vanished from the mirror keeps its label: it was paid for, and nothing is left to
rebuild it from. One hash covers a whole directory, because the one angle comes from one source.
"""

import argparse
import json
import shutil
import sys
from pathlib import Path

import jev

INDEX = jev.INDEX  # the catalog: two copies of it, before and after a sync, are the whole input


def hashes(path: Path) -> dict[str, str]:
    """`id -> content hash` from a catalog; a skill whose hash cannot be read is left out."""
    entries = (json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line)
    return {entry["id"]: entry["hash"] for entry in entries if entry.get("hash")}


def changed(before: dict[str, str], after: dict[str, str]) -> list[str]:
    """The ids both indexes hold whose hash differs, in path order."""
    return sorted(sid for sid, digest in before.items() if sid in after and after[sid] != digest)


def retire(config: jev.Config, ids: list[str]) -> list[str]:
    """Delete those skills' profiles; returns the ones that had any, in path order."""
    dropped = []
    for sid in ids:
        directory = jev.profile_dir(config, sid)
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

    config = jev.Config()
    after = config.output_dir / INDEX
    # a first sync has nothing to compare, and a sync that never completed has nothing to say
    if not args.before.is_file() or not after.is_file():
        print("no previous index - nothing to retire", file=sys.stderr)
        return 0

    ids = changed(hashes(args.before), hashes(after))
    retired = retire(config, ids)
    if retired:
        print("\n".join(retired))
    print(f"retired {len(retired)} profile(s) for {len(ids)} skill(s) whose source changed",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
