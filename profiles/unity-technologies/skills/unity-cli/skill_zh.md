# Unity CLI

## 驱动正在运行的 Unity 编辑器（如果已打开）

**如果此计算机上打开了 Unity 编辑器，此 CLI 可以实时控制它** — 创建和修改 GameObject，编辑场景和资源，检查层级结构，以及运行任意 C# — 通过项目的 **Pipeline** 包 (`com.unity.pipeline`)。这完全在您的本地计算机上运行，在您自己的用户帐户中，针对您自己打开的编辑器：它不是远程访问，也不授予您在您自己的终端上没有的任何权限。当编辑器可用时，驱动它而不是手动编辑场景或资源文件。

```bash
unity status                    # 确认连接的编辑器（查找状态 "ready"）
unity command                   # 列出编辑器暴露的命令
unity command editor_play       # 运行一个 — 例如，进入 Play 模式
# 运行任意 C# — 例如，添加一个名为 "Joe" 的 GameObject — 当编辑器暴露 eval 时：
unity command eval 'new UnityEngine.GameObject("Joe");'
```

### 打开多个编辑器？传递 `--project-path`

每个驱动编辑器的命令都接受 `--project-path <path>`。**每当可能打开多个编辑器时，请传递它** — 如果不传递它，CLI 会针对包含当前目录的项目中的编辑器，因此目标跟随 shell 的 cwd：

```bash
unity command editor_play --project-path /path/to/MyProject
```

