# 生成 Apex

使用此技能生成生产级 Apex：新类、选择器、服务、异步作业、可调用方法以及触发器；以及针对现有 `.cls` 或 `.trigger` 的基于证据的审查。

## 必需输入

在编写前收集或推断：

- 类类型（服务、选择器、域、批处理、队列式、可计划、可调用、触发器、触发器操作、DTO、实用程序、接口、抽象、异常、REST 资源）
- 目标对象和业务目标
- 类名（使用下表中的命名规则导出）
- 全新开发与重构/修复；任何组织/API 限制
- 部署目标（默认为 `runSpecifiedTests` 并在适用情况下使用生成的测试）

默认值（除非指定）：

- 分享：`with sharing`（见每种类型的分享规则）
- 访问权限：`public`（仅在受管理包或 `@RestResource` 需要时使用 `global`）
- API 版本：`66.0`（最低版本）
- ApexDoc 注释：是

如果用户提供清晰、完整的请求，则立即生成，无需不必要的来回沟通。

---

## 工作流程

所有步骤都是按顺序执行的。不要跳过、合并或重新排序。如果遇到障碍，请停止并请求缺失的上下文。如果不适用，请在报告中用一句话说明 `N/A` 并提供理由。

### 第一阶段 — 编写

1. **发现项目约定**
   - 服务-选择器-域分层结构、日志实用程序
   - 现有类/触发器和当前触发器框架或处理模式
   - 是否已使用触发器操作框架（TAF）

2. **选择最小的正确模式**（见类型特定指导）

3. **审查模板和资源**
   - 在编写前从 `assets/` 中读取匹配的模板（见类型特定指导的文件映射）
   - 当类型存在 `references/` 示例时，将其作为具体的样式指南读取
   - 对于任何测试类工作，始终读取并使用 `platform-apex-test-generate` 技能

4. **受约束的编写** -- 应用以下规则中的每一条
   - 使用 ApexDoc 生成 `{ClassName}.cls`
   - 生成 `{ClassName}.cls-meta.xml`   

5. **生成测试类** -- 加载技能 `platform-apex-test-generate` 以创建 `{ClassName}Test.cls` 和 `{ClassName}Test.cls-meta.xml`。Apex 测试始终需要生成才能部署。没有测试文件创建或编辑可以不加载 `platform-apex-test-generate` 技能来生成测试。

### 第二阶段 — 验证（报告前必须执行）

编写文件是中途点，不是终点。步骤 6 和 7 各需要一次工具调用，并产生必须在步骤 8 报告中出现的输出。在两个步骤都运行并捕获其输出之前，不要总结或展示报告。

6. **运行代码分析器**
   - 对所有生成的/更新的 `.cls` 文件调用 MCP `run_code_analyzer`。
   - 修复所有 `sev0`、`sev1` 和 `sev2` 违规；重新运行直到干净。
   - 原封不动地捕获最终工具输出以供报告。
   - 备用方案：`sf code-analyzer run --target <target>`。如果两者都不可用，请在报告中记录 `run_code_analyzer=unavailable: <error>`。

7. **执行 Apex 测试**
   - 通过 `sf apex run test` 或 MCP 运行 org 测试，包括 `{ClassName}Test`。
   - 将所有测试生成/修复/覆盖率工作委托给 `platform-apex-test-generate`；迭代直到测试通过。
   - 捕获通过/失败计数和覆盖率百分比以供报告。
   - 如果不可用，请在报告中记录 `test_execution=unavailable: <error>`。

### 第三阶段 — 报告

8. **报告** -- 使用本文件底部的输出格式。
   - `Analyzer` 行必须包含实际步骤 6 的工具输出（或在尝试调用后记录 `run_code_analyzer=unavailable: <reason>`）。
   - `Testing` 行必须包含实际步骤 7 的结果（或在尝试调用后记录 `test_execution=unavailable: <reason>`）。
   - 缺少任何一行的报告是不完整的。始终在记录不可用之前尝试工具调用。

