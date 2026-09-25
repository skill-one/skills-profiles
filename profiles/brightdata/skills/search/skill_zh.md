# Bright Data — 搜索

在网络上查找信息。这个技能中有两个命令：

- **`bdata search`** — 经典的关键词SERP（Google/Bing/Yandex）。当你想知道“关键词X排名如何”时最佳。
- **`bdata discover`** — 带有可选页面内容的AI意图排序发现。当你想知道“与主题Y匹配意图Z的页面”时最佳。

对于来自已知平台（Amazon、LinkedIn、TikTok、…）的结构化数据，**请停止并使用`data-feeds`**。

## 设置网关（首先运行）

```bash
if ! command -v bdata >/dev/null 2>&1; then
    echo "bdata CLI未安装 — 请查看bright-data-best-practices/references/cli-setup.md"
elif ! bdata zones >/dev/null 2>&1; then
    echo "bdata未认证 — 运行：bdata login  (或：bdata login --device用于SSH)"
fi
```

如果任何检查失败，请停止并跳转到`skills/bright-data-best-practices/references/cli-setup.md`。

## 选择你的路径

| 情况 | 操作 |
|---|---|
| 单个关键词查询，仅SERP | `bdata search "<query>" --engine google --json --pretty` |
| 分页SERP（更多结果） | 循环`--page 0`、`--page 1`、…（0索引） |
| 多个查询 | 在查询文件上使用shell循环 |
| 意图排序/语义（非关键词） | `bdata discover "<query>" --intent "<intent>" --num-results 20` |
| 想要结果和页面正文，一次调用 | `bdata discover ... --include-content` |
| 新闻/图片/购物SERP | `bdata search "<query>" --type news` (或`images`、`shopping`) |
| 想要Amazon/LinkedIn/TikTok/…的结构化数据 | **停止 — 转交至`data-feeds`** |
| 有URL，想要内容 | **转交至`scrape`** |

## 操作

核心命令：

```bash
# Google SERP，结构化JSON
bdata search "site:example.com privacy policy" --engine google --json --pretty

# 本地化Bing（德国结果，德语语言）
bdata search "datenschutz" --engine bing --country de --language de --json

# 第二页结果（0索引）
bdata search "machine learning papers" --page 1 --json

# 移动SERP（排名与桌面不同）
bdata search "best coffee shops" --device mobile --json

# 新闻垂直
bdata search "openai" --type news --json --pretty

# 意图排序发现
bdata discover "enterprise LLM platforms" \
    --intent "vendor pages with pricing" \
    --num-results 15 --json

# 带有markdown页面内容的发现
bdata discover "webhook best practices" \
    --include-content --num-results 10 -o results.json

# 日期过滤发现
bdata discover "react server components" \
    --start-date 2025-01-01 --end-date 2025-12-31 --num-results 20
```

完整标志参考：[`references/flags.md`](references/flags.md)。

### `search` vs `discover` — 选择正确的命令

| 你想要 | 使用 |
|---|---|
| "Google对此确切关键词的排名" | `search` |
| "与这个含义/意图匹配的页面" | `discover` |
| "新闻/图片/购物垂直SERP" | `search --type <vertical>` |
| "一次调用返回结果+页面正文" | `discover --include-content` |
| "跨查询去重/语义排序" | `discover` |

## 验证网关

1. **JSON解析无误：** `jq . <output>`返回0。
2. **结果数组非空** — 如果为空，查询确实没有结果；放宽查询并重新运行。不要在没有告知用户的情况下声称空结果成功。
3. **必需字段存在：**
   - `search`：结果位于`.organic[]`；每个结果都有`title` + `link`
   - `discover`：结果位于`.results[]`；每个结果都有`title` + `link`；如果`--include-content`，还有`content`
4. **对于`discover --include-content`：** `content`字段中无阻止页面签名（与scrape相同，不区分大小写）：
   - `Access Denied`
   - `Just a moment`
   - `Attention Required`
   - `Checking your browser`
   - `captcha`
   - `cf-browser-verification`
   - `cloudflare` *(总body小于2KB)*
5. **地理合理性：** 如果用户期望国家特定结果，检查顶级结果的TLD/语言。如果定位错误，使用显式的`--country`和`--language`重新运行。

## 信号旗

- 使用`search`从Amazon、LinkedIn、TikTok等获取内容，而`data-feeds`一次即可返回干净的 结构化数据。
- 盲目抓取每个SERP结果 — 首先过滤（域名白名单、标题中包含关键词、相关性启发式）。
- 混淆`search`（关键词）与`discover`（语义）。它们回答不同的问题。
- 在抓取之前不跨结果集去重URL的多查询。
- 假设SERP顺序是通用的 — 它由地理+设备个性化。始终显式设置`--country`和`--device`以实现可重复性。
- 使用`--page`作为结果计数 — 它是页面索引，不是限制。每页返回约10个结果。
- 假设SERP结果位于`.results[]` — 对于`bdata search`它们位于`.organic[]`。（Discover使用`.results[]`。）
- 在`discover`上硬编码`--num-results 100`而未意识到管道会一直轮询直到找到这么多结果；可能很慢。

## 参考

- [`references/flags.md`](references/flags.md) — `search`和`discover`的完整标志及使用说明。
- [`references/patterns.md`](references/patterns.md) — 多查询去重、SERP → 过滤 → 抓取管道、`search` vs `discover`决策、遗留`curl`回退、共享验证清单。
- [`references/examples.md`](references/examples.md) — (1)单个Google查询，(2)本地化Bing，(3)批量查询+去重成URL列表，(4)`discover --include-content`端到端。
