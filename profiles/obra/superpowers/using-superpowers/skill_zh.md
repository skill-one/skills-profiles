<SUBAGENT-STOP]
如果你被派发作为子代理以执行特定任务，请忽略此技能。
</SUBAGENT-STOP>

<<EXTREMELY-IMPORTANT>>
即使你认为存在哪怕 1% 的可能性，某个技能可能适用于你的任务，你也 ABSOLUTELY 必须调用该技能。

如果技能适用于你的任务，你没有选择，必须使用它。

这不是可以讨价还价的问题。你无法通过理性方式规避此要求。
</EXTREMELY-IMPORTANT>>

## The Rule

**在作出任何回应或操作之前，调用相关或要求的技能** — 包括澄清问题、探索代码库或检查文件。

**在进入计划模式之前：** 如果你尚未进行头脑风暴，请先调用 brainstorming 技能。

然后宣布“使用 [技能] 来 [目的]”，并严格按照该技能的要求操作。如果该技能有清单，请为每一项创建一个待办事项。

## Skill Priority

当多个技能适用时，先处理流程技能——它们设定方法，然后实现技能（如前端设计等）来执行。头脑风暴和 systematic-debugging 是 Superpowers 中最常见的流程技能，但此规则适用于其中任何技能。

- “让我们构建 X” → 先调用 superpowers:brainstorming，然后调用实现技能。
- “修复此 Bug” → 先调用 superpowers:systematic-debugging，然后调用领域技能。

## Red Flags

当出现以下想法时，意味着你必须停止——你正在进行合理化：

**想法 | 现实**

---

"只是简单的问题" | "问题属于任务。检查是否有相关技能。"

"需要先获得更多信息" | "技能检查应在澄清问题之前进行。"

"让我先探索代码库" | "技能会告诉你如何探索。先检查。"

"我可以快速检查 git/文件" | "文件缺乏对话上下文。检查相关技能。"

"让我先收集信息" | "技能会告诉你如何收集信息。"

"这不需要正式技能" | "如果存在技能，请使用它。"

"我记得这个技能" | "技能会更新。阅读当前版本。"

"这不算是任务" | "行动 = 任务。检查相关技能。"

"这个技能大材小用" | "简单的事情也会变得复杂。请使用它。"

"我先做这一件事" | "在做任何事之前先检查。"

"这感觉很有成效" | "不自律的行动会浪费时间。技能可以防止这种情况。"

"我知道这含义" | "了解概念 ≠ 使用技能。请调用它。"

## Platform Adaptation

如果当前平台显示此处，请阅读其参考文件以获取特殊指令：

- Claude Code: `references/claude-code-tools.md`
- Codex: `references/codex-tools.md`
- Pi: `references/pi-tools.md`
- Antigravity: `references/antigravity-tools.md`
- Hermes Agent: `references/hermes-tools.md`
- Muse: `references/muse-tools.md`

## 用户指令

用户指令（CLAUDE.md、AGENTS.md、GEMINI.md 等，直接请求）优先于技能，而技能又覆盖默认行为。仅当你的合作者明确要求你时才跳过技能工作流或相关指令。
