# 编写模糊测试框架

模糊测试框架是接收模糊测试器随机数据并将其路由到待测系统（SUT）的入口函数。你的框架质量直接决定了哪些代码路径会被执行，以及是否能够发现关键错误。一个编写糟糕的框架可能会遗漏整个子系统或产生无法重现的崩溃。

## 概述

框架是模糊测试器随机字节生成与你的应用程序API之间的桥梁。它必须将原始字节解析为有意义的输入，调用目标函数，并优雅地处理边缘情况。任何模糊测试设置中最重要的部分就是框架——如果编写不当，你的应用程序的关键部分可能无法被覆盖。

### 关键概念

| 概念 | 描述 |
|------|-------------|
| **框架** | 接收模糊测试器输入并调用待测代码的函数 |
| **SUT** | 待测系统—the 被模糊测试的代码 |
| **入口点** | 模糊测试器要求的函数签名（例如，`LLVMFuzzerTestOneInput`） |
| **FuzzedDataProvider** | 用于从原始字节中结构化提取类型数据的辅助类 |
| **确定性** | 确保相同输入始终产生相同行为的属性 |
| **交错模糊测试** | 单个框架执行多个操作，基于输入 |

## 应用场景

**应用此技术时：**
- 首次为模糊测试目标创建
- 模糊测试活动代码覆盖率低或未发现错误
- 模糊测试期间发现的崩溃无法重现
- 目标API需要复杂或结构化输入
- 应一起测试多个相关函数

**跳过此技术时：**
- 使用项目中现有的经过充分测试的框架
- 工具提供满足你需求的自动框架生成
- 目标已具有全面的模糊测试基础设施

## 快速参考

| 任务 | 模式 |
|------|---------|
| 最小C++框架 | `extern "C" int LLVMFuzzerTestOneInput(const uint8_t* data, size_t size)` |
| 最小Rust框架 | `fuzz_target!(|data: &[u8]| { ... })` |
| 大小验证 | `if (size < MIN_SIZE) return 0;` |
| 转换为整数 | `uint32_t val = *(uint32_t*)(data);` |
| 使用FuzzedDataProvider | `FuzzedDataProvider fuzzed_data(data, size);` |
| 提取类型数据（C++） | `auto val = fuzzed_data.ConsumeIntegral<uint32_t>();` |
| 提取字符串（C++） | `auto str = fuzzed_data.ConsumeBytesWithTerminator<char>(32, 0xFF);` |

## 分步指南

### 第1步：识别入口点

在代码库中查找以下函数：
- 接收外部输入（解析器、验证器、协议处理器）
- 解析复杂数据格式（JSON、XML、二进制协议）
- 执行安全关键操作（身份验证、密码学）
- 具有高圈复杂度或许多分支

好的目标是：
- 协议解析器
- 文件格式解析器
- 序列化/反序列化函数
- 输入验证例程

### 第2步：编写最小框架

从调用你的目标函数的最简单可能的框架开始：

**C/C++:**
```cpp
extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    target_function(data, size);
    return 0;
}
```

**Rust:**
```rust
#![no_main]
use libfuzzer_sys::fuzz_target;

fuzz_target!(|data: &[u8]| {
    target_function(data);
});
```

### 第3步：添加输入验证

拒绝太小或太大的输入，使其没有意义：

```cpp
extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    // 确保最小大小对有意义输入
    if (size < MIN_INPUT_SIZE || size > MAX_INPUT_SIZE) {
        return 0;
    }
    target_function(data, size);
    return 0;
}
```

**原理：** 模糊测试器生成所有大小的随机输入。你的框架必须处理空、微小、巨大或格式错误的输入，而不会在框架本身（SUT中的崩溃是可以接受的——那正是我们想要的）中引起意外问题。

### 第4步：结构化输入

对于需要类型数据（整数、字符串等）的API，使用转换或像`FuzzedDataProvider`这样的辅助工具：

**简单转换:**
```cpp
extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    if (size != 2 * sizeof(uint32_t)) {
        return 0;
    }

    uint32_t numerator = *(uint32_t*)(data);
    uint32_t denominator = *(uint32_t*)(data + sizeof(uint32_t));

    divide(numerator, denominator);
    return 0;
}
```

