---
name: site-launch-checklist
description: 新网站或网络应用上线前的检查清单。范围：分析（GA4、PostHog、Google Search Console、Ahrefs）、DNS、TLS和备份、法律和CNIL/GDPR合规性、安全头信息、SEO和GEO（robots.txt、站点地图、llms.txt、hreflang、schema标记、关键词研究）、通过TONE.md进行文案风格调整和人性化处理、OpenGraph和社交预览、图标和网页清单、Lighthouse、核心网络健康指标和WCAG质量门、目录提交、Product Hunt、G2/Capterra评价、上线后监控。当用户说“检查清单”、“准备上线”、“上线前”、“准备生产环境”、“上线前审计”，或询问网站评审、上线前审计、帮助上线网站或应用、部署域名到生产环境，或发布营销、文档、SaaS或潜在客户吸引网站时使用。
---

**问题：** 通过环境的问题工具向用户提问——切勿以纯文本散文形式提问。一次一个问题，2-4个可点击选项，等待答案。如果环境没有问题工具，则使用相同的选项以散文形式提问，一次一个。

# 网站发布检查清单

发布新网站的预发布审计和设置工作流程。针对 Cloudflare DNS + Vercel 托管 + PostHog + 法律环境的意见性方案。

## 交互风格（首先阅读）

这项技能是故意交互式的。与其假设，不如积极提问。用户将点击，而不是输入。

**在每次运行开始时始终提出以下问题**（一次一个，按此顺序）：

1. 网站类型：`doc-site` | `marketing/lead-gen` | `SaaS-app` | `training/paid-course` | `personal-portfolio`
2. 迁移：`greenfield-new-domain` | `migration-need-301-redirects` | `replacing-existing-on-same-domain`
3. 多语言：`single-locale` | `en` | `fr+en` | `other-multi`
4. PostHog 设置：`hogpost.samber.dev` | `set-up-new-proxy` | `skip-PostHog`
5. AI 抓取策略：`use-default-for-site-type` | `customize-per-bot` | `block-all`
6. 浏览器工具可用：`claude-chrome-extension` | `playwright` | `neither-skip-browser-checks`

**在每个阶段中的每个决策点再次提问**，包括：

- 是否安装 Sentry / BetterStack / Crisp（取决于网站类型，明确提问）
- www 与 apex 算法偏好（大多数网站：apex；无论如何都要提问）
- 如果用户选择了 `customize-per-bot`，允许哪些 AI 机器人
- CSP 严格程度：`strict-default-src-none` | `balanced-allow-self` | `permissive-for-marketing`
- 是否完全跳过某个阶段（例如，如果非 FR 网站则跳过阶段 3）

在未获得明确用户输入之前，切勿继续下一个决策点。没有检查点的冗长检查清单不是目标。

**切勿在未获得明确用户确认的情况下安装任何 MCP 服务器或技能。** 在运行 `npx skills add`、`claude mcp add` 或任何等效安装命令之前，始终通过问题工具询问——即使技能选择工作流程建议了一个经过筛选的子集。

## 如何使用此技能

1. 运行上述会话开始问题。
2. 按顺序引导用户完成阶段 1-10。对于每个阶段：a. 列出项目，询问是否应跳过。b. 对于每个剩余项目，运行验证命令（见下文“验证工具”）。c. 报告通过/失败。失败时，询问用户是否要立即修复或稍后排队。
3. 以阶段分组的方式结束状态报告，明确区分阻塞项、建议修复和可选改进。

## 伴随技能

六个技能包对网站发布很有用。**切勿安装完整的多技能包**。实际要安装的子集是在调用时根据用户确认的网站类型决定的。

### 包清单

| 包 | 涵盖内容 | 通常适用于 |
|---|---|---|
| `AgriciDaniel/claude-seo` | SEO + GEO + schema + hreflang + sitemaps 审计，并行子代理 | 所有网站类型 |
| `addyosmani/web-quality-skills` | Lighthouse、核心网络性能、无障碍性、性能、最佳实践 | 所有网站类型 |
| `trailofbits/skills` | 安全审计（OWASP、标题、依赖项） | 所有网站类型 |
| `aaron-he-zhu/seo-geo-claude-skills` | 20 个 SEO+GEO 技能，CORE-EEAT + CITE 框架，`/seo:` 命令 | 内容密集型网站、竞争性细分市场 |
| `coreyhaines31/marketingskills` | 约 30 个营销技能（CRO、文案、广告、弹出窗口、电子邮件、付费墙等） | `marketing/lead-gen`、`SaaS-app`、`training/paid-course` |
| `jonathimer/devmarketing-skills` | 33 个开发者营销技能（角色、文档作为营销、技术教程等） | `doc-site`、`SaaS-app` 用于开发者 |

### 技能选择工作流程（在会话开始时运行）

用户确认网站类型后，对于**与该网站类型相关的每个包**：

1. **列出可用子技能**：`npx skills add owner/repo --list`
2. **根据网站类型和此技能将执行的阶段提出经过筛选的子集**。将每个阶段的需求与列表返回的特定子技能相匹配。
3. **与用户确认**。当建议列表有 3 个以上项目时使用多选，否则使用单选（`install-as-proposed` | `let-me-modify` | `skip-this-pack`）。
4. **批量安装同意的子集**：`npx skills add owner/repo --skill A B C`

规则：

- 子技能名称存在于包中，而不是在 SKILL.md 中。始终查询 `--list` 获取当前状态。包内容会变化。
- 切勿在缺少 `--skill` 的情况下运行 `npx skills add owner/repo`（那会安装所有内容）。
- 网站类型 → 包映射（要枚举哪些包，每个工作流程仍按子技能选择）：
  - `doc-site`：claude-seo、web-quality-skills、trailofbits、seo-geo-claude-skills、devmarketing-skills
  - `marketing/lead-gen`：claude-seo、web-quality-skills、trailofbits、seo-geo-claude-skills、marketingskills
  - `SaaS-app`：全部六个
  - `training/paid-course`：claude-seo、web-quality-skills、trailofbits、marketingskills
  - `personal-portfolio`：claude-seo、web-quality-skills、trailofbits、seo-geo-claude-skills（轻量级子集）
- 如果用户后来请求需要尚未安装的子技能的阶段，请再次运行该单个子技能的工作流程，而不是重新安装整个子集。

这避免了导入用户不需要的 80 多个技能，避免了子技能名称过时，避免了针对单个包版本过度拟合。

在阶段中委派时，不要重复此技能协调的工作。调用具有狭窄范围的专家（例如，“仅运行 URL X 的安全标题子审计”）。

## 阶段 0：发布准备门

**在任何其他阶段之前运行此操作。** 产品会自行营销——但一个未准备好的产品不会营销。发布机制只有在你要发布的东西值得发布时才会奏效。

两种失败模式从相反的两端扼杀发布：

