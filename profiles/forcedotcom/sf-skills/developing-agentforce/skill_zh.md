# 代理脚本技能

## 该技能的用途

Agent Script 是 Salesforce 的脚本语言，用于在 Atlas 推理引擎上编写下一代 AI 代理。该技能于 2025 年推出，无需任何 AI 模型的训练数据。编写、修改、诊断或部署 Agent Script 代理所需的一切内容都包含在此技能的参考文件中。

**⚠️关键警告：** Agent Script 不是 AppleScript、JavaScript、Python 或任何其他语言。请勿将 Agent Script 语法或语义与其他您已训练过的语言混淆。

Agent Script 代理由 `AiAuthoringBundle` 元数据定义——这是一个包含 `.agent` 文件的目录，该文件包含描述操作、指令、子代理、流程控制和配置的 Agent Script 源代码；以及包含捆绑包元数据的 `bundle-meta.xml` 文件。代理通过路由到子代理来处理语句，每个子代理都有由 Apex、流程、提示模板和其他类型的支持逻辑背书的指令和操作。

此技能涵盖了 Agent Script 的完整生命周期：设计代理、编写 Agent Script 代码、验证和调试、部署和发布，以及测试。

## 如何使用此技能

此文件将用户意图映射到 `references/` 中的任务域和相关参考文件。深入知识包括语法规则、设计模式、CLI 命令、调试工作流等。

从任务描述中识别用户意图。在开始工作之前，**始终**阅读指示的参考文件。

## 始终适用的规则

1. **始终 `--json`。** 在**每个** `sf` CLI 命令中都包含 `--json`。**不要**将 CLI 输出通过 `jq` 或 `2>/dev/null`。直接读取完整的 JSON 响应——LLM 原生解析 JSON。

2. **验证目标组织。** 在任何组织交互之前，运行 `sf config get target-org --json` 以确认已设置目标组织。如果未配置，请指导用户使用 `sf config set target-org <alias>` 设置一个。

3. **在修复之前进行诊断。** 在验证/调试代理行为时，**始终**使用 `--use-live-actions` 预览作者捆绑包。发送语句，然后读取结果会话跟踪以巩固您对代理行为的理解。跟踪文件显示子代理选择、操作 I/O 和 LLM 推理。**不要**在缺乏这种理解的情况下修改 `.agent` 文件或支持逻辑。有关跟踪文件位置和诊断模式的更多信息，请参阅 [验证和调试](references/agent-validation-and-debugging.md)。

4. **规范批准是一个硬性门槛。** 在没有明确用户批准的情况下，**不要**继续通过 Agent Spec 创建。

## 任务域

下面的每个任务域都有**必需步骤**。按顺序逐字遵循。**不要**用自己的计划替换或跳过步骤。

### 创建代理

用户希望从头开始构建新代理。**始终**使用 Agent Script。与用户合作，使用普通语言（而不是 Salesforce 特定术语）了解代理的目的、子代理和操作。

#### 必需步骤

阅读 [CLI for Agents](references/salesforce-cli-for-agents.md) 以获取确切的命令语法。

1. **设计** — 阅读 [Design & Agent Spec](references/agent-design-and-spec-creation.md) 以起草 Agent Spec。始终询问您是否应该扫描现有支持逻辑。除非另有指示，否则通过读取 `sfdx-project.json` 来扫描，以识别包目录，然后在每个目录中搜索 `@InvocableMethod`（在 `classes/` 中）、`AutoLaunchedFlow`（在 `flows/` 中）和 `promptTemplates/` 中的模板元数据。将匹配项标记为 `EXISTS`；未匹配的操作标记为 `NEEDS STUB`。还扫描 `objects/` 中的 `.object-meta.xml` 以发现自定义对象——相关对象通常包含代理应公开的数据，即使提示中未提及也是如此。**始终将 Agent Spec 保存为文件。**
2. **停用以供用户批准 Agent Spec。** 向用户展示。询问批准或反馈。**未经批准，不要**继续。一旦获得批准，除非步骤失败，否则无需停止即可继续。
3. **验证环境先决条件** — 阅读 [Design & Agent Spec](references/agent-design-and-spec-creation.md)，第 3 节（环境先决条件）。根据设计中的代理类型，验证组织环境：
   - **员工代理**：确认配置块**不**包含 `default_agent_user`、`connection messaging:` 或 MessagingSession 链接变量。如果存在，请将其删除。有关完整的员工代理示例，请参阅 [示例](references/examples.md)。
   - **服务代理**：查询组织以查找 Einstein Agent User。如果存在，请与用户确认用户名。如果不存在，请指导用户进行创建。有关创建步骤，请参阅 [CLI for Agents](references/salesforce-cli-for-agents.md)，第 12 节；有关 [Agent User Setup](references/agent-user-setup.md) 的必要权限，请参阅 [Agent User Setup](references/agent-user-setup.md)。
   **环境验证后，才可进行代码生成。**
