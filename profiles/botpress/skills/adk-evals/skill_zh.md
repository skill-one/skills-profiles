# ADK 评估技能

## 什么是评估？

评估是用于 ADK 代理的自动化对话测试。每个评估定义一个场景——一系列用户消息或事件——并断言机器人应该做什么：它说什么、调用哪些工具、状态如何变化、运行哪些工作流等。

评估针对实时开发机器人（`adk dev`）运行，因此它们测试的是完整的技术栈——而不是模拟。

## 何时使用此技能

当开发者询问以下内容时使用此技能：

- **编写评估**——文件格式、断言、回合类型、设置
- **运行评估**——CLI 命令、过滤、输出解释
- **测试特定原语**——如何测试操作、工具、工作流、对话、状态
- **测试循环**——编写 → 运行 → 检查跟踪 → 迭代
- **CI 集成**——退出代码、`--format json` 标志、标记策略
- **评估配置**——空闲超时、判断通过阈值、判断模型

或者当你正在开发 ADK 机器人并需要编写相当于单元测试/端到端测试的内容时。

**触发问题：**

- "我该如何编写评估？"
- "我该如何测试我的工作流？"
- "我该如何断言工具被使用并带有特定参数？"
- "我的评估失败了，我该如何调试它？"
- "我该如何测试机器人保持沉默？"
- "我该如何在 CI 中运行评估？"
- "我该如何在评估之前初始化状态？"
- "我该如何在评估中触发工作流？"

## 可用的文档

| 文件                             | 内容                                                                                                      |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `references/eval-format.md`      | 完整文件格式——所有字段、回合类型、断言类别、匹配运算符、设置、结果、选项 |
| `references/testing-workflow.md` | 运行评估、解释输出、使用跟踪、编写 → 测试 → 迭代循环、CI 集成             |
| `references/test-patterns.md`    | 针对 actions、tools、workflows、conversations 和状态的每个原语模式        |

## 如何回答

1. **编写评估** → 阅读 `eval-format.md` 了解结构和断言
2. **运行评估** → 阅读 `testing-workflow.md` 了解 CLI 命令和输出
3. **测试特定原语** → 阅读 `test-patterns.md` 了解相关部分
4. **调试失败** → 结合 `testing-workflow.md`（检查跟踪）+ `eval-format.md`（检查断言语法）

---

## 快速参考

### 评估文件结构

```typescript
import { Eval } from '@botpress/evals'

export default new Eval({
  name: 'greeting',
  type: 'regression',
  tags: ['basic'],

  setup: {
    state: { bot: { welcomeSent: false } },
    workflow: { trigger: 'onboarding', input: { userId: 'test-1' } },
  },

  conversation: [
    {
      user: 'Hi!',
      assert: {
        response: [{ not_contains: 'error' }, { llm_judge: 'Response is friendly and offers to help' }],
        tools: [{ not_called: 'createTicket' }],
        state: [{ path: 'conversation.greeted', equals: true }],
      },
    },
  ],

  outcome: {
    state: [{ path: 'conversation.greeted', equals: true }],
  },

  options: {
    idleTimeout: 60000,
    judgePassThreshold: 4,
  },
})
```

### 回合类型

| 回合                  | 何时使用                                    |
| --------------------- | ---------------------------------------------- |
| `user: 'message'`     | 标准用户消息                              |
| `event: { payload }`  | 推送自定义事件（作为 `chat:custom` 到达） |
| `expectSilence: true` | 断言机器人不回复                          |

### 断言类别

| 类别   | 它检查的内容                                              |
| ---------- | ----------------------------------------------------------- |
| `response` | 机器人回复文本（contains、not_contains、matches、llm_judge） |
| `tools`    | 工具调用（called、not_called、call_order、params）         |
| `state`    | 机器人/用户/对话状态（equals、changed）               |
| `workflow` | 工作流执行（entered、completed）                     |
| `timing`   | 响应时间（ms）（lte、gte）                              |

### CLI 命令

```bash
adk evals                        # 运行所有评估
adk evals <name>                 # 运行单个评估
adk evals --tag <tag>            # 按标签过滤
adk evals --type regression      # 按类型过滤
adk evals --verbose              # 显示所有断言
adk evals --format json          # JSON 输出用于 CI

adk evals runs                   # 列出最近的运行
adk evals runs --latest          # 最新的运行
adk evals runs --latest -v       # 带完整详细信息
```

---

## 关键模式

✅ **每个回合都需要 `user` 或 `event`**

```typescript
// 正确
{ user: 'hello', expectSilence: true }
{ event: { payload: { kind: 'payment.failed' } }, expectSilence: true }
```

❌ **仅 `expectSilence` 不是有效的回合**

```typescript
// 错误——缺少 user 或 event
{
  expectSilence: true
}
```

---

✅ **断言工具参数以验证正确提取**

```typescript
// 正确——验证 LLM 提取了正确的值
{ called: 'createTicket', params: { priority: { equals: 'high' } } }
```

❌ **仅断言工具被调用**

```typescript
// 不完整——不验证参数是否正确
{
  called: 'createTicket'
}
```

---

✅ **使用 `outcome` 进行对话后状态和工作流断言**

```typescript
// 正确——在所有回合后检查最终状态
outcome: {
  state: [{ path: 'conversation.resolved', equals: true }],
  workflow: [{ name: 'ticketFlow', completed: true }],
}
```

---

✅ **初始化状态以测试条件行为，而无需运行设置回合**

```typescript
// 正确——从已知状态开始
setup: {
  state: {
    user: { plan: 'pro' },
    conversation: { phase: 'support' },
  },
}
```

❌ **使用对话回合来设置状态（慢且易碎）**

```typescript
// 错误——依赖于机器人正确处理设置回合
conversation: [
  { user: 'I am on the pro plan' }, // 期望机器人设置 user.plan
  { user: 'I need help with billing' }, // 实际测试回合
]
```

---

## 示例问题

**编写评估：**

- "编写一个评估来测试我的 createTicket 工具是否以正确的优先级被调用"
- "我该如何断言机器人在内事件后保持沉默？"
- "我该如何测试一个多回合对话，其中上下文被保留？"

**运行评估：**

- "我该如何仅运行回归评估？"
- "我该如何看到哪些断言失败以及为什么？"
- "我该如何将评估集成到 GitHub Actions？"

**调试：**

- "我的评估说工具没有被调用，但我认为它被调用了——我该如何检查？"
- "我该如何检查评估期间机器人实际做了什么？"

**针对原语：**

- "我该如何测试使用 step.sleep() 的工作流？"
- "我该如何测试状态是否从初始化值发生了变化？"

---

## 响应格式

**根据问题的深度进行匹配。**

### 简单问题（"有哪些可用的断言？", "我该如何运行评估？"）

直接回答——显示相关的表格或 CLI 命令。不要为信息性问题生成完整的评估文件。

### 编写评估

1. 显示完整的 `new Eval({})` 调用，带有现实的字段值
2. 包括导入（`import { Eval } from '@botpress/evals'`）
3. 简要解释非显式的断言——如果断言是自解释的，则跳过
4. 建议运行它的 CLI 命令：`adk evals <name>`

### 调试失败的评估

1. 询问或显示失败的断言（`expected` / `actual` 差异）
2. 建议在开发控制台中打开跟踪以查看机器人做了什么
3. 确定问题是在评估断言还是机器人的行为中
