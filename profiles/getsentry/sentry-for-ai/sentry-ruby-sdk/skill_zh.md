> [所有技能](../../SKILL_TREE.md) > [SDK 安装](../sentry-sdk-setup/SKILL.md) > Ruby SDK

# Sentry Ruby SDK

一个有主见的向导，扫描项目并指导完成 Sentry 的完整设置。

## 在以下情况调用此技能

- 用户询问在 Ruby 应用中“添加 Sentry”或“设置 Sentry”
- 用户希望在 Ruby 中进行错误监控、跟踪、日志记录、指标、分析或定时任务
- 用户提到 `sentry-ruby`、`sentry-rails` 或 Ruby Sentry SDK
- 用户从 AppSignal、Honeybadger、Bugsnag、Rollbar 或 Airbrake 迁移到 Sentry
- 用户希望在 Rails/Sinatra 中监控异常、HTTP 请求或后台作业

> **注意：** 以下 SDK API 反映 sentry-ruby v6.6.2 版本。
> 在实施之前，请始终参考 [docs.sentry.io/platforms/ruby/](https://docs.sentry.io/platforms/ruby/) 进行验证。

---

## 第一阶段：检测

```bash
# 现有的 Sentry gem
grep -i sentry Gemfile 2>/dev/null

# 框架
grep -iE '\brails\b|\bsinatra\b' Gemfile 2>/dev/null

# Web 服务器 — Puma 触发队列时间指导
grep -iE '\bpuma\b' Gemfile 2>/dev/null

# 后台作业
grep -iE '\bsidekiq\b|\bresque\b|\bdelayed_job\b' Gemfile 2>/dev/null

# Yabeda 指标框架
grep -iE '\byabeda\b' Gemfile 2>/dev/null

# 竞争对手监控工具 — 如果找到则触发迁移路径
grep -iE '\bappsignal\b|\bhoneybadger\b|\bbugsnag\b|\brollbar\b|\bairbrake\b' Gemfile 2>/dev/null

# 定时任务 — 触发 Crons 建议
grep -iE '\bsidekiq-cron\b|\bclockwork\b|\bwhenever\b|\brufus-scheduler\b' Gemfile 2>/dev/null
grep -rn "Sidekiq::Cron\|Clockwork\|every.*do" config/ lib/ --include="*.rb" 2>/dev/null | head -10

# OpenTelemetry 跟踪 — 检查 SDK 和仪器化
grep -iE '\bopentelemetry-sdk\b|\bopentelemetry-instrumentation\b' Gemfile 2>/dev/null
grep -rn "OpenTelemetry::SDK\.configure\|\.use_all\|\.in_span" config/ lib/ app/ --include="*.rb" 2>/dev/null | head -5

# 现有的指标模式（StatsD、Datadog、Prometheus）
grep -rE "(statsd|dogstatsd|prometheus|\.gauge|\.histogram|\.increment|\.timing)" \
  app/ lib/ --include="*.rb" 2>/dev/null | grep -v "_spec\|_test" | head -20

# 伴随的前端
cat package.json frontend/package.json web/package.json 2>/dev/null | grep -E '"@sentry|"sentry-'
```

**根据发现进行路由：**
- **检测到竞争对手** (`appsignal`, `honeybadger`, `bugsnag`, `rollbar`, `airbrake`) → 首先加载 `${SKILL_ROOT}/references/migration.md`；作为迁移的一部分**删除竞争对手的初始化器**
- **Sentry 已存在** → 跳转到第二阶段配置功能
- **Rails** → 使用 `sentry-rails` + `config/initializers/sentry.rb`
- **Rack/Sinatra/纯 Ruby** → `sentry-ruby` + `Sentry::Rack::CaptureExceptions` 中间件
- **Sidekiq** → 添加 `sentry-sidekiq`；如果发现现有的指标模式，建议 Metrics
- **Yabeda 检测到** → 添加 `sentry-yabeda`；将 Yabeda 指标路由到 Sentry 指标
- **Puma 检测到** → 队列时间捕获是自动的（v6.4.0+），但反向代理必须设置 `X-Request-Start` 标头；见 `${SKILL_ROOT}/references/tracing.md` → "请求队列时间"
- **OTel 跟踪检测到** (`opentelemetry-sdk` + Gemfile 中的仪器化，或源代码中的 `OpenTelemetry::SDK.configure`) → 使用 OTLP 路径：`config.otlp.enabled = true`；**不要**设置 `traces_sample_rate`；Sentry 会自动将错误链接到 OTel 跟踪

---

## 第二阶段：建议

提出具体的建议，不要问开放式问题：

| 功能 | 当...建议 |
|------|----------|
| 错误监控 | **始终** |
| OTLP 集成 | OTel 跟踪检测到 — **替换** 原生跟踪 |
| 跟踪 | Rails / Sinatra / Rack / 任何 HTTP 框架；**如果 OTel 跟踪检测到则跳过** |
| 日志记录 | **始终** — `enable_logs: true` 没有成本 |
| 指标 | Sidekiq 存在；检测到现有的指标库（StatsD、Prometheus） |
| 分析 | ⚠️ Beta — 请求性能分析；需要 `stackprof` 或 `vernier` gem；**如果 OTel 跟踪检测到则跳过**（需要 `traces_sample_rate`，与 OTLP 不兼容） |
| 定时任务 | 检测到定时任务（ActiveJob、Sidekiq-Cron、Clockwork、Whenever） |

**OTel 跟踪检测到：** *"我在项目中看到 OpenTelemetry 跟踪。我建议 Sentry 的 OTLP 集成用于跟踪（通过您现有的 OTel 设置）+ 错误监控 + Sentry 日志记录[+ 指标/定时任务（如果适用）]。是否继续？"*

**没有 OTel：** *"我建议错误监控 + 跟踪 + 日志记录[+ 指标（如果适用）]。是否继续？"*

---

## 第三阶段：指导

### 安装

**Rails:**
```ruby
# Gemfile
gem "sentry-ruby"
gem "sentry-rails"
gem "sentry-sidekiq"      # 如果使用 Sidekiq
gem "sentry-resque"       # 如果使用 Resque
gem "sentry-delayed_job"  # 如果使用 DelayedJob
gem "sentry-yabeda"       # 如果使用 Yabeda 指标框架
```

**Rack / Sinatra / 纯 Ruby:**
```ruby
gem "sentry-ruby"
```

运行 `bundle install`。

### 框架集成

| 框架 / 运行时 | Gem | 初始化位置 | 自动仪器化 |
|----------------|-----|------------|------------|
| Rails | `sentry-rails` | `config/initializers/sentry.rb` | 控制器、ActiveRecord、ActiveJob、ActionMailer |
| Rack / Sinatra | `sentry-ruby` | `config.ru` 的顶部 | 请求（通过 `Sentry::Rack::CaptureExceptions` 中间件） |
| Sidekiq | `sentry-sidekiq` | Sentry 初始化器或 Sidekiq 配置 | 工作执行 → 事务 |
| Resque | `sentry-resque` | Sentry 初始化器 | 工作执行 → 事务 |
| DelayedJob | `sentry-delayed_job` | Sentry 初始化器 | 任务执行 → 事务 |
| Yabeda 指标 | `sentry-yabeda` | Sentry 初始化器 | Yabeda 指标事件 → Sentry 指标 |

### 初始化 — Rails (`config/initializers/sentry.rb`)

```ruby
Sentry.init do |config|
  config.dsn = ENV["SENTRY_DSN"]
  config.spotlight = Rails.env.development?  # 本地 Spotlight UI；开发环境中不需要 DSN
  config.breadcrumbs_logger = [:active_support_logger, :http_logger]
  config.send_default_pii = true
  config.traces_sample_rate = 1.0  # 在生产环境中降低到 0.05–0.2
  config.enable_logs = true
  # 默认启用指标；使用 `config.enable_metrics = false` 禁用
end
```

`sentry-rails` 自动仪器化 ActionController、ActiveRecord、ActiveJob、ActionMailer。

### 初始化 — Rack / Sinatra

```ruby
require "sentry-ruby"

Sentry.init do |config|
  config.dsn = ENV["SENTRY_DSN"]
  config.spotlight = ENV["RACK_ENV"] == "development"
  config.breadcrumbs_logger = [:sentry_logger, :http_logger]
  config.send_default_pii = true
  config.traces_sample_rate = 1.0
  config.enable_logs = true
end

use Sentry::Rack::CaptureExceptions  # 在 config.ru 中，在应用中间件之前
```

### 初始化 — Sidekiq 独立

```ruby
require "sentry-ruby"
require "sentry-sidekiq"

Sentry.init do |config|
  config.dsn = ENV["SENTRY_DSN"]
  config.spotlight = ENV.fetch("RAILS_ENV", "development") == "development"
  config.breadcrumbs_logger = [:sentry_logger]
  config.traces_sample_rate = 1.0
  config.enable_logs = true
end
```

### 环境变量

```bash
SENTRY_DSN=https://xxx@oYYY.ingest.sentry.io/ZZZ
SENTRY_ENVIRONMENT=production   # 覆盖 RAILS_ENV / RACK_ENV
SENTRY_RELEASE=my-app@1.0.0
```

### 功能参考文件

逐个遍历功能。加载每个功能的参考文件，按照其步骤操作，并在继续下一个之前进行验证：

| 功能 | 参考文件 | 加载时... |
|------|----------|----------|
| 迁移 | `${SKILL_ROOT}/references/migration.md` | 检测到竞争对手 gem — 在安装 Sentry 之前加载 |
| 错误监控 | `${SKILL_ROOT}/references/error-monitoring.md` | 始终 |
| 跟踪 | `${SKILL_ROOT}/references/tracing.md` | HTTP 处理程序 / 分布式跟踪 |
| 日志记录 | `${SKILL_ROOT}/references/logging.md` | 结构化日志捕获 |
| 指标 | `${SKILL_ROOT}/references/metrics.md` | Sidekiq 存在；检测到现有的指标模式 |
| 分析 | `${SKILL_ROOT}/references/profiling.md` | 请求性能分析（Beta） |
| 定时任务 | `${SKILL_ROOT}/references/crons.md` | 检测到定时任务或请求 |

对于每个功能：`读取 ${SKILL_ROOT}/references/<feature>.md`，精确跟随步骤，验证其是否正常工作。

---

## 配置参考

### `Sentry.init` 的关键选项

| 选项 | 类型 | 默认值 | 目的 |
|------|------|--------|------|
| `dsn` | 字符串 | `nil` | 如果为空则禁用 SDK；环境：`SENTRY_DSN` |
| `environment` | 字符串 | `nil` | 例如，`"production"`；环境：`SENTRY_ENVIRONMENT` |
| `release` | 字符串 | `nil` | 例如，`"myapp@1.0.0"`；环境：`SENTRY_RELEASE` |
| `spotlight` | 布尔值 | `false` | 将事件发送到 Spotlight 侧车（本地开发，不需要 DSN） |
| `send_default_pii` | 布尔值 | `false` | 包括 IP 地址和请求标头 |
| `sample_rate` | 浮点数 | `1.0` | 错误事件采样率（0.0–1.0） |
| `traces_sample_rate` | 浮点数 | `nil` | 事务采样率；`nil` 禁用跟踪 |
| `profiles_sample_rate` | 浮点数 | `nil` | 分析率相对于 `traces_sample_rate`；需要 `stackprof` 或 `vernier` |
| `enable_logs` | 布尔值 | `false` | 启用 Sentry 结构化日志 |
| `enable_metrics` | 布尔值 | `true` | 启用自定义指标（默认启用） |
| `breadcrumbs_logger` | 数组 | `[]` | 自动 breadcrumbs 的日志记录器（见日志记录参考） |
| `max_breadcrumbs` | 整数 | `100` | 每个事件的最大 breadcrumbs |
| `debug` | 布尔值 | `false` | 详细的 SDK 输出到 stdout |
| `capture_queue_time` | 布尔值 | `true` | 从 `X-Request-Start` 标头记录请求队列时间（v6.4.0+，Rails 在 v6.4.1 中修复） |
| `otlp.enabled` | 布尔值 | `false` | 通过 OTLP 将 OTel 跨段路由到 Sentry；**不要**与 `traces_sample_rate` 结合使用 |
| `otlp.collector_url` | 字符串 | `nil` | OTel 收集器的 OTLP HTTP 端点（例如，`http://localhost:4318/v1/traces`）；设置后，跨段将发送到收集器而不是直接发送到 Sentry |
| `org_id` | 字符串 | `nil` | 显式组织 ID；覆盖 DSN 提取的值；适用于自托管/Relay 设置（v6.5.0+） |
| `strict_trace_continuation` | 布尔值 | `false` | 仅当 `sentry-org_id` 负载匹配 SDK 的组织 ID 时才继续传入的跨段；防止从第三方服务拼接跨段（v6.5.0+） |
| `before_send` | Lambda | `nil` | 在发送之前修改或丢弃错误事件 |
| `before_send_transaction` | Lambda | `nil` | 在发送之前修改或丢弃事务事件 |
| `before_send_log` | Lambda | `nil` | 在发送之前修改或丢弃日志事件 |

### 环境变量

| 变量 | 映射到 | 目的 |
|------|--------|------|
| `SENTRY_DSN` | `dsn` | 数据源名称 |
| `SENTRY_RELEASE` | `release` | 应用版本（例如，`my-app@1.0.0`） |
| `SENTRY_ENVIRONMENT` | `environment` | 部署环境 |

在 `Sentry.init` 中设置的选项会覆盖环境变量。

---

## 验证

**本地开发（不需要 DSN）— Spotlight:**
```bash
npx @spotlightjs/spotlight          # 浏览器 UI 在 http://localhost:8969
# 或者将事件流到终端：
npx @spotlightjs/spotlight tail traces --format json
```
`config.spotlight = Rails.env.development?`（已在上述初始化块中）自动将事件路由到本地侧车。

**使用真实的 DSN:**
```ruby
Sentry.capture_message("Sentry Ruby SDK test")
```

没有任何显示？设置 `config.debug = true` 并检查 stdout。验证 DSN 格式：`https://<key>@o<org>.ingest.sentry.io/<project>`。

---

## 第四阶段：跨链接

```bash
cat package.json frontend/package.json web/package.json 2>/dev/null | grep -E '"@sentry|"sentry-'
```

| 前端检测到 | 建议 |
|------------|------|
| React / Next.js | `sentry-react-sdk` |
| Svelte / SvelteKit | `sentry-svelte-sdk` |
| Vue | `@sentry/vue` — [docs.sentry.io/platforms/javascript/guides/vue/](https://docs.sentry.io/platforms/javascript/guides/vue/) |

对于 Ruby 后端和 JS 前端之间的跨段拼接，请参阅 `references/tracing.md` → "前端跨段拼接"。

---

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| 事件未出现 | `config.debug = true`；验证 DSN；确保 `Sentry.init` 在第一个请求之前 |
| Rails 异常缺失 | 必须使用 `sentry-rails` — `sentry-ruby` 单独使用不会挂钩 Rails 错误处理程序 |
| 没有跨段（原生） | 设置 `traces_sample_rate > 0`；确保 `sentry-rails` 或 `Sentry::Rack::CaptureExceptions` |
| 没有跨段（OTLP） | 验证 `opentelemetry-exporter-otlp` gem 是否已安装；使用 `otlp.enabled = true` 时**不要**设置 `traces_sample_rate` |
| Sidekiq 作业未跟踪 | 添加 `sentry-sidekiq` gem |
| 缺少请求上下文 | 设置 `config.send_default_pii = true` |
| 日志未出现 | 设置 `config.enable_logs = true`；需要 sentry-ruby ≥ 5.27.0 |
| 指标未出现 | 检查 `enable_metrics` 不是 `false`；验证 DSN |
| 关闭时事件丢失 | `Process.exit!` 跳过 `at_exit` 钩子 — 在强制退出之前显式调用 `Sentry.flush` |
| 分叉服务器丢失事件 | Puma/Unicorn 分叉工作进程 — 在 `on_worker_boot` 或 `after_fork` 中重新初始化；如果没有这样做，后台工作线程在子进程中死亡 |
| DSN 拒绝 / 事件未交付 | 验证 DSN 格式：`https://<key>@o<org>.ingest.sentry.io/<project>`；设置 `config.debug = true` 以查看传输错误 |