---

## 规则

### 硬停止约束（必须强制执行）

如果任何约束会在生成的代码中违规，**在继续之前停止并解释问题**：

| 约束 | 理由 |
|---|---|
| 将所有 SOQL 放在循环外 | 避免查询治理器限制（100 个查询） |
| 将所有 DML 放在循环外 | 避免DML治理器限制（150 个语句） |
| 在每个类上声明分享关键字 | 防止意外的 `without sharing` 默认值和数据暴露 |
| 使用自定义元数据/标签/描述调用，而不是硬编码 ID | 确保跨组织可移植性 |
| 始终处理异常（记录、重新抛出或恢复） | 防止静默失败 |
| 使用绑定变量处理所有带有用户输入的动态 SOQL | 防止 SOQL 注入 |
| 使用 Apex 原生集合（`List`、`Map`、`Set`），而不是 Java 类型 | 防止编译错误 |
| 在使用前验证 Apex 中是否存在方法 | 防止依赖不存在的 API |
| 在主代码路径中避免使用 `System.debug()` | 调试语句即使在日志未激活时也会执行并消耗 CPU。如果主代码路径需要日志，请使用日志框架 |
| 永远不要使用 `@future` 方法 | 使用带有 `System.Finalizer` 的 Queueable；`@future` 不能链式调用，不能从 Batch 调用，不能接受非原始类型 |

### 批量化和治理器限制

- 所有公共 API 接受并处理集合；单记录重载委托给批量方法
- 在批处理/批量流程中，优先使用部分成功 DML（`Database.update(records, false)`）并处理 `SaveResult` 以获取错误
- 使用 `Map<Id, SObject>` 构造函数从查询结果中进行高效的 ID 基于查找
- 使用 `Map<Id, List<SObject>` 将子记录按父记录分组；在处理前在一个循环中构建该映射
- 使用 `Set<Id>` 进行去重和成员检查；优先使用 `Set.contains()` 而不是 `List.contains()`
- 使用关系子查询在需要时同时获取父记录和子记录
- 使用 `AggregateResult` 与 `GROUP BY` 进行汇总计算，而不是在 Apex 中查询和计数
- 仅 DML 记录实际发生变化 — 在将其添加到更新列表之前，与 `Trigger.oldMap` 或先前状态进行比较
- 使用 `Limits.getQueries()`、`Limits.getDmlStatements()`、`Limits.getCpuTime()` 监控复杂事务中的消耗

### SOQL 优化

- 使用选择性查询并带有适当的 `WHERE` 子句；在可能的情况下使用索引字段（`Id`、`Name`、`OwnerId`、查找/主从字段、`ExternalId` 字段、自定义索引）作为过滤器
- SOQL 中不存在 `SELECT *` —— 始终指定所需的精确字段
- 对有界结果集应用 `LIMIT` 子句；使用 `ORDER BY` 获取确定性结果
- 查询自定义元数据类型（以 `__mdt` 结尾的对象）时，**不要**使用 SOQL — 使用内置方法（`{CustomMdt__mdt}.getAll().values()`、`getInstance()` 等）
- 在 API 版本为 67.0 及以上的 `without sharing` 关键字类中执行的查询将在运行用户没有适当字段或对象级安全时抛出。如果正在更新 API 版本，请确保查询正确保护，并相应地更新测试。默认情况下，只有明确说明的查询中 `SYSTEM_MODE` 变体的使用才应该被允许。

### 缓存

- 使用平台缓存（`Cache.Org` / `Cache.Session`）用于频繁访问、很少更改的数据；设置 TTL 并始终处理缓存未命中 — 缓存可能随时被清除
- 使用 `private static Map` 字段作为事务范围缓存，以防止在同一执行上下文中重复查询；第一次访问时懒加载

### 安全

