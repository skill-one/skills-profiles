# Transitions.dev

十二种便携式 CSS 过渡效果，每个效果都使用 `t-*` 选择器命名空间，并具有语义 CSS 自定义属性。即插即用：粘贴代码片段，连接文档中说明的 HTML 钩子，搞定。无需框架依赖，无需特定演示的标记，每个代码片段都附带 `prefers-reduced-motion` 保护。

## 快速参考

| 过渡效果 | 使用场景 | 参考 |
| --- | --- | --- |
| **卡片调整大小** | 当容器的布局状态发生变化时，对容器的宽度或高度进行插值动画。 | [01-card-resize.md](./01-card-resize.md) |
| **数字弹出** | 当数字更新时，每个数字都以模糊滑入的方式重新进入。 | [02-number-pop-in.md](./02-number-pop-in.md) |
| **通知徽章** | 将一个小徽章滑到触发器上，并弹出圆点。 | [03-notification-badge.md](./03-notification-badge.md) |
| **文本状态交换** | 使用模糊的上下过渡效果，原地交换文本。 | [04-text-states-swap.md](./04-text-states-swap.md) |
| **菜单下拉** | 打开一个感知原点的下拉菜单，从其触发器处展开。 | [05-menu-dropdown.md](./05-menu-dropdown.md) |
| **模态框打开/关闭** | 打开模态对话框时进行缩放，关闭时进行更柔和的缩放。 | [06-modal.md](./06-modal.md) |
| **面板显示** | 使用交叉模糊效果将面板滑入页面区域。 | [07-panel-reveal.md](./07-panel-reveal.md) |
| **页面并排** | 在两个并排的页面之间滑动（列表 ↔ 详情，步骤 1 ↔ 步骤 2）。 | [08-page-side-by-side.md](./08-page-side-by-side.md) |
| **图标交换** | 使用模糊和缩放效果，在同一位置交叉淡入淡出两个图标。 | [09-icon-swap.md](./09-icon-swap.md) |
| **成功检查** | 组合淡入 + 旋转 + Y 形摆动 + 路径绘制来庆祝完成的操作。 | [10-success-check.md](./10-success-check.md) |
| **头像组悬停** | 在一排项目上使用距离衰减提升，返回时使用弹跳弹簧。 | [11-avatar-group-hover.md](./11-avatar-group-hover.md) |
| **错误状态抖动** | 每个片段使用三次贝塞尔曲线抖动，并自动恢复边框 + 消息。 | [12-error-state-shake.md](./12-error-state-shake.md) |

## 决策规则

当用户需要过渡效果时，首先匹配可见的 UI 元素，然后匹配动词：

- **触发器 + 顶部漂浮的小圆点** → 通知徽章。
- **触发器 + 从其扩展的表面** → 下拉菜单（锚定，感知原点）或模态框（居中，无锚定）。
- **滑入页面区域的表面** → 面板显示。
- **两个屏幕，列表 ↔ 详情或步骤 1 ↔ 步骤 2** → 页面并排。
- **元素宽度或高度发生变化** → 卡片调整大小。
- **元素文本内容原地变化** → 文本状态交换。
- **同一位置的两个图标** → 图标交换。
- **数字更新** → 数字弹出。
- **确认 / 成功 / "完成"时刻**（勾选标记，支付处理，文件上传）→ 成功检查。
- **在水平堆栈中悬停项目**（头像，标签，分段按钮，标签药丸）→ 头像组悬停。
- **表单验证错误 / "这是错误的"反馈**（无效字段，错误的 PIN，重复名称）→ 错误状态抖动。

如果两个过渡效果都适用，优先选择开销较低的（卡片调整大小优先于面板显示，下拉菜单优先于模态框，成功检查优先于完整的模态框庆祝效果），除非设计明确要求使用更复杂的表面。成功检查仅使用动画——如果你还需要从加载器切换到检查，请将其与 **图标交换** 配合使用。

## 通用安装

将这个 `:root` 块一次性放入你的项目中。每个过渡效果代码片段都从此语义名称读取——后面没有需要追踪的每个组件的值。

