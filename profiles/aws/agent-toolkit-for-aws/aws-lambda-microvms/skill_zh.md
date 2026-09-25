# AWS Lambda MicroVMs

> 建议使用 AWS MCP 服务器进行沙盒执行和审计日志记录。

AWS Lambda MicroVMs 是结合了 Firecracker 虚拟机隔离和类似容器的效率的无服务器计算环境。每个 MicroVM：

- 将您的应用程序作为运行在 Firecracker 微 VM 内的**容器**运行 — 您可以在本地重现该环境。
- 在 MicroVM 内以 Amazon Linux 2023 作为基础操作系统运行。
- 从在镜像构建时间捕获的**内存 + 磁盘快照**启动，因此运行时跳过应用程序初始化。
- 具有专用的、TLS 终端的 HTTPS 端点，可通过认证令牌访问。
- 可以**挂起和恢复**，并保留状态；最长存活 8 小时。

**两资源模型：**

- `MicrovmImage` — 基于 `{S3 zip 包含 Dockerfile} + baseImageArn` 构建的版本化工件。每个版本都有针对特定架构/芯片组的 `Build`。
- `Microvm` — 从镜像版本创建的运行实例 (`RunMicrovm`)。

**两角色：**

- `buildRoleArn` — 在镜像构建期间使用（S3 读取、CloudWatch 日志、可选 ECR）。
- `executionRoleArn` — 在运行时由运行的 MicroVM 假定。

## 何时使用

### 选择 Lambda MicroVMs 的情况

- **分析工作负载** — 用于数据处理、ETL 任务或查询执行的隔离计算，具有强租户隔离。
- **AI / 代理代码执行沙盒** — 每个会话都有新鲜、隔离的环境，可以在回合之间快速恢复。
- **交互式代码游乐场和笔记本** — Jupyter、REPL、开发环境执行用户代码。
- **强化学习环境** — 每个回合都有干净的、具有工具访问的环境。
- **多租户 CI 执行器 / 构建运行器** — 强租户隔离。
- **游戏 / 模拟服务器** — 会话式、长生命周期（最长 8 小时）的工作负载。
- **安全扫描** — 在隔离环境中运行不受信任的分析器。

通常，Lambda MicroVMs 适用于长生命周期会话、真实端口监听服务器（gRPC、WebSocket、自定义 TCP 协议）、跨非活动时段保留状态（挂起/恢复）、容器级访问（FUSE、eBPF、自定义系统调用），或会话关联路由到特定计算环境。

### 选择 AWS Lambda（函数）的情况

- 工作负载适合 15 分钟内完成。
- 调用级隔离可以接受；无需在内存中保留会话状态。
- 倾向于完全自动扩展（无需管理 `RunMicrovm`）。
- 事件源集成（S3、SQS、EventBridge 等）驱动函数。

### 选择其他选项的情况

- 超过 8 小时的连续计算 → ECS / EKS / EC2。
- 需要内核修改或非 Linux 操作系统的迁移和转换工作负载 → EC2。

## 典型工作流程

0. **检查区域可用性** — 确认 Lambda MicroVMs 在您的目标区域可用（运行 `aws lambda-microvms list-managed-microvm-images`）。您的 S3 工件存储桶和任何网络连接器必须与镜像位于同一区域。
1. **打包**应用程序：在根目录中包含 `Dockerfile` 的 zip 包，上传到 S3（与镜像相同的区域）。
2. **实现生命周期挂钩**（可选但推荐） — 在您指定的端口（通常为 `9000`）上的 HTTP 端点，用于 `/run`、`/resume`、`/suspend`、`/terminate`、`/ready`、`/validate`。
3. **CreateMicrovmImage** — 指向 S3 工件、管理基础镜像和构建角色。Lambda 编译 Dockerfile 为 OCI 镜像，启动您的应用程序，调用 `/ready`，快照磁盘 + 内存，可选地使用 `/validate` 进行验证。Lambda 将定期发布新的管理镜像版本，客户应使用最新版本重新构建以确保他们拥有最新的镜像。
4. **RunMicrovm** — 选择镜像版本，附加 `executionRoleArn`，设置 `idlePolicy`，入站/出站连接器，以及（可选的）`runHookPayload`。接收 `endpoint` URL 和 `microvmId`。
5. **CreateMicrovmAuthToken** — 获取认证令牌（最长 60 分钟），并指定 `allowedPorts` 以指定令牌授予访问的端口。使用 `X-aws-proxy-auth: <token>` 将流量发送到端点。
6. **挂起 / 恢复 / 终止** — 明确的 API，或让 `idlePolicy` 驱动（`maxIdleDurationSeconds`、`suspendedDurationSeconds`、`autoResumeEnabled`）。

