# .NET P/Invoke

从 .NET 调用原生代码功能强大但要求严格。错误的签名、乱码的字符串以及泄漏或释放的内存是最常见的错误来源——所有这些都可能表现为间歇性崩溃、静默数据损坏或远离实际缺陷的访问违规。

这项技能涵盖了 `DllImport`（自 .NET Framework 1.0 起可用）和 `LibraryImport`（源生成，.NET 7+）。针对 .NET Framework 时，始终使用 `DllImport`。针对 .NET 7+ 时，对于新代码优先考虑 `LibraryImport`。当原生 AOT 是要求时，`LibraryImport` 是唯一的选择。

## 何时使用这项技能

- 从 C/C++ 头文件编写新的 `[DllImport]` 或 `[LibraryImport]` 声明
- 审查 P/Invoke 签名以确保正确性（类型大小、调用约定、字符串编码）
- 为 .NET 封装整个 C 库
- 调试原生边界处的 `AccessViolationException`、`DllNotFoundException` 或静默数据损坏
- 将 `DllImport` 声明迁移到 `LibraryImport` 以兼容 AOT/修剪
- 诊断涉及原生句柄或缓冲区的内存泄漏或堆损坏

## 停止信号

- **仅单个函数？** 映射签名（步骤 1-3），仅在相关时处理字符串/内存，跳过工具和迁移部分。
- **不迁移** 现有的 `DllImport` 到 `LibraryImport`，除非用户要求或 AOT/修剪是明确要求。
- **不推荐 CsWin32** 除非目标是特定的 Win32 API。
- **不生成回调**（步骤 8）除非原生 API 需要函数指针。
- **需要审查请求？** 使用验证清单——不要重写正常工作的代码。

## 输入

| 输入 | 是否必需 | 描述 |
|-------|----------|-------------|
| 原生头文件或文档 | 是 | C/C++ 函数签名、结构定义、调用约定 |
| 目标框架 | 是 | 确定是否使用 `DllImport` 或 `LibraryImport` |
| 目标平台 | 推荐 | 影响类型大小（`long`、`size_t`）和库命名 |
| 内存所有权契约 | 是 | 谁分配，谁释放每个缓冲区或句柄 |

**代理行为：** 当文档和原生头文件不一致时，始终信任头文件。在线文档（包括官方 Win32 API 文档）经常省略或简化有关类型、调用约定和结构布局的详细信息，而这些信息对于正确的 P/Invoke 签名至关重要。

---

## 工作流程

### 步骤 1：选择 DllImport 或 LibraryImport

| 方面 | `DllImport` | `LibraryImport` (.NET 7+) |
|--------|-------------|---------------------------|
| **机制** | 运行时封送处理 | 源生成器（编译时） |
| **AOT / 修剪安全** | 否 | 是 |
| **字符串封送处理** | `CharSet` 枚举 | `StringMarshalling` 枚举 |
| **错误处理** | `SetLastError` | `SetLastPInvokeError` |
| **可用性** | .NET Framework 1.0+ | 仅 .NET 7+ |

### 步骤 2：将原生类型映射到 .NET 类型

最危险的映射——这些是大多数错误的原因：

| C / Win32 类型 | .NET 类型 | 原因 |
|----------------|-----------|-----|
| `long` | **`CLong`** | Windows 上 32 位，64 位 Unix 上 64 位。使用 `LibraryImport` 时，需要 `[assembly: DisableRuntimeMarshalling]` |
| `size_t` | `nuint` / `UIntPtr` | 指针大小。在 .NET 8+ 上使用 `nuint`，在早期 .NET 上使用 `UIntPtr`。永远不要使用 `ulong` |
| `BOOL` (Win32) | `int` | 不是 `bool`——Win32 `BOOL` 是 4 字节 |
| `bool` (C99) | `[MarshalAs(UnmanagedType.U1)] bool` | 必须指定 1 字节封送 |
| `HANDLE`, `HWND` | `SafeHandle` | 优先于原始 `IntPtr` |
| `LPWSTR` / `wchar_t*` | `string` | Windows 上 UTF-16（最低成本的 `in` 字符串）。在跨平台代码中避免使用——`wchar_t` 宽度由编译器定义（非 Windows 上通常是 UTF-32） |
| `LPSTR` / `char*` | `string` | 必须指定编码（ANSI 或 UTF-8）。始终需要封送处理成本以用于 `in` 参数 |

