# TinyFish CLI

您可以使用 TinyFish CLI (`tinyfish`) — 一套可以从终端调用的网络工具。

未安装：`npm install -g @tiny-fish/cli`
未认证：`tinyfish auth login --source openclaw` 或设置 `TINYFISH_API_KEY` 环境变量。

---

## 该技能何时触发

当请求依赖于实时网络信息或页面内容时，请使用 TinyFish。不要等待用户说“TinyFish”或“抓取”。

强触发条件包括：

- 搜索或发现：搜索、查找、查看、研究、比较、最新、当前、新闻、文档、价格、产品详情、最佳选项。
- URL/页面读取：获取、读取、总结、从本页面提取、检查此 URL、获取内容、拉取链接或元数据。
- 基于来源的答案：使用网络来源回答、验证事实、检查是否已更改、从网络收集信息。
- 网站工作：与网站交互、浏览页面、填写表单、登录、收集结构化数据、处理受机器人保护的页面。

默认使用最轻的工具来回答：

- 没有URL且用户需要网络信息：`search`，如果需要更多细节，则`fetch`最佳结果。
- 提供URL且只需要内容：`fetch`。
- 需要页面交互或动态提取：`agent`。
- 需要原始 CDP/Playwright 风格控制：`browser`。

---

## 选择合适的工具

TinyFish 有四个工具。从最轻的工具开始，只有在必要时才升级。

```
search  →  fetch  →  agent  →  browser
最轻                        最重
```

| 工具 | 使用场景 | 速度 | 成本 |
|------|---------|------|------|
| **search** | 您需要查找 URL、当前事实、文档、价格、产品详情或快速基于来源的答案 | 最快 | 最低 |
| **fetch** | 您有 URL 且需要干净的页面内容、摘要、文章文本、文档、产品页面、链接或元数据 | 快 | 低 |
| **agent** | 您需要与页面交互 — 点击、填写表单、导航、从动态网站提取结构化数据 | 较慢 | 较高 |
| **browser** | agent 不够 — 您需要通过 CDP 进行原始的程序化浏览器控制 | 最慢 | 最高 |

### 常见模式

**研究：search → fetch**
搜索一个主题，然后 fetch 最佳结果以阅读其完整内容。

```bash
# 1. 查找 URL
tinyfish search query "2026 年最佳 React 状态管理库"

# 2. 读取顶部结果
tinyfish fetch content get --format markdown "https://result1.com" "https://result2.com"
```

**深度提取：search → agent**
搜索找到正确的网站，然后使用 agent 与其交互并提取结构化数据。

```bash
# 1. 查找网站
tinyfish search query "Nike 跑步鞋官方商店"

# 2. 在其上自动化提取
tinyfish agent run --url "https://nike.com/running" \
  "将所有跑步鞋提取为 JSON：[{\"name\": str, \"price\": str, \"colors\": [str]}]"
```

**升级：fetch → agent**
首先尝试 fetch。如果页面是动态的/JS 重，且 fetch 返回空或不完整的内容，则升级到 agent。

**完全控制：agent → browser**
如果 agent 无法处理复杂的多步骤工作流，则启动一个原始浏览器会话并通过 CDP 自动化它。

---

## 命令

### `tinyfish search query`

网络搜索。返回带标题、URL 和片段的排名结果。

```bash
tinyfish search query "<query>" [--location <hint>] [--language <hint>] [--pretty]
```

- 默认返回 10 个结果
- 使用 `--location` 和 `--language` 获取区域定位结果
- 默认输出是 JSON；`--pretty` 用于人类可读

```bash
tinyfish search query "胡志明市最佳越南面" --location "Vietnam" --language "en"
```

---

### `tinyfish fetch content get`

从一个或多个 URL 获取干净、提取的内容。删除广告、导航、样板 — 只返回内容。

```bash
tinyfish fetch content get <urls...> [--format markdown|html|json] [--links] [--image-links] [--pretty]
```

