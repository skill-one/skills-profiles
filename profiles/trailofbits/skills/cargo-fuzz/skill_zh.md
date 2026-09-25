# cargo-fuzz

cargo-fuzz 是使用 Cargo 构建 Rust 项目时事实上的模糊测试工具。它使用 libFuzzer 作为后端，并提供一个方便的 Cargo 子命令，可以自动为您的 Rust 项目启用相关的编译标志，包括对 AddressSanitizer 等清理器的支持。

## 使用场景

cargo-fuzz 目前是使用 Cargo 构建 Rust 项目的主要且最成熟的模糊测试解决方案。

| 模糊测试器 | 最适合 | 复杂度 |
|--------|----------|------------|
| cargo-fuzz | 基于 Cargo 的 Rust 项目，快速设置 | 低 |
| AFL++ | 多核模糊测试，非 Cargo 项目 | 中等 |
| LibAFL | 自定义模糊测试器，研究，高级用例 | 高 |

**选择 cargo-fuzz 的情况：**
- 您的项目使用 Cargo（必需）
- 您希望进行简单、快速的设置，配置最小化
- 您需要集成清理器支持
- 您正在模糊测试带有或不带有 unsafe 块的 Rust 代码

## 快速入门

```rust
#![no_main]

use libfuzzer_sys::fuzz_target;

fn harness(data: &[u8]) {
    your_project::check_buf(data);
}

fuzz_target!(|data: &[u8]| {
    harness(data);
});
```

初始化并运行：
```bash
cargo fuzz init
# 编辑 fuzz/fuzz_targets/fuzz_target_1.rs 以使用您的 harness
cargo +nightly fuzz run fuzz_target_1
```

## 安装

cargo-fuzz 需要 nightly Rust 工具链，因为它使用仅在 nightly 中可用的功能。

### 前置条件

