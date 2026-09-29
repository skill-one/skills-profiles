#!/usr/bin/env python3
"""Unpack repository tarballs: every skill's SKILL.md, from its own repository.

`batch.py` downloads the repositories a batch needs - one codeload tarball each, on demand by the
first job that touches one, and only the ones not already on disk - and this module streams each
tarball once. A skill is a `SKILL.md` in a
subdirectory of the repository, named after that directory; the repository's own root `SKILL.md` is
its readme, not a skill, and is left out. Only a source that can say what the skill is for is taken
(one without a description can never be built), and a slug already taken is skipped - one directory,
one skill. The repository directory is created either way, so its presence on disk is the cache: a
repository is downloaded once. The catalog is not read here - what is listed is `index.py`'s
question, not this one's.

The mirror keys a skill by the kebab case of its front matter `name`, the tree by the directory
the source sat in; when an author spells the two differently, the source is written under both
spellings, so a mirror row finds it either way (`write_aliases` repairs the tree already fetched).
"""

from __future__ import annotations

import re
import tarfile
from pathlib import Path

import common
from common import Config

INVALID_SLUGS = {"", ".", ".."}


def alias_slug(name: str) -> str:
    """The mirror spells a skill's slug as the kebab case of the front matter `name`; the tree
    spells it as the directory the source sat in. Both spellings land in the tree, so a mirror
    row keyed by either finds a source. A kebab that only re-spells the separators the directory
    spelling already covers (`-` where the id had `:`) is not an alias: the catalog joins those
    rows through `skill_dir_name` anyway."""
    return re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")


def is_alias(alias: str, slug: str) -> bool:
    """True when the name-spelled slug is a genuinely different directory, not the directory
    slug with its separators re-spelled."""
    return alias != slug and alias.replace("-", "_") != slug


def extract(stage: Path, config: Config) -> tuple[int, int]:
    """Write every skill's SKILL.md into place; returns the skills taken and the repositories
    processed. A skill is a `SKILL.md` under a subdirectory, named after that directory; the
    repository's own root `SKILL.md` (its readme) is not one. A source with no description is
    skipped, and a slug already taken is left alone - the first source for a name wins. The
    repository directory is created either way: it is the cache, and a repository on disk is never
    fetched again."""
    tarballs = sorted(stage.glob("*.tgz"))
    return sum(extract_tarball(tarball, config) for tarball in tarballs), len(tarballs)


def extract_tarball(tarball: Path, config: Config) -> int:
    """One repository tarball unpacked: the skills taken from it, on the same rules as `extract`."""
    owner, _, repo = tarball.stem.partition("_")
    repo_dir = config.output_dir / common.SKILLS_DIR / owner / repo
    repo_dir.mkdir(parents=True, exist_ok=True)
    taken: set[str] = set()
    skills = 0
    with tarfile.open(tarball, "r:gz") as tar:
        for member in tar:
            if not member.isfile() or not member.name.endswith(f"/{common.SKILL_MD}"):
                continue
            parts = member.name.rsplit("/", 2)
            if len(parts) != 3:
                continue  # <root>/SKILL.md, the repository's readme rather than a skill
            slug = common.skill_dir_name(parts[1])
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
            # the mirror row for this skill is keyed by the kebab case of the `name` field, which
            # an author may spell differently from the directory; write that spelling too, so the
            # mirror row finds a source without ever meeting the directory itself
            alias = alias_slug(common.skill_name(text))
            if alias and is_alias(alias, slug) and alias not in taken \
                    and alias not in INVALID_SLUGS:
                common.write_atomic(repo_dir / alias / common.SKILL_MD, text)
                taken.add(alias)
    return skills


def write_aliases(config: Config) -> int:
    """The alias half of `extract_tarball` over the tree already on disk: every fetched source
    whose `name` spells differently from its directory gains the name-spelled copy. Sync runs
    this, so sources fetched before the alias rule - and their mirror rows - are repaired
    without a refetch; returns the aliases written."""
    written = 0
    sources = (config.output_dir / common.SKILLS_DIR).glob("*/*/*/SKILL.md")
    for source in sources:
        skill_dir = source.parent
        text = source.read_text(encoding="utf-8", errors="replace")
        if not common.skill_description(text):
            continue
        alias = alias_slug(common.skill_name(text))
        alias_dir = skill_dir.parent / alias
        if not alias or not is_alias(alias, skill_dir.name) or alias in INVALID_SLUGS \
                or alias_dir.is_dir() or (alias_dir / common.SKILL_MD).is_file():
            continue
        common.write_atomic(alias_dir / common.SKILL_MD, text)
        written += 1
    return written
