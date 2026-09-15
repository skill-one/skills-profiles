"""Fetch the skill dataset (the scraper's dist branch) once, then read it locally.

`sync` downloads the whole branch as one tarball and unpacks into <data_dir> only
what a run reads: skills.jsonl plus every skills/<id>/SKILL.md. One request still
fetches the whole branch, so index and sources can never drift apart, and every
later read is a local file read.

Upstream publishes each daily scrape as a `<branch>-<date>` tag and keeps a
one-line `latest` pointer naming the newest of them. A sync reads that pointer,
records the tag it fetched in <data_dir>/SNAPSHOT.json and re-downloads only
when the newest tag differs, so repeat syncs (locally, or in CI behind a cache)
cost one small request instead of the whole snapshot.
"""

import json
import logging
import re
import shutil
import tarfile
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

import httpx

from .config import DIST_BRANCH, LATEST_URL, TARBALL_URL, Settings, tarball_url
from .layout import INDEX_NAME, SKILLS_SUBDIR, skill_dir_name
from .models import SkillRecord
from .outputs import load_hashes

logger = logging.getLogger(__name__)

SKILL_MD = "SKILL.md"
MARKER_NAME = "SNAPSHOT.json"  # which upstream ref the local snapshot holds
# what the pointer is allowed to hold: a `<branch>-<date>` tag. Anything else
# (a 404 page, a half-written file) is not a ref a download could use
TAG_PATTERN = re.compile(rf"^{DIST_BRANCH}-\d{{4}}-\d{{2}}-\d{{2}}$")
MAX_DOWNLOAD_RETRIES = 3
MD_MAX_CHARS = 20000  # cap on the SKILL.md text sent to the LLM


@dataclass(frozen=True)
class SyncReport:
    """What one sync did, for the CLI summary.

    `tag` is the snapshot ref now on disk (an upstream `<branch>-<date>` tag, or
    the branch itself when upstream publishes no tags); `downloaded` False means
    the local snapshot was already at `tag` and nothing was fetched;
    `seconds` times the download pass, 0 on a cache hit.
    """

    data_dir: Path
    tag: str
    downloaded: bool
    seconds: float


def _not_published() -> RuntimeError:
    return RuntimeError(
        f"'{DIST_BRANCH}' branch is not published at {TARBALL_URL} yet - "
        "the upstream daily scrape is still running; retry `skills-profiles sync` later"
    )


def url_without_query(url: str) -> str:
    """`url` minus its query string, for logs.

    A generated image's presigned url carries a short-lived security token and a
    signature in its query, and a 1.7 KB line per attempt also buries the log.
    """
    return url.split("?", 1)[0]


def download_file(url: str, dest: Path, timeout: float | None = None) -> bool:
    """Download url into dest atomically, retrying with exponential backoff.

    Shared by `sync` (snapshot tarballs) and by the cover renderer (generated
    images, whose provider url expires within the hour). False means "no such
    file" (HTTP 404); a failure that survives all retries raises RuntimeError.
    `timeout` bounds a single attempt: a caller that holds a concurrency slot
    while downloading cannot afford an attempt that never finishes.
    """
    partial = dest.with_name(dest.name + ".part")
    safe_url = url_without_query(url)
    last_error: Exception | None = None
    for attempt in range(1, MAX_DOWNLOAD_RETRIES + 1):
        try:
            logger.info("Downloading %s (attempt %d/%d)", safe_url, attempt,
                            MAX_DOWNLOAD_RETRIES)
            start = time.monotonic()
            # stream so a 100+ MB snapshot never lands in memory, and so the
            # bytes go straight to the partial file the caller can rename
            with httpx.stream("GET", url, timeout=timeout, follow_redirects=True) as response:
                if response.status_code == 404:
                    logger.warning("No content at %s", safe_url)
                    partial.unlink(missing_ok=True)
                    return False
                response.raise_for_status()
                with open(partial, "wb") as out:
                    for chunk in response.iter_bytes():
                        out.write(chunk)
            logger.info("Downloaded %s in %.1fs", safe_url, time.monotonic() - start)
            partial.replace(dest)
            return True
        except (httpx.HTTPError, OSError) as e:
            last_error = e
        logger.warning("Download failed: %s", last_error)
        if attempt < MAX_DOWNLOAD_RETRIES:
            time.sleep(2 ** attempt)
    partial.unlink(missing_ok=True)
    raise RuntimeError(
        f"Failed to download {safe_url} after {MAX_DOWNLOAD_RETRIES} attempts: {last_error}"
    ) from last_error


