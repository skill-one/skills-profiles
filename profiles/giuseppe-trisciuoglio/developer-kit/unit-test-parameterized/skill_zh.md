# 使用JUnit 5进行参数化单元测试

## 概述

提供使用JUnit 5在Java中进行参数化单元测试的模式。涵盖`@ValueSource`、`@CsvSource`、`@MethodSource`、`@EnumSource`、`@ArgumentsSource`和自定义显示名称。通过使用多个输入值运行相同的测试逻辑来减少测试重复。

## 使用场景

- 编写具有多个输入组合的JUnit测试
- 在Java中实现数据驱动测试
- 使用不同值运行相同的测试（边界分析）
- 从单个测试方法测试多个场景

## 使用说明

1. **添加依赖项**：确保`junit-jupiter-params`在测试类路径上（包含在`junit-jupiter`中）
2. **选择数据源**：`@ValueSource`用于简单值，`@CsvSource`用于表格数据，`@MethodSource`用于复杂对象
3. **匹配参数**：测试方法参数必须与数据源类型匹配
4. **设置显示名称**：使用`name = "{0}..."`以获得可读的输出
5. **验证**：运行`./gradlew test --info`或`mvn test`并验证所有参数组合都执行

## 示例

### Maven / Gradle 依赖项

JUnit 5参数化测试需要`junit-jupiter`（包含参数功能）。添加`assertj-core`用于断言：

```xml
<!-- Maven -->
<dependency>
  <groupId>org.junit.jupiter</groupId>
  <artifactId>junit-jupiter</artifactId>
  <scope>test</scope>
</dependency>
```

```kotlin
// Gradle
testImplementation("org.junit.jupiter:junit-jupiter")
```

### `@ValueSource` — 简单值

```java
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import static org.assertj.core.api.Assertions.assertThat;

@ParameterizedTest
@ValueSource(strings = {"hello", "world", "test"})
void shouldCapitalizeAllStrings(String input) {
  assertThat(StringUtils.capitalize(input)).isNotEmpty();
}

@ParameterizedTest
@ValueSource(ints = {1, 2, 3, 4, 5})
void shouldBePositive(int number) {
  assertThat(number).isPositive();
}

@ParameterizedTest
@ValueSource(ints = {Integer.MIN_VALUE, -1, 0, 1, Integer.MAX_VALUE})
void shouldHandleBoundaryValues(int value) {
  assertThat(Math.incrementExact(value)).isGreaterThan(value);
}
```

### `@CsvSource` — 表格数据

```java
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;

@ParameterizedTest
@CsvSource({
  "alice@example.com, true",
  "bob@gmail.com,     true",
  "invalid-email,     false",
  "user@,             false",
  "@example.com,       false"
})
void shouldValidateEmailAddresses(String email, boolean expected) {
  assertThat(UserValidator.isValidEmail(email)).isEqualTo(expected);
}
```

### `@MethodSource` — 复杂数据

```java
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.MethodSource;
import java.util.stream.Stream;

@ParameterizedTest
@MethodSource("additionTestCases")
void shouldAddNumbersCorrectly(int a, int b, int expected) {
  assertThat(Calculator.add(a, b)).isEqualTo(expected);
}

static Stream<Arguments> additionTestCases() {
  return Stream.of(
    Arguments.of(1, 2, 3),
    Arguments.of(0, 0, 0),
    Arguments.of(-1, 1, 0),
    Arguments.of(100, 200, 300)
  );
}
```

### `@EnumSource` — 枚举值

```java
@ParameterizedTest
@EnumSource(Status.class)
void shouldHandleAllStatuses(Status status) {
  assertThat(status).isNotNull();
}

@ParameterizedTest
@EnumSource(value = Status.class, names = {"ACTIVE", "INACTIVE"})
void shouldHandleSpecificStatuses(Status status) {
  assertThat(status).isIn(Status.ACTIVE, Status.INACTIVE);
}
```

### 自定义显示名称

```java
@ParameterizedTest(name = "Discount of {0}% should be calculated correctly")
@ValueSource(ints = {5, 10, 15, 20})
void shouldApplyDiscount(int discountPercent) {
  double result = DiscountCalculator.apply(100.0, discountPercent);
  assertThat(result).isEqualTo(100.0 * (1 - discountPercent / 100.0));
}
```

### 自定义`ArgumentsProvider`

```java
class RangeValidatorProvider implements ArgumentsProvider {
  @Override
  public Stream<? extends Arguments> provideArguments(ExtensionContext context) {
    return Stream.of(
      Arguments.of(0, 0, 100, true),
      Arguments.of(50, 0, 100, true),
      Arguments.of(-1, 0, 100, false),
      Arguments.of(101, 0, 100, false)
    );
  }
}

@ParameterizedTest
@ArgumentsSource(RangeValidatorProvider.class)
void shouldValidateRange(int value, int min, int max, boolean expected) {
  assertThat(RangeValidator.isInRange(value, min, max)).isEqualTo(expected);
}
```

### 错误条件测试

```java
@ParameterizedTest
@ValueSource(strings = {"", " ", null})
void shouldThrowExceptionForInvalidInput(String input) {
  assertThatThrownBy(() -> Parser.parse(input))
    .isInstanceOf(IllegalArgumentException.class);
}
```

## 最佳实践

- 使用描述性显示名称：`name = "{0}..."`以获得可读的输出
- 测试边界值：包括最小值、最大值、零和边缘情况
- 保持测试逻辑集中：每个参数集一个断言
- 使用`@MethodSource`用于复杂对象，`@CsvSource`用于表格数据
- 逻辑组织测试数据——将相关场景分组

## 限制和警告

- **参数数量必须匹配**：源中的参数数量必须与测试方法签名匹配
- **`@ValueSource`限制**：仅支持原始类型、字符串和枚举——不能直接支持对象或null
- **CSV转义**：`@CsvSource`中逗号分隔的字符串必须使用单引号
- **`@MethodSource`可见性**：工厂方法必须在同一测试类中为静态
- **显示名称占位符**：使用`{0}`、`{1}`等来引用参数
- **执行次数**：每个参数集作为单独的测试调用执行

## 参考

- [JUnit 5参数化测试](https://junit.org/junit5/docs/current/user-guide/#writing-tests-parameterized-tests)
- [`@ParameterizedTest` API](https://junit.org/junit5/docs/current/api/org.junit.jupiter.params/org/junit/jupiter/params/ParameterizedTest.html)
