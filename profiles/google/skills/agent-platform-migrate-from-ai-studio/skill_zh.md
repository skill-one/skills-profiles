# 从 AI Studio 的 Gemini API 迁移到 Agent 平台

在您需要将应用程序从以开发者为中心的 Google AI Studio 生态系统（`generativelanguage.googleapis.com`）迁移到企业级 Google Cloud Agent 平台（`aiplatform.googleapis.com`）时，请使用此技能。

--------------------------------------------------------------------------------

## 何时调用此技能

*   您希望将应用程序从 Google AI Studio 迁移到 Agent 平台（以前称为 Vertex AI）。
*   您拥有 **Google Cloud 信用额度**（例如，$300 的欢迎免费试用），希望将其用于 Gemini API 推理成本。
*   您需要统一您的推理管道、IAM 权限、遥测数据和计费，以与现有的 Google Cloud 基础设施（Compute Engine、Cloud SQL、BigQuery）保持一致。
*   您正在 Google Cloud VM 上部署开源编排引擎（如 OpenClaw 或 ADK 代理），并希望整个系统在统一的 Google Cloud 计费结构下运行。

--------------------------------------------------------------------------------

## Gemini API 对比

功能 / 控制      | Google AI Studio (Gemini 开发者 API)                               | Agent 平台 (企业 Gemini API)
:--------------------- | :-------------------------------------------------------------------- | :-------------------------------------
**API 端点**       | `generativelanguage.googleapis.com`                                   | `aiplatform.googleapis.com`
**目标受众**    | 开发者、初创公司、学生、研究人员构建生产应用程序。                     | 企业生产、MLOps 工程师
**GCP 信用额度支持** | 否（GCP 信用额度/免费试用 **不能** 应用）                     | 是（完全由欢迎或自定义信用额度覆盖）
**数据隐私**       | 数据可能会被审查以改进 Google 产品                       | 提示/响应**永远不会**用于训练
**安全 & IAM**     | API 密钥、OAuth                                                        | Google Cloud IAM（服务账户、OAuth 2.0、VPC-SC）
**合规性 & SLA**  | 无（尽力提供可用性）                                       | 24/7 企业支持、SLA、HIPAA、SOC2
**吞吐量选项** | 共享 / 速率限制                                                 | 按需付费 OR 预配吞吐量
**MLOps 生态系统**    | 基本提示管理                                               | 模型注册、模型监控、管道评估
**推理范围**  | 仅全局端点仅                                                 | 全局和严格区域端点

有关这两个产品之间差异的更多信息，请参阅
[Google Cloud 文档](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/migrate/migrate-google-ai.md.txt)。

--------------------------------------------------------------------------------

## 迁移指南

### 计费和信用额度

