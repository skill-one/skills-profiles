# skills-profiles: 对外的那一面

黑盒视角：用户或消费方能看见的一切，完全不涉及它内部怎么实现的。

**产物是一个目录** —— `output/`：一棵中文档案的目录树，每个 skill 六个角度，每个角度都是一次围绕
该 skill `SKILL.md` 的 LLM 单轮调用，而生成这些档案所依据的快照就放在它们旁边。生成器是为了产出这
个目录而存在的，所以它就是接口，命令只决定其中哪一部分被写出来。

English: [SPEC.md](SPEC.md)

## 1. 输出 —— 接口本身

```
<output_dir>/
├── skills/<id>/
│   ├── domain.json  scenario.json  tagline.json
│   ├── blackbox.json  whitebox.json  comments.json
│   └── md/<angle>.md      # 同样的内容，渲染成方便阅读的版本
├── skills.jsonl           # `just index`：这棵树的列表，每个 skill 一行、扁平
└── cache/skills-sh/       # 这些档案所依据的上游快照
```

`<id>` 是 skill id，即 `{owner}/{repo}/{slug}`，其中的 `:` 与 `&` 改写成 `_`。它是与上游镜像、
与 `https://www.skills.sh/<id>` 之间的关联键。

| 角度 | json 结构 | 内容 |
| --- | --- | --- |
| `domain` | `{domain, reason}` | 13 个闭合分类之一，加一句话理由 |
| `scenario` | `{text}` | 一段 100 字以内的场景化介绍，从用户痛点切入 |
| `tagline` | `{taglines[3]}` | 3 条宣传短标语，每条 20 字以内 |
| `blackbox` | `{function, input_output[3–5]}` | 黑盒视角：你给什么 → 你得到什么 |
| `whitebox` | `{execution_flow[3–5], mechanisms[2–3]}` | 白盒视角：主路径、关键机制、真实依赖 |
| `comments` | `{comments[4–6]}` | 用户第一人称评论：`{user, category, comment}` |

- 每个 skill 一个目录，每个角度一个文件。各角度彼此独立——没有任何文件读另一个文件。
- `.json` 是数据；`md/<angle>.md` 是同样字段的渲染版，先写。
- **这棵树是唯一的契约。** `skills.jsonl` 是它的派生列表，由 `just index` 写出：每个 skill 一行、
  扁平——`{id, domain, reason}`，按路径顺序，还没生成 domain 的 skill 不占一行。没有任何东西读它。
- id、路径与字段名是 ASCII；所有值都是中文。`domain.domain` 是闭合枚举，可以直接筛。

## 2. 输入

| 什么 | 哪里 | 由谁放进去 |
| --- | --- | --- |
| 快照：`skills/<id>/SKILL.md` 以及它旁边的文件 | `data_dir`——默认就是 `output_dir/cache/skills-sh`，所以它会跟档案一起发布 | `just sync`，来自上游 `dist` 分支 |
| 一个 prompt：`prompts/<id>.md`（任务）+ `prompts/<id>.json`（它的 schema） | `prompts_dir` | 你，手工 |
| 共享 system prompt `prompts/_system.md` | `prompts_dir` | 你 |

快照自带的 `skills.jsonl`——和输出根目录那份档案索引是**两个不同的文件**——是运行除了源文件之外会读
的唯一一个快照文件：它给窗口排序，安装量降序。不在、或形状不对时，窗口退回目录树的路径顺序。

快照是拉取来的镜像，只读。一个 prompt 是「任务 + 契约」这一对：schema 会原样作为模型服务
的严格 `json_schema` response format 随请求发出。**新增一个角度就是两个文件、零代码。**

## 3. 控制

批次是一个 recipe 加若干修饰符，另有六个动词：

| 命令 | 作用 |
| --- | --- |
| `just` | 构建窗口内所有还缺的 (skill, angle) |
| `just one <angle> <id>` | 构建一个格子，无论它在不在窗口内 |
| `just invalidate <angle>` | 删除这个角度在所有 skill 上的输出 |
| `just index` | 把已生成的 domain 折成 `skills.jsonl` |
| `just sync` | 拉取快照，整体替换 |
| `just refresh` | 拉取，并删掉所有「来源 hash 随之变了」的档案 |
| `just clean` | 删掉档案——`skills/` 与 `skills.jsonl`；快照不动 |
| `just render <angle> <id>` · `just test` | 仅开发用：打印请求 · 跑测试 |

修饰符是命令行变量，只在命令行上设置：

| 旋钮 | 默认值 | 含义 |
| --- | --- | --- |
| `limit` | 1 | 按快照自身的顺序（安装量降序）取前 N 个 skill；`0` = 全量，无上限 |
| `prompt` | – | 一个角度，或全部角度 |
| `jobs` | 每个核一个 | 同时在飞的生成数 |
| `rpm` | 0 | 把一次运行配速到端点每分钟的配额 |
| `dry` | – | `1` = 假模型、真布局 |
| `data_dir` `output_dir` `prompts_dir` `snapshot` `py` | 见 [DEVELOPING.zh-CN.md](DEVELOPING.zh-CN.md) | 管路 |

它下面一次一个格子：

```
gen.py <angle> <id> [--print]
```

- stdout 是数据（`--print` 时是那份请求）；stderr 是进度。
- 源文本截断在 20000 字符，且这个截断在源文本内部被声明。
- 退出码：`0` 已构建 · `1` 输入或模型不可用 · `2` 参数错误。

## 4. 配置

`.env`（复制 [`.env.example`](.env.example)）或 `SKILLS_PROFILES_*`；环境变量 → `.env` → 默认值。
这里只放端点：`MODEL`、`BASE_URL`、`API_KEY`、`MAX_RETRIES`、`TIMEOUT`、`THINKING`、`DRY_RUN`
—— 外加三个路径，如果你确实需要挪动它们。

上面那些批次旋钮**不是**环境变量：一次运行只会因为它自己说了要变而变。

## 5. 消费方可以依赖的东西

- **存在就是缓存。** 已写出的永远不会重建；中断的批次从第一个缺失的文件接着做。
- **失效就是删除。** 改模板本身不会让任何东西失效；新快照会让它改动过的那些失效，而
  `just refresh` 就是删掉这些档案的那个动词。
- **失败不丢东西。** 调用失败不写文件、也不结束批次；下一次运行只重试它。
- **文件要么完整、要么不存在。** 先写 markdown，json 以重命名落位。
- **每个文件一次单轮调用。** 没有顺序、没有依赖、没有级联。
- **索引可选且是派生品。** `skills.jsonl` 可能不存在、也可能比树旧——重建它的唯一方式是
  `just index`，除此之外没有任何东西会写它。
- **布局是唯一的契约。** 发布时请把 `output/` 原样保留，快照也在里面。

## 6. 待定 —— 在把它定为规范之前需要达成一致

1. `render` 与 `test` 算对外的一面，还是仅开发用（不进入上面的承诺）？
2. `snapshot` 与 `py` 该不该是公开旋钮，还是固定默认值的管路？
