# Wycheproof

Wycheproof 是一个广泛的测试向量集合，旨在验证加密实现的正确性并测试已知攻击。它最初由 Google 开发，现在是一个社区管理的项目，贡献者可以为特定的加密构造添加测试向量。

## 背景

### 关键概念

| 概念 | 描述 |
|------|------|
| 测试向量 | 用于验证加密实现正确性的输入/输出对 |
| 测试组 | 具有相同属性（密钥大小、IV 大小、曲线）的测试向量集合 |
| 结果标志 | 指示测试是否应通过（有效）、失败（无效）或可接受 |
| 边缘情况测试 | 测试已知漏洞和攻击模式 |

### 为什么这很重要

加密实现 notoriously 难以正确实现。即使是很小的错误也可能：
- 暴露私钥
- 允许签名伪造
- 启用消息解密
- 当不同的实现接受/拒绝相同的输入时创建共识问题

Wycheproof 在包括 OpenJDK 的 SHA1withDSA、Bouncy Castle 的 ECDHC 和椭圆 npm 包在内的主要库中发现了漏洞。

## 何时使用

**应用 Wycheproof 时：**
- 测试加密实现（AES-GCM、ECDSA、ECDH、RSA 等）
- 验证加密代码正确处理边缘情况
- 验证实现针对已知攻击向量
- 为加密库设置 CI/CD
- 审计第三方加密代码的正确性

**考虑替代方案时：**
- 测试时间侧信道（使用常量时间测试工具）
- 查找新的未知错误（使用模糊测试）
- 测试自定义/实验性加密算法（Wycheproof 仅涵盖已建立的算法）

## 快速参考

| 场景 | 推荐方法 | 备注 |
|------|----------|------|
| AES-GCM 实现 | 使用 `aes_gcm_test.json` | 316 个测试向量跨 44 个测试组 |
| ECDSA 验证 | 使用 `ecdsa_*_test.json` 针对特定曲线 | 测试签名 malleability、DER 编码 |
| ECDH 密钥交换 | 使用 `ecdh_*_test.json` | 测试无效曲线攻击 |
| RSA 签名 | 使用 `rsa_*_test.json` | 测试填充 oracle 攻击 |
| ChaCha20-Poly1305 | 使用 `chacha20_poly1305_test.json` | 测试 AEAD 实现 |

## 测试工作流

```
阶段 1：设置                 阶段 2：解析测试向量
┌─────────────────┐          ┌─────────────────┐
│ 添加 Wycheproof  │    →     │ 加载 JSON 文件  │
│ 作为子模块      │          │ 按参数过滤      │
└─────────────────┘          └─────────────────┘
         ↓                            ↓
阶段 4：CI 集成        阶段 3：编写测试框架
┌─────────────────┐          ┌─────────────────┐
│ 自动更新       │    ←     │ 测试有效和    │
│ 测试向量      │          │ 无效情况       │
└─────────────────┘          └─────────────────┘
```

## 仓库结构

Wycheproof 仓库按以下方式组织：

```text
┣ 📜 README.md       : 项目概述
┣ 📂 doc             : 文档
┣ 📂 java            : Java JCE 接口测试框架
┣ 📂 javascript      : JavaScript 测试框架
┣ 📂 schemas         : 测试向量模式
┣ 📂 testvectors     : 测试向量
┗ 📂 testvectors_v1  : 更新后的测试向量（更详细）
```

基本文件夹是 `testvectors` 和 `testvectors_v1`。虽然两者都包含相似的文件，但 `testvectors_v1` 包含更详细的信息，并且建议用于新的集成。

## 支持的算法

Wycheproof 提供了广泛的加密算法的测试向量：

| 类别 | 算法 |
|------|------|
| **对称加密** | AES-GCM、AES-EAX、ChaCha20-Poly1305 |
| **签名** | ECDSA、EdDSA、RSA-PSS、RSA-PKCS1 |
| **密钥交换** | ECDH、X25519、X448 |
| **哈希** | HMAC、HKDF |
| **曲线** | secp256k1、secp256r1、secp384r1、secp521r1、ed25519、ed448 |

