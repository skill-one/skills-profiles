# Reddit 技能

通过公共 JSON API 从 Reddit 获取帖子、评论、子版块信息以及用户资料。

## 前置条件

**无需 API 密钥！** Reddit 的公共 JSON API 无需身份验证即可工作。

**快速检查**：
```bash
cd <技能目录>
python3 scripts/get_posts.py python --limit 3
```

## 命令

所有命令均从技能目录运行。

### 子版块帖子
```bash
python3 scripts/get_posts.py python --limit 20           # 热门帖子（默认）
python3 scripts/get_posts.py python --sort new --limit 20
python3 scripts/get_posts.py python --sort top --time week
python3 scripts/get_posts.py python --sort top --time all --limit 10
```

### 搜索帖子
```bash
python3 scripts/search_posts.py "AI agent" --limit 20
python3 scripts/search_posts.py "MCP server" --subreddit ClaudeAI --limit 10
python3 scripts/search_posts.py "async python" --sort top --time year
```

### 子版块信息
```bash
python3 scripts/get_subreddit.py python
python3 scripts/get_subreddit.py ClaudeAI
```

### 帖子与评论
```bash
python3 scripts/get_post.py abc123                       # 通过 ID 获取帖子
python3 scripts/get_post.py abc123 --comments 50         # 包含更多评论
```

### 用户资料
```bash
python3 scripts/get_user.py spez
python3 scripts/get_user.py spez --posts 10              # 包含近期帖子
```

## 排序选项

| 排序 | 描述 | 时间选项 |
|------|-------------|--------------|
| `hot` | 流行帖子（默认） | - |
| `new` | 最新帖子 | - |
| `top` | 最高票数 | 小时、天、周、月、年、全部 |
| `rising` | 越来越受欢迎 | - |
| `controversial` | 混合票数 | 小时、天、周、月、年、全部 |

## API 信息
- **方法**：公共 JSON API（无需认证）
- **技巧**：将 `.json` 添加到任何 Reddit URL
- **速率限制**：每分钟 100 个请求
- **文档**：https://www.reddit.com/dev/api
