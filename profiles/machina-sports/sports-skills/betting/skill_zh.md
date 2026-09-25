# 赌注分析

在编写查询之前，请查阅 `references/api-reference.md` 以获取赔率格式、命令参数和关键概念的信息。

## 快速入门

```bash
sports-skills betting convert_odds --odds=-150 --from_format=american
sports-skills betting devig --odds=-150,+130 --format=american
sports-skills betting find_edge --fair_prob=0.58 --market_prob=0.52
sports-skills betting evaluate_bet --book_odds=-150,+130 --market_prob=0.52
sports-skills betting find_arbitrage --market_probs=0.48,0.49
sports-skills betting parlay_analysis --legs=0.58,0.62,0.55 --parlay_odds=600
sports-skills betting line_movement --open_odds=-140 --close_odds=-160
```

Python SDK:
```python
from sports_skills import betting

betting.convert_odds(odds=-150, from_format="american")
betting.devig(odds="-150,+130", format="american")
betting.find_edge(fair_prob=0.58, market_prob=0.52)
betting.find_arbitrage(market_probs="0.48,0.49")
betting.parlay_analysis(legs="0.58,0.62,0.55", parlay_odds=600)
betting.line_movement(open_odds=-140, close_odds=-160)
```

## 关键：在进行任何分析之前

关键：在调用任何分析命令之前，请验证：
- 赔率格式是否正确识别（美式、小数或概率）。
- 在计算预测市场价格与赔率之间的优势之前，使用 `devig` 对ESPN赔率进行去 vigging。
- 该模块用于计算，而不是获取。首先从特定运动的技能或 polymarket/kalshi 获取赔率。

## 工作流程

### 比较 ESPN 与 Polymarket/Kalshi

1. 获取ESPN moneyline赔率（例如，从 `nba get_scoreboard`）：主队：`-150`，客队：`+130`
2. 获取Polymarket/Kalshi对相同结果的报价（例如，主队为 `0.52`）
3. 去 vigging：`devig --odds=-150,+130 --format=american` → 公平：主队 57.9%，客队 42.1%
4. 比较：`find_edge --fair_prob=0.579 --market_prob=0.52` → 优势：5.9%，预期收益：11.3%
5. 或者一步到位：`evaluate_bet --book_odds=-150,+130 --market_prob=0.52`

### 备兑检测

1. 从不同来源获取每个结果的最佳报价（Polymarket主队为 0.48，Kalshi客队为 0.49）
2. `find_arbitrage --market_probs=0.48,0.49 --labels=home,away`
3. 总隐含概率 0.97 (< 1.0) → 发现备兑，保证 ROI：3.09%

### 备兑评估

1. 去 vigging 每个投注：投注1 → 0.58，投注2 → 0.55，投注3 → 0.50
2. `parlay_analysis --legs=0.58,0.55,0.50 --parlay_odds=600`
3. 返回组合公平概率、优势和凯利分数

### 线变动分析

1. 获取ESPN开盘和收盘线：开盘 -140，收盘 -160
2. `line_movement --open_odds=-140 --close_odds=-160`
3. 返回概率变动、方向和分类（sharp_action、steam_move 等）

## 示例

示例 1：使用ESPN和Polymarket价格进行优势检查
用户说："湖人队的比赛有优势吗？ESPN 给出 -150，Polymarket 给出 52 分"
操作：
1. 调用 `devig(odds="-150,+130", format="american")` → 公平主队概率 ~58%
2. 调用 `find_edge(fair_prob=0.58, market_prob=0.52)` → 优势 ~6%，正预期收益
3. 调用 `kelly_criterion(fair_prob=0.58, market_prob=0.52)` → 最佳投注分数
结果：显示优势百分比、每美元预期收益和推荐投注金额（占资金库的百分比）

示例 2：备兑机会检测
用户说："我能备兑吗？Polymarket 主队为 48 分，Kalshi 客队为 49 分"
操作：
1. 调用 `find_arbitrage(market_probs="0.48,0.49", labels="home,away")`
2. 检查结果中的 `arbitrage_found`
结果：如果存在备兑：显示分配百分比和保证 ROI。如果不存在：显示总隐含概率并解释没有保证收益

示例 3：备兑评估
用户说："这个 3 投注备兑 +600 值得吗？"
操作：
1. 去 vigging 每个投注以获取公平概率（例如，0.58、0.62、0.55）
2. 调用 `parlay_analysis(legs="0.58,0.62,0.55", parlay_odds=600)`
结果：显示组合公平概率、优势、预期收益、+EV 或 -EV 判定和凯利分数

示例 4：线变动解释
用户说："线从 -140 移动到 -160，这意味着什么？"
操作：
1. 调用 `line_movement(open_odds=-140, close_odds=-160)`
结果：显示概率变动、方向、幅度和分类（sharp action、steam move 等）

示例 5：去 vigging 标准让分
用户说："这个让分的真实赔率是多少？双方都是 -110"
操作：
1. 调用 `devig(odds="-110,-110", format="american")`
结果：显示每方为 50% 公平概率，vig 约为 4.5%

示例 6：赔率格式转换
用户说："将 -200 转换为隐含概率"
操作：
1. 调用 `convert_odds(odds=-200, from_format="american")`
结果：显示 66.7% 隐含概率和 1.50 小数赔率

## 不存在的命令 — 永远不要调用这些

- ~~`get_odds`~~ — 不存在。该模块分析赔率；它不获取赔率。使用 nba-data/nfl-data 等 ESPN 赔率，或 polymarket/kalshi 预测市场价格。
- ~~`calculate_ev`~~ — 不存在。使用 `find_edge` 或 `evaluate_bet` 代替。
- ~~`compare_markets`~~ — 不存在。使用 `markets` 技能进行跨平台比较。

如果命令未列在 `references/api-reference.md` 中，则不存在。

## 故障排除

错误：调用 `convert_odds` 时出现 `ValueError: unknown format`
原因：`from_format` 参数不是 `american`、`decimal` 或 `probability` 之一
解决方案：使用确切的 `american`、`decimal` 或 `probability` 作为格式字符串

错误：`find_edge` 返回负预期收益，而预期是正优势
原因：公平概率和市场概率可能颠倒，或者跳过了去 vigging
解决方案：首先对博彩公司赔率运行 `devig`，然后将去 vigging 的 `fair_prob` 传递给 `find_edge`

错误：`find_arbitrage` 即使价格看似较低时也显示没有备兑
原因：所有结果正确包含时，价格总和可能超过 1.0
解决方案：验证您是否使用了所有结果的正确概率；检查结果中的 `total_implied`

错误：凯利分数非常高（大于 0.5）
原因：优势估计非常大——通常是由于公平概率计算错误
解决方案：使用半凯利或四分之一凯利进行保守的规模。重新验证公平概率 via `devig`
