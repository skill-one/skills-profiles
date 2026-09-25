# 技能：RSA 攻击技巧 — 专家密码分析手册

> **AI 加载指令**：用于 CTF 和授权安全评估的专家级 RSA 攻击技巧。涵盖分解攻击、小指数利用、基于格的方法（Wiener/Boneh-Durfee/Coppersmith）、广播攻击、共同模数、填充预言机、故障攻击。基础模型通常建议的攻击方式与给定参数不匹配，或未能根据已知信息选择正确的攻击方式。

## 0. 相关路由

- [lattice-crypto-attacks](../lattice-crypto-attacks/SKILL.md) 用于 Coppersmith/Boneh-Durfee 深入格理论
- [hash-attack-techniques](../hash-attack-techniques/SKILL.md) 当 RSA 签名伪造涉及哈希弱点时
- [symmetric-cipher-attacks](../symmetric-cipher-attacks/SKILL.md) 当 RSA 保护对称密钥（混合加密）时

### 高级参考

当您需要时，也加载 [RSA_ATTACK_CATALOG.md](./RSA_ATTACK_CATALOG.md)：
- 每种攻击的 SageMath/Python 详细实现
- 逐步数学推导
- 每种攻击的边缘情况和失败条件

### 快速攻击选择

| 给定 / 可观察 | 攻击 | 工具 |
|---|---|---|
| 小 n (< 512 位) | 直接分解 | factordb, yafu, msieve |
| e = 3, 小消息 | 立方根 | gmpy2.iroot |
| 多个 (n, c) 相同小 e | Hastad 广播 | CRT + iroot |
| 非常大的 e 或非常小的 d | Wiener / Boneh-Durfee | SageMath, RsaCtfTool |
| 部分已知 p | Coppersmith 小根 | SageMath |
| 相同 n，不同 e | 共同模数 | 扩展 GCD |
| 多个 n 值 | 批量 GCD（共享因子） | Python/SageMath |
| 填充错误预言机 | Bleichenbacher | 自定义脚本 |
| LSB 奇偶预言机 | LSB 预言机攻击 | 自定义脚本 |
| CRT 计算中的故障 | RSA-CRT 故障 | 单个故障签名 |

---

## 1. 分解攻击

### 1.1 直接分解（小 n）

```python
from sympy import factorint

n = 0x...  # 小模数
factors = factorint(n)
p, q = list(factors.keys())
```

**当**：n < ~512 位，或已知在 factordb 中。

### 1.2 Fermat 分解

当 p 和 q 接近时：|p - q| 很小。

```python
from gmpy2 import isqrt, is_square

def fermat_factor(n):
    a = isqrt(n) + 1
    while True:
        b2 = a * a - n
        if is_square(b2):
            b = isqrt(b2)
            return (a + b, a - b)
        a += 1
```

### 1.3 Pollard 的 p-1

当 p-1 只有小的素数因子（B-smooth）时。

```python
from gmpy2 import gcd

def pollard_p1(n, B=2**20):
    a = 2
    for j in range(2, B):
        a = pow(a, j, n)
    d = gcd(a - 1, n)
    if 1 < d < n:
        return d
    return None
```

### 1.4 批量 GCD（多个 n 共享因子）

```python
from math import gcd
from functools import reduce

def batch_gcd(moduli):
    """在多个 RSA 模数中查找共享因子。"""
    product = reduce(lambda a, b: a * b, moduli)
    results = {}
    for i, n in enumerate(moduli):
        remainder = product // n
        g = gcd(n, remainder)
        if g != 1 and g != n:
            results[i] = (g, n // g)
    return results
```

---

## 2. 小指数攻击

### 2.1 立方根攻击（e = 3，小 m）

如果 m^e < n（没有模运算），直接取 e 次方根。

```python
from gmpy2 import iroot

c = 0x...  # 密文
e = 3
m, exact = iroot(c, e)
if exact:
    print(f"明文: {bytes.fromhex(hex(m)[2:])}")
```

### 2.2 Hastad 广播攻击

相同消息用相同小 e 在不同模数（n₁, n₂, ..., nₑ）下加密。

```python
from sympy.ntheory.modular import crt
from gmpy2 import iroot

# e = 3，三个不同 n 下的密文
n_list = [n1, n2, n3]
c_list = [c1, c2, c3]

# CRT：找到 x，使得 x ≡ ci (mod ni) 对所有 i
r, M = crt(n_list, c_list)
m, exact = iroot(r, 3)
assert exact
```

### 2.3 相关消息攻击（Franklin-Reiter）

两个消息通过已知线性函数相关：m₂ = a·m₁ + b。相同 n 和 e。

