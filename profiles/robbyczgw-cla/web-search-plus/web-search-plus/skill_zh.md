# Web Search Plus

**停止选择搜索服务提供商。让技能为您处理。**

此技能现在连接您到 **11 个搜索服务提供商**，并添加了一个用于从 URL 提取内容的辅助提取流程。广泛网络查询？→ Brave 或 Serper。研究问题？→ Tavily 或 Exa。需要引文和依据？→ Linkup。需要可抓取的内容？→ Firecrawl。注重隐私？→ SearXNG。需要低成本的 Google SERP 并使用预付费积分？→ SerpBase（显式/仅回退）。需要一个独立索引作为最后的回退方案（即使无密钥）？→ Keenable。

此技能是 **仅源**：排名链接和提取的页面文本，不是模型生成的答案。4.0.0 中移除了 Perplexity/Kilo 答案合成。原生 OpenClaw 插件是 `web-search-plus-plugin-v2`。

---

## 🔐 数据处理与隐私

**在用敏感查询搜索前请阅读此内容。**

- **搜索查询和提取 URL 会发送给第三方提供商。** 每次搜索都会将您的查询文本传输给所选配置的提供商（Serper、Brave、Tavily、Linkup、Querit、Exa、Firecrawl、SerpBase、Keenable、You.com 或您的 SearXNG 实例）。每次提取都会将目标 URL 传输给所选提取提供商（Tavily、Exa、Linkup、Firecrawl、You.com、Keenable、Serper），其基础设施随后会获取页面。每个提供商自己的隐私政策和应用保留规则适用。
- **对于敏感工作，请显式选择提供商** (`--provider <name>`) 而不是依赖自动路由，以便您控制确切哪个第三方接收查询。自托管 SearXNG 会将查询保留在您控制的基础设施上。
- **不要提交内部或私有 URL 进行提取。** 您提取的 URL 会转发到外部服务。该技能还会默认阻止私有/回环/链路本地目标以及云元数据端点（见下文安全部分）。
- **本地缓存默认开启。** 查询、结果、提供商失败历史记录以及提供商性能样本（延迟/结果数/错误，用于自适应路由）会持久化到缓存目录（默认为 `.cache`，`WSP_CACHE_DIR` 可重新定位），包括 `provider_health.json`（包含提供商错误消息）和 `provider_stats.json`。缓存文件以仅所有者权限写入（目录 `0700`，文件 `0600`）。
  - 一次性绕过：`--no-cache`
  - 全局禁用：`WSP_DISABLE_CACHE=1`
  - 清除：`python3 scripts/search.py --clear-cache`（使用 `--cache-stats` 查看缓存）
- **API 密钥永远不会被技能记录或持久化**；错误在到达缓存或 stderr 之前会被清理。

---

## 🎯 触发器

为了避免在日常请求上自动激活，清单仅注册了范围狭小的触发短语：

- `web search plus`
- `wsp search`
- `search the web for`
- `multi-provider web search`
- `extract url content`
- `extract content from url`

像“search”、“find”、“look up”或“research”这样的通用词语**故意不会**触发此技能。

---

## ✨ 什么使其与众不同？

- **只需搜索** — 无需考虑使用哪个提供商
- **智能路由** — 查询分析自动选择最佳提供商
- **11 个提供商，1 个界面** — 汇集了通用网络、研究、语义发现、注重隐私、预付费积分和可提取内容提供商
- **URL 提取包含** — 使用 7 个提供商（Tavily 优先）的回退功能提取 markdown/HTML 内容
- **研究模式** — 一次调用即可实现并发多提供商搜索 + 去重 + 顶级来源提取
- **规范来源重新排序** — 官方/主要来源在发布/文档/政策/财务/安全查询中优于镜像域
- **仅需 1 个凭证即可使用** — 可从任何单个提供商开始，之后添加更多
- **提供免费/自托管选项** — SearXNG 可在 0 API 成本下运行

---

## 🚀 快速入门

```bash
# 交互式设置（推荐首次运行）
python3 scripts/setup.py

# 或手动
cp .env.example .env
python3 scripts/search.py -q "latest OpenClaw release"
python3 scripts/extract.py --url https://example.com
```

向导会解释提供商、收集密钥并设置默认值。

---

## 🔑 提供商

### 搜索提供商

