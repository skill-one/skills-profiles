# Gepetto

协调一个多步骤的规划流程：研究 → 面试 → 需求综合 → 规划 → 外部评审 → 章节

## 关键：首要操作

**在开始任何其他操作之前**，请按顺序执行以下操作：

### 1. 打印介绍

立即打印介绍横幅：
```
═══════════════════════════════════════════════════════════════
GEPETTO：AI辅助实施规划
═══════════════════════════════════════════════════════════════
研究 → 面试 → 需求综合 → 规划 → 外部评审 → 章节

注意：GEPETTO将向其传递的规划目录写入许多.md文件
```

### 2. 验证规范文件输入

**检查用户在调用时是否提供了@file，并且它是一个规范文件（以“.md”结尾）。**

如果未提供@file，或者路径不以“.md”结尾，则输出以下内容并停止：
```
═══════════════════════════════════════════════════════════════
GEPETTO：需要规范文件
═══════════════════════════════════════════════════

此技能需要一个以.md结尾的Markdown规范文件路径。
规划目录是从规范文件的父目录推断出来的。

要开始一个新的规划：
  1. 创建一个描述您想要构建内容的Markdown规范文件
  2. 它可以详细或模糊
  3. 将其放在gepetto可以保存规划文件的位置
  4. 运行：/gepetto @path/to/your-spec.md

要恢复现有的规划：
  1. 运行：/gepetto @path/to/your-spec.md

示例：/gepetto @planning/my-feature-spec.md
═══════════════════════════════════════════════════════════════
```
**不要继续。等待用户重新调用.md文件路径。**

### 3. 设置规划会话

通过检查现有文件来确定会话状态：

1. 设置`planning_dir` = 规范文件的父目录
2. 设置`initial_file` = 规范文件路径
3. 扫描现有的规划文件：
   - `claude-research.md`
   - `claude-interview.md`
   - `claude-spec.md`
   - `claude-plan.md`
   - `claude-integration-notes.md`
   - `claude-ralph-loop-prompt.md`
   - `claude-ralphy-prd.md`
   - `reviews/`目录
   - `sections/`目录

4. 确定模式和恢复点：

| 找到的文件 | 模式 | 从哪里恢复 |
|-------------|------|-------------|
| 无 | 新建 | 步骤 4 |
| 仅研究 | 恢复 | 步骤 6（面试） |
| 研究 + 面试 | 恢复 | 步骤 8（需求综合） |
| + 规范 | 恢复 | 步骤 9（规划） |
| + 规划 | 恢复 | 步骤 10（外部评审） |
| + 评审 | 恢复 | 步骤 11（集成） |
| + 集成笔记 | 恢复 | 步骤 12（用户评审） |
| + sections/index.md | 恢复 | 步骤 14（编写章节） |
| 所有章节已完成 | 恢复 | 步骤 15（执行文件） |
| + claude-ralph-loop-prompt.md + claude-ralphy-prd.md | 完成 | 完成 |

5. 使用TodoWrite根据当前状态创建TODO列表

打印状态：
```
规划目录：{planning_dir}
模式：{mode}
```

如果恢复：
```
从步骤 {N} 恢复
要重新开始，请删除规划目录文件。
```

---

## 日志格式

```
═══════════════════════════════════════════════════════════════
STEP {N}/17: {STEP_NAME}
═══════════════════════════════════════════════════════════════
{details}
步骤 {N} 完成：{summary}
───────────────────────────────────────────────────────────────
```

---

## 工作流

### 4. 研究决策

参见[research-protocol.md](references/research-protocol.md)。

1. 读取规范文件
2. 提取潜在的研究主题（技术、模式、集成）
3. 询问用户关于代码库研究需求
4. 询问用户关于网络研究需求（以多选形式呈现派生主题）
5. 记录在步骤 5 中要执行的研究类型

### 5. 执行研究

参见[research-protocol.md](references/research-protocol.md)。

根据步骤 4 的决策，启动研究子代理：
- **代码库研究：** `Task(subagent_type=Explore)`
- **网络研究：** `Task(subagent_type=Explore)`与WebSearch

如果两者都需要，则并行启动Task工具（单条消息包含多个工具调用）。

**重要：** 子代理返回其发现——它们不会直接写入文件。收集所有子代理的结果后，将它们合并并写入`<planning_dir>/claude-research.md`。

如果用户在步骤 4 中选择不进行任何研究，则完全跳过此步骤。

### 6. 详细面试

参见[interview-protocol.md](references/interview-protocol.md)

在主上下文中运行（AskUserQuestion需要它）。面试应受以下内容启发：
- 初始规范
- 研究结果（如果有）

### 7. 保存面试记录

将问答写入`<planning_dir>/claude-interview.md`

### 8. 编写初始规范（需求综合）

将以下内容组合到`<planning_dir>/claude-spec.md`：
- **初始输入**（规范文件）
- **研究结果**（如果步骤 5 已完成）
- **面试答案**（来自步骤 6）

这将对用户的原始需求进行综合，形成完整的规范。

### 9. 生成实施计划

创建详细计划 → `<planning_dir>/claude-plan.md`

**重要**：为不熟悉的读者编写。计划必须完全自包含——工程师或LLM在没有先前上下文的情况下应能通过阅读此文档理解我们正在构建什么、为什么以及如何构建。

### 10. 外部评审

参见[external-review.md](references/external-review.md)

