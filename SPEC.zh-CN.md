# skills-profiles：外部视图

黑盒视角：用户或消费者能看到的一切，不含任何内部构建方式。

**产品是一个目录**——`output/`：每个 skill 一个目录、里面是它的 `SKILL.md`，为每个 skill 写的一个
领域标签和一份中文页面，以及把这些连起来的一份清单。生成器为产出这个目录而存在，所以它就是接口，
命令只决定写它的哪一部分。

English: [SPEC.md](SPEC.md)

## 1. 产出——接口

```
<output_dir>/
├── skills/<owner>/<repo>/<slug>/     # 每个 skill 一个目录——可直接当 skill 安装，
│   ├── SKILL.md                      #   标注随行：源页面，从该 skill 自己的仓库拉取
│   ├── domain.json                   # 标签：{domain, confidence, probabilities}
│   └── SKILL.zh.md                   # 中文页面；front matter 里带中文 description
├── repos.jsonl                       # 一行一仓库：{id, owner, repo, description, stars,
│                                     #   updated_at, pushed_at, html_url, gone, fetched_at}
├── owners/<owner>.png                # 一个 owner 的头像，前端只看 owner 即可拼接的固定路径——
│                                     #   owner 没有清单
├── skills.jsonl                      # `just index`：清单，每个 skill 扁平一行
└── README.md                         # ……以及旁边的首页：这个目录是什么、
    README.zh-CN.md                   #     建了多少；同一页面，中文一份
```

这里的一切都不需要镜像：清单写明每个 skill，每个 skill 目录里装着源页面和为它建的东西。
`repos.jsonl` 与 `owners/` 下的头像是 skill 之上的实体——一行一仓库（description、stars 和最近
更新时间）、一 owner 一张头像——按 skill id 开头的 `owner/repo`（或 `owner`）作键，所以不必第二份
清单就能拼上。镜像的清单由 `just sync` 现拉进清单文件
——清单是它唯一留下的痕迹。

`<id>` 是 skill id，`{owner}/{repo}/{slug}`。行里按镜像的拼写携带它；两个目录把 `:` 和 `&` 拼
写成 `_`，这也是交给 `jev.py` 的句柄。

`domain.json` 是 `{domain, confidence, probabilities}`：

- `domain`——13 个封闭英文分类之一：development · testing · data-analysis · devops-security ·
  office-productivity · content-creation · design-media · knowledge-management · business-ops ·
  finance-payment · education · lifestyle · other。可以直接过滤。
- `confidence`——端点自己对这次调用有多接近的读数，端点没说时为 `null`；不是标签正确的概率，
  发布它是为了排序，而不是当作概率来信任。
- `probabilities`——那个分布，完整保留，因为无法从赢家恢复它：0.52 对 0.48 的抉择与 0.99 对
  0.01 的抉择说的不是一回事。所有值均为英文。

- 每个 skill 一个目录、两个生成文件：`domain.json`，即端点完整的类型化回答；以及 `SKILL.zh.md`，
  中文页面——代码组装的 front matter，其 `description` 是一句话描述的中文译文，下面是翻译后的正文。
  front matter 从不经模型之手，所以 description 永远能从页面里解析回来。
- **实体是一份清单加一组文件。** `repos.jsonl` 一行一仓库（`id`、`owner`、`repo`、`description`、
  `stars`、`updated_at`、`pushed_at`、`html_url`、`gone`、`fetched_at`）；每个 owner 就是一张头像，
  在固定的 `owners/<owner>.png`，前端只看 owner 名即可拼接，没有 owner 清单要读。仓库行带 `gone: true`
  的是 GitHub 无答案的仓库：否定结果留在清单里，所以没有哪一轮会重拉；owner 没有这样的行，404 的
  owner 就在下一轮重试。与 skill 的连接键是 id 开头的 `owner/repo`（或 `owner`）。
