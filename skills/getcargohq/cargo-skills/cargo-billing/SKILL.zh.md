---
name: cargo-billing
description: 了解Cargo的成本构成——剩余额度、按工作流、连接器或代理的使用情况、订阅状态和发票历史。触发条件："我还有多少额度"、"这个成本是多少"、"为什么账单这么高"、"我快要超支了吗"、"这个是否符合我们的预算"、"显示我的发票"、"我这个月花了多少钱"、"我当前使用哪个套餐"、"免费额度包含哪些"、"我还有多少免费额度"、"我能负担这次运行吗"、"添加一张卡"、"更新我的支付方式"、"为什么我的卡被拒"。需要具有管理员访问权限的令牌。在归因于特定节点或切割运行成本时跳过——使用cargo-diagnostics。
---

# Cargo CLI — 账单

账单和信用管理：获取使用指标、检查订阅状态、查看发票和管理信用额度。

> 查看完整的 JSON 响应结构，请参阅 `references/response-shapes.md`。
> 查看常见错误及其解决方法，请参阅 `references/troubleshooting.md`。
> 查看使用指标和订阅示例，请参阅 `references/examples/usage-metrics.md`。

## 初始化

如果已经登录（`cargo-ai whoami` 返回工作区），则跳到下一节。

```bash
npm install -g @cargo-ai/cli            # 没有全局安装？请为每个命令添加 `npx @cargo-ai/cli` 前缀
cargo-ai login --email you@company.com  # 通过邮件验证，无需浏览器；首次使用时创建账户
                                        # 可选参数：--oauth（浏览器） · --token <api-token>（CI）
cargo-ai whoami                         # 在执行任何写入操作前确认活动工作区
```

每个命令都会将 JSON 输出到标准输出；失败时以非零状态退出并输出 `{"errorMessage": "..."}`。创建运行或批处理操作都是异步的 — 请传递 `--wait-until-finished` 或轮询匹配的 `get`。**仅管理员可用：** 此技能中的每个命令都需要具有工作区管理员访问权限的令牌。非管理员令牌将返回 `{"errorMessage":"forbidden"}`。当完整技能包安装完成后，`[../cargo/references/prerequisites.md](../cargo/references/prerequisites.md)` 会添加 CLI 版本锁定、令牌范围和管理员专用界面。

## 先发现资源

使用指标可以按资源 UUID 进行过滤和分组。在查询前发现它们。

```bash
cargo-ai orchestration play list            # 所有 play（名称，workflowUuid）
cargo-ai orchestration tool list            # 所有工具（名称，workflowUuid）
cargo-ai ai agent list                     # 所有代理（uuid，名称）
cargo-ai connection connector list          # 所有连接器（uuid，名称，integrationSlug）
cargo-ai storage model list                # 所有模型（uuid，名称，slug）
```

## 快速参考

```bash
cargo-ai billing usage get-metrics --from <YYYY-MM-DD> --to <YYYY-MM-DD>
cargo-ai billing usage get-metrics --from <YYYY-MM-DD> --to <YYYY-MM-DD> --group-by workflow_uuid
cargo-ai billing subscription get
cargo-ai billing subscription get-invoices
cargo-ai billing subscription update-payment-method --card-number <number> --card-exp <MM/YYYY> --card-cvc <cvc>
cargo-ai billing subscription create-portal-session
```

## 在运行批处理前估算成本

在触发大型批处理之前，估算信用额度消耗以避免意外费用。

**步骤 1 — 检查当前信用额度余额：**

```bash
cargo-ai billing subscription get
# → subscriptionAvailableCreditsCount - subscriptionCreditsUsedCount = 剩余信用额度
```

**步骤 2 — 从样本运行中估算成本：**

首先在单个记录上运行工作流并测量消耗的信用额度：

```bash
# 在一个记录上运行
cargo-ai orchestration run create --workflow-uuid <uuid> --data '{...}'
# → 轮询至完成

# 检查该运行的信用额度消耗
cargo-ai billing usage get-metrics \
  --from <today> --to <today> \
  --workflow-uuid <uuid>
# → metrics[].items[] 对于该工作流（响应只有一个键，`metrics` — 没有总使用量）
```

