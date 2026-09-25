# OKX 增长竞赛 — 交易竞赛

仅限 Agent Wallet 的交易竞赛。全生命周期按专注参考进行划分：

- **参与**（发现 / 注册 / 交易 / 已注册钱包 / 导出守卫）— `references/participation.md`
- **详情**（规则 / 奖金池 / 四个奖励部分）— `references/details.md`
- **排名**（排行榜 / 我的排名与 CASE 1/2/3 模板）— `references/rank.md`
- **领取**（奖励状态检查 / 原子领取 / 联系信息收集）— `references/claim.md`
- **CLI 参考**（命令、参数、返回模式）— `references/cli-reference.md`

此 SKILL.md 包含 **全球规则**（事实、身份不变量、路由、输出规则、时间格式、状态码、错误处理），所有参考都依赖于这些规则。始终先阅读此文件；然后根据用户的意图跳转到匹配的参考。

## 每个 Agent Wallet 竞赛的事实

当用户询问竞赛如何运作时，将以下内容视为 **事实真相**。两个与链相关的字段扮演 **明确、不重叠的角色** — 切勿混淆它们：

- `chainId` — 单一 ID。**仅限领取 / 奖励链**（奖励在此链上支付；其合约地址在此处）。它不是交易链，除非它也出现在 `participateChainIds` 中。
- `participateChainIds` — 由 **`list` 和 `detail` 端点都返回的 ID 数组**。**交易链集**。此列表中任何链上的交易都计入同一竞赛排名。

**交易链集 = `participateChainIds`。领取链 = `chainId`。** 这两个是不同的概念；以下显示规则永远不会将它们合并。

1. **链 ID → 显示名称** 映射。目前支持的竞赛链：`1 → Ethereum`，`196 → X Layer`，`501 → Solana`。
2. 在检查 `participateChainIds` 之前，切勿告诉用户“您的链不被计算在内”。
3. `myRankInfo.userTotal = 0` 表示用户尚未达到合格门槛或后端指标管道尚未收集到他们的交易 — 这 **不** 表示用户的链不受支持。
4. `competition_rank` 接受一个可选的 `wallet`。省略它以进行自我排名 — 工具发送您的 `accountId`（涵盖 `participateChainIds` 中的所有链；无链选择）。仅当查询他人的排名时才传递显式地址；地址链族（EVM `0x...` 否则 Solana）必须与活动的主链匹配，否则工具将拒绝调用（无静默错链查询）。

## 身份解析不变量

`competition_rank` 和 `competition_user_status` 的查询身份 **互斥**：后端接受 `accountId`（自我）或 `walletAddress`（跨用户）中的任意一个 — 永远不会同时接受两者。关于“您使用了哪个身份？”的答案是从调用形状 **确定** 的。

| 调用形状 | 发送的身份 |
|---|---|
| `competition_user_status` (任何) | `accountId` — 一次涵盖 `participateChainIds` 中的所有链 |
| `competition_rank` 不带 `wallet` | `accountId` |
| `competition_rank` 带 `wallet=<addr>` | `walletAddress` — 工具验证 addr 的链族（EVM `0x...` 否则 Solana）与活动的 `chainId` 匹配；不匹配 → 拒绝 |
| `competition_claim` (预检查) | `accountId` |

对于多活动 `competition_user_status`（无 `activity_name`），相同的 `accountId` 跨所有活动重复使用 — 后端按 accountId 进行连接。

## 强制阅读顺序

**在生成任何关于竞赛的用户界面消息之前，您必须首先定位到以下正确的参考文件中的匹配部分，并遵循其固定的模板结构。** 不要即兴创作格式。不要缩短模板。不要省略部分或合并它们。模板是产品强制的文本（参与 / 技能质量措辞、免责声明）并且不得进行释义。

模板 **结构是固定的**；**语言跟随用户** — 见下文的 `## 输出语言` 规则。当用户使用中文时，将模板字符串翻译为自然中文。当用户使用英文时，使用英文原文。占位符（包括来自 `{supportedChains}` 的链显示名称）保持不变。

快速路由（用户意图 → 参考文件 + 部分）：

| 用户意图 | 参考文件 | 部分 |
|---|---|---|
| “列出竞赛 / 显示可用竞赛” | `references/participation.md` | 步骤 1 — 发现 |
| “显示详情 / 显示规则 / 显示奖金池” | `references/details.md` | 步骤 2 — 查看详情 |
| “注册 / 加入” | `references/participation.md` | 步骤 3 — 加入 |
| “替我交易” | `references/participation.md` | 步骤 4 — 交易（委托给 okx-agentic-wallet） |
| “排行榜 / 完整排行榜 / 谁在获胜” | `references/rank.md` | 检查排行榜（完整排行榜） |
| “我的排名 / 我的名次是什么 / 我在奖金区吗” | `references/rank.md` | 检查用户的自我排名（跨所有排行榜） |
| “显示已注册钱包” | `references/participation.md` | 查询已注册钱包 |
| “导出钱包” | `references/participation.md` | 钱包导出守卫 |
| “检查我的状态 / 我是否赢了” | `references/claim.md` | 检查参与状态 |
| “领取奖励 / 领取我的奖品” | `references/claim.md` | 步骤 6 — 领取奖励 |
| 顶级获胜者联系后续（领取后 `needContact: true`） | `references/claim.md` | 联系信息收集（仅限顶级获胜者） |

如果用户的意图没有明确映射到以上任何一个，请在回复前询问他们的意图 — 不要创作自由格式。

## 预飞行检查

> 阅读 `../okx-agentic-wallet/_shared/preflight.md`。如果缺失，请阅读 `_shared/preflight.md`。

