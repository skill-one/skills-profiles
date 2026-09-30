---
name: constant-time-analysis
description: 检测加密代码中的时序侧信道漏洞。在实现或审查加密代码、遇到涉及密钥的除法、密钥相关的分支或 C、C++、Go、Rust、Swift、Java、Kotlin、C#、PHP、JavaScript、TypeScript、Python 或 Ruby 中的常时编程问题时使用。
---

# 常量时间分析

编译代码，检查生成的汇编或字节码中的变量时间指令，然后确定哪些被标记的操作实际上接触了秘密。编译步骤是机械的；分诊步骤是工作。

## 何时使用

- 实现或审查签名、加密、KEM 或密钥派生例程
- 代码将 `/` 或 `%` 应用于从密钥、明文、nonce 或令牌派生的值
- 用户提到“常量时间”、“时间攻击”、“侧信道”或“KyberSlash”
- 审查名为 `sign`、`verify`、`encrypt`、`decrypt`、`derive_key` 的函数

## 何时不使用

- **测量**运行二进制文件的时序差异 — 使用 `constant-time-testing` 技能，该技能来自 `testing-handbook-skills` 插件，它涵盖 dudect 和统计方法，可能未安装。此技能静态检查编译器输出，并且永远不会执行要测试的代码。
- 非加密代码，或每个输入都是公开的加密代码
- 高级 API 使用，其中经过审核的库拥有常量时间保证
- 缓存和其他微架构侧信道 — 汇编视图看不到它们

## 语言路由

在解释任何发现之前，先阅读目标语言的指南；每个指南都列出了该语言的危险指令和常量时间的典型替换方法。

| 指南 | 语言 |
| ---- | ---- |
| [references/compiled.md](references/compiled.md) | C、C++、Go、Rust |
| [references/swift.md](references/swift.md) | Swift |
| [references/vm-compiled.md](references/vm-compiled.md) | Java、C# |
| [references/kotlin.md](references/kotlin.md) | Kotlin |
| [references/php.md](references/php.md) | PHP |
| [references/javascript.md](references/javascript.md) | JavaScript、TypeScript |
| [references/python.md](references/python.md) | Python |
| [references/ruby.md](references/ruby.md) | Ruby |

## 运行分析器

分析器接受一个文件并从其扩展名检测语言。**始终传递 `--warnings`：**

```bash
uv run {baseDir}/ct_analyzer/analyzer.py --warnings <source_file>
```

没有它，分析器只报告错误严重性的发现，这意味着除法、模除和弱 RNG。四个检测家族是警告严重性并保持沉默：依赖于秘密的分支、早期退出比较（`memcmp`、`strcmp`、`.equals`、`==`）、由秘密索引的表查找和变量时间编码。认证标签的早期退出比较是真实代码中最常见的时序错误 — Lucky Thirteen 正是如此 — 因此默认运行对您最可能发现的发现保持沉默。

| 标记 | 效果 |
| ---- | ---- |
| `--warnings` | 添加上述四个警告严重性家族。每次传递它 |
| `--func <regex>` | 将输出限制为匹配正则表达式的函数名 |
| `--json` | 机器可读输出 |
| `--github` | GitHub Actions 注释 |
| `--arch <target>` | 目标架构（`x86_64`、`arm64`、`riscv64`、...） — 仅限原生语言 |
| `--opt-level <level>` | 优化级别（`O0` 通过 `O3`、`Os`、`Oz`） — 仅限原生语言 |
| `--compiler <name>` | 覆盖编译器选择（`gcc`、`clang`、`go`、`rustc`、`swiftc`） |

使用正则表达式将大文件缩小到处理秘密的例程，例如 `--func 'sign|verify'`。

**原生编译代码（C、C++、Go、Rust、Swift）在多个 `--arch` 和 `--opt-level` 下运行。** 除法时序和分支降低取决于架构和优化：x86_64 `IDIV` 和 arm64 `SDIV` 不同，并且 `-O2` 的 `cmov` 在 `-O0` 时可能变成分支。单个干净的运行证明一种配置是安全的，而不是代码。

