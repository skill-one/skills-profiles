# 技能：对称密码攻击 — 专家密码分析 playbook

> **AI 加载指令**：CTF 和授权测试中攻击对称加密的专家技术。涵盖 CBC 填充预言机、CBC 位翻转、ECB 检测和利用、流密码密钥重用、LFSR/LCG 状态恢复、RC4 偏差以及中间相遇攻击。基础模型通常混淆 ECB 和 CBC 攻击策略，或未能正确设置字节逐个 ECB 解密。

## 0. 相关路由

- [rsa-attack-techniques](../rsa-attack-techniques/SKILL.md) 当对称密钥受 RSA 保护时
- [hash-attack-techniques](../hash-attack-techniques/SKILL.md) 当涉及 HMAC 或基于哈希的认证时
- [lattice-crypto-attacks](../lattice-crypto-attacks/SKILL.md) 通过格方法进行 LCG/LFSR 状态恢复

### 高级参考

当您需要以下内容时，也加载 [BLOCK_CIPHER_ATTACKS.md](./BLOCK_CIPHER_ATTACKS.md)：
- 带有完整 Python 实现的详细攻击脚本
- 字节逐个 ECB 的逐步演练
- PadBuster 使用和自定义填充预言机脚本
- LCG/LFSR 恢复实现

### 快速攻击选择

| 可观察行为 | 可能的弱点 | 攻击 |
|---|---|---|
| 相同的明文 → 相同的密文（块对齐） | ECB 模式 | 切割粘贴 / 字节逐个 |
| 填充错误可区分 | CBC 填充预言机 | 无需密钥解密 |
| 可以修改密文，影响下一个块 | CBC 模式，无完整性检查 | 位翻转 |
| 密钥与 XOR/流密码重用 | 两次加密 | XOR 密文 |
| 可预测的 PRNG 输出 | LCG 或 LFSR | 状态恢复 |
| 使用双重加密 | 类似 2DES | 中间相遇 |

---

## 1. 填充预言机攻击（CBC 模式）

### 1.1 机制

CBC 解密：`P_i = D_K(C_i) ⊕ C_{i-1}`

如果服务器揭示填充是否有效（PKCS#7），我们可以通过操纵前一个密文块来解密任何块。

### 1.2 攻击步骤

```
目标：解密块 C_i（明文 P_i 未知）

对于字节位置 b = 15 降至 0（最后一个字节优先）：
  填充值 = 16 - b
  
  对于猜测 = 0x00 到 0xFF：
    构造修改后的 C'_{i-1}：
      - 字节 0..b-1：原始 C_{i-1} 字节
      - 字节 b：猜测
      - 字节 b+1..15：计算以产生正确的填充
    
    将 (C'_{i-1} || C_i) 发送到预言机
    
    如果预言机说“填充有效”：
      intermediate_byte[b] = 猜测 ⊕ 填充值
      plaintext_byte[b] = intermediate_byte[b] ⊕ 原始 C_{i-1}[b]
```

### 1.3 Python 实现

```python
def padding_oracle_attack(ciphertext, block_size, oracle):
    """
    oracle(ct) 返回 True 如果填充有效，否则返回 False。
    ciphertext 包括 IV 作为第一个块。
    """
    blocks = [ciphertext[i:i+block_size] for i in range(0, len(ciphertext), block_size)]
    plaintext = b""

    for block_idx in range(1, len(blocks)):
        prev_block = bytearray(blocks[block_idx - 1])
        curr_block = blocks[block_idx]
        intermediate = [0] * block_size
        decrypted = [0] * block_size

        for byte_pos in range(block_size - 1, -1, -1):
            padding_val = block_size - byte_pos

            for guess in range(256):
                modified = bytearray(block_size)
                modified[byte_pos] = guess

                for j in range(byte_pos + 1, block_size):
                    modified[j] = intermediate[j] ^ padding_val

                test_ct = bytes(modified) + curr_block
                if oracle(test_ct):
                    if byte_pos == block_size - 1:
                        # 验证不是误报（填充 0x02 0x02）
                        check = bytearray(modified)
                        check[byte_pos - 1] ^= 1
                        if not oracle(bytes(check) + curr_block):
                            continue

                    intermediate[byte_pos] = guess ^ padding_val
                    decrypted[byte_pos] = intermediate[byte_pos] ^ prev_block[byte_pos]
                    break

        plaintext += bytes(decrypted)

    return plaintext
```

