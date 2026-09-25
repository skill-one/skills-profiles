# WP 能力 API

## 使用场景

当任务涉及以下情况时，使用此技能：

- 在 PHP 中注册能力或能力类别，
- 通过 REST (`wp-abilities/v1`) 向客户端暴露能力，
- 在 JS 中使用能力（特别是 `@wordpress/abilities`），
- 诊断“能力未显示” / “客户端看不到能力” / “REST 返回空”。

## 所需输入

- 仓库根目录（如果尚未运行，请先运行 `wp-project-triage`）。
- 目标 WordPress 版本以及这是 WP 核心 还是插件/主题。
- 变更应放置的位置（插件 vs 主题 vs mu 插件）。

## 操作步骤

在决定要注册什么之前，请阅读 `references/domain-vs-projection.md` — 能力位于领域能力层；MCP / 命令面板 / REST 暴露是一个投影。注册形状和暴露形状是不同的决定，将它们混淆会导致每次消费者约束条件更改时都需要重新注册。

### 1) 确认可用性和版本约束

- 如果这是 WP 核心工作，请检查 `signals.isWpCoreCheckout` 和 `versions.wordpress.core`。
- 如果项目目标是 WP < 6.9，您可能需要 Abilities API 插件/包，而不是依赖核心。

### 2) 查找现有的能力使用

在仓库中搜索以下内容：

- `wp_register_ability(`
- `wp_register_ability_category(`
- `wp_abilities_api_init`
- `wp_abilities_api_categories_init`
- `wp-abilities/v1`
- `@wordpress/abilities`

如果没有找到，请决定您是全新引入 Abilities API（新的注册 + 客户端使用）还是仅使用。

### 3) 注册类别（可选）

如果您需要逻辑分组，请尽早注册一个能力类别（见 `references/php-registration.md`）。

### 4) 注册能力（PHP）

对于分组决策（要注册多少能力，以及在哪里放置过滤器 vs. 新的能力名称），请先阅读 `references/grouping-heuristic.md` — 它可以防止您为每个 REST 操作发送一个原子能力。

为了避免能力与现有 UI / REST 代码路径之间的差异，请参阅 `references/shared-core-service.md` — 能力、REST 处理程序、CLI 命令和 UI 控制器应该是共享服务的薄适配器。参考也涵盖了指标陷阱（发出使用遥测的 REST 处理程序）和 `AGENTS.md` 规则，用于在底层代码路径更改时保持注册同步。

对于多个执行回调委托给现有 REST 控制器的共享辅助模式，请参阅 `references/plugin-family-patterns.md`（识别共享-API-客户端 vs 零参数控制器形状）和 `references/delegate-helper-pattern.md`（一个有效的辅助形状，以及何时不使用它）。

对于标准化的 `WP_Error` 代码，允许代理推理重试 vs. 升级，请参阅 `references/error-code-vocabulary.md`。

使用 PHP 注册实现能力：

- 稳定的 `id`（命名空间），
- `label`/`description`，
- `category`，
- `meta`:
  - 当能力是信息性时，添加 `readonly: true`，
  - 为您希望客户端可见的能力设置 `show_in_rest: true`。

使用文档中记录的 Abilities API 注册初始化钩子，以便它们在正确的时间加载（见 `references/php-registration.md`）。

### 5) 确认 REST 暴露

- 验证 REST 端点存在并返回预期结果（见 `references/rest-api.md`）。
- 如果客户端仍然看不到能力，请确认 `meta.show_in_rest` 已启用，并且您正在查询正确的端点。

### 6) 从 JS 消费（如果需要）

- 优先使用 `@wordpress/abilities` API 进行客户端访问和检查。
- 确保构建工具包含依赖项，并且项目构建管道将其捆绑。

## 验证

- `wp-project-triage` 在您的更改后指示 `signals.usesAbilitiesApi: true`（如果适用）。
- REST 检查（在 WP 环境中）：`wp-abilities/v1` 下端点在预期时返回您的能力和类别。
- 如果仓库有测试，请在附近添加/更新覆盖率：
  - PHP：能力注册和元暴露
  - JS：能力消费和 UI 网关

## 失败模式 / 调试

- 能力从未出现：
  - 注册代码未运行（错误的钩子 / 文件未加载），
  - 缺少 `meta.show_in_rest`，
  - 类别/ID 不匹配不正确。
- REST 显示能力但 JS 不显示：
  - 错误的 REST 基/命名空间，
  - JS 依赖项未捆绑，
  - 缓存（对象/页面缓存）掩盖了更改。
- 执行回调返回意外的错误或静默忽略输入：
  - `input_schema` 默认值未应用，能力与底层之间的分页键漂移，或基于 `empty()` 的 ID 验证 — 见 `references/input-schema-gotchas.md`。

## 升级

- 如果您不确定版本支持，请确认目标 WP 核心版本，以及 Abilities API 是预期来自核心还是作为插件。
- 对于规范细节，请参阅：
  - `references/rest-api.md`
  - `references/php-registration.md`
