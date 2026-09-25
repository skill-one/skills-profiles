# 配置 Dataverse MCP 以供 GitHub Copilot 使用

此技能将 Dataverse MCP 服务器配置为 GitHub Copilot，使用您组织的环境 URL。每个组织都基于组织标识符注册一个唯一的服务器名称（例如，`DataverseMcporgbc9a965c`）。如果用户提供了 URL，则为 `$ARGUMENTS`。

## 说明

### 0. 询问 MCP 范围

询问用户是否希望全局配置 MCP 服务器或仅为此项目配置：

> 您希望配置 Dataverse MCP 服务器：
> 1. **全局**（在所有项目中可用）
> 2. **仅限项目**（仅在当前项目中可用）

根据他们的选择，设置 `CONFIG_PATH` 变量：
- **全局**：`~/.copilot/mcp-config.json`（使用用户的家目录）
- **项目**：`.mcp/copilot/mcp.json`（相对于当前工作目录）

将此路径存储以用于步骤 1 和步骤 6。

### 1. 检查已配置的 MCP 服务器

读取步骤 0 确定的 `CONFIG_PATH` 处的 MCP 配置文件，以检查已配置的服务器。

配置文件是一个具有以下结构的 JSON 文件：

```json
{
  "mcpServers": {
    "ServerName1": {
      "type": "http",
      "url": "https://example.com/api/mcp"
    }
  }
}
```

或者它可能使用 `"servers"` 而不是 `"mcpServers"` 作为顶层键。

从已配置的服务器中提取所有 `url` 值，并将它们存储为 `CONFIGURED_URLS`。例如：

```json
["https://orgfbb52bb7.crm.dynamics.com/api/mcp"]
```

如果文件不存在或为空，则将 `CONFIGURED_URLS` 视为空（`[]`）。此步骤必须永远不会阻塞技能。

### 2. 询问如何获取环境 URL

询问用户：

> 您希望如何提供您的 Dataverse 环境 URL？
> 1. **自动发现** — 列出来自您的 Azure 账户的可用环境（需要 Azure CLI）
> 2. **手动输入** — 直接输入 URL

根据他们的选择：
- 如果 **自动发现**：继续步骤 2a
- 如果 **手动输入**：跳到步骤 2b

### 2a. 自动发现环境

**检查先决条件：**
- 验证是否已安装 Azure CLI (`az`)（使用 `which az` 或 Windows 上的 `where az` 检查）
- 如果未安装，通知用户并回退到步骤 2b

**进行 API 调用：**

1. 检查用户是否已登录 Azure CLI：
   ```bash
   az account show
   ```
   如果此操作失败，提示用户登录：
   ```bash
   az login
   ```

2. 获取 Power Apps API 的访问令牌：
   ```bash
   az account get-access-token --resource https://service.powerapps.com/ --query accessToken --output tsv
   ```

3. 调用 Power Apps API 列出环境：
   ```
   GET https://api.powerapps.com/providers/Microsoft.PowerApps/environments?api-version=2016-11-01
   Authorization: Bearer {token}
   Accept: application/json
   ```

4. 解析 JSON 响应以过滤出 `properties?.linkedEnvironmentMetadata?.instanceUrl` 不为空的環境。

5. 对于每个匹配的環境，提取：
   - `properties.displayName` 作为 `displayName`
   - `properties.linkedEnvironmentMetadata.instanceUrl`（删除尾随斜杠）作为 `instanceUrl`

6. 创建一个格式为以下的环境列表：
   ```json
   [
     { "displayName": "My Org (default)", "instanceUrl": "https://orgfbb52bb7.crm.dynamics.com" },
     { "displayName": "Another Env", "instanceUrl": "https://orgabc123.crm.dynamics.com" }
   ]
   ```

**如果 API 调用成功**，继续到步骤 3。

**如果 API 调用失败**（用户未登录、网络错误、未找到环境或任何其他错误），告诉用户出了什么问题并回退到步骤 2b。

### 2b. 手动输入 — 询问 URL

要求用户直接提供他们的环境 URL：

> 请输入您的 Dataverse 环境 URL。
>
> 示例：`https://myorg.crm10.dynamics.com`
>
> 您可以在 Power Platform 管理中心的环境下找到此 URL。

然后跳到步骤 4。

### 3. 询问用户选择环境

