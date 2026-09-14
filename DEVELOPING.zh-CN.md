# 开发 skills-profiles

[README.zh-CN.md](README.zh-CN.md) 里那份数据的生成器：它从
[skills-sh-mirror](https://github.com/skill-one/skills-sh-mirror) 读取每个 skill 的 `SKILL.md`，
按七个角度让 OpenAI 兼容的 LLM 产出结构化档案，并据 `persona.tool` 直接渲染出工具头像配图，发布到本
仓库的 `dist` 分支。

English: [DEVELOPING.md](DEVELOPING.md)

## 快速开始

需要 Python 3.12+ 和 [uv](https://docs.astral.sh/uv/)；凭据放在本地 `.env`
（复制 [`.env.example`](.env.example)——除镜像、你自己的端点，以及渲染配图时的图像端点外，不访问
任何网络）。

```bash
uv sync
skills-profiles sync            # 下载上游快照（tag 未变则跳过）
skills-profiles run --limit 10  # 生成档案 + 渲染就绪的配图，按安装量从高到低
```

想离线走通全流程、不调任何 API：`skills-profiles run --limit 5 --dry-run`（文本 + 占位配图）。

## 命令行

| 命令                                                                      | 作用                                                                                                                                                                                                                                                                                                                                                                                                 |
| ------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `sync [--refresh]`                                                        | 先读上游一行的 `latest` 指针得知最新 tag，再把该 ref 作为一个 tarball 拉到 `cache/skills-sh`，只解压 `skills.jsonl` 和每个 `SKILL.md`。tag 记在 `SNAPSHOT.json`，未变则跳过下载（`--refresh` 强制）。从不碰产物。                                                                                                                                                                                    |
| `run [--limit N] [--prompts a,b] [--concurrency C] [--dry-run] [--debug]` | 把 skill 补到完整，按安装量排序取 N 个（`0` = 所有有缺口的）。一个 skill「完整」= 所有 prompt 已缓存且 `cover.png` 已画出——选择同时计入两半，run 先补缺失文本，再渲染本轮选中 skill 缺失的配图，按 `SKILLS_PROFILES_IMAGE_RATE_LIMIT` 张/分钟/key 限速。什么都不缺的、以及快照里没有 `SKILL.md` 的 skill 会被跳过且不占名额；没有 `SKILLS_PROFILES_IMAGE_API_KEY` 时渲染阶段会告警并跳过，而非报错。 |
| `invalidate [--skill ID]... [--prompts a,b] [--stale] [--all]`            | 删除缓存输出，让下一次 `run` 重算。`--stale` 选上游 hash 变化或已从快照消失的 skill（先 `sync`）。无任何筛选条件时必须显式 `--all`。失效一个 prompt 会连同它在 DAG 里的下游 prompt 和各自资产一起删掉：`persona` 级联到 `cover`，这正是重画一张配图的途径。                                                                                                                                                                                   |

重算从来不是 `run` 的参数：`invalidate` 删，`run` 补。单个 skill 的失败会被隔离：run 继续，已完成的
prompt 保留并随本轮发布，只有全军覆没才以非零码退出。图像请求按 key 限速——每个 key 每分钟最多
`SKILLS_PROFILES_IMAGE_RATE_LIMIT` 张（`0` 表示不限），大批量时会排队等待，而不是攒一堆 429。

所有命令都工作在同一道数据集封顶之内，即 `SKILLS_PROFILES_TOTAL_LIMIT`（默认 1000）：无论单次 run 的
`--limit` 多大，只有安装量最高的前 N 个 skill 会被生成档案或绘制配图。它是排名窗口而非「完成了多少个」
的计数——排在前面但还有缺口的 skill 会占着名额，所以重跑和 `invalidate` 重画都复用同一批 N 个。

## 工作原理

```
镜像 dist 分支 tarball ──► cache/skills-sh (skills.jsonl + skills/<id>/SKILL.md)
                                 │
                                 └─► 按安装量取 --limit 个仍有缺失的 ──► 每 skill 执行 prompt DAG
                                        ──► output/skills/<id>/<prompt>.json
                                        ──► output/skills/<id>/md/<prompt>.md
                                        ──► output/skills.jsonl (id + hash + domain + persona)
                                persona.json ──► `run` 的后置阶段
                                                ──► output/skills/<id>/cover.png
```

`output/`（产物）与 `cache/skills-sh`（上游数据）是两个独立根目录：从上游取到的东西永远不会写进产物
目录。Prompt DAG（边表示「依赖其输出」）：

```
domain   scenario   blackbox   whitebox   tagline   persona   comments   （全部是根节点）
                                                                   └─► cover   （唯一一条边）
# 在 frontmatter 里加 `depends_on: [scenario]` 即可串联
```

关键设计决策：

- **不引入编排框架** —— DAG 排序用 Python 标准库
  [`graphlib.TopologicalSorter`](https://docs.python.org/3/library/graphlib.html)。
- **结构化输出** —— 每个 prompt 在 frontmatter 的 `output:` 声明一个 pydantic schema，LLM 调用经
  [instructor](https://python.useinstructor.com/) 走 OpenAI 兼容客户端；schema 与 13 个取值的
  `Domain` 分类体系都在 `models.py`。
- **基于文件的断点续跑** —— 每个 prompt 的输出是自己的 `<prompt_id>.json`（`md/` 下有 markdown
  副本），一生成即落盘：存在且通过 schema 校验就不调 LLM。先写 markdown 再写 json，所以崩溃只会留下
  多余的 markdown，不会出现没有副本的 json。续跑粒度是 prompt 级。
- **索引是投影** —— `skills.jsonl` 每次全量重写、内容来自磁盘，所以行不可能与文件漂移；它是
  `invalidate --stale` 比对 hash 的依据。
- **配图 = 配方 + 渲染** —— DAG 里有一个配方 prompt（`cover`，输入 `persona.tool`），把中文工具名
  翻译成一段英文画面主体描述；`images.py` 随后拼接统一的英文风格尾段（`COVER_STYLE`）与改写为
  正向 "no ..." 短语的禁用内容（`NEGATIVE_PROMPT`）——图像端点 Agnes Image 2.5 Flash 不支持
  `negative_prompt` 字段，禁令只能随正向提示词一起发送。
  `cover.png` 在 `PROMPT_ASSETS` 里登记为 `cover` 的资产，所以失效配方会把 json 和配图一起删掉，
  而失效 persona 会级联到 cover（新的工具名不能留旧配方）。配图的缓存就是文件本身是否存在，
  因为接口返回的 url 会过期——存下来的是字节，url 从不保存——而重渲染不花 LLM 调用。
- **一次请求拿整个快照** —— `sync` 用 codeload 把分支作为一个 tarball 下载，只解压真正会读的内容，
  并整包替换上一次快照。上游每天为抓取结果打 tag，并在根目录放一行 `latest` 指针指向最新的那个，因此
  重复 sync 只有当指针指向的 tag 本地还没有时才下载；在 CI 里快照从我们自己的 `dist` 恢复。
- **Prompt 即文件** —— `prompts/` 下一个 markdown 文件一个 prompt，文件名即 prompt id：YAML
  frontmatter 存元数据，正文是 jinja2 用户提示词模板，`_system.md` 是共享 system prompt。

### 局部重跑

`run --prompts <id>` 先算目标 prompt 的依赖闭包，只生成闭包里缺失的部分：依赖属于输入，因此复用已存的
json，仅在缺失或 schema 校验失败时重算。闭包之外完全不动；某 skill 若一个输出都不剩，会从
`skills.jsonl` 除名。失效一个 prompt 时，它在 DAG 里的所有下游 prompt（`persona` 会级联到 `cover`）
连同各自登记的资产一起删掉——`invalidate --prompts persona` 后再 `run`，工具名、配方和配图会一起补上。
配图的两半在生成侧也是一个整体：`run --prompts cover` 一条命令重生成配方（缺 persona 时连带补上）
并渲染图片。

## 新增一个 prompt

一个 markdown 文件就是一个 prompt——除非需要新的输出 schema（那就在 `models.py` 注册），不必改代码：

```markdown
---
description: 一行说明
output: IntroText # models.py 中注册的 pydantic schema
depends_on: [scenario] # DAG 依赖; 根节点可省略
---

请为下面的 skill 写……
{{ deps.scenario.text }} # deps 将 prompt id 映射到其解析后的输出对象
```

`_system.md` 提供 `{{ skill.name }}`、`{{ skill.description }}` 和完整的 `{{ skill_md }}`
（截断到 20,000 字符），因此 prompt 文件只需描述任务本身。然后为所有 skill
补这一角度——已缓存的角度会复用，只有新角度花钱：

```bash
skills-profiles run --prompts my_angle --limit 0
```

把 prompt id 加进 `outputs.py` 的 `AGGREGATED_PROMPTS`，它就会折进每一行 `skills.jsonl`；若它拥有
非 json 的产物，在同一个文件里的 `PROMPT_ASSETS` 登记资产文件名——`cover` 就是这样持有
`cover.png` 的，也正因如此，失效这个 prompt 时会连同渲染出的产物一起丢弃。

## 项目结构

```
prompts/             # 每个 prompt 一个 md 文件（+ _system.md）
src/skills_profiles/
├── data.py          # 镜像指针 + tarball + 索引解析 + 过期判定
├── models.py        # Domain 分类体系 + 输出 schema
├── prompts.py       # frontmatter + DAG 排序 + jinja2 渲染
├── generate.py      # 异步 DAG 执行 + 断点续跑 + 覆盖率
├── outputs.py       # json/md 输出 + 附带文件 + 索引 + 失效
├── layout.py        # 快照与产物共用的文件/目录名
├── llm.py, images.py    # API 客户端 + 离线 FakeLLM / FakeImages
└── config.py, logging.py, cli.py
tests/               # 离线 fixture + 端到端 CLI 测试
```

## 配置

优先级从高到低：`SKILLS_PROFILES_*` 环境变量 → 本地 `.env` → 内置默认值。

| 变量                               | 默认值                           | 说明                                                                                    |
| ---------------------------------- | -------------------------------- | --------------------------------------------------------------------------------------- |
| `SKILLS_PROFILES_MODEL`            | `gpt-4.1-mini`                   | 任意 OpenAI 兼容模型                                                                    |
| `SKILLS_PROFILES_BASE_URL`         | 无                               | OpenAI 兼容端点                                                                         |
| `SKILLS_PROFILES_API_KEY`          | 无                               | 端点 API key                                                                            |
| `SKILLS_PROFILES_LIMIT`            | `10`                             | 每次 run 生成的 skill 数（`0` = 全部；已缓存的跳过不计数）                              |
| `SKILLS_PROFILES_TOTAL_LIMIT`      | `1000`                           | 整条管道服务的 skill 数，按安装量从高到低——是对数据集的封顶、不是单次 run（`0` = 全部） |
| `SKILLS_PROFILES_CONCURRENCY`      | `2`                              | LLM 调用 / 图像请求的最大并发数，跨 skill 及 skill 内 prompt 共享                       |
| `SKILLS_PROFILES_OUTPUT_DIR`       | `output`                         | 产物目录                                                                                |
| `SKILLS_PROFILES_DATA_DIR`         | `cache/skills-sh`                | 上游数据目录                                                                            |
| `SKILLS_PROFILES_PROMPTS_DIR`      | `prompts`                        | prompt markdown 目录（含 `_system.md`）                                                 |
| `SKILLS_PROFILES_IMAGE_BASE_URL`   | `https://apihub.agnes-ai.com/v1` | 文生图端点；配图由一个自成一套的服务绘制                                                |
| `SKILLS_PROFILES_IMAGE_API_KEY`    | 无                               | 它的 key（没有时 `run` 会告警并跳过渲染阶段；`--dry-run` 则不需要）                     |
| `SKILLS_PROFILES_IMAGE_API_KEYS`   | 无                               | 追加的 key，逗号分隔：每个 key 独享自己的每分钟配额，N 个 key 即 N 倍速率               |
| `SKILLS_PROFILES_IMAGE_RATE_LIMIT` | `0`                              | 每分钟每 key 允许的最多图像张数；端点未公布配额，默认不限速                             |
| `SKILLS_PROFILES_IMAGE_MODEL`      | `agnes-image-2.5-flash`          | 端点提供的任意模型                                                                      |
| `SKILLS_PROFILES_IMAGE_SIZE`       | `1024x1024`                      | 精确尺寸；端点也接受 `1K`/`2K`/`3K`/`4K` 档位，冷门尺寸会被自动归一化                   |

## 发布（GitHub Actions）

[`ci`](.github/workflows/ci.yml) 在每次 push 与 pull request 上做检查（测试、lint、类型）；下面的
手动触发工作流共用同一个发布锁（`concurrency: publish-dist`）：

| 工作流                                         | 流水线                                                  | Tag                                                    |
| ---------------------------------------------- | ------------------------------------------------------- | ------------------------------------------------------ |
| [`sync`](.github/workflows/sync.yml)           | 恢复 dist → 同步上游 → `invalidate --stale` → 发布      | `dist-YYYY-MM-DD`（同日内 force 覆盖）                 |
| [`generate`](.github/workflows/generate.yml)   | 恢复 dist → `run --limit <输入，默认 10>` → 发布        | `dist-<base>-N`（base = 最近一次 sync 的 tag，N 递增） |
| [`invalidate`](.github/workflows/invalidate.yml) | 恢复 dist → `invalidate --prompts [--skill …]` → 发布 | `dist-<base>-N`（与 `generate` 同一计数）        |

```bash
gh workflow run generate.yml -f limit=50 -f concurrency=8   # 补完整 50 个 skill（文本 + 配图）
gh workflow run sync.yml                                     # 刷新上游，丢弃过期档案
gh workflow run invalidate.yml -f prompts=cover              # 重做全部封面（配方 + 配图）
gh workflow run invalidate.yml -f prompts=persona            # 重做全部 persona（级联到 cover）
```

两条工作流共用 [restore-dist](.github/actions/restore-dist/action.yml)（一个 codeload 请求把分支拉回
到 `output/` 和 `cache/`，跳过根目录指针——每次发布都会重写它，管道从不读它）与
[publish-dist](.github/actions/publish-dist/action.yml)（把工作目录镜像回 `dist`、写入根目录的 `latest`
指针标明本次 tag、给 `stats.json` 盖章写入 `publishedAt` 与数据集来自镜像的哪个 tag、打 tag、按
时间窗剪枝）。指针和章都在 commit 之前写入，所以快照与它的身份一起发布；只有 `latest`、tag、`HEAD`
三者一致、且已发布的 `stats.json` 章还在时该步骤才算成功——镜像 tag 由数据集自己的 marker 派生，所以
不论哪条工作流发布它都不会滞后于数据；又因为 [stamp-stats.sh](.github/actions/publish-dist/stamp-stats.sh)
能把章再剥掉，只改了时间戳的一轮什么都不发布。`dist` 是唯一的原子快照
——根目录是档案，外加 `cache/skills-sh/` 数据集镜像——所以**只有 `sync` 会碰上游**，而 `generate` 只读
上一次 `sync` 发布的数据集并增加二进制体积：`limit` 封顶单批，`SKILLS_PROFILES_TOTAL_LIMIT` 封顶数据集，
所以是这道封顶（而非任何单次 run）决定了 `dist` 最多能装多少张配图。历史按滚动时间窗剪枝
（默认 `1 month`）。

需在 Settings → Secrets and variables → Actions 配置：

| 位置     | 名称                                                                                          | 示例                                                   |
| -------- | --------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| Secret   | `SKILLS_PROFILES_API_KEY`                                                                     | 端点对应的 API key                                     |
| Secret   | `SKILLS_PROFILES_IMAGE_API_KEY`                                                               | 文生图端点的 key（可选：没有时 `generate` 仍是纯文本） |
| Variable | `SKILLS_PROFILES_BASE_URL`                                                                    | `https://api.b.ai/v1`                                  |
| Variable | `SKILLS_PROFILES_MODEL`                                                                       | `GLM-5.3-Flash`                                        |
| Variable | `SKILLS_PROFILES_IMAGE_BASE_URL`、`SKILLS_PROFILES_IMAGE_MODEL`、`SKILLS_PROFILES_IMAGE_SIZE` | 可选；默认用文档里那个 Agnes 端点、`1024x1024`         |
| Variable | `SKILLS_PROFILES_TOTAL_LIMIT`                                                                 | 可选；内置的 `1000` 已经同时封顶了本地和 CI            |

## 测试

整条管道均离线验证：数据解析、`latest` 指针的解析与对垃圾内容的拒绝、发布盖章的往返（给 `stats.json`
加上 `publishedAt` / `upstream` 再剥回去，因此「什么都没改」的一轮仍然认得出来）、DAG 排序、模板渲染、续跑跳过、
失效、依赖传递、markdown 渲染、直接据 persona 渲染配图的 prompt/种子/请求体构造、端点的重试规则、按 key 的限流器，
以及 `run` 的完整 CLI dry-run——都不需要网络（`conftest.py` 把 `data.download_file` 换成由 fixture
构造快照 tarball 的假服务，上游指针与图像端点则都只通过一个打了桩的 `httpx` 调用触达）。

```bash
uv run pytest          # 离线测试套件
uv run ruff check .    # lint
uv run mypy            # 类型检查
```

[`ci`](.github/workflows/ci.yml) 会在每次 push 与 pull request 上跑同样这三项。

文档规范：每份英文文档都要有对应中文版（`README.md` / `README.zh-CN.md`、
`DEVELOPING.md` / `DEVELOPING.zh-CN.md`），同一轮改动里保持同步。
