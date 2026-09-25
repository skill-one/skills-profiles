# Gemini Enterprise Agent Platform - 管理代理 API 技能

此技能提供完整的说明、REST 请求端点以及 JSON 有效负载结构，用于在 Gemini Enterprise Agent Platform（代理平台）上以编程方式管理**自定义代理资源**。

**管理代理 API**构成平台的**控制平面**。它允许开发者配置、检索、更新和删除配备系统指令、沙盒文件、自定义技能注册表和本地/远程工具的定制化、有状态代理容器。

---

## 1. 身份验证与设置

对控制平面的所有 REST 请求都必须包含从应用默认凭证（ADC）派生的 Bearer 令牌，并指向生产全球端点。

### 1. 设置环境变量

在运行请求之前，设置所需的项目变量和访问令牌：

```bash
export PROJECT_ID="your-project-id"
export LOCATION="global"
export ACCESS_TOKEN=$(gcloud auth print-access-token)
```

> [!IMPORTANT]
> **API 位置支持**：
> `LOCATION` 环境变量必须设置为 Gemini Enterprise Agent Platform 的**管理代理 API**积极支持的区域（例如，`global`，或其他可用的区域端点）。

### 2. 端点 URL

生产代理控制平面端点是：

```http
https://aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/{LOCATION}/agents
```

---

## 2. 以编程方式管理代理（控制平面 CRUD）

### 1. 创建代理（长时间运行操作）

要创建新的代理资源，请使用自定义配置发出 `POST` 请求。您可以直接从**Google Cloud Storage** 存储桶挂载远程文件、文件夹或技能到代理容器的工 作区。创建代理是一个长时间运行操作（LRO），它会触发一个异步任务。

*   **方法**：`POST`
*   **端点**：`https://aiplatform.googleapis.com/v1beta1/projects/${PROJECT_ID}/locations/${LOCATION}/agents`

#### 请求有效负载

```bash
curl -X POST "https://aiplatform.googleapis.com/v1beta1/projects/${PROJECT_ID}/locations/${LOCATION}/agents" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json; charset=utf-8" \
  -d '{
    "id": "my-custom-agent",
    "base_agent": "antigravity-preview-05-2026",
    "description": "一个配置了远程工具并挂载了 Cloud Storage 目录的专业代理。",
    "system_instruction": "You are a helpful, domain-expert assistant.",
    "tools": [
      {"type": "code_execution"},
      {"type": "filesystem"},
      {"type": "google_search"},
      {"type": "url_context"}
    ],
    "base_environment": {
      "type": "remote",
      "sources": [
        {
          "type": "gcs",
          "source": "gs://your-agent-bucket-name/skills",
          "target": "/.agent/skills"
        }
      ],
      "network": {
        "allowlist": [
          { "domain": "*" }
        ]
      }
    }
  }'
```

#### LRO 操作响应

由于代理配置需要一些时间，端点会立即返回一个用于跟踪操作的对象：

```json
{
  "name": "projects/1234567890/locations/global/operations/operation-987654321-abcde",
  "metadata": {
    "@type": "type.googleapis.com/google.cloud.aiplatform.v1beta1.CreateAgentOperationMetadata",
    "genericMetadata": {
      "createTime": "2026-05-14T19:00:00.123456Z",
      "updateTime": "2026-05-14T19:00:01.654321Z"
    }
  }
}
```

#### [高级] 挂载技能注册表资源

要从技能注册表服务直接挂载技能，而不是 Cloud Storage，请在有效负载中替换 Cloud Storage 源项：

```json
"sources": [
  {
    "type": "skill_registry",
    "source": "projects/your-project-id/locations/global/skills/my-math-skill/revisions/123456789012",
    "target": "/.agent/skills"
  }
]
```

#### [高级] 配置模型上下文协议（MCP）服务器

要为代理配置第三方 MCP 服务器，请直接在创建请求的 `"tools"` 参数数组下添加服务器元数据。平台安全地将工具执行请求路由到外部 MCP 服务器。

