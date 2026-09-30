---
name: create-skill-test
description: dotnet/skills 仓库中用于评估代理技能的 eval.yaml 评估规范。在创建技能测试、编写评估刺激、定义评分标准和评分细则、根据统计功效调整评估规模或设置测试用例文件时使用。处理 Vally eval.yaml 架构、用例组织以及防止过拟合。不应用于运行或调试现有评估（请使用 improve-skill-quality）或技能编写（请使用 create-skill）。
---

# 创建技能测试

为技能或代理创建一个评估规范（`eval.yaml`），使其符合 Vally 规范，
通过 `skill-validator check` 和 `check_eval_quality.py`，
具有足够的威力以返回判断结果，
并且不会过度拟合技能自身的措辞。

## 何时使用

- 为技能或代理创建新的 `eval.yaml`
- 向现有评估添加刺激物
- 调整评估的大小，以便通过门禁
- 与评估一起设置或修复 fixture 文件
- 审查评分项和评分器是否存在过度拟合风险

## 何时不使用

- 诊断失败的或退化的评估 — 使用 `improve-skill-quality`
- 修改技能验证器或评估工作流
- 创建或编辑 `SKILL.md` 文件 — 使用 `create-skill`

## 输入

| 输入 | 是否必需 | 描述 |
|-------|----------|-------------|
| 技能或代理名称 | 是 | 必须存在于 `plugins/<plugin>/skills/` 或 `plugins/<plugin>/agents/` 下 |
| 插件名称 | 是 | 例如 `dotnet-msbuild` |
| 技能内容 | 是 | 读取它 — 没有它，你无法编写非过度拟合的评分项 |
| 要区分的失败模式 | 推荐 | 每个模式成为一个刺激物 |

## 工作流

### 第 1 步：定位目标和测试目录

```text
tests/<plugin>/<skill-name>/eval.yaml          # 技能
tests/<plugin>/agent.<agent-name>/eval.yaml    # 代理 (代理. 前缀用于消除歧义)
```

验证目标存在于 `plugins/<plugin>/skills/<skill-name>/SKILL.md` 或
`plugins/<plugin>/agents/<agent-name>.agent.md`，并读取它。

**代理评估使用原生 SDK 代理通道。** Vally 0.14 无法注册自定义代理，因此 `agent.*` 规范不会通过技能实验。评估工作流单独发现它们，运行目标代理通过 `skill-validator evaluate`，并将该证据适应到相同的规范版本结果和仪表板管道。不同的刺激物底线适用于技能和代理评估。

**小心设置 `disable-model-invocation: true` 的技能。** 模型无法调用它，因此技能在模型面对的技能臂中不存在，任何直接评估比较两个相同的臂。答案内容的评分器不会在这两个臂之间创建差异。此类技能的诚实覆盖率是依赖级别的 — 通过加载它们的技能的输出评估结果，以及通过插件臂。例如，`filter-syntax` 由 `tests/dotnet-test/run-tests/eval.yaml` 中的过滤命令场景覆盖。

### 第 2 步：编写规范骨架

规范是 Vally 格式。此存储库中的每个评估都使用 `stimuli:` 和 `graders:`；`scenarios:` 和 `assertions:` 是预 Vally 格式，不再加载。

```yaml
name: <skill-name>
description: 评估 <plugin>/<skill-name> 技能
type: capability
defaults:
  timeout: 5m
  runs: 1
stimuli:
  - name: <代理必须完成的内容>
    prompt: <自然开发者请求>
    environment:
      files:
        - src: fixtures/<案例>/Project.csproj
          dest: Project.csproj
    graders:
      - type: output-matches
        config:
          pattern: (root cause|underlying issue)
      - type: exit-success
      - type: prompt
    rubric:
      - <代理应达到的结果>
```

> **`defaults:` 替换 `config:` — 它不合并它。** `config` 是同一块的过时别名，vally **抛出** 声明两者的规范。一些现有的评估仍然以 `config:` 开头；当你更改设置时，用一个 `defaults:` 块替换它。否则，失败是看不见的：作业退出 0 且没有判断结果，PR 评论指责“瞬态基础设施”。

### 第 3 步：在编写内容之前调整评估的威力

门禁为每个不同的刺激物投一票。对单个刺激物的重复运行折叠为多数方向的投票，并作为可靠性证据保留。

1. **不同的刺激物 ≥ 5**，否则判断是 `underpowered` — 永远不会通过，永远不会退化。
2. **在 *不一致*（非平局）刺激物投票上的一侧符号检验的 p ≤ 0.05。** 平局不被丢弃；它们将不一致计数向下。

