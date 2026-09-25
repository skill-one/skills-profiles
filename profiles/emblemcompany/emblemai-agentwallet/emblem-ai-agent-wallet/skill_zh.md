# Emblem Agent Wallet

连接到 **EmblemAI** —— EmblemVault 的自主加密 AI，跨越 7 条区块链提供 250 多种交易工具。浏览器认证、流式响应、基于配置文件的范围本地状态、插件系统以及零配置代理模式。

**需要 CLI**：`npm install -g @emblemvault/agentwallet`

---

## 快速入门 —— 如何使用此技能

**步骤 1：安装 CLI**

```bash
npm install -g @emblemvault/agentwallet
```

这提供了一个单一命令：`emblemai`

**步骤 2：使用它**

当此技能加载时，您可以询问 EmblemAI 任何关于加密货币的问题：

- "我的钱包地址是什么？"
- "显示我在所有链上的余额"
- "Solana 上有什么趋势？"
- "将 $20 的 SOL 兑换为 USDC"
- "将 0.1 ETH 发送到 0x..."

对于零配置代理配置，一个配置文件可以创建并持久化自己的钱包，只需一个命令：

```bash
emblemai --agent --profile hustle -m "我的钱包地址是什么？"
```

**要调用此技能，可以说：**
- "使用我的 Emblem 钱包检查余额"
- "询问 EmblemAI 我拥有的代币"
- "连接到 EmblemVault"
- "检查我的加密货币投资组合"
- "创建或使用我的代理钱包配置文件并显示我的地址"

所有请求都在底层通过 `emblemai` 路由。如果存在多个配置文件，则每个代理模式调用都必须包含 `--profile <name>`。

---

## 前置条件

