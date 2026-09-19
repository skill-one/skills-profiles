# skills-profiles

Chinese multi-angle profiles for the [agent skills](https://www.skills.sh) collected by
[skill-one/skills-sh-mirror](https://github.com/skill-one/skills-sh-mirror): six LLM-written
angles per skill, each one a single turn built from that skill's own description and `SKILL.md`.

中文: [README.zh-CN.md](README.zh-CN.md) · Dev guide: [DEVELOPING.md](DEVELOPING.md)

## What it produces

Everything lands under one root, `output/`, and the directory is self-contained: the skills
themselves, the profiles written about them, and one catalog joining the two — so nothing here sends
a reader back to the mirror. Publishing is copying that one directory.

```
output/
├── skills/<owner>/<repo>/<slug>/    the mirror's own skill directory, complete and unchanged:
│   ├── SKILL.md                     copy one of these into your skills folder and it is installed
│   └── ...every file the skill ships
├── profiles/<owner>/<repo>/<slug>/
│   ├── domain.json  scenario.json  tagline.json
│   ├── blackbox.json  whitebox.json  comments.json
│   └── md/                          the same six angles as markdown, for reading
├── skills.jsonl                     `just index`: one flat line per skill — the mirror's own row
│                                    (id, installs, url, hash, fetchedAt) plus description and domain
└── upstream/                        the rest of the mirror: its index, repos, owners, avatars
```

`skills.jsonl` is the way in. It lists every skill the mirror has, in the mirror's own order — the
most installed first — with the `description` read out of that skill's own `SKILL.md` and the
`domain` and `reason` this project labelled it with. Both are `null` while they are unknown, so the
profiled part of the dataset is a filter away:

```bash
jq -r 'select(.domain == "开发编程") | [.installs, .id] | @tsv' output/skills.jsonl | head
```

One directory per skill, one file per angle. Every json is exactly one prompt's structured output,
written in full the moment it is generated — so an interrupted batch loses only the prompts it was in
the middle of, and the next one picks up where it stopped.

| Prompt     | Shape                                    | Content                                                               |
| ---------- | ---------------------------------------- | --------------------------------------------------------------------- |
| `domain`   | `{domain, reason}`                       | one of the 13 categories below, plus one line of justification         |
| `scenario` | `{text}`                                 | a ≤100-character pitch, built on the user's pain point                 |
| `tagline`  | `{taglines[3]}`                          | three slogans, ≤20 characters each                                     |
| `blackbox` | `{function, input_output[3–5]}`          | outside view: what you hand it → what you get back, no internals       |
| `whitebox` | `{execution_flow[3–5], mechanisms[2–3]}` | inside view: happy path, key mechanisms, real dependencies             |
| `comments` | `{comments[4–6]}`                        | first-person user notes; `category` typically 妙用 / 坑 / 注意 / 启发 |

`{...[n–m]}` is an array of that many entries; `input_output` items are `{input, output}` and
`comments` items `{user, category, comment}`. Everything but ids, paths and field names is
Chinese.

`domain.domain` is a closed enum, so it is directly filterable: 开发编程 · 测试与质量 · 数据分析 ·
运维与安全 · 办公效率 · 内容创作 · 设计多媒体 · 知识管理 · 商业运营 · 支付金融 · 教育学习 · 生活服务 · 其他.

## Running it

Needs Python 3.12+, [uv](https://docs.astral.sh/uv/) and [`just`](https://just.systems). Credentials
go in a local `.env` (copy [`.env.example`](.env.example)); the only hosts touched are the mirror
and your own model endpoint.

```bash
uv sync
just sync              # fetch the mirror into output/skills and output/upstream
just refresh           # ... and drop the profiles whose source changed with it
just                   # build the first skill: a one-skill smoke run
just limit=0           # build every profile still missing, the whole snapshot, no cap
just prompt=scenario   # only that angle, for every skill in the window
just limit=20 jobs=8   # eight at a time, for the first 20 skills
just dry=1 limit=2     # offline smoke test: fake model, real layout
just index             # rebuild output/skills.jsonl from what is on disk
```

`jobs` bounds how many generations run at once, and `rpm` paces them to what your endpoint allows
(`just rpm=20` for a free tier that documents 20 requests a minute). `limit` counts work, not
positions: it takes the next skills that still need something, in the catalog's own order (which is
the mirror's: installs descending), so a bounded run does the most installed skills first and
repeated runs walk down the dataset instead of redoing the top of it.
An output that already exists
is never rebuilt — the files are the whole cache. `just invalidate <prompt>` (or deleting an
output, or `just clean`) is how a prompt is regenerated. See [DEVELOPING.md](DEVELOPING.md).

## Consuming it

The catalog says what a skill is; the two directories are the payload. `output/skills/<id>/` is the
skill exactly as the mirror publishes it — complete, so installing one is a copy — and
`output/profiles/<id>/` is what was written about it. `<id>` is the path under both, with a `:` or an
`&` spelled `_` (two skills of the current snapshot):

```bash
# what a skill is, what it is worth, and what it was labelled
jq -r '[.id, .installs, (.domain // "-")] | @tsv' output/skills.jsonl | head

# install one: its directory is complete, exactly as the mirror publishes it
cp -r output/skills/mattpocock/skills/grill-me ~/.claude/skills/

# the profiles written about it, beside it
cat output/profiles/mattpocock/skills/grill-me/domain.json
```

Publish `output/` as it is — the layout is the only contract, the mirror's own files included. The
catalog is a convenience derived from the tree: it goes stale exactly when the tree does, and
`just index` rebuilds it whole.
