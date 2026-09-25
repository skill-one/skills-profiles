# QuickBooks 自动化

全面的技能，用于自动化 QuickBooks 会计和簿记工作流程。

## 核心工作流程

### 1. 会计流程

```
QUICKBOOKS 自动化流程：
┌─────────────────────────────────────────────────────────┐
│                    数据录入                            │
│  发票 │ 支出 │ 付款 │ 银行数据导入            │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   分类                            │
│  总账科目表 │ 类别 │ 地点                │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│                   对账                            │
│  银行对账 │ 信用卡 │ 清算                │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│                    报表                            │
│  损益表 │ 资产负债表 │ 现金流量表 │ 税务报表          │
└─────────────────────────────────────────────────────────┘
```

### 2. 自动化规则

```yaml
automation_rules:
  - name: auto_categorize_amazon
    trigger:
      vendor: "Amazon"
    action:
      account: "办公用品"
      class: "运营"
      
  - name: auto_categorize_payroll
    trigger:
      vendor: "Gusto"
    action:
      account: "工资支出"
      split:
        - account: "工资"
          percentage: 85
        - account: "工资税"
          percentage: 15
          
  - name: invoice_reminder
    trigger:
      invoice_days_overdue: 7
    action:
      send_reminder_email: true
      add_late_fee: false
```

## 发票管理

### 发票创建

```yaml
invoice_template:
  customer:
    name: "{{customer_name}}"
    email: "{{customer_email}}"
    billing_address: "{{billing_address}}"
    
  header:
    invoice_number: "INV-{{auto_increment}}"
    invoice_date: "{{today}}"
    due_date: "{{today + 30}}"
    terms: "净30天"
    
  line_items:
    - description: "{{service_description}}"
      quantity: "{{quantity}}"
      rate: "{{unit_price}}"
      amount: "{{quantity * unit_price}}"
      account: "服务收入"
      
  footer:
    subtotal: "{{sum_line_items}}"
    tax_rate: "{{tax_percent}}"
    tax_amount: "{{subtotal * tax_rate}}"
    total: "{{subtotal + tax_amount}}"
    
  delivery:
    send_email: true
    cc_accountant: false
    attach_pdf: true
```

### 重复性发票

```yaml
recurring_invoices:
  - name: 月度咨询费
    customer: "Acme Corp"
    frequency: 每月
    day_of_month: 1
    amount: 5000
    description: "月度咨询费"
    auto_send: true
    
  - name: 季度订阅
    customer: "TechStart Inc"
    frequency: 每季度
    start_date: "2024-01-01"
    amount: 2500
    description: "Q{{quarter}} 软件订阅"
    auto_send: true
```

## 支出跟踪

### 支出类别

```yaml
expense_categories:
  operating_expenses:
    - 广告
    - 银行费用
    - 保险
    - 法律与专业
    - 办公用品
    - 租金
    - 公用事业
    
  成本商品:
    - 材料成本
    - 运输
    - 直接人工
    
  工资:
    - 工资与薪金
    - 工资税
    - 员工福利
```

### 收据处理

```yaml
receipt_automation:
  capture:
    sources:
      - email_forward
      - mobile_app
      - 银行数据导入
      
  extraction:
    fields:
      - 供应商
      - 日期
      - 金额
      - 付款方式
      
  matching:
    auto_match:
      threshold: 0.95
      rules:
        - 金额精确匹配
        - 日期在3天内
        - 供应商模糊匹配
        
  categorization:
    use_history: true
    default_category: "咨询会计"
```

## 银行对账

### 银行数据导入规则

```yaml
bank_rules:
  - name: Stripe 存款
    conditions:
      description_contains: "STRIPE"
    action:
      category: "销售收入"
      class: "在线销售"
      auto_match_invoices: true
      
  - name: 工资
    conditions:
      description_contains: "GUSTO"
      amount_range: [-50000, -1000]
    action:
      category: "工资"
      split_by_historical: true
      
  - name: AWS 费用
    conditions:
      description_contains: "AMAZON WEB SERVICES"
    action:
      category: "云托管"
      class: "技术"
```

### 对账仪表盘

