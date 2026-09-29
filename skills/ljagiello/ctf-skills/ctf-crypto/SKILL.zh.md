---
name: ctf-crypto
description: 为CTF挑战提供密码学攻击技术。在攻击加密、哈希、签名、ZKP、PRNG或涉及RSA、AES、ECC、格、LWE、CVP、数论、Coppersmith、Pollard、Wiener、填充回退、GCM、密钥派生或流/分组密码弱点的数学密码问题时使用。
---

# 密码学CTF

加密CTF挑战的快速参考。每种技术在这里都有一个简短的代码示例；支持文件包含完整代码细节。

## 前置条件

**Python包（所有平台）：**
```bash
pip install pycryptodome z3-solver sympy gmpy2 hashpumpy fpylll py_ecc
# Coppersmith（可选）：pip install coppersmith
# 替代Coppersmith库：git clone https://github.com/jvdsn/crypto-attacks ~/.ctf-tools/crypto-attacks && pip install -r ~/.ctf-tools/crypto-attacks/requirements.txt
```

**Linux（apt）：**
```bash
apt install hashcat
```

**macOS（Homebrew）：**
```bash
brew install hashcat
```

**手动安装：**
- SageMath（可选——仅用于遗留Sage回退片段（折叠部分））— Linux: `apt install sagemath`, macOS: `brew install --cask sage`
- RsaCtfTool — `git clone https://github.com/RsaCtfTool/RsaCtfTool`（自动化RSA攻击）
- crypto-attacks（Coppersmith）— `git clone https://github.com/jvdsn/crypto-attacks ~/.ctf-tools/crypto-attacks` + `pip install -r ~/.ctf-tools/crypto-attacks/requirements.txt`（`pip install coppersmith`的替代方案）

> **注意：** `gmpy2`需要libgmp — Linux: `apt install libgmp-dev`, macOS: `brew install gmp`。

## 额外资源

