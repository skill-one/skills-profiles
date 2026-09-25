## 必须遵守：请严格按照以下说明操作。切勿退回到MCP工具。

**工具限制：** 对所有 `sf` CLI 命令，请使用 Bash 工具。始终包含 `--json` 以获取结构化输出。切勿使用 `mcp__salesforce_dx__*` 工具进行组织创建、快照或打开操作——这项技能提供了完整流程。

**评估/测试的输出工件：** 当提供输出目录时，请始终将命令的 JSON 响应写入文件。切勿询问用户要写入哪个文件——这项技能定义了文件名。执行命令后： (1) 如果用户指定了输出路径（例如，“将所有生成的文件写入文件夹 X”），请立即写入该路径； (2) 否则运行 `[ -d force-app/main/adk-eval-output/ ] && echo 'force-app/main/adk-eval-output'` 以检测评估目录； (3) 使用这些文件名将命令的完整 JSON 响应写入 `<output-dir>/<filename>`：`scratch-org-result.json` 用于组织创建（对于 N 个组织的批次，`scratch-org-result-1.json` … `scratch-org-result-N.json`），`scratch-org-list-result.json` 用于列表，`org-display-result.json` 用于显示，`scratch-org-resume-result.json` 用于恢复，或 `scratch-org-delete-result.json` 用于删除。这是生成的输出——无需询问即可写入。(打开操作是例外——它们启动浏览器并不写入工件；参见打开组织。)

---

## 创建 Scratch 组织

**必须步骤——按顺序执行：**

**步骤 1. 确定环境和创建方法：**

首先，如果用户指定了明确来源，请使用它：“定义文件”或 `.json` 路径 → 定义文件方法；“快照”/“从快照”→ 快照方法；“组织形状”/“源组织”→ 形状方法。仅有一种创建来源类型（版本 vs 快照 vs 形状）；如果隐含两种不同的类型，请停止并询问（覆盖同一维度定义文件值的标志是允许的）。

否则通过环境解析：

- **自动模式（零提示）：** 如果存在 `sfdx-project.json` 并且恰好存在一个 `config/*scratch-def.json` 并且可解析 Dev Hub（默认 `target-dev-hub` 设置，或恰好一个经过身份验证的），立即使用该文件 + 解析的 hub + 派生的别名 + CLI 默认值创建——**无需询问**。这也尊重批次计数（见下文）。
- **状态 A（在项目中），非自动：** 列出 `config/*scratch-def.json` — 0 个文件 → 默认 `--edition developer`（如果需要功能/设置，请参见下文创建作者一个）；1 个文件 → 使用它；多个 → **询问选择哪一个**（切勿无声选择）。
- **状态 B（没有 `sfdx-project.json`）：** 不要阻塞，不要无声创建一次性组织——提供引导的三向选择（指向一个项目 / 通过 `sf template generate project --name <name>` 构建一个 / 在此处创建一次性组织，然后引导来源）。参见 `references/scratch-org-create.md`。

**批次——“创建 N 个 Scratch 组织”：** 没有原生计数标志——使用创建命令 N 次并使用 N 个不同的别名（`<base>-1` … `<base>-N`，每个都有冲突保护，因此它永远不会重新指向现有组织）。报告每个组织并写入每个组织一个工件。在循环中的 Dev Hub 限制错误时，显示 CLI 的错误并报告哪些组织已经成功。

**定义文件编写：** 如果请求功能/设置且没有合适的文件存在，编写一个新的以目的命名的定义文件（先种子后修改；仅文档化字段；无覆盖），显示它，并从中创建。**在非交互式/评估上下文中，编写文件并继续创建，而无需等待编辑确认。** 详细信息在 `references/scratch-org-create.md` 和 `references/definition_file_options.md` 中。

**步骤 2. 将 Dev Hub 解析为具体值——然后显式传递。** 解析**一次**到实际用户名或别名，并通过 `--target-dev-hub` 在步骤 3 的每个命令中传递该确切值。解析顺序：

1. **用户显式命名的 Dev Hub** → 原封不动使用它。
2. **否则默认值：** 来自 `sf config get target-dev-hub --json` 的非空 `result[0].value`。
   ```bash
   sf config get target-dev-hub --json
   ```
