# 技术SEO审计

## 类别

### 1. 可抓取性
- robots.txt：存在，有效，不阻塞重要资源
- XML站点地图：运行 `"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run sitemap_discovery.py <url> --json"`；需要在`found`中有一个有效条目，并单独报告过时的或不安全的robots.txt声明，与工作回退位置分开
- Noindex标签：有意为之与意外为之
- 抓取深度：重要页面在主页的3次点击范围内
- JavaScript渲染：检查是否需要JS执行的关键内容
- 抓取预算：对于大型网站（>10k页），效率很重要
- Googlebot **抓取限制**：Googlebot抓取前**2MB的HTML**和前**64MB的PDF**（未压缩；15MB是更广泛的爬虫基础设施默认值）。长期存在，不是2026年的变化，但内联base64图像、过大的内联CSS/JS或臃肿的导航可能会将关键内容/JSON-LD推过上限并使其出索引。将关键内容+结构化数据保持在第一个2MB内。
- 抓取速率**自动调整**（在5xx/慢响应时回退）；没有**手动抓取速率控制**（2024年1月移除了遗留的Search Console设置）。通过站点地图、服务器响应性和robots控制来影响抓取。
- Google的规范抓取/robots参考已迁移到**developers.google.com/crawling**（迁移于2025-11-20）；IP范围文件已移至`/crawling/ipranges/`，`googlebot.json`已重命名为`common-crawlers.json`。
- AMP没有单独的排名优势。自2026-07-01起，Google搜索直接将用户发送到发布商托管的AMP URL，因此不建议使用AMP缓存、AMP查看器或签名交换维护。审计AMP与其他页面相同的内容、操作一致性和质量要求。

#### AI爬虫管理

自2025-2026年起，AI公司积极抓取网络以训练模型并支持AI搜索。通过robots.txt管理这些爬虫是关键技术SEO考虑因素。

**已知的AI爬虫：**

| 爬虫 | 公司 | robots.txt标记 | 目的 |
|---------|---------|-----------------|---------|
| GPTBot | OpenAI | `GPTBot` | 模型训练（不是ChatGPT搜索） |
| OAI-SearchBot | OpenAI | `OAI-SearchBot` | ChatGPT搜索的可引用性 |
| ChatGPT-User | OpenAI | `ChatGPT-User` | 实时浏览（用户触发） |
| ClaudeBot | Anthropic | `ClaudeBot` | 模型训练（不是Claude搜索的可引用性） |
| Claude-SearchBot | Anthropic | `Claude-SearchBot` | Claude搜索结果的可引用性 |
| PerplexityBot | Perplexity | `PerplexityBot` | 搜索索引+训练 |
| Bytespider | ByteDance | `Bytespider` | 模型训练 |
| Google-Extended | Google | `Google-Extended` | Gemini训练（不是搜索） |
| Applebot-Extended | Apple | `Applebot-Extended` | Apple Intelligence训练选择退出（不是Siri/Spotlight/Safari） |
| CCBot | Common Crawl | `CCBot` | 开放数据集 |

**主要区别：**
- 阻塞`Google-Extended`会阻止Gemini训练使用，但**不会**影响Google搜索索引或AI概览（那些使用`Googlebot`）
- 阻塞`GPTBot`会阻止OpenAI训练，但**不会**影响ChatGPT搜索的可引用性，可引用性由`OAI-SearchBot`管理，也不影响用户触发的浏览（`ChatGPT-User`）。检查`OAI-SearchBot`的任何可引用性声明；`GPTBot`状态仅是关于训练使用的证据
- 阻塞`ClaudeBot`会阻止Anthropic模型训练，但**不会**影响Claude自身搜索功能中的可引用性，可引用性由`Claude-SearchBot`管理（根据Anthropic的爬虫支持文章）。检查`Claude-SearchBot`的任何Claude搜索可引用性声明；`ClaudeBot`状态仅是关于训练使用的证据
- 阻塞`Applebot-Extended`会选择退出Apple Intelligence/生成模型训练使用，但**不会**影响通过Siri、Spotlight或Safari的发现，这些遵循`Applebot`（根据Apple的支持文章）；`Applebot-Extended`本身不爬取
- ~3-5%的网站现在使用AI特定的robots.txt规则

