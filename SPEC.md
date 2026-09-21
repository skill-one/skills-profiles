# skills-profiles: the outside

The black-box view: everything a user or a consumer can see, and nothing about how it is built.

**The product is one directory** — `output/`: the mirror's skill directories exactly as it publishes
them, Chinese profiles written about them, the mirror's own files beside them, and one catalog joining
the two. The generator exists to produce that directory, so it is the interface, and the commands only
decide which part of it gets written.

中文: [SPEC.zh-CN.md](SPEC.zh-CN.md)

## 1. Output — the interface


```
<output_dir>/
├── skills/<owner>/<repo>/<slug>/     # the mirror's own directory, complete and unchanged:
│   ├── SKILL.md                      #   copy one of these into a skills folder and the skill is
│   └── ...every file the skill ships #   installed - which is what a user downloads
├── profiles/<owner>/<repo>/<slug>/
│   ├── domain.json  scenario.json  tagline.json
│   ├── blackbox.json  whitebox.json  comments.json
│   └── md/<angle>.md      # the same content, rendered for reading
├── skills.jsonl           # `just index`: the catalog, one flat line per skill
├── README.md              # ... and the front page beside it: what this directory is, and how
├── README.zh-CN.md        #     much of it is built; the same page, in Chinese
└── upstream/              # the rest of the mirror: skills.jsonl, repos.jsonl, owners.jsonl,
                           # curated.jsonl, trending.json, stats.json, latest, avatars/
```

Nothing here needs the mirror: a skill is installed from `skills/`, and everything known about it is
in `skills.jsonl`.

`<id>` is the skill id, `{owner}/{repo}/{slug}`. A row carries it the way the mirror spells it; the
two directories spell a `:` and an `&` as `_`, which is also the handle `gen.py` is handed.

| angle | json shape | content |
| --- | --- | --- |
| `domain` | `{domain, confidence, probabilities}` | one of 13 closed English categories, the endpoint's own confidence in it, and the distribution it was read off |
| `scenario` | `{text}` | a ≤100-character pitch, built on the user's pain point |
| `tagline` | `{taglines[3]}` | three slogans, ≤20 characters each |
| `blackbox` | `{function, input_output[3–5]}` | outside view: what you hand it → what you get back |
| `whitebox` | `{execution_flow[3–5], mechanisms[2–3]}` | inside view: happy path, mechanisms, real dependencies |
| `comments` | `{comments[4–6]}` | first-person user notes: `{user, category, comment}` |

- One directory per skill, one file per angle. Every angle is independent — no file reads another.
- A `.json` is the data; `md/<angle>.md` is the same fields rendered, written first.
- **The catalog is the way in.** `skills.jsonl` is written by `just index`: one flat line per skill,
  in the mirror's own order, being the mirror's row — `id`, `installs`, `url`, `hash`, `fetchedAt` —
  plus the `description` read out of that skill's own `SKILL.md`, the `domain` this project labelled
  it with, and the `confidence` it was labelled at.
  The three are `null` while they are unknown, so a row states the dataset rather than the work:
  `.domain != null` is what has been built, and `.installs` ranks what has not.
- **The READMEs are the front page**, written by the same command from the same walk: two lines on
  what the directory is, then how much of the dataset is built — the `skill × angle` cells on disk,
  per angle, counted and weighted by installs, under the snapshot they describe. They stay short on
  purpose: the project's own prose lives in this repository, and a longer page would be a second copy
  of it to keep in step. Nothing reads them back, and every line is a function of the tree, so a tree
  that did not change rewrites them identically.
- Ids, paths and field names are ASCII; `domain` is one member of a closed English enum, so it
  filters directly. The profile keeps the whole answer beside it: `confidence`, the endpoint's own
  reading of how close the call was - derived from the distribution over the enum, so it is not the
  probability of the label being right, and published to be sorted on rather than trusted as one -
  and `probabilities`, that distribution. It is kept because it cannot be recovered from the winner:
  a call decided 0.52 to 0.48 says something a call decided 0.99 to 0.01 does not. The catalog takes
  two of the three, the label and the confidence, and the profile is where the answer itself lives.
  The `domain` angle's value is English, every other angle's values are Chinese.
- An angle is built by one of two producers, and `just` sends a pair to whichever owns it: a prompt
  pair goes to a chat model, and an angle named by `jev.py --angles` is asked of a System One
  endpoint as typed questions instead. That is why `domain` has no prompt pair and no reason line:
  the endpoint answers a closed set with one member of it and writes no prose.

## 2. Input

| what | where | put there by |
| --- | --- | --- |
| the mirror: a directory per skill, and its own index and metadata | `<output_dir>/skills` and `<output_dir>/upstream` | `just sync`, from the upstream `dist` branch |
| a prompt: `prompts/<id>.md` (the task) + `prompts/<id>.json` (its schema) | `prompts_dir` | you, by hand |
| the shared system prompt `prompts/_system.md` | `prompts_dir` | you |

