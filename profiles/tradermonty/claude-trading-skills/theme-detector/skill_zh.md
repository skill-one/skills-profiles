# 主题检测器

## 概述

该技能通过分析跨行业动能、成交量和广度信号来检测和排名市场热门主题。它识别看涨（向上动能）和看跌（向下压力）主题，评估生命周期成熟度（新兴/加速/趋势/成熟/衰竭），并结合定量数据与叙事分析提供置信度评分。

**三维评分模型：**
1. **主题热度** (0-100)：方向中性的主题强度（动能、成交量、上升趋势比率、广度）
2. **生命周期成熟度**：阶段分类（新兴 / 加速 / 趋势 / 成熟 / 衰竭）基于持续时间、极端性聚类、估值和ETF扩散
3. **置信度** (低 / 中 / 高)：检测的可靠性，结合定量广度与叙事确认。脚本输出上限为中等；Claude的WebSearch叙事确认步骤可提升至高。
4. **股票领导力**：可选的每日扫描命中证据（5D+20%、EP9M、区间扩张、新高和高RS股票）。当提供时，此信息会融入主题热度v2；当缺失时，会降低置信度覆盖但不会将领导力强制设为零。
5. **主题匹配质量**：从行业参与、明确股票篮子命中、代理ETF确认和可选的离线叙事评分中确定主题匹配的特异性。这是证据质量，不是交易建议。

**主要功能：**
- 使用FINVIZ行业数据进行的跨行业主题检测
- 方向感知评分（看涨和看跌主题）
- 生命周期成熟度评估以识别拥挤与新兴交易
- ETF扩散评分（ETF越多=越成熟/拥挤的主题）
- 与上升趋势仪表板的集成进行3点评估
- 通过`--scan-hits`提供股票级领导力证据
- 通过明确股票篮子和代理ETF确认提供主题匹配质量
- 按异常波动/成交量/区间/RS指标排名的领导者候选证据，市值仅作为风险桶显示
- 通过`--history-file`提供主题历史和加速指标
- 双模式操作：FINVIZ精英（快速）或公共抓取（较慢、有限）
- 基于WebSearch的叙事确认用于顶级主题

---

## 何时使用此技能

**明确触发器：**
- “当前哪些市场主题正在流行？”
- “哪些行业是热门/冷门？”
- “检测当前市场主题”
- “哪些是最强的看涨/看跌叙事？”
- “AI/清洁能源/国防是否仍然是强劲主题？”
- “行业轮动将走向何方？”
- “向我展示主题投资机会”

**隐含触发器：**
- 用户希望理解广泛的市况叙事变化
- 用户正在寻找主题ETF或行业配置想法
- 用户询问拥挤的交易或晚周期主题
- 用户想知道哪些主题正在新兴而非衰竭

**不使用时：**
- 个股分析（请使用us-stock-analysis）
- 带图表阅读的特定行业深度分析（请使用sector-analyst）
- 投资组合再平衡（请使用portfolio-manager）
- 股息/收入投资（请使用value-dividend-screener）

---

## 前置条件

**必需：**
- Python 3.9+ 及核心依赖项。
  ```bash
  pip install -r skills/theme-detector/requirements.txt
  ```

**Cron / 混合Python回退**：如果活动的 `python3` 早于3.10，或者更新的Hermes venv缺少数据科学依赖项，请通过 `uv` 使用显式的现代解释器和临时依赖项运行检测器，而不是在cron期间编辑环境：
```bash
uv run --python 3.12 \
  --with requests --with beautifulsoup4 --with lxml \
  --with pandas --with numpy --with yfinance \
  --with finvizfinance --with PyYAML \
  python skills/theme-detector/scripts/theme_detector.py \
  --finviz-api-key "$FINVIZ_API_KEY" \
  --fmp-api-key "$FMP_API_KEY" \
  --output-dir reports/
```
将其用作设置绕过方案，而不是作为检测器损坏的证据；仍然单独报告FINVIZ/FMP/API-data注意事项。

