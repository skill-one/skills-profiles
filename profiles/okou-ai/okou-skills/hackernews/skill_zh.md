## 如何使用

### 1. 获取顶级故事

获取当前前500个故事的ID：

```bash
curl -s "https://hacker-news.firebaseio.com/v0/topstories.json" | jq '.[:10]'
```

### 2. 获取最佳故事

获取最佳故事（按时间投票最高）：

```bash
curl -s "https://hacker-news.firebaseio.com/v0/beststories.json" | jq '.[:10]'
```

### 3. 获取新故事

获取最新故事：

```bash
curl -s "https://hacker-news.firebaseio.com/v0/newstories.json" | jq '.[:10]'
```

### 4. 获取Ask HN故事

获取"Ask HN"帖子：

```bash
curl -s "https://hacker-news.firebaseio.com/v0/askstories.json" | jq '.[:10]'
```

### 5. 获取Show HN故事

获取"Show HN"帖子：

```bash
curl -s "https://hacker-news.firebaseio.com/v0/showstories.json" | jq '.[:10]'
```

### 6. 获取工作故事

获取工作发布：

```bash
curl -s "https://hacker-news.firebaseio.com/v0/jobstories.json" | jq '.[:10]'
```

## 项目详情

### 7. 获取故事/评论/工作详情

通过ID获取任何项目的完整详情。将`<item-id>`替换为实际的项目ID：

```bash
curl -s "https://hacker-news.firebaseio.com/v0/item/<item-id>.json"
```

**响应字段：**

| 字段 | 描述 |
|-------|-------------|
| `id` | 唯一项目ID |
| `type` | `story`, `comment`, `job`, `poll`, `pollopt` |
| `by` | 作者的用户名 |
| `time` | Unix时间戳 |
| `title` | 故事标题（仅限故事） |
| `url` | 故事URL（如果是外部链接） |
| `text` | 内容文本（Ask HN, 评论） |
| `score` | 点赞数 |
| `descendants` | 总评论数 |
| `kids` | 子评论ID数组 |

### 8. 获取带详情的多个故事

获取前5个故事及其完整详情。将`<item-id>`替换为实际的项目ID：

```bash
curl -s "https://hacker-news.firebaseio.com/v0/topstories.json" | jq '.[:5][]' | while read id; do
  curl -s "https://hacker-news.firebaseio.com/v0/item/${id}.json" | jq '{id, title, score, url, by}'
done
```

### 9. 获取故事及其评论

获取一个故事及其顶级评论。将`<story-id>`替换为实际的故事ID：

```bash
curl -s "https://hacker-news.firebaseio.com/v0/item/<story-id>.json" | jq '{title, score, descendants, kids}'
```

然后对于`kids`数组中的每个评论ID，将`<comment-id>`替换为实际评论ID：

```bash
curl -s "https://hacker-news.firebaseio.com/v0/item/<comment-id>.json" | jq '{by, text, score}'
```

## 用户数据

### 10. 获取用户资料

获取用户详情。将`<username>`替换为实际的用户名：

```bash
curl -s "https://hacker-news.firebaseio.com/v0/user/<username>.json"
```

**响应字段：**

| 字段 | 描述 |
|-------|-------------|
| `id` | 用户名 |
| `created` | 账户创建时间戳 |
| `karma` | 用户的karma分数 |
| `about` | 用户简介（HTML） |
| `submitted` | 提交的项目ID数组 |

### 11. 获取用户的最近提交

获取用户的最近提交。将`<username>`替换为实际的用户名：

```bash
curl -s "https://hacker-news.firebaseio.com/v0/user/<username>.json" | jq '.submitted[:5]'
```

## 实时更新

### 12. 获取最大项目ID

获取当前最大的项目ID（用于轮询新项目）：

```bash
curl -s "https://hacker-news.firebaseio.com/v0/maxitem.json"
```

### 13. 获取变更的项目和资料

获取最近变更的项目和资料（用于实时更新）：

```bash
curl -s "https://hacker-news.firebaseio.com/v0/updates.json"
```

## 实用示例

### 获取今天的Top 10及分数

```bash
curl -s "https://hacker-news.firebaseio.com/v0/topstories.json" | jq '.[:10][]' | while read id; do
  curl -s "https://hacker-news.firebaseio.com/v0/item/${id}.json" | jq -r '"\(.score) points | \(.title) | \(.url // "Ask HN")"'
done
```

### 查找高分故事（100+分）

```bash
curl -s "https://hacker-news.firebaseio.com/v0/topstories.json" | jq '.[:30][]' | while read id; do
  curl -s "https://hacker-news.firebaseio.com/v0/item/${id}.json" | jq -r 'select(.score >= 100) | "\(.score) | \(.title)"'
done
```

### 获取最新的AI/ML相关故事

```bash
curl -s "https://hacker-news.firebaseio.com/v0/topstories.json" | jq '.[:50][]' | while read id; do
  curl -s "https://hacker-news.firebaseio.com/v0/item/${id}.json" | jq -r 'select(.title | test("AI|GPT|LLM|Machine Learning|Neural"; "i")) | "\(.score) | \(.title)"'
done
```

## API端点摘要

| 端点 | 描述 |
|----------|-------------|
| `/v0/topstories.json` | 前500个故事 |
| `/v0/beststories.json` | 最佳故事 |
| `/v0/newstories.json` | 最新500个故事 |
| `/v0/askstories.json` | Ask HN故事 |
| `/v0/showstories.json` | Show HN故事 |
| `/v0/jobstories.json` | 工作发布 |
| `/v0/item/{id}.json` | 项目详情 |
| `/v0/user/{id}.json` | 用户资料 |
| `/v0/maxitem.json` | 当前最大项目ID |
| `/v0/updates.json` | 变更的项目/资料 |

## 指南

1. **无速率限制文档记录**：但请保持尊重，批量获取时添加延迟
2. **使用jq进行过滤**：过滤JSON响应以提取所需数据
3. **缓存结果**：故事不经常变更，尽可能缓存
4. **小心批量请求**：每个项目需要单独的API调用
5. **处理null值**：某些字段可能为null或缺失（例如，Ask HN的`url`）
6. **Unix时间戳**：所有时间都是Unix时间戳，按需转换
