---
name: cargo-mailbox-management
description: 从 Cargo 拥有的收件箱发送邮件——为发送域配置邮箱，运行提供者预热并执行每日5→40的发送增量，使用 `sendEmail` 动作发送，并读取回邮件线程、回复、送达事件和工作区屏蔽列表。触发条件： "设置发送邮箱"、"为外发配置收件箱"、"预热此邮箱"、"我今天还能发送多少"、"从 Cargo 发送此邮件"、"他们回复了吗"、"谁退订了"、"屏蔽此收件人"、"把我从列表中移除"、"再也不要给他们发邮件"、"邮箱费用是多少"、"我的邮箱卡在待处理状态"。邮箱是按月计费的周期性信用额度，每次发送都基于基础、屏蔽和相关性进行限制。跳过时：编写文案或构建受众时——使用 cargo-gtm；邮箱属于 git 仓库——使用 cargo-project。
---

# Cargo CLI — 邮箱管理

**邮箱**。邮箱是一个工作区**拥有的**真实发送收件箱——通过 Cargo 在工作区也拥有的发送域上配置，Cargo 持有并使用 SMTP 和 IMAP 凭据来投递外发邮件并读取回复的邮件。有两件事随之而来，而且都很容易出错：邮箱是一个**每月递归信用费用**，而不是按记录收费，并且这个域**不**发送。它配置收件箱，进行预热，并报告它所做的事情；发送本身是 `sendEmail` 操作，在
[`cargo-orchestration`](../cargo-orchestration/SKILL.md) 下。

```bash
cargo-ai mailboxManagement mailbox      …   # 配置、预热、发送额度
cargo-ai mailboxManagement message      …   # 外发发送
cargo-ai mailboxManagement thread       …   # 会话及其回复
cargo-ai mailboxManagement event        …   # 已发送/已打开/已点击/已回复/已退订
cargo-ai mailboxManagement suppression  …   # 工作区范围的勿发列表
cargo-ai mailboxManagement pricing      …   # 每个邮箱类型的每月信用额度
```

> **版本说明**。本页上的所有内容都在固定 CLI（1.0.66）中实时可用，包括
> `mailbox get-warmup-stats` 和 `--daily-target` 默认值为 40——这两个都是在编写此技能时合并但未发布的。在**旧版** CLI 上，`--daily-target` 读取 "如果省略则使用提供者默认值"，而 `get-warmup-stats` **静默打印 `mailbox` 组帮助而不是报错**，因此这里缺少子命令看起来像使用错误而不是过时的安装。`cargo-ai mailboxManagement mailbox --help` 列出您的 CLI 实际拥有的内容；重新运行
> [`../cargo/SKILL.md`](../cargo/SKILL.md) 中的会话刷新以更新。

## 初始化

已经登录 (`cargo-ai whoami` 返回工作区)？跳到下一节。

```bash
npm install -g @cargo-ai/cli            # 没有全局安装？为每个命令前缀 `npx @cargo-ai/cli`
cargo-ai login --email you@company.com  # 发送代码，无需浏览器；首次使用时创建帐户
                                        # 替代方案：--oauth (浏览器) · --token <api-token> (CI)
cargo-ai whoami                         # 在任何写入之前确认活动工作区
```

每个命令都打印 JSON 到标准输出；失败时以非零状态退出，并带有 `{"errorMessage": "..."}`。
这个域中的任何内容都不是异步的——每个命令都是一个单独的 HTTP 调用，因此没有轮询的运行（唯一看起来异步的东西是 `pending` 状态下新创建的邮箱，使用 `mailbox refresh-status` 而不是 `run get` 来轮询）。邮箱由
`mailboxManagement:read` / `mailboxManagement:write` 权限保护，管理员和编辑都持有，而查看者不持有；如果创建或更新返回权限错误，则令牌是只读的 ([`../cargo-workspace-management/SKILL.md`](../cargo-workspace-management/SKILL.md))。
当完整技能包安装时，[`../cargo/references/prerequisites.md`](../cargo/references/prerequisites.md)
添加了 CLI 版本固定、令牌范围和仅管理员界面。

