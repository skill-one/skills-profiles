# Material Design 3

本指南指导实现 Google 的 Material Design 3 (MD3)——一个个性化、自适应、富有表现力的设计系统。MD3 使用动态颜色、色调表面、圆角形状和基于弹簧的运动，创建出感觉生动且个性化的 UI。

## 哲学

MD3 建立在三个原则之上：
- **个性化**：动态颜色适应用户的壁纸或内容。主题是个性化的，而非一刀切。
- **自适应**：布局跨越 5 个窗口大小类别进行转换。组件会相应地调整大小、重新定位并改变形态。
- **富有表现力**：形状变形、弹簧物理和强调的排版在不牺牲可用性的情况下创造了令人愉悦的时刻。

## 当前更新：Google I/O 2026

Material 的 [Google I/O 2026 更新](https://m3.material.io/blog/whats-new-at-io26) 强调了 **优先使用 Compose** 的 Android 路径，并扩展了富有表现力和自适应的指导：
- **Material Android 优先使用 Compose**：对于新的 Android 工作，优先使用 Jetpack Compose Material3 以获取最新的组件、富有表现力的 API、自适应框架和 Styles API 集成。在现有应用中可能仍需要 Android Views，但它们不应被视为新 Material 3 实现的默认路径。
- **富有表现力的布局系统**：使用富有表现力的布局框架来适应跨越移动设备、桌面、折叠屏、手表、XR 和其他空间形态的屏幕。从自适应框架/窗口大小类别开始，而不是从固定的以手机优先的布局开始。
- **8dp 间距系统**：应用间距标记用于边距、填充和间隙，以便布局和组件可以针对设备类型和密度进行程序化调整。
- **新的/更新的富有表现力的组件**：列表、菜单、搜索和搜索应用栏具有更新的富有表现力的指导，Jetpack Compose 作为主要实现目标。
- **手表和 XR**：手表强调基于物理的运动、弧形文本和边缘紧贴容器。XR 强调空间面板和基于深度的提升。

**与 MD2 的主要区别**：
- 色调表面取代了提升阴影作为主要的深度提示
- 动态颜色从单一种子颜色生成完整方案
- 默认情况下完全圆角（而不是微圆角）
- 基于弹簧的运动物理取代了组件的固定缓动曲线
- 用户控制的对比度三级（标准/中等/高）

**与前端设计技能的关系**：
当两个技能都处于活动状态时，MD3 提供设计系统（标记、组件、布局规则），而前端设计在前端设计的约束内提供创意方向。MD3 规则优先于组件结构和标记使用。注意：Roboto/Roboto Flex 在 MD3 中确实是正确的默认字体——当实现 MD3 时，前端设计的指导避免使用 Roboto 不适用。

## 决策树

**你在构建什么？**
```
完整应用框架        → 查看 "常见模式：应用外壳" + references/layout-and-responsive.md
单个组件            → 查看 "组件快速参考" 表格 → references/component-catalog.md
自定义主题            → 查看 references/theming-and-dynamic-color.md
表单 / 输入布局      → 查看 references/component-catalog.md § 输入组件
导航结构            → 查看 references/navigation-patterns.md
数据显示            → 查看 references/component-catalog.md § 数据显示
```

**在哪个平台？**
```
Jetpack Compose        → 主要：androidx.compose.material3, MaterialTheme, references/*
Flutter                  → useMaterial3: true 在 ThemeData 中, ColorScheme.fromSeed()
Web (vanilla JS)         → @material/web (有限；维护模式) + CSS 自定义属性
Web (React/Vue/Svelte)   → CSS 自定义属性 + 包装组件 (没有官方 React 库)
Web (CSS-only)           → MD3 标记值作为 CSS 自定义属性 (没有 <md-*> 元素)
```

## 设计标记系统

所有 MD3 标记都使用 `md.sys` 命名空间。**Jetpack Compose** 将角色映射到 `MaterialTheme.colorScheme`、`MaterialTheme.typography` 和 `MaterialTheme.shapes`（与规范具有相同的语义角色）。**在 Web 上**，这些映射到 CSS 自定义属性 (`--md-sys-*`)：

### 颜色标记 (`--md-sys-color-*`)
| 标记 | 目的 |
|-------|---------|
| `primary` | 高强调度的填充、文本、图标针对表面 |
| `on-primary` | 主色上的文本/图标 |
| `primary-container` | 关键组件（FAB 等）的突出填充 |
| `on-primary-container` | 主色容器上的文本/图标 |
| `secondary` / `on-secondary` | 较不突出的强调 |
| `secondary-container` / `on-secondary-container` | 保守的组件（色调按钮） |
| `tertiary` / `on-tertiary` | 对比强调 |
| `tertiary-container` / `on-tertiary-container` | 互补容器 |
| `error` / `on-error` | 错误状态（静态——不会随着动态颜色变化） |
| `error-container` / `on-error-container` | 错误容器填充 |
| `surface` | 默认背景 |
| `on-surface` | 任何表面上的文本/图标 |
| `on-surface-variant` | 表面上的低强调度文本/图标 |
| `surface-container-lowest` | 最低强调度的容器 |
| `surface-container-low` | 低强调度的容器 |
| `surface-container` | 默认容器（导航区域） |
| `surface-container-high` | 高强调度的容器 |
| `surface-container-highest` | 最高强调度的容器 |
| `surface-dim` / `surface-bright` | 在亮/暗之间保持相对亮度 |
| `inverse-surface` / `inverse-on-surface` / `inverse-primary` | 对比元素（snackbars） |
| `outline` | 重要边界（文本字段边框） |
| `outline-variant` | 装饰元素（分隔符） |

完整详情：`references/color-system.md`

### 排版标记 (`--md-sys-typescale-*`)
| 尺寸 | 尺寸 | 使用 |
|-------|-------|-----|
| Display | L / M / S | 英雄文本、大数字 |
| Headline | L / M / S | 章节标题 |
| Title | L / M / S | 较小的标题、卡片标题 |
| Body | L / M / S | 段落文本、描述 |
| Label | L / M / S | 按钮、芯片、标题 |

每个样式都有标记：`-font`、`-weight`、`-size`、`-line-height`、`-tracking`
加上 15 个 **强调** 变体（更高的权重）通过 `--md-sys-typescale-emphasized-*`

完整详情：`references/typography-and-shape.md`

### 形状标记 (`--md-sys-shape-corner-*`)
| 标记 | 值 | 示例组件 |
|-------|-------|-------------------|
| `none` | 0dp | — |
| `extra-small` | 4dp | 芯片、snackbars |
| `small` | 8dp | 文本字段、菜单 |
| `medium` | 12dp | 卡片 |
| `large` | 16dp | FABs、导航抽屉 |
| `large-increased` | 20dp | (富有表现力) |
| `extra-large` | 28dp | 对话框、底部表单 |
| `extra-large-increased` | 32dp | (富有表现力) |
| `extra-extra-large` | 48dp | (富有表现力) |
| `full` | 9999px | 按钮、芯片、徽章 |

### 提升级别
| 级别 | DP | 色调偏移 | 使用 |
|-------|-----|-------------|-----|
| 0 | 0dp | 无 | 平面表面、大多数组件处于静止状态 |
| 1 | 1dp | +5% 主色 | 提升的卡片、模态表单 |
| 2 | 3dp | +8% 主色 | 菜单、导航栏、滚动应用栏 |
| 3 | 6dp | +11% 主色 | FAB、对话框、搜索、日期/时间选择器 |
| 4 | 8dp | +12% 主色 | (悬停/焦点增加仅) |
| 5 | 12dp | +14% 主色 | (悬停/焦点增加仅) |

MD3 中的提升通过 **色调表面颜色** 传达，而不是阴影。阴影仅在需要时用于额外的保护以防止繁忙的背景。

### 运动
MD3 富有表现力（2025 年 5 月）引入了 **基于弹簧的运动物理** 的组件。传统的缓动/持续时间系统仍然用于 **过渡**（进入/退出/共享轴）：

| 缓动 | 持续时间 | 过渡类型 |
|--------|----------|-----------------|
| Emphasized | 500ms | 在屏幕上开始和结束 |
| Emphasized decelerate | 400ms | 进入屏幕 |
| Emphasized accelerate | 200ms | 离开屏幕 |
| Standard | 300ms | 在屏幕上开始和结束（实用） |
| Standard decelerate | 250ms | 进入屏幕 (实用) |
| Standard accelerate | 200ms | 离开屏幕 (实用) |

CSS 缓动值：
- Emphasized: `cubic-bezier(0.2, 0, 0, 1)`
- Emphasized decelerate: `cubic-bezier(0.05, 0.7, 0.1, 1)`
- Emphasized accelerate: `cubic-bezier(0.3, 0, 0.8, 0.15)`
- Standard: `cubic-bezier(0.2, 0, 0, 1)`
- Standard decelerate: `cubic-bezier(0, 0, 0, 1)`
- Standard accelerate: `cubic-bezier(0.3, 0, 1, 1)`

## 组件快速参考

| 组件 | Web 元素 | 关键变体 | 类别 |
|-----------|------------|--------------|----------|
| Button | `md-filled-button`, `md-outlined-button`, `md-text-button`, `md-elevated-button`, `md-filled-tonal-button` | 填充、轮廓、文本、提升、色调；5 个尺寸 (XS–XL)；切换 | 操作 |
| Button group | `md-button-group` | 标准、连接 | 操作 |
| Extended FAB | `md-extended-fab` | 表面、主色、次要色、三级色 | 操作 |
| FAB | `md-fab` | 小、中、大 | 操作 |
| FAB menu | — | — | 操作 |
| Icon button | `md-icon-button`, `md-filled-icon-button`, `md-filled-tonal-icon-button`, `md-outlined-icon-button` | 标准、填充、填充色调、轮廓 | 操作 |
| Segmented button | — | 单选、多选 | 操作 |
| Split button | — | — | 操作 |
| Badge | — | 小 (点)、大 (计数) | 通信 |
| Loading indicator | — | 线性、圆形 | 通信 |
| Progress indicator | `md-linear-progress`, `md-circular-progress` | 线性、圆形；确定/不确定 | 通信 |
| Snackbar | — | 单行、两行、操作 | 通信 |
| Tooltip | — | 普通、丰富 | 通信 |
| Card | — | 填充、轮廓、提升 | 包含 |
| Carousel | — | 多浏览、无包含、英雄 | 包含 |
| Dialog | `md-dialog` | 基本、全屏 | 包含 |
| Bottom sheet | — | 标准、模态 | 表单 |
| Side sheet | — | 标准、模态 | 表单 |
| Divider | `md-divider` | 全宽、嵌入 | 包含 |
| Checkbox | `md-checkbox` | — | 输入 |
| Chips | `md-chip-set`, `md-assist-chip`, `md-filter-chip`, `md-input-chip`, `md-suggestion-chip` | 辅助、过滤、输入、建议 | 输入 |
| Date picker | — | 锚定、模态、范围 | 输入 |
| Menu | `md-menu`, `md-menu-item` | — | 输入 |
| Radio button | `md-radio` | — | 输入 |
| Slider | `md-slider` | 连续、离散、范围 | 输入 |
| Switch | `md-switch` | 带图标/不带图标 | 输入 |
| Text field | `md-filled-text-field`, `md-outlined-text-field` | 填充、轮廓 | 输入 |
| Time picker | — | 锚定、模态 | 输入 |
| App bar (top) | — | 居中对齐、小、中、大 | 导航 |
| Navigation bar | `md-navigation-bar` | — | 导航 |
| Navigation drawer | `md-navigation-drawer` | 标准、模态 | 导航 |
| Navigation rail | — | — | 导航 |
| Search | — | 搜索栏、搜索视图 | 导航 |
| Tabs | `md-tabs`, `md-primary-tab`, `md-secondary-tab` | 主色、次要色 | 导航 |
| Toolbar | — | — | 导航 |
| List | `md-list`, `md-list-item` | 一行、两行、三行 | 数据显示 |

**注意**：Web 元素标记为 `—` 的组件尚未在 `@material/web` 中提供实现。使用标准 HTML 和 CSS 自定义属性。**Compose** 映射和示例位于 `references/component-catalog.md`。

完整组件详情与代码示例：`references/component-catalog.md`

## Jetpack Compose (主要)

使用 **`androidx.compose.material3`** 与 `MaterialTheme` 和 Material 3 可组合组件 (`Scaffold`, `Button`, `NavigationBar`, 顶部应用栏等)。

- **主题**：`MaterialTheme(colorScheme = …, typography = …, shapes = …)`。在 **Android 12+ (API 31+)** 上优先使用 `dynamicLightColorScheme` / `dynamicDarkColorScheme` 以获取动态颜色；否则使用 `lightColorScheme` / `darkColorScheme` 或从 Material Theme Builder 生成的主题代码。
- **自适应 UI**：窗口大小类别、列表-详情和支持面板布局、折叠屏——查看 `references/layout-and-responsive.md` 和 `references/navigation-patterns.md`。
- **边缘到边缘 & insets**：使用 `WindowInsets` / scaffold 填充来布局内容，以便条栏和 IME 正确行为——查看 `references/layout-and-responsive.md`。
- **实验性 API**：一些 Material 3 API 需要要求 `@OptIn(ExperimentalMaterial3Api::class)` 或富有表现力的选择入——匹配您的 BOM 和编译器。

```kotlin
MaterialTheme(
    colorScheme = colorScheme, // 来自 dynamicLightColorScheme / lightColorScheme / 等.
    typography = Typography(),
    shapes = Shapes(),
) {
    // M3 内容 — 优先参考 Scaffold, 导航, 文本字段
}
```

## Web (有限): @material/web

**重要提示**：根据 [Material Design 3 for Web](https://m3.material.io/develop/web)，**Material Web Components 处于维护模式**，**M3 富有表现力在 Web 上未实现**。在适当的情况下使用 `@material/web` 以获取基于标记的 Web UI，但不要将其视为当前富有表现力功能的 Compose 等价物。

### 设置

```bash
npm install @material/web
```

### 单独导入组件

始终单独导入您使用的组件——导入整个包会膨胀捆绑包：

```javascript
// 好 — 单独导入
import '@material/web/button/filled-button.js';
import '@material/web/button/outlined-button.js';
import '@material/web/textfield/outlined-text-field.js';
import '@material/web/icon/icon.js';

// 坏 — 绝对不要这样做
import '@material/web'; // 导入所有内容
```

### 基本用法

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <link href="https://fonts.googleapis.com/css2?family=Roboto+Flex:wght@400;500;700&display=swap" rel="stylesheet">
  <link href="https://fonts.googleapis.com/icon?family=Material+Symbols+Outlined" rel="stylesheet">
</head>
<body>
  <md-filled-button>Get started</md-filled-button>
  <md-outlined-text-field label="Email" type="email"></md-outlined-text-field>

  <script type="module">
    import '@material/web/button/filled-button.js';
    import '@material/web/textfield/outlined-text-field.js';
  </script>
</body>
</html>
```

### 使用 CSS 自定义属性进行主题设置

通过在 `:root` 或任何祖先上设置 CSS 自定义属性来应用自定义主题：

```css
:root {
  /* 颜色方案 (使用 @material/material-color-utilities 生成) */
  --md-sys-color-primary: #6750A4;
  --md-sys-color-on-primary: #FFFFFF;
  --md-sys-color-primary-container: #EADDFF;
  --md-sys-color-on-primary-container: #21005D;
  --md-sys-color-secondary: #625B71;
  --md-sys-color-on-secondary: #FFFFFF;
  --md-sys-color-secondary-container: #E8DEF8;
  --md-sys-color-on-secondary-container: #1D192B;
  --md-sys-color-surface: #FEF7FF;
  --md-sys-color-on-surface: #1D1B20;
  --md-sys-color-surface-container: #F3EDF7;
  --md-sys-color-outline: #79747E;
  --md-sys-color-outline-variant: #CAC4D0;

  /* 排版 */
  --md-sys-typescale-body-large-font: 'Roboto Flex', sans-serif;
  --md-sys-typescale-body-large-size: 1rem;
  --md-sys-typescale-body-large-weight: 400;
  --md-sys-typescale-body-large-line-height: 1.5rem;

  /* 形状 */
  --md-sys-shape-corner-full: 9999px;
  --md-sys-shape-corner-medium: 12px;
}
```

### 组件级覆盖

针对特定自定义进行单个组件标记覆盖：

```css
md-filled-button {
  --md-filled-button-container-color: var(--md-sys-color-primary);
  --md-filled-button-label-text-color: var(--md-sys-color-on-primary);
  --md-filled-button-container-shape: var(--md-sys-shape-corner-full);
  --md-filled-button-container-height: 40px;
}

md-outlined-text-field {
  --md-outlined-text-field-container-shape: var(--md-sys-shape-corner-small);
  --md-outlined-text-field-focus-outline-color: var(--md-sys-color-primary);
}
```

### 暗色主题

通过在类或媒体查询上覆盖颜色标记来应用暗色主题：

```css
@media (prefers-color-scheme: dark) {
  :root {
    --md-sys-color-primary: #D0BCFF;
    --md-sys-color-on-primary: #381E72;
    --md-sys-color-primary-container: #4F378B;
    --md-sys-color-on-primary-container: #EADDFF;
    --md-sys-color-surface: #141218;
    --md-sys-color-on-surface: #E6E0E9;
    --md-sys-color-surface-container: #211F26;
    --md-sys-color-outline: #938F99;
    --md-sys-color-outline-variant: #49454F;
  }
}
```

完整主题指南：`references/theming-and-dynamic-color.md`

## 常见模式

### 应用外壳

标准 MD3 应用，具有响应式导航 + 顶部应用栏 + 内容区域：

```html
<div class="md3-app">
  <nav class="md3-nav-rail" aria-label="Main navigation">
    <!-- 中等及以上屏幕的导航轨道 -->
    <md-fab size="small" aria-label="Compose">
      <md-icon slot="icon">edit</md-icon>
    </md-fab>
    <md-navigation-bar>
      <md-navigation-tab label="Home">
        <md-icon slot="active-icon">home</md-icon>
        <md-icon slot="inactive-icon">home</md-icon>
      </md-navigation-tab>
      <md-navigation-tab label="Search">
        <md-icon slot="active-icon">search</md-icon>
        <md-icon slot="inactive-icon">search</md-icon>
      </md-navigation-tab>
    </md-navigation-bar>
  </nav>
  <main class="md3-content">
    <header class="md3-top-app-bar">
      <h1 class="md3-top-app-bar__title" style="font: var(--md-sys-typescale-title-large)">
        Page Title
      </h1>
    </header>
    <div class="md3-body">
      <!-- 内容在这里 -->
    </div>
  </main>
</div>
```

```css
.md3-app {
  display: flex;
  min-height: 100vh;
  background: var(--md-sys-color-surface);
  color: var(--md-sys-color-on-surface);
}

.md3-nav-rail {
  width: 80px;
  background: var(--md-sys-color-surface);
  border-right: 1px solid var(--md-sys-color-outline-variant);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 12px;
  gap: 12px;
}

.md3-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.md3-top-app-bar {
  height: 64px;
  padding: 0 16px;
  display: flex;
  align-items: center;
  background: var(--md-sys-color-surface);
}

.md3-body {
  padding: 24px;
  flex: 1;
}

/* 响应式：在小屏幕上切换到底部导航 */
@media (max-width: 599px) {
  .md3-app { flex-direction: column; }
  .md3-nav-rail {
    order: 1;
    width: 100%;
    flex-direction: row;
    justify-content: center;
    border-right: none;
    padding: 0;
  }
}
```

### 卡片网格

```html
<div class="md3-card-grid">
  <div class="md3-card md3-card--outlined">
    <img src="image.jpg" alt="Description" class="md3-card__media">
    <div class="md3-card__content">
      <h3 style="font: var(--md-sys-typescale-title-medium)">Card Title</h3>
      <p style="font: var(--md-sys-typescale-body-medium); color: var(--md-sys-color-on-surface-variant)">
        Supporting text for this card.
      </p>
    </div>
    <div class="md3-card__actions">
      <md-text-button>Learn more</md-text-button>
      <md-filled-tonal-buttonActionCode
```

```css
.md3-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.md3-card--outlined {
  border: 1px solid var(--md-sys-color-outline-variant);
  border-radius: var(--md-sys-shape-corner-medium, 12px);
  background: var(--md-sys-color-surface);
  overflow: hidden;
}

.md3-card__content { padding: 16px; }
.md3-card__actions { padding: 8px 16px 16px; display: flex; gap: 8px; justify-content: flex-end; }
.md3-card__media { width: 100%; aspect-ratio: 16/9; object-fit: cover; }
```

### 表单布局

```html
<form class="md3-form">
  <md-outlined-text-field label="Full name" required></md-outlined-text-field>
  <md-outlined-text-field label="Email" type="email" required></md-outlined-text-field>
  <md-outlined-text-field label="Message" type="textarea" rows="4"></md-outlined-text-field>
  <div class="md3-form__actions">
    <md-text-button type="reset">Cancel</md-text-button>
    <md-filled-button type="submit">Submit</md-filled-button>
  </div>
</form>
```

```css
.md3-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 560px;
}

.md3-form__actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  margin-top: 8px;
}
```

更多模式：`references/navigation-patterns.md`, `references/layout-and-responsive.md`

## 反模式

**在实现 MD3 时，绝对不要这样做**：

- **混合 MD2 和 MD3 库**：不要在 `@material/mdc-*`（MD2）和 `@material/web`（MD3）之间使用。它们具有不兼容的 API 和样式。
- **硬编码颜色**：始终使用 `var(--md-sys-color-*)` 标记，不要使用原始的十六进制/rgb 值。硬编码颜色会破坏动态主题、暗色模式和对比度调整。
- **忽略色调配对**：只组合预期的颜色对（例如，`primary` + `on-primary`，`surface-container` + `on-surface`）。随意的组合会破坏动态颜色和高对比度模式下的对比度。
- **使用 `outline` 作为分隔符**：使用 `outline-variant` 作为分隔符。`outline` 用于重要边界（如文本字段边框）。
- **导入所有 @material/web**：始终单独导入组件模块。桶导入包含每个组件，会膨胀捆绑包。
- **直接使用 `border-radius`**：使用形状标记 (`var(--md-sys-shape-corner-medium)`)，以便形状与主题保持一致。
- **默认情况下使用阴影表示提升**：MD3 通过色调表面颜色传达提升，而不是阴影。仅在需要时使用阴影以防止繁忙的背景对元素造成额外保护。
- **应用前端设计“避免 Roboto”规则**：在 **Android** 上，**Roboto** 是默认的 Material 字体——**web** 通常使用 Roboto 或 Roboto Flex 与 MD3 标记一起使用。仅在故意自定义类型规模时才替换。
- **假设 SSR 兼容性**：`@material/web` 使用 Web Components (自定义元素) 需要 JavaScript 才能渲染。如果没有额外的 hydration 策略，它们在 SSR 中不会生成有意义的 HTML。
- **忽略折叠屏和大屏幕**：MD3 设计用于所有屏幕尺寸。不要仅发送手机优先布局——使用规范布局、600dp+ 的多面板，并在折叠屏/平板电脑模拟器上测试。不要在折叠/铰链上放置任何交互内容。
- **拉伸内容以填充宽屏幕**：在 1200dp+ 和 1600dp+ 窗口中，将内容约束到最大宽度（840–1040dp）。无限宽度的文本行难以阅读。
