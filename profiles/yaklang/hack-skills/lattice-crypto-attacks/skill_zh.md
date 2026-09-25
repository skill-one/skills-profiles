# 技能：基于格的密码分析——专家攻击手册

> **AI 加载指令**：CTF 和密码分析中的专家级格技术。涵盖 LLL/BKZ 简化、Coppersmith 方法（单变量和多变量）、DSA/ECDSA 随机数恢复的隐藏数问题、背包攻击和 NTRU 分析。基础模型通常无法构建正确的攻击格（维度错误、缺少缩放因子）或错误应用 Coppersmith 界。

## 0. 相关路由

- [rsa-attack-techniques](../rsa-attack-techniques/SKILL.md) 用于使用格方法的 RSA 特定攻击（Coppersmith、Boneh-Durfee）
- [symmetric-cipher-attacks](../symmetric-cipher-attacks/SKILL.md) 用于通过格恢复 LCG 状态
- [classical-cipher-analysis](../classical-cipher-analysis/SKILL.md) 当格方法适用于古典密码分析时

### 快速应用指南

| 问题类型 | 格技术 | 关键参数 |
|---|---|---|
| RSA 小根 | Coppersmith (在多项式格上应用 LLL) | 根界 X < N^(1/e) |
| RSA 小 d | Boneh-Durfee (多变量 Coppersmith) | d < N^0.292 |
| DSA/ECDSA 随机数偏差 | 隐藏数问题 → CVP | 已知偏差位 |
| 背包密码 | 低密度格攻击 | 密度 < 0.9408 |
| LCG 截断输出 | 在递归格上进行 CVP | 每个输出未知位数 |
| 子集和 | 在背包格上进行 LLL 简化 | 元素大小与数量 |
| NTRU 密钥恢复 | 在 NTRU 格上进行格简化 | 维度和密钥大小 |

---

## 1. 格基础

### 1.1 定义

一个 **格** L 是所有基向量的整数线性组合的集合：

```
L = { a₁·b₁ + a₂·b₂ + ... + aₙ·bₙ | aᵢ ∈ ℤ }
```

其中 b₁, ..., bₙ 是 ℝᵐ 中的线性无关向量。

**关键问题**：
- **SVP** (最短向量问题)：在 L 中找到最短的非零向量
- **CVP** (最近向量问题)：给定目标 t，找到 L 中最接近 t 的 v
- **SVP 在一般情况下是 NP-hard**，但 LLL 可以在多项式时间内找到一个近似短向量

### 1.2 格质量指标

```
行列式：det(L) = |det(B)| 其中 B 是基矩阵
高斯启发式：最短向量 ≈ √(n/(2πe)) · det(L)^(1/n)
```

---

## 2. LLL 算法

### 2.1 LLL 做什么

对一个格基 B 进行处理，生成一个 **简化基** B'，其中：
- 向量几乎正交
- 第一个向量近似短（SVP 的 2^((n-1)/2) 因子内）
- 运行在多项式时间内：O(n^5 · d · log³ B) 其中 d = 维度，B = 最大条目大小

### 2.2 SageMath 用法

```python
# SageMath
M = matrix(ZZ, [
    [1, 0, 0, large_value_1],
    [0, 1, 0, large_value_2],
    [0, 0, 1, large_value_3],
    [0, 0, 0, modulus],
])

L = M.LLL()
# L 中的短向量揭示了解
short_vector = L[0]  # 第一行通常是最近的
```

### 2.3 Python (fpylll)

```python
from fpylll import IntegerMatrix, LLL

n = 4
A = IntegerMatrix(n, n)
# 填充矩阵 A...
A[0] = (1, 0, 0, large_value_1)
A[1] = (0, 1, 0, large_value_2)
A[2] = (0, 0, 1, large_value_3)
A[3] = (0, 0, 0, modulus)

LLL.reduction(A)
print(A[0])  # 最短向量
```

---

## 3. BKZ (BLOCK KORKINE-ZOLOTAREV)

### 3.1 与 LLL 的比较

| 属性 | LLL | BKZ-β |
|---|---|---|
| 质量 | 2^((n-1)/2) 近似 | 2^(n/(β-1)) 近似 |
| 速度 | 多项式 | β 的指数 |
| 块大小 | 固定 (2) | 可配置 β |
| 最适用于 | 快速简化 | 高质量简化 |

