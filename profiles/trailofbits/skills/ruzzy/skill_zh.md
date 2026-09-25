# Ruzzy

Ruzzy 是一个基于 libFuzzer 构建的、用于 Ruby 的覆盖率引导模糊测试器。它支持模糊测试纯 Ruby 代码和 Ruby C 扩展，并具有卫生器支持，用于检测内存损坏和未定义行为。

## 使用场景

Ruzzy 目前是唯一一个可用于 Ruby 的生产级覆盖率引导模糊测试器。

**选择 Ruzzy 的情况：**
- 模糊测试 Ruby 应用程序或库
- 测试 Ruby C 扩展以发现内存安全问题
- 需要 Ruby 代码的覆盖率引导模糊测试
- 使用具有原生扩展的 Ruby gem

## 快速入门

设置环境：
```bash
export ASAN_OPTIONS="allocator_may_return_null=1:detect_leaks=0:use_sigaltstack=0"
```

使用内置的示例进行测试：
```bash
LD_PRELOAD=$(ruby -e 'require "ruzzy"; print Ruzzy::ASAN_PATH') \
    ruby -e 'require "ruzzy"; Ruzzy.dummy'
```

这应该能快速找到一个崩溃，证明 Ruzzy 工作正常。

## 安装

### 支持的平台