**可选API密钥：**

FINVIZ精英（推荐用于完整行业覆盖和速度）：
```bash
export FINVIZ_API_KEY=your_finviz_elite_api_key_here
```

FMP API（可选，用于P/E比率估值数据）：
```bash
export FMP_API_KEY=your_fmp_api_key_here
```

要求包括 `finvizfinance`、PyYAML、pandas/numpy、requests和
yfinance，因为正常公共模式执行会导入或使用它们中的每一个。

没有FINVIZ精英，该技能使用公共FINVIZ抓取（限制为每个行业约20只股票，速率限制较慢）。

---

## 工作流程

### 第1步：验证环境

检查API密钥是否配置（见前置条件）：

```bash
# 验证FINVIZ精英API密钥（可选但推荐）
echo $FINVIZ_API_KEY

# 验证FMP API密钥（可选）
echo $FMP_API_KEY
```

### 第2步：执行主题检测脚本

运行主检测脚本：

```bash
python3 skills/theme-detector/scripts/theme_detector.py \
  --output-dir reports/
```

**脚本选项：**
```bash
# 全部运行（公共FINVIZ模式，无需API密钥）
python3 skills/theme-detector/scripts/theme_detector.py \
  --output-dir reports/

# 使用FINVIZ精英API密钥
python3 skills/theme-detector/scripts/theme_detector.py \
  --finviz-api-key $FINVIZ_API_KEY \
  --output-dir reports/

# 使用FMP API密钥以获取增强股票数据
python3 skills/theme-detector/scripts/theme_detector.py \
  --fmp-api-key $FMP_API_KEY \
  --output-dir reports/

# 自定义限制
python3 skills/theme-detector/scripts/theme_detector.py \
  --max-themes 5 \
  --max-stocks-per-theme 10 \
  --output-dir reports/

# 显式FINVIZ模式
python3 skills/theme-detector/scripts/theme_detector.py \
  --finviz-mode public \
  --output-dir reports/

# 添加Stockbee/Pradeep风格的领导力证据
python3 skills/theme-detector/scripts/theme_detector.py \
  --scan-hits data/theme_scan_hits_YYYY-MM-DD.json \
  --narrative-scores data/theme_narrative_scores_YYYY-MM-DD.json \
  --history-file reports/theme_detector_history.json \
  --as-of-date YYYY-MM-DD \
  --output-dir reports/
```

**扫描命中输入合同**：`--scan-hits` 接受JSON、JSONL或CSV。行可以预先标记为 `scan_type` / `scan_types`，或者包含 `symbol`、`return_5d`、`change_pct`、`volume`、`avg_volume_50d`、`relative_volume`、`true_range`、`atr_20`、`atr_expansion`、`close_location`、`industry`、`sector` 和 `theme_guess` 等字段的原始行。当原始行满足多个规则时，它可以扩展成多个命中。

初始扫描规则：
- `five_day_20pct`：`return_5d >= 20`
- `ep9m`：`volume >= 9,000,000`，`relative_volume >= 2.0`，且 `change_pct >= 4`
- `range_expansion`：`change_pct >= 4`，`true_range / atr_20 >= 1.5` 或 `atr_expansion >= 1.5`，且 `close_location >= 0.75`
- `new_high`：显式 `new_high` / `is_new_high`，或52周高证据
- `high_rs`：`rs_rating >= 90` 或标准化 `relative_strength >= 0.90`

**叙事评分输入合同**：`--narrative-scores` 是一个离线JSON输入，不是实时WebSearch调用。它接受 `{"Theme Name": 82}` 或 `{"themes": {"Theme Name": {"narrative_keyword_score": 82}}}`。缺少叙事输入会使 `narrative_keyword_score` 为 `null` 并降低 `theme_match_coverage`；它不会导致运行失败。

**预期执行时间：**
- FINVIZ精英模式：~2-3分钟（14+主题）
- 公共FINVIZ模式：~5-8分钟（速率限制抓取）

