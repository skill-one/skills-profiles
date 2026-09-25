# 自动化：沙盒复制后配置

将 Salesforce 沙盒复制后自动化 JSON 配置应用于目标组织。三个标准的 `ConfigurationName` 值被固定：
`OutboundMessages` 和 `RemoteSiteSettings` 采用复合 `Metadata` PATCH 路径（步骤 A–E）；`ScheduledApex` 采用匿名 Apex 路径（步骤 F），因为 `CronTrigger` 在 Tooling API 中是只读的。任何其他 `ConfigurationName` 都会被派生并描述验证。每个 A–E 条目——固定的或派生的——在计划任何 PATCH 之前都必须通过步骤 B（描述返回 200 并带有 `Metadata` 复合字段）；步骤 B 不适用于 `ScheduledApex`。API 无法验证的条目会在摘要中显示并被跳过——绝不猜测。

## 工具限制

**仅使用 Bash 工具**来执行 `sf` CLI 命令（`sf data query --use-tooling-api`，`sf api request rest`，`sf org display`）。**不要**使用 MCP 工具，如 `execute_soql`——完全忽略它们；这个技能所需的复合 `Metadata` PATCH 模式无法通过 MCP 工具包装器提供。如果目标组织别名没有由用户明确命名，请调用 `sf` 命令**不带** `--target-org`——框架已经设置了 CLI 的默认目标组织。**永远不要传递** `--target-org default`——`default` 不是别名，并且会因 `NamedOrgNotFoundError` 而失败。

SOQL-over-REST (`sf data query --use-tooling-api ...`) 被视为 API 调用——与后续的 PATCH 具有相同的 OAuth 会话和相同的授权边界。没有直接的数据库/非 Salesforce SQL 访问。

## 停止——在执行任何 API 调用之前执行此操作

从内存中**永不**调用该组织。在第一个请求之前：

1. 从用户给定的确切路径（默认 `./post-copy-config.json`）端到端读取配置 JSON。每个条目必须具有所有五个键（`ConfigurationName`，`Label`，`Fields`，`IsActive`，`ExecutionOrder`）。如果任何条目格式不正确，请中止并显示文件路径 + 条目索引——**不要**部分应用。**不要**编造条目。如果文件丢失，请停止并询问；**永远不要**针对合成标签编造计划。
2. 对于配置中的每个不同的 `ConfigurationName`，在计划任何 PATCH 之前运行派生 + 描述验证步骤（如下所述）。API 无法验证的条目**绝不能**作为计划的 PATCH 出现——它从一开始就被拒绝。
3. 与用户确认目标组织别名，除非他们明确提供了。这个技能会修改一个活动的组织——将内容写入错误的组织（例如，将生产别名设置为默认值）是最昂贵的失败模式。

如果你宣布“我现在将应用……”而没有读取配置文件并为每个不同的 `ConfigurationName` 运行描述验证，请停止并首先执行这些操作。

---

## 每个条目程序（这个技能的核心）

该技能包含固定映射，用于下述标准类型，并为任何其他内容提供派生然后验证的路径。按照以下步骤**为每个条目**，按顺序执行。`Step B`（描述验证）是强制性的，无论映射来自固定表还是派生路径——其 HTTP 状态必须在摘要中显示。

### 步骤 A — 解析 Tooling API sobject 和查找过滤器

**固定标准（权威——请使用这些确切值，**不要**替换不同的 sobject 名称）：**

| ConfigurationName | Tooling API sobject | 记录查找 SOQL |
|-------------------|---------------------|--------------------|
| `OutboundMessages`   | `WorkflowOutboundMessage` | `SELECT Id, FullName FROM WorkflowOutboundMessage WHERE EntityDefinition.QualifiedApiName = '<Fields.Object>'` — 然后在客户端选择行，其 `FullName == '<Fields.Object>.<Label>'`。SOQL 不能直接对这个 sobject 按照过滤 `FullName`。 |
| `RemoteSiteSettings` | `RemoteProxy`             | `SELECT Id, SiteName FROM RemoteProxy WHERE SiteName = '<Label>'`. |
| `ScheduledApex`      | `CronTrigger` (只读——匿名 Apex 路径，见步骤 F) | 见步骤 F — 预飞行 `SELECT Id FROM CronTrigger WHERE CronJobDetail.Name = '<escaped>'` 门。 |

对于标准条目，使用固定的 sobject 和 SOQL，保持不变；跳过“派生”。**不要**编造 `OutboundMessage`，`RemoteSiteSetting` 或 `MasterLabel` 变体——看起来合理但错误。