```
银行对账状态
═══════════════════════════════════════

账户: 商业支票 ****4567

银行余额:       $125,450.23
QuickBooks 余额: $124,890.45
差额:         $559.78

未匹配交易:
┌────────────┬────────────────────┬──────────┐
│ 日期       │ 描述                │ 金额   │
├────────────┼────────────────────┼──────────┤
│ 01/15      │ 支票 #1234        │ $450.00  │
│ 01/16      │ 电汇              │ $109.78  │
└────────────┴────────────────────┴──────────┘

待处理项目:
未兑现支票:  $1,234.50
在途存款: $674.72

上次对账: 2024年1月10日
```

## 财务报表

### 标准报表

```yaml
reports:
  profit_loss:
    type: standard
    period: 本月
    comparison: 上月
    columns:
      - 实际
      - 预算
      - 差异
      - 百分比变化
      
  balance_sheet:
    type: standard
    as_of_date: 期末
    show_totals: true
    
  cash_flow:
    type: standard
    method: 间接法
    period: 本季度
    
  ar_aging:
    type: aging
    aging_buckets: [30, 60, 90, 120]
    
  ap_aging:
    type: aging
    aging_buckets: [30, 60, 90]
```

### 报表仪表盘

```
财务仪表盘 - 2024年1月
═══════════════════════════════════════

损益表:
收入:          $185,450
成本:             $45,230
毛利润:     $140,220 (75.6%)
运营支出:    $82,340
净利润:       $57,880 (31.2%)

与预算对比:
收入     ████████████████░░ +8%
支出    ██████████████░░░░ -3%
利润      ██████████████████ +15%

资产负债表:
资产:           $456,780
负债:      $123,450
权益:           $333,330

现金状况:
运营现金:   $125,450
应收账款:      $89,230
应付账款:         $34,560
净现金:         $180,120

应收账款账龄:
当前     ████████████████ $45,230
1-30天   ████████░░░░░░░░ $23,450
31-60天  ████░░░░░░░░░░░░ $12,340
61-90天  ██░░░░░░░░░░░░░░ $5,670
90+天    █░░░░░░░░░░░░░░░ $2,540
```

## 集成工作流程

### 电子商务同步

```yaml
shopify_sync:
  frequency: 每日
  
  orders:
    create_invoice: true
    match_customer: true
    create_customer_if_new: true
    
  products:
    sync_inventory: true
    update_cogs: true
    
  payments:
    record_deposits: true
    account: "未存款"
    
  refunds:
    create_credit_memo: true
    link_to_original: true
```

### 工资集成

```yaml
gusto_sync:
  frequency: 每次工资
  
  mapping:
    gross_pay: "工资与薪金"
    employer_taxes: "工资税"
    benefits: "员工福利"
    
  journal_entry:
    debit:
      - account: "工资支出"
        amount: total_gross
    credit:
      - account: "工资负债"
        amount: withholdings
      - account: "现金"
        amount: net_pay
```

## API 示例

### 创建发票

```javascript
// QuickBooks API - 创建发票
const invoice = {
  CustomerRef: {
    value: "123"
  },
  Line: [
    {
      DetailType: "SalesItemLineDetail",
      Amount: 1000,
      SalesItemLineDetail: {
        ItemRef: { value: "1" },
        Qty: 10,
        UnitPrice: 100
      }
    }
  ],
  DueDate: "2024-02-15"
};

const response = await qbo.createInvoice(invoice);
```

### 查询交易

```javascript
// 查询近期支出
const expenses = await qbo.findPurchases({
  TxnDate: { $gt: '2024-01-01' },
  AccountRef: { value: '50' } // 运营支出
});

// 查询未付款发票
const unpaid = await qbo.findInvoices({
  Balance: { $gt: 0 },
  DueDate: { $lt: new Date().toISOString() }
});
```

## 最佳实践

1. **每日银行数据导入审查**: 及时匹配交易
2. **一致分类**: 使用标准总账科目表
3. **月度对账**: 每月结账
4. **文件附件**: 将收据附加到交易
5. **类别跟踪**: 用于部门/项目跟踪
6. **定期备份**: 定期导出数据
7. **访问控制**: 限制用户权限
8. **审计追踪**: 定期审查变更