## 发送前——三项检查

**这是一个阻塞门，而不是建议。** Cargo 拥有邮箱会改变谁按发送；它不会改变是否应该发送消息。规范规则是
[`../cargo-gtm/references/acceptable-use.md`](../cargo-gtm/references/acceptable-use.md) §3，它们在这里保持不变——在第一个 `sendEmail` 之前运行所有三项，而不是之后：

- **基础**——哪个权限覆盖这个受众（客户、已选择联系人的联系人、活动参与者，或 B2B 角色的已记录合法利益情况）？
- **勿发**——在丰富或发送之前，从受众中减去工作区勿发列表。`suppression list` 是免费的，这个域是它的权威来源。
- **相关性**——您能否按接收者命名，为什么这条消息是给他们的？

任何失败的检查都是停止并询问。Cargo 拥有的发送有两个特定的义务：

- **预热是上限，而不是目标。** `get-send-allowance` 报告邮箱今天可以发送什么；它不是一个要填满的配额。要求提高它，将一个活动分布在一批新邮箱上以清除相同容量，或旋转身份以便过滤器从每个地方看到较少的东西，是 `acceptable-use.md` §2 中的规避拒绝——不是一个配置问题。
- **退订是自动且绝对的。** 每次发送都带有一个签名的 `List-Unsubscribe` 标头；使用它的接收者会写入工作区范围的 `suppression` 行，并且引擎会拒绝发送到该地址。没有删除命令，这正是要点——永远不要绕过勿发来重新联系某人。

## 控制邮箱的两个数字

它们看起来相似，但含义相反。混淆它们是最常见的误读邮箱健康的方式。

| | `mailbox get-send-allowance` | `mailbox get-warmup-stats` |
| --- | --- | --- |
| 衡量 | **您的** 真实触达 | 提供者的 **虚拟** 预热流量 |
| 窗口 | 滚动 24 小时 | 当天，UTC |
| 返回 | `dailyLimit`，`sentCount`，`remainingCount` | `sentCount`，`deliveredCount`，`spamCount`，`inboxRate`，`spamRate` |
| 回答 | "我可以再发送多少？" | "这个收件箱是进入收件箱还是垃圾邮件？" |

`dailyLimit` 不是一个设置——它是根据预热运行了多长时间推导出来的。算术、`warmupStatus` 转变以及如何根据它调整舰队大小在
**[`references/warmup-and-allowance.md`](references/warmup-and-allowance.md)** 中。在您承诺任何发送量之前阅读它。

## 命令

所有命令输出 JSON。读取需要 `mailboxManagement:read`；所有提供配置、更新、删除或勿发都需要 `mailboxManagement:write`。

### 配置邮箱

**首先，您会遇到的差距。** `mailbox create` 需要 `--domain-uuid`，而 Cargo 没有列出发送域的命令——`domainManagement` API 存在但没有 CLI 界面。从 Cargo 网络应用程序获取 UUID，或在 CDK 仓库中使用 `defineDomain` 声明域，然后从 `cargo.state.json` 读取它。对用户说这些，而不是猜测 UUID。

在购买之前为域定价也有同样的差距，一个直接的 API 调用可以关闭它：
`GET /v1/domainManagement/domains/search?name=<domain>` 返回 `available` 和 `priceCredits`
（其中 **`null` 表示不可购买，不是免费的**）。舰队的一侧——那个调用，根据轰炸半径而不是容量调整域大小， apex 重定向，DMARC，命名，以及为什么 `dnsRecords` 必须保持未声明——是
**[`references/sending-domains.md`](references/sending-domains.md)**。

```bash
cargo-ai mailboxManagement mailbox create \
  --domain-uuid <domain-uuid> \
  --type google \
  --username jane \
  --first-name Jane \
  --last-name Doe \
  --signature '<p>Jane Doe · Acme</p>' \
  --folder-uuid <folder-uuid>

cargo-ai mailboxManagement mailbox refresh-status <uuid>   # 重复直到状态为 "active"
```

- `--type` — `google`，`shared` 或 `private`。**`outlook` 被标志接受，但始终失败**
  `transportNotSupported`：Graph 传输尚未推出，因此 Outlook 邮箱无法投递。选择其他三个中的一个。
