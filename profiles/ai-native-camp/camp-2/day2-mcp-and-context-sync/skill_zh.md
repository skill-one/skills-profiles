# 第 2 天：MCP 与上下文同步

当这个技能被调用时，必须严格遵守以下 **停止协议**。

---

## 术语解释

这个技能中使用的关键术语：

| 术语 | 说明 |
|------|------|
| **MCP** | 模型上下文协议。连接 AI 和外部工具的开放标准。像 USB-C 一样，将多种服务通过一种规范连接起来 |
| **主机/客户端/服务器** | MCP 的三要素。主机=AI 应用 (Claude Code)，客户端=连接管理器，服务器=外部工具提供者 |
| **传输** | MCP 服务器连接方式。HTTP (云服务) 和 stdio (本地执行) 两种 |
| **插件** | 将 Skill + MCP + Hook + Agent 打包的软件包。一行安装代码即可自动连接到 MCP 服务器 |
| **子代理** | Claude 调用其他 Claude 来执行任务。用于同时处理多个任务 |
| **探索代理** | 专门用于识别项目文件夹结构的子代理。只读 |
| **API** | 服务提供的数据接口。在没有 MCP 时，通过代码直接获取数据的方法 |
| **技能(Skill)** | 向 Claude Code 教授特定操作方法文档。在第 1 天 Block 3-2 中体验过的 |
| **STUB** | 后续要填写的空白。标记为“此处将填写后续内容”的占位符。在 Part B 中，每个 Block 填写一个 |
| **骨架** | 只有空白 (STUB) 的框架。相当于建筑中只搭建了钢结构 |
| **frontmatter** | 文件顶部用 `---` 包围的信息区域。在此处填写技能名称、描述、触发器等 |
| **YAML / JSON** | 整理数据的方式。像 Excel 用表格整理数据一样，以文本方式整理数据 |
| **CLI** | 命令行界面。直接在终端输入命令的方式 |

---

## 停止协议 — 绝对禁止违反

> 此协议是此技能的最高优先级规则。
> 违反以下协议会导致课程失败。

### 每个 Block 必须分两轮进行

```
┌─ Phase A (第一轮) ──────────────────────────────┐
│ 1. 在 references/ 中阅读该 Block 文件的 EXPLAIN 部分    │
│ 2. 解释功能                                        │
│ 3. 在 references/ 中阅读该 Block 文件的 EXECUTE 部分    │
│ 4. 指导“现在直接运行”                              │
│ 5. ⛔ 此处必须停止。结束本轮。                      │
│                                                          │
│ ❌ 绝对不做的操作：出题，阅读 QUIZ 部分             │
│ ❌ 绝对不做的操作：AskUserQuestion 调用 (Block 6,7,8,9,10 除外)│
│ ❌ 绝对不做的操作：“运行了吗？”的提问                   │
└──────────────────────────────────────────────────────────┘

  ⬇️ 使用者返回并输入“好了”、“完成”、“下一个”等

┌─ Phase B (第二轮) ──────────────────────────────┐
│ 1. 在 references/ 中阅读该 Block 文件的 QUIZ 部分       │
│ 2. AskUserQuestion 出题                            │
│ 3. 给出正确/错误的反馈                             │
│ 4. AskUserQuestion 询问是否跳转到下一个 Block         │
│ 5. ⛔ 开始下一个 Block 时，再次进入 Phase A。        │
└──────────────────────────────────────────────────────────┘
```

### 核心禁止事项 (绝对禁止违反)

1. **在 Phase A 中不调用 AskUserQuestion (Block 6, 7, 8, 9, 10 除外)** — 这 5 个 Block 需要用户选择/确认，因此是例外
2. **在 Phase A 中不出题** — QUIZ 部分只在 Phase B 中读取
3. **在 Phase A 中不问“运行了吗？”** — 等待用户先说话
4. **在一轮中同时进行 EXPLAIN + QUIZ** — 必须分两轮进行

### 公式文档 URL 输出 (绝对禁止遗漏)

在所有 Block 的 Phase A 开始时，必须**原样输出**该 reference 文件顶部的 `> 公式文档:` URL。

```
📖 公式文档: [URL]
```

- reference 文件中有多个 URL 则全部输出
- 不总结或省略 URL
- 参与者可以直接点击查看公式文档

### Phase A 结束时的必要语句

Phase A 结束时，必须输出以下格式的语句并停止：

```
---
👆 请直接运行上述内容。
运行完成后，请输入“完成”或“下一个”。
```

在此语句之后，**不能**输出任何工具调用 (包括 AskUserQuestion) 或额外文本。

---

