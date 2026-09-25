# 使用 `@JsonTest` 进行 JSON 序列化单元测试

## 概述

提供使用 Spring 的 `@JsonTest` 和 Jackson 进行 JSON 序列化和反序列化的单元测试模式。涵盖 POJO 映射、自定义序列化器、字段名映射、嵌套对象、日期/时间格式化和多态类型。

## 何时使用

- 测试 DTO 的 JSON 序列化/反序列化
- 验证自定义 Jackson 序列化器/反序列化器
- 验证 `@JsonProperty`、`@JsonIgnore` 和字段名映射
- 测试日期/时间格式处理（LocalDateTime、Date）
- 测试空值处理和缺失字段
- 测试多态类型反序列化

## 指南

1. **使用 `@JsonTest` 注解测试类** → 启用 JacksonTester 自动配置
2. **为目标类型自动装配 JacksonTester** → 提供类型安全的 JSON 断言
3. **测试序列化** → 调用 `json.write(object)` 并使用 `extractingJsonPath*` 断言 JSON 路径
4. **测试反序列化** → 调用 `json.parse(json)` 或 `json.parseObject(json)` 并断言对象状态
5. **验证往返一致性** → 序列化，然后反序列化，验证相同的数据（如果对象可以正确比较）
6. **测试边界情况** → 空值、缺失字段、空集合、无效 JSON
7. **添加验证检查点**：在每个断言之后，使用错误数据验证测试是否有意义地失败

## 示例

### Maven 设置
```xml
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-json</artifactId>
</dependency>
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-test</artifactId>
  <scope>test</scope>
</dependency>
```

### Gradle 设置
```kotlin
dependencies {
  implementation("org.springframework.boot:spring-boot-starter-json")
  testImplementation("org.springframework.boot:spring-boot-starter-test")
}
```

### 基本序列化和反序列化

```java
@JsonTest
class UserDtoJsonTest {

  @Autowired
  private JacksonTester<UserDto> json;

  @Test
  void shouldSerializeUserToJson() throws Exception {
    UserDto user = new UserDto(1L, "Alice", "alice@example.com", 25);
    JsonContent<UserDto> result = json.write(user);

    result
      .extractingJsonPathNumberValue("$.id").isEqualTo(1)
      .extractingJsonPathStringValue("$.name").isEqualTo("Alice")
      .extractingJsonPathStringValue("$.email").isEqualTo("alice@example.com")
      .extractingJsonPathNumberValue("$.age").isEqualTo(25);
  }

  @Test
  void shouldDeserializeJsonToUser() throws Exception {
    String json_content = "{\"id\":1,\"name\":\"Alice\",\"email\":\"alice@example.com\",\"age\":25}";
    UserDto user = json.parse(json_content).getObject();

    assertThat(user.getId()).isEqualTo(1L);
    assertThat(user.getName()).isEqualTo("Alice");
    assertThat(user.getEmail()).isEqualTo("alice@example.com");
    assertThat(user.getAge()).isEqualTo(25);
  }

  @Test
  void shouldHandleNullFields() throws Exception {
    String json_content = "{\"id\":1,\"name\":null,\"email\":\"alice@example.com\"}";
    UserDto user = json.parse(json_content).getObject();
    assertThat(user.getName()).isNull();
  }
}
```

### 自定义 JSON 属性

```java
public class Order {
  @JsonProperty("order_id")
  private Long id;

  @JsonProperty("total_amount")
  private BigDecimal amount;

  @JsonIgnore
  private String internalNote;
}

@JsonTest
class OrderJsonTest {

  @Autowired
  private JacksonTester<Order> json;

  @Test
  void shouldMapJsonPropertyNames() throws Exception {
    String json_content = "{\"order_id\":123,\"total_amount\":99.99}";
    Order order = json.parse(json_content).getObject();
    assertThat(order.getId()).isEqualTo(123L);
    assertThat(order.getAmount()).isEqualByComparingTo(new BigDecimal("99.99"));
  }

  @Test
  void shouldIgnoreJsonIgnoreFields() throws Exception {
    Order order = new Order(123L, new BigDecimal("99.99"));
    order.setInternalNote("Secret");
    assertThat(json.write(order).json).doesNotContain("internalNote");
  }
}
```

### 嵌套对象

```java
public class Product {
  private Long id;
  private String name;
  private Category category;
  private List<Review> reviews;
}

@JsonTest
class ProductJsonTest {

  @Autowired
  private JacksonTester<Product> json;

  @Test
  void shouldSerializeNestedObjects() throws Exception {
    Product product = new Product(1L, "Laptop", new Category(1L, "Electronics"));
    JsonContent<Product> result = json.write(product);

    result
      .extractingJsonPathNumberValue("$.category.id").isEqualTo(1)
      .extractingJsonPathStringValue("$.category.name").isEqualTo("Electronics");
  }

  @Test
  void shouldDeserializeNestedObjects() throws Exception {
    String json_content = "{\"id\":1,\"name\":\"Laptop\",\"category\":{\"id\":1,\"name\":\"Electronics\"}}";
    Product product = json.parse(json_content).getObject();
    assertThat(product.getCategory().getName()).isEqualTo("Electronics");
  }

  @Test
  void shouldHandleListOfNestedObjects() throws Exception {
    String json_content = "{\"id\":1,\"reviews\":[{\"rating\":5},{\"rating\":4}]}";
    Product product = json.parse(json_content).getObject();
    assertThat(product.getReviews()).hasSize(2);
  }
}
```

