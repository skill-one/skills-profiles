# 获取推文

从 X/Twitter URL 中获取推文原文、作者信息、互动数据的功能。
利用 FxEmbed 开源项目的 API (`api.fxtwitter.com`)，无需 JavaScript 即可提取推文数据。

## 工作原理

将 X/Twitter URL 的域名转换为 `api.fxtwitter.com` 后，会以 JSON 格式返回推文全部数据。

```
https://x.com/user/status/123456
  → https://api.fxtwitter.com/user/status/123456
```

## 脚本

`scripts/fetch_tweet.py` - 仅使用标准库，无外部依赖。

```bash
# 基本使用（格式化输出）
python scripts/fetch_tweet.py https://x.com/garrytan/status/2020072098635665909

# JSON 输出（编程使用）
python scripts/fetch_tweet.py https://x.com/garrytan/status/2020072098635665909 --json
```

支持的 URL 格式: `x.com`, `twitter.com`, `fxtwitter.com`, `fixupx.com`

## API 响应字段

| 字段 | 说明 |
|------|------|
| `tweet.text` | 推文正文（URL 扩展） |
| `tweet.author` | 作者（name, screen_name, bio, followers） |
| `tweet.likes/retweets/replies/bookmarks/views` | 互动数据 |
| `tweet.created_at` | 创建时间 |
| `tweet.media` | 附件媒体（photos, videos） |
| `tweet.quote` | 引用推文（相同结构） |
| `tweet.lang` | 语言代码 |

## 工作流程

### 获取单个推文

1. 从 URL 中提取 screen_name 和 status_id
2. 执行 `scripts/fetch_tweet.py <url>`
3. 将结果展示给用户或进行翻译

### 翻译请求时

1. 使用脚本获取原文
2. 将获取的文本翻译成韩语后提供
3. 同时显示互动数据

### 与其他功能联动

在 Contents Hub 等处收集的 X URL 列表进行批量处理时:

```bash
# JSON 输出进行管道联动
python scripts/fetch_tweet.py <url> --json | python3 -c "import sys,json; print(json.load(sys.stdin)['tweet']['text'])"
```

## WebFetch 备用方案

脚本执行困难时，可直接使用 WebFetch 工具调用 API:

```
URL: https://api.fxtwitter.com/{screen_name}/status/{status_id}
Prompt: "Extract the full tweet text and author name"
```

## 限制

- 无法查看私密账户的推文
- 无法查看已删除的推文
- API rate limit 遵循 FxEmbed 服务器政策（常规使用级别不受影响）
