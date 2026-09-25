# Agent Script 技能

## 此技能的用途

此技能用于开发 Agentforce 代理，主要使用 Salesforce 的 AI 代理脚本语言 Agent Script。

基于组织的流程需要 Agentforce 许可证、API v66.0 或更高版本，以及 Einstein Agent 用户。静态编写和审查可以在不访问组织的情况下进行。

**关键：** Agent Script 不是 AppleScript、JavaScript、Python 或任何其他语言。请勿将 Agent Script 语法或语义与其他您所受训练的语言混淆。

Agent Script 代理由 `AiAuthoringBundle` 元数据定义：一个 `<ApiName>.agent` 文件（代理行为）以及一个同名的 `<ApiName>.bundle-meta.xml` 文件（包元数据）。目录和两个文件名必须使用相同的区分大小写的 API 名称；一个字面值 `bundle-meta.xml` 文件不可部署。可以使用可调用的 Apex、自动启动的流程、Prompt Templates 和其他支持类型来实现操作。

此技能涵盖了 Agent Script 的完整生命周期：设计代理、编写 Agent Script 代码、验证和调试、部署和发布，以及测试。

## 如何使用此技能

此文件将用户意图映射到 `references/` 中的任务域和相关参考文件。将此文件视为端到端代理开发的执行路由器，并使用参考文件以获取详细信息。

从任务描述中识别用户意图。仅阅读活动步骤明确要求的或当前决策所需的参考文件。每个 **参考文件** 部分是一个查找索引，而不是预加载列表；不要加载用于后续步骤或不相关的步骤的文件。

对于全面的健康检查、常见错误审查或审计-修复-评估循环，请使用下方的 **审计和修复现有代理** 任务域作为相同编写生命周期的一部分。

## 始终适用的规则

1. **始终 `--json`。** 在每个 `sf` CLI 命令中始终包含 `--json`。不要将 CLI 输出通过 `jq` 或 `2>/dev/null`。直接读取完整的 JSON 响应——LLMs 原生解析 JSON。

2. **验证目标组织。** 在任何组织交互之前，运行 `sf config get target-org --json` 以确认已设置目标组织。如果没有配置，请让用户使用 `sf config set target-org <alias>` 设置一个。

3. **按比例诊断更改。** 对于语法或本地静态缺陷，首先运行支持本地解析器/编译器，然后在可用时添加目标组织验证。
   对于行为缺陷，保留基线并使用预览和跟踪。
   对于表面修复，冻结确切的接受编辑列表，然后检查最终差异并撤销其他每个 hunk，包括块标量或元数据规范化。在最小更改修复中，除非用户明确将清理包括在范围内，否则保留可选的装饰性发现建议；没有诊断或使用案例后果的有效语法不是额外的修复。
   模拟可以建立路由和操作选择；仅在明确批准、已验证的非生产环境和安全测试数据的情况下使用 `--use-live-actions`。不要声称来自模拟或响应文本的外部效果。参见
   [验证和调试](references/agent-validation-and-debugging.md)。

4. **使用按比例的规范门。** 获取明确的 Agent Spec 批准用于绿色字段代理和结构或重写更改。用户授权的、良好规范的本地修复不需要重新创建或重新批准整个规范；记录受影响的用例并保留现有设计。
   当用户提供足够详细的设计并明确说明它已经批准时，将其视为已批准的规范：不要重新创建它或停止以获取另一个批准，除非要求缺失或实质性更改。

5. **不要停滞。** 在步骤成功完成后，宣布下一步并开始它。不要等待用户说“下一步是什么”或“好的，继续”。需要明确用户批准的检查点包括：
   (a) 当规则 4 要求时，Agent Spec 批准，
   (b) 发布前的检查点，
   (c) 具有破坏性或后果性的外部操作，以及
   (d) 技能明确显示的任何 A/B 分支（例如，ADL 设置期间未配置数据云）。像 ADL 索引这样的长时间运行的非阻塞工作应在技能继续进行不依赖于结果的工作时在后台运行。

6. **草稿优先生命周期。** 在正常编写期间，保持在草稿迭代：
   编辑 `.agent` + 操作实现，验证、部署和预览，直到需要为止。默认情况下不要发布/激活。发布 + 激活是要求用户确认他们准备好将当前草稿提交到元数据并暴露给最终用户的具体发布操作。

