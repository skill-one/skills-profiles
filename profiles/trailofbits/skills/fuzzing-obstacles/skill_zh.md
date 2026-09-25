# 克服模糊测试障碍

代码库中经常包含反模糊测试模式，这些模式会阻止有效的覆盖率。校验和、全局状态（如时间种子伪随机数生成器）和验证检查可能会阻止模糊测试器探索更深的代码路径。本技术展示了如何修补您的待测系统（SUT），以便在模糊测试期间绕过这些障碍，同时保留生产行为。

## 概述

许多现实世界的程序都不是为模糊测试而设计的。它们可能：
- 在处理输入之前验证校验和或加密哈希
- 依赖全局状态（例如系统时间、环境变量）
- 使用非确定性随机数生成器
- 执行复杂的验证，使模糊测试器难以生成有效输入

这些模式使模糊测试变得困难，因为：
1. **校验和**：模糊测试器必须猜测正确的哈希值（概率极低）
2. **全局状态**：相同的输入在不同运行中产生不同的行为（破坏确定性）
3. **复杂验证**：模糊测试器花费精力处理验证失败，而不是探索更深层的代码

解决方案是条件编译：在模糊测试构建期间修改代码行为，同时保持生产代码不变。

### 关键概念

| 概念 | 描述 |
|-------|-------------|
| SUT修补 | 修改待测系统以使其对模糊测试友好 |
| 条件编译 | 根据编译时标志表现不同行为的代码 |
| 模糊测试构建模式 | 启用模糊测试特定修补的特别构建配置 |
| 假阳性 | 在模糊测试期间发现的在生产中不可能发生的崩溃 |
| 确定性 | 相同输入始终产生相同行为（对模糊测试至关重要） |

## 何时应用

**应用此技术时：**
- 模糊测试器在校验和或哈希验证处卡住
- 覆盖率报告显示大量无法访问的代码位于验证之后
- 代码使用基于时间的种子或其他非确定性全局状态
- 复杂验证使生成有效输入几乎不可能
- 您看到模糊测试器反复遇到相同的验证失败

**跳过此技术时：**
- 障碍可以通过良好的种子语料库或字典克服
- 验证足够简单，模糊测试器可以学习（例如，魔术字节）
- 您正在进行基于语法的或结构感知的模糊测试，可以处理验证
- 跳过检查会引入过多的假阳性
- 代码已经是模糊测试友好的

## 快速参考

| 任务 | C/C++ | Rust |
|------|-------|------|
| 检查模糊测试构建 | `#ifdef FUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION` | `cfg!(fuzzing)` |
| 在模糊测试期间跳过检查 | `#ifndef FUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION return -1; #endif` | `if !cfg!(fuzzing) { return Err(...) }` |
| 常见障碍 | 校验和、PRNG、基于时间的逻辑 | 校验和、PRNG、基于时间的逻辑 |
| 支持的模糊测试器 | libFuzzer、AFL++、LibAFL、honggfuzz | cargo-fuzz、libFuzzer |

## 分步指南

### 第1步：识别障碍

运行模糊测试器并分析覆盖率，以找到无法访问的代码。常见模式：

1. 查找在更深层处理之前进行校验和/哈希验证
2. 检查对`rand()`、`time()`或`srand()`的调用，使用系统种子
3. 查找拒绝大多数输入的验证函数
4. 识别跨运行不同的全局状态初始化

**帮助工具：**
- 覆盖率报告（见覆盖率分析技术）
- 使用`-fprofile-instr-generate`进行性能分析
- 手动检查入口点代码

### 第2步：添加条件编译

修改障碍以在模糊测试构建期间绕过它。

**C/C++示例：**

```c++
// 之前：硬障碍
if (checksum != expected_hash) {
    return -1;  // 模糊测试器永远无法通过这里
}

// 之后：条件绕过
if (checksum != expected_hash) {
#ifndef FUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION
    return -1;  // 仅在生产中强制执行
#endif
}
// 模糊测试器现在可以探索此检查之后的代码
```

**Rust示例：**

```rust
// 之前：硬障碍
if checksum != expected_hash {
    return Err(MyError::Hash);  // 模糊测试器永远无法通过这里
}

// 之后：条件绕过
if checksum != expected_hash {
    if !cfg!(fuzzing) {
        return Err(MyError::Hash);  // 仅在生产中强制执行
    }
}
// 模糊测试器现在可以探索此检查之后的代码
```

### 第3步：验证覆盖率改进

修补后：

1. 使用模糊测试仪器重新构建
2. 运行模糊测试器一小段时间
3. 与未修补版本比较覆盖率
4. 确认正在探索新的代码路径

### 第4步：评估假阳性风险

考虑跳过检查是否会引入不可能的程序状态：

- 代码是否假设验证后的属性？
- 跳过验证是否会引发在生产中不可能发生的崩溃？
- 是否存在隐式状态依赖？

如果可能存在假阳性，请考虑更针对性的修补（见常见模式以下）。

## 常见模式

### 模式：绕过校验和验证

**用例**：哈希/校验和阻止所有模糊测试器进度

