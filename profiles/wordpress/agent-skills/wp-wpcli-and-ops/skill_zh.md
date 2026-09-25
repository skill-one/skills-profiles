# WP-CLI 和运维

## 使用场景

当任务涉及通过 WP-CLI 进行的 WordPress 运维工作时应使用此技能，包括：

- `wp search-replace`（URL 变更、域名迁移、协议切换）
- 数据库导出/导入、重置和检查（`wp db *`）
- 插件/主题安装/激活/更新、语言包
- 定时任务列表/执行
- 缓存/重写清理
- 多站点操作（`wp site *`，`--url`，`--network`）
- 构建可重复使用的脚本（`wp-cli.yml`，shell 脚本，CI 任务）

## 所需输入

- WP-CLI 将运行的位置（本地开发、预发布、生产）以及是否安全运行。
- 如何定位正确的站点根目录：
  - `--path=<wordpress-root>` 以及（多站点）`--url=<site-url>`
- 是否为多站点以及命令是否应跨网络运行。
- 任何约束（无停机时间、无数据库写入、维护窗口）。

## 操作步骤

### 0) 安全措施：确认环境和影响范围

WP-CLI 命令可能具有破坏性。在执行任何写入操作之前：

1. 确认环境（开发/预发布/生产）。
2. 确认目标（路径/URL），以免误操作错误站点。
3. 在执行有风险的操作时进行备份。

阅读：

- `references/safety.md`

### 1) 检查 WP-CLI 和站点定位（确定性）

运行检查器：

- `node skills/wp-wpcli-and-ops/scripts/wpcli_inspect.mjs --path=<path> [--url=<url>]`

如果 WP-CLI 不可用，则通过项目的文档化工具（Composer、容器或系统包）进行安装，或请求预期的执行环境。

### 2) 选择正确的流程

#### A) 安全的 URL/域名迁移（`search-replace`）

遵循安全顺序：

1. `wp db export`（备份）
2. `wp search-replace --dry-run`（审查影响）
3. 使用适当的标志执行实际替换
4. 如有必要，清理缓存/重写

阅读：

- `references/search-replace.md`

#### B) 插件/主题操作

使用 `wp plugin *` / `wp theme *` 并首先确认是否在预期的站点（和网络）上操作。

阅读：

- `references/packages-and-updates.md`

#### C) 定时任务和队列

检查定时任务状态，并通过调试运行单个事件，而不是盲目地“运行所有事件”。

阅读：

- `references/cron-and-cache.md`

#### D) 多站点操作

多站点变更可能影响多个站点。始终决定是否在：

- 单个站点上操作（`--url=`），或
- 跨网络操作（`--network` / 迭代站点）

阅读：

- `references/multisite.md`

### 3) 自动化模式（脚本 + wp-cli.yml）

对于可重复的运维操作，优先选择：

- `wp-cli.yml` 用于默认设置（路径/URL、PHP 内存限制）
- 记录命令并在出错时停止的 shell 脚本
- 默认执行只读检查的 CI 任务

阅读：

- `references/automation.md`

## 验证

- 在可能影响定位或配置的变更后重新运行 `wpcli_inspect`。
- 确认预期的副作用：
  - 正确的 URL 已更新
  - 插件/主题处于预期状态
  - 在需要的地方清理了定时任务/缓存
- 如果有健康检查端点或冒烟测试套件，在运维变更后运行它。

## 失败模式 / 调试

- “错误：这看起来不是一个 WordPress 安装。”
  - 错误的 `--path`、错误的容器或缺少 `wp-config.php`
- 多站点命令影响错误站点
  - 缺少 `--url` 或错误的 URL
- `search-replace` 导致意外的序列化问题
  - 错误的标志或在不安全的情况下更改序列化数据

参见：

- `references/debugging.md`

## 升级

- 如果无法确认环境安全性，不要运行写入操作。
- 如果仓库使用容器化工具（Docker/wp-env）但无法访问，请求预期的命令运行器或 CI 任务。
