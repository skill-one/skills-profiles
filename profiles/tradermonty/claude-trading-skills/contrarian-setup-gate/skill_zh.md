# 反向操作设置门

## 概述

将Jason Shapiro的三步反向操作流程的输出结果整合为一个可执行状态。cot-contrarian-detector（第一步）标记拥挤定位，news-reaction-failure-analyzer（第二步）测试市场是否未对有利于群体的新闻做出反应，技术分析师的反向确认模式（第三步）确认每周价格行为证据显示反转。此门读取这三个报告的JSON文件，并应用一个明确且经过彻底测试的优先级规则集来生成一个`setup_status`，并将每个无法确认的输入的失败原因附加到其上。

此门不进行获取、不进行API调用，也不进行除验证和组合其提供的三个输入之外的任何计算。它是管道的合成中心，而不是数据源。

## 使用场景

- 运行cot-contrarian-detector后（始终需要——这是管道的入口点）
- 管道中途，仅使用检测器报告，以查看CROWDED状态和剩余步骤
- 运行news-reaction-failure-analyzer后，以查看设置是否推进到WATCHING_PRICE或被REJECTED
- 运行技术分析师的反向确认模式后，以查看设置是否达到READY_FOR_PLAN
- 在将符号方向和止损水平交给位置调整技能之前

## 前置条件

- Python 3.9+
- 无API密钥——此技能完全离线
- 需要一个针对评估符号的cot-contrarian-detector JSON报告（必需）
- 可选地，需要针对同一符号的news-reaction-failure-analyzer JSON报告（第二步）
- 可选地，需要针对同一符号的技术分析师反向确认JSON报告（第三步）

## 工作流程

### 第一步：运行门

```bash
python3 skills/contrarian-setup-gate/scripts/run_contrarian_setup_gate.py \
  --symbol B6 \
  --detector-json reports/cot_crowding_2026-07-12.json \
  --news-json reports/nrf_B6_2026-07-12.json \
  --price-action-json reports/ta_confirmation_B6_2026-07-12.json \
  --as-of 2026-07-15 \
  --output-dir reports/
```

`--symbol`和`--detector-json`是必需的；`--news-json`和`--price-action-json`是可选的——省略任何一个以查看该管道阶段的状态。`--as-of`是必需的（没有隐含的“今天”）：陈旧性始终针对明确的参考日期进行评估，因此重新运行是确定的。

退出行为有意设计为不对称：缺少或格式错误的`--as-of`（或任何其他CLI使用错误）是操作员配置错误，因此CLI退出`2`并显示使用说明，不生成报告。三个不受信任的报告文件中出现问题——不可读、格式错误、陈旧、不一致——始终以失败关闭方式处理：CLI退出`0`并生成报告，命名失败原因，就像管道中的其他每个技能一样。

### 第二步：读取设置状态

| 状态 | 含义 | 下一步 |
|---|---|---|
| `READY_FOR_PLAN` | 三个步骤全部确认；方向、entry_trigger和invalidation_level已填充 | 将`direction`和`invalidation_level`交给位置调整技能 |
| `WATCHING_PRICE` | 拥挤+新闻确认；价格行为仍待确认 | 运行技术分析师的反向确认模式 |
| `CROWDED` | 拥挤确认；新闻和/或价格仍待确认 | 运行news-reaction-failure-analyzer |
| `REJECTED` | 拥挤未确认（分类NEUTRAL），或新闻/价格返回未确认 | 停止——不要为该符号/方向运行进一步步骤 |
| `INSUFFICIENT_EVIDENCE` | 必须的输入缺失、不可读、陈旧、不一致或本身无法做出裁决 | 停止——在重新运行之前修复或重新生成命名输入 |

`missing_confirmations`列出了每个仍阻止的步骤，及其`state`和`reason`。`warnings`永远不会改变状态——它们标记值得审计的条件，例如中等置信度的确认信号或接近陈旧的输入。

### 第三步：仅对READY_FOR_PLAN采取行动

在`READY_FOR_PLAN`时，`direction`（SHORT/LONG，群体的衰减侧）、`entry_trigger`（确认的每周信号的客观回声）和`invalidation_level`（价格行为报告的止损参考）已填充。`gate_confidence`是新闻和价格行为置信度中较弱的一个（HIGH/MEDIUM/LOW——`LOW`是一个标记，上游技能记录为保留但实际从未发出；门接受它并将其排名最弱，而不是将其作为未知拒绝）。位置调整是下一个管道阶段（截至此技能发布时尚未构建——请参阅存储库工作流程文档中的路线图）；此门永远不会下单或建议订单。

## 优先级（摘要）

每个步骤按严格的管道顺序评估——拥挤、然后新闻、然后价格行为——并且每个步骤完全确定之前才会咨询下一个步骤的文件。较早步骤的最终裁决永远不会因后续步骤的问题而软化。

