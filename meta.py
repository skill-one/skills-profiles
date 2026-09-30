#!/usr/bin/env python3
"""The entities above a skill: a repository's profile, and the avatar of the owner it belongs to.

A skill id leads with `owner/repo`, and a repository is worth more than the id alone says: it has a
description, a star count and a last-update time, and it carries its owner. So this module reads
GitHub's own `/repos` for each repository - one call yields both artifacts - and puts each where it
fits: the repository into the catalog `repos.jsonl`, one row each; the owner into the one file it is,
`owners/<owner>.png`, at the fixed path a frontend builds from the owner alone. Reading the owner
from the repository rather than `/users` matters: `/repos` follows a rename where `/users` answers
404, so a renamed owner still yields an avatar. A repository GitHub has no answer for becomes a `gone`
row, so it is not fetched again.

The shaping is here; `headers()` builds what every request carries - the versioned accept, the
user-agent GitHub refuses to answer without, and the token when one is set. `batch.py` owns the
window and the pool: one repository per pool job, its row into the catalog and its owner's avatar
to their one file.
"""

from __future__ import annotations

import json
import tempfile
from datetime import UTC, datetime
from pathlib import Path

import common
from common import Config, Downloader


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
    """Fetch one repository: return its catalog row and write its owner's avatar. The `/repos` payload
    carries the owner - with the login the endpoint resolved, which is why a renamed owner still
    yields an avatar - so one call serves both."""
    payload = _json(downloader, repo_url(config.github_api_url, repo))
    _write_avatar(config, repo.partition("/")[0], payload.get("owner"), downloader)
    return repo_row(repo, _now(), payload=payload)


def _write_avatar(config: Config, owner: str, holder: object, downloader: Downloader) -> None:
    """Write `owners/<owner>.png` from a payload's `owner` object, unless the file is already there.
    The mirror's own spelling names the file, so a frontend's `owners/<owner>.png` always matches."""
    avatar_url = holder.get("avatar_url") if isinstance(holder, dict) else None
    path = common.owner_avatar_path(config, owner)
    if path.is_file() or not (isinstance(avatar_url, str) and avatar_url):
        return
    with tempfile.TemporaryDirectory(prefix="skills-meta-") as tmp:
        blob = Path(tmp) / "avatar"
        downloader.get(avatar_url, blob)
        common.write_bytes(path, blob.read_bytes())


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
