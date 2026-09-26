**问题:** 通过环境的问题工具询问用户，绝不要以纯文本形式提问。一次只问一个问题，2-4个可点击选项，等待答案。如果环境没有问题工具，请以纯文本形式提问，并使用相同的选项，一次一个。

# 网站上线清单

为新网站发布前的审计和设置工作流程。对 Cloudflare DNS + Vercel 托管 + PostHog + 法律环境持意见。

## 交互风格（首先阅读）

这项技能是故意交互式的。与其假设，不如主动提问。用户会点击，而不是输入。

**在每次运行开始时始终提出以下问题**（一次一个）：

1. 网站类型：`doc-site` | `marketing/lead-gen` | `SaaS-app` | `training/paid-course` | `personal-portfolio`
2. 迁移：`greenfield-new-domain` | `migration-need-301-redirects` | `replacing-existing-on-same-domain`
3. 多语言：`single-locale` | `en` | `fr+en` | `other-multi`
4. PostHog 设置：`hogpost.samber.dev` | `set-up-new-proxy` | `skip-PostHog`
5. AI 抓取策略：`use-default-for-site-type` | `customize-per-bot` | `block-all`
6. 浏览器工具可用：`claude-chrome-extension` | `playwright` | `neither-skip-browser-checks`

**在各个阶段的所有决策点再次提问**，包括：

- 是否安装 Sentry / BetterStack / Crisp（取决于网站类型，明确提问）
- www 与 apex 算法偏好（大多数网站：apex；无论如何都要提问）
- 如果用户选择了 `customize-per-bot`，允许哪些 AI 机器人
- CSP 严格程度：`strict-default-src-none` | `balanced-allow-self` | `permissive-for-marketing`
- 是否完全跳过某个阶段（例如，如果非 FR 网站，则跳过阶段 3）

在任何决策点之前，如果没有明确用户输入，绝不要继续进行。没有检查点的详细清单不是目标。

**在安装任何 MCP 服务器或技能之前，必须获得明确的用户确认。** 在运行 `npx skills add`、`claude mcp add` 或任何等效安装命令之前，始终通过问题工具询问——即使技能选择工作流程建议精选子集。

## 如何使用此技能

1. 运行上述会话开始问题。
2. 按顺序引导用户完成第 1-10 个阶段。对于每个阶段：a. 列出项目，询问是否应跳过。b. 对于每个剩余项目，运行验证命令（见下文“验证工具”）。c. 报告通过/失败。失败时，询问用户是否要立即修复或稍后排队。
3. 以按阶段分组的状态报告结束，明确区分阻止项、建议修复和可选改进。

## 伴随技能

六个技能包对网站发布很有用。**绝对不要安装完整的多个技能包**。实际要安装的子集取决于用户确认的网站类型。

### 技能清单

| 技能 | 它涵盖的内容 | 通常适用于 |
| --- | --- | --- |
| `AgriciDaniel/claude-seo` | SEO + GEO + schema + hreflang + sitemaps 审计，并行子代理 | 所有网站类型 |
| `addyosmani/web-quality-skills` | Lighthouse, Core Web Vitals, 可访问性, 性能, 最佳实践 | 所有网站类型 |
| `trailofbits/skills` | 安全审计 (OWASP, headers, 依赖项) | 所有网站类型 |
| `aaron-he-zhu/seo-geo-claude-skills` | 20 个 SEO+GEO 技能，CORE-EEAT + CITE 框架，`/seo:` 符号命令 | 内容密集型网站, 竞争性细分市场 |
| `coreyhaines31/marketingskills` | ~30 个营销技能 (CRO, 文案写作, 广告, 弹窗, 电子邮件, 付费墙等) | `marketing/lead-gen`, `SaaS-app`, `training/paid-course` |
| `jonathimer/devmarketing-skills` | 33 个开发者营销技能 (角色, 文档作为营销, 技术教程等) | `doc-site`, `SaaS-app` for developers |

