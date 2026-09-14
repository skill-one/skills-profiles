# skills-profiles

为 [skill-one/skills-sh-mirror](https://github.com/skill-one/skills-sh-mirror) 收录的
[agent skills](https://www.skills.sh) 生成的多角度中文档案：一个可查询的索引，加上每个 skill 七份
由 LLM 依据它的 `SKILL.md` 写出的档案，以及一张直接渲染的工具头像配图，按自包含的快照发布。

English: [README.md](README.md) · 开发指南：[DEVELOPING.zh-CN.md](DEVELOPING.zh-CN.md)

## 数据是什么

```
├── latest         最新一次发布的 tag，一行——读它即可钉住版本
├── skills.jsonl   每个已生成档案的 skill 一行，按 id 排序——筛选 / 关联 / 排行都从这里开始
├── stats.json     产物有多完整，外加盖章写入的 publishedAt 与 upstream（来自镜像的哪个 tag）
└── skills/        每个 skill 一个目录，目录名就是它的 id
    └── vercel-labs/skills/find-skills/   ({owner}/{repo}/{slug})
        ├── domain.json  scenario.json  blackbox.json  whitebox.json
        ├── tagline.json persona.json   comments.json
        ├── cover.png    persona 工具的头像配图（只有已经画过的 skill 才有）
        └── md/          七份档案的 markdown 版，方便阅读
```

`skills.jsonl` 的一行（真实数据）：

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

| 字段      | 含义                                                                         |
| --------- | ---------------------------------------------------------------------------- |
| `id`      | skills.sh 的 skill id，`{owner}/{repo}/{slug}`——与镜像的 id 完全一致         |
| `hash`    | 上游记录的技能文件 SHA-256：档案描述的就是这一份内容                         |
| `domain`  | `domain`：下面 13 个分类之一；`reason`：一句话理由                           |
| `persona` | 把 skill 拟人化成一件现实物理工具——`tool` 物理工具、`pitch` 第一人称自我介绍 |

`domain.domain` 是闭合枚举，可以直接筛：开发编程 · 测试与质量 · 数据分析 · 运维与安全 · 办公效率 ·
内容创作 · 设计多媒体 · 知识管理 · 商业运营 · 支付金融 · 教育学习 · 生活服务 · 其他。

索引只折入你会拿去筛选的那两个角度；七个角度本身都是每个 skill 目录下的文件，各有各的结构：

| Prompt     | 结构                                     | 内容                                                        |
| ---------- | ---------------------------------------- | ----------------------------------------------------------- |
| `domain`   | `{domain, reason}`                       | 分类 + 理由——同时进索引                                     |
| `persona`  | `{tool, pitch}`                          | 物理工具拟人画像——同时进索引                                |
| `scenario` | `{text}`                                 | 一段 100 字以内的场景化介绍，从用户痛点切入                 |
| `tagline`  | `{taglines[3]}`                          | 3 条宣传短标语，每条 20 字以内                              |
| `blackbox` | `{function, input_output[3–5]}`          | 黑盒视角：你给什么 → 你得到什么，不谈内部实现               |
| `whitebox` | `{execution_flow[3–5], mechanisms[2–3]}` | 白盒视角：主路径流程、关键机制、真实依赖                    |
| `comments` | `{comments[4–6]}`                        | 用户第一人称评论；`category` 通常为 妙用 / 坑 / 注意 / 启发 |

`{...[n–m]}` 表示长度为 n~m 的数组；`input_output` 的元素是 `{input, output}`，`comments` 的元素是
`{user, category, comment}`。除 id、路径和字段名外，全部是中文。

`stats.json` 说明产物有多完整，以及它们是哪一份快照：

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

- `prompts` 数的是每个角度已缓存的输出数；`covers.rendered` 数的是直接据 `persona.tool`
  渲染出的配图数。把 `cover.png`（自动调色板量化后约 200 KB）当作每个 skill 上「有则有、无则无」的东西。
- `skills.profiled` 数的是每个角度都已缓存的 skill（文字那一半）；`skills.complete` 是其子集，要求
  `cover.png` 也已画出——也就是 `run --limit` 会占用预算的那个口径，所以没有配图 key 的一轮可以让
  `profiled == total` 而 `complete` 仍在追赶。
- `skills.total` 是整条管道刻意设了封顶的窗口：安装量最高的至多 `SKILLS_PROFILES_TOTAL_LIMIT` 个
  skill（默认 1000），而非上游全量。计数在每轮 `generate` 发布时重写，要精确数字就数 `skills.jsonl`
  的行数。
- `publishedAt`（这份快照何时发布）与 `upstream`（它随包的数据集来自镜像的哪个 tag）由发布环节盖章写
  入，而不是由管道抄写，所以二者都不可能滞后于数据：比 `publishedAt` 判断两份快照是否不同，按
  `upstream` 对齐 hash。本地尚未发布时，文件里这两个键都不存在。

三条由结构本身保证的性质：索引是每个 skill 目录的投影、每次重写都从磁盘重新推导（行存在当且仅当目录
存在，且行里的 `domain` / `persona` 必然与该目录的 json 一致）；`hash` 就是生成档案时依据的那份内容，
所以上游改写某个 skill 后它的档案会被丢弃，而不是继续描述另一个版本；`latest` 指明是哪一份快照，
`stats.json` 则盖章写明它何时发布、基于哪一版镜像，因为指针、tag、commit 三者不一致，或已发布的快照
丢了章，发布都算失败。

不存在「配图配方」这一步：`cover.png` 直接拿 persona 的工具名（`persona.tool`，一个中文物理工具
名）做主体，头像级取景和统一的高级 3D 插画画风由生成器追加。要重画配图就 invalidate `persona`
——配图是 persona 的资产，json 和 png 会一起重建；重渲染不产生额外的文本调用。细节见
[DEVELOPING.zh-CN.md](DEVELOPING.zh-CN.md)。

## 如何获取数据

[`dist` 分支](../../tree/dist)的根目录**就是**快照：滚动分支是最新状态，`sync` 打 `dist-YYYY-MM-DD`
（同日内 force 覆盖），`generate` 每批追加一个不可变的 `dist-YYYY-MM-DD-N`。钉版本只需一个指针——根目录
的 `latest`（镜像也发布同样形状的一行），快照身份的其余部分则由 `stats.json` 带出：它何时发布、数据集来自
镜像的哪个 tag。文字档案压缩后不到 1 MB；`dist` 还附带内部 `cache/skills-sh/`
数据集镜像供 CI 恢复（约 120 MB 文本，整包克隆会带上，不属于档案 API）。

```bash
BASE=https://raw.githubusercontent.com/skill-one/skills-profiles
latest=$(curl -s $BASE/dist/latest)   # 一行，例如 dist-2026-09-09-12

curl -sO $BASE/dist/skills.jsonl                    # 最新：滚动分支
curl -sO $BASE/$latest/skills.jsonl                 # 钉住：tag 内容永不变化
curl -s $BASE/$latest/skills/vercel-labs/skills/find-skills/md/persona.md   # 任意文件，按路径取
```

GitHub 对分支有约 5 分钟缓存（最坏延迟）、对 tag 则永久缓存，所以只要读指针，当它指向一个你还没有的
tag 时才重新拉取。索引很小（约 130 KB），筛选用 jq 就够：
`jq -r 'select(.domain.domain == "设计多媒体") | [.id, .persona.tool] | @tsv'`。整份快照只需一个请求
——`git clone --depth 1 -b "$latest" https://github.com/skill-one/skills-profiles.git`，或从
`codeload.github.com/skill-one/skills-profiles/tar.gz/$latest` 取同一棵树的 tarball——tag 按滚动一个月
剪枝。

### 与镜像数据关联

安装量、stars、简介和 `SKILL.md` 原文在
[skills-sh-mirror](https://github.com/skill-one/skills-sh-mirror)；用 `id` 关联行，用 `hash` 确认内容
一致。若也要按 hash 对齐，就从盖好章的 `stats.json` 取镜像 tag：

```bash
BASE=https://raw.githubusercontent.com/skill-one/skills-profiles
up=$(curl -s $BASE/dist/stats.json | jq -r .upstream)   # 例如 dist-2026-09-12
curl -s "https://raw.githubusercontent.com/skill-one/skills-sh-mirror/$up/skills.jsonl" -o up.jsonl
curl -s $BASE/dist/skills.jsonl -o mine.jsonl

# id  installs  category  tool
jq -r --slurpfile up up.jsonl '($up | map({(.id): .installs}) | add) as $i | [.id, $i[.id], .domain.domain, .persona.tool] | @tsv' mine.jsonl
```

同一个 `id` 还能定位到它的 skills.sh 页面（`https://www.skills.sh/<id>`）；档案由本仓库的 `sync` 与
`generate` 两条工作流生成（`gh workflow run generate.yml -f limit=50`）。
