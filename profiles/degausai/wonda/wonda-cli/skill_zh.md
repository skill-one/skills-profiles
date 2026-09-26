# Wonda CLI

Wonda CLI 是一款基于终端的内容创作工具包。使用它来生成图片、视频、音乐和音频；编辑和组合媒体；发布到社交平台；以及在领英、Reddit 和 X/Twitter 上进行研究和自动化。

## 安装

如果 PATH 中找不到 `wonda`，请先安装它。推荐的安装方式是已签名的桌面安装程序（包含 CLI、托盘图标和始终在线中继，无需额外步骤）：macOS `brew install --cask degausai/tap/wonda-app`（或从发布版下载 wonda-macos.pkg），Windows winget/wonda-windows-setup.exe。下面的 CLI 仅通道可以在任何地方使用，并且可以使用 `wonda app install` 后续添加桌面应用：

```bash
# npm
npm i -g @degausai/wonda

# Homebrew
brew tap degausai/tap && brew install wonda
```

## 设置

- **认证**：`wonda auth login`（打开浏览器，推荐）或设置 `WONDA_API_KEY` 环境变量
- **验证**：`wonda auth check`

### OAuth 连接器认证

Claude web 和 Cowork 连接器使用 Wonda 的 OAuth 2.1 流程，而不是 CLI API 密钥字段。连接器通过浏览器登录 Wonda，授予请求的账户访问权限，并接收与 Wonda API 资源绑定的 OAuth 令牌。服务器仅在 Wonda 内部将令牌交换为账户的内部 API 密钥，因此代理和连接器主机永远不会看到 `sk_...` 密钥。对于 CLI 和本地 stdio MCP 路径，继续使用 `wonda auth login` 或 `WONDA_API_KEY`。

### Claude Cowork 本地中继

Claude Cowork（桌面应用）在主机上运行本地 MCP 服务器，因此它可以直接加载 `.mcpb` 套件或本地 stdio `wonda-mcp` 配置，WAB 包含在内（已验证 2026-07-07）。Claude web 无法做到。Wonda 本地中继是替代路径：它允许 REMOTE 连接器（web 或 Cowork）在用户自己的 Mac 和住宅 IP 上执行操作，而无需任何本地 MCP 配置：

1. 登录状态下打开 `https://wonda.sh/download` 并安装已认证的 Mac 包。
2. 使用 `wonda relay pair` 或首次运行时的浏览器手递手来配对中继。这使用现有的 `cli-auth` 流程，并将具有中继范围的 `wrelay_...` 凭证存储在 macOS Keychain 中。不要要求用户粘贴 API 密钥或设备代码。
3. 打开 `https://wonda.sh/setup`，通过全屏本地 WAB 连接领英、X 和 Reddit，然后在 Claude 中一次批准 Wonda 连接器。

引擎策略是 `auto | my_machine | cloud`。`auto` 在在线时使用本地中继，否则使用云端。`my_machine` 必须不会静默回退：如果中继离线，请询问是否切换到云端。

### 组织和支出上下文

Wondercat 组织是具有自己的座位和计费的共享钱包。
成员可以通过切换上下文从组织钱包支出（而不是使用个人积分）：

- `wonda organizations list`（别名：`wonda orgs list`，`wonda org list`）— 查看您所属的每个组织及其角色和座位计划。
- `wonda use --org <slug>` — 此机器的粘性组织上下文。为每个请求设置 `X-Wonda-Org`；通过组织钱包持有、扣费和 `wonda balance` 路由。
- `wonda use --personal` — 返回个人。
- `wonda usage` — 某段时间的支出仅使用摘要（总计 + 按模型 + 按项目细分）（`--month 2026-05`，或 `--from`/`--to`；默认为当前月份，UTC）。`--project <name>` 将报告限制为单个项目。在组织上下文中，它报告组织范围的支出，包括按成员细分 — 需要 admin/owner 角色。管理员还可以从 Web 上组织页面下载完整的 Excel 报告。

### 项目（支出标记）

项目将支出归因于命名的业务流程以进行监控。代理应在任务开始时检查活动项目（`wonda use` 会打印它），并且在操作员按项目监控支出时为每个任务设置一个项目：

- `wonda use --project <name>` — 粘性：每个后续扣费都带有项目（在 `wonda usage`、API 和组织 Excel 报告中）。`wonda use --no-project` 停止标记；切换组织/个人上下文会自动清除项目（项目是按范围划分的）。
- 任何命令上的 `--project <name>` — 仅针对该调用的单次覆盖。
- `wonda project list|create|delete` — 在活动范围内管理注册表。组织项目仅由组织管理员/所有者创建；个人项目是自助服务的。针对不存在的名称进行标记会失败，显示 `unknown_project`（没有静默新桶，因此拼写错误不能分割监控数据）。

`wonda topup` 总是充值您的**个人**钱包，无论上下文如何。充值组织钱包（和配置自动充值）仅限管理员，并在 Web 上通过 `/organizations/<slug>` 进行。如果成员用完组织积分，错误会提示他们要求管理员或切换回个人 — 他们无法从 CLI 充值组织钱包。

组织内的角色与座位计划是分开的：

- **所有者**：原始创建者。不能降级或踢出。可以从组织页面将所有权转移给组织中的另一个成员（很少见）。
- **管理员**：可以邀请（单个或通过粘贴批量邀请）、踢出、更改角色、更改座位、充值、配置自动充值、更改月度限制。
- **用户**：只能使用组织钱包支出（如果管理员设置了，则受每个成员每月限制约束）。

付费组织座位（`WONDA` / `WONDA_PREMIUM`）与个人付费计划一样，提供相同的付费功能访问（技能等），但仅在组织上下文中有效。`wonda use --personal` 会回退到用户个人账户计划。

### 访问层

Wonda 仅限付费：每个产品界面都需要付费计划，包括 API 调用、本地平台读取、浏览器自动化、媒体组合、文件编辑、诊断、生成、发布、抓取、分析、技能、中继操作和云孪生。在执行任何产品命令之前，CLI 会针对 Wonda 执行实时授权检查。当无法验证访问权限时，检查会失败关闭。新账户在订阅之前没有任何产品访问权限，正面的信用余额不能替代计划。

| 层级                                        | 访问权限                                                                                                                                                                                                                                                                              |
| ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **匿名**（未登录）                          | 没有产品访问权限。认证、配置、定价、组织发现/选择、shell 完成和本地关闭命令仍然可用，以便用户可以订阅、恢复或停止后台服务。运行 `wonda auth login`，然后订阅。                                                                                       |
| **免费**（已登录，没有付费计划）              | 没有产品访问权限。在 https://wonda.sh/account 订阅以使用产品。                                                                                                                                                                                                                      |
| **WONDA**（`$19.99/月`，"Pro"）                  | 除云孪生之外的一切：生成（`image/generate`，`video/generate`，...）、媒体上传/下载、发布、抓取、分析、视频分析、技能（`wonda skill install/list/get`）、过渡、剪辑、电子邮件、reddit/linkedin 账户创建、样式、品牌。 |
| **WONDA_PREMIUM**（`$49.99/月`，"Premium"）      | WONDA 中的一切，加上**云孪生**（`wonda twin`：配置、计划运行、流式登录）具有反检测/影子封禁保护、无限制，以及美国账户创建。                                                                                                                                             |
| **标记**（按账户 PostHog 关闭开关）            | 包含在付费计划中，但仍然可以通过按账户标记进行门控：`wonda reddit signup`（redditAccountCreationEnabled）、`wonda email`（emailServerApiEnabled）、公开 LinkedIn 个人资料增强（linkedinProfileEnrichmentEnabled）。                                             |

如果命令返回 `403`（`paid_plan_required`），请在 https://wonda.sh/account 订阅。

这也适用于本地 stdio MCP 路径，因为 MCP 执行相同的 CLI。平台 cookie 和数据保留在设备上，但命令必须首先从 `GET /api/v1/auth/access` 接收成功的付费访问决策。仅中继安装可以使用其范围的 `wrelay_...` 凭证进行该授权探测。范围的凭证仍然无法调用普通账户 API。

### 语音克隆

从 10 秒以上的音频片段克隆语音并在 TTS 中使用。硬限制：每个账户最多 20 个克隆语音。成本：每个克隆 1.50 美元。

```bash
# 从本地文件克隆（首先自动上传到媒体库）
wonda voice create "Andu" --file ./sample.mp3 --description "我的声音"

# 从现有的 wonda 媒体克隆
wonda voice create "Brand" --media-id <uuid>

# 可选的源音频预处理
wonda voice create "Clean" --file ./raw.wav --降噪 --标准化音量

# 列出克隆的语音（每行报告 isExpired 和 expiresInDays）
wonda voice list

# 一个语音
wonda voice get <voice-id>

# 重命名/重新描述（仅本地，无提供者调用）
wonda voice update <voice-id> --name "新名称" --description "..."

# 删除
wonda voice delete <voice-id>
```

**使用克隆的语音在 TTS 中**：通过 `voice get` 中的 `providerVoiceId` 作为 `voiceId` 传递给 `/audio/speech`：

```bash
wonda audio speech "Hello world" \
  --model minimax-speech-2-8-hd \
  --params '{"voiceId":"<providerVoiceId>"}'
```

**7 天过期**：未在 7 天内使用 TTS 的克隆语音会自动过期。使用克隆语音运行 TTS 会自动刷新其过期。过期的空闲语音必须重新克隆（再次 1.50 美元）。

### 凭证保险库

持久化在外部平台（Instagram、TikTok、Twitter 等）上创建的登录，以便下次运行时可以重用。密码使用 AES-256-GCM 加密，使用服务器端密钥，仅在 `get` 时解密。

```bash
# 创建
wonda credentials create --website instagram.com --username myhandle \
  --email me@example.com --password-stdin <<< "hunter2" \
  --metadata '{"signup_source":"wonda-email"}'

# 列出（省略密码）
wonda credentials list --website instagram.com

# 获取完整记录，包括解密的密码
wonda credentials get <id>

# 更新任何字段（使用 --password-stdin 旋转；--username "" 清除）
wonda credentials update <id> --username newhandle

# 删除
wonda credentials delete <id>

# 拉取并记录您使用它的原因在一个调用中 — POST，而不是 GET，因为它会写入带有原因的 'used' 事件。尽可能使用此方法而不是 `get`，因为您可以说明原因。
wonda credentials use <id> --reason "instagram signup flow"

# 查看最近事件（创建/使用/旋转/更新）以进行审计
wonda credentials events <id>
```

字段：`website`（必需 — 类似 `insta` 的输入会规范化为 `instagram.com`），`username`，`email`，`password`（必需），`metadata`（任意 JSON）。`username` / `email` 至少必须有一个存在。允许 `(website, username)` 的多个记录 — 如果需要，请您自己进行去重。

**事件日志**：每个 `credentials get`/`use`，`create`，密码旋转和其他更新都会作为事件记录在凭证上（操作者：`cli` | `web` | `system`）。使用 `credentials events <id>` 或 Web UI 的历史记录图标进行审计。事件日志是追加的，并且在凭证删除时级联。

### 全局输出标志

所有命令都支持这些输出控制标志：

- `--json` — 强制 JSON 输出（当 stdout 被管道时自动启用）
- `--quiet` — 仅输出主要标识符（作业 ID、媒体 ID 等）— 脚本的理想选择
- `-o <path>` — 下载输出到文件（隐含 `--wait`）
- `--fields status,outputs` — 选择特定的 JSON 字段
- `--jq '.outputs[0].media.url'` — 使用 jq 表达式过滤 JSON 输出

### CLI 公告和弃用警告

在每次命令中，CLI 会轮询 `GET /api/v1/updates`（匿名，1 小时缓存 `~/.wonda/state.json`）以获取活动公告：弃用通知、事件提示、升级提示。消息仅打印到 stderr，因此 stdout/JSON 保持干净，可用于管道。

请求级别的弃用提示作为标准的 `Warning: 299 - "<message>"` HTTP 头到达，并由 CLI 的 HTTP 客户端作为 `[deprecated METHOD /path] <message>` 显示到 stderr。

使用 `WONDA_QUIET=1`（环境变量）或 `--quiet`（标志）静音两个通道。仅禁用网络检查 `WONDA_NO_UPDATE_CHECK=1`。

### WAB / Wonda 自动化浏览器（`wonda wab`）

**1Password 包含在本地 WAB 配置中。** WAB 下载官方稳定的 1Password 浏览器扩展，验证其发布者签名，并在首次设置时将其固定到工具栏。使用 `wonda wab show <persona>` 打开 WAB，然后点击 1Password 进行登录。每个 persona 保留自己的 1Password 会话。桌面应用可能需要您批准 WAB 作为附加浏览器；直接在扩展中登录也有效。缓存的扩展文件可以在离线状态下工作。WAB 在 persona 启动时最多每天检查一次缓存的扩展更新，包括失败的检查；更改 Chromium 版本会触发兼容性检查。如果扩展从未成功安装，每次启动都会重试安装。已经运行的浏览器在其下次启动时拾取扩展更新。启动和 `wab install` 会修剪 7 天前未使用的缓存版本；正在运行的 WAB 进程使用的版本会被保留。在启动 WAB 之前设置 `WAB_ONEPASSWORD=0` 以跳过捆绑扩展。匿名捕获、临时会话和云孪生不会加载它。包含逗号的 Wonda 数据路径也会跳过 1Password，并附带驱动程序日志警告；使用不带逗号的 `WONDA_HOME` 路径以启用扩展。增强型安全浏览或管理员策略也可以阻止自动加载扩展；WAB 在其驱动程序日志中报告 Chromium 的拒绝，并保留您的浏览器设置。

Wonda Automation Browser (WAB) 是一款付费的隐蔽反检测浏览器，经过强化，平台无法将其指纹为自动化。`wonda wab` 是反检测 Chromium 堆栈（未检测的 Playwright 分叉）的唯一命令。它有两个面：

- **认证会话。** 每个 persona 一个持久的全屏 Chromium，用于保存领英、X、Reddit 和朋友的登录会话。CLI 按需启动它，允许它空闲，并在每次命令运行 `--via wab` 时通过它路由平台读取/写入。Cookies 存储在 persona 的 Chromium 配置文件中，而不是 `~/.wonda/config.json`。
- **匿名捕获。** `wonda wab screenshot <url>`，`wonda wab record <url>` 和 `wonda brand extract` 驱动一个具有新鲜指纹、无 persona 和无 cookies 的临时 Chromium。截图支持响应式单次、批量和清单捕获。请参阅下方的截图和记录块。

心理模型：您有**账户**（每个平台一个身份）。每个平台命令通过 flat JSON 存储（`--via cookies`，快速，无需 Chromium）或账户的 **persona**（`--via wab`，实时反检测 Chromium）路由到该账户的 cookie。persona 是可以容纳多个账户在一个指纹下的 Chromium 信封。在几乎所有情况下，persona 在首次使用 `--via wab` 时自动创建，以账户命名，因此您永远不会输入 persona 名称。

本地 `wonda.mcpb` 桌面扩展使用从 Claude Desktop 或 Claude Code 处的本地 WAB 路径：平台 cookie 保留在设备上，读取使用本地 cookie，写入使用本地 WAB。Claude web 和 Cowork 需要远程 MCP 连接器。

**本地登录是新角色的默认设置。** `wonda wab login <角色> <平台>` 会打开一个无头 WAB 窗口，并在其中登录。会话在 WAB 内部创建，因此它是独立的（在无关的 Chrome 中注销同一账户无法撤销它），并且 cookie 在 WAB 自己的指纹下生成，因此会话和浏览器身份保持一致。在第一次使用 `--via wab` 时自动创建的新角色会直接链入此流程。登录 X 后，Wonda 检测到已登录的 `screen_name` 并将其记录为角色的 X 账户绑定。现有的绑定永远不会被静默更改；检测到不同的处理手柄会产生警告。从其他浏览器粘贴 cookie（`wonda linkedin auth set`，`wonda x auth set`，...）仍然有效，并且是明确的回退方案，但手动粘贴的新 WAB 指纹上的 `li_at` 是最高风险形式。

```bash
wonda wab install                             # 一次性：npm install + 隐形浏览器 Chromium（由会话、截图、录制、品牌提取共享）
wonda wab update                              # 刷新此 CLI 固定的运行时版本（运行时版本随 CLI 发布一起提供）：分阶段下载、验证，然后原子交换，因此失败的下载不会影响当前驱动树；在角色运行时拒绝运行时交换（先停止它们；中继在下次生成时拾取新的运行时，无需重启），而已经当前的树会话刷新便宜，无需门：它将漂移的当前文件协调回此构建的嵌入字节（增量重写，在运行的角色下安全）并且仅在没有任何角色运行时修剪过时的文件，将修剪（并保持不匹配可见）推迟到树安静时；--check 报告安装与固定，不做任何更改，--force 即使当前也重新安装并重新下载共享的 Chromium 构建（损坏缓存恢复；注意：--force 在重新下载前清除缓存的 Chromium，因此失败的强制下载会留下共享缓存直到重试成功）。驱动树还携带一个记录其生成内容的清单：嵌入驱动资产身份兼容性实际上是键的，加上 CLI 构建和平台作为来源。记录的资产与此二进制嵌入集不同（或预先生成的清单）的树会在下次浏览器生成或 wab update 时自动刷新；两个构建发送字节相同的驱动资产共享一个清单，而记录的 CLI 版本可以落后于最新的兼容二进制。--check 报告清单状态（ok|absent|mismatch|unreadable）而不触摸任何内容；--json 仅更改输出格式并仍然执行更新
wonda wab start [账户]                     # 生成（默认无头；--visible 显示）
wonda wab stop [账户]                      # 优雅关闭
wonda wab show [账户]                       # 查看屏幕上的后台 WAB 以观察它（暂停 macOS 聚焦保护）；如果需要，首先将其无头启动
wonda wab hide [账户]                       # 将显示的 WAB 发送回无头，恢复静默后台操作
wonda wab screenshot [角色]                 # 角色模式：捕获已打开的标签页而不显示它；--json 仍然返回内联 base64，--output 写入文件，--tab/--full-page 可选
wonda wab screenshot <url> --output page.png   # 新的匿名 PNG 在临时浏览器中；响应式等待，注入，动画，元素，剪辑，批量，清单和诊断 JSON 控制，见下文
wonda wab browse [url] --persona <角色>     # 加载页面并像人一样滚动它：暂停，滚动，暂停，滚动；一旦滚动元素停止前进，就提前停止，见下文（纯文本输出，不是 JSON）
wonda wab menubar                              # 桌面控制，macOS 菜单栏或 Windows 通知区域：带有角落状态徽章的 Wonda 猫图标。绿色填充 = 在此运行并服务；橙色半填充 = 备用，这只能证明这台机器不是活动设备（是否是另一台设备或没有设备在服务是另一个三向徽章无法回答的问题，菜单的详细信息行仅回显最后一个中继健康检查，一个快照可能在此机器保持待机时滞后）；红色三角形 = 运行但无法服务；灰色空心 = 未在此运行。徽章也带有形状以及颜色（填充/半填充/三角形/空心）在两个平台上；macOS 会回退到带有相同状态的 🐱 文本项。点击以重启中继，一个状态跟随的停止/启动切换（`wonda relay disable`/`enable`，从不 `relay stop`），打开日志（macOS 仅限；Windows 任务以无日志文件运行中继），以及按每个运行的 WAB 显示/隐藏；工具提示包含完整状态句。底部项目“退出 Wonda”运行 `wonda app quit`（停止中继 + 禁用自动启动 + 删除每个登录时打开的机制（macOS 登录项，Windows 启动条目）+ 删除图标；退出后保持退出状态，直到应用或 `wonda app open` 再次运行）。Windows 桌面是一个消耗 `relay health --json`（状态）加上定期 `wab status --json`（角色显示/隐藏列表）并执行 wonda 语句的 PowerShell/WinForms NotifyIcon，脚本中没有平台逻辑。--stop 仅删除图标并保留中继运行
# macOS Dock 菜单：右键单击正在运行的 WAB 的 Dock 图标（🐱）以获取“在屏幕上显示”/“发送到后台”（与 wab show/hide 相同）。每个正在运行的角色都有自己的 Dock 图标，其菜单仅控制该角色。使用 WAB_DOCK_MENU=0 选择退出。
# macOS：后台 WAB 不再窃取焦点或闪烁菜单栏 / Dock 当它打开新标签页时；Dock 图标保持不变，直到你 `wab show` 它才进入前景。
wonda wab status                              # 列出角色 + 最后活动 + 浏览器上下文健康（正在运行的守护进程其 Chromium 已死显示浏览器死并带有重启提示，而不是误导性的纯文本“运行”）
wonda wab login <账户> <linkedin|x|reddit|instagram> # 推荐的新角色：打开无头窗口，用户登录，会话在 WAB 内创建（独立 + 指纹协调）
wonda wab check <账户> <linkedin|x|reddit|instagram> # 非交互式会话存活探测
wonda wab bind <角色> --x <账号> --reddit <账号> --linkedin <账号>  # 多账户高级用户路径：将 N 个账户绑定到一个角色
wonda wab record <url>                        # 匿名一次性 webm 录制（无账户，无 cookie），见下文
wonda wab sync-cookies [账户]              # 现在强制 wab → 磁盘 cookie 同步（不要等待 10 分钟定时器）
wonda wab logs [账户] --tail 100           # 尾部驱动器.log（--audit 为结构化每个命令日志）
wonda wab errors --tail 20 --since 24h        # 尾部跨角色操作失败日志
wonda wab top-failures --since 7d             # 按平台/操作/原因对本地 WAB 失败进行排名，与 DOM 恢复统计信息合并
wonda wab top-failures --platform x --json    # 机器可读的本地失败排名
wonda wab bundle-failures list                # 最近操作失败捆绑（每个失败运行一个：截图，dom，可见元素，cookie 摘要 REDACTED）
wonda wab bundle-failures show <id>           # 打印清单 + 文件树（id = unix-ms-ts 前缀）
wonda wab bundle-failures ship <id>           # 压缩到 ~/Downloads/wonda-failure-<id>.zip 以便共享
wonda wab bundle-failures prune               # 删除 30 天前的捆绑（或 --max-per-persona，--all）
# 远程监控：在每次 wab 操作失败时，我们报告（操作，平台，原因，错误字符串，has_bundle，cli_version）作为 wab_action_failed PostHog 事件，以便维护人员可以检测到用户之间的平台旋转。没有捆绑内容，没有 cookie，没有 DOM，没有截图不会离开用户的机器。选择退出：WONDA_TELEMETRY_DISABLED=1。对于服务器端细分，在 PostHog 中按 `platform`，`action`，`reason`，和 `has_bundle` 对 `wab_action_failed` 进行分组。本地，`wonda wab top-failures` 仅读取 `~/.wonda/wab/errors.jsonl` 和角色本地 `dom-recoveries.jsonl`，然后显示计数，最后看到，恢复率，捆绑计数和样本捆绑 ID。
wonda wab migrate-legacy                      # 将遗留 WAB 驱动器配置文件复制到角色槽位
wonda wab restore <角色> [时间戳]       # 从每小时快照恢复（--list 列出）
wonda wab backup disable                      # 选择退出自动推送（默认开启；现有的云备份不受影响）
wonda wab backup enable                       # 选择重新启用（自动推送同步 cookie JSON 到 wondercat 后每个磁盘同步）
wonda wab backup status                       # 显示配置 + 远程清单
wonda wab backup push [账户]               # 对所有平台绑定进行一次性手动推送
wonda wab backup pull [账户]               # 受保护的恢复到 ~/.wonda/<平台>-cookies/<账户>.json；拒绝非空本地，除非 --force
wonda wab backup pull [账户] --dry-run     # 预览恢复而不写入
wonda wab backup list                         # 云备份清单，包括设备/来源元数据（当可用时）
wonda wab backup delete <plat> <角色> [账号] # 删除一个备份
wonda wab cookies list                        # 显式 cookie 备份清单，元数据仅
wonda wab cookies status [账户]            # 本地 cookie 文件加上云备份行
wonda wab cookies port <plat> <角色> [账号] --from-device <id|label> # 安全地将一个选定的云行移植到此机器
wonda wab config set <角色> <键> <值>  # 持久化每个角色的生成默认值（空闲超时，区域设置，可见，交互，代理_url，时区，geo_lat/lon）
wonda wab config get <角色>                # 打印角色的持久化配置
```

**保持 cron 角色温暖。** 一个持续备份 cookie 仅读 cron 的角色可以使用 `wonda wab config set <角色> idle-timeout off`，然后 `wonda wab start <角色>`。然后 WAB 会保持开启，其现有的 10 分钟 cookie 同步会保持平面文件当前。仅对 cron 支持角色使用始终开启；`wonda wab config unset <角色> idle-timeout` 恢复默认 30 分钟空闲关闭。

**本地浏览器代理（`proxy_url`）。** 默认情况下，本地 WAB 直接拨号（你自己的 IP）。设置 `wonda wab config set <角色> proxy_url managed` 将本地浏览器通过你账户生成的孪生代理路由，使其与云孪生共享相同的出站（用于 IP 连续性或 VPN/办公室/CGNAT 网络）。字面值 `socks5://…`/`https://…` 是手动覆盖；清除它将恢复直接拨号。代理是可选的：如果为环境禁用生成或不可用，浏览器会回退到直接拨号。

生命周期命令接受 `--账户`（例如 `wonda wab login <账户> linkedin`）；角色自动从账户名称派生。`wonda wab bind` 是唯一一个明确命名角色的地方：当必须使用一个 Chromium 来托管具有不同平台名称的账户时使用它。

**像人一样滚动页面（`browse`）。** `wonda wab browse [url] --persona <角色>` 在角色的 WAB 中加载页面并滚动它：暂停查看页面，然后滚动，暂停，滚动，`--scrolls` 次（默认 `5`）。`--scrolls` 接受 `1`-`200`；超出该范围的值是硬错误，不是限制，并且在启动浏览器之前被拒绝。`--first-wait`（默认 `10s`）是第一次滚动前的暂停；`--wait`（默认 `5s`）是滚动之间的暂停；两者都抖动 +/-30%，因为精确重复的间隔本身就是一个指纹，并且两者都向下取整到 250ms，因此一个非常小的值不会被抖动到零——`--first-wait 0 --wait 0` 仍然在每个等待时暂停约 250ms，而不是 0，所以与 `--scrolls 200` 该下限单独加起来大约 50s。它只滚动——不点击，不参与——因此它适用于任何网站。

进度是在实际滚动的元素上测量的：当网站有填充视口的溢出容器时（LinkedIn 的信息流生活在 `<main id="workspace">` 中，其中 `window.scrollY` 从不移动），否则是文档滚动器。一旦该元素在连续两次滚动中停止前进，滚动就会提前停止，打印摘要中报告为 `(reached bottom)`，因此短页面不会在底部磨擦。无限信息流会继续滚动 `--scrolls` 的完整时间。