字段名解析（覆盖 + 大小写规则 + 存在性检查）由 `scripts/map-metadata-key.mjs` 拥有。

**非标准**：派生一个候选者（通常是 Metadata API 类型名的单数形式，有时会加前缀）；步骤 B 规则会排除错误的猜测。使用步骤 C 中的通用 SOQL 模式。

### 步骤 B — 验证候选者是否存在并支持 Metadata 写入

对于每个候选者，GET 描述：

```bash
sf api request rest \
  "/services/data/v<apiVersion>/tooling/sobjects/<Candidate>/describe/"
```

只有当**两者**都为真时才接受候选者：

- HTTP 200（该 sobject 存在于此组织的 Tooling API 上），**并且**
- 描述响应的 `fields` 数组包含一个名为 `Metadata` 的字段（复合字段——这是 PATCH 通过写入的内容）。

如果没有任何候选者通过这两个门，请将条目标记为 `API_NOT_IDENTIFIED` 并跳过。**不要**猜测 REST 路径——在最好的情况下，错误的路径会 404，在最坏的情况下会更新错误的记录。

### 步骤 C — 解析记录 Id（SOQL-over-REST）

**对于固定标准**：逐字运行步骤 A 表中的 SOQL（替换 `<Label>` / `<Fields.Object>`）。**不要**替换不同的过滤列，例如 `MasterLabel`——固定的 SOQL 是经过测试和正确的过滤条件。

**对于非标准（派生）sobjects**：查询已验证的 sobject，以获取由条目的 `Label`（当存在时 `Fields.Object`）标识的记录：

```bash
# SOQL 到变量 + 独立的 jq 调用——避免这个技能中最常见的 shell 引号失败。
SOQL='SELECT Id, FullName FROM <VerifiedSobject> WHERE <UniqueFilter>'
sf data query --use-tooling-api --json --query "$SOQL" \
  > /tmp/entry-<Slug>-lookup.json
ID=$(jq -r '.result.records[0].Id // empty' /tmp/entry-<Slug>-lookup.json)
```

根据步骤 B 描述响应中显示的可查询字段选择 `<UniqueFilter>`。如果该行包含 `FullName` 字段，SOQL 通常会拒绝直接 `FullName = ...` 过滤——通过直接列过滤（例如 `EntityDefinition.QualifiedApiName`，`DeveloperName`，`SiteName`）并应用客户端 `FullName` 匹配（`jq -r '.result.records[] | select(.FullName == "<Object>.<Label>") | .Id'`）。

结果：

- 零行 → `NOT_FOUND`（永远不会回退到插入）。
- 多行（在客户端过滤后）→ `AMBIGUOUS`（在摘要中显示所有 Id 并跳过；错误的 Id 比没有 Id 更糟）。
- 恰好一行 → 继续步骤 D。

### 步骤 D — GET 当前 Metadata，变异，PATCH 回去

`Metadata` 是**完全替换**——省略的键在 PATCH 上会被清空。保留步骤 D-1 GET 的每个现有键；仅覆盖配置中变异的键。摘要中的“计划的 PATCH 正文”（应用和干运行）是此完整的合并对象——冗长或组织特定的值可能会渲染为 `"<preserved-from-GET>"` 占位符字符串，但每个键都必须存在。每个步骤 D 文件名必须包含步骤 C 中的记录 `<Id>`（例如 `/tmp/entry-<Id>-meta.json`）——并行阶段共享工作目录，并且会覆盖共享名称。

1. **GET** 当前 `Metadata` → `/tmp/entry-<Id>-meta.json`。
2. **解析变异键** — 对于每个 `Fields.<Xxx>`，运行 `node scripts/map-metadata-key.mjs "<ConfigurationName>" "<ConfigFieldName>" /tmp/entry-<Id>-meta.json`。在 `{"status":"OK","key":...}` 上使用返回的键。在 `{"status":"FIELD_MAP_UNKNOWN",...}` 上标记条目并跳过。
3. **PATCH** — heredoc 构建 `/tmp/entry-<Id>-mutation.json`，使用 `jq --slurpfile m /tmp/entry-<Id>-mutation.json '. + $m[0] | {Metadata: .}' /tmp/entry-<Id>-meta.json > /tmp/entry-<Id>-patch.json`（保留 JSON 类型），使用 `-b @/tmp/entry-<Id>-patch.json` PATCH，捕获响应正文到 `/tmp/entry-<Id>-response.json`。完整的 bash 在 `references/api_endpoints.md` §Step D 中。**永远不要使用** `--arg`（将布尔/数字字符串化，在特殊字符上会中断）。将 PATCH 包裹在 `for attempt in 1 2; do <cmd> && break; done` 中——在 shell/jq 引号失败时（HTTP 调用发出之前的非零退出）重试一次。
4. **分类** — `node scripts/classify-patch-result.mjs "<httpCode>" /tmp/entry-<Id>-response.json`。退出 0 → `SUCCESS`；退出 2 → `FAILED`（解析错误在 stdout 上）。204 且正文非空是 `FAILED`。

