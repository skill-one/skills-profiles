# AWS DevOps Agent — Claude 设置

以下说明专门用于为 Claude 应用设置 AWS DevOps Agent 插件。对于其他客户端，请以此作为参考，但根据客户端的具体要求调整说明。

## 第 0 步：检查是否需要设置

1/ 检查 "aws-devops-agent" MCP 服务器是否正在运行。如果正在运行，请验证其是否具有有效连接（见“第 3 步：验证连接”）。

如果验证成功，您应告知用户插件已设置，使用 `SigV4 或 Bearer Token`。提供您可以将配置切换为 `Bearer Token 或 SigV4` 的选项，详情见“第 2 步：决定认证路径”下方说明。

如果用户不想更改其认证配置，则您已完成，停止操作。

2/ 检查以下位置是否存在带有键 "aws-devops-agent" 的 MCP 服务器配置：

- 插件作用域：`${CLAUDE_PLUGIN_ROOT}/.mcp.json`
- 项目作用域：.mcp.json（在您的项目目录中，受版本控制）
- 项目特定：.claude/settings.local.json（在您的项目目录中）
- 用户特定本地：~/.claude/settings.local.json
- 用户特定全局：~/.claude/settings.json
- 主 Claude.json：~/.claude.json
- 专用 MCP 文件：~/.claude/mcp_servers.json

然后：

- 如果 `aws-devops-agent` 键存在 **且** 服务器已连接（工具可用，见“第 3 步：验证连接”）→ 告知用户："DevOps Agent 已配置并连接。" 如果 MCP 配置中使用 Bearer Token，建议您可以另选设置插件以使用 AWS DevOps Agent 的 SigV4 凭证（多个 Agent 空间，管理工具）。如果 MCP 配置中使用 SigV4 凭证，建议您可以另选设置插件以使用 Bearer Token 凭证为 AWS DevOps Agent（单个 Agent 空间）。
- 如果 `aws-devops-agent` 键存在但失败 → 继续执行“第 1 步：诊断当前状态”
- 如果 `aws-devops-agent` 键不存在 → 继续执行“第 1 步：诊断当前状态”

---

## 第 1 步：诊断当前状态

运行以下检查：

```bash
# Bearer token
echo "DEVOPS_AGENT_TOKEN: $([ -n "$DEVOPS_AGENT_TOKEN" ] && echo '已设置' || echo '未设置')"
echo "DEVOPS_AGENT_REGION: ${DEVOPS_AGENT_REGION:-未设置}"

# SigV4 依赖项
uvx --version 2>&1

# AWS 凭证
aws sts get-caller-identity 2>&1
```

确定：

- `bearer_ready` = `DEVOPS_AGENT_TOKEN` 已设置 **且** `DEVOPS_AGENT_REGION` 已设置
- `sigv4_ready` = `aws sts get-caller-identity` 成功 **且** `uvx` 已安装

---

## 第 2 步：决定认证路径

诊断后，**始终**询问用户他们希望选择哪个路径，即使只有一个可用。展示您发现的内容并让他们选择。

如果用户只能访问 Agent 空间的操作员应用，他们可能希望使用 Bearer Token。

如果他们使用多个 Agent 空间和/或具有管理 Agent 空间的管理员权限，他们可能希望使用 SigV4。

| Bearer ready | SigV4 ready | 操作 |
|:---:|:---:|--------|
| 是 | 是 | "您同时配置了 Bearer Token 和 AWS 凭证。您希望为 DevOps Agent 选择哪个？**Bearer Token**（单个 Agent 空间）或 **AWS 凭证 / SigV4**（多个 Agent 空间和管理工具）？" |
| 是 | 否 | "您配置了 Bearer Token。您希望我使用您的 **Bearer Token**（单个 Agent 空间）设置 DevOps Agent 吗？还是您希望配置 **AWS 凭证 / SigV4** 而不是（多个 Agent 空间和管理工具）？" |
| 否 | 是 | "您具有有效的 AWS 凭证。您希望我使用 **SigV4**（多个 Agent 空间和管理工具）设置 DevOps Agent 吗？还是您希望另选设置 **Bearer Token**（单个 Agent 空间）？" |
| 否 | 否 | "既未配置 Bearer Token 也未配置 AWS 凭证。您希望通过 **Bearer Token**（单个 Agent 空间）连接还是通过 **AWS 凭证 / SigV4**（多个 Agent 空间和管理工具）连接？然后指导他们完成所选路径。" |

