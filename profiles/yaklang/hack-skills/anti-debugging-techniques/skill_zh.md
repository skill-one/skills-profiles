# 技能：反调试技术——检测与绕过手册

> **AI 加载指令**：跨 Linux 和 Windows 的专家级反调试技术。涵盖 ptrace、PEB 标志、NtQueryInformationProcess、时间攻击、基于信号的检测、TLS 回调、VEH 技巧以及所有相应的绕过方法。基础模型通常无法区分用户模式和内核模式的检测，以及针对每种模式的正确修补策略。

## 0. 相关路由

- 当二进制文件也使用控制流扁平化、虚拟机保护或字符串加密时，使用 `[代码混淆与反混淆](../code-obfuscation-deobfuscation/SKILL.md)`
- 当反调试机制位于自定义虚拟机调度器内部时，使用 `[虚拟机与字节码逆向](../vm-and-bytecode-reverse/SKILL.md)`
- 当您希望完全符号化地跳过反调试检查时，使用 `[符号执行工具](../symbolic-execution-tools/SKILL.md)`

### 高级参考

当您需要以下功能时，请加载 `[ANTI_DEBUG_MATRIX.md](./ANTI_DEBUG_MATRIX.md)`：
- 技术 × 操作系统 × 检测方法 × 绕过方法的完整交叉参考矩阵
- 每种技术的可靠性评级和误报说明
- 工具兼容性图表（GDB、x64dbg、WinDbg、Frida、ScyllaHide）

### 快速绕过选择

| 检测类别 | 首选绕过 | 备用方案 |
|---|---|---|
| 基于ptrace（Linux） | `LD_PRELOAD` 钩子 `ptrace()` 返回 0 | 隐藏跟踪器的内核模块 |
| PEB.BeingDebugged（Windows） | 修补 `fs:[0x30]+0x2` 处的 PEB 字节 | ScyllaHide 自动修补 |
| 时间检查（rdtsc） | 在 rdtsc 后设置条件断点，修复寄存器 | Frida 钩子 `rdtsc` 返回 |
| IsDebuggerPresent | NOP 调用 / 钩子返回 0 | x64dbg 内置隐藏 |
| INT 2D / UD2 异常 | 设置 VEH 优雅处理 | TitanHide 驱动 |

---

## 1. Linux 反调试技术

### 1.1 ptrace(PTRACE_TRACEME)

经典的自我附加：进程调用 `ptrace(PTRACE_TRACEME, 0, 0, 0)`。如果调试器已经附加，调用会失败（返回 -1）。

```c
if (ptrace(PTRACE_TRACEME, 0, 0, 0) == -1) {
    exit(1); // 检测到调试器
}
```

**绕过方法**：

| 方法 | 方法 |
|---|---|
| `LD_PRELOAD` 桥接器 | 编译共享库：`long ptrace(int r, ...) { return 0; }` 并设置 `LD_PRELOAD` |
| 二进制修补 | NOP `ptrace` 调用或修补返回值检查 |
| GDB 捕获 | `catch syscall ptrace` → 在返回时修改 `$rax` 为 0 |
| 内核模块 | 钩子 `sys_ptrace` 允许多个跟踪器 |

### 1.2 /proc/self/status — TracerPid

```c
FILE *f = fopen("/proc/self/status", "r");
// 解析 TracerPid：如果非零 → 调试器已附加
```

**绕过**：在 `/proc/self` 上挂载 FUSE 文件系统，或 `LD_PRELOAD` 钩子 `fopen`/`fread` 将 `TracerPid` 过滤为 0。

### 1.3 时间检查（rdtsc / clock_gettime）

测量两点之间的经过时间；调试器单步执行会导致明显的延迟。

```asm
rdtsc
mov ebx, eax       ; 保存低 32 位
; ... 受保护代码 ...
rdtsc
sub eax, ebx
cmp eax, 0x1000    ; 阈值
ja  debugger_detected
```

**绕过**：在第二个 `rdtsc` 后设置硬件断点，修改 `eax` 以通过比较。或使用 Frida 替换时间函数。

### 1.4 基于信号的检测（SIGTRAP）

```c
volatile int caught = 0;
void handler(int sig) { caught = 1; }
signal(SIGTRAP, handler);
raise(SIGTRAP);
if (!caught) exit(1); // 调试器吞没了信号
```