### 技能选择工作流程（在会话开始时运行）

在用户确认网站类型后，对于**与该网站类型相关的每个包**：

1. **列出可用子技能**: `npx skills add owner/repo --list`
2. **根据网站类型和此技能将执行的阶段，建议一个精选子集**。将每个阶段的需要与列表返回的特定子技能相匹配。
3. **确认用户**。如果建议列表中有超过 3 个项目，请使用多选。否则使用单选 (`install-as-proposed` | `let-me-modify` | `skip-this-pack`)。
4. **批量安装商定的子集**: `npx skills add owner/repo --skill A B C`

规则：

- 子技能名称存在于包中，而不是在 `SKILL.md` 中。始终查询 `--list` 以获取当前状态。包的内容会发生变化。
- 绝对不要在没有 `--skill` 的情况下运行 `npx skills add owner/repo`（那会安装所有内容）。
- 网站类型 → 包映射（要枚举哪些包，每个包的子技能仍然按工作流程选择）：
  - `doc-site`: claude-seo, web-quality-skills, trailofbits, seo-geo-claude-skills, devmarketing-skills
  - `marketing/lead-gen`: claude-seo, web-quality-skills, trailofbits, seo-geo-claude-skills, marketingskills
  - `SaaS-app`: 所有六个
  - `training/paid-course`: claude-seo, web-quality-skills, trailofbits, marketingskills
  - `personal-portfolio`: claude-seo, web-quality-skills, trailofbits, seo-geo-claude-skills（轻量级子集）
- 如果用户稍后请求需要尚未安装的子技能的某个阶段，请再次运行该工作流程以安装该单个子技能，而不是重新安装整个子集。

这避免了导入 80 多个用户不需要的技能，避免了子技能名称过时，避免了针对单个包版本的过度拟合。

在分配期间，不要重复此技能协调的工作。调用范围狭窄的专家（例如，“仅运行 URL X 的安全标题子审计”）。

## 阶段 0：发布准备就绪门

**在任何其他阶段之前运行此阶段。** 产品不会自我推广——但一个未准备好的产品不会推广。只有当你发布的东西值得发布时，发布机制才会奏效。

两种失败模式会从两端扼杀发布：

- **隐形模式** — 过晚发布。 “穿着华服的拖延症。” 你在私下里不断打磨，等待产品完美。它永远不会发布，没有人会知道你的存在。
- **“再添加一个功能”** — 从不发布。每个建议的发布日期都会因为一个更多功能而被推迟。范围无限蔓延；发布永远不会到来。

中间的道路是 **SLC — 简单、可喜爱、完整**（Jason Cohen），是发布一个极简 MVP 的解毒剂，MVP 是极简但不可爱的。不要发布一个无人想要的 stub；不要等待一个臃肿的 everything-app。可发布的 v1 是：

- **简单** — 它只做一件事。不是很多事做得不好。一个清晰的工作，做得很好。
- **可喜爱** — 人们想要使用它，而不仅仅是忍受它。MVP 要求用户忍受精简的体验“以提供反馈”。SLC 给他们提供他们愿意选择的东西。如果没有人会对失去它感到难过，它还不可爱。
- **完整** — 它是针对那件事的完整体验，而不是一个有明显漏洞的 stub。在其选择的作用范围内是完整的，而不是更大承诺的提示。

**门:** 如果它还不简单、可喜爱和完整，你就处于“再添加一个功能”的领域——只有在添加范围是所缺少的情况下，否则你处于隐形模式，应该发布。缩小范围，直到有一个东西是可喜爱和完整的，然后发布那个东西。SLC 给你一个真正的发布，而不是一个永远不会到来的完美发布。

**运行阶段之前的快速检查：**

