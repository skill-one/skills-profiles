---
name: automation-sandbox-post-copy-configure
description: 对目标组织应用 Salesforce 沙盒复制后自动化 JSON 配置。对于每个条目，该技能根据条目的 `ConfigurationName` 推导正确的 Tooling API 对象，通过描述探测验证推导结果，通过 SOQL-over-REST 解析记录 ID，然后通过复合 `Metadata` 字段使用 `sf api request rest` 执行 PATCH 操作。当用户要求对沙盒应用、运行、执行、干跑或预览复制后或刷新后配置文件（例如 `post-copy-config.json`）时使用。触发短语："应用复制后配置"、"运行复制后自动化"、"执行沙盒刷新后 JSON"、"应用沙盒刷新配置"、"刷新后配置沙盒"。禁止触发用于从 SOP 生成配置 JSON（委托给 `automation-sandbox-post-copy-config-generate`），或用于部署元数据 XML。
---

# 自动化：沙盒复制后配置

将 Salesforce 沙盒复制后自动化 JSON 配置应用于目标组织。该技能将固定 Tooling API 对象 **和** 记录查找 SOQL 过滤器，用于其校准的两个规范 `ConfigurationName` 值（`OutboundMessages`、`RemoteSiteSettings`）；对于任何其他 `ConfigurationName`，它从条目值中派生候选值，并针对实时组织的描述端点进行验证。每个条目——固定的或派生的——在计划任何 PATCH 之前仍必须通过步骤 B（描述返回 200 并带有 `Metadata` 复合字段）。

## 工具限制

**仅使用 Bash 工具** 执行 `sf` CLI 命令（`sf data query --use-tooling-api`、`sf api request rest`、`sf org display`）。**不要**使用 MCP 工具，如 `execute_soql`——完全忽略它们；该技能所需的复合 `Metadata` PATCH 模式不可通过 MCP 工具包装器获得。如果目标组织别名未由用户明确命名，请调用 `sf` 命令 **不带** `--target-org`——框架已设置 CLI 的默认目标组织。**永远不要传递 `--target-org default`**——`default` 不是别名，并且会因 `NamedOrgNotFoundError` 而失败。

SOQL-over-REST (`sf data query --use-tooling-api ...`) 被视为 API 调用——相同的 OAuth 会话、相同的授权边界，与后续的 PATCH 相同。没有直接数据库 / 非 Salesforce SQL 访问。

## 停止——在执行任何 API 调用之前执行此操作

**永远不要从内存中调用组织**。在第一个请求之前：

1. 从用户提供的确切路径（默认 `./post-copy-config.json`）端到端读取配置 JSON。每个条目必须具有所有五个键（`ConfigurationName`、`Label`、`Fields`、`IsActive`、`ExecutionOrder`）。如果任何条目格式不正确，请中止并显示文件路径 + 条目索引——**不要**部分应用。**不要**编造条目。如果文件丢失，请停止并询问；**永远不要**针对合成标签编造计划。
2. 对于配置中的每个不同的 `ConfigurationName`，在计划任何 PATCH 之前运行派生 + 描述验证步骤（如下所述）。API 无法验证的条目绝不能作为计划的 PATCH 出现——它会在一开始就被拒绝。
3. 除非用户明确提供，否则请向用户确认目标组织别名。该技能会修改实时组织——写入错误组织（例如，将生产别名设置为默认）是最昂贵的失败模式。

如果你宣布“我现在将应用……”而没有读取配置文件并为每个不同的 `ConfigurationName` 运行描述验证，请停止并首先执行这些操作。

---

## 每个条目的程序（该技能的核心）

该技能包含规范类型的固定映射，以及任何其他类型的派生然后验证路径。按照以下步骤**为每个条目**，按顺序执行。`步骤 B`（描述验证）是强制性的，无论映射来自固定表还是派生路径——其 HTTP 状态必须在摘要中显示。

### 步骤 A — 解析 Tooling API 对象和查找过滤器

**固定规范（权威——请使用这些确切值，不要替换不同的对象名称）：**

