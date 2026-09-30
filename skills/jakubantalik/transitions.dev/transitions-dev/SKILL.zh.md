---
name: transitions-dev
description: 适用于 Web 应用的生产级 CSS 过渡效果。在实现通知徽章、下拉菜单、模态框、面板显示、页面过渡、卡片调整大小、数字弹出、文本交换、图标交换、成功检查、头像组悬停、错误状态抖动、搜索/输入清除、骨架加载器、闪烁文本、滑动标签、工具提示、交错文本显示、卡片悬停倾斜、加号到菜单变形、手风琴、吐司、点赞按钮、了解更多悬停、复选框勾选、旋转计数器、切换、AI 思考状态、推理流、流式文本、矩阵点加载器或横幅堆叠时使用。触发于"添加过渡"、"动画下拉菜单"、"使模态框平滑打开"、"交换图标"、"页面滑动"、"交错动画"、"打开/关闭过渡"、"使其动画化"、"淡入淡出"、"成功动画"、"表单错误"、"无效时抖动"、"悬停提升"、"头像堆叠悬停"、"清除搜索"、"骨架加载器"、"加载闪烁"、"闪烁文本"、"滑动标签"、"分段控制"、"工具提示"、"显示文本"、"倾斜卡片"、"3D 悬停倾斜"、"光标眩光"、"加号到菜单"、"FAB 变形"、"手风琴"、"可折叠"、"展开/折叠"、"披露"、"吐司"、"提示条"、"点赞按钮"、"心形动画"、"了解更多箭头"、"复选框"、"勾选动画"、"旋转计数器"、"里程表"、"老虎机数字"、"切换"、"开关"、"思考状态"、"AI 状态行"、"代理推理"、"推理流"、"流式文本"、"流式输入"、"矩阵加载器"、"点加载器"、"横幅堆叠"、"堆叠吐司"。还包括"运动标记"、"扫描自定义过渡"、"用运动标记替换硬编码持续时间"、"标记我的动画"，以及命令"过渡显示"、"过渡审查"、"过渡应用"、"过渡优化"。
---

# Transitions.dev

包含三十二种便携式 CSS 过渡效果，每个效果都使用 `t-*` 选择器命名空间，并具有语义 CSS 自定义属性。即插即用：粘贴代码片段，连接文档中记录的 HTML 钩子，即可完成。无需框架依赖，无需特定演示的标记，并且每个代码片段都包含 `prefers-reduced-motion` 保护。

## 快速参考

