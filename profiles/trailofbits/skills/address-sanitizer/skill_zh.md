# AddressSanitizer (ASan)

AddressSanitizer (ASan) 是一种广泛使用的内存错误检测工具，在软件测试中（尤其是模糊测试）被大量使用。它有助于检测那些可能被忽略的内存损坏错误，例如缓冲区溢出、使用后释放错误以及其他内存安全违规行为。

## 概述

ASan 是模糊测试的标准实践，因为它在识别内存漏洞方面非常有效。它在编译时对代码进行插桩，以跟踪内存分配和访问，并在运行时检测非法操作。

### 关键概念

| 概念 | 描述 |
|------|-------------|
| 插桩 | ASan 在编译时向内存操作添加运行时检查 |
| 影子内存 | 将 20TB 的虚拟内存映射到跟踪分配状态 |
| 性能开销 | 与未插桩的代码相比，大约慢 2-4 倍 |
| 检测范围 | 检测缓冲区溢出、使用后释放、双重释放和内存泄漏 |

## 何时应用

**应用此技术时：**
- 模糊测试 C/C++ 代码以查找内存安全漏洞
- 使用 unsafe 块测试 Rust 代码
- 调试与内存损坏相关的崩溃
- 运行单元测试，其中怀疑存在内存错误

**跳过此技术时：**
- 运行生产代码（ASan 可能会降低安全性）
- 平台是 Windows 或 macOS（ASan 支持有限）
- 性能开销对于您的用例不可接受
- 模糊测试没有 FFI 的纯安全语言（例如，纯 Go、纯 Java）

## 快速参考

| 任务 | 命令/模式 |
|------|-----------------|
| 启用 ASan (Clang/GCC) | `-fsanitize=address` |
| 启用详细程度 | `ASAN_OPTIONS=verbosity=1` |
| 禁用泄漏检测 | `ASAN_OPTIONS=detect_leaks=0` |
| 强制错误时中止 | `ASAN_OPTIONS=abort_on_error=1` |
| 多个选项 | `ASAN_OPTIONS=verbosity=1:abort_on_error=1` |

## 分步指南

### 第 1 步：使用 ASan 编译

使用 `-fsanitize=address` 标志编译和链接您的代码：

```bash
clang -fsanitize=address -g -o my_program my_program.c
```

推荐使用 `-g` 标志，以便在 ASan 检测到错误时获得更好的堆栈跟踪。

### 第 2 步：配置 ASan 选项

设置 `ASAN_OPTIONS` 环境变量以配置 ASan 的行为：

```bash
export ASAN_OPTIONS=verbosity=1:abort_on_error=1:detect_leaks=0
```

### 第 3 步：运行您的程序

执行 ASan 插桩的二进制文件。当检测到内存错误时，ASan 将打印详细报告：

```bash
./my_program
```

### 第 4 步：调整模糊测试器内存限制

ASan 需要 20TB 的虚拟内存。禁用模糊测试器内存限制：

- libFuzzer: `-rss_limit_mb=0`
- AFL++: `-m none`

## 常见模式

### 模式：基本的 ASan 集成

**用例：** 带有 ASan 的标准模糊测试设置

**之前：**
```bash
clang -o fuzz_target fuzz_target.c
./fuzz_target
```

**之后：**
```bash
clang -fsanitize=address -g -o fuzz_target fuzz_target.c
ASAN_OPTIONS=verbosity=1:abort_on_error=1 ./fuzz_target
```

### 模式：带单元测试的 ASan

**用例：** 为单元测试套件启用 ASan

**之前：**
```bash
gcc -o test_suite test_suite.c -lcheck
./test_suite
```

**之后：**
```bash
gcc -fsanitize=address -g -o test_suite test_suite.c -lcheck
ASAN_OPTIONS=detect_leaks=1 ./test_suite
```

## 高级用法

### 提示和技巧

| 提示 | 有何帮助 |
|-----|--------------|
| 使用 `-g` 标志 | 提供详细的堆栈跟踪以进行调试 |
| 设置 `verbosity=1` | 确认在程序启动前 ASan 已启用 |
| 在模糊测试期间禁用泄漏 | 泄漏检测不会导致立即崩溃，会弄乱输出 |
| 启用 `abort_on_error=1` | 一些模糊测试器需要 `abort()` 而不是 `_exit()` |

