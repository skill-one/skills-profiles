"""meta.py and the `meta` batch: a repository's profile and an owner's avatar.

The shaping is unit-tested directly; the catalog merge, the avatar download and the gone row run
in-process through `batch.py`, against a local `file://` GitHub root, so no test calls out.
"""

from types import SimpleNamespace

import httpx

import batch
import common
import meta
from conftest import make_github_root

REPO_A = "owner-a/repo-a"
REPO_B = "owner-b/repo-b"
OWNER_A = "owner-a"


def run_meta(capsys, root, monkeypatch, *args: str) -> SimpleNamespace:
    """One in-process `batch.py meta` run against a local GitHub root; stderr is what we assert."""
    monkeypatch.setenv("SKILLS_PROFILES_GITHUB_API_URL", f"file://{root}")
    rc = batch.main(["meta", *args])
    return SimpleNamespace(returncode=rc, stderr=capsys.readouterr().err)


def repos_of(config) -> dict:
    """The repository catalog, keyed by id, the way a consumer joins it."""
    return {row["id"]: row for row in common.read_jsonl(common.repos_index_path(config))}


def fail_with(code: int):
    """A `Downloader.get` that answers one status for every request."""
    def get(self, url, dest):
        raise httpx.HTTPStatusError(f"{code}", request=httpx.Request("GET", url),
                                    response=httpx.Response(code))
    return get


# ------------------------------------------------------------------ the shaping


def test_a_repository_row_carries_what_the_catalog_cannot_know():
    row = meta.repo_row(REPO_A, "now", payload={
        "description": "Tidies a note list.", "stargazers_count": 7,
        "updated_at": "2026-09-01T00:00:00Z", "pushed_at": "2026-08-31T00:00:00Z",
        "html_url": "https://github.com/owner-a/repo-a"})

    assert row == {"id": REPO_A, "owner": "owner-a", "repo": "repo-a",
                   "description": "Tidies a note list.", "stars": 7,
                   "updated_at": "2026-09-01T00:00:00Z", "pushed_at": "2026-08-31T00:00:00Z",
                   "html_url": "https://github.com/owner-a/repo-a", "gone": False,
                   "fetched_at": "now"}


def test_a_gone_row_has_no_metadata_and_the_same_keys():
    row = meta.repo_gone_row(REPO_A)

    assert row["gone"] is True and row["id"] == REPO_A
    assert row["description"] is None and row["stars"] is None
    assert set(row) == set(meta.repo_row(REPO_A, "now"))  # one shape whether built or gone


def test_headers_carry_the_versioned_accept_and_the_token_only_when_set(monkeypatch, workdir):
    bare = meta.headers(common.Config())
    assert bare["Accept"] == "application/vnd.github+json"
    assert "User-Agent" in bare and "Authorization" not in bare

    monkeypatch.setenv("SKILLS_PROFILES_GITHUB_TOKEN", "ghp_test")
    assert meta.headers(common.Config())["Authorization"] == "Bearer ghp_test"


# ------------------------------------------------------------------ the roster


def test_the_roster_is_the_catalogs_entities_deduped_and_in_order(workdir):
    config = common.Config()

    assert batch.meta_entities(config, meta.REPO_KIND) == [
        "owner-a/repo-a", "owner-b/repo-b", "owner-c/repo-c", "owner-h/repo-h",
        "owner-e/.dotcfg", "owner-d/repo-d"]
    assert batch.meta_entities(config, meta.OWNER_KIND) == [
        "owner-a", "owner-b", "owner-c", "owner-h", "owner-e", "owner-d"]


# ---------------------------------------------------------------- the batch


def test_one_run_writes_the_catalog_and_the_avatars(capsys, workdir, tmp_path, monkeypatch):
    root = make_github_root(tmp_path / "github")

    assert run_meta(capsys, root, monkeypatch).returncode == 0

    config = common.Config()
    repos = repos_of(config)
    assert list(repos) == ["owner-a/repo-a", "owner-b/repo-b", "owner-c/repo-c", "owner-h/repo-h",
                           "owner-e/.dotcfg", "owner-d/repo-d"]
    assert repos[REPO_A]["stars"] == 60
    assert repos[REPO_A]["description"].startswith("A repository the test fakes")
    assert repos[REPO_A]["gone"] is False
    assert common.owner_avatar_path(config, OWNER_A).read_bytes().startswith(b"\x89PNG")
    assert not (config.output_dir / "owners.jsonl").exists()  # an owner has no row


