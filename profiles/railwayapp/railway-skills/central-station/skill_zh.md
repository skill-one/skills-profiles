# 中央站

搜索和浏览 Railway 的中央站 - 用于主题、讨论和文档的社区支持平台。

## API 端点

| 端点         | URL                                       |
|--------------|------------------------------------------|
| GraphQL      | `https://station-server.railway.com/gql` |
| 主题 Markdown | `https://station-server.railway.com/api/threads/:slug` |
| LLM 数据导出 | `https://station-server.railway.com/api/llms-station` |
| 前端         | `https://station.railway.com`             |

## 何时使用

- 用户想要搜索中央站的主题或文档
- 用户询问关于社区讨论或支持问题
- 用户想要查找关于特定主题（部署、数据库等）的主题
- 用户询问“人们在询问 X 的什么”
- 用户想要查看最近的主题或问题
- 用户提到中央站、社区主题或支持讨论
- 用户在创建新主题之前想要查找现有解决方案

## 何时**不**使用

- 用户想要查看 Railway 产品文档 - 使用 `railway-docs` 技能
- 用户想要检查他们的项目状态 - 使用 `status` 技能
- 用户想要管理他们的 Railway 项目 - 使用适当的技能（部署、环境等）

## 文档搜索

对于官方 Railway 文档，使用 `railway-docs` 技能，它从 `https://docs.railway.com/api/llms-docs.md` 获取。

中央站的 `unifiedSearch` 可以识别文档类型，但字段访问有限：

```bash
curl -s 'https://station-server.railway.com/gql' \
  -H 'content-type: application/json' \
  --data-raw '{"query":"{ unifiedSearch(input: { query: \"volumes\", limit: 10 }) { results { document { __typename } } } }"}'
```

返回的文档类型：`EsThreadItem`（主题）和 `DocSearchResult`（文档）。

**注意**：对于搜索主题内容，使用 LLM 数据导出端点（见下文），它提供完整主题数据。

## 快速操作

### 获取最近主题

获取最近主题，可选择按主题过滤：

```bash
curl -s 'https://station-server.railway.com/gql' \
  -H 'content-type: application/json' \
  -d '{"query": "{ threads(first: 10, sort: recent_activity) { edges { node { slug subject status topic { slug displayName } upvoteCount createdAt } } } }"}'
```

带主题过滤：

```bash
curl -s 'https://station-server.railway.com/gql' \
  -H 'content-type: application/json' \
  -d '{"query": "{ threads(first: 10, sort: recent_activity, topic: \"questions\") { edges { node { slug subject status topic { displayName } upvoteCount } } } }"}'
```

### 通过 Slug 获取主题

获取特定主题及其内容：

```bash
curl -s 'https://station-server.railway.com/gql' \
  -H 'content-type: application/json' \
  -d '{"query": "{ thread(slug: \"THREAD_SLUG\") { slug subject status content { data } topic { displayName } upvoteCount } }"}'
```

### 获取 Markdown 格式的主题

为更清晰的阅读，获取主题的 Markdown 格式：

```bash
# 在前端 URL 后追加 .md（需要主题 Slug）
curl -s 'https://station.railway.com/TOPIC_SLUG/THREAD_SLUG.md'

# 或使用带 format 查询参数的 API
curl -s 'https://station-server.railway.com/api/threads/THREAD_SLUG?format=md'

# 或使用 Accept 头
curl -s 'https://station-server.railway.com/api/threads/THREAD_SLUG' \
  -H 'Accept: text/markdown'
```

### 列出主题

获取所有可用主题：

```bash
curl -s 'https://station-server.railway.com/gql' \
  -H 'content-type: application/json' \
  -d '{"query": "{ topics { slug displayName displayNamePlural } }"}'
```

返回：questions, feedback, community, billing, bug-bounty, privacy, abuse, templates

### 获取热门主题

获取当前热门主题：

```bash
curl -s 'https://station-server.railway.com/gql' \
  -H 'content-type: application/json' \
  -d '{"query": "{ trendingThreads { slug subject status topic { displayName } upvoteCount } }"}'
```

### 获取置顶主题

获取置顶/重要主题：

```bash
curl -s 'https://station-server.railway.com/gql' \
  -H 'content-type: application/json' \
  -d '{"query": "{ pinnedThreads { slug subject topic { displayName } } }"}'
```

### 通过 LLM 数据导出搜索

对于搜索主题内容，获取所有主题并本地过滤：

```bash
curl -s 'https://station-server.railway.com/api/llms-station' | jq '.items[] | select(.title | test("postgres"; "i")) | {title, topic: .topic.name, status: .metadata.status}'
```

此端点返回所有公开主题的完整内容，适用于按关键词搜索。

## 主题状态

| 状态                 | 描述                     |
|----------------------|--------------------------|
| `OPEN`               | 未解决，接受回复         |
| `SOLVED`             | 标记为已解决             |
| `AWAITING_RAILWAY_RESPONSE` | 等待 Railway 团队回复 |
| `AWAITING_USER_RESPONSE` | 等待原始发布者回复       |
| `CLOSED`             | 不再接受回复             |
| `ARCHIVED`           | 旧主题，保留以供参考     |

## 排序选项

对于 `threads` 查询，使用 `sort` 参数：

| 排序值             | 描述                     |
|---------------------|--------------------------|
| `recent_activity`   | 最近活跃（默认）         |
| `newest`            | 最新优先                 |
| `highest_votes`     | 最受点赞                 |

## 展示结果

当展示主题时：

1. **主题标题** - 主题
2. **主题** - 分类（问题、反馈等）
3. **状态** - 开放、已解决、等待回复
4. **摘要** - 内容的简要预览
5. **链接** - `https://station.railway.com/{topic_slug}/{thread_slug}`

格式示例：
```
找到 3 个关于 "postgres" 的主题：

1. "连接到 Postgres 时超时"
   主题：问题 | 状态：SOLVED | 点赞：5
   https://station.railway.com/questions/connection-timeout-postgres

2. "如何从本地开发环境连接到 Postgres"
   主题：社区 | 状态：OPEN | 点赞：12
   https://station.railway.com/community/connect-postgres-local

3. "Postgres SSL 证书验证失败"
   主题：问题 | 状态：AWAITING_RAILWAY_RESPONSE
   https://station.railway.com/questions/postgres-ssl-verification
```

## 常见搜索模式

| 用户查询                 | 过滤/搜索                 |
|--------------------------|--------------------------|
| "为什么我的部署失败？"   | 主题：问题，搜索："deploy" |
| "无法连接到数据库"       | 主题：问题，搜索："database" 或 "postgres" |
| "域名无法工作"           | 主题：问题，搜索："domain" |
| "功能请求"               | 主题：反馈               |
| "人们在做什么？"         | 主题：社区               |

## 组合性

- **找到主题后**：总结解决方案或链接到它
- **未找到结果**：建议使用 `railway-docs` 技能或创建新主题
- **发现技术问题**：使用相关技能（部署、环境等）帮助解决

## 错误处理

### 未找到结果

```
未找到主题。尝试：
- 不同的主题过滤
- 查看 Railway 文档
- 在 https://station.railway.com 创建新主题
```

### 无效主题

首先列出可用主题：
```bash
curl -s 'https://station-server.railway.com/gql' -H 'content-type: application/json' -d '{"query": "{ topics { slug } }"}'
```

### 主题未找到

```
主题未找到。它可能已被删除或标记为私密。
```