### 理解 ASan 报告

当 ASan 检测到内存错误时，它将打印详细报告，包括：

- **错误类型**：缓冲区溢出、使用后释放等
- **堆栈跟踪**：错误发生的位置
- **分配/释放跟踪**：内存分配/释放的位置
- **内存映射**：错误周围的影子内存状态

示例 ASan 报告：
```
==12345==ERROR: AddressSanitizer: heap-buffer-overflow on address 0x60300000eff4 at pc 0x00000048e6a3
READ of size 4 at 0x60300000eff4 thread T0
    #0 0x48e6a2 in main /path/to/file.c:42
```

### 组合其他清理器

ASan 可以与其他清理器结合使用以进行综合检测：

```bash
clang -fsanitize=address,undefined -g -o fuzz_target fuzz_target.c
```

### 平台特定注意事项

**Linux**：完整的 ASan 支持和最佳性能
**macOS**：有限支持，某些功能可能无法工作
**Windows**：实验性支持，不推荐用于生产模糊测试

## 反模式

| 反模式 | 问题 | 正确方法 |
|--------------|---------|------------------|
| 在生产中使用 ASan | 可能使应用程序安全性降低 | 仅在测试中使用 ASan |
| 未禁用内存限制 | 模糊测试器可能因 20TB 虚拟内存限制而终止进程 | 设置 `-rss_limit_mb=0` 或 `-m none` |
| 忽略泄漏报告 | 内存泄漏表明资源管理问题 | 在模糊测试活动结束时审查泄漏报告 |

## 工具特定指南

### libFuzzer

同时编译模糊测试器和地址清理器：

```bash
clang++ -fsanitize=fuzzer,address -g harness.cc -o fuzz
```

使用无限 RSS 运行：

```bash
./fuzz -rss_limit_mb=0
```

**集成提示：**
- 始终将 `-fsanitize=fuzzer` 与 `-fsanitize=address` 结合使用
- 使用 `-g` 以便在崩溃报告中获得详细的堆栈跟踪
- 考虑 `ASAN_OPTIONS=abort_on_error=1` 以更好地处理崩溃