1. 首先且唯一地评估拥挤：INVALID/INSUFFICIENT拥挤始终为`INSUFFICIENT_EVIDENCE`；NOT_CONFIRMED（NEUTRAL）分类始终为`REJECTED`，无论任何下游文件的状态或损坏情况如何。
2. 确认拥挤后，接下来独立评估新闻：INVALID（不可读、格式错误、陈旧、符号不匹配、方向不匹配、不支持的架构）强制`INSUFFICIENT_EVIDENCE`；NOT_CONFIRMED强制`REJECTED`；INSUFFICIENT强制`INSUFFICIENT_EVIDENCE`——在所有这些情况下，都不会检查价格行为以做出决策。
3. 一旦新闻确认（或PENDING，用于顺序外使用），最后评估价格行为，并使用相同的四向裁决。在新闻之前运行价格行为（顺序外管道使用）将状态限制在`CROWDED`并附带警告——NOT_CONFIRMED的价格行为裁决仍然REJECT，即使顺序外，因为该分支中价格行为仍完全评估。
4. 拥挤确认，下游步骤均待确认 -> `CROWDED`。
5. 拥挤+新闻确认，价格行为待确认 -> `WATCHING_PRICE`。
6. 三个全部确认 -> `READY_FOR_PLAN`。

有关完整的决策表（每个可达的{拥挤} x {新闻} x {价格行为}状态组合）、原因标记词汇表和工作示例，请参阅`references/gate-decision-table.md`。

## 输出契约

脚本将`contrarian_setup_gate_<SYMBOL>_<as-of>.json`和`.md`写入`--output-dir`：

```yaml
symbol: B6
setup_status: READY_FOR_PLAN | WATCHING_PRICE | CROWDED | REJECTED | INSUFFICIENT_EVIDENCE
direction: SHORT | LONG | null
gate_confidence: HIGH | MEDIUM | LOW | null
entry_trigger: string | null
invalidation_level: number | null
missing_confirmations: [{step, state, reason}, ...]
warnings: [string, ...]
inputs:
  crowding: {state, classification, data_date, age_days, report_path}
  news_failure: {state, verdict, confidence, verdict_reason, as_of, age_days, report_path}
  price_action: {state, verdict, confidence, verdict_reason, stop_reference, as_of, age_days, report_path}
run_context: {symbol, as_of, max_detector_age_days, max_report_age_days, schema_version, skill}
```

每个输入的`state`是`CONFIRMED`、`NOT_CONFIRMED`、`INSUFFICIENT`、`PENDING`（未提供报告）或`INVALID`（提供了报告但无法使用——不可读、格式错误、陈旧或与其他输入不一致；始终附带命名原因）之一。

## 安全机制

1. **永远不会下单或建议订单。** `READY_FOR_PLAN`是此技能达到的最远状态。订单进入和位置调整是分开的、下游的决策。
2. **INSUFFICIENT_EVIDENCE和REJECTED永远不会推进。** 没有警告、置信度或部分输入会推动状态超过优先级规则允许的范围。
3. **每个输入始终失败关闭。** 不可读、格式错误、陈旧、符号不匹配或未知枚举报告永远不会被视为通过——它会被命名并阻止或降低状态。这包括价格行为报告的`verdict_reason`（允许列出技术分析师的实际确认信号词汇，而不仅仅是类型检查）及其`stop_reference`（必须是一个有限的正数——永远不会是非有限的、零、负数或布尔值）。在三个报告文件中的任何一个达到此验证之前，CLI也会在文件中包含非有限数字（`Infinity`/`-Infinity`/`NaN`，包括看起来像普通数字的`1e309`，它在解析时溢出）的任何地方直接拒绝文件（原因`<input>_non_finite`）——这是确保每个报告都是有效、完整的JSON文件，即使在对抗性输入下的机制。
4. **`READY_FOR_PLAN`始终附带可用的计划。** `entry_trigger`在状态为`READY_FOR_PLAN`时保证非空，`invalidation_level`保证是有限的正数——这既通过输入验证也通过防御性不变量检查来强制执行。
5. **不是投资建议。** `entry_trigger`和`invalidation_level`是上游价格行为报告的客观回声，而不是建议。

## 资源

- `scripts/run_contrarian_setup_gate.py` -- CLI：强化的JSON加载（不可读 / parse_error包括RecursionError / non_finite通过迭代全文扫描），报告生成
- `scripts/gate_logic.py` -- 纯合成核心：规范化（包括格式错误检测）、一致性检查、优先级状态机
- `references/gate-decision-table.md` -- 完整决策表、原因标记词汇表、工作示例（包括真实的B6 REJECTED案例）