## 测试文件结构

每个 JSON 测试文件测试特定的加密构造。所有测试文件共享公共属性：

```json
"algorithm"         : 测试的算法名称
"schema"            : JSON 模式（在 schemas 文件夹中找到）
"generatorVersion"  : 版本号
"numberOfTests"     : 此文件中的测试向量总数
"header"            : 测试向量的详细描述
"notes"             : 测试向量中标志的深入解释
"testGroups"        : 一个或多个测试组的数组
```

### 测试组

测试组根据共享属性（如：
- 密钥大小
- IV 大小
- 公钥
- 曲线
）分组测试集。

这种分类允许提取与正在测试的构造相关的测试。

### 测试向量属性

#### 共享属性

所有测试向量包含四个公共字段：

- **tcId**: 在文件内唯一的测试向量标识符
- **comment**: 关于测试用例的附加信息
- **flags**: 描述特定测试用例类型和潜在危险的说明（参考 `notes` 字段）
- **result**: 测试的预期结果

`result` 字段可以取三个值：

| 结果 | 含义 |
|------|------|
| **valid** | 测试用例应成功 |
| **acceptable** | 测试用例允许成功但包含非理想属性 |
| **invalid** | 测试用例应失败 |

#### 独有属性

独有属性是针对正在测试的算法特定的：

| 算法 | 独有属性 |
|------|----------|
| AES-GCM | `key`、`iv`、`aad`、`msg`、`ct`、`tag` |
| ECDH secp256k1 | `public`、`private`、`shared` |
| ECDSA | `msg`、`sig`、`result` |
| EdDSA | `msg`、`sig`、`pk` |

## 实现指南

### 阶段 1：将 Wycheproof 添加到您的项目

**选项 1：Git 子模块（推荐）**

将 Wycheproof 作为 git 子模块添加可确保自动更新：

```bash
git submodule add https://github.com/C2SP/wycheproof.git
```

**选项 2：获取特定测试向量**

如果子模块不可行，则获取特定的 JSON 文件：

```bash
#!/bin/bash

TMP_WYCHEPROOF_FOLDER=".wycheproof/"
TEST_VECTORS=('aes_gcm_test.json' 'aes_eax_test.json')
BASE_URL="https://raw.githubusercontent.com/C2SP/wycheproof/master/testvectors_v1/"

# 创建 wycheproof 文件夹
mkdir -p $TMP_WYCHEPROOF_FOLDER

# 如果不存在，请求所有测试向量文件
for i in "${TEST_VECTORS[@]}"; do
  if [ ! -f "${TMP_WYCHEPROOF_FOLDER}${i}" ]; then
    curl -o "${TMP_WYCHEPROOF_FOLDER}${i}" "${BASE_URL}${i}"
    if [ $? -ne 0 ]; then
      echo "下载失败 ${i}"
      exit 1
    fi
  fi
done
```

### 阶段 2：解析测试向量

确定您的算法的测试文件并解析 JSON：

**Python 示例：**

```python
import json

def load_wycheproof_test_vectors(path: str):
    testVectors = []
    try:
        with open(path, "r") as f:
            wycheproof_json = json.loads(f.read())
    except FileNotFoundError:
        print(f"未找到 Wycheproof 文件：{path}")
        return testVectors

    # 需要十六进制到字节转换的属性
    convert_attr = {"key", "aad", "iv", "msg", "ct", "tag"}

    for testGroup in wycheproof_json["testGroups"]:
        # 根据实现约束过滤测试组
        if testGroup["ivSize"] < 64 or testGroup["ivSize"] > 1024:
            continue

        for tv in testGroup["tests"]:
            # 将十六进制字符串转换为字节
            for attr in convert_attr:
                if attr in tv:
                    tv[attr] = bytes.fromhex(tv[attr])
            testVectors.append(tv)

    return testVectors
```

