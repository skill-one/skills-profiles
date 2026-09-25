# libFuzzer

libFuzzer是一个进程内、基于覆盖率的模糊测试器，它是LLVM项目的一部分。由于其简单性和与LLVM工具链的集成，它是C/C++项目模糊测试的推荐起点。虽然libFuzzer自2022年底以来一直处于仅维护模式，但它的安装和使用比其替代方案更容易，得到了广泛的支持，并且将在可预见的未来得到维护。

## 使用场景

| 模糊测试器 | 最佳用途 | 复杂性 |
|--------|----------|------------|
| libFuzzer | 快速设置、单项目模糊测试 | 低 |
| AFL++ | 多核模糊测试、多样化变异 | 中等 |
| LibAFL | 自定义模糊测试器、研究项目 | 高 |
| Honggfuzz | 基于硬件的覆盖率 | 中等 |

**选择libFuzzer的情况：**
- 您需要为C/C++代码进行简单、快速的设置
- 项目使用Clang进行编译
- 初始阶段单核模糊测试就足够了
- 后续可以考虑迁移到AFL++（测试框架是兼容的）

**注意：** 为libFuzzer编写的测试框架与AFL++兼容，如果您需要更高级的功能（如更好的多核支持），迁移非常容易。

## 快速入门

```c++
#include <stdint.h>
#include <stddef.h>

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    // 如果需要，验证输入
    if (size < 1) return 0;

    // 使用模糊测试器提供的数据调用您的目标函数
    my_target_function(data, size);

    return 0;
}
```

编译和运行：
```bash
clang++ -fsanitize=fuzzer,address -g -O2 harness.cc target.cc -o fuzz
mkdir corpus/
./fuzz corpus/
```

## 安装

### 前置条件

- LLVM/Clang编译器（包含libFuzzer）
- LLVM用于覆盖率分析的工具（可选）

### Linux (Ubuntu/Debian)

```bash
apt install clang llvm
```

对于最新版本的LLVM：
```bash
# 从apt.llvm.org添加LLVM仓库
# 然后安装特定版本，例如：
apt install clang-18 llvm-18
```

### macOS

```bash
# 使用Homebrew
brew install llvm

# 或者使用Nix
nix-env -i clang
```

### Windows

