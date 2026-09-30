---
name: session-analyzer
description: 当用户要求“分析会话”、“세션 분석”、“评估技能执行”、“스킬 실행 검증”、“检查会话日志”、“로그 분석”，提供带技能路径的会话ID，或希望验证过去会话中技能是否正确执行时，应使用此技能。对Claude Code会话进行事后分析，以验证技能/代理/钩子的行为是否符合SKILL.md规范。
---

# 会话分析技能

用于验证 Claude 代码会话行为是否符合 SKILL.md 规范的后处理分析工具。

## 目的

分析已完成的会话以验证：
1. **预期行为与实际行为** - 技能是否遵循 SKILL.md 工作流？
2. **组件调用** - 是否正确调用了 SubAgents、Hooks 和 Tools？
3. **工件** - 是否创建了/删除了预期的文件？
4. **错误检测** - 是否存在意外的错误或偏差？

---

## 输入要求

| 参数 | 必填 | 描述 |
|------|------|------|
| `sessionId` | 是 | 要分析的会话的 UUID |
| `targetSkill` | 是 | 用于验证的 SKILL.md 路径 |
| `additionalRequirements` | 否 | 额外的验证标准 |

---

## 第一阶段：定位会话文件

### 第 1.1 步：查找会话文件

会话文件位于 `~/.claude/`：

```bash
# 主会话日志
~/.claude/projects/-{encoded-cwd}/{sessionId}.jsonl

# 调试日志（详细）
~/.claude/debug/{sessionId}.txt

# 代理文本记录（如果使用了子代理）
~/.claude/projects/-{encoded-cwd}/agent-{agentId}.jsonl
```

使用脚本定位文件：
```bash
${baseDir}/scripts/find-session-files.sh {sessionId}
```

### 第 1.2 步：验证文件是否存在

在继续之前检查所有必需文件是否存在。如果缺少调试日志，分析将受限。

---

## 第二阶段：解析目标 SKILL.md

### 第 2.1 步：提取预期组件

读取目标 SKILL.md 并识别：

**从 YAML 前置部分：**
- `hooks.PreToolUse` - 预期的 PreToolUse hooks 和匹配器
- `hooks.PostToolUse` - 预期的 PostToolUse hooks
- `hooks.Stop` - 预期的 Stop hooks
- `hooks.SubagentStop` - 预期的 SubagentStop hooks
- `allowed-tools` - 技能允许使用的 Tools

**从 Markdown 正文：**
- 提及的子代理（`Task(subagent_type="...")`）
- 调用的技能（`Skill("...")`）
- 创建的工件（`.dev-flow/drafts/`、`.dev-flow/plans/` 等）
- 工作流步骤和条件

### 第 2.2 步：构建预期行为清单

从 SKILL.md 分析创建清单：

```markdown
## 预期行为

### 子代理
- [ ] 调用了 Explore 代理（并行、run_in_background）
- [ ] gap-analyzer 在计划生成前被调用
- [ ] reviewer 在计划创建后被调用

### Hooks
- [ ] PreToolUse[Edit|Write] 触发了 plan-guard.sh
- [ ] Stop hook 验证了 reviewer 的批准

### 工件
- [ ] 在 .dev-flow/drafts/{name}.md 创建了草稿文件
- [ ] 在 .dev-flow/plans/{name}.md 创建了计划文件
- [ ] OKAY 后删除了草稿文件

### 工作流
- [ ] 计划生成前的访谈模式
- [ ] 用户显式请求触发计划生成
- [ ] reviewer REJECT 导致修订循环
```

---

## 第三阶段：分析调试日志

调试日志（`~/.claude/debug/{sessionId}.txt`）包含详细的执行跟踪。

### 第 3.1 步：提取子代理调用

搜索模式：
```
SubagentStart with query: {agent-name}
SubagentStop with query: {agent-id}
```

使用脚本：
```bash
${baseDir}/scripts/extract-subagent-calls.sh {debug-log-path}
```

### 第 3.2 步：提取 Hook 事件

搜索模式：
```
Getting matching hook commands for {HookEvent} with query: {tool-name}
Matched {N} unique hooks for query "{query}"
Hooks: Processing prompt hook with prompt: {prompt}
Hooks: Prompt hook condition was met/not met
permissionDecision: allow/deny
```

