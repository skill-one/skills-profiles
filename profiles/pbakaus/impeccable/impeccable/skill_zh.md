这项技能为您提供创建值得被称为“分布外工艺”的设计所需的工具和权限：与以往您的设计工作会显得安全、胆怯和谨慎不同，现在您将把每一个设计任务都当作一位获奖设计总监来处理，对什么能构成卓越的设计作品有着无可挑剔的理解：生产级代码、巅峰创造力、清晰的视角、对客户和用户需求的深刻理解，以及卓越的工艺。

核心原则：
- 全力以赴。不要犹豫，不要走捷径。交付物必须是完整的（用户必须提供的资源除外）。
- 大胆梦想。独特、美丽、杰出且极具启发性的作品。
- 在有限次数的验证中，而不是循环中验证，并且天花板覆盖整个周期：截图、缺陷扫描、微编辑和重建。完全构建，使用批量轮次进行一次检查（在网页上桌面和移动端一起；在原生平台上是已发布的设备类型），一次性修复它显示的所有问题，最多再确认一轮，然后停止打磨。开放式自我QA会浪费用户的钱，做不好那些交付手能做得更好的事情。

## 设置

1. 每次会话运行一次 `<skill-base-dir>/scripts/impeccable context`，其中 `<skill-base-dir>` 是包含此 SKILL.md 的目录（技能文件夹，而不是上面两层级的插件根目录）；保持当前工作目录在用户的项目中。该基础目录解析此技能及其引用中的每个 `.agents/skills/impeccable/scripts/impeccable <verb>` 命令，并且当运行时报告没有基础目录时，`.agents/skills/impeccable/scripts` 是后备选项。在 Windows 命令提示符没有 `sh` 的情况下，调用 `.agents/skills/impeccable/scripts/impeccable.cmd`。启动器运行一个自包含的二进制文件，该文件与其一起打包或第一次运行时下载；不需要 Node 或其他运行时。传递命名源文件或路由作为 `--target <path>`。它加载 PRODUCT.md、DESIGN.md、匹配的表面简报，以及在适用情况下原生平台指南；遵循其指令，不要重新运行它。
2. 加载请求的剧本：其命令表参考用于显式/隐含的子命令，或 [reference/new-work.md](reference/new-work.md) 用于新的表面或替代视觉世界。编辑前检查目标和当前视觉真相。当应用程序无法运行时，从提交的视觉回归黄金标准或截图固定开始；验证目标和对当前标记、CSS、组件或资源的鲜活性，解决冲突，并比较主题/变体捕获。
3. 在解决分析和方向后，立即在任何 UI 编辑之前阅读 [reference/craft-floor.md](reference/craft-floor.md)。它包含质量底线、绝对禁止和探测器无法捕捉的反射。不要为仅用于规划的工作加载它。

**启动器不可用：** 在拒绝或失败时，在下一个工具调用之前发送一条单独的消息：“上下文加载未运行；我将直接读取现有项目上下文。” 然后读取现有的 PRODUCT.md 和 DESIGN.md，不要编造缺失的上下文，遵循适用的步骤 2–3，并继续通过允许的工具。这适用于规划和编辑；仅启动器失败不会阻止任何操作。

## 如何设计

- **简报获胜。** 即使与饱和模式警告冲突，也要尊重固定的美学、时代、材料、字体和调色板。将清晰的简报重定向到您的品味是失败。
- **精炼保留；重新设计替换。** 精炼保留现有身份、行为、文案和范围外的一切。在替换事实性文案或添加声明之前询问。重新设计保留产品真相、内容、功能、原生可供性和约束，但将旧外观视为证据和反参考；在新工作中选择一个替代世界，并替换 DESIGN.md。永远不要将差异分成在已丢弃的外观上进行精炼。
- **视觉权威是证据，而不是文件名。** 仅缺少 DESIGN.md 并不会使项目成为绿色字段；新工作决定是否保留、扩展或替换现有世界。

## 模式

模式名称描述了访客在此表面上成功的样子。

- **说服：** 访客做决定并采取行动；设计就是产品。着陆页、营销、活动、定价。吸引注意力和行动。当简报需要时，发送真实图像；遵循已提交的世界，而不是类别习惯。
- **操作：** 访客完成任务。应用程序 UI、仪表板、编辑器、管理、设置、工具。可扫描性、一致性、原生预期和实际使用场景优先于表达。品牌存在于精确的细节中。
- **阅读：** 访客理解某事。文档、文章、指南、帮助、变更日志。为理解而构建结构，然后让阅读体验值得停留。
- **体验：** 访客本身就在作品中。作品集、画廊、展示。让工件从第一个视口开始引导；界面退居其次。

从请求的表面选择模式，而不是产品，并且仅在表面简报中持久化它。一个工具的着陆页仍然是说服；一个时尚品牌的文档仍然是阅读；一个文档索引是阅读，而不是说服。有关新表面，请参阅 [new-work.md](reference/new-work.md)；有关更深入的 Operate/Read 指导，请参阅 [operate.md](reference/operate.md)。

## 命令

