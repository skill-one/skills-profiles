---
name: retrieving-developer-knowledge
description: 搜索、检索和整合来自 Google Cloud、AI/Gemini、Android、Chrome、Web、Flutter、Go、Firebase 以及其他 Google 开发者平台的官方 Google 开发者文档。与开发者知识 MCP 服务器（search_documents、get_documents、answer_query）或开发者知识 REST API 备用方案集成。在搜索 gcloud CLI 命令、API 语法、IAM 权限、官方文档、架构比较或产品选择概览时使用。不用于本地文件系统查找或非 Google 文档。
---

# Google 开发者知识库

开发者知识库技能通过开发者知识库 MCP 服务器或 REST API 回退，提供对 Google Cloud、AI/ML（ai.google.dev、ADK、TensorFlow）、Android、Chrome、Web、Flutter、Go、Firebase 和其他 Google 开发者平台的官方开发者文档的访问。

## 工作流程

1. **直接检索**：在回答技术问题时，直接在当前对话上下文中执行单个文档查找（不要将检索委托给子代理）：
   - **如果您的环境中存在 MCP 工具**：调用 `answer_query`（用于概念指南/工作流）或 `search_documents`（用于 CLI 标志/语法）。
   - **如果您的环境中不存在 MCP 工具**：通过 `curl` 对 `https://developerknowledge.googleapis.com/v1` 执行 REST API 请求。
   - **声明的服务器不一定是连接的服务器。** 某些客户端无法与该服务器完成 MCP 握手，并且完全不暴露 `answer_query`、`search_documents` 或 `get_documents` 工具，即使插件声明了这些工具。将它们的缺失视为正常情况，并使用下面的 REST 回退。
2. **在使用前确认查找是否成功**：到达的响应不自动是答案。`PERMISSION_DENIED`、`UNAUTHENTICATED`、HTTP 401 或 403、空结果集或任何错误负载，即使工具本身报告了没有错误，也是一种失败的查找。在查找失败时，不要像它成功了一样回答。尝试一次其他传输，如果这也失败了，请在回复用户时明确说明您无法访问开发者知识库，并且没有它正在回答。将回忆的文档呈现为检索结果是最糟糕的结果，因为回复中没有任何内容可以将其与真实的查找区分开来。
3. **立即且完整的解决方案输出**：在接收到文档响应后，立即在您的响应文本中输出完整、自包含且可执行的解决方案（带有所有必需标志和占位符的命令、YAML/JSON 配置或代码片段）。

## 工具选择与使用

根据您的运行时环境中工具的可用性选择适当的工具：

### 1. 开发者知识库 MCP 工具（首选）
当 MCP 工具存在于您的活动工具定义中时：
- **`answer_query(query="...")`**：用于概念指南、架构比较、产品选择概述和多步骤工作流。
- **`search_documents(query="...")`**：用于粒度的 CLI 标志、确切的语法、参数名称和 IAM 权限（`service.resource.verb`）。使用 2-5 个聚焦的关键字（例如，`cloud run filestore nfs mount gcloud`），而不是完整的对话句子。
- **`get_documents(names=["documents/{uri_without_scheme}"])`**：通过资源名称获取完整的文档页面（例如，`names: ["documents/docs.cloud.google.com/run/docs/overview/what-is-cloud-run"]`）。

### 2. REST API 回退
当 MCP 工具不存在时，查询开发者知识库 REST API（`https://developerknowledge.googleapis.com/v1`）使用 `curl`。两种凭证有效，您应该按此顺序尝试它们。

**现有的 Google 凭证，首选。** 如果 `gcloud` 已经过认证，请传递一个访问令牌和您的配额项目。不需要安装或配置任何内容：

```bash
curl -s -X POST "https://developerknowledge.googleapis.com/v1:answerQuery" \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "X-Goog-User-Project: $(gcloud config get-value project 2>/dev/null)" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"如何配置 Cloud Storage 的公共读取访问？\"}"
```

如果认证失败，在 401、403 或任何其他凭证错误上，帐户有一个 API 不会接受的令牌。在上述命令中将 `gcloud auth application-default print-access-token` 替换为 `gcloud auth print-access-token` 并再次尝试。API 接受哪种凭证取决于环境如何认证，因此将这里的认证错误视为尝试应用默认凭证而不是失败查找的原因。

**API 密钥，如果已配置。** 如果 `DEVELOPERKNOWLEDGE_API_KEY` 在环境中设置，请将其作为 `key` 查询参数而不是 `Authorization` 标头传递。如果既没有凭证可用，API 密钥是此客户端支持的路径：启用 API 并按照 [开发者知识快速入门](https://developers.google.com/knowledge/quickstart) 创建一个，然后将其导出为 `DEVELOPERKNOWLEDGE_API_KEY`。说您需要一个凭证而不是在没有查找的情况下回答。本节中的其余示例使用该形式：
- **回答查询**：
  ```bash
  curl -s -X POST "https://developerknowledge.googleapis.com/v1:answerQuery?key=${DEVELOPERKNOWLEDGE_API_KEY}" \
    -H "Content-Type: application/json" \
    -d '{"query": "如何配置 Cloud Storage 的公共读取访问？"}'
  ```
- **搜索文档片段**（使用 2-5 个聚焦的关键字）：
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

1. **基于官方文档**：所有解决方案都应直接基于检索到的文档。官方文档约定比记忆中的默认值具有绝对优先权。
2. **确切的参数格式**：根据官方 Google 规范格式化 CLI 标志、复合键（例如 `location=IP:PATH`）和 IAM 权限字符串。
3. **最终响应中的完整解决方案**：始终在最终消息中输出完整、自包含且可执行的技术解决方案（命令、配置或代码片段），带有清晰的标准占位符（例如 `PROJECT_ID`、`SERVICE_NAME`、`REGION`），即使之前在内部规划中已引用。

## 参考

- [MCP 使用 & 工具详情](references/mcp-usage.md)
- [REST API 回退指南](references/api-fallback.md)
- [支持的域 & 范围](references/supported-domains.md)