- `--username` — 仅本地部分（`jane` 对于 `jane@acme.com`）。小写；字母、数字、点、连字符和下划线，1–64 个字符，开头和结尾是字母数字。
- `--first-name` / `--last-name` — 接收者看到的发件人标题。在真实身份下使用真实人的名字；一个虚构的发送者是一个 §2 拒绝。
- `--signature` — HTML，存储在邮箱上（最大 10,000 个字符）。
- `--folder-uuid` — 一个 `mailbox` 类型的文件夹，来自
  [`cargo-workspace-management`](../cargo-workspace-management/SKILL.md)。

`create` 立即返回 `status: "pending"`——提供者尚未发出凭证。当 `refresh-status` 说它时，或者在其自己的五分钟内达到 `active`；在那时尝试发送会失败，带有 `credentialsMissing`。

```bash
cargo-ai mailboxManagement mailbox list                        # 每个邮箱
cargo-ai mailboxManagement mailbox list --statuses active      # 以逗号分隔，无空格
cargo-ai mailboxManagement mailbox list --domain-uuid <uuid>
cargo-ai mailboxManagement mailbox get <uuid>

cargo-ai mailboxManagement mailbox update --uuid <uuid> --first-name Janet
cargo-ai mailboxManagement mailbox update --uuid <uuid> --folder-uuid none   # "none" 清除

cargo-ai mailboxManagement mailbox remove <uuid>               # 在提供者处删除
```

- `--statuses` — `pending`，`active`，`inactive`，以逗号分隔**无空格**。一个 `inactive` 邮箱由提供者禁用；`errorCode` 说原因 (`401` 认证，`402` 垃圾邮件) 并且它不会发送，直到它被修复。
- `none` 是 `--folder-uuid` 和 `--signature` 上的哨兵，表示 "清除它"。在 `list` 中，`--folder-uuid none` 表示 "无文件夹的邮箱"。
- `remove` 是如何停止每月计费。没有暂停。

### 预热

一个从未开始预热的邮箱被固定在**每天 5 个真实发送，永远**。预热是让它移动，并且它需要 45 天才能完成。

```bash
cargo-ai mailboxManagement mailbox start-warmup <uuid> --daily-target 40
cargo-ai mailboxManagement mailbox get-warmup-stats <uuid>                    # 下一个 CLI 发布

cargo-ai mailboxManagement mailbox update-warmup --uuid <uuid> --status paused
cargo-ai mailboxManagement mailbox update-warmup --uuid <uuid> --daily-target 25
cargo-ai mailboxManagement mailbox stop-warmup <uuid>                         # 重置预热
```

- `--daily-target` — 全预热时每天预热消息，1–40（默认 40）。这是提供者的虚拟流量，**不是**您的发送额度。
- `--status` 在 `update-warmup` 上接受整个枚举，但只有 `active` 和 `paused` 才会起作用：`pending` 和 `failed` 是提供者自行达到的状态，`disabled` 是 `stop-warmup` 的用途。
- `stop-warmup` **重置 Cargo 发送预热**以及拆除提供者预热——邮箱会回到每天 5 个并重新开始 45 天。除非您真的想那样，否则暂停。

### 在发送前检查额度

```bash
cargo-ai mailboxManagement mailbox get-send-allowance <uuid>
# → {"allowance":{"dailyLimit":12,"sentCount":4,"remainingCount":8}}
```

在注册批量之前读取 `remainingCount`。超过它的发送不会排队给明天——它们会立即失败，每行浪费一次运行。

### 读取发生的事情

```bash
cargo-ai mailboxManagement message list --mailbox-uuid <uuid> --statuses sent,replied --limit 50
cargo-ai mailboxManagement message get <uuid>

cargo-ai mailboxManagement thread list --mailbox-uuid <uuid> --search acme
cargo-ai mailboxManagement thread get <uuid>

cargo-ai mailboxManagement event list --kinds replied,unsubscribed --occurred-after 2026-08-01
```