**JavaScript 示例：**

```javascript
const fs = require('fs').promises;

async function loadWycheproofTestVectors(path) {
  const tests = [];

  try {
    const fileContent = await fs.readFile(path);
    const data = JSON.parse(fileContent.toString());

    data.testGroups.forEach(testGroup => {
      testGroup.tests.forEach(test => {
        // 将共享测试组属性添加到每个测试
        test['pk'] = testGroup.publicKey.pk;
        tests.push(test);
      });
    });
  } catch (err) {
    console.error('读取或解析文件错误：', err);
    throw err;
  }

  return tests;
}
```

### 阶段 3：编写测试框架

创建处理有效和无效测试用例的测试函数。

**Python/pytest 示例：**

```python
import pytest
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

tvs = load_wycheproof_test_vectors("wycheproof/testvectors_v1/aes_gcm_test.json")

@pytest.mark.parametrize("tv", tvs, ids=[str(tv['tcId']) for tv in tvs])
def test_encryption(tv):
    try:
        aesgcm = AESGCM(tv['key'])
        ct = aesgcm.encrypt(tv['iv'], tv['msg'], tv['aad'])
    except ValueError as e:
        # 实现引发错误 - 验证测试是否预期失败
        assert tv['result'] != 'valid', tv['comment']
        return

    if tv['result'] == 'valid':
        assert ct[:-16] == tv['ct'], f"密文不匹配：{tv['comment']}"
        assert ct[-16:] == tv['tag'], f"标签不匹配：{tv['comment']}"
    elif tv['result'] == 'invalid' or tv['result'] == 'acceptable':
        assert ct[:-16] != tv['ct'] or ct[-16:] != tv['tag']

@pytest.mark.parametrize("tv", tvs, ids=[str(tv['tcId']) for tv in tvs])
def test_decryption(tv):
    try:
        aesgcm = AESGCM(tv['key'])
        decrypted_msg = aesgcm.decrypt(tv['iv'], tv['ct'] + tv['tag'], tv['aad'])
    except ValueError:
        assert tv['result'] != 'valid', tv['comment']
        return
    except InvalidTag:
        assert tv['result'] != 'valid', tv['comment']
        assert 'ModifiedTag' in tv['flags'], f"预期 'ModifiedTag' 标志：{tv['comment']}"
        return

    assert tv['result'] == 'valid', f"不应通过无效测试：{tv['comment']}"
    assert decrypted_msg == tv['msg'], f"解密不匹配：{tv['comment']}"
```

**JavaScript/Mocha 示例：**

```javascript
const assert = require('assert');

function testFactory(tcId, tests) {
  it(`[${tcId + 1}] ${tests[tcId].comment}`, function () {
    const test = tests[tcId];
    const ed25519 = new eddsa('ed25519');
    const key = ed25519.keyFromPublic(toArray(test.pk, 'hex'));

    let sig;
    if (test.result === 'valid') {
      sig = key.verify(test.msg, test.sig);
      assert.equal(sig, true, `[${test.tcId}] ${test.comment}`);
    } else if (test.result === 'invalid') {
      try {
        sig = key.verify(test.msg, test.sig);
      } catch (err) {
        // 点无法解码
        sig = false;
      }
      assert.equal(sig, false, `[${test.tcId}] ${test.comment}`);
    }
  });
}

// 为所有测试向量生成测试
for (var tcId = 0; tcId < tests.length; tcId++) {
  testFactory(tcId, tests);
}
```

### 阶段 4：CI 集成

通过以下方式确保测试向量保持最新：

1. **使用 git 子模块**：在运行测试之前在 CI 中更新子模块
2. **获取最新向量**：在测试执行之前运行获取脚本
3. **计划更新**：设置每周/每月更新以捕获新的测试向量

## 常见漏洞检测

