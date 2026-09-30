---
name: eas-simulator
description: EAS服务（付费）。在EAS云端托管远程iOS/Android模拟器上运行和控制用户的应用。在运行任何`eas simulator:*`命令前请先阅读说明——它包含了此实验性API的当前语法。当用户需要无法在本地运行的模拟器时，请随时使用——例如“在云端模拟器上运行我的应用”、“使用eas simulator运行/安装/截图我的应用”、“我在Linux/Cursor上需要一台iOS设备”、“这台机器没有模拟器/无头CI”、“让代理点击并截图我的应用”、“在远程模拟器上测试我的开发版本并启用实时重载”、“将模拟器流式传输到我的浏览器”——即使他们没有明确提到“EAS模拟器”或“云端”。在没有本地模拟器的主机（Linux、CI、云端沙盒）上，它是默认选项；在macOS上，对于简单的“在模拟器上运行”命令，请勿自动触发——仅用于云端/远程/可共享的模拟器、缺少的iOS版本，或由代理驱动的会话。不适用于本地模拟器（expo run:ios、Xcode、Android Studio）、EAS构建/更新、网页预览或物理设备。
---

# EAS 模拟器

> **EAS 服务 - 适用费用。** EAS 模拟器是一个托管的 EAS 服务。会话使用受您账户的定价和限制约束。请参阅 https://expo.dev/pricing 获取当前条款。

EAS 模拟器在 EAS 基础设施上运行远程 iOS 模拟器或 Android 模拟器，您可以从您的机器上控制它——通过 CLI、通过 AI 代理（通过 `agent-device`）以及通过浏览器预览。它是解锁**无法在本地运行模拟器的环境**（Linux 盒子、云/后台代理如 Cursor Cloud）的钥匙，并允许代理在真实设备上验证更改，而不仅仅是推理代码。

`simulator:*` 命令是**实验性且隐藏的**，需要较新的 eas-cli（截至撰写时为 ≥ 20.3.0）——这就是为什么这个技能通过 `npx --yes eas-cli@latest` 运行所有内容的原因。标志和动词可能会更改；**相关子命令的 `--help` 输出具有权威性。**

## 使用场景

frontmatter `description` 承载了触发短语。简而言之：使用此功能将用户的 App 部署到**云**模拟器并与其交互——尤其是在 Mac 无或云/沙盒代理的情况下。**不**用于本地模拟器（`expo run:ios`、Xcode、Android Studio）、商店构建/签名（那是 EAS Build），或物理设备。对于 macOS 情况，请参阅下一节 *云与本地*。

## 云与本地：首先决定这一点

- **明确的云/远程/可共享请求**：在检查访问权限后，在任何主机上使用 EAS 模拟器。
- **通用模拟器请求**：在可用时使用合适的本地模拟器。如果主机无法运行请求的模拟器（例如，在 Linux 上运行 iOS 或云沙盒），在检查访问权限后使用 EAS 模拟器。非 macOS 主机可能仍然支持本地 Android 模拟器。
- 尊重明确的本地选择；适当地将任务交给 `expo run:ios` / Xcode / Android Studio。仅在请求的环境仍然模糊且影响任务时才进行澄清。

当用户请求 EAS 模拟器或云模拟器时，请在该请求和任何声明的预算内进行操作。解释适用的使用情况一次，并在会话中保留现有的授权。在超出声明的预算或超出请求的工作范围之前，请先询问。

## 前置条件

