# 技能编写器

将此用作技能创建和改进的单一规范工作流。
主要成功条件：在编写前最大化高价值输入覆盖范围，同时最小化浪费的运行时令牌。

按顺序遵循工作流步骤。仅加载您当前所在步骤所需的参考文件。
`SKILL.md` 是主要路由器：每个捆绑的参考文件应在 `references/` 下扁平化，并在此处列出直接 "何时打开..." 的原因。

## 核心工作流参考

| 需要时打开... | 阅读 |
|--------------------------|------|
| 选择创建、更新、迭代或先研究的工作的最小工作流路径 | `references/mode-selection.md` |
| 在决定文件之前选择最简单的适当执行形状 | `references/execution-shapes.md` |
| 应用关于深度、简洁性和可移植性的写作约束 | `references/design-principles.md` |
| 决定哪些内容属于 `SKILL.md`、`references/`、`SPEC.md` 或支持文件 | `references/reference-architecture.md` |
| 创建或更新技能的维护合同 | `references/spec-template.md` |
| 查找缺失的高信号源，包括历史记录和回归 | `references/source-discovery.md` |
| 将上游提示、工作流、评分标准、基准或文档适配为技能 | `references/source-adaptation.md` |
| 运行完整的合成过程，包括覆盖检查和源捕获 | `references/synthesis-path.md` |
| 编写或更新 `SKILL.md`、`SPEC.md` 和支持文件 | `references/authoring-path.md` |
| 改进触发语言和误报/误报行为 | `references/description-optimization.md` |
| 从正面、负面或修复示例进行迭代 | `references/iteration-path.md` |
| 存储用于未来修订的持久工作示例和保留示例 | `references/iteration-evidence.md` |
| 选择响应模板、模式或输出合同 | `references/output-contracts.md` |
| 为技能的生成输出或运行时行为添加或更新评估 | `references/skill-evals.md` |
| 排查过载布局、隐藏引用或其他结构故障 | `references/structure-troubleshooting.md` |
| 注册技能并运行最终验证检查 | `references/registration-validation.md` |

## 文件布局参考

| 需要时打开... | 阅读 |
|--------------------------|------|
| 在一个连贯的 `SKILL.md` 中保持整个技能 | `references/layout-inline-skill.md` |
| 将可选的深度知识拆分为聚焦的路由参考 | `references/layout-reference-backed-skill.md` |
| 添加用于确定性自动化或验证的脚本 | `references/layout-script-backed-workflow.md` |
| 定义通常使用显式参数调用的技能 | `references/layout-argument-driven-skill.md` |
| 发布可重用的模板、模式或其他静态资源 | `references/layout-asset-template-skill.md` |

## 工作流机制参考

| 需要时打开... | 阅读 |
|--------------------------|------|
| 将任务拆分为固定的顺序步骤 | `references/workflow-prompt-chaining.md` |
| 对请求进行分类并将它们路由到不同的下游路径 | `references/workflow-routing.md` |
| 将独立工作拆分为并行单元或投票 | `references/workflow-parallel.md` |
| 动态发现工作单元并协调工作输出 | `references/workflow-orchestrator-workers.md` |
| 在编写或执行期间运行验证-修复-重复检查 | `references/workflow-validation-loops.md` |
| 在执行风险操作之前验证计划 | `references/workflow-plan-validate-execute.md` |

## Claude 代码参考

| 需要时打开... | 阅读 |
|--------------------------|------|
| 使用 Claude 特定的 frontmatter 或调用控制 | `references/claude-frontmatter-invocation.md` |
| 使用 Claude 参数字段或替换变量 | `references/claude-argument-substitutions.md` |
| 构建在隔离的 `context: fork` 中运行的技能 | `references/claude-subagent-fork.md` |
| 构建使用 Claude 钩子进行确定性执行的技能 | `references/claude-hook-backed.md` |
| 使用 Claude shell 预处理进行动态上下文注入 | `references/claude-dynamic-context.md` |

## 示例配置文件

| 需要时打开... | 阅读 |
|--------------------------|------|
| 查看文档化技能的预期深度 | `references/example-documentation-skill.md` |
| 查看工作流处理技能的预期深度 | `references/example-workflow-process-skill.md` |
| 查看良好的路由技能的样子 | `references/example-router-skill.md` |
| 查看良好的子代理-分支技能的样子 | `references/example-subagent-fork-skill.md` |
| 查看良好的钩子支持技能的样子 | `references/example-hook-backed-skill.md` |

