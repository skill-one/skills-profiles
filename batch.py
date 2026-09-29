#!/usr/bin/env python3
"""The batch driver: window the catalog, fetch the window's repositories, build one angle.

The justfile is a thin launcher of this script. It owns the three things that used to be shell:
walking `skills.jsonl` (parsed as jsonl, never sed'ed) to pick the next `limit` skills still
missing the angle, downloading and unpacking each window repository once (the repository
directory is the cache), and the `jobs`-wide pool that runs the producers - one producer process
per skill. `sync` is the other subcommand: reconcile with the mirror - pull its listing, refetch
the repositories it adds a skill to, and rewrite the catalog last.

A failed job never ends the run: the skill is named on stderr and, when CI gives the paths, in
FAIL_LOG/GEN_ERR_LOG, and the next run retries exactly it - its angle file is still missing.

    batch.py build <angle> --limit N --jobs N [--repo-tarball URL]
    batch.py clean <angle> --limit N        # the inverse: forget the first N built outputs
    batch.py sync --listing URL [--repo-tarball URL]
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlsplit

import httpx

import common
import fetch
import index
from common import Config

DEFAULT_LISTING = ("https://raw.githubusercontent.com/skill-one/"
                   "skills-sh-mirror/dist/skills.jsonl")
DEFAULT_REPO_TARBALL = "https://codeload.github.com/{owner}/{repo}/tar.gz/HEAD"

# one pool job is one producer process: the per-skill isolation the command contract assumes
ANGLE_SCRIPT = {common.DOMAIN_ANGLE: "jev.py", common.SKILL_ZH_ANGLE: "skill_zh.py"}
ANGLE_LABEL = {common.DOMAIN_ANGLE: "domain", common.SKILL_ZH_ANGLE: "zh page"}

# FAIL_LOG/GEN_ERR_LOG are append-only CI handovers; workers append from threads.
_log_lock = threading.Lock()


class BatchError(Exception):
    """A fatal batch error: one stderr line and exit 1, never a traceback."""


# --------------------------------------------------------------------------- the catalog


def read_ids(path: Path) -> list[str]:
    """The skill ids in one jsonl file, in its own order; a line that is not json is a hard
    error rather than a silently empty catalog."""
    ids: list[str] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except ValueError as error:
            raise BatchError(
                f"{path}: line {line_no} is not valid JSON - run `just sync` first") from error
        skill = entry.get("id") if isinstance(entry, dict) else None
        if isinstance(skill, str):
            ids.append(common.skill_dir_name(skill))
    return ids


def catalog_ids(config: Config) -> list[str]:
    """The catalog's ids in the batch's own order - the mirror's, installs descending."""
    path = config.output_dir / common.INDEX
    if not path.is_file():
        raise BatchError(f"no catalog under {config.output_dir} - run `just sync` first")
    ids = read_ids(path)
    if not ids:
        raise BatchError("the catalog lists no skill")
    return ids


def repo_of(skill: str) -> str:
    """A skill's `owner/repo`, the unit a tarball is downloaded and cached in."""
    owner, repo, _slug = skill.split("/", 2)
    return f"{owner}/{repo}"


def repo_dir(config: Config, repo: str) -> Path:
    return config.output_dir / common.SKILLS_DIR / Path(repo)


def window(config: Config, angle: str, limit: int) -> list[str]:
    """The next `limit` skills still missing the angle, in catalog order. A skill whose
    repository is already on disk without a source for it can never be built, so it is skipped
    forever; `0` means no cap. The count is work, not positions."""
    out_name = common.ANGLE_FILES[angle]
    work: list[str] = []
    for skill in catalog_ids(config):
        if (common.skill_dir(config, skill) / out_name).is_file():
            continue
        if repo_dir(config, repo_of(skill)).is_dir() and not \
                common.skill_md_path(config, skill).is_file():
            continue
        work.append(skill)
        if limit and len(work) >= limit:
            break
    return work


# ------------------------------------------------------------------------- the downloads


