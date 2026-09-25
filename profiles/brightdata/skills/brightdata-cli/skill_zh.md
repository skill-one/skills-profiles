# Bright Data CLI

Bright Data CLI (`brightdata`或`bdata`)让您能够通过终端完整访问Bright Data的网页数据平台。它自动处理身份验证、代理区域、反爬虫绕过、验证码识别和JavaScript渲染——用户只需登录一次即可。

## 安装

如果尚未安装CLI，请引导用户：

**macOS / Linux:**
```bash
curl -fsSL https://cli.brightdata.com/install.sh | bash
```

**Windows或手动安装（任何平台）:**
```bash
npm install -g @brightdata/cli
```

**无需安装（一次性使用）:**
```bash
npx --yes --package @brightdata/cli brightdata <command>
```

需要Node.js >= 20。安装后，`brightdata`和`bdata`（简称）均可使用。

## 首次设置

在所有操作之前，请检查用户是否已通过身份验证。如果他们尚未登录，请引导他们完成一次性设置：

```bash
# 一次性登录——打开浏览器进行OAuth认证，然后一切自动完成
bdata login
```

此命令将：
1. 打开浏览器进行安全的OAuth身份验证
2. 本地保存API密钥（无需再次输入）
3. 自动创建所需的代理区域（`cli_unlocker`，`cli_browser`）
4. 设置默认配置

登录后，后续的所有命令无需任何手动干预即可运行。

对于无头/SSH环境（没有浏览器可用）：
```bash
bdata login --device
```

对于直接API密钥认证（非交互式）：
```bash
bdata login --api-key <key>
```

为验证设置是否完成，请运行：
```bash
bdata config
```

## 命令参考

完整命令参考（包括所有标志、选项和每个命令的示例），请参阅[references/commands.md](references/commands.md)。

完整40+管道类型（亚马逊、领英、Instagram、抖音、YouTube、Reddit等）及其特定参数列表，请参阅[references/pipelines.md](references/pipelines.md)。

## 快速命令概览

`bdata`是`brightdata`的简称。两者功能完全相同。

| 命令 | 目的 |
|---------|---------|
| `bdata scrape <url>` | 将任何URL抓取为markdown、HTML、JSON或截图 |
| `bdata search "<query>"` | 使用结构化结果搜索Google/Bing/Yandex |
| `bdata pipelines <type> [params]` | 从40+平台提取结构化数据 |
| `bdata pipelines list` | 列出所有40+可用管道类型 |
| `bdata status <job-id>` | 检查异步任务状态 |
| `bdata zones` | 列出代理区域 |
| `bdata budget` | 查看账户余额和费用 |
| `bdata skill add` | 安装AI代理技能 |
| `bdata skill list` | 列出可用技能 |
| `bdata config` | 查看/设置配置 |
| `bdata login` | 使用Bright Data进行身份验证 |
| `bdata version` | 显示CLI版本和系统信息 |

## 如何使用每个命令

### 抓取

使用自动反爬虫绕过、验证码处理和JS渲染抓取任何URL：

```bash
# 默认：返回干净的markdown
bdata scrape https://example.com

# 获取原始HTML
bdata scrape https://example.com -f html

# 获取结构化JSON
bdata scrape https://example.com -f json

# 截图
bdata scrape https://example.com -f screenshot -o page.png

# 从美国进行地理定位抓取
bdata scrape https://amazon.com --country us

# 保存到文件
bdata scrape https://example.com -o page.md

# 异步模式（适用于重页面）
bdata scrape https://example.com --async
```

### 搜索

搜索引擎提供结构化JSON输出（Google返回解析的有机结果、广告、People Also Ask和相关搜索）：

```bash
# 格式化表格的Google搜索
bdata search "web scraping best practices"

# 获取原始JSON用于管道
bdata search "typescript tutorials" --json

# 搜索Bing
bdata search "bright data pricing" --engine bing

# 本地化搜索
bdata search "restaurants berlin" --country de --language de

# 新闻搜索
bdata search "AI regulation" --type news

# 提取URL
bdata search "open source tools" --json | jq -r '.organic[].link'
```

