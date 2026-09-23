# Developing skills-profiles

The generator behind the dataset described in [README.md](README.md): it reads each skill's
`SKILL.md` from [skills-sh-mirror](https://github.com/skill-one/skills-sh-mirror) and asks the Jev
(TypeSafe System One) endpoint one typed question - which closed domain category the skill belongs
to.

中文: [DEVELOPING.zh-CN.md](DEVELOPING.zh-CN.md)

## Quickstart

Needs Python 3.12+, [uv](https://docs.astral.sh/uv/) and [`just`](https://just.systems); the
endpoint key goes in a local `.env` (copy [`.env.example`](.env.example)).

```bash
uv sync
just sync             # fetch the mirror into output/skills and output/upstream
just                  # label the first skill, end to end
just limit=0          # ... or every skill still unlabelled, whole snapshot, no cap
```

Offline, no API calls and no credentials: `just dry=1 limit=5`.

## The batch is `just`

| Command             | What it does |
| ------------------- | ------------ |
| `just`              | Label the next `limit` skills still missing `domain.json`, most installed first. The order is the catalog's own (`OUTPUT_DIR/skills.jsonl`, installs-descending) filtered to rows with a description and a `SKILL.md` on disk; with no catalog it is the directory listing in path order. The window is the first `limit` of those skills - a count of work, not of positions, so repeated runs walk down the dataset. The recipe feeds them to an `xargs -P` pool running `jev.py`. `jobs` is the whole concurrency story. |
| `just one <skill>`  | Label exactly one skill, whether or not the batch has reached it. The only way to address one skill - and the only way to rebuild one without the batch skipping it. |
| `just render <skill>` | Print the request one label would send - the state and the typed question - calling nothing. |
| `just invalidate`   | Delete every `domain.json`, so the next run relabels the whole window. |
| `just index`        | Write `<output_dir>/skills.jsonl` - the catalog: one flat line per skill the mirror lists, in the mirror's order, being the mirror's own row (`id`, `installs`, `url`, `hash`, `fetchedAt`) joined with the `description` read out of that skill's `SKILL.md`, and the `domain` and `confidence` in `profiles/<id>/domain.json`. Both are `null` while unknown. It reads the tree alone - no network, no calls - and rewrites the file whole. It writes the READMEs beside it from the same walk: see `readme.py` below. |
| `just sync`         | Download the whole upstream `dist` branch as one tarball and unpack it: the skill directories into `output_dir/skills`, the rest - the mirror's own index above all - into `output_dir/upstream`. Then rewrite the catalog. The fetch lands in a scratch directory and the swap happens only once it is whole; a guard refuses to replace a `skills/` that is not a snapshot. Pure data: it never touches a generated label. |
| `just refresh`      | `just sync`, plus the consequence: the catalog as it was before the sync is kept aside, and every label whose source content hash moved is deleted. A skill that vanished upstream keeps its label. |
| `just clean`        | Drop what was generated: `output_dir/profiles`, the catalog and the READMEs. The skill directories and the mirror's own files stay. |
| `just test`         | `uv run pytest`. |

| Variable     | Default                                | Meaning                                                                     |
| ------------ | -------------------------------------- | --------------------------------------------------------------------------- |
| `limit`      | `1`                                    | The next N skills still unlabelled, in the catalog's order; `0` = all. One is the default, so a bare `just` is a smoke run. It counts work rather than positions. |
| `jobs`       | one per core                           | Calls in flight at once (`xargs -P`).                                       |
| `rpm`        | –                                      | What the endpoint allows per minute; `0` = no pace. The pool is capped at it and each worker waits `pool * 60 / rpm` between calls. |
| `dry`        | –                                      | `1` = fake endpoint, real layout: nothing is called.                        |
| `output_dir` | `output`                               | The published root, where all four layers live.                             |
| `snapshot`   | the codeload url for the `dist` branch | What `just sync` fetches; a local `file://` tarball is how the tests run it. |
| `py`         | `uv run python`                        | How to run the script (override with an absolute interpreter path in CI).   |

The knobs are `just` variables - set on the command line and nowhere else: `SKILLS_PROFILES_LIMIT=20
just` does *not* work. `.env` belongs to the script and holds the endpoint and its key; the justfile
exports `output_dir`, `prompts_dir` and `dry`, and that export is the only handover between the two.

Because an output has no prerequisites anywhere, **its existence is the entire cache** - checked per
skill with a `[ -f ]`, so a batch that stopped halfway resumes at the first file that is not there
and never rebuilds one that is. That has three consequences:

- **Invalidation is deletion.** `just invalidate` (or `rm output/profiles/<id>/domain.json`) removes
  outputs; the next run regenerates them. Editing `_system.md` does *not* invalidate anything by
  itself - mtimes moving on every checkout would otherwise relabel the whole dataset for free.
- **The one thing that does invalidate is a new snapshot.** `just refresh` compares the index the
  download replaced with the one it brought and drops the labels of every skill whose content hash
  moved. A skill that vanished upstream is *not* dropped: its label was paid for.
- **There is no partial-failure bookkeeping.** A job that raises (quota, connection) exits non-zero,
  the pool reports it, and nothing was written - so the next run simply tries again.

## The script

One job, one call per `jev.py` process:

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
from `prompts/_system.md`, the only template: the skill's name, its description, its `SKILL.md` body
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

`index.py` joins the mirror's rows with the tree and writes `output/skills.jsonl`. It has no
arguments, no network and no call, and it is not in the build's path: `just index` is a verb you run
when you want the catalog, and `just sync` runs it because a sync moves the source layer under it.
The same run writes `output/README.md` and its Chinese twin - `readme.py` holds the words,
`index.py` hands it the numbers - the one thing the catalog cannot answer: **how much of the dataset
is labelled.** It reads the snapshot's own identity (`upstream/latest`, `upstream/stats.json`)
rather than stamping a wall clock, so a publish with nothing new spends no version number.

`stale.py` does the one comparison a shell is bad at: two catalogs in, the ids whose content hash
moved out - minus the ones the new one no longer holds, which are nobody's to delete. `just refresh`
is `sync` and it, in that order.

## How it works

```
                        output/  ── the whole artifact, published as one directory
                          │
mirror `dist` branch ─────┼──► skills/<id>/**      the skill itself, as published
     (`just sync`)        │                          downloads means one of these, install means copying
                          ├──► upstream/**         the rest of the mirror, its own index above all
                          │
                          └─► the justfile walks the catalog
                                      │
                        `just` labels what is missing, JOBS at a time
                                      │
                        profiles/<id>/domain.json
                                      │
                `just index` ──► skills.jsonl + READMEs: upstream × skills/ × profiles/
```

The runner is a command runner, not a build system: **existence is the skip**, the order is the
mirror's own (a `find` rather than a glob, because `.claude` is a repo name people use, and
`LC_ALL=C sort` because plain `sort` moves `_` around), and the pool is plain `xargs -P jobs` with
no jobserver. The rate limit is a pace, not a bucket: every worker waits `pool * 60 / rpm` between
calls, so a batch cannot outrun the endpoint; a 429 is still absorbed by the client's own backoff.

## Project layout

```
justfile                # the orchestrator: sync, the pool, the cache policy
jev.py                  # the one request: <skill> in, domain.json out; source reading and state too
index.py                # the catalog and its numbers: one flat jsonl, and the facts a README is
readme.py               # the page: those numbers said for a reader, in both languages
stale.py                # the comparison: two catalogs in, the changed skills' profiles out
prompts/_system.md      # the state template: name, description, body, and the repository block
tests/                  # offline unit tests plus a just end-to-end suite
.github/                # ci on every push and pull request, sync and publish by hand
```

## Configuration

Resolution order (highest first): `SKILLS_PROFILES_*` env vars → local `.env` → built-in defaults.
An empty value means "not set".

| Variable                        | Default          | Description                                                |
| ------------------------------- | ---------------- | ---------------------------------------------------------- |
| `SKILLS_PROFILES_API_KEY`       | –                | Its key; no key means no call                              |
| `SKILLS_PROFILES_BASE_URL`      | 302.AI's System One path | Where `jev.py` posts; nothing else does           |
| `SKILLS_PROFILES_MODEL`         | `jev-latest`     | The System One model, an alias over the pinned version     |
| `SKILLS_PROFILES_TIMEOUT`       | `20`             | Seconds per request: the endpoint answers in one to three, and drops a first call after idle |
| `SKILLS_PROFILES_MAX_RETRIES`   | `3`              | Extra attempts, for a dropped call or a busy gateway       |
| `SKILLS_PROFILES_DRY_RUN`       | `false`          | Use the fake endpoint: no API calls                        |
| `SKILLS_PROFILES_OUTPUT_DIR`    | `output`         | The published root: skills, profiles, upstream and catalog |
| `SKILLS_PROFILES_PROMPTS_DIR`   | `prompts`        | The directory holding `_system.md`                         |

## Testing

The suite is offline: `conftest.py` writes a fake snapshot tree, and constructing a real HTTP client
fails loudly, so a test can never call out even with a local `.env` full of keys.

- `tests/test_jev.py` covers the taxonomy as one object, the body a call posts (a state and typed
  questions, no messages), a dropped call retried where a rejected one is not, the guard on an
  answer outside the closed set, the source reading (front matter, YAML descriptions, the cut), the
  repository siblings and their caps, and the command - the gate, the exit codes, a request printed
  without a key.
- `tests/test_index.py` covers the catalog and its numbers; `tests/test_readme.py` the bilingual
  page; `tests/test_stale.py` the hash comparison; `tests/test_just.py` drives the justfile itself -
  the window, the pool, the cache, `sync`, `refresh`, `invalidate` - against a local tarball.

```bash
uv run pytest          # offline test suite
uv run ruff check .    # lint
uv run mypy            # types
just dry=1 limit=2     # the batch itself, end to end
```

## CI

Three workflows, and each one is thin: the work they do is `just`.

| workflow | trigger | does |
| --- | --- | --- |
| `ci.yml` | every push and pull request | `uv sync`, `ruff check .`, `mypy`, `pytest`, with `just` installed. Offline. |
| `sync.yml` | manual | `restore-dist` → `just refresh` → `publish-dist` (`date`). Replaces the dataset and retires what it invalidates; no model calls and no key. |
| `publish.yml` | manual | `restore-dist` → `just limit=… jobs=… rpm=…` → `just index` → `publish-dist` (`date-counter`). Needs the endpoint's own secret and variables; `replace` drops every label first. |

Docs rule: every English document has a Chinese counterpart — keep both in sync, in the same pass.
