# firecrawl interact

通过实时浏览器会话与抓取的页面进行交互。先抓取页面，然后使用自然语言提示或代码来点击、填写表单、导航和提取数据。对于网络搜索，请使用 `search` —— interact 用于对特定页面进行操作。

## 快速入门

```bash
# 1. 抓取页面（抓取 ID 会自动保存）
firecrawl scrape "<url>"

# 2. 使用位置提示与页面交互
firecrawl interact "点击登录按钮"
firecrawl interact "用 test@example.com 填写邮箱字段"
firecrawl interact "提取价格表"

# 第一个参数为 UUID 时会自动检测为抓取 ID
firecrawl interact "<抓取-id>" "提取价格表"

# 3. 或使用代码进行精确控制
firecrawl interact --code "agent-browser click @e5" --bash
firecrawl interact --code "agent-browser snapshot -i" --bash

# 4. 完成后停止会话
firecrawl interact stop
```

运行 `firecrawl interact --help` 获取完整选项列表。

**完成条件：** 请求的内容或操作结果被捕获，并且使用 `firecrawl interact stop` 停止了会话。

## 配置文件

在抓取时使用 `--profile` 以跨抓取持久化浏览器状态（cookies、localStorage）：

```bash
# 会话 1：登录并保存状态
firecrawl scrape "https://app.example.com/login" --profile my-app
firecrawl interact --prompt "用 user@example.com 填写邮箱并点击登录"

# 会话 2：返回已认证状态
firecrawl scrape "https://app.example.com/dashboard" --profile my-app
firecrawl interact --prompt "提取仪表板数据"
```

只读重连（不会写入配置文件状态）：

```bash
firecrawl scrape "https://app.example.com" --profile my-app --no-save-changes
```

## 小贴士

- 始终先抓取页面 —— `interact` 需要 `firecrawl scrape` 调用之前的抓取 ID
- 抓取 ID 会自动保存，因此后续的 interact 调用可以省略 `--scrape-id`。保存的会话可能在约 10 分钟后过期；如果 CLI 警告会话已过期，请重新抓取
- 使用 `firecrawl interact stop` 完成后释放资源
- 对于并行工作，抓取多个页面，并使用 `--scrape-id` 与每个页面交互

## 参见

- [firecrawl-scrape](../firecrawl-scrape/SKILL.md) —— 先尝试抓取，仅在需要时升级到 interact
- [firecrawl-search](../firecrawl-search/SKILL.md) —— 使用 `search` 进行网络搜索
- [firecrawl-agent](../firecrawl-agent/SKILL.md) —— AI 驱动的提取（手动控制较少）
- [firecrawl-build-interact](https://github.com/firecrawl/skills/tree/main/skills/build/firecrawl-build-interact) —— 将 interact 集成到应用程序中而不是在此处运行
