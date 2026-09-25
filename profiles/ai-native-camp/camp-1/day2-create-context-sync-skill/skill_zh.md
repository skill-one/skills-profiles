# 第 2 天：创建我的专属 Context Sync 技能

当此技能被调用时，必须严格遵循以下 **STOP 协议**。

---

## 术语解释

本技能中使用的关键术语：

| 术语 | 说明 |
|------|------|
| **MCP** | Claude 与外部服务（Slack、Gmail 等）对话的通道。Day 1 中学习的“工具”的外部扩展 |
| **subagent** | Claude 调用其他 Claude 来执行任务。用于同时处理多项任务 |
| **Explore Agent** | 专门用于分析项目文件夹结构的 subagent |
| **API** | 服务提供的数据接口。在没有 MCP 时，通过代码直接获取数据的方法 |
| **技能 (Skill)** | 向 Claude Code 教授特定操作方法的文档。Day 1 Block 3-2 中体验过的内容 |

---

## STOP 协议 — 绝对禁止违反

> 此协议是本技能的最高优先级规则。
> 违反以下协议会导致课程失败。

### 每个区块必须在 2 轮内完成

```
┌─ Phase A (第一轮) ──────────────────────────────┐
│ 1. 读取 references/ 中对应区块文件的 EXPLAIN 部分    │
│ 2. 解释功能                                        │
│ 3. 读取 references/ 中对应区块文件的 EXECUTE 部分    │
│ 4. 指导“现在直接运行”                              │
│ 5. ⛔ 此处必须停止。结束本轮。                    │
│                                                          │
│ ❌ 绝对禁止：出题，读取 QUIZ 部分                   │
│ ❌ 绝对禁止：AskUserQuestion 调用（Block 0、2、4 除外）│
│ ❌ 绝对禁止：询问“运行了吗？”                        │
└──────────────────────────────────────────────────────────┘

  ⬇️ 等待用户回复“是”、“完成”、“下一步”等输入

┌─ Phase B (第二轮) ──────────────────────────────┐
│ 1. 读取 references/ 中对应区块文件的 QUIZ 部分       │
│ 2. 使用 AskUserQuestion 出题                      │
│ 3. 提供正确/错误反馈                              │
│ 4. 询问是否跳转到下一个区块                        │
│ 5. ⛔ 开始下一个区块时，重新进入 Phase A。          │
└──────────────────────────────────────────────────────────┘
```

### 核心禁止事项（绝对禁止违反）

1. **Phase A 中不调用 AskUserQuestion（Block 0、2、4 除外）** — 这 3 个区块需要用户选择，因此是例外
2. **Phase A 中不出题** — QUIZ 部分仅在 Phase B 中读取
3. **Phase A 中不询问“运行了吗？”** — 等待用户先发言
4. **一轮内不同时进行 EXPLAIN + QUIZ** — 必须分两轮进行

### 必须输出官方文档 URL（绝对禁止遗漏）

在所有区块的 Phase A 开始时，必须**原样输出**对应 reference 文件顶部的 `> 官方文档:` URL。

```
📖 官方文档: [URL]
```

- reference 文件中有多个 URL 则全部输出
- 不总结或遗漏 URL

### Phase A 结束时的必要语句

Phase A 结束时，必须输出以下格式的语句并停止：

```
---
👆 请直接运行上述内容。
运行完成后，请输入“完成”或“下一步”。
```

在此语句之后，**不能**输出任何工具调用（包括 AskUserQuestion）或额外文本。

---

## 核心策略：先模板，再逐步定制

按以下方式推进：

1. 在 Block 0 中，如果用户选择工具，则基于 `templates/context-sync.md` 立即创建技能文件
2. 之后在 Block 1~5 中仅修改/扩展已创建技能的对应部分
3. 最终运行完成的技能以确认结果

> 模板中包含 Slack、Notion、Gmail、Google Calendar 四种工具的示例。
> 根据用户选择的工具组合，保留必要的部分，新工具按相同模式添加。

### 区块-模板部分映射

每个区块修改的模板区域：

| 区块 | 修改对象 | 模板部分 |
|------|----------|------------|
| 0 | 技能框架创建 | 全部（仅保留所选工具） |
| 1 | 反映项目上下文 | frontmatter description, 收集范围 |
| 2 | 确定连接方式 | 每个源的“收集方法” |
| 3 | 收集执行 & 验证 | “执行流程”部分 + 调整“提取信息” |
| 4 | 设置输出格式 | “输出格式”部分 |
| 5 | 最终整理 + 执行 | 全部收尾 |

---

## 区块特殊规则

- **Block 0（工具选择 + 技能创建）**：Phase A 中解释 + AskUserQuestion 选择工具。根据选择结果基于模板创建技能 → 停止。Phase B 中对创建的技能进行确认性提问。
- **Block 1（项目探索）**：Phase A 中使用 Explore Agent 探索项目结构并分享结果 → 停止。Phase B 中提问。
- **Block 2（工具连接）**：Phase A 中提供 MCP vs API 选择说明 + AskUserQuestion → **Claude 代替执行设置**，用户仅确认结果 → 停止。Phase B 中提问。
- **Block 3（收集执行 & 验证）**：Phase A 中解释 subagent 并行收集 + 执行 → 将收集结果按成功/失败分类展示 → 对失败源进行重试 + 检查收集数据质量 → 停止。Phase B 中提问。
- **Block 4（Output 设置）**：Phase A 中提供 Output format 选择说明 + AskUserQuestion → 根据选择修改技能 → 停止。Phase B 中提问。
- **Block 5（完成 + 执行）**：Phase A 中整理最终技能配置 + 实际执行 → 停止。Phase B 中进行综合提问 + 结束。

