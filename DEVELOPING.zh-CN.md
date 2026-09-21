# 开发 skills-profiles

[README.zh-CN.md](README.zh-CN.md) 里那份数据集的生成器：读取
[skills-sh-mirror](https://github.com/skill-one/skills-sh-mirror) 中每个 skill 的 `SKILL.md`，
为其索取六份结构化档案 —— 五份中文的来自 OpenAI 兼容的对话模型，`domain` 标签则来自 System One
端点，后者回答的是强类型问题。

English: [DEVELOPING.md](DEVELOPING.md)

## 快速开始

需要 Python 3.12+、[uv](https://docs.astral.sh/uv/) 和 [`just`](https://just.systems)；LLM 凭据放在
本地 `.env`（复制 [`.env.example`](.env.example)）。

```bash
uv sync
just sync             # 把镜像拉进 output/skills 与 output/upstream
just                  # 构建第一个 skill，端到端
just limit=0          # ……或者所有还缺的档案：整份快照，无上限
```

离线、不调 API、不需要凭据：`just dry=1 limit=5`。

## 编排全在 `just`

| 命令                        | 作用                                                                                                                                                                                          |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `just`                      | 构建接下来还缺档案的 `limit` 个 skill，安装量最高的优先。顺序来自清单自己的顺序（`OUTPUT_DIR/skills.jsonl`，即镜像的安装量降序），并滤掉「没有 description」和「磁盘上没有 `SKILL.md`」的行；清单不在时退回目录列表的路径顺序。窗口再取这些 skill 里「至少还缺一个角度」的前 `limit` 个——数的是工作而不是位置，所以反复运行会沿着数据集往下走。recipe 从两个生产者取角度 —— `PROMPTS_DIR/*.json` 与 `jev.py --angles` —— 留下 json 还缺的组合，交给 `xargs -P` 池，由池把每个组合交给拥有该角度的那个脚本。`jobs` 就是并发的全部。 |
| `just one <prompt> <skill>` | 只构建一个输出，无论批次有没有轮到它。`limit` 是按数据集自身顺序划的窗口、不是按名指定某个 skill 的方式，所以这是唯一能寻址「一个格子」的入口——也是唯一能在批次会跳过它的前提下重做它的入口。 |
| `just invalidate <prompt>`  | 删掉某一个 prompt 的全部档案，下一次运行就只重建这些。                                                                                                                                          |
| `just index`                | 写出 `<output_dir>/skills.jsonl`，即那份清单：镜像列出的每个 skill 一行、扁平，顺序就是镜像的顺序，内容是镜像自己的行（`id`、`installs`、`url`、`hash`、`fetchedAt`）连接上从该 skill 的 `SKILL.md` 里读出的 `description`，以及 `profiles/<id>/domain.json` 里的 `domain` 与 `confidence`。未知时两者都是 `null`；镜像已删除但档案还在的 skill 也会有自己的行。它只读这棵树——不联网、不调模型——并且每次整文件重写，所以它是磁盘现状的投影，而不是一份要手工同步的第二副本。它还在旁边写出两份 README，出自同一次遍历：见下面的 `index.py`。 |
| `just sync`                 | 把整个上游 `dist` 分支作为一个 tarball 下载并按层解压进树里：skill 目录进 `output_dir/skills`（完整、未改动），其余部分——首先是镜像自己的索引——进 `output_dir/upstream`。最后重写清单，因为刚移动的源层让它失效了。下载先落在输出根旁边的暂存目录，落齐之后才做替换，所以抓取失败什么都不会变；前面还有一道守卫，拒绝替换「不是快照」的 `skills/`。每次运行都会下载——没有任何「已是最新」的状态。纯数据操作：它永远不碰生成的档案。 |
| `just refresh`              | `just sync` 加上它的后果：先把同步之前的那份清单留到一边，然后删掉所有「来源内容 hash 随新快照变了」的 skill 的档案，让下一批重建它们。上游已删除的 skill 保留它的档案。比对完，那份临时清单就消失。 |
| `just clean`                | 删掉生成物：`output_dir/profiles`、清单以及关于它的两份 README（`output_dir/skills.jsonl`、`output_dir/README.md`、`output_dir/README.zh-CN.md`）。skill 目录与镜像自己的文件不动：它们才是档案的依据，重新拉取才是贵的那一步。                                                                          |
| `just test`                 | `uv run pytest`。                                                                                                                                                                              |

上面每一条都是 recipe 名，`just --list` 会把它们连同各自的一行说明列出来。

| 变量         | 默认值                                 | 含义                                                                                                            |
| ------------ | -------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| `limit`      | `1`                                    | 按清单自身的顺序服务接下来还缺内容的 N 个 skill：`skills.jsonl` 里是镜像的行、按镜像的顺序（安装量降序），所以有限的窗口先做安装量最高的那些。`0` = 全量，无上限。默认 1，所以裸 `just` 只碰一个 skill。它数的是工作而不是位置——已经做完的 skill 不在窗口里——这既让反复运行沿着数据集往下走，也让有限的 `publish` 运行不会从第二次起变成空转。已经建好的内容都保留：窗口决定一次运行能够到哪，而不是产物树里留什么。 |
| `prompt`     | –                                      | 一个 prompt id；留空表示全部。这是「列」而不是「格」。不存在的 id 会在派发任何任务之前失败，并列出可选的那些。 |
| `jobs`       | 每个核一个                             | 同时在飞的生成数（`xargs -P`）。这是「突发」，不是「节奏」。                                                       |
| `rpm`        | –                                      | 端点每分钟允许多少次；`0` = 不配速。池子会被它压住，且每个 worker 在两次调用之间等 `pool * 60 / rpm`，所以批次快不过它。Agnes 免费档用 `just rpm=20`。 |
| `dry`        | –                                      | `1` = 假 LLM、真布局：不调模型，但真实落盘。                                                                      |
| `output_dir` | `output`                               | 要发布的根目录，四层内容都在它下面。`just sync`、`just clean` 与 `just invalidate` 也要用，所以它是个变量。                                    |
| `snapshot`   | `dist` 分支的 codeload 地址            | `just sync` 下载什么；指向本地 `file://` tarball 就是测试离线运行它的方式。                                        |
| `py`         | `uv run python`                        | 如何运行脚本（CI 里可以换成解释器的绝对路径）。                                                                    |

旋钮是 `just` 变量，也就是说只在命令行上设置：`SKILLS_PROFILES_LIMIT=20 just` **不生效**，而且这是刻
意的——一个批次只会因为「某次运行明确这么说了」而改变。`.env` 属于这些脚本，放端点和 key；justfile 把
批次要读的三个值（`output_dir`、`prompts_dir`、`dry`）导出到自己的环境里，这个 export
就是两者之间唯一的交接。

因为输出文件在任何地方都没有前置依赖，**它的存在与否就是全部缓存**——按 `(skill, prompt)` 用一次
`[ -f ]` 判断，所以中途停下的批次从第一个不存在的文件接着做，且永远不会重建已经存在的那个。由此有
三条值得直说的结论：

- **失效就是删除。** `just invalidate scenario`（或 `rm output/profiles/<id>/scenario.json`）删掉输出，
  下一次运行就只重建被删的那些。反过来，改 prompt 模板本身*不会*让任何东西失效——这是刻意的，否则
  任何一次廉价编辑都会重写全部档案（单是 `git checkout` 就会，因为 mtime 变了）。
- **唯一会失效的是新快照。** `just refresh` 把替换之前的那份清单与新拉来的那份对比，删掉所有内容
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
- **`<skill>`** 是 `<output_dir>/skills` 下的一个目录名：id 里的 `:` 与 `&` 写成 `_`，镜像自己的树就是这
  么命名的。justfile 用同样的拼写去判断哪些还没做，且有测试走 justfile 构建——所以两边不可能漂移。
- **输出**落在 `<output_dir>/profiles/<skill>/<prompt>.json`，markdown 先写、json 以重命名落位——所以
  崩溃既不可能留下一个 json 却没有它的可读副本，也不可能留下一个半写的 json 被下一批当成「已完成」
  跳过。
- **源文本截断在 20000 字符**，一个巨大的 `SKILL.md` 不至于把调用撑爆。
- **description 取自 front matter 里的 `description`**，按 YAML 解析；它是对一个 skill 的门槛而不是它的
  某个字段：表头缺失、解析不了、或其中没有 description，这个 skill 就被丢弃——不调用、不写文件、
  stderr 一行、退出码 1。镜像索引里曾经有一份副本，上游已把它去掉；清单用同一批字节把它写出来，
  读不出的写成 `null`，而这也正是让那一行不进窗口的原因。
- **退出码**：0 已构建、1 输入或模型不可用、2 参数错误。失败是一行而不是回溯——六万条回溯就不再是信息了。

把「该构建什么」留在 justfile 里而不是放进脚本，出于同一个理由：构建图就是一次目录遍历加一个 glob，
再写个脚本把它打印出来，只是给目录布局多留一个可能出错的地方。拉取不需要自己的脚本：`just sync`
就是一条 `curl`、一条 `tar`，外加一次清单重写，唯一要做对的是其余部分所读的那两个目录。

`index.py` 是另一个脚本，做的正是 shell 循环得额外挂上 `jq` 才能做的那件事：把镜像的行与这棵树连接
起来，写出 `output/skills.jsonl`。它没有参数、不联网、不调模型——只有它读的那些行、它从 skill 自己
的字节里解析出的 description、树里已有的 domain，以及它重命名落位的那个文件。它也不在构建路径上：
`just index` 是你想要这份清单时才跑的一个动词，而 `just sync` 会顺手跑它，因为一次同步移动了它底下
的源层。除此之外没有任何东西写这个文件，所以它不可能和一棵并非同时写出的树漂移。

同一次运行、同一次遍历还会写出 `output/README.md` 与它的中文版——文字在 `readme.py`，数字由 `index.py`
交给它——它们合起来回答的正是清单答不了的那件事：**数据集建成了多少。** 两行说明哪些文件才是 skill、
哪些是为它写的内容，然后表格像批次一样数格子——角度的 json 才是工作单元，所以 `just invalidate` 留下
的目录不算进度——分母是真正建得出来的 skill，因为一个 front matter 读不出 description 的 skill 会让这
个数字永远到不了 100%。每个角度一行：有多少 skill 有了它，以及这覆盖了镜像安装量的多大比例——后者才是
要紧的数字，因为批次是按安装量从高到低做的（计数 0.3%、加权 16% 说的是同一棵树，而只有后者说明一份
半成品值多少）。表格下面两行：这些数字描述的那份快照，以及分母。**整页就这么多，而「就这么长」正是
要点**——它是一个已发布目录的门面，本项目自己的说明住在这个仓库里；更长的页面只会是它第二份需要同步
的副本，所以有个测试把行数钉在 25 行。有三点决定值得知道。**它叫 README，因为发布根就是产品**：
`publish-dist` 把 `output/` 拷到 `dist` 分支根，所以 `README.md` 就是任何人点进那里时 GitHub 渲染出来
的那一页——这也是为什么有两份，本项目对文档的一贯要求。**文字与数字分开**，于是第二种语言是第二页而
不是第二条代码路径：一个渲染器、两张文字表，外加一个测试断言两者的键完全一致。**它们读的是快照自己的
身份**（`upstream/latest`、`upstream/stats.json`）而不是盖一个墙上时钟，因为发布要把这棵树和分支对比，
一个每次运行都会变的文件会让每次发布都为「并没变过的树」花掉一个版本号。

`stale.py` 是第三个，负责 shell 不擅长的那个比对：两份清单进，内容 hash 变了的 id 出——新清单里已经
没有的那些不算，它们不该由谁来删。它唯一的参数是被替换掉的那份清单，把退掉的 id 打到 stdout，并删掉
那些 skill 的 `profiles/<id>` 目录。`just refresh` 就是按这个顺序的 `sync` 加它。

## 工作原理

```
                      output/  ── 整个产物，发布时就是复制这一个目录
                        │
镜像 `dist` 分支 ────────┼──► skills/<id>/**     skill 本身，就是镜像发布的样子：用户「下载一个
     (`just sync`)      │                         skill」指的就是它，「安装」就是复制它
                        ├──► upstream/**        镜像的其余部分，首先是它自己的索引
                        │
                        └─► justfile 顺着清单走 ◄── prompts/*.json
                                    │
                      `just` 只构建缺的部分，JOBS 个并行
                                    │
                      profiles/<id>/<angle>.json + md/<angle>.md
                                    │
              `just index` ──► skills.jsonl + 两份 README：upstream × skills/ × profiles/
```

`output/` 一个根里放四样东西，每样都按它是什么来命名：skill、围绕它写出的档案、镜像自己的文件，以及
把前两者连起来的清单。镜像原先待在根里的 `cache/` 下，而档案待在一个「并不是 skill」的 `skills/` 里；
按内容给层命名之后，消费者「装一个 skill」就是复制 `skills/<id>/`，而关于它的其它一切都能从
`skills.jsonl` 的一行里读到。整个根都 gitignore：由 CI 发布到 `dist` 分支，仓库本身不带它。

设计取舍：

- **一个 prompt、一个文件、一次单轮调用。** 每个 prompt 都是自包含任务：`SKILL.md` 进 system
  消息，prompt 模板进 user 消息，结构化结果落成一个 json。没有任何 prompt 读取别的 prompt 的
  输出，所以既没有需要排序的 DAG，也没有需要计算的依赖闭包，更没有级联失效。新增一个角度只花
  一个 markdown 文件，零代码改动。
- **运行器就是个命令运行器。** `just` 不是构建系统，也没假装是：make 当年白送的两件事，在这里各是
  一  行 shell。**存在与否就是跳过**——recipe 在派发之前就把 json 已存在的组合滤掉，而窗口是在剩下的
  里数出来的：`limit` 指「接下来还至少缺一个角度的 N 个 skill」，不是列表最前面的 N 个——最上面那个
  skill 一轮就做完了，按位置切窗口会让之后每一轮都空转。这件事用一次 awk 读产物树算出来（把已有的
  json 按 skill 计数），因为在 shell 循环里做六万次 `[ -f ]` 就是一分钟的 fork。**顺序来自镜像
  自己**——清单里是镜像的行、按镜像的顺序（安装量降序），读它就是全部的排序，安装量最高的自然排在
  前面；没有 description 的行、以及磁盘上没有 `SKILL.md` 的行都跳过；完全没有清单则退回目录树：用
  `find` 而不是 glob（glob 不匹配前导点，而 `.claude` 是真实存在的 repo 名），并用 `LC_ALL=C sort`
  而不是裸 `sort`（`sort` 会把 `_` 挪位置，窗口就会因机器而异）。**池子就是并发**——`xargs -P jobs`，
  一个普通数字，没有 jobserver 要协商。
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
  `_system.md` 承载共享的 system prompt，而它是 skill 的 name、description 与正文触达 prompt 的
  唯一途径。两半不可能各自成为孤儿：它们总是一起被读取，有测试盯着这个配对，而 recipe 枚举的是
  schema 那一半，所以没有 schema 的 prompt 永远不会成为目标。
- **一个职责一个脚本。** `gen.py` 不知道镜像存在（它只拿到一个 skill id），也不知道构建图；
  `index.py` 同样两样都不知道，它只读这棵树；`readme.py` 是它的另一半，把同样的数字说给读者听，
  不知道那些数字从哪来；justfile 只负责指认文件。正是这样，请求本身才
  小到可以一口气读完。
- **两个生产者，一条分派。** `jev.py` 是第三个写档案的脚本，也是第二个生产者，它存在的原因是那个
  端点不是对话式的：`POST /v1/systemone` 收一个 `state` 和一张强类型 `questions` 表，回一张强类型
  `answers` 表——没有 messages、没有 `json_schema`、没有自由文本。所以它自己拼请求，其余全部与
  `gen.py` 共用：同一份渲染好的 system message 当作 `state`、同一个写入器、同样的
  `profiles/<id>/<angle>.json` 与 markdown 副本、同样「读不出 description 就丢弃」的门、同样的退出码。
  `just` 把每个组合交给拥有该角度的那个脚本，而 `jev.py --angles` 是它自己角度列表的唯一来源——
  往那个 dict 里加一条，就是加一个批次会构建的角度。它换掉的东西是实在的：System One 的答案只能是
  闭合集合里的一个成员，所以 `domain` 没有理由句、也没有数组。它换来的是把答案整份留在档案里：标签、
  置信度，以及据以判断的那份覆盖 13 个分类的分布 —— 这也正是别的角度的文件所是的东西：模型给出的
  答案本身，而不是对它的摘要。分布值得留下，因为赢家身上并不包含它：52 比 48 决出的结果和 99 比 1
  决出的结果说的不是一件事，而且事后都要不回来。目录只取其中两样（标签与置信度），其余留在它该在的
  地方。
- **一份镜像，一次请求。** `just sync` 是一条 `curl`、一条 `tar` 加一次清单重写，拉整个分支：不做
  选择性解压、不维护 tag、没有任何会过期的状态。代价是磁盘和下载时间（分支里还带着 avatars 等一批
  任务永远不读的文件），这是一次刻意取舍：`sync` 不再有任何可能做错的判断。它永远是整体替换而不是
  合并，所以上游消失的 skill 不会把文件留在原地。
- **其余的都不要。** 这个项目早期形态里的三样东西被刻意去掉了：`stats.json`（目录列表本身就是
  索引，也就没有东西会和它漂移）、渲染出来的配图（少一个端点、一个 key、一份配额和一类二进制
  资产）、以及 `dist` 发布工作流（除了这棵目录树，本来也没有别的可发布）。`just index` 确实又写出
  一份 `skills.jsonl`，但没有把别的东西一起带回来：它只是每个 skill 一行，由一条明说的命令从树里
  派生。由产出那棵树的运行顺手写出来的索引，才正是这里要避开的漂移。两份 README 不是那个文件换了
  个名字：没有东西回读它们、消费者不得依赖它们的数字，它们也不持有任何不在树里的状态——删掉它们，
  下一次 `just index` 会一字不差地写回来。

## 新增一个 prompt

两个文件，完全不用改代码。

`prompts/my_angle.md` 是任务。模板能用的变量只有三个：`{{ name }}`（树用来称呼这个 skill 的那个 id）、
`{{ description }}`（该 skill 自己 front matter 里的 `description`，按 YAML 解析，所以折行块标量与引号
字符串都是以文本形态抵达）与 `{{ skill_body }}`（它的 `SKILL.md`，已去掉 front matter），而且三者只在
`_system.md` 里可用：那里是 skill 被送出去的那条消息，也是任务之前模型知道的全部。正文之所以不带表头，
是因为表头就是前两部分的重复：name 与 description 正是从那里读出来的。正文里它是**整块**去掉而不是逐字段
挑，因为字段是 YAML；留下来的东西是 `license`、`allowed-tools`、版本号——讲一个 skill 怎么装，而不是它
是干什么用的。任务模板若提到这三者之一，会在**加载时**失败，而不是以空字符串的形式抵达。模板是
jinja2，加载时立即解析并试渲染，所以语法错误或凭空冒出的变量都会点名文件，而不是在批次中途才炸：

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
把另外五个走一遍、发现无事可做。

关于这份 schema 有两点值得知道。让它保持真正的 `.json` 文件就是重点：编辑器或别的工具能校验它，
而 markdown 保持是散文。`strict` 是模型服务的规则而不是我们的，所以它拒绝的 schema——对象没封闭、
字段没进 `required`——会让调用直接 400，而不是被悄悄纠正：`tests/test_gen.py` 会按这些规则检查每
一个 prompt 的 schema，所以 `uv run pytest` 会在批次之前就拦住。

Jev 角度是另一类，而且它是 `jev.py` 里的一条条目而不是两个文件：`QUESTIONS` 里的一个名字，装着
端点要回答的强类型问题——带选项的 `choice`、带档位的 `score`，或只有一句 instruction 的 `noul`。
它没有 prompt 模板、也没有 schema，所以没有任何两份东西需要保持一致——`domain` 那 13 个分类就是一个
dict，作为它只能在其中作答的选项交出去。在那里加一条，下一次 `just` 就会构建它，跟新增一对 prompt
文件一样。

## 项目结构

```
justfile                # 编排器：拉取、两个生产者、并发池、缓存策略
gen.py                  # 对话请求：<prompt> <skill> 进，一个 json + markdown 出
jev.py                  # System One 请求：同样进同样出，但用强类型问题代替提示词
index.py                # 清单与它的数字：一份扁平 jsonl 出，外加 README 要用的那些事实
readme.py               # 那一页：把这些数字说给读者听，两种语言各一份
stale.py                # 比对：两份清单进，内容变了的 skill 的档案出
prompts/                # 每个对话角度一对 <id>.md（任务）+ <id>.json（schema），外加 _system.md
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
| `SKILLS_PROFILES_JEV_MODEL`     | `jev-latest`      | System One 模型，别名指向某个版本（`jev-1.13.0`） |
| `SKILLS_PROFILES_JEV_BASE_URL`  | 302.AI 的 System One 路径 | `jev.py` 发往的地址；只有它用得到        |
| `SKILLS_PROFILES_JEV_API_KEY`   | –                 | 它的 key；没有 key 就没有调用                 |
| `SKILLS_PROFILES_JEV_TIMEOUT`   | `20`              | 单次请求秒数：端点一到三秒作答，而空闲后第一次调用会被丢弃 |
| `SKILLS_PROFILES_JEV_MAX_RETRIES` | `3`             | 额外尝试次数，用于被丢弃的调用或忙碌的网关    |
| `SKILLS_PROFILES_MAX_RETRIES`   | `3`               | 每次 LLM 调用的额外重试次数（`0` = 只试一次） |
| `SKILLS_PROFILES_THINKING`      | `false`           | 让模型先思考再作答：模型服务的 `enable_thinking`，只发 `true`（文档也只写了 `true`） |
| `SKILLS_PROFILES_DRY_RUN`       | `false`           | 用假 LLM：不调 API                            |
| `SKILLS_PROFILES_OUTPUT_DIR`    | `output`          | 要发布的那个根目录：skill、档案、upstream 与清单            |
| `SKILLS_PROFILES_PROMPTS_DIR`   | `prompts`         | 每个 prompt 一对 `<id>.md` + `<id>.json`（外加 `_system.md`） |

## 测试

测试套件全离线：`conftest.py` 写出一个假的镜像，按新布局铺进产物树，并让构造真实 LLM 客户端直接
失败——所以即使本地 `.env` 里全是真 key，测试也绝不可能网出去。

- `tests/test_gen.py` 覆盖这次请求：prompt 加载与它的几种失败模式、每个 schema 都必须满足的 strict
  规则、模板渲染、调用实际发出的关键字、dry-run 占位内容、两份输出文件，以及命令本身——再加上把
  description 按 YAML 从表头里读出来，和三种导致 skill 被丢弃的表头。
- `tests/test_jev.py` 覆盖另一个生产者：作为单一对象的分类体系、它声明的角度、调用发出的请求体
  （一个 state 加强类型问题，没有任何 messages）、被丢弃的调用会重试而被告知的请求不会、闭合集合之外
  的答案会被拦下，以及命令本身——同一道门、同样的退出码，还有不用 key 也能打印请求。
- `tests/test_index.py` 覆盖这份清单：镜像那一行逐字段转发、我们的三个字段接在后面；镜像列出的每个
  skill 都有行（包括还没生成任何档案的）、镜像已删除但档案还在的也有行；读不出 description 的和还没
  定 domain 的都是 `null`；id 用镜像的拼写而目录树用另一种；孤儿靠遍历而不是 glob（包括名字带前导点
  的 repo）；缺镜像索引时的报错；justfile 用来匹配的那个 `"description":null` 拼写；
  以及「要么完整要么不存在」的写入——再加上 README 所依据的那些数字：工作单元是 json 而不是目录、
  只算真建得出来的分母、被下架的 skill 既不算覆盖也不算数据集、安装量加权、快照身份读自 `upstream/`
  而不是自己盖章、答不出来的树用一个破折号表示，以及同一棵树读出同样的数字。
- `tests/test_readme.py` 覆盖那一页：两种语言持有完全相同的键、其中的占位符都是报告里有的数字、
  页面不超出它的长度上限、一棵什么都没建的树与一棵建了一部分的树各渲染一次、两页互指、都写明自己是
  生成物，以及两页都是这棵树的函数。
- `tests/test_stale.py` 覆盖这个比对：hash 变了只退那一个 skill、上游删掉的 skill 保留档案、没存 hash
  的行不参与比对、还没生成就先变了 hash 的 skill 什么都不退，以及两种冷启动（没有旧清单、树上没有清单）。
- `tests/test_just.py` 覆盖 justfile，它同时承担联网与并发两件事：全新构建、有限的一轮取的是接下来
  还缺的那些 skill 而不是最上面那几个、整份都建好时什么都不做、删掉一个 json 只重建那一个、
  `limit` 窗口及其顺序（清单，没有清单则是路径序）、读不出 description 的 skill 完全不是目标、
  `jobs` 决定池子大小、`just one` 能触及窗口之外、
  `just invalidate` 只忘记一个 prompt、`just index` 把镜像的行与档案连起来并顺手写出旁边的两份 README、`just refresh` 只退掉
  新快照真正改动的那些、`DRY=1` 的两种写法、
  继承来的 `SKILLS_PROFILES_DRY_RUN` 不被覆盖地传到每个任务、`just sync` 从本地 tarball 拉一份
  快照、按两层解压并整体替换、并重写它刚把源层移走的那份清单；拒绝替换「不是快照」的目录的守卫、
  just 拉来的快照正是批次随后要读的那一份、
  `just clean`，以及缺来源时报错会点出该跑什么。

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
| `sync.yml` | 手动 | `restore-dist` → `just refresh` → `publish-dist`（`date`）。替换数据集、退掉它失效的那些并重写清单（`just refresh` 里已经包含 `just index`）；不调模型、不需要 key。 |
| `publish.yml` | 手动 | `restore-dist` → `just limit=… jobs=… rpm=… prompt=…` → `just index` → `publish-dist`（`date-counter`）。对着 `sync` 发布的那份数据集生成，永远不碰上游，并需要端点自己的 secret 与变量。 |

两个数据工作流都是先恢复、后发布，所以一次运行＝一个干净的 runner 加两个 tarball。两端各由一个
composite action 负责：

- `.github/actions/restore-dist` 把已发布的根目录放回 `output/`，但去掉 `latest` 指针：那是发布写的，
  运行从不读它。
- `.github/actions/publish-dist` 把 `output/` 变成 `dist` 分支：一个提交、按时间窗裁剪的历史、一个
  `dist-YYYY-MM-DD` 或 `dist-<base>-N` 标签，以及指向它的 `latest` 指针。树没有变化就什么都不发布，
  也不消耗标签——因为与分支的比对发生在选标签之前。

已经没有任何地方需要盖「来源印章」了：skill 就和档案发布在同一棵树里，一份档案依据的是什么，看它
旁边的 `skills/<id>/` 就知道——这也是发布从两个目录变成一个目录的原因。

文档约定：每份英文文档都有对应的中文版（`README.md` / `README.zh-CN.md`、
`DEVELOPING.md` / `DEVELOPING.zh-CN.md`）——同一次改动里一起更新。