`upstream/skills.jsonl` is the mirror's own listing, and it is the catalog's left side: the row set,
the order a batch works in (installs, descending), and the fields the tree has no way to know.
`skills/<id>/SKILL.md` is the whole of what a prompt is built from — the files beside it are carried
for the user who installs the skill, not read.

A skill's one-line description is not in the mirror's index, upstream having dropped it: it is read
from the skill's own front matter, and a skill whose front matter does not yield one is never built.

The mirror is a fetched snapshot, read-only. A prompt is a task/contract pair: the schema travels to
the provider verbatim as a strict `json_schema` response format, which is what makes **adding a chat
angle two files and no code**. An angle on the other side of the split is an entry in `jev.py`: the
questions, their types, and the options a closed one may answer - which is where the domain taxonomy
lives now, stated once rather than as prose for a model and an enum for a decoder.

## 3. Control

The batch is one recipe with modifiers, plus six verbs:

| command | does |
| --- | --- |
| `just` | build every missing (skill, angle) in the window |
| `just one <angle> <id>` | build one cell, inside or outside the window |
| `just invalidate <angle>` | delete that angle's profiles, everywhere |
| `just index` | write the catalog and the READMEs: the mirror's rows joined with the descriptions and the domains, and the published root's front page |
| `just sync` | fetch the mirror, replacing `skills/` and `upstream/` wholesale, and rewrite the catalog |
| `just refresh` | fetch it, and drop every profile whose source hash changed with it |
| `just clean` | drop the profiles, the catalog and the READMEs; keep the skills and the mirror's files |
| `just render <angle> <id>` · `just test` | dev only: print the request · run the suite |

The modifiers are command-line variables, nowhere else:

| knob | default | meaning |
| --- | --- | --- |
| `limit` | 1 | the next N skills that still need something, in the catalog's order — the mirror's, installs descending; `0` = all, with no cap. It counts work rather than positions, so repeated runs walk down the dataset, and it bounds the batch |
| `prompt` | – | one angle, or every angle |
| `jobs` | one per core | generations in flight at once |
| `rpm` | 0 | pace the run to the endpoint's per-minute allowance |
| `dry` | – | `1` = fake model, real layout |
| `output_dir` `prompts_dir` `snapshot` `py` | see [DEVELOPING.md](DEVELOPING.md) | plumbing |

Under it, one cell at a time:

```
gen.py <angle> <id> [--print]     # a chat angle: prompts/<id>.md with its schema beside it
jev.py <angle> <id> [--print]     # a System One angle: the questions in jev.py itself
```

The one the batch uses is whichever names that angle: `prompts/*.json` for the first, `jev.py
--angles` for the second.

- stdout is data (the request, under `--print`); stderr is progress.
- The source is cut at 20 000 characters, and the cut is announced inside the source itself.
- Exit: `0` built · `1` unusable input or model · `2` bad arguments. A skill whose front matter
  yields no description is unusable input: it is dropped, one line on stderr and nothing written.

## 4. Configuration

`.env` (copy [`.env.example`](.env.example)) or `SKILLS_PROFILES_*`; env → `.env` → defaults. It
holds the two endpoints only: the chat one as `MODEL`, `BASE_URL`, `API_KEY`, `MAX_RETRIES`,
`TIMEOUT`, `THINKING`, and the System One one as `JEV_MODEL`, `JEV_BASE_URL`, `JEV_API_KEY`,
`JEV_TIMEOUT`, `JEV_MAX_RETRIES` — plus `DRY_RUN` and the two paths if you must move them.

The batch knobs above are **not** environment variables: a run changes only because a run said so.

## 5. What a consumer may rely on

- **Existence is the cache.** Anything already written is never rebuilt; a stopped batch resumes
  at the first missing file.
- **Invalidation is deletion.** Editing a template invalidates nothing by itself; a new snapshot
  invalidates what it changed, and `just refresh` is the verb that deletes those profiles.
- **A failure loses nothing.** A failed call writes no file and does not end the batch; the next
  run retries exactly it.
- **A skill nothing can be read from is never built.** Its front matter has to yield a description
  before a call is made, so the catalog writes `description: null` for it and the window skips the
  row: no call, no file, no failure to retry.
- **A file is whole or absent.** The markdown is written first, the json renamed into place.
- **One turn per file.** No ordering, no dependency, no cascade.
- **The catalog is derived and complete.** `just index` rebuilds it whole from the tree, offline: one
  row per skill the mirror lists, and one for a skill it has dropped while profiles remain — with the
  READMEs written from the same walk, so no two things there can describe different trees.
- **The layout is the only contract.** Publish `output/` as it is; the mirror's own files included.

## 6. Open — to agree before this is the spec

1. Are `render` and `test` part of the surface, or dev-only (kept out of the promise above)?
2. Should `snapshot` and `py` be public knobs, or plumbing with a fixed default?