```python
# SageMath
def franklin_reiter(n, e, c1, c2, a, b):
    R.<x> = PolynomialRing(Zmod(n))
    f1 = x^e - c1
    f2 = (a*x + b)^e - c2
    return Integer(n - gcd(f1, f2).coefficients()[0])
```

---

## 3. 大 e / 小 d 攻击

### 3.1 Wiener 攻击（连分数）

当 d < n^(1/4) / 3 时，e/n 的连分数展开揭示 d。

```python
def wiener_attack(e, n):
    """通过连分数恢复 d，当 d 较小时。"""
    cf = continued_fraction(e, n)
    convergents = get_convergents(cf)

    for k, d in convergents:
        if k == 0:
            continue
        phi_candidate = (e * d - 1) // k
        # φ(n) = n - p - q + 1 → p + q = n - φ + 1
        s = n - phi_candidate + 1
        # p, q 是 x^2 - s*x + n = 0 的根
        discriminant = s * s - 4 * n
        if discriminant >= 0:
            from gmpy2 import isqrt, is_square
            if is_square(discriminant):
                return d
    return None

def continued_fraction(a, b):
    cf = []
    while b:
        cf.append(a // b)
        a, b = b, a % b
    return cf

def get_convergents(cf):
    convergents = []
    h_prev, h_curr = 0, 1
    k_prev, k_curr = 1, 0
    for a in cf:
        h_prev, h_curr = h_curr, a * h_curr + h_prev
        k_prev, k_curr = k_curr, a * k_curr + k_prev
        convergents.append((h_curr, k_curr))
    return convergents
```

### 3.2 Boneh-Durfee 攻击（基于格）

扩展 Wiener：当 d < n^0.292 时。使用格约简（LLL/BKZ）。

**使用 SageMath 实现** — 参考 [lattice-crypto-attacks](../lattice-crypto-attacks/SKILL.md) 了解理论。

---

## 4. Coppersmith 方法

### 4.1 标准化消息

已知部分明文，未知部分较小。

```python
# SageMath
n = ...
e = 3
c = ...
known_prefix = b"flag{" + b"\x00" * 27  # 已知前缀，未知后缀
known_int = int.from_bytes(known_prefix, 'big')

R.<x> = PolynomialRing(Zmod(n))
f = (known_int + x)^e - c
roots = f.small_roots(X=2^(27*8), beta=1.0)
if roots:
    m = known_int + int(roots[0])
    print(bytes.fromhex(hex(m)[2:]))
```

### 4.2 部分密钥暴露

已知 p 的 MSB 或 LSB → 通过 Coppersmith 恢复完整 p。

```python
# SageMath — 已知 p 的 MSB
p_msb = ...  # 已知 p 的高位
R.<x> = PolynomialRing(Zmod(n))
f = p_msb + x
roots = f.small_roots(X=2^unknown_bits, beta=0.5)
if roots:
    p = p_msb + int(roots[0])
    q = n // p
```

---

## 5. 共同模数攻击

两个相同消息在相同 n 但不同 e₁, e₂ 下的密文，其中 gcd(e₁, e₂) = 1。

```python
from gmpy2 import gcd, invert

def common_modulus(n, e1, e2, c1, c2):
    """当相同消息用两个不同 e 在相同 n 下加密时恢复 m。"""
    assert gcd(e1, e2) == 1
    _, s1, s2 = extended_gcd(e1, e2)  # s1*e1 + s2*e2 = 1

    if s1 < 0:
        c1 = invert(c1, n)
        s1 = -s1
    if s2 < 0:
        c2 = invert(c2, n)
        s2 = -s2

    m = (pow(c1, s1, n) * pow(c2, s2, n)) % n
    return m

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    g, x, y = extended_gcd(b % a, a)
    return g, y - (b // a) * x, x
```

---

## 6. 预言机攻击

### 6.1 LSB 预言机（奇偶预言机）

预言机揭示解密后的消息是奇数还是偶数。

```python
from gmpy2 import mpz

def lsb_oracle_attack(n, e, c, oracle_func):
    """使用 LSB（奇偶）预言机解密。oracle_func(c) 返回 m%2。"""
    from fractions import Fraction
    lo, hi = Fraction(0), Fraction(n)

    for _ in range(n.bit_length()):
        c = (c * pow(2, e, n)) % n  # 将明文乘以 2
        if oracle_func(c) == 0:
            hi = (lo + hi) / 2
        else:
            lo = (lo + hi) / 2

    return int(hi)
```

### 6.2 Bleichenbacher（PKCS#1 v1.5 填充预言机）

给定填充有效性预言机（有效/无效 PKCS#1 v1.5），逐步缩小明文范围。