Wycheproof 测试向量旨在捕获特定的漏洞模式：

| 漏洞 | 描述 | 影响算法 | 示例 CVE |
|------|------|----------|----------|
| 签名 malleability | 相同消息的多个有效签名 | ECDSA、EdDSA | CVE-2024-42459 |
| 无效 DER 编码 | 接受非规范 DER 签名 | ECDSA | CVE-2024-42460, CVE-2024-42461 |
| 无效曲线攻击 | 使用无效曲线点的 ECDH | ECDH | 许多库中常见 |
| 填充 oracle | 填充验证中的时间泄漏 | RSA-PKCS1 | 历史 OpenSSL 问题 |
| 标签伪造 | 接受修改的认证标签 | AES-GCM、ChaCha20-Poly1305 | 各种实现 |

### 签名 malleability：深入分析

**问题**：未验证签名编码的实现可以接受相同消息的多个有效签名。

**示例（EdDSA）**：签名添加或删除零：
```text
有效签名：   ...6a5c51eb6f946b30d
无效签名： ...6a5c51eb6f946b30d0000  （应被拒绝）
```

**如何检测：**
```python
# 添加签名长度检查
if len(sig) != 128:  # EdDSA 签名必须正好是 64 字节（128 十六进制字符）
    return False
```

**影响**：可能导致不同实现接受/拒绝相同签名时的共识问题。

**相关 Wycheproof 测试：**
- EdDSA：tcId 37 - "从签名中删除 0 字节"
- ECDSA：tcId 06 - "传统：r 的 ASN 编码缺少前导 0"

## 案例研究：Elliptic npm 包

本案例研究展示了 Wycheproof 如何在流行的 elliptic npm 包（3000+ 依赖项，每周数百万次下载）中发现三个 CVE。

### 概述

