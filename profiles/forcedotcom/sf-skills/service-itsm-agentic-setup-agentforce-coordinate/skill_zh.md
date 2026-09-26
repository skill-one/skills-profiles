# Agentforce for ITSM 设置编排器

通过展示可用功能、委派给专业子技能以及跟踪进度，引导用户设置 Agentforce Studio、IT 服务履行代理、IT 服务员工代理、专业员工代理以及 Salesforce Service Cloud ITSM 中的员工-代理到人工升级。

## 目标

作为 ITSM 中 Agentforce 功能配置的协调者。向用户展示可配置功能的菜单，为每个选择调用相应的子技能，并在每个功能完成后返回更新进度的菜单，直到用户完成。

## 行为

### 1. 从对话中提取上下文

在展示选项之前，扫描聊天记录以：

- 确定用户已经设置哪些功能（跳过或标记为完成）
- 任何提及的偏好或限制（例如，“仅启用 Agentforce Studio”，“我们已经有 Studio 了”）
- 目标组织（如果提及）
- 商业上下文，以确定哪些功能相关

### 2. 确认目标组织

Agentforce 设置对**真实组织进行写操作**（功能开关启用、代理创建和激活）。在委派给任何子技能之前，请用户确认目标组织，并明确说明该组织将被修改。永远不要假设生产环境是安全的——要求明确确认组织。

### 3. 将 Agentforce 功能菜单作为多选展示

向用户展示可用和已完成的内容，并按两个**顺序设置阶段**组织——**阶段 1：启用平台功能**（Agentforce Studio 启用）和**阶段 2：安装和激活代理模板**（履行者和员工代理）。这种分离是承重的：阶段 1 *启用*组织级别的平台开关/偏好，而阶段 2 *从模板安装和激活*代理——它们是不同类型的操作，必须作为不同阶段读取，而不是一个未区分的列表。只有具有可用子技能的功能会出现在菜单中——使用 `examples/output-templates.md` 中的 **Feature menu** 模板。通过单个多选提示收集用户的选择（当工具允许时，使用 `AskUserQuestion` 并设置 `multiSelect: true`，否则请用户回复数字列表，例如 `1, 2`）。使用 **Feature menu 表格中的确切 Item 名称**作为多选选项标签——逐字，包括每个项目的括号注释和“Agent”及其大写（`Agentforce Studio enablement (所有代理的基础)`，`IT Service Fulfiller Agent`，`IT Service Employee Agent`，`Specialized Agents for Employee`，`Employee Agent escalation`）——以便选择器选项和表格永远不会出现分歧。每个项目的**描述列与 Salesforce 设置 → Agentforce for IT Service 页面上的措辞匹配**（履行者和员工代理模板描述以及专业员工代理文本被逐字使用），以便用户在评估要安装哪个模板时读取相同的目的/范围——不要释义或缩短产品副本。对于三个阶段 2 代理项目，跟随逐字产品副本后添加一个简短的 `Setup:` 行，说明安装的内容（对于履行者和员工代理，`Setup: 从此模板创建代理并激活版本。`；对于专业员工代理，`Setup: 选择一个专业模板（例如密码管理器、入职），然后创建和激活该独立代理。重新运行此项目以添加更多。`，对于您，您首先询问用户想要哪个专业员工代理，并将该名称传递给子技能），以便单个行包含目的、范围和安装操作。阶段 1 行（Agentforce Studio enablement）是一个平台启用开关，不是模板安装，因此没有 `Setup:` 行。当引发 `AskUserQuestion` 时，将相同的描述文本（产品副本 + `Setup:` 行）放在每个选项的 `description` 字段中，以便选择器也包含详细信息。**报告文件（harness / 非交互式运行）。** 如果提供了 `${outputDir}`（通过 harness 的生成文件位置指令），在引发 `AskUserQuestion` **之前**将菜单输出（归属头 + 功能表与状态 + 委派目标 + 依赖信号 + 多选提示本身）写入 `${outputDir}/report.md` —— 这样即使 harness 在确认门处停止，报告文件也始终存在。在每次功能完成后，使用更新后的状态表覆盖同一文件。在为用户在聊天表面上交互式运行时跳过这些写入——仅在将 `${outputDir}` 作为显式目标传递时写入。

### 4. 按依赖顺序委派给子技能

**Studio 优先规则（无条件）。** 如果 Agentforce Studio 启用（#1）在用户的选择中并且尚未完成，则**始终首先运行**它——无论用户列出其数字的顺序如何。履行者代理（#2）、员工代理（#3）和专业员工代理（#4）都依赖于 Studio 启用，如果首先尝试它们将失败。静默重新排序队列，以便 Studio 在任何代理之前运行。此规则无商量的余地，无论用户选择两个功能（Studio + 一个代理）还是所有功能。员工代理升级（#5）是一个后设置操作，也永远不会在 Studio 之前运行。

