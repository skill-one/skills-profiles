"""Shared fixtures: an isolated workdir with a small fake snapshot on disk, so no
test touches the network."""

import json
import tarfile
import tempfile
from pathlib import Path

import httpx
import pytest

import skills_profiles.data as data_mod
from skills_profiles.config import TARBALL_URL, Settings
from skills_profiles.llm import FakeLLM
from skills_profiles.prompts import load_prompt_set

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# captured here, before the autouse fixture below swaps the name out
real_latest_dist_tag = data_mod.latest_dist_tag

SKILLS = [
    {"id": "owner-a/repo-a/alpha", "name": "Alpha", "description": "Alpha 的官方技能描述",
     "installs": "300", "source": "owner-a/repo-a", "hash": "a" * 64},
    {"id": "owner-b/repo-b/beta", "name": "Beta", "description": "Beta 的官方技能描述",
     "installs": "200", "source": "owner-b/repo-b", "hash": "b" * 64},
    {"id": "owner-c/repo-c/gamma", "name": "Gamma", "description": "Gamma 的官方技能描述",
     "installs": "100", "source": "owner-c/repo-c", "hash": "c" * 64},
    # no description in the index: SkillRecord.description falls back to ""
    {"id": "owner-h/repo-h/hotel:sub", "name": "Hotel", "installs": "50",
     "source": "owner-h/repo-h", "hash": "h" * 64},
    # filtered out: no saved content (no hash)
    {"id": "owner-d/repo-d/delta", "name": "Delta", "installs": "90",
     "source": "owner-d/repo-d"},
]

# the root dir GitHub puts inside a branch tarball
ARCHIVE_ROOT = "skills-sh-mirror-dist"


def skill_md_text(entry: dict) -> str | None:
    """The SKILL.md the fake snapshot holds for one index entry; None = no content."""
    if not entry.get("hash"):  # the scraper saved no source for it
        return None
    name = entry.get("name") or entry["id"]
    return f"---\nname: {name}\n---\n\n{name} does useful things.\n"


def make_fake_dataset(settings: Settings) -> None:
    """Write the fake snapshot: skills.jsonl + one SKILL.md per skill."""
    data_dir = settings.data_dir
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "skills.jsonl").write_text(
        "".join(json.dumps(entry) + "\n" for entry in SKILLS), encoding="utf-8"
    )
    for entry in SKILLS:
        text = skill_md_text(entry)
        if text is None:
            continue
        path = data_dir / "skills" / entry["id"].replace(":", "_") / "SKILL.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def make_tarball(archive: Path, entries: list[dict]) -> None:
    """Build a dist-branch tarball: skills.jsonl + one SKILL.md per entry."""
    files = {"skills.jsonl": "".join(json.dumps(e) + "\n" for e in entries)}
    for entry in entries:
        text = skill_md_text(entry)
        if text:
            slug = entry["id"].replace(":", "_")
            files[f"skills/{slug}/SKILL.md"] = text
            files[f"skills/{slug}/extra.md"] = "part of the skill repo, not needed\n"
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / ARCHIVE_ROOT
        for name, content in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        with tarfile.open(archive, "w:gz") as tar:
            tar.add(root, arcname=root.name)


def fake_download(entries: list[dict]):
    """Offline stand-in for data.download_file: serves a snapshot tarball."""

    def _download(url: str, dest: Path) -> bool:
        assert url == TARBALL_URL, f"unexpected download url: {url}"
        make_tarball(Path(dest), entries)
        return True

    return _download


@pytest.fixture(autouse=True)
def _no_upstream_tags(monkeypatch):
    """Pretend upstream publishes no tags: a sync must not reach the network for
    anything but the snapshot itself, and tests that care set their own tag."""
    monkeypatch.setattr(data_mod, "latest_dist_tag", lambda: None)


@pytest.fixture
def latest_pointer(monkeypatch):
    """Serve a fake upstream `latest` pointer through the real reader.

    The autouse fixture above stubs `latest_dist_tag` itself so tests never
    reach the network; this puts the real function back and stubs the single
    request underneath it. `serve(body, error=None)` returns the urls fetched.
    """
    def serve(body: bytes, error: Exception | None = None) -> list[str]:
        calls: list[str] = []
        monkeypatch.setattr(data_mod, "latest_dist_tag", real_latest_dist_tag)

        def get(url: str, **kwargs):
            calls.append(url)
            if error is not None:
                raise error
            return httpx.Response(200, text=body.decode("utf-8", "replace"))

        monkeypatch.setattr(data_mod.httpx, "get", get)
        return calls

    return serve


@pytest.fixture
def settings(tmp_path) -> Settings:
    s = Settings(output_dir=tmp_path / "output",
                 data_dir=tmp_path / "cache" / "skills-sh",
                 image_api_key=None, image_api_keys=[])  # tests stay offline even when a local .env has keys
    make_fake_dataset(s)
    return s


@pytest.fixture
def prompt_set():
    return load_prompt_set(PROJECT_ROOT / "prompts")


# LLM doubles shared by the CLI and generation suites. They are keyed on the
# rendered prompt, so they fail exactly the skills a test means them to.

class FailingForAlpha:
    """Answers like the fake, except for Alpha: quota errors, one skill only."""

    def __init__(self) -> None:
        self.inner = FakeLLM()

    async def create(self, response_model=None, messages=None, **kwargs):
        system = messages[0]["content"] if messages else ""
        if "Alpha does useful things." in system:
            raise RuntimeError("quota exceeded")
        return await self.inner.create(response_model, messages, **kwargs)


class DeadLLM:
    """Fails every call: a systemic error (bad key, endpoint down)."""

    async def create(self, response_model=None, messages=None, **kwargs):
        raise RuntimeError("endpoint down")
