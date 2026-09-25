# PayPal 集成

掌握 PayPal 支付集成，包括快速结账、IPN 处理、周期性计费和退款流程。

## 使用此技能的场景

- 将 PayPal 作为支付选项进行集成
- 实现快速结账流程
- 设置 PayPal 周期性计费
- 处理退款和支付争议
- 处理 PayPal Webhook（IPN）
- 支持国际支付
- 实现 PayPal 订阅

## 核心概念

### 1. 支付产品

**PayPal 快速结账**

- 单次支付
- 快速结账体验
- 访客和 PayPal 账户支付

**PayPal 订阅**

- 周期性计费
- 订阅计划
- 自动续订

**PayPal 汇款**

- 向多个收件人发送资金
- 市场和平台支付

### 2. 集成方法

**客户端（JavaScript SDK）**

- 智能支付按钮
- 托管支付流程
- 最少后端代码

**服务器端（REST API）**

- 完全控制支付流程
- 自定义结账界面
- 高级功能

### 3. IPN（即时支付通知）

- 类似 Webhook 的支付通知
- 异步支付更新
- 需要验证

## 快速入门

```javascript
// 前端 - PayPal 智能按钮
<div id="paypal-button-container"></div>

<script src="https://www.paypal.com/sdk/js?client-id=YOUR_CLIENT_ID&currency=USD"></script>
<script>
  paypal.Buttons({
    createOrder: function(data, actions) {
      return actions.order.create({
        purchase_units: [{
          amount: {
            value: '25.00'
          }
        }]
      });
    },
    onApprove: function(data, actions) {
      return actions.order.capture().then(function(details) {
        // 支付成功
        console.log('Transaction completed by ' + details.payer.name.given_name);

        // 发送到后端进行验证
        fetch('/api/paypal/capture', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({orderID: data.orderID})
        });
      });
    }
  }).render('#paypal-button-container');
</script>
```

```python
# 后端 - 验证并捕获订单
from paypalrestsdk import Payment
import paypalrestsdk

paypalrestsdk.configure({
    "mode": "sandbox",  # 或 "live"
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET"
})

def capture_paypal_order(order_id):
    """捕获 PayPal 订单."""
    payment = Payment.find(order_id)

    if payment.execute({"payer_id": payment.payer.payer_info.payer_id}):
        # 支付成功
        return {
            'status': 'success',
            'transaction_id': payment.id,
            'amount': payment.transactions[0].amount.total
        }
    else:
        # 支付失败
        return {
            'status': 'failed',
            'error': payment.error
        }
```

## 详细模式和实例

详细模式文档位于 `references/details.md`。当上层导航层级不足时，请阅读该文件。

## 测试

```python
# 使用沙盒凭证
SANDBOX_CLIENT_ID = "..."
SANDBOX_SECRET = "..."

# 测试账户
# 在 developer.paypal.com 创建测试买方和卖方账户

def test_payment_flow():
    """测试完整支付流程."""
    client = PayPalClient(SANDBOX_CLIENT_ID, SANDBOX_SECRET, mode='sandbox')

    # 创建订单
    order = client.create_order(10.00)
    assert 'id' in order

    # 获取批准 URL
    approval_url = next((link['href'] for link in order['links'] if link['rel'] == 'approve'), None)
    assert approval_url is not None

    # 批准后（手动步骤，使用测试账户）
    # 捕获订单
    # captured = client.capture_order(order['id'])
    # assert captured['status'] == 'COMPLETED'
```
