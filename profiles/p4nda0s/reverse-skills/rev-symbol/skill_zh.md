# rev-symbol - 符号恢复

分析函数代码特征以恢复/识别函数符号和名称。

## 预检查

**确定可用的 IDA 访问方法：**

**选项 A — IDA Pro MCP（如果连接则优先选择）：**
检查 IDA Pro MCP 服务器是否连接（查找活动的 `ida-pro` 或等效 MCP 连接）。如果已连接，您可以通过 MCP 工具直接查询 IDA，无需导出文件。使用 MCP 进行分析。

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
├── decompile/              # 反编译 C 代码目录
│   ├── 0x401000.c          # 每个函数一个文件，以十六进制地址命名
│   ├── 0x401234.c
│   └── ...
├── decompile_failed.txt    # 失败的反编译列表
├── decompile_skipped.txt   # 跳过的函数列表
├── strings.txt             # 字符串表（地址、长度、类型、内容）
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

## 符号恢复步骤

### 第 1 步：分析内部特征

仔细检查目标函数以查找：

- **字符串常量**：函数中使用的字符串可能揭示其用途
- **数值常量 / 魔数**：
  - MD5：`0x67452301`, `0xEFCDAB89`, `0x98BADCFE`, `0x10325476`
  - CRC32：`0xEDB88320`
  - Base64 字符集：`ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/`
  - AES S-Box：`0x63, 0x7C, 0x77, 0x7B...`
  - Zlib：`0x78`, `0x9C`（压缩头）
  - 其他常量/魔数...
- **代码结构**：循环模式、位运算、特定算法流程

如果您可以通过常量/结构识别出已知算法，请直接告知用户。

### 第 2 步：分析交叉引用

**分析被调用函数 (callee)：**
- 读取被调用函数列表中的函数
- 对于每个被调用函数，检查其地址是否存在于 `imports.txt` 中
- 即使符号缺失，也要识别调用模式：

  **配对函数模式（通过匹配调用对识别）：**
  ```c
  // malloc/free, new/delete, alloc/dealloc
  xx = sub_A(0x100);        // alloc：接受大小，返回指针
  ...
  sub_B(xx);                // free：接受相同指针
  
  // mutex_lock/mutex_unlock, pthread_mutex_lock/unlock
  sub_A(lock_ptr);          // 锁定
  ...                       // 临界区
  sub_B(lock_ptr);          // 解锁（相同锁对象）
  
  // open/close, fopen/fclose, CreateFile/CloseHandle
  fd = sub_A("/path", 0);   // open：路径 + 标志，返回句柄
  ...
  sub_B(fd);                // close：接受句柄
  
  // pthread_create/pthread_join
  sub_A(&tid, 0, func, arg); // 创建：输出参数，属性，函数，参数
  ...
  sub_B(tid, &ret);          // 加入：线程 ID，输出参数
  

  **参数模式识别：**
  ```c
  // socket(AF_INET, SOCK_STREAM, 0) - 固定常量
  sub_XXX(2, 1, 0);         // socket：域=2，类型=1，协议=0
  
  // connect/bind(sockfd, addr, addrlen)
  sub_XXX(fd, &var, 16);   // 地址结构，长度=16（IPv4）
  
  // memcpy/memmove(dst, src, size)
  sub_XXX(dst, src, n);     // 3 个参数：目标，源，计数
  
  // memset(ptr, value, size)
  sub_XXX(ptr, 0, 0x100);   // 3 个参数：指针，字节值，计数
  
  // read/write(fd, buf, count)
  ret = sub_XXX(fd, buf, n); // 返回读取/写入的字节数
  
  // strcmp/strncmp(s1, s2) 或 (s1, s2, n)
  if (sub_XXX(s1, s2) == 0)  // 相等时返回 0
  ```

  **返回值模式：**
  ```c
  // 文件/套接字操作：出错时为 -1
  if ((fd = sub_XXX(...)) == -1) goto error;
  
  // 分配：失败时为 NULL
  if (!(ptr = sub_XXX(size))) goto error;
  
  // 成功/失败：0 = 成功
  if (sub_XXX(...) != 0) goto error;
  
  // strlen：返回 size_t
  len = sub_XXX(str);
  sub_YYY(dst, src, len);   // len 用于 memcpy
  ```

**分析调用函数 (caller)：**
- 读取调用函数列表中的函数
- 如果一个调用者有符号（检查 `exports.txt`），从上下文中推断被调用函数的用途
- 递归检查：沿着调用链向上追溯，直到找到有符号的函数
- 分析调用者如何使用返回值

### 第 3 步：信息收集和搜索

收集以下信息：
- 函数中的字符串（检查 `strings.txt` 中函数使用的地址）
- 魔数 / 常量
- 已知的被调用导入（交叉引用被调用函数与 `imports.txt`）
- `exports.txt` 中的调用者/被调用符号
- 识别的配对函数模式

基于收集的信息：
1. 首先尝试基于以下内容进行本地推理：
   - 函数签名（参数的数量和类型）
   - 配对调用模式（alloc/free，lock/unlock）
   - 调用链中的已知导入
   - 与已知算法相似的代码结构

2. 如果不确定，使用 **网络搜索** 进行搜索：
   - 搜索魔数：`0x67452301 0xEFCDAB89 算法`
   - 搜索代码模式：`左旋转 xor 常量 算法`
   - 搜索函数中发现的唯一字符串
   - 搜索参数模式：`function(int, int, 0) socket`

---

## 输出格式

```
## 符号恢复分析：<函数地址>

### 函数特征
- 字符串：<发现字符串列表>
- 常量：<关键常量列表>
- 被调用导入：<列表>

### 交叉引用分析
- 调用者：<调用者和其符号>
- 被调用者：<被调用者和其符号>

### 推断结果
- **建议符号名称**：<建议名称>
- **置信度**：高 / 中 / 低
- **推理**：<解释为什么建议这个名字>

### 类似的开源实现
- <如果找到类似的开源代码，提供链接>
```
