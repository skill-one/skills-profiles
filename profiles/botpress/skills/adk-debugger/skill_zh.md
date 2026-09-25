# ADK Debugger 技能

## 什么是 ADK 调试？

每个 ADK 代理都会将其行为记录为跟踪记录和日志——每一步对话、工具调用、LLM 推理步骤和错误。这些是理解您的代理做了什么以及为什么的真相来源。

ADK CLI 提供了您需要的调试工具。大多数诊断命令支持 `--format json`；用于程序化输出。例外是 `adk dev`，它没有 `--format` 标志，并使用 `adk dev --non-interactive` 用于结构化的 NDJSON 输出。

## 何时使用此技能

当开发者询问以下问题时使用此技能：

- **机器人无法工作**——无响应、错误响应、意外行为
- **工具问题**——调用错误工具、工具错误、幻觉参数
- **工作流问题**——卡住的工作流、步骤未执行、状态问题
- **读取跟踪记录/日志**——如何查询、过滤和解释调试输出
- **LLM 异常行为**——幻觉、拒绝、循环、提取质量差
- **构建/部署失败**——验证错误、模式不匹配
- **配置问题**——agent.json 与 agent.local.json、集成设置
- **修复后验证**——确认修复是否有效、编写回归评估

**触发问题：**

- "我的机器人无响应"
- "调用了错误的工具"
- "我的工作流卡住了"
- "我如何读取跟踪记录？"
- "我如何检查日志？"
- "LLM 在幻觉"
- "在我上次更改后出了问题"
- "我的部署失败了"
- "`adk check` 发现了错误"
- "总结这个跟踪记录"
- "跟踪记录 X 中发生了什么？"
- "给我这个对话步骤的概述"
- "为什么这个跟踪记录中机器人做了 X？"
- "向我展示发生了什么"
- "我如何调试这个？"
- "总结这个对话"
- "解释对话 X 中发生了什么"
- "为什么机器人那样回复？"
- "向我展示这个对话"
- "这个对话中出了什么问题？"

## 可用的文档

| 文件                                  | 内容                                                                                                                                     |
| ------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `references/traces-and-logs.md`       | CLI 调试工具、日志查询、跟踪记录结构、跨度类型、`onTrace` 钩子、使用 `adk chat` 重现 | |
| `references/common-failures.md`       | 运行时失败模式——验证、机器人无响应、工具错误、工作流卡住、集成失败、构建错误、配置混淆 | |
| `references/llm-debugging.md`         | LLM 行为问题——错误工具、幻觉参数、拒绝、令牌限制、循环、读取模型推理             | |
| `references/debug-workflow.md`        | 系统化的 8 步调试循环：验证 → 重现 → 日志 → 跟踪记录 → 分类 → 修复 → 验证 → 预防   | |
| `references/trace-summarization.md`   | 如何获取、遍历和总结跟踪记录为自由形式的自然语言叙述——根据上下文调整深度         | |
| `references/conversation-analysis.md` | 如何总结和解释完整对话——列出对话、时间线分析、与跟踪记录关联、常见模式         | |

## 如何回答

1. **"我如何读取跟踪记录/日志？"** → 阅读 `traces-and-logs.md` 获取 CLI 命令和跟踪记录结构
2. **出了问题，已知模式** → 阅读 `common-failures.md` 获取匹配的失败模式
3. **LLM 异常行为** → 阅读 `llm-debugging.md` 获取匹配的行为问题
4. **需要系统化调查** → 阅读 `debug-workflow.md` 并遵循 8 步循环
5. **"总结这个跟踪记录" / "发生了什么？"** → 阅读 `trace-summarization.md` 了解如何获取、遍历和叙述跟踪记录
6. **"总结这个对话" / "解释发生了什么"** → 阅读 `conversation-analysis.md` 获取多轮对话总结和解释
7. **修复后，需要防止回归** → 指向 `adk-evals` 技能编写评估

---

## 快速参考

### 调试循环

```
症状 → 验证 (adk check) → 重现 (adk chat) → 日志 (adk logs) → 跟踪记录 (adk traces) → 根本原因 → 修复 → 验证
```

### CLI 命令（优先结构化输出）

```bash
adk check --format json                         # 离线验证
adk logs error --format json                     # 最近错误
adk logs --follow --format json                  # 实时流
adk traces --format json                         # 最近跟踪记录
adk traces conversation=<id> --format json       # 特定对话
adk chat --single "msg" --format json            # 测试消息
adk dev --non-interactive                        # 结构化的 NDJSON 开发输出（无 TUI）
adk conversations --format json                  # 列出最近对话
adk conversations show <id> --format json        # 对话时间线
adk conversations show <id> --include-llm --format json  # 带有 LLM 推理的时间线
```