| 过渡效果 | 使用场景 | 参考 |
| --- | --- | --- |
| **卡片调整大小** | 当容器的布局状态发生变化时，对容器的宽度或高度进行插值动画。 | [01-card-resize.md](./01-card-resize.md) |
| **数字弹出** | 当数字更新时，以模糊滑入的方式重新进入每个数字。 | [02-number-pop-in.md](./02-number-pop-in.md) |
| **通知徽章** | 将一个小徽章滑到触发器上，然后弹出圆点。 | [03-notification-badge.md](./03-notification-badge.md) |
| **文本状态交换** | 使用模糊的上下过渡效果，原地交换文本。 | [04-text-states-swap.md](./04-text-states-swap.md) |
| **菜单下拉** | 打开一个源感知的下拉菜单，从其触发器处展开。 | [05-menu-dropdown.md](./05-menu-dropdown.md) |
| **模态框打开/关闭** | 打开时缩放模态对话框，关闭时进行更柔和的缩放。 | [06-modal.md](./06-modal.md) |
| **面板显示** | 使用交叉模糊效果将面板滑入页面区域。 | [07-panel-reveal.md](./07-panel-reveal.md) |
| **页面并排** | 在两个并排的页面之间滑动（列表 ↔ 详情，步骤 1 ↔ 步骤 2）。 | [08-page-side-by-side.md](./08-page-side-by-side.md) |
| **图标交换** | 在同一位置使用模糊和缩放效果交叉淡入淡出两个图标。 | [09-icon-swap.md](./09-icon-swap.md) |
| **成功检查** | 组合淡入 + 旋转 + Y 轴摆动 + 路径绘制来庆祝完成的操作。 | [10-success-check.md](./10-success-check.md) |
| **头像组悬停** | 在项目行上使用距离衰减提升，返回时使用弹性弹簧。 | [11-avatar-group-hover.md](./11-avatar-group-hover.md) |
| **错误状态抖动** | 每个段使用三次贝塞尔曲线抖动，自动恢复边框 + 消息。 | [12-error-state-shake.md](./12-error-state-shake.md) |
| **输入清除带溶解** | 文本字段清除时飞出 + 每个单词的轨迹。 | [13-input-clear-dissolve.md](./13-input-clear-dissolve.md) |
| **骨架加载器显示** | 脉冲占位符，然后交叉淡入 + 交叉模糊到加载的内容。 | [14-skeleton-reveal.md](./14-skeleton-reveal.md) |
| **闪烁文本** | 在静音文本上循环扫过高亮带（纯 CSS）。 | [15-shimmer-text.md](./15-shimmer-text.md) |
| **选项卡滑动** | 在分段控制中，将活动药丸在选项卡之间滑动。 | [16-tabs-sliding.md](./16-tabs-sliding.md) |
| **工具提示打开/关闭** | 延迟淡入 + 缩放，立即淡出，在触发器之间移动。 | [17-tooltip.md](./17-tooltip.md) |
| **文本显示** | 堆叠文本行使用交错模糊上升，安静淡出。 | [18-texts-reveal.md](./18-texts-reveal.md) |
| **卡片悬停倾斜** | 在 3D 中向指针倾斜卡片，并带有光标跟踪眩光。 | [19-card-tilt.md](./19-card-tilt.md) |
| **加号到菜单变形** | 将圆形触发器变形为它打开的菜单 / 面板。 | [20-plus-menu-morph.md](./20-plus-menu-morph.md) |
| **手风琴展开** | 通过网格行增长 / 收缩面板，并带有旗标翻转。 | [21-accordion.md](./21-accordion.md) |
| **吐司打开/关闭** | 从下方升起吐司，带有淡入 + 交叉模糊，进入速度慢于退出速度。 | [22-toast.md](./22-toast.md) |
| **点赞按钮** | 点赞时用弹出 + 粒子爆发填充心形。 | [23-like-button.md](./23-like-button.md) |
| **了解更多悬停** | 悬停时滑动旗标，并将其手臂展开成箭头。 | [24-learn-more-hover.md](./24-learn-more-hover.md) |
| **复选框勾选** | 填充框，然后绘制勾选标记。 | [25-checkbox-check.md](./25-checkbox-check.md) |
| **旋转计数器** | 使用垂直运动模糊旋转老虎机数字轮。 | [26-spinning-counter.md](./26-spinning-counter.md) |
| **切换** | 切换拇指以进行双弹跳过冲。 | [27-toggle.md](./27-toggle.md) |
| **思考状态** | 在它保持时闪烁状态行，然后将其交换到下一个状态。 | [28-thinking-states.md](./28-thinking-states.md) |
| **推理流** | 在循环中每次以两行的方式逐步代理推理转录。 | [29-reasoning-stream.md](./29-reasoning-stream.md) |
| **流式文本** | 通过柔和的交叉模糊逐个解析流式单词。 | [30-streaming-text.md](./30-streaming-text.md) |
| **矩阵点加载器** | 以扫描 / 闪烁 / 轨道 / 脉冲模式脉冲 4×4 点矩阵。 | [31-matrix-loader.md](./31-matrix-loader.md) |
| **横幅堆叠** | 像吐司一样堆叠横幅 — 新的从上方升起，旧的向后推。 | [32-banner-stacking.md](./32-banner-stacking.md) |

## 决策规则

当用户请求过渡效果时，首先匹配可见的 UI 元素，然后匹配动词：

