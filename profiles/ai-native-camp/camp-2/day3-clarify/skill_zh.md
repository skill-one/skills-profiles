# Day 3: 明确

当此技能被调用时，必须严格遵循以下 **停止协议**。

---

## 术语解释

| 术语 | 说明 |
|------|------|
| **明确 (Clarify)** | 将模糊的需求明确化的过程。Claude 通过提问将隐含需求转换为明确需求 |
| **AskUserQuestion** | Claude 向用户提出结构化问题的工具。通过提供选项来降低认知负荷 |
| **假设选项 (Hypothesis-as-Options)** | 用选项提供假设代替开放式提问的原则。"想要什么？" 而不是 "A/B/C 中哪个？" |
| **插件 (Plugin)** | 将 Skill + MCP + Hook + Agent 打包为一个安装单元的软件包 |
| **已知/未知 (Known/Unknown)** | 用于寻找策略盲区的四象限框架 (KK/KU/UK/UU) |
| **前后对比 (Before/After)** | 通过比较明确前后需求来可视化变化的格式 |
| **PRD** | 产品需求文档。整理"这个项目要解决什么问题，要创建什么"的文档 |
| **GitHub** | 代码和文档的在线管理和共享服务。相当于 Google Docs 的代码版本 |
| **PR (Pull Request)** | 向运营团队发送"请确认我的工作"的审核请求。相当于提交按钮 |

---

## 停止协议 — 绝对禁止违反

> 此协议是此技能的最高优先级规则。
> 违反以下规则会导致课程失败。

### 每个模块必须分两轮进行

```
┌─ Phase A (第一轮) ──────────────────────────────┐
│ 1. 读取 references/ 中的对应模块文件 EXPLAIN 部分    │
│ 2. 解释功能                                              │
│ 3. 读取 references/ 中的对应模块文件 EXECUTE 部分    │
│ 4. 指导"现在直接运行"                                     │
│ 5. ⛔ 必须在此处停止。结束本轮。                          │
│                                                          │
│ ❌ 绝对禁止: 出题, 读取 QUIZ 部分                      │
│ ❌ 绝对禁止: 调用 AskUserQuestion                      │
│ ❌ 绝对禁止: 询问"运行了吗？"                             │
└──────────────────────────────────────────────────────────┘

  ⬇️ 等待用户回复"是", "完成", "下一个"等

┌─ Phase B (第二轮) ──────────────────────────────┐
│ 1. 读取 references/ 中的对应模块文件 QUIZ 部分       │
│ 2. 使用 AskUserQuestion 出题                        │
│ 3. 提供正确/错误反馈                                  │
│ 4. 使用 AskUserQuestion 询问是否进入下一个模块         │
│ 5. ⛔ 开始下一个模块时，重新进入 Phase A。            │
└──────────────────────────────────────────────────────────┘
```

### 核心禁止事项 (绝对禁止)

1. **Phase A 中不调用 AskUserQuestion** — 解释+运行指导后立即停止
2. **Phase A 中不出题** — QUIZ 部分只在 Phase B 中读取
3. **Phase A 中不询问"运行了吗？"** — 等待用户先说话
4. **一轮中不同时进行 EXPLAIN + QUIZ** — 必须分两轮进行

### Phase A 结束时的必要语句

Phase A 结束时必须输出以下格式的语句并停止：

```
---
👆 请直接运行上述内容。
运行完成后请输入"完成"或"下一个"。
```

输出此语句后不得再输出任何工具调用(包括 AskUserQuestion)或额外文本。

### 模块特殊规则

- **模块 0 (概念)**: 标准 Phase A/B。AskUserQuestion 体验是 EXECUTE 的核心。
- **模块 1 (模糊体验)**: **例外** — Phase A 中 Claude 会演示 clarify:vague 协议。当学生提出模糊需求时，Claude 会使用 AskUserQuestion 进行明确。学生扮演"接收明确者"角色。
- **模块 2 (构建明确)**: 标准流程，但在 EXECUTE 中读取插件 vague SKILL.md 后，基于模板编写自己的技能。
- **模块 3 (插件与未知)**: **主模块** — 插件深度分析 + clarify:unknown 体验。
- **模块 4 (PRD & GitHub)**: 标准 Phase A/B，但 PRD 编写是交互式的。Claude 会自动完成 GitHub ID 验证 → PRD 草稿编写 → 验证 → PR 提交。Phase B 测验后说明 Day 3 作业。

