# n8n 二进制和数据

每个 n8n 项目都包含两个独立的插槽：`$json` 用于结构化数据，`$binary` 用于文件字节。它们在流程中并排传递。文件内容——实际的 PDF、图像或 zip 文件——存储在 `$binary` 中，永远不会存储在 `$json` 中。如果搞错了这个分割，你将读取一个空字段，在流程中途丢失文件，或者向 AI 代理提供一个它无法使用的工具输入。

这项技能涵盖了二进制存储的位置、如何读取和写入它、如何防止它被无声地剥离、二进制与 AI 代理工具边界之间的硬墙，以及为什么聊天界面需要 URL 而不是原始字节。

---

## 防止 90% 二进制错误的三个规则

1. **文件内容存储在 `$binary` 中，而不是 `$json`。** 在 HTTP 下载、"读取文件" 或电子邮件附件触发器之后，字节存储在 `$binary.<key>` 中。`$json` 最多只包含元数据。读取 `$json.data` 以获取文件内容将一无所得。

2. **二进制不能跨越 AI 代理工具边界——无论是方向。** 工具参数和工具返回值都是 JSON 格式。上传的图像不能作为文件传递到工具中，工具也不能返回原始字节。先预存到存储中，然后通过 JSON 传递键或 URL。参见 `AGENT_TOOL_BINARY.md`。

3. **聊天界面通过 URL 渲染图像，而不是通过 `$binary`。** Slack、Discord、Teams、Telegram、嵌入式 webhook 聊天——它们都不读取二进制插槽。图像必须存储在 URL 可以获取的地方。参见 `CDN_REQUIREMENT.md`。

---

## 两个插槽

每个项目都像这样：

```json
{
  "json": { "customerId": 42, "status": "sent" },
  "binary": {
    "invoice": {
      "data": "<base64 编码的字节>",
      "mimeType": "application/pdf",
      "fileName": "invoice-42.pdf",
      "fileExtension": "pdf"
    }
  }
}
```

`binary` 内部的键（这里是 `invoice`）是**二进制属性名称**。大多数文件处理节点都有一个 `binaryPropertyName` 参数指向它——生产者命名插槽，消费者通过该名称引用它。大多数节点中的默认键是 `data`，所以当没有其他指示时，假设 `$binary.data`。

`$json` 和 `$binary` 是独立的命名空间。像 `{{ $binary.invoice.fileName }}` 这样的表达式读取文件元数据；`{{ $json.customerId }}` 读取数据。它们永远不会混合。

这种分割也解释了一个 webhook 惯例：接收 `multipart/form-data` 的 Webhook 触发器将上传的文件存储在 `$binary` 中，将伴随的表单字段存储在 `$json.body` 中——所以上传的文件根本不在 `$json` 下任何地方。（Webhook 的 `$json.body` 嵌套是 **n8n-expression-syntax** 领域的内容。）

参见 `BINARY_BASICS.md` 以获取完整的插槽解剖结构、MIME 类型和大小的限制。

---

## 生成二进制

你很少手动构建 `$binary` 插槽——节点为你填充它：

| 来源 | 二进制如何出现 |
|---|---|
| 带有 `responseFormat: "file"` 的 HTTP 请求 | 响应正文存储在 `$binary.data`（或你设置的名称） |
| 从磁盘读取/写入文件 | 文件内容读取到 `$binary` |
| 存储（S3、Google Drive、Dropbox 等）下载 | 下载的文件在 `$binary.<key>` |
| 带附件的电子邮件触发器 | 每个附件都到达 `$binary` |
| 提供商 AI 媒体节点（图像/音频生成） | 设置 `options.binaryPropertyOutput` 以使字节到达下一个节点 |

对于 HTTP 下载，唯一重要的字段是 `responseFormat`。使用 `get_node` 在 `nodes-base.httpRequest` 上确认它——将其保留为默认的 JSON/字符串格式是下载的文件最终以混乱文本形式出现在 `$json` 中而不是干净的字节出现在 `$binary` 中的经典原因。

