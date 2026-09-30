# skills-profiles

为 [skill-one/skills-sh-mirror](https://github.com/skill-one/skills-sh-mirror) 收集的 [agent
skills](https://www.skills.sh) 打领域标签并做中文翻译：每个 skill 一个封闭分类标签，由
Jev（TypeSafe System One）端点根据该 skill 自己的 description 与 `SKILL.md` 通过一次类型化问答
生成；另有若干次 OpenAI 兼容的聊天调用——先有一次把那句 description 翻译成中文，之后正文按
markdown 接缝切块、每块一次调用，各块译文重新拼成一份独立的中文页面。

English: [README.md](README.md) · 开发指南: [DEVELOPING.zh-CN.md](DEVELOPING.zh-CN.md)

## 产出

一切都落在同一个根目录 `output/` 下：各角度所依据的构建源、为它们写的东西（一个标签加中文翻
译），以及把这些连起来的一份清单——读者不需要再回到镜像。发布就是拷贝这一个目录。skills 旁边，
`repos.jsonl` 一行一仓库、`owners/<owner>.png` 一 owner 一张头像，按 skill id 开头的同一个
`owner/repo` 作键。

```
output/
├── skills/<owner>/<repo>/<dir>/     每个 skill 一个目录——可直接当 skill 安装，
│   ├── SKILL.md                     标注随行：源页面，从该 skill 自己的仓库拉取
│   ├── domain.json                  一个标签，类型化端点回答的完整内容
│   └── SKILL.zh.md                  中文页面；front matter 里带中文 description
├── repos.jsonl                      一行一仓库：description、stars、最近更新时间和链接，
│                                    GitHub 无答案处 `gone`
├── owners/<owner>.png               owner 头像——前端无需读清单即可拼接的固定文件
├── skills.jsonl                     清单：镜像列出的、树仍可构建的每个 skill 一行——镜像自己的行
│                                    （id、name、installs）外加 dir（文件在 skills/ 下的位置，
│                                    原样拼接）、description、description_zh 和 domain，
│                                    未拉取构建前均为 null
└── README.md                        ……以及旁边的首页：这个目录是什么、建了多少——
    README.zh-CN.md                  一份英文，这份中文
```

`skills.jsonl` 是入口。它按镜像自己的顺序（安装量从高到低）列出镜像有的、树仍可构建的每个 skill，带着从该
skill 自己的 `SKILL.md` 读出的 `description`、它的 `description_zh`、本项目标的 `domain`，以及
端点对该标签的确信度。拼接字段在拉取并构建之前都是 `null`——这也是批次判断还剩什么的方式；仓库
一无所获的 skill 则整行不出现——所以
已标注的部分一个过滤就能取出：

```bash
jq -r 'select(.domain == "development") | [.installs, .id] | @tsv' output/skills.jsonl | head

# 端点最不确信的标签，完整回答在它旁边的文件里
jq -r 'select(.confidence != null and .confidence < 0.7) | [.confidence, .domain, .id] | @tsv' \
  output/skills.jsonl
```

每个 skill 一个目录、两个生成文件：`domain.json` 和 `SKILL.zh.md`。每个文件一生成就完整写入
——中断的批次只会丢掉正在进行的那一次调用，下一次从停下的地方继续。两个角度互相独立：各自
构建、各自重建。

`domain.json` 的形状是 `{domain, confidence, probabilities}`：下面 13 个英文分类之一、端点对它
的确信度，以及读出该标签的概率分布。全部为英文。

`domain` 是封闭枚举的一员，可以直接过滤：
development · testing · data-analysis · devops-security · office-productivity · content-creation ·
design-media · knowledge-management · business-ops · finance-payment · education · lifestyle ·
other。旁边的 `confidence` 是端点自己说出的确信度——不是标签正确的概率，而是你想找出值得再
看一眼的标签时用来排序的数字（端点没说时为 `null`）。

profile 保留完整回答，包括 `probabilities`，因为赢家本身不包含它：0.52 对 0.48 的抉择与 0.99
对 0.01 的抉择说的不是一回事。清单只带标签和确信度，到此为止：

```bash
# 选中了一个标签；端点差点改选的另一个在同一文件里
jq '{domain, confidence, second: (.probabilities | to_entries | sort_by(-.value) | .[1])}' \
  output/skills/mattpocock/skills/grill-me/domain.json
```

`SKILL.zh.md` 是代码组装的中文页面：front matter 里是那句话描述的中文译文（产品名和代码保持
原样、已是中文的内容保持不变），下面是翻译后的正文。front matter 从不经模型之手，所以
description 永远能从页面里机器可读地解析回来。聊天端点没有封闭枚举，所以没有确信度、没有
分布——字符串就是完整回答。

## 运行

需要 Python 3.12+、[uv](https://docs.astral.sh/uv/) 和 [`just`](https://just.systems)。凭据放在
本地 `.env`（复制 [`.env.example`](.env.example)）；访问的主机有镜像、System One 端点（回答
类型化问题而不是提示词），以及负责翻译的 OpenAI 兼容聊天端点。

```bash
uv sync
just sync                          # 与镜像对账：清单、新增源、目录文件
just                               # 构建第一个 domain 标签：单 skill 冒烟，顺带拉仓库
just build domain                  # 同上的具名写法
just limit=0 build domain          # 构建所有还缺的标签，整个快照，无上限
just limit=20 jobs=8 build domain  # 前 20 个 skill，一次八个（默认池大小 32）
just dry=1 limit=2 build domain    # 假端点，真实目录结构
just build all                     # 两个角度共池共窗口，一次跑完
just build skill_zh                # 第二个角度：构建第一个还缺的 SKILL.zh.md
just limit=0 build skill_zh        # 构建所有中文页面，limit/jobs/dry 旋钮相同
just clean domain                  # 反操作：忘掉第一个已构建的标签
just limit=0 clean all             # 忘掉两个角度的全部产物
just meta                          # 抓取每个仓库的 GitHub 资料与每个 owner 的头像
just index                         # 按磁盘内容重建 output/skills.jsonl 和两个 README
```

`build` 和 `clean` 是同一清单顺序上的互逆窗口：`build` 取接下来 `limit` 个**缺**该角度文件的
skill，`clean` 取接下来 `limit` 个**已有**该文件的 skill，所以 clean 之后再 build 恰好重建被
清掉的那些（`limit 0` 表示无上限）。

`jobs` 限制同时进行的调用数（默认 32）；瞬时 429 交给客户端自己的重试，不再有每分钟限速。

一个 skill 的仓库会在第一次构建它（们）时被拉取，之后不再拉——磁盘上的仓库目录就是缓存，
所以有限额度的运行只下载窗口真正需要的仓库，而不是整个数据集。`just sync` 会重新拉取镜像后来
给它新增了 skill 的仓库。

`limit` 数的是工作量而不是位置：它按清单自己的顺序（即镜像顺序：安装量降序）取下一批还缺当前
角度产物的 skill，所以有限额度的运行先做安装量最高的，重复运行沿数据集往下走。已存在的产出永不
重建——文件就是全部缓存。
`just clean <angle>`（或删除某个产出）是重新生成某个角度的方式；保留源的完整重置是
`just limit=0 clean all` 之后再 `just sync`。见 [DEVELOPING.zh-CN.md](DEVELOPING.zh-CN.md)。

## 使用

清单说明一个 skill 是什么；各 skill 目录是实际内容。`output/skills/<id>/` 装着源页面和为它写
的东西：`domain.json` 与中文页面 `SKILL.zh.md`。`<id>` 即 `skills/` 下的路径，其中的 `:` 或
`&` 写作 `_`。目录可以直接当 skill 安装——不过一个 skill 自带的远不止 `SKILL.md`（脚本、参考、
资源），完整内容在它自己的仓库里。

```bash
# 一个 skill 是什么、值多少、被标成什么
jq -r '[.id, .installs, (.domain // "-")] | @tsv' output/skills.jsonl | head

# 一个 skill 的构建源：批次读的就是它；完整 skill 在它自己的仓库里
cat output/skills/mattpocock/skills/grill-me/SKILL.md

# 为它写的东西，就在旁边：标签和中文页面
cat output/skills/mattpocock/skills/grill-me/domain.json
cat output/skills/mattpocock/skills/grill-me/SKILL.zh.md
```

原样发布 `output/` 即可——目录结构是唯一的契约。清单是从树派生的便利之
物：树变它才过期，`just index` 整体重建它。
