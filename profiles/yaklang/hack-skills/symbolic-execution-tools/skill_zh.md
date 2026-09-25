# 技能：符号执行工具——专家分析操作手册

> **AI 加载指令**：使用 angr、Z3 和 Unicorn Engine 的专家符号执行技术。涵盖 CTF 挑战自动化、约束求解模式、函数钩子、SimProcedure 替换和基于仿真的解包。基础模型由于状态初始化错误或缺少 libc 函数的钩子，通常会产生损坏的 angr 脚本。

## 0. 相关路由

- [反调试技术](../anti-debugging-techniques/SKILL.md) 当需要符号绕过反调试检查时
- [代码混淆与反混淆](../code-obfuscation-deobfuscation/SKILL.md) 当使用符号执行进行反混淆时
- [虚拟机与字节码逆向](../vm-and-bytecode-reverse/SKILL.md) 当将 angr 应用于自定义虚拟机挑战时

### 高级参考

当您需要时，也加载 [ANGR_COOKBOOK.md](./ANGR_COOKBOOK.md)：
- 15+ 常用 CTF 挑战现成 angr 脚本模式
- scanf、printf、malloc、strcmp 的钩子模板
- 符号文件输入、stdin、argv 模式
- 路径爆炸管理优化技巧

### 何时使用哪个工具

| 场景 | 最佳工具 | 原因 |
|---|---|---|
| 纯数学 / 方程系统 | Z3 | 直接约束求解，无需二进制文件 |
| 具有控制流的二进制文件 | angr | 探索路径，自动管理约束 |
| 仿真的特定代码区域 | Unicorn | 快速，无符号开销，适合解包 |
| 复杂二进制文件 + 自定义虚拟机 | angr + Unicorn（组合） | angr 用于控制流，Unicorn 用于虚拟机处理 |
| 内核 / 固件代码 | Qiling | 具有操作系统感知的完整系统仿真 |

---

## 1. ANGR — 核心概念

### 1.1 管道

```
Project(binary)
  → Factory.entry_state() / blank_state(addr=)
    → SimulationManager(state)
      → explore(find=target, avoid=bad)
        → found[0].solver.eval(symbolic_var)
```

### 1.2 基本设置

```python
import angr
import claripy

proj = angr.Project('./challenge', auto_load_libs=False)

# 入口状态：从程序入口点开始
state = proj.factory.entry_state()

# 空状态：从任意地址开始
state = proj.factory.blank_state(addr=0x401000)

# 完整初始化状态：带有命令行参数
state = proj.factory.full_init_state(args=['./challenge', arg1_sym])

simgr = proj.factory.simulation_manager(state)
simgr.explore(find=0x401234, avoid=[0x401300])

if simgr.found:
    found = simgr.found[0]
    solution = found.solver.eval(symbolic_input, cast_to=bytes)
    print(f"Solution: {solution}")
```

### 1.3 符号变量（claripy）

```python
# 位向量（固定大小整数）
sym_input = claripy.BVS("input", 64)        # 64位符号
sym_byte = claripy.BVS("byte", 8)           # 8位符号
sym_buf = claripy.BVS("buffer", 8 * 32)     # 32字节的缓冲区

# 具体位向量
concrete = claripy.BVV(0x41, 8)             # 具体值 0x41

# 约束
state.solver.add(sym_input > 0)
state.solver.add(sym_input < 100)
state.solver.add(sym_byte >= 0x20)           # 可打印的 ASCII
state.solver.add(sym_byte <= 0x7e)

# 评估
value = state.solver.eval(sym_input)
all_values = state.solver.eval_upto(sym_input, 10)  # 最多 10 个解
```

### 1.4 符号 stdin

```python
flag_len = 32
sym_stdin = claripy.BVS("stdin", 8 * flag_len)

state = proj.factory.entry_state(stdin=sym_stdin)

# 限制为可打印的 ASCII
for i in range(flag_len):
    byte = sym_stdin.get_byte(i)
    state.solver.add(byte >= 0x20)
    state.solver.add(byte <= 0x7e)
```

### 1.5 钩子函数

```python
# 通过地址钩子（跳过原始代码的 N 个字节）
@proj.hook(0x401100, length=5)
def skip_check(state):
    state.regs.eax = 1  # 强制成功

# SimProcedure：替换库函数
class MyStrcmp(angr.SimProcedure):
    def run(self, s1, s2):
        return claripy.If(
            self.state.memory.load(s1, 32) == self.state.memory.load(s2, 32),
            claripy.BVV(0, 32),
            claripy.BVV(1, 32)
        )

proj.hook_symbol('strcmp', MyStrcmp())

# 钩子常见问题函数
proj.hook_symbol('printf', angr.SIM_PROCEDURES['libc']['printf']())
proj.hook_symbol('scanf', angr.SIM_PROCEDURES['libc']['scanf']())
proj.hook_symbol('puts', angr.SIM_PROCEDURES['libc']['puts']())
```

