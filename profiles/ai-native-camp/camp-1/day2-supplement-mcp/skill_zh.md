# Day 2 补充：MCP 深入探索

当此技能被调用时，必须严格遵循以下 **停止协议**。

---

## 停止协议 — 绝对禁止违反

> 此协议是此技能的最高优先级规则。
> 违反以下协议会导致课程失败。

### 每个模块必须分两个回合进行

```
┌─ Phase A (第一回合) ──────────────────────────────┐
│ 1. 在 references/ 中阅读相应模块文件的 EXPLAIN 部分    │
│ 2. 解释功能                                        │
│ 3. 在 references/ 中阅读相应模块文件的 EXECUTE 部分    │
│ 4. 指导"现在直接运行"                              │
│ 5. ⛔ 此处必须停止。结束回合。                    │
│                                                          │
│ ❌ 绝对禁止：出题，阅读 QUIZ 部分                   │
│ ❌ 绝对禁止：调用 AskUserQuestion                  │
│ ❌ 绝对禁止："运行了吗？"的提问                   │
└──────────────────────────────────────────────────────────┘

  ⬇️ 等待用户回复"是"、"完成"、"下一个"等

┌─ Phase B (第二回合) ──────────────────────────────┐
│ 1. 在 references/ 中阅读相应模块文件的 QUIZ 部分       │
│ 2. 使用 AskUserQuestion 出题                      │
│ 3. 提供正确/错误的反馈                            │
│ 4. 使用 AskUserQuestion 询问是否进入下一个模块         │
│ 5. ⛔ 开始下一个模块时，重新进入 Phase A。            │
└──────────────────────────────────────────────────────────┘
```

### 核心禁止事项 (绝对禁止违反)

1. **在 Phase A 中不调用 AskUserQuestion** — 解释 + 运行指导后立即停止
2. **在 Phase A 中不出题** — QUIZ 部分仅在 Phase B 中读取
3. **在 Phase A 中不问"运行了吗？"** — 等待用户先发言
4. **一回合内不同时进行 EXPLAIN + QUIZ** — 必须分两个回合进行

### 公式文档 URL 输出 (绝对禁止遗漏)

在所有模块的 Phase A 开始时，必须**原样输出**对应 reference 文件顶部的 `> 公式文档:` URL。

```
📖 公式文档: [URL]
```

- reference 文件中有多个 URL 则全部输出
- 不总结或省略 URL
- 参与者必须能直接点击查看公式文档

### Phase A 结束时的必要语句

Phase A 结束时，必须输出以下格式的语句并停止：

```
---
👆 请直接运行上述内容。
运行完成后请输入"完成"或"下一个"。
```

之后不得输出任何工具调用（包括 AskUserQuestion）或额外文本。

---

## References 文件映射

| 模块 | 文件 | 主题 |
|------|------|------|
| Block 0 | `references/block0-concept.md` | MCP 概念理解 |
| Block 1 | `references/block1-add-server.md` | 添加 MCP 服务器 |
| Block 2 | `references/block2-mcp-command.md` | 使用 /mcp 命令探索工具 |
| Block 3 | `references/block3-popular-servers.md` | 探索和安装热门 MCP 服务器 |
| Block 4 [BONUS] | `references/block4-plugin-mcp.md` | 使用 /plugin 扩展 MCP |

> 文件路径相对于此 SKILL.md。
> 每个reference文件由 `## EXPLAIN`, `## EXECUTE`, `## QUIZ` 部分组成。

---

## 进度规则

- 一次进行一个模块
- 使用"下一个"、"跳过"或模块编号/名称切换
- BONUS 模块仅在有剩余时间时进行
- 接收 Claude Code 相关问题时，使用 claude-code-guide 代理（内置工具）回答。回答后逐步引导用户操作，提问时使用 AskUserQuestion
- 完成Block 3后给出整体结束提示（BONUS Block 4 在有时间时进行）

---

## 开始

技能开始时**首先安装最新课程**，然后选择模块。

### Step 1: 安装最新技能

输出以下命令并使用 Bash 执行：

```bash
npx skills add ai-native-camp/camp-1 --agent claude-code --yes
```

简要说明执行结果（例如："4个技能已安装为最新版本"）。

### Step 2: 选择模块

显示以下表格，并使用 AskUserQuestion 询问从哪里开始。

| 模块 | 主题 | 内容 |
|-------|------|------|
| 0 | MCP 概念 | MCP是什么，USB-C比喻，架构 |
| 1 | 添加服务器 | 使用 `claude mcp add` 连接实际服务器 |
| 2 | /mcp 探索 | 检查已连接服务器和工具列表 |
| 3 | 热门服务器 | 安装官方列表中的有用服务器 |
| 4 [BONUS] | Plugin + MCP | 使用 /plugin 安装包含 MCP 的插件 |

```json
AskUserQuestion({
  "questions": [{
    "question": "从哪里开始？",
    "header": "开始模块",
    "options": [
      {"label": "Block 0: MCP 概念", "description": "了解 MCP 是什么，为什么需要它"},
      {"label": "Block 1: 添加服务器", "description": "立即进行 MCP 服务器连接实践"},
      {"label": "Block 2: /mcp 探索", "description": "先检查已有服务器和工具"},
      {"label": "Block 3: 热门服务器", "description": "查看有哪些服务器可用"}
    ],
    "multiSelect": false
  }]
})
```

> 选择开始模块后 → 进入该模块的 Phase A 进行。