- [ ] 它是否只做一件明确定义的事情？(简单)
- [ ] 目标用户是否会选择使用它，而不仅仅是忍受它？(可喜爱)
- [ ] 那件事是一个完整的体验，没有任何明显的 stub？(完整)
- [ ] 你是否在达到这个标准线之后继续打磨？→ 停止。你处于隐形模式。发布。
- [ ] 你是否仍在添加新的东西到范围中？→ 停止。你处于“再添加一个功能”模式。缩小范围以返回 SLC。

**目录提交准备就绪（来自 `directory-submissions` 技能）:** 询问以下 9 个问题。如果有任何一个回答“否”，它们就不准备就绪——首先帮助他们构建缺失的部分。

1. 产品是否公开可访问（没有密码墙）？
2. 是否有定价页面（即使是“在测试期间免费”）？
3. 隐私政策 + 条款是否已上线？
4. PNG + SVG + 方形 + 偏好的图标资产？
5. 5-8 个真实截图 + 60-90 秒演示视频？
6. 落地页 GEO 就绪（单个 H1, 顺序层次结构, FAQ schema, 结构化数据）？
7. 至少 3 个替代页面和 3 个用例页面已上线并索引？
8. 模板库或引导磁铁资产（如果适用）？
9. 至少 20 个 beta/早期用户可以在 G2 上留下评论？

1-7 中的任何“否”都是硬性阻止。8-9 中的“否”是软性阻止：你可以发布，但会失去 Tier 2 审查价值并出现 Typeform 风格的复合效果。

**ORB 通道策略（来自发布技能）:** 结构化你的发布营销跨三种通道类型。所有内容最终都应该回到自有通道。

### 自有通道

你拥有通道（尽管你拥有受众）。直接访问，无需算法或平台规则。

- 电子邮件列表、博客、播客、品牌社区（Slack、Discord）、网站/产品
- **根据受众从 1-2 个通道开始**：行业缺乏高质量内容 → 博客；人们想要直接更新 → 电子邮件；互动很重要 → 社区

### 租用通道

提供可见性但你不控制的平台。算法会变化，规则会改变，付费才能玩。

- 社交媒体（Twitter/X, LinkedIn, Instagram）、应用商店、YouTube、Reddit
- **如何正确使用**：选择 1-2 个受众活跃的平台；使用它们将流量引导到自有通道；不要依赖它们作为你唯一的策略

### 借用通道

利用别人的受众来简化最难的部分——获得关注。

- 客座内容（博客文章、播客访谈、简报特色）
- 合作（网络研讨会、联合营销、社交接管）
- 演讲活动（会议、小组讨论、虚拟峰会）
- 影响者合作
- **要积极主动**：列出你的受众关注的行业领导者 → 提议双赢合作 → 使用 SparkToro 或 Listen Notes 等工具查找受众重叠

通过门，然后运行下面的阶段。

## 风格化语音和人性化处理

每个网站都有可见的营销文本（英雄、功能、CTA、元描述、OG 描述、博客文章、404 页面文本）。在发布之前，必须进行两层润色：

### 1. 一次定义 `TONE.md` 每个网站

询问用户：“这个网站是否已经有一个 `TONE.md`？” (`yes-already-exists` | `no-create-from-template` | `skip-use-default`).

如果创建：写入 `.agents/TONE.md` 或 repo 根目录 `TONE.md`。有关 `TONE.md` 结构，请参阅 `references/templates.md`（第“TONE.md 模板”部分）。

`TONE.md` 指定：声音（简洁、反叛等），禁止模式（例如，“探索”、“关键”、“em 短横线”，AI 听起来像开头的句子），句子长度偏好，受众阅读水平，用户自己写作中好的和坏的句子的示例。

### 1. 在匹配的语言中运行人性化处理

在每次起草步骤后（无论是由文案技能、手动或直接由 Claude 直接执行），运行人性化处理以去除 AI 模式。

询问用户在会话开始时（如果尚未知道）网站的主要受众语言：

