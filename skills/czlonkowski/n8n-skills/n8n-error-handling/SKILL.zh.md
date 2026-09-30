---
name: n8n-error-handling
description: 为n8n配置错误处理，确保失败时能发出响亮、结构化且可恢复的提示。适用于构建任何webhook/API工作流、计划或非计划工作流，或任何在静默失败时会中断用户可见工作的路径——以及每当用户提及错误处理、onError、continueErrorOutput、错误分支/输出、重试、retryOnFail、响应Webhook状态码、4xx/5xx、错误触发器或"我的工作流静默失败"时。涵盖每个节点的错误输出和连接、重试/自我修复、错误触发工作流以及4xx/5xx响应形状。
---

# n8n 错误处理

默认情况下，当 n8n 节点抛出异常时，**整个工作流会停止**。对于您正在交互式运行的流程，这是没问题的——您会看到红色的节点并修复它。但对于任何非交互式运行的情况（例如 webhook API、cron 作业、队列工作程序或代理工具），这个默认设置是错误的：调用者会收到超时或空的 500 响应，操作员不会收到警报，症状是“集成突然停止工作”，没有日志，也没有线索。

这项技能的目标是使失败**响亮、结构化且可恢复**——最好是**自我修复**，这样瞬时的故障永远不会到达人类。

防止大多数静默失败的两种思路：

- **节点级错误输出**——节点的失败会路由到您控制的第二个输出，而不是终止运行。
- **工作流级错误工作流**——一个通用的捕获器，它会触发任何从节点级处理中逃逸的情况（超时、节点之间的崩溃、未连接的失败）。

---

## 实际需要这种情况的时候

| 工作流形状 | 错误处理姿态 |
|---|---|
| Webhook / API（任何带有 `Respond to Webhook` 的） | **必需。** 每个有故障的节点的错误输出都连接；状态码与原因匹配。 |
| 定时 / cron / 队列工作程序 / 代理工具（非交互式） | **必需。** 一个工作流级错误工作流，以及网络节点上的 `retryOnFail`。 |
| 您自己运行和监控的内部一次性工作流 | **可选。** 默认的 `onError: "stopWorkflow"` 是可以的——您会看到红色的节点并重新运行。 |

分界线：**如果除了您之外还有其他人看到输出**——下游系统、最终用户、值班工程师——那么必须处理失败，而不是忽略它。如果您是唯一的观察者，并且失败的成本是“我注意到并重新运行”，那么宽松一点也是可以的。

---

## 最大的静默陷阱：节点级错误输出是一个两步设置

这是 n8n 工作流“处理”错误时实际吞掉错误的最常见方式。将节点的失败路由到处理程序需要**两个**更改，只做其中一个看起来是完整的，但实际上会出问题：

1. **在节点上设置 `onError: "continueErrorOutput"`**。这是创建第二个输出的原因。如果没有它，无论您如何连接，`main[1]` 都不存在。
2. **将错误输出连接**（`connections.<node>.main[1]`，即 `sourceIndex: 1`）到一个真正的处理程序。如果没有目标，错误数据会发送到虚空。

只做其中一个而没有另一个，您会遇到一个失败模式：

| 您做了什么 | 运行时会发生什么 |
|---|---|
| `onError` 设置，错误输出**未**连接 | 错误数据被静默丢弃。下游不会触发。仪表板显示运行**成功**。最坏的情况——任何地方都没有记录错误。 |
| 错误输出连接，`onError` **未**设置 | 该插槽永远不会触发；处理程序无法访问。失败时工作流只是**停止**（默认 `stopWorkflow`）。 |
| 都完成了 | 失败会路由到 `main[1]` 到您的处理程序。 ✅ |

### 使用 `n8n_update_partial_workflow` 同时完成这两个步骤

```javascript
// 1) 启用错误输出（创建 main[1]）
{ type: "updateNode", nodeName: "HTTP Request",
  changes: { onError: "continueErrorOutput" } }

// 2) 将错误输出连接到处理程序。sourceIndex: 1 = 错误输出。
{ type: "addConnection",
  source: "HTTP Request",
  target: "Handle Error",
  sourceIndex: 1 }
```

`sourceIndex: 0` 是成功路径，`sourceIndex: 1` 是错误路径。（对于 IF 节点，别名 `branch: "true"`/`"false"` 映射到索引 0/1；对于通用有故障的节点，使用明确的 `sourceIndex: 1`。）

