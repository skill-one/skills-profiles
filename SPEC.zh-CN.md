# skills-profiles: 对外的那一面

黑盒视角：用户或消费方能看见的一切，完全不涉及它内部怎么实现的。

**产物是一个目录** —— `output/`：镜像原样发布的 skill 目录、围绕它们写出的中文档案、镜像自己的那
些文件，以及把前两者连起来的一份清单。生成器是为了产出这个目录而存在的，所以它就是接口，命令只决定
其中哪一部分被写出来。

English: [SPEC.md](SPEC.md)

## 1. 输出 —— 接口本身

```
<output_dir>/
├── skills/<owner>/<repo>/<slug>/     # 镜像自己的目录，完整且未改动：
│   ├── SKILL.md                      #   把它拷进 skills 目录就等于装好了这个 skill
│   └── ...该 skill 随附的一切        #   ——这正是用户「下载一个 skill」的含义
├── profiles/<owner>/<repo>/<slug>/
│   ├── domain.json  scenario.json  tagline.json
│   ├── blackbox.json  whitebox.json  comments.json
│   └── md/<angle>.md      # 同样的内容，渲染成方便阅读的版本
├── skills.jsonl           # `just index`：清单，每个 skill 一行、扁平
├── stats.txt              # …… 以及它旁边的报告：数据集建成到什么程度了
└── upstream/              # 镜像的其余部分：skills.jsonl、repos.jsonl、owners.jsonl、
                           # curated.jsonl、trending.json、stats.json、latest、avatars/
```

这里没有任何一处需要回头去找镜像：装 skill 用 `skills/`，而关于它的全部已知信息都在 `skills.jsonl`。

`<id>` 是 skill id，即 `{owner}/{repo}/{slug}`。清单里的行按镜像自己的拼写记它；两个目录树则把 `:`
与 `&` 写成 `_`，那也正是交给 `gen.py` 的句柄。

| 角度 | json 结构 | 内容 |
| --- | --- | --- |
| `domain` | `{domain[1–3], reason}` | 13 个闭合英文分类中的一个到三个,按贴合度降序、主分类在前,加一句话理由 |
| `scenario` | `{text}` | 一段 100 字以内的场景化介绍，从用户痛点切入 |
| `tagline` | `{taglines[3]}` | 3 条宣传短标语，每条 20 字以内 |
| `blackbox` | `{function, input_output[3–5]}` | 黑盒视角：你给什么 → 你得到什么 |
| `whitebox` | `{execution_flow[3–5], mechanisms[2–3]}` | 白盒视角：主路径、关键机制、真实依赖 |
| `comments` | `{comments[4–6]}` | 用户第一人称评论：`{user, category, comment}` |

- 每个 skill 一个目录，每个角度一个文件。各角度彼此独立——没有任何文件读另一个文件。
- `.json` 是数据；`md/<angle>.md` 是同样字段的渲染版，先写。
- **清单是入口。** `skills.jsonl` 由 `just index` 写出：每个 skill 一行、扁平，按镜像自身的顺序，
  内容就是镜像那一行——`id`、`installs`、`url`、`hash`、`fetchedAt`——再加上从该 skill 自己的
  `SKILL.md` 里读出的 `description`，以及本项目标出的 `domain` 与其 `reason`。未知时 `description`
  与 `domain` 为 `null`，所以一行陈述的是数据集的状态而不是工作的取舍：`.domain != null` 是已建成的
  部分，`.installs` 给没建的那部分排序。
- **`stats.txt` 是进度报告**，由同一条命令、同一次遍历写出：数据集的 `skill × 角度` 格子有多少已在
  磁盘上，逐角度给出数量、并按安装量加权的占比，外加它所描述的那份快照与已用到的标签。它是给人看的
  文字，没有任何东西读它；它的每一行都是这棵树的函数，所以没变过的树写出来的报告总是一模一样。
- id、路径与字段名是 ASCII；`domain.domain` 是一个数组,元素取自闭合英文枚举(一到三个,主分类在前),
  依然可以直接筛；domain 角度的值都是英文，其余角度的所有值都是中文。

## 2. 输入

| 什么 | 哪里 | 由谁放进去 |
| --- | --- | --- |
| 镜像：每个 skill 一个目录，外加它自己的索引与元数据 | `<output_dir>/skills` 与 `<output_dir>/upstream` | `just sync`，来自上游 `dist` 分支 |
| 一个 prompt：`prompts/<id>.md`（任务）+ `prompts/<id>.json`（它的 schema） | `prompts_dir` | 你，手工 |
| 共享 system prompt `prompts/_system.md` | `prompts_dir` | 你 |

