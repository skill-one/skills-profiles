# 开发 skills-profiles

[README.md](README.md) 所述数据集背后的生成器：它从各 skill 自己的仓库拉取每个 skill 的
`SKILL.md`——镜像的索引说明什么存在，仓库持有它是什么——并向 Jev（TypeSafe System One）端点问
一个类型化问题：这个 skill 属于哪个封闭领域分类。第二个生产者 `skill_zh.py` 向 OpenAI 兼容的聊天
端点发起调用：一句话描述一次，正文按 markdown 接缝切块后每块一次；再按代码组装出中文页面
`SKILL.zh.md`，其 front matter 从不经模型之手。两者是同一个 skill 目录上的平行角度，而且都很薄：
目录树、源读取、prompt 文件、配置、带重试的调用、原子写和命令本身都只在 `common.py` 里有一份；
`translate.py` 是页面角度所调用的聊天端点库。`meta.py` 不是作用在 skill 上的角度，而是作用在它之上
的两个实体：它读取每个仓库与 owner 的 GitHub 资料，写进 skills 旁的两棵树。开窗、懒拉取和 `jobs` 宽的
生产者池都在同一个驱动器 `batch.py` 里；justfile 只负责启动它。

English: [DEVELOPING.md](DEVELOPING.md)

## 快速开始

