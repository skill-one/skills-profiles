# Apple 平台崩溃日志 .NET 符号化

将 .NET MAUI 和 Mono 应用在 Apple 平台（iOS、tvOS、Mac Catalyst、macOS）上的崩溃的本地回溯帧解析为函数名、源文件和行号，使用 Mach-O UUID 和 dSYM 调试符号包。

**输入：** 崩溃日志文件（`.ips` JSON 格式，iOS 15+ / macOS 12+），`atos`（来自 Xcode），可选地连接的 iOS 设备以拉取崩溃日志。

**不使用时：** 崩溃的库不是 .NET 组件（例如，纯 Swift/UIKit），或者崩溃日志是 Android 坟墓石。

---

## 工作流程

### 第 1 步：解析 .ips 崩溃日志

**格式检查：** 在继续之前，请验证文件是 `.ips` JSON 格式。第一行必须是有效的 JSON。如果文件是纯文本（例如，带有 `#NN pc` 堆栈帧行的 Android 坟墓石，或旧的 Apple `.crash` 文本格式），**立即停止**——此工作流程不适用。向用户报告格式不匹配，不要尝试任何符号化。

`.ips` 文件是**两部分的 JSON**：第一行是元数据标题；其余行是单独的 JSON 崩溃正文。分别解析它们：

```python
lines = open('crash.ips').readlines()
metadata = json.loads(lines[0])           # app_name, bundleID, os_version, slice_uuid
crash    = json.loads(''.join(lines[1:])) # 完整的崩溃报告
```

崩溃正文中的关键字段：
- `usedImages[N]` 包含每个加载的二进制的 `name`、`base`（加载地址）、`uuid`、`arch`
- `threads[N].frames[M]` 包含 `imageOffset`、`imageIndex`；帧地址 = `usedImages[imageIndex].base + imageOffset`
- `exception.type`、`exception.signal`（例如，`EXC_CRASH` / `SIGABRT`）
- `asi`（应用程序特定信息）通常包含托管异常消息
- `lastExceptionBacktrace` 包含引发崩溃的异常的帧
- `faultingThread` 是 `threads` 数组中的索引

**解析技巧：** 一些 .ips 文件有大小写冲突的重复键（`vmRegionInfo` / `vmregioninfo`）。在解析之前对原始 JSON 进行预处理以重命名小写重复项。`asi` 字段可能不存在。

### 第 2 步：识别 .NET 运行时库

过滤 `usedImages` 以筛选出 .NET 运行时库：

| 库          | 运行时         |
|-------------|---------------|
| `libcoreclr` | CoreCLR 运行时 |
| `libmonosgen-2.0` | Mono 运行时   |
| `libSystem.Native` | .NET BCL 本地组件 |
| `libSystem.Globalization.Native` | .NET BCL 全球化 |
| `libSystem.Security.Cryptography.Native.Apple` | .NET BCL 加密 |
| `libSystem.IO.Compression.Native` | .NET BCL 压缩 |
| `libSystem.Net.Security.Native` | .NET BCL 网络安全 |

在 Apple 平台上这些作为 `.framework` 包提供，因此图像名称可能省略 `.dylib`。使用子字符串匹配（例如，`libcoreclr` 而不是 `libcoreclr.dylib`）。应用程序二进制文件可能会**两次**出现在 `usedImages` 中，具有不同的 UUID。

**应用程序二进制中的关键桥接函数：** `xamarin_process_managed_exception`（托管异常桥接到 ObjC NSException）、`xamarin_main`、`mono_jit_exec`、`coreclr_execute_assembly`。

**原生 AOT：** 运行时静态链接到应用程序二进制文件中。`libSystem.*` BCL 库保持为单独的。应用程序二进制文件需要其自己的从构建输出中获取的 dSYM。

除非特别要求，否则跳过 `libsystem_kernel.dylib`、`UIKitCore` 和其他 Apple 系统框架。

### 第 3 步：解释崩溃

**从 `asi`（应用程序特定信息）开始**——对于 .NET 崩溃，它通常包含托管异常类型和消息（例如，`XamlParseException`、`NullReferenceException`）。根本原因可能在这里已经可见。

然后检查**故障线程**（`threads[faultingThread]`）。在检查其他线程之前解释第 0 和第 1 个帧的含义。跨线程上下文（GC 状态、线程池）对于验证很有用，但不是因果关系的证据。

还检查 `lastExceptionBacktrace` 以获取通过 `xamarin_process_managed_exception` 等桥接函数的托管异常路径。

有时 .NET 运行时版本在 `usedImages` 中的图像路径中可见，特别是在 macOS 上使用共享框架安装或 NuGet-pack 风格布局时（例如，`.../Microsoft.NETCore.App/10.0.4/libcoreclr.dylib`）。然而，在 iOS 上，图像路径通常在应用程序包内（例如，`.../Frameworks/libcoreclr.framework/libcoreclr`），并且不嵌入运行时版本，因此您通常需要通过匹配 SDK 包或符号服务器下载来推断它，而不是依赖路径。

### 第 4 步：定位 dSYMs

对于每个需要符号化的 .NET 库，定位匹配 UUID 的 dSYM：