### 第3步：读取和解析检测结果

脚本生成两个输出文件：
- `theme_detector_YYYY-MM-DD_HHMMSS.json` - 结构化数据用于程序使用
- `theme_detector_YYYY-MM-DD_HHMMSS.md` - 人类可读报告

读取JSON输出以了解定量结果：

```bash
# 查找最新报告
ls -lt reports/theme_detector_*.json | head -1

# 读取JSON输出
cat reports/theme_detector_YYYY-MM-DD_HHMMSS.json
```

### 第4步：通过WebSearch执行叙事确认

针对前5个主题（按主题热度评分排序），执行WebSearch查询以确认叙事强度：

**搜索模式：**
```
"[theme name] stocks market [current month] [current year]"
"[theme name] sector momentum [current month] [current year]"
```

**评估叙事信号：**
- **强叙事**：多个主要媒体覆盖主题，分析师上调，政策催化剂
- **中等叙事**：一些覆盖，混合情绪，没有明确的催化剂
- **弱叙事**：很少覆盖，或主要是反方/怀疑论调

根据发现更新置信度级别：
- 定量高 + 叙事强 = **高** 置信度
- 定量高 + 叙事弱 = **中** 置信度（可能的动能分化）
- 定量低 + 叙事强 = **中** 置信度（叙事可能引导价格）
- 定量低 + 叙事弱 = **低** 置信度

### 第5步：分析结果并提供建议

将检测结果与知识库进行交叉参考：

**参考文档：**
1. `references/cross_sector_themes.md` - 主题定义和构成行业
2. `references/thematic_etf_catalog.md` - 按主题的ETF敞口选项
3. `references/theme_detection_methodology.md` - 评分模型细节
4. `references/finviz_industry_codes.md` - 行业分类参考

**分析框架：**

对于 **热门看涨主题**（热度 >= 70，方向 = 看涨）：
- 确定生命周期阶段（新兴 = 机会，成熟/衰竭 = 谨慎）
- 列出主题内表现最好的行业
- 推荐主题ETF进行敞口
- 如果ETF扩散度高（拥挤交易警告），请标记

对于 **热门看跌主题**（热度 >= 70，方向 = 看跌）：
- 确定受压力的行业
- 评估看跌动能是加速还是减速
- 推荐对冲策略或要避免的板块
- 如果生命周期是成熟/衰竭，注意均值回归机会

对于 **新兴主题**（热度 40-69，生命周期 = 新兴）：
- 这些可能代表早期轮动信号
- 建议添加到观察列表
- 确定可能加速主题的催化剂事件

对于 **衰竭主题**（热度 >= 60，生命周期 = 衰竭）：
- 警告拥挤交易风险
- 高ETF数量确认了过多的散户参与
- 考虑反方头寸或减少敞口

### 第6步：生成最终报告

使用报告模板结构向用户展示最终报告：

```markdown
# 主题检测报告
**日期：** YYYY-MM-DD
**模式：** FINVIZ精英 / 公共
**分析主题数：** N
**数据质量：** [注意任何限制]

## 主题仪表板
[前主题表格，带热度、方向、生命周期、置信度]

## 今日变化
[新出现主题、最大热度加速、新EP9M集群、衰减主题]

## 领导力证据
[5D+20%、EP9M、区间扩张、新高、高RS计数和领导者符号]

## 看涨主题详情
[按热度排序的看涨主题详细分析]

## 看跌主题详情
[按热度排序的看跌主题详细分析]

## 所有主题摘要
[完整主题排名表]

## 行业排名
[表现最好和最差的行业]

## 板块上升趋势率
[如果可用，提供板块级聚合]

## 方法论说明
[评分模型的简要解释]
```

将报告保存到 `reports/` 目录。

---

## 输出

该技能在 `reports/` 目录中生成两个输出文件：

