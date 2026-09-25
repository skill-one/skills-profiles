# 市场营销技能 — 指南 + 路由器

这是市场营销插件的索引技能。它只做一件工作：将你路由到正确的专业技能，然后退出。对于按请求路由的逻辑，[../marketing-ops/SKILL.md](../marketing-ops/SKILL.md) 是标准的路由器——这个文件是地图。

**计数（保持诚实）：** `skills/` 中的 44 个专业技能（加上这个索引和已弃用的 `content-creator` 重定向），`video-content-strategist/` 中的 1 个视频技能，59 个仅使用 stdlib 的 Python 工具。不需要 pip 安装。

## 从这里开始

1. **首次运行？** 使用 `skills/marketing-context/` 创建 `.claude/product-marketing-context.md`。其他所有技能都会读取它以获取品牌声音、角色和竞争格局。
2. **知道你的任务？** 在下面的路由表中找到它，并仅加载该技能的 `SKILL.md`。
3. **模糊请求？** 加载 `skills/marketing-ops/`——其路由矩阵将短语映射到技能。

## 路由表

所有路径都是相对于 `marketing-skill/` 的。

### 基础 + 运营
| 任务 | 技能 |
|---|---|
| 捕获品牌/产品上下文（首先运行） | `skills/marketing-context/` |
| 路由请求、规划活动、选择渠道 | `skills/marketing-ops/` |
| 需求生成计划、漏斗 + CRM 运营 | `skills/marketing-demand-acquisition/` |
| 定位、ICP、产品营销策略 | `skills/marketing-strategy-pmm/` |
| 品牌声音/视觉一致性审核 | `skills/brand-guidelines/` |

### 内容
| 任务 | 技能 |
|---|---|
| 撰写博客文章、文章、指南 | `skills/content-production/` |
| 规划要创建的内容 | `skills/content-strategy/` |
| 编辑文案（七次扫过） | `skills/copy-editing/` |
| 修复听起来像 AI 的内容 | `skills/content-humanizer/` |
| 落地页/销售页文案 | `skills/copywriting/` |
| 标题、钩子、想法生成 | `skills/marketing-ideas/` |
| 说服框架、心智模型 | `skills/marketing-psychology/` |

### SEO + AEO
| 任务 | 技能 |
|---|---|
| 传统 SEO 审核工具 | `skills/seo-audit/` |
| AI 搜索引用（ChatGPT、Perplexity、AI Overviews） | `skills/aeo/` |
| 大规模程序化 SEO | `skills/programmatic-seo/` |
| 结构化数据 / schema.org | `skills/schema-markup/` |
| 网站结构、内部链接 | `skills/site-architecture/` |

### CRO（转化）
| 任务 | 技能 |
|---|---|
| 落地页/营销页转化 | `skills/page-cro/` |
| 表单 | `skills/form-cro/` |
| 注册流程 | `skills/signup-flow-cro/` |
| 引导/激活 | `skills/onboarding-cro/` |
| 弹窗/模态框 | `skills/popup-cro/` |
| 付费墙/升级屏幕 | `skills/paywall-upgrade-cro/` |
| A/B 测试设计 + 样本量 | `skills/ab-test-setup/` |

### 渠道
| 任务 | 技能 |
|---|---|
| 邮件序列/滴灌 | `skills/email-sequence/` |
| 冷呼出邮件 | `skills/cold-email/` |
| 付费广告（Google/Meta/LinkedIn） | `skills/paid-ads/` |
| 广告创意 + 文案 | `skills/ad-creative/` |
| 社交日历 + 管理 | `skills/social-media-manager/` |
| 平台原生社交帖子 | `skills/social-content/` |
| X/Twitter 增长 | `skills/x-twitter-growth/` |
| YouTube（数据 + 策略） | `skills/youtube-full/` |
| 视频内容策略 | `video-content-strategist/`（兄弟文件夹，独立插件） |
| 网络研讨会（漏斗数学） | `skills/webinar-marketing/` |
| App Store / Play Store (ASO) | `skills/app-store-optimization/` |

### 增长
| 任务 | 技能 |
|---|---|
| 发布（PH、HN 等） | `skills/launch-strategy/` |
| 定价 + 包装 | `skills/pricing-strategy/` |
| 推荐计划 | `skills/referral-program/` |
| 免费工具作为获取 | `skills/free-tool-strategy/` |
| 客户流失预防 | `skills/churn-prevention/` |

### 智能分析 + 销售赋能
| 任务 | 技能 |
|---|---|
| 活动表现、归因 | `skills/campaign-analytics/` |
| 跟踪计划、UTM、GA4 关键事件 | `skills/analytics-tracking/` |
| 社交账户分析 | `skills/social-media-analyzer/` |
| 竞争对手/替代页 | `skills/competitor-alternatives/` |
| 营销团队 LLM 提示模板 + 治理 | `skills/prompt-engineer-toolkit/` |

## Python 工具

每个技能在其 `SKILL.md` 中记录自己的工具（一个“工具”或工作流部分，包含确切的 CLI 行）。从技能的文件夹中调用：

```bash
python3 skills/<skill>/scripts/<tool>.py --help
```

所有 59 个脚本都是仅使用 stdlib 的；大多数不带参数运行一个演示。

## 规则

- 每个任务加载一个专业技能——不要批量加载。
- 如果存在 `.claude/product-marketing-context.md`，则在任何市场营销任务之前读取它。
- `content-creator` 已弃用——使用 `skills/content-production/`。
- 不要为这些工具 pip 安装任何东西。
