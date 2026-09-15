"""Cover images: one png per skill, an avatar of the persona's physical tool.

Two steps stand between the persona and the picture. First the `cover` prompt
(the DAG's one LLM recipe, fed by `persona.tool`) turns the Chinese tool name
into an English subject description — the visual details a bare name cannot
carry. Then `image_prompt` assembles the full prompt from three parts: that
recipe text, the one shared look every cover gets (`COVER_STYLE`), and the
banned content restated as positive "no ..." phrases (`NEGATIVE_PROMPT`) —
the endpoint takes no negative_prompt field, so the bans ride in the prompt
itself. The recipe and style phrases stay English because diffusion training
captions are English short phrases.

Rendering is a post-pass of `run` rather than a prompt in the DAG for three
reasons: the image endpoint is a different service with its own key (see
config's `image_*`), its calls are far slower and costlier than a chat call, and
its answer is a url the provider expires - so the bytes must be fetched at once
and stored, never referenced.

The file is the cache, as everywhere else in the artifact layout: a skill that
has a `cover.png` is never re-rendered, and dropping one is
`invalidate --prompts cover`'s job (the picture is an asset of the cover
recipe, so the two are refilled together; invalidating persona cascades to
cover, so a new tool name redraws the picture). A skill with no cover recipe
yet simply has nothing to render and waits for a later run.
"""

import asyncio
import base64
import logging
import time
import zlib
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path

import httpx
from aiolimiter import AsyncLimiter
from PIL import Image

from .config import Settings
from .data import download_file
from .layout import SKILLS_SUBDIR
from .models import SkillRecord
from .outputs import read_prompt_output, skill_result_dir

logger = logging.getLogger(__name__)

COVER_PROMPT_ID = "cover"  # its `text` field supplies the picture's subject
COVER_FILENAME = "cover.png"  # the rendered cover, next to the prompt jsons
# The one shared look every cover gets, kept English: diffusion training
# captions are comma-separated English short phrases. Cyberpunk flat: neon
# glow does the drama, the dark backdrop does the contrast, and everything
# else stays minimal. "single centered object" states positively what the
# negatives below only forbid — positive phrasing obeys better — and makes
# the recipe's own job (one tool, no layout talk) redundantly safe.
COVER_STYLE = ("cyberpunk flat illustration, neon cyan and magenta glow, "
               "dark plain background, bold minimal shapes, "
               "single centered object")
# What no cover may contain: letters render as garbage, and anything alive or
# busy would turn the tool avatar into an illustration of a scene. The endpoint
# takes no negative_prompt field, so the bans are restated as positive "no ..."
# phrases and ride in the prompt itself. Kept short on purpose — one phrase per
# failure mode, word-family synonyms (letters/numbers/logo ≈ text) dropped:
# diffusion obeys "no X" weakly and mentioning extra X's only invites them.
NEGATIVE_PROMPT = ("no text, no watermark, no person, no hands, "
                   "no duplicates, not photorealistic")
# a stalled endpoint must become a timeout, not a hung CI job (a slow generation
# takes ~20s; the timeout leaves room for the retry backoff on top)
REQUEST_TIMEOUT_SECONDS = 300
# transient statuses worth a retry: 429 rate limit, 503 model service
# overloaded, 504 gateway timeout, plus the proxy-side 502 that fronts them
RETRYABLE_STATUS = frozenset({429, 502, 503, 504})
# the window the endpoint's per-minute quota is counted in: each key's limiter
# lets at most settings.image_rate_limit requests into any 60-second stretch
RATE_WINDOW_SECONDS = 60

@dataclass
class _KeyEntry:
    """One endpoint key: its own per-minute bucket, and when it was last claimed."""

    key: str
    limiter: AsyncLimiter | None
    claimed: float = 0.0


class KeyPool:
    """The endpoint's keys, each paced by its own per-minute bucket.

    A quota belongs to a key, not to the process: `image_rate_limit` images per
    minute per key, so N keys render N times as fast. A render takes the key
    that has been idle longest (the claim timestamp is set before waiting, so
    concurrent renders spread across the pool), then queues in that key's
    bucket; with rate 0 the pool only rotates.
    """

    def __init__(self, keys: list[str], rate: int,
                 window: int = RATE_WINDOW_SECONDS) -> None:
        if not keys:
            raise RuntimeError(
                "no image endpoint key configured (SKILLS_PROFILES_IMAGE_API_KEY)")
        self._entries = [
            _KeyEntry(key=key, limiter=AsyncLimiter(rate, window) if rate else None)
            for key in keys
        ]

    @asynccontextmanager
    async def slot(self) -> AsyncIterator[str]:
        """Hold one key until the render leaves the context, quota-permitting."""
        entry = min(self._entries, key=lambda e: e.claimed)
        entry.claimed = time.monotonic()
        if entry.limiter is not None:
            async with entry.limiter:
                yield entry.key
        else:
            yield entry.key

# a real 1x1 png, so a dry-run exercises the same layout as a real render
FAKE_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGNoaGgAAAMEAYFL09IQAAAAAElFTkSuQmCC"
)

