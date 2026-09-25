# OKX Outcomes CLI

通过外部 `okx-outcomes` 二进制文件（以前称为 OKX 预测市场 / `okx-predict`）进行二元结果（YES / NO）事件合约交易，在 `okx outcomes <command>` 下封装。

## 预检查

1. 运行 [`../_shared/preflight.md`](../_shared/preflight.md) **仅步骤 1**（主 CLI 自动升级）。步骤 2 和 3（OAuth/API 密钥检测、版本漂移）**不**适用——Outcomes 市场使用独立的凭证集。
2. 确认 `okx-outcomes` 二进制文件可访问：
   ```bash
   okx outcomes status
   ```
   如果你看到 `Error: okx-outcomes binary not found in PATH`，请先安装它（见先决条件）。

## 先决条件

```bash
# 1. 主 OKX CLI（提供 `okx outcomes` 包装命令）
npm install -g @okx_ai/okx-trade-cli

# 2. Outcomes 二进制文件
#    macOS / Linux:
curl -fsSL https://raw.githubusercontent.com/okx/outcomes-cli/main/install.sh | sh
#    Windows：从 https://github.com/okx/outcomes-cli/releases 下载 okx-outcomes.exe
#             并将其放置在你的 PATH 上。

# 3. 首次设置——登录 + 绑定钱包。
#    在真实终端中，你可以运行完整的交互式向导：
okx outcomes setup
#    在代理 / 聊天上下文中，逐步驱动它——见
#    “设置与引导”下方（完整的向导需要一个 TTY 并且不能从代理中启动）。

# 4. 验证
okx outcomes status
```

配置存储在 `~/.okx-outcomes/config.json`（非机密）和操作系统密钥环（机密；加密 `~/.okx-outcomes/keyring.enc` 回退）。**没有 `.env` 自动加载**——如果设置了 `PREDICTIONS_*` 环境变量，它们仅覆盖存储的值。

### 环境变量（可选覆盖）

| 变量 | 用于 | 备注 |
|---|---|---|
| `PREDICTIONS_AGENT_PRIVATE_KEY` | 链上写入（创建订单 / 取消 / ctf *） | secp256k1 十六进制。通常由 `okx outcomes setup` 生成并存储在密钥环中——这个环境变量仅**覆盖**它。**永远不要**分享或打印。 |
| `PREDICTIONS_API_BASE` | REST 主机覆盖 | 默认为设置期间选择的区域 |
| `OKX_OUTCOMES_BIN` | 二进制路径覆盖 | 对于本地开发构建很有用 |

> **安全**：**永远不要**在聊天中接受签名私钥。钱包由 `okx outcomes setup` / `setup bind` 创建并存储在密钥环中。如果用户无论如何都粘贴了密钥，请拒绝并告诉他们撤销 / 旋转它。

> **命名注意**：环境变量仍然使用 `PREDICTIONS_*` 前缀（上游遗留命名），即使在产品重新品牌为 OKX Outcomes 之后。

## 身份验证路径

Outcomes 市场使用 OKX **OAuth 登录**进行认证读取，并使用 **EIP-712 签名密钥**进行链上写入。这些**不**与主 `okx` CLI 的 OAuth / API 密钥流程相关——**不要**为 outcomes 调用 `okx auth login`；outcomes 有自己的 `okx outcomes auth login`。

| 操作类别 | 示例命令 | 凭证 |
|---|---|---|
| 公开数据 | `data events/event/market/ticker/candles`，`clob price/prices/midpoint/spread/book/books` | 无 |
| 认证读取 | `account balance/order/orders/positions/trades`（关闭 = `positions --status closed`），`search`，`status` | OAuth 会话（`okx outcomes auth login`） |
| 链上写入 | `clob create-order / market-order / cancel-oid / cancel-all / heartbeat`，`ctf split / merge / redeem`，`wallet show` | 签名密钥（密钥环 `agent_private_key`，或 `PREDICTIONS_AGENT_PRIVATE_KEY`） |

## 设置与引导

设置可以**完全从代理完成——无需终端**。用户只在**浏览器**中操作（打开一个 URL + 输入一个代码，并打开一个绑定**短链接**——这将在手机上启动 OKX 应用程序，或在任何浏览器中打开一个网络回退）；代理运行每个命令。

首次设置有**三个部分，按依赖顺序**：（1）区域，（2）OAuth 登录，（3）EOA 钱包绑定。使用以下方式检测进度：

```bash
okx outcomes setup status --json
# → { "region": {...}, "oauth": {...}, "eoa_binding": {...}, "next_step": "...", "complete": false }
```

