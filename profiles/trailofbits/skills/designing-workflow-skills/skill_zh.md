# 设计工作流技能

通过遵循结构化模式而非散文来构建可靠的工作流技能。

## 基本原则

<essential_principles>

<principle name="description-is-the-trigger">
**`description` 字段是唯一控制技能何时激活的东西。**

Claude 会根据技能的前置 `description` 判断是否加载技能。SKILL.md 的正文——包括 "何时使用" 和 "何时不用" 部分——只有在技能已经激活后才会被读取。将触发关键词、用例和排除项放在描述中。描述不佳会导致错误的激活或遗漏激活，无论正文如何说明。

"何时使用" 和 "何时不用" 部分仍然有其作用：它们在技能激活后限定 LLM 的行为。"何时不用" 应该指定具体的替代方案："使用 Semgrep 进行简单模式匹配"，而不是 "不适用于简单任务"。
</principle>

<principle name="numbered-phases">
**阶段必须编号，并包含入口和退出标准。**

无编号的散文式指令会导致不可靠的执行顺序。每个阶段都需要：
- 编号（阶段 1、阶段 2、...）
- 入口标准（开始前必须满足的条件）
- 编号化的操作（要做什么）
- 退出标准（如何知道已完成）
</principle>

<principle name="tools-match-executor">
**工具必须与执行者匹配。**

技能在前置中使用 `allowed-tools:`。代理在前置中使用 `tools:`。子代理从其 `subagent_type` 获取工具。绝不要列出组件未使用的工具。绝不要使用 Bash 执行有专用工具的操作（Glob、Grep、Read、Write、Edit）。

大多数技能和代理应在其工具列表中包含 `TodoRead` 和 `TodoWrite`——这些在多步骤执行期间启用进度跟踪，即使对于不显式管理任务的技能也很有用。
</principle>

<principle name="progressive-disclosure">
**渐进式披露是结构化的，而非可选的。**

SKILL.md 保持在 500 行以内。它只包含 LLM 每次调用所需的元素：原则、路由、快速参考和链接。详细模式放在 `references/` 中。分步流程放在 `workflows/` 中。一级深度——无引用链。
</principle>

<principle name="scalable-tool-patterns">
**指令必须产生可扩展的工具调用模式。**

每个工作流指令在运行时都会变成工具调用。如果一个工作流搜索 N 个文件中的 M 个模式，应将它们组合成一个正则表达式——而不是 N×M 次调用。如果一个工作流按项目生成子代理，使用批处理——而不是每个文件一个子代理。应用 10,000 个文件测试：在大型代码库中想象运行工作流，并检查工具调用数量是否保持有界。参见 [anti-patterns.md](references/anti-patterns.md) AP-18 和 AP-19。
</principle>

<principle name="degrees-of-freedom">
**将指令的特定性与任务的易碎性相匹配。**

并非每个步骤都需要相同级别的规定。按步骤校准：
- **低自由度**（精确命令，无变化）：易碎操作——数据库迁移、加密、破坏性操作。"运行这个脚本"。
- **中等自由度**（带参数的伪代码）：首选模式，允许变化。"使用这个模板并根据需要自定义"。
- **高自由度**（启发式和判断）：可变任务——代码审查、探索、文档。"分析结构并建议改进"。

一个技能可以混合自由度级别。一个安全审计技能可能在发现阶段使用高自由度（"探索代码库中的认证模式"），在报告阶段使用低自由度（"使用这个严重性分类表"）。
</principle>

</essential_principles>

## 何时使用

- 设计具有多步骤工作流或分阶段执行的新技能
- 创建在多个独立任务之间路由的技能
- 构建具有安全门（需要确认的破坏性操作）的技能
- 结构化使用子代理或任务跟踪的技能
- 审查或重构现有工作流技能以提高质量
- 决定如何将内容拆分到 SKILL.md、references/ 和 workflows/

## 何时不用

- 简单的单用途技能，无工作流（仅指导）——直接编写 SKILL.md
- 编写技能的实际领域内容（这教的是结构，不是领域专业知识）
- 插件配置（plugin.json、hooks、commands）——使用插件开发指南
- 非技能 Claude 代码开发——这专门用于技能架构

## 模式选择

为技能的结构选择正确的模式。在 [workflow-patterns.md](references/workflow-patterns.md) 中阅读完整模式描述。

