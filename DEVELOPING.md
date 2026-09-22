# Developing skills-profiles

The generator behind the dataset described in [README.md](README.md): it reads each skill's
`SKILL.md` from [skills-sh-mirror](https://github.com/skill-one/skills-sh-mirror) and asks for six
structured angles per skill - five of them Chinese, from an OpenAI-compatible chat model, and the
`domain` label from the System One endpoint, which answers typed questions instead.

中文: [DEVELOPING.zh-CN.md](DEVELOPING.zh-CN.md)

## Quickstart

Needs Python 3.12+, [uv](https://docs.astral.sh/uv/) and [`just`](https://just.systems); LLM
credentials go in a local `.env` (copy [`.env.example`](.env.example)).

```bash
uv sync
just sync             # fetch the mirror into output/skills and output/upstream
just                  # build the first skill, end to end
just limit=0          # ... or every profile still missing, whole snapshot, no cap
```

Offline, no API calls and no credentials: `just dry=1 limit=5`.

## The batch is `just`

| Command                     | What it does                                                                                                                                                                                     |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `just`                      | Build the missing profiles for the next `limit` skills that still need one, most installed first. The order is the catalog's own (`OUTPUT_DIR/skills.jsonl`, which the mirror wrote installs-descending) filtered to the rows that have a description and a `SKILL.md` on disk; with no catalog it is the directory listing in path order. The window is then the first `limit` of those skills that are missing at least one angle - a count of work, not of positions, so repeated runs walk down the dataset. The recipe takes the angles from both producers - `PROMPTS_DIR/*.json` and `jev.py --angles` - keeps the pairs whose json is missing, and feeds them to an `xargs -P` pool that hands each pair to the script that owns its angle. `jobs` is the whole concurrency story. |
| `just one <prompt> <skill>` | Build exactly one output, whether or not the batch has reached it. `limit` is a window over the dataset in its own order, not a way to name a skill, so this is the only way to address one cell - and the only way to rebuild one without the batch skipping it. |
| `just invalidate <prompt>`  | Delete one prompt's profiles, so the next run rebuilds exactly those.                                                                                                                               |
| `just index`                | Write `<output_dir>/skills.jsonl` - the catalog: one flat line per skill the mirror lists, in the mirror's order, being the mirror's own row (`id`, `installs`, `url`, `hash`, `fetchedAt`) joined with the `description` read out of that skill's `SKILL.md`, and the `domain` and `confidence` in `profiles/<id>/domain.json`. Both are `null` while they are unknown, and a skill the mirror has dropped while profiles remain gets a row of its own. It reads the tree alone - no network, no calls - and rewrites the file whole, so it is a projection of what is on disk rather than a second copy to keep in step by hand. It writes the READMEs beside it, from the same walk: see `index.py` below. |
| `just sync`                 | Download the whole upstream `dist` branch as one tarball and unpack it into the tree: the skill directories into `output_dir/skills`, complete and unchanged, and the rest - the mirror's own index above all - into `output_dir/upstream`. Then rewrite the catalog, which the moved source layer just invalidated. The fetch lands in a scratch directory beside the output root and the swap happens only once it is whole, so a failed download changes nothing; a guard refuses to replace a `skills/` that is not a snapshot. Every run downloads - nothing tracks "already current". Pure data: it never touches a generated profile. |
| `just refresh`              | `just sync`, plus the consequence: the catalog as it was before the sync is kept aside, and every profile whose source content hash moved with the new one is deleted, so the next batch rebuilds them. A skill that vanished upstream keeps its profiles. The scratch catalog is gone when the comparison is done. |
| `just clean`                | Drop what was generated: `output_dir/profiles`, the catalog and the READMEs about it (`output_dir/skills.jsonl`, `output_dir/README.md`, `output_dir/README.zh-CN.md`). The skill directories and the mirror's own files stay: they are what a profile is built from, and re-fetching them is the expensive part. |
| `just test`                 | `uv run pytest`.                                                                                                                                                                                   |

Every command above is a recipe name, and `just --list` prints them with a line about each.

| Variable     | Default                                | Meaning                                                                                                      |
| ------------ | -------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `limit`      | `1`                                    | Serve the next N skills that still need something, in the catalog's order: `skills.jsonl` carries the mirror's rows in the mirror's order, installs-descending, so a bounded run does the most installed skills first. `0` = the whole dataset, with no cap. One is the default, so a bare `just` is a one-skill smoke run. It counts work rather than positions - a skill that is done is not in the window - which is what makes repeated runs walk down the dataset, and what keeps a bounded `publish` run from being a no-op after its first one. What is already built is kept either way: the window decides what a run reaches, not what the tree holds. |
| `prompt`     | –                                      | One prompt id, or empty for every prompt: the column rather than the cell. An id that is not there fails before anything is dispatched, naming the ones that are. |
| `jobs`       | one per core                           | Generations in flight at once (`xargs -P`). This is the burst, not the pace.                                  |
| `rpm`        | –                                      | What the endpoint allows per minute; `0` = no pace. The pool is capped at it and each worker waits `pool * 60 / rpm` between calls, so a batch cannot outrun it. `just rpm=20` for Agnes's free tier. |
| `dry`        | –                                      | `1` = fake LLM, real layout: nothing is called, and the real layout is written.                               |
| `output_dir` | `output`                               | The published root, where all four layers live. `just sync`, `just clean` and `just invalidate` need it, hence the variable. |
| `snapshot`   | the codeload url for the `dist` branch | What `just sync` fetches; pointing it at a local `file://` tarball is how the tests run it offline.           |
| `py`         | `uv run python`                        | How to run the script (override with an absolute interpreter path in CI).                                      |

The knobs are `just` variables, which is to say they are set on the command line and nowhere else:
`SKILLS_PROFILES_LIMIT=20 just` does *not* work, and that is deliberate - a batch changes only
because a run said so. `.env` belongs to the scripts and holds the endpoints and their keys; the
justfile exports the three values the batch reads (`output_dir`, `prompts_dir`, `dry`) into its
environment, and that export is the only handover between the two.

Because an output has no prerequisites anywhere, **its existence is the entire cache** - checked per
`(skill, prompt)` with a `[ -f ]`, so a batch that stopped halfway resumes at the first file that is
not there and never rebuilds one that is. That has three
consequences worth stating plainly:

- **Invalidation is deletion.** `just invalidate scenario` (or `rm output/profiles/<id>/scenario.json`)
  removes outputs; the next run regenerates exactly those. Editing a prompt template does *not*
  invalidate anything by itself - that is deliberate, since it would otherwise rewrite every profile
  on every cheap edit (`git checkout` alone would do it, as mtimes move).
- **The one thing that does invalidate is a new snapshot.** `just refresh` compares the index the
  download replaced with the one it brought and drops the profiles of every
  skill whose content hash moved: those were built from text that is no longer there.
  It stays a separate verb because
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
- **`<skill>`** is a skill's directory under `<output_dir>/skills`: its id with `:` and `&` spelled
  `_`, which is how the mirror's own tree is named. The justfile spells the same path to decide what
  is missing, and a test builds through it, so the two spellings cannot drift.
- **The output** lands at `<output_dir>/profiles/<skill>/<prompt>.json`, with the markdown written
  first and the json renamed into place - so a crash can leave neither a json without its readable
  copy, nor a half-written one that the next batch would skip as done.
- **The source is cut at 20 000 characters**, so one enormous `SKILL.md` cannot blow up a call.
- **The description is the front matter's `description`**, parsed as YAML, and it is the gate on a
  skill rather than one of its fields: a header that is missing, that does not parse, or that carries
  no description drops the skill - no call, no file, one line on stderr, status 1. The mirror's index
  used to carry a copy of that line and no longer does; the catalog writes it out of the same bytes,
  as `null` for a skill nothing can be read from, which is also what keeps the row out of the window.
- **Status** is 0 built, 1 an input or the model was unusable, 2 bad arguments. A failure is one
  line rather than a traceback, because a batch of sixty thousand of them is where a traceback
  stops being information.

`jev.py` is the third writer of a profile and the second producer, and it exists because its
endpoint is not a chat one: `POST /v1/systemone` takes a `state` and a map of typed `questions`, and
answers with typed `answers` - no messages, no `json_schema`, no free text. So it builds its own
request and shares everything else with `gen.py`: the same rendered system message as the `state`,
plus the one layer no chat angle is handed - the skill's repository, as its siblings' one-line
descriptions, each cut to a hint and the count capped - because `domain` is a property of a
repository rather than of one file, and the siblings decide what a lone, ambiguous skill leaves
open: the same writer,
the same `profiles/<id>/<angle>.json` and markdown copy, the same gate on a skill with no
description, the same exit codes. `just` sends a pair to whichever of the two owns the angle,
and `jev.py --angles` is the only list of its own there is - adding one to that dict is adding an
angle the batch builds. What it trades away is real: a System One answer is a member of a closed set,
so `domain` has no reason line and no array. What it gives instead is the answer itself, kept whole
in the profile: the label, the confidence, and the distribution over all 13 categories it was read
off - which is what another angle's file is too, its model's answer rather than a summary of it. The
distribution is worth keeping because the winner does not contain it: a call decided 0.52 to 0.48
says something a call decided 0.99 to 0.01 does not, and neither can be asked for again. The catalog
takes two of the three, the label and the confidence, and leaves the rest where it lives.

Naming what to build lives in the justfile rather than in a script for the same reason: the graph is
a directory listing and a glob, and a script that printed it would be a second place for the layout
to be wrong. Fetching needs no script of its own: `just sync` is a `curl`, a `tar` and one rewrite of
the catalog, and the only things it has to get right are the two directories everything else reads.

`index.py` is the other script, and it is one thing a shell loop would need `jq` bolted on for: join
the mirror's rows with the tree and write `output/skills.jsonl`. It has no arguments, no network and
no call - only the rows it reads, the descriptions it parses out of the skills themselves, the
domains the tree holds and the file it renames into place. It is not in the build's path either:
`just index` is a verb you run when you want the catalog, and `just sync` runs it because a sync
moves the source layer under it. Nothing else writes the file, so it cannot drift from a tree it was
not written alongside.

The same run writes `output/README.md` and its Chinese twin from the same walk - `readme.py` holds
the words, `index.py` hands it the numbers - and together they are the one thing the catalog cannot
answer: **how much of the dataset is built.** Two lines say which files are the skill and which are
what was written about it, then the table counts cells the way the batch does - an angle's json is the
unit of work, so a directory left behind by `just invalidate` is not progress - over the skills that
can actually be built, since a skill whose front matter yields no description would pin the number
below 100% forever. Each angle is a row: how many skills have it, and what share of the mirror's
installs that covers, which is the number that matters because the batch works most-installed-first (a
count of 0.3% and a weight of 16% are the same tree, and only the second says what a partial dataset
is worth). Under it, two lines: the snapshot the numbers describe, and the denominator. **That is the
whole page, and the length is the point** - it is the front door of a published directory, and the
project's own prose lives in this repository; a longer page would be a second copy of it to keep in
step, so a test pins it at 25 lines. Three decisions are worth knowing. **It is a README, because the
published root is the product**: `publish-dist` copies `output/` to the `dist` branch root, so
`README.md` is what GitHub renders for anyone who lands there - which is also why there are two of
them, the repository's own rule for a document. **The words are separated from the numbers** so that a
second language is a second page rather than a second code path: one renderer, two tables of text, and
a test that both hold the same keys. **They read the snapshot's own identity** (`upstream/latest`,
`upstream/stats.json`) rather than stamping a wall clock, because a publish compares the tree with the
branch and a file that changes on every run would spend a version number on a tree that did not
change.

`stale.py` is the third, for the one comparison a shell is bad at: two catalogs in, the ids whose
content hash moved out - minus the ones the new one no longer holds, which are nobody's to delete.
Its only argument is the catalog that was replaced; it prints what it retired and deletes those
skills' `profiles/<id>` directories. `just refresh` is `sync` and it, in that order.

## How it works

```
                        output/  ── the whole artifact, published as one directory
                          │
mirror `dist` branch ─────┼──► skills/<id>/**      the skill itself, as published: what a user
     (`just sync`)        │                          downloads means one of these, install means copying
                          ├──► upstream/**         the rest of the mirror, its own index above all
                          │
                          └─► the justfile walks the catalog ◄── prompts/*.json
                                      │
                        `just` builds what is missing, JOBS at a time
                                      │
                        profiles/<id>/<angle>.json + md/<angle>.md
                                      │
                `just index` ──► skills.jsonl + READMEs: upstream × skills/ × profiles/
```

`output/` is one root holding four things, each named after what it is: the skills, the profiles
written about them, the mirror's own files, and the catalog joining the two. The mirror used to sit
in a `cache/` inside the root, with the profiles in a `skills/` that was not the skills; naming the
layers after their contents is what lets a consumer install a skill by copying `skills/<id>/` and
read everything else about it out of one line of `skills.jsonl`. The whole root is gitignored: CI
publishes it to the `dist` branch, so the repository does not carry it.

Design decisions:

- **One prompt, one file, one turn.** Every prompt is a self-contained task: `SKILL.md` goes in
  the system message, the prompt template in the user message, and the structured answer becomes
  one json. No prompt reads another prompt's output, so there is no DAG to order, no dependency
  closure to compute and nothing to cascade when one of them changes. Adding an angle costs one
  markdown file and no code.
- **The runner is a command runner.** `just` is not a build system, and it does not pretend to be:
  the two things make did for free are one shell line each here. **Existence is the skip** - the
  recipe filters out the pairs whose json is there before anything is dispatched, and the window is
  counted over what is left: `limit` is the next N skills missing at least one angle rather than the
  first N of the listing, since a skill at the top of the listing is finished after one run and a
  position-based window would make every run after it a no-op. It reads that off the tree in one awk
  over the files that are there, because sixty thousand `[ -f ]` calls in a shell loop is a minute of
  forking. **The order is the
  mirror's own** - the catalog carries its rows in its order, installs-descending, so reading it is
  the whole sort and the most installed skills come first; a row with no description, or with no
  `SKILL.md` on disk, is skipped, and no catalog at all falls back to the tree, walked as a `find`
  rather than a glob (a glob does not match a leading dot, and `.claude` is a repo name people use)
  and ordered with `LC_ALL=C sort` (plain `sort` moves `_` around, so the window would differ between
  machines). **The pool is the
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
  is its contract, and `_system.md` holds the shared system prompt — the only way a skill's name,
  its description and its body reach a prompt. Neither half can be orphaned: they are read
  together, a test checks the pairing, and the recipe enumerates the schemas so a prompt without one
  is never a target.
- **One script per job.** `gen.py` knows nothing about the snapshot (it is handed a skill id) and
  nothing about the build graph; `index.py` knows nothing about either and only reads the output
  tree; `readme.py` is its other half, the same numbers said for a reader, and knows nothing about
  where they came from; the justfile only names files. That is what
  keeps the request itself small enough to read in one sitting.
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
  `domain`, derived from the tree by a command that says so. An index that is written by the run that
  produces a tree would be the drift this one avoids. The READMEs are not that file under another
  name: nothing reads them back, no consumer may rely on their numbers, and they hold no state that
  is not already in the tree — remove them and the next `just index` writes them back, byte for byte.

## Adding a prompt

Two files, and no code change at all.

`prompts/my_angle.md` is the task. The variables a template can use are `{{ name }}` - the id the
tree calls the skill by - `{{ description }}`, the `description` of the skill's own front matter, read
as YAML so that a folded block or a quoted string arrives as text, `{{ skill_body }}`, its
`SKILL.md` with that front matter dropped, and a fourth, `{{ repo }}`, the skill's repository as
context: its id and the one-line descriptions of the siblings beside it. All are available in
`_system.md` alone: that is the message the skill is sent in, and it is the whole of what the model
is told before the task. `repo` is `None` for every chat angle and the template says nothing when it
is, `jev.py` being the only caller that passes one - so `domain` is the only angle handed the
repository. The body
carries no header because the header is those first two parts said again: the name and the description
are read out of it. The block goes whole for the body, the fields beside them being YAML; what is left
behind is `license`, `allowed-tools`, a version - how a skill is installed rather than what it is for.
A task template that asks for one of the three fails when it is loaded, rather than arriving as an
empty string.
Templates are jinja2, parsed and rendered eagerly at load time, so a syntax error or a stray variable
names the file instead of failing mid-batch:

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
says so outright, instead of walking the other five to find nothing to do.

Two things about the schema are worth knowing. Keeping it a real `.json` file is the point: an
editor or another tool can validate it, and the markdown stays prose. `strict` mode is the
provider's rule, not ours, so a schema it refuses — an unclosed object, a field missing from
`required` — fails the call with a 400 rather than being quietly coerced; `tests/test_gen.py`
checks every prompt schema against those rules, so `uv run pytest` catches it before a batch does.

A Jev angle is the other kind, and it is one entry in `jev.py` rather than two files: a name in
`QUESTIONS` holding the typed questions the endpoint answers, each a `choice` with its options, a
`score` with its levels, or a `noul` with nothing but an instruction. There is no prompt template and
no schema, so there is nothing to keep in step - `domain`'s 13 categories are one dict, handed over
as the options its answer is confined to. An entry there is built by `just` on the next run, just as
a new prompt pair is.

## Project layout

```
justfile                # the orchestrator: sync, the two producers, the pool, the cache policy
gen.py                  # the chat request: <prompt> <skill> in, one json + markdown out
jev.py                  # the System One request: the same, with typed questions instead of a prompt
index.py                # the catalog and its numbers: one flat jsonl, and the facts a README is
readme.py               # the page: those numbers said for a reader, in both languages
stale.py                # the comparison: two catalogs in, the changed skills' profiles out
prompts/                # one <id>.md (task) + <id>.json (schema) per chat angle, plus _system.md
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
| `SKILLS_PROFILES_JEV_MODEL`     | `jev-latest`     | The System One model, an alias over the version (`jev-1.13.0`)       |
| `SKILLS_PROFILES_JEV_BASE_URL`  | 302.AI's System One path | Where `jev.py` posts; nothing else does                     |
| `SKILLS_PROFILES_JEV_API_KEY`   | –                | Its key; no key means no call                                        |
| `SKILLS_PROFILES_JEV_TIMEOUT`   | `20`             | Seconds per request: the endpoint answers in one to three, and drops a first call after idle |
| `SKILLS_PROFILES_JEV_MAX_RETRIES` | `3`            | Extra attempts, for a dropped call or a busy gateway                 |
| `SKILLS_PROFILES_MAX_RETRIES`   | `3`              | Extra attempts per LLM call (`0` = a single try)                     |
| `SKILLS_PROFILES_THINKING`      | `false`          | Let the model reason first: the provider's `enable_thinking`, only ever sent as `true`, which is all the documentation states |
| `SKILLS_PROFILES_DRY_RUN`       | `false`          | Use the fake LLM: no API calls                                       |
| `SKILLS_PROFILES_OUTPUT_DIR`    | `output`         | The published root: skills, profiles, upstream and the catalog       |
| `SKILLS_PROFILES_PROMPTS_DIR`   | `prompts`        | Prompt markdown directory (plus `_system.md`)                        |

## Testing

The suite is offline: `conftest.py` writes a fake snapshot tree, and constructing a real LLM client
fails loudly, so a test can never call out even with a local `.env` full of keys.

- `tests/test_gen.py` covers the request: prompt loading and its failure modes, the strict-mode
  rules every schema has to satisfy, template rendering, the keywords a call is sent with, the
  dry-run placeholder, the two output files, and the command - plus the description read out of a
  header as YAML, and the three kinds of header that drop a skill.
- `tests/test_jev.py` covers the other producer: the taxonomy as one object, the angles it names,
  the body a call posts (a state and typed questions, and no messages), a dropped call being retried
  where a rejected one is not, the guard on an answer outside the closed set, and the command - the
  same gate, the same exit codes, and a request printed without a key.
- `tests/test_index.py` covers the catalog: the mirror's row forwarded field by field with the three
  of ours added, a row for every skill it lists - including one with no profile built yet - and a row
  for a skill the mirror has dropped while profiles remain, `null` for a description nothing can be
  read from and for a domain not decided yet, the mirror's spelling of an id against the tree's, an
  orphan walked rather than globbed (a repo whose name starts with a dot among them), the error a
  missing mirror index gives, the `"description":null` spelling the justfile matches on, and the
  write being whole or absent - plus the numbers a README is said from: a json rather than a directory
  as the unit of work, the buildable denominator, a dropped skill counting as neither coverage nor
  dataset, the installs weight, the snapshot read out of `upstream/` instead of stamped, a tree that
  cannot answer saying so in one dash, and the same tree reading the same numbers.
- `tests/test_readme.py` covers the page: both languages holding the same keys, every placeholder in
  them being a number the report has, the page staying inside its length, the two rendered for a tree
  with nothing built and one built partway, each page pointing at the other, both saying they are
  generated, and both being a function of the tree.
- `tests/test_stale.py` covers the comparison: a moved hash retiring exactly that skill, a skill that
  vanished keeping its profiles, a row with no hash saved being nobody's business, a skill whose hash
  moved before anything was built retiring nothing, and the two cold starts (no previous catalog, no
  catalog on the tree).
- `tests/test_just.py` covers the justfile, which owns both the networked and the parallel work:
  a fresh build, a bounded run taking the next skills rather than the first ones again, an
  already-built dataset having nothing to build at all, deleting one json rebuilding exactly that
  one, the `limit` window and its order (the catalog, path order without one), a skill no description
  can be read from being no target at all, `jobs` sizing
  the pool, `just one` reaching outside the window, `just invalidate`
  forgetting exactly one prompt, `just index` joining the mirror's rows with the profiles and
  writing the READMEs beside them, `just refresh`
  retiring exactly what a new snapshot changed, `DRY=1` in both of its
  spellings, an inherited `SKILLS_PROFILES_DRY_RUN` reaching the jobs unclobbered, `just sync`
  fetching a snapshot from a local tarball, unpacking its two layers and replacing them wholesale,
  rewriting the catalog it moved the sources under, the guard that keeps `rm -rf` away from a
  directory that is not a snapshot, a snapshot fetched by `just` being what the batch
  then reads, `just clean`, and the missing-sources error naming the fix.

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
| `publish.yml` | manual | `restore-dist` → `just limit=… jobs=… rpm=… prompt=…` → `just index` → `publish-dist` (`date-counter`). Builds against the dataset `sync` published, never against upstream, and needs the endpoint's own secret and variables. |

Both data workflows restore first and publish last, so a run is a fresh runner plus two tarballs. Two
composite actions own the two ends:

- `.github/actions/restore-dist` puts the published root back into `output/`, minus the `latest`
  pointer: a publish writes that, a run never reads it.
- `.github/actions/publish-dist` turns `output/` into the `dist` branch: one commit, history pruned
  to a time window, a `dist-YYYY-MM-DD` or `dist-<base>-N` tag, and a `latest` pointer naming it. A
  tree that has not changed publishes nothing and spends no tag, because the comparison with the
  branch happens before a tag is chosen.

Nothing stamps provenance any more: the skills are published inside the same tree, so what a profile
was built from is the `skills/<id>/` beside it - which is also why publishing is one directory
instead of two.

Docs rule: every English document has a Chinese counterpart (`README.md` / `README.zh-CN.md`,
`DEVELOPING.md` / `DEVELOPING.zh-CN.md`) — keep both in sync, in the same pass.