---

## 在 Code 节点中读取和写入二进制

大多数工作流不需要打开字节——它们只是将二进制传递给消费者（电子邮件附件、文件上传、Slack 文件）。当你确实需要原始字节时，请在 Code 节点中执行。

**读取**使用 `getBinaryDataBuffer`——不要尝试手动 base64 解码 `$binary.<key>.data`：

```javascript
// Code 节点，"为每个项目运行一次"
const buffer = await this.helpers.getBinaryDataBuffer(0, 'data'); // (itemIndex, propertyName)
const text = buffer.toString('utf-8');
const length = buffer.length;

return [{
  json: { ...$json, length },
  binary: $input.item.binary,   // 传递二进制，否则它将丢失
}];
```

**写入**通过自己构建插槽——base64 编码字节加上 MIME 类型和文件名：

```javascript
const text = 'Hello, world!';
return [{
  json: { ok: true },
  binary: {
    report: {
      data: Buffer.from(text).toString('base64'),
      mimeType: 'text/plain',
      fileName: 'report.txt',
      fileExtension: 'txt',
    },
  },
}];
```

Code 节点的沙盒、帮助程序和执行模式是 **n8n-code-javascript**（和 **n8n-code-python**）的领域——使用它们以获取语言级别的细节。这里的二进制特定要点：返回 `[{ json: {...} }]` 而不重新附加 `binary` 的 Code 节点**会无声地丢弃文件**。参见 `BINARY_BASICS.md`。

---

## 在转换过程中保持二进制

仅 JSON 节点——编辑字段（设置）、Code、IF 和其他——可以从它们的输出中删除 `$binary` 插槽。工作流验证干净并运行无误；当电子邮件节点尝试附加它时，下游的文件就不存在了。

两种方法保持它：

- **转换节点的传递选项。** 编辑字段有 `includeOtherFields`；Code 节点可以显式返回 `binary: $input.item.binary`。当可用时，这是最简单的修复方法。
- **分支并合并。** 将源路由到转换和绕过分支，然后以 `combineByPosition` 模式重新组合。JSON 来自转换侧，二进制在绕过侧存活。

```
[带二进制的源] ─┬─→ [编辑字段：更改 JSON] ─┐
                      │      (二进制在这里被剥离)     ├─→ [合并：combineByPosition] ─→ [电子邮件：附加]
                      └──────────────────────────────────┘
                          (绕过——二进制未经更改通过)
```

`combineByPosition` 将每个输入的项目 N 配对，所以字段计数必须对齐。连接布线和许多条带点链（提前上传、子工作流）的替代方案在 `MERGE_FOR_CONTEXT.md` 中。

---

## 代理工具的二进制边界

这是最锋利的边缘。AI 代理通过 JSON 与其工具（自定义代码工具、调用 n8n 工作流工具、HTTP 请求工具、MCP 工具）交谈。二进制不能以任何方向通过这个管道。修复方法是相同的形状：**将字节预存到存储中，通过 JSON 传递键/URL，在另一侧获取。**

**输入——用户上传了代理工具必须操作的文件：**

1. 聊天触发器给你一个 `files[]` 数组。将其拆分并上传每个文件到私有存储在哈希键下。
2. 在代理运行之前重新合并该分支（这是一个同步屏障，而不是装饰），并在代理上设置 `executeOnce: true` 以防止 N 个文件触发 N 次代理运行。
3. 将键注入代理的系统提示中，列出原始名称（人类上下文）和存储键（工具需要什么），并明确“使用确切的这个键”。
4. 工具接收键作为字符串参数并从存储中下载文件。

**输出——工具生成了代理必须返回的文件：**

1. 工具子工作流生成二进制，上传到存储，并返回类似 `{ "ok": true, "key": "...", "url": "https://...", "mimeType": "image/png" }` 的 JSON。
2. 代理将其 URL 嵌入回复中（或将键传递给另一个工具）。

