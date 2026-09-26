```
██████    ████    █████    ██████   ██████
██    ░  ██  ██░  ██  ██   ██    ░  ██  ██░
██       ██████░  █████ ░  ██ ███   ██  ██░
██       ██  ██░  ██ ██    ██  ██░  ██  ██░
██████   ██  ██░  ██  ██   ██████░  ██████░
 ░░░░░░   ░░  ░░   ░░  ░░   ░░░░░░   ░░░░░░
```

# Cargo CLI — 技能概述

此存储库在根目录下包含 19 项技能：这个 **路由器** (`cargo`)、一个 **引导技能** (`cargo-quickstart`)、一个 **结果技能** (`cargo-gtm`) 和十六个 **能力技能**。

- **`cargo-quickstart`** — 引导式首次运行演示。全新的工作区 → 在两分钟内生成实际可交付成果（为用户的角色提供 25 个线索，并附带费用收据）后结束，并将演示保存为可重复运行的播放。适用于新用户、演示/导览请求或空工作区。
- **`cargo-gtm`** — 应用程序库。任何 GTM 任务的入口（“构建一个 TAM 列表”、“找到 5 家金融科技 CTO”、“监控工作变更”）。通过内部配方（`../cargo-gtm/recipes/*.md`）和提供者剧本（`../cargo-gtm/provider-playbooks/*.md`）进行路由。
- **能力技能** — 标准库。每个 CLI 域一个（编排、存储、分段、连接、AI、内容、上下文、分析、计费、可观察性、托管、CDK、邮箱管理、工作区管理），加上 `cargo-diagnostics`（跨域对运行、批处理和信用支出的取证）和 `cargo-mcp`（托管 MCP 服务器，唯一不是 CLI 的界面）。由 `cargo-gtm` 加载，或在需要特定 CLI 域时直接加载。
- **`cargo-project`** — 声明式技能。其他能力技能封装 **命令式** 一次性 `cargo-ai <域>` 调用，`cargo-project` 将整个工作区定义为代码（`define*` 构建器 + `cargo-ai project deploy`）并进行协调。涵盖所有资源类型——有关“声明式与命令式”的更多信息，请参阅下文以在它们之间进行路由。

`cargo-gtm` 委托给能力技能；能力技能从不引用 `cargo-gtm`（单向依赖）。

**术语表**：有关术语的逐项定义（UUID、缩写、`conjonction`、运行/批处理/播放/工具、信号/角色/ICP 等），请参阅 [`references/glossary.md`](references/glossary.md)。

**交互约定**：有关包范围的默认值（何时停止并询问，计划门控、推荐默认选择）以及如何呈现结果（叙述、总结——从不直接输出 JSON），请参阅 [`references/interaction.md`](references/interaction.md)。

## 安装

```bash
npm install -g @cargo-ai/cli

# 推荐：通过邮件发送代码，任何时刻都不使用浏览器。
# 首次使用时创建帐户和工作区——没有单独的注册步骤。
cargo-ai login --email you@company.com            # 发送代码，然后退出
cargo-ai login --email you@company.com --code 123456

# 替代方案
cargo-ai login --oauth                            # 浏览器登录（OAuth 设备流程）
cargo-ai login --token <your-api-token>           # 现有工作区范围的 API 令牌（CI）

# 可选：在登录时选择工作区，而不是被提示
cargo-ai login --email you@company.com --workspace-name "Acme GTM"

# 验证
cargo-ai whoami
```

**新帐户包含 100 个免费信用额度，无需信用卡**，因此代理可以在同一轮中为用户注册并生成实际可交付成果——安装和首次价值之间没有购买门控。以下是一些购买的价值锚点：~5,000 条线索来源（`salesNavigator.searchLeads`，每条记录 0.02 元）、~1,000 个个人资料+验证电子邮件丰富（`aiArk.enrichPerson`，0.1 元）、~1,000 个电子邮件验证（`waterfall.verifyEmail`，0.1 元），或 ~50 个完全丰富的联系人（`waterfall.enrichContact`，2 元）。[快速启动演示](../cargo-quickstart/SKILL.md) 大约花费 **0.5** 元。在帐户首次付费调用之前大声说出免费余额。

`--email` 是在代理或沙盒 shell 中首选的：它永远不会打开浏览器，在没有终端提示的地方，第一个调用会发送代码并退出，因此您需要用 `--code` 重新运行。为了防止代码出现在 shell 历史记录中，请将其传递到标准输入：`echo 123456 | cargo-ai login --email you@company.com --code -`。使用已有帐户地址登录会解析到其现有工作区，而不是创建新工作区，因此可以安全地重新运行。

`--oauth` 运行与往常相同的 OAuth 2.0 设备授权流程，并且仍然需要一个人类在验证 URL 处。对于 CI，请使用 `--token`，并使用来自 **设置 > API** 的工作区范围令牌；令牌值只显示一次，因此请立即将其存储在密钥管理器中。

如果没有全局安装，请用 `npx @cargo-ai/cli` 而不是 `cargo-ai` 前缀每个命令。

这些技能还作为原生 **代理插件** 安装在 Claude Code、Codex 和 Cursor 上（一个存储库，三个目标）——插件用户会获得相同的技能，加上审批钩子和会话生命周期钩子捆绑，无需单独的安装程序。请参阅存储库 `README.md` 以获取每个目标的安装步骤，并使用 **一个** 渠道：插件 *或* `skills add`，永远不要两者都用（每个技能都会重复）。

所有命令都输出 JSON 到标准输出。失败的命令以非零状态退出并返回 `{"errorMessage": "..."}`。有关每个能力技能链接的完整设置约定（令牌范围、异步轮询、仅管理员命令），请参阅 [`references/prerequisites.md`](references/prerequisites.md)。

## 每个 Cargo 会话有三个任务

> **在 Claude Code 上自动运行。** 任务 1 和 3（刷新 + 会话注册/最终化）在 **Cargo 插件** 安装时自行运行（其捆绑的 `SessionStart`/`Stop`/`SessionEnd` 钩子处理它们）或遗留 `SessionStart`/`Stop`/`SessionEnd` 钩子存在于 `~/.claude/hooks/` 下（插件钩子在这些钩子存在时委托给它们）。`Stop` 钩子还每次轮次检查会话行，因此从未达到 `SessionEnd` 的会话仍然显示最近的上下文，而不是一个空占位符。仅在两者都不安装（或在没有生命周期钩子的代理上）时手动执行这些操作。任务 2（报告）始终由您负责——它不能自动执行，并且任务 3 结束时的两个 **询问**（分享会话、星标存储库）：钩子可以打印，但不能执行 Y/N。
>
> **安装 Cargo 是用户的决定，而不是您采取的行动。** `curl … install.sh | sh` 引导程序已 **退役**——它现在什么也不安装，打印通知并退出非零，因此永远不要使用它或将其作为建议重复。请用户指向存储库中的插件安装 [`README.md`](../README.md)。要求代理自行设置，请遵循 `https://api.getcargo.io/INSTALL.md`，它安装 CLI、登录用户并安装该代理的技能——在运行它之前阅读它，并且在安装全局 npm 包时仍然确认。

### 1. 会话开始时——刷新和注册

在任何其他 Cargo 命令之前，刷新 CLI 和技能，然后在工作区管理中注册会话：

