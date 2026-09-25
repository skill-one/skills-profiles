# 第一天：入职培训

当此技能被调用时，必须严格遵循以下 **停止协议**。

---

## 停止协议 — 绝对禁止违反

> 此协议是此技能的首要规则。
> 违反以下协议会导致课程失败。

### 每个模块必须分两个回合进行

```
┌─ 阶段 A（第一回合） ──────────────────────────────┐
│ 1. 在 references/ 中阅读相应模块文件的 EXPLAIN 部分    │
│ 2. 解释功能                                        │
│ 3. 在 references/ 中阅读相应模块文件的 EXECUTE 部分    │
│ 4. 指导“现在直接运行”                              │
│ 5. ⛔ 在此处必须停止。结束回合。                    │
│                                                          │
│ ❌ 绝对禁止：出题，阅读 QUIZ 部分                     │
│ ❌ 绝对禁止：调用 AskUserQuestion                  │
│ ❌ 绝对禁止：询问“运行了吗？”                        │
└──────────────────────────────────────────────────────────┘

  ⬇️ 等待用户返回并输入“好了”、“完成”、“下一个”等

┌─ 阶段 B（第二回合） ──────────────────────────────┐
│ 1. 在 references/ 中阅读相应模块文件的 QUIZ 部分       │
│ 2. 使用 AskUserQuestion 出题                      │
│ 3. 提供正确/错误的反馈                            │
│ 4. 使用 AskUserQuestion 询问是否进入下一个模块         │
│ 5. ⛔ 开始下一个模块时，重新进入阶段 A。            │
└──────────────────────────────────────────────────────────┘
```

### 核心禁止事项（绝对禁止违反）

1. **在阶段 A 中不调用 AskUserQuestion** — 解释 + 运行指导后立即停止
2. **在阶段 A 中不出题** — QUIZ 部分仅在阶段 B 中读取
3. **在阶段 A 中不询问“运行了吗？”** — 等待用户先说话
4. **一个回合中不同时进行 EXPLAIN + QUIZ** — 必须分两个回合进行

### 公式文档 URL 输出（绝对禁止遗漏）

在所有模块的阶段 A 开始时，必须**原样输出**相应 reference 文件顶部的 `> 公式文档:` URL。

```
📖 公式文档: [URL]
```

- reference 文件中有多个 URL 则全部输出
- 不总结或遗漏 URL
- 参与者必须能直接点击查看公式文档

### 阶段 A 结束时的必要语句

阶段 A 结束时，必须输出以下格式的语句并停止：

```
---
👆 请直接运行上述内容。
运行完成后，请输入“完成”或“下一个”。
```

之后不得输出任何工具调用（包括 AskUserQuestion）或额外文本。

### 模块特殊规则

- **模块 0（设置）**：无测验。阶段 A 中解释+运行指导 → 停止。阶段 B 仅确认完成。
- **模块 1（体验）**：阶段 A 中指导三种演示 → 停止。阶段 B 确认体验感受。
- **模块 2（为何）**：阶段 A 中出题 Quiz 1 → 提供反馈 → 停止。阶段 B 出题 Quiz 2 + 视频指导。
- **模块 3（是什么）**：7个功能各自为独立模块。从 3-1 到 3-7 各自阶段 A → 阶段 B。
- **模块 3-休息（休息）**：只有阶段 A，无阶段 B。无测验。介绍终端 + Status Line 设置体验。
- **模块 4（基础）**：阶段 A 中解释+运行指导 → 停止。阶段 B 连续出题 3 个。

---

## References 文件映射

| 模块 | 文件 |
|------|------|
| Block 0 | `references/block0-setup.md` |
| Block 1 | `references/block1-experience.md` |
| Block 2 | `references/block2-why.md` |
| Block 3-1 ~ 3-4 | `references/block3-1-claude-md.md` ~ `references/block3-4-subagent.md` |
| Block 3-Break | `references/block3-break.md` (休息: 终端 & Status Line) |
| Block 3-5 ~ 3-7 | `references/block3-5-agent-teams.md` ~ `references/block3-7-plugin.md` |
| Block 3 总结 | `references/block3-summary.md` |
| Block 4 | `references/block4-basics.md` |

> 文件路径以此 SKILL.md 为基准的相对路径。
> 每个 reference 文件由 `## EXPLAIN`、`## EXECUTE`、`## QUIZ` 部分构成。

---

## 进度规则

- 一次进行一个模块
- 使用“下一个”、“跳过”、模块编号/名称进行切换
- 如收到 Claude Code 相关问题，则使用 claude-code-guide 代理（内置工具）回答。回答后逐步指导用户自行操作，提问时使用 AskUserQuestion。若判断内置代理回答不准确，则使用 `curl` 将公式文档保存为文件，后使用 Read 工具仔细阅读并重新回答（因 WebFetch 存在摘要/信息丢失风险，故不使用）
- 完成模块 3-4(Subagent) 后 → 模块 3-Break(休息) → 模块 3-5(Agent Teams)
- 完成模块 3 的 7 个功能后 → 阅读 `references/block3-summary.md` 并展示关系图

---

## 开始

技能启动时显示以下表格，并使用 AskUserQuestion 询问从何处开始。

| 模块 | 主题 | 内容 |
|-------|------|------|
| 0 | 设置 | Claude Code 安装 + 首次对话 + CLAUDE.md |
| 1 | 体验 | Working Backward 演示 3 项 |
| 2 | 为何 | 为何 CLI？为何终端？(测验 2 项) |
| 3 | 是什么 | 7 个功能介绍 |
| 4 | 基础 | CLI + git + GitHub (测验 3 项) |

```json
AskUserQuestion({
  "questions": [{
    "question": "从哪里开始？",
    "header": "起始模块",
    "options": [
      {"label": "Block 0: Setup", "description": "Claude Code 安装 + 首次对话 + CLAUDE.md"},
      {"label": "Block 1: Experience", "description": "Working Backward 演示 3 项"},
      {"label": "Block 2: Why", "description": "为何 CLI？为何终端？"},
      {"label": "Block 3: What", "description": "7 个功能介绍"}
    ],
    "multiSelect": false
  }]
})
```

> 选择起始模块后 → 开始该模块的阶段 A。
