# 生成 Apex 测试

生成适用于生产环境的 Apex 测试类，并执行有纪律的测试-修复循环，同时进行覆盖率分析。

## 核心原则

1. **每个方法一个行为** — 每个测试方法验证一个单一场景。分离正向、负向和批量测试。永远不要在一个方法中组合相关的但不同的输入（例如，null 和空值）— 将 `_NullInput_` 和 `_EmptyInput_` 作为单独的测试方法创建
2. **批量化测试** — 使用 251+ 条记录来跨越 200 条记录的触发器批处理边界。**批量 Apex 异常**：在测试上下文中只运行一个 `execute()` 调用，因此设置 `batchSize >= testRecordCount`。参见 [references/async-testing.md](references/async-testing.md)
3. **隔离测试数据** — 每个 `@TestSetup` 必须将记录创建委托给 `TestDataFactory` 类。如果不存在，请先创建一个。永远不要在 `@TestSetup` 中内联构建记录列表。永远不要依赖组织数据（`SeeAllData=false`）或硬编码的 ID。有关重复规则处理，参见 [references/test-data-factory.md](references/test-data-factory.md)
4. **有意义地断言** — 使用从测试数据设置中计算的确切预期值。当值是确定性时，永远不要使用范围断言或近似计数。始终包含失败消息。参见 [references/assertion-patterns.md](references/assertion-patterns.md)
5. **仅使用 `Assert` 类** — `Assert.areEqual`、`Assert.isTrue`、`Assert.fail` 等。永远不要使用遗留的 `System.assert`、`System.assertEquals` 或 `System.assertNotEquals`
6. **模拟外部边界** — 使用 `HttpCalloutMock` 进行调用，使用 `Test.setFixedSearchResults` 进行 SOSL，使用 DML 模拟类进行数据库隔离。通过构造函数注入进行可测试性设计。参见 [references/mocking-patterns.md](references/mocking-patterns.md)
7. **测试负向路径** — 验证错误处理和异常场景，而不仅仅是“快乐路径”
8. **用 start/stop 包裹** — 将 `Test.startTest()` 与 `Test.stopTest()` 配对以重置管理员限制并强制异步执行

## Test.startTest() / Test.stopTest()

始终将待测试代码包裹在 `Test.startTest()` / `Test.stopTest()` 中：

- 重置管理员限制，以便测试仅测量待测试代码
- 同步执行异步操作（队列式、批量、future 方法）
- 立即触发计划任务

## 测试代码反模式

| 反模式 | 修复 |
|---|---|
| 循环内的 SOQL/DML | 在循环之前查询一次；使用 `Map<Id, SObject>` 进行查找 |
| 断言中的魔法数字 | 从设置常量中派生预期值 |
| 神话测试类（>500 行） | 按行为区域拆分为多个测试类 |
| 长测试方法（>30 行） | 将 Given/When/Then 提取到辅助方法中 |
| 通用 `Exception` 捕获 | 捕获特定的预期类型（例如，`DmlException`） |

## 工作流程

### 第 1 步 — 收集上下文

在生成或修复测试之前，识别：

- 待测试的生产类
- 现有的测试类、测试数据工厂和设置辅助程序
- 期望的测试范围（单个类、特定方法、套件或本地测试）
- 覆盖率阈值（部署最低 75%，推荐 90%+）
- 运行测试时使用的组织别名

### 第 2 步 — 生成测试类

应用资产模板和参考文档中的结构、命名约定和模式。

**强制要求 — 文件交付物**：对于每个测试类，创建以下两个文件：
1. `{ClassName}Test.cls` — 测试类（使用 [assets/test-class-template.cls](assets/test-class-template.cls) 作为起点）
2. `{ClassName}Test.cls-meta.xml` — 元数据文件：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ApexClass xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>66.0</apiVersion>
    <status>Active</status>
