# AWS SDK for Java 2.x - Amazon DynamoDB

## 概述

使用 AWS SDK for Java 2.x 提供的增强客户端，实现类型安全的 CRUD、查询、批量操作、事务以及 Spring Boot 集成，支持 DynamoDB 模式。

## 何时使用

- 对 DynamoDB 项目执行 CRUD 操作
- 使用排序键或 GSI 查询表
- 对多个项目执行批量操作
- 跨表执行原子事务
- 与 DynamoDB 集成 Spring Boot

## 说明

1. 将 AWS SDK DynamoDB 依赖项添加到 `pom.xml`
2. 配置客户端设置（低级或增强客户端）
3. 使用 `@DynamoDbBean` 注解定义实体类
4. 使用 `DynamoDbTable` 执行操作（CRUD、查询、扫描、批量、事务）
5. 使用重试逻辑和指数退避处理部分失败
6. 使用仓库模式进行 Spring Boot 集成

## 依赖项

添加到 `pom.xml`：
```xml
<!-- 低级 DynamoDB 客户端 -->
<dependency>
    <groupId>software.amazon.awssdk</groupId>
    <artifactId>dynamodb</artifactId>
</dependency>

<!-- 增强客户端（推荐） -->
<dependency>
    <groupId>software.amazon.awssdk</groupId>
    <artifactId>dynamodb-enhanced</artifactId>
</dependency>
```
## 客户端设置

### 低级客户端
```java
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;

DynamoDbClient dynamoDb = DynamoDbClient.builder()
    .region(Region.US_EAST_1)
    .build();
```

### 增强客户端（推荐）
```java
import software.amazon.awssdk.enhanced.dynamodb.DynamoDbEnhancedClient;

DynamoDbEnhancedClient enhancedClient = DynamoDbEnhancedClient.builder()
    .dynamoDbClient(dynamoDb)
    .build();
```

## 实体映射

```java
@DynamoDbBean
public class Customer {

    @DynamoDbPartitionKey
    private String customerId;

    @DynamoDbAttribute("customer_name")
    private String name;

    private String email;

    @DynamoDbSortKey
    private String orderId;

    // 获取器和设置器
}
```

对于使用 GSI 和自定义转换器的复杂实体映射，请参阅 [实体映射参考](references/entity-mapping.md)。

## CRUD 操作

### 基本操作
```java
// 创建或更新项目
DynamoDbTable<Customer> table = enhancedClient.table("Customers", TableSchema.fromBean(Customer.class));
table.putItem(customer);

// 获取项目
Customer result = table.getItem(Key.builder().partitionValue(customerId).build());

// 更新项目
return table.updateItem(customer);

// 删除项目
table.deleteItem(Key.builder().partitionValue(customerId).build());
```

### 复合键操作
```java
// 使用复合键获取项目
Order order = table.getItem(Key.builder()
    .partitionValue(customerId)
    .sortValue(orderId)
    .build());
```

## 查询操作

### 基本查询
```java
import software.amazon.awssdk.enhanced.dynamodb.model.QueryConditional;

QueryConditional queryConditional = QueryConditional
    .keyEqualTo(Key.builder()
        .partitionValue(customerId)
        .build());

List<Order> orders = table.query(queryConditional).items().stream()
    .collect(Collectors.toList());
```

### 带过滤器的高级查询
```java
import software.amazon.awssdk.enhanced.dynamodb.Expression;

Expression filter = Expression.builder()
    .expression("status = :pending")
    .putExpressionValue(":pending", AttributeValue.builder().s("PENDING").build())
    .build();

List<Order> pendingOrders = table.query(r -> r
    .queryConditional(queryConditional)
    .filterExpression(filter))
    .items().stream()
    .collect(Collectors.toList());
```

对于详细的查询模式，请参阅 [高级操作参考](references/advanced-operations.md)。

## 扫描操作

> **警告**：扫描会读取整个表并消耗所有项目的读取容量。尽可能使用带有分区键或 GSI 的查询操作。

**扫描前的验证**：
- 确认使用分区键的查询对您的访问模式不可行
- 验证表具有足够的预配读取容量或使用按需模式
- 考虑使用 `limit()` 进行分页以控制容量消耗

