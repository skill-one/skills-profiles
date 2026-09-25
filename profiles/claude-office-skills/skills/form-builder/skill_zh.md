# 表单构建技能

## 概述

此技能可使用 **docassemble**（一个用于引导式访谈并生成文档的平台）创建智能文档表单。创建可根据答案调整的问卷。

## 如何使用

1. 描述您需要的表单或文档
2. 指定条件逻辑需求
3. 我将创建 docassemble 访谈 YAML 文件

**示例提示：**
- "为新客户创建一个登记表"
- "构建用于法律文档的条件式问卷"
- "生成用于合同生成的多步骤表单"
- "设计一个交互式文档组装表单"

## 领域知识

### 访谈结构

```yaml
metadata:
  title: 客户登记表
  short title: 登记

---
question: |
  您叫什么名字？
fields:
  - 姓名: first_name
  - 姓氏: last_name

---
question: |
  您需要哪种服务？
field: service_type
choices:
  - 合同审查
  - 文档起草
  - 咨询

---
mandatory: True
question: |
  谢谢您，${ first_name }！
subquestion: |
  我们将就您的 ${ service_type } 请求与您联系。
```

### 条件逻辑

```yaml
---
question: |
  您是公司还是个人？
field: client_type
choices:
  - 公司
  - 个人

---
if: client_type == "公司"
question: |
  您的公司名称是什么？
fields:
  - 公司: company_name
  - EIN: ein
    required: False

---
if: client_type == "个人"
question: |
  您的出生日期是什么时候？
fields:
  - 出生日期: birthdate
    datatype: date
```

### 字段类型

```yaml
fields:
  # 文本
  - 名称: name
  
  # 邮箱
  - 邮箱: email
    datatype: email
  
  # 数字
  - 年龄: age
    datatype: integer
  
  # 货币
  - 金额: amount
    datatype: currency
  
  # 日期
  - 开始日期: start_date
    datatype: date
  
  # 是/否
  - 同意条款?: agrees
    datatype: yesno
  
  # 单选
  - 颜色: color
    choices:
      - 红色
      - 蓝色
      - 绿色
  
  # 复选框
  - 选择选项: options
    datatype: checkboxes
    choices:
      - 选项 A
      - 选项 B
  
  # 文件上传
  - 上传文档: document
    datatype: file
```

### 文档生成

```yaml
---
mandatory: True
question: |
  您的文档已准备好。
attachment:
  name: 合同
  filename: contract
  content: |
    # 服务协议
    
    本协议由 **${ client_name }**
    和 **服务提供方** 签订。
    
    ## 服务
    ${ service_description }
    
    ## 付款
    总金额: ${ currency(amount) }
    
    日期: ${ today() }
```

## 示例：客户登记

```yaml
metadata:
  title: 法律客户登记
  short title: 登记

---
objects:
  - client: 个人

---
question: |
  欢迎填写我们的登记表。
subquestion: |
  请回答以下问题。
continue button field: intro_screen

---
question: |
  您叫什么名字？
fields:
  - 姓名: client.name.first
  - 姓氏: client.name.last
  - 邮箱: client.email
    datatype: email
  - 电话: client.phone
    required: False

---
question: |
  这是什么类型的案件？
field: matter_type
choices:
  - 合同: contract
  - 争议: dispute
  - 咨询: advisory

---
if: matter_type == "合同"
question: |
  合同详情
fields:
  - 合同类型: contract_type
    choices:
      - 雇佣
      - 服务协议
      - NDA
  - 另一方: other_party
  - 预计金额: contract_value
    datatype: currency

---
mandatory: True
question: |
  谢谢您，${ client.name.first }！
subquestion: |
  **摘要：**
  
  - 姓名: ${ client.name }
  - 邮箱: ${ client.email }
  - 案件: ${ matter_type }
  
  我们将在 24 小时内与您联系。
```

## 资源

- [docassemble 文档](https://docassemble.org/docs.html)
- [GitHub 仓库](https://github.com/jhpyle/docassemble)
