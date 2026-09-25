# CTF逆向工程

RE挑战的快速参考。有关详细技术，请参阅支持文件。

## 前置条件

**Python包（所有平台）：**
```bash
pip install frida-tools angr qiling uncompyle6 capstone lief z3-solver
# 对于Python 3.9+字节码：从源代码构建pycdc
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

**radare2插件：**
```bash
r2pm -ci r2ghidra   # radare2的原生Ghidra反编译器
```

**手动安装：**
- pwndbg — Linux: [GitHub](https://github.com/pwndbg/pwndbg), macOS: `brew install pwndbg/tap/pwndbg-gdb`

## 其他资源

- [unicorn-emulation.md](unicorn-emulation.md) - Unicorn CPU模拟：原始二进制汇编模拟、钩子、ARM/MIPS/Thumb、混合模式、固件MMIO、Keystone+Capstone逆向跟踪、shellcode解包、自定义虚拟机、vs Qiling决策（有时使用unicorn+二进制+汇编比使用完整的GDB/angr更容易逆向）
- [tools.md](tools.md) - 静态分析工具（GDB、Ghidra、radare2、IDA、Binary Ninja、dogbolt.org、Capstone RISC-V、Unicorn模拟、Python字节码、WASM、Android APK、.NET、打包二进制文件）
- [tools-dynamic.md](tools-dynamic.md) - 动态分析工具：Frida（钩子、反调试绕过、内存扫描、Android/iOS）、angr符号执行（路径探索、约束、CFG）、lldb（macOS/LLVM调试器）、x64dbg（Windows）
- [tools-emulation.md](tools-emulation.md) - 模拟框架和侧信道工具：Qiling（跨平台操作系统级模拟）、Triton（DSE）、Intel Pin指令计数+遗传算法侧信道、指令仅跟踪重建、LD_PRELOAD时间冻结和memcmp侧信道用于字节逐个暴力破解
- [tools-advanced.md](tools-advanced.md) - 高级工具（第一部分）：VMProtect/Themida分析、二进制差异（BinDiff、Diaphora）、反混淆框架（D-810、GOOMBA、Miasm）、Qiling框架、Triton DSE、Manticore、Rizin/Cutter、RetDec、自定义虚拟机字节码提升到LLVM IR
- [tools-advanced-2.md](tools-advanced-2.md) - 高级工具（第二部分）：高级GDB（Python脚本、暴力破解、条件断点、观察点、使用rr的逆向调试、pwndbg/GEF）、高级Ghidra脚本、补丁（Binary Ninja API、LIEF）、GDB约束提取+ILP求解器（BackdoorCTF 2017）、GDB位置编码输入零标志监控（EKOPARTY 2017）、LD_PRELOAD执行-only二进制转储（BackdoorCTF 2017）、PEDA当前_inst逐位标志刮擦器（CONFidence CTF 2019 Teaser）
- [anti-analysis.md](anti-analysis.md) - 反分析分类：Linux反调试（ptrace、/proc、时间、信号、直接系统调用）、Windows反调试（PEB、NtQueryInformationProcess、堆标志、TLS回调、硬件/软件断点检测、基于异常、线程隐藏）、反VM/沙盒（CPUID、MAC、时间、痕迹、资源）、反DBI（Frida检测/绕过）、代码完整性/自哈希、反反汇编（不透明谓词、垃圾字节）、MBA识别/简化、综合绕过策略
- [anti-analysis-ctf.md](anti-analysis-ctf.md) - CTF写解技术：SIGILL处理程序用于执行模式切换（Hack.lu 2015）、SIGFPE信号处理程序侧信道通过strace计数（PlaidCTF 2017）、使用Keystone和Unicorn的指令跟踪逆向（MeePwn 2017）、通过栈帧操作的无调用函数链（THC 2018）、通过`process_vm_writev`的父进程修补子二进制转储（Google CTF Quals 2018）
- [patterns.md](patterns.md) - 基础二进制模式：自定义虚拟机、反调试、纳米米、自修改代码、XOR密码、混合模式stagers、LLVM混淆、S-box/密钥流、SECCOMP/BPF、异常处理程序、内存转储、逐字节转换、x86-64陷阱、自定义mangle逆向、基于位置的转换、十六进制编码字符串比较、基于信号的二进制探索
- [patterns-runtime.md](patterns-runtime.md) - 运行时补丁和预言机技术：恶意软件反分析绕过、多阶段shellcode加载器、时间侧信道攻击、多线程反调试与诱饵+信号处理程序MBA（ApoorvCTF 2026）、INT3补丁+核心转储暴力破解预言机（Pwn2Win 2016）、信号处理程序链+LD_PRELOAD预言机（Nuit du Hack 2016）、printf格式字符串虚拟机反编译到Z3（SECCON 2017）、四叉树递归图像格式解析（Google CTF Quals 2018）
- [patterns-ctf.md](patterns-ctf.md) - 竞赛特定模式（第一部分）：隐藏模拟器操作码、LD_PRELOAD密钥提取、SPN静态提取、图像XOR平滑度、逐字节密码、数学收敛位图、Windows PE XOR位图OCR、两阶段RC4+VM加载器、GBA ROM中间值、Sprague-Grundy博弈理论、内核模块迷宫解决、多线程虚拟机通道、通过字符串差异检测后门共享库、带有RC4平面二进制的自定义binfmt内核模块、哈希解析导入/无导入勒索软件、ELF节头损坏用于反分析
- [patterns-ctf-2.md](patterns-ctf-2.md) - 竞赛特定模式（第二部分）：多层自解密暴力破解、嵌入式ZIP+XOR许可证、栈字符串反混淆、前缀哈希暴力破解、CVP/LLL格网用于整数验证、决策树函数混淆分析（ROPfuscation）
- [patterns-ctf-3.md](patterns-ctf-3.md) - 竞赛特定模式（第三部分）：Z3单行Python电路、滑动窗口popcount、通过ioctl的键盘LED摩尔斯电码、C++析构函数隐藏验证、系统调用副作用内存损坏、MFC对话框事件处理程序、虚拟机顺序密钥链暴力破解、Burrows-Wheeler变换逆向、OpenType字体连字利用、GLSL着色器虚拟机带自修改代码、指令计数作为加密状态、通过objdump批量破解me自动化、fork+pipe+死分支反分析、通过sigmoid层逆向的TensorFlow DNN逆向、通过内核JIT到x64汇编的BPF过滤器分析
- [languages.md](languages.md) - 语言特定：Python字节码&操作码重映射、Python版本特定字节码、Pyarmor静态解包、DOS桩、Unity IL2CPP、HarmonyOS HAP/ABC、Brainfuck/esolangs（+ BF逐字符静态分析、BF侧信道读取计数预言机、BF比较惯语检测）、UEFI、转编译为C、代码覆盖率侧信道、OPAL函数逆向、非双射替换、FRACTRAN程序逆向
- [languages-platforms.md](languages-platforms.md) - 平台/框架特定：Roblox位置文件分析、Godot游戏资源提取、Rust serde_json模式恢复、Android JNI RegisterNatives混淆、Android DEX运行时字节码修补通过/proc/self/maps、通过新项目绕过Android原生.so加载、Frida Firebase Cloud Functions绕过、Verilog/硬件逆向、前缀与前缀哈希逆向、Ruby/Perl多语言约束满足、Electron ASAR提取+原生二进制分析、Node.js npm运行时内省
- [languages-compiled.md](languages-compiled.md) - Go二进制逆向（GoReSym、goroutines、内存布局、通道操作、embed.FS、Go二进制UUID修补用于C2枚举）、Rust二进制逆向（demangling、Option/Result、Vec、panic字符串）、Swift二进制逆向（demangling、协议见证表）、Kotlin/JVM（协程状态机）、Haskell GHC CMM中间语言用于递归结构分析、C++（vtable重建、RTTI、STL模式）
- [platforms.md](platforms.md) - 平台特定逆向：macOS/iOS（Mach-O、代码签名、Objective-C运行时、Swift、dyld、越狱绕过）、嵌入式/IoT固件（binwalk、UART/JTAG/SPI提取、ARM/MIPS、RTOS）、内核驱动（Linux .ko、eBPF、Windows .sys）、游戏引擎（Unreal Engine、Unity、反作弊、Lua）、汽车CAN总线
- [platforms-hardware.md](platforms-hardware.md) - 硬件和高级架构逆向：HD44780 LCD控制器GPIO重建、RISC-V高级（自定义扩展、特权模式、调试）、ARM64/AArch64逆向和利用（调用约定、ROP小工具、qemu-aarch64-static模拟）
- [field-notes.md](field-notes.md) - 快速参考笔记：二进制类型、反调试绕过、专业模式、CTF案例笔记

---

## 何时转向

- 如果你已经理解了二进制文件，现在需要堆、ROP或内核利用，切换到`/ctf-pwn`。
- 如果挑战实际上是恢复已删除的文件、PCAP数据或磁盘痕迹，切换到`/ctf-forensics`。
- 如果目标是Web应用程序，并且你只逆向一个小型客户端辅助脚本，切换到`/ctf-web`。
- 如果二进制文件实现了机器学习模型，并且挑战是关于模型攻击或对抗性输入，切换到`/ctf-ai-ml`。
- 如果逆向的二进制文件的核心逻辑是加密算法或数学问题，切换到`/ctf-crypto`。
- 如果二进制文件是真实的恶意软件样本，具有C2、打包或规避行为，切换到`/ctf-malware`。
- 如果挑战是一个玩具虚拟机、编码谜题或pyjail而不是一个真实的二进制文件，切换到`/ctf-misc`。

## 问题解决工作流程

1. **从字符串提取开始** - 许多简单的挑战都有明文标志
2. **尝试ltrace/strace** - 动态分析通常无需逆向即可揭示标志
3. **尝试Frida钩子** - 钩子strcmp/memcmp以捕获预期值而无需逆向
4. **尝试angr** - 符号执行自动解决许多标志检查器
5. **尝试Qiling** - 模拟外架构二进制文件或绕过重反调试而无需痕迹
6. **在修改执行之前映射控制流**
7. **通过脚本（r2pipe、Frida、angr、Python）自动化手动过程**
8. **通过比较反编译器输出来验证假设**（dogbolt.org用于并排比较）

## 快速胜利（首先尝试！）

```bash
# 明文标志提取
strings binary | grep -E "flag\{|CTF\{|pico"
strings binary | grep -iE "flag|secret|password"
rabin2 -z binary | grep -i "flag"

