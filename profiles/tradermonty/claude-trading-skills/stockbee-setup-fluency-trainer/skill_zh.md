# Stockbee 设置流畅性训练器

构建和维护 Stockbee 风格的动量爆发设置模型书。这项技能将每日筛选器候选转换为结构化的学习记录，在 3 天和 5 天窗口成熟后更新它们，并总结哪些设置特征是有效的或无效的。

## 使用场景

- 用户希望系统地学习 Stockbee 动量爆发设置
- 用户要求从 `stockbee-momentum-burst-screener` 输出构建模型书
- 用户希望回顾失败的候选、错过的交易或 A/B 设置质量
- 用户希望获得 3 天 / 5 天向前回报、MFE、MAE 和止损击穿结果
- 用户希望在增加仓位大小之前提高设置识别能力
- 用户询问哪些 Stockbee 标签应该被提升、降级或过滤

## 前置条件

- Python 3.10+
- 一个 `stockbee-momentum-burst-screener` JSON 报告，或兼容的候选 JSON
- 可选：FMP API 密钥，用于在未提供离线 OHLCV JSON 时更新结果
- 推荐本地状态路径：`state/stockbee/model_book.jsonl`

## 工作流程

### 第 1 步：摄入动量爆发候选

在 Stockbee 动量爆发筛选器生成 JSON 报告后运行。

```bash
python3 skills/stockbee-setup-fluency-trainer/scripts/build_model_book.py ingest \
  --screener-json reports/stockbee_momentum_burst_YYYY-MM-DD_HHMMSS.json \
  --model-book state/stockbee/model_book.jsonl \
  --output-dir reports/
```

在有意构建负面示例集时使用 `--include-rejects`。否则，跳过被拒绝的候选。

### 第 2 步：更新 3 天和 5 天结果

使用 FMP：

```bash
python3 skills/stockbee-setup-fluency-trainer/scripts/build_model_book.py update \
  --model-book state/stockbee/model_book.jsonl \
  --horizons 3,5 \
  --output-dir reports/
```

使用离线 OHLCV JSON：

```bash
python3 skills/stockbee-setup-fluency-trainer/scripts/build_model_book.py update \
  --model-book state/stockbee/model_book.jsonl \
  --prices-json data/daily_ohlcv.json \
  --horizons 3,5 \
  --output-dir reports/
```

更新步骤记录：

- 每个时间范围内的向前收盘回报
- 每个时间范围内的 MFE 和 MAE
- 止损击穿状态和首次止损击穿日期
- 结果标签，如 `STRONG_WINNER`、`WORKED`、`FAILED_STOP`、`FAILED_FADE`、`CHOPPY_FAILURE` 或 `NEUTRAL`

### 第 3 步：汇总群体

```bash
python3 skills/stockbee-setup-fluency-trainer/scripts/build_model_book.py summarize \
  --model-book state/stockbee/model_book.jsonl \
  --group-by rating,primary_trigger,setup_tags \
  --min-sample 5 \
  --output-dir reports/
```

查看生成的 Markdown 和 JSON 报告。将 `rule_candidates` 视为证据提示，而不是自动的规则更改。

### 第 4 步：将证据转化为实践

对于具有足够示例的群体：

- 提升具有高胜率、正向 5 天预期和可接受平均 MAE 的标签
- 降级或过滤具有弱 5 天预期、频繁止损击穿或重复衰减失败的标签
- 在更改交易规则之前手动检查代表性图表
- 在 `trader-memory-core` 或月度审查过程中记录接受的教训

## 模型书字段

每个 JSONL 记录包括：

- `record_id`, `symbol`, `setup_date`, `primary_trigger`
- `rating`, `setup_score`, `setup_tags`
- `entry_reference`, `stop_reference`, `risk_pct_to_stop`
- `human_label`, `human_decision`, `human_notes`
- `outcomes.3d` 和 `outcomes.5d`
- `overall_outcome`, `matured`, `raw_candidate`

## 解释规则

- `STRONG_WINNER`：5 天收盘回报 >= 8% 或 MFE >= 12%，且无止损击穿
- `WORKED`：5 天收盘回报 >= 4% 或 MFE >= 6%，且无止损击穿
- `FAILED_STOP`：止损在时间范围内被触及
- `FAILED_FADE`：向前回报 <= -2% 且无记录的止损击穿
- `CHOPPY_FAILURE`：不利波动较大且向前进展不佳
- `NEUTRAL`：无决定性延续或失败
- `PENDING`：未来数据条目不足

## 输出

- `state/stockbee/model_book.jsonl` - 持久化的设置模型书
- `stockbee_setup_fluency_ingest_YYYY-MM-DD_HHMMSS.json/md`
- `stockbee_setup_fluency_update_YYYY-MM-DD_HHMMSS.json/md`
- `stockbee_setup_fluency_summary_YYYY-MM-DD_HHMMSS.json/md`

## 资源

- `references/model_book_schema.md` - JSONL 架构和生命周期状态
- `references/outcome_tags.md` - 结果分类和标签定义
- `references/review_workflow.md` - 每日、3 天、5 天和月度审查流程