7. **从一个执行块和无可变状态开始。** 一个专注的代理将推理和操作直接放在 `start_agent` 中。仅当存在真实的客观目标、指令、操作、权限或升级边界时才添加子代理。仅当存在命名的确定性消费者时才添加持久状态，并为其提供完整的生命周期。普通连续性保留在生存历史中。应用
   [AgentScript 的禅意](references/zen-of-agentscript.md) 和
   [姿态和确定性](references/posture-and-determinism.md)
   中的具体检查。

8. **使用支持的控制流。** 使用规范的条件形式，并永远不要生成嵌套的 `if`，Agentforce linter 会拒绝它。参见
   [条件控制流语法](references/agent-script-core-language.md#conditional-control-flow-syntax)，
   然后运行完整的包验证。

9. **操作实现是用户决策。** 在规划和规范工作中，将新操作默认设置为 `NEEDS STUB` 占位符。始终询问用户他们是否想要扫描组织/项目以查找现有实现和/或生成新的 Apex/Flow/Prompt 实现，然后再采取任何路径。

10. **给每个可到达的分支一个下一个结果。** 选择一个主要结果：回答、询问、调用操作、转换、拒绝或升级。
    编译器选择子代理 `system.instructions` 覆盖而不是全局值，并且当前运行时为模型组装有效系统和解析的推理文本。将编写构造符从面向模型的文本中排除。参见
    [指令解析](references/instruction-resolution.md)。

11. **使用可移植的结构化缩进。** 使用 4 个空格生成新的 `.agent` 文件每个级别。在手术编辑期间保留一致缩进的遗留文件，或作为单独的验证更改规范化整个文件。

12. **不要让提示格式模仿控制流。** `|` 文本内的缩进、编号步骤以及 `Show`、`Ask`、`Call`、`Set` 或 `STOP` 等单词是模型指令，不是可执行范围。独立地控制操作。每个连续的提示块使用一个 `|`；重复的相邻标记不会创建阶段或优先级。不要使用
    `@utils.setVariables` 来强制回合边界或另一个推理迭代。应用
    [常见控制流陷阱](references/common-control-flow-pitfalls.md)
    中的检查表。

13. **选择谁拥有每个决策。** 当一个精确的机器已知事实必须保持稳定时使用运行时谓词。当语义意图、歧义、恢复或情境感知判断使灵活性更有价值时使用模型指令。模型无法读取存储的变量值，除非提示文本使用 `{!@variables.X}` 将它们注入；插值会显示值，但不会使模型的比较确定性。应用
    [姿态和确定性](references/posture-and-determinism.md)
    中的权衡测试。

14. **首先在本地编译 AgentScript，快速且可见。** 对于每个具有现有 `.agent` 文件的编写、修复或审计任务，首先尝试捆绑本地索引/编译器，然后再进行组织侧验证或完成报告。运行
    `node <skill-directory>/scripts/index-agent.mjs <agent-file>`。如果 SDK 无法加载，请遵循
    [AgentScript 编译器设置](references/agentscript-toolchain.md)，重试，并使用其有界的 npm/源回退。修复每个严重性-1 诊断并重新运行，直到干净。报告提供者和确切版本或提交。组织访问不会取代此廉价的本地传递。如果两个本地设置路径都失败，请继续进行目标组织验证或有界静态审查，并声明 **未使用编译器** 以及原因；不要停滞任务或暗示建议的未来命令是验证。**离线** 或
    **非交互** 模式不会豁免此步骤：它禁止网络和组织操作，而不是捆绑的本地编译器。

15. **保持编写包的形状可部署。** 在
    `aiAuthoringBundles/<ApiName>/` 下，要求完全匹配的 `<ApiName>.agent` 和
    `<ApiName>.bundle-meta.xml`。不要将元数据文件名缩短为 `bundle-meta.xml`。保留构建的或检索到的元数据，而不是重写其架构。一个新的 CLI-构建的包通常使用 `<bundleType>AGENT</bundleType>`；现有的描述符可以改用已建立的 `fullName`/`type`/`status` 形状，带有可选的 `label` 和 `description`。不要创建部分混合或发明字段。本地编译 `.agent` 文件不会验证元数据文件名或 XML，因此在报告验证成功之前检查两者。

## 任务域

选择与用户当前目标匹配的域。在采取行动之前阅读其命名的参考；链接是加载指令，而不是可选的参考书目。仅遵循适用的工作流并保留任何满足的先决条件。正常生命周期是设计 -> 草稿 -> 验证/预览 -> 明确批准的发布。

### 创建代理

用于新代理或编写包。

1. 阅读 [设计与代理规范](references/agent-design-and-spec-creation.md)，
   然后使用已批准的、足够详细提供的作为构建合同的设计，而无需重新生成或重新批准它。否则，捕获要求在保存的 Agent Spec 中，并获取明确的批准。将新的操作实现保留为 `NEEDS STUB`，直到用户选择是否要重用实现、生成它们或保留占位符。

2. 阅读 [CLI for Agents](references/salesforce-cli-for-agents.md)
   和 [部署](references/deploy-reference.md) 的适用部分，并在进行组织工作之前验证目标组织先决条件。对于文档接地，阅读 [数据库](references/data-library-reference.md)。对于语音代理，阅读 [语音模态](references/voice-modality-reference.md)
   和 [语音延迟](references/voice-latency-heuristics.md)。

3. 使用 Salesforce CLI 生成编写包。编辑构建的 `<ApiName>.agent` 并保留匹配的 `<ApiName>.bundle-meta.xml`。
   阅读 [核心语言](references/agent-script-core-language.md)，
   [指令解析](references/instruction-resolution.md)，以及适用的模板，然后再编写。

4. 运行规则 14 要求的本地编译器。当有认证的目标组织可用时，也在组织中验证编写包。在实现或部署操作依赖项之前修复阻止诊断。

5. 仅在用户选择该路径时才生成操作实现。一次验证和部署一个依赖项。

6. 使用
   [验证和调试](references/agent-validation-and-debugging.md)
   预览草稿并检查跟踪。覆盖现实的快乐、相邻、恢复和取消路径。

7. 停留在草稿循环中。只有在 **部署、发布和激活** 中的发布门通过并且用户明确批准后，才发布和激活。

### 理解现有代理

当用户想要理解现有包时使用。

1. 定位包和匹配的编写包文件。

2. 阅读 [核心语言](references/agent-script-core-language.md)，然后映射子代理图、确定性块、模型指令、操作、变量和操作实现。

3. 阅读 [设计与代理规范](references/agent-design-and-spec-creation.md) 并逆向工程保存的 Agent Spec。使用
   [子代理映射图](references/agent-subagent-map-diagrams.md) 用于图。仅在用户请求时才注释源。

4. 标记支持的反模式，区分观察到的行为与静态推断。仅在否则无法解释的解决方案的情况下加载 [已知问题](references/known-issues.md)。

### 审计和修复现有代理

用于“修复我的 AgentScript”、健康检查、常见错误审查和基线与候选修复循环。

1. 阅读 [审计和修复](references/agent-audit-and-repair.md)，然后按顺序遵循其链接的范围/路径审查和修复/报告工作流。

2. 仅使用 [诊断目录](references/agent-audit-diagnostic-catalog.md)
   及其聚焦诊断参考，仅用于包中存在的类别。使用 [常见控制流陷阱](references/common-control-flow-pitfalls.md)
   及其聚焦参考，用于怀疑提示/控制流缺陷。

3. 在更改包之前冻结接受的表面编辑。对于结构或重写工作，获取规则 4 要求的批准。

4. 本地编译，比较未更改的基线和候选与相同的用例，并遵循
   [审计评估循环](references/agent-audit-evaluation-loop.md)。

5. 分别报告表面、结构和重写评估。除非用户单独请求发布操作，否则保持草稿状态。

#### 审计参考文件

- [审计范围和路径审查](references/agent-audit-scope-path-review.md)
- [审计修复和报告](references/agent-audit-repair-report.md)
- [审计候选验证](references/agent-audit-candidate-verification.md)
- [指令和路由诊断](references/agent-audit-diagnostics-instructions-routing.md)
- [操作和状态诊断](references/agent-audit-diagnostics-actions-state.md)
- [架构和评估诊断](references/agent-audit-diagnostics-architecture-evaluation.md)
- [操作和序列陷阱](references/control-flow-actions-sequencing.md)
- [生命周期和副作用陷阱](references/control-flow-lifecycle-side-effects.md)
- [AgentScript 编译器设置](references/agentscript-toolchain.md)

### 修改现有代理

用于对现有响应、路由、操作、子代理、状态流、接地源或模态进行批准更改。

1. 首先理解受影响的路径。对于重大的设计更改，更新 Agent Spec 并获取批准；对于狭窄的指定修复，记录受影响的用例，而无需强制重写整个规范。

2. 阅读 [核心语言](references/agent-script-core-language.md) 以及仅用于更改所需的特征参考。保留无关的元数据、合同、格式和行为。

3. 原地编辑现有包。仅在明确请求时才生成操作实现。

4. 本地编译，当可用时，在目标组织中验证。预览每个更改和相邻路径并检查跟踪。在草稿中迭代。

5. 仅当用户单独请求发布时才使用发布工作流。

### 诊断编译错误

1. 捕获报告的确切错误，并运行规则 14 本地编译器。

2. 当有认证的目标组织可用时，运行组织验证；仅在编译成功但运行时准备仍然失败时才使用实时预览。

3. 使用
   [验证和调试](references/agent-validation-and-debugging.md) 和
   [核心语言](references/agent-script-core-language.md)
   对每个具体错误进行分类和修复。

4. 重新运行暴露错误的表面。报告确切执行的检查、剩余限制，以及未执行的命令作为验证证据。

### 诊断行为或生产问题

对于本地行为问题，保留基线，使用现实的用例预览，并使用
[验证和调试](references/agent-validation-and-debugging.md)
检查跟踪。在编辑之前，确认实际发生了哪些子代理、操作调用、操作结果、状态更改和最终响应。

对于生产会话或跟踪 ID，使用 **agentforce-observe** 进行检索和重建。仅在证据识别出 AgentScript 更改时才返回这里。永远不要编造不可用的操作输入、输出或模型推理。

### 部署、发布和激活

1. 阅读 [CLI for Agents](references/salesforce-cli-for-agents.md)，
   [元数据和生命周期](references/agent-metadata-and-lifecycle.md)，以及
   [部署](references/deploy-reference.md)。

2. 本地编译并在目标组织中验证。部署包和依赖项，然后使用现实的覆盖运行实时预览并检查跟踪。不要通过阻止结果继续进行。

3. 展示确切的目标组织和版本状态。在发布或激活之前，获取明确的用户批准。

4. 在批准后，才发布、激活并验证面向用户的代理。

5. **语音代理——连接电话通道是单独的、可选步骤；永远不要自动连接。** 连接电话号码会创建实际的路由基础设施（流程、队列、活动的 `MessagingChannel`），并消耗一个配置的号码，因此仅在用户 **明确要求** 并提供了 **配置的电话号码**（确认它存在——不要假设或编造一个）。如果缺少任何一个，请停止并说明需要什么。当两者都存在时，通过 CLI 头部方式连接它——不要将用户发送到 Agent Builder。遵循
   [头部电话 CLI](references/voice-telephony-cli.md)。

### 删除或重命名代理

阅读 [CLI for Agents](references/salesforce-cli-for-agents.md)
和 [元数据和生命周期](references/agent-metadata-and-lifecycle.md)
的删除/重命名部分。枚举参考和依赖项，显示受影响的包的确切内容，并在删除之前获取明确的确认。对于重命名，在删除原始文件之前创建并验证替换文件；之后验证遗弃的元数据。

### 测试代理

使用 **agentforce-test** 进行测试规范设计、安全覆盖、元数据创建、执行和结果分析。首先将 Agent Spec 和所有可到达的路由/操作映射到覆盖目标。在添加安全测试或运行可能调用实时操作的测试之前，确认。

### 优化代理

1. 阅读 [核心语言](references/agent-script-core-language.md) 并使用
   [常见控制流陷阱](references/common-control-flow-pitfalls.md)
   扫描每个可到达路径。

2. 仅加载适用的优化参考：数据流、确定性逻辑、引用语法、人工手交和语音准备。

3. 在编辑之前，获取批准的证据支持改进。

4. 仅应用已批准的更改，本地编译，当可用时在组织中验证，并报告结果证据。

### 管理 MCP 服务器

在进行任何 MCP 操作之前，请阅读 [MCP 服务器管理](references/mcp-management-reference.md)。验证目标组织，使用 `--json`，将秘密从命令行中移除，在允许列表之前审查工具，并对破坏性或后果性的更改要求确认。

## 代理规范

**代理规范** 是此技能生成和消费的中心工件。一个结构化设计文档，代表代理目的、用户结果、子代理图、操作和实现、变量、子代理姿态、确定性控制（当需要时）和行为意图。

代理规范随着代理的演变而演变。在代理创建期间稀疏（目的、用例、计划占位符）。在构建期间充实（流程图、操作实现映射、姿态选择记录、仅在证明合理时添加确定性控制）。在理解现有代理时逆向工程。对于高级故障排除至关重要，提供参考以比较预期行为与实际行为。在测试期间，测试覆盖映射到它。

对于绿色字段工作、重大设计更改或分析，其结果更改了记录的合同，请生成或更新代理规范。对于狭窄的、已指定的修复，记录受影响的用例和证据，而无需强制重写整个规范。

阅读 [设计与代理规范](references/agent-design-and-spec-creation.md) 以获取代理规范结构和生产方法。

## 资产

`assets/` 目录包含模板和示例。当您需要一个起点或有关工件和源文件的具体系列参考时，请阅读。

- **`assets/agent-spec-template.md`** — 包含所有部分和占位符内容的代理规范模板。将它们复制到项目目录中的 `<AgentName>-AgentSpec.md`，然后在设计期间填写。将代理规范作为文件保存——重要的设计工件，从适当的渲染中受益，特别是 Mermaid Subagent Map 图。

- **`assets/agents/local-info-agent-annotated.agent`** — 基于 Local Info Agent 的完整注释示例，在上下文中显示所有主要的 Agent Script 构造，并使用内联注释解释每个构造的用途。当您需要一个具体的参考，了解概念如何组合成工作代理，或者当参考文件中的专注示例不足以满足需求时，用作后备。

- **`assets/agents/template-single-subagent.agent`** — 兼容命名的专注启动器，具有一个 `start_agent` 执行块，没有路由器或子代理块。

- **`assets/agents/template-multi-subagent.agent`** — 具有多个子代理和转换的最小代理。复制并修改以用于复杂代理。

- **`assets/agents/router-first.agent`** — 仅转换路由示例，具有 HyperClassifier 和简洁的路由指令。

- **`assets/agents/verification-gate.agent`** — 具有受保护操作可用的身份/授权网关。

- **`assets/agents/simple-qa.agent`**, **`production-faq.agent`**, 和
  **`order-service.agent`** — 行为和操作复杂性不断增加的完整示例。

- **`assets/patterns/README.md`** — 路径到回调、输入绑定、生命周期、委托和多步骤工作流的完整模式。仅在它的声明用例先决条件适用时才使用模式。

- **`assets/invocable-apex-template.cls`** — 可调用 Apex 类的参考。当需要复杂的 Apex 操作实现时，复制并修改。

## 重要约束

- **使用支持所需证据的工具。** 使用 Salesforce CLI 和目标组织进行组织支持的验证和发布操作。使用发布的 AgentScript SDK 进行本地解析/编译检查，并仅在文档化边界内调用相关技能。

- **只有某些实现类型对操作有效。** 例如，只有可调用的 Apex（而不是任意的 Apex 类）可以支持操作。类似约束可能适用于流程和 Prompt Templates。在将操作连接到实现时，请参考设计与代理规范参考文件以获取有效的类型和占位符方法。

- **`sf agent generate test-spec` 不是用于代理的。** 它是一个交互式、REPL 风格的命令，专为人类设计。在创建测试规范时，从资产中的样板模板开始。

## 快速参考常见问题

**在发布期间 `Internal Error, try again later`：**
服务器端编译失败。500 不会告诉你哪个检查失败——按顺序走完四个原因，然后再询问用户出了什么问题。不要在第 1 步停止。

1. **`access.default_agent_user` 上的代理类型不匹配。** 员工代理通常省略 `access.default_agent_user`；服务代理必须具有它（并且用户必须持有 Einstein Agent 许可证）。参见
   [设计与代理规范](references/agent-design-and-spec-creation.md)，第 3 节。重新运行查询——不要编造用户名。

2. **操作定义缺少 `outputs:` 块。** 如果任何操作具有 `target:` 和 `inputs:` 但没有 `outputs:`, 服务器端编译器无法生成返回绑定。CLI `validate` 和 LSP 都通过——只有发布失败。参见
   [已知问题](references/known-issues.md)，问题 15。

3. **`.agent` 文件中的其他结构漂移。** 与同一组织中的已知良好包进行比较：
   `sf project retrieve start --metadata "AiAuthoringBundle:<known-working-agent>" --output-dir /tmp/diff-bundle --json`
   关键字按关键字比较。查找缺少必需但未记录的字段、块顺序漂移，或您捆绑使用的 DSL 关键字与工作捆绑不匹配。

4. **真正的瞬态后端错误。** 如果 1–3 干净，并且响应 `requestId` 在重试时不同，请等待 60 秒后重试一次。

**在预览期间 `Unable to access Salesforce Agent APIs...`：**
`default_agent_user` 缺乏权限。参见 [代理用户设置和权限](references/agent-user-setup.md)。不要发布作为修复——`--use-live-actions` 不需要已发布的代理。

**权限错误引用的用户名与配置的不同：**
与上述修复相同——错误引用组织的默认运行用户，但根本原因是 Einstein Agent 用户权限。

**代理即使当前子代理的操作正常工作也会出现权限错误：**
规划器在启动时验证所有子代理中的所有操作。一个缺失的权限会失败整个代理。

**Apex 操作在实时预览中返回空结果但在模拟中工作：**
`WITH USER_MODE` + 缺少对象权限 = 沉默失败（0 行，无错误）。参见
   [代理用户设置和权限](references/agent-user-setup.md)，第 6.2 节。

**代理已发布，ADL 索引（`retrieverId` 已填充），但每个接地问题都返回空的 `knowledgeSummary` / “我没有那个信息”：**
Einstein Agent 用户缺乏数据云访问。有两个需要检查的步骤，按顺序：
1. **Permset/PSL 未分配。** 运行来自 [代理用户设置，步骤 3b.3](references/agent-user-setup.md) 的验证查询。如果没有数据云 permset/PSL 出现，请运行发现然后分配程序（优先级：`GenieDataPlatformStarterPsl` PSL → `GenieUserEnhancedSecurity` PS → `DataCloudUser` PS → `DataCloudArchitect` PS）。
2. **Permset 上的数据空间范围未授予。** 目前没有 API。设置 → 权限集 → 点击分配的 permset → “Data Cloud Data Space Management” 下 Apps → 编辑 → 添加 ADL 的数据空间（通常 `default`）→ 保存。参见
   [代理用户设置，步骤 3b.4](references/agent-user-setup.md)。

## 快速链接（详细内容存在于参考中）

- 语法和执行模型：[核心语言](references/agent-script-core-language.md)
- 代理设计/规范过程：[设计与代理规范](references/agent-design-and-spec-creation.md)
- 姿态旋钮（代理 vs 确定性）：[姿态和确定性](references/posture-and-determinism.md)
- 具体编写不变量：[AgentScript 的禅意](references/zen-of-agentscript.md)
- 按场景选择模式：[按需求模式](references/patterns-by-requirement.md)
- 架构机制、HyperClassifier 路由和迁移：[架构模式](references/architecture-patterns.md)
- 验证、预览和跟踪：[验证和调试](references/agent-validation-and-debugging.md)
- 部署/发布/激活生命周期：[部署参考](references/deploy-reference.md)
- 元数据生命周期和发布故障排除：[元数据和生命周期](references/agent-metadata-and-lifecycle.md)
- ADL 配置和连接：[数据库参考](references/data-library-reference.md)
- 代理访问和权限：[代理访问指南](references/agent-access-guide.md), [代理用户设置](references/agent-user-setup.md)
- 语音模态和电话代理：[语音模态参考](references/voice-modality-reference.md)
- 安全审查框架：[安全审查](references/safety-review-reference.md)
- 评分标准：[评分标准](references/scoring-rubric.md)
- 优化模式：[模式 1 — 数据流](references/optimization-pattern-1-data-flow.md), [模式 2 — 确定性逻辑](references/optimization-pattern-2-deterministic-logic.md), [模式 3 — 引用语法](references/optimization-pattern-3-reference-syntax.md), [模式 4 — 升级](references/optimization-pattern-4-escalation.md)
- MCP 服务器注册和工具白名单：[MCP 服务器管理](references/mcp-management-reference.md)