**使用FuzzedDataProvider:**
```cpp
#include "FuzzedDataProvider.h"

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    FuzzedDataProvider fuzzed_data(data, size);

    size_t allocation_size = fuzzed_data.ConsumeIntegral<size_t>();

    std::vector<char> str1 = fuzzed_data.ConsumeBytesWithTerminator<char>(32, 0xFF);
    std::vector<char> str2 = fuzzed_data.ConsumeBytesWithTerminator<char>(32, 0xFF);

    concat(&str1[0], str1.size(), &str2[0], str2.size(), allocation_size);
    return 0;
}
```

### 第5步：测试和迭代

运行模糊测试器并监控：
- 代码覆盖率（是否到达有趣的路径？）
- 每秒执行次数（是否足够快？）
- 崩溃可重现性（能否用保存的输入重现崩溃？）

迭代框架以改进这些指标。

## 常见模式

### 模式：超越字节数组—转换为整数

**用例：** 当目标期望原始类型（如整数或浮点数）时

**实现:**
```cpp
extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    // 确保正好是两个4字节数字
    if (size != 2 * sizeof(uint32_t)) {
        return 0;
    }

    // 将输入拆分为两个整数
    uint32_t numerator = *(uint32_t*)(data);
    uint32_t denominator = *(uint32_t*)(data + sizeof(uint32_t));

    divide(numerator, denominator);
    return 0;
}
```

**Rust等效:**
```rust
fuzz_target!(|data: &[u8]| {
    if data.len() != 2 * std::mem::size_of::<i32>() {
        return;
    }

    let numerator = i32::from_ne_bytes([data[0], data[1], data[2], data[3]]);
    let denominator = i32::from_ne_bytes([data[4], data[5], data[6], data[7]]);

    divide(numerator, denominator);
});
```

**为什么有效：** 任何8字节输入都是有效的。模糊测试器学习输入必须正好是8字节，并且每个位翻转都会产生一个新的、可能有趣的输入。

### 模式：使用FuzzedDataProvider进行复杂输入

**用例：** 当目标需要多个字符串、整数或可变长度数据时

**实现:**
```cpp
#include "FuzzedDataProvider.h"

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    FuzzedDataProvider fuzzed_data(data, size);

    // 提取不同类型的数据
    size_t allocation_size = fuzzed_data.ConsumeIntegral<size_t>();

    // 提取带终止符的可变长度字符串
    std::vector<char> str1 = fuzzed_data.ConsumeBytesWithTerminator<char>(32, 0xFF);
    std::vector<char> str2 = fuzzed_data.ConsumeBytesWithTerminator<char>(32, 0xFF);

    char* result = concat(&str1[0], str1.size(), &str2[0], str2.size(), allocation_size);
    if (result != NULL) {
        free(result);
    }

    return 0;
}
```

**为什么有帮助：** `FuzzedDataProvider` 处理从字节流中提取结构化数据的复杂性。它对于需要多个不同类型参数的API特别有用。

### 模式：交错模糊测试

**用例：** 当多个相关操作应在单个框架中测试时

**实现:**
```cpp
extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    if (size < 1 + 2 * sizeof(int32_t)) {
        return 0;
    }

    // 第一个字节选择操作
    uint8_t mode = data[0];

    // 接下来的字节是操作数
    int32_t numbers[2];
    memcpy(numbers, data + 1, 2 * sizeof(int32_t));

    int32_t result = 0;
    switch (mode % 4) {
        case 0:
            result = add(numbers[0], numbers[1]);
            break;
        case 1:
            result = subtract(numbers[0], numbers[1]);
            break;
        case 2:
            result = multiply(numbers[0], numbers[1]);
            break;
        case 3:
            result = divide(numbers[0], numbers[1]);
            break;
    }

    // 防止编译器优化掉调用
    printf("%d", result);
    return 0;
}
```

**优点：**
- 编写一个框架比多个独立框架更快
- 单个共享语料库意味着一个操作有趣的输入可能对其他操作也很有趣
- 可以发现操作之间的交互错误

**何时使用：**
- 操作共享相似的输入类型
- 操作在逻辑上相关（例如，算术操作、CRUD操作）
- 单个语料库对所有操作都有意义

