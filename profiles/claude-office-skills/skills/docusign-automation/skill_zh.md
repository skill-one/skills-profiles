# DocuSign 自动化

全面的技能，用于自动化电子签名和文档签署工作流。

## 核心工作流

### 1. 签署流程

```
DOCUSIGN 签署流程：
┌─────────────────┐
│  创建回执     │
│  - 文档       │
│  - 收件人     │
└────────┬────────┘
         ▼
┌─────────────────┐
│  添加字段     │
│  - 签名       │
│  - 印鉴       │
│  - 日期       │
└────────┬────────┘
         ▼
┌─────────────────┐
│  发送至       │
│  签名       │
└────────┬────────┘
         ▼
┌─────────────────┐
│  签署人 1 签署 │
│  (按顺序)     │
└────────┬────────┘
         ▼
┌─────────────────┐
│  签署人 2 签署 │
│  (如有多个)  │
└────────┬────────┘
         ▼
┌─────────────────┐
│   已完成     │
│  - 归档       │
│  - 分发       │
└─────────────────┘
```

### 2. 回执配置

```yaml
envelope_config:
  email_subject: "{{document_type}} - 请签署"
  email_blurb: |
    请审阅并签署附件中的 {{document_type}}。
    此文档需要在 {{due_date}} 前签署。
    
  documents:
    - name: "{{contract_name}}.pdf"
      document_id: 1
      
  recipients:
    signers:
      - email: "{{signer_1_email}}"
        name: "{{signer_1_name}}"
        routing_order: 1
        tabs:
          sign_here:
            - anchor: "/sig1/"
              offset_x: 0
              offset_y: 0
          date_signed:
            - anchor: "/date1/"
              
      - email: "{{signer_2_email}}"
        name: "{{signer_2_name}}"
        routing_order: 2
        tabs:
          sign_here:
            - anchor: "/sig2/"
            
    carbon_copies:
      - email: "legal@company.com"
        name: "法务团队"
        routing_order: 3
        
  settings:
    reminder_enabled: true
    reminder_delay: 2  # 天
    reminder_frequency: 2  # 天
    expiration_days: 30
```

## 模板管理

### 模板创建

```yaml
template_config:
  name: "标准保密协议模板"
  description: "供应商保密协议"
  
  documents:
    - name: "NDA_Template.pdf"
      
  roles:
    - role_name: "公司代表"
      routing_order: 1
      
    - role_name: "对方"
      routing_order: 2
      
  tabs:
    company_rep:
      - type: sign_here
        anchor: "/company_signature/"
      - type: date_signed
        anchor: "/company_date/"
      - type: text
        anchor: "/company_name/"
        label: "姓名"
      - type: text
        anchor: "/company_title/"
        label: "职位"
        
    counterparty:
      - type: sign_here
        anchor: "/counterparty_signature/"
      - type: date_signed
        anchor: "/counterparty_date/"
      - type: text
        anchor: "/counterparty_name/"
        label: "姓名"
```

### 模板库

```yaml
template_library:
  contracts:
    - name: "雇佣协议"
      id: "template_emp_001"
      category: "人力资源"
      
    - name: "供应商协议"
      id: "template_vendor_001"
      category: "采购"
      
    - name: "保密协议（相互）"
      id: "template_nda_001"
      category: "法律"
      
  销售合同:
    - name: "销售订单"
      id: "template_so_001"
      
    - name: "工作说明书"
      id: "template_sow_001"
      
    - name: "主服务协议"
      id: "template_msa_001"
```

## 工作流自动化

### 条件路由

```yaml
conditional_workflow:
  name: "合同审批流程"
  
  conditions:
    - field: "contract_value"
      operator: "greater_than"
      value: 100000
      then:
        add_recipient:
          role: "VP 审批"
          routing_order: 1
          
    - field: "contract_type"
      operator: "equals"
      value: "国际"
      then:
        add_recipient:
          role: "法务审核"
          routing_order: 1
          
  default_flow:
    - role: "销售经理"
      routing_order: 1
    - role: "客户"
      routing_order: 2
```

### 批量发送

