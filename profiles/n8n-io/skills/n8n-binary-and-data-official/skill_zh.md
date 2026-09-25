# n8n 二进制和数据

n8n 处理两种类型的数据：JSON（在 `$json` 中）和二进制（在 `$binary` 中），它们并行流动。二进制在代理工具、存储和显示上下文（聊天界面、消息渲染）周围有明显的边界。

有关表格存储（数据表），请参阅 **`n8n-data-tables-official`** 技能。

## 不可协商的规则

1. **二进制存储在 `$binary` 中，而不是 `$json` 中。** 不要从 `$json` 中读取文件内容。
2. **二进制不能在任何方向上跨越代理工具边界。** 工具参数仅支持 JSON（通过 `fromAi()`），工具结果也仅支持 JSON。在存储中预先处理二进制，并通过 JSON 传递密钥/URL。代理的 `passthroughBinaryImages: true` 允许 LLM *查看* 上传的图像用于视觉，但它**不**使工具能够接收它们。参见 `references/AGENT_TOOL_BINARY.md`。

## 强制性默认值

- **合并节点保持二进制上下文。** 当侧计算移除二进制时，合并它而不是重新获取。参见 `references/MERGE_FOR_CONTEXT.md`。

## 二进制基础

在 n8n 中，每个项目有两个插槽：

```ts
{
    json: { ... },           // 你的数据
    binary: {                // 你的文件
        data: {              // 'data' 是典型键；可以是任何名称
            data: '<base64>',
            mimeType: 'application/pdf',
            fileName: 'invoice.pdf',
            fileExtension: 'pdf',
        },
    },
}
```

`$binary.<key>` 读取命名的属性。大多数文件处理节点都有一个 `binaryPropertyName` 参数，它是 `$binary` 中的键。

### 设置二进制

产生文件的节点（带有二进制响应的 HTTP 请求、读取文件等）会自动填充 `$binary`。要在 Code 节点中产生二进制：

```ts
return [{
    json: { ... },
    binary: {
        data: {
            data: Buffer.from(content).toString('base64'),
            mimeType: 'text/plain',
            fileName: 'output.txt',
        },
    },
}]
```

### 读取二进制

```ts
// 在 Code 节点中
const buffer = await this.helpers.getBinaryDataBuffer(0, 'data')
const text = buffer.toString('utf-8')
```

大多数工作流不需要直接读取二进制。将其传递给消费者节点（电子邮件附件、文件上传等）。

有关更多信息，请参阅 `references/BINARY_BASICS.md`。

## 代理工具的技巧

代理工具（连接到 LangChain Agent 的子工作流，或作为 MCP 工具暴露的工作流）有一个限制：参数和结果是 JSON，而不是二进制。这影响双向。

**入站（用户上传 → 工具消费）：** 聊天触发器提供 `files[]`。代理可以有 `passthroughBinaryImages: true` 用于视觉，但 `fromAi()` 不能将二进制传递给工具。因此：

1. 预先处理上传的文件：对密钥进行哈希，上传到私有存储。
2. 将密钥注入代理的系统提示中："传递的文件：[{originalFileName, fileName}]。调用工具时使用确切的 `fileName` 字段。"
3. 工具的 `fromAi('imageName', '...', 'string')` 接收密钥。子工作流从存储中下载。

**出站（工具生成 → 代理返回）：** 工具生成一个文件。它不能直接返回原始二进制。

1. 内部生成二进制。
2. 上传到存储，获取 URL/密钥。
3. 返回 JSON：`{ ok: true, file_id: '...', url: '...' }`。
4. 代理将其 URL 嵌入其响应中，或另一个工具通过密钥获取。

有关完整模式，包括用于长时间运行工具的异步通过 webhook 变体，请参阅 `references/AGENT_TOOL_BINARY.md`。

## 合并以保持二进制上下文

JSON 仅操作（编辑字段、Code、IF）通常会从项目中移除二进制。要保持它：

```
[带二进制的源] ─┬─→ [编辑字段：转换 JSON] ─┐
                      │                                    ├─→ [合并：按位置] ─→ [带附件的电子邮件]
                      └─────────────────────────────────────┘
```

合并组合了流，二进制得以保留。参见 `references/MERGE_FOR_CONTEXT.md`。

## 聊天界面需要 CDN

当工作流生成图像，并且用户希望将其嵌入聊天消息（Slack、Discord、Teams、Telegram、嵌入 webhook 聊天等）时：

- **项目中的二进制不够。** 聊天界面不读取 `$binary`；它们渲染引用图像 URL（或通过平台特定的文件上传 API）的消息。
- **图像必须存储在可以获取 URL 的位置。** 首先上传到 CDN 或对象存储。
- **用户配置此存储。** 不是 n8n 内置的。

常见选项包括对象存储（S3、R2、GCS、Azure Blob、Vercel Blob、Supabase Storage）和驱动式服务（Dropbox、Google Drive、OneDrive、Box）。询问用户他们使用什么，而不是默认为 S3。

参见 `references/CDN_REQUIREMENT.md`。

## 数据表

有关数据表，请参阅 **`n8n-data-tables-official`** 技能。具有其自己的陷阱（默认列、没有外键、没有 JSON 列类型、手动映射 UI 特性）的独特界面。

## 参考文件

| 文件 | 读取时机 |
|---|---|
| `references/BINARY_BASICS.md` | 首次处理二进制，或读取/写入 `$binary` 插槽时 |
| `references/AGENT_TOOL_BINARY.md` | 代理工具需要用户上传的文件，或生成文件（任何方向的边界）时 |
| `references/MERGE_FOR_CONTEXT.md` | 二进制在 JSON 转换后消失并需要重新附加时 |
| `references/CDN_REQUIREMENT.md` | 在聊天界面或其他需要 URL 引用图像的位置显示图像时 |

## 反模式

| 反模式 | 问题所在 | 解决方法 |
|---|---|---|
| 尝试从 `$json` 读取文件内容 | 二进制不在 `$json` 中 | 使用 `$binary` |
| 构建返回二进制的代理工具 | 工具输出是 JSON 仅，因此二进制不会保留 | 上传到存储，以 JSON 返回密钥/URL（参见 `AGENT_TOOL_BINARY.md`） |
| 尝试通过 `fromAi` 将上传的聊天文件传递给工具 | `fromAi` 不携带二进制，因此工具什么也得不到 | 将上传预置到存储，在系统提示中注入密钥，并让工具按密钥下载 |
| 设置 `passthroughBinaryImages: true` 并假设工具现在可以看到文件 | 该标志仅影响 LLM 看到的内容，而不是工具接收的内容 | 仍然需要上传和传递密钥的模式用于工具 |
| JSON 转换后丢失二进制 | 转换的输出项目没有二进制 | 使用合并将 JSON 输出与二进制流组合 |
| 在 n8n 二进制中存储图像并期望聊天界面显示 | 聊天界面需要 URL 可访问的图像（或平台原生文件上传），而不是原始 `$binary` | 上传到 CDN，嵌入 URL 或使用平台的文件 API |
| 在 Code 节点中硬编码二进制 base64 | 工作流 JSON 巨大、缓慢、泄漏 | 通过 `$binary` 正确引用二进制，或上传到存储并通过 URL 引用 |
