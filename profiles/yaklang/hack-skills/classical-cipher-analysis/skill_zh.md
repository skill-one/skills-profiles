# 技能：古典密码分析 — 专家密码分析手册

> **AI 加载指令**：CTF 中的专家级古典密码识别和破解技术。涵盖密码识别方法（频率分析、IC、卡西斯基法）、单字母替换、凯撒/ROT、维吉尼亚、恩尼格玛、仿射、希尔、移位密码，以及培根/波利比乌斯/普莱费亚和 XOR 密码。基础模型通常跳过识别步骤，直接跳到错误的密码类型，或者无法识别需要解码才能分析的编码（base64/hex）密文。

## 0. 相关路由

- [对称密码攻击](../symmetric-cipher-attacks/SKILL.md) 当处理现代对称密码（AES/DES）而不是古典密码时
- [哈希攻击技术](../hash-attack-techniques/SKILL.md) 当挑战涉及基于哈希的构造时
- [格基密码攻击](../lattice-crypto-attacks/SKILL.md) 当遇到基于背包的密码时

### 快速识别指南

| 观察 | 可能的密码 | 首要操作 |
|---|---|---|
| 所有 uppercase 字母，不均匀频率 | 单字母替换 | 频率分析 |
| 所有 uppercase，平坦频率分布 | 多字母（维吉尼亚） | IC + 卡西斯基法 |
| 仅 A-Z 均匀偏移 | 凯撒/ROT | 尝试 25 次移位 |
| Base64 字母表（A-Za-z0-9+/=） | Base64 编码（先解码） | Base64 解码 |
| 十六进制字符串（0-9a-f） | 十六进制编码（先解码） | 十六进制解码 |
| 二进制（0s 和 1s） | 二进制编码 | 转换为 ASCII |
| 点和划线 | 摩尔斯电码 | 摩尔斯解码 |
| 抬高/正常文本模式 | 培根密码 | 映射到 A/B，解码 |
| 两位数数字对（11-55） | 波利比乌斯方格 | 网格查找 |
| 文本看起来是乱序的（正确的字母，错误的顺序） | 移位 | 字母重组分析 |
| 非打印字节类似 XOR | XOR 密码 | 单字节/重复密钥 XOR 分析 |

---

## 1. 密码识别方法

### 1.1 第一步：字符集分析

```python
def analyze_charset(ciphertext):
    """通过字符集识别编码/密码."""
    chars = set(ciphertext.strip())

    if chars <= set('01 \n'):
        return "二进制编码"
    if chars <= set('.-/ \n'):
        return "摩尔斯电码"
    if chars <= set('0123456789abcdef \n'):
        return "十六进制编码"
    if chars <= set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=\n'):
        if '=' in ciphertext or len(ciphertext) % 4 == 0:
            return "Base64 编码"
    if chars <= set('ABCDEFGHIJKLMNOPQRSTUVWXYZ \n'):
        return "仅 uppercase — 古典密码"
    if all(c in '12345' for c in ciphertext.replace(' ', '').replace('\n', '')):
        return "波利比乌斯方格（数字 1-5）"

    return "混合字符集 — 需要进一步分析"
```

### 1.2 第二步：频率分析

```python
from collections import Counter

def frequency_analysis(text):
    """计算字母频率分布."""
    text = text.upper()
    letters = [c for c in text if c.isalpha()]
    total = len(letters)
    freq = Counter(letters)

    print("字母频率:")
    for letter, count in freq.most_common():
        pct = count / total * 100
        bar = '#' * int(pct)
        print(f"  {letter}: {pct:5.1f}% {bar}")

    return freq

# 英语字母频率（用于比较）：
# E T A O I N S H R D L C U M W F G Y P B V K J X Q Z
# 12.7 9.1 8.2 7.5 7.0 6.7 6.3 6.1 6.0 4.3 4.0 2.8 ...
```

### 1.3 第三步：巧合指数（IC）

```python
def index_of_coincidence(text):
    """
    IC ≈ 0.065 → 英语 / 单字母替换
    IC ≈ 0.038 → 随机 / 多字母密码
    """
    text = [c for c in text.upper() if c.isalpha()]
    N = len(text)
    freq = Counter(text)

    ic = sum(f * (f - 1) for f in freq.values()) / (N * (N - 1))
    return ic

# 解释：
# IC > 0.060 → 单字母（凯撒，简单替换，普莱费亚）
# IC ≈ 0.045-0.055 → 多字母，短密钥（维吉尼亚密钥 < 10）
# IC ≈ 0.038-0.042 → 多字母，长密钥或随机
```

