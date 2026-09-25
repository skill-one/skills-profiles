# 使用 Exa 构建

## 范围

默认包含：

- 核心检索 API：搜索端点、内容端点、答案端点
- 长时运行的研究工作流：Agent API (`/agent`)
- 异步和周期性工作流：Monitors API
- 遗留界面：Websets API（仅限现有集成；新的集合构建工作使用 Agent API）
- SDK 指导：Python `exa-py`、TypeScript `exa-js`

> 数据保留注意事项：`/search`、`/answer` 和 `/agent/` 提供零数据保留 (ZDR)。Websets 和 Monitors 不支持 ZDR。如果用例需要 ZDR，请保持在 ZDR 界面或联系 Exa。

## 安装

```bash
# Python
pip install exa-py

# TypeScript / JavaScript
npm install exa-js
```

使用包管理器安装最新 SDK 版本，以便解析最新版本，所有 SDK 界面都将可用。

## 认证

```bash
export EXA_API_KEY="your_api_key_here"
```

Exa 接受 `x-api-key` 头或 `Authorization: Bearer <key>`。

推荐的 Exa 搜索请求是查询加上高效的文本提取，除此之外不做其他。文本提取是一个建议，不是服务器默认设置：省略 `contents`，结果将仅包含元数据（标题、URL、日期），不包含页面内容。

```json
{
  "query": "最新的大型语言模型发展",
  "type": "auto",
  "contents": { "highlights": true }
}
```

**其他所有请求字段都是受限制的：仅在用户的任务明确要求时才添加。** 不要重复服务器默认设置，也不要添加控件，因为它们看起来可能有用。特别是：

- `type` 默认为 `auto`；明确声明 `type: "auto"` 是可以的，但如果任务不需要其他模式（例如延迟敏感的 UI 或深度合成），不要发送其他模式。
- `numResults` 默认为 10；除非任务需要不同数量的结果，否则省略 `numResults`。仅作为有意的产品决策设置它，而不是作为样板代码。
- 省略 `category`。仅在用户明确要求受类别限制的检索时使用它。
- `includeDomains` 和 `excludeDomains` 应仅在用户明确请求硬允许列表或阻止列表并提供或批准其内容时设置。通过查询短语或 `systemPrompt` 表达源偏好。
- `maxAgeHours` 应仅在提取的页面内容必须是最新的时设置。它限制缓存年龄，直到进行实时爬取；它不是一个发布时效过滤器。
- 对于“最新故事”任务，将时效性放在查询中（“最新”、“最近”）。`startPublishedDate` / `endPublishedDate` 是硬过滤器，会丢弃未标记日期和错误标记的页面；仅在任务声明必须强制执行的有限窗口时添加它们（“过去七天”、“2026 年发布”）。不要使用 `maxAgeHours`。
- `highlights` 应默认为 `true`，除非另有指定。除非任务中有明确的预算要求，否则不要添加 `maxCharacters` 或其他高亮选项。

## API 决策工作流

在选择端点之前，确定哪种工作流形状适合：

- 为自己的 LLM 或代理提供原始网页内容：使用 `/search` 并添加上述推荐请求
- 需要特定输出形状，或必须从页面中提取或合成字段：使用 `/search` 并添加 `outputSchema`（如果需要行为指导，则添加 `systemPrompt`）。用户不必说“JSON”或“schema”：“每篇文章报告的资助金额”、“每个人的姓名、标题和公司”，或结果必须携带但有时不携带的元数据字段（例如必需的作者）都是结构化输出请求。结果已经携带的字段（标题、URL、发布日期）不是：推荐使用 `numResults` 请求“10 篇带有标题和 URL 的文章”。紧凑的架构（每篇文章的作者和 URL）保持为 `auto`；`type: "deep"` 当架构较宽或其字段需要多个搜索来填充时，因为它会运行多个搜索。参见 `references/search.md` 中的结构化输出。
- 长时运行的多步骤研究、列表构建或结构化输出丰富：使用 Agent API (`/agent`)，其字段规则与 `outputSchema` 相同