- `english-global` → `npx skills add https://github.com/blader/humanizer --skill humanizer`
- `french` → 使用 `samber/cc-skills@humaniseur-fr`（定制的法语人性化处理程序）或等效法语调整技能
- `other` → 如果有可用的匹配人性化处理程序，请安装；否则，技能会以语言特定的反模式清单形式写入行内

将人性化处理应用于：英雄副本、功能描述、CTA 按钮、元描述、OG/Twitter 卡描述、博客文章、电子邮件注册确认、404 页面文本。法律页面除外（它们有固定的措辞要求）。

### 2. 始终在调用文案技能时引用 `TONE.md`

当委派给任何文案或内容写作子技能（在会话开始时根据技能选择工作流程选择）时，请将 `TONE.md` 包含在提示上下文中。明确传递声音约束：“遵循 `.agents/TONE.md`。避免列出的模式。起草后应用人性化处理。”

## 浏览器交互偏好

许多检查需要真实的浏览器（Lighthouse 运行，securityheaders.com 扫描，opengraph.xyz 验证，Twitter 卡验证器，移动视口，屏幕阅读器烟雾，网络标签检查）。

**始终优先使用 Claude Chrome 扩展程序。** 只有在 Claude Chrome 扩展程序不可用时才回退到 Playwright。如果两者都不可用，请询问用户是否要完全跳过浏览器检查或等待他们启用一个。

## 验证工具

大多数检查都可以在命令行中完成，无需第三方服务。在每個阶段都使用这些工具内联。不要单独依赖 Cloudflare/Vercel/Google 控制面板中的面板。

**DNS（阶段 1）:**

```bash
dig +short A example.com                          # A 记录
dig +short AAAA example.com                       # AAAA (IPv6)
dig +short MX example.com                         # MX (邮件)
dig +short TXT example.com                        # SPF + 验证 TXT
dig +short TXT _dmarc.example.com                 # DMARC
dig +short TXT default._domainkey.example.com     # DKIM（选择器变化）
dig +short CAA example.com                        # CAA
dig +dnssec example.com | grep RRSIG              # DNSSEC 激活
```

**TLS / HTTPS（阶段 1）:**

```bash
curl -sIL https://example.com | head             # 跟随重定向
curl -sI https://www.example.com                 # 检查 www 处理
openssl s_client -showcerts -connect example.com:443 < /dev/null 2>/dev/null | openssl x509 -noout -dates
```

**标题（阶段 4）:**

```bash
curl -sI https://example.com | grep -iE 'content-security-policy|strict-transport-security|x-frame-options|x-content-type-options|referrer-policy|permissions-policy'
# 完整标题输出:
curl -sI https://example.com
# 外部评分器:
curl -sI "https://api.securityheaders.com/?q=https://example.com&followRedirects=on&hide=on" -I | grep -i 'x-grade'
```

**SEO 文件（阶段 5）:**

```bash
curl -s https://example.com/robots.txt
curl -sI https://example.com/sitemap.xml
curl -s https://example.com/sitemap.xml | head -40
curl -s https://example.com/llms.txt
# Schema (JSON-LD):
curl -s https://example.com/ | grep -A 50 'application/ld+json'
# hreflang:
curl -s https://example.com/ | grep -i hreflang
```

**Open Graph & 社交预览（阶段 6）:**

使用 `curl -s URL | grep -iE 'og:|twitter:'` 验证所有 OG 和 Twitter 标签

