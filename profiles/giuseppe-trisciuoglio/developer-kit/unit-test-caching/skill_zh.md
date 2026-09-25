# 单元测试 Spring 缓存

## 概述

本技能提供了在无完整 Spring 上下文的情况下，对 Spring 缓存注解（`@Cacheable`、`@CacheEvict`、`@CachePut`）进行单元测试的模式。它涵盖了缓存命中/未命中、失效、键生成和条件缓存，使用内存中的 `ConcurrentMapCacheManager`。

## 使用场景

- 编写 `@Cacheable` 方法的单元测试
- 验证 `@CacheEvict` 缓存失效是否正常工作
- 测试 `@CachePut` 缓存更新
- 验证 SpEL 表达式生成的缓存键
- 测试使用 `unless`/`condition` 参数的条件缓存
- 在无需 Redis 的情况下快速单元测试中模拟缓存管理器

## 指令

1. **配置内存 CacheManager**：使用 `ConcurrentMapCacheManager` 进行测试
2. **设置测试固定装置**：在 `@BeforeEach` 中模拟仓库并创建服务实例
3. **验证仓库调用次数**：使用 `times(n)` 断言确认缓存行为
4. **测试缓存命中**：调用方法两次，验证仓库调用一次
5. **测试缓存未命中**：验证每次调用都会调用仓库
6. **测试失效**：在 `@CacheEvict` 后，验证下次读取时仓库再次被调用
7. **测试键生成**：验证来自 SpEL 表达式的复合键
8. **验证条件缓存**：测试 `unless`（空结果）和 `condition`（基于参数）

**验证检查点：**
- 运行测试 → 如果缓存未工作：验证测试配置中存在 `@EnableCaching` 注解
- 如果代理问题：确保方法调用通过 Spring 代理（不要直接 `this` 调用）
- 如果键不匹配：记录实际缓存键并与 `@Cacheable(key="...")` 表达式比较

## 示例

### Maven

```xml
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-cache</artifactId>
</dependency>
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-test</artifactId>
  <scope>test</scope>
</dependency>
```

### Gradle

```kotlin
dependencies {
  implementation("org.springframework.boot:spring-boot-starter-cache")
  testImplementation("org.springframework.boot:spring-boot-starter-test")
}
```

### 测试 `@Cacheable`（缓存命中/未命中）

```java
// Service
@Service
public class UserService {
  private final UserRepository userRepository;

  public UserService(UserRepository userRepository) {
    this.userRepository = userRepository;
  }

  @Cacheable("users")
  public User getUserById(Long id) {
    return userRepository.findById(id).orElse(null);
  }
}

// Test
class UserServiceCachingTest {

  private UserRepository userRepository;
  private UserService userService;

  @BeforeEach
  void setUp() {
    userRepository = mock(UserRepository.class);
    userService = new UserService(userRepository);
  }

  @Test
  void shouldCacheUserAfterFirstCall() {
    User user = new User(1L, "Alice");
    when(userRepository.findById(1L)).thenReturn(Optional.of(user));

    // 第一次调用 - 访问数据库
    User firstCall = userService.getUserById(1L);
    // 第二次调用 - 访问缓存
    User secondCall = userService.getUserById(1L);

    assertThat(firstCall).isEqualTo(secondCall);
    verify(userRepository, times(1)).findById(1L); // 由于缓存，仅调用一次
  }

  @Test
  void shouldInvokeRepositoryOnCacheMiss() {
    when(userRepository.findById(1L)).thenReturn(Optional.of(new User(1L, "Bob")));

    userService.getUserById(1L);
    userService.getUserById(1L);

    verify(userRepository, times(2)).findById(1L); // 未发生缓存
  }
}
```

### 测试 `@CacheEvict`

```java
// Service
@Service
public class ProductService {
  private final ProductRepository productRepository;

  public ProductService(ProductRepository productRepository) {
    this.productRepository = productRepository;
  }

  @Cacheable("products")
  public Product getProductById(Long id) {
    return productRepository.findById(id).orElse(null);
  }

  @CacheEvict("products")
  public void deleteProduct(Long id) {
    productRepository.deleteById(id);
  }
}

// Test
class ProductCacheEvictTest {

  private ProductRepository productRepository;
  private ProductService productService;

  @BeforeEach
  void setUp() {
    productRepository = mock(ProductRepository.class);
    productService = new ProductService(productRepository);
  }

  @Test
  void shouldEvictProductFromCacheWhenDeleted() {
    Product product = new Product(1L, "Laptop", 999.99);
    when(productRepository.findById(1L)).thenReturn(Optional.of(product));

    productService.getProductById(1L); // 缓存产品
    productService.deleteProduct(1L); // 从缓存中失效

    // 失效后仓库再次被调用
    productService.getProductById(1L);
    verify(productRepository, times(2)).findById(1L);
  }

  @Test
  void shouldClearAllEntriesWithAllEntriesTrue() {
    Product product1 = new Product(1L, "Laptop", 999.99);
    Product product2 = new Product(2L, "Mouse", 29.99);
    when(productRepository.findById(anyLong())).thenAnswer(i ->
      Optional.of(new Product(i.getArgument(0), "Product", 10.0)));

    productService.getProductById(1L);
    productService.getProductById(2L);

    // 使用反射或 `ConcurrentMapCache` 的 `clear()` 方法
    productService.clearAllProducts();

    productService.getProductById(1L);
    productService.getProductById(2L);

    verify(productRepository, times(4)).findById(anyLong());
  }
}
```

### 测试 `@CachePut`

