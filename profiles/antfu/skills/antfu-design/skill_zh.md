使用此方法在任何框架（React、Vue、Svelte、Solid 或纯 HTML）中构建使用 UnoCSS 的界面，从密集的开发工具面板到落地页。先阅读核心设计指南以确定方向，然后应用符号系统以及修饰和防脏规则。

## 核心规则

- 在标记中使用语义快捷方式（`bg-base`、`border-base`、`color-active`、`btn-action`），而不是原始的实用工具链。
- 一起设计亮色和暗色模式。核心符号必须在两种主题中都有效。
- 命名 z-index 层级（`z-top-nav`、`z-panel-content`、`z-drawer-content`）。在模板中不要使用原始的 z 值。
- 仅生成基于类的实用工具（`class="..."`）。在生成的代码中避免使用 Attributify 语法。
- 保持图标/状态类字符串为字面量，以便 UnoCSS 可以静态提取它们（需要时使用 `// @unocss-include`）。
- 使用 `font-mono` + `tabular-nums` 来表示技术值（路径、SHA、计数器、时间戳、百分比）。
- 对于长路径和 ID，视觉上截断，但在 `title` 中保留完整值。
- 阅读简介并设置三个旋钮，然后再选择外观（核心设计指南）。
- 对于密集或结构性的表面使用边框，对于提升的表面使用分层阴影（微交互特性）。
- 在任何面向用户文本中禁止使用零 em-dash 和 en-dash 字符（最佳实践-防脏）。

## 启动快捷方式

一个最小的语义核心。有关完整的 `uno.config.ts` 和基础样式的信息，请参阅核心启动套件。

```ts
shortcuts: [
  {
    'color-base': 'color-neutral-800 dark:color-neutral-200',
    'bg-base': 'bg-white dark:bg-#111',
    'bg-secondary': 'bg-#eee dark:bg-#222',
    'border-base': 'border-#8882',

    'bg-active': 'bg-#8881',
    'color-active': 'color-primary-600 dark:color-primary-300',
    'border-active': 'border-primary-600/25 dark:border-primary-400/25',

    'btn-action': 'inline-flex items-center gap-2 rounded border border-base px2 py1 op75 hover:op100 hover:bg-active disabled:pointer-events-none disabled:op30!',
    'op-fade': 'op65 dark:op55',
    'op-mute': 'op30 dark:op25',

    'z-top-nav': 'z-60',
    'z-panel-content': 'z-70',
    'z-drawer-content': 'z-100',
  },
]
```

## 核心参考

| 主题 | 描述 | 参考 |
|------|------|------|
| 核心原则 | 语义符号、暗色模式一致性、z-index 命名、类优先输出 | [核心原则](references/core-principles.md) |
| 启动套件 | 复制粘贴 UnoCSS 启动配置和基础亮色/暗色样式 | [核心启动套件](references/core-starter-kit.md) |
| 符号和组合 | 符号家族、可重用类组合、移动安全外壳符号 | [核心符号和组合](references/core-tokens-and-combinations.md) |
| 设计指南和旋钮 | 阅读简介、声明设计指南、设置变化/运动/密度旋钮 | [核心设计指南](references/core-design-read.md) |

## 最佳实践

| 主题 | 描述 | 参考 |
|------|------|------|
| 严格规则和预检 | 做/不做的清单和综合预检 | [最佳实践-严格规则](references/best-practices-strict-rules.md) |
| 类优先于 Attributify | 为什么生成的代码使用类实用工具，以及转换 | [最佳实践-类实用工具优先于 Attributify](references/best-practices-class-utilities-over-attributify.md) |
| 防脏卫生 | 砍断连字符和禁止的 AI 指示模式 | [最佳实践-防脏](references/best-practices-anti-slop.md) |
| 偏见校正 | 字体、颜色、布局和材质性的默认值以覆盖 | [最佳实践-偏见校正](references/best-practices-bias-correction.md) |

## 功能

| 主题 | 描述 | 参考 |
|------|------|------|
| 数据展示 | 路径、图标、时间、日期、数字、徽章、按钮 | [功能-数据展示](references/features-data-presentation.md) |
| 微交互 | 半径、对齐、阴影、动画、数字、轮廓、点击区域 | [功能-微交互](references/features-micro-interactions.md) |
| 浮动 Vue 覆盖 | 共享浮动 Vue 设置和弹出器样式 | [功能-浮动 Vue 覆盖](references/features-floating-vue-overrides.md) |

## 高级

| 主题 | 描述 | 参考 |
|------|------|------|
| 模式词汇 | 用于识别和选择的命名 UI 模式 | [高级-模式词汇](references/advanced-pattern-vocabulary.md) |
| 重新设计协议 | 检测模式、先审计、保留 IA 和 SEO | [高级-重新设计协议](references/advanced-redesign-protocol.md) |

<!-- 源参考：
- https://github.com/antfu/node-modules-inspector
- https://github.com/vitejs/devtools/tree/main/packages/rolldown
- https://github.com/eslint/config-inspector
- https://github.com/antfu/vite-plugin-inspect
- https://github.com/antfu/agent-container
- https://github.com/Leonxlnx/taste-skill
- https://github.com/jakubkrehel/make-interfaces-feel-better
-->
