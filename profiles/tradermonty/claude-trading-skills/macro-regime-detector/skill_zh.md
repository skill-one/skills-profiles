# 宏观周期检测器

使用月度频率的跨资产比率分析来检测结构化宏观周期转换。该技能识别1-2年的周期变化，为战略投资组合定位提供信息。

## 使用场景

- 用户询问当前宏观周期或周期转换
- 用户希望了解结构性市场轮动（集中与扩散）
- 用户基于收益率曲线、信用或跨资产信号询问长期定位
- 用户引用RSP/SPY比率、IWM/SPY、HYG/LQD或其他跨资产比率
- 用户希望评估是否正在进行周期变化

## 工作流程

1. 加载用于方法论背景的参考文档：
   - `references/regime_detection_methodology.md`
   - `references/indicator_interpretation_guide.md`

2. 执行主分析脚本：
   ```bash
   python3 -m pip install -r skills/macro-regime-detector/requirements.txt
   uv run python3 skills/macro-regime-detector/scripts/macro_regime_detector.py --output-dir reports/
   ```
   这会获取9个ETF 600天的数据。使用FMP密钥时，客户端首先尝试FMP获取国债利率（总计约10次API调用），然后回退到yfinance获取不可用的ETF历史。不使用FMP密钥时，它以yfinance模式运行，并使用SHY/TLT作为收益率曲线的回退方案。

   检测器在它的六个组件都没有可用数据时失败并写入无报告。不要将缺失报告或非零退出视为有效的低转换周期。

3. 读取生成的Markdown报告并向用户展示发现。

4. 当用户询问历史类比时，使用`references/historical_regimes.md`提供额外背景。

## 前置条件

- **Python依赖项**（必需）：安装`requirements.txt`，包括yfinance和requests
- **FMP API密钥**（可选）：设置`FMP_API_KEY`或传递`--api-key`以在回退到yfinance/SHY-TLT之前使用FMP和国债数据
- FMP免费套餐可能无法服务所有ETF；不可用的符号将自动使用yfinance

## 6个组件

| # | 组件 | 比率/数据 | 权重 | 检测内容 |
|---|-------|------------|------|----------|
| 1 | 市场集中度 | RSP/SPY | 25% | 大盘股集中与市场扩散 |
| 2 | 收益率曲线 | 10Y-2Y利差 | 20% | 利率周期转换 |
| 3 | 信用环境 | HYG/LQD | 15% | 信用周期风险偏好 |
| 4 | 规模因子 | IWM/SPY | 15% | 小盘股与大盘股轮动 |
| 5 | 股债 | SPY/TLT + 相关性 | 15% | 股票-债券关系周期 |
| 6 | 行业轮动 | XLY/XLP | 10% | 周期性与防御性偏好 |

## 5个周期分类

- **集中**：大盘股领导，狭窄市场
- **扩散**：扩大参与，小盘股/价值轮动
- **收缩**：信用收紧，防御性轮动，风险规避
- **通胀**：正的股债相关性，传统对冲失效
- **过渡**：多重信号但模式不明确

## 输出

- `macro_regime_YYYY-MM-DD_HHMMSS.json` — 用于程序化使用的结构化数据
- `macro_regime_YYYY-MM-DD_HHMMSS.md` — 人类可读报告，包含：
  1. 当前周期评估
  2. 转换信号仪表盘
  3. 组件详情
  4. 周期分类证据
  5. 投资组合立场建议

## 与其他技能的关系

| 方面 | 宏观周期检测器 | 市场顶部检测器 | 市场广度分析器 |
|------|----------------|----------------|----------------|
| 时间范围 | 1-2年（结构性） | 2-8周（战术性） | 当前快照 |
| 数据粒度 | 月度（6M/12M SMA） | 每日（25个交易日） | 每日CSV |
| 检测目标 | 周期转换 | 10-20%修正 | 广度健康评分 |
| API调用 | ~10 | ~33 | 0（免费CSV） |

## 脚本参数

```bash
python3 macro_regime_detector.py [options]

选项：
  --api-key KEY       FMP API密钥（默认：$FMP_API_KEY）
  --output-dir DIR    输出目录（默认：当前目录）
  --days N            获取历史的天数（默认：600）
```

## 资源

- `references/regime_detection_methodology.md` — 检测方法论和信号解释
- `references/indicator_interpretation_guide.md` — 跨资产比率解释指南
- `references/historical_regimes.md` — 用于背景的历史周期示例
