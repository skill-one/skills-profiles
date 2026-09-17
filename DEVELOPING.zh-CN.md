# 开发 skills-profiles

[README.zh-CN.md](README.zh-CN.md) 里那份数据集的生成器：读取
[skills-sh-mirror](https://github.com/skill-one/skills-sh-mirror) 中每个 skill 的 `SKILL.md`，
向一个 OpenAI 兼容的 LLM 要六份结构化中文档案。

English: [DEVELOPING.md](DEVELOPING.md)

## 快速开始

需要 Python 3.12+、[uv](https://docs.astral.sh/uv/) 和 [`just`](https://just.systems)；LLM 凭据放在
本地 `.env`（复制 [`.env.example`](.env.example)）。

```bash
uv sync
just sync             # 把上游快照下载到 output/cache/skills-sh
just                  # 构建第一个 skill，端到端
just limit=0          # ……或者所有还缺的档案：整份快照，无上限
```

离线、不调 API、不需要凭据：`just dry=1 limit=5`。

## 编排全在 `just`

| 命令                        | 作用                                                                                                                                                                                          |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `just`                      | 构建前 `limit` 个 skill 缺失的档案，安装量最高的优先。窗口按快照自带的索引（`DATA_DIR/skills.jsonl`，安装量降序）排序，并滤掉磁盘上没有 `SKILL.md` 的 id；索引不在时退回目录列表的路径顺序。旁边 recipe 枚举 `PROMPTS_DIR/*.json`，留下 json 还缺的 `(skill, prompt)` 组合，交给 `xargs -P` 池。`jobs` 就是并发的全部。 |
| `just one <prompt> <skill>` | 只构建一个输出，无论批次有没有轮到它。`limit` 是按快照自身顺序划的窗口、不是按名指定某个 skill 的方式，所以这是唯一能寻址「一个格子」的入口——也是唯一能在批次会跳过它的前提下重做它的入口。 |
| `just invalidate <prompt>`  | 删掉某一个 prompt 的全部输出，下一次运行就只重建这些。                                                                                                                                          |
| `just index`                | 把已生成的 `domain` 折成 `<output_dir>/skills.jsonl`：每个 skill 一行、扁平（`id`、`domain`、`reason`），按路径顺序，还没生成 domain 的 skill 不占行。它只读产物树——不用快照、不调模型——并且每次整文件重写，所以它是树的投影，而不是一份要手工同步的第二副本。 |
| `just sync`                 | 把整个上游 `dist` 分支作为一个 tarball 下载并解压进 `data_dir`，整体替换上一份快照。新树先解在旧树旁边，所以下载失败什么都不会变；前面还有一道守卫，拒绝替换「不是快照」的目录。每次运行都会下载——没有任何「已是最新」的状态。纯数据操作：它永远不碰生成的档案。 |
| `just refresh`              | `just sync` 加上它的后果：先把将被替换的那份索引留到一边，然后删掉所有「来源内容 hash 随新快照变了」的 skill 的档案，让下一批重建它们。上游已删除的 skill 保留它的档案。比对完，那份临时索引就消失。 |
| `just clean`                | 删掉档案——`output_dir/skills` 与旁边的索引。同一个根里的快照不动：重新拉取才是贵的那一步。                                                                                                        |
| `just test`                 | `uv run pytest`。                                                                                                                                                                              |

上面每一条都是 recipe 名，`just --list` 会把它们连同各自的一行说明列出来。

| 变量         | 默认值                                 | 含义                                                                                                            |
| ------------ | -------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| `limit`      | `1`                                    | 按快照自身的顺序服务前 N 个 skill：`skills.jsonl` 是安装量降序，所以有限的窗口先做安装量最高的那些。`0` = 全量，无上限。默认 1，所以裸 `just` 只碰一个 skill。窗口负责给一次运行划定范围，顺序只决定有限的窗口能碰到哪些 skill。 |
| `prompt`     | –                                      | 一个 prompt id；留空表示全部。这是「列」而不是「格」。不存在的 id 会在派发任何任务之前失败，并列出可选的那些。 |
| `jobs`       | 每个核一个                             | 同时在飞的生成数（`xargs -P`）。这是「突发」，不是「节奏」。                                                       |
| `rpm`        | –                                      | 端点每分钟允许多少次；`0` = 不配速。池子会被它压住，且每个 worker 在两次调用之间等 `pool * 60 / rpm`，所以批次快不过它。Agnes 免费档用 `just rpm=20`。 |
| `dry`        | –                                      | `1` = 假 LLM、真布局：不调模型，但真实落盘。                                                                      |
| `data_dir`   | `<output_dir>/cache/skills-sh`         | 快照所在位置。它在输出根目录内部、并跟着它走，所以来源会跟档案一起发布；想读别的快照就在命令行上传它。            |
| `output_dir` | `output`                               | 档案目录，规则同上。`just clean` 与 `just invalidate` 也要用，所以它是个变量。                                    |
| `snapshot`   | `dist` 分支的 codeload 地址            | `just sync` 下载什么；指向本地 `file://` tarball 就是测试离线运行它的方式。                                        |
| `py`         | `uv run python`                        | 如何运行脚本（CI 里可以换成解释器的绝对路径）。                                                                    |

旋钮是 `just` 变量，也就是说只在命令行上设置：`SKILLS_PROFILES_LIMIT=20 just` **不生效**，而且这是刻
意的——一个批次只会因为「某次运行明确这么说了」而改变。`.env` 属于 gen.py，放端点和 key；justfile 把
gen.py 要读的四个值（`data_dir`、`output_dir`、`prompts_dir`、`dry`）导出到自己的环境里，这个 export
就是两者之间唯一的交接。

因为输出文件在任何地方都没有前置依赖，**它的存在与否就是全部缓存**——按 `(skill, prompt)` 用一次
`[ -f ]` 判断，所以中途停下的批次从第一个不存在的文件接着做，且永远不会重建已经存在的那个。由此有
三条值得直说的结论：

- **失效就是删除。** `just invalidate scenario`（或 `rm output/skills/<id>/scenario.json`）删掉输出，
  下一次运行就只重建被删的那些。反过来，改 prompt 模板本身*不会*让任何东西失效——这是刻意的，否则
  任何一次廉价编辑都会重写全部档案（单是 `git checkout` 就会，因为 mtime 变了）。
- **唯一会失效的是新快照。** `just refresh` 把刚被替换的那份索引与新拉来的那份对比，删掉所有内容
  hash 变了的 skill 的档案：它们是由已经不存在的文本生成的。它之所以单独是一个动词，是因为
  `just sync` 是纯数据操作——只搬数据的运行不该顺手删掉别人的工作。上游已删除的 skill **不**删：
  它的档案是花过钱的，而且已经没有东西可以重建它了。
- **没有局部失败簿记。** 某个任务报错退出（配额、连接），池会报告，并且什么都没写入——下一次运行
  自然会重试。

## 脚本

一件事，每个 `gen.py` 进程恰好一次 LLM 调用：

```bash
uv run python gen.py <prompt> <skill>           # 只构建一个输出
uv run python gen.py <prompt> <skill> --print   # 打印请求后即停止（不调用、不落盘）
```

`gen.py` 刻意不做「已存在就跳过」：决定构建什么是 justfile 的职责，一个进程只该做被要求的那一件事。
`--print` 是唯一不是构建的那个问题，它不调用也不写文件就能回答——`just render` 就是它。请求与答案作为
数据走 stdout，进度留在 stderr，六万条进度可以就这么扔在那儿。

它与调用方之间的契约就这么多：

- **`<prompt>`** 指向 `prompts/<prompt>.md` 和旁边的 `<prompt>.json`。
- **`<skill>`** 是 `<data_dir>/skills` 下的一个目录名：id 里的 `:` 与 `&` 写成 `_`，上游就是这么写的。
  justfile 用同样的拼写去判断哪些还没做，且有测试走 justfile 构建——所以两边不可能漂移。
- **输出**落在 `<output_dir>/skills/<skill>/<prompt>.json`，markdown 先写、json 以重命名落位——所以
  崩溃既不可能留下一个 json 却没有它的可读副本，也不可能留下一个半写的 json 被下一批当成「已完成」
  跳过。
- **源文本截断在 20000 字符**，一个巨大的 `SKILL.md` 不至于把调用撑爆。
- **退出码**：0 已构建、1 输入或模型不可用、2 参数错误。失败是一行而不是回溯——六万条回溯就不再是信息了。

把「该构建什么」留在 justfile 里而不是放进脚本，出于同一个理由：构建图就是一次目录遍历加一个 glob，
再写个脚本把它打印出来，只是给数据目录布局多留一个可能出错的地方。拉取干脆没有脚本：`just sync`
就是一条 `curl` 加一条 `tar`，唯一要做对的是其余部分所读的那个数据目录布局。

`index.py` 是另一个脚本，做的正是 shell 循环得额外挂上 `jq` 才能做的那件事：读
`<output_dir>/skills`，写出 `output/skills.jsonl`。它没有参数、不用快照、不调模型——只有它遍历的
id、它读的那个角度，以及它重命名落位的那个文件。它不在构建路径上：`just index` 是你想要这份列表时
才跑的一个动词，这也正是索引不可能和一棵并非同时写出的树漂移的原因。

`stale.py` 是第三个，负责 shell 不擅长的那个比对：两份 jsonl 索引进，内容 hash 变了的 id 出——新
索引里已经没有的那些不算，它们不该由谁来删。它唯一的参数是被替换掉的那份索引，把退掉的 id 打到
stdout，并删掉那些 skill 的目录。`just refresh` 就是按这个顺序的 `sync` 加它。

## 工作原理

```
                                    output/  ── 整个产物，发布时就是复制这一个目录
                                      │
镜像 dist 分支 tarball ──► cache/skills-sh (skills/<id>/SKILL.md + 它旁边的文件)
        (`just sync`)                  │
                                       └─► justfile 自己遍历它 ◄── prompts/*.json
                                                       │
                                   `just` 只构建缺的部分，JOBS 个并行
                                                       │
                    output/skills/<id>/<angle>.json + md/<angle>.md
                                                       │
                                  `just index` ──► output/skills.jsonl（派生）
```

`output/` 一个根里放三样东西：档案、放在它们旁边的索引，以及这些档案所依据的快照。快照原先在它旁边
的 `cache/` 里；放进来之后，要发布的那个目录就是自足的——来源和由它生成的东西一起被归档——发布步骤
也从复制两个目录变成复制一个。整个根都 gitignore：由 CI 发布到 `dist` 分支，仓库本身不带它。

设计取舍：

- **一个 prompt、一个文件、一次单轮调用。** 每个 prompt 都是自包含任务：`SKILL.md` 进 system
  消息，prompt 模板进 user 消息，结构化结果落成一个 json。没有任何 prompt 读取别的 prompt 的
  输出，所以既没有需要排序的 DAG，也没有需要计算的依赖闭包，更没有级联失效。新增一个角度只花
  一个 markdown 文件，零代码改动。
- **运行器就是个命令运行器。** `just` 不是构建系统，也没假装是：make 当年白送的两件事，在这里各是
  一行 shell。**存在与否就是跳过**——recipe 在派发之前就把 json 已存在的组合滤掉。**顺序来自快照
  自己**——`skills.jsonl` 写成安装量降序，读它就是全部的排序，安装量最高的自然排在前面；它写到的 id
  在磁盘上没有 `SKILL.md` 就跳过；完全没有索引则退回目录树：用 `find` 而不是 glob（glob 不匹配前导
  点，而 `.claude` 是真实存在的 repo 名），并用 `LC_ALL=C sort` 而不是裸 `sort`（`sort` 会把 `_`
  挪位置，窗口就会因机器而异）。**池子就是并发**——`xargs -P jobs`，一个普通数字，没有 jobserver
  要协商。
  手写的 `graphlib` DAG、信号量、限流器、断点缓存、覆盖度报告和索引投影，当初都是为了回答目录列表、
  `[ -f ]` 和 `xargs` 天生就回答得了的问题；这些全部删掉了，批次改成通过 `just` 本身做端到端验证。
- **限流是一个「节奏」，不是一个令牌桶。** `jobs` 约束的是同时在飞多少，这与批次跑多快不是一回事：
  十个 worker 去打一个一秒就返回的端点，就是一秒十次调用，和你有几个核无关。`rpm` 声明端点允许
  多少，然后每个 worker 在两次调用之间等 `pool * 60 / rpm`——于是 worker 的周期至少有这么长，批次
  无论返回得多快都快不过 `rpm`。池子同样被压到 `rpm` 以内，所以第一轮的突发也落在配额里。六万个
  进程之间不共享、也不协调任何东西；每一个只是知道这个数字。429 依然在它该在的地方被消化——客户端
  自己的退避重试，`max_retries` 则是给「端点真实上限比文档更低」这种情况兜底。
- **输出契约就放在任务旁边。** `prompts/<id>.json` 是那个 prompt 答案的 JSON Schema，它会原样作为
  模型服务自己的 `json_schema` response format（带 `strict`）随请求发出，所以模型是*被解码进*
  这个形状，而不是先好好求它、事后才校验。既没有本地校验器，也没有重试回路，代码里更没有第二份
  输出形状——这也是为什么现在唯一的 LLM 依赖就是模型服务自家的 SDK。
- **一个 prompt 就是一对文件。** `prompts/<id>.md` 是任务，旁边的 `prompts/<id>.json` 是它的契约，
  `_system.md` 承载共享的 system prompt，而它是 `SKILL.md` 触达 prompt 的唯一途径。两半不可能各自
  成为孤儿：它们总是一起被读取，有测试盯着这个配对，而 recipe 枚举的是 schema 那一半，所以没有
  schema 的 prompt 永远不会成为目标。
- **一个职责一个脚本。** `gen.py` 不知道快照存在（它只拿到一个 skill id），也不知道构建图；
  `index.py` 同样两样都不知道，它只读产物树；justfile 只负责指认文件。正是这样，请求本身才小到
  可以一口气读完。
- **一份快照，一次请求。** `just sync` 就是一条 `curl` 加一条 `tar`，拉整个分支：不做选择性解压、不维护
  tag、没有任何会过期的状态。代价是磁盘和下载时间（分支里还带着 avatars 等一批任务永远不读的文件
  ——82687 个文件，而真正要读的只有 9766 个），这是一次刻意取舍：`sync` 不再有任何可能做错的判断。
  它永远是整体替换而不是合并，所以上游消失的 skill 不会把文件留在原地。
- **其余的都不要。** 这个项目早期形态里的三样东西被刻意去掉了：`stats.json`（目录列表本身就是
  索引，也就没有东西会和它漂移）、渲染出来的配图（少一个端点、一个 key、一份配额和一类二进制
  资产）、以及 `dist` 发布工作流（除了这棵目录树，本来也没有别的可发布）。`just index` 确实又写出
  一份 `skills.jsonl`，但没有把别的东西一起带回来：它只是每个 skill 一行、只覆盖它的 `domain`，
  由一条明说的命令从树里派生，也没有任何东西读它。由产出那棵树的运行顺手写出来的索引，才正是这里
  要避开的漂移。

## 新增一个 prompt

两个文件，完全不用改代码。

`prompts/my_angle.md` 是任务。模板唯一能用的变量是 `{{ skill_md }}`，而它只在 `_system.md` 里可用
——源码就是在那条消息里送出去的。任务模板若提到它，会在**加载时**失败，而不是以空字符串的形式抵达。
模板是 jinja2，加载时立即解析并试渲染，所以语法错误或凭空冒出的变量都会点名文件，而不是在批次中途
才炸：

```markdown
请为下面的 skill 写……
```

`prompts/my_angle.json` 是约束答案的 JSON Schema：

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["text"],
  "properties": {
    "text": {"type": "string", "description": "介绍词正文, 100 个字以内"}
  }
}
```

然后给所有 skill 补齐这个角度：

```bash
just prompt=my_angle
```

已生成的角度本来就会被跳过，所以花调用的只有新角度——`prompt=<id>` 只是把这件事说白，而不是去
把另外六个走一遍、发现无事可做。

关于这份 schema 有三点值得知道。让它保持真正的 `.json` 文件就是重点：编辑器或别的工具能校验它，
而 markdown 保持是散文。`strict` 是模型服务的规则而不是我们的，所以它拒绝的 schema——对象没封闭、
字段没进 `required`——会让调用直接 400，而不是被悄悄纠正：`tests/test_gen.py` 会按这些规则检查每
一个 prompt 的 schema，所以 `uv run pytest` 会在批次之前就拦住。另外 `domain` 把 13 个分类写了两遍，
一遍是 markdown 里给模型看的散文，一遍是 schema 里给解码器用的 `enum`；请保持两者一致（也有测试从
enum 这一侧检查）。

## 项目结构

```
justfile                # 编排器：拉取、构建图、并发池、缓存策略
gen.py                  # 请求本身：<prompt> <skill> 进，一个 json + markdown 出
index.py                # 投影：产物树进，一份扁平 jsonl 出
stale.py                # 比对：两份快照索引进，内容变了的 skill 的档案出
prompts/                # 每个 prompt 一对 <id>.md（任务）+ <id>.json（schema），外加 _system.md
tests/                  # 离线单元测试，外加一套 just 端到端测试
.github/                # push / PR 上跑 ci，sync 与 publish 手动触发
```

## 配置

解析优先级（由高到低）：`SKILLS_PROFILES_*` 环境变量 → 本地 `.env` → 内置默认值。空值表示「未
设置」，所以一个没配置的 secret 被导出成 `""` 也不会顶掉默认值。`.env` 由 `just` 自己加载，所以
justfile 自己的变量——那几个路径、`py`——也按同样这三个地方解析。

| 变量                            | 默认值            | 说明                                          |
| ------------------------------- | ----------------- | --------------------------------------------- |
| `SKILLS_PROFILES_MODEL`         | `gpt-4.1-mini`    | 任意 OpenAI 兼容的 chat 模型                  |
| `SKILLS_PROFILES_BASE_URL`      | –                 | OpenAI 兼容端点                               |
| `SKILLS_PROFILES_API_KEY`       | –                 | 端点 API key                                  |
| `SKILLS_PROFILES_MAX_RETRIES`   | `3`               | 每次 LLM 调用的额外重试次数（`0` = 只试一次） |
| `SKILLS_PROFILES_THINKING`      | `false`           | 让模型先思考再作答：模型服务的 `enable_thinking`，只发 `true`（文档也只写了 `true`） |
| `SKILLS_PROFILES_DRY_RUN`       | `false`           | 用假 LLM：不调 API                            |
| `SKILLS_PROFILES_OUTPUT_DIR`    | `output`          | 要发布的那个目录：档案、索引与快照            |
| `SKILLS_PROFILES_DATA_DIR`      | `output/cache/skills-sh` | 解压后的上游快照，位于输出根目录内部   |
| `SKILLS_PROFILES_PROMPTS_DIR`   | `prompts`         | 每个 prompt 一对 `<id>.md` + `<id>.json`（外加 `_system.md`） |

## 测试

测试套件全离线：`conftest.py` 写出一棵假快照树，并让构造真实 LLM 客户端直接失败——所以即使本地
`.env` 里全是真 key，测试也绝不可能网出去。

- `tests/test_gen.py` 覆盖这次请求：prompt 加载与它的几种失败模式、每个 schema 都必须满足的 strict
  规则、分类文案与 enum 的一致性、模板渲染、调用实际发出的关键字、dry-run 占位内容、两份输出文件，
  以及命令本身。
- `tests/test_index.py` 覆盖这个索引：构建图就是产物树、按路径顺序（包括名字带前导点的 repo）、
  每个已生成的 domain 一行且扁平、json 不在的 skill 不占行、id 的拼写，
  以及「要么完整要么不存在」的写入。
- `tests/test_stale.py` 覆盖这个比对：hash 变了只退那一个 skill、上游删掉的 skill 保留档案、没存
  hash 的行不参与比对、还没生成就先变了 hash 的 skill 什么都不退，以及两种冷启动（没有旧索引、
  没有快照索引）。
- `tests/test_just.py` 覆盖 justfile，它同时承担联网与并发两件事：全新构建、第二次运行什么都不做、
  删掉一个 json 只重建那一个、`limit` 窗口及其顺序（快照索引，没有索引则是路径序）、`jobs` 决定
  池子大小、`just one` 能触及窗口之外、
  `just invalidate` 只忘记一个 prompt、`just index` 把整棵树折成一个文件、`just refresh` 只退掉
  新快照真正改动的那些、`DRY=1` 的两种写法、
  继承来的 `SKILLS_PROFILES_DRY_RUN` 不被覆盖地传到每个任务、`just sync` 从本地 tarball 拉一份
  快照并整体替换、拒绝替换「不是快照」的目录的守卫、just 拉来的快照正是批次随后要读的那一份、
  `just clean`，以及缺快照时报错会点出该跑什么。

```bash
uv run pytest          # 离线测试
uv run ruff check .    # lint
uv run mypy            # 类型
just dry=1 limit=2     # 批次本身的端到端
```

## CI

三个工作流，每一个都很薄：活都是 `just` 干的，所以能在本地验证的都在本地验证——`tests/test_just.py`
驱动的是同一批 recipe。

| 工作流 | 触发 | 做什么 |
| --- | --- | --- |
| `ci.yml` | 每次 push 与 PR | `uv sync`、`ruff check .`、`mypy`、`pytest`，并装上 `just` 好让驱动它的那套测试不会跳过。全离线：不要凭据、不要快照。 |
| `sync.yml` | 手动 | `restore-dist` → `just refresh` → `just index` → `publish-dist`（`date`）。替换数据集并退掉它失效的那些；不调模型、不需要 key。 |
| `publish.yml` | 手动 | `restore-dist` → `just limit=… jobs=… rpm=… prompt=…` → `just index` → `publish-dist`（`date-counter`）。对着 `sync` 发布的那份数据集生成，永远不碰上游。 |

两个数据工作流都是先恢复、后发布，所以一次运行＝一个干净的 runner 加两个 tarball。两端各由一个
composite action 负责：

- `.github/actions/restore-dist` 把已发布的根目录放回 `output/`，但去掉 `latest` 指针：那是发布写的，
  运行从不读它。
- `.github/actions/publish-dist` 把 `output/` 变成 `dist` 分支：一个提交、按时间窗裁剪的历史、一个
  `dist-YYYY-MM-DD` 或 `dist-<base>-N` 标签，以及指向它的 `latest` 指针。树没有变化就什么都不发布，
  也不消耗标签——因为与分支的比对发生在选标签之前。

已经没有任何地方需要盖「来源印章」了：快照就和档案发布在同一棵树里，一份档案依据的是什么，看它
旁边的 `cache/skills-sh` 就知道——这也是发布从两个目录变成一个目录的原因。

文档约定：每份英文文档都有对应的中文版（`README.md` / `README.zh-CN.md`、
`DEVELOPING.md` / `DEVELOPING.zh-CN.md`）——同一次改动里一起更新。
