# EAS 模拟器

> **EAS 服务 - 适用费用。** EAS 模拟器是一个托管的 EAS 服务。会话使用情况取决于您账户的定价和限制。请访问 https://expo.dev/pricing 获取当前条款。

EAS 模拟器在 EAS 基础设施上运行远程 iOS 模拟器或 Android 模拟器，您从您的机器上控制它——从 CLI、从 AI 代理（通过 `agent-device`）以及从浏览器预览。它是解锁**无法在本地运行模拟器的环境**（Linux 盒子、云/后台代理如 Cursor Cloud）的钥匙，并且允许代理在真实设备上*验证*更改，而不仅仅是推理代码。

`simulator:*` 命令是**实验性且隐藏的**，需要较新的 eas-cli（截至撰写时为 ≥ 20.3.0）——这就是为什么这个技能通过 `npx --yes eas-cli@latest` 运行所有内容的原因。标志和动词可能会更改；**相关子命令的 `--help` 输出具有权威性。**

## 使用场景

frontmatter `description` 承载了触发短语。简而言之：使用此功能将用户的 App 上传到**云**模拟器并与其交互——尤其是在没有 Mac 或云/沙盒代理的情况下。**不**用于本地模拟器（`expo run:ios`、Xcode、Android Studio）、商店构建/签名（那是 EAS Build），或物理设备。对于 macOS 情况，请参阅下一节 *云与本地*。

## 云与本地：首先确定这一点

- **明确的云/远程/可共享请求**：在检查访问权限后，在任何主机上使用 EAS 模拟器。
- **通用模拟器请求**：在可用时使用合适的本地模拟器。如果主机无法运行请求的模拟器（例如，在 Linux 或云沙盒上的 iOS），在检查访问权限后使用 EAS 模拟器。非 macOS 主机可能仍然支持本地 Android 模拟器。
- 尊重明确的本地选择；适当地将任务交给 `expo run:ios` / Xcode / Android Studio。仅在请求的环境仍然模糊且会影响任务时才进行澄清。

当用户请求 EAS 模拟器或云模拟器时，在该请求和任何声明的预算范围内进行操作。解释适用的使用情况一次，并通过会话保留现有的授权。在超出声明的预算或超出请求的工作范围之前进行询问。

## 前置条件