`--persona` 与其他 `wonda wab` 命令一样回退到配置的默认账户，并且无效的角色名称会立即被拒绝而不是静默创建一个空注销的配置文件。使用 url 时，`browse` 在其自己的隔离标签中导航（像其他每个 WAB 写入一样），并报告实际浏览的页面（在重定向后）。省略 url 会将调度到角色的共享**默认**标签——驱动器的初始页面，相同的标签 id `wonda wab show`/`hide` 引用——滚动该标签已经显示的内容。`wonda wab login` 不会留下任何东西：它会打开并导航它自己的 `<平台>-login` 标签，因此刚刚登录的角色仍然有一个未受影响的默认标签（通常仍然是 `about:blank`）。`wonda wab show`/`hide` 也不导航默认标签——它们仅切换窗口的显示/隐藏状态——因此没有一个“在那里打开页面”。实际上在默认标签上留下页面的东西是直接导航它的东西，例如 `wonda wab start --open <平台|url>`（也是 MCP `wab_open` 工具调用的东西）。**这不是从先前的 `wonda wab browse <url>` 运行中继续页面的方法**：该运行在它自己的隔离标签中导航，无 url 形式永远不会看到它。如果默认标签没有打开的页面（`about:blank`）——在登录新角色后常见的案例，因为登录的标签是分开的——命令会失败并要求 url 而不是报告一个成功的滚动为空。

`browse` 打印纯文本摘要，不是 JSON，因此全局 `--json` / `--fields` / `--jq` 标志不适用于它。

```bash
wonda wab browse https://example.com --persona <角色> --scrolls 6
wonda wab browse --persona <角色>                      # 滚动共享默认标签的当前页面，无导航
```

**匿名 PNG 捕获（`screenshot`）。** `wonda wab screenshot` 仍然有一个保留兼容性的角色模式和新的匿名 URL 模式。

`wonda wab screenshot [角色]` 仍然捕获角色的已打开标签页而不显示窗口。其现有标志保留其含义：`--tab` 选择标签，`--full-page` 捕获可滚动的页面，`--output` 写入文件。使用 `--json` 和没有输出文件时，它仍然返回 `{path, base64, mimeType}`，因此 MCP 和现有自动化接收内联 PNG 不变。

绝对 `http://` 或 `https://` 参数选择匿名模式。它启动一个全新的临时 Chromium，没有角色，cookie 或持久状态：

```bash
wonda wab screenshot \
  'http://127.0.0.1:8765/hero-lab.html#close-colorflight' \
  --output tmp/close-proof.png \
  --viewport 2048x982 \
  --scale 1 \
  --wait-until networkidle \
  --wait-for '#hero-preview' \
  --delay 700ms \
  --animations disabled
```

匿名默认值是 `--viewport 1280x720`，`--scale 1`，`--wait-until networkidle`，`--delay 0`，和 `--animations allow`。`--wait-until` 接受 `load`，`domcontentloaded`，或 `networkidle`。Wonda 自动等待 `document.fonts.ready`；`--wait-for <selector>` 等待可见元素，`--delay <duration>` 添加最终稳定延迟。`--inject-js <file>` 在导航后在异步 IIFE 中运行，因此顶层 `await` 有效。

对于确定性动画，使用 `--animations disabled` 在捕获时完成有限动画并取消无限动画，或使用 `--freeze-at 800ms` 将 Web Animations 定位到精确的时间线偏移并暂停它们。这两个选项相互冲突。`--selector '.hero-stage'` 捕获第一个匹配的元素。`--clip x,y,width,height` 捕获 CSS 像素中精确的文档坐标矩形。该矩形可以超出视口，但必须适合渲染的页面。`--selector`、`--clip` 和 `--full-page` 是互斥的捕获模式。

传递多个绝对 URL 以捕获所有内容。或者，在绝对基础 URL 后传递相对路径、查询或引号哈希参数；当存在任何相对目标时，第一个 URL 仅作为解析基础，不会单独捕获。添加 `--viewports` 以获取视口矩阵。Chromium 为整个批次只启动一次：

```bash
wonda wab screenshot http://127.0.0.1:8765/hero-lab.html \
  '#fast-close' '#close-colorflight' \
  --viewports 2048x982,1440x1000,390x844 \
  --output tmp/qa \
  --output-template '{route}-{viewport}.png'
```

对于没有 `--output-template` 的单个捕获，`--output` 是 PNG 路径。对于批次、清单或任何模板驱动的捕获，它是输出目录。`--output-template` 支持 `{index}`、`{route}` 和 `{viewport}`，展开路径必须唯一。`{route}` 会进行清理；过长的展开路径组件会使用稳定的哈希后缀缩短。`--viewport` 和 `--viewports` 相互冲突。如果没有输出标志，一个 URL 会将 `screenshot-<timestamp>.png` 写入当前目录，而批次会写入 `screenshots-<timestamp>/`。没有 `--output` 的模板相对于当前目录，或者相对于来自清单的清单目录。

严格的 JSON 清单描述了相同的时间线：

```json
{
  "url": "http://127.0.0.1:8765/hero-lab.html",
  "routes": ["#fast-close", "#close-colorflight"],
  "viewports": ["2048x982", "1440x1000", "390x844"],
  "scale": 1,
  "waitUntil": "networkidle",
  "waitFor": "#hero-preview",
  "delay": "700ms",
  "injectJs": "scripts/visual-state.mjs",
  "animations": "disabled",
  "outputTemplate": "{route}-{viewport}.png"
}
```

使用 `wonda wab screenshot --manifest visual-qa.json --output tmp/qa` 运行它。使用 `urls` 而不是 `url` 表示独立的绝对目标；`routes` 相对于 `url` 解析。清单键映射到匿名标量标志的驼峰形式，包括 `freezeAt`、`selector`、`clip` 和 `fullPage`。显式 CLI 标志会覆盖清单值。

匿名 `--json` 返回 `{ok, captures: [...]}` 而不嵌入 PNG 字节。每个捕获报告 `url`、`finalUrl`、`viewport`、`dpr`、`pageDimensions`、`consoleErrors`、`failedRequests` 和 `fontsLoaded`。成功的捕获还会报告 `path`，这意味着 PNG 已写入该路径。失败的捕获会省略 `path`、携带 `error` 并保留失败前收集的任何诊断信息。浏览器在项目失败后会继续剩余的时间线，并在任何捕获失败时以非零状态退出。使用此输出进行视觉 QA 诊断。非 JSON 输出仅打印成功生成的 PNG 路径。

**匿名视频捕获（`record`）。** `wonda wab record <url>` 将 URL 录制为 webm 格式，使用临时的 Chromium（每次调用都有新的指纹，没有 persona，没有 cookies）。用于 cookie 屏障页面（Notion 公开共享、pdf.js 渲染、任何触发 Playwright 机器人检查的网站）和营销演示捕获。

```bash
wonda wab record https://example.notion.site/page \
  --output recording.webm \
  --duration 5 \
  --viewport 960x1080 \
  --inject-js scripts/page-script.mjs   # 可选：在加载后、计时器开始前运行

# 将 webm 转换为 mp4，30 fps（隐蔽浏览器录制 webm/VP8）
ffmpeg -y -i recording.webm -t 5 -r 30 -an \
  -c:v libx264 -pix_fmt yuv420p -crf 18 recording.mp4
```

`--inject-js` 文件被包装在异步 IIFE 中，以便 `top-level await` 正常工作。它在 `domcontentloaded` + `networkidle` + 400 ms 画布稳定后运行，但在持续时间计时器开始前运行。任何 `await` 都会计算在录制窗口内。用于暗主题注入、cookie 屏障移除、滚动动画，任何需要在页面上下文中发生的事情。

Node.js 要求：wonda 需要 PATH 上的 Node >= v20。Brew 用户通过 `node` 依赖获取它；npm 用户默认就有它；`install.sh` 用户可能需要 `brew install node`（或任何 Node 发行版）。如果缺少 Node，`wonda wab install` 会将私有副本获取到 `~/.wonda/node/`。

**Cookie 云备份。** 默认开启（每台机器通过 `wonda wab backup disable` 禁用）。WAB 驱动程序在每次 wab → 磁盘同步和优雅关闭后，将每个绑定平台的同步 cookie JSON 推送到 wondercat 后端；当没有配置 `api_key` 时，自动推送不会执行。在服务器端以 AES-256-GCM 加密存储时（当 `SOCIAL_COOKIES_KEY` 设置时），否则为明文 jsonb；网络有效负载始终为明文，因为服务器持有密钥。Cookie 值永远不会由 `list/status/port` 命令打印。

恢复受到保护。`wonda wab backup pull <account>` 和 `wonda wab cookies port <platform> <persona> [account]` 除非传递 `--force`，否则拒绝覆盖非空或更新的本地 cookie 文件。强制写入会首先创建一个隐藏的 `.before-pull-*` 备份。使用 `--dry-run` 检查计划的写入。当后端为同一平台/persona/账户暴露多个设备行时，使用 `wonda wab cookies port ... --from-device <id|label>` 以明确源行。

当前后端兼容性：遗留服务器仍然为每个 `(account, platform, persona, account_label)` 暴露一个最后写入者胜出的行。较新的服务器可能包括 `device_id`、`device_label`、`source`、`status`、`generation` 和 `provenance`；CLI 在存在这些字段时显示它们，并将遗留行显示为设备 `legacy`。

源位于 `cli/wondercat/wab/`。驱动程序是 `launch.mjs`，每个平台的操作脚本位于 `actions/<platform>/`。

当选择的浏览器配置文件没有活动的平台会话 cookie 时，WAB 读取会早期失败。对于 LinkedIn、X、Reddit 和 Instagram，错误包括 `wonda wab login <persona> <platform>` 而不是显示无法解释的平台 401/403。这个预检是只读的；写入保留其现有的错误处理，原生登录本身不受影响。

**命令级传输（`--via`）。** `linkedin`、`x` 和 `reddit` 命令接受：

- `--via cookies|wab`：`cookies` 读取扁平的每个账户 JSON 存储（快速，无 Chromium）；`wab` 通过账户的 persona Chromium 路由（cookies + TLS 指纹继承自真实浏览器会话）。不支持值会大声报错，而不是静默降级。
- `--via public`：付费公共数据 API，其中命令明确支持它。对于 LinkedIn，这避免了登录 cookie 和 WAB 配置文件读取，并使用公共抓取任务路由为 `wonda linkedin profile` 和 `wonda linkedin enrich`。
- `--account <name>`：使用哪个磁盘身份（cookie 文件名 / persona）。persona 解析是隐式的：第一个 `--via wab` 使用会自动创建一个以账户命名的 persona，并在 TTY 上直接进入登录。

**读取和写入的默认值不同。** 读取命令（profile、posts、search、timeline 等）默认为 `cookies`（直接 API），因为该路径快速且检测安全。写入/参与命令（post、comment、like、follow、connect、message、mute、repost、delete）默认为 `wab`，因为 cookie-API 路径会在任何有意义的使用量上触发 LinkedIn / X / Reddit 的反滥用启发式算法。如果你明确想要使用遗留 API 路径（如果命令支持它），可以将 `--via cookies` 传递给写入命令。

**需要 `--via wab` 的命令。** 几个命令没有 cookie 路径，并且只能通过 Wonda Automation Browser 运行：`wonda linkedin comment`、`wonda linkedin reply-comment`、`wonda linkedin mute`、`wonda linkedin follow`、`wonda linkedin edit-post`、`wonda linkedin edit-comment`、`wonda linkedin delete-comment`、`wonda linkedin post --media`、`wonda x delete`、`wonda x reply --attach`、`wonda x dm send`、`wonda x dm accept` 和 `wonda x dm start`。在这些命令上，默认已经解析为 wab（一条 stderr 行注明这一点）；显式传递 `--via cookies` 会报错。Reddit 的写入（`vote`、`comment`、`subscribe`、`save`、`unsave`、`delete` 和 subreddit `submit`）也是 wab 唯一。

**运行位置（`--engine`）。** `--via` 选择传输（浏览器 vs. cookies）；`--engine` 选择位置，这两个是正交的。值：`local`（此机器的 WAB）、`cloud`（账户的云端副本，通过 twin-action API 访问，控制会话的预热隐藏在阻塞等待后面），或 `auto`（默认）。`auto` 在身份存在于此机器时解析为 `local`，在它仅作为云端副本存在时解析为 `cloud`（没有本地足迹的 persona，或从 `wonda twin provision` 缓存为 `home=cloud` 的 persona）。因此，`wonda linkedin posts <profile> --account <twin> --engine cloud --via wab` 通过云端副本的浏览器返回最近的帖子，与本地命令具有相同的结构化结果。`--via` 在两个引擎上工作方式相同：读取默认为 `cookies`，写入默认为 `wab`，并且显式支持的重写会被保留。为 LinkedIn（`posts`、`connect`、`like`/`unlike`、`comment`、`reply-comment`、`edit-comment`、`send-message`、`follow`、`mute`、`delete-post`、`edit-post`）、X（`like`/`unlike`、`bookmark`、`retweet`/`unretweet`、`follow`/`unfollow`、`delete`）、Reddit（`vote`、`subscribe`、`save`/`unsave`、`delete`）和 Instagram（`comment`）；其他动词仅在本地运行。`--engine` 可以在平台级别接受（所以 `linkedin --engine cloud posts` 和 `linkedin posts --engine cloud` 都有效），但仅在有线动词上生效；将其传递给其他读取或未有线写入是明确的错误，而不是静默的无操作。**`wonda twin run-action` 已弃用，改为 `<platform> <verb> --engine cloud`**（它仍然有效，所以正在运行的代理不会中断）。在云端，`like` 支持纯 like 和反应（`--reaction`，路由到 `react` 动作）；只有评论反应（`--comment`）目前保持本地。`auto` 在 persona 没有本地足迹且没有云端副本时解析为本地（所以首次使用的 auto-create 仍然有效），在存在云端副本时解析为云端。显式 `--engine cloud` 始终在云端副本上运行，并且永远不会回退到实时本地中继。

**每个账户的凭证。** Cookies 存储在每个账户的磁盘 JSON 文件中：

- `~/.wonda/x-cookies/<account>.json`
- `~/.wonda/reddit-cookies/<account>.json`
- `~/.wonda/linkedin-cookies/<account>.json`（自动从遗留单文件格式迁移）

每个文件是会话拥有的本地缓存，不是可移植的凭证。平台账户可以在多台计算机上拥有多个会话和云端 Twin。该文件记录了拥有设备/persona 的 WAB 会话，并且每次注入、覆盖、仅 cookie 读取、刷新和备份恢复都会首先检查该身份。CLI 不会将这些 cookies 上传到或从遗留共享托管令牌存储下载。`--force` 永远不会绕过会话不匹配。

将 `--account <name>` 传递给 `auth set` 以在当前设备上并排保留多个登录。绑定记录在 `account-bindings.json` 中，即使省略了 `--persona`，也是如此，如果匹配的 persona 的 Chromium 正在运行，则旋转的 cookies 会被推送到该实时上下文中。永远不要使用 `auth set` 从另一台设备或 Twin 复制 cookies。原生 `wab login` 更安全。驱动程序还每 10 分钟将 cookies 同步回磁盘（并在优雅关闭时），因此旋转的 cookies（ct0 周期、token_v2 服务器端刷新等）会流回 cookies 路径，无需手动重新粘贴。直接 X cookie 请求也会吸收响应 cookie 旋转到同一存储，并发送完整的存储 cookie 箱，以保留设备信任 cookies 跨读取。

云端 Twin 是其自己的稳定、始终在线会话。常规提供不会从本地 cookie 文件中为 LinkedIn 种子；使用 `wonda twin login <persona> --platform linkedin` 在 Twin 内部登录。云端备份仅是它们源会话的恢复工件。使用 `wonda wab cookies status [persona]` 检查本地和云端所有权；它永远不会打印 cookie 值。最近的 LinkedIn 帖子有一条直接的云端路径：`wonda linkedin posts <profile> --persona <persona> --engine cloud --via wab`。其他尚未有线连接的读取可以在 Twin 内部运行，使用 `wonda twin run-now <persona> --command "<platform read command>"`；使用 `wonda twin output <twinRunId>` 获取捕获的结果，使用 `run-now` 返回的 id。这两个路径都不会将 Twin cookies 本地下载。

**安全刷新 LinkedIn 的扁平 cookie 文件。** 在 cookie 仅读取批次之前运行 `wonda linkedin auth refresh --account <account> --persona <persona>`。新鲜的磁盘 cookies 是快速的本地无操作。过时或接近过期的 cookies 会导致一次 WAB 启动（当已经运行时是无操作的），一次 WAB 到磁盘同步，以及本地/WAB 端的 LinkedIn 会话检查。刷新路径永远不会调用原始 `wonda linkedin auth check` 探测，也永远不会重试凭证。如果 WAB 会话已死，它将以 `native re-login required` 非零退出；停止批次并手动恢复，使用 `wonda wab login <persona> linkedin`。

`wonda linkedin auth refresh --json` 返回 `{fresh, refreshed, ageSeconds, expiresAt, sessionAlive}`。`fresh` 描述了最终的磁盘状态；`refreshed` 仅在 WAB 到磁盘同步运行时为 true；`ageSeconds` 是磁盘 cookie 的年龄；`expiresAt` 是已知的过期时间或 null；`sessionAlive` 是本地/WAB 端的登录结果。`sessionAlive` 在新鲜本地无操作时为 null，因为不需要 WAB 检查。`--fresh-within` 改变最大接受的磁盘年龄和最小剩余记录的 `li_at` 生命周期（默认为 15 分钟）。将非零退出视为权威，即使有 JSON 输出。

cookie 支持的 LinkedIn 读取接受 `--freshen` 选项，与 `--via cookies` 一起使用。它仅在磁盘 cookies 过时时运行相同的本地预检，然后尝试请求的读取一次。默认保持不变：如果没有 `--freshen`，`--via cookies` 保持快速且无浏览器。

**安全刷新 X 的扁平 cookie 文件。** `wonda x auth refresh --account <account> --persona <persona>` 使用与 X 特定的 freshness 规则相同的本地优先生命周期。由于 `auth_token` 没有本地可读的过期声明，新鲜度仅取决于 cookie 存储的年龄。比 `--fresh-within`（默认为 15 分钟）更新的存储是无浏览器的无操作。过时的存储会启动选定的 WAB（如果需要），将 X cookies 同步到磁盘，并在不调用原始 `x auth check` 探测的情况下检查 WAB 端的会话。死亡的会话会以确切的本地登录命令非零退出。

`wonda x auth refresh --json` 返回 `{fresh, refreshed, ageSeconds, sessionAlive}`。cookie 支持的 X 读取接受 opt-in `--freshen`；它仅在选定的磁盘存储过时时运行相同的刷新，将读取固定到刷新的账户，并且永远不会应用于 WAB 读取、写入或 auth 命令。

使用 `wonda x auth status --account <name>` 获取纯本地视图的 cookie 源、最新捕获来源、生成、所有权、cookie 名称和缺失设备信任 cookie 风险。它永远不会联系 X，也永远不会打印 cookie 值。使用 `wonda x browser-bootstrap --account <name>` 将选定的存储 cookie 箱显式推送到绑定到该账户的正在运行的 WAB personas。

### 动作速率限制

每个平台命令（`linkedin`、`x`、`reddit`、`instagram`），读取和写入，都通过每个配置文件的速率限制保护，以防止突发触发平台的影子封禁 / 反滥用启发式算法。会计是 `(platform, account)` 在滚动 24 小时窗口内，在 `~/.wonda/wab/personas/<persona>/` 下记录每个配置文件（所以云端 Twin 的配额跨运行持久）。

- **读取**操作会进行速率控制，不会发生阻塞：通过抖动间隔来保持每分钟读取量不超过`read_per_min`（默认值为75次/分钟），此速率控制会跨多次调用保持一致。
- **写入**操作会检查每个桶的每日配额。LinkedIn的默认值（其他平台会跟踪并计入每日总量，但默认情况下没有按类型设置写入配额）：

  | 桶名             | 命令                          | 安全值   | 最大值 |
  | ---------------- | ----------------------------- | -------- | ------ |
  | outreach         | `connect` + `send-message` + `inmail` | 20       | 40     |
  | post             | `post`                        | 3        | 5      |
  | comment          | `comment`, `reply-comment`    | 10       | 20     |
  | react            | `like`                        | 25       | 50     |
  | visit            | `visit`                       | 15       | 30     |
  | search           | `search`, `search-posts`      | 25       | 50     |
  | **总计**（所有非读取操作） | 上述任意命令                  | 达到90%时警告 | 100    |

`salesnav search`（Sales Navigator）是例外：它没有商业使用限制，因此会像无限制的读取操作一样进行速率控制，而不是计入`search`配额或每日总量。

配额默认为**软性限制**：如果操作过于保守或超出最大限制，会在stderr输出一个可能被限流的风险警告，然后**继续执行**。通过传递`--hard`（或在配置中设置`mode: hard`）可以使超出配额的写入操作**中止**（退出状态码为1）。

`wonda actions`是一个JSON数据查询（不是仪表盘），用于按需读取个人资料的24小时滚动使用情况与配额；配额/速率控制/警告会在实时钩子中静默运行。

```bash
wonda actions                        # 以JSON格式显示每个个人资料的24小时滚动使用情况与配额
wonda actions --persona <个人资料>        # 查询一个个人资料
wonda actions --platform linkedin    # 筛选到特定平台
wonda linkedin quota                 # 规划视图：在执行大量操作前，显示每个桶的剩余LinkedIn配额（已用 vs 安全值/最大值 + 剩余，包括未使用的桶），而不是在输出中途发出警告
wonda actions sync                   # 将本地操作/健康事件信息同步到您的Wonda账户
wonda actions sync --persona <个人资料>   # 同步一个个人资料的账本
wonda linkedin post "…" --hard       # 对此命令强制执行配额作为硬性限制
```

当配置了API密钥时，本地账本（操作日志、WAB审计/错误日志、cookie来源）会在每次命令执行时自动在后台同步到您的Wonda账户健康记录：尽力而为、批量处理且幂等（每个记录都有一个稳定的客户端事件ID，意味着重试不会重复计数），因此离线使用仍然有效，同步可以在稍后补上。`wonda actions sync`会强制执行完整同步并输出服务器的插入/去重计数；如果没有API密钥，它将是一个静默的无操作命令。只有事件元数据会传输，cookie值或错误包永远不会传输。`WONDA_TELEMETRY_DISABLED=1`会关闭后台同步。

通过`~/.wonda/config.json`下的`action_limits`（配额会被限制在安全下限/上限，因此覆盖可以放宽但不能无声禁用保护）来覆盖/禁用/硬模式：

```json
{
  "action_limits": {
    "mode": "hard",
    "read_per_min": 75,
    "total_per_day": 100,
    "buckets": { "linkedin": { "outreach": { "safe": 15, "max": 30 } } }
  }
}
```

### 配置键

`wonda config get|set|list`键：

- `api-key`：您的wondercat API密钥。
- `base-url`：API基础地址（默认为生产环境，设置为`https://staging.api.wondercat.ai`为测试环境）。
- `default-account`：当平台命令未传递`--account`时使用的账户。
- `wab-backup-enabled`：`true`/`false`表示cookie云端备份（与`wonda wab backup enable`/`disable`相同）。默认开启；只有显式`false`会禁用它。

传输方式**不是**配置键。每个命令根据类型选择传输方式（读取默认为`cookies`，写入/互动默认为`wab`），在所有平台上都保持一致。通过`--via cookies|wab`（如果平台支持）来为每个命令覆盖传输方式。

## 如何思考内容创作

您是一位拥有完整生产工具包的市场总监。在接触任何工具之前，请思考：

1. **产品类别是什么？**（美容、食品、科技、时尚、健身等）
2. **该类别哪种格式表现更好？**（日常产品的UGC表情包、奢侈品的电影感视频、前后对比图、服务行业的客户评价）
3. **钩子是什么？**（ relatable scenario, surprising twist, aspirational lifestyle, social proof）
4. **具体场景是什么？**（不是“产品在桌子上”，而是“人物在有趣情境中发现产品”）

## 决策流程

当被要求创建内容时，请按以下顺序操作：

### 第一步：收集上下文

```bash
wonda brand                                                    # 当前活跃品牌：身份、颜色、字体、标志、产品
wonda brand list                                               # 此账户/组织拥有的所有品牌
wonda brand show <品牌ID>                                    # 具体品牌
wonda brand extract https://stripe.com                         # 本地仅用：写入 ./output/stripe.com/{DESIGN.md, tokens.json, assets/}
wonda brand extract https://stripe.com --save --make-active    # 本地 + 持久化 + 激活（常见路径）
wonda brand extract https://stripe.com --save --name "Stripe"  # 持久化并使用自定义名称
wonda brand extract https://stripe.com --no-output --save      # 不写入磁盘，仅持久化
wonda brand save                                               # 将最新的 ./output/<域名>/ 目录持久化到服务器
wonda brand save --from ./output/stripe.com --make-active
wonda brand pull <品牌ID>                                    # 将已保存的品牌下载回 ./output/<域名>/
wonda brand activate <品牌ID>                                # 设置为活跃品牌
wonda brand upload-logo <品牌ID> https://acme.com/logo.svg   # 通过URL附加标志（`--variant wordmark|icon|dark|light`）
wonda brand upload-font <品牌ID> https://acme.com/Geist.woff2 --weight 700
wonda brand delete <品牌ID>
wonda analytics instagram                                      # 哪些内容表现良好
wonda scrape social --handle @competitor --platform instagram --wait  # 竞争性研究（如果相关）

# 跨平台研究（如果相关）
wonda x search "话题 OR 关键词"                              # 在X/Twitter上查找对话
wonda x user-tweets @competitor                                # 竞争对手的最新推文
wonda reddit search "话题" --sort top --time week             # Reddit讨论
wonda reddit feed marketing --sort hot                         # 子版块趋势
wonda linkedin search "话题" --type COMPANIES                 # LinkedIn公司/人员研究
wonda linkedin profile competitor-vanity-name                  # LinkedIn个人资料情报
```

### 第二步：检查内容技能

内容技能是针对常见内容类型的分步指南。每个技能都会告诉您确切的模型、提示和编辑操作，以及它们的执行顺序。**在从零开始构建之前，请始终检查技能**。

技能是**服务器托管、按账户划分且可编辑**的（与`wonda brand save`相同），您不会下载属于自己的一组`.md`文件。Wonda提供了一套标准的**默认**技能，作为备用只读服务。将它们用于任务；当您想修改时，将其从默认版本fork到自己的副本；Wonda会保留完整的版本历史。`skill list`显示您的有效技能（默认版本与您自己的编辑叠加），并标记任何默认版本已更改的fork。

```bash
wonda skill list                                # 浏览您的有效技能（默认版本 + 您自己的编辑）；标记默认版本已更改的fork
wonda skill get <slug>                          # 将技能的完整分步指南实时拉取到stdout
```

<!-- SKILLS_TABLE_START -->

**默认技能目录**（实时来源：`wonda skill list`，该命令也显示您自己的fork/编辑并标记差异）：

**视频**

| Slug                | 它的作用                                                                                                                                                                                                 |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| product-demo-video  | 高级~15秒多节拍产品演示，开发人员遇到痛点，运行您的工具，屏幕上显示实际效果，然后是品牌CTA，作为一整个HTML合成帧捕获并使用ffmpeg混合 |
| product-video       | 产品/场景视频，可从图像或从头开始生成                                                                                                                                                                       |
| split-screen-demo   | 5秒16:9 LinkedIn循环，源文档到设计幻灯片比较，最后是一个划掉竞争对手的CTA                                                                                                                                   |
| tiktok-ugc-pipeline | 反向工程病毒视频，生成5个变体，自动发布                                                                                                                                                                     |
| ugc-dance-motion    | 从图像和参考中生成舞蹈和动作转移视频                                                                                                                                                                        |
| ugc-hook-brainstorm | 25个等级的滚动停止UGC钩子，热投票，iPhone 16美学，心理杠杆                                                                                                                                                  |
| ugc-reaction-batch  | 批量生产TikTok原生UGC反应视频                                                                                                                                                                               |
| ugc-talking         | UGC访谈广告，单片段，双角度PIP，或20秒以上的长视频                                                                                                                                                          |

