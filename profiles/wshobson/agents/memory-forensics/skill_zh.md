# 内存取证

获取、分析和提取内存转储文件中证据的全面技术，用于事件响应和恶意软件分析。

## 何时使用这项技能

- 在事件响应或入侵调查期间进行内存分析
- 从内存捕获中提取恶意软件证据（进程、注入代码、网络连接）
- 在Windows/Linux/macOS系统关机前获取易失性内存
- 使用Volatility 3 / Rekall对内存转储进行初步分析
- 从进程内存中恢复凭据、浏览器会话或打开的文件

## 内存获取

### 活体获取工具

#### Windows

```powershell
# WinPmem（推荐）
winpmem_mini_x64.exe memory.raw

# DumpIt
DumpIt.exe

# Belkasoft RAM Capturer
# 基于图形界面，输出原始格式

# Magnet RAM Capture
# 基于图形界面，输出原始格式
```

#### Linux

```bash
# LiME（Linux内存提取器）
sudo insmod lime.ko "path=/tmp/memory.lime format=lime"

# /dev/mem（有限制，需要权限）
sudo dd if=/dev/mem of=memory.raw bs=1M

# /proc/kcore（ELF格式）
sudo cp /proc/kcore memory.elf
```

#### macOS

```bash
# osxpmem
sudo ./osxpmem -o memory.raw

# MacQuisition（商业版）
```

### 虚拟机内存

```bash
# VMware：.vmem文件是原始内存
cp vm.vmem memory.raw

# VirtualBox：使用调试控制台
vboxmanage debugvm "VMName" dumpvmcore --filename memory.elf

# QEMU
virsh dump <domain> memory.raw --memory-only

# Hyper-V
# 检查点包含内存状态
```

## 详细部分：Volatility 3框架

最初是SKILL.md中的一个2680字节部分。已移动到`references/details.md`以适应Codex的8 KB技能主体限制。

## 分析工作流

### 恶意软件分析工作流

```bash
# 1. 初始进程调查
vol -f memory.raw windows.pstree > processes.txt
vol -f memory.raw windows.pslist > pslist.txt

# 2. 网络连接
vol -f memory.raw windows.netscan > network.txt

# 3. 检测注入
vol -f memory.raw windows.malfind > malfind.txt

# 4. 分析可疑进程
vol -f memory.raw windows.dlllist --pid <PID>
vol -f memory.raw windows.handles --pid <PID>

# 5. 转储可疑可执行文件
vol -f memory.raw windows.pslist --pid <PID> --dump

# 6. 从转储中提取字符串
strings -a pid.<PID>.exe > strings.txt

# 7. YARA扫描
vol -f memory.raw windows.yarascan --yara-rules malware.yar
```

### 事件响应工作流

```bash
# 1. 事件时间线
vol -f memory.raw windows.timeliner > timeline.csv

# 2. 用户活动
vol -f memory.raw windows.cmdline
vol -f memory.raw windows.consoles

# 3. 持久化机制
vol -f memory.raw windows.registry.printkey \
    --key "Software\Microsoft\Windows\CurrentVersion\Run"

# 4. 服务
vol -f memory.raw windows.svcscan

# 5. 定时任务
vol -f memory.raw windows.scheduled_tasks

# 6. 最近文件
vol -f memory.raw windows.filescan | grep -i "recent"
```

## 数据结构

### Windows进程结构

```c
// EPROCESS（执行进程）
typedef struct _EPROCESS {
    KPROCESS Pcb;                    // 内核进程块
    EX_PUSH_LOCK ProcessLock;
    LARGE_INTEGER CreateTime;
    LARGE_INTEGER ExitTime;
    // ...
    LIST_ENTRY ActiveProcessLinks;   // 双向链表
    ULONG_PTR UniqueProcessId;       // PID
    // ...
    PEB* Peb;                        // 进程环境块
    // ...
} EPROCESS;

// PEB（进程环境块）
typedef struct _PEB {
    BOOLEAN InheritedAddressSpace;
    BOOLEAN ReadImageFileExecOptions;
    BOOLEAN BeingDebugged;           // 反调试检查
    // ...
    PVOID ImageBaseAddress;          // 可执行文件基址
    PPEB_LDR_DATA Ldr;              // 加载器数据（DLL列表）
    PRTL_USER_PROCESS_PARAMETERS ProcessParameters;
    // ...
} PEB;
```

### VAD（虚拟地址描述符）