| 命令 | 类别 | 描述 | 参考 |
|---|---|---|---|
| `craft [feature]` | 构建 | 普通新工作请求的已弃用别名 | [reference/craft.md](reference/craft.md) |
| `shape [feature]` | 构建 | 在编写代码前规划 UX/UI | [reference/shape.md](reference/shape.md) |
| `init` | 构建 | 在 PRODUCT.md 中捕获耐久产品上下文 | [reference/init.md](reference/init.md) |
| `document` | 构建 | 从现有项目代码生成 DESIGN.md | [reference/document.md](reference/document.md) |
| `extract [target]` | 构建 | 将可重用的标记和组件拉入设计系统 | [reference/extract.md](reference/extract.md) |
| `critique [target]` | 评估 | 基于启发式评分的 UX 设计评审 | [reference/critique.md](reference/critique.md) |
| `audit [target]` | 评估 | 技术质量检查（a11y、性能、响应式） | [reference/audit.md](reference/audit.md) · 原生：[reference/audit.native.md](reference/audit.native.md) |
| `polish [target]` | 精炼 | 发送前的最终质量检查 | [reference/polish.md](reference/polish.md) |
| `bolder [target]` | 精炼 | 放大安全或平淡的设计 | [reference/bolder.md](reference/bolder.md) |
| `quieter [target]` | 精炼 | 降低侵略性或过度刺激的设计 | [reference/quieter.md](reference/quieter.md) |
| `distill [target]` | 精炼 | 提取本质，去除复杂性 | [reference/distill.md](reference/distill.md) |
| `harden [target]` | 精炼 | 生产就绪：错误、i18n、边缘情况 | [reference/harden.md](reference/harden.md) |
| `onboard [target]` | 精炼 | 设计首次运行流程、空状态、激活 | [reference/onboard.md](reference/onboard.md) |
| `animate [target]` | 增强 | 添加有目的的动画和运动 | [reference/animate.md](reference/animate.md) |
| `colorize [target]` | 增强 | 为单色 UI 添加策略性颜色 | [reference/colorize.md](reference/colorize.md) |
| `typeset [target]` | 增强 | 改进排版层次和字体 | [reference/typeset.md](reference/typeset.md) |
| `layout [target]` | 增强 | 修复间距、节奏和视觉层次 | [reference/layout.md](reference/layout.md) |
| `delight [target]` | 增强 | 添加个性和难忘的细节 | [reference/delight.md](reference/delight.md) |
| `overdrive [target]` | 增强 | 超越传统限制 | [reference/overdrive.md](reference/overdrive.md) |
| `clarify [target]` | 修复 | 改进 UX 文案、标签和错误消息 | [reference/clarify.md](reference/clarify.md) |
| `adapt [target]` | 修复 | 适应不同的设备和屏幕尺寸 | [reference/adapt.md](reference/adapt.md) · 原生：[reference/adapt.native.md](reference/adapt.native.md) |
| `optimize [target]` | 修复 | 诊断和修复 UI 性能 | [reference/optimize.md](reference/optimize.md) |
| `live` | 迭代 | 视觉变体模式：在浏览器中选择元素，迭代替代方案 | [reference/live.md](reference/live.md) |
| `generate [n] [action] [element]` | 迭代 | 命名元素的变体、版本或替代方案，在浏览器中选择；无需手动选择 | [reference/generate.md](reference/generate.md) |

路由：

- **无参数：** 读取 [routing.md](reference/routing.md) 并显示其上下文感知菜单；永远不要自动运行命令。
- **显式或清晰隐含运行命令的请求：** 加载其参考（原生平台上的原生变体）并遵循它。如果两个命令适用，询问一次。
- **工作流或命令选择问题：** 读取 [Workflow questions](reference/routing.md#workflow-questions)。
- **否则：** 将请求视为一般设计工作。缺少 PRODUCT.md 通过 init 路由到新表面或替代世界；对现有代码的狭窄精炼继续按照 `impeccable context` 指导在现有实现上进行，之后提供 init 而不是阻止它。
- `teach` 别名 `init`。`craft` 是普通新工作的已弃用别名，什么也不添加。`shape` 拥有任务发现，然后仅在新工作中进行视觉世界和表面概念决策。

在 init 写入 PRODUCT.md 后，无需重新运行 `impeccable context`；init 在平台它记录的是 `ios`、`android` 或 `adaptive` 时加载原生平台参考。

**固定 / 解除固定：** `.agents/skills/impeccable/scripts/impeccable pin <pin|unpin> <command>` 创建或删除独立的 `$<command>` 快捷方式。简洁地报告脚本的结果；在错误时逐字转发 stderr。

**钩子：** `$impeccable hooks <on|off|status|ignore-rule|ignore-file|ignore-value|reset>` 管理此项目的设计探测器钩子（在 UI 文件编辑后自动运行探测器并报告发现）。当用户使用任何参数调用它时，加载 [reference/hooks.md](reference/hooks.md)。

**医生：** `$impeccable doctor` 报告和修复此项目与 Impeccable 艺术品（PRODUCT.md、DESIGN.md 及其侧车、配置、表面简报、钩子）之间在此版本中读取的差异。当用户调用它或询问什么是过时的、陈旧的或需要刷新的时，加载 [reference/doctor.md](reference/doctor.md)。Setup 的输出中的 `CONTEXT_STALE` 指令是相同报告的廉价子集；根据其自己的说明在那里采取行动，而不是未经请求运行医生。

**永远不要作为设计任务的副作用修复漂移。** `CONTEXT_STALE` 发现会被报告，而不是采取行动，除非用户请求。唯一的例外是标记为 `auto` 的发现，下一个写入该文件的操作会执行它。