**图像**

| Slug                              | 它的作用                                                                                                                                                                                                                                                                                         |
| --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| creative-static-ads               | 高转化率单帧静态广告，6个转化支柱，8种格式原型，8种心理钩子                                                                                                                                                                                                                                      |
| linkedin-media-premium-generation | 使用分层视觉词汇渲染单个停止滚动LinkedIn英雄卡片（1920x1080）：斜体衬线标题、真实产品截图、纸张纹理、浮动社交证明卡片。六个共享相同基因的布局模式。Wonda CLI从X / LinkedIn / Reddit获取真实引言。 |
| premium-static-ads                | 像素级HTML+Playwright静态广告，品牌提取（`wonda brand extract`）。真实字体、精确token、可重复的模板                                                                                                                                                                                               |
| tiktok-slideshow-carousel         | 3-5张幻灯片的TikTok轮播，看起来自然但推广您的产品、钩子、桥梁、揭示                                                                                                                                                                                                                               |

**社交研究**

| Slug                                 | 它的作用                                                                                                              |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------- |
| analyze-reel                         | 分析病毒视频或TikTok，病毒分解 + 5个改编内容创意                                                                                     |
| linkedin-account-multithreading-map  | 覆盖当前账户范围、关系状态和平台建议的介绍路径，针对已接受的人员                                                                                             |
| linkedin-buying-committee-radar      | 监控命名账户的新角色匹配、工作变动、最近发布和Sales Navigator警报                                                                                             |
| linkedin-comment-first-opportunities | 查找几个可以添加特定有用公共贡献的实时LinkedIn对话                                                                                             |
| linkedin-competitor-engager-watch    | 监控命名LinkedIn人员，并将他们新的高信号互动者转化为合格的接触列表                                                                                             |
| linkedin-engager-intel               | 拉取LinkedIn帖子上的每个评论者+反应者，附带个人资料URL，用于热接触                                                                                             |
| linkedin-icp-angle-brief             | 将LinkedIn个人资料转换为可解释的ICP决策和一个有证据支持的接触角度                                                                                             |
| linkedin-icp-qualify                 | 通过当前雇主（行业、员工人数、总部、描述）丰富LinkedIn互动者，以便您可以按ICP匹配进行筛选                                                                                             |
| linkedin-inbound-intent-triage       | 将新的LinkedIn通知、邀请、消息和自有帖子评论转换为有证据支持的响应队列                                                                                             |
| linkedin-social-listening            | 将狭窄的痛点、迁移和购买语言搜索转换为排名靠前、有证据支持的LinkedIn短名单                                                                                             |
| reddit-subreddit-intel               | 抓取顶级帖子，分析病毒模式，生成帖子创意                                                                                             |
| twitter-influencer-search            | 查找微型影响者和放大器，用于产品发布                                                                                             |

**策略**

| Slug                 | 它的功能                                                                                                                                                                                                                                                         |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| linkedin-post-system | 将原始想法转化为符合经过验证的格式和用户精确口吻的领英帖子。通过wonda领英个人资料/帖子引导用户的语音语料库，将想法映射到28种经过验证的内容格式之一，草拟2个带有反AI污染防护的变体。 |
| marketing-brain      | 钩子、视觉效果、广告和竞争分析的策略大脑                                                                                                                                                                                                                         |

**工具**

| Slug                   | 它的功能                                                                                                                                                                                               |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| extract-apply-style    | 从任何图像中提取视觉风格，然后在该风格中生成新主题                                                                                                                            |
| ffmpeg                 | 本地确定性媒体转换、剪辑、替换音频、烧录字幕、社交格式化、场景分割、静音剪辑、帧提取、分析伪影                                                                                                            |
| image-edit             | 编辑现有图像、img2img、背景移除、裁剪、文本叠加、矢量化                                                                                                                           |
| slide-generation       | 从任何内容来源、代码库、Notion笔记或Google Docs生成带品牌的幻灯片演示文稿                                                                                                               |
| software-ui-mockups    | 渲染真实的软件UI、终端/CLI TUI、Chrome浏览器窗口、macOS桌面，在HTML中精确到像素，用于演示视频、幻灯片、截图和文档，从程序的实时真实来源获取                                                                 |
| tiktok-caption-presets | 通过wonda edit --preset应用的TikTok风格文本叠加和动画字幕预设                                                                                                                      |

<!-- SKILLS_TABLE_END -->

**编辑技能（可选）。** 当默认选项不太合适时，与其绕过它不如直接编辑它。编辑默认选项会自动将其复制到您的账户中：

```bash
wonda skill create my-ugc --from ugc-talking    # 将默认选项复制到您自己的可编辑副本中
wonda skill edit my-ugc --editor                # 记录新版本（打开$EDITOR；或--file <md> / 标准输入）
wonda skill diff <slug>                          # 查看自您复制以来默认选项发生了哪些变化（漂移）
wonda skill refactor <slug> --editor             # 将您的分支重新基于更新的默认选项，清除漂移提示
```

**如果技能匹配** → `wonda skill get <slug>`，读取它，根据上下文进行调整，执行每个步骤。

**如果不匹配任何技能** → 从头开始构建（步骤3）。

### 步骤2.5：决定是否应本地完成

并非所有媒体任务都应该通过Wonda编辑。使用此路由规则：

- 使用 `wonda` 进行AI生成、AI转录/对齐、抓取、发布、托管转换和需要媒体ID或远程作业的工作流。
- 使用本地 `ffmpeg` 对您已有的或可以下载的文件进行确定性转换：剪辑、裁剪/缩放/填充、连接（合并多个片段）、替换音频、提取音频/帧、反转、为交付标准化、烧录字幕、分割场景、剪辑静音，并构建分析伪影。**始终在本地合并片段** — 服务器端合并可能在任何输入超过~7MB后挂起30多分钟。

当任务从Wonda媒体ID开始但实际编辑是确定性时，首先将其移动到本地文件：

```bash
wonda media download <mediaId> -o ./input.mp4
```

在执行任何本地ffmpeg工作之前：

```bash
which ffmpeg
which ffprobe
ffmpeg -version
ffprobe -v error -show_format -show_streams -of json ./input.mp4
```

本地字幕/文本工作的字体规则：

- 优先使用显式的字体文件路径而不是字体名称。
- 假设字体存在。首先使用 `fc-match`、`fc-list`、`/System/Library/Fonts`、`/Library/Fonts`、`~/Library/Fonts` 或 `/usr/share/fonts` 检查。
- 如果任务主要是本地完成/字幕/格式化/分割/伪影提取，请在使用命令之前检查 `ffmpeg` 技能。
- `wonda edit video` 运行 **本地 ffmpeg** 对每个编辑操作：`trim`、`crop`、`volume`、`speed`、`reverseVideo`、`extractFrame`、`extractAudio`、`editAudio`、`imageCrop`、`imageToVideo`、`merge`、`overlay`、`splitScreen`、`splitScenes`、`skipSilence`。渲染在您的计算机上通过ffmpeg运行：没有服务器端 `editor_job`，渲染本身不占用积分（输入被下载，结果被上传）。`textOverlay` 和 `animatedCaptions` 也通过捆绑的hyperframes（Chromium）渲染器在本地运行。ffmpeg必须在PATH上（`wonda doctor` 验证）。公共API `/video/edit`、`/image/edit`、`/audio/edit` 现在不再用于这些操作，并返回 410 Gone。
- **始终在本地合并片段。** 服务器端合并可能在任何输入超过~7MB后挂起30多分钟，并且 `wonda edit video --operation merge` 现在默认在本地ffmpeg中运行，原因相同。
- **切勿混合每片段音频然后连接。** 首先连接视频轨道，然后在连接的时间线上叠加一次完整的旁白或音乐轨道。每片段音频烘焙会创建剪辑线冲突和静音间隙。

除非用户要求否则默认的本地导出目标：

```bash
-c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -movflags +faststart -c:a aac -b:a 192k
```

始终将 `-y` 作为第一个标志，以便命令自动覆盖输出。当输出路径存在时，`ffmpeg` 会交互式提示，而代理外壳在提示上挂起，直到超时。

### 步骤2.6：选择正确的本地工具

编辑映射到四个工具之一。选择与第一个匹配的行。

| 需要                                                         | 工具                                                                   | 原因                                                                                              |
| ------------------------------------------------------------ | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| 基本转换（剪辑、裁剪、速度、合并、叠加、...）                | `wonda edit video --operation <op>`                                    | 封装本地ffmpeg。免费、确定性、在您的计算机上渲染（无服务器渲染，无积分）。                               |
| 动态图形、动画文本、角标、片头/片尾                          | `wonda compose <kind>` (hyperframes HTML组合，本地渲染)                   | 一次性操作，无Lambda，无Node捆绑到wonda中。需要Node >= 22 + ffmpeg。                                   |
| 动态字幕、品牌效果管道、场景特效                              | `wonda transitions run --preset <name>` (miruna的过渡服务)              | 托管；更丰富的效果库（SAM3遮罩、场景过渡、字幕预设）。                                                    |
| 一次性原始转换，未涵盖在基本转换中                           | 通过Bash的原始 `ffmpeg`（见 `ffmpeg` 技能）                         | 比选择错误的原始转换更快；匹配“在本地文件上执行确定性转换”。                                               |
| 复杂的多步骤管道                                          | 链接上述 (`wonda edit ...` → 原始ffmpeg → `wonda compose ...`)          | 每个步骤写入一个本地mp4；将其作为 `--input` / `--media` 传递给下一个步骤。                               |

在新机器上运行一次 `wonda doctor` 以确认ffmpeg、node和hyperframes都可用。传递 `--warm-chrome` 以预取hyperframes捆绑的Chromium（~150 MB），以便第一个剪辑渲染不会暂停下载它。传递 `--wab` 以审计磁盘上的WAB浏览器运行时（安装的驱动程序与此构建的固定版本、驱动程序树清单）；离线、只读和顾问，如 `--relay`。

**示例：**

基本剪辑和合并（wonda edit，本地ffmpeg）：

```bash
wonda edit video --operation trim --media $VID \
  --params '{"trimStartMs":3000,"trimEndMs":10000}' \
  --wait -o ./trimmed.mp4

wonda edit video --operation merge --media $A,$B,$C \
  --wait -o ./merged.mp4
```

动态图形片头（wonda compose，hyperframes）：

```bash
wonda compose motion --template fade-in \
  --text "Q4 Recap" --subtitle "Wondercat" \
  --duration 4 --resolution portrait -o intro.mp4

wonda compose text --input ./clip.mp4 --text "NEW DROP" \
  --position bottom-center -o overlay.mp4
```

在完成的片段上应用动态字幕（过渡服务）：

```bash
wonda transitions run --media $VID --preset caption_word_pop --wait -o final.mp4
```

原始ffmpeg用于未涵盖的操作（例如带音频淡出的连接）：

```bash
ffmpeg -y -f concat -safe 0 -i list.txt \
  -af "afade=out:st=29:d=1" \
  -c:v libx264 -crf 18 -pix_fmt yuv420p \
  -c:a aac -b:a 192k out.mp4
```

多步骤管道（compose片头 → wonda合并与主视频 → 过渡字幕）：

```bash
wonda compose motion --template scale-pop --text "Hello" --duration 3 -o intro.mp4
wonda edit video --operation merge --media $(wonda media upload intro.mp4 --quiet),$MAIN_VID \
  --wait -o merged.mp4
MERGED_ID=$(wonda media upload merged.mp4 --quiet)
wonda transitions run --media $MERGED_ID --preset caption_word_pop --wait -o final.mp4
```

### 步骤3：从头开始构建（链接端点）

当没有技能匹配时，链接单个CLI命令。每一步都生成一个输出，作为下一步的输入。

**单个资产：**

```bash
wonda generate image --model gpt-image-2 --prompt "..." --aspect-ratio 9:16 --wait -o out.png
# --params '{"quality":"high"}' — 自动/低/中/高（默认自动）
# --negative-prompt "..."       — 覆盖要排除的内容（模型相关）
# --seed <number>               — 固定种子以获得可重复结果（模型相关）
wonda generate video --model seedance-2 --prompt "..." --duration 5 --params '{"quality":"high"}' --wait -o out.mp4
wonda generate text --model <model> --prompt "..." --wait
wonda generate music --model suno-music --prompt "upbeat lo-fi" --wait -o music.mp3
```

**音频（语音、转录、对话）：**

```bash
# 列出可用声音（TTS + 对话使用相同的声音集）
wonda audio voices

# 文本到语音
wonda audio speech --model elevenlabs-tts --prompt "您的脚本在这里" \
  --params '{"voiceId":"hpp4J3VqNfWAUOO0d1Us"}' --wait -o speech.mp3
# elevenlabs-tts始终需要一个voiceId — 从 `wonda audio voices` 中选择一个

# 转录音频/视频为文本
wonda audio transcribe --model elevenlabs-stt --attach $MEDIA --wait

# 多说话者对话（每个说话者需要一个来自 `wonda audio voices` 的voiceId）
wonda audio dialogue --model elevenlabs-dialogue \
  --prompt 'ALICE: Hi! BOB: Hello!' \
  --params '{"speakers":[{"label":"ALICE","voiceId":"hpp4J3VqNfWAUOO0d1Us"},{"label":"BOB","voiceId":"IKne3meq5aSn9XLyUdCD"}]}' \
  --wait -o dialogue.mp3
```

**音频AI操作（直接推理，非编辑操作）：**

```bash
# 噪声消除/去混响语音
wonda audio enhance --model replicate-resemble-enhance --attach $MEDIA \
  --params '{"denoise":true,"chunkSeconds":10}' --wait -o enhanced.wav

# 将轨道拆分为人声和器乐音轨
wonda audio extract-voice --model replicate-demucs --attach $MEDIA \
  --wait -o vocals.wav
```

**向视频添加动画字幕：**

`animatedCaptions` 操作在一个步骤中处理所有内容 — 它提取音频、为逐字时间转录，并将逐字动画字幕渲染到视频上。

```bash
# 生成带有语音音频的视频
VID_JOB=$(wonda generate video --model seedance-2 --prompt "..." --duration 5 --aspect-ratio 9:16 --params '{"quality":"high"}' --wait --quiet)
VID_MEDIA=$(wonda jobs get inference $VID_JOB --jq '.outputs[0].media.mediaId')

# 添加动画字幕（单步操作）
wonda edit video --operation animatedCaptions --media $VID_MEDIA \
  --params '{"fontFamily":"TikTok Sans SemiCondensed","position":"bottom-center","sizePercent":80,"strokeWidth":2.5,"fontSizeScale":0.8,"highlightColor":"rgb(252, 61, 61)"}' \
  --wait -o final.mp4
```

视频的原始音频被保留。**切勿用TTS替换音频** — Sora已经生成了语音。

**过渡（单个视频上的效果管道）：**

```bash
wonda transitions presets                            # 列出内置预设（JSON）
wonda transitions operations                         # 按类别分组（分析/效果/...）
wonda transitions operations --json                  # 完整的每参数元数据
wonda transitions llms                               # 完整参考（预设+操作+依赖）
wonda transitions run --media $VID --preset flash_glow --wait -o out.mp4
# 或者发送代理生成的片段时间线（内联JSON）：
wonda transitions run --media $VID \
  --clips '[{"layer_type":"video","start_frame":0,"end_frame":60}]' --wait -o out.mp4
# 或者从文件（长代理时间线很方便）：
wonda transitions run --media $VID --clips ./timeline.json --wait -o out.mp4
# 要附加场景过渡：传递一个包络（片段+场景过渡）
# 而不是裸片段数组 — 相同文件，两个字段转发。
wonda transitions run --media $VID --clips ./timeline_with_transitions.json --wait -o out.mp4
# 其中 timeline_with_transitions.json 是：
#   { "clips": [...],
#     "scene_transitions": [{"name":"crossfade","params":{"duration":8},"boundaries":[60]}] }
wonda transitions job <jobId>                        # 汇报过渡作业
```

使用 `--preset` 或 `--clips` 中的一个。需要完整的（登录）账户。**在组合片段时间线时，始终先阅读 `wonda transitions llms`。** 它记录了检测/分割/效果依赖，哪些操作需要遮罩，以及完整的片段规格形状（层类型、轨道、效果、转换）。

**预设变量（`variables` 块）。** 每个预设在其 `wonda transitions presets` 中的 `variables` 下声明它接受的模板变量。每个条目都有 `name`、`description` 和 `required`。必需变量必须提供，否则作业会以400错误拒绝 — 没有更多沉默跳过。使用 `--var name=value`（可重复）传递，或者对于常见的 `prompt` 情况，使用 `--prompt` 快捷方式：

```bash
# flash_glow_prompted 需要 { prompt }
wonda transitions run --media $VID --preset flash_glow_prompted \
  --prompt "woman in white dress" --wait -o out.mp4

# text_behind_person 需要 { prompt, text }
wonda transitions run --media $VID --preset text_behind_person \
  --var prompt="the person" --var text="HELLO WORLD" --wait -o out.mp4

# 数值类型变量：纯数字被解码为数字，"true"/"false" 作为布尔值，所有其他内容保持为字符串。比较帧索引数值的预设（border_frame、marquee_text、quick_motion_text、bg_remove_scale）
# 需要这个 — 引用整数会将其转换回字符串。
wonda transitions run --media $VID --preset border_frame \
  --var exit_start_frame=200 --var exit_end_frame=251 --wait -o out.mp4
```

`prompt`变量是一个**检测文本查询**，用于描述需要遮罩的主题，将其输入SAM3以生成逐帧分割掩码。这不是一个内容生成提示。

构建需要检测掩码的自定义`--clips`时间线？添加一个`layer_type: "video"`的片段，并添加`mask: {layer_type: "mask", analysis_steps: [{name: segment, params: {prompt: "..."}}]}`。SAM3从提示中一次性处理检测和分割，因此不需要单独的`detect`步骤。

### 渲染前预加热掩码（推荐）

对于包含`mask:<label>`变量的预设，首先运行`wonda transitions ensure-masks`，以便渲染开始时掩码已经准备就绪。对于(媒体, 标签)对的第一次调用需要1-3分钟；后续调用几乎是即时的。

```bash
# 1. 确保掩码已准备好，并阻塞直到就绪。
wonda transitions ensure-masks --media $VID --labels person,phone --wait

# 2. 运行渲染。掩码已准备好。
wonda transitions run --media $VID --preset slide_reflect_background \
  --var "masks=mask:person+phone" --wait -o out.mp4
```

`ensure-masks`标志：

- `--media MEDIA_ID` — 必须的，掩码对应的视频
- `--label NAME` — 可重复的，每次调用一个标签 (`--label person --label phone`)
- `--labels NAME,NAME` — 逗号分隔的替代方式 (`--labels person,phone`)
- `--wait` — 阻塞直到每个标签都准备好
- `--timeout DUR` — 当设置`--wait`时限制等待时间（默认10m）

多提示语法：`--var`中的`mask:woman+phone`会被拆分为单独的掩码(`woman`, `phone`)，并在每帧中进行并集。将每个子标签分别传递给`ensure-masks`，以便所有掩码都预热。

何时跳过`ensure-masks`：

- 非掩码预设（没有`mask:<label>`变量） — 无需准备
- 之前的渲染已使用这些（媒体, 标签） — 已准备就绪

何时`ensure-masks`最为重要：

- 新媒体基于掩码预设的第一次渲染
- 在渲染中迭代参数 — 预热一次，然后可以多次运行而无需重新准备

**多场景预设（`requiresMultiScene: true`）。** 某些预设使用场景感知逻辑，并期望视频具有多个剪辑/场景。检查`wonda transitions presets`中的`requiresMultiScene`。如果为true，输入单个连续镜头将只生成一个场景，效果可能不尽如人意。先组合片段，或使用具有自然剪辑的视频。

**调整预设参数。** 每个预设都是基于片段的。使用`wonda transitions preset <name> --json`获取单个预设，读取其`clips:`（单轨道）或`tracks:`（多轨道）字段，编辑任何片段参数，然后作为`--clips`提交。对于多轨道预设，通过为每个片段分配来自其来源轨道的`track`索引进行展平。如果预设声明`sceneTransitions:`，则在请求中传递该数组而不变。

```bash
# 单轨道预设（例如flash_glow_montage）：直接复制clips:
wonda transitions preset flash_glow_montage --json | jq '.preset.clips' > clips.json
# 编辑clips.json
wonda transitions run --media $VID --clips "$(cat clips.json)" --wait -o out.mp4
```

**自动修复安全网（`--auto-repair`, `--face-bbox`）。** 对于`--clips`渲染，工作进程会在渲染前对提交的JSON运行确定性修复步骤，默认开启。修复包括：宽度适配字体、底部对齐、堆叠间距对齐（`ROW1_py`来自帽高公式）、关键帧边界对齐到`[0, source_duration]`、同一行字幕重叠修剪、掩码全时长扩展、描边宽度归零、每字体目标间距对齐、掩码切割时长扩展、负起始对齐，以及（使用`--face-bbox`时）面部重叠字幕偏移。传递`--auto-repair=false`进行严格验证；超出规格的值将作为渲染错误显示。

```bash
# 将身体字幕移开说话者的脸。bbox是画布像素中的x1,y1,x2,y2（左上角原点）。
wonda transitions run --media $VID --clips ./timeline.json \
  --face-bbox 200,160,520,520 --wait -o out.mp4

# 严格模式 — 禁用自动修复以查看哪些片段未通过验证。
wonda transitions run --media $VID --clips ./timeline.json \
  --auto-repair=false --wait -o out.mp4
```

`--face-bbox`仅偏移身体字幕。您希望放在说话者后面的装饰性文本仍然通过显式的`mask_cutout {prompt: "person"}`片段路由。

**输出URL路径因作业类型而异：**

- 推理作业（生成、音频）：`.outputs[0].media.url`和`.outputs[0].media.mediaId`
- 编辑作业（编辑）：`.outputs[0].url`和`.outputs[0].mediaId`

## 模型瀑布

### 图像

默认：`gpt-image-2`。OpenAI的旗舰产品 — 最强的提示遵循性、最佳文本图像、通过参考图像进行高保真度编辑。处理1-4个参考图像。质量等级：`auto`（默认）、`low`、`medium`、`high` — 通过`--params '{"quality":"high"}'`传递。输出上限为1536px。

对于特定的img2img编辑（更改、添加/删除、重绘、背景移除、裁剪、文本覆盖、矢量化），使用`wonda skill get image-edit` — 它具有完整的编辑特定决策树。

仅在以下情况下选择其他模型：

- 用户明确请求其他模型
- **超过4个参考图像** → `nano-banana-2`（gpt-image-2在4个参考图像上限；nano-banana-2最多接受14个参考图像）。对于1-4个参考图像，保持`gpt-image-2`。
- 需要矢量输出 → `runware-vectorize`
- 需要背景移除 → `birefnet-bg-removal`
- 最便宜的可能/最快的草稿 → `z-image`
- 需要>1536px / 真正的4K输出 → `nano-banana-pro`（1K/2K/4K）或`nano-banana-2`（1K/2K/4K）。gpt-image-2上限为1536px。
- gpt-image-2不可用 / OpenAI故障 → `nano-banana-2`或`seedream-4-5`或`grok-imagine-pro`

### 视频

默认：`seedance-2`（持续时间5/10/15秒，默认5秒，质量：高）。升级：

- 质量投诉或不同风格 → `sora2`或`sora2pro`
- 单个片段的最大持续时间是**15秒**（Seedance 2）、**20秒**（Sora）→ 对于更长时间的内容，通过合并多个片段
- Veo（`veo3_1`，`veo3_1-fast`）可用，但**不在默认瀑布中**。仅在用户明确要求Veo时选择Veo。
- Gemini Omni（`gemini-omni-video`）可用，但**不在默认瀑布中**。仅在用户要求Gemini或特定需要多图像参考T2V/I2V（最多7个参考图像）或4K输出时选择。

**图像到视频路由（附加参考图像时强制执行）：**

- 参考图像中可见人/脸 → 必须使用`kling_3_pro`（更好地保留面部身份）
- 参考图像中无人 → 使用`seedance-2`
- **文本到视频（无参考图像）：** Seedance 2可以很好地生成人物。此规则仅适用于您`--attach`了图像时。

**Kling模型系列：**

- `kling_3_pro` — 文本到视频和图像到视频，支持起始/结束图像、自定义元素（@Element1，@Element2），3-15秒持续时间，16:9/9:16/1:1
- `kling_2_6_pro` — 通用型，5-10秒，16:9/9:16/1:1，文本到视频和图像到视频
- `kling_2_6_motion_control` — 运动传递：需要参考图像和参考视频，用图像外观重现视频运动
- `kling2_5-pro` — Kling的预算选项，5-10秒，支持首帧/尾帧图像

**Kling提示规则（重要）：** Kling的提示字段限制在**2,500个字符**，Kling对Sora风格的结构化简报（`SCENE:` / `SUBJECT:` / `MOTION:` / `BANNED LOOK:`部分标题）反应不佳。在该格式下，Kling会抓住氛围名词并默默忽略中心主题（经实证：相同的2,842字符Sora风格提示在Sora 2 Pro和Seedance 2上渲染正确，但在Kling上产生没有手机的渲染 — 即使修剪到2,250字符）。当从Seedance升级到Kling，或直接针对Kling时，**将提示重写为简短的自然语言散文（~1,000–1,500字符）**，并**在开头以英雄主题**而不是将主题埋在`SUBJECT:`块中。**不要将Sora格式化的提示原封不动地传递给Kling。**

**其他视频模型：**

- `grok-imagine-video` — xAI视频生成，5-15秒，支持7种宽高比，包括4:3和3:2
- `gemini-omni-video`: Google Gemini Omni。文本到视频和图像到视频，最多7个参考图像（槽位`reference_image_1`到`reference_image_7`）。持续时间4/6/8/10秒，宽高比9:16和16:9，分辨率720p / 1080p / 4K。定价：$0.15基础 + $0.075/s（720p/1080p），$0.75基础 + $0.075/s（4K）。无原生音频（如果需要语音，请与单独的音频模型配对）。
- `topaz-video-upscale` — 提升视频分辨率（1-4倍因子，支持fps转换）
- `sync-lipsync-v2-pro` — 遗留的唇同步，用于用户提供的视频+音频对。不如原生音频生成，几乎不适用于新内容。请参阅“唇同步”部分了解规则。

Seedance系列（默认视频模型，自动移除水印）：

- `seedance-2` — 基础Seedance 2.0（T2V/I2V，5-15秒，高=标准/基本=快速）
- `seedance-2-omni` — 多参考生成（图像、音频参考）
- `seedance-2-video-edit` — 通过文本提示编辑现有视频

**视频持续时间：** 不同模型的接受`--duration`值不同。使用`wonda capabilities`或`wonda models info <slug>`查询。

### 音频

- 音乐：`suno-music`（设置`--params '{"instrumental":true}'`以无人声）
- 文本到语音：`elevenlabs-tts` — 仅用于在无声片段上请求旁白/配音。**不要**用于“让UGC角色说话” — Sora / Sora 2 Pro / Veo 3.1 / Kling 3 / Seedance 2在任何语言中生成原生同步语音，看起来和听起来都远好。始终在参数中设置`voiceId`。默认女性声音：`--params '{"voiceId":"21m00Tcm4TlvDq8ikWAM"}'`（Rachel）。
- 转录：`elevenlabs-stt`
- 多说话者对话：`elevenlabs-dialogue`
- 增强音频（清理嘈杂语音）：`replicate-resemble-enhance`通过`wonda audio enhance` — 去噪+去混响。当语音录音听起来模糊、回声或背景噪音时使用。**不是**一个通用的“听起来更好”按钮；如果源已经干净，这可能会使其变软。
- 提取人声（隔离人声/分离音轨）：`replicate-demucs`通过`wonda audio extract-voice` — 分离为语音和器乐轨道。用于将说话者或歌手从轨道中提取出来，或隔离人声背后的音乐。

