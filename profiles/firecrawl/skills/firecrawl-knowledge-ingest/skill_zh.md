# Firecrawl 知识摄入

当文档门户需要浏览器导航、认证、分页或 JS 渲染时使用。

## 欢迎面试

从上下文中推断门户 URL、输出格式、认证需求和页面限制。如果门户清晰，立即进行。

如果遇到阻塞，最多只问 1-3 个简洁的问题，例如门户 URL、是否需要认证或期望的输出格式。

## Firecrawl 集合计划

使用 Firecrawl 浏览器：

- 打开门户并检查导航
- 识别部分、类别、侧边栏链接和文章 URL
- 跟随侧边栏导航、下一页链接、分页、加载更多控件或搜索
- 以 Markdown 格式抓取文章内容
- 提取元数据，如标题、部分、最后更新日期、作者和标签

尝试使用 Firecrawl 地图作为公共 URL 的补充，但对于认证保护或 JS 依赖内容，使用浏览器导航。

## 最终交付物

```markdown
# 知识摄入：[门户]

## 摘要
[提取的页面数、覆盖的部分、限制]

## 输出
[JSON/Markdown/合并文件路径或内容]

## 部分
[部分名称和文章数量]

## 失败或受限页面
[任何访问/加载问题]

## 来源
[提取的 URL]

## 重新运行输入
workflow: firecrawl-knowledge-ingest
url: [门户 URL]
format: [json/markdown/merged]
max_pages: [数字]
```

## JSON 结构

使用 `source`、`url`、`extractedAt`、`totalArticles` 和 `sections[]`，其中包含文章的 `title`、`url`、`section`、`content` 和 `metadata`。

## 质量标准

- 保留代码示例、表格和格式。
- 移除导航 Chrome、页眉和页脚。
- 跟踪提取进度和页面失败。
- 尊重认证边界。
