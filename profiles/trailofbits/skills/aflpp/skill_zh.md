# AFL++

AFL++ 是原始 AFL fuzzer 的分支，在保持稳定性的同时提供了更好的模糊测试性能和更高级的功能。与 libFuzzer 相比的主要优势在于 AFL++ 支持在多个核心上稳定运行模糊测试活动，使其成为大规模模糊测试工作的理想选择。

## 使用场景

| 模糊测试器 | 最适合 | 复杂度 |
|--------|----------|------------|
| AFL++ | 多核心模糊测试、多样化变异、成熟项目 | 中等 |
| libFuzzer | 快速设置、单线程、简单 harness | 低 |
| LibAFL | 自定义模糊测试器、研究、高级用例 | 高 |

**选择 AFL++ 当：**
- 您需要多核心模糊测试以最大化吞吐量
- 您的项目可以使用 Clang 或 GCC 编译
- 您想要多样化的变异策略和成熟的工具
- libFuzzer 已经达到平台期，您需要更多覆盖率
- 您正在模糊生产代码库，从并行执行中受益

## 快速入门

```c++
extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    // 使用模糊测试器提供的数据调用您的代码
    check_buf((char*)data, size);
    return 0;
}
```

编译和运行：
```bash
# 首先设置 AFL++ 包装脚本（见安装）
./afl++ docker afl-clang-fast++ -DNO_MAIN=1 -O2 -fsanitize=fuzzer harness.cc main.cc -o fuzz
mkdir seeds && echo "aaaa" > seeds/minimal_seed
./afl++ docker afl-fuzz -i seeds -o out -- ./fuzz
```

## 安装

AFL++ 有许多依赖项，包括 LLVM、Python 和 Rust。我们建议使用当前的 Debian 或 Ubuntu 发行版进行 AFL++ 模糊测试。

| 方法 | 使用场景 | 支持的编译器 |
|--------|-------------|---------------------|
| Ubuntu/Debian 软件仓库 | 近期 Ubuntu，仅基本功能 | Ubuntu 23.10: Clang 14 & GCC 13<br>Debian 12: Clang 14 & GCC 12 |
| Docker（来自 Docker Hub） | 特定的 AFL++ 版本，Apple Silicon 支持 | 自 4.35c 起: Clang 19 & GCC 11 |
| Docker（从源代码） | 测试未发布的特性，应用补丁 | Dockerfile 中可配置 |
| 从源代码 | 避免使用 Docker，需要特定补丁 | 可通过 `LLVM_CONFIG` 环境变量调整 |

### Ubuntu/Debian

在安装 AFL++ 之前，使用 `apt-cache show afl++` 检查包的 clang 版本依赖项，并安装匹配的 `lld` 版本（例如，`lld-17`）。

```bash
apt install afl++ lld-17
```

### Docker（来自 Docker Hub）

```bash
docker pull aflplusplus/aflplusplus:stable
```

### Docker（从源代码）

```bash
git clone --depth 1 --branch stable https://github.com/AFLplusplus/AFLplusplus
cd AFLplusplus
docker build -t aflplusplus .
```

### 从源代码