4. **生成作者捆绑包** —
   `sf agent generate authoring-bundle --json --no-spec --name "<Label>" --api-name <Developer_Name>`
5. **编写代码** — 阅读 [Core Language](references/agent-script-core-language.md) 以获取语法、块结构和反模式。使用参考文件和模板编辑生成的 `.agent` 文件。**不要**手动创建 `.agent` 或 `bundle-meta.xml` 文件。
6. **验证编译** —
   `sf agent validate authoring-bundle --json --api-name <Developer_Name>`
   如果验证失败，请阅读 [Validation & Debugging](references/agent-validation-and-debugging.md) 以诊断和修复，然后重新验证。**始终**在生成支持逻辑之前修复语法和结构错误。
7. **生成支持逻辑** — 对于每个标记为 NEEDS STUB 的操作：
   `sf template generate apex class --name <ClassName> --output-dir <PACKAGE_DIR>/main/default/classes`
   将类体替换为 [Design & Agent Spec](references/agent-design-and-spec-creation.md) 中的可调用模式。**始终**部署：
   `sf project deploy start --json --metadata ApexClass:<ClassName>`
   **始终**在生成和部署下一个桩之前修复部署错误。如果没有添加新操作，请跳过。
8. **验证行为** — 阅读 [Validation & Debugging](references/agent-validation-and-debugging.md) 以获取预览工作流和会话跟踪分析。
   `sf agent preview start --json --use-live-actions --authoring-bundle <Developer_Name>`
   如果操作查询数据，请使用以下命令进行接地测试语句：
   `sf data query --json -q "SELECT <Relevant_Fields> FROM <SObject> LIMIT 100"`
   使用以下命令发送测试语句：
   `sf agent preview send --json --authoring-bundle <Developer_Name> --session-id <ID> -u "<message>"`
   确认子代理路由、门控和操作调用是否与 Agent Spec 匹配。如果行为出现偏差，请切换到 **诊断行为问题** 工作流。修复问题后返回。**检查点——除非所有以下内容都为真，否则不要继续发布：**
   - `validate authoring-bundle` 通过且错误为零
   - 使用代表每个子代理的典型语句进行实时预览 (`--use-live-actions`)
   - 跟踪确认正确的子代理路由和操作调用
   - 用户明确批准部署
9. **发布** — 发布验证元数据结构，而不是代理行为。每次发布都会创建永久版本号。
   `sf agent publish authoring-bundle --json --api-name <Developer_Name>`
   如果发布失败，请在重试之前遵循 [Metadata & Lifecycle](references/agent-metadata-and-lifecycle.md) 第 5 节中的故障排除清单。
10. **激活** — 使新版本可供用户使用。
    `sf agent activate --json --api-name <Developer_Name>`
11. **验证发布的代理** — 激活后，使用以下命令预览面向用户的行為：
     `sf agent preview start --json --api-name <Developer_Name>`
     使用 `--api-name`，而不是 `--authoring-bundle`。
12. **配置最终用户访问** — 仅适用于员工代理。阅读 [Agent Access Guide](references/agent-access-guide.md) 以配置权限并分配访问权限。

#### 参考文件

