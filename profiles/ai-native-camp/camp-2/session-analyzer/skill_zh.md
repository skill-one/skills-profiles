# 会话分析技能

用于验证Claude Code会话行为是否符合SKILL.md规范的后期分析工具。

## 目的

分析已完成的会话以验证：
1. **预期行为与实际行为** - 技能是否遵循SKILL.md工作流？
2. **组件调用** - 是否正确调用了SubAgents、Hooks和Tools？
3. **工件** - 是否创建了/删除了预期的文件？
4. **错误检测** - 是否存在意外错误或偏差？

---

## 输入要求

| 参数 | 必填 | 描述 |
|------|------|------|
| `sessionId` | 是 | 要分析的会话的UUID |
| `targetSkill` | 是 | 用于验证的SKILL.md路径 |
| `additionalRequirements` | 否 | 额外的验证标准 |

---

## 第一阶段：定位会话文件

### 第1.1步：查找会话文件

会话文件位于`~/.claude/`：

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

### 第1.2步：验证文件是否存在

在继续之前检查所有必需文件是否存在。如果调试日志缺失，分析将受限。

---

## 第二阶段：解析目标SKILL.md

### 第2.1步：提取预期组件

读取目标SKILL.md并识别：

**从YAML前导部分：**
- `hooks.PreToolUse` - 预期的PreToolUse钩子和匹配器
- `hooks.PostToolUse` - 预期的PostToolUse钩子
- `hooks.Stop` - 预期的Stop钩子
- `hooks.SubagentStop` - 预期的SubagentStop钩子
- `allowed-tools` - 技能允许使用的工具

**从Markdown正文：**
- 提及的子代理（`Task(subagent_type="...")`）
- 调用的技能（`Skill("...")`）
- 创建的工件（`.dev-flow/drafts/`、`.dev-flow/plans/`等）
- 工作流步骤和条件

### 第2.2步：构建预期行为清单

从SKILL.md分析创建清单：

```markdown
## 预期行为

### 子代理
- [ ] 调用了探索代理（并行、run_in_background）
- [ ] gap-analyzer在计划生成前被调用
- [ ] reviewer在计划创建后被调用

### 钩子
- [ ] PreToolUse[Edit|Write]触发plan-guard.sh
- [ ] Stop钩子验证reviewer批准

### 工件
- [ ] 在 .dev-flow/drafts/{name}.md 创建草稿文件
- [ ] 在 .dev-flow/plans/{name}.md 创建计划文件
- [ ] OKAY后删除草稿文件

### 工作流
- [ ] 计划生成前的访谈模式
- [ ] 用户显式请求触发计划生成
- [ ] Reviewer REJECT导致修订循环
```

---

## 第三阶段：分析调试日志

调试日志（`~/.claude/debug/{sessionId}.txt`）包含详细的执行跟踪。

### 第3.1步：提取子代理调用

搜索模式：
```
SubagentStart with query: {agent-name}
SubagentStop with query: {agent-id}
```

使用脚本：
```bash
${baseDir}/scripts/extract-subagent-calls.sh {debug-log-path}
```

### 第3.2步：提取钩子事件

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

### 第3.3步：提取工具调用

搜索模式：
```
executePreToolHooks called for tool: {tool-name}
File {path} written atomically
```

### 第3.4步：提取钩子结果

对于基于提示的钩子，找到模型响应：
```
Hooks: Model response: {
  "ok": true/false,
  "reason": "..."
}
```

---

## 第四阶段：验证工件

### 第4.1步：检查文件创建

对于每个预期的工件：
1. 在调试日志中搜索 `FileHistory: Tracked file modification for {path}`
2. 搜索 `File {path} written atomically`
3. 验证当前文件系统状态

### 第4.2步：检查文件删除

对于应该被删除的文件：
1. 在Bash调用中搜索 `rm` 命令
2. 验证文件不再存在于文件系统中

---

## 第五阶段：比较预期与实际

### 第5.1步：构建比较表

```markdown
| 组件 | 预期 | 实际 | 状态 |
|------|------|------|------|
| 探索代理 | 2个并行调用 | 2次调用于09:39:26 | ✅ |
| gap-analyzer | 在计划生成前调用 | 调用于09:43:08 | ✅ |
| reviewer | 在计划后调用 | 2次调用（REJECT→OKAY） | ✅ |
| PreToolUse钩子 | Edit\|Write匹配器 | 触发了Write | ✅ |
| Stop钩子 | 验证批准 | 返回ok:true | ✅ |
| 草稿文件 | 创建后删除 | 创建→删除 | ✅ |
| 计划文件 | 创建 | 存在（10KB） | ✅ |
```

### 第5.2步：识别偏差

标记任何不匹配：
- 缺失组件调用
- 操作顺序错误
- 钩子失败
- 缺失工件
- 意外错误

---

## 第六阶段：生成报告

### 报告模板

```markdown
# 会话分析报告

## 会话信息
- **会话ID**: {sessionId}
- **目标技能**: {skillPath}
- **分析日期**: {date}

---

## 1. 预期行为（来自SKILL.md）

[预期工作流的摘要]

---

## 2. 技能/子代理/钩子验证

### 子代理
| 子代理 | 预期 | 实际 | 时间 | 结果 |
|------|------|------|------|------|
| ... | ... | ... | ... | ✅/❌ |

### 钩子
| 钩子 | 匹配器 | 触发 | 结果 |
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

**摘要**: [1-2句摘要]
```

---

## 脚本参考

| 脚本 | 目的 |
|------|------|
| `find-session-files.sh` | 定位会话ID的所有文件 |
| `extract-subagent-calls.sh` | 从调试日志解析子代理调用 |
| `extract-hook-events.sh` | 从调试日志解析钩子事件 |

---

## 使用示例

```
用户: "分析会话3cc71c9f-d27a-4233-9dbc-c4f07ea6ec5b相对于.claude/skills/specify/SKILL.md"

1. 定位会话文件
2. 解析SKILL.md → 预期：Explore、gap-analyzer、reviewer、钩子
3. 分析调试日志 → 提取实际调用
4. 验证工件 → 检查 .dev-flow/
5. 比较 → 构建验证表
6. 生成报告 → PASS/FAIL及详情
```

---

## 额外资源

### 参考文件
- **`references/analysis-patterns.md`** - 用于日志分析的详细grep模式
- **`references/common-issues.md`** - 已知问题和故障排除

### 脚本
- **`scripts/find-session-files.sh`** - 会话文件定位器
- **`scripts/extract-subagent-calls.sh`** - 子代理调用提取器
- **`scripts/extract-hook-events.sh`** - 钩子事件提取器
