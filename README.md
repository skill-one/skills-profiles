# skills-profiles

Domain labels and Chinese translations for the [agent skills](https://www.skills.sh) collected by
[skill-one/skills-sh-mirror](https://github.com/skill-one/skills-sh-mirror): one closed-category
label per skill, each a single typed call to the Jev (TypeSafe System One) endpoint built from
that skill's own description and `SKILL.md`, and two OpenAI-compatible chat calls - one
translating that description into Chinese, one translating the `SKILL.md` body into a Chinese
page of its own.

中文: [README.zh-CN.md](README.zh-CN.md) · Dev guide: [DEVELOPING.md](DEVELOPING.md)

## What it produces

Everything lands under one root, `output/`: the source pages the angles were built from, what is
written about them — a label and Chinese translations — and one catalog joining it all, so nothing
here sends a reader back to the mirror. Publishing is copying that one directory.

```
output/
├── skills/<owner>/<repo>/<slug>/    one directory per skill, its SKILL.md alone: the source page
│   └── SKILL.md                     the angles read; the full skill lives in its own repository
├── profiles/<owner>/<repo>/<slug>/
│   ├── domain.json                  one label, the typed endpoint's whole answer
│   ├── description_zh.json          one Chinese translation of the one-line description
│   └── skill_zh.md                  the SKILL.md body, translated into Chinese
├── skills.jsonl                     `just index`: one flat line per skill — the mirror's own row
│                                    (id, installs, url, hash, fetchedAt) plus description,
│                                    description_zh and domain
├── README.md                        ... and the front page beside it: what this directory is, and
├── README.zh-CN.md                  how much of it is built — the first is in English, this Chinese
└── upstream/                        the mirror's own files the tree reads: its index, the version
                                     pointer, the scan stats
```

`skills.jsonl` is the way in. It lists every skill the mirror has, in the mirror's own order — the
most installed first — with the `description` read out of that skill's own `SKILL.md`, its
`description_zh`, the `domain` this project labelled it with, and how sure the endpoint was of it.
All four are `null` while they are unknown, so the labelled part of the dataset is a filter away:

```bash
jq -r 'select(.domain == "development") | [.installs, .id] | @tsv' output/skills.jsonl | head

# the labels the endpoint was least sure of, with the rest of the answer in the profile beside them
jq -r 'select(.confidence < 0.7) | [.confidence, .domain, .id] | @tsv' output/skills.jsonl
```

One directory per skill, three files: `domain.json`, `description_zh.json` and `skill_zh.md`. Each
is written in full the moment it is generated — so an interrupted batch loses only the call it was
in the middle of, and the next one picks up where it stopped. The three angles are independent:
each is built and rebuilt on its own.

`domain.json` is `{domain, confidence, probabilities}`: one of the 13 English categories below, the
endpoint's confidence in it, and the distribution it was read off. Everything is English.

`domain` is one member of the closed enum, so it is directly filterable:
development · testing · data-analysis · devops-security · office-productivity · content-creation ·
design-media · knowledge-management · business-ops · finance-payment · education · lifestyle ·
other. Beside it, `confidence` is how sure the endpoint was, derived from its distribution over the
whole enum — not the probability of the label being right, but the number to sort on when you want
to find the labels worth a second look.

The profile keeps the whole answer, `probabilities` included, because the winner does not contain
it: a call decided 0.52 to 0.48 says something a call decided 0.99 to 0.01 does not. The catalog
carries the label and the confidence and stops there:

```bash
# one label was chosen; what the endpoint nearly chose instead is in the same skill's profile
jq '{domain, confidence, second: (.probabilities | to_entries | sort_by(-.value) | .[1])}' \
  output/profiles/mattpocock/skills/grill-me/domain.json
```

`description_zh.json` is just `{description_zh}`: the one-line description rendered in Chinese,
product names and code kept as written and Chinese left unchanged. A chat endpoint has no closed
enum, so there is no confidence and no distribution — the string is the whole answer.

## Running it

Needs Python 3.12+, [uv](https://docs.astral.sh/uv/) and [`just`](https://just.systems). Credentials
go in a local `.env` (copy [`.env.example`](.env.example)); the hosts touched are the mirror, the
System One endpoint (asked typed questions rather than a prompt) and the OpenAI-compatible chat
endpoint that does the translations.

```bash
uv sync
just sync              # fetch the mirror into output/skills and output/upstream
just refresh           # ... and drop the profiles whose source changed with it
just                   # label the first skill: a one-skill smoke run
just limit=0           # label every skill still missing one, the whole snapshot, no cap
just limit=20 jobs=8   # eight at a time, for the first 20 skills (default pool: 32)
just dry=1 limit=2     # offline smoke test: fake endpoint, real layout
just translate         # the second angle: translate the first missing description_zh
just limit=0 translate # translate every skill, same limit/jobs/dry knobs as above
just skill-zh          # the third angle: the SKILL.md body in Chinese, same knobs
just index             # rebuild output/skills.jsonl and the READMEs from what is on disk
```

`jobs` bounds how many calls run at once (32 by default); a transient 429 is left to the client's
own retry, there is no per-minute pacing.

`limit` counts work, not positions: it takes the next skills still missing the angle being built,
in the catalog's own order (the mirror's: installs descending), so a bounded run does the most
installed skills first and repeated runs walk down the dataset. An output that already exists is
never rebuilt — the files are the whole cache. `just invalidate` and `just invalidate-translate`
(or deleting an output, or `just clean`) is how an angle is regenerated.
See [DEVELOPING.md](DEVELOPING.md).

## Consuming it

The catalog says what a skill is; the two directories are the payload. `output/skills/<id>/` holds
the source page every angle was built from, and `output/profiles/<id>/` holds what was written
about it: `domain.json`, `description_zh.json` and the Chinese page `skill_zh.md`.
`<id>` is the path under both, with a `:` or an `&` spelled `_`. Nothing here is an installation:
a skill ships more than its `SKILL.md` — scripts, references, assets — and the whole of it lives
in its own repository, which the catalog's `url` names.

```bash
# what a skill is, what it is worth, and what it was labelled
jq -r '[.id, .installs, (.domain[0] // "-")] | @tsv' output/skills.jsonl | head

# a skill's source page: what the batches read; the full skill is at the url the catalog names
cat output/skills/mattpocock/skills/grill-me/SKILL.md

# what was written about it, beside it: the label and the Chinese description
cat output/profiles/mattpocock/skills/grill-me/domain.json
cat output/profiles/mattpocock/skills/grill-me/description_zh.json
```

Publish `output/` as it is — the layout is the only contract, the mirror's own files included. The
catalog is a convenience derived from the tree: it goes stale exactly when the tree does, and
`just index` rebuilds it whole.
