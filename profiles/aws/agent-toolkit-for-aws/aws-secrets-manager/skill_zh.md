# 使用代理安全地处理密钥

## 概述

当 AI 代理处理密钥、凭证、API 密钥、令牌或密码，并使用 shell 或 AWS API 访问时，它们可以调用 `aws secretsmanager get-secret-value` 并在其上下文窗口中接收明文值。这会带来风险：密钥可能会泄露到日志、会话历史记录或下游工具调用中。

本技能教授一种更安全的模式：**动态引用**，由包装脚本 (`asm-exec`) 在运行时解析，因此代理永远不会看到密钥值。

> **尽力防御，而非安全边界。** 这可以防止最常见的泄露路径，但无法阻止所有规避向量。结合 IAM 最小权限、CloudTrail 监控和 VPC 端点策略。

## 规则

在处理密钥时，你必须遵循以下规则：

1. **不得调用 `get-secret-value` 或 `batch-get-secret-value`** -- 不论是通过 AWS CLI、SDK、MCP 工具、curl 或任何其他机制。
2. **不得尝试直接从 Secrets Manager 代理 (SMA) 守护进程读取密钥值** (localhost:2773 或任何回环变体)。
3. **必须使用 `{{resolve:secretsmanager:...}}` 引用** -- 这些引用由 `asm-exec` 在运行时解析，而不会将值暴露给你。

## `{{resolve:...}}` 语法

```
{{resolve:secretsmanager:<secret-id>:<field-type>:<json-key>:<version-stage>}}
```

| 组件 | 是否必需 | 默认值 | 示例 |
|------|----------|--------|------|
| `secret-id` | 是 | -- | `prod/db-creds` 或完整 ARN |
| `field-type` | 否 | `SecretString` | `SecretString` |
| `json-key` | 否 | (完整值) | `password` |
| `version-stage` | 否 | `AWSCURRENT` | `AWSPENDING` |

## 使用 `asm-exec`

`asm-exec` 是一个包装器，用于在命令参数和环境变量中解析 `{{resolve:...}}` 引用，然后执行目标命令。密钥值仅存在于子进程中 -- 永远不会出现在代理的上下文中。

### 用法

```bash
# 将数据库密码传递给 psql 而不暴露它
asm-exec -- psql \
  "host=mydb.example.com \
   user={{resolve:secretsmanager:prod/db-creds:SecretString:username}} \
   password={{resolve:secretsmanager:prod/db-creds:SecretString:password}}" \
  -c "SELECT * FROM users LIMIT 10"

# 使用默认字段类型 (SecretString) 和完整值 (无 json-key)
asm-exec -- curl -H "Authorization: Bearer {{resolve:secretsmanager:prod/api-token}}" \
  https://api.example.com/data

# 在一个命令中使用多个密钥
asm-exec -- mysql \
  -h {{resolve:secretsmanager:prod/mysql:SecretString:host}} \
  -u {{resolve:secretsmanager:prod/mysql:SecretString:username}} \
  -p{{resolve:secretsmanager:prod/mysql:SecretString:password}} \
  -e "SHOW TABLES"
```

### 工作原理

1. 扫描所有命令参数以查找 `{{resolve:...}}` 模式
2. 按顺序通过第一个可用的后端解析每个引用：
   1. **AWS Secrets Manager 代理 (SMA)** 在 localhost:2773 (零延迟、缓存)
   2. **AWS MCP 端点** (`https://aws-mcp.us-east-1.api.aws/mcp`)，通过 SigV4 签名的请求调用 `aws___run_script` 工具 (该工具运行一个简短的服务器端 Python 脚本，通过 `call_boto3` 获取密钥)
   3. 从 ARN 的区域段确定密钥的区域，或从 `AWS_REGION` / `AWS_DEFAULT_REGION` 获取区域，并将其传递给解析器
3. 使用 `re.sub` 替换解析后的值，使用可调用的单次扫描 -- 如果密钥值包含 `{{resolve:...}}`，则防止重新扫描注入
4. 通过 `subprocess.run` 运行目标命令 -- 密钥值仅存在于 asm-exec 进程中，永远不会出现在代理的上下文窗口中

