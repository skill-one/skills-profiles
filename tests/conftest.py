"""Shared fixtures and helpers: an isolated workdir with a small fake snapshot on
disk, so no test touches the network."""

import json
import tarfile
import tempfile
from pathlib import Path

import pytest

import common

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ["justfile", "batch.py", "common.py", "fetch.py", "jev.py", "meta.py", "translate.py",
           "skill_zh.py", "index.py", "readme.py"]
REPO_SHA = "abc1234"  # codeload names a repository tarball's root <repo>-<sha>
# the published root: the skill directories, the labels written about them, the mirror's own files
# and the catalog, which are the four things the justfile and the scripts all read
OUTPUT = Path("output")

# The fake mirror's own index: five skills with sources on disk, one without (its repository holds
# no skills/ directory, so the fetch yields nothing). The mirror carries no description and no
# content hash any more - a skill's own front matter is the only description, and the hash is
# computed here, over the fetched source.
SKILLS = [
    {"id": "owner-a/repo-a/alpha", "installs": "300",
     "description": "Tidies a note list, folds the loose ends into a running index, and keeps "
                    "the whole pile searchable."},
    {"id": "owner-b/repo-b/beta", "installs": "200",
     "description": "Drafts a release note from the merged pull requests, then trims it down to "
                    "the sentences a reader would actually care about."},
    {"id": "owner-c/repo-c/gamma", "installs": "100",
     "description": "Converts a table into CSV, guessing the delimiter and the encoding, and "
                    "reporting what it guessed instead of failing quietly."},
    {"id": "owner-h/repo-h/hotel:sub", "installs": "50",
     "description": "Books a hotel room for the dates in a sentence, then hands the confirmation "
                    "number back to whoever asked for it."},
    {"id": "owner-e/.dotcfg/settings", "installs": "40",
     "description": "Keeps dotfiles in order across machines, one file per tool, and no symlink "
                    "surprises on a new laptop."},
    {"id": "owner-d/repo-d/delta", "installs": "90"},
]


def skill_dir_name(skill_id: str) -> str:
    """Upstream writes `_` where an id carries a colon or an ampersand."""
    return skill_id.replace(":", "_").replace("&", "_")


def skill_md_text(entry: dict) -> str | None:
    """The SKILL.md the skill's own repository holds for one entry; None = the repository has none.
    The front matter `name` is the skill's own slug, the way real skills spell it."""
    if not entry.get("description"):
        return None
    return (f"---\nname: {entry['id'].rsplit('/', 1)[-1]}\n"
            f"description: {entry['description']}\n---\n\n"
            f"{entry['id']} does useful things.\n")


def index_row(entry: dict) -> dict:
    """One row of the mirror's listing: what upstream publishes for a skill, and no more."""
    return {name: entry[name] for name in ("id", "installs") if name in entry}


def catalog_row(entry: dict) -> dict:
    """One row of the catalog as this project publishes it: the mirror's fields, and no more - the
    fixture only has to carry the order and the installs the window reads."""
    return index_row(entry)


def skill_path(output: Path, skill_id: str) -> Path:
    """A skill's own directory in the tree: its SKILL.md alone, the way the lazy fetch leaves it."""
    return output / common.SKILLS_DIR / skill_dir_name(skill_id)


def profile_path(output: Path, skill_id: str) -> Path:
    """The skill's directory, seen from the generated side: the angles' files live beside the
    source page since the two travel together now."""
    return skill_path(output, skill_id)


def write_zh_page(output: Path, skill_id: str, description_zh: str) -> Path:
    """The zh page as skill_zh.py writes one: the front matter carries the Chinese description,
    the machine-assembled header a reader parses the translation back out of."""
    path = skill_path(output, skill_id) / "SKILL.zh.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"---\nname: {skill_id}\ndescription: {description_zh}\n---\n\n中文页面。\n",
                    encoding="utf-8")
    return path


def make_listing(path: Path, entries: list[dict] | None = None) -> Path:
    """The mirror's listing, as `just sync` pulls it: one `{id, installs}` row per skill."""
    entries = SKILLS if entries is None else entries
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(index_row(entry)) + "\n" for entry in entries),
                    encoding="utf-8")
    return path


