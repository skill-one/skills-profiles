"""Tests for cover rendering: the direct persona.tool projection, the endpoint
contract, the file-is-the-cache rule, the per-key rate limiter, and `run`'s
render post-pass. All offline: the image endpoint is reached only through a
stubbed `httpx.post`, and dry-runs through FakeImages."""

import asyncio
import json
from pathlib import Path

import httpx
import pytest
from typer.testing import CliRunner

import skills_profiles.images as images_mod
from skills_profiles.cli import app
from skills_profiles.config import Settings
from skills_profiles.data import load_skills, portfolio
from skills_profiles.images import (
    COVER_STYLE,
    FAKE_PNG,
    NEGATIVE_PROMPT,
    CoverStats,
    FakeImages,
    ImageClient,
    cover_needed,
    covers_on_disk,
    image_prompt,
    request_payload,
    run_covers,
    seed_for,
)
from skills_profiles.outputs import invalidate, write_prompt_output

runner = CliRunner()


def store(settings, skill_id: str, prompt_id: str, output: dict) -> None:
    """Put one prompt's output on disk, as a run would."""
    write_prompt_output(settings, skill_id, prompt_id, output)


def cover_of(settings, skill_id: str) -> Path:
    return images_mod.cover_path(settings, skill_id)


def json_response(body: dict, status: int = 200) -> httpx.Response:
    """An endpoint answer: a json body (no informative headers)."""
    return httpx.Response(status, json=body)


def text_response(text: str, status: int = 200) -> httpx.Response:
    """An endpoint answer that is not json (e.g. an html error page)."""
    return httpx.Response(status, text=text)


class StubPost:
    """Serves canned responses (or errors) in order and records what was posted."""

    def __init__(self, *outcomes):
        self.outcomes = list(outcomes)
        self.requests: list[tuple[dict, dict]] = []

    def __call__(self, url, *, json, headers, timeout=None, follow_redirects=False):
        self.requests.append((json, headers))
        if len(self.requests) > len(self.outcomes):
            raise AssertionError("asked the endpoint more times than the test staged")
        outcome = self.outcomes[len(self.requests) - 1]
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


@pytest.fixture
def with_profiles(settings):
    """Two skills holding a persona: the Chinese tool name is the cover subject."""
    skills = load_skills(settings)
    store(settings, skills[0].id, "persona",
          {"tool": "放大镜", "pitch": "放大细节给你看——我是一只放大镜。"})
    store(settings, skills[1].id, "persona",
          {"tool": "扳手", "pitch": "拧好松掉的地方——我是一把扳手。"})
    return skills[:2]


# --- the projection: the tool name leads the assembled prompt ---------------

def test_image_prompt_leads_with_the_tool_name(settings, with_profiles):
    assert image_prompt(settings, with_profiles[0].id).startswith("放大镜. ")


def test_every_cover_assembles_style_and_bans_into_one_prompt(settings):
    """Style and negative terms ride in the prompt (the endpoint has no
    negative_prompt field), after the persona's subject."""
    skill = load_skills(settings)[0]
    store(settings, skill.id, "persona", {"tool": "某物", "pitch": "x"})
    prompt = image_prompt(settings, skill.id)
    assert prompt.startswith("某物. ")
    assert f". {COVER_STYLE}. " in prompt
    assert prompt.endswith(NEGATIVE_PROMPT)
    assert "no person" in NEGATIVE_PROMPT and "no text" in NEGATIVE_PROMPT


def test_image_prompt_is_none_without_a_persona(settings):
    assert image_prompt(settings, load_skills(settings)[0].id) is None


def test_image_prompt_is_none_for_an_empty_tool_name(settings):
    """A persona without a usable tool name has no subject: nothing to render."""
    skill = load_skills(settings)[0]
    store(settings, skill.id, "persona", {"tool": "   ", "pitch": "x"})
    assert image_prompt(settings, skill.id) is None


def test_image_prompt_does_not_read_any_other_prompt(settings, with_profiles):
    """The picture derives from persona only: deleting domain.json must not
    change the prompt."""
    before = image_prompt(settings, with_profiles[0].id)
    invalidate(settings, [with_profiles[0].id], {"domain"})
    assert image_prompt(settings, with_profiles[0].id) == before


# --- the request, per the documented contract ------------------------------

def test_payload_uses_the_documented_field_names(settings):
    assert request_payload(settings, "a lighthouse at dusk", 42) == {
        "model": "agnes-image-2.5-flash",
        "prompt": "a lighthouse at dusk",
        "size": "1024x1024",
        "seed": 42,
    }