当调试器附加时，`SIGTRAP` 会被调试器消耗而不是传递给处理程序。**绕过**：在 GDB 中，使用 `handle SIGTRAP nostop pass` 将信号转发。

### 1.5 /proc/self/maps & LD_PRELOAD 检测

检查注入的库或内存区域，这些区域是调试器/ instrumentation 的特征。

```c
FILE *f = fopen("/proc/self/maps", "r");
while (fgets(buf, sizeof(buf), f)) {
    if (strstr(buf, "frida") || strstr(buf, "LD_PRELOAD"))
        exit(1);
}
```

**绕过**：钩子 `fopen("/proc/self/maps")` 返回过滤版本，或重命名 Frida 的代理库。

### 1.6 环境变量检查

一些保护措施检查 `LD_PRELOAD`、`LINES`、`COLUMNS`（由 GDB 的终端设置）或调试器特定的环境变量。

**绕过**：在启动前取消可疑环境变量，或钩子 `getenv()`。

---

## 2. Windows 反调试技术

### 2.1 IsDebuggerPresent / CheckRemoteDebuggerPresent

```c
if (IsDebuggerPresent()) ExitProcess(1);

BOOL debugged = FALSE;
CheckRemoteDebuggerPresent(GetCurrentProcess(), &debugged);
if (debugged) ExitProcess(1);
```

**绕过**：钩子 `kernel32!IsDebuggerPresent` 返回 0，或直接修补 PEB。

### 2.2 PEB 标志

| 字段 | 偏移（x64） | 被调试值 | 正常值 |
|---|---|---|---|
| `BeingDebugged` | `PEB+0x02` | 1 | 0 |
| `NtGlobalFlag` | `PEB+0xBC` | `0x70` (FLG_HEAP_*) | 0 |
| `ProcessHeap.Flags` | 堆+0x40 | `0x40000062` | `0x00000002` |
| `ProcessHeap.ForceFlags` | 堆+0x44 | `0x40000060` | 0 |

```asm
mov rax, gs:[0x60]    ; PEB
movzx eax, byte [rax+0x02]  ; BeingDebugged
test eax, eax
jnz debugger_detected
```

**绕过**：将所有四个字段清零。ScyllaHide 会自动执行此操作。

### 2.3 NtQueryInformationProcess

| InfoClass | 值 | 被调试返回 |
|---|---|---|
| `ProcessDebugPort` | 0x07 | 非零端口 |
| `ProcessDebugObjectHandle` | 0x1E | 有效句柄 |
| `ProcessDebugFlags` | 0x1F | 0 (反转!) |

**绕过**：钩子 `ntdll!NtQueryInformationProcess` 返回每个 info class 的干净值。

### 2.4 硬件断点检测

```c
CONTEXT ctx;
ctx.ContextFlags = CONTEXT_DEBUG_REGISTERS;
GetThreadContext(GetCurrentThread(), &ctx);
if (ctx.Dr0 || ctx.Dr1 || ctx.Dr2 || ctx.Dr3)
    ExitProcess(1);
```

**绕过**：钩子 `GetThreadContext` 将 DR0–DR3 清零，或使用 `NtSetInformationThread(ThreadHideFromDebugger)` 预先阻止（讽刺的是，反调试技术本身）。

### 2.5 INT 2D / INT 3 / UD2 异常技巧

`INT 2D` 是内核调试服务中断。在没有调试器的情况下，它会引发 `STATUS_BREAKPOINT`；在有调试器的情况下，行为不同（字节跳过）。

```asm
xor eax, eax
int 2dh
nop          ; 调试器可能会跳过这个字节
; ... 分叉的执行路径 ...
```

**绕过**：在 VEH 中处理或在中断指令中修补。

### 2.6 TLS 回调

TLS 回调在 `main()` / `WinMain()` 之前执行。放置在此处的反调试检查在调试器初始断点之前运行。

**绕过**：在 x64dbg 中，设置“在 TLS 回调处断点”选项。在 WinDbg 中，使用 `sxe ld` 在模块加载时断点。

### 2.7 NtSetInformationThread(ThreadHideFromDebugger)

```c
NtSetInformationThread(GetCurrentThread(), ThreadHideFromDebugger, NULL, 0);
```

