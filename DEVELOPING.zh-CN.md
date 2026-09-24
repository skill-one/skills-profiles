# 开发 skills-profiles

[README.md](README.md) 所述数据集背后的生成器：它从
[skills-sh-mirror](https://github.com/skill-one/skills-sh-mirror) 读取每个 skill 的 `SKILL.md`，
向 Jev（TypeSafe System One）端点问一个类型化问题——这个 skill 属于哪个封闭领域分类。第二个生
产者 `translate.py` 向 OpenAI 兼容的聊天端点问一个自由文本问题——skill 的一句话描述进去、中文
出来；第三个 `skill_zh.py` 向同一个端点请求把 `SKILL.md` 正文翻译成一份中文页面。三者是同一个
profile 目录上的平行角度，而且都很薄：目录树、源读取、prompt 文件、配置、
带重试的调用、原子写和命令本身都只在 `common.py` 里有一份。

English: [DEVELOPING.md](DEVELOPING.md)

## 快速开始

需要 Python 3.12+、[uv](https://docs.astral.sh/uv/) 和 [`just`](https://just.systems)；两个端点
的密钥放在本地 `.env`（复制 [`.env.example`](.env.example)）。

```bash
uv sync
just sync             # 拉取镜像到 output/skills 和 output/upstream
just                  # 端到端标注第一个 skill
just limit=0          # ……或所有还没标签的 skill，整个快照，无上限
just translate        # 第二个角度：翻译第一个还缺的 description_zh
just skill-zh         # 第三个角度：SKILL.md 正文的中文页面
```

离线、无 API 调用、无凭据：`just dry=1 limit=5`（以及 `just dry=1 translate`、
`just dry=1 skill-zh`）。

## 批处理就是 `just`

| 命令                            | 作用                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| ------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `just`                          | 按安装量从高到低，为接下来 `limit` 个还缺 `domain.json` 的 skill 打标签。顺序是清单自己的（`OUTPUT_DIR/skills.jsonl`，安装量降序），并过滤掉有 description 且磁盘上有 `SKILL.md` 的行；没有清单时按路径顺序遍历目录。窗口取前 `limit` 个——数的是工作量而不是位置，所以重复运行沿数据集往下走。配方把它们喂给跑 `jev.py` 的 `xargs -P` 池。`jobs` 就是并发的全部。                                                                             |
| `just translate`                | 第二个角度的同一套批处理：接下来 `limit` 个还缺 `description_zh.json` 的 skill，同样的顺序、同样的池子，跑 `translate.py`。下面所有旋钮用法相同。                                                                                                                                                                                                                                                                                             |
| `just skill-zh`                 | 第三个角度的同一套批处理：接下来 `limit` 个还缺 `skill_zh.md` 的 skill，同样的顺序、同样的池子，跑 `skill_zh.py`。下面所有旋钮用法相同。                                                                                                                                                                                                                                                                                                       |
| `just one <skill>`              | 无论批次是否走到它，精确标注一个 skill。唯一定位单个 skill 的方式——也是不用等批次跳过就能重建单个的唯一方式。                                                                                                                                                                                                                                                                                                                                 |
| `just translate-one <skill>`    | 精确翻译一个 skill，窗口内外皆可。                                                                                                                                                                                                                                                                                                                                                                                                            |
| `just skill-zh-one <skill>`     | 精确翻译一个 skill 的 SKILL.md 正文，窗口内外皆可。                                                                                                                                                                                                                                                                                                                                                                                           |
| `just render <skill>`           | 打印一次标注将发送的请求——state 和类型化问题——什么都不调用。                                                                                                                                                                                                                                                                                                                                                                                  |
| `just translate-render <skill>` | 打印一次翻译将发送的请求——翻译模板渲染出的两段话——什么都不调用。                                                                                                                                                                                                                                                                                                                                                                              |
| `just invalidate`               | 删除所有 `domain.json`，下一次运行重新标注整个窗口。                                                                                                                                                                                                                                                                                                                                                                                          |
| `just invalidate-translate`     | 删除所有 `description_zh.json`，下一次翻译运行重建整个窗口。                                                                                                                                                                                                                                                                                                                                                                                  |
| `just invalidate-skill-zh`      | 删除所有 `skill_zh.md`，下一次 skill-zh 运行重建整个窗口。                                                                                                                                                                                                                                                                                                                                                                                    |
| `just index`                    | 写 `<output_dir>/skills.jsonl`——清单：镜像列出的每个 skill 一行，按镜像顺序，由镜像自己的行（`id`、`installs`、`url`、`hash`、`fetchedAt`）拼接从该 skill 的 `SKILL.md` 读出的 `description`、`profiles/<id>/description_zh.json` 里的 `description_zh`，以及 `profiles/<id>/domain.json` 里的 `domain` 和 `confidence`。拼接字段未知时为 `null`。只读树——无网络、无调用——整体重写文件。同一次遍历还在旁边写两个 README：见下文 `readme.py`。 |
| `just sync`                     | 把上游 `dist` 分支整体下成一个 tarball 并解包：skill 目录——剪到只剩 `SKILL.md`——进 `output_dir/skills`，镜像自己的文件只留树会读取的（索引、`latest`、`stats.json`）进 `output_dir/upstream`。然后重建清单。下载落在暂存目录，完整后才切换；有守卫拒绝替换一个不是快照的 `skills/`。纯数据：绝不碰生成的 profile。                                                                                                                                                                                   |
| `just refresh`                  | `just sync` 加上它的后果：保留 sync 前的清单，源内容 hash 随之变化的每个 skill，其整个 profile——两个文件——都删除。从镜像消失的 skill 保留 profile。                                                                                                                                                                                                                                                                                           |
| `just clean`                    | 删除生成物：`output_dir/profiles`、清单和两个 README。skill 目录和镜像自己的文件保留。                                                                                                                                                                                                                                                                                                                                                        |
| `just test`                     | `uv run pytest`。                                                                                                                                                                                                                                                                                                                                                                                                                             |

三个批次共用一个配方体——带参数的 `[script] build angle:`，由角度决定脚本（`jev.py`、
`translate.py` 还是 `skill_zh.py`）、表示“完成”的文件、以及失败日志里的标签；`default`、
`translate` 和 `skill-zh` 只是调用它。

| 变量         | 默认                       | 含义                                                                                                          |
| ------------ | -------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `limit`      | `1`                        | 按清单顺序接下来 N 个还缺当前角度产物的 skill；`0` = 全部。默认一个，所以裸 `just` 是冒烟。数工作量不数位置。 |
| `jobs`       | `32`                       | 同时进行的调用数（`xargs -P`）。                                                                              |
| `dry`        | –                          | `1` = 假端点、真实目录结构：不调用任何东西。                                                                  |
| `output_dir` | `output`                   | 发布根目录，四个层都在下面。                                                                                  |
| `snapshot`   | `dist` 分支的 codeload url | `just sync` 拉取什么；测试用本地 `file://` tarball 离线跑。                                                   |
| `py`         | `uv run python`            | 怎么跑脚本（CI 里用绝对解释器路径覆盖）。                                                                     |

这些旋钮是 `just` 变量——只在命令行设置，别无他处：`SKILLS_PROFILES_LIMIT=20 just` *不*生效。
`.env` 属于脚本，装两个端点和它们的密钥；justfile 导出 `output_dir`、`prompts_dir` 和 `dry`，
这个导出是两者之间唯一的交接。

因为产出没有任何前置条件，**它的存在就是全部缓存**——逐 skill 用 `[ -f ]` 检查，所以半途停止
的批次从第一个缺失的文件恢复，绝不重建已有的。一个 profile 里的两个文件各自缓存——domain 标
签不算翻译，翻译也不算标签。这有三个值得明说的后果：

- **失效即删除。** `just invalidate` / `just invalidate-translate`（或 `rm` 掉
  `output/profiles/<id>/` 里的任一文件）删掉产出；下次运行重新生成。改 prompt 文件
  （`_system.md`、`translate.md`、`translate_user.md`）本身*不*会让任何东西失效——否则每次
  checkout 移动 mtime 都会免费重标整个数据集。
- **唯一会造成失效的是新快照。** `just refresh` 比较被替换的清单和新清单，删掉内容 hash 变化
  的每个 skill 的整个 profile——两个角度一起删，因为它们都来自那份 `SKILL.md`。从上游消失的
  skill *不*删：profile 已经付过钱了。
- **单个 skill 失败不会结束整批。** 任务失败（配额、连接等）会按 id 报出来，不写入文件，池子继续处理；
  CI 会记录错误详情并发布已经成功生成的产物。下一轮会重试仍缺少文件的 skill。

## 脚本

一个进程一个活、一次调用。两个命令做的事其实是同一个命令——`common.py` 里的共享骨架（`run`）：
解析唯一的 skill 参数、读源、以 description 为门槛、构造请求、调用、把该角度的一个 json 原地改
名写好，并把失败变成一行 stderr 和一个状态码。每个生产者只提供三样东西：请求、回答它的调用、
dry-run 占位值。domain 角度：

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
——没有 messages、没有 `json_schema`、没有自由文本。`state` 由模板 `prompts/_system.md`
渲染：skill 的名字、description、去掉 front matter 的 `SKILL.md` 正文，以及 `domain` 独有的一层
——skill 所属仓库，即其旁系 skill 的一句话描述，每条截成提示、数量封顶 50——因为分类是仓库的
属性而不是单个文件的属性，旁系能为孤立、含糊的 skill 消歧。分类法在代码里是一个对象：
`CRITERIA`（13 个分类及其措辞）和 `INSTRUCTION`（唯一的规则：判断 skill 是干什么的，而不是它
怎么实现的），作为答案被限定的 `criteria` 交给端点——所以没有 schema 里的 enum，也不需要保持同
步的解码器。完整回答被保留——标签、确信度和在全部 13 个分类上的分布；清单取前两者，其余留在
profile。端点闲置后的第一次调用常被丢弃（表现为超时），会重试；被拒绝的请求体（400）不重试。

翻译角度与它对称：

```bash
uv run python translate.py <owner>/<repo>/<slug>           # 精确翻译一个 skill
uv run python translate.py <owner>/<repo>/<slug> --print   # 打印请求就停，什么都不调用
```

`translate.py` 故意做成与 `jev.py` 相同的形状——相同的命令行、相同的门槛（没有 description 则
状态 1）、相同的退出码、相同的原地改名写入，产出落在
`<output_dir>/profiles/<skill>/description_zh.json`，形如 `{description_zh}`；dry-run 也相同
（写一个 `【占位】` 占位串，没有密钥也能走一遍目录结构）。两者使用同一个 `common.Config`——共享
配置（超时、重试、dry-run、路径），三个翻译配置与类型化端点的三个配置并列。真正不同的只有调
用：标准的 OpenAI 兼容 `POST {base}/chat/completions`，Bearer 密钥、`temperature` 0，两段话从
`prompts/translate.md` 和 `prompts/translate_user.md` 用代码固定的唯一目标语言渲染——一条忠实
翻译的 system 指令（保留含义、语气、段落与有效格式；代码和占位符原样不动；沿用给出的上下文与
术语），以及承载那句描述的 `Translate to …:` user 段。深度思考默认开启：MaaS 扩展字段
`enable_thinking: true` 加上 `max_tokens: 32768`（文档上限——端点自己的 2048 默认会把推理截
断）。模型先把推理写进 `reasoning_content`；这份草稿永不读取（`translation()` 只取
`choices[0].message.content`），也永不写入角度文件——两个旋钮都是配置项：
`TRANSLATE_ENABLE_THINKING`、`TRANSLATE_MAX_TOKENS`。描述是 Jinja 变量、永远不是模板文本的一
部分，所以 skill 自己那句话里的花括号只是数据。它只发描述——不发 `SKILL.md`，没有截断。
`choices[0].message.content` 就是完整回答：空响应是端点不可用，而不是空翻译。重试规则在
`common.py` 里，与 domain 角度共用：瞬时状态码和连接错误指数退避，4xx 立即失败。默认值指向讯
飞星辰 MaaS 上的 Spark-X2.5-4B；控制台显示的模型 id 可能不同，因此留了环境变量覆盖。

第三个角度再次与它对称：

```bash
uv run python skill_zh.py <owner>/<repo>/<slug>           # 精确翻译一个 skill 的正文
uv run python skill_zh.py <owner>/<repo>/<slug> --print   # 打印请求就停，什么都不调用
```

`skill_zh.py` 又是同一个形状——相同的命令行、相同的门槛、相同的退出码、相同的原地改名写入——
只有两处不同。它发送的是 SKILL.md *正文*（front matter 是标识性元数据，清单和其他角度文件已
经携带），两段话从 `prompts/skill_zh.md` 和 `prompts/skill_zh_user.md` 渲染；它写的是一个文本
文件 `<output_dir>/profiles/<skill>/skill_zh.md`：只有译文本身。
正文超过 `MAX_BODY_CHARS`（脚本内，60 000 字符）即为不可用输入——半截翻译的页面绝不能冒充完整
的一页——和缺 description 一样，丢弃该 skill：不调用、不写文件。

`index.py` 把镜像的行与树拼接，写 `output/skills.jsonl`。它无参数、无网络、无调用，也不在构建
路径上：`just index` 是你想要清单时跑的命令，`just sync` 跑它是因为 sync 移动了它下面的源层。
每行先带镜像字段，然后是 `description`、`description_zh`、`domain`、`confidence` 和 `skill_zh`——
各角度从自己的文件读出，互相独立、也各自缺失（`skill_zh` 是存在标记：页面本身就是回答）。同一次
运行写 `output/README.md` 和它的中文双胞胎——
`readme.py` 装措辞，`index.py` 给数字——即清单回答不了的那件事：**数据集标了多少**（domain 覆
盖率；翻译覆盖率不在页面上）。它读快照自己的身份（`upstream/latest`、`upstream/stats.json`）而
不是盖墙上时钟，所以没有新内容的发布不花版本号。

`stale.py` 做 shell 不擅长的那个比较：两份清单进去，内容 hash 变化的 id 出来——减去新清单不再
持有、谁也无权删除的那些。`just refresh` 依次是 `sync` 和它。

## 工作方式

```
                        output/  ── 整个产物，作为一个目录发布
                          │
镜像 `dist` 分支 ─────────┼──► skills/<id>/**      各角度共用的构建源，只有 SKILL.md
     (`just sync`)        │                          不是安装件：完整的 skill 在它的 url 里
                          ├──► upstream/**         树会读取的镜像文件，首要是它自己的索引
                          │
                          └─► justfile 遍历清单
                                      │
                        `just` 标注缺失项，一次 JOBS 个
                        `just translate` 翻译缺失项，同一个池子
                        `just skill-zh` 翻译页面，同一个池子
                                      │
                        profiles/<id>/domain.json + description_zh.json + skill_zh.md
                                      │
                `just index` ──► skills.jsonl + README：upstream × skills/ × profiles/
```

运行器是命令运行器，不是构建系统：**存在即跳过**，顺序是镜像自己的（用 `find` 而不是 glob，因
为 `.claude` 是有人用的仓库名；用 `LC_ALL=C sort` 因为普通 `sort` 会挪动 `_`），池子是朴素的
`xargs -P jobs`，没有 jobserver，也没有每分钟限速——每个 worker 上一次调用一返回就发下一次；
瞬时 429 由客户端自己的指数退避吸收。

## 项目布局

```
justfile                # 编排器：sync、共享的 build-angle 批处理、缓存策略
common.py               # 两个生产者共用的内核：Config、目录树、源读取、prompt、带重试的调用、
                        # 原子写，以及 run() 命令骨架
jev.py                  # domain 角度：分类法、state、类型化问题
translate.py            # 翻译角度：一次聊天调用，套在共享命令之上
skill_zh.py             # 页面角度：SKILL.md 正文的翻译，写一个 .md
index.py                # 清单及其数字：一行一个 json，以及 README 用的事实
readme.py               # 页面：把那些数字说给读者，双语
stale.py                # 比较：两份清单进，变化 skill 的 profile 出
prompts/_system.md        # state 模板：name、description、正文和 repository 块
prompts/translate.md      # 翻译 system 模板：忠实翻译任务，{{to}}
prompts/translate_user.md # 翻译 user 模板：承载 {{text}} 的 “Translate to {{to}}:”
prompts/skill_zh.md       # 页面 system 模板：翻译文档、保留格式
prompts/skill_zh_user.md  # 页面 user 模板：承载正文的 “Translate to {{to}}:”
tests/                  # 离线单元测试加 just 端到端套件
.github/                # 每次 push 和 PR 跑 ci，sync 和 publish 手动触发
```

## 配置

解析顺序（高到低）：`SKILLS_PROFILES_*` 环境变量 → 本地 `.env` → 内置默认值。空值表示“未设置”。

| 变量                                        | 默认值                    | 含义                                                                                                  |
| ------------------------------------------- | ------------------------- | ----------------------------------------------------------------------------------------------------- |
| `SKILLS_PROFILES_API_KEY`                   | –                         | 类型化端点的密钥；没有密钥就不调用                                                                    |
| `SKILLS_PROFILES_BASE_URL`                  | 302.AI 的 System One 路径 | `jev.py` 发往哪里；别的都不发                                                                         |
| `SKILLS_PROFILES_MODEL`                     | `jev-latest`              | System One 模型，固定版本之上的别名                                                                   |
| `SKILLS_PROFILES_TRANSLATE_API_KEY`         | –                         | 聊天端点的密钥；`translate.py` 和 `skill_zh.py` 用                                                    |
| `SKILLS_PROFILES_TRANSLATE_BASE_URL`        | 星辰 MaaS v2 根地址       | OpenAI 兼容根地址；`translate.py` 发往 `{base}/chat/completions`                                      |
| `SKILLS_PROFILES_TRANSLATE_MODEL`           | `spark-x2.5-4b`           | 聊天模型 id；以控制台服务页显示的拼写为准                                                             |
| `SKILLS_PROFILES_TRANSLATE_ENABLE_THINKING` | `true`                    | 发送 MaaS 的 `enable_thinking` 开关；模型先推理再作答（`reasoning_content`）                          |
| `SKILLS_PROFILES_TRANSLATE_MAX_TOKENS`      | `32768`                   | 回答的 token 预算，含推理；端点自己的默认值只有 2048                                                  |
| `SKILLS_PROFILES_TIMEOUT`                   | `20`                      | 每次请求秒数，两个端点通用：一到三秒回答，闲置后首个调用会被丢弃。思考式翻译更慢——该批次请调大（120） |
| `SKILLS_PROFILES_MAX_RETRIES`               | `3`                       | 额外重试次数，针对丢弃的调用或繁忙的网关；两个端点通用                                                |
| `SKILLS_PROFILES_DRY_RUN`                   | `false`                   | 两个生产者都用假的：不发 API 调用                                                                     |
| `SKILLS_PROFILES_OUTPUT_DIR`                | `output`                  | 发布根目录：skills、profiles、upstream 和清单                                                         |
| `SKILLS_PROFILES_PROMPTS_DIR`               | `prompts`                 | 放 `_system.md`、`translate.md` 和 `translate_user.md` 的目录                                         |

## 测试

套件离线：`conftest.py` 写一棵假快照树，构造真实 HTTP 客户端会响亮地失败，所以即使本地 `.env`
装满真密钥也没有测试能偷偷联网。

- `tests/test_common.py` 覆盖两个生产者共用的部分：源读取（front matter、YAML description、
  20 000 字符截断）、仓库旁系及其封顶、prompt 文件、原子写，以及重试规则（丢弃的调用重试、被
  拒绝的不重试）。
- `tests/test_jev.py` 覆盖 domain 角度本身：作为单一对象的分类法、调用发送的请求体（state 加
  类型化问题，无 messages）、封闭集之外答案的守卫、仓库进入 state，以及命令本身——门槛、退出码、
  无需密钥打印请求。
- `tests/test_translate.py` 以同样方式覆盖第二个角度：请求体（两个 prompt 文件渲染成 system 和
  user 两段，无 state）、描述作为 Jinja 值传入、URL 拼接和 Bearer 头、空回答被拒、dry-run
  占位，以及命令本身——门槛、退出码、无需密钥打印请求。
- `tests/test_index.py` 覆盖清单和数字（包括 `description_zh` 独立拼接）；`tests/test_readme.py`
  覆盖双语页面；`tests/test_stale.py` 覆盖 hash 比较；`tests/test_just.py` 对着本地 tarball 驱动
  justfile 本身——各批次、窗口、池子、缓存、`sync`、`refresh`、每个角度各自的 `invalidate`。
- `tests/test_skill_zh.py` 覆盖第三个角度：请求（正文作为 Jinja 值传入、front matter 绝不外发）、
  产出（原样发布的 front matter 加译文，一个 `skill_zh.md`）、长度门槛，以及命令本身——门槛、
  退出码、无需密钥打印请求。

```bash
uv run pytest          # 离线测试套件
uv run ruff check .    # lint
uv run mypy            # 类型
just dry=1 limit=2     # 批处理本身，端到端
just dry=1 translate   # 第二个批次，端到端
just dry=1 skill-zh    # 第三个批次，端到端
```

## CI

三个 workflow，每个都很薄：它们做的活就是 `just`。

| workflow      | 触发            | 作用                                                                                                                                                                                                                                       |
| ------------- | --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `ci.yml`      | 每次 push 和 PR | `uv sync`、`ruff check .`、`mypy`、`pytest`，装了 `just`。离线。                                                                                                                                                                           |
| `sync.yml`    | 手动            | `restore-dist` → `just refresh` → `publish-dist`（`date`）。替换数据集并失效它所改变的；无模型调用、无密钥。                                                                                                                               |
| `publish.yml` | 手动            | `restore-dist` → 对所选 `angle`（`domain`、`translate`、`skill_zh` 或 `all`——按此顺序）跑 `just limit=… jobs=…` → `just index` → `publish-dist`（`date-counter`）。需要所选角度各自的 secret 和变量；`replace` 会先删掉这些角度的产物。 |

文档规则：每份英文文档都有中文对应版——同一次修改保持两者同步。
