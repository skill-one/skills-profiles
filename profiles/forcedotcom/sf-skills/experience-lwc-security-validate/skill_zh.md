<!-- adk-managed-skill -->

# 审核LWS安全

对 Lightning Web 组件 (LWC) 运行结构化的 Lightning Web 安全 (LWS) 和产品安全合规检查。有两种输出模式：

- **审核模式**（默认）— 严重性排序的发现结果 + 应用代码修复。
- **评分模式** — SARIF 2.1.0 JSON 报告，按 LWS 规则目录（`lws-001`…`lws-023b`）索引，用于下游门禁、评估评分或 CI 摄入。

两种模式都使用来自参考的相同检测规则；仅输出格式不同。

## 使用场景

- 用户要求对特定 LWC 进行“安全审核”、“LWS 检查”、“发货前安全审计”或“合规检查”→ 审核模式。
- 用户要求“评分”组件的安全性或需要机器可读的发现结果以供门禁或评估使用 → 评分模式。
- 准备组件发布并需要统一的安防报告。
- 实施修复后，以验证安全态势没有回归。

**不使用此技能的情况**：
- 构建新组件（使用 `experience-lwc-generate`）。
- 可访问性（单独应用 WCAG 2.2）或 RTL 审核范围外。
- 在修复后通过功能标志门禁（修复完成后应用功能标志门禁）。
- 非 LWC 安全审核（Apex、Aura、服务器端）范围外。

## 前置条件

- 组件路径（`modules/…` 下的 LWC 包）。
- 可以访问组件的 JS/TS、HTML 模板、CSS 和 `.js-meta.xml`。
- 输出模式：`review`（默认 — 发现、修复、报告）或 `score`（发现、发出 SARIF JSON，不要修改代码）。如果请求中不明显，请在开始前与用户确认。

## 知识库

每个参考都是事实来源。不要凭记忆总结 — 打开参考，应用指南，并在报告中引用您使用的具体章节。

- Lightning Web 安全 (LWS) 目录：[LWS 安全专家](references/lws-security-expert.md) — 阻止的 API 和允许的替代方案。
- 规则目录（`lws-001`…`lws-023b`）：[产品安全框架](references/security-analysis.md) — 目录为每个规则提供检测模式和标准的 SARIF `ruleId` / `level` / `message` 模板。**评分模式使用这些确切值对每个匹配项发出一个 SARIF 结果。**

## 工作流程

### 第 1 步 — 确定范围

收集组件路径并确定要审核的文件。包含组件包中的每个文件：`.html`、`.js`/`.ts`、`.css`、`.js-meta.xml`，以及由同一团队拥有的、在目标中调用的子组件。

注意任何现有的功能标志门禁 — 需要代码更改的发现结果必须尊重它们。

### 第 2 步 — 阅读知识库

在判断前，从上到下阅读 [LWS 安全专家](references/lws-security-expert.md) 和 [产品安全框架](references/security-analysis.md)。LWS 参考列出了阻止的 DOM API 及其允许的替代方案；产品安全框架提供了严重性分类、23 条 SARIF 目录和修复模式。

### 第 3 步 — 遍历规则目录

对组件包运行 [产品安全框架](references/security-analysis.md) 中的每个规则（`lws-001` 到 `lws-023b`）。对于每个规则：

1. 逐字应用 **“如何发现问题”** 模式。不要走捷径 — 每个规则列出了需要考虑的混淆模式（括号表示法、Unicode 转义、`Reflect.*`、字符串连接）。
2. 对于每个匹配项记录：`ruleId`、`level`（来自目录的 `error` / `warning`）、`file`、`startLine`、`startColumn`（如果未知则为第 1 列）、`message`（使用目录的 `message` 模板，替换代码中的任何 `{placeholder}`）。
3. 如果规则有先决条件“仅分析从 'lwc' 导入的文件”（lws-008），通过 `scripts/check-lwc-import.sh <file>` 门禁它 — 当存在 `from 'lwc'` 导入时脚本会打印 `lwc-import=yes`，否则打印 `lwc-import=no`。当答案是 `no` 时，跳过该文件。

此目录是标准的检测列表；后面的 JS/TS、HTML 和 `.js-meta.xml` 指示是 SARIF 规则之外的附加检查。

### 第 4 步 — HTML 模板检查（附加）

对每个模板进行以下检查：

- `lwc:inner-html` 使用 — 验证源是受信任的。
- 未转义的表达式传递给 LWS 视为敏感的属性（`href`、`src`、`srcdoc`、内联事件处理程序）。
- 直接 `style="…"` 与绑定表达式 — CSS 类替换的候选者。
- 没有沙箱的嵌入式 `<iframe>` 或 `<object>`（第 3 步通过 lws-023a/lws-023b 捕获 `srcdoc` 和协议情况；此步骤捕获缺少 `sandbox` 属性）。

### 第 5 步 — 元数据和配置检查（附加）

检查 `.js-meta.xml`：

