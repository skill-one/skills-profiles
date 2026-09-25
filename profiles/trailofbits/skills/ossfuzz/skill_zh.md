# OSS-Fuzz

[OSS-Fuzz](https://google.github.io/oss-fuzz/) 是由 Google 开发的开源项目，它提供免费的分布式基础设施用于持续模糊测试。它简化了模糊测试流程，并促进了更简单的修改。虽然只有部分项目会被接受到 OSS-Fuzz 中，但该项目的核心是开源的，允许任何人为自己的私有项目托管自己的实例。

## 概述

OSS-Fuzz 提供了一个简单的 CLI 框架，用于构建和启动 harness 或计算它们的覆盖率。此外，OSS-Fuzz 还可以用作服务，托管从模糊测试输出（如覆盖率信息）生成的静态网页。

### 关键概念

| 概念 | 描述 |
|------|-------------|
| **helper.py** | 用于构建镜像、构建模糊器以及本地运行 harness 的 CLI 脚本 |
| **基础镜像** | 提供构建依赖项和编译器的分层 Docker 镜像 |
| **project.yaml** | 定义 OSS-Fuzz 入选项目元数据的配置文件 |
| **Dockerfile** | 具有构建依赖项的项目特定镜像 |
| **build.sh** | 为您的项目构建模糊测试 harness 的脚本 |
| **关键性分数** | OSS-Fuzz 团队用于评估项目接受度的指标 |

## 何时应用

**在以下情况下应用此技术：**
- 为开源项目设置持续模糊测试
- 需要分布式模糊测试基础设施，而无需管理服务器
- 希望覆盖率报告和错误跟踪与模糊测试集成
- 在本地测试现有的 OSS-Fuzz harness
- 复现 OSS-Fuzz 错误报告中的崩溃

**跳过此技术的情况：**
- 项目是闭源的（除非您自己托管 OSS-Fuzz 实例）
- 项目未达到 OSS-Fuzz 的关键性分数阈值
- 需要专有或专门的模糊测试基础设施
- 模糊测试简单的脚本，不值得使用基础设施

## 快速参考

| 任务 | 命令 |
|------|---------|
| 克隆 OSS-Fuzz | `git clone https://github.com/google/oss-fuzz` |
| 构建项目镜像 | `uv run --no-project python infra/helper.py build_image --pull <project>` |
| 使用 ASan 构建模糊器 | `uv run --no-project python infra/helper.py build_fuzzers --sanitizer=address <project>` |
| 运行特定的 harness | `uv run --no-project python infra/helper.py run_fuzzer <project> <harness>` |
| 生成覆盖率报告 | `uv run --no-project python infra/helper.py coverage <project>` |
| 检查 helper.py 选项 | `uv run --no-project python infra/helper.py --help` |

## OSS-Fuzz 项目组件

OSS-Fuzz 提供了一些公开可用的工具和网络界面：

### 错误跟踪器

错误跟踪器 [https://issues.oss-fuzz.com/issues?q=status:open](https://issues.oss-fuzz.com/issues?q=status:open) 允许您：
- 检查特定项目的错误（最初仅对维护者可见，后来 [公开](https://google.github.io/oss-fuzz/getting-started/bug-disclosure-guidelines/)）
- 创建新问题并在现有问题上进行评论
- 搜索所有项目中的类似错误以了解问题

### 构建状态系统

构建状态系统 [https://oss-fuzz-build-logs.storage.googleapis.com/index.html](https://oss-fuzz-build-logs.storage.googleapis.com/index.html) 帮助跟踪：
- 所有包含项目的构建状态
- 最后一次成功构建的日期
- 构建失败及其持续时间

### 模糊分析器

模糊分析器 [https://oss-fuzz-introspector.storage.googleapis.com/index.html](https://oss-fuzz-introspector.storage.googleapis.com/index.html) 显示：
- 已加入 OSS-Fuzz 的项目的覆盖率数据
- 覆盖代码的命中频率
- 性能分析和阻塞器识别

阅读 [此案例研究](https://github.com/ossf/fuzz-introspector/blob/main/doc/CaseStudies.md) 获取示例和解释。

## 分步指南：运行单个 harness

您不需要托管整个 OSS-Fuzz 平台即可使用它。helper 脚本使运行单个 harness 变得容易。

### 第 1 步：克隆 OSS-Fuzz

```bash
git clone https://github.com/google/oss-fuzz
cd oss-fuzz
uv run --no-project python infra/helper.py --help
```

### 第 2 步：构建项目镜像

```bash
uv run --no-project python infra/helper.py build_image --pull <project-name>
```

这将下载并构建项目的 base Docker 镜像。

### 第 3 步：使用 Sanitizers 构建 Fuzzers

```bash
uv run --no-project python infra/helper.py build_fuzzers --sanitizer=address <project-name>
```

**Sanitizer 选项：**
- `--sanitizer=address` 用于 [AddressSanitizer](https://appsec.guide/docs/fuzzing/techniques/asan/) 和 [LeakSanitizer](https://github.com/google/sanitizers/wiki/AddressSanitizerLeakSanitizer)
- 其他 sanitizer 可用（语言支持各不相同）

**注意：** Fuzzers 会构建到 `/build/out/<project-name>/`，其中包含 harness 可执行文件、字典、语料库和崩溃文件。

### 第 4 步：运行 Fuzzer

```bash
uv run --no-project python infra/helper.py run_fuzzer <project-name> <harness-name> [<fuzzer-args>]
```

helper 脚本会自动运行任何跳过的步骤。

### 第 5 步：覆盖率分析（可选）

首先，[安装 gsutil](https://cloud.google.com/storage/docs/gsutil_install)（跳过 gcloud 初始化）。

```bash
uv run --no-project python infra/helper.py build_fuzzers --sanitizer=coverage <project-name>
uv run --no-project python infra/helper.py coverage <project-name>
```

使用 `--no-corpus-download` 仅使用本地语料库。该命令会生成并本地托管覆盖率报告。

有关详细信息，请参阅 [官方 OSS-Fuzz 文档](https://google.github.io/oss-fuzz/advanced-topics/code-coverage/)。

## 常见模式

### 模式：运行 irssi 示例

**用例：** 使用简单的已注册项目测试 OSS-Fuzz 设置

```bash
# 克隆并导航到 OSS-Fuzz
git clone https://github.com/google/oss-fuzz
cd oss-fuzz

# 构建并运行 irssi fuzzer
uv run --no-project python infra/helper.py build_image --pull irssi
uv run --no-project python infra/helper.py build_fuzzers --sanitizer=address irssi
uv run --no-project python infra/helper.py run_fuzzer irssi irssi-fuzz
```

**预期输出：**
```
INFO:__main__:Running: docker run --rm --privileged --shm-size=2g --platform linux/amd64 -i -e FUZZING_ENGINE=libfuzzer -e SANITIZER=address -e RUN_FUZZER_MODE=interactive -e HELPER=True -v /private/tmp/oss-fuzz/build/out/irssi:/out -t gcr.io/oss-fuzz-base/base-runner run_fuzzer irssi-fuzz.
Using seed corpus: irssi-fuzz_seed_corpus.zip
/out/irssi-fuzz -rss_limit_mb=2560 -timeout=25 /tmp/irssi-fuzz_corpus -max_len=2048 < /dev/null
INFO: Running with entropic power schedule (0xFF, 100).
INFO: Seed: 1531341664
INFO: Loaded 1 modules   (95687 inline 8-bit counters): 95687 [0x1096c80, 0x10ae247),
INFO: Loaded 1 PC tables (95687 PCs): 95687 [0x10ae248,0x1223eb8),
INFO:      719 files found in /tmp/irssi-fuzz_corpus
INFO: seed corpus: files: 719 min: 1b max: 170106b total: 367969b rss: 48Mb
#720        INITED cov: 409 ft: 1738 corp: 640/163Kb exec/s: 0 rss: 62Mb
#762        REDUCE cov: 409 ft: 1738 corp: 640/163Kb lim: 2048 exec/s: 0 rss: 63Mb L: 236/2048 MS: 2 ShuffleBytes-EraseBytes-
```

### 模式：注册新项目

**用例：** 将您的项目添加到 OSS-Fuzz（或私有实例）

在 `projects/<your-project>/` 中创建三个文件：

**1. project.yaml** - 项目元数据：
```yaml
homepage: "https://github.com/yourorg/yourproject"
language: c++
primary_contact: "your-email@example.com"
main_repo: "https://github.com/yourorg/yourproject"
fuzzing_engines:
  - libfuzzer
sanitizers:
  - address
  - undefined
```

**2. Dockerfile** - 构建依赖项：
```dockerfile
FROM gcr.io/oss-fuzz-base/base-builder
RUN apt-get update && apt-get install -y \
    autoconf \
    automake \
    libtool \
    pkg-config
RUN git clone --depth 1 https://github.com/yourorg/yourproject
WORKDIR yourproject
COPY build.sh $SRC/
```

**3. build.sh** - 构建 harness：
```bash
#!/bin/bash -eu
./autogen.sh
./configure --disable-shared
make -j$(nproc)

# 构建 harnesses
$CXX $CXXFLAGS -std=c++11 -I. \
    $SRC/yourproject/fuzz/harness.cc -o $OUT/harness \
    $LIB_FUZZING_ENGINE ./libyourproject.a

# 如果可用，复制语料库和字典
cp $SRC/yourproject/fuzz/corpus.zip $OUT/harness_seed_corpus.zip
cp $SRC/yourproject/fuzz/dictionary.dict $OUT/harness.dict
```

## OSS-Fuzz 中的 Docker 镜像

Harnesses 在 Docker 容器中构建和执行。所有项目共享一个 runner 镜像，但每个项目都有自己的构建镜像。

### 镜像层次结构

镜像按以下顺序构建：

1. **[base_image](https://github.com/google/oss-fuzz/blob/master/infra/base-images/base-image/Dockerfile)** - 特定的 Ubuntu 版本
2. **[base_clang](https://github.com/google/oss-fuzz/tree/master/infra/base-images/base-clang)** - Clang 编译器；基于 `base_image`
3. **[base_builder](https://github.com/google/oss-fuzz/tree/master/infra/base-images/base-builder)** - 构建依赖项；基于 `base_clang`
   - 语言特定变体：[`base_builder_go`](https://github.com/google/oss-fuzz/tree/master/infra/base-images/base-builder-go)，等等
   - 查看 [/oss-fuzz/infra/base-images/](https://github.com/google/oss-fuzz/tree/master/infra/base-images) 获取完整列表
4. **您的项目 Docker 镜像** - 项目特定依赖项；基于 `base_builder` 或语言变体

### Runner 镜像（单独使用）

- **[base_runner](https://github.com/google/oss-fuzz/tree/master/infra/base-images/base-runner)** - 执行 harness；基于 `base_clang`
- **[base_runner_debug](https://github.com/google/oss-fuzz/tree/master/infra/base-images/base-runner-debug)** - 带有调试工具；基于 `base_runner`

## 高级用法

### 提示和技巧

| 提示 | 有何帮助 |
|-----|--------------|
| **不要手动复制源代码** | 项目 Dockerfile 可能已经拉取了最新版本 |
| **查看现有项目** | 浏览 [oss-fuzz/projects](https://github.com/google/oss-fuzz/tree/master/projects) 获取示例 |
| **将 harness 存放在单独的仓库中** | 如 [curl-fuzzer](https://github.com/curl/curl-fuzzer) - 更清晰的组织 |
| **使用特定编译器版本** | Base images 提供一致的构建环境 |
| **在 Dockerfile 中安装依赖项** | 可能需要批准才能将项目加入 OSS-Fuzz |

### 关键性分数

OSS-Fuzz 使用 [关键性分数](https://github.com/ossf/criticality_score) 来评估项目接受度。查看 [此示例](https://github.com/google/oss-fuzz/pull/11444#issuecomment-1875907472) 了解评分方式。

关键性分数较低的项目仍可能被添加到私有 OSS-Fuzz 实例中。

### 托管自己的实例

由于 OSS-Fuzz 是开源的，您可以托管自己的实例用于：
- 不符合公开 OSS-Fuzz 条件的项目
- 关键性分数较低的项目
- 定制模糊测试基础设施需求

## 反模式

| 反模式 | 问题 | 正确方法 |
|--------------|---------|------------------|
| **在 build.sh 中手动拉取源代码** | 不会使用最新版本 | 让 Dockerfile 处理 git clone |
| **将代码复制到 OSS-Fuzz 仓库** | 难以维护，违反分离原则 | 引用外部 harness 仓库 |
| **忽略 base image 版本** | 构建不一致 | 使用提供的 base images 和编译器 |
| **跳过本地测试** | 浪费 CI 资源 | 在 PR 之前使用 helper.py 本地测试 |
| **不检查构建状态** | 未注意到的构建失败 | 定期监控构建状态页面 |

## 工具特定指南

### libFuzzer

OSS-Fuzz 主要使用 libFuzzer 作为 C/C++ 项目的模糊测试引擎。

**Harness 签名：**
```c++
extern "C" int LLVMFuzzerTestOneInput(const uint8_t *data, size_t size) {
    // 您的模糊测试逻辑
    return 0;
}
```

**在 build.sh 中构建：**
```bash
$CXX $CXXFLAGS -std=c++11 -I. \
    harness.cc -o $OUT/harness \
    $LIB_FUZZING_ENGINE ./libproject.a
```

**集成技巧：**
- 使用 OSS-Fuzz 提供的 `$LIB_FUZZING_ENGINE` 变量
- 包含 `-fsanitize=fuzzer` 会自动处理
- 尽可能链接静态库

### AFL++

OSS-Fuzz 支持 AFL++ 作为另一种模糊测试引擎。

**在 project.yaml 中启用：**
```yaml
fuzzing_engines:
  - afl
  - libfuzzer
```

**集成技巧：**
- AFL++ harness 与 libFuzzer harness 并用
- 使用持久模式以获得更好的性能
- OSS-Fuzz 处理引擎特定的编译标志

### Atheris (Python)

用于具有 C 扩展的 Python 项目。

**来自 [cbor2 集成](https://github.com/google/oss-fuzz/pull/11444) 的示例：**

**Harness：**
```python
import atheris
import sys
import cbor2

@atheris.instrument_func
def TestOneInput(data):
    fdp = atheris.FuzzedDataProvider(data)
    try:
        cbor2.loads(data)
    except (cbor2.CBORDecodeError, ValueError):
        pass

def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()

if __name__ == "__main__":
    main()
```

**在 build.sh 中构建：**
```bash
# allow-legacy-python: build.sh 在 oss-fuzz 容器中运行，其中缺少 shims。
pip3 install .
for fuzzer in $(find $SRC -name 'fuzz_*.py'); do
  compile_python_fuzzer $fuzzer
done
```

**集成技巧：**
- 使用 OSS-Fuzz 提供的 `compile_python_fuzzer` 辅助程序
- 查看 [Continuously Fuzzing Python C Extensions](https://blog.trailofbits.com/2024/02/23/continuously-fuzzing-python-c-extensions/) 博客文章

### Rust 项目

**在 project.yaml 中启用：**
```yaml
language: rust
fuzzing_engines:
  - libfuzzer
sanitizers:
  - address  # Rust 仅支持 AddressSanitizer
```

**在 build.sh 中构建：**
```bash
cargo fuzz build -O --debug-assertions
cp fuzz/target/x86_64-unknown-linux-gnu/release/fuzz_target_1 $OUT/
```

**集成技巧：**
- [Rust 仅支持 AddressSanitizer 与 libfuzzer](https://google.github.io/oss-fuzz/getting-started/new-project-guide/rust-lang/#projectyaml)
- 使用 cargo-fuzz 进行本地开发
- OSS-Fuzz 处理 Rust 特定的编译

## 故障排除

| 问题 | 原因 | 解决方案 |
|-------|-------|----------|
| **构建因缺少依赖项而失败** | 依赖项不在 Dockerfile 中 | 在 Dockerfile 中添加 `apt-get install` 或等效命令 |
| **Harness 立即崩溃** | 缺少输入验证 | 在 harness 中添加大小检查 |
| **覆盖率是 0%** | Harness 未到达目标代码 | 验证 harness 实际调用目标函数 |
| **构建超时** | 复杂的构建过程 | 优化 build.sh，考虑并行构建 |
| **构建中的 sanitizer 错误** | 不兼容的标志 | 使用 OSS-Fuzz 环境变量提供的标志 |
| **找不到源代码** | Dockerfile 中的工作目录错误 | 设置 WORKDIR 或使用绝对路径 |

## 相关技能

### 使用此技术的工具

| 技能 | 如何应用 |
|-------|----------------|
| **libfuzzer** | OSS-Fuzz 主要使用的模糊测试引擎 |
| **aflpp** | OSS-Fuzz 支持的另一种模糊测试引擎 |
| **atheris** | 用于模糊测试 Python 项目 |
| **cargo-fuzz** | 用于 Rust 项目 |

### 相关技术

| 技能 | 关系 |
|-------|--------------|
| **覆盖率分析** | OSS-Fuzz 通过 helper.py 生成覆盖率报告 |
| **AddressSanitizer** | OSS-Fuzz 项目的默认 sanitizer |
| **Fuzz Harness 编写** | 在 OSS-Fuzz 中注册项目的必要技能 |
| **语料库管理** | OSS-Fuzz 维护已注册项目的语料库 |

## 资源

### 关键外部资源

**[OSS-Fuzz 官方文档](https://google.github.io/oss-fuzz/)**
涵盖 OSS-Fuzz 平台注册、harness 编写和故障排除的综合文档。

**[入门指南](https://google.github.io/oss-fuzz/getting-started/accepting-new-projects/)**
将新项目注册到 OSS-Fuzz 的分步过程，包括要求和审批流程。

**[cbor2 OSS-Fuzz 集成 PR](https://github.com/google/oss-fuzz/pull/11444)**
将 Python 项目与 C 扩展注册到 OSS-Fuzz 的实际示例。显示：
- 初始提案和项目介绍
- 关键性分数评估
- 完整实现（project.yaml、Dockerfile、build.sh、harnesses）

**[Fuzz Introspector 案例研究](https://github.com/ossf/fuzz-introspector/blob/main/doc/CaseStudies.md)**
使用 Fuzz Introspector 分析覆盖率和识别模糊测试阻塞器的示例和解释。

### 视频资源

查看 OSS-Fuzz 文档，了解关于注册和 harness 开发的研讨会录像和教程。
