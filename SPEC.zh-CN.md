# skills-profiles：外部视图

黑盒视角：用户或消费者能看到的一切，不含任何内部构建方式。

**产品是一个目录**——`output/`：镜像原样发布的 skill 目录、为每个 skill 写的一个领域标签、旁边
镜像自己的文件，以及把两者连起来的一份清单。生成器为产出这个目录而存在，所以它就是接口，命
令只决定写它的哪一部分。

English: [SPEC.md](SPEC.md)

## 1. 产出——接口

```
<output_dir>/
├── skills/<owner>/<repo>/<slug>/     # 镜像自己的目录，完整且原样：
│   ├── SKILL.md                      #   拷一个进 skills 文件夹，skill 就
│   └── ...该 skill 自带的每个文件     #   装上了——这就是用户下载的东西
├── profiles/<owner>/<repo>/<slug>/
│   └── domain.json                   # 标签：{domain, confidence, probabilities}
├── skills.jsonl                      # `just index`：清单，每个 skill 扁平一行
├── README.md                         # ……以及旁边的首页：这个目录是什么、
├── README.zh-CN.md                   #     建了多少；同一页面，中文一份
└── upstream/                         # 镜像的其余部分：skills.jsonl、repos.jsonl、owners.jsonl、
                                      # curated.jsonl、trending.json、stats.json、latest、avatars/
```

这里的一切都不需要镜像：skill 从 `skills/` 安装，关于它的一切都在 `skills.jsonl` 里。

`<id>` 是 skill id，`{owner}/{repo}/{slug}`。行里按镜像的拼写携带它；两个目录把 `:` 和 `&` 拼
写成 `_`，这也是交给 `jev.py` 的句柄。

`domain.json` 是 `{domain, confidence, probabilities}`：

- `domain`——13 个封闭英文分类之一：development · testing · data-analysis · devops-security ·
  office-productivity · content-creation · design-media · knowledge-management · business-ops ·
  finance-payment · education · lifestyle · other。可以直接过滤。
- `confidence`——端点自己对这次调用有多接近的读数，由枚举上的分布导出；不是标签正确的概率，发
  布它是为了排序，而不是当作概率来信任。
- `probabilities`——那个分布，完整保留，因为无法从赢家恢复它：0.52 对 0.48 的抉择与 0.99 对
  0.01 的抉择说的不是一回事。所有值均为英文。

- 每个 skill 一个目录、一个文件：`domain.json`，即端点的完整回答。
- **清单是入口。** `skills.jsonl` 由 `just index` 写：每个 skill 扁平一行，按镜像自己的顺序，由
  镜像的行——`id`、`installs`、`url`、`hash`、`fetchedAt`——加上从该 skill 自己的 `SKILL.md` 读出
  的 `description`、标的 `domain` 和标注时的 `confidence`。三者未知时为 `null`，所以行陈述的是数
  据集而不是在制品：`.domain != null` 是已建成的部分，`.installs` 给未建成的排序。清单取三个标签
  字段中的两个，回答本身住在 profile 里。
- **README 是首页**，由同一命令从同一次遍历写出：两行说明目录是什么，然后数据集标了多少——数量
  及其占镜像安装量的份额，在它们所描述的快照之下。没有任何东西回读它们，每一行都是树的函数，
  所以没变的树会重写出逐字节相同的页面。
- 标签由一个生产者写：`jev.py` 向 System One 端点问类型化问题，而不是发聊天提示词。这就是为什
  么 `domain` 没有提示词对、没有理由行：端点用封闭集的一个成员作答，不写任何散文。

## 2. 输入

| 是什么 | 在哪 | 由谁放进去 |
| --- | --- | --- |
| 镜像：每个 skill 一个目录，以及它自己的索引和元数据 | `<output_dir>/skills` 和 `<output_dir>/upstream` | `just sync`，来自上游 `dist` 分支 |
| state 模板 `prompts/_system.md` | `prompts_dir` | 你 |

`upstream/skills.jsonl` 是镜像自己的清单，是清单拼接的左表：行集合、批次工作的顺序（安装量降
序），以及树无法知道的字段。`skills/<id>/SKILL.md` 是构造 state 的全部材料——此外为消歧还会用
同仓库旁系 skill 的一句话描述；skill 目录里的其他文件是为安装它的用户携带的，并不读取。