**有关完整的类型映射表、结构布局和可空类型规则**，请参阅 [references/type-mapping.md](references/type-mapping.md)。

> ❌ **永远不要** 使用 `int` 或 `long` 作为 C `long`——Windows 上是 32 位，Unix 上是 64 位。始终使用 `CLong`。
> ❌ **永远不要** 使用 `ulong` 作为 `size_t`——在 32 位上会导致栈损坏。使用 `nuint` 或 `UIntPtr`。
> ❌ **永远不要** 在没有 `MarshalAs` 的情况下使用 `bool`——默认封送大小是错误的。

### 步骤 3：编写声明

给定一个 C 头文件：

```c
int32_t process_records(const Record* records, size_t count, uint32_t* out_processed);
```

**DllImport:**

```csharp
[DllImport("mylib")]
private static extern int ProcessRecords(
    [In] Record[] records, UIntPtr count, out uint outProcessed);
```

**LibraryImport:**

```csharp
[LibraryImport("mylib")]
internal static partial int ProcessRecords(
    [In] Record[] records, nuint count, out uint outProcessed);
```

调用约定仅在针对 Windows x86（32 位）时需要指定，此时 `Cdecl` 和 `StdCall` 不同。在 x64、ARM 和 ARM64 上，调用约定是单一的，不需要此属性。

**代理行为：** 如果你检测到 Windows x86 是目标——通过项目属性（例如，`<PlatformTarget>x86</PlatformTarget>`）、运行时标识符（例如，`win-x86`）、构建脚本、注释或开发者说明——请向开发者报告并建议在所有 P/Invoke 声明中显式指定调用约定。

```csharp
// DllImport (x86 目标)
[DllImport("mylib", CallingConvention = CallingConvention.Cdecl)]

// LibraryImport (x86 目标)
[LibraryImport("mylib")]
[UnmanagedCallConv(CallConvs = [typeof(CallConvCdecl)])]
```

如果托管方法名与原生导出名不同，请指定 `EntryPoint` 以避免 `EntryPointNotFoundException`：

```csharp
// DllImport
[DllImport("mylib", EntryPoint = "process_records")]
private static extern int ProcessRecords(
    [In] Record[] records, UIntPtr count, out uint outProcessed);

// LibraryImport
[LibraryImport("mylib", EntryPoint = "process_records")]
internal static partial int ProcessRecords(
    [In] Record[] records, nuint count, out uint outProcessed);
```

### 步骤 4：正确处理字符串

1. **了解原生函数期望的编码。** 没有安全的默认值。
2. **Windows API：** 始终调用 `W`（UTF-16）变体。`A` 变体需要特定原因和显式的 ANSI 编码。
3. **跨平台 C 库：** 通常期望 UTF-8。
4. **显式指定编码。** 永远不要依赖 `CharSet.Auto`。
5. **永远不要** 为输出缓冲区引入 `StringBuilder`。

> ❌ **永远不要** 依赖 `CharSet.Auto` 或省略字符串编码——没有安全的默认值。

```csharp
// DllImport — Windows API (UTF-16)
[DllImport("kernel32.dll", CharSet = CharSet.Unicode, SetLastError = true)]
private static extern int GetModuleFileNameW(
    IntPtr hModule, [Out] char[] filename, int size);

// DllImport — 跨平台 C 库 (UTF-8)
[DllImport("mylib")]
private static extern int SetName(
    [MarshalAs(UnmanagedType.LPUTF8Str)] string name);

// LibraryImport — UTF-16
[LibraryImport("kernel32", StringMarshalling = StringMarshalling.Utf16,
    SetLastPInvokeError = true)]
internal static partial int GetModuleFileNameW(
    IntPtr hModule, [Out] char[] filename, int size);

// LibraryImport — UTF-8
[LibraryImport("mylib", StringMarshalling = StringMarshalling.Utf8)]
internal static partial int SetName(string name);
```

