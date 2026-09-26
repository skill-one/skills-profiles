# 内容差距分析

通过将您的网站与竞争对手进行比较，识别内容机会，并对优先关闭的差距进行评分。

## 快速入门

```
查找我的网站 [URL] 和 [竞争对手 URL] 之间的内容差距
```

```
与我的前 3 名竞争对手相比，我缺少哪些内容？
```

## 技能合同

**预期输出**：一个优先级差距简报以及 `memory/research/` 的标准交接摘要。

- **读取**：您的域名、竞争对手域名、主题/内容类型重点、受众、业务目标以及任何用户提供的或工具内容清单。
- **写入**：面向用户的分析和可重用的摘要。
- **促进**：持久的优先级关键词、竞争对手事实和待定策略决策到 `memory/hot-cache.md`、`memory/open-loops.md` 和 `memory/research/`。
- **完成时**：每个优先级差距都指明了覆盖该内容的竞争对手，而您没有覆盖；差距被分为快速获胜 / 战略构建 / 长期；交付成果包括每个快速获胜的日期内容日历条目。
- **主要后续技能**：当优先级差距列表获得批准时，[content-writer](../../implement/content-writer/SKILL.md)。

### 交接摘要

> 从 [skill-contract.md §交接摘要格式](../../../references/skill-contract.md) 发出标准形状。

## 数据来源

可选集成：~~SEO 工具、~~搜索控制台、~~分析、~~AI 监控。没有工具时，请提供网站 URL、内容清单、竞争对手 URL 和业务目标。参见 [CONNECTORS.md](../../../CONNECTORS.md)。

**作为差距发现输入的趋势侦察（无密钥）**：将多源趋势侦察——Google Trends RSS 加上 Hacker News 和 Reddit，通过 [`scripts/connectors/rss_monitor.py`](../../../scripts/connectors/rss_monitor.py)——输入以揭示您和竞争对手可能都遗漏的上升主题。将每个命中视为候选差距，然后根据步骤 5-7 检查您和竞争对手的覆盖范围。标记这些信号 **估计**。参见 [CONNECTORS.md](../../../CONNECTORS.md) `~~趋势数据库`。

**无密钥竞争对手覆盖清单**：`python3 "${CLAUDE_PLUGIN_ROOT}/scripts/connectors/firecrawl.py" map <竞争对手域名> --search "<主题>" --limit 1000` 列出按主题相关性排序的竞争对手 URL——步骤 5-7 的快速 **测量** 覆盖清单——以及 `firecrawl.py scrape <url>` 读取任何候选页面作为渲染的 markdown。robots.txt 在本地预检；拒绝根据 [SECURITY.md §抓取边界](../../../SECURITY.md) 的 Disallow。Firecrawl 无密钥免费套餐 (~1,000 信用点/月)。参见 [scripts/connectors/README.md](../../../scripts/connectors/README.md)。

## 决策关卡

**停止并询问**——差距分析是相对于竞争对手的，不能仅靠按需运行：

1. 未提供竞争对手域名且无法从 `CLAUDE.md` 或先前研究中推断出任何域名 → 要求用户命名 1-3 名竞争对手，或提供切换到 [keyword-research](../keyword-research/SKILL.md) 以进行需求侧发现。
2. 您的域名/内容清单不可用且无法获取 → 要求提供网站 URL 或内容列表，因为“差距”需要知道当前覆盖范围。

**静默继续**——不要停止：选择 3-5 个命名的竞争对手进行深入挖掘（选择最接近的）；缺少可选工具数据（标记为估计/N/A 并继续）；主题范围不明确（分析完整重叠并标记最广泛的集群）。

## 指令

当用户请求内容差距分析时：

1. **定义分析范围**——确认您的网站、竞争对手、主题重点、内容类型、受众和业务目标。
2. **审计您现有的内容**——映射索引页面、内容类型、主题集群、赢家和劣势。
3. **分析竞争对手内容**——比较内容量、流量、类型组合、主题覆盖范围和独特资产。
4. **识别关键词差距**——根据量、难度和相关性将差距分组为高优先级、快速获胜和长期。
5. **映射主题差距**——比较主题集群覆盖范围，并为缺失的主题推荐支柱/集群方法。
6. **识别内容格式差距**——比较指南、教程、比较、案例研究、工具、模板、视频和研究。
7. **分析 GEO / AI 差距**——识别竞争对手被引用的缺失问答、定义和比较内容。
8. **映射到受众旅程**——比较认知、考虑、决策和留存覆盖范围。
9. **优先级排序并创建行动计划**——交付执行摘要、优先级差距列表（快速获胜 / 战略构建 / 长期）、内容日历和成功指标。

将每个指标标记为 **测量**（工具/导出）、**用户提供** 或 **估计**（模型推断）；永远不要将估计呈现为测量；如果必需指标不可用，标记为 N/A——不要凭空捏造。

**质量标准**：每个差距都指明覆盖该内容的竞争对手、其量或流量估计以及为何值得关闭——永远不要在没有证据的情况下列出裸主题。

> **参考**：参见 [Analysis Templates](references/analysis-templates.md) 以获取每一步使用的紧凑模板。

## 示例

参见 [references/example-report.md](references/example-report.md) 以获取完整的 SaaS 营销示例。

## 高级分析

### 竞争集群比较

```
比较我们的主题集群 [主题] 与前 5 名竞争对手
```

### 时间差距分析

```
竞争对手在过去 6 个月内发布而我们未覆盖的内容是什么？
```

### 基于意图的差距

```
查找我们的 [商业/信息性] 意图内容的差距
```

## 保存结果

写入路径：`memory/research/content-gap-analysis/YYYY-MM-DD-<主题>.md`；将持久的差距优先级和竞争对手事实推广到 `memory/hot-cache.md`。参见 [Skill Contract](../../../references/skill-contract.md) §保存结果模板。

## 参考资料

- [Analysis Templates](references/analysis-templates.md) — 差距分析模板
- [Gap Analysis Frameworks](references/gap-analysis-frameworks.md) — 审计和优先级排序框架
- [Example Report](references/example-report.md) — 示例

## 下一个最佳技能

主要：[content-writer](../../implement/content-writer/SKILL.md)。