### 1.4 第四步：卡西斯基检验（用于多字母）

```python
from math import gcd
from functools import reduce

def kasiski(ciphertext, min_len=3):
    """查找重复序列及其距离 → 密钥长度."""
    text = ''.join(c for c in ciphertext.upper() if c.isalpha())
    distances = []

    for length in range(min_len, min(20, len(text) // 3)):
        for i in range(len(text) - length):
            seq = text[i:i+length]
            j = text.find(seq, i + 1)
            while j != -1:
                distances.append(j - i)
                j = text.find(seq, j + 1)

    if not distances:
        return None

    # 密钥长度可能是常见距离的最大公约数
    common_gcds = Counter()
    for d in distances:
        for factor in range(2, min(d + 1, 30)):
            if d % factor == 0:
                common_gcds[factor] += 1

    print("可能的密钥长度（按频率）:")
    for length, count in common_gcds.most_common(5):
        print(f"  密钥长度 {length}: {count} 次出现")

    return common_gcds.most_common(1)[0][0]
```

---

## 2. 单字母替换

### 2.1 频率分析攻击

```python
def solve_substitution(ciphertext, interactive=False):
    """通过频率分析解决单字母替换."""
    freq = frequency_analysis(ciphertext)

    # 英语频率顺序
    eng_order = "ETAOINSRHLDCUMWFGYPBVKJXQZ"
    cipher_order = ''.join(c for c, _ in freq.most_common())

    # 初始映射（基于频率的猜测）
    mapping = {}
    for i, c in enumerate(cipher_order):
        if i < len(eng_order):
            mapping[c] = eng_order[i]

    # 应用映射
    result = ""
    for c in ciphertext.upper():
        result += mapping.get(c, c)

    return result, mapping

# 更好的方法：使用自动解密器
# quipqiup.com — 在线替换解密器
# dcode.fr/monoalphabetic-substitution — 带有单词模式匹配
```

### 2.2 已知明文（窃取法）

