# LlamaParse 技能

使用 LlamaParse 解析非结构化文档（如 PDF、DOCX、PPTX、XLSX），并提取其内容（文本、Markdown、图像等）。

## 初始设置

当此技能被调用时，回复：

```
我已准备好使用 LlamaParse 解析文件。在开始之前，请确认：

- `LLAMA_CLOUD_API_KEY` 已作为当前环境中的环境变量设置
- `@llamaindex/llama-cloud@latest` 已安装并在当前 Node 环境中可用

如果这两个条件都满足，请提供：

1. 一个或多个要解析的文件
2. 具体的解析选项，例如级别、API 版本、自定义提示、处理选项...
3. 任何关于文件解析内容的请求。

我将生成一个 TypeScript 脚本来运行解析任务，一旦您批准其执行，我将根据您的请求将结果报告给您。
```

然后等待用户的输入。

---

## 第 0 步 — 安装 `llama-cloud`（可选）

如果用户没有安装 `@llamaindex/llama-cloud` 包，可以通过运行以下命令将其添加到当前环境中：

```bash
npm install @llamaindex/llama-cloud@latest
```

## 第 1 步 — 生成 TypeScript 脚本

一旦用户确认环境变量已设置并提供了解析任务的必要详细信息，就生成一个 **TypeScript 脚本**。

作为 TypeScript 脚本的权威来源，您可以：

- 参考 [example.ts](scripts/example.ts) 脚本，该脚本涵盖了 LlamaParse 的绝大多数必要配置
- 参考 LlamaParse 完整文档，获取 `https://developers.llamaindex.ai/python/cloud/llamaparse/api-v2-guide/` 页面。

### 脚本编写最佳实践

在生成脚本时，请遵循以下指南：

#### 1. 始终使用顶层 `LlamaCloud` 客户端

对所有解析操作使用 `LlamaCloud`（API 客户端）：

```typescript
import LlamaCloud from "@llamaindex/llama-cloud";

// 定义一个客户端
const client = new LlamaCloud({
  apiKey: process.env["LLAMA_CLOUD_API_KEY"], // 这是默认值，可以省略
});
```

#### 2. 两步上传 → 解析模式

始终先上传以获取文件 ID，然后使用文件 ID 进行解析。切勿将原始文件字节直接传递给 `parse()`。

```typescript
import { readFile, writeFile } from "fs/promises";
import { basename } from "path";

// 1. 将文件路径转换为 File 对象
const buffer = await readFile(filePath);
const fileName = basename(filePath);
const file = new File([buffer], fileName);
// 2. 将文件上传到云端
const fileObj = await client.files.create({
  file: file,
  purpose: "parse",
});
// 3. 获取文件 ID
const fileId = fileObj.id;
// 4. 使用文件 ID 解析文件
const result = await client.parsing.parse({
  tier: "agentic",
  version: "latest",
  file_id: fileId,
  ...
});
```

如果用户已经有一个文件 ID（例如，来自先前的上传），则跳过上传步骤并直接使用它。

#### 3. 选择合适的级别

| 级别 | 使用场景 |
|------|-------------|
| `fast` | 速度优先；简单文档 |
| `cost_effective` | 节约成本；简单的文本提取 |
| `agentic` | 复杂布局、表格、混合内容（默认推荐） |
| `agentic_plus` | 高级分析，最高精度 |

默认使用 `agentic`，除非用户指定其他选项或文档简单。

#### 4. 始终包含 `expand` 参数

`expand` 参数控制返回的内容。省略它将返回最少的数据。始终明确指定您需要的内容：

| 值 | 返回 |
|-------|---------|
| `text_full` | 通过 `result.text_full` 返回纯文本 |
| `markdown_full` | 通过 `result.markdown_full` 返回 Markdown |
| `items` | 通过 `result.items.pages` 返回页面级 JSON |
| `text_content_metadata` | 每页文本元数据 |
| `markdown_content_metadata` | 每页 Markdown 元数据 |
| `items_content_metadata` | 每页项目元数据 |
| `images_content_metadata` | 带有预签名 URL 的图像列表 |
| `output_pdf_content_metadata` | 输出 PDF 元数据 |
| `xlsx_content_metadata` | Excel 特定元数据 |

仅在您需要预签名 URL 或每页详细信息时请求 `*_content_metadata` 变体——它们会增加有效载荷大小。

#### 5. 防御性处理无结果

`result.text_full`、`result.markdown_full` 和 `result.items` 在失败时可能是 `undefined`。始终防范这种情况：

```typescript
const text = result.text_full ?? "";
const markdown = result.markdown_full ?? "";
```

#### 6. 使用结构化选项进行高级配置

使用正确的嵌套键分组选项：

```typescript
const result = await client.parsing.parse({
  tier: "agentic",
  version: "latest",
  file_id: fileId,
  input_options: {
    presentation: {
      skip_embedded_data: false,
    },
  },
  output_options: {
    images_to_save: ["screenshot"],
    markdown: {
      tables: { output_tables_as_markdown: true },
      annotate_links: true,
    },
  },
  processing_options: {
    specialized_chart_parsing: "agentic",
    ocr_parameters: { languages: ["de", "en"] },
  },
  agentic_options: {
    custom_prompt:
      "从提供的文件中提取文本并将其从德语翻译成英语。",
  },
  expand: [
    "markdown_full",
    "images_content_metadata",
    "markdown_content_metadata",
  ],
});
```

当用户希望指导提取（翻译、摘要、结构化提取等）时，使用 `agentic_options.custom_prompt`。

#### 7. 下载图像需要 `httpx` 和认证

当 `images_content_metadata` 在 `expand` 中时，通过预签名 URL 并使用 Bearer 认证下载图像：

```typescript
if (result.images_content_metadata) {
  for (const image of result.images_content_metadata.images) {
    if (image.presigned_url) {
      const response = await fetch(image.presigned_url, {
        headers: {
          Authorization: `Bearer ${process.env["LLAMA_CLOUD_API_KEY"]}`,
        },
      });
      if (response.ok) {
        const content = await response.bytes();
        await writeFile(image.filename, content);
      }
    }
  }
}
```

#### 8. 使用 Node shebang

每个生成的脚本都应包含 Node shebang：

```typescript
#!/usr/bin/env node
```

---

## 第 2 步 — 执行 TypeScript 脚本

一旦 TypeScript 脚本生成，您应该：

1. 向用户展示脚本并请求运行权限（取决于当前的权限设置）
2. 获得运行权限后，执行脚本
3. 根据用户的请求探索结果

> 为了运行 TypeScript 脚本，强烈建议使用：`npx tsx script.ts`。