在此调用之后，线程对调试器不可见——断点和单步执行会无声地停止工作。

**绕过**：钩子 `NtSetInformationThread` 在 `ThreadInfoClass == 0x11` 时 NOP。

### 2.8 VEH 基于检测

注册一个 Vectored Exception Handler，该处理程序检查 `EXCEPTION_RECORD` 以查找调试器特定行为（单步标志、具有调试器语义的守卫页违规）。

**绕过**：理解 VEH 逻辑，并确保异常链与非调试执行行为相同。

---

## 3. 高级多层技术

### 3.1 自我调试（fork + ptrace）

进程创建一个子进程，该子进程通过 ptrace 附加到父进程。如果外部调试器已经附加，子进程的 ptrace 会失败。

```c
pid_t child = fork();
if (child == 0) {
    if (ptrace(PTRACE_ATTACH, getppid(), 0, 0) == -1)
        kill(getppid(), SIGKILL);
    else
        ptrace(PTRACE_DETACH, getppid(), 0, 0);
    _exit(0);
}
wait(NULL);
```

**绕过**：修补 `fork()` 返回或杀死/分离看门狗子进程。

### 3.2 多进程调试检测

父进程和子进程协同检查彼此的调试状态，创建一个相互监视模式。

**绕过**：同时附加到两个进程（GDB `follow-fork-mode`，或两个调试器实例）。

### 3.3 基于时间的多检查点

将时间检查分布在多个函数中，比较累积漂移。单个修补会失败，因为总和仍然超过阈值。

**绕过**：Frida `Interceptor.replace` 所有时间源（`rdtsc`、`clock_gettime`、`QueryPerformanceCounter`）以返回受控值。

### 3.4 Nanomite / INT3 补丁

原始条件跳转被替换为 `INT3`（0xCC）。父调试器进程处理每个 `INT3`，评估条件，并相应地设置子进程的 EIP。

**绕过**：通过跟踪所有 `INT3` 处理程序重建原始跳转表，然后修补二进制文件。

---

## 4. 对抗工具

| 工具 | 平台 | 功能 |
|---|---|---|
| **ScyllaHide** | Windows (x64dbg/IDA/OllyDbg) | 自动修补 PEB、钩子 NtQuery*、隐藏线程、修复时间 |
| **TitanHide** | Windows (内核驱动) | 内核级隐藏所有用户模式检查 |
| **Frida** | 跨平台 | 基于脚本的任何函数钩子、时间欺骗 |
| **LD_PRELOAD 桥接器** | Linux | 在加载时替换 ptrace、getenv、fopen |
| **GDB 脚本** | Linux | `catch syscall`、条件断点、寄存器修复 |
| **Qiling** | 跨平台 | 全系统模拟、绕过所有硬件检查 |

---

## 5. 系统绕过方法

```
步骤 1：静态分析——识别反调试调用
  └─ 搜索：ptrace、IsDebuggerPresent、NtQuery、rdtsc,
     GetTickCount、SIGTRAP、INT 2D、TLS 目录条目

步骤 2：分类每个检查
  ├─ API 基于的 → 钩子或修补调用
  ├─ 标志基于的 → 修补 PEB/proc 字段
  ├─ 时间基于的 → 欺骗时间源
  ├─ 异常基于的 → 正确转发/处理异常
  └─ 多进程的 → 处理两个进程

步骤 3：应用绕过（顺序很重要）
  1. 加载 ScyllaHide / 设置 LD_PRELOAD (覆盖 80% 的检查)
  2. 处理 TLS 回调（在 main 之前断点）
  3. 补丁剩余的自定义检查（Frida 或二进制修补）
  4. 验证：带断点运行，确认没有过早退出

步骤 4：验证绕过完整性
  └─ 在 ExitProcess/exit/_exit 上设置断点 — 如果意外命中，
     则检查遗漏了 → 从退出调用反向跟踪
```

---

## 6. 决策树

