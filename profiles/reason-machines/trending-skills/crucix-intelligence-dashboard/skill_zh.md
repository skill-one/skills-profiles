# Crucix 智能仪表盘

> 技能由 [ara.so](https://ara.so) 提供 — 每日 2026 技能收集。

Crucix 是一个自托管的智能终端，每 15 分钟从 27 个开源数据源（卫星火灾探测、航班追踪、辐射监测、冲突数据、市场价格、海上 AIS、经济指标等）获取数据，在 WebGL 球体仪表盘上渲染所有信息，并可选地将警报推送到 Telegram/Discord，附带 LLM 增强的分析。

---

## 安装

```bash
git clone https://github.com/calesthio/Crucix.git
cd crucix
npm install          # 安装 Express (唯一的硬依赖)
cp .env.example .env # 然后编辑 .env 文件以添加您的 API 密钥
npm run dev          # 仪表盘位于 http://localhost:3117
```

**Docker:**
```bash
cp .env.example .env
docker compose up -d
# 扫描数据持久化在 ./runs/ 目录，通过卷挂载实现
```

**要求:** Node.js 22+ (使用原生 `fetch`、顶层 `await`、ESM 模块)

**如果 `npm run dev` 安静退出:**
```bash
node --trace-warnings server.mjs   # 跳过 npm 脚本运行器 (在 Windows PowerShell 上很有用)
node diag.mjs                       # 诊断 Node 版本、模块导入、端口可用性
```

---

## 环境配置 (`.env`)

```dotenv
# ── 核心免费 API (强烈推荐) ──────────────────────────────────────
FRED_API_KEY=           # 联邦储备经济数据 — fred.stlouisfed.org
FIRMS_MAP_KEY=          # NASA 卫星火灾探测 — firms.modaps.eosdis.nasa.gov
EIA_API_KEY=            # 美国能源信息管理局 — eia.gov/opendata/register.php

# ── 可选数据源 ─────────────────────────────────────────────────────
ACLED_EMAIL=            # 武装冲突数据 — acleddata.com/register
ACLED_PASSWORD=
AISSTREAM_API_KEY=      # 海上船舶追踪 — aisstream.io (免费)
ADSB_API_KEY=           # 未过滤的航班追踪 — RapidAPI (~$10/月)

# ── LLM 提供商 (选择一个) ───────────────────────────────────────────
LLM_PROVIDER=           # anthropic | openai | gemini | codex
LLM_API_KEY=            # codex 不需要 API 密钥 (使用 ~/.codex/auth.json)

# ── Telegram 机器人 ─────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN=     # 来自 @BotFather
TELEGRAM_CHAT_ID=       # 来自 @userinfobot
TELEGRAM_CHANNELS=      # 可选: 超过 17 个内置频道的额外频道 ID
TELEGRAM_POLL_INTERVAL= # ms 之间命令轮询的间隔，默认 5000

# ── Discord 机器人 ─────────────────────────────────────────────────
DISCORD_BOT_TOKEN=      # Discord 开发者门户 → 机器人 → 令牌
DISCORD_CHANNEL_ID=     # 右键单击频道 → 复制频道 ID
DISCORD_GUILD_ID=       # 可选: 立即斜杠命令注册
DISCORD_WEBHOOK_URL=    # 可选: 仅警报模式，无需 discord.js

# ── 交易 (可选) ────────────────────────────────────────────────────────
ALPACA_API_KEY=
ALPACA_SECRET_KEY=
```

---

## 关键命令

| 命令 | 描述 |
|---|---|
| `npm run dev` | 启动仪表盘并自动刷新 |
| `node server.mjs` | 直接启动 (跳过 npm 脚本运行器) |
| `node diag.mjs` | 诊断设置问题 |
| `docker compose up -d` | 在后台运行 Docker |
| `npx @openai/codex login` | 通过 ChatGPT 订阅验证 Codex LLM |

---

## Telegram 机器人命令

一旦设置 `TELEGRAM_BOT_TOKEN` 和 `TELEGRAM_CHAT_ID`，机器人将响应：

| 命令 | 它的作用 |
|---|---|
| `/status` | 系统健康状况、上次扫描时间、源/LLM 状态 |
| `/sweep` | 立即触发手动智能扫描 |
| `/brief` | 紧凑文本摘要：方向、关键指标、顶级 OSINT |
| `/portfolio` | 投资组合状态 (需要 Alpaca 密钥) |
| `/alerts` | 最近警报历史记录，带有级别标签 |
| `/mute` / `/mute 2h` | 静音警报 1 小时或自定义持续时间 |
| `/unmute` | 恢复警报 |
| `/help` | 列出所有命令 |

---

## Discord 机器人命令

安装 `discord.js` 以启用完整机器人模式；否则 Crucix 会自动回退到仅 webhook 模式：

```bash
npm install discord.js   # 可选: 启用斜杠命令 + 丰富嵌入
```

可用的斜杠命令：`/status`、`/sweep`、`/brief`、`/portfolio`

警报嵌入按颜色编码：🔴 红色 = 闪现，🟡 黄色 = 优先级，🔵 蓝色 = 例行。

**仅 webhook 模式** (无 `discord.js`，无斜杠命令):
```dotenv
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN
```

---

## LLM 提供商设置

### Anthropic Claude
```dotenv
LLM_PROVIDER=anthropic
LLM_API_KEY=$ANTHROPIC_API_KEY
```

### OpenAI
```dotenv
LLM_PROVIDER=openai
LLM_API_KEY=$OPENAI_API_KEY
```

### Google Gemini
```dotenv
LLM_PROVIDER=gemini
LLM_API_KEY=$GEMINI_API_KEY
```

### OpenAI Codex (ChatGPT 订阅 — 无需 API 密钥)
```bash
npx @openai/codex login   # 一次验证
```
```dotenv
LLM_PROVIDER=codex
# LLM_API_KEY 不需要
```

LLM 失败不会导致崩溃 — Crucix 会自动回退到基于规则的警报评估，而不会中断扫描周期。

---

## 架构与数据流

每个 15 分钟的扫描周期：
1. **并行获取** — 同时查询所有 27 个源 (~30–60 秒)
2. **综合** — 原始数据标准化为仪表盘格式
3. **增量计算** — 与上次运行相比，发生了什么变化、升级或降级
4. **LLM 分析** — 生成 5–8 个交易想法 (或基于规则的回退)
5. **警报评估** — FLASH / 优先级 / 例行级别，带有语义去重
6. **推送** — SSE 更新到所有连接的浏览器 + 如果配置了 Telegram/Discord
7. **持久化** — 扫描写入到 `./runs/` 目录

---

## 仪表盘功能

- **3D WebGL 球体** (Globe.gl) 带有大气层、星空、旋转 + 平面地图切换
- **9 种标记类型**：火灾、飞机、辐射、海上咽喉、SDR 接收器、OSINT 事件、健康警报、地理定位新闻、冲突事件
- **动画 3D 航线** 在空中交通热点之间
- **区域过滤器**：世界、美洲、欧洲、中东、亚太、非洲
- **实时市场**：指数、加密货币、能源、大宗商品 (Yahoo Finance，无需密钥)
- **风险指标**：VIX、高收益利差、供应链压力指数
- **OSINT 源**：17 个内置 Telegram 智能频道
- **扫描增量面板**：此周期内发生变化的实时差异
- **核监测**：Safecast + EPA RadNet 辐射读数
- **太空监测**：CelesTrak 卫星追踪 — 国际空间站、Starlink、军事星座

---

## 常见模式

### 最小化设置 (无 API 密钥)
```bash
# 直接工作 — 没有密钥的源仍然会填充：
# Yahoo Finance 市场、CelesTrak 卫星、GDELT 新闻、RSS 源，
# OpenSky 航班追踪 (公共级别)、Safecast 辐射
npm run dev
```

### 最大免费覆盖范围
```dotenv
# 注册所有三个免费密钥 (~3 分钟总时间):
FRED_API_KEY=       # fred.stlouisfed.org — 60 秒注册
FIRMS_MAP_KEY=      # firms.modaps.eosdis.nasa.gov — 60 秒注册
EIA_API_KEY=        # eia.gov/opendata/register.php — 60 秒注册
```

### 仅 Telegram 警报 (无 LLM)
```dotenv
TELEGRAM_BOT_TOKEN=your_token_from_botfather
TELEGRAM_CHAT_ID=your_chat_id_from_userinfobot
# LLM_PROVIDER 故意省略 — 基于规则的警报仍然会触发
```

### 带有 LLM 和两个机器人的完整堆栈
```dotenv
FRED_API_KEY=...
FIRMS_MAP_KEY=...
EIA_API_KEY=...
LLM_PROVIDER=anthropic
LLM_API_KEY=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
DISCORD_BOT_TOKEN=...
DISCORD_CHANNEL_ID=...
DISCORD_GUILD_ID=...   # 用于立即斜杠命令注册
```

### 添加额外的 Telegram OSINT 频道
```dotenv
# 超过 17 个内置频道的逗号分隔频道 ID
TELEGRAM_CHANNELS=-1001234567890,-1009876543210
```

---

## 故障排除

**启动后仪表盘为空:**
正常 — 第一次扫描需要 30–60 秒来查询所有 27 个源。在它完成之前不要期望数据。

**`npm run dev` 安静退出 (尤其是在 Windows PowerShell 上):**
```bash
node --trace-warnings server.mjs
# 或运行诊断工具:
node diag.mjs
```

**端口已被占用:**
```bash
# 默认端口是 3117 — 检查是否有其他东西在使用它:
lsof -i :3117        # macOS/Linux
netstat -ano | findstr :3117   # Windows
```

**Telegram 机器人未接收命令:**
- 验证 `TELEGRAM_BOT_TOKEN` 和 `TELEGRAM_CHAT_ID` 都已设置
- 确认聊天 ID 是您的个人聊天，而不是群组 (使用 @userinfobot)
- 默认轮询间隔为 5000ms — 设置 `TELEGRAM_POLL_INTERVAL=2000` 以获得更快的响应

**Discord 斜杠命令未出现:**
- 设置 `DISCORD_GUILD_ID` 以立即注册 (而不是长达 1 小时的全局)
- 确保机器人邀请 URL 包含 `bot` 和 `applications.commands` 范围
- 检查 **消息内容意图** 在开发者门户中已启用

**LLM 错误导致扫描崩溃:**
它们不会 — LLM 失败会被捕获，扫描继续使用基于规则的回退。检查日志以获取特定提供者的错误 (无效密钥、速率限制等)。

**ACLED 冲突数据缺失:**
ACLED 使用 OAuth2 并需要电子邮件/密码 — `ACLED_EMAIL` 和 `ACLED_PASSWORD` 必须一起设置。

**扫描数据持久化:**
所有运行都会保存到 `./runs/`。在 Docker 中，这是通过卷挂载实现的，因此数据在容器重启后仍然存在。