- **隐形模式**——发布太晚。“穿着华服的拖延症。”你一直在私下打磨，等待产品完美。它永远不会发布，而且没有人会知道你的存在。
- **“再多一个功能”**——永远不发布。每个建议的发布日期都会因为一个更多功能而被推迟。范围无限蔓延；发布永远不会到来。

中间的道路是 **SLC——简单、可爱、完整**（Jason Cohen），是发布一个最小但不受欢迎的 MVP 的解毒剂。不要发布一个无人想要的桩；不要等待一个臃肿的“一切应用”。一个可发布的 v1 是：

- **简单**——它只做一件事。不是糟糕地做很多事。一个清晰的工作，做得很好。
- **可爱**——人们想要使用它，而不仅仅是忍受它。MVP 要求用户忍受一个精简的体验“以提供反馈”。SLC 给他们一些他们会选择的东西。如果没有人会因为失去它而感到难过，它还不可爱。
- **完整**——它是针对那件事的完整体验，而不是一个有明显漏洞的桩。在其选择范围内完整，而不是更大承诺的预告片。

**门**：如果它还不简单、可爱、完整，你就在“再多一个功能”的领域，只有当增加范围是缺失的东西时——否则你就在隐形模式中，应该发布。削减范围，直到一件事变得可爱且完整，然后发布那件事。SLC 让你立即有一个真实的发布，而不是一个永远不会完美的发布。

**在运行阶段之前快速检查：**

- [ ] 它是否做一件清晰定义的事？（简单）
- [ ] 目标用户是否会选择使用它，而不仅仅是忍受它？（可爱）
- [ ] 那件事是一个完整体验，没有明显的桩？（完整）
- [ ] 你是否在这一点之后继续打磨？→ 停止。你处于隐形模式。发布。
- [ ] 你是否仍在增加范围的新事物？→ 停止。你处于“再多一个功能”。削减回 SLC。

**目录提交准备情况（来自目录提交技能）：** 提问这 9 个问题。如果有任何“否”，它们就不准备——首先帮助他们构建缺失的部分。

1. 产品是否公开可访问（没有密码墙）？
2. 是否有定价页面（即使是“在 Beta 期间免费”）？
3. 隐私政策 + 条款是否已发布？
4. Logo 资产在 PNG + SVG + 方形 + 网站图标？
5. 5-8 张真实截图 + 60-90 秒演示视频？
6. 落地页面 GEO 就绪（单个 H1、顺序层次结构、FAQ schema、结构化数据）？
7. 至少 3 个替代页面和 3 个用例页面已上线并索引？
8. 模板库或引子磁铁资产（如果适用于类别）？
9. 至少 20 个 Beta/早期用户可以在 G2 上留下评论？

1-7 中的任何“否”都是硬性障碍。8-9 中的“否”是软性障碍：你可以发布，但会失去 Tier 2 审查价值和 Typeform 风格的复合效果。

**ORB 渠道策略（来自发布技能）：** 在三种渠道类型中构建你的发布营销。最终一切都应该回到自有渠道。

### 自有渠道

你拥有渠道（尽管不是受众）。没有算法或平台规则的直接访问。

- 邮件列表、博客、播客、品牌社区（Slack、Discord）、网站/产品
- **根据受众从 1-2 个开始**：行业缺乏优质内容 → 博客；人们想要直接更新 → 电子邮件；参与度很重要 → 社区

### 租赁渠道

提供可见性但你不控制的平台。算法会变化，规则会改变，付费玩会增加。

- 社交媒体（Twitter/X、LinkedIn、Instagram）、应用商店、YouTube、Reddit
- **如何正确使用**：选择 1-2 个你的受众活跃的平台；使用它们将流量引导至自有渠道；不要依赖它们作为你唯一的策略

### 借用渠道

利用他人的受众来简化最难的部分——获得关注。

- 客座内容（博客文章、播客访谈、通讯特色）
- 合作（网络研讨会、联合营销、社交接管）
- 演讲活动（会议、小组讨论、虚拟峰会）
- 影响者合作
- **要积极主动**：列出你的受众关注的行业领导者 → 提议双赢合作 → 使用 SparkToro 或 Listen Notes 等工具查找受众重叠

通过门，然后运行下面的阶段。

## 文案声音和人性化处理

每个网站都有可见的营销文案（英雄、功能、CTA、元描述、OG 描述、博客文章、404 页面文本）。在发布前必须进行两层润色：

### 1. 一次为每个网站定义 `TONE.md`

询问用户：“这个网站是否已经有一个 `TONE.md`？”（`yes-already-exists` | `no-create-from-template` | `skip-use-default`）。

如果创建：将其写入 `.agents/TONE.md` 或仓库根目录 `TONE.md`。参见 `references/templates.md`（“TONE.md 模板”部分）了解结构。

TONE.md 指定：声音（简洁、反叛等）、禁止模式（例如，“深入探索”、“至关重要”、破折号、AI 听起来开头的句子）、句子长度偏好、受众阅读水平、用户自己写作的良好和糟糕句子的示例。

### 2. 在匹配的语言中运行人性化处理

在每次起草步骤后（无论是由文案技能、手工或直接由 Claude 完成），运行人性化处理以去除 AI 模式。

如果会话开始时尚未知道网站的主要受众语言：

- `english-global` → `npx skills add https://github.com/blader/humanizer --skill humanizer`
- `french` → 使用 `samber/cc-skills@humaniseur-fr`（定制的法语人性化处理程序）或等效法语调整技能
- `other` → 如果有可用的匹配人性化处理程序，请安装；否则，技能以简短的特定语言反模式清单形式内联编写

将人性化处理应用于：英雄文案、功能描述、CTA 按钮文本、元描述、OG/Twitter 卡描述、博客文章、电子邮件注册确认、404 页面文本。法律页面（mentions légales、CGV）除外，因为它们有严格的措辞要求。

### 3. 在调用文案技能时始终参考 `TONE.md`

在将任务委托给任何文案或内容写作子技能（根据技能选择工作流程在调用时选择）时，将 `TONE.md` 包含在提示上下文中。明确传递声音约束：“遵循 `.agents/TONE.md`。避免列出的模式。起草后应用人性化处理。”

## 浏览器交互偏好

许多检查需要真实浏览器（Lighthouse 运行、securityheaders.com 扫描、opengraph.xyz 验证、Twitter 卡验证器、移动视口、屏幕阅读器烟雾、网络选项卡检查）。

**始终优先使用 Claude Chrome 扩展程序。** 只有在 Chrome 扩展程序不可用时才回退到 Playwright。如果两者都不可用，请询问用户是否要完全跳过浏览器检查或等待他们启用一个。

## 验证工具

大多数检查都可以从命令行完成，无需第三方服务。在每个阶段使用这些工具内联。不要单独依赖 Cloudflare/Vercel/Google 仪表板中的面板，使用 curl 进行验证。

**DNS（阶段 1）：**

