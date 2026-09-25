# 锐边分析

评估 API、配置和界面是否对开发者误用具有抵抗力。识别那些“捷径”导致不安全的架构设计。

## 使用场景

- 审查 API 或库的设计决策
- 审计配置模式中的危险选项
- 评估加密 API 的易用性
- 评估身份验证/授权界面
- 审查任何将与安全相关的选择暴露给开发者的代码

## 不适用场景

- 实现错误（使用标准代码审查）
- 业务逻辑缺陷（使用特定领域分析）
- 性能优化（不同关注点）

## 代理

`sharp-edges-analyzer` 代理会自主运行完整的锐边分析工作流程。当你需要专门分析 API、配置或界面对于误用抵抗和潜在陷阱风险时使用它。该代理遵循四阶段工作流程（表面识别、边缘案例探测、威胁建模、验证发现），并根据需要读取语言特定的参考信息。

## 核心原则

**成功陷阱**：安全的使用应该是阻力最小的路径。如果开发者必须理解加密、仔细阅读文档或记住特殊规则来避免漏洞，那么 API 就失败了。

## 拒绝的理由

| 理由 | 为什么错误 | 必要行动 |
|------|----------|----------|
| “有文档” | 开发者在截止日期压力下不会阅读文档 | 将安全选择设为默认或唯一选项 |
| “高级用户需要灵活性” | 灵活性会制造陷阱；大多数“高级”用法是复制粘贴 | 提供安全的高级 API；隐藏原始操作 |
| “这是开发者的责任” | 推卸责任；你设计了陷阱 | 移除陷阱或使其无法被误用 |
| “实际上没人会这么做” | 开发者在压力下会做任何事情 | 假设开发者最大程度的困惑 |
| “只是一个配置选项” | 配置就是代码；错误的配置会发往生产环境 | 验证配置；拒绝危险的组合 |
| “我们需要向后兼容” | 不安全的默认值不能被“祖父条款”豁免 | 大声弃用；强制迁移 |

## 锐边类别

### 1. 算法/模式选择陷阱

允许开发者选择算法的 API 会招致选择错误算法。

**JWT 模式**（典型示例）：
- 头部指定算法：攻击者可以设置 `"alg": "none"` 来绕过签名
- 算法混淆：在切换 RS256→HS256 时，RSA 公钥被用作 HMAC 密钥
- 根本原因：让不受信任的输入控制安全关键决策

**检测模式**：
- 函数参数如 `algorithm`、`mode`、`cipher`、`hash_type`
- 枚举/字符串选择加密原语
- 安全机制配置选项

**示例 - PHP password_hash 允许弱算法**：
```php
// 危险：允许 crc32、md5、sha1
password_hash($password, PASSWORD_DEFAULT); // 好 - 无选择
hash($algorithm, $password); // BAD：接受 "crc32"
```

### 2. 危险默认值

不安全的默认值，或零/空值禁用安全功能。

**OTP 生命周期模式**：
```python
# 当 lifetime=0 时会发生什么？
def verify_otp(code, lifetime=300):  # 300 秒默认值
    if lifetime == 0:
        return True  # OOPS：0 表示“接受所有”？
        # 或者它表示“立即过期”？
```

**检测模式**：
- 接受 0 的超时/生命周期（无限？立即过期？）
- 空字符串绕过检查
- 空值跳过验证
- 布尔默认值禁用安全功能
- 负值具有未定义的含义

**需要询问的问题**：
- `timeout=0` 会发生什么？`max_attempts=0`？`key=""`？
- 默认值是最安全的选择吗？
- 任何默认值都能完全禁用安全功能吗？

### 3. 原语与语义 API

暴露原始字节而不是有意义类型的 API 会招致类型混淆。

**Libsodium 与 Halite 模式**：

```php
// Libsodium（原语）：字节就是字节
sodium_crypto_box($message, $nonce, $keypair);
// 容易：交换 nonce/keypair、重用 nonce、使用错误类型的密钥

// Halite（语义）：类型强制正确使用
Crypto::seal($message, new EncryptionPublicKey($key));
// 错误的密钥类型 = 类型错误，不是静默失败
```

**检测模式**：
- 接受 `bytes`、`string`、`[]byte` 用于不同安全概念的函数
- 可以无类型错误交换的参数
- 相同类型用于密钥、nonce、密文、签名

**比较陷阱**：
```go
// 时序安全的比较看起来与不安全相同
if hmac == expected { }           // BAD：时序攻击
if hmac.Equal(mac, expected) { }  // 好：常数时间
// 相同类型，不同安全属性
```

### 4. 配置悬崖

一个错误设置会导致灾难性失败，且没有警告。

**检测模式**：
- 完全禁用安全的布尔标志
- 未验证的字符串配置
- 危险地交互的设置组合
- 覆盖安全设置的環境变量
- 构造函数参数具有合理默认值但无验证（调用者可以用不安全的值覆盖）

**示例**：
```yaml
# 一个拼写错误 = 灾难
verify_ssl: fasle  # 拼写错误被静默接受为 truthy？

# 魔术值
session_timeout: -1  # 这意味着“永不过期”？

# 危险组合被静默接受
auth_required: true
bypass_auth_for_health_checks: true
health_check_path: "/"  # 哦
```

```php
// 合理默认值无法保护调用者
public function __construct(
    public string $hashAlgo = 'sha256',  // 好 - 无选择...
    public int $otpLifetime = 120,       // ...但接受 md5、0 等
) {}
```

