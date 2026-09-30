---
name: coverage-analysis
description: 使用llvm-cov、lcov或模糊测试器自身的覆盖率输出，衡量并解释模糊测试活动实际达到的范围。涵盖为新活动建立基线、读取覆盖率报告以及将未覆盖区域转化为测试框架、种子或字典工作。在模糊测试器停滞不前、判断测试框架是否有效、更改测试框架后，或询问某些代码为何从未被执行时使用。
---

# 覆盖率分析

覆盖率分析对于理解在模糊测试过程中代码的哪些部分被执行至关重要。它有助于识别模糊测试阻塞器（如魔法值检查），并跟踪 harness 改进随时间的有效性。

## 概述

模糊测试期间的代码覆盖率有两个关键目的：

1. **评估 harness 的有效性**：了解您的模糊测试 harness 实际上执行了应用程序的哪些部分
2. **跟踪模糊测试进度**：监控在更新 harness、模糊器或系统在测试 (SUT) 时覆盖率的变化

覆盖率是模糊器能力和性能的代理。虽然覆盖率在绝对意义上[并非理想用于衡量模糊器性能](https://arxiv.org/abs/1808.09700)，但它可靠地指示您的 harness 在特定设置中是否有效工作。

### 关键概念

| 概念 | 描述 |
|---------|-------------|
| **覆盖率插桩** | 跟踪哪些代码路径被执行的编译器标志 |
| **语料库覆盖率** | 运行模糊测试语料库中所有测试用例所达到的覆盖率 |
| **魔法值检查** | 难以发现的条件检查，会阻塞模糊器进度 |
| **覆盖率引导模糊测试** | 优先考虑发现新代码路径的输入的模糊测试策略 |
| **覆盖率报告** | 已执行代码与未执行代码的可视化或文本表示 |

## 何时应用

**在以下情况下应用此技术：**
- 开始新的模糊测试活动以建立基线
- 模糊器似乎停滞不前而未发现新路径
- harness 修改后验证改进
- 在不同的模糊器之间迁移时
- 确定需要字典条目或种子输入的领域
- 调试为什么某些代码路径未被访问

**在以下情况下跳过此技术：**
- 模糊测试活动正在主动发现崩溃
- 覆盖率基础设施尚未设置
- 与极大型代码库一起工作，其中完整的覆盖率报告不切实际
- 模糊器的内部覆盖率指标足以满足您的需求

## 快速参考

| 任务 | 命令/模式 |
|------|-----------------|
| LLVM 覆盖率插桩 (C/C++) | `-fprofile-instr-generate -fcoverage-mapping` |
| GCC 覆盖率插桩 | `-ftest-coverage -fprofile-arcs` |
| cargo-fuzz 覆盖率 (Rust) | `cargo +nightly fuzz coverage <target>` |
| 生成 LLVM 配置文件数据 | `llvm-profdata merge -sparse file.profraw -o file.profdata` |
| LLVM 覆盖率报告 | `llvm-cov report ./binary -instr-profile=file.profdata` |
| LLVM HTML 报告 | `llvm-cov show ./binary -instr-profile=file.profdata -format=html -output-dir html/` |
| gcovr HTML 报告 | `gcovr --html-details -o coverage.html` |

## 理想的覆盖率工作流程

以下工作流程代表了将覆盖率分析集成到您的模糊测试活动中的最佳实践：

```
[Fuzzing Campaign]
       |
       v
[Generate Corpus]
       |
       v
[Coverage Analysis]
       |
       +---> 覆盖率增加？ --> 使用更大的语料库继续模糊测试
       |
       +---> 覆盖率减少？ --> 修复 harness 或调查 SUT 变化
       |
       +---> 覆盖率停滞？ --> 添加字典条目或种子输入
```

**关键原则**：使用每次模糊测试活动后生成的语料库来计算覆盖率，而不是实时模糊器统计信息。这种方法提供可重复的、可比较的测量结果，适用于不同的模糊测试工具。

## 分步指南

### 第 1 步：使用覆盖率插桩构建

根据工具链选择您的插桩方法：

**LLVM/Clang (C/C++)：**
```bash
clang++ -fprofile-instr-generate -fcoverage-mapping \
  -O2 -DNO_MAIN \
  main.cc harness.cc execute-rt.cc -o fuzz_exec
```

**GCC (C/C++)：**
```bash
g++ -ftest-coverage -fprofile-arcs \
  -O2 -DNO_MAIN \
  main.cc harness.cc execute-rt.cc -o fuzz_exec_gcov
```

**Rust：**
```bash
rustup toolchain install nightly --component llvm-tools-preview
cargo +nightly fuzz coverage fuzz_target_1
```

### 第 2 步：创建执行运行时 (C/C++ 仅限)

对于 C/C++ 项目，创建一个执行您的语料库的运行时：

```cpp
// execute-rt.cc
#include <stdio.h>
#include <stdlib.h>
#include <dirent.h>
#include <stdint.h>

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size);

void load_file_and_test(const char *filename) {
    FILE *file = fopen(filename, "rb");
    if (file == NULL) {
        printf("Failed to open file: %s\n", filename);
        return;
    }

    fseek(file, 0, SEEK_END);
    long filesize = ftell(file);
    rewind(file);

    uint8_t *buffer = (uint8_t*) malloc(filesize);
    if (buffer == NULL) {
        printf("Failed to allocate memory for file: %s\n", filename);
        fclose(file);
        return;
    }

    long read_size = (long) fread(buffer, 1, filesize, file);
    if (read_size != filesize) {
        printf("Failed to read file: %s\n", filename);
        free(buffer);
        fclose(file);
        return;
    }

    LLVMFuzzerTestOneInput(buffer, filesize);

    free(buffer);
    fclose(file);
}

int main(int argc, char **argv) {
    if (argc != 2) {
        printf("Usage: %s <directory>\n", argv[0]);
        return 1;
    }

    DIR *dir = opendir(argv[1]);
    if (dir == NULL) {
        printf("Failed to open directory: %s\n", argv[1]);
        return 1;
    }

    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        if (entry->d_type == DT_REG) {
            char filepath[1024];
            snprintf(filepath, sizeof(filepath), "%s/%s", argv[1], entry->d_name);
            load_file_and_test(filepath);
        }
    }

    closedir(dir);
    return 0;
}
```

### 第 3 步：在语料库上执行

**LLVM (C/C++)：**
```bash
LLVM_PROFILE_FILE=fuzz.profraw ./fuzz_exec corpus/
```

**GCC (C/C++)：**
```bash
./fuzz_exec_gcov corpus/
```

**Rust：**
覆盖率数据在运行 `cargo fuzz coverage` 时自动生成。

### 第 4 步：处理覆盖率数据

**LLVM：**
```bash
# 合并原始配置文件数据
llvm-profdata merge -sparse fuzz.profraw -o fuzz.profdata

# 生成文本报告
llvm-cov report ./fuzz_exec \
  -instr-profile=fuzz.profdata \
  -ignore-filename-regex='harness.cc|execute-rt.cc'

# 生成 HTML 报告
llvm-cov show ./fuzz_exec \
  -instr-profile=fuzz.profdata \
  -ignore-filename-regex='harness.cc|execute-rt.cc' \
  -format=html -output-dir fuzz_html/
```

**GCC with gcovr：**
```bash
# 安装 gcovr (uv 管理隔离环境)
uv tool install gcovr
export PATH="$HOME/.local/bin:$PATH"   # uv 的工具 bin，如果尚未存在

# 生成报告
gcovr --gcov-executable "llvm-cov gcov" \
  --exclude harness.cc --exclude execute-rt.cc \
  --root . --html-details -o coverage.html
```

**Rust：**
```bash
# 安装所需工具
cargo install cargo-binutils rustfilt

# 创建 HTML 生成脚本
cat <<'EOF' > ./generate_html
#!/bin/sh
if [ $# -lt 1 ]; then
    echo "Error: Name of fuzz target is required."
    echo "Usage: $0 fuzz_target [sources...]"
    exit 1
fi
FUZZ_TARGET="$1"
shift
SRC_FILTER="$@"
TARGET=$(rustc -vV | sed -n 's|host: ||p')
cargo +nightly cov -- show -Xdemangler=rustfilt \
  "target/$TARGET/coverage/$TARGET/release/$FUZZ_TARGET" \
  -instr-profile="fuzz/coverage/$FUZZ_TARGET/coverage.profdata" \
  -show-line-counts-or-regions -show-instantiations \
  -format=html -o fuzz_html/ $SRC_FILTER
EOF
chmod +x ./generate_html

# 生成 HTML 报告
./generate_html fuzz_target_1 src/lib.rs
```

### 第 5 步：分析结果

查看覆盖率报告以识别：

- **未覆盖的代码块**：可能需要更好的种子输入或字典条目
- **魔法值检查**：具有硬编码值的条件语句，会阻塞进度
- **死代码**：可能无法通过您的 harness 访问的函数
- **覆盖率变化**：与基线比较以跟踪改进或退化

## 常见模式

### 模式：识别魔法值

**问题**：模糊器无法发现受魔法值检查保护的路径。

**覆盖率显示：**
```cpp
// 覆盖率显示此块从未被执行
if (buf == 0x7F454C46) {  // ELF 魔法数字
    // 开始解析 buf
}
```

**解决方案**：将魔法值添加到字典文件：
```
# magic.dict
"\x7F\x45\x4C\x46"
```

### 模式：处理崩溃输入

**问题**：覆盖率生成在语料库包含崩溃输入时失败。

**之前：**
```bash
./fuzz_exec corpus/  # 坏输入导致崩溃，未生成覆盖率
```

**之后：**
```cpp
// 使用分叉来隔离崩溃
int main(int argc, char **argv) {
    // ... 打开目录代码 ...

    while ((entry = readdir(dir)) != NULL) {
        if (entry->d_type == DT_REG) {
            pid_t pid = fork();
            if (pid == 0) {
                // 子进程 - 崩溃不会影响父进程
                char filepath[1024];
                snprintf(filepath, sizeof(filepath), "%s/%s", argv[1], entry->d_name);
                load_file_and_test(filepath);
                exit(0);
            } else {
                // 父进程等待子进程
                waitpid(pid, NULL, 0);
            }
        }
    }
}
```

### 模式：CMake 集成

**用例**：将覆盖率构建添加到 CMake 项目。

```cmake
project(FuzzingProject)
cmake_minimum_required(VERSION 3.0)

# 主二进制文件
add_executable(program main.cc)

# 模糊测试二进制文件
add_executable(fuzz main.cc harness.cc)
target_compile_definitions(fuzz PRIVATE NO_MAIN=1)
target_compile_options(fuzz PRIVATE -g -O2 -fsanitize=fuzzer)
target_link_libraries(fuzz -fsanitize=fuzzer)

# 覆盖率执行二进制文件
add_executable(fuzz_exec main.cc harness.cc execute-rt.cc)
target_compile_definitions(fuzz_exec PRIVATE NO_MAIN)
target_compile_options(fuzz_exec PRIVATE -O2 -fprofile-instr-generate -fcoverage-mapping)
target_link_libraries(fuzz_exec -fprofile-instr-generate)
```

构建：
```bash
cmake -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ .
cmake --build . --target fuzz_exec
```

## 高级用法

### 提示和技巧

| 提示 | 它如何帮助 |
|-----|--------------|
| 使用 LLVM 18+ 与 `-show-directory-coverage` | 将大型报告按目录结构组织，而不是扁平文件列表 |
| 导出为 lcov 格式以获得更好的 HTML | `llvm-cov export -format=lcov` + `genhtml` 提供更清晰的每个文件报告 |
| 比较跨活动覆盖率 | 存储带有时间戳的 `.profdata` 文件以跟踪随时间的进度 |
| 从报告中过滤 harness 代码 | 使用 `-ignore-filename-regex` 仅关注 SUT 覆盖率 |
| 在 CI/CD 中自动化覆盖率 | 在计划的模糊测试运行后自动生成覆盖率报告 |
| 使用 gcovr 5.1+ 与 Clang 14+ | 较旧的 gcovr 版本与最新的 LLVM 存在兼容性问题 |

### 增量覆盖率更新

GCC 的 gcov 插桩跨多次运行增量更新 `.gcda` 文件。这对于跟踪添加测试用例时的覆盖率很有用：

```bash
# 第一次运行
./fuzz_exec_gcov corpus_batch_1/
gcovr --html coverage_v1.html

# 第二次运行（添加到现有覆盖率）
./fuzz_exec_gcov corpus_batch_2/
gcovr --html coverage_v2.html

# 重新开始
gcovr --delete  # 删除 .gcda 文件
./fuzz_exec_gcov corpus/
```

### 处理大型代码库

对于具有数百个源文件的项目：

1. **按前缀过滤**：仅生成相关目录的报告
   ```bash
   llvm-cov show ./fuzz_exec -instr-profile=fuzz.profdata /path/to/src/
   ```

2. **使用目录覆盖率**：按目录分组以减少混乱（LLVM 18+）
   ```bash
   llvm-cov show -show-directory-coverage -format=html -output-dir html/
   ```

3. **生成 JSON 以进行程序分析**：
   ```bash
   llvm-cov export -format=lcov > coverage.json
   ```

### 差异覆盖率

比较两个模糊测试活动之间的覆盖率：

```bash
# 活动 1
LLVM_PROFILE_FILE=campaign1.profraw ./fuzz_exec corpus1/
llvm-profdata merge -sparse campaign1.profraw -o campaign1.profdata

# 活动 2
LLVM_PROFILE_FILE=campaign2.profraw ./fuzz_exec corpus2/
llvm-profdata merge -sparse campaign2.profraw -o campaign2.profdata

# 比较
llvm-cov show ./fuzz_exec \
  -instr-profile=campaign2.profdata \
  -instr-profile=campaign1.profdata \
  -show-line-counts-or-regions
```

## 反模式

| 反模式 | 问题 | 正确方法 |
|--------------|---------|------------------|
| 使用模糊器报告的覆盖率进行比较 | 不同的模糊器计算覆盖率的方式不同，使得跨工具比较没有意义 | 使用专用的覆盖率工具 (llvm-cov, gcovr) 进行可重复的测量 |
| 使用优化生成覆盖率 | `-O3` 优化可能会消除代码，使覆盖率具有误导性 | 使用 `-O2` 或 `-O0` 进行覆盖率构建 |
| 不过滤 harness 代码 | harness 覆盖率会虚增数字并掩盖 SUT 覆盖率 | 使用 `-ignore-filename-regex` 或 `--exclude` 过滤 harness 文件 |
| 混合 LLVM 和 GCC 插桩 | 不兼容的格式会导致解析失败 | 坚持使用一个工具链进行覆盖率构建 |
| 忽略崩溃输入 | 崩溃会阻止覆盖率生成，隐藏真实的覆盖率数据 | 首先修复崩溃，或者使用进程分叉来隔离它们 |
| 不跟踪覆盖率随时间变化 | 一次性覆盖率检查会错过回归和改进 | 存储带有时间戳的覆盖率数据并跟踪趋势 |

## 工具特定指南

### libFuzzer

libFuzzer 默认使用 LLVM 的 SanitizerCoverage 进行引导模糊测试，但您需要单独的插桩来生成报告。

**构建用于覆盖率：**
```bash
clang++ -fprofile-instr-generate -fcoverage-mapping \
  -O2 -DNO_MAIN \
  main.cc harness.cc execute-rt.cc -o fuzz_exec
```

**执行语料库并生成报告：**
```bash
LLVM_PROFILE_FILE=fuzz.profraw ./fuzz_exec corpus/
llvm-profdata merge -sparse fuzz.profraw -o fuzz.profdata
llvm-cov show ./fuzz_exec -instr-profile=fuzz.profdata -format=html -output-dir html/
```

**集成提示：**
- 不要在覆盖率构建中使用 `-fsanitize=fuzzer`（它与配置文件插桩冲突）
- 使用不同的 main 函数重用相同的 harness 函数 (`LLVMFuzzerTestOneInput`)
- 使用 `-ignore-filename-regex` 标志从覆盖率报告中排除 harness 代码
- 考虑使用 llvm-cov 的 `-show-instantiation` 标志用于模板密集型 C++ 代码

### AFL++

AFL++ 提供了自己的覆盖率反馈机制，但用于详细报告请使用标准的 LLVM/GCC 工具。

**使用 LLVM 构建用于覆盖率：**
```bash
clang++ -fprofile-instr-generate -fcoverage-mapping \
  -O2 main.cc harness.cc execute-rt.cc -o fuzz_exec
```

**使用 GCC 构建用于覆盖率：**
```bash
AFL_USE_ASAN=0 afl-gcc -ftest-coverage -fprofile-arcs \
  main.cc harness.cc execute-rt.cc -o fuzz_exec_gcov
```

**执行并生成报告：**
```bash
# LLVM 方法
LLVM_PROFILE_FILE=fuzz.profraw ./fuzz_exec afl_output/queue/
llvm-profdata merge -sparse fuzz.profraw -o fuzz.profdata
llvm-cov report ./fuzz_exec -instr-profile=fuzz.profdata

# GCC 方法
./fuzz_exec_gcov afl_output/queue/
gcovr --html-details -o coverage.html
```

**集成提示：**
- 不要使用 AFL++ 的插桩 (`afl-clang-fast`) 进行覆盖率构建
- 使用标准的编译器和覆盖率标志
- AFL++ 的 `queue/` 目录包含您的语料库
- AFL++ 的内置覆盖率统计对于实时监控很有用，但不适用于详细分析

### cargo-fuzz (Rust)

cargo-fuzz 提供了内置的覆盖率生成，使用 LLVM 工具。

**安装先决条件：**
```bash
rustup toolchain install nightly --component llvm-tools-preview
cargo install cargo-binutils rustfilt
```

**生成覆盖率数据：**
```bash
cargo +nightly fuzz coverage fuzz_target_1
```

**创建 HTML 报告脚本：**
```bash
cat <<'EOF' > ./generate_html
#!/bin/sh
FUZZ_TARGET="$1"
shift
SRC_FILTER="$@"
TARGET=$(rustc -vV | sed -n 's|host: ||p')
cargo +nightly cov -- show -Xdemangler=rustfilt \
  "target/$TARGET/coverage/$TARGET/release/$FUZZ_TARGET" \
  -instr-profile="fuzz/coverage/$FUZZ_TARGET/coverage.profdata" \
  -show-line-counts-or-regions -show-instantiations \
  -format=html -o fuzz_html/ $SRC_FILTER
EOF
chmod +x ./generate_html
```

**生成报告：**
```bash
./generate_html fuzz_target_1 src/lib.rs
```

**集成技巧：**
- 始终使用 nightly 工具链进行覆盖率分析
- `-Xdemangler=rustfilt` 标志可以使函数名称可读
- 通过源文件（例如 `src/lib.rs`）进行过滤，以专注于 crate 代码
- 使用 `-show-line-counts-or-regions` 和 `-show-instantiations` 获取更好的 Rust 特定输出
- 测试用例位于 `fuzz/corpus/<目标>/`

### honggfuzz

honggfuzz 与标准 LLVM/GCC 覆盖率分析工具兼容。

**为覆盖率构建：**
```bash
# 使用标准编译器，而不是 honggfuzz 编译器
clang -fprofile-instr-generate -fcoverage-mapping \
  -O2 harness.c execute-rt.c -o fuzz_exec
```

**执行测试用例：**
```bash
LLVM_PROFILE_FILE=fuzz.profraw ./fuzz_exec honggfuzz_workspace/
```

**集成技巧：**
- 不要使用 `hfuzz-clang` 进行覆盖率构建
- honggfuzz 测试用例通常位于工作区目录
- 使用与 libFuzzer 相同的 LLVM 工作流程

## 故障排除

| 问题 | 原因 | 解决方案 |
|-------|-------|----------|
| `error: no profile data available` | 未生成分析数据或路径错误 | 确认 `LLVM_PROFILE_FILE` 是否设置且 `.profraw` 文件存在 |
| `Failed to load coverage` | 二进制文件与分析数据不匹配 | 使用与执行时相同标志重新构建二进制文件 |
| 覆盖率报告显示 0% | 用于报告生成的二进制文件不正确 | 使用分析过的二进制文件，而不是模糊测试二进制文件 |
| `no_working_dir_found` 错误 (gcovr) | `.gcda` 文件位于预期位置之外 | 添加 `--gcov-ignore-errors=no_working_dir_found` 标志 |
| 断言阻止覆盖率生成 | 测试用例包含导致崩溃的输入 | 过滤断言或使用分叉方法隔离失败 |
| 覆盖率在 harness 更改后降低 | harness 现在跳过某些代码路径 | 审查 harness 逻辑；可能需要支持更多输入格式 |
| HTML 报告是扁平文件列表 | 使用较旧的 LLVM 版本 | 升级到 LLVM 18+ 并使用 `-show-directory-coverage` |
| `incompatible instrumentation` | 混合 LLVM 和 GCC 覆盖率 | 使用相同工具链重新构建所有内容 |

## 相关技能

### 使用该技术的工具

| 技能 | 应用方式 |
|-------|----------------|
| **libfuzzer** | 使用 SanitizerCoverage 进行反馈；覆盖率分析评估 harness 效果 |
| **aflpp** | 使用边缘覆盖率进行反馈；详细分析需要单独的覆盖率分析 |
| **cargo-fuzz** | Rust 项目的内置 `cargo fuzz coverage` 命令 |
| **honggfuzz** | 使用边缘覆盖率；使用标准 LLVM/GCC 工具分析 |

### 相关技术

| 技能 | 关系 |
|-------|--------------|
| **fuzz-harness-writing** | 覆盖率显示 harness 到达的代码路径；指导 harness 改进 |
| **fuzzing-dictionaries** | 覆盖率识别需要字典条目的魔法值检查 |
| **corpus-management** | 覆盖率分析通过识别冗余测试用例帮助管理测试用例库 |
| **sanitizers** | 覆盖率验证 sanitizer 分析的代码是否实际执行 |

## 资源

### 关键外部资源

**[基于源代码的 LLVM 覆盖率](https://clang.llvm.org/docs/SourceBasedCodeCoverage.html)**
LLVM 的分析数据的全面指南，包括分支覆盖率、区域覆盖率和与现有构建系统的集成等高级功能。涵盖编译器标志、运行时行为和配置数据格式。

**[llvm-cov 命令指南](https://llvm.org/docs/CommandGuide/llvm-cov.html)**
`show`、`report` 和 `export` 等 llvm-cov 命令的详细 CLI 参考。记录所有过滤选项、输出格式以及与 llvm-profdata 的集成。

**[gcovr 文档](https://gcovr.com/)**
用于从 gcov 数据生成覆盖率报告的完整指南。涵盖 HTML 主题、过滤选项、多目录项目和 CI/CD 集成模式。

**[SanitizerCoverage 文档](https://clang.llvm.org/docs/SanitizerCoverage.html)**
LLVM 的 SanitizerCoverage 分析数据的低级文档。解释了内联 8 位计数器、PC 表以及模糊测试如何使用覆盖率反馈进行指导。

**[模糊测试性能评估](https://arxiv.org/abs/1808.09700)**
研究论文，探讨覆盖率作为模糊测试性能指标的局限性。主张使用比简单的代码覆盖率百分比更细致的评估方法。

### 视频资源

不适用 - 覆盖率分析主要是工具和工作流程主题，最佳学习方式是通过文档和实际操作练习。