def test_seed_is_stable_within_the_documented_range():
    assert seed_for("owner/repo/slug") == seed_for("owner/repo/slug")
    assert seed_for("a/b/c") != seed_for("a/b/d")
    assert 0 <= seed_for("owner/repo/slug") <= 999


def test_endpoint_url_is_derived_from_the_image_base_url():
    assert Settings(image_base_url="https://apihub.agnes-ai.com/v1/").images_url == (
        "https://apihub.agnes-ai.com/v1/images/generations")


@pytest.mark.parametrize("size", ["1024x1024", "864x1152"])
def test_settings_accept_any_exact_size(size):
    """The endpoint takes exact sizes (legacy style) and normalizes exotic ones."""
    assert Settings(image_size=size).image_size == size


@pytest.mark.parametrize("kwargs, message", [
    ({"image_size": "square"}, r"image_size must be \[width\]x\[height\]"),
    ({"image_rate_limit": -1}, r"image_rate_limit must be >= 0"),
])
def test_settings_reject_values_the_docs_do_not_allow(kwargs, message):
    with pytest.raises(ValueError, match=message):
        Settings(**kwargs)


def test_settings_reject_a_negative_total_limit():
    """The dataset ceiling is a size, so a negative is a config mistake, not "all"."""
    with pytest.raises(ValueError, match="total_limit must be >= 0"):
        Settings(total_limit=-1)


def test_request_returns_the_image_url_and_task_id(settings, monkeypatch):
    stub = StubPost(json_response(
        {"data": [{"url": "https://cdn/x.png"}], "task_id": "task-1"}))
    monkeypatch.setattr(images_mod.httpx, "post", stub)
    settings.image_api_key = "sk-image"

    url, trace = images_mod._request_image(settings, "p", 1, key="sk-image")

    assert (url, trace) == ("https://cdn/x.png", "task-1")
    body, headers = stub.requests[0]
    assert body["prompt"] == "p"
    assert body["model"] == "agnes-image-2.5-flash"
    assert headers["Authorization"] == "Bearer sk-image"


def test_request_retries_a_rate_limit_then_gives_up(settings, monkeypatch):
    monkeypatch.setattr(images_mod.time, "sleep", lambda _s: None)

    def limited() -> httpx.Response:
        return json_response({"error": {"message": "rate limit reached"}}, status=429)

    stub = StubPost(*[limited() for _ in range(4)])
    monkeypatch.setattr(images_mod.httpx, "post", stub)
    settings.max_retries = 3

    with pytest.raises(RuntimeError, match="rate limit reached"):
        images_mod._request_image(settings, "p", 1, key="sk")
    assert len(stub.requests) == 4, "the initial try plus three retries, no more"


def test_request_does_not_retry_a_rejected_payload(settings, monkeypatch):
    """A 400 says the request itself is wrong; sending it again only burns time."""
    monkeypatch.setattr(images_mod.time, "sleep", lambda _s: None)
    stub = StubPost(json_response(
        {"error": {"message": "seed must be between -1 and 999"}}, status=400))
    monkeypatch.setattr(images_mod.httpx, "post", stub)
    settings.max_retries = 3

    with pytest.raises(RuntimeError, match="seed must be between"):
        images_mod._request_image(settings, "p", 1, key="sk")
    assert len(stub.requests) == 1


def test_request_needs_a_url_in_the_answer(settings, monkeypatch):
    monkeypatch.setattr(images_mod.httpx, "post", StubPost(json_response({"data": []})))
    with pytest.raises(RuntimeError, match="no image url"):
        images_mod._request_image(settings, "p", 1, key="sk")


async def test_client_stores_the_bytes_behind_the_expiring_url(settings, with_profiles,
                                                               monkeypatch):
    settings.image_api_key = "sk-image"  # the client builds its key pool from it
    dest = cover_of(settings, with_profiles[0].id)
    dest.parent.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(images_mod.httpx, "post",
                        StubPost(json_response({"data": [{"url": "https://cdn/x.png"}]})))
    seen = {}

    def fake_download(url, target, timeout=None):
        seen["url"], seen["timeout"] = url, timeout
        Path(target).write_bytes(FAKE_PNG)
        return True

    monkeypatch.setattr(images_mod, "download_file", fake_download)
    await ImageClient(settings).generate("a subject, a style", 3, dest)

    assert seen["url"] == "https://cdn/x.png"  # fetched at once: the url dies in an hour
    assert seen["timeout"] == images_mod.REQUEST_TIMEOUT_SECONDS, "a hung download would" \
        " hold a concurrency slot forever"
    assert dest.read_bytes() == FAKE_PNG  # the 1x1 fake re-encodes no smaller, so it stays


