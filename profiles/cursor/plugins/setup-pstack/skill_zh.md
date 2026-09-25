# 设置 pstack

编写 `~/.cursor/rules/pstack-models.mdc`，这是一个始终生效的规则，用于根据角色设置 pstack 的模型。

## 步骤

### 1. 检测可用模型

枚举在本会话中可以传递给 `Task` 子代理的模型 slugs。这是可靠的信息来源。如果 Cursor 还公开一个模型 API 或 CLI，列出用户有权访问的模型，则优先使用它以保持完整性。如果你无法检测到任何模型，请要求用户粘贴他们有权访问的 slugs。切勿写入你未确认可用的真实 slug。别名 `inherit-parent` 和 `auto` 总是有效的，即使它们不是检测到的 slugs。

### 2. 加载当前状态

默认的角色到模型映射是步骤 5 中显示的规则形状。如果 `~/.cursor/rules/pstack-models.mdc` 已经存在，则读取它并将其 `# budget` 行及其角色值视为当前选择。否则从默认值开始。像 `how critics` 这样的行中的角色不在步骤 5 中，是来自已退役的角色。将其丢弃。

### 3. 预算、映射和确认

**(a) 请求预算。** 优先使用 AskQuestion 而不是自由文本。提供以下四个选项，并使用这些确切的标签，并在规则记录一个当前预算时命名它。

- `unlimited — keep max`
- `large — xhigh reasoning`
- `medium — high reasoning`
- `small — medium reasoning`

**(b) 应用它。** 从技能默认值构建工作表，并在重新运行时保留你通过家族、列表或别名 (`inherit-parent`, `auto`) 改变的任何角色。`unlimited` 将每个努力保留在该表中。`large`、`medium` 和 `small` 将每个真实 slug（包括面板条目）的努力标记设置为 `xhigh`、`high` 或 `medium`。努力标记是梯子 `max` > `xhigh` > `high` > `medium` > `low` 中的最后一个标记，或在尾随 `fast` 之前的标记。如果结果不是检测到的 slug，则使用具有最高目标以下努力的相同家族的检测到的 slug，否则将角色标记为需要选择。`inherit-parent` 和 `auto` 不改变。因此 `small` 将 `claude-opus-5-5-max` 转换为 `claude-opus-5-5-medium`，将 `grok-4.7-xhigh-fast` 转换为 `grok-4.7-medium-fast`。

**(c) 显示角色并确认。** 显示每个角色及其模型，将任何不在检测集中的真实 slug 标记为需要选择。还列出步骤 2 丢弃的每一行。询问是否接受当前设置或更改特定角色，提供检测到的模型加上 `inherit-parent` 和 `auto`（两者都表示：此角色在父聊天模型上运行，这是 Auto 用户保持在使用 Auto 的方式）作为选项。优先使用 AskQuestion 而不是自由文本。对于面板角色（arena runners、architect runners、interrogate reviewers），值是一个列表，每个条目运行一个子代理，包括别名条目，所以列表长度设置计数。`arena cross-judge pool` 也是一个列表，但 Arena 在可能的情况下从其中选择一个值，其模型家族与父模型不同。`swarm workers` 是每个工作者的默认模型，除非比赛或比较为每个臂分配了另一个模型。

### 4. 验证

写入的每个真实 slug 必须在检测集中。`inherit-parent` 和 `auto` 总是通过。如果选择的真实 slug 不可用，则停止并再次询问。

### 5. 写入规则

使用 `alwaysApply: true`、一个带有所选标签及其目标努力的 `# budget` 行，以及每个角色一行（使用 poteto-mode 使用的相同标签），编写 `~/.cursor/rules/pstack-models.mdc`。覆盖整个文件，以便重新运行保持幂等性。形状：

```
---
description: pstack 每个角色的模型选择（覆盖技能默认值）
alwaysApply: true
---
# pstack 模型配置。每行一个角色。删除一行以回退到技能默认值。
# `inherit-parent` 或 `auto` 作为值：该角色在父聊天模型上运行（省略 Task `model`）。面板列表中的别名条目仍然计入其 fan-out。
# budget: unlimited (max)
feature, refactoring: grok-4.7-xhigh-fast
bug-fix: grok-4.7-xhigh-fast
perf-issue: grok-4.7-xhigh-fast
hillclimb: grok-4.7-xhigh-fast
judgment and prose: claude-opus-5-5-max
hardest tasks: claude-opus-5-5-max
how explorer: grok-4.7-xhigh-fast
how explainer: claude-opus-5-5-max
why investigators: grok-4.7-xhigh-fast
why synthesizer: claude-opus-5-5-max
reflect tooling: gpt-5.6-sol-max
reflect judgment, divergent, synthesizer: claude-opus-5-5-max
arena runners: claude-opus-5-5-max, gpt-5.6-sol-max, grok-4.7-xhigh-fast
arena cross-judge pool: claude-opus-5-5-max, gpt-5.6-sol-max, grok-4.7-xhigh-fast
swarm workers: grok-4.7-xhigh-fast
architect runners: claude-opus-5-5-max, gpt-5.6-sol-max, grok-4.7-xhigh-fast
interrogate reviewers: claude-opus-5-5-max, gpt-5.6-sol-max, grok-4.7-xhigh-fast
```

### 6. 确认

告诉用户规则已写入，并且它适用于新的会话。重新运行此技能会更新它。

### 7. 提供一个验证技能（可选）

检查项目是否有驱动真实应用以进行验证的方法（一个 `verify-*` 技能，或一个现有的 harness）。如果没有，请提供一次："想要一个项目本地的验证技能，以便代理可以像用户一样驱动应用并证明更改有效？我可以使用 `/create-verification-skill` 生成一个。" 在是的情况下，调用 `/create-verification-skill`（解析 pstack 安装的位置：工作区、用户或插件）。在否的情况下，继续而不推送。