- **触发器 + 顶部漂浮的小圆点** → 通知徽章。
- **触发器 + 从其处增长的表面** → 下拉菜单（锚定，源感知）或模态框（居中，无锚定）。
- **滑入页面区域的表面** → 面板显示。
- **两个屏幕，列表 ↔ 详情或步骤 1 ↔ 步骤 2** → 页面并排。
- **元素更改宽度或高度** → 卡片调整大小。
- **元素的原地文本内容更改** → 文本状态交换。
- **同一槽位中的两个图标** → 图标交换。
- **数字更新** → 数字弹出。
- **确认 / 成功 / “完成”时刻**（勾选标记，支付处理，文件上传）→ 成功检查。
- **在水平堆栈中悬停项目**（头像，标签，分段按钮，标签药丸）→ 头像组悬停。
- **表单验证错误 / “这是错误的”反馈**（无效字段，错误的 PIN，重复名称）→ 错误状态抖动。
- **清除文本字段**（搜索框 × 按钮，过滤器重置）→ 输入清除带溶解。
- **加载后交换到真实内容的占位符**（列表行，卡片，个人资料标题）→ 骨架加载器显示。
- **应感觉活跃的进行中 / “思考”文本**（加载标签，流式状态）→ 闪烁文本。
- **具有移动高亮的小水平互斥选项**（视图切换器，分段控制，过滤器选项卡）→ 选项卡滑动。
- **悬停/聚焦提示**（图标工具提示，信息气泡）→ 工具提示打开 / 关闭。
- **堆叠的标题 + 带节奏进入的辅助行**（英雄副本，空状态，引导步骤）→ 文本显示。
- **应 3D 反应到指针悬停的卡片 / 图标**（产品卡片，封面艺术，会员卡，带或不带光晕）→ 卡片悬停倾斜。
- **圆形触发器变成它打开的表面**（+ FAB 变形为菜单 / 面板，组合按钮展开）→ 加号到菜单变形。如果表面是一个仅仅是从此触发器处增长的 *独立* 弹出层，则使用菜单下拉菜单。
- **可折叠身体的标题**（设置组，常见问题解答，过滤器部分，“显示更多”，披露）→ 手风琴展开。
- **没有明显匹配** → 落回 `transitions reveal` 并让用户选择。不要猜测。

如果有两个过渡效果可以匹配，优先选择低开销的（卡片调整大小优于面板显示，下拉菜单优于模态框，成功检查优于完整模态框庆祝）除非设计明确要求更重的表面。成功检查是纯动画 — 如果你还需要从旋转器交换到检查，请将其与 **图标交换** 配对。

## 命令

技能暴露了四个命名空间动词，代理应识别，除了直接过渡请求。每个命令都以 `transitions` 开头，因此调用永远不会与其他项目中安装的技能的动词冲突。

### transitions reveal — 列出所有过渡效果

**触发短语：** `transitions reveal`，"显示过渡效果"，"列出所有过渡效果"，"这个技能中有哪些过渡效果"，"显示过渡效果目录"。

**行为：** 以编号纯文本列表的形式打印三十二种过渡效果 — 名称，一句话摘要，以及匹配的参考文件名。重用上面 `## 快速参考` 中的行；不要编造新的副本。不需要项目访问权限。

### transitions review — 审计项目是否适用

**触发短语：** `transitions review`，"审查我的项目"，"审计我的动画"，"transitions.dev 哪里能帮上忙"，"找到使用这个技能的地方"。

**行为：**

1. 在工作区中搜索指示：`transition:` 声明，`@keyframes`，样式文件中硬编码的 `ms` / `s` 持续时间，匹配决策规则模式的组件（模态框，下拉菜单，徽章，搜索输入，骨架，选项卡，工具提示，…）。
2. 对于每个命中项，根据决策规则选择最佳匹配的过渡效果。
3. 按文件分组输出编号列表：
   - `path/to/Component.tsx:L42` — 看起来像下拉菜单打开，建议 **menu-dropdown** (`05-menu-dropdown.md`)。
   - 跳过已经使用 `t-*` 类的临时过渡效果。
4. 不要编辑任何内容。以："在任意行上运行 `transitions apply` 来安装建议的过渡效果" 结尾。

### transitions apply — 安装最佳匹配的过渡效果

**触发短语：** `transitions apply`，"在这里应用过渡效果"，"添加正确的过渡效果"，"安装 transitions-dev"，"修复这个元素的动画"。

**行为：**

1. 读取上下文：当前打开的文件，光标最近的元素，周围的 CSS / JSX。如果用户明确指定了过渡效果（例如 `transitions apply menu-dropdown`），则使用它。
2. 运行 `## 决策规则` 中的决策规则在该上下文中，并选择 **一个** 过渡效果。如果有两个可以匹配，优先选择低开销的（与现有规则使用的相同破折号规则）。
3. 提出一个单行建议："我会在这里应用 **menu-dropdown**，因为元素从触发器处打开并且是锚定的。确认安装？"。
4. 确认后，逐字遵循 `## 输出格式` 中现有的五步程序（根块，代码片段，钩子，reduced-motion 保护，如果需要则 JS 命令）。
5. 如果代理不能有信心选择单个过渡效果，则回退到 `transitions reveal` 并要求用户选择。

### transitions refine — 用运动标记替换临时运动

**触发短语：** `transitions refine`，"优化我的过渡效果"，"扫描临时过渡效果"，"用运动标记替换硬编码持续时间"，"标记我的动画"，"调整持续时间和缓动"，"审计我的自定义关键帧"，"使时间一致"，"对齐到运动标记"。

