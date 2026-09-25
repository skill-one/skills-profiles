# Stripe 集成

掌握 Stripe 支付处理集成，构建强大且符合 PCI 标准的支付流程，包括结账、订阅、Webhooks 和退款。

## 何时使用此技能

- 在 Web/移动应用中实现支付处理
- 设置订阅计费系统
- 处理一次性支付和周期性收费
- 处理退款和争议
- 管理客户支付方式
- 为欧洲支付实现 SCA（强客户认证）
- 使用 Stripe Connect 构建市场支付流程

## 核心概念

### 1. 支付流程

**结账会话**

- 适用于大多数集成
- 支持所有 UI 路径：
  - Stripe 托管的结账页面
  - 嵌入式结账表单
  - 使用 Elements（支付元素、Express Checkout 元素）的自定义 UI（`ui_mode='custom'`）
- 提供内置结账功能（商品、折扣、税费、运费、地址收集、保存的支付方式和结账生命周期事件）
- 相比 Payment Intents，集成和维护负担更低

**支付意图（定制控制）**

- 您自行计算最终金额，包括税费、折扣、订阅和货币转换
- 实现更复杂，长期维护负担更大
- 需要 Stripe.js 以符合 PCI 标准

**设置意图（保存支付方式）**

- 收集支付方式但不扣款
- 用于订阅和未来支付
- 需要客户确认

### 2. Webhooks

**关键事件：**

- `payment_intent.succeeded`：支付完成
- `payment_intent.payment_failed`：支付失败
- `customer.subscription.updated`：订阅变更
- `customer.subscription.deleted`：订阅取消
- `charge.refunded`：退款处理
- `invoice.payment_succeeded`：订阅支付成功

### 3. 订阅

**组件：**

- **商品**：您销售的产品
- **价格**：金额和频率
- **订阅**：客户的周期性支付
- **账单**：每个计费周期生成

### 4. 客户管理

- 创建和管理客户记录
- 存储多个支付方式
- 跟踪客户元数据
- 管理计费详情

## 快速入门

```python
import stripe

stripe.api_key = "sk_test_..."

# 创建结账会话
session = stripe.checkout.Session.create(
    line_items=[{
        'price_data': {
            'currency': 'usd',
            'product_data': {
                'name': '高级订阅',
            },
            'unit_amount': 2000,  # $20.00
            'recurring': {
                'interval': 'month',
            },
        },
        'quantity': 1,
    }],
    mode='subscription',
    success_url='https://yourdomain.com/success?session_id={CHECKOUT_SESSION_ID}',
    cancel_url='https://yourdomain.com/cancel'
)

# 重定向用户到 session.url
print(session.url)
```

## 详细模式和示例

详细模式文档位于 `references/details.md`。当上层导航层级不足时，请阅读该文件。

## 测试

```python
# 使用测试模式密钥
stripe.api_key = "sk_test_..."

# 测试卡号
TEST_CARDS = {
    'success': '4242424242424242',
    'declined': '4000000000000002',
    '3d_secure': '4000002500003155',
    'insufficient_funds': '4000000000009995'
}

def test_payment_flow():
    """测试完整支付流程。"""
    # 创建测试客户
    customer = stripe.Customer.create(
        email="test@example.com"
    )

    # 创建支付意图
    intent = stripe.PaymentIntent.create(
        amount=1000,
        automatic_payment_methods={
            'enabled': True
        },
        currency='usd',
        customer=customer.id
    )

    # 使用测试卡确认
    confirmed = stripe.PaymentIntent.confirm(
        intent.id,
        payment_method='pm_card_visa'  # 测试支付方式
    )

    assert confirmed.status == 'succeeded'
```
