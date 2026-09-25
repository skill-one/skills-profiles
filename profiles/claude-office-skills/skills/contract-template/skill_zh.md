# 合同模板技能

## 概述

该技能可使用 **Accord Project**（一个用于创建具有法律约束力、机器可读的合同的开放源代码框架）来创建智能合同模板。创建包含嵌入式逻辑的模板，以实现合同执行的自动化。

## 如何使用

1. 描述合同类型和条款
2. 指定变量和逻辑规则
3. 我将生成 Accord Project 模板

**示例提示：**
- "创建一份具有变量条款的保密协议模板"
- "构建一份带有付款里程碑的服务协议"
- "生成一份租赁协议模板"
- "设计一份带有终止条款的咨询合同"

## 领域知识

### 模板结构

```
contract-template/
├── package.json           # 元数据
├── grammar/
│   └── template.tem.md    # 自然语言模板
├── model/
│   └── model.cto          # 数据模型
├── logic/
│   └── logic.ergo         # 业务逻辑
└── text/
    └── sample.md          # 示例合同
```

### 模板语法（TemplateMark）

```markdown
# 服务协议

本协议由 [{supplier}]（"供应商"）与 [{buyer}]（"买方"）签订。

## 服务
供应商同意提供 [{serviceDescription}]。

## 付款
买方应在开票后 [{paymentDays}] 天内支付 [{paymentAmount}]。

## 期限
本协议自 [{startDate as "MMMM DD, YYYY"}] 开始，持续 [{termMonths}] 个月。

{{#if latePenalty}}
## 滞纳金
逾期付款将适用 [{penaltyPercent}%] 的滞纳金。
{{/if}}
```

### 数据模型（Concerto）

```cto
namespace org.example.service

import org.accordproject.time.*

asset ServiceAgreement extends Contract {
  o String supplier
  o String buyer
  o String serviceDescription
  o Double paymentAmount
  o Integer paymentDays
  o DateTime startDate
  o Integer termMonths
  o Boolean latePenalty optional
  o Double penaltyPercent optional
}

transaction PaymentRequest {
  o Double amount
  o DateTime dueDate
}

transaction PaymentResponse {
  o Double amount
  o Double penalty
  o DateTime paymentDue
}
```

### 业务逻辑（Ergo）

```ergo
namespace org.example.service

import org.accordproject.time.*

contract ServiceContract over ServiceAgreement {
  
  clause payment(request : PaymentRequest) : PaymentResponse {
    let dueDate = addDuration(request.dueDate, 
                              Duration{ amount: contract.paymentDays, unit: ~org.accordproject.time.TemporalUnit.days });
    
    let penalty = 
      if contract.latePenalty
      then request.amount * contract.penaltyPercent / 100.0
      else 0.0;
    
    return PaymentResponse{
      amount: request.amount,
      penalty: penalty,
      paymentDue: dueDate
    }
  }
}
```

### 使用 Cicero CLI

```bash
# 安装
npm install -g @accordproject/cicero-cli

# 解析合同
cicero parse --template ./contract-template --sample ./text/sample.md

# 执行逻辑
cicero trigger --template ./contract-template \
  --sample ./text/sample.md \
  --request ./request.json

# 起草新合同
cicero draft --template ./contract-template --data ./data.json
```

## 示例：保密协议模板

### template.tem.md
```markdown
# 保密协议

本保密协议（"协议"）由 [{effectiveDate as "MMMM DD, YYYY"}] 签订，由以下双方签订：

**披露方：** [{disclosingParty}]
**接收方：** [{receivingParty}]

## 1. 保密信息

"保密信息"是指披露方披露的所有非公开信息，包括但不限于：
[{confidentialScope}]。

## 2. 义务

接收方同意：
- 维持保密期限为 [{termYears}] 年
- 仅将信息用于 [{permittedPurpose}]
- 未经书面同意，不得向第三方披露

## 3. 排除条款

本协议不适用于以下信息：
{{#if hasExclusions}}
[{exclusions}]
{{else}}
- 已公开或即将公开的信息
- 披露前已知晓的信息
- 独立开发的信息
{{/if}}

## 4. 材料返还

终止后，接收方应在 [{returnDays}] 天内返还或销毁所有保密信息。

## 5. 补救措施

{{#if monetaryPenalty}}
违反本协议将导致 [{penaltyAmount}] 的违约金。
{{else}}
披露方有权寻求禁令救济。
{{/if}}

**签字**

披露方： ____________________
日期： ____________________

接收方： ____________________
日期： ____________________
```

### data.json
```json
{
  "effectiveDate": "2024-01-15",
  "disclosingParty": "Tech Corp",
  "receivingParty": "Consultant LLC",
  "confidentialScope": "商业秘密、客户名单和技术规格",
  "termYears": 3,
  "permittedPurpose": "评估潜在的商业关系",
  "hasExclusions": false,
  "returnDays": 30,
  "monetaryPenalty": true,
  "penaltyAmount": "$50,000"
}
```

## 资源

- [Accord Project](https://accordproject.org/)
- [GitHub 组织](https://github.com/accordproject)
- [模板库](https://templates.accordproject.org/)