### 1.4 工具

```bash
# PadBuster
padbuster http://target/decrypt?ct= CIPHERTEXT_HEX 16 -encoding 0
padbuster http://target/decrypt?ct= CIPHERTEXT_HEX 16 -encoding 0 -plaintext "admin=true"
```

---

## 2. CBC 位翻转

### 2.1 概念

在 C_{i-1} 的位置 j 处翻转位会翻转 P_i 中相同位置的位（并损坏所有 P_{i-1}）。

```
原始：  P_i[j] = D_K(C_i)[j] ⊕ C_{i-1}[j]
修改后：  P'_i[j] = D_K(C_i)[j] ⊕ C'_{i-1}[j]
                    = P_i[j] ⊕ (C_{i-1}[j] ⊕ C'_{i-1}[j])
```

### 2.2 实际示例

```python
def cbc_bitflip(ciphertext, block_size, target_byte_pos, old_value, new_value):
    """
    通过修改密文块 N 来翻转明文块 N+1 中的字节。
    target_byte_pos：明文中的绝对位置（0 索引）
    """
    ct = bytearray(ciphertext)
    block_num = target_byte_pos // block_size
    byte_in_block = target_byte_pos % block_size

    # 修改前一个块（块号 block_num - 1）以翻转目标字节
    modify_pos = (block_num - 1) * block_size + byte_in_block

    # XOR 以取消旧值并设置新值
    ct[modify_pos] ^= old_value ^ new_value
    return bytes(ct)

# 示例：将 "admin=0" 翻转为 "admin=1"
# 如果 "admin=0" 位于字节位置 22（块 1，字节 6）：
modified_ct = cbc_bitflip(ciphertext, 16, 22, ord('0'), ord('1'))
```

---

## 3. ECB 模式攻击

### 3.1 检测

```python
def detect_ecb(ciphertext, block_size=16):
    """ECB 产生相同的明文块对应相同的密文块。"""
    blocks = [ciphertext[i:i+block_size] for i in range(0, len(ciphertext), block_size)]
    return len(blocks) != len(set(blocks))

# 强制检测：发送重复的明文
test_input = b"A" * 48  # 至少 3 个相同的块数据
# 如果响应有重复的块 → ECB
```

### 3.2 ECB 切割粘贴

重新排序密文块以创建新的有效明文。

```
原始块：
  块 0： "email=foo@bar.c"
  块 1： "om&role=user&uid"
  块 2： "=10\x0d\x0d\x0d..."

攻击：构造输入，使 "admin" + 填充位于其自己的块中，
然后将其放置在 "user" 块的位置。

步骤 1：发送对齐 "admin" + PKCS7 的邮件：
  email = "foo@bar.coadmin\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b"
  → 块 1 加密为 "admin\x0b\x0b..."（保存此块）

步骤 2：发送将 "role=" 放在块末尾的邮件：
  email = "foo@bar.co"
  → 块 2 = "=user&uid=10..."（但我们替换这个）

步骤 3：用保存的 "admin\x0b..." 块替换最后一个块
```

### 3.3 字节逐个 ECB 解密

逐字节解密未知附加的密钥。

```python
def ecb_byte_at_a_time(encrypt_oracle, block_size=16):
    """
    encrypt_oracle(input_bytes) = AES_ECB(input || unknown_secret)
    返回 unknown_secret。
    """
    secret = b""
    secret_len = len(encrypt_oracle(b"")) 

    for i in range(secret_len):
        block_num = i // block_size
        pad_len = block_size - 1 - (i % block_size)
        padding = b"A" * pad_len

        # 构建查找表
        target_ct = encrypt_oracle(padding)
        target_block = target_ct[block_num * block_size:(block_num + 1) * block_size]

        for byte_val in range(256):
            test_input = padding + secret + bytes([byte_val])
            test_ct = encrypt_oracle(test_input)
            test_block = test_ct[block_num * block_size:(block_num + 1) * block_size]

            if test_block == target_block:
                secret += bytes([byte_val])
                break

    return secret
```