Google Cloud 免费试用信用额度
**[不适用于 AI Studio](https://docs.cloud.google.com/free/docs/free-cloud-features.md.txt)**。
要使用您的信用额度为 Gemini 模型付费，您必须通过 Agent 平台路由调用。

1.  创建一个 Google Cloud 计费账户。在设置过程中，您必须提供有效的支付方式以验证身份。
2.  如果您是新客户，请确保您的 $300 欢迎信用额度在计费控制台中处于活动状态。
3.  **避免计费意外：** 为防止信用额度用尽时自动回退到您的标准支付方式，您应该建立预算警报：
    *   转到 **计费** -> **预算和警报** -> **创建预算**。
    *   将阈值设置为映射到您的信用额度上限或最大舒适支出。

### 启用 Agent 平台 API

您必须在您的目标 Google Cloud 项目上显式启用 Agent 平台 API。通过您的本地 shell 运行以下命令：

```bash
gcloud services enable aiplatform.googleapis.com --project="{project_id}"
```

### 身份验证 & 授权 (IAM)

#### 用户认证

对于本地调试或脚本执行，使用
[应用默认凭证](https://docs.cloud.google.com/docs/authentication/application-default-credentials.md.txt)
(ADC) 进行身份验证。

**选项 1 - 自动脚本**：

```bash
bash <(curl -sSL https://storage.googleapis.com/cloud-samples-data/adc/setup_adc.sh)
```

**选项 2 - 手动设置**：

```bash
gcloud auth login
gcloud auth application-default login
```

授予您的用户身份执行推理调用所需的 IAM 角色：

```bash
gcloud projects add-iam-policy-binding "{project_id}" \
    --member="user:YOUR_EMAIL@domain.com" \
    --role="roles/aiplatform.user"
```

#### 服务认证

当您的应用程序在 Google Cloud 基础设施（如 Compute Engine VM）上运行时，使用附加到机器的 Service Account 进行身份验证。例如，
[Compute Engine 默认 Service Account](https://docs.cloud.google.com/compute/docs/access/service-accounts#default_service_account.md.txt)。

1.  授予虚拟机底层 Service Account 用户角色：

```bash
gcloud projects add-iam-policy-binding "{project_id}" \
    --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/aiplatform.user"
```

2.  **[Compute Engine 访问范围](https://docs.cloud.google.com/compute/docs/access/service-accounts.md.txt):**
    遗留访问范围可以覆盖 IAM 绑定。在创建或修改您的 Compute Engine 实例时，您必须验证虚拟机访问范围是否配置为
    **允许对所有 Cloud API 的完全访问**
    (`https://www.googleapis.com/auth/cloud-platform`) 或明确包含标准 cloud-platform 范围。

--------------------------------------------------------------------------------

## 在 Agent 平台中使用 Gemini API

### SDK（客户端库）

您仍然可以使用统一的
[Google GenAI SDK](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/sdks/overview.md.txt)
(`google-genai`)。此 SDK 与 AI Studio 和 Agent 平台都兼容。您只需要通过您的运行时环境变量切换路由标志，以针对 Agent 平台后端。

设置您的目标环境详细信息：

```bash
export GOOGLE_CLOUD_PROJECT="{project_id}"
export GOOGLE_CLOUD_LOCATION="global"  # 或您选择的区域端点
export GOOGLE_GENAI_USE_ENTERPRISE=TRUE
```

现在，您的标准 python 代码从使用 AI Studio 转移到 Agent Platform，而无需更改核心初始化块：

```python
from google import genai

# 客户端会自动检测到 GOOGLE_GENAI_USE_ENTERPRISE=TRUE 环境标志
client = genai.Client()

response = client.models.generate_content(
    model='gemini-3-flash-preview',
    contents='Hello world!',
)
print(response.text)
```

### 代理开发套件 (ADK)

要从 Agent 平台中的代理开发套件代理调用 Gemini 模型，请按照以下步骤操作。

1.  身份验证到 Google Cloud。

如果在一个 ADK 代理在 Google Cloud 中运行（例如 Agent 平台运行时），请使用分配给代理的 Service Account。或者，如果本地运行 ADK，请运行：

```bash
gcloud auth application-default login
```

1.  设置环境变量。无论您的 ADK 代理是在 Google Cloud 中运行还是本地运行，请确保这些变量已设置：

```bash
export GOOGLE_CLOUD_PROJECT="{project_id}"
export GOOGLE_CLOUD_LOCATION="global"
export GOOGLE_GENAI_USE_ENTERPRISE=TRUE
```

2.  初始化 ADK 代理。您可以使用与 AI Studio 使用的相同模型字符串（例如 `gemini-3-flash-preview`）。

```python
from google.adk.agents.llm_agent import Agent

def get_current_time(city: str) -> dict:
    """返回指定城市的当前时间。"""
    return {"status": "success", "city": city, "time": "10:30 AM"}

root_agent = Agent(
    model='gemini-3-flash-preview',
    name='root_agent',
    description="告诉指定城市的当前时间。",
    instruction="您是一个乐于助人的助手，告诉指定城市的当前时间。使用 'get_current_time' 工具为此目的。",
    tools=[get_current_time],
)
```

有关将 ADK 代理与 Agent 平台集成的更多信息，
[请参阅 ADK 文档](https://raw.githubusercontent.com/google/adk-docs/main/docs/agents/models/agent-platform.md)。

### Antigravity CLI

Google Cloud 用户现在可以访问
[Antigravity 2.0](https://antigravity.google/pricing)，包括 Antigravity CLI，以及 Gemini 企业 Agent 平台。

1.  [安装 Antigravity CLI](https://antigravity.google/docs/cli-install)
    到您的本地环境。
2.  启动 Antigravity CLI。

    ```bash
    agy
    ```

3.  按照 CLI 设置提示操作 - 选择 **使用 Google Cloud 项目**。

4.  在打开的浏览器窗口中完成 OAuth 流程，使用您的经过身份验证的 Google Cloud Workspace 或用户身份。

5.  复制确认令牌，并将其直接粘贴回您的终端。

6.  按照提示输入您的 Google Cloud 项目 ID。

7.  选择您的 Google Cloud 位置（例如 `global`）。

8.  可选地，运行 `/model` 命令以在 Agent 平台中选择不同的 Gemini 模型。

### OpenClaw

要配置 OpenClaw 代理以在 Agent 平台中使用 Gemini 模型，请按照以下步骤操作。

1.  [按照 OpenClaw 的官方说明安装 OpenClaw](https://docs.openclaw.ai/install)。

⚠️ 重要提示：OpenClaw 2026.5.28 目前存在 `google-vertex` 错误。请暂时使用 2026.5.20。

2.  确保运行 OpenClaw 的运行时（例如具有 Service Account 的 GCE VM）具有 `aiplatform.user` IAM 角色 - 请参阅上面的身份验证和授权部分。

3.  从用户的项目 ID 获取项目编号。在 GCE 外运行：

```bash
export PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format="value(projectNumber)")
echo "Project number: $PROJECT_NUMBER"

```

在 Compute Engine VM 中运行：

```bash
export PROJECT_NUMBER=$(curl "http://metadata.google.internal/computeMetadata/v1/project/project-id" -H "Metadata-Flavor: Google")
echo "Project number: $PROJECT_NUMBER"
```

4.  从 GCE 实例外部，使用 Google Cloud 项目编号生成 `GOOGLE_APPLICATION_CREDENTIALS`
    然后，`scp` 这些凭证到 GCE VM。

```bash
mkdir -p ~/.config/gcloud
gcloud iam service-accounts keys create ~/.config/gcloud/application_default_credentials.json --iam-account="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
```

> ⚠️ **解决新组织的策略约束问题**：新 Google Cloud 组织（在 2024 年 5 月 4 日或之后创建的）执行一个 [限制 Service Account 密钥创建的遗留组织策略](https://docs.cloud.google.com/organization-policy/restrict-service-accounts.md.txt)。要完成此步骤，必须暂时禁用此组织策略。
> 组织策略管理员必须将此策略设置为非活动状态。代理：检查是否强制执行此策略，如果是：暂停，并提示用户在此控制台链接处禁用它：
> https://console.cloud.google.com/iam-admin/orgpolicies


5.  编辑通常位于以下位置的配置文件：
    `~/.openclaw/openclaw.json`。确保您将 Gemini 模型前缀为
    `google-vertex/`。

> ⚠️ 重要提示：不要使用 Gemini 3.5 模型，因为 OpenClaw 的 `google-vertex`
> 提供者尚不支持它。旧模型可以工作。在 Agent 平台中使用
> [Gemini 3 Flash Preview](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/gemini/3-flash)
> 模型时，始终将位置设置为 `global`，而不是区域端点。

```json
{
  "env": {
    "vars": {
      "GOOGLE_CLOUD_PROJECT": "PROJECT_ID",
      "GOOGLE_CLOUD_LOCATION": "global",
      "GOOGLE_APPLICATION_CREDENTIALS": "~/.config/gcloud/application_default_credentials.json"
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "google-vertex/gemini-3-flash-preview"
      },
      "workspace": "~/.openclaw/workspace",
      "compaction": {
        "mode": "safeguard"
      },
      "heartbeat": {
        "model": "google-vertex/gemini-3-flash-preview"
      }
    },
    "list": [
      {
        "id": "main",
        "workspace": "~/.openclaw/workspace",
        "model": "google-vertex/gemini-3-flash-preview"
      }
    ]
  },
  "session": {
    "dmScope": "per-channel-peer"
  },
  "tools": {
    "profile": "coding"
  }
}

```

6.  重启 OpenClaw。

```bash
openclaw gateway restart

```

7.  验证 OpenClaw 与 Agent 平台的连接：

```bash
openclaw models status
openclaw agent --agent main --message "Hello world!"

```

--------------------------------------------------------------------------------

## 其他资源

*   [Google Cloud 免费试用功能和限制](https://docs.cloud.google.com/free/docs/free-cloud-features.md.txt)
*   [从 Google AI Studio 迁移到 Gemini 企业 Agent 平台](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/migrate/migrate-google-ai.md.txt)
*   [Gemini 企业 Agent 平台 - 模型](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/google-models.md.txt)
*   [代理开发套件文档 - 连接到 Agent 平台中的模型](https://adk.dev/agents/models/agent-platform/#agent-platform-setup)
*   [OpenClaw 文档 - 连接到 Google 模型](https://docs.openclaw.ai/providers/google)
*   [Google Cloud 预算警报 - 设置指南](https://docs.cloud.google.com/billing/docs/how-to/budgets#steps-to-create-budget.md.txt)
