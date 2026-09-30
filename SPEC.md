# skills-profiles: the outside

The black-box view: everything a user or a consumer can see, and nothing about how it is built.

**The product is one directory** — `output/`: one directory per skill holding its `SKILL.md`, one
domain label and one Chinese page written about each, and one catalog joining them. The generator
exists to produce that directory, so it is the interface, and the commands only decide which part of
it gets written.

中文: [SPEC.zh-CN.md](SPEC.zh-CN.md)

## 1. Output — the interface

```
<output_dir>/
├── skills/<owner>/<repo>/<slug>/     # one directory per skill - it installs as the skill itself,
│   ├── SKILL.md                      #   its annotations riding along: the source page, fetched
│   │                                 #   from the skill's own repository
│   ├── domain.json                   # the label: {domain, confidence, probabilities}
│   └── SKILL.zh.md                   # the page in Chinese; its front matter carries the
│                                     #   Chinese description
├── repos.jsonl                       # one row per repository: {id, owner, repo, description,
│                                     #   stars, updated_at, pushed_at, html_url, gone, fetched_at}
├── owners/<owner>.png                # one owner's avatar, the fixed path a frontend builds from
│                                     #   the owner alone - an owner has no catalog
├── skills.jsonl                      # `just index`: the catalog, one flat line per skill
└── README.md                         # ... and the front page beside it: what this directory is,
    README.zh-CN.md                   #     and how much of it is built; the same page, in Chinese
```

Nothing here needs the mirror: the catalog names every skill, and each skill directory holds the
source page with what was built about it. `repos.jsonl` and the `owners/` avatars are the entities
above a skill - one row per repository (its description, stars and last-update time) and one avatar
per owner - keyed by the `owner/repo` (or `owner`) a skill id leads with, so they join without a
second catalog. The mirror's listing is pulled fresh by `just sync`
into the catalog - its only lasting trace.

`<id>` is the skill id, `{owner}/{repo}/{slug}`. A row carries it the way the mirror spells it; the
two directories spell a `:` and an `&` as `_`, which is also the handle `jev.py` is handed.

`domain.json` is `{domain, confidence, probabilities}`:

- `domain` — one of 13 closed English categories: development · testing · data-analysis ·
  devops-security · office-productivity · content-creation · design-media · knowledge-management ·
  business-ops · finance-payment · education · lifestyle · other. It filters directly.
- `confidence` — the endpoint's own reading of how close the call was, `null` when it does not say;
  not the probability of the label being right, published to be sorted on rather than trusted as
  one.
- `probabilities` — that distribution, kept whole because it cannot be recovered from the winner: a
  call decided 0.52 to 0.48 says something a call decided 0.99 to 0.01 does not. Every value is
  English.

- One directory per skill, two generated files: `domain.json`, the endpoint's whole typed
  answer; and `SKILL.zh.md`, the page in Chinese - a machine-assembled front matter whose
  `description` is the Chinese translation of the one-line description, over the translated body.
  The model never shapes the front matter, so the description always parses back out of the page.
- **The entities are one catalog and one file.** `repos.jsonl` holds one row per repository (`id`,
  `owner`, `repo`, `description`, `stars`, `updated_at`, `pushed_at`, `html_url`, `gone`,
  `fetched_at`), and each owner is one avatar at the fixed `owners/<owner>.png` - a path a frontend
  builds from the owner alone, with no owner catalog to read. A repository row with `gone: true` is
  one GitHub has no answer for: the negative lives in the catalog, so no run fetches it again. An
  owner has no such row, so a 404 owner is a dead end retried next run - it does not fail the run.
  The join to a skill is the `owner/repo` (or `owner`) its id leads with.
- **The catalog is the way in.** `skills.jsonl` holds one flat line per skill the mirror lists and
  the tree can still build, in the mirror's own order - the mirror's row (`id`, `installs`) plus the
  `description` read out of that skill's own `SKILL.md`, its `description_zh` (the `description` in
  the zh page's front matter), the `domain` it was labelled with, and the `confidence` it was
  labelled at. Every listed skill is a row, fetched or not: the joined fields are `null` until the
  tree fetches and builds it, so an unfetched skill is a row of nulls rather than a missing one, and
  the catalog is both the dataset and the order the batches work in. A listed skill whose repository
  is already on disk without a readable description is no row at all - the fetch took the repository
  and yielded nothing, so no run could ever build it, and it does not dilute the dataset.
  `.domain != null` is what has been labelled,
  `.description_zh != null` what has been translated, and `.installs` ranks what has not. The
  catalog takes two of the three label fields; the profile is where the answer lives.
- **The READMEs are the front page**, written by the same command from the same walk: two lines on
  what the directory is, then how much of the dataset is built — each angle's count and share of the
  mirror's installs, and the repository and owner coverage the entity catalog adds, under the
  snapshot they describe. Nothing reads them back, and every line is a
  function of the tree, so a tree that did not change rewrites them identically.