### 日期/时间格式化

```java
@JsonTest
class DateTimeJsonTest {

  @Autowired
  private JacksonTester<Event> json;

  @Test
  void shouldFormatDateTimeCorrectly() throws Exception {
    LocalDateTime dt = LocalDateTime.of(2024, 1, 15, 10, 30, 0);
    json.write(new Event("Conference", dt))
      .extractingJsonPathStringValue("$.scheduledAt").isEqualTo("2024-01-15T10:30:00");
  }
}
```

### 自定义序列化器

```java
public class CustomMoneySerializer extends JsonSerializer<BigDecimal> {
  @Override
  public void serialize(BigDecimal value, JsonGenerator gen, SerializerProvider serializers) throws IOException {
    gen.writeString(value == null ? null : String.format("$%.2f", value));
  }
}

@JsonTest
class CustomSerializerTest {

  @Autowired
  private JacksonTester<Price> json;

  @Test
  void shouldUseCustomSerializer() throws Exception {
    json.write(new Price(new BigDecimal("99.99")))
      .extractingJsonPathStringValue("$.amount").isEqualTo("$99.99");
  }
}
```

### 多态反序列化

```java
@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "type")
@JsonSubTypes({
  @JsonSubTypes.Type(value = CreditCard.class, name = "credit_card"),
  @JsonSubTypes.Type(value = PayPal.class, name = "paypal")
})
public abstract class PaymentMethod { }

@JsonTest
class PolymorphicJsonTest {

  @Autowired
  private JacksonTester<PaymentMethod> json;

  @Test
  void shouldDeserializeCreditCard() throws Exception {
    String json_content = "{\"type\":\"credit_card\",\"id\":\"card123\"}";
    assertThat(json.parse(json_content).getObject()).isInstanceOf(CreditCard.class);
  }

  @Test
  void shouldDeserializePayPal() throws Exception {
    String json_content = "{\"type\":\"paypal\",\"id\":\"pp123\"}";
    assertThat(json.parse(json_content).getObject()).isInstanceOf(PayPal.class);
  }
}
```

## 最佳实践

- 测试序列化和反序列化以实现完整覆盖
- 逐个验证 JSON 路径，而不是比较完整的 JSON 字符串
- 明确测试空值处理 — 根据 `@JsonInclude`，空字段可能被包含或排除
- 使用 `extractingJsonPath*` 方法进行精确的字段断言
- 测试往返一致性：序列化一个对象，反序列化 JSON，验证结果是否匹配
- 验证边界情况：空字符串、空集合、深层嵌套结构
- 将相关的断言分组在单个测试中以提高清晰度

## 限制和警告

- **`@JsonTest` 加载有限上下文**：仅加载 JSON 相关的 Bean；使用 `@SpringBootTest` 获取完整 Spring 上下文
- **Jackson 版本**：确保注解版本与使用的 Jackson 版本匹配
- **日期格式**：默认为 ISO-8601；使用 `@JsonFormat` 自定义模式
- **空值处理**：使用 `@JsonInclude(Include.NON_NULL)` 从序列化中排除空值
- **循环引用**：使用 `@JsonManagedReference`/`@JsonBackReference` 防止无限循环
- **不可变对象**：使用 `@JsonCreator` + `@JsonProperty` 进行基于构造函数的反序列化
- **多态类型**：`@JsonTypeInfo` 必须正确识别子类型，反序列化才能正常工作

## 调试工作流

当 JSON 测试失败时，请遵循以下工作流：

| 失败症状 | 常见原因 | 如何验证 |
|----------------|--------------|---------------|
| `JsonPath` 断言失败 | 字段名不匹配 | 检查 `@JsonProperty` 拼写是否与 JSON 键匹配 |
| 预期空值但获取了值 | `@JsonInclude(NON_NULL)` 配置 | 验证字段/类的注解 |
| 反序列化返回了错误类型 | 缺失 `@JsonTypeInfo` | 向 JSON 添加类型信息属性或配置子类型映射 |
| 日期格式不匹配 | 格式字符串错误 | 确认 `@JsonFormat(pattern=...)` 是否与预期字符串匹配 |
| 输出中缺失字段 | `@JsonIgnore` 或 transient 修饰符 | 检查字段是否有 `@JsonIgnore` 或 `transient` 关键字 |
| 嵌套对象为空 | 内部 JSON 缺失或格式错误 | 记录解析后的 JSON；验证内部结构是否与 POJO 匹配 |
| `JsonParseException` | 无效的 JSON 字符串 | 验证 JSON 语法；检查是否有未转义字符 |

**修复后的验证检查点**：重新运行测试 — 如果通过，编写一个互补的测试以防止回归（例如，如果修复了空值处理，添加一个测试以验证非空值）。