```css
/* transitions-dev — 将这个 :root 块一次性复制到你的项目中。
   每个过渡效果代码片段都从此语义名称读取。 */
:root {
  /* 卡片调整大小 */
  --resize-dur: 300ms;
  --resize-ease: cubic-bezier(0.22, 1, 0.36, 1);
  /* 数字弹出 */
  --digit-dur: 500ms;
  --digit-distance: 8px;
  --digit-stagger: 70ms;
  --digit-blur: 2px;
  --digit-ease: cubic-bezier(0.34, 1.45, 0.64, 1);
  --digit-dir-x: 0;
  --digit-dir-y: 1;
  /* 通知徽章 */
  --badge-slide-dur: 260ms;
  --badge-pop-dur: 500ms;
  --badge-pop-close-dur: 180ms;
  --badge-fade-dur: 400ms;
  --badge-fade-close-dur: 180ms;
  --badge-blur: 2px;
  --badge-offset-x: -8.2px;
  --badge-offset-y: 12.4px;
  --badge-slide-ease: cubic-bezier(0.22, 1, 0.36, 1);
  --badge-pop-ease: cubic-bezier(0.34, 1.36, 0.64, 1);
  --badge-close-ease: cubic-bezier(0.4, 0, 0.2, 1);
  /* 文本状态交换 */
  --text-swap-dur: 200ms;
  --text-swap-translate-y: 8px;
  --text-swap-blur: 2px;
  --text-swap-ease: ease-out;
  /* 菜单下拉 */
  --dropdown-open-dur: 250ms;
  --dropdown-close-dur: 150ms;
  --dropdown-pre-scale: 0.97;
  --dropdown-closing-scale: 0.99;
  --dropdown-ease: cubic-bezier(0.22, 1, 0.36, 1);
  /* 模态框打开/关闭 */
  --modal-open-dur: 250ms;
  --modal-close-dur: 150ms;
  --modal-scale: 0.96;
  --modal-scale-close: 0.96;
  --modal-ease: cubic-bezier(0.22, 1, 0.36, 1);
  /* 面板显示 */
  --panel-open-dur: 400ms;
  --panel-close-dur: 350ms;
  --panel-translate-y: 100px;
  --panel-blur: 2px;
  --panel-ease: cubic-bezier(0.22, 1, 0.36, 1);
  /* 页面并排 */
  --page-slide-dur: 200ms;
  --page-fade-dur: 200ms;
  --page-slide-distance: 8px;
  --page-blur: 3px;
  --page-stagger: 0ms;
  --page-exit-enabled: 1;
  --page-slide-ease: cubic-bezier(0.22, 1, 0.36, 1);
  --page-fade-ease: cubic-bezier(0.22, 1, 0.36, 1);
  /* 图标交换 */
  --icon-swap-dur: 200ms;
  --icon-swap-blur: 2px;
  --icon-swap-start-scale: 0.25;
  --icon-swap-ease: ease-in-out;
  /* 成功检查 */
  --check-opacity-dur: 550ms;
  --check-rotate-dur: 550ms;
  --check-rotate-from: 80deg;
  --check-bob-dur: 450ms;
  --check-y-amount: 40px;
  --check-blur-dur: 500ms;
  --check-blur-from: 10px;
  --check-path-dur: 550ms;
  --check-path-delay: 80ms;
  --check-ease-out: cubic-bezier(0.22, 1, 0.36, 1);
  --check-ease-opacity: cubic-bezier(0.22, 1, 0.36, 1);
  --check-ease-rotate: cubic-bezier(0.22, 1, 0.36, 1);
  --check-ease-bob: cubic-bezier(0.34, 1.35, 0.64, 1);
  --check-ease-path: cubic-bezier(0.22, 1, 0.36, 1);
  /* 头像组悬停 */
  --avatar-lift: -4px;
  --avatar-dur: 320ms;
  --avatar-scale: 1.05;
  --avatar-falloff: 0.45;
  --avatar-ease-in: cubic-bezier(0.22, 1, 0.36, 1);
  --avatar-ease-out: cubic-bezier(0.34, 3.85, 0.64, 1);
  /* 错误状态抖动 */
  --shake-distance: 6px;
  --shake-overshoot: 4px;
  --shake-dur-a: 80ms;
  --shake-dur-b: 60ms;
  --shake-ease: cubic-bezier(0.22, 1, 0.36, 1);
  --revert-hold: 3000ms;
  --revert-dur: 280ms;
}
```

