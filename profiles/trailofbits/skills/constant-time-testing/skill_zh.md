# 恒时测试

时序攻击利用执行时间的变化来从密码实现中提取秘密信息。与针对理论弱点的密码分析不同，时序攻击利用实现缺陷——它们可能影响任何密码代码。

## 背景

时序攻击由 Kocher 于 1996 年引入。自那时起，研究人员已经展示了针对 RSA ([Schindler](https://link.springer.com/content/pdf/10.1007/3-540-44499-8_8.pdf))、OpenSSL ([Brumley and Boneh](https://crypto.stanford.edu/~dabo/papers/ssl-timing.pdf))、AES 实现甚至后量子算法如 [Kyber](https://eprint.iacr.org/2024/1049.pdf) 的实际攻击。

### 关键概念

| 概念 | 描述 |
|------|------|
| 恒时 | 代码路径和内存访问与秘密数据无关 |
| 时序泄露 | 与秘密数据相关的可观察的执行时间差异 |
| 侧信道 | 从实现中而不是算法中提取的信息 |
| 微架构 | CPU 级别的时序差异（缓存、除法、移位） |

### 这为什么重要

时序漏洞可能导致：
- **暴露私钥** - 提取 RSA/ECDH 中的秘密指数
- **启用远程攻击** - 网络可观察的时序差异
- **绕过密码学安全性** - 削弱理论保证
- **无声地持续存在** - 在没有专门分析的情况下通常无法检测

两个先决条件使利用成为可能：
1. **访问预言机** - 对易受攻击的实现进行足够的查询
2. **时序依赖性** - 执行时间与秘密数据之间的相关性

### 常见的恒时违规模式

四种模式解释了大多数时序漏洞：

```c
// 1. 条件跳转 - 最严重的时序差异
if(secret == 1) { ... }
while(secret > 0) { ... }

// 2. 数组访问 - 缓存时序攻击
lookup_table[secret];

// 3. 整数除法（取决于处理器）
data = secret / m;

// 4. 移位操作（取决于处理器）
data = a << secret;
```

**条件跳转**导致不同的代码路径，从而导致巨大的时序差异。

**数组访问**依赖于秘密数据，可以启用缓存时序攻击，如 [AES 缓存时序研究](https://cr.yp.to/antiforgery/cachetiming-20050414.pdf) 中所示。

**整数除法和移位操作**在某些 CPU 架构和编译器配置下泄露秘密。

当无法避免模式时，采用 [掩码技术](https://link.springer.com/chapter/10.1007/978-3-642-38348-9_9) 来消除时序与秘密之间的相关性。

### 示例：模幂运算时序攻击

模幂运算（用于 RSA 和 Diffie-Hellman）容易受到时序攻击。RSA 解密计算：

$$ct^{d} \mod{N}$$

其中 $d$ 是秘密指数。*指数平方乘法*优化将乘法减少到 $\log{d}$：

$$
\begin{align*}
& \textbf{输入: } \text{基数 }y,\text{指数 } d=\{d_n,\cdots,d_0\}_2,\text{模数 } N \\
& r = 1 \\
& \textbf{for } i=|n| \text{ downto } 0: \\
& \quad\textbf{if } d_i == 1: \\
& \quad\quad r = r * y \mod{N} \\
& \quad y = y * y \mod{N} \\
& \textbf{return }r
\end{align*}
$$

代码在指数位 $d_i$ 上分支，违反了恒时原则。当 $d_i = 1$ 时，发生额外的乘法，增加执行时间并泄露比特信息。

Montgomery 乘法（通常用于模运算）也泄露时序：当中间值超过模数 $N$ 时，需要额外的约减步骤。攻击者构造输入 $y$ 和 $y'$ 使得：

$$
\begin{align*}
y^2 < y^3 < N \\
y'^2 < N \leq y'^3
\end{align*}
$$

对于 $y$，两个乘法都花费时间 $t_1+t_1$。对于 $y'$，第二个乘法需要约减，花费时间 $t_1+t_2$。这种时序差异揭示了 $d_i$ 是否为 0 或 1。

## 何时使用

**应用恒时分析时：**
- 审计密码实现（原语、协议）
- 代码处理秘密密钥、密码或敏感密码学材料
- 从头开始实现密码算法
- 审查触及密码代码的 PR
- 调查潜在的时序漏洞

**考虑替代方案时：**
- 代码不处理秘密数据
- 没有秘密输入的公共算法
- 非密码学时序要求（性能优化）

## 快速参考

| 场景 | 推荐方法 | 技能 |
|------|----------|------|
| 证明没有泄露 | 形式验证 | SideTrail, ct-verif, FaCT |
| 检测统计时序差异 | 统计测试 | **dudect** |
| 追踪运行时秘密数据流 | 动态分析 | **timecop** |
| 查找缓存时序漏洞 | 符号执行 | Binsec, pitchfork |

## 恒时工具类别

密码学社区已经开发了四类时序分析工具：

| 类别 | 方法 | 优点 | 缺点 |
|------|------|------|------|
| **形式** | 对模型进行数学证明 | 保证没有泄露 | 复杂性、建模假设 |
| **符号** | 符号执行路径 | 具体反例 | 路径探索耗时 |
| **动态** | 带标记秘密的运行时跟踪 | 精细、灵活 | 执行路径覆盖有限 |
| **统计** | 测量实际执行时序 | 实用、简单设置 | 无根本原因、噪声敏感性 |

### 1. 形式工具

形式验证在代码的抽象（模型）上数学证明时序属性。工具从源代码/二进制创建模型并验证其满足指定属性（例如，标记为秘密的变量）。

**流行工具：**
- [SideTrail](https://github.com/aws/s2n-tls/tree/main/tests/sidetrail)
- [ct-verif](https://github.com/imdea-software/verifying-constant-time)
- [FaCT](https://github.com/plsyssec/fact)

**优点：** 缺失证明、语言无关（LLVM 字节码）
**缺点：** 需要专业知识、建模假设可能遗漏现实问题

### 2. 符号工具

符号分析分析路径和内存访问如何依赖于符号变量（秘密）。提供具体反例。专注于缓存时序攻击。

**流行工具：**
- [Binsec](https://github.com/binsec/binsec)
- [pitchfork](https://github.com/PLSysSec/haybale-pitchfork)

**优点：** 具体反例有助于调试
**缺点：** 路径爆炸导致执行时间过长

### 3. 动态工具

动态分析标记敏感内存区域并跟踪执行以检测时序依赖操作。

**流行工具：**
- [Memsan](https://clang.llvm.org/docs/MemorySanitizer.html): [教程](https://crocs-muni.github.io/ct-tools/tutorials/memsan)
- **Timecop**（见下文）

**优点：** 精细控制、目标分析
**缺点：** 覆盖范围仅限于执行路径

> **详细指导：** 见 **timecop** 技能的设置和使用。

### 4. 统计工具

使用各种输入执行代码，测量经过时间，并检测不一致性。测试实际实现，包括编译器优化和架构。

**流行工具：**
- **dudect**（见下文）
- [tlsfuzzer](https://github.com/tlsfuzzer/tlsfuzzer)

**优点：** 简单设置、实用现实结果
**缺点：** 无根本原因信息、噪声掩盖弱信号

> **详细指导：** 见 **dudect** 技能的设置和使用。

## 测试工作流

```
阶段 1：静态分析        阶段 2：统计测试
┌─────────────────┐            ┌─────────────────┐
│ 识别秘密数据流 │      →     │ 检测时序差异     │
│ 工具：ct-verif  │            │ 工具：dudect    │
└─────────────────┘            └─────────────────┘
         ↓                              ↓
阶段 4：根本原因             阶段 3：动态跟踪
┌─────────────────┐            ┌─────────────────┐
│ 定位泄露位置   │      ←     │ 跟踪秘密传播     │
│ 工具：Timecop   │            │ 工具：Timecop   │
└─────────────────┘            └─────────────────┘
```

**推荐方法：**
1. **从 dudect 开始** - 快速统计检查时序差异
2. **如果发现泄露** - 使用 Timecop 定位根本原因
3. **为高保证** - 应用形式验证（ct-verif, SideTrail）
4. **持续监控** - 将 dudect 集成到 CI 管道

## 工具和方法

### Dudect - 统计分析

[Dudect](https://github.com/oreparaz/dudect/) 测量两个输入类别（固定与随机）的执行时间，并使用 Welch's t-test 检测统计上显著差异。

> **详细指导：** 见 **dudect** 技能的完整设置、使用模式和 CI 集成。

#### 快速开始用于恒时分析

```c
#define DUDECT_IMPLEMENTATION
#include "dudect.h"

uint8_t do_one_computation(uint8_t *data) {
    // 要测量的代码放在这里
}

void prepare_inputs(dudect_config_t *c, uint8_t *input_data, uint8_t *classes) {
    for (size_t i = 0; i < c->number_measurements; i++) {
        classes[i] = randombit();
        uint8_t *input = input_data + (size_t)i * c->chunk_size;
        if (classes[i] == 0) {
            // 固定输入类别
        } else {
            // 随机输入类别
        }
    }
}
```

**主要优点：**
- 简单的 C 头文件仅集成
- 通过 Welch's t-test 的统计严谨性
- 可用于编译后的二进制文件（现实条件）

**主要限制：**
- 检测到泄露时无根本原因信息
- 对测量噪声敏感
- 不能保证不存在泄露（仅统计置信度）

### Timecop - 动态跟踪

[Timecop](https://post-apocalyptic-crypto.org/timecop/) 包装 Valgrind 以检测依赖于秘密内存区域的运行时操作。

> **详细指导：** 见 **timecop** 技能的安装、示例和调试。

#### 快速开始用于恒时分析

```c
#include "valgrind/memcheck.h"

#define poison(addr, len) VALGRINDMAKE_MEM_UNDEFINED(addr, len)
#define unpoison(addr, len) VALGRINDMAKE_MEM_DEFINED(addr, len)

int main() {
    unsigned long long secret_key = 0x12345678;

    // 将 secret 标记为有毒
    poison(&secret_key, sizeof(secret_key));

    // 任何依赖于 secret_key 的分支或内存访问
    // 都会由 Valgrind 报告
    crypto_operation(secret_key);

    unpoison(&secret_key, sizeof(secret_key));
}
```

使用 Valgrind 运行：
```bash
valgrind --leak-check=full --track-origins=yes ./binary
```

**主要优点：**
- 指定泄露的确切行
- 无需代码插桩
- 跟踪秘密通过执行的传播

**主要限制：**
- 无法检测微架构时序差异
- 覆盖范围仅限于执行路径
- 性能开销（在合成 CPU 上运行）

## 实现指南

### 阶段 1：初始评估

**识别处理秘密的密码代码：**
- 私钥、指数、nonce
- 密码哈希、认证令牌
- 加密/解密操作

**快速统计检查：**
1. 为密码函数编写 dudect 装置
2. 运行 5-10 分钟，使用 `timeout 600 ./ct_test`
3. 监控 t 值：高绝对值指示泄露

**工具：** dudect
**预期时间：** 1-2 小时（装置编写 + 初始运行）

### 阶段 2：详细分析

如果 dudect 检测到泄露：

**根本原因调查：**
1. 使用 Timecop `poison()` 标记秘密变量
2. 在 Valgrind 下运行以识别确切行
3. 审查四个常见违规模式
4. 检查汇编输出以查找条件分支

**工具：** Timecop, 编译器输出 (`objdump -d`)

### 阶段 3：修复

**修复时序泄露：**
- 用恒时选择替换条件分支（位操作）
- 使用恒时比较函数
- 替换数组查找为恒时替代方案或掩码
- 验证编译器不会优化掉恒时代码

**重新验证：**
1. 运行 dudect 再次进行长时间（30+ 分钟）
2. 在不同编译器和优化级别上测试
3. 在不同 CPU 架构上测试

### 阶段 4：持续监控

**集成到 CI：**
- 将 dudect 测试添加到测试套件
- 在 CI 中运行固定持续时间（5-10 分钟）
- 如果检测到泄露则失败构建

见 **dudect** 技能的 CI 集成示例。

## 常见漏洞

| 漏洞 | 描述 | 检测 | 严重性 |
|------|------|------|------|
| 秘密依赖分支 | `if (secret_bit) { ... }` | dudect, Timecop | 危急 |
| 秘密依赖数组访问 | `table[secret_index]` | Timecop, Binsec | 高 |
| 变量时序除法 | `result = x / secret` | Timecop | 中 |
| 变量时序移位 | `result = x << secret` | Timecop | 中 |
| Montgomery 约减泄露 | 中间值 > N 时发生额外约减 | dudect | 高 |

### 秘密依赖分支：深入分析

**漏洞：**
执行时间因分支是否被跳转而不同。常见于优化的模幂运算。

**如何使用 dudect 检测：**
```c
uint8_t do_one_computation(uint8_t *data) {
    uint64_t base = ((uint64_t*)data)[0];
    uint64_t exponent = ((uint64_t*)data)[1]; // 秘密!
    return mod_exp(base, exponent, MODULUS);
}

void prepare_inputs(dudect_config_t *c, uint8_t *input_data, uint8_t *classes) {
    for (size_t i = 0; i < c->number_measurements; i++) {
        classes[i] = randombit();
        uint64_t *input = (uint64_t*)(input_data + i * c->chunk_size);
        input[0] = rand(); // 随机基数
        input[1] = (classes[i] == 0) ? FIXED_EXPONENT : rand(); // 固定与随机
    }
}
```

**如何使用 Timecop 检测：**
```c
poison(&exponent, sizeof(exponent));
result = mod_exp(base, exponent, modulus);
unpoison(&exponent, sizeof(exponent));
```

Valgrind 将报告：
```
条件跳转或移动依赖于未初始化的值(s)
  at 0x40115D: mod_exp (example.c:14)
```

**相关技能：** **dudect**, **timecop**

## 案例研究

### 案例研究：OpenSSL RSA 时序攻击

Brumley 和 Boneh（2005 年）从 OpenSSL 中提取了 RSA 私钥。漏洞利用了 Montgomery 乘法的变量时序约减步骤。

**攻击向量：** 模幂运算的时序差异
**检测方法：** 统计分析（dudect 的前身）
**影响：** 远程密钥提取

**使用的工具：** 自定义时序测量
**应用的技术：** 统计分析、选择密文查询

### 案例研究：KyberSlash

后量子算法 Kyber 的参考实现中包含多项式操作的时序漏洞。除法操作泄露了秘密系数。

**攻击向量：** 秘密依赖除法时序
**检测方法：** 动态分析和统计测试
**影响：** 后量子密码学中的密钥恢复

**使用的工具：** 时序测量工具
**应用的技术：** 差分时序分析

## 高级用法

### 提示和技巧

| 提示 | 为什么有帮助 |
|------|------------|
| 将 dudect 绑定到隔离的 CPU 核心 (`taskset -c 2`) | 减少 OS 噪声，提高信号检测 |
| 测试多个编译器 (gcc, clang, MSVC) | 优化可能引入或消除泄露 |
| 运行长时间 dudect（数小时） | 增加统计置信度 |
| 在装置中尽量减少非密码代码 | 减少掩盖弱信号的噪声 |
| 检查汇编输出 (`objdump -d`) | 验证编译器没有引入分支 |
| 使用 `-O3 -march=native` 进行测试 | 匹配生产优化级别 |

### 常见错误

| 错误 | 为什么不正确 | 正确方法 |
|------|----------------|----------|
| 仅测试一种输入分布 | 可能遗漏其他模式可见的泄露 | 测试固定与随机、固定与固定不同等 |
| dudect 运行时间短（< 1 分钟） | 对于弱信号不够充分的测量 | 运行 5-10+ 分钟，高保证需要更长时间 |
| 忽略编译器优化级别 | `-O0` 可能隐藏 `-O3` 中存在的泄露 | 在生产优化级别测试 |
| 不在目标架构上测试 | x86 与 ARM 有不同的时序特性 | 在部署平台测试 |
| 在 Timecop 中标记太多为秘密 | 假阳性，结果不清晰 | 仅标记真正的秘密（密钥，而不是公共数据） |

## 相关技能

### 工具技能

| 技能 | 在恒时分析中的主要用途 |
|------|--------------------------|
| **dudect** | 通过 Welch's t-test 统计检测时序差异 |
| **timecop** | 动态跟踪以定位时序泄露的确切位置 |

### 技术技能

| 技能 | 何时应用 |
|------|----------|
| **coverage-analysis** | 确保测试输入执行密码函数中的所有代码路径 |
| **ci-integration** | 在持续集成管道中自动执行恒时测试 |

### 相关领域技能

| 技能 | 关系 |
|------|------|
| **crypto-testing** | 恒时分析是密码学测试的关键组成部分 |
| **fuzzing** | 模糊测试密码代码可能触发时序依赖路径 |

## 技能依赖图

```
                    ┌─────────────────────────┐
                    │  constant-time-analysis │
                    │     (this skill)        │
                    └───────────┬─────────────┘
                                │
                ┌───────────────┴───────────────┐
                │                               │
                ▼                               ▼
    ┌───────────────────┐           ┌───────────────────┐
    │      dudect       │           │     timecop       │
    │  (statistical)    │           │    (dynamic)      │
    └────────┬──────────┘           └────────┬──────────┘
             │                               │
             └───────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │   Supporting Techniques      │
              │ coverage, CI integration     │
              └──────────────────────────────┘
```

## 资源

### 关键外部资源

**[这些结果必须是假的：恒时分析工具的可用性评估](https://www.usenix.org/system/files/sec24fall-prepub-760-fourne.pdf)**
综合可用性研究恒时分析工具。关键发现：开发人员难以处理假阳性，需要更好的错误消息，并从工具集成中受益。评估 FaCT、ct-verif、dudect 和 Memsan 跨多个密码实现。建议改进工具 UX 和更好文档。

**[恒时工具列表 - CROCS](https://crocs-muni.github.io/ct-tools/)**
精选的恒时分析工具目录，附带教程。涵盖形式工具（ct-verif、FaCT）、动态工具（Memsan、Timecop）、符号工具（Binsec）、统计工具（dudect）。包括实用教程，用于设置和使用。

**[Paul Kocher：对 Diffie-Hellman、RSA、DSS 和其他系统的时序攻击](https://paulkocher.com/doc/TimingAttacks.pdf)**
1996 年引入时序攻击的原始论文。展示了 RSA 中模幂运算的实际攻击。了解时序漏洞的必要历史背景。

**[远程时序攻击是实用的 (Brumley & Boneh)](https://crypto.stanford.edu/~dabo/papers/ssl-timing.pdf)**
展示了针对 OpenSSL 的实际远程时序攻击。显示了网络可观察的时序差异足以提取 RSA 密钥。证明时序攻击在现实网络条件下有效。

**[AES 缓存时序攻击](https://cr.yp.to/antiforgery/cachetiming-20050414.pdf)**
显示使用查找表的 AES 实现容易受到缓存时序攻击。展示了实际攻击提取 AES 密钥通过缓存侧信道。

**[KyberSlash：除法时序泄露秘密](https://eprint.iacr.org/2024/1049.pdf)**
最近发现 Kyber（NIST 后量子标准）中时序漏洞。显示了除法操作泄露秘密系数。强调即使现代后量子密码学中，时序问题仍然存在。

### 视频资源

- [Trail of Bits：恒时编程](https://www.youtube.com/watch?v=vW6wqTzfz5g) - 恒时编程原则和工具概述
