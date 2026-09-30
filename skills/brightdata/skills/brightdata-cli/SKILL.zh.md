---
name: brightdata-cli
description: 使用 Bright Data CLI (`brightdata` / `bdata`) 进行网站抓取、网络搜索、从 40+ 平台提取结构化数据、管理代理区域以及检查账户预算的指南。当用户需要抓取 URL、搜索 Google/Bing/Yandex、从 Amazon/LinkedIn/Instagram/TikTok/YouTube/Reddit 或任何其他平台提取数据、检查其 Bright Data 余额或区域，或通过终端进行任何网络数据收集操作时，均可使用此技能。此外，当用户提及 brightdata、bdata、网络抓取 CLI、SERP API，或希望将 Bright Data 技能安装到其代码代理中时，也会触发该技能。
---

# Bright Data CLI

Bright Data CLI (`brightdata` 或 `bdata`) 可让您从终端完整访问 Bright Data 的网络数据平台。它自动处理身份验证、代理区域、反机器人绕过、CAPTCHA 解析和 JavaScript 渲染 — 用户只需登录一次。

## 安装

如果尚未安装 CLI，请引导用户：

**macOS / Linux:**
```bash
curl -fsSL https://cli.brightdata.com/install.sh | bash
```

**Windows 或手动安装（任何平台）:**
```bash
npm install -g @brightdata/cli
```

**不安装（一次性使用）:**
```bash
npx --yes --package @brightdata/cli brightdata <command>
```

需要 Node.js >= 20。安装后，`brightdata` 和 `bdata`（简称）均可使用。

## 首次设置

在其他任何操作之前，检查用户是否已通过身份验证。如果他们尚未登录，请引导他们完成一次性设置：

```bash
# 一次性登录 — 打开浏览器进行 OAuth 认证，然后一切自动完成
bdata login
```

此单一命令：
1. 打开浏览器进行安全的 OAuth 认证
2. 本地保存 API 密钥（无需再输入）
3. 自动创建所需的代理区域（`cli_unlocker`、`cli_browser`）
4. 设置默认配置

登录后，后续的每个命令都可以无需任何手动干预即可运行。

对于没有浏览器的无头/SSH 环境：
```bash
bdata login --device
```

对于直接 API 密钥认证（非交互式）：
```bash
bdata login --api-key <key>
```

要验证设置是否完成，请运行：
```bash
bdata config
```

## 命令参考

阅读 [references/commands.md](references/commands.md) 获取包含所有标志、选项和每个命令示例的完整命令参考。

阅读 [references/pipelines.md](references/pipelines.md) 获取 40 多种管道类型（亚马逊、领英、Instagram、抖音、YouTube、Reddit 等）及其特定参数的完整列表。

## 快速命令概览

`bdata` 是 `brightdata` 的简称。两者功能完全相同。

| 命令 | 目的 |
|---------|---------|
| `bdata scrape <url>` | 将任何 URL 抓取为 markdown、HTML、JSON 或截图 |
| `bdata search "<query>"` | 使用结构化结果搜索 Google/Bing/Yandex |
| `bdata pipelines <type> [params]` | 从 40 多个平台提取结构化数据 |
| `bdata pipelines list` | 列出所有 40 多种可用的管道类型 |
| `bdata status <job-id>` | 检查异步作业状态 |
| `bdata zones` | 列出代理区域 |
| `bdata budget` | 查看账户余额和费用 |
| `bdata skill add` | 安装 AI 代理技能 |
| `bdata skill list` | 列出可用技能 |
| `bdata config` | 查看/设置配置 |
| `bdata login` | 使用 Bright Data 进行身份验证 |
| `bdata version` | 显示 CLI 版本和系统信息 |

## 如何使用每个命令

### 抓取

使用自动反机器人绕过、CAPTCHA 处理和 JS 渲染抓取任何 URL：

```bash
# 默认：返回干净的 markdown
bdata scrape https://example.com

# 获取原始 HTML
bdata scrape https://example.com -f html

# 获取结构化 JSON
bdata scrape https://example.com -f json

# 拍摄截图
bdata scrape https://example.com -f screenshot -o page.png

# 从美国进行地理定位抓取
bdata scrape https://amazon.com --country us

# 保存到文件
bdata scrape https://example.com -o page.md

# 异步模式用于重页面
bdata scrape https://example.com --async
```

### 搜索

搜索引擎具有结构化 JSON 输出（Google 返回解析的有机结果、广告、People Also Ask 和相关搜索）：

```bash
# Google 搜索带格式化表格
bdata search "web scraping best practices"

# 获取原始 JSON 以便管道传输
bdata search "typescript tutorials" --json

# 搜索 Bing
bdata search "bright data pricing" --engine bing

# 本地化搜索
bdata search "restaurants berlin" --country de --language de

# 新闻搜索
bdata search "AI regulation" --type news

# 提取仅 URL
bdata search "open source tools" --json | jq -r '.organic[].link'
```

