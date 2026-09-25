# 单元测试配置属性和配置文件

## 概述

本技能提供了用于单元测试 `@ConfigurationProperties` 绑定、特定环境的配置以及使用 JUnit 5 进行属性验证的模式。涵盖测试属性名称映射、类型转换、验证约束、嵌套结构以及无需完整启动 Spring 上下文的特定配置文件配置。

**关键验证检查点：**
- `@ConfigurationProperties` 和测试属性之间的属性前缀匹配
- 在具有无效值的 `@Validated` 类上触发验证
- Duration、DataSize、集合和映射的类型转换是否正常工作

## 使用场景

- 测试 `@ConfigurationProperties` 属性绑定
- 测试属性名称映射和类型转换
- 使用 `@NotBlank`、`@Min`、`@Max`、`@Email` 约束验证配置
- 测试特定环境的配置（开发、生产）
- 测试嵌套属性结构和集合
- 验证未指定属性时的默认值
- 无需启动 Spring 上下文进行快速配置测试

## 使用说明

1. **设置测试依赖项**：添加 `spring-boot-starter-test` 和 AssertJ 依赖项
2. **使用 ApplicationContextRunner**：无需启动完整 Spring 上下文即可测试属性绑定
3. **定义属性前缀**：确保 `@ConfigurationProperties(prefix = "...")` 与测试属性路径匹配
4. **测试所有属性路径**：验证每个属性，包括嵌套结构和集合
5. **测试验证约束**：使用 `context.hasFailed()` 验证 `@Validated` 属性是否拒绝无效值
6. **测试类型转换**：验证 Duration (`30s`)、DataSize (`50MB`)、集合和映射是否正确转换
7. **测试默认值**：验证当未在测试属性中指定时属性是否具有正确的默认值
8. **测试特定配置文件配置**：使用 `@Profile` 与 `ApplicationContextRunner` 进行特定环境的配置测试
9. **测试边界情况**：包括空字符串、null 值和类型不匹配

**故障排除流程：**
- 如果属性未绑定 → 检查前缀是否匹配（kebab-case 到 camelCase 转换）
- 如果验证未触发 → 验证是否存在 `@Validated` 注解
- 如果上下文启动失败 → 检查依赖项和 `@ConfigurationProperties` 类结构

## 示例

### 设置：测试依赖项

```xml
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-configuration-processor</artifactId>
  <scope>provided</scope>
</dependency>
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-test</artifactId>
  <scope>test</scope>
</dependency>
<dependency>
  <groupId>org.assertj</groupId>
  <artifactId>assertj-core</artifactId>
  <scope>test</scope>
</dependency>
```

### 基本模式：属性绑定

```java
@ConfigurationProperties(prefix = "app.security")
@Data
public class SecurityProperties {
  private String jwtSecret;
  private long jwtExpirationMs;
  private int maxLoginAttempts;
  private boolean enableTwoFactor;
}

class SecurityPropertiesTest {

  @Test
  void shouldBindPropertiesFromEnvironment() {
    new ApplicationContextRunner()
      .withPropertyValues(
        "app.security.jwtSecret=my-secret-key",
        "app.security.jwtExpirationMs=3600000",
        "app.security.maxLoginAttempts=5",
        "app.security.enableTwoFactor=true"
      )
      .withBean(SecurityProperties.class)
      .run(context -> {
        SecurityProperties props = context.getBean(SecurityProperties.class);
        assertThat(props.getJwtSecret()).isEqualTo("my-secret-key");
        assertThat(props.getJwtExpirationMs()).isEqualTo(3600000L);
        assertThat(props.getMaxLoginAttempts()).isEqualTo(5);
        assertThat(props.isEnableTwoFactor()).isTrue();
      });
  }

  @Test
  void shouldUseDefaultValuesWhenPropertiesNotProvided() {
    new ApplicationContextRunner()
      .withPropertyValues("app.security.jwtSecret=key")
      .withBean(SecurityProperties.class)
      .run(context -> {
        SecurityProperties props = context.getBean(SecurityProperties.class);
        assertThat(props.getJwtSecret()).isEqualTo("key");
        assertThat(props.getMaxLoginAttempts()).isZero();
      });
  }
}
```

### 验证测试