然后推进 `next_step`：

1. **区域** — `okx outcomes setup region <global|us>`（非交互式；代理运行它）。
2. **OAuth 登录（设备代码）** — `okx outcomes auth login --manual --json`。这将打印一个包含 `{verificationUri, userCode, expiresIn}` 的单行信封，并且**立即退出**（它不会阻塞或读取 stdin）。将它传递给用户：*"在任何设备上打开 `<verificationUri>` 并输入代码 `<userCode>`（有效 ~N 分钟)."* 在他们通过浏览器授权后，使用 `okx outcomes auth refresh --json` 进行验证（在成功时写入会话标记）——几次后进行退避，或者在用户说他们完成后运行一次。
3. **钱包绑定** — `okx outcomes setup bind --json`（代理运行它）：生成签名钱包并打印钱包 `address` 以及一个**短链接**（JSON 输出中的 `deeplink` 字段）的形式 `https://okx.com/ul/3OauBX?eoa=<eoa>&uid=<uid>`（`eoa` 是新钱包的公共地址，`uid` 是登录的账户 ID——两者都由 CLI 填充）。**原样显示短链接**（不要缩短或包装它），并告诉用户三件事：（a）在他们的手机上点击它将启动 OKX 应用程序以批准绑定，（b）他们也可以将其复制到任何浏览器，以及（c）如果链接打不开，请复制上面显示的钱包 `address` 并在 OKX 应用程序中手动绑定：**Outcomes → Profile → Settings → API 绑定钱包**。要重新显示而不旋转钱包，请使用 `setup bind --keep`（普通的 `setup bind` 每次都会重新生成一个新鲜的钱包）。

   **显示模板** — 原样传递（中文）：

   ```
   我刚为你新生成了一个签名钱包(私钥保存在本地 keyring,永远不会展示)。
   请在手机上打开下面的短链接,在 OKX App 中批准绑定这个新钱包:

   新钱包地址:<address>
   绑定短链:<short link>

   (也可以把短链复制到浏览器打开。如果打不开,请复制上面的新钱包地址,
    在 OKX App 里手动绑定:Outcomes → Profile → Settings → API 绑定钱包,
    把钱包地址粘贴进去。)

   ⚠️ 关于这个钱包:
   • 它只用来给你的交易做签名授权,不是一个充值钱包。
   • 不要往这个地址转任何币 —— 余额在你的 OKX 账户里,转到这个地址的资金无法使用、大概率找不回。
   • 地址可以公开(用于绑定),但它背后的私钥永远不要外泄。

   在 App 中批准后告诉我。
   ```

   英文等效：

   ```
   I just generated a fresh signing wallet for you (the private key
   stays in the local keyring and is never displayed). Open this short
   link on your phone — it'll launch the OKX app to approve binding
   this new wallet:

   New wallet address: <address>
   Binding short link: <short link>

   (You can also copy the link into any browser. If the link won't open,
    copy the wallet address above and bind it manually in the OKX app:
    Outcomes → Profile → Settings → API Bind Wallet.)

   ⚠️ About this wallet:
   • It's only used to sign your trade authorizations — it is NOT a deposit wallet.
   • Do NOT send any crypto/tokens to this address. Your balance lives in your
     OKX account; funds sent here are unusable and likely unrecoverable.
   • The address is fine to share (it's used for binding), but the private key
     behind it must never be exposed.

   Tell me when you've approved it in the app.
   ```

   `address` 是公开的——安全显示。它背后的签名密钥永远不会离开本地密钥环。

在每一步后重新运行 `setup status --json`，然后 `okx outcomes status` 一旦 `complete: true`。

### 非 TTY / 代理环境

`okx outcomes` 包装器使用继承的 stdio 启动二进制文件，因此代理捕获的 stdout 接收每个命令的输出。所有每步设置命令都是**代理可运行**：

- ✅ **代理直接运行**：`setup status`，`setup region`，`auth login --manual --json`，`auth refresh`，`auth status`，`setup bind`（传递绑定短链接；用户在他们的手机上打开它或将其粘贴到浏览器中）。
- 🙋 **用户操作仅限于浏览器/手机**（永远不会是命令）：在浏览器中授权设备代码 URL；打开绑定短链接（手机上点击 → OKX 应用程序，或将其粘贴到浏览器中）；如果它打不开，请复制钱包地址并在 OKX 应用程序中手动绑定。
- 🚫 **永远不会从代理中启动**：完整的交互式 `okx outcomes setup` 向导和 `okx outcomes shell` REPL——两者都使用原始终端输入，如果没有 TTY 会挂起 / EOF 错误。使用上述每步子命令代替。

