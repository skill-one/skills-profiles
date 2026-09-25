# PCI 合规

掌握 PCI DSS（支付卡行业数据安全标准）合规性，以确保安全的支付处理和持卡人数据的处理。

## 使用此技能的场景

- 构建支付处理系统
- 处理信用卡信息
- 实施安全的支付流程
- 进行 PCI 合规审计
- 缩小 PCI 合规范围
- 实施令牌化和加密
- 准备 PCI DSS 评估

## PCI DSS 要求（12 核心要求）

### 构建和维护安全网络

1. 安装和维护防火墙配置
2. 不要使用供应商提供的默认密码

### 保护持卡人数据

3. 保护存储的持卡人数据
4. 对公共网络上传输的持卡人数据进行加密

### 维护漏洞管理

5. 保护系统免受恶意软件的侵害
6. 开发和维护安全的系统和应用程序

### 实施强访问控制

7. 根据业务需要限制对持卡人数据的访问
8. 识别和验证系统组件的访问
9. 限制对持卡人数据的物理访问

### 监控和测试网络

10. 跟踪和监控对网络资源和持卡人数据的所有访问
11. 定期测试安全系统和流程

### 维护信息安全策略

12. 维护一项解决信息安全问题的策略

## 合规级别

**级别 1**：每年 > 600 万笔交易（需要年度 ROC）
**级别 2**：每年 1-600 万笔交易（需要年度 SAQ）
**级别 3**：每年 20,000-1,000 万笔电子商务交易
**级别 4**：< 20,000 笔电子商务交易或 < 1,000 万笔总交易

## 数据最小化（永远不要存储）

```python
# 永远不要存储这些
PROHIBITED_DATA = {
    'full_track_data': '磁条数据',
    'cvv': '卡片验证码/值',
    'pin': 'PIN 或 PIN 块'
}

# 可以存储（如果加密）
ALLOWED_DATA = {
    'pan': '主要账户号码（卡号）',
    'cardholder_name': '卡片上的姓名',
    'expiration_date': '卡片到期日',
    'service_code': '服务代码'
}

class PaymentData:
    """安全处理支付数据。"""

    def __init__(self):
        self.prohibited_fields = ['cvv', 'cvv2', 'cvc', 'pin']

    def sanitize_log(self, data):
        """从日志中移除敏感数据。"""
        sanitized = data.copy()

        # 掩码 PAN
        if 'card_number' in sanitized:
            card = sanitized['card_number']
            sanitized['card_number'] = f"{card[:6]}{'*' * (len(card) - 10)}{card[-4:]}"

        # 移除禁止存储的数据
        for field in self.prohibited_fields:
            sanitized.pop(field, None)

        return sanitized

    def validate_no_prohibited_storage(self, data):
        """确保没有存储禁止的数据。"""
        for field in self.prohibited_fields:
            if field in data:
                raise SecurityError(f"尝试存储禁止字段：{field}")
```

## 令牌化

### 使用支付处理器令牌

```python
import stripe

class TokenizedPayment:
    """使用令牌处理支付（服务器上没有卡数据）。"""

    @staticmethod
    def create_payment_method_token(card_details):
        """从卡详情创建令牌（仅客户端）。"""
        # 这应该只在客户端使用 STRIPE.JS 完成
        # 永远不要将卡数据发送到你的服务器

        """
        // 前端 JavaScript
        const stripe = Stripe('pk_...');

        const {token, error} = await stripe.createToken({
            card: {
                number: '4242424242424242',
                exp_month: 12,
                exp_year: 2024,
                cvc: '123'
            }
        });

        // 将 token.id 发送到服务器（不是卡数据）
        """
        pass

    @staticmethod
    def charge_with_token(token_id, amount):
        """使用令牌支付（服务器端）。"""
        # 你的服务器只看到令牌，永远不会看到卡号
        stripe.api_key = "sk_..."

        charge = stripe.Charge.create(
            amount=amount,
            currency="usd",
            source=token_id,  # 使用令牌而不是卡详情
            description="支付"
        )

        return charge

    @staticmethod
    def store_payment_method(customer_id, payment_method_token):
        """将支付方式作为令牌存储以供将来使用。"""
        stripe.Customer.modify(
            customer_id,
            source=payment_method_token
        )

        # 在你的数据库中只存储 customer_id 和 payment_method_id
        # 永远不要存储实际的卡数据
        return {
            'customer_id': customer_id,
            'has_payment_method': True
            # 不要存储：卡号、CVV 等
        }
```

### 自定义令牌化（高级）

```python
import secrets
from cryptography.fernet import Fernet

class TokenVault:
    """安全令牌保险库用于卡数据（如果你必须存储它）。"""

    def __init__(self, encryption_key):
        self.cipher = Fernet(encryption_key)
        self.vault = {}  # 在生产环境中：使用加密数据库

    def tokenize(self, card_data):
        """将卡数据转换为令牌。"""
        # 生成安全的随机令牌
        token = secrets.token_urlsafe(32)

        # 加密卡数据
        encrypted = self.cipher.encrypt(json.dumps(card_data).encode())

        # 存储令牌 -> 加密数据映射
        self.vault[token] = encrypted

        return token

    def detokenize(self, token):
        """从令牌中检索卡数据。"""
        encrypted = self.vault.get(token)
        if not encrypted:
            raise ValueError("令牌未找到")

        # 解密
        decrypted = self.cipher.decrypt(encrypted)
        return json.loads(decrypted.decode())

    def delete_token(self, token):
        """从保险库中移除令牌。"""
        self.vault.pop(token, None)
```

## 加密

### 静态数据

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

class EncryptedStorage:
    """使用 AES-256-GCM 加密静态数据。"""

    def __init__(self, encryption_key):
        """使用 256 位密钥初始化。"""
        self.key = encryption_key  # 必须是 32 字节

    def encrypt(self, plaintext):
        """加密数据。"""
        # 生成随机 nonce
        nonce = os.urandom(12)

        # 加密
        aesgcm = AESGCM(self.key)
        ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)

        # 返回 nonce + 密文
        return nonce + ciphertext

    def decrypt(self, encrypted_data):
        """解密数据。"""
        # 提取 nonce 和密文
        nonce = encrypted_data[:12]
        ciphertext = encrypted_data[12:]

        # 解密
        aesgcm = AESGCM(self.key)
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)

        return plaintext.decode()

# 使用
storage = EncryptedStorage(os.urandom(32))
encrypted_pan = storage.encrypt("4242424242424242")
# 将 encrypted_pan 存储在数据库中
```

### 传输中数据

```python
# 始终使用 TLS 1.2 或更高版本
# Flask/Django 示例
app.config['SESSION_COOKIE_SECURE'] = True  # 仅 HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'

# 强制 HTTPS
from flask_talisman import Talisman
Talisman(app, force_https=True)
```

## 其他模式和模板

更详细的模板和实际示例位于 `references/details.md`。阅读该文件以获取完整的模式库。
