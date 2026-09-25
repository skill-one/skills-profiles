# PDF 阅读器 — 交互式文档工作流

您拥有一个本地 PDF 服务器，它可以在实时查看器中渲染文档，并允许您进行注释、填写表单以及放置签名，并提供实时视觉反馈。

## 何时使用此技能

**当用户需要交互时使用 PDF 阅读器：**
- "给我显示这份合同" / "打开这份文件"
- "突出显示关键条款并让我审阅"
- "帮助我填写这份表单"
- "在第 3 页上签名" / "在每一页上添加我的签名"
- "在此处加盖机密印章" / "标记为已批准"
- "向我讲解这份文档并注释重要部分"

**不要用于纯粹的文本输入：**
- "总结这份 PDF" → 直接使用原生的阅读工具
- "第 5 页上说什么？" → 使用阅读工具
- "从第 3 节中提取表格" → 使用阅读工具

阅读器的价值在于向用户展示文档并协作进行标注——而不是将文本流回给您。

## 工具

### `list_pdfs`
列出可用的本地 PDF 文件和允许的本地目录。无参数。

### `display_pdf`
在交互式查看器中打开 PDF。**每个文档调用一次。**
- `url` — 本地文件路径或 HTTPS URL
- `page` — 初始页面（可选，默认为 1）
- `elicit_form_inputs` — 如果为 `true`，则在显示之前提示用户填写表单字段（用于交互式表单填写）

返回 `viewUUID` — 将其传递给每个 `interact` 调用。再次调用 `display_pdf` 会创建一个**独立的**查看器；使用新 UUID 的交互调用将不会到达用户正在查看的那个查看器。

还返回 `formFields`（名称、类型、页面、边界框），如果 PDF 包含可填写字段——使用这些坐标进行签名放置。

### `interact`
在 `display_pdf` 之后的所有后续操作。传递 `viewUUID` 以及一个或多个命令。**通过 `commands` 数组在一个调用中批量多个命令**——它们按顺序执行。以 `get_screenshot` 结束批量，以视觉方式验证更改。

**标注操作：**
- `add_annotations` — 添加标注（见下文类型）
- `update_annotations` — 修改现有（需要 id + 类型）
- `remove_annotations` — 通过 id 数组删除
- `highlight_text` — 自动查找文本并突出显示它（优于手动矩形进行文本标注）

**导航操作：**
- `navigate`（页面）、`search`（查询）、`find`（查询，静默）、`search_navigate`（匹配索引）、`zoom`（缩放 0.5–3.0）

**提取操作：**
- `get_text` — 从页面范围提取文本（最多 20 页）。用于阅读内容以决定要标注什么，**不用于总结。**
- `get_screenshot` — 将页面捕获为图像（验证您的标注）

**表单操作：**
- `fill_form` — 填写命名字段：`fields: [{name, value}, ...]`

## 标注类型

所有标注都需要 `id`（唯一字符串）、`type`、`page`（1 索引）。坐标是 PDF 点（1/72 英寸），原点**左上角**，Y 轴向下增加。美国信纸是 612×792pt。

| 类型 | 关键属性 | 用于 |
|------|----------|------|
| `highlight` | `rects`, `color?`, `content?` | 标记重要文本 |
| `underline` | `rects`, `color?` | 强调术语 |
| `strikethrough` | `rects`, `color?` | 标记删除内容 |
| `note` | `x`, `y`, `content`, `color?` | 便签式评论 |
| `freetext` | `x`, `y`, `content`, `fontSize?` | 页面上的可见文本 |
| `rectangle` | `x`, `y`, `width`, `height`, `color?`, `fillColor?` | 盒子区域 |
| `circle` | `x`, `y`, `width`, `height`, `color?`, `fillColor?` | 圆形区域 |
| `line` | `x1`, `y1`, `x2`, `y2`, `color?` | 绘制线条/箭头 |
| `stamp` | `x`, `y`, `label`, `color?`, `rotation?` | 已批准、草稿、机密等 |
| `image` | `imageUrl`, `x?`, `y?`, `width?`, `height?` | **签名、签名**、标志 |

**图像标注**接受本地文件路径或 HTTPS URL（无数据：URI）。如果省略，则自动检测尺寸。用户还可以将图像直接拖放到查看器上。

## 交互式工作流

### 协作标注（AI 驱动）
1. `display_pdf` 打开文档
2. `interact` → `get_text` 在相关页面范围上获取文本以理解内容
3. 向用户提议一批标注（描述您将标记的内容）
4. 批准后，`interact` → `add_annotations` + `get_screenshot`
5. 向用户展示，请求编辑，迭代
6. 完成时，提醒他们可以从查看器工具栏下载标注的 PDF

### 表单填写（视觉，非程序化）
与无头表单工具不同，这为用户提供**实时视觉反馈**，并处理具有神秘/未命名字段的表单，其中标签打印在页面上而不是在字段元数据中。

1. `display_pdf` — 检查返回的 `formFields`（名称、类型、页面、边界框）
2. 如果字段名称神秘（`Text1`、`Field_7`），`get_screenshot` 页面并匹配边界框到视觉标签
3. 使用**视觉**标签向用户询问值，或从上下文中推断
4. `interact` → `fill_form`，然后 `get_screenshot` 显示结果
5. 用户确认或直接在查看器中编辑

对于简单的、标签清晰的表单，`display_pdf` 使用 `elicit_form_inputs: true` 提示用户 upfront。

### 签名（视觉，非认证）
1. 询问签名/签名的图像路径
2. `display_pdf`，检查 `formFields` 签名类型字段或询问页面/位置
3. `interact` → `add_annotations` 在目标坐标处使用 `type: "image"`
4. `get_screenshot` 确认位置

**免责声明：** 这放置一个视觉签名图像。它**不是**认证或加密的数字签名。

## 支持的来源

- 本地文件（客户端 MCP 根路径下的路径）
- arXiv（`/abs/` URL 自动转换为 PDF）
- 任何直接的 HTTPS PDF URL（bioRxiv、Zenodo、OSF 等——使用直接的 PDF 链接，而不是着陆页）

## 不在范围内

- **总结 / 文本提取** — 使用原生的阅读工具
- **认证数字签名** — 仅图像盖章
- **PDF 创建** — 仅适用于现有的 PDF 文件
