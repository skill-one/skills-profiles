# /tdd -- .NET 的红绿重构

## 什么是

指导 .NET 功能的严格测试驱动开发周期。与其先编写实现再附加测试，这个命令会颠倒顺序：先编写一个失败的测试来定义所需行为，然后实现使其通过的最小代码，再带着信心进行重构。

每个周期都使用 .NET 测试栈：
- **xUnit v3** -- 具有 `[Fact]` 和 `[Theory]` 的测试框架
- **WebApplicationFactory** -- 针对真实 HTTP 管道的集成测试
- **Testcontainers** -- 测试中的真实数据库（PostgreSQL、SQL Server）
- **Verify** -- 复杂响应结构的快照测试
- **FakeTimeProvider** -- 测试中的确定性时间

## 何时使用

- 用户说 "TDD"、"测试驱动"、"我们来 TDD 这个"、"先写测试"
- 构建具有明确验收标准的全新功能
- 修复 Bug（先编写重现 Bug 的测试，然后修复）
- 向现有功能添加行为（先测试新行为）
- 任何用户希望在代码发布前验证其功能的时候

**跳过 TDD 的情况：** 简单的配置更改、无逻辑的脚手架、文档。

## 如何使用

### 周期：红 -> 绿 -> 重构

每个功能会经历一个或多个 TDD 周期。一个周期覆盖一个独立的特性。

#### 第 1 步：红 -- 编写失败的测试

编写一个描述所需行为的测试。由于实现尚不存在，测试必须失败。

```csharp
[Fact]
public async Task CreateOrder_WithValidItems_Returns201WithOrderId()
{
    // Arrange
    var client = _factory.CreateClient();
    var request = new CreateOrderRequest([
        new OrderItemRequest("SKU-001", 2, 29.99m)
    ]);

    // Act
    var response = await client.PostAsJsonAsync("/api/orders", request);

    // Assert — 简单的 xUnit Assert（FluentAssertions v8+ 需要商业许可）
    Assert.Equal(HttpStatusCode.Created, response.StatusCode);
    var result = await response.Content.ReadFromJsonAsync<CreateOrderResponse>();
    Assert.NotNull(result);
    Assert.NotEqual(Guid.Empty, result.OrderId);
}
```

运行测试并确认其失败：
```bash
dotnet test --filter "CreateOrder_WithValidItems_Returns201WithOrderId"
```

如果测试在未实现的情况下通过，则测试没有测试你想要测试的内容。重写它。

#### 第 2 步：绿 -- 最小实现

编写使测试通过的最小代码。不要添加功能、优化或边缘情况处理。目标是绿色的测试，仅此而已。

- 根据需要创建端点、处理器、请求/响应类型和 EF 配置
- 使用满足测试断言的最简单逻辑
- 不要重构——在这个阶段，丑陋的通过代码是允许的

运行测试并确认其通过：
```bash
dotnet test --filter "CreateOrder_WithValidItems_Returns201WithOrderId"
```

#### 第 3 步：重构 -- 带着信心进行清理

现在测试是绿色的，可以自由重构：
- 提取方法、重命名变量、改进结构
- 应用现代 C# 模式（主构造函数、记录、集合表达式）
- 添加验证、错误处理和边缘情况（每个新测试一个）
- 在每次重构步骤后运行完整测试套件以捕获回归

```bash
dotnet test
```

如果在重构期间任何测试变红，则撤销上一次更改并尝试更小的步骤。

### 多周期功能

大多数功能需要多个 TDD 周期。提前规划周期：

```
功能：订单管理

周期 1：使用有效项创建订单 -> 201
周期 2：使用空项创建订单 -> 400 验证错误
周期 3：使用无效 SKU 创建订单 -> 400 带有特定错误
周期 4：通过 ID 获取订单 -> 200 带有完整订单详情
周期 5：获取不存在的订单 -> 404
```

每个周期添加一个行为。永远不要在单个周期中组合多个行为。

### 测试基础设施设置

如果项目缺乏测试基础设施，在第一个周期之前设置它：

1. 创建具有 xUnit v3 和所需包的测试项目
2. 使用 Testcontainers 配置 `WebApplicationFactory` 以使用真实数据库
3. 添加共享固定件以避免每个测试类启动容器
4. 使用简单的健康检查测试验证基础设施

## 示例

```
用户：/tdd 让我们 TDD 一个产品搜索端点

Claude：我将为产品搜索规划 TDD 周期：

周期 1：使用匹配项搜索返回匹配产品
周期 2：使用无匹配项搜索返回空列表
周期 3：使用分页搜索返回正确页面
周期 4：使用过滤器缩小结果

开始周期 1：红阶段
编写基本产品搜索的失败集成测试...

[writes test, runs it, confirms failure]

周期 1：绿阶段
实现使搜索测试通过的最小代码...

[implements, runs test, confirms pass]

周期 1：重构阶段
实现工作正常，但查询可以使用投影而不是加载完整实体。重构...

[refactors, runs full suite, all green]

周期 1 完成。移动到周期 2...
```

## 相关

- `/verify` -- 完成所有 TDD 周期后运行完整验证
- `/scaffold` -- 生成由测试驱动的初始功能结构
