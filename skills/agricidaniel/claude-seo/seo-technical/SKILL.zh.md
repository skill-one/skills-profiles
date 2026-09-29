---
name: seo-technical
description: 对技术SEO进行审计，涵盖可爬取性、可索引性、安全性、URL、移动端、核心网页指标、渲染、结构化数据以及IndexNow。排除内容策略和反向链接。
---

# 技术SEO审计

## 类别

### 1. 可抓取性
- robots.txt：存在，有效，不阻止重要资源
- XML站点地图：运行 `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run sitemap_discovery.py <url> --json"`；需要在`found`中有一个有效条目，并将过时的或不安全的robots.txt声明与工作备用位置分开报告
- Noindex标签：有意为之与意外为之
- 抓取深度：重要页面在主页的3次点击范围内
- JavaScript渲染：检查关键内容是否需要JS执行（第8节中的方法）
- 抓取预算：对于大型网站（>10k页），效率很重要
- Googlebot **抓取限制**：Googlebot抓取前**2MB的HTML**和前**64MB的PDF**（未压缩；15MB是更广泛的爬虫基础设施默认值）。长期存在，不是2026年的变化，但内联base64图像、过大的内联CSS/JS或臃肿的导航可能会将关键内容/JSON-LD推过上限并使其出索引。将关键内容+结构化数据保持在第一个2MB内。
- 抓取速率**自动调整**（在5xx/慢响应时回退）；没有**手动抓取速率控制**（2024年1月移除了传统的搜索控制台设置）。通过站点地图、服务器响应性和robots控制来影响抓取。
- Google的规范抓取/robots参考已移动到**developers.google.com/crawling**（迁移于2025-11-20）；IP范围文件已移至`/crawling/ipranges/`，`googlebot.json`已重命名为`common-crawlers.json`。
- AMP没有单独的排名优势。自2026-07-01起，Google搜索直接将用户发送到发布商托管的AMP URL，因此不建议使用AMP缓存、AMP查看器或签名交换维护。审计AMP与其他页面一样的内容、行动一致性要求和质量要求。

#### AI爬虫管理

自2025-2026年起，AI公司积极抓取网络以训练模型并支持AI搜索。通过robots.txt管理这些爬虫是关键技术SEO考虑因素。

**已知AI爬虫**（权威表格，每个爬虫的robots.txt行为在`seo-geo`中）：

| 爬虫 | 公司 | robots.txt标记 | 目的 |
|---------|---------|-----------------|---------|
| GPTBot | OpenAI | `GPTBot` | 模型训练（不是ChatGPT搜索） |
| OAI-SearchBot | OpenAI | `OAI-SearchBot` | ChatGPT搜索的可引用性 |
| ChatGPT-User | OpenAI | `ChatGPT-User` | 实时浏览（用户触发） |
| ClaudeBot | Anthropic | `ClaudeBot` | 模型训练（不是Claude搜索的可引用性） |
| Claude-SearchBot | Anthropic | `Claude-SearchBot` | Claude搜索结果的可引用性 |
| PerplexityBot | Perplexity | `PerplexityBot` | Perplexity搜索索引（不是模型训练） |
| Bytespider | ByteDance | `Bytespider` | 模型训练 |
| Google-Extended | Google | `Google-Extended` | Gemini训练（不是搜索） |
| Applebot-Extended | Apple | `Applebot-Extended` | Apple智能训练选择退出（不是Siri/Spotlight/Safari） |
| CCBot | Common Crawl | `CCBot` | 开放数据集 |

**主要区别**：
- 阻止`Google-Extended`会阻止Gemini训练使用，但**不会**影响Google搜索索引或AI概述（那些使用`Googlebot`）
- 阻止`GPTBot`会阻止OpenAI训练，但**不会**影响ChatGPT搜索的可引用性，这由`OAI-SearchBot`管理，也不是用户触发的浏览（`ChatGPT-User`）。检查`OAI-SearchBot`是否有任何可引用性声明；`GPTBot`状态仅是关于训练使用的证据
- 阻止`ClaudeBot`会阻止Anthropic模型训练，但**不会**影响Claude自身搜索功能中的可引用性，这由`Claude-SearchBot`管理（根据Anthropic的爬虫支持文章）。检查`Claude-SearchBot`是否有任何Claude搜索可引用性声明；`ClaudeBot`状态仅是关于训练使用的证据
- 阻止`Applebot-Extended`会选择退出Apple智能/生成模型训练使用，但**不会**影响通过Siri、Spotlight或Safari的发现，这些遵循`Applebot`（根据Apple的支持文章）；`Applebot-Extended`本身不爬取

