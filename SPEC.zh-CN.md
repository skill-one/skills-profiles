# skills-profiles：外部视图

黑盒视角：用户或消费者能看到的一切，不含任何内部构建方式。

**产品是一个目录**——`output/`：每个 skill 一个目录、里面只有它的 `SKILL.md`，为每个 skill 写的
一个领域标签和一段中文描述、旁边镜像自己的文件，以及把这些连起来的一份清单。生成器为产出这个
目录而存在，所以它就是接口，命令只决定写它的哪一部分。

English: [SPEC.md](SPEC.md)

## 1. 产出——接口

```
<output_dir>/
├── skills/<owner>/<repo>/<slug>/     # 每个 skill 一个目录，只有它的 SKILL.md：各角度
│   └── SKILL.md                      #   共用的构建源——不是安装件；完整的 skill
│                                     #   在它自己的仓库里
├── profiles/<owner>/<repo>/<slug>/
│   ├── domain.json                   # 标签：{domain, confidence, probabilities}
│   ├── description_zh.json           # 中文描述：{description_zh}
│   └── skill_zh.md                   # SKILL.md 正文的中文翻译
├── skills.jsonl                      # `just index`：清单，每个 skill 扁平一行
├── README.md                         # ……以及旁边的首页：这个目录是什么、
├── README.zh-CN.md                   #     建了多少；同一页面，中文一份
└── upstream/                         # 镜像自己的文件，原样保留：skills.jsonl、latest、stats.json 等
```

这里的一切都不需要镜像：清单写明每个 skill，profile 里是为它建的东西。
`skills/` 是生成器读取的源，与由它建出的产物放在一起——其中没有任何东西是安装件。

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

- 每个 skill 一个目录、三个文件：`domain.json`，即端点完整的类型化回答；`description_zh.json`，
  一句话描述的中文翻译；以及 `skill_zh.md`，SKILL.md 正文的中文翻译。
- **清单是入口。** `skills.jsonl` 由 `just index` 写：镜像列出的、能从其自身 `SKILL.md` 读出
  description 的每个 skill 扁平一行——读不出的根本不入清单——按镜像自己的顺序，由
  镜像的行——`id`、`installs`、`hash`、`fetchedAt`——加上从该 skill 自己的 `SKILL.md` 读出
  的 `description`、它的 `description_zh`、标的 `domain` 和标注时的 `confidence`。后三者未知时为
  `null`，所以行陈述的是数据集而不是在制品：`.domain != null` 是已标注、`.description_zh != null`
  是已翻译的部分，`.installs` 给未建成的排序。清单取三个标签字段中的两个，回答本身住在 profile
  里。
- **README 是首页**，由同一命令从同一次遍历写出：两行说明目录是什么，然后数据集标了多少——数量
  及其占镜像安装量的份额，在它们所描述的快照之下。没有任何东西回读它们，每一行都是树的函数，
  所以没变的树会重写出逐字节相同的页面。
- 三个角度各有一个生产者。`jev.py` 向 System One 端点问类型化问题，而不是发聊天提示词：这就是
  为什么 `domain` 没有提示词对、没有理由行——端点用封闭集的一个成员作答，不写任何散文。
  `translate.py` 向 OpenAI 兼容的聊天端点问一个自由文本问题——描述进去、中文出来——所以
  `description_zh` 是纯字符串，没有 confidence，也没有分布。`skill_zh.py` 向同一个聊天端点请求
  翻译 SKILL.md 正文；正文超过单次回答所能时按其自身的 Markdown 缝合线切块、逐块翻译，每一块都回来才写页面——半截翻译的页面
  绝不能冒充完整的一页。三者都是同一个共享内核 `common.py`
  之上的薄角度：目录树、源读取、prompt 文件、带重试的调用、原子写，以及命令本身。

## 2. 输入

