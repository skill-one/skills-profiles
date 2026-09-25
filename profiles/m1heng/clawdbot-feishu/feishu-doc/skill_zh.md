# 飞书文档工具

单一工具 `feishu_doc`，支持所有文档操作，包括评论管理，并提供操作参数。

## 令牌提取

从 URL `https://xxx.feishu.cn/docx/ABC123def` → `doc_token` = `ABC123def`
从 URL `https://xxx.feishu.cn/docs/doccn123c` → `doc_token` = `doccn123c`

## 操作

### 读取文档

```json
{ "action": "read", "doc_token": "ABC123def" }
```

返回：标题、纯文本内容、区块统计信息。检查 `hint` 字段 - 如果存在，表示存在结构化内容（表格、图片），需要使用 `list_blocks` 获取。

### 写入文档（全部替换）

```json
{ "action": "write", "doc_token": "ABC123def", "content": "# 标题\n\nMarkdown 内容..." }
```

用 Markdown 内容替换整个文档。支持：标题、列表、代码块、引用、链接、图片 (`![](url)` 自动上传)、粗体/斜体/删除线。

**限制：** Markdown 表格不支持。

### 创建 + 写入（原子操作，推荐）

```json
{
  "action": "create_and_write",
  "title": "新文档",
  "content": "# 标题\n\nMarkdown 内容..."
}
```

带文件夹：
```json
{
  "action": "create_and_write",
  "title": "新文档",
  "content": "# 标题\n\nMarkdown 内容...",
  "folder_token": "fldcnXXX"
}
```

一次性创建文档并写入内容。优先使用此操作，而不是分开的 `create` + `write`。

### 追加内容

```json
{ "action": "append", "doc_token": "ABC123def", "content": "附加内容" }
```

将 Markdown 追加到文档末尾。

### 创建文档

```json
{ "action": "create", "title": "新文档" }
```

带文件夹：
```json
{ "action": "create", "title": "新文档", "folder_token": "fldcnXXX" }
```

创建一个空文档（仅标题）。

### 列出区块

```json
{ "action": "list_blocks", "doc_token": "ABC123def" }
```

返回完整的区块数据，包括表格、图片。用于读取结构化内容。

### 获取单个区块

```json
{ "action": "get_block", "doc_token": "ABC123def", "block_id": "doxcnXXX" }
```

### 更新区块文本

```json
{ "action": "update_block", "doc_token": "ABC123def", "block_id": "doxcnXXX", "content": "新文本" }
```

### 删除区块

```json
{ "action": "delete_block", "doc_token": "ABC123def", "block_id": "doxcnXXX" }
```

### 列出评论

```json
{ "action": "list_comments", "doc_token": "ABC123def", "page_size": 50 }
```

返回文档的所有评论。使用 `page_token` 进行分页。评论包含 `is_whole` 字段，用于区分文档级评论（true）和区块级评论（false）。

### 获取单个评论

```json
{ "action": "get_comment", "doc_token": "ABC123def", "comment_id": "comment_xxx" }
```

### 创建评论

```json
{ "action": "create_comment", "doc_token": "ABC123def", "content": "评论内容" }
```

### 列出评论回复

```json
{ "action": "list_comment_replies", "doc_token": "ABC123def", "comment_id": "comment_xxx", "page_size": 50 }
```

`page_size` 应为正整数。如果省略，工具默认为 `50`。

### 评论写入范围

当前工具提供文档化的评论写入操作 `create_comment`（全局评论创建）。
对于回复，使用 `list_comment_replies` 进行检索；回复创建端点未在当前 SDK 表面暴露。

## 读取工作流

1. 以 `action: "read"` 开始 - 获取纯文本 + 统计信息
2. 检查响应中的 `block_types`，查看是否有 Table、Image、Code 等
3. 如果存在结构化内容，使用 `action: "list_blocks"` 获取完整数据

## 配置

```yaml
channels:
  feishu:
    tools:
      doc: true  # 默认：true
```

**注意：** `feishu_wiki` 依赖于此工具 - wiki 页面内容通过 `feishu_doc` 读取/写入。

## 权限

必需：`docx:document`、`docx:document:readonly`、`docx:document.block:convert`、`drive:drive`

对于评论操作：
- 读取评论：`docx:document.comment:read`
- 写入评论：`docx:document.comment`（可选，用于 `create_comment`）
