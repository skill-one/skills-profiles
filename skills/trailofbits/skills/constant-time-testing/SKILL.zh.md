---
name: constant-time-testing
description: 通过运行程序、使用dudect进行统计分析以及利用Valgrind上的Timecop进行动态跟踪，来测量加密实现中的时序侧信道。涵盖形式化、符号化、动态和统计工具类别，以及如何解读结果。在测试运行中的实现是否为常数时间、测量编译二进制文件的时序差异，或调查疑似时序攻击时使用。不用于静态检查编译器输出——常数时间分析插件负责该功能。
---

# 恒时测试

时序攻击利用执行时间的变化来从密码学实现中提取秘密信息。与针对理论弱点的密码分析不同，时序攻击利用实现缺陷——它们可能影响任何密码学代码。

## 背景

时序攻击由 Kocher 于 1996 年提出。自那时起，研究人员已经展示了针对 RSA ([Schindler](https://link.springer.com/content/pdf/10.1007/3-540-44499-8_8.pdf))、OpenSSL ([Brumley 和 Boneh](https://crypto.stanford.edu/~dabo/papers/ssl-timing.pdf))、AES 实现甚至后量子算法（如 [Kyber](https://eprint.iacr.org/2024/1049.pdf)）的实际攻击。

### 关键概念

| 概念 | 描述 |
|------|------|
| 恒时 | 代码路径和内存访问与秘密数据无关 |
| 时序泄露 | 与秘密数据相关的可观察的执行时间差异 |
| 侧信道 | 从实现中提取信息而不是算法 |
| 微架构 | CPU 级别的时序差异（缓存、除法、移位） |

### 这为什么重要

时序漏洞可能导致：
- **暴露私钥** - 提取 RSA/ECDH 中的秘密指数
- **启用远程攻击** - 网络可观察的时序差异
- **绕过密码学安全** - 削弱理论保证
- **无声地持续存在** - 在没有专门分析的情况下通常无法检测

利用的两个前提条件是：
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

**数组访问**依赖于秘密，使缓存时序攻击成为可能，如 [AES 缓存时序研究](https://cr.yp.to/antiforgery/cachetiming-20050414.pdf) 所示。

**整数除法和移位操作**在某些 CPU 架构和编译器配置下泄露秘密。

当无法避免这些模式时，采用 [掩码技术](https://link.springer.com/chapter/10.1007/978-3-642-38348-9_9) 来消除时序和秘密之间的相关性。

### 示例：模幂运算时序攻击

模幂运算（用于 RSA 和 Diffie-Hellman）容易受到时序攻击。RSA 解密计算：

$$ct^{d} \mod{N}$$

其中 $d$ 是秘密指数。*指数平方法*优化将乘法减少到 $\log{d}$：

$$
\begin{align*}
& \textbf{输入: } \text{底数 }y,\text{指数 } d=\{d_n,\cdots,d_0\}_2,\text{模数 } N \\
& r = 1 \\
& \textbf{for } i=|n| \text{ downto } 0: \\
& \quad\textbf{if } d_i == 1: \\
& \quad\quad r = r * y \mod{N} \\
& \quad y = y * y \mod{N} \\
& \textbf{return }r
\end{align*}
$$

代码在指数位 $d_i$ 上分支，违反了恒时原则。当 $d_i = 1$ 时，发生额外的乘法，增加执行时间并泄露位信息。

Montgomery 乘法（通常用于模运算）也泄露时序：当中间值超过模数 $N$ 时，需要额外的约减步骤。攻击者构造输入 $y$ 和 $y'$ 使得：

$$
\begin{align*}
y^2 < y^3 < N \\
y'^2 < N \leq y'^3
\end{align*}
$$

对于 $y$，两个乘法都花费时间 $t_1+t_1$。对于 $y'$，第二个乘法需要约减，花费时间 $t_1+t_2$。这种时序差异揭示了 $d_i$ 是否为 0 或 1。

## 何时使用

**在以下情况下应用恒时分析：**
- 审计密码学实现（原语、协议）
- 代码处理秘密密钥、密码或敏感密码学材料
- 从头开始实现密码学算法
- 审查触及密码学代码的 PR
- 调查潜在的时序漏洞

**在以下情况下考虑替代方案：**
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

密码学社区已经开发了四种时序分析工具类别：

| 类别 | 方法 | 优点 | 缺点 |
|------|------|------|------|
| **形式** | 对模型进行数学证明 | 保证没有泄露 | 复杂性、建模假设 |
| **符号** | 符号执行路径 | 具体反例 | 路径探索耗时 |
| **动态** | 带标记秘密的运行时跟踪 | 粒度化、灵活 | 执行路径覆盖有限 |
| **统计** | 测量实际执行时序 | 实用、简单设置 | 无根本原因、噪声敏感性 |

### 1. 形式工具

形式验证在代码的抽象（模型）上数学证明时序属性。工具从源代码/二进制文件创建模型并验证它是否满足指定属性（例如，标记为秘密的变量）。

**流行工具：**
- [SideTrail](https://github.com/aws/s2n-tls/tree/main/tests/sidetrail)
- [ct-verif](https://github.com/imdea-software/verifying-constant-time)
- [FaCT](https://github.com/plsyssec/fact)

**优点：** 缺失证明、语言无关（LLVM 字节码）
**缺点：** 需要专业知识、建模假设可能遗漏现实问题

### 2. 符号工具

符号分析分析路径和内存访问如何依赖于符号变量（秘密）。提供具体反例。侧重于缓存时序攻击。

**流行工具：**
- [Binsec](https://github.com/binsec/binsec)
- [pitchfork](https://github.com/PLSysSec/haybale-pitchfork)

**优点：** 具体反例有助于调试
**缺点：** 路径爆炸导致执行时间过长

### 3. 动态工具

动态分析标记敏感内存区域并跟踪执行以检测时序相关操作。

**流行工具：**
- [Memsan](https://clang.llvm.org/docs/MemorySanitizer.html)：[教程](https://crocs-muni.github.io/ct-tools/tutorials/memsan)
- **Timecop**（见下文）

**优点：** 粒度化控制、目标分析
**缺点：** 覆盖范围仅限于执行路径

> **详细指南：** 见 **timecop** 技能的设置和使用。

### 4. 统计工具

使用各种输入执行代码，测量经过时间，并检测不一致性。测试实际实现，包括编译器优化和架构。

**流行工具：**
- **dudect**（见下文）
- [tlsfuzzer](https://github.com/tlsfuzzer/tlsfuzzer)

**优点：** 简单设置、实际现实结果
**缺点：** 无根本原因信息、噪声掩盖弱信号

> **详细指南：** 见 **dudect** 技能的设置和使用。

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
3. **对于高保证** - 应用形式验证（ct-verif, SideTrail）
4. **持续监控** - 将 dudect 集成到 CI 管道

## 工具和方法

### Dudect - 统计分析

[Dudect](https://github.com/oreparaz/dudect/) 测量两个输入类别（固定与随机）的执行时间，并使用 Welch's t-test 检测统计上显著差异。

> **详细指南：** 见 **dudect** 技能的完整设置、使用模式和 CI 集成。

#### 恒时分析的快速入门

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
- 通过 Welch's t-test 进行统计严谨性
- 可用于编译后的二进制文件（现实条件）

**主要限制：**
- 检测到泄露时无根本原因信息
- 对测量噪声敏感
- 不能保证不存在泄露（仅统计置信度）

### Timecop - 动态跟踪

[Timecop](https://post-apocalyptic-crypto.org/timecop/) 包装 Valgrind 以检测依赖于秘密内存区域的运行时操作。

> **详细指南：** 见 **timecop** 技能的安装、示例和调试。

#### 恒时分析的快速入门

```c
#include "valgrind/memcheck.h"

#define poison(addr, len) VALGRINDMAKE_MEM_UNDEFINED(addr, len)
#define unpoison(addr, len) VALGRINDMAKE_MEM_DEFINED(addr, len)

int main() {
    unsigned long long secret_key = 0x12345678;

    // 将秘密标记为中毒
    poison(&secret_key, sizeof(secret_key));

    // 任何依赖于 secret_key 的分支或内存访问
    // 都将由 Valgrind 报告
    crypto_operation(secret_key);

    unpoison(&secret_key, sizeof(secret_key));
}
```

使用 Valgrind 运行：
```bash
valgrind --leak-check=full --track-origins=yes ./binary
```

**主要优点：**
- 指定时序泄露的确切行
- 无需代码注入
- 跟踪秘密通过执行的传播

**主要限制：**
- 无法检测微架构时序差异
- 覆盖范围仅限于执行路径
- 性能开销（在合成 CPU 上运行）

## 实现指南

### 阶段 1：初始评估

**识别处理秘密的密码学代码：**
- 私钥、指数、nonce
- 密码哈希、身份验证令牌
- 加密/解密操作

**快速统计检查：**
1. 为密码学函数编写 dudect 框架
2. 运行 `timeout 600 ./ct_test` 5-10 分钟
3. 监控 t 值：绝对值高表示泄露

**工具：** dudect
**预期时间：** 1-2 小时（框架编写 + 初始运行）

### 阶段 2：详细分析

如果 dudect 检测到泄露：

**根本原因调查：**
1. 使用 Timecop `poison()` 标记秘密变量
2. 在 Valgrind 下运行以识别确切行
3. 审查四个常见违规模式
4. 检查汇编输出中的条件分支

**工具：** Timecop, 编译器输出 (`objdump -d`)

### 阶段 3：修复

**修复时序泄露：**
- 用恒时选择替换条件分支（位操作）
- 使用恒时比较函数
- 用恒时替代或掩码替换数组查找
- 验证编译器不会优化掉恒时代码

**重新验证：**
1. 运行 dudect 再次进行长时间（30+ 分钟）
2. 在不同的编译器和优化级别上测试
3. 在不同的 CPU 架构上测试

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
| 变量时间除法 | `result = x / secret` | Timecop | 中 |
| 变量时间移位 | `result = x << secret` | Timecop | 中 |
| Montgomery 约减泄露 | 中间值 > N 时需要额外约减 | dudect | 高 |

### 秘密依赖分支：深入分析

**漏洞：**
基于分支是否被触发，执行时间不同。常见于优化的模幂运算（平方乘法）。

**如何用 dudect 检测：**
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
        input[0] = rand(); // 随机底数
        input[1] = (classes[i] == 0) ? FIXED_EXPONENT : rand(); // 固定与随机
    }
}
```

**如何用 Timecop 检测：**
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

Brumley 和 Boneh（2005 年）通过网络从 OpenSSL 中提取了 RSA 私钥。该漏洞利用了 Montgomery 乘法的变量时间约减步骤。

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
| 测试多个编译器（gcc, clang, MSVC） | 优化可能引入或消除泄露 |
| 运行 dudect 延长时间（数小时） | 提高统计置信度 |
| 最小化非密码学代码在框架中 | 减少掩盖弱信号的噪声 |
| 检查汇编输出 (`objdump -d`) | 验证编译器没有引入分支 |
| 使用 `-O3 -march=native` 在测试中 | 匹配生产优化级别 |

### 常见错误

| 错误 | 错误原因 | 正确做法 |
|---------|----------------|------------------|
| 仅测试单一输入分布 | 可能遗漏在其他模式下可见的泄露 | 测试固定值对随机值、固定值对不同固定值等组合 |
| 短时间的 dudect 运行（少于 1 分钟） | 测量次数不足，无法检测弱信号 | 运行 5-10 分钟以上，需更高置信度时运行更长时间 |
| 忽略编译器优化级别 | `-O0` 可能掩盖在 `-O3` 中存在的泄露 | 在生产环境的优化级别下进行测试 |
| 未在目标架构上测试 | x86 与 ARM 具有不同的时序特性 | 在部署平台上进行测试 |
| 在 Timecop 中标记过多内容为秘密数据 | 导致误报，结果不明确 | 仅标记真正的秘密数据（如密钥，而非公开数据） |

## 相关技能

### 工具技能

| 技能 | 在常数时间分析中的主要用途 |
|-------|---------------------------------------|
| **dudect** | 通过 Welch 的 t 检验统计检测时序差异 |
| **timecop** | 动态跟踪以精确定位时序泄露的位置 |

### 技术技能

| 技能 | 适用场景 |
|-------|---------------|
| **coverage-analysis** | 确保测试输入覆盖加密函数中的所有代码路径 |
| **ci-integration** | 在持续集成流水线中自动化常数时间测试 |

### 相关领域技能

| 技能 | 关联关系 |
|-------|--------------|
| **crypto-testing** | 常数时间分析是加密测试的重要组成部分 |
| **fuzzing** | 对加密代码进行模糊测试可能会触发依赖于时序的代码路径 |

## 技能依赖关系图

```
                    ┌─────────────────────────┐
                    │  constant-time-analysis │
                    │     (此技能)             │
                    └───────────┬─────────────┘
                                │
                ┌───────────────┴───────────────┐
                │                               │
                ▼                               ▼
    ┌───────────────────┐           ┌───────────────────┐
    │      dudect       │           │     timecop       │
    │  (统计方法)       │           │    (动态方法)      │
    └────────┬──────────┘           └────────┬──────────┘
             │                               │
             └───────────────┬───────────────┘
                             │
                             ▼
              ┌──────────────────────────────┐
              │   辅助技术                   │
              │  代码覆盖、CI 集成          │
              └──────────────────────────────┘
```

## 资源

### 关键外部资源

**[这些结果必须是假阴性：常数时间分析工具的可用性评估](https://www.usenix.org/system/files/sec24fall-prepub-760-fourne.pdf)**
针对常数时间分析工具的综合可用性研究。关键发现：开发人员难以应对误报，需要更好的错误信息提示，并从工具集成中受益。该研究评估了多个加密实现中的 FaCT、ct-verif、dudect 和 Memsan。建议改进工具的交互界面并完善文档。

**[常数时间工具列表 - CROCS](https://crocs-muni.github.io/ct-tools/)**
精心整理的常数时间分析工具目录，附带教程。涵盖形式化工具（ct-verif, FaCT）、动态工具（Memsan, Timecop）、符号工具（Binsec）和统计工具（dudect）。包含关于安装和使用的实用教程。

**[Paul Kocher：针对 Diffie-Hellman、RSA、DSS 及其他系统实现的时序攻击](https://paulkocher.com/doc/TimingAttacks.pdf)**
1996 年引入时序攻击的开创性论文。展示了针对 RSA 和 Diffie-Hellman 中模幂运算的攻击。是理解时序漏洞必要历史背景。

**[远程时序攻击是可行的（Brumley & Boneh）](https://crypto.stanford.edu/~dabo/papers/ssl-timing.pdf)**
展示了对 OpenSSL 的实用远程时序攻击。证明了网络层面的时序差异足以提取 RSA 密钥。证实了时序攻击在真实的网络条件下是有效的。

**[针对 AES 的缓存时序攻击](https://cr.yp.to/antiforgery/cachetiming-20050414.pdf)**
表明使用查找表的 AES 实现容易受到缓存时序攻击的影响。展示了通过缓存时序侧通道提取 AES 密钥的实用攻击方法。

**[KyberSlash：除法时序泄露秘密](https://eprint.iacr.org/2024/1049.pdf)**
最近发现的 Kyber（NIST 后量子标准）中的时序漏洞。显示除法操作会泄露秘密系数。凸显了即使在现代后量子密码学中，常数时间问题依然存在。

### 视频资源

- [Trail of Bits：常数时间编程](https://www.youtube.com/watch?v=vW6wqTzfz5g) - 常数时间编程原则和工具的概述
