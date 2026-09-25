# Agentforce 流程管理配置

在 Salesforce 组织中端到端配置 Agentforce 流程管理。此技能处理全新组织（无需配置）和需要修复或完成的半配置组织。

## 范围

- **在范围内**：启用流程管理、配置销售管理代理、激活/自定义流程（更新字段建议、获取机会基础数据、从通话转录中获取 AI 推荐）、提示模板配置、权限集分配、数据源设置、机会阶段描述、自主字段更新配置和部分组织修复。
- **超出范围**：从头开始构建自定义代理（使用 `agentforce-generate`）、Einstein 对话洞察或 Einstein 活动捕获的初始配置（这些都是独立产品）、Slack 应用安装、机会团队成员上的自定义 Apex 触发器。

---

## 前置条件

### 您必须验证（脚本无法检查或更改这些）

1. **版本**：企业版、性能版、无限版或开发者版，并带有 Agentforce for Sales 附加组件（或 Agentforce 1 Sales 版本）。设置**探针**（步骤 0）——在无法运行流程管理的组织中快速失败，显示许可证/版本消息——但在询问任何内容之前，许可证/版本配置本身仍由管理员拥有。
2. **用户权限**：执行用户需要 `查看设置` AND (`修改所有数据` OR `自定义应用程序`)，`管理 AI 代理` AND (`管理 Agentforce 员工代理` OR `自定义应用程序`)，以及 `分配权限集`。

### `scripts/setup-all.sh` 自动启用

以下设置由设置自动切换——在运行脚本之前不要手动启用它们。

- **Einstein 生成式 AI** (`EinsteinGptSettings.enableEinsteinGptPlatform`) — **必需**；必须在 Agentforce 代理之前启用。
- **Agentforce 代理** (`EinsteinCopilotSettings.enableEinsteinGptCopilot`) — **必需**；依赖于 Einstein 生成式 AI。
- **Agentforce Studio / 代理平台** (`AgentPlatformSettings.enableAgentPlatform`) — **必需**；依赖于 Agentforce 代理，并控制交易代理。核心在关闭此功能时拒绝 `SalesDealAgentSettings.enableDealAgent`，显示为不透明的交易代理激活失败。
- **增强型笔记** (`EnhancedNotesSettings.enableEnhancedNotes`) — **必需**；流程管理使用 ContentNote 作为主要数据源。
- **机会团队** (`OpportunitySettings.enableOpportunityTeam`) — **必需**；建议流程使用 OpportunityTeamMember，没有它将失败部署。
- **流程检查** (`OpportunitySettings.enablePipelineInspection`) — **必需**；提供代表查看和接受/拒绝建议的 UI。没有它，建议仍然生成，但用户无处查看。
- **增强型电子邮件** (`EmailAdministrationSettings.enableEnhancedEmailEnabled`) — **可选但推荐**；仅在 Einstein 活动捕获使用时需要电子邮件正文索引。
- **流程管理** (`SalesDealAgentSettings.enableDealAgent`) — **必需**；功能本身。

---

## 澄清问题

> **首先运行许可证预检——在询问任何这些问题之前。** 作为你非常第一个动作（在解决组织别名之后），运行 `bash scripts/setup-all.sh <org-alias> --check-license`。它只运行身份验证 + 能力门，不询问任何内容，也不更改任何内容。**如果它退出非零**，将打印的许可证/版本阻止器传达给用户并**停止**——不要询问任何澄清问题，也不要进行任何更改。只有当它退出 0（组织有能力——全新或已配置）时，才继续下面的问题。

预检通过后，确定：

1. **全新还是修复？** 这是一个从未有过流程管理的全新组织，还是一个部分配置的组织？
2. **数据源**：哪些数据源应通知代理？
   - 笔记（默认启用）
   - 电子邮件（需要 Einstein 活动捕获）
   - 语音/视频通话（需要 Einstein 对话洞察）
   - 增强型电子邮件（用于电子邮件正文索引——需要 `EmailAdministrationSettings.enableEnhancedEmailEnabled`）