**示例，选择性AI爬虫阻塞：**
```
# 允许搜索索引，阻塞AI训练爬虫
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

**建议：** 在阻塞之前考虑您的AI可见性策略。被AI系统引用会提高品牌知名度并带来推荐流量。参考`seo-geo`技能以获取完整的AI爬虫/抓取器分类。

> **用户触发的抓取器按设计忽略robots.txt。** Google现在记录**Google-Agent**（Project Mariner，代理浏览）以及**Google-NotebookLM**和**Google Messages**作为*用户触发的*抓取器，这些**不能通过robots.txt阻塞**。使用服务器端访问控制。相比之下，`Google-Extended`和`Google-CloudVertexBot`遵守robots.txt。新兴：**Web Bot Auth**（RFC 9421）允许爬虫通过`Signature-Agent`标头+`agent.bot.goog`处的密钥目录进行加密身份验证（Google-Agent使用）；反向DNS验证仍然是回退。

### 2. 可索引性
- 规范标签：自我引用，与noindex无冲突
- 重复内容：近似重复，参数URL，www与非www
- 规范化修复可能需要时间：Google可能会在重新评估它们时保留更正后的页面在一个重复集群中**长达两周**。不要将修复后立即不变的规范解释为修复失败。
- 薄内容：每类低于最低字数的页面
- 分页：rel=next/prev或load-more模式
- Hreflang：多语言/多区域网站的正确设置
- 索引膨胀：消耗抓取预算的不必要页面

### 3. 安全性
- HTTPS：强制执行，有效的SSL证书，无混合内容
- 安全标头：
  - 内容安全策略（CSP）
  - 严格传输安全（HSTS）
  - X-Frame-Options
  - X-Content-Type-Options
  - Referrer-Policy
- HSTS预加载：检查高安全性网站是否包含在预加载列表中
- **后退按钮劫持**（垃圾邮件策略违规，恶意行为）：标记通过`history.pushState`/`replaceState`击败后退按钮的页面（包括第三方广告/库平台注入的脚本）。2026-04-13添加到Google的垃圾邮件策略中；**自2026-06-15开始执行**（手动操作+自动降级）：视为关键。

### 4. URL结构
- 干净URL：描述性，连字符，内容不使用查询参数
- 层次结构：反映网站架构的逻辑文件夹结构
- 重定向：无链（最多1跳），301用于永久移动
- URL长度：标记>100个字符
- 尾随斜杠：一致使用

### 5. 移动优化与页面体验
- 响应式设计：视口元标签，响应式CSS
- 触摸目标：最小48x48px，8px间距
- 字体大小：最小16px基础
- 无水平滚动
- 移动优先索引：Googlebot Smartphone是主要爬虫（于2024年完成推广）。需要一个移动版本是**不是严格要求的**（Google表示“非常强烈推荐”），不适用于移动设备的网站仍然可以被索引，但真正的风险是**内容/一致性损失**，而不是硬性排除。
- **移动/桌面内容一致性**（最高价值的移动检查）：等效主要内容，匹配robots元标签，匹配标题/描述，等效结构化数据，可抓取资源；避免需要用户交互才能加载的主要内容懒加载。
- **侵入性插屏/广告密度**：标记全页插屏，独立的同意重定向页面，持续阻塞对话框和过多的分散广告密度（命名页面体验方面）。可接受：小横幅，标准CMS/法律对话框。
- **“阅读更多”深度链接**：在加载时保持关键内容**立即可见**（不在标签/手风琴后面），不要在加载时劫持滚动，并保留URL哈希片段，隐藏在可展开部分后面的内容不太可能符合条件。

> **页面体验是指导，不是单一排名系统。** 只有**核心网页指标**直接影响排名；**HTTPS**是一个已确认但轻量级的信号（影响<~1%的查询）。即使页面体验较差，相关性仍然可以获胜，因此不要过度重视安全标头。注意：**页面体验报告**已从Search Console中移除（通过核心网页指标+HTTPS报告监控）。

### 6. 核心网页指标
- **LCP**（最大内容绘制）：目标<=2.5秒
- **INP**（交互到下一次绘制）：目标<=200毫秒
  - INP于2024年3月12日取代了FID。FID已于2024年9月9日从Chrome的字段数据工具（CrUX API，PageSpeed Insights）中移除（Lighthouse是一个实验室工具，从未报告过FID）。**任何地方不要引用FID。**
- **CLS**（累积布局偏移）：目标<=0.1
- 评估使用真实用户数据的第75个百分位数
- 如果MCP可用，使用PageSpeed Insights API或CrUX数据

### 7. 结构化数据
- 检测：JSON-LD（首选），Microdata，RDFa
- 与Google支持的类型进行验证
- 参考seo-schema技能进行完整分析

### 8. JavaScript渲染
- 检查初始HTML中可见的内容与是否需要JS
- 识别客户端渲染（CSR）与服务器端渲染（SSR）
- 标记可能引起索引问题的SPA框架（React，Vue，Angular）
- 如果检测到动态渲染，将其标记为技术债务而不是有效设置。Google将其记录为“一个变通方法，不是一个推荐解决方案”，因为增加了复杂性和资源成本。
  参考https://developers.google.com/search/docs/crawling-indexing/javascript/dynamic-rendering

**推荐渲染策略：**

| 策略 | 用例 |
|----------|----------|
| **SSR** | 公共SEO内容，动态页面 |
| **SSG** | 静态内容，博客，文档 |
| **CSR** | 仅认证/登录后内容 |

**首选框架：** Next.js，Astro，React Router v7（Remix），SvelteKit

#### JavaScript SEO：规范与索引指导（2025年12月）

Google于2025年12月更新了其JavaScript SEO文档，并提供了关键澄清：

1. **规范冲突：** 如果原始HTML中的规范标签与JavaScript注入的标签不同，Google可能会使用**任何一个**。确保服务器渲染的HTML和JS渲染的输出之间的规范标签完全相同。
2. **noindex与JavaScript：** 如果原始HTML包含`<meta name="robots" content="noindex">`，但JavaScript将其移除，Google**可能**仍然会从原始HTML中尊重noindex。在初始HTML响应中提供正确的robots指令。
3. **非200状态代码：** Google**不会**在返回非200 HTTP状态代码的页面上渲染JavaScript。任何在错误页面上通过JS注入的内容或元标签对Googlebot都是不可见的。
4. **JavaScript中的结构化数据：** 通过JS注入的产品、文章和其他结构化数据可能会面临延迟处理。对于时间敏感的结构化数据（尤其是电子商务产品标记），请将其包含在初始服务器渲染的HTML中。

**最佳实践：** 在初始服务器渲染的HTML中提供关键SEO元素（规范，meta robots，结构化数据，标题，meta描述），而不是依赖JavaScript注入。

### 9. IndexNow协议
- 检查网站是否支持IndexNow用于Bing、Yandex、Naver
- 由除Google以外的搜索引擎支持
- 建议在非Google引擎上实施以加快索引

## 代理友好页面与代理浏览

AI代理（不仅仅是AI摘要器）越来越多地通过三个渠道读取网站：截图上的视觉模型、原始HTML/DOM和**可访问性树**（最干净的信号）。审计标准：语义HTML（真实的`<button>`和`<a>`，不是`<div onclick>`），标签关联，交互目标尺寸，模板之间布局稳定性，`cursor: pointer`正确性，存在于`references/agent-friendly-pages.md`中。

Google现在提供Lighthouse的**代理浏览**类别（自Lighthouse 13.3.0起默认开启，Chrome 150+；桶：代理中心可访问性，CLS + llms.txt，三个WebMCP审计）。它报告**分数（X of N），而不是0-100分数**，将其与该技能自己的Agent-UX 0-100启发式区分开来。Lighthouse 13.4.1通过PSI API重新启用了该类别。它也通过Lighthouse CLI使用`--only-categories=agentic-browsing`，DevTools和PSI Web UI提供。参考`references/agent-friendly-pages.md`。

### 审计命令

```bash
# 使用Playwright渲染并捕获可访问性树，然后评分
"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run agent_ux_check.py https://example.com --json
```

扫描器输出Agent-UX分数（0-100）和分项问题：
- HTML发现：真实按钮/锚点，`<div onclick>`小部件，语义地标，没有`<label for>`的输入，没有ARIA标签的输入

可访问性树快照使用Chromium的`Accessibility.getFullAXTree` CDP命令通过Playwright捕获。要捕获树而不评分，使用
`"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run render_page.py <url> --a11y-tree --json`。

