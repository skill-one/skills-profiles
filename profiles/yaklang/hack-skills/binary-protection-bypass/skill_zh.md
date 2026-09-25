# 技能：二进制保护绕过 — 专家攻击手册

> **AI 加载指令**：专家级二进制保护识别与绕过技术。涵盖 ASLR、PIE、NX、RELRO、canary、FORTIFY_SOURCE、栈冲突、CET 阴影栈和 ARM MTE。每种保护都与其绕过方法及所需原语配对。内容源自 ctf-wiki 缓解部分和实际漏洞利用经验。基础模型常混淆哪些保护阻止了哪些攻击，且忽略多重保护的组合效果。

## 0. 相关路由

- [栈溢出与 ROP](../stack-overflow-and-rop/SKILL.md) — ROP 链绕过 NX，ret2libc 绕过 ASLR
- [格式化字符串漏洞利用](../format-string-exploitation/SKILL.md) — 泄露 canary、PIE、libc 地址的主要方法
- [堆溢出利用](../heap-exploitation/SKILL.md) — 堆攻击绕过 RELRO（当 GOT 为只读时）
- [任意写至 RCE](../arbitrary-write-to-rce/SKILL.md) — 当 GOT 被 RELRO 保护时，应覆盖什么内容

### 高级参考

加载 [PROTECTION_BYPASS_MATRIX.md](./PROTECTION_BYPASS_MATRIX.md) 获取全面保护 × 绕过 × 原语矩阵。

---

## 1. 保护识别

```bash
$ checksec ./binary
[*] '/path/to/binary'
    架构:     amd64-64-little
    RELRO:    全局 RELRO          ← GOT 只读
    栈:      发现 canary        ← 栈 canary 已启用
    NX:       NX 已启用          ← 栈不可执行
    PIE:      PIE 已启用         ← 位置无关代码
    FORTIFY:  已启用             ← 加固的 libc 函数
```

### 快速识别表

| 保护机制 | 检查命令 | 二进制指示 |
|---|---|---|
| ASLR | `cat /proc/sys/kernel/randomize_va_space` | 操作系统级别（0=关闭，1=部分，2=完全） |
| PIE | `checksec` 或 `readelf -h`（类型：DYN） | 二进制使用 `-pie` 编译 |
| NX | `checksec` 或 `readelf -l`（无 RWE 段） | `gcc -z noexecstack`（默认启用） |
| Canary | `checksec` 或查找 `__stack_chk_fail@plt` | `gcc -fstack-protector-all` |
| 部分RELRO | `readelf -l`（GNU_RELRO 段，`.got.plt` 可写） | `gcc -Wl,-z,relro` |
| 全局RELRO | `readelf -l` + `.got` 段只读 | `gcc -Wl,-z,relro,-z,now` |
| FORTIFY | 存在 `__printf_chk`、`__memcpy_chk` 等 | `gcc -D_FORTIFY_SOURCE=2` |

---

## 2. ASLR 绕过

ASLR 在每次执行时随机化栈、堆、libc 和 mmap 区域的基地址。

| 绕过方法 | 所需原语 | 备注 |
|---|---|---|
| 信息泄露 | 任何读取原语（格式化字符串、OOB 读取、UAF） | 泄露 libc/栈/堆地址 → 计算基地址 |
| 部分覆盖 | 写入原语（有限长度） | 覆盖最后 1-2 字节（页偏移固定） |
| 暴力破解（32位） | 重新连接/重试能力 | ~256–4096 次尝试（8-12 位熵） |
| 返回至 PLT | 栈溢出 | PLT 地址位于二进制基地址的固定偏移（若无 PIE） |
| ret2dlresolve | 栈溢出 + 写入原语 | 无需知道 libc 基址即可解析任意函数 |
| 格式化字符串泄露 | 格式化字符串漏洞 | `%N$p` 用于读取栈/libc/堆地址 |
| 栈读取 | 字节逐个（崩溃预言机） | 通过崩溃预言机逐字节读取栈 |

### ASLR 熵（x86-64 Linux）

| 区域 | 熵（位） | 位置 |
|---|---|---|
| 栈 | 22 | ~4M |
| mmap / libc | 28 | ~256M |
| 堆（brk） | 13 | ~8K |
| PIE 二进制 | 28 | ~256M |

---

## 3. PIE 绕过

PIE（位置独立可执行文件）随机化二进制自身的代码/数据基地址。

| 绕过方法 | 所需原语 | 备注 |
|---|---|---|
| 信息泄露 | 从栈读取返回地址 | PIE 基址 = 泄露地址 - 已知偏移 |
| 部分覆盖 | 单字节或双字节写入 | 页偏移的最后 12 位固定 |
| 格式化字符串泄露 | 格式化字符串漏洞 | `%N$p` 其中 N 指向 .text 返回地址 |
| 相对寻址 | 知晓二进制布局 | 如果知道相对偏移，仅需一次泄露 |

