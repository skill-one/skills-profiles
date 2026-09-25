# Atheris

Atheris 是一个基于 libFuzzer 的覆盖率引导型 Python 模糊测试工具。它支持对纯 Python 代码和 Python C 扩展进行模糊测试，并集成了 AddressSanitizer 以检测内存损坏问题。

## 使用场景

| 模糊测试器 | 最佳用途 | 复杂度 |
|--------|----------|------------|
| Atheris | Python 代码和 C 扩展 | 低-中 |
| Hypothesis | 基于属性的测试 | 低 |
| python-afl | AFL 风格的模糊测试 | 中 |

**选择 Atheris 的情况：**
- 使用覆盖率引导模糊测试纯 Python 代码
- 测试 Python C 扩展以检测内存损坏
- 希望与 libFuzzer 生态系统集成
- 需要 AddressSanitizer 支持

## 快速入门

```python
import sys
import atheris

@atheris.instrument_func
def TestOneInput(data: bytes):
    if len(data) == 4:
        if data[0] == 0x46:  # "F"
            if data[1] == 0x55:  # "U"
                if data[2] == 0x5A:  # "Z"
                    if data[3] == 0x5A:  # "Z"
                        raise RuntimeError("You caught me")

def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()

if __name__ == "__main__":
    main()
```

运行：
```bash
uv run python fuzz.py
```

## 安装

Atheris 支持 32 位和 64 位的 Linux 以及 macOS。我们推荐在 Linux 上进行模糊测试，因为管理起来更简单，通常速度也更快。

### 前置条件

