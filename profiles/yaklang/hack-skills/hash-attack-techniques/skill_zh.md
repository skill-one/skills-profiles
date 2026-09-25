# 技能：哈希攻击技术 — 专家密码分析实战手册

> **AI 加载指令**：CTF 比赛和安全评估中的专家级哈希攻击技术。涵盖长度扩展攻击、MD5/SHA1 碰撞生成、中间相遇攻击、HMAC 时间侧信道、生日攻击和工作量证明解决。基础模型常错误地将长度扩展应用于 HMAC 或 SHA-3，或无法区分相同前缀和选择前缀的碰撞。

## 0. 相关路由

- [rsa-attack-techniques](../rsa-attack-techniques/SKILL.md) 当哈希弱点影响 RSA 签名方案时
- [symmetric-cipher-attacks](../symmetric-cipher-attacks/SKILL.md) 当哈希用于密钥派生时
- [classical-cipher-analysis](../classical-cipher-analysis/SKILL.md) 当分析古典密码中的哈希类结构时

### 快速攻击选择

| 场景 | 攻击 | 工具 |
|---|---|---|
| `H(secret || msg)` 已知，扩展消息 | 长度扩展 | HashPump, hash_extender |
| 需要两个具有相同 MD5 的文件 | 相同前缀碰撞 | fastcoll |
| 需要特定 MD5 前缀匹配 | 选择前缀碰撞 | hashclash |
| 字节逐字节 HMAC 比较 | 时间攻击 | 自定义脚本 |
| 查找任何碰撞 | 生日攻击 | O(2^(n/2)) |
| 工作量证明：查找具有前导零的哈希 | 暴力破解 | hashcat, Python |

---

## 1. 长度扩展攻击

### 1.1 易受攻击与不易受攻击

| 哈希 | 易受攻击 | 原因 |
|---|---|---|
| MD5 | 是 | Merkle-Damgard 构造 |
| SHA-1 | 是 | Merkle-Damgard 构造 |
| SHA-256 | 是 | Merkle-Damgard 构造 |
| SHA-512 | 是 | Merkle-Damgard 构造 |
| SHA-3 / Keccak | 否 | 沥青构造 |
| HMAC-* | 否 | 双重哈希防止扩展 |
| SHA-256 截断 | 否（如果截断） | 缺少内部状态位 |
| BLAKE2 | 否 | 不同的构造 |

### 1.2 攻击机制

```
给定:   MAC = H(secret || original_message)
已知:   original_message, len(secret), MAC 值
计算:   H(secret || original_message || padding || extension)
         而无需知道 secret!

方法:   MAC 值是处理后的内部哈希状态
        (secret || original_message || padding).
        使用此状态初始化哈希，继续哈希扩展。
```

### 1.3 填充计算 (MD5/SHA)

```python
def md5_padding(message_len_bytes):
    """计算给定消息长度的 MD5/SHA 填充."""
    bit_len = message_len_bytes * 8

    # 用 0x80 + 零填充到长度 ≡ 56 (mod 64)
    padding = b'\x80'
    padding += b'\x00' * ((55 - message_len_bytes) % 64)

    # 追加原始长度作为 64 位小端（MD5）
    # 或大端（SHA）
    padding += bit_len.to_bytes(8, 'little')  # MD5
    # padding += bit_len.to_bytes(8, 'big')    # SHA

    return padding
```

### 1.4 工具使用

```bash
# HashPump
hashpump -s "known_mac_hex" \
         -d "original_data" \
         -k 16 \            # secret length
         -a "extension_data"

# 输出: new_mac, new_data (original + padding + extension)

# hash_extender
hash_extender --data "original" \
              --secret 16 \
              --append "extension" \
              --signature "known_mac_hex" \
              --format md5
```

### 1.5 Python 实现