## 预计耗时

| Part | Block | 预计时间 |
|------|------|----------|
| Part A: MCP 深入 | Block 0~4 | ~60分钟 |
| Part B: 上下文同步技能制作 | Block 5~10 | ~110分钟 |
| **总计** | **Block 0~10** | **~170分钟** |

---

## 核心策略

### Part A: 从 MCP 概念到 Plugin 系统地学习

从 MCP 的概念 (Block 0) 开始，按顺序进行：添加服务器 (Block 1)、工具探索 (Block 2)、流行服务器安装 (Block 3)、Plugin 扩展 (Block 4)。

### Part B: 4 个工具 × 4 种连接方法 — 逐步构建

按以下方式推进：

1. 在 Block 5 中，基于 `templates/context-sync.md` 创建一个包含 **4 个源 STUB** 的骨架技能文件
2. 在 Block 6~9 中，**每个 Block 使用一种不同的连接方法连接一个工具**，并将对应的源 STUB 填充为实际内容
3. 在 Block 10 中，完成执行流程 + 输出格式，并运行整个技能

> **核心**: 不是批量连接 4 个工具，而是每个 Block **练习不同的连接方式**。

#### Part B Block 结构

| Block | 连接方法 | 工具 | 难度 | 时间 |
|-------|----------|------|------|------|
| 5 | — | 全部 | — | ~12min |
| 6 | claude.ai Connector | Slack | ★☆☆☆ | ~15min |
| 7 | `claude mcp add` | Notion | ★★☆☆ | ~18min |
| 8 | 官方 Plugin (`/plugin`) | Linear | ★★★☆ | ~15min |
| 9 | 社区 Plugin (结构分析) | Google Calendar/Gmail | ★★★★ | ~20min |
| 10 | — (并行收集 + Output + 结束) | 全部 | — | ~20min |

#### 逐步构建 — 模板填充顺序

```
Block 5:  [STUB] [STUB] [STUB] [STUB] [STUB流程] [STUB格式]
Block 6:  [Slack] [STUB] [STUB] [STUB] [STUB流程] [STUB格式]
Block 7:  [Slack] [Notion] [STUB] [STUB] [STUB流程] [STUB格式]
Block 8:  [Slack] [Notion] [Linear] [STUB] [STUB流程] [STUB格式]
Block 9:  [Slack] [Notion] [Linear] [Google] [STUB流程] [STUB格式]
Block 10: [Slack] [Notion] [Linear] [Google] [完成流程] [完成格式] → 运行!
```

#### Block-源映射

| Block | 填充源 | 连接方法 | 技能文件修改区域 |
|-------|--------|----------|------------------|
| 5 | — (创建骨架) | — | 创建整个骨架 |
| 6 | 源 1: Slack | Connector | 源 1 STUB → 实际内容 |
| 7 | 源 2: Notion | `claude mcp add` | 源 2 STUB → 实际内容 |
| 8 | 源 3: Linear | `/plugin install` | 源 3 STUB → 实际内容 |
| 9 | 源 4: Google | 社区 Plugin | 源 4 STUB → 实际内容 |
| 10 | — (完成 + 运行) | — | 完成执行流程 + 输出格式 |

---

## Block 特殊规则

### Part A (Block 0~4)

- **Block 4 [BONUS]**: 只有在有时间时才进行
- 完成 Block 3 后，给出 Part A 结束提示 → Part B 转换提示
- Part A 中学习的 MCP 知识将在 Part B 的工具连接 (Block 7) 中直接应用

### Part B (Block 5~10)

- **Block 5 (创建骨架)**: Phase A 中介绍 Context Sync 概念 + 4 种连接方法 + Explore 进行项目探索 + 基于 `templates/context-sync.md` 创建骨架 → 停止。Phase B 进行测验。
- **Block 6 (Connector → Slack)**: Phase A 中解释 Connector 概念 + Slack Connector 连接说明 + 测试 + 填充技能源 1 → 停止。Phase B 进行测验。
- **Block 7 (mcp add → Notion)**: Phase A 中解释 `claude mcp add` + AskUserQuestion 确认 Notion 使用情况 + 注册 MCP 服务器 + 测试 + 填充技能源 2 → 停止。Phase B 进行测验。
- **Block 8 (Plugin → Linear)**: Phase A 中解释 Plugin 概念 + `/plugin install linear` + 确认 MCP 自动注册 + 测试 + 填充技能源 3 → 停止。Phase B 进行测验。
- **Block 9 (社区 Plugin → Google)**: Phase A 中分析 Plugin 结构 + AskUserQuestion 选择 Calendar/Gmail + Explore 探索 Plugin 结构 + 安装 + 填充技能源 4 → 停止。Phase B 进行测验。
- **Block 10 (并行收集 + Output + 结束)**: Phase A 中 AskUserQuestion 选择输出格式 + 完成执行流程/输出格式 + 运行 4 个源并行收集 + 检查结果 → 停止。Phase B 进行综合测验 + 结束。