```java
@Service
public class OrderService {
  private final OrderRepository orderRepository;

  public OrderService(OrderRepository orderRepository) {
    this.orderRepository = orderRepository;
  }

  @Cacheable("orders")
  public Order getOrder(Long id) {
    return orderRepository.findById(id).orElse(null);
  }

  @CachePut(value = "orders", key = "#order.id")
  public Order updateOrder(Order order) {
    return orderRepository.save(order);
  }
}

class OrderCachePutTest {

  private OrderRepository orderRepository;
  private OrderService orderService;

  @BeforeEach
  void setUp() {
    orderRepository = mock(OrderRepository.class);
    orderService = new OrderService(orderRepository);
  }

  @Test
  void shouldUpdateCacheWhenOrderIsUpdated() {
    Order original = new Order(1L, "Pending", 100.0);
    Order updated = new Order(1L, "Shipped", 100.0);

    when(orderRepository.findById(1L)).thenReturn(Optional.of(original));
    when(orderRepository.save(updated)).thenReturn(updated);

    orderService.getOrder(1L);
    orderService.updateOrder(updated);

    // 下次调用从缓存返回更新后的版本
    Order cachedOrder = orderService.getOrder(1L);
    assertThat(cachedOrder.getStatus()).isEqualTo("Shipped");
  }
}
```

### 测试条件缓存

```java
@Service
public class DataService {
  private final DataRepository dataRepository;

  public DataService(DataRepository dataRepository) {
    this.dataRepository = dataRepository;
  }

  // 不缓存空结果
  @Cacheable(value = "data", unless = "#result == null")
  public Data getData(Long id) {
    return dataRepository.findById(id).orElse(null);
  }

  // 仅当 id > 0 时缓存
  @Cacheable(value = "users", condition = "#id > 0")
  public User getUser(Long id) {
    return dataRepository.findById(id).map(u -> new User(u.getId(), u.getName())).orElse(null);
  }
}

class ConditionalCachingTest {

  @Test
  void shouldNotCacheNullResults() {
    DataRepository dataRepository = mock(DataRepository.class);
    when(dataRepository.findById(999L)).thenReturn(Optional.empty());
    DataService service = new DataService(dataRepository);

    service.getData(999L);
    service.getData(999L);

    verify(dataRepository, times(2)).findById(999L); // 调用两次 - 未缓存
  }

  @Test
  void shouldNotCacheWhenConditionIsFalse() {
    DataRepository dataRepository = mock(DataRepository.class);
    when(dataRepository.findById(-1L)).thenReturn(Optional.of(new Data(-1L, "Test")));

    DataService service = new DataService(dataRepository);

    service.getUser(-1L);
    service.getUser(-1L);

    verify(dataRepository, times(2)).findById(-1L); // 条件 "#id > 0" = false
  }
}
```

### 使用 SpEL 测试缓存键

```java
@Service
public class InventoryService {
  private final InventoryRepository inventoryRepository;

  public InventoryService(InventoryRepository inventoryRepository) {
    this.inventoryRepository = inventoryRepository;
  }

  // 复合键：productId-warehouseId
  @Cacheable(value = "inventory", key = "#productId + '-' + #warehouseId")
  public InventoryItem getInventory(Long productId, Long warehouseId) {
    return inventoryRepository.findByProductAndWarehouse(productId, warehouseId);
  }
}

class CacheKeyTest {

  @Test
  void shouldUseCorrectCacheKeyForDifferentCombinations() {
    InventoryRepository repository = mock(InventoryRepository.class);
    InventoryItem item = new InventoryItem(1L, 1L, 100);
    when(repository.findByProductAndWarehouse(1L, 1L)).thenReturn(item);

    InventoryService service = new InventoryService(repository);

    // 相同键："1-1" - 应缓存
    service.getInventory(1L, 1L);
    service.getInventory(1L, 1L); // 缓存命中
    verify(repository, times(1)).findByProductAndWarehouse(1L, 1L);

    // 不同键："2-1" - 缓存未命中
    service.getInventory(2L, 1L); // 缓存未命中
    verify(repository, times(2)).findByProductAndWarehouse(any(), any());
  }
}
```

## 最佳实践

- **模拟仓库调用**：使用 `verify(mock, times(n))` 断言缓存行为
- **测试命中和未命中场景**：不要只测试快乐路径
- **清除缓存状态**：在测试之间重置以避免结果不稳定
- **使用 `ConcurrentMapCacheManager`**：快速，无外部依赖
- **验证失效**：始终测试 `@CacheEvict` 是否真正使缓存数据失效

## 限制和警告

- **`@Cacheable` 需要代理**：直接方法调用（`this.method()`）绕过缓存 - 使用依赖注入
- **缓存键冲突**：来自 SpEL 的复合键必须对每个数据集唯一
- **空缓存**：默认情况下缓存空结果 - 使用 `unless = "#result == null"` 排除
- **`@CachePut` 总是执行**：与 `@Cacheable` 不同，它始终运行方法
- **内存使用**：内存缓存无限制增长 - 对于长时间运行的测试考虑 TTL
- **线程安全**：`ConcurrentMapCacheManager` 是线程安全的；分布式缓存可能需要额外配置

## 故障排除

| 问题 | 解决方案 |
|-------|----------|
| 缓存未工作 | 验证测试配置中存在 `@EnableCaching` 注解 |
| 代理绕过 | 使用自动注入/构造函数注入，不要直接 `this` 调用 |
| 键不匹配 | 使用 `cache.getNativeKey()` 记录缓存键以调试 SpEL |
| 不稳定的测试 | 在每个测试前 `@BeforeEach` 清除缓存 |

## 参考

- [Spring 缓存文档](https://docs.spring.io/spring-framework/docs/current/reference/html/integration.html#cache)
- [Cacheable 注解](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/cache/annotation/Cacheable.html)
- [SpEL 表达式](https://docs.spring.io/spring-framework/docs/current/reference/html/core.html#expressions)