如果部分明文已知（例如，“flag{" 前缀）：

```python
def crib_drag_substitution(ciphertext, known_plain, known_cipher):
    """从已知明文-密文对构建部分映射."""
    mapping = {}
    for p, c in zip(known_plain.upper(), known_cipher.upper()):
        mapping[c] = p

    # 应用部分映射
    result = ""
    for c in ciphertext.upper():
        result += mapping.get(c, '?')

    return result, mapping
```

---

## 3. 凯撒 / ROT 密码

### 3.1 暴力破解

```python
def caesar_bruteforce(ciphertext):
    """尝试所有 25 次移位，通过英语频率评分."""
    results = []
    for shift in range(26):
        decrypted = ""
        for c in ciphertext:
            if c.isalpha():
                base = ord('A') if c.isupper() else ord('a')
                decrypted += chr((ord(c) - base - shift) % 26 + base)
            else:
                decrypted += c

        # Chi-squared 评分针对英语频率
        score = chi_squared_score(decrypted)
        results.append((shift, score, decrypted))

    results.sort(key=lambda x: x[1])
    return results[0]  # 最佳匹配

def chi_squared_score(text):
    """分数越低 = 越接近英语."""
    expected = {
        'E': 12.7, 'T': 9.1, 'A': 8.2, 'O': 7.5, 'I': 7.0,
        'N': 6.7, 'S': 6.3, 'H': 6.1, 'R': 6.0, 'D': 4.3,
        'L': 4.0, 'C': 2.8, 'U': 2.8, 'M': 2.4, 'W': 2.4,
        'F': 2.2, 'G': 2.0, 'Y': 2.0, 'P': 1.9, 'B': 1.5,
        'V': 1.0, 'K': 0.8, 'J': 0.2, 'X': 0.2, 'Q': 0.1, 'Z': 0.1,
    }
    text = text.upper()
    letters = [c for c in text if c.isalpha()]
    total = len(letters)
    if total == 0:
        return float('inf')

    freq = Counter(letters)
    score = sum(
        (freq.get(c, 0) / total * 100 - expected.get(c, 0)) ** 2 / max(expected.get(c, 0.1), 0.1)
        for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    )
    return score
```

### 3.2 ROT13 和 ROT47

```python
import codecs

# ROT13（仅字母）
rot13 = codecs.decode(ciphertext, 'rot_13')

# ROT47（ASCII 33-126）
def rot47(text):
    return ''.join(
        chr(33 + (ord(c) - 33 + 47) % 94) if 33 <= ord(c) <= 126 else c
        for c in text
    )
```

---

## 4. 维吉尼亚密码

### 4.1 完整攻击工作流

```
步骤 1：确认多字母（IC ≈ 0.04-0.05）
步骤 2：查找密钥长度（卡西斯基法 + 每个周期的 IC）
步骤 3：对每个密钥位置，作为单个凯撒密码解决
步骤 4：组装密钥 → 解密
```

### 4.2 基于IC的密钥长度检测

```python
def find_vigenere_key_length(ciphertext, max_key=20):
    """使用 IC 查找维吉尼亚密钥长度."""
    text = [c for c in ciphertext.upper() if c.isalpha()]
    results = []

    for kl in range(1, max_key + 1):
        # 将文本分成 kl 列
        columns = [[] for _ in range(kl)]
        for i, c in enumerate(text):
            columns[i % kl].append(c)

        # 计算各列的平均 IC
        avg_ic = sum(
            index_of_coincidence(''.join(col)) for col in columns
        ) / kl

        results.append((kl, avg_ic))
        print(f"  密钥长度 {kl:2d}: IC = {avg_ic:.4f}")

    # IC 最接近 0.065 的密钥长度
    best = max(results, key=lambda x: x[1])
    return best[0]
```

### 4.3 按位置频率攻击

```python
def crack_vigenere(ciphertext, key_length):
    """给定已知密钥长度，破解维吉尼亚密码."""
    text = [c for c in ciphertext.upper() if c.isalpha()]
    key = ""

    for pos in range(key_length):
        column = ''.join(text[i] for i in range(pos, len(text), key_length))
        # 作为凯撒密码解决
        shift, score, _ = caesar_bruteforce(column)
        key += chr(shift + ord('A'))

    # 解密
    plaintext = ""
    ki = 0
    for c in ciphertext:
        if c.isalpha():
            shift = ord(key[ki % key_length]) - ord('A')
            base = ord('A') if c.isupper() else ord('a')
            plaintext += chr((ord(c) - base - shift) % 26 + base)
            ki += 1
        else:
            plaintext += c

    return key, plaintext
```

---

## 5. 仿射密码

### 5.1 定义

`E(x) = (a·x + b) mod 26` 其中 gcd(a, 26) = 1。

有效 a 值：1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25（12 个值）。

### 5.2 暴力破解（312 种组合）

```python
def crack_affine(ciphertext):
    """暴力破解仿射密码：12 × 26 = 312 种组合."""
    valid_a = [a for a in range(1, 26) if gcd(a, 26) == 1]

    for a in valid_a:
        a_inv = pow(a, -1, 26)
        for b in range(26):
            plaintext = ""
            for c in ciphertext.upper():
                if c.isalpha():
                    y = ord(c) - ord('A')
                    x = (a_inv * (y - b)) % 26
                    plaintext += chr(x + ord('A'))
                else:
                    plaintext += c

            score = chi_squared_score(plaintext)
            if score < 50:  # 合理的英语
                print(f"a={a}, b={b}: {plaintext[:50]}...")
```

### 5.3 已知明文

```python
def affine_from_known(plain1, cipher1, plain2, cipher2):
    """从两个已知明文-密文对恢复 (a, b)."""
    p1, c1 = ord(plain1) - ord('A'), ord(cipher1) - ord('A')
    p2, c2 = ord(plain2) - ord('A'), ord(cipher2) - ord('A')

    # c1 = a*p1 + b, c2 = a*p2 + b
    # c1 - c2 = a*(p1 - p2) mod 26
    diff_p = (p1 - p2) % 26
    diff_c = (c1 - c2) % 26

    if gcd(diff_p, 26) != 1:
        return None

    a = (diff_c * pow(diff_p, -1, 26)) % 26
    b = (c1 - a * p1) % 26
    return a, b
```

---

## 6. 希尔密码

基于矩阵的密码：`C = K · P mod 26` 其中 K 是 n×n 密钥矩阵。

### 6.1 已知明文攻击

```python
import numpy as np

def crack_hill(known_plain, known_cipher, n=2):
    """从已知明文-密文恢复希尔密码密钥（模 26）。"""
    # 转换为数字
    P = [ord(c) - ord('A') for c in known_plain.upper()]
    C = [ord(c) - ord('A') for c in known_cipher.upper()]

    # 构建矩阵（至少需要 n 对 n-gram）
    P_matrix = np.array(P[:n*n]).reshape(n, n).T
    C_matrix = np.array(C[:n*n]).reshape(n, n).T

    # K = C · P⁻¹ mod 26
    # 需要模矩阵逆
    from sympy import Matrix
    P_mat = Matrix(P_matrix.tolist())
    C_mat = Matrix(C_matrix.tolist())

    P_inv = P_mat.inv_mod(26)
    K = (C_mat * P_inv) % 26

    return K
```

---

## 7. 移位密码

### 7.1 铁轨密码

```python
def rail_fence_decrypt(ciphertext, rails):
    """解密铁轨密码."""
    n = len(ciphertext)
    # 构建之字形模式
    pattern = []
    for i in range(n):
        row = 0
        cycle = 2 * (rails - 1)
        pos = i % cycle
        row = pos if pos < rails else cycle - pos
        pattern.append((row, i))

    pattern.sort()

    # 填充字符
    result = [''] * n
    ci = 0
    for _, orig_pos in pattern:
        result[orig_pos] = ciphertext[ci]
        ci += 1

    return ''.join(result)

# 暴力破解所有铁轨数
for rails in range(2, 20):
    print(f"铁轨 {rails}: {rail_fence_decrypt(ct, rails)[:50]}")
```

### 7.2 列式移位

```python
def columnar_decrypt(ciphertext, key):
    """给定密钥词，解密列式移位."""
    n_cols = len(key)
    n_rows = -(-len(ciphertext) // n_cols)  # 向上取整除法

    # 从密钥确定列顺序
    order = sorted(range(n_cols), key=lambda i: key[i])

    # 计算列长度（有些可能更短）
    full_cols = len(ciphertext) % n_cols
    if full_cols == 0:
        full_cols = n_cols

    # 将密文分成列（按密钥顺序）
    columns = [''] * n_cols
    pos = 0
    for col_idx in order:
        col_len = n_rows if col_idx < full_cols else n_rows - 1
        columns[col_idx] = ciphertext[pos:pos + col_len]
        pos += col_len

    # 按行读取
    plaintext = ''
    for row in range(n_rows):
        for col in range(n_cols):
            if row < len(columns[col]):
                plaintext += columns[col][row]

    return plaintext
```

---

## 8. XOR 密码

### 8.1 单字节 XOR

参见 [对称密码攻击](../symmetric-cipher-attacks/SKILL.md) 第 4.2 节的完整实现。

### 8.2 多字节 XOR（xortool）

```bash
# 自动密钥长度检测和破解
xortool ciphertext.bin -l 5        # 尝试密钥长度 5
xortool ciphertext.bin -b          # 暴力破解密钥长度
xortool ciphertext.bin -c 20       # 假设最常见字符是空格（0x20）
```

### 8.3 已知明文 XOR

```python
def xor_known_plaintext(ciphertext, known_plain, offset=0):
    """从给定偏移的已知明文恢复 XOR 密钥."""
    key_fragment = bytes(
        c ^ p for c, p in zip(ciphertext[offset:], known_plain)
    )
    print(f"密钥片段: {key_fragment}")

    # 如果重复密钥，从片段推断完整密钥
    return key_fragment
```

---

## 9. 特殊密码

### 9.1 培根密码

使用两种字体（A=正常，B=粗体/斜体）的二进制编码。

```python
BACON = {
    'AAAAA': 'A', 'AAAAB': 'B', 'AAABA': 'C', 'AAABB': 'D',
    'AABAA': 'E', 'AABAB': 'F', 'AABBA': 'G', 'AABBB': 'H',
    'ABAAA': 'I', 'ABAAB': 'J', 'ABABA': 'K', 'ABABB': 'L',
    'ABBAA': 'M', 'ABBAB': 'N', 'ABBBA': 'O', 'ABBBB': 'P',
    'BAAAA': 'Q', 'BAAAB': 'R', 'BAABA': 'S', 'BAABB': 'T',
    'BABAA': 'U', 'BABAB': 'V', 'BABBA': 'W', 'BABBB': 'X',
    'BAAAA': 'Y', 'BAAAB': 'Z',
}

def decode_bacon(text):
    """解码培根密码：uppercase=B, lowercase=A（或类似映射）。"""
    binary = ''.join('B' if c.isupper() else 'A' for c in text if c.isalpha())
    result = ''
    for i in range(0, len(binary) - 4, 5):
        chunk = binary[i:i+5]
        result += BACON.get(chunk, '?')
    return result
```

### 9.2 波利比乌斯方格

```
    1 2 3 4 5
  ┌──────────
1 │ A B C D E
2 │ F G H I/J K
3 │ L M N O P
4 │ Q R S T U
5 │ V W X Y Z

"HELLO" = "23 15 31 31 34"
```

### 9.3 普莱费亚

5×5 网格密码，加密双字母。

```
密钥: "MONARCHY" → 网格:
  M O N A R
  C H Y B D
  E F G I/J K
  L P Q S T
  U V W X Z

规则:
  同一行 → 向右移：HE → FE → "GF"
  同一列 → 向下移
  矩形 → 交换列
```

---

## 10. 决策树

```
未知密文 — 如何识别和破解？
│
├─ 第一步：检查编码
│  ├─ Base64 字母表带填充？ → 先解码，然后重新分析
│  ├─ 十六进制字符串？ → 转换为字节，重新分析
│  ├─ 二进制（01）？ → 转换为 ASCII
│  ├─ 摩尔斯（.-/）？ → 解码摩尔斯
│  └─ 可打印文本？ → 继续到第 2 步
│
├─ 第 2 步：字符集
│  ├─ 仅字母 (A-Z)?
│  │  ├─ 计算 IC
│  │  │  ├─ IC ≈ 0.065 → 单字母
│  │  │  │  ├─ 频率均匀偏移？ → 凯撒 → 暴力破解 25
│  │  │  │  ├─ 看起来是随机映射？ → 简单替换 → 频率分析
│  │  │  │  └─ 双字母模式？ → 普莱费亚 → 双字母分析
│  │  │  │
│  │  │  ├─ IC ≈ 0.04-0.05 → 多字母
│  │  │  │  ├─ 卡西斯基法 → 查找密钥长度
│  │  │  │  └─ 每个密钥位置，作为单个凯撒密码解决
│  │  │  │
│  │  │  └─ IC ≈ 0.038 → 非常长的密钥或一次性密码本
│  │  │     └─ 寻找密钥重用或弱密钥生成
│  │  │
│  │  └─ 字母看起来是乱序的（正确的频率，错误的顺序）?
│  │     └─ 移位
│  │        ├─ 铁轨 → 暴力破解铁轨数
│  │        └─ 列式 → 尝试常见密钥长度
│  │
│  ├─ 数字（数字对）?
│  │  ├─ 对在范围 11-55 → 波利比乌斯方格
│  │  └─ 数字模 26 → 数字替换
│  │
│  ├─ 混合大小写带模式?
│  │  └─ 大小写编码二进制 → 培根密码
│  │
│  └─ 非打印字节?
│     └─ XOR 密码
│        ├─ 单字节密钥 → 暴力破解 256
│        ├─ 重复密钥 → xortool / 汉明距离
│        └─ 已知明文 → 直接密钥恢复
│
└─ 第 3 步：应用特定攻击
   ├─ 替换 → quipqiup.com / 频率分析
   ├─ 凯撒 → dcode.fr / 暴力破解
   ├─ 维吉尼亚 → 卡西斯基法 + 每列凯撒
   ├─ 仿射 → 暴力破解 312 种组合
   ├─ 希尔 → 已知明文矩阵攻击
   └─ 移位 → 模式分析 + 暴力破解
   └─ XOR → xortool / 窃取法
```

---

## 11. 工具

| 工具 | 目的 | URL/使用 |
|---|---|---|
| **CyberChef** | 通用编码/密码瑞士军刀 | gchq.github.io/CyberChef |
| **dcode.fr** | 在线 200+ 密码解密器 | dcode.fr |
| **quipqiup** | 自动替换密码解密器 | quipqiup.com |
| **xortool** | XOR 密码分析和破解 | `pip install xortool` |
| **RsaCtfTool** | RSA + 一些古典密码支持 | GitHub |
| **Ciphey** | 自动密码检测和解密 | `pip install ciphey` |
| **hashID** | 识别哈希类型 | `pip install hashid` |
| **Python** | 自定义频率分析和脚本 | 上述所有攻击 |

### CyberChef 菜单（常见）

```
ROT13:               ROT13
Caesar 暴力破解:   ROT13（带偏移滑块）
Base64 解码:        从 Base64
Hex 解码:           从 Hex
XOR:                  XOR（密钥作为 hex/utf8）
维吉尼亚:             维吉尼亚解密
摩尔斯:                从摩尔斯电码
```