1. **Microsoft 符号服务器**（自动）：通过 `https://msdl.microsoft.com/download/symbols/_.dwarf/mach-uuid-sym-{UUID}/_.dwarf`（UUID 小写，无连字符）下载 `.dwarf`。转换为 `.dSYM` 包（使用 `usedImages[].name` 中的图像名称，例如，`libcoreclr`）：
   ```bash
   mkdir -p libcoreclr.dSYM/Contents/Resources/DWARF
   cp _.dwarf libcoreclr.dSYM/Contents/Resources/DWARF/libcoreclr
   ```
2. **构建输出**：`bin/Debug/net*-ios/ios-arm64/<App>.app.dSYM/`
3. **SDK 包**：`$DOTNET_ROOT/packs/Microsoft.NETCore.App.Runtime.<rid>/<version>/runtimes/<rid>/native/`
4. **NuGet 缓存**：`~/.nuget/packages/microsoft.netcore.app.runtime.<rid>/<version>/runtimes/<rid>/native/`
5. **`dotnet-symbol`**：`dotnet-symbol --symbols -o symbols-out <path-to-binary.dylib>`

始终验证：`dwarfdump --uuid <dsym>` 必须与崩溃日志中的 UUID 完全匹配。

### 第 5 步：使用 atos 符号化

```bash
atos -arch arm64 -o <path.dSYM/Contents/Resources/DWARF/binary_name> -l <load_address> <frame_addresses...>
```

- `-o` 指向 `.dSYM` 包内的 DWARF 二进制（`Contents/Resources/DWARF/`），而不是包本身
- `-l` 是从 `usedImages[N].base` 的加载地址
- 使用 `usedImages[N].arch` 中的 `arch`（通常是 `arm64`，可能是 `arm64e`）
- 每次调用传递多个地址以进行批量符号化

```bash
# 示例：符号化 libcoreclr 帧
atos -arch arm64 -o libcoreclr.dSYM/Contents/Resources/DWARF/libcoreclr -l 0x104000000 0x104522098 0x1043c0014
```

从输出中删除 `/__w/1/s/` CI 工作区前缀——有意义的路径从 `src/runtime/` 开始，映射到 [dotnet/dotnet](https://github.com/dotnet/dotnet) VMR。

### 自动化脚本

[scripts/Symbolicate-Crash.ps1](scripts/Symbolicate-Crash.ps1) 自动化完整工作流程（解析、dSYM 查找、符号下载和符号化）。相对于此 SKILL.md 文件解析路径。

```powershell
# $SKILL_DIR 是包含此 SKILL.md 的目录
pwsh "$SKILL_DIR/scripts/Symbolicate-Crash.ps1" -CrashFile MyApp-2026-02-25.ips
```

从 `-ParseOnly` 开始以快速概述，而无需 `atos`。脚本在本地 dSYMs 缺失时自动从 Microsoft 符号服务器下载符号。

标志：`-CrashingThreadOnly`、`-OutputFile path`、`-ParseOnly`、`-SkipVersionLookup`、`-SkipSymbolDownload`、`-SymbolCacheDir path`、`-DsymSearchPaths path1,path2`。

---

## 获取崩溃日志

使用 `idevicecrashreport`（来自 [libimobiledevice](https://libimobiledevice.org/)）从连接的 iOS 设备拉取崩溃日志：

```bash
idevicecrashreport -e /tmp/crashlogs/
find /tmp/crashlogs/ -iname '*MyApp*' -name '*.ips'
```

也可在 **Xcode > Window > Devices and Simulators > View Device Logs** 中找到，或在 `~/Library/Logs/CrashReporter/`（Mac Catalyst）、`~/Library/Logs/DiagnosticReports/`（macOS）中找到。

---

## 验证

1. `dwarfdump --uuid <dsym>` 与崩溃日志中的 UUID 匹配
2. 至少有一个 .NET 帧解析为函数名（而不是原始地址）
3. 解析的路径包含可识别的 .NET 运行时结构（例如，`src/coreclr/`、`mono/metadata/`、`mono/mini/`）

## 停止信号

- **错误的文件格式**：如果文件不是 `.ips` JSON（例如，带有 `#NN pc` 堆栈帧的 Android 坟墓石，旧的 `.crash` 文本格式），**立即停止**——向用户报告格式不匹配，不要继续进行任何符号化。不要尝试使用其他工具或工作流程进行符号化。
- **未找到 .NET 帧**：报告解析的帧并停止。
- **所有帧解析完毕**：显示符号化的回溯并简要分析崩溃（故障线程、异常类型、可能区域）。如果用户要求更深入的调查，请继续。
- **dSYM 不可用 / UUID 不匹配**：报告未符号化的帧及其 UUID 和地址。建议定位原始构建工件。
- **atos 不可用**：为用户提供手动 `atos` 命令。不要安装 Xcode。`atos` 随 Xcode 命令行工具提供（`xcode-select --install`）。

## 参考

- **IPS 格式详细信息**：有关额外的 .ips 解析细节和 macOS 符号包差异，请参阅 [references/ips-crash-format.md](references/ips-crash-format.md)。
