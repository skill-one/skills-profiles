# NuGet 信任发布设置

在 GitHub Actions 仓库中设置 [NuGet 信任发布](https://learn.microsoft.com/en-us/nuget/nuget-org/trusted-publishing)。用基于 OIDC 的短时效令牌替代长期有效的 API 密钥——无需轮换或泄露密钥。

## 前置条件

- **GitHub Actions** — 本技能仅涵盖 GitHub Actions 的设置
- **nuget.org 账户** — 用户需要有权创建信任发布策略

## 何时使用此技能

在以下情况下使用此技能：
- 为 NuGet 包设置信任发布
- 从 `secrets.NUGET_API_KEY` 迁移到基于 OIDC 的发布
- 被问及无密钥或安全的 NuGet 发布
- 从零开始创建新的 NuGet 发布工作流
- 被问及“删除 NuGet API 密钥”或“使用 NuGet/login”
- 为 .NET 工具、MCP 服务器或模板包设置发布
- 被问及 `NuGet/login@v1` 或 `id-token: write`

## 安全规则

> ⚠️ **退出规则**：如果基础设施/认证问题在尝试修复一次后任何阶段失败，停止并询问用户。不要在环境问题上循环。

> ⚠️ **未经确认，切勿删除或覆盖**：删除 API 密钥密钥、删除标签/发布、删除工作流步骤或更改包 ID。NuGet 包 ID 是永久性的——错误无法撤销。

## 流程

> **适用于空白仓库的快速路径**：当用户有简单设置（一个可打包项目，没有现有的发布工作流）时，不要设置多轮评估。合并阶段：立即创建工作流，包含 nuget.org 策略指南、本地打包建议和文件名匹配警告，全部在一个响应中。下面的完整分阶段流程适用于复杂或迁移场景。

### 第一阶段：评估

在做出任何更改之前检查仓库并报告发现。

1. **查找并分类可打包项目** — 检查 `.csproj` 文件和 `Directory.Build.props`（包元数据通常在仓库范围内设置）。按以下顺序分类（先匹配的优先）：
   - `<PackageType>Template</PackageType>` → **模板**
   - `<PackageType>McpServer</PackageType>` → **MCP 服务器**（也是 .NET 工具）
   - `<PackAsTool>true</PackAsTool>` → **.NET 工具**
   - 类库（`IsPackable=true` 或没有 `OutputType`）→ **库**
   - `<OutputType>Exe</OutputType>` 且 `<IsPackable>true</IsPackable>` → **应用程序包**（不是工具，但仍然可发布）
   - `<OutputType>Exe</OutputType>` 且没有 `PackAsTool` 或 `IsPackable` → 默认不可打包（询问用户是否打算发布它）

2. **验证每个项目的结构**：

   | 类型 | 必需 |
   |------|------|
   | 所有 | `PackageId`, `Version`（在 .csproj 或 Directory.Build.props 中） |
   | .NET 工具 | `PackAsTool`（必需）；`ToolCommandName`（可选但推荐——默认为程序集名称） |
   | MCP 服务器 | `PackageType=McpServer`，`.mcp/server.json` 包含在包中 |
   | 模板 | `PackageType=Template`，`.template.config/template.json` 在内容目录下 |

3. **查找现有的发布工作流** 在 `.github/workflows/` 中 — 查找 `dotnet nuget push`、`nuget push` 或 `dotnet pack`。

4. **检查版本一致性** — 对于 MCP 服务器，验证 `.csproj` `<Version>` 与 `server.json` 的两个版本字段（根 `version` 和 `packages[].version`）是否匹配。标记任何不匹配。

5. **向用户报告发现**：分类、缺失属性、版本不匹配、现有工作流。对于多项目仓库，注意是否需要一个工作流或每个包单独的工作流。提供修复差距的选项——使用 `ask_user` 之前不要修改项目文件。

> ❌ 参考文档 [references/package-types.md](references/package-types.md) 获取每个类型的详细信息和必需属性。

### 第二阶段：本地验证

在触摸 nuget.org 之前进行打包和验证——发布错误会浪费永久版本号。

> ⚠️ **始终提及此步骤**，即使你推迟运行它。告诉用户：“在第一次发布之前，运行 `dotnet pack -c Release -o ./artifacts` 以验证是否正确创建 .nupkg。”

1. `dotnet pack -c Release -o ./artifacts` — 验证是否创建 `.nupkg`
2. 对于工具/MCP 服务器：从 `./artifacts` 安装，运行 `--help`，卸载
3. 对于库：检查 `.nupkg` 内容（它是一个 zip）

### 第三阶段：nuget.org 策略

此阶段需要用户在 nuget.org 上操作——用确切的值指导他们。

1. 确定仓库所有者、仓库名称以及将要发布的**工作流文件名**。

   > ❌ 策略要求**精确的工作流文件名**（例如，`publish.yml` 或 `publish.yaml`）——仅文件名，不带路径前缀。匹配不区分大小写。不要使用工作流 `name:` 字段。

2. 指导用户创建信任发布策略：
   > 前往 [**nuget.org/account/trustedpublishing**](https://www.nuget.org/account/trustedpublishing) → **添加策略**
   >
   > - **仓库所有者**：`{owner}`
   > - **仓库**：`{repo}`
   > - **工作流文件**：`{filename}.yml`
   > - **环境**：`release` *(仅当工作流使用 `environment:`；否则留空)*

   策略所有权：用户选择个人账户或组织。组织拥有的策略适用于该组织拥有的所有包。

   对于**私有仓库**：策略在 7 天内“临时激活”——在第一次成功发布后变为永久。

3. 指导用户创建一个**GitHub 环境**（推荐但可选——提供密钥范围 + 审批门）：
   > 仓库 **设置** → **环境** → **新建环境** → `release`
   >
   > 添加环境密钥：**名称** = `NUGET_USER`，**值** = nuget.org 用户名（不是电子邮件）

   可选：添加**必需的审阅者**以进行审批门。

> ⚠️ 在要求用户删除旧的 API 密钥/密钥或尝试使用工作流运行/发布之前，等待用户确认他们已创建策略。在确认之前，可以起草或显示工作流文件本身。

### 第四阶段：工作流设置

创建或修改发布工作流。**工作流必须始终在你的响应中创建或显示**——即使 nuget.org 策略尚未确认，你也可以起草/显示它，但在确认之前不要指导用户实际运行/发布或删除旧密钥。

**空白仓库**：从 [references/publish-workflow.md](references/publish-workflow.md) 中的模板创建 `publish.yml`。调整 .NET 版本、项目路径和环境名称。确保你的输出明确提到 `id-token: write` 和 `NuGet/login@v1`。

**迁移**（现有使用 API 密钥的工作流）：就地修改—

1. **向发布作业添加 OIDC 权限和环境**：
   ```yaml
   jobs:
     publish:
       environment: release
       permissions:
         id-token: write     # 必需——没有这个，NuGet/login 会以 403 失败
         contents: read      # 显式——设置权限会覆盖默认值
   ```

2. **在推送之前添加 NuGet 登录步骤**：
   ```yaml
   - name: NuGet login (OIDC)
     id: login
     uses: NuGet/login@v1
     with:
       user: ${{ secrets.NUGET_USER }}  # nuget.org 个人资料名称，不是电子邮件
   ```

3. **替换推送步骤中的 API 密钥**：
   ```yaml
   --api-key ${{ steps.login.outputs.NUGET_API_KEY }} --skip-duplicate
   ```

4. **验证**：要求用户触发发布并确认包出现在 nuget.org 上。

> ❌ **在信任发布验证之前不要删除旧的 API 密钥密钥**。删除它是一个单向门——等待确认。

## 故障排除

| 问题 | 原因 | 修复 |
|------|------|------|
| `NuGet/login` 403 | 缺少 `id-token: write` | 添加到作业权限 |
| "没有匹配的策略" | 工作流文件名不匹配 | 在 nuget.org 上验证精确文件名 |
| 推送未授权 | 包不属于策略账户 | 在 nuget.org 上检查策略所有者 |
| 令牌过期 | 登录步骤在推送前超过 1 小时 | 将 `NuGet/login` 移近推送 |
| "临时激活" 策略 | 私有仓库，第一次发布待定 | 在 7 天内发布 |
| `already_exists` 在推送时 | 重新运行相同版本 | 添加 `--skip-duplicate` |
| GitHub Release 422 | 标签的重复发布 | 删除冲突的发布（先确认） |
| 重新运行使用错误的 YAML | `gh run rerun` 重放原始提交的 YAML | 删除障碍，重新运行——永远不要重新标记 |

> ⚠️ 如果任何障碍在尝试修复一次后仍然存在，**停止并询问用户**。

## 参考

- **包类型详细信息**：[references/package-types.md](references/package-types.md) — 检测逻辑、必需属性、最小的 .csproj 示例
- **发布工作流模板**：[references/publish-workflow.md](references/publish-workflow.md) — 完整的标签触发工作流，准备好适应
- **Microsoft 文档**：[NuGet 信任发布](https://learn.microsoft.com/en-us/nuget/nuget-org/trusted-publishing)
