# 响应式模式

使用容器查询、流体排版和移动优先策略的现代响应式设计模式，适用于 React 应用程序（2026 年最佳实践）。

## 概述

- 构建可重用的适应其容器的组件
- 实现平滑缩放的流体排版
- 创建响应式布局，避免媒体查询过度
- 为多个上下文构建设计系统组件
- 优化可变容器尺寸（侧边栏、模态框、网格）

## 核心概念

### 容器查询与媒体查询

| 功能 | 媒体查询 | 容器查询 |
|------|----------|----------|
| 响应于 | 视口尺寸 | 容器尺寸 |
| 组件重用 | 上下文相关 | 真正可移植 |
| 浏览器支持 | 普遍支持 | 2023 年底基础支持 |
| 用例 | 页面布局 | 组件布局 |

## 现代CSS布局

> 加载 `Read("rules/css-subgrid.md")` 获取CSS Subgrid模式：嵌套网格对齐、带对齐标题/内容/操作的卡片布局、二维子网格。

> 加载 `Read("rules/css-intrinsic-responsive.md")` 获取内在响应式布局：auto-fit/minmax网格、clamp()用于流体元素、容器查询用于组件逻辑、零媒体查询模式。

> 加载 `Read("rules/responsive-foldables.md")` 获取可折叠/多屏设备支持：env(safe-area-inset-*), 视口分段查询, 双屏布局, 渐进增强。

**涵盖的关键模式：** CSS Subgrid对齐、内在响应式网格（auto-fit + minmax）、流体clamp()缩放、可折叠设备布局、安全区域内边距、视口分段查询。

## CSS模式

> 加载 `Read("rules/css-patterns.md")` 获取完整CSS示例：容器查询、cqi/cqb单位、使用clamp()的流体排版、移动优先断点、CSS网格模式、滚动查询。

**涵盖的关键模式：** 容器查询基础、容器查询单位（cqi/cqb）、使用clamp()的流体排版、基于容器的流体排版、移动优先断点、CSS网格响应式模式、容器滚动查询（Chrome 126+）。

## React模式

> 加载 `Read("rules/react-patterns.md")` 获取完整React示例：ResponsiveCard组件、Tailwind容器查询、useContainerQuery钩子、响应式图片。

**涵盖的关键模式：** 使用容器查询的响应式组件、Tailwind CSS容器查询、useContainerQuery钩子、响应式图片模式。

## 可访问性考虑

```css
/* 重要提示：流体排版中始终包含rem */
/* 这确保尊重用户字体偏好 */

/* ❌ 错误：仅视口单位忽略用户偏好 */
font-size: 5vw;

/* ✅ 正确：包含rem以尊重用户设置 */
font-size: clamp(1rem, 0.5rem + 2vw, 2rem);

/* 用户缩放仍需正常工作 */
@media (min-width: 768px) {
  /* 理想情况下使用em/rem而非px设置断点 */
  /* (浏览器仍使用px，但考虑用户缩放) */
}
```

## 反模式（禁止使用）

```css
/* ❌ 绝对禁止：仅使用视口单位设置文本 */
.title {
  font-size: 5vw; /* 忽略用户字体偏好！ */
}

/* ❌ 绝对禁止：使用cqw/cqh（应使用cqi/cqb） */
.card {
  padding: 5cqw; /* cqw = 容器宽度，非逻辑单位 */
}
/* ✅ 正确：使用逻辑单位 */
.card {
  padding: 5cqi; /* 容器行内 = 逻辑方向 */
}

/* ❌ 绝对禁止：无container-type的容器查询 */
@container (min-width: 400px) {
  /* 无父级container-type将无法工作！ */
}

/* ❌ 绝对禁止：桌面优先媒体查询 */
.element {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
}
@media (max-width: 768px) {
  .element {
    grid-template-columns: 1fr; /* 覆盖 = 更多CSS */
  }
}

/* ❌ 绝对禁止：文本的固定像素断点 */
@media (min-width: 768px) {
  body { font-size: 18px; } /* 使用rem！ */
}

/* ❌ 绝对禁止：过度嵌套容器查询 */
@container a {
  @container b {
    @container c {
      /* 太复杂，重新考虑架构 */
    }
  }
}
```

