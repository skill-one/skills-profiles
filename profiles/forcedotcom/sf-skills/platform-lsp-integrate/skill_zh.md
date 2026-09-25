# 使用 Salesforce LSP

`salesforce-development` 插件托管了一个名为 **`salesforce-lsp`** 的本地 MCP 服务器，该服务器懒加载 Salesforce 语言服务器子进程，并将它们的语义能力作为 MCP 工具公开。这项技能是其他技能调用这些工具时遵循的 **合同**，也是“如何使用 Salesforce LSP？”的答案——每个工具的作用是什么，如何读取其结果，每个错误代码的含义，以及当主机缺失时如何回退。

这是一个文档/参考技能。它不编写或部署代码；它告诉您（和其他技能）如何正确驱动 LSP 工具。

> **此插件构建仅支持 Apex + SOQL。** `salesforce-lsp` 主机提供了 Apex 语言服务器（`@salesforce/apex-ls`）和 SOQL 语言服务器。**LWC** 语言服务器有意 **不** 随此插件捆绑——`lwc.*` 工具由主机注册，但在这里始终返回 `unavailable` 类型的信封。将任何 `lwc.*` 调用视为不可用，并使用回退（读取组件源 / 部署编译）。

## 何时使用此技能

- 用户询问如何使用 Salesforce LSP，或哪些 LSP/MCP 工具可用。
- 用户询问特定工具的作用（`apex.diagnostics`、`validate_soql`、`complete_soql` 等）或如何读取其输出。
- LSP 工具返回了错误信封（`lsp_disabled`、`spawn_timeout`、`circuit_open`、`no_apex_workspace`、`no_org_connected`），您需要知道其含义以及如何恢复。
- 您正在编写或审查另一个调用 LSP 工具的技能，需要规范调用/回退模式。
- LSP 似乎出错了，您需要调试它（`lsp.health`、`${CLAUDE_PLUGIN_ROOT}/bin/lsp-doctor`、关闭开关）。

## 工具

所有工具都由 MCP 服务器 **`salesforce-lsp`** 提供（调用名称遵循插件前缀模式：`mcp__plugin_salesforce-development_salesforce-lsp__<tool_name>`，其中工具名称中的点转换为下划线——例如 `apex.diagnostics` 变为 `mcp__plugin_salesforce-development_salesforce-lsp__apex_diagnostics`）。懒加载：需要语言服务器的工具在第一次调用时启动子进程（Apex 的冷启动只需几秒钟），然后重用它。纯静态分析工具从不启动任何东西。

### Apex（启动 Apex LSP）

| 工具 | 目的 | 关键输入 | 关键输出 |
|---|---|---|---|
| `apex.diagnostics` | 编译检查 `.cls`/`.trigger`；暴露错误/警告 | `{ filePath }` | `{ ok, diagnostics: [{ line, column, severity, message }] }` |
| `apex.hover` | 位置处的类型/签名 | `{ filePath, line, character }` | hover markdown |
| `apex.documentSymbol` | 文件的符号结构 | `{ filePath }` | 符号树 |
| `apex.completion` | 位置处的代码补全 | `{ filePath, line, character }` | 补全项 |

### SOQL

| 工具 | 目的 | 启动？ | 关键输出 |
|---|---|---|---|
| `validate_soql` | 解析 SOQL 字符串的 **语法** 错误 | SOQL LSP | `{ ok, diagnostics: [{ line, column, severity, message }] }` |
| `complete_soql` | 模式感知光标处的补全（SObjects、字段、组织解析的 picklist 值） | SOQL LSP | `{ ok, items, expanded, unresolved, hint? }` |
| `extract_soql_from_apex` | 静态提取 Apex 中的所有内联 `[SELECT …]` | **否**（纯静态） | `{ ok, totalQueries, totalDynamic, files }` |
| `check_soql_selectivity` | 选择性启发式（可选组织 LIMIT-0 探测） | 默认 **否** | 选择性报告 |
| `refresh_org_schema` | 使缓存的组织描述失效，以便补全重新获取 | **否** | `{ ok, removed }` |

