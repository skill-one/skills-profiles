# 技能：虚拟机与字节码逆向工程——专家分析手册

> **AI 加载指令**：逆向工程自定义虚拟机与字节码解释器的高级技术。涵盖调度器识别、操作码映射、自定义指令集架构重建、反汇编器/反编译器编写、迷宫挑战和现实世界虚拟机保护程序分析。基础模型通常无法识别获取-解码-执行模式或尝试将虚拟机字节码作为原生代码进行分析。

## 0. 相关路由

- 当虚拟机是商业保护程序（VMProtect/Themida）时，使用 `[代码混淆与解混淆](../code-obfuscation-deobfuscation/SKILL.md)`
- 当使用 angr 解决基于虚拟机的挑战时，使用 `[符号执行工具](../symbolic-execution-tools/SKILL.md)`
- 当虚拟机包含反调试检查时，使用 `[反调试技术](../anti-debugging-techniques/SKILL.md)`

### 快速识别

| 二进制模式 | 可能的虚拟机类型 | 从何处开始 |
|---|---|---|
| `while(1) { switch(bytecode[pc]) }` | 基于切换的调度器 | 将每个案例映射到操作 |
| 通过表间接跳转 `jmp [table + opcode*8]` | 基于表的调度器 |转储跳转表，分析处理程序 |
| 基于字节值的嵌套 if-else 链 | if 链调度器 | 与切换相同，只是语法不同 |
| 栈推送/弹出主导操作 | 基于栈的虚拟机 | 识别推送、弹出、算术操作 |
| `reg[X] = ...` 数组操作 | 基于寄存器的虚拟机 | 将寄存器索引映射到操作 |
| 2D 网格 + 方向输入 | 迷宫挑战 | 提取网格，应用 BFS/DFS |

---

## 1. 自定义虚拟机识别

### 1.1 结构指示器

```
虚拟机架构组件：
┌─────────────────────────────────┐
│  字节码程序（数据段）            │
├─────────────────────────────────┤
│  程序计数器（pc/ip）            │
│  寄存器文件 / 栈                │
│  内存 / 数据区域                │
├─────────────────────────────────┤
│  调度器循环                    │
│  ├─ 获取：opcode = code[pc]    │
│  ├─ 解码：查找处理程序          │
│  └─ 执行：运行处理程序          │
└─────────────────────────────────┘
```

### 1.2 IDA/Ghidra 签名

**切换调度器**（CTF 中最常见）：
```c
while (running) {
    unsigned char op = bytecode[pc++];
    switch (op) {
        case 0x00: /* nop */       break;
        case 0x01: /* push imm */  stack[sp++] = bytecode[pc++]; break;
        case 0x02: /* add */       stack[sp-2] += stack[sp-1]; sp--; break;
        // ...
        case 0xFF: /* halt */      running = 0; break;
    }
}
```

**表调度器**（更优化）：
```c
typedef void (*handler_t)(vm_ctx_t*);
handler_t handlers[256] = { handle_nop, handle_push, handle_add, ... };

while (running) {
    handlers[bytecode[pc++]](&ctx);
}
```

---

## 2. 分析方法

### 第 1 步：找到调度器

寻找：
- 循环中包含大量案例的大型切换语句
- 通过数据缓冲区中的字节索引的函数指针数组
- 具有高圈复杂度的单个函数
- 逐字节读取数据缓冲区的交叉引用

### 第 2 步：将操作码映射到操作

对于每个案例/处理程序，确定：

| 属性 | 如何识别 |
|---|---|
| 操作码值 | 案例编号或表索引 |
| 操作类型 | 寄存器/栈修改 |
| 操作数数量 | 操作码后消耗多少字节 |
| 操作数类型 | 立即值、寄存器索引或内存地址 |
| 侧效应 | 输出、内存写入、标志修改 |

### 第 3 步：提取字节码程序

```python
# 从二进制中典型提取
import struct

with open('challenge', 'rb') as f:
    f.seek(bytecode_offset)
    bytecode = f.read(bytecode_length)

# 或从 IDA：
# bytecode = idc.get_bytes(bytecode_addr, bytecode_len)
```

### 第 4 步：编写自定义反汇编器

