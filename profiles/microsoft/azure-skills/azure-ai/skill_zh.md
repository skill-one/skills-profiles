# Azure AI Services

## 服务

| 服务 | 使用场景 | MCP 工具 | CLI |
|---------|----------|-----------|-----|
| AI Search | 全文、向量、混合检索 | `azure__search` | `az search` |
| 语音识别 | 语音转文本、文本转语音 | `azure__speech` | - |
| OpenAI | GPT 模型、嵌入、DALL-E | - | `az cognitiveservices` |
| 文档智能 | 表单提取、OCR | - | - |

## MCP Server（推荐）

当启用 Azure MCP 时：

### AI 搜索
- 使用 `azure__search` 并执行 `search_index_list` 命令 - 列出搜索索引
- 使用 `azure__search` 并执行 `search_index_get` 命令 - 获取索引详情
- 使用 `azure__search` 并执行 `search_query` 命令 - 查询搜索索引

### 语音识别
- 使用 `azure__speech` 并执行 `speech_transcribe` 命令 - 语音转文本
- 使用 `azure__speech` 并执行 `speech_synthesize` 命令 - 文本转语音

**如果未启用 Azure MCP：** 运行 `/azure:setup` 或通过 `/mcp` 启用。

## AI 搜索功能

| 功能 | 说明 |
|---------|-------------|
| 全文检索 | 语言分析、词干还原 |
| 向量检索 | 基于嵌入的语义相似性 |
| 混合检索 | 关键词与向量相结合 |
| AI 增强 | 实体提取、OCR、情感分析 |

## 语音识别功能

| 功能 | 说明 |
|---------|-------------|
| 语音转文本 | 实时和批量转录 |
| 文本转语音 | 神经语音、SSML 支持 |
| 说话人分离 | 识别说话时间与说话人 |
| 自定义模型 | 领域特定词汇 |

## SDK 快速参考

如需对这些服务进行程序化访问，请参阅精简版的 SDK 指南：

- **AI 搜索**：[Python](references/sdk/azure-search-documents-py.md) | [TypeScript](references/sdk/azure-search-documents-ts.md) | [.NET](references/sdk/azure-search-documents-dotnet.md)
- **OpenAI**：[.NET](references/sdk/azure-ai-openai-dotnet.md)
- **视觉**：[Python](references/sdk/azure-ai-vision-imageanalysis-py.md) | [Java](references/sdk/azure-ai-vision-imageanalysis-java.md)
- **转录**：[Python](references/sdk/azure-ai-transcription-py.md)
- **翻译**：[Python](references/sdk/azure-ai-translation-text-py.md) | [TypeScript](references/sdk/azure-ai-translation-ts.md)
- **文档智能**：[.NET](references/sdk/azure-ai-document-intelligence-dotnet.md) | [TypeScript](references/sdk/azure-ai-document-intelligence-ts.md)
- **内容安全**：[Python](references/sdk/azure-ai-contentsafety-py.md) | [TypeScript](references/sdk/azure-ai-contentsafety-ts.md) | [Java](references/sdk/azure-ai-contentsafety-java.md)

## 服务详情

有关特定服务的深度文档：

- AI 搜索索引与查询 -> [Azure AI 搜索文档](https://learn.microsoft.com/azure/search/search-what-is-azure-search)
- 语音转录模式 -> [Azure AI 语音文档](https://learn.microsoft.com/azure/ai-services/speech-service/overview)