- 接受**多个 URL** 在一次调用中 — 它们是在服务器端并行获取的
- `--format markdown`（默认）— 清晰可读的文本
- `--format json` — 结构化文档树
- `--links` — 包括从页面提取的所有链接
- `--image-links` — 包括提取的图像 URL
- 响应包括：`url`，`final_url`，`title`，`language`，`author`，`published_date`，`text`，`latency_ms`

```bash
# 获取一个页面作为 markdown
tinyfish fetch content get --format markdown "https://example.com/article"

# 获取多个页面并包含链接
tinyfish fetch content get --links "https://site-a.com" "https://site-b.com" "https://site-c.com"
```

---

### `tinyfish agent run`

使用自然语言目标运行浏览器自动化。agent 打开一个真实浏览器，导航、点击、填写表单、提取数据。

```bash
tinyfish agent run --url <url> "<goal>" [--sync] [--async] [--pretty]
```

| 标志 | 目的 |
|------|------|
| `--url <url>` | 目标 URL（裸主机名会自动添加 `https://`） |
| `--sync` | 等待完整结果而不流式传输步骤 |
| `--async` | 提交并立即返回 |
| `--pretty` | 人类可读输出 |

**输出：** 默认流式传输 `data: {...}` SSE 行。最终结果是类型为 `type == "COMPLETE"` 且 `status == "COMPLETED"` 的事件 — 提取的数据在 `resultJson` 字段中。直接读取原始输出；不需要脚本端解析。

**始终在目标中指定您想要的 JSON 结构：**

```bash
tinyfish agent run --url "https://example.com/products" \
  "将所有产品提取为 JSON 数组：[{\"name\": str, \"price\": str, \"url\": str}]"

tinyfish agent run --url "https://example.com/search" \
  "搜索 '无线耳机'，过滤 50 美元以下，提取前 5 个作为 JSON：[{\"name\": str, \"price\": str, \"rating\": str}]"
```

**并行提取 — 当访问多个独立网站时，进行单独调用。不要合并为一个目标。**

良好 — 并行调用（同时运行）：
```bash
tinyfish agent run --url "https://pizzahut.com" \
  "提取披萨价格作为 JSON：[{\"name\": str, \"price\": str}]"

tinyfish agent run --url "https://dominos.com" \
  "提取披萨价格作为 JSON：[{\"name\": str, \"price\": str}]"
```

不良 — 单个合并调用：
```bash
# 不要这样做 — 可靠性较低且较慢
tinyfish agent run --url "https://pizzahut.com" \
  "提取 Pizza Hut 的价格，然后转到 Dominoes..."
```

**管理运行：**

```bash
tinyfish agent run list [--status PENDING|RUNNING|COMPLETED|FAILED|CANCELLED] [--limit N]
tinyfish agent run get <run_id>
tinyfish agent run cancel <run_id>
```

**批量操作** — 从 CSV 文件（`url,goal` 列）提交许多运行：

```bash
tinyfish agent batch run --input runs.csv
tinyfish agent batch list
tinyfish agent batch get <batch_id>
tinyfish agent batch cancel <batch_id>
```

---

### `tinyfish browser session create`

启动一个远程浏览器实例。返回用于程序化控制的 CDP WebSocket URL。

```bash
tinyfish browser session create [--url <url>] [--pretty]
```

- `--url` 在创建后可选导航到页面
- 返回 `session_id`，`cdp_url`（WebSocket）和 `base_url`
- 使用 `cdp_url` 与 Playwright、Puppeteer 或任何 CDP 客户端

```bash
tinyfish browser session create --url "https://example.com"
# 返回：{ session_id, cdp_url: "wss://...", base_url: "https://..." }
```

---

## 一般说明

- **匹配用户的语言**：使用用户书写的任何语言进行响应。
- 所有命令支持 `--pretty` 用于人类可读输出。默认是 JSON。
- 在根命令上使用 `--debug` 或设置 `TINYFISH_DEBUG=1` 将 HTTP 请求记录到 stderr。
