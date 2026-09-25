# 使用 GitNexus 进行调试

## 何时使用

- "这个函数为什么失败？"
- "追踪这个错误来自哪里"
- "谁调用了这个方法？"
- "这个端点返回 500"
- 调查错误、异常行为或意外情况

## 首先绑定仓库

在错误的仓库中追踪根本原因是错误的根本原因。

在首次调用工具之前调用 `list_repos {}`。对于单个索引的仓库，直接使用以下示例。对于多个仓库，每个调用都传递 `repo`：省略 `repo` 通常会报错，但在配置了默认值的 MCP 策略下会静默解析为默认值。如果你无法确定哪个仓库是目标，请停止并询问。这对于 `cypher` 最重要，因为其语句本身不包含任何关于它针对哪个数据库的内部提示。

`list_repos` 是分页的，所以在得出仓库不存在的结论之前，使用 `offset: pagination.nextOffset` 分页，直到 `hasMore` 为假。

陈旧的索引描述的是你错误之前的代码，所以在信任跟踪之前刷新它，并在诊断中说明仓库和索引的新鲜度。

## 工作流程

```
0. list_repos {}                                          → 绑定仓库
1. query({search_query: "<错误或症状>"})            → 查找相关的执行流程
2. context({name: "<可疑对象>"})                    → 查看调用者/被调用者/进程
3. READ gitnexus://repo/{name}/process/{name}                → 追踪执行流程
4. cypher({statement: "MATCH path..."})                 → 如需自定义跟踪
```

> 如果显示"索引陈旧" → 在终端中运行 `node .gitnexus/run.cjs analyze`。
> 热工具 `staleness` 指出哪个索引回答了 (`branch`/`lastCommit`) 以及它有多新 (`status`)。仅对 `behind` 或 `diverged` 重新分析 — `current` 是身份，`unknown` 是不可测量的。

## 检查清单

```
- [ ] list_repos {} — 绑定仓库；当索引 >1 时显式指定仓库，如果模糊则询问
- [ ] 理解症状（错误消息、意外行为）
- [ ] 查询错误文本或相关代码
- [ ] 从返回的进程中识别可疑函数
- [ ] context 查看调用者和被调用者
- [ ] 通过进程资源（如适用）追踪执行流程
- [ ] cypher 进行自定义调用链跟踪（如需）
- [ ] 阅读源文件以确认根本原因
- [ ] 在诊断中说明仓库和索引的新鲜度
```

## 调试模式

| 症状              | GitNexus 方法                                          |
| -------------------- | ---------------------------------------------------------- |
| 错误消息        | `query` 查询错误文本 → `context` 在抛出位置 |
| 错误的返回值   | `context` 在函数上 → 追踪被调用者以查找数据流    |
| 间歇性失败      | `context` → 查找外部调用、异步依赖            |
| 性能问题        | `context` → 查找有多个调用者（热点路径）的符号     |
| 最近回归        | `detect_changes` 查看你的更改影响了什么 — 传递 `worktree` 用于关联工作树 |
| "A 如何到达 B?" | `trace` 在两个符号之间 — 单次调用中的最短调用链 |

## 工具

**query** — 查找与错误相关的代码：

```
query({search_query: "payment validation error", repo: "my-app"})
→ 进程：CheckoutFlow, ErrorHandling
→ 符号：validatePayment, handlePaymentError, PaymentException
```

**context** — 可疑对象的全局上下文：

```
context({name: "validatePayment", repo: "my-app"})
→ 入站调用：processCheckout, webhookHandler
→ 出站调用：verifyCard, fetchRates (外部 API!)
→ 进程：CheckoutFlow (步骤 3/7)
```

**cypher** — 自定义调用链跟踪。与语句一起传递 `repo`；Cypher 文本本身不命名任何仓库，因此没有它结果无法归属：

```cypher
MATCH path = (a)-[:CodeRelation {type: 'CALLS'}*1..2]->(b:Function {name: "validatePayment"})
RETURN [n IN nodes(path) | n.name] AS chain
```

**trace** — 两个符号之间的最短调用链（"A 如何到达 B？"），一次调用代替链式 `context` 跳转：

```
trace({ from: "processCheckout", to: "fetchRates", repo: "my-app" })
→ 状态：ok, 跳转次数：3
→ 跳转：processCheckout → validatePayment → verifyCard → fetchRates
→ 边缘：CALLS (1.0), CALLS (0.95), CALLS (1.0)
```

如果没有路径，`trace` 报告最远的可达节点 — 恰好是链断裂的位置（动态分发、反射或外部边界）。

## 示例："支付端点间歇性返回 500"

```
0. list_repos {}
   → 总数：2 (my-app, billing-api) — 每次调用显式绑定 my-app

1. query({search_query: "payment error handling", repo: "my-app"})
   → 进程：CheckoutFlow, ErrorHandling
   → 符号：validatePayment, handlePaymentError

2. context({name: "validatePayment", repo: "my-app"})
   → 出站调用：verifyCard, fetchRates (外部 API!)

3. READ gitnexus://repo/my-app/process/CheckoutFlow
   → 步骤 3：validatePayment → 调用 fetchRates (外部)

4. 根本原因：fetchRates 调用外部 API 但没有适当的超时
   仓库：my-app  索引：当前
```

对于单个索引的仓库，步骤 0 返回 `total: 1`，并且上述每个调用中的 `repo` 参数会消失。