### 步骤 E — 验证更改是否生效

重新读取记录以确认 PATCH 是否生效：

- 如果变异字段是 sobject 上的直接查询 SOQL 列（很少——大多数可写入 `Metadata` 的字段不是），只需通过 Id 选择就足够了。
- 否则，GET 记录并检查 `.Metadata` 内的相应键。

如果读取回的值与请求的值不匹配，记录 `FAILED_VERIFY`——PATCH 返回 204 但效果不可见（通常是命名或权限问题）。

### 步骤 F — 定时 Apex（匿名 Apex 路径）

`ScheduledApex` 条目针对只读的 `CronTrigger` sobject——步骤 A–E 不适用。**在执行之前阅读 `references/scheduled_apex_path.md`**——它拥有完整的 F-1 → F-4 配方（预飞行 AMBIGUOUS 门，片段构建，`sf apex run`，验证，干运行）。

---

## IsActive 语义

- `IsActive: true`  → 按照步骤 A–E 应用 PATCH。
- `IsActive: false` → **不要**PATCH。为条目记录 `SKIPPED_INACTIVE`，并在摘要文件的“Follow-ups”下添加一个点，列出条目的 `ConfigurationName` + `Label`，以便客户注意到配置声明的非活动记录在目标组织中未被更改。

理由：`IsActive: false` 意味着“在此沙盒中不活动”，而不是“停用现有记录”。无声地停用活动集成比保留它更具更大的影响范围。

---

## 标准输出形状（始终发出此内容）

写入到 `./post-copy-<mode>-summary.md` 的单个 Markdown 摘要（模式是 `dry-run` 或 `apply`）。打印给用户。不生成 JSON 侧文件（`plan/phases.json`，`requests/*.request.json` 等）——在 Markdown 中内联每个计划的/实际的请求。

**阶段枚举由脚本拥有。** 运行 `node scripts/plan-phases.mjs <config.json>` 并逐字消费其 `phases[]` — 每个条目都携带 `ordinal`（1 索引用于标题）和 `executionOrder`（原始，用于 `(ExecutionOrder = <raw>)`）；稀疏值会折叠；`IsActive:false` 条目预先标记为 `SKIP_INACTIVE`。见 `references/execution_phasing.md` 了解工作示例。

**目标组织解析由脚本拥有。** 运行 `node scripts/resolve-target-org.mjs`；将返回的 `.alias` 替换到标题中。**永远不要**逐字发出 `<env:SF_TARGET_ORG>` 或 `$SF_TARGET_ORG`。

对于干运行条目，`HTTP` 列是 `—`。摘要结束于：
`未发出任何 PATCH 请求。要应用，请重新运行而不带干运行标志。`

```markdown
# Post-Copy Configure Run — <N> 条目 <planned|applied> 对 `<alias>`
针对 `<alias>`

配置文件: `<path>`
目标组织: `<alias>`
模式: <dry-run|apply>

## 阶段 <ExecutionOrder> — <count> 条目(y|ies)

计划请求:
- 方法: `PATCH`
- 路径: `/services/data/v<apiVersion>/tooling/sobjects/<VerifiedSobject>/<Id>`
- 正文: `<JSON — 完整合并的 Metadata 对象：来自步骤 D-1 GET 的每个现有键，覆盖配置中变异的键。冗长或组织特定的值可能会渲染为 "<preserved-from-GET>" 占位符字符串，但每个键都必须存在。永远不要发出仅包含变异键的最小正文。>`

| ConfigurationName | Label | Object | Sobject | 描述 | 结果 | HTTP |
|-------------------|-------|--------|---------|----------|---------|------|
| <name>            | <lbl> | <obj>  | <VerifiedSobject> | <200 或 404> | <outcome> | <code> |

## 总计

| 结果 | 计数 |
|---------|-------|
| <state> | <n>   |

## Follow-ups

- <每个 SKIPPED_INACTIVE / API_NOT_IDENTIFIED / AMBIGUOUS / FIELD_MAP_UNKNOWN / NOT_FOUND 条目的点>

```