| ConfigurationName | Tooling API 对象 | 记录查找 SOQL |
|-------------------|---------------------|--------------------|
| `OutboundMessages`   | `WorkflowOutboundMessage` | `SELECT Id, FullName FROM WorkflowOutboundMessage WHERE EntityDefinition.QualifiedApiName = '<Fields.Object>'` — 然后在客户端选择行，其 `FullName == '<Fields.Object>.<Label>'`。SOQL 不能直接过滤此对象上的 `FullName`。 |
| `RemoteSiteSettings` | `RemoteProxy`             | `SELECT Id, SiteName FROM RemoteProxy WHERE SiteName = '<Label>'`. |

对于规范条目，请使用固定的对象和 SOQL，不要“派生”。不要编造 `OutboundMessage`、`RemoteSiteSetting` 或 `MasterLabel` 变体——看起来合理但错误。

字段名解析（覆盖 + 大小写规则 + 存在性检查）由 `scripts/map-metadata-key.mjs` 拥有。

**非规范**：派生候选值（通常是 Metadata API 类型名称的单数形式，有时会添加前缀）；步骤 B 规则会排除错误的猜测。使用步骤 C 中的通用 SOQL 模式。

### 步骤 B — 验证候选值是否存在并支持 Metadata 写入

对于每个候选值，GET 描述：

```bash
sf api request rest \
  "/services/data/v<apiVersion>/tooling/sobjects/<Candidate>/describe/"
```

只有当**两者**都为真时才接受候选值：

- HTTP 200（此组织上的 Tooling API 存在此对象），**并且**
- 描述响应的 `fields` 数组包含一个名为 `Metadata` 的字段（复合字段——这是 PATCH 通过写入的字段）。

如果候选值没有通过这两个门，请将条目标记为 `API_NOT_IDENTIFIED` 并跳过。**不要猜测 REST 路径**——在最好的情况下，错误的路径会返回 404，在最坏的情况下会更新错误的记录。

### 步骤 C — 解析记录 ID（SOQL-over-REST）

**对于固定的规范**：逐字运行步骤 A 表中的 SOQL（替换 `<Label>` / `<Fields.Object>`）。不要替换不同的过滤列，例如 `MasterLabel`——固定的 SOQL 是经过测试和正确的过滤条件。

**对于非规范（派生的）对象**：查询已验证的对象，以获取由条目的 `Label`（如果存在，则 `Fields.Object`）标识的记录：

```bash
# SOQL 到变量 + 分离的 jq 调用——避免此技能中最常见的 shell 引号失败。
SOQL='SELECT Id, FullName FROM <VerifiedSobject> WHERE <UniqueFilter>'
sf data query --use-tooling-api --json --query "$SOQL" \
  > /tmp/entry-<Slug>-lookup.json
ID=$(jq -r '.result.records[0].Id // empty' /tmp/entry-<Slug>-lookup.json)
```

根据步骤 B 描述响应中显示的可查询字段选择 `<UniqueFilter>`。如果行包含 `FullName` 字段，SOQL 通常会拒绝直接 `FullName = ...` 过滤——通过描述中显示的直接列过滤（例如 `EntityDefinition.QualifiedApiName`、`DeveloperName`、`SiteName`），并在客户端应用 `FullName` 匹配（`jq -r '.result.records[] | select(.FullName == "<Object>.<Label>") | .Id'`）。

结果：

- 零行 → `NOT_FOUND`（永远不会回退到插入）。
- 多行（客户端过滤后）→ `AMBIGUOUS`（在摘要中显示所有 ID 并跳过；错误的 ID 比没有 ID 更糟）。
- 恰好一行 → 继续步骤 D。

### 步骤 D — GET 当前 Metadata，变异，PATCH 回去

`Metadata` 是**完全替换**——省略的键在 PATCH 时会被清空。保留来自步骤 D-1 GET 的每个现有键；仅覆盖变异数据。摘要中的“计划 PATCH 正文”（应用和干运行）是此完整的合并对象——冗长或组织特定的值可能会渲染为 `"<preserved-from-GET>"` 占位符字符串，但每个键都必须存在。

