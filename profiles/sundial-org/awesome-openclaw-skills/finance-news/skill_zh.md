# 金融新闻技能

基于AI的市场新闻简报，支持可配置的语言输出和自动发送。

## 首次设置

运行交互式设置向导来配置您的来源、发送渠道和计划：

```bash
finance-news setup
```

向导将引导您完成以下步骤：
- 📰 **RSS源**：启用/禁用华尔街日报、巴伦周刊、彭博社、雅虎等。
- 📊 **市场**：选择区域（美国、欧洲、日本、亚洲）
- 📤 **发送**：配置WhatsApp/Telegram群组
- 🌐 **语言**：设置默认语言（英语/德语）
- ⏰ **计划**：配置上午/晚上的cron时间

您还可以配置特定部分：
```bash
finance-news setup --section feeds     # 仅RSS源
finance-news setup --section delivery  # 仅发送渠道
finance-news setup --section schedule  # 仅cron计划
finance-news setup --reset             # 重置为默认值
finance-news config                    # 显示当前配置
```

## 快速入门

```bash
# 生成上午简报
finance-news briefing --morning

# 查看市场概览
finance-news market

# 获取您的投资组合新闻
finance-news portfolio

# 获取特定股票新闻
finance-news news AAPL
```

## 功能

### 📊 市场覆盖范围
- **美国市场**：标普500、道琼斯、纳斯达克
- **欧洲**：DAX、STOXX 50、富时100
- **日本**：日经225

### 📰 新闻来源
- **高级**：华尔街日报、巴伦周刊（RSS源）
- **免费**：彭博社、雅虎财经、Finnhub
- **投资组合**：来自雅虎的特定股票新闻

### 🤖 AI摘要
- 基于Gemini的分析
- 可配置的语言（英语/德语）
- 简报风格：摘要、分析、头条

### 📅 自动简报
- **上午**：太平洋时间6:30（美国市场开盘）
- **晚上**：太平洋时间13:00（美国市场收盘）
- **发送**：WhatsApp（在cron脚本中配置群组）

## 命令

### 简报生成

```bash
# 上午简报（默认为英语）
finance-news briefing --morning

# 带WhatsApp发送的晚上简报
finance-news briefing --evening --send --group "市场简报"

# 德语选项
finance-news briefing --morning --lang de

# 分析风格（更详细）
finance-news briefing --style analysis
```

### 市场数据

```bash
# 市场概览（指数+头条新闻）
finance-news market

# JSON输出用于处理
finance-news market --json
```

### 投资组合管理

```bash
# 列出投资组合
finance-news portfolio-list

# 添加股票
finance-news portfolio-add NVDA --name "英伟达公司" --category 科技

# 移除股票
finance-news portfolio-remove TSLA

# 从CSV导入
finance-news portfolio-import ~/my_stocks.csv

# 交互式投资组合创建
finance-news portfolio-create
```

### 股票新闻

```bash
# 特定股票新闻
finance-news news AAPL
finance-news news TSLA
```

## 配置

### 投资组合CSV格式

位置：`~/clawd/skills/finance-news/config/portfolio.csv`

```csv
symbol,name,category,notes
AAPL,Apple Inc.,科技,核心持仓
NVDA,NVIDIA Corporation,科技,AI投资
MSFT,Microsoft Corporation,科技,
```

### 来源配置

位置：`~/clawd/skills/finance-news/config/config.json`（遗留回退：`config/sources.json`）

- 华尔街日报、巴伦周刊、彭博社、雅虎的RSS源
- 按区域划分的市场指数
- 语言设置

## Cron任务

### 通过OpenClaw设置

```bash
# 添加上午简报cron任务
openclaw cron add --schedule "30 6 * * 1-5" \
  --timezone "America/Los_Angeles" \
  --command "bash ~/clawd/skills/finance-news/cron/morning.sh"

# 添加晚上简报cron任务
openclaw cron add --schedule "0 13 * * 1-5" \
  --timezone "America/Los_Angeles" \
  --command "bash ~/clawd/skills/finance-news/cron/evening.sh"
```

