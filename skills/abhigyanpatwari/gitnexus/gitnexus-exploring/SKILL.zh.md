---
name: gitnexus-exploring
description: 当用户询问代码如何工作、想要理解架构、追踪执行流程或探索代码库中不熟悉的部分时使用。例如：“X是如何工作的？”，“什么调用了这个函数？”，“给我展示认证流程”。
---

# 使用 GitNexus 探索代码库

## 使用场景

- "认证是如何工作的？"
- "项目结构是怎样的？"
- "展示主要组件"
- "数据库逻辑在哪里？"
- 理解未知的代码

## 首先绑定仓库

第一步会发现已索引的内容；之后的每次调用都必须指明是其中的哪一个。对于单个已索引的仓库，直接使用以下示例即可。对于多个仓库，每次调用时都需要传递 `repo` 参数：省略 `repo` 通常会导致错误，但在配置了默认值的 MCP 策略下会静默地解析为默认值。如果你无法确定指的是哪个仓库，请停止并询问。在解释时，请报告绑定的仓库和索引的新鲜度。

`list_repos` 是分页的，所以在得出仓库不存在之前，需要使用 `offset: pagination.nextOffset` 分页，直到 `hasMore` 为 `false`。

## 工作流程

```
1. list_repos {} 或 READ gitnexus://repos                          → 发现已索引的仓库
2. READ gitnexus://repo/{name}/context             → 代码库概览，检查是否过时
3. query({search_query: "<你想理解的内容>"})  → 查找相关的执行流程
4. context({name: "<符号>"})            → 深入特定符号
5. READ gitnexus://repo/{name}/process/{name}      → 追踪完整的执行流程
```

> 如果步骤 2 显示 "索引过时" → 在终端中运行 `node .gitnexus/run.cjs analyze`。
> 热工具 `staleness` 会命名回答了哪个索引 (`branch`/`lastCommit`) 以及它的新鲜度 (`status`)。仅对 `behind` 或 `diverged` 进行重新分析 — `current` 是身份，`unknown` 是不可测量的。

## 检查清单

```
- [ ] list_repos {} — 绑定仓库；多个已索引时显式指定仓库，如果模糊则询问
- [ ] READ gitnexus://repo/{name}/context
- [ ] 查询你想理解的概念
- [ ] 审查返回的流程（执行流程）
- [ ] 对调用者/被调用者的关键符号进行 context
- [ ] READ 流程资源以获取完整的执行跟踪
- [ ] 阅读源文件以获取实现细节
- [ ] 在解释时说明仓库和索引的新鲜度
```

## 资源

| 资源                                | 你能获得的内容                                            |
| --------------------------------------- | ------------------------------------------------------- |
| `gitnexus://repo/{name}/context`        | 统计信息，过时警告 (~150 个 token)                  |
| `gitnexus://repo/{name}/clusters`       | 所有功能区域及其凝聚力分数 (~300 个 token)              |
| `gitnexus://repo/{name}/cluster/{name}` | 区域成员及其文件路径 (~500 个 token)              |
| `gitnexus://repo/{name}/process/{name}` | 步步执行跟踪 (~200 个 token)              |

## 工具

**query** — 查找与某个概念相关的执行流程：

```
query({search_query: "支付处理", repo: "my-app"})
→ 流程：CheckoutFlow, RefundFlow, WebhookHandler
→ 按流程分组符号及其文件位置
```

**context** — 符号的 360 度视图：

```
context({name: "validateUser", repo: "my-app"})
→ 入站调用：loginHandler, apiMiddleware
→ 出站调用：checkToken, getUserById
→ 流程：LoginFlow (步骤 2/5), TokenRefresh (步骤 1/3)
```

`repo` 在索引多个仓库时是必需的，对于单个仓库可以省略。

## 示例："支付处理是如何工作的？"

```
1. list_repos {}                             → 总计：1 (my-app) — 绑定它
   READ gitnexus://repo/my-app/context       → 918 个符号，45 个流程
2. query({search_query: "支付处理"})
   → CheckoutFlow：processPayment → validateCard → chargeStripe
   → RefundFlow：initiateRefund → calculateRefund → processRefund
3. context({name: "processPayment"})
   → 入站：checkoutHandler, webhookHandler
   → 出站：validateCard, chargeStripe, saveTransaction
4. 阅读 src/payments/processor.ts 以获取实现细节
5. 回答，注意：仓库 my-app，索引当前
```

如果步骤 1 返回了两个仓库，上述每次调用都会携带 `repo: "my-app"`。