---

## 4. 流密码攻击

### 4.1 已知明文 / 密钥重用（两次加密）

```python
def two_time_pad(c1, c2, known_crib=None):
    """
    c1 = m1 ⊕ K, c2 = m2 ⊕ K (相同的密钥 K)
    c1 ⊕ c2 = m1 ⊕ m2 (密钥抵消)
    """
    xored = bytes(a ^ b for a, b in zip(c1, c2))

    if known_crib:
        results = []
        for offset in range(len(xored) - len(known_crib) + 1):
            candidate = bytes(
                xored[offset + i] ^ known_crib[i] for i in range(len(known_crib))
            )
            if all(0x20 <= b <= 0x7e for b in candidate):
                results.append((offset, candidate))
        return results
    return xored
```

### 4.2 单字节 XOR 暴力破解

```python
def single_byte_xor_crack(ciphertext):
    """使用频率分析暴力破解单字节 XOR 密钥。"""
    english_freq = {
        'e': 12.7, 't': 9.1, 'a': 8.2, 'o': 7.5, 'i': 7.0,
        'n': 6.7, 's': 6.3, 'h': 6.1, 'r': 6.0, 'd': 4.3,
    }
    best_score, best_key, best_plaintext = 0, 0, b""

    for key in range(256):
        plaintext = bytes(b ^ key for b in ciphertext)
        score = sum(
            english_freq.get(chr(b).lower(), 0)
            for b in plaintext if 0x20 <= b <= 0x7e
        )
        if score > best_score:
            best_score = score
            best_key = key
            best_plaintext = plaintext

    return best_key, best_plaintext
```

### 4.3 重复密钥 XOR（类似 Kasiski）

```python
def repeating_xor_crack(ciphertext, max_keylen=40):
    """使用汉明距离破解重复密钥 XOR（密钥长度）。"""
    def hamming(a, b):
        return sum(bin(x ^ y).count('1') for x, y in zip(a, b))

    # 查找密钥长度
    scores = []
    for kl in range(2, max_keylen + 1):
        blocks = [ciphertext[i:i+kl] for i in range(0, len(ciphertext) - kl, kl)]
        if len(blocks) < 4:
            continue
        dist = sum(hamming(blocks[i], blocks[i+1]) for i in range(min(3, len(blocks)-1)))
        normalized = dist / (min(3, len(blocks)-1) * kl)
        scores.append((normalized, kl))

    best_keylen = sorted(scores)[0][1]

    # 用单字节 XOR 破解每个位置
    key = b""
    for i in range(best_keylen):
        column = bytes(ciphertext[j] for j in range(i, len(ciphertext), best_keylen))
        k, _ = single_byte_xor_crack(column)
        key += bytes([k])

    return key
```

### 4.4 LFSR 状态恢复（Berlekamp-Massey）

```python
def berlekamp_massey_gf2(output_bits):
    """从输出序列恢复 LFSR 反馈多项式（GF(2)）。"""
    n = len(output_bits)
    C = [0] * (n + 1)
    B = [0] * (n + 1)
    C[0] = B[0] = 1
    L = 0
    m = 1
    b = 1

    for N in range(n):
        d = output_bits[N]
        for i in range(1, L + 1):
            d ^= C[i] & output_bits[N - i]

        if d == 0:
            m += 1
        elif 2 * L <= N:
            T = C[:]
            for i in range(m, n + 1):
                C[i] ^= B[i - m]
            L = N + 1 - L
            B = T
            b = d
            m = 1
        else:
            for i in range(m, n + 1):
                C[i] ^= B[i - m]
            m += 1

    return C[:L + 1], L
```

### 4.5 RC4 偏差

