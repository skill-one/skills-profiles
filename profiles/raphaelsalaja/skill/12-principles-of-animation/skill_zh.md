# 动画 12 原则

检查动画代码是否符合为网页界面调整的迪士尼 12 原则。

## 工作原理

1. 读取指定文件（或提示用户输入文件/模式）
2. 检查以下所有规则
3. 以 `文件:行` 格式输出结果

## 规则类别

| 优先级 | 类别     | 前缀   |
|--------|----------|--------|
| 1      | 时间     | `timing-` |
| 2      | 缓动     | `easing-` |
| 3      | 物理效果 | `physics-` |
| 4      | 舞台效果 | `staging-` |

## 规则

### 时间规则

#### `timing-under-300ms`
用户触发的动画必须在 300ms 内完成。

**失败：**
```css
.button { transition: transform 400ms; }
```

**通过：**
```css
.button { transition: transform 200ms; }
```

#### `timing-consistent`
相似元素必须使用相同的时间值。

**失败：**
```css
.button-primary { transition: 200ms; }
.button-secondary { transition: 150ms; }
```

**通过：**
```css
.button-primary { transition: 200ms; }
.button-secondary { transition: 200ms; }
```

#### `timing-no-entrance-context-menu`
上下文菜单不应在进入时动画（仅退出时动画）。

**失败：**
```tsx
<motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} />
```

**通过：**
```tsx
<motion.div exit={{ opacity: 0 }} />
```

### 缓动规则

#### `easing-entrance-ease-out`
进入时必须使用 `ease-out`（快速到达，柔和停止）。

**失败：**
```css
.modal-enter { animation-timing-function: ease-in; }
```

**通过：**
```css
.modal-enter { animation-timing-function: ease-out; }
```

#### `easing-exit-ease-in`
退出时必须使用 `ease-in`（在离开前积累动量）。

**失败：**
```css
.modal-exit { animation-timing-function: ease-out; }
```

**通过：**
```css
.modal-exit { animation-timing-function: ease-in; }
```

#### `easing-no-linear-motion`
线性缓动仅用于进度指示器，不应用于动画。

**失败：**
```css
.card { transition: transform 200ms linear; }
```

**通过：**
```css
.progress-bar { transition: width 100ms linear; }
```

#### `easing-natural-decay`
使用指数衰减，而不是线性衰减。

**失败：**
```ts
gain.gain.linearRampToValueAtTime(0, t + 0.05);
```

**通过：**
```ts
gain.gain.exponentialRampToValueAtTime(0.001, t + 0.05);
```

### 物理效果规则

#### `physics-active-state`
交互元素必须有激活/按下状态，并使用缩放变换。

**失败：**
```css
.button:hover { background: var(--gray-3); }
/* 缺少 :active 状态 */
```

**通过：**
```css
.button:active { transform: scale(0.98); }
```

#### `physics-subtle-deformation`
挤压/拉伸变形必须微妙（0.95-1.05 范围内）。

**失败：**
```tsx
<motion.div whileTap={{ scale: 0.8 }} />
```

**通过：**
```tsx
<motion.div whileTap={{ scale: 0.98 }} />
```

#### `physics-spring-for-overshoot`
需要过冲并稳定时，应使用弹簧（而不是缓动）。

**失败：**
```tsx
<motion.div transition={{ duration: 0.3, ease: "easeOut" }} />
// 元素需要弹跳/稳定时
```

**通过：**
```tsx
<motion.div transition={{ type: "spring", stiffness: 500, damping: 30 }} />
```

#### `physics-no-excessive-stagger`
每个项目的延迟 stagger 不得超过 50ms。

**失败：**
```tsx
transition={{ staggerChildren: 0.15 }}
```

**通过：**
```tsx
transition={{ staggerChildren: 0.03 }}
```

### 舞台效果规则

#### `staging-one-focal-point`
一次只有一个元素应突出显示动画。

**失败：**
```tsx
// 多个元素有竞争的进入动画
<motion.div animate={{ scale: 1.1 }} />
<motion.div animate={{ scale: 1.1 }} />
```

#### `staging-dim-background`
模态/对话框背景应变暗以引导注意力。

**失败：**
```css
.overlay { background: transparent; }
```

**通过：**
```css
.overlay { background: var(--black-a6); }
```

#### `staging-z-index-hierarchy`
动画元素必须尊重 z-index 层级。

**失败：**
```css
.tooltip { /* 无 z-index，可能被其他元素遮挡 */ }
```

**通过：**
```css
.tooltip { z-index: 50; }
```

## 输出格式

检查文件时，按以下格式输出结果：

```
文件:行 - [规则编号] 描述问题

示例：
components/modal/index.tsx:45 - [timing-under-300ms] 退出动画 400ms 超过 300ms 限制
components/button/styles.module.css:12 - [physics-active-state] 缺少 :active 变换
```

## 摘要表

检查结果后，输出摘要：

| 规则         | 数量 | 严重程度 |
|--------------|------|----------|
| `timing-under-300ms` | 2   | 高       |
| `physics-active-state` | 3   | 中       |
| `easing-entrance-ease-out` | 1   | 中       |

## 参考文献

- [《生命之幻觉：迪士尼动画》](https://www.amazon.com/Illusion-Life-Disney-Animation/dp/0786860707)
- [Apple WWDC23: 使用弹簧动画](https://developer.apple.com/videos/play/wwdc2023/10158)
