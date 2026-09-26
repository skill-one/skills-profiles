# 竞争对手分析

分析竞争对手的 SEO 和 GEO 策略，揭示可重复的胜利、弱点和市场空白。

## 快速入门

```
分析 [竞争对手 URL] 的 SEO 策略
```

```
将我的网站 [URL] 与 [竞争对手 1]、[竞争对手 2]、[竞争对手 3] 进行比较
```

## 技能合约

**预期输出**：优先级竞争对手简报和 `memory/research/` 的标准交接摘要。

- **读取**：竞争对手 URL/域名、您自己的网站指标、商业模式、目标受众、行业背景以及任何用户提供的或工具数据。
- **写入**：面向用户的分析和可重用的摘要。
- **推广**：持久的竞争对手事实、关键词优先级、实体候选者和待定策略决策到 `memory/hot-cache.md`、`memory/open-loops.md` 和 `memory/research/`。
- **完成条件**：在一个比较表中，针对关键词、反向链接和流量份额对 3-5 个竞争对手进行基准测试；每个需要学习的优势和需要利用的弱点都引用证据；并且可交付成果以即时/短期/长期计划结束。
- **主要后续技能**：当竞争格局清晰时，[content-gap-analysis](../content-gap-analysis/SKILL.md)。

### 交接摘要

> 从 [skill-contract.md §交接摘要格式](../../../references/skill-contract.md) 发出标准形状。

## 数据来源

可选集成：~~SEO 工具、~~分析、~~AI 监控。没有工具时，请要求提供竞争对手 URL、您自己的网站指标和行业背景。参见 [CONNECTORS.md](../../../CONNECTORS.md)。

**零依赖竞争对手抓取（无密钥）**：`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/connectors/firecrawl.py" scrape <competitor-url>` 返回 LLM 准备好的渲染页面（包括 JavaScript 重的页面），`firecrawl.py map <competitor-domain> --limit 500` 快速清点其 URL 表面，`firecrawl.py search "<品牌或主题>" --tbs qdr:m` 找到他们最新的报道 — 所有这些都基于 Firecrawl 的无密钥免费套餐（~每月 1,000 个信用点）。连接器在本地预飞目标的 robots.txt 并根据 [SECURITY.md §抓取边界](../../../SECURITY.md) 中的 Disallow 拒绝。参见 [scripts/connectors/README.md](../../../scripts/connectors/README.md)。

## 决策关卡

**停止并询问** — 当无法建立竞争对手集合时：

1. 未命名任何竞争对手，也无法从 `CLAUDE.md`、先前研究或用户的细分市场推断出任何竞争对手 → 要求用户命名 2-5 个竞争对手，或通过 [serp-analysis](../serp-analysis/SKILL.md) 首先从目标关键词推断它们。

**静默继续** — 不要停止：对于较长的列表中选择 3-5 个进行深度挖掘（选择最直接的竞争对手并注明其余的）；缺少您自己的网站指标（将竞争对手相互基准测试并标记您的行 N/A）；缺少可选工具数据（标记为估计值并继续）。

## 指令

当用户请求竞争对手分析时：

1. **识别竞争对手** — 如果用户尚未命名，则分离直接竞争对手、间接替代品和内容竞争对手。
2. **收集竞争对手数据** — 捕获 URL、域名年龄、估计流量、域名权威性、商业模式、目标受众和关键产品。
3. **分析关键词排名** — 记录总排名、前 10/前 3 计数、高价值关键词、意图组合和关键词空白。
4. **审核内容策略** — 审查内容量、顶级表现者、发布模式、主题和成功因素。
5. **分析反向链接概况** — 审查反向链接总数、质量组合、顶级链接域名、链接获取模式和可链接资产。
6. **技术 SEO 评估** — 评估核心网络指标、移动友好性、架构、内部链接、URL 结构和突出的优势/弱点。
7. **GEO / AI 引用分析** — 测试哪些查询引用竞争对手，哪些格式被引用，以及竞争对手仍然留下的空白。
8. **综合竞争情报** — 提供执行摘要、比较表、CITE 比较表、需要学习的优势、需要利用的弱点、关键词机会、内容建议和即时/短期/长期计划。

将每个指标标记为 **测量**（工具/导出）、**用户提供** 或 **估计**（模型推断）；永远不要将估计值呈现为测量值；如果缺少必要的指标，请标记为 N/A — 不要编造它。

**质量标准**：每个优势或弱点都与标记的指标和命名的竞争对手相关联 — 为命名域名提供具体的排名或反向链接数字，而不是“强大的内容存在”。

> **参考**：参见 [Analysis Templates](references/analysis-templates.md) 以获取在每个步骤中使用的紧凑模板。

## 示例

参见 [references/example-report.md](references/example-report.md) 以获取一个完整分析 HubSpot 营销关键词主导地位的示例。

## 高级分析类型

### 内容差距分析

对于成对的主题覆盖差距地图（“内容 [竞争对手] 有而我没有，按流量潜力排序”），转交给 [content-gap-analysis](../content-gap-analysis/SKILL.md) — 那是它专门的工作。

### 视频基准测试

当竞争对手投资视频时，基准测试他们的 YouTube 异常值（观看次数 >=2 倍其频道平均数）以及推动这些胜利的标题/缩略图包装 — 这些模式显示了哪些主题和框架赚取了覆盖范围。参见 [platforms/youtube.md](../../../references/platforms/youtube.md)。

### 链接交集

```
查找同时链接到 [竞争对手 1] 和 [竞争对手 2] 但不链接到我 的网站
```

### SERP 功能分析

```
竞争对手在哪些 SERP 功能中获胜？（精选片段、PAA 等）
```

### 历史跟踪

```
过去一年 [竞争对手] 的 SEO 策略如何演变？
```

## 保存结果

写入路径：`memory/research/competitor-analysis/YYYY-MM-DD-<主题>.md`；将持久的竞争对手事实和实体候选者推广到 `memory/hot-cache.md`。参见 [Skill Contract](../../../references/skill-contract.md) §保存结果模板。

## 参考资料

- [Analysis Templates](references/analysis-templates.md) — 步骤分析模板
- [Battlecard Template](references/battlecard-template.md) — 快速参考战斗卡格式
- [Positioning Frameworks](references/positioning-frameworks.md) — 定位和差异化框架
- [Example Report](references/example-report.md) — 工作示例
- [platforms/youtube.md](../../../references/platforms/youtube.md) — 视频密集型竞争对手的 YouTube 异常值和标题包装基准测试

## 下一个最佳技能

主要：[content-gap-analysis](../content-gap-analysis/SKILL.md)。此外：[serp-analysis](../serp-analysis/SKILL.md) 和 [offsite-signal-analyzer](../../evaluate/offsite-signal-analyzer/SKILL.md)。如果目标是“我们 vs 他们”的页面，将经过审核的竞争对手集合交给 [page-play-builder](../../implement/page-play-builder/SKILL.md)。