- **消息与线程与事件。** 一个 *消息* 是一次外发发送。一个 *线程* 是一个会话——它的 `lastEmail` 和 `lastEvent` 是您按回复队列排序的东西。一个 *事件* 是消息发生的事情（`sent`，`opened`，`clicked`，`replied`，`bounced`，`unsubscribed`）。传入的回复是事件，不是消息行；只有外发邮件是消息。
- `--statuses` 在 `message list` / `thread list` 上是**列表状态**——`pending`，`error` 或事件类型。`success` 不在那一组中：已投递的消息读取为 `sent` 或之后。
- `--kinds`，`--statuses`，`--reasons` 都是逗号分隔，无空格。
- **`bounced` 目前还没有触发。** 没有解析投递状态通知，所以退订不会产生事件，也不会自动抑制。不要构建一个可投递性报告，将空的退订计数视为干净列表。
- `message`，`thread` 和 `event` 列表默认为 `--limit 50`（最大 200）并返回一个 `count`。`mailbox list` 和 `suppression list` 没有默认限制（最大 1000），并且 `mailbox list`
  返回**没有** `count`——见 [`references/response-shapes.md`](references/response-shapes.md)。

### 勿发

工作区范围的，不是每个邮箱：接收者选择退订是选择退订发送者，而不是发送者碰巧拥有的一个地址。

```bash
cargo-ai mailboxManagement suppression list --reasons unsubscribed,manual
cargo-ai mailboxManagement suppression create --email opted-out@acme.com
```

- 原因是 `unsubscribed`（接收者自己的选择，通过 `List-Unsubscribe`），`bounced`，`complained` 和 `manual`。`suppression create` 总是记录 `manual`。
- 它是幂等的——抑制一个已经抑制的地址会返回现有行。
- 地址在写入和检查时都会规范化（`trim().toLowerCase()`），所以大小写和多余的空格不能让被抑制的接收者重新进入发送。
- 没有 `suppression remove`。这是故意的。

### 定价

```bash
cargo-ai mailboxManagement pricing get
# → {"monthlyCredits":{"google":125,"outlook":160,"shared":100,"private":100}}
```

在引用舰队成本之前**实时**阅读这个——上面的数字是工作区在编写时返回的，不是常数。

## 发送：`sendEmail` 操作

投递故意不在本 CLI 域中。它是一个原生编排操作，以便发送继承编排的节拍、重试和信用机制：

```bash
cargo-ai orchestration action execute \
  --action '{"kind":"native","actionSlug":"sendEmail"}' \
  --data '{"mailboxUuid":"<mailbox-uuid>","to":"jane@acme.com","subject":"...","bodyHtml":"<p>…</p>"}' \
  --wait-until-finished
```

- **每发送 0.1 信用**，固定。操作不携带 `config`；输入在 `--data` 中，就像其他所有操作一样 ([`../cargo-orchestration/SKILL.md`](../cargo-orchestration/SKILL.md)).
- 可选 `bodyText`（省略时从 HTML 生成），`inReplyTo` 和 `references`。
- **要保持回复线程，发送整个链。** `references` 是到目前为止线程中所有的 `Message-ID`，按最旧的顺序——不是仅父级。否则邮件客户端会断开线程。
- 操作按**每个邮箱**限制到该邮箱自己的每日限额，分布在整天。在具有 40 个剩余的邮箱上 100 个突发会立即失败第 41 个，而不是将其保留一天。
- **被拒绝的发送是节点错误，而不是抛出的异常。** `recipientSuppressed`，`mailboxNotActive` 和 `transportNotSupported` 需要人工干预，不会重试；
  `dailyLimitReached`，`credentialsMissing` 和 `deliveryFailed` 会自行重试。
- **CLI 没有干运行。** 引擎有一个，但没有 `action execute` 标志达到它——命令运行时发送是实时的。先发送给自己。

线程、完整的拒绝表以及 Cargo 注入到每个消息中的内容（退订标题、打开像素、点击重定向）在
**[`references/sending.md`](references/sending.md)** 中。

### 从工作流中读取事件：`listEmailEvents`