**默认使用搜索端点。** 对于大多数新集成，使用搜索端点 (`/search`)，然后在任务形状明显需要时才迁移到更专业的 Exa 界面。

1. 需要一般语义网页检索、合成输出或从搜索结果中提取内容：使用搜索端点 (`/search`)
2. 已经知道 URL 并需要干净的页面提取或新鲜度控制：使用内容端点 (`/contents`)
3. 需要已知种子 URL 相关的页面：使用搜索端点 (`/search`) 并添加从页面派生的查询（例如标题、主题或来自 `/contents` 的文本）
4. 需要带有引用的无 LLM 生成的基础答案：使用答案端点 (`/answer`)。如果产品已经有一个聊天 LLM，则将其作为工具提供给 `/search`。
5. 需要与 OpenAI SDK 兼容的聊天或响应客户端：使用 OpenAI 兼容端点 (`/chat/completions`, `/responses`)
6. 需要异步多步骤研究、列表构建、丰富或基于先前研究的问题：使用 Agent API (`/agent`)
7. 需要带 webhook 交付的定期搜索：使用 Monitors API (`/monitors`)
8. 维护现有的 Websets 集成：参见迁移指南 (`references/migrate-websets-to-agent.md`) 并迁移到 Agent API (`references/agent.md`)。不要为新工作使用 Websets；使用 Agent API 代替。
9. 需要过去某个时间点的页面内容（用于回测代理、可重复的评估、比较早期版本的文档、定价页面、政策或报告）：使用 Exa Snapshot，`snapshotAsOf` 字段在 `/contents`（顶层）或 `/search`（在 `contents` 内部）。参见 `references/snapshot.md`。

## 快速入门

有关更完整的示例，请参见下表中的相关参考文件。

**Python** (`/search`):

```python
from exa_py import Exa

exa = Exa(api_key="YOUR_EXA_API_KEY")
result = exa.search(
    "最新的大型语言模型发展",
    type="auto",
    contents={"highlights": True}
)

for item in result.results:
    print(item.title, item.url)
```

**TypeScript** (`/search`):

```typescript
import Exa from "exa-js";

const exa = new Exa();
const result = await exa.search("最新的大型语言模型发展", {
  type: "auto",
  contents: { highlights: true }
});

for (const item of result.results) {
  console.log(item.title, item.url);
}
```

**原始 HTTP** (`/search`):

```bash
curl -X POST "https://api.exa.ai/search" \
  -H "Content-Type: application/json" \
  -H "x-api-key: $EXA_API_KEY" \
  -d '{
    "query": "最新的大型语言模型发展",
    "type": "auto",
    "contents": {
      "highlights": true
    }
  }'
```

## 严重陷阱

