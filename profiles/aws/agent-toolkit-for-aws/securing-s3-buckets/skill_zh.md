## 概述

实现跨五个工作流的分层 S3 安全控制：保护新存储桶、审计现有配置、修复问题、配置加密和启用监控。遵循 AWS Well-Architected 安全最佳实践。

连接时使用 AWS MCP 服务器执行命令（沙盒执行、审计日志记录、可观察性）。否则，回退到 AWS CLI 或 shell。

## 常见任务

### 0. 验证依赖项

开始前检查所需工具。

**约束条件：**

- 您必须在使用前告知用户所需工具缺失
- 您应该使用 `aws sts get-caller-identity` 确认凭证

有关工作流的 IAM 权限，请参阅 [references/iam-permissions.md](references/iam-permissions.md)。

### 1. 分类请求

| 用户意图 | 工作流 |
|---|---|
| 保护新存储桶 | A：保护新存储桶 |
| 审计/审查现有存储桶 | B：审计现有存储桶 |
| 修复特定问题 | C：修复问题 |
| 配置加密 | D：配置加密 |
| 启用日志记录/监控 | E：启用监控 |

**约束条件：**

- 您必须提前请求所有所需参数
- 您必须在任何写入操作之前确认存储桶名称和区域
- 如果用户明确说明，您可以从用户上下文中推断区域
- 您应该在写入操作前运行 `aws iam simulate-principal-policy` 以验证权限
- 您应该在执行前显示写入命令并等待确认

### put-bucket-policy 安全规则

这些规则适用于所有调用 `put-bucket-policy` 的工作流：

- 您必须首先尝试检索现有策略（`aws s3api get-bucket-policy`）— `put-bucket-policy` 会替换整个策略
- 如果存在策略，您必须在修改前备份它：`aws s3api get-bucket-policy --bucket <name> --output text > backup-policy-$(date +%s).json`
- 如果返回 `NoSuchBucketPolicy`，则继续使用新策略 — 无需备份
- 您必须将新声明合并到现有策略的 Statement 数组中（如果存在）
- 您必须在应用前验证合并的 JSON 语法（例如 `echo '<policy>' | python3 -m json.tool`）
- 您应该显示完整的 `put-bucket-policy` 命令并等待确认

### 2. 工作流 A — 保护新存储桶

有关完整 CLI 步骤，请参阅 [references/workflows.md](references/workflows.md)。

**必需步骤（按顺序执行，不得跳过）：**

1. 使用 `--bucket-namespace account-regional` 创建存储桶
2. 启用版本控制
3. 启用加密（SSE-S3 + 存储桶密钥 + 阻止 SSE-C）
4. 启用日志记录（询问用户选项 — 条件性）
5. 通过 `DenyInsecureTransport` 存储桶策略强制执行 HTTPS 仅
6. 启用 ABAC

**约束条件：**

- 您必须在 `create-bucket` 调用中传递 `--bucket-namespace account-regional` — 这是必需的，不是可选的。示例：

  ```
  aws s3api create-bucket --bucket <name> --bucket-namespace account-regional --region <region>
  ```

- 您不得更改阻止公共访问 — S3 默认在新存储桶上启用它
- 您不得更改 ACL 所有权控制 — S3 默认禁用 ACLs（`BucketOwnerEnforced`）
- 您必须应用一个带有 `DenyInsecureTransport` 声明的存储桶策略，该声明在 `aws:SecureTransport` 为 `false` 时拒绝 `s3:*` — 这是必需的，不是可选的。示例：

  ```
  aws s3api put-bucket-policy --bucket <name> --policy '{"Version":"2012-10-17","Statement":[{"Sid":"DenyInsecureTransport","Effect":"Deny","Principal":"*","Action":"s3:*","Resource":["arn:aws:s3:::<name>/*","arn:aws:s3:::<name>"],"Condition":{"Bool":{"aws:SecureTransport":"false"}}}]}'
  ```

