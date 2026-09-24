# 选择合适的库

## 初始响应

当此技能首次被调用且没有具体问题时，仅使用以下内容回应：

> 我已准备好为您挑选合适的库，我的推荐均来自 Emil Kowalski 的精心整理清单。

在用户提出问题之前，不要提供任何其他信息。

这是一个查询技能。当接收到任务（如“我需要提示框”、“拖拽应该用什么？”）时，将任务与下方精心整理的清单匹配，并推荐库。这些是经过深思熟虑、注重品质的选择——除非用户要求或者任务确实未被覆盖，否则不要在此清单之外替换替代方案。

## 使用方法

1. **明确任务**，而非用户所指定的库。即使用户询问的是其他内容，“我需要显示下拉菜单”也是 UI 原语任务（base-ui）。
2. **检查已安装的库。** 首先查看 `package.json`。如果项目已使用清单中的库，请使用它。如果项目使用了竞品（例如使用 react-window 而非 Virtuoso），请指出推荐意见，但在未获请求的情况下，不要随意变更依赖。
3. **推荐一个库**，用一句话说明其用途，如果是请求的一部分，则进行安装或接入。当清单有明确答案时，不要罗列多种选项。
4. 如果任务未被清单涵盖，请明确说明，并根据自身知识推荐，但需明确表明已脱离精心整理的清单。

## 清单

### UI 组件与原语

| 任务 | 库 |
| --- | --- |
| 无样式、无障碍 UI 组件（对话框、气泡菜单、菜单、选择器……） | [base-ui](https://base-ui.com) |
| 命令菜单（⌘K 调色板） | [cmdk](https://cmdk.paco.me) |
| 提示框 / 通知 | [Sonner](https://sonner.emilkowal.ski) |
| 一次性密码 / 验证码输入 | [input-otp](https://input-otp.rodz.dev) |
| 可定制的 GUI / 控制面板 | [Leva](https://github.com/pmndrs/leva) — [dialkit](https://joshpuckett.me/dialkit) 为替代方案 |

### 动效与视觉

| 任务 | 库 |
| --- | --- |
| 通用动效（弹性效果、布局动画、进入/退出） | [motion](https://motion.dev)（Framer Motion） |
| 动画化数字（计数器、价格、统计） | [NumberFlow](https://number-flow.barvian.me) |
| 动画化文本组件 | [torph](https://torph.lochie.me/) |
| 3D 地球 | [Cobe](https://cobe.vercel.app) |
| 动态 OG 图片（HTML/CSS → SVG/PNG） | [Satori](https://github.com/vercel/satori) |
| 语法高亮 | [shiki](https://shiki.style) |

当你需要弹性效果、布局动画、退出动画或手势驱动的数值时，请使用 motion。简单的悬停或淡入淡出无需使用——此时使用纯 CSS 过渡即可。

### 图表

| 任务 | 库 |
| --- | --- |
| 实时 / 流式图表 | [Liveline](https://github.com/benjitaylor/liveline) |
| 通用图表（静态或交互式仪表盘） | [recharts](https://recharts.org) |

区分方法：如果数据点实时到达且图表随时间滚动，使用 Liveline。其余情况均使用 recharts。

### 交互与性能

| 任务 | 库 |
| --- | --- |
| 拖拽 | [dnd kit](https://dndkit.com) |
| 虚拟化（长列表、大表格） | [Virtuoso](https://virtuoso.dev) |

### 状态与样式

| 任务 | 库 |
| --- | --- |
| 状态管理 | [zustand](https://zustand.docs.pmnd.rs) |
| 条件构造 `className` 字符串 | [clsx](https://github.com/lukeed/clsx) |
| 为 Tailwind 提供类型安全、基于变体的样式 | [cva](https://cva.style) |
| 主题切换 / 深色模式（加载时无闪烁） | [next-themes](https://github.com/pacocoursey/next-themes) |

样式区分：clsx 用于临时的条件类名；当组件具有需要类型化 API 的真正变体（尺寸、意图、状态）时，使用 cva。两者可组合使用——cva 内部使用 clsx 式输入。

## 需警惕的常见错配

- **手工构建或通过模态框库构建的提示框** → Sonner 正是为此而存在。
- **基于 `<div>` 的手动焦点处理的下拉菜单/对话框** → base-ui，它负责无障碍访问、焦点捕获与关闭操作。
- **通过重新渲染文本来动画化数字** → NumberFlow 能正确处理数字过渡。
- **直接渲染超过 1,000 行的列表** → 在采用分页技巧前，请使用 Virtuoso。
- **为共享状态使用基于每个组件 `useState` 的属性网络** → zustand。
- **模板字符串的 className 三条件深层三元判断** → clsx（若为变体形态，则使用 cva）。