### 模式：使用Arbitrary进行结构化模糊测试（Rust）

**用例：** 当模糊测试使用自定义struct的Rust代码时

**实现:**
```rust
use arbitrary::Arbitrary;

#[derive(Debug, Arbitrary)]
pub struct Name {
    data: String
}

impl Name {
    pub fn check_buf(&self) {
        let data = self.data.as_bytes();
        if data.len() > 0 && data[0] == b'a' {
            if data.len() > 1 && data[1] == b'b' {
                if data.len() > 2 && data[2] == b'c' {
                    process::abort();
                }
            }
        }
    }
}
```

**框架与arbitrary:**
```rust
#![no_main]
use libfuzzer_sys::fuzz_target;

fuzz_target!(|data: your_project::Name| {
    data.check_buf();
});
```

**添加到Cargo.toml:**
```toml
[dependencies]
arbitrary = { version = "1", features = ["derive"] }
```

**为什么有帮助：** `arbitrary` 包自动处理将原始字节反序列化为你的Rust struct，减少样板代码并确保有效的struct构造。

**限制：** arbitrary包不提供反向序列化，因此你无法手动构造映射到特定struct的字节数组。这最适合从空语料库开始（对于libFuzzer很好，但对于AFL++有问题）。

## 高级用法

### 提示和技巧

| 提示 | 为什么有帮助 |
|-----|--------------|
| **从解析器开始** | 高错误密度，清晰的入口点，易于框架 |
| **模拟I/O操作** | 防止因阻塞I/O导致的挂起，实现确定性 |
| **使用FuzzedDataProvider** | 简化从原始字节中提取结构化数据 |
| **重置全局状态** | 确保每次迭代都是独立且可重现的 |
| **在框架中释放资源** | 防止在长时间活动中发生内存耗尽 |
| **在框架中避免日志记录** | 日志记录很慢——模糊测试需要100s-1000s执行/秒 |
| **手动首先测试框架** | 在开始活动之前用已知输入运行框架 |
| **早期检查覆盖率** | 确保框架到达预期的代码路径 |

### 使用Protocol Buffers进行结构化模糊测试

对于高度结构化的输入格式，考虑使用Protocol Buffers作为中间格式和自定义变异器：

```cpp
// 在.proto文件中定义你的输入格式
// 使用libprotobuf-mutator生成有效的变异
// 这确保模糊测试器变异消息内容，而不是protobuf编码本身
```