#### AskUserQuestion 例外 Block

| Block | 原因 |
|-------|------|
| Block 6 | 确认 Slack 使用情况 (公司账户限制时提供替代方案) |
| Block 7 | 确认 Notion workspace 使用情况 |
| Block 8 | 确认 Linear 使用情况 (未使用时提供替代 Plugin 说明) |
| Block 9 | 选择 Google Calendar vs Gmail vs 都选 |
| Block 10 | 选择 Output format |

#### Block 6 例外规则

Block 6 的 Phase A **使用 AskUserQuestion**。需要确认 Slack 的使用情况和连接是否成功。

使用 Slack 时:
1. 在 claude.ai/settings/connectors 中连接 Slack Connector
2. 使用 `/mcp` 在 claude.ai 部分注册
3. 连接测试后填充技能源 1

Slack 未使用或公司账户限制时 (Plan B):
1. 连接个人 Slack workspace 或 AI Native Camp Slack
2. 说明连接方式本身是重点

> ⚠️ 安全提示: 公司 Slack 可能因管理员政策禁止外部应用连接。这种情况下使用个人 workspace。

#### Block 7 例外规则

Block 7 的 Phase A **使用 AskUserQuestion**。需要确认 Notion 使用情况。

**核心原则**: Claude 代替用户执行设置，用户检查结果。

使用 Notion 时:
1. 执行 `claude mcp add --transport http notion https://mcp.notion.com/mcp`
2. 在 `/mcp` 的 local 部分注册
3. 连接测试后填充技能源 2

Notion 未使用时 (Plan B):
1. 使用 `scripts/mcp_servers.py` 搜索替代 MCP 服务器
2. 从搜索结果中选择并使用 `claude mcp add` 注册

#### Block 8 例外规则

Block 8 的 Phase A **使用 AskUserQuestion**。需要确认 Linear 使用情况。

使用 Linear 时:
1. 执行 `/plugin install linear`
2. 在 `/mcp` 的 local 部分确认 Linear MCP 自动注册
3. 连接测试后填充技能源 3

Linear 未使用时 (Plan B):
1. 使用 `/plugin` 命令查看可安装的官方 Plugin 列表
2. 如果使用中，安装该 Plugin
3. 如果没有 Plugin，可以跳过 Block 8 进入 Block 9
4. **核心**: Plugin 安装 → MCP 自动注册的过程是重点

> ⚠️ 安装 Plugin 后可能需要重新启动 Claude Code。如果 MCP 连接未显示，请重启 Claude Code。

#### Block 9 例外规则

Block 9 的 Phase A **使用 AskUserQuestion**。需要选择 Google Calendar vs Gmail vs 都选。

Phase A 进度顺序:
1. 阅读 `references/block9-skill-google.md` 的 EXPLAIN 部分，解释 Plugin 结构
2. 执行 `/plugin marketplace add team-attention/plugins-for-claude-natives`
3. AskUserQuestion 选择 Calendar/Gmail/都选/Skip
4. 使用 Explore 代理探索 Plugin 目录结构 + 解释
5. 安装选择的工具 Plugin + 测试 + 填充技能源 4 → 停止

#### Block 10 例外规则

Block 10 的 Phase A **使用 AskUserQuestion**。需要选择 Output format。

---

## References 文件映射

### Part A: MCP 深入

| Block | 文件 | 主题 |
|-------|------|------|
| Block 0 | `references/block0-concept.md` | 理解 MCP 概念 |
| Block 1 | `references/block1-add-server.md` | 添加 MCP 服务器 |
| Block 2 | `references/block2-mcp-command.md` | /mcp 命令探索 |
| Block 3 | `references/block3-popular-servers.md` | 探索和安装流行服务器 |
| Block 4 [BONUS] | `references/block4-plugin-mcp.md` | Plugin + MCP |

### Part B: 制作自己的 Context Sync 技能 (4 个工具 × 4 种连接方法)

| Block | 连接方法 | 工具 | 主题 |
|-------|----------|------|------|
| Block 5 | — | 全部 | Context Sync 概念 + 创建骨架 |
| Block 6 | Connector | Slack | 通过浏览器点击连接 Slack |
| Block 7 | `claude mcp add` | Notion | 通过 CLI 命令连接 Notion |
| Block 8 | Plugin (`/plugin`) | Linear | 通过官方 Plugin 连接 Linear |
| Block 9 | 社区 Plugin | Google | 分析 Plugin 结构 + 连接 Google |
| Block 10 | — | 全部 | 并行收集 + Output + 最终运行 |

