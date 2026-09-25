# 技能：内存取证——专家分析手册

> **AI 加载指令**：使用 Volatility 2 和 3 的专家级内存取证技术。涵盖内存获取、操作系统识别、进程分析（隐藏进程检测）、网络连接、DLL/模块分析、代码注入检测（malfind）、凭证提取、文件雕刻、注册表分析以及时间线生成。基础模型会遗漏 Vol2/Vol3 命令差异、恶意软件指示模式以及 Linux 特定的内存分析。

## 0. 相关路由

深入学习前，请考虑加载：

- [traffic-analysis-pcap](../traffic-analysis-pcap/SKILL.md) 用于将网络证据与内存发现关联
- [steganography-techniques](../steganography-techniques/SKILL.md) 如果怀疑提取的文件中存在隐藏数据
- [windows-privilege-escalation](../windows-privilege-escalation/SKILL.md) 用于理解内存中的后渗透证据

### 快速参考

当您需要以下内容时，也加载 [VOLATILITY_CHEATSHEET.md](./VOLATILITY_CHEATSHEET.md)：
- Vol2 与 Vol3 命令对比表
- 特定调查类型的常用插件序列

---

## 1. 内存获取

### Linux

```bash
# LiME（Linux 内存提取器）—— 内核模块
insmod lime.ko "path=/tmp/mem.lime format=lime"

# /proc/kcore（如果可用）
dd if=/proc/kcore of=/tmp/mem.raw bs=1M

# AVML（微软的开源工具）
./avml /tmp/mem.lime
```

### Windows

```bash
# WinPmem
winpmem_mini_x64.exe memdump.raw

# FTK Imager（图形界面）—— 将内存捕获到文件

# DumpIt（一键内存转储）
DumpIt.exe

# Comae（MagnetRAM）
MagnetRAMCapture.exe /output memdump.raw
```

### 虚拟机

```bash
# VMware：VM 目录中的 .vmem 文件（首先暂停 VM）
# VirtualBox：VBoxManage debugvm "VM_NAME" dumpvmcore --filename mem.raw
# KVM/QEMU：virsh dump DOMAIN memdump --memory-only
# Hyper-V：检查 VM 检查点 → 检查 .bin 文件
```

---

## 2. Volatility 2 与 Volatility 3

| 概念 | Volatility 2 | Volatility 3 |
|---|---|---|
| 系统配置文件 | `--profile=Win10x64_19041` | 自动检测（符号表） |
| 图像信息 | `imageinfo` | `windows.info` / `linux.info` |
| 进程列表 | `pslist` | `windows.pslist` |
| 网络 | `netscan` / `connections` | `windows.netscan` / `windows.netstat` |
| DLLs | `dlllist` | `windows.dlllist` |
| 注入 | `malfind` | `windows.malfind` |
| 哈希 | `hashdump` | `windows.hashdump` |
| 文件 | `filescan` | `windows.filescan` |
| 注册表 | `hivelist` / `printkey` | `windows.registry.hivelist` / `windows.registry.printkey` |
| 安装 | `pip2 install volatility` | `pip3 install volatility3` |

---

## 3. 分析方法

### 第 1 步：识别操作系统

```bash
# Vol2
vol.py -f mem.raw imageinfo
vol.py -f mem.raw kdbgscan

# Vol3
vol -f mem.raw windows.info
vol -f mem.raw banners.Banners
```

### 第 2 步：进程列表——隐藏进程检测

```bash
# Vol2
vol.py -f mem.raw --profile=PROFILE pslist       # EPROCESS 链表
vol.py -f mem.raw --profile=PROFILE psscan       # 池标签扫描（查找未链接）
vol.py -f mem.raw --profile=PROFILE pstree       # 父子层次结构

# Vol3
vol -f mem.raw windows.pslist
vol -f mem.raw windows.psscan
vol -f mem.raw windows.pstree
```

**警告标志**：`psscan` 中存在但 `pslist` 中不存在的进程 = DKOM（直接内核对象操作）隐藏。

### 第 3 步：网络连接