def test_compress_png_reduces_a_full_color_cover(tmp_path):
    """A downloaded full-color cover is re-encoded as a palette PNG, in place."""
    import random

    from PIL import Image as PILImage

    dest = tmp_path / "cover.png"
    rng = random.Random(7)
    img = PILImage.new("RGB", (256, 256))
    img.putdata([(rng.randint(0, 255), rng.randint(0, 255), rng.randint(0, 255))
                 for _ in range(256 * 256)])
    img.save(dest)
    raw = dest.stat().st_size

    images_mod._compress_png(dest)

    with PILImage.open(dest) as out:
        assert out.mode == "P", "flat-illustration covers store as 256-color palettes"
    assert dest.stat().st_size < raw
    assert not (tmp_path / "cover.tmp.png").exists(), "no candidate file is left behind"


def test_compress_png_keeps_bytes_a_reencode_cannot_shrink(tmp_path):
    """The guard: when the re-encode is not smaller, the raw download stays."""
    dest = tmp_path / "cover.png"
    dest.write_bytes(FAKE_PNG)

    images_mod._compress_png(dest)

    assert dest.read_bytes() == FAKE_PNG


async def test_client_reports_an_already_expired_url(settings, with_profiles, monkeypatch):
    settings.image_api_key = "sk-image"
    dest = cover_of(settings, with_profiles[0].id)
    monkeypatch.setattr(images_mod.httpx, "post",
                        StubPost(json_response({"data": [{"url": "https://cdn/x.png"}]})))
    monkeypatch.setattr(images_mod, "download_file", lambda url, target, timeout=None: False)

    with pytest.raises(RuntimeError, match="already gone"):
        await ImageClient(settings).generate("p", 3, dest)
    assert not dest.exists()


# --- selection and the run --------------------------------------------------

def test_cover_needed_follows_the_file_is_the_cache_rule(settings, with_profiles):
    """A persona without a picture is pending; a drawn one never renders again."""
    skills = load_skills(settings)
    assert [s.id for s in skills if cover_needed(settings, s.id)] == [
        skills[0].id, skills[1].id]  # the two others have no persona yet

    cover_of(settings, skills[0].id).parent.mkdir(parents=True, exist_ok=True)
    cover_of(settings, skills[0].id).write_bytes(FAKE_PNG)
    assert cover_needed(settings, skills[0].id) is False
    assert [s.id for s in skills if cover_needed(settings, s.id)] == [skills[1].id]


def test_portfolio_is_a_rank_window_not_a_count_of_done_work(settings):
    """The ceiling is the top N by installs; 0 or N past the end serves everyone."""
    skills = load_skills(settings)  # alpha, beta, gamma, hotel — installs descending
    assert [s.id for s in portfolio(Settings(total_limit=2), skills)] == [
        skills[0].id, skills[1].id]
    assert portfolio(Settings(total_limit=0), skills) == skills
    assert portfolio(Settings(total_limit=99), skills) == skills


def test_covers_never_reach_past_the_window_even_with_a_persona(settings, with_profiles):
    """beta holds a persona but sits outside a top-1 window: it is never drawn.

    The window is positional, so a filled-in slot never hands its turn to a skill
    the total cap excludes — that is what bounds the dataset, not just one run.
    """
    skills = load_skills(settings)
    settings.total_limit = 1
    window = portfolio(settings, skills)
    assert with_profiles[1].id not in [s.id for s in window], "beta has a persona but is outside"
    assert [s.id for s in window if cover_needed(settings, s.id)] == [skills[0].id]


async def test_run_covers_renders_each_pending_skill_once(settings, with_profiles):
    stats = CoverStats()
    seen: list[str] = []
    skills = with_profiles

    rendered = await run_covers(FakeImages(), settings, skills,
                               on_skill_done=lambda s, w: seen.append(s.id), stats=stats)

    assert rendered == [s.id for s in skills]
    assert seen == [s.id for s in skills]
    assert stats.rendered == 2 and stats.skills_failed == 0
    assert all(cover_of(settings, s.id).read_bytes() == FAKE_PNG for s in skills)
    assert covers_on_disk(settings) == 2

    again = await run_covers(FakeImages(), settings,
                             [s for s in load_skills(settings)
                              if cover_needed(settings, s.id)],
                             stats=stats)
    assert again == [], "a rendered cover is never re-rendered"