如果用户希望设置 Bearer Token，请将其引导至 AWS 文档中的 [连接到 DevOps Agent 远程服务器](https://docs.aws.amazon.com/devopsagent/latest/userguide/accessing-devops-agent-connect-to-devops-agent-remote-servers.html#create-an-access-token) 或引导他们根据本文档中的步骤创建访问令牌。

**在用户确认其选择之前，不要继续进行第 3 步。**

---

## 第 3 步：验证连接

如果 "aws-devops-agent" MCP 服务器已正在运行，请检查您是否可以列出工具。如果可以，则已验证连接。

否则，继续操作。

在写入 `.mcp.json` 之前验证。这确认凭据对实时端点有效。或者使用此方法验证现有的 MCP 服务器配置。

### Bearer 验证

```bash
curl -s -w "\nHTTP_STATUS: %{http_code}" \
  -X POST \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $DEVOPS_AGENT_TOKEN" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' \
  "https://connect.aidevops.${DEVOPS_AGENT_REGION}.api.aws/mcp"
```

| 结果 | 含义 | 操作 |
|--------|---------|--------|
| HTTP 200 + `result.tools` 数组 | 成功 | 继续进行第 4 步 |
| HTTP 401 | 令牌无效或过期 | 告知用户在操作员 Web 应用中创建新令牌 |
| HTTP 403 | 令牌范围不足 | 告知用户令牌需要 `agent:read` + `agent:operate` 范围 |
| 连接拒绝 / 超时 | 端点无法访问 | 如果 SigV4 可用，提供回退。否则报告不可用。 |

### SigV4 验证

```bash
timeout 30 bash -c '
{
echo "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"initialize\",\"params\":{\"protocolVersion\":\"2024-11-05\",\"capabilities\":{},\"clientInfo\":{\"name\":\"setup-check\",\"version\":\"1.0\"}}}"
sleep 0.5
echo "{\"jsonrpc\":\"2.0\",\"method\":\"notifications/initialized\"}"
sleep 0.5
echo "{\"jsonrpc\":\"2.0\",\"id\":2,\"method\":\"tools/list\",\"params\":{}}"
sleep 8
} | uvx mcp-proxy-for-aws-cli@latest "https://connect.aidevops.${DEVOPS_AGENT_REGION}.api.aws/mcp" --service aidevops --region "$DEVOPS_AGENT_REGION"
'
```

> **注意：** 第一次运行可能需要 10-15 秒，因为 `uvx` 下载 `mcp-proxy-for-aws-cli` 及其依赖项。后续运行几乎即时。

| 结果 | 含义 | 操作 |
|--------|---------|--------|
| 第二行包含 `result.tools` | 成功 | 继续进行第 4 步 |
| 无输出 / 超时 | 凭证无效或端点无法访问 | 再次检查 `aws sts get-caller-identity` |
| `ExpiredTokenException` 在 stderr | AWS 会话凭证过期 | 告知用户重新认证（`aws sso login` 或刷新凭证） |
| `AccessDeniedException` | 缺少 IAM 权限 | 用户需要在其角色上具有 DevOps Agent 权限 |

---

## 第 4 步：确认并写入 `.mcp.json`

写入前，请与用户确认：

> "我已验证连接。我将添加 **[Bearer Token / SigV4]** MCP 服务器到插件的 `.mcp.json`。继续吗？"

只有在用户确认后才能写入。写入一个服务器条目——永远不要同时写入。在 `${CLAUDE_PLUGIN_ROOT}/.mcp.json` 中安装 MCP 配置。您也可以提供在工作区级别安装 MCP 服务器的选项。安装选项为：

- 插件作用域：`${CLAUDE_PLUGIN_ROOT}/.mcp.json`（默认）
- 项目作用域：.mcp.json（在您的项目目录中，受版本控制）
- 项目特定：.claude/settings.local.json（在您的项目目录中）

### Bearer 配置

```json
{
  "mcpServers": {
    "aws-devops-agent": {
      "type": "http",
      "url": "https://connect.aidevops.${DEVOPS_AGENT_REGION}.api.aws/mcp",
      "headers": {
        "Authorization": "Bearer ${DEVOPS_AGENT_TOKEN}"
      },
      "timeout": 120000
    }
  }
}
```

### SigV4 配置

将 `<REGION>` 替换为用户的实际区域：

```json
{
  "mcpServers": {
    "aws-devops-agent": {
      "command": "uvx",
      "timeout": 120000,
      "args": [
        "mcp-proxy-for-aws-cli@latest",
        "https://connect.aidevops.<REGION>.api.aws/mcp",
        "--service", "aidevops",
        "--region", "<REGION>"
      ]
    }
  }
}
```

### 回退（aws-mcp）

仅在主要 `aws-devops-agent` 端点无法访问 **且** SigV4 凭证可用时添加：

```json
{
  "mcpServers": {
    "aws-mcp": {
      "command": "uvx",
      "timeout": 100000,
      "args": [
        "mcp-proxy-for-aws-cli@latest",
        "https://aws-mcp.us-east-1.api.aws/mcp",
        "--metadata",
        "AWS_REGION=us-east-1"
      ]
    }
  }
}
```

对于 Sigv4 仅：写入新的 MCP 配置后，告知用户 MCP 服务器已成功写入。继续到下一步。

---

## 第 5 步：多空间路由（仅 SigV4）

成功设置 SigV4 后，发现并配置 AgentSpace 路由：

1. 通过新连接的 MCP 调用 `list_agent_spaces` 以发现可用空间
2. 将列表展示给用户
3. 如果存在多个空间，将路由指南写入 `.claude/aws-agents-for-devsecops.md`：

```markdown
# AWS DevOps Agent — 路由指南

| 空间 | Agent Space ID | 用途 |
|-------|----------------|---------|
| <名称> | <ID> | <询问用户> |
```

1. 指导：在针对特定空间时，每次调用工具时传递 `agent_space_id`。

---

## 第 6 步：重新加载插件

告知用户他们需要运行 `/reload-plugins` 来启动新的 MCP 服务器。您可能需要提示用户运行它。同时提及在重新启动 MCP 服务器后，他们应尝试以下提示：

- 设置多空间路由（仅 SigV4）
- <从 ${CLAUDE_PLUGIN_ROOT}/README.md 列出技能和提示建议>

---

## Bearer 令牌指导（需要创建令牌的用户）

1. 打开您的 AgentSpace 的 AWS DevOps Agent **操作员 Web 应用**
2. 导航到 **设置 → 访问令牌 → 生成令牌**
3. 创建一个具有权限 **`Operate`** 的令牌
4. 设置环境变量：

   ```bash
   export DEVOPS_AGENT_TOKEN="<your-token>"
   export DEVOPS_AGENT_REGION="<your-region>"
   ```

   可用区域：https://docs.aws.amazon.com/devopsagent/latest/userguide/about-aws-devops-agent-supported-regions.html
5. 重新启动 Claude Code（它从启动它的 shell 读取环境变量）

> **重要：** 没有 `Operate` 权限，`chat` 和 `investigate` 工具将完全不可见——不仅会失败，而且会从工具列表中消失。

---

## SigV4 指导（需要配置 AWS 凭证的用户）

1. 如果尚未安装，请安装 `uvx`：
   - macOS: `brew install uv`
   - Linux: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. 配置 AWS 凭证：

   ```bash
   aws configure sso --profile devops-agent
   aws sso login --profile devops-agent
   export AWS_PROFILE=devops-agent
   ```

3. 设置区域：

   ```bash
   export DEVOPS_AGENT_REGION="<your-region>"
   ```

4. 验证：`aws sts get-caller-identity`
5. IAM 角色必须具有 DevOps Agent 权限（例如，具有 aidevops 访问的托管策略）

> **重要：** 使用 SigV4 时，请取消设置 `DEVOPS_AGENT_TOKEN`。如果两者都设置，客户端可能会尝试 Bearer 认证而不是签名代理。

---

## 故障排除

| 错误 | 原因 | 修复 |
|-------|-------|-----|
| 无工具可见 | 令牌未设置或未重新启动 Claude Code | 设置 `DEVOPS_AGENT_TOKEN` + `DEVOPS_AGENT_REGION`，重新启动 |
| HTTP 401 | 令牌无效/过期 | 在操作员 Web 应用中创建新令牌 |
| `chat`/`investigate` 缺失 | 令牌范围仅为 `agent:read` | 创建具有 `agent:operate` 范围的令牌 |
| 连接拒绝 / 超时 | 端点无法访问 | 检查网络；如果 SigV4 可用，提供 `aws-mcp` 回退 |
| `ExpiredTokenException` | AWS 会话凭证过期 | `aws sso login` 或刷新凭证 |
| `AccessDeniedException`（SigV4） | 缺少 IAM 权限 | 使用具有 DevOps Agent 访问的角色 |
| 代理不会启动 | 未安装 `uvx` | `brew install uv`（macOS）或按平台安装 |
| 工具可见但调用超时 | 正常，`chat`（5-30 秒） | 确保 `"timeout": 120000` 在 mcp.json 中 |