### 跨度类型

| 类型                       | 它显示的内容                                        |
| -------------------------- | ---------------------------------------------------- |
| `think`                    | LLM 推理——它为什么选择了一个操作                     |
| `tool_call`                | 工具调用——名称、输入、输出、成功/错误                 |
| `code_execution_exception` | 运行时错误——消息和堆栈跟踪                          |
| `end`                      | 对话步骤完成                                      |

---

## 前置条件检查

在调试之前，请验证：

- [ ] **项目有效吗？** 运行 `adk check --format json` — 首先修复任何报告的问题
- [ ] **开发服务器在运行吗？** `adk dev`（或 `adk dev --non-interactive` 用于结构化的 NDJSON 输出）
- [ ] **机器人已链接？** `agent.json` 存在，包含 `botId` 和 `workspaceId`（由 `adk link` 创建）
- [ ] **已创建开发机器人？** `agent.local.json` 包含 `devId`（由第一个 `adk dev` 运行自动设置）
- [ ] **集成已配置？** 检查本地主机:3001 的开发控制台中的未配置集成

---

## 关键模式

✅ **在调试运行时问题之前运行 `adk check`**

```bash
# 正确——首先离线捕获配置/模式问题
adk check --format json
# 然后调试运行时问题
```

❌ **跳过离线验证**

```bash
# 错误——直接跳到运行时调试会浪费时间在配置问题上
adk traces --format json  # 可能是在追逐配置问题
```

---

✅ **在所有 CLI 命令上使用 `--format json`**

```bash
# 正确——结构化输出用于可靠解析
adk logs error --format json
adk traces --format json
adk chat --single "test" --format json
```

❌ **解析人类可读输出**

```bash
# 错误——人类可读格式用于显示，不是解析
adk logs error
adk traces
```

---

✅ **使用 `adk logs error` 过滤错误**

```bash
# 正确——专注的错误扫描
adk logs error --format json
adk logs warning since=1h --format json
```

❌ **滚动浏览所有输出**

```bash
# 错误——太多噪音，容易错过实际错误
adk logs --format json  # 50 条所有内容
```

---

✅ **使用 `onTrace` 钩子进行程序化监控**

```typescript
// 正确——结构化、自动化的跟踪记录分析
hooks: {
  onTrace: ({ trace }) => {
    if (trace.type === 'tool_call' && !trace.success) {
      console.error(`[TOOL ERROR] ${trace.tool_name}`, trace.error)
    }
  }
}
```

❌ **只检查控制台输出**

```typescript
// 错误——处理程序中的 console.log 忽略结构化的跟踪记录数据
handler: async (input) => {
  console.log('tool called') // 对调试没有用
}
```

---

✅ **修复后编写回归评估**

```typescript
// 正确——防止错误再次出现
export default new Eval({
  name: 'fix-order-lookup',
  type: 'regression',
  conversation: [{ user: '查找订单 123', assert: { tools: [{ called: 'lookupOrder' }] } }],
})
```

❌ **修复后继续**

```
// 错误——相同的错误会再次出现，您会再次调试它
```

---

## 示例问题

**基础：**

- "我的机器人无响应——我如何找出原因？"
- "我如何检查我的 ADK 项目的错误？"
- "agent.json 和 agent.local.json 之间的区别是什么？"

**中级：**

- "机器人调用了 createTicket 而不是 lookupTicket——我如何修复这个？"
- "我的工作流开始但第二步从未运行"
- "我如何看到 LLM 在做决定时在想什么？"
- "集成操作因认证错误而失败"

**高级：**

- "我如何设置 onTrace 钩子以进行自动化的错误检测？"
- "模型在相同的工具调用上循环——我如何添加一个防护措施？"
- "我如何使用时间度量监控工具调用性能？"
- "我如何系统地调试多步骤工作流失败？"

---

## 响应格式

**根据问题的深度进行匹配。**

### 简单问题（"我如何检查日志？"、"跟踪记录跨度是什么？"）

直接回答——一句话 + CLI 命令或概念。不要为信息性问题运行完整的调试循环。

### 主动调试（"我的机器人坏了"："X 不工作"）

遵循完整循环：

1. **检查前置条件**——验证开发服务器、配置文件、项目验证
2. **首先使用 `adk check --format json`**——排除离线问题
3. **重现**——使用 `adk chat --single "msg" --format json` 创建干净的再现
4. **读取证据**——`adk logs error --format json` 快速扫描，`adk traces --format json` 详细信息
5. **确定根本原因**——指向特定的跨度、日志条目或配置问题
6. **建议有针对性的修复**——参考相应的失败模式文档
7. **验证**——重新运行再现，确认干净输出
8. **编写回归评估**——加载 `adk-evals` 技能并自动生成评估文件