### 部分覆盖细节

```
PIE 二进制加载于: 0x555555554000（示例）
偏移 0x1234 处的函数: 0x555555555234

覆盖返回地址最后 2 字节: 0x?234 → 0x?XXX
未知: 位 12-15（一个十六进制位 = 4 位 = 16 种可能性）
成功率: 每次尝试 1/16
```

---

## 4. NX/DEP 绕过

NX（无执行）/ DEP（数据执行防护）防止在栈/堆上执行代码。

| 绕过方法 | 详情 |
|---|---|
| ROP（返回导向编程） | 链接以 `ret` 结尾的现有代码小 gadget |
| ret2libc | 直接调用 libc 函数（system、execve） |
| ret2csu | 使用 `__libc_csu_init` 小 gadget 进行受控函数调用 |
| ret2dlresolve | 伪造动态链接器结构以解析任意函数 |
| SROP | 使用 sigreturn 设置所有寄存器（来自伪造信号帧） |
| mprotect ROP | 链接 mprotect(addr, size, PROT_RWX) → 使页面可执行 → 跳转至 shellcode |
| JIT 喷溅 | 在 JIT 环境（V8 等）中，通过 JIT 编译器创建可执行代码 |

### mprotect 链

```python
# 使栈可执行，然后跳转至 shellcode
rop = b'A' * offset
rop += p64(pop_rdi) + p64(stack_page)     # 页对齐地址
rop += p64(pop_rsi) + p64(0x1000)         # 大小
rop += p64(pop_rdx) + p64(7)              # PROT_READ|PROT_WRITE|PROT_EXEC
rop += p64(mprotect_addr)
rop += p64(shellcode_addr)                 # 在可执行栈上跳转至 shellcode
```

---

## 5. RELRO 绕过

| RELRO 级别 | GOT 状态 | 绕过 |
|---|---|---|
| 无 RELRO | GOT 完全可写 | 直接覆盖 GOT |
| 部分RELRO | `.got.plt` 可写（懒加载） | GOT 覆盖仍然有效 |
| 全局RELRO | 加载时所有 GOT 条目已解析，GOT 只读 | 无法写入 GOT → 攻击其他结构 |

### 全局RELRO 替代目标

| 目标 | 条件 | 方法 |
|---|---|---|
| `__malloc_hook` | glibc < 2.34 | 使用 one_gadget 覆盖 |
| `__free_hook` | glibc < 2.34 | 覆盖为 `system`，触发 `free("/bin/sh")` |
| `_IO_FILE vtable` | 任何 glibc | FSOP / vtable 欺骗 |
| `__exit_funcs` | 任何 glibc | 覆盖退出处理程序列表 |
| `TLS_dtor_list` | glibc ≥ 2.34 | 线程本地析构函数列表（需要指针保护） |
| `.fini_array` | 若可写 | 覆盖析构函数指针 |
| 栈返回地址 | 直接栈写入 | 覆盖返回地址以进行 ROP |

参见 [任意写至 RCE](../arbitrary-write-to-rce/SKILL.md) 获取全面目标列表。

---

## 6. Canary 绕过

| 方法 | 条件 | 详情 |
|---|---|---|
| 格式化字符串泄露 | `printf(user_input)` | `%N$p` 从栈中读取 canary |
| 暴力破解 | fork() 服务器（canary 在子进程中持续存在） | 字节逐个：256 × (canary_size-1) 尝试 |
| 栈读取 | 部分覆盖 / 信息泄露 | 覆盖 canary 的空字节，通过输出泄露 |
| 线程 canary 覆盖 | 溢出达到 TLS | canary 位于 `fs:[0x28]`；溢出超出缓冲区至 TLS → 用已知值覆盖 canary |
| Canary-相对覆盖 | 溢出在 canary 之后但返回地址之前 | 跳过 canary，仅覆盖返回地址（罕见布局） |
| 堆基础 | 漏洞位于堆而非栈 | Canary 仅保护栈 |
| `__stack_chk_fail` GOT 覆盖 | 部分RELRO | 覆盖 `__stack_chk_fail@GOT` 指向无害函数 → canary 检查通过 |

### Canary 格式

```
x86:    0x00XXXXXX (4 字节，前导空字节)
x86-64: 0x00XXXXXXXXXXXXXX (8 字节，前导空字节)
```

前导 `\x00` 防止字符串操作意外读取 canary。

---

## 7. FORTIFY_SOURCE 绕过

`_FORTIFY_SOURCE=2` 添加缓冲区大小检查并限制格式化字符串操作。