| 是什么                                              | 在哪                                             | 由谁放进去                        |
| --------------------------------------------------- | ------------------------------------------------ | --------------------------------- |
| 镜像：每个 skill 一个目录，以及它自己的索引和元数据 | `<output_dir>/skills` 和 `<output_dir>/upstream` | `just sync`，来自上游 `dist` 分支 |
| state 模板 `prompts/_system.md`                     | `prompts_dir`                                    | 你                                |
| 翻译 system 提示词 `prompts/translate.md`           | `prompts_dir`                                    | 你                                |
| 翻译 user 提示词 `prompts/translate_user.md`        | `prompts_dir`                                    | 你                                |
| 页面 system 提示词 `prompts/skill_zh.md`            | `prompts_dir`                                    | 你                                |
| 页面 user 提示词 `prompts/skill_zh_user.md`         | `prompts_dir`                                    | 你                                |

`upstream/skills.jsonl` 是镜像自己的清单，是清单拼接的左表：行集合、批次工作的顺序（安装量降
序），以及树无法知道的字段。`skills/<id>/SKILL.md` 是构造 state 的全部材料——此外为消歧还会用
同仓库旁系 skill 的一句话描述；sync 会剥掉 skill 自带的其他文件，树里不保留任何它不读取的
东西。

skill 的一句话描述不在镜像索引里（上游已移除）：它从 skill 自己的 front matter 读出，front
matter 给不出描述的 skill 永远不会被任何一个生产者构建。镜像是拉来的快照，只读。分类法是代码：
`jev.py` 里的 `CRITERIA` 和 `INSTRUCTION`，作为答案被限定的选项交给端点——只陈述一次，没有
schema 里的 enum，也没有要保持同步的解码器。翻译任务正好相反：两段话都是 Jinja 模板，放在
`prompts/translate.md` 和 `prompts/translate_user.md`，用代码固定的目标语言和那句描述渲染，
代码里没有任何关于任务本身的东西。

## 3. 控制

批处理是一个带修饰符的共享配方，为两个角度之一运行，外加这些动词：

| 命令                                                            | 作用                                                                                  |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| `just`                                                          | 标注窗口内每个还缺 `domain.json` 的 skill                                             |
| `just translate`                                                | 翻译窗口内每个还缺 `description_zh.json` 的 skill                                     |
| `just skill-zh`                                                 | 翻译窗口内每个还缺 `skill_zh.md` 的 skill                                             |
| `just one <id>`                                                 | 标注一个 skill 的 domain，窗口内外皆可                                                |
| `just translate-one <id>`                                       | 翻译一个 skill 的描述，窗口内外皆可                                                   |
| `just skill-zh-one <id>`                                        | 翻译一个 skill 的 SKILL.md 正文，窗口内外皆可                                         |
| `just invalidate`                                               | 删除所有 domain 标签，所有位置                                                        |
| `just invalidate-translate`                                     | 删除所有中文描述，所有位置                                                            |
| `just invalidate-skill-zh`                                      | 删除所有中文 SKILL.md 页面，所有位置                                                  |
| `just index`                                                    | 写清单和两个 README：镜像的行拼接 description、其中文翻译与标签，以及发布根目录的首页 |
| `just sync`                                                     | 拉取镜像，整体替换 `skills/` 和 `upstream/`，重建清单                                 |
| `just refresh`                                                  | 拉取，并删除随之源 hash 变化的每个 profile——两个角度一起删                            |
| `just clean`                                                    | 删除 profiles、清单和 README；保留 skill 和镜像的文件                                 |
| `just render <id>` · `just translate-render <id>` · `just test` | 仅开发：打印请求 · 跑套件                                                             |

修饰符是命令行变量，别无他处：

| 旋钮                                       | 默认                                          | 含义                                                                                                                                    |
| ------------------------------------------ | --------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `limit`                                    | 1                                             | 按清单顺序——镜像顺序，安装量降序——接下来 N 个还缺当前角度产物的 skill；`0` = 全部，无上限。数工作量不数位置，所以重复运行沿数据集往下走 |
| `jobs`                                     | 32                                            | 同时在飞的调用数；瞬时 429 仍由客户端自己的重试吸收                                                                                     |
| `dry`                                      | –                                             | `1` = 假端点、真实目录结构                                                                                                              |
| `output_dir` `prompts_dir` `snapshot` `py` | 见 [DEVELOPING.zh-CN.md](DEVELOPING.zh-CN.md) | 管道配置                                                                                                                                |

