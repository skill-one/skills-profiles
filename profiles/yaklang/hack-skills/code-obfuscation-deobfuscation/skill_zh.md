# 技能：代码混淆与反混淆——专家分析手册

> **AI 加载指令**：识别、分类和破解原生二进制文件中代码混淆的专家技术。涵盖无用代码、不透明谓词、自修改代码（SMC）、控制流扁平化、movfuscator、虚拟机保护程序（VMProtect/Themida/Code Virtualizer）、字符串加密、导入隐藏和反反汇编技巧。基础模型通常将加壳与混淆混淆，并且无法区分静态和动态反混淆策略。

## 0. 相关路由

- [反调试技术](../anti-debugging-techniques/SKILL.md) 当混淆的二进制文件还包含反调试层时
- [符号执行工具](../symbolic-execution-tools/SKILL.md) 当使用 angr/Z3 进行自动反混淆时
- [虚拟机与字节码逆向](../vm-and-bytecode-reverse/SKILL.md) 用于深度虚拟机保护程序字节码分析

### 快速识别选择

| IDA/Ghidra 中的症状 | 可能的混淆 | 从何处开始 |
|---|---|---|
| 平坦的 CFG，单个巨大的 switch | 控制流扁平化 | 符号执行以恢复 CFG |
| 仅 `mov` 指令 | movfuscator | demovfuscation / 基于跟踪的提取 |
| pushad/pushfd → 虚拟机入口 | 虚拟机保护程序 | 处理器表提取 |
| 执行代码之前的 XOR 循环 | SMC / 字符串加密 | 动态分析，解码后设置断点 |
| 不可能的条件（不透明谓词） | 无用代码插入 | 基于模式删除 |
| 所有字符串都不可读 | 字符串加密 | 钩子解密例程，或模拟 |
| IAT 中没有导入 | 导入隐藏 | 跟踪 GetProcAddress / 哈希解析 |

---

## 1. 无用代码与不透明谓词

### 1.1 无用代码插入

不影响程序输出的死代码，添加以增加分析时间。

**识别**：
- 写入寄存器/内存但之后从未读取的指令
- 返回值被丢弃且没有副作用的功能调用
- 具有不变边界且计算未使用结果的循环

**删除策略**：
1. 计算定义使用链（IDA/Ghidra 数据流分析）
2. 将没有下游使用的指令标记为死代码
3. 验证删除不会改变程序行为（跟踪比较）

### 1.2 不透明谓词

条件分支的条件始终为真或始终为假，但这一点不明显。

| 类型 | 示例 | 始终评估为 |
|---|---|---|
| 算术 | `x² ≥ 0` | 真 |
| 数论 | `x*(x+1) % 2 == 0` | 真（连续整数的乘积） |
| 指针 | `ptr == ptr` 在别名之后 | 真 |
| 哈希 | `CRC32(constant) == known_value` | 真 |

**反混淆**：
- 抽象解释：证明条件是常数
- 符号执行：Z3 证明 `∀x: predicate(x) = True`
- 模式匹配：识别已知的不透明谓词系列
- 动态：跟踪并观察分支从未被触发 / 始终被触发

```python
import z3
x = z3.BitVec('x', 32)
s = z3.Solver()
s.add(x * (x + 1) % 2 != 0)
print(s.check())  # unsat → 始终为真
```

---

## 2. 自修改代码（SMC）

运行时代码修补：加密代码在执行前立即解密。

### 2.1 XOR 解密循环（最常见）

```asm
lea esi, [encrypted_code]
mov ecx, code_length
mov al, xor_key
decrypt_loop:
    xor byte [esi], al
    inc esi
    loop decrypt_loop
    jmp encrypted_code  ; 现在已解密
```

### 2.2 分析策略

```
1. 识别解密例程（查找循环中向 .text 写入的 XOR/ADD/SUB）
2. 在循环完成后设置断点
3. 在断点处：转储解密后的内存区域
4. 在 IDA/Ghidra 中重新分析转储的代码
5. 对于多层：对每个解密阶段重复
```

### 2.3 通过模拟进行自动解包

```python
from unicorn import *
from unicorn.x86_const import *

mu = Uc(UC_ARCH_X86, UC_MODE_32)
mu.mem_map(0x400000, 0x10000)
mu.mem_write(0x400000, binary_code)
mu.emu_start(decrypt_entry, decrypt_end)
decrypted = mu.mem_read(code_start, code_length)
```

---

## 3. 控制流扁平化（CFF）

### 3.1 结构

原始顺序块被转换为调度器循环：

```
原始:      A → B → C → D

扁平化:     ┌──────────────────┐
               │   调度器     │
               │   switch(state) │◄─────┐
               ├──────────────────┤      │
               │ case 1: 块 A  │──────┤
               │ case 2: 块 B  │──────┤
               │ case 3: 块 C  │──────┤
               │ case 4: 块 D  │──────┘
               └──────────────────┘
```

每个块在跳回调度器之前设置 `state = next_state`。

### 3.2 恢复技术

