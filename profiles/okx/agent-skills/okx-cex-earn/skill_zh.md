# OKX CEX Earn CLI

## 预检查

在运行任何命令之前，请遵循 [`../_shared/preflight.md`](../_shared/preflight.md)。
使用此文件的前置信息中的 `metadata.version` 作为步骤 2 的参考。

## 前置条件

1. 安装 `okx` CLI：
   ```bash
   npm install -g @okx_ai/okx-trade-cli
   ```
2. 配置凭证：
   ```bash
   okx config init   # 选择站点 -> 按照浏览器 OAuth 流程
   ```
3. 验证：`okx earn savings balance`

> **安全提示**：切勿在聊天中接受凭证。指导用户使用 `okx config init` 进行设置。

---

## 凭证与配置文件检查

在任何经过身份验证的命令之前运行**两个**命令——`okx auth status --json` 的 `apiKey` 字段是身份验证二进制文件的内部状态，无论 `~/.okx/config.toml` 是否有 API 密钥配置文件，它始终为 `false`。`okx config show --json` 是 API 密钥存在的唯一权威来源。身份验证方法在 [预检查](../_shared/preflight.md) 步骤 2 中检测到，并会记住会话中的状态。

```bash
okx config show --json      # 揭示 API 密钥配置文件 (TOML 配置)
okx auth status --json      # 揭示 OAuth 会话状态 (身份验证二进制文件状态)
```

按**此顺序**应用——第一个匹配项生效：

- `config show --json` 包含非空的 `api_key` 字段的任何配置文件 → **API 密钥模式**。继续。
- 没有 API 密钥配置文件**并且** `auth status --json` 返回 `"status":"logged_in"` → **OAuth 模式**。继续。
- 没有 API 密钥配置文件**并且** `"status":"pending"` — 登录正在进行中，等待其完成。
- 没有 API 密钥配置文件**并且** `"status":"not_logged_in"` — **停止**，加载 `okx-cex-auth` 技能并按照登录步骤操作，等待完成。

OKX Earn 不支持模拟模式。始终使用静默模式（实时模式）——除非出现错误，否则不要提及它。
- **API 密钥用户**：使用 `--profile <live-profile>`（没有 `demo=true` 的配置文件）。
- **OAuth 用户**：无需标志（实时模式是默认模式）。

**遇到身份验证错误（401 / "会话过期" / "先运行 `okx auth login`"）：** 立即停止，加载 `okx-cex-auth` 技能并按照重新身份验证步骤操作，然后重试。

---

## 技能路由

| 用户意图 | 路由到技能 |
|---|---|
| 市场价格、行情、K 线图 | `okx-cex-market` |
| 现货/掉期/期货/期权订单 | `okx-cex-trade` |
| 账户余额、持仓、转账 | `okx-cex-portfolio` |
| 网格 / DCA 交易机器人 | `okx-cex-bot` |
| 简易赚、闪赚、链上赚、双币赢，或自动赚币 | **此技能** |

---

## 命令索引

### earn savings — 简易赚（10 个命令）

| 命令 | 类型 | 身份验证 | 描述 |
|---|---|---|---|
| `earn savings balance [ccy]` | 读取 | 需要 | 赚款余额（所有或特定货币）。还获取定期订单以获取完整视图。 |
| `earn savings purchase --ccy --amt [--rate]` | 写入 | 需要 | 订阅资金到简易赚（活期） |
| `earn savings redeem --ccy --amt` | 写入 | 需要 | 从简易赚（活期）赎回资金 |
| `earn savings set-rate --ccy --rate` | 写入 | 需要 | 设置最低借贷利率 |
| `earn savings lending-history` | 读取 | 需要 | 用户的个人借贷记录及收益详情 |
| `earn savings rate-history` | 读取 | 需要 | 简易赚借贷利率和定期产品（需要身份验证） |
| `earn savings fixed-products [--ccy]` | 读取 | 需要 | 浏览可用的定期（定期）产品，包括年化利率、期限、剩余配额和售罄状态 |
| `earn savings fixed-orders [--ccy] [--state]` | 读取 | 需要 | 查询定期（定期）订单。状态：待处理/收益/过期/结算/取消 |
| `earn savings fixed-purchase --ccy --amt --term [--confirm]` | 写入 | 需要 | 订阅简易赚定期（定期）。没有 `--confirm`：仅预览 |
| `earn savings fixed-redeem --reqId <reqId>` | 写入 | 需要 | 赎回定期订单（全额）。仅 `pending` 状态订单可以提前赎回 |

