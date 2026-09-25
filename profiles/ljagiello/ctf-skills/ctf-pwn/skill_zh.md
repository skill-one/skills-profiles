# CTF 二进制漏洞利用（Pwn）

二进制漏洞利用（Pwn）CTF 挑战快速参考。这里每种技术都有一个简短示例；有关详细信息，请参阅支持文件。

## 前置条件

**Python 包（所有平台）：**
```bash
pip install "pwntools==4.15.0" "ROPgadget==7.7" "ropper==1.13.13"
# 或通过脚本：bash scripts/install_ctf_tools.sh python
```

**uv 替代方案：**
```bash
uv venv && uv pip install "pwntools==4.15.0" "ROPgadget==7.7" "ropper==1.13.13"
```

**Linux (apt)：**
```bash
apt install gdb binutils strace ltrace qemu-system-x86
```

**可选的跨架构（ARM/MIPS — Debian/Ubuntu）：**
```bash
apt install qemu-user qemu-user-static gdb-multiarch binutils-multiarch libc6-armhf-cross libc6-arm64-cross libc6-mips-cross
```

**macOS (Homebrew)：**
```bash
brew install gdb binutils qemu
```

**Ruby 宝石（所有平台）：**
```bash
gem install one_gadget seccomp-tools
```

**手动安装：**
- pwndbg — Linux: [GitHub](https://github.com/pwndbg/pwndbg), macOS: `brew install pwndbg/tap/pwndbg-gdb`
- checksec — 包含在 pwntools 中 (`checksec --file=binary`)

## 额外资源

- [overflow-basics.md](overflow-basics.md) - 栈/全局缓冲区溢出，ret2win，canary 绕过，在分叉服务器上对 canary 字节逐字节暴力破解，结构指针覆盖，有符号整数绕过，隐藏的 gadgets，基于步长的 OOB 读取泄露，通过未检查的 `memcpy` 长度的解析器栈溢出（带调用者保存寄存器恢复）
- [rop-and-shellcode.md](rop-and-shellcode.md) - 核心 ROP 链（ret2libc，syscall ROP，rdx 控制，shell 交互），ret2csu，坏字符 XOR 绕过，异国情调的 x86 gadgets（BEXTR/XLAT/STOSB/PEXT），通过 xchg rax,esp 的栈转换，sprintf() gadgets 链接以绕过坏字符，canary XOR 尾部作为 RDX 清零 gadgets，stub_execveat 系统调用作为 execve 的替代方案（通过 read() 返回值）
- [rop-advanced.md](rop-advanced.md) - 高级 ROP 技术：通过 leave;ret 将栈转换到 BSS，SROP（Sigreturn-导向编程）带 UTF-8 限制，seccomp 绕过，RETF 架构切换（x64→x32）以绕过 seccomp，带输入反转的 shellcode，.fini_array 欺骗，ret2vdso，pwntools 模板，x32 ABI 系统调用别名以绕过 seccomp，基于时间的盲 shellcode 拉取
- [format-string.md](format-string.md) - 格式字符串利用（泄露，GOT 覆盖，盲 Pwn，过滤绕过，canary 泄露，__free_hook，.rela.plt 补丁，保存的 EBP 覆盖以进行 .bss 转换，argv[0] 覆盖以进行栈溢出信息泄露，.fini_array 循环以进行多阶段利用，__printf_chk 绕过带顺序的 %p，单次调用泄露 + GOT 覆盖，通过输入转换的 ROT13 编码的格式字符串利用）
- [advanced.md](advanced.md) - seccomp 高级技术，UAF，JIT，异国情调的 GOT，通过基础转换的堆重叠，树数据结构栈未分配，ret2dlresolve，内核利用（基本）
- [heap-techniques.md](heap-techniques.md) - House of Apple 2（+ setcontext SUID 变体），House of Einherjar，House of Orange/Spirit/Lore/Force，堆整理，自定义分配器（nginx，talloc），经典 unlink，musl libc 堆（元指针 + atexit 欺骗），tcache 储存 unlink 攻击，不安全的 unlink + 顶部块合并
- [heap-techniques-2.md](heap-techniques-2.md) - CTF-writeup 堆变体：UAF vtable 指针编码 shell 参数，未初始化块残留指针泄露，tcache strcpy null-byte 溢出 + 向后合并，相邻结构 fn-pointer 溢出以泄露 libc + GOT 覆盖，隐藏菜单 tcache 欺骗，tcache double-free + 假 _IO_FILE vtable stdout 欺骗，tcache-to-fastbin 推广跨 bin 攻击，6 位索引 OOB + written_bytes 累加器，IS_MMAPED 位翻转以在 calloc'd 块上泄露未排序的 bin，通过 LSB 仅堆指针覆盖的文件名正则约束 fastbin，自定义分配器不安全的 unlink 到 GOT
- [heap-fsop.md](heap-fsop.md) - FILE-结构 (_IO_FILE) 欺骗：fastbin stdout vtable 两阶段欺骗以进行 PIE + Full RELRO，_IO_buf_base null-byte stdin 欺骗，glibc 2.24+ _IO_FILE vtable 验证绕过，对 stdin _IO_buf_end 的未排序 bin 攻击，通过 mp_ 结构的未排序 bin 损坏，realloc(ptr, 0) 作为 free() UAF，单字节引用计数器回绕 UAF
- [advanced-exploits.md](advanced-exploits.md) - 高级利用技术（第一部分）：VM 签名比较，BF JIT shellcode，类型混淆，索引偏移损坏，DNS 溢出，ASAN 阴影内存，带编码限制的格式字符串，自定义 canary 保留，有符号整数绕过，canary-aware 部分溢出，CSV 注入，MD5 原像 gadgets，VM GC UAF slab 重用，路径遍历清理器绕过，FSOP + seccomp 绕过（通过 openat/mmap/write）
- [advanced-exploits-2.md](advanced-exploits-2.md) - 高级利用技术（第二部分）：通过自我修改绕过字节码验证器，io_uring UAF 带 SQE 注入，整数截断 int32->int16，GC null-reference 级联损坏，无泄露的 libc（通过多阶段 fgets stdout FILE 覆盖），有符号/无符号 char 下溢堆溢出，XOR 密钥流暴力破解写原语，tcache 指针解密堆泄露，通过伪造块大小提升未排序 bin，FSOP stdout TLS 泄露，通过 `__call_tls_dtors` 的 TLS 析构器欺骗，自定义阴影栈指针溢出绕过，有符号 int 溢出负 OOB 堆写，XSS-to-binary Pwn 桥
- [advanced-exploits-4.md](advanced-exploits-4.md) - 高级利用技术（第四部分）：Windows SEH 覆盖 + pushad VirtualAlloc ROP，IAT 相对解析，分离进程 shell 稳定性，SeDebugPrivilege SYSTEM 提升权限，ARM 缓冲区溢出带 Thumb shellcode，Forth 解释器系统字利用，GF(2) 高斯消元法用于多阶段 tcache 欺骗，单位翻转利用原语（mprotect + 迭代代码修补），通过 still-lifes 的 Game of Life shellcode 进化，通过菜单驱动 strdup/free 排序的 UAF，通过 system() 作为有效调用目标的 Windows CFG 绕过，神经网络输出作为函数指针索引 OOB，shellcode 独特字节限制绕过（通过计数器溢出）
- [advanced-exploits-3.md](advanced-exploits-3.md) - 高级利用技术（第三部分）：栈变量重叠/进位损坏 OOB，1 字节溢出通过 8 位循环计数器，游戏 AI 算术平均值 OOB 读取，任意读写 GOT 覆盖到 shell，通过 __environ + memcpy 溢出进行栈泄露，通过 uint16 跳转截断进行 JIT 沙盒逃逸，带多问题 ROP 的 DNS 压缩指针栈溢出，通过程序头修改绕过 ELF 代码签名，游戏等级格式有符号/无符号坐标不匹配，通过缺少 O_CLOEXEC 的文件描述符继承，元数据解析中的符号扩展整数下溢，带只读原语的 ROP 链构造，4 字节 shellcode 带基于时间的侧信道（通过持久寄存器），CRC 或acle 作为任意读取，UTF-8 大小写转换缓冲区溢出
- [advanced-exploits-5.md](advanced-exploits-5.md) - 高级利用技术（第五部分）：数据解释利用 — Chip-8 模拟器 OOB 内存用于 ret2libc，双精度浮点快速排序 canary 重新定位，bloom filter abs(INT_MIN) 负索引 OOB 写入
- [sandbox-escape.md](sandbox-escape.md) - 自定义 VM 利用，FUSE/CUSE 设备，busybox/restricted shell，shell 技巧，process_vm_readv 沙盒绕过，命名管道文件大小绕过，CPU 模拟器打印指令 Python eval 注入（交叉引用 ctf-misc/pyjails.md 以获取 Python 监狱技巧）
- [kernel.md](kernel.md) - Linux 内核利用基础：环境设置，QEMU 调试，堆喷雾结构（tty_struct，poll_list，user_key_payload，seq_operations），内核栈溢出，canary 泄露，权限提升（ret2usr，内核 ROP），modprobe_path 覆盖，core_pattern 覆盖，kmalloc 大小不匹配堆溢出 + struct file f_op 损坏
- [kernel-techniques.md](kernel-techniques.md) - 内核利用技术：tty_struct kROP（假 vtable + 栈转换），通过 ioctl 寄存器控制进行 AAW，userfaultfd 竞态稳定，SLUB 分配器内部（freelist 硬化/混淆），通过内核恐慌泄露，MADV_DONTNEED 竞态窗口扩展（DiceCTF 2026），跨缓存 CPU 分裂攻击（DiceCTF 2026），PTE 重叠文件写入（DiceCTF 2026），通过失败的文件打开绕过 addr_limit 以进行内核内存读写
- [kernel-bypass.md](kernel-bypass.md) - 内核保护绕过：KASLR/FGKASLR 绕过（__ksymtab），KPTI 绕过（swapgs trampoline，signal handler，通过 ROP 的 modprobe_path/core_pattern），SMEP/SMAP 绕过，GDB 内核模块调试，initramfs/virtio-9p 工作流程，利用模板，利用交付
- [field-notes.md](field-notes.md) - 详细的 pwn 笔记：堆利用快速参考，额外的利用笔记，有用命令

---

## 何时转换

- 如果你还没有理解二进制程序的作用，在尝试利用它之前切换到 `/ctf-reverse`。
- 如果服务实际上是受限的 shell，编码谜题或沙盒语言挑战，切换到 `/ctf-misc`。
- 如果利用路径依赖于 Web 端点，会话错误或上传原语比内存损坏更多，切换到 `/ctf-web`。
- 如果漏洞需要在利用之前打破加密原语，切换到 `/ctf-crypto`。

## 快速启动命令

```bash
# 二进制分析
checksec --file=binary
file binary
readelf -h binary

# 查找 gadgets
ROPgadget --binary binary | grep "pop rdi"
ropper -f binary --search "pop rdi"
one_gadget /lib/x86_64-linux-gnu/libc.so.6

# 调试
gdb -q binary -ex 'start' -ex 'checksec'

# 模式用于偏移查找
python3 -c "from pwn import *; print(cyclic(200))"
python3 -c "from pwn import *; print(cyclic_find(0x61616168))"

# libc 识别
./libc-database/find puts <leaked_addr_last_3_nibbles>
```

## 源代码警告标志

- 线程/`pthread` -> 竞态条件
- `usleep()`/`sleep()` -> 定时窗口
- 多个线程中的全局变量 -> TOCTOU

## 竞态条件利用

```bash
bash -c '{ echo "cmd1"; echo "cmd2"; sleep 1; } | nc host port'
```

## 常见漏洞

- 缓冲区溢出：`gets()`，`scanf("%s")`，`strcpy()`
- 格式字符串：`printf(user_input)`
- 整数溢出，UAF，竞态条件

## 保护对利用策略的影响

| 保护 | 状态 | 影响 |
|------|------|------|
| PIE | 禁用 | 所有地址（GOT，PLT，函数）都是固定的 - 直接覆盖有效 |
| RELRO | 部分禁用 | GOT 是可写的 - GOT 覆盖攻击可能 |
| RELRO | 全部禁用 | GOT 是只读的 - 需要替代目标（钩子，vtables，返回地址） |
| NX | 启用 | 不能在栈/堆上执行 shellcode - 使用 ROP 或 ret2win |
| Canary | 存在 | 栈损坏检测 - 需要泄露或避免栈溢出（使用堆） |

**快速决策树：**
- 部分RELRO + 无 PIE -> GOT 覆盖（最简单，使用固定地址）
- 全部 RELRO -> 目标 `__free_hook`，`__malloc_hook`（glibc < 2.34），或返回地址
- 栈 canary 存在 -> 优先使用基于堆的攻击或首先泄露 canary

## 栈缓冲区溢出

1. 查找偏移：`cyclic 200` 然后 `cyclic -l <value>`
2. 检查保护：`checksec --file=binary`
3. 无 PIE + 无 canary = 直接 ROP
4. 通过格式字符串或部分覆盖泄露 canary
5. 在分叉服务器上对 canary 进行逐字节暴力破解（7*256 次尝试最大）

**带魔法值的 ret2win：** 溢出 -> `ret`（对齐）-> `pop rdi; ret` -> 魔法 -> win(). **栈对齐：** 在 `movaps` 中 SIGSEGV = 添加额外的 `ret` gadgets。**偏移：** 缓冲区在 `rbp - N`，返回在 `rbp + 8`，总计 = N + 8。**输入过滤：** 断言有效载荷避免 `memmem()` 禁止的字符串。**Gadgets：** `ROPgadget --binary binary | grep "pop rdi"`，或 pwntools `ROP()` 用于 CMP 立即数中的隐藏 gadgets。有关完整利用代码，请参阅 [overflow-basics.md](overflow-basics.md)。

## 解析器栈溢出（未检查的 memcpy）

**模式：** 自定义文件解析器（PCAP，图像，存档）分配固定栈缓冲区，但输入记录可以超过它。`memcpy` 在未验证长度的情况下复制，溢出保存的寄存器和返回地址。必须恢复调用者保存的寄存器：`rbx` 到可读内存（BSS），循环计数器到退出值，然后 `ret` gadgets + win 函数。有关完整利用和 GOT 目标选择表，请参阅 [overflow-basics.md](overflow-basics.md#parser-stack-overflow-via-unchecked-memcpy-length-metactf-flash-2026)。

## 结构指针覆盖（堆菜单挑战）

**模式：** 菜单创建/修改/删除具有数据缓冲区的结构 + 指针。将名称溢出到指针字段，然后通过修改写入 win 地址。有关完整利用和 GOT 目标选择表，请参阅 [overflow-basics.md](overflow-basics.md)。

## 有符号整数绕过

**模式：** `scanf("%d")` 而没有符号检查；负数量 * 价格 = 负总数，绕过余额检查。有关详细信息，请参阅 [overflow-basics.md](overflow-basics.md)。

## Canary-aware 部分溢出

**模式：** 溢出 `valid` 标志在缓冲区和 canary 之间。使用 `./` 作为无操作路径填充以进行精确长度。有关详细信息，请参阅 [overflow-basics.md](overflow-basics.md) 和 [advanced.md](advanced.md) 的完整利用链。

## 全局缓冲区溢出（CSV 注入）

**模式：** 相邻的全局变量；通过额外的 CSV 分隔符溢出更改文件名指针。有关详细信息，请参阅 [overflow-basics.md](overflow-basics.md) 和 [advanced.md](advanced.md) 的完整利用。

## ROP 链构建

通过 `puts@PLT(puts@GOT)` 泄露 libc，返回到漏洞，使用 `system("/bin/sh")` 进行第二阶段。有关完整的两阶段 ret2libc 模式，泄露解析和返回目标选择，请参阅 [rop-and-shellcode.md](rop-and-shellcode.md)。

**DynELF libc 发现：** `pwntools.DynELF(leak_func, pointer_in_libc)` 远程解析 libc 符号而无需知道 libc 版本。有关详细信息，请参阅 [rop-and-shellcode.md](rop-and-shellcode.md#dynelf-automated-libc-discovery-rc3-ctf-2016)。

**在小型缓冲区中的约束 shellcode：** 当缓冲区太小，使用 `read()` shellcode 存根（< 20 字节）来拉取完整的第二阶段 shellcode。有关详细信息，请参阅 [rop-and-shellcode.md](rop-and-shellcode.md#constrained-shellcode-in-small-buffers-tum-ctf-2016)。

**原始系统调用 ROP：** 当 `system()`/`execve()` 导致崩溃（CET/IBT）时，使用来自 libc 的 `pop rax; ret` + `syscall; ret`。有关详细信息，请参阅 [rop-and-shellcode.md](rop-and-shellcode.md)。

**ret2csu：** `__libc_csu_init` gadgets 控制 `rdx`，`rsi`，`edi` 并调用任何 GOT 函数 — 通用 3 参数调用而无需 libc gadgets。有关详细信息，请参阅 [rop-and-shellcode.md](rop-and-shellcode.md#ret2csu--__libc_csu_init-gadgets-crypto-cat)。

**坏字符 XOR 绕过：** 在写入 `.data` 之前，用密钥 XOR 有效载荷数据，然后在原位用 ROP gadgets XOR 回去。避免空字节，换行符和其他过滤字符。有关详细信息，请参阅 [rop-and-shellcode.md](rop-and-shellcode.md#bad-character-bypass-via-xor-encoding-in-rop-crypto-cat)。

**异国情调的 gadgets（BEXTR/XLAT/STOSB/PEXT）：** 当标准的 `mov` 写入 gadgets 不可用时，链接晦涩的 x86 指令以进行逐字节内存写入。有关详细信息，请参阅 [rop-and-shellcode.md](rop-and-shellcode.md#exotic-x86-gadgets--bextrxlatstosbpext-crypto-cat)。

**栈转换（xchg rax,esp）：** 当溢出太小而无法进行完整的 ROP 链时，将栈指针交换到攻击者控制的堆/缓冲区。需要首先使用 `pop rax; ret` 加载转换地址。有关详细信息，请参阅 [rop-and-shellcode.md](rop-and-shellcode.md#stack-pivot-via-xchg-raxesp-crypto-cat)。

**rdx 控制：** 在 `puts()` 之后，rdx 被破坏为 1。使用来自 libc 的 `pop rdx; pop rbx; ret`，或重新进入二进制的读取设置 + 栈转换。有关详细信息，请参阅 [rop-and-shellcode.md](rop-and-shellcode.md)。

**Canary XOR 尾部作为 rdx 清零 gadgets：** 当没有 `pop rdx; ret` 存在时，跳转到 canary 检查尾部 `xor rdx, fs:28h` — 当 canary 完好时，它会将 RDX 清零。有关详细信息，请参阅 [rop-and-shellcode.md](rop-and-shellcode.md#stack-canary-xor-epilogue-as-rdx-zeroing-gadget-volgactf-2017)。

**stub_execveat 作为 execve 的替代方案：** 当没有 `pop rax; ret` 存在时，使用 `stub_execveat`（系统调用 322/0x142）而不是 `execve` — 发送恰好 0x142 字节，因此 `read()` 返回值设置 rax。有关详细信息，请参阅 [rop-and-shellcode.md](rop-and-shellcode.md#stub_execveat-syscall-as-execve-alternative-asis-ctf-2018)。

**shell 交互：** 在 `execve` 之后，`sleep(1)` 然后 `sendline(b'cat /flag*')`。有关详细信息，请参阅 [rop-and-shellcode.md](rop-and-shellcode.md)。

## 通过输入转换的格式字符串

**ROT13 编码的格式字符串：** 当输入在到达 `printf` 之前被 ROT13/Caesar 变换时，预先编码格式字符串有效载荷以逆转换，以便它完整地到达。有关详细信息，请参阅 [format-string.md](format-string.md#format-string-exploit-through-rot13-encoding-sunshinectf-2018)。

## 内核利用

**通过失败的文件打开绕过 addr_limit：** 当内核模块设置 `addr_limit = KERNEL_DS` 但在错误路径上未能恢复它时，强制错误（例如，使目标文件成为目录）以保留来自用户空间的 `read()`/`write()` 的内核内存访问。有关详细信息，请参阅 [kernel-techniques.md](kernel-techniques.md#kernel-addr_limit-bypass-via-failed-file-open-midnight-sun-ctf-2018)。

## 沙盒和模拟器逃逸

**CPU 模拟器 eval 注入：** 当模拟器的打印指令使用 `eval('"' + buf + '"')` 用于转义序列时，在模拟器内存中构建 `"+__import__("os").system("cmd")#` 以通过 ADD 指令逃逸字符串并执行 Python。有关详细信息，请参阅 [sandbox-escape.md](sandbox-escape.md#cpu-emulator-print-opcode-python-eval-injection-midnight-sun-ctf-2018)。

## 高级利用原语

**神经网络函数指针 OOB：** 当二进制使用 NN 输出作为没有边界检查的函数指针数组的索引时，重新训练权重/偏差以产生一个越界的索引，从偏差数组读取目标地址。有关详细信息，请参阅 [advanced-exploits-4.md](advanced-exploits-4.md#neural-network-output-as-function-pointer-index-oob-swampctf-2018)。

**通过计数器溢出绕过 shellcode 独特字节限制：** 当 shellcode 限制为 N 个独特字节时，喷雾栈以损坏 `seen[256]` 计数器，然后重新执行 main（跳过 `memset`）以便溢出的计数器在第二次运行时允许任意字节。有关详细信息，请参阅 [advanced-exploits-4.md](advanced-exploits-4.md#shellcode-unique-byte-limit-bypass-via-counter-overflow-blaze-ctf-2018)。

## 深入笔记

在确认挑战确实是重度利用之后，使用 [field-notes.md](field-notes.md)。

- 堆和分配器笔记：House of Apple，tcache，不安全的 unlink，talloc，UAF，FSOP
- 高级利用笔记：seccomp 绕过，ret2vdso，io_uring，整数截断，ASAN，定时或acles
- 沙盒和混合笔记：pyjail 交叉引用，busybox 逃逸，自定义 VMs，shell 技巧，路径清理器
- 内核和 Windows 笔记：内核剧本，SEH，CFG 绕过，权限提升
- 历史案例笔记：较旧的但仍可重用的 CTF 利用模式
