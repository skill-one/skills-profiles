"""Shared fixtures and helpers: an isolated workdir with a small fake snapshot on
disk, so no test touches the network."""

import json
import tarfile
import tempfile
from pathlib import Path

import pytest

import gen

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ["justfile", "gen.py", "index.py", "stale.py"]
ARCHIVE_ROOT = "skills-sh-mirror-dist"  # GitHub wraps a branch in <repo>-<branch>/
# the published root: the skill directories, the profiles written about them, the mirror's own files
# and the catalog, which are the four things the justfile and the three scripts all read
OUTPUT = Path("output")

# The fake mirror's own index: five skills with saved content, one without (the scraper recorded no
# source for it, so nothing could be generated from it). A mirror row carries no description any
# more - upstream dropped it - so a skill's own front matter is the only copy of it.
SKILLS = [
    {"id": "owner-a/repo-a/alpha", "installs": "300", "hash": "a" * 64,
     "description": "Tidies a note list, folds the loose ends into a running index, and keeps "
                    "the whole pile searchable."},
    {"id": "owner-b/repo-b/beta", "installs": "200", "hash": "b" * 64,
     "description": "Drafts a release note from the merged pull requests, then trims it down to "
                    "the sentences a reader would actually care about."},
    {"id": "owner-c/repo-c/gamma", "installs": "100", "hash": "c" * 64,
     "description": "Converts a table into CSV, guessing the delimiter and the encoding, and "
                    "reporting what it guessed instead of failing quietly."},
    {"id": "owner-h/repo-h/hotel:sub", "installs": "50", "hash": "h" * 64,
     "description": "Books a hotel room for the dates in a sentence, then hands the confirmation "
                    "number back to whoever asked for it."},
    {"id": "owner-e/.dotcfg/settings", "installs": "40", "hash": "e" * 64,
     "description": "Keeps dotfiles in order across machines, one file per tool, and no symlink "
                    "surprises on a new laptop."},
    {"id": "owner-d/repo-d/delta", "installs": "90"},
]


def skill_dir_name(skill_id: str) -> str:
    """Upstream writes `_` where an id carries a colon or an ampersand."""
    return skill_id.replace(":", "_").replace("&", "_")


def skill_md_text(entry: dict) -> str | None:
    """The SKILL.md the fake mirror holds for one skill; None = no content.

    Upstream writes the skill's name and description into the front matter, and since the index
    dropped its own copy of the description, that block is where gen.py reads it from.
    """
    if not entry.get("hash"):  # the scraper saved no source for it
        return None
    return (f"---\nname: {entry['id']}\ndescription: {entry['description']}\n---\n\n"
            f"{entry['id']} does useful things.\n")


def index_row(entry: dict) -> dict:
    """One row of the fake mirror's index: what upstream publishes for a skill, and no description."""
    return {name: entry[name] for name in ("id", "installs", "hash") if name in entry}


def skill_path(output: Path, skill_id: str) -> Path:
    """A skill's own directory, as the mirror publishes it: what a user downloads and installs."""
    return output / gen.SKILLS_DIR / skill_dir_name(skill_id)


def profile_path(output: Path, skill_id: str) -> Path:
    """What this project writes about a skill."""
    return output / gen.PROFILES_DIR / skill_dir_name(skill_id)


def branch_files(entries: list[dict]) -> dict[str, str]:
    """The files the fake mirror's branch holds: its index, one directory per skill, and the
    metadata a real branch carries beside them."""
    files = {"skills.jsonl": "".join(json.dumps(index_row(entry)) + "\n" for entry in entries),
             "repos.jsonl": '{"repo": "owner-a/repo-a", "stars": 1}\n'}
    for entry in entries:
        text = skill_md_text(entry)
        if text:
            rel = f"skills/{skill_dir_name(entry['id'])}"
            files[f"{rel}/SKILL.md"] = text
            files[f"{rel}/extra.md"] = "part of the skill repo\n"
    return files


def write_snapshot(output: Path, entries: list[dict] | None = None) -> None:
    """A snapshot already unpacked into the output tree, the way `just sync` leaves it: the skill
    directories at the root, the mirror's own files beside them under `upstream/`."""
    for name, content in branch_files(SKILLS if entries is None else entries).items():
        where = output / name if name.startswith("skills/") else output / gen.UPSTREAM_DIR / name
        where.parent.mkdir(parents=True, exist_ok=True)
        where.write_text(content, encoding="utf-8")


def make_tarball(archive: Path, entries: list[dict] | None = None) -> None:
    """Build a dist-branch tarball for `make sync` to fetch."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / ARCHIVE_ROOT
        for name, content in branch_files(SKILLS if entries is None else entries).items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        with tarfile.open(archive, "w:gz") as tar:
            tar.add(root, arcname=root.name)


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    """No test reaches the network.

    Constructing the SDK client raises, so a test cannot silently call out even with
    a local `.env` full of real keys. `make sync` never runs against the network in a
    test either: it is pointed at a local tarball through the SNAPSHOT variable.
    """
    import openai

    def _no_client(*args, **kwargs):
        raise AssertionError("a real LLM client was constructed")

    monkeypatch.setattr(openai, "OpenAI", _no_client)


@pytest.fixture
def workdir(tmp_path, monkeypatch) -> Path:
    """An isolated working directory, wired up through SKILLS_PROFILES_* env vars.

    The scripts each build their own Config, so the tests point them at tmp_path the
    way a user would - through the environment - and chdir into it so nothing
    relative (`.env`, `output/`) can escape.
    """
    workdir = tmp_path / "work"
    workdir.mkdir()
    monkeypatch.chdir(workdir)
    monkeypatch.setenv("SKILLS_PROFILES_OUTPUT_DIR", str(workdir / OUTPUT))
    monkeypatch.setenv("SKILLS_PROFILES_PROMPTS_DIR", str(PROJECT_ROOT / "prompts"))
    monkeypatch.setenv("SKILLS_PROFILES_DRY_RUN", "1")
    write_snapshot(workdir / OUTPUT)
    return workdir


@pytest.fixture
def config(workdir) -> gen.Config:
    """The Config gen.py would build for `workdir`."""
    return gen.Config()