将发现作为**机会**而不是失败呈现；不要以低于100的Agent-UX分数来限制审计。WebMCP origin-trial/注册状态需要验证，并且没有WebMCP支持仍然是一个机会，而不是缺陷。

## 输出

### 技术分数：XX/100

### 类别细分
| 类别 | 状态 | 分数 |
|----------|--------|-------|
| 可抓取性 | 通过/警告/失败 | XX/100 |
| 可索引性 | 通过/警告/失败 | XX/100 |
| 安全性 | 通过/警告/失败 | XX/100 |
| URL结构 | 通过/警告/失败 | XX/100 |
| 移动 | 通过/警告/失败 | XX/100 |
| 核心网页指标 | 通过/警告/失败 | XX/100 |
| 结构化数据 | 通过/警告/失败 | XX/100 |
| JS渲染 | 通过/警告/失败 | XX/100 |
| IndexNow | 通过/警告/失败 | XX/100 |

### 紧急问题（立即修复）
### 高优先级（一周内修复）
### 中优先级（一个月内修复）
### 低优先级（待办事项）

## DataForSEO集成（可选）

如果DataForSEO MCP工具可用，使用`on_page_instant_pages`进行真实页面分析（状态代码，页面时间，断链，页面检查），`on_page_lighthouse`进行Lighthouse审计（性能，可访问性，SEO分数），以及`domain_analytics_technologies_domain_technologies`进行技术栈检测。