**步骤 3 — 估算批处理成本：**

```
estimated_cost = (credits_per_record × number_of_records)      # 提供者操作
               + (nodes_per_record × number_of_records / 100)  # 执行费用
```

第二项是每执行 0.01 信用额的平台费用（“执行费用”）。样本运行免费测量它 — 记录的执行次数是 `length(run.executions)`，或样本窗口中 `--unit orchestration.executions` 的单行。忽略它会导致每个步骤密集的图报价过低。

在继续之前，与 `subscriptionAvailableCreditsCount - subscriptionCreditsUsedCount` 进行比较。

**步骤 4 — 在批处理期间监控：**

```bash
# 检查批处理期间的运行成本
cargo-ai billing usage get-metrics \
  --from <start-date> --to <today> \
  --workflow-uuid <uuid>
```

**成本杠杆：**

| 操作 | 效果 |
|---|---|
| 使用更便宜的模型（例如 `gpt-4o-mini` vs `gpt-4o`） | AI 节点显著降低成本 |
| 在图早期添加 `filter` 节点 | 在昂贵的连接器调用之前跳过不符合条件的记录 |
| 设置 `fallbackOnFailure: false` | 在失败时提前停止运行，而不是继续到下游节点 |
| 减少代理节点上的 `maxSteps` | 限制代理每条记录可以调用的工具数量 |
| 减少节点数量 — 合并链式 `variables`，将分支对合并为一个 `switch` | 0.01/执行 × 记录；对于步骤密集而非提供者成本的图，这是唯一的杠杆 |

> 要找出在挑选杠杆之前 **哪个** 节点或提供者主导了 play 的支出，请遵循 [`../cargo-diagnostics/references/play-optimize-credits.md`](../cargo-diagnostics/references/play-optimize-credits.md) 中的归因运行手册。

## 使用指标

获取任何时间范围内的信用额度和使用数据，可选地按维度过滤和分组。

```bash
# 基本使用指标
cargo-ai billing usage get-metrics --from <start-date> --to <end-date>

# 按维度分组
cargo-ai billing usage get-metrics --from <start-date> --to <end-date> --group-by workflow_uuid
cargo-ai billing usage get-metrics --from <start-date> --to <end-date> --group-by connector_uuid
cargo-ai billing usage get-metrics --from <start-date> --to <end-date> --group-by integration_slug
cargo-ai billing usage get-metrics --from <start-date> --to <end-date> --group-by model_uuid
cargo-ai billing usage get-metrics --from <start-date> --to <end-date> --group-by agent_uuid

# 按特定资源过滤
cargo-ai billing usage get-metrics --from <start-date> --to <end-date> --workflow-uuid <uuid>
cargo-ai billing usage get-metrics --from <start-date> --to <end-date> --agent-uuid <uuid>
cargo-ai billing usage get-metrics --from <start-date> --to <end-date> --connector-uuid <uuid>
cargo-ai billing usage get-metrics --from <start-date> --to <end-date> --integration-slug <slug>

# 一次一个单位 — 以下三个是唯一接受的值
cargo-ai billing usage get-metrics --from <start-date> --to <end-date> --unit billing.credits
cargo-ai billing usage get-metrics --from <start-date> --to <end-date> --unit orchestration.executions
cargo-ai billing usage get-metrics --from <start-date> --to <end-date> --unit storage.records
```

`--group-by` 值：`workflow_uuid`，`connector_uuid`，`model_uuid`，`integration_slug`，`agent_uuid`。

可用过滤器：`--workflow-uuid`，`--model-uuid`，`--connector-uuid`，`--integration-slug`，`--slug`，`--agent-uuid`。可与 `--group-by` 和 `--unit` 结合使用。

### 三个使用单位

`--unit` 必须是 `billing.credits`，`orchestration.executions` 或 `storage.records` — 任何其他内容都会返回 400 并列出它们。**如果没有 `--unit`，所有三个都会以交错的方式返回在同一个 `items[]` 数组中**，它们的 `count` 字段数量不同。从 slugs 中读取单位：

