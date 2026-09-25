# WP区块开发

## 何时使用

使用此技能进行区块工作，例如：

- 创建新区块或更新现有区块
- 修改 `block.json`（scripts/styles/supports/attributes/render/viewScriptModule）
- 修复“区块无效 / 无法保存 / 属性无法持久化”问题
- 添加动态渲染（`render.php` / `render_callback`）
- 区块弃用和迁移（`deprecated` 版本）
- 区块的构建工具（`@wordpress/scripts`，`@wordpress/create-block`，`wp-env`）

## 所需输入

- 仓库根目录和目标（插件 vs 主题 vs 完整站点）。
- 区块名称/命名空间及其位置（如果知道，则为 `block.json` 的路径）。
- 目标 WordPress 版本范围（尤其是在使用模块 / `viewScriptModule` 时）。

## 流程

### 0) 筛选和定位区块

1. 运行筛选：
   - `node skills/wp-project-triage/scripts/detect_wp_project.mjs`
2. 列出区块（确定性扫描）：
   - `node skills/wp-block-development/scripts/list_blocks.mjs`
3. 确定你要修改的区块根（包含 `block.json` 的目录）。

如果此仓库是完整站点（存在 `wp-content/`），请明确说明包含区块的*哪个*插件/主题。

### 1) 创建新区块（如果需要）

如果你正在创建新区块，优先使用脚手架而不是手动构建结构：

- 使用 `@wordpress/create-block` 来搭建现代区块/插件设置。
- 如果你需要从一开始就使用交互式 API，请使用交互式模板。

阅读：
- `references/creating-new-blocks.md`

搭建后：

1. 重新运行区块列表脚本并确认新区块根目录。
2. 继续执行剩余步骤（模型选择、元数据、注册、序列化）。

### 2) 确保 apiVersion 3（WordPress 6.9+）

WordPress 6.9 要求 `block.json` 脚本中强制使用 `apiVersion: 3`。apiVersion 为 2 或更低的区块在 `SCRIPT_DEBUG` 开启时会触发控制台警告。

**为什么这很重要：**
- WordPress 7.0 将在 iframe 中运行帖子编辑器，无论区块的 apiVersion 如何。
- apiVersion 3 确保你的区块在 iframe 编辑器中正常工作（样式隔离、视口单位、媒体查询）。

**迁移：** 从版本 2 更改为 3 通常只需更新 `block.json` 中的 `apiVersion` 字段。但是：
- 在本地环境中启用 iframe 编辑器进行测试。
- 确保所有样式句柄都包含在 `block.json` 中（iframe 中缺失的样式将不会应用）。
- 绑定到特定 `window` 的第三方脚本可能会出现作用域问题。

阅读：
- `references/block-json.md`（apiVersion 和 schema 详细信息）

### 3) 选择正确的区块模型

- **静态区块**（将标记保存在帖子内容中）：实现 `save()`；保持属性序列化稳定。
- **动态区块**（服务器渲染）：在 `block.json` 中使用 `render`（或在 PHP 中使用 `render_callback`）并保持 `save()` 最小或 `null`。
- **交互式前端行为**：
  - 优先使用 `viewScriptModule`（在支持的情况下）为现代基于模块的视图脚本。
  - 如果你主要在 `data-wp-*` 指令或存储上工作，也使用 `wp-interactivity-api`。

### 4) 安全更新 `block.json`

在区块的 `block.json` 中进行更改，然后确认注册与元数据匹配。

对于字段级指导，阅读：
- `references/block-json.md`

常见陷阱：

- 更改 `name` 会破坏兼容性（将其视为稳定 API）
- 更改保存的标记而不添加 `deprecated` 会触发“无效区块”
- 未正确定义源/序列化而添加属性会导致“属性无法保存”

### 5) 注册区块（推荐服务器端）

优先使用元数据进行 PHP 注册，尤其是在：

- 你需要动态渲染时
- 你需要翻译（`wp_set_script_translations`）
- 你需要条件性资源加载时

阅读并应用：
- `references/registration.md`

### 6) 实现编辑/保存/渲染模式

遵循包装属性最佳实践：

- 编辑器：`useBlockProps()`
- 静态保存：`useBlockProps.save()`
- 动态渲染（PHP）：`get_block_wrapper_attributes()`

阅读：
- `references/supports-and-wrappers.md`
- `references/dynamic-rendering.md`（如果动态）

### 7) 内部区块（区块组合）

如果你的区块是一个“容器”嵌套其他区块，将内部区块视为一等特性：

- 使用 `useInnerBlocksProps()` 将内部区块与包装属性集成。
- 如果你更改内部标记，请考虑迁移。

阅读：
- `references/inner-blocks.md`

### 8) 属性和序列化

更改属性前：

- 确认属性值的位置（注释分隔符 vs HTML vs 上下文）
- 避免使用已弃用的 `meta` 属性源

阅读：
- `references/attributes-and-serialization.md`

### 9) 迁移和弃用（避免“无效区块”）

如果你更改了保存的标记或属性：

1. 添加 `deprecated` 条目（最新 → 最旧）。
2. 为旧版本提供 `save`，并提供可选的 `migrate` 以规范化属性。

阅读：
- `references/deprecations.md`

### 10) 工具和验证命令

优先使用仓库当前使用的工具：

- `@wordpress/scripts`（常用）→ 运行现有的 npm 脚本
- `wp-env`（常用）→ 用于本地 WP + E2E

阅读：
- `references/tooling-and-testing.md`

## 验证

- 区块出现在插入器中并成功插入。
- 保存并重新加载不会触发“无效区块”。
- 前端输出符合预期（静态：保存的标记；动态：服务器输出）。
- 资源按预期加载（编辑器 vs 前端）。
- 运行筛选推荐的仓库的代码检查/构建/测试。

## 失败模式 / 调试

如果出现故障，从这里开始：

- `references/debugging.md`（常见故障 + 最快检查）
- `references/attributes-and-serialization.md`（属性无法保存）
- `references/deprecations.md`（更改后无效区块）

## 升级

如果你不确定上游行为或版本支持，请先查阅权威文档：

- WordPress 开发者资源（区块编辑器手册、主题手册、插件手册）
- Gutenberg 仓库文档（用于前沿行为）
