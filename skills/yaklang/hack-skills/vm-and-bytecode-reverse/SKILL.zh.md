---
name: vm-and-bytecode-reverse
description: 自定义虚拟机与字节码逆向工程手册。在CTF挑战或受保护软件中实现自定义虚拟机、专有字节码、调度器循环或迷宫式挑战时使用。
---

# 技能：虚拟机与字节码逆向工程 — 专家分析手册

> **AI 加载指令**：逆向自定义虚拟机和字节码解释器的专家级技术。涵盖分发器识别、操作码映射、自定义指令集架构 (ISA) 重建、反汇编器/反编译器编写、迷宫挑战以及真实世界虚拟机保护器分析。基础模型通常无法识别“取指-解码-执行”模式，或者尝试将虚拟机字节码当作原生代码进行分析。

## 0. 相关路由

- 当虚拟机是商业保护器 (VMProtect/Themida) 时，参考 [code-obfuscation-deobfuscation](../code-obfuscation-deobfuscation/SKILL.md)
- 当使用 angr 解决基于虚拟机的挑战时，参考 [symbolic-execution-tools](../symbolic-execution-tools/SKILL.md)
- 当虚拟机包含反调试检查时，参考 [anti-debugging-techniques](../anti-debugging-techniques/SKILL.md)

### 快速识别

| 二进制模式 | 可能的虚拟机类型 | 起始步骤 |
|---|---|---|
| `while(1) { switch(bytecode[pc]) }` | 基于 switch 的分发器 | 将每个 case 映射到一个操作 |
| 通过表进行间接跳转 `jmp [table + opcode*8]` | 基于表的分发器 | 转储跳转表，分析处理函数 |
| 针对字节值的嵌套 if-else 链 | if 链分发器 | 与 switch 相同，只是语法不同 |
| 堆栈推/弹操作占主导地位 | 基于堆栈的虚拟机 | 识别 push、pop、算术操作 |
| `reg[X] = ...` 数组操作 | 基于寄存器的虚拟机 | 将寄存器索引映射到操作 |
| 2D 网格 + 方向输入 | 迷宫挑战 | 提取网格，应用 BFS/DFS |

---

## 1. 自定义虚拟机识别

### 1.1 结构指示器

```
VM 架构组件：
┌─────────────────────────────────┐
│  字节码程序 (数据段)          │
├─────────────────────────────────┤
│  程序计数器 (pc/ip)           │
│  寄存器文件 / 堆栈            │
│  内存 / 数据区                │
├─────────────────────────────────┤
│  分发器循环                   │
│  ├─ 取指: opcode = code[pc]   │
│  ├─ 解码: 查找处理函数       │
│  └─ 执行: 运行处理函数       │
└─────────────────────────────────┘
```

### 1.2 IDA/Ghidra 特征

**Switch 分发器** (在 CTF 中最常见):
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

**表分发器** (优化程度更高):
```c
typedef void (*handler_t)(vm_ctx_t*);
handler_t handlers[256] = { handle_nop, handle_push, handle_add, ... };

while (running) {
    handlers[bytecode[pc++]](&ctx);
}
```

---

## 2. 分析方法论

### 步骤 1：查找分发器

寻找以下特征：
- 循环中的大型 switch 语句 (包含许多 case)
- 由数据缓冲区中的字节索引的函数指针数组
- 高圈复杂度的单个函数
- 对逐字节读取的数据缓冲区的交叉引用

### 步骤 2：将操作码映射到操作

对于每个 case/处理函数，确定：

| 属性 | 如何识别 |
|---|---|
| 操作码值 | Case 编号或表索引 |
| 操作类型 | 寄存器/堆栈修改 |
| 操作数数量 | 操作码后消耗了多少个字节 |
| 操作数类型 | 立即数、寄存器索引或内存地址 |
| 副作用 | 输出、内存写入、标志修改 |

### 步骤 3：提取字节码程序

```python
# 从二进制文件中的典型提取
import struct

with open('challenge', 'rb') as f:
    f.seek(bytecode_offset)
    bytecode = f.read(bytecode_length)

# 或者从 IDA 中获取：
# bytecode = idc.get_bytes(bytecode_addr, bytecode_len)
```

### 步骤 4：编写自定义反汇编器

```python
OPCODES = {
    0x00: ("nop",  0),    # (助记符, 操作数字节数)
    0x01: ("push", 1),    # 压入立即数字节
    0x02: ("pop",  0),
    0x03: ("add",  0),
    0x04: ("sub",  0),
    0x05: ("xor",  0),
    0x06: ("cmp",  0),
    0x07: ("jmp",  2),    # 跳转到 16 位地址
    0x08: ("je",   2),
    0x09: ("jne",  2),
    0x0A: ("mov",  2),    # mov reg, imm
    0x0B: ("load", 1),    # 从 memory[operand] 加载
    0x0C: ("store",1),    # 存储到 memory[operand]
    0x0D: ("print",0),
    0x0E: ("read", 0),    # 读取输入
    0xFF: ("halt", 0),
}

def disassemble(bytecode):
    pc = 0
    while pc < len(bytecode):
        op = bytecode[pc]
        if op not in OPCODES:
            print(f"  {pc:04x}: UNKNOWN {op:#04x}")
            pc += 1
            continue

        mnemonic, operand_size = OPCODES[op]
        operands = bytecode[pc+1:pc+1+operand_size]
        operand_str = ' '.join(f'{b:#04x}' for b in operands)
        print(f"  {pc:04x}: {mnemonic:8s} {operand_str}")
        pc += 1 + operand_size

disassemble(bytecode)
```

