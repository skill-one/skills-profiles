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
# the snapshot's home inside the output root, where the justfile and gen.py both look for it
DATA_ROOT = Path("output") / "cache" / "skills-sh"

# The fake upstream index: four skills with saved content, one without (the
# scraper recorded no hash for it, so nothing could be generated from it).
SKILLS = [
    {"id": "owner-a/repo-a/alpha", "installs": "300", "hash": "a" * 64},
    {"id": "owner-b/repo-b/beta", "installs": "200", "hash": "b" * 64},
    {"id": "owner-c/repo-c/gamma", "installs": "100", "hash": "c" * 64},
    {"id": "owner-h/repo-h/hotel:sub", "installs": "50", "hash": "h" * 64},
    {"id": "owner-e/.dotcfg/settings", "installs": "40", "hash": "e" * 64},
    {"id": "owner-d/repo-d/delta", "installs": "90"},
]


def skill_dir_name(skill_id: str) -> str:
    """Upstream writes `_` where an id carries a colon or an ampersand."""
    return skill_id.replace(":", "_").replace("&", "_")


def skill_md_text(entry: dict) -> str | None:
    """The SKILL.md the fake snapshot holds for one index entry; None = no content."""
    if not entry.get("hash"):  # the scraper saved no source for it
        return None
    return f"---\nname: {entry['id']}\n---\n\n{entry['id']} does useful things.\n"


def skill_path(root: Path, skill_id: str) -> Path:
    """A skill's directory inside a snapshot (or artifact) tree."""
    return root / "skills" / skill_dir_name(skill_id)


def snapshot_files(entries: list[dict]) -> dict[str, str]:
    """The files the fake branch holds: the index, a SKILL.md per skill, and the
    noise a real skill repo carries beside it."""
    files = {"skills.jsonl": "".join(json.dumps(entry) + "\n" for entry in entries)}
    for entry in entries:
        text = skill_md_text(entry)
        if text:
            rel = f"skills/{skill_dir_name(entry['id'])}"
            files[f"{rel}/SKILL.md"] = text
            files[f"{rel}/extra.md"] = "part of the skill repo\n"
    return files


def write_dataset(data_dir: Path, entries: list[dict] | None = None) -> None:
    """Write a fake snapshot tree straight to disk (no tarball involved)."""
    for name, content in snapshot_files(SKILLS if entries is None else entries).items():
        path = data_dir / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def make_tarball(archive: Path, entries: list[dict] | None = None) -> None:
    """Build a dist-branch tarball for `make sync` to fetch."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / ARCHIVE_ROOT
        for name, content in snapshot_files(SKILLS if entries is None else entries).items():
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
    monkeypatch.setenv("SKILLS_PROFILES_OUTPUT_DIR", str(workdir / "output"))
    monkeypatch.setenv("SKILLS_PROFILES_DATA_DIR", str(workdir / DATA_ROOT))
    monkeypatch.setenv("SKILLS_PROFILES_PROMPTS_DIR", str(PROJECT_ROOT / "prompts"))
    monkeypatch.setenv("SKILLS_PROFILES_DRY_RUN", "1")
    write_dataset(workdir / DATA_ROOT)
    return workdir


@pytest.fixture
def config(workdir) -> gen.Config:
    """The Config gen.py would build for `workdir`."""
    return gen.Config()
