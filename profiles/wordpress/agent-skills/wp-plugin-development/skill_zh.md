# WordPress 插件开发

## 使用场景

用于插件开发工作，例如：

- 创建或重构插件结构（启动文件、包含文件、命名空间/类）
- 添加钩子/动作/过滤器
- 激活/停用/卸载行为和迁移
- 添加设置页面/选项/管理界面（设置 API）
- 安全修复（nonce、权限、清理/转义、SQL 安全性）
- 打包发布版本（构建产物、readme、资源文件）

## 所需输入

- 仓库根目录 + 目标插件（如果知道插件主文件路径）
- 插件运行环境：单站点 vs 多站点；如果适用，需遵循 WP.com 规范
- 目标 WordPress + PHP 版本（影响可用 API 和 `$wpdb->prepare()` 中的占位符支持）

## 操作步骤

### 0) 筛选并定位插件入口点

1. 运行筛选：
   - `node skills/wp-project-triage/scripts/detect_wp_project.mjs`
2. 检测插件头部（确定性扫描）：
   - `node skills/wp-plugin-development/scripts/detect_plugins.mjs`

如果这是一个完整站点的仓库，在修改代码前，需选择 `wp-content/plugins/` 或 `mu-plugins/` 下的特定插件。

### 1) 遵循可预测的架构

指南：

- 保持单个启动文件（带头部的插件主文件）
- 避免在文件加载时产生副作用；通过钩子加载
- 优先使用专门的加载器/类来注册钩子
- 将仅限管理员的代码放在 `is_admin()`（或管理钩子）之后，以减少前端开销

参考：
- `references/structure.md`

### 2) 钩子与生命周期（激活/停用/卸载）

激活钩子比较脆弱；需遵循约束：

- 在顶层注册激活/停用钩子，不要在其他钩子内部注册
- 仅在需要时刷新重写规则，且必须在注册 CPT/规则之后
- 卸载应明确且安全（`uninstall.php` 或 `register_uninstall_hook`）

参考：
- `references/lifecycle.md`

### 3) 设置和管理界面（设置 API）

优先使用设置 API 来处理选项：

- `register_setting()`、`add_settings_section()`、`add_settings_field()`
- 通过 `sanitize_callback` 进行清理

参考：
- `references/settings-api.md`

### 4) 安全基线（始终）

发布前：

- 早期验证/清理输入；晚期转义输出
- 使用 nonce 防止 CSRF *和* 权限检查授权
- 避免直接信任 `$_POST` / `$_GET`；使用 `wp_unslash()` 和特定键
- 使用 `$wpdb->prepare()` 处理 SQL；避免使用字符串拼接构建 SQL

参考：
- `references/security.md`

### 5) 数据存储、计划任务、迁移（如果需要）

- 小型配置优先使用选项；仅在必要时使用自定义表
- 对于计划任务，确保幂等性并提供手动执行路径（WP-CLI 或管理界面）
- 对于架构变更，编写升级例程并存储架构版本

参考：
- `references/data-and-cron.md`

## 验证

- 插件激活时无严重错误或警告
- 设置保存和读取正确（权限 + nonce 检查生效）
- 卸载时移除预期数据（且不删除其他数据）
- 运行仓库代码检查/测试（如果存在 PHPUnit/PHPCS）和任何 JS 构建步骤（如果插件包含资源文件）

## 失败模式/调试

- 激活钩子未触发：
  - 钩子注册错误（不在主文件作用域内）、主文件路径错误，或插件是网络激活
- 设置未保存：
  - 设置未注册、选项组错误、缺少权限、nonce 失败
- 安全回归：
  - 存在 nonce 但缺少权限检查；或清理后的输入未在输出时转义

参考：
- `references/debugging.md`

## 升级

在发明模式前，需先查阅插件手册和安全指南以获取规范细节。
