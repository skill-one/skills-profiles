# LibAFL

LibAFL 是一个模块化的模糊测试库，实现了 AFL++ 等基于 AFL 的模糊测试器中的功能。与传统的模糊测试器不同，LibAFL 以 Rust 库的形式提供所有功能，并以模块化和可定制的方式实现。它可以用作 libFuzzer 的即插即用替代品，或作为从头开始构建自定义模糊测试器的库。

## 使用场景

| 模糊测试器 | 最适合 | 复杂度 |
|--------|----------|------------|
| libFuzzer | 快速设置，单线程 | 低 |
| AFL++ | 多核，通用 | 中等 |
| LibAFL | 自定义模糊测试器，高级功能，研究 | 高 |

**选择 LibAFL 的情况：**
- 您需要自定义变异策略或反馈机制
- 标准模糊测试器不支持您的目标架构
- 您想实现新的模糊测试技术
- 您需要对模糊测试组件进行细粒度控制
- 您正在进行模糊测试研究

## 快速入门

LibAFL 可以用作 libFuzzer 的即插即用替代品，只需进行最小的设置：

```c++
extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    // 使用模糊测试器提供的数据调用您的代码
    my_function(data, size);
    return 0;
}
```

构建 LibAFL 的 libFuzzer 兼容层：
```bash
git clone https://github.com/AFLplusplus/LibAFL
cd LibAFL/libafl_libfuzzer_runtime
./build.sh
```

编译和运行：
```bash
clang++ -DNO_MAIN -g -O2 -fsanitize=fuzzer-no-link libFuzzer.a harness.cc main.cc -o fuzz
./fuzz corpus/
```

## 安装

### 前置条件

- Clang/LLVM 15-18
- Rust (通过 rustup 安装)
- 额外的系统依赖项

### Linux/macOS

安装 Clang：
```bash
apt install clang
```

或者通过 apt.llvm.org 安装特定版本：
```bash
wget https://apt.llvm.org/llvm.sh
chmod +x llvm.sh
sudo ./llvm.sh 15
```

配置 Rust 环境：
```bash
export RUSTFLAGS="-C linker=/usr/bin/clang-15"
export CC="clang-15"
export CXX="clang++-15"
```

安装 Rust：
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

安装额外的依赖项：
```bash
apt install libssl-dev pkg-config
```

对于 libFuzzer 兼容模式，安装 nightly Rust：
```bash
rustup toolchain install nightly --component llvm-tools
```

### 验证

构建 LibAFL 以验证安装：
```bash
cd LibAFL/libafl_libfuzzer_runtime
./build.sh
# 应该生成 libFuzzer.a
```

## 编写测试框架

LibAFL 测试框架在使用即插即用替换模式时，与 libFuzzer 的模式相同：

```c++
extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    // 您的模糊测试目标代码在这里
    return 0;
}
```

当使用 LibAFL 作为 Rust 库构建自定义模糊测试器时，测试框架逻辑直接集成到模糊测试器中。有关完整模式，请参阅下文“编写自定义模糊测试器”部分。

> **另见：** 有关详细的测试框架编写技术，请参阅 **harness-writing** 技术技能。

## 使用模式

LibAFL 支持两种主要的使用模式：

### 1. libFuzzer 即插即用替换

使用 LibAFL 作为 libFuzzer 的替代品，并使用现有的测试框架。

**编译：**
```bash
clang++ -DNO_MAIN -g -O2 -fsanitize=fuzzer-no-link libFuzzer.a harness.cc main.cc -o fuzz
```

**运行：**
```bash
./fuzz corpus/
```

**推荐用于长时间运行：**
```bash
./fuzz -fork=1 -ignore_crashes=1 corpus/
```

### 2. 作为 Rust 库的自定义模糊测试器

使用 LibAFL 组件构建完全自定义的模糊测试器。