3. **自主更新**：代理应自主更新机会字段，还是仅建议更新供用户审查？
4. **代理应管理哪些字段？（首先， upfront 询问这个问题——设置由字段选择驱动）。** `setup-all.sh` 使用**仅您选择的字段**构建流程，从开始——没有部署两者然后删除步骤。询问：*"代理应建议哪些机会字段的值？OOTB 选项是下一步 (`NextStep`) 和机会阶段 (`StageName`)；您还可以添加自定义文本字段（例如，竞争对手分析字段）。"*
   - **至少需要 1 个字段**——如果未选择任何字段，设置将中止（退出 1）。**没有**默认的 `NextStep`。
   - **硬限制：总共 5 个字段**；OOTB 字段计入其中。选择更多将在任何更改之前中止。
   - 在非交互式运行中传递该集合 `--fields "NextStep,StageName,Risk__c"`，或在交互式提示时输入它。
5. **按字段提示自定义（所有字段除外 `StageName`）。** 对于每个选择的非 `StageName` 字段，设置收集可选的**目标**（“您必须考虑...”）和**指令**（提取指导）：
   - **`NextStep`** 配备了经过策划的 OOTB 管理提示。设置仅在您提供目标/指令时才覆盖它（交互式：它询问是否要自定义；非交互式：传递 `--field-goal "NextStep:..."` / `--field-instruction "NextStep:..."`）。跳过自定义以保留 OOTB 提示。
   - **自定义字段**始终获得目标/指令（您的文本，或脚本的合理默认值）。
   - **`StageName` 无法自定义**——它是一个无法覆盖的管理 picklist 模板；设置永远不会提示它。
6. **自定义字段资格**：仅支持机会上的标准或自定义**文本**字段——纯文本 (`type=string`) 或文本区域 ≤ 255 (`type=textarea`, `htmlFormatted=false`)；长度 ≤ 255；不是长文本区域（长度 > 255）、富文本区域 (`htmlFormatted=true`)、picklist 或公式。建议受字段自身长度的限制。在设置时选择的问题 4 中连接的字段在 `setup-all.sh` 期间被连接；**之后**添加的**新**字段运行 `scripts/add-field-suggestion.sh <org-alias> <FieldApiName>`（每个字段一个；见第 4.3 部分 Phase）。两者都执行 5 个总限制——`add-field-suggestion.sh` 拒绝连接第 6 个字段。
7. **机会阶段**：机会阶段是 picklist 值，不同的机会记录类型可能暴露不同的阶段子集。使用标准机会阶段还是自定义机会阶段？它们的描述是否需要定义/更新？注意：`OpptStageDescription` 是**每个阶段全局**——仅由 `OpportunityStageApiName` 键控，没有每个记录类型的列——因此每个活动阶段都编写**一次**，并适用于每个暴露该阶段的记录类型。无论组织是否有机会记录类型，设置工作方式都相同。

---

## 管理员沟通指南

**关键**：此技能服务于管理员用户，而不是开发人员。请遵循以下规则：

1. **在后台运行所有 bash 命令** (`run_in_background: true`) - 这包括主设置命令和任何用于进度监控的日志尾随
2. **在不显示命令的情况下监控进度** - 您可以尾随日志以提供进度更新，但也要在后台运行尾随命令。解析输出并仅显示友好的更新，如 "✓ 机会团队：启用"。永远不要显示尾随命令本身或原始日志行。
3. **静默调查错误** - 当某事失败时，请在后台进行您的诊断（检查数据、运行查询、修复环境问题），而无需描述每个步骤。仅显示结论和操作："我需要先创建一个测试机会。让我做..."，而不是 "JSON 输出损坏...让我检查... ANSI 颜色代码...让我修复..."
4. **用普通语言描述**：说 "设置平台..."，而不是 "运行 setup-all.sh Phase 1.5"
5. **隐藏技术细节**：没有 SOAP 响应、curl 命令、jq 解析、阶段编号或脚本路径，除非用户要求调试
6. **检查退出代码**：始终解析成功/失败，并将技术错误转换为管理员友好的消息
7. **设定时间预期**："这需要 ~3 分钟..." 可以防止 "是否冻结？" 问题
8. **优雅地处理错误**：自动重试瞬态故障；解释并提供针对真实阻塞器的选择