```yaml
bulk_send:
  template_id: "template_nda_001"
  
  recipients:
    - email: "vendor1@example.com"
      name: "供应商一"
      custom_fields:
        company_name: "供应商一公司"
        effective_date: "2024-02-01"
        
    - email: "vendor2@example.com"
      name: "供应商二"
      custom_fields:
        company_name: "供应商二有限责任公司"
        effective_date: "2024-02-01"
        
  settings:
    batch_name: "第一季度供应商保密协议"
    send_immediately: true
```

## 集成工作流

### Salesforce 集成

```yaml
salesforce_integration:
  triggers:
    opportunity_closed_won:
      template: "msa_template"
      recipients:
        - from_field: "Contact.Email"
          role: "客户"
      custom_fields:
        account_name: "Account.Name"
        contract_value: "Opportunity.Amount"
        
  callbacks:
    on_completed:
      - update_opportunity:
          stage: "合同已签署"
      - attach_document:
          to: "Opportunity"
      - create_task:
          subject: "合同已签署 - 开始入职流程"
```

### CRM Webhook

```yaml
webhook_config:
  events:
    - envelope-sent
    - envelope-delivered
    - envelope-completed
    - envelope-declined
    - envelope-voided
    
  callback_url: "https://api.example.com/docusign/webhook"
  
  payload_handling:
    envelope_completed:
      actions:
        - download_documents
        - update_crm_record
        - notify_team
        - archive_to_storage
```

## 状态跟踪

### 回执仪表盘

```
回执状态 - 本月
═══════════════════════════════════════

总计: 156 个回执

按状态:
已完成    ████████████████ 89 (57%)
已发送     ████████░░░░░░░░ 34 (22%)
已送达    ████░░░░░░░░░░░░ 18 (12%)
已拒绝     █░░░░░░░░░░░░░░░ 5 (3%)
已作废    █░░░░░░░░░░░░░░░ 10 (6%)

平均完成时间: 2.3 天

待签署:
┌────────────────────┬──────────────┬─────────┐
│ 文档             │ 等待       │ 已发送   │
├────────────────────┼──────────────┼─────────┤
│ Acme Corp 保密协议      │ John Smith   │ 3 天  │
│ TechStart 工作说明书      │ Jane Doe     │ 1 天   │
│ 供应商协议       │ Bob Wilson   │ 5 天  │
└────────────────────┴──────────────┴─────────┘

已发送提醒: 23
```

### 审计追踪

```yaml
audit_trail:
  events:
    - timestamp: "2024-01-15T10:30:00Z"
      action: "回执创建"
      user: "sender@company.com"
      ip: "192.168.1.1"
      
    - timestamp: "2024-01-15T10:31:00Z"
      action: "回执发送"
      recipients: ["signer@example.com"]
      
    - timestamp: "2024-01-15T14:22:00Z"
      action: "文档查看"
      user: "signer@example.com"
      ip: "10.0.0.1"
      
    - timestamp: "2024-01-15T14:25:00Z"
      action: "签名应用"
      user: "signer@example.com"
      signature_type: "电子"
      
    - timestamp: "2024-01-15T14:25:30Z"
      action: "回执完成"
```

## API 示例

### 创建并发送回执

```javascript
// 从模板创建回执
const envelope = await docusign.envelopes.create(accountId, {
  templateId: "template_123",
  templateRoles: [
    {
      roleName: "客户",
      email: "customer@example.com",
      name: "John Customer",
      tabs: {
        textTabs: [
          {
            tabLabel: "CompanyName",
            value: "客户公司"
          }
        ]
      }
    }
  ],
  status: "sent"
});

// 获取回执状态
const status = await docusign.envelopes.get(
  accountId, 
  envelopeId
);

// 下载已完成文档
const documents = await docusign.envelopes.getDocuments(
  accountId,
  envelopeId,
  { certificate: true }
);

// 作废回执
await docusign.envelopes.update(accountId, envelopeId, {
  status: "voided",
  voidedReason: "合同条款变更"
});
```

## 最佳实践

1. **使用模板**: 标准化常用文档
2. **设置提醒**: 自动化跟进
3. **过期日期**: 确保及时完成
4. **审计追踪**: 维护合规性
5. **批量发送**: 高效处理多个收件人
6. **Webhooks**: 实时状态更新
7. **品牌签署**: 自定义签署体验
8. **归档**: 安全存储已完成文档