- **清单是入口。** `skills.jsonl` 按镜像自己的顺序为镜像列出的、树仍可构建的每个 skill 存扁平一行——镜像的行
  （`id`、`installs`）加上从该 skill 自己的 `SKILL.md` 读出的 `description`、它的
  `description_zh`（即 zh 页面 front matter 里的 `description`）、标的 `domain` 和标注时的
  `confidence`。每个列出的 skill 都是一行，无论拉没拉取：拼接字段在树拉取并构建之前为 `null`，
  所以未拉取的 skill 是一行 null 而不是缺失的行，清单同时是数据集和批次工作的顺序。
  仓库已在盘上、却解析不出可读 description 的行不是一行——fetch 已取过该仓库而一无所获，
  任何一轮都无法构建它，死行不稀释数据集。
  `.domain != null` 是已标注、`.description_zh != null` 是已翻译的部分，`.installs` 给未建成的
  排序。清单取三个标签字段中的两个，回答本身住在 profile 里。
- **README 是首页**，由同一命令从同一次遍历写出：两行说明目录是什么，然后数据集建了多少——各角度的数量
  及其占镜像安装量的份额，外加实体清单带来的仓库与 owner 覆盖率，在它们所描述的快照之下。没有任何东西回读它们，每一行都是树的函数，
  所以没变的树会重写出逐字节相同的页面。
- 两个角度各有一个生产者。`jev.py` 向 System One 端点问类型化问题，而不是发聊天提示词：这就是
  为什么 `domain` 没有提示词对、没有理由行——端点用封闭集的一个成员作答，不写任何散文。
  `skill_zh.py` 向 OpenAI 兼容的聊天端点发起调用：描述一次，正文按其自身的 Markdown 缝合线
  切块后每块一次、逐块翻译；页面由代码组装，每一块都回来才写——半截翻译的页面绝不能冒充完整
  的一页。两者都是同一个共享内核 `common.py` 之上的薄角度：目录树、源读取、prompt 文件、
  带重试的调用、原子写，以及命令本身。开窗、懒拉取和驱动它们的进程池是同一个驱动器
  `batch.py`，justfile 只负责启动它。

## 2. 输入

| 是什么                                                 | 在哪                  | 由谁放进去                                                  |
| ------------------------------------------------------ | --------------------- | ----------------------------------------------------------- |
| 各 skill：每个 skill 一个目录，SKILL.md 与它的角度文件 | `<output_dir>/skills` | 各批次——每个批次在第一次构建某仓库的 skill 时拉取该仓库一次 |
| state 模板 `prompts/_system.md`                        | `prompts_dir`         | 你                                                          |
| 翻译 system 提示词 `prompts/translate.md`              | `prompts_dir`         | 你                                                          |
| 翻译 user 提示词 `prompts/translate_user.md`           | `prompts_dir`         | 你                                                          |
| 页面 system 提示词 `prompts/skill_zh.md`               | `prompts_dir`         | 你                                                          |
| 页面 user 提示词 `prompts/skill_zh_user.md`            | `prompts_dir`         | 你                                                          |

镜像的清单——`just sync` 现拉进清单文件，清单是它唯一留下的痕迹——是行集合：批次工作的顺序
（安装量降序），以及树无法知道的安装量。`skills/<id>/SKILL.md` 是构造 state 的全部材料——此外为
消歧还会用同仓库旁系 skill 的一句话描述；一次 fetch 把仓库里每个 skill 的 `SKILL.md` 都取出来
（子目录里的那个才算 skill；只在根目录有一个 `SKILL.md` 的仓库本身是单个 skill，根文件就是它的源，
而子目录 skill 旁的根 `SKILL.md` 仍是 readme），所以树里留下的是仓库所带的 skill。

