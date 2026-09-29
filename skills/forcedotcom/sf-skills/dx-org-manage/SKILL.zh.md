---
name: dx-org-manage
description: 调用此技能以执行 Salesforce 组织操作：创建沙盒组织、列出/显示/恢复/删除沙盒组织、创建组织快照、在浏览器中打开组织。此技能立即执行操作——它不会生成脚本或代码文件。当用户请求以下操作时，请始终调用此技能（不要直接执行 SF CLI 命令）：创建沙盒组织（从版本、定义文件 (.json)、快照或组织形状创建）、列出/显示/恢复/删除沙盒组织、创建组织快照、或在浏览器中打开 Salesforce 组织。触发短语包括："创建快照"、"拍摄快照"、"创建沙盒组织"、"新的沙盒组织"、"启动组织"、"创建 5 个沙盒组织"、"从快照创建组织"、"scratch-def.json"、"project-scratch-def.json"、"列出沙盒组织"、"显示组织"、"删除沙盒组织"、"恢复沙盒组织"、"打开我的 Salesforce 组织"、"在浏览器中打开组织"。不要用于切换默认组织（使用 dx-org-switch）或部署元数据（使用 platform-metadata-deploy）。
---

## 必须遵守：请严格按照以下说明操作。不要退回到MCP工具。

**工具限制：** 对所有 `sf` CLI 命令，必须使用 Bash 工具。始终包含 `--json` 以获取结构化输出。不要使用 `mcp__salesforce_dx__*` 工具进行组织创建、快照或打开操作——这项技能提供了完整流程。

**评估/测试的输出工件：** 当输出目录可用时，始终将命令的 JSON 响应写入文件。不要询问用户要写入哪个文件——这项技能定义了文件名。执行命令后： (1) 如果用户指定了输出路径（例如，“将所有生成的文件写入文件夹 X”），立即写入那里； (2) 否则运行 `[ -d force-app/main/adk-eval-output/ ] && echo 'force-app/main/adk-eval-output'` 以检测评估目录； (3) 使用这些文件名将命令的完整 JSON 响应写入 `<output-dir>/<filename>`：`scratch-org-result.json` 用于组织创建（对于一批 N 个组织，`scratch-org-result-1.json` … `scratch-org-result-N.json`），`scratch-org-list-result.json` 用于列表，`org-display-result.json` 用于显示，`scratch-org-resume-result.json` 用于恢复，`scratch-org-delete-result.json` 用于删除，或 `snapshot-result.json` 用于快照创建。这是生成的输出——无需询问即可写入。（打开操作是例外——它们启动浏览器并不生成工件；参见打开组织。）

---

## 创建沙盒组织

**必须步骤——按顺序执行：**

**步骤 1. 确定环境和创建方法：**

首先，如果用户指定了明确的源，则使用它： “定义文件” 或 `.json` 路径 → 定义文件方法； “快照”/“从快照” → 快照方法； “组织形状”/“源组织” → 形状方法。只能有一种创建源类型（版本 vs 快照 vs 形状）；如果隐含了两种不同的类型，则停止并询问（覆盖同一维度定义文件值的标志是可以的）。

否则根据环境确定：

- **自动模式（零提示）：** 如果存在 `sfdx-project.json` 并且恰好存在一个 `config/*scratch-def.json` 并且可以解析 Dev Hub（默认 `target-dev-hub` 设置，或恰好一个经过身份验证的），立即使用该文件 + 解析的 hub + 派生的别名 + CLI 默认值创建——**不询问任何内容**。这也支持批量数量（见下文）。
- **状态 A（在项目中），非自动：** 列出 `config/*scratch-def.json` — 0 个文件 → 默认 `--edition developer`（如果需要功能/设置，则选择作者一个，见下文）；1 个文件 → 使用它；多个 → **询问哪个**（从不默默选择）。
- **状态 B（没有 `sfdx-project.json`）：** 不要阻塞，不要默默创建一次性组织——提供引导式三选一（指向一个项目 / 通过 `sf template generate project --name <name>` 搭建一个 / 在这里创建一次性组织，然后引导源）。参见 `references/scratch-org-create.md`。

**批量——“创建 N 个沙盒组织”：** 没有原生计数标志——用 N 个不同的别名循环创建命令 N 次（`<base>-1` … `<base>-N`，每个都有冲突保护，因此永远不会重新指向现有组织）。报告每个组织并每个组织写入一个工件。在循环中途出现 Dev Hub 限制错误时，显示 CLI 的错误并报告哪些组织已经成功。