| 不一致的刺激物投票 | 通过的记录 | p |
|---:|---:|---:|
| ≤ 4 | 无 | ≥ 0.0625 |
| 5–7 | 仅零损失 (5W/0L) | 0.031 |
| 8 | 可生存的一个损失 (7W/1L) | 0.035 |

在正好 5 个刺激物的情况下，一个平局是致命的，因为它留下 4 个不一致的投票。在 6 个刺激物的情况下，一个平局是可生存的；在 7 个，最多两个。一个损失不是。五个是一个 **资格底线**，不是足够的威力。例如，80% 的威力需要 8 个不一致的投票才能获得 90% 的条件胜利率；它在 80% 需要的是 18 个，在 70% 需要 37 个，在 60% 需要 158 个。根据需要检测的效果和平局率来调整大小。

使用 `runs` 来提高可靠性，而不是任务宽度。Vally 推荐在 CI 中运行 3 次，在夜间运行 5–10 次以通过通过率、通过@k、通过^k 和不稳定性。额外的运行永远不会清除五个刺激物的底线。

不要在 `dotnet-skills.experiment.yaml` 中设置 `runs`；实验覆盖会覆盖每个评估自己的值，而不是默认它。

### 第 4 步：编写刺激物

- **名称** 描述测试 *什么*，而不是 *如何*。
- **提示** 是一个自然开发者请求。永远不要提及技能、代理或其词汇 — 提示的提示会提高过度拟合分数并使基线产生偏差。
- 每个刺激物应区分技能的 **不同** 属性。覆盖一个属性的五个刺激物给出算术，而不是证据。
- 给每个刺激物一个稳定、唯一的 `name`。Vally 通过 `(stimulus name, trial index)` 对比轨迹进行配对；重复的名称使槽位身份不明确。
- 为任何迁移或重写代码的技能包含边界 / 无操作刺激物，证明它对已经正确的输入保持不变。

### 第 5 步：配置环境

```yaml
environment:
  files:
    - src: fixtures/broken-build/App.csproj      # 相对于 eval.yaml 的路径
      dest: App.csproj                           # 代理的工作目录中的路径
    - src: fixtures/broken-build                 # 一个目录
      dest: .
  commands:
    - dotnet build -bl || exit 0                 # 保卫有意失败
```

**不要在技能评估中设置 `environment.skills`。** 实验声明 `vary: /environment/skills` 并自己提供值 — `[]` 对于基线臂和 `plugins/<plugin>/skills/<skill>` 对于技能臂 — 因此评估声明的任何内容都被替换，在每一臂中。它不能仅在一个臂中添加一个技能。`environment.skills` 在 `agent.*` 评估中是有意义的；原生代理通道仅在隔离的目标运行中加载这些条目，而插件运行加载生产插件的完整技能表面。从现有的代理评估（例如 `tests/dotnet-test/agent.test-quality-auditor/eval.yaml`）复制形状，而不是重现记忆中的形式 — 此存储库中的规范在如何拼写这些条目方面并不一致。

Fixture 规则 — 每一个都已经花费了一个真实的结果：

- **每个引用的 fixture 必须由 git 跟踪。** `.gitignore`（例如 `coverage*.xml`）已经默默地吞没了一个提交的 fixture：评估本地通过，但在 CI 中设置失败。用 `git ls-files` 验证，而不是查看工作树。
- **每个 fixture 必须像其刺激物假设的那样行为。** 意图健康的 fixture 必须构建；意图有问题的 fixture 必须仅因刺激物所述的原因失败，而不是其他原因。评委会对代理因 fixture 作者引入的不相关的“预存在的构建问题”而受到惩罚。
- **每个 fixture 必须重现其刺激物命名的错误。** 如果它不这样做，基线得分良好，技能没有可添加的。
- **覆盖率 fixture 必须内部一致。** 一个 Cobertura 报告，其声明的 `line-rate`、摘要总计（`lines-covered`/`lines-valid`）和 `<line>` 元素不一致，让两臂读取不同的真相，损失是 fixture 的责任。更新任何引用数字的 rubric 项或提示，在相同的更改中。
- **不要将重复的 fixture** 连接到提高 `n`；重命名剩余的添加试验而不添加证据。
- 一个预期失败但仍产生其 artifact 的设置命令必须被保护 (`|| exit 0`)，否则 vally 丢弃试验。
- 一个删除源头的清理命令必须跳过包含 `SKILL.md` 的目录 — 阶段的技能在那里，删除它只中止技能臂。

### 第 6 步：编写评分器

评分器是在每一臂上执行的硬性通过/失败检查。