[transitions.dev](https://transitions.dev) 的实时演示使用的 `--pX-*` 源标记**故意不**在此处导出。可调值被重命名为语义名称（`--badge-*`，`--dropdown-*`，`--modal-*`，…），以便用户拥有设计词汇。

## 输出格式

将过渡效果插入用户项目时：

1. **在用户的全局样式表中添加 `:root` 块**，但仅当它不存在时。如果用户已经一次性导入了通用安装块，则**不要**重复它。
2. **从相关参考文件中逐字粘贴所选过渡效果的 CSS**。不要重写选择器，不要将过渡效果简化为简写形式，不要删除 `will-change`。代码片段经过调整和测试。
3. **连接文档中说明的 HTML 钩子**——类名（`.t-dropdown`，`.t-modal`，`.t-success-check`，`.t-avatar`，`.t-input`，…）和状态属性（`data-open`，`data-state`，`data-page`，`.is-open`，`.is-closing`，`.is-exit`，`.is-enter-start`，`.is-animating`，`.is-error`，`.is-shaking`）。
4. **保留 `@media (prefers-reduced-motion: reduce)` 块**。每个代码片段都附带一个。删除它会使组件无法通过无障碍性审核。
5. **对于需要 JS 的过渡效果**（下拉菜单，模态框，文本交换，数字弹出，页面滑动，成功检查，头像组悬停，错误状态抖动），从参考文件中复制小的编排代码片段，并将选择器调整为用户的 DOM。保留时间读取（`getComputedStyle(...)getPropertyValue("--…")`），以便持续时间与 `:root` 值保持同步。

保持差异小：仅编辑引入过渡效果所需的文件。不要重命名用户现有的变量，不要重新格式化无关的 CSS，不要引入运动库。

## 避免常见错误

- **在 dropdown/modal 上删除关闭状态类清理**——没有 `setTimeout` 删除 `.is-closing`，下一个打开将从关闭缩放跳转到静止的预打开缩放。
- **忘记在文本交换，数字弹出，成功检查重播和错误状态抖动中进行重排**——`void el.offsetWidth`（或 `offsetHeight`）在类/属性移除和重新添加之间是保证动画重播的关键。
- **对单个容器进行动画**而不是内部部分——对于徽章，动画圆点而不是触发器；对于页面滑动，动画页面部分而不是容器。
- **用 `transition: …` 替换 `transition: all`**——每个代码片段故意枚举确切的属性，以便无关的样式更改不会免费搭乘。
- **在 CSS 中硬编码成功检查的 `stroke-dasharray`**——代码片段将 `20` 作为占位符。用 `path.getTotalLength()` 向上取整为 *你的* 路径的值，否则笔触会预先显示或过度绘制。
- **在 CSS 中设置 `transition-timing-function`**对于头像组悬停——它必须在 JS 中设置在 `--shift` / `--scale-active` 写入之前，以便弹跳的 ease-out 仅适用于 `mouseleave`。
- **将 `.is-error` 和 `.is-shaking` 混合到一个类中**用于错误状态抖动——保持它们正交是允许抖动重播（移除 → 重排 → 重新添加）而不会使整个错误处理闪烁的关键。

## 参考文件

- [01-card-resize.md](./01-card-resize.md) — 卡片调整大小
- [02-number-pop-in.md](./02-number-pop-in.md) — 数字弹出
- [03-notification-badge.md](./03-notification-badge.md) — 通知徽章
- [04-text-states-swap.md](./04-text-states-swap.md) — 文本状态交换
- [05-menu-dropdown.md](./05-menu-dropdown.md) — 菜单下拉
- [06-modal.md](./06-modal.md) — 模态框打开/关闭
- [07-panel-reveal.md](./07-panel-reveal.md) — 面板显示
- [08-page-side-by-side.md](./08-page-side-by-side.md) — 页面并排
- [09-icon-swap.md](./09-icon-swap.md) — 图标交换
- [10-success-check.md](./10-success-check.md) — 成功检查
- [11-avatar-group-hover.md](./11-avatar-group-hover.md) — 头像组悬停
- [12-error-state-shake.md](./12-error-state-shake.md) — 错误状态抖动
- [_root.css](./_root.css) — 仅包含通用安装块的独立文件，可直接导入。