**示例，选择性地AI爬虫阻止**：
```
# 允许搜索索引，阻止AI训练爬虫
User-agent: GPTBot
Disallow: /

User-agent: Google-Extended
Disallow: /

User-agent: Bytespider
Disallow: /

# 允许所有其他爬虫（包括用于搜索的Googlebot）
User-agent: *
Allow: /
```

**建议**：在阻止之前考虑您的AI可见性策略：阻止AI搜索爬虫会从该引擎的答案中删除您的网站。不要承诺允许一个带来的流量。参考`seo-geo`技能以获取完整的AI爬虫/抓取器分类。

> **Google的用户触发的抓取器通常忽略robots.txt规则**（其他供应商不同：Anthropic的Claude-User尊重它）。Google现在记录**Google-Agent**（用户触发的代理浏览）加上**Google-GeminiNotebook**（以前是Google-NotebookLM）和**Google Messages**作为*用户触发的*抓取器，这些**不能通过robots.txt阻止**。使用服务器端访问控制。相比之下，`Google-Extended`和`Google-CloudVertexBot`遵守robots.txt。新兴的：**Web Bot Auth**（RFC 9421）允许爬虫通过`Signature-Agent`标头+密钥目录`agent.bot.goog`进行加密认证（Google-Agent使用）；反向DNS验证仍然是备用方案。

### 2. 可索引性
- 规范标签：自我引用，与noindex无冲突
- 重复内容：近似重复、参数URL、www与非www
- 规范化修复可能需要时间：Google可能会在重新评估它们时保留更正后的页面在重复集群中**长达两周**。不要将修复后立即不变的规范解释为修复失败。
- 薄内容：每类低于最低字数的页面
- 分页：可抓取的`<a href>`链接到每个页面（Google不再使用rel=next/prev；它在2019年宣布了这一点）；给每个页面一个自我引用的规范；加载更多和无限滚动需要它们后面的分页URL
- Hreflang：针对多语言/多区域网站的正确设置
- 索引膨胀：不必要的页面消耗抓取预算

### 3. 安全性
- HTTPS：强制执行，有效的SSL证书，无混合内容
- 安全标头：
  - 内容安全策略（CSP）
  - 严格传输安全（HSTS）
  - X-Frame-Options
  - X-Content-Type-Options
  - Referrer-Policy
- HSTS预加载：检查高安全网站是否包含预加载列表
- **后退按钮劫持**（垃圾邮件政策违规，恶意行为）：标记通过`history.pushState`/`replaceState`击败后退按钮的页面（包括第三方广告/库平台注入的脚本）。2026-04-13添加到Google的垃圾邮件政策；**自2026-06-15起执行**（手动操作+自动降级）：视为关键。

### 4. URL结构
- 干净URL：描述性，连字符，内容无查询参数
- 层次结构：反映网站架构的逻辑文件夹结构
- 重定向：无链（最多1跳），301用于永久移动
- URL长度：标记>100个字符
- 尾随斜杠：一致使用

### 5. 移动优化与页面体验
- 响应式设计：视口元标签，响应式CSS
- 触摸目标：WCAG 2.2 AA要求至少24x24 CSS px；48x48px带间距是舒适的指南（不是Google要求）
- 字体大小：可读文本无需缩放（16px基础是常见做法，不是Google规则）
- 无水平滚动
- 移动优先索引：Googlebot Smartphone是主要爬虫（于2024年完成推广）。一个移动版本**不是严格必需的**（Google表示“非常强烈推荐”），不在移动设备上工作的网站仍然可以索引，但真正的风险是**内容/一致性损失**，而不是硬性排除。
- **移动/桌面内容一致性**（最高价值的移动检查）：等效主要内容，匹配robots元标签，匹配标题/描述，等效结构化数据，可抓取资源；避免需要用户交互才能加载的主要内容。
- **侵入性插屏/广告密度**：标记全页插屏、独立的同意重定向页面、持续阻塞对话框和过度/分散的广告密度（命名页面体验方面）。可接受的：小横幅，标准CMS/法律对话框。
- **“阅读更多”深度链接**：在加载时立即显示关键内容（不在标签/手风琴后面），不要在加载时劫持滚动，并保留URL哈希片段，隐藏在可展开部分后面的内容不太可能符合资格。