**JSON输出** (`theme_detector_YYYY-MM-DD_HHMMSS.json`)：
```json
{
  "report_type": "theme_detector",
  "generated_at": "2026-04-18 10:30:00",
  "metadata": {
    "generated_at": "2026-04-18 10:30:00",
    "data_mode": "full",
    "finviz_mode": "elite",
    "fmp_available": true,
    "max_themes": 14,
    "max_stocks_per_theme": 5,
    "data_sources": {
      "finviz_industries": 152,
      "yfinance_stocks": 68,
      "etf_volume": 24
    }
  },
  "summary": {
    "total_themes": 14,
    "bullish_count": 8,
    "bearish_count": 6,
    "top_bullish": "AI & Machine Learning",
    "top_bearish": "Regional Banks"
  },
  "themes": {
    "all": [
      {
        "name": "AI & Machine Learning",
        "direction": "bullish",
        "heat": 85.3,
        "maturity": 42.1,
        "stage": "Accelerating",
        "confidence": "Medium",
        "heat_label": "Hot",
        "industries": ["Software - Infrastructure", "Semiconductors"],
        "representative_stocks": ["NVDA", "MSFT"],
        "stock_details": [{"symbol": "NVDA"}, {"symbol": "MSFT"}],
        "proxy_etfs": ["BOTZ", "ROBO"],
        "theme_match_score": 78.4,
        "theme_match_components": {
          "industry_match_score": 84.2,
          "static_stock_hit_score": 80.0,
          "proxy_etf_momentum_score": 70.0,
          "narrative_keyword_score": null
        },
        "leader_candidates": [
          {
            "symbol": "NVDA",
            "leader_score": 91.2,
            "scan_types": ["ep9m", "range_expansion"],
            "risk_bucket": "mega"
          }
        ],
        "theme_origin": "seed"
      }
    ],
    "bullish": [...],
    "bearish": [...],
    "match_ranked": [...]
  },
  "industry_rankings": {
    "top": [...],
    "bottom": [...]
  },
  "sector_uptrend": {...},
  "data_quality": {...}
}
```

**Markdown报告** (`theme_detector_YYYY-MM-DD_HHMMSS.md`)：
- 可排序的主题仪表板
- 看涨/看跌主题详细部分
- 行业表现排名
- 板块上升趋势率摘要
- 方法论说明

**每个主题的关键输出字段：**
| 字段 | 描述 |
|-------|-------------|
| `heat` | 0-100方向中性的主题强度 |
| `direction` | `"bullish"` (LEAD) 或 `"bearish"` (LAG) |
| `stage` | 新兴 / 加速 / 趋势 / 成熟 / 衰竭 |
| `confidence` | 低 / 中 / 高（脚本上限为中等；WebSearch可提升至高） |
| `representative_stocks` | 主题的顶级股票代码 |
| `stock_details` | 可选的选股指标对象，用于选股代表 |
| `proxy_etfs` | 主题ETF代码（长度=ETF数量；越高=越拥挤） |
| `theme_match_score` | 0-100证据质量评分，来自行业参与、股票篮子命中、代理ETF确认和可选的叙事输入 |
| `theme_match_components` | 可检查的子分数，解释主题匹配 |
| `leader_candidates` | 主题证据排名的符号；不是入场/止损/无效化指导 |
| `fresh_leadership_symbols` | 当前运行中具有EP9M、区间扩张或新高证据的符号 |
| `extended_symbols` | 当前运行中具有5D+20%证据的符号；仅用作超卖证据 |
| `theme_origin` | `"seed"`（来自YAML配置）或 `"discovered"`（自动聚类） |

---

## 资源

### 脚本目录 (`scripts/`)

**主脚本：**
- `theme_detector.py` - 主协调脚本
  - 协调行业数据收集、主题分类和评分
  - 生成JSON + Markdown输出
  - 使用方法：`python3 theme_detector.py [选项]`

- `theme_classifier.py` - 将行业映射到跨行业主题
  - 从 `cross_sector_themes.md` 读取主题定义
  - 计算主题级聚合评分
  - 从构成行业确定方向（看涨/看跌）
  - 显示映射："看涨" → **LEAD**，"看跌" → **LAG**（见 `report_generator.py::_direction_label()`）