```bash
dig +short A example.com                          # A 记录
dig +short AAAA example.com                       # AAAA（IPv6）
dig +short MX example.com                         # MX（邮件）
dig +short TXT example.com                        # SPF + 验证 TXT
dig +short TXT _dmarc.example.com                 # DMARC
dig +short TXT default._domainkey.example.com     # DKIM（选择器变化）
dig +short CAA example.com                        # CAA
dig +dnssec example.com | grep RRSIG              # DNSSEC 活跃
```

**TLS / HTTPS（阶段 1）：**

```bash
curl -sIL https://example.com | head             # 跟随重定向
curl -sI https://www.example.com                 # 检查 www 处理
openssl s_client -showcerts -connect example.com:443 < /dev/null 2>/dev/null | openssl x509 -noout -dates
```

**标题（阶段 4）：**

```bash
curl -sI https://example.com | grep -iE 'content-security-policy|strict-transport-security|x-frame-options|x-content-type-options|referrer-policy|permissions-policy'
# 完整标题转储：
curl -sI https://example.com
# 外部评分者：
curl -s "https://api.securityheaders.com/?q=https://example.com&followRedirects=on&hide=on" -I | grep -i 'x-grade'
```

**SEO 文件（阶段 5）：**

```bash
curl -s https://example.com/robots.txt
curl -sI https://example.com/sitemap.xml
curl -s https://example.com/sitemap.xml | head -40
curl -s https://example.com/llms.txt
# Schema（JSON-LD）：
curl -s https://example.com/ | grep -A 50 'application/ld+json'
# hreflang：
curl -s https://example.com/ | grep -i hreflang
```

**Open Graph & 社交（阶段 6）：**

```bash
curl -s https://example.com/page | grep -iE 'og:|twitter:|<title|name="description"'
```

**Favicons & manifest（阶段 7）：**

```bash
curl -sI https://example.com/favicon.ico
curl -sI https://example.com/favicon.svg
curl -sI https://example.com/apple-touch-icon.png
curl -s https://example.com/manifest.json | jq .
```

**404 / 500 / 重定向：**

```bash
curl -sI https://example.com/this-does-not-exist
curl -sIL https://example.com/old-url     # 验证 301 链
```

始终运行相关命令，将输出粘贴给用户以报告，然后询问是否要立即修复或排队。

- [ ] Cloudflare： apex 和 www 域名的代理已开启，TLS 1.3 为最低版本，已启用“始终使用 HTTPS”，在 Cloudflare SSL/TLS 设置中已启用 HSTS 预加载
- [ ] DNS A/AAAA 或 CNAME 指向 Vercel（使用 `dig +short A example.com` 进行验证）
- [ ] Google Workspace 的 MX 记录（使用 `dig +short MX example.com` 进行验证）
- [ ] SPF、DKIM、DMARC 记录（使用上述 dig 命令验证所有三项）
- [ ] 限制证书颁发的 CAA 记录（使用 `dig +short CAA example.com` 进行验证）
- [ ] 在注册商级别启用 DNSSEC（使用 `dig +dnssec` 进行验证）
- [ ] Vercel：项目已链接到仓库，prod 和 preview 环境变量已设置，自定义域名已附加，prod 和 preview 别名正确
- [ ] 确定 www 和 apex 的规范化设置，为非规范化设置配置 308 重定向（使用 `curl -sIL https://www.example.com` 进行验证）
- [ ] 自定义 404 页面可以渲染（使用 `curl -sI https://example.com/does-not-exist` 进行验证）
- [ ] 自定义 500 页面存在（无法轻易验证，除非强制错误，询问用户）
- [ ] 如果是迁移：每个旧 URL 的 301 重定向映射（使用 `curl -sIL` 按每个 URL 进行循环验证）

### 备份

如果在启动时没有配置备份，你将永远不会配置。现在就做。

询问用户：“此应用程序写入哪些数据存储？”（`database-only` | `database-plus-file-storage` | `file-storage-only` | `stateless-no-persistent-data`）。如果是 `stateless-no-persistent-data`，则跳过本节。

**数据库：**

- [ ] 在提供者级别启用自动每日备份（Neon、Supabase、PlanetScale、Railway、RDS — 每个都有一键切换）。通过打开备份面板并确认最后一个备份时间戳是最近的来验证。
- [ ] 保留策略设置为 ≥30 天
- [ ] 如果可用，启用时间点恢复（PITR）（Neon、Supabase、RDS 都支持它）
- [ ] 离站副本：如果提供者在与主站点相同的区域存储备份，请配置跨区域复制或每晚导出到单独的存储账户（S3、R2、GCS）
- [ ] **在启动前进行恢复演练**：选择一个最近的备份，恢复到暂存数据库，验证行数和样本查询。未测试的备份不是备份。

**文件存储（如果适用 — S3、R2、GCS、Cloudflare Images）：**

- [ ] 在主存储桶上启用版本控制
- [ ] 跨区域复制或定期同步到次级存储桶。Backblaze B2 是一个经济实惠且可靠的离站副本选项（比 S3/GCS 出口显著便宜）。使用 `rclone` 每天从 S3/R2/GCS 同步到 B2 的 cron。
- [ ] 生命周期规则：30 天后将旧版本过渡到更便宜的存储，90 天后删除（根据成本承受能力进行调整）

**密钥 / 环境变量：**

- [ ] 所有环境变量都有文档记录并存储在密钥管理器中（1Password、Doppler、Vault 或等效产品）。不在某人的笔记本电脑上的 `.env` 文件中。
- [ ] 验证：如果每个工程师的机器今晚都烧毁了，新团队成员是否只能使用密钥管理器 + git 从头开始恢复 prod？

**监控：**

- [ ] 如果每日备份作业失败，设置警报（电子邮件或 Slack）。大多数提供者都支持此功能；在关闭备份面板之前配置它。

---

## 第二阶段：分析和可观察性

大多数第三方集成都可以通过 Cloudflare 或 Vercel 的一键操作完成。

**对于条件工具（Crisp、Sentry、BetterStack），询问用户** 确认每个站点类型。参见 `references/decisions.md` 中的可观察性级别矩阵。

**始终启用：**

- [ ] Google Analytics 4：已创建属性，嵌入测量 ID，由 CNIL 同意控制
- [ ] PostHog：根据用户的先前回答：
  - 如果 `hogpost.samber.dev`：使用 `api_host: "https://hogpost.samber.dev"` 配置客户端，并验证 CORS 允许新域名（使用浏览器控制台或 `curl -H "Origin: https://newsite.com" -I https://hogpost.samber.dev/decide` 进行测试）
  - 如果 `set-up-new-proxy`：在 `next.config.js` 中添加路径重写到 `us.i.posthog.com` 和 `us-assets.i.posthog.com`，使用 `api_host: "/ingest"` 初始化客户端
  - 如果 `skip-PostHog`：跳过