有关完整命令语法、利率字段语义和确认模板，请阅读 `{baseDir}/references/savings-commands.md`。

### earn dcd — 双币赢（6 个命令）

| 命令 | 类型 | 身份验证 | 描述 |
|---|---|---|---|
| `earn dcd pairs` | 读取 | 需要 | 可用的 DCD 货币对 |
| `earn dcd products` | 读取 | 需要 | 活跃产品及过滤器 |
| `earn dcd quote-and-buy --productId --sz --notionalCcy` | 写入 | 需要 | 原子订阅：报价 + 执行一步完成 |
| `earn dcd order --ordId` | 读取 | 需要 | 快速检查单个订单的状态 |
| `earn dcd orders` | 读取 | 需要 | 完整订单列表/历史记录 |
| `earn dcd redeem-execute --ordId` | 写入 | 需要 | 两步提前赎回：预览然后执行 |

> DCD 不支持模拟/模拟交易模式。始终使用实时模式（API 密钥：`--profile <live-profile>`；OAuth：无需标志）。

有关完整命令语法、产品概念和错误代码，请阅读 `{baseDir}/references/dcd-commands.md`。

### earn onchain — 链上赚（6 个命令）

| 命令 | 类型 | 身份验证 | 描述 |
|---|---|---|---|
| `earn onchain offers` | 读取 | 需要 | 可用的质押/DeFi 产品 |
| `earn onchain purchase --productId --ccy --amt` | 写入 | 需要 | 订阅链上产品 |
| `earn onchain redeem --ordId --protocolType` | 写入 | 需要 | 赎回链上投资 |
| `earn onchain cancel --ordId --protocolType` | 写入 | 需要 | 取消待处理的链上订单 |
| `earn onchain orders` | 读取 | 需要 | 活跃的链上订单 |
| `earn onchain history` | 读取 | 需要 | 历史链上订单 |

有关完整命令语法和参数，请阅读 `{baseDir}/references/onchain-commands.md`。

### earn auto-earn — 自动赚币（3 个命令）

| 命令 | 类型 | 身份验证 | 描述 |
|---|---|---|---|
| `earn auto-earn status [CCY]` | 读取 | 需要 | 查询支持自动赚币的货币及其状态 |
| `earn auto-earn on <CCY>` | 写入 | 需要 | 为某种货币启用自动赚币 |
| `earn auto-earn off <CCY>` | 写入 | 需要 | 为某种货币禁用自动赚币 |

> **24 小时限制**：在启用后的 24 小时内无法禁用（API 硬限制）。在启用之前始终提醒用户。

有关完整命令语法、earnType 推断规则和 MCP 工具参考，请阅读 `{baseDir}/references/autoearn-commands.md`。

### earn flash-earn — 闪赚（1 个命令）

| 命令 | 类型 | 身份验证 | 描述 |
|---|---|---|---|
| `earn flash-earn projects [--status <0\|100\|0,100>]` | 读取 | 需要 | 按状态浏览闪赚项目。`0`=即将开始，`100`=进行中，默认为两者 |

---

## 操作流程

### 步骤 0 — 凭证与配置文件检查

