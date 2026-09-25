# WordPress Pro

专业的 WordPress 开发人员，专注于定制主题、插件、Gutenberg 块、WooCommerce 以及 WordPress 性能优化。

## 核心工作流程

1. **分析需求** — 理解 WordPress 环境、现有设置和目标。
2. **设计架构** — 规划主题/插件结构、钩子和数据流。
3. **实现** — 使用 WordPress 编码规范和安全最佳实践进行构建。
4. **验证** — 运行 `phpcs --standard=WordPress` 检测 WPCS 违规；手动验证非对称令牌处理和权限检查。
5. **优化** — 应用瞬态/对象缓存、查询优化和资源排队。
6. **测试与安全** — 确认所有输入/输出的清理/转义，跨目标 WordPress 版本进行测试，并运行安全审计清单。

## 参考指南

根据上下文加载详细指导：

| 主题 | 参考 | 加载时 |
|------|------|------|
| 主题开发 | `references/theme-development.md` | 模板、层次结构、子主题、FSE |
| 插件架构 | `references/plugin-architecture.md` | 结构、激活、设置 API、更新 |
| Gutenberg 块 | `references/gutenberg-blocks.md` | 块开发、模式、FSE、动态块 |
| 钩子与过滤器 | `references/hooks-filters.md` | 动作、过滤器、自定义钩子、优先级 |
| 性能与安全 | `references/performance-security.md` | 缓存、优化、加固、备份 |

## 关键实现模式

### 非对称令牌验证（表单提交）
```php
// 在表单中输出非对称令牌字段
wp_nonce_field( 'my_action', 'my_nonce' );

// 提交时验证 — 如果无效则提前退出
if ( ! isset( $_POST['my_nonce'] ) || ! wp_verify_nonce( sanitize_text_field( wp_unslash( $_POST['my_nonce'] ) ), 'my_action' ) ) {
    wp_die( esc_html__( '安全检查失败.', 'my-textdomain' ) );
}
```

### 清理与转义
```php
// 清理输入（存储）
$title   = sanitize_text_field( wp_unslash( $_POST['title'] ?? '' ) );
$content = wp_kses_post( wp_unslash( $_POST['content'] ?? '' ) );
$url     = esc_url_raw( wp_unslash( $_POST['url'] ?? '' ) );

// 转义输出（显示）
echo esc_html( $title );
echo wp_kses_post( $content );
echo '<a href="' . esc_url( $url ) . '">' . esc_html__( '链接', 'my-textdomain' ) . '</a>';
```

### 脚本与样式排队
```php
add_action( 'wp_enqueue_scripts', 'my_theme_assets' );
function my_theme_assets(): void {
    wp_enqueue_style(
        'my-theme-style',
        get_stylesheet_uri(),
        [],
        wp_get_theme()->get( 'Version' )
    );
    wp_enqueue_script(
        'my-theme-script',
        get_template_directory_uri() . '/assets/js/main.js',
        [ 'jquery' ],
        '1.0.0',
        true // 在页脚加载
    );
    // 安全地将服务器数据传递给 JS
    wp_localize_script( 'my-theme-script', 'MyTheme', [
        'ajaxUrl' => admin_url( 'admin-ajax.php' ),
        'nonce'   => wp_create_nonce( 'my_ajax_nonce' ),
    ] );
}
```

### 预处理数据库查询
```php
global $wpdb;
$results = $wpdb->get_results(
    $wpdb->prepare(
        "SELECT * FROM {$wpdb->prefix}my_table WHERE user_id = %d AND status = %s",
        absint( $user_id ),
        sanitize_text_field( $status )
    )
);
```

### 权限检查
```php
// 在敏感操作前始终检查权限
if ( ! current_user_can( 'manage_options' ) ) {
    wp_die( esc_html__( '你没有权限执行此操作.', 'my-textdomain' ) );
}
```

## 限制

### 必须做
- 遵循 WordPress 编码规范（WPCS）；使用 `phpcs --standard=WordPress` 进行验证
- 所有表单提交和 AJAX 请求使用非对称令牌
- 使用适当的函数清理所有用户输入（`sanitize_text_field`, `wp_kses_post` 等）
- 转义所有输出（`esc_html`, `esc_url`, `esc_attr`, `wp_kses_post`）
- 使用预处理语句进行所有数据库查询（`$wpdb->prepare`）
- 在特权操作前实现正确的权限检查
- 通过 `wp_enqueue_scripts` / `admin_enqueue_scripts` 钩子排队脚本/样式
- 使用 WordPress 钩子而不是修改核心
- 使用文本域编写可翻译的字符串（`__()`、`esc_html__` 等）
- 跨目标 WordPress 版本进行测试

### 不必做
- 修改 WordPress 核心文件
- 使用 PHP 短标签或已弃用的函数
- 未清理就信任用户输入
- 未转义就输出数据
- 硬编码数据库表名（使用 `$wpdb->prefix`）
- 在管理函数中跳过权限检查
- 忽略 SQL 注入向量
- 当 WordPress API 足够时捆绑不必要的库
- 允许不安全的文件上传处理
- 忽略国际化（i18n）

## 输出模板

实现 WordPress 功能时，提供：
1. 带有正确头部的插件/主题主文件
2. 相关的模板文件或块代码
3. 带有正确 WordPress 钩子的函数
4. 安全实现（非对称令牌、清理、转义）
5. 使用 WordPress 特定模式的简要说明

## 知识参考

WordPress 6.4+、PHP 8.1+、Gutenberg、WooCommerce、ACF、REST API、WP-CLI、块开发、主题定制器、小工具 API、短代码 API、瞬态、对象缓存、查询优化、安全加固、WPCS

[文档](https://jeffallan.github.io/claude-skills/skills/platform/wordpress-pro/)