**创建项目：**
```bash
cargo init --lib my_fuzzer
cd my_fuzzer
cargo add libafl@0.13 libafl_targets@0.13 libafl_bolts@0.13 libafl_cc@0.13 \
  --features "libafl_targets@0.13/libfuzzer,libafl_targets@0.13/sancov_pcguard_hitcounts"
```

**配置 Cargo.toml：**
```toml
[lib]
crate-type = ["staticlib"]
```

## 编写自定义模糊测试器

> **另见：** 有关详细的测试框架编写技术、处理复杂输入的模式和高级策略，请参阅 **fuzz-harness-writing** 技术技能。

### 模糊测试器组件

LibAFL 模糊测试器由模块化组件组成：

1. **观察者** - 收集执行反馈（覆盖率、时间）
2. **反馈** - 确定输入是否有趣
3. **目标** - 定义模糊测试目标（崩溃、超时）
4. **状态** - 维护语料库和元数据
5. **变异器** - 生成新输入
6. **调度器** - 选择要变异的输入
7. **执行器** - 使用输入运行目标

### 基本模糊测试器结构

```rust
use libafl::prelude::*;
use libafl_bolts::prelude::*;
use libafl_targets::{libfuzzer_test_one_input, std_edges_map_observer};

#[no_mangle]
pub extern "C" fn libafl_main() {
    let mut run_client = |state: Option<_>, mut restarting_mgr, _core_id| {
        // 1. 设置观察者
        let edges_observer = HitcountsMapObserver::new(
            unsafe { std_edges_map_observer("edges") }
        ).track_indices();
        let time_observer = TimeObserver::new("time");

        // 2. 定义反馈
        let mut feedback = feedback_or!(
            MaxMapFeedback::new(&edges_observer),
            TimeFeedback::new(&time_observer)
        );

        // 3. 定义目标
        let mut objective = feedback_or_fast!(
            CrashFeedback::new(),
            TimeoutFeedback::new()
        );

        // 4. 创建或恢复状态
        let mut state = state.unwrap_or_else(|| {
            StdState::new(
                StdRand::new(),
                InMemoryCorpus::new(),
                OnDiskCorpus::new(&output_dir).unwrap(),
                &mut feedback,
                &mut objective,
            ).unwrap()
        });

        // 5. 设置变异器
        let mutator = StdScheduledMutator::new(havoc_mutations());
        let mut stages = tuple_list!(StdMutationalStage::new(mutator));

        // 6. 设置调度器
        let scheduler = IndexesLenTimeMinimizerScheduler::new(
            &edges_observer,
            QueueScheduler::new()
        );

        // 7. 创建模糊测试器
        let mut fuzzer = StdFuzzer::new(scheduler, feedback, objective);

        // 8. 定义测试框架
        let mut harness = |input: &BytesInput| {
            let buf = input.target_bytes().as_slice();
            libfuzzer_test_one_input(buf);
            ExitKind::Ok
        };

        // 9. 设置执行器
        let mut executor = InProcessExecutor::with_timeout(
            &mut harness,
            tuple_list!(edges_observer, time_observer),
            &mut fuzzer,
            &mut state,
            &mut restarting_mgr,
            timeout,
        )?;

        // 10. 加载初始输入
        if state.must_load_initial_inputs() {
            state.load_initial_inputs(
                &mut fuzzer,
                &mut executor,
                &mut restarting_mgr,
                &input_dir
            )?;
        }

        // 11. 开始模糊测试
        fuzzer.fuzz_loop(&mut stages, &mut executor, &mut state, &mut restarting_mgr)?;
        Ok(())
    };

    // 启动模糊测试器
    Launcher::builder()
        .run_client(&mut run_client)
        .cores(&cores)
        .build()
        .launch()
        .unwrap();
}
```

## 编译

### 详细模式

手动指定所有仪器标志：