def test_a_second_run_has_nothing_to_do(capsys, workdir, tmp_path, monkeypatch):
    root = make_github_root(tmp_path / "github")
    assert run_meta(capsys, root, monkeypatch).returncode == 0

    again = run_meta(capsys, root, monkeypatch)

    assert again.returncode == 0
    assert "nothing to build" in again.stderr


def test_a_repository_github_lacks_becomes_a_gone_row(capsys, workdir, tmp_path, monkeypatch):
    root = make_github_root(tmp_path / "github")
    real = common.Downloader.get

    def gone(self, url, dest):
        if url.endswith(f"/repos/{REPO_A}"):
            raise httpx.HTTPStatusError("Client error '404 Not Found'",
                                        request=httpx.Request("GET", url),
                                        response=httpx.Response(404))
        return real(self, url, dest)

    monkeypatch.setattr(common.Downloader, "get", gone)
    result = run_meta(capsys, root, monkeypatch)

    assert result.returncode == 0, result.stderr
    assert f"gone: {REPO_A}" in result.stderr
    repos = repos_of(common.Config())
    assert repos[REPO_A]["gone"] is True and repos[REPO_A]["stars"] is None
    assert repos[REPO_B]["gone"] is False

    again = run_meta(capsys, root, monkeypatch)
    assert "nothing to build" in again.stderr  # the gone row is resolved, so not retried


def test_an_owner_github_lacks_is_retried_next_run(capsys, workdir, tmp_path, monkeypatch):
    root = make_github_root(tmp_path / "github")
    real = common.Downloader.get

    def gone(self, url, dest):
        if url.endswith(f"/users/{OWNER_A}"):
            raise httpx.HTTPStatusError("Client error '404 Not Found'",
                                        request=httpx.Request("GET", url),
                                        response=httpx.Response(404))
        return real(self, url, dest)

    monkeypatch.setattr(common.Downloader, "get", gone)
    assert run_meta(capsys, root, monkeypatch).returncode == 0
    config = common.Config()
    assert not common.owner_avatar_path(config, OWNER_A).exists()
    assert common.owner_avatar_path(config, "owner-b").is_file()

    again = run_meta(capsys, root, monkeypatch)
    assert f"failed: {OWNER_A}" in again.stderr  # no catalog, no gone: it is tried again


def test_a_broken_payload_fails_only_its_own_repository(capsys, workdir, tmp_path, monkeypatch):
    root = make_github_root(tmp_path / "github")
    (root / "repos" / "owner-a" / "repo-a").write_text("[]", encoding="utf-8")

    result = run_meta(capsys, root, monkeypatch)

    assert result.returncode == 0, result.stderr  # partial output is published output
    assert f"failed: {REPO_A}" in result.stderr
    repos = repos_of(common.Config())
    assert REPO_A not in repos and REPO_B in repos


def test_a_run_whose_every_fetch_failed_is_status_one(capsys, workdir, tmp_path, monkeypatch):
    root = make_github_root(tmp_path / "github")
    monkeypatch.setattr(common.Downloader, "get", fail_with(400))

    result = run_meta(capsys, root, monkeypatch)

    assert result.returncode == 1
    assert not common.repos_index_path(common.Config()).is_file()  # nothing was written


def test_clean_forgets_the_catalog_and_the_avatars(capsys, workdir, tmp_path, monkeypatch):
    root = make_github_root(tmp_path / "github")
    assert run_meta(capsys, root, monkeypatch).returncode == 0
    config = common.Config()
    assert common.repos_index_path(config).is_file()
    assert common.owner_avatar_path(config, OWNER_A).is_file()

    rc = batch.main(["meta", "--clean"])
    capsys.readouterr()

    assert rc == 0
    assert not common.repos_index_path(config).exists()
    assert not common.owner_avatar_path(config, OWNER_A).exists()
    assert not (config.output_dir / common.OWNERS_DIR).exists()
