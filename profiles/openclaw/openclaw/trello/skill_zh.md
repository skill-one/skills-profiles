# Trello 技能

直接从 OpenClaw 管理 Trello 的看板、列表和卡片。

## 设置

1. 获取你的 API 密钥：https://trello.com/app-key
2. 生成一个令牌（点击该页面上的“令牌”链接）
3. 设置环境变量：
   ```bash
   export TRELLO_API_KEY="your-api-key"
   export TRELLO_TOKEN="your-token"
   ```

## 使用

所有命令都使用 curl 来调用 Trello REST API。

### 列出看板

```bash
curl -s "https://api.trello.com/1/members/me/boards?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" | jq '.[] | {name, id}'
```

### 列出看板中的列表

```bash
curl -s "https://api.trello.com/1/boards/{boardId}/lists?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" | jq '.[] | {name, id}'
```

### 列出列表中的卡片

```bash
curl -s "https://api.trello.com/1/lists/{listId}/cards?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" | jq '.[] | {name, id, desc}'
```

### 创建卡片

```bash
curl -s -X POST "https://api.trello.com/1/cards?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" \
  -d "idList={listId}" \
  -d "name=Card Title" \
  -d "desc=Card description"
```

### 将卡片移动到另一个列表

```bash
curl -s -X PUT "https://api.trello.com/1/cards/{cardId}?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" \
  -d "idList={newListId}"
```

### 向卡片添加评论

```bash
curl -s -X POST "https://api.trello.com/1/cards/{cardId}/actions/comments?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" \
  -d "text=Your comment here"
```

### 归档卡片

```bash
curl -s -X PUT "https://api.trello.com/1/cards/{cardId}?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" \
  -d "closed=true"
```

## 注意事项

- 看板/列表/卡片 ID 可以在 Trello URL 中找到，或通过列表命令获取
- API 密钥和令牌可完全访问你的 Trello 账户 - 请保持它们安全！
- 速率限制：每个 API 密钥每 10 秒 300 个请求；每个令牌每 10 秒 100 个请求；`/1/members` 端点每 900 秒限制 100 个请求

## 示例

```bash
# 获取所有看板
curl -s "https://api.trello.com/1/members/me/boards?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN&fields=name,id" | jq

# 通过名称查找特定看板
curl -s "https://api.trello.com/1/members/me/boards?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" | jq '.[] | select(.name | contains("Work"))'

# 获取看板上的所有卡片
curl -s "https://api.trello.com/1/boards/{boardId}/cards?key=$TRELLO_API_KEY&token=$TRELLO_TOKEN" | jq '.[] | {name, list: .idList}'
```