- `og:title`, `og:description`, `og:url`, `og:type`, `og:site_name`
- `og:image` 1200×630px, 绝对 URL, `og:image:width` 和 `og:image:height` 声明, `og:image:alt` 设置
- **每个页面的 `og:image`**，而不是一个全局的。对于文档网站：动态生成自页面标题。对于博客文章：每篇文章的自定义图像。
- `og:locale` + `og:locale:alternate` 为每个语言设置（如果多语言）
- Twitter 卡片: `twitter:card=summary_large_image`, `twitter:title`, `twitter:description`, `twitter:image`, `twitter:site` (handle)
- 使用 opengraph.xyz（涵盖 FB, LinkedIn, Slack, Discord, WhatsApp 预览）通过 Claude Chrome 扩展程序进行验证
- 使用 Twitter 的卡片验证器进行验证
- 手动检查：将 URL 粘贴到 LinkedIn DM、Slack 频道、Discord、iMessage。预览必须在所有这些地方正确显示。

## 偏好的图标和 Web 窗口程序

查看 `references/templates.md` 中的 `manifest.json` 模板。

使用 realfavicongenerator.net 或 favicon.io 从单个 1024×1024 源 PNG 生成。至少现代集：

- [ ] `/favicon.ico`（多分辨率 16/32/48）。使用 `curl -sI https://example.com/favicon.ico` 验证。
- [ ] `/favicon.svg` 包含嵌入的 `<style>@media (prefers-color-scheme: dark) { ... }</style>` 以支持暗黑模式。使用 `curl -sI https://example.com/favicon.svg` 验证。
- [ ] `/apple-touch-icon.png` 180×180px，无透明度，不透明背景。使用 `curl -sI` 验证。
- [ ] `/web-app-manifest-192x192.png`（Android PWA 图标）
- [ ] `/web-app-manifest-512x512.png`（Android 启动画面）
- [ ] `/manifest.json` 引用这两个 PNG，并包含 `theme_color`, `background_color`, `name`, `short_name`, `display`。使用 `curl -s https://example.com/manifest.json | jq .` 验证。

**已弃用：**

- `mstile-*.png`（Windows 图标）
- `safari-pinned-tab.svg`（自 macOS Big Sur 以来已弃用）
- `favicon-16x16.png` / `favicon-32x32.png`（由 `.ico` 和 `.svg` 涵盖）

**HTML 头验证:**

```bash
curl -s https://example.com/ | grep -iE 'rel="icon"|rel="apple-touch-icon"|rel="manifest"'
```

---

## 质量门

委托给 `addyosmani/web-quality-skills`。该技能涵盖 150 多个 Lighthouse 审计，涵盖性能、可访问性、SEO 和最佳实践。

- [ ] **Unlighthouse 站点级爬取**: `npx unlighthouse --site {site}` — 爬取所有页面并在每个页面上运行 Lighthouse。在执行每个 URL 检查之前，显示任何在任何一个轴上低于 90 的页面。

- [ ] Lighthouse 所有 4 个轴，移动模式：每个轴 ≥90 目标（性能、a11y、最佳实践、SEO）
- [ ] Lighthouse 所有 4 个轴，桌面模式：每个轴 ≥95
- [ ] Core Web Vitals 实际数据（CrUX 通过 PageSpeed Insights）：LCP < 2.5s, INP < 200ms, CLS < 0.1, 在移动和桌面模式下都适用
- [ ] 可访问性（WCAG 2.2 AA 通过 `web-quality-skills`）：键盘导航工作于每个交互元素，焦点环可见，文本颜色对比度 ≥4.5:1，所有图像都有 `alt`，标题层次结构是单调的（H1 → H2 → H3），图标按钮的 ARIA 标签
- [ ] 真实的移动设备测试（而不仅仅是开发工具模拟器）。使用 Claude Chrome 扩展程序在真实设备上的移动视口或 BrowserStack。
- [ ] 跨浏览器烟雾测试：Chrome, Safari, Firefox 最新稳定版
- [ ] 打印样式表合理性（Cmd+P 应该不会破坏布局）

---

## 生态系统交叉链接

自有属性之间的内部交叉链接。对于任何多域所有者来说，这是一个高杠杆的 SEO 行动。

询问用户：“列出您生态系统中的其他域，它们与这个新网站主题相关。” 然后对于每个域：

