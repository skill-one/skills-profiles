#!/usr/bin/env python3
"""The batch driver: window the catalog, fetch the window's repositories, build one angle.

The justfile is a thin launcher of this script. It owns the three things that used to be shell:
walking `skills.jsonl` (parsed as jsonl, never sed'ed) to pick the next `limit` skills still
missing the angle, fetching each repository just in time (the repository directory is the cache:
one download, unpacked by the first job that touches it), and the `jobs`-wide pool that runs the
producers - one call into a producer module per skill, in this process. `sync` is the other
subcommand: reconcile with the mirror - pull its listing, refetch the repositories it adds a skill
to, and rewrite the catalog last. `meta` is the third: the same catalog read as repositories and
owners, one GitHub fetch each - every repository missing a row and every owner missing an avatar;
`--clean` forgets them instead.

A failed job never ends the run: the skill is named on stderr and, when CI gives the paths, in
FAIL_LOG/GEN_ERR_LOG, and the next run retries exactly it - its angle file is still missing. A
run whose every job failed is a broken run and says so in its exit status.

    batch.py build <angle> --limit N --jobs N [--repo-tarball URL]
    batch.py clean <angle> --limit N        # the inverse: forget the first N built outputs
    batch.py meta [--clean]                 # the entity catalog and the owner avatars, both ways
    batch.py sync --listing URL [--repo-tarball URL]
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
import threading
import traceback
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from importlib import import_module
from pathlib import Path

import httpx

import common
import fetch
import index
import meta
from common import Config, Downloader

DEFAULT_LISTING = ("https://raw.githubusercontent.com/skill-one/"
                   "skills-sh-mirror/dist/skills.jsonl")
DEFAULT_REPO_TARBALL = "https://codeload.github.com/{owner}/{repo}/tar.gz/HEAD"

# the producers are plain modules: one pool job is one call into one of them
ANGLE_MODULE = {common.DOMAIN_ANGLE: "jev", common.SKILL_ZH_ANGLE: "skill_zh"}
ANGLE_LABEL = {common.DOMAIN_ANGLE: "domain", common.SKILL_ZH_ANGLE: "zh page"}

# FAIL_LOG/GEN_ERR_LOG are append-only CI handovers; workers append from threads.
_log_lock = threading.Lock()

# a repository GitHub answers 404/410 for is gone for good - deleted or made private. Its
# repository directory is still created as the cache marker, so the window skips its skills on
# every later run instead of refetching and failing them again.
GONE_STATUSES = frozenset({404, 410})


class BatchError(Exception):
    """A fatal batch error: one stderr line and exit 1, never a traceback."""


# --------------------------------------------------------------------------- the catalog


def read_ids(path: Path) -> list[str]:
    """The skill ids in one jsonl file, in its own order; a line that is not json is a hard
    error rather than a silently empty catalog."""
    try:
        rows = common.read_jsonl(path)
    except ValueError as error:
        raise BatchError(f"{error} - run `just sync` first") from error
    return [row["id"] for row in rows if isinstance(row.get("id"), str)]


def catalog_rows(config: Config) -> list[dict]:
    """The catalog's rows in the batch's own order - the mirror's, installs descending - each
    carrying the `dir` its files live at (null while the repository has not been fetched) and
    the `name` the tree resolves a still-unfetched skill by."""
    path = config.output_dir / common.INDEX
    if not path.is_file():
        raise BatchError(f"no catalog under {config.output_dir} - run `just sync` first")
    try:
        rows = common.read_jsonl(path)
    except ValueError as error:
        raise BatchError(str(error)) from error
    rows = [row for row in rows if isinstance(row.get("id"), str)]
    if not rows:
        raise BatchError("the catalog lists no skill")
    return rows


def repo_of(skill: str) -> str:
    """A skill's `owner/repo`, the unit a tarball is downloaded and cached in."""
    owner, repo, _slug = skill.split("/", 2)
    return f"{owner}/{repo}"


def repo_dir(config: Config, repo: str) -> Path:
    return config.output_dir / common.SKILLS_DIR / Path(repo)