> **没有本地 AWS CLI 回退用于解析。** `asm-exec` 不会 shell 到 `aws secretsmanager get-secret-value` 来解析引用。解析仅通过 SMA 或 MCP 端点发生，因此明文值永远不会写入本地进程的 stdout，从而可能被捕获。

### SigV4 签名

MCP 端点使用 AWS SigV4 对每个工具调用进行身份验证。`asm-exec` 使用 Python 标准库 (`hashlib`/`hmac`) 自行签名请求 -- 它**不**依赖于 botocore 或启动 `mcp-proxy-for-aws-cli` 代理，从而保持包装器为轻量级临时进程。签名服务和区域从端点主机名推断 (例如 `aws-mcp.us-east-1.api.aws` -> 服务 `aws-mcp`，区域 `us-east-1`)；此签名区域独立于密钥自身的区域，作为 `region_name` 参数传递给服务器端的 `call_boto3` 调用。

签名凭证按顺序解析：环境变量 (`AWS_ACCESS_KEY_ID` 等)、`aws configure export-credentials` (AWS CLI v2)、然后 `aws configure get` (AWS CLI v1)。

### 前置条件

必须可以访问其中一个后端，并且凭证具有 `secretsmanager:GetSecretValue` 权限：

- **AWS Secrets Manager 代理 (SMA)** 在 localhost:2773 上运行，OR
- **AWS 凭证** 可用于 MCP 端点的 SigV4 签名 (见上文)。对于跨区域密钥，设置 `AWS_REGION` (或使用完整 ARN) 以目标正确区域。

参见 [SMA 设置指南](https://docs.aws.amazon.com/secretsmanager/latest/userguide/secrets-manager-agent.html)。

## 常见模式

### 数据库连接

```bash
asm-exec -- psql "postgresql://{{resolve:secretsmanager:prod/db:SecretString:username}}:{{resolve:secretsmanager:prod/db:SecretString:password}}@db.example.com:5432/mydb"
```

### Docker 与密钥

```bash
asm-exec -- docker run -e "DB_PASSWORD={{resolve:secretsmanager:prod/db:SecretString:password}}" myapp:latest
```

### 配置文件模板

```bash
# 使用解析后的密钥生成配置，写入文件
asm-exec -- sh -c 'echo "password={{resolve:secretsmanager:app/db:SecretString:password}}" > /tmp/app.conf'
```

## 结构强制执行 (插件钩子)

当 `aws-core` 插件启用时，`PreToolUse` 钩子会自动阻止任何尝试调用 `get-secret-value` 或 `batch-get-secret-value` -- 不论是通过 AWS CLI、MCP 工具或直接 SMA 访问。无需手动配置。

钩子定义在 `plugins/aws-core/com.anthropic.claude-code/hooks/hooks.json` 中，并在插件安装时自动激活。

## 故障排除

### "密钥未找到" 错误

验证密钥是否存在，并且你的 IAM 角色具有 `secretsmanager:GetSecretValue` 权限。检查密钥名称是否完全匹配 (区分大小写)。

### SMA 连接被拒绝

Secrets Manager 代理可能未运行。这不是致命的：`asm-exec` 会回退到 SigV4 签名的 MCP 端点。确保 AWS 凭证可解析 (见 SigV4 签名上文)，以便后端可以身份验证。

### "解析失败" 错误

两个后端都不可达或返回无值。当 MCP 解析失败时，`asm-exec` 会将具体原因打印到 stderr (`asm-exec: MCP 解析失败: ...`) -- 超时、无法到达端点、HTTP 状态码、拒绝权限或缺失值 -- 因此首先读取该行。检查 SMA 是否运行或 AWS 凭证是否有效 (`aws sts get-caller-identity`)，密钥的区域是否正确 (设置 `AWS_REGION` 或使用完整 ARN)，以及你的身份是否对密钥具有 `secretsmanager:GetSecretValue` 权限。来自 MCP 端点的 `401` 表示 SigV4 签名或凭证问题，而不是缺失密钥。如果失败是超时，服务器端调用可能需要比默认 30 秒更长时间 -- 使用 `ASM_EXEC_MCP_TIMEOUT` (秒) 调整它。

### 解析产生空字符串

JSON 键可能不存在于密钥值中。验证 AWS 控制台中的密钥结构或询问密钥所有者确认可用的键。