**行为：**

1. **扫描整个项目**（不仅限于专用样式表 — 还包括内联 `style=` / CSS-in-JS，styled-components，`<style>` 块，Tailwind 任意值如 `duration-[300ms]`）中的临时运动：`transition` / `animation` 短语和长格式，自定义 `@keyframes` 块，硬编码持续时间（`…ms` / `…s`），缓动（`cubic-bezier(...)` 或关键词），平移距离（`px`），`scale(...)`，和 `blur(...)`。
2. 对于每个值，根据周围的 选择器 / 组件推断 **运动做什么**（模态框关闭，下拉菜单打开，工具提示，徽章出现，文本显示，页面滑动，抖动，…）从 `## 决策规则`。对于 `@keyframes` 块，读取驱动它的 `animation` 并判断关键帧自己的持续时间和缓动。
3. **关键决策点是使用情况，而不是原始数字。** 在 `## 运动标记` 中查找推断的使用情况，并建议与文档中记录的使用情况匹配的标记 — 只有当使用情况一致时。300ms 模态框关闭映射到 `--duration-quick` 因为两者都是 "模态框关闭"，即使数字不同。如果一个值的用途与 **没有** 标记的用途匹配，则将其列为 `no matching token usage` 并保留不变 — 永远不要因为数字接近而强制交换。
4. 按文件分组输出编号列表，仅显示应更改的值，每个值作为 `path/to/Component.css:L42` — `modal close: 300ms → var(--duration-quick) (150ms)`，`ease → var(--ease-smooth-out)`。对于由关键帧驱动的运动，建议驱动 `animation` 的持续时间/缓动。
5. 不要编辑任何内容。以："确认任意行以应用更改，或运行 `transitions apply` 来安装完整的过渡效果" 结尾。

## 运动标记