| 单位 | `items[]` 中的 slugs | `count` 是什么 |
|---|---|---|
| `billing.credits` | `integration.<slug>.action.<action>`，`native.<action>`，`integration.<slug>.chat`，`integration.<slug>.extractor.<name>` | 信用额度（分数） |
| `orchestration.executions` | `success`，`error` | **节点执行**，一对一计数 — 不是信用额度 |
| `storage.records` | `insert` | 写入的记录 |

一个未指定调用的调用，显示 `{"slug":"success","count":1043}` 接着是 `{"slug":"integration.peopleDataLabs.action.queryPeople","count":174}`，报告 1,043 个 *执行* 接着是 174 个 *信用额度*。当数字用于估算时，请传递 `--unit`。

### 执行费用

**每个节点执行都计费 0.01 信用额度 — 每 100 次执行 1 信用额度。** 它适用于每种节点类型和每个节点，包括不携带提供者价格的结构性原生节点：`branch`，`filter`，`switch`，`split`，`group`，`variables`，`start`，`end`。工作流中没有免费的步骤。

此费用**不按节点归因**。`run get` → `executions[].creditsUsedCount` 和 `spans.execution_credits_used_count` 列都只携带 *提供者* 成本，原生节点即使不收费也会读取 `0`。因此，按节点归因会低估每个图，并且随着步骤数的增加，短缺会增长，而不是随着支出增长。

唯一显示它的界面：

```bash
cargo-ai billing usage get-metrics --from <YYYY-MM-DD> --to <YYYY-MM-DD> --unit orchestration.executions
# → items[] = [{"slug":"success","count":<executions>}, {"slug":"error","count":<executions>}]
# credits = (success + error) / 100
```

与运行时表进行交叉检查，它们按行一致：

```bash
cargo-ai orchestration query execute \
  "SELECT execution_status, count() AS executions, count() / 100 AS credits
   FROM spans WHERE execution_started_at >= '<YYYY-MM-DD>' GROUP BY execution_status"
```

**为什么这对估算很重要。** 一个图的成本有两个项：

```
credits = (provider cost per record × records) + (nodes per record × records ÷ 100)
```

第二项在动作密集的 play 中很小（每条记录的 LinkedIn 富集会使其 8 个步骤显得微不足道），而在步骤密集、动作稀疏的图中占主导地位 — 12 个节点的路由扫描 20,000 条记录，没有任何提供者调用，成本为 2,400 信用额度。失败的执行也会计费，因此一个在后期失败的图会为其整个前缀计费。

**工具会发散。** 一个工具节点是一个执行 *加上* 工具自身图中的每个节点，每个节点都单独计费。将子图提取到工具中是一个调试性优势，而不是节省成本 — 它为每条记录增加了一个执行，在内部成本之上。当图的执行次数超过其可见节点数量时，工具节点是首先要查找的地方：在 `spans` 中按 `node_slug` 分组以找到它们。

## 订阅和信用额度

```bash
cargo-ai billing subscription get                    # 当前计划，已用/可用信用额度，周期日期
cargo-ai billing subscription get-invoices            # 发票历史（金额以分为单位）
cargo-ai billing subscription get-credit-card         # 存储的卡
cargo-ai billing subscription update-payment-method   # 添加或替换卡（见下文）
cargo-ai billing subscription create-portal-session   # Stripe 门户 URL 用于自助服务账单
```

剩余信用额度 = `subscriptionAvailableCreditsCount - subscriptionCreditsUsedCount` 从 `subscription get`。

**注意：** 发票金额以分为单位返回。除以 100 获取美元价值。

### 免费层级

新账户从 **100 个免费信用额度且没有存储卡** 开始。当 `subscription get` 显示新鲜或接近新鲜的余额时，请根据该预算回答成本问题，而不是作为抽象数字 — “你已经使用了 12 个你 100 个免费信用额度中的” 是对 “你做得怎么样？” 有用的答案，当用户决定是否继续时，这也是诚实的答案。

