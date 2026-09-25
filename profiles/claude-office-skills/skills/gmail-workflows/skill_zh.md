# Gmail 工作流

通过智能工作流自动管理 Gmail 附件、组织电子邮件和集成 Google Drive。基于 n8n 的 7,800 多个工作流模板。

## 概述

此技能可帮助您设计和实施 Gmail 自动化工作流，实现：
- 自动将附件保存到 Google Drive
- 使用智能标签组织电子邮件
- 归档已处理的电子邮件
- 通过 Slack/电子邮件发送通知
- 跟踪电子邮件指标

## 核心工作流模板

### 1. Gmail 附件管理器

**目的**：自动从电子邮件中提取附件并保存到 Google Drive

**工作流步骤**：
```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ Gmail       │───▶│ 筛选条件    │───▶│ 提取附件    │───▶│ 上传到 Google Drive│
│ 触发器     │    │              │    │              │    │              │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                │
                         ┌─────────────┐    ┌─────────────┐    │
                         │ 发送通知    │◀───│ 应用标签 & 归档 │◀───┘
                         │            │    │              │
                         └─────────────┘    └─────────────┘
```

**配置**：
```yaml
trigger:
  type: gmail_new_email
  filters:
    has_attachment: true
    from: ["*@company.com", "*@vendor.com"]
    subject_contains: ["invoice", "report", "contract"]

actions:
  - extract_attachments:
      file_types: [pdf, xlsx, docx, csv]
      max_size_mb: 25
  
  - upload_to_drive:
      folder_path: "/Attachments/{year}/{month}"
      naming_pattern: "{filename}_{sender}_{date}"
      create_folder_if_missing: true
  
  - organize_email:
      apply_label: "Processed/Attachments"
      mark_as_read: true
      archive: true
  
  - notify:
      channel: slack
      message: "新附件已保存: {filename} 来自 {sender}"
```

**最佳实践**：
- 使用特定的发件人筛选器以避免处理垃圾邮件
- 设置文件大小限制以防止存储问题
- 使用基于日期的文件夹结构以便于检索
- 启用重复检测以避免重复上传

---

### 2. 发票自动归档器

**目的**：自动从电子邮件中收集和组织发票

**工作流步骤**：
```
Gmail 触发器 → 检测发票 → 提取 PDF → OCR/解析 → 保存到 Drive → 更新电子表格 → 归档电子邮件
```

**配置**：
```yaml
trigger:
  subject_patterns:
    - "invoice"
    - "bill"
    - "statement"
    - "付款"
    - "发票"

processing:
  - detect_invoice:
      methods: [subject_keywords, attachment_name, sender_domain]
  
  - extract_data:
      fields: [invoice_number, amount, date, vendor, due_date]
      use_ocr: true
  
  - save_to_drive:
      folder: "/Finance/Invoices/{year}/{vendor}"
      naming: "{date}_{vendor}_{amount}"
  
  - update_tracker:
      spreadsheet: "Invoice Tracker"
      columns: [Date, Vendor, Amount, Invoice#, Status, File_Link]
  
  - archive:
      label: "Finance/Invoices"
      star: true
```

---

### 3. 客户沟通组织器

**目的**：自动按项目/客户组织客户电子邮件

**配置**：
```yaml
rules:
  - name: "客户 A 邮件"
    condition:
      from_domain: "clienta.com"
    actions:
      - apply_label: "Clients/Client A"
      - forward_to: "team-a@company.com"
      - save_attachments: "/Clients/Client A/{subject}"

  - name: "项目 X 更新"
    condition:
      subject_contains: ["Project X", "PX-"]
    actions:
      - apply_label: "Projects/Project X"
      - add_to_task: "Project X Board"
      - notify_slack: "#project-x"

  - name: "紧急请求"
    condition:
      subject_contains: ["URGENT", "ASAP", "紧急"]
      is_unread: true
    actions:
      - apply_label: "Priority/Urgent"
      - send_sms: "+1234567890"
      - move_to_inbox: true
```

---

### 4. 电子邮件分析仪表板

**目的**：跟踪电子邮件指标并生成报告

**要跟踪的指标**：
```yaml
daily_metrics:
  - emails_received: count(inbox)
  - emails_sent: count(sent)
  - response_time_avg: avg(reply_time)
  - unread_count: count(unread)
  - attachment_count: count(has_attachment)

weekly_report:
  - top_senders: group_by(from, count)
  - busiest_hours: group_by(hour, count)
  - label_distribution: group_by(label, count)
  - response_rate: sent / received

automation:
  - schedule: "每周一 9 点"
  - output: Google Sheets
  - notify: Slack #email-metrics
```

---

## 实施指南

### 使用 n8n