> **页面体验是指导，不是单一排名系统。** 只有**核心网页性能**直接输入排名；**HTTPS**是一个已确认但轻量级的信号（Google在2014年宣布时称其为非常轻量级）。即使页面体验不佳，相关性仍然可以获胜，因此不要过度加权安全标头。注意：**页面体验报告已从搜索控制台移除**（通过核心网页性能+HTTPS报告进行监控）。

### 6. 核心网页性能
- **LCP**（最大内容绘制）：目标<=2.5秒
- **INP**（交互到下一次绘制）：目标<=200毫秒
  - INP于2024年3月12日取代了FID。FID于2024年9月9日从Chrome的字段数据工具（CrUX API、PageSpeed Insights）中移除（Lighthouse是一个实验室工具，从未报告过FID）。**在任何地方不要引用FID**。
- **CLS**（累积布局偏移）：目标<=0.1
- 评估使用真实用户数据的75分位数
- 如果可用，使用PageSpeed Insights API或CrUX数据

### 7. 结构化数据
- 检测：JSON-LD（首选），Microdata，RDFa
- 验证Google支持的类型
- 参考seo-schema技能进行完整分析

### 8. JavaScript渲染
- 方法：`"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run agentic_check.py <url> --json`报告原始HTML中的可见单词（`server-rendered`）；当Chromium可用时，与`render_page.py <url> --mode always --json`比较。如果没有Chromium，报告原始HTML结果，并说明未比较渲染内容。
- 检查初始HTML中可见的内容与是否需要JS
- 识别客户端渲染（CSR）与服务器端渲染（SSR）
- 标记可能引起索引问题的SPA框架（React、Vue、Angular）
- 如果检测到动态渲染，将其标记为技术债务而不是有效设置。Google将其记录为“一个变通方法，不是一个推荐解决方案”，因为增加了复杂性和资源成本。
  参考https://developers.google.com/search/docs/crawling-indexing/javascript/dynamic-rendering

**推荐渲染策略**：

| 策略 | 用例 |
|----------|----------|
| **SSR** | 公共SEO内容，动态页面 |
| **SSG** | 静态内容，博客，文档 |
| **CSR** | 仅认证/登录后内容 |

**首选框架**：Next.js，Astro，React Router v7（Remix），SvelteKit

#### JavaScript SEO：规范与索引指导（2025年12月）

Google在2025年12月更新了其JavaScript SEO文档，并提供了关键澄清：

1. **规范冲突**：如果原始HTML中的规范标签与JavaScript注入的标签不同，Google可能会使用**任何一个**。确保服务器渲染的HTML和JS渲染输出之间的规范标签完全相同。
2. **noindex与JavaScript**：如果原始HTML包含`<meta name="robots" content="noindex">`但JavaScript将其移除，Google**可能**仍然会从原始HTML中保留noindex。在初始HTML响应中提供正确的robots指令。
3. **非200状态代码**：Google**不会**在返回非200 HTTP状态代码的页面上渲染JavaScript。在错误页面上通过JS注入的任何内容或元标签对Googlebot都是不可见的。
4. **JavaScript中的结构化数据**：通过JS注入的产品、文章和其他结构化数据可能会面临延迟处理。对于时间敏感的结构化数据（尤其是电子商务产品标记），请将其包含在初始服务器渲染的HTML中。

**最佳实践**：在初始服务器渲染的HTML中提供关键SEO元素（规范、meta robots、结构化数据、标题、meta描述），而不是依赖JavaScript注入。

### 9. IndexNow协议
- 检查网站是否支持IndexNow用于Bing、Yandex、Naver
- 由除Google以外的搜索引擎支持
- 建议在非Google引擎上实施以实现更快的索引

## Agent-Friendly Pages & Agentic Browsing

Agent准备状态有自己的子技能：`/seo agentic <url>`（`seo-agentic`）。
它拥有Lighthouse的**Agent Browsing**类别（一个分数，X of N，不是0-100分），用于代理的可访问性树、AI代理访问策略、llms.txt、Markdown交付、ai-catalog.json、`/.well-known`发现文件和WebMCP。在技术审计期间，仅记录这两个信号，并指向`seo-agentic`以获取其余内容：