列语义：`Object` = 如果存在，则为条目的 `Fields.Object`，否则为 `—`。`Sobject` = 步骤 A 解析的 sobject。`Describe` = 步骤 B 描述 HTTP 状态（`200` 表示已验证，`404` 表示 `API_NOT_IDENTIFIED`）——强制性的，以便可以一目了然地看到跳过的 Step Bs。结果词汇：`SUCCESS`，`NOT_FOUND`，`AMBIGUOUS`，`API_NOT_IDENTIFIED`，`FIELD_MAP_UNKNOWN`，`FAILED`，`FAILED_VERIFY`，`SKIPPED_INACTIVE`，`SKIPPED`，`DRY_RUN`，`DELETE_NOT_SUPPORTED`，`NOT_ATTEMPTED`。

**脚本是内部的。** **不要**将原始 `node scripts/…` stdout 或“我运行了 node …”的叙述内联到摘要或打印的响应中——消费 JSON，使用返回的值，渲染上述确切形状。

## 范围

- **在范围内**：读取沙盒后配置 JSON（由 `automation-sandbox-post-copy-config-generate` 产生的形状），将条目分组到 `ExecutionOrder` 阶段，为每个条目派生并验证 Tooling API sobject，通过 SOQL-over-REST 解析 Id，通过复合 `Metadata` PATCH，以及报告每个条目的结果。
- **超出范围**：从 SOP 生成配置 JSON（委托给 `automation-sandbox-post-copy-config-generate`）；部署元数据 XML；运行异步任务框架（ATF）协调器本身（那是平台端的 Java 实现）；为 `ConfigurationName` 值编造 API 路径，其描述探测失败（作为 `API_NOT_IDENTIFIED` 并停止）。

每个 API 调用都是针对活动组织的。将此技能视为一个变异工具：首先使用 `--dry-run`，确认目标组织别名，并且永远不要对不同的端点无声重试失败的条目。

---

## 必需输入

在应用之前收集或推断：

- **配置文件路径**：由 `automation-sandbox-post-copy-config-generate` 产生的 JSON 的路径（默认：当前目录中的 `./post-copy-config.json`）。如果文件不存在，请停止并询问。
- **目标组织别名/用户名**：目标沙盒的 `sf` CLI 别名或用户名。**永远不要**假设默认组织——始终确认。如果用户没有提供，请使用 `sf org list --json` 列出可用组织并询问要使用哪个。
- **干运行标志**（可选，默认 `false`）：**读取 ALLOWED，写入 FORBIDDEN**——不是“没有网络调用”。仍然运行每个读取（Step B 描述 `GET`，Step C SOQL，Step D-1 记录 `GET`）；计划的 PATCH 正文仅针对真实的 Metadata 块准确。唯一跳过的调用是 Step D-3（`PATCH`）和 Step E（验证）。**永远不要**编造当前 Metadata 或编造键。在读取失败（401，404，`NamedOrgNotFoundError`）时，显示并停止——**永远不要**回退到从内存中的计划。在第一次通过时优先使用干运行。
- **错误继续**（可选，默认 `true`）：true = 失败的条目不会中止阶段（在摘要中报告失败）；false = 中途中止。

如果用户提供清晰的配置路径和目标别名，请无需进一步提问即可继续。

---

## 工作流程

每个步骤都通过 Bash 执行真实的 `sf` CLI 命令。**不要**在未运行命令的情况下叙述计划——这个技能会修改目标组织。

1. **读取和验证配置 JSON** — 使用读取工具加载文件。每个条目必须是一个具有五个顶层键（`ConfigurationName`，`Label`，`Fields`，`IsActive`，`ExecutionOrder`）的 JSON 对象。格式不正确的条目会中止。

2. **解析目标组织和 API 版本** — 运行 `sf org display --json`。解析 JSON 以确认别名解析有效并捕获 `result.apiVersion`（例如 `62.0`）。**不要**打印原始 JSON——它包含访问令牌。

3. **计划阶段** — 运行 `node scripts/plan-phases.mjs <config.json>` 并迭代其 `phases[]` 输出。见 `references/execution_phasing.md` 了解并发限制。

4. **每个条目描述验证通过** — 对于每个不等于 `ScheduledApex` 的不同 `ConfigurationName`，运行一次 Step A + Step B 并缓存已验证的 sobject。任何 `ConfigurationName` 通过 Step B 失败的条目将标记所有具有该名称的条目为 `API_NOT_IDENTIFIED`。`ScheduledApex` 跳过描述验证——它使用匿名 Apex 路径（Step F），而不是复合 `Metadata` PATCH。

