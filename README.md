# skills-profiles

Chinese multi-angle profiles for the [agent skills](https://www.skills.sh) collected by
[skill-one/skills-sh-mirror](https://github.com/skill-one/skills-sh-mirror): a queryable index,
seven LLM-written angles per skill, and one rendered tool-avatar cover, generated from its
`SKILL.md` and published as self-contained snapshots.

中文: [README.zh-CN.md](README.zh-CN.md) · Dev guide: [DEVELOPING.md](DEVELOPING.md)

## What the data is

```
├── latest         the newest publish's tag, one line — read it to pin a version
├── skills.jsonl   one row per profiled skill, sorted by id — filter / join / rank here
├── stats.json     how complete the artifacts are, plus publishedAt and the upstream mirror tag
└── skills/        one directory per skill, named after its id
    └── vercel-labs/skills/find-skills/   ({owner}/{repo}/{slug})
        ├── domain.json  scenario.json  blackbox.json  whitebox.json
        ├── tagline.json persona.json   comments.json
        ├── cover.png    the persona tool's rendered avatar (only where one exists)
        └── md/          the seven angles rendered as markdown, for reading
```

One `skills.jsonl` row (real data):

```json
{
  "id": "vercel-labs/skills/find-skills",
  "hash": "b146008599c31057cef1c145774cea5d5afb30e8f43fa802e47a4b461419aaaf",
  "domain": {
    "domain": "开发编程",
    "reason": "面向开发者的技能包检索与安装工具, 属于 agent 开发工具链生态"
  },
  "persona": {
    "tool": "磁铁",
    "pitch": "我按需求找到能干活的技能, 直接给你装好——我是一块磁铁"
  }
}
```

| Field     | Meaning                                                                                         |
| --------- | ----------------------------------------------------------------------------------------------- |
| `id`      | the skills.sh skill id, `{owner}/{repo}/{slug}` — identical to the mirror's ids                 |
| `hash`    | SHA-256 of the skill's files, as recorded upstream: the profile describes exactly this content  |
| `domain`  | `domain`: one of the 13 categories below; `reason`: one line of justification                   |
| `persona` | the skill personified as one real-world physical tool — its `tool`, plus a first-person `pitch` |

`domain.domain` is a closed enum, so it is directly filterable: 开发编程 · 测试与质量 · 数据分析 ·
运维与安全 · 办公效率 · 内容创作 · 设计多媒体 · 知识管理 · 商业运营 · 支付金融 · 教育学习 · 生活服务 · 其他.

The index folds in only the two angles you filter on; all seven are per-skill files, each with its own
schema:

| Prompt     | Shape                                    | Content                                                               |
| ---------- | ---------------------------------------- | --------------------------------------------------------------------- |
| `domain`   | `{domain, reason}`                       | category + why — also in the index                                    |
| `persona`  | `{tool, pitch}`                          | physical-tool persona — also in the index                             |
| `scenario` | `{text}`                                 | one ≤100-character pitch, built on the user's pain point              |
| `tagline`  | `{taglines[3]}`                          | three slogans, ≤20 characters each                                    |
| `blackbox` | `{function, input_output[3–5]}`          | outside view: what you hand it → what you get back, no internals      |
| `whitebox` | `{execution_flow[3–5], mechanisms[2–3]}` | inside view: happy path, key mechanisms, real dependencies            |
| `comments` | `{comments[4–6]}`                        | first-person user notes; `category` typically 妙用 / 坑 / 注意 / 启发 |

`{...[n–m]}` = an array of that many entries; `input_output` items are `{input, output}`, `comments`
items `{user, category, comment}`. Everything but ids, paths and field names is Chinese.

`stats.json` says how complete the artifacts are, and which snapshot they are:

```json
{
  "covers": { "rendered": 999 },
  "prompts": {
    "blackbox": 1000,
    "comments": 1000,
    "domain": 1000,
    "persona": 1000,
    "scenario": 1000,
    "tagline": 1000,
    "whitebox": 1000
  },
  "publishedAt": "2026-09-13T01:02:03Z",
  "skills": { "profiled": 1000, "complete": 999, "total": 1000 },
  "upstream": "dist-2026-09-12"
}
```

- `prompts` counts the cached outputs of each angle; `covers.rendered` counts the pictures rendered
  directly from `persona.tool`. Treat `cover.png` (~200 KB after the automatic palette-quantization)
  as present-or-absent per skill.
- `skills.profiled` counts skills with every angle cached (the text half); `skills.complete` the subset
  whose `cover.png` is drawn too — the sense `run --limit` spends budget on, so a key-less run can
  reach `profiled == total` with `complete` still catching up.
- `skills.total` is the pipeline's capped window — the most installed `SKILLS_PROFILES_TOTAL_LIMIT`
  skills (default 1000), never every upstream one. The counters are rewritten on every `generate`
  publish, so count `skills.jsonl` lines when an exact number matters.
- `publishedAt` (when the snapshot was published) and `upstream` (the mirror tag its dataset came from)
  are stamped by the publish step rather than written by the pipeline, so they can never lag the data:
  compare `publishedAt` to tell two snapshots apart, join on `upstream` to match hashes. Locally,
  before anything is published, the file carries neither.

Three guarantees the layout enforces: the index is a projection re-derived from disk (a row exists iff
its directory does, and its `domain` / `persona` always match that directory's json); `hash` is the
content the profiles were generated from, so when upstream rewrites a skill its profiles are dropped
rather than left describing another version; and `latest` names the snapshot while `stats.json` stamps
when it was published and from which mirror tag, because publishing fails unless pointer, tag and
commit agree — or a published snapshot turns out to have lost its stamp.

There is no image-recipe prompt: `cover.png` is rendered straight from the persona's tool name
(`persona.tool`, a Chinese physical-tool name), with the avatar framing and the unified premium 3D
illustration style appended by the generator. Invalidate `persona` to re-draw a cover — the picture
is its asset, so json and png are refilled together; re-rendering costs no extra text call.
Full detail: [DEVELOPING.md](DEVELOPING.md).

## How to get the data

The [`dist` branch](../../tree/dist) root _is_ the snapshot: the rolling branch is the newest state,
`sync` tags `dist-YYYY-MM-DD` (force-updated within the day) and `generate` appends an immutable
`dist-YYYY-MM-DD-N` per batch. One pointer names the version — the root `latest`, the shape the mirror
publishes too — while `stats.json` carries the rest of its identity: when it was published and which
mirror tag its dataset came from. Text profiles are under 1 MB compressed; `dist` also carries the
internal `cache/skills-sh/` dataset mirror CI restores (~120 MB of text, included in a full clone, not
part of this API).

```bash
BASE=https://raw.githubusercontent.com/skill-one/skills-profiles
latest=$(curl -s $BASE/dist/latest)   # one line, e.g. dist-2026-09-09-12

curl -sO $BASE/dist/skills.jsonl                    # newest: the rolling branch
curl -sO $BASE/$latest/skills.jsonl                 # pinned: a tag never changes
curl -s $BASE/$latest/skills/vercel-labs/skills/find-skills/md/persona.md   # any file, by path
```

GitHub caches the branch for ~5 minutes (the worst case) and a tag forever, so read the pointer and
fetch again only when it names a tag you do not have. The index is small (≈130 KB) and jq is enough to
filter it: `jq -r 'select(.domain.domain == "设计多媒体") | [.id, .persona.tool] | @tsv'`. The whole
snapshot is one request — `git clone --depth 1 -b "$latest"
https://github.com/skill-one/skills-profiles.git`, or the same tree as a tarball from
`codeload.github.com/skill-one/skills-profiles/tar.gz/$latest` — and tags are pruned to a rolling month.

### Join with the mirror

Installs, stars, descriptions and the `SKILL.md` sources are in
[skills-sh-mirror](https://github.com/skill-one/skills-sh-mirror); `id` joins the rows, `hash` proves
the content matches. Read the mirror tag off the stamped `stats.json` for an exact hash join:

```bash
BASE=https://raw.githubusercontent.com/skill-one/skills-profiles
up=$(curl -s $BASE/dist/stats.json | jq -r .upstream)   # e.g. dist-2026-09-12
curl -s "https://raw.githubusercontent.com/skill-one/skills-sh-mirror/$up/skills.jsonl" -o up.jsonl
curl -s $BASE/dist/skills.jsonl -o mine.jsonl

# id  installs  category  tool
jq -r --slurpfile up up.jsonl '($up | map({(.id): .installs}) | add) as $i | [.id, $i[.id], .domain.domain, .persona.tool] | @tsv' mine.jsonl
```

The same `id` also resolves to the skill's skills.sh page (`https://www.skills.sh/<id>`); profiles come
from this repository's `sync` and `generate` workflows (`gh workflow run generate.yml -f limit=50`).