- `finviz_industry_scanner.py` - FINVIZ行业数据收集
  - 精英模式：每个行业完整的股票数据CSV导出
  - 公共模式：带速率限制的Web抓取
  - 提取：表现、成交量、变化%、平均成交量、市值

- `calculators/lifecycle_calculator.py` - 生命周期成熟度评估
  - 持续时间评分、极端性聚类、估值分析
  - ETF扩散评分来自 `thematic_etf_catalog.md`
  - 阶段分类：新兴 / 加速 / 趋势 / 成熟 / 衰竭

- `report_generator.py` - 报告输出生成
  - 从模板生成Markdown报告
  - 结构化JSON输出
  - 主题仪表板格式化

### 参考文档目录 (`references/`)

**知识库：**
- `cross_sector_themes.md` - 主题定义、行业、ETF、股票和匹配标准
- `thematic_etf_catalog.md` - 主题ETF目录，按主题计数
- `finviz_industry_codes.md` - 完整的FINVIZ行业到过滤代码映射
- `theme_detection_methodology.md` - 3D评分模型的技术文档

### 资产目录 (`assets/`)

- `report_template.md` - 报告生成Markdown模板，带占位符格式

---

## 交易日历和重播

在运行检测器之前安装 `requirements.txt`。`--as-of-date` 是严格的 `YYYY-MM-DD` 封顶，用于上升趋势新鲜度检查和提供者历史窗口。由于FINVIZ、报价、资料和上升趋势输入是实时而非PIT快照，非当前的 `--as-of-date` 会失败关闭。新鲜度计算XNYS会话，并排除未来日期的源行。

## 重要说明

### FINVIZ模式差异

| 功能 | 精英模式 | 公共模式 |
|---------|-----------|-------------|
| 行业覆盖 | 所有 ~145个行业 | 所有 ~145个行业 |
| 每个行业的股票 | 完整宇宙 | ~20只股票（第1页） |
| 速率限制 | 0.5秒请求间隔 | 2.0秒请求间隔 |
| 数据新鲜度 | 实时 | 15分钟延迟 |
| API密钥要求 | 是 ($39.50/月) | 否 |
| 执行时间 | ~2-3分钟 | ~5-8分钟 |

### 方向检测逻辑

主题方向由构成行业的相对排名多数决定：

1. **行业排名**：所有 ~145个行业按多时间框架动能评分排名
2. **基于排名的方向**：排名前半部分的行业被归类为“看涨”；后半部分为“看跌”
3. **主题多数投票**：`_majority_direction()` 计数每个主题中看涨与看跌行业的多数；多数获胜

显示映射："看涨" → **LEAD**，"看跌" → **LAG**（见 `report_generator.py::_direction_label()`）

LEAD主题表示其构成行业的相对表现。LAG主题可能仍有正向绝对回报——它表示相对表现不佳，不是短期信号。

### 已知限制

1. **生存偏差**：仅分析当前上市股票和ETF
2. **滞后**：FINVIZ数据可能滞后日内变动15分钟（公共模式）
3. **主题边界**：某些股票适合多个主题；分类使用主要行业
4. **ETF扩散**：目录是静态的，可能不会捕获非常新的ETF
5. **叙事评分**：基于WebSearch，本质上主观
6. **公共模式限制**：每个行业~20只股票可能遗漏小盘股信号

### 声明

**此分析仅用于教育和信息目的。**
- 不是投资建议
- 过去的主题趋势不能保证未来表现
- 主题检测识别动能，不是基本面价值
- 在做出投资决策之前进行自己的研究

---

**版本：** 1.0
**最后更新：** 2026-02-16
**API要求：** FINVIZ精英（推荐）或公共模式（免费）；可选FMP API
**执行时间：** ~2-8分钟（取决于模式）
**输出格式：** JSON + Markdown
**覆盖主题：** 14+ 跨行业主题