def window(config: Config, angles: list[str], limit: int, dirs: common.SkillDirs) -> list[dict]:
    """The next `limit` catalog rows still missing at least one of the angles, in catalog order.
    A row's files live at its `dir`; a row fetched without a source carrying its `name` can never
    be built, so it is skipped forever; `0` means no cap. The count is work, not positions."""
    names = [common.ANGLE_FILES[angle] for angle in angles]
    work: list[dict] = []
    for row in catalog_rows(config):
        repo = repo_of(row["id"])
        dir_path = row.get("dir")
        if dir_path and all((common.skill_dir(config, dir_path) / name).is_file()
                            for name in names):
            continue
        if repo_dir(config, repo).is_dir():
            # the repository is fetched: the row resolves now or never
            if not dir_path and isinstance(row.get("name"), str):
                dir_path = dirs.find(repo, row["name"])
            if dir_path is None or not common.skill_md_path(config, dir_path).is_file():
                continue
            row["dir"] = dir_path
        work.append(row)
        if limit and len(work) >= limit:
            break
    return work


# ------------------------------------------------------------------------- the downloads


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


class LazyFetcher:
    """The repositories a batch needs, fetched the first time a job touches one.

    The pool hands every job this fetcher: the first job to need a repository starts its one
    download (bounded by `fetch_jobs`), every later job on the same repository waits on that one
    result - so a whole-snapshot run unpacks sources as it produces instead of fetching every
    tarball up front, and a repository is still downloaded exactly once: the directory on disk is
    the cache. A repository that will not download is named once and fails only its own skills;
    one GitHub answers 404/410 for is gone for good - its directory is left as the marker, so its
    skills are skipped, not failed.
    """

    def __init__(self, config: Config, template: str, fetch_jobs: int):
        self.config = config
        self.template = template
        self._pool = ThreadPoolExecutor(max_workers=max(fetch_jobs, 1))
        self._futures: dict[str, Future[str | None]] = {}
        self._lock = threading.Lock()
        self._taken = 0
        self._processed = 0

    def ensure(self, repo: str) -> str | None:
        """The repository unpacked under the tree, or the error that stopped it."""
        with self._lock:
            future = self._futures.get(repo)
            if future is None:
                future = self._pool.submit(self._one, repo)
                self._futures[repo] = future
        return future.result()

    def _one(self, repo: str) -> str | None:
        owner, _, name = repo.partition("/")
        url = self.template.replace("{owner}", owner).replace("{repo}", name)
        try:
            with tempfile.TemporaryDirectory(prefix="skills-tarballs-") as tmp:
                tarball = Path(tmp) / f"{owner}_{name}.tgz"
                with Downloader(self.config) as downloader:
                    downloader.get(url, tarball)
                taken = fetch.extract_tarball(tarball, self.config)
        except (httpx.HTTPError, OSError) as error:
            detail = f"{type(error).__name__}: {error}"
            if isinstance(error, httpx.HTTPStatusError) and \
                    error.response.status_code in GONE_STATUSES:
                repo_dir(self.config, repo).mkdir(parents=True, exist_ok=True)
                print(f"gone: {repo} ({detail})", file=sys.stderr)
                return None
            print(f"failed to fetch: {repo} ({detail})", file=sys.stderr)
            return detail
        with _log_lock:
            self._taken += taken
            self._processed += 1
        return None

    def close(self) -> None:
        self._pool.shutdown()
        if self._processed:
            print(f"fetched {self._taken} skill(s) from {self._processed} repository tarball(s)",
                  file=sys.stderr)

    def __enter__(self) -> LazyFetcher:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


# ----------------------------------------------------------------------------- the pool