有关详细错误翻译模式、示例和恢复策略，请参阅 `references/admin-communication.md`。

## 工作流程

**重要——主要入口点**：对于端到端设置，驱动 `scripts/setup-all.sh`。它处理所有先决条件、启用、流程部署、权限和验证，并按正确的依赖顺序进行。仅在 `setup-all.sh` 运行后诊断或修复特定组件时才使用单个脚本。

`setup-all.sh` 是一个**三阶段、由字段选择驱动的**设置：（1）平台启用 + 代理用户 + PSG 分配；（2）字段选择 → 提示模板创建/激活 → 阶段描述（仅当选择 `StageName` 时）→ 提示验证；（3）流程构建（仅选择的字段）、流程激活、代理激活、PSG 重新计算。它默认**安全**：建议模式、除非询问否则不创建阶段描述，并且流程在提示就位之前不会上线。

#### 标准代理路径——两个调用之间有一个交互式微调循环

有关完整两调用模式、代码示例、代理规则、叙述模板和内部步骤映射，请参阅 `references/canonical-agent-path.md`。

**总结**：将设置分为调用 1 (`--through-phase prompts`) 和调用 2 (`--from-phase flow`)，并在它们之间进行微调循环，以驱动每个字段的提示批准。调用 2 是**必需的**——没有它，就不会存在流程，也不会生成建议。

#### 无需交互式/CI 路径（单个调用，无微调循环）

对于完全无需交互式运行（cron/CI，或当用户明确拒绝提示审查）：

```bash
bash setup-all.sh <org-alias> --fields "NextStep,StageName,Risk__c" \
  [--field-goal "NextStep:<text>"] [--field-instruction "NextStep:<text>"] \
  [--autonomous] [--create-stage-descriptions] [--skip-prompt-verification] \
  --non-interactive [--users "a@x.com,b@x.com"]
```

在单次模式下，验证步骤仍然打印每个字段的建议（信息性）。将它们传达给用户。

#### 标志

有关完整标志文档，请参阅 `references/flags.md`。主要标志：

- `--check-license` — 仅预检（退出 0 = 有能力，1 = 阻塞）。首先运行。
- `--through-phase prompts` / `--from-phase flow` — 分段运行端点（互斥）
- `--fields "NextStep,StageName"` — 必需字段集（至少 1 个，最多 5 个）
- `--autonomous` — 启用自动应用模式（默认关闭）
- `--non-interactive` / `--yes` — 无需交互模式（需要 `--fields`)
- `--users "a@x.com,b@x.com"` — 明确用户列表用于 PSG 分配（电子邮件验证）

下面的阶段解释了手动/修复场景的决策逻辑。有关逐步详细信息，请参阅 `references/setup-order.md`。

### 自动化摘要

每个配置步骤以及它是否是 CLI 自动化（以及如何）或 UI 仅有的，都存在于 `references/automation-matrix.md` 中。简而言之：先决条件、启用、流程克隆/激活、代理发布/激活、权限、字段建议和阶段描述都是 CLI 自动化的（`setup-all.sh` 按依赖顺序执行）；只有代理分析是 UI 仅有的。

---

### 阶段 0 — 身份验证和组织评估

1. **身份验证** — 请参阅 `references/auth-and-cli.md`。始终使用 `2>/dev/null` 在 `sf --json | jq`。

2. **评估组织状态** — 分支信号（不是 PSG 存在——PSGs 随许可证一起提供，即使在不配置的组织中也是如此）：
   - **启用**：通过 SOAP `readMetadata` 读取 `SalesDealAgentSettings.enableDealAgent`
   - **设置已运行**（任何之一）：(a) 代理用户持有 `SalesManagementAgentUserPsg`，(b) 存在流程 `Process_Field_Update_Suggestions`（通过 ApiName，而不是标签），(c) `BotDefinition` 与 `AgentTemplate IN ('SalesMgmt__NGASalesAgent','SalesMgmt__SalesAgent')`