- **通过 `npx --yes eas-cli@latest …` 运行每个 `eas` 命令**——确保 CLI 新到足以包含 `simulator:*`（全局 `eas` 通常太旧），并且 `--yes` 跳过 npx 的提示。（如果 `eas --version` 是最新的，裸 `eas` 也很好。）
- **已认证。** 交互式机器 → `npx --yes eas-cli@latest login`。**云沙盒 / CI / 无头代理没有浏览器登录——在环境中设置 `EXPO_TOKEN`**（expo.dev → Account → Access Tokens）。无论哪种方式，都可以通过 `npx --yes eas-cli@latest whoami` 进行验证。
- 从 Expo **项目目录**中运行。一个新应用需要一次性设置：`npx --yes eas-cli@latest init` 创建/链接项目（当没有 `projectId` 时），如果缺失，则**在应用配置中设置 `ios.bundleIdentifier`**——新 `create-expo-app` 通常没有，并且 `prebuild`/`eas build` 需要它（没有它会提示或失败；例如 `dev.<owner>.<slug>`）。使用 `npx expo config --json` 阅读当前配置（它可能存在于 `app.config.js` 中）。第一次 Mode-C 运行很慢（原生构建）；后续运行会重用它。
- 一个控制器来驱动设备。此技能使用 **agent-device**（开源，MIT），通过 `npx agent-device@latest` 按需运行——没有全局安装的。**Appium** 和 **argent** 是替代的自动化接口；`web-preview-only` 没有自动化接口。请参阅 [references/controllers.md](./references/controllers.md)。
- **`.env.eas-simulator`** 由 eas-cli（不是此技能）编写/管理：它包含会话 ID（`EAS_SIMULATOR_SESSION_ID`）+ 守护程序 URL/**令牌**，因此 `get`/`stop`/`exec` 默认针对该会话（通常**省略 `--id`**；将 `--id <id>` 传递给目标另一个）。它包含一个**令牌 → 将其 git 忽略**（eas-cli 将其标记为“不要提交”，但可能不会添加忽略规则，并且新应用的 `.gitignore` 不会覆盖它——如果缺失，请添加 `.env.eas-simulator`）。
- **命令块假设 POSIX shell**（bash/zsh）——`printf`、`lsof`、`$(seq …)` 循环在 cmd/PowerShell 中无法运行。在 Windows 上，在 WSL 或 Git Bash 中运行它们，或者边走边翻译（`eas-cli`/`agent-device` 调用本身是跨平台的）。

## 会话生命周期

- `--max-duration-minutes N` 是硬性自动停止截止日期。当账户支持时自定义它；否则使用服务的默认会话限制。
- `--max-idle-time-minutes N` 在经过这么多非活动分钟后停止会话。省略意味着**没有空闲超时**：会话运行到其最大持续时间或显式停止。
- **仅通过 `agent-device` 和 `argent` 报告的活动会重置空闲计时器。** Appium 命令和浏览器预览活动不会重置它。对于 Appium 或用户驱动的浏览器预览，依靠最大持续时间而不是空闲时间来限制会话；当账户支持时，使用 `--max-duration-minutes` 自定义它。

## 首先检查可用性

EAS 模拟器是一个**有限访问**的 EAS 功能，仍在逐步推出中，因此它不会在所有账户上都启用。在启动会话之前检查访问权限；此只读命令不会创建会话。

```bash
npx --yes eas-cli@latest simulator:availability --json
# → {"available": true, ...}  启用 → 继续到核心循环
# → {"available": false, ...} 未启用 → 不要启动会话
```

如果它**未**可用，不要调用 `simulator:start`（它将失败）。相反，优雅地转移，以便您在不使用此技能的情况下继续取得进展：
- 告知用户他们的账户上尚未启用 EAS 模拟器——它很快就会到来。
- 回退到他们正常的本地路径以实现实际目标——`expo run:ios` / Xcode / Android Studio 用于本地模拟器/模拟器、EAS Build 或其他适合的内容。不要在云模拟器上卡住；请求几乎永远不会是“专门使用 EAS 模拟器”。

（如果 `simulator:availability` 不可识别，CLI 太旧——升级，或者将 `simulator:start` 从“此账户未启用”错误相同地处理：停止并回退。）

## 核心循环（始终相同）

会话是：**启动 → （安装您的应用）→ 驱动 → 停止。** `eas-cli` 拥有 *会话*；设备 *动词*（打开/点击/截图）来自控制器，`npx --yes eas-cli@latest simulator:exec` 为您运行它并加载会话的连接环境。

```bash
# 1. 启动会话（启动远程模拟器 + agent-device 守护程序；写入 .env.eas-simulator）。
# 如果 dotenv 指定了一个会话，首先使用 simulator:get --json 检查它。当它属于此运行时重用它；仅在它处于范围内且不再需要时停止它。IN_PROGRESS 会话可能有意并发，因此重置 dotenv 之前保留其 id/配置。
# 仅在选择如何处理现有会话后继续下方。
printf '# managed by eas-cli\n' > .env.eas-simulator   # 仅在解决任何活动会话后清除
npx --yes eas-cli@latest simulator:start --platform ios --type agent-device --non-interactive \
  --name "Checkout flow screenshots"   # 始终命名它——见 '始终命名会话'
#    然后确认它正在运行：simulator:get --json → 状态 IN_PROGRESS (run-your-app.md 中的有界轮询)。

# 2. 通过 `exec` 驱动它（加载会话环境，然后运行您给它的命令）。
#    agent-device 通过 npx 按需运行——没有全局安装的。
npx --yes eas-cli@latest simulator:exec npx agent-device@latest open <app-or-url> --platform ios
npx --yes eas-cli@latest simulator:exec npx agent-device@latest snapshot -i          # 交互式 UI 树 → @e1, @e2 引用
npx --yes eas-cli@latest simulator:exec npx agent-device@latest press @e2            # 点击一个引用（注意：'press'，不是 'tap')
npx --yes eas-cli@latest simulator:exec npx agent-device@latest screenshot ./shot.png

# 3. 停止会话并重置 dotenv。省略 --id 以针对 dotenv 会话。
npx --yes eas-cli@latest simulator:stop
printf '# managed by eas-cli\n' > .env.eas-simulator
```

要**实时观看**它，请将 `webPreviewUrl`（`start` 打印的）交给用户。所有当前会话类型都包括浏览器预览；`agent-device`、`appium` 和 `argent` 也提供自动化，而 `web-preview-only` 提供没有自动化接口。**此 URL 是用于 *用户的* 浏览器——您不能为他们打开它，并且它永远不会接触模拟器：**
- **"在这里打开它"（Cursor/VS Code）** → 将 URL 单独打印一行，并告诉用户打开 Simple Browser（`Cmd/Ctrl+Shift+P` → "Simple Browser: Show"）并粘贴它。然后**停止**：不要 shell out 到系统浏览器或 Cursor/VS Code URL 处理器，并且不要问“是否出现了一个标签页？”——您无法确认，转移已经完成。
- **永远不要在模拟器上 `open` `webPreviewUrl`。** 它是一个浏览器预览，不是深度链接，也不是 `agent-device open` 参数；将其路由到设备会渲染一个浏览器中的浏览器（一个真实的失败）。
- **无头代理**（无显示器）→ 仅将 URL 作为交付物返回。
- **保持它 alive 以供用户驱动** → 当支持时使用 `--max-duration-minutes N`，否则使用服务的默认限制。浏览器预览活动不会重置 `--max-idle-time-minutes`，因此空闲超时不是这种情况下的可靠生命周期边界。告诉用户会话何时过期，使用 CLI 报告的持续时间或过期时间。为请求的预览保持运行；当一次性任务完成时停止创建的会话。

`start` 还打印一个 job-run URL。

## 始终命名会话

在每次 `simulator:start` 上传递 `--name "<description>"`。名称出现在 `simulator:list`、`simulator:get` 和 expo.dev 上的 **模拟器会话** 页面中，它替换了每一行的通用标题。未命名的每一行都显示“模拟器会话”和一个随机 ID——一堵无法导航的相同条目墙。为**人类扫描该列表数天后的**命名，而不是在运行期间为自己命名。

写几行简单的文字说明会话的用途：

```bash
--name "Checkout flow screenshots"     # 您做了什么
--name "Dev build — dark mode fix"     # 您在测试什么
--name "Login repro for issue 412"     # 它存在的原因
```

规则：
- 从用户的请求中派生，而不是从模式或工具中派生。`Mode C session`、`agent-device ios` 和 `test` 一无是处。
- **长度：目标为 3–6 个词，约 40 个字符，并将 50 视为实用限制。** 它在一个窄表格列中渲染为单行标题，因此长名称会被截断。API 接受最多 **255 个字符**，并拒绝空/空白名称，但 255 是一个天花板，您永远不会接近，而不是一个目标。一个名词短语，没有句子。
- 在该预算内保持具体。当有票证或 PR 编号时，请包含它。
- **句子大小写：** 仅大写第一个单词，并将标识符保留为实际大小写（`Dev build for expo-router v4`，`Repro for EXPO-1234`）。它是一个行标题，因此没有标题大小写、没有全小写，也没有句号。
- **不要重复表格中已经显示的内容。** 每一行都显示会话 ID、平台、开始时间、持续时间和创建者——因此没有 ID、没有 `iOS`、没有日期、没有您的姓名。在那些列无法表达的内容上花费整个预算：目的。
- 如果用户命名它，请原样使用他们的名称。
- 会话是按运行划分的，因此为每个新运行命名。不要将旧名称用于不同的工作。

`--name` 比较新的 `simulator:start` 本身更新，因此较旧的已安装 `eas-cli` 可能会拒绝它。如果发生这种情况，通过 `npx --yes eas-cli@latest` 或升级运行；作为最后的手段，一次不带 `--name` 重试（会话未命名）。请参阅 [references/troubleshooting.md](./references/troubleshooting.md)。

## 一览命令

在使用非默认启动标志、机器可读/配置输出、列表过滤器或会话事件之前，查询已安装的 CLI 以获取完整的当前标志集：

```bash
# 将 `start` 替换为您即将运行的模拟器子命令。
npx --yes eas-cli@latest simulator:start --help
```

下面的示例涵盖了常见的流程；它们有意不是 CLI 表面的详尽副本。即使在从 `--help` 构建命令时，也要保留此技能的非明显行为指南——尤其是 [会话生命周期](#session-lifetime)。

| 命令 | 目的 |
|---|---|
| `npx --yes eas-cli@latest simulator:availability [--json] [--non-interactive]` | 检查访问权限而不创建会话。 |
| `npx --yes eas-cli@latest simulator:start --platform ios\|android --name "<description>" [flags]` | 创建会话；启动模拟器 + 选定的接口；默认写入 `.env.eas-simulator`；打印预览 + job-run URL。**始终传递 `--name`**。`--json` 不会抑制 dotenv；当不应写入文件时使用 `--out-config-type env`。 |
| `npx --yes eas-cli@latest simulator:exec <cmd> [args…]` | 加载 `.env.eas-simulator`，然后以该环境运行 `<cmd>`。通往控制器的桥梁。 |
| `npx --yes eas-cli@latest simulator:get [--id <id>] [--json] [--non-interactive]` | 会话状态 + 连接详细信息，包括会话名称。**使用此命令确认就绪**（见 *操作原则*）。 |
| `npx --yes eas-cli@latest simulator:list [filters] [--limit N] [--after <cursor>] [--json]` | 列出并分页项目会话；按状态、类型、平台、名称前缀和标签过滤。 |
| `npx --yes eas-cli@latest simulator:events [--id <id>] [--follow\|--json]` | 显示记录的活动事件；`--follow` 监控直到会话结束。 |
| `npx --yes eas-cli@latest simulator:stop [--id <id>] [--json] [--non-interactive]` | 停止会话（幂等）。 |

## 运行用户的 App — 选择一个模式

远程模拟器启动**空白——没有 Expo Go，没有应用。** 安装构建，然后驱动它——但**首先匹配构建 *类型* 与目标**（下方的框）；这是 live-session 运行偏离的地方。完整序列：[references/run-your-app.md](./references/run-your-app.md) — 在运行模式之前阅读。

> **在安装任何内容之前，先匹配构建与目标——这是 live-session 运行偏离的地方。** 两个陷阱，同一个根源（抓取不适合请求的构建）：
> 1. **类型错误。** live 编辑（Mode C）**需要开发构建。** 一个静态构建——本地发布（A）、默认 EAS 模拟器构建（B），或**从早期截图运行留在模拟器上的任何构建**——在构建时冻结其 JS，并且**永远无法热重载。** 对于 live 请求，**完全忽略现有构建**并安装**开发**构建（本地调试，或带有 `developmentClient: true` 的 EAS 构建）。永远不要将 Metro 连接到静态构建，希望它能够重载——它不会。
> 2. **过时。** 静态快照必须与当前源匹配——仅重用具有指纹匹配的构建，否则重新构建；显式仅重用。因此，遗留的 EAS/发布构建**不是**“迭代 live”的快捷方式——它是错误的二进制文件。构建存在的事实永远不会使其成为正确的选择。

| 模式 | 它是什么 | 选择何时 | live 编辑？ |
|---|---|---|---|
| **A — 本地发布构建** | 本地构建发布 `.app`，然后 `agent-device install` 它（上传） | 用户有 Mac 工具链，并希望快速“在云设备上运行我的当前代码” | 否（需要重新构建以查看更改） |
| **B — EAS 构建**（罕见，仅显式） | `eas build` 模拟器构建，`agent-device install-from-source <url>`（虚拟机下载它） | **仅在明确要求时**——用户命名现有/EAS 构建，或想要用于 CI/共享的静态 EAS 资产。不用于“显示给我”/“迭代”（使用 C）。模拟器构建不需要凭证。 | 否 |
| **C — 本地开发构建 + 隧道** | 开发（调试）构建 + `EXPO_UNSTABLE_TUNNEL_V2=1 expo start --tunnel` + 连接开发客户端到 Metro | **代理编辑和查看循环**——更改代码并实时查看（快速刷新） | **是** |

快速决策——**默认选择C；A和B仅用于显式操作：**
- **C（几乎 everything）：** 迭代、交互、调试应用、实时编辑——并且大多数“显示我的应用”（当前代码需要构建，所以实时+当前更优）。Mac → 开发客户端本地构建；无Mac → 在EAS上构建（`developmentClient: true`）。**不确定 → C。**
- **A：** 仅在Mac上执行一次**静态**截图。
- **B：** 仅在用户命名现有/EAS构建或需要静态EAS工件（CI/共享）时使用——见上方框内原因，静态构建不适合“迭代。”

在开始C模式隧道或连接开发客户端之前，请阅读[Tunnel scope and approvals](./references/run-your-app.md#tunnel-scope-and-approvals)。通过隧道创建、连接和实时编辑，携带此项目的远程开发传输的现有授权；在审批请求中包含其来源和具体数据流。

## 驱动设备（agent-device）

如果控制器未能下载录制内容，请从[EAS session artifacts](./references/controllers.md#recording-download-recovery)中检索。

`agent-device`是控制器。常用动词（每个都作为`npx --yes eas-cli@latest simulator:exec npx agent-device@latest <verb>`运行）：

| 动词 | 执行 |
|---|---|
| `apps --platform ios` | 列出用户安装的应用（空白模拟器显示无）；添加`--all`以包含系统应用 |
| `install <appId> <path> --platform ios` | 安装本地`.app`（上传它） |
| `install-from-source <url> --platform ios` | 从URL安装——虚拟机下载它（用于EAS工件） |
| `open <appId\|deep-link> --platform ios` | 启动应用（bundle id）或跟随应用**深度链接**（`exp+slug://…`）。首次深度链接会触发系统**“在'<app>'中打开？”**对话框——预期它会（不要浪费截图发现它）并`press 'label="Open"'`以转交；它可能很慢，因此使用agent-device的`--timeout`（例如`press 'label="Open"' --timeout 120000`）——**不是**shell的`timeout`包装（macOS没有`timeout`二进制文件）。（C模式通过“手动输入URL”绕过Metro连接链接的此对话框——见run-your-app.md。）**不**用于`webPreviewUrl`——那是用户的浏览器预览，永远不会是设备。 |
| `snapshot -i` | 交互式无障碍树 → `@e1`样式引用 |
| `press <ref\|selector>` | 点击（例如`press @e2`或`press 'label="Open"'`）——**点击动词是`press`，不是`tap`** |
| `fill <ref> "text"` | 在字段中输入文本 |
| `screenshot <path>` | 将屏幕捕获到本地PNG（从守护进程下载）——需要先打开应用（先`open`） |
| `record start` / `record stop <path>` | 将屏幕录制为视频——用于**运动**（动画、手势、过渡、计时），单个截图无法捕获 |
| `metro prepare` / `metro reload` | 指向Metro/重新加载（C模式） |

**截图与视频。** 默认使用`screenshot`进行静态状态，但对于任何移动内容——动画、过渡、手势、计时/卡顿问题——**录制视频并检查帧**；静态图像无法证明运动。两个控制器都记录（agent-device `record start`/`stop`，argent `screen-recording-start`/`stop`）。录制以~30fps采样——足以看到可见卡顿，但不能证明亚帧60/120Hz抖动。对于**计时**特别，argent默认丢弃静态帧（关闭`trimStatic`）——加上其他每个控制器的特定问题，都在[references/controllers.md](./references/controllers.md)。

有关完整动词集和`argent`控制器替代方案，请参阅[references/controllers.md](./references/controllers.md)。

## 应用崩溃时：设备日志和崩溃报告（iOS）

当应用崩溃或在启动时关闭时，在从截图猜测之前，请阅读iOS会话的崩溃报告和设备日志。从`simulator:get --json`中的预览API URL读取它们。该URL包含会话令牌，因此切勿打印它。

**在复现崩溃之前保留设备日志。** 没有保留，崩溃会生成报告但空的日志尾部。命令、字段和备用方案在[references/logs-and-crashes.md](./references/logs-and-crashes.md)。

## 运行原则

值得内化的非显而易见的思维模型。特定错误→修复查找（挂起的动词、`tap`→`press`、`--platform`、`--json`、`pod install`区域设置、孤立的会话、启动可变性）位于[references/troubleshooting.md](./references/troubleshooting.md)。

1. **建立真实情况，然后重置——不要打补丁循环。** 假设现有会话或Metro是您自己的或健康的。在驾驶前确认：
   - **cwd** — 您位于预期的Expo项目目录（错误的`start`/`exec`会话*错误的应用* + 丢弃一个随意的`.env.eas-simulator`；`pwd` / 检查`app.json`）。
   - **session live** — `IN_PROGRESS`通过`simulator:get --json`（停止的会话保留其id + `remoteConfig`，所以dotenv本身不是证据）。
   - **Metro在其自己的端口上** — 仅当您在此会话中启动它时才重用；否则在空闲端口上启动一个（`--port <N>`，例如8082），不要杀死另一个服务器以回收`:8081`（run-your-app.md）。
   - **构建符合意图** — **发布构建不能实时重新加载**；如果需要实时编辑且已安装发布构建，**安装开发构建，不要重新连接**。

   如果当前代码在您的**首次**连接后未渲染，停止触摸实时状态：**重置为基准**（停止会话 → 清除dotenv → 杀死您的Metro）并重做模式**一次**；第二次失败 → 停止并报告。切勿原地重新启动Metro，连接超过一次，重新构建原生客户端以修复JS/连接问题，或在状态未知时显示预览URL。（守护进程掉线——`ERR_NGROK_3200` / `Remote daemon is unavailable`——也是这样：重置，不要重试。）
2. **`exec`是一个包装器，不是驱动器。** `simulator:exec`加载`.env.eas-simulator`并生成您传递的命令；设备动词来自控制器（`npx agent-device@latest`）。没有`simulator:tap`。
3. **立即行动；不要闲置空闲会话。** 会话是短命的——安装后立即驾驶。闲置一个会话会释放隧道/守护进程（→ 根据第1点重置）。
4. **在完成或失败时停止您创建的会话并重置dotenv。** `--non-interactive`在您的任务结束时不会停止会话。对于请求的实时预览，请遵循上述持续时间指导。在慢启动期间轮询现有会话；启动另一个会话会创建一个额外的会话并覆盖dotenv的会话id。
5. **仅截图正确的、新鲜构建。** C模式仅在开发客户端连接到Metro后；A/B仅从与当前源匹配的构建——重用预现有构建是#1“我的编辑未显示”的原因（见上述构建注意事项）。（状态栏中的`9:41`是模拟器的默认值，不是陈旧。）

## 停止并清理

完成任务后，停止您创建的会话**并重置dotenv**，以便后续运行不会尝试重用死会话。对于请求的实时预览，在约定的持续时间內保持其可用性：

```bash
npx --yes eas-cli@latest simulator:stop          # 省略--id → 停止dotenv会话（或传递--id <id>）
printf '# managed by eas-cli\n' > .env.eas-simulator   # 清除陈旧的会话id，以免被重用
# 如果您为C模式启动了Metro，也停止它（在其终端中按Ctrl+C，或杀死expo进程）
```

## 参考

- [references/run-your-app.md](./references/run-your-app.md) — 模式A、B和C的完整命令序列（在运行模式前阅读）。
- [references/controllers.md](./references/controllers.md) — agent-device动词参考和`argent`替代方案。
- [references/logs-and-crashes.md](./references/logs-and-crashes.md) — iOS会话的设备日志和崩溃报告（应用崩溃或行为异常时阅读）。
- [references/troubleshooting.md](./references/troubleshooting.md) — 具体错误和修复。

真实来源：Expo文档和`eas` / `agent-device` CLI（`npx --yes eas-cli@latest simulator:* --help`，`agent-device --help`）。这项技能教您如何应用它们；它不会取代它们。

## 提交反馈
如果您遇到错误、误导性或过时的信息，请报告它，以便Expo可以改进：
```bash
npx --yes submit-expo-feedback@latest --category skills --subject "eas-simulator" "<可操作的反馈>"
```
仅在您有具体且可操作的反馈时才提交。尽可能包含所有相关上下文。
如果AI代理反复失败或用户不得不接管Expo任务，加载expo-skill-feedback技能并遵循其eval-candidate流程，而不是重复使用上面的命令。