## Google API集成（可选）

如果配置了Google API凭证，使用`"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run pagespeed_check.py <url> --json`进行真实PSI + CrUX字段数据（取代仅实验室的CWV估计），`"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run crux_history.py <url> --json`进行25周CWV趋势，以及`"${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run gsc_inspect.py <url> --json`进行每个URL的真实索引状态。

## 本地或私有主机审计

`url_safety`默认拒绝回环和私有地址，因此`http://localhost:3000`和Tailscale上的预发布主机会失败，显示“Blocked hostname”或“Blocked IP literal”。此默认值是故意的：这些脚本遵循它们抓取的页面上的URL。

要审计预发布主机，操作员在`CLAUDE_SEO_LOCAL_TARGETS`中命名它，这是一个由`host`或`host:port`条目组成的逗号分隔列表：

```bash
CLAUDE_SEO_LOCAL_TARGETS="localhost:3000,127.0.0.1:8080,100.101.102.103" \
  "${CLAUDE_PLUGIN_ROOT}/scripts/claude-seo" run fetch_page.py http://localhost:3000/
```

它做什么和不做什么覆盖：

| 行为 | 允许的主机 |
|-----------|------------------|
| 首先，顶级URL通过原始HTTP | 允许 |
| 从该URL到达的重定向目标 | 拒绝 |
| 渲染的页面抓取的子资源 | 拒绝 |
| Playwright渲染（`--render`，截图） | 拒绝；使用原始HTTP路径 |
| 未在变量中命名的主机 | 拒绝 |
| 云元数据端点，即使列出时 | 拒绝 |

`host:port`仅匹配该端口；裸`host`匹配任何端口。变量未设置时策略不变。永远不要建议为用户不控制的托管设置它。参考SECURITY.md。

## 错误处理

| 场景 | 操作 |
|----------|--------|
| URL无法访问 | 报告连接错误和状态代码。建议验证URL，检查DNS解析，并确认网站公开可访问。 |
| 未找到robots.txt | 注意在根域名下未检测到robots.txt。建议创建一个带有适当指令的robots.txt。继续在剩余类别上审计。 |
| 未配置HTTPS | 标记为关键问题。报告HTTP是否未经重定向提供服务，是否存在混合内容，或SSL证书是否缺失/过期。 |
| 核心网页指标数据不可用 | 注意CrUX数据不可用（低流量网站常见）。建议使用Lighthouse实验室数据作为代理，并建议在重新测试前增加流量。 |