见 [config-patterns.md](references/config-patterns.md#unvalidated-constructor-parameters) 获取详细模式。

### 5. 静默失败

不显示的错误，或成功掩盖了失败。

**检测模式**：
- 返回布尔值的函数而不是在安全失败时抛出
- 安全操作周围的空 catch 块
- 解析错误时使用默认值
- 验证函数在格式化输入上“成功”

**示例**：
```python
# 静默绕过
def verify_signature(sig, data, key):
    if not key:
        return True  # 无密钥 = 跳过验证?!

# 返回值被忽略
signature.verify(data, sig)  # 失败时抛出
crypto.verify(data, sig)     # 失败时返回 False
# 开发者忘记检查返回值
```

### 6. 字符串类型安全

作为普通字符串的安全关键值会启用注入和混淆。

**检测模式**：
- 从字符串连接构建的 SQL/命令
- 权限作为逗号分隔的字符串
- 角色范围作为任意字符串而不是枚举
- 由字符串连接构建的 URL

**权限累积陷阱**：
```python
permissions = "read,write"
permissions += ",admin"  # 太容易升级

# vs. 类型安全
permissions = {Permission.READ, Permission.WRITE}
permissions.add(Permission.ADMIN)  # 至少它是明确的
```

## 分析工作流程

### 第一阶段：表面识别

1. **映射与安全相关的 API**：身份验证、授权、加密、会话管理、输入验证
2. **识别开发者选择点**：开发者可以在哪里选择算法、配置超时、选择模式？
3. **查找配置模式**：环境变量、配置文件、构造函数参数

### 第二阶段：边缘案例探测

对于每个选择点，询问：
- **零/空/空值**：`0`、`""`、`null`、`[]` 会发生什么？
- **负值**：`-1` 意味着什么？无限？错误？
- **类型混淆**：不同安全概念可以交换吗？
- **默认值**：默认值安全吗？有文档吗？
- **错误路径**：无效输入时会发生什么？静默接受？

### 第三阶段：威胁建模

考虑三个对手：

1. **无赖**：主动恶意开发者或攻击者控制配置
   - 他们能通过配置禁用安全吗？
   - 他们能降级算法吗？
   - 他们能注入恶意值吗？

2. **懒惰的开发者**：复制粘贴示例，跳过文档
   - 他们找到的第一个示例会安全吗？
   - 最低阻力路径安全吗？
   - 错误信息是否引导安全使用？

3. **困惑的开发者**：误解 API
   - 他们能无类型错误地交换参数吗？
   - 他们能意外使用错误的密钥/算法/模式吗？
   - 失败模式明显还是静默？

### 第四阶段：验证发现

对于每个识别的锐边：

1. **重现误用**：编写最小代码演示陷阱
2. **验证可利用性**：误用是否创建真实漏洞？
3. **检查文档**：危险被记录了吗？（文档不能原谅糟糕设计，但影响严重性）
4. **测试缓解措施**：API 是否可以通过合理努力安全使用？

如果一个发现看起来可疑，返回第二阶段探测更多边缘案例。

## 严重性分类

| 严重性 | 标准 | 示例 |
|------|------|------|
| 危急 | 默认或明显使用不安全 | `verify: false` 默认；允许空密码 |
| 高 | 容易配置错误破坏安全 | 算法参数接受 "none" |
| 中 | 不寻常但可能的配置错误 | 负超时有未定义含义 |
| 低 | 需要故意误用 | 奇怪的参数组合 |

## 参考文献

**按类别**：

- **加密 API**：见 [references/crypto-apis.md](references/crypto-apis.md)
- **配置模式**：见 [references/config-patterns.md](references/config-patterns.md)
- **身份验证/会话**：见 [references/auth-patterns.md](references/auth-patterns.md)
- **真实世界案例研究**：见 [references/case-studies.md](references/case-studies.md)（OpenSSL、GMP 等）

**按语言**（通用陷阱，非特定加密）：

| 语言 | 指南 |
|------|------|
| C/C++ | [references/lang-c.md](references/lang-c.md) |
| Go | [references/lang-go.md](references/lang-go.md) |
| Rust | [references/lang-rust.md](references/lang-rust.md) |
| Swift | [references/lang-swift.md](references/lang-swift.md) |
| Java | [references/lang-java.md](references/lang-java.md) |
| Kotlin | [references/lang-kotlin.md](references/lang-kotlin.md) |
| C# | [references/lang-csharp.md](references/lang-csharp.md) |
| PHP | [references/lang-php.md](references/lang-php.md) |
| JavaScript/TypeScript | [references/lang-javascript.md](references/lang-javascript.md) |
| Python | [references/lang-python.md](references/lang-python.md) |
| Ruby | [references/lang-ruby.md](references/lang-ruby.md) |

另见 [references/language-specific.md](references/language-specific.md) 获取综合快速参考。

## 质量检查清单

在完成分析前：

- [ ] 探测所有零/空/空值边缘案例
- [ ] 验证默认值安全
- [ ] 检测算法/模式选择陷阱
- [ ] 测试安全概念之间的类型混淆
- [ ] 考虑所有三个对手类型
- [ ] 验证错误路径不会绕过安全
- [ ] 检查配置验证
- [ ] 构造函数参数验证（不只是默认值） - 见 [config-patterns.md](references/config-patterns.md#unvalidated-constructor-parameters)
