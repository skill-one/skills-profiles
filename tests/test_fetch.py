"""fetch.py: a repository's skills unpacked from its tarball, the listing not consulted."""

import io
import tarfile
from pathlib import Path

import common
import fetch

REPO = "owner-x/repo-x"


def source(description: str) -> str:
    return f"---\nname: x\ndescription: {description}\n---\n\nBody.\n"


def tarball(stage: Path, files: dict[str, str], repo: str = REPO) -> Path:
    """One `<owner>_<repo>.tgz` laid out the way codeload ships a repository: every file under a
    `<repo>-<sha>/` root, in the order given - so a `SKILL.md` in a subdirectory is a skill and the
    root one is the repository's readme, and "first" means first here."""
    owner, name = repo.split("/")
    root = f"{name}-abc1234"
    stage.mkdir(parents=True, exist_ok=True)
    with tarfile.open(stage / f"{owner}_{name}.tgz", "w:gz") as tar:
        for where, content in files.items():
            data = content.encode("utf-8")
            info = tarfile.TarInfo(f"{root}/{where}")
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
    return stage


def repo_dir(config: common.Config) -> Path:
    return config.output_dir / common.SKILLS_DIR / REPO


def test_a_skill_is_a_skill_md_in_a_subdirectory(config, tmp_path):
    """The repository's own root `SKILL.md` is its readme, not a skill: only the subdirectory one
    is unpacked, named after its directory."""
    stage = tarball(tmp_path / "stage", {
        "SKILL.md": "# A repository readme, not a skill.\n",
        "skills/alpha/SKILL.md": source("Tidies a list."),
    })

    assert fetch.extract(stage, config) == (1, 1)

    assert [p.name for p in repo_dir(config).iterdir()] == ["alpha"]
    assert common.skill_md_path(config, f"{REPO}/alpha").is_file()


def test_a_source_with_no_description_is_skipped(config, tmp_path):
    """A source that cannot say what the skill is for can never be built: it is left out, so the
    skill's directory stays empty and the batch reads it as unbuildable."""
    stage = tarball(tmp_path / "stage", {"skills/alpha/SKILL.md": "# no front matter\n"})

    assert fetch.extract(stage, config) == (0, 1)

    assert not common.skill_md_path(config, f"{REPO}/alpha").exists()


def test_a_duplicate_skill_name_is_taken_once(config, tmp_path):
    """One directory, one skill: a second source with the same name is skipped, the first winning."""
    stage = tarball(tmp_path / "stage", {
        "skills/alpha/SKILL.md": source("The first one."),
        "other/alpha/SKILL.md": source("The second one."),
    })

    assert fetch.extract(stage, config) == (1, 1)

    assert "The first one." in common.skill_md(config, f"{REPO}/alpha")


def test_a_slug_that_is_not_a_name_writes_nowhere_outside(config, tmp_path):
    """A repository that names its skill directory `..` must not write outside the tree: the
    slug is skipped, like any other source this project cannot install as a skill."""
    stage = tarball(tmp_path / "stage", {"../SKILL.md": source("Escapes.")})

    assert fetch.extract(stage, config) == (0, 1)

    assert not (config.output_dir / common.SKILLS_DIR / "owner-x" / "SKILL.md").exists()
    assert not (config.output_dir / common.SKILLS_DIR / "SKILL.md").exists()


def test_every_skill_in_the_repository_is_taken(config, tmp_path):
    """The catalog is not consulted: a skill the listing has not reached yet is unpacked all the
    same, so a listing that lags behind its repository catches up without a second download."""
    stage = tarball(tmp_path / "stage", {
        "skills/alpha/SKILL.md": source("Alpha."),
        "skills/beta/SKILL.md": source("Beta."),
    })

    assert fetch.extract(stage, config) == (2, 1)

    assert common.skill_md_path(config, f"{REPO}/alpha").is_file()
    assert common.skill_md_path(config, f"{REPO}/beta").is_file()


def test_a_repository_that_holds_no_skill_is_still_a_directory(config, tmp_path):
    """The repository directory is the cache, created even when the repository yields nothing, so
    it is never downloaded again."""
    stage = tarball(tmp_path / "stage", {"SKILL.md": "# A repository readme.\n"})

    assert fetch.extract(stage, config) == (0, 1)

    assert repo_dir(config).is_dir()
