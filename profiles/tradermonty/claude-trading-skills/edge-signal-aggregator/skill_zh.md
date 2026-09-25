# 边缘信号聚合器

## 概述

将多个上游边缘发现技能的输出结果整合到一个加权信念仪表板中。该技能应用可配置的信号权重，去重重叠的主题，标记技能之间的矛盾，并按综合置信度得分对复合边缘想法进行排序。结果是一个带有每个贡献技能溯源链接的优先级边缘短名单。

## 使用场景

- 运行多个边缘发现技能后，需要统一视图
- 整合来自边缘候选代理、主题检测器、行业分析师和机构流量追踪器的信号
- 在基于多个信号来源做出投资组合分配决策之前
- 识别不同分析方法之间的矛盾
- 优先考虑哪些边缘想法值得深入研究

## 前置条件

- Python 3.9+
- 无需API密钥（处理来自其他技能的本地JSON/YAML文件）
- 依赖项：`pyyaml`（大多数环境中都是标准库）

## 工作流程

### 第1步：收集上游技能输出

收集您要聚合的上游技能的输出文件：
- 来自边缘候选代理的 `reports/edge_candidate_*.json`
- 来自边缘概念综合器的 `reports/edge_concepts_*.yaml`
- 来自主题检测器的 `reports/theme_detector_*.json`
- 来自行业分析师的 `reports/sector_analyst_*.json`
- 来自机构流量追踪器的 `reports/institutional_flow_*.json`
- 来自边缘提示提取器的 `reports/edge_hints_*.yaml`

### 第2步：运行信号聚合

执行聚合器脚本，指定上游输出路径：

```bash
python3 skills/edge-signal-aggregator/scripts/aggregate_signals.py \
  --edge-candidates reports/edge_candidate_agent_*.json \
  --edge-concepts reports/edge_concepts_*.yaml \
  --themes reports/theme_detector_*.json \
  --sectors reports/sector_analyst_*.json \
  --institutional reports/institutional_flow_*.json \
  --hints reports/edge_hints_*.yaml \
  --output-dir reports/
```

可选：使用自定义权重配置：

```bash
python3 skills/edge-signal-aggregator/scripts/aggregate_signals.py \
  --edge-candidates reports/edge_candidate_agent_*.json \
  --weights-config skills/edge-signal-aggregator/assets/custom_weights.yaml \
  --output-dir reports/
```

### 第3步：查看聚合仪表板

打开生成的报告进行查看：
1. **排序的边缘想法** - 按复合信念得分排序
2. **信号溯源** - 哪些技能贡献了每个想法
3. **矛盾** - 标记供手动审查的冲突信号
4. **去重日志** - 合并重叠主题

### 第4步：处理高信念信号

按最低信念阈值筛选短名单：

```bash
python3 skills/edge-signal-aggregator/scripts/aggregate_signals.py \
  --edge-candidates reports/edge_candidate_agent_*.json \
  --min-conviction 0.7 \
  --output-dir reports/
```

## 输出格式

### JSON报告

```json
{
  "schema_version": "1.0",
  "generated_at": "2026-03-02T07:00:00Z",
  "config": {
    "weights": {
      "edge_candidate_agent": 0.25,
      "edge_concept_synthesizer": 0.20,
      "theme_detector": 0.15,
      "sector_analyst": 0.15,
      "institutional_flow_tracker": 0.15,
      "edge_hint_extractor": 0.10
    },
    "min_conviction": 0.5,
    "dedup_similarity_threshold": 0.8
  },
  "summary": {
    "total_input_signals": 42,
    "unique_signals_after_dedup": 28,
    "contradictions_found": 3,
    "signals_above_threshold": 12
  },
  "ranked_signals": [
    {
      "rank": 1,
      "signal_id": "sig_001",
      "title": "AI Infrastructure Capex Acceleration",
      "composite_score": 0.87,
      "contributing_skills": [
        {
          "skill": "edge_candidate_agent",
          "signal_ref": "ticket_2026-03-01_001",
          "raw_score": 0.92,
          "weighted_contribution": 0.23
        },
        {
          "skill": "theme_detector",
          "signal_ref": "theme_ai_infra",
          "raw_score": 0.85,
          "weighted_contribution": 0.13
        }
      ],
      "tickers": ["NVDA", "AMD", "AVGO"],
      "direction": "LONG",
      "time_horizon": "3-6 months",
      "confidence_breakdown": {
        "multi_skill_agreement": 0.30,
        "signal_strength": 0.35,
        "recency": 0.22
      }
    }
  ],
  "contradictions": [
    {
      "contradiction_id": "contra_001",
      "description": "Conflicting sector view on Energy",
      "skill_a": {
        "skill": "sector_analyst",
        "signal": "Energy sector bearish rotation",
        "direction": "SHORT"
      },
      "skill_b": {
        "skill": "institutional_flow_tracker",
        "signal": "Heavy institutional buying in XLE",
        "direction": "LONG"
      },
      "resolution_hint": "Check timeframe mismatch (short-term vs long-term)"
    }
  ],
  "deduplication_log": [
    {
      "merged_into": "sig_001",
      "duplicates_removed": ["theme_detector:ai_compute", "edge_hints:datacenter_demand"],
      "similarity_score": 0.92
    }
  ]
}
```

### Markdown报告

Markdown报告提供人类可读的仪表板：

```markdown
# 边缘信号聚合器仪表板
**生成时间：** 2026-03-02 07:00 UTC

## 摘要
- 总输入信号：42
- 去重后唯一信号：28
- 矛盾：3
- 高信念 (>0.7)：12

## 信念最高的10个边缘想法

### 1. AI Infrastructure Capex Acceleration (得分：0.87)
- **股票代码：** NVDA, AMD, AVGO
- **方向：** 多头 | **时间范围：** 3-6个月
- **贡献技能：**
  - edge-candidate-agent: 0.92 (ticket_2026-03-01_001)
  - theme-detector: 0.85 (theme_ai_infra)
- **信念分解：** 协议 0.30 | 强度 0.35 | 近期性 0.22

...

## 需要审查的矛盾

### 能源行业矛盾
- **sector-analyst：** 市场疲软轮动 (空头)
- **institutional-flow-tracker：** XLE重仓买入 (多头)
- **提示：** 检查时间范围不匹配

## 去重摘要
- 14个信号合并为8个唯一主题
- 合并信号的相似度平均值：0.89

```

报告保存在 `reports/` 目录下，文件名格式：
- `edge_signal_aggregator_YYYY-MM-DD_HHMMSS.json`
- `edge_signal_aggregator_YYYY-MM-DD_HHMMSS.md`

## 资源

- `scripts/aggregate_signals.py` -- 主要聚合脚本，带CLI接口
- `references/signal-weighting-framework.md` -- 默认权重和评分方法的合理性说明
- `assets/default_weights.yaml` -- 默认技能权重配置

## 核心原则

1. **溯源追踪** -- 每个聚合信号都链接到其来源技能和原始参考
2. **矛盾透明** -- 冲突信号不会被隐藏，以支持明智决策
3. **可配置权重** -- 默认权重反映典型可靠性，但可按用户自定义
4. **无损失去重** -- 合并信号保留所有原始来源的引用
5. **可操作输出** -- 排序列表，每个想法都有清晰的股票代码、方向和时间范围
