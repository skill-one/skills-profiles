# ADK 部署指南

> **使用脚手架项目？** 在本指南中，请使用 `make` 命令——它们将 Terraform、Docker 和部署封装成一个经过测试的流程。
>
> **没有脚手架？** 请参阅下方的 [快速部署](#quick-deploy-adk-cli)，或参阅 [ADK 部署文档](https://adk.dev/deploy/)。
> 对于生产基础设施，请使用 `/adk-scaffold` 进行脚手架搭建。

### 参考文件

如需更详细信息，请参阅 `references/` 目录中的以下参考文件：

- **`cloud-run.md`** — 扩展默认值、Dockerfile、会话类型、网络配置
- **`agent-engine.md`** — deploy.py CLI、AdkApp 模式、Terraform 资源、部署元数据、CI/CD 差异
- **`gke.md`** — GKE Autopilot 集群、Terraform 管理的 Kubernetes 资源、工作负载身份验证、会话类型、网络配置
- **`terraform-patterns.md`** — 自定义基础设施、IAM、状态管理、导入资源
- **`event-driven.md`** — Pub/Sub、Eventarc、通过自定义 `fast_api_app.py` 端点触发的 BigQuery 远程函数

> **可观测性：** 请参阅 **adk-observability-guide** 技能，了解 Cloud Trace、提示-响应日志记录、BigQuery 分析和第三方集成。

---

## 部署目标决策矩阵

根据您的需求选择合适的部署目标：

| 标准 | Agent Engine | Cloud Run | GKE |
|------|-------------|-----------|-----|
| **语言** | Python | Python | Python (+ 通过自定义容器支持其他语言) |
| **扩展** | 管理自动扩展（可配置最小/最大值、并发量） | 完全可配置（最小/最大实例数、并发量、CPU 分配） | 完整 Kubernetes 扩展（HPA、VPA、节点自动配置） |
| **网络** | 支持 VPC-SC 和 PSC | 支持 VPC 全功能、直接 VPC 出口、IAP、入站规则 | 完整 Kubernetes 网络配置 |
| **会话状态** | 本地 `VertexAiSessionService`（持久化、管理） | 内存（开发）、Cloud SQL 或 Agent Engine 会话后端 | 内存（开发）、Cloud SQL 或 Agent Engine 会话后端 |
| **批处理/事件处理** | 不支持 | `/invoke` 端点用于 Pub/Sub、Eventarc、BigQuery | 自定义（Kubernetes Jobs、Pub/Sub） |
| **成本模型** | vCPU 小时 + 内存小时（空闲时不计费） | 每实例秒 + 最小实例成本 | 节点池成本（始终开启或自动配置） |
| **设置复杂度** | 较低（管理型、专为代理设计） | 中等（Dockerfile、Terraform、网络配置） | 较高（需要 Kubernetes 专业知识） |
| **适用场景** | 管理型基础设施、最小运维 | 自定义基础设施、事件驱动工作负载 | 完全 Kubernetes 控制 |

**询问用户** 哪个部署目标适合他们的需求。每个都是有效的生产选择，具有不同的权衡。

---

## 快速部署 (ADK CLI)

适用于没有 Agent Starter Pack 脚手架的项目。无需 Makefile、Terraform 或 Dockerfile。

```bash
# Cloud Run
adk deploy cloud_run --project=PROJECT --region=REGION path/to/agent/

# Agent Engine
adk deploy agent_engine --project=PROJECT --region=REGION path/to/agent/

# GKE（需要现有集群）
adk deploy gke --project=PROJECT --cluster_name=CLUSTER --region=REGION path/to/agent/
```

所有命令都支持 `--with_ui` 以部署 ADK 开发 UI。Cloud Run 还接受 `--` 后面的额外 `gcloud` 标志（例如，`-- --no-allow-unauthenticated`）。

请参阅 `adk deploy --help` 或 [ADK 部署文档](https://adk.dev/deploy/) 获取完整标志参考。

> 对于 CI/CD、可观测性或生产基础设施，请使用 `/adk-scaffold` 进行脚手架搭建，并使用下文中的部分。

---

## 开发环境设置与部署 (已脚手架项目)

### 设置开发基础设施（可选）

`make setup-dev-env` 会运行 `deployment/terraform/dev/` 目录中的 `terraform apply`。这将提供支持基础设施：
- 服务账户（`app_sa` 用于代理，用于运行时权限）
- 资源库（用于容器镜像）
- IAM 绑定（授予应用 SA 必要的角色）
-遥测资源（Cloud Logging 存储桶、BigQuery 数据集）
- `deployment/terraform/dev/` 中定义的任何自定义资源

此步骤为**可选**——即使没有它，`make deploy` 也能正常工作（Cloud Run 会动态创建服务，通过 `gcloud run deploy --source .`）。但运行此步骤可以为您提供正确的服务账户、可观测性和 IAM 设置。

```bash
make setup-dev-env
```

> **注意：** `make deploy` 不会自动使用 Terraform 创建的 `app_sa`。请显式传递 `--service-account` 或更新 Makefile。

### 部署

1. **通知人员**："评估分数达到阈值且测试通过。准备部署到开发环境？"
2. **等待明确批准**
3. 批准后：`make deploy`

**重要提示**：未经明确人员批准，切勿运行 `make deploy`。

---

## 生产部署 — CI/CD 管道

**适用场景：** 生产应用程序、需要 staging → 生产发布的团队。

**前提条件：**
1. 项目不能位于 git 忽略文件夹中
2. 用户必须提供 staging 和生产 GCP 项目 ID
3. GitHub 仓库名称和所有者

**步骤：**
1. 如果是原型，请首先使用 Agent Starter Pack CLI 添加 Terraform/CI-CD 文件（有关完整选项，请参阅 `/adk-scaffold`）：
   ```bash
   uvx agent-starter-pack enhance . --cicd-runner github_actions -y -s
   ```

2. 确保已登录 GitHub CLI：
   ```bash
   gh auth login  # (如果已认证，则跳过)
   ```

3. 运行 setup-cicd：
   ```bash
   uvx agent-starter-pack setup-cicd \
     --staging-project YOUR_STAGING_PROJECT \
     --prod-project YOUR_PROD_PROJECT \
     --repository-name YOUR_REPO_NAME \
     --repository-owner YOUR_GITHUB_USERNAME \
     --auto-approve \
     --create-repository
   ```

4. 推送代码以触发部署

#### setup-cicd 的关键标志

| 标志 | 描述 |
|------|-------------|
| `--staging-project` | staging 环境的 GCP 项目 ID |
| `--prod-project` | 生产环境的 GCP 项目 ID |
| `--repository-name` / `--repository-owner` | GitHub 仓库名称和所有者 |
| `--auto-approve` | 跳过 Terraform 计划确认提示 |
| `--create-repository` | 如果不存在，则创建 GitHub 仓库 |
| `--cicd-project` | 用于 CI/CD 基础设施的独立 GCP 项目。默认为生产项目 |
| `--local-state` | 将 Terraform 状态存储在本地，而不是 GCS（请参阅 `references/terraform-patterns.md`） |

运行 `uvx agent-starter-pack setup-cicd --help` 获取完整标志参考（Cloud Build 选项、开发项目、区域等）。

### 选择 CI/CD 运行器

| 运行器 | 优点 | 缺点 |
|--------|------|------|
| **github_actions**（默认） | 无需 PAT、使用 `gh auth`、基于 WIF、完全自动化 | 需要 GitHub CLI 认证 |
| **google_cloud_build** | 本地 GCP 集成 | 需要交互式浏览器授权（或程序化模式下的 PAT + 应用安装 ID） |

### 身份验证如何工作 (WIF)

两个运行器都使用**工作负载身份联合 (WIF)**——GitHub/Cloud Build OIDC 令牌被 GCP 工作负载身份池信任，该池授予 `cicd_runner_sa` 代理权限。无需长生命周期的服务账户密钥。`setup-cicd` 中的 Terraform 自动创建池、提供程序和 SA 绑定。如果身份验证失败，请在 CI/CD Terraform 目录中重新运行 `terraform apply`。

### CI/CD 管道阶段

管道有三个阶段：

1. **CI（PR 检查）** — 在拉取请求触发时运行。运行单元和集成测试。
2. **Staging CD** — 在合并到 `main` 时触发。构建容器、部署到 staging、运行负载测试。
   > **路径过滤器：** Staging CD 使用 `paths: ['app/**']`——它仅在 `app/` 下文件更改时触发。首次推送后（`setup-cicd`）不会触发 staging CD，除非您修改 `app/` 中的内容。如果推送后无任何变化，原因在于此。
3. **生产 CD** — 在 staging 部署成功后通过 `workflow_run` 触发。可能需要**手动批准**才能部署到生产。
   > **批准：** 前往 GitHub Actions → 生产工作流运行 → 点击“审核部署”→ 批准待处理的 `production` 环境。这是 GitHub 的环境保护规则，而不是自定义机制。

**重要提示**：`setup-cicd` 创建基础设施，但不会自动部署。Terraform 配置所有所需的 GitHub 密钥和变量（WIF 凭据、项目 ID、服务账户）。推送代码以触发管道：

```bash
git add . && git commit -m "Initial agent implementation"
git push origin main
```

要批准生产部署：

```bash
# GitHub Actions: 通过仓库 Actions 选项卡（环境保护规则）批准

# Cloud Build: 找到待处理的构建并批准
gcloud builds list --project=PROD_PROJECT --region=REGION --filter="status=PENDING"
gcloud builds approve BUILD_ID --project=PROD_PROJECT
```

---

## Cloud Run 特定配置

有关详细基础设施配置（扩展默认值、Dockerfile、FastAPI 端点、会话类型、网络配置），请参阅 `references/cloud-run.md`。有关 Cloud Run 部署的 ADK 文档，请获取 `https://adk.dev/deploy/cloud-run/index.md`。

---

## Agent Engine 特定配置

Agent Engine 是一个用于部署 Python ADK 代理的 Vertex AI 管理服务。使用基于源码的部署（无需 Dockerfile）通过 `deploy.py` 和 `AdkApp` 类。

> **不存在 `gcloud` CLI 用于 Agent Engine。** 通过 `deploy.py` 或 `adk deploy agent_engine` 进行部署。通过 Python `vertexai.Client` SDK 进行查询。

部署可能需要 5-10 分钟。如果 `make deploy` 超时，请检查引擎是否已创建，并手动填充 `deployment_metadata.json` 以包含引擎资源 ID（请参阅参考文件了解详情）。

有关详细基础设施配置（deploy.py 标志、AdkApp 模式、Terraform 资源、部署元数据、会话/资源服务、CI/CD 差异），请参阅 `references/agent-engine.md`。有关 Agent Engine 部署的 ADK 文档，请获取 `https://adk.dev/deploy/agent-engine/index.md`。

---

## GKE 特定配置

有关详细基础设施配置（Terraform 管理的 Kubernetes 资源、工作负载身份验证、会话类型、网络配置），请参阅 `references/gke.md`。有关 GKE 部署的 ADK 文档，请获取 `https://adk.dev/deploy/gke/index.md`。

---

## 服务账户架构

已脚手架项目使用两个服务账户：

- **`app_sa`**（每个环境）——部署代理的运行时身份。角色定义在 `deployment/terraform/iam.tf` 中。
- **`cicd_runner_sa`**（CI/CD 项目）——CI/CD 管道的身份（GitHub Actions / Cloud Build）。存在于 CI/CD 项目（默认为生产项目），需要在 staging 和 prod 项目中都具有权限。

检查 `deployment/terraform/iam.tf` 获取确切的角色绑定。跨项目权限（Cloud Run 服务代理、资源库访问）也配置在那里。

**常见的 403 错误：**
- "Cloud Run 权限被拒绝" → `cicd_runner_sa` 缺少目标项目的部署角色
- "无法代理服务账户" → 缺少 `iam.serviceAccountUser` 绑定在 `app_sa`
- "密钥访问被拒绝" → `app_sa` 缺少 `secretmanager.secretAccessor`
- "资源库读取被拒绝" → Cloud Run 服务代理缺少在 CI/CD 项目中的读取权限

---

## 密钥管理器（用于 API 凭据）

不要将敏感密钥作为环境变量传递，而应使用 GCP 密钥管理器。

```bash
# 创建密钥
echo -n "YOUR_API_KEY" | gcloud secrets create MY_SECRET_NAME --data-file=-

# 更新现有密钥
echo -n "NEW_API_KEY" | gcloud secrets versions add MY_SECRET_NAME --data-file=-
```

**授予权限：** 对于 Cloud Run，授予 `secretmanager.secretAccessor` 给 `app_sa`。对于 Agent Engine，授予它给平台管理的 SA（`service-PROJECT_NUMBER@gcp-sa-aiplatform-re.iam.gserviceaccount.com`）。对于 GKE，授予 `app_sa` `secretmanager.secretAccessor`。通过 Kubernetes Secrets 或直接通过 Secret Manager API（使用工作负载身份）访问密钥。

**部署时传递密钥（Agent Engine）：**
```bash
make deploy SECRETS="API_KEY=my-api-key,DB_PASS=db-password:2"
```

格式：`ENV_VAR=SECRET_ID` 或 `ENV_VAR=SECRET_ID:VERSION`（默认为最新）。通过 `os.environ.get("API_KEY")` 在代码中访问。

---

## 可观测性

请参阅 **adk-observability-guide** 技能，了解可观测性配置（Cloud Trace、提示-响应日志记录、BigQuery 分析和第三方集成）。

---

## 测试已部署的代理

### Agent Engine 部署

**选项 1：测试笔记本**
```bash
jupyter notebook notebooks/adk_app_testing.ipynb
```

**选项 2：Python 脚本**
```python
import json
import vertexai

with open("deployment_metadata.json") as f:
    engine_id = json.load(f)["remote_agent_engine_id"]

client = vertexai.Client(location="us-central1")
agent = client.agent_engines.get(name=engine_id)

async for event in agent.async_stream_query(message="Hello!", user_id="test"):
    print(event)
```

**选项 3：Playground**
```bash
make playground
```

### Cloud Run 部署

> **默认需要身份验证。** Cloud Run 部署时使用 `--no-allow-unauthenticated`，因此所有请求都需要带有 `Authorization: Bearer` 头部和一个身份令牌。如果收到 403，您很可能缺少此头部。要允许公开访问，请重新部署并使用 `--allow-unauthenticated`。

```bash
SERVICE_URL="https://SERVICE_NAME-PROJECT_NUMBER.REGION.run.app"
AUTH="Authorization: Bearer $(gcloud auth print-identity-token)"

# 测试健康端点
curl -H "$AUTH" "$SERVICE_URL/"

# 第一步：创建会话（发送消息前需要）
curl -X POST "$SERVICE_URL/apps/app/users/test-user/sessions" \
  -H "Content-Type: application/json" \
  -H "$AUTH" \
  -d '{}'
# → 返回包含 "id" 的 JSON——使用此 ID 作为下文的 SESSION_ID

# 第二步：通过 SSE 流式传输发送消息
curl -X POST "$SERVICE_URL/run_sse" \
  -H "Content-Type: application/json" \
  -H "$AUTH" \
  -d '{
    "app_name": "app",
    "user_id": "test-user",
    "session_id": "SESSION_ID",
    "new_message": {"role": "user", "parts": [{"text": "Hello!"}]}
  }'
```

> **常见错误：** 使用 `{"message": "Hello!", "user_id": "...", "session_id": "..."}` 返回 `422 Field required`。ADK HTTP 服务器期望上述 `new_message` / `parts` 模式，并且会话必须已存在。

### GKE 部署

GKE LoadBalancer 服务默认为公共——无需身份验证头部（与 Cloud Run 不同）。请参阅 `references/gke.md` 获取 curl 示例和端点详情。

### 负载测试

```bash
make load-test
```

有关配置、默认设置和 CI/CD 集成详情，请参阅 `tests/load_test/README.md`。

---

## 使用 UI 部署 (IAP)

要使用受 Google 身份认证保护的 Web UI 暴露您的代理：

```bash
# 使用 IAP（内置框架 UI）部署
make deploy IAP=true

# 使用自定义前端在不同端口部署
make deploy IAP=true PORT=5173
```

IAP（身份感知代理）保护 Cloud Run 服务——只有授权的 Google 账户才能访问它。部署后，请通过 [Cloud Console IAP 设置](https://cloud.google.com/run/docs/securing/identity-aware-proxy-cloud-run#manage_user_or_group_access) 授予用户访问权限。

对于使用自定义前端的 Agent Engine，请使用**解耦部署**——将前端单独部署到 Cloud Run 或 Cloud Storage，连接到 Agent Engine 后端 API。

---

## 回滚与恢复

主要的回滚机制是**基于 git**：修复问题、提交、推送到 `main`。CI/CD 管道将自动构建并部署新版本，通过 staging → 生产。

对于立即回滚 Cloud Run 而无需新提交，请使用修订流量转移：
```bash
gcloud run revisions list --service=SERVICE_NAME --region=REGION
gcloud run services update-traffic SERVICE_NAME \
  --to-revisions=REVISION_NAME=100 --region=REGION
```

Agent Engine 不支持基于修订的回滚——修复并重新部署，通过 `make deploy`。

对于 GKE 回滚，使用 `kubectl rollout undo`：
```bash
kubectl rollout undo deployment/DEPLOYMENT_NAME -n NAMESPACE
kubectl rollout status deployment/DEPLOYMENT_NAME -n NAMESPACE
```

---

## 自定义基础设施 (Terraform)

对于自定义基础设施模式（Pub/Sub、BigQuery、Eventarc、Cloud SQL、IAM），请参阅 `references/terraform-patterns.md`，了解：
- 自定义 Terraform 文件放置位置（开发 vs CI/CD）
- 资源示例（Pub/Sub、BigQuery、Eventarc 触发器）
- 自定义资源的 IAM 绑定
- Terraform 状态管理（远程 vs 本地，导入资源）
- 常见基础设施模式

---

## 故障排除

| 问题 | 解决方案 |
|-------|----------|
| Terraform 状态锁定 | 在 `deployment/terraform/` 中运行 `terraform force-unlock -force LOCK_ID` |
| GitHub Actions 身份验证失败 | 在 CI/CD Terraform 目录中重新运行 `terraform apply`；验证 WIF 池/提供程序 |
| Cloud Build 授权挂起 | 使用 `github_actions` 运行器 |
| 资源已存在 | `terraform import`（请参阅 `references/terraform-patterns.md`） |
| Agent Engine 部署超时/挂起 | 部署需要 5-10 分钟；检查引擎是否已创建（请参阅 Agent Engine 特定配置） |
| 密钥不可用 | 验证已向 `app_sa` 授予 `secretAccessor`（不是默认的 compute SA） |
| 部署时出现 403 | 检查 `deployment/terraform/iam.tf`——`cicd_runner_sa` 需要在目标项目中具有部署和 SA 代理角色 |
| 测试 Cloud Run 时出现 403 | 默认为 `--no-allow-unauthenticated`；包括 `Authorization: Bearer $(gcloud auth print-identity-token)` 头部 |
| 冷启动太慢 | 在 Cloud Run Terraform 配置中设置 `min_instance_count > 0` |
| Cloud Run 503 错误 | 检查资源限制（内存/CPU），增加 `max_instance_count`，或检查容器崩溃日志 |
| 授予 IAM 角色后立即出现 403 | IAM 传播不是即时的——等待几分钟再重试。不要反复授予相同的角色 |
| 资源似乎缺失但 Terraform 创建了它 | 运行 `terraform state list` 检查 Terraform 实际管理的资源。通过 `null_resource` + `local-exec`（例如，BQ 链接数据集）创建的资源不会出现在 `gcloud` CLI 输出中 |
