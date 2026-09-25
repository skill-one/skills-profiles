# 第4天：封装与分析

当调用此技能时，必须严格遵循以下 **停止协议**。

---

## 术语解释

本技能中使用的关键术语：

| 术语 | 说明 |
|------|------|
| **session-wrap** | 编码会话结束时进行整理和文档化的技能。"下班前整理办公桌" |
| **multi-agent** | 多个代理同时工作的模式。"会议中同时向各位队长汇报" |
| **并行(Parallel)** | 同时处理多个任务。"同时向4位队长汇报"（反义：顺序 = 逐一） |
| **2-Phase Pipeline** | 先分析（阶段1，并行）→ 后验证（阶段2，顺序）。"先收集专家意见，再由队长进行重复检查" |
| **frontmatter** | 在技能文件顶部用 `---` 包裹的"标题"。在此处填写技能的名称(name)和描述(description) |
| **history-insight** | 分析过去会话记录以提取见解的技能 |
| **session-analyzer** | 验证技能是否按预期执行的分析工具 |
| **插件(Plugin)** | 外部安装的技能集合。"技能包" |
| **fetch** | 从外部获取数据。"像订外卖一样，只需URL即可收到内容" |
| **digest** | 消化（总结、测验、学习）获取的内容。"不只是阅读，而是要内化" |
| **技能链式调用** | 将一个技能的结果作为另一个技能的输入连接起来。"fetch → digest 管道" |
| **Quiz-First** | 先做测验再阅读总结的学习法。提升9-12%的记忆效果 |
| **compound** | 将验证中的见解记录为结构化文档的技能。"将所学内容整理到笔记中，以便日后搜索" |
| **team-assemble** | 将复杂任务拆分为专家团队并行执行的技能。"自动配置项目TF团队" |
| **content-digest** | 以Quiz-First方式消化获取内容的技能。"不只是阅读，而是通过测验来内化" |

---

## 停止协议 — 绝对禁止违反

> 此协议是本技能的最高优先级规则。
> 违反以下协议会导致课程失败。

### 每个模块必须分两轮进行

```
┌─ Phase A (第一轮) ──────────────────────────────┐
│ 1. 在 references/ 中阅读该模块文件的 EXPLAIN 部分    │
│ 2. 解释功能                                        │
│ 3. 在 references/ 中阅读该模块文件的 EXECUTE 部分    │
│ 4. 指导"现在请直接运行"                             │
│ 5. ⛔ 必须在此处停止。结束本轮。                    │
│                                                          │
│ ❌ 绝对禁止：出题，阅读 QUIZ 部分                   │
│ ❌ 绝对禁止：AskUserQuestion 调用                  │
│ ❌ 绝对禁止："运行了吗？"提问                         │
└──────────────────────────────────────────────────────────┘

  ⬇️ 等待用户输入"是"、"完成"、"下一个"等

┌─ Phase B (第二轮) ──────────────────────────────┐
│ 1. 在 references/ 中阅读该模块文件的 QUIZ 部分       │
│ 2. AskUserQuestion 出题                           │
│ 3. 提供正确/错误反馈                               │
│ 4. AskUserQuestion 询问是否跳转到下一个模块         │
│ 5. ⛔ 开始下一个模块时，必须重新进入 Phase A。        │
└──────────────────────────────────────────────────────────┘
```

### 核心禁止事项（绝对禁止违反）

1. **在 Phase A 中不调用 AskUserQuestion** — 解释+运行说明后立即停止
2. **在 Phase A 中不出题** — QUIZ 部分仅在 Phase B 中读取
3. **在 Phase A 中不问"运行了吗？"** — 等待用户先说话
4. **一轮中不同时进行 EXPLAIN + QUIZ** — 必须分两轮进行

### 必须输出官方文档URL（绝对禁止遗漏）

在所有模块的 Phase A 开始时，必须**原样输出**该 reference 文件顶部的 `> 官方文档:` URL。

```
📖 官方文档: [URL]
```

- reference 文件中有多个 URL 则全部输出
- 不总结或省略 URL

### Phase A 结束时的必要语句

Phase A 结束时，必须输出以下格式的语句并停止：

```
---
👆 请直接运行上述内容。
运行完成后，请输入"完成"或"下一个"。
```

之后**不能**输出任何工具调用（包括 AskUserQuestion）或额外文本。

---

## 时间指南

| 模块 | 主题 | 预计时间 |
|------|------|-----------|
| 0 | 概念理解 | ~10分钟 |
| 1 | 技能制作 | ~30分钟 |
| 2 | 运行 & 验证 | ~15分钟 |
| 3 | History Insight | ~10分钟 |
| 4 | Session Analyzer | ~15分钟 |
| 5 | 内容消化体验 + 奖励技能 + 结束 | ~25分钟 |
| **总计** | | **~105分钟** |

> 根据参与者速度，可能需要 90-110 分钟。Block 1 是最耗时的核心模块。Block 5（内容消化）以体验为主，会快速进行。

---

## 核心策略：通过拆解原技能来学习

按以下方式进行：

1. 在 Block 0 中理解 session-wrap 技能的结构和 multi-agent 原理
2. 在 Block 1 中，让参与者直接编写 session-wrap 技能的 SKILL.md（分步指导）
3. 在 Block 2 中，直接运行制作的技能并确认结果
4. 在 Block 3 中，使用 history-insight 分析过去会话记录
5. 在 Block 4 中，使用 session-analyzer 验证技能执行
6. 在 Block 5 中体验内容消化管道(fetch-tweet + content-digest)
7. 在 Block 5 中体验内容消化管道(fetch-tweet → content-digest)
8. 在 Block 5 选择练习中，使用 compound 记录见解，使用 team-assemble 体验代理团队配置