**原生同步语音（优先于TTS+唇同步）：** Sora、Sora 2 Pro、Veo 3.1、Kling 3和Seedance 2直接在视频中生成对话，并内置口型动作。将行（和语言）放在视频模型的`--prompt`中。**永远不要**将`elevenlabs-tts` → `sync-lipsync-v2-pro`链用于在无声生成上模拟语音。

## 角色

角色是可重复使用的保存组合（图像+可选的语音音频），您可以在提示中用`@name`提及它们。服务器自动将图像、可选的面部视频和音频注入到所选模型的正确槽位。适用于Kling 3 Pro（`start_image` + `element_1` + `voice_audio`）和Seedance 2 Omni（`ref_image_1` + `ref_video_1` + `ref_audio_1`）。命名规则：必须以字母开头，1-31个字符，字母数字+`_`/`-`。

**提供者陷阱（Seedance 2 Omni）：** 当提及角色时，API会自动将Seedance路由到MuAPI。Replicate强制执行15秒`ref_audio_1`限制，并拒绝标记为敏感的著名名人参考（`E005 — 上传图像中检测到人脸。请使用没有真实人物的图像。`）。MuAPI是角色驱动作业的可靠路径。即使在MuAPI上，顶级名人参考（想想Sydney Sweeney、Leonardo DiCaprio）也会被阻止。如果您在真实人物参考上看到该错误，请使用Kling 3 Pro（其角色管道在服务器端运行语音克隆，因此原始面部音频永远不会接触到审核分类器）。

**从Kling片段** — 从您喜欢的生成中提取帧+语音：

```bash
VID=$(wonda generate video --model kling_3_pro --prompt "年轻男性，灰色T恤，对着镜头说话" --wait --quiet)
VID_MEDIA=$(wonda jobs get inference $VID --jq '.outputs[0].media.mediaId')
wonda character from-media alex --source $VID_MEDIA --frame-ms 2500
wonda generate video --model kling_3_pro --prompt "@alex欢迎观众加入频道" --wait -o alex-welcome.mp4
```

**从零开始** — 生成肖像和TTS样本，然后绑定它们：

```bash
IMG=$(wonda generate image --model nano-banana-2 --prompt "年轻女性，工作室肖像" --wait --quiet)
IMG_MEDIA=$(wonda jobs get inference $IMG --jq '.outputs[0].media.mediaId')
AUD=$(wonda audio speech --model elevenlabs-tts --prompt "嗨，我是我" --params '{"voiceId":"21m00Tcm4TlvDq8ikWAM"}' --wait --quiet)
AUD_MEDIA=$(wonda jobs get inference $AUD --jq '.outputs[0].media.mediaId')
wonda character create maya --image $IMG_MEDIA --audio $AUD_MEDIA
```

列出/检查/更新/删除：`wonda character list`，`wonda character get <name>`，`wonda character update <name> --audio $NEW`，`wonda character delete <name>`。每次生成只能引用一个带音频的角色。

## 提示编写规则

从上到下遵循此瀑布。使用第一个匹配的规则并停止。

1. **PASSTHROUGH** — 如果用户说“使用我的确切提示” / “逐字” / “无增强” → 精确复制他们的文字。零修改。

2. **图像到视频** — 当源图像输入到视频模型时，仅描述运动。模型可以看到图像。**不要**描述图像内容。
   - 好：`"轻柔呼吸运动，摄像机缓慢推进，氛围灯光变化"`
   - 坏：`"两只猫在薰衣草背景上轻柔呼吸"`（描述图像）

3. **空提示（从零开始）** — 使用用户的请求作为提示。**不要**添加风格描述符、灯光、构图或情绪。
   - 用户说“创建一个戴着太阳镜的猫的图像” → 提示：`"创建一个戴着太阳镜的猫的图像"`
   - **不要**增强为：`"一只活泼的橘色虎斑猫戴着超大反光太阳镜，工作室灯光，浅景深"`

4. **非空提示（调整模板）** — 保持结构和风格，仅替换内容以匹配用户的请求。保持提示字面和约束密集。

## 宽高比规则

三种情况，无例外：

1. 用户指定宽高比 → 使用它：`--aspect-ratio 16:9`
2. 用户未提及宽高比 → 明确设置为`--aspect-ratio 9:16`用于社交内容（UGC、TikTok、Reels、Stories）。肖像是对任何社交/营销视频的默认值。
3. 编辑现有媒体 → 使用`--aspect-ratio auto`以保留源尺寸

**UGC和社交内容**始终是**肖像（9:16）**。如果有人要求TikTok、Reel、Story或UGC视频，始终使用`--aspect-ratio 9:16`。横向是仅用于YouTube、演示文稿或明确请求时。

**方形（1:1）**由所有Kling模型和某些图像模型支持 — 用于请求的Instagram动态页面。

## 常见链接模式

这些模式展示了如何通过链接CLI命令来组合多步骤管道。每一步的输出都输入到下一步。

> **无需在步骤之间下载和重新上传。** 每次生成和编辑
> 产生一个媒体ID在其输出中。通过`--media`或`--audio-media`直接将此ID传递给下一个命令
>。使用`--jq '.outputs[0].media.mediaId'`用于推理作业和`--jq '.outputs[0].mediaId'`用于编辑作业。
> 仅在最终步骤上使用`-o <file>`以下载最终输出。

### 将图像动画化为视频

```bash
MEDIA=$(wonda media upload ./product.jpg --quiet)
# 图像中无人 → Seedance 2
wonda generate video --model seedance-2 --prompt "摄像机缓慢推进，产品旋转" \
  --attach $MEDIA --duration 5 --params '{"quality":"high"}' --wait -o animated.mp4
# 图像中有人 → Kling（仅当附加的参考图像中有人的情况下）
wonda generate video --model kling_3_pro --prompt "这个人转身微笑" \
  --attach $MEDIA --duration 5 --wait -o person.mp4
```

### 替换视频中的音频（TTS旁白或音乐）

```bash
# 生成TTS
TTS_JOB=$(wonda audio speech --model elevenlabs-tts --prompt "The script" \
  --params '{"voiceId":"21m00Tcm4TlvDq8ikWAM"}' --wait --quiet)
TTS_MEDIA=$(wonda jobs get inference $TTS_JOB --jq '.outputs[0].media.mediaId')
# 混合到视频上（静音原音频，全旁白）
wonda edit video --operation editAudio --media $VID_MEDIA --audio-media $TTS_MEDIA \
  --params '{"videoVolume":0,"audioVolume":100}' --wait -o with-voice.mp4
```

仅在需要替换视频音频时使用。Sora、Sora 2 Pro、Veo 3.1、Kling 3 和 Seedance 2 都能生成任何语言的本地同步语音，不要用TTS替换它们，除非用户明确要求不同的旁白。不要用这个步骤为UGC/口播片段“添加语音”，而是将对话放在视频模型的提示中。

### 添加静态文本叠加

静态叠加（梗图文字、"chat did i cook"等）使用比字幕更小的字体大小。它们是氛围化的，不是用来主导画面的。

```bash
wonda edit video --operation textOverlay --media $VID_MEDIA \
  --prompt-text "chat, did i cook" \
  --params '{"fontFamily":"TikTok Sans SemiCondensed","position":"top-center","sizePercent":66,"fontSizeScale":0.5,"strokeWidth":4.5,"paddingTop":10}' \
  --wait -o with-text.mp4
```

**推荐的textOverlay + animatedCaptions预设。** `wonda edit {video,image,audio}` 接受 `--preset <name>`（限定在 `--operation` 范围内）。`--params` 字段在关键冲突时覆盖预设值。

`textOverlay`（静态，居中顶部）：

- `TikTok White Highlight` — 黑色文字在略微圆角的白色框内。
- `TikTok Black Highlight` — 白色文字在略微圆角的黑色框内。
- `TikTok Red Highlight` — 白色文字在略微圆角的红色（`#E14135`）框内。

`animatedCaptions`（STT驱动，居中底部）：

- `TikTok White Captions` — 黑色文字，白色高亮在当前单词上。
- `TikTok Black Captions` — 白色文字，黑色高亮在当前单词上。
- `TikTok Red Captions` — 白色文字，红色（`#E14135`）高亮在当前单词上。

```bash
wonda edit video --operation textOverlay \
  --preset "TikTok Red Highlight" --media <id> \
  --params '{"text":"YOUR HEADLINE"}' --wait -o ./out.mp4
```

`textOverlay` 通过捆绑的hyperframes（Chromium）渲染器本地渲染。现在没有服务器端的 `textOverlay` 了。

**字体大小指南：**

- 静态叠加：`sizePercent: 66`, `fontSizeScale: 0.5`, `strokeWidth: 4.5`
- 动画字幕：`sizePercent: 80`, `fontSizeScale: 0.8`, `strokeWidth: 2.5`, `highlightColor: rgb(252, 61, 61)`
- 字体：`TikTok Sans SemiCondensed`，两者都使用

### 添加逐字动画字幕（带时间同步）

`animatedCaptions` 操作提取音频、转录并渲染逐字动画字幕——全部一步完成。

```bash
wonda edit video --operation animatedCaptions --media $VIDEO_MEDIA \
  --params '{"fontFamily":"TikTok Sans SemiCondensed","position":"bottom-center","sizePercent":80,"strokeWidth":2.5,"fontSizeScale":0.8,"highlightColor":"rgb(252, 61, 61)"}' \
  --wait -o with-captions.mp4
```

对于快速静态字幕（无时间，只需屏幕上显示文字），使用 `textOverlay` 和 `--prompt-text`：

```bash
wonda edit video --operation textOverlay --media $VIDEO_MEDIA \
  --prompt-text "Summer Sale - 50% Off" \
  --params '{"fontFamily":"TikTok Sans SemiCondensed","position":"bottom-center","sizePercent":80}' \
  --wait -o captioned.mp4
```

### 添加背景音乐

```bash
MUSIC_JOB=$(wonda generate music --model suno-music \
  --prompt "upbeat lo-fi hip hop, warm vinyl crackle" --wait --quiet)
MUSIC_MEDIA=$(wonda jobs get inference $MUSIC_JOB --jq '.outputs[0].media.mediaId')
wonda edit video --operation editAudio --media $VID_MEDIA --audio-media $MUSIC_MEDIA \
  --params '{"videoVolume":100,"audioVolume":30}' --wait -o with-music.mp4
```

### 编辑器输出链式操作

当链式多个编辑器操作（例如 editAudio → animatedCaptions → textOverlay）时，从每个编辑器作业输出中提取媒体ID，并将其传递到下一步。注意jq路径与推理作业不同：

```bash
# 推理作业：.outputs[0].media.mediaId
# 编辑器作业：.outputs[0].mediaId

EDIT_JOB=$(wonda edit video --operation editAudio --media $VID --audio-media $AUDIO \
  --params '{"videoVolume":0,"audioVolume":100}' --wait --quiet)
STEP1_MEDIA=$(wonda jobs get editor $EDIT_JOB --jq '.outputs[0].mediaId')

CAP_JOB=$(wonda edit video --operation animatedCaptions --media $STEP1_MEDIA \
  --params '{"fontFamily":"TikTok Sans SemiCondensed","position":"bottom-center","sizePercent":80,"strokeWidth":2.5,"fontSizeScale":0.8,"highlightColor":"rgb(252, 61, 61)"}' --wait --quiet)
STEP2_MEDIA=$(wonda jobs get editor $CAP_JOB --jq '.outputs[0].mediaId')

wonda edit video --operation textOverlay --media $STEP2_MEDIA \
  --prompt-text "Hook text" --params '{"position":"top-center","fontFamily":"TikTok Sans SemiCondensed","sizePercent":66,"fontSizeScale":0.5,"strokeWidth":4.5}' --wait -o final.mp4
```

### 合并多个片段

**始终使用ffmpeg本地合并。** 服务器端合并（`wonda edit video --operation merge`）一旦任何输入超过~7MB，可能会卡住30多分钟。

下载每个Wonda媒体ID，然后拼接。流复制快，但需要匹配的编解码器/配置/分辨率；如果出错，则回退重新编码：

```bash
wonda media download $CLIP1 -o /tmp/clip-1.mp4
wonda media download $CLIP2 -o /tmp/clip-2.mp4
wonda media download $CLIP3 -o /tmp/clip-3.mp4
cat > /tmp/concat.txt <<EOF
file '/tmp/clip-1.mp4'
file '/tmp/clip-2.mp4'
file '/tmp/clip-3.mp4'
EOF
ffmpeg -y -f concat -safe 0 -i /tmp/concat.txt -c copy /tmp/merged.mp4
# 如果流复制失败，重新编码：
# ffmpeg -y -f concat -safe 0 -i /tmp/concat.txt \
#   -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -movflags +faststart \
#   -c:a aac -b:a 192k /tmp/merged.mp4

# 仅当下游wonda步骤需要媒体ID时才重新上传。
MERGED_MEDIA=$(wonda media upload /tmp/merged.mp4 --quiet)
```

`concat.txt`中的文件顺序 = 播放顺序。参见 `ffmpeg` 技能获取完整的concat参考。

### 分割场景 / 保留特定场景

两种模式，根据意图选择：

```bash
# 分割模式（默认）—— 返回每个检测到的场景作为其自己的媒体。
# JSON输出在 scenes[] 下列出每个场景（{mediaId,index,startS,endS}）。
wonda edit video --operation splitScenes --media $VID_MEDIA \
  --params '{"mode":"split","threshold":0.5,"minClipDuration":2}' --json
# 使用 -o，每个场景下载到编号文件（out-1.mp4, out-2.mp4, ...）；
# 单个检测到的场景直接写入路径。
wonda edit video --operation splitScenes --media $VID_MEDIA \
  --params '{"mode":"split","threshold":0.5,"minClipDuration":2}' -o scenes.mp4

# 移除模式（omit模式）—— 移除一个场景，将剩余部分合并为一个文件。
wonda edit video --operation splitScenes --media $VID_MEDIA \
  --params '{"mode":"omit","threshold":0.5,"minClipDuration":2,"outputSelection":"first"}' \
  --wait -o without-first.mp4
# outputSelection（omit模式仅限）："first", "last", 或1索引的数字 = 要移除的场景
```

使用omit模式用于“移除冻结的首帧”（Sora视频常见）。使用split模式获取所有场景作为单独片段。

### 图像编辑

任何图像编辑——img2img、背景移除、裁剪、文本叠加、矢量化——都有自己的技能，带有完整的决策树、宽高比规则和编辑模型瀑布：

```bash
wonda skill get image-edit
```

这里值得注意的一个技巧：图像和视频背景移除使用**不同**的模型（`birefnet-bg-removal` vs `bria-video-background-removal`）。切勿互换它们。

### 嘴唇同步（最后手段回退——优先使用原生音频视频模型）

Sora、Sora 2 Pro、Veo 3.1、Kling 3 和 Seedance 2 都能生成任何语言的语音，并带有正确同步的口型，作为视频本身的一部分。这条路径产生的结果远优于 `sync-lipsync-v2-pro`：更好的口型物理效果、更好的光照、更好的成本，且无需第二次推理往返。对于任何口播UGC、广告或代言人视频，直接将对话放在视频模型的提示中——不要链式TTS + 嘴唇同步。

仅在用户明确提供现有视频和现有音频片段并要求你将口型与音频对齐时，才使用 `sync-lipsync-v2-pro`。如果用户要求使用默认方法让角色说话，请提出反对：原生音频视频模型是更好的工具，并且适用于任何语言。

```bash
wonda generate video --model sync-lipsync-v2-pro --attach $VIDEO_MEDIA,$AUDIO_MEDIA --wait -o synced.mp4
```

### 视频放大

```bash
wonda generate video --model topaz-video-upscale --attach $VIDEO_MEDIA \
  --params '{"upscaleFactor":2}' --wait -o upscaled.mp4
```

### 切片（长视频 → 垂直短片）

`wonda clipping` 将长视频（播客、访谈、口播）处理成短垂直片段。选择由LLM驱动，并支持自然语言 `--brief`，以便你可以要求特定时刻而不是通用病毒性内容。

V1渲染9:16，带**人脸跟踪重帧**（LR-ASD主动说话者检测 + One-Euro稳定器，默认）和现有的 `animatedCaptions` 操作 + 每个片段的顶部三分之一钩状叠加。传递 `--reframe blur-fill` 以保持完整横向源在垂直画布内，背景模糊。

**翻译字幕：** 传递 `--caption-language <code>`（ISO-639-1，例如 `en`）以在另一种语言中渲染字幕，同时保留原始音频。每个片段的文本转录按句子翻译，语音时间保持同步，因此字幕保持同步。省略标志以使用说话语言字幕。在 `--restyle` 中，语言继承自父作业，除非被覆盖，因此你可以廉价地生成已切片作业的英文字幕版本（重用转录文本，无需重新转录）。

异步：`POST /api/v1/clipping` 返回 `clippingJobId`；CLI轮询 `GET /api/v1/clipping/jobs/{id}` 在 `--wait` 下。传递 `--output <dir>`，CLI下载每个渲染片段 + `plan.json`。

认证：包含在付费计划中。

**源：`--url` 接受YouTube和直接mp4 URL。**

```bash
wonda clipping --url "<youtube-url>" --brief "the most controversial moments" --wait
```

YouTube链接有效；长视频可能需要几分钟摄取才能开始转录。如果YouTube摄取失败，请先本地下载文件并上传，然后使用 `--media` 切片：

```bash
yt-dlp -o /tmp/source.mp4 \
  -f "bv*[ext=mp4][height<=720]+ba[ext=m4a]/b[ext=mp4][height<=720]" \
  --merge-output-format mp4 "<youtube-url>"
MEDIA=$(wonda media upload /tmp/source.mp4 --no-transcode --quiet)
```

`--no-transcode` 跳过服务器端normalize，因此长视频源在几秒钟内可用，而不是分钟（否则1小时上传会先转码约19分钟才能开始切片）。切片自动处理不兼容格式（AV1、旋转手机视频）根据选择的片段。省略标志用于计划发布或直接编辑而不切片的上传。

```bash
# 仅计划——快，不渲染
wonda clipping --media $MEDIA --brief "the most controversial moments" --dry-run --wait

# 完整流程：选择 + 渲染 + 下载
wonda clipping --media $MEDIA \
  --brief "the most controversial moments" \
  --caption-preset "TikTok Red Captions" \
  --hook auto \
  --wait --output ./clips/

# 翻译字幕为英文（原始音频保留）
wonda clipping --media $MEDIA --caption-language en --wait --output ./clips/

# 重新字幕现有作业为英文（重用STT + 片段选择，~$0）
wonda clipping --restyle <jobId> --caption-language en --wait --output ./clips/

# 按说话人筛选（使用ElevenLabs说话人分割标签）
wonda clipping --media $MEDIA --speaker SPEAKER_00 --wait --output ./clips/

# 说话人重命名用于可读性理由
wonda clipping --media $MEDIA --speaker Joe \
  --speaker-map '{"SPEAKER_00":"Joe","SPEAKER_01":"Guest"}' --wait --output ./clips/

# 调整数量和持续时间——选择目标长度带容差
wonda clipping --media $MEDIA --brief "punchy one-liners" \
  --count 5 --duration 20 --tolerance 5 --wait --output ./clips/

# 或者指定显式的最小/最大范围（与--duration/--tolerance互斥）
wonda clipping --media $MEDIA --brief "punchy one-liners" \
  --count 5 --min-duration 8 --max-duration 30 --wait --output ./clips/

# 从目录自动选择FX预设每个片段
wonda clipping --media $MEDIA --auto-preset \
  --preset-catalog '[{"slug":"flash_glow","description":"glow + scene flash"},{"slug":"text_glow","description":"per-word text glow"}]' \
  --wait --output ./clips/
```

作业状态形状（由GET `/api/v1/clipping/jobs/{id}`返回）：

```json
{
  "clippingJobId": "...",
  "status": "succeeded",
  "stage": "succeeded",
  "progress": 1,
  "plan": {
    "sourceDurationSec": 1800.5,
    "speakers": ["SPEAKER_00", "SPEAKER_01"],
    "clips": [
      {
        "start": 12.4,
        "end": 38.7,
        "title": "Why he quit the agency",
        "hookText": "He admits…",
        "rationale": "Concedes \"the agency model is dead\" then explains why...",
        "score": 87,
        "dominantSpeaker": "SPEAKER_00",
        "reframeMode": "blur-fill",
        "preset": null,
        "mediaId": "uuid-of-rendered-clip",
        "url": "https://storage.googleapis.com/.../clip.mp4"
      }
    ]
  },
  "error": null
}
```

## 编辑器操作参考

| 操作          | 输入                      | 关键参数                                                                                                 |
| ------------- | ------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `animatedCaptions` | video_0                   | fontFamily, position, sizePercent, fontSizeScale, strokeWidth, highlightColor                              |
| `textOverlay`      | video_0 + prompt            | fontFamily, position, sizePercent, fontSizeScale, strokeWidth                                              |
| `editAudio`        | video_0 + audio_0           | videoVolume (0-100), audioVolume (0-100)                                                                   |
| `merge`            | video_0..video_4            | Handle order = playback order                                                                              |
| `overlay`          | video_0 (bg) + video_1 (fg) | position, resizePercent                                                                                    |
| `splitScreen`      | video_0 + video_1           | targetAspectRatio (16:9 or 9:16)                                                                           |
| `trim`             | video_0                   | trimStartMs, trimEndMs (milliseconds)                                                                      |
| `crop`             | video_0                   | aspectRatio (16:9/9:16/1:1/4:5/21:9/custom) OR cropPercent+cropAxis. Ratio/percent based, NOT pixel coords |
| `volume`           | video_0                   | volume (0-100) or muted                                                                                    |
| `speed`            | video_0                   | speed (multiplier: 2 = 2x faster)                                                                          |
| `extractFrame`     | video_0                   | timestampMs or timestampPercent (outputs an image)                                                         |
| `extractAudio`     | video_0                   | Extracts audio track (outputs mp3)                                                                         |
| `reverseVideo`     | video_0                   | Plays backwards                                                                                            |
| `splitScenes`      | video_0                   | mode (split returns all scenes / omit returns one merged file), threshold, outputSelection (omit only)     |
| `skipSilence`      | video_0                   | maxSilenceDuration (default 0.03)                                                                          |
| `audioTrim`        | audio_0                   | trimStartMs, trimEndMs (milliseconds)                                                                      |
| `imageCrop`        | image_0                   | cropPixelX, cropPixelY, cropPixelWidth, cropPixelHeight (exact pixel rectangle)                            |
| `textOverlay`      | video_0 (image)             | Same as video textOverlay — works on images, outputs image (png/jpg)                                       |

> **`crop` vs `imageCrop`:** video `crop` is **ratio/percent** based (`aspectRatio` or `cropPercent`+`cropAxis`); it does NOT take pixel coordinates and rejects `cropPixelX/Y/Width/Height` with an error. For an **exact pixel rectangle**, use `imageCrop`. Run `wonda operations info <operation>` for the full param list, defaults, and ranges of any op.

有效文本覆盖字体：Inter, Montserrat, Bebas Neue, Oswald, TikTok Sans, TikTok Sans Condensed, TikTok Sans SemiCondensed, TikTok Sans SemiExpanded, TikTok Sans Expanded, TikTok Sans ExtraExpanded, Nohemi, Poppins, Raleway, Anton, Comic Cat, Gavency
有效位置：top-left, top-center, top-right, center-left, center, center-right, bottom-left, bottom-center, bottom-right

## 营销与分发

```bash
# 连接社交账号
wonda accounts instagram
wonda accounts tiktok

# 分析
wonda analytics instagram
wonda analytics tiktok
wonda analytics meta-ads

# 有机自有帖子分析使用平台特定读取命令：
# wonda x analytics, wonda linkedin analytics, wonda reddit analytics.
# 上述全局分析组用于连接的营销API。

# 爬取竞争对手
wonda scrape social --handle @nike --platform instagram --wait
wonda scrape social-status <taskId>                   # 获取社交爬取结果
wonda scrape cancel <taskId>                          # 取消任何公开爬取任务
wonda scrape ads --query "sneakers" --country US --wait
wonda scrape ads --query "sneakers" --country US --search-type keyword \
  --active-status active --sort-by impressions_desc --period last30d \
  --media-type video --max-results 50 --wait
wonda scrape ads-status <taskId>                      # 获取广告搜索结果

# 下载单个reel或TikTok视频
SCRAPE=$(wonda scrape video --url "https://www.instagram.com/reel/ABC123/" --wait --quiet)
# → 返回包含mediaId的媒体数组爬取结果

# 发布
wonda publish instagram --media <id> --account <accountId> --caption "New drop"
wonda publish instagram --media <id> --account <accountId> --caption "..." --alt-text "..." --product IMAGE --share-to-feed
wonda publish instagram-carousel --media <id1>,<id2>,<id3> --account <accountId> --caption "..."
wonda tiktok creator-info --account <accountId>      # 实时隐私选项 + 评论/合拍/拼接默认值
wonda publish tiktok --media <id> --account <accountId> --caption "New drop" --privacy PUBLIC_TO_EVERYONE
wonda publish tiktok --media <id> --account <accountId> --caption "..." --privacy PUBLIC_TO_EVERYONE \
  --disable-comment --commercial-disclose --brand-organic
wonda publish tiktok-carousel --media <id1>,<id2> --account <accountId> --caption "..." \
  --privacy PUBLIC_TO_EVERYONE --cover-index 0

# 历史记录
wonda publish history instagram --limit 10
wonda publish history tiktok --limit 10

# 浏览媒体库
wonda media list --kind image --limit 20
wonda media info <mediaId>
```

### X/Twitter

支持读取、写入和社交图谱。

> ⚠️ **反欺诈警告：不要探测刚粘贴的cookie。** 当你刚收到cookie（你的或用户的）时，它们上的第一个请求应该是用户实际想要的操作，而不是 `wonda x auth check`，不是 `wonda x home`，不是任何探测操作。新IP/设备/进程上的突发活动是X（以及Reddit / LinkedIn / IG）将凭证盗窃标记为文本的典型信号，cookie会被影子封禁或硬杀死。如果你必须验证，请使用 `wonda x auth check --account <name> --via wab`（该操作通过账户现有的登录浏览器会话路由：相同IP，相同指纹，相同浏览历史）而不是从新进程发出原始API请求。