3. **运行 `scripts/setup-all.sh <org-alias>`** — 自动处理分支：
   - 无启用 + 无信号 → 全新（阶段 1）
   - 部分信号 → 修复（阶段 3）
   - 所有存在 → 仅验证

### 阶段 1 — 启用先决条件和流程管理

**请参阅 `references/setup-order.md` 以获取完整的脚本。** 按依赖顺序启用：Einstein GenAI → Agentforce Agent → Agent Platform → Enhanced Notes → Opportunity Team → 流程管理 → 流程检查。然后部署流程 (`scripts/create-flow.sh`) 并验证代理架构 (`references/agent-creation.md`).

**启用时自动创建的内容**：代理用户 + PSGs（自动分配）。**您必须创建的内容**：`BotDefinition:SalesAgent`（通过作者ing-bundle 发布）和计划触发流程（通过模板部署）。

### 阶段 2 — 分配权限

1. **定义代理访问**：`bash scripts/define-agent-access.sh <org-alias>` — 创建自定义权限集，链接到两个 PSG。请参阅 `references/agent-creation.md` → "代理访问"。

2. **将 PSG 分配给目标用户**：**硬规则——永远不要批量分配。** 仅授予 `SalesManagementUserPsg` 给：(1) 运行用户，以及 (2) 显式的 `--users` 列表。不枚举并授予。

### 阶段 3 — 修复模式（部分配置组织）

请参阅 `references/repair-diagnostics.md` 以获取完整清单。常见问题：流程已停用 → Tooling API `PATCH`；代理未激活 → `sf agent activate`；提示模板未激活 → 版本循环重新部署；代理缺失 → SOAP 开关关闭/打开。

### 阶段 4 — 自定义（需要管理员决策）

1. **定义机会阶段描述** — 使用来自 `references/opportunity-stages.md` 的“提议和纠正”模式。查询活动阶段，显示参考文件中的默认值，应用用户更正，通过 Tooling API 批量创建。

   **重要**：当流程管理启用时，阶段描述**可能**会自动配置（测试组织显示 MEDDIC 描述预先填充）。**始终在尝试创建它们之前检查是否存在描述**。如果描述已存在，请更新而不是创建以避免重复。

2. **配置其他数据源** — 请参阅 `references/data-sources.md` 以获取决策表（Einstein 对话洞察、Einstein 活动捕获、Inbox）。

3. **添加自定义机会字段建议（设置后）** — 在设置时选择的问题 4 中连接的字段在 `setup-all.sh --fields` 期间被连接。要向已配置的组织添加**新**字段，请运行 `scripts/add-field-suggestion.sh <org-alias> <FieldApiName>`（例如 `Risk__c` 字段）。脚本验证字段，填充规范模板 (`assets/field-completion-template.genAiPromptTemplate-meta.xml`)，通过版本循环部署和激活它，并 idempotently 将字段连接到实时 `Process_Field_Update_Suggestions` 流程（尊重 5 个字段限制）。可选标志：`--label`, `--goal`, `--instruction`（两个字段特定的提示行），`--verify-with-note`（为同步生成种子一个笔记），`--opp <Id>`, `--skip-flow`, `--force`。有关机制和 `references/field-completion-prompts.md` 中 `references/field-completion-prompt-template.md` 中编写目标/指令行的说明，请参阅 `references/field-completion-prompts.md`。

   > **命名注意**：提示模板 `<type>` 是 `einstein_gpt__fieldCompletion`（在所有元数据中使用——永远不要更改它）。**设置 UI**（提示构建器）将此类别标记为 **"字段生成"**——相同的东西。管理员应查找 "字段生成"，而不是 "字段完成"。

4. **配置自主更新** — 自主模式是一个**组织范围的**切换 (`SalesDealAgentSettings.enableDealAgentAutoApproveAllTasks`)，而不是每个字段的设置：开启时，代理自动应用所有字段建议而无需审查；关闭时（默认值），每个建议都等待人工批准。它通过 `setup-all.sh --autonomous` 选择性启用。有关切换和安全考虑，请参阅 `references/autonomous-updates.md`。