**字符串生命周期警告：** 封送的字符串在调用返回后会被释放。如果原生代码存储了指针（而不是复制），则必须手动管理生命周期。在 Windows 或 .NET Framework 上，`CoTaskMemAlloc`/`CoTaskMemFree` 是跨边界所有权的首选；在非 Windows 目标上，使用 `NativeMemory` API。库可能有自己的分配器，必须使用它。

### 步骤 5：建立内存所有权

当内存跨越边界时，必须且仅有一方拥有它——并且双方必须达成一致。

> ❌ **永远不要** 使用不匹配的分配器释放——在 `malloc` 分配的内存上使用 `Marshal.FreeHGlobal` 是堆损坏。

**模型 1——调用者分配，调用者释放（最安全）：**

```csharp
[LibraryImport("mylib")]
private static partial int GetName(
    Span<byte> buffer, nuint bufferSize, out nuint actualSize);

public static string GetName()
{
    Span<byte> buffer = stackalloc byte[256];
    int result = GetName(buffer, (nuint)buffer.Length, out nuint actualSize);
    if (result != 0) throw new InvalidOperationException($"Failed: {result}");
    return Encoding.UTF8.GetString(buffer[..(int)actualSize]);
}
```

**模型 2——调用者分配，调用者释放（Win32 中常见）：**

```csharp
[LibraryImport("mylib")]
private static partial IntPtr GetVersion();
[LibraryImport("mylib")]
private static partial void FreeString(IntPtr s);

public static string GetVersion()
{
    IntPtr ptr = GetVersion();
    try { return Marshal.PtrToStringUTF8(ptr) ?? throw new InvalidOperationException(); }
    finally { FreeString(ptr); } // 必须使用库自己的释放函数
}
```

**关键规则：** 始终使用匹配的分配器释放。永远不要使用 `Marshal.FreeHGlobal` 或 `Marshal.FreeCoTaskMem` 在 `malloc` 分配的内存上。

**固定托管对象**——当原生代码存储指针或运行异步时：

```csharp
// 同步：使用 fixed
public static unsafe void ProcessSync(byte[] data)
{
    fixed (byte* ptr = data) { ProcessData(ptr, (nuint)data.Length); }
}

// 异步：使用 GCHandle
var gcHandle = GCHandle.Alloc(data, GCHandleType.Pinned);
// 必须保持固定，直到原生处理完成，然后调用 gcHandle.Free()
```

### 步骤 6：使用 SafeHandle 处理原生句柄

原始 `IntPtr` 在异常时泄漏，并且没有双重释放保护。`SafeHandle` 是必不可少的。

```csharp
internal sealed class MyLibHandle : SafeHandleZeroOrMinusOneIsInvalid
{
    // 由封送处理基础设施实例化句柄所必需。
    // 不要删除——没有直接调用者。
    private MyLibHandle() : base(ownsHandle: true) { }

    [LibraryImport("mylib", StringMarshalling = StringMarshalling.Utf8)]
    private static partial MyLibHandle CreateHandle(string config);

    [LibraryImport("mylib")]
    private static partial int UseHandle(MyLibHandle h, ReadOnlySpan<byte> data, nuint len);

    [LibraryImport("mylib")]
    private static partial void DestroyHandle(IntPtr h);

    protected override bool ReleaseHandle() { DestroyHandle(handle); return true; }

    public static MyLibHandle Create(string config)
    {
        var h = CreateHandle(config);
        if (h.IsInvalid) throw new InvalidOperationException("Failed to create handle");
        return h;
    }

    public int Use(ReadOnlySpan<byte> data) => UseHandle(this, data, (nuint)data.Length);
}

// 使用：SafeHandle 是 IDisposable
using var handle = MyLibHandle.Create("config=value");
int result = handle.Use(myData);
```

### 步骤 7：处理错误

```csharp
// Win32 API — 检查 SetLastError
[LibraryImport("kernel32", SetLastPInvokeError = true)]
[return: MarshalAs(UnmanagedType.Bool)]
internal static partial bool CloseHandle(IntPtr hObject);

if (!CloseHandle(handle))
    throw new Win32Exception(Marshal.GetLastPInvokeError());

// HRESULT API
int hr = NativeDoWork(context);
Marshal.ThrowExceptionForHR(hr);
```

