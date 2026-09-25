# 头脑风暴一个功能或改进

通过对话头脑风暴要构建的**内容**；`ce-plan`随后将相同的统一计划工件丰富为**方法**。这项技能不实现代码。**当前年份是2026年**，用于标注工件。

**成果**：根据`ce-plan`可以构建的工作量大小而定，不发明产品行为、范围边界或成功标准：对于轻量级工作，生成一个聊天段落；当文件被创建时，在`<root>/plans/`下生成一个仅包含需求统一计划。

**在头脑风暴路径上完成**：该工件被写入并通过“准备规划检查” — 或者没有文件被写入，因为对话没有产生一个需要记录在稳定ID下的决策（供后续读者，如规划者、审阅者或未来读者参考），且用户未要求记录 — 并且已展示第4阶段的交接。

**轻量级工作以聊天结束**。Phase 0.3根据请求分类层级，并在任何工作被派发前进行有界内联读取；当层级不确定时，选择更重量的层级。轻量级工作 — 小型、边界清晰、低歧义 — 以一个无文件的聊天段落结束，无基础侦察、无方法生成、无声明验证器。只有当需要记录在稳定ID下的决策，或用户要求时，才会生成文件。

**在三种情况下停止并路由**，由`references/phase-0.md`决定，而非记忆。每种情况都以自己的方式结束运行，因此上述完成条件不适用：非软件工作，`references/universal-brainstorming.md`取代Phase 0.2–4；关于命名外部候选人的裁决问题，你提供`ce-pov`交接；既非前者也非后者 — 快速帮助、事实性问题、单步任务 — 直接回答。

功能描述是调用携带的内容，无论是用户编写还是调用技能传递。如果没有提供，请询问用户他们想探索什么，并在获得一个之前不要继续。

**`mode:return-to-caller`**（由调用技能如`lfg`设置的引导标记）：移除它，不变更对话，并用`references/handoff.md`定义的结构化返回替换第4阶段：无菜单，无`lfg`或`ce-plan`调用。


## 工件根

第一次组合或读取`<root>/`路径时解析`<root>`，绝不提前；仅用于草稿或无仓库运行且不接触任何文件时，则完全跳过此步骤。

<!-- ce-docs-root:start -->
**在组合任何工件路径前解析CE工件根`<root>`。**

- **读取** `docs_root`仅从`<repo-root>/.compound-engineering/config.yaml`（`<repo-root>` = `git rev-parse --show-toplevel`）。不要从`config.local.yaml`读取。未设置 -> `<root>`是`docs`，与之前相同。
- **验证** 设置的值：一个仓库相对目录，其真实路径（解析符号链接后）始终在仓库内，且既不是仓库根也不是`.git/`下。否则报错，并命名`docs_root`和值 — 绝不回退到`docs`。
- **使用** `<root>`作为唯一工件位置：如果不存在则创建它，以该技能自己的子目录组合每个路径为`<root>/<subdir>`，且永不同时读取`docs`。
<!-- ce-docs-root:end -->

`brainstorm_output`和`brainstorm_model`按此规则解析：

<!-- ce-config-layers:start -->
**从两个仓库文件解析普通CE yaml键。**

- **读取** `<repo-root>/.compound-engineering/config.local.yaml`，然后`config.yaml`（`<repo-root>` = `git rev-parse --show-toplevel`）。跳过缺失文件。Gitignore不改变解析。
- **优先** 第一个激活（非注释）的值。对于标量，空值是未设置；无效值继续到下一层，然后是技能默认值。对于列表和映射，存在的键 — 包括空列表或映射 — 会替换整个键。
- **不要**用于`docs_root` — 该键仅存在于`config.yaml`。
<!-- ce-config-layers:end -->

## 执行流程

阶段按此顺序运行。每个阶段命名它正确运行所需的文件：在到达时读取它们，且永不仅从此表单独执行工作。

| 阶段 | 首先读取 | 仅这些文件携带的内容 |
|---|---|---|
| 第一个问题之前，以及整个运行期间 — 包括非软件路由 | 读取`references/interaction-rules.md` | 核心原则和交互规则：每轮一个问题，仅询问环境无法裁决的决策，阻塞问题工具默认值和覆盖它的视觉探测门，当问题真正开放时，以及该技能在`references/phase-0.md`中完整陈述的`ce-prototype`路由测试 |
| 在将对话携带的决策视为已解决之前 | 读取`references/settled-decisions.md` | 解决测试；跳过它将重新询问已决定的问题或提升未审查的断言 |
| 0.0输出模式 | `references/output-mode.md` | `OUTPUT_FORMAT`优先级；标记解析约定 |
| 0.1–0.4恢复、分类、路由、范围 | `references/phase-0.md` | 恢复扫描；停止并路由分类；范围层级；连贯工作门（这是单一工作吗？）；两个触发器（视觉或空间特征；不熟悉领域）；任务列表 |
| 1理解想法 | `references/dialogue.md` | 上下文扫描和基础侦察；选择加入Slack研究员；压力测试；盲点和视觉探测门；与现有`CONCEPTS.md`和验证代码的冲突门；Phase 1.3退出条件 |
| 2–2.6方法、综合、验证 | `references/approaches.md`，组合综合前加上`references/synthesis-summary.md` | 方法生成；模型提升；范围综合；声明验证器 |
| 3编写计划 | `references/plan-write.md`，然后`references/brainstorm-sections.md`和格式渲染参考 | 值得编写文档吗；章节契约；准备规划检查 |
| 4交接 | `references/handoff.md` | 选项集及其可见性条件；渲染模式规则；按选择分发，包括传递给`ce-plan`的内容；总结性陈述 |

这些规则无需读取：

**`OUTPUT_FORMAT`是排他的** — markdown OR HTML，绝不两者兼有。格式是第一个适用的：此提示中的请求、用户先前声明的偏好、配置，然后是markdown，在包括无头运行在内的所有运行中。

**当在头脑风暴路径上写入文件时，工件契约不会改变**：写入`<root>/plans/YYYY-MM-DD-HHMM-<type>-<topic>-plan.<md|html>`，其中`HHMM`来自写入时的本地墙上时间；frontmatter携带`artifact_contract: ce-unified-plan/v1`和`product_contract_source: ce-brainstorm`；正文是目标胶囊加上产品契约。**不要**发出目标启动块或读者索引。非软件路由不写入任何内容。

**当写入文件时，不要声明其已写入或进入第4阶段，而任何检查在准备规划检查中失败**；聊天结果直接进入第4阶段（交接），无需运行检查。即兴交接菜单是另一种无声失败：它显示应隐藏的选项，并将错误输入传递给下一个技能。