skill 的一句话描述不在镜像索引里（上游已移除）：它从 skill 自己的 front matter 读出，front
matter 给不出描述的 skill 永远不会被任何一个生产者构建。镜像是拉来的快照，只读。分类法是代码：
`jev.py` 里的 `CRITERIA` 和 `INSTRUCTION`，作为答案被限定的选项交给端点——只陈述一次，没有
schema 里的 enum，也没有要保持同步的解码器。翻译任务正好相反：它的话术都是 Jinja 模板——
描述用 `prompts/translate.md` 和 `prompts/translate_user.md`，正文用 `prompts/skill_zh.md` 和
`prompts/skill_zh_user.md`——用代码固定的目标语言和文本渲染，代码里没有任何关于任务本身的东西。

## 3. 控制

批处理是一个驱动器 `batch.py`，修饰符走命令行，为一个角度或两个角度运行；justfile 只负责选择
命令与旋钮。动词如下：

| 命令                 | 作用                                                                                                                  |
| -------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `just build <angle>` | 构建接下来 `limit` 个还缺该角度文件的 skill（`domain`、`skill_zh`，或 `all` 表示两者共池共窗口一次跑完）；裸 `just` 即默认只做一个的 `build domain` |
| `just clean <angle>` | 逆窗口：从接下来 `limit` 个**已有**该文件的 skill 删除它（`domain`、`skill_zh`，或 `all` 表示两者）；`limit 0` 为全部 |
| `just meta`          | 抓取清单列出、还缺产物的每个仓库与 owner——仓库资料写进 `repos.jsonl`，头像写进 `owners/<owner>.png`；`just meta --clean` 则忘掉它们 |
| `just index`         | 写清单和两个 README：镜像的行拼接 description、其中文翻译与标签，以及发布根目录的首页                                 |
| `just sync`          | 与镜像对账：拉取清单、合并新增了 skill 的仓库里的源，其余源原样不动；镜像删掉的 skill 会在 stderr 提到，文件原地保留 |
| `just test`          | 跑套件                                                                                                                |

`build` 和 `clean` 是同一清单顺序上的互逆窗口，受同一个 `limit` 约束：build 数缺文件的
skill，clean 数有文件的 skill。保留已拉取源的完整重置是 `just limit=0 clean all` 之后再
`just sync`。连源也要丢掉则删除仓库目录，下一次 build 或 sync 会重新拉取。要在窗口之外直接
构建某个具名 skill，直接跑它的脚本（`jev.py <id>` / `skill_zh.py <id>`）。`meta` 是唯一的实体动词：
它抓取清单里还缺行的每个仓库、还缺头像的每个 owner，`meta --clean` 再忘掉它们——顺序仍是清单，
按 `owner/repo` 与 `owner` 去重读出。

修饰符是命令行变量，别无他处：

| 旋钮                                      | 默认                                          | 含义                                                                                                                                    |
| ----------------------------------------- | --------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `limit`                                   | 1                                             | 按清单顺序——镜像顺序，安装量降序——接下来 N 个还缺当前角度产物的 skill；`0` = 全部，无上限。数工作量不数位置，所以重复运行沿数据集往下走 |
| `jobs`                                    | 32                                            | 同时在飞的调用数；瞬时 429 仍由客户端自己的重试吸收                                                                                     |
| `dry`                                     | –                                             | `1` = 假端点、真实目录结构                                                                                                              |
| `output_dir` `prompts_dir` `listing` `py` | 见 [DEVELOPING.zh-CN.md](DEVELOPING.zh-CN.md) | 管道配置                                                                                                                                |

底下一次一个 skill：

```
jev.py <id> [--print]         # 仅开发：类型化问题，state 来自 _system.md——只打印，不调用
skill_zh.py <id> [--print]    # 仅开发：页面的请求数组，先描述后正文各块
```

- stdout 是数据（`--print` 下是请求）；stderr 是进度。
- jev.py 的源在 20 000 字符处截断，截断在源内部声明；skill_zh.py 按正文自身的 Markdown 缝合线
  切块，并把那句话描述整段发送。
- 聊天调用默认带上 MaaS 深度思考开关（`enable_thinking`，`max_tokens` 取文档上限）：模型先把推理
  写进 `reasoning_content`；这份草稿不读取也不落盘——页面里只有 `content`，即译文本身。