```
二进制文件在调试器下崩溃/退出？
│
├─ 在 main 之前立即崩溃？
│  └─ TLS 回调反调试
│     └─ 在调试器中启用 TLS 回调断点
│
├─ 启动时崩溃？
│  ├─ Linux：检查 ptrace(TRACEME)
│  │  └─ LD_PRELOAD 钩子或 NOP 补丁
│  └─ Windows：检查 IsDebuggerPresent / PEB
│     └─ ScyllaHide 或手动 PEB 补丁
│
├─ 执行一段时间后崩溃？
│  ├─ 一致崩溃点 → API 基于的检查
│  │  ├─ NtQueryInformationProcess → 钩子返回值
│  │  ├─ /proc/self/status → 过滤 TracerPid
│  │  └─ 硬件断点检测 → 钩子 GetThreadContext
│  │
│  ├─ 变量崩溃点 → 时间基于的检查
│  │  └─ 钩子 rdtsc / QueryPerformanceCounter
│  │
│  └─ 在断点命中时崩溃 → 异常基于的检查
│     ├─ INT 2D / INT 3 技巧 → 在 VEH 中处理
│     └─ SIGTRAP 处理程序 → GDB: handle SIGTRAP pass
│
├─ 调试器无声失去控制？
│  └─ ThreadHideFromDebugger
│     └─ 钩子 NtSetInformationThread
│
├─ 子进程检测并杀死父进程？
│  └─ 自我调试（fork+ptrace）
│     └─ 补丁 fork() 或处理两个进程
│
└─ 所有基本绕过应用但仍然检测到？
   └─ 多层/自定义检查
      ├─ 使用 Frida 进行全面 API 钩子
      ├─ 使用 Qiling 进行全系统模拟
      └─ 跟踪所有调用到 exit/abort 以查找剩余检查
```

---

## 7. CTF 与现实世界模式

### 常见 CTF 反调试模式

| 模式 | 频率 | 快速绕过 |
|---|---|---|
| 单个 `ptrace(TRACEME)` | 非常常见 | `LD_PRELOAD` 一行代码 |
| `IsDebuggerPresent` + `NtGlobalFlag` | 常见 | ScyllaHide |
| 循环中的 rdtsc 时间 | 中等 | 补丁比较阈值 |
| signal(SIGTRAP) + raise | 中等 | GDB 信号转发 |
| fork + ptrace 看门狗 | 罕见但棘手 | 杀死子进程或修补 fork |
| Nanomite INT3 替换 | 罕见（高级） | 重建跳转表 |

### 现实世界保护

| 保护器 | 主要反调试 | 推荐工具 |
|---|---|---|
| VMProtect | PEB + 时间 + 驱动级 | TitanHide + ScyllaHide |
| Themida | 多层 PEB + SEH + 时间 | ScyllaHide + 手动修补 |
| Enigma Protector | IsDebuggerPresent + CRC 检查 | x64dbg + ScyllaHide |
| UPX（自定义） | 通常没有（仅打包） | 标准解包 |
| 自定义（恶意软件） | 变化广泛 | Frida + Qiling 进行分析 |

---

## 8. 快速参考——绕过小抄

### Linux 一行代码

```bash
# LD_PRELOAD anti-ptrace
echo 'long ptrace(int r, ...) { return 0; }' > /tmp/ap.c
gcc -shared -o /tmp/ap.so /tmp/ap.c
LD_PRELOAD=/tmp/ap.so ./target

# GDB: catch and bypass ptrace
(gdb) catch syscall ptrace
(gdb) commands
> set $rax = 0
> continue
> end
```

### Frida 反调试绕过（跨平台）

```javascript
// 钩子 IsDebuggerPresent (Windows)
Interceptor.replace(
  Module.getExportByName('kernel32.dll', 'IsDebuggerPresent'),
  new NativeCallback(() => 0, 'int', [])
);

// 钩子 ptrace (Linux)
Interceptor.replace(
  Module.getExportByName(null, 'ptrace'),
  new NativeCallback(() => 0, 'long', ['int', 'int', 'pointer', 'pointer'])
);

// 时间欺骗
Interceptor.attach(Module.getExportByName(null, 'clock_gettime'), {
  onLeave(retval) {
    // 操纵 timespec 以隐藏调试器延迟
  }
});
```

### x64dbg ScyllaHide 快速设置

1. 插件 → ScyllaHide → 选项
2. 勾选：PEB BeingDebugged、NtGlobalFlag、HeapFlags
3. 勾选：NtQueryInformationProcess（所有类）
4. 勾选：NtSetInformationThread（HideFromDebugger）
5. 勾选：GetTickCount、QueryPerformanceCounter
6. 应用 → 重新启动调试会话