`mailboxManagement event list` 是 CLI 读取，但在工作流中，投递事件来自一个**原生操作**（CLI ≥ 1.0.86），所以播放可以根据某人回复分支：

```bash
cargo-ai orchestration action execute \
  --action '{"kind":"native","actionSlug":"listEmailEvents"}' \
  --data '{"threadUuid":"<thread-uuid>","kinds":["replied","clicked"],"limit":50}' \
  --wait-until-finished
```

- `threadUuid` 是必需的；`kinds` 是可选的（对于线程上的每个事件都省略）并且 `limit` 默认为 **50**，上限为 **200**，按最新顺序排列。
- 事件类型为 `sent`、`opened`、`clicked`、`replied`、`bounced`、`unsubscribed`。注意，即使 UI 标签为“Viewed”，线值也是 **`opened`**。
- 每个事件返回 `uuid`、`mailboxUuid`、`messageUuid`、`threadUuid`、`kind`、`occurredAt`、`actorEmail`，以及可空的 `url`（在 `clicked` 上）、`inboundRfcMessageId` 和 `snippet`。
- **`bounced` 仍然没有生产者** — 目前还没有解析投递状态通知，因此基于它进行过滤将返回空结果且证明不了任何事。切勿将空的退回计数报告为干净的列表。

## 成本约束

此域名的计费方式与其他不同，在配置任何东西之前，需要明确这一点。

- **邮箱是按月计费的** — 每个邮箱每月 100–160 信用点，只要它存在。五个邮箱每月就是 500–625 信用点，不是一次性的。`mailbox remove` 是唯一停止计费的方式；没有暂停功能。在第一次 `create` 之前，引用实时 `pricing get` 的舰队规模和每月信用点估算，并明确得到肯定答复。
- **发送每个 0.1 信用点**，因此数量便宜，但舰队不便宜。按顺序进行计算。
- **调用 `sendEmail` 的运行或计划工具在每个运行时都会重新计费** — 并且每个运行都会重新联系相同的人，这是 `acceptable-use.md` 中 §6 节奏门，与支出门一样重要。在批量注册之前检查 `get-send-allowance`：超出允许范围的行每次运行都会消耗一次运行并什么也不发送。
- 完整的支出规则 — 在完全注册前的抽样、审批消息、收据 — 请参阅 [`../cargo-gtm/references/cost-discipline.md`](../cargo-gtm/references/cost-discipline.md)。

## 声明式替代方案：`defineMailbox` (CDK)

对于收件箱本身，**优先使用 CDK** — `mailbox create` 帮助文档就是这么说的，原因在于邮箱是长期存在的基础设施，具有月度成本，这正是应该放在 git 和可审查计划中的内容。`defineMailbox`（以及 `defineDomain` 用于发送域）涵盖了这一点；`adopt: true` 绑定的是在 Web 应用中购买的邮箱，而不是配置第二个。请参阅 [`../cargo-project/SKILL.md`](../cargo-project/SKILL.md) 和 [`../cargo/SKILL.md`](../cargo/SKILL.md) 中的“声明式 vs 命令式”。

使用此技能的命令式命令进行一次性配置，以及 CDK 完全未建模的所有内容：预热、允许、消息、线程、事件和抑制。

## 当 CLI 让你意外

如果文档中记录的标志或响应形状与你的观察结果不匹配，请重新刷新 CLI 和技能；如果仍然对不上，请提交报告 — 团队会阅读。缺少的 `domainManagement` 表面是一个活生生的例子：`mailbox create` 需要 `--domain-uuid`，而没有任何命令可以生成它。

```bash
cargo-ai workspaceManagement report create \
  --title "<一句话摘要>" \
  --description "<确切的命令、错误消息逐字、预期与实际、UUID>"
```

## 展示结果

遵循 [`../cargo/references/interaction.md`](../cargo/references/interaction.md)：以结果开头（“邮箱活跃，今天 12 次发送中有 8 次，自周一以来有 2 次回复”），将舰队或回复队列总结为紧凑的表格，并且永远不要将原始 `mailbox get` 或 `event list` JSON 倾倒到对话中。当你报告舰队时，报告其 **每月** 成本，而不是一次性成本。
