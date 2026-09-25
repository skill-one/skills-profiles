# 二进制分析模式

用于分析编译二进制文件、理解汇编代码和重建程序逻辑的全面模式和技巧。

## 何时使用这项技能

- 反编译未知可执行文件以理解其行为
- 使用 Ghidra / IDA Pro / Binary Ninja 分析恶意软件或混淆的二进制文件
- 识别常见的汇编惯用法（函数前序、开关表、虚表分发）
- 从编译代码中重建高级控制流
- 识别编译器引入的模式（栈保护、PIC 跳转表）

## 详细章节：反汇编基础

最初是此 SKILL.md 中的一个 2047 字节章节。已移动到 `references/details.md` 以适应 Codex 的 8 KB 技能主体限制。

## 控制流模式

### 条件分支

```asm
; if (a == b)
cmp eax, ebx
jne skip_block
; ... if body ...
skip_block:

; if (a < b) - 有符号
cmp eax, ebx
jge skip_block    ; 如果大于或等于则跳转
; ... if body ...
skip_block:

; if (a < b) - 无符号
cmp eax, ebx
jae skip_block    ; 如果大于或等于则跳转
; ... if body ...
skip_block:
```

### 循环模式

```asm
; for (int i = 0; i < n; i++)
xor ecx, ecx           ; i = 0
loop_start:
cmp ecx, [n]           ; i < n
jge loop_end
; ... loop body ...
inc ecx                ; i++
jmp loop_start
loop_end:

; while (condition)
jmp loop_check
loop_body:
; ... body ...
loop_check:
cmp eax, ebx
jl loop_body

; do-while
loop_body:
; ... body ...
cmp eax, ebx
jl loop_body
```

### 开关语句模式

```asm
; 跳转表模式
mov eax, [switch_var]
cmp eax, max_case
ja default_case
jmp [jump_table + eax*8]

; 顺序比较（小开关）
cmp eax, 1
je case_1
cmp eax, 2
je case_2
cmp eax, 3
je case_3
jmp default_case
```

## 数据结构模式

### 数组访问

```asm
; array[i] - 4 字节元素
mov eax, [rbx + rcx*4]        ; rbx=基地址, rcx=索引

; array[i] - 8 字节元素
mov rax, [rbx + rcx*8]

; 多维数组[i][j]
; arr[i][j] = 基地址 + (i * 列数 + j) * 元素大小
imul eax, [cols]
add eax, [j]
mov edx, [rbx + rax*4]
```

### 结构体访问

```c
struct Example {
    int a;      // 偏移 0
    char b;     // 偏移 4
    // 填充  // 偏移 5-7
    long c;     // 偏移 8
    short d;    // 偏移 16
};
```

```asm
; 访问结构体字段
mov rdi, [struct_ptr]
mov eax, [rdi]         ; s->a (偏移 0)
movzx eax, byte [rdi+4] ; s->b (偏移 4)
mov rax, [rdi+8]       ; s->c (偏移 8)
movzx eax, word [rdi+16] ; s->d (偏移 16)
```

### 链表遍历

```asm
; while (node != NULL)
list_loop:
test rdi, rdi          ; node == NULL?
jz list_done
; ... 处理节点 ...
mov rdi, [rdi+8]       ; node = node->next (假设 next 在偏移 8)
jmp list_loop
list_done:
```

## 常见代码模式

### 字符串操作

```asm
; strlen 模式
xor ecx, ecx
strlen_loop:
cmp byte [rdi + rcx], 0
je strlen_done
inc ecx
jmp strlen_loop
strlen_done:
; ecx 包含长度

; strcpy 模式
strcpy_loop:
mov al, [rsi]
mov [rdi], al
test al, al
jz strcpy_done
inc rsi
inc rdi
jmp strcpy_loop
strcpy_done:

; 使用 rep movsb 的 memcpy
mov rdi, dest
mov rsi, src
mov rcx, count
rep movsb
```

### 算术模式

```asm
; 常数乘法
; x * 3
lea eax, [rax + rax*2]

; x * 5
lea eax, [rax + rax*4]

; x * 10
lea eax, [rax + rax*4]  ; x * 5
add eax, eax            ; * 2

; 除以 2 的幂（有符号）
mov eax, [x]
cdq                     ; 符号扩展到 EDX:EAX
and edx, 7              ; 用于除以 8
add eax, edx            ; 负数调整
sar eax, 3              ; 算术右移

; 模 2 的幂
and eax, 7              ; x % 8
```