3. **否则单个经过身份验证的 Dev Hub。** 运行**这个确切命令**——不要自己编写过滤器。Dev Hub 可以出现在**任何** `sf org list` 桶中（`devHubs`、`nonScratchOrgs`、`other`、`sandboxes`、`scratchOrgs`）；只检查一个桶（例如，仅 `.other[]`）的过滤器会遗漏它并使你误以为没有 hub 存在：
   ```bash
   sf org list --json | jq -r '[.result.devHubs[]?, .result.nonScratchOrgs[]?, .result.other[]?, .result.sandboxes[]?, .result.scratchOrgs[]?] | map(select(.isDevHub == true).username) | unique | .[]'
   ```
   - **打印出确切一个**用户名 → 使用它。
   - **打印出零个** → 没有经过身份验证的 hub。**切勿运行 `sf org create`**——没有要传递给 `--target-dev-hub` 的内容，任何创建尝试都会失败。相反，在此停止：建议 `sf org login web --set-default-dev-hub`，如果提供输出目录，将此建议写入工件。不要继续到步骤 3。
   - **两个或更多** → 询问用户选择哪一个（不要任意选择）。

- **切勿编造或猜测 Dev Hub 名称。** 编造占位符别名（例如 `eval-target`、`my-dev-hub`、`DevHub`）是评估失败的顶级原因——CLI 正确地使用 `NotADevHubError` 拒绝它。如果上述命令打印出空内容，这意味着**此环境中不存在 Dev Hub**——这意味着你不应该替换一个名称。没有有效的编造名称：未解析的 hub 是硬停止，而不是要猜测的值。不要使用编造的 `--target-dev-hub` 运行 `sf org create scratch`，也不要运行没有 `--target-dev-hub` 标志的命令（那会产生 `NoDefaultDevHubError`）。停止并建议 `sf org login web --set-default-dev-hub`。
- 默认的 `target-dev-hub` 在某些 CLI 设置中可能**是目录范围的**（`sf config get` 在 `cd` 后可能返回空），这就是为什么步骤 3 的所有桶 `sf org list` 检查是可靠的回退——它不是目录范围的。
- 在解析出具体 Dev Hub 值之前，不要继续。

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
`--source-org` 接收 15 个字符的**源组织 ID**——形状捕获自的组织的 ID（一个 `00D…` 组织 ID），不是 `3SR…` 形状记录 ID（由 `sf org list shape` 显示）。通过用户给出的 ID 不变。如果 CLI 拒绝它（例如 `InvalidIdLengthError`、`InvalidPrefixError`），原封不动显示 CLI 的错误并停止——不要截断、重新格式化、猜测或使用不同的 ID 重试。

**在请求时应用这些标志：**
- `--duration-days <days>` — 默认 7，最大 30
- `--set-default` — 将其设置为默认组织
- `--no-track-source` — 禁用源跟踪（用于 CI/CD）

**步骤 4. 必须执行——仅成功路径下运行组织列表并写入输出：** 这一步骤仅在步骤 3 成功创建组织时运行。如果步骤 3 返回错误，跳过此步骤并按照**错误处理**下文中的说明操作。创建组织后，你必须运行此命令：

```bash
sf org list --json
```

然后：
1. 解析 JSON 结果并找到 `scratchOrgs` 数组
2. 找到 `username` 匹配步骤 3 创建结果的用户名的条目
3. 提取该完整组织对象（它将包括：别名、username、orgId、instanceUrl、loginUrl、isDefaultUsername、orgEdition、status、expirationDate、devHubUsername 以及 CLI 返回的其他字段）。
4. 向用户报告：
    - 创建了 Scratch 组织。
    - 别名：[组织列表条目中的别名]
    - 用户名：[用户名]
    - 组织 ID：[orgId]

5. 如果提供输出目录（根据输出工件规则），将提取的组织对象写入 `<output-dir>/scratch-org-result.json` **原样——这项技能是一个传递式包装器**。写入 CLI 为该组织返回的每个字段；不要策展、白名单或丢弃非秘密字段（例如 `instanceName`、`createdOrgInstance`、`signupUsername`、`orgName`、`edition` 是 CLI 自由返回的非秘密元数据——保留它们）。你永远不会发出的是活秘密：`accessToken` 和 `sfdxAuthUrl`——CLI 已经在 `--json` 输出中删除这些（它们作为 `"[REDACTED] …"` 到达），所以只需保留这种删除并永远不要取消删除或重新导出真实值。

