# Trump Code — 市场信号分析

> 技能由 [ara.so](https://ara.so) 提供 — 每日 2026 技能合集。

Trump Code 是一个开源系统，通过暴力计算来寻找特朗普的 Truth Social/X 发布行为与标普 500 指数之间的统计显著模式。它测试了 3150 万种模型组合，维护着 551 条存活规则，并在 566 次预测中验证了 61.3% 的命中率（z=5.39, p<0.05）。

## 安装

```bash
git clone https://github.com/sstklen/trump-code.git
cd trump-code
pip install -r requirements.txt
```

### 环境变量

```bash
# 用于 AI 汇报和聊天机器人
export GEMINI_KEYS="key1,key2,key3"       # 以逗号分隔的 Gemini API 密钥

# 可选：用于 Claude Opus 深度分析
export ANTHROPIC_API_KEY="your-key-here"

# 可选：用于 Polymarket/Kalshi 集成
export POLYMARKET_API_KEY="your-key-here"
```

## CLI — 关键命令

```bash
# 从特朗普的帖子中检测到的今日信号
python3 trump_code_cli.py signals

# 模型性能排行榜（所有 11 个命名模型）
python3 trump_code_cli.py models

# 获取 LONG/SHORT 一致性预测
python3 trump_code_cli.py predict

# 预测市场套利机会
python3 trump_code_cli.py arbitrage

# 系统健康检查（断路器状态）
python3 trump_code_cli.py health

# 完整每日报告（三语种）
python3 trump_code_cli.py report

# 将所有数据导出为 JSON
python3 trump_code_cli.py json
```

## 核心脚本

```bash
# 实时特朗普帖子监控器（每 5 分钟轮询一次）
python3 realtime_loop.py

# 暴力模型搜索（约 25 分钟，测试数百万种组合）
python3 overnight_search.py

# 单独分析
python3 analysis_06_market.py        # 帖子与标普 500 相关性
python3 analysis_09_combo_score.py   # 多信号组合评分

# Web 仪表板 + AI 聊天机器人（端口 8888）
export GEMINI_KEYS="key1,key2,key3"
python3 chatbot_server.py
# → http://localhost:8888
```

## REST API（实时运行于 trumpcode.washinmura.jp）

```python
import requests

BASE = "https://trumpcode.washinmura.jp"

# 一次性获取所有仪表板数据
data = requests.get(f"{BASE}/api/dashboard").json()

# 今日信号 + 7 天历史
signals = requests.get(f"{BASE}/api/signals").json()

# 模型性能排名
models = requests.get(f"{BASE}/api/models").json()

# 最新 20 条特朗普帖子（带信号标签）
posts = requests.get(f"{BASE}/api/recent-posts").json()

# 实时 Polymarket 特朗普预测市场（316+）
markets = requests.get(f"{BASE}/api/polymarket-trump").json()

# LONG/SHORT 策略
playbook = requests.get(f"{BASE}/api/playbook").json()

# 系统健康/断路器状态
status = requests.get(f"{BASE}/api/status").json()
```

### AI 聊天机器人 API

```python
import requests

response = requests.post(
    "https://trumpcode.washinmura.jp/api/chat",
    json={"message": "今天触发了哪些信号？共识是什么？"}
)
print(response.json()["reply"])
```

## MCP 服务器（Claude 代码 / Cursor 集成）

添加到 `~/.claude/settings.json`：

```json
{
  "mcpServers": {
    "trump-code": {
      "command": "python3",
      "args": ["/path/to/trump-code/mcp_server.py"]
    }
  }
}
```

可用的 MCP 工具：`signals`, `models`, `predict`, `arbitrage`, `health`, `events`, `dual_platform`, `crowd`, `full_report`

## 开放数据文件

所有数据都存储在 `data/` 目录中，并每日更新：

```python
import json, pathlib

DATA = pathlib.Path("data")

# 4.4 万+ Truth Social 帖子
posts = json.loads((DATA / "trump_posts_all.json").read_text())

# 带有信号预标签的帖子
posts_lite = json.loads((DATA / "trump_posts_lite.json").read_text())

# 566 条已验证预测及结果
predictions = json.loads((DATA / "predictions_log.json").read_text())

# 551 条活跃规则（暴力计算 + 进化）
rules = json.loads((DATA / "surviving_rules.json").read_text())

# 384 个特征 × 414 个交易日
features = json.loads((DATA / "daily_features.json").read_text())

# 标普 500 OHLC 历史数据
market = json.loads((DATA / "market_SP500.json").read_text())

# 断路器/系统健康
cb = json.loads((DATA / "circuit_breaker_state.json").read_text())

# 规则进化日志（交叉/变异）
evo = json.loads((DATA / "evolution_log.json").read_text())
```

## 通过 API 下载数据

```python
import requests

BASE = "https://trumpcode.washinmura.jp"

# 列出可用数据集
catalog = requests.get(f"{BASE}/api/data").json()

# 下载特定文件
raw = requests.get(f"{BASE}/api/data/surviving_rules.json").content
rules = json.loads(raw)
```

## 实际代码示例

### 解析今日信号

```python
import requests

signals_data = requests.get("https://trumpcode.washinmura.jp/api/signals").json()

today = signals_data.get("today", {})
print("今日触发的信号:", today.get("signals", []))
print("共识:", today.get("consensus"))        # "LONG" / "SHORT" / "NEUTRAL"
print("置信度:", today.get("confidence"))      # 0.0–1.0
print("活跃模型:", today.get("active_models", []))
```

### 从存活规则中查找表现最佳的规则

```python
import json

rules = json.loads(open("data/surviving_rules.json").read())

# 按命中率降序排序
top_rules = sorted(rules, key=lambda r: r.get("hit_rate", 0), reverse=True)

for rule in top_rules[:10]:
    print(f"规则: {rule['id']} | 命中率: {rule['hit_rate']:.1%} | "
          f"交易次数: {rule['n_trades']} | 平均回报: {rule['avg_return']:.3%}")
```

### 检查预测市场机会

```python
import requests

arb = requests.get("https://trumpcode.washinmura.jp/api/insights").json()
markets = requests.get("https://trumpcode.washinmura.jp/api/polymarket-trump").json()

# 按成交量排序的市场
active = [m for m in markets.get("markets", []) if m.get("active")]
by_volume = sorted(active, key=lambda m: m.get("volume", 0), reverse=True)

for m in by_volume[:5]:
    print(f"{m['title']}: YES={m['yes_price']:.0%} | 成交量=${m['volume']:,.0f}")
```

### 将帖子特征与回报相关联

```python
import json
import numpy as np

features = json.loads(open("data/daily_features.json").read())
market   = json.loads(open("data/market_SP500.json").read())

# 构建按日期索引的回报映射
returns = {d["date"]: d["close_pct"] for d in market}

# 示例：将帖子数量与次日回报相关联
xs, ys = [], []
for day in features:
    date = day["date"]
    if date in returns:
        xs.append(day.get("post_count", 0))
        ys.append(returns[date])

correlation = np.corrcoef(xs, ys)[0, 1]
print(f"帖子数量与同日回报: r={correlation:.3f}")
```

### 在自定义信号上运行回测

```python
import json

posts    = json.loads(open("data/trump_posts_lite.json").read())
market   = json.loads(open("data/market_SP500.json").read())

returns  = {d["date"]: d["close_pct"] for d in market}

# 查找在东部时间上午 9:30 之前带有 RELIEF 信号的日期
relief_days = [
    p["date"] for p in posts
    if "RELIEF" in p.get("signals", []) and p.get("hour", 24) < 9
]

hits = [returns[d] for d in relief_days if d in returns]
if hits:
    print(f"RELIEF 预盘: n={len(hits)}, "
          f"平均={sum(hits)/len(hits):.3%}, "
          f"命中率={sum(1 for h in hits if h > 0)/len(hits):.1%}")
```

## 关键信号类型

| 信号 | 描述 | 典型影响 |
|------|------|----------|
| `RELIEF` 预盘 | "缓解"语言在东部时间上午 9:30 之前 | 同日平均 +1.12% |
| `TARIFF` 市场时段 | 交易时段提及关税 | 次日平均 -0.758% |
| `DEAL` | 交易/协议语言 | 52.2% 命中率 |
| `CHINA`（仅限 Truth Social） | 提及中国（从未在 X 上提及） | 加权提升 1.5 倍 |
| `SILENCE` | 无帖子日 | 80% 看涨，平均 +0.409% |
| 爆发 → 沉默 | 快速发布后突然安静 | 65.3% 看涨信号 |

## 模型参考

| 模型 | 策略 | 命中率 | 平均回报 |
|------|------|--------|----------|
| A3 | 预盘 RELIEF → 激增 | 72.7% | +1.206% |
| D3 | 成交量激增 → 恐慌底部 | 70.2% | +0.306% |
| D2 | 签名切换 → 正式声明 | 70.0% | +0.472% |
| C1 | 爆发 → 长期沉默 → 看涨 | 65.3% | +0.145% |
| C3 ⚠️ | 深夜关税（反指标） | 37.5% | −0.414% |

> **注意:** C3 是一个反指标——如果它触发，断路器会自动将其反转为看涨（反转后准确率 62%）。

## 系统架构流程

```
检测到 Truth Social 帖子（每 5 分钟）
    → 分类信号（RELIEF / TARIFF / DEAL / CHINA / 等）
    → 双平台加权（TS 仅限中国 = 1.5 倍权重）
    → 快照 Polymarket + 标普 500
    → 运行 551 条存活规则 → 生成预测
    → 按 1h / 3h / 6h 追踪
    → 验证结果 → 更新规则权重
    → 断路器：如果系统退化 → 暂停/反转
    → 每日：进化规则（交叉/变异/蒸馏）
    → 同步数据到 GitHub
```

## 故障排除

**`realtime_loop.py` 未检测到新帖子**
- 检查对 Truth Social 抓取端点的网络访问
- 验证 `data/trump_posts_all.json` 时间戳是否为最新
- 运行 `python3 trump_code_cli.py health` 查看断路器状态

**`chatbot_server.py` 无法启动**
- 确保 `GEMINI_KEYS` 环境变量已设置：`export GEMINI_KEYS="key1,key2"`
- 端口 8888 可能已被占用：`lsof -i :8888`

**`overnight_search.py` 内存不足**
- 运行约 3150 万种组合——需要 4GB RAM
- 在 8GB+ 机器上运行或减少脚本配置中的搜索空间

**命中率低于 55%**
- 检查 `data/circuit_breaker_state.json`——系统可能已自动暂停
- 查看 `data/learning_report.json` 查找被降级的规则
- 重新运行 `overnight_search.py` 刷新存活规则

**`data/` 目录中数据陈旧**
- 每日管道自动同步到 GitHub（如果运行中）
- 手动触发：`python3 trump_code_cli.py report` 强制刷新
- 或从远程拉取最新版本：`git pull origin main`