- 您必须在第 4 步之前询问用户他们想要哪个日志记录选项
- 您必须遵循 [put-bucket-policy 安全规则](#put-bucket-policy-safety-rules) 来执行第 4 步和第 5 步
- 您应该在继续之前确认每一步是否成功

### 3. 工作流 B — 审计现有存储桶

有关完整清单，请参阅 [references/audit-checklist.md](references/audit-checklist.md)。

**约束条件：**

- 您必须在报告发现前运行所有只读审计命令
- 您在审计期间不得执行任何写入或修改命令
- 您必须以严重性报告每个控制项为 PASS / FAIL / 未配置
- 对于日志记录：如果 S3 服务器访问日志记录或 CloudTrail 数据事件已启用，则报告 PASS；如果两者都未启用，则报告未配置

### 4. 工作流 C — 修复问题

有关按问题类型修复命令，请参阅 [references/remediation.md](references/remediation.md)。

**约束条件：**

- 您必须在应用任何修复前识别问题类型
- 您在修改策略时必须遵循 [put-bucket-policy 安全规则](#put-bucket-policy-safety-rules)
- 您必须在应用修复后重新运行相关审计检查以确认问题已解决

### 5. 工作流 D — 配置加密

有关加密选项和命令，请参阅 [references/encryption.md](references/encryption.md)。

**约束条件：**

- 您必须默认使用 SSE-S3 并启用 S3 存储桶密钥，同时阻止 SSE-C，除非用户明确要求 KMS
- 使用 SSE-KMS 时，您必须使用客户管理的密钥 — 绝不使用 AWS 管理的 `aws/s3` 密钥
- 您必须通过完整 ARN 而不是别名指定客户管理的 KMS 密钥
- 您必须在所有配置中包含 `BucketKeyEnabled: true` 和 `BlockedEncryptionTypes: [SSE-C]`
- **注意**：S3 API 接受 `aws/s3` 和别名而不报错 — 代理强制执行的约束。应用后通过 `get-bucket-encryption` 验证。

### 6. 工作流 E — 启用监控

有关完整 CLI 步骤，请参阅 [references/workflows.md](references/workflows.md)。

**约束条件：**

- 您必须在创建之前检查是否已存在 GuardDuty 探测器
- 您必须使用跟踪的主区域（而不是存储桶的区域）执行 CloudTrail 命令
- 您应该启用所有四个核心推荐 AWS Config 规则

## 故障排除

**`ObjectLockConfigurationNotFoundError`** — 对象锁定未启用。视为未配置，不是失败。

**审计命令上的 `AccessDenied`** — 检查 IAM 策略、存储桶策略、阻止公共访问、VPC 端点策略以及 SCPs/RCPs。使用 `aws iam simulate-principal-policy` 进行诊断。

**`put-bucket-policy` 静默移除现有声明** — 请参阅 [put-bucket-policy 安全规则](#put-bucket-policy-safety-rules)。

**GuardDuty `BadRequestException: detector already exists`** — 首先运行 `aws guardduty list-detectors`；如果为空，才调用 `create-detector`。

**CloudTrail 更改未生效** — 验证您是否使用 `--region <trail-home-region>`，而不是存储桶的区域。使用 `aws cloudtrail describe-trails --query 'trailList[*].[Name,HomeRegion]'` 找到它。

## 其他资源

- [references/iam-permissions.md](references/iam-permissions.md) — 按工作流的 IAM 权限
- [references/audit-checklist.md](references/audit-checklist.md) — 每个控制的清单，包括严重性和通过条件
- [references/encryption.md](references/encryption.md) — 加密选项、KMS 指导、SSE-C 阻止
- [references/remediation.md](references/remediation.md) — 常见发现的修复命令
- [references/workflows.md](references/workflows.md) — 工作流 A 和 E 的完整 CLI 命令序列
- [AWS S3 安全最佳实践](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html)
- [AWS Well-Architected 安全支柱](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html)
