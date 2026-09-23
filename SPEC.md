# skills-profiles: the outside

The black-box view: everything a user or a consumer can see, and nothing about how it is built.

**The product is one directory** — `output/`: the mirror's skill directories exactly as it publishes
them, one domain label written about each, the mirror's own files beside them, and one catalog
joining the two. The generator exists to produce that directory, so it is the interface, and the
commands only decide which part of it gets written.

中文: [SPEC.zh-CN.md](SPEC.zh-CN.md)

## 1. Output — the interface

```
<output_dir>/
├── skills/<owner>/<repo>/<slug>/     # the mirror's own directory, complete and unchanged:
│   ├── SKILL.md                      #   copy one of these into a skills folder and the skill is
│   └── ...every file the skill ships #   installed - which is what a user downloads
├── profiles/<owner>/<repo>/<slug>/
│   └── domain.json                   # the label: {domain, confidence, probabilities}
├── skills.jsonl                      # `just index`: the catalog, one flat line per skill
├── README.md                         # ... and the front page beside it: what this directory is,
├── README.zh-CN.md                   #     and how much of it is built; the same page, in Chinese
└── upstream/                         # the rest of the mirror: skills.jsonl, repos.jsonl, owners.jsonl,
                                      # curated.jsonl, trending.json, stats.json, latest, avatars/
```

Nothing here needs the mirror: a skill is installed from `skills/`, and everything known about it is
in `skills.jsonl`.

`<id>` is the skill id, `{owner}/{repo}/{slug}`. A row carries it the way the mirror spells it; the
two directories spell a `:` and an `&` as `_`, which is also the handle `jev.py` is handed.

`domain.json` is `{domain, confidence, probabilities}`:

- `domain` — one of 13 closed English categories: development · testing · data-analysis ·
  devops-security · office-productivity · content-creation · design-media · knowledge-management ·
  business-ops · finance-payment · education · lifestyle · other. It filters directly.
- `confidence` — the endpoint's own reading of how close the call was, derived from the distribution
  over the enum; not the probability of the label being right, published to be sorted on rather than
  trusted as one.
- `probabilities` — that distribution, kept whole because it cannot be recovered from the winner: a
  call decided 0.52 to 0.48 says something a call decided 0.99 to 0.01 does not. Every value is
  English.

- One directory per skill, one file: `domain.json`, the endpoint's whole answer.
- **The catalog is the way in.** `skills.jsonl` is written by `just index`: one flat line per skill,
  in the mirror's own order, being the mirror's row — `id`, `installs`, `url`, `hash`, `fetchedAt` —
  plus the `description` read out of that skill's own `SKILL.md`, the `domain` it was labelled with,
  and the `confidence` it was labelled at. The three are `null` while unknown, so a row states the
  dataset rather than the work: `.domain != null` is what has been built, and `.installs` ranks what
  has not. The catalog takes two of the three label fields; the profile is where the answer lives.
- **The READMEs are the front page**, written by the same command from the same walk: two lines on
  what the directory is, then how much of the dataset is labelled — the count and its share of the
  mirror's installs, under the snapshot they describe. Nothing reads them back, and every line is a
  function of the tree, so a tree that did not change rewrites them identically.
- The label is written by one producer: `jev.py` asks a System One endpoint a typed question instead
  of sending a chat prompt. That is why `domain` has no prompt pair and no reason line: the endpoint
  answers a closed set with one member of it and writes no prose.

## 2. Input

| what | where | put there by |
| --- | --- | --- |
| the mirror: a directory per skill, and its own index and metadata | `<output_dir>/skills` and `<output_dir>/upstream` | `just sync`, from the upstream `dist` branch |
| the state template `prompts/_system.md` | `prompts_dir` | you |

`upstream/skills.jsonl` is the mirror's own listing, and it is the catalog's left side: the row set,
the order a batch works in (installs, descending), and the fields the tree has no way to know.
`skills/<id>/SKILL.md` is the whole of what the state is built from — plus, for disambiguation, the
one-line descriptions of the sibling skills beside it in its repository; the other files in the
skill directory are carried for the user who installs it, not read.

