---
name: wp-phpstan
description: 在配置、运行或修复 WordPress 项目（插件/主题/站点）中的 PHPStan 静态分析时使用：phpstan.neon 设置、基线、WordPress 特定类型定义以及处理第三方插件类。
---

# WP PHPStan

## 使用场景

在 WordPress 代码库中使用 PHPStan 时，可以使用此技能，例如：

- 设置或更新 `phpstan.neon` / `phpstan.neon.dist`
- 生成或更新 `phpstan-baseline.neon`
- 通过 WordPress 友好的 PHPDoc 修复 PHPStan 错误（REST 请求、钩子、查询结果）
- 安全处理第三方插件/主题类（stubs/autoload/targeted 忽略）

## 需要的输入

- `wp-project-triage` 输出（如果没有运行，请先运行）
- 是否允许添加/更新 Composer 开发依赖（stubs）
- 是否允许为此任务更改基线。

## 步骤

### 0) 发现 PHPStan 入口点（确定性）
1. 检查 PHPStan 设置（配置、基线、脚本）：
   - `node skills/wp-phpstan/scripts/phpstan_inspect.mjs`

当存在时，优先使用仓库现有的 `composer` 脚本（例如 `composer run phpstan`）。

### 1) 确保 WordPress 核心 stubs 已加载

`szepeviktor/phpstan-wordpress` 或 `php-stubs/wordpress-stubs` 对大多数 WordPress 插件/主题仓库来说是必需的。没有它，预期会有一大批关于未知 WordPress 核心 函数的错误。

- 确认已安装该包（参见检查报告中的 `composer.dependencies`）。
- 确保 PHPStan 配置引用了 stubs（参见 `references/third-party-classes.md`）。

### 2) 确保 WordPress 项目的 `phpstan.neon` 合理

- 保持 `paths` 聚焦于第一方代码（插件/主题目录）。
- 排除生成代码和托管的代码（`vendor/`、`node_modules/`、构建工件、测试除非明确分析）。
- 保持 `ignoreErrors` 条目狭窄并记录。

参见：
- `references/configuration.md`

### 3) 使用 WordPress 特定的类型修复错误（首选）

优先于忽略错误来修正类型。常见的 WP 模式需要帮助：

- REST 端点：使用 `WP_REST_Request<...>` 类型化请求参数
- 钩子回调：为回调参数添加准确的 `@param` 类型
- 数据库结果和可迭代对象：使用数组形状或对象形状来表示查询结果
- Action Scheduler：为作业回调类型化 `$args` 数组形状

参见：
- `references/wordpress-annotations.md`

### 4) 处理第三方插件/主题类（仅在需要时）

当与不在分析环境中存在的插件/主题集成时：

- 首先，确认依赖是真实的（已安装/要求）。
- 优先使用仓库中已使用的特定插件 stubs（常见示例：`php-stubs/woocommerce-stubs`、`php-stubs/acf-pro-stubs`）。
- 如果 PHPStan 仍然无法解析类，为特定的供应商前缀添加目标 `ignoreErrors` 模式。

参见：
- `references/third-party-classes.md`

### 5) 基线管理（作为迁移工具，而不是垃圾桶）

- 对遗留代码生成一次基线，然后随着时间的推移减少它。
- 不要“基线化”新引入的错误。

参见：
- `references/configuration.md`

## 验证

- 使用发现的命令运行 PHPStan（`composer run ...` 或 `vendor/bin/phpstan analyse`）。
- 确认基线文件（如果使用）已包含且没有意外增长。
- 更改 `ignoreErrors` 后重新运行，以确保模式没有掩盖无关问题。

## 失败模式 / 调试

- “类未找到”：
  - 确认自动加载/stubs，或添加狭窄的忽略模式
- 启用 PHPStan 后错误数量巨大：
  - 减少 `paths`，添加 `excludePaths`，从较低级别开始，然后逐步提高
- 钩子/REST 参数周围的类型不一致：
  - 添加明确的 PHPDoc（参见参考资料）而不是运行时守卫

## 升级

- 如果一个类型依赖于您无法确认的第三方插件 API，请在发明类型之前请求依赖版本或来源。
- 如果修复需要添加新的 Composer 依赖（stubs/扩展），请先与用户确认。
