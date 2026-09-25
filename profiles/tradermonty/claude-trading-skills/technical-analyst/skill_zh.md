# 技术分析师

## 概述

这项技能能够对周线价格图表进行全面的技术分析。通过分析图表图像，识别趋势、支撑与阻力水平、移动平均关系、成交量模式，并针对未来价格走势制定概率性情景。所有分析均基于客观的图表数据，不受新闻、基本面或市场情绪的影响。

## 使用场景

- 用户提供周线图表图像（股票、指数、加密货币、外汇）并请求技术分析
- 需要识别趋势方向、强度和潜在反转点
- 寻找支撑/阻力水平以及关键价格区域
- 希望进行具有具体价格目标的概率性情景规划
- 需要基于图表的客观分析，不考虑基本面或新闻因素

## 前置条件

- **图表图像**：用户必须提供用于分析的周线时间框架图表图像
- **无需API密钥**：此技能分析用户提供的图像；无需外部数据获取

## 输出

此技能生成保存到`reports/`目录的markdown分析报告：
- **文件格式**：`[SYMBOL]_technical_analysis_[YYYY-MM-DD].md`
- **内容**：包括趋势、S/R水平、MA分析、成交量、模式以及2-4个具有目标值和失效水平的概率性情景的全面分析

## 核心原则

1. **纯图表分析**：所有结论均仅基于图表中可见的技术数据
2. **系统化方法**：对每个图表分析遵循结构化的方法论
3. **客观评估**：避免主观偏见；专注于可观察的模式和数据
4. **概率性情景**：将未来可能性表达为概率加权的情景
5. **顺序处理**：逐个分析每个图表并立即记录发现

## 分析工作流程

### 第1步：接收图表图像

当用户提供一个或多个用于分析的周线图表图像时：

1. 确认收到所有图表图像
2. 确定要分析的图表数量
3. 记录用户请求的任何特定关注区域
4. 依次逐个分析图表

### 第2步：加载技术分析框架

在开始分析之前，阅读全面的技术分析方法论：

```
读取：references/technical_analysis_framework.md
```

该参考包含以下详细指导：
- 趋势分析和分类
- 支撑和阻力识别
- 移动平均解读
- 成交量分析
- 图表模式和K线分析
- 情景开发和概率分配
- 分析纪律和客观性

### 第3步：系统化分析每个图表

对每个图表图像，按照以下顺序进行系统化分析：

#### 3.1 趋势分析
- 识别趋势方向（上升趋势、下降趋势、横盘整理）
- 评估趋势强度（强、中、弱）
- 记录趋势持续时间及潜在的衰竭信号
- 检查更高高点/更低低点或更低高点/更高低点模式

#### 3.2 支撑和阻力分析
- 标记重要的水平支撑位
- 标记重要的水平阻力位
- 识别趋势线支撑/阻力
- 记录任何支撑/阻力角色的反转
- 评估多个S/R水平重合的汇聚区域

#### 3.3 移动平均分析
- 确定价格相对于20周、50周和200周MA的位置
- 评估MA排列（看涨、看跌或中性配置）
- 记录MA斜率（上升、下降、平缓）
- 识别任何最近的或即将发生的MA交叉
- 观察MA作为动态支撑或阻力

#### 3.4 成交量分析
- 评估整体成交量趋势（增加、减少、稳定）
- 识别成交量峰值及其上下文（在支撑/阻力位、突破时）
- 检查成交量与价格的确认或背离
- 记录任何成交量顶峰或衰竭模式

#### 3.5 图表模式和价格行为
- 识别任何反转模式（锤子线、上吊线、吞没模式等）
- 识别任何延续模式（旗形、三角形等）
- 记录重要的K线形态
- 观察最近的突破或跌破

#### 3.6 综合观察
- 将所有技术要素整合为连贯的当前评估
- 识别影响图表的最显著因素
- 记录任何冲突信号或模糊之处
- 确定决定未来方向的关键水平

### 第4步：制定概率性情景

对每个分析的图表，创建2-4个不同的未来价格走势情景：

#### 情景结构

