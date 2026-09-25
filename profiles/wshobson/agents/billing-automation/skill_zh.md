# 账单自动化

掌握自动化账单系统，包括周期性账单、发票生成、催款管理、按比例调整费用和税务计算。

## 使用此技能的场景

- 实施SaaS订阅账单
- 自动化发票生成和交付
- 管理失败付款回收（催款）
- 计算计划变更的按比例调整费用
- 处理销售税、增值税和商品及服务税
- 处理基于使用量的账单
- 管理账单周期和续订

## 核心概念

### 1. 账单周期

**常见间隔：**

- 按月（SaaS中最常见）
- 按年（长期折扣）
- 按季
- 按周
- 自定义（基于使用量、按座位数）

### 2. 订阅状态

```
试用 → 活跃 → 逾期 → 已取消
              → 暂停 → 恢复
```

### 3. 催款管理

通过以下方式自动回收失败付款：

- 重试计划
- 客户通知
- 宽限期
- 账户限制

### 4. 按比例调整费用

在以下情况下调整费用：

- 周期内升级/降级
- 添加/删除座位
- 更改账单频率

## 快速入门

```python
from billing import BillingEngine, Subscription

# 初始化账单引擎
billing = BillingEngine()

# 创建订阅
subscription = billing.create_subscription(
    customer_id="cus_123",
    plan_id="plan_pro_monthly",
    billing_cycle_anchor=datetime.now(),
    trial_days=14
)

# 处理账单周期
billing.process_billing_cycle(subscription.id)
```

## 详细模式和实例

详细模式文档位于 `references/details.md`。当上层导航层级不足时，请阅读该文件。