skill 的一句话描述不在镜像索引里（上游已移除）：它从 skill 自己的 front matter 读出，front
matter 给不出描述的 skill 永远不会被构建。镜像是拉来的快照，只读。分类法是代码：`jev.py` 里的
`CRITERIA` 和 `INSTRUCTION`，作为答案被限定的选项交给端点——只陈述一次，没有 schema 里的 enum，
也没有要保持同步的解码器。

## 3. 控制

批处理是一个带修饰符的配方，加六个动词：

| 命令 | 作用 |
| --- | --- |
| `just` | 标注窗口内每个还缺 `domain.json` 的 skill |
| `just one <id>` | 标注一个 skill，窗口内外皆可 |
| `just invalidate` | 删除所有标签，所有位置 |
| `just index` | 写清单和两个 README：镜像的行拼接 description 与标签，以及发布根目录的首页 |
| `just sync` | 拉取镜像，整体替换 `skills/` 和 `upstream/`，重建清单 |
| `just refresh` | 拉取，并删除随之源 hash 变化的每个标签 |
| `just clean` | 删除 profiles、清单和 README；保留 skill 和镜像的文件 |
| `just render <id>` · `just test` | 仅开发：打印请求 · 跑套件 |

修饰符是命令行变量，别无他处：

| 旋钮 | 默认 | 含义 |
| --- | --- | --- |
| `limit` | 1 | 按清单顺序——镜像顺序，安装量降序——接下来 N 个还没标签的 skill；`0` = 全部，无上限。数工作量不数位置，所以重复运行沿数据集往下走 |
| `jobs` | 每核一个 | 同时进行的调用数 |
| `rpm` | 0 | 按端点每分钟额度控速 |
| `dry` | – | `1` = 假端点、真实目录结构 |
| `output_dir` `prompts_dir` `snapshot` `py` | 见 [DEVELOPING.zh-CN.md](DEVELOPING.zh-CN.md) | 管道配置 |

底下一次一个 skill：

```
jev.py <id> [--print]     # 类型化问题在 jev.py 自己这里，state 来自 _system.md
```

- stdout 是数据（`--print` 下是请求）；stderr 是进度。
- 源在 20 000 字符处截断，截断在源内部声明。
- 退出：`0` 已建 · `1` 输入或端点不可用 · `2` 参数错误。front matter 给不出 description 的
  skill 属于不可用输入：被丢弃，stderr 一行，什么都不写。

## 4. 配置

`.env`（复制 [`.env.example`](.env.example)）或 `SKILLS_PROFILES_*`；env → `.env` → 默认值。它只
装唯一的端点：`API_KEY`、`BASE_URL`、`MODEL`、`TIMEOUT`、`MAX_RETRIES`——外加 `DRY_RUN`，以及必要
时移动两个路径用的变量。

上面的批处理旋钮**不是**环境变量：一次运行只因为命令行明说才改变。

## 5. 消费者可以依赖什么

- **存在即缓存。** 已写出的东西绝不重建；停下的批次从第一个缺失文件恢复。
- **失效即删除。** 改 `_system.md` 本身不使任何东西失效；新快照使它改变的东西失效，`just
  refresh` 是删除那些标签的动词。
- **失败不丢任何东西。** 失败的调用不写文件，也不结束批次；下次运行恰好重试它。
- **读不出东西的 skill 永不构建。** 调用前它的 front matter 必须给出 description，所以清单为它
  写 `description: null`，窗口跳过该行：不调用、不写文件、没有要重试的失败。
- **文件要么完整要么不存在。** json 原地改名写入，所以写了一半的永远不可见。
- **每个文件一次对话。** 无排序、无依赖、无级联。
- **清单是派生且完整的。** `just index` 离线地从树整体重建它：镜像列出的每个 skill 一行，镜像
  已删除但标签仍在的 skill 也一行——README 从同一次遍历写出，所以那里没有两样东西能描述不同的
  树。
- **目录结构是唯一的契约。** 原样发布 `output/`；包括镜像自己的文件。

## 6. 待定——成为正式 spec 前先达成一致

1. `render` 和 `test` 是表面的一部分，还是仅开发用（排除在上面的承诺之外）？
2. `snapshot` 和 `py` 应该是公开旋钮，还是固定默认值的管道配置？
