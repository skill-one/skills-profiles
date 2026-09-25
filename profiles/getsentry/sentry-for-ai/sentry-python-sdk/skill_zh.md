> [所有技能](../../SKILL_TREE.md) > [SDK 安装](../sentry-sdk-setup/SKILL.md) > Python SDK

# Sentry Python SDK

一个有主见的向导，它会扫描您的 Python 项目并指导您完成完整的 Sentry 设置。

## 在何时调用此技能

- 用户询问在 Python 应用中“添加 Sentry”或“设置 Sentry”
- 用户希望在 Python 中进行错误监控、跟踪、分析、日志记录、指标或定时任务
- 用户提到 `sentry-sdk`、`sentry_sdk` 或 Sentry + 任何 Python 框架
- 用户希望监控 Django 视图、Flask 路由、FastAPI 端点、Celery 任务或计划任务

> **注意：** 以下 SDK 版本和 API 反映了编写本文时 Sentry 文档的状态（sentry-sdk 2.x）。
> 在实施之前，请始终参考 [docs.sentry.io/platforms/python/](https://docs.sentry.io/platforms/python/) 进行验证。

---

## 第一阶段：检测

在提供建议之前，运行这些命令以了解项目：

```bash
# 检查现有的 Sentry
grep -i sentry requirements.txt pyproject.toml setup.cfg setup.py 2>/dev/null

# 检测 Web 框架
grep -rE "django|flask|fastapi|starlette|aiohttp|tornado|quart|falcon|sanic|bottle|pyramid" \
  requirements.txt pyproject.toml 2>/dev/null

# 检测任务队列
grep -rE "celery|rq|huey|arq|dramatiq" requirements.txt pyproject.toml 2>/dev/null

# 检测日志库
grep -E "loguru" requirements.txt pyproject.toml 2>/dev/null

# 检测 AI 库
grep -rE "openai|anthropic|langchain|huggingface|google-genai|pydantic-ai|litellm" \
  requirements.txt pyproject.toml 2>/dev/null

# 检测调度器 / 定时任务
grep -rE "celery|apscheduler|schedule|crontab" requirements.txt pyproject.toml 2>/dev/null

# OpenTelemetry 跟踪 — 检查 SDK + 仪器化
grep -rE "opentelemetry-sdk|opentelemetry-instrumentation|opentelemetry-distro" \
  requirements.txt pyproject.toml 2>/dev/null
grep -rn "TracerProvider\|trace\.get_tracer\|start_as_current_span" \
  --include="*.py" 2>/dev/null | head -5

# 检查配套前端
ls frontend/ web/ client/ ui/ static/ templates/ 2>/dev/null
```

**需要注意的事项：**
- `sentry-sdk` 是否已经在 `requirements` 中？如果是，请检查是否存在 `sentry_sdk.init()` — 可能只需要配置功能。
- 哪个框架？（决定在哪里放置 `sentry_sdk.init()`。）
- 哪个任务队列？（Celery 需要双进程初始化；RQ 需要一个设置文件。）
- AI 库？（OpenAI、Anthropic、LangChain 会自动仪器化。）
- OpenTelemetry 跟踪？（使用 OTLP 路径而不是原生跟踪。）
- 配套前端？（触发第四阶段跨链接。）

---

## 第二阶段：建议

根据您的发现，提出具体的建议。不要提出开放式问题 — 直接给出建议：

**从 OTel 检测的路线：**
- **检测到 OTel 跟踪**（`requirements` 中存在 `opentelemetry-sdk` / `opentelemetry-distro`，或在源代码中存在 `TracerProvider`）→ 使用 OTLP 路径：`OTLPIntegration()`；**不要**设置 `traces_sample_rate`；Sentry 会自动将错误链接到 OTel 跟踪

**始终推荐（核心覆盖）：**
- ✅ **错误监控** — 捕获未处理的异常，支持 `ExceptionGroup`（Python 3.11+）
- ✅ **日志记录** — Python `logging` 标准库自动捕获；如果检测到 Loguru 则会增强

**检测到时推荐：**
- ✅ **跟踪** — 检测到 HTTP 框架（Django/Flask/FastAPI 等）
- ✅ **AI 监控** — 检测到 OpenAI/Anthropic/LangChain 等（自动仪器化，无需配置）
- ⚡ **分析** — 对性能重要的生产应用；**不适用于 OTLP 路径**
- ⚡ **定时任务** — 检测到 Celery Beat、APScheduler 或 cron 模式
- ⚡ **指标** — 业务 KPI、SLO 追踪

**建议矩阵：**

| 功能 | 检测到时推荐... | 参考 |
|------|----------------|------|
| 错误监控 | **始终** — 不可协商的基线 | `${SKILL_ROOT}/references/error-monitoring.md` |
| OTLP 集成 | 检测到 OTel 跟踪 — **替换** 原生跟踪 | `${SKILL_ROOT}/references/tracing.md` |
| 跟踪 | 检测到 Django/Flask/FastAPI/AIOHTTP 等；**如果检测到 OTel 跟踪则跳过** | `${SKILL_ROOT}/references/tracing.md` |
| 分析 | 生产 + 性能敏感的工作负载；**如果检测到 OTel 跟踪则跳过**（需要 `traces_sample_rate`，与 OTLP 不兼容） | `${SKILL_ROOT}/references/profiling.md` |
| 日志记录 | **始终**（标准库）；Loguru 会增强 | `${SKILL_ROOT}/references/logging.md` |
| 指标 | 需要业务事件或 SLO 追踪 | `${SKILL_ROOT}/references/metrics.md` |
| 定时任务 | Celery Beat、APScheduler 或 cron 模式 | `${SKILL_ROOT}/references/crons.md` |
| AI 监控 | 检测到 AI 库 | `${SKILL_ROOT}/references/ai-monitoring.md` |

**检测到 OTel 跟踪：***"我在项目中看到 OpenTelemetry 跟踪。我建议 Sentry 的 OTLP 集成用于跟踪（通过您现有的 OTel 设置）+ 错误监控 + Sentry 日志记录[如果适用，可添加指标/定时任务/AI 监控]。要继续吗？"*

**未检测到 OTel：***"我建议错误监控 + 跟踪[如果适用，可添加日志记录]。还需要分析、定时任务或 AI 监控吗？"*

---

## 第三阶段：指导

### 安装

```bash
# 核心 SDK（始终需要）
pip install sentry-sdk

# 可选扩展（仅安装与检测到的框架匹配的扩展）：
pip install "sentry-sdk[django]"
pip install "sentry-sdk[flask]"
pip install "sentry-sdk[fastapi]"
pip install "sentry-sdk[celery]"
pip install "sentry-sdk[aiohttp]"
pip install "sentry-sdk[tornado]"

# 多个扩展：
pip install "sentry-sdk[django,celery]"
```

> 扩展是可选的 — 纯 `sentry-sdk` 对所有框架都有效。扩展会安装互补的包。

### 快速入门 — 推荐初始化

启用最多功能并使用合理默认值的完整初始化。在任何应用/框架代码**之前**放置：

```python
import sentry_sdk

sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN"],
    environment=os.environ.get("SENTRY_ENVIRONMENT", "production"),
    release=os.environ.get("SENTRY_RELEASE"),   # 例如 "myapp@1.0.0"
    send_default_pii=True,

    # 跟踪（在高流量生产环境中将 `traces_sample_rate` 降至 0.1–0.2）
    traces_sample_rate=1.0,

    # 分析 — 持续的，与活动跨度绑定
    profile_session_sample_rate=1.0,
    profile_lifecycle="trace",

    # 结构化日志（SDK ≥ 2.35.0）
    enable_logs=True,
)
```

### 每个框架的初始化位置

| 框架 | 调用 `sentry_sdk.init()` 的位置 | 备注 |
|------|--------------------------------|------|
| **Django** | `settings.py` 的顶部，任何导入之前 | 无需中间件 — Sentry 内部会修补 Django |
| **Flask** | 在 `app = Flask(__name__)` 之前 | 必须在应用创建之前 |
| **FastAPI** | 在 `app = FastAPI()` 之前 | `StarletteIntegration` + `FastApiIntegration` 会自动启用 |
| **Starlette** | 在 `app = Starlette(...)` 之前 | 与 FastAPI 相同的自动集成 |
| **AIOHTTP** | 模块级别，在 `web.Application()` 之前 | |
| **Tornado** | 模块级别，在应用设置之前 | 无需集成类 |
| **Quart** | 在 `app = Quart(__name__)` 之前 | |
| **Falcon** | 模块级别，在 `app = falcon.App()` 之前 | |
| **Pyramid** | 模块级别，在 `config = Configurator()` 之前 | WSGI 框架 |
| **Sanic** | 在 `@app.listener("before_server_start")` 内部 | Sanic 的生命周期需要异步初始化 |
| **Celery** | 在 worker 中通过 `@signals.celeryd_init.connect` 调用，并在调用进程中也调用 | 需要双进程初始化 |
| **RQ** | 通过 `rq worker -c mysettings` 加载的 `mysettings.py` | |
| **ARQ** | 工作模块和入队进程中都检测到 | |

**Django 示例**（`settings.py`）:
```python
import sentry_sdk

sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN"],
    send_default_pii=True,
    traces_sample_rate=1.0,
    profile_session_sample_rate=1.0,
    profile_lifecycle="trace",
    enable_logs=True,
)

# 剩余的 Django 设置...
INSTALLED_APPS = [...]
```

**FastAPI 示例**（`main.py`）:
```python
import sentry_sdk

sentry_sdk.init(
    dsn=os.environ["SENTRY_DSN"],
    send_default_pii=True,
    traces_sample_rate=1.0,
    profile_session_sample_rate=1.0,
    profile_lifecycle="trace",
    enable_logs=True,
)

from fastapi import FastAPI
app = FastAPI()
```

### 自动启用与显式集成

大多数集成在其包安装时自动激活 — 无需 `integrations=[...]`：

| 自动启用 | 需要显式设置 |
|---------|--------------|
| Django, Flask, FastAPI, Starlette, AIOHTTP, Tornado, Quart, Falcon, Pyramid, Sanic, Bottle | `DramatiqIntegration` |
| Celery, RQ, Huey, ARQ | `GRPCIntegration` |
| SQLAlchemy, Redis, asyncpg, pymongo | `StrawberryIntegration` |
| Requests, HTTPX, httpx2, aiohttp-client | `AsyncioIntegration` |
| OpenAI, Anthropic, LangChain, Pydantic AI, MCP | `OpenTelemetryIntegration` |
| Python `logging`, Loguru | `WSGIIntegration` / `ASGIIntegration` |

### 每个已同意的功能

逐个功能进行操作。加载参考文件，按照其步骤操作，验证后再继续：

| 功能 | 参考文件 | 加载时... |
|------|----------|----------|
| 错误监控 | `${SKILL_ROOT}/references/error-monitoring.md` | 始终（基线） |
| 跟踪 | `${SKILL_ROOT}/references/tracing.md` | HTTP 处理器 / 分布式跟踪 |
| 分析 | `${SKILL_ROOT}/references/profiling.md` | 性能敏感的生产环境 |
| 日志记录 | `${SKILL_ROOT}/references/logging.md` | 始终；Loguru 会增强 |
| 指标 | `${SKILL_ROOT}/references/metrics.md` | 业务事件 / SLO 追踪 |
| 定时任务 | `${SKILL_ROOT}/references/crons.md` | 调度器 / cron 模式检测到 |
| AI 监控 | `${SKILL_ROOT}/references/ai-monitoring.md` | 检测到 AI 库 |

对于每个功能：`读取 ${SKILL_ROOT}/references/<功能>.md`，精确跟随步骤，验证其是否正常工作。

---

## 配置参考

### `sentry_sdk.init()` 的关键选项

| 选项 | 类型 | 默认值 | 目的 |
|------|------|--------|------|
| `dsn` | `str` | `None` | 如果为空则禁用 SDK；环境变量：`SENTRY_DSN` |
| `environment` | `str` | `"production"` | 例如 `"staging"`；环境变量：`SENTRY_ENVIRONMENT` |
| `release` | `str` | `None` | 例如 `"myapp@1.0.0"`；环境变量：`SENTRY_RELEASE` |
| `send_default_pii` | `bool` | `False` | 包括 IP、头部、Cookie、认证用户、查询字符串（ASGI 框架） |
| `traces_sample_rate` | `float` | `None` | 事务采样率；`None` 会禁用跟踪 |
| `traces_sampler` | `Callable` | `None` | 自定义每笔交易的采样（覆盖率） |
| `profile_session_sample_rate` | `float` | `None` | 持续分析会话率 |
| `profile_lifecycle` | `str` | `"manual"` | `"trace"` = 自动启动与跨度绑定的分析器 |
| `profiles_sample_rate` | `float` | `None` | 事务级分析率 |
| `enable_logs` | `bool` | `False` | 将日志发送到 Sentry（SDK ≥ 2.35.0） |
| `sample_rate` | `float` | `1.0` | 错误事件采样率 |
| `attach_stacktrace` | `bool` | `False` | 在 `capture_message()` 上附加堆栈跟踪 |
| `max_breadcrumbs` | `int` | `100` | 每个事件的最大面包屑数 |
| `debug` | `bool` | `False` | SDK 详细调试输出 |
| `before_send` | `Callable` | `None` | 用于修改/丢弃错误事件的钩子 |
| `before_send_transaction` | `Callable` | `None` | 用于修改/丢弃事务事件的钩子 |
| `ignore_errors` | `list` | `[]` | 要抑制的异常类型或正则表达式模式 |
| `auto_enabling_integrations` | `bool` | `True` | 设置为 `False` 以禁用所有自动检测 |

#### `OTLPIntegration` 选项（传递给构造函数）

| 选项 | 类型 | 默认值 | 目的 |
|------|------|--------|------|
| `setup_otlp_traces_exporter` | `bool` | `True` | 自动配置 OTLP 导出器；如果您发送到自己的 Collector，则设置为 `False` |
| `collector_url` | `str` | `None` | OTel Collector 的 OTLP HTTP 端点（例如 `http://localhost:4318/v1/traces`）；设置后，跨度会发送到 Collector 而不是直接发送到 Sentry |
| `setup_propagator` | `bool` | `True` | 自动配置 Sentry 传播器以进行分布式跟踪 |
| `capture_exceptions` | `bool` | `False` | 拦截通过 OTel `Span.record_exception` 记录的异常 |

### 环境变量

| 变量 | 映射到 | 备注 |
|------|--------|------|
| `SENTRY_DSN` | `dsn` | |
| `SENTRY_RELEASE` | `release` | 还会自动检测 git SHA、Heroku、CircleCI、CodeBuild、GAE |
| `SENTRY_ENVIRONMENT` | `environment` | |
| `SENTRY_DEBUG` | `debug` | |

---

## 验证

测试 Sentry 是否正在接收事件：

```python
# 触发一个真实的错误事件 — 几秒钟内在控制台查看
division_by_zero = 1 / 0
```

或用于非崩溃检查：
```python
sentry_sdk.capture_message("Sentry Python SDK 测试")
```

如果没有任何内容出现：
1. 在 `sentry_sdk.init()` 中设置 `debug=True` — 将 SDK 内部信息打印到 stdout
2. 验证 DSN 是否正确
3. 检查运行进程中的 `SENTRY_DSN` 环境变量是否已设置
4. 对于 Celery/RQ：确保在 **worker** 进程中初始化，而不仅仅是调用进程

---

## 第四阶段：跨链接

完成 Python 设置后，检查是否有缺少 Sentry 的配套前端：

```bash
ls frontend/ web/ client/ ui/ 2>/dev/null
cat frontend/package.json web/package.json client/package.json 2>/dev/null \
  | grep -E '"react"|"svelte"|"vue"|"next"|"nuxt"'
```

如果存在没有 Sentry 的前端，建议匹配的技能：

| 前端检测到 | 建议技能 |
|------------|----------|
| React / Next.js | `sentry-react-sdk` |
| Svelte / SvelteKit | `sentry-svelte-sdk` |
| Vue / Nuxt | 使用 `@sentry/vue` — 参考 [docs.sentry.io/platforms/javascript/guides/vue/](https://docs.sentry.io/platforms/javascript/guides/vue/) |
| 其他 JS/TS | `sentry-react-sdk`（涵盖通用浏览器 JS 模式） |

---

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| 事件未出现 | 设置 `debug=True`，验证 DSN，检查运行进程中的环境变量 |
| DSN 格式错误 | 格式：`https://<key>@o<org>.ingest.sentry.io/<project>` |
| Django 异常未捕获 | 确保 `sentry_sdk.init()` 在 `settings.py` 的**顶部**，在导入其他内容之前 |
| Flask 异常未捕获 | 初始化必须发生在 `app = Flask(__name__)` 之前 |
| FastAPI 异常未捕获 | 初始化在 `app = FastAPI()` 之前；`StarletteIntegration` 和 `FastApiIntegration` 会自动启用 |
| ASGI 链接异常被抑制 | 默认情况下，Sentry 的 ASGI 中间件会剥离异常链（`raise exc from None`）。要保留链接异常，请在 `sentry_sdk.init()` 中设置 `_experiments={"suppress_asgi_chained_exceptions": False}` |
| Celery 任务错误未捕获 | 必须在 worker 进程中通过 `celeryd_init` 信号调用 `sentry_sdk.init()` |
| Sanic 初始化不工作 | 初始化必须在 `@app.listener("before_server_start")` 内部，而不是模块级别 |
| uWSGI 未捕获 | 在 uWSGI 命令中添加 `--enable-threads --py-call-uwsgi-fork-hooks` |
| 未出现跟踪（原生） | 验证 `traces_sample_rate` 已设置（不能为 `None`）；检查集成是否已自动启用 |
| 未出现跟踪（OTLP） | 验证已安装 `sentry-sdk[opentelemetry-otlp]`；在使用 `OTLPIntegration` 时**不要**设置 `traces_sample_rate` |
| 分析未启动 | 需要 `traces_sample_rate > 0` + `profile_session_sample_rate` 或 `profiles_sample_rate`；**与 OTLP 路径不兼容** |
| `enable_logs` 未工作 | 需要 SDK ≥ 2.35.0；直接结构化日志使用 `sentry_sdk.logger`；标准库桥接使用 `LoggingIntegration(sentry_logs_level=...)` |
| 事务过多 | 降低 `traces_sample_rate` 或使用 `traces_sampler` 来丢弃健康检查 |
| 跨请求数据泄露 | 不要使用 `get_global_scope()` 进行每个请求的数据 — 使用 `get_isolation_scope()` |
| 查询字符串未捕获（ASGI） | ASGI 框架（FastAPI、Starlette 等）中的查询字符串和客户端 IP 需要 `send_default_pii=True` |
| RQ 工作器未报告 | 将 `--sentry-dsn=""` 传递给 RQ 以禁用 RQ 自身的 Sentry 快捷方式；通过设置文件进行初始化 |