### 管道（结构化数据提取）

从 40 多个平台提取结构化数据。这些会触发异步作业，直到结果准备好才会轮询：

```bash
# 领英个人资料
bdata pipelines linkedin_person_profile "https://linkedin.com/in/username"

# 亚马逊产品
bdata pipelines amazon_product "https://amazon.com/dp/B09V3KXJPB"

# Instagram 资料卡
bdata pipelines instagram_profiles "https://instagram.com/username"

# 亚马逊搜索
bdata pipelines amazon_product_search "laptop" "https://amazon.com"

# YouTube 评论（前 50 条）
bdata pipelines youtube_comments "https://youtube.com/watch?v=..." 50

# Google 地图评论（最后 7 天）
bdata pipelines google_maps_reviews "https://maps.google.com/..." 7

# 输出为 CSV
bdata pipelines amazon_product "https://amazon.com/dp/..." --format csv -o product.csv

# 列出所有可用的管道类型
bdata pipelines list
```

### 检查状态

对于异步作业（来自 `--async` 抓取或管道）：

```bash
# 快速状态检查
bdata status <job-id>

# 等待完成
bdata status <job-id> --wait

# 自定义超时
bdata status <job-id> --wait --timeout 300
```

### 预算和区域

```bash
# 快速账户余额
bdata budget

# 详细余额，包括待处理的费用
bdata budget balance

# 所有区域成本/带宽
bdata budget zones

# 特定区域成本
bdata budget zone my_zone

# 日期范围过滤
bdata budget zones --from 2024-01-01T00:00:00 --to 2024-02-01T00:00:00

# 列出所有区域
bdata zones

# 区域详情
bdata zones info cli_unlocker
```

### 配置

```bash
# 查看所有配置
bdata config

# 设置默认值
bdata config set default_zone_unlocker my_zone
bdata config set default_format json
```

### 安装 AI 代理技能

```bash
# 交互式选择器 — 选择技能和目标代理
bdata skill add

# 安装特定技能
bdata skill add scrape

# 列出可用技能
bdata skill list
```

## 输出模式

每个命令都支持多种输出格式：

| 标志 | 效果 |
|---------|---------|
| *(无)* | 带颜色的可读格式化输出 |
| `--json` | 紧凑的 JSON 输出到标准输出 |
| `--pretty` | 带缩进的 JSON 输出到标准输出 |
| `-o <path>` | 写入文件（从扩展名自动检测格式） |

当管道传输（标准输出不是 TTY）时，颜色和旋转器会自动禁用。

## 命令链式调用

CLI 对管道传输友好：

```bash
# 搜索 → 提取第一个 URL → 抓取它
bdata search "top open source projects" --json \
  | jq -r '.organic[0].link' \
  | xargs bdata scrape

# 抓取并使用 markdown 阅读器查看
bdata scrape https://docs.github.com | glow -

# 亚马逊产品数据到 CSV
bdata pipelines amazon_product "https://amazon.com/dp/xxx" --format csv > product.csv
```

## 环境变量

这些会覆盖存储的配置：

| 变量 | 目的 |
|----------|---------|
| `BRIGHTDATA_API_KEY` | API 密钥（完全跳过登录） |
| `BRIGHTDATA_UNLOCKER_ZONE` | 默认 Web Unlocker 区域 |
| `BRIGHTDATA_SERP_ZONE` | 默认 SERP 区域 |
| `BRIGHTDATA_POLLING_TIMEOUT` | 轮询超时（秒） |

## 故障排除

| 错误 | 解决方法 |
|-------|-----|
| CLI 未找到 | 使用 `npm i -g @brightdata/cli` 或 `curl -fsSL https://cli.brightdata.com/install.sh \| bash` 安装 |
| "未指定 Web Unlocker 区域" | `bdata config set default_zone_unlocker <zone>` 或重新运行 `bdata login` |
| "无效或过期的 API 密钥" | `bdata login` |
| "访问被拒绝" | 在 Bright Data 控制面板中检查区域权限 |
| "超出速率限制" | 等待并重试，或使用 `--async` 处理大型作业 |
| 异步作业超时 | 使用 `--timeout 1200` 或 `BRIGHTDATA_POLLING_TIMEOUT=1200` 增加超时 |

## 关键设计原则

- **一次性认证**：登录 `bdata` 后，一切自动完成。无需管理令牌，无需传递密钥。
- **区域自动创建**：登录会自动创建 `cli_unlocker` 和 `cli_browser` 区域。
- **智能默认值**：markdown 输出，从文件扩展名自动检测格式，仅在 TTY 中显示颜色。
- **对管道友好**：JSON 输出 + jq 用于自动化。在管道中禁用颜色/旋转器。
- **异步支持**：重页面可以在后台运行，使用 `--async` + `status --wait`。
- **npm 包**：`@brightdata/cli` — 可以全局安装或使用 `npx`。
