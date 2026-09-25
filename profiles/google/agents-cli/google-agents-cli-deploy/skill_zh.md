# 部署指南

> **要求：** `agents-cli` (`uv tool install google-agents-cli`) — 如果需要，请先安装 uv：[安装 uv](https://docs.astral.sh/uv/getting-started/installation/index.md)。
>
> 在本指南中，请尽量使用 `agents-cli` 命令 — 它们将 Terraform、Docker 和部署封装为一个经过测试的管道。如果你的项目尚未构建，请查看 `/google-agents-cli-scaffold` 首先添加部署支持。

### 参考文件

有关更详细的信息，请参阅 `references/` 中的以下参考文件：

- **`cloud-run.md`** — 扩展默认值、Dockerfile、会话类型、网络
- **`agent-runtime.md`** — 基于容器的部署、统一的 FastAPI 应用、`/api` 转发、Terraform 资源、部署元数据、CI/CD 差异
- **`gke.md`** — GKE Autopilot 集群、Kubernetes 配置文件、工作负载身份、会话类型、网络
- **`terraform-patterns.md`** — 自定义基础设施、IAM、状态管理、导入资源
- **`batch-inference.md`** — BigQuery 远程函数触发；有关 ADK 上的 Pub/Sub / Eventarc，请查看 `/google-agents-cli-adk-code`
- **`cicd-pipeline.md`** — 完整的 CI/CD 管道设置、`infra cicd` 标志、运行器比较、WIF 身份验证、管道阶段
- **`testing-deployed-agents.md`** — 按部署目标测试说明、curl 示例、负载测试

> **可观察性：** 请参阅 `/google-agents-cli-observability` 技能，了解 Cloud Trace、提示-响应日志记录、BigQuery 分析和第三方集成。

---

## 部署目标决策矩阵

根据你的需求选择正确的部署目标：

| 标准 | Agent Runtime | Cloud Run | GKE |
|------|-------------|-----------|-----|
| **扩展** | 管理的自动扩展（可配置的最小/最大值、并发性） | 完全可配置（最小/最大实例数、并发性、CPU 分配） | 完整的 Kubernetes 扩展（HPA、VPA、节点自动配置） |
| **网络** | 支持 VPC-SC 和 PSC-I（通过网络附加组件实现私有 VPC 连接） | 完全支持 VPC，直接 VPC 出站，IAP，入站规则 | 完整的 Kubernetes 网络 |
| **会话状态** | 管理的 Agent Engine 会话（ADK 自动连接 `VertexAiSessionService`） | 内存（开发）、Cloud SQL 或 Agent Platform 会话后端 | 内存（开发）、Cloud SQL 或 Agent Platform 会话后端 |
| **批处理/事件处理** | 可达的触发端点（通过 Agent Engine `/api` 转发） | 原生触发端点（Pub/Sub、Eventarc）；ADK：请查看 `/google-agents-cli-adk-code` | 自定义（Kubernetes Jobs、Pub/Sub） |
| **成本模型** | vCPU 小时 + 内存小时（空闲时不计费） | 每实例-秒 + 最小实例成本 | 节点池成本（始终开启或自动配置） |
| **设置复杂性** | 较低（管理型、专为代理设计） | 中等（Dockerfile、Terraform、网络） | 较高（需要 Kubernetes 专业知识） |
| **最适合** | 管理型基础设施、最小运维 | 自定义基础设施、完全网络控制 | 完全 Kubernetes 控制 |

**询问用户** 哪个部署目标适合他们的需求。每个都是有效的生产选择，具有不同的权衡。

所有三个目标都是基于容器的，因此任何语言都可以使用。

> **产品名称映射：** "Agent Engine" / "Vertex AI Agent Engine" 现在是 **Agent Runtime**。使用 `--deployment-target agent_runtime`。

> **环境/计划/事件驱动代理（ADK 项目）：** ADK 的 `trigger_sources` 在相同的 FastAPI 应用上注册 `/apps/{app}/trigger/*` 端点，用于 **所有** 目标。在 **Cloud Run** / **GKE** 中，这些是公开的 HTTP 路由，你可以指向 Pub/Sub 推送订阅或 Eventarc 触发器；在 **Agent Runtime** 中，相同的路由可以通过 Agent Engine `/api` 转发（例如 `.../reasoningEngines/v1/{resource}/api/apps/{app}/trigger/pubsub`）。Cloud Run 仍然是未经身份验证触发源的最简单目标。有关 `trigger_sources` 模式的详细信息，请查看 `/google-agents-cli-adk-code` (`references/adk-python.md`，部分 "12. Event-Driven / Ambient Agents")。

> **OAuth / 用户同意代理：** 使用 **Agent Runtime** 和 Gemini Enterprise 为需要 OAuth 2.0 用户同意的代理（例如访问 Google Drive、日历或其他用户范围 API），Cloud Run 目前不支持管理的 OAuth 流。有关 ADK 工作示例，请在 `/google-agents-cli-adk-code` 中的主题索引中查找 OAuth 用户同意 → `references/samples.md`。

---

## 部署到开发环境

### 部署工作流

**任务跟踪：** 部署涉及多个顺序步骤（基础设施设置、CI/CD 配置、部署、验证）。使用任务列表跟踪这些步骤的进度 — 跳过其中一个步骤通常会导致后续步骤失败且难以追溯。

1. 如果是原型（没有部署目标），首先增强：`agents-cli scaffold enhance . --deployment-target <target>`
2. **通知人类**：粘贴评估分数和测试结果，然后询问“准备好部署到开发环境了吗？”
3. **等待明确批准**
4. 批准后：`agents-cli deploy`

> **Agent Runtime 超时恢复：** Agent Runtime 部署可能需要 5-10 分钟，并且可能超过命令超时。如果部署命令被取消或超时，部署将在服务器端继续。运行 `agents-cli deploy --status` 检查进度 — 每 60 秒轮询一次，直到报告完成或失败。

**重要提示**：未经明确人类批准，切勿运行 `agents-cli deploy`。

> **在部署之前切勿运行 `agents-cli infra single-project`。** 它不是前提条件 — `agents-cli deploy` 可以单独工作。如果用户需要可观察性功能（提示-响应日志记录、BigQuery 分析），请单独运行它 — 请参阅 `/google-agents-cli-observability`。

### 单项目基础设施设置（可选 — 高级）

`agents-cli infra single-project` 在 `deployment/terraform/single-project/` 中运行 `terraform apply`。使用此方法可以**在不使用 CI/CD 的情况下提供单项目 GCP 基础设施**（服务帐户、IAM 绑定、遥测资源、Artifact Registry）。在转到生产之前，在单个项目中测试也非常有用。它**不是部署所必需的**。

```bash
# 可选 — 在单个 GCP 项目中提供基础设施
agents-cli infra single-project
```

> **注意：** `agents-cli deploy` 不会自动使用 Terraform 创建的 `app_sa`。显式传递服务帐户：`agents-cli deploy --service-account SA_EMAIL`。

### 部署标志参考

| 标志 | 描述 | 目标 |
|------|-------------|---------|
| `--project` | GCP 项目 ID | 所有 |
| `--region` | GCP 区域 | 所有 |
| `--service-account` | 部署代理的服务帐户电子邮件 | 所有 |
| `--service-name` | 覆盖部署的服务名称（Cloud Run 服务或 Agent Runtime 显示名称）；默认为项目名称。如果你覆盖它，请考虑更新你的 Terraform 和 CI（如果存在） — 它们根据项目名称命名资源。GKE 不支持此功能，其名称完全由 Terraform 控制。 | Agent Runtime, Cloud Run |
| `--secrets` | 以逗号分隔的 `ENV=SECRET` 或 `ENV=SECRET:VERSION` 对 | Agent Runtime, Cloud Run |
| `--update-env-vars` | 以逗号分隔的 `KEY=VALUE` 环境变量 | Agent Runtime, Cloud Run |
| `--agent-identity` | 启用 [Agent Identity](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/runtime/agent-identity) | Agent Runtime |
| `--no-agent-identity` | 禁用 Agent Identity。传递 `--agent-identity` 或 `--no-agent-identity` 都会默认为无 Agent Identity，当创建新代理时，或在后续重新部署中保持当前身份类型。 | Agent Runtime |
| `--network-attachment` | 用于 [PSC 接口](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/runtime/private-service-connect-interface) 的网络附加组件资源名称（启用私有 VPC 连接） | Agent Runtime |
| `--dns-peering-domain` | DNS 对等域后缀，例如 `my-internal.corp.`（需要 `--network-attachment`） | Agent Runtime |
| `--dns-peering-project` | 托管 Cloud DNS 管理区域的 Cloud DNS 项目 ID（需要 `--network-attachment`） | Agent Runtime |
| `--dns-peering-network` | 目标项目中用于 DNS 对等的 VPC 网络名称（需要 `--network-attachment`） | Agent Runtime |
| `--agent-gateway-egress` | 将代理绑定到控制出站流量的 [Agent Gateway](https://docs.cloud.google.com/gemini-enterprise-agent-platform/govern/gateways/agent-gateway-overview)。具有 `governedAccessPath=AGENT_TO_ANYWHERE` 的网关的完整资源名称。空值会解除绑定；省略则保持不变。请参阅 [Agent Gateway](#agent-gateway) | Agent Runtime |
| `--agent-gateway-ingress` | 将代理绑定到控制入站流量的 Agent Gateway。具有 `governedAccessPath=CLIENT_TO_AGENT` 的网关的完整资源名称。空值会解除绑定；省略则保持不变 | Agent Runtime |
| `--memory` | 内存限制（默认：`4Gi`） | Agent Runtime, Cloud Run |
| `--cpu` | CPU 限制（默认：`1`） | Agent Runtime, Cloud Run |
| `--min-instances` | 最小实例数（默认：`0`，即扩展到零；生成的 Terraform 使用 `1`） | Agent Runtime, Cloud Run |
| `--max-instances` | 最大实例数（默认：`10`） | Agent Runtime, Cloud Run |
| `--concurrency` | 每个容器的并发请求（默认：`8`；请参阅 [部署缩放](#sizing-a-deployment)） | Agent Runtime, Cloud Run |
| `--port` | 容器端口 | Cloud Run, Agent Runtime |
| `--build-args` | 以逗号分隔的 `KEY=VALUE` Docker 构建参数 | Agent Runtime |
| `--labels` | 以逗号分隔的 `KEY=VALUE` 资源标签。增量：添加/更新您命名的标签；未命名的标签将保持不变。 | Agent Runtime, Cloud Run |
| `--iap` | 启用 Identity-Aware Proxy | Cloud Run |
| `--image` | 容器镜像 URI（跳过源构建；Agent Runtime 不支持） | Cloud Run, GKE |
| `--no-wait` | 开始部署并立即返回 | Agent Runtime, Cloud Run |
| `--status` | 检查挂起的 `--no-wait` 部署的状态 | Agent Runtime, Cloud Run |
| `--list` | 列出现有部署并退出 | 所有 |
| `--dry-run` / `-n` | 打印实际执行的命令而不执行它 | 所有 |
| `--no-confirm-project` | 跳过项目确认提示 | 所有 |

运行 `agents-cli deploy --help` 获取完整标志参考。

> **高级 Cloud Run 部署：** 如果你需要 `agents-cli` 标志未暴露的功能，使用 `--dry-run`（或 `-n`）打印完整的 `gcloud` 命令，复制它，并根据需要添加其他参数。

> **项目确认：** 如果项目自动解析（未通过 `--project` 传递），命令将在交互模式下提示确认。由于代理通常在非交互模式下运行，如果你依赖自动项目解析，你必须传递 `--no-confirm-project` 才能继续。

---

## 部署缩放

默认值（Agent Runtime 和 Cloud Run 上相同）：`--cpu 1`，`--memory 4Gi`，`--concurrency 8`，`--min-instances 0`，`--max-instances 10`。生成的 `service.tf` 与此匹配，除了它将 `min_instances = 1` 固定，以便生产部署不会遇到冷启动。建议值是针对 Python 代理调整的，因此将它们视为起点，并通过负载测试进行调整（见下文）。

`agents-cli deploy` 默认扩展到零，因此空闲的开发和演示代理不会占用容量。当你需要热实例时，请传递 `--min-instances 1`（或通过 Terraform 部署）。

这些参数是耦合的 — 一起扩展它们：

- **一个进程 — 水平扩展，而不是垂直扩展。** 容器运行单个服务器进程来处理许多并发请求，因此吞吐量来自 `--concurrency` 和水平扩展 (`--max-instances`)，而不是来自额外的 worker 进程。仅在分析显示实际 CPU 饱和而不是花费时间等待模型时才增加 `--cpu`。
- **内存限制并发。** 每个并发请求在等待模型时将其完整的工作集（上下文窗口、历史记录、RAG 块、响应缓冲区）保留在内存中，因此峰值 ≈ 基础 + `concurrency × 每个请求的内存`。内存 — 不是 CPU — 是第一个限制，因此在不增加 `--concurrency` 的情况下增加 `--memory` 是主要的 OOM 原因。
- **并发默认值保守。** 工作器可以在等待模型时服务许多并发请求，但每个请求的内存是特定于代理的，因此 `8` 可以保护内存密集型（RAG/多模态）代理。轻量级代理在负载测试后可以将它提高到 16–32+。

```bash
# 4 倍吞吐量：每个参数都扩展，而不仅仅是扩展一个
agents-cli deploy --cpu 4 --concurrency 16 --memory 16Gi --max-instances 20
```

**通过负载测试进行调整**（在 Python 项目的 `tests/load_test/` 中，或在 Go 项目的 `e2e/load_test/` 中；可以在本地运行或在 CI/CD 部署管道中运行）：驱动负载，观察 *最大* 延迟和内存/OOM 重启，然后调整 — 高最大延迟 → 增加并发 (+ 工作者/ CPU)；OOM → 增加内存或降低并发。

> 在 **GKE** 上，这些缩放标志会被拒绝 — 通过 Terraform 配置文件 + HorizontalPodAutoscaler 进行缩放。

---

## 生产部署 — CI/CD 管道

有关完整的 CI/CD 管道设置指南 — 前提条件、`infra cicd` 标志、运行器比较、WIF 身份验证、管道阶段和生产批准 — 请参阅 `references/cicd-pipeline.md`。

---

## Cloud Run 特定内容

有关详细的基础设施配置（扩展默认值、Dockerfile、FastAPI 端点、会话类型、网络），请参阅 `references/cloud-run.md`。**ADK：** 有关 Cloud Run 部署的 ADK 文档，请获取 `https://adk.dev/deploy/cloud-run/index.md`。

> **ADK 项目。** 有关 Cloud Run 上的事件驱动/环境代理部署，请查看 [`ambient-expense-agent`](https://github.com/google/adk-samples/tree/main/core/python/ambient-expense-agent) 示例和 `/google-agents-cli-adk-code` (`references/adk-python.md`，部分 "12. Event-Driven / Ambient Agents") 中的 `trigger_sources` 模式。

---

## Agent Runtime 特定内容

Agent Runtime 是一个 Vertex AI 服务，用于将代理作为容器部署。使用基于容器的部署：`agents-cli deploy` 打包你的项目，Agent Engine 从你的项目的 `Dockerfile`（必需）构建镜像（与 Cloud Run 和 GKE 使用的相同镜像）。

> **不存在 `gcloud` CLI 用于 Agent Runtime。** 通过 `agents-cli deploy` 部署。通过 Python `agentplatform.Client` SDK 查询。

部署可能需要 5-10 分钟。使用 `--no-wait` 开始部署并立即返回，然后稍后使用 `--status` 检查它：

```bash
# 不阻塞地开始部署
agents-cli deploy --no-wait

# 稍后检查进度
agents-cli deploy --status
```

当 `--status` 检测到操作已完成时，它会写入 `deployment_metadata.json` 并打印与正常部署相同的成功输出。

有关详细的基础设施配置（容器部署流程、统一的 FastAPI 应用和 `/api` 转发、Terraform 资源、部署元数据、会话/工件服务、CI/CD 差异），请参阅 `references/agent-runtime.md`。**ADK：** 有关 ADK 文档中 Agent Runtime 部署，请获取 `https://adk.dev/deploy/agent-runtime/index.md`。

---

## GKE 特定内容

有关详细的基础设施配置（Kubernetes 配置文件、Terraform 资源、工作负载身份、会话类型、网络），请参阅 `references/gke.md`。**ADK：** 有关 ADK 文档中 GKE 部署，请获取 `https://adk.dev/deploy/gke/index.md`。

---

## 服务帐户架构

构建项目使用两个服务帐户：

- **`app_sa`**（每个环境） — 部署代理的运行时身份。在 `deployment/terraform/iam.tf` 中定义的角色。
- **`cicd_runner_sa`**（CI/CD 项目） — CI/CD 管道的身份（GitHub Actions / Cloud Build）。存在于 CI/CD 项目中（默认为生产项目），需要在 ** staging** 和 **生产** 项目中都需要权限。

检查 `deployment/terraform/iam.tf` 以获取确切的角色绑定。跨项目权限（Cloud Run 服务代理、Artifact Registry 访问）也配置在那里。

**常见 403 错误：**
- "Cloud Run 权限被拒绝" → `cicd_runner_sa` 缺少目标项目的部署角色
- "无法作为服务帐户操作" → `app_sa` 缺少 `iam.serviceAccountUser` 绑定
- "密钥访问被拒绝" → `app_sa` 缺少 `secretmanager.secretAccessor`
- "Cloud SQL 连接失败 / 未授权" → 运行时服务帐户缺少 `roles/cloudsql.client`
- "Artifact Registry 读取被拒绝" → Cloud Run 服务代理缺少 CI/CD 项目的读取权限

---

## CI/CD 设置所需的权限

- **`roles/secretmanager.admin`** 授予 CI/CD 项目中的 Cloud Build 服务帐户 (`service-<PROJECT_NUMBER>@gcp-sa-cloudbuild.iam.gserviceaccount.com`)。这允许 Cloud Build 访问存储在 Secret Manager 中的 GitHub 令牌。

---

## 所需的 API

以下 Google Cloud API 必须在你项目中启用，以便技能和部署才能工作：

- **`cloudbuild.googleapis.com`** — 用于构建容器镜像和运行 CI/CD 管道所必需。
- **`secretmanager.googleapis.com`** — 用于管理密钥和 API 密码所必需。
- **`run.googleapis.com`** — 用于部署到 Cloud Run 所必需。

在运行部署或 CI/CD 设置命令之前确保这些已启用：
```bash
gcloud services enable cloudbuild.googleapis.com secretmanager.googleapis.com run.googleapis.com --project=YOUR_PROJECT_ID
```

---

## Secret Manager（用于 API 凭证）

不要将敏感密钥作为环境变量传递，而应使用 GCP Secret Manager。

```bash
# 创建密钥
echo -n "YOUR_API_KEY" | gcloud secrets create MY_SECRET_NAME --data-file=-

# 更新现有密钥
echo -n "NEW_API_KEY" | gcloud secrets versions add MY_SECRET_NAME --data-file=-
```

**授予权限：** 对于 Cloud Run，将 `secretmanager.secretAccessor` 授予 `app_sa`。对于 Agent Runtime，将其授予平台管理的 SA (`service-PROJECT_NUMBER@gcp-sa-aiplatform-re.iam.gserviceaccount.com`)。对于 GKE，将 `secretmanager.secretAccessor` 授予 `app_sa`。通过 Kubernetes Secrets 或直接通过 Secret Manager API 使用 Workload Identity 访问密钥。

**在部署时传递密钥（Agent Runtime, Cloud Run）：**
```bash
agents-cli deploy --secrets "API_KEY=my-api-key,DB_PASS=db-password:2"
```

格式：`ENV_VAR=SECRET_ID` 或 `ENV_VAR=SECRET_ID:VERSION`（默认为最新）。

---

## Cloud SQL 权限（手动部署）

在使用 Cloud SQL 和 Cloud Run 的**手动部署**（例如，在非 Terraform 设置中添加 `--add-cloudsql-instances`），你必须手动授予运行时服务帐户 `Cloud SQL Client` 角色。

如果没有此设置，部署可能成功，但在运行时可能会出现 `cloudsql.instances.get` 授权错误。

```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:YOUR_RUNTIME_SA_EMAIL" \
  --role="roles/cloudsql.client"
```

> **注意：** 在完整的 Terraform 管理设置中 (`infra cicd` / `infra single-project`), 此角色会自动配置和管理。

---

## 可观察性

请参阅 **agents-cli-observability** 技能，了解可观察性配置（Cloud Trace、日志记录、BigQuery 分析和第三方集成）。

---

## 测试已部署的代理

测试已部署代理的最快方法是 `agents-cli run --url <service-url> --mode a2a "your prompt"` — 它会自动处理身份验证、会话和流式传输（支持 Agent Runtime 和 Cloud Run）。**ADK：** `--mode adk` 与 ADK 流式 API 通信。

对于高级测试（自定义标头、会话重用、脚本、负载测试），请参阅 `references/testing-deployed-agents.md`。

---

## 使用 UI 部署（IAP）

IAP（Identity-Aware Proxy）保护 Cloud Run 服务，以便只有授权的 Google 账户才能访问它。通过在部署时添加 `--iap` 标志（仅限 Cloud Run）启用它：`agents-cli deploy --iap`.

对于具有自定义前端的 Agent Runtime，请使用**解耦部署** — 将前端单独部署到 Cloud Run 或 Cloud Storage，连接到 Agent Runtime 后端 API。

有关 Cloud Run 中 IAP 的更多信息，请参阅 [Cloud Console IAP 设置](https://cloud.google.com/run/docs/securing/identity-aware-proxy-cloud-run#manage_user_or_group_access).

---

## 回滚与恢复

主要的回滚机制是 **基于 git 的**：修复问题，提交并推送到 `main`。CI/CD 管道将自动构建和部署新版本通过 staging → production。

对于立即 Cloud Run 回滚（无需新提交），请使用版本流量转移：
```bash
gcloud run revisions list --service=SERVICE_NAME --region=REGION
gcloud run services update-traffic SERVICE_NAME \
  --to-revisions=REVISION_NAME=100 --region=REGION
```

Agent Runtime 不支持基于版本的回滚 — 修复并重新部署 via `agents-cli deploy`.

对于 GKE 回滚，使用 `kubectl rollout undo`：
```bash
kubectl rollout undo deployment/DEPLOYMENT_NAME -n NAMESPACE
kubectl rollout status deployment/DEPLOYMENT_NAME -n NAMESPACE
```

---

## 自定义基础设施（Terraform）

**关键**：当你的代理需要自定义基础设施（Cloud SQL、Pub/Sub、Eventarc、BigQuery 等），你必须使用 Terraform 定义它 — 永远不要通过 `gcloud` 命令手动创建资源。例外：快速实验可以使用 `gcloud` 或控制台，但生产基础设施必须在 Terraform 中。

有关自定义基础设施模式，请参阅 `references/terraform-patterns.md`，了解：
- 自定义 Terraform 文件放置的位置（单项目 vs CI/CD）
- 资源示例（Pub/Sub、BigQuery、Eventarc 触发器）
- 自定义资源的 IAM 绑定
- Terraform 状态管理（远程 vs 本地，导入资源）
- 常见基础设施模式

---

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| Terraform 状态锁定 | `terraform force-unlock -force LOCK_ID` 在 deployment/terraform/ |
| GitHub Actions 身份验证失败 | 在 CI/CD terraform 目录中重新运行 `terraform apply`；验证 WIF 池/提供者 |
| Cloud Build 授权挂起 | 使用 `github_actions` 运行器 |
| 资源已存在 | `terraform import` (请参阅 `references/terraform-patterns.md`) |
| Agent Runtime 部署超时 / 挂起 | 部署需要 5-10 分钟；检查是否创建了引擎（请参阅 Agent Runtime 特定内容） |
| 密钥不可用 | 验证已将 `secretAccessor` 授予 `app_sa`（不是默认的 compute SA） |
| Cloud SQL 连接失败 / 403 | 在手动部署中，将 `roles/cloudsql.client` 授予运行时服务帐户 |
| 部署时 403 | 检查 `deployment/terraform/iam.tf` — `cicd_runner_sa` 在目标项目中需要部署和 SA 仿冒角色 |
| 测试 Cloud Run 时 403 | 默认为 `--no-allow-unauthenticated`；包括 `Authorization: Bearer $(gcloud auth print-identity-token)` 标头 |
| 冷启动太慢 | 在 Cloud Run Terraform 配置中设置 `min_instance_count > 0` |
| Cloud Run 503 错误 | 检查资源限制（内存/CPU），增加 `max_instance_count` 或检查容器崩溃日志 |
| 授予 IAM 角色后立即 403 | IAM 传播不是即时的 — 等待几分钟再重试。不要不断重新授予相同的角色 |
| 资源似乎缺失但 Terraform 创建了它 | 运行 `terraform state list` 检查 Terraform 实际管理的资源。通过 `null_resource` + `local-exec` 创建的资源（例如 BQ 链接数据集）不会出现在 `gcloud` CLI 输出中 |
| 部署失败或代理无响应 | 检查 Cloud Logging: `gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=SERVICE" --project=PROJECT --limit=50 --format="table(timestamp,severity,textPayload)"` 对于 Cloud Run，或 `gcloud logging read "resource.type=aiplatform.googleapis.com/ReasoningEngine" --project=PROJECT --limit=50` 对于 Agent Runtime |
| 部署后代理返回错误 | 在控制台打开 Cloud Logging → 按服务名称（Cloud Run）或推理引擎资源（Agent Runtime）过滤 → 查找最近的日志条目中的堆栈跟踪或权限错误 |

---

## 平台注册

有关将已部署的代理注册到 Gemini Enterprise，请参阅 `/google-agents-cli-publish`。

---

## Agent Gateway

> **注意：** 没有 `agents-cli` 命令用于创建或管理 Agent Gateways 或
> Semantic Governance 策略 — 分别设置这些（通过 Terraform 或 Cloud Console）。
> `agents-cli deploy` 是唯一感知网关的命令，其支持是转发：它作为 Agent Runtime 创建/更新调用的一部分将代理绑定到现有的网关。

**Agent Gateway** 是所有代理交互（用户↔代理、代理↔工具、代理↔代理）的网络和安全入口点 — 它集中控制访问控制和受管理的连接（入站/出站）。它不是一个部署目标。

要设置网关，请按照 [设置 Agent Gateway](https://docs.cloud.google.com/gemini-enterprise-agent-platform/govern/gateways/set-up-agent-gateway)
和 [将 Agent Runtime 流量通过 Agent Gateway](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/runtime/agent-gateway-runtime-deploy)。您也可以使用 [`google_network_services_agent_gateway`](https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/network_services_agent_gateway) 在 Terraform 中管理网关（目前位于 `google-beta` 提供商）。

一旦存在网关，`agents-cli deploy` 就会使用 `--agent-gateway-egress`
和/或 `--agent-gateway-ingress` 将代理绑定到它，每个都采用完整资源名称
(`projects/PROJECT/locations/REGION/agentGateways/GATEWAY`)。仅支持 Agent Runtime 部署，并且代理必须具有 Agent Identity。

出站网关对代理的出站通信执行 TLS 解密和检查，因此镜像必须信任网关的根 CA。该设置在构建时是可选的。如果你正在创建新项目，请将 `--agent-gateway` 标志传递给 `agents-cli create`：

```bash
agents-cli create my-agent -d agent_runtime --agent-gateway
```

或者，你可以将相同的标志传递给 `agents-cli scaffold enhance` 以升级现有项目：
```bash
agents-cli scaffold enhance . --agent-gateway
```

无论哪种方式，都会写入 Dockerfile，该 Dockerfile 消耗平台注入的 `AGENT_GATEWAY_ROOT_CERTIFICATES` 构建参数，并记录 `agent_gateway: true` 在 `create_params` 下，以便 `scaffold upgrade` 保留它。使用 `--agent-gateway-egress` 部署时，如果 Dockerfile 缺少构建参数，则失败，并指向上面的命令；`--no-agent-gateway` 会删除设置。

背景：[Agent Gateway 概述](https://docs.cloud.google.com/gemini-enterprise-agent-platform/govern/gateways/agent-gateway-overview)。

## Semantic Governance

**Semantic Governance Policies (SGP)** 添加了一层自然语言安全/合规层，以保持代理的工具调用与用户意图和组织约束一致。

- 概述：https://docs.cloud.google.com/gemini-enterprise-agent-platform/govern/policies/semantic-governance-overview
- 配置：https://docs.cloud.google.com/gemini-enterprise-agent-platform/govern/policies/configure-semantic-governance

---

## 相关技能

- `/google-agents-cli-workflow` — 开发工作流、编码规范和操作规则
- `/google-agents-cli-adk-code` — ADK API 快速参考，用于编写代理代码
- `/google-agents-cli-eval` — 评估方法、数据集模式以及评估-修复循环
- `/google-agents-cli-scaffold` — 使用 `agents-cli scaffold create` / `scaffold enhance` 创建和增强项目
- `/google-agents-cli-observability` — Cloud Trace、日志记录、BigQuery 分析和第三方集成
- `/google-agents-cli-publish` — Gemini Enterprise 注册