> **刚部署了一个字段/对象，但它无法解析？** 当 SOQL 或 Apex 对新部署的字段引用失败时（例如 `No such column 'Foo__c'`，或 `complete_soql` 不提供它），在部署后立即失败，缓存的组织描述已过时——调用 **`refresh_org_schema`** 使其失效，然后重新运行检查，在假设代码错误或重命名任何东西之前。这是部署后模式延迟的杠杆；在将其视为查询/类的错误之前先使用它。（它仅清除本地缓存；它不能加快服务器端传播，因此如果组织本身尚未发布该字段，稍等片刻后重新运行是回退方法。）

### LWC——在此构建中不可用

`lwc.*` 工具（`lwc.diagnostics`、`lwc.hover`、`lwc.definition`、`lwc.completion`、`lwc.workspace_symbols`）由主机注册，但 LWC 语言服务器在此插件中 **不** 提供了。每个 `lwc.*` 调用都返回一个不可用的信封。对于 LWC 工作，回退到直接读取组件源/模板，或部署编译并读取 CLI 错误。

### 诊断/健康

| 工具 | 目的 | 启动？ |
|---|---|---|
| `lsp.health` | 只读视图，关闭开关模式、工作区、每服务器状态、断路器状态、冷启动时间、apex-ls 版本 | **否**——从不启动 |

所有坐标都是 **一基**（`line`/`column`）。`validate_soql` 诊断坐标相对于 **查询字符串**，而不是文件——当查询来自 `extract_soql_from_apex` 时，使用该查询的范围进行转换。

## 调用/回退合同

每个调用 LSP 工具的技能都遵循相同的三个规则：

1. **优先使用 LSP 工具而不是猜测。** 如果存在用于该步骤的工具（验证查询、编译检查类、针对组织模式补全），在回退到手动分析之前调用它。
2. **将错误信封视为“不可用”，而不是“通过”。** 工具可能会返回 `{ error: <code> }` 而不是结果（见错误代码）。对于任何此类代码，在报告中记录 `<tool>=unavailable: <code>` 并继续回退路径——**永远**不要因为检查未运行就报告输入有效/干净。
3. **降级，而不是失败。** LSP 是加速器，而不是硬依赖。如果主机完全不可用，`salesforce-lsp` 工具将不存在——回退到 CLI/手动路径，并说明。

### 当 LSP 主机缺失时

如果插件/主机不可用，上述 MCP 工具未注册，因此对（例如）`validate_soql` 的调用将无法解析。检测到错误信封的方式与检测到错误信封相同——工具不可用——并使用文档中记录的回退：

| LSP 工具不可用 | 回退 |
|---|---|
| `apex.diagnostics` | 通过 `sf project deploy` 部署/编译并读取 CLI 错误 |
| `validate_soql` | 通过 `sf data query --json` 以只读方式运行查询（解析错误在 CLI 错误中显示） |
| `complete_soql` | `sf sobject describe --sobject <O> --json` 用于字段；从用户声明的名称编写 |
| `extract_soql_from_apex` | 读取文件并手动定位 `[SELECT … ]` |
| `apex.completion` / `apex.hover` | 直接读取源代码 |
| `lwc.*`（始终不可用） | 直接读取组件源/模板，或部署编译并读取 CLI 错误 |

## 错误代码

工具返回 `{ error: <code> }`（或对于 `complete_soql`，返回一个 `hint`）而不是结果。每个代码都映射到一个恢复方法：

| 代码 | 含义 | 应该做什么 |
|---|---|---|
| `lsp_disabled` | 关闭开关（`SFDX_LSP`）禁止此语言 | 使用非 LSP 回退；或重新启用 LSP（见调试） |
| `spawn_timeout` | 语言服务器未在规定时间内启动 | 重试一次；如果仍然存在，回退并运行 `${CLAUDE_PLUGIN_ROOT}/bin/lsp-doctor` |
| `circuit_open` | 重复启动失败触发了断路器；调用被短路 | 立即回退；使用 `lsp.health` / `${CLAUDE_PLUGIN_ROOT}/bin/lsp-doctor` 调查 |
| `no_apex_workspace` | 任何包目录下都没有 `classes/*.cls`——Apex 工具不会启动 | 预期在非 Apex 项目中；无需检查 |
| `no_org_connected` | （`complete_soql` 提示）组织模式无法解析 | 关键字补全仍然有效；请求确切的字段/对象名称或连接组织。**不要**将 `__…_PLACEHOLDER` 标签显示为实际字段 |