- 默认为 `with sharing`；记录 `without sharing` 或 `inherited sharing` 的理由
- 在 SOQL 中使用 `WITH USER_MODE`，在 `Database` DML 中使用 `AccessLevel.USER_MODE` 以强制执行 CRUD/FLS — 这些是 API 版本为 67.0 或更高的所有 Apex 类的默认值
- 通过允许列表或 `Schema.describe` 验证动态字段/操作名称
- 所有外部凭证/API 密钥使用命名凭证
- `AuraHandledException` 用于 `@AuraEnabled` 用户界面错误（不显示内部详细信息）
- `without sharing` 需要自定义权限检查
- 将 `without sharing` 逻辑隔离在专用辅助类中；从 `with sharing` 入口点调用以限制提升访问权限的范围
- 通过平台加密在静态时加密 PII/敏感数据；永远不要在调试语句、错误消息或 API 响应中暴露 PII

### 安全验证

在最终确定前验证：CRUD/FLS 强制执行（SOQL + DML） · 每个类都有显式的分享关键字 · 没有硬编码的密钥或记录 ID · PII 排除在日志和错误消息之外 · 错误消息对最终用户进行了清理。

### 错误处理

- 在通用 `Exception` 之前捕获特定异常；在消息中包含上下文
- 仅在可能抛出代码周围使用 `try/catch`（DML、调用外部系统、JSON 解析、类型转换）；避免对简单的赋值/集合操作/算术进行防御性包装
- 保留异常原因链：`new CustomException('message', cause)`（不要用连接的消息替换堆栈跟踪）
- 在服务域中提供自定义异常类，当有意义时
- 在 `@AuraEnabled` 方法中捕获异常并作为 `AuraHandledException` 重新抛出
- 备用选项：当没有有意义的域异常时，捕获通用 `Exception` 并要么重新抛出它，要么将其包装在保留原始原因的最小自定义异常中。

### 空值安全

- 在每个公共方法的顶部添加空值/空输入的守卫子句；根据上下文匹配样式：在私有/触发器处理程序方法中提前返回，在公共 API 中抛出异常，在验证服务中 `record.addError()`
- 返回空集合而不是 `null`
- 使用安全导航（`?.`）进行链式属性访问
- 除非保证存在，否则永远不要内联取消引用 `map.get(key)`；首先使用 `containsKey`、赋值 + 空值检查或安全导航
- 使用空值合并（`??`）为默认值
- 优先使用 `String.isBlank(value)` 而不是手动检查，如 `value == null || value.trim().isEmpty()`

### 常量 & 字面量

- 尽可能使用枚举而不是字符串常量；枚举值遵循 `UPPER_SNAKE_CASE`
- 将重复的常量字符串/数字提取到 `private static final` 常量或常量类中
- 使用 `Label.` 自定义标签用于用户界面字符串
- 使用自定义元数据用于可配置值（阈值、映射、功能标志）
- 永远不要在代码中输出 HTML 转义实体（例如，`&#39;`）；在 Apex 字符串字面量中使用单引号 `'` 

### 命名约定

| 类型 | 模式 | 示例 |
|---|---|---|
| 服务 | `{SObject}Service` | `AccountService` |
| 选择器 | `{SObject}Selector` | `AccountSelector` |
| 域 | `{SObject}Domain` | `OpportunityDomain` |
| 批处理 | `{描述性}Batch` | `AccountDeduplicationBatch` |
| 队列式 | `{描述性}Queueable` | `ExternalSyncQueueable` |
| 可计划 | `{描述性}Schedulable` | `DailyCleanupSchedulable` |
| DTO | `{描述性}DTO` | `AccountMergeRequestDTO` |
| 包装器 | `{描述性}Wrapper` | `OpportunityLineWrapper` |
| 实用程序 | `{描述性}Util` | `StringUtil` |
| 接口 | `I{描述性}` | `INotificationService` |
| 抽象 | `Abstract{描述性}` | `AbstractIntegrationService` |
| 异常 | `{描述性}Exception` | `AccountServiceException` |
| REST 资源 | `{SObject}RestResource` | `AccountRestResource` |
| 触发器 | `{SObject}Trigger` | `AccountTrigger` |
| 触发器操作 | `TA_{SObject}_{操作}` | `TA_Account_SetDefaults` |