**之前：**
```c++
uint32_t computed = hash_function(data, size);
if (computed != expected_checksum) {
    return ERROR_INVALID_HASH;
}
process_data(data, size);
```

**之后：**
```c++
uint32_t computed = hash_function(data, size);
if (computed != expected_checksum) {
#ifndef FUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION
    return ERROR_INVALID_HASH;
#endif
}
process_data(data, size);
```

**假阳性风险**：低 - 如果数据处理不依赖于校验和的正确性

### 模式：确定性PRNG种子

**用例**：非确定性随机状态防止可重复性

**之前：**
```c++
void initialize() {
    srand(time(NULL));  // 每次运行种子不同
}
```

**之后：**
```c++
void initialize() {
#ifdef FUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION
    srand(12345);  // 模糊测试使用固定种子
#else
    srand(time(NULL));
#endif
}
```

**假阳性风险**：低 - 模糊测试器可以使用固定种子探索所有代码路径

### 模式：谨慎验证跳过

**用例**：必须跳过验证，但下游代码有假设

**之前（危险）：**
```c++
#ifndef FUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION
if (!validate_config(&config)) {
    return -1;  // 确保config.x != 0
}
#endif

int32_t result = 100 / config.x;  // 在模糊测试中崩溃：除以零
```

**之后（安全）：**
```c++
#ifndef FUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION
if (!validate_config(&config)) {
    return -1;
}
#else
// 在模糊测试期间，为失败的验证使用安全默认值
if (!validate_config(&config)) {
    config.x = 1;  // 防止除以零
    config.y = 1;
}
#endif

int32_t result = 100 / config.x;  // 两种构建都安全
```

**假阳性风险**：缓解 - 提供安全默认值而不是跳过

### 模式：绕过复杂格式验证

**用例**：多步骤验证使有效输入生成几乎不可能

**Rust示例：**

```rust
// 之前：多个验证阶段
pub fn parse_message(data: &[u8]) -> Result<Message, Error> {
    validate_magic_bytes(data)?;
    validate_structure(data)?;
    validate_checksums(data)?;
    validate_crypto_signature(data)?;

    deserialize_message(data)
}

// 之后：在模糊测试期间跳过昂贵的验证
pub fn parse_message(data: &[u8]) -> Result<Message, Error> {
    validate_magic_bytes(data)?;  // 保持廉价检查

    if !cfg!(fuzzing) {
        validate_structure(data)?;
        validate_checksums(data)?;
        validate_crypto_signature(data)?;
    }

    deserialize_message(data)
}
```

**假阳性风险**：中等 - 反序列化必须优雅地处理损坏的数据

## 高级用法

### 提示和技巧

| 提示 | 为什么有帮助 |
|-----|--------------|
| 保持廉价验证 | 魔术字节和大小检查无需太多成本即可引导模糊测试器 |
| 使用固定种子PRNG | 在探索所有代码路径的同时使行为确定性 |
| 逐步修补 | 一次跳过一个障碍，并测量覆盖率影响 |
| 添加防御性默认值 | 在跳过验证时提供安全的回退值 |
| 记录所有修补 | 未来维护者需要理解模糊测试与生产差异 |

### 真实世界示例