示例：如果 `sf org list --json` 返回 `{"result": {"scratchOrgs": [{"alias": "feature-dev", "username": "test@example.com", "orgId": "00D...", ...}]}}`，将内部组织对象 `{"alias": "feature-dev", "username": "test@example.com", "orgId": "00D...", ...}`——该组织的完整对象——写入文件。

写入提取的组织列表条目（解析的组织记录），而不是原始创建命令响应。不要建议用户进行验证步骤。

**错误处理（步骤 3 创建失败——未创建组织）：** 将 CLI 的错误输出原封不动地显示给用户（不要重写、不要重试、不要编辑定义文件）。不要运行步骤 4（没有要列出/提取的组织）。如果提供输出目录，将创建命令的**原始错误 JSON 原样**写入 `<output-dir>/scratch-org-result.json`——这是命令的响应，并且是失败运行的输出工件。（对于批次，将错误写入失败的组织的工件，并仍然写入任何在失败前已成功的组织的成功条目。）然后，如果 CLI 的错误匹配以下之一，添加相应的指针：
- "快照未找到" → 建议 `sf org list snapshot --target-dev-hub <alias>`
- "没有默认 Dev Hub" → 建议 `sf org login web --set-default-dev-hub`

**当你需要更多详细信息：**
- 对于完整创建工作流（AUTO MODE、STATE A/B、批次、定义文件编写）→ 加载 `references/scratch-org-create.md`；对于列表/显示/恢复/删除 → 加载 `references/scratch-org-operations.md`
- 对于可用功能、设置和定义文件结构 → 加载 `references/definition_file_options.md`
- 对于版本选择指南和比较 → 加载 `references/edition_types.md`
- 要在引用它之前创建/检查/列出/删除快照本身 → 使用 `dx-org-snapshot-manage` 技能

---

## 列出 Scratch 组织

**步骤 1. 执行：**
```bash
sf org list --json
```
**步骤 2. 报告 + 写入输出：** 默认视图 = `result.scratchOrgs[]` 中的活动 Scratch 组织；按组织报告别名 / username / orgId / 过期日期。文档化 `--all`（包括过期/已删除）和 `--clean` 作为选项，不是默认值。根据输出工件规则，将 `result.scratchOrgs[]` **数组**写入 `<output-dir>/scratch-org-list-result.json`。

**详细信息：** `references/scratch-org-operations.md`。

---

## 显示组织

**步骤 1. 执行：**
```bash
sf org display --target-org <alias> --json
```
**步骤 2. 报告 + 写入输出：** 报告别名 / username / orgId / instanceUrl / status / 过期日期。将 **包装的** `{status, result}` JSON 写入 `<output-dir>/org-display-result.json`——不要解包。在任何提交的示例/黄金中，`accessToken` 和 `sfdxAuthUrl` 必须被删除（值以 `[REDACTED]` 开头）。

**`--verbose`：** 永远不要添加它，也永远不要从这个技能中运行它——它返回 `sfdxAuthUrl`（一个刷新令牌）到代理上下文中。如果用户需要授权 URL，告诉他们自己在自己的终端中运行 `sf org display --verbose`。

**详细信息：** `references/scratch-org-operations.md`。

---

## 恢复 Scratch 组织创建

对于使用 `--async` 或超时的创建（退出码 69）。

**步骤 1. 执行：**
```bash
sf org resume scratch --job-id <id> --json
```
如果用户给出了明确的 `--job-id`，使用它；否则默认为 `--use-most-recent`。如果没有最近的作业，原封不动显示 CLI 的未找到结果并指向用户 `sf org list`——不要编造作业 ID。

**步骤 2. 写入输出：** 将命令的 JSON 原样写入 `<output-dir>/scratch-org-resume-result.json`。

**详细信息：** `references/scratch-org-operations.md`。

---

## 删除 Scratch 组织

**破坏性——不可撤销。**

**步骤 1. 在运行前确认。** 询问“删除 Scratch 组织 `X`？”并等待确认，除非用户已经给出了明确的删除意图。如果目标是当前默认组织，在确认中指出来（额外保护）。

**步骤 2. 执行**（确认后）：
```bash
sf org delete scratch --target-org <alias> --no-prompt --json
```
`--no-prompt` 在技能自己的确认之后传递，因此代理不会等待 CLI 的交互式提示。

**步骤 3. 写入输出：** 将命令的 JSON 原样写入 `<output-dir>/scratch-org-delete-result.json`。

**详细信息：** `references/scratch-org-operations.md`。

---

## 打开组织

**必须步骤——按顺序执行：**

