## 何时使用此技能

当您需要执行以下操作时，请使用此技能：
- 为对象创建列表视图
- 生成基于列的过滤记录列表
- 配置列表视图的可见性和共享
- 排查与列表视图相关的部署错误

## 规格

# Salesforce 列表视图元数据知识

## 📋 概述
Salesforce 列表视图定义了对象选项卡上的基于列的过滤记录列表。

## 🎯 目的
- 提供经过筛选的、按角色或任务特定的记录子集
- 在团队之间标准化常用的过滤器和可见字段

## 🔧 配置

除非特别要求内联生成，列表视图存储在以下位置：
- force-app/main/default/objects/<ObjectName>/listViews/<fullName>.listView-meta.xml
只有当用户要求时，它们才会包含在对象的元数据文件中：
- fore-app/main/default/objects/<ObjectName>/<ObjectName>.object-meta.xml

关键元素：
- label：在 UI 中显示的友好名称（长度必须小于 40 个字符）
- fullName (fullName)：用于元数据和文件名的 API 标识符
- filterScope：全部 | 我的 | 队列
- filters：字段/操作/值三元组
- booleanFilterLogic：使用 AND/OR 逻辑组合多个过滤器（例如，“1 AND (2 OR 3)”）
- columns：要显示的字段 API 名称的有序列表

引用：
- listViews 出现在实体的选项卡上
- listViews 可以使用“filterListCard”组件被 flexipages 引用

### 关键决策：可见性策略
选择视图在组织中应显示的广泛程度。

**当选择“对所有用户可见”时：**
- 视图对多个配置文件/角色有用
- 它是一个受管理的、共享的工件，通过源代码控制进行管理
- 包含的数据适合广泛的可见性

**当选择“仅限所有者/限制”时：**
- 在迭代期间它是实验性或专业的
- 它被明确要求仅限于用户、组或角色
- 有治理/安全审查待处理

**不确定时：** 默认选择“对所有用户可见”。

### 关键决策：列密度
**当选择最小、高信号列时：**
- 用户需要快速扫描
- 移动端/响应式性能很重要

**当选择更丰富的列集时：**
- 桌面端为主的流程需要在不打开记录的情况下提供更多上下文
- 它作为工作队列，额外字段减少了点击次数

**不确定时：** 从 4-6 列开始，这些列直接支持主要任务。

## 关键规则（首先阅读）

### 规则 1：自定义字段 API 名称
对于自定义字段，请使用确切的 API 名称（例如，Status__c），而不是标签。

错误：
- Status (标签)

正确：
- Status__c (API 名称)

### 规则 2：标准字段名称
对于自定义对象上的标准字段，请使用已定义的名称：

错误：
- Name (API 名称)

正确：
- NAME

自定义对象上的标准字段是：
- NAME
- RECORDTYPE
- OWNER.ALIAS
- OWNER.FIRST_NAME
- OWNER.LAST_NAME
- CREATEDBY_USER.ALIAS
- CREATEDBY_USER
- CREATED_DATE
- UPDATEDBY_USER.ALIAS
- UPDATEDBY_USER
- LAST_UPDATE
- LAST_ACTIVITY

### 规则 3：操作必须与字段类型匹配
选择列表需要 equals/notEqual；日期字段需要日期操作符；布尔值是 0 和 1；不要将纯文本操作符与非文本字段混合。

错误：
- operation="contains" 在选择列表上
- value=True 在布尔值上

正确：
- operation="equals" 并使用有效的选择列表值
- value=1 在布尔值上

### 规则 4：名称和路径一致性
文件名、fullName（有时也称为 DeveloperName）和唯一性必须一致。

错误：
- 文件：My_List.listView-meta.xml
- fullName：MyList

正确：
- 文件：MyList.listView-meta.xml
- fullName：MyList

### 规则 5：文件夹位置
将文件放置在对象的 listViews 目录下，否则部署将无法解析组件。只有当用户要求时，列表视图才可能内联包含在 force-app/main/default/objects/<ObjectName>/<ObjectName>.object-meta.xml 中。

