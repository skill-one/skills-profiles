> [所有技能](../../SKILL_TREE.md) > [SDK 安装](../sentry-sdk-setup/SKILL.md) > Elixir SDK

# Sentry Elixir SDK

一个有主见的向导，它会扫描您的 Elixir 项目并指导您完成 Sentry 的完整设置。

## 在何时调用此技能

- 用户询问在 Elixir 或 Phoenix 应用中“添加 Sentry”或“设置 Sentry”
- 用户希望在 Elixir 或 Phoenix 中进行错误监控、跟踪、日志记录或定时任务
- 用户提到 `sentry` hex 包、`getsentry/sentry-elixir` 或 Elixir Sentry SDK
- 用户希望监控异常、Plug 错误、LiveView 错误或定时任务

> **注意：** 以下 SDK 版本和 API 反映了编写时 Sentry 文档的状态（sentry v13.2.0，需要 Elixir ~> 1.13）。
> 在实施之前，请始终参考 [docs.sentry.io/platforms/elixir/](https://docs.sentry.io/platforms/elixir/) 进行验证。

---

## 第一阶段：检测

在提出任何建议之前，运行这些命令以了解项目：

```bash
# 检查现有的 Sentry 依赖
grep -i sentry mix.exs 2>/dev/null

# 检测 Elixir 版本
cat .tool-versions 2>/dev/null | grep elixir
grep "elixir:" mix.exs 2>/dev/null

# 检测 Phoenix 或 Plug
grep -E '"phoenix"|"plug"' mix.exs 2>/dev/null

# 检测 Phoenix LiveView
grep "phoenix_live_view" mix.exs 2>/dev/null

# 检测 Oban（任务队列 / 定时任务）
grep "oban" mix.exs 2>/dev/null

# 检测 Quantum（定时任务调度器）
grep "quantum" mix.exs 2>/dev/null

# 检测 OpenTelemetry 使用情况
grep "opentelemetry" mix.exs 2>/dev/null

# 检查配套前端
ls assets/ frontend/ web/ client/ 2>/dev/null
```

**需要注意的事项：**

| 信号 | 影响 |
|------|------|
| `sentry` 已经在 `mix.exs` 中？ | 跳过安装；进入第二阶段（配置功能） |
| 检测到 Phoenix？ | 添加 `Sentry.PlugCapture`、`Sentry.PlugContext`，可选添加 `Sentry.LiveViewHook` |
| 检测到 LiveView？ | 在 `my_app_web.ex` 中的 `live_view` 宏中添加 `Sentry.LiveViewHook` |
| 检测到 Oban？ | 推荐使用 Oban 集成进行定时任务 + 错误捕获 |
| 检测到 Quantum？ | 推荐使用 Quantum 集成进行定时任务 |
| 已经存在 OpenTelemetry？ | 跟踪设置只需要 `Sentry.OpenTelemetry.*` 配置 |
| 检测到前端目录？ | 触发第四阶段跨链接建议 |

---

## 第二阶段：推荐

根据您的发现，提出具体的建议。不要提出开放式问题——直接提出建议：

**推荐（核心覆盖）：**
- ✅ **错误监控** — 总是；捕获异常和崩溃报告
- ✅ **日志记录** — `Sentry.LoggerHandler` 将崩溃报告和错误日志转发到 Sentry
- ✅ **跟踪** — 如果检测到 Phoenix、Plug 或 Ecto（通过 OpenTelemetry）

**可选（增强可观察性）：**
- ⚡ **定时任务** — 检测定时任务中的静默失败（Oban、Quantum 或手动 GenServer）
- ⚡ **Sentry 日志** — 将结构化日志转发到 Sentry 日志协议（sentry v12.0.0+）

**推荐逻辑：**

| 功能 | 当...推荐 |
|------|----------|
| 错误监控 | **始终** — 不可协商的基线 |
| 日志记录 | **始终** — `LoggerHandler` 捕获不是显式 `capture_exception` 调用的崩溃 |
| 跟踪 | 检测到 Phoenix、Plug、Ecto 或 OpenTelemetry 导入 |
| 定时任务 | 检测到 Oban、Quantum 或周期性 `GenServer`/`Task` 模式 |
| Sentry 日志 | 使用 sentry v12.0.0+ 且需要结构化日志搜索 |

提议：*"我建议设置 Error Monitoring + Logging [+ 如果检测到 Phoenix/Ecto 则添加 Tracing]。是否还需要添加 Crons 或 Sentry Logs？*"

---

## 第三阶段：指导

### 选项 1：Igniter 安装器（推荐）

> **您需要自行运行** — Igniter 安装器需要交互式终端输入，代理无法处理。将以下内容复制粘贴到您的终端：
>
> ```bash
> mix igniter.install sentry
> ```
>
> 自 sentry v11.0.0 起可用。它会自动配置 `config/config.exs`、`config/prod.exs`、`config/runtime.exs` 和 `lib/my_app/application.ex`。
>
> **完成后，回来并跳转到 [验证](#verification)。**

如果用户跳过 Igniter 安装器，请继续执行下面的 Option 2（手动设置）。

---

### 选项 2：手动设置

#### 安装

在 `mix.exs` 依赖中添加：

```elixir
# mix.exs
defp deps do
  [
    {:sentry, "~> 13.0"},
    {:finch, "~> 0.21"}
    # 如果使用 Elixir < 1.18，添加 jason：
    # {:jason, "~> 1.4"},
  ]
end
```

```bash
mix deps.get
```

#### 配置

```elixir
# config/config.exs
config :sentry,
  dsn: System.get_env("SENTRY_DSN"),
  environment_name: config_env(),
  enable_source_code_context: true,
  root_source_code_paths: [File.cwd!()],
  in_app_otp_apps: [:my_app]
```

对于运行时配置（推荐用于 DSN 和发布版本）：

```elixir
# config/runtime.exs
import Config

config :sentry,
  dsn: System.fetch_env!("SENTRY_DSN"),
  release: System.get_env("SENTRY_RELEASE", "my-app@#{Application.spec(:my_app, :vsn)}")
```

#### 快速启动——推荐初始化配置

此配置使用合理的默认值启用最多功能：

```elixir
# config/config.exs
config :sentry,
  dsn: System.get_env("SENTRY_DSN"),
  environment_name: config_env(),
  enable_source_code_context: true,
  root_source_code_paths: [File.cwd!()],
  in_app_otp_apps: [:my_app],
  # Logger 处理器配置——捕获崩溃报告
  logger: [
    {:handler, :sentry_handler, Sentry.LoggerHandler, %{
      config: %{
        metadata: [:request_id],
        capture_log_messages: true,
        level: :error
      }
    }}
  ]
```

#### 激活 Logger 处理器

在 `Application.start/2` 中添加 `Logger.add_handlers/1`：

```elixir
# lib/my_app/application.ex
def start(_type, _args) do
  Logger.add_handlers(:my_app)   # 激活上面配置的 :sentry_handler

  children = [
    MyAppWeb.Endpoint
    # ... 其他子进程
  ]

  Supervisor.start_link(children, strategy: :one_for_one)
end
```

#### Phoenix 集成

**`lib/my_app_web/endpoint.ex`**

```elixir
defmodule MyAppWeb.Endpoint do
  use Sentry.PlugCapture          # 在使用 Phoenix.Endpoint（仅 Cowdy）之前添加
  use Phoenix.Endpoint, otp_app: :my_app

  # ...

  plug Plug.Parsers,
    parsers: [:urlencoded, :multipart, :json],
    pass: ["*/*"],
    json_decoder: Phoenix.json_library()

  plug Sentry.PlugContext          # 在 Plug.Parsers 下方添加
  # ...
end
```

> **注意：** `Sentry.PlugCapture` 仅在 **Cowboy** 适配器中需要。Phoenix 1.7+ 默认使用 **Bandit**，其中 `PlugCapture` 无害但不需要。`Sentry.PlugContext` 始终推荐——它使用 HTTP 请求数据丰富事件。

**LiveView 错误——`lib/my_app_web.ex`**

```elixir
def live_view do
  quote do
    use Phoenix.LiveView

    on_mount Sentry.LiveViewHook   # 在 mount/handle_event/handle_info 中捕获错误
  end
end
```

#### 纯 Plug 应用

```elixir
defmodule MyApp.Router do
  use Plug.Router
  use Sentry.PlugCapture          # 仅 Cowdy

  plug Plug.Parsers, parsers: [:urlencoded, :multipart]
  plug Sentry.PlugContext
  # ...
end
```

### 对于每个同意的功能

逐个通过功能。加载每个功能的参考文件，按照其步骤操作，并在进入下一个功能之前进行验证：

| 功能 | 参考文件 | 在何时加载... |
|------|----------|-------------|
| 错误监控 | `${SKILL_ROOT}/references/error-monitoring.md` | 始终（基线） |
| 跟踪 | `${SKILL_ROOT}/references/tracing.md` | 检测到 Phoenix / Ecto / OpenTelemetry |
| 日志记录 | `${SKILL_ROOT}/references/logging.md` | `LoggerHandler` 或 Sentry Logs 设置 |
| 定时任务 | `${SKILL_ROOT}/references/crons.md` | 检测到 Oban、Quantum 或周期性任务 |

对于每个功能：`读取 ${SKILL_ROOT}/references/<功能>.md`，精确跟随步骤，验证其是否正常工作。

---

## 配置参考

### 关键配置选项

| 选项 | 类型 | 默认值 | 目的 |
|------|------|--------|------|
| `:dsn` | `string \| nil` | `nil` | 如果为 nil 则禁用 SDK；环境变量：`SENTRY_DSN` |
| `:environment_name` | `atom \| string` | `"production"` | 例如，`:prod`；环境变量：`SENTRY_ENVIRONMENT` |
| `:release` | `string \| nil` | `nil` | 例如，`"my-app@1.0.0"`；环境变量：`SENTRY_RELEASE` |
| `:sample_rate` | `float` | `1.0` | 错误事件采样率（0.0–1.0） |
| `:enable_source_code_context` | `boolean` | `false` | 在错误周围包含源代码行 |
| `:root_source_code_paths` | `[path]` | `[]` | 启用源代码上下文时必须 |
| `:in_app_otp_apps` | `[atom]` | `[]` | 在堆栈跟踪中“应用内”的 OTP 应用模块 |
| `:before_send` | `(event -> event \| nil) \| {m, f}` | `nil` | 用于变异或丢弃错误事件的钩子 |
| `:after_send_event` | `(event, result -> any) \| {m, f}` | `nil` | 发送事件后调用的钩子 |
| `:filter` | `module` | `Sentry.DefaultEventFilter` | 实现 `Sentry.EventFilter` 的模块 |
| `:max_breadcrumbs` | `integer` | `100` | 每个进程的最大面包屑 |
| `:max_stacktrace_arg_length` | `integer` | `10000` | 堆栈跟踪变量中每个检查的函数参数的最大长度（v13.2.0+） |
| `:dedup_events` | `boolean` | `true` | 在约 30 秒内去重重复事件 |
| `:tags` | `map` | `%{}` | 每个事件发送的全局标签 |
| `:traces_sample_rate` | `float \| nil` | `nil` | 非空则启用跟踪（需要 OTel 设置） |
| `:traces_sampler` | `fn \| {m, f} \| nil` | `nil` | 自定义每笔交易的采样 |
| `:enable_logs` | `boolean` | `false` | 启用 Sentry Logs 协议（v12.0.0+） |
| `:scrubber` | `keyword` | `[]` | 清理配置（v13.1.1+）；键：`:conn_private_allow_list`（`Plug.Conn.private` 中的原子列表） |
| `:test_mode` | `boolean` | `false` | 在内存中捕获事件用于测试 |

### 默认 PII 指导

大多数 Sentry SDK 提供一个 `send-default-PII` 选项。自 sentry v12 起，Elixir SDK 没有在文档选项列表或当前配置模式中暴露 `send_default_pii` 配置选项，因此**不要**添加不存在的选项。对于更丰富的用户上下文，使用 `Sentry.PlugContext` 并使用 `Sentry.Context.set_user_context/1` 明确设置允许的字段，然后在需要时使用 `:before_send` 进行清理。如果未来的 Elixir SDK 版本添加了 `send_default_pii`，建议设置它。

**自动 PII 清理：** 自 v13.1.0 起，堆栈跟踪帧变量和 `FunctionClauseError`/`Phoenix.ActionClauseError` 参数会使用与 HTTP 请求数据相同的清理规则自动清理敏感数据。使用 `:scrubber` 配置自定义保留哪些 `Plug.Conn.private` 键。

### 环境变量

| 变量 | 映射到 | 目的 |
|------|--------|------|
| `SENTRY_DSN` | `:dsn` | 数据源名称 |
| `SENTRY_RELEASE` | `:release` | 应用版本（例如，`my-app@1.0.0`） |
| `SENTRY_ENVIRONMENT` | `:environment_name` | 部署环境 |

---

## 验证

测试 Sentry 是否接收事件：

```bash
# 从您的项目发送测试事件
MIX_ENV=dev mix sentry.send_test_event
```

或者在一个控制器动作中添加临时调用：

```elixir
# 临时测试——确认后删除
def index(conn, _params) do
  Sentry.capture_message("Sentry Elixir SDK 测试事件")
  text(conn, "sent")
end
```

几秒钟内在 Sentry 仪表板中检查。如果什么都没有出现：
1. 设置 `config :sentry, log_level: :debug` 以获取详细的 SDK 输出
2. 验证 `SENTRY_DSN` 是否已设置且项目存在
3. 确认 `:environment_name` 没有设置为 Sentry 在您的警报规则中过滤的值

---

## 第四阶段：跨链接

完成 Elixir 设置后，检查是否有缺少 Sentry 覆盖的配套前端：

```bash
ls assets/ frontend/ web/ client/ ui/ 2>/dev/null
cat assets/package.json frontend/package.json 2>/dev/null | grep -E '"react"|"svelte"|"vue"|"next"'
```

如果存在未配置 Sentry 的前端目录，建议匹配的技能：

| 前端检测到 | 建议技能 |
|------------|----------|
| React / Next.js | `sentry-react-sdk` 或 `sentry-nextjs-sdk` |
| Svelte / SvelteKit | `sentry-svelte-sdk` |
| Vue | 参考 [docs.sentry.io/platforms/javascript/guides/vue/](https://docs.sentry.io/platforms/javascript/guides/vue/) |
| 其他 JS/TS | `sentry-browser-sdk` |

连接 Phoenix 后端和 JavaScript 前端，使用链接的 Sentry 项目可以启用**分布式跟踪**——跨越浏览器、Phoenix HTTP 服务器和下游服务的单个跟踪视图。

---

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| 事件未出现 | 验证 `SENTRY_DSN` 是否已设置；运行 `mix sentry.send_test_event`；设置 `log_level: :debug` |
| 捕获的异常缺少堆栈跟踪 | 在 `rescue` 块中传递 `stacktrace: __STACKTRACE__`：`Sentry.capture_exception(e, stacktrace: __STACKTRACE__)` |
| `PlugCapture` 在 Bandit 中不起作用 | `Sentry.PlugCapture` 仅适用于 Cowdy；在 Bandit 中错误通过 `LoggerHandler` 显示 |
| 生产中缺少源代码上下文 | 在构建 OTP 发布之前运行 `mix sentry.package_source_code` |
| 异步事件未出现上下文 | `Sentry.Context.*` 是进程范围的；显式传递值或跨进程传递 Logger 元数据 |
| Oban 集成未报告定时任务 | 需要 Oban v2.17.6+ 或 Oban Pro；定时任务必须在任务元数据中具有 `"cron" => true` |
| Cowboy/Bandit 崩溃的重复事件 | 在 `LoggerHandler` 配置中设置 `excluded_domains: [:cowboy, :bandit]`（两者自 v13.1.0 起默认排除） |
| `finch` 未启动 | 确保 `{:finch, "~> 0.21"}` 在依赖中；Finch 是自 v12.0.0 起的默认 HTTP 客户端 |
| JSON 编码错误 | 添加 `{:jason, "~> 1.4"}` 并设置 `json_library: Jason` 对于 Elixir < 1.18 |