- 通过 [rustup](https://rustup.rs/) 安装的 Rust 和 Cargo
- nightly 工具链

### Linux/macOS

```bash
# 安装 nightly 工具链
rustup install nightly

# 安装 cargo-fuzz
cargo install cargo-fuzz
```

### 验证

```bash
cargo +nightly --version
cargo fuzz --version
```

## 编写 Harness

### 项目结构

cargo-fuzz 在您的代码作为库 Crate 结构时工作最佳。如果您有一个二进制项目，请将您的 `main.rs` 分成：

```text
src/main.rs  # 入口点（main 函数）
src/lib.rs   # 要模糊测试的代码（公共函数）
Cargo.toml
```

初始化模糊测试：
```bash
cargo fuzz init
```

这将创建：
```text
fuzz/
├── Cargo.toml
└── fuzz_targets/
    └── fuzz_target_1.rs
```

### Harness 结构

```rust
#![no_main]

use libfuzzer_sys::fuzz_target;

fn harness(data: &[u8]) {
    // 1. 如有必要，验证输入大小
    if data.is_empty() {
        return;
    }

    // 2. 使用模糊测试数据调用目标函数
    your_project::target_function(data);
}

fuzz_target!(|data: &[u8]| {
    harness(data);
});
```

### Harness 规则

| 做 | 不要 |
|----|-------|
| 将代码结构化为库 Crate | 将所有内容保留在 main.rs 中 |
| 使用 `fuzz_target!` 宏 | 编写自定义 main 函数 |
| 优雅地处理 `Result::Err` | 在预期错误时恐慌 |
| 保持 harness 确定性 | 使用随机数生成器 |

> **另见：** 有关详细的 harness 编写技术和使用 `arbitrary` Crate 进行结构感知模糊测试的技巧，请参阅 **fuzz-harness-writing** 技能。

## 结构感知模糊测试

cargo-fuzz 与 [arbitrary](https://github.com/rust-fuzz/arbitrary) Crate 集成，用于结构感知模糊测试：

```rust
// 在您的库 Crate 中
use arbitrary::Arbitrary;

#[derive(Debug, Arbitrary)]
pub struct Name {
    data: String
}
```

```rust
// 在您的模糊测试目标中
#![no_main]
use libfuzzer_sys::fuzz_target;

fuzz_target!(|data: your_project::Name| {
    data.check_buf();
});
```

将以下内容添加到您库的 `Cargo.toml` 中：
```toml
[dependencies]
arbitrary = { version = "1", features = ["derive"] }
```

## 运行 Campaigns

### 基本运行

```bash
cargo +nightly fuzz run fuzz_target_1
```

### 不使用清理器（安全 Rust）

如果您的项目不使用 unsafe Rust，禁用清理器以获得 2 倍的性能提升：

```bash
cargo +nightly fuzz run --sanitizer none fuzz_target_1
```

检查您的项目是否使用 unsafe 代码：
```bash
cargo install cargo-geiger
cargo geiger
```

### 重新执行测试用例

```bash
# 运行特定的测试用例（例如，崩溃）
cargo +nightly fuzz run fuzz_target_1 fuzz/artifacts/fuzz_target_1/crash-<hash>

# 不进行模糊测试地运行所有语料库条目
cargo +nightly fuzz run fuzz_target_1 fuzz/corpus/fuzz_target_1 -- -runs=0
```

### 使用字典

```bash
cargo +nightly fuzz run fuzz_target_1 -- -dict=./dict.dict
```

### 解释输出

| 输出 | 含义 |
|--------|---------|
| `NEW` | 发现了新的、增加覆盖率的输入 |
| `pulse` | 定期状态更新 |
| `INITED` | 模糊测试器初始化成功 |
| 带堆栈跟踪的崩溃 | 发现了错误，保存到 `fuzz/artifacts/` |

语料库位置：`fuzz/corpus/fuzz_target_1/`
崩溃位置：`fuzz/artifacts/fuzz_target_1/`

## 清理器集成

### AddressSanitizer (ASan)

ASan 默认启用，并检测内存错误：

```bash
cargo +nightly fuzz run fuzz_target_1
```

### 禁用清理器

对于纯安全 Rust（您的代码或依赖项中没有 unsafe 块）：

```bash
cargo +nightly fuzz run --sanitizer none fuzz_target_1
```

**性能影响：** ASan 增加了约 2 倍的开销。禁用清理器以提高安全 Rust 的模糊测试速度。

### 检查 unsafe 代码

```bash
cargo install cargo-geiger
cargo geiger
```

> **另见：** 有关详细的清理器配置、标志和故障排除，请参阅 **address-sanitizer** 技能。

## 覆盖率分析

cargo-fuzz 集成了 Rust 的覆盖率工具来分析模糊测试的有效性。

### 前置条件

```bash
rustup toolchain install nightly --component llvm-tools-preview
cargo install cargo-binutils
cargo install rustfilt
```

### 生成覆盖率报告

```bash
# 从语料库生成覆盖率数据
cargo +nightly fuzz coverage fuzz_target_1
```

创建覆盖率生成脚本：

```bash
cat <<'EOF' > ./generate_html
#!/bin/sh
if [ $# -lt 1 ]; then
    echo "Error: 需要模糊测试目标的名称。"
    echo "用法: $0 fuzz_target [sources...]"
    exit 1
fi
FUZZ_TARGET="$1"
shift
SRC_FILTER="$@"
TARGET=$(rustc -vV | sed -n 's|host: ||p')
cargo +nightly cov -- show -Xdemangler=rustfilt \
  "target/$TARGET/coverage/$TARGET/release/$FUZZ_TARGET" \
  -instr-profile="fuzz/coverage/$FUZZ_TARGET/coverage.profdata"  \
  -show-line-counts-or-regions -show-instantiations  \
  -format=html -o fuzz_html/ $SRC_FILTER
EOF
chmod +x ./generate_html
```

生成 HTML 报告：
```bash
./generate_html fuzz_target_1 src/lib.rs
```

HTML 报告保存到：`fuzz_html/`

> **另见：** 有关详细的覆盖率分析技术和系统覆盖率改进，请参阅 **coverage-analysis** 技能。

## 高级用法

### 提示和技巧

| 提示 | 帮助原因 |
|-----|--------------|
| 从种子语料库开始 | 大幅加快初始覆盖率发现 |
| 对于安全 Rust 使用 `--sanitizer none` | 2 倍性能提升 |
| 定期检查覆盖率 | 识别 harness 或种子语料库中的差距 |
| 使用字典进行解析器 | 帮助克服魔法值检查 |
| 将代码结构化为库 | cargo-fuzz 集成所需 |

### libFuzzer 选项

在 `--` 后传递选项：

```bash
# 查看所有选项
cargo +nightly fuzz run fuzz_target_1 -- -help=1

# 设置每次运行的超时
cargo +nightly fuzz run fuzz_target_1 -- -timeout=10

# 使用字典
cargo +nightly fuzz run fuzz_target_1 -- -dict=dict.dict

# 限制最大输入大小
cargo +nightly fuzz run fuzz_target_1 -- -max_len=1024
```

### 多核模糊测试

```bash
# 实验性分叉支持（不推荐）
cargo +nightly fuzz run --jobs 1 fuzz_target_1
```

注意：多核模糊测试功能是实验性的，不推荐使用。对于并行模糊测试，请考虑手动运行多个实例或使用 AFL++。

## 真实世界示例

### 示例：ogg Crate

[ogg crate](https://github.com/RustAudio/ogg) 解析 Ogg 媒体容器文件。解析器是优秀的模糊测试目标，因为它们处理不受信任的数据。

```bash
# 克隆并初始化
git clone https://github.com/RustAudio/ogg.git
cd ogg/
cargo fuzz init
```

在 `fuzz/fuzz_targets/fuzz_target_1.rs` 中编写 harness：

```rust
#![no_main]

use ogg::{PacketReader, PacketWriter};
use ogg::writing::PacketWriteEndInfo;
use std::io::Cursor;
use libfuzzer_sys::fuzz_target;

fn harness(data: &[u8]) {
    let mut pck_rdr = PacketReader::new(Cursor::new(data.to_vec()));
    pck_rdr.delete_unread_packets();

    let output = Vec::new();
    let mut pck_wtr = PacketWriter::new(Cursor::new(output));

    if let Ok(_) = pck_rdr.read_packet() {
        if let Ok(r) = pck_rdr.read_packet() {
            match r {
                Some(pck) => {
                    let inf = if pck.last_in_stream() {
                        PacketWriteEndInfo::EndStream
                    } else if pck.last_in_page() {
                        PacketWriteEndInfo::EndPage
                    } else {
                        PacketWriteEndInfo::NormalPacket
                    };
                    let stream_serial = pck.stream_serial();
                    let absgp_page = pck.absgp_page();
                    let _ = pck_wtr.write_packet(
                        pck.data, stream_serial, inf, absgp_page
                    );
                }
                None => return,
            }
        }
    }
}

fuzz_target!(|data: &[u8]| {
    harness(data);
});
```

为语料库种子：
```bash
mkdir fuzz/corpus/fuzz_target_1/
curl -o fuzz/corpus/fuzz_target_1/320x240.ogg \
  https://commons.wikimedia.org/wiki/File:320x240.ogg
```

运行：
```bash
cargo +nightly fuzz run fuzz_target_1
```

分析覆盖率：
```bash
cargo +nightly fuzz coverage fuzz_target_1
./generate_html fuzz_target_1 src/lib.rs
```

## 故障排除

| 问题 | 原因 | 解决方案 |
|---------|-------|----------|
| "requires nightly" 错误 | 使用稳定工具链 | 使用 `cargo +nightly fuzz` |
| 模糊测试性能慢 | 为安全 Rust 启用了 ASan | 添加 `--sanitizer none` 标志 |
| "cannot find binary" | 没有库 Crate | 将代码从 `main.rs` 移动到 `lib.rs` |
| 清理器编译问题 | 错误的 nightly 版本 | 尝试不同的 nightly：`rustup install nightly-2024-01-01` |
| 低覆盖率 | 缺少种子语料库 | 向 `fuzz/corpus/fuzz_target_1/` 添加示例输入 |
| 未找到魔法值 | 没有字典 | 创建包含魔法值的字典文件 |

## 相关技能

### 技能技能

| 技能 | 用例 |
|-------|----------|
| **fuzz-harness-writing** | 使用 `arbitrary` Crate 进行结构感知模糊测试 |
| **address-sanitizer** | 理解 ASan 输出和配置 |
| **coverage-analysis** | 衡量和改进模糊测试有效性 |
| **fuzzing-corpus** | 构建和管理种子语料库 |
| **fuzzing-dictionaries** | 创建用于格式感知模糊测试的字典 |

### 相关模糊测试器

| 技能 | 考虑何时使用 |
|-------|------------------|
| **libfuzzer** | 使用类似工作流程模糊测试 C/C++ 代码 |
| **aflpp** | 多核模糊测试或非 Cargo Rust 项目 |
| **libafl** | 高级模糊测试研究或自定义模糊测试器开发 |

## 资源

**[Rust Fuzz Book - cargo-fuzz](https://rust-fuzz.github.io/book/cargo-fuzz.html)**
cargo-fuzz 的官方文档，涵盖安装、使用和高级功能。

**[arbitrary crate 文档](https://docs.rs/arbitrary/latest/arbitrary/)**
使用自动派生为 Rust 类型的结构感知模糊测试指南。

**[cargo-fuzz GitHub 仓库](https://github.com/rust-fuzz/cargo-fuzz)**
cargo-fuzz 的源代码、问题跟踪器和示例。
