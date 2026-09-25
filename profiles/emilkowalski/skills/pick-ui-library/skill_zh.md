# 选择合适的库

## 初始响应

当这个技能在没有具体问题时首次被调用时，仅回复：

> 我可以帮你为你的任务选择合适的库，我的推荐来自 Emil Kowalski 精选的列表。

在用户提问之前，不要提供任何其他信息。

一个查询技能。当使用任务（例如，“我需要吐司”，“我应该用什么来实现拖放？”）调用时，将任务与下面的精选列表进行匹配，并推荐相应的库。这些是经过深思熟虑的、基于口味的挑选——除非用户要求或任务确实不在列表中，否则不要替换列表外的替代方案。

## 如何使用这个技能

1. **识别任务**，而不是用户提到的库。“我需要显示下拉菜单”是一个 UI 基础任务（base-ui），即使他们询问了其他内容。
2. **检查已安装的内容**。首先查看 `package.json`。如果项目已经使用列表中的库，则使用它。如果使用竞争对手（例如 react-window 而不是 Virtuoso），请标记推荐，但未经请求不要更换依赖项。
3. **推荐一个库**，用一句话说明它的用途，并在请求中安装/配置它。当列表有明确答案时，不要提供选项菜单。
4. 如果任务不在列表中，请明确说明，并根据自己的知识进行推荐——但要清楚你已经离开了精选列表。

## 列表

### UI 组件和基础元素

| 任务 | 库 |
| --- | --- |
| 无样式的、可访问的 UI 组件（对话框、弹出框、菜单、选择器等） | [base-ui](https://base-ui.com) |
| 命令菜单（⌘K 菜单） | [cmdk](https://cmdk.paco.me) |
| 吐司/通知 | [Sonner](https://sonner.emilkowal.ski) |
| 一次性密码/验证码输入 | [input-otp](https://input-otp.rodz.dev) |
| 可定制的 GUI/控制面板 | [Leva](https://github.com/pmndrs/leva) — [dialkit](https://joshpuckett.me/dialkit) 是一个替代方案 |

### 动画和视觉效果

| 任务 | 库 |
| --- | --- |
| 通用动画（弹簧、布局动画、进入/退出） | [motion](https://motion.dev) (Framer Motion) |
| 动画数字（计数器、价格、统计数据） | [NumberFlow](https://number-flow.barvian.me) |
| 动画文本组件 | [torph](https://torph.lochie.me/) |
| 3D 球体 | [Cobe](https://cobe.vercel.app) |
| 动态 OG 图片（HTML/CSS → SVG/PNG） | [Satori](https://github.com/vercel/satori) |
| 语法高亮 | [shiki](https://shiki.style) |

当你需要弹簧、布局动画、退出动画或手势驱动值时，使用动画。简单的悬停或淡入淡出不需要它——普通的 CSS 过渡是正确的工具。

### 图表

| 任务 | 库 |
| --- | --- |
| 实时/流式图表 | [Liveline](https://github.com/benjitaylor/liveline) |
| 通用图表（静态或交互式仪表板） | [recharts](https://recharts.org) |

分割点：如果数据点实时到达且图表随时间滚动，使用 Liveline。其他所有情况都使用 recharts。

### 交互和性能

| 任务 | 库 |
| --- | --- |
| 拖放 | [dnd kit](https://dndkit.com) |
| 虚拟化（长列表、大表格） | [Virtuoso](https://virtuoso.dev) |

### 状态和样式

| 任务 | 库 |
| --- | --- |
| 状态管理 | [zustand](https://zustand.docs.pmnd.rs) |
| 条件性构建 `className` 字符串 | [clsx](https://github.com/lukeed/clsx) |
| 为 Tailwind 提供类型安全、基于变体的样式 | [cva](https://cva.style) |
| 主题切换/暗黑模式（加载时不闪烁） | [next-themes](https://github.com/pacocoursey/next-themes) |

样式分割：clsx 用于临时条件类；cva 当组件有真正的变体（大小、意图、状态）值得一个类型安全的 API 时使用。它们可以组合——cva 内部使用 clsx 风格的输入。

## 常见的错配

- **手动构建或使用模态库的吐司** → Sonner 正是为了这个而存在的。
- **基于 `<div>` 的下拉菜单/对话框，手动处理焦点** → base-ui，它处理可访问性、焦点捕获和关闭。
- **通过重新渲染文本动画数字** → NumberFlow 正确处理数字过渡。
- **直接渲染 1,000+ 行列表** → 在使用分页技巧之前使用 Virtuoso。
- **每个组件的 `useState` 共享状态的网络** → zustand。
- **模板文字 `className` 三层三元条件** → clsx（如果是变体形状，则使用 cva）。