`upstream/skills.jsonl` 是镜像自己的列表，也是清单的左半边：行集合、批次的工作顺序（安装量降序），
以及这棵树无从知道的那些字段。`skills/<id>/SKILL.md` 是一个 prompt 的全部依据——它旁边的文件是替
「要安装这个 skill 的用户」带的，不参与生成。

每个 skill 的一句话 description 不在镜像索引里（上游已把它去掉）：它读自该 skill 自己的 front matter，
而 front matter 给不出 description 的 skill 永远不会被构建。

镜像是一份拉取来的快照，只读。一个 prompt 是「任务 + 契约」这一对：schema 会原样作为模型服务
的严格 `json_schema` response format 随请求发出。**新增一个角度就是两个文件、零代码。**

## 3. 控制

批次是一个 recipe 加若干修饰符，另有六个动词：

| 命令 | 作用 |
| --- | --- |
| `just` | 构建窗口内所有还缺的 (skill, angle) |
| `just one <angle> <id>` | 构建一个格子，无论它在不在窗口内 |
| `just invalidate <angle>` | 删除这个角度在所有 skill 上的档案 |
| `just index` | 写出清单与报告：镜像的行连接上 description 与 domain，外加 `stats.txt` |
| `just sync` | 拉取镜像，整体替换 `skills/` 与 `upstream/`，并重写清单 |
| `just refresh` | 拉取，并删掉所有「来源 hash 随之变了」的档案 |
| `just clean` | 删掉档案、清单与报告；skill 目录与镜像文件不动 |
| `just render <angle> <id>` · `just test` | 仅开发用：打印请求 · 跑测试 |

修饰符是命令行变量，只在命令行上设置：

| 旋钮 | 默认值 | 含义 |
| --- | --- | --- |
| `limit` | 1 | 按清单自身的顺序（即镜像的顺序，安装量降序）取接下来还缺内容的 N 个 skill；`0` = 全量，无上限。它数的是工作而不是位置，所以反复运行会沿着数据集往下走，档案批次就是这个语义 |
| `prompt` | – | 一个角度，或全部角度 |
| `jobs` | 每个核一个 | 同时在飞的生成数 |
| `rpm` | 0 | 把一次运行配速到端点每分钟的配额 |
| `dry` | – | `1` = 假模型、真布局 |
| `output_dir` `prompts_dir` `snapshot` `py` | 见 [DEVELOPING.zh-CN.md](DEVELOPING.zh-CN.md) | 管路 |

它下面一次一个格子：

```
gen.py <angle> <id> [--print]
```

- stdout 是数据（`--print` 时是那份请求）；stderr 是进度。
- 源文本截断在 20000 字符，且这个截断在源文本内部被声明。
- 退出码：`0` 已构建 · `1` 输入或模型不可用 · `2` 参数错误。front matter 给不出 description 的
  skill 就是「输入不可用」：它被丢弃，stderr 一行，什么都不写。

## 4. 配置

`.env`（复制 [`.env.example`](.env.example)）或 `SKILLS_PROFILES_*`；环境变量 → `.env` → 默认值。
这里只放端点：`MODEL`、`BASE_URL`、`API_KEY`、`MAX_RETRIES`、`TIMEOUT`、`THINKING`、`DRY_RUN`
—— 外加两个路径，如果你确实需要挪动它们。

上面那些批次旋钮**不是**环境变量：一次运行只会因为它自己说了要变而变。

## 5. 消费方可以依赖的东西

- **存在就是缓存。** 已写出的永远不会重建；中断的批次从第一个缺失的文件接着做。
- **失效就是删除。** 改模板本身不会让任何东西失效；新快照会让它改动过的那些失效，而
  `just refresh` 就是删掉这些档案的那个动词。
- **失败不丢东西。** 调用失败不写文件、也不结束批次；下一次运行只重试它。
- **读不出东西的 skill 永远不会被构建。** 只有 front matter 给得出 description 才会发起调用，所以清单
  为它写的是 `description: null`，而窗口会跳过这一行：不调用、不写文件、也没有需要重试的失败。
- **文件要么完整、要么不存在。** 先写 markdown，json 以重命名落位。
- **每个文件一次单轮调用。** 没有顺序、没有依赖、没有级联。
- **清单是派生品，而且是完整的。** `just index` 可以离线地把它整份从树里重建：镜像列出的每个 skill
  一行，另外为「镜像已删除但档案还在」的 skill 补一行——`stats.txt` 出自同一次遍历，所以两者不可能
  描述两棵不同的树。
- **布局是唯一的契约。** 发布时请把 `output/` 原样保留，镜像自己的文件也在里面。

## 6. 待定 —— 在把它定为规范之前需要达成一致

1. `render` 与 `test` 算对外的一面，还是仅开发用（不进入上面的承诺）？
2. `snapshot` 与 `py` 该不该是公开旋钮，还是固定默认值的管路？