```python
import struct

def md5_extend(original_mac, original_data_len, secret_len, extension):
    """
    执行 MD5 长度扩展攻击.
    original_mac: H(secret || original_data) 的十六进制字符串
    """
    # 将 MAC 解析为 MD5 内部状态（4 × 32 位单词，小端）
    h = struct.unpack('<4I', bytes.fromhex(original_mac))

    # 计算填充后的总长度
    total_original = secret_len + original_data_len
    padding = md5_padding(total_original)
    forged_len = total_original + len(padding) + len(extension)

    # 从保存的状态继续 MD5 哈希扩展
    # （需要接受初始状态的 MD5 实现）
    from hashlib import md5
    # 大多数 stdlib md5 不暴露状态设置
    # 使用: hlextend 库或自定义 MD5

    import hlextend
    sha = hlextend.new('md5')
    new_hash = sha.extend(extension, original_data, secret_len,
                          original_mac)
    new_data = sha.payload  # 包括 original + padding + extension

    return new_hash, new_data
```

---

## 2. MD5 碰撞攻击

### 2.1 相同前缀碰撞 (fastcoll)

两个具有相同前缀但内容不同的消息，产生相同的 MD5。

```bash
# 生成碰撞对
fastcoll -p prefix_file -o collision1.bin collision2.bin

# 结果: MD5(collision1.bin) == MD5(collision2.bin)
# 文件在恰好 128 字节（两个 MD5 块）上不同
```

### 2.2 选择前缀碰撞 (hashclash)

两个具有不同选择前缀的消息，通过计算后缀使其碰撞。

```bash
# hashclash (Marc Stevens)
./hashclash prefix1.bin prefix2.bin

# 结果: MD5(prefix1 || suffix1) == MD5(prefix2 || suffix2)
```

### 2.3 UniColl (单块近似碰撞)

产生两个在单个 MD5 块内差异为一个字节的相同哈希的消息。

```
应用: 生成具有相同 MD5 的两个 PDF/PE 文件
  - 文件 1: 良性内容
  - 文件 2: 恶意内容
  - 相同的 MD5 哈希
```

### 2.4 碰撞应用

| 应用 | 技术 | 影响 |
|---|---|---|
| 证书伪造 | 选择前缀 | 恶意 CA 证书（2008 年已证明） |
| 二进制替换 | 相同前缀 + 条件 | 两个可执行文件，相同 MD5，不同行为 |
| PDF 碰撞 | UniColl | 两个显示不同内容的 PDF |
| Git 提交碰撞 | 选择前缀（SHAttered 用于 SHA1） | 具有相同哈希的两个提交 |
| CTF：绕过 MD5 检查 | fastcoll | 两个不同输入被接受为相同 |

### 2.5 CTF MD5 碰撞技巧

```php
// PHP: md5($_GET['a']) == md5($_GET['b']) && $_GET['a'] != $_GET['b']

// 方法 1: 数组技巧（不是真正的碰撞）
?a[]=1&b[]=2  // md5(array) 返回 NULL, NULL == NULL

// 方法 2: 真正的碰撞（fastcoll 输出，URL 编码的二进制）
?a=<collision1_urlencoded>&b=<collision2_urlencoded>

// 方法 3: 0e 魔法哈希（松散比较 ==）
// md5("240610708") = "0e462097431906509019562988736854"
// md5("QNKCDZO")   = "0e830400451993494058024219903391"
// PHP: "0e..." == "0e..." 为 TRUE（两者作为浮点数都计算为 0）
```

---

## 3. SHA-1 碰撞

### 3.1 SHAttered 攻击 (2017)

首个实用的 SHA-1 碰撞：两个具有相同 SHA-1 的 PDF 文件。

- 复杂度：~2^63 个 SHA-1 计算
- 成本：~$110K 在 GPU 集群上（2017 年价格）
- 工具：shattered.io 提供碰撞 PDF

### 3.2 SHA-1 选择前缀碰撞 (2020)

- 复杂度：~2^63.4 个计算
- 实际用于攻击 PGP/GnuPG 密钥服务器
- 证明 SHA-1 对于碰撞抵抗已失效

### 3.3 影响

```
SHA-1 不应用于：
  ✗ 数字签名
  ✗ 证书指纹
  ✗ Git 提交完整性（正在迁移到 SHA-256）
  ✗ 基于哈希的重复数据删除

SHA-1 仍然适用于：
  ✓ HMAC-SHA1（不需要碰撞抵抗）
  ✓ HKDF-SHA1（PRF 安全性足够）
  ✓ 非对抗性校验和
```