这种方法设置更复杂，但可以防止模糊测试器浪费时间在不解析的输入上。有关详细信息，请参阅[结构化模糊测试文档](https://github.com/google/fuzzing/blob/master/docs/structure-aware-fuzzing.md)。

### 处理非确定性

**问题：** 随机值或时间依赖性导致非可重现的崩溃。

**解决方案：**
- 用来自模糊测试器输入的确定性PRNG替换`rand()`：
  ```cpp
  uint32_t seed = fuzzed_data.ConsumeIntegral<uint32_t>();
  srand(seed);
  ```
- 模拟返回时间、PID或随机数据的系统调用
- 避免从`/dev/random`或`/dev/urandom`读取

### 重置全局状态

如果SUT使用全局状态（单例、静态变量），在每次迭代后重置它：

```cpp
extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    // 在每次迭代前重置全局状态
    global_reset();

    target_function(data, size);

    // 清理资源
    global_cleanup();
    return 0;
}
```

**原理：** 全局状态可能导致N次迭代后崩溃，而不是特定输入上的崩溃，使崩溃不可重现。

## 实用框架规则

遵循这些规则以确保有效的模糊测试框架：

| 规则 | 原理 |
|------|-----------|
| **处理所有输入大小** | 模糊测试器生成空、微小、巨大的输入——框架必须优雅地处理 |
| **永远不要调用`exit()`** | 调用`exit()`会停止模糊测试器进程。如果SUT需要，请使用`abort()` |
| **加入所有线程** | 每次迭代必须运行到完成，然后才能开始下一次迭代 |
| **要快** | 目标是100s-1000s执行/秒。避免日志记录、高复杂性、多余内存 |
| **保持确定性** | 相同输入必须始终产生相同行为，以实现可重现性 |
| **避免全局状态** | 全局状态会降低可重现性——如果不可避免，请在每个迭代中重置 |
| **使用窄目标** | 不要在同一个框架中模糊PNG和TCP——不同格式需要单独的目标 |
| **释放资源** | 防止内存泄漏导致长时间活动中的资源耗尽 |

**注意：** 这些指南不仅适用于框架代码，也适用于整个SUT。如果SUT违反了这些规则，请考虑修复它（见模糊测试障碍技术）。

## 反模式

| 反模式 | 问题 | 正确方法 |
|--------------|---------|------------------|
| **没有重置的全局状态** | 非确定性崩溃 | 在框架开始时重置所有全局状态 |
| **阻塞I/O或网络调用** | 挂起模糊测试器，浪费时间 | 模拟I/O，使用内存缓冲区 |
| **框架中的内存泄漏** | 资源耗尽导致活动结束 | 释放所有分配，使用泄漏检测器找到泄漏 |
| **SUT中调用`exit()`** | 停止整个模糊测试过程 | 使用`abort()`或返回错误代码 |
| **框架中大量日志记录** | 通过数量级降低执行/秒 | 在模糊测试期间禁用日志记录 |
| **每次迭代执行过多操作** | 模糊测试器速度变慢 | 保持迭代快速且专注 |
| **混合不相关的输入格式** | 语料库条目对格式不适用 | 为不同格式使用单独的框架 |
| **不验证输入大小** | 框架在边缘情况下崩溃 | 在访问`data`之前检查`size` |

## 工具特定指南

### libFuzzer

**框架签名:**
```cpp
extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    // 你的代码在这里
    return 0;  // 非零返回是保留的，供将来使用
}
```

**编译:**
```bash
clang++ -fsanitize=fuzzer,address -g harness.cc -o fuzz_target
```

**集成技巧:**
- 使用`FuzzedDataProvider.h`进行结构化输入提取
- 使用`-fsanitize=fuzzer`链接模糊测试运行时
- 添加卫生器（`-fsanitize=address,undefined`）以检测更多错误
- 使用`-g`以在崩溃时获得更好的堆栈跟踪
- libFuzzer可以开始时使用空语料库——不需要种子输入

**运行:**
```bash
./fuzz_target corpus_dir/
```

**资源:**
- [libFuzzer文档](https://llvm.org/docs/LibFuzzer.html)

### AFL++

AFL++支持多种框架风格。为了获得最佳性能，请使用持久模式：

**持久模式框架:**
```cpp
#include <unistd.h>

int main(int argc, char **argv) {
    #ifdef __AFL_HAVE_MANUAL_CONTROL
        __AFL_INIT();
    #endif

    unsigned char buf[MAX_SIZE];

    while (__AFL_LOOP(10000)) {
        // 从stdin读取输入
        ssize_t len = read(0, buf, sizeof(buf));
        if (len <= 0) break;

        // 调用目标函数
        target_function(buf, len);
    }

    return 0;
}
```

**编译:**
```bash
afl-clang-fast++ -g harness.cc -o fuzz_target
```

**集成技巧:**
- 使用持久模式（`__AFL_LOOP`）以获得10-100倍的加速
- 考虑延迟初始化（`__AFL_INIT()`）以跳过设置开销
- AFL++需要至少一个种子输入在语料库目录中
- 使用`AFL_USE_ASAN=1`或`AFL_USE_UBSAN=1`进行卫生器构建

**运行:**
```bash
afl-fuzz -i seeds/ -o findings/ -- ./fuzz_target
```

### cargo-fuzz (Rust)

**框架签名:**
```rust
#![no_main]
use libfuzzer_sys::fuzz_target;

fuzz_target!(|data: &[u8]| {
    // 你的代码在这里
});
```

**使用结构化输入（arbitrary crate）:**
```rust
#![no_main]
use libfuzzer_sys::fuzz_target;

fuzz_target!(|data: YourStruct| {
    data.check();
});
```

**创建框架:**
```bash
cargo fuzz init
cargo fuzz add my_target
```

**集成技巧:**
- 使用`arbitrary` crate进行自动struct反序列化
- cargo-fuzz包装libFuzzer，所以所有libFuzzer功能都可用
- 通过cargo-fuzz自动编译卫生器
- 框架位于`fuzz/fuzz_targets/`目录

**运行:**
```bash
cargo +nightly fuzz run my_target
```

**资源:**
- [cargo-fuzz文档](https://rust-fuzz.github.io/book/cargo-fuzz.html)
- [arbitrary crate](https://github.com/rust-fuzz/arbitrary)

### go-fuzz

**框架签名:**
```go
// +build gofuzz

package mypackage

func Fuzz(data []byte) int {
    // 调用目标函数
    target(data)

    // 返回代码：
    // -1如果输入无效
    //  0如果输入有效但无趣
    //  1如果输入有趣（例如，添加了新的覆盖率）
    return 0
}
```

**构建:**
```bash
go-fuzz-build
```

**集成技巧:**
- 返回1以指示输入添加了覆盖率（可选——模糊测试器可以自动检测）
- 返回-1以指示无效输入以降低类似变异的优先级
- go-fuzz自动处理持久性

**运行:**
```bash
go-fuzz -bin=./mypackage-fuzz.zip -workdir=fuzz
```

## 故障排除

| 问题 | 原因 | 解决方案 |
|-------|-------|----------|
| **执行/秒低** | 框架太慢（日志记录、I/O、复杂性） | 分析框架，移除瓶颈，模拟I/O |
| **未发现崩溃** | 覆盖率未到达有问题的代码 | 检查覆盖率，改进框架以到达更多路径 |
| **非可重现崩溃** | 非确定性或全局状态 | 移除随机性，在迭代之间重置全局状态 |
| **模糊测试器立即退出** | 框架调用`exit()` | 用`abort()`或返回错误代码 |
| **内存错误** | 框架或SUT中的内存泄漏 | 释放分配，使用泄漏检测器找到泄漏 |
| **空输入上的崩溃** | 框架不验证大小 | 添加`if (size < MIN_SIZE) return 0;` |
| **语料库未增长** | 输入太受限或格式太严格 | 使用FuzzedDataProvider或结构化模糊测试 |

## 相关技能

### 使用此技术的工具

| 技能 | 如何应用 |
|-------|----------------|
| **libfuzzer** | 使用`LLVMFuzzerTestOneInput`框架签名和FuzzedDataProvider |
| **aflpp** | 支持持久模式框架（`__AFL_LOOP`）以获得性能 |
| **cargo-fuzz** | 使用Rust特定的`fuzz_target!`宏和arbitrary crate集成 |
| **atheris** | Python框架接收字节，调用Python函数 |
| **ossfuzz** | 需要特定目录结构的框架以进行云模糊测试 |

### 相关技术

| 技能 | 关系 |
|-------|--------------|
| **覆盖率分析** | 衡量框架有效性——你是否到达了目标代码？ |
| **地址卫生器** | 检测框架发现的错误（缓冲区溢出、使用后释放） |
| **模糊测试字典** | 提供令牌以帮助模糊测试器通过框架的格式检查 |
| **模糊测试障碍** | 当它违反框架规则时修补SUT |

## 资源

### 关键外部资源

**[libFuzzer中的输入拆分 - Google模糊测试文档](https://github.com/google/fuzzing/blob/master/docs/split-inputs.md)**
解释在单个模糊测试框架中处理多个输入参数的技术，包括使用魔法分隔符和FuzzedDataProvider。

**[使用Protocol Buffers进行结构化模糊测试](https://github.com/google/fuzzing/blob/master/docs/structure-aware-fuzzing.md)**
高级技术，使用protobuf作为中间格式和自定义变异器，确保模糊测试器变异消息内容而不是格式编码。

**[libFuzzer文档](https://llvm.org/docs/LibFuzzer.html)**
官方LLVM文档，涵盖框架要求、最佳实践和高级功能。

**[cargo-fuzz书籍](https://rust-fuzz.github.io/book/cargo-fuzz.html)**
关于使用cargo-fuzz和arbitrary crate编写Rust模糊测试框架的全面指南。

### 视频资源

- [有效的文件格式模糊测试](https://www.youtube.com/watch?v=qTTwqFRD1H8) - 会议演讲，关于编写用于文件格式解析器的框架
- [现代C/C++项目模糊测试](https://www.youtube.com/watch?v=x0FQkAPokfE) - 指南，涵盖框架设计模式