1. [CLI for Agents](references/salesforce-cli-for-agents.md) — 验证、部署、预览、发布、激活的确切命令语法
2. [Core Language](references/agent-script-core-language.md) — 语法、反模式
3. [Design & Agent Spec](references/agent-design-and-spec-creation.md) — Agent Spec 更新、支持逻辑分析
4. [Validation & Debugging](references/agent-validation-and-debugging.md) — 编译诊断、预览工作流、会话跟踪分析
5. [Known Issues](references/known-issues.md) — 仅在代码修复后错误仍然存在时加载

### 理解现有代理

用户希望理解他们没有编写或需要重新访问的 Agent Script 代理。可以指向 `AiAuthoringBundle` 目录，或询问“这个代理做什么？”或“我需要修复这个代理，但我不知道它如何工作。”。

#### 必需步骤

1. **定位代理** — 阅读 `sfdx-project.json` 以识别包目录。在它们之间找到 `AiAuthoringBundle` 目录。阅读 `.agent` 文件和 `bundle-meta.xml`。
2. **阅读代码** — 在解析 `.agent` 文件之前，请阅读 [Core Language](references/agent-script-core-language.md) 以获取语法和执行模型。
3. **映射支持逻辑** — 对于每个具有 `target` 的操作，在项目中定位支持实现（Apex 类、流程、提示模板）。注意输入/输出合同。
4. **逆向工程 Agent Spec** — 阅读 [Design & Agent Spec](references/agent-design-and-spec-creation.md) 以获取 Agent Spec 结构。从代码中生成 Agent Spec 并保存为文件。
5. **生成子代理映射图** — 阅读 [Subagent Map Diagrams](references/agent-subagent-map-diagrams.md) 以获取 Mermaid 图表约定。生成子代理图的流程图，显示转换、门控和操作关联。
6. **注释源代码** — 询问用户是否希望用说明注释 Agent Script 源代码。如果要求，请向 `.agent` 文件添加内联注释，解释流程控制决策、门控推理和子代理关系。
7. **向用户展示** — 分享 Agent Spec、Subagent Map 和注释的源代码（如果生成）。检查 [Core Language](references/agent-script-core-language.md) 中的反模式部分，并标记代码中发现的任何匹配项。

#### 参考文件

1. [Core Language](references/agent-script-core-language.md) — 语法、执行模型、反模式
2. [Design & Agent Spec](references/agent-design-and-spec-creation.md) — Agent Spec 结构、流程控制模式识别
3. [Subagent Map Diagrams](references/agent-subagent-map-diagrams.md) — 用于可视化代理子代理图的 Mermaid 图表约定
4. [Metadata & Lifecycle](references/agent-metadata-and-lifecycle.md) — 目录约定、捆绑包元数据
5. [Known Issues](references/known-issues.md) — 仅在代码包含未解释的解决方案模式时加载

### 修改现有代理

用户希望添加、删除或更改现有代理的子代理、操作、指令或流程控制。可以描述更改（例如，“添加一个计费子代理”）或引用特定的 Agent Script 结构。

#### 必需步骤

阅读 [CLI for Agents](references/salesforce-cli-for-agents.md) 以获取确切的命令语法。

1. **理解** — 如果不存在 Agent Spec，请按照上述“理解现有代理”工作流程进行逆向工程。
2. **更新 Agent Spec** — 阅读 [Design & Agent Spec](references/agent-design-and-spec-creation.md) 以获取流程控制模式和支持逻辑分析。修改 Agent Spec 以反映预期更改。对于新操作，始终询问您是否应该扫描现有支持逻辑。除非另有指示，否则通过读取 `sfdx-project.json` 来扫描，以识别包目录，然后在每个目录中搜索 `@InvocableMethod`（在 `classes/` 中）、`AutoLaunchedFlow`（在 `flows/` 中）和 `promptTemplates/` 中的模板元数据。将匹配项标记为 `EXISTS`；未匹配的操作标记为 `NEEDS STUB`。**始终将更新的 Agent Spec 保存为文件。**
3. **停用以供用户批准更新的 Agent Spec。** 向用户展示。询问批准或反馈。**未经批准，不要**继续。一旦获得批准，除非步骤失败，否则无需停止即可继续。
4. **编辑代码** — 阅读 [Core Language](references/agent-script-core-language.md) 以获取语法和反模式。编辑 `.agent` 文件以实施批准的更改。
5. **验证编译** —
   `sf agent validate authoring-bundle --json --api-name <Developer_Name>`
   如果验证失败，请阅读 [Validation & Debugging](references/agent-validation-and-debugging.md) 以诊断和修复，然后重新验证。
