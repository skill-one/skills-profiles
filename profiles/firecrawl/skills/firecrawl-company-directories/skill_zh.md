# Firecrawl 公司目录

使用此工具将初创公司或公司目录转换为结构化列表。

## 入职面试

从上下文中推断目录、筛选条件、结果数量和输出格式。如果来源清晰，请立即进行。

如果遇到阻碍，最多只问 1-3 个简洁的问题，例如目录的 URL 或名称、所需的筛选条件或目标结果数量。

## Firecrawl 收集计划

当目录需要筛选条件、分页、无限滚动或个人资料点击时，使用 Firecrawl 浏览器。当列表是公开且静态时，使用 scrape/map。

建议的来源包括 YC 公司、Crunchbase、Product Hunt、G2 类别或任何自定义目录 URL。

## 提取字段

捕获可见字段：

- 名称
- 描述
- 行业/类别
- 当可见时，阶段/成立时间/地点/团队规模/融资
- 标签
- 目录个人资料 URL
- 公司网站 URL

不可用字段留空。不要推断。

## 最终交付物

```markdown
# 公司目录导出：[来源]

## 摘要
[筛选条件、提取数量、限制]

## 公司
[表格或链接到 JSON/CSV]

## 来源
[使用的目录页面和个人资料]

## 重新运行输入
workflow: firecrawl-company-directories
directory: [来源]
filters: [标准]
max_results: [数量]
output: [json/csv/markdown]
```

## JSON 结构

使用 `source`、`filters`、`extractedAt`、`totalResults` 和 `companies[]`，其中 `name`、`url`、`description`、`industry`、`stage`、`founded`、`location`、`teamSize`、`funding`、`tags`、`profileUrl` 和 `websiteUrl`。

## 质量标准

- 去重公司。
- 跟踪分页进度。
- 记录速率限制、登录障碍或验证码阻止。
