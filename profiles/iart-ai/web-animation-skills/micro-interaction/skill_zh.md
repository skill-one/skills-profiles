# 微交互（UI 动效）

小型的功能性动效，使界面感觉响应迅速且生动：悬停/点击/聚焦反馈、切换开关、轻提示、抽屉、列表/布局动画。目标是反馈和连贯性，而非装饰。

## 何时使用

- 悬停/点击/聚焦反馈；切换开关、复选框、点赞/爱心按钮
- 轻提示/轻通知栏、抽屉、模态框、工具提示、手风琴（进入/退出）
- 列表添加/删除/排序；共享元素（“魔法移动”）布局过渡
- 加载 → 成功 → 错误状态过渡

## 原则（适用于所有情况）

- 持续时间：UI 微交互存在于 **100–250ms** 之间。超过 ~400ms 的点击响应会感觉卡顿。
- 仅动画化 `transform` 和 `opacity` —— 它们是 GPU 合成的（无布局/绘制）。避免动画化 `width/height/top/left`；使用 `scale` 或布局动画代替。
- 提供即时点击反馈：点击时使用快速弹簧实现 `scale: 0.96`。
- 非对称时间：进入稍慢（缓出），退出更快（缓入）。事物应优雅地出现并迅速离开。
- 尊重 `prefers-reduced-motion`：屏蔽非必要动效；保留不透明度变化，避免大幅度移动。
- 缓动默认值：进入使用 `ease-out` `cubic-bezier(0.16, 1, 0.3, 1)`；适度的过冲使用 `cubic-bezier(0.34, 1.56, 0.64, 1)`；标准移动使用 `cubic-bezier(0.4, 0, 0.2, 1)`。

## Framer Motion (motion/react) 基础

自 v11+ 起，该包作为 `motion/react` 导入（`framer-motion` 名称仍然有效）。

### 手势和弹簧

```jsx
import { motion } from "motion/react";

<motion.button
  whileHover={{ scale: 1.03 }}
  whileTap={{ scale: 0.96 }}
  whileFocus={{ boxShadow: "0 0 0 3px rgba(59,130,246,.5)" }}
  transition={{ type: "spring", stiffness: 400, damping: 30 }}
/>
```

弹簧直觉：更高的 `stiffness` = 更快；更高的 `damping` = 更少弹跳。`stiffness: 400, damping: 30` 是一个灵敏的 UI 默认值。要实现可见的弹跳，降低阻尼（例如 `damping: 12`）。

### 使用 AnimatePresence 实现进入/退出

退出动画需要 `AnimatePresence` 包裹条件渲染的子元素，每个子元素都有一个稳定的 `key`。

```jsx
import { AnimatePresence, motion } from "motion/react";

<AnimatePresence>
  {open && (
    <motion.div
      key="panel"
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: 8 }}
      transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
    />
  )}
</AnimatePresence>
```

对于轻提示/列表，使用 `mode="popLayout"` 以确保退出时被移除的项不占用空间。

### 布局动画（超能力）

`layout` 会自动使用变换动画化任何布局变化（位置/大小）—— 非常适合重新排序、展开卡片和网格<->列表。

```jsx
<motion.li layout transition={{ type: "spring", stiffness: 500, damping: 40 }} />
```

跨组件的共享元素过渡：给两个元素相同的 `layoutId`，Framer Motion 在它们挂载和卸载时将它们作为一个整体进行动画。

```jsx
{!open && <motion.div layoutId="card" onClick={() => setOpen(true)} />}
<AnimatePresence>
  {open && <motion.div layoutId="card" />}
</AnimatePresence>
```

注意：一个普通的 `layout` 元素在缩放时会扭曲 `border-radius` 和文本。将 `layout` 添加到应反向缩放的直接子元素，并优先使用 `borderRadius`/`boxShadow` 作为动效值，或使用 `layout="position"` 仅动画化位置。

## 纯 CSS 路径（无 JS，包括离散属性）

现代 CSS 可以在不使用库的情况下动画化进入/退出，甚至 `display` 切换。

```css
.toast {
  transition: opacity 0.2s ease, transform 0.2s ease;
  /* 允许从 display:none 动画到/from 初始渲染 */
  transition-behavior: allow-discrete;
}
.toast[hidden] { display: none; }

/* 在首次渲染/进入时从这些值开始动画 */
@starting-style {
  .toast { opacity: 0; transform: translateY(8px); }
}
```