### 步骤 5：分析反汇编后的程序

有了自定义的反汇编结果后，应用标准的逆向工程技术：
- 识别输入读取 (read 操作码)
- 跟踪从输入到比较的数据流
- 确定成功/失败条件
- 提取检查逻辑 (通常是输入的 XOR/ADD 变换与常量进行比较)

---

## 3. CTF 中的常见虚拟机模式

### 3.1 基于堆栈的虚拟机

操作在堆栈上执行 (类似 JVM 或 Python 字节码)。

| 操作码 | 操作 | 堆栈影响 |
|---|---|---|
| PUSH imm | 压入立即数值 | [...] → [..., imm] |
| POP | 丢弃顶部 | [..., a] → [...] |
| ADD | 相加顶部两个 | [..., a, b] → [..., a+b] |
| SUB | 相减 | [..., a, b] → [..., a-b] |
| MUL | 相乘 | [..., a, b] → [..., a*b] |
| XOR | 按位异或 | [..., a, b] → [..., a^b] |
| CMP | 比较 | [..., a, b] → [..., (a==b)] |
| JMP addr | 无条件跳转 | 无变化 |
| JZ addr | 如果顶部为零则跳转 | [..., a] → [...] |
| PRINT | 将顶部输出为字符 | [..., a] → [...] |
| READ | 将字符读入堆栈 | [...] → [..., input] |
| HALT | 停止执行 | - |

### 3.2 基于寄存器的虚拟机

操作使用寄存器索引 (类似 x86, ARM)。

| 操作码 | 格式 | 操作 |
|---|---|---|
| MOV r, imm | `0x01 RR II II` | reg[R] = imm16 |
| MOV r1, r2 | `0x02 R1 R2` | reg[R1] = reg[R2] |
| ADD r1, r2 | `0x03 R1 R2` | reg[R1] += reg[R2] |
| SUB r1, r2 | `0x04 R1 R2` | reg[R1] -= reg[R2] |
| XOR r1, r2 | `0x05 R1 R2` | reg[R1] ^= reg[R2] |
| CMP r1, r2 | `0x06 R1 R2` | flags = compare(r1, r2) |
| JMP addr | `0x07 AA AA` | pc = addr |
| JE addr | `0x08 AA AA` | 如果相等: pc = addr |
| LOAD r, [addr] | `0x09 RR AA` | reg[R] = mem[addr] |
| STORE [addr], r | `0x0A AA RR` | mem[addr] = reg[R] |
| SYSCALL | `0x0B` | 基于 reg[0] 的 I/O 操作 |
| HALT | `0xFF` | 停止 |

### 3.3 类似 Brainfuck / 冷门的虚拟机

| BF 命令 | 虚拟机等效 | 描述 |
|---|---|---|
| `>` | INC ptr | 移动数据指针向右 |
| `<` | DEC ptr | 移动数据指针向左 |
| `+` | INC [ptr] | 增加指针处的字节 |
| `-` | DEC [ptr] | 减少指针处的字节 |
| `.` | OUTPUT [ptr] | 输出指针处的字节 |
| `,` | INPUT [ptr] | 将输入字节存入指针 |
| `[` | JZ forward | 如果字节为零则跳过 `]` |
| `]` | JNZ back | 如果字节非零则跳回 `[` |

---

## 4. 迷宫挑战

### 4.1 识别

- 二进制读取方向输入 (WASD, 箭头键, UDLR)
- 数据段中的 2D 数组 (墙壁, 路径, 起点, 终点)
- 带有 x,y 坐标的位置跟踪
- 在特定坐标处获胜

### 4.2 地图提取

```python
# 从二进制数据段提取迷宫网格
MAZE_ADDR = 0x601060
WIDTH = 20
HEIGHT = 15

# 从二进制转储中：
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

### 4.3 自动化求解

```python
from collections import deque

def solve_maze(maze, start, end):
    """BFS 求解器返回方向字符串。"""
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
print(f"Path: {solution}")
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

## 5. 真实世界虚拟机保护器

### 5.1 VMProtect 分析方法

```
1. 查找虚拟机入口：搜索 pushad/pushfd 序列
2. 识别虚拟机上下文结构 (寄存器, 标志, 字节码指针)
3. 定位处理函数表 (通常用不透明谓词混淆)
4. 对于每个处理函数：
   a. 移除垃圾代码 / 不透明谓词
   b. 识别核心操作
   c. 记录处理函数语义
5. 跟踪字节码执行 (指令级跟踪)
6. 从跟踪中重建原始代码
```