**然后进行验证。** 这个陷阱不会在 `validate_workflow` 中暴露——一个半连接的错误输出会验证干净。使用 `n8n_get_workflow` 拉取工作流并确认**两个**部分：

- 节点的 `onError` 是 `"continueErrorOutput"`。
- `connections["HTTP Request"].main[1]` 包含您的处理程序。

有效的 `onError` 值：

| 值 | 效果 |
|---|---|
| `"stopWorkflow"`（默认） | 错误停止整个工作流。 |
| `"continueRegularOutput"` | 错误项流出**正常**输出。罕见，通常错误——下游收到错误形状的数据并继续。 |
| `"continueErrorOutput"` | 错误项流出**单独**的错误输出 (`main[1]`)。您连接的那个。 |

完整的失败模式目录、扇入/扇出形状和验证：**NODE_ERROR_OUTPUTS.md**。

### 错误输出从未看到的失败

一个正确连接的错误输出仍然会错过整个类别的失败。在 n8n 2.38.5 上验证：

| 失败 | 使用 `continueErrorOutput` | 使用 `continueRegularOutput` |
|---|---|---|
| **`{{ }}` 内的 JS 错误**（缺少路径的 TypeError、对坏输入的 `JSON.parse`、抛出的 `Error`、JMESPath 语法错误） | 什么都不会触发；字段是 `null`，项目走**成功**路径 | 相同 |
| Python 代码节点**在运行前被拒绝**（阻塞导入、dunder 访问：`Security violations detected`）或**返回形状错误**（每个项目模式下的列表） | 节点标记为失败，但**未更改的输入项目通过成功输出离开**；`main[1]` 保持为空，执行显示成功 | 未更改的输入项目通过 |
| 代码运行时**异常**（`raise`/`throw`、`KeyError`、`NameError`） | 路由到 `main[1]` 作为 `{ error }` ✅ | `{ error }` 项在主输出上 |

所以仅错误分支无法保护这些：

- **保护数据，而不仅仅是节点。** 在一个输出很重要的转换之后，检查您生成的字段是否存在（IF/Filter on `{{ $json.total !== undefined && $json.total !== null }}`）并将缺失项发送到错误路径。
- **运行测试并读取节点状态和输出值。** Python 案例显示红色节点在绿色执行内。表达式案例只显示 `null`。
- 根本原因和修复：**n8n-expression-syntax**（调试）和 **n8n-code-python**（错误和 `onError`）。

---

## 首先自我修复：在连接错误路径之前使用 `retryOnFail`

在您构建错误分支之前，吸收瞬时的失败，这样它们永远不会到达那些分支。在**任何调用网络服务的节点**上——HTTP 请求、通讯（Gmail/Slack/Discord）、数据库、AI 节点、第三方集成——设置节点级重试：

```javascript
{ type: "updateNode", nodeName: "HTTP Request",
  changes: {
    retryOnFail: true,
    maxTries: 3,
    waitBetweenTries: 5000   // ms
  } }
```

为什么这**首先**：429 或短暂的上游中断会重试，并且通常会自行成功。错误输出仅在*真正的、持久的*失败时触发——因此您的 5xx 响应和值班警报反映了实际的问题，而不是噪音。

需要了解的引擎限制：重试会在**任何**错误时触发（没有按状态码过滤），`maxTries` 限制在 5，`waitBetweenTries` 限制在 5000ms——所以 5000 既是最大值也是一个合理的默认值。有关节点特定说明，请参阅 **n8n-node-configuration**（NODE_FAMILY_GOTCHAS.md）。

---

## API 工作流：规范形状

一个 webhook 触发的工作流，如果响应其调用者，有一条规则会覆盖所有其他规则：**没有悬挂的分支**。每条路径——成功和每个错误——都必须以一个 `Respond to Webhook` 结束，否则调用者会一直等待直到超时。

```
Webhook (responseMode: "responseNode")
  ├── 验证输入 → 处理 → Respond (200, body)
  └── (任何有故障的节点的错误输出 → sourceIndex 1)
            → Respond (4xx/5xx, 结构化的错误正文)
            → 可选：私下记录完整错误 / 通知
```

使它起作用的三件事：

