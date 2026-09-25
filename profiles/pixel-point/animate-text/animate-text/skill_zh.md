# 文本动画

使用此技能作为基于生成 JSON 合同的文本动画目录。

使用 `assets/specs/<id>.json` 获取可移植的运动合同。使用 `assets/effects/<id>.json` 获取精确的动画重制，包括内容、渲染算法、播放、运行时、主机要求、渲染合同和库适配器。

此技能共包含 24 个规范。网站目前展示了其中的 20 个。

## 使用场景

在以下情况下使用此技能：

- 动画化标题、标签、计数器、编辑文案或文本交换
- 匹配命名效果 ID，例如 `soft-blur-in`、`typewriter`、`shared-axis-y` 或 `kinetic-center-build`
- 从精选目录中选择运动模式并将其转换为目标堆栈
- 在不依赖示例组件的情况下，在另一个堆栈中重制当前动画行为
- 使用 WAAPI、Motion / motion.dev、GSAP、CSS、Lottie、Rive 或其他渲染器实现相同的规范

## 工作流程

1. 确定用户是否需要：
   - 可见效果的精确网站版本
   - 运动合同的便携式翻译
2. 如果用户指定了效果 ID，则读取 `assets/specs/<id>.json` 或运行 `node scripts/get-spec.mjs <id>`。
3. 否则使用 `references/catalog.md` 或可选运行：
   - `node scripts/list-specs.mjs`
   - `node scripts/find-spec.mjs "<query>"`
4. 当用户需要运动意图的便携式翻译时，使用 `assets/specs/<id>.json`。
5. 当用户需要精确生成的动画行为时，使用 `assets/effects/<id>.json` 或 `node scripts/get-effect.mjs <id>`。
6. 如果用户指定了目标动画库，将其视为绑定。遵循 `showcase.library_selection` 并仅使用匹配的 `showcase.library_adapters.<library>` 块。
7. 对于精确重制，遵循 `showcase.renderer`、`showcase.playback`、`showcase.timing`、`showcase.runtime`、`showcase.stage`、`showcase.rendering_contract`、`showcase.library_selection` 和 `showcase.library_adapters`，而不是仅从便携式规范中推断的假设。
8. 将 `showcase.stage` 视为动画主机要求。除非用户明确要求该 UI，否则不要从源网站复制排版、颜色、填充、卡片边框或页面布局。
9. 将效果应用于现有部分时，保留该部分的文本。仅将 `showcase.content` 用作演示/备用文案，除非用户明确要求重制展示文案。

## 嵌套资源

- `references/catalog.md`：嵌套规范库的紧凑摘要
- `references/schema.md`：便携式规范和精确展示效果食谱的字段级架构
- `references/selection-guide.md`：选择正确效果系列的启发式方法
- `references/implementation-notes.md`：常见动画堆栈的翻译说明
- `assets/specs/*.json`：可移植运动合同
- `assets/effects/*.json`：精确生成的动画食谱
- `assets/catalog.json`：可见网站目录顺序和渲染器覆盖
- `assets/samples.json`：生成示例使用的样本文案
- `assets/runtime-presets.json`：运行时乘数和循环时间预设
- `assets/stage-presets.json`：动画主机要求，非呈现样式
- `assets/renderer-recipes.json`：共享渲染器算法
- `assets/library-adapters.json`：WAAPI、Motion 和 GSAP 实现映射指导

## 可选辅助脚本

辅助脚本是无须确定的快捷方式。它们需要 Node.js 20+。

- `node scripts/list-specs.mjs` 以 JSON 格式打印嵌套规范元数据
- `node scripts/get-spec.mjs <id>` 以 JSON 格式打印一个可移植运动规范
- `node scripts/get-effect.mjs <id>` 以 JSON 格式打印一个精确生成的动画食谱
- `node scripts/find-spec.mjs "<query>"` 返回按元数据排序的可能匹配

如果 Node 不可用，核心技能仍可通过 Markdown 参考和 JSON 资源单独工作。

## 翻译规则

- 精确保留 `target`：`whole`、`per-character`、`per-word` 或 `per-line`。
- 将 `enter` 和 `exit` 持续时间、缓动和错开直接映射到目标堆栈。
- 当目标堆栈支持时，保留变换、不透明度、模糊、缩放、旋转和间距字段。
- 对于布局感知效果（如 `kinetic-center-build` 或 `short-slide-down`），使用精确的效果食谱，而不是将效果扁平化为通用错开。
- 对于精确动画重制，保留 `assets/effects/<id>.json` 中的 `showcase.renderer`、`showcase.playback`、`showcase.timing`、`showcase.runtime`、`showcase.stage`、`showcase.rendering_contract` 和 `showcase.library_adapters` 字段。
- 不要替换请求的动画库。如果用户要求 GSAP，则导入并使用 GSAP；如果用户要求 Motion，则导入并使用 Motion；如果用户要求 WAAPI，则使用 `Element.animate`。
- 当针对 Motion 或 GSAP 时，使用匹配的 `showcase.library_adapters.motion` 或 `showcase.library_adapters.gsap` 块进行导入、时间单位转换、缓动转换、关键帧形状、完成和渲染器特定说明。
- 仔细阅读 `showcase.engine_notes` 和 `showcase.reproduction_notes`。它们描述了实现视觉一致性所需的堆栈特定细节。
- 对于精确网站行为，实现完整的 `showcase.playback` 循环。除非用户明确要求一次性揭示，否则不要在第一次进入动画时停止。
- 如果渲染器食谱指示等待阶段完成，则要么等待动画/补间 Promise，要么休眠计算阶段总时间，不要同时进行。

## 注意事项

- 公共网站使用嵌套库的精选子集。技能仍可以使用当前网站上未显示的额外嵌套规范。
- `assets/specs/*.json` 是权威的可移植运动合同。
- `assets/effects/*.json` 是权威的精确动画重制合同。
- 隐藏效果在精确效果食谱中具有 `"showcase": null`。
- 如果散文注释与 JSON 字段冲突，则优先考虑 JSON。
