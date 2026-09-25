# data360-schema-get 技能


## 概述

该技能使用 SSOT REST API 从 Salesforce Data Cloud 中检索数据湖对象 (DLO) 和数据模型对象 (DMO) 的架构信息。它可以列出组织中的所有 DLO 或 DMO，或检索特定 DLO 或 DMO 的详细架构。

## 使用场景

- 用户想要查看数据云组织中的所有 DLO 或 DMO
- 用户需要特定 DLO 或 DMO 的字段架构
- 用户正在探索数据云数据结构
- 用户需要了解 DLO 或 DMO 字段类型和元数据


## 前置条件

- 已安装 SF CLI 并认证到目标组织
- 组织已启用数据云
- 用户具有适当的数据云权限


## 技能执行

### 参数

1. **org_alias** (必需): SF CLI 组织别名（例如，'afvibe'，'myorg'）
2. **dlo_name** (可选): 特定 DLO 开发者名称（例如，'Employee__dll'）
3. **dmo_name** (可选): 特定 DMO 开发者名称（例如，'Individual__dlm'）

### 第 1 步：发现连接的组织

首先，运行 `sf org list` 找出连接的组织并提取用于后续所有调用的别名：

```bash
sf org list
```

示例输出：
```text
┌────┬───────┬──────────────────────────┬────────────────────┬───────────┐
│    │ Alias │ Username                 │ Org Id             │ Status    │
├────┼───────┼──────────────────────────┼────────────────────┼───────────┤
│ 🍁 │ myorg │ chandresh@afvidedemo.org │ 00DKZ00000b80NT2AY │ Connected │
└────┴───────┴──────────────────────────┴────────────────────┴───────────┘
```

从输出中提取 **Alias** 值（例如，`myorg`）并将其用作后续所有调用的 `<org_alias>`。使用 `--all` 可以查看过期的和已删除的沙盒组织。

### 第 2 步：验证 SF CLI 认证

在执行 API 调用之前，验证组织是否已连接：

```bash
sf org display --target-org <org_alias> --json
```

如果未连接，提示用户运行：
```bash
sf org login web --alias <org_alias>
```

### 第 3 步 a：执行 DLO 架构脚本

Python 脚本随此技能一起打包在 `scripts/` 子目录中。

**列出所有 DLO：**
```bash
python3 ./scripts/get_dlo_schema.py <org_alias>
```

**获取特定 DLO 架构：**
```bash
python3 ./scripts/get_dlo_schema.py <org_alias> <dlo_name>
```

### 第 3 步 b：执行 DMO 架构脚本

**列出所有 DMO：**
```bash
python3 ./scripts/get_dmo_schema.py <org_alias>
```

**获取特定 DMO 架构：**
```bash
python3 ./scripts/get_dmo_schema.py <org_alias> <dmo_name>
```

### 第 4 步：展示结果

以用户友好的格式解析并展示结果：

**对于 DLO 列表：**
- 显示 DLO 名称、标签、类别和 ID
- 指示总数
- 突出显示有数据的 DLO（totalRecords > 0）

**对于 DLO 架构：**
- 显示基本信息（名称、标签、类别、状态）
- 列出所有字段，包括：
  - 字段名称
  - 数据类型
  - 主键指示器
  - 可空状态
- 突出显示自定义字段（排除系统字段，如 DataSource__c、cdp_sys_*）
- 如果可用，显示记录数

**对于 DMO 列表：**
- 显示 DMO 名称、标签、类别和 ID
- 指示总数

**对于 DMO 架构：**
- 显示基本信息（名称、标签、类别、描述）
- 列出所有字段，包括：
  - 字段名称
  - 数据类型
  - 主键指示器
  - 可空状态
- 如果可用，显示数据空间信息

### 第 5 步：提供下一步操作建议

展示结果后，建议相关的后续操作：
- 从 DLO 查询数据
- 创建计算洞察
- 构建细分
- 设置数据流
- 创建 DMO 映射


## 使用的 API 端点

### 列出所有 DLO

```text
GET /services/data/v64.0/ssot/data-lake-objects
```

响应结构：
```json
{
  "dataLakeObjects": [
    {
      "name": "Employee__dll",
      "label": "Employee",
      "category": "Profile",
      "id": "1dlXXXXXXXXXXXXXXX",
      "status": "ACTIVE",
      "totalRecords": 12,
      "fields": [...]
    }
  ],
  "totalSize": 5
}
```

### 获取 DLO 架构

```text
GET /services/data/v64.0/ssot/data-lake-objects/{dlo_name}
```

响应结构（与列表响应中的单个对象相同，但以分页格式包装）。

### 列出所有 DMO

```text
GET /services/data/v64.0/ssot/data-model-objects
```

响应结构：
```json
{
  "dataModelObjects": [
    {
      "name": "Individual__dlm",
      "label": "Individual",
      "category": "Profile",
      "id": "0dmXXXXXXXXXXXXXXX",
      "fields": [...]
    }
  ],
  "totalSize": 10
}
```

### 获取 DMO 架构