| 技术 | 工具 | 效果 |
|---|---|---|
| 符号执行 | angr, Triton, miasm | 高 — 跟踪所有状态转换 |
| 基于跟踪的恢复 | Pin/DynamoRIO 跟踪 → 重建 CFG | 中等 — 仅覆盖执行路径 |
| 模式匹配 | 自定义 IDA/Ghidra 脚本 | 中等 — 适用于已知扁平化器 |
| D-810 (IDA 插件) | IDA Pro | 高 — 专门为 CFF 设计 |

### 3.3 符号反扁平化（angr 方法）

```python
import angr, claripy

proj = angr.Project('./obfuscated')
cfg = proj.analyses.CFGFast()

# 找到调度器块（入度最高的基本块）
dispatcher = max(cfg.graph.nodes(), key=lambda n: cfg.graph.in_degree(n))

# 对于每个 case 块，符号化确定后继
for block in case_blocks:
    state = proj.factory.blank_state(addr=block.addr)
    # ... 解决状态变量以找到真实后继
```

---

## 4. MOVFUSCATOR

### 4.1 概念

所有计算都简化为仅 `mov` 指令（通过内存映射计算表实现图灵完备）。由 Christopher Domas 创建。

### 4.2 识别

- 函数仅包含 `mov` 指令（没有 add, sub, xor, jmp, call）
- 数据段中有大型查找表
- 内存映射标志寄存器

### 4.3 反 movfuscator

| 方法 | 描述 |
|---|---|
| demovfuscator (工具) | 静态分析，从 mov 模式恢复原始操作 |
| 跟踪 + 污点分析 | 使用 Pin/DynamoRIO 运行，污点输入，观察计算 |
| 符号执行 | 将整个函数视为约束系统 |

---

## 5. 虚拟机保护（VMProtect / Themida / Code Virtualizer）

### 5.1 虚拟机架构

```
受保护的代码 → 字节码编译器 → 自定义字节码
运行时: 虚拟机入口（pushad/pushfd）→ 获取 → 解码 → 执行 → 虚拟机退出（popad/popfd）
```

### 5.2 虚拟机入口点识别

```asm
; 典型的 VMProtect 入口
pushad                    ; 保存所有寄存器
pushfd                    ; 保存标志
mov ebp, esp              ; 虚拟机栈帧
sub esp, VM_LOCALS_SIZE   ; 分配虚拟机上下文
mov esi, bytecode_addr    ; 字节码指令指针
jmp vm_dispatcher         ; 进入虚拟机循环
```

### 5.3 处理器表提取

```
1. 找到调度器（大型 switch 或通过表进行间接跳转）
2. 每个 case/入口 = 一个虚拟机处理器（实现一个虚拟机指令）
3. 通过分析每个处理器映射处理器地址到操作：
   - 处理器从字节码流（esi）读取操作数
   - 对虚拟机寄存器/栈执行操作
   - 前进字节码指针
   - 返回调度器
```

### 5.4 反虚拟化方法

| 方法 | 描述 | 工具 |
|---|---|---|
| 手动处理器映射 | 逆向每个处理器，构建 ISA 规范 | IDA + 脚本 |
| 跟踪记录 | 记录所有处理器执行，重建程序 | REVEN, Pin |
| 符号提升 | 符号化执行处理器，提升到 IR | Triton, miasm |
| 模式匹配 | 匹配处理器模式到已知虚拟机系列 | 自定义脚本 |

### 5.5 VMProtect 特定内容

- 在调度器中使用不透明谓词
- 处理器变异：相同指令，不同构建的处理器代码
- 多层 VM（VM 内嵌 VM）
- 集成反调试和完整性检查

---

## 6. 字符串加密

### 6.1 常见模式

| 模式 | 示例 | 恢复 |
|---|---|---|
| XOR 循环 | `for (i=0; i<len; i++) s[i] ^= key;` | 钩子或模拟 XOR 函数 |
| 栈字符串 | `mov [esp+0], 'H'; mov [esp+1], 'e'; ...` | IDA FLIRT / Ghidra 脚本重新组装 |
| RC4 加密 | 加密块 + RC4 密钥在二进制中 | 提取密钥，离线解密 |
| AES 加密 | 加密块 + 运行时派生的 AES 密钥 | 解密后钩子 |
| 自定义编码 | Base64 + XOR + 反转 | 跟踪解码函数，复制 |

### 6.2 自动字符串解密

```python
# Ghidra 脚本：查找 XOR 解密调用，模拟它们
from ghidra.program.model.symbol import SourceType

decrypt_func = getFunction("decrypt_string")
refs = getReferencesTo(decrypt_func.getEntryPoint())

for ref in refs:
    call_addr = ref.getFromAddress()
    # 提取参数（加密缓冲区指针、密钥、长度）
    # 模拟解密，添加注释显示明文
```

---

## 7. 导入隐藏

### 7.1 GetProcAddress + 哈希查找

```c
FARPROC resolve(DWORD hash) {
    // 遍历 PEB → LDR → InMemoryOrderModuleList
    // 对于每个 DLL，遍历导出表
    // 哈希每个导出名称，与目标哈希比较
    // 返回匹配的函数指针
}
```

