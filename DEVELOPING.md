# Developing skills-profiles

The generator behind the dataset described in [README.md](README.md): it reads each skill's
`SKILL.md` from [skills-sh-mirror](https://github.com/skill-one/skills-sh-mirror) and asks the Jev
(TypeSafe System One) endpoint one typed question - which closed domain category the skill belongs
to. A second producer, `translate.py`, asks an OpenAI-compatible chat endpoint one free-text
question - the skill's one-line description in, Chinese out - and a third, `skill_zh.py`, asks the
same endpoint to translate the `SKILL.md` body into a Chinese page. The three are parallel angles
on the same profile directory, and all are thin: the tree, the source, the prompt files, the
settings, the retried call, the atomic write and the command itself all live once in `common.py`.

中文: [DEVELOPING.zh-CN.md](DEVELOPING.zh-CN.md)

## Quickstart

Needs Python 3.12+, [uv](https://docs.astral.sh/uv/) and [`just`](https://just.systems); the two
endpoint keys go in a local `.env` (copy [`.env.example`](.env.example)).

```bash
uv sync
just sync             # fetch the mirror into output/skills and output/upstream
just                  # label the first skill, end to end
just limit=0          # ... or every skill still unlabelled, whole snapshot, no cap
just translate        # the second angle: translate the first missing description_zh
just skill-zh         # the third angle: the SKILL.md body in Chinese
```

Offline, no API calls and no credentials: `just dry=1 limit=5` (and `just dry=1 translate`,
`just dry=1 skill-zh`).

## The batch is `just`

| Command                         | What it does                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `just`                          | Label the next `limit` skills still missing `domain.json`, most installed first. The order is the catalog's own (`OUTPUT_DIR/skills.jsonl`, installs-descending) filtered to rows with a description and a `SKILL.md` on disk; with no catalog it is the directory listing in path order. The window is the first `limit` of those skills - a count of work, not of positions, so repeated runs walk down the dataset. The recipe feeds them to an `xargs -P` pool running `jev.py`. `jobs` is the whole concurrency story.                                                                        |
| `just translate`                | The same batch for the second angle: the next `limit` skills still missing `description_zh.json`, the same ordering and the same pool, running `translate.py`. Every modifier below works identically.                                                                                                                                                                                                                                                                                                                                                                                             |
| `just skill-zh`                 | The same batch for the third angle: the next `limit` skills still missing `skill_zh.md`, the same ordering and the same pool, running `skill_zh.py`. Every modifier below works identically.                                                                                                                                                                                                                                                                                                                                                                                                       |
| `just one <skill>`              | Label exactly one skill, whether or not the batch has reached it. The only way to address one skill - and the only way to rebuild one without the batch skipping it.                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `just translate-one <skill>`    | Translate exactly one skill, inside or outside the window.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `just skill-zh-one <skill>`     | Translate exactly one skill's SKILL.md body, inside or outside the window.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `just render <skill>`           | Print the request one label would send - the state and the typed question - calling nothing.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `just translate-render <skill>` | Print the request one translation would send - the two turns rendered from the translate templates - calling nothing.                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| `just invalidate`               | Delete every `domain.json`, so the next run relabels the whole window.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| `just invalidate-translate`     | Delete every `description_zh.json`, so the next translate run rebuilds the whole window.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| `just invalidate-skill-zh`      | Delete every `skill_zh.md`, so the next skill-zh run rebuilds the whole window.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `just index`                    | Write `<output_dir>/skills.jsonl` - the catalog: one flat line per skill the mirror lists, in the mirror's order, being the mirror's own row (`id`, `installs`, `hash`, `fetchedAt`) joined with the `description` read out of that skill's `SKILL.md`, the `description_zh` in `profiles/<id>/description_zh.json`, and the `domain` and `confidence` in `profiles/<id>/domain.json`. The joined fields are `null` while unknown. It reads the tree alone - no network, no calls - and rewrites the file whole. It writes the READMEs beside it from the same walk: see `readme.py` below. |
| `just sync`                     | Download the whole upstream `dist` branch as one tarball and unpack it: the skill directories - stripped to their `SKILL.md` - into `output_dir/skills`, and of the mirror's own files only the ones the tree reads (its index, `latest`, `stats.json`) into `output_dir/upstream`. Then rewrite the catalog. The fetch lands in a scratch directory and the swap happens only once it is whole; a guard refuses to replace a `skills/` that is not a snapshot. Pure data: it never touches a generated profile.                                                                                                                                                                     |
| `just refresh`                  | `just sync`, plus the consequence: the catalog as it was before the sync is kept aside, and the whole profile - both files - of every skill whose source content hash moved is deleted. A skill that vanished upstream keeps its profile.                                                                                                                                                                                                                                                                                                                                                          |
| `just clean`                    | Drop what was generated: `output_dir/profiles`, the catalog and the READMEs. The skill directories and the mirror's own files stay.                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| `just test`                     | `uv run pytest`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |

The three batches are one recipe body - the `[script] build angle:` parameterized recipe, with the
angle choosing the script (`jev.py` vs `translate.py` vs `skill_zh.py`), the file that means "done",
and the label in the failure log; `default`, `translate` and `skill-zh` just call it.

| Variable     | Default                                | Meaning                                                                                                                                                                              |
| ------------ | -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `limit`      | `1`                                    | The next N skills still missing the angle being built, in the catalog's order; `0` = all. One is the default, so a bare `just` is a smoke run. It counts work rather than positions. |
| `jobs`       | `32`                                   | Calls in flight at once (`xargs -P`).                                                                                                                                                |
| `dry`        | –                                      | `1` = fake endpoint, real layout: nothing is called.                                                                                                                                 |
| `output_dir` | `output`                               | The published root, where all four layers live.                                                                                                                                      |
| `snapshot`   | the codeload url for the `dist` branch | What `just sync` fetches; a local `file://` tarball is how the tests run it.                                                                                                         |
| `py`         | `uv run python`                        | How to run the script (override with an absolute interpreter path in CI).                                                                                                            |

The knobs are `just` variables - set on the command line and nowhere else: `SKILLS_PROFILES_LIMIT=20
just` does _not_ work. `.env` belongs to the scripts and holds the two endpoints and their keys; the
justfile exports `output_dir`, `prompts_dir` and `dry`, and that export is the only handover between
the two.

Because an output has no prerequisites anywhere, **its existence is the entire cache** - checked per
skill with a `[ -f ]`, so a batch that stopped halfway resumes at the first file that is not there
and never rebuilds one that is. The two files in a profile cache independently - a domain label does
not count as a translation, or the reverse. That has three consequences:

- **Invalidation is deletion.** `just invalidate` / `just invalidate-translate` (or `rm`-ing either
  file in `output/profiles/<id>/`) remove outputs; the next run regenerates them. Editing a
  prompt file (`_system.md`, `translate.md`, `translate_user.md`) does _not_ invalidate anything
  by itself - mtimes moving on every checkout would otherwise relabel the whole dataset for free.
- **The one thing that does invalidate is a new snapshot.** `just refresh` compares the index the
  download replaced with the one it brought and removes the whole profile of every skill whose
  content hash moved - both angles at once, since both came from that `SKILL.md`. A skill that
  vanished upstream is _not_ dropped: its profile was paid for.
- **Per-skill failures do not end a batch.** A job that raises (quota, connection) is reported by id,
  writes nothing, and the pool continues; CI records the error details and publishes the successful
  outputs. The next run retries the skills whose files are still missing.

## The scripts

One job, one call per process. What the two commands do is one command - the shared skeleton in
`common.py` (`run`): parse the one skill argument, read the source, gate on its description, build
the request, call, write the angle's one json file renamed into place, and turn a failure into one
stderr line and a status. Each producer supplies only three things: the request, the call that
answers it, and its dry-run placeholder. The domain angle:

```bash
uv run python jev.py <owner>/<repo>/<slug>           # label exactly one skill
uv run python jev.py <owner>/<repo>/<slug> --print   # print the request and stop, calling nothing
```

`jev.py` has no "skip if it exists" check on purpose: deciding what to build is the justfile's job.
Its whole contract with the caller is:

- **`<skill>`** is a skill's directory under `<output_dir>/skills`: its id with `:` and `&` spelled
  `_`, which is how the mirror's own tree is named.
- **The output** lands at `<output_dir>/profiles/<skill>/domain.json`, renamed into place - a
  half-written one would be skipped as done by the next batch.
- **The source is cut at 20 000 characters**, on a line break, and the cut is announced.
- **The description is the front matter's `description`**, parsed as YAML, and it is the gate on a
  skill: a header that is missing, that does not parse, or that carries no description drops the
  skill - no call, no file, one line on stderr, status 1.
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

The translation angle mirrors it:

```bash
uv run python translate.py <owner>/<repo>/<slug>           # translate exactly one skill
uv run python translate.py <owner>/<repo>/<slug> --print   # print the request and stop, calling nothing
```

`translate.py` is deliberately the same shape as `jev.py` - same command line, same gate (no
description, status 1), same exit codes, same rename-into-place write at
`<output_dir>/profiles/<skill>/description_zh.json` as `{description_zh}`, same dry-run switch (a
`【占位】` placeholder, so the layout is exercised without a key). Both take the same `common.Config`

- the shared settings (timeout, retries, dry run, the paths), the typed endpoint's three, and the
  translation ones beside them. What differs is only the call: a normal OpenAI-compatible
  `POST {base}/chat/completions` with a Bearer key, `temperature` 0, and the two turns rendered from
  `prompts/translate.md` and `prompts/translate_user.md` with the one target language fixed in code -
  a faithful-translation system instruction (preserve meaning, tone, paragraph and formatting; keep
  code and placeholders; follow the supplied context and terminology) and the `Translate to …:` user
  turn carrying the one description. Deep thinking is on by default: the MaaS extension
  `enable_thinking: true` plus `max_tokens: 32768` (the documented ceiling - the endpoint's own 2048
  default would cut the reasoning off). The model reasons into `reasoning_content` first; that draft
  is never read (`translation()` takes `choices[0].message.content` alone) and never written to the
  angle file - both knobs are settings, `TRANSLATE_ENABLE_THINKING` and `TRANSLATE_MAX_TOKENS`. The
  description is a Jinja variable, never part of the template text, so braces in a skill's own line
  are data. It sends the description alone - no `SKILL.md`, no source cut. `choices[0].message.content`
  is the whole answer: an empty body is an unusable endpoint, not an empty translation. The retry
  rules are `common.py`'s, shared with the domain angle: transient status codes and connection errors
  back off exponentially, a 4xx fails at once. Defaults point at Xunfei Xingchen MaaS serving
  Spark-X2.5-4B; the model id the console shows may differ, hence the env override.

The third angle mirrors it once more:

```bash
uv run python skill_zh.py <owner>/<repo>/<slug>           # translate exactly one skill's body
uv run python skill_zh.py <owner>/<repo>/<slug> --print   # print the request and stop, calling nothing
```

`skill_zh.py` is the same shape again - same command line, same gate, same exit codes, same
rename-into-place write - with two differences. It sends the SKILL.md *body* (the front matter is
identifying metadata, and the catalog and the other angle files already carry it), rendered from
`prompts/skill_zh.md` and `prompts/skill_zh_user.md`, and it writes the one text file
`<output_dir>/profiles/<skill>/skill_zh.md`: the translation alone. A body past `MAX_BODY_CHARS`
(60 000 characters, in the script) is unusable input - a
half-translated page must never pass for a whole one - and, like a missing description, drops the
skill with no call and no file.

`index.py` joins the mirror's rows with the tree and writes `output/skills.jsonl`. It has no
arguments, no network and no call, and it is not in the build's path: `just index` is a verb you run
when you want the catalog, and `just sync` runs it because a sync moves the source layer under it.
Each row carries the mirror's fields, then `description`, `description_zh`, `domain` and
`confidence` - the angles read from their own files, independently and missing independently
(the Chinese page stays in its profile; a consumer falls back to the original without it). The same run
writes `output/README.md` and its Chinese twin - `readme.py` holds the words, `index.py` hands it
the numbers - the one thing the catalog cannot answer: **how much of the dataset is labelled**
(domain coverage; translation coverage is not on the page). It reads the snapshot's own identity
(`upstream/latest`, `upstream/stats.json`) rather than stamping a wall clock, so a publish with
nothing new spends no version number.

`stale.py` does the one comparison a shell is bad at: two catalogs in, the ids whose content hash
moved out - minus the ones the new one no longer holds, which are nobody's to delete. `just refresh`
is `sync` and it, in that order.

## How it works

```
                        output/  ── the whole artifact, published as one directory
                          │
mirror `dist` branch ─────┼──► skills/<id>/**      the source page every angle reads, SKILL.md alone
     (`just sync`)        │                          not an installation: the full skill is at its url
                          ├──► upstream/**         the mirror's own files the tree reads, its index above all
                          │
                          └─► the justfile walks the catalog
                                      │
                        `just` labels what is missing, JOBS at a time
                        `just translate` translates what is missing, the same pool
                        `just skill-zh` translates the pages, the same pool
                                      │
                        profiles/<id>/domain.json + description_zh.json + skill_zh.md
                                      │
                `just index` ──► skills.jsonl + READMEs: upstream × skills/ × profiles/
```

The runner is a command runner, not a build system: **existence is the skip**, the order is the
mirror's own (a `find` rather than a glob, because `.claude` is a repo name people use, and
`LC_ALL=C sort` because plain `sort` moves `_` around), and the pool is plain `xargs -P jobs` with
no jobserver and no per-minute pace - every worker runs its next call as soon as the last returns;
a transient 429 is absorbed by the client's own exponential backoff.

## Project layout

```
justfile                # the orchestrator: sync, the shared build-angle batch, the cache policy
common.py               # the kernel both producers share: Config, the tree, the source, prompts,
                        # the retried call, the atomic write, and the run() command skeleton
jev.py                  # the domain angle: the taxonomy, the state, the typed question
translate.py            # the translation angle: one chat call, shaped over the shared command
skill_zh.py             # the page angle: the SKILL.md body translated, one .md written
index.py                # the catalog and its numbers: one flat jsonl, and the facts a README is
readme.py               # the page: those numbers said for a reader, in both languages
stale.py                # the comparison: two catalogs in, the changed skills' profiles out
prompts/_system.md       # the state template: name, description, body, and the repository block
prompts/translate.md     # the translation system template: the faithful-translation task, {{to}}
prompts/translate_user.md  # the translation user template: "Translate to {{to}}:" carrying {{text}}
prompts/skill_zh.md      # the page system template: translate the document, keep the formatting
prompts/skill_zh_user.md # the page user template: "Translate to {{to}}:" carrying the body
tests/                  # offline unit tests plus a just end-to-end suite
.github/                # ci on every push and pull request, sync and publish by hand
```

## Configuration

Resolution order (highest first): `SKILLS_PROFILES_*` env vars → local `.env` → built-in defaults.
An empty value means "not set".

| Variable                                    | Default                  | Description                                                                                                                                                              |
| ------------------------------------------- | ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `SKILLS_PROFILES_API_KEY`                   | –                        | The typed endpoint's key; no key means no call                                                                                                                           |
| `SKILLS_PROFILES_BASE_URL`                  | 302.AI's System One path | Where `jev.py` posts; nothing else does                                                                                                                                  |
| `SKILLS_PROFILES_MODEL`                     | `jev-latest`             | The System One model, an alias over the pinned version                                                                                                                   |
| `SKILLS_PROFILES_TRANSLATE_API_KEY`         | –                        | The chat endpoint's key; `translate.py` is the only caller                                                                                                               |
| `SKILLS_PROFILES_TRANSLATE_BASE_URL`        | Xingchen MaaS v2 root    | The OpenAI-compatible root; `translate.py` posts to `{base}/chat/completions`                                                                                            |
| `SKILLS_PROFILES_TRANSLATE_MODEL`           | `spark-x2.5-4b`          | The chat model id; spell it as the console's service page shows it                                                                                                       |
| `SKILLS_PROFILES_TRANSLATE_ENABLE_THINKING` | `true`                   | Send the MaaS `enable_thinking` switch; the model reasons before it answers (`reasoning_content`)                                                                        |
| `SKILLS_PROFILES_TRANSLATE_MAX_TOKENS`      | `32768`                  | The answer's token budget including the reasoning; the endpoint's own default is 2048                                                                                    |
| `SKILLS_PROFILES_TIMEOUT`                   | `20`                     | Seconds per request, for both endpoints: they answer in one to three, and drop a first call after idle. A thinking translation is slower - raise it (120) for that batch |
| `SKILLS_PROFILES_MAX_RETRIES`               | `3`                      | Extra attempts, for a dropped call or a busy gateway; both endpoints                                                                                                     |
| `SKILLS_PROFILES_DRY_RUN`                   | `false`                  | Fake both producers: no API calls                                                                                                                                        |
| `SKILLS_PROFILES_OUTPUT_DIR`                | `output`                 | The published root: skills, profiles, upstream and catalog                                                                                                               |
| `SKILLS_PROFILES_PROMPTS_DIR`               | `prompts`                | The directory holding `_system.md`, `translate.md` and `translate_user.md`                                                                                               |

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
- `tests/test_translate.py` covers the second angle the same way: the request body (the two prompt
  files rendered to system and user turns, no state), the description carried as a Jinja value, the
  URL join and Bearer header, an empty answer rejected, the dry-run placeholder, and the command -
  the gate, the exit codes, a request printed without a key.
- `tests/test_index.py` covers the catalog and its numbers (including `description_zh` joining
  independently); `tests/test_readme.py` the bilingual page; `tests/test_stale.py` the hash
  comparison; `tests/test_just.py` drives the justfile itself - the batches, the window, the pool,
  the cache, `sync`, `refresh`, `invalidate` for every angle - against a local tarball.
- `tests/test_skill_zh.py` covers the third angle: the request (the body as a Jinja value, the
  front matter never sent), the output (front matter as published over the translation, one
  `skill_zh.md`), the length gate, and the command - the gate, the exit codes, a request printed
  without a key.

```bash
uv run pytest          # offline test suite
uv run ruff check .    # lint
uv run mypy            # types
just dry=1 limit=2     # the batch itself, end to end
just dry=1 translate   # the second batch, end to end
just dry=1 skill-zh    # the third batch, end to end
```

## CI

Three workflows, and each one is thin: the work they do is `just`.

| workflow      | trigger                     | does                                                                                                                                                                                                                                                           |
| ------------- | --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ci.yml`      | every push and pull request | `uv sync`, `ruff check .`, `mypy`, `pytest`, with `just` installed. Offline.                                                                                                                                                                                   |
| `sync.yml`    | manual                      | `restore-dist` → `just refresh` → `publish-dist` (`date`). Replaces the dataset and retires what it invalidates; no model calls and no key.                                                                                                                    |
| `publish.yml` | manual                      | `restore-dist` → `just limit=… jobs=…` for the chosen `angle` (`domain`, `translate`, or `both` - domain then translate) → `just index` → `publish-dist` (`date-counter`). Needs the chosen angles' secrets and variables; `replace` drops those angles first. |

Docs rule: every English document has a Chinese counterpart — keep both in sync, in the same pass.
