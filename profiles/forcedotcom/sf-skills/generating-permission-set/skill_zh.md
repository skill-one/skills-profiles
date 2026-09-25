## 何时使用此技能

在生成或编辑权限集元数据，或授予权限对象、字段、用户和应用程序权限时使用。

## 第 1 步：定义核心属性

首先定义所需的权限集属性：

```xml
<PermissionSet xmlns="http://soap.sforce.com/2006/04/metadata">
    <fullName>您的权限集名称</fullName>
    <label>管理员显示名称</label>
    <description>清晰描述用途和目标受众</description>
</PermissionSet>
```

**命名约定：**
- 使用描述性 API 名称（例如，`Sales_Manager_Access`）

## 第 2 步：配置对象权限

为标准对象和自定义对象添加 CRUD 权限：

```xml
<objectPermissions>
    <allowCreate>true</allowCreate>
    <allowRead>true</allowRead>
    <allowEdit>true</allowEdit>
    <allowDelete>false</allowDelete>
    <modifyAllRecords>false</modifyAllRecords>
    <viewAllRecords>false</viewAllRecords>
    <viewAllFields>false</viewAllFields>
    <object>Account</object>
</objectPermissions>
```

## 第 3 步：设置字段级安全

定义敏感或自定义字段的权限：

```xml
<fieldPermissions>
    <editable>true</editable>
    <readable>true</readable>
    <field>Account.SSN__c</field>
</fieldPermissions>
```

**重要：**
- 必须字段绝不能出现在字段权限列表中。平台不允许对必须字段设置字段级安全，这会导致部署失败。
- 在添加任何字段之前，请从对象元数据中确认该字段存在且不是必须字段
- 当其元数据包含 `<required>true</required>` 时，字段是必须字段：
- 公式字段不能编辑
- 主从字段是子（明细）对象上的必须字段

```xml
<fields>
    <fullName>FieldName__c</fullName>
    <required>true</required>
</fields>
```
- 使用 `ObjectName.FieldName` 格式引用字段
- 当用户需要编辑权限时，将 readable 和 editable 都设置为 true；editable 意味着 readable
- 如果所有字段都应该可见，可以改为启用 "viewAllFields" 对象权限

## 第 4 步：授予权限用户

为功能和功能添加系统级权限：

```xml
<userPermissions>
    <enabled>true</enabled>
    <name>ApiEnabled</name>
</userPermissions>
<userPermissions>
    <enabled>true</enabled>
    <name>RunReports</name>
</userPermissions>
```

**常见权限：**
- `ApiEnabled`：API 访问
- `ViewSetup`：查看设置菜单
- `ManageUsers`：用户管理
- `RunReports`：报告执行

**需要安全审核的权限：**
- `ViewAllData`：读取所有记录
- `ModifyAllData`：编辑所有记录
- `ManageUsers`：用户管理

## 第 5 步：配置应用程序和标签可见性

使应用程序和标签对用户可见：

```xml
<applicationVisibilities>
    <application>Sales_Console</application>
    <visible>true</visible>
</applicationVisibilities>
<tabSettings>
    <tab>CustomTab__c</tab>
    <visibility>Visible</visibility>
</tabSettings>
```

**应用程序可见性选项：**
- <visible> 可以是 true 或 false

**标签可见性选项：**
- `Visible`：标签在所有标签页上可用，并在其关联应用程序的可见标签中显示。可以自定义。
- `Available`：标签在所有标签页上可用。单个用户可以自定义显示，使标签在任何应用程序中可见
- `None`：不可见

**关键 - 标签命名：**
- 自定义对象标签：必须包含 __c 后缀（例如，MyCustomObject__c）
- 标准对象标签：使用带有 "standard-" 前缀的对象名称（例如，standard-Account, standard-Contact）
- 标签名称与对象的 API 名称完全匹配

## 第 6 步：添加 Apex 和 Visualforce 访问（可选）

授予权限以访问自定义代码：

```xml
<classAccesses>
    <apexClass>CustomController</apexClass>
    <enabled>true</enabled>
</classAccesses>
<pageAccesses>
    <apexPage>CustomPage</apexPage>
    <enabled>true</enabled>
</pageAccesses>
```

## 第 7 步：设置许可证和记录类型设置（可选）

指定许可证要求和记录类型可见性：

```xml
<license>Salesforce</license>
<hasActivationRequired>false</hasActivationRequired>
<recordTypeVisibilities>
    <recordType>Account.Business</recordType>
    <visible>true</visible>
    <default>true</default>
</recordTypeVisibilities>
```
## 第 8 步：设置代理访问（可选）
                                              
为分配到此权限集的用户启用对 Agentforce 员工代理的访问：

<agentAccesses>
    <agentName>Sales_Assistant_Agent</agentName>
    <enabled>true</enabled>
</agentAccesses>

字段要求：
- agentName (必需)：员工代理的开发者名称
- enabled (必需)：设置为 true 以授予权限，设置为 false 以拒绝

重要：
- 代理名称必须与现有的 Agentforce 员工代理开发者名称匹配

## 验证清单

在部署之前，请验证：
- [ ] fullName, label, description 已设置
- [ ] 权限遵循最小权限原则
- [ ] `<fieldPermissions>` 中没有必须字段
- [ ] 没有重复权限
- [ ] 没有长篇评论

## 部署失败的原因

- **必须字段的字段权限：** `<fieldPermissions>` 中的任何必须字段都会导致部署失败。必须字段不能有 FLS；完全省略它们。始终从对象/字段元数据中确认字段存在且不是必须字段——切勿假设。
- **错误的 API 名称：** 使用错误名称或缺少后缀（例如，自定义对象、字段、标签缺少 `__c`）会导致失败。

## 部署

使用 Salesforce CLI 部署