```python
OPCODES = {
    0x00: ("nop",  0),    # (助记符, 操作数字节)
    0x01: ("push", 1),    # 推送立即字节
    0x02: ("pop",  0),
    0x03: ("add",  0),
    0x04: ("sub",  0),
    0x05: ("xor",  0),
    0x06: ("cmp",  0),
    0x07: ("jmp",  2),    # 跳转到 16 位地址
    0x08: ("je",   2),
    0x09: ("jne",  2),
    0x0A: ("mov",  2),    # mov reg, imm
    0x0B: ("load", 1),    # 从内存[操作数]加载
    0x0C: ("store",1),    # 存储到内存[操作数]
    0x0D: ("print",0),
    0x0E: ("read", 0),    # 读取输入
    0xFF: ("halt", 0),
}

def disassemble(bytecode):
    pc = 0
    while pc < len(bytecode):
        op = bytecode[pc]
        if op not in OPCODES:
            print(f"  {pc:04x}: 未知 {op:#04x}")
            pc += 1
            continue

        mnemonic, operand_size = OPCODES[op]
        operands = bytecode[pc+1:pc+1+operand_size]
        operand_str = ' '.join(f'{b:#04x}' for b in operands)
        print(f"  {pc:04x}: {mnemonic:8s} {operand_str}")
        pc += 1 + operand_size

disassemble(bytecode)
```

### 第 5 步：分析反汇编程序

使用自定义反汇编，应用标准逆向工程：
- 识别输入读取（读取操作码）
- 从输入跟踪数据流到比较
- 确定成功/失败条件
- 提取检查逻辑（通常是输入与常数的 XOR/ADD 变换）

---

## 3. CTF 中常见的虚拟机模式

### 3.1 基于栈的虚拟机

操作在栈上工作（类似于 JVM 或 Python 字节码）。

| 操作码 | 操作 | 栈效果 |
|---|---|---|
| PUSH imm | 推送立即值 | [...] → [..., imm] |
| POP | 弃用顶部 | [..., a] → [...] |
| ADD | 顶部两个相加 | [..., a, b] → [..., a+b] |
| SUB | 减去 | [..., a, b] → [..., a-b] |
| MUL | 乘以 | [..., a, b] → [..., a*b] |
| XOR | 按位 XOR | [..., a, b] → [..., a^b] |
| CMP | 比较 | [..., a, b] → [..., (a==b)] |
| JMP addr | 无条件跳转 | 无变化 |
| JZ addr | 如果顶部为零则跳转 | [..., a] → [...] |
| PRINT | 输出顶部作为字符 | [..., a] → [...] |
| READ | 读取字符到栈 | [...] → [..., input] |
| HALT | 停止执行 | - |

### 3.2 基于寄存器的虚拟机

操作使用寄存器索引（类似于 x86、ARM）。

| 操作码 | 格式 | 操作 |
|---|---|---|
| MOV r, imm | `0x01 RR II II` | reg[R] = imm16 |
| MOV r1, r2 | `0x02 R1 R2` | reg[R1] = reg[R2] |
| ADD r1, r2 | `0x03 R1 R2` | reg[R1] += reg[R2] |
| SUB r1, r2 | `0x04 R1 R2` | reg[R1] -= reg[R2] |
| XOR r1, r2 | `0x05 R1 R2` | reg[R1] ^= reg[R2] |
| CMP r1, r2 | `0x06 R1 R2` | flags = compare(r1, r2) |
| JMP addr | `0x07 AA AA` | pc = addr |
| JE addr | `0x08 AA AA` | 如果相等：pc = addr |
| LOAD r, [addr] | `0x09 RR AA` | reg[R] = mem[addr] |
| STORE [addr], r | `0x0A AA RR` | mem[addr] = reg[R] |
| SYSCALL | `0x0B` | 基于 reg[0] 的 I/O 操作 |
| HALT | `0xFF` | 停止 |

### 3.3 类 Brainfuck / 奇异虚拟机

| BF 命令 | 虚拟机等效 | 描述 |
|---|---|---|
| `>` | INC ptr | 向右移动数据指针 |
| `<` | DEC ptr | 向左移动数据指针 |
| `+` | INC [ptr] | 增加指针处的字节 |
| `-` | DEC [ptr] | 减少指针处的字节 |
| `.` | OUTPUT [ptr] | 输出指针处的字节 |
| `,` | INPUT [ptr] | 将字节输入指针 |
| `[` | JZ forward | 如果字节为零，则跳过 `]` |
| `]` | JNZ back | 如果字节非零，则跳回 `[` |