### 步骤 8：处理回调（如果需要）

**首选（.NET 8+）：`UnmanagedCallersOnly`**——避免使用委托，没有 GC 生命周期风险：

```csharp
[UnmanagedCallersOnly]
private static void LogCallback(int level, IntPtr message)
{
    string msg = Marshal.PtrToStringUTF8(message) ?? string.Empty;
    Console.WriteLine($"[{level}] {msg}");
}

[LibraryImport("mylib")]
private static unsafe partial void SetLogCallback(
    delegate* unmanaged<int, IntPtr, void> cb);

unsafe { SetLogCallback(&LogCallback); }
```

该方法必须是 `static`，不能向原生代码抛出异常，并且只能使用可空参数类型。

**后备（较旧的 TFM 或需要实例状态时）：带 rooting 的委托**

```csharp
[UnmanagedFunctionPointer(CallingConvention.Cdecl)] // 仅在 Windows x86 上需要
private delegate void LogCallbackDelegate(int level, IntPtr message);

// 关键：防止委托被垃圾回收
private static LogCallbackDelegate? s_logCallback;

public static void EnableLogging(Action<int, string> handler)
{
    s_logCallback = (level, msgPtr) =>
    {
        string msg = Marshal.PtrToStringUTF8(msgPtr) ?? string.Empty;
        handler(level, msg);
    };
    SetLogCallback(s_logCallback);
}
```

如果原生代码存储了函数指针，委托 **必须** 保持 rooting 以保持其整个生命周期。被收集的委托会导致崩溃。

**`GC.KeepAlive` 用于短生命周期回调：** 当使用 `Marshal.GetFunctionPointerForDelegate` 将委托转换为函数指针时，GC 不会跟踪指针和委托之间的关系。在原生调用完成之前使用 `GC.KeepAlive` 防止收集：

```csharp
var callback = new LogCallbackDelegate((level, msgPtr) =>
{
    string msg = Marshal.PtrToStringUTF8(msgPtr) ?? string.Empty;
    Console.WriteLine($"[{level}] {msg}");
});

IntPtr fnPtr = Marshal.GetFunctionPointerForDelegate(callback);
NativeUsesCallback(fnPtr);
GC.KeepAlive(callback); // 防止收集——fnPtr 不会 root 委托
```

---

## 跨平台库加载

对于复杂场景，使用 `NativeLibrary.SetDllImportResolver`，或对于简单情况使用条件编译。使用 `CLong`/`CULong` 用于 C `long`/`unsigned long`。注意：`CLong`/`CULong` 与 `LibraryImport` 一起使用时需要 `[assembly: DisableRuntimeMarshalling]`。

```csharp
// 简单：使用平台命名约定
// 默认命名约定在搜索 nativelibrary 时会添加相应的前缀和扩展。结果文件名将在 Windows 上为 mylib.dll，Linux 上为 libmylib.so，macOS 上为 libmylib.dylib。
private const string LibName = "mylib";

// 简单：条件编译
// WINDOWS、LINUX、MACOS 仅在针对特定 OS TFM（例如 net8.0-windows）时预定义
// 对于可移植 TFM（例如 net8.0），这些符号未定义——请使用下面的运行时解析器方法。
#if WINDOWS
    private const string LibName = "mylib.dll";
#elif LINUX
    private const string LibName = "libmylib.so";
#elif MACOS
    private const string LibName = "libmylib.dylib";
#endif

// 复杂：运行时解析器
// 当针对 netstandard2.0 或其他框架且不可用 OperatingSystem.IsXXX 时，使用 RuntimeInformation.IsOSPlatform(OSPlatform.XXX) api。
NativeLibrary.SetDllImportResolver(typeof(MyLib).Assembly,
    (name, assembly, searchPath) =>
    {
        if (name != "mylib") return IntPtr.Zero;
        string libName = OperatingSystem.IsWindows()
            ? "mylib.dll"
            : OperatingSystem.IsMacOS()
                ? "libmylib.dylib" : "libmylib.so";
        NativeLibrary.TryLoad(libName, assembly, searchPath, out var handle);
        return handle;
    });
```

---

## 将 DllImport 迁移到 LibraryImport