| 加固函数 | 限制 | 绕过 |
|---|---|---|
| `__printf_chk` | `%n` 与位置参数 (`%N$n`) 禁止 | 使用非位置 `%n` 或 `%hn` 链 |
| `__memcpy_chk` | 检查目标缓冲区大小 | 使用堆溢出而非栈 |
| `__strcpy_chk` | 相同 | |
| `__read_chk` | 检查读取大小与缓冲区 | |

### FORTIFY_SOURCE 下的格式化字符串

```python
# %1$n 被 __printf_chk 阻止
# 但顺序（非位置）%n 可能仍然工作：
# 打印精确字节计数，然后 %hn — 必须非常精确
# 或：通过 ROP 查找二进制/libc 中的未加固 printf
```

---

## 8. CET（控制流执行技术）

Intel CET 添加两个机制：

### 阴影栈

- 硬件维护的返回地址副本
- 在 `ret` 时，CPU 检查阴影栈是否匹配实际栈
- 不匹配 → `#CP` 异常（控制保护异常）

| 影响 | 详情 |
|---|---|
| ROP 被阻止 | `ret` 时检测到返回地址覆盖 |
| JOP 可能 | `jmp [reg]` 未被阴影栈检查 |
| COP 可能 | `call [reg]` 推送至阴影栈，但目标由 IBT 验证 |

### 间接分支跟踪（IBT）

- 间接 `jmp`/`call` 必须落在 `ENDBR64` 指令上
- 非 ENDBR 落地 → `#CP` 异常

**绕过**： 
- 数据攻击（不改变控制流）
- 查找有效的 ENDBR 小 gadget 以链入有用操作
- JOP 使用 ENDBR 前缀的小 gadget
- 攻击 CFI 范围外的结构（modprobe_path、函数指针数组）

---

## 9. MTE（内存标记扩展，ARM）

ARM MTE 为内存指针和分配分配 4 位标签。标签不匹配 = 异常。

| 方面 | 详情 |
|---|---|
| 标签位 | 指针中的 4 位（位 56-59）= 16 种可能标签 |
| 粒度 | 16 字节（每个 16 字节粒度有一个标签） |
| 检查 | 加载/存储：指针标签必须匹配内存标签 |
| 概率 | 随机标签 → 攻击者正确猜测的概率为 1/16 |

### 绕过方法

| 方法 | 成功率 |
|---|---|
| 暴力破解 | 每次尝试 1/16（6.25%） |
| 标签预言机 | 侧信道确定标签（时间、错误消息） |
| 内部边界利用 | 停留在同一标记区域（使用相对偏移） |
| 标签绕过小 gadget | 如果可访问，使用 `LDGM`/`STGM` 指令 |
| 规测执行 | Spectre 风格绕过标签检查 |

---

## 10. 决策树

```
二进制分析：checksec 输出
├── NX 禁用？
│   └── 栈/堆上的 shellcode（最简单路径）
│
├── NX 启用（标准现代二进制）？
│   ├── 需要代码执行 → ROP/ret2libc
│   │
│   ├── Canary 启用？
│   │   ├── fork 服务器？ → 字节逐个暴力破解
│   │   ├── 格式化字符串？ → 通过 `%p` 泄露 canary
│   │   ├── 堆漏洞？ → canary 不保护堆
│   │   └── 部分RELRO？ → 覆盖 `__stack_chk_fail@GOT`
│   │
│   ├── PIE 启用？
│   │   ├── 格式化字符串？ → 泄露 .text 地址 → PIE 基址
│   │   ├── 部分覆盖 → 页偏移的最后 12 位固定（1/16 暴力破解）
│   │   └── OOB 读取？ → 泄露代码指针
│   │
│   ├── ASLR 启用？
│   │   ├── 可用信息泄露 → 泄露 libc 基址
│   │   ├── 无泄露 → ret2dlresolve 或 SROP
│   │   ├── 32位？ → 暴力破解可行（~4096 次尝试）
│   │   └── 返回至 PLT（无需 libc 基址即可调用 PLT）
│   │
│   ├── RELRO 级别？
│   │   ├── 无/部分 → GOT 覆盖
│   │   └── 全局 → 替代目标：
│   │       ├── glibc < 2.34 → `__malloc_hook` / `__free_hook`
│   │       ├── glibc ≥ 2.34 → `_IO_FILE` / exit_funcs / TLS_dtor_list
│   │       ├── `.fini_array`（若可写）
│   │       └── 栈返回地址
│   │
│   └── FORTIFY_SOURCE？
│       ├── 阻止位置 `%n` → 使用顺序 `%n` 或堆利用
│       └── 阻止加固函数中的缓冲区溢出 → 使用未加固路径
│
├── CET（阴影栈）？
│   ├── ROP 被阻止 → 数据攻击或 JOP
│   └── ENDBR-gadget 链接
│
└── MTE（ARM）？
    ├── 1/16 暴力破解
    └── 停留在内部进行相对腐蚀
```