### 5.2 Tigress 混淆器

一种具有可配置保护层层的学术虚拟机混淆器。

| 特性 | 方法 |
|---|---|
| 单分发虚拟机 | 标准处理函数提取 |
| 拆分处理函数 | 处理函数分布在多个函数中 |
| 嵌套虚拟机 | 外部虚拟机处理函数调用内部虚拟机 |
| 加密字节码 | 在每次取指前动态解密 |
| 多态处理函数 | 每次构建中相同操作有不同的代码 |

### 5.3 常见虚拟机保护器模式

| 保护器 | 分发器风格 | 难度 |
|---|---|---|
| VMProtect | 表 + 不透明谓词 | 高 |
| Themida (Code Virtualizer) | 类 CISC, 大型处理函数集 | 高 |
| Tigress | 可配置, 学术性 | 中高 |
| 自定义 CTF 虚拟机 | 简单 switch | 低中 |
| Movfuscator | 全 mov 计算 | 中 |

---

## 6. 工具

| 工具 | 用途 | 用法 |
|---|---|---|
| IDA Pro | 识别分发器, 逆向处理函数 | F5 反编译, 交叉引用分析 |
| Ghidra | 带有 Sleigh 处理器模块的免费替代品 | 为虚拟机 ISA 编写自定义处理器 |
| angr | 通过虚拟机进行符号执行 | 将整个虚拟机视为约束系统 |
| Pin / DynamoRIO | 用于跟踪的动态插桩 | 记录操作码处理函数执行序列 |
| REVEN | 全系统跟踪记录 | 回放和分析虚拟机执行 |
| Unicorn | 模拟虚拟机执行 | 快速模拟处理函数 |
| Miasm | 基于 IR 的分析 | 将虚拟机处理函数提升到 IR 进行分析 |
| 自定义 Python | 编写反汇编器/反编译器 | 针对每个挑战的自定义工具 |

### Ghidra Sleigh 处理器模块

对于重复出现的虚拟机架构，编写 Sleigh 处理器规范：

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
├─ 你能识别分发器吗？
│  ├─ 能 (switch/表/if 链)
│  │  ├─ 少量操作码 (< 20) → 简单的 CTF 虚拟机
│  │  │  ├─ 基于堆栈 → 映射 push/pop/算术操作
│  │  │  ├─ 基于寄存器 → 映射 mov/add/cmp 操作
│  │  │  └─ 编写反汇编器 → 分析程序 → 求解
│  │  │
│  │  └─ 大量操作码 (50+) → 商业保护器
│  │     ├─ 已知保护器 → 使用特定的去保护工具
│  │     └─ 自定义 → 跟踪执行, 模式匹配处理函数
│  │
│  └─ 没有明显的分发器
│     ├─ 全 mov 指令 → movfuscator
│     ├─ 加密字节码 → 找到解密方法, 在解码后转储
│     └─ 拆分/分布式处理函数 → 跟踪执行以找到它们
│
├─ 它是迷宫挑战吗？
│  ├─ 从数据段提取网格
│  ├─ 识别方向编码
│  ├─ BFS/DFS 查找最短路径
│  └─ 将路径转换为预期的输入格式
│
├─ 虚拟机中有输入验证吗？
│  ├─ 小输入空间 → 通过 Unicorn 模拟进行暴力破解
│  ├─ 已知格式 → 使用 angr 进行约束求解
│  └─ 复杂检查 → 编写反汇编器, 分析检查逻辑
│
└─ 多层虚拟机 (虚拟机中的虚拟机)？
   ├─ 先分析外部虚拟机
   ├─ 提取内部字节码
   ├─ 对内部虚拟机重复分析
   └─ 考虑：符号执行可能直接处理嵌套虚拟机
```

---

## 8. CTF 求解工作流

```
1. 运行二进制 — 理解 I/O 行为
   └─ 它期望什么输入？成功/失败时的输出是什么？

2. 在 IDA/Ghidra 中打开 — 找到主循环
   └─ 寻找带有 switch 或间接跳转的 while/for 循环

3. 识别虚拟机组件：
   ├─ 字节码位置 (程序数据在哪里？)
   ├─ PC/IP 变量 (如何跟踪当前位置？)
   ├─ 寄存器/堆栈 (虚拟机状态存储在哪里？)
   └─ I/O 处理函数 (哪些操作码读取输入 / 写入输出？)

4. 映射所有操作码 (创建 ISA 规范)
   └─ 对于每个 case/处理函数：操作码编号, 操作, 操作数

5. 用 Python 编写反汇编器
   └─ 输出字节码的可读汇编

6. 分析反汇编后的程序：
   ├─ 找到输入读取
   ├─ 跟踪应用于输入的变换
   ├─ 找到与预期值的比较
   └─ 反向变换以找到有效输入

7. 求解：
   ├─ 如果是简单变换 (XOR, ADD) → 手动反向
   ├─ 如果复杂 → 作为约束提供给 Z3
   └─ 如果是迷宫 → 提取网格, 运行路径查找
```