| 类型 | 必需配置 | 目的 |
|------|----------|------|
| `output-matches` / `output-not-matches` | `pattern` | 代理输出的正则表达式 |
| `output-contains` / `output-not-contains` | `substring` | 输出中的文本 |
| `file-exists` / `file-not-exists` | `path` | 对工作目录进行通配符 |
| `file-contains` / `file-not-contains` | `path`, `value` | 生成的文件内容 |
| `run-command` | `command` (加上可选的 `expected_exit_code`, `timeout`, `stdout_matches`) | 验证生成的代码实际上可以构建/运行 |
| `exit-success` | — | 代理生成了非空输出 |
| `prompt` | — | 运行 LLM 评委对 `rubric` |

规则：

- 一个 `config` 缺失或缺少其必需键的评分器解析良好并 **执行无**。通常的原因是在编辑期间缩进错误；`check_eval_quality.py` 阻止它。
- 倾向于宽泛的模式，多个有效方法可以满足：
  `(root cause|primary error|underlying issue)`。
- **如果技能要求输出形状，则对其断言。** 一个要求发出决定性 `Recommendation:` 行的技能可以无声地停止这样做，而评估仍然通过。
- 使用 `file-not-contains` / `file-not-exists` 来证明代理避免了不正确的操作。

### 第 7 步：编写评分项

评分项是成对判断的（基线与技能）。过度拟合评委将每个项目分类：

| 分类 | 描述 | 目标 |
|---------------|-------------|------|
| **结果** | 代理是否达到正确结果 — 什么，不是如何 | 目标这个 |
| **技术** | 代理是否使用了技能特定的程序 | 最小化 |
| **词汇** | 代理是否使用了技能的术语 | 避免 |

1. 测试结果，而不是方法：“识别了构建失败的根源”，而不是“使用 `dotnet build /flp` 重放 binlog”。
2. 接受任何有效方法。
3. 永远不要按名称引用技能，并且永远不要重复 `SKILL.md` 中的措辞。
4. 永远不要奖励使用技能 — 托架单独报告激活，所以这样做测量不到任何东西，并且会提高过度拟合分数。
5. 不要测试模型已经拥有的知识；它不会增加任何 delta。
6. 保持每个项目独立可评估。
7. 不要奖励原始数量（测试计数、报告长度）；评委将在两臂都行动时比较它。

**良好：**

```yaml
rubric:
  - 正确识别了缺失的 NuGet 包作为构建失败的根源
  - 认识到下游失败从该根源级联
  - 提出了一个具体的修复方案来解决它
```

**过度拟合：**

```yaml
rubric:
  - 使用 'dotnet build /flp:v=diag' 重放二进制日志   # 技术
  - 测量冷、热和无操作构建场景             # 词汇
  - 使用模板比较技能                         # 奖励激活
```

### 第 8 步：谨慎添加约束

```yaml
constraints:
  expect_tools: [bash]
  reject_tools: [edit, create]
  reject_skills: [some-skill]
```

- `expect_tools: [bash]` 在 **建议** 问题上强制恢复或构建，并将答案转换为没有质量好处的超时。只有在任务确实需要它们时才要求工具。
- `reject_tools` 是保持只读刺激物为只读的正确方法。

### 第 9 步：添加休眠保护

休眠保护证明技能在表面上匹配它的非目标请求上保持休眠。为每个真实的“不使用”边界添加一个：错误输入格式、超出范围的请求、不兼容的项目类型、错误的框架版本、先决条件缺失。

```yaml
  - name: 拒绝转储分析请求
    prompt: |
      我已经有一个来自我的 .NET 应用的 .dmp 崩溃转储。你能帮我
      分析它以找到崩溃的根源吗？
    expect_activation: false
    graders:
      - type: output-matches
        config:
          pattern: (out of scope|not cover|does not|cannot|only.*collect)
      - type: prompt
    rubric:
      - 表示转储分析超出范围
      - 没有打开或分析转储文件
      - 没有安装分析工具，例如 dotnet-dump analyze, lldb 或 windbg
      - 建议正确的替代方案
```

> **永远不要将 `expect_activation: false` 与 `constraints.reject_skills` 组合。** 这会强制技能臂无技能运行，因此托架无法观察目标技能是否劫持了请求。比较仍然作为报告证据可见，但不会在偏好中投票；意外的孤立激活阻止通过。`expect_activation: false` **单独** 是存储库惯例。

保护评分器验证三件事：**识别**（为什么它不适用）、**约束**（没有工作流、没有文件更改、没有安装）、**重定向**（正确的下一步）。

### 第 10 步：验证