每个情景必须包括：
1. **情景名称**：清晰、描述性的标题（例如，“看涨情景：突破阻力位”）
2. **概率估计**：基于技术因素的百分比可能性（所有情景的概率总和必须为100%）
3. **描述**：该情景包含的内容及其如何展开
4. **支持因素**：支持该情景的技术证据（至少2-3个因素）
5. **目标水平**：如果情景实现，预期的价格水平
6. **失效水平**：会使该情景失效的特定价格水平

#### 典型情景框架

- **基准情景（40-60%）**：基于当前结构的可能性最高的结果
- **看涨情景（20-40%）**：需要向上突破的乐观情景
- **看跌情景（20-40%）**：需要向下突破的悲观情景
- **替代情景（5-15%）**：较低概率但技术上可能的结果

根据支持技术因素的力量调整概率。确保概率是现实的，总和为100%。

### 第5步：生成分析报告

对每个分析的图表，使用以下模板结构创建全面的markdown报告：

```
读取并使用作为模板：assets/analysis_template.md
```

报告必须包括所有部分：
1. 图表概述
2. 趋势分析
3. 支撑和阻力水平
4. 移动平均分析
5. 成交量分析
6. 图表模式和价格行为
7. 当前市场评估
8. 情景分析（2-4个情景及概率）
9. 总结
10. 声明

**文件命名约定**：将每个分析保存为`[SYMBOL]_technical_analysis_[YYYY-MM-DD].md`

示例：`SPY_technical_analysis_2025-11-02.md`

### 第6步：重复分析多个图表

如果提供多个图表：

1. 完成第一个图表的完整分析工作流（步骤3-5）
2. 保存分析报告
3. 继续下一个图表
4. 重复，直到所有图表都已分析和记录

不要批量分析。在移动到下一个图表之前，完成并保存每个报告。

## 质量标准

### 客观性要求

- 所有分析严格基于可观察的图表数据
- 避免纳入外部信息（新闻、基本面、情绪）
- 不要使用主观语言，如“我认为”或“我感觉”
- 当信号模糊时，明确表达不确定性
- 提供看涨和看跌可能性，避免确认偏差

### 完整性要求

- 涵盖分析模板的所有部分
- 提供支撑、阻力和目标的具体价格水平
- 用技术因素证明概率估计
- 包括每个情景的失效水平
- 记录分析的任何局限性或注意事项

### 清晰性要求

- 正确使用精确的技术术语
- 使用清晰、专业的语言
- 逻辑地组织信息
- 包括具体价格水平（而不是模糊描述）
- 使情景清晰且互斥

## 示例使用场景

**示例1：单个图表分析**
```
用户：“请分析这张标普500的周线图表”
[提供图表图像]

分析师：
1. 确认收到图表图像
2. 读取technical_analysis_framework.md以获取方法论
3. 进行系统化分析（趋势、S/R、MA、成交量、模式）
4. 制定3个情景并给出概率（例如，55%看涨延续，30%盘整，15%反转）
5. 使用模板生成全面分析报告
6. 保存为SPY_technical_analysis_2025-11-02.md
```

**示例2：多个图表分析**
```
用户：“分析这三个图表：比特币、以太坊和纳斯达克”
[提供3个图表图像]

分析师：
1. 确认收到3个图表
2. 读取technical_analysis_framework.md
3. 完全分析比特币图表 → 生成报告 → 保存为BTC_technical_analysis_2025-11-02.md
4. 完全分析以太坊图表 → 生成报告 → 保存为ETH_technical_analysis_2025-11-02.md
5. 完全分析纳斯达克图表 → 生成报告 → 保存为NDX_technical_analysis_2025-11-02.md
6. 通知用户所有三个分析已完成
```

**示例3：重点关注分析请求**
```
用户：“我特别关注这只股票是否会突破阻力位。分析图表。”
[提供图表图像]

分析师：
1. 进行全面系统分析
2. 特别关注阻力位和突破可能性
3. 制定侧重于突破与拒绝可能性的情景
4. 根据成交量、趋势强度和距离阻力位的情况分配概率
5. 生成包含重点关注情景分析的完整报告
```

