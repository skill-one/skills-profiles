---
name: unity-cli
description: 控制 Unity 编辑器和从命令行启动项目，用于编辑场景和资源或运行 C#。在需要安装或管理编辑器、许可证或项目，设置版本控制，构建，测试，配置 Unity MCP 服务器或运行任何 Unity 命令时使用。
---

# Unity CLI

## 驱动正在运行的 Unity 编辑器（如果已打开）

**如果这台机器上打开了 Unity 编辑器，此 CLI 可以实时控制它** — 创建和修改 GameObjects，编辑场景和资源，检查层级结构，以及运行任意 C# — 通过项目的 **Pipeline** 包 (`com.unity.pipeline`)。这完全在您的本地机器上运行，在您自己的用户账户中，针对您自己打开的编辑器：它不是远程访问，也不授予您在终端上没有的任何权限。当编辑器可用时，驱动它而不是手动编辑场景或资源文件。

```bash
unity status                    # 确认连接的编辑器（查找状态 "ready"）
unity command                   # 列出编辑器暴露的命令
unity command editor_play       # 运行一个 — 例如，进入 Play 模式
# 当编辑器暴露 eval 时运行任意 C# — 例如，添加一个名为 "Joe" 的 GameObject —
unity command eval 'new UnityEngine.GameObject("Joe");'
```

### 打开多个编辑器？传递 `--project-path`

每个驱动编辑器的命令都接受 `--project-path <path>`。**当可能打开多个编辑器时，请始终传递它** — 没有它，CLI 会针对包含当前目录的项目中的编辑器，因此目标跟随 shell 的 cwd：

```bash
unity command editor_play --project-path /path/to/MyProject
```