### 管道（结构化数据提取）

从40+平台提取结构化数据。这些会触发异步任务，直到结果准备好：

```bash
# 领英个人资料
bdata pipelines linkedin_person_profile "https://linkedin.com/in/username"

# 亚马逊产品
bdata pipelines amazon_product "https://amazon.com/dp/B09V3KXJPB"

# Instagram个人资料
bdata pipelines instagram_profiles "https://instagram.com/username"

# 亚马逊搜索
bdata pipelines amazon_product_search "laptop" "https://amazon.com"

# YouTube评论（前50条）
bdata pipelines youtube_comments "https://youtube.com/watch?v=..." 50

# Google Maps评论（最近7天）
bdata pipelines google_maps_reviews "https://maps.google.com/..." 7

# 输出为CSV
bdata pipelines amazon_product "https://amazon.com/dp/..." --format csv -o product.csv

# 列出所有可用管道类型
bdata pipelines list
```

### 检查状态

对于异步任务（来自`--async`抓取或管道）：

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

# 详细余额（包括待处理费用）
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

### 安装AI代理技能

```bash
# 交互式选择器——选择技能和目标代理
bdata skill add

# 安装特定技能
bdata skill add scrape

# 列出可用技能
bdata skill list
```

## 输出模式

每个命令都支持多种输出格式：

| 标志 | 效果 |
|------|------|
| *(无)* | 带颜色的可读格式输出 |
| `--json` | 紧凑JSON输出到stdout |
| `--pretty` | 带缩进的JSON输出到stdout |
| `-o <path>` | 写入文件（自动检测扩展名确定格式） |

当管道（stdout不是TTY）时，颜色和加载动画会自动禁用。

## 命令链式调用

CLI支持管道：

```bash
# 搜索→提取第一个URL→抓取它
bdata search "top open source projects" --json \
  | jq -r '.organic[0].link' \
  | xargs bdata scrape

# 抓取并使用markdown阅读器查看
bdata scrape https://docs.github.com | glow -

# 亚马逊产品数据到CSV
bdata pipelines amazon_product "https://amazon.com/dp/xxx" --format csv > product.csv
```

## 环境变量

这些会覆盖存储的配置：

| 变量 | 目的 |
|----------|---------|
| `BRIGHTDATA_API_KEY` | API密钥（完全跳过登录） |
| `BRIGHTDATA_UNLOCKER_ZONE` | 默认Web解锁器区域 |
| `BRIGHTDATA_SERP_ZONE` | 默认SERP区域 |
| `BRIGHTDATA_POLLING_TIMEOUT` | 秒级轮询超时 |

## 故障排除

| 错误 | 解决方法 |
|-------|-----|
| CLI未找到 | 使用`npm i -g @brightdata/cli`或`curl -fsSL https://cli.brightdata.com/install.sh \| bash`安装 |
| "未指定Web解锁器区域" | `bdata config set default_zone_unlocker <zone>`或重新运行`bdata login` |
| "无效或过期的API密钥" | `bdata login` |
| "访问被拒绝" | 在Bright Data控制面板中检查区域权限 |
| "超出速率限制" | 等待并重试，或使用`--async`处理大任务 |
| 异步任务超时 | 使用`--timeout 1200`或`BRIGHTDATA_POLLING_TIMEOUT=1200`增加超时 |

## 关键设计原则

- **一次性认证**：`bdata login`后，一切自动完成。无需管理令牌，无需传递密钥。
- **区域自动创建**：登录时自动创建`cli_unlocker`和`cli_browser`区域。
- **智能默认值**：markdown输出，从文件扩展名自动检测格式，仅在TTY中显示颜色。
- **支持管道**：JSON输出+jq用于自动化。管道中禁用颜色/加载动画。
- **异步支持**：重任务可使用`--async`+`status --wait`在后台运行。
- **npm包**：`@brightdata/cli`——可全局安装或使用`npx`。