```
技能有多少个独立路径？
|
+-- 一个路径，始终相同
|   +-- 它执行破坏性操作吗？
|       +-- 是 -> 安全门模式
|       +-- 否 -> 线性执行模式
|
+-- 从共享设置出发的多个独立路径
|   +-- 路由模式
|
+-- 顺序执行的多个依赖步骤
    +-- 步骤是否有复杂依赖？
        +-- 是 -> 任务驱动模式
        +-- 否 -> 顺序管道模式
```

### 模式总结

| 模式 | 何时使用 | 关键特征 |
|---------|----------|-------------|
| **路由** | 多个独立任务从共享输入 | 路由表将意图映射到工作流文件 |
| **顺序管道** | 依赖步骤，每个步骤为下一个步骤提供输入 | 自动检测可能从部分进度恢复 |
| **线性执行** | 单一路径，每次都相同 | 带入口/退出标准的编号阶段 |
| **安全门** | 破坏性/不可逆操作 | 执行前有两个确认门 |
| **任务驱动** | 复杂依赖，部分失败容忍 | TaskCreate/TaskUpdate 带依赖跟踪 |

## 结构化解剖

每个工作流技能都需要这个骨架，无论模式如何：

```markdown
---
name: kebab-case-name
description: "第三人称描述，包含触发关键词——这是 Claude 决定激活技能的方式"
allowed-tools: Tool1 Tool2 Tool3  # 空格分隔的工具名称列表
# 可选字段——参见 tool-assignment-guide.md 获取完整参考：
# disable-model-invocation: true    # 只有用户可以调用（不是 Claude）
# user-invocable: false             # 只有 Claude 可以调用（隐藏在 / 菜单中）
# context: fork                     # 在隔离的子代理上下文中运行
# agent: Explore                    # 子代理类型（需要 context: fork）
# model: [model-name]               # 技能激活时切换模型
# argument-hint: "[filename]"       # 自动完成期间显示的提示
---

# 标题

## 基本原则
[3-5 不可协商的规则，附带解释]

## 何时使用
[4-6 具体场景——激活后限定行为]

## 何时不用
[3-5 带有命名替代方案的场景——激活后限定行为]

## [模式特定部分]
[路由表 / 管道步骤 / 阶段列表 / 门]

## 快速参考
[频繁需要的信息的紧凑表格]

## 参考索引
[所有支持文件的链接]

## 成功标准
[输出验证的清单]
```

技能支持三种类型的字符串替换：美元符号前缀变量用于参数和会话 ID，以及感叹号反引号语法用于 shell 预处理。技能加载器在 Claude 看到文件之前处理这些内容——即使在代码围栏内也是如此，因此永远不要在文档文本中使用原始语法。参见 [tool-assignment-guide.md](references/tool-assignment-guide.md) 获取完整变量参考和使用指南。

## 反模式快速参考

最常见的错误。完整目录和修复前后的示例在 [anti-patterns.md](references/anti-patterns.md) 中。

| AP | 反模式 | 一行修复 |
|----|-------------|-------------|
| AP-1 | 缺少目标/反目标 | 添加 "何时使用" 和 "何时不用" 部分 |
| AP-2 | 单体 SKILL.md (>500 行) | 拆分为 references/ 和 workflows/ |
| AP-3 | 引用链 (A -> B -> C) | 所有文件与 SKILL.md 只有一级距离 |
| AP-4 | 硬编码路径 | 使用 `{baseDir}` 进行所有内部路径 |
| AP-5 | 破坏的文件引用 | 提交前验证每个路径是否有效 |
| AP-6 | 无编号阶段 | 为每个阶段编号并带入口/退出标准 |
| AP-7 | 缺少退出标准 | 定义每个阶段"完成"的含义 |
| AP-8 | 无验证步骤 | 在每个工作流的末尾添加验证 |
| AP-9 | 模糊路由关键词 | 为每个工作流路由使用独特的关键词 |
| AP-11 | 错误的工具 | 使用 Glob/Grep/Read，而不是 Bash 等价物 |
| AP-12 | 过权工具 | 移除未实际使用的工具 |
| AP-13 | 模糊子代理提示 | 指定要分析、查找和返回的内容 |
| AP-15 | 引用转储 | 教授判断，而不是原始文档 |
| AP-16 | 缺少理由 | 为审计技能添加 "拒绝理由" |
| AP-17 | 无具体示例 | 为关键指令显示输入 -> 输出 |
| AP-18 | 笛卡尔积工具调用 | 将模式组合成一个正则表达式，一次 grep，然后过滤 |
| AP-19 | 无界子代理生成 | 将项目批处理成组，每个子代理处理一批 |
| AP-20 | 描述总结工作流 | 描述 = 触发条件，绝不包含工作流步骤 |