路径：
- force-app/main/default/objects/<ObjectName>/listViews/<fullName>.listView-meta.xml

## 生成工作流

### 第 1 步：获取元数据信息
- 确定目标对象 API 名称（例如，Object__c）。
- 收集业务需求：目的、受众、字段、过滤器。
- 验证值和操作符与字段类型的兼容性。

### 第 2 步：检查现有示例
- 仓库：force-app/main/default/objects/<Object>/listViews/（除非用户另有要求）
- 组织：检索现有的列表视图以获取经过验证的模式（过滤器、逻辑、列）。
- 记录通过审核/部署的内容和预期的用户体验。

### 第 3 步：创建规范
在实施之前记录：
- 名称：fullName 和 Label
- 受众：可见性范围（“所有用户”与共享）
- 过滤范围：全部 | 我的 | 队列
- 过滤项：过滤器、操作符、值；如果多个，则加上 booleanFilterLogic
- 列：字段 API 名称的有序列表
- 接受标准：哪些记录出现、分页行为、关键场景

### 第 4 步：编写元数据文件
使用 Lightning 兼容模板并确保有效的 XML：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ListView xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>OpenMine</fullName>
    <label>Open - 我的记录</label>
    <filterScope>Mine</filterScope>
    <columns>NAME</columns>
    <columns>Status__c</columns>
    <columns>OWNER.ALIAS</columns>
    <columns>LAST_UPDATE</columns>
    <filters>
        <field>Status__c</field>
        <operation>equals</operation>
        <value>Open</value>
    </filters>
    <sharedTo>
        <role>CEO</role>
        <roleAndSubordinatesInternal>COO</roleAndSubordinatesInternal>
    </sharedTo>
</ListView>
```

注意：
- 对于“我的”视图，使用 filterScope="Mine"。
- 保持列紧密且目的明确。
- 如果打算供所有用户使用，请省略“sharedTo”部分。

### 第 5 步：本地验证
- 有效的 XML；正确的命名空间
- 字段名称存在于对象上；操作符和值与字段类型匹配
- 路径和 fullName 一致
- 如果有多个过滤器：正确设置 booleanFilterLogic（例如，“1 AND (2 OR 3)”）

### 第 6 步：在组织中部署和验证
- 部署组件路径或整个对象。
- 在 UI 中打开对象选项卡并：
    - 确认记录与过滤器匹配
    - 确认列正确渲染
    - 确认可见性与受众一致

## 常见部署错误

| 错误 | 原因                                                                                       | 修复                                                                                |
|-------|---------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| "无效字段 Status" | 使用了标签而不是 API 名称，或使用了 API 名称而不是定义的标准字段名称 | 使用 Status__c（或正确的 API 名称），或使用 NAME 而不是 Name（对于标准字段） |
| "无效过滤器操作符" | 操作符对字段类型无效  | 选择与字段类型兼容的操作符（例如，选择列表的 equals）            |
| "路径上找不到组件" | 错误的文件夹或文件名  | 放置在 objects/<Object>/listViews 下，并使文件名与 fullName 对齐              |
| "Malformed booleanFilterLogic" | 语法或索引不匹配  | 使用 "1 AND 2" 风格，确保过滤器索引顺序匹配                            |

## 验证清单
- [ ] 所有必需字段已填写（fullName、label、filterScope、columns）
- [ ] 属性值在需要时已 XML 编码
- [ ] 自定义字段引用使用 API 名称（例如，Status__c）
- [ ] 标准字段引用使用定义的名称（例如，NAME）
- [ ] 操作符与字段类型匹配；选择列表值有效
- [ ] booleanFilterLogic（如果使用）与过滤器顺序和数量匹配
- [ ] 文件路径和 fullName/developerName 一致
- [ ] 未包含已弃用或仅限 Classic 的属性
- [ ] 成功部署且可见性符合预期
- [ ] 记录、列和过滤行为符合预期
