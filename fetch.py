#!/usr/bin/env python3
"""Unpack a window's repository tarballs: every skill's SKILL.md, from its own repository.

`batch.py` downloads the window's repositories - one codeload tarball each, and only the ones not
already on disk - and this module streams each tarball once. A skill is a `SKILL.md` in a
subdirectory of the repository, named after that directory; the repository's own root `SKILL.md` is
its readme, not a skill, and is left out. Only a source that can say what the skill is for is taken
(one without a description can never be built), and a slug already taken is skipped - one directory,
one skill. The repository directory is created either way, so its presence on disk is the cache: a
repository is downloaded once. The catalog is not read here - what is listed is `index.py`'s
question, not this one's.
"""

import tarfile
from pathlib import Path

import common
from common import Config


def extract(stage: Path, config: Config) -> tuple[int, int]:
    """Write every skill's SKILL.md into place; returns the skills taken and the repositories
    processed. A skill is a `SKILL.md` under a subdirectory, named after that directory; the
    repository's own root `SKILL.md` (its readme) is not one. A source with no description is
    skipped, and a slug already taken is left alone - the first source for a name wins. The
    repository directory is created either way: it is the cache, and a repository on disk is never
    fetched again."""
    skills = 0
    repos = 0
    for tarball in sorted(stage.glob("*.tgz")):
        owner, _, repo = tarball.stem.partition("_")
        repo_dir = config.output_dir / common.SKILLS_DIR / owner / repo
        repo_dir.mkdir(parents=True, exist_ok=True)
        taken: set[str] = set()
        with tarfile.open(tarball, "r:gz") as tar:
            for member in tar:
                if not member.isfile() or not member.name.endswith(f"/{common.SKILL_MD}"):
                    continue
                parts = member.name.rsplit("/", 2)
                if len(parts) != 3:
                    continue  # <root>/SKILL.md, the repository's readme rather than a skill
                slug = common.skill_dir_name(parts[1])
                if slug in taken:
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
        repos += 1
    return skills, repos
