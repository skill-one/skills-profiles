# CTF 密码学

快速参考加密 CTF 挑战。每种技术在这里都有一个简短的说明；有关完整代码的详细说明，请参阅支持文件。

## 前置条件

**Python 包（所有平台）：**
```bash
pip install pycryptodome z3-solver sympy gmpy2 hashpumpy fpylll py_ecc
# Coppersmith（可选）：pip install coppersmith
# 替代 Coppersmith 库：git clone https://github.com/jvdsn/crypto-attacks ~/.ctf-tools/crypto-attacks && pip install -r ~/.ctf-tools/crypto-attacks/requirements.txt
```

**Linux (apt):**
```bash
apt install hashcat
```

**macOS (Homebrew):**
```bash
brew install hashcat
```

**手动安装：**
- SageMath（可选——仅用于遗留 Sage 回退片段（折叠部分））— Linux: `apt install sagemath`, macOS: `brew install --cask sage`
- RsaCtfTool — `git clone https://github.com/RsaCtfTool/RsaCtfTool`（自动 RSA 攻击）
- crypto-attacks (Coppersmith) — `git clone https://github.com/jvdsn/crypto-attacks ~/.ctf-tools/crypto-attacks` + `pip install -r ~/.ctf-tools/crypto-attacks/requirements.txt`（`pip install coppersmith` 的替代方案）

> **注意：** `gmpy2` 需要 libgmp — Linux: `apt install libgmp-dev`, macOS: `brew install gmp`.

## 额外资源

