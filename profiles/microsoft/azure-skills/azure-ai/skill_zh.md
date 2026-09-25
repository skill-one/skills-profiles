# Azure AI 服务

## 服务

| 服务 | 使用场景 | MCP 工具 | CLI |
|------|----------|----------|-----|
| AI 搜索 | 全文、向量、混合搜索 | `azure__search` | `az search` |
| 语音 | 语音转文本、文本转语音 | `azure__speech` | - |
| OpenAI | GPT 模型、嵌入、DALL-E | - | `az cognitiveservices` |
| 文档智能 | 表单提取、OCR | - | - |

## MCP 服务器（推荐）

当 Azure MCP 启用时：

### AI 搜索
- `azure__search` 使用命令 `search_index_list` - 列出搜索索引
- `azure__search` 使用命令 `search_index_get` - 获取索引详情
- `azure__search` 使用命令 `search_query` - 查询搜索索引

### 语音
- `azure__speech` 使用命令 `speech_transcribe` - 语音转文本
- `azure__speech` 使用命令 `speech_synthesize` - 文本转语音

**如果 Azure MCP 未启用：** 运行 `/azure:setup` 或通过 `/mcp` 启用。

## AI 搜索功能

| 功能 | 描述 |
|------|------|
| 全文搜索 | 语言分析、词干提取 |
| 向量搜索 | 嵌入的语义相似度 |
| 混合搜索 | 关键词 + 向量组合 |
| AI 增强 | 实体提取、OCR、情感分析 |

## 语音功能

| 功能 | 描述 |
|------|------|
| 语音转文本 | 实时和批量转录 |
| 文本转语音 | 神经语音、SSML 支持 |
| 说话人分割 | 识别谁在何时说话 |
| 定制模型 | 特定领域的词汇 |

## SDK 快速参考

要编程访问这些服务，请参阅精简的 SDK 指南：

- **AI 搜索**: [Python](references/sdk/azure-search-documents-py.md) | [TypeScript](references/sdk/azure-search-documents-ts.md) | [.NET](references/sdk/azure-search-documents-dotnet.md)
- **OpenAI**: [.NET](references/sdk/azure-ai-openai-dotnet.md)
- **视觉**: [Python](references/sdk/azure-ai-vision-imageanalysis-py.md) | [Java](references/sdk/azure-ai-vision-imageanalysis-java.md)
- **转录**: [Python](references/sdk/azure-ai-transcription-py.md)
- **翻译**: [Python](references/sdk/azure-ai-translation-text-py.md) | [TypeScript](references/sdk/azure-ai-translation-ts.md)
- **文档智能**: [.NET](references/sdk/azure-ai-document-intelligence-dotnet.md) | [TypeScript](references/sdk/azure-ai-document-intelligence-ts.md)
- **内容安全**: [Python](references/sdk/azure-ai-contentsafety-py.md) | [TypeScript](references/sdk/azure-ai-contentsafety-ts.md) | [Java](references/sdk/azure-ai-contentsafety-java.md)

## 服务详情

有关特定服务的深入文档：

- AI 搜索索引和查询 -> [Azure AI 搜索文档](https://learn.microsoft.com/azure/search/search-what-is-azure-search)
- 语音转录模式 -> [Azure AI 语音文档](https://learn.microsoft.com/azure/ai-services/speech-service/overview)
