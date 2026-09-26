# 策略：网站结构

指导网站结构规划：需要构建哪些页面、页面优先级，以及结构如何支持用户体验、搜索引擎优化和增长。结构是页面的组织和连接方式；它影响用户导航、Google 对内容重要性的理解、可抓取性以及在搜索结果页面中的站点链接。有关站点链接和搜索结果页面优化的信息，请参阅 **serp-features**。

**调用时机**：在 **首次使用** 时，如果有帮助，先用 1-2 句话说明此技能涵盖的内容及其重要性，然后提供主要输出。在 **后续使用** 或用户要求跳过时，直接进入主要输出。

## 初步评估

**首先检查项目背景**：如果存在 `.claude/project-context.md` 或 `.cursor/project-context.md`，请阅读它以了解产品类型、受众和增长目标。

识别：
1. **网站类型**：产品/SaaS、B2B、电子商务、作品集、论坛、目录
2. **阶段**：新网站（从零开始规划）或现有网站（扩展或审计）
3. **增长策略**：联盟营销、教育、多语言、社区、B2B、开发者
4. **限制条件**：团队规模、预算、技术栈

## 页面优先级框架

按优先级规划页面，用于开发排期。有关完整页面类型和网站类型映射，请参阅 [skills-reference §2 页面分类](../../../docs/skills-reference.md#2-page-taxonomy)。

| 优先级 | 页面 | 备注 |
|--------|------|------|
| **必须拥有** | 首页、产品/功能、定价、博客、关于我们、隐私政策、条款、联系方式 | 对信任和转化至关重要；定价：导航中的公共页面，用于自助服务；企业专属可能使用“联系销售”替代；参见 **pricing-page-generator**（可见性与位置） |
| **很好拥有** | 用户评价、常见问题解答、站点地图（HTML）、404页面、退款/退货 | 支持用户体验和搜索引擎优化 |
| **可选** | 搜索结果、新闻、职业发展、信息披露 | 情境性 |
| **流量驱动** | 分类/集合页面 | 适用于内容密集型或电子商务；需要分类 + 标签 |

## 通用模板结构

适用于SaaS、工具和内容网站。通过删除未使用的节点（例如，没有API则删除 /api、/docs）并添加特定模块（例如，行业、地区）进行适配。

| 部分 | 典型路径 | 页面技能 |
|------|----------|----------|
| **根目录** | /, /features, /pricing, /demo, /contact | homepage-generator、features-page-generator、pricing-page-generator |
| **工具** | /tools, /free-tools；中心 + 每个工具页面 | tools-page-generator；免费工具用于获取潜在客户；通常是单页应用；程序化；参见 **programmatic-seo** |
| **资源** | /blog, /changelog, /glossary, /faq, /教程 | blog-page-generator、changelog-page-generator、glossary-page-generator、faq-page-generator |
| **合作伙伴关系** | /affiliate, /startups, /ambassadors | affiliate-page-generator、landing-page-generator |
| **法律** | /terms, /privacy, /careers | terms-page-generator、privacy-page-generator、careers-page-generator |
| **竞争对手** | /alternatives, /compare, /migrate | alternatives-page-generator、migration-page-generator |
| **独立页面** | /dashboard, /login, /signup, /docs, /api, /status, /support | signup-login-page-generator、docs-page-generator、api-page-generator、status-page-generator |

## 增长策略 → 结构映射

结构反映增长策略。子目录表示渠道：

| 目标 | 路径示例 | 页面/渠道 |
|------|----------|----------|
| 联盟营销转化 | /affiliate | affiliate-page-generator |
| 教育学生计划 | /education, /startups, /student-discount | education-program、startups-page-generator |
| 多语言 | /zh-CN, /ja | localization-strategy |
| 社区 | /ambassadors, /showcase | creator-program、landing-page-generator |
| B2B / 企业 | 解决方案（按行业优先）、用例（按场景优先；可以是子页面）、客户故事 | solutions-page-generator、use-cases-page-generator、customer-stories-page-generator |
| 开发者产品 | /api, /docs, /status | api-page-generator、docs-page-generator、status-page-generator |
| 用户反馈 | 反馈、路线图 | feedback-page-generator；外部（Canny、FeatureBase） |
| 插件/集成 | /integrations, /plugins | integrations-page-generator、category-page-generator |
| 赠品/竞赛 | /giveaway | contest-page-generator |

## 域名结构（多个产品）

在规划多个产品或品牌时，请参阅 **domain-architecture** 以了解子文件夹与子域名与独立域名的区别。此技能涵盖单个域名内的页面结构。有关初始域名选择（品牌 vs PMD vs EMD，TLD），请参阅 **domain-selection**。

## 规划工作流程

1. **选择模板**：从通用结构开始；映射到 [skills-reference §2](../../../docs/skills-reference.md#2-page-taxonomy) 网站类型
2. **删除模块**：删除无关节点（例如，没有API则删除 /api、/docs）
3. **添加特定内容**：行业页面、地区、产品变体
4. **分配URL**：每个节点；遵循 **url-structure**（小写、连字符、简短、关键词丰富）
5. **导出列表**：“页面类型 + URL + 优先级”用于开发排期
6. **技术栈**：将页面类型匹配到服务（DNS、认证、CMS、状态页面等）
7. **迭代**：随新功能、市场扩展；保持结构清晰

## 结构原则

| 原则 | 指导方针 |
|------|----------|
| **扁平结构** | 从首页到任何页面的点击次数最多为4次；提高可抓取性和权重分布 |
| **早期规划** | 在增长之前规划结构；可以在域名购买后立即开始 |
| **站点链接** | 良好结构 + 目录 + 权威内部链接 → 搜索结果页面中的自然站点链接（无法通过模式强制）；参见 **serp-features** |
| **防止孤立页面** | 每个页面都需要内部链接；参见 **site-crawlability** 和 **internal-links** |
| **功能 vs 用例** | /features = 按能力优先；/use-cases = 按场景优先；区分内容角度，相互链接，避免重叠；参见 **features-page-generator**、**use-cases-page-generator** |
| **清晰的导航** | 清晰的层次结构和导航提高任务完成率；用户能更快找到所需内容；参见 **navigation-menu-generator** |
| **定价位置** | 营销网站：/pricing 在主导航中，用于潜在客户；应用内：设置 → 订阅在侧边栏中，用于已登录用户（订阅管理）。企业专属：“联系销售”可能替代公共定价页面；参见 **pricing-page-generator** |

## 首页模块参考

有关常见模块（标题、副标题、CTA、优势、社会证明等）、导航选项，以及 **hero-generator** 的英雄设计，请参阅 **homepage-generator**。

## 输出格式

- **页面列表**，包含优先级（必须拥有 / 很好拥有 / 可选）
- **URL结构**（每个部分的路径）
- **网站类型适配**（每个 [skills-reference §2](../../../docs/skills-reference.md#2-page-taxonomy) 适用的页面）
- **增长映射**（哪些路径支持哪些渠道）
- **下一步**：url-structure 用于URL规则；xml-sitemap 用于提交；site-crawlability 用于审计

## 参考文献

- [网站结构SEO指南](https://alignify.co/zh/seo/website-structure) — Alignify：结构重要性、页面优先级、通用模板、规划工作流程、增长映射、首页模块
- **skills-reference §2** (docs/skills-reference.md#2-page-taxonomy) — 完整页面类型、网站类型矩阵、核心与扩展；用于页面选择

## 相关技能

- **seo-strategy**：SEO工作流程顺序；结构规划适合在技术阶段之前
- **domain-selection**：初始域名选择；在结构规划时选择域名之前
- **domain-architecture**：子文件夹与子域名与独立；如果域名决策悬而未决，则在结构规划之前
- **url-structure**：URL优化、层次结构、别名；在结构定义后应用
- **site-crawlability**：可抓取性、孤立页面、重定向；审计现有结构
- **internal-links**：链接策略、中心辐射；在页面存在后实施
- **xml-sitemap**：站点地图创建；包含计划URL
- **breadcrumb-generator**：层次结构面包屑；大型网站、电子商务
- **navigation-menu-generator**：导航设计；主要、页脚、移动
- **content-strategy**：内容集群、支柱页面；补充结构规划
