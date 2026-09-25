# Salesforce 开发者

## 核心工作流

1. **分析需求** - 理解业务需求、数据模型、治理限制、可扩展性
2. **设计解决方案** - 选择声明式与程序化、规划批量处理、设计集成方案
3. **实施** - 按最佳实践编写 Apex 类、LWC 组件、SOQL 查询
4. **验证治理限制** - 在继续前验证 SOQL/DML 计数、堆大小和 CPU 时间是否在平台限制范围内
5. **全面测试** - 编写覆盖率 90%+ 的测试类，测试批量场景（200 记录批次）
6. **部署** - 使用 Salesforce DX、沙盒环境、CI/CD 进行元数据部署

## 参考指南

根据上下文加载详细指导：

| 主题 | 参考 | 加载时机 |
|------|------|----------|
| Apex 开发 | `references/apex-development.md` | 类、触发器、异步模式、批量处理 |
| Lightning Web 组件 | `references/lightning-web-components.md` | LWC 框架、组件设计、事件、线服务 |
| SOQL/SOSL | `references/soql-sosl.md` | 查询优化、关系、治理限制 |
| 集成模式 | `references/integration-patterns.md` | REST/SOAP API、平台事件、外部服务 |
| 部署与 DevOps | `references/deployment-devops.md` | Salesforce DX、CI/CD、沙盒环境、元数据 API |

## 限制

### 必须执行
- 批量化 Apex 代码 — 在循环前收集 ID/记录，查询/DML 在循环外执行
- 编写测试类，代码覆盖率至少 90%，包括批量场景
- 使用带索引字段的筛选性 SOQL 查询；利用关系查询
- 使用适当的异步处理（批量、可排队、未来）处理耗时任务
- 实现适当的错误处理和日志记录；使用 `Database.update(scope, false)` 处理部分成功
- 使用 Salesforce DX 进行源驱动开发和元数据部署

### 严禁执行
- 在循环内执行 SOQL/DML（违反治理限制 — 请参阅下方的批量化触发器模式）
- 在代码中硬编码 ID 或凭证
- 创建无保护机制的递归触发器
- 跳过字段级安全性和共享规则检查
- 使用已弃用的 Salesforce API 或组件

## 代码模式

### 批量化触发器（正确模式）

```apex
// 正确：收集 ID，循环外查询一次
trigger AccountTrigger on Account (before insert, before update) {
    AccountTriggerHandler.handleBeforeInsert(Trigger.new);
}

public class AccountTriggerHandler {
    public static void handleBeforeInsert(List<Account> newAccounts) {
        Set<Id> parentIds = new Set<Id>();
        for (Account acc : newAccounts) {
            if (acc.ParentId != null) parentIds.add(acc.ParentId);
        }
        Map<Id, Account> parentMap = new Map<Id, Account>(
            [SELECT Id, Name FROM Account WHERE Id IN :parentIds]
        );
        for (Account acc : newAccounts) {
            if (acc.ParentId != null && parentMap.containsKey(acc.ParentId)) {
                acc.Description = 'Child of: ' + parentMap.get(acc.ParentId).Name;
            }
        }
    }
}
```

```apex
// 错误：循环内 SOQL — 违反治理限制
trigger AccountTrigger on Account (before insert) {
    for (Account acc : Trigger.new) {
        Account parent = [SELECT Id, Name FROM Account WHERE Id = :acc.ParentId]; // 错误
        acc.Description = 'Child of: ' + parent.Name;
    }
}
```

### 批量 Apex

```apex
public class ContactBatchUpdate implements Database.Batchable<SObject> {
    public Database.QueryLocator start(Database.BatchableContext bc) {
        return Database.getQueryLocator([SELECT Id, Email FROM Contact WHERE Email = null]);
    }
    public void execute(Database.BatchableContext bc, List<Contact> scope) {
        for (Contact c : scope) {
            c.Email = 'unknown@example.com';
        }
        Database.update(scope, false); // 允许部分成功
    }
    public void finish(Database.BatchableContext bc) {
        // 发送通知或链式下一个批次
    }
}
// 执行：Database.executeBatch(new ContactBatchUpdate(), 200);
```

### 测试类

```apex
@IsTest
private class AccountTriggerHandlerTest {
    @TestSetup
    static void makeData() {
        Account parent = new Account(Name = 'Parent Co');
        insert parent;
        Account child = new Account(Name = 'Child Co', ParentId = parent.Id);
        insert child;
    }

    @IsTest
    static void testBulkInsert() {
        Account parent = [SELECT Id FROM Account WHERE Name = 'Parent Co' LIMIT 1];
        List<Account> children = new List<Account>();
        for (Integer i = 0; i < 200; i++) {
            children.add(new Account(Name = 'Child ' + i, ParentId = parent.Id));
        }
        Test.startTest();
        insert children;
        Test.stopTest();

        List<Account> updated = [SELECT Description FROM Account WHERE ParentId = :parent.Id];
        System.assert(!updated.isEmpty(), 'Children 应该有描述设置');
        System.assert(updated[0].Description.startsWith('Child of:'), '描述格式不匹配');
    }
}
```

### SOQL 最佳实践

```apex
// 筛选性查询 — 在 WHERE 子句中使用索引字段
List<Opportunity> opps = [
    SELECT Id, Name, Amount, StageName
    FROM Opportunity
    WHERE AccountId IN :accountIds      // 索引字段
      AND CloseDate >= :Date.today()    // 索引字段
    ORDER BY CloseDate ASC
    LIMIT 200
];

// 关系查询避免额外往返
List<Account> accounts = [
    SELECT Id, Name,
           (SELECT Id, LastName, Email FROM Contacts WHERE Email != null)
    FROM Account
    WHERE Id IN :accountIds
];
```

### Lightning Web 组件（计数器示例）

```html
<!-- counterComponent.html -->
<template>
    <lightning-card title="计数器">
        <div class="slds-p-around_medium">
            <p>计数：{count}</p>
            <lightning-button label="增加" onclick={handleIncrement}></lightning-button>
        </div>
    </lightning-card>
</template>
```

```javascript
// counterComponent.js
import { LightningElement, track } from 'lwc';
export default class CounterComponent extends LightningElement {
    @track count = 0;
    handleIncrement() {
        this.count += 1;
    }
}
```

```xml
<!-- counterComponent.js-meta.xml -->
<?xml version="1.0" encoding="UTF-8"?>
<LightningComponentBundle xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>59.0</apiVersion>
    <isExposed>true</isExposed>
    <targets>
        <target>lightning__AppPage</target>
        <target>lightning__RecordPage</target>
    </targets>
</LightningComponentBundle>
```

[文档](https://jeffallan.github.io/claude-skills/skills/platform/salesforce-developer/)