| 偏差 | 描述 | 利用 |
|---|---|---|
| 初始字节偏差 | P(K[0] = 0) ≈ 2/256（双倍正常） | 统计明文恢复第一个字节 |
| Fluhrer-Mantin-Shamir | 弱密钥调度与 IV | WEP 攻击（历史） |
| NOMORE 攻击 | 密钥流中的长期偏差 | TLS/RC4 明文恢复（2^24-2^26 密文） |
| 不变性弱点 | 整个流中的密钥相关偏差 | 对多次加密进行统计攻击 |

---

## 5. 中间相遇

### 5.1 双重加密攻击

```
双重加密：C = E_K2(E_K1(P))
暴力破解：预期 2^(2n)
MITM：        2^(n+1) + 存储 2^n 条目

攻击：
1. 用所有可能的 K1 加密 P → 存储 (E_K1(P), K1) 在表中
2. 用所有可能的 K2 解密 C → 检查 D_K2(C) 是否匹配任何条目
3. 匹配找到 → (K1, K2) 恢复
```

```python
from itertools import product

def meet_in_the_middle(encrypt, decrypt, plaintext, ciphertext, keyspace_bits):
    """MITM 攻击双重加密。"""
    # 第一阶段：构建加密表
    enc_table = {}
    for k1 in range(2**keyspace_bits):
        intermediate = encrypt(plaintext, k1)
        enc_table[intermediate] = k1

    # 第二阶段：解密并查找
    for k2 in range(2**keyspace_bits):
        intermediate = decrypt(ciphertext, k2)
        if intermediate in enc_table:
            k1 = enc_table[intermediate]
            return k1, k2

    return None
```

---

## 6. 决策树

```
对称密码挑战 — 你能观察到什么？
│
├─ 能否检测模式？
│  ├─ 相同输入 → 相同输出块？
│  │  └─ 是 → ECB 模式
│  │     ├─ 能控制前缀 → 字节逐个解密
│  │     ├─ 能重新排序块 → 切割粘贴
│  │     └─ 能检测块边界 → 块对齐预言机
│  │
│  ├─ 错误消息因填充错误而不同？
│  │  └─ 是 → 填充预言机（CBC）
│  │     └─ PadBuster 或自定义脚本
│  │
│  └─ 能否修改密文并观察效果？
│     └─ 下一个块明文变化 → CBC 位翻转
│
├─ 流密码或 XOR？
│  ├─ 密钥在不同消息中重用？
│  │  └─ XOR 密文 → 串联拖动
│  │
│  ├─ 已知明文-密文对？
│  │  └─ 直接恢复密钥流
│  │
│  ├─ 单字节 XOR 密钥？
│  │  └─ 暴力破解 256 个密钥，使用频率分析
│  │
│  ├─ 重复密钥 XOR？
│  │  └─ 汉明距离 → 密钥长度 → 每个位置的破解
│  │
│  └─ 基于 LFSR？
│     └─ Berlekamp-Massey 用于状态/多项式恢复
│
├─ 基于 PRNG 的密码？
│  ├─ LCG → 截断输出格攻击
│  ├─ Mersenne Twister → 624 输出 → 完全状态恢复
│  └─ 自定义 PRNG → 分析周期和状态大小
│
├─ 双重 / 三重加密？
│  └─ 中间相遇
│
└─ RC4 特定？
   ├─ 单重加密 → 初始字节偏差
   ├─ 多次加密相同密钥 → 统计攻击
   └─ IV 预先附加到密钥 → FMS 攻击（类似 WEP）
```

---

## 7. 工具

| 工具 | 目的 |
|---|---|
| **PadBuster** | 自动化填充预言机利用 |
| **xortool** | 重复密钥 XOR 分析（密钥长度检测 + 破解） |
| **CyberChef** | 快速 XOR、编码、块密码操作 |
| **SageMath** | LFSR/LCG 分析，基于格的恢复 |
| **pycryptodome** | AES/DES 实现，用于测试 |
| **hashcat** | 暴力破解对称密钥（GPU 加速） |
| **自定义 Python** | 上述所有攻击可在纯 Python 中实现 |
