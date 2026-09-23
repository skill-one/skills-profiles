# 开发 skills-profiles

[README.md](README.md) 所述数据集背后的生成器：它从
[skills-sh-mirror](https://github.com/skill-one/skills-sh-mirror) 读取每个 skill 的 `SKILL.md`，
向 Jev（TypeSafe System One）端点问一个类型化问题——这个 skill 属于哪个封闭领域分类。

English: [DEVELOPING.md](DEVELOPING.md)

## 快速开始

需要 Python 3.12+、[uv](https://docs.astral.sh/uv/) 和 [`just`](https://just.systems)；端点密钥
放在本地 `.env`（复制 [`.env.example`](.env.example)）。

```bash
uv sync
just sync             # 拉取镜像到 output/skills 和 output/upstream
just                  # 端到端标注第一个 skill
just limit=0          # ……或所有还没标签的 skill，整个快照，无上限
```

离线、无 API 调用、无凭据：`just dry=1 limit=5`。

## 批处理就是 `just`

| 命令                | 作用 |
| ------------------- | ---- |
| `just`              | 按安装量从高到低，为接下来 `limit` 个还缺 `domain.json` 的 skill 打标签。顺序是清单自己的（`OUTPUT_DIR/skills.jsonl`，安装量降序），并过滤掉有 description 且磁盘上有 `SKILL.md` 的行；没有清单时按路径顺序遍历目录。窗口取前 `limit` 个——数的是工作量而不是位置，所以重复运行沿数据集往下走。配方把它们喂给跑 `jev.py` 的 `xargs -P` 池。`jobs` 就是并发的全部。 |
| `just one <skill>`  | 无论批次是否走到它，精确标注一个 skill。唯一定位单个 skill 的方式——也是不用等批次跳过就能重建单个的唯一方式。 |
| `just render <skill>` | 打印一次标注将发送的请求——state 和类型化问题——什么都不调用。 |
| `just invalidate`   | 删除所有 `domain.json`，下一次运行重新标注整个窗口。 |
| `just index`        | 写 `<output_dir>/skills.jsonl`——清单：镜像列出的每个 skill 一行，按镜像顺序，由镜像自己的行（`id`、`installs`、`url`、`hash`、`fetchedAt`）拼接从该 skill 的 `SKILL.md` 读出的 `description`，以及 `profiles/<id>/domain.json` 里的 `domain` 和 `confidence`。未知时均为 `null`。只读树——无网络、无调用——整体重写文件。同一次遍历还在旁边写两个 README：见下文 `readme.py`。 |
| `just sync`         | 把上游 `dist` 分支整体下成一个 tarball 并解包：skill 目录进 `output_dir/skills`，其余——首要是镜像自己的索引——进 `output_dir/upstream`。然后重建清单。下载落在暂存目录，完整后才切换；有守卫拒绝替换一个不是快照的 `skills/`。纯数据：绝不碰生成的标签。 |
| `just refresh`      | `just sync` 加上它的后果：保留 sync 前的清单，删除源内容 hash 随之变化的每个标签。从镜像消失的 skill 保留标签。 |
| `just clean`        | 删除生成物：`output_dir/profiles`、清单和两个 README。skill 目录和镜像自己的文件保留。 |
| `just test`         | `uv run pytest`。 |

| 变量         | 默认                                   | 含义                                                        |
| ------------ | -------------------------------------- | ----------------------------------------------------------- |
| `limit`      | `1`                                    | 按清单顺序接下来 N 个还没标签的 skill；`0` = 全部。默认一个，所以裸 `just` 是冒烟。数工作量不数位置。 |
| `jobs`       | 每核一个                               | 同时进行的调用数（`xargs -P`）。                             |
| `rpm`        | –                                      | 端点每分钟允许多少；`0` = 不限速。池大小也被它封顶，每个 worker 两次调用间等 `pool * 60 / rpm`。 |
| `dry`        | –                                      | `1` = 假端点、真实目录结构：不调用任何东西。                 |
| `output_dir` | `output`                               | 发布根目录，四个层都在下面。                                 |
| `snapshot`   | `dist` 分支的 codeload url             | `just sync` 拉取什么；测试用本地 `file://` tarball 离线跑。  |
| `py`         | `uv run python`                        | 怎么跑脚本（CI 里用绝对解释器路径覆盖）。                    |

这些旋钮是 `just` 变量——只在命令行设置，别无他处：`SKILLS_PROFILES_LIMIT=20 just` *不*生效。
`.env` 属于脚本，装端点和密钥；justfile 导出 `output_dir`、`prompts_dir` 和 `dry`，这个导出是
两者之间唯一的交接。

因为产出没有任何前置条件，**它的存在就是全部缓存**——逐 skill 用 `[ -f ]` 检查，所以半途停止
的批次从第一个缺失的文件恢复，绝不重建已有的。这有三个值得明说的后果：

- **失效即删除。** `just invalidate`（或 `rm output/profiles/<id>/domain.json`）删掉产出；下次
  运行重新生成。改 `_system.md` 本身*不*会让任何东西失效——否则每次 checkout 移动 mtime 都会免费
  重标整个数据集。
- **唯一会造成失效的是新快照。** `just refresh` 比较被替换的清单和新清单，删掉内容 hash 变化
  的每个 skill 的标签。从上游消失的 skill *不*删：标签已经付过钱了。
- **没有部分失败的簿记。** 抛出异常（配额、连接）的任务非零退出、池子报告、什么都没写——所以
  下次运行直接重试。

## 脚本

每个 `jev.py` 进程一个活、一次调用：

```bash
uv run python jev.py <owner>/<repo>/<slug>           # 精确标注一个 skill
uv run python jev.py <owner>/<repo>/<slug> --print   # 打印请求就停，什么都不调用
```

`jev.py` 故意没有“存在则跳过”的检查：决定建什么是 justfile 的职责。它与调用方的完整契约是：

- **`<skill>`** 是 `<output_dir>/skills` 下的一个 skill 目录：其 id 里的 `:` 和 `&` 写作 `_`，
  镜像自己的树就是这么命名的。
- **产出**落在 `<output_dir>/profiles/<skill>/domain.json`，原地改名写入——写了一半的文件会被
  下一批当成已完成而跳过。
- **源在 20 000 字符处截断**，在换行处下刀，并声明被截断。
- **description 取 front matter 的 `description`**，按 YAML 解析，它是 skill 的门槛：缺失、无法
  解析或没有 description 的头会丢弃该 skill——不调用、不写文件、stderr 一行、状态 1。
- **状态码**：0 已建，1 输入或端点不可用，2 参数错误。失败是一行而不是 traceback，因为几千个
  失败的批次里 traceback 不再是信息。

端点不是聊天型的：`POST /v1/systemone` 接收 `state` 和类型化 `questions`，回答类型化 `answers`
——没有 messages、没有 `json_schema`、没有自由文本。`state` 由唯一的模板 `prompts/_system.md`
渲染：skill 的名字、description、去掉 front matter 的 `SKILL.md` 正文，以及 `domain` 独有的一层
——skill 所属仓库，即其旁系 skill 的一句话描述，每条截成提示、数量封顶 50——因为分类是仓库的
属性而不是单个文件的属性，旁系能为孤立、含糊的 skill 消歧。分类法在代码里是一个对象：
`CRITERIA`（13 个分类及其措辞）和 `INSTRUCTION`（唯一的规则：判断 skill 是干什么的，而不是它
怎么实现的），作为答案被限定的 `criteria` 交给端点——所以没有 schema 里的 enum，也不需要保持同
步的解码器。完整回答被保留——标签、确信度和在全部 13 个分类上的分布；清单取前两者，其余留在
profile。端点闲置后的第一次调用常被丢弃（表现为超时），会重试；被拒绝的请求体（400）不重试。

`index.py` 把镜像的行与树拼接，写 `output/skills.jsonl`。它无参数、无网络、无调用，也不在构建
路径上：`just index` 是你想要清单时跑的命令，`just sync` 跑它是因为 sync 移动了它下面的源层。
同一次运行写 `output/README.md` 和它的中文双胞胎——`readme.py` 装措辞，`index.py` 给数字——即清单
回答不了的那件事：**数据集标了多少。** 它读快照自己的身份（`upstream/latest`、
`upstream/stats.json`）而不是盖墙上时钟，所以没有新内容的发布不花版本号。

`stale.py` 做 shell 不擅长的那个比较：两份清单进去，内容 hash 变化的 id 出来——减去新清单不再
持有、谁也无权删除的那些。`just refresh` 依次是 `sync` 和它。

## 工作方式

```
                        output/  ── 整个产物，作为一个目录发布
                          │
镜像 `dist` 分支 ─────────┼──► skills/<id>/**      skill 本身，发布原样
     (`just sync`)        │                          下载就是拿其中一个，安装就是拷贝
                          ├──► upstream/**         镜像的其余部分，首要是它自己的索引
                          │
                          └─► justfile 遍历清单
                                      │
                        `just` 标注缺失项，一次 JOBS 个
                                      │
                        profiles/<id>/domain.json
                                      │
                `just index` ──► skills.jsonl + README：upstream × skills/ × profiles/
```

运行器是命令运行器，不是构建系统：**存在即跳过**，顺序是镜像自己的（用 `find` 而不是 glob，因
为 `.claude` 是有人用的仓库名；用 `LC_ALL=C sort` 因为普通 `sort` 会挪动 `_`），池子是朴素的
`xargs -P jobs`，没有 jobserver。限速是步伐而不是令牌桶：每个 worker 两次调用间等
`pool * 60 / rpm`，批次不可能跑赢端点；429 仍由客户端自己的退避吸收。

## 项目布局

```
justfile                # 编排器：sync、池子、缓存策略
jev.py                  # 唯一的请求：<skill> 进、domain.json 出；也负责读源和渲染 state
index.py                # 清单及其数字：一行一个 json，以及 README 用的事实
readme.py               # 页面：把那些数字说给读者，双语
stale.py                # 比较：两份清单进，变化 skill 的 profile 出
prompts/_system.md      # state 模板：name、description、正文和 repository 块
tests/                  # 离线单元测试加 just 端到端套件
.github/                # 每次 push 和 PR 跑 ci，sync 和 publish 手动触发
```

## 配置

解析顺序（高到低）：`SKILLS_PROFILES_*` 环境变量 → 本地 `.env` → 内置默认值。空值表示“未设置”。

| 变量                            | 默认值           | 含义                                                |
| ------------------------------- | ---------------- | --------------------------------------------------- |
| `SKILLS_PROFILES_API_KEY`       | –                | 密钥；没有密钥就不调用                               |
| `SKILLS_PROFILES_BASE_URL`      | 302.AI 的 System One 路径 | `jev.py` 发往哪里；别的都不发              |
| `SKILLS_PROFILES_MODEL`         | `jev-latest`     | System One 模型，固定版本之上的别名                  |
| `SKILLS_PROFILES_TIMEOUT`       | `20`             | 每次请求秒数：端点一到三秒回答，闲置后首个调用会被丢弃 |
| `SKILLS_PROFILES_MAX_RETRIES`   | `3`              | 额外重试次数，针对丢弃的调用或繁忙的网关             |
| `SKILLS_PROFILES_DRY_RUN`       | `false`          | 用假端点：不发 API 调用                              |
| `SKILLS_PROFILES_OUTPUT_DIR`    | `output`         | 发布根目录：skills、profiles、upstream 和清单        |
| `SKILLS_PROFILES_PROMPTS_DIR`   | `prompts`        | 放 `_system.md` 的目录                               |

## 测试

套件离线：`conftest.py` 写一棵假快照树，构造真实 HTTP 客户端会响亮地失败，所以即使本地 `.env`
装满真密钥也没有测试能偷偷联网。

- `tests/test_jev.py` 覆盖：作为单一对象的分类法、调用发送的请求体（state 加类型化问题，无
  messages）、丢弃的调用重试而被拒绝的不重试、封闭集之外答案的守卫、源读取（front matter、YAML
  description、截断）、仓库旁系及其封顶，以及命令本身——门槛、退出码、无需密钥打印请求。
- `tests/test_index.py` 覆盖清单和数字；`tests/test_readme.py` 覆盖双语页面；`tests/test_stale.py`
  覆盖 hash 比较；`tests/test_just.py` 对着本地 tarball 驱动 justfile 本身——窗口、池子、缓存、
  `sync`、`refresh`、`invalidate`。

```bash
uv run pytest          # 离线测试套件
uv run ruff check .    # lint
uv run mypy            # 类型
just dry=1 limit=2     # 批处理本身，端到端
```

## CI

三个 workflow，每个都很薄：它们做的活就是 `just`。

| workflow | 触发 | 作用 |
| --- | --- | --- |
| `ci.yml` | 每次 push 和 PR | `uv sync`、`ruff check .`、`mypy`、`pytest`，装了 `just`。离线。 |
| `sync.yml` | 手动 | `restore-dist` → `just refresh` → `publish-dist`（`date`）。替换数据集并失效它所改变的；无模型调用、无密钥。 |
| `publish.yml` | 手动 | `restore-dist` → `just limit=… jobs=… rpm=…` → `just index` → `publish-dist`（`date-counter`）。需要端点自己的 secret 和变量；`replace` 会先删掉所有标签。 |

文档规则：每份英文文档都有中文对应版——同一次修改保持两者同步。