### 位操作

```asm
; 测试特定位
test eax, 0x80          ; 测试位 7
jnz bit_set

; 设置位
or eax, 0x10            ; 设置位 4

; 清除位
and eax, ~0x10          ; 清除位 4

; 切换位
xor eax, 0x10           ; 切换位 4

; 计算前导零
bsr eax, ecx            ; 位扫描反向
xor eax, 31             ; 转换为前导零

; population count (popcnt)
popcnt eax, ecx         ; 计算设置位
```

## 反编译模式

### 变量恢复

```asm
; 局部变量在 rbp-8
mov qword [rbp-8], rax  ; 存储到局部
mov rax, [rbp-8]        ; 从局部加载

; 栈分配数组
lea rax, [rbp-0x40]     ; 数组从 rbp-0x40 开始
mov [rax], edx          ; array[0] = 值
mov [rax+4], ecx        ; array[1] = 值
```

### 函数签名恢复

```asm
; 通过寄存器使用识别参数
func:
    ; rdi 用作第一个参数（System V）
    mov [rbp-8], rdi    ; 将参数保存到局部
    ; rsi 用作第二个参数
    mov [rbp-16], rsi
    ; 通过 RAX 在末尾识别返回值
    mov rax, [result]
    ret
```

### 类型恢复

```asm
; 1 字节操作暗示 char/bool
movzx eax, byte [rdi]   ; 零扩展字节
movsx eax, byte [rdi]   ; 符号扩展字节

; 2 字节操作暗示 short
movzx eax, word [rdi]
movsx eax, word [rdi]

; 4 字节操作暗示 int/float
mov eax, [rdi]
movss xmm0, [rdi]       ; 浮点数

; 8 字节操作暗示 long/double/指针
mov rax, [rdi]
movsd xmm0, [rdi]       ; 双精度浮点数
```

## Ghidra 分析技巧

### 改进反编译

```java
// 在 Ghidra 脚本中
// 修复函数签名
Function func = getFunctionAt(toAddr(0x401000));
func.setReturnType(IntegerDataType.dataType, SourceType.USER_DEFINED);

// 创建结构类型
StructureDataType struct = new StructureDataType("MyStruct", 0);
struct.add(IntegerDataType.dataType, "field_a", null);
struct.add(PointerDataType.dataType, "next", null);

// 应用到内存
createData(toAddr(0x601000), struct);
```

### 模式匹配脚本

```python
# 查找所有对危险函数的调用
for func in currentProgram.getFunctionManager().getFunctions(True):
    for ref in getReferencesTo(func.getEntryPoint()):
        if func.getName() in ["strcpy", "sprintf", "gets"]:
            print(f"Dangerous call at {ref.getFromAddress()}")
```

## IDA Pro 模式

### IDAPython 分析

```python
import idaapi
import idautils
import idc

# 查找所有函数调用
def find_calls(func_name):
    for func_ea in idautils.Functions():
        for head in idautils.Heads(func_ea, idc.find_func_end(func_ea)):
            if idc.print_insn_mnem(head) == "call":
                target = idc.get_operand_value(head, 0)
                if idc.get_func_name(target) == func_name:
                    print(f"Call to {func_name} at {hex(head)}")

# 基于字符串重命名函数
def auto_rename():
    for s in idautils.Strings():
        for xref in idautils.XrefsTo(s.ea):
            func = idaapi.get_func(xref.frm)
            if func and "sub_" in idc.get_func_name(func.start_ea):
                # 使用字符串作为命名提示
                pass
```

## 最佳实践

### 分析工作流程

1. **初步筛选**：文件类型、架构、导入/导出
2. **字符串分析**：识别有趣字符串、错误消息
3. **函数识别**：入口点、导出、交叉引用
4. **控制流映射**：理解程序结构
5. **数据结构恢复**：识别结构体、数组、全局变量
6. **算法识别**：加密、哈希、压缩
7. **文档**：注释、重命名符号、类型定义

### 常见陷阱

- **优化器伪影**：代码可能与源结构不匹配
- **内联函数**：函数可能被内联展开
- **尾调用优化**：`jmp` 而不是 `call` + `ret`
- **死代码**：优化导致不可达的代码
- **位置无关代码**：RIP 相对寻址
