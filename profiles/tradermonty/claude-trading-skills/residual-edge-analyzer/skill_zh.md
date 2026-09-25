# 残差边缘分析器

## 概述

测试策略的表观性能是否在明确比较预定义的基准回报系列时仍然存在。生成可审计的 JSON 资产和简洁的 Markdown 报告，而无需获取数据或更改交易敞口。

将其视为 `backtest-expert` 之后的伪证关卡，而不是交易授权。

## 前置条件

- 使用 Python 3.9+。
- 准备一个包含 ISO 日期、策略回报以及同一行上所有基准回报的 CSV 文件。
- 准备遵循 `[references/input-contract.md](references/input-contract.md)` 的 JSON 规范。
- 提供实际期间回报。不要用 CAGR、夏普比率、累积盈亏或其他汇总指标来替代。

## 工作流程

### 1. 在检查结果之前定义问题

用一句话陈述所声称的独立边缘。选择一个可能是策略简单副本的主要基准，然后选择至少一个替代基准模型。

在配置中记录这些声明：

- `baseline_selection: predeclared`
- `strategy_return_basis` 和 `baseline_return_basis`：都为 `gross` 或都为 `net`
- `analysis_scope`：`out_of_sample`、`live` 或 `in_sample`
- `universe_data`：`point_in_time`、`current_constituents` 或 `not_applicable`

每个声明对于决策级别的裁决都是必需的。遗漏任何一个被视为未声明，而不是良性，并将报告降级为 `REVIEW_REQUIRED`。`not_applicable` 的存在是为了能够明确声明没有宇宙成员资格的基准，而不是留空。

不要因为基准给出了偏好的残差结果而选择它。

### 2. 验证回报系列合同

要求：

- 唯一的 ISO 日期；
- 大于 -100% 的有限数值回报；
- 策略和基准之间具有相同的频率和成本基础；
- 同一宇宙的等权重或动量基准的点时成员资格；
- 规则标签独立于正在解释的损失期间定义。

如果输入缺少带日期的策略回报系列，则停止。将仅汇总输入报告为不足，而不是凭空编造观察结果。

### 3. 运行分析器

```bash
python3 skills/residual-edge-analyzer/scripts/analyze_residual_edge.py \
  --input reports/strategy_returns.csv \
  --config reports/residual_edge_config.json \
  --output-json reports/residual_edge_report.json \
  --output-markdown reports/residual_edge_report.md
```

该脚本在一个执行中运行预定义的主要模型和所有敏感性模型。它使用截距 OLS 模型和 HAC/Newey-West 标准误差。它报告残差边缘比率作为年化 alpha 除以年化残差波动率；不要从原始 OLS 残差均值计算夏普比率，因为截距使该均值为零。

### 4. 解释证据

使用四个状态作为诊断标签：

- `RESIDUAL_EDGE`：alpha、残差边缘比率和滚动稳定性满足配置的阈值。
- `BASELINE_EXPLAINED`：基准 R-squared 较高，而残差证据较弱。
- `RESIDUAL_FRAGILE`：结果未能通过一个或多个稳健性关卡或在不同声明的基准模型之间发生变化。当滚动分析被禁用、不可用、不完整或未提供敏感性模型时，也使用此状态。
- `INSUFFICIENT_EVIDENCE`：样本低于配置的最小值。

单独阅读 `decision_eligibility`。当存在关键来源、成本基础、样本或多重共线性警告时，当滚动证据不可用，或未测试替代基准时，统计上有趣的 结果仍然保持 `REVIEW_REQUIRED`。

检查：

1. 主要和敏感性模型状态；
2. 年化 alpha 和 HAC t 统计量；
3. 残差边缘比率和残差自相关；
4. 滚动 alpha 稳定性；
5. 多因素模型的 VIF；
6. 预定义规则下的主动回报分解。

### 5. 交接发现

- 将基准选择、OOS 和稳定性发现反馈给 `backtest-expert`。
- 将重复的残差失败规则发送到 `signal-postmortem`。
- 仅将证据和操作约束传递给 `trade-performance-coach`。
- 永远不要自动更改头寸大小、敞口或订单。

## 边界

- 不要调用此基于持有量的贡献分析。Brinson 分配、选择和交互效应需要历史持有量、基准权重和成分回报。
- 不要从仅基于市场指数的基准中声称股票选择 alpha。
- 不要从当前成分构建等权重基准并标记为点时。
- 不要将样本内残差边缘解释为确认的 alpha。
- 不要在看到损失后挖掘许多规则定义。预定义一小部分，并在样本外确认结果。
- 不要假设高 R-squared 使策略毫无价值；容量、尾部行为、成本和实施价值需要单独的证据。

## 资源

- `scripts/analyze_residual_edge.py` — 确定性的 CSV-to-JSON/Markdown 分析器。
- `references/input-contract.md` — CSV/配置合同和可运行示例。
- `references/methodology.md` — 统计定义、解释和局限性。
