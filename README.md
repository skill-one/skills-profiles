# skills-profiles

Domain labels for the [agent skills](https://www.skills.sh) collected by
[skill-one/skills-sh-mirror](https://github.com/skill-one/skills-sh-mirror): one closed-category
label per skill, each a single typed call to the Jev (TypeSafe System One) endpoint built from
that skill's own description and `SKILL.md`.

中文: [README.zh-CN.md](README.zh-CN.md) · Dev guide: [DEVELOPING.md](DEVELOPING.md)

## What it produces

Everything lands under one root, `output/`, and the directory is self-contained: the skills
themselves, the labels written about them, and one catalog joining the two — so nothing here sends
a reader back to the mirror. Publishing is copying that one directory.

```
output/
├── skills/<owner>/<repo>/<slug>/    the mirror's own skill directory, complete and unchanged:
│   ├── SKILL.md                     copy one of these into your skills folder and it is installed
│   └── ...every file the skill ships
├── profiles/<owner>/<repo>/<slug>/
│   └── domain.json                  one label, the endpoint's whole answer
├── skills.jsonl                     `just index`: one flat line per skill — the mirror's own row
│                                    (id, installs, url, hash, fetchedAt) plus description and domain
├── README.md                        ... and the front page beside it: what this directory is, and
├── README.zh-CN.md                  how much of it is built — the first is in English, this Chinese
└── upstream/                        the rest of the mirror: its index, repos, owners, avatars
```

`skills.jsonl` is the way in. It lists every skill the mirror has, in the mirror's own order — the
most installed first — with the `description` read out of that skill's own `SKILL.md`, the `domain`
this project labelled it with, and how sure the endpoint was of it. All three are `null` while they
are unknown, so the labelled part of the dataset is a filter away:

```bash
jq -r 'select(.domain == "development") | [.installs, .id] | @tsv' output/skills.jsonl | head

# the labels the endpoint was least sure of, with the rest of the answer in the profile beside them
jq -r 'select(.confidence < 0.7) | [.confidence, .domain, .id] | @tsv' output/skills.jsonl
```

One directory per skill, one `domain.json`. It is written in full the moment it is generated — so
an interrupted batch loses only the call it was in the middle of, and the next one picks up where
it stopped.

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

## Running it

Needs Python 3.12+, [uv](https://docs.astral.sh/uv/) and [`just`](https://just.systems). Credentials
go in a local `.env` (copy [`.env.example`](.env.example)); the only hosts touched are the mirror
and the one System One endpoint, which is asked typed questions rather than a prompt.

```bash
uv sync
just sync              # fetch the mirror into output/skills and output/upstream
just refresh           # ... and drop the labels whose source changed with it
just                   # label the first skill: a one-skill smoke run
just limit=0           # label every skill still missing one, the whole snapshot, no cap
just limit=20 jobs=8   # eight at a time, for the first 20 skills
just rpm=20            # paced to 20 calls a minute
just dry=1 limit=2     # offline smoke test: fake endpoint, real layout
just index             # rebuild output/skills.jsonl and the READMEs from what is on disk
```

`jobs` bounds how many calls run at once, and `rpm` paces them to what your endpoint allows.
`limit` counts work, not positions: it takes the next skills still unlabelled, in the catalog's own
order (the mirror's: installs descending), so a bounded run does the most installed skills first
and repeated runs walk down the dataset. An output that already exists is never rebuilt — the files
are the whole cache. `just invalidate` (or deleting an output, or `just clean`) is how a label is
regenerated. See [DEVELOPING.md](DEVELOPING.md).

## Consuming it

The catalog says what a skill is; the two directories are the payload. `output/skills/<id>/` is the
skill exactly as the mirror publishes it — complete, so installing one is a copy — and
`output/profiles/<id>/domain.json` is what was written about it. `<id>` is the path under both,
with a `:` or an `&` spelled `_`.

```bash
# what a skill is, what it is worth, and what it was labelled
jq -r '[.id, .installs, (.domain[0] // "-")] | @tsv' output/skills.jsonl | head

# install one: its directory is complete, exactly as the mirror publishes it
cp -r output/skills/mattpocock/skills/grill-me ~/.claude/skills/

# the label written about it, beside it
cat output/profiles/mattpocock/skills/grill-me/domain.json
```

Publish `output/` as it is — the layout is the only contract, the mirror's own files included. The
catalog is a convenience derived from the tree: it goes stale exactly when the tree does, and
`just index` rebuilds it whole.