*AP-10（无默认/回退路由）、AP-14（代理中缺少工具理由）、和 AP-20（描述总结工作流）在 [完整目录](references/anti-patterns.md) 中。AP-20 因其高影响而包含在快速参考中。*

## 工具分配快速参考

将组件类型映射到正确的工具集。完整指南在 [tool-assignment-guide.md](references/tool-assignment-guide.md) 中。

| 组件类型 | 典型工具 |
|---------------|---------------|
| 只读分析技能 | Read, Glob, Grep, TodoRead, TodoWrite |
| 交互式分析技能 | Read, Glob, Grep, AskUserQuestion, TodoRead, TodoWrite |
| 代码生成技能 | Read, Glob, Grep, Write, Bash, TodoRead, TodoWrite |
| 管道技能 | Read, Write, Glob, Grep, Bash, AskUserQuestion, Task, TaskCreate, TaskList, TaskUpdate, TodoRead, TodoWrite |
| 只读代理 | Read, Grep, Glob, TodoRead, TodoWrite |
| 操作代理 | Read, Grep, Glob, Write, Bash, TodoRead, TodoWrite |

**关键规则：**
- 使用 Glob（不是 `find`）、Grep（不是 `grep`）、Read（不是 `cat`）——始终优先使用专用工具
- 技能使用 `allowed-tools:` — 代理使用 `tools:`
- 只列出指令实际引用的工具
- 只读组件绝不能有 Write 或 Bash

## 拒绝理由

设计工作流技能时，拒绝这些捷径：

| 拒绝理由 | 为什么错误 |
|-----------------|----------------|
| "下一个阶段很明显" | LLM 无法从散文中推断顺序。编号阶段。 |
| "退出标准是隐含的" | 隐含标准是跳过的标准。明确写出它们。 |
| "一个大的 SKILL.md 更简单" | 写起来简单，执行起来更差。LLM 在 500 行后失去焦点。 |
| "描述并不重要" | 描述是技能如何被触发的。描述不佳会导致错误的激活或遗漏激活。 |
| "Bash 可以做所有事情" | Bash 文件操作是脆弱的。专用工具更好地处理编码、权限和格式。 |
| "LLM 会猜出工具" | 它会猜错。为每个操作指定确切的工具。 |
| "我稍后会添加细节" | 不完整的技能会以不完整的方式交付。设计完成后才能编写。 |

## 参考索引

| 文件 | 内容 |
|------|---------|
| [workflow-patterns.md](references/workflow-patterns.md) | 5 个模式，带结构骨架和示例 |
| [anti-patterns.md](references/anti-patterns.md) | 20 个反模式，带修复前后的示例 |
| [tool-assignment-guide.md](references/tool-assignment-guide.md) | 工具选择矩阵，组件比较，子代理指南 |
| [progressive-disclosure-guide.md](references/progressive-disclosure-guide.md) | 内容拆分规则，500 行规则，尺寸指南 |

| 工作流 | 目的 |
|----------|---------|
| [design-a-workflow-skill.md](workflows/design-a-workflow-skill.md) | 从范围到自我审查的 6 阶段创建过程 |
| [review-checklist.md](workflows/review-checklist.md) | 结构化自我审查清单，用于提交准备 |

## 成功标准

一个设计良好的工作流技能：

- [ ] 具有 "何时使用" 和 "何时不用" 部分
- [ ] 使用可识别的模式（路由、管道、线性、安全门或任务驱动）
- [ ] 编号所有阶段，并带入口和退出标准
- [ ] 只列出它实际使用的工具（最小权限）
- [ ] 将 SKILL.md 保持在 500 行以内，详细信息在 references/workflows 中
- [ ] 无硬编码路径（使用 `{baseDir}`)
- [ ] 无损坏的文件引用
- [ ] 无引用链（所有链接与 SKILL.md 只有一级距离）
- [ ] 在工作流末尾包含验证步骤
- [ ] 描述正确触发（第三人称，特定关键词）
- [ ] 为关键指令提供具体示例
- [ ] 解释 "为什么"，而不仅仅是 "什么"，对于基本原则
