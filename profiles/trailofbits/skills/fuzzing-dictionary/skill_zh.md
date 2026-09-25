# Fuzzing Dictionary

Fuzzing dictionary提供特定领域的标记，指导模糊测试器生成有趣的输入。模糊测试器不仅进行纯粹的随机变异，还会结合已知的关键词、魔法数字、协议命令以及更可能到达解析器、协议处理器和文件格式处理器中更深层代码路径的格式特定字符串。

## 概述

字典是包含引号字符串的文本文件，这些字符串代表目标中的有意义的标记。它们帮助模糊测试器绕过早期验证检查，并探索通过盲目变异难以到达的代码路径。

### 关键概念

| 概念 | 描述 |
|------|-------------|
| **字典条目** | 引号字符串（例如，`"keyword"`）或键值对（例如，`kw="value"`） |
| **十六进制转义** | 非打印字符的字节序列，如`"\xF7\xF8"` |
| **标记注入** | 模糊测试器将字典条目注入生成的输入中 |
| **跨模糊测试器格式** | 字典文件可与libFuzzer、AFL++和cargo-fuzz一起使用 |

## 何时应用

**应用此技术时：**
- 模糊测试解析器（JSON、XML、配置文件）
- 模糊测试协议实现（HTTP、DNS、自定义协议）
- 模糊测试文件格式处理程序（PNG、PDF、媒体编解码器）
- 早期覆盖率停滞，未达到深层逻辑
- 目标代码检查特定关键词或魔法值

**跳过此技术时：**
- 模糊测试纯算法，无格式预期
- 目标没有基于关键词的解析
- 语料库已实现高覆盖率

## 快速参考

| 任务 | 命令/模式 |
|------|-----------------|
| 与libFuzzer一起使用 | `./fuzz -dict=./dictionary.dict ...` |
| 与AFL++一起使用 | `afl-fuzz -x ./dictionary.dict ...` |
| 与cargo-fuzz一起使用 | `cargo fuzz run fuzz_target -- -dict=./dictionary.dict` |
| 从头文件中提取 | `grep -o '".*"' header.h > header.dict` |
| 从二进制文件中生成 | `strings ./binary \| sed 's/^/"&/; s/$/&"/' > strings.dict` |

## 分步指南

### 第1步：创建字典文件

创建一个每行包含引号字符串的文本文件。使用注释（`#`）进行文档说明。

**示例字典格式：**

```conf
# 以'#'开头的行和空行将被忽略。

# 向字典添加"blah"（不带引号）。
kw1="blah"
# 使用\\表示反斜杠，\"表示引号。
kw2="\"ac\\dc\""
# 使用\xAB表示十六进制值
kw3="\xF7\xF8"
# 关键词的名称后跟'='可以省略：
"foo\x0Abar"
```

### 第2步：生成字典内容

根据可用资源选择生成方法：

**从LLM生成：** 向ChatGPT或Claude提示：
```text
字典可用于指导模糊测试器。为我编写一个用于模糊测试<PNG解析器>的字典文件。每行应是一个引号字符串或键值对，如kw="value"。包含魔法字节、块类型和常见头值。使用十六进制转义，如"\xF7\xF8"表示二进制值。
```

**从头文件生成：**
```bash
grep -o '".*"' header.h > header.dict
```

**从man页面（用于CLI工具）：**
```bash
man curl | grep -oP '^\s*(--|-)\K\S+' | sed 's/[,.]$//' | sed 's/^/"&/; s/$/&"/' | sort -u > man.dict
```

**从二进制字符串生成：**
```bash
strings ./binary | sed 's/^/"&/; s/$/&"/' > strings.dict
```

### 第3步：将字典传递给模糊测试器

使用适合您模糊测试器的适当标志（见上文的快速参考）。

## 常见模式

### 模式：协议关键词

**用例：** 模糊测试HTTP或自定义协议处理程序

**字典内容：**
```conf
# HTTP方法
"GET"
"POST"
"PUT"
"DELETE"
"HEAD"

# 头部
"Content-Type"
"Authorization"
"Host"

# 协议标记
"HTTP/1.1"
"HTTP/2.0"
```

### 模式：魔法字节和文件格式头

**用例：** 模糊测试图像解析器、媒体解码器、存档处理程序

**字典内容：**
```conf
# PNG魔法字节和块
png_magic="\x89PNG\r\n\x1a\n"
ihdr="IHDR"
plte="PLTE"
idat="IDAT"
iend="IEND"

# JPEG标记
jpeg_soi="\xFF\xD8"
jpeg_eoi="\xFF\xD9"
```

### 模式：配置文件关键词

**用例：** 模糊测试配置文件解析器（YAML、TOML、INI）

**字典内容：**
```conf
# 常见配置关键词
"true"
"false"
"null"
"version"
"enabled"
"disabled"

# 部分标题
"[general]"
"[network]"
"[security]"
```

## 高级用法

### 提示和技巧

| 提示 | 为什么有帮助 |
|-----|--------------|
| 组合多种生成方法 | LLM生成的关键词+二进制中的字符串覆盖广泛的表面 |
| 包含边界值 | `"0"`，`"-1"`，`"2147483647"`触发边缘情况 |
| 添加格式分隔符 | `:`, `=`, `{`, `}`帮助模糊测试器构建有效结构 |
| 保持字典专注 | 50-200条目比成千上万的条目表现更好 |
| 测试字典有效性 | 带有和不带字典运行，比较覆盖率 |