def write_snapshot(output: Path, entries: list[dict] | None = None) -> None:
    """A snapshot already unpacked into the output tree, the way a lazy fetch leaves one: each
    skill's SKILL.md, its repository directory (the cache - nothing re-downloads it), and the
    catalog - the listing's only lasting trace - at the root. A listed skill its repository holds
    no source for is an empty directory, which is how the batch tells it from an unfetched one."""
    entries = SKILLS if entries is None else entries
    catalog = output / common.INDEX
    catalog.parent.mkdir(parents=True, exist_ok=True)
    catalog.write_text("".join(json.dumps(catalog_row(entry)) + "\n" for entry in entries),
                       encoding="utf-8")
    for entry in entries:
        owner, repo, _ = entry["id"].split("/")
        (output / common.SKILLS_DIR / owner / repo).mkdir(parents=True, exist_ok=True)
        text = skill_md_text(entry)
        if text:
            where = skill_path(output, entry["id"]) / common.SKILL_MD
            where.parent.mkdir(parents=True, exist_ok=True)
            where.write_text(text, encoding="utf-8")


def make_repo_tarballs(stage: Path, entries: list[dict] | None = None) -> Path:
    """The tarballs a window's lazy fetch downloads, one per repository in the listing, laid out for the
    recipe's `repo_tarball` template: <owner>_<repo>.tgz holding the repository's skills at
    `skills/<slug>/SKILL.md`, what the repository ships beside them, and a SKILL.md of its own at
    the root that belongs to no listed skill."""
    entries = SKILLS if entries is None else entries
    stage.mkdir(parents=True, exist_ok=True)
    repos: dict[tuple[str, str], list[dict]] = {}
    for entry in entries:
        owner, repo, _ = entry["id"].split("/")
        repos.setdefault((owner, repo), []).append(entry)
    for (owner, repo), group in repos.items():
        root = f"{repo}-{REPO_SHA}"
        files = {f"{root}/SKILL.md": f"# {repo}\n\nA repository readme, not a skill.\n"}
        for entry in group:
            text = skill_md_text(entry)
            if text:
                slug = entry["id"].split("/")[2]
                files[f"{root}/skills/{slug}/SKILL.md"] = text
                files[f"{root}/skills/{slug}/extra.md"] = "part of the skill repo\n"
        with tempfile.TemporaryDirectory() as tmp:
            packaged = Path(tmp) / "pack"
            for name, content in files.items():
                path = packaged / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
            with tarfile.open(stage / f"{owner}_{repo}.tgz", "w:gz") as tar:
                tar.add(packaged, arcname=root)
    return stage


def write_json_file(path: Path, payload: dict) -> None:
    """One json object on disk, the way the fake GitHub root serves it to `Downloader`."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def make_github_root(root: Path, entries: list[dict] | None = None) -> Path:
    """A local stand-in for the GitHub API, laid out for the `--github-api file://…` knob: a
    `repos/<owner>/<repo>` payload, a `users/<owner>` payload, and the avatar bytes its `avatar_url`
    points at. The payloads carry what `meta.py` reads, and nothing wider."""
    entries = SKILLS if entries is None else entries
    repos = sorted({"/".join(entry["id"].split("/")[:2]) for entry in entries})
    owners = sorted({entry["id"].split("/")[0] for entry in entries})
    for repo in repos:
        owner, name = repo.split("/")
        write_json_file(root / "repos" / owner / name,
                        {"full_name": repo, "description": f"A repository the test fakes: {name}.",
                         "stargazers_count": len(name) * 10,
                         "html_url": f"https://github.com/{repo}",
                         "updated_at": "2026-09-01T00:00:00Z",
                         "pushed_at": "2026-08-30T00:00:00Z"})
    for owner in owners:
        avatar = root / "avatars" / f"{owner}.png"
        avatar.parent.mkdir(parents=True, exist_ok=True)
        avatar.write_bytes(b"\x89PNG\r\n\x1a\n" + owner.encode())
        write_json_file(root / "users" / owner,
                        {"login": owner, "name": owner.title(), "type": "Organization",
                         "html_url": f"https://github.com/{owner}", "avatar_url": avatar.as_uri()})
    return root


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    """No test reaches the network.

    Constructing a real httpx client raises, so a test cannot silently call out even with a local
    `.env` full of real keys. The tests that exercise the call inject a stand-in client.
    """

    def _no_client(*args, **kwargs):
        raise AssertionError("a real HTTP client was constructed")

    monkeypatch.setattr(common.httpx, "Client", _no_client)


@pytest.fixture
def workdir(tmp_path, monkeypatch) -> Path:
    """An isolated working directory, wired up through SKILLS_PROFILES_* env vars.

    The script builds its own Config, so the tests point it at tmp_path the way a user would -
    through the environment - and chdir into it so nothing relative (`.env`, `output/`) can escape.
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
def config(workdir) -> common.Config:
    """The Config the scripts build for `workdir`."""
    return common.Config()