## 反向确认模式（Shapiro第3步）

这是一种附加模式，与上述纯图表分析工作流程分开。它仅在明确的反向确认请求下激活——通常在`cot-contrarian-detector`（第1步）标记市场拥挤后，并且可选地`news-reaction-failure-analyzer`（第2步）显示其未能对有利新闻做出反应时。一个简单的“分析这个图表”请求仍然会运行上述工作流程（步骤1-6）。

### 目的

确认周线图表是否显示价格行为证据表明拥挤的市场正在反转：周线关键反转、周内失败极端或确认后被拒绝的失败突破——被拥挤方向的新收盘极端（比任何发现的信号更近）否决。有关完整、逐字的方法论，请参阅`references/contrarian-confirmation-checklist.md`，图表模式和脚本模式共享此方法论。

### 输入

- **拥挤方向**：`CROWDED_LONG`或`CROWDED_SHORT`——来自用户，或来自先前的`cot-contrarian-detector`报告
- **图表图像（主要）**：用户提供的周线图表，与现有工作流程相同的方式读取，使用严格的定义
- **脚本后备（数据驱动）**：`scripts/check_weekly_price_action.py`，当未提供图表时，或当需要可审计的确定性结果时（或与视觉阅读一起使用）

### 三个检查+摆动水平

1. **周线关键反转**：新的摆动回溯极端（默认13周）后，收盘穿过前一周的相反水平
2. **失败极端**：周内刺穿前极端回溯水平（默认52周），同周收盘穿过它
3. **失败突破**：周线收盘突破前极端回溯水平，在<=3个后续周内被拒绝（`week_of`是失败周，不是突破周）
4. **延续否决**：拥挤方向的新收盘极端，严格比上述最新触发的信号更近，否决确认，无论触发什么
5. **摆动水平**：最近的分形摆动高/低（5周枢轴，有记录的备用方案）提供`stop_reference`——当衰减拥挤LONG时，最近的摆动高；当衰减拥挤SHORT时，最近的摆动低

每个比较都是严格的非等式；窗口截断是按评估的每周，而不是按运行。完整定义、方向镜像表、工作示例和置信度-HIGH规则在`references/contrarian-confirmation-checklist.md`中——在产生图表模式裁决之前阅读它，以便图表和脚本做出相同的判断。

### 输出合同

```yaml
symbol: BT
direction: CROWDED_LONG
mode: data # "chart"用于图表图像阅读
verdict: CONFIRMED | NOT_CONFIRMED | INSUFFICIENT_DATA
confidence: HIGH | MEDIUM | LOW # LOW保留，v1中永不发出
verdict_reason: key_reversal | failed_extreme | failed_breakout |
  continuation_intact | no_reversal_evidence |
  insufficient_weekly_bars | no_price_source | ...
checks:
  weekly_key_reversal:
    { triggered, week_of, swing_window_weeks_used,
      extreme_window_weeks_used, is_full_window_extreme, detail }
  failed_extreme: { triggered, attempted_level, week_of, window_weeks_used, detail }
  failed_breakout: { triggered, breakout_level, week_of, window_weeks_used, detail }
  continuation: { new_closing_extreme_with_crowd, week_of, window_weeks_used }
swing_levels:
  nearest_swing_high: { price, week_of, fallback }
  nearest_swing_low: { price, week_of, fallback }
  stop_reference: 0.0
weekly_bars_used: 52
last_completed_week: 2026-07-06
handoff: # 被contrarian-setup-gate (#241)消耗
  price_action: { verdict, confidence, stop_reference, report_path }
run_context:
  {
    price_symbol,
    price_source,
    proxy_used,
    as_of,
    lookbacks,
    recency,
    min_weeks,
    detector_json,
    detector_age_days,
    schema_version,
  }
```

**不变量**：`checks`（和`swing_levels`）在`verdict: INSUFFICIENT_DATA`时始终为`null`——无论具体原因（`no_price_source`、`insufficient_weekly_bars`、一个detector-json拒绝、...）。下游消费者可以单独检查`verdict`，然后再决定是否安全读取`checks.*`，而无需根据`verdict_reason`分支。

