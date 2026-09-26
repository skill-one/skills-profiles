# remocn

复制粘贴用于 Remotion 视频的组件。组件通过 `shadcn` 安装，并放置在
`components/remocn/` — 你拥有这些代码。

## 目录位于 remocn.dev

这个技能不包含组件目录的副本。大约有 240 个组件，它们会变化；一个捆绑的副本会默默过时。请查阅实时文档。

**组件搜索从这里开始：**

```
https://remocn.dev/llms-components.txt
```

每个类别一个表格，所有可安装的组件，每行包含 `Use for` / `Avoid for`、自然长度、氛围、等级、依赖项和指向其完整页面的链接。扫描它，筛选出，然后只获取你筛选出的页面。

**一个组件的完整参考** — 带描述的属性、示例用法、所有使用/不使用说明 — 是文档 URL 加上 `.md` 后缀：

```
https://remocn.dev/docs/typography/blur-out-up.md
https://remocn.dev/docs/transitions/whip-pan.md
https://remocn.dev/docs/ui/components/dialog.md
```

索引为你提供每个组件的确切 URL — 不要从名称猜测部分，几个组件位于不太明显的地方。

使用你的环境提供的任何工具（网络抓取工具、`curl`、`WebFetch`）获取。如果网络不可用，请说明并停止 — 不要凭记忆编造属性、默认值或持续时间，也不要替换你没有阅读的组件。错误的属性名会在构建时失败；编造的持续时间会默默裁剪动画。

## 安装

前提条件：一个 Remotion 项目 (`npx create-video@latest`)。

```bash
shadcn add @remocn/blur-out-up
```

`@remocn/<name>` 是规范命名空间形式（在 `components.json` 中的 `registries` 下配置）。纯注册 URL `https://remocn.dev/r/<name>.json` 也有效。

### 依赖项自动安装

许多组件通过 `registryDependencies` 拉取其他组件 — `shadcn` 递归地安装它们。例如，`shadcn add @remocn/typewriter` 也拉取 `@remocn/remocn-ui` 和 `@remocn/caret`。

- **`@remocn/remocn-ui`** 是共享的核心库（时间轴折叠钩子、主题上下文、颜色计算）。
  大多数 UI 基本元素依赖于它。你很少直接安装它。

## 两个等级

remocn 有两种组件 — 它们有 **不同的 API**：

- **动画等级** (`remocn`) — 文本动画、过渡、背景、UI 块模拟、品牌/社交卡片、完整组合。帧驱动。共享属性：`speed`（时间乘数），以及对于文本：`fontSize`、`color`、`fontWeight`。
- **UI 基本元素** (`remocn-ui`) — 时间轴驱动的 shadcn 风格基本元素（按钮、对话框、选择、命令菜单、工具提示...）。基于状态的属性 (`state`、`style`、`variant`、`theme`)。**没有 `speed` 属性。** 基于 `@remocn/remocn-ui` 构建。

索引的 `Tier` 列告诉你在打开页面之前你在查看哪种类型的组件。

## 组件模式

等级不同，约定也不同 — 不要在基本元素上假设动画等级的属性。

### 动画等级 (`remocn`)

- 每个组件命名 `Props` 接口（例如 `BlurOutUpProps`）。
- `speed?: number` — 全局时间乘数（默认 `1`），作为 `frame * speed` 应用。
- 文本组件：`fontSize`、`color`、`fontWeight`。
- 过渡：小写工厂（例如 `whipPan(props)`）返回 `TransitionPresentation` — 通过 `presentation` 传递给 `TransitionSeries.Transition`，使用 `linearTiming` / `springTiming` 调整节奏。
- `className?: string` 在根元素上。

并非所有归入过渡类别的都被视为呈现：`slide-swap` 和 `spring-settle` 是场景序列器，它们接受一个 `scenes` 数组并拥有整个时间轴。页面会说明你拥有的是哪种。

### UI 基本元素 (`remocn-ui`)

- 基于状态，**不是** `speed` 基于的：`state`（例如 `"open"` / `"closed"`）、`style`、`variant`、`size`、`theme?: Partial<RemocnTheme>`。
- 打开/关闭/活动状态纯粹是时间轴（关键帧预设）的函数。
- 使用触发元素组合模态层基本元素（对话框、警报对话框、抽屉） — 查看每个组件的示例。

### 动画 API

```tsx
import { interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

const opacity = interpolate(frame, [0, 30], [0, 1], { extrapolateRight: "clamp" });
const scale = spring({ fps, frame, config: { damping: 12, mass: 1, stiffness: 100 } });

// 确定性随机（永远不要使用 `Math.random()`）
import { random } from "@remotion/random";
const jitter = random(`seed-${frame}`);
```

### 组合结构