```c
typedef struct _MMVAD {
    MMVAD_SHORT Core;
    union {
        ULONG LongFlags;
        MMVAD_FLAGS VadFlags;
    } u;
    // ...
    PVOID FirstPrototypePte;
    PVOID LastContiguousPte;
    // ...
    PFILE_OBJECT FileObject;
} MMVAD;

// 内存保护标志
#define PAGE_EXECUTE           0x10
#define PAGE_EXECUTE_READ      0x20
#define PAGE_EXECUTE_READWRITE 0x40
#define PAGE_EXECUTE_WRITECOPY 0x80
```

## 检测模式

### 进程注入指标

```python
# Malfind指标
# - PAGE_EXECUTE_READWRITE保护（可疑）
# - MZ头在非图像VAD区域
# - 分配起始处的shellcode模式

# 常见的注入技术
# 1. 经典DLL注入
#    - VirtualAllocEx + WriteProcessMemory + CreateRemoteThread

# 2. 进程空洞化
#    - CreateProcess（挂起） + NtUnmapViewOfSection + WriteProcessMemory

# 3. APC注入
#    - 针对可唤醒线程的QueueUserAPC

# 4. 线程执行劫持
#    - SuspendThread + SetThreadContext + ResumeThread
```

### 根目录检测

```bash
# 比较进程列表
vol -f memory.raw windows.pslist > pslist.txt
vol -f memory.raw windows.psscan > psscan.txt
diff pslist.txt psscan.txt  # 隐藏进程

# 检查DKOM（直接内核对象操作）
vol -f memory.raw windows.callbacks

# 检测钩子函数
vol -f memory.raw windows.ssdt  # 系统服务描述表

# 驱动分析
vol -f memory.raw windows.driverscan
vol -f memory.raw windows.driverirp
```

### 凭据提取

```bash
# 转储哈希（需要先使用hivelist）
vol -f memory.raw windows.hashdump

# LSA密钥
vol -f memory.raw windows.lsadump

# 缓存的域凭据
vol -f memory.raw windows.cachedump

# Mimikatz风格提取
# 需要特定插件/工具
```

## YARA集成

### 编写内存YARA规则

```yara
rule Suspicious_Injection
{
    meta:
        description = "检测常见注入shellcode"

    strings:
        // 常见shellcode模式
        $mz = { 4D 5A }
        $shellcode1 = { 55 8B EC 83 EC }  // 函数前缀
        $api_hash = { 68 ?? ?? ?? ?? 68 ?? ?? ?? ?? E8 }  // Push哈希，调用

    condition:
        $mz at 0 or any of ($shellcode*)
}

rule Cobalt_Strike_Beacon
{
    meta:
        description = "检测内存中的Cobalt Strike信标"

    strings:
        $config = { 00 01 00 01 00 02 }
        $sleep = "sleeptime"
        $beacon = "%s (admin)" wide

    condition:
        2 of them
}
```

### 扫描内存

```bash
# 扫描所有进程内存
vol -f memory.raw windows.yarascan --yara-rules rules.yar

# 扫描特定进程
vol -f memory.raw windows.yarascan --yara-rules rules.yar --pid 1234

# 扫描内核内存
vol -f memory.raw windows.yarascan --yara-rules rules.yar --kernel
```

## 字符串分析

### 提取字符串

```bash
# 基本字符串提取
strings -a memory.raw > all_strings.txt

# Unicode字符串
strings -el memory.raw >> all_strings.txt

# 从进程转储中针对性提取
vol -f memory.raw windows.memmap --pid 1234 --dump
strings -a pid.1234.dmp > process_strings.txt

# 模式匹配
grep -E "(https?://|[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3})" all_strings.txt
```

### 开源软件用于混淆字符串

```bash
# FLOSS提取混淆字符串
floss malware.exe > floss_output.txt

# 从内存转储
floss pid.1234.dmp
```

## 最佳实践

### 获取最佳实践

1. **最小化占用空间**：使用轻量级获取工具
2. **记录所有内容**：记录时间、工具和捕获的哈希值
3. **验证完整性**：捕获内存转储后立即进行哈希校验
4. **维护证据链**：保持正确的取证处理

### 分析最佳实践

1. **从宏观入手**：在深入分析前获取整体概览
2. **交叉参考**：对相同数据进行多次插件分析
3. **时间线关联**：将内存发现与磁盘/网络关联
4. **记录发现**：保持详细笔记和截图
5. **验证结果**：通过多种方法验证发现

### 常见陷阱

- **过时数据**：内存是易失的，需及时分析
- **不完整转储**：验证转储大小是否与预期RAM匹配
- **符号问题**：确保为操作系统版本提供正确的符号文件
- **涂抹**：在获取过程中内存可能发生变化
- **加密**：某些数据可能以加密形式存在于内存中