6. **生成新的支持逻辑** — 对于每个标记为 NEEDS STUB 的新操作：
   `sf template generate apex class --name <ClassName> --output-dir <PACKAGE_DIR>/main/default/classes`
   将类体替换为 [Design & Agent Spec](references/agent-design-and-spec-creation.md) 中的可调用模式。**始终**部署：
   `sf project deploy start --json --metadata ApexClass:<ClassName>`
   **始终**在生成和部署下一个桩之前修复部署错误。如果没有添加新操作，请跳过。
7. **验证行为** — 阅读 [Validation & Debugging](references/agent-validation-and-debugging.md) 以获取预览工作流和会话跟踪分析。
   `sf agent preview start --json --use-live-actions --authoring-bundle <Developer_Name>`
   如果操作查询数据，请使用以下命令进行接地测试语句：
   `sf data query --json -q "SELECT <Relevant_Fields> FROM <SObject> LIMIT 100"`
   使用以下命令发送测试语句：
   `sf agent preview send --json --authoring-bundle <Developer_Name> --session-id <ID> -u "<message>"`
   首先测试更改的路径，然后测试相邻路径以捕获现有行为中的回归。
   **检查点——除非所有以下内容都为真，否则不要继续发布：**
   - `validate authoring-bundle` 通过且错误为零
   - 使用代表每个子代理的典型语句进行实时预览 (`--use-live-actions`)
   - 跟踪确认正确的子代理路由和操作调用
   - 用户明确批准部署
8. **发布** — 发布验证元数据结构，而不是代理行为。**不要**在开发/测试内循环中发布。**仅在**激活代理并使其面向最终用户之前作为最终步骤发布。
   `sf agent publish authoring-bundle --json --api-name <Developer_Name>`
   如果发布失败，请在重试之前遵循 [Metadata & Lifecycle](references/agent-metadata-and-lifecycle.md) 中的“故障排除发布失败”部分。
9. **激活** — 使新版本可供用户使用。
   `sf agent activate --json --api-name <Developer_Name>`
10. **验证发布的代理** — 激活后，使用以下命令预览面向用户的行為：
     `sf agent preview start --json --api-name <Developer_Name>`
     使用 `--api-name`，而不是 `--authoring-bundle`。

#### 参考文件

1. [CLI for Agents](references/salesforce-cli-for-agents.md) — 验证、部署、预览、发布、激活的确切命令语法
2. [Core Language](references/agent-script-core-language.md) — 语法、反模式
3. [Design & Agent Spec](references/agent-design-and-spec-creation.md) — Agent Spec 更新、支持逻辑分析
4. [Validation & Debugging](references/agent-validation-and-debugging.md) — 编译诊断、预览工作流、会话跟踪分析
5. [Known Issues](references/known-issues.md) — 仅在代码修复后错误仍然存在时加载

### 部署、发布和激活

用户希望将本地开发中的工作代理部署到 Salesforce 组织中的运行状态。涉及部署 `AiAuthoringBundle` 及其依赖项，发布到提交版本，然后激活以使其生效。

#### 必需步骤

阅读 [CLI for Agents](references/salesforce-cli-for-agents.md) 以获取确切的命令语法。

1. **验证编译** —
   `sf agent validate authoring-bundle --json --api-name <Developer_Name>`
   如果验证失败，则无法继续。