- [classic-ciphers.md](classic-ciphers.md) - 古典密码：Vigenere（+ Kasiski 检查），Atbash，替换轮，XOR 变体（+ 多字节频率分析），确定性 OTP，级联 XOR，书籍密码，OTP 密钥重用 / 多次垫，可变长度同音替代表，网格排列密码密钥空间缩减，基于图像的 Caesar 移位密码，通过文件格式头部恢复 XOR 密钥
- [modern-ciphers.md](modern-ciphers.md) - 现代密码攻击：AES (CFB-8, ECB 泄露), CBC-MAC/OFB-MAC, 填充Oracle, S-box 碰撞, GF(2) 消除, LCG 部分输出恢复, 复合模数上的仿射密码, AES-GCM 使用派生密钥, AES-GCM 非法重用 nonce（禁止攻击），Ascon 类似减少轮次的差分密码分析, 自定义线性 MAC 拒绝, CBC 填充Oracle（完整块解密）, Bleichenbacher RSA PKCS#1 v1.5 填充Oracle（ROBOT）, 生日攻击 / 中间相遇, CRC32 碰撞签名拒绝, AES 通过逐字节清零Oracle恢复 AES 密钥, AES-CBC 纠删码伪造通过错误消息解密Oracle
- [modern-ciphers-2.md](modern-ciphers-2.md) - 现代密码攻击（第 2 部分）：Blum-Goldwasser 位扩展Oracle, 哈希长度扩展, 压缩Oracle（CRIME风格）, 通过循环检测反转哈希函数, OFB 模式可逆随机数生成器反向解密, 通过公钥哈希 XOR 导出弱密钥, HMAC-CRC 线性攻击, DES 弱密钥在 OFB 模式下, SRP 协议绕过, 修改 AES S-Box 暴力破解, 减少轮次 AES 的平方攻击, AES-ECB 字节选择明文, AES-ECB 切片块操作, AES-CBC IV 位翻转身份验证绕过, Rabin LSB 奇偶校验Oracle, PBKDF2 预先哈希绕过, MD5 多次碰撞通过 fastcol
- [modern-ciphers-3.md](modern-ciphers-3.md) - 现代密码攻击（第 3 部分）：自定义哈希状态反转, CRC32 暴力破解（小有效载荷）, 噪声 RSA LSB Oracle 错误校正, 拖把哈希 MITM 碰撞, CBC IV 伪造 + 块截断, 填充Oracle 到 CBC 位翻转 RCE, SPN S-box 交集攻击, AES-CFB IV 恢复来自时间戳种子伪随机数生成器, 三轮 XOR 协议密钥取消, AES-CBC UnicodeDecodeError 侧信道Oracle, SHA-256 基础攻击用于 XOR 聚合哈希绕过, 自定义 MAC 拒绝通过 XOR 块取消, HMAC 密钥恢复通过 XOR+加法算术
- [modern-ciphers-4.md](modern-ciphers-4.md) - 现代密码攻击（第 4 部分）：ChaCha20-Poly1305 nonce 重用禁止攻击在 $2^{130}-5$ 上（RFC 8439, CTR $C_1\oplus C_2=P_1\oplus P_2$, Poly1305 $\sum c_i r^{n-i}$ 通过 galois/sympy, 2消息 $ad=""$ 向量), 分区Oracle / 密钥提交 AEAD 分割格网, 拖把生成器普遍性（SHA-3/Keccak $0x06$ vs $0x01$, Ascon/Gimli/Sparkle 速率/容量/轮次/填充表 + 末尾字节序工作流程), eSTREAM Trivium 1152 轮预热 & 立方体攻击概述（Grain）
- [stream-ciphers.md](stream-ciphers.md) - 流密码攻击：LFSR（Berlekamp-Massey, 相关攻击, 已知明文, Galois 与 Fibonacci, Galois 倒数通过自相关恢复），RC4 第二字节偏差, XOR 连续字节相关
- [rsa-attacks.md](rsa-attacks.md) - RSA 攻击：小 e（立方根），共同模数, Wiener 攻击, Pollard 的 p-1, Hastad 的广播, Hastad 与线性填充（Coppersmith）, Franklin-Reiter 相关消息（e=3）, Coppersmith 线性相关素数, Fermat/连续素数, 多素数, 限制数字, Coppersmith 结构化素数, Manger Oracle, 多项式哈希
- [rsa-attacks-2.md](rsa-attacks-2.md) - RSA 攻击（特殊化）：RSA p=q 验证绕过, 立方根 CRT gcd(e,phi)>1, 从 phi(n) 多倍数分解, 乘法同态签名拒绝, 通过基表示生成弱密钥, RSA 与 gcd(e,phi)>1 指数减少, 批量 GCD 共享素数分解, 从 dp/dq/qinv 恢复部分密钥, RSA-CRT 故障攻击, 同态解密Oracle 绕过, 小素数 CRT 分解, Montgomery 减少时序攻击, Bleichenbacher 低指数签名拒绝, RSA 签名绕过与 e=1 和精心设计的模数
- [ecc-attacks.md](ecc-attacks.md) - 椭圆曲线攻击：小子群, 无效曲线, 奇异曲线, Smart 攻击（异常，带有 Sage 代码）, 故障注入, 时钟组 DLP, Pohlig-Hellman, ECDSA nonce 重用, Ed25519 扭结侧信道, DSA nonce 重用, 通过 MD5 碰撞恢复 DSA 密钥, X25519 低阶点 + 所有零检查
- [dh-attacks.md](dh-attacks.md) - 经典有限域 DH：平凡的 g (0/1/p-1), 当 p-1 平滑时 Pohlig-Hellman, 小子群限制 / Lim-Lee 静态密钥恢复通过 CRT, 静态与临时 + Logjam 下调分级
- [zkp-and-advanced.md](zkp-and-advanced.md) - ZKP/图 3 色彩, Z3 求解器指南, 混乱电路, Shamir SSS, 大双词约束求解, 竞态条件, Groth16 故障设置, DV-SNARG 拒绝, KZG 配对Oracle 用于排列恢复, Shamir SSS 重用多项式系数
- [prng.md](prng.md) - PRNG 攻击（基础）：MT19937, MT 浮点恢复通过 GF(2) 魔法矩阵用于令牌预测, LCG, GF(2) 矩阵 PRNG, V8 XorShift128+ Math.random 状态恢复通过 Z3, 中间平方, 确定性 RNG 山羊爬坡, 随机模式Oracle, 基于时间的种子, 通过 ctypes 的 C srand/rand 同步, 密码破解, 对数映射混沌 PRNG
- [prng-attacks.md](prng-attacks.md) - PRNG 攻击（CTF 时代，2017+）：MT 子集和种子恢复, MT19937 约束传播, 规则 86 细胞自动机反转通过 Z3, Java LCG 中间相遇部分模数, LCG 向后步进通过模逆, LFSR 位折叠 ASCII 奇偶校验, Z3 求解时间时序Oracle, randcrack DSA k 预测, 格式字符串 PRNG 种子偏移, NTP 毒化 PRNG UUID XOR
- [historical.md](historical.md) - 历史密码（Lorenz SZ40/42, 书籍密码实现）
- [advanced-math.md](advanced-math.md) - 高级数学攻击（同构, Pohlig-Hellman, 小步大步 (BSGS) 用于一般 DLP, LLL, Merkle-Hellman 背包通过 LLL, Coppersmith 通过 Howgrave-Graham hg_matrix -> IntegerMatrix -> LLL -> sympy Poly (beta=0.5, 单调检查, flatter 可选 dim>100), 四元数 RSA, GF(2)[x] CRT, S-box 碰撞代码, LWE 格子 CVP 攻击, 非素数模数上的仿射密码, 通过 GF(2) 线性代数进行反思性 CRC)

