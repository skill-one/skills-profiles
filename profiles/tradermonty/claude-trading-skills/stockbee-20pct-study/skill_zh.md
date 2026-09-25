# Stockbee 20% 研究分析

构建一个针对美国股票的每日事件研究，涵盖在定义窗口期内涨幅或跌幅达到 ±20% 的股票。将大幅波动股票转换为结构化研究记录，对催化剂和图表背景进行分类，更新未来结果，并总结重复出现的模式以供研究使用。

这项技能是一个研究、模型书和设置流畅性工作流。它不会生成买入/卖出信号、下单或输出经纪商执行指令。

## 使用场景

- 用户希望运行 Stockbee 风格的每日 ±20% 波动股票研究
- 用户询问今天、本周或在一个可配置的回溯窗口期内哪些股票涨幅或跌幅达到 ±20%
- 用户希望回填历史 ±20% 波动股票并研究接下来发生了什么
- 用户希望识别延续、反转、耗尽或主题集群模式
- 用户希望构建一个包含爆发性赢家、重大失败和失败的低质量弹升的模型书
- 用户希望为下游策略研究提供边缘提示，而不是立即的交易信号

## 前置条件

- Python 3.9+
- FMP API 密钥用于实时美国股票池扫描，或通过 `--prices-json` 获取离线 OHLCV JSON 数据
- 可选的结构化新闻/催化剂 JSON 数据，用于更高质量的催化剂分类
- 推荐使用 `market-regime-daily` 生成的市场状态文件
- 推荐本地状态路径：`state/stockbee/20pct_study_events.jsonl`

## 工作流程

### 第 1 步：扫描 ±20% 波动股票

在美股市场收盘后运行，或针对离线 OHLCV 文件中的最新完整日 K 线

```bash
python3 skills/stockbee-20pct-study/scripts/run_20pct_study.py scan \
  --fmp-universe \
  --max-symbols 300 \
  --as-of 2026-06-28 \
  --lookback-days 5 \
  --min-abs-return-pct 20 \
  --min-price 5 \
  --min-dollar-volume 20000000 \
  --include-down-movers \
  --state-file state/stockbee/20pct_study_events.jsonl \
  --output-dir reports/
```

使用离线数据替代 FMP：

```bash
python3 skills/stockbee-20pct-study/scripts/run_20pct_study.py scan \
  --prices-json data/us_daily_ohlcv.json \
  --as-of 2026-06-28 \
  --lookback-days 5 \
  --include-down-movers \
  --state-file state/stockbee/20pct_study_events.jsonl \
  --output-dir reports/
```

### 第 2 步：丰富和分类事件

在可用时使用结构化催化剂数据。丰富步骤尽力而为：如果找不到新闻记录，事件将保持为仅价格信息的 `NO_CLEAR_NEWS` 研究记录。

```bash
python3 skills/stockbee-20pct-study/scripts/run_20pct_study.py enrich \
  --events-json reports/stockbee_20pct_events_YYYY-MM-DD_HHMMSS.json \
  --news-json data/catalysts_YYYY-MM-DD.json \
  --market-regime reports/market_regime_latest.json \
  --state-file state/stockbee/20pct_study_events.jsonl \
  --output-dir reports/
```

### 第 3 步：更新成熟的未来结果

在存在足够多未来 K 线后更新 1 天、3 天、5 天、10 天和 20 天的未来结果。

```bash
python3 skills/stockbee-20pct-study/scripts/run_20pct_study.py update-outcomes \
  --prices-json data/us_daily_ohlcv.json \
  --state-file state/stockbee/20pct_study_events.jsonl \
  --horizons 1,3,5,10,20 \
  --output-dir reports/
```

更新记录将包含收盘回报、MFE、MAE、方向调整的延续回报和结果标签。

### 第 4 步：总结群体

```bash
python3 skills/stockbee-20pct-study/scripts/run_20pct_study.py summarize \
  --state-file state/stockbee/20pct_study_events.jsonl \
  --group-by direction,catalyst.label,technical_context.pattern_label,technical_context.close_quality \
  --min-sample 10 \
  --output-dir reports/
```

将 `rule_candidates` 和导出的边缘提示视为研究提示。在更改交易规则之前，需要代表性图表审查、样本量阈值和样本外验证。

### 第 5 步：历史回填

```bash
python3 skills/stockbee-20pct-study/scripts/run_20pct_study.py backfill \
  --from 2020-01-01 \
  --to 2026-06-28 \
  --prices-json data/us_daily_ohlcv.json \
  --min-abs-return-pct 20 \
  --include-down-movers \
  --state-file state/stockbee/20pct_study_events.jsonl \
  --output-dir reports/
```

回填记录默认标记为 `CURRENT_UNIVERSE_BACKFILL_SURVIVORSHIP_BIAS`。仅在提供的 OHLCV 包含退市股票和历史股票池覆盖时添加 `--survivorship-complete`。

## 输出格式

- `stockbee_20pct_events_YYYY-MM-DD_HHMMSS.json` — 扫描元数据和事件记录
- `stockbee_20pct_daily_report_YYYY-MM-DD_HHMMSS.md` — 人类可读的每日 ±20% 研究报告
- `stockbee_20pct_enriched_YYYY-MM-DD_HHMMSS.json` — 丰富的事件记录
- `stockbee_20pct_outcome_update_YYYY-MM-DD_HHMMSS.json/md` — 成熟的未来结果更新
- `stockbee_20pct_cohort_summary_YYYY-MM-DD_HHMMSS.json/md` — 群体统计和规则候选
- `stockbee_20pct_edge_hints_YYYY-MM-DD_HHMMSS.yaml` — 用于下游研究技能的边缘提示导出
- `state/stockbee/20pct_study_events.jsonl` — 持久的 ±20% 波动股票模型书

## 资源

- `references/methodology.md` — ±20% 研究方法和审查清单
- `references/event_schema.md` — JSONL 事件记录架构
- `references/catalyst_taxonomy.md` — 催化剂和风险标签定义
- `references/scoring_system.md` — 事件质量和研究优先级评分
- `references/cohort_mining_rules.md` — 过拟合控制和样本量规则
- `scripts/run_20pct_study.py` — 用于扫描、丰富、更新结果、总结和回填的 CLI