```javascript
// n8n 工作流：Gmail 到 Google Drive
{
  "nodes": [
    {
      "name": "Gmail Trigger",
      "type": "n8n-nodes-base.gmailTrigger",
      "parameters": {
        "pollTimes": { "item": [{ "mode": "everyMinute" }] },
        "filters": { "labelIds": ["INBOX"] }
      }
    },
    {
      "name": "筛选附件",
      "type": "n8n-nodes-base.if",
      "parameters": {
        "conditions": {
          "boolean": [{
            "value1": "={{ $json.hasAttachment }}",
            "value2": true
          }]
        }
      }
    },
    {
      "name": "获取附件",
      "type": "n8n-nodes-base.gmail",
      "parameters": {
        "operation": "getAttachments",
        "messageId": "={{ $json.id }}"
      }
    },
    {
      "name": "上传到 Drive",
      "type": "n8n-nodes-base.googleDrive",
      "parameters": {
        "operation": "upload",
        "folderId": "your-folder-id",
        "name": "={{ $json.filename }}"
      }
    }
  ]
}
```

### 使用 Google Apps Script

```javascript
// Gmail 到 Drive 自动化
function processNewEmails() {
  const threads = GmailApp.search('has:attachment is:unread');
  const targetFolder = DriveApp.getFolderById('FOLDER_ID');
  
  threads.forEach(thread => {
    const messages = thread.getMessages();
    messages.forEach(message => {
      const attachments = message.getAttachments();
      attachments.forEach(attachment => {
        // 保存到 Drive
        const file = targetFolder.createFile(attachment);
        
        // 重命名，包含日期和发件人
        const newName = `${Utilities.formatDate(message.getDate(), 'GMT', 'yyyy-MM-dd')}_${message.getFrom()}_${attachment.getName()}`;
        file.setName(newName);
      });
      
      // 标记为已处理
      message.markRead();
      thread.addLabel(GmailApp.getUserLabelByName('Processed'));
    });
  });
}

// 设置触发器
function setupTrigger() {
  ScriptApp.newTrigger('processNewEmails')
    .timeBased()
    .everyMinutes(5)
    .create();
}
```

---

## 常见工作流模式

### 模式 1：筛选 → 处理 → 组织 → 通知

```
电子邮件到达
    │
    ▼
┌─────────────────┐
│ 应用筛选       │ → 如果不匹配则跳过
│ (发件人, 主题, │
│  附件)         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 处理内容       │ → 提取数据、附件
│                 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 组织         │ → 保存文件、应用标签
│                 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 通知         │ → Slack、电子邮件、SMS
│                 │
└─────────────────┘
```

### 模式 2：批量处理

```yaml
schedule: "每天早上 6 点"
steps:
  1. 收集过去 24 小时内的所有未处理电子邮件
  2. 按类别分组（发票、报告、杂项）
  3. 批量上传到相应的 Drive 文件夹
  4. 生成摘要报告
  5. 向利益相关者发送每日摘要
```

### 模式 3：条件路由

```yaml
conditions:
  - if: attachment_type == "pdf" AND subject contains "invoice"
    then: route_to_finance_folder
  
  - if: from_domain in ["important-client.com"]
    then: priority_handling + immediate_notification
  
  - if: attachment_size > 10MB
    then: save_to_large_files_folder + skip_backup
  
  - default:
    then: standard_processing
```

---

## 故障排除

### 常见问题

| 问题 | 解决方案 |
|-------|----------|
| 附件未检测到 | 检查 MIME 类型筛选器，增加触发频率 |
| 重复文件 | 通过哈希或文件名启用去重 |
| 频率限制 | 减少触发频率，使用批量处理 |
| 权限错误 | 重新授权 OAuth 凭证 |
| 大文件失败 | 设置大小限制，使用分块上传 |

---

## 安全注意事项

1. **OAuth 范围**：请求最小权限
   - `gmail.readonly` 用于读取
   - `gmail.modify` 用于标签/归档
   - `drive.file` 用于 Drive 访问

2. **数据隐私**：
   - 不要记录电子邮件内容
   - 使用安全存储凭据
   - 实施保留策略

3. **访问控制**：
   - 限制谁可以修改工作流
   - 审计自动化活动
   - 使用单独的服务账户

---

## 输出示例

**每日电子邮件报告**：
```markdown
# 电子邮件活动报告 - 2026-01-30

## 摘要
- 收到电子邮件: 47
- 发送电子邮件: 23
- 处理附件: 12
- 平均回复时间: 2.3 小时

## 附件处理
| 文件 | 发件人 | 保存到 | 时间 |
|------|--------|----------|------|
| Invoice_Jan.pdf | vendor@co.com | /Finance/Invoices | 09:15 |
| Report_Q4.xlsx | team@company.com | /Reports/Q4 | 10:30 |
| Contract_v2.docx | legal@client.com | /Contracts | 14:22 |

## 应用标签
- Finance/Invoices: 5 封电子邮件
- Projects/Active: 12 封电子邮件
- Clients/Priority: 8 封电子邮件

## 待处理操作
- 3 封电子邮件需要手动审核
- 2 个大附件需要批准
```

---

*Gmail 工作流技能 - 隶属于 Claude 办公技能*
