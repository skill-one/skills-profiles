# Markdown 文档

## 目录

- [概述](#概述)
- [何时使用](#何时使用)
- [快速入门](#快速入门)
- [参考指南](#参考指南)
- [最佳实践](#最佳实践)

## 概述

掌握 Markdown 语法和最佳实践，使用标准 Markdown 和 GitHub Flavored Markdown (GFM) 创建格式良好、易于阅读的文档。

## 何时使用

- README 文件
- 文档页面
- GitHub/GitLab 维基
- 博客文章
- 技术写作
- 项目文档
- 注释格式化

## 快速入门

- 注释格式化

```markdown
# H1 标题

## H2 标题

### H3 标题

#### H4 标题

##### H5 标题

###### H6 标题

# 替代 H1

## 替代 H2
```

## 参考指南

`references/` 目录中的详细实现：

| 指南 | 内容 |
|---|---|
| [文本格式化](references/text-formatting.md) | 文本格式化 |
| [列表](references/lists.md) | 列表 |
| [链接和图片](references/links-and-images.md) | 链接和图片、代码块、表格 |
| [扩展语法 (GitHub Flavored Markdown)](references/extended-syntax-github-flavored-markdown.md) | 扩展语法 (GitHub Flavored Markdown) |
| [可折叠部分](references/collapsible-sections.md) | 可折叠部分、语法高亮、徽章 |
| [警告和提示](references/alerts-and-callouts.md) | 警告和提示 |
| [Mermaid 图表](references/mermaid-diagrams.md) | Mermaid 图表 |

## 最佳实践

### ✅ 应该

- 使用描述性链接文本
- 为长文档包含目录
- 为图片添加替代文本
- 使用带语言声明的代码块
- 保持行长度在 80-100 个字符以内
- 使用相对链接进行内部文档
- 添加徽章以显示构建状态、覆盖率等
- 包含示例和截图
- 使用语义行断
- 定期测试所有链接

### ❌ 不应该

- 使用 "点击这里" 作为链接文本
- 忘记图片的替代文本
- 不必要地混合 HTML 和 Markdown
- 使用绝对路径引用本地文件
- 创建没有断行的文本墙
- 在代码块中省略语言声明
- 使用图片作为文本内容（无障碍性）
