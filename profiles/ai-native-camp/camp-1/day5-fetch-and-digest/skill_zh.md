# 第 5 天：获取与消化——将内容内化的技能

当调用此技能时，必须严格遵守以下 **停止协议**。

---

## 术语解释

本技能中使用的关键术语：

| 术语 | 说明 |
|------|------|
| **fetch** | 从外部获取数据。 "就像订外卖一样，只给 URL 内容就会送达" |
| **digest** | 消化获取的内容（摘要·测验·学习）。 "不只是阅读就结束，而是要咀嚼内化为自己的东西" |
| **API** | 程序间对话的窗口。 "就像餐厅菜单一样，请求格式是固定的" |
| **JSON** | 电脑易于读取的数据格式。 人看起来是花括号一堆，但 Claude 完全理解 |
| **yt-dlp** | 从 YouTube 提取字幕·元数据的免费工具 |
| **自动字幕** | YouTube 用 AI 制作的字幕。 专业术语或名称可能出错 |
| **Web Search 修正** | 用网络搜索立即纠正自动字幕的错误 |
| **Quiz-First** | 不先看摘要，先做测验的学习法。 提高记忆效果 9-12% |
| **技能链式** | 将一个技能的结果作为另一个技能的输入来连接。 "fetch → digest 管道" |

---

## 停止协议——绝对禁止违反

> 此协议是本技能的最高优先级规则。
> 违反以下协议会导致课程失败。

### 每个模块必须分两轮进行

```
┌─ Phase A (第一轮) ──────────────────────────────┐
│ 1. 在 references/ 中阅读对应模块文件的 EXPLAIN 部分    │
│ 2. 解释功能                                        │
│ 3. 在 references/ 中阅读对应模块文件的 EXECUTE 部分    │
│ 4. 指导 "现在直接运行"                              │
│ 5. ⛔ 必须在这里停止。结束本轮。                    │
│                                                          │
│ ❌ 绝对不能做：出题，阅读 QUIZ 部分                 │
│ ❌ 绝对不能做：AskUserQuestion 调用                  │
│ ❌ 绝对不能做："运行了吗？" 询问                       │
└──────────────────────────────────────────────────────────┘

  ⬇️ 等待用户回复 "是"、"完成"、"下一个" 等

┌─ Phase B (第二轮) ──────────────────────────────┐
│ 1. 在 references/ 中阅读对应模块文件的 QUIZ 部分       │
│ 2. 用 AskUserQuestion 出题                        │
│ 3. 给出正确/错误的反馈                            │
│ 4. 询问是否要跳转到下一个模块                      │
│ 5. ⛔ 开始下一个模块后，再次进入 Phase A。            │
└──────────────────────────────────────────────────────────┘
```

### 核心禁止事项（绝对禁止违反）

1. **Phase A 中不调用 AskUserQuestion** — 解释+运行指导后立即停止
2. **Phase A 中不出题** — QUIZ 部分只在 Phase B 中读取
3. **Phase A 中不问 "运行了吗？"** — 等待用户先说话
4. **一轮中不同时进行 EXPLAIN + QUIZ** — 必须分两轮进行

### 必须输出官方文档 URL（绝对不能遗漏）

