# Twitter 技能（仅读）

使用 [opencli](https://github.com/jackwener/opencli) 读取 Twitter/X 进行金融研究，opencli 是一个通用 CLI 工具，通过浏览器会话复用将网络服务连接到终端。

**此技能仅支持读取操作。** 它专为金融研究设计：搜索市场讨论、阅读分析师推文、追踪情绪、监控 Twitter/X 上的金融新闻。它**不支持**发布、点赞、转发、回复或任何写入操作。

**重要提示**：opencli 会复用您现有的 Chrome 登录会话 — 无需 API 密钥或提取 Cookie。只需在 Chrome 中登录 x.com 并安装 Browser Bridge 扩展即可。

---

## 第 1 步：确保 opencli 已安装并准备就绪

**当前环境状态：**

```
!`(command -v opencli && opencli doctor 2>&1 | head -5 && echo "READY" || echo "SETUP_NEEDED") 2>/dev/null || echo "NOT_INSTALLED"`
```

如果上述状态显示 `READY`，则跳至第 2 步。如果显示 `NOT_INSTALLED`，请先安装：

```bash
# 全局安装 opencli
npm install -g @jackwener/opencli
```

如果显示 `SETUP_NEEDED`，请引导用户完成设置：

### 设置

opencli 需要 Node.js >= 20 和带有 Browser Bridge 扩展的 Chrome 浏览器：

1. **安装 Browser Bridge 扩展：**
   - 从 [GitHub 发布页面](https://github.com/jackwener/opencli/releases) 下载最新的 `opencli-extension-v{版本}.zip`
   - 解压，在 Chrome 中打开 `chrome://extensions`，并启用 **开发者模式**
   - 点击 **加载已解压的扩展** 并选择解压后的文件夹
2. **在 Chrome 中登录 x.com** — opencli 会复用您现有的浏览器会话
3. **验证连接性：**

```bash
opencli doctor
```

这将自动启动守护进程，验证扩展是否连接，并检查会话健康状况。

### 常见设置问题

| 症状 | 解决方法 |
|-------|-----|
| `Extension not connected` | 在 Chrome 中安装 Browser Bridge 扩展并确保已启用 |
| `Daemon not running` | 运行 `opencli doctor` — 它会自动启动守护进程 |
| `No session for twitter.com` | 在 Chrome 中登录 x.com，然后重试 |
| `CSRF token missing` | 在 Chrome 中刷新 x.com 以重新生成 ct0 Cookie |

---

## 第 2 步：确定用户需求

将用户的请求匹配到下方的读命令之一，然后使用 `references/commands.md` 中的相应命令。

| 用户请求 | 命令 | 关键标志 |
|---|---|---|
| 设置检查 | `opencli doctor` | — |
| 主页信息 / 时间线 | `opencli twitter timeline` | `--type for-you\|following`, `--limit N` (默认 20) |
| 搜索推文 | `opencli twitter search "QUERY"` | `--filter top\|live`, `--limit N` (默认 15) |
| 热门话题 | `opencli twitter trending` | `--limit N` (默认 20) |
| 收藏夹 | `opencli twitter bookmarks` | `--limit N` (默认 20) |
| 某用户的最新推文 | `opencli twitter tweets USERNAME` | `--limit N` (默认 20) |
| 查看特定话题 | `opencli twitter thread TWEET_ID` | `--limit N` (默认 50) |
| Twitter 文章 | `opencli twitter article TWEET_ID` | — |
| 用户资料 | `opencli twitter profile USERNAME` | — (默认为登录用户) |
| 关注者 | `opencli twitter followers USERNAME` | `--limit N` (默认 50) |
| 正在关注 | `opencli twitter following USERNAME` | `--limit N` (默认 50) |
| 通知 | `opencli twitter notifications` | `--limit N` (默认 20) |

---

## 第 3 步：执行命令

### 通用模式

```bash
# 使用 -f json 或 -f yaml 获取结构化输出
opencli twitter timeline -f json --limit 20
opencli twitter timeline --type following --limit 20

# 某用户的最新推文
opencli twitter tweets elonmusk --limit 20 -f json

# 搜索金融话题
opencli twitter search "$AAPL earnings" --filter live --limit 10 -f json
opencli twitter search "Fed rate decision" --limit 20 -f yaml

# 热门话题
opencli twitter trending --limit 20 -f json
```

### 关键规则

1. **先检查设置** — 如果不确定连接性，请在执行其他命令前运行 `opencli doctor`
2. **使用 `-f json` 或 `-f yaml`** 在处理数据时获取结构化输出
3. **使用 `-f csv`** 当用户需要电子表格兼容的输出时
4. **使用 `--limit N`** 控制结果数量 — 默认 10-20，除非用户要求更多
5. **搜索时使用 `--filter`** — `top` (默认) 表示相关性，`live` 表示最新推文
6. **绝对不要执行写入操作** — 此技能仅支持读取；不要发布、点赞、转发、回复、引用、关注或删除

### 输出格式标志 (`-f`)

| 格式 | 标志 | 适用场景 |
|---|---|---|
| 表格 | `-f table` (默认) | 人类可读的终端输出 |
| JSON | `-f json` | 程序化处理，LLM 上下文 |
| YAML | `-f yaml` | 结构化输出，可读 |
| Markdown | `-f md` | 文档，报告 |
| CSV | `-f csv` | 电子表格导出 |

### 输出列

推文列表命令 (`timeline`, `search`, `thread`) 包含：`id`, `author`, `text`, `created_at`, `likes`, `retweets`, `replies`, `views`, `url`, `has_media`, `media_urls`。

`tweets` (用户推文) 还包括 `is_retweet`。

`bookmarks` 列：`author`, `text`, `likes`, `retweets`, `bookmarks`, `url`。

`trending` 列：`rank`, `topic`, `tweets`, `category`。

资料 (`profile`) 列：`screen_name`, `name`, `bio`, `location`, `url`, `followers`, `following`, `tweets`, `likes`, `verified`, `created_at`。

`followers` / `following` 列：`screen_name`, `name`, `bio`, `followers`。

`notifications` 列：`id`, `action`, `author`, `text`, `url`。

---

## 第 4 步：展示结果

获取数据后，清晰展示结果以支持金融研究：

1. **总结关键内容** — 突出显示与用户金融研究最相关的推文
2. **注明来源** — 显示 @username、推文文本和互动指标（点赞、浏览量）
3. **提供推文链接** 当用户可能想阅读完整话题时
4. **搜索结果** 按相关性分组，突出关键主题、情绪或市场信号
5. **用户资料** 展示关注者数量、简介和近期显著活动
6. **标记情绪** — 注明看涨/看跌情绪，共识与反共识观点
7. **保护会话隐私** — 绝不暴露浏览器会话详情

---

## 第 5 步：诊断

如果出现问题，运行：

```bash
opencli doctor
```

这将检查守护进程状态、扩展连接性和浏览器会话健康状况。

---

## 错误参考

| 错误 | 原因 | 解决方法 |
|-------|-----|-----|
| `Extension not connected` | Browser Bridge 未安装/未启用 | 安装扩展并在 Chrome 中启用 |
| `No session` | 未登录 x.com | 在 Chrome 中登录 x.com |
| `CSRF token missing` | Cookie 过期或页面需要刷新 | 在 Chrome 中刷新 x.com |
| Rate limited | 请求过多 | 等待几分钟，然后重试 |

---

## 参考文件

- `references/commands.md` — 完整的读命令参考，包含所有标志、研究工作流和示例
- `references/schema.md` — 输出格式文档和列定义

需要精确命令语法、研究工作流模式或输出详情时，请阅读参考文件。