1. **到一个错误响应器扇入。** 许多有故障的节点可以将它们的 `main[1]` 路由到单个 `Respond` 节点。保持图形可读。
2. **验证失败（4xx）是在*上游*检查的，而不是通过错误输出。** 缺少字段不是节点*崩溃*——这是一个预期结果，具有已知响应。使用 IF/Switch（或下面的模式验证器）分支，并直接返回 400/401/403/404。错误输出用于*意外的*失败（5xx）。
3. **`responseCode` 默认为 200——即使在错误分支上。** 这本身就是一种静默陷阱（见 RESPONSE_SHAPES.md 和 **n8n-node-configuration** NODE_FAMILY_GOTCHAS.md）：一个返回 200 但带有错误正文的错误分支看起来对调用者的 HTTP 客户端像成功一样，所以他们的错误处理永远不会触发。在每一个 Respond 节点上明确设置 `responseCode`。

### 输入验证：Set 节点的模式验证器

对于任何执行结构化输入验证的端点，在单个 **Set** 节点内运行检查，而不是按字段使用 IF/Switch 节点的链。一个节点验证整个负载，返回 `{ valid, validationError, details, requiredSchema }`，并且 IF 分支在 `valid` → 您的逻辑（200）或一个回显模式以 400 Respond，以便调用者可以自我纠正。它也比 Code 节点中的递归验证和子工作流快得多。完整模式、约束配方和表达式逃逸陷阱在 **API_WORKFLOWS.md** 中。

---

## 响应形状：映射原因 → 状态码

带有 `text/plain "Internal Server Error"` 的 5xx 实际上是错误响应，在实践中无济于事。并且并非所有失败都是 5xx。**将状态码与请求失败*的原因*匹配**，因为调用者会根据它分支：他们的监控警报会在 5xx（您的错误）上，但不会在 4xx（他们的错误）上，5xx 建议重试，而 4xx 建议不要。

**常见的错误：**将所有内容——包括坏输入——连接到一个返回 500 `internal_error` 的 `Respond`。现在调用者无法区分他们的错误和您的停机，并且您的错误率无法区分真实事件和客户端噪音。

| 原因 | 状态 | `error` 代码 | 处理位置 |
|---|---|---|---|
| 缺少必需字段 / 类型错误 | 400 | `validation_error` | 上游检查（模式验证器 / IF），不是错误输出 |
| 缺少或无效的身份验证 | 401 | `unauthorized` | 上游检查 |
| 已验证但无权访问 | 403 | `forbidden` | 上游检查 |
| 请求中的资源 ID 在您的数据中有效 | 404 | `not_found` | 分支在查找*结果*上，而不是其错误 |
| 与当前状态冲突（重复、竞争） | 409 | `conflict` | 使用逻辑检测 |
| 调用者超出速率限制 | 429 | `rate_limit_exceeded` | 设置 `Retry-After` 标头 |
| 节点抛出，原因未知 | 500 | `internal_error` | 错误输出路径 |
| 第三方 API 返回错误 | 502 | `upstream_error` | HTTP 节点的错误输出 |
| 现在无法处理（下游宕机） | 503 | `service_unavailable` | 检测特定错误，提示重试 |
| 第三方 API 超时 | 504 | `upstream_timeout` | 错误输出按消息过滤 |

所以有两种不同的流程：**4xx 是在工作*之前*决定的**（IF/Switch + 专用 Respond），**5xx 来自错误输出**（“我们尝试了，它崩溃了”）。

**一个 Respond，表达式驱动代码。** 当错误路径仅因*编号和消息*不同时（相同的正文形状，相同的标头），不要通过 Switch 扇出到 N 个 Respond 节点。Respond 节点接受 `Response Code` 和正文中的表达式——内联计算代码：

```javascript
// 单个 Respond to Webhook 的 Response Code 字段：
{{ (() => {
    const msg = $json.error?.message || $json.message || '';
    if (msg.includes('INVALID_ID')) return 400;
    if (/429|too many/i.test(msg)) return 429;
    if (/timeout/i.test(msg))      return 504;
    if (/upstream|llm|api/i.test(msg)) return 502;
    return 500;
})() }}
```

为结构不同的情况（不同的标头、不同的正文形状、重定向）保留 Switch + 多个 Respond。相同形状但不同编号的是一个表达式驱动的 Respond。

默认包封是 `{ "error": "<code>", "message": "<人类文本>" }`——HTTP 状态码已经表示成功与失败，所以不需要 `ok: false` 标志。**永远不要泄露内部信息**（堆栈跟踪、SQL、上游正文、令牌）到响应中——私下记录这些，返回一个清理过的消息。相关 ID、`retry_after`、验证 `details` 和完整不泄露列表在 **RESPONSE_SHAPES.md** 中。