### 手动Cron（crontab）

```cron
# 上午简报（太平洋时间6:30，工作日）
30 6 * * 1-5 bash ~/clawd/skills/finance-news/cron/morning.sh

# 晚上简报（太平洋时间13:00，工作日）
0 13 * * 1-5 bash ~/clawd/skills/finance-news/cron/evening.sh
```

## 示例输出

```markdown
🌅 **股市上午简报**
星期二，2026年1月21日 | 06:30

📊 **市场**
• 标普500：5,234 (+0,3%)
• DAX：16,890 (-0,1%)
• 日经：35,678 (+0,5%)

📈 **您的投资组合**
• AAPL $256 (+1,2%) — iPhone销量超出预期
• NVDA $512 (+3,4%) — AI芯片需求增长

🔥 **头条新闻**
• [华尔街日报] 美联储暗示3月可能降息
• [彭博社] 科技股引领涨势

🤖 **分析**
标普显示强势。您的投资组合受益于英伟达的动能。美联储评论可能引发波动。
```

## 集成

### 与OpenBB（现有技能）
```bash
# 获取详细报价，然后新闻
openbb-quote AAPL && finance-news news AAPL
```

### 与OpenClaw代理
代理在询问以下内容时将自动使用此技能：
- "市场情况如何？"
- "我的投资组合新闻"
- "生成上午简报"
- "英伟达怎么了？"

### 与Lobster（工作流引擎）

通过[Lobster](https://github.com/openclaw/lobster)运行简报以进行审批门和可重用性：

```bash
# 在WhatsApp发送前进行审批运行
lobster "workflows.run --file workflows/briefing.yaml"

# 带自定义参数
lobster "workflows.run --file workflows/briefing.yaml --args-json '{\"time\":\"evening\",\"lang\":\"en\"}'"
```

有关完整文档，请参阅`workflows/README.md`。

## 文件

```
skills/finance-news/
├── SKILL.md              # 此文档
├── Dockerfile            # NixOS兼容容器
├── config/
│   ├── portfolio.csv     # 您的监控列表
│   ├── config.json       # RSS/API/语言配置
│   ├── alerts.json       # 价格目标警报
│   └── manual_earnings.json  # 收益日历覆盖
├── scripts/
│   ├── finance-news      # 主CLI
│   ├── briefing.py       # 简报生成器
│   ├── fetch_news.py     # 新闻聚合器
│   ├── portfolio.py      # 投资组合CRUD
│   ├── summarize.py      # AI摘要
│   ├── alerts.py         # 价格警报管理
│   ├── earnings.py       # 收益日历
│   ├── ranking.py        # 标题排名
│   └── stocks.py         # 股票管理
├── workflows/
│   ├── briefing.yaml     # 带审批门Lobster工作流
│   └── README.md         # 工作流文档
├── cron/
│   ├── morning.sh        # 上午cron（基于Docker）
│   └── evening.sh        # 晚上cron（基于Docker）
└── cache/                # 15分钟新闻缓存
```

## 依赖项

- Python 3.10+
- `feedparser` (`pip install feedparser`)
- Gemini CLI (`brew install gemini-cli`)
- OpenBB（现有的`openbb-quote`包装器）
- OpenClaw消息工具（用于WhatsApp发送）

## 故障排除

### Gemini无法工作
```bash
# 认证Gemini
gemini  # 按照登录流程操作
```

### RSS源超时
- 检查网络连接
- 华尔街日报/巴伦周刊可能需要订阅cookie以获取某些内容
- 免费源（彭博社、雅虎）应始终正常工作

### WhatsApp发送失败
- 验证WhatsApp群组是否存在且机器人有访问权限
- 检查`openclaw doctor`的WhatsApp状态