- [ ] Google Search Console：已验证站点（DNS TXT 或 HTML 文件），已提交站点地图
- [ ] Bing Webmaster Tools：已验证站点，已提交站点地图，IndexNow 密钥文件位于 `/{key}.txt` 在根目录（使用 `curl -sI https://example.com/{key}.txt` 进行验证）
- [ ] Ahrefs：将站点添加到仪表板进行跟踪
- [ ] 将站点添加到内部统计电子表格（如果适用，PostHog 属性注册表 + GitHub Sponsors 跟踪表）

**品牌监控（Google Alerts）：**

对于每个警报，使用以下设置：**频率**：每天一次 | **来源**：自动 | **多少**：所有结果 | **区域**：任何区域

通过 alerts.google.com 设置每个关键词的警报：

- [ ] 域名（例如，`example.com`）
- [ ] 品牌或产品名称（如果是多词，请加引号，例如，`"My Brand"`）
- [ ] 如果网站记录了项目，则关键功能或库名称
- [ ] 竞争对手品牌名称（可选 — 询问用户：`yes-monitor-competitors` | `skip`）

询问用户：“要监控哪些附加关键词？”（`product-name-only` | `domain-plus-brand` | `full-set-with-competitors` | `custom-list`）

**开发者社区监控（F5bot）— 适用于 `doc-site` 和 `SaaS-app` 面向开发者的：**

F5bot（f5bot.com）监控 Reddit、Hacker News 和 Lobste.rs 中的关键词提及并发送电子邮件警报。免费，无需 API。

在 f5bot.com/add 每行设置一个关键词：

- [ ] 品牌或产品名称
- [ ] 域名（捕获链接分享）
- [ ] 关键功能或库名称
- [ ] 如果适用，常见拼写错误

**竞争对手分析（`marketing/lead-gen`、`SaaS-app`、`training/paid-course` 仅限）：**

在编写文案、设置广告或规划内容之前，运行竞争对手分析以了解市场中的现有工作——定位、信息角度、CTA 模式、定价展示和内容策略。

使用深度研究工具或工具链中的竞争对手分析技能（如果可用）。询问：

- "您是否已经有了要分析的竞争对手名称/URL？"（`yes-provide-list` | `no-discover-for-me` | `skip`）
- 如果 `yes-provide-list`：请用户粘贴 2-5 个名称或 URL（自由文本）
- "我们在寻找什么？"（`positioning-and-messaging` | `pricing-strategy` | `content-and-seo` | `full-spectrum`）

将输出输入到：

- 第五阶段关键词策略（目标他们排名但您可以超越或侧翼的查询）
- `TONE.md` 语音校准（故意与该类别中的主导语音区分开来）
- 第六阶段 OG 文案和 CTA 语言（借用经过验证的框架，不要逐字复制）
- 后续调用的文案子技能（将竞争对手快照作为上下文传递）

**条件（询问用户，默认按 `references/decisions.md` 中的站点类型）：**

- [ ] Crisp
- [ ] Sentry
- [ ] BetterStack

---

## 第三阶段：法律和合规（FR）

首先询问：“此网站受法国法律约束吗？”（`yes-FR-operator-or-audience` | `no-EU-only` | `no-non-EU`）。如果没有，请询问是否适用 GDPR 或等效规定并进行调整。

对于 FR 网站：

- [ ] 法律声明页面（强制，每项遗漏的罚款最高可达 75k€）
- [ ] CGV（通用销售条件）如果进行商业活动
- [ ] 隐私政策
- [ ] 服务条款
- [ ] CNIL 合规的 Cookie 同意，该同意**控制** GA4、PostHog、Crisp、Sentry 脚本的加载（而不仅仅是始终加载跟踪器的横幅）。使用 CMP（Axeptio、Tarteaucitron 或自定义）。使用浏览器网络选项卡验证：在明确同意之前没有跟踪器触发。

---

## 第四阶段：安全

将深度审计委托给 `trailofbits/skills`。下面的项目是必须通过的清单。

首先询问：CSP 严格程度级别（`strict-default-src-none` | `balanced-allow-self` | `permissive-for-marketing`）。参见 `references/templates.md` 中每个级别的 CSP 模板。

- [ ] CSP：目标选择的严格程度级别。脚本不使用 `'unsafe-inline'`（使用非空）。使用 `curl -sI ... | grep -i content-security-policy` 进行验证。
- [ ] HSTS：`max-age=31536000; includeSubDomains; preload`。向 hstspreload.org 提交。使用 `curl -sI ... | grep -i strict-transport` 进行验证。
- [ ] X-Frame-Options：`DENY`
- [ ] X-Content-Type-Options：`nosniff`
- [ ] Referrer-Policy：`strict-origin-when-cross-origin`
- [ ] Permissions-Policy：除非使用，否则拒绝相机、麦克风、地理位置、支付
- [ ] 一次性运行所有标题：`curl -sI https://example.com | grep -iE 'content-security|strict-transport|x-frame|x-content-type|referrer-policy|permissions-policy'`
- [ ] securityheaders.com：目标 A+（通过 Claude Chrome 扩展或 `curl https://securityheaders.com/?q=URL` 并解析进行验证）
- [ ] observatory.mozilla.org：目标 90+（通过 Chrome 扩展）
- [ ] 在代码库上运行 `trailofbits/skills` 安全审计
- [ ] 验证客户端包中没有泄露的密钥：通过 Claude Chrome 扩展打开 Chrome DevTools 网络选项卡，grep 响应正文中的 `sk_`、`pk_`、`AKIA`、`ghp_`、`Bearer`

---

## 第五阶段：SEO & GEO

将完整审计委托给 `AgriciDaniel/claude-seo`。下面的项目是编排列表。

参见 `references/templates.md` 中的 `robots.txt`、`llms.txt` 和 `manifest.json` 模板。参见 `references/decisions.md` 中按站点类型划分的 AI 抓取策略矩阵。