## 第 1 步：确定目标、路径和形状

1. 确定预期操作（`create`、`update`、`synthesize`、`iterate`）并在选择文件所属位置之前检查工作区先例。
2. 从观察到的约定中选择目标技能根。如果在检查后规范位置仍然不清楚，则在编辑文件之前问一个直接问题。
3. 阅读 `references/mode-selection.md` 以选择最少的必需工作流路径。
4. 阅读 `references/execution-shapes.md` 以选择主要执行形状。
5. 默认为最简单的适当形状。如果选择更复杂的形状，请记录为什么拒绝了更简单的形状。
6. 仅加载该形状所需的精确文件布局、工作流机制和提供程序特定叶文件。
7. 在添加指导之前，确定应缩小、替换或删除的现有规则、部分或文件。
8. 在使用提供程序特定机制之前，记录可移植性影响。

## 第 2 步：按需运行合成

阅读 `references/synthesis-path.md`。

1. 使用此路径用于新技能、材料更改和研究优先规划。
2. 收集和评分相关的源，并记录其来源。
3. 当源材料稀疏、陈旧或不明确时，阅读 `references/source-discovery.md`。
4. 当适配上游提示、工作流、评分标准、基准或文档时，阅读 `references/source-adaptation.md`。
5. 生成基于源的决策和覆盖/差距状态，包括类别和执行形状选择。
6. 仅在它们为所选类别或形状添加具体深度时才加载示例配置文件。
7. 如果技能使用提供程序特定机制，请包含当前官方提供程序文档并捕获使用约束。
8. 在理解所需覆盖范围或明确差距之前，不要移动到编写。

## 第 3 步：在从结果/示例改进时首先运行迭代

当所选路径包括 `iteration`（例如操作 `iterate`）时，首先阅读 `references/iteration-path.md`。

1. 捕获和匿名化具有来源的示例。
2. 当示例应在当前回合之后持续存在时，阅读 `references/iteration-evidence.md`。
3. 审查技能行为相对于工作切片和保留切片。
4. 从正面/负面/修复证据提出改进建议。
5. 将具体行为差异带入编写。

当所选路径不包括 `iteration` 时，跳过此步骤。

## 第 4 步：编写或更新技能工件

阅读 `references/authoring-path.md`。

1. 使用命令式语气编写或更新 `SKILL.md`，并包含丰富的触发描述。
2. 将 `SKILL.md` 作为运行时路由器，而不是百科全书。
3. 在创建新部分或文件之前，在 `references/authoring-path.md` 中运行预编辑精确检查。
4. 在添加大量指令或新参考文件之前，阅读 `references/reference-architecture.md`。
5. 使用 `references/spec-template.md` 创建新技能或实质性更改其合同时，创建或更新 `SPEC.md`。
6. 仅在每份文件都有一个明确的 "何时打开..." 原因且无法通过收紧现有文件来处理时，创建专注的参考文件、脚本和资产。
7. 如果您添加了捆绑的参考文件，请在 `SKILL.md` 中为它添加直接的路线条目。
8. 优先考虑清单、表格、模板和输入/输出示例，而不是解释性文字。
9. 仅遵循为该技能选择的特定文件布局、工作流机制、Claude 特定和输出合同参考。
10. 对于高级执行形状，在考虑技能完成之前，添加所需的路由、委托或安全合同。
11. 对于编写/生成技能，在参考中包含转换示例：
    - 快乐路径
    - 安全/健壮变体
    - 反模式 + 修复版本
12. 当请求要求评估、回归案例、基准案例或模型评分质量检查时，阅读 `references/skill-evals.md`。
13. 在任何技能工件更改后，在描述优化或验证之前，在 `references/authoring-path.md` 中运行更改后的后精确检查。

## 第 5 步：优化描述质量

阅读 `references/description-optimization.md`。

1. 验证应触发和不应触发的查询集。
2. 通过有针对性的描述编辑减少误报和误报。
3. 除非技能有意特定于提供程序，否则保持触发语言跨提供程序通用。

## 第 6 步：注册和验证

阅读 `references/registration-validation.md`。

1. 对您在工作区验证的活跃布局应用存储库注册步骤。
2. 运行快速验证以进行结构检查。
3. 在完成前，带判断审查验证器警告、精确检查结果和覆盖差距。

## 输出格式

返回：

1. `摘要`
2. `所做的更改`
3. `验证结果`
4. `未关闭的差距`