# 动态分析 - 通常直接捕获标志
ltrace ./binary
strace -f -s 500 ./binary

# 十六进制转储搜索
xxd binary | grep -i flag

# 使用测试输入运行
./binary AAAA
echo "test" | ./binary
```

## 初始分析

```bash
file binary           # 类型、架构
checksec --file=binary # 安全特性（用于pwn）
chmod +x binary       # 使其可执行
```

## 内存转储策略

**关键洞察：** 让程序计算答案，然后转储它。在最终比较处断点（`b *main+OFFSET`），输入任何正确长度的输入，然后`x/s $rsi`以转储计算出的标志。

## 诱饵标志检测

**模式：** 在真实检查之前有多个假目标。查找序列中具有不同成功消息的多个比较目标。在最终比较处设置断点，而不是之前的断点。

## GDB PIE调试

PIE二进制文件随机化基地址。使用相对断点：
```bash
gdb ./binary
start                    # 强制PIE基地址解析
b *main+0xca            # 相对于main
run
```

## 比较方向（关键！）

两种模式： (1) `transform(flag) == stored_target` — 反转转换。 (2) `transform(stored_target) == flag` — 标志是转换后的数据，只需将转换应用于存储的目标。

## 常见加密模式

- 单字节XOR - 尝试所有256个值
- 已知明文XOR（`flag{`、`CTF{`）
- 带硬编码密钥的RC4
- 自定义置换+XOR
- 位置索引XOR（`^ i`或`^ (i & 0xff)`）与重复密钥分层

## 快速工具参考

```bash
# Radare2
r2 -d ./binary     # 调试模式
aaa                # 分析
afl                # 列出函数
pdf @ main         # 反汇编main

# Ghidra (无头)
analyzeHeadless project/ tmp -import binary -postScript script.py

# IDA
ida64 binary       # 在IDA64中打开
```

## 深入笔记

在第一轮筛选后，当你知道目标类型时，使用[field-notes.md](field-notes.md)。

- 目标格式：Python字节码、WASM、Android、Flutter、.NET、UPX、Tauri
- 技术笔记：反调试绕过、虚拟机分析、x86-64陷阱、迭代求解器、Unicorn、时间侧信道
- 平台笔记：Godot、Roblox、macOS/iOS、嵌入式固件、内核驱动、游戏引擎、Swift、Kotlin、Go、Rust、D
- 案例笔记：现代CTF特定逆向模式和旧经典挑战模式
