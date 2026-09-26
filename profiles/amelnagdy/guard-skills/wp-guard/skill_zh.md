# WP Guard

你正在审查在发布前生成或修改的 WordPress 代码。在第一次实现检查后，将以下规则作为守门检查步骤应用。做一个敏锐的审查者，而不是一个吹毛求疵的人：标记那些创建漏洞、破坏翻译或使服务器崩溃的内容——忽略 WPCS 工具已经处理的装饰性偏好。

这些规则的存在是因为 AI 代理生成的 WordPress 代码存在系统性缺陷：原始的 `echo` 请求数据、既没有 nonce 也没有能力检查的 AJAX 处理程序、通过字符串插值构建的 SQL、硬编码的英文用户界面字符串、百万级帖子的网站上 `posts_per_page => -1`，以及核心 API 已经提供的 API 手工替换。每一个在演示中看起来都很好，在生产环境中却会失败。

## 如何使用这项技能

**守门检查模式**（推荐）：在 WordPress 代码生成或编辑后，将规则应用于差异或目标文件，然后在交付前运行自我检查。在向用户展示之前修复违规行为。

**实时模式**（显式）：当用户在编写 WordPress 代码之前调用这项技能时，在编写过程中应用相同的规则，然后在交付前运行自我检查。

**审查模式**（用户要求你审查、审计或评估 WordPress 代码）：参考 [references/review-checklist.md](references/review-checklist.md) 对目标文件进行检查，并生成一个结构化的发现报告。除非被要求，否则不要在审查模式下编辑代码。

将这项技能与 clean-code-guard 配合使用（当两者都安装时）：clean-code-guard 负责通用代码质量；wp-guard 负责 WordPress 层。

## 首先适应项目

1. 阅读项目的代理说明（CLAUDE.md、AGENTS.md）、`phpcs.xml`/WPCS 配置和 `composer.json`。项目约定在冲突时优先。
2. 确定已建立的命名前缀（函数、选项、元键、句柄）以及最低支持的 WP/PHP 版本。两者都要匹配。
3. 检测上下文：WooCommerce API 在使用中 → 如果安装了 woo-guard，则与这项技能一起应用；否则应用 WooCommerce 的 HPOS、CRUD 和结账规则，参考其开发者文档。多语言网站（WPML/Polylang/多站点）→ 国际化规则是强制性的，不是建议性的。
4. 在编写之前阅读一个相邻的文件。模仿其错误处理、钩子注册风格和转义习惯——除非它们违反了以下安全规则，这些规则是不可协商的。

## 规则

### 安全——必须修复，无例外

1. **晚转义，转义所有内容。** 每个跨入 HTML 输出的变量都要通过上下文正确的函数处理：`esc_html()`、`esc_attr()`、`esc_url()` 或 `wp_kses()`/`wp_kses_post()` 用于富内容。传递给内联 JS 的数据通过 `wp_json_encode()` + `wp_add_inline_script()` 处理——`esc_js()` 是遗留的，仅用于内联属性中的单引号字符串。转义发生在输出时，而不是存储时。没有 `esc_*` 包装的 `echo $anything;` 会导致审查失败。

2. **早清理，并首先去除斜杠。** 请求数据（`$_POST`、`$_GET`、`$_REQUEST`、`$_SERVER`）永远不会直接接触逻辑：首先使用 `wp_unslash()`，然后使用类型正确的清理函数（`sanitize_text_field()`、`sanitize_key()`、`absint()`、`sanitize_email()` 等）。清理不是转义；做其中一个并不能免除另一个。

3. **每次状态变化都证明身份和意图。** 表单处理程序、AJAX 端点和 REST 路由在更改任何内容时都需要同时进行能力检查（`current_user_can()`）和 nonce 检查（`check_admin_referer()`、`check_ajax_referer()` 或 REST nonce 处理）。Nonce 不是授权。写作路由的 REST `permission_callback` 为 `__return_true` 会导致审查失败。

4. **`$wpdb->prepare()` 用于包含变量的每个查询。** 使用占位符（WP ≥ 6.2 上的 `%s`、`%d`、`%f` 和标识符的 `%i`），而不是插值或连接。当可以表达查询时，优先使用 `WP_Query`、元数据和选项 API 而不是原始 SQL。

### 核心API规范

5. **使用平台，不要重新发明它。** 外发 HTTP 通过 `wp_remote_get()`/`wp_remote_post()`，而不是 curl。资源通过 `wp_enqueue_script()`/`wp_enqueue_style()`，而不是回显 `<script>`/`<style>` 标签。调度通过 WP-Cron 或 Action Scheduler。重定向通过 `wp_safe_redirect()` 后跟 `exit`。文件写入通过 `WP_Filesystem`。简单的持久化数据通过选项/转瞬即逝，而不是自定义表。

