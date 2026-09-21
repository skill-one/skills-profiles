# skills-profiles

为 [skill-one/skills-sh-mirror](https://github.com/skill-one/skills-sh-mirror) 收录的
[agent skills](https://www.skills.sh) 生成多角度中文档案：每个 skill 六份由模型写出的档案，
每份都是一次调用，依据该 skill 自己的 description 与 `SKILL.md` 写成。

English: [README.md](README.md) · 开发指南：[DEVELOPING.zh-CN.md](DEVELOPING.zh-CN.md)

## 产物是什么

所有东西都落在一个根目录 `output/` 下，而且这个目录是自足的：skill 本身、围绕它写出的中文档案，以及
把两者连起来的一份清单——这里的任何一处都不会把读者送回镜像。发布就是复制这一个目录。

```
output/
├── skills/<owner>/<repo>/<slug>/    镜像自己的 skill 目录，完整且未改动：
│   ├── SKILL.md                     把它拷进你的 skills 目录就等于装好了
│   └── ...该 skill 随附的一切
├── profiles/<owner>/<repo>/<slug>/
│   ├── domain.json  scenario.json  tagline.json
│   ├── blackbox.json  whitebox.json  comments.json
│   └── md/                          同样六个角度的 markdown 版，方便阅读
├── skills.jsonl                     `just index`：每个 skill 一行——镜像那一行（id、installs、
│                                    url、hash、fetchedAt）再加上 description 与 domain
├── README.md                        …… 以及它旁边的首页：这个目录是什么、建到了什么程度
├── README.zh-CN.md                  同一页的中文版
└── upstream/                        镜像的其余部分：索引、repos、owners、avatars
```

`skills.jsonl` 是入口。它列出镜像持有的每一个 skill，顺序就是镜像自己的顺序（安装量降序），
`description` 读自该 skill 自己的 `SKILL.md`，`domain` 是本项目为它标定的，外加端点当时的置信度。
三者在未知时都是 `null`，所以「已经做完的那部分数据集」只差一次筛选：

```bash
jq -r 'select(.domain == "development") | [.installs, .id] | @tsv' output/skills.jsonl | head

# 端点最没把握的那些标签，完整答案就在旁边的档案里
jq -r 'select(.confidence < 0.7) | [.confidence, .domain, .id] | @tsv' output/skills.jsonl
```

旁边的两份 README 是发布根的首页，也是尽可能短地把这棵树说成进度：先说明哪两个目录分别是 skill 与
为它写的内容，再逐角度给出有多少 skill 有了它、这覆盖了镜像安装量的多大比例，附上这些数字所描述的那
份快照。它们是写给读者看的——要拿来做东西请用那份清单——而且它们是这棵树的投影，所以没变过的树写出来
的页面总是一模一样。两份都由 `just index` 生成，都不是手写的。

每个 skill 一个目录，每个角度一个文件。每个 json 恰好是一个 prompt 的结构化输出，生成完即完整落盘——
所以批次被中断只会丢掉它正在处理的那几个 prompt，下一批会从断点继续。

| Prompt     | 结构                                     | 内容                                                        |
| ---------- | ---------------------------------------- | ----------------------------------------------------------- |
| `domain`   | `{domain, confidence, probabilities}`    | 下面 13 个英文分类中的一个、端点自己给出的置信度，以及它据以判断的那份分布 |
| `scenario` | `{text}`                                 | 一段 100 字以内的场景化介绍，从用户痛点切入                 |
| `tagline`  | `{taglines[3]}`                          | 3 条宣传短标语，每条 20 字以内                              |
| `blackbox` | `{function, input_output[3–5]}`          | 黑盒视角：你给什么 → 你得到什么，不谈内部实现               |
| `whitebox` | `{execution_flow[3–5], mechanisms[2–3]}` | 白盒视角：主路径流程、关键机制、真实依赖                    |
| `comments` | `{comments[4–6]}`                        | 用户第一人称评论；`category` 通常为 妙用 / 坑 / 注意 / 启发 |

`{...[n–m]}` 表示长度为 n~m 的数组；`input_output` 的元素是 `{input, output}`，`comments`
的元素是 `{user, category, comment}`。除 domain 角度(值都是英文)外，全部是中文。

`domain` 取自下面这个闭合英文枚举的单个值,可以直接筛：development · testing · data-analysis ·
devops-security · office-productivity · content-creation · design-media · knowledge-management ·
business-ops · finance-payment · education · lifestyle · other。旁边的 `confidence` 是端点对这次
判断的把握，由它在整个枚举上的分布导出 —— 它不是"这个标签正确的概率"，而是你想找出"值得再看一眼"的
标签时用来排序的那个数。

档案保留的是整份答案，包括 `probabilities`，因为赢家身上并不包含它：52 比 48 决出的结果和 99 比 1
决出的结果说的不是一件事，而"第二名是只差一步、还是根本不存在"恰恰是读到一条没把握的标签时想知道
的。目录只带标签与置信度，到此为止：

```bash
# 一个标签被选中；它差点选成什么，在同一个 skill 的档案里
jq '{domain, confidence, second: (.probabilities | to_entries | sort_by(-.value) | .[1])}' \
  output/profiles/mattpocock/skills/grill-me/domain.json
```

## 怎么跑

需要 Python 3.12+、[uv](https://docs.astral.sh/uv/) 和 [`just`](https://just.systems)。凭据放在
本地 `.env`（复制 [`.env.example`](.env.example)）；只会访问镜像和你的两个模型端点 —— 五个角度走
对话端点，`domain` 走 System One 端点，后者收到的是强类型问题而不是提示词。

```bash
uv sync
just sync              # 把镜像拉进 output/skills 与 output/upstream
just refresh           # ……并删掉来源随之变了的那些档案
just                   # 只做第一个 skill：一次单 skill 冒烟
just limit=0           # 生成所有还缺的档案：整份快照，无上限
just prompt=scenario   # 只做这一个角度，窗口内每个 skill 都要
just limit=20 jobs=8   # 同时跑 8 个，只做前 20 个 skill
just dry=1 limit=2     # 离线冒烟：假模型、真布局
just index             # 从磁盘上的内容重建 output/skills.jsonl 与两份 README
```

`jobs` 决定同时跑多少个生成，`rpm` 把它们配速到端点允许的节奏（写着每分钟 20 次的免费档就用
`just rpm=20`）。`limit` 数的是工作而不是位置：它取接下来**还缺内容**的那些 skill，顺序按清单自身的
顺序（也就是镜像的：安装量降序），所以有限的窗口先做安装量最高的 skill，反复运行则沿着数据集往下走，
而不是反复做最上面那几个。已存在的输出永远不会被重建——文件本身就是全部的缓存。
`just invalidate <prompt>`（或删掉某个输出、或 `just clean`）就是「失效」的全部含义。细节见
[DEVELOPING.zh-CN.md](DEVELOPING.zh-CN.md)。

## 怎么用这份数据

清单说清一个 skill 是什么，两个目录才是内容。`output/skills/<id>/` 就是镜像原样发布的那个 skill——
完整，所以「安装」就是一次复制；`output/profiles/<id>/` 是围绕它写出的东西。`<id>` 就是两者下面的
路径，其中的 `:` 或 `&` 写成 `_`（当前快照里有两个这样的 skill）：

```bash
# 一个 skill 是什么、值多少、被归到哪一类
jq -r '[.id, .installs, (.domain[0] // "-")] | @tsv' output/skills.jsonl | head

# 安装一个：它的目录是完整的，与镜像发布的一模一样
cp -r output/skills/mattpocock/skills/grill-me ~/.claude/skills/

# 或者读放在它旁边的那些档案
cat output/profiles/mattpocock/skills/grill-me/domain.json
```

发布时请把这整个 `output/` 原样保留——布局是唯一的契约，镜像自己的文件也在里面。清单只是从树派生出来
的便利：树一陈旧它也就陈旧，而 `just index` 会把整个文件重写一遍。