```bash
clang++-15 -DNO_MAIN -g -O2 \
  -fsanitize-coverage=trace-pc-guard \
  -fsanitize=address \
  -Wl,--whole-archive target/release/libmy_fuzzer.a -Wl,--no-whole-archive \
  main.cc harness.cc -o fuzz
```

### 编译器包装（推荐）

创建一个 LibAFL 编译器包装器来自动处理仪器。

**创建 `src/bin/libafl_cc.rs`：**
```rust
use libafl_cc::{ClangWrapper, CompilerWrapper, Configuration, ToolWrapper};

pub fn main() {
    let args: Vec<String> = env::args().collect();
    let mut cc = ClangWrapper::new();
    cc.cpp(is_cpp)
      .parse_args(&args)
      .link_staticlib(&dir, "my_fuzzer")
      .add_args(&Configuration::GenerateCoverageMap.to_flags().unwrap())
      .add_args(&Configuration::AddressSanitizer.to_flags().unwrap())
      .run()
      .unwrap();
}
```

**编译和使用：**
```bash
cargo build --release
target/release/libafl_cxx -DNO_MAIN -g -O2 main.cc harness.cc -o fuzz
```

> **另见：** 有关详细的 sanitizer 配置、常见问题和高级标志，请参阅 **address-sanitizer** 和 **undefined-behavior-sanitizer** 技术技能。

## 运行测试活动

### 基本运行

```bash
./fuzz --cores 0 --input corpus/
```

### 多核模糊测试

```bash
./fuzz --cores 0,8-15 --input corpus/
```

这将在核心 0 上运行 9 个客户端：一个在核心 0 上，8 个在核心 8-15 上。

### 带选项

```bash
./fuzz --cores 0-7 --input corpus/ --output crashes/ --timeout 1000
```

### 文本用户界面 (TUI)

启用图形统计视图：

```bash
./fuzz -tui=1 corpus/
```

### 解释输出

| 输出 | 含义 |
|--------|---------|
| `corpus: N` | 找到的有趣测试用例数量 |
| `objectives: N` | 找到的崩溃/超时数量 |
| `executions: N` | 目标总调用次数 |
| `exec/sec: N` | 当前执行吞吐量 |
| `edges: X%` | 代码覆盖率百分比 |
| `clients: N` | 并行模糊测试进程数量 |

模糊测试器发出两种主要事件类型：
- **UserStats** - 定期心跳，包含当前统计信息
- **Testcase** - 发现新的有趣输入

## 高级用法

### 提示和技巧

| 提示 | 它如何帮助 |
|-----|--------------|
| 使用 `-fork=1 -ignore_crashes=1` | 崩溃后继续模糊测试 |
| 使用 `InMemoryOnDiskCorpus` | 跨重启持久化语料库 |
| 使用 `-tui=1` 启用 TUI | 更好地可视化进度 |
| 使用特定的 LLVM 版本 | 避免兼容性问题 |
| 正确设置 `RUSTFLAGS` | 防止链接错误 |

### 崩溃去重

避免从同一错误存储重复的崩溃：

**添加回溯观察者：**
```rust
let backtrace_observer = BacktraceObserver::owned(
    "BacktraceObserver",
    libafl::observers::HarnessType::InProcess
);
```

**更新执行器：**
```rust
let mut executor = InProcessExecutor::with_timeout(
    &mut harness,
    tuple_list!(edges_observer, time_observer, backtrace_observer),
    &mut fuzzer,
    &mut state,
    &mut restarting_mgr,
    timeout,
)?;
```

**使用哈希反馈更新目标：**
```rust
let mut objective = feedback_and!(
    feedback_or_fast!(CrashFeedback::new(), TimeoutFeedback::new()),
    NewHashFeedback::new(&backtrace_observer)
);
```

这确保仅保存具有唯一回溯的崩溃。

### 字典模糊测试

使用字典引导模糊测试到特定标记：

