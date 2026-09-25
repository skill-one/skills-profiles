# AI 代理的营销技能

> 技能由 [ara.so](https://ara.so) 提供 — 2026 每日技能集合。

[coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) 是一个基于 markdown 的 AI 代理技能集合，涵盖 CRO（转化率优化）、文案写作、SEO（搜索引擎优化）、分析、付费广告、电子邮件和增长工程。安装一次后，任何兼容的代理（Claude Code、Cursor、Codex、Windsurf）都能获得专业的营销专长和框架。

---

## 技能如何工作

每个技能都是一个 markdown 文件，它告诉 AI 代理：
- **何时激活**（触发短语）
- **应用哪些框架**（例如 AIDA、PAS、Jobs-to-be-Done）
- **生成什么内容**（文案、代码、审核、策略）
- **参考哪些其他技能**（跨技能依赖）

所有技能首先读取 `product-marketing-context` — 它是包含您的产品、受众和定位的共享基础。

---

## 安装

### 选项 1：CLI（推荐）

```bash
# 一次性安装所有 33 个技能
npx skills add coreyhaines31/marketingskills

# 仅安装特定技能
npx skills add coreyhaines31/marketingskills --skill page-cro copywriting seo-audit

# 安装前查看所有可用技能
npx skills add coreyhaines31/marketingskills --list
```

技能将安装到 `.agents/skills/`，并为 Claude Code 创建一个指向 `.claude/skills/` 的软链接。

### 选项 2：Claude Code 插件

```
/plugin marketplace add coreyhaines31/marketingskills
/plugin install marketing-skills
```

### 选项 3：Git 克隆

```bash
git clone https://github.com/coreyhaines31/marketingskills.git
cp -r marketingskills/skills/* .agents/skills/
```

### 选项 4：Git 子模块（用于团队项目）

```bash
git submodule add https://github.com/coreyhaines31/marketingskills.git .agents/marketingskills
# 从 .agents/marketingskills/skills/ 引用技能
```

---

## 项目结构

```
marketingskills/
├── skills/
│   ├── product-marketing-context/   ← 从这里开始 — 所有其他技能的基础
│   ├── page-cro/
│   ├── copywriting/
│   ├── seo-audit/
│   ├── ab-test-setup/
│   ├── email-sequence/
│   ├── paid-ads/
│   └── ... (共 33 个技能)
└── README.md
```

每个技能目录包含一个 `SKILL.md`（或 `README.md`），代理会读取其中的结构化指令。

---

## 第一步：设置产品营销上下文

在使用任何其他技能之前，创建您的上下文文件。这是最重要的一步。

```
"创建我的产品营销上下文"
```

代理将通过询问以下内容来生成 `.agents/skills/product-marketing-context/context.md`：
- 产品名称、描述和类别
- 目标受众和 ICP（客户画像）
- 核心价值主张和定位
- 主要竞争对手
- 定价和商业模式
- 语气和品牌声音

其他每个技能在执行前都会自动读取此文件。

---

## 可用技能参考

### 基础
| 技能 | 使用场景 |
|-------|----------|
| `product-marketing-context` | 创建或更新您的共享产品/定位文档 |

### SEO & 内容
| 技能 | 使用场景 |
|-------|----------|
| `seo-audit` | 审核或诊断 SEO 问题 |
| `ai-seo` | 优化 LLM/AI 搜索引用 |
| `site-architecture` | 规划 URL 结构、导航、内部链接 |
| `programmatic-seo` | 从模板 + 数据大规模构建 SEO 页面 |
| `schema-markup` | 添加结构化数据 / JSON-LD |
| `content-strategy` | 规划要创建的内容及其原因 |

### CRO（转化率优化）
| 技能 | 使用场景 |
|-------|----------|
| `page-cro` | 优化任何营销或着陆页 |
| `signup-flow-cro` | 改进注册/试用激活流程 |
| `onboarding-cro` | 改进注册后激活和价值实现时间 |
| `form-cro` | 优化线索捕获、联系或非注册表单 |
| `popup-cro` | 创建或改进弹窗、模态框、滑入 |
| `paywall-upgrade-cro` | 应用内付费墙、升级屏幕、功能门 |

### 文案 & 内容
| 技能 | 使用场景 |
|-------|----------|
| `copywriting` | 编写主页、着陆页或任何营销文案 |
| `copy-editing` | 编辑或改进现有文案 |
| `cold-email` | 编写 B2B 冷接触序列 |
| `email-sequence` | 构建滴灌、生命周期或注册后电子邮件 |
| `social-content` | LinkedIn、Twitter/X、Instagram 内容 |

### 付费 & 测量
| 技能 | 使用场景 |
|-------|----------|
| `paid-ads` | Google Ads、Meta、LinkedIn、Twitter 营销活动 |
| `ad-creative` | 生成广告标题、描述、主要文本 |
| `ab-test-setup` | 规划和实施 A/B 实验 |
| `analytics-tracking` | 设置或审核 GA4、Segment、Mixpanel |

### 增长 & 留存
| 技能 | 使用场景 |
|-------|----------|
| `referral-program` | 构建推荐或联盟计划 |
| `free-tool-strategy` | 规划免费工具用于线索生成或 SEO |
| `churn-prevention` | 取消流程、保留优惠、催收 |
| `lead-magnets` | 创建电子邮件捕获线索磁铁 |

### 销售 & GTM
| 技能 | 使用场景 |
|-------|----------|
| `revops` | 线索生命周期、CRM、营销到销售交接 |
| `sales-enablement` | 演示文稿、单页、异议处理 |
| `launch-strategy` | 产品发布、功能公告 |
| `pricing-strategy` | 定价、包装、变现决策 |
| `competitor-alternatives` | 比较和替代页面 |

### 策略
| 技能 | 使用场景 |
|-------|----------|
| `marketing-ideas` | 头脑风暴营销策略和技巧 |
| `marketing-psychology` | 将行为科学应用于营销 |

---

## 使用示例

### 示例 1：审核并改进着陆页

```
"审核我的着陆页 src/pages/index.tsx 并提出 CRO 改进建议"
```

代理读取 `product-marketing-context`，激活 `page-cro`，然后：
1. 审核页面结构、标题、CTA 位置
2. 应用框架（AIDA、视窗分析、社会证明审核）
3. 输出优先级更改列表及实现代码

### 示例 2：从零开始编写主页

```
"使用文案写作技能为我的 SaaS 产品编写主页文案"
```

输出包括英雄标题变体、副标题、功能部分、社会证明块和 CTA — 所有内容均基于您的 `product-marketing-context`。

### 示例 3：设置 A/B 测试

```
"帮助我为我的定价页 CTA 按钮设置 A/B 测试"
```

代理激活 `ab-test-setup` 并生成：

```javascript
// 示例输出：Google Optimize / 自定义 A/B 测试脚手架
const experiments = {
  pricing_cta_test: {
    id: 'pricing-cta-v1',
    variants: [
      { id: 'control', cta: '免费试用' },
      { id: 'variant_a', cta: '立即开始免费' },
      { id: 'variant_b', cta: '免费试用 — 无需信用卡' }
    ],
    metric: 'signup_click',
    minimumDetectableEffect: 0.05,
    confidenceLevel: 0.95
  }
};

// 按用户 ID 确定性地分配流量
function getVariant(userId, experimentId) {
  const hash = simpleHash(`${userId}-${experimentId}`);
  const variantIndex = hash % experiments[experimentId].variants.length;
  return experiments[experimentId].variants[variantIndex];
}
```

### 示例 4：生成程序化 SEO 页面

```
"为 '[工具] 替代品' 页面创建程序化 SEO 页面模板"
```

代理激活 `programmatic-seo` + `competitor-alternatives` 并构建：

```javascript
// Next.js 动态路由：/pages/[competitor]-alternatives.js
export async function getStaticPaths() {
  const competitors = await fetchCompetitors(); // 您的数据源
  return {
    paths: competitors.map(c => ({ params: { competitor: c.slug } })),
    fallback: 'blocking'
  };
}

export async function getStaticProps({ params }) {
  const data = await getCompetitorData(params.competitor);
  return { props: { competitor: data }, revalidate: 86400 };
}
```

### 示例 5：构建电子邮件序列

```
"为新的试用用户编写 5 封注册后电子邮件序列"
```

激活 `email-sequence` + `onboarding-cro`。生成：
- 电子邮件 1：欢迎 + 单一激活操作（第 0 天）
- 电子邮件 2：价值强化 + 功能亮点（第 2 天）
- 电子邮件 3：社会证明 / 案例研究（第 4 天）
- 电子邮件 4：克服异议 / 常见问题解答（第 6 天）
- 电子邮件 5：试用结束 + 升级 CTA（第 8 天）

每封邮件都包含主题行、预览文本、正文文案和 CTA。

### 示例 6：SEO 的模式标记

```
"在我的博客页面模板中添加模式标记"
```

```javascript
// 输出：JSON-LD for Article schema
const articleSchema = {
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": post.title,
  "description": post.excerpt,
  "author": {
    "@type": "Person",
    "name": post.author.name,
    "url": post.author.url
  },
  "datePublished": post.publishedAt,
  "dateModified": post.updatedAt,
  "publisher": {
    "@type": "Organization",
    "name": process.env.SITE_NAME,
    "logo": {
      "@type": "ImageObject",
      "url": process.env.SITE_LOGO_URL
    }
  }
};
```

---

## 技能跨引用（依赖关系图）

在处理任务时，代理可能会一起激活多个技能：

```
着陆页优化：
  page-cro → copywriting → ab-test-setup → analytics-tracking

SEO 内容策略：
  seo-audit → content-strategy → ai-seo → schema-markup

销售管道：
  revops → sales-enablement → cold-email → email-sequence

增长循环：
  free-tool-strategy → programmatic-seo → referral-program → analytics-tracking
```

您可以显式调用多个技能：

```
"使用 page-cro 和 copywriting 技能重写我的 /定价 页面"
"应用营销心理学和文案写作到我的结账流程"
```

---

## 配置

无需配置文件。技能是自包含的 markdown 文件。唯一的配置是您的 `product-marketing-context` 文档。

要随时更新您的上下文：

```
"更新我的产品营销上下文 — 我们刚刚将目标受众更改为企业"
```

---

## 添加自定义技能

按照相同模式创建新的技能目录：

```bash
mkdir .agents/skills/my-custom-skill
cat > .agents/skills/my-custom-skill/SKILL.md << 'EOF'
---
name: my-custom-skill
description: 这个技能的作用
triggers:
  - 激活这个技能的短语
---

# 我的自定义技能

## 使用场景
...

## 流程
...

## 相关技能
- product-marketing-context (始终首先读取)
EOF
```

---

## 贡献

```bash
git clone https://github.com/coreyhaines31/marketingskills.git
cd marketingskills

# 添加新技能
mkdir skills/my-new-skill
# 按照现有技能格式创建 skills/my-new-skill/README.md

# 更新 README.md 中的技能表格
# 打开一个 PR
```

`README.md` 技能表格在 `<!-- SKILLS:START -->` 和 `<!-- SKILLS:END -->` 标记之间自动生成。

---

## 故障排除

**技能在 Claude Code 中未激活**
```bash
# 验证软链接是否存在
ls -la .claude/skills/
# 如果缺失，重新运行安装
npx skills add coreyhaines31/marketingskills
```

**代理忽略产品上下文**
- 确保 `.agents/skills/product-marketing-context/context.md` 存在
- 如果缺失：`"创建我的产品营销上下文"` 以重新生成它

**仅安装特定技能**
```bash
npx skills add coreyhaines31/marketingskills --skill copywriting page-cro seo-audit analytics-tracking
```

**更新到最新技能**
```bash
npx skills update coreyhaines31/marketingskills
# 或如果使用子模块：
git submodule update --remote .agents/marketingskills
```

**技能与其他已安装技能包冲突**
- 技能按目录命名空间化 — 不预期冲突
- 如果代理激活了错误的技能，请显式指定：`"使用 marketingskills 的 page-cro 技能"`

---

## 资源

- [Agent Skills spec](https://agentskills.io) — 这些技能遵循的标准
- [Coding for Marketers](https://codingformarketers.com) — 非技术人员指南
- [Conversion Factory](https://conversionfactory.co) — Corey 的 CRO 机构
- [Swipe Files](https://swipefiles.com) — 营销简报
- [Magister](https://magistermarketing.com) — 使用这些技能的自主 AI CMO
- [Issues](https://github.com/coreyhaines31/marketingskills/issues) — 获取帮助或报告错误