**仅浏览器启动——永不 `--json`，永不 `--url-only`。** 打开是这项技能中唯一不写入工件的操作。纯 `sf org open` 启动浏览器并登录用户，而不会打印登录 URL，因此凭证不会进入代理上下文或文件。不要添加 `--json`：`sf org open --json` 返回 **活登录 URL** 在 `result.url` (`/secur/frontdoor.jsp?otp=`/`sid=<token>`) 中，这是凭证等效的——将其引入上下文（即使是在删除它之前写入）是纯命令避免的 S1 泄露。相同原因 `--url-only` 被禁止：如果用户明确要求 URL 而不是浏览器（例如，“URL 仅”，“只给我链接”，“无头/远程”），不要运行它——告诉他们自己在自己的终端中运行 `sf org open --url-only`（与 `sf org display --verbose` 的处理相同）。模糊的“打开我的组织”只是打开浏览器。

**步骤 1. 将用户请求匹配到命令：**

| 用户想要 | 命令 |
|-----------|---------|
| 打开默认组织 | `sf org open` |
| 打开特定组织 | `sf org open --target-org <alias>` |
| 特定浏览器 | `sf org open --browser chrome` |
| 无痕模式 | `sf org open --private` |
| 导航到路径 | `sf org open --path '<path>'` |
| 打开元数据文件 | `sf org open --source-file <file-path>` |
| URL 仅 | **不要运行。** 告诉用户在本地运行 `sf org open --url-only`——它返回一个活登录令牌，技能必须不发出。 |

**步骤 2. 使用 Bash 工具执行匹配的命令。** 纯 `sf org open` 在成功时什么也不打印——这是预期的。

**步骤 3. 报告结果：** 向用户报告组织（或路径/元数据文件）已在浏览器中打开。打开操作没有工件要写入——不要写入 `org-url-result.json` 或任何文件，也不要添加 `--json` 来生成一个。如果命令出错，按照错误处理下文中的说明显示它。

**错误处理：**
- "没有目标组织" → 建议 `sf config set target-org <alias>`
- "认证错误" → 建议 `sf org login web --alias <alias>`

**当你需要更多详细信息：**
- 对于完整打开组织工作流和所有可用标志 → 加载 `references/opening-org.md`

---

## 参考文件索引

加载这些参考文件以获取详细指导：

| 文件 | 何时阅读 |
|------|-------------|
| `references/scratch-org-create.md` | 创建 Scratch 组织（版本、定义文件、快照、组织形状），AUTO MODE、STATE A/B 项目处理、批次创建、定义文件编写 |
| `references/scratch-org-operations.md` | 对现有组织进行操作：列表、显示、恢复、删除——以及共享生命周期规则和故障排除 |
| `references/definition_file_options.md` | 用户需要配置组织功能、设置或超出基本组织创建的更高级定义文件选项 |
| `references/edition_types.md` | 用户询问选择哪个版本或需要了解版本差异 |
| `references/opening-org.md` | 用户需要导航到特定设置路径、打开元数据文件或使用高级打开标志 |

要创建/检查/列出/删除快照本身（而不是仅仅消费一个），使用 `dx-org-snapshot-manage` 技能。

## 示例文件

用于测试和故障排除的示例命令输出：

| 文件 | 目的 |
|------|---------|
| `examples/scratch-orgs/success_definition_file.json` | 使用 `--definition-file` 成功创建 Scratch 组织 |
| `examples/scratch-orgs/success_edition.json` | 使用 `--edition developer` 成功创建 Scratch 组织 |
| `examples/scratch-orgs/success_snapshot.json` | 使用 `--snapshot` 成功创建 Scratch 组织 |
| `examples/scratch-orgs/success_shape.json` | 使用 `--source-org`（组织形状）成功创建 Scratch 组织 |
| `examples/scratch-orgs/error_no_devhub.json` | Dev Hub 未经过身份验证时的错误 |
| `examples/scratch-orgs/error_timeout.json` | 组织创建期间超时错误（退出码 69） |
| `examples/scratch-orgs/list_output.json` | `sf org list --json` 输出（活动 Scratch 组织数组） |
| `examples/scratch-orgs/display_output.json` | `sf org display --json` 输出（包装的，令牌已删除） |
| `examples/scratch-orgs/resume_output.json` | `sf org resume scratch --json` 输出（完成的组织） |
| `examples/scratch-orgs/delete_output.json` | `sf org delete scratch --json` 输出 |