5. **启用代理分析** — 设置 → Einstein 反馈和监控 → 代理分析（UI 仅有的）。

---

## 理解流程

请参阅 `references/flow-clone-from-template.md` 以获取完整的流程架构、克隆方法和技术限制。

**关键事实**：流程管理使用计划触发的流程 (`Process_Field_Update_Suggestions`) 从管理模板克隆。检测通过 ApiName（而不是标签）。流程调用 `getOrExecFieldUpdtSuggestion` 使用选定的字段——添加字段需要同时激活其模板并将其连接到流程的集合（由 `add-field-suggestion.sh` 原子处理）。**直到此流程激活，否则不会生成任何建议。**

---

## 关键注意事项

- **流程管理需要一个独立的 `BotDefinition:SalesAgent`** — 缺少 BotDefinition 会阻止设置。在大多数版本中，自动配置会创建它，但在没有的情况下，`publish_and_activate_agent()`（在 `shared/agent-bundle-publish.sh` 中，由 `setup-all.sh` 和 `create-agent.sh` 调用）从 `assets/sales_management_agent.agent` 发布捆绑包并激活它。**不要依赖 `EmployeeCopilotPlanner` 回退**——用户需要交互式聊天界面。
- 流程仅在代理**激活**并具有**读取/写入**机会时运行；代理作为机会团队成员加入（注意机会团队成员上的 Apex 触发器）
- 每日限制：8,000 LLM 请求 / ~4,000 机会。建议在 30 天后过期
- 阶段模板通过 `GetOpportunityStageDetailsInvocableAction` 读取 `OpptStageDescription` — 如果任何活动阶段缺少描述，**阶段建议会失败**
- **不要使用 CLI Metadata 部署**来启用 DealAgent — 仅 SOAP API v64.0（CLI 有静默失败模式）
- **不要启用 `BotSettings`/`enableBots`** — 遗留消息传递代理，与之无关，会因“法律条款”错误而失败
- 流程管理**不使用**管理包——组件在启用时直接配置
- 切换在设置中不可见——验证 Sales Cloud EE+ 许可证和 Agentforce SKU
- 始终使用 `2>/dev/null` 在 `sf ... --json` 管道到 jq（删除损坏 JSON 的 CLI 警告）

---

## 参考

- `references/setup-order.md` — 完整的复制粘贴设置序列，包含所有脚本
- `references/soap-api-enablement.md` — 所有先决条件的 SOAP API 模式
- `references/flow-clone-from-template.md` — 基于ApiName检测的流程克隆方法
- `references/agent-creation.md` — 代理创建（自动配置 + 作者ing-bundle 发布；SOAP 开关仅重新配置代理用户和 PSGs，而不是 BotDefinition）
- `references/field-completion-prompts.md` — 端到端添加自定义字段建议（验证 v67 模式，三个要求，`add-field-suggestion.sh` 机制，验证）
- `references/field-completion-prompt-template.md` — 编写脚本消耗的字段特定目标/指令行
- `references/opportunity-stages.md` — 阶段描述 + 方法
- `references/repair-diagnostics.md` — 部分配置组织处理
- `references/auth-and-cli.md` — 身份验证方法，CLI 兼容性
- `references/data-sources.md` — EAC/ECI/笔记/增强型电子邮件的决策表
- `references/autonomous-updates.md` — 自动应用模式切换和安全考虑
- `references/metadata-inventory.md` — 完整的已配置元数据组件清单
- `references/automation-matrix.md` — 设置步骤哪些是 CLI 自动化（以及如何）与 UI 仅有的
- `references/admin-communication.md` — 管理员友好的叙述模式：错误翻译表，静默调查示例，以及每一步叙述模板，用于对话式设置

## 示例

- `examples/custom-prompt-instructions.md` — 自定义提示指令模式，用于方法对齐和更新侵略性控制

## 独立脚本

