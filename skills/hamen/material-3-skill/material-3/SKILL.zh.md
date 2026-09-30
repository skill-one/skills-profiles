---
name: material-3
description: 实现 Google 的 Material Design 3 (Material You) UI 系统。主要：Jetpack Compose Material3 (MaterialTheme, 组件, 自适应布局)。也包括 Flutter 和有限的 Web (@material/web, 维护模式)。涵盖主题、30+ 组件、布局、主题定制、M3 表达式（平台矩阵）和可访问性。使用场景：当提到 "material design"、"MD3"、"material you"、"Jetpack Compose"、"MaterialTheme"、"material component"、"md3 button" 时。
---

# Material Design 3

本技能指导实现 Google 的 Material Design 3 (MD3) — 一种个性化、自适应、富有表现力的设计系统。MD3 使用动态颜色、色调表面、圆角形状和基于弹簧的运动，创建出感觉生动且个性化的 UI。

## 哲学

MD3 基于三个原则构建：
- **个性化**：动态颜色适应用户的壁纸或内容。主题是个性化的，而非一刀切。
- **自适应**：布局跨越 5 个窗口尺寸类别进行转换。组件会响应式地调整大小、重新定位和改变形态。
- **富有表现力**：形状变形、弹簧物理效果和强调的排版，在牺牲可用性的前提下，创造出令人愉悦的时刻。

## 当前更新：Google I/O 2026