```java
@ConfigurationProperties(prefix = "app.server")
@Data
@Validated
public class ServerProperties {
  @NotBlank
  private String host;

  @Min(1)
  @Max(65535)
  private int port = 8080;

  @Positive
  private int threadPoolSize;
}

class ConfigurationValidationTest {

  @Test
  void shouldFailValidationWhenHostIsBlank() {
    new ApplicationContextRunner()
      .withPropertyValues(
        "app.server.host=",
        "app.server.port=8080",
        "app.server.threadPoolSize=10"
      )
      .withBean(ServerProperties.class)
      .run(context -> {
        assertThat(context).hasFailed()
          .getFailure()
          .hasMessageContaining("host");
      });
  }

  @Test
  void shouldPassValidationWithValidConfiguration() {
    new ApplicationContextRunner()
      .withPropertyValues(
        "app.server.host=localhost",
        "app.server.port=8080",
        "app.server.threadPoolSize=10"
      )
      .withBean(ServerProperties.class)
      .run(context -> {
        assertThat(context).hasNotFailed();
        assertThat(context.getBean(ServerProperties.class).getHost()).isEqualTo("localhost");
      });
  }
}
```

### 类型转换测试

```java
@ConfigurationProperties(prefix = "app.features")
@Data
public class FeatureProperties {
  private Duration cacheExpiry = Duration.ofMinutes(10);
  private DataSize maxUploadSize = DataSize.ofMegabytes(100);
  private List<String> enabledFeatures;
  private Map<String, String> featureFlags;
}

class TypeConversionTest {

  @Test
  void shouldConvertDurationFromString() {
    new ApplicationContextRunner()
      .withPropertyValues("app.features.cacheExpiry=30s")
      .withBean(FeatureProperties.class)
      .run(context -> {
        assertThat(context.getBean(FeatureProperties.class).getCacheExpiry())
          .isEqualTo(Duration.ofSeconds(30));
      });
  }

  @Test
  void shouldConvertCommaDelimitedList() {
    new ApplicationContextRunner()
      .withPropertyValues("app.features.enabledFeatures=feature1,feature2")
      .withBean(FeatureProperties.class)
      .run(context -> {
        assertThat(context.getBean(FeatureProperties.class).getEnabledFeatures())
          .containsExactly("feature1", "feature2");
      });
  }
}
```

对于**嵌套属性**、**特定配置文件配置**、**集合绑定**和**高级验证模式**，请参阅 `references/advanced-examples.md`。

## 最佳实践

- **测试所有属性绑定**，包括嵌套结构和集合
- **测试验证约束**，针对所有 `@NotBlank`、`@Min`、`@Max`、`@Email`、`@Positive` 注解
- **测试默认值和自定义值**，以验证回退行为
- **使用 ApplicationContextRunner** 进行快速无上下文测试
- **使用 `@Profile` 分别测试特定配置文件配置**
- **验证 Duration、DataSize、集合和映射的类型转换**
- **测试边界情况**：空字符串、null 值、类型不匹配、超出范围的值

## 约束和警告

- **kebab-case 到 camelCase**：属性 `app.my-property` 映射到 Java 中的 `myProperty`
- **松散绑定**：Spring Boot 默认使用松散绑定；如有需要，可使用严格绑定
- **`@Validated` 必须存在**：向配置类添加 `@Validated` 注解以启用约束验证
- **`@ConstructorBinding`**：使用构造函数绑定时，所有参数必须可绑定
- **列表索引**：使用 `[0]`、`[1]` 语法；确保列表的顺序索引
- **Duration 格式**：接受 ISO-8601 (`PT30S`) 或简单语法 (`30s`、`1m`、`2h`)
- **上下文隔离**：每个 `ApplicationContextRunner` 创建一个无共享状态的新上下文
- **配置文件激活**：在 `withPropertyValues()` 中使用 `spring.profiles.active=profileName` 进行配置文件测试

## 故障排除

| 问题 | 原因 | 解决方案 |
|-------|-------|----------|
| 属性未绑定 | 前缀不匹配 | 验证 `@ConfigurationProperties(prefix="...")` 是否与属性路径匹配 |
| 验证未触发 | 缺少 `@Validated` | 向配置类添加 `@Validated` 注解 |
| 上下文启动失败 | 缺少依赖项 | 确保 `spring-boot-starter-test` 在测试范围内 |
| 嵌套属性为 null | 内部类缺失 | 在嵌套类上使用 `@Data` 或提供获取器/设置器 |
| 集合绑定失败 | 索引错误 | 使用 `[0]`、`[1]` 语法，而不是 `(0)`、`(1)` |