使用脚本：
```bash
${baseDir}/scripts/extract-hook-events.sh {debug-log-path}
```

### 第 3.3 步：提取 Tool 调用

搜索模式：
```
executePreToolHooks called for tool: {tool-name}
File {path} written atomically
```

### 第 3.4 步：提取 Hook 结果

对于基于提示的 hooks，找到模型响应：
```
Hooks: Model response: {
  "ok": true/false,
  "reason": "..."
}
```

---

## 第四阶段：验证工件

### 第 4.1 步：检查文件创建

对于每个预期的工件：
1. 在调试日志中搜索 `FileHistory: Tracked file modification for {path}`
2. 搜索 `File {path} written atomically`
3. 验证当前文件系统状态

### 第 4.2 步：检查文件删除

对于应该被删除的文件：
1. 在 Bash 调用中搜索 `rm` 命令
2. 验证文件不再存在于文件系统中

---

## 第五阶段：比较预期与实际

### 第 5.1 步：构建比较表

```markdown
| 组件 | 预期 | 实际 | 状态 |
|------|------|------|------|
| Explore 代理 | 2 个并行调用 | 09:39:26 的 2 次调用 | ✅ |
| gap-analyzer | 在计划生成前调用 | 09:43:08 调用 | ✅ |
| reviewer | 在计划后调用 | 2 次调用（REJECT→OKAY） | ✅ |
| PreToolUse hook | Edit\|Write 匹配器 | 触发了 Write | ✅ |
| Stop hook | 验证批准 | 返回 ok:true | ✅ |
| 草稿文件 | 创建后删除 | 创建→删除 | ✅ |
| 计划文件 | 创建 | 存在（10KB） | ✅ |
```

### 第 5.2 步：识别偏差

标记任何不匹配：
- 缺失的组件调用
- 操作顺序错误
- Hook 失败
- 缺失的工件
- 意外的错误

---

## 第六阶段：生成报告

### 报告模板

```markdown
# 会话分析报告

## 会话信息
- **会话 ID**: {sessionId}
- **目标技能**: {skillPath}
- **分析日期**: {date}

---

## 1. 预期行为（来自 SKILL.md）

[预期工作流的摘要]

---

## 2. 技能/子代理/Hook 验证

### 子代理
| 子代理 | 预期 | 实际 | 时间 | 结果 |
|------|------|------|------|------|
| ... | ... | ... | ... | ✅/❌ |

### Hooks
| Hook | 匹配器 | 触发 | 结果 |
|------|--------|------|------|
| ... | ... | ... | ✅/❌ |

---

## 3. 工件验证

| 工件 | 路径 | 预期状态 | 实际状态 |
|------|------|----------|----------|
| ... | ... | ... | ✅/❌ |

---

## 4. 问题/错误

| 严重性 | 描述 | 位置 |
|------|------|------|
| ... | ... | ... |

---

## 5. 总体结果

**结论**: ✅ 通过 / ❌ 失败

**摘要**: [1-2 句话的摘要]
```

---

## 脚本参考

| 脚本 | 目的 |
|------|------|
| `find-session-files.sh` | 定位会话的所有文件 |
| `extract-subagent-calls.sh` | 从调试日志解析子代理调用 |
| `extract-hook-events.sh` | 从调试日志解析 Hook 事件 |

---

## 使用示例

```
用户: "分析会话 3cc71c9f-d27a-4233-9dbc-c4f07ea6ec5b 对比 .claude/skills/specify/SKILL.md"

1. 定位会话文件
2. 解析 SKILL.md → 预期: Explore、gap-analyzer、reviewer、hooks
3. 分析调试日志 → 提取实际调用
4. 验证工件 → 检查 .dev-flow/
5. 比较 → 构建验证表
6. 生成报告 → 通过/失败及详情
```

---

## 额外资源

### 参考文件
- **`references/analysis-patterns.md`** - 用于日志分析的详细 grep 模式
- **`references/common-issues.md`** - 已知问题和故障排除

### 脚本
- **`scripts/find-session-files.sh`** - 会话文件定位器
- **`scripts/extract-subagent-calls.sh`** - 子代理调用提取器
- **`scripts/extract-hook-events.sh`** - Hook 事件提取器