每个步骤 D 文件名必须包含步骤 C 中的记录 `<Id>`（例如 `/tmp/entry-<Id>-meta.json`）——并行阶段条目共享工作目录，并且会覆盖共享名称。

1. **GET** 当前 `Metadata` → `/tmp/entry-<Id>-meta.json`。
2. **解析变异键**——对于每个 `Fields.<Xxx>`，运行 `node scripts/map-metadata-key.mjs "<ConfigurationName>" "<ConfigFieldName>" /tmp/entry-<Id>-meta.json`。在 `{"status":"OK","key":...}` 上使用返回的键。在 `{"status":"FIELD_MAP_UNKNOWN",...}` 上标记条目并跳过。
3. **PATCH** — heredoc 构建(`/tmp/entry-<Id>-mutation.json`)，使用 `jq --slurpfile m /tmp/entry-<Id>-mutation.json '. + $m[0] | {Metadata: .}' /tmp/entry-<Id>-meta.json > /tmp/entry-<Id>-patch.json`（保留 JSON 类型），使用 `-b @/tmp/entry-<Id>-patch.json` PATCH，捕获响应正文到 `/tmp/entry-<Id>-response.json`。完整的 bash 在 `references/api_endpoints.md` §Step D 中。**永远不要使用 `--arg**`（将布尔值/数字转换为字符串，在特殊字符上会中断）。将 PATCH 包裹在 `for attempt in 1 2; do <cmd> && break; done`——在 shell/jq 引号失败时重试一次（HTTP 调用发出之前的非零退出）。
4. **分类** — `node scripts/classify-patch-result.mjs "<httpCode>" /tmp/entry-<Id>-response.json`。退出 0 → `SUCCESS`；退出 2 → `FAILED`（解析错误在 stdout 上）。204 且正文非空是 `FAILED`。

### 步骤 E — 验证更改是否生效

重新读取记录以确认 PATCH 是否生效：

- 如果变异字段是对象上的直接可查询 SOQL 列（很少——大多数可写入的 `Metadata` 字段不是），只需通过 ID 选择即可。
- 否则，GET 记录并检查 `.Metadata` 中的相应键。

如果读取回的值与请求的值不匹配，记录 `FAILED_VERIFY`——PATCH 返回 204，但效果不可见（通常是命名或权限问题）。

---

## IsActive 语义

- `IsActive: true`  → 按照步骤 A–E 应用 PATCH。
- `IsActive: false` → **不要**PATCH。为条目记录 `SKIPPED_INACTIVE`，并在摘要文件的“后续操作”下添加一个项目，列出条目的 `ConfigurationName` + `Label`，以便客户注意到目标组织上未处理的配置声明为不活动的记录。

理由：`IsActive: false` 意味着“在此沙盒中不活动”，而不是“停用现有记录”。静默停用实时集成比保留它的影响更大。

---

## 规范输出形状（始终发出此内容）

写入到 `./post-copy-<mode>-summary.md`（模式是 `dry-run` 或 `apply`）的单个 Markdown 摘要，并打印给用户。没有 JSON 侧文件（`plan/phases.json`、`requests/*.request.json` 等）——在 Markdown 中内联每个计划的/实际的请求。

**阶段枚举由脚本拥有**。运行 `node scripts/plan-phases.mjs <config.json>` 并消费其 `phases[]` 输出。每个条目都带有 `ordinal`（1 索引阶段编号）和 `executionOrder`（原始值，用于 `(ExecutionOrder = <raw>)` 标题注释）。稀疏值折叠（`1, 2, 5` → 索引 `1, 2, 3`）。`IsActive:false` 条目预先标记为 `SKIP_INACTIVE`。见 `references/execution_phasing.md` 工作示例。

对于干运行条目，`HTTP` 列是 `—`（短划线）。摘要以：`未发出任何 PATCH 请求。要应用，请重新运行而不带干运行标志。`

