# .NET MAUI 诊断工具

验证和修复 .NET MAUI 开发环境。所有版本要求都动态地从 NuGet API 中发现——从不硬编码版本。

## 使用场景

- 设置新的 .NET MAUI 开发环境
- 构建错误提示缺少 SDK、工作负载、JDK 或 Android 组件
- 出现 "未找到 Android SDK"、"Java 版本" 或 "未找到 Xcode" 等错误
- SDK 或操作系统更新后的环境健康检查

## 不适用场景

- 非 MAUI 的 .NET 项目（使用标准的 .NET SDK 故障排除方法）
- Xamarin.Forms 应用（具有不同的工具链和工作负载要求）
- 与环境设置无关的运行时应用崩溃
- 应用商店发布或签名问题
- IDE 特定问题（Visual Studio 或 VS Code 配置）

## 重要提示：.NET 版本时效性

您的训练数据可能已过时，无法反映最新的 .NET 版本。.NET 每年都会发布新的主要版本（11 月）。始终检查 releases-index.json（任务 2）以发现**最新的活跃主要版本**——不要假设您的训练数据反映了当前版本。例如，如果您知道 .NET 9.0，但发布索引显示 .NET 10.0 是活跃的，请使用 .NET 10.0。

## 输入

- 运行 macOS、Windows 或 Linux 的开发机器
- Shell 访问（macOS/Linux 上的 Bash，Windows 上的 PowerShell）
- 用于 NuGet API 查询和 SDK 下载的互联网访问
- 可能需要管理员/sudo 访问权限来安装 SDK 和工作负载
- **Bash 前置条件**：`curl`、`jq` 和 `unzip`（macOS/Linux）
- **PowerShell 前置条件**：`Invoke-RestMethod` 和 `System.IO.Compression`（Windows 上内置）

## 行为

- 自主运行所有任务
- 每次修复后重新验证
- 迭代直到完成或没有更多操作可能
- 检测到平台（任务 1）后，仅加载匹配的平台特定引用

## 工作流程

### 任务 1：检测环境

```bash
# macOS
sw_vers && uname -m

# Windows
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"

# Linux
cat /etc/os-release && uname -m
```

检测后，加载匹配的平台引用：
- **macOS**：`references/platform-requirements-macos.md`、`references/installation-commands-macos.md`、`references/troubleshooting-macos.md`
- **Windows**：`references/platform-requirements-windows.md`、`references/installation-commands-windows.md`、`references/troubleshooting-windows.md`
- **Linux**：`references/platform-requirements-linux.md`

### 任务 2：检查 .NET SDK

```bash
dotnet --info
```

与 https://dotnetcli.blob.core.windows.net/dotnet/release-metadata/releases-index.json 中的 `latest-sdk` 对比，其中 `support-phase` 为 `"active"`。

### 任务 3：检查 MAUI 工作负载

| 工作负载 | macOS | Windows | Linux |
|----------|-------|---------|-------|
| `maui` | 需要 | 需要 | ❌ 使用 `maui-android` |
| `maui-android` | 别名 | 别名 | 需要 |
| `android` | 需要 | 需要 | 需要 |
| `ios` | 需要 | 可选 | N/A |

### 任务 4：从 NuGet 发现要求

参考 `references/workload-dependencies-discovery.md` 了解完整流程。

查询 NuGet 以获取工作负载清单 → 提取 `WorkloadDependencies.json` → 获取：
- `jdk.version` 范围和 `jdk.recommendedVersion`
- `androidsdk.packages`、`buildToolsVersion`、`apiLevel`
- `xcode.version` 范围

### 任务 5：验证 Java JDK

**仅支持 Microsoft OpenJDK。** 验证 `java -version` 输出是否包含 "Microsoft"。参考 `references/microsoft-openjdk.md` 了解检测路径。

> 使用 WorkloadDependencies.json 推荐的 JDK 版本 (`jdk.recommendedVersion`)，确保它满足 `jdk.version` 范围。不要硬编码 JDK 版本。

**不需要 JAVA_HOME。** .NET MAUI 工具会自动检测 Microsoft OpenJDK 安装路径。不要告诉用户设置 JAVA_HOME——这是不必要的，并且可能导致指向非 Microsoft JDK。

| JAVA_HOME 状态 | OK? | 操作 |
|-----------------|-----|------|
| 未设置 | ✅ | 无需操作——自动检测有效 |
| 设置为 Microsoft JDK | ✅ | 无需操作 |
| 设置为非 Microsoft JDK | ⚠️ | **报告为异常**——让用户决定是否取消设置或重定向 |

### 任务 6：验证 Android SDK

检查 `androidsdk.packages`、`buildToolsVersion`、`apiLevel`（任务 4）。参考 `references/installation-commands.md` 了解 sdkmanager 命令。

### 任务 7：验证 Xcode（仅 macOS）

