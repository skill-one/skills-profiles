# 创建技能测试

为技能或代理创建一个评估规范（`eval.yaml`），使其符合 Vally 规范，
通过 `skill-validator check` 和 `check_eval_quality.py`，
具有足够的威力以返回判断结果，
并且不会过度拟合技能自身的措辞。

## 使用场景

- 为技能或代理创建新的 `eval.yaml`
- 向现有评估添加刺激物
- 调整评估规模，以便通过门禁
- 与评估一起设置或修复 fixture 文件
- 审查评分项和评分器是否存在过度拟合风险

## 不适用场景

- 诊断失败的或退化的评估 — 使用 `improve-skill-quality`
- 修改技能验证器或评估工作流
- 创建或编辑 `SKILL.md` 文件 — 使用 `create-skill`

## 输入

| 输入 | 是否必需 | 描述 |
|-------|----------|-------------|
| 技能或代理名称 | 是 | 必须存在于 `plugins/<plugin>/skills/` 或 `plugins/<plugin>/agents/` 下 |
| 插件名称 | 是 | 例如 `dotnet-msbuild` |
| 技能内容 | 是 | 必须读取 — 没有它无法编写非过度拟合的评分项 |
| 需要区分的失败模式 | 推荐使用 | 每个模式成为一条刺激物 |

## 工作流

### 第 1 步：定位目标和测试目录

```text
tests/<plugin>/<skill-name>/eval.yaml          # 技能
tests/<plugin>/agent.<agent-name>/eval.yaml    # 代理 (代理. 前缀消除歧义)
```

验证目标存在于 `plugins/<plugin>/skills/<skill-name>/SKILL.md` 或
`plugins/<plugin>/agents/<agent-name>.agent.md`，并读取它。

**代理评估使用原生 SDK 代理通道。** Vally 0.14 无法注册自定义代理，
因此 `agent.*` 规范不会通过技能实验。评估工作流单独发现它们，
运行目标代理通过 `skill-validator evaluate`，
并将该证据适应到相同的规范版本结果和仪表板管道。不同的刺激物底线适用于技能和代理评估。

**小心设置 `disable-model-invocation: true` 的技能。** 模型无法调用它，
因此技能在模型面对的熟练臂中不存在，任何直接评估比较两个相同的臂。答案内容评分器不会在这两个臂之间创建差异。此类技能的诚实覆盖率是依赖级别的 — 通过加载它们的技能的输出评估，
以及通过插件臂。例如，`filter-syntax` 由 `tests/dotnet-test/run-tests/eval.yaml` 中的过滤命令场景覆盖。

### 第 2 步：编写规范骨架

规范是 Vally 格式。本仓库中的每个评估都使用 `stimuli:` 和 `graders:`；`scenarios:` 和
`assertions:` 是预 Vally 格式，不再加载。

