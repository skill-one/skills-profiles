# skills-profiles

为 [skill-one/skills-sh-mirror](https://github.com/skill-one/skills-sh-mirror) 收录的
[agent skills](https://www.skills.sh) 生成多角度中文档案：每个 skill 六份由 LLM 写出的档案，
每份都是一次单轮调用，依据该 skill 的 `SKILL.md` 写成。

English: [README.md](README.md) · 开发指南：[DEVELOPING.zh-CN.md](DEVELOPING.zh-CN.md)

## 产物是什么

所有东西都落在一个根目录 `output/` 下：档案、放在它们旁边的索引，以及这些档案所依据的快照——所以
发布就是复制这一个目录。

```
output/
├── skills/<owner>/<repo>/<slug>/
│   ├── domain.json  scenario.json  blackbox.json  whitebox.json
│   ├── tagline.json comments.json
│   └── md/                    同样六个角度的 markdown 版，方便阅读
├── skills.jsonl               `just index`：每个 skill 一行——id、domain、reason
└── cache/skills-sh/           这些档案所依据的上游快照
```

索引由这棵树派生——`just index` 会把整个文件重写一遍，还没生成 domain 的 skill 不占行——树始终是
唯一的契约。

每个 skill 一个目录，目录名就是它的 id（`{owner}/{repo}/{slug}`，其中的 `:` 改写为 `_`）。
每个 json 恰好是一个 prompt 的结构化输出，生成完即完整落盘——所以批次被中断只会丢掉它正在
处理的那几个 prompt，下一批会从断点继续。

| Prompt     | 结构                                     | 内容                                                        |
| ---------- | ---------------------------------------- | ----------------------------------------------------------- |
| `domain`   | `{domain, reason}`                       | 下面 13 个分类之一 + 一句话理由                             |
| `scenario` | `{text}`                                 | 一段 100 字以内的场景化介绍，从用户痛点切入                 |
| `tagline`  | `{taglines[3]}`                          | 3 条宣传短标语，每条 20 字以内                              |
| `blackbox` | `{function, input_output[3–5]}`          | 黑盒视角：你给什么 → 你得到什么，不谈内部实现               |
| `whitebox` | `{execution_flow[3–5], mechanisms[2–3]}` | 白盒视角：主路径流程、关键机制、真实依赖                    |
| `comments` | `{comments[4–6]}`                        | 用户第一人称评论；`category` 通常为 妙用 / 坑 / 注意 / 启发 |

`{...[n–m]}` 表示长度为 n~m 的数组；`input_output` 的元素是 `{input, output}`，`comments`
的元素是 `{user, category, comment}`。除 id、路径和字段名外，全部是中文。

`domain.domain` 是闭合枚举，可以直接筛：开发编程 · 测试与质量 · 数据分析 · 运维与安全 · 办公效率 ·
内容创作 · 设计多媒体 · 知识管理 · 商业运营 · 支付金融 · 教育学习 · 生活服务 · 其他。

## 怎么跑

需要 Python 3.12+、[uv](https://docs.astral.sh/uv/) 和 [`just`](https://just.systems)。凭据放在
本地 `.env`（复制 [`.env.example`](.env.example)）；只会访问镜像和你自己的模型端点。

```bash
uv sync
just sync              # 把快照下载到 output/cache/skills-sh（整个 dist 分支）
just refresh           # ……并删掉来源随之变了的那些档案
just                   # 只做第一个 skill：一次单 skill 冒烟
just limit=0           # 生成所有还缺的档案：整份快照，无上限
just prompt=scenario   # 只做这一个角度，窗口内每个 skill 都要
just limit=20 jobs=8   # 同时跑 8 个，只做前 20 个 skill
just dry=1 limit=2     # 离线冒烟：假模型、真布局
just index             # 把已生成的 domain 折成 output/skills.jsonl
```

`jobs` 决定同时跑多少个生成，`rpm` 把它们配速到端点允许的节奏（写着每分钟 20 次的免费档就用
`just rpm=20`）。`limit` 按快照自带的索引往下数——`skills.jsonl` 是安装量降序——所以有限的窗口先做
安装量最高的 skill，而不是字母表最前面的那些。已存在的输出永远不会被重建——文件本身就是全部的缓存。
`just invalidate <prompt>`
（或删掉某个输出、或 `just clean`）就是「失效」的全部含义。细节见
[DEVELOPING.zh-CN.md](DEVELOPING.zh-CN.md)。

## 怎么用这份数据

目录树就是 API。关联键是 skill id——与镜像、与 `https://www.skills.sh/<id>` 完全一致的
`{owner}/{repo}/{slug}`——所以直接按路径取你要的角度：

```bash
# 从一棵产物树里取出每个 skill 的分类
for d in output/skills/*/*/*/; do
  printf '%s\t%s\n' "${d#output/skills/}" "$(jq -r .domain "$d/domain.json")"
done
```

`just index` 把同一个角度折进 `output/skills.jsonl`，每个已生成它的 skill 一行：

```bash
jq -r '[.id, .domain] | @tsv' output/skills.jsonl
```

发布时请把这整个 `output/` 原样保留——布局是唯一的契约，快照也在里面。索引只是从树派生出来的
便利：树一陈旧它也就陈旧，而 `just index` 会把整个文件重写一遍。