```bash
xcodebuild -version
```

与任务 4 中的 `xcode.version` 范围对比。参考 `references/installation-commands-macos.md`。

### 任务 8：验证 Windows SDK（仅 Windows）

Windows SDK 通常作为 .NET MAUI 工作负载或 Visual Studio 的一部分安装。参考 `references/installation-commands-windows.md`。

### 任务 9：修复

参考 `references/installation-commands.md` 了解所有命令。

关键规则：
- **工作负载**：始终使用 `--version` 标志。不要使用 `workload update` 或 `workload repair`。
- **JDK**：仅安装 Microsoft OpenJDK。不要设置 JAVA_HOME（自动检测）。
- **Android SDK**：使用 `sdkmanager`（来自 Android SDK 命令行工具）。在 Windows 上使用 `sdkmanager.bat`。

### 任务 10：重新验证

每次修复后，重新运行相关的验证任务。迭代直到所有检查通过。

## 验证

成功运行将产生：
- 安装并匹配活跃版本的 .NET SDK
- 所有必需的工作负载安装并具有一致版本
- 检测到 Microsoft OpenJDK（`java -version` 包含 "Microsoft"）
- 所有必需的 Android SDK 包按 WorkloadDependencies.json 安装
- Xcode 版本在支持范围内（仅 macOS）
- Windows SDK 检测到（仅 Windows）

### 构建验证（推荐）

所有检查通过后，创建并构建一个测试项目以确认环境实际可用：

```bash
TEMP_DIR=$(mktemp -d)
dotnet new maui -o "$TEMP_DIR/MauiTest"
dotnet build "$TEMP_DIR/MauiTest"
rm -rf "$TEMP_DIR"
```

在 Windows 上，使用 `$env:TEMP` 或 `New-TemporaryFile` 作为临时目录。

如果构建成功，环境已验证。如果失败，使用错误输出诊断剩余问题。

### 运行验证（可选——先询问用户）

成功构建后，**询问用户**是否希望在目标平台上启动应用以进行端到端验证：

```bash
# 将 net10.0 替换为当前的主要 .NET 版本
dotnet build -t:Run -f net10.0-android
dotnet build -t:Run -f net10.0-ios        # 仅 macOS
dotnet build -t:Run -f net10.0-maccatalyst # 仅 macOS
dotnet build -t:Run -f net10.0-windows    # 仅 Windows
```

仅运行与用户平台和意图相关的目标框架。此步骤将部署到模拟器/模拟器/设备，因此在进行之前请与用户确认。

## 常见陷阱

- **`maui` vs `maui-android` 工作负载**：在 Linux 上，`maui` 元工作负载不可用——使用 `maui-android`。在 macOS/Windows 上，`maui` 安装所有平台工作负载。
- **`workload update` / `workload repair`**：不要使用这些命令。始终使用显式的 `--version` 标志安装工作负载以确保版本一致性。
- **非 Microsoft JDK**：仅支持 Microsoft OpenJDK。其他发行版（Oracle、Adoptium、Azul）即使版本正确也会导致构建失败。
- **不必要的 JAVA_HOME**：不要设置 JAVA_HOME。MAUI 会自动检测已知安装路径的 JDK。如果 JAVA_HOME 设置为非 Microsoft JDK（例如 Temurin），请将其报告为异常——它可能覆盖自动检测并导致失败。让用户决定是否取消设置。
- **硬编码版本**：不要硬编码 SDK、工作负载或依赖版本。始终从 NuGet API 动态发现它们（参考任务 4）。
- **Windows 上的 Android SDK `sdkmanager`**：在 Windows 上使用 `sdkmanager.bat`，而不是 `sdkmanager`。
- **过时的训练数据**：LLM 训练数据可能引用过时的 .NET 版本。始终检查 releases-index.json 以发现当前的活跃版本。

## 参考

- `references/workload-dependencies-discovery.md` — NuGet API 发现流程
- `references/microsoft-openjdk.md` — JDK 检测路径、识别、JAVA_HOME
- `references/installation-commands.md` — .NET 工作负载、Android SDK（sdkmanager）
- `references/troubleshooting.md` — 常见错误和解决方案
- `references/platform-requirements-{platform}.md` — 平台特定要求
- `references/installation-commands-{platform}.md` — 平台特定安装命令
- `references/troubleshooting-{platform}.md` — 平台特定故障排除

官方文档：
- [.NET MAUI 安装](https://learn.microsoft.com/en-us/dotnet/maui/get-started/installation)
- [.NET SDK 下载](https://dotnet.microsoft.com/download)
- [Microsoft OpenJDK](https://learn.microsoft.com/en-us/java/openjdk/install)
- [Android SDK 命令行工具](https://developer.android.com/studio#command-line-tools-only)
- [Xcode 下载](https://developer.apple.com/xcode/)