一个 `unity status` 实例的 `project` 字段是 `--project-path` 接收的。对于 `unity command`/`list`/`job`/`mcp`，匹配没有运行的项目会失败并显示 `AMBIGUOUS_EDITOR`，并列出候选者。[详细信息](references/integration-advanced.md#targeting-one-of-several-running-editors)。

需要项目的 `com.unity.pipeline` 包（Unity 6.0+） — 使用 `unity pipeline install` 一次性添加它。完整详细信息 — 启动无头编辑器进行驱动，`unity list` 工具发现，以及编写自定义 `[CliCommand]` 工具 — 在 [integration-advanced.md](references/integration-advanced.md) 中。

该包还附带一个更深层的 `unity-pipeline` agent 技能，对 `Library/PackageCache` 中的客户端不可见 — 在包含该包的项目中，运行 `unity skill install <client> --local` 一次性将其镜像到此技能旁边。

> **无法连接 / 命令超时？首先检查安全模式。** 当项目有 C# 编译错误时，编辑器会启动到 **安全模式**，其中 Pipeline 包不会加载 — 因此 `unity command`、`unity status` 和 `unity list` 完全无法连接。不要退回到盲目的文件编辑：运行 `unity pipeline list` 进行确认，然后修复编译错误并重新启动 Unity。完整恢复循环在 [integration-advanced.md → 从安全模式恢复](references/integration-advanced.md#recovering-from-safe-mode-connection-fails-because-of-compile-errors)。

> **作为沙盒编码代理运行，并且 `unity status` 报告没有实例？** 严格的沙盒可能会隐藏此 CLI 视图中的真正正在运行的编辑器 — 不要单独将其视为编辑器已关闭的证据。完整详细信息在 [integration-advanced.md → 沙盒代理工具可以隐藏正在运行的编辑器](references/integration-advanced.md#sandboxed-agent-tooling-can-hide-a-running-editor)。

## 安装 CLI（如果尚未安装）

首先检查是否可用：

```bash
which unity && unity --version
```

如果未找到，请安装它：

**macOS / Linux**
```bash
curl -fsSL https://public-cdn.cloud.unity3d.com/hub/prod/cli/install.sh | UNITY_CLI_CHANNEL=beta bash
```

**Windows (PowerShell)**
```powershell
$env:UNITY_CLI_CHANNEL='beta'; irm https://public-cdn.cloud.unity3d.com/hub/prod/cli/install.ps1 | iex
```

安装后，打开一个新的 shell，以便 `unity` 在 PATH 中，然后使用 `unity --version` 进行验证。如果安装脚本失败或二进制文件仍然找不到，请通知用户并停止；如果命令本身因权限错误或崩溃而失败，则安装可能已损坏 — 建议重新运行安装脚本。

---

## 全局标志

这些标志适用于每个命令：

| 标志 | 描述 |
|---|---|
| `--format <fmt>` | 输出格式：`human`（默认）、`json`、`tsv`、`ndjson`、`github`。也通过 `UNITY_FORMAT` 环境变量。 |
| `--json` | 全局简写，表示 `--format json`，在所有命令中都接受（例如 `unity status --json`，`unity doctor --json`）。当两者都提供时，`--format` 优先。 |
| `--no-banner` | 抑制品牌页眉 — 用于脚本 |
| `--no-pager` | 关闭分页。控制两个分页器：外部分页器用于长列表（`unity command`、`releases`、`editors`、`changelog`、`logs`）和交互式分页器在 `unity projects list` 中。也通过 `UNITY_NO_PAGER`（基于存在 — 任何值，包括 `0`，都会禁用它）。 |
| `--non-interactive` | 禁用所有交互式提示 — 用于 CI |
| `--quiet` | 抑制非必要输出 |
| `--verbose` | 在失败时打印完整错误详细信息（堆栈跟踪 + 原因链）。也通过 `UNITY_VERBOSE`。 |
| `--proxy <url>` | 此调用的 HTTP/HTTPS/SOCKS/PAC 代理 URL。也通过 `UNITY_PROXY`。优先于标准的 `HTTPS_PROXY`/`HTTP_PROXY`/`ALL_PROXY` 环境变量和持久化的 `proxy.json` 设置。 |
| `--proxy-disable` | 禁用此调用的代理，忽略所有来源（环境变量、持久化配置、系统设置）。 |
| `--log-proxy` | 将每个出站请求的一个脱敏条目记录到 `proxy-request.json` — 用于重现代理问题。也通过 `UNITY_LOG_PROXY=1` 或 `proxyRequestLogging` 设置。 |
| `--no-log-proxy` | 当全局启用时，使单个调用从代理请求日志记录中排除。 |
| `--color <auto\|always\|never>` | 控制此调用的彩色输出，覆盖 `NO_COLOR`/`FORCE_COLOR` 和 TTY 自动检测。控制每个发出 ANSI 代码的表面（帮助、表格、旋转器、错误），而不仅仅是 `human` 输出。 |
| `--no-color` | `--color never` 的简写。无论 `--color`/`--no-color` 在行上出现得最后，哪个都会生效。 |

**当您需要以编程方式解析输出时，始终使用 `--format json`。**

`--accelerator <host:port>` 和 `--no-accelerator` 不是 **根全局** — 它们仅在 `run`、`test` 和 `build` 上接受，并且仅在命令名称之后接受。请参阅 [build-run-test.md](references/build-run-test.md)。

**`unity projects list` 是唯一分页 IN-PROCESS 的命令。** 它每屏显示 10 个项目，并在屏幕之间等待按键，并且只有在 stdout 是终端时才会这样做。分页关闭用于重定向的 stdout、`--format json` 和 `--format ndjson`，以及 `--all`、`--watch` 或 `--no-pager` / `UNITY_NO_PAGER`。

**并非每台机器格式都会绕过分页。** 只有 `json` 和 `ndjson` 会获得自己的非交互式渲染；在终端上，`--format tsv` 和 `--format github` 会像 `human` 一样绕过分页器 — 因此 TTY 上的 `--format tsv` 既不会生成 TSV 也不会生成未分页的输出。重定向 stdout（机器格式的通常情况）或传递 `--no-pager`。请注意，这是 **相反** 的，外部分页器仅限于 `human`：这两个机制在此处不同，`projects list` 是令人惊讶的一个。

**长列表通过外部分页器分页，就像 `git log`。** `unity command`（纯列表）、`unity releases`、`unity editors`、`unity changelog` 和 `unity logs` 将人类输出通过终端上的 `less -RFX` 分页 — 保留颜色，不清屏，并且 `-F` 在输出已经适合一屏时自动退出，因此短列表不会显示分页器 UI。`$UNITY_PAGER` 然后 `$PAGER` 覆盖选择并在 shell 中运行，因此 `PAGER="less -S"` 有效；空值会被忽略，而不是被视为放弃。使用 `q` 退出会以命令自己的退出码干净退出。与 `projects list` 的分页器不同，这个分页器是 **`human` 仅限** 的，并且永远不会为重定向的 stdout、任何机器格式（`json`、`tsv`、`ndjson`、`github`）、`--quiet`、`TERM=dumb`、流式模式（`editors --watch`、`logs --follow`）、命名的 `unity command <name>` 或在 `unity shell` 中触发。一个损坏的分页器会导致分页失败，而不是输出失败：`$PAGER` 指向不存在的东西会在任何东西生成之前解决，并且一个生成后立即死亡的分页器会将其输出重新打印到终端，这取决于分页器的退出状态（干净退出是一个正常的 `q` 并丢弃；失败状态会重新打印）。例外是一个分页器在成功退出之前没有读取 — `PAGER=true`，或者任何在退出前停留并退出 0 的情况 — 没有什么可以将其与 `q` 区分，并且 `git` 也失去了它。一个分页器启动并仅仅是等待，不会被处理为损坏，因此 CLI 会等待它。

一个带有品牌 Unity 页眉（标志、品牌名称、CLI 版本）在着陆表面渲染 — 纯 `unity`、`unity --help` / `-h`、`unity help`，以及第一次运行同意提示符上方。它仅在 TTY 上显示，最多打印一次，并在窄终端上退化为一行紧凑的未着色文本，没有 Unicode，或在 `NO_COLOR` 下。管道输出不受影响。在脚本中使用 `--no-banner` 来抑制它。纯 `unity` 打印用法并退出 0。

## 环境变量

所有 CLI 环境变量都使用 `UNITY_` 前缀。CLI 标志始终覆盖相应的环境变量。

| 变量 | 映射标志 | 描述 |
|---|---|---|
| `UNITY_FORMAT` | `--format` | 输出格式 (`human`、`json`、`tsv`、`ndjson`、`github`)。`HUB_FORMAT` 是一个已弃用的别名。 |
| `UNITY_EDITOR_VERSION` | `--editor-version` | 编辑器版本（例如 `2023.3.0f1`、`latest`、`lts`）。 |
| `UNITY_ARCHITECTURE` | `--architecture` | 芯片架构 (`x86_64`、`arm64`)。 |
| `UNITY_PROJECT_PATH` | path 参数 | 项目路径 — 用于 `open`，并且 `status` 和云命令也认可它。 |
| `UNITY_QUIET` | `--quiet` | 抑制非必要输出。 |
| `UNITY_VERBOSE` | `--verbose` | 在失败时显示完整错误详细信息。 |
| `UNITY_NON_INTERACTIVE` | `--non-interactive` | 禁用交互式提示。 |
| `UNITY_NO_BANNER` | `--no-banner` | 抑制品牌横幅。 |
| `UNITY_NO_PAGER` | `--no-pager` | 关闭分页 — 两个分页器：外部分页器用于长列表和 `unity projects list` 的交互式分页器。基于存在：任何值都有效，包括 `0`。 |
| `UNITY_PAGER` | — | 用于长列表的分页器，覆盖 `$PAGER` 和 `less -RFX` 默认值。通过 shell 运行，因此标志有效 (`less -S`)。空值会被忽略，不是放弃。 |
| `PAGER` | — | 与 `UNITY_PAGER` 相同，仅在后者未设置或为空时查询。 |
| `LESS` / `LV` / `LESSCHARSET` / `MORE` | — | 仅当您未设置它们时才传递给分页器，默认为 `FRX`、`-c`、`utf-8` 和 `FRX`。`LESSCHARSET` 保留多字节字形在区域设置未声明 UTF-8 的情况下可读；`MORE` 存在是因为 macOS/BSD 上的 `more` 是 `less` 的另一个名称，并且读取 `$MORE`，因此如果没有它，`PAGER=more` 即使对于一行也会等待按键。 |
| `UNITY_RUN_TIMEOUT` | `--timeout` | `unity run` 的超时时间（秒）。 |
| `UNITY_TEST_TIMEOUT` | `--timeout` | `unity test` 的超时时间（秒）。 |
| `UNITY_CLOUD_ORG` | `--cloud-org` | 单次调用中活动的 Unity Cloud 组织 id 或名称。 |
| `UNITY_SERVICE_ACCOUNT_ID` | — | 非交互式（CI）认证的服务账户客户端 ID。 |
| `UNITY_SERVICE_ACCOUNT_SECRET` | — | 非交互式（CI）认证的服务账户客户端密钥。 |
| `UNITY_PROXY` | `--proxy` | HTTP/HTTPS/SOCKS/PAC 代理 URL。优先于 `HTTPS_PROXY`/`HTTP_PROXY`/`ALL_PROXY` 和持久化的 `proxy.json` 设置。 |
| `UNITY_NO_UPDATE_CHECK` | — | 禁用背景“有更新可用”检查（参见 `unity config update-check`）。 |
| `UNITY_NO_CONSENT_PROMPT` | — | 抑制一次性首次运行分析同意提示符 *而不* 记录选择 — 用于在交互式终端上运行的包装脚本，这些脚本绝对不能吸收提示符。分析功能直到您运行 `unity analytics opt-in` 才会关闭。与 `UNITY_NON_INTERACTIVE` 不同，它不会改变命令行为的任何其他方面。 |
| `UNITY_NO_CRASH_REPORT` | — | 完全禁用匿名崩溃/错误报告（Sentry）。 |
| `UNITY_LOG_PROXY` | `--log-proxy` | 将每个出站请求的一个脱敏条目记录到 `proxy-request.json`。真值：`1`、`true`。 |
| `UNITY_ACCELERATOR` | `--accelerator` | Unity Accelerator 端点 (`host:port`)。优先于持久化的 `accelerator.json`；`--accelerator` 优先。 |
| `UNITY_NO_ELEVATE` | `--no-elevate` | Windows：跳过 `install` / `install-modules` 的提升（UAC）安装辅助程序，因此安装服务以非提升方式运行。编辑器的 NSIS 安装程序如果 Windows 要求您的账户进行提升，仍然会按需请求提升 — 管理员令牌始终会；标准用户永远不会。 |
| `UNITY_INSTALL_RETRIES` | `--retries` (`install-modules` 仅限) | `install` 和 `install-modules` 重试下载失败或验证失败的项目编辑器或模块的次数。`0` 禁用重试；`unity install` 没有 `--retries` 标志，因此在此处设置变量。 |
| `UNITY_NO_AUTH_BROKER` | — | 跳过驻留认证代理，直接从操作系统密钥环读取凭证。默认情况下，需要令牌的每个命令都通过一个在按需启动并在两分钟后退出（参见 [auth-license-cloud.md](references/auth-license-cloud.md)）的代理。 |
| `UNITY_PEER_AUTH_MODE` | — | 认证代理和编辑器身份辅助程序如何验证连接进程的代码签名。`enforce` 是 macOS 和 Windows 上的默认值：未签名或非 Unity 签名的对等方会被拒绝。`identify-only` 会在不拒绝的情况下记录 — 用于从源代码构建的编辑器。Linux 仅记录，除非与 `UNITY_PEER_AUTH_LINUX_ALLOWED_HASHES`（逗号分隔的 SHA-256 签名，用于受信任的可执行文件）一起设置为 `enforce`。 |
| `UNITY_CLI_HOME` | — | 安装脚本和 `unity self-install` 的安装根，在所有平台上包括 Windows：二进制文件位于 `<UNITY_CLI_HOME>/bin` 而不是默认位置。 |
| `UNITY_NO_EDITOR_IDENTITY_SERVER` | — | 禁用 `unity open` 启动以回答编辑器登录查找的背景身份辅助程序，当没有 Hub 运行时（参见 [projects-templates.md](references/projects-templates.md)）。基于存在。 |

**CI 服务账户认证：** 将 `UNITY_SERVICE_ACCOUNT_ID` 和 `UNITY_SERVICE_ACCOUNT_SECRET` 都设置为跳过浏览器 OAuth 流 — 这会将密钥从进程参数列表和 shell 历史记录中排除。这些映射到 `unity auth login` 的 `--client-id` / `--secret-from-stdin` 输入，但从环境中读取凭证并不是完整的登录：它不会运行交互式流程或将凭证保存在密钥环中。

## 获取帮助

在任何级别将 `-h` 或 `--help` 追加到任何命令或子命令：`unity --help`，`unity projects create --help`。

## 退出代码

| 代码 | 含义 |
|---|---|
| 0 | 成功 |
| 1 | 一般错误 |
| 2 | 命令行参数错误 |
| 3 | 认证失败 |
| 4 | 预条件未满足（例如，没有许可证激活，浮动服务器未配置） |
| 6 | 命令特定失败 |
| 8 | `unity test` 仅限 — 测试运行了，并且一个或多个 **失败**。测试运行失败的任何其他方式（编译错误、许可证不可用、编辑器崩溃、`--timeout`）保持 `6`，因此 CI 可以重试基础设施故障，但永远不会重试失败的测试。 |
| 130 | 被中断 — Ctrl+C / SIGINT (128 + 2) |
| 143 | 被 SIGTERM 终止 (128 + 15) — 例如 `kill` 或 CI/runner 超时。由长时间运行的命令发出，这些命令安装了一个信号处理程序以首先清理（目前是 `unity build`，它会清理临时的 Android keystore）。 |

`cloud` 和 `auth` 命令将认证失败（会话过期/缺失、拒绝登录）映射到 `3`，并将任何其他操作失败（网络、服务器错误）映射到 `6` — 因此脚本可以可靠地区分“重新登录”和真正的命令失败。

命令的完整参考——语法、标志和示例——位于分组文件下 [`references/`](references/)。**请阅读您需要的命令组的文件**；上面提到的所有全局标志、环境变量和退出代码在整个范围内都适用。每个命令也支持 `-h` / `--help`（参见 [获取帮助](#getting-help)）。

| 命令 | 参考文件 |
|---|---|
| `auth` (登录 / 注销 / 状态 / 列表 / 切换 / 默认 / 消费者 / 撤销), `license` (激活 / 返回 / 服务器), `cloud` (组织 / 项目) | [auth-license-cloud.md](references/auth-license-cloud.md) |
| `editors` (列表 / 运行中 / 添加 / 默认 / 路径 / 安装路径 / 信息 / 升级 / 修剪 / 验证 / 模块), `install`, `uninstall`, `modules`, `install-modules` | [editors-install.md](references/editors-install.md) |
| `projects` (列表 / 创建 / 新建 / 克隆 / 打开 / 链接 / 需要 / 升级 / 导出 / 导入 / 固定 / 大小 / 清理 / 执行), `releases`, `templates` (列表 / 信息 / 创建 / 打包 / 删除), `assets` (`inspect`) | [projects-templates.md](references/projects-templates.md) |
| `config` (代理 / 更新检查 / 加速器 / 获取 / 设置 / 列表 / 取消设置 / 解析), `context` (保存 / 使用 / 列表 / 当前 / 删除), `hub install` | [config-hub.md](references/config-hub.md) |
| `run`, `test`, `build` (+ `build run`), `watch` (`test`) | [build-run-test.md](references/build-run-test.md) |
| `logs`, `doctor`, `env`, `version`, `cache`, `ci init`, `analytics`, `changelog`, `language`, `completion`, `bug`, `self-update`, `self-uninstall`, `diagnose proxy`, `diagnose accelerator` | [diagnostics-maintenance.md](references/diagnostics-maintenance.md) |
| `mcp` (+ `configure`), `skill` (安装 / 刷新 / 显示), `plugin` (安装 / 移除 / 升级 / 列表 / 更改日志), 连接的编辑器 (`pipeline` / `command` / `commands` / `状态` / `列表`), `shell` | [integration-advanced.md](references/integration-advanced.md) |
| `vcs` — `setup` / `状态` / `同步` / `切换` / `doctor` / `提供者` / `合并设置` / `冲突` / `解释` / `解析` / `差异` / `归因` / `钩子`, `vcs git` (`migrate-lfs` / `worktree`), `vcs uvcs` (`锁` / `变更集` / `评审`) | [版本控制.md](references/version-control.md) |
| `collaboration` (别名 `collab`) — `注释` / `附件` / `缩略图` / `反应` / `阅读` / `订阅` / `jira` | [collaboration.md](references/collaboration.md) |

## 常见工作流

### 编辑场景、GameObject 或资源——首先运行 `unity status`

**在编辑任何场景、GameObject、预制件或资源之前，运行 `unity status` 来检测连接的编辑器。** 如果有一个可访问的编辑器，请使用实时命令来驱动它，而不是触摸项目文件——编辑器将更改应用于*实际的活动场景*并保持其内存状态同步。

```bash
unity status                       # 是否连接了编辑器？（查找状态 "ready"）
unity command                      # 发现此编辑器公开的场景/GameObject 命令
# 然后使用它列出的命令来驱动它——例如，如果您的编辑器公开了它们：
unity command create_gameobject    # 对实时、活动的场景采取行动
unity command save_scene           # 持久化活动场景
```

命令名称由编辑器定义，因此运行 `unity command`（或 `unity list`）以查看确切的一组——不要假设名称。

> **在实时编辑器可访问时，切勿手动编辑 `.unity`、`.prefab` 或 `.asset` YAML。** 原始文件编辑：
> - **容易出错**——文件ID和GUID由手动分配，容易出错；
> - **对正在运行的编辑器不可见**，直到重新导入，因此更改无声地失败；
> - **容易击中错误的文件**——例如，在编辑器的活动场景实际上是 `Demo2.unity` 时写入 `SampleScene.unity`，生成看起来有效的 YAML，但用户看不到任何变化。

**在得出没有编辑器可访问的结论之前，排除两种假阴性——两者都与真正关闭的编辑器看起来相同，并且在时间压力下很容易出错：**

- **安全模式。** 如果编辑器*确实*正在运行此项目，但 `unity status` / `unity command` 无法连接，它可能由于编译错误而卡在**安全模式**，而不是真正消失。运行 `unity pipeline list`——如果它报告安全模式，编辑 C# 源代码以修复编译错误（然后重新启动 Unity）*就是正确的做法*，而不是备用方案。参见 [integration-advanced.md → 从安全模式恢复](references/integration-advanced.md#recovering-from-safe-mode-connection-fails-because-of-compile-errors)。
- **沙盒化的代理 shell。** 如果您自己的 shell 命令在限制性沙盒内运行——这对于像这样这样的编码代理来说是正常情况——沙盒可以像隐藏真正运行的编辑器一样隐藏 `unity status`。这适用于**每个**到达此预检的场景/GameObject/预制件/资源任务，而不仅仅是明显需要实时编辑器完成的任务：您原本可以无需任何 CLI 参与就能完成的任务（例如，通过普通编辑器 API 生成资源）仍然可以在这里被路由到“没有编辑器”，并且会被中断。不要将“没有实例”视为编辑器已关闭的证据，也不要悄悄地编造第三条路径——例如，驱动一个单独的无头编辑器进程来模拟实时连接会做什么——作为披露文件编辑的替代方案。明确说明您的沙盒可能正在阻止您看到真实的编辑器，并在回退之前询问是否实际打开了编辑器。详细信息：[integration-advanced.md → 沙盒代理工具可以隐藏正在运行的编辑器](references/integration-advanced.md#sandboxed-agent-tooling-can-hide-a-running-editor)。

只有在排除了以上两者之后，才直接编辑文件——并明确说明（“检测不到实时编辑器，直接编辑文件”）。

### 从头开始引导一个新项目

> 对于**引导式**端到端体验——概念问题、在您规划时在后台安装编辑器、包选择和变现交接——请使用 **`new-unity-project`** 技能。本节是技能构建的原始 CLI 配方；当您只想使用命令时，请直接使用它。

仅使用 CLI 将想法转化为运行中的、版本控制的项目。首先决定**目标平台**——它们决定了在步骤 2 中您需要安装哪些编辑器模块。您可以稍后添加模块（`unity install-modules`），但项目不能为平台构建，直到该平台的模块已安装，因此最简单的方法是事先决定。

```bash
# 1. 确认 CLI 正常工作，并且您已登录并拥有许可证（参见 references/auth-license-cloud.md）。
unity --version
unity auth status --format json      # 如果已注销：      unity auth login
unity license status --format json   # 如果没有激活的许可证：      unity license activate

# 2. 选择并安装具有目标平台所需模块的编辑器。
#    默认为最新的 LTS（最稳定，约 2 年的补丁）。对于 LTS 中尚未提供的功能，请仅使用 --stream tech 版本；
#    将 --stream beta/alpha 视为仅用于评估，切勿用于计划发布的项目。截止日期支持 LTS。
#    (lts / latest 别名几乎在所有接受版本的地方都有效——`templates` 是例外；参见步骤 3。)
unity releases --stream lts --limit 5 --format json
unity install lts --module android --module ios --yes --accept-eula   # 添加 --module webgl, 等。
unity editors --installed --format json                               # 确认它已安装

# 3. 列出此编辑器提供的真实模板 ID——不要猜测它们——并按渲染管线选择，而不仅仅是 2D/3D。默认为 URP 模板：
#      3D → com.unity.template.urp-blank      ("Universal 3D")
#      2D → com.unity.template.universal-2d   ("Universal 2D": URP + 2D 包)
#    com.unity.template.3d 和 com.unity.template.2d 是内置渲染管线模板
#    (displayName "… (内置渲染管线)"): 从 Unity 6.5 开始弃用，6.7 中消失。仅在用户明确要求使用内置时才使用它们。
#    确认选择，使用 JSON `renderPipeline` 字段——它在当前版本中为 universal-2d 为空，因此匹配该 ID。
#    注意：`templates` 不会解析 lts / latest 别名——与 `install` 和 `projects create` 不同，
#    它直接传递 --editor 并拒绝任何不是具体 6000.x.y 的内容。使用您刚刚安装的版本（从 `editors --installed` 读取）。
unity templates list --editor <6000.x.y> --type core --format json

# 4. 创建项目。第一个位置参数是 NAME；--path 设置父目录。
#    所有选项都已提供，因此不会提示；在 CI 中添加 --non-interactive。
unity projects create "MyGame" --path ~/UnityProjects \
  --editor-version lts --template com.unity.template.urp-blank
```

**版本控制——让用户选择。** CLI 一步将新项目发布到任何提供者的新远程存储中。**始终通过 stdin 传递令牌** (`--git-token-stdin`)，以便密钥永远不会出现在 shell 历史记录或进程列表中。根据项目选择，不要默认选择一个：

- **Git — GitHub / GitLab** (`--vcs github` / `--vcs gitlab`)。普遍存在。对于资源密集型游戏，添加 **Git LFS** (`--git-lfs`)，以便大型二进制文件不会使历史记录膨胀。
- **Unity 版本控制 — UVCS** (`--vcs uvcs`)。Unity 自己的版本控制系统，专为大型二进制游戏资源构建：它原生处理它们（**不需要 LFS**）并支持文件锁定——通常是艺术密集型项目或较大团队的更好选择。认证使用您的 Unity 登录；`--vcs-region` 选择区域。

```bash
# Git (GitHub) — 如果游戏不是资源密集型，请删除 --git-lfs。如果您想在第一次提交之前添加包/资源（参见新的 new-unity-project 流程），
# 添加 --no-initial-commit。
unity projects create "MyGame" --path ~/UnityProjects \
  --editor-version lts --template com.unity.template.urp-blank \
  --vcs github --git-namespace my-org --git-repo my-game \
  --git-visibility private --git-default-branch main --git-token-stdin --git-lfs

# Unity 版本控制 (UVCS) — 原生处理二进制文件，因此不需要 LFS：
unity projects create "MyGame" --path ~/UnityProjects \
  --editor-version lts --template com.unity.template.urp-blank \
  --vcs uvcs --git-namespace my-org --git-repo my-game --vcs-region <region>
```

从密钥库中提供令牌给 `--git-token-stdin`，而不是字面量——例如 `… --git-token-stdin <<<"$GIT_TOKEN"`，其中 `$GIT_TOKEN` 来自您的 CI/密钥管理器（UVCS 使用您的 Unity 登录，因此不需要令牌）。

**日常使用 UVCS 工作区：一些包装的读取，其他所有内容直接通过到 `cm`。** 这种分割是故意的，值得教给用户，因为猜测错误会浪费用户的时间：

- **`unity vcs uvcs <verb>`** 包装将 `cm` 的数据与您的项目连接起来的读取——`locks`（谁持有锁，*以及哪些锁覆盖您已经更改的文件*）、`changesets` 和 `review`。这些连接是 `cm` 无法为您做的事情，并且它们以稳定的信封形式出现，因此每当有*解析*输出时，请优先使用它们。
- **`unity uvcs <args>`** 将整个命令行原封不动地转发给 `cm`，包括 `--help` 和 `--format`。这是支持的路由，而不是解决方案：`cm` 拥有并版本控制这个词汇，因此包装它将锁定一个过时的释义。对于**部分检出**、**货架**以及**获取或释放锁**，以及当人类读取输出时，请使用它。

```bash
unity vcs uvcs locks                       # 谁持有什么，以及哪些与您的更改冲突
unity uvcs lock list                       # 原始列表，cm 自己的标志和输出
unity uvcs partial update /Assets/Levels   # cm 自己的词汇，未更改
unity uvcs shelve -c "wip: lighting pass"
```

每个动词、标志和陷阱：[version-control.md](references/version-control.md)。

`unity cm <args>` 在 cm 自己的名称下执行相同的传递。两者都需要 `cm` 客户端；如果命令说它缺失，请使用 `unity plugin install plastic` 安装它。

**设置之外，`vcs` 组涵盖了第二天循环的整个内容**——`状态`、`同步`、`切换`、`合并设置`、`冲突` / `解释` / `解析`、`差异`、`归因`、`钩子`、`doctor`、`提供者`——以及 Unity 语义是选择它而不是原始 `git` 的原因。完整参考，包括标志和陷阱：
[version-control.md](references/version-control.md)。

**Git 令牌属于用户的凭证管理器，而不是 CLI。** 当没有提供令牌标志或环境变量时，CLI 请求 `git credential fill` 并使用配置的助手返回的内容；它不会存储它传递或被告知的任何内容。不要建议 CLI 可以保存 Git 令牌，并且在用户已经有一个工作的凭证助手时不要使用令牌标志。如果他们希望每个组织使用不同的令牌，那就是 `git config --global credential.useHttpPath true` 加上一个多账户助手，例如 [Git Credential Manager](https://github.com/git-ecosystem/git-credential-manager)。CLI 传递完整的存储库 URL，以便助手可以进行区分，但它永远不会安装或重新配置助手。`UNITY_GITHUB_TOKEN` / `UNITY_GITLAB_TOKEN` 是每个提供者的一个令牌，因此跨越多个组织的 CI 作业应该针对每次调用传递 `--git-token-stdin`。参见 [references/projects-templates.md](references/projects-templates.md) 以获取完整的源代码控制标志集。对于纯本地 Git 存储库，使用 Unity 适当的忽略文件初始化 git，以便 `Library/` 和其他生成的文件夹永远不会被提交：

```bash
cd ~/UnityProjects/MyGame
git init -b main
# 下载（不要将其传递给 shell）一个维护的 Unity .gitignore：
curl -fsSL https://raw.githubusercontent.com/github/gitignore/main/Unity.gitignore -o .gitignore

# 资源密集型游戏？使用 Git LFS 将大型二进制文件排除在 git 历史记录之外：
git lfs install
git lfs track "*.psd" "*.fbx" "*.wav" "*.mp3" "*.png"   # 调整到您的资源类型
git add .gitattributes

git add -A
git status                             # 检查：Library/ Temp/ obj/ Build/ 绝不能被暂存
git commit -m "Initial Unity project: MyGame"
git ls-files | grep -c '^Library/'     # 必须打印 0
```

**CLI 做什么和不做什么。** CLI 处理编辑器、项目和源代码控制。它**不**管理 UPM（Unity 包管理器）包——要无头地添加模板头之外的包，请使用 **`unity-package-management`** 技能（C# PackageManager Client API）。对于变现/后端，将任务交给专门的技能：`implement-in-app-purchases` (IAP)、`levelplay-unity-integration` (广告) 或 `build-live-game` (账户、云保存、经济、远程配置、排行榜)。打开项目开始工作：
`unity open ~/UnityProjects/MyGame`。

### 查找并安装缺失的编辑器

```bash
# 1. 检查已安装的内容
unity editors --installed --format json

# 2. 浏览可用的 LTS 版本
unity releases --lts --limit 5 --format json

# 3. 安装
unity install 6000.0.47f1 --yes --accept-eula
```

### 使用正确的编辑器打开项目

```bash
# 1. 检查项目所需的编辑器版本
unity projects info /path/to/MyProject --format json
# 查看 "editorVersion" 在结果中

# 2. 确认该编辑器已安装
unity editors --installed --format json

# 3. 打开（如果编辑器版本缺失会发出警告）
unity open /path/to/MyProject
```

### CI：激活许可证，然后构建

```bash
# 1. 使用服务账户非交互式登录
unity auth login --client-id "$UNITY_SERVICE_ACCOUNT_ID" --secret-from-stdin <<<"$UNITY_SERVICE_ACCOUNT_SECRET"

# 2. 激活授权许可证（或使用 --serial / --floating）
unity license activate

# 3. 构建
unity build /path/to/MyProject \
  --editor-version 6000.0.47f1 \
  --target StandaloneLinux64 \
  --execute-method Builder.PerformBuild \
  --allow-install
echo "退出码: $?"

# 4. 完成后归还席位（浮动/分配）
unity license return --yes
```

### CI: 无头构建

优先使用专用的 `unity build` 命令（处理批处理模式、日志记录和 CI 标志）：

```bash
unity build /path/to/MyProject \
  --editor-version 6000.0.47f1 \
  --target StandaloneLinux64 \
  --execute-method Builder.PerformBuild \
  --allow-install
echo "退出码: $?"
```

或使用 `unity run`（批处理模式自动生效——永远不要传递 `-batchmode`/`-quit`）：

```bash
unity run /path/to/MyProject \
  --editor-version 6000.0.47f1 \
  --allow-install \
  -- -executeMethod Builder.PerformBuild -logFile build.log
echo "退出码: $?"
```

### CI: 运行测试并发布结果

```bash
unity test /path/to/MyProject \
  --editor-version 6000.0.47f1 \
  --mode EditMode \
  --report-format junit \
  --output ./test-results.xml \
  --allow-install \
  --timeout 600
case $? in
  0) echo "所有测试通过" ;;
  8) echo "测试失败——报告给开发者，不要重试" ;;
  *) echo "运行未完成——基础设施故障，可以安全重试" ;;
esac
```

退出 `8` 表示运行完成并报告了失败的测试；任何其他非零代码表示它从未产生结果。在 `--format json` 下，相同的分割是 `errors[0].code`：`TESTS_FAILED` 对比 `TEST_RUN_ERROR` / `TEST_TIMED_OUT`。

`--report-format junit` 使 `--output` 成为 JUnit-规范报告，GitHub Actions 和 GitLab 会将其作为原生测试结果摄入，无需转换步骤。即使测试失败也会生成。移除该标志使用 NUnit3 默认，或使用 `--report-format nunit,junit` 从一次运行中获取两者。添加 `--coverage` 通过 Unity 代码覆盖率包收集覆盖率——如果项目没有该包，会警告并继续。参见 [build-run-test.md](references/build-run-test.md)。

### 调试 CLI

```bash
# 一次性检查认证 + 已安装编辑器 + 最近错误
unity doctor --format json

# 在安装期间实时跟踪日志
unity logs --follow --level info
```

---

## 注意事项

- `--non-interactive` 和 `--yes` 一起抑制所有提示——在 CI 中使用两者。
- `--format json` 总是生成机器可读输出；优先于解析人类文本。错误包与成功包使用相同的 2 空格缩进进行美化打印。
- **从 stdout 读取失败，而不是 stderr。** 失败的命令仍然会向 stdout 写入完整文档：在 `--format json` 下是一个带有 `success: false` 和填充 `errors` 数组（`errors[0].code` 是稳定的分支标记）的包；在 `--format ndjson` 下是终端的 `{"type":"result","success":false,…}` 帧结构。**基于 `success` 分支，永远不要基于 `data`**——`data` 在失败时通常是 `null`，但不总是如此：部分 `unity editors add` 失败会按路径携带一行，而模糊的 `unity auth switch` 会携带 `data.candidates` 供你区分。检查 `success` 和退出码——永远不要将空的 stdout 视为失败信号，并且不要解析 stderr，它在这些格式下只携带人类诊断信息。少数命令尚未迁移，仍然将 `{"error": "…"}` 打印到 stderr 并带有空的 stdout；如果 stdout 为空且退出码非零，那是该命令的已知错误，而不是你应该编写的形状。
- `unity <版本> [路径]` 是 `unity open [路径] --editor-version <版本>` 的缩写。适用于 `lts`、`latest` 或完整版本字符串如 `6000.0.47f1`。
- CLI 支持 kubectl 风格的插件：任何 `unity-<名称>` 二进制文件在 PATH 上都可通过 `unity <名称>` 调用。
- 终端输出针对服务器提供的值（项目标题、编辑器版本、模块名称）中的控制字符/转义序列注入进行了加固——C0 控制字符和非 SGR 转义序列从表格/列表/树输出中移除，现在也从 Commander 使用错误、`unity bug` 日志存档警告以及 `unity projects add`/`remove` 机器（tsv）输出中移除，而 SGR 颜色/样式代码被保留。
- CLI 通过 Sentry 报告匿名崩溃和错误以帮助修复错误（不包含 IP 地址或主机名；家目录路径和类似令牌的值在发送前被清理），与 Unity Hub 保持一致。选择分析会额外附加一个匿名机器 ID；选择退出用户保持完全匿名。设置 `UNITY_NO_CRASH_REPORT` 完全禁用报告。另外，每次运行都会发送一个匿名的 `cli telemetry` 使用 ping，无论分析/同意状态如何——参见 [diagnostics-maintenance.md](references/diagnostics-maintenance.md#analytics--usagetelemetry-consent)。
- CLI 目前处于 **测试版**（最新：`1.0.0-beta.10`）。它在 `1.0.0-beta.1` 时迁移到 1.0 版本；它仍然是测试版，因此请在安装命令中保持 `UNITY_CLI_CHANNEL=beta`，直到 GA 发布，之后可以移除这部分。
- 自 `0.1.0-beta.8` 起，CLI 在后台检查更新版本并打印一个不显眼的“有可用更新”通知（仅交互式会话；永远不会延迟命令）。使用 `unity config update-check off` 或环境变量 `UNITY_NO_UPDATE_CHECK` 关闭它。
- 每个 CLI 命令的外发 HTTP 尊重解析的代理（参见 `unity config proxy`）。无效的 `--proxy` 值（格式错误的 URL 或不支持的方案）会以使用错误（退出 2）失败，而不是被静默忽略。使用 `unity env --format json` 或 `unity doctor --format json` 查看CLI实际解析的内容——两者都会显示活动代理 URL、其来源和认证来源。