在所有模块的 Phase A 开始时，必须**原样输出**对应 reference 文件顶部的 `> 官方文档:` URL。

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
运行完成后请输入 "完成" 或 "下一个"。
```

之后**不能**输出任何工具调用（包括 AskUserQuestion）或额外文本。

---

## 时间指南

| 模块 | 主题 | 预计时间 |
|------|------|-----------|
| 0 | 概念理解 | ~10分钟 |
| 1 | fetch-tweet 技能制作 | ~20分钟 |
| 2 | fetch-youtube 技能制作 | ~30分钟 |
| 3 | content-digest 技能制作 | ~20分钟 |
| 4 | 综合练习+总结 | ~15分钟 |
| **总计** | | **~95分钟** |

> Block 2 是耗时最长的核心模块。包含 yt-dlp 设置和 Web Search 修正。
> **推荐提前准备**: 提前安装 yt-dlp 可以节省 Block 2 10 分钟以上时间。(`brew install yt-dlp` 或 `pip install yt-dlp`)
> **快速通道**: 如果时间不足，可以将 Block 1~3 各自作为一个提示语一次性制作完成。

---

## 核心策略：通过拆解实际技能来学习

按以下方式推进：

1. 在 Block 0 中理解内容消化管道(fetch → digest)的概念
2. 在 Block 1 中直接制作 fetch-tweet 技能（API 使用+翻译管道）
3. 在 Block 2 中直接制作 fetch-youtube 技能（字幕提取+Web Search 修正）
4. 在 Block 3 中直接制作 content-digest 技能（Quiz-First 学习）
5. 在 Block 4 中将 3 个技能连接起来用实际内容进行练习

> 参考运营人员实际使用的技能(fetch-tweet, content-digest)制作自己的版本。

---

## 模块特殊规则

- **Block 0 (概念理解)**: Phase A 中解释内容管道概念+分析原始技能结构 → 停止。Phase B 进行测验。
- **Block 1 (fetch-tweet)**: Phase A 中指导如何 Step-by-Step 制作 fetch-tweet 技能 → 参与者直接编写 → 停止。Phase B 进行测验。
- **Block 2 (fetch-youtube)**: Phase A 中指导制作 fetch-youtube 技能（yt-dlp + Web Search 修正）→ 参与者直接编写 → 停止。Phase B 进行测验。 (最长的模块—完成后给予 "很好，你一直跟得很好！" 鼓励)
- **Block 3 (content-digest)**: Phase A 中指导制作 content-digest 技能（Quiz-First 学习）→ 参与者直接编写 → 停止。Phase B 进行测验。
- **Block 4 (综合练习)**: Phase A 中指导 3 个技能连接的练习 → 用实际内容练习 → 停止。Phase B 进行综合测验+总结。

---

## reference 文件映射

| 模块 | 文件 | 主题 |
|------|------|------|
| Block 0 | `references/block0-concept.md` | 内容消化管道+技能链式 |
| Block 1 | `references/block1-fetch-tweet.md` | fetch-tweet 技能制作 |
| Block 2 | `references/block2-fetch-youtube.md` | fetch-youtube 技能制作 |
| Block 3 | `references/block3-content-digest.md` | content-digest 技能制作 |
| Block 4 | `references/block4-integration.md` | 综合练习+总结 |

> 文件路径是相对于 SKILL.md 的相对路径。
> 每个 reference 文件由 `## EXPLAIN`, `## EXECUTE`, `## QUIZ` 部分组成。

---

## 进行规则

- 一次进行一个模块
- 用 "下一个"、"skip"、模块编号/名称进行跳转
- 每个模块中创建的技能文件将在下一个模块中继续使用
- 参与者将技能创建在 `.claude/skills/` 下
- 如果收到 Claude Code 相关问题，用 claude-code-guide 代理（内置工具）回答。回答后引导用户分步骤操作，提问时使用 AskUserQuestion。如果判断内置代理回答不准确，则用 `curl` 将官方文档保存为文件后用 Read 工具仔细阅读，再用准确信息回答（WebFetch 有摘要/信息损失风险，因此不使用）

---

## 开始

技能开始时**首先安装最新课程**后选择模块。

### Step 1: 安装最新技能

输出以下命令并用 Bash 执行：

```bash
npx skills add ai-native-camp/camp-1 --agent claude-code --yes
```

简要说明执行结果（例如："技能已安装为最新版本"）。

### Step 2: 选择模块

显示以下表格并使用 AskUserQuestion 询问从哪里开始：

| 模块 | 主题 | 内容 |
|------|------|------|
| 0 | 概念理解 | 内容消化管道、技能链式是什么？ |
| 1 | fetch-tweet | 制作从 X/Twitter 获取并翻译推文的技能 |
| 2 | fetch-youtube | 制作从 YouTube 获取并翻译字幕的技能 |
| 3 | content-digest | 制作用获取内容进行测验-学习的技能 |
| 4 | 综合练习 | 连接 3 个技能用实际内容进行练习 |

```json
AskUserQuestion({
  "questions": [{
    "question": "Day 5: Fetch & Digest\n\n从哪里开始？",
    "header": "开始模块",
    "options": [
      {"label": "从头开始 (Block 0)", "description": "从内容管道概念逐步学习"},
      {"label": "fetch-tweet (Block 1)", "description": "直接制作推文技能"},
      {"label": "fetch-youtube (Block 2)", "description": "直接制作 YouTube 技能"},
      {"label": "content-digest (Block 3~4)", "description": "制作测验-学习技能"}
    ],
    "multiSelect": false
  }]
})
```

> 选择开始模块后 → 进入该模块的 Phase A 进行。