- **Node.js** >= 20.18.0
- **终端** 支持 256 色彩（iTerm2、Kitty、Windows Terminal 或任何 xterm 兼容终端）
- **可选**：[glow](https://github.com/charmbracelet/glow) 用于丰富 markdown 渲染（在 macOS 上使用 `brew install glow`）

## 安装

### 从 npm（推荐）

```bash
npm install -g @emblemvault/agentwallet
```

### 从源代码

```bash
git clone https://github.com/EmblemCompany/EmblemAi-cli.git
cd EmblemAi-cli
npm install
npm link   # 使 `emblemai` 可全局使用
```

## 首次运行

1. 安装：`npm install -g @emblemvault/agentwallet`
2. 创建或选择一个配置文件：`emblemai profile create hustle`
3. 运行 `emblemai --profile hustle` 或 `emblemai --agent --profile hustle -m "我的钱包地址是什么？"`
4. 查看 `/plugins` 以查看加载了哪些插件
5. 输入 `/help` 以查看所有命令
6. 首次创建钱包后立即备份配置文件认证

---

## 认证

EmblemAI v3 支持两种具有基于配置文件的范围本地状态的认证方法：**浏览器认证**（用于交互式使用）和**密码认证**（用于代理/脚本使用）。

### 配置文件规则

配置文件是规范的多代理隔离机制。

- `emblemai profile list`
- `emblemai profile create <name>`
- `emblemai profile use <name>`
- `emblemai profile inspect [name]`
- `emblemai profile delete <name>`
- `emblemai --profile <name> ...`

**严格关闭规则**：如果 `~/.emblemai` 中存在多个配置文件，则每个 `--agent` 调用都必须包含 `--profile <name>`。代理模式永远不会猜测要使用哪个钱包身份。

使用单独的 `HOME` 目录是可选的隔离，不是主要模式。优先考虑配置文件。

### 浏览器认证（交互模式）

当您运行 `emblemai --profile <name>` 而不带 `-p` 时，CLI：

1. 检查选定配置文件中是否有保存的会话
2. 如果存在有效的（未过期的）会话，则立即恢复它——无需登录
3. 如果没有会话，则在 `127.0.0.1:18247` 上启动本地服务器并打开您的浏览器
4. 您通过浏览器中的 EmblemVault 认证模态框进行认证
5. 捕获会话 JWT，保存到磁盘上的该配置文件中，然后 CLI 继续进行
6. 如果浏览器无法打开，则打印 URL 以手动复制粘贴
7. 如果认证超时（5 分钟），则回退到相同配置文件的密码提示

### 密码认证（代理模式）

**登录和注册是同一个操作。** 第一次使用密码会创建一个保险库；后续使用相同密码将返回相同的保险库。不同的密码会产生不同的钱包，而配置文件隔离了围绕这些钱包的本地会话和存储凭证。

在代理模式下，如果为选定配置文件未提供密码，则会自动生成一个安全的随机密码，并通过 dotenvx 加密存储在 `~/.emblemai/profiles/<name>/` 下。代理模式无需手动设置即可立即工作。

### 认证时会发生什么

1. 解析选定的配置文件
2. 浏览器认证：从浏览器接收会话 JWT 并将其注入 SDK
   密码认证：密码发送到 `EmblemAuthSDK.authenticatePassword()`，并且可以存储在选定的配置文件中以供重复使用
3. 推导出一个确定性保险库——相同的凭证始终产生相同的保险库
4. 会话提供跨多个链的钱包地址：Solana、Ethereum、Base、BSC、Polygon、Hedera、Bitcoin
5. 使用配置文件的会话初始化 EmblemAI 客户端

### 凭证发现

在为配置文件做出请求之前，使用以下优先级定位密码：

| 方法 | 如何使用 | 优先级 |
|------|-----------|----------|
| CLI 参数 | `emblemai --profile <name> -p "your-password"` | 1（最高，加密存储） |
| 环境变量 | `EMBLEM_PASSWORD="your-password" emblemai --profile <name>` | 2（不存储） |
| 加密凭证 | dotenvx 加密的 `~/.emblemai/profiles/<name>/.env` | 3 |
| 自动生成（代理模式） | 在首次运行时 `emblemai --agent --profile <name> ...` | 4 |
| 交互式提示 | 浏览器认证失败时的回退 | 5（最低） |

交互模式按以下顺序解析选定配置文件的认证：保存的会话、存储的密码、浏览器认证模态框，然后是终端密码提示。

如果选定配置文件未找到凭证，代理模式可以自动生成并存储它们。仅在用户明确希望连接现有密码派生的钱包时才要求用户输入密码：
> "我可以自动为该配置文件创建一个新鲜的 EmblemVault 钱包，或者如果您在 CLI 中本地输入原始密码，则可以连接现有钱包。
>
> **注意**：如果是您第一次使用，输入新密码将创建一个新钱包。如果您之前使用过，请使用相同的密码访问现有钱包。
>
> 您是否希望在此配置文件中提供密码？"

- 密码必须至少为 16 个字符
- 如果丢失，则无法恢复（像私钥一样）

---

## 执行说明

**允许足够的时间。** EmblemAI 查询可能需要长达 2 分钟才能完成复杂的操作（交易、跨链查找）。CLI 每 5 秒钟输出一个进度点，以指示它正在工作。

**清晰地显示 EmblemAI 的响应。** 将 EmblemAI 的响应显示给用户，使用 markdown 代码块：

```markdown
**EmblemAI 响应：**
\`\`\`
[来自 EmblemAI 的响应]
\`\`\`
```

---

## 使用方法

### 代理模式（用于 AI 代理——单次使用）

使用 `--agent` 模式进行程序化、单消息查询，并具有基于配置文件的范围认证：

```bash
# 零配置——在首次运行时为配置文件自动生成钱包
emblemai --agent --profile hustle -m "我的钱包地址是什么？"

# 为配置文件指定显式密码
emblemai --agent --profile hustle -p "$PASSWORD" -m "显示我的余额"

# 将输出管道到其他工具
emblemai -a --profile treasury -m "我的 SOL 余额是多少？" | jq .

# 用于脚本
ADDRESSES=$(emblemai -a --profile treasury -m "将我的地址列表作为 JSON")
```

任何可以调用 CLI 的系统都可以为其代理提供一个钱包：

```bash
# OpenClaw、CrewAI、AutoGPT 或任何代理框架
emblemai --agent --profile ops -m "将 0.1 SOL 发送到 <地址>"
emblemai --agent --profile treasury -m "在 Base 上将 100 USDC 兑换为 ETH"
emblemai --agent --profile research -m "我在所有链上持有哪些代币？"
```

配置文件是隔离代理钱包的主要方式。要给多个代理提供不同的钱包，请使用不同的配置文件：

```bash
emblemai --agent --profile agent-alice -m "我的地址？"
emblemai --agent --profile agent-bob -m "我的地址？"
```

代理模式始终使用密码认证（从不使用浏览器认证），在选定配置文件之间保留对话历史记录，并支持完整的 EmblemAI 工具集，包括交易、转账、投资组合查询和跨链操作。

### 交互模式（用于人类）

基于 Readline 的交互模式，具有流式 AI 响应、glow markdown 渲染和斜杠命令。

```bash
emblemai --profile hustle              # 浏览器认证（推荐）
emblemai --profile hustle -p "$PASSWORD"  # 密码认证
```

### 重置对话

```bash
emblemai --reset
```

---

## 交互命令

所有命令都以 `/` 开头。在输入栏中输入它们并按 Enter。

### 常规

| 命令 | 描述 |
|------|-------------|
| `/help` | 显示所有可用命令 |
| `/settings` | 显示当前配置（保险库 ID、模型、流式传输、调试、工具） |
| `/exit` | 退出 CLI（也：`/quit`） |

### 配置文件

| 命令 | 描述 |
|---------|-------------|
| `/profile` | 列出配置文件及其当前/默认标记 |
| `/profile create <name>` | 创建命名的配置文件 |
| `/profile use <name>` | 切换此会话和新的会话到配置文件 |
| `/profile inspect [name]` | 检查配置文件元数据、文件和运行时钱包信息 |
| `/profile delete <name>` | 删除非当前配置文件 |

如果存在多个配置文件，则每个代理模式 CLI 调用都必须包含 `--profile <name>`。

### 聊天和历史记录

| 命令 | 描述 |
|---------|-------------|
| `/reset` | 清除对话历史记录并重新开始 |
| `/clear` | `/reset` 的别名 |
| `/history on\|off` | 在消息之间切换历史记录保留 |
| `/history` | 显示历史记录状态和最近的消息 |

### 流式传输和调试

| 命令 | 描述 |
|---------|-------------|
| `/stream on\|off` | 切换流式传输模式（生成的标记按顺序出现） |
| `/stream` | 显示当前流式传输状态 |
| `/debug on\|off` | 切换调试模式（显示工具参数、意图上下文） |
| `/debug` | 显示当前调试状态 |

### 模型选择

| 命令 | 描述 |
|---------|-------------|
| `/model <id>` | 通过 ID 设置活动模型 |
| `/model clear` | 重置为 CLI 的默认模型 |
| `/model` | 显示当前选定的模型 |
| `/models` | 显示当前模型和精选默认选择 |
| `/models use <number\|id>` | 从精选默认模型中选择一个 |
| `/models search <query>` | 模糊搜索 OpenRouter 模型并通过 `/model <number\|id>` 选择一个 |

### 工具管理

| 命令 | 描述 |
|---------|-------------|
| `/tools` | 列出所有工具及其选择状态 |
| `/tools add <id>` | 将工具添加到活动集 |
| `/tools remove <id>` | 从活动集删除工具 |
| `/tools clear` | 清除工具选择（启用自动工具模式） |

在没有选择任何工具的情况下，AI 在 **自动工具模式** 下运行，根据对话上下文动态选择适当的工具。

### 认证

| 命令 | 描述 |
|---------|-------------|
| `/auth` | 打开认证菜单 |
| `/wallet` | 显示钱包地址（EVM、Solana、BTC、Hedera） |
| `/portfolio` | 显示投资组合（作为聊天查询路由） |

`/auth` 菜单提供：

| 选项 | 描述 |
|--------|-------------|
| 1. 获取 API 密钥 | 获取您的保险库 API 密钥 |
| 2. 获取保险库信息 | 显示保险库 ID、地址、创建日期 |
| 3. 会话信息 | 显示当前会话详细信息（标识符、过期、认证类型） |
| 4. 刷新会话 | 刷新认证会话令牌 |
| 5. EVM 地址 | 显示您的以太坊/EVM 地址 |
| 6. Solana 地址 | 显示您的 Solana 地址 |
| 7. BTC 地址 | 显示您的比特币地址（P2PKH、P2WPKH、P2TR） |
| 8. 备份代理认证 | 将当前配置文件的认证材料导出到备份文件 |
| 9. 注销 | 清除当前配置文件会话并退出（加密凭证保留在磁盘上） |

### 支付（PAYG 订阅）

| 命令 | 描述 |
|---------|-------------|
| `/payment` | 显示 PAYG 订阅状态（启用、模式、债务、代币） |
| `/payment enable\|disable` | 切换按需付费订阅 |
| `/payment token <TOKEN>` | 设置支付代币（SOL、ETH、HUSTLE 等） |
| `/payment mode <MODE>` | 设置支付模式：`pay_per_request` 或 `debt_accumulation` |

### Markdown 渲染

| 命令 | 描述 |
|---------|-------------|
| `/glow on\|off` | 切换通过 glow 进行 markdown 渲染 |
| `/glow` | 显示 glow 状态和版本 |

需要安装 [glow](https://github.com/charmbracelet/glow) 才能使用。

### 日志记录

| 命令 | 描述 |
|---------|-------------|
| `/log on\|off` | 切换流式传输日志记录到文件 |
| `/log` | 显示日志记录状态和文件路径 |

日志文件默认为 `~/.emblemai-stream.log`。使用 `--log-file <path>` 覆盖。

---

## 键盘快捷键

| 键 | 动作 |
|-----|--------|
| `Enter` | 发送消息 |
| `Up` | 回调之前输入 |
| `Ctrl+C` | 退出 |
| `Ctrl+D` | 退出（EOF） |

---

## CLI 标志

| 标志 | 别名 | 描述 |
|------|-------|-------------|
| `--profile <name>` | | 选择调用的命名钱包配置文件 |
| `--password <pw>` | `-p` | 认证密码（至少 16 个字符）——跳过浏览器认证 |
| `--message <msg>` | `-m` | 代理模式的消息 |
| `--agent` | `-a` | 以代理模式运行（单次使用，仅密码认证；当存在多个配置文件时需要 `--profile`） |
| `--restore-auth <path>` | | 从备份文件将凭证恢复到选定配置文件并退出 |
| `--reset` | | 清除对话历史记录并退出 |
| `--debug` | | 启用调试模式启动 |
| `--stream` | | 启用流式传输启动（默认：开启） |
| `--log` | | 启用流式传输日志记录 |
| `--log-file <path>` | | 覆盖日志文件路径（默认：`~/.emblemai-stream.log`） |
| `--hustle-url <url>` | | 覆盖 EmblemAI 服务器 URL |
| `--auth-url <url>` | | 覆盖认证服务 URL |
| `--api-url <url>` | | 覆盖 API 服务 URL |

## 环境变量

| 变量 | 描述 |
|----------|-------------|
| `EMBLEM_PASSWORD` | 认证密码 |

CLI 参数在提供时覆盖环境变量。在显式 CLI 和环境覆盖之后，将检查基于配置文件的存储凭证。

---

## 权限和安全模式

代理默认以 **安全模式** 运行。任何影响钱包的操作都需要用户明确确认才能执行：

- **交易**（交换、发送、转账）——代理显示详细信息并询问批准
- **签名**（消息签名、交易签名）——需要明确用户同意
- **订单挂单**（限价订单、止损）——必须在提交前确认
- **DeFi 操作**（LP 存款、收益农耕）——用户必须批准每个操作

只读操作（检查余额、查看地址、市场数据、投资组合查询）不需要确认并立即执行。

代理永远不会在没有用户首先查看和批准操作的情况下自动移动资金、签名交易或挂单。

---

## 沟通风格

**关键：使用详细、自然的语言。**

EmblemAI 将简短命令解释为 "$0" 交易。始终用完整的句子解释您的意图。

| 坏（简短） | 好（详细） |
|-------------|----------------|
| `"SOL 余额"` | `"What is my current SOL balance on Solana?"` |
| `"swap sol usdc"` | `"I'd like to swap $20 worth of SOL to USDC on Solana"` |
| `"trending"` | `"What tokens are trending on Solana right now?"` |

您提供的上下文越多，EmblemAI 就越能理解您的意图。

---

## 功能

| 类别 | 功能 |
|----------|----------|
| **链** | Solana、Ethereum、Base、BSC、Polygon、Hedera、Bitcoin |
| **交易** | 交换、限价订单、条件订单、止损 |
| **DeFi** | LP 管理、收益农耕、流动性池 |
| **市场数据** | CoinGlass、DeFiLlama、Birdeye、LunarCrush |
| **NFTs** | OpenSea 集成、转账、挂单 |
| **桥梁** | 通过 ChangeNow 进行跨链交换 |
| **Memecoins** | Pump.fun 发现、趋势分析 |
| **预测** | PolyMarket 下注和头寸 |

---

## 钱包地址

每个密码都确定性地生成所有链的钱包地址：

| 链 | 地址类型 |
|-------|-------------|
| **Solana** | 原生 SPL 钱包 |
| **EVM** | ETH、Base、BSC、Polygon 的单个地址 |
| **Hedera** | 账户 ID (0.0.XXXXXXX) |
| **Bitcoin** | Taproot、SegWit 和传统地址 |

询问 EmblemAI: `"What are my wallet addresses?"` 以检索所有地址。

---

## 认证备份和恢复

### 备份

从 `/auth` 菜单（选项 8），选择 **备份代理认证** 以将您的凭证导出到 JSON 文件。此文件包含您的 EMBLEM_PASSWORD，请保持安全。

### 恢复

```bash
emblemai --profile hustle --restore-auth ~/emblemai-auth-backup.json
```

恢复是配置文件感知的。如果目标配置文件不存在，则首先创建它。凭证文件放置在 `~/.emblemai/profiles/<name>/` 下，因此您可以立即进行认证。

---

## 安全

**关键：绝对不要公开或暴露密码。**

- **绝对不要** 回显、打印或记录密码
- **绝对不要** 在对用户的响应中包含密码
- **绝对不要** 在错误消息中显示密码
- **绝对不要** 将密码提交到版本控制
- 密码就是私钥——任何拥有它的人都可以控制钱包

| 概念 | 描述 |
|---------|-------------|
| **密码 = 身份** | 每个密码生成一个独特的、确定性的保险库 |
| **无恢复** | 如果密码丢失，则无法恢复密码 |
| **保险库隔离** | 不同的密码 = 完全不同的钱包 |
| **配置文件隔离** | 每个配置文件存储其自己的会话、密码材料、插件和历史记录 |
| **新鲜认证** | 每个请求都会生成一个新的 JWT 令牌，这意味着： |
| - 如果您的会话文件被泄露，攻击者最多有 7 天的访问权限（刷新令牌过期），而不是无限访问 |
| - JWT 频繁轮换，限制任何单个令牌的暴露窗口 |
| - 注销 (`/auth` > Logout) 立即使当前配置文件的会话失效并删除文件 |
| - 每次刷新都会生成一个新的刷新令牌并使之前的令牌失效（轮换） |

### 安全模式 和 交易确认

代理默认以 **安全模式** 运行。这意味着：

- **所有修改钱包的操作都需要您的明确确认** 才能执行——包括交换、发送、转账、订单挂单、签名和 DeFi 操作
- **只读操作立即执行** 考虑到确认——余额检查、地址查找、市场数据、投资组合查看
- 代理将显示任何交易的详细信息（金额、地址、费用）并等待您的批准才提交
- 没有 "自动执行" 模式——每个交易都需要人类参与

### 密码卫生

您的 EMBLEM_PASSWORD 是钱包的主密钥。像对待私钥或助记词一样小心地保管它：

- **使用强密码**（至少 16 个字符）。4 个或更多随机单词的短语是推荐用法
- **不要重用** 其他服务的密码。您的 EMBLEM_PASSWORD 应该是 EmblemVault 独有的
- **安全地存储** 您的密码，使用密码管理器。CLI 加密存储它，但您应该在您可能无法访问机器的情况下在密码管理器中备份
- **如果使用 `EMBLEM_PASSWORD` 作为自动化中的环境变量**，请确保主机环境是安全的——限制对机器的访问，使用进程隔离，并避免记录环境变量
- **交互式使用时优先考虑浏览器认证**——它避免了将密码放入 shell 历史记录或环境变量，并将认证限制为选定配置文件
- **不同的密码创建不同的钱包**——这是设计目的。使用此功能将资金按用途分离（例如，一个钱包用于日常使用，另一个用于长期持有）

### 验证包

在安装之前或之后，您可以检查包的确切内容：

```bash
# 不安装即可查看包内容
npm pack @emblemvault/agentwallet --dry-run

# 安装后，检查源代码
ls $(npm root -g)/@emblemvault/agentwallet/

# 与 GitHub 源进行比较
git clone https://github.com/EmblemCompany/EmblemAi-AgentWallet.git
diff -r node_modules/@emblemvault/agentwallet EmblemAi-AgentWallet/publish
```

### 报告安全问题

如果您发现一个安全漏洞，请负责任地报告：

- **GitHub**：在 [github.com/EmblemCompany/EmblemAi-AgentWallet/issues](https://github.com/EmblemCompany/EmblemAi-AgentWallet/issues) 打开问题
- **Discord**：在安全频道中报告 [discord.gg/Q93wbfsgBj](https://discord.gg/Q93wbfsgBj)

---

## 链接

- [npm 包](https://www.npmjs.com/package/@emblemvault/agentwallet)
- [EmblemVault](https://emblemvault.dev)
- [EmblemAI](https://emblemvault.ai)
- [GitHub](https://github.com/EmblemCompany/EmblemAi-AgentWallet)