## 格子 / LWE 攻击

- **快速分级：** 如果挑战提供模线性方程式和一个隐藏量很小、稀疏、有偏差或部分泄露的承诺，首先将其视为格子候选。参见 [lattice-and-lwe.md](lattice-and-lwe.md#快速分级这是否是一个格子问题).
- **LLL / BKZ / Babai：** fpylll LLL.reduction / BKZ.reduction / GSO.Mat.babai / CVP.closest_vector (Sage Matrix(ZZ).LLL() / M.BKZ 回退在详细说明中) — 从 LLL 开始，当 LLL 几乎起作用时转到 BKZ，使用 Babai 进行近似 CVP。参见 [lattice-and-lwe.md](lattice-and-lwe.md#核心工具 lll-bkz-babai-cvp-svp asis-ctf-finals-2015-ctfzone-2017).
- **HNP 来自部分 nonce 泄露：** 部分或有偏差的 ECDSA/Schnorr 非ces，通常减少为隐藏数字问题格子；规范化方程式，隔离有界误差，减少，如果需要，则逆向最后几个位。参见 [lattice-and-lwe.md](lattice-and-lwe.md#隐藏数字问题 hnp 部分nonce--有偏差nonce-nullcon-hackim-2020-ledger-donjon-ctf-2020).
- **截断 LCG 状态恢复：** 高位或低位泄露来自仿射递归通常是 HNP 的伪装；将每个状态写成 `observed * 2^t + hidden` 并求解小的 hidden 修正。参见 [lattice-and-lwe.md](lattice-and-lwe.md#lcg 和截断输出作为格子问题 x-mas-ctf-2018-fwordctf-2020).
- **LWE 通过 CVP (Babai)：** 从 `[q*I | 0; A^T | I]` 构造格子，使用 fpylll GSO.Mat.babai 或 CVP.closest_vector 找到最近向量，投影到三元 {-1,0,1}。注意服务器描述和实际编码之间的字节序不匹配。
- **Ring-LWE / Module-LWE 识别：** 多项式或负循环结构通常看起来很可怕，但许多 CTFs 通过使用微小的系数、有缺陷的表示或足够的泄露将其减弱回普通的 LWE。参见 [lattice-and-lwe.md](lattice-and-lwe.md#ring-lwe--module-lwe 识别说明 plaidctf-2016-dicectf-2022).
- **正交格子：** 隐藏子集或隐藏子空间问题可能需要您首先恢复正交格子，然后从其补码中重建实际二进制或短基。参见 [lattice-and-lwe.md](lattice-and-lwe.md#正交格子 hssp--ahssp 风格恢复 zer0pts-ctf-2022).
- **LLL 用于近似 GCD：** fpylll LLL.reduction (Sage Matrix(ZZ).LLL() 回退) — 格子中的短向量揭示了隐藏因子
- **子集和背包：** 二进制背包和低密度子集和实例仍然是经典的格子领域；构建标准基，寻找具有零最终坐标的简化行。参见 [lattice-and-lwe.md](lattice-and-lwe.md#子集和背包 via lattice reduction hitcon-ctf-2017-backdoorctf-2023).
- **多层挑战：** 几何 → 子空间恢复 → LWE → AES-GCM 解密链

参见 [advanced-math.md](advanced-math.md) 的 LWE 解法代码和 [lattice-and-lwe.md](lattice-and-lwe.md) 的攻击选择、嵌入和失败模式分级。

## ZKP & 约束求解

- **ZKP 欺骗：** 对于不可能的问题（3-色 K4），找到哈希碰撞或预测 PRNG 盐
- **图 3 色彩：** `nx.coloring.greedy_color(G, strategy='saturation_largest_first')`
- **Z3 求解器：** BitVec 用于位级, Int 用于任意精度; BPF/SECCOMP 过滤求解
- **混乱电路（免费 XOR）：** XOR 三个真值表条目以恢复全局 delta
- **双词替换：** OR-Tools CP-SAT 使用自动机约束以已知明文结构
- **三词分解：** 位置模 n 形成独立的单字母密码
- **Shamir SSS (确定性系数)：** 一个份额 + 种子随机数 = 单变量方程中的秘密
- **竞态条件 (TOCTOU)：** 同步并发请求绕过 `counter < N` 检查
- **Groth16 故障设置 (delta==gamma)：** 容易伪造：A=alpha, B=beta, C=-vk_x。始终首先检查验证器常量
- **Groth16 证明重放：** 无约束 nullifier + 无跟踪 = 从设置 tx 无限重放。参见 [zkp-and-advanced.md](zkp-and-advanced.md#groth16 证明重放).
- **DV-SNARG 拒绝：** 使用验证器 Oracle 访问，从无约束对中学习秘密 v 值，通过 CRS 条目取消伪造。参见 [zkp-and-advanced.md](zkp-and-advanced.md#shamir-secret-sharing-with-reused-polynomial-coefficients-polictf-2017).

参见 [zkp-and-advanced.md](zkp-and-advanced.md) 的完整代码示例和解算器模式。

## 现代密码攻击（附加）

- **复合模数上的仿射密码：** `c = A*x+b (mod M)`, M 复合（例如，65=5*13）。通过单热向量选择明文恢复，每个素数因子的 CRT 翻转。参见 [modern-ciphers.md](modern-ciphers.md#复合模数上的仿射密码 nullcon-2026).
- **自定义线性 MAC 拒绝：** 基于XOR的签名与秘密块线性相关。从约 5 个已知对中恢复秘密，伪造目标。参见 [modern-ciphers.md](modern-ciphers.md#自定义线性mac拒绝 nullcon-2026).
- **Manger Oracle (RSA 阈值)：** RSA 乘法 + 二进制搜索 on `m*s < 2^128`. ~128 次查询以恢复 AES 密钥。

## 通过 GF(2) 线性代数进行反思性 CRC

自我指代 CRC：找到 ASCII 字符串，其 CRC 等于自身。CRC 在 GF(2) 上是线性的，因此约束变成了可解的线性系统。自由变量选择可打印 ASCII 范围。参见 [advanced-math.md](advanced-math.md#introspective-crc-via-gf2-linear-algebra-google-ctf-2017).

## CBC 填充Oracle攻击

服务器揭示有效/无效填充 → 解密任何 CBC 密文而无需密钥。每个 16 字节块约 4096 次查询。使用 PadBuster 或 `padding-oracle` Python 库。参见 [modern-ciphers.md](modern-ciphers.md#cbc-padding-oracle-attack).

## Bleichenbacher RSA 填充Oracle (ROBOT)

RSA PKCS#1 v1.5 填充验证Oracle → 自适应选择密文明文恢复。RSA-2048 约需 10K 次查询。影响 TLS 实现通过时序。参见 [modern-ciphers.md](modern-ciphers.md#bleichenbacher--pkcs1-v15-rsa-padding-oracle).

## 生日攻击 / 中间相遇

n 位哈希碰撞在 ~2^(n/2) 次尝试中。中间相遇打破双重加密在 O(2^k) 而不是 O(2^(2k))。参见 [modern-ciphers.md](modern-ciphers.md#生日攻击--中间相遇).

- **拖把哈希 MITM 碰撞：** 当拖把速率小于状态大小，不受控制的状
