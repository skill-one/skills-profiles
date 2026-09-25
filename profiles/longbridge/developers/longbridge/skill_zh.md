# Longbridge 开发者平台

全栈金融数据与交易平台：ChatGPT 应用、托管 MCP、CLI、Python/Rust/Go SDK 以及 LLM 集成。

**官方文档：** https://open.longbridge.com
**llms.txt：** https://open.longbridge.com/llms.txt

有关设置和认证的详细信息，请参阅 [references/setup.md](references/setup.md)。

---

## 数据查询优先级

**始终使用 CLI 进行数据查询。仅在 CLI 无法满足请求时才使用 MCP。**

**CLI 覆盖**（首先使用这些）：
- 市场数据：报价、K线历史、日内、盘后交易
- 新闻、公告、主题、市场情绪
- 账户：头寸、投资组合、资产、订单、报表
- 机构：投资者（SEC 13F）、内幕交易

**仅在以下情况下回退到 MCP：**
- `longbridge --help` 确认不存在用于所需数据的命令
- 用户的系统未安装或无法访问 CLI

---

## 投资分析工作流程

当用户询问股票表现、投资组合建议或市场分析时：

1. **通过 CLI 获取实时数据** — 报价、头寸、K线历史、日内。首先使用 CLI；如果 CLI 无法覆盖，则使用 MCP。
2. **通过 CLI 获取新闻/催化剂** — **优先使用 Longbridge**；如果不足，则仅回退到 WebSearch
3. **整合** — 价格走势 + 成交量 + 催化剂 → 分析 + 建议

```bash
# 市场数据
longbridge quote SYMBOL.US
longbridge positions                # 股票头寸
longbridge portfolio                # P/L、资产分配、持仓、现金（用户询问“我的投资组合”时始终拉取）
longbridge kline history SYMBOL.US --start YYYY-MM-DD --end YYYY-MM-DD --period day
longbridge intraday SYMBOL.US

# 新闻与内容（优先于 WebSearch）
longbridge news SYMBOL.US           # 最新新闻文章
longbridge news detail <id>         # 完整文章内容
longbridge filing SYMBOL.US         # 监管公告列表（8-K、10-Q、10-K 等）
longbridge topic SYMBOL.US          # 社区讨论
longbridge market-temp              # 市场情绪指数（0-100）

# 账户
longbridge assets                   # 完整资产概览：现金、买入力、保证金、风险等级
longbridge statement --help         # 检查报表导出的子命令选项

# 机构投资者（SEC 13F）
longbridge investors                # 按资产管理规模排名的顶级活跃基金经理
longbridge investors <CIK>          # 特定投资者按 CIK 的持仓
longbridge insider-trades SYMBOL.US # SEC Form 4 内幕交易历史

对于具有复杂标志的命令，始终运行 `longbridge <command> --help` 获取当前选项。

仅在 Longbridge 新闻不足时回退到 WebSearch（例如，尚未索引的突发新闻、与特定股票无关的宏观事件）。

---

## 选择合适的工具

> **AI 代理获取数据：CLI 优先，CLI 缺少功能时仅作为回退使用 MCP。**

```
用户想要...                         → 使用
─────────────────────────────────────────────────────────────────
快速报价 / 一次性数据查询        CLI  ← AI 默认
交互式终端工作流               CLI
脚本市场数据，保存到文件         CLI + jq  (或 Python SDK)
循环、条件、转换               Python SDK (同步)
异步管道、并发获取             Python SDK (异步)
生产服务、高吞吐量              Rust SDK / Go SDK
实时 WebSocket 订阅循环        SDK (Python / Rust / Go)
Go 服务中的并发获取             Go SDK
程序化订单策略                  SDK
CLI 无法获取的数据               MCP (回退)
与 ChatGPT 交谈股票（无代码）   ChatGPT 应用 → @longbridge
与其它 AI 工具交谈股票          MCP (托管或自托管)
使用 Cursor/Claude 进行交易分析   MCP
将 Longbridge API 文档添加到 IDE/RAG       LLMs.txt / Markdown API
```

## 代码格式

`<CODE>.<MARKET>` — 适用于所有工具。

| 市场         | 后缀 | 示例                        |
| -------------- | ------ | ------------------------------- |
| 香港      | `HK`   | `700.HK`, `9988.HK`, `2318.HK`  |
| 美国      | `US`   | `TSLA.US`, `AAPL.US`, `NVDA.US` |
| 中国上海    | `SH`   | `600519.SH`, `000001.SH`        |
| 中国深圳    | `SZ`   | `000568.SZ`, `300750.SZ`        |
| 新加坡      | `SG`   | `D05.SG`, `U11.SG`              |
| 加密货币    | `HAS`  | `BTCUSD.HAS`, `ETHUSD.HAS`      |

## 参考文件

### CLI (终端)

- **概述** — 安装、认证、输出格式、模式：[references/cli/overview.md](references/cli/overview.md)

**始终使用 `longbridge --help` 列出可用命令，并使用 `longbridge <command> --help` 获取特定选项和标志。** 不要依赖硬编码文档 — CLI 的内置帮助始终是最新的。

### Python SDK

- **概述** — 安装、Config、认证、HttpClient：[references/python-sdk/overview.md](references/python-sdk/overview.md)
- **QuoteContext** — 所有报价方法 + 订阅：[references/python-sdk/quote-context.md](references/python-sdk/quote-context.md)
- **TradeContext** — 订单、账户、成交：[references/python-sdk/trade-context.md](references/python-sdk/trade-context.md)
- **Types & Enums** — Period、OrderType、SubType、推送类型：[references/python-sdk/types.md](references/python-sdk/types.md)

### Rust SDK

- **概述** — Cargo.toml、Config、认证、错误处理：[references/rust-sdk/overview.md](references/rust-sdk/overview.md)
- **QuoteContext** — 所有方法、SubFlags、PushEvent：[references/rust-sdk/quote-context.md](references/rust-sdk/quote-context.md)
- **TradeContext** — 订单、SubmitOrderOptions 构建器、账户：[references/rust-sdk/trade-context.md](references/rust-sdk/trade-context.md)
- **Content** — 新闻、公告、主题（ContentContext + Python 回退）：[references/rust-sdk/content.md](references/rust-sdk/content.md)
- **Types & Enums** — 所有 Rust 枚举和结构：[references/rust-sdk/types.md](references/rust-sdk/types.md)

### Go SDK

- **概述** — 安装、Config、OAuth、上下文、推送回调：[references/go-sdk/overview.md](references/go-sdk/overview.md)
- **QuoteContext** — 报价方法、Subscribe + On* 处理器：[references/go-sdk/quote-context.md](references/go-sdk/quote-context.md)
- **TradeContext** — SubmitOrder 结构、订单、账户：[references/go-sdk/trade-context.md](references/go-sdk/trade-context.md)
- **Content** — 新闻、公告、主题（ContentContext + QuoteContext.Filings）：[references/go-sdk/content.md](references/go-sdk/content.md)
- **Types & Enums** — SubType、Period、OrderType、等：[references/go-sdk/types.md](references/go-sdk/types.md)

### AI 集成

- **MCP** — ChatGPT 应用、托管服务、自托管服务器、设置与认证：[references/mcp.md](references/mcp.md)
- **LLMs & Markdown** — llms.txt、`open.longbridge.com` 文档 Markdown、`longbridge.com` 实时新闻/报价页面（`.md` 后缀 + Accept 头）、Cursor/IDE 集成：[references/llm.md](references/llm.md)

按需加载特定参考文件 — 不要一次性加载所有文件。