- 退出：`0` 已建 · `1` 输入或端点不可用 · `2` 参数错误。front matter 给不出 description 的
  skill 属于不可用输入：被丢弃，stderr 一行，什么都不写。批次本身只在窗口内所有任务都失败时才
  退出 `1`——部分产出即是已发布的产出。

## 4. 配置

`.env`（复制 [`.env.example`](.env.example)）或 `SKILLS_PROFILES_*`；env → `.env` → 默认值。它装
两个端点：类型化端点是 `API_KEY`、`BASE_URL`、`MODEL`，OpenAI 兼容聊天端点是 `TRANSLATE_API_KEY`、
`TRANSLATE_BASE_URL`、`TRANSLATE_MODEL`——外加 `MAX_RETRIES`、`DRY_RUN`、读取实体资料所用的
`GITHUB_TOKEN`，以及必要时移动两个路径用的变量。超时是每个端点各一个：`TIMEOUT`（类型化端点一到三秒即答）与 `TRANSLATE_TIMEOUT`（默认
120，因为思考调用先推理、常常超出类型化端点的耐心）。聊天调用方还有 `TRANSLATE_ENABLE_THINKING`
（默认开）和 `TRANSLATE_MAX_TOKENS`。页面角度 `skill_zh.py` 是聊天端点唯一的调用方，先要描述、
再要正文各块，共用同一组 `TRANSLATE_*` 设置。默认地址和模型指向讯飞星辰 MaaS 上的
Spark-X2.5-4B；模型 id 以控制台服务页显示的为准，订阅方通过 `TRANSLATE_MODEL` 指定。该端点失败
的 skill 会在一个兜底聊天端点上重试一次——`TRANSLATE_FALLBACK_BASE_URL`、
`TRANSLATE_FALLBACK_MODEL` 与 `TRANSLATE_FALLBACK_API_KEY`；默认指向 Agnes AI，不设密钥即关闭
兜底。兜底请求只换模型：MaaS 专属的思考开关不带过去——更严格的 OpenAI 兼容端点会因为不认识的
字段拒绝整个请求。

上面的批处理旋钮**不是**环境变量：一次运行只因为命令行明说才改变。

## 5. 消费者可以依赖什么

- **存在即缓存。** 已写出的东西绝不重建；停下的批次从第一个缺失文件恢复。两个角度各自缓存：有
  标签不能满足 zh 页面批次，反之亦然。
- **失效即 `clean`。** 改 `_system.md` 本身不使任何东西失效，且已在磁盘上的源不会重新拉取：某角度
  靠删除它的文件（`just clean <angle>`）重新生成，某个源靠删除它的仓库
  目录重新拉取，或在清单给该仓库新增 skill 后由 `just sync` 重新拉取。
- **失败不丢任何东西。** 失败的调用不写文件，也不结束批次；下次运行恰好重试它。
- **读不出东西的 skill 永不构建。** 调用前它的 front matter 必须给出 description，所以清单里没有
  它，窗口也看不到它：不调用、不写文件、没有要重试的失败——两个角度都一样。
- **文件要么完整要么不存在。** json 原地改名写入，所以写了一半的永远不可见。
- **每个文件一次对话。** 无排序、角度之间无依赖、无级联。
- **清单是派生且完整的。** `just index` 离线地从树整体重建它：镜像列出的、树仍可构建的每个 skill 一行，树还没
  产出的拼接字段为 `null`——README 从同一次遍历写出，所以那里没有两样东西能描述不同的树。
- **目录结构是唯一的契约。** 原样发布 `output/`。

## 6. 待定——成为正式 spec 前先达成一致

1. `test` 是表面的一部分，还是仅开发用（排除在上面的承诺之外）？请求打印已定论：不为它设
   配方——`--print` 是两个脚本上仅开发用的开关，直接用 `uv run python <脚本> <id> --print` 跑。
2. `listing` 和 `py` 应该是公开旋钮，还是固定默认值的管道配置？