前三个是每个启动工具共享的瞬态/配置状态；其余的是特定工作区/组织/文件上下文的健康预期状态——不是损坏安装的迹象。（`no_lwc_bundles` / `unsupported_lwc_file` 是 LWC 仅有的代码；在此构建中 LWC 服务器未提供，因此 `lwc.*` 返回不可用。）

## 调试 LSP

三个层级，从最便宜的开始：

1. **`lsp.health`（MCP 工具）。** 最快的检查——从不启动子进程。报告关闭开关模式、解析的工作区、每服务器状态、断路器状态、上次冷启动时间以及提供的 apex-ls 版本。要求 Claude 运行 `lsp.health`，或直接调用 `lsp.health` 工具。

2. **`bin/lsp-doctor`（CLI）。** 更深入的安装级诊断，用于支持和入门。验证提交的捆绑包是否存在，提供的 apex-ls 艺术品是否解析，组织模式缓存是否可解析，以及每个 LSP 子进程是否可以实际启动。健康时退出 `0`，出错时退出 `1` 并带有结构化的每个检查输出。

   ```bash
   "${CLAUDE_PLUGIN_ROOT}"/bin/lsp-doctor            # 人类可读报告
   "${CLAUDE_PLUGIN_ROOT}"/bin/lsp-doctor --json     # 机器可读
   "${CLAUDE_PLUGIN_ROOT}"/bin/lsp-doctor --no-spawn # 跳过子进程探测（CI/受限）
   ```

   （在此构建中 `lsp-doctor` 会报告 LWC 服务器缺失——这是预期的；这里仅提供了 Apex + SOQL。）

3. **`SFDX_LSP_DEBUG=1`。** 向 stderr 发出单行 JSON 远程指标（启动时间、缓存命中、断路器事件、每工具延迟）。默认关闭（零开销）。

### 关闭开关——`SFDX_LSP`

快速控制或禁用 LSP 的方法。设置环境变量：

| `SFDX_LSP` | 效果 |
|---|---|
| 未设置 / `all` | 每个提供的 LSP 都可以启动（默认） |
| `apex-only` | 仅 Apex LSP 可以启动；SOQL 工具返回 `lsp_disabled` |
| `disabled` | 没有启动 LSP；每个 LSP 工具返回 `lsp_disabled` |

要排除 LSP 的问题，设置 `SFDX_LSP=disabled` 并重新运行：如果问题仍然存在，则不是 LSP 的问题，技能将自动回退到非 LSP 路径。未知值默认为 `all`（带警告），因此打字错误永远不会无声地禁用功能。

## 部署前诊断门

`PreToolUse` 钩子（`bin/lsp-precheck`）在 `sf project deploy start`/`validate` 即将推送 `.cls`/`.trigger` 文件时运行 Apex 诊断，并发出决策。它 **允许失败**：任何错误（包括缺失/慢的 LSP）都允许部署。模式由 `SFDX_LSP_DEPLOY_GATE` (`off` | `warn` | `block`，默认 `warn`) 控制——`warn` 显示诊断但不阻止；`block` 拒绝有 Apex 编译错误的部署。

## 验证

- 询问“如何使用 Salesforce LSP 工具？”此技能是匹配的，并列出了工具、它们的输入/输出以及回退合同。
- 出现在 `/skills` 列表中，作为 `platform-lsp-integrate`。
- 给定一个错误代码（例如 `no_apex_workspace`），它解释了含义和正确的恢复，而不会将未运行的检查视为通过。

## 跨技能集成

| 需要 | 委托给 |
|---|---|
| 编译检查 + 分析您刚编写的 Apex | `platform-apex-generate` |
| 验证 `.cls`/`.trigger` 中的内联 SOQL | `validate_soql`（此技能）；回退：通过 `sf data query --json` 以只读方式运行 |
| 编写并运行针对组织的 SOQL 查询 | `complete_soql` + `sf data query` |
| 部署前诊断门行为 | 见“部署前诊断门”以上 |
