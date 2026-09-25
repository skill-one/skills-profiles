# Twitter/X 技能

通过 twitterapi.io 从 Twitter/X 获取用户资料、推文、回复、关注者/正在关注、社区、空间和趋势。

## 前置条件

在 `~/.zshrc` 中设置 API 密钥：
```bash
export TWITTERAPI_API_KEY="your_api_key"
```

**快速检查**：
```bash
cd <技能目录>
python3 scripts/get_user_info.py elonmusk
```

## 命令

所有命令从技能目录运行。

### 用户端点
```bash
python3 scripts/get_user_info.py USERNAME
python3 scripts/get_user_about.py USERNAME
python3 scripts/batch_get_users.py USER_ID1,USER_ID2
python3 scripts/get_user_tweets.py USERNAME --limit 20
python3 scripts/get_user_mentions.py USERNAME --limit 20
python3 scripts/get_followers.py USERNAME --limit 100
python3 scripts/get_following.py USERNAME --limit 100
python3 scripts/get_verified_followers.py USERNAME --limit 20
python3 scripts/check_relationship.py USER1 USER2
python3 scripts/search_users.py "query" --limit 20
```

### 推文端点
```bash
python3 scripts/get_tweet.py TWEET_ID [TWEET_ID2...]
python3 scripts/search_tweets.py "query" --type Latest --limit 20
python3 scripts/get_tweet_replies.py TWEET_ID --limit 20
python3 scripts/get_tweet_quotes.py TWEET_ID --limit 20
python3 scripts/get_tweet_retweeters.py TWEET_ID --limit 50
python3 scripts/get_tweet_thread.py TWEET_ID
python3 scripts/get_article.py TWEET_ID
```

### 列表端点
```bash
python3 scripts/get_list_followers.py LIST_ID --limit 20
python3 scripts/get_list_members.py LIST_ID --limit 20
```

### 社区端点
```bash
python3 scripts/get_community.py COMMUNITY_ID
python3 scripts/get_community_members.py COMMUNITY_ID --limit 20
python3 scripts/get_community_moderators.py COMMUNITY_ID
python3 scripts/get_community_tweets.py COMMUNITY_ID --limit 20
python3 scripts/search_community_tweets.py "query" --limit 20
```

### 其他端点
```bash
python3 scripts/get_space.py SPACE_ID
python3 scripts/get_trends.py --woeid 1  # 全球
```

## 搜索查询语法

```bash
# 基本搜索
python3 scripts/search_tweets.py "AI agent"

# 从特定用户
python3 scripts/search_tweets.py "from:elonmusk"

# 日期范围
python3 scripts/search_tweets.py "AI since:2024-01-01 until:2024-12-31"

# 排除转发
python3 scripts/search_tweets.py "AI -filter:retweets"

# 带媒体
python3 scripts/search_tweets.py "AI filter:media"

# 最小互动量
python3 scripts/search_tweets.py "AI min_faves:1000"
```

## API: twitterapi.io
- 基础 URL: https://api.twitterapi.io/twitter
- 认证: X-API-Key 头部
- 定价: ~$0.15-0.18/1k 请求
- 文档: https://docs.twitterapi.io/