async def test_run_covers_isolates_a_failing_skill(settings, with_profiles):
    class Exploding(FakeImages):
        async def generate(self, prompt, seed, dest):
            if "扳手" in prompt:  # the second fixture skill's tool
                raise RuntimeError("429 rate limit reached")
            await super().generate(prompt, seed, dest)

    skills = with_profiles
    stats = CoverStats()
    rendered = await run_covers(Exploding(), settings, skills, stats=stats)

    assert rendered == [skills[0].id], "one bad skill must not stop the others"
    assert (stats.rendered, stats.skills_failed) == (1, 1)
    assert cover_of(settings, skills[0].id).is_file()
    assert not cover_of(settings, skills[1].id).exists()


def test_image_keys_merge_the_primary_and_the_extra_ones(settings):
    settings.image_api_key = "k1"
    settings.image_api_keys = ["k2", "k1", " k3 "]
    assert settings.image_keys == ["k1", "k2", "k3"], "deduplicated, stripped, primary first"
    settings.image_api_key = None
    assert settings.image_keys == ["k2", "k1", "k3"]


def test_image_api_keys_parse_from_a_comma_separated_env(monkeypatch):
    monkeypatch.setenv("SKILLS_PROFILES_IMAGE_API_KEYS", "k1, k2,,k3")
    s = Settings(_env_file=None)
    assert s.image_api_keys == ["k1", "k2", "k3"]


async def test_key_pool_spreads_load_across_keys():
    """Concurrent renders take the most-rested key, so N keys serve N at once."""
    pool = images_mod.KeyPool(["a", "b"], rate=0)
    used: list[str] = []

    async def grab():
        async with pool.slot() as key:
            used.append(key)

    await asyncio.gather(*(grab() for _ in range(4)))
    assert used.count("a") == 2 and used.count("b") == 2


async def test_key_pool_paces_each_key_at_the_rate():
    """Each key holds its own bucket: 2 keys x 2/min admit 4 at once, the 5th waits."""
    pool = images_mod.KeyPool(["a", "b"], rate=2, window=0.05)
    times: list[float] = []

    async def grab():
        async with pool.slot():
            times.append(asyncio.get_running_loop().time())

    await asyncio.gather(*(grab() for _ in range(6)))
    assert len(times) == 6
    # the bucket leaks continuously: 4 renders fit the two keys' immediate
    # capacity, the 5th must wait roughly half a window for leaked capacity
    assert times[3] - times[0] < 0.04, "the first four go out at once"
    assert times[4] - times[0] >= 0.02, "the 5th render had to wait for capacity"


def test_key_pool_refuses_to_be_built_without_keys():
    with pytest.raises(RuntimeError, match="no image endpoint key"):
        images_mod.KeyPool([], rate=2)


async def test_an_unlimited_rate_limit_never_paces(settings, with_profiles):
    settings.image_rate_limit = 0
    times: list[float] = []

    class Timed(FakeImages):
        async def generate(self, prompt, seed, dest):
            times.append(asyncio.get_running_loop().time())
            await super().generate(prompt, seed, dest)

    await run_covers(Timed(), settings, with_profiles)
    assert times[1] - times[0] < 0.05


async def test_render_refuses_a_skill_with_no_persona(settings):
    skill = load_skills(settings)[0]

    with pytest.raises(RuntimeError, match="no persona output"):
        await images_mod.render_cover(FakeImages(), settings, skill, asyncio.Semaphore(1))


# --- invalidation drops the picture with its persona ------------------------

def test_invalidate_persona_takes_the_png_with_the_json(settings, with_profiles):
    """The picture is persona's asset: one invalidation drops both, so a run
    refills the tool name and the picture together."""
    skill = with_profiles[0]
    cover_of(settings, skill.id).parent.mkdir(parents=True, exist_ok=True)
    cover_of(settings, skill.id).write_bytes(FAKE_PNG)

    assert invalidate(settings, [skill.id], {"persona"}) == 1
    assert not cover_of(settings, skill.id).exists()
    assert image_prompt(settings, skill.id) is None
    assert not cover_needed(settings, skill.id), "nothing to render until run refills persona"


def test_invalidate_a_different_prompt_keeps_the_picture(settings, with_profiles):
    skill = with_profiles[0]
    cover_of(settings, skill.id).parent.mkdir(parents=True, exist_ok=True)
    cover_of(settings, skill.id).write_bytes(FAKE_PNG)

    # no domain.json in the fixture, and the picture derives only from persona:
    # invalidating domain removes nothing and leaves the cover intact
    assert invalidate(settings, [skill.id], {"domain"}) == 0
    assert cover_of(settings, skill.id).is_file(), "only persona owns the png"
    assert image_prompt(settings, skill.id).startswith("放大镜. ")


