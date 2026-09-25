# PDF 表单自动填写工具

自动填写 PDF 表单并从已完成表单中提取数据。

## 概述

此功能可帮助您：
- 使用提供的数据自动填写 PDF 表单
- 从已填写表单中提取数据
- 批量填写多个表单
- 验证表单数据
- 创建表单填写模板

## 使用方法

### 填写表单
```
"使用以下数据填写此 PDF 表单：
- 姓名：约翰·史密斯
- 日期：2026-01-29
- 金额：$1,500"
```

### 提取表单数据
```
"从此 PDF 中提取所有表单字段值"
"此表单中填写了哪些数据？"
```

### 批量填写
```
"使用来自电子表格的数据填写此表单的 50 份副本"
"为此 CSV 中的每一行生成表单"
```

## 表单字段类型

### 支持的字段
| 字段类型 | 描述 | 填写方法 |
|------------|------|----------|
| **文本字段** | 单行/多行文本 | 直接输入文本 |
| **复选框** | 是/否选择 | 勾选/取消勾选 |
| **单选按钮** | 多个选项中的一个 | 选择选项 |
| **下拉列表** | 列表选择 | 选择值 |
| **日期字段** | 日期选择器 | 日期值 |
| **签名** | 数字签名 | 签名图像/证书 |
| **组合框** | 带文本输入的下拉列表 | 选择或输入 |

### 字段识别
```markdown
## 表单字段：[表单名称]

### 字段映射
| 字段名称 | 类型 | 必填 | 页码 | 备注 |
|----------|------|------|------|------|
| applicant_name | 文本 | 是 | 1 | 最大 50 个字符 |
| birth_date | 日期 | 是 | 1 | MM/DD/YYYY |
| gender | 单选按钮 | 是 | 1 | M/F/其他 |
| employed | 复选框 | 否 | 1 | 如是则勾选 |
| state | 下拉列表 | 是 | 2 | 美国各州 |
| signature | 签名 | 是 | 3 | 数字签名 |
```

## 填写模板

### 数据映射模板
```markdown
## 表单填写模板：[表单名称]

### 表单信息
- **文件**：application_form.pdf
- **总字段数**：25
- **必填字段数**：15

### 字段映射
```yaml
# 个人信息
applicant_name: "${firstName} ${lastName}"
date_of_birth: "${birthDate}"
ssn_last_four: "${ssnLast4}"
phone: "${phone}"
email: "${email}"

# 地址
street_address: "${address.street}"
city: "${address.city}"
state: "${address.state}"
zip_code: "${address.zip}"

# 就业情况
currently_employed: ${isEmployed}  # 复选框
employer_name: "${employer.name}"
job_title: "${employer.title}"

# 选择项
payment_method: "${paymentMethod}"  # 下拉列表
agree_terms: true  # 复选框
```

### 示例数据
```json
{
  "firstName": "John",
  "lastName": "Smith",
  "birthDate": "1990-05-15",
  "phone": "555-123-4567",
  "email": "john.smith@email.com",
  "address": {
    "street": "123 Main St",
    "city": "New York",
    "state": "NY",
    "zip": "10001"
  },
  "isEmployed": true,
  "employer": {
    "name": "Acme Corp",
    "title": "Manager"
  },
  "paymentMethod": "Direct Deposit"
}
```
```

## 输出格式

### 填写结果报告
```markdown
## 表单填写结果

### 摘要
| 状态 | 值 |
|------|----|
| **表单** | application_form.pdf |
| **已填写字段** | 23/25 |
| **错误** | 2 |
| **输出** | filled_application.pdf |

### 已填写字段
| 字段 | 值 | 状态 |
|------|----|------|
| applicant_name | John Smith | ✅ |
| date_of_birth | 05/15/1990 | ✅ |
| phone | 555-123-4567 | ✅ |
| state | NY | ✅ |
| payment_method | Direct Deposit | ✅ |

### 错误/警告
| 字段 | 问题 | 建议 |
|------|------|------|
| ssn | 字段未找到 | 检查字段名称 |
| signature | 需要证书 | 手动添加签名 |

### 验证
- ✅ 所有必填字段已填写
- ✅ 日期格式正确
- ⚠️ 签名字段需要手动完成
```

