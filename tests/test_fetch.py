"""fetch.py: a repository's skills unpacked from its tarball, the listing not consulted."""

import io
import tarfile
from pathlib import Path

import common
import fetch

REPO = "owner-x/repo-x"


def source(description: str) -> str:
    """A front matter whose `name` kebab-cases to the directory the tests drop it in."""
    return f"---\nname: alpha\ndescription: {description}\n---\n\nBody.\n"


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
    is unpacked, keyed by the front matter `name`."""
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
    """A repository that names its skill directory `..` must not write outside the tree: without
    a `name` to key the source by, the directory slug is skipped, like any other source this
    project cannot install as a skill."""
    stage = tarball(tmp_path / "stage", {"../SKILL.md": "---\ndescription: Escapes.\n---\n"})

    assert fetch.extract(stage, config) == (0, 1)

    assert not (config.output_dir / common.SKILLS_DIR / "owner-x" / "SKILL.md").exists()
    assert not (config.output_dir / common.SKILLS_DIR / "SKILL.md").exists()


def test_a_source_is_keyed_by_its_name_not_its_directory(config, tmp_path):
    """The mirror spells a skill id's slug out of the front matter `name`, and the tree keys the
    directory by the same field: an author whose directory spelling differs still lands at the
    slug the catalog rows use, one directory, one skill."""
    stage = tarball(tmp_path / "stage", {
        "skills/writing-rules/SKILL.md":
            "---\nname: hookify-rules\ndescription: D.\n---\n\nBody.\n"})

    assert fetch.extract(stage, config) == (1, 1)

    assert common.skill_md_path(config, f"{REPO}/hookify-rules").is_file()
    assert [p.name for p in repo_dir(config).iterdir()] == ["hookify-rules"]


def test_a_name_that_would_escape_falls_back_to_its_directory(config, tmp_path):
    stage = tarball(tmp_path / "stage", {
        "skills/alpha/SKILL.md": "---\nname: ../escape\ndescription: D.\n---\n\nBody.\n"})

    assert fetch.extract(stage, config) == (1, 1)

    assert common.skill_md_path(config, f"{REPO}/alpha").is_file()


def test_a_source_whose_name_matches_its_directory_writes_one_directory(config, tmp_path):
    stage = tarball(tmp_path / "stage", {"skills/alpha/SKILL.md": source("Alpha.")})

    assert fetch.extract(stage, config) == (1, 1)

    assert [p.name for p in repo_dir(config).iterdir()] == ["alpha"]


def test_a_source_without_a_name_takes_its_directory(config, tmp_path):
    stage = tarball(tmp_path / "stage", {
        "skills/alpha/SKILL.md": "---\ndescription: D.\n---\n\nBody.\n"})

    assert fetch.extract(stage, config) == (1, 1)

    assert [p.name for p in repo_dir(config).iterdir()] == ["alpha"]


def test_every_skill_in_the_repository_is_taken(config, tmp_path):
    """The catalog is not consulted: a skill the listing has not reached yet is unpacked all the
    same, so a listing that lags behind its repository catches up without a second download."""
    stage = tarball(tmp_path / "stage", {
        "skills/alpha/SKILL.md": source("Alpha."),
        "skills/beta/SKILL.md": "---\nname: beta\ndescription: Beta.\n---\n\nBody.\n",
    })

    assert fetch.extract(stage, config) == (2, 1)

    assert common.skill_md_path(config, f"{REPO}/alpha").is_file()
    assert common.skill_md_path(config, f"{REPO}/beta").is_file()


def test_a_repository_that_holds_no_skill_is_still_a_directory(config, tmp_path):
    """The repository directory is the cache, created even when the repository yields nothing, so
    it is never downloaded again. A root `SKILL.md` that cannot say what it is for stays nothing."""
    stage = tarball(tmp_path / "stage", {"SKILL.md": "# A repository readme.\n"})

    assert fetch.extract(stage, config) == (0, 1)

    assert repo_dir(config).is_dir()


def test_a_repository_whose_only_skill_md_is_at_the_root(config, tmp_path):
    """A single-skill repository keeps its source at the root: with nothing in a subdirectory, the
    root `SKILL.md` is the skill itself, keyed by its `name`."""
    stage = tarball(tmp_path / "stage", {
        "SKILL.md": "---\nname: alpha-skill\ndescription: Does one thing well.\n---\n\nBody.\n",
    })

    assert fetch.extract(stage, config) == (1, 1)

    assert common.skill_md_path(config, f"{REPO}/alpha-skill").is_file()


def test_a_root_source_without_a_name_takes_the_repositorys_name(config, tmp_path):
    stage = tarball(tmp_path / "stage", {
        "SKILL.md": "---\ndescription: Does one thing well.\n---\n\nBody.\n",
    })

    assert fetch.extract(stage, config) == (1, 1)

    assert common.skill_md_path(config, f"{REPO}/repo-x").is_file()


def test_a_root_readme_beside_subdirectory_skills_stays_a_readme(config, tmp_path):
    """The root `SKILL.md` is the single-skill repository's source only when nothing below it is a
    skill; beside subdirectory skills it is the repository's readme, described or not."""
    stage = tarball(tmp_path / "stage", {
        "SKILL.md": "---\nname: root-skill\ndescription: The readme, described.\n---\n\nBody.\n",
        "skills/alpha/SKILL.md": source("The real skill."),
    })

    assert fetch.extract(stage, config) == (1, 1)

    assert [p.name for p in repo_dir(config).iterdir()] == ["alpha"]