三十二种过渡效果背后的共享运动比例 — 与 [transitions.dev](https://transitions.dev) 运动标记选项卡暴露的相同标记。它们位于 [`_root.css`](./_root.css) 的顶部，因此一旦导入，您就可以将它们中的任何一个作为 `var(--…)` 引用（例如 `transition: transform var(--duration-fast) var(--ease-smooth-out)`）。

`transitions refine` 将每个现有值映射到下面的使用情况，然后建议要引用的标记。基于 **使用情况** 而不是原始数字匹配 — 一个 300ms 模态框关闭仍然映射到 `--duration-quick` (150ms)。

**持续时间**

| 标记 | 值 | 使用情况 |
| --- | --- | --- |
| `--duration-stagger` | `40ms` | 每个项目的交错偏移 |
| `--duration-micro` | `80ms` | 工具提示/路径延迟，抖动段，大交错 |
| `--duration-quick` | `150ms` | 模态框/下拉菜单关闭，文本交换，工具提示出现 |
| `--duration-fast` | `250ms` | 图标交换，下拉菜单/模态框打开，选项卡滑动，页面滑动 |
| `--duration-medium` | `350ms` | 面板关闭，吐司关闭 |
| `--duration-slow` | `400ms` | 面板打开，骨架内容显示，输入清除 |
| `--duration-very-slow` | `500ms` | 强调时刻，徽章出现，文本显示，成功检查 |

**缓动**

| 标记 | 值 | 使用情况 |
| --- | --- | --- |
| `--ease-smooth-out` | `cubic-bezier(0.22, 1, 0.36, 1)` | 模态框/下拉菜单/面板打开 + 关闭，页面滑动，调整大小，位置更改 |
| `--ease-in-out` | `ease-in-out` | 图标交换，文本交换，文本显示，骨架显示 |
| `--ease-out` | `ease-out` | 工具提示打开 / 关闭 |
| `--ease-linear` | `linear` | 闪烁，骨架脉冲，旋转器 |
| `--ease-bounce` | `cubic-bezier(0.34, 1.36, 0.64, 1)` | 徽章弹出打开 |
| `--ease-bounce-strong` | `cubic-bezier(0.34, 3.85, 0.64, 1)` | 弹性悬停出（头像返回） |

**距离**

| 标记 | 值 | 使用情况 |
| --- | --- | --- |
| `--distance-micro` | `4px` | 文本交换 |
| `--distance-small` | `6px` | 错误抖动（小段） |
| `--distance-base` | `8px` | 徽章对角线显示，页面滑动，错误抖动（大段） |
| `--distance-medium` | `12px` | 文本显示 |
| `--distance-large` | `30px` | 勾选徽章出现 |

**缩放**

| 标记 | 值 | 使用情况 |
| --- | --- | --- |
| `--scale-large` | `0.96` | 模态框打开 / 关闭 |
| `--scale-medium` | `0.97` | 下拉菜单打开 |
| `--scale-small` | `0.98` | 工具提示打开 |
| `--scale-tiny` | `0.99` | 下拉菜单关闭 |

**模糊**

| 标记 | 值 | 使用情况 |
| --- | --- | --- |
| `--blur-small` | `2px` | 面板显示，图标交换，文本交换，骨架显示，数字弹出 |
| `--blur-medium` | `3px` | 页面滑动，文本显示 |
| `--blur-large` | `8px` | 成功检查打开 |

## 通用安装

将 [`_root.css`](./_root.css) 复制到您的项目中 **一次** 并导入它（或将其 `:root` 块粘贴到您的全局样式表中）。它以共享的 **运动标记比例** (`--duration-*`，`--ease-*`，`--distance-*`，`--scale-*`，`--blur-*` — 见 `## 运动标记`）开头，然后是所有三十二种过渡效果的语义可调变量。每个代码片段都从此处读取这些名称 — `--resize-*`，`--badge-*`，`--dropdown-*`，`--clear-*`，`--shimmer-*`，`--tabs-*`，`--tt-*`，`--stagger-*`，`--tilt-*`，`--morph-*`，`--acc-*`，以及其他。

每个参考文件也重述了该代码片段需要的仅变量，因此您可以在不拉取整个块的情况下安装单个过渡效果。不要复制块 — 如果 `_root.css` 已经导入，则跳过重新粘贴任何每个代码片段的 `:root`。

在 [transitions.dev](https://transitions.dev) 的实时演示中使用的 `--pX-*` 源标记**故意不**导出。可调值被重命名为语义名称，以便用户拥有设计词汇。几个过渡效果（输入清除，闪烁文本，选项卡，工具提示）带有**颜色**标记，这些标记因主题而异 — 每个参考文件都记录了 `html[data-theme="dark"]` 的覆盖。

## 输出格式

当将过渡效果插入用户的项目中时：

1. **将 `_root.css` 中的变量** **安装到用户的全局样式表中**，但前提是它们尚未存在——如果仅安装单个过渡效果，则只需从参考文件中复制每个片段的 `:root` 块。如果通用块已经导入，则**不要**重复它。
2. **从相关的参考文件中** **逐字粘贴所选过渡效果的 CSS**。不要重写选择器，不要将过渡效果简化为简写形式，不要删除 `will-change`。这些片段已经过调整和测试。
3. **连接文档中记录的 HTML 钩子**——类名（`.t-dropdown`, `.t-modal`, `.t-success-check`, `.t-avatar`, `.t-clear`, `.t-skel`, `.t-shimmer`, `.t-tabs`, `.t-tt`, `.t-stagger`, `.t-tilt`, `.t-morph`, `.t-acc`, …）和状态属性（`data-open`, `data-state`, `data-page`, `data-origin`, `aria-selected`, `aria-expanded`, `.is-open`, `.is-closing`, `.is-error`, `.is-shaking`, `.has-value`, `.is-clearing`, `.is-pulsing`, `.is-revealed`, `.is-shown`, `.is-hiding`, `.is-hover`, `.is-tilting`）。
4. **保留 `@media (prefers-reduced-motion: reduce)` 块**。每个片段都附带一个。删除它会导致组件无法通过无障碍性审核。
5. **对于需要 JS 的过渡效果**（下拉菜单、模态框、文本交换、数字弹出、页面滑动、成功检查、头像组悬停、错误状态抖动、输入清除、骨架加载、选项卡滑动、提示框、文本显示、卡片悬停倾斜、加号→菜单变形、手风琴展开），从参考文件中复制小的编排片段，并将选择器调整为用户的 DOM。保留时间读取（`getComputedStyle(...)getPropertyValue("--…")`），以便持续时间与 `:root` 值保持同步。闪烁文本是**纯 CSS**——不需要 JS。

保持差异小：仅编辑引入过渡效果所需的文件。不要重命名用户现有的变量，不要重新格式化无关的 CSS，不要引入运动库。

## 常见错误

- **在下拉菜单/模态框中移除关闭状态类清理**——如果没有 `setTimeout` 删除 `.is-closing`，下一个打开将直接从关闭的缩放效果跳转，而不是从静止的预打开缩放效果开始。
- **在文本交换、数字弹出、成功检查重播和错误状态抖动中忘记重排**——类/属性移除和重新添加之间的 `void el.offsetWidth`（或 `offsetHeight`）是确保动画重播的关键。
- **对单个容器进行动画**而不是内部元素——对于徽章，动画点，而不是触发器；对于页面滑动，动画页面部分，而不是容器。
- **用 `transition: all` 替换 `transition: …`**——每个片段都故意枚举了确切的属性，以便无关的样式更改不会免费搭乘。
- **在 CSS 中硬编码成功检查的 `stroke-dasharray`**——片段附带 `20` 作为占位符。用 1 向上舍入的 `path.getTotalLength()` 替换它，以匹配*你的*路径，否则笔触会预先显示或过度绘制。
- **在 CSS 中设置 `transition-timing-function`**用于头像组悬停——它必须在 JS 中设置*在* `--shift` / `--scale-active` 写入之前，以便弹跳的 ease-out 仅在 `mouseleave` 时应用。
- **将 `.is-error` 和 `.is-shaking` 混合为同一个类**用于错误状态抖动——保持它们正交是允许抖动重播（移除→重排→重新添加）而不会使整个错误处理闪烁的原因。
- **在暗黑模式下将输入清除辉光保留在 `mix-blend-mode: multiply` 中**——切换到 `screen`，将 `--glow-opacity` 提高到约 0.85，并在 JS 中绘制白色渐变。
- **忘记在无过渡效果的情况下设置选项卡药丸的初始位置**——在首次绘制和调整大小时，使用 `transition: none` 设置 `transform` + `width`（然后重排+恢复），否则药丸会从 `translateX(0)` / `width: 0` 动画进入。
- **在倾斜元素本身上跟踪指针**用于卡片悬停倾斜——将 `pointermove` 绑定到平坦的外部 `.t-tilt` 包装器，而不是 `.t-tilt-card`，否则旋转的边缘会滑到光标下方，悬停会闪烁。
- **在手风琴网格轨道上设置填充**——将填充放在 `.t-acc-panel-inner` 上，绝不能放在 `.t-acc-panel` 上；`0fr` 轨道上的填充会留下残高的条带，因此面板永远不会完全关闭。
- **变形手风琴箭头的 `d` 路径**——CSS `d:` 路径插值仅限于 Chrome，因此在移动 Safari / Firefox 上永远不会动画。将箭头垂直翻转（`transform: scaleY(-1)`）而不是——它就像路径变形一样穿过中点的水平线，并且可以在任何地方工作。保持路径关于其 viewBox 中心对称，并添加 `vector-effect: non-scaling-stroke`，以便笔触在翻转过程中保持不变。这就是片段附带的内容。

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
- [13-input-clear-dissolve.md](./13-input-clear-dissolve.md) — 带溶解的输入清除
- [14-skeleton-reveal.md](./14-skeleton-reveal.md) — 骨架加载和显示
- [15-shimmer-text.md](./15-shimmer-text.md) — 闪烁文本
- [16-tabs-sliding.md](./16-tabs-sliding.md) — 选项卡滑动
- [17-tooltip.md](./17-tooltip.md) — 提示框打开/关闭
- [18-texts-reveal.md](./18-texts-reveal.md) — 文本显示
- [19-card-tilt.md](./19-card-tilt.md) — 卡片悬停倾斜
- [20-plus-menu-morph.md](./20-plus-menu-morph.md) — 加号→菜单变形
- [21-accordion.md](./21-accordion.md) — 手风琴展开
- [22-toast.md](./22-toast.md) — 提示框打开/关闭
- [23-like-button.md](./23-like-button.md) — 喜欢按钮
- [24-learn-more-hover.md](./24-learn-more-hover.md) — 了解更多悬停
- [25-checkbox-check.md](./25-checkbox-check.md) — 复选框勾选
- [26-spinning-counter.md](./26-spinning-counter.md) — 旋转计数器
- [27-toggle.md](./27-toggle.md) — 切换
- [28-thinking-states.md](./28-thinking-states.md) — 思考状态
- [29-reasoning-stream.md](./29-reasoning-stream.md) — 推理流
- [30-streaming-text.md](./30-streaming-text.md) — 流式文本
- [31-matrix-loader.md](./31-matrix-loader.md) — 矩阵点加载器
- [32-banner-stacking.md](./32-banner-stacking.md) — 横幅堆叠
- [_root.css](./_root.css) — 独立的全局安装块，可直接导入。