`@starting-style` 定义了“打开前”的值，以便元素在首次出现时动画化；`transition-behavior: allow-discrete` 允许 `display`（以及弹出窗口/对话框的 `overlay`）参与，以便退出动画在元素被移除之前运行。Chrome/Edge/Safari 的基线；为旧版浏览器提供无动画回退。

始终包含一个减少动效的守卫：

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

## 状态，而非装饰

加载 → 成功 → 错误应是一个连续的动效（例如按钮变形为旋转器 → 对勾），而不是跳切。保持元素挂载并动画化状态转换，以便眼睛跟踪同一对象。

## 交付与验证（独立 HTML）

> **打包辅助工具** (`scripts/`)：`scripts/seek-shot.sh anim.html 0 1.5 3` 会冻结 `?t=N` 捕获器并截图每个时刻；`scripts/contact-sheet.sh sheet.png frame-*.png` 将它们平铺以供快速查看。参见 `scripts/README.md`。

对于自包含的交互演示（切换、点赞按钮、轻提示、抽屉），交付物是一个直接在浏览器中打开的**一个 HTML 文件**。纯 CSS 交互直接交付；对于 Framer Motion 演示，从 CDN (`esm.sh`) 加载 React + `motion` 到一个内联模块——无需构建步骤。一个文件是正确的层级；不要使用打包器。

**输出合同：**
- 一个 `.html` 文件：你的标记加上 CSS 过渡/`@starting-style` 或从 CDN 导入 `motion` 的内联 `<script type="module">`。
- 一种方法可以停留在**解析的最终状态**以供截图——交互由状态驱动而非时间驱动，因此冻结状态而非时钟。

**Seek 捕获器——固定一个确定性状态。** 微交互的“帧”是其状态（空闲 / 悬停 / 点击 / 打开）。`?state=open` 在加载时应用目标状态，以便截图捕获其稳定状态：

```html
<script>
  const s = new URLSearchParams(location.search).get("state");
  if (s) document.documentElement.dataset.state = s;   // CSS 基于 [data-state="open"] 键
  // Framer Motion：从 `s` 设置受控属性（例如 const [open]=useState(s==="open"))
  // 对于 CSS @keyframes 循环，冻结它：el.style.animationDelay=(-N)+"s"; el.style.animationPlayState="paused";
  window.__ready = true;
</script>
```

**验证循环——渲染 → 设置状态 → 截图 → 检查：** 打开每个有意义的状态 (`?state=idle`, `?state=hover`, `?state=open`)，截图并检查**保真度**（点击反馈即时，退出在卸载前运行）加上**伪影**（`layout` 扭曲 `border-radius`/文本，退出后轻提示占用空间，FOUC，卡顿）。任何无头工具都可以：

```bash
npx playwright screenshot --wait-for-timeout=400 "file://$PWD/demo.html?state=open" open.png
```

**完成前：**
1. 独立打开——无控制台错误，CDN React/`motion`（如果使用）解析。
2. `?state=`（或受控属性）冻结到达确定性、稳定的状态。
3. 跨状态截图——空闲 / 活跃 / 打开——与简报匹配，无伪影。
4. 尊重 `prefers-reduced-motion`——大幅度移动被移除，不透明度/反馈保留。
5. 缓动有意为之——进入缓出，退出缓入，持续时间在 100–250ms 范围内。

## 快速参考

| 需求 | 方法 |
|------|------|
| 点击反馈 | `whileTap={{ scale: 0.96 }}` 弹簧 400/30 |
| 进入/退出 | `AnimatePresence` + `initial/animate/exit` |
| 重新排序 / 调整大小 | `layout` 属性（弹簧） |
| 魔法移动 | 共享 `layoutId` |
| 轻提示堆栈 | `AnimatePresence mode="popLayout"` |
| 无 JS 进入 | `@starting-style` + 过渡 |
| 动画到 display:none | `transition-behavior: allow-discrete` |
| 可访问性 | `prefers-reduced-motion` 守卫始终 |

## 参考文件

- `references/framer-motion-recipes.md` — 变体 + 交错，`AnimatePresence` 模式，`layout`/`layoutId` 魔法移动，`Reorder` 拖动排序，拖动约束，手势组合，以及 `useReducedMotion`。
- `references/css-recipes.md` — `@starting-style`，`transition-behavior: allow-discrete`，弹出窗口/对话框退出动画，关键帧旋转器/切换，`@property` 用于可动画化自定义属性，以及 `prefers-reduced-motion` 模式。