**从文件添加标记：**
```rust
let mut tokens = Tokens::new();
if let Some(tokenfile) = &tokenfile {
    tokens.add_from_file(tokenfile)?;
}
state.add_metadata(tokens);
```

**更新变异器：**
```rust
let mutator = StdScheduledMutator::new(
    havoc_mutations().merge(tokens_mutations())
);
```

**硬编码标记示例（PNG）：**
```rust
state.add_metadata(Tokens::from([
    vec![137, 80, 78, 71, 13, 10, 26, 10], // PNG 标头
    "IHDR".as_bytes().to_vec(),
    "IDAT".as_bytes().to_vec(),
    "PLTE".as_bytes().to_vec(),
    "IEND".as_bytes().to_vec(),
]));
```

> **另见：** 有关详细的字典创建策略和特定格式的字典，请参阅 **fuzzing-dictionaries** 技术技能。

### 自动标记

自动从程序中提取魔法值和校验和：

**在编译器包装中启用：**
```rust
cc.add_pass(LLVMPasses::AutoTokens)
```

**在模糊测试器中加载自动标记：**
```rust
tokens += libafl_targets::autotokens()?;
```

**验证标记部分：**
```bash
echo "p (uint8_t *)__token_start" | gdb fuzz
```

### 性能调优

| 设置 | 影响 |
|---------|--------|
| 多核模糊测试 | 核心数线性加速 |
| `InMemoryCorpus` | 更快但非持久 |
| `InMemoryOnDiskCorpus` | 速度和持久性之间的平衡 |
| Sanitizers | 2-5x 减慢，对于发现错误是必要的 |
| 优化级别 `-O2` | 速度和覆盖率之间的平衡 |

### 调试模糊测试器

以单进程模式运行模糊测试器以便于调试：

```rust
// 用直接调用替换启动器
run_client(None, SimpleEventManager::new(monitor), 0).unwrap();

// 注释掉：
// Launcher::builder()
//     .run_client(&mut run_client)
//     ...
//     .launch()
```

然后使用 GDB 调试：
```bash
gdb --args ./fuzz --cores 0 --input corpus/
```

## 真实世界示例

### 示例：libpng

使用 LibAFL 模糊测试 libpng：

**1. 获取源代码：**
```bash
curl -L -O https://downloads.sourceforge.net/project/libpng/libpng16/1.6.37/libpng-1.6.37.tar.xz
tar xf libpng-1.6.37.tar.xz
cd libpng-1.6.37/
apt install zlib1g-dev
```

**2. 设置编译器包装器：**
```bash
export FUZZER_CARGO_DIR="/path/to/libafl/project"
export CC=$FUZZER_CARGO_DIR/target/release/libafl_cc
export CXX=$FUZZER_CARGO_DIR/target/release/libafl_cxx
```

**3. 构建静态库：**
```bash
./configure --enable-shared=no
make
```

**4. 获取测试框架：**
```bash
curl -O https://raw.githubusercontent.com/glennrp/libpng/f8e5fa92b0e37ab597616f554bee254157998227/contrib/oss-fuzz/libpng_read_fuzzer.cc
```

**5. 链接模糊测试器：**
```bash
$CXX libpng_read_fuzzer.cc .libs/libpng16.a -lz -o fuzz
```

**6. 准备种子：**
```bash
mkdir seeds/
curl -o seeds/input.png https://raw.githubusercontent.com/glennrp/libpng/acfd50ae0ba3198ad734e5d4dec2b05341e50924/contrib/pngsuite/iftp1n3p08.png
```

**7. 获取字典（可选）：**
```bash
curl -O https://raw.githubusercontent.com/glennrp/libpng/2fff013a6935967960a5ae626fc21432807933dd/contrib/oss-fuzz/png.dict
```

**8. 开始模糊测试：**
```bash
./fuzz --input seeds/ --cores 0 -x png.dict
```

### 示例：CMake 项目

将 LibAFL 集成到 CMake 构建系统中：

