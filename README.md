# skills-profiles

Domain labels and Chinese translations for the [agent skills](https://www.skills.sh) collected by
[skill-one/skills-sh-mirror](https://github.com/skill-one/skills-sh-mirror): one closed-category
label per skill, each a single typed call to the Jev (TypeSafe System One) endpoint built from
that skill's own description and `SKILL.md`, and OpenAI-compatible chat calls - one translating
that description into Chinese, then one per markdown piece of the `SKILL.md` body, the pieces
rejoined into a Chinese page of its own.

中文: [README.zh-CN.md](README.zh-CN.md) · Dev guide: [DEVELOPING.md](DEVELOPING.md)

## What it produces

Everything lands under one root, `output/`: the source pages the angles were built from, what is
written about them — a label and Chinese translations — and one catalog joining it all, so nothing
here sends a reader back to the mirror. Publishing is copying that one directory. Beside the
skills, `repos.jsonl` holds one row per repository and `owners/<owner>.png` one avatar per owner —
keyed by the `owner/repo` a skill id leads with.

```
output/
├── skills/<owner>/<repo>/<slug>/    one directory per skill — it installs as the skill itself,
│   ├── SKILL.md                     with its annotations riding along: the source page, fetched
│   │                                from the skill's own repository
│   ├── domain.json                  one label, the typed endpoint's whole answer
│   └── SKILL.zh.md                  the page in Chinese; its front matter carries the Chinese
│                                    description
├── repos.jsonl                      one row per repository: description, stars, last-update time
│                                    and link, `gone` where GitHub has none
├── owners/<owner>.png               one owner's avatar - the fixed file a frontend builds unaided
├── skills.jsonl                     the catalog: one flat line per skill the mirror lists — its
│                                    own row (id, installs) plus description, description_zh and
│                                    domain, each null until the skill is fetched and built
└── README.md                        ... and the front page beside it: what this directory is, and
    README.zh-CN.md                  how much of it is built — the first is in English, this Chinese
```

`skills.jsonl` is the way in. It lists every skill the mirror has that the tree can still build, in
the mirror's own order, the
most installed first, with the `description` read out of that skill's own `SKILL.md`, its
`description_zh`, the `domain` this project labelled it with, and how sure the endpoint was of it.
The joined fields are `null` until the skill is fetched and built — which is also how a batch knows
what is left; a skill whose repository yielded nothing is no row at all — so the labelled part of
the dataset is a filter away:

```bash
jq -r 'select(.domain == "development") | [.installs, .id] | @tsv' output/skills.jsonl | head

# the labels the endpoint was least sure of, with the rest of the answer in the profile beside them
jq -r 'select(.confidence != null and .confidence < 0.7) | [.confidence, .domain, .id] | @tsv' \
  output/skills.jsonl
```

One directory per skill, two generated files: `domain.json` and `SKILL.zh.md`. Each is written in
full the moment it is generated — so an interrupted batch loses only the call it was in the middle
of, and the next one picks up where it stopped. The two angles are independent: each is built and
rebuilt on its own.

`domain.json` is `{domain, confidence, probabilities}`: one of the 13 English categories below, the
endpoint's confidence in it, and the distribution it was read off. Everything is English.

`domain` is one member of the closed enum, so it is directly filterable:
development · testing · data-analysis · devops-security · office-productivity · content-creation ·
design-media · knowledge-management · business-ops · finance-payment · education · lifestyle ·
other. Beside it, `confidence` is how sure the endpoint said it was about the choice — not the
probability of the label being right, but the number to sort on when you want to find the labels
worth a second look (and `null` where the endpoint did not say).

The profile keeps the whole answer, `probabilities` included, because the winner does not contain
it: a call decided 0.52 to 0.48 says something a call decided 0.99 to 0.01 does not. The catalog
carries the label and the confidence and stops there:

```bash
# one label was chosen; what the endpoint nearly chose instead is in the same file
jq '{domain, confidence, second: (.probabilities | to_entries | sort_by(-.value) | .[1])}' \
  output/skills/mattpocock/skills/grill-me/domain.json
```

`SKILL.zh.md` is the page in Chinese, assembled by code: a front matter carrying the one-line
description rendered in Chinese — product names and code kept as written, Chinese left unchanged —
over the translated body. The model never shapes the front matter, so the description is always
machine-readable back out of it. A chat endpoint has no closed enum, so there is no confidence and
no distribution — the string is the whole answer.

## Running it

Needs Python 3.12+, [uv](https://docs.astral.sh/uv/) and [`just`](https://just.systems). Credentials
go in a local `.env` (copy [`.env.example`](.env.example)); the hosts touched are the mirror, the
System One endpoint (asked typed questions rather than a prompt) and the OpenAI-compatible chat
endpoint that does the translations.

```bash
uv sync
just sync                       # reconcile with the mirror: its listing, new sources, the catalog
just                            # build the first domain label: a one-skill smoke, fetches its repo
just build domain               # the same thing, named
just limit=0 build domain       # build every missing label, the whole snapshot, no cap
just limit=20 jobs=8 build domain   # eight at a time, the first 20 skills (default pool: 32)
just dry=1 limit=2 build domain     # fake endpoint, real layout
just build all                  # both angles in one pool, over the shared window
just build skill_zh             # the second angle: build the first missing SKILL.zh.md
just limit=0 build skill_zh     # build every zh page, same limit/jobs/dry knobs
just clean domain               # the inverse: forget the first built label
just limit=0 clean all          # forget every built output of both angles
just meta                       # fetch each repository's GitHub profile and each owner's avatar
just index                      # rebuild output/skills.jsonl and the READMEs from what is on disk
```

`build` and `clean` are inverse windows over the same catalog order: `build` takes the next
`limit` skills missing an angle's file, `clean` the next `limit` that have one, so cleaning and
building regenerates exactly the cleaned skills (`limit 0` means no cap).

`jobs` bounds how many calls run at once (32 by default); a transient 429 is left to the client's
own retry, there is no per-minute pacing.

A skill's repository is fetched the first time one of its skills is built and never again — the
repository directory on disk is the cache — so a bounded run downloads only the repositories its
window actually needs, not the whole dataset. `just sync` fetches again any repository the mirror
has since added a skill to.

`limit` counts work, not positions: it takes the next skills still missing the angle being built,
in the catalog's own order (the mirror's: installs descending), so a bounded run does the most
installed skills first and repeated runs walk down the dataset. An output that already exists is
never rebuilt — the files are the whole cache. `just clean <angle>` (or deleting an output) is
how an angle is regenerated; a full reset keeping the sources is `just limit=0 clean all` then
`just sync`.
See [DEVELOPING.md](DEVELOPING.md).

## Consuming it

The catalog says what a skill is; the skill directories are the payload. `output/skills/<id>/`
holds the source page with what was written beside it: `domain.json` and the Chinese page
`SKILL.zh.md`. `<id>` is the path under `skills/`, with a `:` or an `&` spelled `_`. The directory
installs as the skill itself — though a skill ships more than its `SKILL.md` (scripts, references,
assets), and the whole of it lives in its own repository.

```bash
# what a skill is, what it is worth, and what it was labelled
jq -r '[.id, .installs, (.domain // "-")] | @tsv' output/skills.jsonl | head

# a skill's source page: what the batches read; the full skill is at its own repository
cat output/skills/mattpocock/skills/grill-me/SKILL.md

# what was written about it, beside it: the label and the Chinese page
cat output/skills/mattpocock/skills/grill-me/domain.json
cat output/skills/mattpocock/skills/grill-me/SKILL.zh.md
```

Publish `output/` as it is — the layout is the only contract. The
catalog is a convenience derived from the tree: it goes stale exactly when the tree does, and
`just index` rebuilds it whole.