**用户顺序规则（仅 #2、#3 和 #4 之间）。** 履行者代理（#2）、员工代理（#3）和专业员工代理（#4）相互独立——没有一个依赖于另一个。如果选择多个，则按用户列出的顺序运行（默认 2 → 3 → 4 当未指定时）。此规则**仅**适用于 #2、#3 和 #4 之间的排序；它永远不会覆盖上面的 Studio 优先规则。

**升级-后-员工规则（#5 依赖于 #3）。** 员工代理升级（#5）配置员工代理的手动交接，因此它**需要员工代理（#3）存在并处于活动状态**首先。如果 #5 被选择，请确保 #3 在此运行中成功完成（或已经完成）再委派给它；否则将 #3 提前于 #5。#5 永远不会在 Studio（#1）之前运行。

**运行时访问-后-创建规则（无条件）。** 每当任何阶段 2 代理（#2、#3、#4）在此会话中返回一个**活状态**（`CREATED`/`ALREADY-CREATED`/`ACTIVATED`），则在队列**后**自动附加一个**阶段 3 运行时访问**步骤——阶段 3 的后置依赖关系：始终附加，永远不会是菜单选择——并在最后一个阶段 2 代理后委派给 `service-itsm-agentic-setup-agent-runtime-access-assign`，涵盖每个新活的代理（其自己的目标用户 + 确认写入门控制权限；阶段 3 保证*提供*，永远不会是静默授予）。这是无商量的：一个活代理的操作在没有用户权限的情况下会失败，直到此设置它们。**不要**在仅 Studio 运行或没有代理变为活状态（`FAILED`/`PARTIAL`/`PENDING CONFIRMATION`/`DECLINED`，或一个停止队列的阶段 2 验证）时附加它。叙述 + 状态映射：**运行时访问交接**在 `examples/output-templates.md`。

| # | 功能 | 阶段 | 子技能 |
|---|-------|-------|-------|
| 1 | Agentforce Studio enablement (所有代理的基础) | 1 | `service-itsm-agentic-setup-agentforce-studio-configure` |
| 2 | IT Service Fulfiller Agent | 2 | `service-itsm-agentic-setup-fulfiller-agent-configure` |
| 3 | IT Service Employee Agent | 2 | `service-itsm-agentic-setup-employee-agent-configure` |
| 4 | Specialized Agents for Employee | 2 | `service-itsm-agentic-setup-employee-agent-configure` |
| 5 | Employee Agent escalation | 后 | `service-agentforce-human-escalation-configure`（传递 IT 场景输入：代理 `IT_Service_Employee_Agent`，队列 `General_IT_Queue`，`CONTEXT_OBJECT=MessagingSession`） |
| — | 运行时访问（自动在任何阶段 2 创建/激活后；永远不会是用户选择） | 3 | `service-itsm-agentic-setup-agent-runtime-access-assign` |

**IT Service Employee Agent 与 Specialized Agents for Employee。** 两者都委派给相同的子技能，`service-itsm-agentic-setup-employee-agent-configure`——区别在于它安装的模板。IT Service Employee Agent 安装**广泛、即用型**的员工代理（子技能的默认值，当未命名专业化时）。专业员工代理安装一个**专业化**的代理，而不是——子技能仅在传递专业模板名称时才采取专业路径；传递无内容时它静默回退到广泛代理，重新创建 IT Service Employee Agent。因此，**在委派专业员工代理之前，询问用户想要哪个专业员工代理**——提供常见示例（密码管理器、证书管理、入职、硬件请求），注意还有更多可用，并让子技能消除部分或不明确的名称；然后委派**具有该命名专业化**（所选模板命名代理）。**永远不要在没有命名专业化的情况下委派专业员工代理**——这是产生重复广泛代理的唯一情况。专业模板本身在阶段 1 中启用；此项目是构建和激活其中一个模板的代理。

`service-itsm-agentic-setup-agentforce-studio-configure` 执行自己的预运行读和分类（在写入之前读取活状态切换）而不是委派给 `service-itsm-agentic-setup-agentforce-studio-validate`——该技能是一个单独的只读入口点，用户可以直接调用以检查准备状态而不进行写入。此编排器不需要作为上述委派流程的一部分调用它。

### 5. 每个功能完成后

一旦子技能完成：

1. **验证**子技能自己的确定性裁决，通过运行 `node "<skill_dir>/scripts/verify-child-verdict.mjs" <studio|fulfiller|employee|escalation|runtime> <verdict>`——永远不要在散文中重新推导成功/失败的比较。传递 Studio 的 `overall` 字段来自 `classify-final-report.mjs`，履行者/员工代理的 Phase 8 汇总裁决，升级叶子的 `status`（`CONFIGURED`/`ALREADY-CONFIGURED`），或运行时访问技能的 Phase-7 汇总作为 `<verdict>`。退出代码 `0` 表示前进；退出代码 `1` 表示**停止并以 plain language 表面失败——不要前进到队列中的下一个功能。** 部分启用的 Studio（例如 Einstein GenAI 开启但父级伞状仍然阻止，`overall: PARTIAL`）也会导致履行者/员工代理创建失败，因此脚本将 `PARTIAL` 与 `FAILED` 视为前进目的。