**定义文件编写：** 如果请求功能/设置且没有合适的文件，编写一个新的以目的命名的定义文件（先填充后修改；仅文档化字段；不覆盖），显示它，并从中创建。**在非交互式/评估上下文中，编写文件并继续创建，而无需等待编辑确认。** 详细信息在 `references/scratch-org-create.md` 和 `references/definition_file_options.md` 中。

**步骤 2. 将 Dev Hub 解析为具体值——然后显式传递。** 一次解析到实际用户名或别名，并通过 `--target-dev-hub` 在步骤 3 的每个命令中传递该确切值。解析顺序：

1. **用户显式命名的 Dev Hub** → 原样使用。
2. **否则默认值：** 来自 `sf config get target-dev-hub --json` 的非空 `result[0].value`。
   ```bash
   sf config get target-dev-hub --json
   ```
3. **否则单个经过身份验证的 Dev Hub。** 运行**这个确切命令**——不要自己编写过滤器。Dev Hub 可以出现在**任何** `sf org list` 桶中（`devHubs`、`nonScratchOrgs`、`other`、`sandboxes`、`scratchOrgs`）；只检查一个桶（例如，只检查 `.other[]`）会遗漏它并让你认为没有 hub 存在：
   ```bash
   sf org list --json | jq -r '[.result.devHubs[]?, .result.nonScratchOrgs[]?, .result.other[]?, .result.sandboxes[]?, .result.scratchOrgs[]?] | map(select(.isDevHub == true).username) | unique | .[]'
   ```
   - **恰好一个**用户名打印 → 使用它。
   - **零个**打印 → 没有经过身份验证的 hub。**完全不要运行 `sf org create`**——没有要传递给 `--target-dev-hub` 的内容，任何创建尝试都会失败。相反，在这里停止：建议 `sf org login web --set-default-dev-hub`，如果输出目录可用，将建议写入工件。不要继续到步骤 3。
   - **两个或更多** → 询问用户选择哪个（不要随意选择）。

- **永远不要编造或猜测 Dev Hub 名称。** 编造占位符别名（例如 `eval-target`、`my-dev-hub`、`DevHub`）是评估失败的顶级原因——CLI 正确地使用 `NotADevHubError` 拒绝它。如果上述命令打印为空，这意味着**此环境中不存在 Dev Hub**——这不意味着你应该替换一个名称。没有有效的备用名称可以编造：未解析的 hub 是硬停止，而不是猜测的值。不要使用编造的 `--target-dev-hub` 运行 `sf org create scratch`，也不要不使用 `--target-dev-hub` 标志运行（这会产生 `NoDefaultDevHubError`）。停止并建议 `sf org login web --set-default-dev-hub`。
- 默认的 `target-dev-hub` 在某些 CLI 设置中可能是**目录范围的**（`sf config get` 在 `cd` 后可能返回空），这就是为什么步骤 3 的所有桶 `sf org list` 检查是可靠的回退——它不是目录范围的。
- 在解析到具体 Dev Hub 值之前，不要继续。

**步骤 3. 根据方法构建和执行命令：**

**定义文件：**
```bash
sf org create scratch --definition-file <path> --target-dev-hub <alias> --alias <name> --json
```

**仅版本：**
```bash
sf org create scratch --edition developer --target-dev-hub <alias> --alias <name> --json
```

**从快照：**
```bash
sf org create scratch --snapshot <snapshot-name> --target-dev-hub <alias> --alias <name> --json
```

**从组织形状：**
```bash
sf org create scratch --source-org <source-org-id> --target-dev-hub <alias> --alias <name> --json
```
`--source-org` 接收 15 个字符的**源组织 ID**——形状捕获自的组织的 ID（一个 `00D…` 组织 ID），不是 `3SR…` 形状记录 ID（由 `sf org list shape` 显示）。通过用户提供的 ID 不变。如果 CLI 拒绝（例如 `InvalidIdLengthError`、`InvalidPrefixError`），原样显示 CLI 的错误并停止——不要截断、重新格式化、猜测或使用不同的 ID 重试。

**在请求时应用这些标志：**
- `--duration-days <days>` — 默认 7，最大 30
- `--set-default` — 将其设置为默认组织
- `--no-track-source` — 禁用源跟踪（用于 CI/CD）