**CMakeLists.txt：**
```cmake
project(BuggyProgram)
cmake_minimum_required(VERSION 3.0)

add_executable(buggy_program main.cc)

add_executable(fuzz main.cc harness.cc)
target_compile_definitions(fuzz PRIVATE NO_MAIN=1)
target_compile_options(fuzz PRIVATE -g -O2)
```

**构建非仪器化二进制文件：**
```bash
cmake -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++ .
cmake --build . --target buggy_program
```

**构建模糊测试器：**
```bash
export FUZZER_CARGO_DIR="/path/to/libafl/project"
cmake -DCMAKE_C_COMPILER=$FUZZER_CARGO_DIR/target/release/libafl_cc \
      -DCMAKE_CXX_COMPILER=$FUZZER_CARGO_DIR/target/release/libafl_cxx .
cmake --build . --target fuzz
```

**运行模糊测试：**
```bash
./fuzz --input seeds/ --cores 0
```

## 故障排除

| 问题 | 原因 | 解决方案 |
|---------|-------|----------|
| 没有覆盖率增加 | 仪器化失败 | 验证使用的编译器包装器，检查 `-fsanitize-coverage` |
| 模糊测试器无法启动 | 空语料库且没有有趣的输入 | 提供触发代码路径的种子输入 |
| 使用 `libafl_main` 的链接器错误 | 未链接运行时 | 使用 `-Wl,--whole-archive` 或 `-u libafl_main` |
| LLVM 版本不匹配 | LibAFL 需要 LLVM 15-18 | 安装兼容的 LLVM 版本，设置环境变量 |
| Rust 编译失败 | 过时的 Rust 或 Cargo | 使用 `rustup update` 更新 Rust |
| 模糊测试速度慢 | 启用了 Sanitizers | 预期 2-5x 减慢，对于发现错误是必要的 |
| 环境变量干扰 | 设置了 `CC`、`CXX`、`RUSTFLAGS` | 构建完 LibAFL 项目后清除 |
| 无法附加调试器 | 多进程模糊测试 | 以单进程模式运行（见调试部分） |

## 相关技能

### 技术技能

| 技能 | 用例 |
|-------|----------|
| **fuzz-harness-writing** | 编写有效测试框架的详细指导 |
| **address-sanitizer** | 模糊测试期间的内存错误检测 |
| **undefined-behavior-sanitizer** | 未定义行为检测 |
| **coverage-analysis** | 衡量和提高代码覆盖率 |
| **fuzzing-corpus** | 构建和管理种子语料库 |
| **fuzzing-dictionaries** | 创建用于格式感知模糊测试的字典 |

### 相关模糊测试器

| 技能 | 考虑何时使用 |
|-------|------------------|
| **libfuzzer** | 简单设置，不需要 LibAFL 的高级功能 |
| **aflpp** | 无需自定义模糊测试器开发的多核模糊测试 |
| **cargo-fuzz** | 使用更少设置的 Rust 项目模糊测试 |

## 资源

### 官方文档

- [LibAFL 书籍](https://aflplus.plus/libafl-book/) - 官方手册，包含全面文档
- [LibAFL GitHub](https://github.com/AFLplusplus/LibAFL) - 源代码和示例
- [LibAFL API 文档](https://docs.rs/libafl/latest/libafl/) - Rust API 参考

### 示例和教程

- [LibAFL 示例](https://github.com/AFLplusplus/LibAFL/tree/main/fuzzers) - 示例模糊测试器集合
- [cargo-fuzz with LibAFL](https://github.com/AFLplusplus/LibAFL/tree/main/fuzzers/fuzz_anything/cargo_fuzz) - 使用 LibAFL 作为 cargo-fuzz 后端
- [Testing Handbook LibAFL 示例](https://github.com/trailofbits/testing-handbook/tree/main/materials/fuzzing/libafl) - 来自此手册的完整工作示例