> 文件路径相对于此 SKILL.md 是相对路径。
> 每个 reference 文件由 `## EXPLAIN`, `## EXECUTE`, `## QUIZ` 部分组成。

---

## Templates / Scripts 文件映射

| 文件 | 用途 |
|------|------|
| `templates/context-sync.md` | Context Sync 技能基础模板 (包含 Slack, Notion, Gmail, GCal 4 种) |
| `scripts/mcp_servers.py` | 从 GitHub 搜索 MCP 服务器 + 解析 README.md + 提供安装说明 |

> Gmail/Calendar 等收集脚本由 Block 7 中 Claude 根据用户选择直接编写。

---

## 进行规则

- 一次进行一个 Block
- 使用“下一个”、“跳过”、Block 编号/名称进行切换
- BONUS Block (Block 4) 只有在有时间时才进行
- 完成 Part A (Block 0~4) 后自然过渡到 Part B (Block 5~10)。Part A 中学习的 MCP 知识将在 Part B 的工具连接 (Block 6~9) 中直接应用
- Block 5 创建的骨架技能文件的 STUB 将在 Block 6~9 中逐个填充。每个 Block 连接工具后，将对应的源部分替换为实际内容
- 在用户项目的 `.claude/skills/my-context-sync/` 目录中创建技能
- Block 6~9 中分别练习 Connector, mcp add, Plugin, 社区 Plugin 的不同连接方式
- 积极使用 Explore 代理和 subagent
- 如果有 Claude Code 相关问题，使用 claude-code-guide 代理 (内置工具) 回答。回答后引导用户按步骤操作，使用 AskUserQuestion 进行提问。如果判断内置代理回答不准确，则使用 `curl` 将公式文档保存为文件，然后使用 Read 工具仔细阅读，并再次提供准确信息

---

## 开始

技能开始时，**首先安装最新课程**，然后选择 Block。

### 步骤 1: 安装最新技能

输出以下命令并使用 Bash 执行：

```bash
npx skills add ai-native-camp/camp-2 --agent claude-code --yes
```

简要说明执行结果 (例如：“技能已安装为最新版本”)。

### 步骤 2: 选择 Block

显示以下表格，并使用 AskUserQuestion 询问从哪里开始。

**Part A: MCP 深入**

| Block | 主题 | 内容 |
|-------|------|------|
| 0 | MCP 概念 | MCP 是什么，为什么需要，类比 USB-C，架构 |
| 1 | 添加服务器 | 已了解 MCP 概念，从实际操作开始 |
| 2 | /mcp 探索 | 查看连接的服务器和工具列表 |
| 3 | 流行服务器 | 从官方列表安装有用的服务器 |
| 4 [BONUS] | Plugin + MCP | 安装包含 MCP 的 Plugin |

**Part B: 制作自己的 Context Sync 技能 (4 个工具 × 4 种连接方法)**

| Block | 连接方法 | 工具 | 内容 |
|-------|----------|------|------|
| 5 | — | 全部 | Context Sync 概念 + 创建骨架 |
| 6 | Connector | Slack | 通过浏览器点击连接 Slack |
| 7 | `claude mcp add` | Notion | 通过 CLI 命令连接 Notion |
| 8 | Plugin (`/plugin`) | Linear | 通过官方 Plugin 连接 Linear |
| 9 | 社区 Plugin | Google | 分析 Plugin 结构 + 连接 Google |
| 10 | — | 全部 | 并行收集 + Output + 最终运行 |

```json
AskUserQuestion({
  "questions": [{
    "question": "Day 2: MCP & Context Sync\n\n从哪里开始?",
    "header": "开始 Block",
    "options": [
      {"label": "Part A: MCP 概念 (Block 0)", "description": "从 MCP 是什么，为什么需要，类比 USB-C，架构开始"},
      {"label": "Part A: 添加服务器 (Block 1)", "description": "已了解 MCP 概念，从实际操作开始"},
      {"label": "Part B: 创建骨架 (Block 5)", "description": "已了解 MCP，从制作技能开始"},
      {"label": "Part B: Notion 连接 (Block 7)", "description": "已连接 Slack，从 mcp add 连接 Notion 开始"}
    ],
    "multiSelect": false
  }]
})
```

> 选择开始 Block 后 → 从该 Block 的 Phase A 开始进行。
