# ProductHunt 技能

通过官方的 GraphQL API 从 Product Hunt 获取帖子、主题、用户和收藏。

## 前置条件

在 `~/.zshrc` 中设置访问令牌：
```bash
export PRODUCTHUNT_ACCESS_TOKEN="你的开发者令牌"
```

从以下链接获取你的令牌：https://www.producthunt.com/v2/oauth/applications

**快速检查**：
```bash
cd <技能目录>
python3 scripts/get_posts.py --limit 3
```

## 命令

所有命令都在技能目录下运行。

### 帖子
```bash
python3 scripts/get_post.py chatgpt                    # 通过 slug 获取帖子
python3 scripts/get_post.py 12345                      # 通过 ID 获取帖子
python3 scripts/get_posts.py --limit 20                # 今日精选帖子
python3 scripts/get_posts.py --topic ai --limit 10     # 主题中的帖子
python3 scripts/get_posts.py --after 2026-01-01        # 指定日期后的帖子
python3 scripts/get_post_comments.py POST_ID --limit 20
```

### 主题
```bash
python3 scripts/get_topic.py artificial-intelligence  # 通过 slug 获取主题
python3 scripts/get_topics.py --query "AI" --limit 20 # 搜索主题
python3 scripts/get_topics.py --limit 50              # 热门主题
```

### 用户
```bash
python3 scripts/get_user.py rrhoover                  # 通过用户名获取用户
python3 scripts/get_user_posts.py rrhoover --limit 20 # 用户的帖子
```

### 收藏
```bash
python3 scripts/get_collection.py SLUG_OR_ID          # 获取收藏
python3 scripts/get_collections.py --featured --limit 20
```

## API 信息
- **端点**: https://api.producthunt.com/v2/api/graphql
- **类型**: GraphQL
- **速率限制**: 15 分钟内 6250 复杂度点
- **文档**: https://api.producthunt.com/v2/docs