```text
GET /services/data/v64.0/ssot/data-model-objects/{dmo_name}
```

响应结构（与列表响应中的单个对象相同，但以分页格式包装）。

## 错误处理

**常见问题：**

1. **组织未连接**
   - 消息："Org not connected"
   - 解决方案：提示用户通过 SF CLI 进行认证

2. **DLO 未找到**
   - 消息："DLO 'XYZ__dll' not found"
   - 解决方案：首先列出所有 DLO 以验证名称

5. **DMO 未找到**
   - 消息："DMO 'XYZ__dlm' not found"
   - 解决方案：首先列出所有 DMO 以验证名称

3. **权限问题**
   - 消息：HTTP 403 错误
   - 解决方案：验证用户具有数据云权限

4. **API 版本不匹配**
   - 当前：v64.0
   - 解决方案：脚本可以更新以支持较新的 API 版本


## 示例用法

**示例 1：列出所有 DLO**

```text
用户："Show me all DLOs in afvibe org"

响应：
1. 运行 sf org list 以发现连接的组织别名
2. 认证到 afvibe
3. 运行：python3 ./scripts/get_dlo_schema.py afvibe
4. 展示格式化的 DLO 列表
```

**示例 2：获取特定 DLO 架构**

```text
用户："Get the schema for Employee__dll in afvibe"

响应：
1. 运行 sf org list 以发现连接的组织别名
2. 认证到 afvibe
3. 运行：python3 ./scripts/get_dlo_schema.py afvibe Employee__dll
4. 展示字段架构，包括类型和元数据
```

**示例 3：探索 DLO 然后获取架构**

```text
用户："What DLOs exist in myorg and show me the schema for the Employee one"

响应：
1. 运行 sf org list 以发现连接的组织别名
2. 列出 myorg 中的所有 DLO
3. 确定 Employee__dll
4. 获取 Employee__dll 的详细架构
5. 展示结果
```

**示例 4：列出所有 DMO**

```text
用户："Show me all DMOs in afvibe org"

响应：
1. 运行 sf org list 以发现连接的组织别名
2. 认证到 afvibe
3. 运行：python3 ./scripts/get_dmo_schema.py afvibe
4. 展示格式化的 DMO 列表
```

**示例 5：获取特定 DMO 架构**

```text
用户："Get the schema for Individual__dlm in afvibe"

响应：
1. 运行 sf org list 以发现连接的组织别名
2. 认证到 afvibe
3. 运行：python3 ./scripts/get_dmo_schema.py afvibe Individual__dlm
4. 展示字段架构，包括类型和元数据
```

**示例 6：探索 DMO 然后获取架构**

```text
用户："What DMOs exist in myorg and show me the schema for the Individual one"

响应：
1. 运行 sf org list 以发现连接的组织别名
2. 列出 myorg 中的所有 DMO
3. 确定 Individual__dlm
4. 获取 Individual__dlm 的详细架构
5. 展示结果
```

## 输出格式

### DLO 列表输出

```text
Found 5 DLOs in org 'afvibe':

1. DataCustomCodeLogs__dll
   Label: DataCustomCodeLogs
   Category: Engagement
   Records: 233

2. Employee__dll
   Label: Employee
   Category: Profile
   Records: 12

[...]
```

### DLO 架构输出

```yaml
DLO: Employee__dll
Label: Employee
Category: Profile
Status: ACTIVE
Records: 12

自定义字段：
  • id__c (Text) - 主键
  • name__c (Text)
  • position__c (Text)
  • manager_id__c (Number)

系统字段：
  • DataSource__c (Text)
  • InternalOrganization__c (Text)
  • cdp_sys_SourceVersion__c (Text)

下一步操作：
- 查询数据：SELECT * FROM Employee__dll LIMIT 10
- 基于position字段创建细分
- 设置实时更新数据流
```

### DMO 列表输出

```text
Found 10 DMOs in org 'afvibe':

1. Individual__dlm
   Label: Individual
   Category: Profile

2. ContactPointEmail__dlm
   Label: Contact Point Email
   Category: Profile

[...]
```

### DMO 架构输出

```yaml
DMO: Individual__dlm
Label: Individual
Category: Profile
Description: Represents an individual person

字段：
  • Id__c (Text) - 主键
  • FirstName__c (Text)
  • LastName__c (Text)
  • BirthDate__c (DateTime)

下一步操作：
- 查询数据：SELECT * FROM Individual__dlm LIMIT 10
- 查看 DMO 到此 DMO 的映射
- 创建计算洞察
```

## 注意事项

- DLO 名称始终以 `__dll` 后缀结尾
- DMO 名称始终以 `__dlm` 后缀结尾
- 字段名称始终以 `__c` 后缀结尾
- 系统字段（DataSource__c、KQ_*、cdp_sys_*）会自动添加
- DLO 和 DMO 查询需要主键字段
- API 支持分页（limit/offset）以处理大型结果集


## 相关技能

- **datakit_workflow**: 用于 DMO 映射操作
- **datakit_validation**: 用于验证 datakit 配置
- 在创建 DMO 映射之前使用此技能以了解源 DLO 结构