---

## 4. 迷宫挑战

### 4.1 识别

- 二进制读取方向输入（WASD、箭头键、UDLR）
- 数据段中的 2D 数组（墙壁、路径、起点、终点）
- 位置跟踪使用 x,y 坐标
- 在特定坐标处获胜条件

### 4.2 地图提取

```python
# 从二进制数据段提取迷宫网格
MAZE_ADDR = 0x601060
WIDTH = 20
HEIGHT = 15

# 从二进制转储：
maze = []
for row in range(HEIGHT):
    line = ""
    for col in range(WIDTH):
        cell = bytecode[MAZE_ADDR + row * WIDTH + col - base_addr]
        if cell == 0: line += "."    # 路径
        elif cell == 1: line += "#"  # 墙壁
        elif cell == 2: line += "S"  # 起点
        elif cell == 3: line += "E"  # 终点
        else: line += "?"
    maze.append(line)
    print(line)
```

### 4.3 自动化解决

```python
from collections import deque

def solve_maze(maze, start, end):
    """BFS 解决器返回方向字符串。"""
    rows, cols = len(maze), len(maze[0])
    directions = {'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1)}
    queue = deque([(start, "")])
    visited = {start}

    while queue:
        (r, c), path = queue.popleft()
        if (r, c) == end:
            return path

        for name, (dr, dc) in directions.items():
            nr, nc = r + dr, c + dc
            if (0 <= nr < rows and 0 <= nc < cols and
                maze[nr][nc] != '#' and (nr, nc) not in visited):
                visited.add((nr, nc))
                queue.append(((nr, nc), path + name))

    return None

# 找到起点和终点位置
for r, row in enumerate(maze):
    for c, cell in enumerate(row):
        if cell == 'S': start = (r, c)
        if cell == 'E': end = (r, c)

solution = solve_maze(maze, start, end)
print(f"路径: {solution}")
```

### 4.4 方向编码

不同的挑战以不同的方式编码方向：

| 编码 | 上 | 下 | 左 | 右 |
|---|---|---|---|---|
| WASD | W | S | A | D |
| UDLR | U | D | L | R |
| 箭头键 | ↑ (0x48) | ↓ (0x50) | ← (0x4B) | → (0x4D) |
| 数字 | 1 | 2 | 3 | 4 |
| 十六进制操作码 | 0x01 | 0x02 | 0x03 | 0x04 |

---

## 5. 现实世界虚拟机保护程序

### 5.1 VMProtect 分析方法

```
1. 找到 VM 入口：搜索 pushad/pushfd 序列
2. 识别 VM 上下文结构（寄存器、标志、字节码指针）
3. 定位处理程序表（通常使用不透明的谓词混淆）
4. 对于每个处理程序：
   a. 删除垃圾代码 / 不透明谓词
   b. 识别核心操作
   c. 记录处理程序语义
5. 跟踪字节码执行（指令级跟踪）
6. 从跟踪中重建原始代码
```

### 5.2 Tigress 混淆器

具有可配置保护层的学术 VM 混淆器。

| 功能 | 方法 |
|---|---|
| 单调度器 VM | 标准处理程序提取 |
| 分割处理程序 | 处理程序分布在多个函数中 |
| 嵌套 VM | 外部 VM 处理程序调用内部 VM |
| 加密字节码 | 在每次获取前动态解密 |
| 多态处理程序 | 每次构建对同一操作具有不同代码 |

### 5.3 常见 VM 保护程序模式

| 保护程序 | 调度器风格 | 难度 |
|---|---|---|
| VMProtect | 表 + 不透明谓词 | 高 |
| Themida (Code Virtualizer) | 类 CISC，大型处理程序集 | 高 |
| Tigress | 可配置，学术 | 中高 |
| 自定义 CTF VM | 简单切换 | 低中 |
| Movfuscator | 所有 mov 计算 | 中 |

---

## 6. 工具