---

## 4. 生日攻击

### 4.1 通用生日界限

```
对于 n 位哈希：预期在 ~2^(n/2) 个哈希后出现碰撞

哈希     位    生日界限
MD5      128     2^64
SHA-1    160     2^80
SHA-256  256     2^128

CTF 应用：如果哈希被截断到 k 位，
碰撞在 ~2^(k/2) 次尝试中出现
```

### 4.2 生日攻击实现

```python
import hashlib
import os

def birthday_attack(hash_func, output_bits, max_attempts=2**28):
    """查找截断哈希的碰撞."""
    mask = (1 << output_bits) - 1
    seen = {}

    for _ in range(max_attempts):
        msg = os.urandom(16)
        h = int(hash_func(msg).hexdigest(), 16) & mask

        if h in seen and seen[h] != msg:
            return seen[h], msg  # 碰撞！
        seen[h] = msg

    return None

# 示例：查找 SHA-256 前 32 位的碰撞
result = birthday_attack(hashlib.sha256, 32)
```

---

## 5. HMAC 时间攻击

### 5.1 易受攻击的比较

```python
# VULNERABLE: 早期退出字符串比较
def verify_hmac(received, expected):
    return received == expected  # Python == 从左到右比较

# 比较可能在第一个不同字节时短路，
# 泄露时间信息
```

### 5.2 攻击策略

```python
import requests
import time

def hmac_timing_attack(url, data, hmac_len=32):
    """通过时间攻击逐字节恢复 HMAC."""
    known = ""

    for pos in range(hmac_len * 2):  # 十六进制字符
        best_char = ""
        best_time = 0

        for c in "0123456789abcdef":
            candidate = known + c + "0" * (hmac_len * 2 - len(known) - 1)
            times = []

            for _ in range(50):  # 多次采样以提高精度
                start = time.perf_counter_ns()
                requests.get(url, params={**data, "mac": candidate})
                elapsed = time.perf_counter_ns() - start
                times.append(elapsed)

            avg_time = sorted(times)[len(times)//2]  # 中位数
            if avg_time > best_time:
                best_time = avg_time
                best_char = c

        known += best_char
        print(f"位置 {pos}: {known}")

    return known
```

### 5.3 恒定时间比较（防御）

```python
import hmac

# SECURE: 恒定时间比较
def verify_hmac_secure(received, expected):
    return hmac.compare_digest(received, expected)
```

---

## 6. 中间相遇（哈希）

### 6.1 概念

将哈希计算分成两半，预计算一半，匹配另一半。

```
哈希计算: H = f(g(x₁), h(x₂))

预计算: table[g(x₁)] = x₁  对于空间₁ 中的所有 x₁
搜索:     对于空间₂ 中的每个 x₂:
              如果 h(x₂) 在 table 中:
                找到！ (x₁, x₂)

时间:  O(2^(n/2)) 而不是 O(2^n)
空间: O(2^(n/2))
```

---

## 7. 哈希工作量证明

### 7.1 常见 CTF 工作量证明格式

```python
# 格式 1: 找到 x，使得 SHA256(prefix + x) 以 N 个零位开头
import hashlib

def solve_pow_prefix(prefix, zero_bits):
    target = '0' * (zero_bits // 4)
    i = 0
    while True:
        candidate = prefix + str(i)
        h = hashlib.sha256(candidate.encode()).hexdigest()
        if h.startswith(target):
            return str(i)
        i += 1

# 格式 2: 找到 x，使得 SHA256(x) 以特定后缀结尾
def solve_pow_suffix(suffix_hex, hash_func=hashlib.sha256):
    i = 0
    while True:
        h = hash_func(str(i).encode()).hexdigest()
        if h.endswith(suffix_hex):
            return str(i)
        i += 1
```

### 7.2 GPU 加速工作量证明

```bash
# hashcat 用于 SHA256 工作量证明
hashcat -a 3 -m 1400 --hex-charset \
  "0000000000000000000000000000000000000000000000000000000000000000:prefix" \
  "?a?a?a?a?a?a?a?a"
```