一个 `unity status` 实例的 `project` 字段是 `--project-path` 使用的。对于 `unity command`/`list`/`job`/`mcp`，匹配没有运行的项目会以 `AMBIGUOUS_EDITOR` 失败并列出候选者。[详细信息](references/integration-advanced.md#targeting-one-of-several-running-editors)。

需要项目的 `com.unity.pipeline` 包（Unity 6.0+） — 使用 `unity pipeline install` 一次添加它。完整详细信息 — 启动无头编辑器以驱动，`unity list` 工具发现，以及编写自定义 `[CliCommand]` 工具 — 在 [integration-advanced.md](references/integration-advanced.md) 中。

该包还附带一个更深层的 `unity-pipeline` 代理技能，对 `Library/PackageCache` 内的客户端不可见 — 在包含该包的项目中，运行 `unity skill install <client> --local` 一次即可在与此技能旁边镜像它。

> **无法连接 / 命令超时？首先检查安全模式。** 当项目有 C# 编译错误时，编辑器会启动**安全模式**，其中 Pipeline 包不会加载 — 因此 `unity command`，`unity status` 和 `unity list` 完全无法连接。不要退回到盲目的文件编辑：运行 `unity pipeline list` 以确认，然后修复编译错误并重新启动 Unity。完整恢复循环在 [integration-advanced.md → 从安全模式恢复](references/integration-advanced.md#recovering-from-safe-mode-connection-fails-because-of-compile-errors)。

> **作为沙盒编码代理运行，而 `unity status` 报告没有实例？** 严格的沙盒可以隐藏一个确实正在运行的编辑器，使其对 CLI 的视图不可见 — 不要将这一点单独视为编辑器已关闭的证据。完整细节在 [integration-advanced.md → 沙盒代理工具可以隐藏正在运行的编辑器](references/integration-advanced.md#sandboxed-agent-tooling-can-hide-a-running-editor)。

## 安装 CLI（如果尚未安装）

首先检查 CLI 是否可用：

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
| `--format <fmt>` | 输出格式：`human`（默认），`json`，`tsv`，`ndjson`，`github`。也通过 `UNITY_FORMAT` 环境变量设置。 |
| `--json` | `--format json` 的全局缩写，在所有命令中接受（例如 `unity status --json`，`unity doctor --json`）。当两者都提供时，`--format` 优先级更高。 |
| `--no-banner` | 抑制品牌页眉 — 用于脚本 |
| `--no-pager` | 关闭分页。管理两个分页器：外部分页器用于长列表（`unity command`，`releases`，`editors`，`changelog`，`logs`）和交互式分页器在 `unity projects list` 中。也通过 `UNITY_NO_PAGER`（基于存在 — 任何值，包括 `0`，都会禁用它）。 |
| `--non-interactive` | 禁用所有交互式提示 — 用于 CI |
| `--quiet` | 抑制非必要输出 |
| `--verbose` | 在失败时打印完整错误详细信息（堆栈跟踪 + 原因链）。也通过 `UNITY_VERBOSE` 设置。 |
| `--proxy <url>` | 此调用的 HTTP/HTTPS/SOCKS/PAC 代理 URL。也通过 `UNITY_PROXY` 设置。优先级高于标准的 `HTTPS_PROXY`/`HTTP_PROXY`/`ALL_PROXY` 环境变量和持久化的 `proxy.json` 设置。 |
| `--proxy-disable` | 禁用此调用的代理，忽略所有来源（环境变量、持久化配置、系统设置）。 |
| `--log-proxy` | 将每个出站请求的一条脱敏条目记录到 `proxy-request.json` — 用于重现代理问题。也通过 `UNITY_LOG_PROXY=1` 或 `proxyRequestLogging` 设置。 |
| `--no-log-proxy` | 当全局启用代理请求记录时，使单个调用排除代理请求记录。 |
| `--color <auto\|always\|never>` | 控制此调用的彩色输出，覆盖 `NO_COLOR`/`FORCE_COLOR` 和 TTY 自动检测。管理每个发出 ANSI 代码的表面（帮助，表格，旋转器，错误），而不仅仅是 `human` 输出。 |
| `--no-color` | `--color never` 的缩写。无论 `--color`/`--no-color` 出现在行尾的最后一个，以哪个为准。 |

**始终使用 `--format json` 当您需要解析输出时。**

`--accelerator <host:port>` 和 `--no-accelerator` 不是**根全局标志** — 它们仅在 `run`，`test` 和 `build` 命令中接受，并且仅在命令名称之后接受。请参阅 [build-run-test.md](references/build-run-test.md)。

**`unity projects list` 是唯一分页 IN-PROCESS 的命令。** 它每屏显示 10 个项目，并在屏幕之间等待按键，并且只有在 stdout 是终端时才这样做。分页关闭，用于重定向 stdout，`--format json` 和 `--format ndjson` 下，以及 `--all`，`--watch` 或 `--no-pager` / `UNITY_NO_PAGER`。

**并非每台机器格式都绕过那个。** 只有 `json` 和 `ndjson` 才有自己的非交互式渲染；在终端上，`--format tsv` 和 `--format github` 会像 `human` 一样绕过到人类表格并分页 — 因此在 TTY 上 `--format tsv` 不会产生 TSV 或未分页输出。重定向 stdout（通常是机器格式的常规情况）或传递 `--no-pager`。请注意，这与其他机制相反，其中 `projects list` 是令人惊讶的。

**长列表通过外部分页器分页，就像 `git log`。** `unity command`（裸列表），`unity releases`，`unity editors`，`unity changelog` 和 `unity logs` 将人类输出通过终端上的 `less -RFX` — 保留颜色，不清屏，并且 `-F` 在输出已经适合一屏时自动退出，因此短列表不显示分页 UI。`$UNITY_PAGER` 然后 `$PAGER` 覆盖选择并在 shell 中运行，因此 `PAGER="less -S"` 有效；空值被忽略而不是视为放弃。使用 `q` 退出干净地以命令的退出代码退出。与 `projects list` 的分页器不同，这个分页器是**`human` 仅**，并且它永远不会为重定向 stdout，任何机器格式（`json`，`tsv`，`ndjson`，`github`），`--quiet`，`TERM=dumb`，流式模式（`editors --watch`，`logs --follow`），命名的 `unity command <name>` 或在 `unity shell` 内部。损坏的分页器会导致分页失败，而不是输出：`$PAGER` 指定不存在的内容会在生成之前解决，而一个生成后死亡的分页器会将其输出重新打印到终端，由分页器的退出状态决定（干净的退出是一个正常的 `q` 并丢弃；失败状态会重新打印）。例外是一个分页器在成功退出时不读取 — `PAGER=true` 或任何在停留后退出 0 的内容 — 没有任何东西可以将其与 `q` 区分，并且 `git` 也失去了它。一个分页器启动并仅仅是等待，则不被视为损坏，因此 CLI 会等待它。

品牌 Unity 页眉（标志，文字标志，CLI 版本）在着陆表面渲染 — 裸 `unity`，`unity --help` / `-h`，`unity help` 和第一次运行同意提示符上方。它仅在 TTY 上显示，最多打印一次，并在窄终端上退化为一行紧凑的未着色文本，没有 Unicode，或在 `NO_COLOR` 下。管道输出不受影响。在脚本中使用 `--no-banner` 来抑制它。裸 `unity` 打印用法并退出 0。

## 环境变量

所有 CLI 环境变量都使用 `UNITY_` 前缀。CLI 标志始终覆盖相应的环境变量。

| 变量 | 映射标志 | 描述 |
|---|---|---|
| `UNITY_FORMAT` | `--format` | 输出格式 (`human`，`json`，`tsv`，`ndjson`，`github`)。`HUB_FORMAT` 是一个已弃用的别名。 |
| `UNITY_EDITOR_VERSION` | `--editor-version` | 编辑器版本（例如 `2023.3.0f1`，`latest`，`lts`)。 |
| `UNITY_ARCHITECTURE` | `--architecture` | 硬件架构 (`x86_64`，`arm64`)。 |
| `UNITY_PROJECT_PATH` | path 参数 | 项目路径 — 用于 `open`，并且 `status` 和云命令也认可。 |
| `UNITY_QUIET` | `--quiet` | 抑制非必要输出。 |
| `UNITY_VERBOSE` | `--verbose` | 在失败时显示完整错误详细信息（堆栈跟踪 + 原因链）。也通过 `UNITY_VERBOSE` 设置。 |
| `UNITY_NON_INTERACTIVE` | `--non-interactive` | 禁用所有交互式提示 — 用于 CI |
| `UNITY_NO_BANNER` | `--no-banner` | 抑制品牌标志。 |
| `UNITY_NO_PAGER` | `--no-pager` | 关闭分页 — 两个分页器：外部分页器用于长列表（`unity command`，`releases`，`editors`，`changelog`，`logs`) 和 `unity projects list` 中的交互式分页器。基于存在 — 任何值，包括 `0`，都会禁用它。 |
| `UNITY_PAGER` | — | 用于长列表的分页器，覆盖 `$PAGER` 和 `less -RFX` 默认。在 shell 中运行，因此标志有效 (`less -S`)。空值被忽略，而不是视为放弃。 |
| `PAGER` | — | 与 `UNITY_PAGER` 相同，仅在 `UNITY_PAGER` 未设置或为空时才咨询。 |
| `LESS` / `LV` / `LESSCHARSET` / `MORE` | — | 仅当您未设置它们时才传递给分页器，默认为 `FRX`，`-c`，`utf-8` 和 `FRX`。`LESSCHARSET` 在区域设置未声明 UTF-8 的情况下保持多字节字形可读；`MORE` 存在是因为 macOS/BSD 上的 `more` 是 `less` 的另一个名称，它读取 `$MORE`，因此即使对于单行，`PAGER=more` 也会等待按键。 |
| `UNITY_RUN_TIMEOUT` | `--timeout` | `unity run` 的超时时间（秒）。 |
| `UNITY_TEST_TIMEOUT` | `--timeout` | `unity test` 的超时时间（秒）。 |
| `UNITY_CLOUD_ORG` | `--cloud-org` | 单次调用中活动的 Unity Cloud 组织 id 或名称。 |
| `UNITY_SERVICE_ACCOUNT_ID` | — | 非交互式（CI）认证的服务帐户客户端 ID。 |
| `UNITY_SERVICE_ACCOUNT_SECRET` | — | 非交互式（CI）认证的服务帐户客户端密钥。 |
| `UNITY_PROXY` | `--proxy` | HTTP/HTTPS/SOCKS/PAC 代理 URL。优先级高于 `HTTPS_PROXY`/`HTTP_PROXY`/`ALL_PROXY` 和持久化的 `proxy.json` 设置。 |
| `UNITY_NO_UPDATE_CHECK` | — | 禁用后台“有更新可用”检查（参见 `unity config update-check`)。 |
| `UNITY_NO_CONSENT_PROMPT` | — | 抑制一次性首次运行分析同意提示符*不*记录选择 — 用于交互式终端上的包装脚本，这些脚本绝不能吸收提示符。分析保持关闭，直到您运行 `unity analytics opt-in`。与 `UNITY_NON_INTERACTIVE` 不同，它不会改变命令行为的任何其他内容。 |
| `UNITY_NO_CRASH_REPORT` | — | 完全禁用匿名崩溃/错误报告（Sentry)。 |
| `UNITY_LOG_PROXY` | `--log-proxy` | 将每个出站请求的一条脱敏条目记录到 `proxy-request.json`。真值：`1`，`true`。 |
| `UNITY_ACCELERATOR` | `--accelerator` | Unity 加速器端点 (`host:port`)。优先级高于持久化的 `accelerator.json`；`--accelerator` 优先级更高。 |
| `UNITY_NO_ELEVATE` | `--no-elevate` | Windows：跳过 `install` / `install-modules` 的提升（UAC）安装辅助程序，因此安装服务以非提升方式运行。编辑器的 NSIS 安装程序仍然会在 Windows 要求您的帐户提升时请求提升 — 管理员令牌始终这样做；标准用户从不这样做。 |
| `UNITY_INSTALL_RETRIES` | `--retries` (`install-modules` 仅) | 重试下载失败（传输或验证失败）的编辑器或模块的次数。`0` 禁用重试；`unity install` 没有 |--retries` 标志，因此在此处设置变量。 |
| `UNITY_NO_AUTH_BROKER` | — | 跳过驻留认证代理并直接从操作系统密钥库读取凭据。默认情况下，每个需要令牌的命令都通过一个在按需启动并在闲置两分钟后退出的代理，该代理启动并退出（参见 [auth-license-cloud.md](references/auth-license-cloud.md))。 |
| `UNITY_PEER_AUTH_MODE` | — | 认证代理和编辑器身份辅助程序如何验证连接进程的代码签名。`enforce` 是 macOS 和 Windows 上的默认值：未签名或非 Unity 签名的对等方会被拒绝。`identify-only` 会在不拒绝的情况下记录 — 用于从源代码构建的编辑器。Linux 仅在设置为 `enforce` 与 `UNITY_PEER_AUTH_LINUX_ALLOWED_HASHES`（逗号分隔的 SHA-256 哈希值，受信任的可执行文件）一起时才记录。 |
| `UNITY_CLI_HOME` | — | 安装脚本和 `unity self-install` 的安装根，在所有平台上包括 Windows：二进制文件位于 `<UNITY_CLI_HOME>/bin` 而不是默认位置。 |
| `UNITY_NO_EDITOR_IDENTITY_SERVER` | — | 禁用启动 `unity open` 以回答编辑器登录查找的背景身份辅助程序，当没有 Hub 运行时（参见 [projects-templates.md](references/projects-templates.md))。基于存在。 |

**CI 服务帐户认证：** 将 `UNITY_SERVICE_ACCOUNT_ID` 和 `UNITY_SERVICE_ACCOUNT_SECRET` 都设置为跳过浏览器 OAuth 流 — 这将密钥保持在进程参数列表和 shell 历史记录之外。这些映射到 `unity auth login` 的 `--client-id` / `--secret-from-stdin` 输入，但从未从环境变量中读取凭据，这不是完整的登录：它不会运行交互式流程或将凭据持久化到密钥库。参见 [references/projects-templates.md](references/projects-templates.md) 中的完整源代码控制标志集。对于纯本地 Git 仓库，使用 Unity 适当的忽略初始化 git，以便 `Library/` 和其他生成的文件夹永远不会提交：

```bash
cd ~/UnityProjects/MyGame
git init -b main
# 下载（不要将其管道到 shell）一个维护的 Unity .gitignore：
curl -fsSL https://raw.githubusercontent.com/github/gitignore/main/Unity.gitignore -o .gitignore

