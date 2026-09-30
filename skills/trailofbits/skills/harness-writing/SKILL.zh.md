---
name: harness-writing
description: 为C/C++和Rust设计并改进模糊测试框架。涵盖将原始字节映射到目标API、生成结构化输入、避免非确定性错误和虚假崩溃，以及决定一起模糊测试的内容。在编写第一个LLVMFuzzerTestOneInput或fuzz_target!框架时使用，当活动未发现任何问题或报告无法复现的崩溃时使用，或者当目标API需要结构化输入而不是原始输入时使用。
---

# 编写模糊测试框架

模糊测试框架是接收模糊测试器随机数据并将其路由到待测系统（SUT）的入口函数。你的框架质量直接决定了哪些代码路径会被执行以及是否发现关键错误。编写的框架不好可能会导致遗漏整个子系统或产生无法重现的崩溃。

## 概述

框架是模糊测试器随机字节生成和应用程序API之间的桥梁。它必须将原始字节解析为有意义的输入，调用目标函数，并优雅地处理边缘情况。任何模糊测试设置中最重要的部分就是框架——如果编写不好，应用程序的关键部分可能无法被覆盖。

### 关键概念

| 概念 | 描述 |
|------|-------------|
| **框架** | 接收模糊测试器输入并调用待测代码的函数 |
| **SUT** | 待测系统——被模糊测试的代码 |
| **入口点** | 模糊测试器要求的函数签名（例如，`LLVMFuzzerTestOneInput`） |
| **FuzzedDataProvider** | 用于从原始字节中提取类型数据的结构化提取辅助类 |
| **确定性** | 确保相同输入始终产生相同行为的属性 |
| **交错模糊测试** | 单个框架执行多个基于输入的操作 |

## 何时应用

**在以下情况应用此技术：**
- 首次为创建新的模糊测试目标
- 模糊测试活动代码覆盖率低或未发现错误
- 模糊测试期间发现的崩溃无法重现
- 目标API需要复杂或结构化输入
- 应该一起测试多个相关函数

**何时跳过此技术：**
- 使用项目中现有的经过充分测试的框架
- 工具提供满足你需求的自动框架生成
- 目标已经具有全面的模糊测试基础设施

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
- 接受外部输入（解析器、验证器、协议处理器）
- 解析复杂数据格式（JSON、XML、二进制协议）
- 执行安全关键操作（身份验证、密码学）
- 具有高圈复杂度或有多个分支

好的目标是：
- 协议解析器
- 文件格式解析器
- 序列化/反序列化函数
- 输入验证例程

### 第2步：编写最小框架

从调用目标函数的最简单可能的框架开始：

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
    // 确保最小大小对有意义的输入
    if (size < MIN_INPUT_SIZE || size > MAX_INPUT_SIZE) {
        return 0;
    }
    target_function(data, size);
    return 0;
}
```

**理由：** 模糊测试器生成所有大小的随机输入。你的框架必须处理空、微小、巨大或格式错误的输入，而不会在框架本身中引起意外问题（SUT中的崩溃是可以接受的——那正是我们正在寻找的）。

### 第4步：结构化输入

对于需要整数、字符串等类型数据的API，使用强制转换或像`FuzzedDataProvider`这样的辅助工具：

**简单强制转换:**
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
- 代码覆盖率（是否所有有趣的路径都被访问到？）
- 每秒执行次数（是否足够快？）
- 崩溃可重现性（是否可以用保存的输入重现崩溃？）

迭代框架以改进这些指标。

## 常见模式

### 模式：超越字节数组——强制转换为整数

**用例：** 当目标期望整数或浮点数等原始类型

**实现：**
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

**Rust等效：**
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

**为什么有效：** 任何8字节输入都是有效的。模糊测试器了解到输入必须正好是8字节，并且每个位翻转都会产生一个新的、可能有趣的输入。

### 模式：使用FuzzedDataProvider进行复杂输入

**用例：** 当目标需要多个字符串、整数或可变长度数据

**实现：**
```cpp
#include "FuzzedDataProvider.h"

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    FuzzedDataProvider fuzzed_data(data, size);

    // 提取不同类型的数据
    size_t allocation_size = fuzzed_data.ConsumeIntegral<size_t>();

    // 消费带终止符的可变长度字符串
    std::vector<char> str1 = fuzzed_data.ConsumeBytesWithTerminator<char>(32, 0xFF);
    std::vector<char> str2 = fuzzed_data.ConsumeBytesWithTerminator<char>(32, 0xFF);

    char* result = concat(&str1[0], str1.size(), &str2[0], str2.size(), allocation_size);
    if (result != NULL) {
        free(result);
    }

    return 0;
}
```

**为什么有帮助：** `FuzzedDataProvider` 处理从字节流中提取结构化数据的复杂性。它对于需要不同类型多个参数的API特别有用。

### 模式：交错模糊测试

**用例：** 当应该在一个框架中测试多个相关操作

**实现：**
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
- 比编写多个单独的框架更快
- 单个共享语料库意味着一个操作有趣的输入可能对其他操作也很有趣
- 可以发现操作之间的交互错误

**何时使用：**
- 操作共享相似的输入类型
- 操作在逻辑上相关（例如，算术操作、CRUD操作）
- 单个语料库对所有操作都有意义

### 模式：使用Arbitrary进行结构感知模糊测试（Rust）

**用例：** 当模糊测试使用自定义结构的Rust代码时

**实现：**
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

**框架与arbitrary一起使用：**
```rust
#![no_main]
use libfuzzer_sys::fuzz_target;

