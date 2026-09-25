# 每周业绩摘要

## 概述

每周业绩摘要将您在一周内关闭的交易汇总成一个业绩报告。它读取由 `trader-memory-core` 跟踪的已关闭的 thesis（`state/theses/th_*.yaml`），计算主要指标（胜率、期望值、盈亏比、R 倍数、MAE/MFE），按多种模式维度（来源技能、退出原因、thesis 类型、行业、机制标签、筛选等级）分解结果，并展示本周的最大赢家、输家和经验教训。输出是一个 JSON 记录和一个人类可读的 Markdown 报告。纯计算——无需 API 密钥。

## 使用场景

- 在交易周结束时回顾汇总的已实现业绩
- 衡量所有已关闭头寸的胜率和期望值
- 查看哪些来源技能、退出原因、行业或机制带来了盈利与亏损
- 为月末回顾（合并四周摘要）或事后分析提供数据
- 快速了解“哪些有效/哪些无效”的概览，基于实际已关闭交易

## 不适用场景

- 用于单笔交易的深度分析——请使用 `trade-performance-coach`
- 用于信号级别的真/假阳性分类——请使用 `signal-postmortem`
- 用于买入/卖出建议或头寸规模——此技能仅用于描述

## 前置条件

- Python 3.9+ 和 `PyYAML`（已作为仓库依赖项）
- 一个 `trader-memory-core` 状态目录的 thesis YAML 文件（`state/theses/`）
- 无需 API 密钥

## 工作流程

### 第 1 步：运行一周的摘要

```bash
python3 skills/weekly-performance-digest/scripts/generate_weekly_digest.py \
  --state-dir state/theses \
  --from-date 2026-06-13 --to-date 2026-06-20 \
  --output-dir reports/ -v
```

默认值：`--state-dir state/theses`，`--from-date` = `--to-date` 之前的 7 天，`--to-date` = 今天，`--output-dir reports/`。如果没有日期标志，则摘要最近 7 天。

### 第 2 步：阅读报告

运行会生成 `reports/weekly_digest_<to-date>.json` 和 `reports/weekly_digest_<to-date>.md`。查看 Markdown 以获取执行摘要、指标表、模式分解和最大赢家/输家；下游使用 JSON。

### 第 3 步（可选）：下游使用

合并多个每周 JSON 摘要进行月度回顾，或将 JSON 传递给事后分析/教练步骤。该技能是描述性的——通过您的正常审查流程采取行动。

## 工作原理

- **交易选择**。如果交易的 `exit.actual_date` 落在 `[from-date, to-date]` 范围内且 `status == CLOSED`，则该交易计入本周。
- **盈亏**。`outcome.pnl_dollars > 0` 是赢家，`< 0` 是输家，`== 0` 是平局；`win_rate = winners / total_trades`。
- **R 倍数**。`pnl_dollars / ((entry.actual_price − exit.stop_loss) × position.shares)`。（止损值从 `exit.stop_loss` 读取，根据真实的 thesis 模式）。
- **双重计数防护**。一个已关闭 thesis 的 `outcome.pnl_dollars` 是跨所有分腿加上最终腿的 *累积* 已实现 P&L。主要指标仅使用已关闭 thesis 的累积值。单独的 `partial_trims` 块仅扫描 **部分关闭** thesis（仍开放）的 `status_history[]`，仅用于信息报告——**永远不会**计入主要总数/胜率。因此，在第一周修剪然后在第二周关闭的头寸，在第一周显示为部分修剪，并在第二周的已关闭主要指标中显示；这是有意为之，不是重复。

## 输出格式

### JSON (`weekly_digest_<to-date>.json`)

```json
{
  "schema_version": "1.0",
  "report_type": "weekly_performance_digest",
  "period": {"from": "2026-06-13", "to": "2026-06-20"},
  "generated_at": "2026-06-20T21:39:07Z",
  "summary": {
    "total_trades": 2, "winners": 1, "losers": 1, "breakeven": 0,
    "win_rate": 0.5, "expectancy": 25.0, "profit_factor": 2.0,
    "total_realized_pnl": 50.0, "total_realized_pnl_pct": 4.17
  },
  "metrics": {
    "avg_winner": 100.0, "avg_loser": -50.0,
    "largest_winner": 100.0, "largest_loser": -50.0,
    "avg_holding_days_winners": 9.0, "avg_holding_days_losers": 6.0,
    "r_multiple_avg": 0.25, "r_multiple_stdev": 1.06,
    "avg_mae_pct": -3.75, "avg_mfe_pct": 4.5
  },
  "pattern_analysis": {
    "by_source_skill": {"...": {"wins": 1, "losses": 0, "total": 1, "win_rate": 1.0}},
    "by_exit_reason": {}, "by_thesis_type": {}, "by_sector": {},
    "by_mechanism_tag": {}, "by_screening_grade": {}
  },
  "partial_trims": {"count": 0, "total_realized_pnl": 0.0, "trims": []},
  "lessons": {"top_wins": [], "top_losses": [], "process_improvements": []}
}
```

### Markdown (`weekly_digest_<to-date>.md`)

章节：`# 每周业绩摘要`，`## 执行摘要`，`## 业绩指标`，`## 模式分析`，`## 经验教训`（`### 最大赢家` / `### 最大输家` / `### 流程改进`）。

一个空周仍然会生成一个有效的报告，指标为零（退出代码 0）。

## 资源

- `scripts/generate_weekly_digest.py` — 摘要生成器（JSON + Markdown）
- `references/weekly-digest-metrics.md` — 指标公式和解释

## 关键原则

1. **仅使用已关闭交易计算主要指标**——累积 `outcome.*`，按退出日期键。
2. **无重复计数**——部分修剪仅用于信息，不计入总数。
3. **模式归因**——每个盈亏都跨多个维度归因。
4. **描述性而非指导性**——摘要报告；由您决定。