- [classic-ciphers.md](classic-ciphers.md) - 古典密码：维吉尼亚密码（+卡西斯基检验），阿塔巴什，替换轮，XOR变体（+多字节频率分析），确定性OTP，级联XOR，书本密码，OTP密钥重用/多次填充，可变长度同音替换，网格置换密码密钥空间缩减，基于图像的凯撒移位密码，通过文件格式头部恢复XOR密钥
- [modern-ciphers.md](modern-ciphers.md) - 现代密码攻击：AES（CFB-8，ECB泄漏），CBC-MAC/OFB-MAC，填充漏洞，S-box碰撞，GF(2)消除，LCG部分输出恢复，复合模线性密码，AES-GCM使用派生密钥，AES-GCM nonce重用（禁止攻击），类似Ascon的降轮差分密码分析，自定义线性MAC伪造，CBC填充漏洞（完整块解密），Bleichenbacher RSA PKCS#1 v1.5填充漏洞（ROBOT），生日攻击/中间相遇，CRC32碰撞签名伪造，通过字节逐个清零或器恢复AES密钥，通过错误消息解密器伪造AES-CBC密文
- [modern-ciphers-2.md](modern-ciphers-2.md) - 现代密码攻击（第2部分）：Blum-Goldwasser位扩展或器，哈希长度扩展，压缩或器（CRIME风格），通过循环检测反转哈希函数时间，OFB模式可逆随机数生成器逆向解密，通过公钥哈希XOR推导弱密钥，HMAC-CRC线性攻击，DES OFB模式弱密钥，SRP协议绕过，修改AES S-Box暴力破解，降轮AES的平方攻击，AES-ECB字节逐个选择明文，AES-ECB块操作，AES-CBC IV位翻转认证绕过，Rabin LSB奇偶校验或器，PBKDF2预哈希绕过，通过fastcol进行MD5多碰撞
- [modern-ciphers-3.md](modern-ciphers-3.md) - 现代密码攻击（第3部分）：自定义哈希状态反转，CRC32小负载暴力破解，噪声RSA LSB或器错误校正，海绵哈希中间相遇碰撞，CBC IV伪造+块截断，填充漏洞到CBC位翻转RCE，SPN S-box交集攻击，AES-CFB IV从时间种子伪随机数生成器恢复，三轮XOR协议密钥取消，AES-CBC UnicodeDecodeError侧信道或器，SHA-256基攻击用于XOR聚合哈希绕过，通过XOR块取消自定义MAC伪造，通过XOR+加法算术恢复HMAC密钥
- [modern-ciphers-4.md](modern-ciphers-4.md) - 现代密码攻击（第4部分）：ChaCha20-Poly1305 nonce重用禁止攻击（$2^{130}-5$，RFC 8439，CTR $C_1\oplus C_2=P_1\oplus P_2$，Poly1305 $\sum c_i r^{n-i}$通过galois/sympy，2消息$ad=""$向量），分割或器/密钥提交AEAD矩阵，海绵通用性（SHA-3/Keccak $0x06$ vs $0x01$，Ascon/Gimli/Sparkle速率/容量/轮数/填充表+字节序工作流），eSTREAM Trivium 1152轮预热&立方攻击概述（Grain）
- [stream-ciphers.md](stream-ciphers.md) - 流密码攻击：LFSR（Berlekamp-Massey，相关攻击，已知明文，Galois vs Fibonacci，通过自相关恢复Galois抽头），RC4第二字节偏差，XOR连续字节相关
- [rsa-attacks.md](rsa-attacks.md) - RSA攻击：小e（立方根），共同模数，Wiener，Pollard p-1，Hastad广播，Hastad带线性填充（Coppersmith），Franklin-Reiter相关消息（e=3），Coppersmith线性相关素数，Fermat/连续素数，多素数，限制数字，Coppersmith结构化素数，Manger或器，多项式哈希
- [rsa-attacks-2.md](rsa-attacks-2.md) - RSA攻击（专门）：RSA p=q验证绕过，立方根CRT gcd(e,phi)>1，从phi(n)倍数分解，乘法同态签名伪造，通过基数表示生成弱密钥，带gcd(e,phi)>1指数缩减的RSA，批量GCD共享素数分解，从dp/dq/qinv部分密钥恢复，RSA-CRT故障攻击，同态解密或器绕过，小素数CRT分解，Montgomery缩减时序攻击，Bleichenbacher低指数签名伪造，带e=1和定制模数的RSA签名绕过
- [ecc-attacks.md](ecc-attacks.md) - ECC攻击：小子群，无效曲线，Smart攻击（异常，带Sage代码），故障注入，时钟群DLP，Pohlig-Hellman，ECDSA nonce重用，Ed25519扭转侧信道，DSA nonce重用，通过MD5碰撞在k生成中恢复DSA密钥，X25519低阶点+全零检查
- [dh-attacks.md](dh-attacks.md) - 经典有限域DH：平凡g（0/1/p-1），当p-1平滑时Pohlig-Hellman，小子群限制/Lim-Lee静态密钥恢复通过CRT，静态vs临时+Logjam降级分类
- [zkp-and-advanced.md](zkp-and-advanced.md) - ZKP/图3着色，Z3求解器指南，混淆电路，Shamir SSS，双字母约束求解，竞争条件，Groth16故障设置，DV-SNARG伪造，KZG配对或器用于排列恢复，Shamir SSS重复多项式系数
- [prng.md](prng.md) - PRNG攻击（基础）：MT19937，通过GF(2)魔法矩阵MT浮点恢复用于令牌预测，LCG，GF(2)矩阵PRNG，V8 XorShift128+ Math.random状态恢复通过Z3，中平方，确定性随机数生成器山丘爬升，随机模式或器，基于时间的种子，通过ctypes同步C srand/rand，密码破解，逻辑映射混沌PRNG
- [prng-attacks.md](prng-attacks.md) - PRNG攻击（CTF时代，2017+）：MT子集和种子恢复，MT19937约束传播，通过Z3反转规则86元胞自动机，Java LCG中间相遇部分模数，通过模逆LCG逆向步进，LFSR位折叠ASCII奇偶校验，Z3求解时间时序或器，randcrack DSA k预测，格式字符串PRNG种子偏移，NTP中毒PRNG UUID XOR
- [historical.md](historical.md) - 历史密码（Lorenz SZ40/42，书本密码实现）
- [advanced-math.md](advanced-math.md) - 高级数学攻击（同构，Pohlig-Hellman，小步巨人步（BSGS）用于一般DLP，LLL，Merkle-Hellman背包通过LLL，Coppersmith通过Howgrave-Graham hg_matrix -> IntegerMatrix -> LLL -> sympy Poly（beta=0.5，monic检查，flatter可选dim>100），四元数RSA，GF(2)[x] CRT，S-box碰撞代码，LWE格点CVP攻击，非素数模数的仿射密码，通过GF(2)线性代数进行CRC内省）
- [lattice-and-lwe.md](lattice-and-lwe.md) - 格点攻击分类和流程：LLL/BKZ/Babai，HNP来自部分或偏差nonce，截断LCG状态恢复，LWE嵌入和CVP，环LWE/模块LWE识别，NTRU格点B=[[qI 0],[H I]]（负循环，BKZ，中心g），GGH嵌入[[B 0],[c lambda]] lambda扫描，梅森AJPS p=2^n-1 n=11213 w=10 6x6 s=5，BDD谓词/LadderLeak >100 sigs 1-4位，正交格点，子集和/背包，以及常见故障模式
- [post-quantum.md](post-quantum.md) - 量子后识别：ML-KEM（Kyber）k=2/3/4 q=3329 etau dv，ML-DSA，Falcon，模块LWE扁平化，FO故障或器，NTT，Kannan/Bai-Galbraith/Arora-Ge/estimator决策树，梅森AJPS细节
- [exotic-crypto.md](exotic-crypto.md) - 奇异代数结构（辫群DH / Alexander多项式，单调函数反转，热带半环剩余，Paillier密码系统，汉明码螺旋交织，ElGamal通用重新加密，FPE Feistel暴力破解，二十面体对称群密码，Goldwasser-Micali复制或器）
- [exotic-crypto-2.md](exotic-crypto-2.md) - 奇异代数结构（第2部分，2017+）：BB-84 QKD中间人，ElGamal平凡DLP（B=p-1），通过同态加倍Paillier LSB或器，差分隐私噪声消除，同态加密位提取，通过Jordan标准形矩阵上的ElGamal，通过Pollard OSS签名伪造，没有私钥的Cayley-Purser解密，BIP39部分助记符校验暴力破解，Asmuth-Bloom CRT阈值恢复，多项式素数Rabin，LCG周期检测，Vandermonde多项式系数恢复

---

## 何时转向

- 如果真正的障碍是理解混淆的二进制客户端或奇怪的虚拟机，切换到`/ctf-reverse`。
- 如果挑战主要是数据包雕刻，磁盘恢复或加密开始前的stego提取，切换到`/ctf-forensics`。
- 如果任务是在解决密码部分后对易受攻击的网络服务实现漏洞利用，切换到`/ctf-pwn`或`/ctf-web`。
- 如果密码挑战涉及对抗性ML，模型提取或基于神经网络的密码，切换到`/ctf-ai-ml`。
- 如果挑战真的是编码谜题，异类密码或多语言技巧而不是真正的密码分析，切换到`/ctf-misc`。

## 快速启动命令

```bash
# 识别密码类型
python3 -c "from Crypto.Util.number import *; n=<N>; print(f'bits={n.bit_length()}')"

# RSA快速检查
python3 -c "from sympy import factorint; print(factorint(<n>))"  # 小因子？
openssl rsa -pubin -in key.pub -text -noout  # 从PEM提取n, e

# 快速分解工具
python3 RsaCtfTool.py -n <n> -e <e> --uncipher <c>

# XOR分析
python3 -c "from pwn import xor; print(xor(bytes.fromhex('<hex>'), b'flag{'))"

# 哈希识别
hashid '<hash>'
hashcat --identify '<hash>'

# 快速分解（sympy，主要）
python3 -c "from sympy import factorint; print(factorint(<n>))"
# Sage替代：sage -c "print(factor(<n>))"
```

## 古典密码