---

## 工作流级错误工作流（通用的）

节点级输出处理您在节点上记住并预期连接的失败。一个**错误工作流**捕获所有其他内容：您忘记连接的节点、节点之间的崩溃、整个工作流超时、触发器失败。对于非交互式工作流，这是将“它静默停止”转换为“收到警报”的安全网。

将其构建为以一个**Error Trigger** 节点为起始的单独工作流。n8n 使用失败上下文调用它：

```json
{
  "execution": { "id": "...", "url": "...", "lastNodeExecuted": "Fetch order",
    "error": { "name": "NodeApiError", "message": "...", "timestamp": 1715000000000 } },
  "workflow": { "id": "...", "name": "Sync Stripe customers" }
}
```

最小版本——**捕获 → 通知**：

```
Error Trigger → Set (从执行 + 错误构建警报) → Slack/邮件 (发送到 #incidents)
```

一个好的警报包括工作流名称、指向编辑器和失败执行的链接、失败的节点名称和**真实**的错误消息（不是“工作流失败”）。字段表达式和通过 n8n 节点“获取失败输入”的可选升级在 **ERROR_WORKFLOWS.md** 中。

值得一开始就指出两个陷阱：

- **递归陷阱。** 如果错误工作流通知 Slack，而 Slack 正在宕机，错误工作流也会失败——原始错误会消失。在您的监控工作流使用的*不同*频道上通知（大多数工作流警报 Slack → 错误工作流使用邮件），并添加后备（写入 Data Table），以便即使通知失败，仍然留下痕迹。
- **“处理”的错误不会冒泡。** 如果节点的错误输出连接到一个不执行任何操作的丢弃数据，n8n 将考虑错误*已处理*，错误工作流**不会**触发。只有在您实际上对错误进行处理时才捕获节点级错误。

> **社区 MCP 无法做到的事情：** 分配错误工作流（实例默认或每个工作流覆盖）是一个 n8n **UI 设置**——Workflow Settings → Error Workflow。没有 MCP 工具可以设置它。使用 MCP 构建错误工作流，然后告诉用户确切的 UI 步骤来连接它，并对每个非交互式工作流重复（或设置实例默认值）。

---

## 社区 MCP 不提供的功能

| 想要做什么 | 现实情况 |
|---|---|
| 设置工作流的 **Error Workflow** 设置 | UI 仅限（Workflow Settings → Error Workflow）。没有 MCP 工具。构建工作流，然后手动给用户 UI 步骤。 |
| 切换其他 **工作流设置**（保存执行数据、时区、超时、调用者策略） | UI 仅限。`n8n_update_partial_workflow` 有 `updateSettings`，但错误工作流的分配不可靠地暴露——在 UI 中确认。 |
| 启用实例级错误日志（Sentry、服务器日志） | 实例配置，完全在工作流之外。 |

MCP **可以**做：构建错误工作流，设置节点上的 `onError`/`retryOnFail`（`updateNode`/`patchNodeField`），连接错误输出（`addConnection` with `sourceIndex: 1`），验证（`validate_workflow`, `n8n_validate_workflow`），自动修复常见问题（`n8n_autofix_workflow`），测试（`n8n_test_workflow`），以及检查失败（`n8n_executions`）。

---

## 反模式

