# rev-struct - 结构恢复

通过分析函数及其调用链中的内存访问模式来恢复数据结构定义。

## 预检查

**确定可用的 IDA 访问方法：**

**选项 A — IDA Pro MCP（如果连接则优先选择）：**
检查 IDA Pro MCP 服务器是否已连接（查找活跃的 `ida-pro` 或等效 MCP 连接）。如果已连接，您可以通过 MCP 工具直接查询 IDA，无需导出文件。使用 MCP 进行分析。

**选项 B — IDA-NO-MCP 导出数据：**
如果 MCP 未连接，检查当前目录中是否存在 IDA-NO-MCP 导出数据：

1. 检查是否存在 `decompile/` 目录
2. 检查该目录内是否有 `.c` 文件

如果 MCP 和导出数据都不可用，提示用户：
```
未检测到 IDA 访问方法。请选择以下选项之一：

选项 A — IDA Pro MCP（推荐）：
  连接 IDA Pro MCP 服务器，以便 Claude 可以直接查询 IDA。

选项 B — IDA-NO-MCP 导出：
  1. 下载插件：https://github.com/P4nda0s/IDA-NO-MCP
  2. 将 INP.py 复制到 IDA 插件目录
  3. 在 IDA 中按 Ctrl-Shift-E 导出
  4. 使用 Claude Code 打开导出目录
```

---

## 导出目录结构

```
./
├── decompile/              # 反编译的 C 代码目录
│   ├── 0x401000.c          # 每个函数一个文件，以十六进制地址命名
│   ├── 0x401234.c
│   └── ...
├── decompile_failed.txt    # 失败的反编译列表
├── decompile_skipped.txt   # 跳过的函数列表
├── strings.txt             # 字符串表（地址，长度，类型，内容）
├── imports.txt             # 导入表（地址:函数名）
├── exports.txt             # 导出表（地址:函数名）
└── memory/                 # 内存十六进制转储（1MB 块）
```

## 函数文件格式 (decompile/*.c)

每个 `.c` 文件包含函数元数据注释和反编译代码：

```c
/*
 * func-name: sub_401000
 * func-address: 0x401000
 * callers: 0x402000, 0x403000    // 调用此函数的函数列表
 * callees: 0x404000, 0x405000    // 被此函数调用的函数列表
 */

int __fastcall sub_401000(int a1, int a2)
{
    // 反编译代码...
}
```

---

## 结构恢复步骤

### 第 1 步：读取目标函数

1. 根据用户提供的地址，读取 `decompile/<address>.c`
2. 解析函数元数据，提取调用者和被调用者列表
3. 识别函数中的指针参数（潜在的结构指针）

### 第 2 步：收集内存访问模式

在目标函数中搜索以下模式：

**直接偏移量访问：**
```c
*(a1 + 0x10)           // 偏移量 0x10
*(_DWORD *)(a1 + 8)    // 偏移量 0x8，DWORD 类型
*(_QWORD *)(a1 + 0x20) // 偏移量 0x20，QWORD 类型
*(_BYTE *)(a1 + 4)     // 偏移量 0x4，BYTE 类型
```

**数组访问：**
```c
*(a1 + 8 * i)          // 数组，元素大小 8 字节
a1[i]                  // 数组访问
```

**嵌套结构：**
```c
*(*a1 + 0x10)          // a1 指向的结构的第一字段是指针
```

**记录格式：**
```
offset=0x00, size=8, access=read/write, type=QWORD
offset=0x08, size=4, access=read, type=DWORD
...
```

### 第 3 步：遍历调用者进行分析

读取每个调用者函数并分析：

1. **参数传递**：调用时传递了什么？
   ```c
   sub_401000(v1);        // v1 可能是结构指针
   sub_401000(&v2);       // v2 是结构
   sub_401000(malloc(64)); // 结构大小约为 64 字节
   ```

2. **调用前后的操作**： 
   ```c
   v1 = malloc(0x40);     // 分配 0x40 字节
   *v1 = 0;               // 偏移量 0x00 初始化
   *(v1 + 8) = callback;  // 偏移量 0x08 是函数指针
   sub_401000(v1);
   ```

3. **收集更多偏移量访问**

### 第 4 步：遍历被调用者进行分析

读取每个被调用者函数并分析：

1. **参数如何使用**：
   ```c
   // 在被调用者中
   int callee(void *a1) {
       return *(a1 + 0x18);  // 访问偏移量 0x18
   }
   ```

2. **传递给其他函数**：
   ```c
   another_func(a1 + 0x20);  // 偏移量 0x20 可能是嵌套结构
   ```

### 第 5 步：聚合和推断

1. **合并所有偏移量信息**，按偏移量排序
2. **计算结构大小**：max(偏移量) + 最后字段的长度
3. **推断字段类型**：
   - 调用为函数指针 → 函数指针
   - 传递给 `strlen`/`printf` → 字符串指针
   - 与常量比较 → 枚举/标志
   - 增量/减量操作 → 计数器/索引
4. **识别常见模式**：
   - 偏移量 0 是函数指针表 → vtable（C++ 对象）
   - next/prev 指针 → 链表节点
   - refcount 字段 → 引用计数对象

---

## 输出格式

```c
/*
 * 结构恢复分析
 * 源函数：<func_address>
 * 分析范围：分析调用者/被调用者的数量
 * 
 * 使用此结构的函数：
 *   - 0x401000（初始化）
 *   - 0x401100（字段访问）
 *   - 0x401200（销毁）
 */

// 预估大小：0x48 字节
// 置信度：高 / 中 / 低

struct suggested_name {
    /* 0x00 */ void *vtable;           // vtable 指针，调用：(*(*this))()
    /* 0x08 */ int refcount;           // 引用计数，有 ++/-- 操作
    /* 0x0C */ int flags;              // 标志，与 0x1, 0x2 进行 AND
    /* 0x10 */ char *name;             // 字符串，传递给 strlen/printf
    /* 0x18 */ void *data;             // 数据指针
    /* 0x20 */ size_t size;            // 大小字段
    /* 0x28 */ struct node *next;      // 链表 next 指针
    /* 0x30 */ struct node *prev;      // 链表 prev 指针
    /* 0x38 */ callback_fn handler;    // 回调函数
    /* 0x40 */ void *user_data;        // 用户数据
};

// 字段访问示例：
// 0x401000: *(this + 0x08) += 1;     // refcount++
// 0x401100: printf("%s", *(this + 0x10));  // 打印 name
```
