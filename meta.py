#!/usr/bin/env python3
"""The two entities above a skill: one repository's profile, one owner's avatar.

A skill id leads with `owner/repo`, and both are worth more than the id alone says: a repository
has a description, a star count and a last-update time, and an owner has an avatar. The mirror's
listing carries neither, so this module reads GitHub's own API - one call per repository, one per
owner plus a download of its avatar - and puts each where it fits: repositories into the catalog
`repos.jsonl`, one row each; an owner into the one file it is, `owners/<owner>.png`, at the fixed
path a frontend builds from the owner alone. A repository GitHub has no answer for becomes a `gone`
row, so it is not fetched again.

The shaping is here; `headers()` builds what every request carries - the versioned accept, the
user-agent GitHub refuses to answer without, and the token when one is set. `batch.py` owns the
window and the pool: one entity per pool job, the repositories into the catalog, the avatars to
their one file.
"""

from __future__ import annotations

import json
import tempfile
from datetime import UTC, datetime
from pathlib import Path

import common
from common import Config, Downloader

REPO_KIND = "repo"
OWNER_KIND = "owner"


def headers(config: Config) -> dict[str, str]:
    """What every GitHub request carries: the versioned accept, the user-agent it requires, and the
    token when one is set - which is what keeps the calls off the anonymous rate floor."""
    head = {"Accept": "application/vnd.github+json", "User-Agent": "skills-profiles"}
    if config.github_token:
        head["Authorization"] = f"Bearer {config.github_token}"
    return head


def repo_url(api: str, repo: str) -> str:
    """The one repository endpoint, addressed by the `owner/repo` a skill id leads with."""
    return f"{api.rstrip('/')}/repos/{repo}"


def owner_url(api: str, owner: str) -> str:
    """The one owner endpoint."""
    return f"{api.rstrip('/')}/users/{owner}"


def repo_row(repo: str, fetched_at: str, payload: dict | None = None, gone: bool = False) -> dict:
    """One row of `repos.jsonl`: the description, stars and last-update time the catalog cannot
    know - null, with `gone` set, for a repository GitHub has no answer for."""
    owner, _, name = repo.partition("/")
    payload = payload or {}
    return {"id": repo, "owner": owner, "repo": name,
            "description": payload.get("description"),
            "stars": payload.get("stargazers_count"),
            "updated_at": payload.get("updated_at"),
            "pushed_at": payload.get("pushed_at"),
            "html_url": payload.get("html_url"),
            "gone": gone, "fetched_at": fetched_at}


def repo_gone_row(repo: str) -> dict:
    """The row a repository GitHub has no answer for leaves: no metadata, `gone` set, so the catalog
    records the dead end and no run fetches it again."""
    return repo_row(repo, _now(), gone=True)


def build_repo(config: Config, repo: str, downloader: Downloader) -> dict:
    """Fetch one repository and return its catalog row."""
    return repo_row(repo, _now(), payload=_json(downloader, repo_url(config.github_api_url, repo)))


def build_owner(config: Config, owner: str, downloader: Downloader) -> Path:
    """Fetch one owner's avatar and write it to its fixed path; returns the file. The avatar is the
    whole of what an owner has, so its presence is the cache - no catalog, no row."""
    payload = _json(downloader, owner_url(config.github_api_url, owner))
    avatar_url = payload.get("avatar_url")
    path = common.owner_avatar_path(config, owner)
    if isinstance(avatar_url, str) and avatar_url:
        with tempfile.TemporaryDirectory(prefix="skills-meta-") as tmp:
            blob = Path(tmp) / "avatar"
            downloader.get(avatar_url, blob)
            common.write_bytes(path, blob.read_bytes())
    return path


def _json(downloader: Downloader, url: str) -> dict:
    """One endpoint's payload, downloaded whole and parsed: anything but an object is an error."""
    with tempfile.TemporaryDirectory(prefix="skills-meta-") as tmp:
        dest = Path(tmp) / "payload.json"
        downloader.get(url, dest)
        payload = json.loads(dest.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{url}: the answer is not an object")
    return payload


def _now() -> str:
    """When this profile was read, UTC: the one field that says how fresh the stars are."""
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
