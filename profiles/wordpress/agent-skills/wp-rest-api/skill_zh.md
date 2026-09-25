# WP REST API

## 何时使用

当您需要执行以下操作时，请使用此技能：

- 创建或更新 REST 路由/端点
- 调试 401/403/404 错误或权限/nonce 问题
- 向 REST 响应添加自定义字段/元数据
- 通过 REST 暴露自定义帖子类型或分类法
- 实现模式 + 参数验证
- 调整响应链接/嵌入/分页

## 所需输入

- 仓库根目录 + 目标插件/主题/子插件（入口点路径）。
- 所需的命名空间 + 版本（例如 `my-plugin/v1`）和路由。
- 身份验证模式（cookie + nonce 与应用密码或认证插件）。
- 目标 WordPress 版本限制（如果低于 7.0，请指明）。

## 操作步骤

### 0) 筛选和定位 REST 使用情况

1. 运行筛选：
   - `node skills/wp-project-triage/scripts/detect_wp_project.mjs`
2. 搜索现有的 REST 使用情况：
   - `register_rest_route`
   - `WP_REST_Controller`
   - `rest_api_init`
   - `show_in_rest`, `rest_base`, `rest_controller_class`

如果这是一个完整站点的仓库，请在修改代码前选择特定的插件/主题。

### 1) 选择正确的方法

- **在 `wp/v2` 中暴露 CPT/分类法：**
  - 使用 `show_in_rest => true` + `rest_base`（如果需要）。
  - 可选地提供 `rest_controller_class`。
  - 阅读 `references/custom-content-types.md`。
- **自定义端点：**
  - 在 `rest_api_init` 上使用 `register_rest_route()`。
  - 对于非简单操作，优先使用控制器类（`WP_REST_Controller` 子类）。
  - 阅读 `references/routes-and-endpoints.md` 和 `references/schema.md`。

### 2) 安全注册路由（命名空间、方法、权限）

- 使用唯一的命名空间 `vendor/v1`；除非是核心，否则避免 `wp/*`。
- 始终提供 `permission_callback`（对于公共端点使用 `__return_true`）。
- 使用 `WP_REST_Server::READABLE/CREATABLE/EDITABLE/DELETABLE` 常量。
- 通过 `rest_ensure_response()` 或 `WP_REST_Response` 返回数据。
- 通过 `WP_Error` 返回错误，并带有明确的 `status`。

阅读 `references/routes-and-endpoints.md`。

### 3) 验证/清理请求参数

- 定义 `args`，包含 `type`, `default`, `required`, `validate_callback`, `sanitize_callback`。
- 优先使用 JSON Schema 验证，先 `rest_validate_value_from_schema`，再 `rest_sanitize_value_from_schema`。
- 不要在端点中直接读取 `$_GET`/`$_POST`；使用 `WP_REST_Request`。

阅读 `references/schema.md`。

### 4) 响应、字段和链接

- 不要从默认端点中删除核心字段；而是添加字段。
- 使用 `register_rest_field` 注册计算字段；使用 `register_meta` 并带有 `show_in_rest` 注册元数据。
- 对于 `object`/`array` 元数据，在 `show_in_rest.schema` 中定义模式。
- 如果需要未过滤的帖子内容（例如，目录插件注入 HTML），请求 `?context=edit` 以访问 `content.raw`（需要认证）。与 `_fields=content.raw` 配合使用以保持响应大小。
- 通过 `WP_REST_Response::add_link()` 添加相关资源链接。

阅读 `references/responses-and-fields.md`。

### 5) 身份验证和授权

- 对于 wp-admin/JS：cookie 认证 + `X-WP-Nonce`（动作 `wp_rest`）。
- 对于外部客户端：应用密码（基本认证）或认证插件。
- 在 `permission_callback` 中使用权限检查（授权），而不仅仅是“已登录”。

阅读 `references/authentication.md`。

### 6) 客户端行为（发现、分页、嵌入）

- 确保发现工作正常（`Link` 头或 `<link rel="https://api.w.org/">`）。
- 支持 `_fields`, `_embed`, `_method`, `_envelope`, 分页头。
- 记住 `per_page` 限制为 100。

阅读 `references/discovery-and-params.md`。

## 验证

- `/wp-json/` 索引包含您的命名空间。
- 您的路由上的 `OPTIONS` 返回模式（当提供时）。
- 端点返回预期数据；权限失败返回 401/403。
- 当 `show_in_rest` 为 true 时，CPT/分类法路由出现在 `wp/v2` 下。
- 运行仓库检查/测试和任何 PHP/JS 构建步骤。

## 失败模式 / 调试

- 404：`rest_api_init` 未触发，路由拼写错误，或永久链接关闭（使用 `?rest_route=`）。
- 401/403：缺少 nonce/认证，或 `permission_callback` 过于严格。
- `_doing_it_wrong` 对于缺少 `permission_callback`：添加它（如果公共，使用 `__return_true`）。
- 无效参数：缺少/不正确的 `args` 模式或验证回调。
- 字段缺失：`show_in_rest` 为 false，元数据未注册，或 CPT 缺少 `custom-fields` 支持。

## 升级

如果版本支持或行为不明确，请在发明模式之前咨询 REST API 手册和核心文档。