def build_one(config: Config, angle: str, row: dict, fetcher: LazyFetcher,
              dirs: common.SkillDirs) -> str:
    """Run one producer in this process on one catalog row: "built", "skipped" - its repository
    holds no source carrying its `name`, so it can never be built and the window skips it next
    time - or "failed". A failure - a repository that will not download, any producer exception, a
    SystemExit for a missing key included - is one stderr line here and the traceback in
    GEN_ERR_LOG beside the FAIL_LOG line CI groups partial runs by."""
    repo = repo_of(row["id"])
    detail: str
    dir_path = row.get("dir")
    # the repository directory on disk is the cache: there means fetched
    error = None if repo_dir(config, repo).is_dir() else fetcher.ensure(repo)
    if dir_path is None and error is None and isinstance(row.get("name"), str):
        dir_path = dirs.find(repo, row["name"])
    if error is None and dir_path and common.skill_md_path(config, dir_path).is_file():
        try:
            import_module(ANGLE_MODULE[angle]).main([dir_path])
        except (Exception, SystemExit):  # a producer failure is data, not a crash
            detail = traceback.format_exc()
        else:
            return "built"
    elif error is not None:
        detail = f"failed to fetch: {repo} ({error})"
    else:
        return "skipped"
    with _log_lock:
        fail_log = os.environ.get("FAIL_LOG")
        if fail_log:
            with open(fail_log, "a", encoding="utf-8") as out:
                out.write(f"FAILED {ANGLE_LABEL[angle]} {row['id']}\n")
        error_log = os.environ.get("GEN_ERR_LOG")
        if error_log:
            with open(error_log, "a", encoding="utf-8") as out:
                out.write(detail)
    print(f"failed: {row['id']}", file=sys.stderr)
    return "failed"


def build(config: Config, angle: str, limit: int, jobs: int, fetch_jobs: int,
          template: str) -> int:
    """One batch: window, pool, each job fetching its repository just in time. Partial output is
    published output, so the run is 0 while something was built or nothing could be; a window
    whose every job failed is a broken run and is 1."""
    angles = [common.DOMAIN_ANGLE, common.SKILL_ZH_ANGLE] if angle == "all" else [angle]
    dirs = common.SkillDirs(config)
    skills = window(config, angles, limit, dirs)
    if not skills:
        print(f"nothing to build: every skill is done for {angle}", file=sys.stderr)
        return 0
    jobs_list = [(a, row) for row in skills for a in angles
                 if not (row.get("dir") and common.angle_path(config, row["dir"], a).is_file())]
    if not jobs_list:
        print(f"nothing to build: no missing {angle} output in the window", file=sys.stderr)
        return 0
    with LazyFetcher(config, template, fetch_jobs) as fetcher, \
            ThreadPoolExecutor(max_workers=jobs) as pool:
        futures = [pool.submit(build_one, config, a, row, fetcher, dirs)
                   for a, row in jobs_list]
        results = [future.result() for future in as_completed(futures)]
    built, failed = results.count("built"), results.count("failed")
    print(f"done {built}/{len(jobs_list)} {angle} output(s)", file=sys.stderr)
    return 1 if built == 0 and failed else 0


# ------------------------------------------------------------------------------ clean


def clean(config: Config, angle: str, limit: int) -> int:
    """The inverse of `build`: delete the angle's files from the first `limit` built skills in
    catalog order (0 = every one). `all` forgets both angles' files. Deleting is local and cheap,
    so it runs in this loop rather than the pool."""
    names = (list(common.ANGLE_FILES.values()) if angle == "all"
             else [common.ANGLE_FILES[angle]])
    window: list[list[Path]] = []
    for row in catalog_rows(config):
        dir_path = row.get("dir")
        if not dir_path:
            continue
        files = [common.skill_dir(config, dir_path) / name for name in names]
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


# ------------------------------------------------------------------------------ meta

# The entity fetches run this wide; unlike a producer pool, there is no per-run knob for it.
META_JOBS = 32


def repo_roster(config: Config) -> list[str]:
    """The distinct repositories the catalog names, in its own order - a skill id's first two
    segments, deduped, the roster a meta run works."""
    seen: list[str] = []
    for row in catalog_rows(config):
        repo = repo_of(row["id"])
        if repo not in seen:
            seen.append(repo)
    return seen


def repo_rows(config: Config) -> dict[str, dict]:
    """The repositories already resolved, keyed by id - an absent row is the work left to do."""
    path = common.repos_index_path(config)
    if not path.is_file():
        return {}
    try:
        rows = common.read_jsonl(path)
    except ValueError as error:
        raise BatchError(str(error)) from error
    return {row["id"]: row for row in rows if isinstance(row.get("id"), str)}


def write_repo_rows(config: Config, rows: list[dict]) -> Path:
    """Write the repository catalog whole, renamed into place: a half-written one reads as a whole
    one. Compact, like `skills.jsonl` beside it."""
    text = "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n"
                   for row in rows)
    return common.write_atomic(common.repos_index_path(config), text)