fuzz_target!(|data: your_project::Name| {
    data.check_buf();
});
```

**添加到Cargo.toml：**
```toml
[dependencies]
arbitrary = { version = "1", features = ["derive"] }
```

**为什么有帮助：** `arbitrary` 库自动处理将原始字节反序列化为你的Rust结构，减少样板代码并确保有效的结构构造。

**限制：** arbitrary库不提供反向序列化，因此你不能手动构造映射到特定结构的字节序列。这最适合从空语料库开始（对于libFuzzer很好，但对于AFL++有问题）。

## 高级用法

### 提示和技巧

| 提示 | 为什么有帮助 |
|-----|--------------|
| **从解析器开始** | 高错误密度，清晰的入口点，易于框架 |
| **模拟I/O操作** | 防止因阻塞I/O导致的挂起，实现确定性 |
| **使用FuzzedDataProvider** | 简化从原始字节中提取结构化数据的操作 |
| **重置全局状态** | 确保每次迭代都是独立和可重现的 |
| **在框架中释放资源** | 防止在长时间活动中发生资源耗尽 |
| **在框架中避免日志记录** | 日志记录很慢——模糊测试需要100s-1000s执行/秒 |
| **手动首先测试框架** | 在开始活动之前使用已知输入运行框架 |
| **早期检查覆盖率** | 确保框架到达预期的代码路径 |

### 使用协议缓冲区进行结构感知模糊测试

对于高度结构化的输入格式，考虑使用协议缓冲区作为中间格式和自定义变异器：

```cpp
// 在.proto文件中定义你的输入格式
// 使用libprotobuf-mutator生成有效的变异
// 这确保模糊测试器变异消息内容，而不是protobuf编码本身
```

这种方法设置更复杂，但可以防止模糊测试器浪费时间在无法解析的输入上。有关详细信息，请参阅[结构感知模糊测试文档](https://github.com/google/fuzzing/blob/master/docs/structure-aware-fuzzing.md)。

### 处理非确定性

**问题：** 随机值或时间依赖性导致非重现性崩溃。

**解决方案：**
- 用来自模糊测试器输入的确定性PRNG替换`rand()`：
  ```cpp
  uint32_t seed = fuzzed_data.ConsumeIntegral<uint32_t>();
  srand(seed);
  ```
- 模拟返回时间、PID或随机数据的系统调用
- 避免从`/dev/random`或`/dev/urandom`读取

### 重置全局状态

如果SUT使用全局状态（单例、静态变量），在每次迭代之间重置它：

```cpp
extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    // 在每次迭代之前重置全局状态
    global_reset();

    target_function(data, size);

    // 清理资源
    global_cleanup();
    return 0;
}
```

**理由：** 全局状态可能导致N次迭代后崩溃，而不是在特定输入上崩溃，使错误不可重现。

## 实用框架规则

遵循这些规则以确保有效的模糊测试框架：

| 规则 | 理由 |
|------|-----------|
| **处理所有输入大小** | 模糊测试器生成空、微小、巨大的输入——框架必须优雅地处理 |
| **永远不要调用`exit()`** | 调用`exit()`会停止模糊测试器进程。如果SUT需要，使用`abort()` |
| **加入所有线程** | 每次迭代必须运行到完成，然后才能开始下一次迭代 |
| **要快** | 目标是100s-1000s执行/秒。避免日志记录、高复杂性、多余内存 |
| **保持确定性** | 相同输入必须始终产生相同行为，以实现可重现性 |
| **避免全局状态** | 全局状态会降低可重现性——如果不可避免，请在每个迭代中重置 |
| **使用窄目标** | 不要在同一框架中模糊测试PNG和TCP——不同格式需要单独的目标 |
| **释放资源** | 防止内存泄漏，导致长时间活动期间资源耗尽 |

**注意：** 这些指南不仅适用于框架代码，也适用于整个SUT。如果SUT违反了这些规则，请考虑修复它（见模糊测试障碍技术）。

## 反模式

| 反模式 | 问题 | 正确方法 |
|--------------|---------|------------------|
| **没有重置的全局状态** | 非确定性崩溃 | 在框架开始时重置所有全局状态 |
| **阻塞I/O或网络调用** | 挂起模糊测试器，浪费时间 | 模拟I/O，使用内存缓冲区 |
| **框架中的内存泄漏** | 资源耗尽导致活动结束 | 在返回之前释放所有分配 |
| **在SUT中调用`exit()`** | 停止整个模糊测试过程 | 使用`abort()`或返回错误代码 |
| **框架中大量日志记录** | 通过数量级降低执行/秒 | 在模糊测试期间禁用日志记录 |
| **每次迭代执行过多操作** | 降低模糊测试器速度 | 保持迭代快速且专注 |
| **混合不相关的输入格式** | 语料库条目对格式不适用 | 为不同格式使用单独的框架 |
| **不验证输入大小** | 框架在边缘情况下崩溃 | 在访问`data`之前检查`size` |

## 工具特定指南

### libFuzzer

**框架签名:**
```cpp
extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    // 你的代码在这里
    return 0;  // 非零返回保留用于未来使用
}
```

**编译:**
```bash
clang++ -fsanitize=fuzzer,address -g harness.cc -o fuzz_target
```

**集成技巧:**
- 使用`FuzzedDataProvider.h`进行结构化输入提取
- 使用`-fsanitize=fuzzer`链接模糊测试运行时
- 添加清理器（`-fsanitize=address,undefined`）以检测更多错误
- 使用`-g`以在崩溃时获得更好的堆栈跟踪
- libFuzzer可以从空语料库开始——不需要种子输入

**运行:**
```bash
./fuzz_target corpus_dir/
```

**资源:**
- [FuzzedDataProvider头文件](https://github.com/llvm/llvm-project/blob/main/compiler-rt/include/fuzzer/FuzzedDataProvider.h)
- [libFuzzer文档](https://llvm.org/docs/LibFuzzer.html)

### AFL++

AFL++支持多种框架风格。为了最佳性能，使用持久模式：

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

**集成技巧：**
- 使用持久模式（`__AFL_LOOP`）可加速10-100倍
- 考虑延迟初始化（`__AFL_INIT()`）以跳过设置开销
- AFL++ 需要在语料库目录中至少有一个种子输入
- 使用 `AFL_USE_ASAN=1` 或 `AFL_USE_UBSAN=1` 进行 sanitizer 构建调试

**运行：**
```bash
afl-fuzz -i seeds/ -o findings/ -- ./fuzz_target
```

### cargo-fuzz (Rust)

**测试程序签名：**
```rust
#![no_main]
use libfuzzer_sys::fuzz_target;