参考：[libFuzzer: AddressSanitizer](https://github.com/google/fuzzing/blob/master/docs/good-fuzz-target.md#memory-error-detection)

### AFL++

使用 `AFL_USE_ASAN` 环境变量：

```bash
AFL_USE_ASAN=1 afl-clang-fast++ -g harness.cc -o fuzz
```

使用无限内存运行：

```bash
afl-fuzz -m none -i input_dir -o output_dir ./fuzz
```

**集成提示：**
- `AFL_USE_ASAN=1` 自动添加适当的编译标志
- 使用 `-m none` 以禁用 AFL++ 的内存限制
- 考虑 `AFL_MAP_SIZE` 以便程序具有大型覆盖映射

参考：[AFL++: AddressSanitizer](https://github.com/AFLplusplus/AFLplusplus/blob/stable/docs/fuzzing_in_depth.md#a-using-sanitizers)

### cargo-fuzz (Rust)

使用 `--sanitizer=address` 标志：

```bash
cargo fuzz run fuzz_target --sanitizer=address
```

或在 `fuzz/Cargo.toml` 中配置：

```toml
[profile.release]
opt-level = 3
debug = true
```

**集成提示：**
- ASan 对于模糊测试 unsafe Rust 代码或 FFI 边界很有用
- 安全 Rust 代码可能受益较少（编译器已经阻止了许多错误）
- 专注于 unsafe 块、原始指针和 C 库绑定

参考：[cargo-fuzz: AddressSanitizer](https://rust-fuzz.github.io/book/cargo-fuzz/tutorial.html#sanitizers)

### honggfuzz

使用 ASan 编译目标并使用 honggfuzz 链接：

```bash
honggfuzz -i input_dir -o output_dir -- ./fuzz_target_asan
```

编译目标：

```bash
hfuzz-clang -fsanitize=address -g target.c -o fuzz_target_asan
```

**集成提示：**
- honggfuzz 与 ASan 开箱即用
- 使用反馈驱动模式以获得更好的覆盖范围
- 监控内存使用情况，因为 ASan 增加了内存占用

## 故障排除

| 问题 | 原因 | 解决方案 |
|-------|-------|----------|
| 模糊测试器立即终止进程 | ASan 的 20TB 虚拟内存限制太低 | 使用 `-rss_limit_mb=0` (libFuzzer) 或 `-m none` (AFL++) |
| "ASan 运行时未初始化" | 链接顺序错误或缺少运行时 | 确保 `-fsanitize=address` 在编译和链接中都使用 |
| 泄漏报告弄乱输出 | 泄漏清理器默认启用 | 设置 `ASAN_OPTIONS=detect_leaks=0` |
| 性能差（>4x 延迟） | 调试模式或未优化的构建 | 与 `-fsanitize=address` 一起编译 `-O2` 或 `-O3` |
| ASan 未检测到明显的错误 | 二进制文件未插桩 | 检查 `ASAN_OPTIONS=verbosity=1` 以确认 ASan 打印启动信息 |
| 假阳性 | 中断器冲突 | 检查 ASan 常见问题解答，了解与特定库的已知问题 |

## 相关技能

### 使用此技术的工具

| 技能 | 如何应用 |
|-------|----------------|
| **libfuzzer** | 使用 `-fsanitize=fuzzer,address` 编译以集成模糊测试和内存错误检测 |
| **aflpp** | 使用 `AFL_USE_ASAN=1` 环境变量在编译期间 |
| **cargo-fuzz** | 使用 `--sanitizer=address` 标志为 Rust 模糊目标启用 ASan |
| **honggfuzz** | 使用 `-fsanitize=address` 编译目标以进行 ASan 插桩的模糊测试 |

### 相关技术

| 技能 | 关系 |
|-------|--------------|
| **undefined-behavior-sanitizer** | 通常与 ASan 结合使用以进行综合错误检测（未定义行为 + 内存错误） |
| **fuzz-harness-writing** | 测试框架必须设计为处理 ASan 检测到的崩溃并避免假阳性 |
| **coverage-analysis** | 覆盖引导模糊测试有助于触发 ASan 可以检测内存错误的代码路径 |

## 资源

### 关键外部资源

**[Google Sanitizers Wiki 上的 AddressSanitizer](https://github.com/google/sanitizers/wiki/AddressSanitizer)**

官方 ASan 文档涵盖：
- 算法和实现细节
- 检测到的错误类型完整列表
- 性能特征和开销
- 平台特定行为
- 已知限制和不兼容性

**[SanitizerCommonFlags](https://github.com/google/sanitizers/wiki/SanitizerCommonFlags)**

所有清理器共享的常见配置标志：
- `verbosity`：控制诊断输出级别
- `log_path`：将清理器输出重定向到文件
- `symbolize`：启用/禁用报告中符号解析
- `external_symbolizer_path`：使用自定义符号解析器

**[AddressSanitizerFlags](https://github.com/google/sanitizers/wiki/AddressSanizerFlags)**

ASan 特定的配置选项：
- `detect_leaks`：控制内存泄漏检测
- `abort_on_error`：错误时调用 `abort()` 而不是 `_exit()`
- `detect_stack_use_after_return`：检测堆栈使用后返回错误
- `check_initialization_order`：查找初始化顺序错误

**[AddressSanitizer FAQ](https://github.com/google/sanitizers/wiki/AddressSanitizer#faq)**

常见陷阱和解决方案：
- 链接顺序问题
- 与其他工具的冲突
- 平台特定问题
- 性能调优技巧

**[Clang AddressSanitizer 文档](https://clang.llvm.org/docs/AddressSanitizer.html)**

Clang 特定指南：
- 编译标志和选项
- 与其他 Clang 功能的交互
- 支持的平台和架构

**[GCC Instrumentation Options](https://gcc.gnu.org/onlinedocs/gcc/Instrumentation-Options.html#index-fsanitize_003daddress)**

GCC 特定的 ASan 文档：
- GCC 特定的标志和行为
- 与 Clang 实现的差异
- GCC 中的平台支持

**[AddressSanitizer: A Fast Address Sanity Checker (USENIX Paper)](https://www.usenix.org/sites/default/files/conference/protected-files/serebryany_atc12_slides.pdf)**

原始研究论文，包含技术细节：
- 影子内存算法
- 虚拟内存要求（历史上 16TB，现在 ~20TB）
- 性能基准
- 设计决策和权衡
