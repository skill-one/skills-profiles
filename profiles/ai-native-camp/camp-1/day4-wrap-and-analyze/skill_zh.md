# 第四天：封装与分析

当调用此技能时，必须严格遵循以下 **停止协议**。

---

## 术语解释

本技能中使用的关键术语：

| 术语 | 说明 |
|------|------|
| **session-wrap** | 编码会话结束时进行整理和文档化的技能。"下班前整理办公桌" |
| **multi-agent** | 多个代理同时工作的模式。"会议中同时向各位队长汇报" |
| **并行(Parallel)** | 同时处理多个任务。 "同时向四位队长提交报告"（反义：顺序 = 逐一） |
| **两阶段管道(2-Phase Pipeline)** | 先分析（阶段1，并行）→ 后验证（阶段2，顺序）。"先收集专家意见，再由队长进行重复检查" |
| **frontmatter** | 在技能文件顶部用 `---` 包裹的"标题"。在此处填写技能的名称(name)和描述(description) |
| **history-insight** | 分析过去会话记录以提取见解的技能 |
| **session-analyzer** | 验证技能是否按预期执行的分析工具 |
| **插件(Plugin)** | 从外部安装的技能集合。多个技能组合成的"技能包" |

---

## 停止协议 — 绝对禁止违反

> 此协议是本技能的最高优先级规则。
> 违反以下协议会导致课程失败。

### 每个模块必须分两轮进行

```
┌─ 阶段A（第一轮） ──────────────────────────────┐
│ 1. 在 references/ 中读取对应模块文件的 EXPLAIN 部分    │
│ 2. 解释功能                                        │
│ 3. 在 references/ 中读取对应模块文件的 EXECUTE 部分    │
│ 4. 指导"现在请直接运行"                             │
│ 5. ⛔ 必须在此处停止。结束本轮。                    │
│                                                          │
│ ❌ 绝对禁止：出题，读取 QUIZ 部分                     │
│ ❌ 绝对禁止：AskUserQuestion 调用                      │
│ ❌ 绝对禁止："运行了吗？"提问                         │
└──────────────────────────────────────────────────────────┘

  ⬇️ 等待用户回复"是"、"完成"、"下一个"等

┌─ 阶段B（第二轮） ──────────────────────────────┐
│ 1. 在 references/ 中读取对应模块文件的 QUIZ 部分       │
│ 2. 使用 AskUserQuestion 出题                      │
│ 3. 提供正确/错误的反馈                            │
│ 4. 询问是否跳转到下一个模块（使用 AskUserQuestion）    │
│ 5. ⛔ 开始下一个模块时，重新进入阶段A。                │
└──────────────────────────────────────────────────────────┘
```

### 核心禁止事项（绝对禁止违反）

1. **阶段A中不调用 AskUserQuestion** — 解释+运行说明后立即停止
2. **阶段A中不出题** — QUIZ 部分仅在阶段B中读取
3. **阶段A中不问"运行了吗？"** — 等待用户先发言
4. **一轮中不同时进行 EXPLAIN + QUIZ** — 必须分两轮进行

### 必须输出官方文档 URL（绝对禁止遗漏）

所有模块的阶段A开始时，必须**原样输出**对应 reference 文件顶部的 `> 官方文档:` URL。

```
📖 官方文档: [URL]
```

- reference 文件中存在多个 URL 则全部输出
- 不得总结或遗漏 URL

### 阶段A结束时必须输出的语句

阶段A结束时，必须输出以下格式的语句并停止：

```
---
👆 请直接运行上述内容。
运行完成后，请输入"完成"或"下一个"。
```

输出此语句后，不得输出任何工具调用（包括 AskUserQuestion）或额外文本。

---

## 时间指南

| 模块 | 主题 | 预计时间 |
|------|------|----------|
| 0 | 概念理解 | ~10分钟 |
| 1 | 技能创建 | ~30分钟 |
| 2 | 运行 & 验证 | ~15分钟 |
| 3 | History Insight | ~10分钟 |
| 4 | Session Analyzer + 结束 | ~15分钟 |
| **总计** | | **~80分钟** |

> 根据参与者速度可能需要 75~90 分钟。模块1是耗时最长的核心模块。

---

## 核心策略：通过拆解原技能学习

按以下方式进行：