**目标组织解析由脚本拥有**。运行 `node scripts/resolve-target-org.mjs`；将返回的 `.alias` 替换到标题中。**永远不要**内联 `<env:SF_TARGET_ORG>` 或 `$SF_TARGET_ORG`。

```markdown
# Post-Copy Configure Run — <N> 条目 <planned|applied> 对 `<alias>`

配置文件: `<path>`
目标组织: `<alias>`
模式: <dry-run|apply>

## Phase <ExecutionOrder> — <count> entr(y|ies)

计划请求:
- 方法: `PATCH`
- 路径: `/services/data/v<apiVersion>/tooling/sobjects/<VerifiedSobject>/<Id>`
- 正文: `<JSON — 完整合并的 Metadata 对象：来自步骤 D-1 GET 的每个现有键，覆盖来自配置的变异键。冗长或组织特定的值可能会作为 "<preserved-from-GET>" 占位符字符串出现，但每个键都必须存在。永远不要发出仅包含变异键的最小正文。>`

| ConfigurationName | Label | Object | Sobject | Describe | Outcome | HTTP |
|-------------------|-------|--------|---------|----------|---------|------|
| <name>            | <lbl> | <obj>  | <VerifiedSobject> | <200 或 404> | <outcome> | <code> |

## Totals

| Outcome | Count |
|---------|-------|
| <state> | <n>   |

## Follow-ups

- <每个 SKIPPED_INACTIVE / API_NOT_IDENTIFIED / AMBIGUOUS / FIELD_MAP_UNKNOWN / NOT_FOUND 条目的项目>

```

列语义：`Object` = 如果存在，则为条目的 `Fields.Object`，否则为 `—`。`Sobject` = 步骤 A 解析的对象。`Describe` = 步骤 B 描述 HTTP 状态（`200` 为已验证，`404` 为 `API_NOT_IDENTIFIED`）——强制性的，以便在概览中一目了然地看到跳过的步骤 B。结果词汇：`SUCCESS`、`NOT_FOUND`、`AMBIGUOUS`、`API_NOT_IDENTIFIED`、`FIELD_MAP_UNKNOWN`、`FAILED`、`FAILED_VERIFY`、`SKIPPED_INACTIVE`、`SKIPPED`、`DRY_RUN`、`DELETE_NOT_SUPPORTED`、`NOT_ATTEMPTED`。

**脚本是内部的**。`plan-phases.mjs`、`map-metadata-key.mjs`、`classify-patch-result.mjs`、`resolve-target-org.mjs` 调用是实现细节——**不要**将它们的原始 stdout、JSON 输出或“我运行了 node …”的叙述内联到摘要 Markdown 或打印的响应中。消费 JSON，使用返回的值，并按照上述形状渲染摘要。

## 范围

- **在范围内**：读取复制后配置 JSON（由 `automation-sandbox-post-copy-config-generate` 产生）、将条目分组到 `ExecutionOrder` 阶段、为每个条目派生+验证 Tooling API 对象、通过 SOQL-over-REST 解析 ID、通过复合 `Metadata` PATCH、报告每个条目结果。
- **超出范围**：从 SOP 生成配置 JSON（委托给 `automation-sandbox-post-copy-config-generate`）、部署元数据 XML、运行异步任务框架（ATF）编排器本身（那是平台端的 Java 实现）、为描述探测失败的 `ConfigurationName` 值编造 API 路径（显示为 `API_NOT_IDENTIFIED` 并停止）。

每个 API 调用都是针对实时组织的。将此技能视为变异工具：首先使用 `--dry-run`，确认目标组织别名，并且永远不要对不同的端点静默重试失败的条目。

3. **计划阶段** — 运行 `node scripts/plan-phases.mjs <config.json>` 并迭代其 `phases[]` 输出。参见 `references/execution_phasing.md` 了解并发限制。

4. **每个条目的描述-验证步骤** — 对于每个不同的 `ConfigurationName`，运行步骤 A + 步骤 B 一次并缓存验证后的 sobject。任何失败的 `ConfigurationName` 步骤 B 都会将该名称的所有条目标记为 `API_NOT_IDENTIFIED`。