### 1.6 内存操作

```python
# 读取内存（符号感知）
data = state.memory.load(addr, size)          # 返回 BV
data_concrete = state.solver.eval(data, cast_to=bytes)

# 写入内存
state.memory.store(addr, claripy.BVV(0x41, 8))
state.memory.store(addr, sym_buf)

# 读取/写入寄存器
rax = state.regs.rax
state.regs.rdi = claripy.BVV(0x1000, 64)
```

---

## 2. Z3 约束求解

### 2.1 核心 API

```python
from z3 import *

# 类型
x = BitVec('x', 32)    # 32位位向量
y = Int('y')             # 任意精度整数
b = Bool('b')            # 布尔值

# 求解器
s = Solver()
s.add(x + y == 42)
s.add(x > 0)
s.add(y > 0)

if s.check() == sat:
    m = s.model()
    print(f"x = {m[x]}, y = {m[y]}")
```

### 2.2 常见 CTF 模式

```python
# 序列密钥验证：每个字符满足约束
key = [BitVec(f'k{i}', 8) for i in range(16)]
s = Solver()
for k in key:
    s.add(k >= 0x30, k <= 0x7a)  # 字母数字

# XOR 密钥恢复
plaintext = b"known_plaintext"
ciphertext = b"\x12\x34..."
key_byte = BitVec('key', 8)
s = Solver()
for p, c in zip(plaintext, ciphertext):
    s.add(p ^ key_byte == c)

# 线性方程组（模运算）
a, b, c = BitVecs('a b c', 32)
s = Solver()
s.add(3*a + 5*b + 7*c == 0x12345678)
s.add(2*a + 4*b + 6*c == 0xDEADBEEF)
s.add(a ^ b ^ c == 0xCAFEBABE)
```

### 2.3 优化

```python
from z3 import Optimize

opt = Optimize()
x = BitVec('x', 32)
opt.add(x > 0)
opt.add(x < 1000)
opt.minimize(x)  # 找到满足的最小值
opt.check()
print(opt.model())
```

---

## 3. UNICORN ENGINE — 代码仿真

### 3.1 基本设置

```python
from unicorn import *
from unicorn.x86_const import *
from capstone import Cs, CS_ARCH_X86, CS_MODE_64

mu = Uc(UC_ARCH_X86, UC_MODE_64)

CODE_ADDR = 0x400000
STACK_ADDR = 0x7fff0000
STACK_SIZE = 0x10000

mu.mem_map(CODE_ADDR, 0x10000)
mu.mem_map(STACK_ADDR, STACK_SIZE)

mu.mem_write(CODE_ADDR, code_bytes)
mu.reg_write(UC_X86_REG_RSP, STACK_ADDR + STACK_SIZE - 0x1000)
mu.reg_write(UC_X86_REG_RBP, STACK_ADDR + STACK_SIZE - 0x1000)

mu.emu_start(CODE_ADDR, CODE_ADDR + len(code_bytes))

result = mu.reg_read(UC_X86_REG_RAX)
```

### 3.2 钩子内存和指令

```python
# 钩子内存访问
def hook_mem(uc, access, address, size, value, user_data):
    if access == UC_MEM_WRITE:
        print(f"写入 {value:#x} 到 {address:#x}")
    elif access == UC_MEM_READ:
        print(f"从 {address:#x} 读取")

mu.hook_add(UC_HOOK_MEM_READ | UC_HOOK_MEM_WRITE, hook_mem)

# 钩子特定指令（用于跟踪）
def hook_code(uc, address, size, user_data):
    code = uc.mem_read(address, size)
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    for insn in md.disasm(bytes(code), address):
        print(f"  {insn.address:#x}: {insn.mnemonic} {insn.op_str}")

mu.hook_add(UC_HOOK_CODE, hook_code)
```

### 3.3 用例

| 用例 | 方法 |
|---|---|
| 解包 shellcode | 映射 shellcode，仿真，转储解码后的有效载荷 |
| 解密字符串 | 仿真解密函数，使用受控输入 |
| 暴力破解短密钥 | 循环仿真，使用不同密钥输入 |
| 分析混淆函数 | 仿真函数，观察寄存器/内存状态 |
| 固件代码仿真 | 映射固件内存布局，仿真例程 |

---

## 4. ANGR 探索策略

### 4.1 find/avoid

```python
simgr.explore(
    find=lambda s: b"Correct" in s.posix.dumps(1),   # stdout 包含 "Correct"
    avoid=lambda s: b"Wrong" in s.posix.dumps(1)      # 避免 "Wrong" 输出
)
```

### 4.2 管理路径爆炸