通过Visual Studio安装Clang。有关设置说明，请参阅[Microsoft的文档](https://learn.microsoft.com/en-us/cpp/build/clang-support-msbuild?view=msvc-170)。

**推荐：** 如果可能，在本地x86_64虚拟机上进行模糊测试，或在DigitalOcean、AWS或Hetzner上租用。Linux为libFuzzer提供了最佳支持。

### 验证

```bash
clang++ --version
# 应显示LLVM版本信息
```

## 编写测试框架

### 测试框架结构

测试框架是模糊测试的入口点。libFuzzer会反复调用`LLVMFuzzerTestOneInput`函数，并传入不同的输入。

```c++
#include <stdint.h>
#include <stddef.h>

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    // 1. 可选：验证输入大小
    if (size < MIN_REQUIRED_SIZE) {
        return 0;  // 拒绝过小的输入
    }

    // 2. 可选：将原始字节转换为结构化数据
    // 示例：从字节数组中解析两个整数
    if (size >= 2 * sizeof(uint32_t)) {
        uint32_t a = *(uint32_t*)(data);
        uint32_t b = *(uint32_t*)(data + sizeof(uint32_t));
        my_function(a, b);
    }

    // 3. 调用目标函数
    target_function(data, size);

    // 4. 始终返回0（非零保留用于未来使用）
    return 0;
}
```

### 测试框架规则

| 做 | 不要 |
|----|-------|
| 处理所有输入类型（空、巨大、损坏） | 调用`exit()` - 停止模糊测试过程 |
| 返回前合并所有线程 | 留下正在运行的线程 |
| 保持测试框架快速简单 | 添加过多的日志记录或复杂性 |
| 保持确定性 | 使用随机数生成器或读取`/dev/random` |
| 在运行之间重置全局状态 | 依赖先前执行的状态 |
| 使用狭窄、专注的目标 | 在一个测试框架中混合不相关的数据格式（PNG + TCP） |

**理由：**
- **速度很重要：** 目标是每个核心每秒执行100-1000次执行
- **可重复性：** 模糊测试完成后必须可重现崩溃
- **隔离性：** 每次执行应该是独立的

### 使用FuzzedDataProvider处理复杂输入

对于复杂输入（字符串、多个参数），使用`FuzzedDataProvider`辅助函数：

```c++
#include <stdint.h>
#include <stddef.h>
#include "FuzzedDataProvider.h"  // 来自LLVM项目

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    FuzzedDataProvider fuzzed_data(data, size);

    // 提取结构化数据
    size_t allocation_size = fuzzed_data.ConsumeIntegral<size_t>();
    std::vector<char> str1 = fuzzed_data.ConsumeBytesWithTerminator<char>(32, 0xFF);
    std::vector<char> str2 = fuzzed_data.ConsumeBytesWithTerminator<char>(32, 0xFF);

    // 使用提取的数据调用目标
    char* result = concat(&str1[0], str1.size(), &str2[0], str2.size(), allocation_size);
    if (result != NULL) {
        free(result);
    }

    return 0;
}
```

从[LLVM仓库](https://github.com/llvm/llvm-project/blob/main/compiler-rt/include/fuzzer/FuzzedDataProvider.h)下载`FuzzedDataProvider.h`。

### 交错模糊测试

使用单个测试框架测试多个相关函数：

```c++
extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    if (size < 1 + 2 * sizeof(int32_t)) {
        return 0;
    }

    uint8_t mode = data[0];
    int32_t numbers[2];
    memcpy(numbers, data + 1, 2 * sizeof(int32_t));

    // 根据第一个字节选择函数
    switch (mode % 4) {
        case 0: add(numbers[0], numbers[1]); break;
        case 1: subtract(numbers[0], numbers[1]); break;
        case 2: multiply(numbers[0], numbers[1]); break;
        case 3: divide(numbers[0], numbers[1]); break;
    }

    return 0;
}
```

> **另见：** 有关详细的测试框架编写技术、处理复杂输入的模式、结构感知模糊测试和基于protobuf的模糊测试，请参阅**fuzz-harness-writing**技术技能。

## 编译

### 基本编译

关键标志是`-fsanitize=fuzzer`，它：
- 链接libFuzzer运行时（提供`main`函数）
- 启用SanitizerCoverage覆盖率跟踪
- 禁用内置函数，如`memcmp`

```bash
clang++ -fsanitize=fuzzer -g -O2 harness.cc target.cc -o fuzz
```

**标志说明：**
- `-fsanitize=fuzzer`：启用libFuzzer
- `-g`：添加调试符号（有助于崩溃分析）
- `-O2`：生产级优化（推荐用于模糊测试）
- `-DNO_MAIN`：如果您的代码有`main`函数，定义宏

### 使用Sanitizers

**AddressSanitizer（推荐）：**
```bash
clang++ -fsanitize=fuzzer,address -g -O2 -U_FORTIFY_SOURCE harness.cc target.cc -o fuzz
```

**多个sanitizers：**
```bash
clang++ -fsanitize=fuzzer,address,undefined -g -O2 harness.cc target.cc -o fuzz
```

> **另见：** 有关详细的sanitizer配置、常见问题、ASAN_OPTIONS标志和高级sanitizer使用，请参阅**address-sanitizer**和**undefined-behavior-sanitizer**技术技能。

### 构建标志

| 标志 | 目的 |
|------|---------|
| `-fsanitize=fuzzer` | 启用libFuzzer运行时和仪器 |
| `-fsanitize=address` | 启用AddressSanitizer（内存错误检测） |
| `-fsanitize=undefined` | 启用UndefinedBehaviorSanitizer |
| `-fsanitize=fuzzer-no-link` | 仪器而不链接fuzzer（用于库） |
| `-g` | 包含调试符号 |
| `-O2` | 生产优化级别 |
| `-U_FORTIFY_SOURCE` | 禁用加固（可能会干扰ASan） |

### 构建静态库

对于生成静态库的项目：

1. 使用模糊测试仪器构建库：
```bash
export CC=clang CFLAGS="-fsanitize=fuzzer-no-link -fsanitize=address"
export CXX=clang++ CXXFLAGS="$CFLAGS"
./configure --enable-shared=no
make
```

2. 使用您的测试框架链接静态库：
```bash
clang++ -fsanitize=fuzzer -fsanitize=address harness.cc libmylib.a -o fuzz
```

### CMake集成

```cmake
project(FuzzTarget)
cmake_minimum_required(VERSION 3.0)

add_executable(fuzz main.cc harness.cc)
target_compile_definitions(fuzz PRIVATE NO_MAIN=1)
target_compile_options(fuzz PRIVATE -g -O2 -fsanitize=fuzzer -fsanitize=address)
target_link_libraries(fuzz -fsanitize=fuzzer -fsanitize=address)
```

使用以下命令构建：
```bash
cmake -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ .
cmake --build .
```

## 语料库管理

### 创建初始语料库

创建一个用于语料库的目录（可以开始为空）：

```bash
mkdir corpus/
```

**可选但推荐：** 提供种子输入（有效的示例文件）：

```bash
# 对于PNG解析器：
cp examples/*.png corpus/

# 对于协议解析器：
cp test_packets/*.bin corpus/
```

**种子输入的好处：**
- 模糊测试器不会从零开始
- 更快地到达有效代码路径
- 显著提高效率

### 语料库结构

语料库目录包含：
- 触发唯一代码路径的输入文件
- 最小化版本（libFuzzer自动最小化）
- 按内容哈希命名（例如，`a9993e364706816aba3e25717850c26c9cd0d89d`）

### 语料库最小化

libFuzzer在模糊测试期间自动最小化语料库条目。要显式最小化：

```bash
mkdir minimized_corpus/
./fuzz -merge=1 minimized_corpus/ corpus/
```

这会在`minimized_corpus/`中创建一个去重、最小化的语料库。

> **另见：** 有关语料库创建策略、种子选择、特定格式的语料库构建和语料库维护，请参阅**fuzzing-corpus**技术技能。

## 运行活动

### 基本运行

```bash
./fuzz corpus/
```

这会运行直到找到崩溃或您停止它（Ctrl+C）。

### 推荐：崩溃后继续

```bash
./fuzz -fork=1 -ignore_crashes=1 corpus/
```

`-fork`和`-ignore_crashes`标志（实验性但广泛使用）允许在找到崩溃后继续模糊测试。

### 常见选项

**控制输入大小：**
```bash
./fuzz -max_len=4000 corpus/
```
经验法则：最小实际输入大小的2倍。

**设置超时：**
```bash
./fuzz -timeout=2 corpus/
```
超时测试用例超过2秒则中止。

**使用字典：**
```bash
./fuzz -dict=./format.dict corpus/
```

**关闭stdout/stderr（加快模糊测试）：**
```bash
./fuzz -close_fd_mask=3 corpus/
```

**查看所有选项：**
```bash
./fuzz -help=1
```

### 多核模糊测试

**选项1：任务和工作器（推荐）：**
```bash
./fuzz -jobs=4 -workers=4 -fork=1 -ignore_crashes=1 corpus/
```
- `-jobs=4`：运行4个顺序活动
- `-workers=4`：使用4个进程并行处理工作
- 测试用例在活动之间共享

**选项2：分叉模式：**
```bash
./fuzz -fork=4 -ignore_crashes=1 corpus/
```

**注意：** 对于严肃的多核模糊测试，请考虑切换到AFL++、Honggfuzz或LibAFL。

### 重新执行测试用例

**重新运行单个崩溃：**
```bash
./fuzz ./crash-a9993e364706816aba3e25717850c26c9cd0d89d
```

**在不进行模糊测试的情况下测试所有输入：**
```bash
./fuzz -runs=0 corpus/
```

### 解释输出

模糊测试运行时，您将看到类似以下统计信息：

```
INFO: Seed: 3517090860
INFO: Loaded 1 modules (9 inline 8-bit counters)
#2      INITED cov: 3 ft: 4 corp: 1/1b exec/s: 0 rss: 26Mb
#57     NEW    cov: 4 ft: 5 corp: 2/4b lim: 4 exec/s: 0 rss: 26Mb
```

| 输出 | 含义 |
|--------|---------|
| `INITED` | 模糊测试初始化 |
| `NEW` | 发现新的覆盖率，添加到语料库 |
| `REDUCE` | 在保持覆盖率的同时输入最小化 |
| `cov: N` | 打印的覆盖率边数 |
| `corp: X/Yb` | 语料库大小：X条目，Y总字节 |
| `exec/s: N` | 每秒执行次数 |
| `rss: NMb` | 常驻内存使用 |

**在崩溃时：**
```
==11672== ERROR: libFuzzer: deadly signal
artifact_prefix='./'; Test unit written to ./crash-a9993e364706816aba3e25717850c26c9cd0d89d
0x61,0x62,0x63,
abc
Base64: YWJj
```

崩溃保存到`./crash-<hash>`，并显示输入的十六进制、UTF-8和Base64形式。

**可重复性：** 使用`-seed=<value>`来重现模糊测试活动（仅单核）。

## 模糊测试字典

字典通过提供有关输入格式的提示来帮助模糊测试器更快地发现有趣的输入。

### 字典格式

创建一个文本文件，其中包含引号字符串（每行一个）：

```conf
# 以'#'开头的行是注释

# 魔术字节
magic="\x89PNG"
magic2="IEND"

# 关键字
"GET"
"POST"
"Content-Type"

# 十六进制序列
delimiter="\xFF\xD8\xFF"
```

### 使用字典

```bash
./fuzz -dict=./format.dict corpus/
```

### 生成字典

**从头文件：**
```bash
grep -o '"*"' header.h > header.dict
```

**从man页面：**
```bash
man curl | grep -oP '^\s*(--|-)\K\S+' | sed 's/[,.]$//' | sed 's/^/"&/; s/$/&"/' | sort -u > man.dict
```

**从二进制字符串：**
```bash
strings ./binary | sed 's/^/"&/; s/$/&"/' > strings.dict
```

**使用LLM：** 向ChatGPT或类似工具请求为您的格式生成字典（例如，“为JSON解析器生成libFuzzer字典”）。

> **另见：** 有关高级字典生成、特定格式的字典和字典优化策略，请参阅**fuzzing-dictionaries**技术技能。

## 覆盖率分析

虽然libFuzzer显示基本的覆盖率统计信息（`cov: N`），但详细的覆盖率分析需要额外的工具。

### 基于源代码的覆盖率

**1. 重新编译覆盖率仪器：**
```bash
clang++ -fsanitize=fuzzer -fprofile-instr-generate -fcoverage-mapping harness.cc target.cc -o fuzz
```

**2. 运行模糊测试器以收集覆盖率：**
```bash
LLVM_PROFILE_FILE="coverage-%p.profraw" ./fuzz -runs=10000 corpus/
```

**3. 合并覆盖率数据：**
```bash
llvm-profdata merge -sparse coverage-*.profraw -o coverage.profdata
```

**4. 生成覆盖率报告：**
```bash
llvm-cov show ./fuzz -instr-profile=coverage.profdata
```

**5. 生成HTML报告：**
```bash
llvm-cov show ./fuzz -instr-profile=coverage.profdata -format=html > coverage.html
```

### 提高覆盖率

**技巧：**
- 在语料库中提供更好的种子输入
- 使用字典进行格式感知模糊测试
- 检查测试框架是否正确执行目标
- 考虑结构感知模糊测试以处理复杂格式
- 运行更长时间的活动（数天/数周）

> **另见：** 有关详细的覆盖率分析技术、识别覆盖率差距、系统覆盖率改进以及跨模糊测试器比较覆盖率，请参阅**coverage-analysis**技术技能。

## Sanitizer集成

### AddressSanitizer (ASan)

ASan检测内存错误，如缓冲区溢出和使用后释放的bug。**强烈推荐用于模糊测试。**

**启用ASan：**
```bash
clang++ -fsanitize=fuzzer,address -g -O2 -U_FORTIFY_SOURCE harness.cc target.cc -o fuzz
```

**示例ASan输出：**
```
==1276163==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x6020000c4ab1
WRITE of size 1 at 0x6020000c4ab1 thread T0
    #0 0x55555568631a in check_buf(char*, unsigned long) main.cc:13:25
    #1 0x5555556860bf in LLVMFuzzerTestOneInput harness.cc:7:3
```

**使用环境变量配置ASan：**
```bash
ASAN_OPTIONS=verbosity=1:abort_on_error=1 ./fuzz corpus/
```

**重要标志：**
- `verbosity=1`：显示ASan正在运行
- `detect_leaks=0`：禁用泄漏检测（泄漏在活动结束时报告）
- `abort_on_error=1`：在错误时调用`abort()`而不是`_exit()`

**缺点：**
- 2-4倍减速
- 需要~20TB虚拟内存（禁用内存限制：`-rss_limit_mb=0`）
- 在Linux上支持最佳

> **另见：** 有关全面的ASan配置、常见陷阱、符号化和与其他sanitizers结合使用，请参阅**address-sanitizer**技术技能。

### UndefinedBehaviorSanitizer (UBSan)

UBSan检测未定义行为，如整数溢出、空指针解引用等。

**启用UBSan：**
```bash
clang++ -fsanitize=fuzzer,undefined -g -O2 harness.cc target.cc -o fuzz
```

**与ASan结合使用：**
```bash
clang++ -fsanitize=fuzzer,address,undefined -g -O2 harness.cc target.cc -o fuzz
```

### MemorySanitizer (MSan)

MSan检测未初始化的内存读取。更复杂的使用（需要重新构建所有依赖项）。

```bash
clang++ -fsanitize=fuzzer,memory -g -O2 harness.cc target.cc -o fuzz
```

### 常见Sanitizer问题

| 问题 | 原因 | 解决方案 |
|-------|-------|----------|
| 没有在数小时后找到崩溃 | 语料库差，覆盖率低 | 添加种子输入，使用字典，检查测试框架 |
| 执行速度非常慢 (<100) | 目标太复杂，过多的日志记录 | 优化目标，使用`-close_fd_mask=3`，减少日志记录 |
| 内存不足 | ASan的20TB虚拟内存 | 设置`-rss_limit_mb=0`以禁用RSS限制 |
| 模糊测试器在第一个崩溃后停止 | 默认行为 | 使用`-fork=1 -ignore_crashes=1`继续 |
| 无法重现崩溃 | 模糊测试器/目标中的非确定性 | 移除随机数生成器、全局状态 |
| 使用`-fsanitize=fuzzer`时链接错误 | 缺少libFuzzer运行时 | 确保使用Clang，检查LLVM安装 |
| GCC项目无法使用Clang编译 | GCC特定的代码 | 使用`gcc_plugin`切换到AFL++ |
| 覆盖率没有提高 | 语料库平台期 | 运行更长时间，添加字典，改进种子，检查覆盖率报告 |
| 崩溃但ASan没有触发 | 没有检测到内存错误，如果没有ASan | 重新编译并使用`-fsanitize=address` |

## 相关技能

### 技术技能

| 技能 | 用途 |
|-------|----------|
| **fuzz-harness-writing** | 详细指导编写有效的测试框架，结构感知模糊测试和FuzzedDataProvider使用 |
| **address-sanitizer** | 内存错误检测配置，ASAN_OPTIONS和故障排除 |
| **undefined-behavior-sanitizer** | 在模糊测试期间检测未定义行为 |
| **coverage-analysis** | 衡量模糊测试的有效性和识别未测试的代码路径 |
| **fuzzing-corpus** | 构建和管理种子语料库，语料库最小化策略 |
| **fuzzing-dictionaries** | 创建特定格式的字典以加快错误发现 |

### 相关模糊测试器

| 技能 | 当考虑何时使用 |
|-------|------------------|
| **aflpp** | 当您需要严肃的多核模糊测试，或者libFuzzer覆盖率平台化时 |
| **honggfuzz** | 当您想要基于硬件的覆盖率反馈时（在Linux上） |
| **libafl** | 当构建自定义模糊测试器或进行模糊测试研究时 |