- **通过 `npx --yes eas-cli@latest …` 运行每个 `eas` 命令**——确保 CLI 新 enough 以包含 `simulator:*`（通常全局 `eas` 过旧），并且 `--yes` 跳过 npx 的提示。（如果 `eas --version` 是最新的，裸 `eas` 也很好。）
- **已认证。** 交互式机器 → `npx --yes eas-cli@latest login`。**云沙盒 / CI / 无头代理没有浏览器登录——在环境中设置 `EXPO_TOKEN`**（expo.dev → Account → Access Tokens）。无论哪种方式，都通过 `npx --yes eas-cli@latest whoami` 进行验证。
- 从 Expo **项目目录**中运行。新应用需要一次性设置：`npx --yes eas-cli@latest init` 创建/链接项目（如果没有 `projectId`），如果缺失，则**在应用配置中设置 `ios.bundleIdentifier`**——新的 `create-expo-app` 通常没有，并且 `prebuild`/`eas build` 需要它（它们在没有它的情况下会提示或失败；例如 `dev.<owner>.<slug>`）。使用 `npx expo config --json` 阅读当前配置（它可能位于 `app.config.js` 中）。第一次 Mode-C 运行很慢（原生构建）；后续运行会重用它。
- 一个控制器来驱动设备。这个技能使用 **agent-device**（开源，MIT），通过 `npx agent-device@latest` 按需运行——没有全局安装的内容。**Appium** 和 **argent** 是替代的自动化接口；`web-preview-only` 没有自动化接口。参见 [references/controllers.md](./references/controllers.md)。
- **`.env.eas-simulator`** 由 eas-cli（不是这个技能）编写/管理：它包含会话 ID（`EAS_SIMULATOR_SESSION_ID`）+ 守护程序 URL/**令牌**，因此 `get`/`stop`/`exec` 默认为此会话（通常**省略 `--id`**；将 `--id <id>` 传递给另一个目标）。它包含一个**令牌 → 忽略 gitignore**（eas-cli 将其标记为“不要提交”，但可能不会添加忽略规则，并且新应用的 `.gitignore` 不会覆盖它——如果缺失，请添加 `.env.eas-simulator`）。
- **命令块假设 POSIX shell**（bash/zsh）——`printf`、`lsof`、`$(seq …)` 循环在 cmd/PowerShell 中不会运行。在 Windows 上，在 WSL 或 Git Bash 中运行它们，或者边走边翻译（`eas-cli`/`agent-device` 调用本身是跨平台的）。

## 会话生命周期

- `--max-duration-minutes N` 是硬性自动停止截止日期。当账户支持时自定义它；否则使用服务的默认会话限制。
- `--max-idle-time-minutes N` 在经过这么多非活动分钟后停止会话。省略意味着**没有空闲超时**：会话运行到最大持续时间或显式停止。
- **只有通过 `agent-device` 和 `argent` 报告的活动才会重置空闲计时器。** Appium 命令和浏览器预览活动不会重置它。对于 Appium 或用户驱动的浏览器预览，依靠最大持续时间（而不是空闲时间）来限制会话；当账户支持时，使用 `--max-duration-minutes` 自定义它。

## 首先检查可用性

EAS 模拟器是一个**有限访问**的 EAS 功能，仍在逐步推出中，因此它不会在所有账户上启用。在开始会话之前检查访问权限；此只读命令不会创建会话。

```bash
npx --yes eas-cli@latest simulator:availability [--json] [--non-interactive]
# → {"available": true, ...}  启用 → 继续到核心循环
# → {"available": false, ...} 未启用 → 不要开始会话
```

如果它**未**可用，不要调用 `simulator:start`（它将失败）。相反，优雅地转移，以便您在不使用此技能的情况下继续取得进展：
- 告诉用户他们的账户上**尚未**可用 EAS 模拟器——它很快就会到来。
- 落回到他们正常的本地路径以实现实际目标——`expo run:ios` / Xcode / Android Studio 用于本地模拟器/模拟器、EAS Build 或其他适合的内容。不要在云模拟器上卡住；请求几乎永远不会是“专门使用 EAS 模拟器”。

（如果 `simulator:availability` 不可识别，CLI 过旧——升级，或者将 `simulator:start` 从“此账户未启用”错误视为相同方式：停止并回退。）

## 核心循环（始终相同）

会话是：**启动 → （安装您的应用）→ 驱动 → 停止。** `eas-cli` 拥有 *会话*；设备 *动词*（打开/点击/截图）来自控制器，`npx --yes eas-cli@latest simulator:exec` 为您加载会话连接环境并运行它。

```bash
# 1. 启动会话（启动远程模拟器 + agent-device 守护程序；写入 .env.eas-simulator）。
# 如果 dotenv 指定了一个会话，首先使用 simulator:get --json 检查它。当它属于此运行时重用它；仅在它处于范围内且不再需要时停止它。一个 IN_PROGRESS 会话可能有意并发，因此在重置 dotenv 之前保留其 id/配置。
# 仅在选择如何处理该现有会话后，才继续下方。
printf '# managed by eas-cli\n' > .env.eas-simulator   # 仅在解决任何活动会话后清除
npx --yes eas-cli@latest simulator:start --platform ios --type agent-device --non-interactive \
  --name "Checkout flow screenshots"   # 始终命名它——见“始终命名会话”
#    然后确认它正在运行：simulator:get --json → 状态 IN_PROGRESS（运行-your-app.md 中的有界轮询）。

# 2. 通过 `exec` 驱动它（加载会话环境，然后运行您给它的命令）。
#    agent-device 通过 npx 按需运行——没有全局安装的内容。
npx --yes eas-cli@latest simulator:exec npx agent-device@latest open <app-or-url> --platform ios
npx --yes eas-cli@latest simulator:exec npx agent-device@latest snapshot -i          # 交互式 UI 树 → @e1, @e2 引用
npx --yes eas-cli@latest simulator:exec npx agent-device@latest press @e2            # 点击一个引用（注意：“press”，不是“tap”）
npx --yes eas-cli@latest simulator:exec npx agent-device@latest screenshot ./shot.png

# 3. 停止会话并重置 dotenv。省略 --id 以针对 dotenv 会话。
npx --yes eas-cli@latest simulator:stop
printf '# managed by eas-cli\n' > .env.eas-simulator
```

要**实时观看**它，将 `start` 打印的 `webPreviewUrl` 交给用户。所有当前会话类型都包含浏览器预览；`agent-device`、`appium` 和 `argent` 也提供自动化，而 `web-preview-only` 没有自动化接口。**此 URL 是用于 *用户的* 浏览器——您不能为他们打开它，它永远不能接触模拟器：**
- **“在这里打开”（Cursor/VS Code）** → 将 URL 打印在单独的一行，并告诉用户打开 Simple Browser（`Cmd/Ctrl+Shift+P` → "Simple Browser: Show"）并粘贴它。然后**停止**：不要将命令外放到系统浏览器或 Cursor/VS Code URL 处理器，并且不要问“是否出现标签页？”——您无法确认，转移已经完成。
- **永远不要在模拟器上 `open` `webPreviewUrl`。** 它是一个浏览器预览，不是深度链接，也不是 `agent-device open` 参数；将其路由到设备会渲染一个浏览器中的浏览器（一个真正的失败）。
- **无头代理**（无显示器）→ 仅将 URL 作为交付物返回。
- **让它保持活动状态以供用户驱动** → 当支持时使用 `--max-duration-minutes N`，否则使用服务的默认限制。浏览器预览活动不会重置 `--max-idle-time-minutes`，因此空闲超时在这种情况下不是一个可靠的会话生命周期限制。告诉用户会话何时过期，使用 CLI 报告的持续时间或过期时间。为请求的预览保持运行；当为一次性任务创建的会话完成任务时停止会话。

`start` 还打印一个作业运行 URL。

## 始终命名会话

在每次 `simulator:start` 上传递 `--name "<description>"`。名称出现在 `simulator:list`、`simulator:get` 和 expo.dev 上的 **模拟器会话** 页面中，它替换了每一行的通用标题。未命名的每一行都显示“模拟器会话”和一个随机 ID——一堵无人能导航的相同条目墙。为**人类扫描该列表几天后**命名，而不是在运行期间为自己命名。

写几行简单的文字说明会话的*用途*：

```bash
--name "Checkout flow screenshots"     # 您做了什么
--name "Dev build — dark mode fix"     # 您在测试什么
--name "Login repro for issue 412"     # 它存在的原因
```

规则：
- 从用户的请求中派生，而不是从模式或工具中。`Mode C 会话`、`agent-device ios` 和 `test` 什么也说不清。
- **长度：目标是 3-6 个词，约 40 个字符，并将 50 视为实际限制。** 它在一个窄表格列中作为单行标题呈现，因此长名称会被截断。API 接受最多 **255 个字符**，并拒绝空白的/仅包含空白的名称，但 255 是一个天花板，您永远不会接近它，而不是一个目标。一个名词短语，没有句子。
- 在该预算内保持具体。当有票证或 PR 编号时，请包含它。
- **句子大小写：** 仅大写第一个单词，并将标识符保留在其真实大小写（`Dev build for expo-router v4`，`Repro for EXPO-1234`）。它是一行标题，因此没有标题大小写、没有全小写、没有结尾句号。
- **不要重复表格已经显示的内容。** 每一行都显示会话 ID、平台、开始时间、持续时间和创建者——因此没有 ID、没有 iOS、没有日期、没有您的姓名。在那些列无法表达的内容上花费整个预算：目的。
- 如果用户命名了它，请按原样使用其名称。
- 会话是按运行执行的，因此为每个新运行命名。不要重用旧名称用于不同的工作。

`--name` 比本身 `simulator:start` 更新，因此较旧的已安装 `eas-cli` 可能会拒绝它。如果发生这种情况，通过 `npx --yes eas-cli@latest` 或升级运行；作为最后的手段，一次不带 `--name` 重试（会话未命名）。参见 [references/troubleshooting.md](./references/troubleshooting.md)。

## 一览命令

在使用非默认启动标志、机器可读/配置输出、列表过滤器或会话事件之前，查询已安装 CLI 的完整当前标志集：

```bash
# 将 `start` 替换为您即将运行的模拟器子命令。
npx --yes eas-cli@latest simulator:start --help
```

下面的示例涵盖了常见的流程；它们有意不是 CLI 表面的详尽副本。即使在从 `--help` 构建命令时，也要保留此技能的非明显行为指导——尤其是 [会话生命周期](#session-lifetime)。

| 命令 | 目的 |
|---|---|
| `npx --yes eas-cli@latest simulator:availability [--json] [--non-interactive]` | 无需创建会话即可检查访问权限。 |
| `npx --yes eas-cli@latest simulator:start --platform ios\|android --name "<description>" [flags]` | 创建会话；启动模拟器 + 选定的接口；默认情况下写入 `.env.eas-simulator`；打印预览 + 作业运行 URL。**始终传递 `--name`**。`--json` 不会抑制 dotenv；当不需要写入文件时使用 `--out-config-type env`。 |
| `npx --yes eas-cli@latest simulator:exec <cmd> [args…]` | 加载 `.env.eas-simulator`，然后以该环境运行 `<cmd>`。到控制器的桥梁。 |
| `npx --yes eas-cli@latest simulator:get [--id <id>] [--json] [--non-interactive]` | 会话状态 + 连接详细信息，包括会话名称。**使用此命令确认就绪**（见 *操作原理*）。 |
| `npx --yes eas-cli@latest simulator:list [filters] [--limit N] [--after <cursor>] [--json]` | 列出并分页项目会话；按状态、类型、平台、名称前缀和标签进行过滤。 |
| `npx --yes eas-cli@latest simulator:events [--id <id>] [--follow\|--json]` | 显示记录的活动事件；`--follow` 监控会话结束。 |
| `npx --yes eas-cli@latest simulator:stop [--id <id>] [--json] [--non-interactive]` | 停止会话（幂等）。 |

## 运行用户的 App — 选择模式

远程模拟器启动**空白——没有 Expo Go，没有应用。** 安装构建，然后驱动它——但**首先匹配构建类型与目标**（下框中的内容）；这是 live-session 运行出错的点。完整序列：[references/run-your-app.md](./references/run-your-app.md) — 在运行模式之前阅读。

> **在安装任何内容之前，先匹配构建与目标——这是 live-session 运行出错的点。** 两个陷阱，同一个根源（抓取不适合请求的构建）：
> 1. **类型错误。** live 编辑（Mode C）**需要开发构建。** 一个静态构建——本地发布（A）、默认的 EAS 模拟器构建（B），或**任何从早期截图运行中留在模拟器上的构建**——在构建时冻结其 JS，并且**永远无法热重载。** 对于 live 请求，**完全忽略现有构建**并安装**开发**构建（本地 Debug，或带有 `developmentClient: true` 的 EAS 构建）。永远不要将 Metro 重新连接到静态构建，希望它能够重载——它不会。
> 2. **陈旧。** 静态查看必须匹配当前源——仅重用具有指纹匹配的构建，否则重新构建；重用是显式的。因此，遗留的 EAS/发布构建**不是**“迭代 live”的快捷方式——它是错误的二进制文件。一个构建*存在*的事实永远不会让它成为正确的选择。

| 模式 | 它是什么 | 选择何时 | Live 编辑？ |
|---|---|---|---|
| **A — 本地发布构建** | 本地构建发布 `.app`，`agent-device install` 它（上传） | 用户有 Mac 工具链并希望快速“在云设备上运行我的当前代码” | 否（需要重新构建以查看更改） |
| **B — EAS 构建**（罕见，仅显式） | `eas build` 模拟器构建，`agent-device install-from-source <url>`（虚拟机下载它） | **仅在明确要求时**——用户命名现有/EAS 构建，或想要用于 CI/共享的静态 EAS 实物。不用于“让我看”/“迭代”（使用 C）。模拟器构建不需要凭证。 | 否 |
| **C — 本地开发构建 + 隧道** | 开发（Debug）构建 + `EXPO_UNSTABLE_TUNNEL_V2=1 expo start --tunnel` + 连接开发客户端到 Metro | **代理编辑和查看循环**——更改代码并实时查看（快速刷新） | **是** |

快速决定——**默认为 C；A 和 B 仅显式：**
- **C（几乎 everything）**：迭代、交互、戳戳应用、live 编辑——*以及*大多数“让我看我的应用”（当前代码需要构建，所以 live+current 赢）。Mac → 开发客户端在本地构建；没有 Mac → 在 EAS 上构建它（`developmentClient: true`）。**不确定 → C。**
- **A**：仅在 Mac 上进行显式的**静态**截图。
- **B**：仅在用户命名现有/EAS 构建或想要静态 EAS 实物（CI/共享）时——请参阅上面的框，了解为什么静态构建是“迭代”的错误工具。在连接开发客户端或创建 Mode C 隧道之前，请阅读 [Tunnel scope and approvals](./references/run-your-app.md#tunnel-scope-and-approvals)。通过隧道创建、连接和 live 编辑，携带该项目远程开发传输的现有授权；在批准请求中包含其源和具体数据流。

## 驱动设备（agent-device）

如果控制器无法下载录制，从 [EAS 会话实体](./references/controllers.md#recording-download-recovery) 中检索它。

`agent-device` 是控制器。常见动词（每个动词都作为 `npx --yes eas-cli@latest simulator:exec npx agent-device@latest <verb>` 运行）：

| 动词 | 它做什么 |
|---|---|
| `apps --platform ios` | 列出用户安装的应用（空白的模拟器显示为空）；添加 `--all` 以包括系统应用 |
| `install <appId> <path> --platform ios` | 安装本地 `.app`（上传它） |
| `install-from-source <url> --platform ios` | 从 URL 安装——虚拟机下载它（用于 EAS 实物） |
| `open <appId\|deep-link> --platform ios` | 启动应用（bundle id）或跟随应用的**深度链接**（`exp+slug://…`）。第一次深度链接会引发系统 **“在 '<app>' 中打开？”** 对话框——预期它会（不要浪费截图发现它）并 `press 'label="Open"'` 以转移；它可以很慢，因此使用 agent-device 自己的 `--timeout`（例如 `press 'label="Open"' --timeout 120000`）——**不是** shell `timeout` 包装（macOS 没有 `timeout` 二进制文件）。（Mode C 通过“手动输入 URL”绕过此对话框，见 run-your-app.md。）**不**用于 `webPreviewUrl`——那是用户的浏览器预览，永远不会是设备。 |
| `snapshot -i` | 交互式可访问性树 → `@e1`-样式的引用 |
| `press <ref\|selector>` | 点击（例如 `press @e2` 或 `press 'label="Open"'`）——**点击动词是 `press`，不是 `tap`** |
| `fill <ref> "text"` | 在字段中输入文本 |
| `screenshot <path>` | 将屏幕捕获到本地 PNG（从守护程序下载）——需要先打开应用 (`open` 第一个） |
| `record start` / `record stop <path>` | 将屏幕录制为视频——使用此功能进行**运动**（动画、手势、过渡、时间），单个截图无法捕获的任何内容 |
| `metro prepare` / `metro reload` | 指定开发客户端到 Metro / 重新加载（Mode C） |

**截图与视频。** 默认使用 `screenshot` 进行静态状态，但对于任何移动内容——动画、过渡、手势、时间/卡顿问题——**录制视频并检查帧**；静止图像无法证明运动。两个控制器都记录（agent-device `record start`/`stop`、argent `screen-recording-start`/`stop`）。录制以约 30fps 采样——足够看到可见的卡顿，但不能证明亚帧 60/120Hz 抖动。对于**时间**特定而言，argent 默认丢弃静态帧（关闭 `trimStatic`）——加上其他每个控制器的怪癖，都在 [references/controllers.md](./references/controllers.md) 中。

对于完整的动词集和 `argent` 控制器替代方案，请参阅 [references/controllers.md](./references/controllers.md)。

## 操作原理

值得内化的非明显心理模型。具体的错误→修复查找（挂起的动词、`tap`→`press`、`--platform`、`--json`、`pod install` 区域设置、孤立的会话、启动可变性）都生活在 [references/troubleshooting.md](./references/troubleshooting.md) 中。

1. **建立真实情况，然后重置——不要补丁循环。** 永远不要假设现有的会话或 Metro 是您的或健康的。在驱动之前，请确认：
   - **cwd** — 您位于预期的 Expo 项目目录中（一个误导向的 `start`/`exec` 会话将*错误的 App* + 丢弃一个随意的 `.env.eas-simulator`；`pwd` / 检查 `app.json`）。
   - **会话活动** — `IN_PROGRESS` 通过 `simulator:get --json`（停止的会话保留其 id + `remoteConfig`，因此 dotenv 单独不足以证明）。
   - **Metro 在其自己的端口上** — 如果您在此会话中启动了它，则重用；否则在空闲端口上启动一个 (`--port <N>`，例如 8082)，不要杀死另一个服务器以回收 `:8081`（run-your-app.md）。
   - **构建符合意图** — 一个**发布构建无法热重载**；如果想要 live 编辑并且安装了发布构建，**安装开发构建，不要重新连接**。

   如果在您的**第一次**连接后当前代码没有渲染，停止触摸 live 状态：**重置到基线**（停止会话 → 清除 dotenv → 杀死您的 Metro）并重新做一次模式；第二次失败 → 停止并报告。永远不要原地重启 Metro，重新连接一次以上，重新构建原生客户端以修复 JS/连接问题，或在状态未知时显示预览 URL。 （一个守护程序掉落——`ERR_NGROK_3200` / `Remote daemon is unavailable`——是相同的：重置，不要重试。）
2. **`exec` 是一个包装器，不是驱动器。** `simulator:exec` 加载 `.env.eas-simulator` 并生成您传递的命令；设备动词来自控制器（`npx agent-device@latest`）。没有 `simulator:tap`。
3. **立即行动；不要闲置空闲会话。** 会话很短命——安装并驱动 `start` 后。闲置一个会话会释放隧道/守护程序（→ 重置，见 #1）。
4. **完成或失败时停止您创建的会话并重置 dotenv。** `--non-interactive` 在您的任务结束时不会停止会话。对于请求的 live 预览，按照上面的持续时间指导。在慢启动期间轮询现有会话；启动另一个会话会创建一个额外的会话并覆盖 dotenv 的会话 ID。
5. **仅截图正确的、新鲜的构建。** Mode C 仅在开发客户端连接到 Metro 后；A/B 仅从与当前源匹配的构建——重用预存在的构建是 #1 “我的编辑没有显示”的原因（见上面的构建警告）。（状态栏中的 `9:41` 是模拟器的默认值，不是陈旧。）
