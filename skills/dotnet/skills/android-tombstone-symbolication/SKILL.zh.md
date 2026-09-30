---
name: android-tombstone-symbolication
description: 在 Android 坟墓文件中符号化 .NET 运行时帧。从原生回溯中提取 BuildIds 和 PC 偏移量，从 Microsoft 符号服务器下载调试符号，并运行 llvm-symbolizer 以生成包含源文件和行号的功能名称。用于从坟墓文件中排查 .NET MAUI 或 Mono Android 应用崩溃，将 libmonosgen-2.0.so 或 libcoreclr.so 中的原生回溯帧解析为 .NET 运行时源代码，或调查源自 Android .NET 运行的 SIGABRT、SIGSEGV 或其他原生信号。不适用于纯 Java/Kotlin 崩溃、已在 logcat 中捕获的托管 .NET 异常或 iOS 崩溃日志。调用 Symbolicate-Tombstone.ps1 脚本、llvm-symbolizer 和 Microsoft 符号服务器。
---

# Android Tombstone .NET 符号化

将 .NET Android 应用崩溃（MAUI、Xamarin、Mono）的原生堆栈跟踪帧解析为函数名、源文件和行号，使用 ELF BuildIds 和 Microsoft 的符号服务器。

**输入：** Tombstone 文件或 logcat 崩溃输出、`llvm-symbolizer`（来自 Android NDK 或任何 LLVM 14+ 工具链）、用于符号下载的互联网访问。

**不使用时：** 崩溃是托管 .NET 异常（在 logcat 中可见，带有托管堆栈跟踪）、崩溃的库不是 .NET 组件（例如，`libart.so`）或 Tombstone 来自 iOS。

---

## 工作流程

### 第 1 步：解析 Tombstone 堆栈跟踪

每个堆栈跟踪帧的格式如下：

```
#NN pc OFFSET  /path/to/library.so (optional_symbol+0xNN) (BuildId: HEXSTRING)
```

提取：**帧编号**、**PC 偏移量**（十六进制，已相对于库）、**库名** 和 **BuildId**（32–40 个十六进制字符）。

默认情况下符号化所有线程（后台线程如 GC/终结器通常包含有用的 .NET 帧）。崩溃线程的堆栈跟踪首先列出；额外的线程出现在 `--- --- ---` 标记之后。

**格式说明：**
- 脚本自动检测带或不带 `backtrace:` 头的 `#NN pc` 帧行，并自动删除 logcat 时间戳/标签前缀。
- logcat 捕获的 Tombstone 常常省略 BuildIds。通过 `adb shell readelf -n`、CI 构建工件或 .NET 运行时 NuGet 包恢复。
- GitHub 问题粘贴可能将 `#1 pc` 损坏为问题链接 — 将 `org/repo#N pc` 替换为 `#N pc` 之前保存到文件。
- 如果脚本无法解析格式，则回退到手动提取 `#NN pc OFFSET library.so (BuildId: HEX)` 元组。

### 第 2 步：识别 .NET 运行时库

过滤帧以识别 .NET 运行时库：

| 库          | 运行时         |
|-------------|---------------|
| `libmonosgen-2.0.so` | Mono (MAUI、Xamarin、解释器) |
| `libcoreclr.so` | CoreCLR (JIT 模式) |
| `libSystem.*.so` | .NET BCL 原生组件 (`Native`、`Globalization.Native`、`IO.Compression.Native`、`Security.Cryptography.Native.OpenSsl`、`Net.Security.Native`) |

**原生 AOT：** 没有 `libcoreclr.so` 或 `libmonosgen-2.0.so` — 运行时静态链接到应用二进制文件（例如，`libMyApp.so`）。`libSystem.*.so` BCL 库保持独立，可以通过符号服务器符号化。对于应用二进制文件本身，需要应用自己的调试符号。

跳过 `libc.so`、`libart.so` 和其他 Android 系统库，除非用户特别要求。

### 第 3 步：下载调试符号

为每个唯一的 .NET BuildId 下载调试符号：

```
https://msdl.microsoft.com/download/symbols/_.debug/elf-buildid-sym-<BUILDID>/_.debug
```

```bash
curl -sL "https://msdl.microsoft.com/download/symbols/_.debug/elf-buildid-sym-1eb39fc72918c7c6c0c610b79eb3d3d47b2f81be/_.debug" \
  -o libmonosgen-2.0.so.debug
```

验证 `file libmonosgen-2.0.so.debug` — 应显示 `ELF 64-bit ... with debug_info, not stripped`。如果下载返回 404 或 HTML，则该构建未发布符号。不要添加或减去库基地址 — Tombstone 中的偏移量已相对于库。

### 第 4 步：符号化每个帧

```bash
llvm-symbolizer --obj=libmonosgen-2.0.so.debug -f -C 0x222098
```