```java
// 扫描所有项目
List<Customer> allCustomers = table.scan().items().stream()
    .collect(Collectors.toList());

// 带过滤器的扫描
Expression filter = Expression.builder()
    .expression("points >= :minPoints")
    .putExpressionValue(":minPoints", AttributeValue.builder().n("1000").build())
    .build();

List<Customer> vipCustomers = table.scan(r -> r.filterExpression(filter))
    .items().stream()
    .collect(Collectors.toList());
```

## 批量操作

### 批量获取
```java
import software.amazon.awssdk.enhanced.dynamodb.model.*;

List<Key> keys = customerIds.stream()
    .map(id -> Key.builder().partitionValue(id).build())
    .collect(Collectors.toList());

ReadBatch.Builder<Customer> batchBuilder = ReadBatch.builder(Customer.class)
    .mappedTableResource(table);

keys.forEach(batchBuilder::addGetItem);

BatchGetResultPageIterable result = enhancedClient.batchGetItem(r ->
    r.addReadBatch(batchBuilder.build()));

List<Customer> customers = result.resultsForTable(table).stream()
    .collect(Collectors.toList());
```

### 带错误处理的批量写入
```java
WriteBatch.Builder<Customer> batchBuilder = WriteBatch.builder(Customer.class)
    .mappedTableResource(table);

customers.forEach(batchBuilder::addPutItem);

BatchWriteItemEnhancedRequest request = BatchWriteItemEnhancedRequest.builder()
    .addWriteBatch(batchBuilder.build())
    .build();

BatchWriteResult result = enhancedClient.batchWriteItem(request);

// 验证：检查未处理的项目
if (!result.writeResponsesForTable(table).isEmpty()) {
    // 使用指数退避重试未处理的项目
    Map<String, AttributeValue> unprocessed = result.writeResponsesForTable(table).get(0)
        .unprocessedAttributes();
    if (unprocessed != null && !unprocessed.isEmpty()) {
        enhancedClient.batchWriteItem(r -> r
            .addWriteBatch(WriteBatch.builder(Customer.class)
                .mappedTableResource(table)
                .addPutItemFromItem(unprocessed)
                .build()));
    }
}
```

## 事务

### 带重试的事务写入
```java
public void placeOrderWithRetry(Order order, Customer customer, int maxRetries) {
    int attempt = 0;
    while (attempt < maxRetries) {
        try {
            enhancedClient.transactWriteItems(r -> r
                .addPutItem(customerTable, customer)
                .addPutItem(orderTable, order));
            return;
        } catch (TransactionCanceledException e) {
            if (e.cancellationReasons().stream()
                .anyMatch(r -> r.code().equals("TransactionCanceledException")
                    && r.message().contains("throughput"))) {
                attempt++;
                if (attempt < maxRetries) {
                    try { Thread.sleep((long) Math.pow(2, attempt) * 100); }
                    catch (InterruptedException ie) { Thread.currentThread().interrupt(); }
                }
            } else {
                throw e; // 非重试错误
            }
        }
    }
}
```

### 事务读取
```java
TransactGetItemsEnhancedRequest request = TransactGetItemsEnhancedRequest.builder()
    .addGetItem(customerTable, customerKey)
    .addGetItem(orderTable, orderKey)
    .build();

List<Document> results = enhancedClient.transactGetItems(request);
```

## Spring Boot 集成

### 配置
```java
@Configuration
public class DynamoDbConfiguration {

    @Bean
    public DynamoDbClient dynamoDbClient() {
        return DynamoDbClient.builder()
            .region(Region.US_EAST_1)
            .build();
    }

    @Bean
    public DynamoDbEnhancedClient dynamoDbEnhancedClient(DynamoDbClient dynamoDbClient) {
        return DynamoDbEnhancedClient.builder()
            .dynamoDbClient(dynamoDbClient)
            .build();
    }
}
```

### 仓库模式
```java
@Repository
public class CustomerRepository {

    private final DynamoDbTable<Customer> customerTable;

    public CustomerRepository(DynamoDbEnhancedClient enhancedClient) {
        this.customerTable = enhancedClient.table("Customers", TableSchema.fromBean(Customer.class));
    }

    public void save(Customer customer) {
        customerTable.putItem(customer);
    }

    public Optional<Customer> findById(String customerId) {
        Key key = Key.builder().partitionValue(customerId).build();
        return Optional.ofNullable(customerTable.getItem(key));
    }
}
```

对于全面的 Spring Boot 集成模式，请参阅 [Spring Boot 集成参考](references/spring-boot-integration.md)。