1. 在模块0中理解 session-wrap 技能的结构和 multi-agent 原理
2. 在模块1中，让参与者直接编写 session-wrap 技能的 SKILL.md（分步指导）
3. 在模块2中，直接运行创建的技能并确认结果
4. 在模块3中，使用 history-insight 分析过去会话记录
5. 在模块4中，使用 session-analyzer 验证技能执行

> session-wrap 原版已安装为插件。参与者可参考此版本创建自己的版本。

---

## 模块特殊规则

- **模块0（概念理解）**: 阶段A中解释 multi-agent 概念 + session-wrap 原版结构分析说明 → 停止。阶段B进行测验。
- **模块1（技能创建）**: 阶段A中指导如何分步编写 SKILL.md → 参与者直接编写 → 停止。阶段B进行编写技能结构的测验。（最长的模块 — 完成后给予"很好，你们都跟得很到位！"的鼓励）
- **模块2（运行 & 验证）**: 阶段A中指导运行创建的技能+确认结果 → 停止。阶段B进行运行结果测验。
- **模块3（History Insight）**: 阶段A中介绍 history-insight 技能+运行说明 → 停止。阶段B进行测验。
- **模块4（Session Analyzer）**: 阶段A中介绍 session-analyzer + 运行说明 → 停止。阶段B进行综合测验+结束。

---

## References 文件映射

| 模块 | 文件 | 主题 |
|------|------|------|
| 模块0 | `references/block0-concept.md` | Multi-agent 模式 + session-wrap 概念 |
| 模块1 | `references/block1-build-session-wrap.md` | 直接编写 session-wrap SKILL.md |
| 模块2 | `references/block2-run-session-wrap.md` | 运行创建的技能+验证 |
| 模块3 | `references/block3-history-insight.md` | history-insight 实践 |
| 模块4 | `references/block4-session-analyzer.md` | session-analyzer 实践 |

> 文件路径是相对于此 SKILL.md 的相对路径。
> 每个 reference 文件由 `## EXPLAIN`, `## EXECUTE`, `## QUIZ` 部分构成。

---

## 进行规则

- 一次进行一个模块
- 使用"下一个"、"跳过"、"模块编号/名称"进行切换
- 模块1创建的技能文件在模块2中运行
- 参与者创建 `.claude/skills/my-session-wrap/SKILL.md` 文件
- 遇到 Claude Code 相关问题则使用 claude-code-guide 代理（内置工具）回答。回答后引导用户分步操作，提问时使用 AskUserQuestion。若判断内置代理回答不准确，则使用 `curl` 将官方文档保存为文件后，使用 Read 工具仔细阅读并给出准确信息（不使用 WebFetch，因其存在总结/信息丢失风险）

---

## 开始

技能开始时**首先安装最新课程**，然后选择模块。

### 第一步：安装最新技能

输出以下命令并使用 Bash 执行：

```bash
npx skills add ai-native-camp/camp-1 --agent claude-code --yes
```

简要说明执行结果（例如："技能已安装为最新版本"）。

### 第二步：选择模块

显示以下表格，并使用 AskUserQuestion 询问从哪里开始：

| 模块 | 主题 | 内容 |
|------|------|------|
| 0 | 概念理解 | Multi-agent 模式，session-wrap 是什么？ |
| 1 | 技能创建 | 直接编写 session-wrap SKILL.md |
| 2 | 运行 & 验证 | 运行创建的技能+结果确认 |
| 3 | History Insight | 会话历史分析实践 |
| 4 | Session Analyzer | 会话执行验证实践 |

```json
AskUserQuestion({
  "questions": [{
    "question": "Day 4: Wrap & Analyze\n\n从哪里开始?",
    "header": "开始模块",
    "options": [
      {"label": "从头开始 (Block 0)", "description": "逐步理解 Multi-agent 模式和 session-wrap 概念"},
      {"label": "技能创建 (Block 1)", "description": "如果已了解概念，直接开始技能编写"},
      {"label": "运行 & 验证 (Block 2)", "description": "如果已创建技能，运行+结果确认"},
      {"label": "分析工具 (Block 3~4)", "description": "从 history-insight 和 session-analyzer 实践开始"}
    ],
    "multiSelect": false
  }]
})
```

> 选择开始模块后 → 从该模块的阶段A开始进行。