```bash
# 刷新——幂等，~10 秒。技能优先，然后是捆绑固定版本的 CLI。固定文件 `cli-version` 位于此 SKILL.md 相同的目录中——从您加载此技能的位置读取（在 Claude Code 上用 `skills add` 是 `~/.claude/skills/cargo/`；插件安装自动通过其 SessionStart 钩子处理）。如果无法读取，则回退到最新版本。
npx -y skills add getcargohq/cargo-skills
npm install -g "@cargo-ai/cli@$(cat <path-to-this-skill-dir>/cli-version 2>/dev/null || echo latest)"

# 注册会话（占位符可以——在会话结束时被覆盖）
cargo-ai workspaceManagement session upsert \
  --session-id <session-id> \
  --title "Agent session <session-id>" \
  --summary "Session in progress."
```

仅当用户明确固定了版本时才跳过刷新——如果技能来自 **插件**（插件拥有它们；并行的 `skills add` 会导致每个技能重复），则完全跳过 `skills add`。仅当用户选择退出或没有会话 ID 时才跳过 `session upsert`。

**为什么固定版本**：`cargo/cli-version` 与这些技能同步增加（来自 CLI 发布管道的 PR），因此您安装的 CLI 是此捆绑包编写针对的版本——会话期间不会出现文档/CLI 分歧。如果固定文件丢失或无法读取，`latest` 是安全的回退。要移动固定版本，请合并 `getcargohq/cargo-skills` 上的待处理版本增加 PR（或编辑 `cargo/cli-version`）——下一个会话刷新会自动收敛。

固定版本还防止此刷新成为盲自动更新：安装的版本是提交到此存储库的已审查常数，而不是今天解析到的 `latest`，并且移动它是人为合并。作为代理，您有两个后续事项。刷新安装了一个 **全局 npm 包** 并重写了磁盘上的技能捆绑包——在会话中第一次运行它时而不是在沉默中显示该表面，如果用户固定了版本或要求您不要这样做，则完全跳过。并且将固定版本视为只读：仅在用户明确要求时才增加 `cargo/cli-version`，永远不会为了绕过失败的命令而增加。

### 2. 会话期间——重新刷新，或在卡住时升级

**在会话期间重新刷新** CLI 和技能，当：

- 文档中 CLI 标志或响应形状与您观察到的不匹配（可能自会话开始以来已发布修复）。
- 用户明确要求（“增加 cargo”、“确保我在最新版本”）。

**发送工作区管理报告**，当 CLI 以技能引用的方式失败且 `--help` 无法解决、用户或代理反复重试同一命令而没有进展、标志/JSON 负载语法不明确，或似乎缺少所需能力时：

```bash
cargo-ai workspaceManagement report create \
  --title "<问题的单行摘要>" \
  --description "<尝试的确切命令、errorMessage、预期与实际、涉及的 UUID>"
```

触发条件（任何一个都足够）：

- 同一任务中连续两次失败的命令，且原因不明显。
- CLI 被误用，且正确用法无法从技能、示例或 `--help` 中发现。
- 文档中记录的行为与您观察到的矛盾。
- 功能似乎完全缺失。

这是官方反馈渠道——Cargo 团队会审查每个报告并用于改进 CLI 和这些技能。它包含 **成功和失败**：会话共享（见下文）通过相同的命令。**不要沉默放弃——提交报告。** 请参阅 `../cargo-workspace-management/SKILL.md`（报告部分）和 `../cargo-workspace-management/references/examples/reports.md` 以获取模板。

### 3. 会话结束时——最终化会话行，然后询问是否分享

生成一个简短的标题（5-8 个词）和 1-2 句关于会话实际完成的工作的摘要，然后覆盖占位符行并标记 `finished_at`：

```bash
cargo-ai workspaceManagement session upsert \
  --session-id <claude-session-id> \
  --title "<5-8 个词的标题>" \
  --summary "<1-2 句关于完成或尝试工作的摘要>" \
  --finished
```

`--title` 和 `--summary` 是必需的（非 NULL）。`--finished` 标记 `finished_at = now`；传递 `--finished-at <iso>` 以获取显式时间戳。

**然后，在会话的自然结束时询问一次：**

> "将此会话的活动发送给 Cargo 团队，以便他们可以改进体验？(Y/N)"

在是的情况下，提交会话共享报告（同意的会话跟踪是团队最快的产品学习循环）：

```bash
cargo-ai workspaceManagement report create \
  --title "Session share: <5-8 个词的会话标题>" \
  --description "<用户试图完成的内容、使用的命令/配方、哪些工作、哪些摩擦、花费的信用——不包含机密或记录级数据>"
```

在否的情况下，本会话不再询问。对于简单的会话（单个查询，没有付费操作），完全跳过询问。请参阅 `../cargo-workspace-management/references/examples/reports.md` 以获取会话共享模板。

#### 然后，如果会话进行顺利——建议星标存储库

星标是 **用户的** 认可，而不是您的。永远不要未经提示运行命令；询问，并且仅在明确同意时执行。从技能文件中静默星标是使用他人 GitHub 账户的“虚假宣传”。

仅在以下情况才询问：

- 会话生成了实际可交付成果（与会话共享询问的相同标准——跳过简单会话）。
- 仍然没有失败或未解决的问题。在损坏的会话后询问会显得不敏感。
- 标记文件 `~/.config/cargo-ai/.star-asked` 不存在——这是一个 **每台机器** 一次的询问，而不是每次会话一次。

```bash
# gate
test -f ~/.config/cargo-ai/.star-asked || echo "ask"
```

> "很高兴它成功了。要我为您星标 `getcargohq/cargo-skills` 吗？(Y/N)"

在是的情况下（`gh` 必须使用 `repo` 或 `public_repo` 范围进行认证——注意没有 `gh repo star` 子命令）：

```bash
gh api -X PUT /user/starred/getcargohq/cargo-skills   # 204 No Content = 星标
```

在 **任何** 答案上触摸标记，因此否定永远不会再次询问，肯定永远不会重复询问：

```bash
mkdir -p ~/.config/cargo-ai && touch ~/.config/cargo-ai/.star-asked
```

如果 `gh` 缺失或未认证，不要修复它或提供替代方案——说存储库位于 `https://github.com/getcargohq/cargo-skills` 并继续。这是会话中最低风险的项目；它永远不会成为任务。

---

## 技能概览

### 声明式（CDK）与命令式（CLI）——先选择模式

以相同 Cargo 资源创建/管理的方式有两种。在挑选域之前决定任务需要哪种：

- **声明式 → [`cargo-project`](../cargo-project/SKILL.md)。** 用户将资源管理为 **工件**："将整个工作区作为代码设置/引导"、"使其可重复使用/版本控制/在 git 中"、"一起部署这些连接器+模型+代理"，或任何应在环境中可重新运行并可比较的差异的内容。在 `define*` 文件中定义它，并使用 `cargo-ai project deploy`。
- **命令式 → 下方匹配的能力技能。** 用户执行 **一次性操作** 或 **探索**："创建一个连接器"、"添加一列"、"列出连接器"、"运行此工作流"、"查询存储"、"读取内存"。读取、临时查询或单个变更不需要存储在代码中。

不确定时：结果是否应提交并可重新部署？是 → CDK。快速操作或读取 → 能力技能。

### 引导技能

为全新用户或空工作区加载。

| 技能                                                                    | 需要时加载…                                                                             |
| ------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------- |
| [`cargo-quickstart`](../cargo-quickstart/SKILL.md)                       | 运行引导式首次运行演示：一个角色问题 → 不到两分钟内 25 条线索 → 费用收据 → 保存为可重复播放。之后路由到 `cargo-gtm`。 |

