# skills-profiles

为 [skill-one/skills-sh-mirror](https://github.com/skill-one/skills-sh-mirror) 收集的 [agent
skills](https://www.skills.sh) 打领域标签并给中文描述：每个 skill 一个封闭分类标签，由
Jev（TypeSafe System One）端点根据该 skill 自己的 description 与 `SKILL.md` 通过一次类型化问答
生成；每个 skill 还有一个 `description_zh`，由 OpenAI 兼容的聊天端点把同一句 description 翻译
成中文，也是一次调用。

English: [README.md](README.md) · 开发指南: [DEVELOPING.zh-CN.md](DEVELOPING.zh-CN.md)

## 产出

一切都落在同一个根目录 `output/` 下，目录自包含：skill 原件、为它们写的东西（一个标签加一段
中文描述），以及把这些连起来的一份清单——读者不需要再回到镜像。发布就是拷贝这一个目录。

```
output/
├── skills/<owner>/<repo>/<slug>/    镜像自己的 skill 目录，完整且原样：
│   ├── SKILL.md                     拷一个进你的 skills 目录就等于装上了
│   └── ...该 skill 自带的每个文件
├── profiles/<owner>/<repo>/<slug>/
│   ├── domain.json                  一个标签，类型化端点回答的完整内容
│   └── description_zh.json          一句话描述的一份中文翻译
├── skills.jsonl                     `just index`：每个 skill 一行——镜像自己的行
│                                    （id、installs、url、hash、fetchedAt）外加 description、
│                                    description_zh 和 domain
├── README.md                        ……以及旁边的首页：这个目录是什么、建了多少——
├── README.zh-CN.md                  一份英文，这份中文
└── upstream/                        镜像的其余部分：它的索引、repos、owners、avatars
```

`skills.jsonl` 是入口。它按镜像自己的顺序（安装量从高到低）列出镜像有的每个 skill，带着从该
skill 自己的 `SKILL.md` 读出的 `description`、它的 `description_zh`、本项目标的 `domain`，以及
端点对该标签的确信度。四者未知时都是 `null`，所以已标注的部分一个过滤就能取出：

```bash
jq -r 'select(.domain == "development") | [.installs, .id] | @tsv' output/skills.jsonl | head

# 端点最不确信的标签，完整回答在它旁边的 profile 里
jq -r 'select(.confidence < 0.7) | [.confidence, .domain, .id] | @tsv' output/skills.jsonl
```

每个 skill 一个目录、两个文件：`domain.json` 和 `description_zh.json`。每个文件一生成就完整
写入——中断的批次只会丢掉正在进行的那一次调用，下一次从停下的地方继续。两个角度互相独立：各
自构建、各自重建。

`domain.json` 的形状是 `{domain, confidence, probabilities}`：下面 13 个英文分类之一、端点对它
的确信度，以及读出该标签的概率分布。全部为英文。

`domain` 是封闭枚举的一员，可以直接过滤：
development · testing · data-analysis · devops-security · office-productivity · content-creation ·
design-media · knowledge-management · business-ops · finance-payment · education · lifestyle ·
other。旁边的 `confidence` 是端点的确信度，由它在整个枚举上的分布导出——不是标签正确的概率，
而是你想找出值得再看一眼的标签时用来排序的数字。

profile 保留完整回答，包括 `probabilities`，因为赢家本身不包含它：0.52 对 0.48 的抉择与 0.99
对 0.01 的抉择说的不是一回事。清单只带标签和确信度，到此为止：

```bash
# 选中了一个标签；端点差点改选的另一个在同一 skill 的 profile 里
jq '{domain, confidence, second: (.probabilities | to_entries | sort_by(-.value) | .[1])}' \
  output/profiles/mattpocock/skills/grill-me/domain.json
```

`description_zh.json` 只有 `{description_zh}`：那句话描述的中文译文，产品名和代码保持原样、
已是中文的内容保持不变。聊天端点没有封闭枚举，所以没有确信度、没有分布——字符串就是完整回答。

## 运行

需要 Python 3.12+、[uv](https://docs.astral.sh/uv/) 和 [`just`](https://just.systems)。凭据放在
本地 `.env`（复制 [`.env.example`](.env.example)）；访问的主机有镜像、System One 端点（回答
类型化问题而不是提示词），以及负责翻译的 OpenAI 兼容聊天端点。

```bash
uv sync
just sync              # 拉取镜像到 output/skills 和 output/upstream
just refresh           # ……并删除随快照发生源变更的 profile
just                   # 标注第一个 skill：单 skill 冒烟
just limit=0           # 标注所有还缺标签的 skill，整个快照，无上限
just limit=20 jobs=8   # 前 20 个 skill，一次八个（默认池大小 32）
just dry=1 limit=2     # 离线冒烟：假端点，真实目录结构
just translate         # 第二个角度：翻译第一个还缺的 description_zh
just limit=0 translate # 翻译所有 skill，limit/jobs/dry 旋钮与上面相同
just index             # 按磁盘内容重建 output/skills.jsonl 和两个 README
```

`jobs` 限制同时进行的调用数（默认 32）；瞬时 429 交给客户端自己的重试，不再有每分钟限速。
`limit` 数的是工作量而不是位置：它按清单自己的顺序（即镜像顺序：安装量降序）取下一批还缺当前
角度产物的 skill，所以有限额度的运行先做安装量最高的，重复运行沿数据集往下走。已存在的产出永不
重建——文件就是全部缓存。
`just invalidate` 和 `just invalidate-translate`（或删除某个产出，或 `just clean`）是重新生成
某个角度的方式。见 [DEVELOPING.zh-CN.md](DEVELOPING.zh-CN.md)。

## 使用

清单说明一个 skill 是什么；两个目录是实际内容。`output/skills/<id>/` 是镜像发布的原样 skill
——完整，所以安装就是拷贝；`output/profiles/<id>/` 里是为它写的东西：`domain.json` 和
`description_zh.json`。`<id>` 在两处都是路径，其中的 `:` 或 `&` 写作 `_`。

```bash
# 一个 skill 是什么、值多少、被标成什么
jq -r '[.id, .installs, (.domain[0] // "-")] | @tsv' output/skills.jsonl | head

# 安装一个：它的目录完整，与镜像发布的一致
cp -r output/skills/mattpocock/skills/grill-me ~/.claude/skills/

# 为它写的东西，就在旁边：标签和中文描述
cat output/profiles/mattpocock/skills/grill-me/domain.json
cat output/profiles/mattpocock/skills/grill-me/description_zh.json
```

原样发布 `output/` 即可——目录结构是唯一的契约，包括镜像自己的文件。清单是从树派生的便利之
物：树变它才过期，`just index` 整体重建它。
