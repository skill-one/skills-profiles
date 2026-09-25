# .NET 崩溃转储收集

此技能用于配置和收集 Linux、macOS 和 Windows 上的现代 .NET 应用程序（CoreCLR 和 NativeAOT）的崩溃转储——包括容器。

## 停止信号

🚨 **开始任何工作流程前请阅读。**

- **在启用或收集转储后停止。** 不要打开、分析或处理转储文件。
- **如果用户已经有一个转储文件**，此技能不涵盖分析。告知他们分析不在范围内。
- **不要安装分析工具**（dotnet-dump analyze、windbg）。仅安装收集工具（dotnet-dump collect）。在 macOS 上使用 `lldb` 进行按需转储捕获是允许的——它随 Xcode 命令行工具一起提供，并且不用于分析。
- **不要追踪崩溃的根本原因**。报告转储文件位置并继续。
- **不要修改应用程序代码。** 配置仅限于环境（环境变量、操作系统设置、容器规格）。

## 第 1 步 — 确定场景

询问或确定：

1. **目标**：启用自动崩溃转储，还是立即从正在运行的过程捕获转储？
2. **平台**：Linux、macOS 还是 Windows？是否在容器（Docker/Kubernetes）中运行？
3. **运行时**：CoreCLR 还是 NativeAOT？

### 检测 CoreCLR 与 NativeAOT

**从二进制文件（Linux/macOS）：**
```bash
# CoreCLR — 包含 IL 元数据 / 管理入口点
strings <binary> | grep -q "CorExeMain" && echo "CoreCLR"

# NativeAOT — 包含 Redhawk 运行时符号
strings <binary> | grep -q "Rhp" && echo "NativeAOT"

# 在 macOS/Linux 上，还尝试：
nm <binary> 2>/dev/null | grep -qi "Rhp" && echo "NativeAOT"
```

**从二进制文件（Windows）：**
```powershell
# CoreCLR — 包含 CLI 头（IL 入口点）
dumpbin /clrheader <binary.exe> | Select-String "CLI Header" -Quiet

# NativeAOT — 没有 CLI 头，包含 Redhawk 符号
dumpbin /symbols <binary.exe> | Select-String "Rhp" -Quiet
```

**从正在运行的过程（Linux）：**
```bash
# 解析二进制文件，然后使用相同的文件检查
BINARY=$(readlink /proc/<pid>/exe)
strings "$BINARY" | grep -q "CorExeMain" && echo "CoreCLR" || echo "NativeAOT"
```

**从正在运行的过程（macOS）：**
```bash
# 从正在运行的过程解析二进制路径
BINARY=$(ps -o comm= -p <pid>)
strings "$BINARY" | grep -q "CorExeMain" && echo "CoreCLR" || echo "NativeAOT"
```

**从正在运行的过程（Windows PowerShell）：**
```powershell
# CoreCLR — 加载 coreclr.dll
(Get-Process -Id <pid>).Modules.ModuleName -contains "coreclr.dll"

# .NET Framework — 加载 clr.dll（此技能不适用）
(Get-Process -Id <pid>).Modules.ModuleName -contains "clr.dll"
```

> **如果应用程序是 .NET Framework (`clr.dll`)，停止。** 此技能仅涵盖现代 .NET（CoreCLR 和 NativeAOT）。
>
> **如果未检测到 CoreCLR 或 NativeAOT，停止。** 此技能仅适用于 .NET 应用程序——不要继续。

## 第 2 步 — 加载相应的参考文件

根据第 1 步确定的场景，阅读相关的参考文件：

| 场景 | 参考 |
|------|------|
| CoreCLR 应用（任何平台） | `references/coreclr-dumps.md` |
| NativeAOT 应用（任何平台） | `references/nativeaot-dumps.md` |
| Docker 或 Kubernetes 中的任何应用 | `references/container-dumps.md`（然后还加载特定于运行时的参考） |

## 第 3 步 — 执行

按照加载的参考文件中的说明进行配置或收集转储。始终：

1. **确认转储输出目录存在** 并具有写入权限，然后再启用收集。
2. **收集成功后向用户报告转储文件路径**。
3. **验证配置是否生效** —— 对于环境变量，使用 `echo`；对于操作系统设置，读取它们。
4. **提醒用户如果他们暂时启用了自动转储，请禁用**——删除或取消设置 `DOTNET_DbgEnableMiniDump` 和相关环境变量，以避免积累转储文件。