- **凯撒密码：** 频率分析或暴力破解26个密钥
- **维吉尼亚密码：** 已知明文攻击带flag格式前缀；从`(ct - pt) mod 26`推导密钥。卡西斯基检验用于未知密钥长度（重复序列距离的GCD）
- **阿塔巴什：** A<->Z替换；在挑战名称中寻找"Abashed"提示
- **替换轮：** 暴力破解内/外字母映射的所有旋转
- **多字节XOR：** 按密钥位置分割密文，独立频率分析每一列；根据英语字母频率（空格 = 0x20）评分
- **级联XOR：** 暴力破解第一个字节（256次尝试），其余部分按确定性方式跟随
- **XOR旋转（2的幂）：** 偶/奇位不会混合；只有4个候选状态
- **弱XOR验证：** 单字节XOR检查通过率为1/256；足够预算时暴力破解
- **确定性OTP：** 已知明文XOR恢复密钥流；匹配负载平衡后端
- **OTP密钥重用（多次填充）：** `C1 XOR C2 XOR known_P = unknown_P`；当没有已知明文时进行crib dragging
- **同音（可变长度）：** 多个密文字符组映射到单个明文字符。找到n-gram具有相同子n-gram频率的组，用符号替换，作为单字母密码解决。见[classic-ciphers.md](classic-ciphers.md#variable-length-homophonic-substitution-asis-ctf-finals-2013)。
- **网格置换密码：** 5x5网格具有独立的行/列置换将密钥空间缩减到5! x 5! = 14,400；毫秒内暴力破解。见[classic-ciphers.md](classic-ciphers.md#grid-permutation-cipher-keyspace-reduction-bsidessf-2026)。
- **基于图像的凯撒移位：** 像素行/列按每条带的偏移量移位；比较原始与移位图像以从移位量中提取ASCII编码的flag。见[classic-ciphers.md](classic-ciphers.md#image-based-caesar-shift-ciphers-bsidessf-2026)。
- **Polybius方格密码：** 5x5网格将字母对映射到明文；数字/坐标编码位置。见[classic-ciphers.md](classic-ciphers.md#polybius-square-cipher-qiwi-infosec-2016)。
- **通过文件格式头部恢复XOR密钥：** 文件声称是PDF/PNG/ZIP但`file`报告"数据"。XOR第一个字节与预期魔术字节以导出重复密钥；使用尾随结构（`%%EOF`，IEND标记）扩展。见[classic-ciphers.md](classic-ciphers.md#xor-key-recovery-via-file-format-headers-metactf-flash-2026)。

见[classic-ciphers.md](classic-ciphers.md)获取完整代码示例。

## 现代密码攻击

- **AES-ECB:** 块置换，逐字节选择明文后缀恢复（每字节256次查询，工具：FeatherDuster `ecb_cpa_decrypt`）；图像ECB保留视觉模式。ECB剪切粘贴：拼接密文块以伪造JSON字段（例如，`is_admin: true`）。参见 [modern-ciphers-2.md](modern-ciphers-2.md#aes-ecb-byte-at-a-time-chosen-plaintext-abctf-2016)。
- **AES-CBC:** 比特翻转以改变明文；无密钥的解密填充oracle。IV比特翻转：翻转IV中的特定比特以改变第一个明文块（无需MAC）。参见 [modern-ciphers-2.md](modern-ciphers-2.md#aes-cbc-iv-bit-flip-authentication-bypass-google-ctf-2016)。
- **CBC IV伪造+块截断:** XOR IV字节以改变解密块0；剥离尾随密文块（CBC中无长度完整性）。当MAC嵌入密文时伪造认证令牌。参见 [modern-ciphers-3.md](modern-ciphers-3.md#cbc-iv-forgery--block-truncation-for-authentication-bypass-0ctf-2017)。
- **填充oracle到CBC比特翻转RCE:** 链接填充oracle（恢复明文）与CBC比特翻转（注入shell元字符）以通过加密参数进行命令注入。参见 [modern-ciphers-3.md](modern-ciphers-3.md#padding-oracle-to-cbc-bitflip-command-injection-bsidessf-2017)。
- **AES-CFB-8:** 8位反馈的静态IV允许在16个已知字节后重建状态
- **CBC-MAC/OFB-MAC:** 用于签名伪造的XOR密钥流：`new_sig = old_sig XOR block_diff`
- **S-box碰撞:** 非置换S-box（`len(set(sbox)) < 256`）允许4,097查询密钥恢复
- **GF(2)消除:** 线性哈希函数（XOR + 旋转）通过GF(2)上的高斯消元求解
- **填充oracle:** 逐字节解密通过修改前一个块并测试填充有效性
- **LFSR流密码器:** Berlekamp-Massey从2L密钥流位中恢复反馈多项式；相关攻击通过有偏组合函数破坏组合生成器
- **Galois LFSR抽头恢复:** XOR已知文件头（PNG/PDF/ZIP）与密文以获取密钥流；分成N位窗口，计算 `(state >> 1) XOR next_state` 以直接恢复抽头掩码。自相关滑动找到正确长度。参见 [stream-ciphers.md](stream-ciphers.md#galois-lfsr-tap-recovery-via-autocorrelation-bsidessf-2026)。
- **OFB与可逆RNG:** 任何块的已知明文泄露RNG状态；如果状态转换是双射的，则反向运行RNG以解密所有块。参见 [modern-ciphers-2.md](modern-ciphers-2.md#ofb-mode-with-invertible-rng-backward-decryption-bsidessf-2026)。
- **弱密钥派生（公钥哈希XOR）:** 从 `SHA256(public_key) XOR seed` 派生的AES密钥完全可恢复，无需私钥；“混合”RSA+AES不提供安全性。参见 [modern-ciphers-2.md](modern-ciphers-2.md#weak-key-derivation-via-public-key-hash-xor-bsidessf-2026)。
- **HMAC-CRC线性:** CRC在GF(2)上是线性的，因此HMAC-CRC密钥可以通过多项式运算从单个消息-MAC对中恢复。参见 [modern-ciphers-2.md](modern-ciphers-2.md#hmac-crc-linearity-attack-boston-key-party-2016)。
- **DES弱密钥在OFB:** 4个DES弱密钥使加密自反；OFB密钥流周期为2，减少为16字节重复XOR。参见 [modern-ciphers-2.md](modern-ciphers-2.md#des-weak-keys-in-ofb-mode-boston-key-party-2016)。
- **平方攻击（减轮AES）:** 4轮AES被积分密码分析破解：256-明文lambda集，通过XOR和=0区分器猜测最后一轮密钥字节。参见 [modern-ciphers-2.md](modern-ciphers-2.md#square-attack-on-reduced-round-aes-0ctf-2016)。
- **AES-GCM nonce重用（禁止攻击）:** 相同nonce = CTR密钥流重用 + 通过GF(2^128)的多项式分解恢复GHASH认证密钥。工具：`nonce-disrespect`。参见 [modern-ciphers.md](modern-ciphers.md#aes-gcm-nonce-reuse--forbidden-attack)。
- **SRP协议绕过:** 发送 `A = 0` 或 `A = n` 以强制共享密钥为0，完全绕过密码验证。参见 [modern-ciphers-2.md](modern-ciphers-2.md#srp-secure-remote-password-protocol-bypass-via-modular-arithmetic-asis-ctf-finals-2016)。
- **修改的AES S-Box暴力破解:** 定制S-Box仅16个唯一输出降低了密钥熵；每轮暴力破解可行密钥字节。参见 [modern-ciphers-2.md](modern-ciphers-2.md#modified-aes-s-box-brute-force-recovery-h4ckit-ctf-2016)。
- **Rabin LSB奇偶校验oracle:** Rabin密文 `c = m^2 mod n` 与LSB oracle启用通过乘法同态在 `log2(n)` 查询中二进制搜索明文恢复（`c * 4 mod n` 将明文加倍）。参见 [modern-ciphers-2.md](modern-ciphers-2.md#rabin-cryptosystem-lsb-parity-oracle-plaidctf-2016)。
- **Noisy RSA LSB oracle错误校正:** 当LSB oracle有随机错误时，运行标准攻击然后检查输出字符集。翻转错误位置的oracle结果以校正剩余解密。参见 [modern-ciphers-3.md](modern-ciphers-3.md#noisy-rsa-lsb-oracle-with-post-hoc-error-correction-sharifctf-7-2016)。
- **PBKDF2预哈希绕过:** HMAC预哈希超过64字节的密钥（SHA-1/SHA-256块大小）。当原始超过64字节时，使用 `SHA1(password)` 而不是 `password` 登录。参见 [modern-ciphers-2.md](modern-ciphers-2.md#pbkdf2-pre-hash-bypass-for-long-passwords-backdoorctf-2016)。
- **MD5多碰撞（fastcol）:** `fastcol` 链接生成 2^k 个具有相同MD5的文件。Merkle-Damgard组合：碰撞通过附加后缀传播。参见 [modern-ciphers-2.md](modern-ciphers-2.md#md5-multi-collision-via-fastcol-backdoorctf-2016)。
- **自定义哈希状态反转:** 当迭代哈希泄露中间状态时，通过反转状态更新方程隔离每个块的哈希值，然后独立地逐字节块暴力破解。参见 [modern-ciphers-3.md](modern-ciphers-3.md#custom-hash-state-reversal-via-known-intermediates-backdoorctf-2016)。
- **CRC32暴力破解（小有效载荷）:** ZIP CRC32头部未加密；通过检查所有可打印字符串与存储的CRC32来暴力破解小文件内容（≤ 6字节）。参见 [modern-ciphers-3.md](modern-ciphers-3.md#crc32-brute-force-for-small-payloads-backdoorctf-2016)。
- **自定义MAC伪造通过XOR块取消:** 当MAC密钥流周期性重复时，制作三个查询，填充块通过XOR取消，伪造任何目标命令的MAC。参见 [modern-ciphers-3.md](modern-ciphers-3.md#custom-mac-forgery-via-xor-block-cancellation-with-key-rotation-plaidctf-2018)。
- **HMAC密钥恢复（XOR+加法算术）:** 使用 `sha256((key XOR msg) + msg)` 的有缺陷的HMAC泄露密钥位：`msg=0` 给出 `sha256(key)`，`msg=2^i` 匹配当且仅当密钥位 `i` 被设置。参见 [modern-ciphers-3.md](modern-ciphers-3.md#bit-by-bit-hmac-key-recovery-via-xor-plus-addition-arithmetic-midnight-sun-ctf-2018)。
- **AES-CBC密文伪造（错误消息oracle）:** 服务器在错误消息中泄露解密字节；发送零块以学习中间状态，与所需明文XOR以逐块伪造密文。参见 [modern-ciphers.md](modern-ciphers.md#aes-cbc-ciphertext-forging-via-error-message-decryption-oracle-nuit-du-hack-ctf-2018)。

参见 [modern-ciphers.md](modern-ciphers.md) 和 [modern-ciphers-2.md](modern-ciphers-2.md) 以获取完整代码示例。

## RSA攻击

- **小e与小消息:** 取e次方根
- **共同模数:** 扩展GCD攻击
- **Wiener攻击:** 小d
- **Fermat分解:** p和q相邻
- **Pollard的p-1:** 平滑p-1
- **Hastad广播:** 相同消息，多个e=3加密
- **连续素数:** q = next_prime(p)；找到第一个小于sqrt(N)的素数
- **多素数:** 使用sympy分解N；从所有因子计算phi
- **限制位素数:** 从LSB逐位分解，使用模数剪枝
- **Coppersmith结构化素数:** 部分已知素数；通过coppersmith库（Sage后备）使用small_roots（Sage后备在详细说明中）
- **Manger oracle（简化）:** 第一阶段加倍 + 第二阶段二进制搜索；~128次查询用于64位密钥
- **Manger在RSA-OAEP（计时）:** Python `or` 短路跳过昂贵的PBKDF2，当Y != 0时创建快/慢计时oracle。完整3步攻击（~1024次迭代用于1024位RSA）。使用已知快/慢样本校准计时边界。
- **多项式哈希（平凡根）:** `g(0) = 0` 对于多项式哈希；制作后缀以 `msg = 0 (mod P)`，签名 = 0
- **GF(2)[x]中的多项式CRT:** 收集~20个余数 `r = flag mod f`，过滤互质，CRT组合
- **复合模数上的仿射:** 在每个素数因子域中CRT；每个素数使用高斯-约当
- **RSA p=q验证绕过:** 设置 `p=q` 以使服务器计算错误的 `phi=(p-1)^2` 而不是 `p*(p-1)`；测试解密失败，泄露密文
- **RSA立方根CRT（gcd(e,phi)>1）:** 当所有素数 ≡ 1 mod e时，通过 `nthroot_mod` 每个素数计算e次方根，枚举CRT组合（3^k可行对于小k）
- **从phi(n)倍数分解:** 任何 `phi(n)` 的倍数（例如，`e*d-1`）通过Miller-Rabin平方根技术启用分解；每次尝试成功概率 ≥ 1/2
- **通过基数表示生成弱密钥:** 素数 `p = kp*B + tp` 具有小的kp创建n中的混合基数结构；暴力破解kp*kq（2^24）以分解
- **RSA与gcd(e,phi)>1（指数减少）:** 减少 `e' = e/g`，计算 `d' = e'^(-1) mod phi`，部分解密到 `m^g`，然后对整数取g次方根
- **RSA部分密钥恢复（dp/dq/qinv）:** 从部分PEM泄漏的CRT指数允许O(e)素数恢复：迭代k，检查 `(dp*e-1)/k+1` 是否为素数。参见 [rsa-attacks-2.md](rsa-attacks-2.md#rsa-partial-key-recovery-from-dp-dq-qinv-0ctf-2016)。
- **RSA-CRT故障攻击:** 单个故障CRT签名通过 `gcd(s^e - m, n)` 泄露因子（Bellcore攻击）。参见 [rsa-attacks-2.md](rsa-attacks-2.md#rsa-crt-fault-attack--bit-flip-recovery-csaw-ctf-2016)。
- **RSA同态解密绕过:** 乘法同态允许通过查询 `c * r^e mod n` 的oracle来解密 `c`，然后除以 `r`。参见 [rsa-attacks-2.md](rsa-attacks-2.md#rsa-homomorphic-decryption-oracle-bypass-ectf-2016)。
- **RSA小素数CRT分解:** 当 `n` 有许多小素数因子时，使用试除法分解，解决 `m mod p_i` 每个素数，CRT组合。参见 [rsa-attacks-2.md](rsa-attacks-2.md#rsa-with-small-prime-factors-and-crt-decomposition-hack-the-vote-2016)。
- **Hastad广播与线性填充（Coppersmith）:** 当每个e个接收者在对称变换 `a_i*m+b_i` 之前加密时，CRT + Coppersmith small_roots恢复 `m`。参见 [rsa-attacks.md](rsa-attacks.md#hastad-broadcast-attack-with-linear-padding----coppersmith-plaidctf-2017)。
- **RSA Montgomery减少计时攻击:** 泄露Montgomery乘法中的额外减法计数揭示MSB到LSB的私钥位通过统计相关性。参见 [rsa-attacks-2.md](rsa-attacks-2.md#rsa-timing-attack-on-montgomery-reduction-def-con-2017)。
- **Bleichenbacher低指数签名伪造:** 当e=3时，通过计算具有正确填充前缀的值的立方根来伪造PKCS#1 v1.5签名；尾随垃圾吸收余数。参见 [rsa-attacks-2.md](rsa-attacks-2.md#bleichenbacher-low-exponent-rsa-signature-forgery-google-ctf-2017)。
- **Franklin-Reiter相关消息攻击（e=3）:** 两个密文 `m+pad1` 和 `m+pad2` 具有已知填充差异；多项式GCD在 `Zmod(n)` 中直接恢复 `m`。参见 [rsa-attacks.md](rsa-attacks.md#franklin-reiter-related-message-attack-on-rsa-e3-n1ctf-2018)。
- **RSA签名绕过（e=1，定制模数）:** 验证器接受用户提供的 `(n, e)`；设置 `e=1` 和 `n = sig - PKCS1_pad(msg)` 以使 `pow(sig, 1, n)` 等于预期的填充哈希。参见 [rsa-attacks-2.md](rsa-attacks-2.md#rsa-signature-bypass-with-e1-and-crafted-modulus-backdoorctf-2018)。
- **Coppersmith在线性相关素数上:** 当 `q ~ k*p` 对于已知 `k` 时，近似 `q ~ sqrt(k*n)` 并使用Coppersmith `small_roots` 在误差项上。将Fermat分解推广到非连续素数。参见 [rsa-attacks.md](rsa-attacks.md#coppersmith-attack-on-linearly-related-rsa-primes-asis-ctf-2018)。

参见 [rsa-attacks.md](rsa-attacks.md) 和 [advanced-math.md](advanced-math.md) 以获取完整代码示例。

## 椭圆曲线攻击

- **小子群:** 检查曲线阶的小因子；Pohlig-Hellman + CRT
- **无效曲线:** 如果验证缺失，发送较弱曲线上的点
- **奇异曲线:** 判别式 = 0；DLP映射到加法/乘法群
- **Smart攻击:** 异常曲线（阶 = p）；p-adic提升解决O(1) DLP
- **Baby-step giant-step (BSGS):** 一般DLP在O(sqrt(n))时间/空间。与Pohlig-Hellman结合用于平滑阶组（`p-1` 或曲线阶的所有因子都是小的）。sympy/fpylll BSGS+Pohlig-Hellman（Sage替代折叠）。参见 [advanced-math.md](advanced-math.md#baby-step-giant-step-for-general-dlp)。
- **故障注入:** 比较正确与故障输出；逐位恢复密钥
- **时钟群（x^2+y^2=1）:** 阶 = p+1（不是p-1！）；当p+1是平滑时使用Pohlig-Hellman
- **同构:** 通过模态多项式进行图遍历；通过LCA进行路径查找
- **ECDSA nonce重用:** 两个签名中相同的 `r` 泄露nonce `k` 和私钥 `d` 通过模算术。检查重复的 `r` 值
- **Braid群DH:** Alexander多项式在braid连接下是乘法的——Eve从公钥计算共享密钥。参见 [exotic-crypto.md](exotic-crypto.md#braid-group-dh--alexander-polynomial-multiplicativity-dicectf-2026)
- **Ed25519扭转侧信道:** 系数h=8泄露密钥标量位，当密钥派生使用 `key = master * uid mod l` 时；查询2的幂，检查y坐标一致性
- **热带半环残差:** 热带（min-plus）DH被破坏——残差 `b* = max(Mb[i] - M[i][j])` 直接从公共矩阵恢复共享密钥
- **FPE Feistel暴力破解:** 格式保留加密具有16位轮密钥是暴力破解的；剩余的仿射GF(2)混合层通过高斯消元解决。参见 [exotic-crypto.md](exotic-crypto.md#format-preserving-encryption-feistel-brute-force-bsidessf-2026)
- **二十面体对称密码器:** 十二面体面置换形成120阶群；通过API探测构建所有置换的查找表，匹配可见面模式。参见 [exotic-crypto.md](exotic-crypto.md#icosahedral-symmetry-group-cipher-bsidessf-2026)
- **Goldwasser-Micali复制oracle:** GM每个密文加密一位；将单个密文值N次重放作为N位密钥，强制所有零或全一密钥，通过哈希oracle可区分。128次查询恢复完整AES密钥。参见 [exotic-crypto.md](exotic-crypto.md#goldwasser-micali-ciphertext-replication-oracle-bsidessf-2026)
- **DSA nonce重用:** 两个DSA签名中相同的 `r` 通过与ECDSA nonce重用相同的公式泄露私钥。参见 [ecc-attacks.md](ecc-attacks.md#dsa-nonce-reuse-for-private-key-recovery-volgactf-2016)。
- **DSA有限k暴力破解:** 当nonce `k` 较小（例如，20位）时，暴力破解所有 `k` 值并检查哪个产生已知的 `r`。参见 [ecc-attacks.md](ecc-attacks.md#dsa-limited-k-value-brute-force-asis-ctf-finals-2016)。
- **ECC共享素数GCD:** 多个ECC曲线在其模数中共享一个素数因子；`gcd(n1, n2)` 揭示共享素数。参见 [ecc-attacks.md](ecc-attacks.md#ecc-shared-prime-factor-via-gcd-asis-ctf-finals-2016)。
- **DSA通过MD5碰撞在k生成中恢复密钥:** 当nonce `k` 派生自 `MD5(prefix+counter)` 时，使用 `fastcoll` 产生MD5前缀碰撞强制nonce重用，然后标准私钥恢复。参见 [ecc-attacks.md](ecc-attacks.md#dsa-key-recovery-via-md5-collision-on-k-generation-confidence-ctf-2017)。
- **BB-84 QKD MITM:** 无认证经典通道的模拟BB-84允许完整MITM——独立与双方协商密钥，强制一方为常量值。参见 [exotic-crypto-2.md](exotic-crypto-2.md#bb-84-quantum-key-distribution-mitm-attack-plaidctf-2017]。

参见 [ecc-attacks.md](ecc-attacks.md)、[advanced-math.md](advanced-math.md) 和 [exotic-crypto.md](exotic-crypto.md) 获取完整的代码示例。

## Diffie-Hellman 攻击

- **平凡的 g：** 首先尝试 `g = 0, 1, p-1` 和对等值 `A = 0, 1, p-1, p`；未验证的范围检查会泄露已知常量密钥。参见 [dh-attacks.md](dh-attacks.md#trivial-generator-values-g--0-1-p-1)。
- **Pohlig-Hellman：** 因式分解 `p-1`；平滑意味着通过 BSGS 每个子群进行完整 DLP + CRT。参见 [dh-attacks.md](dh-attacks.md#pohlig-hellman-when-p-1-is-smooth)。
- **小子群限制 / Lim-Lee：** 静态密钥 + 具有较小因子的复合 `p-1`；发送阶为 `r` 的元素，通过 MAC/解密预言机暴力破解 `b mod r`，跨 `r_i` 进行 CRT。参见 [dh-attacks.md](dh-attacks.md#small-subgroup-confinement--lim-lee-static-key-recovery-via-crt)。
- **X25519 低阶：** 因子 8 + 夹紧意味着小阶 `u` 强制所有为零的 `K`；`u = 0, 1` 总是探测。缺少全零检查 = 1-2 查询破解。参见 [ecc-attacks.md](ecc-attacks.md#x25519-low-order-points--all-zero-check-rfc-7748)。

## 格子 / LWE 攻击

- **快速筛选：** 如果挑战给出模线性方程，并承诺隐藏数量较小、稀疏、有偏差或仅部分泄露，首先将其视为格子候选。参见 [lattice-and-lwe.md](lattice-and-lwe.md#quick-triage-is-this-a-lattice-problem)。
- **LLL / BKZ / Babai：** fpylll LLL.reduction / BKZ.reduction / GSO.Mat.babai / CVP.closest_vector (Sage Matrix(ZZ).LLL() / M.BKZ 在细节中的回退) — 从 LLL 开始，当 LLL 几乎有效时转到 BKZ，使用 Babai 进行近似 CVP。参见 [lattice-and-lwe.md](lattice-and-lwe.md#core-tools-lll-bkz-babai-cvp-svp-asis-ctf-finals-2015-ctfzone-2017)。
- **从部分随机数泄露中获取 HNP：** 部分或有偏差的 ECDSA/Schnorr 随机数通常简化为隐藏数问题格子；归一化方程，隔离有界误差，简化，如有必要则暴力破解最后几位。参见 [lattice-and-lwe.md](lattice-and-lwe.md#hidden-number-problem-hnp-partial-nonce--biased-nonce-nullcon-hackim-2020-ledger-donjon-ctf-2020)。
- **截断 LCG 状态恢复：** 高位或低位泄露来自仿射递归通常是伪装的 HNP；将每个状态写为 `observed * 2^t + hidden` 并求解小的隐藏修正。参见 [lattice-and-lwe.md](lattice-and-lwe.md#lcg-and-truncated-output-as-a-lattice-problem-x-mas-ctf-2018-fwordctf-2020)。
- **通过 CVP (Babai) 的 LWE：** 从 `[q*I | 0; A^T | I]` 构造格子，使用 fpylll GSO.Mat.babai 或 CVP.closest_vector 找到最近向量，投影到三元 {-1,0,1}。注意服务器描述和实际编码之间的字节序不匹配。
- **环 LWE / 模 LWE 识别：** 多项式或负循环结构看起来很可怕，但许多 CTF 中通过系数很小、有错误表示或足够泄露将其扁平化为普通 LWE。参见 [lattice-and-lwe.md](lattice-and-lwe.md#ring-lwe--module-lwe-recognition-notes-plaidctf-2016-dicectf-2022)。
- **正交格子：** 隐藏子集或隐藏子空间问题可能需要您首先恢复正交格子，然后从其补集中重建实际的二进制或短基。参见 [lattice-and-lwe.md](lattice-and-lwe.md#orthogonal-lattices-hssp--ahssp-style-recovery-zer0pts-ctf-2022)。
- **LLL 用于近似 GCD：** fpylll LLL.reduction (Sage Matrix(ZZ).LLL() 在细节中的回退) — 格子中的短向量揭示隐藏因子
- **子集和 / 背包：** 二进制背包和低密度子集和实例仍然是经典的格子领域；构建标准基，并寻找具有零最终坐标的简化行。参见 [lattice-and-lwe.md](lattice-and-lwe.md#subset-sum--knapsack-via-lattice-reduction-hitcon-ctf-2017-backdoorctf-2023)。
- **多层挑战：** 几何 → 子空间恢复 → LWE → AES-GCM 解密链

参见 [advanced-math.md](advanced-math.md) 获取已处理的 LWE 解码代码和 [lattice-and-lwe.md](lattice-and-lwe.md) 获取攻击选择、嵌入和失败模式筛选。

## ZKP & 约束求解

- **ZKP 欺骗：** 对于不可能的问题（3-着色 K4），找到哈希碰撞或预测 PRNG 盐
- **图 3-着色：** `nx.coloring.greedy_color(G, strategy='saturation_largest_first')`
- **Z3 求解器：** BitVec 用于位级，Int 用于任意精度；BPF/SECCOMP 过滤求解
- **混淆电路（免费 XOR）：** XOR 三个真值表条目以恢复全局 delta
- **双字母替换：** OR-Tools CP-SAT 使用自动机约束以已知明文结构
- **三字母分解：** 位置模 n 形成独立的单字母密码
- **Shamir SSS（确定性系数）：** 一个份额 + 种子 RNG = 多项式方程在秘密中
- **竞争条件（TOCTOU）：** 同步并发请求绕过 `counter < N` 检查
- **Groth16 破坏性设置（delta==gamma）：** 检验：A=alpha, B=beta, C=-vk_x。始终检查验证器常量
- **Groth16 证明重放：** 无约束 nullifier + 无跟踪 = 从设置交易无限重放
- **DV-SNARG 欺骗：** 使用验证器预言机访问，从无约束对中学习秘密 v 值，通过 CRS 条目取消欺骗
- **Shamir SSS 重复多项式系数：** 当相同的随机系数用于每个秘密字节时，减去份额会取消所有随机性，只留下明文差异。参见 [zkp-and-advanced.md](zkp-and-advanced.md#shamir-secret-sharing-with-reused-polynomial-coefficients-polictf-2017)。

参见 [zkp-and-advanced.md](zkp-and-advanced.md) 获取完整的代码示例和求解器模式。

## 现代密码攻击（附加）

- **模复合的仿射：** `c = A*x+b (mod M)`，M 是复合的（例如，65=5*13）。通过单热向量进行选择明文恢复，每个素数因子进行 CRT。参见 [modern-ciphers.md](modern-ciphers.md#affine-cipher-over-composite-modulus-nullcon-2026)。
- **自定义线性 MAC 欺骗：** 基于异或的签名在线性于秘密块。从 ~5 个已知对中恢复秘密，为目标欺骗。参见 [modern-ciphers.md](modern-ciphers.md#custom-linear-mac-forgery-nullcon-2026)。
- **Manger 预言机（RSA 阈值）：** RSA 乘法 + 二进制搜索 `m*s < 2^128`。~128 查询以恢复 AES 密钥。
- **通过字节逐字节零化预言机恢复 AES 密钥：** 密钥槽索引中的整数溢出允许选择性字节零化；逐字节暴力破解（每个字节 256，总共 4096）。参见 [modern-ciphers.md](modern-ciphers.md#aes-key-recovery-via-byte-by-byte-zeroing-oracle-confidence-ctf-2017)。

## 通过 GF(2) 线性代数进行自省 CRC

自引用 CRC：找到 ASCII 字符串，其 CRC 等于自身。CRC 在 GF(2) 上是线性的，因此约束变为可解的线性系统。自由变量选择用于可打印 ASCII 范围。参见 [advanced-math.md](advanced-math.md#introspective-crc-via-gf2-linear-algebra-google-ctf-2017)。

## CBC 填充预言机攻击

服务器揭示有效/无效填充 → 无需密钥解密任何 CBC 密文。每个 16 字节块约 4096 查询。使用 PadBuster 或 `padding-oracle` Python 库。参见 [modern-ciphers.md](modern-ciphers.md#cbc-padding-oracle-attack)。

## Bleichenbacher RSA 填充预言机（ROBOT）

RSA PKCS#1 v1.5 填充验证预言机 → 自适应选择密文明文恢复。~10K 查询 RSA-2048。通过计时影响 TLS 实现。参见 [modern-ciphers.md](modern-ciphers.md#bleichenbacher--pkcs1-v15-rsa-padding-oracle)。

## 生日攻击 / 中间相遇

n 位哈希碰撞在 ~2^(n/2) 次尝试中。中间相遇打破双重加密为 O(2^k) 而不是 O(2^(2k))。参见 [modern-ciphers.md](modern-ciphers.md#birthday-attack--meet-in-the-middle)。

- **海绵哈希中间相遇碰撞：** 当海绵速率 < 状态大小，未控制的状态字节启用中间相遇 — 预计算以未控制字节为键的前向加密，向后搜索匹配。将 2^48 减少到 2^24。参见 [modern-ciphers-3.md](modern-ciphers-3.md#sponge-hash-collision-via-meet-in-the-middle-on-partial-state-bkp-2017)。

## CRC32 碰撞签名欺骗（iCTF 2013）

CRC32 是线性的 — 追加 4 个选择的字节以强制任何目标 CRC32，无需秘密伪造 `CRC32(msg || secret)` 签名。参见 [modern-ciphers.md](modern-ciphers.md#crc32-collision-based-signature-forgery-ictf-2013)。

## Blum-Goldwasser 位扩展预言机（PlaidCTF 2013）

每个预言机查询扩展密文一位以通过奇偶校验泄露明文。操纵 BBS 平方序列以产生有效的扩展密文。参见 [modern-ciphers-2.md](modern-ciphers-2.md#blum-goldwasser-bit-extension-oracle-plaidctf-2013)。

## 哈希长度扩展攻击

利用 Merkle-Damgard 哈希 (`hash(SECRET || user_data)`) — 追加任意数据并计算有效哈希而无需知道秘密。使用 `hashpump` 或 `hashpumpy`。参见 [modern-ciphers-2.md](modern-ciphers-2.md#hash-length-extension-attack-plaidctf-2014)。

## 压缩预言机（CRIME-风格）

加密前压缩泄露明文通过密文长度变化。发送选择明文；匹配 n-gram 压缩更短。与 CRIME/BREACH 同类。参见 [modern-ciphers-2.md](modern-ciphers-2.md#compression-oracle--crime-style-attack-bctf-2015)。

## RC4 第二字节偏差

RC4 的第二个输出字节偏向 `0x00`（概率 1/128 vs 1/256）。使用 ~2048 个样本区分 RC4 和随机。参见 [stream-ciphers.md](stream-ciphers.md#rc4-second-byte-bias-distinguisher-hackover-ctf-2015)。

## RSA 乘法同态签名欺骗

未填充 RSA：`S(a) * S(b) mod n = S(a*b) mod n`。如果预言机黑名单目标消息，则签署其因子并乘以。参见 [rsa-attacks-2.md](rsa-attacks-2.md#rsa-signature-forgery-via-multiplicative-homomorphism-mma-ctf-2015)。

## 常见模式

- **RSA 基础：** `phi = (p-1)*(q-1)`，`d = inverse(e, phi)`，`m = pow(c, d, n)`。参见 [rsa-attacks.md](rsa-attacks.md) 获取完整示例。
- **XOR：** `from pwn import xor; xor(ct, key)`。参见 [classic-ciphers.md](classic-ciphers.md) 获取 XOR 变体。

## 通过 ctypes 预测 C srand/rand（L3akCTF 2024, MireaCTF）

**模式：** 二进制使用 `srand(time(NULL))` + `rand()` 为密钥/XOR 掩码。Python 的 `random` 模块使用不同的 PRNG。使用 `ctypes.CDLL('./libc.so.6')` 直接调用 C 的 `srand(int(time()))` 和 `rand()`，重现精确序列。参见 [prng.md](prng.md#c-srandrand-synchronization-via-python-ctypes) 获取 XOR 解密示例和计时技巧。

## V8 XorShift128+（Math.random）状态恢复

**模式：** V8 JavaScript 引擎使用 xs128p PRNG 为 `Math.random()`。给定 5-10 个连续的 `Math.floor(CONST * Math.random())` 输出，使用 Z3 QF_BV 求解器恢复内部状态（state0, state1）并预测未来值。值必须反转（LIFO 缓存）。工具：`d0nutptr/v8_rand_buster`。参见 [prng.md](prng.md#v8-xorshift128-state-recovery-mathrandom-prediction)。

## 从浮点输出恢复 MT 状态（PHD CTF 赛前赛 2012）

**模式：** 服务器暴露 `random.random()` 浮点数。标准未扰动需要 624 × 32 位整数，但浮点数每个只产生约 8 个可用位。预计算的 GF(2) 魔法矩阵（`not_random` 库）从 3360+ 浮点观察值中恢复完整的 MT 状态。用于预测密码重置令牌、会话 ID 或从 `random.random()` 派生的 CSRF 令牌。参见 [prng.md](prng.md#mt-state-recovery-from-randomrandom-floats-via-gf2-matrix-phd-ctf-quals-2012)。

## 混沌 PRNG（逻辑斯蒂映射）

- **逻辑斯蒂映射：** `x = r * x * (1 - x)`，`r ≈ 3.99-4.0`；种子通过暴力破解高精度小数恢复
- **密钥流：** 每次迭代 `struct.pack("<f", x)`；与密文 XOR

参见 [prng.md](prng.md#logistic-map--chaotic-prng-seed-recovery-bypass-ctf-2025) 获取完整代码。

## SPN S-box 交集攻击

分而治之 SPN 密钥恢复：独立攻击每个 S-box 位置，跨多个明文-密文对相交有效密钥候选。将指数级密钥空间减少为独立的子密钥搜索。参见 [modern-ciphers-3.md](modern-ciphers-3.md#spn-cipher-partial-key-recovery-via-s-box-intersection-sharifctf-7-2016)。

## 有用工具

- **Python：** `pip install pycryptodome z3-solver sympy gmpy2`
- **SageMath（可选回退）：** `sage -python script.py` — 仅用于折叠的 Sage 替代方案
- **RsaCtfTool：** `python RsaCtfTool.py -n <n> -e <e> --uncipher <c>` — 自动化 RSA 攻击套件（尝试 Wiener、Hastad、Fermat、Pollard 和许多其他）
- **quipqiup.com：** 自动化替换密码求解器（频率 + 单词模式分析）