```bash
# 认证设置（运行 `wonda x auth --help` 获取详细信息）
wonda x auth set --auth-token <token> --ct0 <ct0>
wonda x auth set --account <name> --auth-token <...> --ct0 <...>  # 多账户
wonda x auth check                                              # 原始探测，见警告
wonda x auth check --account <name> --via wab                   # 安全：通过账户的WAB会话路由
wonda x auth status --account <name>                             # 本地来源、生成、所有权、cookie名称和风险；永不探测
wonda x auth refresh --account <name> --persona <persona>       # 过期WAB与磁盘同步，然后WAB侧会话检查；永不原始探测
wonda x browser-bootstrap --account <name>                       # 将存储的cookie注入运行的绑定WAB人格

# 读取
wonda x search "sneakers" -n 20                     # 搜索推文（排序：最新、当前、顶部；时间：天、周、月、年、全部）
wonda x --freshen search "sneakers" --via cookies   # 刷新选定的过期cookie存储，然后进行仅cookie读取
wonda x search "sneakers" --sort top --time week -n 20  # 过去一周的顶部推文
wonda x user @nike                                   # 用户资料
wonda x user-tweets @nike -n 20                      # 用户的最近推文
wonda x read <tweet-id-or-url>                       # 单个推文
wonda x analytics <tweet-id-or-url>                  # 推文指标：viewCount, likeCount, retweetCount, replyCount
wonda x insights <tweet-id-or-url>                   # 别名x analytics
wonda x replies <tweet-id-or-url>                    # 推文的回复
wonda x thread <tweet-id-or-url>                     # 完整线程（作者的自我回复）
wonda x home                                         # 主页时间线（--following为关注标签）
wonda x bookmarks                                    # 你的书签
wonda x likes                                        # 你喜欢的推文
wonda x following @handle                            # 用户关注的人
wonda x followers @handle                            # 用户的关注者
wonda x lists @handle                                # 用户的列表（--member-of为成员资格）
wonda x list-timeline <list-id-or-url>               # 列表中的推文
wonda x news --tab trending                          # 热门话题（标签：for_you, trending, news, sports, entertainment）
wonda x mentions -n 20                               # 最近回复和@提及你的账户
wonda x dm inbox -n 20                               # X DM对话，默认cookie路径
wonda x dm requests -n 20                            # X DM消息请求，默认cookie路径
wonda x dm read <conversation-id> -n 50              # 某个对话中的消息
wonda x dm read <conversation-id> --via wab          # 通过WAB浏览器会话路由的相同读取

# 写入（推文/回复/互动默认为--via wab；X DM发送仅wab）
wonda x tweet "Hello world"                          # 发布推文
wonda x tweet "Hello world" --account <name> --via wab  # 全部隐蔽通过真实浏览器
wonda x tweet "Hello world" --attach ~/clip.mp4      # 附加图像/动图/视频（最多4个）
wonda x reply <tweet-id-or-url> "Great point"        # 回复
wonda x like <tweet-id-or-url>                       # 喜欢
wonda x unlike <tweet-id-or-url>                     # 取消喜欢
wonda x retweet <tweet-id-or-url>                    # 转发
wonda x unretweet <tweet-id-or-url>                  # 取消转发
wonda x follow @handle                               # 关注
wonda x unfollow @handle                             # 取消关注
wonda x feed-engage --authors "a,b" --duration 5m    # 浏览信息流并喜欢这些作者的帖子（仅wab）
wonda x feed-engage --keywords "wonda alternative" --reply --max-reply 3  # 监控搜索结果，门控相关性，通过WAB回复
wonda x dm send <conversation-id> "Hey, quick note"  # 在现有DM对话中发送，仅wab
wonda x dm send <conversation-id> "Hey" --dry-run    # 仅输入，不点击发送
wonda x dm accept <conversation-id> --dry-run        # 打开消息请求但不接受它
wonda x dm accept <conversation-id>                  # 接受传入的DM请求，仅wab
wonda x dm start @handle --text "Hey, quick note"    # 通过handle启动或重用DM，仅wab
wonda x dm passcode set --account <name>             # 为该账户保存加密的XChat密码
wonda x dm passcode status --account <name>          # 显示是否配置了密码

# 维护
wonda x refresh-ids                                  # 从X的JS包中刷新缓存的GraphQL查询ID
```

所有分页命令支持：`-n <count>`，`--cursor`，`--all`，`--max-pages`，`--delay <ms>`。

`wonda x user` 在成员在公共资料中发布明确联系信息或X为该资料暴露扩展URL实体时，包含加性 `emails` 和 `links` 字段。这些字段是只读的，等同于手动读取资料。不涉及推断电子邮件、丰富数据、存储或DOM抓取。

**推文模式：** `tweet` 命令有两个传输：

- **`--via cookies`（内部API）：** X的内部GraphQL（≤280字符的 `CreateTweet`，长文本Premium的 `CreateNoteTweet`）。快速（<1秒），支持 `--attach` 用于媒体。偶尔在X旋转查询ID或功能标志时失败，错误代码226。当这种情况发生时，通过 `twitter-tone-research/_artifacts/scripts/capture-ct-bw.mjs` 重新捕获并调整 `xclient/` 中的三个旋钮。
- **`--via wab`（写入默认）：** 通过账户的WAB Chromium（在第一次使用 `--via wab` 时自动启动），打开x.com撰写，以人类风格抖动输入，点击发布。支持 `--attach`（图像/动图/视频，最多4个）；文件通过Playwright的 `setInputFiles` 驱动，不会打开原生选择对话框；脚本等待X的上传管道完成（视频最多5分钟）然后提交。零指纹风险。较慢（文本~10秒，视频~30-90秒），但完全防漂移：无需维护查询ID、功能标志或请求形状。隐蔽浏览器+Chromium安装一次通过 `wonda wab install`（~315 MB，一次性，幂等）。Cookies存储在 `~/.wonda/x-cookies/<account>.json`，通过 `account-bindings.json` 绑定到账户的人格。`wonda x reply --attach` 仅wab（无cookie路径）。

### 入站互动

收到的互动是指对双胞胎自己内容的入站活动：回复、提及、评论和DM。这是出站发布、喜欢和关注的反向方向。

这不是关键词监控，不是发送邀请/外联接受跟踪，也不是出站行动账本。使用平台搜索命令进行关键词监控。使用 `wonda actions` 进行出站行动统计。

```bash
wonda inbound                                      # 每个本地人格的新入站项
wonda inbound --persona brubakerwise              # 一个人格
wonda inbound --platform x -n 20                  # 仅X提及/回复
wonda inbound --platform linkedin                 # LinkedIn通知
wonda inbound --platform reddit                   # Reddit经典收件箱
wonda inbound --all                               # 抛出获取的项，不进行高水位差异或状态写入
```

`wonda inbound` 仅分发给直接读取客户端：X提及/回复、LinkedIn通知和Reddit经典收件箱。输出始终是标准化JSON：

```json
{
  "new_count": 1,
  "items": [
    {
      "persona": "brubakerwise",
      "platform": "x",
      "account": "brubakerwise",
      "kind": "reply",
      "author": "someone",
      "text": "Useful point",
      "target_id": "2069000000000000000",
      "item_id": "2069000000000000001",
      "timestamp": "2026-06-22T12:00:00Z",
      "url": "https://x.com/someone/status/2069000000000000001"
    }
  ]
}
```

**X DMs:** `wonda x dm inbox`, `wonda x dm requests`, 和 `wonda x dm read` 默认通过 cookie 支持的 `xclient` 路径进行读取，并且可以使用 `--via wab` 来实现浏览器会话传输一致性。`requests` 返回不可信/消息请求的收件箱，以便接收端可以显式处理接受。`wonda x dm send`, `wonda x dm start`, 和 `wonda x dm accept` 仅限于 WAB 的 DOM 写入：发送会打开真实的 X 消息界面，在 `[data-testid="dmComposerTextInput"]` 中输入内容，并点击发送按钮；接受会通过 Chat 打开请求线程，并点击可见的接受/允许控件。`start` 在发送前会验证所选建议的屏幕名是否等于请求的账号，WAB DM 写入会验证当前活跃的 X 浏览器账号（当 `--account` 或 persona 绑定提供时）。如果 `x dm send` 或 `x dm start` 失败并返回 `recipient_cannot_receive_dm`，则 X 在发送前已拒绝该 DM。请确认接收者是否可以从发送者接收 DM：可能需要互相关注/连接，接收者可能需要接受任何待处理的消息请求后重试。如果 X 显示加密的 XChat 密码门，请使用 `wonda x dm passcode set --account <name>` 存储密码；它使用与 cookie 临近存储相同的本地密钥模式进行本地加密，并且永远不会打印或包含在错误包中。更深层的 XChat/Juicebox 消息解密/加密支持在 X 暴露需要它的线程之前仍不受支持。

### LinkedIn

支持搜索、个人资料、公司、消息和互动。

> ⚠️ **与 X 相同的反欺诈注意事项：不要探测刚粘贴的 cookie。** 新 cookie 的首次请求 = 实际操作，绝不是检查。LinkedIn 的反欺诈是所有平台中最激进的（强制登出、重置密码、账号标记）。如果你必须验证，请使用 `wonda linkedin auth check --account <name> --via wab` 通过账号现有的 WAB 会话进行路由。

```bash
# 认证设置（运行 `wonda linkedin auth --help` 获取详细信息）
wonda linkedin auth set --li-at-value <v> --jsessionid-value <v>
wonda linkedin auth set --account brand-A --li-at-value <...> --jsessionid-value <...>  # 多账号
wonda linkedin auth check                                              # 原始探测，见警告信息
wonda linkedin auth check --account <name> --via wab               # 安全：通过账号的 WAB 会话路由
wonda linkedin auth status --account <name>                        # 仅本地：cookie 来源（登录 vs 粘贴）+ 429 风险，永不探测
wonda linkedin auth refresh --account <name> --persona <persona>   # 本地新鲜度预检；陈旧的 WAB → 磁盘同步，永不原始探测

# 读取
wonda linkedin me                                    # 您的身份
wonda linkedin search "data engineer" --type PEOPLE  # 搜索（类型：PEOPLE，COMPANIES，ALL）
wonda linkedin profile johndoe                       # 查看个人资料（昵称或 URL）
wonda linkedin profile johndoe --via public          # 通过付费抓取 API 查看公开个人资料数据
wonda linkedin profile johndoe --via public --force-refresh --idempotency-key run-123
wonda linkedin enrich johndoe janedoe                # 批量个人资料丰富，通过 cookies，最多 25 个输入
wonda linkedin enrich johndoe janedoe --via public   # 付费公开丰富任务，默认等待完成
wonda linkedin enrich johndoe --via public --no-wait # 仅创建任务，然后轮询 GET /scrape/linkedin-profiles/{taskId}
wonda linkedin company google                        # 查看公司页面
wonda linkedin resolve <fsd-profile-id>...            # 将 ACoAA 成员 ID 解析为公开昵称（仅 cookies，按账号缓存）
wonda linkedin conversations                         # 列出消息线程
wonda linkedin conversations --resolve               # 填充缺失的参与者/发送者昵称字段
wonda linkedin messages <conversation-urn>           # 读取线程中的消息
wonda linkedin messages <conversation-urn> --resolve # 填充缺失的发送者昵称字段
wonda linkedin conversation-state <vanity-or-url> --via wab # 仅读取该成员的 1:1 线程摘要；永不列出收件箱或打印正文
wonda linkedin notifications -n 20                   # 最近通知
wonda linkedin connections                           # 您的连接（最近添加的顺序，每个连接都有 connectedAt）
wonda linkedin connections johndoe                   # 对您可见的成员的连接（连接搜索；相关性顺序，无日期；--degree 1|2|3 按您的距离过滤；--all 枚举）
wonda linkedin sent-invitations                      # 待发送的邀请 + 审计对账；cookies 默认，支持 --via wab
wonda linkedin invitations                           # 接收的连接请求，包含备注和 sharedSecret（仅 cookies 读取）
wonda linkedin connection-status johndoe janedoe     # 按成员：已连接 / 待发送（入|出） / 未连接（仅 cookies）
wonda linkedin saves                                 # 您保存的帖子（我的物品 → 保存的帖子；--all, --enrich 用于点赞/评论）
wonda linkedin analytics <activity-id>               # 已拥有的帖子分析：展示量，独立观众，互动量，个人资料浏览量（当 LinkedIn 公开时）
wonda linkedin analytics --profile                   # 个人资料浏览分析（当 LinkedIn 为账号公开时）
wonda linkedin reactions <activity-id>               # 反应，包含反应者个人资料 + 类型
wonda linkedin comment-reactors <comment-url-or-activityId:commentId> # 特定评论上的反应，包含反应者个人资料 + 类型
wonda linkedin browser-bootstrap                     # 将存储的 cookies 注入 WAB 个人资料（一次性 + 旋转时）
wonda linkedin comments <activity-id> --account <name> --via wab  # 评论者，包含个人资料 + 昵称（自动生成 WAB）
wonda linkedin activity johndoe                      # 结构化的最近活动。--type all（他们的帖子 + 转发，默认）| comments（他们评论的帖子，包含他们自己的评论文本）| reactions（他们反应的帖子，包含反应类型）。每个项目都包含底层帖子的发布时间、链接、作者（姓名 + 个人资料 URL）和文本；--count N（默认 20）
wonda linkedin activity johndoe janedoe --engine cloud --via wab --json # 批量接受 2-10 个个人资料，--count 最多 25（最多 250 个项目）通过云双胞胎的实时 WAB 会话；单个个人资料接受 --count 最多 100。永不读取本机上的 cookies 文件或回退到本地执行；批量输出保留每个个人资料的错误，在全局速率限制信号时立即停止，标记剩余个人资料为 not_attempted，并报告可见性为存在活动时可见或不可见时不可见，或未知。
wonda linkedin search-posts "<keyword>" --date-range past-week --account <name>  # 关键字到最近帖子 + 作者个人资料（默认通过 cookies 的 Voyager 内容 API，返回活动 ID + 精确的帖子时间；--via wab 用于 DOM 抓取回退；用于社交聆听运行 `wonda skill get linkedin-social-listening`）

# 销售导航（账号限制：需要 LinkedIn 账号有一个 SN 座位；cookies 读取，每个动词也作为云双胞胎动作运行）
wonda linkedin salesnav search "VP marketing" --seniority CXO --region "Berlin, Germany"  # 分面潜在客户搜索；也 --industry/--company/--function/--connection-of；'~' 前缀排除一个值；--csv 导出。分面标记接受一个普通名称 OR 一个分面 ID：名称自动解析（公司 + connection-of 通过全局类型预测；标题/区域/行业/功能/学校通过分面类型预测，CURRENT_TITLE/PAST_TITLE 在类型 TITLE 下提供，REGION 在 BING_GEO 下提供；SENIORITY_LEVEL 和 YEARS_OF_EXPERIENCE 首先离线针对记录的表：seniority 100 在培训中，110 入门级，120 高级，130 战略，200 入门级经理，210 经验丰富的经理，220 总监，300 副总裁，310 CXO，320 所有者 / 合伙人；名称的表会回退到类型预测下的类型 SENIORITY_V2 / TENURE，所以 LinkedIn 自己的标签如 "3 到 5 年" 也有效）。一个模糊的名称会列出候选 ID 及其子文本（公司/位置对于公司，职位/公司对于人员），以便您选择并重新运行使用 ID。每个潜在客户已经携带搜索响应中内联的卡片装饰（无每个潜在客户的读取）：连接度，当前角色的任期 + 开始月份/年份，和聚光灯徽章（最近雇佣，N 个最近的帖子）。教育/毕业年份不在搜索中；添加 `salesnav profile <urn> --enrich` 添加。默认传输是 sales-api JSON 路径通过 cookies；传递 `--via wab` 用于 DOM 抓取回退（驱动登录的 SN SPA 并抓取渲染的结果卡片），这可以生存 LinkedIn 旋转搜索装饰 ID，代价是渲染卡片不显示的内联字段（成员 urn，精确的职位开始日期，保存/查看/高级标记，和列表成员计数）。连接度，当前角色的任期，和聚光灯徽章仍然被抓取。无论哪种方式，`SalesLead` 输出和 `--csv` 列都相同（CSV 展平了主要 JSON 领导字段：身份，当前角色 + 最新的过去角色，任期，聚光灯标签，保存/查看/打开链接标记，列表计数，两个 URNs；深度嵌套如完整职位列表和公司 URNs 保持 JSON 仅）。销售-api 403 自愈：CLI 驱动角色 WAB 到 linkedin.com/sales 一次以铸造 SN li_a cookie，同步 cookies，并重试；错误意味着恢复无法帮助（死亡的 LinkedIn 登录，没有 SN 座位）或恢复步骤本身失败（例如 WAB 无法启动或同步），消息会说明哪个。恢复被故意禁用在使用显式凭证覆盖（--li-at/--jsessionid 或 LI_AT/LI_JSESSIONID 环境变量）下，因为它重新加载磁盘上的账号存储并可能切换身份：这些调用会显示手动运行手册。
wonda linkedin salesnav search --school "HEC Paris" --past-company SpaceX --past-title 3 --years-of-experience 6-10  # 背景分面：学校/大学，过去雇主，过去工作职位，工作年限桶（id 或标签，尾随 'y' 可选：1 <1y, 2 1-2y, 3 3-5y, 4 6-10y, 5 10+y）；--title 过滤当前工作职位
wonda linkedin salesnav facets SCHOOL "HEC Paris"    # 将分面值名称解析为搜索使用的 ID（无参数列出过滤器类型）。公司在此处不解析（分面类型预测返回 CURRENT_COMPANY/PAST_COMPANY 为 []）：通过 `salesnav typeahead` 解析公司名称，或仅传递名称到搜索标志并让其自动解析。命令自动别名为 CURRENT_TITLE/PAST_TITLE 为 TITLE，REGION 为 BING_GEO，SENIORITY_LEVEL 为 SENIORITY_V2，和 YEARS_OF_EXPERIENCE 为 TENURE（类型预测实际服务的类型），所以 `facets SENIORITY_LEVEL` 列出实时 seniority 值
wonda linkedin salesnav --help                       # 更多账号限制读取：保存的搜索，列表，个人资料，类型预测，推荐潜在客户|公司，警报，最近，个人资料，通知，热介绍，洞察
wonda linkedin salesnav profile "urn:li:fs_salesProfile:(ACwAA...,NAME_SEARCH,eQ3R)"  # 通过 fs_salesProfile urn（名称 + 图片）解析一个或多个 SN 潜在客户（添加 --enrich 为每个潜在客户的学历（学校/学位/领域/年份），完整经验历史，和 years-of-experience（可选；每个潜在客户 2 个额外的 Voyager 读取，最多 25 个）
wonda linkedin salesnav save-lead "urn:li:fs_salesProfile:(ACwAA...,NAME_SEARCH,eQ3R)"  # 保存一个潜在客户（WAB 写入：点击 /sales/lead/ 页面的保存；无 cookies 路径）。幂等：一个已保存的潜在客户报告 changed:false 而不点击。--unsave 选择潜在客户的复选框在保存的搜索中，并点击结果工具栏的直接 Unsave 控制（主要路径，然后验证结果）；旧卡片溢出菜单流程只是一个回退——LinkedIn 忽略该菜单操作（验证 2026-07-22），所以回退运行仍然以诚实的 sn_unsave_inert 错误结束。也接受裸 token urn 或原始潜在客户 ID，如 `salesnav profile`
wonda linkedin salesnav create-list "Berlin CTOs" --description "Q3 outbound"  # 创建一个潜在客户列表（仅 WAB 写入：通过个人资料浏览器中的 SN 列表 UI 点击通过）。打印其数字 ID；SN 允许重复名称，结果会携带 duplicateName:true 当一个已经存在时
wonda linkedin salesnav delete-list 7478163673497243649  # 通过其数字 ID 删除一个潜在客户列表（仅 WAB 写入）。幂等：一个缺失的 ID 报告 notFound 并退出 0
wonda linkedin salesnav message "urn:li:fs_salesProfile:(ACwAA...,NAME_SEARCH,eQ3R)" --text "Hi Ada, ..." --expect-name "Ada Fixture"  # 预览优先（仅 WAB，无 cookies 路径）：在潜在客户的 SN 页面上编写消息/InMail 并返回确切的编写文本（预览ed:true，发送ed:false）而不发送。必须有人批准该文本；添加 --send 以实际发送（一个单独的显式步骤）。在 --send 模式下，编写字段在发送前立即重新读取，必须等于 --text（和 --subject 当存在时）否则发送中止（compose_text_mismatch）——一个消息只能在字段可验证地包含批准的文本时发送。--expect-name 是强制性的：该操作在接触编写之前验证渲染的潜在客户名称，并在不匹配时拒绝（recipient_mismatch）。1st-degree 潜在客户获得常规消息；其他人获得 InMail 表单，其中 --subject 填充主题（当没有主题字段渲染时跳过）。SN 块（没有 InMail 信用，潜在客户不可发送消息）会以对话框文本和结构化原因失败。
wonda linkedin salesnav connect "urn:li:fs_salesProfile:(ACwAA...,NAME_SEARCH,eQ3R)" --expect-name "Ada Fixture" --note "Hi Ada, ..."  # 预览优先（仅 WAB，无 cookies 路径）：在潜在客户的页面上打开 SN 的连接流程（顶卡连接或溢出 "..." 菜单项，使用真实操作系统鼠标点击，因为 SN hue-menu 项可以是惰性的），填充可选的 --note，并返回它（预览ed:true，发送ed:false）而不发送。必须有人批准；添加 --send 以实际发送（一个单独的显式步骤）。在 --send 模式下，备注字段在发送前立即重新读取，必须等于 --note 或发送中止（connect_note_mismatch）。--expect-name 是强制性的：该操作在接触邀请之前验证渲染的潜在客户名称，并在不匹配时拒绝（recipient_mismatch）。1st-degree 潜在客户（或一个有未决邀请的）没有连接功能，并干净地报告 alreadyConnected。SN 块（每周邀请限制，无法连接）会以对话框文本和结构化原因失败。
wonda linkedin salesnav list-add 7478163673497243649 "urn:li:fs_salesProfile:(ACwAA...,NAME_SEARCH,eQ3R)"  # 将一个潜在客户保存到潜在客户列表（列表 ID 或确切名称；urn 来自 `salesnav search`）。仅 WAB 写入：切换潜在客户页面的保存弹出窗口。`list-remove` 撤销它（回退到列表页面的行操作）。两者幂等：已成员/非成员退出 0 并报告 changed:false
wonda linkedin salesnav save-search "UK founders" --seniority 310 --region 101165590  # 在账号上保存搜索（仅 WAB 写入：在个人资料 WAB 中渲染搜索，并切换过滤器面板的保存搜索切换；与 `salesnav search` 相同的关键字 + 分面标志；幂等——已保存报告 changed:false）。当前 SN UI 自动命名保存的搜索：<name> 位置参数仅为建议，不应用（输出携带 named:false；在 SN UI 中重命名，或删除保存的搜索并重新创建在那里）。读取循环：`salesnav saved-searches` 然后显示每个保存的搜索的 id 和 newHitsCount（自上次 viewedAt 以来新匹配的潜在客户）
wonda linkedin salesnav delete-saved-search 50123456  # 通过 id 删除一个保存的搜索（来自 `salesnav saved-searches`）；仅 WAB 写入，幂等：一个缺失的 id 报告 notFound:true 并退出 0

# WAB 生命周期（参见 `wonda wab --help` 获取完整界面：启动/停止/状态/安装/绑定/同步 cookies/日志）
wonda linkedin enrich-engagers --activity-id <id>    # 抓取参与者 + 通过个人资料 + 当前雇主丰富每个（加入 JSON；--company-detail=false 跳过公司页面查找）
wonda linkedin enrich-engagers --activity-id <id> --profile-source public  # 保持参与者集合登录，使用付费公开个人资料详情

# 写入
wonda linkedin visit <vanity-name> --account <name>  # 在 WAB 中访问真实的个人资料页面，停留，并可选通知目标
wonda linkedin connect <vanity-name> --message "Hey!" # 发送连接请求并附带备注
wonda linkedin connect <vanity-name> -m "Hey!" --account <name> --via wab  # 完全隐蔽通过账号的个人资料
wonda linkedin follow <vanity-name-or-url> --account <name> # 关注成员或公司（仅 WAB；主要按钮或“更多”下；幂等）
wonda linkedin comment <activity-id> --account <name> # 添加评论（仅 WAB：需要 SDUI 渲染状态）
wonda linkedin reply-comment <activity-id> <comment-id> "Good point." --account <name> # 在特定评论下回复（仅 WAB）
wonda linkedin mute <vanity-name-or-url> --account <name> # 静音成员在发布者的动态中的帖子（仅 WAB；保留连接）
wonda linkedin edit-post <activity-id-or-url> "Updated body" # 编辑您自己的帖子（仅 WAB：菜单 -> 编辑帖子 -> 保存 -> 验证）
wonda linkedin edit-comment <activity-id-or-url> <comment-id> "Updated comment" # 编辑您自己的评论（仅 WAB：评论菜单 -> 编辑 -> 保存 -> 验证）
wonda linkedin like <activity-urn>                   # 点赞帖子
wonda linkedin like <activity-urn> --comment <commentId>        # 点赞特定评论（仅 WAB）
wonda linkedin like <activity-urn> --comment <commentId> --reaction love  # 对特定评论反应
wonda linkedin unlike <activity-urn>                 # 取消点赞
wonda linkedin unlike <activity-urn> --comment <commentId>      # 从特定评论中移除您的反应（仅 WAB）

wonda linkedin send-message <conversation-urn> "Hi!" # 发送消息
wonda linkedin inmail <vanity-name> --message "Hi!" --subject "Quick question" # 原生LinkedIn InMail (仅WAB)
wonda linkedin post "Excited to announce..."         # 创建帖子
wonda linkedin post "A quick visual note" --media ./image.png --via wab # 带媒体创建帖子
wonda linkedin delete-post <activity-id>             # 删除帖子
wonda linkedin delete-comment <comment-url-or-activityId:commentId> # 删除自己的评论 (WAB: 评论菜单 -> 删除 -> 确认 -> 验证)
wonda linkedin feed-engage --authors "a,b" --duration 5m  # 浏览动态并点赞这些作者的帖子 (仅WAB)
wonda linkedin feed-engage --keywords "short form video" --reply --max-reply 3  # 监控内容搜索，筛选相关性，通过WAB评论
wonda linkedin feed-engage --authors "a,b" --engage-comments --max-comment-engage 2  # 同时对已点赞帖子的匹配评论进行互动
wonda linkedin engage-commenters --post <activity-id-or-url> --actions like,reply,connect --reply-text "Good point." --connect-note "I liked your perspective here." --max-commenters 25 --duration 3m  # 读取帖子的评论者，然后点赞、回复或连接 (付费，WAB写入)

# 账户创建 (仅WAB，标记：linkedinAccountCreationEnabled)
wonda linkedin signup --persona <name> --random                                     # 端到端创建全新账户
wonda linkedin signup --persona <name> --email <addr> --first-name Ada --last-name Lovelace --password <pw>
wonda linkedin signup --persona <name> --job-title "Engineer" --company "Acme"       # 带就业信息的个人资料阶段 (默认：学生路径)
wonda linkedin signup --persona <name> --resume code --email <addr>                  # 手动步骤后的简历

```

分页命令支持：`-n <count>`，`--start`，`--all`，`--max-pages`，`--delay <ms>`。

`wonda linkedin profile` 在成员在LinkedIn的联系方式中显示这些信息时，包含加性的 `emails`，`websites`，`phone` 和 `twitter` 字段。联系方式读取使用与个人资料读取相同的登录的Voyager cookie和CSRF路径，在隐藏或速率限制时尽力而为，等同于手动打开联系方式覆盖层。它不会推断、丰富、持久化或批量收集联系人。

**LinkedIn成员身份解析：** `wonda linkedin resolve <id>...` 接受裸 `ACoAA...` fsd个人资料ID以及 `urn:li:fsd_profile:` 和 `urn:li:fs_miniProfile:` 包装器。它为每个唯一缓存未命中执行一次仅cookie的Voyager读取，并将正面结果存储30天在选定账户下。`--no-cache` 跳过持久化缓存读取和写入，但仍在调用内去重。数值 `urn:li:member:<id>` 值被拒绝，因为LinkedIn的认证网络重定向保留了数值ID，并且没有稳定的Voyager映射端点可用。`conversations --resolve` 和 `messages --resolve` 使用相同的缓存，并且仅填充现有的空白 `vanityName` 字段；如果没有 `--resolve`，其输出保持不变。

