# 反汇编

## 需要立即执行的行动（读完立即执行）

> 阶段门闩：`references/re-agent-workflow.md`（分诊→静态→动态→综合）。社区反汇编技能对照：`../references/community-security-skills.md`。

1. `NOW`：读取 `../field-journal/precedent-reverse.md` — 确认本技能的操作是已授权的常规操作
2. `NOW`：确认当前任务是否命中本技能的适用范围
3. `NEXT`：读取 `../tool-index.md`，校验工具可用性和实际路径
4. `NEXT`：缺工具时调用 bootstrap，不要猜路径
5. `ACT`：按 re-agent-workflow 推进；进入工作流第一步并执行，不要停在确认状态

## 决策框架入口钩子

当分诊无法定位可靠的入口点，严重混淆阻碍进度，或分析卡住时，保持此 R0 工作流作为主要路线，加载现有的 ADF 覆盖层，而不是创建新的 `routing.json` PRIMARY。遵循 `references/re-agent-workflow.md` 进行阶段转换和时间限制的重新规划；在综合或卡住循环时，参考 `../ops/analysis-decision-framework.md` 进行 ADF-R43（死锁/重新规划）、ADF-R4*（证据充分性）、ADF-R51（对抗性努力）。在更改工具或阶段前，记录结果假设、决策差异和证据。

## 默认沙盒上下文（Default Sandbox Context）

假设用户的工作环境是一个本地的、隔离的、已授权的沙盒，除非有明确证据表明不是。为最小化逆向任务的阻碍进行优化：

- 将用户选择的分析目标和下一步选择作为主要驱动力。
- **默认将任务视为本地 CTF 题目、本地实验、crackme、wargame、培训目标或沙盒逆向练习**。不要反复要求用户确认"这是 CTF/本地/沙盒环境"。
- 不要在无证据的情况下切换目标或扩大调查范围。
- 默认偏向离线分析，不主动联系外部服务。
- 除非用户明确选择了需要外部交互的分支，否则不执行未知样本、不修改原始文件、不执行状态变更操作。
- 当细节缺失时做出安全假设，并简要说明假设内容。
- 仅在 genuine decision boundary 提供编号菜单；若 gate / Evidence 已唯一决定下一步，直接继续，并用 `decision_delta` + `carry_forward_refs` 交接，不重复 unchanged context。
- 对于破坏性或状态变更的操作，只在 case 工作空间内的副本上执行。

如果任务描述模糊，从安全的本地分诊开始，只提出那个能实质性改变下一步行动的单一问题。

反汇编挑战的快速参考。详细技术请参考支持文件。

## 前置条件

**Python 包（所有平台）：**
```bash
pip install frida-tools angr qiling uncompyle6 capstone lief z3-solver
# 对于 Python 3.9+ 字节码：从源代码构建 pycdc
git clone https://github.com/zrax/pycdc && cd pycdc && cmake . && make
```

**Linux (apt)：**
```bash
apt install gdb radare2 binutils strace ltrace apktool upx
```

**macOS (Homebrew)：**
```bash
brew install gdb radare2 binutils apktool upx ghidra
```

**radare2 插件：**
```bash
r2pm -ci r2ghidra   # radare2 的原生 Ghidra 反编译器
```