```yaml
name: <skill-name>
description: 评估 <plugin>/<skill-name> 技能
type: capability
defaults:
  timeout: 5m
  runs: 1
stimuli:
  - name: <代理必须完成的任务>
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

> **`defaults:` 替换 `config:` — 它不合并它。** `config` 是 `defaults:` 块的已弃用别名，
> vally 在规范声明两者时 **抛出** 错误。一些现有的评估仍然以 `config:` 开头；
> 当你更改设置时，用单个 `defaults:` 块替换它。否则失败是看不见的：作业退出 0 且没有判断结果，
> PR 评论指责“瞬态基础设施”。

### 第 3 步：在编写内容之前调整评估的威力

门禁为每个不同的刺激物投一票。针对一个刺激物的重复运行折叠为一个多数方向投票，
并作为可靠性证据保留。

1. **不同的刺激物 ≥ 5**，否则判断结果为 `underpowered` — 永远不会通过，永远不会退化。
2. **在 *不一致*（非平局）刺激物投票上的一侧符号检验的 p ≤ 0.05。** 平局不被丢弃；它们将不一致计数向下。

| 不一致刺激物投票 | 通过的记录 | p |
|---:|---:|---:|
| ≤ 4 | 无 | ≥ 0.0625 |
| 5–7 | 仅零损失（5W/0L） | 0.031 |
| 8 | 可存活一个损失（7W/1L） | 0.035 |

在正好 5 个刺激物时，一个平局是致命的，因为它留下 4 个不一致投票。在 6 个刺激物时，一个平局是可存活的；在 7 个，最多两个。损失不是。五个是一个 **资格底线**，不是足够的威力。例如，80% 威力只需要 8 个不一致投票才能达到真正的 90% 条件胜率；
它在 80% 时需要 18 个，在 70% 时需要 37 个，在 60% 时需要 158 个。根据需要检测的效果和平局率调整规模。

使用 `runs` 进行可靠性，而不是任务广度。Vally 推荐在 CI 中运行 3 次，在夜间运行 5–10 次以通过通过率、通过@k、通过^k 和 flakiness。额外的运行永远不会清除五个刺激物的底线。

不要在 `dotnet-skills.experiment.yaml` 中设置 `runs`；实验覆盖会覆盖每个评估自己的值，而不是默认值。

### 第 4 步：编写刺激物

- **名称** 描述测试的内容，而不是如何测试。
- **提示** 是一个自然开发者请求。永远不要提及技能、代理或其词汇 — 提示的提示会提高过度拟合分数并使基线产生偏差。
- 每个刺激物应区分技能的 **不同** 属性。一个属性覆盖五个刺激物提供算术，而不是证据。
- 给每个刺激物一个稳定、唯一的 `name`。Vally 通过 `(stimulus name, trial index)` 对比较轨迹进行配对；重复的名称使槽位身份不明确。
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

**不要在技能评估中设置 `environment.skills`。** 实验声明
`vary: /environment/skills` 并自己提供该值 — `[]` 对于基线臂和
`plugins/<plugin>/skills/<skill>` 对于熟练臂 — 因此任何评估声明的都是被替换，
在每条臂中。它不能仅向一条臂添加技能。`environment.skills` 在代理.* 评估中有意义；
原生代理通道仅在隔离的目标运行中加载这些条目，而插件运行加载生产插件的完整技能表面。从现有的代理评估（例如
`tests/dotnet-test/agent.test-quality-auditor/eval.yaml`）复制形状，而不是重现记忆中的形式 —
本仓库中的规范在如何拼写这些条目方面并不一致。

Fixture 规则 — 每个规则已经花费了一个真实结果：

- **每个引用的 fixture 必须由 git 跟踪。** `.gitignore`（例如 `coverage*.xml`）已经默默地吞没了提交的 fixture：评估本地通过，但在 CI 中设置失败。用 `git ls-files` 验证，而不是查看工作树。
- **每个 fixture 必须像其刺激物假设的那样行为。** 意图健康的 fixture 必须构建；意图有问题的 fixture 必须仅因刺激物声明的确切原因失败，而不是其他原因。裁判会惩罚代理因 fixture 作者引入的不相关的“预现有构建问题”。
- **每个 fixture 必须重现其刺激物命名的错误。** 如果它不这样做，基线得分良好，技能没有可添加的。
- **覆盖率 fixture 必须内部一致。** 一个 Cobertura 报告，其声明的 `line-rate`、摘要总计（`lines-covered`/`lines-valid`）和 `<line>` 元素不一致，让两条臂读取不同的真相，损失是 fixture 的责任。更新任何引用数字的 rubric 项或提示。
- **不要连接重复的 fixture** 来提高 `n`；重命名剩余物会添加试验而不添加证据。
- 一个预期会失败但仍会生成其 artifact 的设置命令必须被保护（`|| exit 0`），否则 vally 会丢弃试验。
- 一个删除源代码的清理命令必须跳过包含 `SKILL.md` 的目录 — 阶段的技能在那里，删除它只会中止熟练臂。

### 第 6 步：编写评分器

评分器是在每条臂上执行的硬性通过/失败检查。

| 类型 | 必需配置 | 目的 |
|------|----------|---------|
| `output-matches` / `output-not-matches` | `pattern` | 代理输出的正则表达式 |
| `output-contains` / `output-not-contains` | `substring` | 输出中的文本 |
| `file-exists` / `file-not-exists` | `path` | 对工作目录进行通配符匹配 |
| `file-contains` / `file-not-contains` | `path`, `value` | 生成的文件内容 |
| `run-command` | `command`（以及可选的 `expected_exit_code`, `timeout`, `stdout_matches`） | 验证生成的代码实际构建/运行 |
| `exit-success` | — | 代理生成了非空输出 |
| `prompt` | — | 运行 LLM 裁判对 `rubric` |

规则：

- 一个 `config` 缺失或缺少其必需键的裁判解析良好并 **执行无操作**。
  通常原因是编辑时的缩进错误；`check_eval_quality.py` 会阻止它。
- 优先使用多个有效方法可以满足的广泛模式：
  `(root cause|primary error|underlying issue)`。
- **如果技能要求输出形状，则断言它。** 一个要求发出决定性 `Recommendation:` 行的技能可以无声地停止这样做，而评估仍然通过。
- 使用 `file-not-contains` / `file-not-exists` 来证明代理避免了不正确的操作。

### 第 7 步：编写评分项

评分项是成对判断的（基线与熟练）。过度拟合裁判将每个项目分类：

| 分类 | 描述 | 目标 |
|---------------|-------------|------|
| **结果** | 代理是否达到正确结果 — 内容，不是方法 | 目标这个 |
| **技术** | 代理是否使用了技能特定程序 | 最小化 |
| **词汇** | 代理是否使用了技能的术语 | 避免 |

1. 测试结果，而不是方法：“识别了构建失败的根源”，而不是“使用 `dotnet build /flp` 重放 binlog”。
2. 接受任何有效方法。
3. 永远不要按名称引用技能，也永远不要重复 `SKILL.md` 提法。
4. 永远不要奖励使用技能 — 框架报告激活情况，所以一个这样做测量无物并使过度拟合分数膨胀的评分项。
5. 不要测试模型已经拥有的知识；它不会增加 delta。
6. 保持每个项目可以独立评估。
7. 不要奖励原始数量（测试计数、报告长度）；裁判将在两条臂都行动时比较它。

**良好：**

```yaml
rubric:
  - 正确识别了缺失的 NuGet 包作为构建失败的根源
  - 认识到下游失败从那个根源级联
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