**OpenSSL**：使用`FUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION`修改加密算法行为。例如，在[crypto/cmp/cmp_vfy.c](https://github.com/openssl/openssl/blob/afb19f07aecc84998eeea56c4d65f5e0499abb5a/crypto/cmp/cmp_vfy.c#L665-L678)中，某些签名检查在模糊测试期间被放宽，以允许更深入地探索证书验证逻辑。

**ogg crate (Rust)**：使用`cfg!(fuzzing)`在模糊测试期间[跳过校验和验证](https://github.com/RustAudio/ogg/blob/5ee8316e6e907c24f6d7ec4b3a0ed6a6ce854cc1/src/reading.rs#L298-L300)。这允许模糊测试器探索音频处理代码，而无需花费精力猜测正确的校验和。

### 衡量修补效果

应用修补后，量化改进：

1. **行覆盖率**：使用`llvm-cov`或`cargo-cov`查看新可达的行
2. **基本块覆盖率**：比行覆盖率更细粒度
3. **函数覆盖率**：现在可以访问多少更多函数？
4. **语料库大小**：模糊测试器是否生成更多多样化的输入？

有效的修补通常使覆盖率提高10-50%或更多。

### 与其他技术的结合

障碍修补与其他技术结合效果良好：
- **语料库种子**：提供有效输入以通过初始解析
- **字典**：帮助模糊测试器学习魔术字节和常见值
- **结构感知模糊测试**：使用protobuf或语法定义处理复杂格式
- **测试框架改进**：更好的测试框架有时可以完全避免障碍

## 反模式

| 反模式 | 问题 | 正确方法 |
|--------------|---------|------------------|
| 整体跳过所有验证 | 创建假阳性和不稳定的模糊测试 | 仅跳过阻止覆盖率的特定障碍 |
| 无风险评估 | 假阳性浪费时间和隐藏真实错误 | 分析下游代码的假设 |
| 忘记记录修补 | 未来维护者不理解差异 | 添加注释解释为什么修补是安全的 |
| 未测量就修补 | 不知道是否有效 | 比较修补前后的覆盖率 |
| 过度修补 | 模糊测试构建与生产差异太大 | 最小化构建之间的差异 |

## 工具特定指南

### libFuzzer

libFuzzer在编译期间自动定义`FUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION`。

```bash
# C++编译
clang++ -g -fsanitize=fuzzer,address -DFUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION \
    harness.cc target.cc -o fuzzer

# 宏通常由-fsanitize=fuzzer自动定义
clang++ -g -fsanitize=fuzzer,address harness.cc target.cc -o fuzzer
```

**集成技巧：**
- 宏自动定义；通常不需要手动定义
- 使用`#ifdef`检查宏
- 与清理器结合使用以检测新可达代码中的错误

### AFL++

AFL++在使用其编译器包装器时也定义`FUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION`。

```bash
# 使用AFL++包装器编译
afl-clang-fast++ -g -fsanitize=address target.cc harness.cc -o fuzzer

# 宏由afl-clang-fast自动定义
```

**集成技巧：**
- 使用`afl-clang-fast`或`afl-clang-lto`自动定义宏
- 持久模式测试框架从障碍修补中受益最大
- 考虑使用`AFL_LLVM_LAF_ALL`进行额外的输入到状态转换

### honggfuzz

honggfuzz在构建目标时也支持宏。

```bash
# 编译
hfuzz-clang++ -g -fsanitize=address target.cc harness.cc -o fuzzer
```

**集成技巧：**
- 使用`hfuzz-clang`或`hfuzz-clang++`包装器
- 宏可用于条件编译
- 与honggfuzz的反馈驱动模糊测试结合使用

### cargo-fuzz (Rust)

cargo-fuzz在构建期间自动设置`fuzzing` cfg选项。

```bash
# 构建模糊测试目标（cfg!(fuzzing)自动设置）
cargo fuzz build fuzz_target_name

# 运行模糊测试目标
cargo fuzz run fuzz_target_name
```

**集成技巧：**
- 在生产构建中使用`cfg!(fuzzing)`进行运行时检查
- 使用`#[cfg(fuzzing)]`进行编译时条件编译
- 模糊测试cfg仅在`cargo fuzz`构建期间设置，不在常规`cargo build`期间
- 可以使用`RUSTFLAGS="--cfg fuzzing"`进行测试手动启用

### LibAFL

LibAFL支持C/C++编写的目标的C/C++宏。

```bash
# 编译
clang++ -g -fsanitize=address -DFUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION \
    target.cc -c -o target.o
```

**集成技巧：**
- 手动定义宏或使用编译器标志
- 与libFuzzer相同
- 在构建自定义LibAFL基础模糊测试器时很有用

## 故障排除

| 问题 | 原因 | 解决方案 |
|-------|-------|----------|
| 覆盖率修补后未提高 | 错误识别了障碍 | 分析执行以找到实际瓶颈 |
| 许多假阳性崩溃 | 下游代码有假设 | 添加防御性默认值或部分验证 |
| 代码编译不同 | 宏未在所有构建配置中定义 | 验证源文件和依赖项中的宏 |
| 模糊测试器在修补代码中找到错误 | 补丁引入了无效状态 | 审查补丁以检查状态不变量；考虑更安全的方法 |
| 无法重现生产中的错误 | 构建差异太大 | 最小化补丁；对状态关键检查保留验证 |

## 相关技能

### 使用此技术的工具

| 技能 | 如何应用 |
|-------|----------------|
| **libfuzzer** | 自动定义`FUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION` |
| **aflpp** | 通过编译器包装器支持宏 |
| **honggfuzz** | 用于条件编译的宏 |
| **cargo-fuzz** | 为Rust条件编译设置`cfg!(fuzzing)` |

### 相关技术

| 技能 | 关系 |
|-------|--------------|
| **fuzz-harness-writing** | 更好的测试框架可能避免障碍；修补使更深入的探索成为可能 |
| **coverage-analysis** | 使用覆盖率识别障碍并衡量修补效果 |
| **corpus-seeding** | 语料库种子可以在不修补的情况下克服障碍 |
| **dictionary-generation** | 字典有助于魔术字节，但不是校验和或复杂验证 |

## 资源

### 关键外部资源

**[OpenSSL模糊测试文档](https://github.com/openssl/openssl/tree/master/fuzz)**
OpenSSL的模糊测试基础设施展示了大规模使用`FUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION`。该项目使用此宏修改加密验证、证书解析和其他安全关键代码路径，以在保持生产正确性的同时启用更深入的模糊测试。

**[LibFuzzer关于标志的文档](https://llvm.org/docs/LibFuzzer.html)**
官方LLVM文档，介绍模糊测试器如何定义编译器宏以及如何有效地使用它们。涵盖与清理器结合使用和覆盖率仪器化。

**[Rust cfg属性参考](https://doc.rust-lang.org/reference/conditional-compilation.html)**
完整的Rust条件编译参考，包括`cfg!(fuzzing)`和`cfg!(test)`。解释编译时与运行时条件编译的区别以及最佳实践。