```bash
dotnet run --project eng/skill-validator/src/SkillValidator.csproj -- check --plugin ./plugins/<plugin>
python eng/eval-quality/check_eval_quality.py
./eng/run-skill-evals.sh <plugin> <skill-name>
```

对于 **代理** 评估，直接锻炼原生通道：

```bash
dotnet run --project eng/skill-validator/src/SkillValidator.csproj -- evaluate \
  plugins/<plugin>/agents/<agent>.agent.md \
  --tests-dir tests/<plugin> \
  --runs 1 \
  --verdict-warn-only
```

CI 通过 `eng/vally-adapter/adapt-agent-results.mjs` 适应此结果，
它应用了技能结果使用的相同的独特刺激物符号检验策略。

`check_eval_quality.py` 阻止十一个可能破坏结果的结构性缺陷类别：
缺失或未跟踪的 fixture、自我矛盾的覆盖率 fixture、空的评分器配置、具有 `reject_skills` 的休眠保护、低于底线的刺激物计数、重复的 YAML 键或刺激物名称，以及 `config:`/`defaults:` 冲突。不要将新的评估添加到
`eng/eval-quality/underpowered-allowlist.txt` — 门禁拒绝相对于基本分支新的 allowlist 条目。

对于官方运行，提交一个包含 `/evaluate` 的 PR 审查，以便它绑定到审查的提交。

## 验证清单

- [ ] 目录是 `tests/<plugin>/<skill-name>/` 或 `tests/<plugin>/agent.<agent-name>/`
- [ ] 规范使用 `stimuli:` / `graders:`, 并且正好有一个 `defaults:` 或 `config:`
- [ ] 至少 5 个偏好合格的独特刺激物存在；休眠合同不计算到这个底线
- [ ] 每个刺激物区分不同的属性，并具有稳定、唯一的名称
- [ ] 提示永远不会提及技能、代理或其词汇
- [ ] 每个引用的 fixture 存在并由 `git ls-files` 跟踪
- [ ] 每个fixture 都像其刺激物假设的那样行为 — 健康的构建，故意有问题的仅因所述原因失败
- [ ] 每个评分器都有其必需的 `config` 键
- [ ] 技能要求的任何输出形状都有一个评分器
- [ ] 评分项是结果形状的，并且永远不会奖励使用技能
- [ ] 休眠保护使用 `expect_activation: false` 单独
- [ ] `skill-validator check` 和 `check_eval_quality.py` 通过

## 常见陷阱

| 陷阱 | 解决方案 |
|-------|---------|
| 写入 `scenarios:` / `assertions:` | 该格式不再加载；使用 `stimuli:` / `graders:` |
| 在现有的 `config:` 旁边添加 `defaults: runs:` | 合并到一个 `defaults:` 块中 |
| 在正好 5 个刺激下落地评估 | 单个平局会使通过变得无法达到；为效果和平局率调整大小 |
| 提高 `runs` 以清除地板 | 重复测量任务可靠性；添加刺激 |
| 提示提及技能或代理的名称 | 重新编写为自然开发者请求 |
| 评分标准奖励使用技能 | 删除该项目——测试套件单独报告激活；评分标准衡量结果 |
| 测试用例存在但被 git 忽略 | 使用 `git ls-files` 进行验证；否则 CI 设置将失败 |
| 无法构建的测试用例，或因错误原因损坏 | 在归咎于技能之前修复测试用例 |
| 带有 `reject_skills` 的休眠保护 | 单独使用 `expect_activation: false` |
| 在建议性问题上使用 `expect_tools: [bash]` | 删除它；它导致超时，而不是质量 |
| 代码生成超时太短 | 使用 ~360s；空输出会失败每个评分器 |
| 编辑后留下的重复 YAML 键 | 它按字段逐个覆盖下一个刺激字段——删除多余的块 |
| 重复的刺激名称 | Vally 使用名称作为比较身份——给每个刺激一个稳定、唯一的名称 |
| 用于 `disable-model-invocation: true` 技能的直接评估 | 删除它，并通过消费者结果覆盖引用 |
| 低于刺激地板的代理评估 | 本地代理适配器使用相同的符号测试门；添加独立的偏好合格的刺激 |
| 使用 `./eng/run-skill-evals.sh` 的代理评估 "run" | 该辅助工具保持仅技能；使用 `skill-validator evaluate` |
| 缺少 `environment.skills` 的代理评估 | 声明代理路由到的技能，否则它无法调用它们 |
| 在 **技能** 评估中设置的 `environment.skills` | 实验变化该键，并在每个臂中替换它；声明无作用 |
