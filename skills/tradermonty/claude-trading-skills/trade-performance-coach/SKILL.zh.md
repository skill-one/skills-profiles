---
name: trade-performance-coach
description: 审查已关闭的交易、部分退出交易以及月度交易汇总，以评估流程合规性、风险纪律、执行质量以及基于证据的交易行为模式。当交易员记忆核心（trader-memory-core）和信号事后分析（signal-postmortem）生成记录时，或当用户要求进行交易后教练式、风险管理式、规则合规性审查、下一时段操作规则或心理感知交易行为反馈时，使用此功能。该技能不提供买入/卖出建议、治疗或经纪执行服务。
---

# 交易表现教练

## 概述

交易表现教练通过审查记录的交易结果和交易日志证据，帮助人类交易者改进其决策过程。它将已关闭的交易记录、事后分析结果、风险规则和可选的市场状态背景转换为基于证据的辅导报告，涵盖：

- 流程遵守情况
- 风险纪律
- 执行质量
- 可能的交易行为模式
- 下一场交易的操作规则
- 教练用于反思的问题

这项技能旨在填补风险经理、交易台主管或交易教练在专业交易环境中可能提供支持的角色。它严格是一个流程审查技能：它从不建议进入、退出、买入、卖出、做空、持有或调整特定证券的规模。

## 何时使用

在以下任何情况下使用此技能：

- 已关闭交易且用户希望进行交易后辅导审查。
- 发生部分关闭且用户希望检查规模、止损或退出行为。
- 用户有 `trader-memory-core` 主题记录和 `signal-postmortem` 分析结果，并希望获得下一场交易的操作规则。
- 用户希望对重复的流程、风险、执行或行为模式进行月度审查。
- 用户要求对其自己的记录交易进行风险经理风格的审查。
- 用户询问亏损是否是流程错误、执行错误、市场环境问题或可接受的偏差。
- 用户希望标记出可能的 FOMO（害怕错过）、复仇交易、过度自信、犹豫、止损移动或规模侵蚀模式，并提供证据。

## 何时不使用

不要使用此技能来：

- 选择股票或对交易候选进行排名。
- 作为财务建议批准或拒绝实时交易。
- 下达订单或起草经纪说明。
- 提供治疗、心理健康诊断或人格评估。
- 推断交易证据所提供的私人心理特征之外的私人心理特征。
- 因亏损或规则违规而羞辱用户。
- 替换 `trader-memory-core`；此技能消耗交易日志/主题记录并生成辅导发现。

如果输入不完整，请默认为 `REVIEW_REQUIRED` 或 `journal_only` 模式，并要求提供缺失的记录，而不是编造证据。

## 前置条件

推荐的上游记录：

- `trader-memory-core` 已关闭的主题记录或交易日志条目
- `signal-postmortem` 事后分析结果
- 原始交易计划或交易票
- 实际的入场/退出/部分关闭操作
- 如果有的话，用户定义的风险计划
- 可选的 `market-regime-daily` / `exposure-coach` 上下文

不需要付费 API 密钥。确定性脚本可以从本地 JSON/YAML 类型的记录中工作。

## 输入

最小有用的输入是一个记录的交易或一个月的汇总。

首选字段：

```yaml
review_type: single_trade | partial_close | monthly_aggregate
trade_id: string
ticker: string
outcome: win | loss | breakeven | mixed
planned:
  thesis: string
  entry: number
  stop: number
  target: number
  risk_r: number
  thesis_recorded_before_entry: boolean
  setup_confirmed: boolean
  market_regime: allowed | restrictive | cash_priority | unknown
actual:
  entry: number
  exit: number
  risk_r: number
  portfolio_heat_r: number
  stop_moved: boolean
  stop_move_planned: boolean
  entry_before_confirmation: boolean
  traded_against_regime: boolean
risk_plan:
  max_risk_per_trade_r: number
  max_portfolio_heat_r: number
  max_weekly_loss_r: number
postmortem:
  root_cause: thesis_quality | execution | risk_sizing | market_environment | rule_violation | randomness | unknown
  notes: [string]
journal:
  reflection: string
  emotions: [string]
monthly:
  trades: [object]
  consecutive_losses: number
  rule_violations: number
```

脚本容忍部分记录。缺失的证据被标记为 `unclear`。

对于实际评估的数值字段（`planned.risk_r`、`actual.risk_r`、`risk_plan.max_risk_per_trade_r`、`actual.portfolio_heat_r`、`risk_plan.max_portfolio_heat_r` 和 `monthly.consecutive_losses`），提供的非空值必须是有限的和非负的。数值字符串和零是被接受的；连续亏损必须是整数。布尔值、负值、NaN、无穷大、格式错误的字符串和转换溢出是被拒绝的。明确无效的最大值不会回退到计划风险。缺失/空字段保留部分记录行为。CLI 验证每个源记录，包括多个输入，并在创建或修改报告之前，当数值无效时返回退出码 2 并带有特定字段的错误。