> 纯 `okx outcomes auth login`（没有 `--manual`）是真实终端上用户的交互式/浏览器前台变体；**代理必须使用 `--manual**`。

## 技能路由

- **YES/NO 事件合约 outcomes 市场** → 此技能
- **OKX CEX 上/下事件合约**（不同产品）→ `okx-cex-trade`（使用 `okx event ...`）
- **加密货币现货/掉期/期货/期权** → `okx-cex-trade`
- **加密货币市场数据**（价格、BTC/ETH 等蜡烛图）→ `okx-cex-market`
- **CEX 投资组合** → `okx-cex-portfolio`

## 快速入门

```bash
# 健康检查
okx outcomes status

# 浏览活动事件
okx outcomes data events --status active --limit 10

# 深入一个事件及其所有市场（每个市场返回 YES + NO 资产 ID）
okx outcomes data event-markets <eventId>

# YES 结果的实时价格
okx outcomes clob price --asset <yesAssetId>

# 顶托深度
okx outcomes clob book --asset <yesAssetId> --sz 5

# 我的账户余额 / 头寸
okx outcomes account balance
okx outcomes account positions

# 下达订单（始终先进行 dry-run — 见操作流程）
okx outcomes clob create-order --asset <assetId> --side buy --price 0.55 --size 100
```

> **标记放置**：在子命令后（`okx outcomes events --json`）或模块前（`okx --json outcomes events`）放置标记。`okx outcomes --json events`——模块和其子命令之间的标记楔入——不受支持。

## 命令索引

### 读取命令（无门控）

| # | 命令 | 身份验证 | 描述 |
|---|---|---|---|
| 1 | `okx outcomes data events [--status active] [--category <c>] [--limit <n>]` | 无 | 列出 outcomes 事件 |
| 2 | `okx outcomes data event <eventId>` | 无 | 单个事件详情 |
| 3 | `okx outcomes data event-markets <eventId>` | 无 | 事件 + 及其所有市场（包括 YES/NO 资产 ID） |
| 4 | `okx outcomes data market <marketId>` | 无 | 单个市场详情 |
| 5 | `okx outcomes data trending` | 无 | 趋势事件 |
| 6 | `okx outcomes data ticker <assetId>` | 无 | 一个 outcomes 资产的 24 小时蜡烛图 |
| 7 | `okx outcomes data candles <assetId> [--bar 1H] [--limit 100]` | 无 | OHLCV 蜡烛图 |
| 8 | `okx outcomes search <keyword>` | OAuth | 关键字搜索 |
| 9 | `okx outcomes clob price --asset <id> [--outcome yes\|no]` | 无 | 修剪价格（最后/买价/卖价/中间价/价差） |
| 10 | `okx outcomes clob prices <id1> <id2> ...` | 无 | 批量价格查看 |
| 11 | `okx outcomes clob midpoint --asset <id>` / `clob midpoints <ids...>` | 无 | (买价+卖价)/2 |
| 12 | `okx outcomes clob spread --asset <id>` / `clob spreads <ids...>` | 无 | 买价/卖价价差 |
| 13 | `okx outcomes clob book --asset <id> [--sz <n>]` / `clob books <ids...>` | 无 | 多级深度（默认 sz=10，最大 400） |
| 14 | `okx outcomes account balance` | OAuth | 账户余额 |
| 15 | `okx outcomes account order <orderId>` | OAuth | 单个订单详情 |
| 16 | `okx outcomes account orders` | OAuth | 开放订单 |
| 17 | `okx outcomes account positions` | OAuth | 开放头寸（寻找状态="Won" → 兑换） |
| 18 | `okx outcomes account positions --status closed` | OAuth | 关闭头寸 + 实现的 PnL |
| 19 | `okx outcomes account trades` | OAuth | 交易历史 |
| 20 | `okx outcomes wallet show` | 签名 | 推导钱包地址 |
| 21 | `okx outcomes status` | OAuth | 健康检查 |
| 22 | `okx outcomes auth status [--json]` | 无 | OAuth 会话状态 |
| 23 | `okx outcomes setup status [--json]` | 无 | 引导进度（区域/oauth/绑定） |

### 设置 / 身份验证命令

