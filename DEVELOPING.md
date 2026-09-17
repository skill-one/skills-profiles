# Developing skills-profiles

The generator behind the dataset described in [README.md](README.md): it reads each skill's
`SKILL.md` from [skills-sh-mirror](https://github.com/skill-one/skills-sh-mirror) and asks an
OpenAI-compatible LLM for six structured Chinese angles per skill.

中文: [DEVELOPING.zh-CN.md](DEVELOPING.zh-CN.md)

## Quickstart

Needs Python 3.12+, [uv](https://docs.astral.sh/uv/) and [`just`](https://just.systems); LLM
credentials go in a local `.env` (copy [`.env.example`](.env.example)).

```bash
uv sync
just sync             # download the upstream snapshot into output/cache/skills-sh
just                  # build the first skill, end to end
just limit=0          # ... or every profile still missing, whole snapshot, no cap
```

Offline, no API calls and no credentials: `just dry=1 limit=5`.

## The batch is `just`

| Command                     | What it does                                                                                                                                                                                     |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `just`                      | Build the missing profiles for the first `limit` skills, most installed first. The window is ordered by the snapshot's own index (`DATA_DIR/skills.jsonl`, installs-descending) and filtered to the ids that have a `SKILL.md` on disk; with no index it is the directory listing in path order. Beside it the recipe enumerates `PROMPTS_DIR/*.json`, keeps the `(skill, prompt)` pairs whose json is missing, and feeds them to an `xargs -P` pool. `jobs` is the whole concurrency story. |
| `just one <prompt> <skill>` | Build exactly one output, whether or not the batch has reached it. `limit` is a window over the snapshot in its own order, not a way to name a skill, so this is the only way to address one cell - and the only way to rebuild one without the batch skipping it. |
| `just invalidate <prompt>`  | Delete one prompt's outputs, so the next run rebuilds exactly those.                                                                                                                               |
| `just index`                | Fold the built `domain` into `<output_dir>/skills.jsonl`: one flat line per skill (`id`, `domain`, `reason`), in path order, with no line at all while a skill's domain is missing. It reads the output tree alone - no snapshot, no calls - and rewrites the file whole, so it is a projection of the tree rather than a second copy to keep in step by hand. |
| `just sync`                 | Download the whole upstream `dist` branch as one tarball and unpack it into `data_dir`, replacing the previous snapshot wholesale. The new tree is unpacked beside the old one, so a failed download changes nothing; a guard refuses to replace a directory that is not a snapshot. Every run downloads - nothing tracks "already current". Pure data: it never touches a generated profile. |
| `just refresh`              | `just sync`, plus the consequence: the index of the snapshot being replaced is kept aside, and every profile whose source content hash moved with the new one is deleted, so the next batch rebuilds it. A skill that vanished upstream keeps its profiles. The scratch index is gone when the comparison is done. |
| `just clean`                | Drop the profiles - `output_dir/skills` and the index beside it. The snapshot in the same root is left alone: re-fetching it is the expensive part.                                                |
| `just test`                 | `uv run pytest`.                                                                                                                                                                                   |

Every command above is a recipe name, and `just --list` prints them with a line about each.

| Variable     | Default                                | Meaning                                                                                                      |
| ------------ | -------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `limit`      | `1`                                    | Serve the first N skills of the snapshot's order: `skills.jsonl` is installs-descending, so a bounded run does the most installed skills first. `0` = the whole snapshot, with no cap. One is the default, so a bare `just` is a one-skill smoke run. The window bounds a run; the order only decides which skills a bounded one reaches. |
| `prompt`     | –                                      | One prompt id, or empty for every prompt: the column rather than the cell. An id that is not there fails before anything is dispatched, naming the ones that are. |
| `jobs`       | one per core                           | Generations in flight at once (`xargs -P`). This is the burst, not the pace.                                  |
| `rpm`        | –                                      | What the endpoint allows per minute; `0` = no pace. The pool is capped at it and each worker waits `pool * 60 / rpm` between calls, so a batch cannot outrun it. `just rpm=20` for Agnes's free tier. |
| `dry`        | –                                      | `1` = fake LLM, real layout: nothing is called, and the real layout is written.                               |
| `data_dir`   | `<output_dir>/cache/skills-sh`         | Where the snapshot lives. Inside the output root and following it, so the sources publish with the profiles; pass it on the command line to read a snapshot from somewhere else. |
| `output_dir` | `output`                               | Where the profiles go, same rule. `just clean` and `just invalidate` need it, hence the variable.             |
| `snapshot`   | the codeload url for the `dist` branch | What `just sync` fetches; pointing it at a local `file://` tarball is how the tests run it offline.           |
| `py`         | `uv run python`                        | How to run the script (override with an absolute interpreter path in CI).                                      |

The knobs are `just` variables, which is to say they are set on the command line and nowhere else:
`SKILLS_PROFILES_LIMIT=20 just` does *not* work, and that is deliberate - a batch changes only
because a run said so. `.env` belongs to gen.py and holds the endpoint and its key; the justfile
exports the four values gen.py reads (`data_dir`, `output_dir`, `prompts_dir`, `dry`) into its
environment, and that export is the only handover between the two.

Because an output has no prerequisites anywhere, **its existence is the entire cache** - checked per
`(skill, prompt)` with a `[ -f ]`, so a batch that stopped halfway resumes at the first file that is
not there and never rebuilds one that is. That has three
consequences worth stating plainly:

- **Invalidation is deletion.** `just invalidate scenario` (or `rm output/skills/<id>/scenario.json`)
  removes outputs; the next run regenerates exactly those. Editing a prompt template does *not*
  invalidate anything by itself - that is deliberate, since it would otherwise rewrite every profile
  on every cheap edit (`git checkout` alone would do it, as mtimes move).
- **The one thing that does invalidate is a new snapshot.** `just refresh` compares the index the
  download replaced with the one it brought and drops the profiles of every skill whose content hash
  moved: those were built from text that is no longer there. It stays a separate verb because
  `just sync` is a data operation - a run that only moves data should not also delete work. A skill
  that vanished upstream is *not* dropped: its profiles were paid for, and nothing is left to
  rebuild them from.
- **There is no partial-failure bookkeeping.** A job that raises (quota, connection) exits non-zero,
  the pool reports it, and nothing was written — so the next run simply tries again.

## The script

One job, one LLM call per `gen.py` process:

```bash
uv run python gen.py <prompt> <skill>           # build exactly one output
uv run python gen.py <prompt> <skill> --print   # print the request and stop, calling nothing
```

`gen.py` is not given a "skip if it exists" check on purpose: deciding what to build is the
justfile's job, and one process should do exactly what it was asked. `--print` is the one
question that is not a build, and it answers it without calling or writing anything - which is
what `just render` is for. Both the request and the answer travel as data (stdout) while
progress stays on stderr, where a batch of sixty thousand of them can be left.

Its whole contract with the caller is then this:

- **`<prompt>`** names `prompts/<prompt>.md` and the `<prompt>.json` schema beside it.
- **`<skill>`** is a skill's directory under `<data_dir>/skills`: its id with `:` and `&` spelled
  `_`, which is what upstream writes. The justfile spells the same path to decide what is
  missing, and a test builds through it, so the two spellings cannot drift.
- **The output** lands at `<output_dir>/skills/<skill>/<prompt>.json`, with the markdown written
  first and the json renamed into place - so a crash can leave neither a json without its readable
  copy, nor a half-written one that the next batch would skip as done.
- **The source is cut at 20 000 characters**, so one enormous `SKILL.md` cannot blow up a call.
- **Status** is 0 built, 1 an input or the model was unusable, 2 bad arguments. A failure is one
  line rather than a traceback, because a batch of sixty thousand of them is where a traceback
  stops being information.

Naming what to build lives in the justfile rather than in a script for the same reason: the graph is
a directory listing and a glob, and a script that printed it would be a second place for the layout
to be wrong. Fetching needs no script at all: `just sync` is a `curl` and a `tar`, and the only thing
it has to get right is the data dir layout the rest reads.

`index.py` is the other script, and it is one thing a shell loop would need `jq` bolted on for:
read `<output_dir>/skills` and write `output/skills.jsonl`. It has no arguments, no snapshot and no
call - only the ids it walks, the one angle it reads and the file it renames into place. It is not
in the build's path: `just index` is a verb you run when you want the listing, which is also why an
index cannot drift from a tree it was not written alongside.

`stale.py` is the third, for the one comparison a shell is bad at: two jsonl indexes in, the ids
whose content hash moved out - minus the ones the new index no longer holds, which are nobody's to
delete. Its only argument is the replaced index; it prints what it retired and deletes those
skills' directories. `just refresh` is `sync` and it, in that order.

## How it works

```
                                    output/  ── the whole artifact, published as one directory
                                      │
mirror dist branch tarball ──► cache/skills-sh (skills/<id>/SKILL.md + the files beside them)
        (`just sync`)                        │
                                             └─► the justfile walks it ◄── prompts/*.json
                                                            │
                                        `just` builds what is missing, JOBS at a time
                                                            │
                              output/skills/<id>/<angle>.json + md/<angle>.md
                                                            │
                                          `just index` ──► output/skills.jsonl (derived)
```

`output/` is one root holding three things: the profiles, the index beside them, and the snapshot
they were built from. The snapshot used to live beside it in `cache/`; keeping it inside means the
published directory is self-contained - the sources are archived with what was made from them - and
the publish step copies one directory instead of two. The whole root is gitignored: CI publishes it
to the `dist` branch, so the repository does not carry it.

Design decisions:

- **One prompt, one file, one turn.** Every prompt is a self-contained task: `SKILL.md` goes in
  the system message, the prompt template in the user message, and the structured answer becomes
  one json. No prompt reads another prompt's output, so there is no DAG to order, no dependency
  closure to compute and nothing to cascade when one of them changes. Adding an angle costs one
  markdown file and no code.
- **The runner is a command runner.** `just` is not a build system, and it does not pretend to be:
  the two things make did for free are one shell line each here. **Existence is the skip** - the
  recipe filters out the pairs whose json is there before anything is dispatched. **The order is the
  snapshot's own** - `skills.jsonl` is written installs-descending, so reading it is the whole sort
  and the most installed skills come first; an id it names with no `SKILL.md` on disk is skipped,
  and no index at all falls back to the tree, walked as a `find` rather than a glob (a glob does not
  match a leading dot, and `.claude` is a repo name people use) and ordered with `LC_ALL=C sort`
  (plain `sort` moves `_` around, so the window would differ between machines). **The pool is the
  concurrency** - `xargs -P jobs`, a plain number, with no jobserver to negotiate. A hand-written `graphlib` DAG, a semaphore, a rate limiter, a
  resume cache, a coverage report and an index projection all existed to answer questions the
  directory listing, `[ -f ]` and `xargs` answer; all of them are gone, and the batch is verified
  end to end through `just` instead.
- **The rate limit is a pace, not a bucket.** `jobs` bounds what is in flight, which is not the
  same thing as how fast a batch goes: ten workers calling an endpoint that answers in a second is
  ten calls a second, whatever the core count. `rpm` states what the endpoint allows, and every
  worker then waits `pool * 60 / rpm` between its calls - so a worker's cycle is at least that
  long, and a batch cannot outrun `rpm` however fast the answers come back. The pool is capped at
  `rpm` too, so the first round's burst fits inside the allowance as well. Nothing is shared and
  nothing is coordinated between the sixty thousand processes; each one just knows the number. A
  429 is still absorbed where it belongs, by the client's own backoff, with `max_retries` as the
  net for an endpoint whose real limit turns out to be lower than its documentation.
- **The output contract lives next to the task.** `prompts/<id>.json` is the JSON Schema for that
  prompt's answer, and it travels to the provider verbatim as its `json_schema` response format
  (with `strict`), so the model is decoded *into* the shape instead of being asked politely and
  validated afterwards. There is no local validator, no retry loop, and no second copy of an
  output's shape anywhere in the code — which is also why the only LLM dependency left is the
  provider SDK itself.
- **A prompt is a pair of files.** `prompts/<id>.md` is the task, the `prompts/<id>.json` beside it
  is its contract, and `_system.md` holds the shared system prompt — the only way `SKILL.md` reaches
  a prompt. Neither half can be orphaned: they are read together, a test checks the pairing, and the
  recipe enumerates the schemas so a prompt without one is never a target.
- **One script per job.** `gen.py` knows nothing about the snapshot (it is handed a skill id) and
  nothing about the build graph; `index.py` knows nothing about either and only reads the output
  tree; the justfile only names files. That is what keeps the request itself small enough to read in
  one sitting.
- **One snapshot, one request.** `just sync` is a `curl` and a `tar` of the whole branch: no
  selective unpacking, no tag bookkeeping, nothing to go stale. That costs disk and download time
  (the branch carries avatars and other files a batch never reads - 82,687 files against the
  9,766 it does), and it is a deliberate trade: `sync` has no decisions left to get wrong. It
  always replaces the previous snapshot rather than merging, so a skill that vanished upstream
  cannot leave its files behind.
- **Nothing else.** The earlier shape of this project carried three things that are deliberately
  gone: `stats.json` (the directory listing is the index — nothing can drift from it), the rendered
  covers (one fewer endpoint, key, quota and binary asset to manage), and the `dist` publishing
  workflows (there is nothing to publish but a directory tree). `just index` does write a
  `skills.jsonl` again, but nothing else came back with it: it is one flat line per skill over its
  `domain`, derived from the tree by a command that says so, and nothing reads it. An index that is
  written by the run that produces a tree would be the drift this one avoids.

## Adding a prompt

Two files, and no code change at all.

`prompts/my_angle.md` is the task. The only variable a template can use is `{{ skill_md }}`, and it
is available in `_system.md` alone - that is the message the source is sent in. A task template
that asks for it fails when it is loaded, rather than arriving as an empty string. Templates are
jinja2, parsed and rendered eagerly at load time, so a syntax error or a stray variable names the
file instead of failing mid-batch:

```markdown
请为下面的 skill 写……
```

`prompts/my_angle.json` is the JSON Schema its answer is decoded into:

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["text"],
  "properties": {
    "text": {"type": "string", "description": "介绍词正文, 100 个字以内"}
  }
}
```

Then fill the angle in for every skill:

```bash
just prompt=my_angle
```

Already-generated angles are skipped, so only the new one costs calls anyway - `prompt=<id>` just
says so outright, instead of walking the other six to find nothing to do.

Three things about the schema are worth knowing. Keeping it a real `.json` file is the point: an
editor or another tool can validate it, and the markdown stays prose. `strict` mode is the
provider's rule, not ours, so a schema it refuses — an unclosed object, a field missing from
`required` — fails the call with a 400 rather than being quietly coerced; `tests/test_gen.py`
checks every prompt schema against those rules, so `uv run pytest` catches it before a batch does.
And `domain` states its 13 categories twice, as prose in the markdown for the model and as the
schema's `enum` for the decoder; keep them in sync (a test checks that too, from the enum side).

## Project layout

```
justfile                # the orchestrator: sync, the build graph, the pool, the cache policy
gen.py                  # the request: <prompt> <skill> in, one json + markdown out
index.py                # the projection: the output tree in, one flat jsonl out
stale.py                # the comparison: two snapshot indexes in, the changed skills' profiles out
prompts/                # one <id>.md (task) + <id>.json (schema) per prompt, plus _system.md
tests/                  # offline unit tests plus a just end-to-end suite
.github/                # ci on every push and pull request, sync and publish by hand
```

## Configuration

Resolution order (highest first): `SKILLS_PROFILES_*` env vars → local `.env` → built-in
defaults. An empty value means "not set", so an unconfigured secret exported as `""` cannot
replace a default. `just` loads `.env` itself, so the justfile's own variables - the paths, `py` -
resolve from the same three places.

| Variable                        | Default          | Description                                                          |
| ------------------------------- | ---------------- | -------------------------------------------------------------------- |
| `SKILLS_PROFILES_MODEL`         | `gpt-4.1-mini`   | Any OpenAI-compatible chat model                                     |
| `SKILLS_PROFILES_BASE_URL`      | –                | OpenAI-compatible endpoint                                           |
| `SKILLS_PROFILES_API_KEY`       | –                | API key for the endpoint                                             |
| `SKILLS_PROFILES_MAX_RETRIES`   | `3`              | Extra attempts per LLM call (`0` = a single try)                     |
| `SKILLS_PROFILES_THINKING`      | `false`          | Let the model reason first: the provider's `enable_thinking`, only ever sent as `true`, which is all the documentation states |
| `SKILLS_PROFILES_DRY_RUN`       | `false`          | Use the fake LLM: no API calls                                       |
| `SKILLS_PROFILES_OUTPUT_DIR`    | `output`         | The published directory: profiles, index and snapshot                |
| `SKILLS_PROFILES_DATA_DIR`      | `output/cache/skills-sh` | The unpacked upstream snapshot, inside the output root       |
| `SKILLS_PROFILES_PROMPTS_DIR`   | `prompts`        | Prompt markdown directory (plus `_system.md`)                        |

## Testing

The suite is offline: `conftest.py` writes a fake snapshot tree, and constructing a real LLM client
fails loudly, so a test can never call out even with a local `.env` full of keys.

- `tests/test_gen.py` covers the request: prompt loading and its failure modes, the strict-mode
  rules every schema has to satisfy, the taxonomy/enum agreement, template rendering, the keywords
  a call is sent with, the dry-run placeholder, the two output files, and the command.
- `tests/test_index.py` covers the index: the graph being the output tree in path order (including a
  repo whose name starts with a dot), a flat row per built domain, a skill whose json is not there
  being no row at all, the id's spelling, and the write being whole or absent.
- `tests/test_stale.py` covers the comparison: a moved hash retiring exactly that skill, a skill
  that vanished keeping its profiles, a line with no hash saved being nobody's business, a skill
  whose hash moved before anything was built retiring nothing, and the two cold starts (no previous
  index, no snapshot index).
- `tests/test_just.py` covers the justfile, which owns both the networked and the parallel work:
  a fresh build, the second run doing nothing, deleting one json rebuilding exactly that one, the
  `limit` window and its order (the snapshot's index, path order without one), `jobs` sizing the
  pool, `just one` reaching outside the window,   `just invalidate`
  forgetting exactly one prompt, `just index` folding the tree into one file, `just refresh`
  retiring exactly what a new snapshot changed, `DRY=1` in both of its
  spellings, an inherited `SKILLS_PROFILES_DRY_RUN` reaching the jobs unclobbered, `just sync`
  fetching a snapshot from a local tarball and replacing it wholesale, the guard that keeps `rm -rf`
  away from a directory that is not a snapshot, a snapshot fetched by `just` being what the batch
  then reads, `just clean`, and the missing-snapshot error naming the fix.

```bash
uv run pytest          # offline test suite
uv run ruff check .    # lint
uv run mypy            # types
just dry=1 limit=2     # the batch itself, end to end
```

## CI

Three workflows, and each one is thin: the work they do is `just`, so what can be verified locally
is verified locally - `tests/test_just.py` drives the same recipes they do.

| workflow | trigger | does |
| --- | --- | --- |
| `ci.yml` | every push and pull request | `uv sync`, `ruff check .`, `mypy`, `pytest`, with `just` installed so the suite that drives it cannot skip. Offline: no credentials, no snapshot. |
| `sync.yml` | manual | `restore-dist` → `just refresh` → `just index` → `publish-dist` (`date`). Replaces the dataset and retires what it invalidates; no model calls and no key. |
| `publish.yml` | manual | `restore-dist` → `just limit=… jobs=… rpm=… prompt=…` → `just index` → `publish-dist` (`date-counter`). Builds against the dataset `sync` published, never against upstream. |

Both data workflows restore first and publish last, so a run is a fresh runner plus two tarballs. Two
composite actions own the two ends:

- `.github/actions/restore-dist` puts the published root back into `output/`, minus the `latest`
  pointer: a publish writes that, a run never reads it.
- `.github/actions/publish-dist` turns `output/` into the `dist` branch: one commit, history pruned
  to a time window, a `dist-YYYY-MM-DD` or `dist-<base>-N` tag, and a `latest` pointer naming it. A
  tree that has not changed publishes nothing and spends no tag, because the comparison with the
  branch happens before a tag is chosen.

Nothing stamps provenance any more: the snapshot is published inside the same tree, so what a profile
was built from is the `cache/skills-sh` beside it - which is also why publishing is one directory
instead of two.

Docs rule: every English document has a Chinese counterpart (`README.md` / `README.zh-CN.md`,
`DEVELOPING.md` / `DEVELOPING.zh-CN.md`) — keep both in sync, in the same pass.