## 浏览器支持

| 功能 | Chrome | Safari | Firefox | Edge |
|------|--------|--------|---------|------|
| 容器尺寸查询 | 105+ | 16+ | 110+ | 105+ |
| 容器样式查询 | 111+ | ❌ | ❌ | 111+ |
| 容器滚动状态 | 126+ | ❌ | ❌ | 126+ |
| cqi/cqb单位 | 105+ | 16+ | 110+ | 105+ |
| clamp() | 79+ | 13.1+ | 75+ | 79+ |
| Subgrid | 117+ | 16+ | 71+ | 117+ |

## 规则

每个类别都有独立的规则文件在 `rules/` 目录中按需加载：

| 类别 | 规则 | 影响 | 关键模式 |
|------|------|------|----------|
| 现代CSS布局 | `rules/css-subgrid.md` | 高 | CSS Subgrid用于嵌套网格对齐、卡片布局 |
| 现代CSS布局 | `rules/css-intrinsic-responsive.md` | 高 | 内在响应式布局，auto-fit/minmax，clamp()，零断点 |
| 现代CSS布局 | `rules/responsive-foldables.md` | 中 | 可折叠设备，安全区域内边距，视口分段 |
| CSS | `rules/css-patterns.md` | 高 | 容器查询，cqi/cqb，流体排版，网格，滚动查询 |
| React | `rules/react-patterns.md` | 高 | 容器查询组件，Tailwind，useContainerQuery，响应式图片 |
| PWA | `rules/pwa-service-worker.md` | 高 | Workbox缓存策略，VitePWA，更新管理 |
| PWA | `rules/pwa-offline.md` | 高 | 离线钩子，后台同步，安装提示 |
| 动画 | `rules/animation-motion.md` | 高 | 动作预设，AnimatePresence，视图转换 |
| 动画 | `rules/animation-scroll.md` | 中 | CSS滚动驱动动画，视差，渐进增强 |
| 触摸与移动 | `rules/touch-interaction.md` | 高 | 触摸目标（最小44px），拇指区域，捏合缩放，安全区域，手势 |

**总计：6类10条规则**

## 关键决策

| 决策 | 选项A | 选项B | 推荐方案 |
|------|-------|-------|----------|
| 查询类型 | 媒体查询 | 容器查询 | **容器**（组件），**媒体**（布局） |
| 容器单位 | cqw/cqh | cqi/cqb | **cqi/cqb**（逻辑，支持多语言） |
| 流体类型基础 | 仅vw | rem + vw | **rem + vw**（可访问性） |
| 移动优先 | 是 | 桌面优先 | **移动优先**（CSS更少，渐进式） |
| 网格模式 | auto-fit | auto-fill | **auto-fit**用于卡片，**auto-fill**用于图标 |

## 相关技能

- `design-system-starter` - 构建响应式设计系统
- `ork:performance` - CLS，响应式图片和图片优化
- `ork:i18n-date-patterns` - RTL/LTR响应式考虑

## 能力详情

### container-queries
**关键词**：@container, container-type, inline-size, container-name
**解决**：组件级响应式设计

### fluid-typography
**关键词**：clamp(), fluid, vw, rem, scale, typography
**解决**：无断点的平滑字体缩放

### responsive-images
**关键词**：srcset, sizes, picture, art direction
**解决**：不同视口的响应式图片

### mobile-first-strategy
**关键词**：min-width, mobile, progressive, breakpoints
**解决**：高效的响应式CSS架构

### grid-flexbox-patterns
**关键词**：auto-fit, auto-fill, subgrid, minmax
**解决**：响应式网格和flexbox布局

### container-units
**关键词**：cqi, cqb, container width, container height
**解决**：相对于容器尺寸的尺寸设置

## 参考文献

按需加载 `Read("references/<file>")`：
| 文件 | 内容 |
|------|------|
| `container-queries.md` | 容器查询模式 |
| `fluid-typography.md` | 可访问的流体类型缩放 |
