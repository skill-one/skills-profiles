# setup-local-sdk

## 目的

指导用户将 .NET SDK 安装到项目本地的 `.dotnet/` 目录，并通过 `.NET 10+` 的 `global.json` `paths` 功能进行配置。
示例使用 .NET 11，但此方法适用于任何版本——预发布版或稳定版。

结果是得到一个完全隔离的 SDK，它：
- **不会**修改系统范围的 .NET 安装。
- 被 `dotnet` 命令从项目根目录自动识别。
- 可以被删除以回滚（`rm -rf .dotnet/` 或 `Remove-Item -Recurse -Force .\.dotnet`）。

## 不应使用的情况

- 用户想要**系统范围**的安装——直接使用官方安装程序。
- 主机 `dotnet` **早于 v10**——`paths` 功能不存在；解释并停止。
- 用户需要**仅运行时**的安装——`paths` 仅适用于 SDK 解析。

## 输入 / 前置条件

| 输入 | 是否必需 | 默认值 | 备注 |
|---|---|---|---|
| 渠道或版本 | 否 | `11.0` | 例如 `11.0`, `STS`, `LTS`, 或精确版本如 `11.0.100-preview.2.26159.112` |
| 质量等级 | 否 | `preview` | 之一：`daily`, `preview`, `ga` |
| jq | 否 | — | 在使用 bash 团队脚本修补现有 `global.json` 时可选；没有它，不要覆盖文件 |

### 前置条件

1. **已全局安装 .NET 10+ SDK** — 运行 `dotnet --version`；主版本 ≥ 10。
2. **curl**（macOS/Linux）或 **PowerShell**（Windows）可用。

## 工作流程

### 第 1 步 — 明确要安装的内容

如果用户没有指定，询问他们想要哪个 .NET SDK 版本（例如，“最新的 .NET 11 预发布版”或精确版本如 `11.0.100-preview.2.26159.112`）。
将答案映射到 `--channel`/`--quality` 或 `--version` 标志。

### 第 2 步 — 验证 .NET 10+ 主机

如果用户已经提供了 `dotnet --version` 输出，将其视为其机器的权威版本。不要用代理工作区的版本覆盖它；如果两者不同，解释工作区不同，并继续为用户的机器提供建议。

```bash
dotnet --version
```

如果主版本 < 10，在下载任何内容之前停止：`paths` 功能需要 .NET 10+ 主机 SDK。告诉用户先系统范围安装 .NET 10 或更高版本，然后返回本地 SDK 设置。

### 第 3 步 — 检测操作系统

运行 `uname -s 2>/dev/null`。如果成功（包括 `MINGW*`, `MSYS*`, `CYGWIN*`——这些是像 Git Bash 一样的 bash 能力环境）→ 使用 bash/`dotnet-install.sh`。
如果失败（没有 Git Bash 的原生 Windows）→ 使用 PowerShell/`dotnet-install.ps1`。

### 第 4 步 — 检查现有的本地 SDK

**macOS / Linux:**

```bash
test -d .dotnet && echo "exists" || echo "not found"
```

**Windows (PowerShell):**

```powershell
if (Test-Path -LiteralPath .\.dotnet) { "exists" } else { "not found" }
```

如果 `.dotnet/` 存在，询问：用新版本更新，还是跳过并保留它？

### 第 5 步 — 下载并运行安装脚本

**macOS / Linux:**

```bash
INSTALL_SCRIPT="$(mktemp "${TMPDIR:-/tmp}/dotnet-install.XXXXXX")"
trap 'rm -f "$INSTALL_SCRIPT"' EXIT
curl -fsSL https://dot.net/v1/dotnet-install.sh -o "$INSTALL_SCRIPT"
bash "$INSTALL_SCRIPT" --channel <CHANNEL> --quality <QUALITY> --install-dir .dotnet
```

**Windows (PowerShell):**

```powershell
$installScript = Join-Path $env:TEMP "dotnet-install-$([guid]::NewGuid()).ps1"
try {
    Invoke-WebRequest -Uri 'https://dot.net/v1/dotnet-install.ps1' -OutFile $installScript
    & $installScript -Channel <CHANNEL> -Quality <QUALITY> -InstallDir .dotnet
}
finally {
    if (Test-Path -LiteralPath $installScript) {
        Remove-Item -LiteralPath $installScript -Force
    }
}
```