```tsx
import { Sequence, Series } from "remotion";

<Sequence from={30} durationInFrames={60}>
  <Typewriter text="npm install remocn" />
</Sequence>

<Series>
  <Series.Sequence durationInFrames={60}><SceneA /></Series.Sequence>
  <Series.Sequence durationInFrames={60}><SceneB /></Series.Sequence>
</Series>
```

### 画布与时间

- **画布标准：** `1280×720 @ 30fps`。组件是为它布局的。
- **`Length` 是组件自身的运动，不是整个节拍。** 对于过渡，它是传递给 `linearTiming` / `springTiming` 的值；对于其他所有内容，它是动画完成的帧。将其视为 `Sequence` 的地板，并在元素应该在它稳定后留在屏幕上时添加保持时间。`state-driven` 意味着组件根据其 `state` 属性渲染，并且没有自己的持续时间。
- **氛围匹配：** 每个条目都带有 `vibe` 标签 (`tech`/`premium`/`data`/`clean`/`playful`/
  `social`/`paper`) — 选择与品牌和预算相匹配的组件。`paper` 是定格动画套件：一个量化为每秒约 10 个姿势的时钟，手写和墨水。这些组件被视为一个世界，所以最好将它们彼此混合，而不是与平滑等级混合。

## 设计默认值 — 避免AI垃圾

你自己的**添加**（文本、场景铬、卡片 — 不是预构建的组件）保持克制：
默认跟踪、句子大小写、实心文本颜色、微妙的 1px 抬升 — 没有装饰性字母间距、ALL-CAPS、渐变文本填充或发光阴影。永远不要从其本质就是效果（`tracking-in`、社交卡片渐变、设计好的抬升）的组件中剥离这些特征。

完整的 do/avoid 示例、设计令牌、运动原则和反模式列表位于 Craft 部分：

```
https://remocn.dev/docs/craft/design-defaults.md
https://remocn.dev/docs/craft/motion-principles.md
https://remocn.dev/docs/craft/anti-patterns.md
```

## 注意事项（remocn 特定）

- **终端滚动是即时的** — 步进函数 `translateY`，永远不要对滚动使用弹簧/缓动。
- **分割布局上的 `overflow: hidden`** — 防止宽度动画期间内容断裂。
- **光标闪烁是确定的** — `Math.floor(frame / 15) % 2 === 0`，不是间隔。
- **静态文件放在 `public/` 中** — 通过 `staticFile('cursor.svg')` 加载，而不是导入。
- **社交卡片离线渲染** — `avatarUrl=""` / `coverUrl=""` 回退到渐变；不会获取。

一般的 Remotion 规则（不使用 `Math.random()`、不使用 `setInterval`、动画 `transform` 而不是 `top`/`left`、在渲染前加载字体）位于 `remotion-best-practices` 技能中。

## 组合视频

不要堆砌组件 — 组合一个故事。当被要求制作完整视频（“制作产品演示”、“版本日志视频”、“我落地页的介绍”）时：

1. **决定策略** — 使用现成模板 vs 从组件组合 vs 构建新组件。参见
   `references/anatomy.md` §1。
2. **遵循节拍** — 产品演示是 Hook → 定位 → 产品揭示 → 功能 → 证明 →
   CTA（最后两项可选）。参见 `references/anatomy.md` §2。
3. **使用配方** — `references/archetypes/index.md` 路由到每个架构类型的构建：内容契约
   （推断 → 询问 → 占位符）、持续时间变体、节拍→组件插槽，以及一个工作的
   `<TransitionSeries>` 骨架。
4. **从 `https://remocn.dev/llms-components.txt` 选择每个节拍的组件**；匹配 `vibe` 标签到品牌，并按上述画布与时间为其 `Sequence` 预算。
5. **检查质量标准** — 一个强调、句子大小写动态文本、真实内容、没有发光光晕、没有功能列表枚举。参见 `references/anatomy.md` §3。

## 参考

随此技能捆绑 — 不随组件变化的判断：

- `references/anatomy.md` — 组合完整视频：策略（模板/组合/新建）、产品演示节拍，以及良好与垃圾质量标准。
- `references/archetypes/index.md` — 路由到每个架构构建配方（产品演示旗舰 + 版本日志、功能公告、开源展示、CLI 工具演示、客户评价轮播、年度回顾、价格揭示、标志横幅）：内容契约、持续时间变体、节拍→插槽映射。

从 remocn.dev 获取 — 所有跟踪组件的内容：

- `https://remocn.dev/llms-components.txt` — 组件索引。始终从这里开始。
- `https://remocn.dev/docs/<section>/<name>.md` — 一个组件的完整参考。
- `https://remocn.dev/docs/craft/design-defaults.md` — 反垃圾默认值和设计令牌。
- `https://remocn.dev/docs/craft/motion-principles.md` — 适应 remocn 的运动原则。
- `https://remocn.dev/docs/craft/anti-patterns.md` — 常见生成错误及其修复。
- `https://remocn.dev/llms.txt` — 整个文档的索引，如果你需要其他内容。
