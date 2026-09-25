# Twitter / X (脚本模式)

对twitterapi.io端点的只读访问。13个函数涵盖推文、用户、关注者、回复、话题串、引用、文章和趋势。

所有请求都通过sc-proxy，通过`core.http_client.proxied_get`发送。`TWITTER_API_KEY`环境变量在服务器端自动注入，代理机器上不需要本地密钥。

## 脚本使用

标准的调用模式：

```bash
python3 - <<'EOF'
import sys, json
sys.path.insert(0, "/data/workspace/skills/twitter")
from exports import twitter_user_info, twitter_user_tweets

profile = twitter_user_info(username="vitalikbuterin")
print(json.dumps(profile, indent=2))

recent = twitter_user_tweets(username="vitalikbuterin")
print(f"got {len(recent.get('tweets', []))} tweets")
EOF
```

从URL中提取推文ID：任何`x.com/{user}/status/{id}`或`twitter.com/{user}/status/{id}` URL的最后一个路径段都是推文ID。将其作为字符串传递（Python整数在长ID上会丢失精度）。

## 函数参考（签名）

所有13个函数都在`exports.py`中。返回值是直接从twitterapi.io返回的字典——每个端点的键都不同，脚本前需要检查一次。

### 推文端点

| 函数 | 描述 |
|---|---|
| `twitter_search_tweets(query, cursor=None)` | 高级搜索。操作符：`from:user`，`to:user`，`#tag`，`$cashtag`，`lang:en`，`has:media`，`has:links`，`is:reply`，`min_faves:N`，`since:YYYY-MM-DD`，`until:YYYY-MM-DD`。 |
| `twitter_get_tweets(tweet_ids)` | 通过ID获取一个或多个推文。`tweet_ids` = 字符串列表（也接受逗号字符串）。 |
| `twitter_tweet_replies(tweet_id, cursor=None)` | 推文的回复。 |
| `twitter_tweet_retweeters(tweet_id, cursor=None)` | 转发的人。 |
| `twitter_tweet_thread_context(tweet_id)` | 完整的话题串上下文（父级 + 直接回复）。 |
| `twitter_tweet_quote(tweet_id, cursor=None)` | 引用推文。 |
| `twitter_get_article(tweet_id)` | 长格式X文章正文。 |
| `twitter_get_trends(woeid=None, country=None, category=None, limit=None)` | 热门话题；所有过滤器都是可选的。 |

### 用户端点

| 函数 | 描述 |
|---|---|
| `twitter_user_info(username)` | 个人资料：简介、关注者/关注数、推文数、已验证。 |
| `twitter_user_tweets(username, cursor=None)` | 用户的最近推文。 |
| `twitter_user_followers(username, cursor=None)` | 关注者列表。 |
| `twitter_user_followings(username, cursor=None)` | 关注的账户。 |
| `twitter_search_users(query, cursor=None)` | 通过名称/关键词搜索用户。 |

`username`是**不包含`@`**的标识符（例如`"elonmusk"`，而不是`"@elonmusk"`）。
分页：当响应包含`next_cursor`时，将其作为下一次调用的`cursor`返回。

## 何时使用此技能

- 任何`x.com/...`或`twitter.com/...` URL → 从这里开始，**不是`web_fetch`**（Twitter阻止爬虫）。
- 单个推文详情 → `twitter_get_tweets([tweet_id])`。
- "用户@user最近在发布什么？" → `twitter_user_tweets`。
- KOL发现 / cashtag提及 → `twitter_search_tweets("$SOL min_faves:50")`。
- 热门话题 → `twitter_get_trends`。

## 计费与成本控制（批量/计划使用前阅读）

twitterapi.io按**实际返回的项目**计费，**不是按请求**，也**不是按你请求的任何"max_results"**。sc-proxy的计费 = 返回的项目数 × 单位（推文45 / 个人资料54 / 关注者45信用；100k信用 = $1；3×上游）。
每个请求至少返回1个项目。

**`last_tweets` / `user_tweets`陷阱**：上游`/twitter/user/last_tweets`端点**没有页大小参数**——它总是返回**每页最多20条推文**。没有`max_results` / `pageSize`杠杆，`twitter_user_tweets()`也不接受一个。所以"我只需要5条"仍然会获取并**计费约20条**。客户端切片**不会省钱**——计费已经在代理从上游响应中计算过了。

### ⭐ 轮询"账户X的新推文" → 使用搜索，**不要使用last_tweets**

这是最大的、最常见的浪费。`twitter_user_tweets()`（上游`last_tweets`）**没有页大小参数**，并且每次调用都会计费一个**完整的~20条推文的页面**，即使没有新发布。官方twitterapi.io指南建议使用**高级搜索**端点，我们的技能已经将其作为`twitter_search_tweets()`公开：

```python
# 廉价的轮询模式——只计费窗口中的实际推文。
# 当没有新推文时，调用计费为1个项目（不是20）。
import time
since = int(last_check_unix)
until = int(time.time())
q = f"from:{handle} include:nativeretweets since_time:{since} until_time:{until}"
res = twitter_search_tweets(q)   # queryType默认为Latest
```

官方定价（上游；我们的代理计费3×）：
- 找到的推文 → 每条返回推文$0.00015
- **未找到推文 → 整个调用$0.00015**（与last_tweets的~20×相比）

我们在计费中的每次调用成本使差异显而易见：
- `last_tweets` → ~$0.009/调用（每次20条推文）
- `advanced_search`空窗口 → ~$0.00045/调用（1个项目）——**~20×更便宜**

频率与月成本（单个账户，上游）：每小时$0.11 · 30分钟$0.22 · 15分钟$0.43 · 5分钟$1.30 · 1分钟$6.48。

### 其他成本杠杆
- **使用`get_tweets([ids])`**当ID已知时——只为你请求的这些确切推文付费，而不是20项页面。
- **关注者/关注**按返回的个人资料计费（默认页200 → 200计费）。仅按需分页。对于仅ID的图工作使用批量关注者-IDs端点（轻量级）。
- **收紧搜索查询**（min_faves，since_time/until_time，lang）以便需要较少页面。

> 注意：twitterapi.io还销售一个托管流/ webhook产品。**我们**不订阅它——不要使用`/oapi/x_user_stream/*`或`/oapi/tweet_filter/*`端点。对于任何账户监控需求，上述高级搜索轮询模式是正确且唯一的方法。

## 错误处理

- `402 信用不足` → 上游代理信用耗尽；告诉用户充值。不要重试。
- `429` → 速率限制；向用户显示，不要自动重试。
- `404 用户未找到` → 建议验证标识符拼写。

## 版本策略（硬规则）

此技能是**脚本模式**（`delivery: script`）。它不会注册运行时工具——代理必须`read_file` SKILL.md并通过`bash` + `python3`调用函数。遗留的`tools.py` / `__init__.py`文件保留以向后兼容，但不再是最优选的入口点。

版本规则：
- 任何签名更改、环境变量更改或sc-proxy合同更改 → MAJOR
- 添加新函数、响应模式澄清 → MINOR
- 修复错误或仅文档更改 → PATCH