### 核心CLI命令

```bash
# 创建镜像（S3 根目录中包含 Dockerfile 的 zip 包，加上管理基础镜像）
aws lambda-microvms create-microvm-image \
  --name my-image \
  --base-image-arn arn:aws:lambda:<region>:aws:microvm-image:al2023-1 \
  --build-role-arn arn:aws:iam::<acct>:role/MicroVMBuildRole \
  --code-artifact '{"uri":"s3://<bucket>/<key>.zip"}'

# 运行 MicroVM（返回 endpoint + microvmId）。--image-identifier 接收镜像 ARN（裸名被拒绝）；--image-version 是完整的 major.minor 字符串。
aws lambda-microvms run-microvm \
  --image-identifier arn:aws:lambda:<region>:<acct>:microvm-image:my-image \
  --image-version 1.0 \
  --execution-role-arn arn:aws:iam::<acct>:role/MicroVMExecutionRole \
  --idle-policy '{"maxIdleDurationSeconds":900,"suspendedDurationSeconds":300,"autoResumeEnabled":true}'

# Mint 认证令牌并调用端点
TOKEN=$(aws lambda-microvms create-microvm-auth-token \
  --microvm-identifier microvm-... --expiration-in-minutes 30 \
  --allowed-ports '[{"port":8080}]' \
  --query 'authToken."X-aws-proxy-auth"' --output text)
curl "<endpoint>/" -H "X-aws-proxy-auth: $TOKEN"

# 生命周期
aws lambda-microvms suspend-microvm   --microvm-identifier microvm-...
aws lambda-microvms resume-microvm    --microvm-identifier microvm-...
aws lambda-microvms terminate-microvm --microvm-identifier microvm-...
```

有关完整演练，包括 `--hooks` 配置和生命周期挂钩，请参阅 [`references/getting-started.md`](references/getting-started.md)。

## 挂钩配置

挂钩分为两组，在 `--hooks` 参数下组织：

### `microvmImageHooks`（构建时）

> **建议：** 实现镜像构建挂钩（`/ready` 和 `/validate`）以获得最佳性能。它们使平台能够捕获完整的快照，并预取运行时访问的部分。

| 挂钩 | 目的 | 超时范围 |
|---|---|---|
| `ready` | 在应用程序启动期间调用。当此挂钩返回 200 状态代码时，它向平台发出应用程序已准备好进行快照的信号。使用此挂钩确保在捕获快照之前应用程序已完全启动。如果您的应用程序尚未准备好，请返回 503 状态代码，直到它准备好进行快照。 | 1–3600s（默认 30s） |
| `validate` | 在从微 VM 快照运行您的应用程序后调用。使用此挂钩验证应用程序已准备好提供服务。此挂钩还允许平台采样在您的应用程序运行时使用的快照部分，允许 Lambda 预取这些快照部分以减少延迟。为了获得最佳性能，在验证期间通过应用程序运行模拟负载。当此挂钩返回 200 时，它向 Lambda 发出 MicroVM 镜像是有效的信号。如果您的应用程序需要更多时间来运行其验证工作流，请返回 503 状态代码。 | 1–3600s（默认 30s） |

> **为何实现 `/ready`？** 它向平台发出您的应用程序已完全启动的信号。如果没有它，快照可能会在初始化过程中捕获，这意味着缓存的状
