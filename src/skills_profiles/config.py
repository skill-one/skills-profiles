"""Runtime configuration: env vars over .env over built-in defaults."""

from pathlib import Path
from typing import Annotated

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

REPO = "skill-one/skills-sh-mirror"
DIST_BRANCH = "dist"
REPO_URL = f"https://github.com/{REPO}"
# upstream's version pointer: one line on the dist branch holding the newest
# tag, so `sync` answers "is there anything to do" with one tiny request
# (raw serves it with a ~5 minute cache; the tag it names is immutable)
LATEST_URL = f"https://raw.githubusercontent.com/{REPO}/{DIST_BRANCH}/latest"


def tarball_url(ref: str = DIST_BRANCH) -> str:
    """The whole branch in one request, at a branch, tag or commit."""
    return f"https://codeload.github.com/{REPO}/tar.gz/{ref}"


TARBALL_URL = tarball_url()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="SKILLS_PROFILES_", env_file=".env", env_file_encoding="utf-8", extra="ignore",
        # the CLI overrides limits by assignment; validating it keeps `--concurrency 0`
        # an error rather than a semaphore that never lets a request through
        validate_assignment=True,
    )

    model: str = "gpt-4.1-mini"
    base_url: str | None = None  # override for OpenAI-compatible endpoints
    api_key: str | None = None
    limit: int = 10  # skills to generate per run; cached/sourceless ones are skipped, not counted
    # a ceiling on the dataset, not a per-run budget: `run` only ever serves the
    # top N, for profiles and pictures alike. Unlike `limit` it is set once
    # (here, or SKILLS_PROFILES_TOTAL_LIMIT) so local and CI cannot drift apart;
    # 0 means "no ceiling, every skill". See data.portfolio for where it applies.
    total_limit: int = 1000
    concurrency: int = 2
    max_retries: int = 3
    # max LLM request starts per minute, shared by the whole run: Agnes
    # documents 20 RPM for its chat models, so 20 is the default and 0 lifts
    # the cap (own-key endpoints may allow more). A start-time budget, on top
    # of the concurrency semaphore's in-flight ceiling.
    llm_rate_limit: int = 20
    # generated profiles: skills.jsonl + skills/<id>/<prompt>.json (with md/ copies)
    output_dir: Path = Path("output")
    # the unpacked dist branch: skills.jsonl + skills/<id>/SKILL.md
    data_dir: Path = Path("cache/skills-sh")
    prompts_dir: Path = Path("prompts")  # one markdown file per prompt

    # Covers: a separate text-to-image endpoint (own key, own base url), so the
    # chat provider and the image provider are freely different services.
    # https://agnes-ai.com/docs/agnes-image-25-flash
    image_base_url: str = "https://apihub.agnes-ai.com/v1"
    image_api_key: str | None = None
    # extra endpoint keys (comma-separated in the env): each key is paced at
    # image_rate_limit/min in its own bucket, so N keys render N times as fast
    image_api_keys: Annotated[list[str], NoDecode] = []
    image_model: str = "agnes-image-2.5-flash"
    image_size: str = "1024x1024"  # exact sizes work too (1K/2K tiers map to them)
    # max images per minute per key; Agnes documents 20 RPM for the image
    # models too, so 20 is the default and 0 would mean unbounded
    image_rate_limit: int = 20

    @field_validator("image_api_keys", mode="before")
    @classmethod
    def _split_keys(cls, value):
        """`SKILLS_PROFILES_IMAGE_API_KEYS=k1,k2` arrives as one raw string."""
        if isinstance(value, str):
            return [key.strip() for key in value.split(",") if key.strip()]
        if isinstance(value, (list, tuple)):
            return [key.strip() for key in value if isinstance(key, str) and key.strip()]
        return value

    @property
    def image_keys(self) -> list[str]:
        """Every configured image key, primary first, deduplicated."""
        keys = [self.image_api_key] if self.image_api_key else []
        keys += [key for key in self.image_api_keys if key not in keys]
        return keys

    @property
    def images_url(self) -> str:
        """The image generations endpoint on the configured base url."""
        return self.image_base_url.rstrip("/") + "/images/generations"

    @model_validator(mode="before")
    @classmethod
    def _empty_means_unset(cls, values):
        """An empty env var or `.env` line means "not set", not "".

        Actions export a secret or variable nobody configured as an empty string,
        which would otherwise replace a default (and an empty `image_size` aborts
        every run) instead of leaving the documented default in place.
        """
        if isinstance(values, dict):
            return {key: value for key, value in values.items() if value != ""}
        return values

    @model_validator(mode="after")
    def _validate(self) -> "Settings":
        if self.concurrency < 1:
            raise ValueError("concurrency must be >= 1")
        if self.max_retries < 0:
            raise ValueError("max_retries must be >= 0")
        if self.llm_rate_limit < 0:
            raise ValueError("llm_rate_limit must be >= 0")
        if self.total_limit < 0:
            raise ValueError("total_limit must be >= 0")
        if self.image_rate_limit < 0:
            raise ValueError("image_rate_limit must be >= 0")
        width, sep, height = self.image_size.partition("x")
        if not sep or not width.isdigit() or not height.isdigit():
            raise ValueError(f"image_size must be [width]x[height], got {self.image_size!r}")
        return self