**跨技能在常见错误上的路由**：
- `未登录` → 引导用户完成 `okx-agentic-wallet` 登录流程（运行 `onchainos wallet login`），然后重试原始操作。
- 后端状态码（`--status` 过滤器 / `status` / `joinStatus` / `rewardStatus`）和错误代码消息（`11002` / `11003` / `11008` / `1860402` / `地址限制达到` / `Sui-chain` / 区域封锁 / `不符合资格`）：见 `references/cli-reference.md`。

## 命令索引

所有 MCP 工具都镜像 CLI；MCP 变体接受 `activity_name`（服务器解析 ID）并自动解析 `accountId` / 钱包地址来自活动会话。完整的标志表和返回形状：`references/cli-reference.md`。

| # | 命令 | 认证 | 描述 |
|---|---------|------|-------------|
| 1 | `onchainos competition list [--status 0\|1\|2] [--page-size N] [--page-num N]` | 无 | 列出竞赛（默认 `status=0`，仅活动状态） |
| 2 | `onchainos competition detail --activity-id <id>` | 无 | 规则、奖金池、链、时间线 |
| 3 | `onchainos competition rank --activity-id <id> [--wallet <addr>] --sort-type <type> [--limit N]` | 无 | 排行榜 + 用户排名。见 `references/rank.md` 关于自我/跨用户语义和 `sort-type` 发现。 |
| 4 | `onchainos competition user-status [--activity-id <id>]` | 钱包登录 | 参与 & 奖励状态（省略 `--activity-id` 用于所有活动） |
| 5 | `onchainos competition join --activity-id <id> --evm-wallet <addr> --sol-wallet <addr> --chain-index <chain_id>` | 钱包登录 | 注册活动中的活跃账户 |
| 6 | `onchainos competition claim --activity-id <id> --evm-wallet <addr> --sol-wallet <addr>` | 钱包登录 | 原子领取 — 在调用内签名 + 广播。见 `references/claim.md`。 |
| 7 | `onchainos competition submit-contact --activity-id <id> --contact-type <Telegram\|WeChat\|Email\|Twitter> --contact-value <text>` | 钱包登录 | 为顶级获胜者记录联系信息；仅领取后 `needContact: true`。见 `references/claim.md`。 |

`--status`（请求过滤器）：`0`=活动，`1`=已结束，`2`=全部
`activityStatus`（响应字段）：**`3`=活动，`4`=已结束** — 与请求过滤器不同

## 输出规则

> **内部 ID 与用户界面显示**。内部数字 ID（`activityId`，`chainIndex`，`accountId`）在工具响应中有意返回 — 它们需要用于工具之间的调用链（例如，在 `competition_join` 成功后，您可能需要使用活动 ID 调用 `competition_detail` 以填充成功模板）。**将它们保留在数据层；永远不要在用户可见消息中渲染它们。**

**在任何情况下，以任何格式都不要在为用户生成的消息中包含任何内部 ID。** 仅通过 `activityName`（如果名称不可用，则使用 `shortName`）专门向用户标识活动。

**禁止的用户可见模式**（不要生成类似此模式的输出）：
- `Agent Trading Contest (#107)`
- `#106 (agenticwallettest1)`
- 任何暴露活动 ID 的列、行或内联参考（例如 `competition 107`，ID 列，标记的 `Activity ID` 行） — 相同规则，无论标签、形状或语言如何。

**正确的用户可见模式**：
- `Agent Trading Contest`
- 当有两个同名活动时，区分它们，附加 `chainName`（例如 `Agent Trading Contest (Solana)`），永远不要附加 ID。

**幕后（允许且预期）**：
- 从 `competition_user_status` / `competition_join` 响应中读取 `activityId` 并传递给 `competition_detail` 以获取固定模板所需的数据。
- 任何工具到工具的调用链通过数字 ID — 只要最终用户界面消息省略它们。

当用户要求对特定活动采取行动时（例如，“领取 Agent Trading Contest”），MCP 工具 `competition_claim` / `competition_join` 接受 `activity_name` 并在服务器端解析 ID，因此您也可以直接使用名称，而无需自行查找。

## 输出语言

**在用户的对话语言中渲染每个固定模板。** 模板结构（部分、顺序、编号项目、表格列数、占位符位置、`{supportedChains}` 占位符以及 `[Disclaimer: ...]` 块）是固定的，并且不得更改。只有内部自然语言文本被翻译为用户的语言。

**占位符永远不会被翻译。** `{supportedChains}`，`{chainName}`，`{rewardUnit}`，`{txHash}`，`{accountName}` 等 API 值按原样填充 — 不要本地化它们。链显示名称（例如 `Solana`，`X Layer`，`Base`）来自规范 ID → 名称映射，并在每种语言中保持不变。

## 交付前检查清单

发送前的最终检查 — 涵盖参考文件必须遵守的容易在长响应后遗漏的规则。（规则已在之前的部分中覆盖 — 内部 ID，`participateChainIds`，`*Formatted`，语言/模板保真度 — 在此处不再重复；通过遵循其各自部分的规则来验证它们。）

- [ ] 成功注册响应 → `[Disclaimer: 数字资产交易涉及风险。 ...]` 行单独位于末尾。 (→ `participation.md` → 成功注册)
- [ ] 领取运行时失败（签名 / 广播 / 网络）→ 添加 3 点式失败建议块。在预检查拒绝（`rewardStatus` 0/2/3/4，代码 11002，代码 11008）→ **省略**建议块。 (→ `claim.md` → 固定失败建议块)
- [ ] 在调用 `competition_claim` 之前 → 渲染了预领取预览行（`您即将领取 {rewardAmount} {rewardUnit} 在 {chainName}。回复 "confirm" 继续。`）并且用户回复了明确的确认。 (→ `claim.md` → 预领取预览)