并行启动两个子代理来评审计划：
1. **Gemini**通过Bash
2. **Codex**通过Bash

两者都接收计划内容并返回其分析。将结果写入`<planning_dir>/reviews/`。

### 11. 集成外部反馈

分析`<planning_dir>/reviews/`中的建议。

您是决定要集成什么或不集成的权威。如果您决定不集成任何内容，也可以。

**步骤 1：** 写入`<planning_dir>/claude-integration-notes.md`记录：
- 您要集成的建议及其原因
- 您不集成的建议及其原因

**步骤 2：** 使用集成更改更新`<planning_dir>/claude-plan.md`。

### 12. 用户评审集成计划

使用AskUserQuestion：
```
计划已更新外部反馈。您现在可以评审和编辑claude-plan.md。

如果您需要Claude帮助编辑计划，请打开一个单独的Claude会话——此会话处于工作流中，直到工作流完成才能协助编辑。

完成评审后，选择“完成”继续。
```

选项："完成评审"

在继续之前等待用户确认。

### 13. 创建章节索引

参见[section-index.md](references/section-index.md)

读取`claude-plan.md`。识别自然章节边界并创建`<planning_dir>/sections/index.md`。

**关键**：index.md必须以SECTION_MANIFEST块开头。参见参考以了解格式要求。

在继续到章节文件创建之前，写入index.md。

### 14. 并行子代理编写章节文件

参见[section-splitting.md](references/section-splitting.md)

**并行启动子代理**——每个章节一个Task以实现最大效率：

1. 首先，解析`sections/index.md`以获取SECTION_MANIFEST列表
2. 然后，在单条消息中启动所有章节Task（并行执行）：

```
# 在一条消息中并行启动：

Task(
  subagent_type="general-purpose",
  prompt="""
  编写章节文件：section-01-{name}

  输入：
  - <planning_dir>/claude-plan.md
  - <planning_dir>/sections/index.md

  输出：<planning_dir>/sections/section-01-{name}.md

  章节文件必须完全自包含。包括：
  - 背景（此章节存在的原因）
  - 需求（完成时必须满足的条件）
  - 依赖关系（要求/阻塞）
  - 实施细节（来自计划）
  - 接受标准（复选框）
  - 要创建/修改的文件

  实施者不应需要参考任何其他文档。
  """
)

Task(
  subagent_type="general-purpose",
  prompt="编写章节文件：section-02-{name} ..."
)

Task(
  subagent_type="general-purpose",
  prompt="编写章节文件：section-03-{name} ..."
)

# ... manifest中的每个章节一个Task
```

在继续之前等待所有子代理完成。

### 15. 生成执行文件——子代理

**委托给子代理**以减少主上下文令牌使用：

```
Task(
  subagent_type="general-purpose",
  prompt="""
  为自主实施生成两个执行文件。

  输入文件：
  - <planning_dir>/sections/index.md（包含SECTION_MANIFEST）
  - <planning_dir>/sections/section-*.md（所有章节文件）

  输出 1：<planning_dir>/claude-ralph-loop-prompt.md
  用于ralph-loop插件。内嵌所有章节内容。

  结构：
  - 任务声明
  - sections/index.md的完整内容
  - 每个章节文件的完整内容（内嵌，不引用）
  - 执行规则（依赖顺序，验证接受标准）
  - 完成信号：<promise>ALL-SECTIONS-COMPLETE</promise>

  输出 2：<planning_dir>/claude-ralphy-prd.md
  用于Ralphy CLI。引用章节文件（不内嵌）。

  结构：
  - PRD头部
  - 如何使用（ralphy --prd命令）
  - 上下文说明
  - 复选框任务列表：每个章节一个"- [ ] Section NN: {name}"

  写入两个文件。
  """
)
```

在继续之前等待子代理完成。

### 16. 最终状态

验证所有文件是否成功创建：
- 来自SECTION_MANIFEST的所有章节文件
- `claude-ralph-loop-prompt.md`
- `claude-ralphy-prd.md`

### 17. 输出摘要

打印生成的文件和下一步操作：
```
═══════════════════════════════════════════════════════════════
GEPETTO：规划完成
═══════════════════════════════════════════════════════════════

生成的文件：
  - claude-research.md（研究结果）
  - claude-interview.md（问答记录）
  - claude-spec.md（综合规范）
  - claude-plan.md（实施计划）
  - claude-integration-notes.md（反馈决策）
  - reviews/（外部LLM反馈）
  - sections/（实施单元）
  - claude-ralph-loop-prompt.md（用于ralph-loop插件）
  - claude-ralphy-prd.md（用于Ralphy CLI）

如何实施：

选项 A - 手动（推荐用于学习/控制）：
  1. 读取sections/index.md以了解依赖关系
  2. 按顺序实现每个章节文件
  3. 每个章节文件都是自包含的，包含接受标准

选项 B - 使用ralph-loop的自主实施（Claude代码插件）：
  /ralph-loop @<planning_dir>/claude-ralph-loop-prompt.md --completion-promise "COMPLETE" --max-iterations 100

选项 C - 使用Ralphy的自主实施（外部CLI）：
  ralphy --prd <planning_dir>/claude-ralphy-prd.md
  # 或：cp <planning_dir>/claude-ralphy-prd.md ./PRD.md && ralphy
═══════════════════════════════════════════════════════════════
```