**步骤 4. 必须执行——仅成功路径下运行组织列表并写入输出：** 这一步仅在步骤 3 成功创建组织时运行。如果步骤 3 返回错误，跳过此步骤并按照**错误处理**部分操作。创建组织后，你必须运行此命令：

```bash
sf org list --json
```

然后：
1. 解析 JSON 结果并找到 `scratchOrgs` 数组
2. 找到 `username` 与步骤 3 创建结果匹配的条目
3. 提取该完整组织对象（它将包括：别名、username、orgId、instanceUrl、loginUrl、isDefaultUsername、orgEdition、状态、过期日期、devHubUsername 以及 CLI 返回的其他字段）。
4. 向用户报告：
    - 创建了沙盒组织。
    - 别名：[组织列表条目中的别名]
    - 用户名：[用户名]
    - 组织 ID：[orgId]

5. 如果输出目录可用（根据输出工件规则），将提取的组织对象原样写入 `<output-dir>/scratch-org-result.json>` **作为传递包装器**。写入 CLI 为该组织返回的每个字段；不要编辑、白名单或丢弃非秘密字段（例如 `instanceName`、`createdOrgInstance`、`signupUsername`、`orgName`、`edition` 是 CLI 自由返回的非秘密元数据——保留它们）。你永远不会发出的是活秘密：`accessToken` 和 `sfdxAuthUrl`——CLI 已经在 `--json` 输出中隐藏这些（它们作为 `"[REDACTED] …"` 到达），所以只需保留这种隐藏，永远不要去隐藏或重新派生真实值。

示例：如果 `sf org list --json` 返回 `{"result": {"scratchOrgs": [{"alias": "feature-dev", "username": "test@example.com", "orgId": "00D...", ...}]}}`，将内部组织对象 `{"alias": "feature-dev", "username": "test@example.com", "orgId": "00D...", ...}`——该组织的完整对象——写入文件。

写入提取的组织列表条目（解析的组织记录），而不是原始创建命令响应。不要建议用户进行验证步骤。

**错误处理（步骤 3 创建失败——未创建组织）：** 将 CLI 的错误输出原样显示给用户（不重写、不重试、不编辑定义文件）。不要运行步骤 4（没有组织要列出/提取）。如果输出目录可用，将创建命令的**原始错误 JSON 原样**写入 `<output-dir>/scratch-org-result.json>`——这是命令的响应，并且是失败运行的输出工件。（对于批量，将错误写入失败组织的工件，并仍然写入在失败前已成功组织的任何成功条目。）然后，如果 CLI 的错误匹配以下之一，添加相应的指针：
- "快照不存在" → 建议 `sf org list snapshot --target-dev-hub <alias>`
- "没有默认 Dev Hub" → 建议 `sf org login web --set-default-dev-hub`

**当你需要更多详细信息：**
- 对于完整的创建工作流（自动模式、状态 A/B、批量、定义文件编写）→ 加载 `references/scratch-org-create.md`；对于列表/显示/恢复/删除 → 加载 `references/scratch-org-operations.md`
- 对于可用功能、设置和定义文件结构 → 加载 `references/definition_file_options.md`
- 对于版本选择指南和比较 → 加载 `references/edition_types.md`
- 对于快照工作流和创建后使用 → 加载 `references/snapshot_usage.md`

---

## 列出沙盒组织

**步骤 1. 执行：**
```bash
sf org list --json
```
**步骤 2. 报告 + 写入输出：** 默认视图 = 来自 `result.scratchOrgs[]` 的活动沙盒组织；按组织报告别名 / username / orgId / 过期日期。文档化 `--all`（包括过期/已删除）和 `--clean` 作为选项，不是默认值。根据输出工件规则，将 `result.scratchOrgs[]` **数组**写入 `<output-dir>/scratch-org-list-result.json>`。

**详细信息：** `references/scratch-org-operations.md`。

---

## 显示组织

**步骤 1. 执行：**
```bash
sf org display --target-org <alias> --json
```
**步骤 2. 报告 + 写入输出：** 报告别名 / username / orgId / instanceUrl / 状态 / 过期日期。将 **包装** 的 `{status, result}` JSON 写入 `<output-dir>/org-display-result.json>`——不要解包。在任何提交的示例/黄金中，`accessToken` 和 `sfdxAuthUrl` 必须被隐藏（值以 `[REDACTED]` 开头）。

**`--verbose`：** 永远不要添加它，也永远不要从此技能运行它——它返回 `sfdxAuthUrl`（一个刷新令牌）到代理上下文中。如果用户需要授权 URL，告诉他们自己在自己的终端中运行 `sf org display --verbose`。