A skill's one-line description is not in the mirror's index, upstream having dropped it: it is read
from the skill's own front matter, and a skill whose front matter does not yield one is never built.
The mirror is a fetched snapshot, read-only. The taxonomy is code: `CRITERIA` and `INSTRUCTION` in
`jev.py`, handed to the endpoint as the options its answer is confined to - stated once, with no enum
in a schema and no decoder to keep in step.

## 3. Control

The batch is one recipe with modifiers, plus six verbs:

| command | does |
| --- | --- |
| `just` | label every skill still missing `domain.json` in the window |
| `just one <id>` | label one skill, inside or outside the window |
| `just invalidate` | delete every label, everywhere |
| `just index` | write the catalog and the READMEs: the mirror's rows joined with the descriptions and the labels, and the published root's front page |
| `just sync` | fetch the mirror, replacing `skills/` and `upstream/` wholesale, and rewrite the catalog |
| `just refresh` | fetch it, and drop every label whose source hash changed with it |
| `just clean` | drop the profiles, the catalog and the READMEs; keep the skills and the mirror's files |
| `just render <id>` · `just test` | dev only: print the request · run the suite |

The modifiers are command-line variables, nowhere else:

| knob | default | meaning |
| --- | --- | --- |
| `limit` | 1 | the next N skills still unlabelled, in the catalog's order — the mirror's, installs descending; `0` = all, with no cap. It counts work rather than positions, so repeated runs walk down the dataset |
| `jobs` | one per core | calls in flight at once |
| `rpm` | 0 | pace the run to the endpoint's per-minute allowance |
| `dry` | – | `1` = fake endpoint, real layout |
| `output_dir` `prompts_dir` `snapshot` `py` | see [DEVELOPING.md](DEVELOPING.md) | plumbing |

Under it, one skill at a time:

```
jev.py <id> [--print]     # the typed question in jev.py itself, the state from _system.md
```

- stdout is data (the request, under `--print`); stderr is progress.
- The source is cut at 20 000 characters, and the cut is announced inside the source itself.
- Exit: `0` built · `1` unusable input or endpoint · `2` bad arguments. A skill whose front matter
  yields no description is unusable input: it is dropped, one line on stderr and nothing written.

## 4. Configuration

`.env` (copy [`.env.example`](.env.example)) or `SKILLS_PROFILES_*`; env → `.env` → defaults. It
holds the one endpoint only: `API_KEY`, `BASE_URL`, `MODEL`, `TIMEOUT`, `MAX_RETRIES` — plus
`DRY_RUN` and the two paths if you must move them.

The batch knobs above are **not** environment variables: a run changes only because a run said so.

## 5. What a consumer may rely on

- **Existence is the cache.** Anything already written is never rebuilt; a stopped batch resumes at
  the first missing file.
- **Invalidation is deletion.** Editing `_system.md` invalidates nothing by itself; a new snapshot
  invalidates what it changed, and `just refresh` is the verb that deletes those labels.
- **A failure loses nothing.** A failed call writes no file and does not end the batch; the next run
  retries exactly it.
- **A skill nothing can be read from is never built.** Its front matter has to yield a description
  before a call is made, so the catalog writes `description: null` for it and the window skips the
  row: no call, no file, no failure to retry.
- **A file is whole or absent.** The json is renamed into place, so a half-written one is never
  visible.
- **One turn per file.** No ordering, no dependency, no cascade.
- **The catalog is derived and complete.** `just index` rebuilds it whole from the tree, offline: one
  row per skill the mirror lists, and one for a skill it has dropped while a label remains — with the
  READMEs written from the same walk, so no two things there can describe different trees.
- **The layout is the only contract.** Publish `output/` as it is; the mirror's own files included.

## 6. Open — to agree before this is the spec

1. Are `render` and `test` part of the surface, or dev-only (kept out of the promise above)?
2. Should `snapshot` and `py` be public knobs, or plumbing with a fixed default?