def _download_snapshot(url: str, dest: Path) -> bool:
    """Replace dest with the tarball's contents; False means "nothing published yet".

    The archive is unpacked next to itself first, so a failed download or a
    corrupt archive leaves whatever is already in dest untouched.
    """
    with tempfile.TemporaryDirectory() as tmp:
        archive = Path(tmp) / "snapshot.tar.gz"
        if not download_file(url, archive):
            return False
        unpacked = Path(tmp) / "unpacked"
        with tarfile.open(archive, "r:gz") as tar:
            tar.extractall(unpacked, members=_snapshot_files(tar), filter="data")
        shutil.rmtree(dest, ignore_errors=True)
        shutil.move(str(_snapshot_root(unpacked)), str(dest))
    return True


def _snapshot_files(tar: tarfile.TarFile):
    """The archive members worth unpacking: the index and every SKILL.md.

    The branch mirrors whole skill repos, and only these two kinds of files are
    ever read — keeping the rest (READMEs, evals, manifests, other markdown)
    would unpack ~70x more data than a run needs, on every single sync.
    """
    for member in tar:
        rel = member.name.split("/", 1)[-1]  # drop GitHub's <repo>-<branch>/ root
        if rel == INDEX_NAME or (
            rel.startswith(f"{SKILLS_SUBDIR}/") and rel.endswith(f"/{SKILL_MD}")
        ):
            yield member


def _snapshot_root(unpacked: Path) -> Path:
    """GitHub archives wrap the branch contents in one <repo>-<branch>/ dir."""
    entries = list(unpacked.iterdir())
    return entries[0] if len(entries) == 1 and entries[0].is_dir() else unpacked


def latest_dist_tag() -> str | None:
    """The `<branch>-<date>` tag upstream's `latest` pointer names, or None.

    One tiny request answers "does a sync have anything to do" — the pointer is
    the file upstream's own publisher asserts equals its newest tag. Reading it
    can fail for reasons that are not a sync's business (no pointer yet, a
    network blip, a cached error page), and the fallback ref — the branch — is
    always downloadable, so a failure only costs the shortcut, never the sync.
    """
    try:
        response = httpx.get(LATEST_URL, timeout=30, follow_redirects=True)
        pointer = response.text.strip()
    except (httpx.HTTPError, OSError) as e:  # never fail a sync over this
        logger.warning("Could not read %s: %s", LATEST_URL, e)
        return None
    if not TAG_PATTERN.match(pointer):
        logger.warning("%s holds %r, not a %s-<date> tag", LATEST_URL, pointer[:60], DIST_BRANCH)
        return None
    return pointer