**复杂度**：平均每个字节 2^16 次预言机查询。

**目标**：TLS 实现返回不同错误以区分有效/无效填充。

### 6.3 Manger 攻击（PKCS#1 OAEP）

与 Bleichenbacher 类似，但用于 OAEP 填充。利用区分预言机，该预言机区分解填充后的第一个字节是否为 0x00。

---

## 7. RSA-CRT 故障攻击

如果 RSA-CRT 签名产生故障签名（一个 CRT 半部分故障）：

```python
def rsa_crt_fault(n, e, correct_sig, faulty_sig, msg):
    """从正确和故障的 CRT 签名中分解 n。"""
    from math import gcd
    diff = pow(correct_sig, e, n) - pow(faulty_sig, e, n)
    p = gcd(diff % n, n)
    if 1 < p < n:
        q = n // p
        return p, q
    return None

# 更简单：如果消息已知，只需要故障签名
def rsa_crt_fault_simple(n, e, faulty_sig, msg):
    p = gcd(pow(faulty_sig, e, n) - msg, n)
    if 1 < p < n:
        return p, n // p
    return None
```

---

## 8. 决策树

```
RSA 挑战 — 你有什么信息？
│
├─ 有 n 且它很小 (< 512 位)？
│  └─ 直接分解：factordb.com → yafu → msieve
│
├─ 有多个 n 值？
│  └─ 批量 GCD — 共享因子？
│     ├─ 是 → 分解所有共享因子的
│     └─ 否 → 分别分析每个 n
│
├─ 知道 e？
│  ├─ e = 3（或小）？
│  │  ├─ 单个密文，小消息 → 立方根
│  │  ├─ 多个密文，不同 n → Hastad 广播
│  │  ├─ 两个相关消息 → Franklin-Reiter
│  │  └─ 部分明文已知 → Coppersmith
│  │
│  ├─ e 非常大？
│  │  └─ d 可能很小 → Wiener → Boneh-Durfee
│  │
│  └─ 相同 n，两个不同 e 值？
│     └─ 共同模数攻击（Bézout 系数）
│
├─ 知道部分分解信息？
│  ├─ 知道 p 的一些位 → Coppersmith 部分密钥
│  ├─ p-1 是 B-smooth → Pollard p-1
│  └─ p ≈ q（接近素数）→ Fermat 分解
│
├─ 有预言机？
│  ├─ 奇偶预言机（LSB）→ LSB 预言机攻击
│  ├─ 填充有效性预言机（PKCS#1 v1.5）→ Bleichenbacher
│  └─ OAEP 预言机 → Manger 攻击
│
├─ 有故障签名？
│  └─ RSA-CRT 故障 → 从故障签名中分解 n
│
├─ 知道 e·d 关系？
│  └─ e·d ≡ 1 mod φ(n) → 从 (e,d,n) 分解 n
│
└─ 以上都不适用？
   ├─ 检查 factordb 查看是否已知分解
   ├─ 尝试 Pollard rho 处理中等大小 n
   ├─ 查找实现缺陷（密钥生成弱 PRNG）
   └─ 如果有物理访问，考虑侧信道
```

---

## 9. 工具

| 工具 | 目的 | 使用 |
|---|---|---|
| **RsaCtfTool** | 自动化 RSA 攻击套件 | `python3 RsaCtfTool.py --publickey pub.pem --uncipherfile flag.enc` |
| **SageMath** | 数学计算 | Coppersmith、格攻击、多项式运算 |
| **factordb.com** | 在线分解数据库 | 检查 n 是否已被分解 |
| **yafu** | 快速分解（SIQS/GNFS） | `yafu "factor(n)"` |
| **msieve** | GNFS 分解 | 大 n 分解 |
| **gmpy2** | 快速 Python 整数库 | `iroot`, `invert`, `gcd` |
| **pycryptodome** | RSA 基本操作 | 从因子构建密钥 |

### RsaCtfTool 快速命令

```bash
# 从公钥
python3 RsaCtfTool.py --publickey pub.pem -n --private

# 从参数
python3 RsaCtfTool.py -n $N -e $E --uncipher $C

# 尝试所有攻击
python3 RsaCtfTool.py --publickey pub.pem --uncipherfile flag.enc --attack all
```

### 分解后解密

```python
from Crypto.PublicKey import RSA
from gmpy2 import invert

p, q = ...  # 已分解
n = p * q
e = 65537
phi = (p - 1) * (q - 1)
d = int(invert(e, phi))

c = ...  # 密文作为整数
m = pow(c, d, n)
plaintext = m.to_bytes((m.bit_length() + 7) // 8, 'big')
print(plaintext)
```