---

## 8. 彩虹表与盐

### 8.1 彩虹表攻击

```
预计算链: 密码 → 哈希 → 还原 → 密码₂ → 哈希₂ → ...
查找: 给定哈希 h，检查 h 是否出现在任何链中
时间-内存权衡: 比完整表空间更小，比直接查找时间更长
```

### 8.2 盐击败彩虹表

```
无盐: H(password) — 相同密码始终产生相同哈希
有盐: H(salt || password) — 每个用户使用不同的盐

彩虹表是密码特定的，而不是（盐+密码）特定的
每个唯一盐需要一个单独的表→不可行
```

### 8.3 现代密码哈希

| 算法 | 盐 | 迭代次数 | 内存硬化 | 推荐 |
|---|---|---|---|---|
| MD5 | 否 | 1 | 否 | 从不 |
| SHA-256 | 否 | 1 | 否 | 从不用于密码 |
| bcrypt | 是 | 可配置 | 否 | 是 |
| scrypt | 是 | 可配置 | 是 | 是 |
| Argon2 | 是 | 可配置 | 是 | 最佳选择 |
| PBKDF2 | 是 | 可配置 | 否 | 可接受 |

---

## 9. 决策树

```
与哈希相关的挑战 — 场景是什么？
│
├─ 拥有 H(secret || message)，需要扩展？
│  ├─ 哈希是 MD5/SHA1/SHA256/SHA512？
│  │  └─ 是 → 长度扩展攻击
│  │     └─ 需要: MAC 值、原始消息、秘密长度
│  │        └─ 工具: HashPump 或 hash_extender
│  │
│  └─ 哈希是 SHA3/HMAC/BLAKE2？
│     └─ 长度扩展无效
│        └─ 查找其他漏洞
│
├─ 需要两个具有相同哈希的输入？
│  ├─ MD5？
│  │  ├─ 相同前缀 → fastcoll（秒级）
│  │  ├─ 不同前缀 → hashclash（小时级）
│  │  └─ CTF PHP 松散比较 → 0e 魔法哈希
│  │
│  ├─ SHA-1？
│  │  └─ SHAttered（昂贵，如果可能使用预计算）
│  │
│  └─ SHA-256+？
│     └─ 没有实际碰撞攻击
│        └─ 查找逻辑漏洞
│
├─ 需要伪造 HMAC？
│  ├─ 时间侧信道可用？
│  │  └─ 字节逐字节时间攻击
│  │
│  ├─ 密钥是短/弱？
│  │  └─ 使用 hashcat 暴力破解密钥
│  │
│  └─ 没有弱点？
│     └─ HMAC 是安全的 — 查找其他地方
│
├─ 哈希被截断（短输出）？
│  └─ 生日攻击 — 碰撞在 2^(位/2) 中
│
├─ 工作量证明？
│  └─ 并行计算暴力破解
│     ├─ Python 多进程用于 < 28 位
│     ├─ hashcat/GPU 用于 > 28 位
│     └─ 优化: 预增量字符串，避免重新编码
│
└─ 密码哈希破解？
   ├─ 无盐 → 彩虹表（预计算）
   ├─ 已知盐 → hashcat / John the Ripper
   └─ 内存硬化（Argon2/scrypt）→ 受内存限制，慢速暴力破解
```

---

## 10. 工具

| 工具 | 目的 | 使用 |
|---|---|---|
| **HashPump** | 长度扩展攻击 | `hashpump -s MAC -d data -k secret_len -a extension` |
| **hash_extender** | 长度扩展（多种算法） | `hash_extender --data D --secret L --append E --sig MAC` |
| **fastcoll** | MD5 相同前缀碰撞 | `fastcoll -p prefix -o out1 out2` |
| **hashclash** | MD5 选择前缀碰撞 | `hashclash prefix1 prefix2` |
| **hashcat** | 密码/哈希破解（GPU） | `hashcat -m MODE -a ATTACK hash wordlist` |
| **John the Ripper** | 密码破解（CPU/GPU） | `john --wordlist=rockyou.txt hashes.txt` |
| **CyberChef** | 快速哈希计算和编码 | 基于网页 |