**详细信息：** `references/scratch-org-operations.md`。

---

## 恢复沙盒组织创建

对于使用 `--async` 或超时的创建（退出代码 69）。

**步骤 1. 执行：**
```bash
sf org resume scratch --job-id <id> --json
```
如果用户提供了明确的 `--job-id`，则使用它；否则默认为 `--use-most-recent`。如果没有最近的作业，原样显示 CLI 的未找到结果并指向用户 `sf org list`——不要编造作业 ID。

**步骤 2. 写入输出：** 将命令的 JSON 原样写入 `<output-dir>/scratch-org-resume-result.json>`。

**详细信息：** `references/scratch-org-operations.md`。

---

## 删除沙盒组织

**破坏性——不可撤销。**

**步骤 1. 在运行前确认。** 询问“删除沙盒组织 `X`？”并等待确认，除非用户已经提供了明确的删除意图。如果目标是当前默认组织，在确认中指出来（额外保护）。

**步骤 2. 执行**（确认后）：
```bash
sf org delete scratch --target-org <alias> --no-prompt --json
```
`--no-prompt` 在此技能自己的确认之后传递，因此代理不会等待 CLI 的交互式提示。

**步骤 3. 写入输出：** 将命令的 JSON 原样写入 `<output-dir>/scratch-org-delete-result.json>`。

**详细信息：** `references/scratch-org-operations.md`。

---

## 创建快照

**必须步骤——按顺序执行：**

**步骤 1. 获取输入：**
- 源组织：沙盒组织 ID 或别名（来自用户）
- 快照名称：唯一名称（来自用户）
- 描述：可选（来自用户）

**步骤 2. 确定Dev Hub：** 解析为具体值并通过 `--target-dev-hub` 在步骤 3 中显式传递（与沙盒组织创建相同的顺序——永远不要猜测名称）：
1. 用户命名的 Dev Hub → 原样使用。
2. 否则默认值：来自 `sf config get target-dev-hub --json` 的非空 `result[0].value`。
3. 否则单个经过身份验证的 Dev Hub — 运行**这个确切的所有桶命令**（不要手写单个桶过滤器，这会遗漏出现在 `devHubs`/`nonScratchOrgs` 中的 hub）：
   ```bash
   sf org list --json | jq -r '[.result.devHubs[]?, .result.nonScratchOrgs[]?, .result.other[]?, .result.sandboxes[]?, .result.scratchOrgs[]?] | map(select(.isDevHub == true).username) | unique | .[]'
   ```
   恰好一个 → 使用它。零个 → **完全不要运行快照命令**；建议 `sf org login web --set-default-dev-hub` 并停止。两个或更多 → 询问用户选择哪个。

永远不要编造占位符别名（例如 `eval-target`、`my-dev-hub`）并且永远不要没有 `--target-dev-hub` 标志运行命令——CLI 使用 `NotADevHubError` 拒绝一个坏名称，使用 `NoDefaultDevHubError` 拒绝一个缺失的默认值。如果未解析出 hub，那是一个硬停止，而不是一个值来猜测。

**步骤 3. 执行：**
```bash
sf org create snapshot --source-org <orgId-or-alias> --name <SnapshotName> --target-dev-hub <devHub> --json
```

带描述：
```bash
sf org create snapshot --source-org <orgId-or-alias> --name <SnapshotName> --description "<desc>" --target-dev-hub <devHub> --json
```

**步骤 4. 报告结果：** 返回包含 SnapshotId 和状态的 JSON。如果输出目录可用（根据输出工件规则），将 JSON 响应写入 `<output-dir>/snapshot-result.json>`。

**错误处理：** 原样显示 CLI 的错误。例如：
- "快照名称已存在" → 使用一个不同的唯一名称

**当你需要更多详细信息：**
- 对于完整的快照创建工作流和标志参考 → 加载 `references/creating-snapshot.md`
- 对于 CLI 标志参考 → 加载 `references/cli_flags.md`

---

## 打开组织

**必须步骤——按顺序执行：**