| 反模式 | 问题所在 | 解决方法 |
|---|---|---|
| `onError` 设置但错误输出未连接 | 错误被静默丢弃；运行结果显示为 **成功** | 将 `sourceIndex: 1` 连接到真实处理器，或恢复 `onError` 为 `stopWorkflow` 以使其响亮 |
| 错误输出已连接但未设置 `onError` | 插槽从未触发；处理器无法访问；工作流在失败时停止 | 设置 `onError: "continueErrorOutput"` |
| Webhook → 处理 → 响应，无错误分支 | 调用者收到超时或 n8n 的通用 500 | 将每个可能失败的节点的错误输出连接到响应 |
| 错误分支返回 200 并带有 `{error}` 主体 | 调用者的客户端读取成功；其错误处理从未触发 | 在错误响应上显式设置 `responseCode` 为 4xx/5xx |
| 所有错误都返回一个 500 `internal_error` | 调用者无法区分其错误输入和您的中断 | 映射原因 → 状态 (4xx 调用者，5xx 您) |
| 在 Code 节点中捕获错误并将其作为数据返回 | 下游进程处理错误形状的数据并继续 | 让它抛出；使用 `onError: "continueErrorOutput"` + 连接路径 |
| 没有 `retryOnFail` 的网络节点 | 每个暂时的 429/闪烁都显示为 5xx；警报在噪音上触发 | `retryOnFail: true, maxTries: 3, waitBetweenTries: 5000` |
| Switch → N 个不同的响应，仅状态码不同 | 5 个节点用于一个响应 | 在一个表达式驱动的响应中内联计算代码 |
| 未处理的错误工作流，没有错误工作流 | 一个真实的失败无处可去 | 构建一个错误触发工作流 + 在 UI 中分配它 |
| 错误工作流通知与工作流监控相同的通道 | 频道中断 → 错误工作流也失败 → 错误消失 | 使用不同的频道 + 数据表回退 |
| 将 `$json.error` (堆栈/SQL/令牌) 泄露到响应中 | 将内部信息暴露给调用者/攻击者 | 私密记录，返回一个清理后的消息 |

---

## 参考文件

| 文件 | 读取时间 |
|---|---|
| **NODE_ERROR_OUTPUTS.md** | 在单个可能失败的节点上连接每个节点的错误输出 |
| **API_WORKFLOWS.md** | 构建审查 webhook → 响应工作流，包括模式验证器 |
| **RESPONSE_SHAPES.md** | 定义响应主体约定、状态码以及不应泄露的内容 |
| **ERROR_WORKFLOWS.md** | 设置未处理工作流的通用捕获 |

---

## 与其他技能的集成

- **n8n-workflow-patterns** — webhook/API 和计划模式是错误处理所在。使用它来获取整体形状；使用此技能来加固它。
- **n8n-node-configuration** — `onError`/`retryOnFail` 是节点配置；NODE_FAMILY_GOTCHAS.md 深入介绍了 Webhook/Respond 响应码陷阱。
- **n8n-validation-expert** — 半连接的错误输出（两个缺失步骤之一）是一个连接/配置审计项，而不是验证错误。此技能是修复方法。
- **n8n-expression-syntax** — 表达式驱动的 `响应代码` 和警报消息表达式依赖于正确的 `{{ }}` 语法和 `$json.error` 访问。
- **n8n-code-javascript / n8n-code-python** — 如果您在 Code 节点内部捕获错误，请故意决定：重新抛出以使用错误输出，或处理并继续。不要返回错误形状的数据并假装成功。
- **n8n-code-tool** — 代理的 Code 工具将抛出的错误返回给 LLM，然后 LLM 重试；这是与工作流节点不同的错误合同。
- **n8n-binary-and-data** — 文件/二进制操作也可能失败；像网络节点一样连接它们的错误输出。

---

## 快速参考清单

对于 **API / webhook** 工作流：

- [ ] Webhook 触发器使用 `responseMode: "responseNode"`
- [ ] 输入在上游验证 → 4xx 响应（模式验证器或 IF）
- [ ] 每个可能失败的节点都有 `onError: "continueErrorOutput"` **和** `main[1]` 连接
- [ ] 网络节点有 `retryOnFail: true, maxTries: 3, waitBetweenTries: 5000`
- [ ] 错误路径以带有 **显式** 4xx/5xx `responseCode` 的响应结束
- [ ] 状态码与原因匹配 (4xx 调用者，5xx 您)
- [ ] 错误主体是 `{ error, message }` — 无堆栈跟踪、SQL 或令牌
- [ ] 使用 `n8n_get_workflow` 验证：每个可能失败的节点上都有 `onError` 和 `main[1]`

对于 **未处理** 的（计划/cron/队列）工作流：

- [ ] 网络节点有 `retryOnFail` 配置
- [ ] 存在一个错误触发工作流（捕获 → 通知，可选重试）
- [ ] 错误工作流在不同的频道上通知 + 有回退（递归陷阱）
- [ ] 错误工作流设置在 n8n UI 中分配（MCP 无法完成 — 提醒用户）

---

**记住**：默认是无声的。错误处理是两步走 — 使失败 *路由*（每个节点的 `onError` + 连接输出，或一个捕获所有错误的通用工作流）并使其 *说话*（一个状态码和主体，告诉真相）。半步比无步更糟，因为它看起来完成了。