- [ ] `/robots.txt` 存在，引用站点地图（使用 `curl -s https://example.com/robots.txt` 进行验证）
- [ ] `/sitemap.xml` 存在，有效（使用 `curl -s https://example.com/sitemap.xml | head -40` 进行验证）。如果多语言，使用站点地图索引和每种语言的站点地图。
- [ ] `/llms.txt` 存在（根据 llmstxt.org 规范，使用 `curl -s https://example.com/llms.txt` 进行验证）
- [ ] AI 抓取策略在 `robots.txt` 中编码。根据站点类型应用 `references/decisions.md` 中的矩阵，然后**通过问题工具确认每个非默认决策**——这将在公共文件中发布，在被抓取之前确保正确。
- [ ] 结构化标记（JSON-LD）：`Organization` + `WebSite` + `BreadcrumbList` 全站；按页面类型适用（`SoftwareApplication` 用于库主页，`Article` 用于博客文章，`FAQPage` 用于 FAQ，`Person` 用于作者简介）。使用 `curl -s URL | grep -A 50 'application/ld+json'` 进行验证。通过 **Google Rich Results Test**（<https://search.google.com/test/rich-results>）和 **Schema.org Validator**（<https://validator.schema.org>）验证结构化数据——Rich Results Test 检查富摘要的资格；Schema.org Validator 捕获 Google 可能静默忽略的规范违规。
- [ ] 每页的元标签：唯一的 `<title>`（50-60 个字符），唯一的 `<meta description>`（150-160 个字符），`<link rel="canonical">`，如果需要 `<meta name="robots">`
- [ ] 如果多语言，每页上的 `hreflang` 标签（每个语言版本都声明所有替代项，包括自身）。使用 `curl -s URL | grep -i hreflang` 进行验证。
- [ ] **使用 Google Trends 和 Ahrefs 进行关键词分析**（它们回答不同的问题，不能互换）：
  - **Google Trends**（trends.google.com）：趋势（上升与下降），地理分布（尤其是 FR 与国际分割），季节性模式，相关查询细分，2-5 个候选关键词的头部对头比较。使用 Trends 来**验证 SEO 投注的方向和时间**。
  - **Exploding Topics**（explodingtopics.com）：在 Google Trends 峰值前几周或几个月出现新兴趋势。使用它来识别上升的查询，在竞争对手巩固之前识别它们，并验证目标关键词是否已经在下降。
  - **Answer The Public**（answerthepublic.com/en）：绘制种子关键词周围的搜索问题、比较和相关查询。使用它来发现长尾意图集群，填充 FAQ 结构化数据，并识别内容差距。
  - **Ahrefs Keywords Explorer**：月度量，关键词难度，SERP 分析，CPC，父主题，流量潜力。使用 Ahrefs 来**从绝对意义上衡量机会**。
  - 结合输出：每页 3-5 个目标查询的排序列表，附带理由（量 × 难度 × 趋势 × 意图匹配）。
  - 委托给会话开始时安装的哪个关键词研究子技能（通过技能选择工作流从安装的包中选择；典型来源是 SEO+GEO 和营销包）。
- [ ] **通过 productrank.ai 进行 AI 可见性审计**：在浏览器中打开 productrank.ai，提交多个类别或产品搜索，运行完整的 AI SEO 报告。它审计网站在 AI 生成的答案（ChatGPT、Perplexity、Gemini、Claude）中如何出现。标记任何零可见性类别并显示 AI 评分员识别的内容差距。
- [ ] 所有可见文本内容进行拼写和语法检查
- [ ] 链接配置文件审计：运行 **Ahrefs Backlink Checker** 和 **Moz Link Explorer** 评估域权威并显示有毒或损坏的入站链接，在启动前进行——尤其是在迁移过程中，以确保旧域股权正确转移
- [ ] 内部链接审计：每个重要页面在主页上 ≤3 次点击内可达

**目标页面策略（来自目录提交技能）：** 如果链接到通用主页，目录将毫无用处。在提交到目录之前构建这些目标页面：

### 1. 替代页面（最高 ROI）

竞争对手的替代页面在 **5–15%** 转化，对于底部的漏斗查询，通常达到 15–30%。每个顶级竞争对手一个页面：

- `/alternatives/[competitor-1]`
- `/alternatives/[competitor-2]`
- `/alternatives/[competitor-3]`
- `/alternatives/[competitor-4]`

每个页面都需要：诚实的功能比较表，“何时选择 X 而非我们”，“何时选择我们而非 X”，价格比较，3–5 个用例示例，强大的 FAQ 带结构化数据。**关键：** 必须诚实。AI 引擎交叉引用竞争对手的功能声明，并会降级撒谎的页面。

### 2. 用例 / ICP 页面

每个 ICP 都有一个专属着陆页：

- `/for/[audience]` — 教练，机构，电子商务，SaaS，顾问等
- `/use-cases/[use-case]` — 领导资格，入职，产品推荐等

### 3. 模板 / 资产库（如果适用）

Typeform 的模板库产生了 **30,000 个非品牌有机注册和 $3M/年的 LTV**。模式：

- 每个可索引页面一个模板在 `/templates/[slug]`。
- H1 使用关键词，150+ 字描述，截图，“何时使用此模板”，“使用此模板” CTA。
- 每页底部相关模板（内部链接 = SEO 复合）。
- 30 天内 100 个模板，90 天内 300 个模板是现实的目标。

### 4. 您自己编写的“最佳”列表

编写您自己类别的诚实汇总：`/blog/best-[category]-tools-2026`。包括自己 + 10 个竞争对手和真实评论。这些排名类别查询，并作为 AI 引擎引用的规范参考。

### 5. 集成页面（当集成推出时）

每个集成 = 一个着陆页在 `/integrations/[partner]`。遵循 Zapier 播放清单：Zapier 从程序化集成页面获得 **~2.6M 月度有机访问量**（其总有机流量的 ~15%）。

**GEO（生成式引擎优化）：** 在 2026 年，30–50% 的“研究工具”查询在 ChatGPT、Claude、Perplexity 或 Google AI Overviews 中进行，而从未接触过传统搜索页面。

### 获取页面引用的策略

- [ ] 确保所有页面都有唯一的 `<title>` 和 `<meta description>`，符合 SEO 最佳实践。
- [ ] 使用 `robots.txt` 和 `sitemap.xml` 正确配置网站地图和抓取规则。
- [ ] 在页面上使用结构化数据（如 JSON-LD），以提高在搜索引擎中的可见性。
- [ ] 通过内部链接和外部链接提高网站的权威性和可信度。
- [ ] 确保网站加载速度快，用户体验良好。
- [ ] 使用社交媒体和其他在线渠道推广网站内容。
- [ ] 监控和分析网站的性能，以便进行持续的优化。

1. **每页一个 H1，顺序标题层级。** 引用率提高 2.8 倍。87% 的引用页面使用单个 H1。
2. **密集、事实性内容，包含可引用的统计数据。** AI 引擎更倾向于具体的数字（“比 X 快 3 倍”）而不是模糊的声明。
3. **每个着陆页都使用 FAQ schema。** AI 引擎对 `FAQPage` JSON-LD 进行答案提取时，会重点考虑。
4. **比较表格。** 可提取、结构化——这正是 AI 答案所需的内容。
5. **在第一 100 字内明确说明“这是什么”的段落。**
6. **在 Reddit 和 Hacker News 上被引用。** Claude 和 Perplexity 对这些网站索引非常重。在 r/SaaS 和 HN 上的真实提及可作为训练燃料。
7. **发布原创研究。** “我们分析了 10,000 个 [事物] 并发现了 X” 成为任何讨论该主题的人的主要引用来源。
8. **声明 Crunchbase、LinkedIn 公司页面和 Wikidata 条目。** 这三个都为 AI 训练语料库提供数据。
9. **如适用，在 MCP 注册表中列出，并使用 A/B 等级**（Glama 特别突出）。LLM 在回答 MCP 问题时会从这些列表中获取信息。

### 测量

每月手动检查：询问 ChatGPT、Claude 和 Perplexity“最好的 [类别] 工具是什么？”并记录产品出现的位置。使用免费的 GEO 跟踪工具（GeoTracker、llmrefs）可自动执行此操作。