### 提取数据报告
```markdown
## 表单数据提取

### 来源：completed_form.pdf

### 提取的值
```json
{
  "form_title": "就业申请",
  "submission_date": "2026-01-29",
  "fields": {
    "applicant_name": "Jane Doe",
    "date_of_birth": "1985-03-20",
    "email": "jane.doe@email.com",
    "phone": "555-987-6543",
    "address": "456 Oak Ave, Chicago, IL 60601",
    "position_applied": "Senior Developer",
    "salary_expectation": "$120,000",
    "available_start": "2026-03-01",
    "references_provided": true
  }
}
```

### 字段统计
| 指标 | 值 |
|------|----|
| 总字段数 | 30 |
| 已填写字段 | 28 |
| 空字段 | 2 |
| 提取置信度 | 98% |
```

## 批量处理

### 批量填写任务
```markdown
## 批量表单填写

### 配置
- **模板表单**：w9_form.pdf
- **数据源**：vendors.csv
- **记录数**：150
- **输出文件夹**：/filled_w9s/

### 数据预览
| 行 | 名称 | TIN | 地址 |
|----|------|-----|------|
| 1 | Acme Corp | XX-XXX1234 | 123 Main St |
| 2 | Beta LLC | XX-XXX5678 | 456 Oak Ave |
| ... | ... | ... | ... |

### 进度
| 状态 | 计数 | 百分比 |
|------|------|--------|
| ✅ 已完成 | 145 | 97% |
| ⚠️ 警告 | 3 | 2% |
| ❌ 错误 | 2 | 1% |

### 错误
| 行 | 问题 |
|----|------|
| 47 | TIN 格式无效 |
| 89 | 缺少必填项：地址 |

### 输出文件
- w9_acme_corp.pdf
- w9_beta_llc.pdf
- ...
```

## 表单验证

### 验证规则
```markdown
## 表单验证规则

### 字段验证
| 字段 | 规则 | 错误消息 |
|------|------|----------|
| email | 有效的电子邮件格式 | "无效的电子邮件地址" |
| phone | 10 位数字 | "电话号码必须是 10 位" |
| ssn | XXX-XX-XXXX 格式 | "无效的 SSN 格式" |
| date | MM/DD/YYYY | "使用 MM/DD/YYYY 格式" |
| zip | 5 或 9 位数字 | "无效的邮政编码" |
| amount | 数字，> 0 | "输入正数" |

### 跨字段验证
| 规则 | 字段 | 条件 |
|------|------|------|
| 条件必填 | employer_name | 如果 employed = true 则必填 |
| 日期范围 | end_date | 必须在 start_date 之后 |
| 总和检查 | item_totals | 必须等于 grand_total |
```

### 验证报告
```markdown
## 填写前验证

### 数据验证结果
| 字段 | 值 | 有效 | 问题 |
|------|------|------|------|
| email | john@email | ❌ | 缺少域名 |
| phone | 555-1234 | ❌ | 只有 7 位数字 |
| date | 2026-01-29 | ✅ | - |
| zip | 10001 | ✅ | - |

### 摘要
- ✅ 有效字段：18 个
- ❌ 无效字段：2 个
- ⚠️ 警告字段：3 个

### 建议
1. 修正电子邮件格式：添加域名（例如，@company.com）
2. 完成电话号码，包括区号
```

## 常见表单类型

### 政府表单
| 表单 | 目的 | 关键字段 |
|------|------|----------|
| W-9 | 税务识别 | TIN、姓名、地址 |
| I-9 | 就业资格 | 身份证信息、公民身份 |
| W-4 | 扣除 | 允许次数、状态 |
| 1099 | 合同收入 | 收入、付款人信息 |

### 商业表单
| 表单 | 目的 | 关键字段 |
|------|------|----------|
| NDA | 保密协议 | 当事人、条款、日期 |
| 发票 | 计费 | 项目、金额、条款 |
| 采购订单 | 采购 | 项目、数量、供应商 |
| 申请 | 各种用途 | 个人信息、历史 |

## 工具推荐

### 桌面软件
- **Adobe Acrobat Pro**：完整的表单功能
- **Foxit PDF 编辑器**：良好的表单支持
- **PDFescape**：免费的在线选项
- **JotForm**：表单创建和填写

### 编程库
- **pdf-lib** (JavaScript)：填写和创建表单
- **PyPDF2** (Python)：基本表单填写
- **iText** (Java/.NET)：企业表单
- **PDFBox** (Java)：Apache 项目

### 自动化工具
- **Adobe Acrobat Actions**：批量处理
- **Power Automate**：微软集成
- **Zapier + PDF.co**：云自动化

## 限制

- 无法执行实际表单填写（仅提供指导）
- 数字签名需要适当的证书
- 一些受保护的 PDF 无法填写表单
- 复杂计算可能无法自动更新
- 平坦化表单无法编辑
- 字段名称必须完全匹配