底下一次一个 skill：

```
jev.py <id> [--print]         # 类型化问题在 jev.py 自己这里，state 来自 _system.md
translate.py <id> [--print]   # 一次聊天：两个翻译模板用那句话描述渲染
```

- stdout 是数据（`--print` 下是请求）；stderr 是进度。
- jev.py 的源在 20 000 字符处截断，截断在源内部声明；translate.py 只发一句话描述，没有可截断的
  东西。
- translate.py 默认带上 MaaS 深度思考开关（`enable_thinking`，`max_tokens` 取文档上限）：模型
  先把推理写进 `reasoning_content`；这份草稿不读取也不落盘——角度文件里只有 `content`，即那句
  译文本身。
- 退出：`0` 已建 · `1` 输入或端点不可用 · `2` 参数错误。front matter 给不出 description 的
  skill 属于不可用输入：被丢弃，stderr 一行，什么都不写。

## 4. 配置

`.env`（复制 [`.env.example`](.env.example)）或 `SKILLS_PROFILES_*`；env → `.env` → 默认值。它装
两个端点：类型化端点是 `API_KEY`、`BASE_URL`、`MODEL`，OpenAI 兼容聊天端点是 `TRANSLATE_API_KEY`、
`TRANSLATE_BASE_URL`、`TRANSLATE_MODEL`——外加两者共用的 `TIMEOUT`、`MAX_RETRIES`、`DRY_RUN`，以
及必要时移动两个路径用的变量。翻译端还有 `TRANSLATE_ENABLE_THINKING`（默认开）和
`TRANSLATE_MAX_TOKENS`；思考调用更慢，因此本地为翻译批次调大 `TIMEOUT`。第三个角度
`skill_zh.py` 调用同一个聊天端点，共用同一组 `TRANSLATE_*` 设置。默认地址和模型指向讯飞
星辰 MaaS 上的 Spark-X2.5-4B；模型 id 以控制台服务页显示的为准，订阅方通过 `TRANSLATE_MODEL`
指定。该端点失败的 skill 会在一个兜底聊天端点上重试一次——`TRANSLATE_FALLBACK_BASE_URL`、
`TRANSLATE_FALLBACK_MODEL` 与 `TRANSLATE_FALLBACK_API_KEY`；默认指向 Agnes AI，不设密钥即关闭
兜底。

上面的批处理旋钮**不是**环境变量：一次运行只因为命令行明说才改变。

## 5. 消费者可以依赖什么

- **存在即缓存。** 已写出的东西绝不重建；停下的批次从第一个缺失文件恢复。三个角度各自缓存：有
  标签不能满足翻译批次，反之亦然。
- **失效即删除。** 改 `_system.md` 本身不使任何东西失效；新快照使它改变的东西失效，`just
refresh` 是删除那些 profile 的动词——两个文件一起删，因为它们都来自同一个源。
- **失败不丢任何东西。** 失败的调用不写文件，也不结束批次；下次运行恰好重试它。
- **读不出东西的 skill 永不构建。** 调用前它的 front matter 必须给出 description，所以清单里没有
  它，窗口也看不到它：不调用、不写文件、没有要重试的失败——两个角度都一样。
- **文件要么完整要么不存在。** json 原地改名写入，所以写了一半的永远不可见。
- **每个文件一次对话。** 无排序、角度之间无依赖、无级联。
- **清单是派生且完整的。** `just index` 离线地从树整体重建它：镜像列出的、有 description 的
  skill 一行——没有 description 的、或上游已删除只剩 profile 的不入清单——README 从同一次遍历
  写出，所以那里没有两样东西能描述不同的树。
- **目录结构是唯一的契约。** 原样发布 `output/`；包括镜像自己的文件。

## 6. 待定——成为正式 spec 前先达成一致

1. `render` 和 `test` 是表面的一部分，还是仅开发用（排除在上面的承诺之外）？
2. `snapshot` 和 `py` 应该是公开旋钮，还是固定默认值的管道配置？