对于针对 .NET 7+ 的代码库，迁移可提供 AOT 兼容性和修剪安全性。

1. 在包含类中添加 `partial`，并将方法设为 `static partial`
2. 将 `[DllImport]` 替换为 `[LibraryImport]`
3. 将 `CharSet` 替换为 `StringMarshalling`
4. 将 `SetLastError = true` 替换为 `SetLastPInvokeError = true`
5. 除非针对 Windows x86，否则删除 `CallingConvention`
6. 构建并修复 `SYSLIB1054`–`SYSLIB1057` 分析器警告

启用互操作分析器：

```xml
<PropertyGroup>
    <EnableTrimAnalyzer>true</EnableTrimAnalyzer>
    <EnableAotAnalyzer>true</EnableAotAnalyzer>
</PropertyGroup>
```

---

## 工具

### CsWin32 (Win32 API)

对于 Win32 P/Invoke，优先使用 [Microsoft.Windows.CsWin32](https://github.com/microsoft/CsWin32) 而不是手动编写的签名。它从元数据中源生成正确的声明。添加一个 `NativeMethods.txt` 列出您需要的 API：

```bash
dotnet add package Microsoft.Windows.CsWin32
```

### CsWinRT (WinRT API)

对于 WinRT 互操作，使用 [Microsoft.Windows.CsWinRT](https://github.com/microsoft/CsWinRT) 从 `.winmd` 文件生成 .NET 投影。

### Objective Sharpie (Objective-C API)

对于绑定 Objective-C 库（macOS/iOS），使用 [Objective Sharpie](https://learn.microsoft.com/previous-versions/xamarin/cross-platform/macios/binding/objective-sharpie) 从 Objective-C 头文件生成初始 P/Invoke 和绑定定义。

---

## 验证

### 审查清单

- [ ] 每个签名与原生头文件完全匹配（类型、大小）
- [ ] 针对Windows x86时指定调用约定；否则省略
- [ ] 字符串编码是显式的——不依赖默认值或 `CharSet.Auto`
- [ ] 内存所有权有文档记录并匹配（谁分配，谁释放，使用什么）
- [ ] 所有原生句柄使用 `SafeHandle`（不使用从互操作层逃逸的原始 `IntPtr`）
- [ ] 作为回调传递的委托被 rooting 以防止 GC 收集
- [ ] 使用 `SetLastError`/`SetLastPInvokeError` 的 API 设置 OS 错误代码
- [ ] 结构布局与原生匹配（打包、对齐、字段顺序）
- [ ] 跨平台代码中使用 `CLong`/`CULong` 用于 C `long`/`unsigned long`
- [ ] 如果使用 `CLong`/`CULong` 与 `LibraryImport` 一起使用，则应用 `[assembly: DisableRuntimeMarshalling]`
- [ ] 没有 `bool` 而没有显式 `MarshalAs`——始终指定 `UnmanagedType.Bool`（4 字节）或 `UnmanagedType.U1`（1 字节）以确保跨语言边界的一致性。

### 可运行的验证步骤

1. **使用互操作分析器构建**——确认没有 `SYSLIB1054`–`SYSLIB1057` 警告：
   ```xml
   <EnableTrimAnalyzer>true</EnableTrimAnalyzer>
   <EnableAotAnalyzer>true</EnableAotAnalyzer>
   ```
2. **验证结构大小匹配**——对于每个跨越边界的结构，断言 `Marshal.SizeOf<T>()` 等于原生 `sizeof`
3. **往返测试**——使用已知输入调用原生函数并验证预期输出
4. **使用非 ASCII 字符串测试**——传递包含 ASCII 范围外字符的字符串以确认编码是否正确

## 参考文件

- **[references/type-mapping.md](references/type-mapping.md)** — 完整的原生到 .NET 类型映射表、结构布局模式、可空类型规则。**加载时**遇到上述步骤 2 未涵盖的类型，或处理结构布局或可空类型问题时。
- **[references/diagnostics.md](references/diagnostics.md)** — 常见陷阱、失败模式和恢复、调试方法、外部资源。**加载时**调试现有的 P/Invoke 失败或审查互操作代码以解决正确性问题。