---

## 第 6 步：Open Graph & 社交预览

使用 `curl -s URL | grep -iE 'og:|twitter:'` 验证所有 OG 和 Twitter 标签。

- [ ] `og:title`、`og:description`、`og:url`、`og:type`、`og:site_name`
- [ ] `og:image` 1200×630 像素，绝对 URL，声明 `og:image:width` 和 `og:image:height`，设置 `og:image:alt`
- [ ] **每页 `og:image`**，不是全局的。对于文档网站：根据页面标题动态生成。对于博客文章：每篇文章使用自定义图片。
- [ ] `og:locale` + `og:locale:alternate` 每种语言（如果多语言）
- [ ] Twitter Cards: `twitter:card=summary_large_image`、`twitter:title`、`twitter:description`、`twitter:image`、`twitter:site`（用户名）
- [ ] 使用 Claude Chrome 扩展程序通过 opengraph.xyz（涵盖 FB、LinkedIn、Slack、Discord、WhatsApp 预览）进行验证
- [ ] 使用 Twitter 的卡片验证器进行验证
- [ ] 手动检查：将 URL 粘贴到 LinkedIn DM、Slack 频道、Discord、iMessage 中。预览必须在所有这些地方正确显示。

---

## 第 7 步：Favicons & Web Manifest

参见 `references/templates.md` 中的 `manifest.json` 模板。

使用 realfavicongenerator.net 或 favicon.io 从单个 1024×1024 源 PNG 生成。

**现代最小设置：**

- [ ] `/favicon.ico`（多分辨率 16/32/48）。使用 `curl -sI https://example.com/favicon.ico` 验证。
- [ ] `/favicon.svg` 带嵌入的 `<style>@media (prefers-color-scheme: dark) { ... }</style>` 用于暗黑模式。使用 `curl -sI https://example.com/favicon.svg` 验证。
- [ ] `/favicon-96x96.png`（PNG 备用）
- [ ] `/apple-touch-icon.png` 180×180 像素，无透明度，不透明背景。使用 `curl -sI` 验证。
- [ ] `/web-app-manifest-192x192.png`（Android PWA 图标）
- [ ] `/web-app-manifest-512x512.png`（Android 启动画面）
- [ ] `/manifest.json` 引用这两个 PNG，包含 `theme_color`、`background_color`、`name`、`short_name`、`display`。使用 `curl -s https://example.com/manifest.json | jq .` 验证。

**已弃用（跳过）：**

- `mstile-*.png`（Windows 图标）
- `safari-pinned-tab.svg`（自 macOS Big Sur 已弃用）
- `favicon-16x16.png` / `favicon-32x32.png`（由 `.ico` 和 `.svg` 覆盖）

**HTML 头验证：**

```bash
curl -s https://example.com/ | grep -iE 'rel="icon"|rel="apple-touch-icon"|rel="manifest"'
```

---

## 第 8 步：质量门槛

委托给 `addyosmani/web-quality-skills`。该技能涵盖 150 多项 Lighthouse 审计，涵盖性能、可访问性、SEO 和最佳实践。

- [ ] **全局 Unlighthouse 扫描**：`npx unlighthouse --site {site}`——扫描所有页面并在每个页面上运行 Lighthouse。在执行每个 URL 检查之前，先找出在任何一个维度上低于 90 的页面。
- [ ] Lighthouse 所有 4 个维度，移动模式：每个维度目标 ≥90（性能、可访问性、最佳实践、SEO）
- [ ] Lighthouse 所有 4 个维度，桌面模式：每个维度目标 ≥95
- [ ] 核心网络指标（CrUX 通过 PageSpeed Insights）的现场数据：LCP < 2.5 秒，INP < 200 毫秒，CLS < 0.1，移动和桌面均适用
- [ ] 可访问性（通过 `web-quality-skills` 的 WCAG 2.2 AA）：键盘导航适用于每个交互元素，焦点环可见，文本色对比度 ≥4.5:1，所有图片都有 `alt`，标题层级是单调的（H1 → H2 → H3），图标按钮上有 ARIA 标签
- [ ] 真实移动设备测试（不只是开发工具模拟器）。使用 Claude Chrome 扩展程序在真实设备上的移动视图中测试，或使用 BrowserStack。
- [ ] 跨浏览器冒烟测试：Chrome、Safari、Firefox 最新稳定版
- [ ] 打印样式表合理性（Cmd+P 不应破坏布局）

---

## 第 9 步：生态系统跨链接

在自有资产之间进行内部跨链接。对于任何多域所有者来说，这是高杠杆的 SEO 操作。

询问用户：“列出您生态系统中与这个新网站主题相关的其他域名。” 然后针对每个域名：

- [ ] 在现有网站（页脚 / 导航 / “其他项目”部分）中添加到新网站的链接，如果主题相关
- [ ] 在匹配的 GitHub 仓库的 README 中添加到新网站的链接，如果它记录了一个库
- [ ] 验证互惠链接：每个添加的链接都应适当返回
- [ ] 如果新网站记录了一个 Go 库，从相关库文档中添加链接

不要过度链接。仅在主题相关时进行跨链接。一个记录日志库的文档网站不应链接到一个关于骑自行车的个人博客。

---

## 第 10 步：设置每周 SEO 维护子代理

发布后，设置一个计划背景代理，例如 Hermes 或 Claude Cowork Routine，每周运行一次以监控 SEO 健康并暴露行动项。

参见 `references/weekly-seo-agent.md` 中的完整代理定义，每个 harness 都有具体对应项——将匹配您环境的块复制到指定的位置，在网站的仓库（或专门的 ops 仓库）中。该代理使用这些 MCP 连接器（或其等效 API 调用）：

- Ahrefs MCP（反向链接、排名、关键词）
- PostHog MCP（分析相关性、AI 机器人流量）
- 网络搜索（SERP 监控、竞争对手检查）
- Google Search Console（通过社区 MCP 或使用服务账户凭证的 `curl`）

**通过问题工具询问**在创建文件之前：“现在设置每周 SEO 代理？”（`yes-create-agent-file` | `yes-but-defer` | `skip-for-now`）。

当 MCP 不可用时，使用 Claude Chrome 扩展程序。

---

## 第 11 步：目录提交执行

执行来自 `directory-submissions` 技能的目录提交工作流。这是分发的基础层——永远不会是整个策略。

### 第 1 步：选择层级（参考 `references/directory-list.md`）

