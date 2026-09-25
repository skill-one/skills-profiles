# Spring Boot 测试

这项技能提供了使用现代模式和最佳实践测试 Spring Boot 4 应用的专家指南。

## 核心原则

1. **测试金字塔**: 单元测试（快速）> 剖分测试（专注）> 集成测试（完整）
2. **正确工具**: 使用能让你建立信心的最窄切片
3. **AssertJ 风格**: 流畅、可读的断言优于冗长的匹配器
4. **现代 API**: 优先使用 MockMvcTester 和 RestTestClient 而非过时的替代方案

## 选择哪种测试切片？

| 场景 | 注解 | 参考 |
|------|------|------|
| 控制器 + HTTP 语义 | `@WebMvcTest` | [references/webmvctest.md](references/webmvctest.md) |
| 仓库 + JPA 查询 | `@DataJpaTest` | [references/datajpatest.md](references/datajpatest.md) |
| REST 客户端 + 外部 API | `@RestClientTest` | [references/restclienttest.md](references/restclienttest.md) |
| JSON (反)序列化 | `@JsonTest` | [references/test-slices-overview.md](references/test-slices-overview.md) |
| 完整应用 | `@SpringBootTest` | [references/test-slices-overview.md](references/test-slices-overview.md) |

## 测试切片参考

- [references/test-slices-overview.md](references/test-slices-overview.md) - 决策矩阵和比较
- [references/webmvctest.md](references/webmvctest.md) - 使用 MockMvc 的 Web 层
- [references/datajpatest.md](references/datajpatest.md) - 使用 Testcontainers 的数据层
- [references/restclienttest.md](references/restclienttest.md) - REST 客户端测试

## 测试工具参考

- [references/mockmvc-tester.md](references/mockmvc-tester.md) - AssertJ 风格的 MockMvc (3.2+)
- [references/mockmvc-classic.md](references/mockmvc-classic.md) - 传统 MockMvc (3.2 之前)
- [references/resttestclient.md](references/resttestclient.md) - Spring Boot 4+ REST 客户端
- [references/mockitobean.md](references/mockitobean.md) - 模拟依赖项

## 断言库

- [references/assertj-basics.md](references/assertj-basics.md) - 标量、字符串、布尔值、日期
- [references/assertj-collections.md](references/assertj-collections.md) - 列表、集合、映射、数组

## Testcontainers

- [references/testcontainers-jdbc.md](references/testcontainers-jdbc.md) - PostgreSQL、MySQL 等

## 测试数据生成

- [references/instancio.md](references/instancio.md) - 生成具有 3+ 属性的复杂测试对象

## 性能与迁移

- [references/context-caching.md](references/context-caching.md) - 加速测试套件
- [references/sb4-migration.md](references/sb4-migration.md) - Spring Boot 4.0 变更

## 快速决策树

```
测试控制器端点？
  是 → 使用 @WebMvcTest 和 MockMvcTester

测试仓库查询？
  是 → 使用 @DataJpaTest 和 Testcontainers (真实数据库)

测试服务中的业务逻辑？
  是 → 使用纯 JUnit + Mockito (无 Spring 上下文)

测试外部 API 客户端？
  是 → 使用 @RestClientTest 和 MockRestServiceServer

测试 JSON 映射？
  是 → 使用 @JsonTest

需要完整集成测试？
  是 → 使用 @SpringBootTest 和最小化上下文配置
```

## Spring Boot 4 突出特性

- **RestTestClient**: TestRestTemplate 的现代替代方案
- **@MockitoBean**: 替代 @MockBean (已弃用)
- **MockMvcTester**: 用于 Web 测试的 AssertJ 风格断言
- **模块化启动器**: 技术特定的测试启动器
- **上下文暂停**: 自动暂停缓存的上下文 (Spring Framework 7)

## 测试最佳实践

### 代码复杂度评估

当方法或类过于复杂而无法有效测试时：

1. **分析复杂度** - 如果你需要 5-7 个以上的测试用例来覆盖单个方法，它可能过于复杂
2. **建议重构** - 建议将代码拆分为更小、更专注的函数
3. **用户决策** - 如果用户同意重构，帮助识别提取点
4. **按需继续** - 如果用户决定继续使用复杂代码，尽管困难也要实现测试

**重构建议示例：**
```java
// 之前：难以测试的复杂方法
public Order processOrder(OrderRequest request) {
  // 验证、折扣计算、支付、库存、通知...
  // 50+ 行混合关注点
}

// 之后：重构为可测试单元
public Order processOrder(OrderRequest request) {
  validateOrder(request);
  var order = createOrder(request);
  applyDiscount(order);
  processPayment(order);
  updateInventory(order);
  sendNotification(order);
  return order;
}
```

### 避免代码冗余

为常用对象和模拟设置创建辅助方法，以提高可读性和可维护性。

### 使用 @DisplayName 组织测试

使用描述性显示名称来澄清测试意图：

```java
@Test
@DisplayName("应为 VIP 客户计算折扣")
void shouldCalculateDiscountForVip() { }

@Test
@DisplayName("当客户信用不足时应拒绝订单")
void shouldRejectOrderForInsufficientCredit() { }
```

### 测试覆盖顺序

始终按此顺序组织测试：

1. **主要场景** - 快乐路径，最常见的用例
2. **其他路径** - 其他有效场景，边缘情况
3. **异常/错误** - 无效输入，错误条件，失败模式

### 测试生产场景

考虑真实生产场景编写测试。这使得测试更具相关性，并有助于理解代码在实际生产中的行为。

### 测试覆盖率目标

以 80% 的代码覆盖率为实际平衡质量与努力的目标。更高的覆盖率是有益的，但不是唯一目标。

使用 Jacoco Maven 插件进行覆盖率报告和跟踪。

**覆盖率规则：**
- 80%+ 最小覆盖率
- 专注于有意义的断言，而不仅仅是执行

**优先考虑：**
1. 业务关键路径 (支付处理、订单验证)
2. 复杂算法 (定价、折扣计算)
3. 错误处理 (异常、边缘情况)
4. 集成点 (外部 API、数据库)

## 依赖项 (Spring Boot 4)

```xml
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-test</artifactId>
  <scope>test</scope>
</dependency>

<!-- 用于 WebMvc 测试 -->
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-webmvc-test</artifactId>
  <scope>test</scope>
</dependency>

<!-- 用于 Testcontainers -->
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-testcontainers</artifactId>
  <scope>test</scope>
</dependency>
```