# 资源密集型游戏？使用 Git LFS 将大型二进制文件从 git 历史记录中排除：

```bash
git lfs install
git lfs track "*.psd" "*.fbx" "*.wav" "*.mp3" "*.png"   # 调整为您的资源类型
git add .gitattributes

git add -A
git status                             # 检查：Library/ Temp/ obj/ Build/ 必须不处于暂存状态
git commit -m "Initial Unity project: MyGame"
git ls-files | grep -c '^Library/'     # 必须打印 0
```

**CLI 做什么不做什么。** CLI 处理编辑器，项目和源代码控制。它不管理 UPM（Unity 包管理器）包 — 要头文件以外以非交互方式添加包，请使用 **`unity-package-management`** 技能（C# PackageManager Client API）。对于变现/后端，将工作交给专用的技能：`implement-in-app-purchases` (IAP)，`levelplay-unity-integration` (广告)，或 `build-live-game` (帐户，云保存，经济，远程配置，排行榜)。打开项目开始工作：
`unity open ~/UnityProjects/MyGame`.

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
# 1. 检查项目的所需编辑器版本
unity projects info /path/to/MyProject --format json
# 查看结果中的 "editorVersion"

# 2. 确认已安装该编辑器
unity editors --installed --format json

# 3. 打开（如果编辑器版本缺失则警告）
unity open /path/to/MyProject
```

### CI：激活许可证，然后构建

```bash
# 1. 使用服务帐户非交互式登录
unity auth login --client-id "$UNITY_SERVICE_ACCOUNT_ID" --secret-from-stdin <<<"$UNITY_SERVICE_ACCOUNT_SECRET"