**`--arch` 如何跨平台取决于工具链。** clang 使用 `--target` 跨平台，不需要第二个编译器，但任何包含 libc 头文件的源也需要该目标的 C 库头文件 — `libc6-dev-riscv64-cross` 和朋友 — 或者它将失败，因为 `bits/libc-header-start.h` 文件未找到。Go 通过 `GOARCH` 跨平台构建，尽管 `go tool objdump` 没有 riscv64 反汇编器。GNU 跨工具链是一个 *单独的二进制文件*，因此 gcc 需要它明确命名 — `--compiler x86_64-linux-gnu-gcc`、`--compiler riscv64-linux-gnu-gcc` — 并且不会为您替换任何内容，因此报告始终命名运行的二进制文件。rustc 需要目标的标准库（`rustup target add`），Swift 在 Linux 目标上只针对主机。与构建您的产品的工具链进行比较，而不是哪个发行版打包的跨构建。

**在修复后重新运行整个扫描，跨编译器、目标以及包括 `Os` 和 `Oz` 的每个级别。** 任何通过向编译器传递常量除数来降低强度的修复都是仅在编译器选择合作的地方起作用的修复，而该选择的变化比看起来更大。将 `key_coef / (2 * gamma2)` 替换为 `#define`d 除数仍然会发出实际的除法：

| 工具链 | 发出除法的级别 |
| ---- | -------------- |
| gcc riscv64 | `O0` 通过 `Oz` — 每个级别 |
| gcc arm64、gcc x86_64 | `Os`、`Oz` |
| clang arm64 | `O0`、`Oz` |

强度降低是优化器的恩惠，而不是语言保证。优先使用显式乘法移位，并验证它相对于完整输入范围的原始表达式，而不是采样值 — 一个 2 的幂次的倒数匹配数百万个输入，然后才会发散。

Java、Kotlin 和 C# 编译成 JVM/CIL 字节码。分析器读取该字节码，因此 `--arch` 和 `--opt-level` 不适用，JIT 可能仍然会引入分析器看不到的变量时间原生代码。

### 每种语言的覆盖限制

覆盖不均匀，差距会改变干净报告的含义：

| 语言 | 报告不涵盖的内容 |
| ---- | ---------------- |
| Go | 仅分析文件中的符号。`go build` 链接运行时，其除法 — 所有在公开数据上 — 否则将主导发现 |
| JavaScript、TypeScript | 字节码发现仅限于文件按名称声明的函数，因为 V8 倾倒 node 的内部与倾倒您的方式相同。匿名回调落入源扫描。对于 TypeScript，字节码发现命名函数但携带无行号，因为 V8 的位置索引转换后的输出 |
| Python、Ruby、PHP | 字节码反映运行的解释器，而不是 JIT 或替代运行时 |
| Rust | 除非文件声明 `fn main`，否则作为库分析；没有调用者的私有函数可能在分析之前被优化掉 |
| Swift | 在 Linux 上针对主机平台；iOS 和 macOS 三重需要 Apple 工具链 |

由于发现和沉默都取决于配置，报告结果时请说明产生了该结果的编译器、架构和优化级别。

要扫描目录，请在 shell 中循环 — 分析器是一个确定性脚本，每个文件一次调用：

```bash
for f in src/crypto/*.c; do uv run {baseDir}/ct_analyzer/analyzer.py --warnings --json "$f"; done
```

### 前置条件

| 语言 | 要求 |
| ---- | ---- |
| C、C++、Go、Rust | `gcc`/`clang`、`go`、`rustc` 在 PATH 中 |
| Swift | Xcode 或 Swift 工具链（`swiftc`） |
| Java / Kotlin | JDK（`javac`、`javap`）；Kotlin 还需要 `kotlinc` |
| C# | .NET SDK 加上 `ilspycmd`（`dotnet tool install -g ilspycmd`） |
| PHP | 带有 VLD 扩展的 PHP 或 OPcache |
| JavaScript / TypeScript | Node.js |
| Python | Python 3.x |
| Ruby | 支持 `--dump=insns` 的 Ruby |

在“工具链未找到”错误的情况下，请参阅 [references/vm-compiled.md](references/vm-compiled.md) 以获取 JVM 和 .NET 安装、macOS keg-only PATH 配置和故障排除。

## 解释结果

**PASSED** — 对于您运行的配置，没有 *错误* 严重性的发现。警告不会影响它，因此 `Result: PASSED` 旁边有 `Warnings: 6` 是正常的，并且不是干净的结果。在得出任何结论之前，请阅读警告列表。

**FAILED** — 发现了危险指令，按函数报告：

```text
[ERROR] SDIV
  函数：decompose_vulnerable
  原因：SDIV 有早期终止优化；执行时间取决于操作数值
```

## 分诊发现

