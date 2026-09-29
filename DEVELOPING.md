# Developing skills-profiles

The generator behind the dataset described in [README.md](README.md): it pulls each skill's
`SKILL.md` from the skill's own repository - the mirror's index says what exists, the repositories
hold what it is - and asks the Jev
(TypeSafe System One) endpoint one typed question - which closed domain category the skill belongs
to. A second producer, `skill_zh.py`, asks an OpenAI-compatible chat endpoint once for the
one-line description and then once per markdown piece of the body, and assembles the Chinese page
`SKILL.zh.md` by code, its front matter never left to the model. The two are parallel angles on
the same skill directory, and both are thin: the tree, the source, the prompt files, the settings,
the retried call, the atomic write and the command itself all live once in `common.py`;
`translate.py` is the chat endpoint library the page angle asks. The window, the lazy fetch and
the `jobs`-wide pool around them live in one driver, `batch.py`; the justfile only launches it.

中文: [DEVELOPING.zh-CN.md](DEVELOPING.zh-CN.md)

## Quickstart

Needs Python 3.12+, [uv](https://docs.astral.sh/uv/) and [`just`](https://just.systems); the two
endpoint keys go in a local `.env` (copy [`.env.example`](.env.example)).

```bash
uv sync
just sync                  # reconcile with the mirror: its listing, new sources, the catalog
just                       # build the first domain label, end to end - fetches its repository
just limit=0 build domain  # ... or every skill still unlabelled, whole snapshot, no cap
just build all             # both angles in one pool, over the shared window
just build skill_zh        # the second angle: build the first missing SKILL.zh.md
just clean domain          # the inverse: forget the first built label
```

Fake endpoint, real layout, no API calls and no credentials: `just dry=1 limit=5 build domain`
(and `just dry=1 build skill_zh`); the repositories are still fetched, so run it where the sources
already are or pass a local `repo_tarball`.

## The batch is `batch.py`

| Command              | What it does                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `just build <angle>` | `batch.py build <angle>`: the next `limit` skills still missing the angle's file (`domain`, `skill_zh`, or `all` for both in one pool over the shared window), most installed first. The order is the catalog's own (`OUTPUT_DIR/skills.jsonl`, the mirror's order, installs-descending) - parsed as jsonl, one row per listed skill. The window is the next `limit` skills this angle has not resolved: no angle file, and not a listed skill whose repository is already on disk without a `SKILL.md` (it can never be built). It is a count of work, not of positions, so repeated runs walk down the dataset. The driver then runs the producers in a `jobs`-wide pool, one call into a producer module per skill: each job fetches its repository just in time - the first job on a repository downloads and unpacks it, the rest wait on that one download - and a skill whose repository holds no source for it is skipped. A bare `just` is `build domain` with the default one-skill limit. |
| `just clean <angle>` | The inverse window, `batch.py clean <angle>`: the next `limit` skills that already HOLD the angle's file, in the same catalog order, with the file deleted. `build` then regenerates exactly those skills; `limit 0` cleans every built one, and `all` forgets both angles' files - the full-reset half that precedes `sync`. A single named skill outside the window is still built by running its script directly (`uv run python jev.py <id>` / `skill_zh.py <id>`).                                                                                                                                                                                                                                                                                                                                         |
| `just index`         | Write `<output_dir>/skills.jsonl` - the catalog: one flat line per skill the mirror lists, in the mirror's order, being the listing's own row (`id`, `installs`) joined with the `description` read out of that skill's `SKILL.md`, the `description_zh` in the `SKILL.zh.md` front matter, and the `domain` and `confidence` in `domain.json`. The joined fields are `null` while unknown. It reads the tree alone - no network, no calls - and rewrites the file whole. It writes the READMEs beside it from the same walk: see `readme.py` below.                                                                                                                                                                                                                                                            |
| `just sync`          | Reconcile with the mirror: pull its listing, the row set, the order and the installs. The sources are fetched lazily: a batch downloads a repository the first time it builds one of its skills, and the repository directory on disk is the cache, so nothing is fetched before it is needed and nothing twice. A repository a fresh listing adds a skill to is fetched again here, the new sources merged in beside the skills already built, and name-spelled aliases repaired over the whole tree.                                                                                                                                                                                                                                                                                                 |
| `just test`          | `uv run pytest`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |

`build` and `clean` are the two inverse verbs of one driver - `batch.py` - sharing the angle
(`domain`/`skill_zh`; clean additionally takes `all`) and the same catalog-order window; build
creates, clean deletes. `sync` is the driver's other subcommand.

| Variable       | Default                                                  | Meaning                                                                                                                                                                              |
| -------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `limit`        | `1`                                                      | The next N skills still missing the angle being built, in the catalog's order; `0` = all. One is the default, so a bare `just` is a smoke run. It counts work rather than positions. |
| `jobs`         | `32`                                                     | Producer calls in flight at once: the driver's thread pool.                                                                                                                          |
| `dry`          | –                                                        | `1` = fake endpoint, real layout: nothing is called.                                                                                                                                 |
| `output_dir`   | `output`                                                 | The published root: the skills (with the angles written beside them), the catalog and the READMEs.                                                                                   |
| `listing`      | the mirror's `dist` listing url                          | The mirror's listing `just sync` pulls fresh; a local `file://` url is how the tests run it.                                                                                         |
| `repo_tarball` | `https://codeload.github.com/{owner}/{repo}/tar.gz/HEAD` | Where a batch gets a repository's tarball; `{owner}` and `{repo}` are substituted per repository, and a `file://` template is how the tests run it.                                  |
| `fetch_jobs`   | `16`                                                     | Repository tarballs in flight at once: the downloader's pool.                                                                                                                        |
| `py`           | `uv run python`                                          | How to run the scripts (override with an absolute interpreter path in CI).                                                                                                           |

The knobs are `just` variables - set on the command line and nowhere else: `SKILLS_PROFILES_LIMIT=20
just` does _not_ work. `.env` belongs to the scripts and holds the two endpoints and their keys; the
justfile exports `output_dir`, `prompts_dir` and `dry`, and that export is the only handover between
the two.

Because an output has no prerequisites anywhere, **its existence is the entire cache** - the driver
checks the angle file per skill, so a batch that stopped halfway resumes at the first file that is
not there and never rebuilds one that is. The two files in a profile cache independently - a domain
label does not count as a zh page, or the reverse. That has three consequences:

- **Invalidation is `clean`.** `just clean <angle>` (or `rm`-ing an angle file in
  `output/skills/<id>/`) removes outputs; the next `build` of that angle regenerates them. Editing
  a prompt file (`_system.md`, `translate.md`, `translate_user.md`) does _not_ invalidate anything
  by itself - mtimes moving on every checkout would otherwise relabel the whole dataset for free.
- **A source is fetched once.** A repository is downloaded by the first job that builds one of its
  skills, and the repository directory on disk is the cache: `just sync` leaves the sources alone,
  so a source changes only when its repository directory is deleted. What sync does do is fetch
  again every repository the new listing adds a skill to, merging the new sources in, and name any
  skill the mirror dropped - its files stay in the tree until a hand decides about them. A listed
  skill whose repository holds no source for it can never be built, so the window skips it rather
  than retrying it forever.
- **Per-skill failures do not end a batch.** A job that raises (quota, connection) is reported by id,
  writes nothing, and the pool continues; CI records the error details and publishes the successful
  outputs. The next run retries the skills whose files are still missing. A window whose every job
  failed is a broken run: the batch exits `1` while the partial output stays published.

## The scripts

One job, one producer call. What the two commands do is one command - the shared skeleton in
`common.py` (`run`): parse the one skill argument, read the source, gate on its description, build
every request the angle makes (computed once), call, write the angle's one file renamed into
place, and turn a failure into one stderr line and a status. Each producer supplies only three
things: the requests, the calls that answer them, and its dry-run placeholder. The domain angle:

```bash
uv run python jev.py <owner>/<repo>/<slug>           # label exactly one skill
uv run python jev.py <owner>/<repo>/<slug> --print   # print the request and stop, calling nothing
```

`jev.py` has no "skip if it exists" check on purpose: deciding what to build is `batch.py`'s job.
Its whole contract with the caller is:

- **`<skill>`** is a skill's directory under `<output_dir>/skills`: its id with `:` and `&` spelled
  `_`, which is how the mirror's own tree is named.
- **The output** lands at `<output_dir>/skills/<skill>/domain.json`, renamed into place - a
  half-written one would be skipped as done by the next batch.
- **The source is cut at 20 000 characters**, on a line break, and the cut is announced.
- **The description is the front matter's `description`**, parsed as YAML, and it is the gate on a
  skill: a header that is missing, that does not parse, or that carries no description drops the
  skill - no call, no angle file, one line on stderr, status 1. The batch never reaches that case:
  `fetch.py` writes only a source that yields a description, so a skill it cannot lead with has no
  `SKILL.md` and the window leaves it alone.
- **Status** is 0 built, 1 an input or the endpoint was unusable, 2 bad arguments. A failure is one
  line rather than a traceback, because a batch of thousands of them is where a traceback stops
  being information.

The endpoint is not a chat one: `POST /v1/systemone` takes a `state` and typed `questions`, and
answers with typed `answers` - no messages, no `json_schema`, no free text. The `state` is rendered
from `prompts/_system.md`: the skill's name, its description, its `SKILL.md` body
with the front matter dropped, and the one extra layer `domain` gets - the skill's repository, as
its siblings' one-line descriptions, each cut to a hint and the count capped at 50 - because a
category is a property of a repository rather than of one file, and siblings disambiguate a lone,
ambiguous skill. The taxonomy lives in the code as one object: `CRITERIA` (the 13 categories and
their own words) and `INSTRUCTION` (the one rule: judge what a skill is for, not how it works),
handed to the endpoint as the `criteria` its answer is confined to - so there is no enum in a schema
and a decoder to keep in step. The whole answer is kept - the label, the confidence and the
distribution over all 13 categories; the catalog takes the first two and leaves the rest in the
profile. A dropped first call after the endpoint has been idle arrives as a timeout and is retried;
a rejected body (400) is not.

The zh page angle is the chat one:

```bash
uv run python skill_zh.py <owner>/<repo>/<slug>           # build exactly one Chinese page
uv run python skill_zh.py <owner>/<repo>/<slug> --print   # print every request as one json array
```

`skill_zh.py` and the chat library it asks, `translate.py`, share the same `common.Config`:
the shared settings (timeout, retries, dry run, the paths), the typed endpoint's three, and the
translation ones beside them. What differs is only the call: a normal OpenAI-compatible
`POST {base}/chat/completions` with a Bearer key, `temperature` 0, and the two turns rendered from
`prompts/translate.md` and `prompts/translate_user.md` with the one target language fixed in code -
a faithful-translation system instruction (preserve meaning, tone, paragraph and formatting; keep
code and placeholders; follow the supplied context and terminology) and the `Translate to …:` user
turn carrying the text to translate. Deep thinking is on by default: the MaaS extension
`enable_thinking: true` plus `max_tokens: 32768` (the documented ceiling - the endpoint's own 2048
default would cut the reasoning off). The model reasons into `reasoning_content` first; that draft
is never read (`translation()` takes `choices[0].message.content` alone) and never written to the
angle file - both knobs are settings, `TRANSLATE_ENABLE_THINKING` and `TRANSLATE_MAX_TOKENS`. The
description is a Jinja variable, never part of the template text, so braces in a skill's own line
are data. It sends the description alone - no `SKILL.md`, no source cut. `choices[0].message.content`
is the whole answer: an empty body is an unusable endpoint, not an empty translation. The retry
rules are `common.py`'s, shared with the domain angle: transient status codes and connection errors
back off exponentially, a 4xx fails at once. Defaults point at Xunfei Xingchen MaaS serving
Spark-X2.5-4B; the model id the console shows may differ, hence the env override. This is
`translate.py`, a library rather than a command - `skill_zh.py` is its only caller.

`skill_zh.py` shares the command shape - same command line, same gate, same exit codes, same
rename-into-place write - and makes every call the page needs, in order: the description first,
then the body. The body is sent without its front matter, rendered from `prompts/skill_zh.md` and
`prompts/skill_zh_user.md`. A body too long for one answer is cut on its own markdown seams (blank
lines outside a code fence; a block with no seam of its own is cut between lines) into pieces of
`MAX_CHUNK_CHARS` characters or fewer, each translated in its own call over the shared endpoint and
fallback, each carrying the seam it was cut on - so a block cut between its lines rejoins on the
line's own newline, and a cut table or list comes back the one block it was. The page is then
assembled by code - a front matter of `name` (the source's own) and the Chinese description, over
the pieces rejoined on those seams - and written only when every call came back: a half-translated
page must never pass for a whole one, and the front matter is the one strictly parsed part of the
page, so it is never left to the model. An empty body, like a missing description, drops the skill
with no call and no file - the same one-line/exit-1 gate as every other unusable input, not a
traceback. The requests for the page are built once and shared by `--print` and the run.

`index.py` joins the mirror's listing with the tree and writes `output/skills.jsonl`. The CLI is
the offline verb - it takes no argument, and the existing catalog carries the installs in the
same order; the driver's sync calls the same `build()` in-process with the fresh listing, so
its installs join in without a process between them. Each row carries the listing's fields, then `description`, `description_zh`, `domain`
and `confidence` - the angles read from their own files, independently and missing independently
(the Chinese page stays in its skill directory; a consumer falls back to the original without it),
and every listed skill is a row, its joined fields `null` until the tree fetches and builds it.
The same run writes `output/README.md` and its Chinese twin - `readme.py` holds the words, `index.py`
hands it the numbers - the one thing the catalog cannot answer: **how much of the dataset is
labelled** (domain coverage and zh-page coverage).

`fetch.py` is the other side: the driver downloads the window's repositories - each `owner/repo` of
the skills about to be built, one codeload tarball each (`--repo-tarball` says where), `fetch_jobs`
at a time, and only the ones not already on disk - and `fetch.py` streams each tarball once. A skill is
a `SKILL.md` under a subdirectory, named after it; the repository's own root `SKILL.md` is its
readme, not a skill. A source is taken only when it yields a description, and only once per name.
The mirror keys a skill by the kebab case of its front matter `name`, the tree by the directory:
when an author spells the two apart, the source lands under both spellings, and `just sync`
repairs the tree already fetched the same way (`fetch.write_aliases`), so a mirror row keyed by
either spelling finds a source and gets built.
The catalog is not consulted here - a skill the listing has not reached yet is unpacked all the
same. The repository directory is created either way, so its presence is the cache: a repository
that holds no source for a listed skill leaves that skill an empty directory. A repository that
will not download is simply not here: its skills fail and the batch carries on.

## How it works

```
                        output/  ── the whole artifact, published as one directory
                          │
mirror `dist` listing ────┼──► skills.jsonl         the catalog: one row per listed skill, and the
   (batch sync pulls      │                          order every batch works in (installs-descending)
    it in, never keeps it)│
                          ├──► batch.py walks the catalog as jsonl
                                      │
                        run the producers, JOBS at a time, one producer call per skill, each
                        fetching its repository just in time (once - the repo dir is the cache);
                        the same pool for domain and skill_zh
                                      │
                        skills/<id>/SKILL.md + domain.json + SKILL.zh.md (the repo dir is the cache)
                                      │
                index.build() ──► skills.jsonl + READMEs: the mirror's rows × the angles' files
```

The driver is a plain Python module behind a thin `just` launcher, not a build system: **existence
is the skip**, the order is the mirror's own read straight out of the jsonl (so leading dots and
`_` in repo names need no shell tricks), and the pool is a `ThreadPoolExecutor` with `jobs`
workers running one producer call each, in this process - no jobserver and no per-minute pace;
every worker runs its next skill as soon as the last returns, and a transient 429 is absorbed by
the client's own exponential backoff, with jitter so a throttled pool does not all knock again at
once.

## Project layout

```
justfile                # a thin launcher: each recipe sets the knobs and runs batch.py or a script
batch.py                # the orchestrator: the jsonl window, the lazy fetch, the producer pool, sync
common.py               # the kernel both producers share: Config, the tree, the source, prompts,
                        # the retried call, the atomic write, and the run() command skeleton
fetch.py                # the sources: a repository's skills unpacked into skills/, once each
jev.py                  # the domain angle: the taxonomy, the state, the typed question
translate.py            # the translation library: one chat call, shaped over the shared command
skill_zh.py             # the page angle: the SKILL.md body translated, one .md written
index.py                # the catalog and its numbers: one flat jsonl, and the facts a README is
readme.py               # the page: those numbers said for a reader, in both languages
prompts/_system.md       # the state template: name, description, body, and the repository block
prompts/translate.md     # the translation system template: the faithful-translation task, {{to}}
prompts/translate_user.md  # the translation user template: "Translate to {{to}}:" carrying {{text}}
prompts/skill_zh.md      # the page system template: translate the document, keep the formatting
prompts/skill_zh_user.md # the page user template: "Translate to {{to}}:" carrying the body
tests/                  # offline unit tests; the batch is driven in-process in test_batch.py,
                        # with only the justfile launcher checks running `just`
.github/                # ci on every push and pull request, sync and publish by hand
```

## Configuration

Resolution order (highest first): `SKILLS_PROFILES_*` env vars → local `.env` → built-in defaults.
An empty value means "not set".

| Variable                                      | Default                    | Description                                                                                                                                                              |
| --------------------------------------------- | -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `SKILLS_PROFILES_API_KEY`                     | –                          | The typed endpoint's key; no key means no call                                                                                                                           |
| `SKILLS_PROFILES_BASE_URL`                    | TypeSafe's System One path | Where `jev.py` posts; nothing else does                                                                                                                                  |
| `SKILLS_PROFILES_MODEL`                       | `jev-latest`               | The System One model, an alias over the pinned version                                                                                                                   |
| `SKILLS_PROFILES_TRANSLATE_API_KEY`           | –                          | The chat endpoint's key; `translate.py` is the only caller                                                                                                               |
| `SKILLS_PROFILES_TRANSLATE_BASE_URL`          | Xingchen MaaS v2 root      | The OpenAI-compatible root; `translate.py` posts to `{base}/chat/completions`                                                                                            |
| `SKILLS_PROFILES_TRANSLATE_MODEL`             | `spark-x2.5-4b`            | The chat model id; spell it as the console's service page shows it                                                                                                       |
| `SKILLS_PROFILES_TRANSLATE_ENABLE_THINKING`   | `true`                     | Send the MaaS `enable_thinking` switch; the model reasons before it answers (`reasoning_content`)                                                                        |
| `SKILLS_PROFILES_TRANSLATE_MAX_TOKENS`        | `32768`                    | The answer's token budget including the reasoning; the endpoint's own default is 2048                                                                                    |
| `SKILLS_PROFILES_TRANSLATE_TIMEOUT`           | `120`                      | Seconds per request for the chat endpoint alone: a thinking call reasons before it answers and routinely runs past the typed endpoint's patience, so this is its own knob |
| `SKILLS_PROFILES_TRANSLATE_FALLBACK_API_KEY`  | –                          | The fallback endpoint's key; unset turns the fallback off - a failed skill fails as before                                                                               |
| `SKILLS_PROFILES_TRANSLATE_FALLBACK_BASE_URL` | Agnes AI root              | Where a skill the chat endpoint fails is retried, once: the same OpenAI-compatible call, only the model swapped - and the MaaS-only thinking switch left out             |
| `SKILLS_PROFILES_TRANSLATE_FALLBACK_MODEL`    | `agnes-3.0-flash`          | The fallback model id; a reasoning model, read the same way (`reasoning_content` beside `content`)                                                                       |
| `SKILLS_PROFILES_TIMEOUT`                     | `20`                       | Seconds per request for the typed endpoint: it answers in one to three, and drops a first call after idle                                                                 |
| `SKILLS_PROFILES_MAX_RETRIES`                 | `3`                        | Extra attempts, for a dropped call or a busy gateway; both endpoints                                                                                                     |
| `SKILLS_PROFILES_DRY_RUN`                     | `false`                    | Fake both producers: no API calls                                                                                                                                        |
| `SKILLS_PROFILES_OUTPUT_DIR`                  | `output`                   | The published root: the skills (with the angles written beside them), the catalog and the READMEs                                                                        |
| `SKILLS_PROFILES_PROMPTS_DIR`                 | `prompts`                  | The directory holding `_system.md`, `translate.md`, `translate_user.md`, `skill_zh.md` and `skill_zh_user.md`                                                            |

## Testing

The suite is offline: `conftest.py` writes a fake snapshot tree, and constructing a real HTTP client
fails loudly, so a test can never call out even with a local `.env` full of keys.

- `tests/test_common.py` covers what the two producers share - the source reading (front matter,
  YAML descriptions, the 20 000-character cut), the repository siblings and their caps, the prompt
  files, the atomic write, and the retry reading (a dropped call retried, a rejected body not).
- `tests/test_jev.py` covers the domain angle itself: the taxonomy as one object, the body a call
  posts (a state and typed questions, no messages), the guard on an answer outside the closed set,
  the state the repository reaches, and the command - the gate, the exit codes, a request printed
  without a key.
- `tests/test_translate.py` covers the chat library the page angle asks: the request body (the two
  prompt files rendered to system and user turns), the description carried as a Jinja value, the
  URL join and Bearer header, the retried call (a dropped one retried, a rejected body not), the
  answer parsing (an empty or truncated one rejected), and the fallback hand-over.
- `tests/test_index.py` covers the catalog and its numbers (one row per listed skill, its fields
  `null` until built, and `description_zh` joining independently); `tests/test_readme.py` the
  bilingual page; `tests/test_batch.py` drives `batch.py` in-process - the window, the lazy fetch
  (a repository fetched once, a failed one failing only its skills), the per-skill failure logs,
  `sync` and the clean inverse window - against local `file://` tarballs. Only the launcher
  checks (the default recipe, the command-line-only dry knob, the pool flags reaching the command)
  still run `just` as a subprocess.
- `tests/test_skill_zh.py` covers the page angle: the requests (description first, then the body
  pieces; the body as a Jinja value, the front matter never sent), the output (front matter as
  published over the translation, one `SKILL.zh.md`), the length gates, and the command - the
  exit codes and the request array printed without a key.

```bash
uv run pytest                                # offline test suite
uv run ruff check .                          # lint
uv run mypy                                  # types
just dry=1 limit=2 build domain              # the batch itself, end to end
just dry=1 build skill_zh                    # the second batch, end to end
uv run python jev.py <owner>/<repo>/<slug> --print   # dev only: see a request without calling
```

There is deliberately no `just render`: printing a request is a dev-only check, so it stays a
script flag run directly, while the justfile holds the production verbs.

## CI

Four workflows, and each one is thin: the work they do is `just`.

| workflow      | trigger                     | does                                                                                                                                                                                                                                                         |
| ------------- | --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `ci.yml`      | every push and pull request | `uv sync`, `ruff check .`, `mypy`, `pytest`, with `just` installed. Offline.                                                                                                                                                                                 |
| `sync.yml`    | manual                      | `restore-dist` → `just sync` → `publish-dist` (`date`). Pulls the mirror's listing and rewrites the catalog; no model is called.                                                                                                                             |
| `publish.yml` | manual                      | `restore-dist` → `just build <angle> limit=… jobs=…` (`domain`, `skill_zh`, or `all` in one pool) → `just index` → `publish-dist` (`date-counter`). Needs the chosen angles' secrets and variables. |
| `invalidate.yml` | manual                   | `restore-dist` → `just limit=0 clean <angle>` → `just index` → `publish-dist`. Forgets every built output of the chosen angle - the one remote invalidation path, run when the taxonomy or the prompts changed - and publishes the tree without them; no model calls. The next publish rebuilds the angle from scratch. |

Docs rule: every English document has a Chinese counterpart — keep both in sync, in the same pass.