</ApexClass>
```

如果项目中不存在 `TestDataFactory`，请使用 [assets/test-data-factory-template.cls](assets/test-data-factory-template.cls) 创建 `TestDataFactory.cls` + `TestDataFactory.cls-meta.xml`。

#### @TestSetup 示例

```apex
@TestSetup
static void setupTestData() {
    List<Account> accounts = TestDataFactory.createAccounts(251, true);
}
```

#### 测试方法结构

使用 Given/When/Then：

```apex
@isTest
static void shouldUpdateStatus_WhenValidInput() {
    // Given
    List<Account> accounts = [SELECT Id FROM Account];

    // When
    Test.startTest();
    MyService.processAccounts(accounts);
    Test.stopTest();

    // Then
    List<Account> updated = [SELECT Id, Status__c FROM Account];
    Assert.areEqual(251, updated.size(), '所有账户都应被处理');
}
```

#### 负向测试 — 异常模式

使用 try/catch 与 `Assert.fail` 验证预期异常：

```apex
@isTest
static void shouldThrowException_WhenInvalidInput() {
    // Given
    List<Account> emptyList = new List<Account>();

    // When/Then
    Test.startTest();
    try {
        MyService.processAccounts(emptyList);
        Assert.fail('预期抛出 MyCustomException');
    } catch (MyCustomException e) {
        Assert.isTrue(e.getMessage().contains('不能为空'),
            '异常消息应指示空输入');
    }
    Test.stopTest();
}
```

#### 命名约定

- `should[预期结果]_When[场景]`：`shouldSendNotification_WhenOpportunityClosedWon`
- `[主题或动作]_[场景]_[预期结果]`：`AccountUpdate_ChangeName_Success`

### 第 3 步 — 运行测试

调试时从窄范围开始；修复稳定后扩展范围。

```bash
# 单个测试类
sf apex run test --class-names MyServiceTest --result-format human --code-coverage --target-org <alias>

# 特定测试方法
sf apex run test --tests MyServiceTest.shouldUpdateStatus_WhenValidInput --result-format human --target-org <alias>

# 所有本地测试
sf apex run test --test-level RunLocalTests --result-format human --code-coverage --target-org <alias>
```

### 第 4 步 — 分析结果

关注：

- 失败的方法 — 异常类型和堆栈跟踪
- 未覆盖的行和弱覆盖区域
- 失败是否指示测试数据问题、脆弱的断言或生产逻辑损坏

### 第 5 步 — 修复循环

当测试失败时，执行有纪律的修复循环（最多 3 次迭代 — 如果仍然失败，停止并暴露根本原因）：

1. 阅读失败的测试类和待测试类
2. 从错误消息和堆栈跟踪中识别根本原因
3. 应用修复 — 调整测试数据或断言以解决测试端问题；将生产代码问题委托给 `generating-apex` 技能
4. 在更广泛的回归之前重新运行聚焦的测试
5. 重复直到所有测试通过、迭代次数达到上限或根本原因需要设计变更

### 第 6 步 — 验证覆盖率

| 级别 | 覆盖率 | 目的 |
|-------|----------|---------|
| 生产部署 | 最低 75% | Salesforce 的要求 |
| 推荐 | 90%+ | 最佳实践目标 |
| 关键路径 | 100% | 关键业务代码 |

覆盖所有路径：正向、负向/异常、批量（251+ 条记录）、调用/异步。

## 按组件测试什么

| 组件 | 关键测试场景 |
|-----------|-------------------|
| 触发器 | 批量插入/更新/删除、递归保护、字段变更检测 |
| 服务 | 有效/无效输入、批量操作、异常处理 |
| 控制器 | 页面加载、动作方法、视图状态 |
| 批量 | start/execute/finish、范围匹配（batchSize >= 记录数）、`Database.Stateful` 跟踪、错误处理、链式（分离方法 — `finish()` 调用 `Database.executeBatch()` 抛出 `UnexpectedException`） |
| 队列式 | 链式（测试中只有第一个作业运行）、批量化、错误处理、在 `Test.startTest()` 之前模拟调用 |
| 调用 | 成功响应、错误响应、超时 |
| 选择器 | 有效/空/空输入、批量（251+）、字段填充、排序顺序、通过 `System.runAs` 的 `WITH USER_MODE` |
| 计划 | 通过 `execute(null)` 直接执行、通过 `CronTrigger` 查询注册 CRON |
| 平台事件 | `Test.enableChangeDataCapture()`、`Test.getEventBus().deliver()`、验证订阅端副作用 |

## 输出预期

每个测试类交付物：
- `{ClassName}Test.cls` + `{ClassName}Test.cls-meta.xml`（与待测试类的 API 版本匹配；默认 `66.0`）
- `TestDataFactory.cls` + `TestDataFactory.cls-meta.xml`（如果不存在）

## 参考文件

按需加载以获取详细模式：

| 参考 | 使用场景 |
|-----------|-------------|
| [references/test-data-factory.md](references/test-data-factory.md) | `TestDataFactory` 模式、字段覆盖、重复规则处理 |
| [references/assertion-patterns.md](references/assertion-patterns.md) | 断言最佳实践、反模式、常见陷阱 |
| [references/mocking-patterns.md](references/mocking-patterns.md) | `HttpCalloutMock`、DML 模拟、StubProvider、SOSL、电子邮件、平台事件 |
| [references/async-testing.md](references/async-testing.md) | 批量、队列式、Future、计划任务测试 |