`wonda linkedin profile` 还返回 `education` (一个包含 `{school, degree, fieldOfStudy, startYear, endYear}` 的列表，`endYear` 0表示正在进行中)，`yearsOfExperience` (职业跨度年数，从最早有日期的经歷计算；如果没有则为0)，以及完整的 `experiences` 工作经历 (每个 `{title, companyName, companyUrn, companyUniversalName, startYear, startMonth, endYear, location}`，`endYear` 0表示当前)，以及 `currentCompany` 在相同形状中显示当前角色。这些读取与个人资料的其他部分使用相同的登录的Voyager cookie/CSRF路径，在隐藏或速率限制时尽力而为。

**LinkedIn个人资料访问预热：** `wonda linkedin visit <vanity-or-url> --account <name>` 仅WAB，并且有意与 `wonda linkedin profile` 分开。`profile` 是一个隐蔽的数据读取，不会触发查看你的个人资料。`visit` 在角色浏览器中打开真实的 `/in/<vanity>/` 页面，默认停留6-20秒，除非设置了 `--no-scroll`，然后返回 `{ ok, status, profile, dwellMs, scrolled }`。LinkedIn的隐私或匿名个人资料查看设置可以抑制目标通知。

**LinkedIn账户创建：** `wonda linkedin signup` 配置全新的LinkedIn账户：它创建一个一次性邮箱（或使用 `--email`），在无头WAB窗口中驱动加入流程（电子邮件加密码、姓名、通过电子邮件验证的代码、个人资料），从收件箱获取验证PIN，然后绑定角色并同步cookies，以便LinkedIn读取和写入通过新账户路由。由 `linkedinAccountCreationEnabled` 标志控制（服务器评估的预检：`GET /linkedin/signup/enabled`）。首先将移动或住宅代理绑定到角色 (`wonda wab config set <persona> proxy_url socks5://...`)：LinkedIn比Reddit更难地阴影禁止在数据中心IP上创建的账户。LinkedIn经常插入一个验证码或“安全验证”谜题，流程无法自动通过；当无法定位字段时，流程会暂停并停留在该屏幕，因此手动完成后再使用 `--resume <step>` (`account|name|code|profile|persist`)。成功时，它打印 `{name, email, password, persona, account}` 以及一个准备粘贴的 `op item create` 块用于“LinkedIn登录”保险库。

**连接请求模式：** `connect` 命令有两个传输：