@dataclass
class CoverStats:
    """Aggregated counters for one rendering post-pass, tallied by `run_covers`."""

    rendered: int = 0
    skills_failed: int = 0


def cover_path(settings: Settings, skill_id: str) -> Path:
    """Where a skill's rendered cover lives."""
    return skill_result_dir(settings, skill_id) / COVER_FILENAME


def covers_on_disk(settings: Settings) -> int:
    """How many skills hold a rendered cover.

    Counted from the artifact tree, like every other number in stats.json: it is
    the dataset's current state, not a run's tally.
    """
    root = settings.output_dir / SKILLS_SUBDIR
    return sum(1 for _ in root.rglob(COVER_FILENAME))


def cover_needed(settings: Settings, skill_id: str) -> bool:
    """True when there is a persona to render and no picture yet."""
    return image_prompt(settings, skill_id) is not None and not cover_path(
        settings, skill_id).is_file()


def image_prompt(settings: Settings, skill_id: str) -> str | None:
    """The full prompt for one cover, assembled from the cover recipe's text.

    Three parts joined with sentence breaks: the recipe's English subject
    description (the `cover` prompt's LLM output, which turns persona.tool
    into visual details), the shared `COVER_STYLE` look, and `NEGATIVE_PROMPT`
    restated as "no ..." phrases since the endpoint takes no negative field.
    None means the skill has no cover recipe yet, i.e. nothing to render.
    """
    stored = read_prompt_output(settings, skill_id, COVER_PROMPT_ID)
    if stored is None:
        return None
    subject = str(stored.get("text") or "").strip()
    if not subject:
        return None
    return f"{subject}. {COVER_STYLE}. {NEGATIVE_PROMPT}"


def seed_for(skill_id: str) -> int:
    """A seed stable per skill id, within the endpoint's documented 0..999.

    Providers do not promise that a fixed seed reproduces the same pixels, so
    this is not a byte-level cache — the file's existence is. Pinning the seed
    just keeps a deliberate re-render close to the picture it replaces.
    """
    return zlib.crc32(skill_id.encode("utf-8")) % 1000


def request_payload(settings: Settings, prompt: str, seed: int) -> dict:
    """The generations body, per the endpoint's documented fields.

    The endpoint takes no `negative_prompt`, `num_inference_steps` or
    `guidance_scale` (each answers 400), and `batch_size` has no meaning for
    one picture per skill.
    """
    return {
        "model": settings.image_model,
        "prompt": prompt,
        "size": settings.image_size,
        "seed": seed,
    }


def _error_detail(response: httpx.Response) -> str:
    """The provider's own message from an error body.

    The endpoint answers OpenAI-shaped errors ({"error": {"message", ...}});
    a proxy in front may answer with other shapes.
    """
    try:
        body = response.json()
    except ValueError:  # not json: an html error page from something in front
        return str(response.status_code)
    if isinstance(body, dict):
        error = body.get("error")
        if isinstance(error, dict) and error.get("message"):
            return str(error["message"])
        return str(body.get("message") or body)
    return str(body)


def _request_image(settings: Settings, prompt: str, seed: int, key: str) -> tuple[str, str]:
    """One generations request on `key`; returns (image url, provider task id).

    Retries transient failures with exponential backoff. A 400/401/403 is raised
    at once: the same request would be rejected the same way, and the message
    (bad size, bad key) is worth seeing rather than three copies of.
    """
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = request_payload(settings, prompt, seed)
    attempts = settings.max_retries + 1  # one try plus the documented retries
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            response = httpx.post(
                settings.images_url, json=payload, headers=headers,
                timeout=REQUEST_TIMEOUT_SECONDS, follow_redirects=True,
            )
            if response.status_code != 200:
                detail = (f"image endpoint returned {response.status_code}: "
                          f"{_error_detail(response)}")
                if response.status_code not in RETRYABLE_STATUS:
                    raise RuntimeError(detail)
                last_error = RuntimeError(detail)
            else:
                try:
                    body = response.json()
                except ValueError as e:
                    # e.g. an html error page from something in front of the endpoint
                    raise RuntimeError(
                        f"image endpoint replied with something that is not json: "
                        f"{response.text[:200]!r}") from e
                # the answer is OpenAI-shaped: `{"data": [{"url": ...}], "task_id"}` —
                # a url, not base64 (`return_base64` stays unset)
                urls = [img.get("url") for img in body.get("data") or [] if img.get("url")]
                if not urls:
                    raise RuntimeError(f"no image url in the response: {str(body)[:200]}")
                trace = str(body.get("task_id") or "")
                logger.debug("generated an image (task %s)", trace)
                return str(urls[0]), trace
        except (httpx.HTTPError, OSError) as e:
            last_error = RuntimeError(f"image endpoint unreachable: {e}")
        logger.warning("%s (attempt %d/%d)", last_error, attempt, attempts)
        if attempt < attempts:
            time.sleep(2**attempt)
    raise RuntimeError(
        f"giving up on the image endpoint after {attempts} attempt(s): {last_error}"
    ) from last_error