class Downloader:
    """One GET per file, streamed, retried on the shared reading. A `file://` URL is a local copy
    with no client - the offline suite's tarballs and listing - so a test never builds an HTTP
    client."""

    def __init__(self, config: Config):
        self.config = config
        self._client: httpx.Client | None = None

    def _http(self) -> httpx.Client:
        if self._client is None:
            # the connect waits on the timeout; a tarball's read is allowed to take its time
            self._client = httpx.Client(
                follow_redirects=True, timeout=httpx.Timeout(self.config.timeout, read=None))
        return self._client

    def get(self, url: str, dest: Path) -> None:
        if urlsplit(url).scheme == "file":
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(urlsplit(url).path, dest)  # a missing local file is a failed fetch
            return
        attempt = 0
        while True:
            try:
                with self._http().stream("GET", url) as response:
                    response.raise_for_status()
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    with dest.open("wb") as out:
                        for chunk in response.iter_bytes():
                            out.write(chunk)
                return
            except httpx.HTTPError as error:
                if attempt >= self.config.max_retries or not common.worth_retrying(error):
                    raise
                attempt += 1
                time.sleep(2 ** attempt)

    def close(self) -> None:
        if self._client is not None:
            self._client.close()

    def __enter__(self) -> "Downloader":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


def download_repos(config: Config, repos: list[str], template: str, jobs: int,
                   downloader: Downloader, stage: Path) -> None:
    """Download each repository's tarball into `stage`, `jobs` at a time; one that fails is named
    and left out - its skills fail below and the next run retries them."""
    def one(repo: str) -> tuple[str, str] | None:
        owner, _, name = repo.partition("/")
        url = template.replace("{owner}", owner).replace("{repo}", name)
        try:
            downloader.get(url, stage / f"{owner}_{name}.tgz")
        except (httpx.HTTPError, OSError) as error:
            return repo, f"{type(error).__name__}: {error}"
        return None

    with ThreadPoolExecutor(max_workers=jobs) as pool:
        failures = [result for result in pool.map(one, repos) if result is not None]
    for repo, detail in failures:
        print(f"failed to fetch: {repo} ({detail})", file=sys.stderr)


def ensure_repositories(config: Config, skills: list[str], template: str, jobs: int,
                        downloader: Downloader) -> None:
    """Download the window's repositories that are not cached, then unpack every tarball once."""
    repos = sorted({repo_of(skill) for skill in skills
                    if not repo_dir(config, repo_of(skill)).is_dir()})
    if not repos:
        return
    with tempfile.TemporaryDirectory(prefix="skills-tarballs-") as tmp:
        stage = Path(tmp)
        download_repos(config, repos, template, jobs, downloader, stage)
        taken, processed = fetch.extract(stage, config)
    print(f"fetched {taken} skill(s) from {processed} repository tarball(s)", file=sys.stderr)


# ----------------------------------------------------------------------------- the pool


def build_one(angle: str, skill: str) -> bool:
    """Run one producer process on one skill. Its stderr is the job's whole output: forwarded on
    success, handed to GEN_ERR_LOG on failure beside the FAIL_LOG line CI groups partial runs by.
    """
    script = Path(__file__).resolve().parent / ANGLE_SCRIPT[angle]
    result = subprocess.run([sys.executable, str(script), skill],
                            capture_output=True, text=True, check=False)
    if result.returncode == 0:
        sys.stderr.write(result.stderr)
        return True
    with _log_lock:
        fail_log = os.environ.get("FAIL_LOG")
        if fail_log:
            with open(fail_log, "a", encoding="utf-8") as out:
                out.write(f"FAILED {ANGLE_LABEL[angle]} {skill}\n")
        error_log = os.environ.get("GEN_ERR_LOG")
        if error_log:
            with open(error_log, "a", encoding="utf-8") as out:
                out.write(result.stderr)
    print(f"failed: {skill}", file=sys.stderr)
    return False


def build(config: Config, angle: str, limit: int, jobs: int, fetch_jobs: int,
          template: str) -> int:
    """One batch: window, lazy fetch, pool. Returns 0 - partial output is published output."""
    skills = window(config, angle, limit)
    if not skills:
        print(f"nothing to build: every skill is done for its {common.ANGLE_FILES[angle]}",
              file=sys.stderr)
        return 0
    with Downloader(config) as downloader:
        ensure_repositories(config, skills, template, fetch_jobs, downloader)
    skills = [skill for skill in skills if common.skill_md_path(config, skill).is_file()]
    if not skills:
        print("nothing to build: the window's repositories hold no source", file=sys.stderr)
        return 0
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        futures = [pool.submit(build_one, angle, skill) for skill in skills]
        done = sum(future.result() for future in as_completed(futures))
    print(f"done {done}/{len(skills)} {ANGLE_LABEL[angle]}", file=sys.stderr)
    return 0


# ------------------------------------------------------------------------------ clean