### 3.2 用法

```python
# SageMath
M = matrix(ZZ, [...])
L = M.BKZ(block_size=20)  # β = 20

# fpylll
from fpylll import BKZ
BKZ.reduction(A, BKZ.Param(block_size=20))
```

经验法则：先用 LLL，如果需要则增加到 BKZ。CTF 中 BKZ 块大小 20-40 通常足够。

---

## 4. COPPERSMITH 的方法

### 4.1 单变量情况

给定 f(x) ≡ 0 (mod N) 且小根 |x₀| < X，找到 x₀。

**界**：X < N^(1/d) 其中 d = f 的次数。

```python
# SageMath — 内置 small_roots
N = ...
R.<x> = PolynomialRing(Zmod(N))
f = x^3 + a*x^2 + b*x + c  # 已知多项式
roots = f.small_roots(X=2^100, beta=1.0, epsilon=1/30)
```

**参数**：
- `X`：根的上界
- `beta`：N = p^beta（beta=1.0 为 N 本身的模根；beta=0.5 为根 mod 未知因子 p ≈ √N）
- `epsilon`：更小 = 更好的结果但更慢（尝试 1/30 到 1/100）

### 4.2 标准化消息攻击 (RSA)

```python
# SageMath
n, e, c = ...  # RSA 参数
known_msb = ...  # 已知消息的上部

R.<x> = PolynomialRing(Zmod(n))
f = (known_msb + x)^e - c

# x 代表未知的低位
X = 2^(unknown_bit_count)
roots = f.small_roots(X=X, beta=1.0)
if roots:
    m = known_msb + int(roots[0])
```

### 4.3 部分密钥暴露 (因子 p)

已知 p 的 MSBs：`p = p_known + x` 其中 x 很小。

```python
# SageMath
n = ...
p_known = ...  # p 的已知高位

R.<x> = PolynomialRing(Zmod(n))
f = p_known + x
roots = f.small_roots(X=2^unknown_bits, beta=0.5)
# beta=0.5 因为 p ≈ √n
if roots:
    p = p_known + int(roots[0])
    q = n // p
```

### 4.4 多变量 Coppersmith (Howgrave-Graham)

对于 f(x, y) ≡ 0 (mod N)：
- 没有保证多项式时间算法
- 启发式方法在实践中有效
- 用于 Boneh-Durfee 的 RSA 小 d

```python
# SageMath — Boneh-Durfee
# e*d ≡ 1 (mod phi) 其中 phi = (p-1)(q-1)
# 重写：e*d = 1 + k*((n+1) - (p+q))
# 令 x = k, y = (p+q)，两者相对于 n 很小

R.<x, y> = PolynomialRing(ZZ)
A = (n + 1) // 2
f = 1 + x * (A + y)  # mod e

# 构建移位多项式并构造格
# 应用 LLL 找到小的 (x₀, y₀)
```

---

## 5. 隐藏数问题 (HNP) — DSA/ECDSA 随机数恢复

### 5.1 问题陈述

给定：签名 (rᵢ, sᵢ) 其中随机数 kᵢ 具有已知偏差（泄露的 MSB 或 LSB）。

DSA 方程：`s = k⁻¹(H(m) + xr) mod q`

重排：`k = s⁻¹(H(m) + xr) mod q`

如果 k 的部分位已知：简化为对格的 CVP。

### 5.2 攻击设置

```python
# SageMath
def ecdsa_nonce_attack(signatures, q, known_bits, bit_position='msb'):
    """
    signatures: 列表，包含 (r, s, hash, 已知随机数位)
    q: 曲线阶
    known_bits: 每个随机数已知的位数
    """
    n = len(signatures)

    # 构建格
    B = 2^(q.nbits() - known_bits)  # 未知部分的界限
    M = matrix(QQ, n + 2, n + 2)

    for i in range(n):
        r_i, s_i, h_i, a_i = signatures[i]
        t_i = Integer(inverse_mod(s_i, q) * r_i % q)
        u_i = Integer(inverse_mod(s_i, q) * h_i % q)

        M[i, i] = q
        M[n, i] = t_i
        M[n+1, i] = u_i - a_i  # a_i = 已知随机数位

    M[n, n] = B / q
    M[n+1, n+1] = B

    # LLL 简化
    L = M.LLL()

    # 找到包含私钥 x 的行
    for row in L:
        x_candidate = Integer(row[n] * q / B) % q
        # 验证 x_candidate 对一个签名
        if verify_private_key(x_candidate, signatures[0], q):
            return x_candidate

    return None
```