| 命令 | 身份验证 | 描述 | 代理可运行？ |
|---|---|---|---|
| `okx outcomes setup region <global\|us>` | 无 | 设置区域（步骤 1） | ✅ 是 |
| `okx outcomes auth login --manual --json` | 无 | OAuth 设备代码（步骤 2）：打印 `{verificationUri,userCode,expiresIn}` 并退出 | ✅ 是（将 URL+代码传递给用户） |
| `okx outcomes auth refresh [--json]` | 无 | 用户授权后验证/刷新会话（写入会话标记） | ✅ 是 |
| `okx outcomes setup bind [--keep] --json` | 签名 | 绑定 EOA 钱包（步骤 3）：打印地址 + 一个**短链接**（JSON 输出的 `deeplink` 字段，`https://okx.com/ul/3OauBX?eoa=…&uid=…`）；`--keep` 重用现有钱包 | ✅ 是（用户打开短链接，或复制地址到浏览器手动绑定） |
| `okx outcomes auth login --site <global\|us>` | 无 | 交互式/浏览器前台登录（用于真实终端上的用户） | 🚫 需要一个 TTY |
| `okx outcomes setup` / `okx outcomes shell` | — | 完整的交互式向导 / REPL | 🚫 需要一个 TTY |

### 写入命令（需要 dry-run 预览 + 用户确认）

| # | 命令 | 风险 |
|---|---|---|
| 24 | `okx outcomes clob create-order --asset <id> --side buy\|sell --price --size [--tif gtc\|gtd\|ioc\|fok\|alo] [--expiry <ms>] [--size-type base\|quote]` | 高 |
| 25 | `okx outcomes clob market-order --asset <id> --side buy\|sell --size [--tif ioc\|fok] [--size-type base\|quote]` | 高（立即交叉） |
| 26 | `okx outcomes clob cancel-oid --oid <id> --asset <id>` | 中等 |
| 27 | `okx outcomes clob cancel-all` | 高 |
| 28 | `okx outcomes clob heartbeat` | 中等（5 分钟死线自动取消所有） |
| 29 | `okx outcomes ctf split --market <id> --amount <xp>` | 高（锁定 xp） |
| 30 | `okx outcomes ctf merge --market <id> --amount <xp>` | 高 |
| 31 | `okx outcomes ctf redeem --market <id>` | 高（燃烧全部获胜余额） |

> 别名：`clob order/orders/trades` 委托给相应的 `account *` 命令。在技能输出中优先使用 `account *` 以提高清晰度。

## 操作流程

### 步骤 0 — 二进制检查

```bash
okx outcomes status --json
```

- 如果包装器打印 "okx-outcomes binary not found"，**停止**并告诉用户通过 `curl -fsSL https://raw.githubusercontent.com/okx/outcomes-cli/main/install.sh | sh` 安装。
- 如果 `status` 返回身份验证错误，用户未登录——检查 `okx outcomes auth status --json` 并指导他们完成“设置与引导”(`auth login`)。

### 步骤 1 — 确定正在请求什么

- 公开数据 → 直接运行命令。
- 认证读取 → 检查用户是否登录 (`okx outcomes auth status --json`)；否则路由到“设置与引导”。
- 链上写入 → 进行步骤 2 dry-run。

### 步骤 2 — 写入 dry-run 预览（强制）

在执行任何 `clob create-order` / `clob market-order` / `clob cancel-*` / `clob cancel-all` / `ctf *` 命令之前，**首先**渲染 dry-run 摘要：

```
即将执行: okx outcomes clob create-order --asset 100888000 --side buy --price 0.55 --size 100

  市场           : "Will BTC be above $100k by Dec 31, 2026?"  (mkt_t001)
  资产            : 100888000  (YES 结果)
  侧             : buy
  价格            : 0.55 xp
  数量            : 100 股份
  TIF              : gtc
  预计名义值       : 55.00 xp
  钱包           : 0x1234...abcd                              (来自 `wallet show`)
  可用 (现货): 1,234.56 xp                               (来自 `account balance`)

回复 "confirm" 执行, 或 "cancel" 取消.
```

摘要字段：
- **市场标题** — 通过 `okx outcomes data market <marketId>` 获取（查找 `marketId` 从资产的父母市场）
- **资产 + 结果** — 从 `event-markets <eventId>` 获取的数字 `assetId` 加上它代表的结果（YES / NO）
- **名义值** — `price * size` (xp)
- **钱包** — `okx outcomes wallet show --json`
- **可用余额** — `okx outcomes account balance --json` → `oddsType="spots"`，`available` 字段

只有在用户回复 `confirm` 后才运行真实命令。如果任何其他内容（包括沉默），则取消。

### 步骤 3 — 执行 & 验证