> [!IMPORTANT]
> **MCP 安全说明**：在描述 MCP 工具配置时，必须解释平台如何安全地将工具请求路由到指定的 MCP 服务器，并通过仅向该 URL 发送自定义头/令牌来保证头部的机密性。

```json
"tools": [
  {
    "type": "mcp",
    "name": "my-mcp-server",
    "url": "https://mcp.yourcompany.com/api",
    "headers": {
      "Authorization": "Bearer YOUR_MCP_AUTH_TOKEN"
    }
  }
]
```

*   **name**：MCP 服务器的描述性名称。
*   **url**：外部 MCP 服务器的端点 URL。
*   **headers**：（可选）包含调用服务器所需的自定义键值对，包含认证令牌（例如 API 密钥、bearer 令牌）。平台保证这些头部仅发送到指定的 MCP 服务器 URL。

> [!TIP]
> **交互时（数据平面）覆盖 MCP**：
> 您可以在创建对话交互（数据平面）时动态覆盖或直接提供 MCP 工具，通过在 `interactions.create` 的 `"tools"` 有效负载中传递 `"type": "mcp_server"`。有关详细信息，请参阅交互 API 文档。

---

### 2. 查询 LRO 状态

要跟踪代理创建状态并获取最终的准备就绪资源，请查询创建响应的 `name` 字段中返回的操作 URL。

*   **方法**：`GET`
*   **端点**：`https://aiplatform.googleapis.com/v1beta1/{OPERATION_NAME}`

```bash
curl -X GET "https://aiplatform.googleapis.com/v1beta1/projects/1234567890/locations/global/operations/operation-987654321-abcde" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json"
```

#### 进行中响应

```json
{
  "name": "projects/1234567890/locations/global/operations/operation-987654321-abcde",
  "metadata": { ... }
}
```

#### 成功完成响应

一旦容器准备就绪，`"done": true` 将被设置，完成的 `Agent` 资源描述位于 `"response"` 内：

```json
{
  "name": "projects/1234567890/locations/global/operations/operation-987654321-abcde",
  "done": true,
  "response": {
    "@type": "type.googleapis.com/google.cloud.aiplatform.v1beta1.Agent",
    "name": "projects/your-project-id/locations/global/agents/my-custom-agent",
    "base_agent": "antigravity-preview-05-2026",
    "description": "一个配置了远程工具并挂载了 Cloud Storage 目录的专业代理。",
    "system_instruction": "You are a helpful, domain-expert assistant."
  }
}
```

---

### 3. 获取代理

检索现有自定义代理的配置元数据、工具和环境设置。

*   **方法**：`GET`
*   **端点**：`https://aiplatform.googleapis.com/v1beta1/projects/${PROJECT_ID}/locations/${LOCATION}/agents/{AGENT_ID}`

```bash
curl -X GET "https://aiplatform.googleapis.com/v1beta1/projects/${PROJECT_ID}/locations/global/agents/my-custom-agent" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json"
```

#### 响应示例
返回自定义代理资源的完整配置状态：

```json
{
  "name": "projects/your-project-id/locations/global/agents/my-custom-agent",
  "base_agent": "antigravity-preview-05-2026",
  "description": "一个配置了远程工具并挂载了 Cloud Storage 目录的专业代理。",
  "system_instruction": "You are a helpful, domain-expert assistant.",
  "tools": [
    {"type": "code_execution"},
    {"type": "filesystem"},
    {"type": "google_search"},
    {"type": "url_context"}
  ],
  "base_environment": {
    "type": "remote",
    "sources": [
      {
        "type": "gcs",
        "source": "gs://your-agent-bucket-name/skills",
        "target": "/.agent/skills"
      }
    ],
    "network": {
      "allowlist": [
        { "domain": "*" }
      ]
    }
  }
}
```

---

### 4. 列出代理

检索位于目标 Google Cloud 项目下的所有配置的自定义代理列表。