- [ ] 从现有网站添加链接（页脚/导航/"其他项目"部分），主题相关
- [ ] 在匹配的 GitHub 仓库的 README 中添加链接（如果它记录了一个库）
- [ ] 验证互惠链接：每个添加的链接都应指向适当的位置
- [ ] 如果新网站记录了 Go 库，请从相关库文档中添加链接

不要过度链接。只有在主题相关时才进行交叉链接。一个记录日志的网站不应该链接到一个关于骑自行车的个人博客。

---

## 第 10 步：设置每周 SEO 维护子代理

发布后，设置一个计划在后台运行的代理，例如 Hermes 或 Claude Cowork Routine，每周监控 SEO 健康并显示操作项。

查看 `references/weekly-seo-agent.md` 以获取完整的子代理定义，其中包含每个 harness 的具体等效内容——将匹配你的环境的块复制到它指定位置，在网站的 repo 中（或专用的 ops repo）。

该代理使用这些 MCP 连接器（或等效 API 调用）：

- Ahrefs MCP（反向链接、排名、关键字）
- PostHog MCP（分析关联，AI 机器人流量）
- 网络搜索（SERP 监控，竞争对手检查）
- Google Search Console（通过社区 MCP 或使用服务帐户凭据的 `curl`)
- **在创建文件之前通过问题工具询问是否设置每周 SEO 代理？** (`yes-create-agent-file` | `yes-but-defer` | `skip-for-now`).

当 MCP 不可用时，请使用 Claude for Chrome extension。

---

## 第 11 步：目录提交执行

执行来自 `directory-submissions` 技能的目录提交工作流程。这是分布的基础层——绝不是整个策略。

### 第 1 步：选择层级（来自 `references/directory-list.md`）

| 层级 | 当初 | 示例 | 典型数量 |
| --- | --- | --- | --- |
| **第 1 级 — 标志性发布** | 发布周仅 | 产品 Hunt (锚点), BetaList, HN Show HN, Fazier, DevHunt | ~15 |
| **第 2 级 — 创业/SaaS** | 第 1 周 + 滚动 | AlternativeTo, SaaSHub, G2, Capterra, F6S, SourceForge, Slashdot | ~50 |
| **第 2 级 — AI 目录** | 第 1-3 周 | TAAFT, Futurepedia, Toolify, Future Tools, aitools.inc, AIStage | ~40 |
| **第 4 级 — Agent/MCP 注册表** | 第 1-3 周（如果 MCP） | Glama, APITracker, LF MCP 注册表, AI Agents List | ~10 |
| **第 5 级 — 无代码目录** | 第 1-3 周（如果无代码） | NoCodeFinder, No Code MBA, We Are No Code, MakerPad | ~8 |
| **第 6 级 — “最佳”列表文章** | 滚动推广 | Cold outreach to DR 40+ 博客文章 | ~10 个包含项 |
| **第 7 级 — 集成市场** | 集成发布时 | Zapier, HubSpot, Slack, Airtable, Notion | ~5 |
| **第 8 级 — 个人资料 & 内容平台** | 滚动 | GitHub, WordPress.com, Substack, Dev.to, SlideShare, Behance | ~50 |
| **第 9 级 — 本地企业目录** | 滚动（如果适用） | Manta, Hotfrog, Locanto, MerchantCircle | ~20 |
| **第 10 级 — 论坛 & 社区** | 滚动（首先参与） | SitePoint, GrowthHackers, Warrior Forum, Designer News | ~13 |
| **第 11 级 — 媒体稿 & 文章网站** | 发布 + 里程碑 | PRLog, PR.com, EzineArticles, Feedspot | ~25 |
| **第 12 级 — 社交书签** | 滚动 | Scoop.it, Diigo, Pearltrees | ~5 |
| **第 13 级 — 垂直垂直目录** | 当垂直适用时 | Justia (法律), Porch (家居), LandBook (设计), 等. | ~20 |