- **`--via cookies` (API)：** 带指纹缓解的Voyager REST API（个人资料访问、抽屉预热、连接）。快速 (~3秒)，支持通过 `customMessage` 的注释。
- **`--via wab`：** 通过账户的角色Chromium（自动启动）进行完全隐蔽的DOM调度。零指纹风险。较慢 (~10秒) 但完全安全。当您需要额外保护时使用。隐蔽浏览器 + Chromium安装一次通过 `wonda wab install` (~315 MB，幂等）。角色在其持久化个人资料下重用 `~/.wonda/wab/personas/<persona>/profile`。Cookies存储在 `~/.wonda/linkedin-cookies/<account>.json`，绑定到通过 `account-bindings.json` 的角色；通过 `wonda linkedin auth set --account <name>` 推送新的cookies到正在运行的实时Chromium。

**连接请求JSON失败：** 一个失败的本地WAB连接退出非零，并将结构化的JSON错误写入stderr。`error.code` 对于真实的单次拒绝保持 `send-rejected`。每周邀请限制或静默发送丢失使用 `send-throttled` 并带有机器原因 `weekly_invitation_limit` 或 `silent_drop`；HTTP 429 保持 `blocked:rate-limit` 并带有原因 `http_429`。连接失败包括 `throttled`，可见的UI失败包括原始toast在 `detail` 中。使用JSON输出时，本地 `--hard` 动作预算停止发出 `error: "hard-rate-limit"`，`throttled: true`，和 `reason: "local_hard_limit"` 在stdout上，同时保持现有的stderr句子。云包装的失败保留现有的外部HTTP状态、`error.code` 和 `error.reason`；原始连接令牌和原因作为附加的 `error.actionCode` 和 `error.actionReason` 字段。

**LinkedIn InMail：** `wonda linkedin inmail <vanity-or-url> --message <body> [--subject <subject>] [--spend-credit] [--dry-run]` 仅在WAB中驱动LinkedIn的原生InMail作曲家。它不是 `connect` 也不是 `send-message`；对于一级收件人，会拒绝并指向 `[text](url)`。打开个人资料 / 免费InMail 可以在不需要信用确认的情况下发送。如果LinkedIn指示将消耗一个InMail信用，命令将停止 `sent:false` 并退出0，除非提供 `--spend-credit` (`--yes-consume-credit` 仍然作为过时的别名工作)。`--dry-run` 填充作曲家并在发送前停止。

**LinkedIn Recruiter Lite (Wonda 1.61.0+)：** `wonda linkedin recruiter` 通过选定的LinkedIn账户/角色提供六个命令，并需要其Recruiter Lite席位。Cookie搜索、列表、有界原生打开和分页已通过正常CLI验证在现有的保存查询上。一个预期候选人的个人资料比较保留了七个职位、两个教育记录和42项技能，跨越cookie和WAB传输；最终的cookie个人资料返回退出0和 `partial:false`。匹配原生参数编码和Recruiter应用上下文解决了观察到的请求失败，使用现有的cookies。原生WAB保存/列表/打开观察到在预期的真实保存中，警报关闭。Cookie保存使用检查的原生客户端合同，带重复/容量检查、单次尝试创建和保存搜索ID验证，但只有 fixture 覆盖；没有为实时测试创建额外记录。没有建立彻底的过滤器/运算符平等性，原生打开拒绝过滤器覆盖。

| 命令                                          | 默认传输 | 行为                                                                                                                                                         |
| ------------------------------------------------ | ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `recruiter filters [filter-type] [query]`        | `cookies`         | 没有参数返回记录的26控制目录，不联系LinkedIn；命名值使用映射的方面/类型ahead路由。WAB读取渲染的控件 |
| `recruiter search [keywords]`                    | `cookies`         | 有界候选人卡片，有效过滤器和连续元数据                                                                                             |
| `recruiter profile <candidate-ref...>`           | `cookies`         | 完全公开的个人资料部分和单独职位描述（如果可用）                                                                                |
| `recruiter saved-searches`                       | `cookies`         | 列出原生记录，项目/所有者身份和警报状态，而无需打开搜索                                                                         |
| `recruiter save-search <name> [keywords]`        | `wab`             | WAB填充原生表单，提交一次并验证持久性；警报默认关闭                                                                             |
| `recruiter open-saved-search <id-or-exact-name>` | `wab`             | 恢复项目范围搜索；返回保存记录加上有界搜索结果                                                                       |

`--via cookies` 意味着经过身份验证的内部Recruiter API；`--via wab` 意味着实际的浏览器导航、渲染的DOM和可信输入。两者都不执行身份验证探测、自动会话刷新、重试或传输回退。初始cookie搜索HTTP 500通过纠正原生参数序列化修复；随后的有界搜索通过。匹配原生Recruiter应用上下文还恢复了请求的个人资料技能。缺少请求的部分仍然产生部分结果。不要通过静默更改传输来绕过错误。

搜索接受可重复的 `--filter TYPE=VALUE`，`--exclude-filter TYPE=VALUE`，`--range-filter TYPE=MIN:MAX`，`--toggle TYPE[=true|false]`，`--filters-json <JSON-or-local-file>`，和捕获的 `--search-url`，包括原生项目/保存搜索GET URL。Cookie原生URL重放保留项目/所有者上下文，目前拒绝过滤器覆盖。结构化子句支持 `operator: "require"`，范围和原始观察值。WAB拒绝未映射的原始字段，然后导航。`--interactive --via wab` 暂停操作员配置实际搜索；它不会保存原生搜索。目录覆盖尚未意味着每个依赖项或运算符都有实时平等性。

`--count` 是每页逻辑结果，不是总数限制。默认值是10个结果 × 10页；`--all` 允许最多100页，除非提供 `--max-pages`。为预期的小操作指定显式的页限制。Recruiter的物理UI页面即使返回结果较少时也包含25个结果。`--delay` 设置每个cookie请求之间的最小间隔，包括准备性收集/项目/类型ahead读取，以及WAB交互之前。它永远不会降低现有的cookie速率限制。`--max-pages` 也限制物理WAB页面，因此一个遥远的 `--start` 可能在其到达之前失败。`--details full` 添加个人资料读取，`--max-profiles` 默认为250。`--override-max-profiles` 允许请求的最大值超过250；请求的 `--max-profiles` 仍然限制访问，并且平台错误和请求节流仍然受执行。这些值是Wonda控制，不是LinkedIn批准的允许。

仅使用捕获的透明候选人引用或实际的 `/talent/profile/...` 链接。公开的 `/in/...` URL 仅在暴露时发出，并具有可追溯性。候选人输出保留当前/过去的职位、多行描述、教育、技能、可选部分和每部分状态，如完整、部分、不可用和未观察。缺失的字段不是空的完整部分。在页面/读取失败时，有用的结果保留在stdout上，带有 `partial`/`errors` 和非零退出。`--csv` 生成Wonda CSV，保留结构化历史记录在引号JSON单元格中；不需要LinkedIn原生导出。CSV `partial` 包括候选人和结果失败；`extraction` 保留候选人特定状态，而 `result_partial` 和JSON `result_errors` 保留每行的整体结果。`record_type=candidate` 识别候选人行；一个空的失败结果发出一个 `record_type=result` 行，没有候选人身份。公式类CSV文本在电子表格导入时接收一个引号开头的制表符；该制表符保留在CSV数据中，而JSON保留原始文本。`--no-cache` 跳过个人资料缓存重用。部分个人资料、显式凭证和未知/过期的席位上下文绕过可重用缓存条目。席位/合同命名空间来自现有的本地Recruiter会话cookie，无需身份验证请求；更改的上下文不会缓存。独立的WAB缓存重用已通过正常CLI。

原生项目标志是 `--recruiter-project`（WAB的精确名称，cookies的ID或精确名称）和 `--new-recruiter-project`；全局 `--project` 仍然意味着Wonda项目上下文。Cookie项目查找优先考虑精确名称，包括数字名称；一个完整的捕获项目URN明确选择ID。警报默认关闭。WAB保存/打开观察到在预期的真实记录上。一个未验证的保存结果不得自动重试。`viewedMarkerChanged:null` 意味着原生GET标记效果未知。永远不要在真实账户中制造一次性记录或容量失败以验证它们。

**LinkedIn InMail 信用余额：** `wonda linkedin inmail-credits` 是只读的，并从 Sales Navigator 信用授予端点通过 cookie 传输返回座位的剩余 InMail 信用余额作为 `remaining`（以及授予类型和 ID）。它从不发送任何内容，也从不消耗信用；在 `wonda linkedin inmail --spend-credit` 之前使用它来计划。它需要账户上有一个活动的 Sales Navigator 座位；旗舰-高级账户无法以这种方式读取其余额。

**LinkedIn 公共资料页丰富：** `wonda linkedin enrich <profile-url-or-vanity...>` 默认为 `--via cookies`，使用本地登录的资料页逐个读取路径，重用 `_artifacts/linkedin-cache`，在缺失之间添加抖动，在 429 风格的速率限制信号上中止，并在直接运行时拒绝超过 25 个输入。`linkedin_enrich` 工具（本地 MCP 和双行动路由）将批量 `targets` 调用限制在 10 个：该路径共享更紧密的调用端截止日期（Go API 客户端的 300 秒请求取消，其他同步 HTTP 调用者），25 个资料的运行可能会超过。`--via cookies` 和 `--via wab` 都在返回的资料中包含每个资料的教育（学校、学位、fieldOfStudy、startYear、endYear）和派生的 `yearsOfExperience`，但教育获取是尽力而为的：该可选请求的临时失败（任何速率限制以外的）仍然返回一个成功的丰富，没有教育字段，该结果按原样缓存。缓存命中按原样提供，由共享此缓存而不获取教育的命令（`enrich-engagers`、`search-posts` 作者资料）、在此更改之前的 `enrich` 或先前的尽力而为的缺失写入的条目缺乏教育，因此当教育重要时要传递 `--force-refresh`。`enrich-engagers` 不请求教育，因此其每个参与者的资料读取计数保持不变。使用 `--via public` 通过 `POST /api/v1/scrape/linkedin-profiles` 进行付费公共丰富，除非设置 `--no-wait`，否则轮询 `GET /api/v1/scrape/linkedin-profiles/{taskId}` 直到完成。使用 `wonda scrape cancel <taskId>` 取消正在运行的付费抓取。公共模式支持 `--force-refresh`、`--timeout 10m`、`--idempotency-key` 和 `--output json|table`。单个资料的 `wonda linkedin profile --via public` 路径使用相同的付费路线，并还支持 `--force-refresh`、`--timeout` 和 `--idempotency-key`。

- `--via wab` 通过角色的 Wonda Automation Browser 会话运行相同的批量：每个资料读取都在登录的浏览器中执行（真实的指纹，没有 flat-store 陈旧）。相同的 25 输入上限、节拍、缓存和教育/yearsOfExperience 字段与 `--via cookies`。当批量跟随 Sales Navigator 导出或当 cookie 读取失败时，请优先使用它。

**LinkedIn 发送邀请跟踪：** `wonda linkedin sent-invitations` 是只读的，默认为 `--via cookies`。它列出了活动的待处理外出邀请，并且默认情况下，它会与本地 WAB 连接审计进行协调，以将已审计的目标标记为 `accepted`、`pending`、`withdrawn` 或 `unknown`；传递 `--reconcile=false` 以获取原始分页待处理列表或传递 `--no-connection-check` 以跳过每个目标的连接状态读取。`--via wab` 将相同的读取路由到账户角色。LinkedIn 的发送列表 Voyager 端点目前正在波动，因此该命令尝试可页面的 Voyager 变体，然后回退到只读的发送邀请管理页面。结果始终报告 `complete`、`fetched`、`knownTotal` 和 `source`。`complete` 只有当库存被证明完整时才为真；`fetched` 计数返回的不同待处理行；`knownTotal` 是 LinkedIn 广告的总数，或者在缺失或不一致时为 null；`source` 是 `voyager` 或 `html`。HTML 回退结果还报告 `fetchCap`，即渲染的 HTML 行上限；当未使用 HTML 时会省略它。部分库存返回有用的行，`complete: false`。从部分库存中缺少的已审计目标在连接检查禁用或失败时变为 `unknown`，永远不会推断撤回。`acceptRate` 排除未知行。`--via public` 和 `--via api` 不受支持。

**LinkedIn 连接状态批量：** `wonda linkedin connection-status <inputs...>` 对原始输入顺序中的每个输入返回一个结果。每一行都包括原始的 `input`。查找失败被标记为 `status: "error"` 和 `error` 而不是被丢弃。一个输入保持对象形状；多个输入保持数组形状。单个查找失败在 stdout 上添加标记的对象，同时保留现有的 stderr 错误和非零退出。

**参与者丰富：** `wonda linkedin enrich-engagers --activity-id <id>` 抓取反应器（并通过 `--comments` 可选地抓取评论者），然后获取每个参与者的资料 + 当前雇主 + 公司页面，并发出一个按虚荣键值组织的 JSON 文档，每个参与者有 `profile` 和 `currentEmployer`（行业、员工人数、总部、描述、员工人数）块。使用 `--company-detail=false` 跳过公司页面查找，并仅保留内联雇主身份（`name`、`urn`、`universalName`）。使用 `--max-profiles N` 来限制批量（默认 250，除非设置 `--override-max-profiles`，否则硬上限为 250）和 `--out file.json` 将其写入磁盘。`--profile-source cookies|public` 仅控制每个资料的详细丰富；参与者收集仍然使用登录的 LinkedIn 访问权限。

对于帖子参与者的 ICP 资格，运行 `wonda skill get linkedin-icp-qualify`。

### Instagram

一个一流的平台，通过 `--via` 选择三个传输方式：

- `--via api` — 通过您连接的 OAuth 账户（`--connection`）的官方 Graph API。服务条款安全，用于发布。
- `--via cookies` — 通过本地 cookie `--account` 的私人移动 API。用于读取（保存的帖子、评论）。
- `--via wab` — 通过账户的 Wonda Automation Browser 角色。用于 `comment` 写入（驱动 Reel 的内联评论合成器，使用真实的浏览器指纹，与 LinkedIn 评论相同的隐蔽路径）。

传输是每个操作能力的：`saved` 和 `comments` 仅限于 cookie（没有 Graph 端点），`post`/`carousel` 仅限于 api，`comment` 仅限于 wab。两个身份是不同的：`--account`/`--sessionid` = 本地 cookie 身份；`--connection` = OAuth `instagram_account` UUID。对于 `--via wab`，角色自动从 `--account` 派生（或者直接传递 `--persona`）；WAB 在启动时将绑定的账户的 `sessionid`（+ `ds_user_id`）注入 Chromium cookie 罐。

> ⚠️ **与其他相同的反欺诈注意事项：不要探测刚粘贴的 cookie。** 在新的 `sessionid` 上的第一个请求应该是您想要的操作。Instagram 标记来自新 IP/进程的突发活动，在刚获得的会话上。

```bash
# 认证设置 — 本地 cookie 身份（运行 `wonda instagram auth --help` 获取详细信息）
wonda instagram auth set --sessionid <value>                # 仅 sessionid cookie（最简单）
wonda instagram auth set --cookies "$(pbpaste)"             # 完整的 DevTools cookie：头部（还捕获 ds_user_id）
wonda instagram auth set --account <name> --sessionid <v>   # 多个账户
wonda instagram auth set --account <name> --sessionid <v> --persona <persona>  # 也绑定到 WAB 角色

# 读取（cookies）
wonda instagram saved                                       # 您保存的帖子（--all 以遍历所有页面）
wonda instagram saved --jq '.posts[] | {authorHandle, url}' # 从结果中提取项目字段
wonda instagram comments https://instagram.com/reel/<code>/ # 帖子/Reel 的评论（--all 以遍历所有页面）
wonda instagram comments <code> --jq '.comments[] | {authorHandle, text}'  # 简短代码也有效

# 发布（--via api，默认 — 通过您连接的账户的官方 Graph API）
wonda instagram post --media <media-id> --caption "Hello"   # 单个图像/Reel
wonda instagram post --media <id> --connection <ig-uuid>    # 明确选择连接的账户
wonda instagram carousel --media <id1> --media <id2>        # 2-10 图像轮播

# 在 Reel 上评论（--via wab 仅限 — 驱动 WAB 中的内联合成器）
wonda instagram comment https://instagram.com/reel/<code>/ "Great reel!" --persona my-account
wonda instagram comment <code> "Love this" --persona my-account   # 简短代码也有效

# Feed-engage（--via wab 仅限：滚动主页并喜欢目标作者的发帖）
wonda instagram feed-engage --authors "a,b" --duration 5m --persona my-account  # 滚动 Feed 并喜欢这些作者的发帖（wab 仅限）
```

`--account` 选择 `~/.wonda/instagram-cookies/<account>.json` 下方的 cookie 文件。对于 `saved`，轮播会为每个子贡献媒体 URL（视频优先于图像用于每个项目的 URL）；分页使用 `max_id` 光标（`--cursor`，`--all`，`--max-pages`，`--delay <ms>`）。`comments` 接受 `/p/<code>/` 或 `/reel/<code>/` URL（或简短代码），在本地解码为数字媒体 ID，然后分页相同的 `max_id` 光标；结果包含每个评论的 `id`、`text`、`authorHandle`、`authorName`、`createdAt`、`likeCount`、`replyCount` 以及父媒体的 `commentCount`。对于发布，`wonda instagram post --via api` 和 `wonda publish instagram` 共享相同的 Graph-API 路径。`comment`（写入）接受 `/reel/<code>/` 或 `/p/<code>/` URL（或简短代码）加上文本，并且是 wab 仅限：如果需要，它会自动启动角色的 WAB，在合成器中键入，提交，并将 `comment` 审计行写入 `~/.wonda/wab/audit.jsonl`（失败会触发 `wab_action_failed` 远程指标并丢弃失败包）。

### Reddit

Reddit 的传输是针对每个命令类型的固定，因此 `--via` 主要不是您在这里选择：

- **读取**（搜索、子版块、Feed、用户、用户发帖、用户评论、帖子、趋势、主页、保存）直接通过 Chrome 指纹的 Go HTTP 客户端运行（快速，~700ms p50）。仅 cookie。`--via wab` 不可用于读取，并且会出错。
- **写入**（投票、评论、订阅、保存、取消保存、删除，以及子版块 `submit`）通过账户的 Wonda Automation Browser 分发，因此 shreddit GraphQL 变化携带一个真实浏览器的信号。仅 WAB。`--via cookies` 在这些情况下会出错。
- **提交到资料页自我发帖**（`u_<handle>` / `u/<handle>`）**或链接发帖**通过 tls-client（cookie）仅限。`--via wab` 不适用于这些（没有 DOM 提交 URL），因此 `--dry-run`（DOM 仅限）也不适用于它们。

`--account` 选择 `~/.wonda/reddit-cookies/` 下方的 cookie 文件（对于写入，选择账户的自动派生角色）。您在这里不传递角色。

> ⚠️ **对刚粘贴的 cookie 的反欺诈注意事项。** `wonda reddit auth check` 是安全的（它仅在本地向解码 JWT exp），但您在新 cookie 上发动的第一个读取或写入会从您的 IP / 进程击中 Reddit 的 API。如果这些 cookie 最后在别处使用（不同的机器，不同的国家），Reddit 的反欺诈会触发会话窃取启发式，并可能强制注销 cookie。模式：粘贴 cookie，直接转到用户想要的操作。永远不要先进行“让我检查一下是否正常”的往返操作。

```bash
# 认证设置（运行 `wonda reddit auth --help` 获取详细信息）
wonda reddit auth set --cookies "$(pbpaste)"                         # 粘贴完整的 DevTools cookie：头部
wonda reddit auth set --account <name>-1 --cookies "$(pbpaste)"      # 多个账户
wonda reddit auth set --account <name>-1 --from-keychain             # 选择：从浏览器密钥链读取
wonda reddit auth check

# 读取（直接 tls-client，--account 选择登录视图的会话）
wonda reddit search "AI video" --sort top --time week   # 搜索帖子（排序：相关性，热门，顶部，新，评论）
wonda reddit subreddit marketing                        # 子版块信息
wonda reddit rules marketing                            # 子版块发帖规则（+ 全站规则）
wonda reddit feed marketing --sort hot                  # 子版块帖子（排序：热门，新，顶部，上升）
wonda reddit comments marketing                         # 最新评论跨子版块（寻找回复机会）
wonda reddit user spez                                  # 用户资料
wonda reddit user-posts spez --sort top                 # 用户的帖子
wonda reddit user-comments spez                         # 用户的评论
wonda reddit post <id-or-url> -n 50                     # 带评论的帖子
wonda reddit analytics <id-or-url>                      # 所有者 viewCount 加上公共分数，upvoteRatio，commentCount
wonda reddit trending --sort hot                        # 流行/趋势帖子
wonda reddit home --sort best                           # 您的主页（需要认证）
wonda reddit saved                                      # 您保存的帖子 + 评论（需要认证；--all 以遍历所有页面）
wonda reddit whoami                                     # 您自己的账户身份：用户名 + id + karma（需要认证；别名：me）
wonda reddit inbox                                      # 经典通知：回复您的帖子/评论，提及，旧私信（需要认证）
wonda reddit inbox --unread                             # 仅未读；--type mentions 仅提及

# 写入（WAB 仅限通过账户的角色；--account 选择身份）
wonda reddit submit marketing --title "Great tool" --text "Check this..." --account <name>-1   # 子版块文本帖子（DOM）
wonda reddit submit marketing --title "..." --text "..." --flair "Discussion" --account <name>-1 # 带有流光的子版块文本帖子
wonda reddit submit u_<your-handle> --title "..." --text "..." --account <name>-1               # 资料页自我发帖（tls-client / cookie 仅限）
wonda reddit submit marketing --title "..." --url "https://..." --account <name>-1              # 链接发帖（tls-client / cookie 仅限）
wonda reddit comment t3_<post-id> --text "Nice post!" --account <name>-1
wonda reddit comment t1_<comment-id> --text "..." --post-id t3_<post-id> --account <name>-1 # 嵌套回复（需要父帖子 id）
wonda reddit vote <fullname> --up --account <name>-1     # 上投（--down，--unvote）
wonda reddit vote t1_<comment-id> --up --post-id t3_<post-id> --account <name>-1
wonda reddit subscribe marketing --account <name>-1      # 订阅（--unsub 以取消订阅）
wonda reddit save <fullname> --account <name>-1          # 保存帖子或评论（--post-id 对于 t1_*）
wonda reddit unsave <fullname> --account <name>-1
wonda reddit delete <fullname> --account <name>-1        # 删除您自己的帖子或评论
wonda reddit feed-engage --authors "a,b" --duration 5m   # 滚动 Feed 并上投这些作者的帖子（wab 仅限）
wonda reddit feed-engage --keywords "ai video,ugc ads" --subreddits SaaS,marketing --reply --max-reply 3  # 监控范围搜索，门控相关性，通过 WAB 评论

# 账户创建（WAB 仅限，标记：redditAccountCreationEnabled）
wonda reddit signup --persona <name> --random                                       # 端到端创建一个全新的账户
wonda reddit signup --persona <name> --email <addr> --username <handle> --password <pw>
wonda reddit signup --persona <name> --resume credentials                           # 在手动步骤后恢复
```

`wonda reddit user` 在用户在公共 About 文本中发布明确联系详情时包括加性的 `emails` 和 `links` 字段。这些字段是只读的，并且等同于手动读取资料。不涉及推断电子邮件、丰富数据、存储或 DOM 抓取。

在子版块 `评论` 或 `提交` 中添加 `--dry-run` 以在 composer 中输入内容但不点击发布（用于审阅）。它是仅基于 DOM 的，因此不适用于个人主页自发布或链接发布。对于子版块提交，在 composer 中通过传递 `--flair "<标签>"` 来选择帖子样式。样式标签不区分大小写，并匹配规范化空白，首先通过精确标签匹配，然后通过包含回退匹配。如果一个子版块需要样式且被省略，或者请求的样式不存在，命令将使用可用的样式标签失败。`--flair` 不支持个人主页自发布或 `--url` 链接发布。

`wonda reddit signup` 提供一个全新的 Reddit 账户：它创建一个一次性邮箱（或使用 `--email`），驱动 5 阶段注册表单（电子邮件、电子邮件验证码、用户名加密码、年龄、兴趣）在一个全屏 WAB 窗口中，从收件箱主题行获取验证码，然后绑定角色并同步 cookie，以便 reddit 通过新账户读写路由。由 `redditAccountCreationEnabled` 标志控制（服务器预检评估：`GET /reddit/signup/enabled`）。首先绑定移动或住宅代理到角色上（`wonda wab config set <角色> proxy_url socks5://...`）：Reddit 会对在数据中心 IP 上创建的账户进行影子封禁。如果无法定位某个字段，流程将暂停并停留在该屏幕；手动完成，然后重新运行 `--resume <步骤>`。成功后，它将打印 `{用户名,电子邮件,密码,角色}` 以及一个准备粘贴的 `op item create` 块，用于“Reddit 登录”保险库。

支持分页命令：`-n <数量>`、`--after <游标>`、`--all`、`--max-pages`、`--delay <ms>`。

**Feed-engage 作者模式** (`wonda {linkedin,x,reddit,instagram} feed-engage`)：像人类一样滚动主页源，并仅与从目标作者滚动过的帖子互动。在 Reddit 上，互动是一个点赞，在其他平台上是一个喜欢。它是仅 WAB 的（它驱动实时浏览器滚动并通过账户的角色进行点击，因此没有 cookie 路径），并且是机会主义的：它永远不会打开个人资料或搜索，只是沿着源滚动并在目标帖子出现时采取行动。通过 `--authors "alice,bob"`（逗号分隔的 handles/vanities/usernames，前导 `@` 和 `u/` 被移除）或 `--authors-file <路径>`（每行一个作者，仅本地使用）传递目标。`--duration` 限制墙时钟浏览时间（例如 `5m`、`90s`、默认 `2m`），`--max-engage` 限制成功点赞/点赞的数量（默认 `8`）；哪个限制先达到将停止运行。节奏是人类的（减缓滚动、随机停留、抖动光标运动），因此让它运行完整持续时间，而不是期望立即结果。

LinkedIn 作者模式还可以选择通过 `--engage-comments` 进行评论反应：默认情况下，它仅对来自 `--authors` 的评论进行反应，`--engage-comments-from any` 包括所有可见评论，`--max-comment-engage` 限制每个互动帖子的评论反应数量（默认 `3`）。

**LinkedIn 互动评论者** (`wonda linkedin engage-commenters`)：读取 LinkedIn 帖子的评论者，然后按顺序运行针对每个评论者的选定操作：`like`、`reply`、`connect`。通过 `--post <activity-id|urn|url>` 传递帖子。`--actions` 接受 `like,reply,connect` 并默认为 `like`；`--reply-text` 在选择 `reply` 时是必需的；`--connect-note` 是可选的；`--max-commenters` 默认为 `25`；`--duration` 默认为 `3m`；`--dry-run` 解析目标并打开控制/composer 而不提交写入。访问层：付费/WAB。传输：评论者读取使用已建立的 LinkedIn DOM 评论路径；每个写入使用 WAB DOM 基本操作。

**Feed-engage 监控模式** (`wonda {linkedin,x,reddit} feed-engage --keywords ...`)：运行一次有边界的键词/意图监控传递，使用 `/text/generate` 对未看到的候选者进行评分，并可选地使用 `/text/generate` 生成角色回复。`--keywords` 启用监控模式，并与 `--authors` 和 `--authors-file` 互斥。Reddit 支持 `--subreddits SaaS,marketing` 来限定搜索范围。没有 `--reply`，监控模式是只读的，并打印候选者及相关性裁决。使用 `--reply --dry-run` 时，它生成回复文本但什么也不发布并保持账本不变。使用 `--reply` 时，它仅通过 DOM/WAB 写入器发布：Reddit 评论 composer、X 回复 composer 和 LinkedIn 评论 composer。读取使用可用的 cookies/tls-client：Reddit 搜索和 X 搜索使用平台客户端；LinkedIn 内容搜索使用现有的 WAB DOM `search-posts` 流，因为 LinkedIn 内容搜索不通过 cookie API 可靠。安全控制：`--max-scan`（默认 50）、`--relevance-threshold`（默认 0.7）、`--max-reply`（默认 3）、`--per-day-cap`（默认 8），以及位于 `~/.wonda/reply-ledger/` 下的持久化去重账本。生成的公共回复会进行后处理以移除破折号。监控模式不支持 Instagram。

### 跨平台 DM 覆盖

| 平台     | 读取收件箱 | 读取对话 | 发送现有线程 | 开始或冷 DM                |
| -------- | ---------- | -------- | ------------ | -------------------------- |
| LinkedIn | 是         | 是       | 是           | 是，通过个人资料/消息流    |
| Reddit   | 是         | 是       | 是           | 是，通过 `wonda reddit chat start` |
| X        | 是         | 是       | 是           | 是，通过 `wonda x dm start` |

### Reddit 聊天 / DM

通过 WAB 进行直接消息传递。聊天使用登录的 Reddit 浏览器会话，并可作为 `--via wab` 的一流双操作使用。没有单独的聊天令牌。

```bash
# 读取
wonda reddit chat inbox                                  # 列出 DM 对话及其最新消息
wonda reddit chat messages <房间 ID> -n 50               # 从一个房间获取消息

# 写入
wonda reddit chat start <用户名> --text "嘿！"         # 通过用户名开始（或重用）与用户的 DM（不需要房间 ID）
wonda reddit chat send <房间 ID> --text "嘿！"           # 向现有房间发送 DM（模拟浏览器输入行为）

# 管理
wonda reddit chat accept-all                             # 接受所有待处理的聊天请求
```

**重要提示**：将 DM 发送速率限制为每天 15-20 条，并使用不同的文本以避免检测。`send` 命令驱动浏览器 composer 并验证渲染的消息。

### 云数字孪生 (`wonda twin`)

管理托管在移动代理后面的云端社交角色。会话是服务器端的；计划驱动定期任务（保存内容同步、互动、代理运行）在 cron 上运行。

**交互式（可观察）与无头：了解你所在的界面。** 云孪生以相同的方式运行相同的 antidetect Chromium，但只有其中一些会流式传输一个你可以（或用户）观看并点击的实时屏幕：

- **可观察、交互式界面（将实时云浏览器流式传输到你在本地 WAB 或任何浏览器中打开的 `viewerUrl`）：** `wonda twin login`、`wonda twin view`、`wonda twin signup` 和 `wonda twin attach`。每当需要人类看到并驱动云浏览器时使用这些：登录、重新认证、创建全新账户或解决任何需要人类触摸的问题。`login`/`view`/`signup` 启动一个全新运行并获取孪生的个人资料租用；`attach` 不同——它通过 `<运行 ID>`（来自 `wonda twin runs`）钩接到一个已经运行的运行，并且永远不会获取租用，因此操作员可以按需观察（或控制）任何实时运行——自动驾驶运行、计划触发运行、`run-now` 命令——而不仅是一个他们刚刚启动的运行。一个验证码（或任何升级挑战）只能在一个可观察界面上解决。你不能为用户输入凭证或解决验证码；将 `viewerUrl` 交给他们手动完成，然后重新检查 `wonda twin login-status` / `health` / `liveness`。
- **无头界面（无屏幕、无观察者、无人值守）：** `wonda twin run-now`、计划、`wonda twin login-status`、`wonda twin seed-from-cookies` 和每个使用 `--engine cloud` 运行的平台操作。这些在代理后面运行，无人观察。如果一个遇到验证码或登录墙无法在本地解决，运行将失败（获取其 `wonda twin artifact <运行 ID>` 截图以查看原因），或者——在它仍然活跃时——你 `wonda twin attach <运行 ID> --control --open` 跳入其中并自行驱动它，然后让它继续。
- **要控制一个实时运行，使用 `wonda twin attach <运行 ID> --control`。** 没有 `wonda twin control` 动词；对任意实时运行的可驱动控制通过 `attach --control`（或，对于你启动的视图，`wonda twin view`）实现。`attach` 而没有 `--control` 是只读的观察者。
- **观察/截图流式传输的观察者（代理）：使用 WAB，永远不要使用裸 Playwright 或无头-Chromium 脚本。** `login`/`view`/`signup` 将观察者作为一个标签在本地 WAB 中打开；这个标签就是观察表面，所以 `wonda wab show <角色>` 显示窗口，`wonda wab screenshot <角色>` 捕获 PNG 而不显示它。对于只读的 `attach` 捕获，省略 `--control` 和 `--open`，然后运行 `wonda wab screenshot <viewerUrl> --output run.png --wait-until domcontentloaded --wait-for '#screen[width][height]'`。`attach` 观察者仅在第一个流式传输的图像加载到画布后，才向 `#screen` 添加 `width` 和 `height` 属性，所以这等待真实的帧内容而不是仅仅等待观察者外壳或空闲网络。经纪人将帧分发到多个只读观察者，所以这个截图可以与其他观察者并行运行。控制是单胜者：如果多个控制器角色观察者连接，第一个保持控制，后来的被降级为只读。在构建任何观察者之前，首先确认运行实际上正在流式传输（`wonda twin liveness <角色>` → `live:true`）。

`wonda twin login-automated` 不是一个无头快乐路径。该路线永远不会自动完成登录；它始终会生成流式传输登录回退并返回 `{ status: "needs_human", viewerUrl }`。将其视为“打开这个 `viewerUrl` 并手动登录”，与 `twin login` 相同。

两个导致错误“正在运行 / 已登录”报告的陷阱：

- **`--engine cloud` 停靠一个持有约 15 分钟忙碌租用的热控制会话。** 在云操作后，孪生将保持“忙碌”状态，直到租用过期，所以接下来的 `twin login`/`view`/`signup`（或另一个 `--engine cloud` 操作）可以 409 为忙碌。这是预期的热会话行为，不是错误；等待它过期或 `wonda twin stop <角色>`。
- **观察者中的“您现在已登录”面板是粘性的。** 它确认在该会话中检测到登录；它并不意味着此时有实时流打开。对于“这一刻是否有实时交互流打开”使用 `wonda twin liveness <角色>`（在标签关闭后约 30 秒变为 false）；对于运行状态使用 `wonda twin runs` / `wonda twin health`。永远不要从粘性面板推断“仍在运行 / 仍在观察”。

MCP 孪生界面将工具标记为“始终允许”和“需要批准”。使用 `run_campaign` 和 `schedule_loop` 进行一审批自动驾驶循环；使用每个动词的平台工具进行监督操作。

Claude 网页和 Cowork 用户可以从 https://wonda.sh/docs/connect-claude 将云孪生连接为自定义远程 MCP 连接器。

```bash
# 会话
wonda twin list                                          # 列出孪生会话
wonda twin show <persona>                                # 显示单个会话
wonda twin provision <persona> --region GB               # 创建 (标志：--provenance, --spend-cap <microdollars>, --allow <cmd> (可重复))
                                                         # --max-writes-per-hour <N>: 在软限制之前每小时的平台最大写入量 (0/未设置 = 无限制)
                                                         # --alert-webhook-url <url> + --alert-webhook-secret <secret>: HMAC签名的主管警报，在 needs_auth / 连续失败时触发 (secret 是只写权限)
wonda twin update <persona> --spend-cap <microdollars>   # 修改限制 + 提前提供警报挂钩，无需重新创建 (标志：--max-writes-per-hour <N>, --alert-webhook-url <url>, --alert-webhook-secret <secret>)
wonda twin pause <persona>                               # 暂停会话
wonda twin resume <persona>                              # 恢复暂停的会话
wonda twin needs-auth <persona>                          # 标记会话需要重新认证
wonda twin needs-auth-view <persona> --platform x        # 标记 needs_auth，然后铸造一个真实的流式登录 (不是只读视图)，并在本地 WAB 的专用选项卡中打开它，与 MCP 工具执行的单次重新认证流程相同。登录重新认证孪生并恢复其活动状态。打印查看器 URL (在 <web-base>/twin-login.html 上提供，令牌在 URL 片段中)，以便您也可以在任何浏览器中打开它。登录由人工控制 (您不能为它们输入凭证)；一次只能查看一个孪生 (按顺序打开)。 (--platform <x|linkedin|reddit|instagram>, --web-base 默认 https://wonda.sh)
wonda twin recover <persona>                             # 清除活动关键安全信号 (验证码 / 异常活动 / 账户限制) 在您在浏览器中解决它之后。这些关键信号不会更改孪生状态，因此安全门会硬阻止具有 persona，直到您清除它；此应用程序会附加一个 '已恢复' 标记，门会读取它以停止将关键信号视为活动状态。安全检查点 / needs_auth 通过重新登录 (wonda twin login) 而不是此方法清除，不是这个。-> { recovered, clearedSignalType, persona }
wonda twin login <persona> --platform instagram          # 在本地 WAB 的专用选项卡中打开一个云生成的流式登录 (云登录看起来像我们的反检测浏览器，只是在云上；您其他选项卡中的现有 WAB 会话保持不变)。可见地生成 persona 的 WAB 并打开查看器在 <web-base>/twin-login.html (令牌在 URL 片段中)；也打印查看器 URL，以便您可以在任何浏览器中打开它。登录时流停止，Wonda "您已登录" 确认替换它 (平台源隐藏，因为您正在登录)。无计量。 (--platform <x|linkedin|reddit|instagram>, --web-base 默认 https://wonda.sh)
wonda twin signup <persona> --platform reddit            # 在专用 WAB 选项卡中打开一个云生成的账户注册，并在实时流中手动创建账户 (3-A 全程参与：您输入整个流程，包括任何验证码/验证)。自动创建一个新 persona；注册拒绝在已经活动/needs-auth 的孪生上运行 (使用 `twin login` 重新认证)。它仅在您按下完成操作并且云确认新账户 (设置会话 cookie，没有未解决的挑战) 时完成；创建的句柄然后绑定到孪生，并且配置文件快照变为活动状态。无计量。 (--platform <x|linkedin|reddit|instagram>, --web-base 默认 https://wonda.sh)
wonda twin signup <persona> --automated                  # Reddit 仅限：云自动驱动注册表单 (邮箱、发送的代码、用户名、密码) 上到出生日期步骤，然后暂停并在流中显示一个恢复横幅。您手动输入出生日期 (自动化难以处理 Reddit 的分段生日小部件)，然后点击恢复，云完成剩余步骤并保存。添加 --dob YYYY-MM-DD 以预填年龄步骤 (留下只有挑战/入职)。需要 redditAccountCreationEnabled + emailServerApiEnabled 以创建账户。平台固定为 reddit。
wonda twin attach <run-id>                               # 将一个实时查看器附加到已经运行的孪生运行 (run id 来自 `wonda twin runs`)。与登录/查看/注册不同，它不会启动运行或获取配置文件租赁：它在实时运行上注册只读存在并打印一个可在浏览器中打开的查看器 URL，以便操作员可以按需观看任何实时运行 (自动驾驶 / 安排 / 立即运行)。添加 --open 在默认浏览器中启动查看器。添加 --control 作为驱动能力的控制器附加，而不是只读观察者 (点击/输入到实时运行)。404 如果运行未知/不是您的；run_not_live 如果它不是实时的；run_not_attachable 如果它是无法流式传输的批处理作业。无计量；需要高级 (云孪生)。
wonda twin sync-cookies <persona> --run-id <run-id> --platform linkedin # 将一个平台的 cookie 从实时云孪生浏览器同步到该运行者的云仅存储。平台必须与实时查看器匹配。请求 session:sync-cookies 并且永远不会打印或下载 cookie 值。刷新的存储立即可用于实时运行者；可写视图将其带入其下一个配置文件快照，而只读视图永远不会持久化运行者更改，并且会被实时服务拒绝。
wonda twin seed-from-cookies <persona> --platform x      # 从之前使用 /social-tokens 存储的浏览器 cookie 开始云种子作业。运行输出包含每个平台的登录状态结果。
wonda twin login-automated <persona> --platform x        # 不是无头快速路径：该路由永远不会自动完成登录。它始终铸造一个流式登录回退并标记孪生 needs_auth，返回 { status: needs_human, viewerUrl } (viewUrl 是自定义查看器的原始 WebSocket)。在浏览器中打开 viewerUrl 以手动完成登录 (与 `twin login` 相同)，然后重新检查 login-status。
wonda twin login-status <persona> --platform x           # 从热控会话读取-only 建议签名登录检查。当控制浏览器仍在预热时，它返回 { status: "warming", loggedIn: false, lastChecked: null, retryAfterMs } (HTTP 202, Retry-After 标头)，CLI 在 stderr 打印重试提示；完成的探测返回 { status: "checked", loggedIn, lastChecked } (HTTP 200)。在预热延迟后重试以获得有意义的结果。
wonda twin sync-profile <persona> --cookies-only         # 将本地 WAB / 本地 cookie 罐提升到云孪生配置文件。强制在运行该 persona 时首先同步本地 WAB cookie。使用 --platform <x|linkedin|reddit|instagram> 限制范围，--dry-run 以检查，--include-storage 也上传 Chromium 存储太。
wonda twin export-cookies <persona> --platform linkedin  # 将当前云孪生生成的清理后的 .seeded-cookies 导入本地 ~/.wonda/<platform>-cookies/<account>.json。除非 --force；--dry-run 显示计划写入；--account-label 覆盖本地标签；--inject-running 显式地将导入的 cookie 推送到已经运行的绑定 WAB persona。

# 分享 (仅所有者：授予的孪生永远不会重新分享授予它们的孪生)
wonda twin share add <persona> --email <email>           # 与另一个 Wonda 账户共享云孪生 (他们必须已经有一个；未知电子邮件 -> 404 "请他们先注册")。--email 或 --org 其中一个必须存在。--role operator (默认) | read-only。默认情况下通过电子邮件发送；--no-notify 沉默地授予。需要高级 (云孪生)。与自己分享 -> 400；现有的实时授予 -> 409。如果通知失败，授予仍然成功：响应包含 emailSent:false，CLI 在 stderr 警告，退出 0。
wonda twin share add <persona> --org <orgId> --role read-only   # 与组织的每个成员共享，而不是一个账户。--no-notify 在这里被拒绝 (一个组织共享没有人可以发送电子邮件)。
wonda twin share list <persona>                          # 此孪生与谁共享：共享 id、授予者电子邮件 (或组织)、角色、createdAt。仅所有者 (授予者会收到 403)。不是高级限制的，所以一个过期的所有者仍然可以审计访问。
wonda twin share rm <share-id>                           # 撤销共享 (id 来自 `twin share list`)。仅所有者；不是您的共享 -> 404 (永远不会泄露它存在)。不是高级限制的，所以一个过期的所有者总是可以切断他们授予的访问。

# 使用与他人共享的孪生：没有单独的界面。通过正常孪生/平台命令 (`wonda twin show <persona>`,
# `wonda twin run-now <persona>`, `linkedin ... --account <persona>`) 添加 persona 名称；服务器首先将裸 persona 解析为您自己的孪生，否则解析为实时授予。
#   - 角色 operator 驱动孪生 (登录、查看、run-now、操作)；read-only 仅读取元数据。
#   - 仅所有者路由即使在 operator 下也被拒绝：`twin export-cookies` 和重写警报挂钩 secret。
#   - 授予者永远不能驱动 home:local 孪生 (它存在于所有者的机器上)，只能 home:cloud。
#   - 如果两个不同的所有者与您共享相同的 persona 名称，请求会被拒绝为歧义，而不是猜测。请其中一个重命名。
#   - 双方都需要高级：孪生路由检查您的云孪生权限，云调度也检查所有者 (他们的账户为运行付费)。

# 计划
wonda twin schedule list --persona <persona>             # 列出计划 (--persona 可选)
wonda twin schedule add <persona> --cron "0 9 * * *" --kind saved_sync --name saved-posts-scrape   # 添加 (--kind: saved_sync|engage|agent; --command, --prompt, --mode deterministic|agent)
                                                         # --name <label>: 人类可读的计划标签 (例如 saved-posts-scrape) 用于列表/审计；可选
                                                         # --command 在服务器上对令牌化引用敏感，因此免费文本写入正文 (帖子、评论、DM 或 InMail) 作为单个参数保留。引用任何有空格的正文。
                                                         # 发布/评论/DM 计划应使用 --kind engage，以便它们计入写入速度信封。
                                                         # --jitter-window-seconds N: 在 cron 时间后 N 秒内随机看起来的一天的分钟内触发一次 (cron 标记窗口开始)；0/未设置 = 按照cron分钟精确触发
                                                         # --jitter-min-seconds A --jitter-max-seconds B: 在 cron 时间后 [A,B) 秒后确定性地触发。任何标志都会覆盖 --jitter-window-seconds；偏移量对于 (计划, 天) 是稳定的，所以重试保持相同的分钟。
                                                         # --timezone <IANA>: 在该区域 (例如 America/New_York) 中读取 cron (而不是 UTC)。在一个回退日，重复的本地时间仍然触发一次；在一个夏令时日，不存在的本地时间被跳过。
                                                         # --at <RFC3339>: 单次触发。在那一刻触发一次然后禁用自己。与 --cron 互斥 (传递恰好一个)。
                                                         # --starts-at <RFC3339> / --ends-at <RFC3339>: 激活窗口。在它之外调度器会跳过滴答而不消耗插槽，因此计划处于休眠状态并且不受影响。
                                                         # --output-webhook <url>: 将每个运行的捕获命令 stdout 交付到您的 HTTPS webhooks (有效载荷携带短 TTL 签名下载 URL)；--output-webhook-secret <s>: HMAC-SHA256 密钥通过 X-Wonda-Signature 标头签名正文
wonda twin schedule add <persona> --kind engage --cron "0 10,14,17 * * 1-5" --jitter-window-seconds 1200 --commands "linkedin feed-engage --authors 'alice,bob' --duration 5m"   # 云孪生上的重复 feed-engage
wonda twin schedule add <persona> --kind engage --cron "0 9 * * 1-5" --timezone America/New_York --jitter-min-seconds 300 --jitter-max-seconds 1800 --command "linkedin post 'morning thought' --via wab --account <persona>"   # 工作日 9am NEW YORK 时间，5-30min 的抖动
wonda twin schedule add <persona> --kind engage --at 2026-08-01T09:00:00Z --command "x tweet 'launch day' --via wab --account <persona>"   # 单次触发：触发一次，然后自动禁用
wonda twin schedule add <persona> --kind engage --cron "0 9 * * 1-5" --command "x tweet 'gm builders' --via wab --account <persona>"   # 计划发布，保留免费文本 argv
                                                         # 注意：--authors 与 --authors-file 内联一致 (逗号分隔，无空格)。--authors-file 仅限本地；云运行者没有文件系统的文件。
                                                         # 计划中的平台动词会针对孪生动作注册进行验证；即使孪生允许列表为空，未知的 LinkedIn/Reddit/X/Instagram 动词也会被拒绝。
wonda twin schedule enable <id>                          # 启用计划
wonda twin schedule disable <id>                         # 禁用计划
wonda twin schedule rm <id>                              # 删除计划

# 运行
wonda twin runs --persona <persona> --limit 20           # 最近运行。每个运行在失败运行捕获了诊断屏幕截图/包时都会携带 hasArtifact:true (使用 `wonda twin artifact` 获取)。
wonda twin run-now <persona> --command <cmd>             # 立即触发运行并捕获其结构化命令输出。写入命令超过每个身份动作限制返回结构化限制 429。--command 对令牌化引用敏感，因此引用有空格的免费文本正文：--command "linkedin send-message alice 'hi there :)' --via wab --account alice"
                                                         # 平台动词会针对孪生动作注册进行验证；非平台命令仍然通过正常允许列表行为传递。
                                                         # 媒体写入动词接受 Wonda 媒体 id 或孪生上的签名 URL：reddit submit --media <media-id>, x tweet/reply/quote --attach <media-id>, linkedin post --media <media-id>。运行者获取字节到 /tmp 并将本地文件路径传递给平台 CLI。
wonda twin run-action --persona <p> <platform> <action> --field key=value   # [弃用：优先使用 `<platform> <verb> --engine cloud`] 通过热托管控制会话运行一个注册验证的动作。仍然有效，因此正在运行的代理不会中断。如果冷，返回 { status: "warming", retryAfterMs }。使用 --payload @file.json 用于结构化负载。需要高级计划 (云孪生)。
wonda twin output <runId>                                # 通过 run-now 返回的孪生运行 id 或 twin runs 显示的运行时 runId 获取运行的捕获命令输出 (--url 仅打印短 TTL 签名下载 URL；新捕获保留私下 30 天)
wonda twin artifact <runId>                              # 打印失败运行的诊断屏幕截图 (image/png，内联打开) + 失败包 tar.zst，每行一个。404 如果运行没有捕获。需要高级计划 (云孪生)。

# SENSE 层 (只读 "在行动前询问" 探测；重用确切的决策 + 限制写入门强制执行)
wonda twin can-act --persona <p> [--action connect]      # 这个孪生现在会运行这个动词 (或任何写入，没有 --action) 吗？-> { canAct, reason, code, deferUntil, actionsRemaining }。读取/生成始终通过。
```

wonda twin actions --persona <p>                          # 每个操作的剩余限制 + 当天已消耗 + 7天滚动窗口，再加上解析后的 `mode` 限制（全局最低限制 + 连接/消息/点赞/评论/访问）。`limit` 在无限制模式（无限模式）时为空。
wonda twin health --persona <p>                           # 活跃状态（活跃|暂停|需要认证） + 信号冷却时间（派生出的分级冷却：最强的未解决平台信号） + 最近信号（仅追加的健康记录尾部：429秒，验证码，检查点）。当未解决的严重问题（验证码 / 异常活动 / 账户限制）处于活动状态时，会在标准错误输出中打印 `run: wonda twin recover <persona> after resolving in-browser` 提示（标准输出 JSON 保持不变）。

# 操作限制（每个 twin 模式 + 自定义覆盖安全门强制执行）
wonda twin limits get <persona>                           # 显示 twin 的限制模式（预热|保守稳定|适度最大|无限） + 自定义覆盖
wonda twin limits set <persona> --mode moderate_max       # 设置限制模式。无限 = 完全无限制（无全局，无每个操作，无每周）
wonda twin limits set <persona> --connect 30 --message 60 # 设置每个操作的每日自定义限制（未限制，自担风险）：--connect/--message/--like/--comment/--visit，--global <N>（每日汇总），--*-weekly <N>（7天滚动）。传递覆盖标志会合并到存储的覆盖中（其他自定义限制保持）；--clear-overrides 会将它们全部恢复到模式。
```

### 本地 WAB 中继 (`wonda relay`)

在调用者仍然使用云代理并使用相同的 `/twin/sessions/{persona}/actions/{platform}/{action}` API 时，在此机器的本地 WAB 上运行注册的 twin 操作。

`relay health` 和 `relay restart` 需要 Wonda CLI v1.57.0 或更高版本。在调用这两个命令之前，请检查 `wonda --version`。在较旧或未知版本上，不要尝试不可用的命令：使用 `wonda doctor --relay` 而不是 `relay health`。不要用 `relay install` 替代 `relay restart`，因为在重新安装而没有每个配置的 `--persona` 的情况下，可能会替换中继的 persona 集合。报告安全的 CLI 重启需要 v1.57.0+，并在该版本可用时提示用户升级。

```bash
wonda relay pair                                        # 使用现有的浏览器登录流程将此机器与您的 Wonda 账户配对
wonda relay run --persona <p>                           # 长轮询云代理并为 persona 提供操作
wonda relay status --persona <p>                        # 显示本地中继配置
wonda relay health                                      # v1.57.0+. 此机器中继的一行判断：状态（连接|待机|降级|离线） + 原因（正常，待机，未安装，未运行，等待登录，钩子不可达，未配对，引导，浏览器引导失败，代理断开连接，代理不可达，代理未知，自我更新失败，版本不匹配，版本阻止）。`待机` 表示在此机器上中继是健康的，但账户的另一个设备是活动的，因此此机器在此用户在设置页面上选择使其成为活动状态之前什么也不做：按设计工作，不是错误。`等待登录` 是一个 Windows 机器，任务已注册且无人登录：预期，不是错误，因此不要将其报告为失败。`钩子不可达` 是一个活跃的中继进程，其回环状态钩子无法读取（自定义 --local-hook-port，或标准端口被占用）：中继可能正在服务，但本地不可观察。JSON 还包含 `serving`（true|false|absent）镜像中继自己的轮询答案；absent 表示未知（旧中继或后端，或最后一次轮询失败），永远不会待机。`版本阻止` 表示服务器的版本策略拒绝此中继发送新操作，直到它更新（它仍然可以报告 serving=true，因此阻止优先于绿色）+ 摘要/详情/提示，以及运行/配对/监督，版本，persona，连接/断开连接，日志路径。基于 `reason` 分支，永远不基于消息。macOS 菜单栏点的 FORENSIC 级别：点的稳态轮询直接通过 HTTP 读取中继的回环 /status（无 CLI 启动），并且仅快速分类健康的当前二进制 payload；此命令在 HTTP 寂静时、状态转换后、用户操作后以及只要 payload 无法快速分类时（持续故障，如未配对/引导/阻止/版本漂移，或一个不报告 `serving` 的旧中继），都会持续运行，因为 forensic 判决是点的唯一状态来源。因此，在持续故障期间重复的 `relay health` 子进程是预期的，不是错误；只有健康的稳态才无需启动。`wonda doctor --relay` 按项打印相同的事实
wonda relay restart                                     # v1.57.0+. 重启安装的中继。macOS：当 launchd 已经监督此二进制时，使用 `launchctl kickstart -k`，否则回退到完整的 `relay install` 路径（重写 plist，引导）。Windows：重新注册并重启计划任务。保留自动启动已经服务的 persona，除非您传递 --persona
wonda relay stop --persona <p>                          # 清除云中继的 persona 存在（此操作不会停止本地中继进程；使用 `wonda relay disable` 停止它，`wonda relay restart` 重启它，或 `wonda relay uninstall` 删除自动启动）
wonda relay disable                                     # 停止运行的中继并将其自动启动持久关闭，直到 `relay enable`/`app open` 恢复：macOS：launchctl bootout + 持久性的 launchctl disable（生存 KeepAlive 和下次登录）。Windows：schtasks /End + 停止中继进程 /End 留下 + /Change /DISABLE（生存登录触发器和失败重启）。两者也会停止手动使用 `relay run` 启动的中继（无论在哪个合法位置继承的标志；此用户唯一），并验证结果：命令失败而不是报告未发生的停止。保留 plist/任务，因此 persona 保留以重新启用。这是进程级别的停止；`relay stop` 是无关的代理存在清除
wonda relay enable                                      # disable 的逆操作。macOS：首先清除 launchd 禁用覆盖（禁用的服务拒绝引导），然后以最终结果为运行中中继的最便宜路径：已经监督的中继带有活 pid 被保留，没有活 pid 的正确加载工作（KeepAlive 回退，手动 `launchctl stop`）获得一个简单的 kickstart（模式 "kickstart"，无 plist 重写），其他状态重新运行完整的安装路径（重写 plist + 引导；模式 "reinstall"）。Windows：schtasks /Change /ENABLE，然后在进行 /Run 之前检查活中继 pid：已经运行的中继（无论是任务的实例还是手动使用 `relay run` 启动的，任务 IgnoreNew 政策无法看到）被保留，并且只有没有活中继的机器才会进行 /Run；未注册的任务会安装新任务。保留安装的 persona，类似于 `relay restart`
wonda relay install [--persona <p>]                     # 安装中继以在登录时自动启动并保持运行。macOS：LaunchAgent（在崩溃时重启，记录到 ~/Library/Logs/wonda-relay.log）。Windows：通过隐藏的 VBScript 包装器（登录触发器 + 失败重启，无管理员，无密码，无控制台窗口）启动的用户级计划任务。重新运行以将自动启动指向新二进制。Homebrew Cellar 路径会自动重写为稳定的 opt 符号，以便 brew cleanup 无法删除目标。.pkg 和 Windows 安装程序为安装的控制用户运行此操作；CLI 仅通道（brew 公式，npm，install.sh）通过 `wonda app install` 获取（install.sh 提供交互式；brew/npm 仅打印指针，因为包钩子无法运行设置：pnpm 10/Bun 块生命周期脚本，npm v12 默认禁用它们）。在既没有应用也没有中继自动启动的机器上，也会进行一次性提示，将其指向 `wonda app install`（y/N，默认不；永远不会静默下载），否则跳过该条目并报告（`loginItem: skipped-app-not-installed`，加上 `appInstallHint`）。Windows：写入隐藏的 Startup 文件夹启动器（wonda-startup.vbs，用户级，在登录时运行 `wonda app open`，如果 wonda.exe 已消失则静默无操作），在每次打开时都会重写，因此后来的 NSIS 安装会重新指向同一个文件（永远不会重复）；中继的计划任务独立保留自己的登录触发器。幂等，并且序列化：并发打开无法堆叠托盘图标或登录项。部分成功退出契约：`app open` 即使子步骤失败也会退出 0（它从 Finder 或开始菜单启动，没有终端；托盘徽章是失败表面），在 JSON 结果中报告失败作为 `relayError`，`loginItemError`，`appInstallError`，`startupEntryError` 或 `trayError`。自动化必须检查这些字段，而不是单独检查退出代码
wonda app install [--release <tag>]                     # 从 CLI 仅安装（brew 公式，npm，curl）到完整桌面体验的桥梁：从发布（macOS：经认证的 wonda-macos.pkg；Windows：wonda-windows-setup.exe）下载此 CLI 版本的签名安装程序，验证其 SHA-256 与发布的 checksums.txt（缺少条目是硬失败，永远不会未验证运行），并运行它。macOS：`sudo installer -pkg ... -target /` 带有正常的 sudo 提示，然后继续到 `app open`；Windows：启动设置程序 DETACHED 并退出（安装程序杀死运行的 wonda.exe 进程以释放图像，包括此程序，并自己完成整个设置）。幂等：已安装的确切版本（macOS：sh.wonda.cli 的 pkgutil 收据；Windows：添加/删除程序记录）提供重新安装，默认不。没有 TTY 时会打印下载 URL 和手动步骤，而不是运行任何内容。开发构建会跳过并显示消息；隐藏的 --release <tag> 安装特定版本（活测试接缝）。豁免于最低版本门：被阻止的 CLI 必须能够获取当前安装程序，这是其自身条件的补救措施。首次运行提示：在既没有应用也没有中继自动启动的机器上的交互式 CLI 会打印一个指针，一次（标记在 ~/.wonda 中），永远不会在 CI 或脚本中
wonda app open                                          # 桌面应用打开，macOS 上的 /Applications/Wonda.app（macOS；一个微小的 shim，运行一个固定路径：pkg 的根拥有的有效负载 CLI 在 /Library/Application Support/Wonda；没有每个用户或 PATH 回退，因此没有跨用户交换表面，而中继本身仍然由 Go 侧交给您的验证式自我更新的 ~/.wonda 二进制）和 Windows 开始菜单中的 "Wonda" 条目（Windows；安装程序写入的隐藏 VBS 启动器）运行：修复 + 启用中继自动启动（健康的中继未被重置），注册 Wonda 以在登录时回来，并显示托盘图标。macOS 登录机制：指向 /Applications/Wonda.app 的登录时打开条目（系统设置 > 通用 > 登录项）；如果该应用未安装（CLI 仅机器），终端运行会提供通过 `app install` 流程获取它（y/N，默认不；永远不会静默下载），否则跳过该条目并报告（`loginItem: skipped-app-not-installed`，加上 `appInstallHint`）。Windows：写入隐藏的 Startup 文件夹启动器（wonda-startup.vbs，用户级，在登录时运行 `wonda app open`，如果 wonda.exe 已消失则静默无操作），在每次打开时都会重写，因此后来的 NSIS 安装会重新指向同一个文件（永远不会重复）；中继的计划任务独立保留自己的登录触发器。幂等，并且序列化：并发打开无法堆叠托盘图标或登录项。部分成功退出契约：`app open` 即使子步骤失败也会退出 0（它从 Finder 或开始菜单启动，没有终端；托盘徽章是失败表面），在 JSON 结果中报告失败作为 `relayError`，`loginItemError`，`appInstallError`，`startupEntryError` 或 `trayError`。自动化必须检查这些字段，而不是单独检查退出代码
wonda app quit                                          # 桌面应用退出，托盘的 "退出 Wonda" 运行：`relay disable`（已验证，包括手动运行的 `relay run`）+ 移除每个回来登录的机制 + 移除图标。macOS：删除 Wonda 应用的登录时打开条目，通过枚举验证（脚本删除每个路径的条目并返回剩余数量）：一个幸存的条目会导致非零退出以修复，图标保留以说明原因，并且无法楔入（在系统设置中删除条目会使下一次退出成功）。没有磁盘上的应用包，系统事件调用会被完全跳过（`loginItem: skipped-app-not-installed`），从而节省 CLI 仅机器的自动化提示（指向缺失应用的条目在登录时无效）。Windows：删除 Startup 文件夹启动器，并且无法删除的启动器（已不存在）会导致非零退出以修复，因为它会在下次登录时重新打开 Wonda。一个已记录的盲点：macOS 自动化权限被拒绝时，条目既不能删除也不能计数，因此退出完成，报告 `loginItemError` 加上注释，并且任何存在的 Open at Login 条目在下次登录时仍会重新打开 Wonda，直到手动在系统设置 > 通用 > 登录项中删除。persona 和登录保持。干净的卸载顺序：`wonda app quit`，然后 brew/npm 卸载（它们没有自己的卸载钩子；NSIS 卸载程序执行自己的清理）
```

中继在您的真实设备和 IP 上运行。平台 cookie 保持本地。它仅在机器和 `wonda relay run` 处于活动状态时提供服务。如果没有活的中继，代理会将相同的 twin 操作调用路由到云 twin。

**在 twin 上运行任何操作的安全性是内在的。** 账户安全性不是序列器的特殊功能：它是 "在 twin 上运行命令" 的属性。相同的每个身份安全门保护 ad-hoc 代理（`wonda linkedin connect --account <name>`），自动驾驶，`twin schedule` 和用户编写的序列，通过一条执行路径针对一个共享的每个身份计数器。因此，在一个 persona 上沉重的 ad-hoc 日常会自动收紧该 persona 的剩余空间（每个身份一组天花板，不会双重收费）。限制是一个每个 twin 模式（预热 / 保守稳定（默认） / 适度最大 / 无限；通过 `wonda twin limits set` 设置）选择每个操作的每日天花板，每个操作的 7 天滚动每周天花板，以及一个全局每日汇总限制；`无限` 关闭所有限制，并且自定义覆盖是未限制的。门根据其 argv 分类每个命令：写入 / 社交操作命令（连接，发送消息，点赞，评论，访问，...）被限制；读取（连接状态，对话，个人资料，搜索），生成（图像/视频/文本），和未知命令自由无门。这就是为什么存在 SENSE 词汇：代理在执行之前会询问 `can-act` / `actions` / `health`，然后根据键入的结果分支，而不是尝试写入并捕获拒绝。

使用 MCP 工具 `sequence_validate`、`sequence_create`、`sequence_run`、`sequence_runs`、`sequence_update`、`sequence_cancel_run` 和 `sequence_schedule`。创建前请先验证。在手动或计划运行前会检查所有必需的 `{{vars.*}}` 值。计划运行是可选的，接受经过验证的 5 字段 cron 加 IANA 时区，或一次性即时、确定性抖动、存储变量和显式的 `allowOverlap`（默认为 false）。

中继执行由功能清单驱动，而非注册表限制：每个生成的 LinkedIn、Sales Navigator、X 和 Reddit 命令都可以在配对机器上运行，包括仅限本地的命令，如 X DM。`transport: auto` 在定义需要这些仅限本地的命令时从 Premium 云偏好回退到中继。每次运行都会快照其定义、解析的传输、组织计费范围和触发器，因此编辑或上下文更改不会重写正在进行的任务。

**统一错误分类（基于 `code` 分支，而非消息）。** 每个双胞胎/外联界面都返回现有的 `{ error: { code, message } }` 封装，并且在配额拒绝时还会携带 `deferUntil`（配额重置的 ISO 时间）+ `reason`（细粒度门禁信号）。代理基于类型的 `code` 分支：

| `code`                | 含义                                                                                                                                                                                                                                                  | 代理应执行的操作                                                                                                                      |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `throttled`           | 一个 WRITE 被每个身份的安全门（遮罩层、HTTP 429）阻止。细粒度原因是 `reason` (`limit_hit` / `weekly_limit_hit` / `warmup_frozen`)。                                                                                                                  | 在 `deferUntil` 后重试；或选择另一个发送者。                                                                                             |
| `limit_reached`       | 对于 UTC 当天的每个操作 DAILY 限制（连接/消息/点赞/评论/访问，根据双胞胎的计费模式）已被消耗。                                                                                                                                             | 等待 `deferUntil`（下一个 UTC 午夜）或使用不同的操作/发送者。                                                                 |
| `limit_exhausted`     | 全局每日汇总限制（`_all` 地板）或每个操作的滚动 7d 周期上限已被消耗。                                                                                                                                                                                | 暂停此身份，直到 `deferUntil`；切换到另一个双胞胎，或通过 `wonda twin limits set` 提高计费模式。                                     |
| `needs_auth`          | 双胞胎的会话需要重新认证（cookie 过期/检查点）。                                                                                                                                                                                                   | 运行 `wonda twin login <persona>`；不要重试 WRITE。                                                                                     |
| `sender_blocked`      | 身份被健康停止：双胞胎已暂停/预热冻结，一个未解决的关键平台信号处于活动状态（验证码/异常活动/账户限制，或慢性 429 风暴），或中继离线。健康停止，而非干净限制。                                                                                              | 停止驱动此身份；检查 `wonda twin health`。对于活动的关键问题，在浏览器中解决它，然后运行 `wonda twin recover <persona>`。             |
| `command_not_allowed` | 命令不在双胞胎的权限允许列表中，或它命名了一个未注册的 LinkedIn / Reddit / X / Instagram 动词。                                                                                                                                                          | 使用 `--allow <cmd>` 重新配置允许列表拒绝；丢弃未注册的平台动词。                                                                |
| `unsupported_channel` | argv 指向双胞胎或 CLI 无法运行的平台/动词。                                                                                                                                                                                                        | 此双胞胎没有这样的 wonda 命令；丢弃它。                                                                                              |
| `invalid_payload`     | 实时流操作有效负载格式不正确，包括一个坏的媒体引用，它不是一个 Wonda 媒体 ID 或 `https://` URL。                                                                                                                                                      | 在重试前修复有效负载。                                                                                                              |
| `media_not_found`     | 双胞胎媒体操作中的 Wonda 媒体 ID 不属于调用者或没有存储的对象。                                                                                                                                                                                        | 使用由运行双胞胎的账户拥有的媒体 ID。                                                                                              |
| `media_fetch_failed`  | 运行者无法将解析的媒体 URL 下载到其每个操作的临时目录中。                                                                                                                                                                                              | 使用新的签名 URL 或可访问的 Wonda 媒体 ID 重试。                                                                                      |
| `not_found`           | 双胞胎/活动/资源不存在。                                                                                                                                                                                                                              | 首先配置/创建它。                                                                                                                    |
| `deferred`            | 结构化、非错误的延迟：在一个 BATCH 中，门禁放弃了一个超限命令并运行了其余命令。                                                                                                                                                                        | 在 `deferUntil` 后重新入队延迟的命令。                                                                                           |

`wonda twin can-act` 返回与稍后 WRITE 会拒绝的相同的 `code` + `reason`，因此一个读取 `code: "needs_auth"` 从 `can-act` 然后在 WRITE 上看到 `needs_auth` 的代理基于一个代码分支。

### 日历 (`wonda calendar`)

一个只读源，覆盖两个否则需要分别检查的事物：即将到来的双胞胎计划触发，以及过去的运行和平台操作。在真实时区解析，因此“周二”意味着用户的周二。

```bash
wonda calendar                                              # 本月此民用时区（检测到的机器 IANA 时区，UTC 回退）
wonda calendar --from 2026-07-01 --to 2026-07-31 --timezone Europe/Paris
wonda calendar --all                                        # 包括空无所有日期的日子
wonda calendar day 2026-07-24 --timezone Europe/Paris --limit 200
```

一个范围返回每日计数；`calendar day` 返回单个条目。这种拆分是故意的：一个繁忙的账户在一个月份中有数万行，而月份网格永远只显示计数。

两个轴永远不能相加：`counts.run` 是双胞胎运行，`actions` 是源中性操作账本中的行。一个运行执行许多平台操作，并且通过中继在用户自己的机器上运行的操作根本不执行云运行。低报数是明说的而非暗示的：`truncated.scheduleFires` 意味着计划的触发枚举达到了上限，因此这些计数是一个下限。

## 工作流与发现

### 品牌提取 (`brand extract`)

将网站的视觉系统（颜色、排版、半径、阴影、间距、字体、标志、英雄装饰、CSS 图案背景、虚线/点状边框处理、`:root` 自定义属性、标题强调模式、胶片颗粒/噪声叠加）提取到 `DESIGN.md` + `tokens.json` + `assets/`。通过捆绑的隐身浏览器 + Chromium 驱动器在本地运行（与 `wonda wab install` 相同，用于 `wonda wab record` 和经过身份验证的会话流）。

需要一次性的 `wonda wab install` 来下载隐身浏览器 + Chromium（~300 MB，跨 `wonda wab record`、经过身份验证的会话流和 `brand extract` 共享）。

这是之前基于 `npx` 的品牌提取 CLI 的内部替代品，用于 `slide-generation` / `creative-static-ads` / `premium-static-ads` 技能。

```bash
# 仅限本地 — 无需认证、无积分、无 API 调用
wonda brand extract https://linear.app                       # 写入 ./output/linear.app/{DESIGN.md, tokens.json, assets/}
wonda brand extract https://stripe.com --output ./refs       # 写入 ./refs/stripe.com/...
wonda brand extract https://vercel.com --screenshot          # 也写入 page.png
wonda brand extract https://stripe.com --viewport 1440x900   # 覆盖默认 1920x1080

# 持久化到服务器（通过媒体预签名 + POSTs /brand/save 上传资源）
wonda brand extract https://stripe.com --save                # 本地 + 持久化
wonda brand extract https://stripe.com --save --make-active  # 本地 + 持久化 + 激活（常见路径）
wonda brand extract https://stripe.com --no-output --save    # 不写入磁盘，仅持久化

# 移动已持久化的品牌
wonda brand save --from ./output/stripe.com --make-active    # 持久化先前提取的目录
wonda brand pull <brand-id>                                  # 将保存的品牌下载回 ./output/<domain>/
```

标志：

- `--save`：通过媒体预签名流程上传 `assets/` 并 POST `{tokens, mediaIds}` 到 `/api/v1/brand/save`。需要认证。
- `--make-active`：隐含 `--save`。将新品牌设置为活动状态。
- `--output <dir>`：覆盖本地输出目录。默认是 `./output/<domain>/`。与 `--no-output` 互斥。
- `--no-output`：不写入磁盘（内存提取用于管道）。与 `--output` 互斥。
- `--name "Brand Name"`：持久化时覆盖品牌名称。默认为域名词干的大写形式。
- `--screenshot`：也保存 `page.png` 与 DESIGN.md 一起。
- `--viewport WxH`：无头浏览器的视口大小。默认 `1920x1080`。

输出（当 `--no-output` 未设置时，始终到 `<output-dir>/<domain>/`）：

- `DESIGN.md`：令牌、排版、英雄装饰、标志、CSS 图案、虚线边框和根 CSS 变量的 Markdown 摘要。在制作幻灯片/静态广告技能中组合 HTML 前阅读此文件。
- `tokens.json`：提取的原始结构化 JSON。
- `page.png`：仅当传递 `--screenshot` 时。
- `assets/`：原始英雄装饰文件加上 `assets/fonts/` 用于任何非 Google `@font-face` URL。始终在 `--no-output` 时写入。

将写入的文件路径打印到标准输出。使用 `--save` 时，还会打印 API 响应（`brandId`、`sourceDomain`、警告）。失败时非零退出（网络错误、导航超时、浏览器崩溃、保存失败）。

### 视频分析

分析视频以提取复合帧网格（视觉）和音频文本（文本）。在创建变体之前了解视频内容很有用。需要 **完整账户**（非匿名）并基于视频时长消耗积分（ElevenLabs STT 定价）。

如果视频刚刚上传并且仍在标准化，CLI 会自动重试，直到媒体准备就绪。

```bash
# 分析视频 — 返回复合网格图像 + 文本
ANALYSIS_JOB=$(wonda analyze video --media $VIDEO_MEDIA --wait --quiet)

# 任务输出包含：
# - compositeGrid：显示 24 个均匀分布帧的图像
# - transcript：任何语音的完整文本
# - wordTimestamps：单词级时间 [{word, start, end}]
# - videoMetadata：{width, height, durationMs, fps, aspectRatio}

# 下载复合网格进行视觉检查
wonda analyze video --media $VIDEO_MEDIA --wait -o /tmp/grid.jpg

# 仅获取文本
wonda analyze video --media $VIDEO_MEDIA --wait --jq '.outputs[] | select(.outputKey=="transcript") | .outputValue'
```

**错误处理**：402 = 积分不足，409 = 媒体仍在处理（CLI 自动重试）。

### 电子邮件

管理一次性电子邮件账户并读取邮箱消息。这些命令需要 `emailServerApiEnabled` 标志。

```bash
wonda email account create [email]                    # 创建电子邮件账户
wonda email account create --random --domain <domain> # 创建具有随机用户名的电子邮件
wonda email account create --username <name> --domain <domain> # 创建具有选定用户名的电子邮件
wonda email account get <email>                       # 获取电子邮件账户详情
wonda email account delete <email>                    # 删除电子邮件账户

wonda email inbox list <email>                        # 列出收件箱消息
wonda email inbox read <email> <id>                   # 读取特定电子邮件并验证代码
wonda email inbox wait <email> --timeout 60           # 等待新电子邮件到达
wonda email inbox wait <email> --since "$SINCE"       # 仅消息在 RFC 3339 时间戳之后
wonda email inbox wait <email> --since-id "$MAX_ID"   # 仅消息 ID 大于此
```

对于注册流程，在触发验证电子邮件之前捕获 `--since`，或使用 `wonda email inbox list <email> --jq '[.[].id] | max // 0'` 快照当前最大消息 ID 并传递给 `--since-id`。

### 任务

```bash
wonda jobs get inference <id>                         # 推理任务状态
wonda jobs get editor <id>                            # 编辑器任务状态
wonda jobs get publish <id>                           # 发布任务状态
wonda jobs wait inference <id> --timeout 20m          # 等待完成
```

### 发现

```bash
wonda models list                                     # 所有可用模型
wonda models info <slug>                              # 模型详情和参数
wonda operations list                                 # 所有编辑操作
wonda operations info <operation>                     # 操作详情
wonda capabilities                                    # 平台全部功能
wonda pricing list                                    # 所有模型的定价
wonda pricing estimate --model seedance-2 --prompt "..." # 成本估算
wonda style list                                      # 可用的视觉风格
wonda balance                                         # 当前信用余额（组织钱包在组织上下文中）
wonda usage                                           # 当月支出摘要（按模型/项目）
wonda usage --month 2026-05                           # ...针对一个日历月
wonda usage --from 2026-04-01 --to 2026-06-30         # ...针对自定义范围
wonda usage --project acme-launch                     # ...限制在一个项目内
wonda project list                                    # 支出标记项目在活动范围内
wonda project create acme-launch                      # 创建一个（组织范围：仅管理员/所有者）
wonda use --project acme-launch                       # 标记后续支出（粘性）
wonda topup                                            # 充值信用（打开 Stripe 结账）
```

### 编辑音频和图像

```bash
# 编辑音频
wonda edit audio --operation <op> --media <id> --wait -o out.mp3
```

对于任何图像编辑（裁剪、文本叠加、img2img、背景移除、矢量化）请拉取专用技能：`wonda skill get image-edit`。

### 对齐（时间戳提取）

```bash
wonda alignment extract-timestamps --model <model> --attach <mediaId> --wait
```

## 质量等级

| 等级     | 图像模型                                    | 分辨率                              | 视频模型              | 说明                                                                                                                                               |
| -------- | ---------------------------------------------- | --------------------------------------- | ------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| 标准     | `gpt-image-2` (自动) — 备选: `nano-banana-2` 1K | 1024×1024 / 1024×1536 (gpt) / 1K (nano) | `seedance-2` (高, 5s)  | 默认。gpt-image-2 用于最强的提示遵循 + 图像中的文本；nano-banana-2 用于更快的 Gemini 迭代，支持多参考。                                           |
| 高       | `gpt-image-2` (高) — 备选: `nano-banana-2` 2K | 1024×1024 / 1024×1536 (gpt) / 2K (nano) | `seedance-2` (高, 15s) | 清晰输出。对 gpt-image-2 使用 `--params '{"quality":"high"}'` 或在 nano-banana-2 上提高 `--params '{"resolution":"2K"}'`。也提供 `sora2pro`。 |
| 最高      | `nano-banana-pro` 4K — 备选: `nano-banana-2` 4K | 4K                                      | `seedance-2` (高, 15s) | 真正的 4K（gpt-image-2 最高 1536px）。使用 `--params '{"resolution":"4K"}'`。也提供 `sora2pro`（1080p）用于视频。                               |

## 故障排除

| 症状                          | 可能原因                                  | 解决方法                                                    |
| -------------------------------- | --------------------------------------------- | ------------------------------------------------------ |
| Sora 拒绝图像              | 图像中有人                               | 切换到 `kling_3_pro`                                |
| 视频添加了源图像中不存在的对象 | 运动提示描述了图像中不存在的元素            | 简化为仅相机运动和氛围                                      |
| 视频中的文字难以辨认         | AI 尝试在生成中渲染文字                   | 从视频提示中删除文字，使用 textOverlay 代替                |
| 手看起来不对                 | 提示中包含复杂的动作                     | 简化为被动位置或帧排除                                      |
| 风格在系列中不一致           | 没有共享锚点                              | 通过 `--attach` 使用相同的参考图像                        |
| 步骤 A 的更改未在步骤 B 中显示  | 陈旧的渲染                                  | 重新运行所有下游步骤                            |

## 时间预期

- 图像：30秒 - 2分钟
- 视频（Sora）：2 - 5分钟
- 视频（Sora Pro）：5 - 10分钟
- 视频（Veo 3.1）：1 - 3分钟
- 视频（Kling）：3 - 8分钟
- 视频（Grok）：2 - 5分钟
- 音乐（Suno）：1 - 3分钟
- TTS：10 - 30秒
- 编辑操作：30秒 - 2分钟
- 唇形同步：1 - 3分钟
- 视频放大：2 - 5分钟

## 错误恢复

- **未知模型**：`wonda models list`
- **没有 API 密钥**：`wonda auth login` 或设置 `WONDA_API_KEY` 环境变量
- **作业失败**：`wonda jobs get inference <id>` 查看错误详情
- **参数错误**：`wonda models info <slug>` 查看有效参数
- **超时**：`wonda jobs wait inference <id> --timeout 20m`
- **信用不足（402）**：`wonda topup` 添加信用

LinkedIn WAB 附件：使用 `linkedin send-message <target> [text] --attach <local-path>` 并带一个支持的本地文件（bmp/gif/jpeg/jpg/png/doc/docx/pdf/mp4/m4a，最大 20,000,000 字节）。添加 `--dry-run` 以在不发送的情况下预览上传。云模式会拒绝本地路径。