| 工具 | 目的 | 使用 |
|---|---|---|
| IDA Pro | 识别调度器，逆向处理程序 | F5 反编译，xref 分析 |
| Ghidra | 免费替代方案，具有 Sleigh 处理器模块 | 编写自定义处理器用于 VM ISA |
| angr | 通过 VM 进行符号执行 | 将整个 VM 视为约束系统 |
| Pin / DynamoRIO | 动态仪器用于跟踪 | 记录操作码处理程序执行序列 |
| REVEN | 全系统跟踪记录 | 回放并分析 VM 执行 |
| Unicorn | 模拟 VM 执行 | 快速处理程序模拟 |
| Miasm | 基于中间表示的分析 | 将 VM 处理程序提升到 IR 进行分析 |
| 自定义 Python | 编写反汇编器/反编译器 | 每个挑战自定义工具 |

### Ghidra Sleigh 处理器模块

对于常见的 VM 架构，编写 Sleigh 处理器规范：

```
define space ram      type=ram_space      size=2  default;
define space register type=register_space  size=1;

define register offset=0 size=1 [ R0 R1 R2 R3 FLAGS PC SP ];

define token opcode(8)
    op = (0,7)
;

:NOP    is op=0x00 { }
:PUSH   imm is op=0x01; imm { SP = SP - 1; *[ram]:1 SP = imm; }
:POP    is op=0x02 { SP = SP + 1; }
:ADD    is op=0x03 { local a = *[ram]:1 (SP+1); *[ram]:1 (SP+1) = a + *[ram]:1 SP; SP = SP + 1; }
```

---

## 7. 决策树

```
二进制包含自定义字节码解释器？
│
├─ 能否识别调度器？
│  ├─ 是（切换/表/if-chain）
│  │  ├─ 案例较少（< 20）→ 简单 CTF VM
│  │  │  ├─ 基于栈 → 映射推送/弹出/算术操作
│  │  │  ├─ 基于寄存器 → 映射 mov/add/cmp 操作
│  │  │  └─ 编写反汇编器 → 分析程序 → 解决
│  │  │
│  │  └─ 案例较多（50+）→ 商业保护程序
│  │     ├─ 已知保护程序 → 使用特定脱保护工具
│  │     └─ 自定义 → 跟踪执行，模式匹配处理程序
│  │
│  └─ 没有明确的调度器
│     ├─ 所有 mov 指令 → movfuscator
│     ├─ 加密字节码 → 找到解密，解码后转储
│     └─ 分割/分布式处理程序 → 跟踪执行以找到它们
│
├─ 它是一个迷宫挑战吗？
│  ├─ 从数据段提取网格
│  ├─ 识别方向编码
│  ├─ BFS/DFS 找到最短路径
│  └─ 将路径转换为预期输入格式
│
├─ VM 中是否有输入验证？
│  ├─ 输入空间较小 → 通过 Unicorn 模拟进行暴力破解
│  ├─ 已知格式 → 使用 angr 进行约束解决
│  └─ 复杂检查 → 编写反汇编器，分析检查逻辑
│
└─ 是否存在多层 VM（VM 中的 VM）？
   ├─ 首先分析外部 VM
   ├─ 提取内部字节码
   ├─ 重复分析内部 VM
   └─ 考虑：符号执行可能直接处理嵌套 VM
```

---

## 8. CTF 解决工作流程

```
1. 运行二进制程序 — 理解 I/O 行为
   └─ 它期望什么输入？成功/失败时的输出是什么？

2. 在 IDA/Ghidra 中打开 — 找到主循环
   └─ 寻找包含切换或间接跳转的 while/for 循环

3. 识别 VM 组件：
   ├─ 字节码位置（程序数据在哪里？）
   ├─ PC/IP 变量（如何跟踪当前位置？）
   ├─ 寄存器/栈（VM 状态存储在哪里？）
   └─ I/O 处理程序（哪些操作码读取输入 / 写入输出？）

4. 映射所有操作码（创建 ISA 规范）
   └─ 对于每个案例/处理程序：操作码编号、操作、操作数

5. 在 Python 中编写反汇编器
   └─ 输出字节码的可读汇编

6. 分析反汇编程序：
   ├─ 找到输入读取
   ├─ 跟踪应用于输入的转换
   ├─ 找到与预期值的比较
   └─ 反转转换以找到有效输入

7. 解决：
   ├─ 如果简单转换（XOR、ADD）→ 手动反转
   ├─ 如果复杂 → 作为约束传递给 Z3
   └─ 如果迷宫 → 提取网格，运行路径查找
```