**筛选规则:** 只有当产品是真实匹配时才提交（DR 低于 10，没有流量，没有编辑质量）。它们会稀释你的反向链接配置文件，Google 的垃圾邮件检测可能会对你的产品进行处罚。

### 第 2 步：为每个层级准备资产变体

对于每个层级，准备一个独特的描述变体（来自 `references/positioning-variations.md`）：

- **标语** 10 个字以内
- **简短描述** 60 个字符
- **长描述** 150 个字
- **5-8 个类别标签**
- **图标** 资产
- **截图** + 演示视频 URL
- **创始人故事**（2-3 句话）

**关键:** 不要在所有目录中复制粘贴相同的长描述。每个层级都应更改开头的句子、功能重点和受众框架。

### 第 3 步：批量提交并跟踪

设置跟踪电子表格 (`references/submission-tracker-template.csv`)。从左到右逐批工作。每批 2-3 小时是现实的。

对于每个提交：

1. 复制适用于该层级的可用变体
2. 填写表单
3. 上传资产
4. 提交
5. 记录：日期、URL、状态、评论员注释
6. 一旦上线，验证反向链接是否存在且为 dofollow：`curl -sIL https://directory.com/your-listing | grep -i rel=`。如果不存在，链接是 dofollow。

---

## 第 12 步：发布后势头

你的发布在公告发布后不会结束。现在需要采用采用和保留工作。不要依赖一个单一的发布事件。定期更新和功能发布可以维持参与度。

### 立即发布后操作

- **教育新用户:** 设置自动的 onboarding 电子邮件序列，介绍关键功能和用例。
- **重申发布:** 在你的每周/每两周/每月摘要电子邮件中包含公告，以捕获错过的人。
- **与竞争对手区分:** 发布比较页面，突出显示为什么你是明显的选择。
- **更新网页:** 在你的网站上添加专门的关于新功能/产品的部分。
- **提供动手预览:** 创建无代码交互式演示（使用 Navattic 等工具）以便访客在注册之前可以探索。

### 如何确定要宣布的内容优先级

使用此矩阵来决定每个更新需要多少营销：

**主要更新**（新功能、产品重做）：

- 跨多个渠道进行完整活动
- 博客文章、电子邮件活动、应用内消息、社交媒体
- 最大化曝光

**中等更新**（新集成、UI 增强功能）：

- 针对相关部分发送电子邮件，应用内横幅
- 不需要完整的宣传

**小更新**（错误修复、小调整）：

- 更改日志和发布说明
- 表明产品正在改进
- 不要主导营销

### 宣传策略

- **分阶段发布:** 不要一次发布所有东西，分阶段发布以维持势头。
- **重用表现良好的策略:** 如果之前的公告产生了共鸣，请应用这些见解到未来的更新。
- **保持参与:** 继续使用电子邮件、社交媒体和应用内消息来突出显示改进。
- **表明积极开发:** 即使是小的更改日志更新也会提醒客户你的产品正在发展。这建立了保留和口碑——客户会感到自信你会继续存在。

---

## KPI 和跟踪仪表板

每周跟踪。如果一个数字没有移动，请调查——不要只是提交更多目录。

| 指标                           | 第 0 天 | 第 30 天目标 | 第 90 天目标 |
| -------------------------------- | ----- | ------------- | ------------- |
| 域评分 (DR)               | 0     | 20            | 30+           |
| 推荐域                       | 0     | 30            | 80+           |
| 索引页面                    | —     | 50            | 200+          |
| 每日有机点击量               | 0     | 30            | 200+          |
| 目录列表存活                 | 0     | 50            | 70+           |
| G2 评论                       | 0     | 10            | 25            |
| Capterra 评论                 | 0     | 5             | 15            |
| AI 引用（手动检查）      | 0     | 3             | 15+           |
| 目录推荐注册                 | 0     | 50            | 300           |
| 用例/ICP 页面注册             | 0     | 20            | 300           |