- 组件不需要时，过宽的 API 访问（`lightning__FlowScreen`、`lightning__AppPage` 等）。
- 暴露的公共属性包含敏感数据。
- 目标表面缺少 `capabilities` 限制。

检查 Apex 绑定：

- `@wire` 到没有 `@AuraEnabled(cacheable=true)` 的 Apex 方法，而缓存是安全的。
- 直接命令式调用绕过权限检查。

第 4-5 步的发现使用规则 ID `lws-tpl-001`…`lws-tpl-NNN`（HTML）和 `lws-meta-001`…`lws-meta-NNN`（元数据）— 报告中每个发现的序列号 — 以避免与 SARIF 目录冲突。

### 第 6 步 — 生成报告

根据 Prerequisites 中确认的模式选择输出格式。

#### 审核模式（默认）

使用 [examples/review-report.md](examples/review-report.md) 作为模板 — 在 `## 安全 (LWS + 产品)` 下每个发现一个项目符号，在 `## 摘要` 下一个总计行。

严重性排序：关键 → 高 → 中 → 低（将 SARIF `error` 映射到高，`warning` 映射到中，除非规则另有说明）。引用产生每个发现的参考章节（例如，“产品安全 § lws-001 document.createProcessingInstruction”）。

#### 评分模式

发出单个 SARIF 2.1.0 JSON 文件 — 除此之外什么也不写。之前或之后没有散文。不要将 JSON 写入文件；直接返回。空 `results` 数组表示未发现问题。

使用 [examples/score-report.sarif.json](examples/score-report.sarif.json) 作为形状参考 — 同样的顶层结构（`$schema`、`version`、`runs[0].tool.driver.rules[]`、`runs[0].results[]`），用实际触发的规则和实际匹配项填充。

规则：
- `ruleId` 与目录条目完全匹配（`lws-001`…`lws-023b`，或来自第 4-5 步的 `lws-tpl-*` / `lws-meta-*` 命名空间）。
- `level` 是 `error`，如果目录中的规则标记为 `level: error`，是 `warning`，如果标记为 `level: warning`。没有其他值。
- `message.text` 使用目录的 `message` 模板，并替换占位符（例如，用代码中找到的实际事件名替换 `{eventName}`）。
- 每个匹配项一个 `result`。如果一个规则在文件中触发三次，发出三个结果。
- 仅包含在 `tool.driver.rules` 中触发的规则；即使 `results` 数组为空，也需要 `tool.driver.rules` 存在（使用 `[]`）。

### 第 7 步 — 应用修复（仅审核模式）

评分模式中跳过 — 评分模式是只读的。

对于每个接受的发现：

1. 编辑组件文件（HTML、JS/TS、CSS、meta.xml）以应用修复。
2. 保留现有的正确行为和现有的功能标志门禁。如果门禁已经配置了相同的问题，则保持不变。分阶段发布的新的功能标志门禁不在此技能范围内 — 分别应用它们。
3. 不要无声地删除旧代码 — 保留需要门禁的原始路径。
4. 不要削弱安全态势以使测试通过；如果测试依赖于不安全的模式，请修复测试。

### 第 8 步 — 验证

- **审核模式**：对更新后的文件重新运行第 3 步的目录遍历；每个修复的发现都不应再出现。运行 Jest 测试和任何组件级安全测试。如果修复影响了 Apex 访问模式，请与服务器端审查员确认权限。
- **评分模式**：返回之前，将发出的 SARIF 写入临时文件并运行 `scripts/validate-sarif.sh <path>` — 脚本确认 JSON 解析、`version` 是 `2.1.0`、每个 `ruleId` 匹配目录模式（`lws-NNN[a-z]?` / `lws-tpl-NNN` / `lws-meta-NNN`）并且在 `tool.driver.rules` 中声明、每个 `level` 是 `error` 或 `warning`、每个结果都有 `physicalLocation.artifactLocation.uri` + `region.startLine`。在返回 SARIF 之前修复任何失败。

## 交叉引用

- 相关技能：
  - `experience-lwc-generate` — 用于从开始就符合安全性的新 LWC 包的编写。
  - `design-systems-slds-validate` — SLDS/设计系统合规检查（可访问性与 WCAG 2.2 重叠 — 分别运行）。
  - `dx-code-analyzer-run` — 仓库级静态分析检查；与此技能一起使用以获得 LWS 目录之外的覆盖率。

## 验证

- 每个目录规则（`lws-001`…`lws-023b`）都针对包进行了评估，而不是手工挑选的子集。
- 每个发现要么已应用（审核模式），要么在 SARIF 结果中显示（评分模式），要么带有明确延迟的注释和原因。
- 每个发现都引用了具体的目录规则 ID — 没有自由形式的“看起来可疑”条目。
- 修复没有引入新的 XSS 池、不安全的 URL 流或阻止的 DOM API。
- 评分模式输出是有效的 SARIF 2.1.0 JSON，直接返回，没有周围的散文。