`passthroughBinaryImages: true` 在代理上只改变 LLM 看到的**视觉内容**——它**不**允许工具接收文件，并且仅限图像（没有 PDF、音频或视频）。你仍然需要上传并传递键的模式来获取任何工具。完整模式、哈希策略、存储选择和长时间运行的工具变体在 `AGENT_TOOL_BINARY.md` 中。

> 自己构建工具？参见 **n8n-code-tool** 以获取自定义代码工具合同和 **n8n-workflow-patterns** 以获取 AI-Agent-with-tools 形状。

---

## 聊天界面的 CDN 要求

当工作流生成图像并且用户希望将其显示在聊天消息中时：

- **项目中的二进制不够。** 聊天客户端通过 URL（或通过平台的自己的文件上传 API 推送字节）渲染消息，它永远不会读取 `$binary`。
- **字节必须存储在 URL 可以通过 HTTPS 获取的地方。** 首先上传到对象存储或驱动器，然后嵌入返回的 URL。
- **n8n 没有内置的 CDN。** 用户提供存储。

询问他们已经使用的存储，而不是默认为 S3——对象存储（S3、R2、GCS、Azure Blob、Backblaze B2、Supabase Storage）和驱动器式服务（Dropbox、Google Drive、OneDrive、Box）都有效，并且都改变 URL 形状。如果他们没有任何东西，Cloudflare R2 是最低摩擦的起点。对于敏感内容，使用带过期时间的签名 URL 而不是永久公开的 URL。参见 `CDN_REQUIREMENT.md`。

---

## 不包含的内容

- **`$fromAI()` 不能携带二进制。** 它用字符串、数字、布尔值和对象填充工具参数——永远不会是文件字节。传递存储键而不是它。
- **工具参数和返回值是 JSON 仅。** 没有工具上的“二进制参数”，进或出。
- **n8n 不提供 CDN 或公共文件主机。** 通过 URL 传递文件始终是用户存储的事情，而不是 n8n。
- **`getBinaryDataBuffer` 是 Code 节点的帮助程序。** 它在 Custom Code Tool 沙盒中不可用（参见 **n8n-code-tool**）。

---

## 数据表的位置

对于持久化表格存储——参考计数预存文件、跟踪哪些键是活动的、去重——那是 `n8n_manage_datatable` 表面，由 **n8n-mcp-tools-expert** 拥有。这项技能不涵盖数据表。

---

## 反模式

| 反模式 | 出现什么问题 | 修复 |
|---|---|---|
| 从 `$json` 读取文件内容 | 字节存储在 `$binary` 中；`$json` 是空的或只有元数据 | 读取 `$binary.<key>`，或在 Code 节点中使用 `getBinaryDataBuffer` |
| 没有 `responseFormat: "file"` 的 HTTP 下载 | 字节作为混乱的文本到达 `$json`，而不是干净的二进制 | 在 HTTP 请求节点上设置 `responseFormat: "file"` |
| Code 节点返回 `[{json:{...}}]`，没有 `binary` | 文件在下游无声地丢失 | 在返回中重新附加 `binary: $input.item.binary` |
| JSON 转换（编辑字段/IF）吃掉二进制 | 电子邮件/上传节点找不到要附加的内容 | 传递选项，或分支 + 按 `combineByPosition` 合并 |
| 通过 `$fromAI` 将上传的文件传递给工具 | `$fromAI` 不能携带二进制；工具什么也得不到 | 预存到存储中，在系统提示中注入键，工具按键获取 |
| 假设 `passthroughBinaryImages` 让工具看到文件 | 它只影响 LLM 看到的，并且仅限图像 | 仍然需要上传并传递键的模式来获取工具 |
| 工具向代理返回原始二进制 | 工具输出是 JSON；字节不会存活（并且会膨胀上下文） | 上传，以 JSON 返回 `{ key, url }` |
| 向聊天界面发布 `$binary` 并期望图像 | 聊天客户端通过 URL 渲染，而不是原始字节 | 上传到存储/CDN，嵌入 URL 或使用平台文件 API |
| 在 Code 节点中硬编码 base64 | 工作流 JSON 巨大，慢，泄漏 | 通过 `$binary` 引用，或上传并通过 URL 引用 |