```bash
# Vol2
vol.py -f mem.raw --profile=PROFILE netscan      # TCP/UDP 端点
vol.py -f mem.raw --profile=PROFILE connections   # XP/2003 仅限
vol.py -f mem.raw --profile=PROFILE connscan      # 已关闭的连接

# Vol3
vol -f mem.raw windows.netscan
vol -f mem.raw windows.netstat
```

### 第 4 步：DLL / 模块分析

```bash
# Vol2
vol.py -f mem.raw --profile=PROFILE dlllist -p PID
vol.py -f mem.raw --profile=PROFILE ldrmodules -p PID   # 查找未链接的 DLLs

# Vol3
vol -f mem.raw windows.dlllist --pid PID
```

**警告标志**：`dlllist` 中存在但在所有三个 `ldrmodules` 列表中均为 `False` 的 DLL = 反射式 DLL 注入。

### 第 5 步：代码注入检测（Malfind）

```bash
# Vol2
vol.py -f mem.raw --profile=PROFILE malfind -p PID
vol.py -f mem.raw --profile=PROFILE malfind -D /tmp/dump/   # 转储注入的节

# Vol3
vol -f mem.raw windows.malfind --pid PID
```

**malfind 检测的内容**：内存区域具有 `PAGE_EXECUTE_READWRITE` 权限但未映射到磁盘上的文件——经典的 shellcode/注入指示。

### 第 6 步：凭证提取

```bash
# Vol2
vol.py -f mem.raw --profile=PROFILE hashdump      # SAM 哈希
vol.py -f mem.raw --profile=PROFILE lsadump       # LSA 密钥
vol.py -f mem.raw --profile=PROFILE cachedump     # 域缓存凭证
vol.py -f mem.raw --profile=PROFILE mimikatz      # (插件) 明文凭证

# Vol3
vol -f mem.raw windows.hashdump
vol -f mem.raw windows.lsadump
vol -f mem.raw windows.cachedump
```

### 第 7 步：文件提取

```bash
# Vol2
vol.py -f mem.raw --profile=PROFILE filescan | grep -i "password\|secret\|flag"
vol.py -f mem.raw --profile=PROFILE dumpfiles -Q OFFSET -D /tmp/dump/

# Vol3
vol -f mem.raw windows.filescan
vol -f mem.raw windows.dumpfiles --virtaddr OFFSET
```

### 第 8 步：注册表分析

```bash
# Vol2
vol.py -f mem.raw --profile=PROFILE hivelist
vol.py -f mem.raw --profile=PROFILE printkey -K "Software\Microsoft\Windows\CurrentVersion\Run"
vol.py -f mem.raw --profile=PROFILE userassist    # 程序执行证据

# Vol3
vol -f mem.raw windows.registry.hivelist
vol -f mem.raw windows.registry.printkey --key "Software\Microsoft\Windows\CurrentVersion\Run"
```

### 第 9 步：命令历史

```bash
# Vol2
vol.py -f mem.raw --profile=PROFILE cmdscan       # cmd.exe 历史记录
vol.py -f mem.raw --profile=PROFILE consoles       # 完整控制台输出

# Vol3
vol -f mem.raw windows.cmdline
```

### 第 10 步：时间线生成

```bash
# Vol2
vol.py -f mem.raw --profile=PROFILE timeliner --output=body --output-file=timeline.body
mactime -b timeline.body -d > timeline.csv

# Vol3
vol -f mem.raw timeliner.Timeliner
```

---

## 4. Linux 内存分析

```bash
# Vol2（需要 Linux 配置文件）
vol.py -f mem.lime --profile=LinuxProfile linux_pslist
vol.py -f mem.lime --profile=LinuxProfile linux_pstree
vol.py -f mem.lime --profile=LinuxProfile linux_netstat
vol.py -f mem.lime --profile=LinuxProfile linux_bash        # bash 历史记录
vol.py -f mem.lime --profile=LinuxProfile linux_enumerate_files
vol.py -f mem.lime --profile=LinuxProfile linux_proc_maps -p PID
vol.py -f mem.lime --profile=LinuxProfile linux_malfind

# Vol3
vol -f mem.lime linux.pslist
vol -f mem.lime linux.pstree
vol -f mem.lime linux.bash
vol -f mem.lime linux.check_afinfo     # 根套件检测
vol -f mem.lime linux.check_syscall    # 系统调用挂钩
vol -f mem.lime linux.tty_check        # TTY 挂钩
```