对于精确版本：使用 `--version <VERSION>`（bash）或 `-Version <VERSION>`（PowerShell）而不是渠道/质量标志。安装脚本来自 Microsoft 的官方 URL：`https://dot.net/v1/dotnet-install.sh` 和 `https://dot.net/v1/dotnet-install.ps1`。

### 第 6 步 — 确认已安装的版本

```bash
./.dotnet/dotnet --version          # macOS/Linux
.\.dotnet\dotnet.exe --version      # Windows
```

记录精确的版本字符串（例如，`11.0.100-preview.2.26159.112`）以供 `global.json` 使用。

### 第 7 步 — 创建或更新 global.json

```json
{
  "sdk": {
    "version": "<INSTALLED_VERSION>",
    "allowPrerelease": true,
    "rollForward": "latestFeature",
    "paths": [".dotnet", "$host$"],
    "errorMessage": "Required .NET SDK not found. Run ./install-dotnet.sh (or .ps1) to install it locally."
  }
}
```

- `paths`：`.dotnet` 优先（本地优先），`$host$` = 系统范围回退。
- `rollForward: "latestFeature"`：用于最新预发布版或浮动功能带安装。
- 精确版本请求：使用 `rollForward: "disable"` 以防止 SDK 解析移动到不同的功能带。
- `allowPrerelease`：仅在安装预发布版 SDK 时设置为 `true`。稳定版则省略。
- `errorMessage`：仅在创建团队安装脚本（第 10 步）时包含。否则省略。

如果 `global.json` 已存在，**小心合并**：保留现有属性（`msbuild-sdks`, `tools` 等），仅添加/更新 `sdk` 部分。先读取现有文件，更新/添加 `sdk` 对象，然后写回。这确保了跨项目配置（例如，MSBuild 设置）不会丢失。修改前始终备份原始文件（例如，`global.json.bak`）。

**最小配置**（当不需要版本固定时）：
`{"sdk":{"paths":[".dotnet","$host$"]}}`

### 第 8 步 — 更新 .gitignore

**macOS / Linux（或 Git Bash）:**

```bash
grep -qxF '.dotnet/' .gitignore 2>/dev/null || printf '\n.dotnet/\n' >> .gitignore
```

**Windows (PowerShell):**

```powershell
if (-not (Test-Path .gitignore) -or -not (Select-String -Path .gitignore -Pattern '^\.dotnet/$' -Quiet)) {
    Add-Content -Path .gitignore -Value '.dotnet/'
}
```

### 第 9 步 — 安装工作负载（如果请求）

仅在此完成 `global.json` 和 `.gitignore` 后执行，以便慢速或平台受限的工作负载安装不会阻止基本本地 SDK 设置的可用性。

如果用户提到 MAUI、移动、工作负载、Blazor WASM 或跨平台，
使用**本地**二进制文件安装（无需 sudo）：

```bash
./.dotnet/dotnet workload install <workload>       # macOS/Linux
.\.dotnet\dotnet.exe workload install <workload>   # Windows
```

验证：`./.dotnet/dotnet workload list`（或 `.\.dotnet\dotnet.exe workload list`）。

对于 MAUI，选择当前 OS 和目标平台支持的工作负载。在 Linux 上，完整的 `maui` 元工作负载不可用；当 Android 是目标时，使用支持的工作负载（如 `maui-android`），或解释平台限制并询问要配置哪个目标。