---

## 不应该做什么

1. **不要为目录提交服务付费** ($60–$200 包裹)。这个目的就是免费的。这是一个下午的复制粘贴工作。
2. **不要提交到垃圾目录**（DR 低于 10，没有流量，没有编辑质量）。它们会稀释你的反向链接配置文件，Google 的垃圾邮件检测可能会对你的产品进行处罚。
3. **不要以错误的定位提交**。重新阅读每个层级的位置表。通用的描述会浪费列表。
4. **不要将目录视为你整个 GTM。** 它们是基础。内容 + 社区 + 评论实际上才是真正将内容转换为用户的东西。
5. **不要在 G2/Capterra 上跳过评论。** 没有评论的列表是死的。运行 10-in-30 协议或不要提交。
6. **不要在 Product Hunt 上要求点赞。** 2026 算法会处罚它。要求 **反馈**。
7. **不要每周修改旧的目录列表**。一次提交，每季度检查一次。
8. **不要在目的地页面存在之前提交**。链接股权需要一个目的地。
9. **不要在目录中重复描述**。AI 引擎会处罚重复内容。
10. **在比较页面上不要撒谎。** AI 引擎会交叉引用并降级谎言。
11. **不要在发布当天出现索引高峰。** 飞轮是模板 + 替代方案 + 评论 + 持续的内容——不是一天 PH。
12. **不要忘记 Crunchbase, LinkedIn 公司页面和 Wikidata。** 这些会为 AI 训练语料库提供信息，对于 GEO 很重要。
13. **在通过 SLC 门之前不要发布。** Stealth Mode 和“再添加一个功能”都会扼杀发布。
14. **不要在营销文案中跳过人性化处理。** AI 模式在英雄、CTA、元描述、OG 描述中会损害信誉。
15. **不要假设分析“只是工作”。** 在发布之前，使用 curl 验证每个集成——GA4, PostHog, GSC, Bing, Ahrefs。
16. **不要忽略备份演练。** 一个未经测试的备份不是备份。在发布之前将其恢复到暂存数据库中。

---

## 输出格式

在完整的运行结束后，输出按阶段分组的状态报告：

```
Phase 1: Domain & Infrastructure  [9/10 pass]
  ✓ Cloudflare 代理开启
  ✓ DNS 记录配置
  ...
  ✗ DMARC 缺失。修复：在 _dmarc.example.com 上添加 TXT 记录，策略 v=DMARC1; p=quarantine;...
```

随后是三个列表，按顺序：

1. **阻止项**（在发布之前必须修复）
2. **建议修复**（在宣布之前应该修复）
3. **可选改进**（发布后）

最后询问：“你想先处理哪个列表？” (`blockers` | `recommended` | `optional` | `done-for-now`).

---

## 参考

- `references/decisions.md`: 网站类型的 AI 抓取策略矩阵, 可观察性层级矩阵
- `references/templates.md`: robots.txt, llms.txt, manifest.json 模板, 每个严格程度级别的安全标题模板
- `references/weekly-seo-agent.md`: 每周 SEO 维护子代理的完整定义（MCPs, 任务, 输出格式）
- `assets/weekly-seo-*.md`, `assets/weekly-seo-vibe.toml`: 每个harness 的代理定义文件（从 `references/weekly-seo-agent.md` 链接）——复制与你的 harness 匹配的块
- `references/directory-list.md`: 13 层级目录目录，包含提交时间、示例和数量
- `references/positioning-variations.md`: 每个目录层级的定位变体库（标语, 短/长描述, 类别标签）
- `references/submission-tracker-template.csv`: 目录提交跟踪电子表格模板

**注意:** 本文档中的 URL、标题、代码块、内联代码、命令、文件路径、URL 和占位符应保持原样。产品名称、专有名词和 API 名称应保持原样；翻译所有其他内容。