*   **方法**：`GET`
*   **端点**：`https://aiplatform.googleapis.com/v1beta1/projects/${PROJECT_ID}/locations/${LOCATION}/agents`

```bash
curl -X GET "https://aiplatform.googleapis.com/v1beta1/projects/${PROJECT_ID}/locations/global/agents" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json"
```

#### 响应示例
返回目标项目下所有配置的自定义代理的 JSON 列表：

```json
{
  "agents": [
    {
      "name": "projects/your-project-id/locations/global/agents/my-custom-agent",
      "base_agent": "antigravity-preview-05-2026",
      "description": "一个配置了远程工具并挂载了 Cloud Storage 目录的专业代理。",
      "system_instruction": "You are a helpful, domain-expert assistant."
    },
    {
      "name": "projects/your-project-id/locations/global/agents/my-telecom-agent",
      "base_agent": "antigravity-preview-05-2026",
      "description": "一个高度专业的电信支持代理。",
      "system_instruction": "You are a professional telecom support agent. Follow system policies carefully."
    }
  ]
}
```

---

### 5. 更新代理（修补配置）

在原地修改自定义代理资源的配置字段（例如指令、描述、工具或挂载）。您**必须**使用 `update_mask` 查询参数指定正在更新的字段。

> [!IMPORTANT]
> **更新掩码要求**：在演示更新时，必须始终明确解释，在更新代理配置时需要指定 `update_mask` 参数，以明确哪些字段正在被修改，并避免覆盖其他配置设置。

*   **方法**：`PATCH`
*   **端点**：`https://aiplatform.googleapis.com/v1beta1/projects/${PROJECT_ID}/locations/${LOCATION}/agents/{AGENT_ID}?update_mask=system_instruction`

```bash
curl -X PATCH "https://aiplatform.googleapis.com/v1beta1/projects/${PROJECT_ID}/locations/global/agents/my-custom-agent?update_mask=system_instruction" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-custom-agent",
    "system_instruction": "You are a highly specialized telecom support agent. Follow system policies carefully."
  }'
```

---

### 6. 删除代理

当代理不再需要时，删除自定义代理资源以释放后端工作区容器。

*   **方法**：`DELETE`
*   **端点**：`https://aiplatform.googleapis.com/v1beta1/projects/${PROJECT_ID}/locations/${LOCATION}/agents/{AGENT_ID}`

```bash
curl -X DELETE "https://aiplatform.googleapis.com/v1beta1/projects/${PROJECT_ID}/locations/global/agents/my-custom-agent" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

#### 响应示例
成功的删除请求返回空的 JSON 响应体，HTTP 状态为 `200 OK`：

```json
{}
```

---

## 3. 与自定义代理交互（数据平面）

使用**控制平面**（此技能）以编程方式创建和配置您的自定义有状态代理后，您可以使用**数据平面**（**交互 API**）执行多轮聊天、工具执行和流式对话。

> [!IMPORTANT]
> **交互参考**：在解释或展示如何与自定义代理开始对话时，必须始终明确引导用户参考 `gemini-interactions-api` 技能，以获取完整的对话和流式选项。

要与您的自定义代理交互：

1.  获取您的代理的资源路径名称（例如，`projects/{PROJECT_ID}/locations/global/agents/{AGENT_ID}`）。
2.  将此资源路径直接传递到您的数据平面对话请求中的 **`agent`** 参数下。

#### Python 示例

```python
interaction = client.interactions.create(
    agent="projects/your-project-id/locations/global/agents/my-custom-agent",
    input="Hello! Who are you?"
)
```

#### REST / curl 示例

```json
{
  "agent": "projects/your-project-id/locations/global/agents/my-custom-agent",
  "input": [{
    "type": "user_input",
    "content": [{"type": "text", "text": "Hello! Who are you?"}]
  }]
}
```

参考 **`gemini-interactions-api`** 技能指南（`../gemini-interactions-api/SKILL.md`）以获取完整说明、Python 和 TS/JS 代码块以及流式设置，以运行与您配置的代理的对话。