- **Serper** — 购物、价格、本地和通用 Google 风格结果；快速通用回退
- **Brave** — 独立网络索引和通用当前网络查询；非 Google 的强大补充
- **Tavily** — 研究、解释和合成；强大的研究路由
- **Querit** — 多语言和国际更新；适合跨语言时效性
- **Linkup** — 基于来源/引文密集型搜索；证据优先查询
- **Exa** — 语义发现和相似站点搜索，附带来源 URL
- **Firecrawl** — 带可抓取元数据的搜索；也是强大的提取提供商
- **You.com** — 当前网络 / RAG 友好片段；也支持提取
- **SearXNG** — 私有/自托管搜索；无需 API 密钥，只需实例 URL
- **SerpBase** — 低成本 Google SERP 并使用预付费积分；显式/仅回退（通过 `--provider serpbase` 或添加到 `config.json` 中的 `provider_priority` 进行选择）
- **Keenable** — 独立网络索引；通过 `KEENABLE_API_KEY` 或无密钥对 **选择加入** 的共享公共层级（`WSP_KEENABLE_ALLOW_PUBLIC=1`，~1000 请求/小时，无 SLA，结果元数据中包含警告）。最低自动路由优先级 — 永远不会取代配置的带密钥提供商

### 提取提供商

`scripts/extract.py` 会自动回退到（Tavily 优先以确保可靠性）：

1. **Tavily**
2. **Exa**
3. **Linkup**
4. **Firecrawl**
5. **You.com**
6. **Keenable**
7. **Serper**（通过 `scrape.serper.dev` 的网页抓取器，优先 markdown）

---

## 🧠 路由概览

默认优先级（按设计排除 SerpBase — 仅选择加入）：

```text
tavily → linkup → querit → exa → firecrawl → brave → serper → you → searxng → keenable
```

路由还会应用 **自适应提供商性能记忆**：每次提供商调用都会将延迟/结果数/错误记录到滚动窗口（50 个样本，7 天新鲜度，持久化为 `provider_stats.json`），该窗口在 5 个新鲜样本后提供有界（±1.0）路由分数调整 — 足以打破平局并推动接近的调用，但永远不足以覆盖明确的查询类获胜者（`routing.adaptive_adjustments`）。

示例：

```bash
python3 scripts/search.py -q "维也纳今天的天气"
# 通用当前网络意图 → Brave 或 Serper

python3 scripts/search.py -q "寻找 AI 辅导结果的可靠来源"
# 引文/证据意图 → Linkup

python3 scripts/search.py -q "德国最新的 AI 政策更新"
# 多语言 + 时效性 → Querit 或 Tavily

python3 scripts/search.py -p exa --exa-depth deep -q "LLM 扩展规律研究"
python3 scripts/search.py -p firecrawl -q "YC 初创公司网络抓取"
python3 scripts/search.py -p serpbase -q "2026 最佳笔记本电脑"   # 显式 SerpBase
```

调试路由：

```bash
python3 scripts/search.py --explain-routing -q "您的查询"
```

以短横线开头的查询可以使用 `--query=-foo` 或 `-q -- "-foo"`。当 `-n` 被省略时，`defaults.max_results` 提供计数（回退 5）；计数被限制在 1–20。

`--time-range` 优先于 `--freshness`。Tavily 将日/周/月/年作为原生 `time_range` 发送；Exa 报告请求中发送的发布边界。

`--cache-ttl SECONDS` 设置搜索缓存生命周期，对实时/小时查询限制在 60 秒，对最新/日查询限制在 300 秒，对周过滤限制在 1800 秒。缓存结果包括 `cache_age_seconds`。`--no-cache` 绕过搜索结果缓存。设置 `WSP_HTTP_KEEPALIVE=0` 以禁用连接重用；通过代理的请求使用标准传输。

### 新鲜度、新闻垂直 & 地域

```bash
python3 scripts/search.py -q "AI 管理" --freshness week
# 具有原生日期过滤器的提供商接收映射值；其他提供商运行正常搜索并报告 `freshness.applied=false` 在元数据中

python3 scripts/search.py -p serper --type news -q "量子计算"
# Serper 原生提供 Google 新闻垂直（日期/来源/缩略图）；其他提供商报告 `search_type.applied=false`

python3 scripts/search.py -q "beste Kaffeehäuser Wien"
# 显式位置提示（经过编辑的城市/国家表）设置国家（at）；设置 `locale.language="auto"`（或 `WSP_LOCALE_LANGUAGE=auto`）以保守推断查询语言。解析值 + 来源出现在 `metadata.locale` 中。未配置行为保持 us/en 精确。
```

### 结果质量过滤器

来自已知 Stack Overflow/GitHub/文档镜像域的结果会被移除（严格精确域/真实子域匹配，无类似域的误报）；通过 `quality.blocked_domains` 扩展或通过 `quality.allowed_domains` 在 `config.json` 中救援。域多样性重新排序将单个域限制在 2 个头部插槽（溢出降级，不丢弃）。显式域意图（`site:` 查询，`--include-domains`）绕过两者。移除和降级在 `metadata.result_filter` 中报告。

---

## 📖 提取示例

```bash
python3 scripts/extract.py --url https://example.com
python3 scripts/extract.py --url https://docs.linkup.so --provider linkup
python3 scripts/extract.py --url https://example.com --url https://example.org --include-images
python3 scripts/extract.py --url https://example.com --format html --include-raw-html
python3 scripts/extract.py --url https://example.com --provider serper   # Serper 网页抓取器
python3 scripts/extract.py --url https://example.com --extract-char-limit 30000
```