需要 Python 3.12+、[uv](https://docs.astral.sh/uv/) 和 [`just`](https://just.systems)；两个端点
的密钥放在本地 `.env`（复制 [`.env.example`](.env.example)）。

```bash
uv sync
just sync                     # 与镜像对账：清单、新增源、目录文件
just                          # 端到端构建第一个 domain 标签，顺带拉取它的仓库
just limit=0 build domain     # ……或所有还没标签的 skill，整个快照，无上限
just build all                # 两个角度共池共窗口，一次跑完
just build skill_zh           # 第二个角度：构建第一个还缺的 SKILL.zh.md
just clean domain             # 反操作：忘掉第一个已构建的标签
```

假端点、真实目录结构、无 API 调用、无凭据：`just dry=1 limit=5 build domain`（以及
`just dry=1 build skill_zh`）；仓库仍会被拉取，所以请在源已在本地时运行，或传一个本地
`repo_tarball`。

## 批处理就是 `batch.py`

| 命令                 | 作用                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `just build <angle>` | `batch.py build <angle>`：按安装量从高到低，为接下来 `limit` 个还缺该角度文件的 skill 构建（`domain`、`skill_zh`，或 `all` 表示两者共池共窗口一次跑完）。顺序是清单自己的（`OUTPUT_DIR/skills.jsonl`，镜像顺序，安装量降序）——按 jsonl 解析，镜像列出的每个 skill 一行。窗口取接下来 `limit` 个该角度尚未解决的 skill：没有角度文件，也不是「仓库已在磁盘上却没有 `SKILL.md`」的 skill（它永远构建不了）。数的是工作量而不是位置，所以重复运行沿数据集往下走。驱动器随后在 `jobs` 宽的池子里跑生产者，每个 skill 一次生产者调用：每个任务在需要时才拉取它的仓库——同一仓库的第一个任务下载并解包，其余任务等这一次下载——仓库没有源的 skill 被跳过。裸 `just` 即默认只做一个的 `build domain`。 |
| `just clean <angle>` | 逆窗口，`batch.py clean <angle>`：按同一清单顺序取接下来 `limit` 个**已有**该角度文件的 skill，删掉文件。之后 `build` 恰好重建这些 skill；`limit 0` 清掉全部已构建的，`all` 同时忘掉两个角度的文件——即 sync 之前的那半步完整重置。窗口之外要按名构建单个 skill，仍直接跑脚本（`uv run python jev.py <id>` / `skill_zh.py <id>`）。                                                                                                                                                                                                                                            |
| `just meta`          | `batch.py meta`：从 GitHub 抓取清单里还缺行/头像的每个仓库与 owner——仓库按清单顺序合并进 `repos.jsonl`，头像写在固定的 `owners/<owner>.png`。GitHub 回 404/410 的仓库变成 `gone` 行——否定结果被留住，之后没有哪轮会重拉（owner 无此机制，404 的 owner 下轮重试）。`just meta --clean` 则忘掉清单与头像。规模快照需要 `SKILLS_PROFILES_GITHUB_TOKEN`（匿名每小时 60 次）。 |
| `just index`         | 写 `<output_dir>/skills.jsonl`——清单：镜像列出的、树仍可构建的每个 skill 一行，按镜像顺序，由镜像自己的行（`id`、`installs`）拼接从该 skill 的 `SKILL.md` 读出的 `description`、`SKILL.zh.md` front matter 里的 `description_zh`，以及 `domain.json` 里的 `domain` 和 `confidence`。拼接字段未知时为 `null`；仓库已在盘上、却解析不出可读 description 的行不是一行——fetch 已取过该仓库而一无所获，任何一轮都无法构建它。只读树——无网络、无调用——整体重写文件。同一次遍历还在旁边写两个 README：见下文 `readme.py`。                                                                                                                                                                                    |
| `just sync`          | 与镜像对账：拉取镜像清单，即行集合、顺序和安装量。源按需拉取：批次在第一次构建某仓库的 skill 时下载该仓库，仓库目录即缓存，所以既不会在需要前拉取，也不会拉取两次。清单新增了 skill 的仓库会在此时被重新拉取，新源合并进已建好的 skill 旁边，并全树修复按 name 拼写的别名。                                                                                                                                                                                                                                                                                                                                 |
| `just test`          | `uv run pytest`。                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |

`build` 和 `clean` 是同一个驱动器 `batch.py` 的两个互逆动词：共用角度（`domain`/`skill_zh`，
clean 另接受 `all`）和同一个清单顺序窗口；build 创建，clean 删除。`meta` 是该驱动器的第三个
动词——同一份清单读成仓库与 owner（`owner/repo`、`owner`），`meta --clean` 是其逆操作。`sync` 是
该驱动器的另一个子命令。

| 变量           | 默认                                                     | 含义                                                                                                          |
| -------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `limit`        | `1`                                                      | 按清单顺序接下来 N 个还缺当前角度产物的 skill；`0` = 全部。默认一个，所以裸 `just` 是冒烟。数工作量不数位置。 |
| `jobs`         | `32`                                                     | 同时在飞的生产者调用数：驱动器的线程池。                                                                      |
| `dry`          | –                                                        | `1` = 假端点、真实目录结构：不调用任何东西。                                                                  |
| `output_dir`   | `output`                                                 | 发布根目录：各 skill（连带写在其旁的角度文件）、清单和 README。                                               |
| `listing`      | 镜像 `dist` 分支上的清单 url                             | 镜像的清单，由 `just sync` 现取；测试用本地 `file://` url 离线跑。                                            |
| `repo_tarball` | `https://codeload.github.com/{owner}/{repo}/tar.gz/HEAD` | 批次从哪里取一个仓库的 tarball；`{owner}`、`{repo}` 按仓库替换，测试用 `file://` 模板离线跑。                 |
| `fetch_jobs`   | `16`                                                     | 同时在传的仓库 tarball 数：下载器的池子。                                                                     |
| `py`           | `uv run python`                                          | 怎么跑这些脚本（CI 里用绝对解释器路径覆盖）。                                                                 |

这些旋钮是 `just` 变量——只在命令行设置，别无他处：`SKILLS_PROFILES_LIMIT=20 just` *不*生效。
`.env` 属于脚本，装两个端点和它们的密钥；justfile 导出 `output_dir`、`prompts_dir` 和 `dry`，
这个导出是两者之间唯一的交接。

因为产出没有任何前置条件，**它的存在就是全部缓存**——驱动器逐 skill 检查角度文件，所以半途
停止的批次从第一个缺失的文件恢复，绝不重建已有的。一个 profile 里的两个文件各自缓存——domain 标
签不算 zh 页面，zh 页面也不算标签。这有三个值得明说的后果：

- **失效即 `clean`。** `just clean <angle>`（或 `rm` 掉
  `output/skills/<id>/` 里的某个角度文件）删掉产出；下次跑该角度时重新生成。改 prompt 文件
  （`_system.md`、`translate.md`、`translate_user.md`）本身*不*会让任何东西失效——否则每次
  checkout 移动 mtime 都会免费重标整个数据集。
- **源只拉取一次。** 仓库会在第一个构建它的某个 skill 的任务里下载，且磁盘上的仓库目录就是缓存：`just sync`
  不动源，所以源只在它的仓库目录被删掉时才改变。sync 会做的是：把新版清单给某仓库新增了 skill 的
  那些仓库重新拉取一次，把新源合并进来，并对镜像删掉的每个 skill 提一行——文件留在树里，去留由人决定。
  镜像列出、但其仓库不含该 skill 的源的 skill 永远构建不了，窗口据此
  跳过它而不是反复重试。
- **单个 skill 失败不会结束整批。** 任务失败（配额、连接等）会按 id 报出来，不写入文件，池子继续处理；
  CI 会记录错误详情并发布已经成功生成的产物。下一轮会重试仍缺少文件的 skill。窗口内全部任务都失败
  则是一次坏掉的运行：批次退出 `1`，部分产出照常保留。

## 脚本

一个活一次生产者调用。两个命令做的事其实是同一个命令——`common.py` 里的共享骨架（`run`）：
解析唯一的 skill 参数、读源、以 description 为门槛、构造该角度要发的全部请求（只构造一次）、
调用、把该角度的一个文件原地改名写好，并把失败变成一行 stderr 和一个状态码。每个生产者只提供
三样东西：请求们、回答它们的调用、dry-run 占位值。domain 角度：

```bash
uv run python jev.py <owner>/<repo>/<dir>           # 精确标注一个 skill
uv run python jev.py <owner>/<repo>/<dir> --print   # 打印请求就停，什么都不调用
```

`jev.py` 故意没有“存在则跳过”的检查：决定建什么是 `batch.py` 的职责。它与调用方的完整契约是：

- **`<skill>`** 是 `<output_dir>/skills` 下的一个 skill 目录：其 id 里的 `:` 和 `&` 写作 `_`，
  镜像自己的树就是这么命名的。
- **产出**落在 `<output_dir>/skills/<skill>/domain.json`，原地改名写入——写了一半的文件会被
  下一批当成已完成而跳过。
- **源在 20 000 字符处截断**，在换行处下刀，并声明被截断。
- **description 取 front matter 的 `description`**，按 YAML 解析，它是 skill 的门槛：缺失、无法
  解析或没有 description 的头会丢弃该 skill——不调用、不写角度文件、stderr 一行、状态 1。批次
  不会走到这一步：`fetch.py` 只写能读出 description 的源，所以这种 skill 没有 `SKILL.md`，窗口
  会跳过它。
- **状态码**：0 已建，1 输入或端点不可用，2 参数错误。失败是一行而不是 traceback，因为几千个
  失败的批次里 traceback 不再是信息。

端点不是聊天型的：`POST /v1/systemone` 接收 `state` 和类型化 `questions`，回答类型化 `answers`
——没有 messages、没有 `json_schema`、没有自由文本。`state` 由模板 `prompts/_system.md`
渲染：skill 的名字、description、去掉 front matter 的 `SKILL.md` 正文，以及 `domain` 独有的一层
——skill 所属仓库，即其旁系 skill 的一句话描述，每条截成提示、数量封顶 50——因为分类是仓库的
属性而不是单个文件的属性，旁系能为孤立、含糊的 skill 消歧。分类法在代码里是一个对象：
`CRITERIA`（13 个分类及其措辞）和 `INSTRUCTION`（唯一的规则：判断 skill 是干什么的，而不是它
怎么实现的），作为答案被限定的 `criteria` 交给端点——所以没有 schema 里的 enum，也不需要保持同
步的解码器。完整回答被保留——标签、确信度和在全部 13 个分类上的分布；清单取前两者，其余留在
profile。端点闲置后的第一次调用常被丢弃（表现为超时），会重试；被拒绝的请求体（400）不重试。

zh 页面角度就是聊天那一个：

```bash
uv run python skill_zh.py <owner>/<repo>/<dir>           # 精确构建一份中文页面
uv run python skill_zh.py <owner>/<repo>/<dir> --print   # 把全部请求打印成一个 json 数组
```

`skill_zh.py` 和它调用的聊天库 `translate.py` 共用同一个 `common.Config`：
共享配置（超时、重试、dry-run、路径），三个类型化端点的配置，以及旁边的翻译配置。真正不同的只有
调用：标准的 OpenAI 兼容 `POST {base}/chat/completions`，Bearer 密钥、`temperature` 0，两段话从
`prompts/translate.md` 和 `prompts/translate_user.md` 用代码固定的唯一目标语言渲染——一条忠实
翻译的 system 指令（保留含义、语气、段落与有效格式；代码和占位符原样不动；沿用给出的上下文与
术语），以及承载待翻译文本的 `Translate to …:` user 段。深度思考默认开启：MaaS 扩展字段
`enable_thinking: true` 加上 `max_tokens: 32768`（文档上限——端点自己的 2048 默认会把推理截
断）。模型先把推理写进 `reasoning_content`；这份草稿永不读取（`translation()` 只取
`choices[0].message.content`），也永不写入角度文件——两个旋钮都是配置项：
`TRANSLATE_ENABLE_THINKING`、`TRANSLATE_MAX_TOKENS`。描述是 Jinja 变量、永远不是模板文本的一
部分，所以 skill 自己那句话里的花括号只是数据。它只发描述——不发 `SKILL.md`，没有截断。
`choices[0].message.content` 就是完整回答：空响应是端点不可用，而不是空翻译。重试规则在
`common.py` 里，与 domain 角度共用：瞬时状态码和连接错误指数退避，4xx 立即失败。默认值指向讯
飞星辰 MaaS 上的 Spark-X2.5-4B；控制台显示的模型 id 可能不同，因此留了环境变量覆盖。这就是
`translate.py`，它是库而不是命令——`skill_zh.py` 是它唯一的调用者。

`skill_zh.py` 与它共享命令形状——相同的命令行、相同的门槛、相同的退出码、相同的原地改名写入——
并按顺序发出页面所需的每一次调用：先描述，后正文。正文不带 front matter，从
`prompts/skill_zh.md` 和 `prompts/skill_zh_user.md` 渲染。正文超过单次回答所能时，按其自身的
Markdown 缝合线切块（代码围栏外的空行；自身没有缝合线的块在行间切）为不超过 `MAX_CHUNK_CHARS`
字符的小块，逐块经同一端点及其兜底各自调用翻译，每块带着它被切开的那道缝合线——所以行间切开的
块按行自己的换行拼回，被切的表格或列表回来还是原来那一块。页面随后由代码组装——front matter 为
`name`（源自己的）加中文 description，下面是各块沿各自缝合线拼回的结果——且只有每一次调用都回
来才写入：半截翻译的页面绝不能冒充完整的一页，而 front matter 是页面里唯一严格解析的部分，所以
绝不交给模型。空正文和缺 description 一样，丢弃该 skill：不调用、不写文件——走与其他不可用输入
相同的一行 stderr/退出码 1 闸门，而不是 traceback。页面的请求只构造一次，`--print` 与实际运行
共用。

`index.py` 把镜像的行与树拼接，写 `output/skills.jsonl`。它的命令行就是离线动词——不接参数，
已有清单本身按同一顺序携带安装量；驱动器 sync 在进程内用新清单调用同一个 `build()`，让新
安装量拼进来，两者之间不再隔一个进程。每行先带镜像字段，然后是 `description`、`description_zh`、`domain` 和
`confidence`——各角度从自己的文件读出，互相独立、也各自缺失（中文页面留在自己的 skill 目录里；
没有时消费者回退原文），而镜像列出的每个 skill 都是一行，其拼接字段在树拉取并构建前为 `null`；
仓库已在盘上、却解析不出可读 description 的行则整行去掉——任何一轮都无法构建它。
同一次运行写 `output/README.md` 和它的中文双胞胎——`readme.py` 装措辞，`index.py` 给数字——即清单
回答不了的那件事：**数据集建了多少**（domain 覆盖率、zh 页面覆盖率，以及伴随的仓库与 owner 覆盖率）。

`fetch.py` 是另一侧：驱动器下载窗口涉及的仓库——即将构建的每个 skill 的 `owner/repo`，每个仓库
一个 codeload tarball（`--repo-tarball` 指明地址），`fetch_jobs` 路并发，且只下载尚未在磁盘上
的那些——随后 `fetch.py` 流式解包每个 tarball。一个 skill 是子目录里的一个 `SKILL.md`，落在它所在的
目录、原名不改；子目录里没有任何 skill 的仓库本身就是单个 skill，根目录的 `SKILL.md` 就是它的源，
留在根上，而子目录 skill 旁的根 `SKILL.md` 仍是 readme。只有能读出 description 的源才会落盘，且
同一目录只取一次。某个目录属于哪一行清单，由 front matter `name`——镜像为每个 skill 发布的字段——
与该仓库所含源匹配而定，每仓库扫一次并记住；清单行的 `dir` 字段携带答案，也是交给 `jev.py` 的句柄。这里不查清单——清单还没
列到的 skill 也照样解出来。仓库目录总会创建，所以它的存在就是缓存：某仓库不含某列出 skill 的
源，就把该 skill 留作空目录。下载不下来的仓库干脆不在——它的 skill 失败，批次继续。GitHub 回答
404/410 的仓库是彻底消失（已删除或转私有），仓库目录仍会创建作为标记，其 skill 之后的每轮运行都
被跳过，而不是反复拉取、反复失败。

`meta.py` 是第三个生产者，但作用于实体而非 skill。清单按 `owner/repo` 读出——即仓库名册，顺序不变
——一个仓库一次 GitHub 调用：`GET {api}/repos/{owner}/{repo}`，其载荷被整形为 `repos.jsonl` 的一行
（由 `batch.py` 按清单自身顺序合并），并带有 owner，其头像由 `common.write_bytes` 写到固定的
`owners/<owner>.png`。从仓库而非 `/users` 读 owner，正是改名后仍能拿到头像的原因（`/repos` 跟随改名，
`/users` 返回 404）；头像的存在就是它全部的缓存，缺一个就重读一次仓库。
每个请求都带 `Accept: application/vnd.github+json`、GitHub 非有不可的 `User-Agent`，以及设了
`SKILLS_PROFILES_GITHUB_TOKEN` 时的 Bearer token。窗口与池属于 `batch.py`；整形属于 `meta.py`
——`headers()`、URL 构造器、`repo_row()`、`repo_gone_row()` 和 `build_repo()`。

## 工作方式

```
                        output/  ── 整个产物，作为一个目录发布
                          │
镜像 `dist` 清单 ─────────┼──► skills.jsonl         清单：镜像列出的每个 skill 一行，也是各批次
   （batch sync 拉进    │                          工作的顺序（安装量降序）
    来、从不保留）       │
                          ├─► batch.py 把清单当 jsonl 遍历
                                      │
                        跑生产者，一次 JOBS 个，每个 skill 一次生产者调用，各自按需拉取仓库
                        （每个仓库一次——仓库目录即缓存）；domain 与 skill_zh 共用同一个池子
                                      │
                        skills/<id>/SKILL.md + domain.json + SKILL.zh.md（仓库目录即缓存）
                                      │
                index.build() ──► skills.jsonl + README：镜像的行 × 各角度文件
```

驱动器是薄 just 启动器背后的普通 Python 模块，不是构建系统：**存在即跳过**，顺序直接按 jsonl
读出镜像自己的顺序（所以仓库名里的前导点和 `_` 不再需要 shell 技巧），池子是 `jobs` 个 worker
的 `ThreadPoolExecutor`，每个 worker 在本进程内跑一次生产者调用——没有 jobserver，也没有每分钟
限速；每个 worker 上一个 skill 一结束就接下一个，瞬时 429 由客户端自己的指数退避吸收，且带抖
动，被限流的池子不会在同一时刻齐刷刷地再敲门。

## 项目布局

```
justfile                # 薄启动器：每个配方设置旋钮并运行 batch.py 或单个脚本
batch.py                # 编排器：jsonl 开窗、懒拉取、生产者池、sync
common.py               # 两个生产者共用的内核：Config、目录树、源读取、prompt、带重试的调用、
                        # 原子写，以及 run() 命令骨架
fetch.py                # 源层：仓库的 skill 解包进 skills/，每个一次
jev.py                  # domain 角度：分类法、state、类型化问题
meta.py                 # skill 之上的实体：仓库与 owner 的 GitHub 资料，含头像，
                        # 写进 skills 旁的两棵树
translate.py            # 翻译库：一次聊天调用，套在共享命令之上
skill_zh.py             # 页面角度：SKILL.md 正文的翻译，写一个 .md
index.py                # 清单及其数字：一行一个 json，以及 README 用的事实
readme.py               # 页面：把那些数字说给读者，双语
prompts/_system.md        # state 模板：name、description、正文和 repository 块
prompts/translate.md      # 翻译 system 模板：忠实翻译任务，{{to}}
prompts/translate_user.md # 翻译 user 模板：承载 {{text}} 的 “Translate to {{to}}:”
prompts/skill_zh.md       # 页面 system 模板：翻译文档、保留格式
prompts/skill_zh_user.md  # 页面 user 模板：承载正文的 “Translate to {{to}}:”
tests/                  # 离线单元测试；批处理在 test_batch.py 里进程内驱动，
                        # 只有 justfile 启动器的检查会真的跑 `just`
.github/                # 每次 push 和 PR 跑 ci；sync、meta、publish 与 invalidate 手动触发
```

## 配置

解析顺序（高到低）：`SKILLS_PROFILES_*` 环境变量 → 本地 `.env` → 内置默认值。空值表示“未设置”。

| 变量                                          | 默认值                      | 含义                                                                                                  |
| --------------------------------------------- | --------------------------- | ----------------------------------------------------------------------------------------------------- |
| `SKILLS_PROFILES_API_KEY`                     | –                           | 类型化端点的密钥；没有密钥就不调用                                                                    |
| `SKILLS_PROFILES_BASE_URL`                    | TypeSafe 的 System One 路径 | `jev.py` 发往哪里；别的都不发                                                                         |
| `SKILLS_PROFILES_MODEL`                       | `jev-latest`                | System One 模型，固定版本之上的别名                                                                   |
| `SKILLS_PROFILES_TRANSLATE_API_KEY`           | –                           | 聊天端点的密钥；`translate.py` 是唯一调用方                                                           |
| `SKILLS_PROFILES_TRANSLATE_BASE_URL`          | 星辰 MaaS v2 根地址         | OpenAI 兼容根地址；`translate.py` 发往 `{base}/chat/completions`                                      |
| `SKILLS_PROFILES_TRANSLATE_MODEL`             | `spark-x2.5-4b`             | 聊天模型 id；以控制台服务页显示的拼写为准                                                             |
| `SKILLS_PROFILES_TRANSLATE_ENABLE_THINKING`   | `true`                      | 发送 MaaS 的 `enable_thinking` 开关；模型先推理再作答（`reasoning_content`）                          |
| `SKILLS_PROFILES_TRANSLATE_MAX_TOKENS`        | `32768`                     | 回答的 token 预算，含推理；端点自己的默认值只有 2048                                                  |
| `SKILLS_PROFILES_TRANSLATE_TIMEOUT`           | `120`                       | 聊天端点单独的每次请求秒数：思考调用先推理，常常超出类型化端点的耐心，所以它有自己的旋钮              |
| `SKILLS_PROFILES_TRANSLATE_FALLBACK_API_KEY`  | –                           | 兜底端点的密钥；不设即关闭兜底——失败的 skill 照旧失败                                                 |
| `SKILLS_PROFILES_TRANSLATE_FALLBACK_BASE_URL` | Agnes AI 根地址             | 聊天端点失败的 skill 在此重试一次：同样的 OpenAI 兼容调用，只换掉 model 一个字段，并去掉 MaaS 专属的思考开关 |
| `SKILLS_PROFILES_TRANSLATE_FALLBACK_MODEL`    | `agnes-3.0-flash`           | 兜底模型 id；推理模型，读法相同（`content` 之外的 `reasoning_content`）                               |
| `SKILLS_PROFILES_TIMEOUT`                     | `20`                        | 类型化端点的每次请求秒数：一到三秒回答，闲置后首个调用会被丢弃                                        |
| `SKILLS_PROFILES_MAX_RETRIES`                 | `3`                         | 额外重试次数，针对丢弃的调用或繁忙的网关；两个端点通用                                                |
| `SKILLS_PROFILES_GITHUB_TOKEN`                | –                           | `meta.py` 用的 GitHub token：没有它匿名客户端每小时仅 60 次                                          |
| `SKILLS_PROFILES_GITHUB_API_URL`              | `https://api.github.com`    | 读取实体资料用的 GitHub API 根；`file://` 根是测试离线跑它的方式                                      |
| `SKILLS_PROFILES_DRY_RUN`                     | `false`                     | 两个生产者都用假的：不发 API 调用                                                                     |
| `SKILLS_PROFILES_OUTPUT_DIR`                  | `output`                    | 发布根目录：各 skill（连带写在其旁的角度文件）、清单和 README                                         |
| `SKILLS_PROFILES_PROMPTS_DIR`                 | `prompts`                   | 放 `_system.md`、`translate.md`、`translate_user.md`、`skill_zh.md` 和 `skill_zh_user.md` 的目录      |

## 测试

套件离线：`conftest.py` 写一棵假快照树，构造真实 HTTP 客户端会响亮地失败，所以即使本地 `.env`
装满真密钥也没有测试能偷偷联网。

- `tests/test_common.py` 覆盖两个生产者共用的部分：源读取（front matter、YAML description、
  20 000 字符截断）、仓库旁系及其封顶、prompt 文件、原子写，以及重试规则（丢弃的调用重试、被
  拒绝的不重试）。
- `tests/test_jev.py` 覆盖 domain 角度本身：作为单一对象的分类法、调用发送的请求体（state 加
  类型化问题，无 messages）、封闭集之外答案的守卫、仓库进入 state，以及命令本身——门槛、退出码、
  无需密钥打印请求。
- `tests/test_translate.py` 覆盖页面角度调用的聊天库：请求体（两个 prompt 文件渲染成 system 和
  user 两段）、描述作为 Jinja 值传入、URL 拼接和 Bearer 头、带重试的调用（丢弃的重试、被拒绝的
  不重试）、回答解析（空或截断的被拒），以及兜底端点的交接。
- `tests/test_index.py` 覆盖清单和数字（镜像列出的每个 skill 一行、字段在构建前为 `null`，以及
  `description_zh` 独立拼接）；`tests/test_readme.py` 覆盖双语页面；`tests/test_batch.py` 进程内
  驱动 `batch.py`——窗口、懒加载（仓库只拉取一次、失败只影响它的 skill）、单 skill 失败日志、
  `sync`，以及删除即失效——全部对着本地 `file://` tarball。只有启动器检查（默认配方、
  dry 旋钮只认命令行、池子参数到达命令行）仍以子进程跑 `just`。
- `tests/test_meta.py` 覆盖实体：整形（仓库行与 `gone` 行）、固定的头像路径、两个窗口与 `--clean`、清单合并——全部对着 `file://` GitHub 根，所以没有测试联网。
- `tests/test_skill_zh.py` 覆盖页面角度：请求们（描述在前、正文各块在后；正文作为 Jinja 值传入、
  front matter 绝不外发）、产出（原样发布的 front matter 加译文，一个 `SKILL.zh.md`）、长度门槛，
  以及命令本身——退出码、无需密钥打印请求数组。

```bash
uv run pytest                                # 离线测试套件
uv run ruff check .                          # lint
uv run mypy                                  # 类型
just dry=1 limit=2 build domain              # 批处理本身，端到端
just dry=1 build skill_zh                    # 第二个批次，端到端
uv run python jev.py <owner>/<repo>/<dir> --print   # 仅开发：不调用，只看请求
```

故意没有 `just render`：打印请求是仅开发用的检查，保留为直接运行的脚本开关，justfile 只放生产动词。

## CI

五个 workflow，每个都很薄：它们做的活就是 `just`。

| workflow      | 触发            | 作用                                                                                                                                                                                                                                                        |
| ------------- | --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ci.yml`      | 每次 push 和 PR | `uv sync`、`ruff check .`、`mypy`、`pytest`，装了 `just`。离线。                                                                                                                                                                                            |
| `sync.yml`    | 手动            | `restore-dist` → `just sync` → `publish-dist`（`date`）。拉取镜像清单并重写清单文件；不调用模型。                                                                                                                                                           |
| `meta.yml`    | 手动            | `restore-dist` → `just meta` → `just index` → `publish-dist`（`date`）。补齐还缺的仓库资料与 owner 头像；不调用模型，只用 GitHub token（PAT 或内置的）。                                                                     |
| `publish.yml` | 手动            | `restore-dist` → 对所选 `angle`（`domain`、`skill_zh`，或 `all` 共池一次跑完）跑 `just build <angle> limit=… jobs=…` → `just index` → `publish-dist`（`date-counter`）。需要所选角度各自的 secret 和变量。 |
| `invalidate.yml` | 手动         | `restore-dist` → `just limit=0 clean <angle>` → `just index` → `publish-dist`。忘掉所选角度的全部已建产出——远程唯一的失效入口，分类法或 prompt 变更时运行——并发布删掉它们之后的树；不调用模型。下一次 publish 从零重建该角度。 |

文档规则：每份英文文档都有中文对应版——同一次修改保持两者同步。
