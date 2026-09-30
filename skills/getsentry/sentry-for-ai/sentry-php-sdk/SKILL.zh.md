---
name: sentry-php-sdk
description: PHP的完整Sentry SDK设置。当被要求“将Sentry添加到PHP”、“安装sentry/sentry”、“在PHP中设置Sentry”或为PHP应用程序配置错误监控、跟踪、分析、日志记录、指标、计划任务或AI监控时使用。支持纯PHP、Laravel和Symfony。
---

> [所有技能](../../SKILL_TREE.md) > [SDK 设置](../sentry-sdk-setup/SKILL.md) > PHP SDK

# Sentry PHP SDK

一个有倾向性的向导，它会扫描您的 PHP 项目并指导您完成完整的 Sentry 设置。

## 在以下情况下调用此技能

- 用户询问在 PHP 应用中“添加 Sentry”或“设置 Sentry”
- 用户希望在 PHP 中进行错误监控、跟踪、分析、日志记录、指标或计划任务
- 用户提到 `sentry/sentry`、`sentry/sentry-laravel`、`sentry/sentry-symfony` 或 Sentry + 任何 PHP 框架
- 用户希望监控 Laravel 路由、Symfony 控制器、队列、计划任务或纯 PHP 脚本

> **注意：** 以下 SDK 版本和 API 反映了编写时 Sentry 文档的状态（sentry/sentry 4.x、sentry/sentry-laravel 4.x、sentry/sentry-symfony 5.x）。
> 在实施之前，请始终参考 [docs.sentry.io/platforms/php/](https://docs.sentry.io/platforms/php/) 进行验证。

---

## 第一阶段：检测

在提出建议之前，运行这些命令以了解项目：

```bash
# 检查现有的 Sentry
grep -i sentry composer.json composer.lock 2>/dev/null

# 检测框架
cat composer.json | grep -E '"laravel/framework"|"symfony/framework-bundle"|"illuminate/'

# 通过文件系统标记确认框架
ls artisan 2>/dev/null && echo "检测到 Laravel"
ls bin/console 2>/dev/null && echo "检测到 Symfony"

# 检测队列系统
grep -E '"laravel/horizon"|"symfony/messenger"' composer.json 2>/dev/null

# 检测 AI 库
grep -E '"(laravel/ai|openai-php|openai/|anthropic|llm)' composer.json 2>/dev/null

# 检查配套前端
ls frontend/ resources/js/ assets/ 2>/dev/null
cat package.json 2>/dev/null | grep -E '"react"|"svelte"|"vue"|"next"'
```

**需要注意的事项：**
- `sentry/sentry`（或 `-laravel` / `-symfony`）是否已经在 `composer.json` 中？如果是，请检查是否存在初始化调用——可能只需要功能配置。
- 检测到框架？**Laravel**（在 composer.json 中有 `artisan` + `laravel/framework`）、**Symfony**（在 composer.json 中有 `bin/console` + `symfony/framework-bundle`）或**纯 PHP**。
- 队列系统？（Laravel Queue / Horizon、Symfony Messenger 需要队列工作器配置。）
- AI 库？（`laravel/ai` 在启用跟踪时由 `sentry/sentry-laravel >= 4.27.0` 自动仪器化；其他 PHP AI 库需要手动跨度。）
- 配套前端？（触发第四阶段跨链接。）

---

## 第二阶段：建议

根据您的发现，提出一个具体的建议。不要提出开放式问题——直接给出建议：

**始终推荐（核心覆盖）：**
- ✅ **错误监控**——捕获未处理的异常和 PHP 错误
- ✅ **日志记录**——Monolog 集成（Laravel/Symfony 自动配置；纯 PHP 使用 `MonologHandler`）

**检测到时推荐：**
- ✅ **跟踪**——检测到 Web 框架（Laravel/Symfony 自动仪器化 HTTP、数据库、Twig/Blade、缓存）
- ⚡ **分析**——性能重要的生产应用（需要 `excimer` PHP 扩展，仅限 Linux/macOS）
- ⚡ **计划任务**——检测到调度器模式（Laravel Scheduler、Symfony Scheduler、自定义 cron 任务）
- ⚡ **指标**——业务 KPI 或 SLO 跟踪（使用 `TraceMetrics` API）
- ✅ **AI 监控**——在 Laravel 应用中检测到 `laravel/ai`（在 `sentry/sentry-laravel >= 4.27.0` 中自动仪器化）

**建议矩阵：**

| 功能 | 在以下情况下建议 | 参考 |
|------|------------------|-------|
| 错误监控 | **始终**——非谈判的基线 | `${SKILL_ROOT}/references/error-monitoring.md` |
| 跟踪 | 检测到 Laravel/Symfony，或需要手动跨度 | `${SKILL_ROOT}/references/tracing.md` |
| 分析 | 生产 + `excimer` 扩展可用 | `${SKILL_ROOT}/references/profiling.md` |
| 日志记录 | **始终**；Monolog 用于 Laravel/Symfony | `${SKILL_ROOT}/references/logging.md` |
| 指标 | 需要业务事件或 SLO 跟踪 | `${SKILL_ROOT}/references/metrics.md` |
| 计划任务 | 检测到调度器或 cron 模式 | `${SKILL_ROOT}/references/crons.md` |
| AI 监控 | 在 Laravel 应用中检测到 `laravel/ai`，或需要手动 PHP AI 跨度 | `${SKILL_ROOT}/references/ai-monitoring.md` |

建议："我建议 Error Monitoring + Tracing [+ Logging]。还需要 Profiling、Crons、Metrics 或 AI Monitoring 吗？"

---

## 第三阶段：指导

### 安装

```bash
# 纯 PHP
composer require sentry/sentry "^4.0"

# Laravel
composer require sentry/sentry-laravel "^4.0"

# Laravel 带 Laravel AI 监控
composer require sentry/sentry-laravel "^4.27.0"

# Symfony
composer require sentry/sentry-symfony "^5.0"
```

**系统要求：**
- PHP 7.2 或更高版本
- 扩展：`ext-json`、`ext-mbstring`、`ext-curl`（所有必需）
- `excimer` PECL 扩展（Linux/macOS 仅限——分析需要）

### 框架特定初始化

#### 纯 PHP

在入口点的顶部（`index.php`、`bootstrap.php` 或等效文件）放置 `\Sentry\init()`，在任何应用程序代码之前：

```php
<?php

require_once 'vendor/autoload.php';

\Sentry\init([
    'dsn'                  => $_SERVER['SENTRY_DSN'] ?? '',
    'environment'          => $_SERVER['SENTRY_ENVIRONMENT'] ?? 'production',
    'release'              => $_SERVER['SENTRY_RELEASE'] ?? null,
    'send_default_pii'     => true,
    'traces_sample_rate'   => 1.0,
    'profiles_sample_rate' => 1.0,
    'enable_logs'          => true,
]);

// 应用其余部分...
```

#### Laravel

**步骤 1 — 注册异常处理器** 在 `bootstrap/app.php` 中：

```php
use Sentry\Laravel\Integration;

return Application::configure(basePath: dirname(__DIR__))
    ->withExceptions(function (Exceptions $exceptions) {
        Integration::handles($exceptions);
    })->create();
```

**步骤 2 — 发布配置并设置 DSN：**

```bash
php artisan sentry:publish --dsn=YOUR_DSN
```

这将创建 `config/sentry.php` 并将 `SENTRY_LARAVEL_DSN` 添加到 `.env`。

**步骤 3 — 配置 `.env`：**

```ini
SENTRY_LARAVEL_DSN=https://examplePublicKey@o0.ingest.sentry.io/0
SENTRY_TRACES_SAMPLE_RATE=1.0
SENTRY_PROFILES_SAMPLE_RATE=1.0
```

> 对于完整的 Laravel 配置选项，请阅读 `${SKILL_ROOT}/references/laravel.md`。

#### Symfony

**步骤 1 — 注册捆绑包** 在 `config/bundles.php` 中（由 Symfony Flex 自动完成）：

```php
Sentry\SentryBundle\SentryBundle::class => ['all' => true],
```

**步骤 2 — 创建 `config/packages/sentry.yaml`：**

```yaml
sentry:
    dsn: '%env(SENTRY_DSN)%'
    options:
        environment: '%env(APP_ENV)%'
        release: '%env(SENTRY_RELEASE)%'
        send_default_pii: true
        traces_sample_rate: 1.0
        profiles_sample_rate: 1.0
        enable_logs: true
```

**步骤 3 — 在 `.env` 中设置 DSN：**

```ini
SENTRY_DSN=https://examplePublicKey@o0.ingest.sentry.io/0
```

> 对于完整的 Symfony 配置选项，请阅读 `${SKILL_ROOT}/references/symfony.md`。

### 快速入门——推荐初始化（纯 PHP）

启用最多功能并使用合理默认值的完整初始化：

```php
\Sentry\init([
    'dsn'                     => $_SERVER['SENTRY_DSN'] ?? '',
    'environment'             => $_SERVER['SENTRY_ENVIRONMENT'] ?? 'production',
    'release'                 => $_SERVER['SENTRY_RELEASE'] ?? null,
    'send_default_pii'        => true,

    // 跟踪（在高流量生产中降低到 0.1–0.2）
    'traces_sample_rate'      => 1.0,

    // 分析——需要 `excimer` 扩展（Linux/macOS 仅限）
    'profiles_sample_rate'    => 1.0,

    // 结构化日志（sentry/sentry >=4.12.0）
    'enable_logs'             => true,
]);
```

### 对于每个同意的功能

逐个通过功能。加载参考，按照其步骤操作，验证后再继续：

| 功能 | 参考文件 | 加载时... |
|------|----------|----------|
| 错误监控 | `${SKILL_ROOT}/references/error-monitoring.md` | 始终（基线） |
| 跟踪 | `${SKILL_ROOT}/references/tracing.md` | HTTP 处理程序 / 分布式跟踪 |
| 分析 | `${SKILL_ROOT}/references/profiling.md` | 性能敏感的生产环境 |
| 日志记录 | `${SKILL_ROOT}/references/logging.md` | 始终；Monolog 用于 Laravel/Symfony |
| 指标 | `${SKILL_ROOT}/references/metrics.md` | 业务 KPI / SLO 跟踪 |
| 计划任务 | `${SKILL_ROOT}/references/crons.md` | 调度器 / cron 模式检测 |
| AI 监控 | `${SKILL_ROOT}/references/ai-monitoring.md` | 在 Laravel 中检测到 `laravel/ai`，或需要手动 PHP AI 跨度 |

对于每个功能：`读取 ${SKILL_ROOT}/references/<功能>.md`，精确跟随步骤，验证其是否正常工作。

---

## 配置参考

### 关键 `\Sentry\init()` 选项（纯 PHP）

| 选项 | 类型 | 默认值 | 目的 |
|------|------|--------|------|
| `dsn` | `string\|bool\|null` | `$_SERVER['SENTRY_DSN']` | 如果为空或 `false`，则禁用 SDK |
| `environment` | `string\|null` | `$_SERVER['SENTRY_ENVIRONMENT']` | 例如，`"staging"` |
| `release` | `string\|null` | `$_SERVER['SENTRY_RELEASE']` | 例如，`"myapp@1.0.0"` |
| `send_default_pii` | `bool` | `false` | 包括请求头、Cookie、IP |
| `sample_rate` | `float` | `1.0` | 错误事件采样率（0.0–1.0） |
| `traces_sample_rate` | `float\|null` | `null` | 事务采样率；`null` 禁用跟踪 |
| `traces_sampler` | `callable\|null` | `null` | 自定义每个事务采样（覆盖率） |
| `profiles_sample_rate` | `float\|null` | `null` | 相对于跟踪的分析率；需要 `excimer` |
| `enable_logs` | `bool` | `false` | 将结构化日志发送到 Sentry（>=4.12.0） |
| `max_breadcrumbs` | `int` | `100` | 每个事件的最大面包屑 |
| `attach_stacktrace` | `bool` | `false` | 在 `captureMessage()` 上堆栈跟踪 |
| `in_app_include` | `string[]` | `[]` | 属于您应用的前缀路径 |
| `in_app_exclude` | `string[]` | `[]` | 第三方代码的路径前缀（在跟踪中隐藏） |
| `ignore_exceptions` | `string[]` | `[]` | 从不报告的异常 FQCN |
| `ignore_transactions` | `string[]` | `[]` | 从不报告的事务名称 |
| `error_types` | `int\|null` | `error_reporting()` | PHP 错误掩码（例如，`E_ALL & ~E_NOTICE`） |
| `capture_silenced_errors` | `bool` | `false` | 捕获由 `@` 操作符抑制的错误 |
| `max_request_body_size` | `string` | `"medium"` | `"none"` / `"small"` / `"medium"` / `"always"` |
| `before_send` | `callable` | identity | `fn(Event $event, ?EventHint $hint): ?Event` — 返回 `null` 以丢弃 |
| `before_breadcrumb` | `callable` | identity | `fn(Breadcrumb $b): ?Breadcrumb` — 返回 `null` 以丢弃 |
| `trace_propagation_targets` | `string[]\|null` | `null` | 要注入 `sentry-trace` 头的下游主机；`null` = 所有，`[]` = 无 |
| `strict_trace_continuation` | `bool` | `false` | 只有当传入的 `sentry-org_id` 负载与 SDK 的 org ID 匹配时才继续传入的分布式跟踪；防止第三方 Sentry 仪器化服务导致的跟踪污染（>=4.21.0） |
| `debug` | `bool` | `false` | SDK 详细输出（使用 PSR-3 `logger` 选项代替以获取结构化输出） |

### 环境变量

| 变量 | 映射到 | 备注 |
|------|--------|------|
| `SENTRY_DSN` | `dsn` | 也映射到 `$_SERVER['SENTRY_DSN']` |
| `SENTRY_ENVIRONMENT` | `environment` | |
| `SENTRY_RELEASE` | `release` | 也读取 `$_SERVER['AWS_LAMBDA_FUNCTION_VERSION']` |
| `SENTRY_SPOTLIGHT` | `spotlight` | |

> **Laravel 注意：** 使用 `SENTRY_LARAVEL_DSN`（回退到 `SENTRY_DSN`）。其他选项遵循 `SENTRY_TRACES_SAMPLE_RATE`、`SENTRY_PROFILES_SAMPLE_RATE` 等。

---

## 验证

测试 Sentry 是否接收事件：

```php
// 触发真实的错误事件——几秒钟内在 Sentry 仪表板中检查
throw new \Exception('Sentry PHP SDK 测试');
```

或用于非崩溃检查：

```php
\Sentry\captureMessage('Sentry PHP SDK 测试');
```

**Laravel:**
```bash
php artisan sentry:test
```

如果什么都没有出现：
1. 启用调试输出：
   ```php
   \Sentry\init([
       'dsn' => '...',
       'logger' => new \Sentry\Logger\DebugStdOutLogger(),
   ]);
   ```
2. 验证 DSN 是否正确（格式：`https://<key>@o<org>.ingest.sentry.io/<project>`）
3. 检查 `SENTRY_DSN`（或 `SENTRY_LARAVEL_DSN`）在运行进程中的环境变量是否已设置
4. 对于队列工作器：确保 Sentry 在**工作器进程**中初始化，而不仅仅是 Web 进程

---

## 第四阶段：跨链接

完成 PHP 设置后，检查是否有缺少 Sentry 的配套前端：

```bash
ls frontend/ resources/js/ assets/ public/ 2>/dev/null
cat package.json frontend/package.json 2>/dev/null \
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
| 事件未出现 | 启用 `logger` 选项 (`DebugStdOutLogger`)，验证 DSN，检查运行进程中的环境变量 |
| Malformed DSN 错误 | 格式：`https://<key>@o<org>.ingest.sentry.io/<project>` |
| Laravel 异常未捕获 | 确保 `Integration::handles($exceptions)` 在 `bootstrap/app.php` 中 |
| Symfony 异常未捕获 | 验证 `SentryBundle` 是否在 `config/bundles.php` 中注册 |
| 未出现跟踪 | 设置 `traces_sample_rate`（不为 `null`）；确认自动仪器化已启用 |
| 分析未工作 | 需要 `excimer` 扩展（Linux/macOS 仅限；Windows 上不可用）；需要 `traces_sample_rate > 0` |
| `enable_logs` 未工作 | 需要 `sentry/sentry >= 4.12.0`、`sentry/sentry-laravel >= 4.15.0` 或 `sentry/sentry-symfony >= 5.4.0` |
| 队列工作器错误缺失 | 在工作器进程本身初始化 Sentry，而不仅仅是 Web 进程；对于 Laravel 使用工作器 `.env` 中的 `SENTRY_LARAVEL_DSN` |
| 事务过多 | 降低 `traces_sample_rate` 或使用 `traces_sampler` 放弃健康检查路由 |
| PII 未捕获 | 设置 `send_default_pii: true`；对于 Laravel 在 `config/sentry.php` 中设置 `send_default_pii: true` |
| `@` 抑制的错误未捕获 | 设置 `capture_silenced_errors: true` |
| 跨服务跟踪损坏 | 检查 `trace_propagation_targets`；确保下游服务已安装 Sentry |
| 来自第三方服务的跟踪污染 | 设置 `strict_trace_continuation: true` 以仅继续传入的 `sentry-org_id` 负载与您的 SDK 的 org ID 匹配的跟踪（>=4.21.0） |