每个设置阶段的可执行脚本（从 `scripts/` 目录运行，`sfdx-project.json` 在当前工作目录中）：

- `scripts/setup-all.sh` — **主编排**：3 阶段，由字段选择驱动的端到端设置（身份验证 + 启用 + 代理用户/PSG → 字段选择 + 提示模板 + 阶段描述（仅当选择 `StageName` 时）+ 提示验证门 → 流程构建/激活 + 代理激活 + PSG 重新计算）。需要 `--fields`（如果没有则中止）；默认交互式；安全默认值（建议模式、除非询问否则不创建阶段描述，并且流程在提示就位之前不会上线）
- `scripts/shared/flow-builder.sh` — `setup-all.sh` 源代码的流程字段收集帮助程序：`build_field_collection`（全新——仅写入选择字段的流程），以及 `strip_flow_field` / `add_flow_field` / `flow_wired_fields`（修复——原地重新协调已部署流程的字段）
- `scripts/shared/stage-descriptions.sh` — 阶段描述（第 4.3 部分）源代码由 `setup-all.sh` 提供；导出 `run_stage_descriptions()`（自我门控 `STAGENAME_SELECTED`；设置 `STAGE_DESCRIPTIONS_BLOCKED` 为第 8.5 阶段总结）
- `scripts/shared/test-opp.sh` — 共享测试机会 + 基础知识笔记解析源代码由两个验证脚本 (`flow-debug-and-verify.sh`, `verify-prompt-generation.sh`) 提供；导出 `resolve_test_opportunity`（重用/创建/回退 `[PM-TEST]` 测试机会，滚动 CloseDate +30 天，种子/刷新基础知识笔记）和 `seed_grounding_note`
- `scripts/retrieve-settings.sh` — 审计当前组织设置状态
- `scripts/enable-prerequisites.sh` — 仅启用先决条件**设置**（Einstein GenAI, Agentforce, Enhanced Notes, Opportunity Team）通过 SOAP — 不部署字段/流程/代理。`setup-all.sh` 运行相同的启用内联；仅用于外科手术，非破坏性先决条件切换
- `scripts/enable-deal-agent.sh` — 通过 SOAP API 启用流程管理（独立辅助程序；`setup-all.sh` 内联启用 PM — 仅用于隔离手动切换）
- `scripts/create-flow.sh` — 检测、从模板部署或激活建议流程（回退到 UI 指导）
- `scripts/create-agent.sh` — 验证/创建/激活代理（自动配置 + 作者ing-bundle 发布；SOAP 开关仅重新配置代理用户/PSGs，而不是 BotDefinition）；完成时还定义了 Agent Access
- `scripts/define-agent-access.sh` — 定义 Agent Access，以便持有 `SalesManagementUserPsg` 的用户和持有 `SalesManagementAgentUserPsg` 的自主代理用户都可以启动/运行代理（自定义权限集 + `SetupEntityAccess` + `PermissionSetGroupComponent` 链接到两个 PSG + 重新计算）
- `scripts/deploy-settings.sh` — 部署非 SOAP 设置（笔记，电子邮件，机会）
- `scripts/add-field-suggestion.sh` — 为任何合格的机会文本字段添加 AI 字段完成建议（验证 → 填充规范模板 → 部署 + 激活通过版本循环 → 流程连接；`--verify-with-note` 用于同步生成）
- `scripts/verify-all.sh` — 全面配置状态检查（只读）

## 管理员验证工具

以下脚本帮助管理员验证设置后流程管理是否正常工作。使用这些脚本来确认字段建议是否按预期生成。

**在运行任何验证脚本之前，请使用 `PM_GROUNDING_NOTE` 环境变量组合一个现实的 grounding note。** 只有当机会的笔记包含真实的销售上下文时，AI 才会生成建议——一个通用的占位符在没有任何内容的情况下生成，使工作设置看起来是损坏的。编写几句话，反映配置的 `--fields` 和任何 `--field-goal`/`--field-instruction`（例如 `NextStep` 的具体下一步和截止日期；买方，预算，痛苦和时间线信号对于 `StageName`）。不要使用僵化的模板——根据配置量身定制。示例：`PM_GROUNDING_NOTE="与销售副总裁的发现通话：确认预算为 $250K，第三季度上线；同意下一步是 IT 进行技术深入分析和 ROI 分析。" bash scripts/flow-debug-and-verify.sh <org>`。如果没有环境变量，脚本会回退到通用笔记。**