> session-wrap 原版已安装在插件中。参与者可参考此原版制作自己的版本。

---

## 模块特殊规则

- **Block 0 (概念理解)**: Phase A 中解释 multi-agent 概念 + session-wrap 原版结构分析说明 → 停止。Phase B 进行测验。
- **Block 1 (技能制作)**: Phase A 中指导 Step-by-Step 编写 SKILL.md → 参与者直接编写 → 停止。Phase B 进行编写技能结构测验。（最长模块 — 完成后给予"很好，您已经很好地跟随了！"鼓励）
- **Block 2 (运行 & 验证)**: Phase A 中指导运行制作技能+确认结果 → 停止。Phase B 进行运行结果测验。
- **Block 3 (History Insight)**: Phase A 中介绍 history-insight 技能+运行说明 → 停止。Phase B 进行测验。
- **Block 4 (Session Analyzer)**: Phase A 中介绍 session-analyzer + 运行说明 → 停止。Phase B 进行测验。
- **Block 5 (内容消化体验)**: Phase A 中解释 fetch-tweet 和 content-digest 概念+实际用推文体验+介绍 compound/team-assemble → 停止。Phase B 进行综合测验+4天训练营结束。

---

## References 文件映射

| 模块 | 文件 | 主题 |
|------|------|------|
| Block 0 | `references/block0-concept.md` | Multi-agent 模式 + session-wrap 概念 |
| Block 1 | `references/block1-build-session-wrap.md` | 直接制作 session-wrap 技能 |
| Block 2 | `references/block2-run-session-wrap.md` | 运行制作技能+验证 |
| Block 3 | `references/block3-history-insight.md` | history-insight 实践 |
| Block 4 | `references/block4-session-analyzer.md` | session-analyzer 实践 |
| Block 5 | `references/block5-content-experience.md` | 内容消化体验 (fetch-tweet + content-digest + 奖励技能) |

> 文件路径是相对于此 SKILL.md 的相对路径。
> 每个 reference 文件由 `## EXPLAIN`, `## EXECUTE`, `## QUIZ` 部分组成。

---

## 进行规则

- 一次进行一个模块
- 使用"下一个"、"跳过"、"模块编号/名称"进行切换
- Block 1 中创建的技能文件在 Block 2 中运行
- 参与者创建 `.claude/skills/my-session-wrap/SKILL.md`
- 关于 Claude Code 的问题，使用 claude-code-guide 代理（内置工具）回答。回答后逐步指导用户自行操作，提问时使用 AskUserQuestion。若判断内置代理回答不准确，则使用 `curl` 将官方文档保存为文件后，用 Read 工具仔细阅读并准确回答（不使用 WebFetch，因其有摘要/信息损失风险）

---

## 开始

技能开始时，**必须先安装最新课程**，然后选择模块。

### 第1步：最新技能更新（必选！）

> **从 Day 4 开始大量新增了技能！** 必须执行以下命令更新。
> 不更新将导致无法使用今天的技能。

输出以下命令并使用 Bash 执行：

```bash
npx skills add ai-native-camp/camp-2 --agent claude-code --yes
```

简要说明执行结果，并展示新增技能列表：

| 新增技能 | 说明 |
|-----------------|------|
| session-wrap | 会话结束时自动整理工作的 multi-agent 技能 |
| history-insight | 分析过去会话记录提取见解 |
| session-analyzer | 验证技能是否按预期执行 |
| fetch-tweet | 获取 X/Twitter 推文进行翻译/摘要 |
| content-digest | 以 Quiz-First 方式消化内容 |
| compound | 将工作中发现的见解记录为结构化文档 |
| team-assemble | 将复杂任务拆分为专家代理团队并行执行 |

### 第2步：模块选择

展示以下表格，并使用 AskUserQuestion 询问从哪里开始：

| 模块 | 主题 | 内容 |
|------|------|------|
| 0 | 概念理解 | Multi-agent 模式，session-wrap 是什么？ |
| 1 | 技能制作 | 直接编写 session-wrap SKILL.md |
| 2 | 运行 & 验证 | 运行制作技能+结果确认 |
| 3 | History Insight | 会话历史分析实践 |
| 4 | Session Analyzer | 会话执行验证实践 |
| 5 | 内容消化体验 | fetch-tweet + Quiz-First 体验+结束 |

```json
AskUserQuestion({
  "questions": [{
    "question": "Day 4: Wrap & Analyze\n\n从哪里开始?",
    "header": "开始模块",
    "options": [
      {"label": "从头开始 (Block 0)", "description": "从 Multi-agent 模式和 session-wrap 概念开始逐步学习"},
      {"label": "技能制作 (Block 1)", "description": "如果已了解概念，可以直接制作技能"},
      {"label": "运行 & 验证 (Block 2)", "description": "如果已制作技能，可以直接运行+结果确认"},
      {"label": "分析工具 (Block 3~4)", "description": "从 history-insight 和 session-analyzer 实践开始"},
      {"label": "内容消化 (Block 5)", "description": "fetch-tweet + content-digest + compound + team-assemble 体验"}
    ],
    "multiSelect": false
  }]
})
```

> 选择开始模块后 → 进入该模块的 Phase A 进行。
