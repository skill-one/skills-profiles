# 博客分类体系

跨 CMS 平台管理标签、分类和主题簇。

## 命令

| 命令 | 目的 |
|------|------|
| `/blog taxonomy suggest <文件>` | 从内容中提取候选标签和分类 |
| `/blog taxonomy sync <cms>` | 通过认证 API 将分类体系推送到 CMS |
| `/blog taxonomy audit [目录]` | 检查瘦标签、孤立标签和分类体系臃肿问题 |

## 标签建议工作流

### 第 1 步：解析内容结构

读取目标文件并提取：
- 所有 H2 和 H3 标题（主要主题信号）
- 粗体和斜体短语（强调信号）
- 如果存在，提取现有的 frontmatter 标签/分类

### 第 2 步：频率分析

扫描正文文本中的高频短语：
- 单词：至少出现 4 次（排除停用词）
- 双词短语：至少出现 3 次
- 三词短语：至少出现 2 次

排除常见的非标签词：冠词、介词、连词、代词。

### 第 3 步：语义分组

将相关候选分组到簇中：
- 合并单复数变体（保留更常见的形式）
- 合并连字符和非连字符形式
- 将同义词归类到最高频词下

### 第 4 步：去重和排序

- 对 slug 化名称进行模糊匹配（Levenshtein 距离 <= 2）
- 不要仅使用 Levenshtein 算法自动合并短于 5 个字符的 slug；需要词重叠或人工审核
- 对每个候选评分：`(频率 * 2) + (标题出现 * 5) + (强调 * 1)`
- 返回前 5-10 个排名靠前的建议

### 输出格式

```
## 标签建议：[文章标题]

| 排名 | 标签 | 分数 | 来源 |
|------|------|------|------|
| 1 | content-marketing | 18 | H2 + 6 次提及 |
| 2 | seo-strategy | 14 | H3 + 4 次提及 |
| 3 | keyword-research | 11 | 5 次提及 + 粗体 |

### 建议分类
- 主要：[最佳匹配分类]
- 次要：[可选第二分类]
```

## CMS 适配器

### 适配器概述

| CMS | API 类型 | 认证方法 | 标签模型 |
|------|----------|----------|----------|
| WordPress | REST | 应用密码（base64） | 具备 ID 的一流实体 |
| Shopify | GraphQL (管理 API) | 管理 API 访问令牌 | Article 上的字符串数组 |
| Ghost | REST (管理 API) | API 密钥带 JWT 签名 | 具备 ID 的一流实体 |
| Strapi | REST 或 GraphQL | API 令牌（Bearer） | 用户定义的内容类型 |
| Sanity | GROQ / Mutations | 项目令牌（Bearer） | 文档类型 |

### WordPress 适配器

**列出标签**：
```
GET {CMS_URL}/wp-json/wp/v2/tags?per_page=100&search={keyword}
Authorization: Basic {base64(username:app_password)}
```

**创建标签**：
```
POST {CMS_URL}/wp-json/wp/v2/tags
Body: {"name": "标签名称", "slug": "tag-name", "description": "可选"}
```

**列出分类**（支持层级，支持 parent 字段）：
```
GET {CMS_URL}/wp-json/wp/v2/categories?per_page=100
```

**创建分类**：
```
POST {CMS_URL}/wp-json/wp/v2/categories
Body: {"name": "分类", "slug": "category", "parent": 0}
```

**为文章分配标签**：
```
POST {CMS_URL}/wp-json/wp/v2/posts/{id}
Body: {"tags": [1, 2, 3], "categories": [4]}
```

分页：遵循 `X-WP-TotalPages` 头部获取完整列表。

### Shopify 适配器

Shopify 中的标签是 Article 对象上的字符串数组，不是一流实体。

**更新文章标签**（GraphQL 管理 API）：
```graphql
mutation {
  articleUpdate(id: "gid://shopify/Article/123", article: {
    tags: ["tag-one", "tag-two", "tag-three"]
  }) {
    article { id tags }
    userErrors { field message }
  }
}
```

**列出所有使用中的标签**（GraphQL）：
```graphql
{
  articles(first: 250, after: $cursor) {
    pageInfo { hasNextPage endCursor }
    edges {
      node { id title tags }
    }
  }
}
```

Auth 头部：`X-Shopify-Access-Token: {token}`

分页：当 `pageInfo.hasNextPage` 为 true 时循环，将 `endCursor` 作为下一个 `$cursor` 传递。

注意：REST API 于 2024 年 10 月标记为过时。自 2025 年 4 月起新应用必须使用 GraphQL。

### Ghost 适配器

**列出标签**：
```
GET {CMS_URL}/ghost/api/admin/tags/?limit=all
Authorization: Ghost {jwt_token}
```

**创建标签**：
```
POST {CMS_URL}/ghost/api/admin/tags/
Body: {"tags": [{"name": "标签名称", "slug": "tag-name"}]}
```

JWT 生成：使用管理 API 密钥（id:secret 格式）签名，iat = now，exp = 5 分钟，audience = `/admin/`。

### Strapi 适配器

端点自动生成自内容类型。典型设置：

```
GET {CMS_URL}/api/tags?pagination[pageSize]=100
POST {CMS_URL}/api/tags
Body: {"data": {"name": "标签名称", "slug": "tag-name"}}
Authorization: Bearer {api_token}
```