2. **部署捆绑包和依赖项** — 阅读 [Metadata & Lifecycle](references/agent-metadata-and-lifecycle.md) 以获取依赖管理部署命令。将 `AiAuthoringBundle` 及其支持逻辑（Apex 类、流程、提示模板）和依赖项部署到组织。
3. **实时预览** — 阅读 [Validation & Debugging](references/agent-validation-and-debugging.md) 以获取预览工作流和会话跟踪分析。
   `sf agent preview start --json --use-live-actions --authoring-bundle <Developer_Name>`
   然后发送测试语句：
   `sf agent preview send --json --authoring-bundle <Developer_Name> --session-id <ID> -u "<message>"`
   测试关键对话路径以验证代理在由实时操作支持时的行为。
   **检查点——除非所有以下内容都为真，否则不要继续发布：**
   - `validate authoring-bundle` 通过且错误为零
   - 使用代表每个子代理的典型语句进行实时预览 (`--use-live-actions`)
   - 跟踪确认正确的子代理路由和操作调用
   - 用户明确批准部署
4. **发布** — 发布验证元数据结构，而不是代理行为。**不要**作为开发/测试内循环的一部分发布。**仅在**激活代理并使其面向最终用户之前作为最终步骤发布。
   `sf agent publish authoring-bundle --json --api-name <Developer_Name>`
   如果发布失败，请在重试之前遵循 [Metadata & Lifecycle](references/agent-metadata-and-lifecycle.md) 中的“故障排除发布失败”部分。
5. **激活** — 使新版本可供用户使用。
   `sf agent activate --json --api-name <Developer_Name>`
6. **验证发布的代理** — 激活后，使用以下命令预览面向用户的行為：
     `sf agent preview start --json --api-name <Developer_Name>`
     使用 `--api-name`，而不是 `--authoring-bundle`。
7. **配置最终用户访问** — 仅适用于员工代理。阅读 [Agent Access Guide](references/agent-access-guide.md) 以配置权限并分配访问权限。

#### 参考文件

1. [CLI for Agents](references/salesforce-cli-for-agents.md) — 部署、发布、激活、停用的确切命令语法
2. [Validation & Debugging](references/agent-validation-and-debugging.md) — 编译验证、预览工作流
3. [Metadata & Lifecycle](references/agent-metadata-and-lifecycle.md) — 依赖管理、部署命令；发布故障排除
4. [Agent Access Guide](references/agent-access-guide.md) — 最终用户访问权限、可见性故障排除
5. [Known Issues](references/known-issues.md) — 仅在部署挂起、发布失败或激活意外失败时加载

### 诊断生产问题

用户的代理已发布并激活，但遇到了预览期间未捕获到的问题。包括信用消耗过多、令牌或大小限制失败、循环门控中断、保留关键字运行时错误、VS Code 同步失败或预览和生产之间意外的行为差异。

#### 必需步骤

阅读 [CLI for Agents](references/salesforce-cli-for-agents.md) 以获取确切的命令语法。

1. **分类问题** — 确定这是计费/成本问题、运行时限制、命名冲突、工具问题，还是预览和生产之间行为差异。
2. **检查已知生产注意事项** — 阅读 [Production Gotchas](references/production-gotchas.md) 以获取信用消耗、令牌限制、循环门控、保留关键字、生命周期钩子和 VS Code 解决方案。
3. **比较预览与生产行为** — 如果问题是行为差异，请使用以下命令预览已发布的代理（不使用 `--authoring-bundle`）：
   `sf agent preview start --json --api-name <Developer_Name>`
   与使用 `--authoring-bundle <Developer_Name> --use-live-actions` 预览已发布的代理进行比较，以隔离预览和生产之间的差异。
4. **检查已知问题** — 阅读 [Known Issues](references/known-issues.md) 以获取可能解释生产仅失败的平台错误。
5. **修复并重新发布** — 应用修复，验证，重新预览，发布，激活，并验证。遵循部署、发布和激活步骤。
6. **解释诊断** — 告诉用户发生了什么，以及您做了哪些更改。用 *Core Language* 代理执行模型解释根本原因。

#### 参考文件

1. [Production Gotchas](references/production-gotchas.md) — 信用
   消耗、令牌限制、循环门控、保留关键字、生命周期钩子、VS Code 解决方案