Material 的 [Google I/O 2026 更新](https://m3.material.io/blog/whats-new-at-io26) 强调了 **优先使用 Compose** 的 Android 路径，并扩展了富有表现力/自适应的指导：
- **Material Android 优先使用 Compose**：对于新的 Android 工作，优先使用 Jetpack Compose Material3 获取最新的组件、富有表现力的 API、自适应骨架和 Styles API 集成。在现有应用中可能仍需要 Android Views，但它们不应被视为新 Material 3 实现的默认路径。
- **富有表现力的布局系统**：使用富有表现力的布局骨架来适应手机、桌面、折叠屏、手表、XR 和其他空间形态。从自适应骨架/窗口尺寸类别开始，而不是固定的手机优先布局。
- **8dp 间距系统**：应用间距标记到边距、填充和间隙，以便布局和组件可以编程方式适应设备类型和密度。
- **新的/更新的富有表现力的组件**：列表、菜单、搜索和搜索应用栏有更新的富有表现力的指导，Jetpack Compose 是主要实现目标。
- **手表和 XR**：手表强调基于物理的运动、弧形文本和边缘紧贴容器。XR 强调空间面板和基于深度的提升。

**与 MD2 的主要区别：**
- 色调表面取代了提升阴影作为主要的深度提示
- 动态颜色从单一种子颜色生成完整的配色方案
- 默认全圆角（不是微圆角）
- 基于弹簧的运动物理取代了组件的固定缓动曲线
- 3 级用户控制的对比度（标准/中等/高）

**与前端设计技能的关系：**
当两个技能都激活时，MD3 提供设计系统（标记、组件、布局规则），而前端设计在这些限制内提供创意指导。MD3 规则优先于组件结构和标记使用。注意：Roboto/Roboto Flex 在 MD3 中确实是正确的默认字体 — 当实现 MD3 时，前端设计的指导避免使用 Roboto 不适用。

## 决策树

**你在构建什么？**
```
完整应用骨架        → 查看 "常见模式：应用壳" + references/layout-and-responsive.md
单个组件            → 查看 "组件快速参考" 表格 → references/component-catalog.md
自定义主题          → 查看 references/theming-and-dynamic-color.md
表单/输入布局      → 查看 references/component-catalog.md § 输入组件
导航结构          → 查看 references/navigation-patterns.md
数据展示            → 查看 references/component-catalog.md § 数据展示
```

**在哪个平台？**
```
Jetpack Compose        → 主要：androidx.compose.material3, MaterialTheme, references/*
Flutter                  → useMaterial3: true in ThemeData, ColorScheme.fromSeed()
Web (vanilla JS)         → @material/web (有限；维护模式) + CSS 自定义属性
Web (React/Vue/Svelte)   → CSS 自定义属性 + 包装组件（没有官方 React 库）
Web (CSS-only)           → MD3 标记值作为 CSS 自定义属性（没有 <md-*> 元素）
```

## 设计标记系统

所有 MD3 标记使用 `md.sys` 命名空间。**Jetpack Compose** 将角色映射到 `MaterialTheme.colorScheme`、`MaterialTheme.typography` 和 `MaterialTheme.shapes`（与规范相同的语义角色）。**在 Web 上**，这些映射到 CSS 自定义属性 (`--md-sys-*`)：

### 颜色标记 (`--md-sys-color-*`)
| 标记 | 目的 |
|-------|---------|
| `primary` | 高强调填充、文本、图标对表面 |
| `on-primary` | 主色上的文本/图标 |
| `primary-container` | 关键组件的突出填充（FAB 等） |
| `on-primary-container` | 主色容器上的文本/图标 |
| `secondary` / `on-secondary` | 较不突出的强调 |
| `secondary-container` / `on-secondary-container` | 退缩组件（色调按钮） |
| `tertiary` / `on-tertiary` | 对比强调 |
| `tertiary-container` / `on-tertiary-container` | 互补容器 |
| `error` / `on-error` | 错误状态（静态 — 不随动态颜色变化） |
| `error-container` / `on-error-container` | 错误容器填充 |
| `surface` | 默认背景 |
| `on-surface` | 任何表面上的文本/图标 |
| `on-surface-variant` | 表面上的低强调文本/图标 |
| `surface-container-lowest` | 最低强调容器 |
| `surface-container-low` | 低强调容器 |
| `surface-container` | 默认容器（导航区域） |
| `surface-container-high` | 高强调容器 |
| `surface-container-highest` | 最高强调容器 |
| `surface-dim` / `surface-bright` | 跨亮/暗保持相对亮度 |
| `inverse-surface` / `inverse-on-surface` / `inverse-primary` | 对比元素（snackbars） |
| `outline` | 重要边界（文本字段边框） |
| `outline-variant` | 装饰元素（分隔符） |

完整细节：`references/color-system.md`

### 字体排版标记 (`--md-sys-typescale-*`)
| 尺寸 | 尺寸 | 使用 |
|-------|-------|-----|
| Display | L / M / S | 英雄文本、大数字 |
| Headline | L / M / S | 区块标题 |
| Title | L / M / S | 较小的标题、卡片标题 |
| Body | L / M / S | 段落文本、描述 |
| Label | L / M / S | 按钮、芯片、标题 |

每种样式都有标记：`-font`、`-weight`、`-size`、`-line-height`、`-tracking`
加上 15 个 **强调** 变体（更高权重）通过 `--md-sys-typescale-emphasized-*`

完整细节：`references/typography-and-shape.md`

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
| 4 | 8dp | +12% 主色 | (悬停/聚焦增加仅) |
| 5 | 12dp | +14% 主色 | (悬停/聚焦增加仅) |

MD3 中的提升通过 **色调表面颜色** 传达，而不是阴影。仅在需要时使用阴影以防止背景杂乱。

### 运动
MD3 富有表现力（2025 年 5 月）引入了组件的 **基于弹簧的运动物理**。传统的缓动/持续时间系统仍用于 **过渡**（进入/退出/共享轴）：

| 缓动 | 持续时间 | 过渡类型 |
|--------|----------|-----------------|
| 强调 | 500ms | 屏幕上开始和结束 |
| 强调减速 | 400ms | 进入屏幕 |
| 强调加速 | 200ms | 离开屏幕 |
| 标准 | 300ms | 屏幕上开始和结束（实用） |
| 标准减速 | 250ms | 进入屏幕（实用） |
| 标准加速 | 200ms | 离开屏幕（实用） |

CSS 缓动值：
- 强调：`cubic-bezier(0.2, 0, 0, 1)`
- 强调减速：`cubic-bezier(0.05, 0.7, 0.1, 1)`
- 强调加速：`cubic-bezier(0.3, 0, 0.8, 0.15)`
- 标准：`cubic-bezier(0.2, 0, 0, 1)`
- 标准减速：`cubic-bezier(0, 0, 0, 1)`
- 标准加速：`cubic-bezier(0.3, 0, 1, 1)`

## 组件快速参考

| 组件 | Web 元素 | 关键变体 | 类别 |
|-----------|------------|--------------|----------|
| 按钮 | `md-filled-button`, `md-outlined-button`, `md-text-button`, `md-elevated-button`, `md-filled-tonal-button` | 填充、轮廓、文本、提升、色调；5 个尺寸（XS–XL）；切换 | 操作 |
| 按钮组 | `md-button-group` | 标准、连接 | 操作 |
| 扩展 FAB | `md-extended-fab` | 表面、主色、次色、三级 | 操作 |
| FAB | `md-fab` | 小、中、大 | 操作 |
| FAB 菜单 | — | — | 操作 |
| 图标按钮 | `md-icon-button`, `md-filled-icon-button`, `md-filled-tonal-icon-button`, `md-outlined-icon-button` | 标准、填充、填充色调、轮廓 | 操作 |
| 分段按钮 | — | 单选、多选 | 操作 |
| 分割按钮 | — | — | 操作 |
| 徽章 | — | 小（点）、大（计数） | 沟通 |
| 加载指示器 | — | 线性、圆形 | 沟通 |
| 进度指示器 | `md-linear-progress`, `md-circular-progress` | 线性、圆形；确定/不确定 | 沟通 |
| Snackbar | — | 单行、两行、操作 | 沟通 |
| 提示 | — | 简单、丰富 | 沟通 |
| 卡片 | — | 填充、轮廓、提升 | 包含 |
| 轮播 | — | 多浏览、无包含、英雄 | 包含 |
| 对话框 | `md-dialog` | 基本、全屏 | 包含 |
| 底部表单 | — | 标准、模态 | 表单 |
| 侧表单 | — | 标准、模态 | 表单 |
| 分隔符 | `md-divider` | 全宽、内嵌 | 包含 |
| 复选框 | `md-checkbox` | — | 输入 |
| 芯片 | `md-chip-set`, `md-assist-chip`, `md-filter-chip`, `md-input-chip`, `md-suggestion-chip` | 辅助、过滤、输入、建议 | 输入 |
| 日期选择器 | — | 锚定、模态、范围 | 输入 |
| 菜单 | `md-menu`, `md-menu-item` | — | 输入 |
| 单选按钮 | `md-radio` | — | 输入 |
| 滑块 | `md-slider` | 连续、离散、范围 | 输入 |
| 开关 | `md-switch` | 带图标/不带图标 | 输入 |
| 文本字段 | `md-filled-text-field`, `md-outlined-text-field` | 填充、轮廓 | 输入 |
| 时间选择器 | — | 锚定、模态 | 输入 |
| 应用栏（顶部） | — | 居中、小、中、大 | 导航 |
| 导航栏 | `md-navigation-bar` | — | 导航 |
| 导航抽屉 | `md-navigation-drawer` | 标准、模态 | 导航 |
| 导航轨道 | — | — | 导航 |
| 搜索 | — | 搜索栏、搜索视图 | 导航 |
| 标签 | `md-tabs`, `md-primary-tab`, `md-secondary-tab` | 主色、次色 | 导航 |
| 工具栏 | — | — | 导航 |
| 列表 | `md-list`, `md-list-item` | 单行、两行、三行 | 数据展示 |

**注意**：Web 元素标记为 `—` 的组件尚未在 @material/web 中实现。使用标准 HTML 和 CSS 自定义属性为这些组件提供支持。**Compose** 映射和示例位于 `references/component-catalog.md`。

完整组件细节和代码示例：`references/component-catalog.md`

## Jetpack Compose (主要)

使用 **`androidx.compose.material3`** 与 `MaterialTheme` 和 Material 3 可组合组件 (`Scaffold`, `Button`, `NavigationBar`, 顶部应用栏等)。

- **主题**：`MaterialTheme(colorScheme = …, typography = …, shapes = …)`。在 **Android 12+ (API 31+)** 上优先使用 `dynamicLightColorScheme` / `dynamicDarkColorScheme` 当动态颜色需要时；否则 `lightColorScheme` / `darkColorScheme` 或从 Material Theme Builder 生成的主题代码。
- **自适应 UI**：窗口尺寸类别、列表-详情和支持面板布局、折叠屏 — 查看 `references/layout-and-responsive.md` 和 `references/navigation-patterns.md`。
- **边缘到边缘 & 插入**：使用 `WindowInsets` / scaffold 填充布局内容，以便条和 IME 正确行为 — 查看 `references/layout-and-responsive.md`。
- **实验性 API**：一些 Material 3 API 需要 `@OptIn(ExperimentalMaterial3Api::class)` 或富有表现力的选择入 — 匹配您的 BOM 和编译器。

```kotlin
MaterialTheme(
    colorScheme = colorScheme, // 从 dynamicLightColorScheme / lightColorScheme / 等
    typography = Typography(),
    shapes = Shapes(),
) {
    // M3 内容 — 优先参考 Scaffold、导航、文本字段
}
```

## Web (有限)：@material/web

**重要**：根据 [Material Design 3 for Web](https://m3.material.io/develop/web)，**Material Web 组件处于维护模式**，**Web 上的 MD3 富有表现力未实现**。在适当的情况下使用 `@material/web` 为 Web UI 提供标记支持，但不要将其视为当前富有表现力功能的 Compose 等价物。

### 设置

```bash
npm install @material/web
```

### 单独导入组件

始终导入您使用的组件 — 导入整个包会膨胀捆绑包：

```javascript
// 好 — 单独导入
import '@material/web/button/filled-button.js';
import '@material/web/button/outlined-button.js';
import '@material/web/textfield/outlined-text-field.js';
import '@material/web/icon/icon.js';

// 坏 — 绝对不要这样做
import '@material/web'; // 导入所有内容
```

### 基本使用

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

### 使用 CSS 自定义属性进行主题

通过在 `:root` 或任何祖先上设置 CSS 自定义属性来应用自定义主题：

```css
:root {
  /* 配色方案（使用 @material/material-color-utilities 生成） */
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

  /* 字体排版 */
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

覆盖单个组件标记以进行特定自定义：

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

通过在类或媒体查询上覆盖颜色标记应用暗色主题：

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

完整的主题指南：`references/theming-and-dynamic-color.md`

## 常见模式

### 应用外壳

标准的 MD3 应用，具有响应式导航 + 顶部应用栏 + 内容区域：

```html
<div class="md3-app">
  <nav class="md3-nav-rail" aria-label="主导航">
    <!-- 中等及以上屏幕的导航轨道 -->
    <md-fab size="small" aria-label="撰写">
      <md-icon slot="icon">edit</md-icon>
    </md-fab>
    <md-navigation-bar>
      <md-navigation-tab label="首页">
        <md-icon slot="active-icon">home</md-icon>
        <md-icon slot="inactive-icon">home</md-icon>
      </md-navigation-tab>
      <md-navigation-tab label="搜索">
        <md-icon slot="active-icon">search</md-icon>
        <md-icon slot="inactive-icon">search</md-icon>
      </md-navigation-tab>
    </md-navigation-bar>
  </nav>
  <main class="md3-content">
    <header class="md3-top-app-bar">
      <h1 class="md3-top-app-bar__title" style="font: var(--md-sys-typescale-title-large)">
        页面标题
      </h1>
    </header>
    <div class="md3-body">
      <!-- 内容在此处 -->
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

/* 响应式：在紧凑模式下切换到底部导航 */
@media (max-width: 599px) {
  .md3-app { flex-direction: column; }
  .md3-nav-rail {
    order: 1;
    width: 100%;
    flex-direction: row;
    justify-content: center;
    border-right: none;
    border-top: 1px solid var(--md-sys-color-outline-variant);
    padding: 0;
  }
}
```

### 卡片网格

```html
<div class="md3-card-grid">
  <div class="md3-card md3-card--outlined">
    <img src="image.jpg" alt="描述" class="md3-card__media">
    <div class="md3-card__content">
      <h3 style="font: var(--md-sys-typescale-title-medium)">卡片标题</h3>
      <p style="font: var(--md-sys-typescale-body-medium); color: var(--md-sys-color-on-surface-variant)">
        此卡片的辅助文本。
      </p>
    </div>
    <div class="md3-card__actions">
      <md-text-button>了解更多</md-text-button>
      <md-filled-tonal-button>操作</md-filled-tonal-button>
    </div>
  </div>
</div>
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
  <md-outlined-text-field label="全名" required></md-outlined-text-field>
  <md-outlined-text-field label="邮箱" type="email" required></md-outlined-text-field>
  <md-outlined-text-field label="消息" type="textarea" rows="4"></md-outlined-text-field>
  <div class="md3-form__actions">
    <md-text-button type="reset">取消</md-text-button>
    <md-filled-button type="submit">提交</md-filled-button>
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

更多模式：`references/navigation-patterns.md`，`references/layout-and-responsive.md`

## 反模式

在实现 MD3 时，切勿这样做：

- **混合 MD2 和 MD3 库**：不要同时使用 `@material/mdc-*`（MD2）和 `@material/web`（MD3）。它们具有不兼容的 API 和样式。
- **硬编码颜色**：始终使用 `var(--md-sys-color-*)` 令牌，不要使用原始的十六进制/rgb 值。硬编码的颜色会破坏动态主题、暗黑模式和对比度调整。
- **忽略色调配对**：仅在预期配对中组合颜色（例如，`primary` + `on-primary`，`surface-container` + `on-surface`）。随意的组合会在动态颜色和高对比度模式下破坏对比度。
- **使用 `outline` 作为分隔符**：使用 `outline-variant` 作为分隔符。`outline` 用于重要边界，如文本字段边框。
- **导入所有 @material/web**：始终导入单个组件模块。包导入包含每个组件并破坏包大小。
- **直接使用 `border-radius`**：使用形状令牌 (`var(--md-sys-shape-corner-medium)`)，以便形状与主题保持一致。
- **默认使用阴影表示提升**：MD3 通过色调表面颜色而不是阴影来传达提升。仅在元素需要与繁忙背景额外分离时才添加阴影。
- **应用前端设计“避免 Roboto”规则**：在**Android**上，**Roboto** 是默认的 Material 字体；**Web** 通常使用 Roboto 或 Roboto Flex 与 MD3 令牌。仅在有意自定义类型比例时才替换。
- **假设 SSR 兼容性**：`@material/web` 使用 Web Components（自定义元素），需要 JavaScript 才能渲染。如果没有额外的 hydration 策略，它们在 SSR 中不会产生有意义的 HTML。
- **忽略折叠屏和大屏幕**：MD3 设计用于所有屏幕尺寸。不要仅发送手机布局——使用规范布局、600dp+ 的多面板，并在折叠屏/平板电脑模拟器上测试。不要将交互式内容跨越折叠/铰链。
- **拉伸内容以填充宽屏幕**：在大屏幕（1200dp+）和超大屏幕（1600dp+）上，将内容约束在最大宽度（840–1040dp）内。无限宽度的文本行难以阅读。

## 平台说明

### Flutter
```dart
MaterialApp(
  theme: ThemeData(
    useMaterial3: true,
    colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
  ),
);
```

### Jetpack Compose
见**[Jetpack Compose (primary)](#jetpack-compose-primary)**。仅在 `Build.VERSION.SDK_INT >= Build.VERSION_CODES.S` 且动态颜色启用时使用 `LocalContext.current` 与 `dynamicLightColorScheme` / `dynamicDarkColorScheme`；否则提供静态的亮/暗方案。

### 组件名称映射
| 概念 | Web | Flutter | Compose |
|------|-----|---------|---------|
| 填充按钮 | `md-filled-button` | `FilledButton` | `Button` |
| 带边框文本字段 | `md-outlined-text-field` | `OutlinedTextField` | `OutlinedTextField` |
| FAB | `md-fab` | `FloatingActionButton` | `FloatingActionButton` |
| 导航栏 | `md-navigation-bar` | `NavigationBar` | `NavigationBar` |
| 开关 | `md-switch` | `Switch` | `Switch` |

## M3 表达式 (2025 年 5 月)

表达式更新增加了视觉丰富性，同时保持了可用性。**平台差异**——不要假设一个堆栈实现了所有功能。

| 功能 | Jetpack Compose | Flutter | Web (`@material/web`) |
|------|-----------------|---------|------------------------|
| 表达式布局骨架 / 自适应布局 | Compose-first via Material3 自适应 API 和窗口大小类 | 使用 Flutter 自适应/布局原语 | CSS/容器查询/手动布局；无 Material Web 对等物 |
| 8dp 间距系统 | 使用设计令牌 / `Dp` 间距常量；保持边距、填充和间隙自适应 | 使用主题间距常量 | CSS 自定义属性 / 设计令牌 |
| 表达式列表、菜单、搜索、搜索应用栏 | 主要目标根据当前 Material 指南；检查 BOM 和选择项 | 检查当前 Flutter Material 文档 | 规范对齐的自定义实现；`@material/web` 仅维护 |
| 弹簧 / 动画物理 | 在 Material 3 中受支持（见 `MotionScheme`，根据 BOM 的表达式 API） | 因 Flutter Material 版本而异 | **不**在 Material Web 中；使用缓动/持续时间或自定义动画 |
| 强调性排版 | 通过主题 / 类型比例 | 通过主题 | 令牌/CSS 仅；无完整的表达式组件集 |
| 形状变形 | Compose-first 在 Google 的表达式发布中 | 检查当前 Flutter 文档 | **不**在 `@material/web` 中 |
| 新按钮大小 (XS–XL)、切换 | 遵循 Compose Material3 组件 | 遵循 Flutter MD3 | 高度/CSS 近似 |
| 额外角落令牌（例如 large-increased） | `MaterialTheme.shapes` / 令牌 | 主题形状 | CSS `--md-sys-shape-*` |
| 3 对比度级别 | 方案构建器 / 系统 | 插件 / 手动 | JS 工具中的 `SchemeContent` 对比度参数 |
| 手表 / XR 形状 | 在可用时使用 Compose/Wear/XR 特定指南 | 平台特定 | Web/空间 UI 自定义实现 |

**Web**：[Material Web 仅维护；M3 表达式不在 Web 上](https://m3.material.io/develop/web)。使用 CSS 缓动/持续时间令牌作为运动的回退，而不是弹簧对等物。

**遗留缓动/持续时间** 对于 **过渡**（进入/退出/共享轴）仍然有效，其中规范仍然引用它们；见下方的运动表。

## MD3 合规性审计

当使用 `audit` 作为参数调用时（例如，`/material-3 audit`），或在要求审计/审查 MD3 合规性时，分析目标应用或页面并生成合规性报告。

### 审计步骤

1. **确定目标**：用户提供 URL（使用浏览器工具检查）、文件路径（读取源代码）或正在运行的应用。
2. **检查以下类别** 并为每个类别评分 0–10：

| 类别 | 检查内容 |
|------|---------|
| **颜色令牌** | **Web**：`--md-sys-color-*` / 生成的 CSS。**Compose**：`MaterialTheme.colorScheme` 角色（没有理由为表面使用 `Color(...)`）。正确的色调配对（`onX` 在 `X` 上）。暗黑主题。**Flutter**：`ColorScheme` 角色。 |
| **排版** | MD3 类型比例：**Compose** `MaterialTheme.typography`；**web** 排版令牌；正确的角色（显示、标题、标题、正文、标签）。 |
| **形状** | **Compose** `MaterialTheme.shapes` / 组件 `Shape`；**web** `var(--md-sys-shape-*)`。按钮：完整；卡片：中等；避免魔法数字。 |
| **提升** | 色调提升（`Surface` 色调/阴影按适用）。**Web**：相关悬停/焦点。 |
| **组件** | **Compose**：Material3 组合组件（`Button`、`Scaffold` 等）。**Web**：`@material/web` 或规范对齐的 HTML/CSS。正确的变体。 |
| **布局** | 规范布局；**Compose** 窗口大小类 / 自适应 API；在大宽度上可读的最大宽度；避免折叠铰链。 |
| **导航** | 条 / 轨道 / 抽屉 / 抽屉+**Compose** `NavHost` 模式按大小类；适用时的预测后退。 |
| **运动** | **Compose** `MotionScheme` / 表达式 API 在使用时；过渡可能仍使用缓动/持续时间。**Web**：CSS 运动令牌回退。 |
| **无障碍** | MD3 角色有助于，但**验证对比度**：UI 组件通常需要 **3:1** 大文本/边框和 **4.5:1** 普通文本（WCAG 2.x）。TalkBack/语义（Compose），焦点顺序，触摸目标（~48dp）。**Web**：ARIA，键盘。 |
| **主题** | **Compose**：`MaterialTheme` + 亮/暗/动态按设计使用。**Web**：`:root` 或子树上的 CSS 自定义属性。**Flutter**：`ThemeData` + `ColorScheme`。 |

3. **生成报告**：

```
# MD3 合规性审计报告

目标：[URL 或文件路径]
日期：[日期]
总分：[X/100]

## 各类别得分
| 类别       | 得分 | 状态 |
|------------|------|------|
| 颜色令牌   | X/10  | [通过/警告/失败] |
| 排版       | X/10  | [通过/警告/失败] |
| 形状       | X/10  | [通过/警告/失败] |
| 提升       | X/10  | [通过/警告/失败] |
| 组件       | X/10  | [通过/警告/失败] |
| 布局       | X/10  | [通过/警告/失败] |
| 导航       | X/10  | [通过/警告/失败] |
| 运动       | X/10  | [通过/警告/失败] |
| 无障碍     | X/10  | [通过/警告/失败] |
| 主题       | X/10  | [通过/警告/失败] |

## 严重问题
[列出得分为 0-3 的项目，带具体文件:行号引用和修复建议]

## 警告
[列出得分为 4-6 的项目，带建议]

## 通过
[列出得分为 7-10 的项目，带做得好的说明]

## 推荐修复（优先级顺序）
1. [最影响的修复首先]
2. ...
```

### 审计方法

**对于实时 URL**（浏览器或 devtools）：
- 检查计算样式和 CSS 变量（`--md-sys-*`）
- 调整视口大小或使用响应式模式以检查断点
- 如有必要，在关键宽度上捕获截图

**对于源代码**（提供的文件路径）：
- **Compose/Kotlin**：`.kt` 文件 — `MaterialTheme`，组合组件，`Color(0x…)` 滥用，硬编码 `Dp`，缺少 `Modifier.semantics` 在需要时
- **Flutter**：`.dart` — `ThemeData`，`ColorScheme`
- **Web**：HTML/JSX/Vue/Svelte；CSS/SCSS 用于令牌
- 检查 **web** 导入，`@material/web` 对 `@material/mdc-*`（MD2）

**快速检查**（根据您的堆栈调整路径）：
```
# Web: 硬编码颜色
grep -rn '#[0-9a-fA-F]\{3,8\}' --include='*.css' --include='*.scss'

# Compose: 原始 Color(...) 审计（示例——根据您的代码库调整）
grep -rn 'Color(0x' --include='*.kt'

# web 上的 MD2
grep -rn '@material/mdc-' --include='*.js' --include='*.ts'
```

**浏览器自动化**（如果您的环境暴露 MCP 浏览器工具）：导航，快照 DOM/CSS 变量，调整大小以检查断点——可选，不要求。

### 评分指南

- **9-10**：完全 MD3 合规，使用正确的令牌和模式
- **7-8**：基本合规，有少量问题（例如，几个硬编码值）
- **4-6**：部分合规，一些 MD3 模式但存在明显差距
- **1-3**：严重违规，主要是非 MD3 或 MD2 模式
- **0**：不适用或完全缺失

状态阈值：**通过**（7+），**警告**（4-6），**失败**（0-3）

## 参考文档

- `references/color-system.md` — 颜色角色、色调调色板、动态颜色、Compose + CSS 映射
- `references/typography-and-shape.md` — 类型比例、形状角落、提升、运动、表达式说明
- `references/component-catalog.md` — 组件：Compose + `@material/web` 在适用情况下
- `references/navigation-patterns.md` — 导航选择、Compose-first 自适应模式
- `references/layout-and-responsive.md` — 断点、规范布局、内边距、折叠屏
- `references/theming-and-dynamic-color.md` — 主题：Compose 首选，然后是 Flutter 和 web