[elliptic](https://www.npmjs.com/package/elliptic) 库是一个用 JavaScript 编写的椭圆曲线密码学库，支持 ECDH、ECDSA 和 EdDSA。使用 Wycheproof 测试向量在版本 6.5.6 上发现多个漏洞：

- **CVE-2024-42459**：EdDSA 签名 malleability（添加/删除零）
- **CVE-2024-42460**：ECDSA DER 编码 - 无效位放置
- **CVE-2024-42461**：ECDSA DER 编码 - 长度字段中的前导零

### 方法论

1. **确定支持的曲线**：ed25519 用于 EdDSA
2. **查找测试向量**：`testvectors_v1/ed25519_test.json`
3. **解析测试向量**：加载 JSON 并提取测试
4. **编写测试框架**：创建参数化测试
5. **运行测试**：识别失败
6. **分析根本原因**：检查实现代码
7. **提出修复方案**：添加验证检查

### 关键发现

**EdDSA 问题 (CVE-2024-42459)：**
- 缺少签名长度验证
- 允许签名中的尾随零
- 修复：添加 `if(sig.length !== 128) return false;`

**ECDSA 问题 1 (CVE-2024-42460)：**
- 缺少检查 DER 编码的 r 和 s 值的第一位是否为零
- 修复：添加 `if ((data[p.place] & 128) !== 0) return false;`

**ECDSA 问题 2 (CVE-2024-42461)：**
- DER 长度字段接受前导零
- 修复：添加 `if(buf[p.place] === 0x00) return false;`

### 影响

所有三个漏洞允许对单个消息进行多个有效签名，导致不同实现之间的共识问题。

**经验教训：**
- Wycheproof 捕获微妙的编码错误
- 可重用测试框架带来回报
- 测试向量注释和标志有助于诊断问题
- 即使是流行库也受益于系统测试向量验证

## 高级用法

### 提示和技巧

| 提示 | 有何帮助 |
|------|----------|
| 按参数过滤测试组 | 专注于与您的实现约束相关的测试向量 |
| 使用测试向量标志 | 了解正在测试的特定漏洞模式 |
| 检查 `notes` 字段 | 获取标志含义的详细解释 |
| 测试加密/解密和签名/验证 | 确保双向正确性 |
| 在 CI 中运行测试 | 捕获回归并受益于新的测试向量 |
| 使用参数化测试 | 获取带有 tcId 和注释的清晰失败消息 |

### 常见错误

| 错误 | 为什么不正确 | 正确方法 |
|------|--------------|----------|
| 仅测试有效情况 | 错过接受无效输入的漏洞 | 测试所有结果类型：valid、invalid、acceptable |
| 忽略 "acceptable" 结果 | 实现可能存在微妙的错误 | 将 acceptable 视为值得调查的警告 |
| 不过滤测试组 | 浪费时间在不支持的参数上 | 根据keySize、ivSize等过滤基于您的实现 |
| 不更新测试向量 | 错过新的漏洞模式 | 使用子模块或计划获取 |
| 仅测试一个方向 | 加密/签名可能工作但解密/验证失败 | 测试两个操作 |

## 相关技能

### 工具技能

| 技能 | 在 Wycheproof 测试中的主要用途 |
|------|--------------------------------|
| **pytest** | Python 测试框架用于参数化测试 |
| **mocha** | JavaScript 测试框架用于生成测试 |
| **常量时间测试** | 与 Wycheproof 结合进行时间侧信道测试 |
| **cryptofuzz** | 基于模糊的加密测试以找到附加错误 |

### 技术技能

| 技能 | 何时应用 |
|------|----------|
| **覆盖率分析** | 确保测试向量覆盖加密实现中的所有代码路径 |
| **属性基础测试** | 测试数学属性（例如，加密/解密往返） |
| **模糊测试框架编写** | 创建加密解析器的框架（补充 Wycheproof） |

### 相关领域技能

| 技能 | 关系 |
|------|------|
| **加密测试** | Wycheproof 是综合加密测试方法学中的一个关键工具 |
| **模糊测试** | 使用模糊测试查找 Wycheproof 未涵盖的漏洞（新的边缘情况） |

## 技能依赖图

```
                    ┌─────────────────────┐
                    │    wycheproof       │
                    │   (此技能)      │
                    └──────────┬──────────┘
                               │
           ┌───────────────────┼───────────────────┐
           │                   │                   │
           ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  pytest/mocha   │ │ constant-time   │ │   cryptofuzz    │
│ (测试框架)      │ │   测试       │ │   (模糊测试)     │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
                             ▼
              ┌──────────────────────────┐
              │   技术技能       │
              │ 覆盖率、框架、PBT   │
              └──────────────────────────┘
```

## 资源

### 官方仓库

**[Wycheproof GitHub 仓库](https://github.com/C2SP/wycheproof)**

官方仓库包含：
- `testvectors/` 和 `testvectors_v1/` 中的所有测试向量
- `schemas/` 中的 JSON 模式
- Java 和 JavaScript 中的参考实现
- `doc/` 中的文档

### 真实案例

**[pycryptodome](https://pypi.org/project/pycryptodome/)**

pycryptodome 库在其测试套件中集成了 Wycheproof 测试向量，展示了 Python 加密实现的最佳实践。

### 社区资源

- [C2SP 社区](https://c2sp.org/) - 维护 Wycheproof 的密码学规范和标准社区
- Wycheproof 问题跟踪器 - 报告测试向量中的错误或建议新的构造

## 总结

Wycheproof 是验证加密实现针对已知攻击向量和边缘情况的一个基本工具。通过将 Wycheproof 测试向量集成到您的测试工作流中：

1. 捕获微妙的编码和验证错误
2. 防止签名 malleability 问题
3. 确保不同实现的一致行为
4. 受益于社区贡献的测试向量
5. 保护免受已知加密漏洞的影响

在编写可重用的测试框架方面的投资通过 Wycheproof 仓库中添加的新测试向量进行持续验证而得到回报。