2. **更新状态**——将已完成的功能标记为“完成”

3. **建议下一步逻辑**——如果还有其他功能可用，根据依赖顺序推荐它

4. **重新展示菜单**使用更新后的状态——使用 `examples/output-templates.md` 中的 **Post-feature progress** 模板

5. **阶段 3 在阶段 2 队列排空后。** 一旦没有阶段 2 代理排队且至少有一个在此会话中变为活状态，委派一次附加的**阶段 3**（如上所述）并使用 `verify-child-verdict.mjs runtime <verdict>` 验证——退出 `0` ⇒ 阶段 3 完成 → 完成摘要；退出 `1` ⇒ 停止并以 plain language 表面。

### 6. 完成摘要

当用户表示他们完成时（或所有可用功能都已配置），使用 `examples/output-templates.md` 中的 **Completion summary** 模板展示最终摘要。

---

## 设置阶段与推荐顺序

设置按**两个顺序设置阶段**运行，然后是可选的后设置升级。阶段 1（启用平台功能）必须在阶段 2（安装和激活代理模板）完成之前完成。升级仅在员工代理激活后运行。

```text
阶段 1 — 基础：启用平台功能
  1. Agentforce Studio enablement (所有代理的基础)   (打开组织级别的 Agentforce + Einstein GenAI 功能开关)

阶段 2 — 代理模板：安装和激活   (仅在阶段 1 之后)
  2. IT Service Fulfiller Agent          (从模板安装、提交并激活代理)
  3. IT Service Employee Agent           (从其模板安装广泛员工代理并激活它)
  4. Specialized Agents for Employee     (从用户选择的模板安装一个专业员工代理——并激活它)

阶段 3 — 运行时访问   (自动 — 在任何阶段 2 代理变为活状态后，不是菜单选择)
  • 授予活代理的运行时功能权限 + 一个 Agent Access 权限集

后设置 — 人工升级   (仅在使用 3 激活后)
  5. Employee Agent escalation           (配置 canEscalate、出站路由、一个有工作人员的 General IT 队列，以及失败阈值指令)
```

阶段 1（Agentforce Studio enablement）是**基础**——它打开组织级别的 Agentforce 和 Einstein GenAI 开关，每个代理（以及专业员工模板）构建在其上，因此首先启用它；任何在它之前尝试安装/激活的代理都会失败。三个阶段 2 项目是独立的兄弟姐妹，一旦阶段 1 完成，可以自由排序，专业员工代理紧跟在 IT Service Employee Agent 之后，因为两者都从相同的子技能构建员工代理（广泛默认与用户选择的模板）。员工代理升级（一个对活员工代理的后设置操作）和 **阶段 3（运行时访问）**（在任何阶段 2 代理变为活状态后自动——不是菜单选择）受上述规则管理。

---

## 规则