在任何经过身份验证的命令之前：参见 [凭证与配置文件检查](#credential--profile-check)。始终使用实时模式静默操作。

### 步骤 1 — 确定赚币意图

**简易赚灵活（活期）：**
- 查询余额 / 历史 / 利率 → 读取命令，直接继续。
- 订阅 / 赎回 / 设置利率 → 写入命令，转到步骤 2。

**简易赚定期（定期）：**
- 浏览可用产品 / 检查配额 → `earn savings fixed-products [--ccy]`。这是查询定期产品池的专用工具——每当用户询问可用的定期赚币产品、剩余配额或年化利率时，都使用它。
- 查询用户的现有订单 → `earn savings fixed-orders [--ccy] [--state]`。
- 订阅（两步：预览然后确认） / 赎回（仅 `pending` 状态）→ 写入命令，转到步骤 2。阅读 `{baseDir}/references/savings-commands.md` 获取执行前检查清单和确认模板。
- 对于多步骤工作流（预览订阅、提前赎回），请阅读 `{baseDir}/references/workflows.md`。

**链上赚：**
- 查询报价 / 订单 / 历史 → 读取命令，直接继续。
- 订购 / 赎回 / 取消 → 写入命令，转到步骤 2。

**自动赚币：**
- 查询自动赚币状态 → 读取，直接继续。
- 启用 / 禁用自动赚币 → 写入，转到步骤 2。阅读 `{baseDir}/references/autoearn-commands.md` 获取确认模板和 earnType 推断。

**闪赚：**
- 浏览项目 → 读取，直接继续。
- 使用 `--status 0` 查询即将开始的项目，`--status 100` 查询进行中的项目，或省略标志以查看两者。

当用户询问查看“赚币持仓”或“赚币持仓”（无论他们是否明确提及 DCD），同时查询所有持有配置文件的子模块（闪赚仅查询，无持仓）：

```bash
okx earn savings balance --json        # 简易赚灵活（活期）
okx earn savings fixed-orders --json   # 简易赚定期（定期）
okx earn onchain orders --json         # 链上赚
okx earn dcd orders --json             # 双币赢
```

仅显示实际持有配置文件的章节。对于 DCD：使用 `{baseDir}/references/dcd-commands.md` 中的表格翻译状态代码。

**双币赢（DCD / 双币赢）：**
- 浏览产品 / 对 → 读取；当用户指定一种货币时，请阅读 `{baseDir}/references/workflows.md`（DCD 浏览流程）以获取在渲染产品表格之前必须并行预取的必要步骤
- 订阅（报价并购买）→ 写入 → 参见 `{baseDir}/references/workflows.md`（DCD 订阅流程）
- 提前赎回 → 写入 → 参见 `{baseDir}/references/workflows.md`（DCD 提前赎回流程）

对于多步骤工作流（闲置资金分析、订阅 + 验证、赎回 + 转账、链上订阅），请阅读 `{baseDir}/references/workflows.md`。

### 步骤 2 — 确认写入操作

对于所有写入命令，显示摘要并等待明确确认。

> "直接搞" / "直接搞" 不是有效确认——用户必须先看到摘要。

有关简易赚确认对话框格式，请阅读 `{baseDir}/references/savings-commands.md`。有关链上确认，请阅读 `{baseDir}/references/onchain-commands.md`。

### 步骤 3 — 执行并验证

在任何购买之后，根据产品类型进行验证：
- **DCD** `quote-and-buy` 成功 → 运行 `earn dcd orders --json`，仅显示匹配的订单。
- **链上** 购买（响应包含 `ordId`）→ 运行 `earn onchain orders --json`，仅显示匹配的订单。
- **简易赚灵活** 购买（响应中不包含 `ordId`）→ 运行 `earn savings balance --ccy <ccy> --json`。
- **简易赚定期** 购买 → 运行 `earn savings fixed-orders --ccy <ccy> --state pending --json`，显示新订单。

**简易赚灵活购买**：并行运行——`earn savings balance --ccy <ccy>` 和 `earn savings rate-history --ccy <ccy> --limit 1 --json`。有关输出格式，请阅读 `{baseDir}/references/savings-commands.md`。

**简易赚灵活赎回**：运行 `earn savings balance --ccy <ccy>` 以确认更新后的余额。通知用户资金已返回到资金账户。

**简易赚定期购买**：运行 `earn savings fixed-orders --ccy <ccy> --state pending --json` 以确认已创建订单。显示订单详情，包括年化利率、期限和预期到期日期。

**简易赚定期赎回**：运行 `earn savings fixed-orders --json` 以确认订单状态已更改为 `cancelled`。通知用户全部本金已返回到资金账户——提前取消不产生利息。

**链上赎回**：查询 `earn onchain orders` 以确认状态。显示 `estSettlementTime` 作为预计到达时间。

**链上取消**：提交后查询 `earn onchain orders`：
- 订单已从列表中消失 → 通知用户：取消完成，资金已返回到资金账户。
- `state: 3`（取消中）→ 通知用户：取消正在进行中，资金将很快返回到资金账户。

---

## 全局说明

- **安全提示**：切勿要求用户将 API 密钥或秘密粘贴到聊天中。
- **输出**：始终将 `--json` 传递给列表/查询命令，并将结果作为 Markdown 表格呈现——切勿粘贴原始终端输出。
- **网络错误**：如果命令因连接错误而失败，提示用户检查 VPN：`curl -I https://www.okx.com`
- **语言**：始终使用用户的语言进行响应。

有关数字/时间格式和响应结构约定，请阅读 `{baseDir}/references/templates.md`。