| 层级 | 时间 | 示例 | 典型数量 |
| --- | --- | --- | --- |
| **第 1 层 — 标志性发布** | 发布周仅限 | Product Hunt（锚点）、BetaList、HN Show HN、Fazier、DevHunt | ~15 |
| **第 2 层 — 创业公司/SaaS** | 第 1 周加滚动 | AlternativeTo、SaaSHub、G2、Capterra、F6S、SourceForge、Slashdot | ~50 |
| **第 3 层 — AI 目录** | 第 1–3 周 | TAAFT、Futurepedia、Toolify、Future Tools、aitools.inc、AIStage | ~40 |
| **第 4 层 — 代理/MCP 注册表** | 第 1–3 周（如果 MCP） | Glama、APITracker、LF MCP 注册表、AI Agents List | ~10 |
| **第 5 层 — 无代码目录** | 第 1–3 周（如果无代码） | NoCodeFinder、No Code MBA、We Are No Code、MakerPad | ~8 |
| **第 6 层 — “最佳”列表** | 滚动外联 | 向 DR 40+ 的博客进行冷外联 | ~10 次包含 |
| **第 7 层 — 集成市场** | 集成发布时 | Zapier、HubSpot、Slack、Airtable、Notion | ~5 |
| **第 8 层 — 个人资料和内容平台** | 滚动 | GitHub、WordPress.com、Substack、Dev.to、SlideShare、Behance | ~50 |
| **第 9 层 — 本地企业目录** | 滚动（如适用） | Manta、Hotfrog、Locanto、MerchantCircle | ~20 |
| **第 10 层 — 论坛和社区** | 滚动（先参与） | SitePoint、GrowthHackers、Warrior Forum、Designer News | ~13 |
| **第 11 层 — 新闻稿和文章网站** | 发布加里程碑 | PRLog、PR.com、EzineArticles、Feedspot | ~25 |
| **第 12 层 — 社交书签** | 滚动 | Scoop.it、Diigo、Pearltrees | ~5 |
| **第 13 层 — 垂直细分目录** | 当垂直匹配时 | Justia（法律）、Porch（住宅）、LandBook（设计）等 | ~20 |

**筛选规则：** 仅在产品是真实匹配的情况下提交。将列表强加到错误类别中会浪费首次提交的优势，并会被版主拒绝。

### 第 2 步：按层级准备资产变体

针对每个层级，准备一个独特的描述变体（来自 `references/positioning-variations.md`）：

- **标语** 10 个字以内
- **简短描述** 60 个字符
- **长描述** 150 字
- **5–8 分类标签**
- **标志** 资产
- **截图** + 演示视频 URL
- **创始人故事**（2–3 句话）

**关键：** 不要在所有目录中复制粘贴相同的长描述。每个层级都应变化开头句、功能重点和受众框架。AI 引擎会交叉引用并降低重复内容的权重。

### 第 3 步：批量提交并跟踪

设置跟踪电子表格（`references/submission-tracker-template.csv`）。从左到右通过它。每批 2–3 小时是现实的。

每个提交：

1. 复制层级适当的定位变体。
2. 填写表单。
3. 上传资产。
4. 提交。
5. 记录：日期、URL、状态、版主备注。
6. 活跃后，验证反向链接是否存在且为 dofollow：`curl -sIL https://directory.com/your-listing | grep -i rel=`。如果缺失，链接是 dofollow。

---

## 第 12 步：Product Hunt 深入分析（锚点事件）

Product Hunt 是单个最高杠杆的提交，但也最容易浪费。2026 年的 PH 算法更重视**评论质量**而不是点赞数——一个 50 个赞 + 30 个真实评论的帖子排名高于一个 200 个赞 + 5 个评论的帖子。**80% 的失败发布**是因为它们在没有温暖受众的情况下发布，或者请求点赞而不是反馈。

### 3 周准备时间表

- **第 -21 天到 -14 天：** 暖化猎手账户。每天对 3 个发布进行点赞 + 有思考地评论。关注 100 多个活跃制作者。为算法构建历史，使您的账户看起来真实。
- **第 -14 天：** 在 PH 上创建“即将发布”页面。将流量导向它以收集“发布时通知”订阅者。
- **第 -10 天：** （可选）预订猎手。不要用现金支付——用功能、喊话或介绍来交换。一个知名的猎手会增加第一天动力的 15%，但不是必需的。
- **第 -7 天：** 起草发布日资产：画廊图片（1270×760）、标语、260 字符描述、您自己的第一个评论、客户的第一个评论。
- **第 -3 天：** 邮件列表暖化。“我们周二发布。这里是什么可以期待。如果您想提前知道，请回复。”
- **第 -1 天：** 最终检查——产品在隐身模式下工作，视频自动播放，CTA 指向注册，PH 列表预览看起来正确。

### 发布日执行

- **太平洋时间凌晨 12:01 发布。** 周二、周三或周四——周末发布会获得 60–70% 的流量。太平洋时间 12:01 的开始时间最大化您的 24 小时窗口。
- **前 2 小时至关重要。** 需要 50 多个支持者在前 2 小时内触发算法分发。
- **自己发布第一个评论**，附上故事：为什么你创建了它，有什么不同，首先尝试什么。
- **在 30 分钟内回复每条评论**。PH 衡量制作者的响应能力。
- **分享链接到：** Twitter/X 帖子、LinkedIn 长篇帖子、个人 Slack/Discord 社区、您的邮件列表、Indie Hackers、通过 DM 的每个权力用户。
- **永远不要请求点赞。** 请求**反馈**。“希望您对定位有诚实的看法”的转化率比“支持我们！”高 3 倍，并且不会触发算法的反操纵过滤器。
- **不要联系陌生人。** 社区会标记这一点，版主会隐藏您的帖子。

### 发布后

- 写一篇发布回顾博客文章，包含数据和教训。诚实，不要炫耀。在第二天发布。
- 将回顾跨帖到 Indie Hackers 和 r/SaaS（在允许推广的地方）。
- 只有在您有**技术角度**要分享时才提交到 Show HN（例如架构、DSL、新方法）。一个通用的“我们发布了一个 SaaS”帖子会被标记为死亡。

---

## 第 13 步：评论策略（G2 / Capterra / TrustRadius）

G2 和 Capterra（截至 2026 年 2 月已归 G2 所有）列表**如果没有评论则毫无价值**。10 条评论是 Grid 出现的魔法阈值。在发布月期间运行 10 在 30 日的协议。

### 10 在 30 日的协议

1. **发布后第 1 天：** 确定 20 个已完成有意义的操作的产品用户。
2. **向每个发送一封个人邮件**，带有直接评论 URL（通过 ~70% 的摩擦减少）。没有表格，没有着陆页——直接链接。
3. **提供适度的感谢。** G2 和 TrustRadius 明确允许小额激励，如 25 美元的亚马逊礼品卡。
4. **跟进一次** 5 天后。不要跟进两次——它会变得令人烦恼并损害关系。
5. **目标：** 50% 转化率 → 从 20 个请求中获得 10 条评论。

### 关键截止日期

- **G2 夏季报告：** 截止日期约为 4 月 28 日。计划评论驱动以在截止日期前完成。
- **G2 秋季报告：** 截止日期约为 7 月 28 日。
- 错过截止日期意味着等待 3 个月才能获得下一个 Grid 更新。

### 徽章和付费计划

