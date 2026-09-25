# Agents Window 开发

在 `src/vs/sessions/**` 下使用此技能进行实现、审查或设计工作。

## 1. 应用核心原则

- 保持层级方向：`vs/sessions` 可能导入 `vs/workbench` 及更低层级的模块；`vs/workbench` 必须永不导入 `vs/sessions`。
- 保持共享 Sessions 代码与提供者无关。非提供者贡献必须不导入提供者实现。
- 使用可观察对象对可变会话和聊天状态进行建模。使用事件进行通知，不要将其用作并行状态模型或控制流。
- 在 `browser/menus.ts` 中注册 Sessions 菜单 ID，并使用 `Menus.*` 进行消费。
- 从适当的 `sessions.*.main.ts` 入口点导入贡献。
- 除非能力确实是共享的，否则优先使用 Sessions 自有的适配，而不是共享工作台的更改。
- 将稳定架构放在所属规范中，将具体行为放在测试中。不要保留实现时间顺序作为开发指导。

## 2. 确定所属区域

从 `src/vs/sessions/README.md` 开始，然后仅阅读与变更相关的规范：

| 区域 | 规范 |
|------|---------------|
| 层级、文件夹所有权、跨模块导入 | `src/vs/sessions/LAYERS.md` |
| 会话/聊天模型、服务、提供者契约、核心数据流 | `src/vs/sessions/SESSIONS.md` |
| 自动化所有权、路由、迁移、持久化、运行生命周期 | `src/vs/sessions/AUTOMATIONS.md` |
| 工作台组件、网格、标题栏、编辑器呈现 | `src/vs/sessions/LAYOUT.md` |
| 会话感知布局状态和恢复 | `src/vs/sessions/LAYOUT_CONTROLLER.md` |
| 单面板行为和预期组合 | `src/vs/sessions/SINGLE_PANE_SCENARIOS.md` |
| Sessions 侧边栏列表、分组、过滤和持久化 | `src/vs/sessions/SESSIONS_LIST.md` |
| 电话布局和移动组件 | `src/vs/sessions/MOBILE.md` |
| AI 自定义 | `src/vs/sessions/AI_CUSTOMIZATIONS.md` |
| Copilot 自定义 | `src/vs/sessions/copilot-customizations-spec.md` |
| Copilot Chat 提供者 | `src/vs/sessions/contrib/providers/copilotChatSessions/COPILOT_CHAT_SESSIONS_PROVIDER.md` |
| Agent Host 提供者 | `src/vs/sessions/contrib/providers/agentHost/AGENT_HOST_SESSIONS_PROVIDER.md` |
| 远程 Agent Host 提供者 | `src/vs/sessions/contrib/providers/remoteAgentHost/REMOTE_AGENT_HOST_SESSIONS_PROVIDER.md` |

默认情况下不要加载学习收件箱。搜索其标题和范围，然后仅在匹配的规范后阅读匹配的条目。

## 3. 修改前检查

- 追踪当前实现及其现有测试。
- 在添加新内容之前，搜索共享助手、上下文键、菜单 ID、入口点导入和提供者抽象。
- 确认哪个层级拥有该行为。将提供者特定决策保留在提供者中，将视图/布局决策保留在 Sessions 自有的浏览器代码中。
- 对于 UI 工作，还请调用适用的可访问性、设计、CSS、布局或主题技能。
- 对于 agent、LLM、策略、权限、遥测或管理设置的更改，在实现前请调用适用的专家技能。

## 4. 实现契约

应用核心原则和专注的规范。优先进行保留这些边界的小更改：

- `ISessionsManagementService` 拥有模型编排和提供者路由。
- `ISessionsService` 拥有可见和活动会话行为。
- 提供者通过 `ISession` 和 `IChat` 提供提供者无关的状态。
- 会话状态是可观察的；消费者以响应式方式派生 UI 状态。
- 贡献通过适当的 `sessions.*.main.ts` 入口点加载。
- Sessions 菜单使用共享的 `Menus` 注册表。
- 共享工作台的更改代表共享能力，而不是 Sessions 特定的策略。

### 规范编辑门禁

当错误修复恢复现有契约时，不要更新规范。在编辑权威规范之前，识别所有三个：

1. 有意更改的现有所有权、接口、生命周期、状态机、持久化或跨组件契约；
2. 受该契约更改影响的实现表面；
3. 为什么回归测试和简短代码注释不能完全表示它。

如果任何答案缺失，请保持规范不变。将具体行为放在专注的测试中，在所属代码旁边保留非明显的实现约束，并在问题或拉取请求中保留调查历史记录。

仅当组件所有权、接口或生命周期契约、状态机、持久化或跨组件不变性发生变化时才更新规范。不要为样式、文本、操作位置、遥测字段、设置默认值、实现算法或单个错误修复更新规范。这些细节属于代码和专注的测试。

## 5. 按比例验证

运行覆盖变更的最小现有检查：

- 受影响行为的专注单元测试；
- 当导入或模块所有权发生变化时运行 `npm run valid-layers-check`；
- 当 TypeScript 变更需要时进行有针对性的类型检查或编译；
- 对于跨进程或 UI 工作，运行相关的集成、E2E 或视觉验证。

仅文档更改需要链接、路径和一致性检查，而不是完整构建。

## 6. 正确记录反馈

当用户明确纠正或拒绝方法时，除非他们使用字面量 `learn!` 触发器，否则请调用 `feedback-learning` 技能。字面量 `learn!` 请求遵循 `.github/instructions/learnings.instructions.md`。持久架构不变性属于所属规范，具体行为属于回归测试，未经证实的可重用指导暂时属于作用域学习收件箱。永远不要将每个纠正追加到此技能。

## 7. 维护此技能

仅在原则稳定、跨领域且对大多数 Agents Window 工作有用，或当路由/工作流本身发生变化时更新此技能。将子系统契约放在其专注的规范中，将错误行为放在测试中。

保持核心原则部分不超过十个要点。在添加一个之前，合并重叠、删除过时指导，并优先重写现有原则。永远不要追加特定事件的详细信息或以此技能作为学习日志。