分页：递增 `pagination[page]` 直至所有页面都处理完毕。

Strapi v4 响应使用 `data` 包装器与 `attributes`；Strapi v5 使用更扁平的响应形状。检测版本或归一化两种形状以进行去重。检查你的内容类型模式以获取字段名称。

### Sanity 适配器

**查询标签**（GROQ）：
```
*[_type == "tag"] { _id, name, slug }
```

**创建标签**（Mutations API）：
```
POST https://{project_id}.api.sanity.io/{SANITY_API_VERSION}/data/mutate/{dataset}
Body: {"mutations": [{"create": {"_type": "tag", "name": "标签", "slug": {"current": "tag"}}}]}
Authorization: Bearer {token}
```

默认 `SANITY_API_VERSION` 为项目环境提供的当前测试 API 日期；不要在生成请求中硬编码它。

## 分类体系审计工作流

### 第 1 步：清单

扫描目标目录中的所有文章（或从 CMS 获取）。构建映射：
- tag_name -> [使用此标签的文章文件/ID 列表]
- category_name -> [使用此分类的文章文件/ID 列表]

### 第 2 步：健康检查

| 检查 | 阈值 | 操作 |
|------|------|------|
| 瘦标签存档 | < 5 篇文章/标签 | 审核合并或设置 noindex 后进行流量、意图和链接检查 |
| 孤立标签 | 0 篇文章 | 建议删除 |
| 标签臃肿 | 超过 `max(50, post_count * 0.25)` 个总标签，根据分类体系目的调整 | 建议合并 |
| 分类深度 | > 3 级 | 建议扁平化 |
| 未分类文章 | 未分配分类 | 分配到适当分类 |
| 重复 slug | 相同 slug，不同名称 | 合并到规范版本 |

### 第 3 步：建议

按优先级分组发现：
- **关键**：孤立标签导致空存档页面（爬虫浪费）
- **高**：瘦标签经流量、意图和链接检查后 < 5 篇文章
- **中**：超过按比例缩放阈值的标签臃肿（稀释分类，导航更困难）
- **低**：命名不一致（大小写混合，连字符与空格）

### 输出格式

```
## 分类体系审计：[网站/目录]

**总标签**：[n] | **总分类**：[n]
**健康**：[n] | **瘦**：[n] | **孤立**：[n]

### 关键问题
- [孤立标签列表]

### 建议
1. 合并 [tag-a] 和 [tag-b]（相同主题，[n] 合并文章）
2. 删除孤立标签：[列表]
3. 仅在流量、意图和链接检查后合并或设置瘦标签存档
```

## 全站指南

- 每个网站 5-10 个主要分类（广泛主题）
- 标签至少有 5 篇文章后才能创建存档页面
- 使用一致的 slug 格式：小写，连字符分隔
- 每篇文章必须恰好 1 个主要分类
- 每篇文章标签：3-8 个推荐，不超过 15 个

## 环境变量

| 变量 | 目的 | 示例 |
|------|------|------|
| CMS_TYPE | 平台标识符 | wordpress, shopify, ghost, strapi, sanity |
| CMS_URL | CMS 的 HTTPS 基础 URL | https://example.com |
| CMS_ALLOWED_HOSTS | 可选的 CMS 主机允许列表，逗号分隔 | example.com,admin.example.com |
| CMS_USERNAME | 使用应用密码时的 WordPress 用户名 | editor@example.com |
| CMS_API_KEY | 认证凭据 | WordPress 应用密码、API 令牌或密钥 |
| SANITY_API_VERSION | Sanity 变化的 API 日期 | v2026-07-01 |

这些必须在 shell 环境中设置。永远不要将凭据存储在文件中或提交到版本控制。该技能通过 `$CMS_TYPE`、`$CMS_URL`、`$CMS_USERNAME`、`$CMS_API_KEY` 和可选的平台特定变量在运行时读取它们。

CMS 调用安全规则：要求 HTTPS，仅允许解析 `http` 和 `https` 路径但仅通过 HTTPS 发送认证请求，解析 DNS 并阻止回环/私有/链路本地/保留 IP，使用相同检查验证重定向或禁用重定向，将超时限制为 10 秒，并强制执行 `CMS_ALLOWED_HOSTS`（如果设置）。

## 错误处理

- **缺失环境变量**：如果 CMS_TYPE、CMS_URL 或 CMS_API_KEY 未设置，或者 WordPress 缺少 CMS_USERNAME，报告缺失的变量并提供预期格式
- **无效凭据**：如果 CMS API 返回 401/403，报告“认证失败 - 检查 CMS_USERNAME/CMS_API_KEY”并不要重试
- **连接超时**：如果 CMS 端点在 10 秒后无法访问，报告超时并建议检查 CMS_URL
- **重复标签 slug**：如果 CMS 上已存在标签，跳过创建并注明“标签已存在：[名称]”
- **速率限制**：如果 CMS API 返回 429，存在时遵循 `Retry-After`；否则使用指数退避并重试一次。如果限制仍然存在，请报告
- **不支持 CMS**：如果 CMS_TYPE 不是 5 个支持平台之一，列出有效选项并退出