# 2. 激活许可（或使用 --serial / --floating）
unity license activate

# 3. 构建
unity build /path/to/MyProject \
  --editor-version 6000.0.47f1 \
  --target StandaloneLinux64 \
  --execute-method Builder.PerformBuild \
  --allow-install
echo "Exit code: $?"

# 4. 完成时返回座位（floating/assigned）
unity license return --yes
```

### CI：无头构建

优先使用专用的 `unity build` 命令（处理批处理模式，日志记录和 CI 标志）：

```bash
unity build /path/to/MyProject \
  --editor-version 6000.0.47f1 \
  --target StandaloneLinux64 \
  --execute-method Builder.PerformBuild \
  --allow-install
echo "Exit code: $?"
```

或者使用 `unity run`（批处理模式自动 — 永远不要传递 `-batchmode`/`-quit`）：

```bash
unity run /path/to/MyProject \
  --editor-version 6000.0.47f1 \
  --allow-install \
  -- -executeMethod Builder.PerformBuild -logFile build.log
echo "Exit code: $?"
```

### CI：运行测试并发布结果

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
  8) echo "测试失败 — 向开发人员报告，不要重试" ;;
  *) echo "运行未完成 — 基础设施故障，可以安全重试" ;;
esac
```

退出 `8` 意味着运行完成并报告了失败的测试；任何其他非零代码都意味着它从未产生判断。在 `--format json` 下，相同的分割是 `errors[0].code`：`TESTS_FAILED` 与 `TEST_RUN_ERROR` / `TEST_TIMED_OUT` 不同。

