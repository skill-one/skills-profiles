#!/usr/bin/env python3
"""Unpack repository tarballs: every skill's SKILL.md, from its own repository.

`batch.py` downloads the repositories a batch needs - one codeload tarball each, on demand by the
first job that touches one, and only the ones not already on disk - and this module streams each
tarball once. A skill is a `SKILL.md` in a subdirectory of the repository, and it lands under the
directory it sat in, unchanged - the tree keeps each skill's own spelling, and which listing row
a directory belongs to is decided by matching the front matter `name`, the field the mirror
publishes for every skill. A repository whose only `SKILL.md` sits at the root is itself one
skill: its source stays at the root. A root `SKILL.md` beside subdirectory skills stays the
repository's readme, not a skill. Only a source that can say what the skill is for is taken (one
without a description can never be built), and a directory already taken is skipped - one
directory, one skill. The repository directory is created either way, so its presence on disk is
the cache: a repository is downloaded once. The catalog is not read here - what is listed and
where it lives is `index.py`'s question, not this one's.
"""

from __future__ import annotations

import tarfile
from pathlib import Path

import common
from common import Config

INVALID_SLUGS = {"", ".", ".."}


def extract(stage: Path, config: Config) -> tuple[int, int]:
    """Write every skill's SKILL.md into place; returns the skills taken and the repositories
    processed. A skill is a `SKILL.md` under a subdirectory; a repository with no skill in a
    subdirectory is itself one skill, its root `SKILL.md` the source. A source with no
    description is skipped, and a directory already taken is left alone - the first source for a
    directory wins. The repository directory is created either way: it is the cache, and a
    repository on disk is never fetched again."""
    tarballs = sorted(stage.glob("*.tgz"))
    return sum(extract_tarball(tarball, config) for tarball in tarballs), len(tarballs)


def extract_tarball(tarball: Path, config: Config) -> int:
    """One repository tarball unpacked: the skills taken from it, on the same rules as `extract`."""
    owner, _, repo = tarball.stem.partition("_")
    repo_dir = config.output_dir / common.SKILLS_DIR / owner / repo
    repo_dir.mkdir(parents=True, exist_ok=True)
    taken: set[str] = set()
    skills = 0
    readme: str | None = None
    with tarfile.open(tarball, "r:gz") as tar:
        for member in tar:
            if not member.isfile() or not member.name.endswith(f"/{common.SKILL_MD}"):
                continue
            parts = member.name.rsplit("/", 2)
            if len(parts) != 3:
                source = tar.extractfile(member)
                readme = source.read().decode("utf-8", errors="replace") if source else None
                continue  # <root>/SKILL.md, held back for the single-skill repository below
            slug = parts[1]
            # a slug that is not a name under the repository - `..`, say - would write outside it
            if slug in taken or slug in INVALID_SLUGS:
                continue
            source = tar.extractfile(member)
            if source is None:
                continue
            text = source.read().decode("utf-8", errors="replace")
            if not common.skill_description(text):
                continue
            common.write_atomic(repo_dir / slug / common.SKILL_MD, text)
            taken.add(slug)
            skills += 1
    # no skill in a subdirectory, but the root SKILL.md can say what it is for: the repository is
    # itself one skill, its source kept at the root where it sat
    if not skills and readme and common.skill_description(readme):
        if not (repo_dir / common.SKILL_MD).is_file():
            common.write_atomic(repo_dir / common.SKILL_MD, readme)
            skills += 1
    return skills