过大的页面会返回头部/尾部窗口加上解释性页脚（默认内联预算 15,000 字符；`WSP_EXTRACT_CHAR_LIMIT` 或 `--extract-char-limit` 覆盖）。内联 base64 图像数据会被替换为 `[IMAGE: alt]` 占位符，在测量内容前防止数据 URI 令牌炸弹，同时保留正常的 `http(s)` 图像链接。

---

## 🔬 研究模式与质量报告

研究模式查询最多三个提供商 **并发**（墙钟成本 ≈ 最慢提供商，不是总和），在提供商间去重并具有确定性排序，然后提取顶级来源以用于依据：

```bash
python3 scripts/search.py --mode research -q "欧盟 AI 法案对基础模型的责任"
python3 scripts/search.py --mode research -q "..." --research-providers tavily linkup exa
python3 scripts/search.py --mode research -q "..." --research-extract-count 2 --research-time-budget 30
```

时间预算控制提供商的启动和是否运行提取；耗尽的步骤在 `routing.provider_errors` / `routing.extraction_error` 中报告，而不是导致调用失败。

质量报告添加透明的路由/结果诊断，包括 **权威信号** 用于规范来源路由类别（`canonical_domain_hits`、`demoted_domain_hits`、`canonical_top_result`）：

```bash
python3 scripts/search.py -q "官方 Anthropic Claude 发布说明" --quality-report
```

对于这些规范类别（官方供应商发布、官方文档、政策 PDF、财务/IR、安全公告），结果还会 **针对意图重新排序**：主要来源被提升，镜像/聚合域被降级（`metadata.intent_rerank` 显示了变化）。

---

## ⚙️ 配置说明

- `.env.example` 文档了支持的 env 变量
- `config.example.json` 包含提供商优先级和提供商特定默认值
- `config.json` 是您的本地运行时配置
- SearXNG 仍然支持显式 URL 配置和 docker 感知的自动检测
- SerpBase 默认为 **显式/仅回退**；要包含在自动路由中，请将 `"serpbase"` 添加到 `auto_routing.provider_priority` 在 `config.json` 中
- Keenable 在自动路由和提取回退中最后；显式启用无密钥使用，使用 `WSP_KEENABLE_ALLOW_PUBLIC=1` 或 `"keenable": {"allow_public": true}`
- 地域默认值：`"locale": {"country": "...", "language": "..."}` 在 `config.json` 中（或 `WSP_LOCALE_COUNTRY`/`WSP_LOCALE_LANGUAGE`）；`--country`/`--language` CLI 标志始终优先
- 速率限制：429 响应解析 `Retry-After`，最多重试一次（等待 ≤30 秒的等待时间得到尊重），并将提供商请求的等待时间输入冷却阶梯；30 分钟前的失败历史记录会衰减而不是无限期升级冷却；缺少密钥的配置错误永远不会触发冷却

---

## 🔒 安全

**URL SSRF 保护（提取、`--similar-url`）：**
- 仅接受 `http` / `https` URL
- 主机名解析并阻止，如果它们指向私有/回环/链路本地/保留范围（`10/8`、`127/8`、`169.254/16`、`172.16/12`、`192.168/16`、CGNAT `100.64/10`、`::1`、`fc00::/7`、`fe80::/10`、IPv4 映射的 IPv6、`0.0.0.0`）
- 云元数据端点（`169.254.169.254`、`metadata.google.internal`）始终被阻止
- 选择加入受信任的私有网络，使用 `--allow-private-urls` 或 `WSP_ALLOW_PRIVATE_URLS=1`（默认关闭；元数据端点保持阻止）

**SearXNG SSRF 保护：**
- 强制 `http` / `https` 仅
- 阻止常见的云元数据端点
- 除非 `SEARXNG_ALLOW_PRIVATE=1`，否则阻止私有/内部 IP 解析
- 仅使用操作员控制的配置/环境，仅用于实例 URL

**本地数据：**
- 缓存目录创建 `0700`；缓存、提供商健康和提供商统计文件通过原子临时文件替换写入 `0600`
- API 密钥永远不会写入缓存或日志

**声明的权限**（见 `package.json → clawhub.permissions`）：
- 出站网络访问仅限于列出的提供商 API 主机（以及任何用户配置的 SearXNG 实例）
- 环境读取仅限于提供商 `*_API_KEY` 变量、`SEARXNG_*` 和 `WSP_*` 设置
- 文件系统写入仅限于缓存目录

---

## ✅ 验证

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/search.py --explain-routing -q "寻找气候变化影响的可靠来源"
python3 scripts/extract.py --url https://example.com --provider auto --compact
```