- **“用户喜欢我们”徽章** 仍然是免费的：需要 20 条评论，平均分 ≥4.0。
- **Grid、Momentum、Index 和 Award 徽章** 需要付费 G2 计划（从 2025 年夏季开始每年 2,999 美元起）。
- **第一年不要在 G2 上花费在付费上。** 免费列表 + Users Love Us 徽章就足够了。

### 跨平台

- TrustRadius 遵循类似的机制，但数量较小。
- Capterra 在某些类别中自动同步自 Gartner Digital Markets——可能无需直接操作即可填充。

---

## 第 14 步：发布后势头

您的发布不会因为公告发布而结束。现在需要采用和保留工作。不要依赖单一发布事件。定期更新和功能发布可以维持参与度。

### 立即发布后行动

- **教育新用户：** 设置自动化的入职邮件序列，介绍关键功能和用例。
- **强化发布：** 将公告包含在您的每周/双周/每月摘要邮件中，以捕捉错过的人。
- **与竞争对手区分开来：** 发布比较页面，突出显示为什么您是明显的选择。
- **更新网页：** 在您的网站上添加专门部分，介绍新的功能/产品。
- **提供动手预览：** 创建无代码交互式演示（使用 Navattic 等工具），以便访客在注册前可以探索。

### 如何确定要宣布什么

使用此矩阵来决定每个更新需要多少营销：

**重大更新**（新功能、产品改版）：

- 跨多个渠道进行完整活动
- 博客文章、邮件活动、应用内消息、社交媒体
- 最大化曝光

**中等更新**（新集成、UI 增强功能）：

- 针对性宣布
- 相关部分邮件、应用内横幅
- 不需要全部张扬

**小更新**（错误修复、小调整）：

- 更改日志和发布说明
- 表明产品正在改进
- 不要主导营销

### 宣布策略

- **分散发布：** 不要一次性发布所有内容，分阶段宣布以保持势头。
- **重用高绩效策略：** 如果之前的宣布产生了共鸣，请应用这些见解到未来的更新。
- **保持参与：** 继续使用邮件、社交和应用内消息来突出显示改进。
- **暗示积极开发：** 即使是小更改日志更新也会提醒客户您的产品正在发展。这建立了保留和口碑——客户确信您会继续存在。

---

## KPIs & 跟踪仪表板

每周跟踪。如果一个数字没有变化，请调查——不要只是提交更多目录。

| 指标                           | 第 0 天 | 第 30 天目标 | 第 90 天目标 |
| ----------------------------- | ----- | ------------- | ------------- |
| 域名权重 (DR)                  | 0     | 20            | 30+           |
| 外链域名数                      | 0     | 30            | 80+           |
| 已收录页面数                    | —     | 50            | 200+          |
| 每日自然点击量                  | 0     | 30            | 200+          |
| 已上架的目录列表                | 0     | 50            | 70+           |
| G2 评论数                       | 0     | 10            | 25            |
| Capterra 评论数                 | 0     | 5             | 15            |
| AI 引用（手动检查）             | 0     | 3             | 15+           |
| 来自目录推荐的注册数             | 0     | 50            | 300           |
| 来自替代方案/用例页面的注册数     | 0     | 20            | 300           |

---

## 不要做的事

1. **不要为目录提交服务付费**（60–200 美元的套餐）。这些目录提交本来就是免费的。只需一下午的复制粘贴即可。
2. **不要提交到垃圾目录**（DR 低于 10、无流量、无编辑质量的目录）。这会稀释你的外链概况，谷歌的垃圾信息检测可能会对你进行惩罚。
3. **不要使用错误的定位进行提交。** 重新阅读每个层级的定位表。通用的描述会浪费该列表资源。
4. **不要将目录视为你的整个 GTM（Go-To-Market，上市策略）。** 它们是基础。内容 + 社区 + 评论才是真正带来转化的因素。
5. **不要忽略在 G2/Capterra 上的评论。** 没有评论的列表是死列表。执行“30天10条评论”协议，否则就不要提交。
6. **不要要求在 Product Hunt 上点赞。** 2026 年的算法会对此进行惩罚。请要求提供**反馈**。
7. **不要每周修改旧的目录列表。** 提交一次，每季度检查一次即可。
8. **不要在目标页面存在之前提交。** 链接权重需要一个目标。
9. **不要在目录之间重复使用相同的描述。** AI 引擎会惩罚重复内容。
10. **不要在比较页面上撒谎。** AI 引擎会交叉参考并降低撒谎内容的排名。
11. **不要过度关注发布当天的流量峰值。** 飞轮效应是模板 + 替代方案 + 评论 + 持续内容——而不是 Product Hunt 上的一天。
12. **不要忘记 Crunchbase、LinkedIn 公司页面和 Wikidata。** 这些内容会输入 AI 训练语料库，对 GEO（生成式引擎优化）很重要。
13. **不要在通过 SLC 门槛之前发布。** “隐形模式”和“再加一个功能”都会扼杀发布。
14. **不要在营销文案上进行人工化润色。** 英雄区域、CTA、元描述和 OG 描述中的 AI 模式会损害可信度。
15. **不要假设分析工具“能正常工作”。** 在发布前使用 curl 验证每个集成——GA4、PostHog、GSC、Bing、Ahrefs。
16. **不要忽略备份演练。** 没有测试过的备份不是备份。在发布前恢复到预发环境。

---

## 输出格式

在完整运行结束后，按阶段分组输出状态报告：

```
阶段 1：域名与基础设施  [9/10 通过]
  ✓ Cloudflare 代理已开启
  ✓ DNS 记录已配置
  ...
  ✗ 缺少 DMARC。修复方法：在 _dmarc.example.com 添加策略为 v=DMARC1; p=quarantine;... 的 TXT 记录

阶段 2：分析与可观测性  [6/7 通过]
  ...
```

随后按顺序列出三个列表：

1. **阻塞项**（发布前必须修复）
2. **建议修复项**（公布前应修复）
3. **可选改进项**（发布后）

最后询问：“你想接下来处理哪个列表？” (`blockers` | `recommended` | `optional` | `done-for-now`)。

---

## 参考资料

- `references/decisions.md`：按站点类型划分的 AI 爬虫策略矩阵，可观测性层级矩阵
- `references/templates.md`：robots.txt、llms.txt、manifest.json、不同严格程度下的 CSP 模板，安全头参考
- `references/weekly-seo-agent.md`：每周 SEO 维护子代理的完整定义（MCP、任务、输出格式）
- `assets/weekly-seo-*.md`、`assets/weekly-seo-vibe.toml`：从 `references/weekly-seo-agent.md` 链接的每个框架的代理定义文件——复制与你框架匹配的文件
- `references/directory-list.md`：13 层级目录目录，包含提交时间、示例和数量
- `references/positioning-variations.md`：每个目录层级的定位变体库（标语、短/长描述、分类标签）
- `references/submission-tracker-template.csv`：用于记录目录提交的提交跟踪电子表格模板