附加命名规则：

- 类：`PascalCase`
- 方法：`camelCase`，以动词开头（`get`、`create`、`process`、`validate`、`is`、`has`、`can`）
- 变量：`camelCase`，描述性名词；列表作为复数名词（例如，`accounts`、`relatedContacts`）；映射作为 `{值}By{键}`（例如，`accountsById`）；集合作为 `{名词}Ids`
- 常量：`UPPER_SNAKE_CASE`
- 使用完整的描述性名称，而不是缩写（`acc`、`tks`、`rec`）

### ApexDoc

- 类头和每个 `public`/`global` 方法都需要
- 包括：简要描述、`@param`、`@return`、`@throws`、`@example`（如有帮助）

类级别格式：

```apex
/**
 * 提供地理位置和地址转换服务。
 */
public with sharing class GeolocationService { }
```

方法级别格式：

```apex
/**
 * @param paramName 参数的描述
 * @return 返回值的描述
 * @example
 * List<Account> results = AccountService.deduplicateAccounts(accountIds);
 */
```

### 代码结构 & 架构

- 每个类只有一个职责；最大 500 行 -- 超过时拆分
- 提前返回：在方法顶部验证先决条件，立即返回/抛出
- 将超过 40 行的方法提取为私有辅助方法
- 使用依赖注入（构造函数/方法参数）以提高可测试性
- 优先使用组合和窄接口，而不是深度继承；通过新的实现扩展，而不是修改
- 在层边界上每个方法强制执行单级抽象：

| 层 | 拥有 | 必须不包含 |
|---|---|---|
| 触发器 | 仅事件路由 | 业务逻辑、编排 |
| 处理程序/服务 | 流程控制、协调 | 内联 SOQL/DML/HTTP/解析 |
| 域 | 业务规则、验证 | 查询、调用外部系统、持久化细节 |
| 数据/集成 | SOQL、DML、HTTP | 业务决策 |

- 禁止：混合编排与内联 SOQL/DML/HTTP 的方法；将业务规则与解析内部混合；一个方法中混合验证 + 持久化 + 跨系统管道

---

## 异步决策矩阵

| 情景 | 默认 | 关键特征 |
|---|---|---|
| 标准异步工作 | **Queueable** | 作业 ID、链式调用、非原始类型、可配置延迟（通过 `AsyncOptions` 最多 10 分钟）、去重签名 |
| 非常大的数据集 | **Batch Apex** | 分块处理、最大 5 个并发；使用 `QueryLocator` 处理大范围 |
| 现代批处理替代方案 | **CursorStep** (`Database.Cursor`) | 2000 记录分块、更高吞吐量、无 5 个作业限制 |
| 定期计划 | **Scheduled Flow**（首选）或 **Schedulable** | 可计划有 100 个作业限制；仅在需要将 Batch 链式调用或需要复杂 Apex 逻辑时使用 |
| 作业后清理 | **Finalizer** (`System.Finalizer`) | 无论 Queueable 成功/失败都会运行 |
| 长时间调用外部系统 | **Continuation** | 每个事务最多 3 个，3 个并行 |
| 超过 10 分钟的延迟 | `System.scheduleBatch()` | 在特定未来时间安排 Batch 作业 |
| 遗留的“发射并忘记” | `@future` | **新代码中不要使用** — 见硬停止约束；用 Queueable + Finalizer 替换 |

---

## 类型特定指导

### 服务
- 模板：`assets/service.cls` · 参考：`references/AccountService.cls`
- `with sharing`；无状态 — 没有 `public` 字段或可变实例状态；公共 API 聚焦并尽可能使用 `static`
- 将所有 SOQL 委托给选择器，将 SObject 行为委托给域
- 将业务错误包装在自定义异常中（例如，`AccountServiceException`）