Ruzzy 支持 Linux x86-64 和 AArch64/ARM64。对于 macOS 或 Windows，请使用 [Dockerfile](https://github.com/trailofbits/ruzzy/blob/main/Dockerfile) 或 [开发环境](https://github.com/trailofbits/ruzzy#developing)。

### 前置条件

- Linux x86-64 或 AArch64/ARM64
- 较新版本的 clang（测试到 14.0.0，推荐使用最新版本）
- 安装了 gem 的 Ruby

### 安装命令

使用 clang 编译器标志安装 Ruzzy：
```bash
MAKE="make --environment-overrides V=1" \
CC="/path/to/clang" \
CXX="/path/to/clang++" \
LDSHARED="/path/to/clang -shared" \
LDSHAREDXX="/path/to/clang++ -shared" \
    gem install ruzzy
```

**环境变量说明：**
- `MAKE`：覆盖 make 以尊重后续环境变量
- `CC`, `CXX`, `LDSHARED`, `LDSHAREDXX`：确保使用正确的 clang 二进制文件以支持最新特性

### 安装故障排除

如果安装失败，启用调试输出：
```bash
RUZZY_DEBUG=1 gem install --verbose ruzzy
```

### 验证

通过运行示例（见快速入门部分）来验证安装。

## 编写测试程序

### 模糊测试纯 Ruby 代码

由于 Ruby 解释器的实现细节，纯 Ruby 模糊测试需要两个脚本。

**跟踪脚本 (`test_tracer.rb`)：**
```ruby
# frozen_string_literal: true

require 'ruzzy'

Ruzzy.trace('test_harness.rb')
```

**测试程序脚本 (`test_harness.rb`)：**
```ruby
# frozen_string_literal: true

require 'ruzzy'

def fuzzing_target(input)
  # 在这里编写模糊测试的代码
  if input.length == 4
    if input[0] == 'F'
      if input[1] == 'U'
        if input[2] == 'Z'
          if input[3] == 'Z'
            raise
          end
        end
      end
    end
  end
end

test_one_input = lambda do |data|
  fuzzing_target(data)
  return 0
end

Ruzzy.fuzz(test_one_input)
```

使用以下命令运行：
```bash
LD_PRELOAD=$(ruby -e 'require "ruzzy"; print Ruzzy::ASAN_PATH') \
    ruby test_tracer.rb
```

### 模糊测试 Ruby C 扩展

C 扩展可以使用单个测试程序文件进行模糊测试，不需要跟踪脚本。

**用于 msgpack 的示例测试程序 (`fuzz_msgpack.rb`)：**
```ruby
# frozen_string_literal: true

require 'msgpack'
require 'ruzzy'

test_one_input = lambda do |data|
  begin
    MessagePack.unpack(data)
  rescue Exception
    # 我们寻找的是内存损坏，而不是 Ruby 异常
  end
  return 0
end

Ruzzy.fuzz(test_one_input)
```

使用以下命令运行：
```bash
LD_PRELOAD=$(ruby -e 'require "ruzzy"; print Ruzzy::ASAN_PATH') \
    ruby fuzz_msgpack.rb
```

### 测试程序规则

| 应该做 | 不应该做 |
|----|-------|
| 测试 C 扩展时捕获 Ruby 异常 | 让 Ruby 异常导致模糊测试器崩溃 |
| 从 `test_one_input` lambda 返回 0 | 返回其他值 |
| 保持测试程序确定性 | 使用随机性或基于时间的逻辑 |
| 使用跟踪脚本进行纯 Ruby | 对于纯 Ruby 代码跳过跟踪脚本 |

> **另见：** 关于编写测试程序的详细技术、处理复杂输入的模式和高级策略，请参阅 **fuzz-harness-writing** 技能。

## 编译

### 使用卫生器安装 Gem

在模糊测试具有 C 扩展的 Ruby gem 时，使用卫生器标志进行编译：
```bash
MAKE="make --environment-overrides V=1" \
CC="/path/to/clang" \
CXX="/path/to/clang++" \
LDSHARED="/path/to/clang -shared" \
LDSHAREDXX="/path/to/clang++ -shared" \
CFLAGS="-fsanitize=address,fuzzer-no-link -fno-omit-frame-pointer -fno-common -fPIC -g" \
CXXFLAGS="-fsanitize=address,fuzzer-no-link -fno-omit-frame-pointer -fno-common -fPIC -g" \
    gem install <gem-name>
```

### 构建标志

| 标志 | 目的 |
|------|---------|
| `-fsanitize=address,fuzzer-no-link` | 启用 AddressSanitizer 和模糊测试器指令 |
| `-fno-omit-frame-pointer` | 提高堆栈跟踪质量 |
| `-fno-common` | 与卫生器更好的兼容性 |
| `-fPIC` | 用于共享库的位置无关代码 |
| `-g` | 包含调试符号 |

## 运行测试活动

### 环境设置

在运行任何模糊测试活动之前，设置 ASAN_OPTIONS：
```bash
export ASAN_OPTIONS="allocator_may_return_null=1:detect_leaks=0:use_sigaltstack=0"
```

**选项说明：**
1. `allocator_may_return_null=1`：跳过低影响的常见分配失败（拒绝服务）
2. `detect_leaks=0`：Ruby 解释器泄漏数据，暂时忽略这些
3. `use_sigaltstack=0`：Ruby 建议禁用 sigaltstack 与 ASan

### 基本运行

```bash
LD_PRELOAD=$(ruby -e 'require "ruzzy"; print Ruzzy::ASAN_PATH') \
    ruby harness.rb
```

**注意：** `LD_PRELOAD` 是必需的，用于注入卫生器。与 `ASAN_OPTIONS` 不同，不要将其导出，因为它可能会干扰其他程序。

### 使用语料库

```bash
LD_PRELOAD=$(ruby -e 'require "ruzzy"; print Ruzzy::ASAN_PATH') \
    ruby harness.rb /path/to/corpus
```

### 传递 libFuzzer 选项

所有 libFuzzer 选项都可以作为参数传递：
```bash
LD_PRELOAD=$(ruby -e 'require "ruzzy"; print Ruzzy::ASAN_PATH') \
    ruby harness.rb /path/to/corpus -max_len=1024 -timeout=10
```

有关完整参考，请参阅 [libFuzzer 选项](https://llvm.org/docs/LibFuzzer.html#options)。

### 重复崩溃

通过传递崩溃文件重新运行崩溃案例：
```bash
LD_PRELOAD=$(ruby -e 'require "ruzzy"; print Ruzzy::ASAN_PATH') \
    ruby harness.rb ./crash-253420c1158bc6382093d409ce2e9cff5806e980
```

### 解释输出

| 输出 | 含义 |
|--------|---------|
| `INFO: Running with entropic power schedule` | 模糊测试活动已开始 |
| `ERROR: AddressSanitizer: heap-use-after-free` | 检测到内存损坏 |
| `SUMMARY: libFuzzer: fuzz target exited` | Ruby 异常发生 |
| `artifact_prefix='./'; Test unit written to ./crash-*` | 保存崩溃输入 |
| `Base64: ...` | 崩溃输入的 Base64 编码 |

## 卫生器集成

### AddressSanitizer (ASan)

Ruzzy 包含预编译的 AddressSanitizer 库：
```bash
LD_PRELOAD=$(ruby -e 'require "ruzzy"; print Ruzzy::ASAN_PATH') \
    ruby harness.rb
```

使用 ASan 检测：
- 堆缓冲区溢出
- 栈缓冲区溢出
- 用后释放
- 双重释放
- 内存泄漏（Ruzzy 默认禁用）

### UndefinedBehaviorSanitizer (UBSan)

Ruzzy 还包含 UBSan：
```bash
LD_PRELOAD=$(ruby -e 'require "ruzzy"; print Ruzzy::UBSAN_PATH') \
    ruby harness.rb
```

使用 UBSan 检测：
- 有符号整数溢出
- 空指针解引用
- 未对齐的内存访问
- 除以零

### 常见卫生器问题

| 问题 | 解决方案 |
|-------|----------|
| Ruby 解释器泄漏警告 | 使用 `ASAN_OPTIONS=detect_leaks=0` |
| Sigaltstack 冲突 | 使用 `ASAN_OPTIONS=use_sigaltstack=0` |
| 分配失败信息 | 使用 `ASAN_OPTIONS=allocator_may_return_null=1` |
| LD_PRELOAD 干扰工具 | 不要导出它；使用 ruby 命令内联设置 |

> **另见：** 关于详细卫生器配置、常见问题和高级标志，请参阅 **address-sanitizer** 和 **undefined-behavior-sanitizer** 技能。

## 真实案例

### 案例：msgpack-ruby

模糊测试 msgpack MessagePack 解析器以发现内存损坏。

**使用卫生器安装：**
```bash
MAKE="make --environment-overrides V=1" \
CC="/path/to/clang" \
CXX="/path/to/clang++" \
LDSHARED="/path/to/clang -shared" \
LDSHAREDXX="/path/to/clang++ -shared" \
CFLAGS="-fsanitize=address,fuzzer-no-link -fno-omit-frame-pointer -fno-common -fPIC -g" \
CXXFLAGS="-fsanitize=address,fuzzer-no-link -fno-omit-frame-pointer -fno-common -fPIC -g" \
    gem install msgpack
```

**测试程序 (`fuzz_msgpack.rb`)：**
```ruby
# frozen_string_literal: true

require 'msgpack'
require 'ruzzy'

test_one_input = lambda do |data|
  begin
    MessagePack.unpack(data)
  rescue Exception
    # 我们寻找的是内存损坏，而不是 Ruby 异常
  end
  return 0
end

Ruzzy.fuzz(test_one_input)
```

**运行：**
```bash
export ASAN_OPTIONS="allocator_may_return_null=1:detect_leaks=0:use_sigaltstack=0"
LD_PRELOAD=$(ruby -e 'require "ruzzy"; print Ruzzy::ASAN_PATH') \
    ruby fuzz_msgpack.rb
```

### 案例：纯 Ruby 目标

使用自定义解析器模糊测试纯 Ruby 代码。

**跟踪脚本 (`test_tracer.rb`)：**
```ruby
# frozen_string_literal: true

require 'ruzzy'

Ruzzy.trace('test_harness.rb')
```

**测试程序脚本 (`test_harness.rb`)：**
```ruby
# frozen_string_literal: true

require 'ruzzy'
require_relative 'my_parser'

test_one_input = lambda do |data|
  begin
    MyParser.parse(data)
  rescue StandardError
    # 预期的来自格式化输入的异常
  end
  return 0
end

Ruzzy.fuzz(test_one_input)
```

**运行：**
```bash
export ASAN_OPTIONS="allocator_may_return_null=1:detect_leaks=0:use_sigaltstack=0"
LD_PRELOAD=$(ruby -e 'require "ruzzy"; print Ruzzy::ASAN_PATH') \
    ruby test_tracer.rb
```

## 故障排除

| 问题 | 原因 | 解决方案 |
|---------|-------|----------|
| 安装失败 | clang 版本或路径错误 | 验证 clang 路径，使用 clang 14.0.0+ |
| `cannot open shared object file` | 未设置 LD_PRELOAD | 使用 ruby 命令内联设置 LD_PRELOAD |
| 模糊测试器立即退出 | 缺少语料库目录 | 创建语料库目录或作为参数传递 |
| 没有覆盖率进度 | 纯 Ruby 需要跟踪脚本 | 使用跟踪脚本进行纯 Ruby 代码 |
| 泄漏检测信息 | Ruby 解释器泄漏 | 设置 `ASAN_OPTIONS=detect_leaks=0` |
| 需要安装调试 | 编译错误 | 使用 `RUZZY_DEBUG=1 gem install --verbose ruzzy` |

## 相关技能

### 技能技能

| 技能 | 使用场景 |
|-------|----------|
| **fuzz-harness-writing** | 编写有效测试程序的详细指导 |
| **address-sanitizer** | 在模糊测试期间检测内存错误 |
| **undefined-behavior-sanitizer** | 检测 C 扩展中的未定义行为 |
| **libfuzzer** | 理解 libFuzzer 选项（Ruzzy 基于 libFuzzer 构建） |

### 相关模糊测试器

| 技能 | 考虑使用时 |
|-------|------------------|
| **libfuzzer** | 当直接在 C/C++ 中模糊测试 Ruby C 扩展代码时 |
| **aflpp** | 作为模糊测试 Ruby 的替代方法，通过在 Ruby 解释器中注入进行 |

## 资源

### 关键外部资源

**[介绍 Ruzzy，一个覆盖率引导的 Ruby 模糊测试器](https://blog.trailofbits.com/2024/03/29/introducing-ruzzy-a-coverage-guided-ruby-fuzzer/)**
官方 Trail of Bits 博客文章，宣布 Ruzzy，涵盖动机、架构和初步结果。

**[Ruzzy GitHub 仓库](https://github.com/trailofbits/ruzzy)**
源代码、附加示例和开发说明。

**[libFuzzer 文档](https://llvm.org/docs/LibFuzzer.html)**
由于 Ruzzy 基于 libFuzzer，理解 libFuzzer 选项和行为是有价值的。

**[模糊测试 Ruby C 扩展](https://github.com/trailofbits/ruzzy#fuzzing-ruby-c-extensions)**
关于使用编译标志和示例的详细指南。

**[模糊测试纯 Ruby 代码](https://github.com/trailofbits/ruzzy#fuzzing-pure-ruby-code)**
关于纯 Ruby 模糊测试所需的跟踪模式的详细指南。