### 7.2 恢复

1. 识别哈希算法（常见：CRC32, djb2, ROR13+ADD）
2. 计算所有已知 API 名称的哈希
3. 构建哈希 → API 名称查找表
4. 在 IDA/Ghidra 中注释解析的调用

### 7.3 常见哈希算法

| 名称 | 算法 | 使用者 |
|---|---|---|
| ROR13 | `hash = (hash >> 13 \| hash << 19) + char` | Metasploit shellcode |
| djb2 | `hash = hash * 33 + char` | 各种恶意软件 |
| CRC32 | 函数名称的标准 CRC32 | 复杂加壳器 |
| FNV-1a | `hash = (hash ^ char) * 0x01000193` | 现代恶意软件 |

---

## 8. 反反汇编技巧

### 8.1 技巧

| 技巧 | 机制 | 修复 |
|---|---|---|
| 重叠指令 | `jmp $+2; db 0xE8`（假调用前缀） | 从正确偏移手动重新分析 |
| 未对齐跳转 | 跳转到多字节指令的中间 | 强制 IDA 在目标处重新分析 |
| 条件跳转对 | `jz $+5; jnz $+3`（始终跳转，混淆线性反汇编） | 转换为无条件跳转 |
| 返回地址操作 | `push addr; ret` 而不是 `jmp addr` | 识别 push+ret 作为跳转 |
| 基于异常的流程 | 触发异常，真实代码在处理器中 | 分析异常处理器链 |
| 调用 + add [esp] | `call $+5; add [esp], N; ret`（计算跳转） | 计算实际目标 |

### 8.2 IDA 修复

```
右键单击 → Undefine (U)
右键单击 → 代码 (C) 在正确偏移处
编辑 → 补丁 → 汇编（永久修复）
```

---

## 9. 决策树

```
混淆的二进制文件 — 如何处理？
│
├─ 你能运行它吗？
│  ├─ 是 → 动态分析优先
│  │  ├─ 在有趣 API 上设置断点（文件、网络、加密）
│  │  ├─ 跟踪执行以了解真实行为
│  │  └─ 在运行时转储解密代码/字符串
│  │
│  └─ 否（嵌入式/固件/异构架构）→ 仅静态
│     └─ 从以下模式识别混淆类型
│
├─ 代码看起来像什么？
│  │
│  ├─ 巨大的平坦 switch/调度器循环？
│  │  ├─ 状态变量驱动控制流 → CFF
│  │  │  └─ 使用 D-810 或符号化反扁平化
│  │  └─ 字节码获取-解码-执行 → 虚拟机保护
│  │     └─ 提取处理器，构建反汇编器
│  │
│  ├─ 仅 mov 指令？
│  │  └─ movfuscator → demovfuscator 工具
│  │
│  ├─ XOR/ADD 循环写入 .text 区域？
│  │  └─ SMC → 断点后解码，转储
│  │
│  ├─ 分支中存在不可能的条件？
│  │  └─ 不透明谓词 → Z3 证明或模式删除
│  │
│  ├─ 反汇编看起来不对 / 函数重叠？
│  │  └─ 反反汇编 → 在正确偏移手动重新分析
│  │
│  ├─ 没有可读字符串？
│  │  └─ 字符串加密 → 钩子解密函数或模拟
│  │
│  ├─ IAT 中没有导入？
│  │  └─ 导入隐藏 → 识别哈希，构建查找表
│  │
│  └─ pushad/pushfd → 复杂代码 → popad/popfd？
│     └─ 虚拟机保护程序入口/退出 → 完整 VM 分析
│
└─ 使用什么工具？
   ├─ 已知保护程序（VMProtect/Themida）→ 具体脱保护指南
   ├─ 自定义混淆 → 组合：IDA 脚本 + Triton + 手动
   ├─ CTF 挑战 → angr 符号执行通常最快
   └─ 恶意软件分析 → 动态（调试器 + API 监控）优先
```

---

## 10. 工具箱

| 工具 | 目的 | 适用于 |
|---|---|---|
| IDA Pro + Hex-Rays | 反汇编、反编译、脚本 | 全面分析 |
| Ghidra | 免费替代方案，具有脚本（Java/Python） | 预算有限的重现 |
| D-810 (IDA 插件) | 自动 CFF 反扁平化 | OLLVM 风格的混淆 |
| miasm | 基于 IR 的分析框架 | 符号反混淆 |
| Triton | 动态符号执行 | 不透明谓词求解，CFF |
| REVEN | 全系统跟踪记录和回放 | 虚拟机保护程序分析 |
| demovfuscator | movfuscator 反转 | mov 仅二进制 |
| x64dbg + 插件 | 带脚本脚本进行动态分析 | Windows 重现 |
| Unicorn Engine | CPU 模拟 | SMC 解包，shellcode |
| Capstone | 反汇编库 | 自定义工具 |
| IDA FLIRT | 函数签名匹配 | 识别剥离二进制中的库代码 |
| Binary Ninja | 另一种反汇编器，具有 MLIL/HLIL | 自动化分析 |