fuzz_target!(|data: &[u8]| {
    // 在此处编写您的代码
});
```

**使用结构化输入（arbitrary crate）：**
```rust
#![no_main]
use libfuzzer_sys::fuzz_target;

fuzz_target!(|data: YourStruct| {
    data.check();
});
```

**创建测试程序：**
```bash
cargo fuzz init
cargo fuzz add my_target
```

**集成技巧：**
- 使用 `arbitrary` crate 进行自动结构反序列化
- cargo-fuzz 封装了 libFuzzer，因此所有 libFuzzer 功能均可使用
- 通过 cargo-fuzz 自动编译使用 sanitizers
- 测试程序位于 `fuzz/fuzz_targets/` 目录

**运行：**
```bash
cargo +nightly fuzz run my_target
```

**资源：**
- [cargo-fuzz 文档](https://rust-fuzz.github.io/book/cargo-fuzz.html)
- [arbitrary crate](https://github.com/rust-fuzz/arbitrary)

### go-fuzz

**测试程序签名：**
```go
// +build gofuzz

package mypackage

func Fuzz(data []byte) int {
    // 调用目标函数
    target(data)

    // 返回代码：
    // -1 如果输入无效
    //  0 如果输入有效但无意义
    //  1 如果输入有意义（例如，新增了代码覆盖率）
    return 0
}
```

**构建：**
```bash
go-fuzz-build
```

**集成技巧：**
- 对于增加覆盖率的输入返回 1（可选——fuzzer 可自动检测）
- 对于无效输入返回 -1 以降低相似变异的优先级
- go-fuzz 自动处理持久化

**运行：**
```bash
go-fuzz -bin=./mypackage-fuzz.zip -workdir=fuzz
```

## 故障排除

| 问题 | 原因 | 解决方案 |
|-------|-------|----------|
| **执行速度低** | 测试程序过慢（日志记录、I/O、复杂性） | 分析测试程序，移除瓶颈，模拟 I/O |
| **未发现崩溃** | 覆盖率未达到有问题的代码 | 检查覆盖率，改进测试程序以覆盖更多路径 |
| **崩溃不可复现** | 非确定性或全局状态 | 移除随机性，每次迭代重置全局变量 |
| **fuzzer 立即退出** | 测试程序调用 `exit()` | 将 `exit()` 替换为 `abort()` 或返回错误 |
| **内存不足错误** | 测试程序或 SUT 存在内存泄漏 | 释放分配，使用内存泄漏 sanitizer 查找泄漏 |
| **空输入崩溃** | 测试程序未验证大小 | 添加 `if (size < MIN_SIZE) return 0;` |
| **语料库未增长** | 输入过于受限或格式过于严格 | 使用 FuzzedDataProvider 或结构化模糊测试 |

## 相关技能

### 使用该技术的工具

| 技能 | 应用方式 |
|-------|----------------|
| **libfuzzer** | 使用 `LLVMFuzzerTestOneInput` 测试程序签名与 FuzzedDataProvider |
| **aflpp** | 支持持久模式测试程序（`__AFL_LOOP`）以提升性能 |
| **cargo-fuzz** | 使用 Rust 特定的 `fuzz_target!` 宏与 arbitrary crate 集成 |
| **atheris** | Python 测试程序接收字节，调用 Python 函数 |
| **ossfuzz** | 需要在特定目录结构中编写测试程序以进行云端模糊测试 |

### 相关技术

| 技能 | 关系 |
|-------|--------------|
| **覆盖率分析** | 衡量测试程序的有效性——是否覆盖了目标代码？ |
| **地址 sanitizer** | 检测测试程序发现的错误（缓冲区溢出、使用后释放） |
| **模糊测试字典** | 提供令牌以帮助测试程序通过格式检查 |
| **模糊测试障碍** | 当 SUT 违反测试程序规则时修补 SUT（退出、非确定性） |

## 资源

### 关键外部资源

**[libFuzzer 中拆分输入 - Google 模糊测试文档](https://github.com/google/fuzzing/blob/master/docs/split-inputs.md)**
解释在单个模糊测试测试程序中处理多个输入参数的技术，包括使用魔法分隔符和 FuzzedDataProvider。

**[使用 Protocol Buffers 进行结构化模糊测试](https://github.com/google/fuzzing/blob/master/docs/structure-aware-fuzzing.md)**
高级技术使用 protobuf 作为中间格式，通过自定义变异器确保 fuzzer 变异消息内容而非格式编码。

**[libFuzzer 文档](https://llvm.org/docs/LibFuzzer.html)**
官方 LLVM 文档，涵盖测试程序要求、最佳实践和高级功能。

**[cargo-fuzz 书籍](https://rust-fuzz.github.io/book/cargo-fuzz.html)**
全面指南，介绍使用 cargo-fuzz 和 arbitrary crate 编写 Rust 模糊测试测试程序。

### 视频资源

- [有效文件格式模糊测试](https://www.youtube.com/watch?v=qTTwqFRD1H8) - 关于编写文件格式解析器测试程序的会议演讲
- [现代 C/C++ 项目模糊测试](https://www.youtube.com/watch?v=x0FQkAPokfE) - 涵盖测试程序设计模式的教程