### 5.3 实际随机数偏差来源

| 来源 | 泄露位数 | 需要的签名 |
|---|---|---|
| MSB 偏差（始终为 0） | 1 位 | ~100 个签名 |
| 使用错误长度的 k 生成 | 可变 | ~50 个签名 |
| 时序侧信道 | 1-4 位 | 20-100 个签名 |
| 不安全的 PRNG | 许多 | 几个 |
| 重用随机数 (k₁ = k₂) | 所有 | 2 个签名 |

对于 **重用随机数**（最简单的情况）：

```python
def ecdsa_reused_nonce(r, s1, s2, h1, h2, q):
    """当随机数 k 被重用时恢复私钥。"""
    # s1 - s2 = k⁻¹(h1 - h2) mod q （因为 r 相同）
    k = ((h1 - h2) * inverse_mod(s1 - s2, q)) % q
    x = ((s1 * k - h1) * inverse_mod(r, q)) % q
    return x, k
```

---

## 6. 背包 / 子集和攻击

### 6.1 低密度攻击

背包：给定权重 a₁,...,aₙ 和目标 S，找到 x₁,...,xₙ ∈ {0,1} 使得 Σxᵢaᵢ = S。

**密度** d = n / max(log₂ aᵢ)。如果 d < 0.9408，格攻击有效。

```python
# SageMath
def knapsack_lattice(weights, target):
    """通过格攻击解决子集和。"""
    n = len(weights)

    # 构建格（Lagarias-Odlyzko 风格）
    N = ceil(sqrt(n) / 2)  # 缩放因子
    M = matrix(ZZ, n + 1, n + 1)

    for i in range(n):
        M[i, i] = 1
        M[i, n] = N * weights[i]
    M[n, n] = N * target

    # 替代方案：CJLOSS 嵌入
    M2 = matrix(ZZ, n + 1, n + 2)
    for i in range(n):
        M2[i, i] = 1
        M2[i, n + 1] = N * weights[i]
    M2[n, n] = 1
    M2[n, n + 1] = N * (-target)

    L = M2.LLL()

    # 寻找条目在 {0, 1, -1} 中的短向量
    for row in L:
        if all(v in (0, 1) for v in row[:n]):
            solution = list(row[:n])
            if sum(solution[i] * weights[i] for i in range(n)) == target:
                return solution

    return None
```

---

## 7. NTRU 密码分析

### 7.1 NTRU 格

```python
# SageMath
def ntru_lattice_attack(h, q, N):
    """
    构建 NTRU 格用于密钥恢复。
    h = 公钥多项式 (mod q)
    q = 模数
    N = 维度
    """
    # NTRU 格：
    # | qI  0 |
    # | H   I |
    # 其中 H 是 h 的循环矩阵

    H = matrix(ZZ, N, N)
    for i in range(N):
        for j in range(N):
            H[i, j] = h[(j - i) % N]

    M = block_matrix([
        [q * identity_matrix(N), zero_matrix(N)],
        [H, identity_matrix(N)]
    ])

    L = M.LLL()

    # 简化基中的短向量 = (f, g) 私钥
    for row in L:
        f = vector(row[:N])
        g = vector(row[N:])
        if f.norm() < q and g.norm() < q:
            return f, g

    return None
```

---

## 8. 构建攻击格 — 方法论

### 8.1 一般配方

```
1. 将密码学问题表示为：
   "找到小的 x 使得 f(x) ≡ 0 (mod N)"
   或 "找到接近目标 t 的格 L 中的 x"

2. 选择格类型：
   ├─ 多项式格 → Coppersmith 风格
   ├─ 模格 → HNP 风格 CVP
   └─ 背包格 → 子集和 / CJLOSS

3. 确定维度：
   └─ 更多维度 = 更好的近似但更慢

4. 设置缩放因子：
   └─ 平衡行以便短向量具有大致相等的条目
   └─ 常见：乘以 N/X 其中 X 是根界

5. 应用简化：
   ├─ 首先使用 LLL（快速，通常足够）
   └─ 如果 LLL 失败，使用 BKZ（增加块大小：20, 30, 40）

6. 提取解：
   └─ 检查简化基行以查找有效解
```

