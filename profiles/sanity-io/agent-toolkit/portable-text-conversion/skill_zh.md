# 可移植文本转换

将外部内容（HTML、Markdown）转换为适用于 Sanity 的可移植文本。主要有三种方法：

1. **`markdownToPortableText`** — 使用 `@portabletext/markdown` 直接转换 Markdown（推荐用于 Markdown）
2. **`htmlToBlocks`** — 使用 `@portabletext/block-tools` 将 HTML 解析为 PT 块（用于 HTML 迁移）
3. **手动构建** — 直接从任何来源（API、数据库等）构建 PT 块

## 可移植文本规范

在转换前了解目标格式。PT 是一个块数组：

```json
[
  {
    "_type": "block",
    "_key": "abc123",
    "style": "normal",
    "children": [
      {"_type": "span", "_key": "def456", "text": "Hello ", "marks": []},
      {"_type": "span", "_key": "ghi789", "text": "world", "marks": ["strong"]}
    ],
    "markDefs": []
  },
  {
    "_type": "block",
    "_key": "jkl012",
    "style": "h2",
    "children": [
      {"_type": "span", "_key": "mno345", "text": "A heading", "marks": []}
    ],
    "markDefs": []
  },
  {
    "_type": "image",
    "_key": "pqr678",
    "asset": {"_type": "reference", "_ref": "image-abc-200x200-png"}
  }
]
```

**关键规则：**
- 每个块和跨度都需要 `_key`（在数组内唯一）
- `_type: "block"` 用于文本块；自定义类型使用自己的 `_type`
- `markDefs` 存储注释数据；跨度上的 `marks` 引用 `markDefs[*]._key` 或为装饰器字符串
- 列表使用 `listItem` ("bullet" | "number") 和 `level` (1, 2, 3...) 在常规块上

## 转换规则

阅读与您的源格式匹配的规则文件：

- **Markdown → 可移植文本**：`rules/markdown-to-pt.md` — `@portabletext/markdown` 使用 `markdownToPortableText`（推荐）
- **HTML → 可移植文本**：`rules/html-to-pt.md` — `@portabletext/block-tools` 使用 `htmlToBlocks`
- **手动 PT 构建**：`rules/manual-construction.md` — 从任何来源编程构建块

> **注意：** `@sanity/block-tools` 是遗留的包名。新项目始终使用 `@portabletext/block-tools`。API 是相同的。
