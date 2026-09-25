# WP 交互 API

## 使用场景

当用户提到以下内容时，使用此技能：

- 交互 API、`@wordpress/interactivity`，
- `data-wp-interactive`、`data-wp-on--*`、`data-wp-bind--*`、`data-wp-context`，
- 块 `viewScriptModule` / 基于模块的视图脚本，
- hydration 问题或“指令未触发”。

## 所需输入

- 仓库根目录 + 筛分输出 (`wp-project-triage`)。
- 受影响的块/主题/插件的表面（前端、编辑器、两者）。
- 任何约束：WP 版本、构建中是否支持模块。

## 流程

### 1) 检测现有使用情况 + 集成风格

搜索：

- `data-wp-interactive`
- `@wordpress/interactivity`
- `viewScriptModule`

确定：

- 这是否是一个通过 `block.json` 视图脚本模块提供交互的块？
- 是否是主题级别的交互？
- 是否是插件端的“增强现有标记”使用？

如果你正在创建一个新的交互式块（不仅仅是调试），请优先使用官方的脚手架模板：

- `@wordpress/create-block-interactive-template`（通过 `@wordpress/create-block`）

### 2) 确定商店

定位商店定义并确认：

- 状态形状，
- 动作（突变），
- `data-wp-on--*` 使用的回调/事件处理器。

### 3) 服务器端渲染（最佳实践）

**在服务器上预渲染 HTML**，然后再输出，以确保：

- JavaScript 加载前的 HTML 中具有正确的初始状态（无布局偏移）。
- SEO 利益和更快的感知加载时间。
- 当客户端 JavaScript 接管时，无缝 hydration。

#### 启用服务器指令处理

对于使用 `block.json` 的组件，添加 `supports.interactivity`：

```json
{
  "supports": {
    "interactivity": true
  }
}
```

对于没有 `block.json` 的主题/插件，使用 `wp_interactivity_process_directives()` 来处理指令。

#### 在 PHP 中初始化状态/上下文

使用 `wp_interactivity_state()` 定义初始全局状态：

```php
wp_interactivity_state( 'myPlugin', array(
  'items'    => array( 'Apple', 'Banana', 'Cherry' ),
  'hasItems' => true,
));
```

对于局部上下文，使用 `wp_interactivity_data_wp_context()`：

```php
<?php
$context = array( 'isOpen' => false );
?>
<div <?php echo wp_interactivity_data_wp_context( $context ); ?>>
  ...
</div>
```

#### 在 PHP 中定义派生状态

当派生状态影响初始 HTML 渲染时，在 PHP 中复制逻辑：

```php
wp_interactivity_state( 'myPlugin', array(
  'items'    => array( 'Apple', 'Banana' ),
  'hasItems' => function() {
    $state = wp_interactivity_state();
    return count( $state['items'] ) > 0;
  }
));
```

这确保了指令如 `data-wp-bind--hidden="!state.hasItems"` 在首次加载时正确渲染。

有关详细示例和模式，请参阅 `references/server-side-rendering.md`。

### 4) 安全地实现或更改指令

当触摸标记指令时：

- 保持指令使用最小化和作用域化，
- 优先使用映射到商店状态的稳定数据属性，
- 确保服务器渲染的标记 + 客户端 hydration 一致。

**WordPress 6.9 更改：**

- **`data-wp-ignore` 已弃用**，未来版本将移除。它破坏了上下文继承并导致客户端导航问题。避免使用它。
- **唯一的指令 ID**：现在可以在一个元素上使用 `---` 分隔符存在多个相同类型的指令（例如，`data-wp-on--click---plugin-a="..."` 和 `data-wp-on--click---plugin-b="..."`）。
- **新的 TypeScript 类型**：`AsyncAction<ReturnType>` 和 `TypeYield<T>` 有助于异步动作类型。

有关快速指令提示，请参阅 `references/directives-quickref.md`。

### 5) 构建工具对齐

验证仓库是否支持所需的模块构建路径：

- 如果它使用 `@wordpress/scripts`，请优先使用其约定。
- 如果它使用自定义打包，请确认模块输出受支持。

### 6) 调试常见失败模式

如果交互时“什么都没发生”：

- 确认 `viewScriptModule` 是否已入队/加载，
- 确认 DOM 元素具有 `data-wp-interactive`，
- 确认商店命名空间与指令的值匹配，
- 确认 hydration 之前没有 JS 错误。

请参阅 `references/debugging.md`。

## 验证

- `wp-project-triage` 在你的更改后指示 `signals.usesInteractivityApi: true`（如果适用）。
- 手动冒烟测试：指令触发和状态更新符合预期。
- 如果存在测试：添加/扩展交互路径的 Playwright E2E。

## 失败模式 / 调试

- 指令存在但无效：
  - 视图脚本未加载、错误的模块入口点或缺少 `data-wp-interactive`。
- hydration 不匹配 / 闪烁：
  - 服务器标记与客户端预期不一致；简化或对齐初始状态。
  - PHP 中未定义派生状态：使用 `wp_interactivity_state()` 与闭包。
- 初始内容缺失或错误：
  - `supports.interactivity` 在 `block.json` 中未设置（对于块）。
  - 未调用 `wp_interactivity_process_directives()`（对于主题/插件）。
  - 渲染之前 PHP 中未初始化状态/上下文。
- 加载时布局偏移：
  - 服务器上缺少派生状态（如 `state.hasItems`），导致 `hidden` 属性缺失。
- 性能回归：
  - 过于宽泛的交互根；将交互作用域到较小的子树。
- 客户端导航问题（WordPress 6.9）：
  - `getServerState()` 和 `getServerContext()` 现在在页面转换之间重置——确保你的代码不会假设陈旧值仍然存在。
  - 路由区域现在支持 `attachTo` 以动态渲染覆盖（模态、弹出）。

## 升级

- 如果仓库构建约束不明确，请询问：“这是使用 `@wordpress/scripts` 还是自定义打包器（webpack/vite）？”
- 参考：
  - `references/server-side-rendering.md`
  - `references/directives-quickref.md`
  - `references/debugging.md`