输出：
```
ves_icall_System_Environment_FailFast
/__w/1/s/src/runtime/src/mono/mono/metadata/icall.c:6244
```

`/__w/1/s/` 前缀是 CI 工作区根目录 — 有意义路径从 `src/runtime/` 开始，映射到 [dotnet/dotnet](https://github.com/dotnet/dotnet) VMR。

### 第 5 步：展示符号化后的堆栈跟踪

将原始帧编号与解析的函数名和源位置组合：

```
#00  libc.so              abort+164
#01  libmonosgen-2.0.so   ves_icall_System_Environment_FailFast        (mono/metadata/icall.c:6244)
#02  libmonosgen-2.0.so   do_icall                                     (mono/mini/interp.c:2457)
#03  libmonosgen-2.0.so   mono_interp_exec_method                      (mono/mini/interp.c)
```

对于未解析的帧（`??`），保留原始行，包括 BuildId 和 PC 偏移量。

### 自动化脚本

[scripts/Symbolicate-Tombstone.ps1](scripts/Symbolicate-Tombstone.ps1) 自动化完整工作流程：

```powershell
pwsh scripts/Symbolicate-Tombstone.ps1 -TombstoneFile tombstone_01.txt -LlvmSymbolizer llvm-symbolizer
```

标志：`-CrashingThreadOnly`（限制为崩溃线程）、`-OutputFile path`（写入文件）、`-ParseOnly`（仅报告库/BuildIds/URLs，不下载）、`-SkipVersionLookup`（跳过运行时版本识别）。

---

## 查找 llvm-symbolizer

首先检查 **Android NDK**：`$ANDROID_NDK_ROOT/toolchains/llvm/prebuilt/*/bin/llvm-symbolizer` 或 `$ANDROID_HOME/ndk/*/toolchains/llvm/prebuilt/*/bin/llvm-symbolizer`。也可通过 `brew install llvm`、`apt install llvm` 或 macOS 上的 `xcrun --find llvm-symbolizer` 获得。

如果不可用，完成步骤 1–3 并展示下载命令和 `llvm-symbolizer` 命令供用户运行。不要浪费时间安装 LLVM。

---

## 理解输出

CI 源路径使用这些前缀：

| 路径前缀        | 映射到         |
|-----------------|---------------|
| `/__w/1/s/src/runtime/` | [dotnet/dotnet](https://github.com/dotnet/dotnet) VMR 中的 `src/runtime/` |
| `/__w/1/s/src/mono/` | VMR 中的 `src/mono/`（旧构建） |
| `/__w/1/s/`      | VMR 根目录     |

### 运行时版本识别

脚本通过匹配 BuildIds 来识别确切的 .NET 运行时版本。它搜索：SDK 包（`$DOTNET_ROOT/packs/`）、NuGet 缓存（`~/.nuget/packages/`），以及 NuGet.org 作为在线回退。找到后，它从 `.nuspec` `<repository commit="..." />` 元素中提取版本和源提交。传递 `-SkipVersionLookup` 以禁用。需要 `llvm-readelf`（从 NDK 自动发现）。

---

## 验证

1. `file <debug-file>` 显示 `ELF ... with debug_info, not stripped`
2. 至少有一个 .NET 帧解析为函数名（不是 `??`）
3. 解析路径包含可识别的 .NET 运行时结构（例如，`mono/metadata/`、`mono/mini/`）

## 停止信号

- **未找到 .NET 帧**：报告解析的帧并停止。
- **所有帧解析完毕**：展示符号化后的堆栈跟踪。不要跟踪到源或尝试构建/调试运行时。
- **符号不可用（404）**：每个 BuildId 尝试一次，然后停止。报告未符号化的帧及其 BuildIds 和偏移量。
- **llvm-symbolizer 不可用**：使用 `-ParseOnly`，展示手动命令。不要安装 LLVM。

## 常见陷阱

- **缺少 BuildIds**：logcat Tombstone 常常省略 BuildIds。通过：`adb shell readelf -n /path/to/lib.so`、CI 构建工件或运行时 NuGet 包（`~/.dotnet/packs/Microsoft.NETCore.App.Runtime.Mono.android-arm64/<version>/`）恢复。优先获取原始 Tombstone 文件（`adb shell cat /data/tombstones/tombstone_XX`），它们始终包含 BuildIds。
- **符号未找到（404）**：预发布/内部构建可能不发布符号。检查构建工件中的本地未剥离的 `.so`/`.so.dbg` 或 NuGet 运行时包。
- **原生 AOT**：Tombstone 中没有运行时 `.so` — 运行时在应用二进制文件中。`libSystem.*.so` BCL 库仍可通过符号服务器工作；应用二进制文件需要自己的调试符号。
- **错误的 llvm-symbolizer 版本**：使用 LLVM 14+ 以获得最佳 DWARF 兼容性。
- **多个 BuildIds**：每个 .NET 库有自己的 BuildId — 分别下载每个库的符号。
