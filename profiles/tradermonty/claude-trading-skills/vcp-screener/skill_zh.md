# VCP筛选器 - Minervini波动收缩模式

筛选标普500指数成分股，寻找满足马克·明维尼（Mark Minervini）的波动收缩模式（VCP）的股票，识别在突破枢轴点附近波动收缩的2阶段上升趋势股票。

## 使用场景

- 用户请求VCP筛选或明维尼风格设置
- 用户希望找到紧密底部/波动收缩模式
- 用户请求2阶段动量股票扫描
- 用户询问具有明确风险的突破候选股
- 用户询问"查找<TICKER>的所有历史VCP"或希望研究某个股票的过去VCP设置及未来结果（`--history --ticker SYM`）

## 前置条件

- FMP API密钥（设置`FMP_API_KEY`环境变量或传递`--api-key`）
- 免费套餐（每天250次调用）足以进行默认筛选（前100个候选股）
- 建议使用付费套餐进行完整的标普500筛选（`--full-sp500`）

## 工作流程

### 第1步：准备和执行筛选

运行VCP筛选器脚本：

```bash
# 默认：标普500，前100个候选股
python3 skills/vcp-screener/scripts/screen_vcp.py --output-dir skills/vcp-screener/scripts

# 自定义股票池
python3 skills/vcp-screener/scripts/screen_vcp.py --universe AAPL NVDA MSFT AMZN META --output-dir skills/vcp-screener/scripts

# 完整的标普500（付费API套餐）
python3 skills/vcp-screener/scripts/screen_vcp.py --full-sp500 --output-dir skills/vcp-screener/scripts
```

### 严格模式（明维尼纯设置）

仅返回`valid_vcp=True` AND `execution_state`在`(突破前, 突破)`中的股票：

```bash
python3 skills/vcp-screener/scripts/screen_vcp.py --strict --output-dir reports/
```

### 历史单股票模式

遍历一个股票的多年历史，检测所有曾经形成的VCP，并为每次检测附加未来结果统计（突破/止损/超时，结果天数，最大收益，最大亏损）。适用于模式研究和回测背景——不是实时筛选器。

```bash
# 默认：扫描约5年（1260个交易日），5天步长，60天结果窗口
python3 skills/vcp-screener/scripts/screen_vcp.py \
  --history --ticker FIX --output-dir reports/

# 自定义扫描长度：750个交易日（约3年），90天结果窗口
python3 skills/vcp-screener/scripts/screen_vcp.py \
  --history 750 --ticker TSLA \
  --stride-days 5 --outcome-days 90 \
  --output-dir reports/

# 长扫描：10年（2520个交易日）
python3 skills/vcp-screener/scripts/screen_vcp.py \
  --history 2520 --ticker NVDA --output-dir reports/
```

输出（带时间戳）：
- `vcp_history_<SYM>_<YYYY-MM-DD_HHMMSS>.json` — 检测时间线，包含完整分析器负载+每次检测的`forward_outcome`+汇总统计。
- `vcp_history_<SYM>_<YYYY-MM-DD_HHMMSS>.md` — 人类可读时间线。

模式特定标志：

| 参数 | 默认 | 范围 | 效果 |
|-------|------|------|------|
| `--history [DAYS]` | (关闭)/1260（无参数时） | 100-5040 | 启用历史模式；可选地指定交易日扫描窗口（需要`--ticker`） |
| `--ticker SYM` | — | — | 要扫描的股票代码 |
| `--stride-days` | 5 | 1-60 | 两个as-of游标位置之间的交易日步长 |
| `--outcome-days` | 60 | 5-252 | 每次检测评估的前向窗口 |

注意：
- 每次扫描两个FMP API调用（股票代码+SPY历史），不是像跨截面管道那样100多次。
- `marketCap`和绝对RS百分位数反映的是股票本身，而不是实时筛选池——使用此报告进行模式研究，而不是投资组合规模。
- 检测通过`(T1_high_date, last_low_date, pivot)`去重，因此随着游标的老化，相同的VCP不会被重复报告。