- `expect_tools: [bash]` 在一个 **建议性** 问题上强制恢复或构建，并将答案转换为没有质量益处的超时。只有在任务真正需要它们时才要求工具。
- `reject_tools` 是保持只读刺激物只读的正确方法。

### 第 9 步：添加休眠保护

一个休眠保护证明技能在表面上匹配它的非目标请求上保持休眠。为每个真实的“不使用”边界添加一个：错误输入格式、超出范围的请求、不兼容的项目类型、错误的框架版本、先决条件缺失。

```yaml
  - name: 拒绝转储分析请求
    prompt: |
      我已经有一个来自我的 .NET 应用的 .dmp 崩溃转储。你能帮我分析它以找到崩溃的根源吗？
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

> **永远不要将 `expect_activation: false` 与 `constraints.reject_skills` 组合。** 这会强制熟练臂无技能运行，所以框架无法观察目标技能是否劫持了请求。比较仍然作为报告证据可见，但不会投票偏好；意外的孤立激活阻止通过。`expect_activation: false` **单独** 是仓库惯例。

保护评分器验证三件事：**识别**（为什么它不适用）、**约束**（无工作流、无文件更改、无安装）、**重定向**（正确的下一步）。

### 第 10 步：验证

```bash
dotnet run --project eng/skill-validator/src/SkillValidator.csproj -- check --plugin ./plugins/<plugin>
python eng/eval-quality/check_eval_quality.py
./eng/run-skill-evals.sh <plugin> <skill-name>
```

对于一个 **代理** 评估，直接锻炼原生通道：

```bash
dotnet run --project eng/skill-validator/src/SkillValidator.csproj -- evaluate \
  plugins/<plugin>/agents/<agent>.agent.md \
  --tests-dir tests/<plugin> \
  --runs 1 \
  --verdict-warn-only
