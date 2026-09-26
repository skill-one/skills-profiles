# rev-u3d-dump - Unity IL2CPP 符号提取工具

从 Unity IL2CPP 构建中提取 C# 方法名称、地址和类型定义，用于 IDA/Ghidra 分析。

---

## 概述

Unity IL2CPP 将 C# 编译为原生代码。原始的类/方法名称在二进制文件中被移除，但保留在 `global-metadata.dat` 中。此工具恢复原生函数地址与其原始 C# 名称之间的映射关系。

### Unity 构建中的关键文件

| 文件 | 位置 | 用途 |
|------|------|------|
| 原生二进制文件 | iOS: `Frameworks/UnityFramework.framework/UnityFramework`<br>Android: `lib/{arch}/libil2cpp.so` | 编译的 C# 代码 (Mach-O / ELF) |
| 元数据 | `Data/Managed/Metadata/global-metadata.dat` | 所有类型/方法/字符串信息 |

---

## 工具选择

### Il2CppDumper (推荐用于元数据 v39+)

使用 **v39 分支**用于 Unity 6+ 构建：

- 仓库: `https://github.com/roytu/Il2CppDumper` (分支: `v39`)
- 支持 元数据 v24–v39
- 输出 `script.json` 包含函数地址 — 准备好用于 IDA/Ghidra 导入

原始的 Il2CppDumper (`https://github.com/Perfare/Il2CppDumper`) 仅支持到 v29。

### Cpp2IL (替代方案)

- 仓库: `https://github.com/SamboyCoding/Cpp2IL`
- 支持 元数据 v39，但哑 DLL 缺少 `[Address]` 属性
- 适用于 C# 源代码重建，不适合 IDA 导入

---

## 分步工作流程

### 第 1 步：定位 IL2CPP 文件

**iOS (IPA):**
```bash
# 解压 IPA
unzip -o app.ipa -d .

# 二进制文件
BINARY="Payload/<AppName>.app/Frameworks/UnityFramework.framework/UnityFramework"

# 元数据
METADATA="Payload/<AppName>.app/Data/Managed/Metadata/global-metadata.dat"
```

**Android (APK):**
```bash
# 解压 APK
unzip -o app.apk -d .

# 二进制文件 (选择目标架构)
BINARY="lib/arm64-v8a/libil2cpp.so"

# 元数据
METADATA="assets/bin/Data/Managed/Metadata/global-metadata.dat"
```

### 第 2 步：检查元数据版本

```bash
# 前 8 个字节: 魔数 (4) + 版本 (4)，小端格式
xxd -l 8 "$METADATA"
# 预期: af1b b1fa 2700 0000  → 魔数正常，版本 = 0x27 = 39
```

| 版本 | Unity | 工具 |
|------|------|------|
| ≤ 29 | Unity 2021 及更早版本 | 原始 Il2CppDumper |
| 31 | Unity 2022 | 原始 Il2CppDumper (部分支持) |
| 39 | Unity 6 (6000.x) | **roytu/Il2CppDumper v39 分支** |

### 第 3 步：构建并运行 Il2CppDumper (v39 分支)

```bash
# 克隆 v39 分支
git clone -b v39 https://github.com/roytu/Il2CppDumper.git

# 构建
cd Il2CppDumper
DOTNET_ROLL_FORWARD=LatestMajor dotnet build -c Release

# 运行 (使用 net8.0 框架)
DOTNET_ROLL_FORWARD=LatestMajor dotnet run \
  --project Il2CppDumper/Il2CppDumper.csproj \
  -c Release --framework net8.0 \
  -- "$BINARY" "$METADATA" output_dir
```

**注意:**
- `DOTNET_ROLL_FORWARD=LatestMajor` 允许在 .NET 9/10 上运行，即使项目目标是 .NET 6/8
- 非交互模式下的退出代码 134 是正常的 (由 `Console.ReadKey()` 引起)
- 在 macOS 上，如果二进制文件被 SIGKILL 终止，请使用 ad-hoc 签名: `codesign -s - <binary>`

### 第 4 步：验证输出

成功运行会在输出目录生成以下文件：

| 文件 | 大小 (典型) | 用途 |
|------|-------------|------|
| `script.json` | 50–100 MB | 函数地址 + 名称 + 签名 (IDA/Ghidra 导入) |
| `dump.cs` | 10–30 MB | 带有 RVA/VA 地址的 C# 类提取 |
| `il2cpp.h` | 50–100 MB | 用于类型导入的 C 结构定义 |
| `ida_py3.py` | ~2 KB | IDA Python 导入脚本 |

检查 `script.json` 格式:
```json
{
  "ScriptMethod": [
    {
      "Address": 40865744,
      "Name": "ClassName$$MethodName",
      "Signature": "ReturnType ClassName__MethodName (args...);",
      "TypeSignature": "viii"
    }
  ]
}
```

检查 `dump.cs` 格式:
```csharp
// RVA: 0x1A2B3C4 Offset: 0x1A2B3C4 VA: 0x1A2B3C4
public void MethodName() { }
```

### 第 5 步：导入到 IDA

1. 在 IDA 中打开原生二进制文件 (UnityFramework / libil2cpp.so)
2. 将 `script.json` 和 `ida_py3.py` 放在同一目录
3. `File → Script file...` → 选择 `ida_py3.py`
4. 脚本自动读取 `script.json` 并重命名所有函数
5. 可选: `File → Load file → Parse C header file...` → 选择 `il2cpp.h` 用于结构类型

### 第 5 步 (替代方案): 导入到 Ghidra

1. 在 Ghidra 中打开二进制文件
2. 使用 Il2CppDumper 中的 `ghidra.py` 或 `ghidra_with_struct.py` 脚本
3. `Window → Script Manager → Run`，并将 `script.json` 放在同一目录

---

## 故障排除

| 错误 | 原因 | 解决方法 |
|------|------|----------|
| `not a supported version[39]` | 使用原始 Il2CppDumper | 切换到 roytu/Il2CppDumper v39 分支 |
| 退出代码 137 (SIGKILL) | macOS 未经签名的二进制文件 | `codesign -s - <binary>` |
| `Cannot read keys` (退出代码 134) | 非交互式控制台 | 忽略 — 提取完成成功 |
| `DOTNET_ROLL_FORWARD` 错误 | .NET 版本不匹配 | 设置 `DOTNET_ROLL_FORWARD=LatestMajor` |
| 空输出 | 错误的二进制/元数据组合 | 验证两个文件是否来自同一构建 |

---

## 输出使用技巧

- `dump.cs` 是最快的参考 — 使用 RVA 地址搜索类/方法名称
- `script.json` 中的地址值是十进制 — 转换为十六进制用于 IDA: `hex(40865744)` → `0x26F8FD0`
- `dump.cs` 中的字段偏移 (例如，`// 0x20`) 是相对于对象基址的，适用于使用 Frida 进行内存检查