### 高级调优（用于回测）

调整VCP检测参数进行研究和回测：

```bash
python3 skills/vcp-screener/scripts/screen_vcp.py \
  --min-contractions 3 \
  --t1-depth-min 12.0 \
  --breakout-volume-ratio 2.0 \
  --trend-min-score 90 \
  --atr-multiplier 1.5 \
  --output-dir reports/
```

| 参数 | 默认 | 范围 | 效果 |
|-------|------|------|------|
| `--min-contractions` | 2 | 2-4 | 更高=更少但更高质量的模式 |
| `--t1-depth-min` | 10.0% | 1-50 | 更高=排除浅层第一次修正 |
| `--breakout-volume-ratio` | 1.5x | 0.5-10 | 更高=更严格的成交量确认 |
| `--trend-min-score` | 85 | 0-100 | 更高=更严格的2阶段过滤器 |
| `--atr-multiplier` | 1.5 | 0.5-5 | 更低=更敏感的摆动检测 |
| `--contraction-ratio` | 0.70 | 0.1-1 | 更低=需要更紧密的收缩 |
| `--min-contraction-days` | 5 | 1-30 | 更高=更长的最小收缩 |
| `--lookback-days` | 120 | 30-365 | 更长=找到更早的模式 |
| `--max-sma200-extension` | 50.0% | — | SMA200距离阈值，用于Overextended状态和惩罚 |
| `--wide-and-loose-threshold` | 15.0% | — | 最终收缩深度超过此阈值时，触发wide-and-loose标志 |
| `--strict` | 关闭 | — | 明维尼严格模式：仅Pre-breakout或Breakout且具有有效VCP |

### 第2步：查看结果

1. 阅读生成的JSON和Markdown报告
2. 加载`references/vcp_methodology.md`获取模式解释背景
3. 加载`references/scoring_system.md`获取评分阈值指导

### 第3步：展示分析

对每个顶级候选股，展示：
- **质量**（`composite_score`/评级）— VCP模式形成得有多好？
- **执行状态**（`execution_state`）— 现在可以买入吗？（突破前/突破=可操作）
- **模式类型**（`pattern_type`）— 经典VCP/邻近VCP/突破后/扩展领导者/受损
- 如果应用了State Cap，则标记`★`（原始评分被下调）
- 收缩细节（T1/T2/T3深度和比率）
- 交易设置：枢轴价格，止损，风险百分比
- 成交量枯竭比率和突破成交量评分
- 相对强度排名

### 第4步：提供可操作的指导

**按执行状态（主要过滤器）：**
- **突破前/突破**：模式处于活跃入场窗口——应用基于评级的规模
- **突破后早期**：突破正在进行但高于理想入场点——减少规模或等待回调
- **扩展/过度扩展**：交易错过——添加到观察列表，等待下一个底部
- **受损/无效**：设置失效——不要入场

**按评级（在确认可操作后，次要过滤器）：**
- **经典VCP（90+）**：在枢轴处买入，激进规模（1.5-2x）
- **强VCP（80-89）**：在枢轴处买入，标准规模（1x）
- **良好VCP（70-79）**：在枢轴上方成交量确认时买入（0.75x）
- **发展中（60-69）**：添加到观察列表，等待更紧密的收缩
- **弱/无VCP（<60）**：仅监控或跳过

## 三阶段管道

1. **预筛选** - 基于报价的筛选（价格、成交量、52周位置）~101次API调用
2. **趋势模板** - 7点2阶段过滤器，使用260天历史 ~100次API调用
3. **VCP检测** - 模式分析、评分、报告生成（无额外API调用）

## 输出

- `vcp_screener_YYYY-MM-DD_HHMMSS.json` - 结构化结果
- `vcp_screener_YYYY-MM-DD_HHMMSS.md` - 人类可读报告

## 资源

- `references/vcp_methodology.md` - VCP理论和趋势模板解释
- `references/scoring_system.md` - 评分阈值和组件权重
- `references/fmp_api_endpoints.md` - API端点和速率限制
