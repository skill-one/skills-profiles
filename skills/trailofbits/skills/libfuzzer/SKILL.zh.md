---
name: libfuzzer
description: 在 Clang 编译的 C/C++ 代码上设置和运行 LLVM 内置的基于覆盖率的模糊测试工具 libFuzzer。涵盖测试框架结构、-fsanitize=fuzzer 构建方式、测试用例和字典管理、模糊测试工具集成以及测试活动筛选。适用于编写或调试 LLVMFuzzerTestOneInput 测试框架、在 C/C++ 库上启动模糊测试、在 libFuzzer 和 AFL++ 之间选择，或解决 libFuzzer 运行未发现任何问题的原因。
---

# libFuzzer

libFuzzer 是 LLVM 项目中的一部分，是一个进程内、基于覆盖率的模糊测试器。由于其简单性和与 LLVM 工具链的集成，它是模糊测试 C/C++ 项目的推荐起点。虽然 libFuzzer 自 2022 年底以来一直处于仅维护模式，但它的安装和使用比其替代方案更容易，支持广泛，并且将在可预见的未来继续维护。

## 使用场景

| 模糊测试器 | 最佳用途 | 复杂度 |
|--------|----------|------------|
| libFuzzer | 快速设置、单项目模糊测试 | 低 |
| AFL++ | 多核模糊测试、多样化变异 | 中等 |
| LibAFL | 自定义模糊测试器、研究项目 | 高 |
| Honggfuzz | 基于硬件的覆盖率 | 中等 |

**选择 libFuzzer 的情况：**
- 您需要为 C/C++ 代码进行简单、快速的设置
- 项目使用 Clang 进行编译
- 单核模糊测试在初始阶段就足够
- 将来可以考虑过渡到 AFL++（测试用例是兼容的）

**注意：** 为 libFuzzer 编写的模糊测试用例与 AFL++ 兼容，如果您需要更高级的功能（如更好的多核支持），迁移起来很方便。

## 快速入门

```c++
#include <stdint.h>
#include <stddef.h>

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    // 如有需要，验证输入
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

- LLVM/Clang 编译器（包含 libFuzzer）
- LLVM 工具用于覆盖率分析（可选）

### Linux (Ubuntu/Debian)

```bash
apt install clang llvm
```

对于最新版本的 LLVM：
```bash
# 从 apt.llvm.org 添加 LLVM 仓库
# 然后安装特定版本，例如：
apt install clang-18 llvm-18
```

### macOS

```bash
# 使用 Homebrew
brew install llvm

# 或者使用 Nix
nix-env -i clang
```

### Windows

通过 Visual Studio 安装 Clang。有关设置说明，请参阅 [Microsoft 的文档](https://learn.microsoft.com/en-us/cpp/build/clang-support-msbuild?view=msvc-170)。

**推荐：** 如果可能，在本地 x86_64 虚拟机或租用 DigitalOcean、AWS 或 Hetzner 上的虚拟机上进行模糊测试。Linux 为 libFuzzer 提供了最佳支持。

### 验证

```bash
clang++ --version
# 应显示 LLVM 版本信息
```

## 编写测试用例

### 测试用例结构

测试用例是模糊测试的入口点。libFuzzer 会反复调用 `LLVMFuzzerTestOneInput` 函数，并传入不同的输入。

```c++
#include <stdint.h>
#include <stddef.h>

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    // 1. 可选：验证输入大小
    if (size < MIN_REQUIRED_SIZE) {
        return 0;  // 拒绝过小的输入
    }

    // 2. 可选：将原始字节转换为结构化数据
    // 示例：从字节数组解析两个整数
    if (size >= 2 * sizeof(uint32_t)) {
        uint32_t a = *(uint32_t*)(data);
        uint32_t b = *(uint32_t*)(data + sizeof(uint32_t));
        my_function(a, b);
    }

    // 3. 调用目标函数
    target_function(data, size);

    // 4. 始终返回 0（非零值保留用于未来使用）
    return 0;
}
```

### 测试用例规则

| 做 | 不要 |
|----|-------|
| 处理所有输入类型（空、巨大、损坏） | 调用 `exit()` - 停止模糊测试过程 |
| 在返回之前合并所有线程 | 留下线程运行 |
| 保持测试用例快速简单 | 添加过多的日志或复杂性 |
| 维护确定性 | 使用随机数生成器或读取 `/dev/random` |
| 在运行之间重置全局状态 | 依赖先前执行的状态 |
| 使用狭窄、专注的目标 | 在一个测试用例中混合不相关的数据格式（PNG + TCP） |

**理由：**
- **速度很重要：** 目标是每个核心每秒执行 100-1000 次执行
- **可重复性：** 在模糊测试完成后必须可重现崩溃
- **隔离性：** 每次执行应该是独立的

### 使用 FuzzedDataProvider 处理复杂输入

对于复杂输入（字符串、多个参数），使用 `FuzzedDataProvider` 辅助函数：

```c++
#include <stdint.h>
#include <stddef.h>
#include "FuzzedDataProvider.h"  // 来自 LLVM 项目

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

