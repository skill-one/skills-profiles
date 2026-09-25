<概述>
## 剂原生架构

剂原生应用程序将代理视为一等公民。功能是代理通过工具在循环中实现的结果，而不是代码中编写的函数。相同的架构可以驱动 Claude Code，也可以驱动远超编码的应用程序。

**五个核心原则：**

1. **平等性** — 用户通过 UI 可以完成的一切，代理都可以通过工具实现。
2. **粒度** — 工具是原子原语；功能是提示定义的结果。要改变行为，请编辑文本，而不是代码。
3. **可组合性** — 新功能 = 新提示，而不是新代码。原子工具 + 平等性使这成为可能。
4. **涌现能力** — 代理可以完成你没有明确设计的事情。开放式请求揭示了潜在需求。
5. **持续改进** — 应用程序通过累积的上下文（例如 `context.md` 文件）和提示优化而变得更好，而无需发布代码。

要深入了解这些原则如何转化为架构模式，请阅读 `references/architecture-patterns.md`。
</概述>

<输入>
## 你需要帮助的剂原生架构的哪个方面？

1. **设计架构** - 从头开始规划一个新的剂原生系统
2. **文件和工作区** - 文件作为通用接口，共享工作区模式
3. **工具设计** - 原子工具，动态能力发现，CRUD 完整性
4. **领域工具** - 何时添加领域工具与保持原语
5. **执行模式** - 完成信号，部分完成，上下文限制
6. **系统提示** - 定义代理行为，判断标准
7. **上下文注入** - 将运行时应用程序状态注入代理提示
8. **动作平等性** - 确保代理可以完成用户可以完成的任何事情
9. **自我修改** - 使代理能够安全地自我进化
10. **产品设计** - 逐步披露，潜在需求，批准模式
11. **移动模式** - iOS 存储，后台执行，检查点/恢复
12. **测试** - 测试剂原生应用程序的能力和平等性
13. **重构** - 使现有代码更具剂原生
14. **审查 / 检查清单** - 架构检查清单，反模式，成功标准

选择一个数字或描述你想要什么。等待响应后再继续。
</输入>

<路由>
| 响应 | 阅读 |
|------|------|
| 1, "设计", "架构", "计划" | `references/architecture-patterns.md`，然后应用 `references/checklists.md` 中的检查清单 |
| 2, "文件", "工作区", "文件系统" | `references/files-universal-interface.md` 和 `references/shared-workspace-architecture.md` |
| 3, "工具", "mcp", "原语", "crud" | `references/mcp-tool-design.md` |
| 4, "领域工具", "何时添加" | `references/from-primitives-to-domain-tools.md` |
| 5, "执行", "完成", "循环" | `references/agent-execution-patterns.md` |
| 6, "提示", "系统提示", "行为" | `references/system-prompt-design.md` |
| 7, "上下文", "注入", "运行时", "动态" | `references/dynamic-context-injection.md` |
| 8, "平等性", "UI 动作", "能力映射" | `references/action-parity-discipline.md` |
| 9, "自我修改", "进化", "git" | `references/self-modification.md` |
| 10, "产品", "逐步", "批准", "潜在需求" | `references/product-implications.md` |
| 11, "移动", "iOS", "Android", "后台", "检查点" | `references/mobile-patterns.md` |
| 12, "测试", "测试", "验证", "验证" | `references/agent-native-testing.md` |
| 13, "重构", "现有", "迁移" | `references/refactoring-to-prompt-native.md` |
| 14, "审查", "审计", "反模式", "检查清单", "成功标准" | `references/checklists.md` |

阅读参考后，将这些模式应用于用户的特定上下文。
</路由>

<参考索引>
## 参考文件

**核心模式：**
- `references/architecture-patterns.md` — 事件驱动，统一协调器，代理到 UI；五个原则的全面覆盖
- `references/files-universal-interface.md` — 为什么文件，组织，context.md
- `references/mcp-tool-design.md` — 工具设计，动态能力发现，CRUD
- `references/from-primitives-to-domain-tools.md` — 何时将原语升级为领域工具
- `references/agent-execution-patterns.md` — 完成信号，部分完成，上下文限制
- `references/system-prompt-design.md` — 功能作为提示，判断标准

**学科：**
- `references/dynamic-context-injection.md` — 运行时上下文注入
- `references/action-parity-discipline.md` — 能力映射，平等性工作流
- `references/shared-workspace-architecture.md` — 共享数据空间，UI 集成
- `references/product-implications.md` — 逐步披露，潜在需求，批准
- `references/agent-native-testing.md` — 测试结果，平等性测试
- `references/checklists.md` — 架构检查清单，反模式，成功标准

**平台特定：**
- `references/mobile-patterns.md` — iOS 存储，检查点/恢复，成本意识
- `references/self-modification.md` — 基于 Git 的进化，护栏
- `references/refactoring-to-prompt-native.md` — 迁移现有代码
</参考索引>