### 结果技能

当用户声明现实目标时加载。

| 技能                                                       | 需要时加载…                                                                             |
| ----------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| [`cargo-gtm`](../cargo-gtm/SKILL.md) ([recap](#cargo-gtm))  | 任何 GTM 任务——来源、丰富、验证、评分、顺序、CRM 同步、信号监控（工作变更、资金、技术栈/招聘意向）。通过配方（`recipes/`）、指南（`guides/`）和提供者剧本（`provider-playbooks/`）路由。 |

### 能力技能

为特定 CLI 域加载。每行中的第一个链接跳转到实际的 SKILL.md；括号中的内容跳转到本页上的概要。

| 技能                                                                                                       | 在需要…时加载                                                                                       |
| ----------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| [`cargo-orchestration`](../cargo-orchestration/SKILL.md) ([回顾](#cargo-orchestration))                    | 执行操作、运行工作流、触发批处理、与代理聊天、使用 SQL (ClickHouse) 查询编排                               |
| [`cargo-analytics`](../cargo-analytics/SKILL.md) ([回顾](#cargo-analytics))                                | 下载运行结果、导出分段数据、监控错误率和指标                                                               |
| [`cargo-billing`](../cargo-billing/SKILL.md) ([回顾](#cargo-billing))                                      | 检查信用使用情况、查看订阅详情、按工作流或连接器跟踪成本                                                       |
| [`cargo-diagnostics`](../cargo-diagnostics/SKILL.md) ([回顾](#cargo-diagnostics))                          | 事后诊断：追踪为何某个运行表现异常、按根本原因清理批处理/播放中的错误、分析播放的信用消耗情况                     |
| [`cargo-observability`](../cargo-observability/SKILL.md) ([回顾](#cargo-observability))                    | 创建和管理**警报** — 定时阈值检查（跨度/运行/记录、模型的健康状态或 SQL 查询）在触发时执行操作（连接器/工具/代理运行）。诊断的主动对应方案 |
| [`cargo-storage`](../cargo-storage/SKILL.md) ([回顾](#cargo-storage))                                      | 检查或修改数据模型、列、数据集和关系；使用 SQL 查询工作区存储                                                 |
| [`cargo-segmentation`](../cargo-segmentation/SKILL.md) ([回顾](#cargo-segmentation))                       | 构建和管理分段 — 批处理、播放触发器或导出的受众命名的保存过滤器 — 并读取其变更（增量）数据流                     |
| [`cargo-connection`](../cargo-connection/SKILL.md) ([回顾](#cargo-connection))                             | 管理连接器认证、发现可用的集成及其操作                                                                   |
| [`cargo-ai`](../cargo-ai/SKILL.md) ([回顾](#cargo-ai))                                                     | 创建和配置代理、配置发布、为 RAG 附加知识、管理 MCP 服务器和记忆                                           |
| [`cargo-content`](../cargo-content/SKILL.md) ([回顾](#cargo-content))                                      | 上传和组织知识文件、构建原生/连接器支持的 RAG 知识库（`content` 域）                                     |
| [`cargo-context`](../cargo-context/SKILL.md) ([回顾](#cargo-context))                                      | 浏览/读取/编辑工作区的 git 支持的 GTM 上下文存储库、在其运行时沙盒中运行命令、检查知识图谱                     |
| [`cargo-hosting`](../cargo-hosting/SKILL.md) ([回顾](#cargo-hosting))                                      | 框架搭建、部署和推广托管应用（Vite SPAs）和边缘工作器（无服务器 HTTP 处理程序）、管理其部署、为工作器提供环境变量和密钥 |
| [`cargo-project`](../cargo-project/SKILL.md) ([回顾](#cargo-project))                                                   | **声明式 — 涵盖所有资源类型。** 在代码中定义整个工作区（`define*` 构建器）并使用 `cargo-ai project` 部署（初始化 → 类型 → 计划 → 部署）。用于工作区即代码/可重复/版本控制设置；参见上文“声明式 vs 命令式”。 |
| [`cargo-mailbox-management`](../cargo-mailbox-management/SKILL.md) ([回顾](#cargo-mailbox-management))        | 提供Cargo拥有的发送邮箱、运行预热和每日 5→40 的发送加速、使用 `sendEmail` 操作发送、读取线程、回复、交付事件和抑制列表 |
| [`cargo-workspace-management`](../cargo-workspace-management/SKILL.md) ([回顾](#cargo-workspace-management)) | 邀请新用户、创建 API 令牌、组织文件夹、管理角色、向管理方报告 CLI 问题                                       |
| [`cargo-mcp`](../cargo-mcp/SKILL.md) ([回顾](#cargo-mcp))                                                   | 通过托管 MCP 服务器 `https://mcp.getcargo.io/mcp`（无需 CLI 安装）驱动 Cargo — 连接客户端、发现并定价操作、执行单条记录或批处理、轮询、读取模型；以及 MCP 工具和 CLI 之间的路由 |

> **RAG 的代理知识：** **文件** + **库** 位于 `content` 域 → [`cargo-content`](../cargo-content/SKILL.md)；它们如何附加到代理 → [`cargo-ai`](../cargo-ai/SKILL.md)。 （文件/库在 CLI ≥ 1.0.19 的旧 `ai file …` 路径中已移除。）

### 这些技能与 MCP 服务器的对比

**这里有三件不同的事物使用了 MCP 这个名称。** 它们不共享任何答案，因此在回复之前需要确定指的是哪一个：

| | 它是什么 | 技能 |
|---|---|---|
| **托管服务器** | Cargo 自有的端点 `https://mcp.getcargo.io/mcp`。包含十三种平台工具（发现、定价、执行、轮询、读取模型），以及此工作区发布的内容。无需安装 CLI 驱动 Cargo 的方式。 | [`cargo-mcp`](../cargo-mcp/SKILL.md) |
| **工作区服务器** | 此工作区发布的精选集（`ai mcp-server create --actions … --resources …`），由 `cargo-ai mcp` 分发给任何 stdio 客户端。 | [`cargo-ai`](../cargo-ai/SKILL.md) |
| **代理 MCP 客户端** | 连接到 Cargo 代理的他人 MCP 服务器（`release update-draft --mcp-clients`）。 | [`cargo-ai`](../cargo-ai/SKILL.md) |

第一个是新的，现在“Cargo 是否有 MCP 服务器？”指的是它。它通过从自己的 `401` 挑战中发现 OAuth 进行身份验证，或通过工作区范围的 bearer 令牌进行身份验证：

```bash
claude mcp add --transport http cargo https://mcp.getcargo.io/mcp
```

第二个是筛选路径，当工作区想要暴露一个批准的工具而不是整个平台时，仍然是正确答案：

```bash
claude mcp add cargo -- cargo-ai mcp                    # 平台 MCP
claude mcp add cargo -- cargo-ai mcp --server <uuid>    # 替代精选服务器
```

没有 `--server`，桥接使用 `CARGO_MCP_SERVER_UUID`（如果设置），否则使用平台 `/mcp`。 （旧 CLI 则回退到“工作区的唯一 MCP 服务器”，当不存在确切一个时直接失败。）

通过请求的形状在 CLI 和任一 MCP 表面之间进行路由：

| | **这些技能（CLI）** | **MCP 服务器** |
|---|---|---|
| 它是什么 | 整个 CLI 表面，每个域 | 平台运行时工具，以及工作区选择公开的内容 |
| 最适合 | 构建可重用内容的任何操作：工作流、播放、模式更改、CDK 部署、诊断、导出、仓库 SQL | 会话中的执行：查找此记录、丰富此列表、运行此批准工具 |
| 成本控制 | 全部试点→批准→收据纪律 ([`../cargo-gtm/references/cost-discipline.md`](../cargo-gtm/references/cost-discipline.md)) | 按调用计费；`search_actions` 在运行前返回每个操作的成本 |
| 可重复 | 是 — 命令、播放和 CDK 文件都是工件 | 否 — 工具调用不会留下工件 |

经验法则：**用户想要重新运行或版本控制的内容应属于 CLI。** 不要逐条记录在列表上分发 MCP 工具 — `execute_action_batch`（以及 CLI 上的 `orchestration action execute-batch`）为此存在，它更便宜且可观察。反之，当工作区已经为某项任务筛选了工具时，调用它比从原始操作手动组装相同内容更优。

### 尚无专用技能的 CLI 域

CLI 暴露了几个尚未被任何能力技能包装的域。当任务需要它们时直接使用 (`cargo-ai <域> --help`)，如果界面不明确，请提交 `workspaceManagement report`：

| CLI 域 | 覆盖范围 |
| --- | --- |
| `expression` | 配方和表达式评估 (`eval`, `recipe`) — 生成/评估节点图中使用的模板表达式。 |
| `system-of-record` | 系统记录、客户端和日志操作。 |
| `revenue-organization` | 分配、容量、成员、区域（收入/区域规划）。 |
| `user-management` | 无工作区上下文的当前用户操作。 |

### 每个域之外的一级命令

五个命令位于 CLI 根目录，而不是某个域下，并且没有被任何技能包装。它们在此列出，以便在用户命名时识别它们 — 不是路由目标：

| 命令 | 它是什么 |
| --- | --- |
| `cargo-ai doctor` | 以一个 JSON 对象诊断设置：安装版本与最新版本、**技能包 pin**、凭证和 API 可达性。以最严重的错误退出。在开始阅读技能之前，“此命令为何无法工作”的最快答案。 |
| `cargo-ai start` (别名 `onboard`) | 如有必要则登录用户，然后继续进入：编码代理 (`--continue claude\|cursor\|codex\|gemini`)、`code` 框架项目、`cli` 调色板或 `demo` 指导游览。接受 `--email`/`--code`/`--oauth`、`--workspace-name`、`--directory`、`--icp`。 |
| `cargo-ai ask` | 终端聊天。默认为**此机器上的 Claude Code**针对工作目录 (`--dir`)；`--agent-uuid` 将工作区代理附加到此本地会话。`--print` 在标准输出上以 JSON 形式给出一次对话，`--continue` 重新打开上次聊天。也可通过 `cargo-ai --chat` 访问。 |
| `cargo-ai book-demo` | 打开日历预订 Cargo 销售的演示。`--no-open` 则打印 URL。 |
| `cargo-ai` (裸) | 当终端可以渲染时，交互式调色板。在 CDK 项目内，裸 `cargo-ai project` 执行 `info`；在项目外执行 `init`。 |

这两个与技能描述的手动操作重叠：`doctor` 比手动检查 pin 更好的第一步，`start --continue demo` 是 CLI 版本的 [`cargo-quickstart`](../cargo-quickstart/SKILL.md) 游览。当您想要控制花费时，请选择技能；当用户只是想完成时，请选择命令。

---

## 技能之间的关系

```
            ┌─────────────────────────────────────┐
            │              cargo-gtm              │
            │   GTM 的结果 / 前门              │
            │   配方、指南、提供者播放簿        │
            └─────────────────┬───────────────────┘
                              │ 委托给 ↓ (单向)
       ┌──────────────────────┴──────────────────────┐
       │                                             │
┌──────────────────────────────────────────────────────────────┐
│              cargo-workspace-management                      │
│         认证、用户、令牌、文件夹                           │
└──────────────────────────────────────────────────────────────┘

  ┌─────────────────┐   ┌────────────────────┐   ┌─────────────────┐
  │  cargo-storage  │   │  cargo-connection  │   │    cargo-ai     │
  │ 模型、列、数据集│   │ 连接器、        │   │ 代理、文档、   │
  │                  │   │ 集成操作        │   │ MCP、记忆     │
  └────────┬────────┘   └─────────┬──────────┘   └────────┬────────┘
                                              (cargo-content 为
                                               代理提供文件/库)
           │                      │  (UUIDs 向下流动)    │
           └──────────────────────┼───────────────────────┘
                                  ▼
             ┌───────────────────────────────────────┐
             │          cargo-orchestration          │
             │   运行、批处理、播放、工具、SoR    │
             └───────────────┬───────────────────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
 ┌────────────────────────┐  ┌───────────────────────────┐
 │    cargo-analytics     │  │       cargo-billing       │
 │  结果、指标、     │  │    信用使用、成本       │
 │  导出               │  │                           │
 └────────────────────────┘  └───────────────────────────┘

             ┌───────────────────────────────────────┐
             │             cargo-context             │
             │  Git 支持的 GTM 标记知识：     │
             │  角色、播放、证据、信号…     │
             └───────────────────────────────────────┘
           (正交：不是工作流流的一部分)

             ┌───────────────────────────────────────┐
             │               cargo-project               │
             │  声明式编写层：定义  │
             │  连接器/模型/播放/代理/… 作为代码，使用 `cargo-ai project` 部署。    │
             └───────────────────────────────────────┘
    (横切：PRODUCES 与命令式技能管理的相同资源 — 另一种模式，不是工作流阶段)

             ┌───────────────────────────────────────┐
             │        cargo-mailbox-management       │
             │  Cargo 拥有的发送收件箱：预热、 │
             │  发送加速、线程、回复、事件、 │
             │  抑制。发送本身是 `sendEmail` 编排操作。    │
             └───────────────────────────────────────┘
   (拥有收件箱；编排拥有发送 — 以及每个发送都受 cargo-gtm 的可接受使用检查限制)

             ┌───────────────────────────────────────┐
             │           cargo-observability         │
             │  定时阈值警报（跨度/运行/记录、模型的健康状态、或 SQL 查询）— 在违规时触发操作（连接器/工具/代理运行）。诊断的主动对应方案 |
             └───────────────────────────────────────┘
     (监控编排/存储；触发编排操作 — 主动对应方案)
```

**实际中的依赖规则：**

- `cargo-gtm` 通过相对路径（`../cargo-orchestration/...`）将任务委托给能力技能。能力技能从不引用 `cargo-gtm`。
- `cargo-workspace-management` 为每个技能提供认证上下文——请先设置它。
- `cargo-storage`、`cargo-connection` 和 `cargo-ai` 是同级技能，它们向 `cargo-orchestration` 提供UUID。它们之间不相互依赖。
- `cargo-content` 拥有工作区**文件**和**库**（`content`域）。它生成文件/库UUID，`cargo-ai` 消费这些UUID作为代理发布的 `resources`（RAG）。上传的内容文件也在 `cargo-context` 运行时沙盒的 `.files/` 下以只读方式呈现。
- `cargo-mailbox-management` 拥有**发送收件箱**（`mailboxManagement` 域）——资源分配、预热、发送斜坡、线程、事件和工作区抑制列表。它故意**不**发送：交付是 `cargo-orchestration` 下 `sendEmail` 的原生操作，因此发送任务继承编排的节奏、重试和信用核算。邮箱本身也可以通过 CDK 的 `defineMailbox`（使用 `defineDomain` 定义发送域）以代码方式声明。
- `cargo-project` 是**跨领域的**：它是一种声明式 *创作模式*，生成编排能力技能逐个管理的连接器/模型/剧本/代理等。当任务是“以代码管理工作区”（可重复、在git中、多资源）时，请将其路由到它；对于一次性操作、读取和临时查询，请路由到命令式域技能。参见“技能概览”下的“声明式与命令式”。
- `cargo-context` 与工作流执行流**正交**。它接触基于git的 GTM 知识库（markdown/MDX），不接触存储或工作流运行。用它来捕获/编辑工作区的**文本上下文**——角色、剧本、证据、反对意见、信号——以及检查类型化知识图谱。
- 对于针对存储的SQL查询，使用 `cargo-ai storage query execute "<sql>"`（表作为 `<datasetSlug>.<modelSlug>`）。加载 `cargo-storage` 以发现数据集和模型Slug，并在需要列类型或SQL方言时获取DDL。
- 对于针对编排运行时表（`runs`、`batches`、`spans`、`records`）——错误率、每节点失败、时间序列——使用 `cargo-ai orchestration query execute "<sql>"`。工作区作用域是自动的；表无需模式前缀即可引用。
- 在构建工作流节点图之前，加载 `cargo-connection` 以获取 `connectorUuid` 和 `actionSlug`。如果任何节点调用**基于信用的提供者操作**，也加载 `cargo-gtm` 并读取该提供者的剧本（`../cargo-gtm/provider-playbooks/<slug>.md`）——如果工作流是计划工具或剧本，则包括其**重复使用**部分，因为配置错误或错误的时间表会导致每次运行都重新计费。即使任务通过 `cargo-orchestration` 或 `cargo-project` 直接到达，没有 GTM 框架，这也适用。
- 在执行使用代理节点的工作流之前，加载 `cargo-ai` 以获取 `agentUuid`。
- 运行完成后，加载 `cargo-analytics` 以下载结果或衡量性能。**对于操作输出检索，优先选择 `cargo-ai orchestration run download-outputs` 而不是 `run download`——前者返回仅包含输出节点数据的签名URL CSV/JSON。**
- 加载 `cargo-billing` 以了解上述任何操作的信用消耗。
- 当运行失败、运行“成功但看起来不对”、批次有错误或剧本成本过高时，加载 `cargo-diagnostics`——它将 `run get` / 编排-SQL / 会计表面序列化为法医运行簿（跟踪单个运行、扫描批次、分析信用支出）。
- 在你开始查找之前得知问题——错误率激增、成本上限、节点缓慢、同步停滞、工作流停止运行——加载 `cargo-observability`。它创建**警报**：对同一遥测（`spans`/`runs`/`records`）、模型健康或SQL查询的定期阈值检查，在违规时触发操作。诊断是**反应性**的（解释发生了什么）；可观察性是**主动性**的（提前发现）。警报也可以通过 CDK 的 `defineAlert` 以代码方式声明。

---

## 每个技能的关键规则

每个技能的非明显规则——如果你猜测错误会导致无声失败或成本——每个技能自己的 SKILL.md 包含完整表面；这些是在选择之前值得了解的。

### cargo-gtm

**提供的配方：**

| 配方 | 在...时使用 |
|---|---|
| `recipes/source-planning.md` | 在花费之前决定来源：探测候选者、每击打成本。 |
| `recipes/prospecting.md` | 端到端查找→丰富→验证→同步（P1/P2/P3 变体）。 |
| `recipes/build-tam.md` | 大规模构建可扩展市场列表（100–10,000 家公司）。 |
| `recipes/linkedin-url-lookup.md` | 从名称+公司解析 LinkedIn URL，严格验证。 |
| `recipes/portfolio-prospecting.md` | 投资者 / 加速器→投资组合公司→联系人。 |
| `recipes/job-change-monitoring.md` | `waterfall.detectJobChange`（cargo-独特）在联系人分段上。 |
| `recipes/funding-watch.md` | 跟踪最近获得资金的公司。 |
| `recipes/tech-intent.md` | 根据技术栈或招聘意图信号查找公司。 |
| `recipes/icp-discovery.md` | 比较已关闭-成功与已关闭-失败分段，暴露 ICP 信号。 |
| `recipes/custom-datapoints.md` | 设计要收集的自定义属性+实时信号，基于真实来源和成本。 |
| `recipes/outreach-activation.md` | 将信号分段转换为可发送的触达（丰富→验证→个性化→序列器交接）。 |
| `recipes/ads-audience-activation.md` | 将分段推送到 Google Ads Customer Match / LinkedIn Matched Audiences。 |
| `recipes/review-and-iterate.md` | 人类审查循环用于判断输出；更正成为永久规则。 |
| `recipes/re-engagement.md` | 仅在新鲜信号触发时唤醒陈旧联系人（工作变动、资金、技术意图）。 |
| `recipes/lost-deal-revival.md` | 通过分支 `lost_reason`（冠军离职、预算、时机）复兴已关闭-失败的 CRM 交易。 |
| `recipes/account-expansion.md` | 多线程客户账户——净新买家、与联系人模型去重。 |

**优先提供者堆栈**（配方以此开头）：salesNavigator（来源）、aiArk（LinkedIn-锚定的丰富+目录中最便宜的公司丰富和搜索）、waterfall（多源丰富+邮件验证+工作变动）、FullEnrich（高级联系人查找）、apolloio（1-信用细分覆盖丰富）、theirStack（技术栈+招聘意图）、peopleDataLabs（重型回填）。**已有 LinkedIn URL（或事件 URL）？** 不要来源——直接前往 `aiArk.enrichPerson`（0.1，个人资料**+验证邮件**，无邮件不收费），或 `linkedin`（`enrichProfile`/`enrichCompany` 0.25，`extractEventAttendees`）当你不需要邮件时；这些是最便宜的 URL-锚定丰富，很容易错过，因为上面的堆栈是来源优先。

**关键规则：**
- **可接受使用门槛每个接触人的步骤**（`../cargo-gtm/references/acceptable-use.md`）：仅限从许可提供者获取的 B2B 专业身份，任何触达步骤前有三个免费阻止检查（*基础*、*抑制*、*相关性*），以及拒绝列表——无差异化扩散、消费者定位、无明确来源的列表、联系被抑制的记录、过滤或身份规避、自动拨号、批量 LinkedIn 参与行动。包永远不会发送：触达在用户的自己的序列器准备好的变量处停止。
- 所有配方使用基于信用的操作——**176** 个 513 个目录暴露的操作，价格在 [`../cargo-gtm/references/credits-cost-table.md`](../cargo-gtm/references/credits-cost-table.md) 和从 `cargo-ai orchestration action list --kind connector` / `--kind native`（免费，读取目录）重新生成的，每个计费操作返回 `credits` 数组。其他 337 个操作不携带*提供者*价格——但运行在工作流中的任何操作都不是免费的：**每个节点执行计费 0.01 信用（100 个计 1）**，结构原生（`branch`、`filter`、`switch`、`variables`）也包括在内。成本表定价操作，不是步骤；参见 [`../cargo-billing/SKILL.md`](../cargo-billing/SKILL.md) → “执行费用”。
- 操作形状：`{"kind":"connector","integrationSlug":"<slug>","actionSlug":"<slug>"}`——顶层操作没有 `config`，并且**`connectorUuid` 永远不嵌套在其中**；它位于节点顶级。
- 输出检索：`cargo-ai orchestration run download-outputs --output-node-slug <slug>`（不是 `run download`）。
- peopleDataLabs 过滤形状：`searchX` 使用 cargo 的 `{conjonction, groups, conditions}` 形状；`queryX` 接受 PDL **SQL 字符串**——永远不会 Elasticsearch。

### cargo-orchestration

**关键规则：**

- 在 `../cargo-orchestration/SKILL.md` 顶部查看决策流程图，了解何时使用 `action execute` vs `run create` vs `batch create`。
- **第一次尝试时永远不要注册完整批次。** `batch create` / `action execute-batch` 跨源中的每条记录扩散。抽样 **10–20 条记录**，报告观察到的成本+命中率，然后要求用户批准完整注册——引用**记录数**和**信用估计**。机制：`../cargo-orchestration/SKILL.md` → “创建批次”；支出规则：`../cargo-gtm/references/cost-discipline.md` §1。
- **搜索操作；永远不浏览目录。** `cargo-ai orchestration action list <keywords> [--kind connector|native|tool|agent] [--integration-slug <slug>] [--limit 20]` 覆盖集成目录、Cargo 原生操作、工作区工具和代理，一次免费调用，并返回可粘贴的 `action` 对象（`connectorUuid` 解析）以及操作的**信用成本**。其兄弟 `cargo-ai connection action search <keywords>` 仅限连接器，但添加 `--credits-only` 和 `--category`，这是 `action list` 缺少的两个过滤器。两者都比分页 `connection integration list` 更好；一旦选择了操作，需要其完整输入模式时，才使用 `integration get <slug>`。
- **在 `action execute` / `action execute-batch` 上省略 `config`**——输入在 `--data` / `--records` 中。这就是 `action list` 返回的形状，所以可以直接粘贴。**`action get-output-schema` 是例外，仍然需要它**（`400` 在没有 `"config": {}` 的 `action.config` 下），以及工作流**节点**、警报 `--actions`、剧本 `healthAlertActions`，以及代理 / MCP-server `--actions`。输入错放在 `config` 中会被丢弃而不是拒绝——操作在没有输入的情况下运行，错误永远不会提到 `config`。
- **`action execute` 是运行操作的默认值；`node execute` 仅用于调试。** 仅用于测试您正在编写的单个工作流节点——它需要 `--workflow-uuid`、`--release-uuid`、`--node`、`--computed-config` 和 `--context`（全部五个）。其他任何操作——丰富记录、调用连接器操作、调用工具或代理——都通过 `action execute` / `action execute-batch`。
- **在构建节点图时优先使用内置操作+表达式。** 避免使用 `python`、`script`（JS）和原始 HTTP 节点，除非必要：使用 `variables` 进行转换，使用原生 `agent` 节点进行 LLM 调用，使用集成专用连接器操作进行 API 调用，使用 `branch`/`filter`/`switch` 进行路由。参见 `../cargo-orchestration/references/node-selection.md`。
- **显示节点图，不要描述它。** 在部署草稿之前，以及每当用户询问工作流或剧本做什么时：`cargo-ai orchestration node diagram --workflow-uuid <uuid> --raw`（免费，运行无操作，CLI ≥ 1.0.54；`references/node-diagram.md`）。路由、回退边、哪些节点计费是正在批准的。让命令绘制它而不是转录——节点 **slugs 在一个发布中重复**，所以手绘图按 slug 键控合并节点。
- 过滤 JSON 使用 `conjonction`（不是 `conjunction`）——拼写错误会无声失败。
- 使用 `cargo-ai orchestration query execute "<sql>"` 对编排运行时表（ClickHouse）进行查询，针对 `runs`、`batches`、`spans`、`records`（无模式前缀；工作区作用域自动）。

- **创建前预览** `alert preview --scope … --threshold … [--window-minutes 60]` 现在不触发执行——这是衡量阈值与现实匹配的唯一方式，可以在它成为每次都会出错的计划之前捕获无效的作用域/阈值配对（结果：`"notComputed"`）。
- **作用域和阈值是一对**。遥测指标（`errorRate`、`duration`+聚合、`credits`+聚合、`count`）需要`spans`/`runs`/`records`；`query`需要一个查询作用域；`recordsCount`/`recordsShare`/`freshness`/`syncDuration`需要`model`。完整矩阵+单位在`references/scopes-and-thresholds.md`中。
- **空窗口与真实零**。大多数指标将空闲窗口报告为`empty`（健康，不触发）。只有`count`和`recordsCount`返回真实的`0`——与`lte 0`配对以实现**死马开关**（当工作流*停止*、模型*清空*时触发警报）。
- **触发最多一次且消耗积分**。操作作为运行（`runUuids`在事件上）触发；持续的违规每秒重新触发一次，只要它仍然为真，永远不会在相同的行上再次触发。如果操作调用付费提供者，请应用`../cargo-gtm/references/cost-discipline.md`——计划的警报会在每次违规时重新计费。
- **`--enabled`是严格的**（仅`true`/`false`）；模型作用域`filter`使用**`conjonction`**指定的分段形状。
- 权限是`observability:read` / `observability:write`（非仅管理员）。声明性等效物是CDK的`defineAlert`——参见`cargo-project`。

### cargo-storage

**关键规则：**

- 通过`cargo-ai storage query execute "<sql>"`（或`storage query download --query "<sql>"`用于完整导出）使用`<datasetSlug>.<modelSlug>`表名（例如`default.companies`）进行查询。`model get-ddl`是可选的——用于列类型和SQL方言。
- 对编排运行时表（`runs`/`batches`/`spans`/`records`）的SQL，使用`cargo-ai orchestration query execute "<sql>"`——在`cargo-orchestration`中记录。
- 对于高级记录查询（过滤、排序、分页），使用`segmentation segment fetch`——在`cargo-segmentation`中记录。
- `storage relationship set` **替换**数据集的整个关系集——从负载中缺失的任何内容都会被删除。先`list`，然后发送完整的数组回来。

### cargo-segmentation

**关键规则：**

- 过滤JSON使用`conjonction`（不是`conjunction`）。拼写错误**不是**错误——过滤器静默匹配无内容。
- **在花费之前先确定大小**。`segment fetch --limit 1`免费计算内联过滤器；保存段的`recordsCount`是权威的大小。在提出任何针对受众的付费运行之前引用它。
- `segment download`需要`--model-uuid`**加上过滤器**，而不是`--segment-uuid`。
- `change list`需要`--segment-uuid`；`change fetch`需要一个**变更**UUID加上`--kinds`（`added`/`updated`/`removed`/`unchanged`）。
- `updatedRecordsCount`除非段使用`--tracking-column-slugs`创建，否则保持`0`——这些列定义了“更新”的含义。
- 名为`GENERATED_PLAY_SEGMENT`（`fromPlay: true`）的段属于一个play。手动编辑或删除它们。

### cargo-connection

**关键概念：**

- **集成** = 外部服务类型（HubSpot、Clearbit、Salesforce、…）
- **连接器** = 集成经过身份验证的实例（在节点中引用`connectorUuid`）

### cargo-ai

**关键规则：**

- 用于RAG的知识通过发布的`resources`附加到代理：**文件** + **库**来自[`cargo-content`](#cargo-content)。使用`release update-draft --resources …`然后`release deploy-draft`将它们连接起来。
- **`cargo-ai mcp`不带`--server`现在桥接第一方平台MCP**（`mcp.getcargo.io/mcp`），而不是“工作区的唯一MCP服务器”。`ai mcp-server`仍然构建一个精选服务器；使用它的uuid与`--server`。参见上面的“这些技能与Cargo的MCP表面”。
- **CLI ≥ 1.0.19：** 文件和库已从`ai`域移至顶级**`content`**域（现在是`cargo-content`技能）。旧的`cargo-ai ai file …`命令不再存在。

> 对于使用代理（发送消息、多轮聊天、轮询），请使用`cargo-orchestration`。

有关按用例使用模型和温度的指导，请参阅`../cargo-ai/SKILL.md`。

### cargo-content

**关键规则：**

- CLI ≥ 1.0.19中的新顶级**`content`**域——`cargo-ai content file …` / `cargo-ai content library …`。旧的`cargo-ai ai file …`路径已消失（`unknown command`→你处于旧路径；升级CLI）。
- 文件或库在附加到代理的已部署发布`resources`之前是惰性的——该连接存在于[`cargo-ai`](#cargo-ai)中。
- 上传的内容文件在`cargo-context`运行时沙盒的`.files/`下也是可读的（只读）。
- 对于批量运行**输入**文件（驱动批量的CSV），请使用`cargo-ai workspaceManagement file upload`（不同的界面）——参见`cargo-workspace-management`。

### cargo-context

**关键概念：**

- **上下文存储库** = 支持工作区上下文的GitHub存储库。规范示例：[`getcargohq/cargo-workspaces`](https://github.com/getcargohq/cargo-workspaces)。文件使用`kebab-case.md`名称，YAML前体带有必需的`title` + `description`，以及`domain/slug`交叉引用（无`.md`）。
- **运行时沙盒** = 上下文存储库的可执行副本。`runtime write`和`runtime edit`推送到默认分支；`runtime execute`不推送到默认分支。
- **知识图谱** = 每个md/mdx文件的类型化图，带有前体和每个节点的出站交叉引用。通过`cargo-ai context graph get`构建。

**关键规则：**

- `runtime write` / `runtime edit`提交并推送。`runtime execute`是短暂的——用于`grep`/`ls`/检查，绝不用于持久更改。
- `runtime edit --old-string`必须与文件内容**完全匹配一次**。先读，然后原样复制空格。
- 在每个`.md`/`.mdx`文件上设置`title` + `description`前体——这是一个**强约定，未强制执行**：缺失/格式不正确的前体仍然会提交，但索引效果不佳（图会回退到文件名+第一段，并读取`summary`，而不是`description`）。
- 图**边**仅从前体`references:`、Markdown链接或维基链接形成——纯文本行在文本中不会创建边。在`references:`中引用源文件。
- 对于域、约定和每个域模板，请参阅`../cargo-context/references/conventions.md`。

**生命周期：**

- 要从域（ICP、角色、证据、信号——幂等，跳过已播种的域）引导新工作区的上下文，请参阅[`../cargo-context/references/examples/bootstrap-from-domain.md`](../cargo-context/references/examples/bootstrap-from-domain.md)。
- 要了解完整的引导+持续的调用驱动刷新剧本（阶段1+阶段2+节奏），请参阅[`../cargo-context/references/examples/lifecycle.md`](../cargo-context/references/examples/lifecycle.md)。

### cargo-hosting

**生命周期：** `init`（本地脚手架）→ `create`（槽位+工作区唯一slug）→ `deployment create`（构建+上传）→ `deployment promote`（上线）。

**关键规则：**

- `--slug`是**每个工作区**唯一的；在线主机是`<slug>-<工作区前缀>.<根>`，并且应用和工作者有不同的根。因此，从`get`读取`url`而不是组合它。应用→工作者调用因此是**跨域**：工作者必须响应CORS。
- **`CARGO_API_TOKEN`永远不会注入。** `createCargoApi`在没有它的情况下会引发错误。铸造一个令牌并将其作为秘密环境变量存储：工作区范围的`workspaceManagement envVar create --secret`，或通过CDK `defineWorker({ env })` / `POST /v1/hosting/env-vars`（因为`hosting` CLI在1.0.96中没有环境命令）。环境变量在上线时绑定，因此**更改后重新部署+上线**。
- 工作者`catch`返回清理错误必须首先`console.error(err)`。只有未捕获的错误会带有堆栈记录到日志中。
- **部署不等于上线。** `deployment create`构建；URL仅在`deployment promote`时移动。`deployment get-promoted`显示当前在线的内容。
- `--source`是**包根目录**，不是`dist/`——构建在服务器端运行：如果`package.json`声明了一个（它拥有整个构建），则应用自己的`build`脚本；否则，检测到的框架的默认值（`vite build`、`next build`、…）；为工作者捆绑。
- 应用环境变量需要一个公共前缀（`VITE_`、`NEXT_PUBLIC_`、…），被编译到公共捆绑包中，并且**不能是秘密**（`secretNotSupportedForApp`）。
- Cargo拥有的主机发送`X-Robots-Tag: noindex`；应用仅在自定义域（`POST /v1/hosting/custom-domains`）上使用预渲染的HTML时才可被索引。
- 构建是异步的——在上线前轮询`deployment get`直到终端。
- `--app-uuid` / `--worker-uuid`在部署命令中互斥；`remove`级联到部署。
- 文件夹来自[`cargo-workspace-management`](#cargo-workspace-management)；`--folder-uuid null`移动到根。

### cargo-project

TypeScript中的整个Cargo工作区（`defineConnector`/`defineModel`/`defineAgent`/
`definePlay`/`defineTool`/`defineMcpServer`/`defineContext`/`defineSegment`/
`defineFolder`/`defineFile`/`defineWorker`/`defineApp`/`defineAlert`/`defineDomain`/
`defineMailbox`）并将其与在线基础设施进行`cargo-ai project`协调。涵盖**所有**资源类型，因此它与上述“声明性vs命令式”重叠。

**生命周期：** `project init`（从`getcargohq/cargo-manifest`脚手架——上下文、节奏和评估，以及它部署的`infra/`中的资源）→ `project types`（工作区类型配置）→ 编写`define*`文件→ `project plan`（离线差异）→
`project deploy`（创建/更新，写入状态）→ `project destroy`。还包括`refresh`（漂移）、`import`（采用现有）、`pull`（从在线工作区生成`define*`并采用）、`rollback`、`check`（验证，无状态）、`info`（这里是什么）、`state`（检查/重定向）。

**关键规则：**

- **提交`cargo.state.json`**——但要知道它是一个**指针**（`{"stateUuid": "…"}`），不是状态。部署状态存在于工作区中，并且是部署的play/代理/警报的*唯一*句柄（无slug）；丢失指针，`project state bind`可以恢复它，丢失状态，它们会变成孤儿。`project state list|create|bind`。
- **通过句柄连接，而不是`.uuid`**——传递`define*`句柄或`xxRef("uuid")`。
- **三个值助手，而不是一个。** `secret("ENV_VAR")`在部署时读取*您的*环境，并保持在状态和内容哈希之外（因此旋转密钥需要`deploy --refresh`才能实际落地）；`env("ENV_VAR")`故意进入哈希；`workspaceEnv("NAME")`是服务器重新读取的指针，因此在工作区中旋转它不需要重新部署。
- **`--yes`** 对于非交互式`deploy`/`destroy`（CI）是必需的。
- **在更改工作区集成后运行`cargo-ai project types`**以进行配置类型检查；类型检查是一个优点，没有它也能部署。
- **`definePlay`/`defineTool`与积分连接器操作图：** 在`../cargo-gtm/provider-playbooks/`中阅读提供者的剧本（尤其是其**重复使用**部分）然后再`project deploy`——部署的play会在每个计划运行时重新计费其节点。
- **发行的配方：** `recipes/scaffold-a-project.md`、`add-connector-and-model.md`、`build-an-agent.md`、`migrate-existing-workspace.md`、`deploy-from-ci.md`。

**食谱：** ~20个预写的GTM结果（TAM构建、入站流、联系人来源、账户评分、AI SDR、…）位于[`getcargohq/gtm-skills`](https://github.com/getcargohq/gtm-skills)旁边，其一次性技能。菜单是本地的：
[`../cargo-project/references/cookbooks.md`](../cargo-project/references/cookbooks.md)。
在从零开始编写常见GTM结果之前检查它。

**路由问题是一次性还是持续。** “构建我们的TAM”是`cargo-gtm`，当用户今天想要一个列表时，是`tam-building`，当他们想要一个持续产生它的管道时。词语相同；倾听结果是否打算持续到来。每个食谱是一个自包含的示例，安装代理会复制到项目并调整，而不是模板来填写：
`npx skills add getcargohq/gtm-skills/<name>`。参见`../cargo-project/SKILL.md`中的注意事项和`--force`警告。

### cargo-mailbox-management

**关键规则：**

- **一个邮箱是*每月、重复*的积分费用**，不是按记录的——每个邮箱每月100–160积分（`mailboxManagement pricing get`获取实时数据），只要它存在。`mailbox remove`是唯一停止它的方法；没有暂停。在第一次`create`之前，引用舰队规模和**积分估算**每月，并得到明确的“是”。
- **此域不发送。** 交付是原生操作`sendEmail`（`{"kind":"native","actionSlug":"sendEmail"}`，输入在`--data`中），**每次发送0.1积分**，通过`cargo-orchestration`运行。调用它的play**重新计费**——并重新联系。
- **量是斜坡，不是设置。** 真实发送每天5个→每天40个线性增长，持续45天从`warmupStartedAt`开始。从未运行`start-warmup`的邮箱永远锁定在每天5个，`stop-warmup`将锚点重置为第0天，并且`dailySendLimit`只能*收紧*斜坡，不能*放松*它。
- **每次发送都受`../cargo-gtm/references/acceptable-use.md` §3**（基础、抑制、相关性）约束。抑制是工作区范围的，在每次发送前检查，没有删除命令，并且`List-Unsubscribe`会自动写入它。提高斜坡——或将一个活动分布在额外的邮箱上以清除相同的量——是§2规避拒绝。
- **这里没有异步**——没有轮询的运行。例外：`mailbox create`返回`status: "pending"`，由`mailbox refresh-status`清除，而不是`run get`。
- `--type outlook`被标志接受，并且**总是**失败（`transportNotSupported`——Graph交付尚未推出）。`--statuses`/`--kinds`/`--reasons`是逗号分隔的**没有空格**。`mailbox list`是唯一**没有`count`**的列表，并且`mailbox`/`suppression`列表**没有默认限制**（最大1000），而消息/线程/事件默认为50。
- **`bounced`还没有生产者**——没有解析交付状态通知，所以退回不会写入事件，也不会自动抑制。永远不要将空的退回计数报告为干净的列表。
- **没有发送域的CLI界面。** `mailbox create --domain-uuid`是必需的，并且`domainManagement`没有`cargo-ai`命令——从Web应用程序或CDK的`defineDomain`获取UUID。权限是`mailboxManagement:read` / `:write`（非仅管理员）。

### cargo-workspace-management

**关键规则：**

- 大多数命令需要一个具有**管理员访问权限**的令牌。
- `workspaceManagement token create`需要`--name`（旧的`--from-user`标志已移除）。选择一个名称，以便在稍后的`token list`中使令牌的用途明显。
- 令牌值仅在创建时**显示一次**——立即存储在密钥管理器中（GitHub Secrets、AWS Secrets Manager、等）。
- **始终发送`workspaceManagement report create`** 当CLI出错、被错误使用，或用户或代理在执行CLI任务时遇到困难时——参见此文件顶部和`../cargo-workspace-management/references/examples/reports.md`中的部分。

### cargo-mcp

**关键规则：**

- **`whoami` 在每次会话开始时使用。** 令牌将会话绑定到唯一的工作区，且无法覆盖。错误的会话会返回属于其他人的真实记录，这会被视为成功。
- **切勿在列表上循环 `execute_action`** — `execute_action_batch` 更高效、可观察，并返回一个对象和输出 CSV 文件。
- `search_actions` 返回每个操作的 `credits[].cost`，因此在运行前请先引用价格，并在全面展开前采样 10–20 条记录。
- `query_models` 不是 SQL：它以限制和偏移量列出记录，不会聚合或连接。将这些路由到 `cargo-storage`。
- 工具列表因工作区而异 — 端点提供平台工具以及工作区使用 `defineMcpServer` 发布的内容。

## 异步轮询

所有操作都是异步的。传递 `--wait-until-finished` 以阻塞，或轮询：

| 结果类型   | 轮询命令                              | 间隔 | 终止时                                  |
| ------------- | ----------------------------------------- | -------- | ---------------------------------------------- |
| 运行           | `cargo-ai orchestration run get <uuid>`   | 2s       | `status` 是 `success`、`error` 或 `cancelled` |
| 批量         | `cargo-ai orchestration batch get <uuid>` | 5s       | `status` 是 `success`、`error` 或 `cancelled` |
| 代理消息     | `cargo-ai ai message get <uuid>`          | 2s       | `status` 是 `success` 或 `error`               |

`action execute` 返回运行；`action execute-batch` 返回批量 — 同样的轮询适用。

有关重试策略、错误处理和大型批量指南，请参阅 `../cargo-orchestration/references/polling.md`。

---

## 技能之间的 UUID 流程

参见 [`references/uuid-flow.md`](references/uuid-flow.md) — 每个跨越技能边界的 UUID 和 slug 的生产者/消费者表格 (`workflowUuid`、`modelUuid`、`connectorUuid`、`actionSlug`、…)，任何工作流运行前的标准发现顺序，以及用于在 UI 中解析 UUID 的 `app.getcargo.io` URL 模式。

---

## 端到端用例

参见 [`references/use-cases.md`](references/use-cases.md) — 8 个实际操作的食谱（单记录丰富、批量+CRM 同步、AI 领域评分、从头开始的自定义工作流、错误监控、新工作区引导、带过滤+排序的段导出、GTM 上下文审计）展示应加载哪些技能以及每个操作的命令序列。

---

## 常见陷阱

参见 [`references/gotchas.md`](references/gotchas.md) — 静默失败的陷阱和经常混淆的命令对（`conjonction` 拼写、`run create` vs `batch create`、`--model-uuid` vs `--segment-uuid`、存储查询表命名、令牌仅显示一次、发票分、第三方连接器速率限制、`context runtime execute` vs `write`/`edit`、…）。
