# skills-profiles

Chinese multi-angle profiles for the [agent skills](https://www.skills.sh) collected by
[skill-one/skills-sh-mirror](https://github.com/skill-one/skills-sh-mirror): six LLM-written
angles per skill, each one a single turn built from that skill's `SKILL.md`.

中文: [README.zh-CN.md](README.zh-CN.md) · Dev guide: [DEVELOPING.md](DEVELOPING.md)

## What it produces

Everything lands under one root, `output/`: the profiles, the index beside them, and the snapshot
they were built from — so publishing is copying that one directory.

```
output/
├── skills/<owner>/<repo>/<slug>/
│   ├── domain.json  scenario.json  blackbox.json  whitebox.json
│   ├── tagline.json comments.json
│   └── md/                     the same six angles as markdown, for reading
├── skills.jsonl                `just index`: one flat line per skill — id, domain, reason
└── cache/skills-sh/            the upstream snapshot those profiles were built from
```

The index is derived from the tree — `just index` rewrites it whole, and no line appears while a
skill's domain is missing — and the tree stays the only contract.

One directory per skill, named after its id (`{owner}/{repo}/{slug}`, any `:` rewritten to
`_`). Every json is exactly one prompt's structured output, written in full the moment it is
generated — so an interrupted batch loses only the prompts it was in the middle of, and the
next one picks up where it stopped.

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
just sync              # download the snapshot into output/cache/skills-sh (the dist branch)
just refresh           # ... and drop the profiles whose source changed with it
just                   # build the first skill: a one-skill smoke run
just limit=0           # build every profile still missing, the whole snapshot, no cap
just prompt=scenario   # only that angle, for every skill in the window
just limit=20 jobs=8   # eight at a time, for the first 20 skills
just dry=1 limit=2     # offline smoke test: fake model, real layout
just index             # fold the domains built so far into output/skills.jsonl
```

`jobs` bounds how many generations run at once, and `rpm` paces them to what your endpoint allows
(`just rpm=20` for a free tier that documents 20 requests a minute). `limit` counts down the
snapshot's own index — `skills.jsonl`, installs descending — so a bounded run does the most
installed skills first rather than the alphabetically first. An output that already exists
is never rebuilt — the files are the whole cache. `just invalidate <prompt>` (or deleting an
output, or `just clean`) is how a prompt is regenerated. See [DEVELOPING.md](DEVELOPING.md).

## Consuming it

The directory tree is the API. The join key is the skill id — the same `{owner}/{repo}/{slug}`
the mirror and `https://www.skills.sh/<id>` use — so read the angles you want straight off the
path:

```bash
# every skill's category, from a checkout of the tree
for d in output/skills/*/*/*/; do
  printf '%s\t%s\n' "${d#output/skills/}" "$(jq -r .domain "$d/domain.json")"
done
```

`just index` folds that same angle into `output/skills.jsonl`, one line per skill that has one:

```bash
jq -r '[.id, .domain] | @tsv' output/skills.jsonl
```

Publish `output/` as it is — the layout is the only contract, snapshot included. The index is a
convenience derived from the tree: it goes stale exactly when the tree does, and `just index`
rebuilds it whole.