- JS渲染：主要内容在原始HTML中缺失也会隐藏在不会运行JavaScript的代理中。
- 5xx robots.txt，合规爬虫将其读取为“禁止所有内容”。

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run agent_ux_check.py https://example.com --json
```

上述Agent-UX 0-100分数是一个本地启发式算法。将其与Lighthouse分数区分开来，并将其发现作为机会而不是失败呈现。失败的Lighthouse `agent-accessibility-tree`审计不同：`seo-agentic`将其评级为P0，因为它是由Google自己测量的检查。

## 输出

### 技术分数：XX/100

仅测量已评估的内容。每个类别的分数是该类别检查中通过的比例，根据严重性调整；您无法测量的类别报告为“未测量”，永远不会给出数字。显示每个分数背后的检查。

### 类别细分
| 类别 | 状态 | 分数 |
|----------|--------|-------|
| 可抓取性 | 通过/警告/失败 | XX/100 |
| 可索引性 | 通过/警告/失败 | XX/100 |
| 安全性 | 通过/警告/失败 | XX/100 |
| URL结构 | 通过/警告/失败 | XX/100 |
| 移动 | 通过/警告/失败 | XX/100 |
| 核心网页性能 | 通过/警告/失败 | XX/100 |
| 结构化数据 | 通过/警告/失败 | XX/100 |
| JS渲染 | 通过/警告/失败 | XX/100 |
| IndexNow | 通过/警告/失败 | XX/100 |

### 紧急问题（立即修复）
### 高优先级（一周内修复）
### 中优先级（一个月内修复）
### 低优先级（待办事项）

## DataForSEO集成（可选）

如果DataForSEO MCP工具可用，请使用`on_page_instant_pages`进行真实页面分析（状态代码、页面时间、断链、页面检查），`on_page_lighthouse`进行Lighthouse审计（性能、可访问性、SEO分数），以及`domain_analytics_technologies_domain_technologies`进行技术堆栈检测。

## Google API集成（可选）

如果配置了Google API凭证，请使用`"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run pagespeed_check.py <url> --json`进行真实PSI + CrUX字段数据（取代仅实验室的CWV估计），`"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run crux_history.py <url> --form-factor PHONE --json`进行25周CWV趋势（使用PHONE：所有设备视图可能会隐藏移动失败），以及`"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run gsc_inspect.py <url> --json`进行每个URL的真实索引状态。

## 审计本地或私有主机

`url_safety`默认拒绝回环和私有地址，因此`http://localhost:3000`和Tailscale上的预发布主机会失败，显示“阻止主机名”或“阻止IP字面量”。此默认值是故意的：这些脚本遵循它们抓取页面上的URL。

要审计预发布主机，操作员在`CLAUDE_SEO_LOCAL_TARGETS`中命名它，这是一个由`host`或`host:port`条目组成的逗号分隔列表：

```bash
CLAUDE_SEO_LOCAL_TARGETS="localhost:3000,127.0.0.1:8080,100.101.102.103" \
  "${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run fetch_page.py http://localhost:3000/
```

它做什么和不做什么：

| 行为 | 允许列表中的主机 |
|-------|------------------|
| 首先覆盖原始 HTTP 的顶层 URL | 允许 |
| 从该 URL 到重定向目标 | 拒绝 |
| 渲染页面获取的子资源 | 拒绝 |
| Playwright 渲染 (`--render`, 截图) | 拒绝；使用原始 HTTP 路径 |
| 未在变量中命名的主机 | 拒绝 |
| 云元数据端点，即使列出 | 拒绝 |

`host:port` 仅匹配该端口；裸 `host` 匹配任何端口。变量未设置时策略不变。切勿建议为用户无法控制的主机设置它。参见 SECURITY.md。

## 错误处理

| 场景 | 操作 |
|------|------|
| URL 不可达 | 报告连接错误并附带状态码。建议验证 URL、检查 DNS 解析并确认网站是否公开可访问。 |
| 未找到 robots.txt | 注意在根域名下未检测到 robots.txt。建议创建带有适当指令的 robots.txt。继续对剩余类别进行审计。 |
| 未配置 HTTPS | 标记为严重问题。报告 HTTP 是否未重定向、是否存在混合内容或 SSL 证书是否缺失/过期。 |
| 核心网络指标数据不可用 | 注意 CrUX 数据不可用（低流量网站常见）。建议使用 Lighthouse 实验室数据作为代理，并建议在重新测试前增加流量。 |