## 测试

### 使用 Mock 进行单元测试
```java
@ExtendWith(MockitoExtension.class)
class CustomerServiceTest {

    @Mock
    private DynamoDbClient dynamoDbClient;

    @Mock
    private DynamoDbEnhancedClient enhancedClient;

    @Mock
    private DynamoDbTable<Customer> customerTable;

    @InjectMocks
    private CustomerService customerService;

    @Test
    void saveCustomer_ShouldReturnSavedCustomer() {
        // 安排
        when(enhancedClient.table(anyString(), any(TableSchema.class)))
            .thenReturn(customerTable);

        Customer customer = new Customer("123", "John Doe", "john@example.com");

        // 行动
        Customer result = customerService.saveCustomer(customer);

        // 验证
        assertNotNull(result);
        verify(customerTable).putItem(customer);
    }
}
```

### 使用 LocalStack 进行集成测试
```java
@Testcontainers
@SpringBootTest
class DynamoDbIntegrationTest {

    @Container
    static LocalStackContainer localstack = new LocalStackContainer(
        DockerImageName.parse("localstack/localstack:3.0"))
        .withServices(LocalStackContainer.Service.DYNAMODB);

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("aws.endpoint",
            () -> localstack.getEndpointOverride(LocalStackContainer.Service.DYNAMODB).toString());
    }

    @Autowired
    private DynamoDbEnhancedClient enhancedClient;

    @Test
    void testCustomerCRUDOperations() {
        // 测试实现
    }
}
```

对于详细的测试策略，请参阅 [测试策略](references/testing-strategies.md)。

## 最佳实践

- **使用增强客户端**：类型安全的操作，减少样板代码
- **设计分区键以实现均匀分布**：避免热点分区
- **优先使用查询而不是扫描**：使用 GSI 进行访问模式
- **批量操作以 25/100 为块**：BatchGetItem 限制为 100，BatchWriteItem 限制为每个表 25 个
- **处理部分失败**：为 `ProvisionedThroughputExceeded` 实现带指数退避的重试
- **使用条件写入**：使用 `attribute_not_exists(pk)` 防止竞争条件

## 示例

### 完整 CRUD 仓库
```java
@Repository
public class UserRepository {

    private final DynamoDbTable<User> userTable;

    public UserRepository(DynamoDbEnhancedClient enhancedClient) {
        this.userTable = enhancedClient.table("Users", TableSchema.fromBean(User.class));
    }

    public User save(User user) {
        userTable.putItem(user);
        return user;
    }

    public Optional<User> findById(String userId) {
        Key key = Key.builder().partitionValue(userId).build();
        return Optional.ofNullable(userTable.getItem(key));
    }

    public void deleteById(String userId) {
        userTable.deleteItem(Key.builder().partitionValue(userId).build());
    }
}
```

### 带重试的条件写入
```java
public boolean createIfNotExists(User user) {
    PutItemEnhancedRequest<User> request = PutItemEnhancedRequest.builder(User.class)
        .item(user)
        .conditionExpression("attribute_not_exists(userId)")
        .build();

    try {
        userTable.putItemWithRequest(request);
        return true;
    } catch (ConditionalCheckFailedException e) {
        return false; // 项目已存在
    }
}
```

## 限制和警告

- **项目大小限制**：DynamoDB 项目限制为 400KB
- **分区键设计**：设计不当会导致热点分区
- **批量限制**：BatchGetItem 最大 100，BatchWriteItem 每个表最大 25 个项目
- **事务成本**：事务成本为读取/写入容量单位的 2 倍
- **扫描操作**：扫描消耗大量读取容量；仅在必要时使用

## 参考

- [AWS DynamoDB 文档](https://docs.aws.amazon.com/dynamodb/)
- [AWS SDK for Java 文档](https://docs.aws.amazon.com/sdk-for-java/latest/developer-guide/)
- [DynamoDB 示例](https://github.com/awsdocs/aws-doc-sdk-examples/tree/main/javav2/example_code/dynamodb)
- [LocalStack 用于测试](https://docs.localstack.cloud/user-guide/aws/)

对于详细的实现，请参阅参考文件夹：
- [实体映射参考](references/entity-mapping.md)
- [高级操作参考](references/advanced-operations.md)
- [Spring Boot 集成参考](references/spring-boot-integration.md)
- [测试策略](references/testing-strategies.md)