### 选择器
- 模板：`assets/selector.cls` · 参考：`references/AccountSelector.cls`
- `inherited sharing`；每个 SObject 或查询域一个
- 返回 `List<SObject>` 或 `Map<Id, SObject>`；使用共享的基本字段列表常量（无内联重复）
- 接受过滤参数；始终包含 `WITH USER_MODE`

### 域
- 模板：`assets/domain.cls`
- `with sharing`；封装字段默认值、派生和验证
- 仅在内存列表上操作；没有 SOQL/DML（属于服务/选择器）

### 批处理
- 模板：`assets/batch.cls` · 参考：`references/AccountDeduplicationBatch.cls`
- `with sharing`；实现 `Database.Batchable<SObject>`（当跨块跟踪时添加 `Database.Stateful`）
- `start()` = 查询定义；`execute()` = 业务逻辑；`finish()` = 日志/通知
- 使用 `QueryLocator` 处理大数据集；通过 `Database.SaveResult` 处理部分失败
- 通过构造函数接受过滤参数以实现可重用性

### 队列式
- 模板：`assets/queueable.cls`
- `with sharing`；实现 `Queueable`，当需要 HTTP 调用外部系统时可选实现 `Database.AllowsCallouts`
- 通过构造函数接受数据
- 添加链式深度保护以防止无限链
- 可选实现 `Finalizer` 以进行恢复/清理
- 使用 `AsyncOptions` 进行可配置延迟（通过 `AsyncOptions` 最多 10 分钟）和去重签名

### 可计划
- 模板：`assets/schedulable.cls`
- `with sharing`；`execute()` 委托给 Queueable 或 Batch
- 提供CRON常量和 `scheduleDaily()` 辅助方法

### DTO / 包装器
- 模板：`assets/dto.cls`
- 无需分享关键字（纯数据容器）
- 简单的公共属性；无参构造函数 + 参数化构造函数；`Comparable` 当排序很重要时
- 使用 `@JsonAccess` 在需要序列化/反序列化的私有/受保护的内部 DTO 上

### 实用程序
- 模板：`assets/utility.cls`
- 无需分享关键字；所有方法 `public static`；私有构造函数
- 纯粹的、无副作用的；没有 SOQL/DML

### 接口
- 模板：`assets/interface.cls`
- 在每个方法签名上使用 ApexDoc 定义清晰的合同

### 抽象
- 模板：`assets/abstract.cls`
- `with sharing`；通过 `virtual` 方法提供默认行为
- 将扩展点标记为 `protected virtual` 或 `protected abstract`
- 在 ApexDoc 中包含一个具体示例，说明如何扩展该类

### 自定义异常
- 模板：`assets/exception.cls`
- 无需分享关键字；使用描述性名称扩展 `Exception`
- 支持的构造函数：`()`、`('msg')`、`(cause)`、`('msg', cause)`

### 触发器
- 模板：`assets/trigger.cls`
- 每个对象一个触发器；将所有逻辑委托给处理程序/TAF 操作类
- 包括所有相关的 DML 上下文；如果 TAF：`new MetadataTriggerHandler().run();`

### 触发器操作（TAF）
- 每个上下文每个关注点一个类；实现 `TriggerAction.{Context}`
- 通过 `Trigger_Action__mdt` 注册（没有注册，操作将处于非活动状态）
- 名称：`TA_{SObject}_{ActionName}`；优先使用字段值比较而不是静态布尔值进行递归