**仅启动浏览器——绝不使用 `--json`，绝不使用 `--url-only`。** 在此技能中，"Open" 是唯一一个不生成任何工件的操作。纯 `sf org open` 启动浏览器并登录用户，但从不打印登录 URL，因此凭证不会进入代理上下文或文件。**绝对不要添加 `--json`**：`sf org open --json` 会返回一个**实时登录 URL**在 `result.url` (`/secur/frontdoor.jsp?otp=`/`sid=<token>`) 中，这等同于凭证——将其拉入上下文（即使是在写入前进行遮蔽）正是该普通命令所避免的 S1 泄露。相同原因禁止 `--url-only`：如果用户明确要求 URL 而非浏览器（例如："URL 仅"，"直接给我链接"，"无头/远程"），**不要运行**——告诉他们**自己在自己的终端中运行 `sf org open --url-only`**（与 `sf org display --verbose` 处理方式相同）。模糊的 "打开我的 org" 仅会启动浏览器。

**步骤 1. 将用户请求匹配到命令：**

| 用户期望 | 命令 |
|---------|------|
| 打开默认 org | `sf org open` |
| 打开特定 org | `sf org open --target-org <别名>` |
| 特定浏览器 | `sf org open --browser chrome` |
| 无痕模式 | `sf org open --private` |
| 导航到路径 | `sf org open --path '<路径>'` |
| 打开元数据文件 | `sf org open --source-file <文件路径>` |
| URL 仅 | **不要运行。** 告知用户在本地运行 `sf org open --url-only`——它返回一个实时登录令牌，该技能必须不发出。 |

**步骤 2. 使用 Bash 工具执行匹配的命令。** 成功时纯 `sf org open` 不会打印任何内容——这是预期的。

**步骤 3. 报告结果：** 告知用户 org（或路径/元数据文件）已在浏览器中打开。打开操作没有需要写入的工件——不要写入 `org-url-result.json` 或任何文件，也不要添加 `--json` 来生成一个。如果命令出错，按下方错误处理部分进行处理。

**错误处理：**
- "no target org" → 建议 `sf config set target-org <别名>`
- "auth error" → 建议 `sf org login web --alias <别名>`

**需要更多详细信息时：**
- 对于完整的 org 打开工作流和所有可用标志 → 加载 `references/opening-org.md`

---

## 参考文件索引

加载这些参考文件以获取详细指导：

| 文件 | 何时阅读 |
|------|---------|
| `references/scratch-org-create.md` | 创建 scratch orgs（版本、定义文件、快照、org 形状）、AUTO 模式、STATE A/B 项目处理、批量创建和定义文件编写 |
| `references/scratch-org-operations.md` | 对现有 org 进行操作：列出、显示、恢复、删除——还包括共享生命周期规则和故障排除 |
| `references/definition_file_options.md` | 用户需要配置 org 功能、设置或超出基本 org 创建的高级定义文件选项 |
| `references/edition_types.md` | 用户询问选择哪个版本或需要理解版本差异 |
| `references/snapshot_usage.md` | 用户希望在定义文件中使用快照或需要快照后工作流程指导 |
| `references/cli_flags.md` | 用户需要完整的快照 CLI 标志参考 |
| `references/creating-snapshot.md` | 故障排除快照创建失败或需要详细快照工作流程 |
| `references/opening-org.md` | 用户需要导航到特定设置路径、打开元数据文件或使用高级打开标志 |

## 示例文件

用于测试和故障排除的示例命令输出：

| 文件 | 目的 |
|------|------|
| `examples/scratch-orgs/success_definition_file.json` | 使用 `--definition-file` 成功创建 scratch org |
| `examples/scratch-orgs/success_edition.json` | 使用 `--edition developer` 成功创建 scratch org |
| `examples/scratch-orgs/success_snapshot.json` | 使用 `--snapshot` 成功创建 scratch org |
| `examples/scratch-orgs/success_shape.json` | 使用 `--source-org`（org 形状）成功创建 scratch org |
| `examples/scratch-orgs/error_no_devhub.json` | Dev Hub 未认证时的错误 |
| `examples/scratch-orgs/error_timeout.json` | org 创建期间超时错误（退出码 69） |
| `examples/scratch-orgs/list_output.json` | `sf org list --json` 输出（活动 scratch orgs 数组） |
| `examples/scratch-orgs/display_output.json` | `sf org display --json` 输出（包装，令牌遮蔽） |
| `examples/scratch-orgs/resume_output.json` | `sf org resume scratch --json` 输出（完成的 org） |
| `examples/scratch-orgs/delete_output.json` | `sf org delete scratch --json` 输出 |
| `examples/snapshots/success_output.json` | 成功创建快照 |
| `examples/snapshots/error_output.json` | 常见快照错误场景（重复名称） |