**文件命名**：`ta_confirmation_<SYMBOL>_<as-of>.json`和`ta_confirmation_<SYMBOL>_<as-of>.md`，保存到`reports/`。

### 图表优先，脚本后备

图表图像仍然是主要输入，与本技能的身份一致。当未提供图表时，或当需要可审计的确定性结果时，运行脚本而不是（或与）图表阅读：

```bash
python3 skills/technical-analyst/scripts/check_weekly_price_action.py \
  --symbol BT --direction CROWDED_LONG --as-of 2026-07-15 \
  --output-dir reports/
```

或者直接从`cot-contrarian-detector`报告解析方向：

```bash
python3 skills/technical-analyst/scripts/check_weekly_price_action.py \
  --symbol BT --detector-json reports/cot_crowding_2026-07-12.json \
  --as-of 2026-07-15 --output-dir reports/
```

脚本通过记录的期货到ETF后备链获取周线重采样的OHLC（见`scripts/check_weekly_price_action.py`中的模块文档字符串），在重采样之前截断每日条目到`--as-of`（无前瞻性），并在无法读取（缺失文件）、语法无效、陈旧或结构性地损坏的`--detector-json`、`--min-weeks`（默认30）过少或没有可用价格源时失败关闭到`INSUFFICIENT_DATA`——永远不会崩溃。

### 保守性分歧规则

如果图表模式和脚本模式对同一符号/方向产生结果，并且它们的裁决不一致，最终裁决将是**`NOT_CONFIRMED`**（`verdict_reason: mode_disagreement`），并将两个子结果附加供审查——永远不会在沉默中偏爱一个模式。如果一个是`INSUFFICIENT_DATA`，另一个是干净的裁决，则干净的裁决有效。

### 安全机制

- **仅裁决——永远不会单独给出交易建议。** 这确认了Shapiro流程的第3步。入场和出场规划仍然是手动且必需的；头寸规模属于`position-sizer` / `futures-position-sizer`，而不是此模式。
- **`INSUFFICIENT_DATA`永远不会推进管道**——对每个退化输入失败关闭，始终以0退出并写入报告。
- **仅周线时间框架。**
- **现有的图表分析工作流程保持不变**——此模式仅在明确的反向确认请求下激活。
- **单个信号的中等裁决是故意弱的证据**——见`references/contrarian-confirmation-checklist.md`的置信度部分。

## 资源

此技能包括以下捆绑资源：

### references/technical_analysis_framework.md

全面的技术分析方法论，包括：
- 趋势分析标准和分类
- 支撑和阻力识别技术
- 移动平均解读指南
- 成交量分析原则
- 图表模式识别
- 情景开发和概率分配框架
- 客观性和纪律提醒

**使用**：在进行分析前阅读此文件，以确保系统化、客观的方法。

### assets/analysis_template.md

具有所有必需部分的结构的结构化技术分析报告模板。

**使用**：为每个分析使用此模板结构。复制格式并填充每个图表的具体发现。

### references/contrarian-confirmation-checklist.md

反向确认模式（Shapiro第3步）的完整方法论：方向约定、窗口/截断规则、3个信号检查+延续否决、摆动水平（分形枢轴）规则、裁决综合、置信度规则、输出合同、图表模式演练和保守性分歧规则。

**使用**：在生成反向确认模式裁决前阅读此文件——图表模式和`scripts/check_weekly_price_action.py`必须做出相同的判断，因此两者都适用相同的严格定义。

### scripts/check_weekly_price_action.py

反向确认模式的备用CLI。获取周线重采样的OHLC（记录的期货到ETF后备链，`--as-of`信息在重采样前截止），运行3个信号检查+延续否决+摆动水平检测，并将`ta_confirmation_<SYMBOL>_<as-of>.json`/`.md`写入`reports/`。

**使用**：当未提供图表图像时，或当需要可审计的确定性结果时运行。有关调用示例，请参阅上述反向确认模式部分。