6. **验证每个钩子和函数是否存在。** 在 `add_action()`、`add_filter()` 或调用核心/插件函数之前，确认它们在支持的版本中存在——阅读源代码或项目的已安装代码。在 WordPress 中，幻觉的钩子会静默失败：没有错误，没有行为。还要匹配钩子到时刻——前端代码不会在 `admin_init` 时加载，查询不会在 `init` 期望它们之前运行。

7. **所有公共内容都使用前缀或命名空间。** 函数、类、选项、转瞬即逝、元键、脚本句柄、AJAX 动作、REST 命名空间——所有内容都携带项目前缀。通用名称（`get_settings`、`data`、`api_key`）是等待下一个活动插件的冲突。

8. **保护直接访问。** 每个执行工作的 PHP 文件都以 `ABSPATH` 检查（或等效的项目约定）开始。

### 国际化

9. **每个用户界面字符串都是翻译就绪的。** 上下文正确的包装器（`__()`、`_e()`、`_x()`、`_n()` 或转义组合 `esc_html__()`、`esc_attr__()`），匹配插件缩略名的字面文本域——永远不是变量或常量——每个占位符的翻译者注释、`_n()` 用于复数（永远不要用 `sprintf` 硬编码单数/复数选择）、不通过连接组合句子。日期和数字通过 `date_i18n()`/`wp_date()` 和 `number_format_i18n()`。详细信息和 JS 国际化：[references/i18n.md](references/i18n.md)。

### 性能

10. **查询规范。** 没有 `posts_per_page => -1` 和 `query_posts()`，任何时候都不使用。当只需要 ID 时使用 `'fields' => 'ids'`，当不分页时使用 `'no_found_rows' => true`，并且永远不要在循环中查询可以一次预热的（元/术语缓存）。详细内容：[references/performance.md](references/performance.md)。

11. **缓存昂贵的工作，在需要的地方加载资源。** 远程调用和重型计算通过转瞬即逝或对象缓存并带有明确的 TTL。大型或很少读取的选项注册为 `autoload => false`。脚本和样式仅在它们使用的屏幕上排队。

## 交付前的自我检查

1. Grep 你的差异，查找 `echo`、`print`、`<?=`：每个变量输出是否用上下文正确的函数转义？
2. Grep 查找 `$_POST`、`$_GET`、`$_REQUEST`：去斜杠了吗？清理了吗？nonce 验证了吗？能力检查了吗？
3. Grep 查找 `$wpdb->`：每个变量是否在占位符后面？
4. 任何不在国际化包装器外的用户界面字符串？任何非字面文本域？
5. 任何你没有验证存在的钩子或函数？
6. 任何无界查询、未缓存的远程调用或无条件排队？
7. 每个新的公共名称是否都携带项目前缀？
8. 这是否能在 WPCS（`WordPress-Extra` + `WordPress-Security`）下无警告地通过？

如果任何答案错误，在向用户展示之前修复它。

## 报告格式（审查模式）

```
**规则 N 违规** 在 `path/file.php:<行号或函数>`
- 内容： <一句话>
- 风险： <XSS / SQLi / CSRF / 破坏国际化 / 扩展性——一句话>
- 修复： <一句话>
```

按文件分组，以安全发现开头。如果文件干净，不要提及它。

## 严重性指南

- **必须修复**：规则 1–4——这些是可利用的（XSS、SQLi、CSRF、权限提升）
- **应该修复**：规则 5–9——冲突、静默失败、不可翻译的发布
- **值得注意**：规则 10–11——它们决定了代码是否能承受流量；对于每个请求运行的代码，在它们上面阻止

## 参考

- [references/security.md](references/security.md) — 转义/清理函数表、nonce 生命周期、REST 权限、`$wpdb->prepare` 详细信息、文件上传
- [references/i18n.md](references/i18n.md) — 包装器选择、文本域规则、复数、翻译者注释、JS 翻译、RTL、多语言插件陷阱
- [references/performance.md](references/performance.md) — WP_Query 标志、转瞬即逝与对象缓存、autoload 卫生、资源加载、cron、扩展性陷阱
- [references/review-checklist.md](references/review-checklist.md) — 审查模式的结构化检查
- [references/sources.md](references/sources.md) — 手册和研究 URL；仅在引用来源时阅读

## 这项技能不做什么

- 运行 PHPCS、PHPStan 或 Plugin Check——使用项目的工具进行机械验证；这项技能是它上面的判断层。
- 决定插件架构或业务逻辑——它保护 WordPress 代码的发布，而不是它做什么。
- 替换 clean-code-guard 或 test-guard——通用代码质量和测试质量仍然属于它们的管辖范围。