5. **每个条目的应用步骤** — 对于每个阶段内的每个条目：
   - 由计划阶段预标记为 `SKIP_INACTIVE` 的条目 → 记录 `SKIPPED_INACTIVE`，添加一个后续事项点，继续。
   - 否则运行步骤 C（解析 Id），然后步骤 D（GET+修改+PATCH），然后步骤 E（验证）。如果 `--dry-run` 为真，仍然运行步骤 C 和 D-1/D-2，以便打印的计划反映真实的合并有效负载 — 仅跳过 D-3（PATCH）和步骤 E，然后记录 `DRY_RUN`。

6. **阶段之间** — 在开始下一阶段之前，等待当前阶段中的每个条目完成。

7. **将摘要文件写入磁盘** — 最终交付物是一个位于 `./post-copy-<mode>-summary.md` 的 Markdown 文件，遵循“规范输出形状”部分中的形状。同时将其打印给用户。永远不要写入访问令牌或完整的 `sf org display` 输出。如果 URL 包含嵌入的凭证，请在摘要中遮盖它们（`https://user:***@host/...`）；实际的 PATCH 正文包含原始 URL。

---

## 规则和注意事项

承重不变量（永不插入；对每个 `ConfigurationName` 进行描述门控；复合 `Metadata` PATCH 保留完整现有块；`IsActive: false` → `SKIPPED_INACTIVE`；永不打印原始访问令牌；阶段内并发限制为 5）以及每个运行时失败的规范响应（运行中 401、429、带凭证的 URL、`Fields.Action = "Delete"`、描述 404、零/多个 SOQL 行）都位于 `references/rules_gotchas.md`。在偏离 A-E 步骤程序之前，请先阅读该文件。

---

## 跨技能集成

| 需要 | 委托给 |
|------|-------------|
| 将客户 SOP 转换为该技能消耗的 JSON 配置 | `automation-sandbox-post-copy-config-generate` |
| 部署 Salesforce 元数据 XML（自定义标签、命名凭证等），这些凭证存在于复合-Metadata 工具 API 模式之外 | 匹配的 `generating-*` 技能 + 一个元数据部署流程 |
| 创建目标组织中尚不存在的记录 | `platform-metadata-deploy` 在生成元数据 XML 之后 |
| 指派运行 API 调用所需的权限集 | `dx-org-permission-set-assign` |

---

## 参考文件索引

| 文件 | 何时阅读 |
|------|-------------|
| `references/api_endpoints.md` | 步骤 A–E — 带有工作示例（OBM、RSS）的完整通用配方和 camelCase-字段约定 |
| `references/execution_phasing.md` | 步骤 3（工作流） — 分组规则和阶段内并发限制。`scripts/plan-phases.mjs` 是阶段枚举的可执行事实来源；该文件解释了其背后的模型 |
| `scripts/plan-phases.mjs` | 步骤 3（工作流） — 确定性阶段规划器（调用，然后读取其输出） |
| `scripts/map-metadata-key.mjs` | 步骤 D-2 — 确定性 Metadata-key 解析器（覆盖表 + 案例规则 + 存在性检查） |
| `scripts/classify-patch-result.mjs` | 步骤 D-4 — 确定性 HTTP 结果分类器（SUCCESS vs FAILED） |
| `scripts/resolve-target-org.mjs` | 规范输出形状 — 确定性目标组织别名解析器 |
| `references/authentication.md` | 步骤 2（工作流） — 会话检查配方以及如何处理运行中 401 |
| `references/rules_gotchas.md` | 在偏离 A-E 步骤之前 — 承重不变量和规范运行时失败响应 |
| `assets/api_request_templates.json` | 步骤 A–E — 描述 / 查找 / GET+PATCH 的通用模板，带占位符键 |
| `examples/sample_config_input.json` | 步骤 1（工作流） — 该技能消耗的配置 JSON 的形状 |
| `examples/sample_execution_summary.md` | 步骤 7（工作流） — 显示给用户的摘要报告的形状 |