### 自动生成的字典（AFL++）

使用`afl-clang-lto`编译器时，AFL++会自动从二进制中的字符串比较中提取字典条目。这通过编译时的AUTODICTIONARY功能发生。

**启用自动字典：**
```bash
export AFL_LLVM_DICT2FILE=auto.dict
afl-clang-lto++ target.cc -o target
# 字典保存到auto.dict
afl-fuzz -x auto.dict -i in -o out -- ./target
```

### 组合多个字典

一些模糊测试器支持多个字典文件：

```bash
# AFL++使用多个字典
afl-fuzz -x keywords.dict -x formats.dict -i in -o out -- ./target
```

## 反模式

| 反模式 | 问题 | 正确方法 |
|-------|-------|------------------|
| 包含完整句子 | 模糊测试器需要原子标记，而不是散文 | 分解为单个关键词 |
| 重复条目 | 浪费变异预算 | 使用`sort -u`去重 |
| 字典过大 | 模糊测试器变慢，稀释有用标记 | 保持专注：50-200最相关的条目 |
| 缺少十六进制转义 | 非打印字节被破坏 | 使用`\xXX`表示二进制值 |
| 无注释 | 难以维护和审计 | 使用`#`注释文档部分 |

## 工具特定指南

### libFuzzer

```bash
clang++ -fsanitize=fuzzer,address harness.cc -o fuzz
./fuzz -dict=./dictionary.dict corpus/
```

**集成提示：**
- 字典标记在变异过程中插入/替换
- 结合`-max_len`控制输入大小
- 使用`-print_final_stats=1`查看字典有效性指标
- 字典条目长度超过`-max_len`将被忽略

### AFL++

```bash
afl-fuzz -x ./dictionary.dict -i input/ -o output/ -- ./target @@
```

**集成提示：**
- AFL++支持多个`-x`标志用于多个字典
- 使用`AFL_LLVM_DICT2FILE`与`afl-clang-lto`一起使用自动生成的字典
- 模糊测试器统计UI显示字典有效性
- 标记在确定性阶段和havoc阶段使用

### cargo-fuzz（Rust）

```bash
cargo fuzz run fuzz_target -- -dict=./dictionary.dict
```

**集成提示：**
- cargo-fuzz使用libFuzzer后端，因此所有libFuzzer dict标志都适用
- 将字典文件放在`fuzz/`目录中，与测试程序一起
- 从测试程序目录引用：`cargo fuzz run target -- -dict=../dictionary.dict`

### go-fuzz（Go）

go-fuzz没有内置字典支持，但您可以手动用字典条目种子语料库：

```bash
# 将字典转换为语料库文件
grep -o '"*"' dict.txt | while read line; do
    echo -n "$line" | base64 > corpus/$(echo "$line" | md5sum | cut -d' ' -f1)
done

go-fuzz -bin=./target-fuzz.zip -workdir=.
```

## 故障排除

| 问题 | 原因 | 解决方案 |
|-------|-------|----------|
| 字典文件未加载 | 路径错误或格式错误 | 检查模糊测试器输出中的dict解析错误；验证文件格式 |
| 没有覆盖率改进 | 字典标记不相关 | 分析目标代码中的实际关键词；尝试不同的生成方法 |
| 字典文件语法错误 | 未转义引号或无效转义 | 使用`\\`表示反斜杠，`\"`表示引号；用测试运行验证 |
| 模糊测试器忽略长条目 | 条目超过`-max_len` | 保持条目在最大输入长度以下，或增加`-max_len` |
| 字典太大导致模糊测试器变慢 | 字典太大 | 修剪到50-200最相关的条目 |

## 相关技能

### 使用此技术的工具

| 技能 | 如何应用 |
|-------|----------------|
| **libfuzzer** | 通过`-dict=`标志原生支持字典 |
| **aflpp** | 原生支持字典，通过`-x`标志；使用AUTODICTIONARIES自动生成 |
| **cargo-fuzz** | 使用libFuzzer后端，继承`-dict=`支持 |

### 相关技术

| 技能 | 关系 |
|-------|--------------|
| **fuzzing-corpus** | 字典与语料库互补：语料库提供结构，字典提供关键词 |
| **coverage-analysis** | 使用覆盖率数据验证字典有效性 |
| **harness-writing** | 捕获结构决定哪些字典标记有用 |

## 资源

### 关键外部资源

**[AFL++ 字典](https://github.com/AFLplusplus/AFLplusplus/tree/stable/dictionaries)**
预构建的常见格式字典（HTML、XML、JSON、SQL等）。是格式特定模糊测试的良好起点。

**[libFuzzer 字典文档](https://llvm.org/docs/LibFuzzer.html#dictionaries)**
官方libFuzzer文档，解释字典格式和用法。说明标记插入策略和性能影响。

### 其他示例

**[OSS-Fuzz 字典](https://github.com/google/oss-fuzz/tree/master/projects)**
Google持续模糊测试服务中的实际字典。搜索项目目录中的`*.dict`文件，查看生产示例。