def read_marker(data_dir: Path) -> dict:
    """What the local snapshot holds: {"ref": ..., "fetched_at": ...}; {} if unknown."""
    try:
        return json.loads((data_dir / MARKER_NAME).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write_marker(data_dir: Path, ref: str) -> None:
    (data_dir / MARKER_NAME).write_text(
        json.dumps({"ref": ref,
                    "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
                   indent=2) + "\n",
        encoding="utf-8",
    )


def _is_current(data_dir: Path, ref: str) -> bool:
    """Whether <data_dir> already holds `ref`.

    Only a tag can answer that: a branch name says nothing about its content, so
    the branch always has to be downloaded again.
    """
    if ref == DIST_BRANCH or not (data_dir / INDEX_NAME).is_file():
        return False
    return read_marker(data_dir).get("ref") == ref


def sync_data(settings: Settings, refresh: bool = False) -> SyncReport:
    """Bring <data_dir> to the newest upstream snapshot.

    One request downloads the whole branch as a tarball, of which only the index
    and the SKILL.md files are unpacked; the previous snapshot is replaced
    wholesale, so there is nothing incremental to fetch or to expire. Upstream
    tags each daily scrape: when the local snapshot already holds the newest
    tag, nothing is downloaded unless `refresh` says otherwise. Sync is a pure
    data operation — it never touches the generated results; invalidating stale
    ones is `invalidate --stale`'s explicit job (see stale_result_ids).
    Returns a SyncReport (tag, whether a download happened, duration).
    """
    data_dir = settings.data_dir
    if (data_dir.exists() and any(data_dir.iterdir())
            and not (data_dir / INDEX_NAME).exists()):
        raise RuntimeError(
            f"{data_dir} exists and is not a dataset directory - move it away or "
            "point SKILLS_PROFILES_DATA_DIR at a different directory"
        )
    ref = latest_dist_tag() or DIST_BRANCH
    if not refresh and _is_current(data_dir, ref):
        logger.info("Already at %s - nothing to download", ref)
        return SyncReport(data_dir=data_dir, tag=ref, downloaded=False, seconds=0.0)

    start = time.monotonic()
    data_dir.parent.mkdir(parents=True, exist_ok=True)
    # only a 404 (the ref is gone) means "nothing published yet"; any other
    # download failure raises with its real cause instead of being relabelled
    if not _download_snapshot(tarball_url(ref), data_dir):
        raise _not_published()
    _write_marker(data_dir, ref)
    return SyncReport(
        data_dir=data_dir, tag=ref, downloaded=True, seconds=time.monotonic() - start,
    )


def stale_result_ids(settings: Settings, skills: list[SkillRecord] | None = None) -> list[str]:
    """Cached skills whose recorded content hash no longer matches the snapshot.

    A skill is stale when upstream changed its content (the freshly downloaded
    snapshot holds a different hash) or when it disappeared from the index.
    Nothing calls this automatically: `invalidate --stale` is the explicit path.
    `skills` lets a caller that already read the whole index reuse it; it must be
    the full list, not the `portfolio` window, or an out-of-window skill would be
    mistaken for a deleted one.
    """
    upstream = {s.id: s.hash for s in (skills if skills is not None else load_skills(settings))}
    hashes = load_hashes(settings)
    return sorted(sid for sid, h in hashes.items() if upstream.get(sid) != h)


def load_skills(settings: Settings) -> list[SkillRecord]:
    """Every skill that has SKILL.md content upstream, most installed first.

    Reads the local snapshot: `skill_md` stays empty until `read_skill_md` fills
    it in, which a run does just for the skills it really generates. Narrowing
    the run is `generate.select_skills`'s job (see `--limit`).
    """
    index = settings.data_dir / INDEX_NAME
    if not index.is_file():
        raise FileNotFoundError(
            f"{INDEX_NAME} not found under {settings.data_dir} - "
            "run `skills-profiles sync` first"
        )

    records: list[SkillRecord] = []
    for line in index.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        entry = json.loads(line)
        # content is saved iff the scraper recorded a content hash
        if not entry.get("hash"):
            continue
        # the index's prose fields (name, description, source) are ignored: the
        # prompt template reads SKILL.md, which already carries them
        records.append(
            SkillRecord(
                id=entry["id"],
                installs=int(entry.get("installs") or 0),
                hash=entry.get("hash", ""),
            )
        )
    records.sort(key=lambda r: r.installs, reverse=True)
    return records


def portfolio(settings: Settings, skills: list[SkillRecord]) -> list[SkillRecord]:
    """The skills the pipeline serves: the most installed `settings.total_limit` of them.

    `load_skills` returns the whole snapshot in install order; this is the single
    place the dataset ceiling (`SKILLS_PROFILES_TOTAL_LIMIT`) is applied, so
    `run` stops at the top N, for profiles and pictures alike. It is a
    rank window, not a "count what got done" quota: a top skill with no recipe
    yet, or a failed render, holds its slot rather than letting a lower skill
    take its place, so `invalidate`-driven redraws reuse the same N skills.

    Deliberately *not* folded into `load_skills`: `sync` and `invalidate --stale`
    must still see the whole index, so a profiled skill that later slips past the
    window is compared against its real upstream hash, not mistaken for a
    deleted one. total_limit <= 0 serves every skill.
    """
    return skills if settings.total_limit <= 0 else skills[:settings.total_limit]


def skill_md_path(settings: Settings, skill: SkillRecord) -> Path:
    """Where one skill's SKILL.md sits in the snapshot."""
    return settings.data_dir / SKILLS_SUBDIR / skill_dir_name(skill.id) / SKILL_MD


def read_skill_md(settings: Settings, skill: SkillRecord) -> str | None:
    """One skill's SKILL.md text from the local snapshot.

    None when the snapshot has no source for it — a skill listed in skills.jsonl
    whose content the scraper could not save.
    """
    path = skill_md_path(settings, skill)
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8", errors="replace")[:MD_MAX_CHARS]
