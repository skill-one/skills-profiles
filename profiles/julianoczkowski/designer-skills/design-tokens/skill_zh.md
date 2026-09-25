这项技能为项目生成基础设计符号。在完成设计简报后、构建任何组件前运行此技能。在此之后构建的每个组件都将引用这些符号，而不是硬编码值。

## 示例提示

- "为这个项目设置设计符号"
- "基于迪特·拉姆斯生成符号系统"
- "在开始构建前，我需要间距尺度和调色板"
- "创建符合我们简报的符号"

## 流程

1. **检查已有内容**。在生成任何内容之前，扫描代码库以查找：
   - CSS 变量定义（`:root`，`[data-theme]`，自定义属性文件）
   - Tailwind 配置（`tailwind.config.js`，`tailwind.config.ts`）及任何主题扩展
   - 主题提供文件（Material UI `createTheme`，Chakra `extendTheme`，shadcn `globals.css`）
   - 设计符号 JSON 文件（Style Dictionary 格式，Figma 符号导出）
   - 任何 `tokens.css`，`variables.css`，`theme.css` 或类似命名的文件
   - `package.json` 中的 UI 框架依赖（tailwindcss，@mui/material，@chakra-ui/react 等）

   如果符号已存在，**扩展它们**而不是替换。识别差距（缺少暗黑模式、间距尺度不完整、没有动画符号）并填补这些内容。

2. **阅读简报**。查找 `.design/*/DESIGN_BRIEF.md` 中的设计简报。如果存在多个子文件夹，使用最新修改的文件，或询问用户他们正在处理哪个功能。如果命名了哲学，使用 `/frontend-design` 中的参数推导符号值。如果不存在简报，询问用户他们希望的方向。

3. **生成符号**，格式与项目技术栈匹配：
   - Tailwind 项目 → 扩展 `tailwind.config.js` 并写入 `globals.css`
   - CSS/HTML 项目 → 写入 `tokens.css` 文件
   - CSS-in-JS 项目 → 写入 `theme.ts` 或 `theme.js` 文件
   - 如果不明确，默认使用 CSS 自定义属性（最可移植）

4. **始终生成亮色和暗色模式调色板**。使用 `[data-theme="dark"]` 或 `prefers-color-scheme` 媒体查询。两个调色板都应针对所选哲学有意设计，而不仅仅是反转值。

## 符号类别

### 颜色

```css
/* 语义颜色符号，非原始值 */
--color-bg-primary:          /* 主要背景 */
--color-bg-secondary:        /* 次要/卡片背景 */
--color-bg-tertiary:         /* 微妙背景（输入、凹槽） */
--color-bg-inverse:          /* 反转背景 */

--color-text-primary:        /* 主要文本 */
--color-text-secondary:      /* 淡化文本 */
--color-text-tertiary:       /* 占位符、禁用文本 */
--color-text-inverse:        /* 反转背景上的文本 */
--color-text-link:           /* 链接颜色 */

--color-border-primary:      /* 默认边框 */
--color-border-secondary:    /* 微妙边框 */
--color-border-focus:        /* 聚焦环颜色 */

--color-accent-primary:      /* 主要操作颜色 */
--color-accent-primary-hover:
--color-accent-primary-active:
--color-accent-secondary:    /* 次要操作颜色 */

--color-status-success:
--color-status-warning:
--color-status-error:
--color-status-info:

--color-surface-overlay:     /* 模态/下拉背景 */
```

### 间距

生成一致的尺度。基本单位应与哲学匹配：
- 紧凑型哲学（Brutalist、Swiss）：4px 基础
- 平衡型哲学（Rams、Scandinavian）：4px 或 8px 基础
- 宽敞型哲学（日本极简主义、编辑）：8px 基础，具有更大的倍数

```css
--space-0:   0;
--space-1:   /* base * 0.25 */
--space-2:   /* base * 0.5 */
--space-3:   /* base * 0.75 */
--space-4:   /* base * 1 */
--space-5:   /* base * 1.5 */
--space-6:   /* base * 2 */
--space-7:   /* base * 3 */
--space-8:   /* base * 4 */
--space-9:   /* base * 6 */
--space-10:  /* base * 8 */
--space-11:  /* base * 12 */
--space-12:  /* base * 16 */
```

### 字体

```css
--font-family-display:       /* 标题/显示字体 */
--font-family-body:          /* 正文字体 */
--font-family-mono:          /* 代码/等宽字体 */

--font-size-xs:
--font-size-sm:
--font-size-base:
--font-size-md:
--font-size-lg:
--font-size-xl:
--font-size-2xl:
--font-size-3xl:
--font-size-4xl:             /* 英雄/显示尺寸 */

--font-weight-normal:
--font-weight-medium:
--font-weight-semibold:
--font-weight-bold:

--line-height-tight:         /* 标题：1.1-1.3 */
--line-height-normal:        /* 正文：1.4-1.6 */
--line-height-relaxed:       /* 宽敞正文：1.6-1.8 */

--letter-spacing-tight:      /* 显示类型 */
--letter-spacing-normal:
--letter-spacing-wide:       /* 全大写、标签 */
```

### 布局

```css
--max-width-content:         /* 最大阅读宽度（65-75ch 等效） */
--max-width-wide:            /* 宽内容区域 */
--max-width-page:            /* 全页最大宽度 */

--border-radius-sm:
--border-radius-md:
--border-radius-lg:
--border-radius-full:        /* 药丸/圆形 */

--shadow-sm:
--shadow-md:
--shadow-lg:
--shadow-focus:              /* 聚焦环阴影 */
```

### 动画

```css
--duration-instant:   50ms;
--duration-fast:      150ms;
--duration-normal:    250ms;
--duration-slow:      400ms;
--duration-slower:    600ms;

--easing-default:     cubic-bezier(0.4, 0, 0.2, 1);
--easing-in:          cubic-bezier(0.4, 0, 1, 1);
--easing-out:         cubic-bezier(0, 0, 0.2, 1);
--easing-bounce:      cubic-bezier(0.34, 1.56, 0.64, 1);
```

### 响应式断点

```css
--breakpoint-sm:   375px;    /* 手机 */
--breakpoint-md:   768px;    /* 平板 */
--breakpoint-lg:   1024px;   /* 小桌面 */
--breakpoint-xl:   1280px;   /* 桌面 */
--breakpoint-2xl:  1536px;   /* 宽桌面 */
```

## 暗黑模式

始终与亮色模式一起生成暗黑模式符号。规则：

- 不要简单反转颜色。暗色背景应根据哲学选择温暖或冷色调。
- 暗黑模式下稍微降低对比度（纯白文本在纯黑背景上过于刺眼）。
- 阴影在暗黑模式下应使用更暗、更透明的值，而不是亮色模式的相同阴影。
- 强调色可能需要亮度调整以保持对比率。
- 包含 `prefers-color-scheme` 媒体查询和 `[data-theme="dark"]` 属性选择器，以便用户支持系统偏好和手动切换。

```css
:root {
  /* 亮色模式符号 */
}

[data-theme="dark"] {
  /* 暗黑模式覆盖 */
}

@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    /* 系统偏好暗黑模式，除非用户明确选择亮色 */
  }
}
```

## 输出

将符号文件保存在项目技术栈的适当位置。说明符号基于哪种哲学，并记录任何偏差或选择。