def clean(config: Config, angle: str, limit: int) -> int:
    """The inverse of `build`: delete the angle's files from the first `limit` built skills in
    catalog order (0 = every one). `all` forgets both angles' files. Deleting is local and cheap,
    so it runs in this loop rather than the pool."""
    names = (list(common.ANGLE_FILES.values()) if angle == "all"
             else [common.ANGLE_FILES[angle]])
    window: list[list[Path]] = []
    for skill in catalog_ids(config):
        files = [common.skill_dir(config, skill) / name for name in names]
        if any(path.is_file() for path in files):
            window.append(files)
            if limit and len(window) >= limit:
                break
    if not window:
        print(f"nothing to clean: no built {angle} output in the catalog", file=sys.stderr)
        return 0
    removed = 0
    for files in window:
        for path in files:
            if path.is_file():
                path.unlink()
                removed += 1
    print(f"cleaned {removed} {angle} output file(s) from {len(window)} skill(s)", file=sys.stderr)
    return 0


# ------------------------------------------------------------------------------ sync


def sync(config: Config, listing_url: str, template: str, fetch_jobs: int) -> int:
    """Reconcile with the mirror: pull its listing, refetch every on-disk repository it adds a
    skill to, merge the new sources in, and rewrite the catalog last. A listing that does not
    download changes nothing."""
    with tempfile.TemporaryDirectory(prefix="skills-sync-") as tmp:
        tmp_dir = Path(tmp)
        listing = tmp_dir / "listing.jsonl"
        with Downloader(config) as downloader:
            try:
                downloader.get(listing_url, listing)
            except (httpx.HTTPError, OSError) as error:
                raise BatchError(
                    f"{listing_url}: {type(error).__name__}: {error}") from error
            old = set(read_ids(config.output_dir / common.INDEX)) \
                if (config.output_dir / common.INDEX).is_file() else set()
            new = set(read_ids(listing))
            # a repository a skill was just added to, already fetched once: refetch and merge
            repos = sorted(repo for repo in {repo_of(skill) for skill in new - old}
                           if repo_dir(config, repo).is_dir())
            if repos:
                stage = tmp_dir / "stage"
                download_repos(config, repos, template, fetch_jobs, downloader, stage)
                taken, processed = fetch.extract(stage, config)
                print(f"fetched {taken} skill(s) from {processed} repository tarball(s)",
                      file=sys.stderr)
        catalog, pages = index.build(config, listing)
    print(f"indexed -> {catalog}", file=sys.stderr)
    print(f"readme -> {', '.join(str(page) for page in pages)}", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Window the catalog, fetch the window's repositories, build one angle.")
    sub = parser.add_subparsers(dest="command", required=True)

    build_parser = sub.add_parser("build", help="build the missing angle for the next skills")
    build_parser.add_argument("angle", choices=[common.DOMAIN_ANGLE, common.SKILL_ZH_ANGLE])
    build_parser.add_argument("--limit", type=int, default=1,
                              help="skills per run, most installed first; 0 = all")
    build_parser.add_argument("--jobs", type=int, default=32, help="calls in flight at once")
    build_parser.add_argument("--fetch-jobs", dest="fetch_jobs", type=int, default=16,
                              help="repository tarballs in flight at once")
    build_parser.add_argument("--repo-tarball", dest="repo_tarball",
                              default=DEFAULT_REPO_TARBALL,
                              help="template with {owner} and {repo} for a repository tarball")

    clean_parser = sub.add_parser("clean", help="delete the angle's files from the first built skills")
    clean_parser.add_argument("angle",
                              choices=[common.DOMAIN_ANGLE, common.SKILL_ZH_ANGLE, "all"])
    clean_parser.add_argument("--limit", type=int, default=1,
                              help="built skills to forget, in catalog order; 0 = every one")

    sync_parser = sub.add_parser("sync", help="reconcile with the mirror: listing, sources, index")
    sync_parser.add_argument("--listing", default=DEFAULT_LISTING,
                             help="the mirror's listing URL (file:// works offline)")
    sync_parser.add_argument("--fetch-jobs", dest="fetch_jobs", type=int, default=16)
    sync_parser.add_argument("--repo-tarball", dest="repo_tarball",
                             default=DEFAULT_REPO_TARBALL)

    args = parser.parse_args(argv)
    config = Config()
    try:
        if args.command == "build":
            return build(config, args.angle, args.limit, args.jobs, args.fetch_jobs,
                         args.repo_tarball)
        if args.command == "clean":
            return clean(config, args.angle, args.limit)
        return sync(config, args.listing, args.repo_tarball, args.fetch_jobs)
    except BatchError as error:
        print(error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