执行后，立即验证状态：

```bash
okx outcomes account orders --json    # 确认订单已放置 / 已取消
okx outcomes account positions --json # 确认头寸变化（对于 ctf）
```

向用户报告结果订单 ID / tx hash。

## CLI 命令参考

每个命令组的详细参数表和示例：

- [`references/setup-auth.md`](references/setup-auth.md) — setup status/region/bind, auth login/refresh/status, config & keyring storage, non-TTY rules
- [`references/data-commands.md`](references/data-commands.md) — events / event / market / trending / ticker / candles / search
- [`references/account-commands.md`](references/account-commands.md) — account balance / orders / positions / trades
- [`references/clob-commands.md`](references/clob-commands.md) — clob price / order / orders / trades / create-order / cancel / cancel-all / heartbeat
- [`references/ctf-commands.md`](references/ctf-commands.md) — ctf split / merge / redeem
- [`references/workflows.md`](references/workflows.md) — first-time setup / daily brief / event deep-dive / portfolio check / safe place-order / resolve-and-redeem

## MCP 工具参考

此模块在当前发布中**不暴露任何 MCP 工具**。代理直接通过 Bash 调用 `okx outcomes <command>`。outcomes 团队可能独立提供未来的 MCP 服务器。

## 边缘情况

- **`okx-outcomes` 不在 PATH 中**：包装器打印安装提示并退出 127。告诉用户运行 `curl -fsSL https://raw.githubusercontent.com/okx/outcomes-cli/main/install.sh | sh`。
- **签名钱包缺失**：任何 `clob create-order` / `market-order` / `ctf *` 都会失败。运行 `okx outcomes setup bind --json`（代理可运行），传递绑定**短链接**（JSON 输出的 `deeplink` 字段，`https://okx.com/ul/3OauBX?eoa=…&uid=…`），并让用户打开它（手机上点击 → OKX 应用程序，或复制到浏览器中）；如果链接打不开，让他们复制钱包地址并在 OKX 应用程序中手动绑定（**Outcomes → Profile → Settings → API 绑定钱包**）——永远不要在聊天中要求密钥。
- **资产 ID 与市场 ID 搞混**：最常见的错误类别。`clob price/book/create-order/market-order` 需要 `assetId`；`ctf *` 和 `account trades --market` 需要 `marketId`。不确定时，首先运行 `event-markets <eventId>`——其输出生成 YES + NO 资产 ID。
- **没有 `--expiry` 的 `--tif gtd`**：客户端拒绝。将它们配对或默认为 `gtc`。
- **`--size-type quote` 在 `buy + ioc` 外**：客户端拒绝 (`create-order`)。提前告诉用户“花费 N 点”语法需要 buy + IOC。
- **从快照被拒绝的 FOK**：当可见深度不足时，`clob market-order --tif fok` 客户端拒绝（未发送签名消息）。显示拒绝并建议减少 `--size` 或使用 `--tif ioc`。
- **模式混淆**：outcomes 市场没有 demo / live 标记。在注册时选择网站。注意用户所在的部署（主网 vs 测试网）——`okx outcomes status` 会报告它。

## 全局说明

- **始终传递 `--json`** 当将其传递到其他工具或总结时——包装器如果用户全局处于 `--json` 模式，会自动附加 `--json`。
- **值的单位**：outcomes 市场以 **点 (xp)** 进行交易，而不是 USDC。所有余额、价格（十进制 `[0,1]`），名义值和 CTF 金额都是 xp。
- **私钥处理**：**永远不要**将 `PREDICTIONS_AGENT_PRIVATE_KEY`（或任何 `0x` 后跟 64 个十六进制字符）回显到聊天中。如果你必须引用它，请将其掩码为 `0x****`。不要写入内存。
- **侧是小写**：`--side buy` / `--side sell`（写入命令）。`account trades --side` 接受 `BUY` / `SELL`（大写）——这种不一致是上游的，请遵循每个命令的签名。
- **速率限制**：认证端点遵循 OKX 风格的限流。在 `429` / 速率限制错误时，退避并在建议的等待时间后重试。
- **包装器是透明的**：每个 `okx outcomes <cmd>` 都会原样转发到 `okx-outcomes`。有关规范二进制文档，请参阅 [`okx/outcomes-cli docs/cli-reference.md`](https://github.com/okx/outcomes-cli/blob/main/docs/cli-reference.md)。
- **`OKX_OUTCOMES_BIN`** 环境变量可以覆盖二进制路径（对于本地开发使用 `cargo build --release` 产物很有用）。