- 不要无理由装饰推荐的请求。在没有明确任务要求的情况下添加 `category`、域过滤器、样板 `numResults` 或新鲜度控制是最常见的集成错误。
- 不要用简单的搜索回答提取请求。必须从页面中提取的字段，或用户要求在每条结果中都必须包含的元数据字段，应放在 `outputSchema` 中；保留/丢弃规则应放在 `systemPrompt` 中；`query` 仅表示检索意图。如果查询的某个子句说 `only`、`include`、`exclude`、`drop` 或 `return`，它就在错误的字段中。不要为每条结果已经携带的字段（标题、URL、发布日期）添加 `outputSchema`。
- 在搜索端点中，`text`、`highlights` 和 `summary` 应在 `contents` 内部，而不是在顶层。
- 在内容端点中，`text`、`highlights` 和 `summary` 是顶层字段，而不是嵌套在 `contents` 中。
- 选择 `highlights`、`text` 或 `summary` 中的一个。不要堆叠它们。`summary` 需要明确的用户请求，以便 Exa 在每条结果上进行合成。
- 几乎所有任务都应该使用 `highlights: true`。`numSentences` 和 `highlightsPerUrl` 已弃用，`maxCharacters` 需要有明确的预算要求。
- 列表构建和丰富工作流应属于 Agent API (`/agent`)，而不是在 `/search` 中使用 `category: "people"` 或 `category: "company"`。这些类别仅用于检索原始人员或公司文档。
- `maxAgeHours` 控制爬取/缓存新鲜度（提取的页面内容在实时爬取之前可以有多旧），而不是发布时效。不要将其用作“最新结果”控制；时效性应在查询短语中。`startPublishedDate` / `endPublishedDate` 用于必须强制执行的有限窗口（“过去七天”、“2026 年”），而不是用于“最近”或“最新”。
- 不要凭空创造类别值，如 `github`、`documentation`、`qa` 或 `pdf`。当用户确实请求受类别限制的检索时，请先检查搜索参考：专用类别（如 `people` 和 `company`）会限制哪些过滤器是有效的。
- OpenAI 兼容端点用于兼容性优先的使用场景。当您希望更清晰的请求语义时，优先考虑原生 Exa 端点进行新集成。
- 不要将 `/agent` 视为 `/search` 的即插即用替代品。它是高延迟的异步操作，因此当工作流形状确实是适合时，请使用专用的 Agent 参考。对于新的集合构建工作，优先使用它而不是 Websets。
- Agent 请求应始终明确设置 `effort`，通过轮询或 SSE 等待终端状态，并在读取 `output` 之前检查运行结束的方式，并在相关情况下暴露 `output.grounding`。
- 将 `/findSimilar` 视为已弃用。优先使用 `/search`（可选地在种子 URL 上使用 `/contents`）进行相关页面发现。

## 参考文件

| 文件 | 主题 |
|------|------|
| [references/search.md](references/search.md) | 搜索端点请求/响应形状、搜索类型、过滤器、嵌套内容、结构化输出 |
| [references/contents.md](references/contents.md) | 内容端点提取、新鲜度、状态、顶层内容字段 |
| [references/snapshot.md](references/snapshot.md) | Exa Snapshot：`snapshotAsOf` 在 `/contents` 和 `/search` 上的历史页面版本，限制，Snapshot 与新鲜度的区别 |
| [references/answer.md](references/answer.md) | 带引用的结构化输出的基础答案生成 |
| [references/agent.md](references/agent.md) | Agent API：异步多步骤研究、丰富、结构化输出、轮询和事件 |
| [references/openai-compat.md](references/openai-compat.md) | OpenAI 兼容端点、模型路由、`extra_body` 使用 |
| [references/monitors.md](references/monitors.md) | 独立 Monitors API：定期搜索 |
| [references/migrate-websets-to-agent.md](references/migrate-websets-to-agent.md) | 从 Websets 迁移到 Agent API：调用点分类、请求映射、交付重写、验证 |
| [references/sdks.md](references/sdks.md) | Python 和 TypeScript SDK 名称、方法和形状差异 |
| [references/http-requests.md](references/http-requests.md) | 跨主要 Exa 界面的最小原始 HTTP 示例 |
| [references/models-and-modes.md](references/models-and-modes.md) | 搜索类型选择、答案/研究模型路由、延迟权衡 |
| [references/prompting-and-patterns.md](references/prompting-and-patterns.md) | 持久查询、提示、新鲜度和输出架构模式 |
| [references/common-mistakes.md](references/common-mistakes.md) | 过度指定和参数形状修正 |

## 原始文档

- 文档主页：`https://exa.ai/docs`
- 文档索引：`https://exa.ai/docs/llms.txt`
- 搜索参考：`https://exa.ai/docs/reference/search`
- Agent API 指南：`https://exa.ai/docs/reference/agent-api-guide`
- Exa Connect 概述：`https://exa.ai/docs/reference/agent-api/connect/overview`
- Exa Snapshot：`https://exa.ai/docs/search/snapshot`
- Python SDK 规范：`https://exa.ai/docs/sdks/python-sdk-specification`
- TypeScript SDK 规范：`https://exa.ai/docs/sdks/typescript-sdk-specification`