将环境以编号列表的形式呈现。对于每个环境，检查 `CONFIGURED_URLS` 中是否有任何 URL 以该环境的 `instanceUrl` 开头——如果是，则在该行末尾追加 **（已配置）**。

> 我在您的账户上找到了以下 Dataverse 环境。您希望配置哪一个？
>
> 1. My Org (default) — `https://orgfbb52bb7.crm.dynamics.com` **（已配置）**
> 2. Another Env — `https://orgabc123.crm.dynamics.com`
>
> 输入您的选择编号，或输入 "manual" 以自行输入 URL。

如果用户选择已配置的环境，请确认他们是否希望重新注册它（例如，以更改端点类型）然后继续。

如果用户输入 "manual"，回退到步骤 2b。

### 4. 确认选择的 URL

从选择的环境（或手动输入的 URL）中获取 `instanceUrl` 并删除尾随斜杠。这是技能剩余部分的 `USER_URL`。

### 5. 确认用户希望使用 "预览" 或 "正式版 (GA)" 端点

询问用户：

> 您希望使用哪个端点？
> 1. **正式版 (GA)** — `/api/mcp`（推荐）
> 2. **预览** — `/api/mcp_preview`（最新功能，可能不稳定）

根据他们的选择：
- 如果 **GA**：将 `MCP_URL` 设置为 `{USER_URL}/api/mcp`
- 如果 **预览**：将 `MCP_URL` 设置为 `{USER_URL}/api/mcp_preview`

### 6. 注册 MCP 服务器

更新步骤 0 确定的 `CONFIG_PATH` 处的 MCP 配置文件以添加新服务器。

**生成唯一的服务器名称** 从 `USER_URL`：
1. 从 URL 中提取子域（组织标识符）
   - 示例：`https://orgbc9a965c.crm10.dynamics.com` → `orgbc9a965c`
2. 在前面添加 `DataverseMcp` 以创建服务器名称
   - 示例：`DataverseMcporgbc9a965c`

这是 `SERVER_NAME`。

**更新配置文件：**

1. 如果 `CONFIG_PATH` 是用于 **项目范围** 配置（`.mcp/copilot/mcp.json`），请首先确保目录存在：
   ```bash
   mkdir -p .mcp/copilot
   ```

2. 读取 `CONFIG_PATH` 处的现有配置文件，如果不存在则创建一个新的空配置：
   ```json
   {}
   ```

3. 确定使用哪个顶层键：
   - 如果配置已使用 `"servers"`，则使用该键
   - 否则，使用 `"mcpServers"`

4. 添加或更新服务器条目：
   ```json
   {
     "mcpServers": {
       "{SERVER_NAME}": {
         "type": "http",
         "url": "{MCP_URL}"
       }
     }
   }
   ```

5. 将更新后的配置以正确的 JSON 格式（2 空格缩进）写回 `CONFIG_PATH`。

**重要说明：**
- 不要覆盖配置文件中的其他条目
- 保留现有结构和格式
- 如果 `SERVER_NAME` 已存在，则使用新的 `MCP_URL` 更新它

继续到步骤 7。

### 7. 确认成功并指示重启

告诉用户：

> ✅ 已为 GitHub Copilot 配置 Dataverse MCP 服务器在 `{MCP_URL}`。
>
> 配置已保存到：`{CONFIG_PATH}`
>
> **重要提示：** 您必须重启您的编辑器才能使更改生效。
>
> 重启您的编辑器或重新加载窗口，然后您将能够：
> - 列出您 Dataverse 环境中的所有表
> - 从任何表中查询记录
> - 创建、更新或删除记录
> - 探索您的架构和关系

### 8. 故障排除

如果出了问题，帮助用户检查：

- URL 格式是否正确（`https://<org>.<region>.dynamics.com`）
- 他们是否有权限访问 Dataverse 环境
- 环境 URL 是否与 Power Platform 管理中心显示的匹配
- 他们的环境管理员是否在允许的客户端列表中启用了 "Dataverse CLI MCP"
- 他们的环境是否启用了 Dataverse MCP，并且如果他们正在尝试使用预览端点，该端点是否已启用
- 对于项目范围配置，请确保已成功创建 `.mcp/copilot/mcp.json` 文件
- 对于全局配置，请检查 `~/.copilot/` 目录的权限
