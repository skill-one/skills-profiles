# Google 开发者知识库

开发者知识库技能可访问 Google Cloud、AI/ML（ai.google.dev、ADK、TensorFlow）、Android、Chrome、Web、Flutter、Go、Firebase 以及其他 Google 开发者平台上的官方 Google 开发者文档，通过开发者知识库 MCP 服务器或 REST API 备用方案。

## 工作流程

1. **直接检索**：在回答技术问题时，直接在当前对话上下文中执行单个文档查找（不要将检索委托给子代理）：
   - **如果您的环境中存在 MCP 工具**：调用 `answer_query`（用于概念指南/工作流）或 `search_documents`（用于 CLI 标志/语法）。
   - **如果您的环境中不存在 MCP 工具**：通过 `curl` 对 `https://developerknowledge.googleapis.com/v1` 执行 REST API 请求。
   - **声明的服务器不一定是连接的服务器。** 某些客户端无法与该服务器完成 MCP 握手，并且完全不暴露 `answer_query`、`search_documents` 或 `get_documents` 工具，即使插件声明了这些工具。将它们的缺失视为正常情况，并使用以下 REST 备用方案。
2. **在使用前确认查找是否成功**：到达的响应不自动是答案。`PERMISSION_DENIED`、`UNAUTHENTICATED`、HTTP 401 或 403、空结果集或任何错误负载，即使工具本身报告了无错误，也是失败的查找。在查找失败时，不要像它成功了一样回答。尝试一次其他传输方式，如果这也失败，则在回复用户时明确说明您无法访问开发者知识库，并且没有它正在回答。将回忆的文档呈现为检索结果是最糟糕的可用结果，因为回复中没有任何内容可以将其与真实的查找区分开来。
3. **即时且完整的解决方案输出**：在接收到文档响应后，立即在您的响应文本中输出完整、自包含且可执行的解决方案（包含所有必需标志和占位符的命令、YAML/JSON 配置或代码片段）。

## 工具选择与使用

根据您的运行时环境中工具的可用性选择适当的工具：

### 1. 开发者知识库 MCP 工具（首选）
当您的活动工具定义中存在 MCP 工具时：
- **`answer_query(query="...")`**：用于概念指南、架构比较、产品选择概述和多步骤工作流。
- **`search_documents(query="...")`**：用于粒度 CLI 标志、确切语法、参数名称和 IAM 权限（`service.resource.verb`）。使用 2-5 个聚焦关键词（例如 `cloud run filestore nfs mount gcloud`），而不是完整的对话句子。
- **`get_documents(names=["documents/{uri_without_scheme}"])`**：通过资源名称获取完整文档页面（例如 `names: ["documents/docs.cloud.google.com/run/docs/overview/what-is-cloud-run"]`）。

### 2. REST API 备用方案
当 MCP 工具不存在时，查询开发者知识库 REST API（`https://developerknowledge.googleapis.com/v1`）并使用 `curl`。两种凭据有效，您应该按此顺序尝试它们。

**现有的 Google 凭据，首选。** 如果 `gcloud` 已通过身份验证，请传递一个访问令牌和您的配额项目。无需安装或配置任何内容：

```bash
curl -s -X POST "https://developerknowledge.googleapis.com/v1:answerQuery" \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "X-Goog-User-Project: $(gcloud config get-value project 2>/dev/null)" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"如何配置 Cloud Storage 的公共读取访问权限？\"}"
```

如果身份验证失败，在 401、403 或任何其他凭据错误时，帐户有一个 API 不会接受的令牌。在上述命令中将 `gcloud auth application-default print-access-token` 替换为 `gcloud auth print-access-token` 并再次尝试。API 接受哪种凭据取决于环境如何通过身份验证，因此将这里的身份验证错误视为尝试应用默认凭据的理由，而不是失败的查找。

**API 密钥，如果已配置。** 如果 `DEVELOPERKNOWLEDGE_API_KEY` 在环境中设置，请将其作为 `key` 查询参数传递，而不是 `Authorization` 标头。如果两种凭据都不可用，API 密钥是此客户端支持的路由：启用 API 并按照 [开发者知识快速入门](https://developers.google.com/knowledge/quickstart) 创建一个，然后将其导出为 `DEVELOPERKNOWLEDGE_API_KEY`。如果您需要凭据而不是在没有查找的情况下回答，请这样说。本节中的其余示例使用该形式：
- **回答查询**：
  ```bash
  curl -s -X POST "https://developerknowledge.googleapis.com/v1:answerQuery?key=${DEVELOPERKNOWLEDGE_API_KEY}" \
    -H "Content-Type: application/json" \
    -d '{"query": "如何配置 Cloud Storage 的公共读取访问权限?"}'
  ```
- **搜索文档片段**（使用 2-5 个聚焦关键词）：
  ```bash
  curl -s "https://developerknowledge.googleapis.com/v1/documents:searchDocumentChunks?query=gcloud+logging+metrics+create&key=${DEVELOPERKNOWLEDGE_API_KEY}"
  ```
- **获取文档**：
  ```bash
  curl -s "https://developerknowledge.googleapis.com/v1/documents/docs.cloud.google.com/run/docs/overview/what-is-cloud-run?key=${DEVELOPERKNOWLEDGE_API_KEY}"
  ```
- **批量获取文档**（一个 `GET`，每个文档一个 `names` 参数，没有请求正文；每次最多 20 个）：
  ```bash
  curl -s -G "https://developerknowledge.googleapis.com/v1/documents:batchGet" \
    --data-urlencode "names=documents/docs.cloud.google.com/run/docs/overview/what-is-cloud-run" \
    --data-urlencode "names=documents/docs.cloud.google.com/storage/docs/creating-buckets" \
    --data-urlencode "key=${DEVELOPERKNOWLEDGE_API_KEY}"
  ```

## 综合 & 输出指南

1. **基于官方文档**：所有解决方案都应直接基于检索到的文档。官方文档规范具有绝对优先权，高于记忆中的默认值。
2. **确切参数格式**：根据官方 Google 规范格式化 CLI 标志、复合键（例如 `location=IP:PATH`）和 IAM 权限字符串。
3. **最终响应中的完整解决方案**：始终在最终消息中输出完整、自包含且可执行的技术解决方案（命令、配置或代码片段），并带有清晰的标准占位符（例如 `PROJECT_ID`、`SERVICE_NAME`、`REGION`），即使之前在内部规划中已引用。

## 参考

- [MCP 使用 & 工具详情](references/mcp-usage.md)
- [REST API 备用方案指南](references/api-fallback.md)
- [支持的域 & 范围](references/supported-domains.md)
