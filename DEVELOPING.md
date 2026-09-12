# Developing skills-profiles

The generator behind the dataset described in [README.md](README.md): it reads each skill's
`SKILL.md` from [skills-sh-mirror](https://github.com/skill-one/skills-sh-mirror), asks an
OpenAI-compatible LLM for eight structured angles per skill, renders a cover image from one of them,
and publishes the result to this repository's `dist` branch.

中文: [DEVELOPING.zh-CN.md](DEVELOPING.zh-CN.md)

## Quickstart

Needs Python 3.12+ and [uv](https://docs.astral.sh/uv/); LLM credentials go in a local `.env` (copy
[`.env.example`](.env.example) — the only hosts touched are the mirror, your own endpoint and, when
covers are rendered, the image endpoint).

```bash
uv sync
skills-profiles sync            # download the upstream snapshot (skipped when the tag is unchanged)
skills-profiles run --limit 10  # generate profiles + render ready covers, most installed first
```

Offline, no API calls: `skills-profiles run --limit 5 --dry-run` (text plus placeholder covers).

## CLI

| Command | What it does |
|---|---|
| `sync [--refresh]` | Read upstream's one-line `latest` pointer to learn the newest tag, then pull that ref as one tarball into `cache/skills-sh`, unpacking only `skills.jsonl` and every `SKILL.md`. Records the tag in `SNAPSHOT.json` and skips the download when it is already current (`--refresh` forces it). Never touches the artifacts. |
| `run [--limit N] [--prompts a,b] [--concurrency C] [--dry-run] [--debug] [--verbose]` | Complete skills, most installed first: `N` of them (`0` = every skill with gaps). A skill is complete when every prompt is cached and its `cover.png` is drawn — the selection counts both halves, so the run fills missing text and then renders the selected skills' missing pictures, paced at `SKILLS_PROFILES_IMAGE_RATE_LIMIT` images/minute per key. Skills that need nothing, or have no `SKILL.md` in the snapshot, are skipped and do not consume the budget; without `SKILLS_PROFILES_IMAGE_API_KEY` the render pass is skipped with a warning, not an error. |
| `invalidate [--skill ID]... [--prompts a,b] [--stale] [--all]` | Drop cached outputs so the next `run` refills them. `--stale` selects the skills whose upstream hash changed or that vanished (run `sync` first). Refuses a filter-less full wipe without `--all`. Invalidating `cover` takes its `cover.png` along, which is how a picture is redrawn. |

`invalidate` deletes and `run` refills — redoing work is never a `run` flag. Failures are isolated per
skill: the run continues, finished prompts are published, and only a total washout exits non-zero.
Renders are paced at `SKILLS_PROFILES_IMAGE_RATE_LIMIT` images/minute **per key** (`0` = unbounded), so
a big batch waits its turn instead of collecting 429s.

One ceiling bounds everything, `SKILLS_PROFILES_TOTAL_LIMIT` (default 1000): only the most installed N
skills are ever profiled or drawn, however large a run's `--limit` is. It is a rank window rather than a
count of finished work, so a top skill holds its slot and redraws reuse the same N.

## How it works

```
mirror dist branch tarball ──► cache/skills-sh (skills.jsonl + skills/<id>/SKILL.md)
                                     │
                                     └─► by installs, --limit of the ones still
                                         missing prompts ──► per-skill prompt DAG
                                                ──► output/skills/<id>/<prompt>.json
                                                ──► output/skills/<id>/md/<prompt>.md
                                                ──► output/skills.jsonl (id + hash + domain + persona)
                        cover.json + domain.json ──► `run`'s post-pass
                                                ──► output/skills/<id>/cover.png
```

`output/` (the artifacts) and `cache/skills-sh` (upstream data) are separate roots: nothing fetched
from upstream is ever written next to a generated profile. Prompt DAG (edges mean "depends on the
output of"):

```
domain   scenario   blackbox   whitebox   tagline   comments      (roots)
persona ──► cover                                                 (the picture is drawn from the portrait)
# add `depends_on: [scenario]` to a prompt's frontmatter to chain it
```

Design decisions:

- **No orchestration framework** — the DAG is ordered with the stdlib
  [`graphlib.TopologicalSorter`](https://docs.python.org/3/library/graphlib.html).
- **Structured outputs** — each prompt declares a pydantic schema (`output:` in its frontmatter) and
  calls go through [instructor](https://python.useinstructor.com/) on an OpenAI-compatible client;
  schemas and the 13-value `Domain` taxonomy live in `models.py`.
- **File-based resume** — a prompt's output is its own `<prompt_id>.json` (markdown copy in `md/`),
  written the moment it is generated: present and schema-valid means no LLM call. Markdown first, json
  last, so a crash cannot leave a json without its copy. Resume granularity is per prompt.
- **The index is a projection** — `skills.jsonl` is rewritten in full from disk, so a row can never
  drift from the files; it is what `invalidate --stale` compares hashes against.
- **A cover is a recipe plus a render** — `cover` is an ordinary prompt, so it inherits the DAG, the
  cache and `invalidate`; `images.py` adds the framing and the per-`Domain` style to the recipe's
  subject. The picture's cache is the file's existence, because the endpoint's url expires within the
  hour — bytes are stored, urls never are — and re-rendering costs no LLM call.
- **One snapshot, one request** — `sync` downloads the branch as a single codeload tarball, unpacks only
  what a run reads, and replaces the previous snapshot wholesale. Upstream tags each daily scrape and
  keeps a one-line `latest` pointer naming the newest tag, so a repeat sync downloads only when the
  pointer names a tag that is not on disk yet; in CI the snapshot is restored from our own `dist`.
- **Prompts as files** — one markdown file per prompt under `prompts/`, the file name being the prompt
  id: YAML frontmatter for metadata, a jinja2 user-prompt template as the body, `_system.md` for the
  shared system prompt.

### Partial regeneration

`run --prompts <id>` computes the dependency closure of the target prompts and generates only what is
missing in it: dependencies are inputs, so they reuse their stored json unless it is missing or
schema-invalid. Nothing outside the closure is recomputed, and a skill left with no output at all is
dropped from `skills.jsonl`. The closure walks to dependencies, never to dependents: invalidating
`persona` leaves the `cover` recipe (and its picture) describing the older portrait — to redo that
follow-on work, name it: `invalidate --prompts persona,cover`.

## Adding a prompt

One markdown file is one prompt — no code change unless you need a new output schema (then register the
model in `models.py`):

```markdown
---
description: one line
output: IntroText          # a pydantic schema registered in models.py
depends_on: [scenario]     # DAG edges; omit for root prompts
---

请为下面的 skill 写……
{{ deps.scenario.text }}   # deps maps prompt ids to their parsed output objects
```

`_system.md` provides `{{ skill.name }}`, `{{ skill.description }}` and the full `{{ skill_md }}`
(capped at 20,000 characters), so a prompt file only has to describe the task. Then fill the angle in
for every skill — cached angles are reused, so only the new one costs calls:

```bash
skills-profiles run --prompts my_angle --limit 0
```

Add the prompt's id to `AGGREGATED_PROMPTS` in `outputs.py` to fold it into every `skills.jsonl` row,
and register its non-json suffixes in `PROMPT_ASSETS` there — that is how `cover` owns `cover.png`, and
why invalidating the prompt drops the rendered artifact with its recipe.

## Project layout

```
prompts/             # one markdown file per prompt (+ _system.md)
src/skills_profiles/
├── data.py          # mirror pointer + tarball + index parsing + stale detection
├── models.py        # Domain taxonomy + output schemas
├── prompts.py       # frontmatter + DAG ordering + jinja2 rendering
├── generate.py      # async DAG execution + resume + coverage
├── outputs.py       # json/md outputs + assets + index + invalidation
├── layout.py        # file/dir names shared by the snapshot and the artifacts
├── llm.py, images.py    # API clients + offline FakeLLM / FakeImages
└── config.py, logging.py, cli.py
tests/               # offline fixtures + end-to-end CLI tests
```

## Configuration

Resolution order (highest first): `SKILLS_PROFILES_*` env vars → local `.env` → built-in defaults.

| Variable | Default | Description |
|---|---|---|
| `SKILLS_PROFILES_MODEL` | `gpt-4.1-mini` | Any OpenAI-compatible chat model |
| `SKILLS_PROFILES_BASE_URL` | – | OpenAI-compatible endpoint |
| `SKILLS_PROFILES_API_KEY` | – | API key for the endpoint |
| `SKILLS_PROFILES_LIMIT` | `10` | Skills per run (`0` = all; cached ones are skipped, not counted) |
| `SKILLS_PROFILES_TOTAL_LIMIT` | `1000` | Skills the whole pipeline serves, most installed first — a ceiling on the dataset, not on one run (`0` = all) |
| `SKILLS_PROFILES_CONCURRENCY` | `2` | Max concurrent LLM calls / image requests, shared across skills and prompts |
| `SKILLS_PROFILES_OUTPUT_DIR` | `output` | Artifacts directory |
| `SKILLS_PROFILES_DATA_DIR` | `cache/skills-sh` | Upstream data directory |
| `SKILLS_PROFILES_PROMPTS_DIR` | `prompts` | Prompt markdown directory (plus `_system.md`) |
| `SKILLS_PROFILES_IMAGE_BASE_URL` | `https://api.siliconflow.cn/v1` | Text-to-image endpoint; covers are drawn from a service of their own |
| `SKILLS_PROFILES_IMAGE_API_KEY` | – | Its key (without one, `run` skips the render pass with a warning; `--dry-run` needs none) |
| `SKILLS_PROFILES_IMAGE_API_KEYS` | – | Extra keys, comma-separated: each key holds its own per-minute quota, so N keys render N times as fast |
| `SKILLS_PROFILES_IMAGE_RATE_LIMIT` | `2` | Max images per minute **per key** (the endpoint's documented quota; `0` = unbounded) |
| `SKILLS_PROFILES_IMAGE_MODEL` | `Kwai-Kolors/Kolors` | Any model the endpoint serves |
| `SKILLS_PROFILES_IMAGE_SIZE` | `1024x1024` | Checked against the sizes the endpoint documents per model |
| `SKILLS_PROFILES_IMAGE_STEPS` | `20` | `num_inference_steps` (1–100); `0` omits the field |
| `SKILLS_PROFILES_IMAGE_GUIDANCE` | `7.5` | `guidance_scale` (≤ 20, documented as Kolors-only); `0` omits it for other models |

## Publishing (GitHub Actions)

[`ci`](.github/workflows/ci.yml) checks every push and pull request (tests, lint, types); the two
manually-triggered workflows below share one publish lock (`concurrency: publish-dist`):

| Workflow | Pipeline | Tag |
|---|---|---|
| [`sync`](.github/workflows/sync.yml) | restore dist → sync upstream → `invalidate --stale` → publish | `dist-YYYY-MM-DD`, force-updated within a day |
| [`generate`](.github/workflows/generate.yml) | restore dist → `run --limit <input, default 10>` → publish | `dist-<base>-N`, base = newest sync tag, N increments |

```bash
gh workflow run generate.yml -f limit=50 -f concurrency=8   # complete 50 skills (text + covers)
gh workflow run sync.yml                                    # refresh upstream, drop stale profiles
```

Both share [restore-dist](.github/actions/restore-dist/action.yml) (one codeload request pulls the
branch back into `output/` and `cache/`, skipping the root pointer — a publish rewrites it and the
pipeline never reads it) and
[publish-dist](.github/actions/publish-dist/action.yml) (mirror the working dirs back to `dist`, write
the root-level `latest` pointer naming the tag it pushes, stamp `stats.json` with `publishedAt` plus the
mirror tag the bundled dataset was synced from, tag, prune). Pointer and stamp are written before the
commit, so a snapshot ships with its own identity, and the step fails unless `latest`, the tag and
`HEAD` agree or the published `stats.json` lost its stamp. The mirror ref comes from the dataset's own
marker, so whichever workflow publishes it cannot lag the data — and because [stamp-stats.sh](.github/actions/publish-dist/stamp-stats.sh)
strips the stamp back off, a run that changed nothing but the timestamp publishes nothing.
`dist` is the single atomic snapshot — the profiles at its root plus the `cache/skills-sh/`
dataset mirror — so **only `sync` ever touches upstream**, while `generate` reads what the last `sync`
published and adds the binary weight: `limit` caps one batch and `SKILLS_PROFILES_TOTAL_LIMIT` caps the
dataset, so that ceiling — not any single run — decides how many covers `dist` holds. History is pruned
to a rolling window (default `1 month`).

Required configuration (Settings → Secrets and variables → Actions):

| Where | Name | Example |
|---|---|---|
| Secret | `SKILLS_PROFILES_API_KEY` | the endpoint's API key |
| Secret | `SKILLS_PROFILES_IMAGE_API_KEY` | the text-to-image endpoint's key (optional: without it `generate` stays text-only) |
| Variable | `SKILLS_PROFILES_BASE_URL` | `https://api.b.ai/v1` |
| Variable | `SKILLS_PROFILES_MODEL` | `GLM-5.3-Flash` |
| Variable | `SKILLS_PROFILES_IMAGE_BASE_URL`, `SKILLS_PROFILES_IMAGE_MODEL`, `SKILLS_PROFILES_IMAGE_SIZE` | optional; default to the documented Kolors endpoint at `1024x1024` |
| Variable | `SKILLS_PROFILES_TOTAL_LIMIT` | optional; the built-in `1000` already bounds local and CI alike |

## Testing

The pipeline is verified offline: dataset parsing, the `latest` pointer's parsing and its refusal of
junk, the publish stamp's round trip (`stats.json` with `publishedAt` / `upstream` added and stripped
back off, so a no-op run stays recognisable), DAG ordering, template rendering, resume skip,
invalidation, dependency passing, markdown
rendering, the cover recipe's prompt/seed/payload construction, the endpoint's retry rules, the per-key
rate limiter, and a full CLI dry-run of `run` — no network access (`conftest.py` replaces
`data.download_file` with a fake serving a snapshot tarball built from the fixtures, and the upstream
pointer plus the image endpoint are reached only through a stubbed `httpx` call).

```bash
uv run pytest          # offline test suite
uv run ruff check .    # lint
uv run mypy            # types
```

[`ci`](.github/workflows/ci.yml) runs the same three on every push and pull request; both must pass
before a publish workflow is worth triggering.

Docs rule: every English document has a Chinese counterpart (`README.md` / `README.zh-CN.md`,
`DEVELOPING.md` / `DEVELOPING.zh-CN.md`) — keep both in sync, in the same pass.
