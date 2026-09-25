# Kanchi 股息审查监控器

## 概述

检测异常股息风险信号并将其路由至人工审查队列。
将自动化视为异常检测，而非自动交易执行。

## 使用场景

当用户需要时使用此功能：
- 对股息持仓进行每日/每周/每季度的异常检测。
- 对 T1-T5 风险触发进行强制审查排队。
- 与投资组合代码相关的 8-K/治理关键词扫描。
- 在人工决策前提供确定性 `OK/WARN/REVIEW` 输出。

## 前置条件

提供遵循以下规范的标准化输入 JSON：
- `references/input-schema.md`

如果上游数据不可用，至少提供：
- `ticker`
- `instrument_type`
- `dividend.latest_regular`
- `dividend.prior_regular`

## 不可协商规则

仅基于机器触发永远不要自动卖出。
始终为人工确认创建 `WARN` 或 `REVIEW` 证据。

## 状态机

- `OK`：无操作。
- `WARN`：加入下次检查周期并暂停可选添加。
- `REVIEW`：立即创建人工审查工单 + 暂停添加。

使用 `references/trigger-matrix.md` 查看触发阈值和操作。

### 平价股息周期注意事项

当 T6 仅由 `freeze_flag` / 最新常规股息等于先前常规股息驱动时，将其视为 `WARN` 以确认周期，而非股息恶化的证明。许多季度股息支付者在年度调增周期之间重复相同股息。在报告中，将其表述为“确认下次股息增长周期 / 暂停可选添加直至核查”，并避免暗示削减或理论破裂，除非 T1/T2/T3/T4/T5 证据也支持升级。

## 监控周期

- 每日：
  - T1 股息削减/暂停。
  - T4 SEC 文件关键词扫描（8-K导向）。
- 每周：
  - T3 代理信用压力检查。
- 每季：
  - T2 覆盖度恶化和 T5 结构性衰退评分。

## 工作流程

### 1) 标准化输入数据集

将每个代码的领域字段收集在一个 JSON 文档中：
- 股息点（最新常规、先前常规、缺失/零标志）。
- 覆盖度字段（FCF 或 FFO 或 NII、已支付股息、比率历史）。
- 资产负债表趋势字段（净债务、利息保障倍数、回购/股息）。
- 文件文本片段（尤其是最近的 8-K 或等效警报文本）。
- 运营趋势字段（收入 CAGR、利润率趋势、指引趋势）。

使用 `references/input-schema.md` 查看字段定义和示例有效负载。

### 2) 运行规则引擎

运行：

```bash
python3 skills/kanchi-dividend-review-monitor/scripts/build_review_queue.py \
  --input /path/to/monitor_input.json \
  --output-dir reports/
```

脚本根据 T1-T5 将每个代码映射到 `OK/WARN/REVIEW`。
输出文件保存到指定目录，文件名带日期（例如，`review_queue_20260227.json` 和 `.md`）。

### 3) 优先级和去重

如果多个触发器触发：
- 保留所有发现以供审计追踪。
- 仅将最终状态升级到最高严重性。
- 将触发原因作为单行证据存储。

### 4) 生成人工审查工单

对每个 `REVIEW` 代码，包括：
- 触发 ID 和证据。
- 疑似失效模式。
- 下次决策所需的 manual checks。

使用 `references/review-ticket-template.md` 输出格式。

## SEC 文件防护栏

在实施实时 SEC 获取器时：
- 包含合规的 `User-Agent` 字符串（名称 + 邮箱）。
- 使用缓存和限流。
- 尊重 SEC 公平访问指南。
- 在上游文件片段为空的定期投资组合审查中，使用 SEC `company_tickers.json` 加 `https://data.sec.gov/submissions/CIK##########.json` 列出每个持仓的近期 8-K / 8-K/A 文件，然后扫描主要文件文档中的 T4 关键词组（`Item 4.02`、非依赖、重述、重大缺陷、SEC 调查、传票、持续经营、审计师辞职、内部控制）。记录扫描窗口、近期 8-K 计数和是否命中。将“无关键词命中”视为狭窄的 T4 扫描结果，而非完整治理批准。

## 输出契约

始终返回：
1. 带摘要计数和代码级发现的队列 JSON。
2. 快速分诊的 Markdown 仪表板。
3. 立即 `REVIEW` 工单列表。

## 多技能交接

- 从 `kanchi-dividend-sop` 消费代码宇宙和基线假设。
- 将 `REVIEW` 结果反馈给 `kanchi-dividend-sop` 以进行再承保和头寸规模审查。
- 当风险事件暗示账户迁移决策时，与 `kanchi-dividend-us-tax-accounting` 共享账户类型上下文。

## 资源

- `scripts/build_review_queue.py`：本地 T1-T5 规则引擎。
- `scripts/tests/test_build_review_queue.py`：T1-T5 和报告渲染的单元测试。
- `references/trigger-matrix.md`：触发定义、周期和操作。
- `references/input-schema.md`：标准化输入架构和示例 JSON。
- `references/review-ticket-template.md`：标准人工审查工单布局。