> **始终使用本地 dotnet 二进制文件执行工作负载命令。** 工作负载元数据相对于主机进程的 dotnet 根目录存储。系统 `dotnet` 将元数据放在错误的位置。（见 [dotnet/sdk#49825](https://github.com/dotnet/sdk/issues/49825)。）

### 第 10 步 — 创建团队安装脚本

如果用户提到“团队”、“共享”、“CI”、“脚本”等，则创建。否则提供。这些示例备份 `global.json` 并保留现有设置。bash 脚本在必须修补现有 `global.json` 时使用 `jq`；如果 `jq` 不可用，它拒绝覆盖文件并打印手动合并的设置。
根据第 1 步的安装选择调整脚本变量：精确版本应使用 `--version` / `-Version` 并设置 `rollForward: "disable"`；渠道安装应使用渠道/质量，仅对预发布版 SDK 设置 `allowPrerelease: true`。
如果 `global.json` 已固定 `sdk.version`，而用户主要需要团队脚本，则在脚本中重用该版本并先更新 `global.json`；不要只是为了发现版本而开始长时间下载 SDK。当用户同时请求设置和脚本时，在任何长时间安装之前创建脚本/配置，以便即使下载或工作负载安装缓慢，可重复的设置也存在。

**install-dotnet.sh:**

```bash
#!/usr/bin/env bash
set -euo pipefail
INSTALL_DIR=".dotnet"
CHANNEL="11.0"
QUALITY="preview"
VERSION=""
ROLL_FORWARD="latestFeature"
ALLOW_PRERELEASE="true"
WORKLOADS=("${@}")
ERROR_MESSAGE="Required .NET SDK not found. Run ./install-dotnet.sh (or .ps1) to install it locally."
INSTALL_SCRIPT="$(mktemp "${TMPDIR:-/tmp}/dotnet-install.XXXXXX")"
GLOBAL_JSON_TMP=""
cleanup() {
    rm -f "$INSTALL_SCRIPT"
    [ -n "$GLOBAL_JSON_TMP" ] && rm -f "$GLOBAL_JSON_TMP"
}
trap cleanup EXIT
curl -fsSL https://dot.net/v1/dotnet-install.sh -o "$INSTALL_SCRIPT"
INSTALL_ARGS=(--install-dir "$INSTALL_DIR")
if [ -n "$VERSION" ]; then
    INSTALL_ARGS+=(--version "$VERSION")
    ROLL_FORWARD="disable"
else
    INSTALL_ARGS+=(--channel "$CHANNEL" --quality "$QUALITY")
fi
bash "$INSTALL_SCRIPT" "${INSTALL_ARGS[@]}"
SDK_VERSION=$("$INSTALL_DIR/dotnet" --version)
write_global_json() {
    if [ -f global.json ]; then
        cp global.json global.json.bak
        if ! command -v jq >/dev/null 2>&1; then
            echo "global.json exists; install succeeded, but this script will not overwrite it without jq." >&2
            echo "Merge these sdk settings manually so existing global.json properties are preserved:" >&2
            cat >&2 <<EOF
{
  "sdk": {
    "version": "$SDK_VERSION",
    "allowPrerelease": $ALLOW_PRERELEASE,
    "rollForward": "$ROLL_FORWARD",
    "paths": [".dotnet", "\$host\$"],
    "errorMessage": "$ERROR_MESSAGE"
  }
}
EOF
            exit 1
        fi
        GLOBAL_JSON_TMP="$(mktemp "${TMPDIR:-/tmp}/global-json.XXXXXX")"
        jq --arg version "$SDK_VERSION" --arg rollForward "$ROLL_FORWARD" --argjson allowPrerelease "$ALLOW_PRERELEASE" --arg errorMessage "$ERROR_MESSAGE" '
          .sdk = ((.sdk // {}) + {
            version: $version,
            allowPrerelease: $allowPrerelease,
            rollForward: $rollForward,
            paths: [".dotnet", "$host$"],
            errorMessage: $errorMessage
          })
        ' global.json > "$GLOBAL_JSON_TMP"
        mv "$GLOBAL_JSON_TMP" global.json
        GLOBAL_JSON_TMP=""
    else
        cat > global.json <<EOF
{
  "sdk": {
    "version": "$SDK_VERSION",
    "allowPrerelease": $ALLOW_PRERELEASE,
    "rollForward": "$ROLL_FORWARD",
    "paths": [".dotnet", "\$host\$"],
    "errorMessage": "$ERROR_MESSAGE"
  }
}
EOF
    fi
}
write_global_json
grep -qxF '.dotnet/' .gitignore 2>/dev/null || printf '\n.dotnet/\n' >> .gitignore
[ ${#WORKLOADS[@]} -gt 0 ] && "$INSTALL_DIR/dotnet" workload install "${WORKLOADS[@]}"
echo "Done. SDK: $SDK_VERSION"
```

```bash
chmod +x install-dotnet.sh
```

**install-dotnet.ps1:**

```powershell
param([string[]]$Workloads = @())
$ErrorActionPreference = 'Stop'
$installDir = '.dotnet'; $channel = '11.0'; $quality = 'preview'
$version = ''; $rollForward = 'latestFeature'; $allowPrerelease = $true
$errorMessage = 'Required .NET SDK not found. Run ./install-dotnet.sh (or .ps1) to install it locally.'
$installScript = Join-Path $env:TEMP "dotnet-install-$([guid]::NewGuid()).ps1"
try {
    Invoke-WebRequest -Uri 'https://dot.net/v1/dotnet-install.ps1' -OutFile $installScript
    $installArgs = @('-InstallDir', $installDir)
    if ($version) {
        $installArgs += @('-Version', $version)
        $rollForward = 'disable'
    } else {
        $installArgs += @('-Channel', $channel, '-Quality', $quality)
    }
    & $installScript @installArgs
}
finally {
    if (Test-Path -LiteralPath $installScript) {
        Remove-Item -LiteralPath $installScript -Force
    }
}
$sdkVersion = & "$installDir\dotnet.exe" --version
$globalJson = if (Test-Path 'global.json') {
    Copy-Item 'global.json' 'global.json.bak'
    Get-Content -Path 'global.json' -Raw | ConvertFrom-Json
} else {
    [pscustomobject]@{}
}
if (-not $globalJson.PSObject.Properties['sdk']) {
    $globalJson | Add-Member -MemberType NoteProperty -Name 'sdk' -Value ([pscustomobject]@{})
}
$updates = [ordered]@{
    version = $sdkVersion
    allowPrerelease = $allowPrerelease
    rollForward = $rollForward
    paths = @('.dotnet', '$host$')
    errorMessage = $errorMessage
}
foreach ($entry in $updates.GetEnumerator()) {
    $property = $globalJson.sdk.PSObject.Properties[$entry.Key]
    if ($property) {
        $property.Value = $entry.Value
    } else {
        $globalJson.sdk | Add-Member -MemberType NoteProperty -Name $entry.Key -Value $entry.Value
    }
}
$globalJson | ConvertTo-Json -Depth 10 | Set-Content -Path 'global.json' -Encoding UTF8
if (-not (Test-Path .gitignore) -or -not (Select-String -Path .gitignore -Pattern '^\.dotnet/$' -Quiet)) {
    Add-Content -Path .gitignore -Value '.dotnet/'
}
if ($Workloads.Count -gt 0) { & "$installDir\dotnet.exe" workload install @Workloads }
Write-Host "Done. SDK: $SDK_VERSION"
```

将这些脚本提交到仓库，以便队友可以运行它们。

### 第 11 步 — 验证 SDK 解析

```bash
dotnet --version
```

输出应与本地安装的版本匹配。如果不匹配，请检查：`global.json` 位置、`paths` 数组内容、主机 dotnet 版本 ≥ 10。

### 第 12 步 — 总结并解释清理步骤

告诉用户：SDK 安装，`global.json` 配置，`.dotnet/` git 忽略，系统安装未受影响。清理：删除 `.dotnet/`，从 `global.json` 中删除 `paths`/`errorMessage`，可选删除安装脚本。包含最终的 `global.json` `sdk` 值（或简短片段），以便用户可以看到配置的版本、`paths` 和任何 `errorMessage`。如果请求了工作负载，请包含本地 `dotnet workload install ...` 命令使用情况和工作负载验证结果或精确的阻止器（如果工作负载无法安装）。

## 常见陷阱

| 陷阱 | 原因 | 修复 |
|---|---|---|
| `paths` 被忽略 | 主机 `dotnet` < v10 | 系统范围安装 .NET 10+ |
| 错误的 SDK 解析 | 父目录中的 `global.json` | 向上检查全局 `global.json` |
| 同事收到 "SDK 未找到" | `.dotnet/` git 忽略，未运行安装脚本 | 在 `global.json` 中使用 `errorMessage` |
| 工作负载缺失 | 使用系统 `dotnet` 而不是本地 | 使用 `./.dotnet/dotnet workload install` |
| `dotnet app.dll` 运行时错误 | `paths` 仅适用于 SDK，不适用于应用主机 | 使用 `dotnet run` 或设置 `DOTNET_ROOT` |