def test_a_transient_failure_then_success_renders(settings, monkeypatch):
    """The point of retrying: a rate-limited first answer must not lose the cover."""
    monkeypatch.setattr(images_mod.time, "sleep", lambda _s: None)
    stub = StubPost(json_response({"error": {"message": "rate limit reached"}}, status=429),
                    json_response({"data": [{"url": "https://cdn/x.png"}]}))
    monkeypatch.setattr(images_mod.httpx, "post", stub)
    settings.max_retries = 3

    url, _trace = images_mod._request_image(settings, "p", 1, key="sk")
    assert url == "https://cdn/x.png" and len(stub.requests) == 2


def test_no_retries_means_exactly_one_attempt(settings, monkeypatch):
    monkeypatch.setattr(images_mod.time, "sleep", lambda _s: None)
    stub = StubPost(json_response({"error": {"message": "overloaded"}}, status=503))
    monkeypatch.setattr(images_mod.httpx, "post", stub)
    settings.max_retries = 0

    with pytest.raises(RuntimeError, match="overloaded"):
        images_mod._request_image(settings, "p", 1, key="sk")
    assert len(stub.requests) == 1


def test_a_reply_that_is_not_json_is_named_as_the_endpoints_fault(settings, monkeypatch):
    monkeypatch.setattr(images_mod.httpx, "post",
                        StubPost(text_response("<html>502 bad gateway</html>")))
    with pytest.raises(RuntimeError, match="not json"):
        images_mod._request_image(settings, "p", 1, key="sk")


def test_an_empty_ci_variable_leaves_the_documented_default():
    """Actions export an unconfigured repo variable as "", which must not erase a default."""
    settings = Settings(image_size="", image_model="", image_base_url="")
    assert settings.image_size == "1024x1024"
    assert settings.image_model == "agnes-image-2.5-flash"
    assert settings.images_url.endswith("/v1/images/generations")


# --- the CLI ----------------------------------------------------------------

def test_run_rejects_a_zero_concurrency(settings, monkeypatch):
    monkeypatch.setattr("skills_profiles.cli.Settings", lambda: settings)
    result = runner.invoke(app, ["run", "--limit", "1", "--concurrency", "0", "--dry-run"])

    assert result.exit_code != 0
    assert "concurrency must be >= 1" in str(result.exception)


def test_run_renders_the_covers_its_personas_are_ready_for(settings, monkeypatch):
    """One command serves both halves: `run` fills persona (the subject) and
    draws the picture in the same invocation, and stats.json records both."""
    monkeypatch.setattr("skills_profiles.cli.Settings", lambda: settings)
    result = runner.invoke(app, ["run", "--limit", "1", "--dry-run"])

    assert result.exit_code == 0, result.output
    assert "Rendering 1 pending cover(s)" in result.output
    assert "1 cover(s) rendered, 0 failed" in result.output
    assert covers_on_disk(settings) == 1
    stats = json.loads((settings.output_dir / "stats.json").read_text(encoding="utf-8"))
    assert stats["covers"] == {"rendered": 1}
    assert stats["prompts"]["persona"] == 1, "the tool name rides in with the rest"


def test_run_without_an_image_key_skips_covers(settings, monkeypatch):
    """A key-less run degrades to text-only with a warning instead of failing;
    a later run picks the backlog up once the key is set."""
    from skills_profiles.llm import FakeLLM

    monkeypatch.setattr("skills_profiles.cli.Settings", lambda: settings)
    monkeypatch.setattr("skills_profiles.cli.make_llm", lambda s: FakeLLM())
    result = runner.invoke(app, ["run", "--limit", "0"])

    assert result.exit_code == 0, result.output
    assert "no image endpoint key" in result.output
    assert "covers not rendered" in result.output
    assert covers_on_disk(settings) == 0


def test_run_completes_the_skills_it_spends_the_budget_on(settings, monkeypatch):
    """A skill whose text is cached but whose picture is missing counts against
    `--limit` and leaves the run complete: one budget, both halves."""
    monkeypatch.setattr("skills_profiles.cli.Settings", lambda: settings)
    runner.invoke(app, ["run", "--limit", "1", "--dry-run"])
    cover_of(settings, load_skills(settings)[0].id).unlink()

    result = runner.invoke(app, ["run", "--limit", "1", "--dry-run"])

    assert result.exit_code == 0, result.output
    assert "Processing 1 of 4 skills" in result.output, \
        "alpha owes only its picture: the budget goes back to it, not to beta"
    assert "Rendering 1 pending cover(s)" in result.output
    assert covers_on_disk(settings) == 1