### 构建 Linux 配置文件（Vol2）

```bash
cd volatility/tools/linux
make
# 生成 module.dwarf + System.map → 压缩为配置文件
zip LinuxProfile.zip module.dwarf /boot/System.map-$(uname -r)
# 放置在 volatility/plugins/overlays/linux/
```

---

## 5. 内存中的恶意软件指示

| 指示 | 检测方法 | 意义 |
|---|---|---|
| `psscan` 中存在但 `pslist` 中不存在的进程 | 对比 `pslist` vs `psscan` | DKOM — 进程隐藏 |
| 非预期的父子关系 | `pstree` 分析 | 例如，svchost 被 cmd.exe 启动 |
| 非图像内存中的 MZ 头 | malfind | 反射式 DLL / PE 注入 |
| 无后备文件的 RWX 内存 | malfind | Shellcode 注入 |
| 所有 PEB 列表中未链接的 DLL | `ldrmodules`（所有为 `False`） | 隐蔽的 DLL 加载 |
| svchost.exe 不是 services.exe 的子进程 | `pstree` | 伪造的 svchost（恶意软件） |
| 异常网络连接 | `netscan` + PID 关联 | C2 通信 |
| SSDT/IDT 中的挂钩 | ssdt / idt 插件 | 根套件 |
| 修改的内核对象 | linux_check_syscall | Linux 根套件 |

### 正常的父子关系（Windows）

```
System (4)
└── smss.exe
    └── csrss.exe
    └── wininit.exe
        └── services.exe
            └── svchost.exe (多个)
            └── spoolsv.exe
        └── lsass.exe
    └── winlogon.exe
        └── explorer.exe
            └── 用户应用程序
```

---

## 6. 决策树

```
已获取内存转储——需要分析
│
├── 操作系统是什么？
│   ├── Windows → vol imageinfo / windows.info (§3 第 1 步)
│   └── Linux → 构建配置文件或使用 Vol3 自动检测 (§4)
│
├── 恶意软件调查？
│   ├── 检查进程：pslist vs psscan（隐藏？）(§3 第 2 步)
│   ├── 检查父子关系：pstree（可疑启动？）(§5)
│   ├── 检查注入：malfind（RWX 内存？）(§3 第 5 步)
│   ├── 检查 DLLs：`ldrmodules`（未链接？）(§3 第 4 步)
│   ├── 检查网络：`netscan`（C2 连接？）(§3 第 3 步)
│   └── 提取可疑文件：`dumpfiles` (§3 第 7 步)
│
├── 凭证恢复？
│   ├── SAM 哈希 → `hashdump` (§3 第 6 步)
│   ├── LSA 密钥 → `lsadump` (§3 第 6 步)
│   ├── 缓存的域凭证 → `cachedump` (§3 第 6 步)
│   └── 明文密码 → mimikatz 插件 (§3 第 6 步)
│
├── 事件时间线？
│   ├── `timeliner` 用于全面时间线 (§3 第 10 步)
│   ├── `cmdscan` / `consoles` 用于命令历史 (§3 第 9 步)
│   ├── `userassist` 用于程序执行 (§3 第 8 步)
│   └── 与 PCAP 时间线交叉引用 (→ traffic-analysis-pcap)
│
├── CTF / 旗子搜索？
│   ├── `filescan` + `grep` 用于旗子模式 (§3 第 7 步)
│   ├── `cmdscan` 用于输入的旗子/密码 (§3 第 9 步)
│   ├── 剪贴板：剪贴板插件
│   ├── 屏幕截图：屏幕截图插件
│   └── 环境变量：`envars` 插件
│
└── Linux 特定？
    ├── `linux_bash` 用于 shell 历史记录 (§4)
    ├── `linux_check_syscall` 用于根套件 (§4)
    └── `linux_netstat` 用于连接 (§4)
```