### 8.2 嵌入技术 (CVP → SVP)

通过将目标嵌入格中，将 CVP 转换为 SVP：

```python
# SageMath
def cvp_to_svp(basis_matrix, target, scale=1):
    """通过 Kannan 嵌入将 CVP 转换为 SVP。"""
    n = basis_matrix.nrows()
    m = basis_matrix.ncols()

    # 增加矩阵
    M = matrix(ZZ, n + 1, m + 1)
    for i in range(n):
        for j in range(m):
            M[i, j] = basis_matrix[i, j]
        M[i, m] = 0

    for j in range(m):
        M[n, j] = target[j]
    M[n, m] = scale  # 缩放因子（尝试 1，然后调整）

    L = M.LLL()

    # 寻找最后一行等于 ±scale 的行
    for row in L:
        if abs(row[m]) == scale:
            return vector(target) - vector(row[:m]) * (row[m] // abs(row[m]))

    return None
```

### 8.3 维度选择指南

| 问题 | 典型维度 | 备注 |
|---|---|---|
| Coppersmith 单变量（次数 d） | d × m 其中 m ≈ 1/ε | 较大的 m = 更小的根界 |
| HNP 使用 n 个签名 | n + 2 | n ≥ known_bits_ratio × q_bits |
| 背包使用 n 个权重 | n + 1 或 n + 2 | 取决于密度 |
| LCG 使用 n 个输出 | n + 1 | 更多输出 = 更容易 |
| Boneh-Durfee | (m+1)(m+2)/2 | m = 参数深度 |

---

## 9. 决策树

```
需要格方法 — 哪种构造？
│
├─ 与 RSA 相关？
│  ├─ 消息的小未知部分 → Coppersmith 单变量
│  │  └─ 检查：unknown_bits < n_bits / e
│  ├─ 部分因子知识 → Coppersmith mod p
│  │  └─ 使用 beta=0.5, X=2^unknown_bits
│  ├─ 小私钥指数 d → Boneh-Durfee
│  │  └─ 检查：d < N^0.292
│  └─ 多个相关方程 → 多变量 Coppersmith
│
├─ 与 DSA/ECDSA 相关？
│  ├─ 重用随机数 → 直接代数恢复（无需格）
│  ├─ 部分随机数泄露 → HNP → CVP 格
│  │  └─ 需要足够的签名：n ≥ q_bits / leaked_bits
│  └─ 随机数偏差 → 统计 HNP → 更大的格
│
├─ 背包 / 子集和？
│  ├─ 低密度 (d < 0.9408) → CJLOSS 格攻击
│  ├─ 高密度 → 格攻击不太可能有效
│  └─ 超增量 → 贪婪算法（无需格）
│
├─ LCG / PRNG？
│  ├─ 完整输出已知 → 代数恢复（无需格）
│  ├─ 截断输出 → 在递归格上进行 CVP
│  └─ 未知模数 → 使用输出差值的 GCD
│
└─ NTRU？
   └─ 构建循环格 → LLL/BKZ 查找短密钥向量
│
└─ 自定义问题？
   ├─ 表示为“找到模 N 的多项式小根” → Coppersmith
   ├─ 表示为“找到接近目标的格点” → CVP
   ├─ 表示为“找到格中的短向量” → SVP / LLL
   └─ 如果都不适用 → 可能不是格问题
```

---

## 10. 常见陷阱

| 陷阱 | 症状 | 修复 |
|---|---|---|
| 根界太大 | `small_roots()` 返回空 | 减少 X，增加 epsilon，验证 Coppersmith 标准满足 |
| 缩放错误 | LLL 找到不相关的短向量 | 缩放列以便目标向量具有平衡条目 |
| 维度不足 | 解不在简化基中 | 增加 m 参数（更多移位多项式） |
| beta 错误 | Coppersmith 没有找到因子 | beta=0.5 用于半大小因子，beta=1.0 用于完整模数 |
| HNP 签名太少 | 格攻击失败 | 收集更多具有随机数偏差的签名 |
| BKZ 块大小太小 | 解不够短 | 增加块大小（尝试 25, 30, 40） |
| 整数溢出 | SageMath 崩溃 | 明确使用 ZZ 环，避免 QQ 和 ZZ 混合 |