### Block 0 异常规则

Block 0 的 Phase A **必须使用 AskUserQuestion**。工具选择是后续所有区块的前提，必须接收用户输入。

Phase A 进行动序：
1. 读取 `references/block0-tool-selection.md` 的 EXPLAIN 部分
2. AskUserQuestion 接收工具选择（multiSelect: true）
3. 读取 `templates/context-sync.md` 模板
4. 根据所选工具为用户的项目创建 `.claude/skills/my-context-sync/SKILL.md`
5. 简要展示创建文件的整体结构并停止（详细内容后续区块处理）

### Block 2 异常规则

Block 2 的 Phase A 也**必须使用 AskUserQuestion**。需要为每个工具选择 MCP 或 API 连接方式。

**核心原则**：Claude 代替执行设置，用户仅确认结果。

MCP 选择时：
1. 遵循 `references/block2-tool-connection.md` 的 MCP 说明
2. 使用 `scripts/mcp_servers.py` 从 GitHub README.md 搜索合适的 MCP 服务器
3. 展示搜索结果，Claude 将服务器注册到 `.mcp.json`
4. 使用 `/mcp` 命令确认服务器连接状态

API 选择时：
1. Claude 直接编写 API 调用代码
2. 保存到用户的技能 `scripts/` 文件夹

### Block 4 异常规则

Block 4 的 Phase A 也**必须使用 AskUserQuestion**。需要选择 Output format。

---

## References 文件映射

| 区块 | 文件 | 内容 |
|------|------|------|
| Block 0 | `references/block0-tool-selection.md` | 工具选择 + 基于模板创建技能 |
| Block 1 | `references/block1-project-explore.md` | 使用 Explore Agent 分析项目结构 |
| Block 2 | `references/block2-tool-connection.md` | MCP vs API 连接方式选择 + 执行 |
| Block 3 | `references/block3-parallel-collection.md` | subagent 并行收集 + 结果验证 |
| Block 4 | `references/block4-output-format.md` | Output format 选择（markdown、Slack、Notion） |
| Block 5 | `references/block5-finalize.md` | 最终技能完成 + 执行 + 结束 |

> 文件路径是相对于此 SKILL.md 的相对路径。
> 每个 reference 文件由 `## EXPLAIN`、`## EXECUTE`、`## QUIZ` 部分组成。

---

## Templates / Scripts 文件映射

| 文件 | 用途 |
|------|------|
| `templates/context-sync.md` | Context Sync 技能基础模板（包含 Slack、Notion、Gmail、GCal 4种示例） |
| `scripts/mcp_servers.py` | 从 GitHub 搜索 MCP 服务器 + README.md 解析 + 安装说明 |

> Gmail/Calendar 等收集脚本在 Block 2 中由 Claude 根据用户选择直接编写。

---

## 进度规则

- 一次处理一个区块
- 使用“下一步”、“跳过”、区块编号/名称导航
- Block 0 创建的技能文件将在后续区块中逐步修改
- 在用户项目的 `.claude/skills/my-context-sync/` 目录中创建技能
- 积极使用 Explore Agent 和 subagent
- 如果出现 Claude Code 相关问题，使用 claude-code-guide Agent（内置工具）回答。回答后以分步方式指导用户执行，提问时使用 AskUserQuestion。如果判断内置 Agent 回答不准确，则使用 `curl` 将官方文档保存为文件，然后使用 Read 工具仔细阅读并给出准确信息

---

## 开始

技能开始时**必须先安装最新课程**，然后选择区块。

### Step 1: 安装最新技能

输出以下命令并使用 Bash 执行：

```bash
npx skills add ai-native-camp/camp-1 --agent claude-code --yes
```

简要说明执行结果（例如：“4个技能已安装为最新版本”）。

### Step 2: 选择区块

展示以下表格，并使用 AskUserQuestion 询问从哪里开始：

| 区块 | 主题 | 内容 |
|------|------|------|
| 0 | 工具选择 | 选择要 sync 的工具 + 创建技能框架 |
| 1 | 项目探索 | 使用 Explore 探索项目结构 |
| 2 | 工具连接 | 使用 MCP 或 API 连接工具 |
| 3 | 收集执行 & 验证 | 并行收集 + 验证结果 |
| 4 | Output 设置 | 选择输出格式 + 修改技能 |
| 5 | 完成 + 执行 | 运行最终技能 + 结束 |

```json
AskUserQuestion({
  "questions": [{
    "question": "Day 2: 나만의 Context Sync 스킬 만들기\n\n어디서부터 시작할까요?",
    "header": "开始区块",
    "options": [
      {"label": "从头开始 (Block 0)", "description": "选择要 sync 的工具 + 创建技能框架"},
      {"label": "工具连接 (Block 2)", "description": "已选择工具，从 MCP/API 连接开始"},
      {"label": "收集执行 & 验证 (Block 3)", "description": "连接完成，从收集开始"},
      {"label": "Output 设置 (Block 4)", "description": "收集完成，从输出格式开始"}
    ],
    "multiSelect": false
  }]
})
```

> 选择开始区块后 → 进入该区块的 Phase A 开始执行。