**分析器没有数据流分析。它标记每个危险指令，无论秘密是否到达它，因此 FAILED 报告是一个工作列表，而不是一个裁决。** 将原始输出报告为一组漏洞是此技能的主要失败模式。

对于每个标记的指令，阅读源并回答一个问题：**操作数是否依赖于秘密数据？** 从指令的函数跟踪回调用者的输入，然后分类：

```c
// FALSE POSITIVE: 操作数是一个缓冲区长度，已经从密文大小公开
int num_blocks = data_len / 16;

// TRUE POSITIVE: 被除数是一个私钥系数；IDIV/SDIV 泄露其大小
int32_t q = secret_coef / GAMMA2;
```

| 问题 | 如果是 |
| ---- | ---- |
| 操作数是编译时常量？ | 可能是误报 |
| 操作数是公开参数 — 长度、计数、索引边界？ | 可能是误报 |
| 操作数是从密钥、明文、nonce 或令牌派生的？ | **真阳性** |
| 攻击者能否影响操作数的值？ | **真阳性** |

为每个标记的项目声明裁决并证明其数据流。无法追溯到秘密的发现不是发现；明确说明这一点，而不是沉默地忽略它。

`{baseDir}/ct_analyzer/tests/triage_samples/` 包含每个语言的已知答案案例：每个固定都配对一个真阳性和一个分析器报告相同的误报，并且 `expectations.json` 记录了哪个是哪个以及原因。`triage_c.c` 是最短的示例 — 分析器标记了 `ct_high_bits` 和 `ct_block_count` 中的除法，正确的分诊确认第一个并清除第二个。

**弱 RNG 和编码发现问一个不同的问题。** 对于 `Math.random`、`mt_rand`、`random.randint`、`System.Random` 和 `base64_encode`，没有操作数是秘密的，因此“操作数是否依赖于秘密？”无法解决它们。相反，询问结果用于什么：用 nonce 或密钥播种是一个真阳性，抖动重试延迟不是。这些是通过源的正则表达式扫描报告的，而不是从字节码，因此它们归因于 `<source>` 并带有行号，而不是包含函数 — 除非在 PHP 中，其中它们携带函数。

**比较和查找发现有自己的问题，也有自己的修复方法。** 对于早期退出比较，询问哪一方是秘密的：比较认证标签、MAC 或密码哈希是一个真阳性，比较公开的协议头不是。对于表查找，询问 *索引* 是否是秘密的 — 数组的內容无关紧要，只有选择元素的是什么。两者都可以按原样利用，因此确认的一个需要语言的常量时间原语，而不是循环的重写：

| 语言 | 常量时间比较 |
| ---- | ------------ |
| C、C++ | `CRYPTO_memcmp`（OpenSSL）或 `sodium_memcmp` |
| Go | `crypto/subtle.ConstantTimeCompare` |
| Rust | `subtle` 库的 `ConstantTimeEq` |
| Java、Kotlin | `MessageDigest.isEqual` |
| C# | `CryptographicOperations.FixedTimeEquals` |
| PHP | `hash_equals` |
| Python | `hmac.compare_digest` |
| Ruby | `OpenSSL.secure_compare` |
| JavaScript、TypeScript | `crypto.timingSafeEqual` |

一个秘密索引查找没有即插即用的替代方案：它需要一个位切片或算术公式来接触每个元素，这就是为什么 AES S-box 表是经典案例。通过表编码秘密 — `base64_encode`、`bin2hex`、`chr`/`ord` — 是库中的相同问题，并且 `paragonie/constant_time_encoding` 是 PHP 的参考修复。

## 限制

1. **仅静态** — 读取汇编和字节码，永远不会运行时行为。缓存时序和其他微架构信道是不可见的。
2. **没有数据流分析** — 见分诊上述。
3. **配置特定** — 不同的编译器、优化级别、架构或运行时版本可以从相同的源发出不同的指令。

## 真实世界影响

- **KyberSlash (2023)** — ML-KEM 实现中的除法指令允许密钥恢复
- **Lucky Thirteen (2013)** — CBC 填充验证中的时序差异启用了明文恢复
- **RSA 时序攻击** — 早期实现通过除法时序泄露了私钥位

## 参考文献

- [Cryptocoding Guidelines](https://github.com/veorq/cryptocoding) — 加密的防御性编码
- [KyberSlash](https://kyberslash.cr.yp.to/) — 量子后加密中的除法时序
- [BearSSL Constant-Time](https://www.bearssl.org/constanttime.html) — 实用的常量时间技术