- Python 3.7 或更高版本
- 较新版本的 clang（最好使用 [最新发布版本](https://github.com/llvm/llvm-project/releases)）
- 对于 Docker 用户：[Docker Desktop](https://www.docker.com/products/docker-desktop/)

### Linux/macOS

```bash
uv init --bare   # 如果 harness 目录还不是 uv 项目，则执行一次
uv add atheris
```

### Docker 环境（推荐）

对于具有所有依赖项配置的完整 Linux 环境：

```dockerfile
# https://hub.docker.com/_/python
ARG PYTHON_VERSION=3.11

FROM python:$PYTHON_VERSION-slim-bookworm

RUN python --version

RUN apt update && apt install -y \
    ca-certificates \
    wget \
    && rm -rf /var/lib/apt/lists/*

# LLVM builds version 15-19 for Debian 12 (Bookworm)
# https://apt.llvm.org/bookworm/dists/
ARG LLVM_VERSION=19

RUN echo "deb http://apt.llvm.org/bookworm/ llvm-toolchain-bookworm-$LLVM_VERSION main" > /etc/apt/sources.list.d/llvm.list
RUN echo "deb-src http://apt.llvm.org/bookworm/ llvm-toolchain-bookworm-$LLVM_VERSION main" >> /etc/apt/sources.list.d/llvm.list
RUN wget -qO- https://apt.llvm.org/llvm-snapshot.gpg.key > /etc/apt/trusted.gpg.d/apt.llvm.org.asc

RUN apt update && apt install -y \
    build-essential \
    clang-$LLVM_VERSION \
    && rm -rf /var/lib/apt/lists/*

ENV APP_DIR "/app"
RUN mkdir $APP_DIR
WORKDIR $APP_DIR

ENV VIRTUAL_ENV "/opt/venv"
RUN python -m venv $VIRTUAL_ENV
ENV PATH "$VIRTUAL_ENV/bin:$PATH"

# https://github.com/google/atheris/blob/master/native_extension_fuzzing.md#step-1-compiling-your-extension
ENV CC="clang-$LLVM_VERSION"
ENV CFLAGS "-fsanitize=address,fuzzer-no-link"
ENV CXX="clang++-$LLVM_VERSION"
ENV CXXFLAGS "-fsanitize=address,fuzzer-no-link"
ENV LDSHARED="clang-$LLVM_VERSION -shared"
ENV LDSHAREDXX="clang++-$LLVM_VERSION -shared"
ENV ASAN_SYMBOLIZER_PATH="/usr/bin/llvm-symbolizer-$LLVM_VERSION"

# 允许 Atheris 找到 fuzzer sanitizer 共享库
# https://github.com/google/atheris#building-from-source
RUN LIBFUZZER_LIB=$($CC -print-file-name=libclang_rt.fuzzer_no_main-$(uname -m).a) \
    python -m pip install --no-binary atheris atheris

# https://github.com/google/atheris/blob/master/native_extension_fuzzing.md#option-a-sanitizerlibfuzzer-preloads
ENV LD_PRELOAD "$VIRTUAL_ENV/lib/python3.11/site-packages/asan_with_fuzzer.so"

# 1. 暂时跳过内存分配失败，它们很常见，且影响较小（拒绝服务）
# 2. https://github.com/google/atheris/blob/master/native_extension_fuzzing.md#leak-detection
ENV ASAN_OPTIONS "allocator_may_return_null=1,detect_leaks=0"

CMD ["/bin/bash"]
```

构建并运行：
```bash
docker build -t atheris .
docker run -it atheris
```

### 验证

```bash
python -c "import atheris; print(atheris.__version__)"
```

## 编写 Harness

### 纯 Python 的 Harness 结构

```python
import sys
import atheris

@atheris.instrument_func
def TestOneInput(data: bytes):
    """
    模糊测试入口点。由模糊测试器提供随机字节序列调用。

    Args:
        data: 模糊测试器生成的随机字节
    """
    # 如有需要，添加输入验证
    if len(data) < 1:
        return

    # 调用目标函数
    try:
        your_target_function(data)
    except ValueError:
        # 预期的异常应该被捕获
        pass
    # 让未预期的异常导致崩溃（这正是我们寻找的！）

def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()

if __name__ == "__main__":
    main()
```

### 使用 FuzzedDataProvider 进行结构化输入

如果目标函数接受多个类型的参数，手动切片 `data` 会导致模糊测试器浪费大部分输入，因为每次变异都会改变其后的字节偏移。`atheris.FuzzedDataProvider` 可以将一个 `bytes` 输入分割为类型值：

```python
fdp = atheris.FuzzedDataProvider(data)
name = fdp.ConsumeUnicodeNoSurrogates(fdp.ConsumeIntInRange(0, 64))
strict = fdp.ConsumeBool()
```

有关完整的方法参考、固定绘制顺序规则以及缓冲区耗尽时每个方法返回的内容，请参阅 [structured-input.md](structured-input.md)。

### Harness 规则

| 做 | 不要 |
|----|-------|
| 使用 `@atheris.instrument_func` 进行覆盖率引导 | 忘记对目标代码进行覆盖率引导 |
| 捕获预期的异常 | 毫无区分地捕获所有异常 |
| 使用 `atheris.instrument_imports()` 进行库引导 | 在 `atheris.Setup()` 之后导入模块 |
| 保持 Harness 确定性 | 使用随机性或基于时间的行為 |

> **另见：** 有关详细的 Harness 编写技巧、处理复杂输入的模式和高级策略，请参阅 **fuzz-harness-writing** 技能。

## 模糊测试纯 Python 代码

对于模糊测试应用程序或库的更广泛部分，请使用 instrumentation 函数：

```python
import atheris
with atheris.instrument_imports():
    import your_module
    from another_module import target_function

def TestOneInput(data: bytes):
    target_function(data)

atheris.Setup(sys.argv, TestOneInput)
atheris.Fuzz()
```

**Instrumentation 选项：**
- `atheris.instrument_func` - 单个函数的装饰器
- `atheris.instrument_imports()` - 用于引导所有导入模块的上下文管理器
- `atheris.instrument_all()` - 系统范围内的所有 Python 代码引导

## 模糊测试 Python C 扩展

Python C 扩展需要使用特定的标志进行编译，以支持 instrumentation 和 sanitizer。

### 环境配置

如果使用提供的 Dockerfile，这些配置已经完成。对于本地设置：

```bash
export CC="clang"
export CFLAGS="-fsanitize=address,fuzzer-no-link"
export CXX="clang++"
export CXXFLAGS="-fsanitize=address,fuzzer-no-link"
export LDSHARED="clang -shared"
```

### 示例：模糊测试 cbor2

从源代码安装扩展：
```bash
CBOR2_BUILD_C_EXTENSION=1 uv add --no-binary-package cbor2 'cbor2==5.6.4'
```

`--no-binary-package` 标志确保本地编译 C 扩展，而不是使用预构建的轮包。使用 `no-binary-package = ["cbor2"]` 在 `pyproject.toml` 的 `[tool.uv]` 下持久化该选择，或者稍后使用 `uv sync` 可以无声地切换到未引导的轮包。

创建 `cbor2-fuzz.py`：
```python
import sys
import atheris

# _cbor2 确保导入 C 库
from _cbor2 import loads

def TestOneInput(data: bytes):
    try:
        loads(data)
    except Exception:
        # 我们在寻找内存损坏，而不是 Python 异常
        pass

def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()

if __name__ == "__main__":
    main()
```

运行：
```bash
uv run python cbor2-fuzz.py
```

> **重要：** 在本地运行时（非 Docker 环境），必须手动设置 `LD_PRELOAD` [https://github.com/google/atheris/blob/master/native_extension_fuzzing.md#option-a-sanitizerlibfuzzer-preloads](https://github.com/google/atheris/blob/master/native_extension_fuzzing.md#option-a-sanitizerlibfuzzer-preloads)。

## 语料库管理

### 创建初始语料库

```bash
mkdir corpus
# 添加种子输入
echo "test data" > corpus/seed1
echo '{"key": "value"}' > corpus/seed2
```

使用语料库运行：
```bash
uv run python fuzz.py corpus/
```

### 语料库最小化

Atheris 继承自 libFuzzer 的语料库最小化：
```bash
uv run python fuzz.py -merge=1 new_corpus/ old_corpus/
```

> **另见：** 有关语料库创建策略、字典和种子选择，请参阅 **fuzzing-corpus** 技能。

## 运行 Campaigns

### 基本运行

```bash
uv run python fuzz.py
```

### 使用语料库目录

```bash
uv run python fuzz.py corpus/
```

### 常见选项

```bash
# 运行 10 分钟
uv run python fuzz.py -max_total_time=600

# 限制输入大小
uv run python fuzz.py -max_len=1024

# 使用多个工作进程
uv run python fuzz.py -workers=4 -jobs=4
```

### 解释输出

| 输出 | 含义 |
|--------|---------|
| `NEW    cov: X` | 发现新的覆盖率，语料库扩展 |
| `pulse  cov: X` | 定期状态更新 |
| `exec/s: X` | 每秒执行次数（吞吐量） |
| `corp: X/Yb` | 语料库大小：X 个输入，Y 字节总计 |
| `ERROR: libFuzzer` | 检测到崩溃 |

## Sanitizer 集成

### AddressSanitizer (ASan)

当使用提供的 Docker 环境或使用适当的标志编译时，AddressSanitizer 会自动集成。

对于本地设置：
```bash
export CFLAGS="-fsanitize=address,fuzzer-no-link"
export CXXFLAGS="-fsanitize=address,fuzzer-no-link"
```

配置 ASan 行为：
```bash
export ASAN_OPTIONS="allocator_may_return_null=1,detect_leaks=0"
```

### LD_PRELOAD 配置

对于原生扩展模糊测试：
```bash
export LD_PRELOAD="$(python -c 'import atheris; import os; print(os.path.join(os.path.dirname(atheris.__file__), "asan_with_fuzzer.so"))')"
```

> **另见：** 有关详细的 sanitizer 配置、常见问题和高级标志，请参阅 **address-sanitizer** 和 **undefined-behavior-sanitizer** 技能。

### 常见 Sanitizer 问题

| 问题 | 解决方案 |
|-------|----------|
| `LD_PRELOAD` 未设置 | 设置 `LD_PRELOAD` 指向 `asan_with_fuzzer.so` 路径 |
| 内存分配失败 | 设置 `ASAN_OPTIONS=allocator_may_return_null=1` |
| 泄漏检测噪声 | 设置 `ASAN_OPTIONS=detect_leaks=0` |
| 缺少符号化器 | 设置 `ASAN_SYMBOLIZER_PATH` 为 `llvm-symbolizer` |

## 高级用法

### 提示和技巧

| 提示 | 帮助原因 |
|-----|--------------|
| 早期使用 `atheris.instrument_imports()` | 确保所有导入都为覆盖率引导 |
| 从小 `max_len` 开始 | 更快的初始模糊测试，逐步增加 |
| 使用字典处理结构化格式 | 帮助模糊测试器理解格式标记 |
| 运行多个并行实例 | 更好的覆盖率探索 |

### 自定义 Instrumentation

微调引导内容：
```python
import atheris

# 仅引导特定模块
with atheris.instrument_imports():
    import target_module
# 不要引导测试 harness 代码

def TestOneInput(data: bytes):
    target_module.parse(data)
```

### 性能调优

| 设置 | 影响 |
|---------|--------|
| `-max_len=N` | 较小的值 = 更快的执行 |
| `-workers=N -jobs=N` | 并行模糊测试以加快覆盖率 |
| `ASAN_OPTIONS=fast_unwind_on_malloc=0` | 更好的堆栈跟踪，执行变慢 |

### UndefinedBehaviorSanitizer (UBSan)

添加 UBSan 以捕获更多错误：
```bash
export CFLAGS="-fsanitize=address,undefined,fuzzer-no-link"
export CXXFLAGS="-fsanitize=address,undefined,fuzzer-no-link"
```

注意：如果使用容器化设置，请在 Dockerfile 中修改标志。

## 实际案例

两个完整的 harness —— 一个纯 Python 解析器和一个 HTTP 响应解析器 —— 在 [examples.md](examples.md) 中。

## 故障排除

| 问题 | 原因 | 解决方案 |
|---------|-------|----------|
| 没有覆盖率增加 | 种子语料库较差或目标未引导 | 添加更好的种子，验证 `instrument_imports()` |
| 执行缓慢 | ASan 开销或大输入 | 减少 `max_len`，使用 `ASAN_OPTIONS=fast_unwind_on_malloc=1` |
| 导入错误 | 在 instrumentation 之前导入模块 | 将导入移动到 `instrument_imports()` 上下文中 |
| 没有ASan输出就段错误 | 缺少 `LD_PRELOAD` | 设置 `LD_PRELOAD` 为 `asan_with_fuzzer.so` 路径 |
| 构建失败 | 错误的编译器或缺少标志 | 验证 `CC`、`CFLAGS` 和 clang 版本 |

## 相关技能

### 技能技巧

| 技能 | 用途 |
|-------|----------|
| **fuzz-harness-writing** | 编写有效 harness 的详细指导 |
| **address-sanitizer** | 模糊测试期间检测内存错误 |
| **undefined-behavior-sanitizer** | 捕获 C 扩展中的未定义行为 |
| **coverage-analysis** | 衡量和改进代码覆盖率 |
| **fuzzing-corpus** | 构建和管理种子语料库 |

### 相关模糊测试器

| 技能 | 考虑使用场景 |
|-------|------------------|
| **hypothesis** | 基于属性的测试，具有类型感知生成 |
| **python-afl** | 当 Atheris 不可用时，使用 AFL 风格的模糊测试 |

## 资源

### 关键外部资源

**[Atheris GitHub 仓库](https://github.com/google/atheris)**
官方仓库，包含安装说明、示例和文档，用于模糊测试纯 Python 和原生扩展。

**[Native Extension Fuzzing 指南](https://github.com/google/atheris/blob/master/native_extension_fuzzing.md)**
全面指南，涵盖编译标志、LD_PRELOAD 设置、sanitizer 配置和故障排除，适用于 Python C 扩展。

**[Continuously Fuzzing Python C Extensions](https://blog.trailofbits.com/2024/02/23/continuously-fuzzing-python-c-extensions/)**
Trail of Bits 博客文章，涵盖 CI/CD 集成、ClusterFuzzLite 设置和实际案例，展示如何在持续集成管道中模糊测试 Python C 扩展。

**[ClusterFuzzLite Python 集成](https://google.github.io/clusterfuzzlite/build-integration/python-lang/)**
指南，用于将 Atheris 模糊测试集成到 CI/CD 管道中，使用 ClusterFuzzLite 进行自动化持续模糊测试。

### 视频资源

Atheris 文档和 libFuzzer 资源中提供视频和教程。