---

## 预计时间

| 模块 | 主题 | 时间 |
|------|------|------|
| 0 | 明确概念 + AskUserQuestion | ~10分钟 |
| 1 | clarify:vague 体验 | ~15分钟 |
| 2 | 编写自己的明确技能 | ~25分钟 |
| 3 | 插件深度分析 + clarify:unknown 体验 | ~30分钟 |
| 4 | PRD 编写 & GitHub 首次提交 + 作业 | ~15分钟 |
| | **总计** | **~95分钟** |

---

## 核心策略

> **"解构已安装的插件，并亲自编写"**

Day 1 中安装的 clarify 插件体验 → 结构分析 → 编写自己的版本 → 深度应用

```
Day 1 安装          Day 3 深入分析
┌──────────────┐       ┌──────────────────────────┐
│ /plugin      │       │ 模块 0: 概念理解        │
│   install    │  ───▶ │ 模块 1: vague 体验       │
│   clarify    │       │ 模块 2: 编写技能        │
└──────────────┘       │ 模块 3: 插件解构 +      │
                       │         unknown 体验     │
                       │ 模块 4: PRD + GitHub 提交 │
                       └──────────────────────────┘
```

---

## References 文件映射

| 模块 | 文件 |
|------|------|
| 模块 0 | `references/block0-concept.md` |
| 模块 1 | `references/block1-experience-vague.md` |
| 模块 2 | `references/block2-build-clarify.md` |
| 模块 3 | `references/block3-plugin-and-unknown.md` |
| 模块 4 | `references/block4-prd-and-github.md` |

> 文件路径相对于此 SKILL.md 是相对路径。
> 每个参考文件由 `## EXPLAIN`, `## EXECUTE`, `## QUIZ` 部分组成。

---

## Templates 文件映射

| 文件 | 用途 |
|------|------|
| `templates/clarify-vague.md` | 编写自己的明确技能模板 |

---

## 进度规则

- 一次一个模块
- 使用"下一个", "跳过", 模块编号/名称切换
- 遇到 Claude Code 相关问题时，使用 claude-code-guide 代理(内置工具)回答。回答后引导用户分步骤操作，提问时使用 AskUserQuestion。若判断内置代理回答不准确，则使用 `curl` 将官方文档保存为文件后，通过 Read 工具仔细阅读并重新回答(不使用 WebFetch，因其有摘要/信息损失风险)

---

## 开始

技能开始时引导以下内容并使用 AskUserQuestion 询问从哪里开始。

> 如果尚未安装 camp-2 技能：
> ```
> npx skills add ai-native-camp/camp-2
> ```

| 模块 | 主题 | 内容 |
|------|------|------|
| 0 | 概念 | 明确概念 + AskUserQuestion 体验 |
| 1 | 体验 | clarify:vague 插件体验 |
| 2 | 构建 | 编写自己的明确技能 |
| 3 | 插件与未知 | 插件深度分析 + clarify:unknown |
| 4 | PRD & GitHub | PRD 编写 + GitHub 首次 PR 提交 + 作业 |

```json
AskUserQuestion({
  "questions": [{
    "question": "从哪里开始?",
    "header": "选择模块",
    "options": [
      {"label": "模块 0: 概念", "description": "明确概念 + AskUserQuestion 体验"},
      {"label": "模块 1: 体验", "description": "clarify:vague 插件体验"},
      {"label": "模块 2: 构建", "description": "编写自己的明确技能"},
      {"label": "模块 3: 插件与未知", "description": "插件深度分析 + unknown 体验"},
      {"label": "模块 4: PRD & GitHub", "description": "PRD 编写 + GitHub 首次 PR 提交"}
    ],
    "multiSelect": false
  }]
})
```

> 选择模块后 → 从该模块的 Phase A 开始进行。