# the stored cover's size: a 1024px render downscaled to 512 — plenty for an
# avatar — and quantized to a 128-color palette, with dithering off to keep
# flat-illustration color blocks clean
COVER_PIXEL_SIZE = 512
COVER_PALETTE_COLORS = 128


def _compress_png(dest: Path) -> None:
    """Re-encode a downloaded cover in place: 512px, 128-color palette PNG.

    The endpoint returns a full-color 1024px PNG (~1.7 MB) although covers are
    flat illustrations shown at avatar size: downscaling to 512 and quantizing
    to a 128-color palette (dithering off, so flat color blocks stay clean)
    shrinks the artifact an order of magnitude. A re-encode that does not
    shrink is discarded — the original download is already on disk, so the
    worst case is the raw bytes.
    """
    with Image.open(dest) as img:
        small = img.convert("RGB").resize(
            (COVER_PIXEL_SIZE, COVER_PIXEL_SIZE), Image.Resampling.LANCZOS)
        palette = small.quantize(colors=COVER_PALETTE_COLORS, dither=Image.Dither.NONE)
    candidate = dest.with_name(f"{dest.stem}.tmp{dest.suffix}")
    try:
        palette.save(candidate, optimize=True)
        if candidate.stat().st_size < dest.stat().st_size:
            logger.debug("%s: compressed %d -> %d bytes", dest.name,
                         dest.stat().st_size, candidate.stat().st_size)
            candidate.replace(dest)
        else:
            candidate.unlink()  # re-encode did not pay: keep the raw download
    finally:
        candidate.unlink(missing_ok=True)


class ImageClient:
    """The provider's text-to-image endpoint (see Settings.images_url).

    Pacing lives here because a quota belongs to a key: the client's KeyPool
    hands each render a key and holds it inside that key's per-minute bucket.
    """

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.keys = KeyPool(settings.image_keys, settings.image_rate_limit)

    async def generate(self, prompt: str, seed: int, dest: Path) -> None:
        """Write one cover to dest; the blocking HTTP runs in a worker thread."""
        async with self.keys.slot() as key:
            await asyncio.to_thread(self._generate, prompt, seed, dest, key)

    def _generate(self, prompt: str, seed: int, dest: Path, key: str) -> None:
        url, trace = _request_image(self.settings, prompt, seed, key)
        # the url expires on the provider's schedule: download it now, store the bytes
        if not download_file(url, dest, timeout=REQUEST_TIMEOUT_SECONDS):
            raise RuntimeError(f"the generated image was already gone (404, task {trace})")
        _compress_png(dest)


class FakeImages:
    """Deterministic offline stand-in for dry-runs and tests."""

    async def generate(self, prompt: str, seed: int, dest: Path) -> None:
        dest.write_bytes(FAKE_PNG)


def make_images(settings: Settings) -> ImageClient:
    """The real client; like `make_llm`, it holds no connection of its own."""
    return ImageClient(settings)


async def render_cover(
    images, settings: Settings, skill: SkillRecord, sem: asyncio.Semaphore,
) -> tuple[float, int]:
    """Render one skill's cover; returns (seconds, bytes written).

    The semaphore bounds how many renders are in flight; per-key pacing happens
    inside the images client (see KeyPool).
    """
    prompt = image_prompt(settings, skill.id)
    if prompt is None:  # callers pre-filter with cover_needed; a caller may not
        raise RuntimeError(f"{skill.id} has no cover recipe to render a cover from")
    logger.debug("%s: image prompt: %s", skill.id, prompt)
    dest = cover_path(settings, skill.id)
    dest.parent.mkdir(parents=True, exist_ok=True)
    async with sem:
        start = time.monotonic()
        await images.generate(prompt, seed_for(skill.id), dest)
        seconds = time.monotonic() - start
    return seconds, dest.stat().st_size


async def run_covers(
    images,
    settings: Settings,
    skills: list[SkillRecord],
    on_skill_done: Callable[[SkillRecord, int | None], None] | None = None,
    stats: CoverStats | None = None,
) -> list[str]:
    """Render covers for the given skills concurrently; returns the ids rendered.

    Same contract as `generate.run_all`: one semaphore bounds the whole run at
    `settings.concurrency` requests in flight, a skill whose render raises is
    isolated (the error is logged, the run continues, the missing picture is
    picked up by the next run), and nothing outside the selection is touched.
    Per-key pacing happens inside the images client (see KeyPool).
    """
    sem = asyncio.Semaphore(settings.concurrency)

    async def _one(skill: SkillRecord) -> str | None:
        try:
            seconds, written = await render_cover(images, settings, skill, sem)
        except Exception as e:
            logger.error("%s: cover failed, continuing with the rest: %s", skill.id, e)
            if on_skill_done:
                on_skill_done(skill, None)
            if stats is not None:
                stats.skills_failed += 1
            return None
        if on_skill_done:
            on_skill_done(skill, written)
        if stats is not None:
            stats.rendered += 1
        logger.debug("%s: %.1fs, %.0f KB", skill.id, seconds, written / 1024)
        return skill.id

    results = await asyncio.gather(*(_one(s) for s in skills))
    return [r for r in results if r]