- **始终**在设置头中显示 "(via service-itsm-agentic-setup-agentforce-coordinate)"
- **始终**在执行任何操作之前展示功能菜单——不要假设用户想要哪个功能
- **始终**将功能菜单作为多选展示——接受一个或多个功能在单个交互中
- **永远**不要在没有用户选择的情况下设置功能。（显式选择确保用户确认意图并避免在流程中取消时出现部分配置；使用“设置所有内容”规则中的顺序确认循环进行批量请求。）
- **永远**不要展示没有可用子技能的功能
- 如果用户说“设置所有内容”或“全部”，按推荐顺序逐个通过每个可用功能进行确认
- 跨对话跟踪进度——不要将已完成的功能重新展示为“未完成”
- 专业员工代理（#4）是**可重新选择**的——每次运行都从用户选择的模板构建一个*不同的*专业员工代理。将刚刚构建的代理标记为 `Done`，但保持 #4 可用以运行更多专业代理；不要像处理一次性完成项目那样将完成的 #4 视为永久完成。如果用户再次选择 #4，请询问要使用哪个专业模板
- 员工代理升级（#5）是一个**后设置**操作，需要 IT Service Employee Agent（#3）处于活动状态才首先执行——永远不会在 #3 在此运行中成功之前委派 #5
- **永远**不要在当前功能失败或仅部分成功的情况下前进到队列中的下一个功能——相反，停止并以 plain language 表面失败
- 如果 Agentforce Studio 启用报告组织缺少 Agentforce 许可证（`accessCheck`），**停止**整个流程——这是一个许可证/版本要求，没有 API 可以授予，履行者或员工代理也无法成功
- **始终**在委派给任何子技能之前确认目标组织，并说明该组织将被修改
- **不要**在用户界面输出中暴露内部技术术语。这包括 Salesforce 记录 ID 和组织 ID、原始 HTTP 状态代码（403、500、…）、API 错误代码（`FUNCTIONALITY_NOT_ENABLED`、`DUPLICATE_VALUE`、…）、内部端点/API 名称、开发者名称（像 `sales-cloud-agent-studio` 这样的功能 apiNames），以及 CLI/工具内部。将所有内容翻译成 plain、human-readable 语言。作为下一步指针显示的子技能名称是允许的。
- **永远**不要在用户界面散文中用裸项目编号命名功能。`#1`–`#5` 标签（以及菜单的 `#` 列）是此技能的排序/委派规则的**内部简称**，仅用于菜单选择处理（用户回复 `1, 2`）——不是功能名称。在每个用户读取的消息中——opt-out/skip、prerequisite/blocked、进度、下一步、以及完成摘要——以完整名称命名每个功能，永远不要裸数字或范围如 `#4` 或 `#1–#3`。这在与阶段 1 开关跳过相关时最重要：命名被阻塞和仍然可用的功能，不要说 "#4 被阻塞，#1–#3 可以进行"。见 **prose 中命名功能**在 `examples/output-templates.md`。
- 如果用户询问关于 Agentforce 功能的，这些功能尚未可用（例如 Requester 代理、自定义主题包、代理指标仪表板），告诉他们这些功能在此编排器中不可用，并将作为其子技能合并时添加

---

## 验证清单

在此技能发出任何菜单或摘要之前，在脑海中确认以下内容。如果任何框未勾选，请在发送之前调整输出。

- [ ] 头行以 `(via service-itsm-agentic-setup-agentforce-coordinate)` 结尾
- [ ] 目标组织已与用户确认，并且他们被告知该组织将被修改，在运行任何子技能之前
- [ ] 当前功能的子技能结果在前进到队列中的下一个排队功能之前被验证为完全成功——失败或部分结果停止了队列
- [ ] 仅显示具有可用子技能的功能；隐藏占位符功能
- [ ] 功能菜单作为多选展示（如果用户已经命名了一个特定功能，则仅单选）
- [ ] 每个功能行的 `Status` 列反映从对话中实际跟踪的状态（`Not done`，`In progress` 或 `Done`）——不是硬编码的默认值
- [ ] 每个功能行的 `Description` 与 Salesforce 设置 → Agentforce for IT Service 页面的措辞匹配（履行者和员工代理模板描述逐字，未释义），三个阶段 2 行每个都以简短的 `Setup:` 安装行结尾，并且 `AskUserQuestion` 选项描述包含相同文本
- [ ] 专业员工代理行作为阶段 2 项目显示为 IT Service Employee Agent 之后，并且 #4 永远不会委派给 `service-itsm-agentic-setup-employee-agent-configure` 而不首先询问用户想要哪个专业模板（传递无名称，子技能默认为广泛代理并重复 #3），并且它带有其 `Setup:` 安装行
- [ ] 员工代理升级行作为后设置项目显示在阶段 2 代理之后，并且 #5 永远不会在 IT Service Employee Agent（#3）处于活动状态之前委派给 `service-agentforce-human-escalation-configure`
- [ ] 对于完成摘要，头行和结尾行由 `examples/output-templates.md` 中的规则选择（所有 `Done` → *Complete*；任何 `Not done`/`In progress` → *Finished*）
- [ ] 仅因为用户显式选择了它（或在“全部”/“所有”请求下的确认下按顺序进行）才配置功能
- [ ] 在委派给任何阶段 2 代理（履行者、员工或专业员工代理）之前验证 Studio 启用已完成
- [ ] 如果任何阶段 2 代理变为活状态，则委派一次附加的**阶段 3** 并委派给 `service-itsm-agentic-setup-agent-runtime-access-assign`（否则跳过）
- [ ] 下一步操作委派给子技能，而不是内联配置功能
- [ ] 输出中不出现 Salesforce 记录 ID —— 仅显示 human-readable 名称
- [ ] 用户界面散文中**永远**不要用裸项目编号或范围（`#4`，`#1–#3`）命名功能——每个功能都以完整名称命名；数字仅作为菜单选择处理时出现

---

## 参考文件索引

| 文件 | 何时读取 |
|------|--------|
| `examples/output-templates.md` | 行为步骤 3、5 和 6 — 功能菜单（两阶段、多选）、后功能进度和完成摘要文本块 |
| `scripts/verify-child-verdict.mjs` | 行为步骤 5 — 通过 `Bash`（`node`）运行以在队列前进之前确定性地检查子技能的裁决 |