### 可调用方法 (`@InvocableMethod`)
- 模板：`assets/invocable.cls`
- `with sharing`；内部 `Request`/`Response` 使用 `@InvocableVariable`
- 方法必须是 `public static`；非静态或单对象签名将无法编译
- 接受 `List<Request>`，返回 `List<Response>`；批量化（SOQL/DML 在循环外）
- 装饰器参数：`label`（必需 — Flow Builder 显示名称）、`description`、`category`（在 Builder 中分组操作）、`callout=true`（当方法执行 HTTP 调用外部系统时必需）
- `@InvocableVariable` 参数：`label`（必需）、`description`、`required=true/false`
- `@InvocableVariable` 支持：原始类型、`Id`、`SObject`、`List<T>` 仅（没有 `Map`/`Set`/`Blob`）；使用 `List<Id>` 或 `List<SObject>` 字段进行 Flow 集合 I/O
- 始终在响应中包括 `isSuccess`、`errorMessage` 和 `errorType` (`e.getTypeName()`)
- 在响应中返回错误（推荐）；抛出异常触发 Flow 错误路径 — 仅用于不可恢复的失败

### REST 资源 (`@RestResource`)
- 模板：`assets/rest-resource.cls`
- `global with sharing`；类和方法都必须是 `global`
- 版本化 URL：`@RestResource(urlMapping='/{resource}/v1/*')`
- 使用适当的 HTTP 状态代码每个分支（`200`/`201`/`400`/`404`/`422`/`500`）；永远不要将所有错误默认为 `500`
- 验证输入（ID 格式：`Pattern.matches('[a-zA-Z0-9]{15,18}', value)`）；在 SOQL 中绑定所有用户输入
- 在查询中包含 `LIMIT`/`ORDER BY`；实现分页（`pageSize`/`offset`）
- 标准化 `ApiResponse` 包装器（`success`、`message`、`data`/`records`）；内部请求/响应 DTOs
- 薄控制器：将业务逻辑委托给服务类

### `@AuraEnabled` 控制器
- `with sharing`；在所有 SOQL 中使用 `WITH USER_MODE`
- 仅对只读查询使用 `@AuraEnabled(cacheable=true)`；将 `cacheable` 不设置用于 DML 操作
- 捕获异常并作为 `AuraHandledException` 重新抛出，使用对最终用户友好的消息

---

## 输出预期

每个类交付物：

- `{ClassName}.cls`
- `{ClassName}.cls-meta.xml`（除非指定，默认 API 版本 `66.0` 或更高）
- `{ClassName}Test.cls`（通过 `platform-apex-test-generate` 技能生成）
- `{ClassName}Test.cls-meta.xml`（通过 `platform-apex-test-generate` 技能生成）

每个触发器交付物：

- `{TriggerName}.trigger`
- `{TriggerName}.trigger-meta.xml`（除非指定，默认 API 版本 `66.0` 或更高）

Meta XML 模板：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ApexClass xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>{API_VERSION}</apiVersion>
    <status>Active</status>
</ApexClass>
```

报告按此顺序：

```text
Apex 工作： <摘要>
文件： <路径>
设计： <模式 / 框架选择>
工作流程： 所有步骤完成（1-8）；任何 N/A 都有理由
风险： <安全、批量化、异步、依赖项说明>
分析器： <必需 -- 粘贴实际 run_code_analyzer 输出或声明 "run_code_analyzer=unavailable: <reason>" >
测试： <必需 -- 粘贴实际测试执行结果（通过/失败、覆盖率）或声明 "test_execution=unavailable: <reason>" >
部署： <干运行或下一步>
```

---

## 跨技能集成

| 需要 | 委托给 |
|---|---|
| Apex 测试 / 修复失败 | `platform-apex-test-generate` 技能 |
| 描述对象/字段 | 元数据技能（如果可用） |
| 部署到组织 | 部署技能（如果可用） |
| Flow 调用 Apex | Flow 技能（如果可用） |
| LWC 调用 Apex | LWC 技能（如果可用） |

---

## 故障排除边界

此技能仅处理生产 `.cls`/`.trigger`/`.apex` 问题：编译/解析失败、部署依赖项错误、运行时治理器限制失败。对于测试执行、断言、覆盖率或 `sf apex run test` 失败，请委托给 `platform-apex-test-generate`.