`--report-format junit` 使 `--output` 成为 JUnit-模式报告，GitHub Actions 和 GitLab 会将其作为原生测试结果摄入，无需转换步骤。即使测试失败也会写入。丢弃此标志以使用 NUnit3 默认，或使用 `--report-format nunit,junit` 从一个运行中获取两者。添加 `--coverage` 以通过 Unity 代码覆盖率包收集覆盖率 — 如果项目没有该包，它会警告并继续进行。参见 [build-run-test.md](references/build-run-test.md)。

### 调试 CLI

```bash
# 使用一个命令检查认证 + 已安装的编辑器 + 最近错误
unity doctor --format json

# 在安装期间跟随实时日志
unity logs --follow --level info
```

---

## 注意事项

- `--non-interactive` 和 `--yes` 一起抑制所有提示 — 在 CI 中使用两者。
- `--format json` 始终产生机器可读输出；优先于解析人类文本。错误信封与成功信封使用相同的 2 空格缩进进行格式化。
- **从 stdout 读取失败，而不是 stderr。** 一个失败的命令仍然会向 stdout 写入完整的文档：在 `--format json` 下，是一个带有 `success: false` 和填充 `errors` 数组的信封 (`errors[0].code` 是分支的稳定标记)；在 `--format ndjson` 下，是终端上的常用 `{"type":"result","success":false,…}` 帧架。**始终基于 `success` 分支，而不是 `data` — `data` 通常在失败时为 `null`，但并不总是如此：一个部分 `unity editors add` 失败会携带每条路径的行，而一个模糊的 `unity auth switch` 会携带 `data.candidates` 以供您区分。检查 `success` 和退出代码 — 永远不要将空的 stdout 视为失败信号，并且不要解析 stderr，它在这些格式中只携带人类诊断。少数命令尚未迁移，仍然将 `{"error": "…"}` 打印到 stderr，而 stdout 为空；如果 stdout 在非零退出时为空，则该命令中存在一个已知错误，而不是您应该编写的形状。