---

## 参考文件

| 文件 | 何时阅读 |
|---|---|
| `BINARY_BASICS.md` | 第一次处理二进制，或读取/写入 `$binary` 插槽、MIME 类型、大小限制 |
| `AGENT_TOOL_BINARY.md` | 代理工具需要上传的文件，或生成一个——任何方向的边界 |
| `MERGE_FOR_CONTEXT.md` | JSON 转换后二进制消失，并且需要重新附加它 |
| `CDN_REQUIREMENT.md` | 在聊天界面中显示图像或任何需要 URL 引用图像的地方 |

---

## 与其他技能的集成

**n8n-code-javascript / n8n-code-python**：Code 节点是读取/写入原始字节的地方（`getBinaryDataBuffer`，`Buffer.from(...).toString('base64')`）。这些技能拥有沙盒、帮助程序和执行模式的细节——这项技能拥有二进制必须在返回时重新附加的规则。

**n8n-code-tool**：自定义代码工具沙盒更窄——没有 `$binary`，没有 `getBinaryDataBuffer`，没有 `$fromAI`。当工具需要文件时，这项技能的存储键模式是它如何获取文件的方式。

**n8n-workflow-patterns**：代理工具的二进制边界位于 AI-Agent-with-tools 模式内；CDN 流是一个生成 → 上传 → 回复链。

**n8n-node-configuration**：`responseFormat`、`binaryPropertyName`、`includeOtherFields`、`binaryPropertyOutput` 都是条件字段——使用 `get_node` 确认用户版本上的确切名称。

**n8n-expression-syntax**：处理 `$binary.<key>.fileName` 与 `$json.body`（特别是 webhook 上传）是表达式领域的内容。

**n8n-validation-expert**：丢失的二进制插槽是沉默的失败——`validate_workflow` 不会标记它。通过检查执行来确认存在。

**n8n-mcp-tools-expert**：拥有 `n8n_manage_datatable`（数据表）和 `n8n_executions`——使用后者来确认某个节点后 `binary` 插槽是否存活。

**n8n-error-handling**：存储上传和下载失败；输入/输出预存步骤需要错误分支，以便一个丢失的键不会无声地 404。

**using-n8n-mcp-skills**：这些技能如何组合的索引。

---

## 验证二进制是否存活

验证不会捕获被剥离的二进制插槽——这是一个沉默的失败。确认它是否正确运行：

1. `n8n_test_workflow`（或触发实际运行）以生成执行。
2. `n8n_executions` 以获取该执行，并检查每个节点的输出以查看 `binary` 插槽——它显示存在和元数据，即使 base64 太大而无法渲染。
3. `binary` 最后出现的节点是剥离之前的节点。那就是传递或合并的地方。

---

## 快速参考清单

- [ ] 文件内容从 `$binary.<key>` 读取——从不 `$json`
- [ ] HTTP 下载使用 `responseFormat: "file"`
- [ ] Code 节点在返回时重新附加 `binary`，因为文件必须继续
- [ ] JSON 转换要么传递二进制，要么按 `combineByPosition` 合并
- [ ] 试图将二进制传递到/从代理工具——通过 JSON 传递键/URL 而不是字节
- [ ] `passthroughBinaryImages` 仅用于 LLM 视觉，而不是作为工具通道
- [ ] 聊天界面图像上传到存储；URL 被嵌入，而不是字节
- [ ] 存储后端由用户选择（不是默认为 S3）；对敏感内容使用带过期时间的签名 URL
- [ ] 通过检查执行确认二进制存在，而不是通过验证

---

**记住**：两个插槽，并排。数据在 `$json` 中骑行，文件在 `$binary` 中骑行——当文件必须跨越代理工具或到达聊天界面时，它作为 URL 而不是字节旅行。