**两个脚本都由技能分别调用，但它们都使用相同的测试机会和相同的 grounding note。** 它们都找到或创建一个名为 `[PM-TEST] Test Pipeline Verification Opp` 的用户拥有的机会（`[PM-TEST]` 前缀使此工具创建的每个机会都可以通过 `Opportunity WHERE Name LIKE '[PM-TEST]%'` 找到）。在重用时，它们将机会的 CloseDate 滚动 +30 天，以便它保持流程资格，并且仅在您传递的 `PM_GROUNDING_NOTE` 与存储的不同时才刷新 grounding note（否则保留现有笔记）。将相同的 `PM_GROUNDING_NOTE` 值传递给两个调用，以便笔记在任何运行顺序下都保持一致。

- `scripts/flow-debug-and-verify.sh` — 两个阶段验证计划触发建议流程的引导。
  - **flow-debug-start** (`bash scripts/flow-debug-and-verify.sh <org> [opp-id]`) 如果仍然符合条件的稳定用户拥有的测试机会（以便重复运行不会堆叠重复的机会），否则创建它，如果创建失败，则回退到任何用户拥有的开放机会，种子/刷新 whichever opportunity 解析的 grounding Note，并打印流程的 **Debug** URL、要选择的机会，以及后续运行的 `verify` 命令的确切内容——包括末尾的基线计数（运行 Debug 之前建议的计数）。它使用用户拥有的机会，因此生成的建议在管理员的所有者范围内可见的 Pipeline Inspection。如果没有机会可用，它会打印一个可操作的消息并退出 0 而不进行验证。将 URL + 机会传达给用户并等待他们运行 Debug in Flow Builder 对该机会进行 Debug — 这是唯一可以按需绑定到计划记录触发流程的实时 `$Record` 的路径（保留回滚模式未选中，以便 DML 持久化）。
  - **verify** (`bash scripts/flow-debug-and-verify.sh <org> <opp-id> verify [baseline]`) 在用户确认 Debug 运行完成后运行：它确认流程达到其操作（代理用户添加到机会团队）并轮询 (~4 分钟) 以等待生成的 `AiGenActionItem` 建议的生成。**传递 flow-debug-start 打印的基线**——它在 Debug 运行之前捕获，因此差异是精确的；省略它回退到较弱的绝对检测。阶段之间的等待发生在对话中，而不是在脚本内部。
- `scripts/verify-prompt-generation.sh` — 通过直接调用 Einstein `/generations` API 测试背后的提示模板。传递**字段** API 名称 (`bash scripts/verify-prompt-generation.sh <org> <field> [opp-id]` — 例如 `NextStep`, `Risk__c`)；它解析字段到其管理/派生模板（一个裸的、无命名空间的已删除返回 `ENTITY_IS_DELETED`）并使用与 `flow-debug-and-verify.sh` 相同的用户拥有的机会选择策略（两者共享一个源库：重用/创建/优雅地跳过）——跳过的唯一区别是未进行 Einstein 端点调用。显示实际生成的建议文本，帮助管理员验证自定义提示指令。

## 代理资源

- `assets/sales_management_agent.agent` — 销售管理代理的代理脚本定义（在自动配置失败时使用）
- `assets/sales_management_agent.bundle-meta.xml` — AiAuthoringBundle 元数据（使用 `sf agent publish authoring-bundle --api-name SalesAgent` 部署）
- `assets/field-completion-template.genAiPromptTemplate-meta.xml` — 带有 `@@PLACEHOLDERS@@` 的规范 `einstein_gpt__fieldCompletion` 提示模板，由 `scripts/add-field-suggestion.sh` 填写（不要直接部署）