`unity <version> [path]` 是 `unity open [path] --editor-version <version>` 的缩写。适用于 `lts`，`latest` 或完整版本字符串，如 `6000.0.47f1`。
- CLI 支持kubectl风格的插件：任何 `unity-<name>` 二进制文件在 PATH 上都可以作为 `unity <name>` 调用。
- 终端输出针对来自服务器提供的值（项目标题，编辑器版本，模块名称）中的控制字符/转义序列注入进行硬化 — 从表格/列表/树输出中删除 C0 控制字符和非 SGR 转义序列，现在也删除了 Commander 使用错误，`unity bug` 日志存档警告，以及 `unity projects add`/`remove` 机器（tsv）输出，而 SGR 颜色/样式代码则被保留。
- CLI 通过 Sentry 报告匿名崩溃和错误以帮助修复错误（不包含 IP 地址或主机名；家目录路径和类似令牌的值在发送前被脱敏），与 Unity Hub 一致。分析附加了一个匿名机器 ID；选择退出用户保持完全匿名。设置 `UNITY_NO_CRASH_REPORT` 以完全禁用报告。
- 另外一次，每个运行都会发送一个匿名的 `cli telemetry` 使用 ping，无论分析/同意状态如何 — 请参阅 [diagnostics-maintenance.md](references/diagnostics-maintenance.md#analytics--usagetelemetry-consent)。
- CLI 目前处于 **beta**（最新：`1.0.0-beta.10`）。它在 `1.0.0-beta.1` 时切换到 1.0 版本，但它仍然是一个 beta，因此请在安装命令中保留 `UNITY_CLI_CHANNEL=beta`，直到 GA 发布，之后可以删除这部分。
- 自 `0.1.0-beta.8` 起，CLI 在后台检查是否有更新的版本，并打印一个不显眼的“有更新可用”通知（仅限交互式会话；永远不会延迟命令）。使用 `unity config update-check off` 或 `UNITY_NO_UPDATE_CHECK` 环境变量关闭它。
- 来自 CLI 命令的每个 CLI 命令的出站 HTTP 尊重解析的代理（见 `unity config proxy`)。无效的 `--proxy` 值（格式错误 URL 或不支持的方案）会以使用错误（退出代码 2）失败，而不是被静默忽略。使用 `unity env --format json` 或 `unity doctor --format json` 检查 CLI 实际解析的内容 — 它们都显示活动的代理 URL，其来源和身份来源。