100 个信用额度能买到什么，作为大致参考（每动作成本在 [`../cargo-gtm/references/credits-cost-table.md`](../cargo-gtm/references/credits-cost-table.md)）：

| 工作 | 成本 | 100 信用额度 ≈ |
|---|---|---|
| 源线索 — `salesNavigator.searchLeads` | 0.02/记录 | ~5,000 条线索 |
| 从 LinkedIn URL 和验证电子邮件中富集 — `aiArk.enrichPerson` | 0.1 | ~1,000 人 |
| 验证电子邮件 — `waterfall.verifyEmail` | 0.1 | ~1,000 次检查 |
| 完整联系人富集 — `waterfall.enrichContact` | 2 | ~50 个联系人 |
| 查找电话 — `FullEnrich.findPhone` | 6 | ~16 个号码 |

[快速入门演示](../cargo-quickstart/SKILL.md) 大约花费 **0.5**。电话查询是烧掉免费层级最快的方式，因此电话是 **受保护的杠杆**：升级层级每条记录运行 3–7 信用额度，约 10 倍于电子邮件，并且永远不会出现在默认链中 — 只有在明确用户请求时，在合格线索上才会进入计划。完整支出规则在 [`../cargo-gtm/references/cost-discipline.md`](../cargo-gtm/references/cost-discipline.md) 中。

### 添加卡

工作区正好持有一个卡。`update-payment-method` 设置它，无论是否已经存储卡，并采用三种方式传递详细信息。

```bash
# 卡详细信息 — 无需浏览器，无需传递
cargo-ai billing subscription update-payment-method \
  --card-number 4242424242424242 --card-exp 12/2030 --card-cvc 123

# 同上，但将卡号从 shell 历史记录和进程列表中排除
echo '{"number":"4242424242424242","expMonth":12,"expYear":2030,"cvc":"123"}' \
  | cargo-ai billing subscription update-payment-method --card-stdin

# 无卡详细信息 — 打印 Stripe 托管的表单 URL 并等待卡到达
cargo-ai billing subscription update-payment-method
```

**优先使用 `--card-stdin`。** 任何作为标志传递的内容都会出现在 shell 历史记录中，并且任何可以读取进程列表的进程都可以读取。卡详细信息直接从您的机器传输到 Stripe 以换取令牌；它们永远不会到达 Cargo API，并且不会打印输出。

**永远不要编造卡详细信息，并且永远不要重用其他地方复制的号码。** 请求用户提供它们，或者使用无参数形式并将 URL 交给用户。

无参数形式是在没有要提交的详细信息时的回退：它打印一个 URL，直接在卡表单上打开，然后轮询直到卡更改（`--timeout`，`--poll-interval`，`--no-open`）。将该 URL 传递给用户 — 它可以通过 SSH 和在沙盒中工作。

无论哪种方式，卡都会在成为默认卡之前与发行商进行验证，因此无法收费的卡会在这里失败，而不是在下次续订时无声地失败。

| 失败 | 意味着什么 | 该怎么做 |
|---|---|---|
| `cardDeclined` + `declineCode` | 发行商拒绝了验证 | 读取 `declineCode`。在一个支出限制的虚拟卡上，`insufficient_funds` 或限制代码意味着预算或商户限制使我们排除在外 — 请请求持卡人提高预算 |
| `authenticationRequired` | 卡需要 3-D Secure，这需要持卡人到场 | 重新运行，不带参数，并将托管表单 URL 交给用户 |
| `paymentMethodNotFound` | 详细信息没有解析为可用的卡 | 与用户重新检查号码和到期日 |

卡更新被限制为 **每小时每个工作区 10 次**（与设置意图共享）。重试一个被拒绝的卡会消耗该预算 — 修复原因，而不是循环。

## 帮助

每个命令都支持 `--help`：

```bash
cargo-ai billing usage get-metrics --help
cargo-ai billing subscription get --help
cargo-ai billing subscription get-invoices --help
```