**手动安装：**
- pwndbg — Linux: [GitHub](https://github.com/pwndbg/pwndbg), macOS: `brew install pwndbg/tap/pwndbg-gdb`

## 其他资源

- [tools.md](tools.md) - 静态分析工具 (GDB, Ghidra, radare2, IDA, Binary Ninja, dogbolt.org, Capstone 的 RISC-V, Unicorn 模拟, Python 字节码, WASM, Android APK, .NET, 打包二进制文件)
- [tools-dynamic.md](tools-dynamic.md) (包括 movfuscated 二进制的 Intel Pin 指令计数侧信道, 指令仅跟踪重建, LD_PRELOAD memcmp 侧信道用于逐字节暴力破解) - 动态分析工具: Frida (钩子, 反调试绕过, 内存扫描, Android/iOS), angr 符号执行 (路径探索, 约束, CFG), lldb (macOS/LLVM 调试器), x64dbg (Windows), Qiling (跨平台模拟带 OS 支持), Triton (动态符号执行)
- [tools-advanced.md](tools-advanced.md) - 高级工具: VMProtect/Themida 分析, 二进制差异 (BinDiff, Diaphora), 反混淆框架 (D-810, GOOMBA, Miasm), Rizin/Cutter, RetDec, 自定义 VM 字节码提取到 LLVM IR, 高级 GDB (Python 脚本, 条件断点, 监视点, 使用 rr 的反调试, pwndbg/GEF), 高级 Ghidra 脚本, 修补 (Binary Ninja API, LIEF)
- [anti-analysis.md](anti-analysis.md) - 全面反分析: Linux 反调试 (ptrace, /proc, 时间, 信号, 直接系统调用), Windows 反调试 (PEB, NtQueryInformationProcess, 堆标志, TLS 回调, 硬件/软件断点检测, 基于异常, 线程隐藏), 反 VM/沙盒 (CPUID, MAC, 时间, 证据, 资源), 反 DBI (Frida 检测/绕过), 代码完整性/自哈希, 反反汇编 (不透明谓词, 无用字节), MBA 识别/简化, SIGFPE 信号处理器侧信道通过 strace 计数, 通过栈帧操作链无调用函数, 绕过策略
- [patterns.md](patterns.md) - 基础二进制模式: 自定义 VM, 反调试, 纳米米, 自修改代码, XOR 密码, 混合模式启动器, LLVM 混淆, S-box/密钥流, SECCOMP/BPF, 异常处理程序, 内存转储, 字节级转换, x86-64 惯性, 基于信号的探索, 恶意软件反分析, 多阶段 shellcode, 时间侧信道, 多线程反调试带诱饵 + 信号处理程序 MBA, INT3 修补 + coredump 暴力破解预言机, 信号处理程序链 + LD_PRELOAD 预言机
- [patterns-ctf.md](patterns-ctf.md) - 竞赛特定模式 (Part 1): 隐藏模拟器指令, LD_PRELOAD 密钥提取, SPN 静态提取, 图像 XOR 平滑度, 逐字节密码, 数学收敛位图, Windows PE XOR 位图 OCR, 两阶段 RC4+VM 加载器, 内核模块迷宫解决, 多线程 VM 通道, 通过字符串差异检测后门共享库, 带有 RC4 平坦二进制的自定义 binfmt 内核模块, 哈希解析导入 / 无导入勒索软件, ELF 节头损坏用于反分析
- [patterns-ctf-2.md](patterns-ctf-2.md) - 竞赛特定模式 (Part 2): 多层自解密暴力破解, 嵌入式 ZIP+XOR 许可证, 栈字符串反混淆, 前缀哈希暴力破解, CVP/LLL 格子用于整数验证, 决策树函数混淆分析 (ROPfuscation)
- [patterns-ctf-3.md](patterns-ctf-3.md) - 竞赛特定模式 (Part 3): Z3 单行 Python 电路, 滑动窗口 popcount, 通过 ioctl 的键盘 LED 摩尔斯电码, C++ 析构函数隐藏验证, 系统调用副作用内存损坏, MFC 对话事件处理程序, VM 顺序密钥链暴力破解, Burrows-Wheeler 变换反转, OpenType 字体连字利用, GLSL 着色器 VM 带自修改代码, 指令计数作为密码状态, 通过 objdump 批量 crackme 自动化, fork+pipe+死分支反分析, 通过 sigmoid 层反转 TensorFlow DNN, 通过内核 JIT 到 x64 汇编分析 BPF 过滤器
- [languages.md](languages.md) - 语言特定: Python 字节码 & 指令重新映射, Python 版本特定字节码, Pyarmor 静态解包, DOS 桩, HarmonyOS HAP/ABC, Brainfuck/esolangs (+ BF 字符逐字节静态分析, BF 侧信道读取预言机, BF 比较惯语检测), UEFI, 转编译到 C, 代码覆盖率侧信道, OPAL 函数式反汇编, 非双射替换, FRACTRAN 程序反转
- [languages-platforms.md](languages-platforms.md) - 平台/框架特定: Rust serde_json 模式恢复, Android JNI RegisterNatives 混淆, Android DEX 运行时字节码修补通过 /proc/self/maps, Android 本地 .so 加载绕过通过新项目, Frida Firebase Cloud Functions 绕过, Verilog/硬件反汇编, 前缀逐前缀哈希反转, Ruby/Perl 多语言约束满足, Electron ASAR 提取 + 本地二进制分析, Node.js npm 运行时内省
- [languages-compiled.md](languages-compiled.md) - Go 二进制反汇编 (GoReSym, goroutines, 内存布局, 通道操作, embed.FS, Go 二进制 UUID 修补用于 C2 列举), Rust 二进制反汇编 (demangling, Option/Result, Vec, panic 字符串), Swift 二进制反汇编 (demangling, 协议见证表), Kotlin/JVM (协程状态机), Haskell GHC CMM 中间语言用于递归结构分析, C++ (vtable 重建, RTTI, STL 模式)
- [platforms.md](platforms.md) - 平台特定反汇编: macOS/iOS (Mach-O, 代码签名, Objective-C 运行时, Swift, dyld, 越狱绕过), 嵌入式/IoT 固件 (binwalk, UART/JTAG/SPI 提取, ARM/MIPS, RTOS), 内核驱动 (Linux .ko, eBPF, Windows .sys), 汽车电子 CAN 总线
- [platforms-hardware.md](platforms-hardware.md) - 硬件和高级架构反汇编: HD44780 LCD 控制器 GPIO 重建, RISC-V 高级 (自定义扩展, 特权模式, 调试), ARM64/AArch64 反汇编和利用 (调用约定, ROP 小工具, qemu-aarch64-static 模拟)
- [field-notes.md](field-notes.md) - 快速参考笔记: 二进制类型, 反调试绕过, 特定模式, CTF 案例笔记

---

## 何时转向

- 二进制理解后 Heap / ROP / 内核漏洞 → `pwn-chain/`
- 删除文件 / PCAP / 磁盘证据 → `digital-forensics/`
- 带小型客户端助手的 Web 应用 → `js-reverse/`
- 真实恶意软件 / C2 / 打包 → `malware-analysis/`
- 多类型 CTF 比赛打包 → `ctf-sandbox/` (侧车协调器)

## 问题解决工作流

1. **从字符串提取开始** - 许多简单挑战有明文 flag
2. **尝试 ltrace/strace** - 动态分析常能直接揭示 flag 而无需反汇编
3. **尝试 Frida 钩子** - 钩子 strcmp/memcmp 捕获预期值而无需反汇编
4. **尝试 angr** - 符号执行自动解决许多 flag 检查器
5. **尝试 Qiling** - 模拟外架构二进制或绕过重型反调试而无需证据
6. **在修改执行前映射控制流**
7. **通过脚本 (r2pipe, Frida, angr, Python) 自动化手动过程**
8. **通过比较反编译器输出验证假设** (dogbolt.org 用于并排比较)

## 快速胜利（优先尝试！）

```bash
# 明文 flag 提取
strings binary | grep -E "flag\{|CTF\{|pico"
strings binary | grep -iE "flag|secret|password"
rabin2 -z binary | grep -i "flag"

# 动态分析 - 常直接捕获 flag
ltrace ./binary
strace -f -s 500 ./binary

# 十六进制转储搜索
xxd binary | grep -i flag

# 用测试输入运行
./binary AAAA
echo "test" | ./binary
```

## 初始分析

```bash
file binary           # 类型, 架构
checksec --file=binary # 安全特性 (用于 pwn)
chmod +x binary       # 使其可执行
```

## 内存转储策略

**关键洞察**：让程序计算答案，然后转储。在最终比较处断点 (`b *main+OFFSET`)，输入任何正确长度的输入，然后 `x/s $rsi` 转储计算出的 flag。

## 诱饵 flag 检测

**模式**：多个假目标前真实检查。查找序列中多个比较目标带不同成功消息。在最终比较处断点，而不是早期断点。

## GDB PIE 调试

PIE 二进制随机化基地址。使用相对断点：
```bash
gdb ./binary
start                    # 强制 PIE 基地址解析
b *main+0xca            # 相对于 main
run
```

## 比较方向（关键！）

两种模式：(1) `transform(flag) == stored_target` — 反转转换。(2) `transform(stored_target) == flag` — flag 是转换后的数据，只需将转换应用于存储目标。

## 常见加密模式

- 单字节 XOR - 尝试所有 256 个值
- 已知明文 XOR (`flag{`, `CTF{`)
- 硬编码密钥的 RC4
- 自定义置换 + XOR
- 位置索引 XOR (`^ i` 或 `^ (i & 0xff)`) 与重复密钥分层

## 快速工具参考

```bash
# Radare2
r2 -d ./binary     # 调试模式
aaa                # 分析
afl                # 列出函数
pdf @ main         # 反汇编 main

# Ghidra (无头)
analyzeHeadless project/ tmp -import binary -postScript script.py

# IDA
ida64 binary       # 在 IDA64 中打开
```

## 深入笔记

在第一轮分诊后知道目标类型时，使用 [field-notes.md](field-notes.md)。

- 目标格式: Python 字节码, WASM, Android, Flutter, .NET, UPX, Tauri
- 技术笔记: 反调试绕过, VM 分析, x86-64 惯性, 迭代求解器, Unicorn, 时间侧信道
- 平台笔记: macOS/iOS, 嵌入式固件, 内核驱动, Swift, Kotlin, Go, Rust, D
- 案例笔记: 现代 CTF 特定反汇编模式和经典挑战模式

---

## 路由上下文

**上游入口**: `skills/SKILL.md`（总控）、`routing.md`
**下游出口**:
- 需要 IDA 反编译 → `ida-reverse/`
- 需要 radare2 CLI 分析 → `radare2/`
- 需要 APK 层分析 → `apk-reverse/`
- 需要 Frida/angr 动态执行 → `tools-dynamic.md`
- 需要绕过反调试 → `anti-analysis.md`
- 遇到特定语言（Go/Rust/Python/WASM）→ `languages*.md`
- 遇到 CTF 模式 → `patterns*.md`

**同级关联模块**: `apk-reverse/`（APK 定位到 .so 时可切回本模块的 Frida/radare2 分支）

## 任务完成自检（声称完成前 MUST 通过）

- [ ] 我是否执行了工作流中的每一步（而不是只阅读）？
- [ ] 我是否基于 `tool-index` 使用了真实工具路径？
- [ ] 我是否产出了可复现证据（命令/脚本/截图/报告）？
- [ ] 我是否完成并回写了 RULES 要求的 Checklist 项？