| 策略 | 实现 |
|---|---|
| 限制输入空间 | 添加约束（可打印的，长度限制） |
| 避免 死端路径 | 使用 `avoid=` 对于已知失败地址 |
| 钩子复杂函数 | 替换为简化的 SimProcedure |
| 限制循环迭代 | `state.options.add(angr.options.LAZY_SOLVES)` |
| 使用 veritesting | `simgr.explore(..., technique=angr.exploration_techniques.Veritesting())` |
| DFS 而不是 BFS | `simgr.use_technique(angr.exploration_techniques.DFS())` |
| 每条路径超时 | `simgr.explore(..., num_find=1)` + 超时包装 |

### 4.3 具体与符号混合

```python
state = proj.factory.entry_state(
    add_options={angr.options.UNICORN}  # 使用 Unicorn 处理具体区域
)
```

这会显著加快执行速度：具体代码通过 Unicorn 本地运行，仅在涉及符号变量时切换到符号执行。

---

## 5. 实际工作流程

### 5.1 CTF 二进制文件解决工作流程

```
1. 静态分析：识别输入方法，成功/失败条件
   └─ 查找 "Correct" / "Wrong" 字符串 → 获取它们的 xref 地址

2. 选择工具：
   ├─ 纯数学（无需二进制文件）→ Z3
   ├─ 小型二进制文件，清晰的成功/失败 → angr explore
   └─ 需要仿真的特定函数 → Unicorn

3. 设置符号输入：
   ├─ stdin → claripy.BVS + entry_state(stdin=)
   ├─ argv → full_init_state(args=[...])
   ├─ 文件输入 → SimFile
   └─ 特定内存 → state.memory.store(addr, sym)

4. 钩子问题函数：
   ├─ printf/puts → SimProcedure 或 no-op
   ├─ scanf → 自定义处理程序
   ├─ time/random → 返回具体值
   └─ 反调试 → 完全跳过

5. 探索和提取：
   └─ simgr.explore(find=, avoid=) → solver.eval()
```

---

## 6. 决策树

```
需要解决一个逆向挑战吗？
│
├─ 挑战是纯数学/方程吗？
│  └─ 是 → Z3
│     ├─ 线性方程 → BitVec + Solver
│     ├─ 模运算 → BitVec（自然模 2^n）
│     ├─ 布尔逻辑 → Bool + Solver
│     └─ 优化 → Optimize + minimize/maximize
│
├─ 它是一个具有清晰成功/失败的编译二进制文件吗？
│  └─ 是 → angr
│     ├─ 通过 stdin 输入 → 符号 stdin
│     ├─ 通过 argv 输入 → full_init_state 带有符号参数
│     ├─ 通过文件输入 → SimFile
│     ├─ 路径爆炸 → 添加约束，避免路径，钩子循环
│     └─ 复杂库调用 → 钩子 SimProcedure
│
├─ 需要仿真特定函数/区域吗？
│  └─ 是 → Unicorn Engine
│     ├─ 解密例程 → 映射代码 + 数据，仿真，读取结果
│     ├─ shellcode 分析 → 映射 shellcode，钩子系统调用
│     └─ 密钥调度 → 使用不同输入仿真
│
├─ 需要分析固件 / 特殊架构吗？
│  └─ 是 → Qiling（具有操作系统支持的完整系统仿真）
│
├─ 二进制文件有 VM 保护吗？
│  └─ angr 用于处理程序分析 + Z3 用于字节码约束
│
└─ 以上都不适用？
   ├─ 组合：Unicorn 处理具体区域 + Z3 处理约束
   ├─ 使用调试器进行手动逆向工程
   └─ 侧信道方法（时间，硬件的功耗分析）
```

---

## 7. 常见陷阱和修复

| 问题 | 原因 | 修复 |
|---|---|---|
| angr 永远挂起 | 循环中的路径爆炸 | 添加 `avoid=` 对于循环回边，或钩子循环 |
| Z3 返回 `unknown` | 非线性约束过于复杂 | 简化，拆分为子问题，使用 `set_param("timeout", 5000)` |
| Unicorn 在系统调用时崩溃 | 未处理的系统调用 | 钩子系统调用中断，处理或跳过 |
| angr 返回错误结果 | 状态初始化错误 | 验证初始内存布局与实际二进制文件匹配 |
| 符号内存过大 | 无界符号读取 | 尽可能具体化数组索引 |
| SimProcedure 类型错误 | 参数类型不匹配 | 检查调用约定（cdecl vs fastcall） |
| angr 无法加载二进制文件 | 缺少库 | 使用 `auto_load_libs=False` + 钩子需要的符号 |

---

## 8. 工具版本和安装

```bash
# angr (Python 3.8+)
pip install angr

# Z3
pip install z3-solver

# Unicorn Engine
pip install unicorn

# Capstone（反汇编，与 Unicorn 配对）
pip install capstone

# Keystone（汇编）
pip install keystone-engine
```