2. [CLI for Agents](references/salesforce-cli-for-agents.md) — 预览、发布、激活的命令语法
3. [Validation & Debugging](references/agent-validation-and-debugging.md) — 预览工作流、会话跟踪分析
4. [Known Issues](references/known-issues.md) — 仅在问题可能是平台错误时加载

### 删除或重命名代理

用户希望删除代理或更改其名称。维护任务因 `AiAuthoringBundle` 版本控制和已发布版本依赖项而变得复杂。

#### 必需步骤

阅读 [CLI for Agents](references/salesforce-cli-for-agents.md) 以获取确切的命令语法。

1. **了解当前状态** — 阅读 [Metadata & Lifecycle](references/agent-metadata-and-lifecycle.md) 以获取版本控制、删除机制和重命名机制。确定代理是否已发布，有多少版本存在，以及它当前是否激活。
2. **如果已激活，则停用** —
   `sf agent deactivate --json --api-name <Developer_Name>`
   激活的代理无法删除或重命名。
3. **执行操作** — 对于删除：遵循 [Metadata & Lifecycle](references/agent-metadata-and-lifecycle.md) 中的删除机制。对于重命名：遵循同一参考文件中的重命名机制。
4. **清理或删除孤儿** — 检查并删除孤儿元数据：Bot、BotVersion、GenAiPlannerBundle、GenAiPlugin、GenAiFunction。参考文件详细说明了要查找的内容。
5. **验证** — 确认操作已干净完成。对于重命名，验证新捆绑包编译并通过预览以确认行为。

#### 参考文件

1. [CLI for Agents](references/salesforce-cli-for-agents.md) — 删除、停用、检索的确切命令语法
2. [Validation & Debugging](references/agent-validation-and-debugging.md) — 编译验证、预览工作流
3. [Metadata & Lifecycle](references/agent-metadata-and-lifecycle.md) — 删除机制、重命名机制、孤儿清理

### 测试代理

用户希望为 Agent Script 代理创建自动测试。涉及编写 `AiEvaluationDefinition` 测试规范，该规范以 YAML 格式定义测试场景、预期行为和质量指标。

#### 必需步骤

阅读 [CLI for Agents](references/salesforce-cli-for-agents.md) 以获取确切的命令语法。

1. **建立覆盖基线** — 阅读 Agent Spec。如果不存在 Agent Spec，请按照“理解现有代理”步骤进行逆向工程。将每个子代理、操作和流程控制路径映射到需要测试覆盖的内容。
2. **设计测试场景** — 对于测试设计方法、预期、指标、测试规范 YAML 格式和模板，请使用 **testing-agentforce** 技能。该技能拥有所有测试内容。对于每个覆盖目标，编写一个或多个测试场景：用户语句、预期的子代理路由、预期的操作调用和代理响应。包括快乐路径和边缘情况。
3. **编写测试规范 YAML** — 使用 **testing-agentforce** 技能的模板和参考文件。保存到 `specs/<Agent_API_Name>-testSpec.yaml` 在 SFDX 项目中。
4. **创建测试元数据** — 使用 CLI 从测试规范生成 `AiEvaluationDefinition`。
5. **部署测试** — 将 `AiEvaluationDefinition` 部署到组织。
6. **运行测试** — 使用 CLI 执行测试运行。捕获结果。
7. **分析结果** — 将实际结果与预期进行比较。对于失败，请确定问题是出在代理代码、支持逻辑还是测试规范本身。
8. **迭代** — 根据需要修复代理代码或测试规范，重新部署并重新运行，直到满足覆盖目标。

#### 参考文件

1. [CLI for Agents](references/salesforce-cli-for-agents.md) — 测试创建、测试运行、测试结果的确切命令语法
2. [Core Language](references/agent-script-core-language.md) — 代理结构以设计有意义的测试
3. [Design & Agent Spec](references/agent-design-and-spec-creation.md) — Agent Spec 作为测试覆盖基线
4. **testing-agentforce** 技能 — 测试规范 YAML 格式、预期、指标、测试设计方法，以及测试规范模板