```

CI 通过 `eng/vally-adapter/adapt-agent-results.mjs` 适应此结果，
它应用技能结果使用的相同的独特刺激物符号检验策略。

`check_eval_quality.py` 阻止十一个可能破坏结果的结构性缺陷类别：
缺失或未跟踪的 fixture、自我矛盾的覆盖率 fixture、空的裁判配置、具有 `reject_skills` 的休眠保护、低于底线的刺激物计数、重复的 YAML 键或刺激物名称，以及 `config:`/`defaults:` 冲突。不要将新的评估添加到
`eng/eval-quality/underpowered-allowlist.txt` — 起门拒绝相对于基本分支新的 allowlist 条目。

对于官方运行，提交一个包含 `/evaluate` 的 PR 审查，以便它绑定到审查的提交。

## 验证清单

- [ ] 目录是 `tests/<plugin>/<skill-name>/` 或 `tests/<plugin>/agent.<agent-name>/`
- [ ] 规范使用 `stimuli:` / `graders:`, 并且正好一个 `defaults:` 或 `config:`
- [ ] 至少 5 个偏好合格的独特刺激物存在；休眠合同不计算到这个底线
- [ ] 每个刺激物区分不同的属性，并具有稳定、唯一的名称
- [ ] 提示永远不会提及技能、代理或其词汇
- [ ] 每个引用的 fixture 存在并由 `git ls-files` 跟踪
- [ ] 每个fixture 都像其刺激物假设的那样行为 — 健康的构建，故意有问题的仅因声明的确切原因失败
- [ ] 每个裁判都有其必需的 `config` 键
- [ ] 任何技能要求的输出形状都有一个裁判
- [ ] 评分项是结果形状的，并且永远不会奖励使用技能
- [ ] 休眠保护使用 `expect_activation: false` 单独
- [ ] `skill-validator check` 和 `check_eval_quality.py` 通过

## 常见陷阱

| 陷阱 | 解决方案 |
|---------|----------|
| 编写 `scenarios:` / `assertions:` | 该格式不再加载；使用 `stimuli:` / `graders:` |
| 在现有 `config:` 旁边添加 `defaults: runs:` | 合并到一个 `defaults:` 块 |
| 恰好 5 个刺激物导致评估 | 一个平局使通过无法实现；根据效果和平局率调整规模 |
| 提高 `runs` 以清除底线 | 重复测量单个任务的可靠性；添加刺激物 |
| 提示提及技能或代理的名称 | 重新编写为自然开发者请求 |
| 评分项奖励使用技能 | 删除该项目 — 框架报告激活情况；评分项测量结果 |
| fixture 存在但被 git 忽略 | 用 `git ls-files` 验证；否则 CI 设置会失败 |
| fixture 无法构建，或因错误原因失败 | 在指责技能之前修复 fixture |
| 休眠保护具有 `reject_skills` | 使用 `expect_activation: false` 单独 |
| 在建议性问题上的 `expect_tools: [bash]` | 删除它；它导致超时，而不是质量 |
| 代码生成超时太短 | 使用 ~360s；空输出使每个裁判失败 |
| 编辑留下的重复 YAML 键 | 它按字段覆盖下一个刺激物字段 — 删除多余的块 |
| 重复的刺激物名称 | Vally 使用名称作为比较身份 — 给每个刺激物一个稳定、唯一的名称 |
| `disable-model-invocation: true` 技能的直接评估 | 删除它并通过消费者结果覆盖引用 |
| 低于刺激物底线的代理评估 | 原生代理适配器使用相同的符号检验门；添加独立的偏好合格的刺激物 |
| 使用 `./eng/run-skill-evals.sh` 运行代理评估 | 该辅助工具仍然是技能专用的；使用 `skill-validator evaluate` |
| 代理评估缺少 `environment.skills` | 声明代理路由到的技能，否则它无法调用它们 |
| 在 **技能** 评估中设置 `environment.skills` | 实验变化该键，并在每条臂中替换它；声明无意义 |