这项技能仍然是测试版。数值验证不建立生产就绪状态；报告 ID 路径安全性和文档中提到的浅层多输入包装仍然需要单独评估。

## 工作流程

### 第 1 步 — 收集源记录

收集最新的已关闭交易记录、事后分析、风险计划和交易日志笔记。

```bash
python3 skills/trade-performance-coach/scripts/review_trade_performance.py \
  --input reports/trade_memory/closed_thesis_EXMPL.json \
  --output-dir reports/trade-performance-coach
```

### 第 2 步 — 评估流程遵守情况

将实际操作与用户的记录计划和规则进行比较。检查：

- 缺少入场前主题
- 跳过了设置确认
- 交易违反了市场状态门禁
- 没有预定义规则就移动了止损
- 退出/部分关闭与计划不一致
- 记录质量不完整

### 第 3 步 — 评估风险纪律

将实际风险和热度与风险计划进行比较。检查：

- 每笔交易风险超过最大值
- 投资组合热度超过最大值
- 周损失或连续亏损升级
- 在赢家或输家之后进行超规模交易
- 如果提供，则检查相关性敞口

### 第 4 步 — 评估执行质量

对入场、止损、退出、加仓、减仓和审查行为进行分类。将干净的流程亏损与执行错误区分开来。

### 第 5 步 — 检测可能的交易行为模式

使用交易日志笔记和操作标志中的证据来标记可能的交易行为模式。始终将标签与证据关联，并使用非诊断性语言。

支持的 MVP 标签：

- `fomo_entry`
- `revenge_trade`
- `premature_exit`
- `overconfidence_after_winner`
- `stop_moved`
- `size_creep`
- `hesitation`
- `rule_drift`
- `no_pattern_detected`

### 第 6 步 — 生成下一场交易的操作规则

将发现转换为临时的具体护栏。示例：

- 在下一次入场之前需要主题记录和截图
- 在规则违规之后，对接下来两笔交易的风险上限设置为 0.5R
- 在重复出现复仇交易证据之后切换到仅审查模式
- 不要追逐错过的入场；将下一个有效设置添加到观察列表

### 第 7 步 — 人类决策门

在每份报告中以人类决策门结束。默认操作是 `journal_only`。

允许的操作：

```text
accept_rules / modify_rules / defer / journal_only
```

## 输出

该技能生成一个 JSON 报告，并可选生成一个 Markdown 报告。

必需的顶级 JSON 字段：

- `schema_version`
- `review_type`
- `review_id`
- `overall_verdict`
- `summary`
- `scores`
- `process_adherence_findings`
- `risk_manager_notes`
- `execution_quality_assessment`
- `behavioral_pattern_tags`
- `next_session_operating_rules`
- `coach_questions`
- `human_decision_gate`
- `disclaimer`

裁决：

| 裁决 | 含义 |
|---|---|
| `OK` | 未发现实质性流程违规。结果似乎与计划兼容。 |
| `WARN` | 出现轻微流程或记录质量问题。 |
| `REVIEW_REQUIRED` | 在下一场类似交易之前发现有意义的流程、风险或行为发现。 |
| `RULE_VIOLATION` | 明确的用户规则似乎已被违反。 |
| `COOL_DOWN` | 重复违规、回撤/复仇模式或升级表明应仅进入审查模式。 |

## 示例命令

```bash
python3 skills/trade-performance-coach/scripts/review_trade_performance.py \
  --input skills/trade-performance-coach/scripts/tests/fixtures/single_trade_rule_violation_loss.json \
  --output-dir reports/trade-performance-coach \
  --markdown
```

## 资源

在调用时选择性阅读：

- `references/review-framework.md` — 五轴审查模型、评分、裁决
- `references/behavior-tags.md` — 行为标签定义和证据规则
- `references/risk-review-checklist.md` — 风险经理检查表和严重性规则
- `references/output-contract.md` — JSON 输出合同和模式说明
- `references/hermes-integration.md` — 建议的 Hermes `/post-trade-coach` 和月度辅导集成
- `assets/performance_coach_report.schema.json` — 机器可读输出模式
- `scripts/review_trade_performance.py` — 确定性本地审查者

## 护栏

- 这不是财务建议，而是流程审查支持。
- 不要建议买入、卖出、做空、持有或调整特定证券的规模。
- 不要提供治疗或心理健康诊断。
- 不要推断人格特征。
- 不要羞辱或对用户进行道德说教。
- 将每个行为标签与证据关联。
- 对行为标签使用“可能的模式”语言。
- 始终包含人类决策门。
- 数据不完整时默认为日记/审查模式。