5. **每个条目应用通过** — 对于每个阶段内的每个条目：
   - `SKIP_INACTIVE` 由计划-phases 预标记 → 记录 `SKIPPED_INACTIVE`，添加 Follow-ups 点，继续。
   - `ScheduledApex` → Step F（F-1 预飞行，F-2 构建，F-3 运行，F-4 验证）。干运行：运行 F-1 + F-2 仅；记录 `DRY_RUN`。
   - 所有其他 → Step C（Id），Step D（GET+变异+PATCH），Step E（验证）。干运行：运行 C + D-1/D-2（因此打印的计划反映真实的合并正文）；跳过 D-3 和 E；记录 `DRY_RUN`。

6. **阶段之间** — 在开始下一个阶段之前，等待当前阶段中的每个条目完成。

7. **将摘要文件写入磁盘** — 最终交付品是位于 `./post-copy-<mode>-summary.md` 的 Markdown 文件，遵循“标准输出形状”部分中的形状。也打印给用户。**永远不要**写入访问令牌或完整的 `sf org display` 输出。如果 URL 包含嵌入的凭据，请在摘要中遮盖它们（`https://user:***@host/...`）；实际的 PATCH 正文携带逐字 URL。

---

## 规则和注意事项

承重不变量（永不插入；每个 `ConfigurationName` 都必须描述验证；复合 `Metadata` PATCH 保留完整的现有块；`IsActive: false` → `SKIPPED_INACTIVE`；永远不要打印原始访问令牌；阶段内并发限制为 5）以及每个运行时失败的标凈响应（运行中 401，429，携带凭据的 URL，`Fields.Action = "Delete"`，描述 404，零/多行 SOQL）都保存在 `references/rules_gotchas.md`。在偏离步骤 A–E 程序之前阅读该文件。

---

## 跨技能集成

| 需要 | 委托给 |
|------|-------------|
| 将客户 SOP 转换为该技能消耗的 JSON 配置 | `automation-sandbox-post-copy-config-generate` |
| 在复合-Metadata Tooling 模式之外部署元数据 XML | 匹配的 `generating-*` 技能 + 元数据部署流程 |
| 创建目标组织中尚不存在的记录 | `platform-metadata-deploy` |
| 指派 API 调用所需的权限集 | `dx-org-permission-set-assign` |

---

## 参考文件索引

| 文件 | 何时阅读 |
|------|-------------|
| `references/api_endpoints.md` | 步骤 A–E — 具有工作示例的通用配方，OBM / RSS，以及 camelCase-字段约定 |
| `references/scheduled_apex_path.md` | 步骤 F — `ScheduledApex` 条目的匿名 Apex 路径 |
| `references/execution_phasing.md` | 步骤 3 (工作流程) — `scripts/plan-phases.mjs` 背后的阶段分组模型 |
| `references/authentication.md` | 步骤 2 — 会话检查 + 如何处理运行中 401 |
| `references/rules_gotchas.md` | 在偏离步骤 A–E 之前——不变量和运行时失败响应 |
| `scripts/plan-phases.mjs` | 步骤 3 — 确定性阶段规划器 |
| `scripts/map-metadata-key.mjs` | 步骤 D-2 — 确定性 Metadata-键解析器 |
| `scripts/classify-patch-result.mjs` | 步骤 D-4 — 确定性 HTTP-结果分类器 |
| `scripts/resolve-target-org.mjs` | 标准输出形状 — 目标组织别名解析器 |
| `scripts/build-scheduled-apex.mjs` | 步骤 F-2 — 匿名 Apex 片段构建器 |
| `scripts/soql-escape-job-name.mjs` | 步骤 F-1/F-4 — SOQL-逃避 `JobName` |
| `assets/api_request_templates.json` | 步骤 A–E — 通用描述 / 查找 / GET+PATCH 模板 |
| `assets/scheduled_apex_template.apex` | 步骤 F-2 — 带有 `{{JOB_NAME}}` / `{{CRON_EXPRESSION}}` / `{{APEX_CLASS_NAME}}` 占位符的匿名 Apex 模板 |
| `examples/sample_config_input.json` | 步骤 1 — 该技能消耗的配置 JSON 的形状 |
| `examples/sample_scheduled_apex_config.json` | 步骤 1 — `ScheduledApex` 配置条目的形状 |
| `examples/sample_execution_summary.md` | 步骤 7 — 显示给用户的摘要报告的形状 |
