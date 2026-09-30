---
name: daily-stock-analysis
description: 基于LLM的A/H/US股票智能分析系统，整合多源数据、实时新闻、AI决策仪表盘，并通过GitHub Actions实现多渠道推送通知。
---

# 每日股票分析 (股票智能分析系统)

> 技能由 [ara.so](https://ara.so) 提供 — 每日 2026 技能合集。

基于大型语言模型的股票分析系统，支持 A 股、港股和美股市场。自动获取行情、新闻和基本面数据，生成 AI 决策看板，包含买入/卖出目标，并按计划通过 GitHub Actions 推送结果至微信/飞书/Telegram/Discord/邮箱 — 无需服务器成本。

## 功能概述

- **AI 决策看板**: 每只股票一行结论 + 精准买入/卖出/止损价格 + 检查清单
- **多市场支持**: A 股 (CN)、港股、美股 + 指数 (SPX, DJI, IXIC)
- **数据来源**: AkShare、Tushare、YFinance 用于行情；Tavily/SerpAPI/Brave 用于新闻
- **LLM 后端**: Gemini、OpenAI、Claude、DeepSeek、Qwen 通过 LiteLLM (统一接入)
- **推送渠道**: 微信工作台、飞书、Telegram、Discord、钉钉、邮箱、PushPlus
- **自动化**: GitHub Actions cron 定时任务，无需服务器
- **Web UI**: 投资组合管理、历史记录、回测、Agent 问答
- **Agent**: 多轮策略问答，内置 11 种策略 (均线金叉、艾略特波浪等)

## 安装方法

### 方法 1: GitHub Actions (推荐，零成本)

**步骤 1: Fork 仓库**
```
https://github.com/ZhuLinsen/daily_stock_analysis
```

**步骤 2: 配置 Secrets** (`Settings → Secrets and variables → Actions`)

**必需 — 至少一个 LLM 密钥:**
```
GEMINI_API_KEY        # Google AI Studio (免费套餐可用)
OPENAI_API_KEY        # OpenAI 或兼容 (DeepSeek, Qwen 等)
OPENAI_BASE_URL       # 例如: https://api.deepseek.com/v1
OPENAI_MODEL          # 例如: deepseek-chat, gpt-4o
AIHUBMIX_KEY          # AIHubMix (推荐，覆盖 Gemini+GPT+Claude+DeepSeek)
ANTHROPIC_API_KEY     # Claude
```

**必需 — 股票列表:**
```
STOCKS                # 例如: 600519,300750,AAPL,TSLA,00700.HK
```

**必需 — 至少一个通知渠道:**
```
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
FEISHU_WEBHOOK_URL
WECHAT_WEBHOOK_URL
EMAIL_SENDER / EMAIL_PASSWORD / EMAIL_RECEIVERS
DISCORD_WEBHOOK_URL
```

**步骤 3: 手动触发或等待 cron**

进入 `Actions → stock_analysis → Run workflow`

---

### 方法 2: 本地 / Docker

```bash
git clone https://github.com/ZhuLinsen/daily_stock_analysis
cd daily_stock_analysis
cp .env.example .env
# 使用你的密钥编辑 .env
pip install -r requirements.txt
python main.py
```

**Docker:**
```bash
docker build -t stock-analysis .
docker run --env-file .env stock-analysis
```

**Docker Compose:**
```bash
docker-compose up -d
```

## 配置

### `.env` 文件 (本地)

```env
# LLM - 选择一个或多个
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
OPENAI_BASE_URL=https://api.deepseek.com/v1
OPENAI_MODEL=deepseek-chat
AIHUBMIX_KEY=your_aihubmix_key

# 股票列表 (逗号分隔)
STOCKS=600519,300750,AAPL,TSLA,00700.HK

# 通知
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# 可选设置
REPORT_TYPE=full           # simple | full | brief
ANALYSIS_DELAY=10          # 股票间间隔秒数 (避免速率限制)
MAX_WORKERS=3              # 并发分析线程数
SINGLE_STOCK_NOTIFY=false  # 完成后立即推送每只股票
NEWS_MAX_AGE_DAYS=3        # 忽略 N 天前的新闻
```

### 多渠道 LLM (高级)

```env
LLM_CHANNELS=gemini,deepseek,claude
LLM_GEMINI_PROTOCOL=google
LLM_GEMINI_API_KEY=your_key
LLM_GEMINI_MODELS=gemini-2.0-flash,gemini-1.5-pro
LLM_GEMINI_ENABLED=true

LLM_DEEPSEEK_PROTOCOL=openai
LLM_DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
LLM_DEEPSEEK_API_KEY=your_key
LLM_DEEPSEEK_MODELS=deepseek-chat
LLM_DEEPSEEK_ENABLED=true
```

### 股票分组 (将不同股票发送至不同邮箱)

```env
STOCK_GROUP_1=600519,300750,000858
EMAIL_GROUP_1=investor1@example.com

STOCK_GROUP_2=AAPL,TSLA,NVDA
EMAIL_GROUP_2=investor2@example.com
```

### 市场复盘模式

```env
MARKET_REVIEW=cn      # cn | us | both
# cn = A 股三阶段复盘策略
# us = 美股制度策略 (多空/中性/空仓)
# both = 两个市场
```

## 关键命令 (CLI)

```bash
# 立即运行完整分析
python main.py

# 仅分析特定股票
STOCKS=600519,AAPL python main.py

# 运行 Web 看板
python web_app.py
# 访问 http://localhost:5000

# 使用 Docker (env 文件)
docker run --env-file .env stock-analysis python main.py

# 运行定时模式 (等待 cron，然后运行)
SCHEDULE_RUN_IMMEDIATELY=true python main.py
```

## GitHub Actions 工作流

工作流文件 `.github/workflows/stock_analysis.yml` 按计划运行:

```yaml
# 默认计划 - 在工作流文件中自定义
on:
  schedule:
    - cron: '30 1 * * 1-5'   # 9:30 AM CST (UTC+8) 工作日
  workflow_dispatch:          # 手动触发
```

**要修改计划:** 编辑 `.github/workflows/stock_analysis.yml` 中的 cron 表达式。

**通过 GitHub CLI 添加 secrets:**
```bash
gh secret set GEMINI_API_KEY --body "$GEMINI_API_KEY"
gh secret set STOCKS --body "600519,300750,AAPL,TSLA"
gh secret set TELEGRAM_BOT_TOKEN --body "$TG_TOKEN"
gh secret set TELEGRAM_CHAT_ID --body "$TG_CHAT_ID"
```

## 代码示例

### 程序化分析 (Python)

```python
# 程序化分析特定股票
import asyncio
from analyzer import StockAnalyzer

async def analyze():
    analyzer = StockAnalyzer()
    
    # 分析一只 A 股
    result = await analyzer.analyze_stock("600519")  # 茅台
    print(result['conclusion'])
    print(result['buy_price'])
    print(result['stop_loss'])
    print(result['target_price'])

asyncio.run(analyze())
```

### 自定义通知集成

```python
from notifier import NotificationManager

notifier = NotificationManager()

# 推送至 Telegram
await notifier.send_telegram(
    token=os.environ['TELEGRAM_BOT_TOKEN'],
    chat_id=os.environ['TELEGRAM_CHAT_ID'],
    message="📈 分析完成\n600519: 买入 1680，止损 1620，目标 1800"
)

# 推送至飞书 webhook
await notifier.send_feishu(
    webhook_url=os.environ['FEISHU_WEBHOOK_URL'],
    content=analysis_report
)
```

### 使用 Agent API

```python
import requests

# 向股票 Agent 提问策略问题
response = requests.post('http://localhost:5000/api/agent/chat', json={
    "message": "600519 现在适合买入吗？用均线金叉策略分析",
    "stock_code": "600519",
    "strategy": "ma_crossover"  # ma_crossover, elliott_wave, chan_theory 等
})

print(response.json()['reply'])
```

### 回测分析准确率

```python
import requests

# 触发股票回测
response = requests.post('http://localhost:5000/api/backtest', json={
    "stock_code": "600519",
    "days": 30  # 评估 AI 预测的最近 30 天
})

result = response.json()
print(f"方向准确率: {result['direction_accuracy']}%")
print(f"止盈命中率: {result['tp_hit_rate']}%")
print(f"止损命中率: {result['sl_hit_rate']}%")
```

### 从图像导入股票 (视觉 LLM)

```python
import requests

# 上传股票列表截图供 AI 提取
with open('watchlist_screenshot.png', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/api/stocks/import/image',
        files={'image': f}
    )

stocks = response.json()['extracted_stocks']
# 返回: [{"code": "600519", "name": "贵州茅台", "confidence": 0.98}, ...]
```

## Web 看板功能

启动 Web 应用:
```bash
python web_app.py
```

| 路径 | 功能 |
|------|------|
| `/` | 今日分析看板 |
| `/portfolio` | 持仓管理，盈亏跟踪 |
| `/history` | 历史分析报告 (支持批量删除) |
| `/backtest` | AI 预测准确率回测 |
| `/agent` | 多轮策略问答 |
| `/settings` | LLM 渠道，通知配置 |
| `/import` | 从图像/CSV/剪贴板导入股票 |

## 支持的股票格式

```
# A 股 (6 位代码)
600519    # 贵州茅台
300750    # 宁德时代
000858    # 五粮液

# 港股 (5 位 + .HK)
00700.HK  # 腾讯控股
09988.HK  # 阿里巴巴

# 美股 (代码)
AAPL
TSLA
NVDA

# 美股指数
SPX       # 标普 500
DJI       # 道琼斯
IXIC      # 纳斯达克
```

## 内置交易规则

| 规则 | 配置 |
|------|------|
| 不追高 | `DEVIATION_THRESHOLD=5` (%, 强趋势自动放宽) |
| 趋势交易 | MA5 > MA10 > MA20 上涨排列要求 |
| 精准目标 | 每只股票的买入价、止损、止盈 |
| 新闻时效性 | `NEWS_MAX_AGE_DAYS=3` (忽略过时新闻) |
| 检查清单 | 每个条件标记: ✅ 满足 / ⚠️ 谨慎 / ❌ 未满足 |

## 故障排除

**分析运行但未收到推送:**
```bash
# 检查通知配置
python -c "from notifier import test_all_channels; test_all_channels()"

# 验证 secrets 是否设置 (GitHub Actions)
gh secret list
```

**LLM API 错误 / 速率限制:**
```env
ANALYSIS_DELAY=15        # 增加股票间延迟
MAX_WORKERS=1            # 降低并发
LITELLM_FALLBACK_MODELS=gemini-1.5-flash,deepseek-chat  # 添加备用模型
```

**AkShare 数据获取失败 (A 股):**
```bash
pip install akshare --upgrade
# A 股数据需要中文网络或代理
```

**YFinance 美股数据问题:**
```bash
pip install yfinance --upgrade
# 美股使用 YFinance 保持一致性
```

**GitHub Actions 未触发:**
- 检查 Actions 是否启用: `Settings → Actions → General → Allow all actions`
- 验证 cron 语法 [crontab.guru](https://crontab.guru)
- 检查工作流文件是否存在: `.github/workflows/stock_analysis.yml`

**Web 认证问题 (管理员密码):**
```env
# 如果认证已禁用再启用，需要当前密码
# 通过环境变量重置
WEB_ADMIN_PASSWORD=new_password
```

**多工作线程部署认证状态:**
```bash
# 认证切换仅适用于当前进程
# 必须重启所有工作线程同步状态
docker-compose restart
```

## 报告类型

```env
REPORT_TYPE=simple   # 简洁: 结论 + 关键价格
REPORT_TYPE=full     # 完整: 所有技术 + 基本面 + 新闻分析
REPORT_TYPE=brief    # 3-5 句摘要
```

**完整报告包含:**
- 一句话核心结论
- 技术面分析 (技术: 均线排列，振幅分布)
- 基本面 (估值、增长、盈利、机构持仓)
- 舆情情报 (新闻情绪、社交媒体 — 美股)
- 精确买卖点位
- 操作检查清单
- 板块涨跌榜

## LLM 优先级顺序

```
Gemini → Anthropic → OpenAI/AIHubMix/兼容
```

推荐使用 AIHubMix 单键访问所有主要模型 (无需 VPN):
```env
AIHUBMIX_KEY=$AIHUBMIX_KEY  # 覆盖 Gemini, GPT, Claude, DeepSeek
# 无需 OPENAI_BASE_URL — 自动配置
```