从 [LLVM 仓库](https://github.com/llvm/llvm-project/blob/main/compiler-rt/include/fuzzer/FuzzedDataProvider.h) 下载 `FuzzedDataProvider.h`。

### 交错模糊测试

使用单个测试用例测试多个相关函数：

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

> **另见：** 有关详细的测试用例编写技术、处理复杂输入的模式、结构感知模糊测试和基于 protobuf 的模糊测试，请参阅 **fuzz-harness-writing** 技能。

## 编译

### 基本编译

关键标志是 `-fsanitize=fuzzer`，它：
- 链接 libFuzzer 运行时（提供 `main` 函数）
- 启用 SanitizerCoverage 仪器进行覆盖率跟踪
- 禁用内置函数，如 `memcmp`

```bash
clang++ -fsanitize=fuzzer -g -O2 harness.cc target.cc -o fuzz
```

**标志说明：**
- `-fsanitize=fuzzer`: 启用 libFuzzer
- `-g`: 添加调试符号（有助于崩溃分析）
- `-O2`: 生产级优化（推荐用于模糊测试）
- `-DNO_MAIN`: 如果您的代码有 `main` 函数，定义宏

### 使用 Sanitizers

**AddressSanitizer（推荐）：**
```bash
clang++ -fsanitize=fuzzer,address -g -O2 -U_FORTIFY_SOURCE harness.cc target.cc -o fuzz
```

**多个 sanitizer：**
```bash
clang++ -fsanitize=fuzzer,address,undefined -g -O2 harness.cc target.cc -o fuzz
```

> **另见：** 有关详细的 sanitizer 配置、常见问题、ASAN_OPTIONS 标志和高级 sanitizer 使用，请参阅 **address-sanitizer** 和 **undefined-behavior-sanitizer** 技能。

### 构建标志

| 标志 | 目的 |
|------|---------|
| `-fsanitize=fuzzer` | 启用 libFuzzer 运行时和仪器 |
| `-fsanitize=address` | 启用 AddressSanitizer（内存错误检测） |
| `-fsanitize=undefined` | 启用 UndefinedBehaviorSanitizer |
| `-fsanitize=fuzzer-no-link` | 不链接模糊测试器进行仪器（用于库） |
| `-g` | 包含调试符号 |
| `-O2` | 生产优化级别 |
| `-U_FORTIFY_SOURCE` | 禁用加固（可能干扰 ASan） |

### 构建静态库

对于生成静态库的项目：

1. 使用模糊测试仪器构建库：
```bash
export CC=clang CFLAGS="-fsanitize=fuzzer-no-link -fsanitize=address"
export CXX=clang++ CXXFLAGS="$CFLAGS"
./configure --enable-shared=no
make
```

2. 使用您的测试用例链接静态库：
```bash
clang++ -fsanitize=fuzzer -fsanitize=address harness.cc libmylib.a -o fuzz
```

### CMake 集成

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

创建一个语料库目录（可以开始为空）：

```bash
mkdir corpus/
```

**可选但推荐：** 提供种子输入（有效的示例文件）：

```bash
# 对于 PNG 解析器：
cp examples/*.png corpus/

# 对于协议解析器：
cp test_packets/*.bin corpus/
```

**种子输入的好处：**
- 模糊测试器不会从零开始
- 更快地到达有效的代码路径
- 显著提高效率

### 语料库结构

语料库目录包含：
- 触发唯一代码路径的输入文件
- 最小化版本（libFuzzer 自动最小化）
- 按内容哈希命名（例如，`a9993e364706816aba3e25717850c26c9cd0d89d`）

### 语料库最小化

libFuzzer 在模糊测试期间自动最小化语料库条目。要显式最小化：

```bash
mkdir minimized_corpus/
./fuzz -merge=1 minimized_corpus/ corpus/
```

这会在 `minimized_corpus/` 中创建一个去重、最小化的语料库。

> **另见：** 有关语料库创建策略、种子选择、特定格式的语料库构建和语料库维护，请参阅 **fuzzing-corpus** 技能。

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

`-fork` 和 `-ignore_crashes` 标志（实验性但广泛使用）允许在找到崩溃后继续模糊测试。

### 常见选项

**控制输入大小：**
```bash
./fuzz -max_len=4000 corpus/
```
经验法则：最小实际输入大小的 2 倍。

**设置超时：**
```bash
./fuzz -timeout=2 corpus/
```
中止运行时间超过 2 秒的测试用例。

**使用字典：**
```bash
./fuzz -dict=./format.dict corpus/
```

**关闭 stdout/stderr（加快模糊测试）：**
```bash
./fuzz -close_fd_mask=3 corpus/
```

**查看所有选项：**
```bash
./fuzz -help=1
```

### 多核模糊测试

**选项 1：任务和工作进程（推荐）：**
```bash
./fuzz -jobs=4 -workers=4 -fork=1 -ignore_crashes=1 corpus/
```
- `-jobs=4`: 运行 4 个顺序活动
- `-workers=4`: 使用 4 个进程并行处理工作
- 测试用例在活动之间共享

**选项 2：Fork 模式：**
```bash
./fuzz -fork=4 -ignore_crashes=1 corpus/
```

**注意：** 对于严肃的多核模糊测试，请考虑切换到 AFL++、Honggfuzz 或 LibAFL。

### 重新执行测试用例

**重新运行单个崩溃：**
```bash
./fuzz ./crash-a9993e364706816aba3e25717850c26c9cd0d89d
```

**在不模糊测试的情况下测试目录中的所有输入：**
```bash
./fuzz -runs=0 corpus/
```

### 解释输出

当模糊测试运行时，您会看到类似以下统计信息：

```
INFO: Seed: 3517090860
INFO: Loaded 1 modules (9 inline 8-bit counters)
#2      INITED cov: 3 ft: 4 corp: 1/1b exec/s: 0 rss: 26Mb
#57     NEW    cov: 4 ft: 5 corp: 2/4b lim: 4 exec/s: 0 rss: 26Mb
```

| 输出 | 含义 |
|--------|---------|
| `INITED` | 模糊测试初始化 |
| `NEW` | 发现新覆盖率，添加到语料库 |
| `REDUCE` | 在保持覆盖率的同时最小化输入 |
| `cov: N` | 打印的覆盖率边数 |
| `corp: X/Yb` | 语料库大小：X 条目，Y 总字节 |
| `exec/s: N` | 每秒执行次数 |
| `rss: NMb` | 常驻内存使用 |

**崩溃时：**
```
==11672== ERROR: libFuzzer: 致命信号
artifact_prefix='./'; 测试单元写入到 ./crash-a9993e364706816aba3e25717850c26c9cd0d89d
0x61,0x62,0x63,
abc
Base64: YWJj
```

崩溃保存到 `./crash-<hash>`，并显示输入的十六进制、UTF-8 和 Base64 格式。

**可重复性：** 使用 `-seed=<value>` 重现模糊测试活动（仅单核）。

## 模糊测试字典

字典通过提供有关输入格式的提示来帮助模糊测试器更快地发现有趣的输入。

### 字典格式

创建一个文本文件，其中包含引号字符串（每行一个）：

```conf
# 以 '#' 开头的行是注释

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
grep -o '".*"' header.h > header.dict
```

**从 man 页面：**
```bash
man curl | grep -oP '^\s*(--|-)\K\S+' | sed 's/[,.]$//' | sed 's/^/"&/; s/$/&"/' | sort -u > man.dict
```

**从二进制字符串：**
```bash
strings ./binary | sed 's/^/"&/; s/$/&"/' > strings.dict
```

**使用 LLM：** 向 ChatGPT 或类似工具请求为您的格式生成字典（例如，"为 JSON 解析器生成 libFuzzer 字典"）。

> **另见：** 有关高级字典生成、特定格式的字典和字典优化策略，请参阅 **fuzzing-dictionaries** 技能。

## 覆盖率分析

虽然 libFuzzer 显示基本覆盖率统计信息（`cov: N`），但详细的覆盖率分析需要额外的工具。

### 基于源码的覆盖率

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

**5. 生成 HTML 报告：**
```bash
llvm-cov show ./fuzz -instr-profile=coverage.profdata -format=html > coverage.html
```

### 提高覆盖率

**技巧：**
- 在语料库中提供更好的种子输入
- 使用字典进行格式感知模糊测试
- 检查测试用例是否适当执行目标
- 考虑结构感知模糊测试以处理复杂格式
- 运行更长的活动（数天/数周）

> **另见：** 有关详细的覆盖率分析技术、识别覆盖率差距、系统覆盖率改进以及跨模糊测试器比较覆盖率，请参阅 **coverage-analysis** 技能。

## Sanitizer 集成

### AddressSanitizer (ASan)

ASan 检测内存错误，如缓冲区溢出和使用后释放的 bug。**强烈推荐用于模糊测试。**

**启用 ASan：**
```bash
clang++ -fsanitize=fuzzer,address -g -O2 -U_FORTIFY_SOURCE harness.cc target.cc -o fuzz
```

**示例 ASan 输出：**
```
==1276163==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x6020000c4ab1
WRITE of size 1 at 0x6020000c4ab1 thread T0
    #0 0x55555568631a in check_buf(char*, unsigned long) main.cc:13:25
    #1 0x5555556860bf in LLVMFuzzerTestOneInput harness.cc:7:3
```

**使用环境变量配置 ASan：**
```bash
ASAN_OPTIONS=verbosity=1:abort_on_error=1 ./fuzz corpus/
```

**重要标志：**
- `verbosity=1`: 显示 ASan 正在活动
- `detect_leaks=0`: 禁用泄漏检测（泄漏在结束时报告）
- `abort_on_error=1`: 在错误时调用 `abort()` 而不是 `_exit()`

**缺点：**
- 2-4 倍减速
- 需要 ~20TB 虚拟内存（禁用内存限制：`-rss_limit_mb=0`）
- 在 Linux 上支持最佳

> **另见：** 有关全面的 ASan 配置、常见陷阱、符号化和与其他 sanitizer 结合使用，请参阅 **address-sanitizer** 技能。

### UndefinedBehaviorSanitizer (UBSan)

UBSan 检测未定义行为，如整数溢出、空指针解引用等。

**启用 UBSan：**
```bash
clang++ -fsanitize=fuzzer,undefined -g -O2 harness.cc target.cc -o fuzz
```

**与 ASan 结合使用：**
```bash
clang++ -fsanitize=fuzzer,address,undefined -g -O2 harness.cc target.cc -o fuzz
```

### MemorySanitizer (MSan)

MSan 检测未初始化内存读取。更复杂的使用（需要重新构建所有依赖项）。

```bash
clang++ -fsanitize=fuzzer,memory -g -O2 harness.cc target.cc -o fuzz
```

### 常见消毒器问题

| 问题 | 解决方案 |
|-------|----------|
| ASan 过度减慢模糊测试 | 对于非致命错误，使用 `-fsanitize-recover=address` |
| 内存不足 | 设置 `ASAN_OPTIONS=rss_limit_mb=0` 或 `-rss_limit_mb=0` |
| 栈溢出 | 增加栈大小：`ASAN_OPTIONS=stack_size=8388608` |
| `_FORTIFY_SOURCE` 导致的误报 | 使用 `-U_FORTIFY_SOURCE` 标志 |
| 依赖项中报告 MSan | 使用 `-fsanitize=memory` 重新构建所有依赖项 |

## 真实案例

### 案例 1：模糊测试 libpng

libpng 是一个广泛使用的用于读取/写入 PNG 图像的库。错误可能导致安全问题。

**1. 获取源代码：**
```bash
curl -L -O https://downloads.sourceforge.net/project/libpng/libpng16/1.6.37/libpng-1.6.37.tar.xz
tar xf libpng-1.6.37.tar.xz
cd libpng-1.6.37/
```

**2. 安装依赖项：**
```bash
apt install zlib1g-dev
```

**3. 使用模糊测试指令编译：**
```bash
export CC=clang CFLAGS="-fsanitize=fuzzer-no-link -fsanitize=address"
export CXX=clang++ CXXFLAGS="$CFLAGS"
./configure --enable-shared=no
make
```

**4. 获取测试框架（或自行编写）：**
```bash
curl -O https://raw.githubusercontent.com/glennrp/libpng/f8e5fa92b0e37ab597616f554bee254157998227/contrib/oss-fuzz/libpng_read_fuzzer.cc
```

**5. 准备语料库和字典：**
```bash
mkdir corpus/
curl -o corpus/input.png https://raw.githubusercontent.com/glennrp/libpng/acfd50ae0ba3198ad734e5d4dec2b05341e50924/contrib/pngsuite/iftp1n3p08.png
curl -O https://raw.githubusercontent.com/glennrp/libpng/2fff013a6935967960a5ae626fc21432807933dd/contrib/oss-fuzz/png.dict
```

**6. 链接并编译模糊测试器：**
```bash
clang++ -fsanitize=fuzzer -fsanitize=address libpng_read_fuzzer.cc .libs/libpng16.a -lz -o fuzz
```

**7. 运行模糊测试活动：**
```bash
./fuzz -close_fd_mask=3 -dict=./png.dict corpus/
```

### 案例 2：简单除法错误

查找除零错误的测试框架：

```c++
#include <stdint.h>
#include <stddef.h>

double divide(uint32_t numerator, uint32_t denominator) {
    // 错误：未检查分母是否为零
    return numerator / denominator;
}

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    if(size != 2 * sizeof(uint32_t)) {
        return 0;
    }

    uint32_t numerator = *(uint32_t*)(data);
    uint32_t denominator = *(uint32_t*)(data + sizeof(uint32_t));

    divide(numerator, denominator);

    return 0;
}
```

编译和模糊测试：
```bash
clang++ -fsanitize=fuzzer harness.cc -o fuzz
./fuzz
```

模糊测试器将快速找到导致崩溃的输入。

## 高级用法

### 小技巧和窍门

| 小技巧 | 有何帮助 |
|-------|--------------|
| 从单核开始，切换到 AFL++ 以支持多核 | libFuzzer 测试框架与 AFL++ 兼容 |
| 使用字典处理结构化格式 | 10-100 倍的更快错误发现速度 |
| 使用 `-close_fd_mask=3` 关闭文件描述符 | 如果 SUT 输出，速度提升 |
| 设置合理的 `-max_len` | 防止在巨大输入上浪费时间 |
| 运行数天/数周，而不是数分钟 | 覆盖率平台需要时间突破 |
| 使用测试套件的种子语料库 | 从有效输入开始模糊测试 |

### 基于结构的模糊测试

对于高度结构化的输入（例如复杂协议、文件格式），使用 libprotobuf-mutator：

- 使用 Protocol Buffers 定义输入结构
- libFuzzer 变换 protobuf 消息（保留结构的变体）
- 测试框架将 protobuf 转换为原生格式

有关详细信息，请参阅 [基于结构的模糊测试文档](https://github.com/google/fuzzing/blob/master/docs/structure-aware-fuzzing.md)。

### 自定义变异器

libFuzzer 允许自定义变异器进行专业模糊测试：

```c++
extern "C" size_t LLVMFuzzerCustomMutator(uint8_t *Data, size_t Size,
                                          size_t MaxSize, unsigned int Seed) {
    // 自定义变异逻辑
    return new_size;
}

extern "C" size_t LLVMFuzzerCustomCrossOver(const uint8_t *Data1, size_t Size1,
                                            const uint8_t *Data2, size_t Size2,
                                            uint8_t *Out, size_t MaxOutSize,
                                            unsigned int Seed) {
    // 自定义交叉逻辑
    return new_size;
}
```

### 性能调优

| 设置 | 影响 |
|---------|--------|
| `-close_fd_mask=3` | 关闭 stdout/stderr，加快模糊测试速度 |
| `-max_len=<合理大小>` | 避免在巨大输入上浪费时间 |
| `-timeout=<秒数>` | 检测死锁，防止卡住执行 |
| 禁用 ASan 作为基准 | 2-4 倍速度提升（但会漏掉内存错误） |
| 使用 `-jobs` 和 `-workers` | 有限的多核支持 |
| 在 Linux 上运行 | 最佳平台支持和性能 |

## 故障排除

| 问题 | 原因 | 解决方案 |
|---------|-------|----------|
| 经过数小时未发现崩溃 | 语料库质量差，覆盖率低 | 添加种子输入，使用字典，检查测试框架 |
| 执行速度非常慢 (<100) | 目标过于复杂，过度日志记录 | 优化目标，使用 `-close_fd_mask=3`，减少日志记录 |
| 内存不足 | ASan 的 20TB 虚拟内存 | 设置 `-rss_limit_mb=0` 以禁用 RSS 限制 |
| 模糊测试器在第一次崩溃后停止 | 默认行为 | 使用 `-fork=1 -ignore_crashes=1` 继续执行 |
| 无法重现崩溃 | 测试框架/目标中的非确定性 | 移除随机数生成，全局状态 |
| 使用 `-fsanitize=fuzzer` 时出现链接错误 | 缺少 libFuzzer 运行时 | 确保使用 Clang，检查 LLVM 安装 |
| GCC 项目无法使用 Clang 编译 | GCC 特定代码 | 使用 `gcc_plugin` 切换到 AFL++ |
| 覆盖率未提升 | 语料库平台 | 运行更长时间，添加字典，改进种子，检查覆盖率报告 |
| 出现崩溃但 ASan 未触发 | 未检测到 ASan 未检测到的内存错误 | 使用 `-fsanitize=address` 重新编译 |

## 相关技能

### 技术技能

| 技能 | 用例 |
|-------|----------|
| **fuzz-harness-writing** | 详细指导如何编写有效的测试框架，基于结构的模糊测试和 FuzzedDataProvider 使用 |
| **address-sanitizer** | 内存错误检测配置，ASAN_OPTIONS 和故障排除 |
| **undefined-behavior-sanitizer** | 在模糊测试期间检测未定义行为 |
| **coverage-analysis** | 衡量模糊测试效果和未测试代码路径 |
| **fuzzing-corpus** | 构建和管理种子语料库，语料库最小化策略 |
| **fuzzing-dictionaries** | 创建特定格式的字典以加快错误发现 |

### 相关模糊测试器

| 技能 | 考虑何时使用 |
|-------|------------------|
| **aflpp** | 当您需要严重的多核模糊测试，或 libFuzzer 覆盖率平台时 |
| **honggfuzz** | 当您希望在 Linux 上获得硬件覆盖反馈时 |
| **libafl** | 当您构建自定义模糊测试器或进行模糊测试研究时 |

## 资源

### 官方文档

- [LLVM libFuzzer 文档](https://llvm.org/docs/LibFuzzer.html) - 官方参考
- [Google 编写的 libFuzzer 指南](https://github.com/google/fuzzing/blob/master/tutorial/libFuzzerTutorial.md) - 步骤指南
- [SanitizerCoverage](https://clang.llvm.org/docs/SanitizerCoverage.html) - 覆盖率指令细节

### 高级主题

- [使用 libprotobuf-mutator 的基于结构的模糊测试](https://github.com/google/fuzzing/blob/master/docs/structure-aware-fuzzing.md)
- [libFuzzer 中的输入拆分](https://github.com/google/fuzzing/blob/master/docs/split-inputs.md)
- [FuzzedDataProvider 头文件](https://github.com/llvm/llvm-project/blob/main/compiler-rt/include/fuzzer/FuzzedDataProvider.h)

### 示例项目

- [OSS-Fuzz](https://github.com/google/oss-fuzz) - 为开源项目提供持续模糊测试（许多 libFuzzer 示例）
- [AFL++ 字典集合](https://github.com/AFLplusplus/AFLplusplus/tree/stable/dictionaries) - 可重用字典