def repo_result(config: Config, repo: str, downloader: Downloader) -> dict | None:
    """Fetch one repository to its row; one GitHub has no answer for becomes a `gone` row, and any
    other failure is one stderr line and nothing - so the next run retries exactly it."""
    try:
        return meta.build_repo(config, repo, downloader)
    except (httpx.HTTPError, OSError, ValueError) as error:
        if isinstance(error, httpx.HTTPStatusError) and error.response.status_code in GONE_STATUSES:
            print(f"gone: {repo} ({error})", file=sys.stderr)
            return meta.repo_gone_row(repo)
        print(f"failed: {repo} ({type(error).__name__}: {error})", file=sys.stderr)
        return None


def meta_window(config: Config, resolved: dict[str, dict]) -> list[str]:
    """The repositories to fetch, in catalog order: those without a row, plus one live repository of
    every owner still without an avatar - the owner is read from its repository's payload, so one
    call serves both. `live` skips a repository already known to be gone, so the representative is
    one that can still answer."""
    roster = repo_roster(config)
    need = {repo for repo in roster if repo not in resolved}
    representative: dict[str, str] = {}
    for repo in roster:
        owner = repo.split("/", 1)[0]
        row = resolved.get(repo)
        if owner not in representative and (row is None or not row.get("gone")):
            representative[owner] = repo
    for owner, repo in representative.items():
        if not common.owner_avatar_path(config, owner).is_file():
            need.add(repo)
    return [repo for repo in roster if repo in need]


def build_meta(config: Config) -> int:
    """Fetch the repositories the catalog names that are missing a row, and one live repository of
    every owner still without an avatar - the `/repos` payload carries the owner, so its avatar lands
    as the repository is fetched. The rows merge into `repos.jsonl` in catalog order; a repository
    GitHub has no answer for gets a `gone` row. A run whose every fetch failed is 1."""
    roster = repo_roster(config)
    resolved = repo_rows(config)
    window = meta_window(config, resolved)
    if not window:
        print("nothing to build: every entity is done", file=sys.stderr)
        return 0
    with Downloader(config, headers=meta.headers(config)) as downloader, \
            ThreadPoolExecutor(max_workers=META_JOBS) as pool:
        fetched = list(pool.map(lambda repo: repo_result(config, repo, downloader), window))
    merged = dict(resolved)
    merged.update({repo: row for repo, row in zip(window, fetched, strict=True)
                   if row is not None})
    rows = [merged[repo] for repo in roster if repo in merged]
    if rows or resolved:
        write_repo_rows(config, rows)
    built = sum(1 for row in fetched if row is not None and not row["gone"])
    failed = sum(1 for row in fetched if row is None)
    print(f"done: {built} built, {failed} failed", file=sys.stderr)
    return 1 if built == 0 and failed else 0


def clean_meta(config: Config) -> int:
    """Forget every entity output: the repository catalog and the owner avatars. Existence is the
    cache, so this is the whole invalidation - the next `meta` rebuilds from nothing."""
    catalog = common.repos_index_path(config)
    if catalog.is_file():
        catalog.unlink()
    shutil.rmtree(config.output_dir / common.OWNERS_DIR, ignore_errors=True)
    print("cleaned the repository catalog and the owner avatars", file=sys.stderr)
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
            for skill in sorted(old - new):
                print(f"the mirror dropped {skill} - its files stay in the tree", file=sys.stderr)
            # a repository a skill was just added to, already fetched once: refetch and merge.
            # The catalog no longer lists a skill its repository yielded nothing for, so such a
            # row reads as new here and its repository is refetched - harmless, idempotent, and
            # the one path that recovers a skill its repository ships again.
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

    build_parser = sub.add_parser("build", help="build the missing angle(s) for the next skills")
    build_parser.add_argument(
        "angle", choices=[common.DOMAIN_ANGLE, common.SKILL_ZH_ANGLE, "all"],
        help="domain, skill_zh, or all: both angles in one pool, over the shared window")
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

    meta_parser = sub.add_parser(
        "meta", help="fetch the GitHub profile of the catalog's repositories and owners")
    meta_parser.add_argument("--clean", action="store_true",
                             help="forget the repository catalog and the owner avatars instead")

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
        if args.command == "meta":
            return clean_meta(config) if args.clean else build_meta(config)
        return sync(config, args.listing, args.repo_tarball, args.fetch_jobs)
    except BatchError as error:
        print(error, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