参考 [Dockerfile](https://github.com/AFLplusplus/AFLplusplus/blob/stable/Dockerfile) 了解 Ubuntu 版本要求和依赖项。设置 `LLVM_CONFIG` 以指定 Clang 版本（例如，`llvm-config-18`）。

### 包装脚本设置

创建一个包装脚本以在主机或 Docker 上运行 AFL++：

```bash
cat <<'EOF' > ./afl++
#!/bin/sh
AFL_VERSION="${AFL_VERSION:-"stable"}"
case "$1" in
   host)
        shift
        bash -c "$*"
        ;;
    docker)
        shift
        /usr/bin/env docker run -i \
            --privileged \
            -v ./:/src \
            --rm \
            --name "afl_fuzzing_$$" \
            "aflplusplus/aflplusplus:$AFL_VERSION" \
            bash -c "cd /src && bash -c \"$*\""
        ;;
    *)
        echo "Usage: $0 {host|docker}"
        exit 1
        ;;
esac
EOF
chmod +x ./afl++
```

以下示例使用 `docker` 模式，系统配置命令必须到达主机内核。将 `host` 替换为在机器上安装的 AFL++ 上运行它们。包装脚本将模式参数之后的所有内容连接成一个单一的 shell 字符串，因此引号不会保留：包含空格的参数（`-x "my dict.dict"`）会到达单词分割。重命名此类文件而不包含空格，或编辑包装脚本以进行该运行。

缺少 `-t` 是故意的。`docker run -ti` 在 stdin 不是终端时中止，显示 `the input device is not a TTY`，这涵盖了 CI 工作和任何由代理或脚本驱动的操作。`afl-fuzz` 注意到没有终端，并在全屏 UI 处打印普通状态行。坚持需要终端的程序（如 `watch`）必须在包装脚本的主机侧运行。`$$` 扩展为包装脚本的 PID，因此并行实例获得不同的容器名称，而不是在单个 `afl_fuzzing` 上冲突。`docker ps` 截断命令列，因此每一行看起来都一样；在停止一个之前，使用 `docker ps --no-trunc` 来区分实例。

**安全警告：** `afl-system-config` 和 `afl-persistent-config` 脚本需要 root 权限并禁用 OS 安全功能。不要在生产系统或开发环境中模糊测试。使用专用虚拟机 instead。

### 系统配置

每次重启后运行，以最多提高 15% 的执行次数：

```bash
./afl++ host afl-system-config
```

`afl-system-config` 调整它运行的对面的内核，因此请在托管活动的主机上运行它。`./afl++ docker afl-system-config` 通过包装脚本的 `--privileged` 容器到达相同的设置，这是仅当 AFL++ 通过 Docker 单独安装时的唯一路线。

为了获得最大性能，禁用内核安全缓解措施（需要 grub 引导加载程序，Docker 不支持）：

```bash
./afl++ host afl-persistent-config
update-grub
reboot
./afl++ host afl-system-config
```

使用 `cat /proc/cmdline` 验证 - 输出应包括 `mitigations=off`。

## 编写 Harness

### Harness 结构

AFL++ 支持类似 libFuzzer 的 harness：

```c++
#include <stdint.h>
#include <stddef.h>

extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    // 如果需要，验证输入大小
    if (size < MIN_SIZE || size > MAX_SIZE) return 0;

    // 使用模糊数据调用目标函数
    target_function(data, size);

    // 返回 0（非零保留用于未来使用）
    return 0;
}
```

### Harness 规则

| 做 | 不要 |
|----|-------|
| 在运行之间重置全局状态 | 依赖前一次运行的状态 |
| 优雅地处理边缘情况 | 在无效输入上退出 |
| 保持 harness 确定性 | 使用随机数生成器 |
| 释放分配的内存 | 创建内存泄漏 |
| 验证输入大小 | 处理无界输入 |

> **另见：** 有关详细的 harness 编写技术、处理复杂输入的模式和高级策略，请参阅 **fuzz-harness-writing** 技能。

## 编译

AFL++ 提供多种编译模式，具有不同的权衡。

### 编译模式决策树

选择您的编译模式：
- **LTO 模式** (`afl-clang-lto`)：最佳性能和仪器。首先尝试这个。
- **LLVM 模式** (`afl-clang-fast`)：如果 LTO 编译失败，则回退。
- **GCC 插件** (`afl-gcc-fast`)：用于需要 GCC 的项目。

### 基本编译（LLVM 模式）

```bash
./afl++ docker afl-clang-fast++ -DNO_MAIN=1 -O2 -fsanitize=fuzzer harness.cc main.cc -o fuzz
```

### GCC 编译

```bash
./afl++ docker afl-g++-fast -DNO_MAIN=1 -O2 -fsanitize=fuzzer harness.cc main.cc -o fuzz
```

**重要：** GCC 版本必须与用于编译 AFL++ GCC 插件的版本匹配。

### 使用 Sanitizers

```bash
./afl++ docker AFL_USE_ASAN=1 afl-clang-fast++ -DNO_MAIN=1 -O2 -fsanitize=fuzzer harness.cc main.cc -o fuzz
```

> **另见：** 有关详细的 sanitizer 配置、常见问题和高级标志，请参阅 **address-sanitizer** 技能。

### 构建标志

注意 `-g` 不是必要的，它由 AFL++ 编译器默认添加。

| 标志 | 目的 |
|------|---------|
| `-DNO_MAIN=1` | 使用 libFuzzer harness 时跳过 main 函数 |
| `-O2` | 生产优化级别（模糊测试推荐） |
| `-fsanitize=fuzzer` | 启用 libFuzzer 兼容模式并在链接可执行文件时添加模糊测试器运行时 |
| `-fsanitize=fuzzer-no-link` | 仪器而不链接模糊测试器运行时（用于静态库和对象文件） |

## 语料库管理

### 创建初始语料库

AFL++ 需要至少一个非空的种子文件：

```bash
mkdir seeds
echo "aaaa" > seeds/minimal_seed
```

对于真实项目，收集有代表性的输入：
- 下载您正在模糊的格式的示例文件
- 从项目的测试套件中提取测试用例
- 使用您文件格式的基本有效输入

### 语料库最小化

在活动后最小化语料库，以仅保留唯一的覆盖率：

```bash
./afl++ docker afl-cmin -i out/default/queue -o minimized_corpus -- ./fuzz
```

> **另见：** 有关语料库创建策略、字典和种子选择，请参阅 **fuzzing-corpus** 技能。

## 运行活动

### 基本运行

```bash
./afl++ docker afl-fuzz -i seeds -o out -- ./fuzz
```

### 设置环境变量

```bash
./afl++ docker AFL_FAST_CAL=1 afl-fuzz -i seeds -o out -- ./fuzz
```

### 解释输出

AFL++ 以两种方式报告这些统计数据，但如何读取它们取决于模式。包装脚本的 `docker run -i` 不会给容器提供 TTY，因此 `afl-fuzz` 会放弃全屏 UI 并将普通状态行写入日志 - 以下字段会出现在那里，以及 `state/<instance>/fuzzer_stats`。要在终端中获取交互式 UI，请在终端中运行 `host` 模式，或在包装脚本中为手动监控的运行添加 `-t`。

| 输出 | 含义 |
|--------|---------|
| **execs/sec** | 执行速度 - 越高越好 |
| **cycles done** | 完成的队列传递数 |
| **corpus count** | 队列中唯一测试用例的数量 |
| **saved crashes** | 发现的唯一崩溃数量 |
| **stability** | 稳定边缘的百分比（应接近 100%） |

### 输出目录结构

```text
out/default/
├── cmdline          # 如何调用 SUT？
├── crashes/         # 使 SUT 出现崩溃的输入
│   └── id:000000,sig:06,src:000002,time:286,execs:13105,op:havoc,rep:4
├── hangs/           # 使 SUT 挂起的输入
├── queue/           # 重复最终模糊器状态的测试用例
│   ├── id:000000,time:0,execs:0,orig:minimal_seed
│   └── id:000001,src:000000,time:0,execs:8,op:havoc,rep:6,+cov
├── fuzzer_stats     # 活动统计信息
└── plot_data        # 绘图数据
```

### 分析结果

查看实时活动统计信息：

```bash
./afl++ docker afl-whatsup out
```

创建覆盖率图。`aflplusplus` 镜像已经预装了 `gnuplot-nox`；在主机模式下，首先使用 `apt install gnuplot` 安装 gnuplot。

```bash
./afl++ docker afl-plot out/default out_graph/
```

### 重新执行测试用例

传递 `out/default/crashes/` 中的一个文件名：

```bash
./afl++ docker ./fuzz out/default/crashes/id:000000,sig:06,src:000002,time:286,execs:13105,op:havoc,rep:4
```

### Fuzzer 选项

| 选项 | 目的 |
|--------|---------|
| `-G 4000` | 最大测试输入长度（默认：1048576 字节） |
| `-t 1000` | 每个测试用例的超时（毫秒）（默认：1000ms） |
| `-m 1000` | 内存限制（兆字节）（默认：0 = 无限制） |
| `-x ./dict.dict` | 使用字典文件指导变异 |

## 相关的环境变量

AFL++ 有许多环境变量，但大多数是利基的。以下是在实践中重要的几个。

### 总是设置这些

```bash
# 每个活动都应该使用 tmpfs — SSD 会感谢您，而且它更快
AFL_TMPDIR=/dev/shm
```

`AFL_TMPDIR` 是一个免费的性能提升，没有任何缺点 - 不设置它会使您的 SSD 磨损并减慢模糊测试。

### 慢目标

```bash
# 加快校准 ~2.5 倍 — 当目标很慢（例如，>10 ms/exec）时使用
AFL_FAST_CAL=1
```

`AFL_FAST_CAL` 通过可忽略的精度损失减少了校准时间。特别推荐用于慢目标，否则校准会花费很长时间。

### 多核心活动

```bash
# 仅在主实例（-M）上 — 需要用于 afl-cmin，而不是用于模糊测试本身
AFL_FINAL_SYNC=1

# 在所有实例上 — 在内存中缓存测试用例（默认：50 MB，良好范围：50-250 MB）
AFL_TESTCACHE_SIZE=100
```

`AFL_FINAL_SYNC` 告知主实例在停止时从所有次要实例执行最终导入。这不会影响模糊测试过程本身 - 它仅在您稍后运行 `afl-cmin` 进行语料库最小化时才重要，以确保主实例的队列具有完整的组合语料库。`AFL_TESTCACHE_SIZE` 在内存中缓存测试用例以减少磁盘 I/O；默认值是 50 MB，大多数活动中的值在 50-250 MB 之间工作良好。

### CI/自动化模糊测试

```bash
# 如果模糊测试没有发现任何内容，则快速失败
AFL_EXIT_ON_TIME=3600  # 1 小时内没有新路径 = 停止

# 或者运行直到 "done"（所有队列条目处理完毕）
AFL_EXIT_WHEN_DONE=1

# 无头环境
AFL_NO_UI=1
```

CI 中的无界模糊测试会浪费资源。设置时间限制或使用退出条件。

### 要避免的变量

| 变量 | 跳过原因 |
|----------|-------------|
| `AFL_NO_ARITH` | 可能会损害二进制格式的覆盖率，但对于基于文本的目标可能有用 |
| `AFL_SHUFFLE_QUEUE` | 仅用于特殊设置，通常有害 |
| `AFL_DISABLE_TRIM` | 剪辑很有价值，没有理由禁用它 |

## 多核心模糊测试

AFL++ 在多核心模糊测试方面表现出色，具有两个主要优势：
1. 每秒更多执行（与物理核心线性扩展）
2. 非对称模糊测试（例如，一个 ASan 任务，其余没有使用 sanitizer）

### 启动活动

启动主模糊器（在后台）：

```bash
./afl++ docker afl-fuzz -M primary -i seeds -o state -- ./fuzz 1>primary.log 2>primary.error </dev/null &
```

启动次要模糊器（与您拥有的核心一样多）：

```bash
./afl++ docker afl-fuzz -S secondary01 -i seeds -o state -- ./fuzz 1>secondary01.log 2>secondary01.error </dev/null &
./afl++ docker afl-fuzz -S secondary02 -i seeds -o state -- ./fuzz 1>secondary02.log 2>secondary02.error </dev/null &
```

`</dev/null` 是必需的，不是装饰性的。`docker run -i` 保持客户端读取自己的 stdin，并且一个在终端中读取的背景进程会收到 `SIGTTIN`，其默认操作是停止它 - 所以没有重定向这些作业会显示为 `Stopped` 在 `jobs` 中，并且永远不会模糊测试。

### 监控多核心活动

列出所有正在运行的作业：

```bash
jobs
```

查看实时统计信息。`watch` 需要一个终端，而 `docker run -i` 不会给它，所以整个调用要包装起来，而不是在容器内运行 `watch`。每个滴答都会启动一个容器，因此间隔设置为 5 秒而不是 1：

```bash
watch -n5 --color ./afl++ docker afl-whatsup state/
```

### 停止所有模糊器

```bash
kill $(jobs -p)
```

## 覆盖率分析

AFL++ 自动通过边缘仪器跟踪覆盖率。覆盖率信息存储在 `fuzzer_stats` 和 `plot_data` 中。

### 测量覆盖率

使用 `afl-plot` 可视化随时间变化的覆盖率：

```bash
./afl++ docker afl-plot out/default out_graph/
```

### 提高覆盖率

- 使用字典进行格式感知模糊测试
- 运行更长的活动（cycles_wo_finds 指示平台期）
- 尝试使用多核心模糊测试的不同变异策略
- 分析覆盖率差距并添加有针对性的种子输入

> **另见：** 有关详细的覆盖率分析技术、识别覆盖率差距和系统覆盖率改进，请参阅 **coverage-analysis** 技能。

## CMPLOG

CMPLOG/RedQueen 是任何模糊器中可用的最佳路径约束求解机制。要启用它，模糊目标需要为其进行仪器。
在构建模糊测试目标之前设置环境变量：

```bash
./afl++ docker AFL_LLVM_CMPLOG=1 make
```

编译和链接 harness 无需特殊操作。

要运行一个使用 CMPLOG 仪器化模糊测试目标的模糊器实例，在命令行参数中添加 `-c0`：

```bash
./afl++ docker afl-fuzz -c0 -S cmplog -i seeds -o state -- ./fuzz 1>cmplog.log 2>cmplog.error </dev/null &
```

## Sanitizer 集成

Sanitizers 对于查找不会导致立即崩溃的内存损坏错误至关重要。

### AddressSanitizer (ASan)

```bash
./afl++ docker AFL_USE_ASAN=1 afl-clang-fast++ -DNO_MAIN=1 -O2 -fsanitize=fuzzer harness.cc main.cc -o fuzz
```

**注意：** 由于 ASan 使用 20TB 虚拟内存保留，因此不支持内存限制 (`-m`)。

### UndefinedBehaviorSanitizer (UBSan)

```bash
./afl++ docker AFL_USE_UBSAN=1 afl-clang-fast++ -DNO_MAIN=1 -O2 -fsanitize=fuzzer,undefined harness.cc main.cc -o fuzz
```

### 常见 Sanitizer 问题

| 问题 | 解决方案 |
|-------|----------|
| ASan 减慢模糊测试 | 在多核心设置中仅使用 1 个 ASan 任务 |
| 栈耗尽 | 使用 `ASAN_OPTIONS=stack_size=...` 增加栈 |
| GCC 版本不匹配 | 确保系统 GCC 与 AFL++ 插件版本匹配 |

> **另见：** 有关全面的 sanitizer 配置和故障排除，请参阅 **address-sanitizer** 技能。

## 高级用法

### 提示和技巧

| 提示 | 帮助原因 |
|-----|--------------|
| 尽可能使用 LLVMFuzzerTestOneInput harnesses | 如果模糊测试活动至少有 85% 的稳定性，那么这是最有效的模糊测试方式。如果不是，则尝试标准输入或文件输入模糊测试 |
| 使用字典 | 帮助模糊器发现格式特定的关键词和魔法字节 |
| 设置现实的超时 | 防止系统负载产生的误报 |
| 限制输入大小 | 更大的输入不一定探索更多空间 |
| 监控稳定性 | 低稳定性指示非确定性行为 |

### 标准输入模糊测试

AFL++ 可以模糊从 stdin 读取的程序，而无需 libFuzzer harness：

```bash
./afl++ docker afl-clang-fast++ -O2 main_stdin.c -o fuzz_stdin
./afl++ docker afl-fuzz -i seeds -o out -- ./fuzz_stdin
```

这比持久模式慢，但不需要 harness 代码。

### 文件输入模糊测试

对于读取文件的程序，使用 `@@` 占位符：

```bash
./afl++ docker afl-clang-fast++ -O2 main_file.c -o fuzz_file
./afl++ docker afl-fuzz -i seeds -o out -- ./fuzz_file @@
```

为了获得更好的性能，使用 `fmemopen` 从内存创建文件描述符。

### 参数模糊测试

使用 `argv-fuzz-inl.h` 模糊命令行参数：

```c++
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifdef __AFL_COMPILER
#include "argv-fuzz-inl.h"
#endif

void check_buf(char *buf, size_t buf_len) {
    if(buf_len > 0 && buf[0] == 'a') {
        if(buf_len > 1 && buf[1] == 'b') {
            if(buf_len > 2 && buf[2] == 'c') {
                abort();
            }
        }
    }
}

int main(int argc, char *argv[]) {
#ifdef __AFL_COMPILER
    AFL_INIT_ARGV();
#endif

    if (argc < 2) {
        fprintf(stderr, "Usage: %s <input_string>\n", argv[0]);
        return 1;
    }

    char *input_buf = argv[1];
    size_t len = strlen(input_buf);
    check_buf(input_buf, len);
    return 0;
}
```

下载头文件：

```bash
curl -O https://raw.githubusercontent.com/AFLplusplus/AFLplusplus/stable/utils/argv_fuzzing/argv-fuzz-inl.h
```

编译和运行：

```bash
./afl++ docker afl-clang-fast++ -O2 main_arg.c -o fuzz_arg
./afl++ docker afl-fuzz -i seeds -o out -- ./fuzz_arg
```

### 性能调优

| 设置 | 影响 |
|---------|--------|
| CPU 核心数 | 与物理核心线性扩展 |
| 持久模式 | 比fork server 快 10-20 倍 |
| `-G` 输入大小限制 | 较小 = 更快，但可能会错过错误 |
| ASan 比率 | 每个非 ASan 作业 4-8 个 ASan 作业 |

## 故障排除

| 问题 | 原因 | 解决方案 |
|---------|-------|----------|
| 低 exec/sec (<1k) | 未使用持久模式 | 创建 LLVMFuzzerTestOneInput 风格的 harness |
| 低稳定性 (<85%) | 非确定性代码 | 通过 stdin 或文件输入模糊测试程序，或创建此类 harness |
| GCC 插件错误 | GCC 版本不匹配 | 确保 system GCC 与 AFL++ 构建和安装 gcc-$GCC_VERSION-plugin-dev 匹配 |
| 未发现崩溃 | 需要 sanitizers | 重新编译为 `AFL_USE_ASAN=1` |
| 内存限制超出 | ASan 使用 20TB 虚拟内存 | 使用 ASan 时移除 `-m` 标志 |
| Docker 性能损失 | 虚拟化开销 | 使用裸机或 VM 进行生产模糊测试 |

## 相关技能

### 技术技能

| 技能 | 用例 |
|-------|----------|
| **fuzz-harness-writing** | 详细指导编写有效的 harness |
| **address-sanitizer** | 模糊测试期间的内存错误检测 |
| **undefined-behavior-sanitizer** | 检测未定义行为错误 |
| **fuzzing-corpus** | 构建和管理种子语料库 |
| **fuzzing-dictionaries** | 创建用于格式感知模糊测试的字典 |

### 相关模糊器

| 技能 | 考虑何时使用 |
|-------|------------------|
| **libfuzzer** | 快速原型设计，单线程模糊测试足够 |
| **libafl** | 需要自定义变异器或研究级功能 |

## 资源

### 关键外部资源

**[AFL++ GitHub 仓库](https://github.com/AFLplusplus/AFLplusplus)**
官方仓库，包含全面的文档、示例和问题跟踪器。

**[深入模糊测试](https://raw.githubusercontent.com/AFLplusplus/AFLplusplus/refs/heads/stable/docs/fuzzing_in_depth.md)**
AFL++ 团队编写的先进文档，涵盖仪器模式、优化技术和高级用例。

**[AFL++ 内部机制](https://blog.ritsec.club/posts/afl-under-hood/)**
AFL++ 内部机制的技术深入，变异策略和覆盖率跟踪机制。

**[AFL++：结合模糊测试研究的增量步骤](https://www.usenix.org/system/files/woot20-paper-fioraldi.pdf)**
描述 AFL++ 架构和原始 AFL 性能改进的研究论文。

### 视频资源

- [模糊测试 cURL](https://blog.trailofbits.com/2023/02/14/curl-audit-fuzzing-libcurl-command-line-interface/) - Trail of Bits 博客文章，使用 AFL++ 参数模糊测试 cURL
- [Sudo 漏洞分析](https://www.youtube.com/playlist?list=PLhixgUqwRTjy0gMuT4C3bmjeZjuNQyqdx) - LiveOverflow 系列，rediscovering CVE-2021-3156
- [libpng 漏洞的重新发现](https://www.youtube.com/watch?v=PJLWlmp8CDM) - LiveOverflow 视频，发现 CVE-2023-4863