- The two angles have two producers. `jev.py` asks a System One endpoint a typed question instead
  of sending a chat prompt: that is why `domain` has no prompt pair and no reason line, the
  endpoint answers a closed set with one member of it and writes no prose. `skill_zh.py` asks an
  OpenAI-compatible chat endpoint once for the description and then once per markdown piece of
  the body - a body too long for one answer cut on its own seams and translated piece by piece -
  and assembles `SKILL.zh.md` by code, writing it only when every call came back, since a
  half-translated page must never pass for a whole one. Both are thin angles over one shared
  kernel, `common.py`: the tree, the source, the prompt files, the retried call, the atomic write
  and the command itself. The window, the lazy fetch and the pool that drives them are one
  driver, `batch.py`, with the justfile only launching it.

## 2. Input

| what                                                             | where                 | put there by                                                                             |
| ---------------------------------------------------------------- | --------------------- | ---------------------------------------------------------------------------------------- |
| the skills: one directory per skill, its SKILL.md and its angles | `<output_dir>/skills` | the batches - each fetches a repository the first time it builds one of its skills, once |
| the state template `prompts/_system.md`                          | `prompts_dir`         | you                                                                                      |
| the translation system prompt `prompts/translate.md`             | `prompts_dir`         | you                                                                                      |
| the translation user prompt `prompts/translate_user.md`          | `prompts_dir`         | you                                                                                      |
| the page system prompt `prompts/skill_zh.md`                     | `prompts_dir`         | you                                                                                      |
| the page user prompt `prompts/skill_zh_user.md`                  | `prompts_dir`         | you                                                                                      |

The mirror's listing - `just sync` pulls it fresh into the catalog, which is its only lasting
trace - is the row set: the order a batch works in (installs, descending), and the installs the
tree has no way to know. `skills/<id>/SKILL.md` is the whole of what the state is built from —
plus, for disambiguation, the one-line descriptions of the sibling skills beside it in its
repository; a fetch takes every skill's SKILL.md from the repository - each one a subdirectory's
SKILL.md, a repository whose only one sits at the root being a single skill with that source, while
a root one beside subdirectory skills stays its readme - so the tree holds the skills the
repository ships.

A skill's one-line description is not in the mirror's index, upstream having dropped it: it is read
from the skill's own front matter, and a skill whose front matter does not yield one is never built
by either producer. The mirror is a fetched snapshot, read-only. The taxonomy is code: `CRITERIA`
and `INSTRUCTION` in `jev.py`, handed to the endpoint as the options its answer is confined to -
stated once, with no enum in a schema and no decoder to keep in step. The translation task is the
opposite: its turns are Jinja templates - `prompts/translate.md` and `prompts/translate_user.md`
for the description, `prompts/skill_zh.md` and `prompts/skill_zh_user.md` for the body - rendered
with the fixed target language and the text, with nothing about the task in code.

## 3. Control

The batch is one driver, `batch.py`, with command-line modifiers, run for one angle or both; the
justfile only chooses the command and the knobs. The verbs:

| command              | does                                                                                                                                                      |
| -------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `just build <angle>` | build the next `limit` skills still missing the angle's file (`domain`, `skill_zh`, or `all` for both in one pool over the shared window); a bare `just` is `build domain` with the default one-skill limit |
| `just clean <angle>` | the inverse window: delete the angle's file from the next `limit` skills that have one (`domain`, `skill_zh`, or `all` for both); `limit 0` is every one  |
| `just meta`          | fetch every repository and owner the catalog names that still lacks one - the profiles into `repos.jsonl`, the avatars into `owners/<owner>.png`; `just meta --clean` forgets them instead |
| `just index`         | write the catalog and the READMEs: the mirror's rows joined with the descriptions, their translations and the labels, and the published root's front page |
| `just sync`          | reconcile with the mirror: pull its listing, merge sources from repositories it added a skill to, the tree's other sources left where they are; a skill the mirror dropped is named on stderr, its files left in place |
| `just test`          | run the suite                                                                                                                                             |

`build` and `clean` are inverse windows over the same catalog order, bounded by the same `limit`:
build counts skills missing the file, clean skills holding it. A full reset that keeps the
fetched sources is `just limit=0 clean all` then `just sync`. Dropping the sources themselves is
deleting the repository directory, after which the next build or sync fetches it again. Building
one named skill outside the window is running its script directly (`jev.py <id>` /
`skill_zh.py <id>`). `meta` is the one entity verb: it fetches every repository the catalog names
without a row and every owner without an avatar, and `meta --clean` forgets them again - the catalog
is still the order, read as `owner/repo` and `owner`.

The modifiers are command-line variables, nowhere else:

| knob                                      | default                            | meaning                                                                                                                                                                                                                 |
| ----------------------------------------- | ---------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `limit`                                   | 1                                  | the next N skills still missing the angle being built, in the catalog's order — the mirror's, installs descending; `0` = all, with no cap. It counts work rather than positions, so repeated runs walk down the dataset |
| `jobs`                                    | 32                                 | calls in flight at once; a transient 429 is still absorbed by the client's own retry                                                                                                                                    |
| `dry`                                     | –                                  | `1` = fake endpoint, real layout                                                                                                                                                                                        |
| `output_dir` `prompts_dir` `listing` `py` | see [DEVELOPING.md](DEVELOPING.md) | plumbing                                                                                                                                                                                                                |

Under it, one skill at a time:

```
jev.py <id> [--print]         # dev only: the typed question, the state from _system.md - print, call nothing
skill_zh.py <id> [--print]    # dev only: the page's requests as one array, description first then body pieces
```

- stdout is data (the request, under `--print`); stderr is progress.
- jev.py's source is cut at 20 000 characters, and the cut is announced inside the source itself;
  skill_zh.py cuts the body on its own markdown seams, and sends the one-line description whole.
- The chat calls run with the MaaS deep-thinking switch on (`enable_thinking`, `max_tokens` at the
  documented ceiling): the model reasons into `reasoning_content` first; that draft is not read or
  stored - the page holds `content`, the translation, alone.
- Exit: `0` built · `1` unusable input or endpoint · `2` bad arguments. A skill whose front matter
  yields no description is unusable input: it is dropped, one line on stderr and nothing written.
  The batch itself exits `1` only when every job in its window failed - partial output is published
  output.

## 4. Configuration

`.env` (copy [`.env.example`](.env.example)) or `SKILLS_PROFILES_*`; env → `.env` → defaults. It
holds two endpoints: the typed one as `API_KEY`, `BASE_URL`, `MODEL`, and the OpenAI-compatible
chat one as `TRANSLATE_API_KEY`, `TRANSLATE_BASE_URL`, `TRANSLATE_MODEL` — plus `MAX_RETRIES` and
`DRY_RUN`, the `GITHUB_TOKEN` the entity profiles are read with, and the two paths if you must move
them. The timeouts are one per endpoint: `TIMEOUT`
(the typed endpoint answers in one to three seconds) and `TRANSLATE_TIMEOUT`, which defaults to
120 because a thinking call reasons first and routinely runs past the typed endpoint's patience.
The chat caller also takes `TRANSLATE_ENABLE_THINKING` (on by default) and `TRANSLATE_MAX_TOKENS`.
The page angle, `skill_zh.py`, is the only caller of the chat endpoint, asking it for the
description and then the body pieces over the same `TRANSLATE_*` settings. The default address and
model point at Xunfei Xingchen MaaS serving Spark-X2.5-4B; the model id is whatever the console's
service page shows, so a subscription spells it via `TRANSLATE_MODEL`. A skill that endpoint fails
is retried once on a fallback chat endpoint — `TRANSLATE_FALLBACK_BASE_URL`,
`TRANSLATE_FALLBACK_MODEL` and `TRANSLATE_FALLBACK_API_KEY`; the defaults point at Agnes AI, and
an unset key turns the fallback off. The fallback request carries only the model swap: the
MaaS-only thinking switch is left out, which a stricter OpenAI-compatible endpoint would reject
the whole request over.

The batch knobs above are **not** environment variables: a run changes only because a run said so.

## 5. What a consumer may rely on

- **Existence is the cache.** Anything already written is never rebuilt; a stopped batch resumes at
  the first missing file. The two angles cache independently: having a label does not satisfy a
  zh-page run, or the reverse.
- **Invalidation is `clean`.** Editing `_system.md` invalidates nothing by itself, and a source
  already on disk is not refetched: an angle is regenerated by deleting its file (`just clean
<angle>`), and a source is refetched by deleting its repository directory, or
  by `just sync` when the listing has since added a skill to that repository.
- **A failure loses nothing.** A failed call writes no file and does not end the batch; the next run
  retries exactly it.
- **A skill nothing can be read from is never built.** Its front matter has to yield a description
  before a call is made, so the catalog leaves it out and the window never sees it:
  no call, no file, no failure to retry - for either angle.
- **A file is whole or absent.** The json is renamed into place, so a half-written one is never
  visible.
- **One turn per file.** No ordering, no dependency between the angles, no cascade.
- **The catalog is derived and complete.** `just index` rebuilds it whole from the tree, offline: one
  row per skill the mirror lists and the tree can still build, its joined fields `null` while the
  tree has not produced them -
  with the READMEs written from the same walk, so no two things there can describe different trees.
- **The layout is the only contract.** Publish `output/` as it is.

## 6. Open — to agree before this is the spec

1. Is `test` part of the surface, or dev-only (kept out of the promise above)? Request rendering
   is settled: there is no recipe for it - `--print` is a dev-only flag on the two scripts, run
   directly with `uv run python <script> <id> --print`.
2. Should `listing` and `py` be public knobs, or plumbing with a fixed default?
