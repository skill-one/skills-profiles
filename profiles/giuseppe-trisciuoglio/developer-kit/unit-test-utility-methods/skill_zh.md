# 单元测试工具类和静态方法

## 概述

此技能为具有静态辅助方法的工具类和纯函数生成测试。它提供了测试空值处理、边界情况、边界条件以及字符串操作、计算、数据验证和集合等常见工具的模板。纯函数无需模拟。

## 使用场景

在以下情况下使用此技能：
- 编写具有静态方法的工具/辅助类的测试
- 测试无状态或无副作用的纯函数
- 测试字符串操作、格式化或转换工具
- 测试计算、转换或数学辅助函数
- 测试数据验证和格式化工具
- 验证工具代码中的空/空输入处理
- 测试集合或数组辅助方法

## 使用说明

1. **创建测试类**：以工具类命名（例如，`StringUtilsTest`）
2. **测试常规路径**：有效输入和预期输出
3. **测试边界情况**：空值、空字符串、空白、单个元素
4. **测试边界条件**：最大/最小值、大数字、精度
5. **使用描述性名称**：`shouldCapitalizeFirstLetter` 而不是 `test1`
6. **使用 AssertJ**：用于可读的链式断言
7. **使用 `@ParameterizedTest`**：用于多个相似输入（参考 `references/parameterized-tests.md`）
8. **避免模拟**：纯工具无需模拟

## 示例

### 基本静态工具类测试

```java
import org.junit.jupiter.api.Test;
import static org.assertj.core.api.Assertions.*;

class StringUtilsTest {

    @Test
    void shouldCapitalizeFirstLetter() {
        assertThat(StringUtils.capitalize("hello")).isEqualTo("Hello");
    }

    @Test
    void shouldReturnNullForNullInput() {
        assertThat(StringUtils.capitalize(null)).isNull();
    }

    @Test
    void shouldHandleEmptyString() {
        assertThat(StringUtils.capitalize("")).isEmpty();
    }

    @Test
    void shouldHandleSingleCharacter() {
        assertThat(StringUtils.capitalize("a")).isEqualTo("A");
    }
}
```

### 全面示例：isEmpty 实现

```java
// 输入：public static boolean isEmpty(String str)
//   { return str == null || str.trim().isEmpty(); }

class StringUtilsTest {

    @Test
    void shouldReturnTrueForNullString() {
        assertThat(StringUtils.isEmpty(null)).isTrue();
    }

    @Test
    void shouldReturnTrueForEmptyString() {
        assertThat(StringUtils.isEmpty("")).isTrue();
    }

    @Test
    void shouldReturnTrueForWhitespaceOnly() {
        assertThat(StringUtils.isEmpty("   ")).isTrue();
    }

    @Test
    void shouldReturnFalseForNonEmptyString() {
        assertThat(StringUtils.isEmpty("hello")).isFalse();
    }
}
```

### 空值安全工具

```java
class NullSafeUtilsTest {

    @Test
    void shouldReturnDefaultWhenNull() {
        assertThat(NullSafeUtils.getOrDefault(null, "default")).isEqualTo("default");
    }

    @Test
    void shouldReturnValueWhenNotNull() {
        assertThat(NullSafeUtils.getOrDefault("value", "default")).isEqualTo("value");
    }

    @Test
    void shouldReturnFalseWhenBlank() {
        assertThat(NullSafeUtils.isNotBlank(null)).isFalse();
        assertThat(NullSafeUtils.isNotBlank("   ")).isFalse();
    }
}
```

### 数学/计算工具

```java
class MathUtilsTest {

    @Test
    void shouldCalculatePercentage() {
        assertThat(MathUtils.percentage(25, 100)).isEqualTo(25.0);
    }

    @Test
    void shouldHandleZeroDivisor() {
        assertThat(MathUtils.percentage(50, 0)).isZero();
    }

    @Test
    void shouldRoundToDecimalPlaces() {
        assertThat(MathUtils.round(3.14159, 2)).isEqualTo(3.14);
    }

    @Test
    void shouldHandleFloatingPointWithTolerance() {
        assertThat(MathUtils.multiply(0.1, 0.2))
            .isCloseTo(0.02, within(0.0001));
    }
}
```

### 集合工具

```java
class CollectionUtilsTest {

    @Test
    void shouldFilterList() {
        List<Integer> result = CollectionUtils.filter(List.of(1, 2, 3, 4), n -> n % 2 == 0);
        assertThat(result).containsExactly(2, 4);
    }

    @Test
    void shouldHandleNullList() {
        assertThat(CollectionUtils.filter(null, n -> true)).isEmpty();
    }

    @Test
    void shouldJoinWithSeparator() {
        assertThat(CollectionUtils.join(List.of("a", "b", "c"), "-")).isEqualTo("a-b-c");
    }

    @Test
    void shouldDeduplicateList() {
        assertThat(CollectionUtils.deduplicate(List.of("a", "b", "a")))
            .containsExactlyInAnyOrder("a", "b");
    }
}
```

### 数据验证工具

```java
class ValidatorUtilsTest {

    @Test
    void shouldValidateEmailFormat() {
        assertThat(ValidatorUtils.isValidEmail("user@example.com")).isTrue();
        assertThat(ValidatorUtils.isValidEmail("invalid")).isFalse();
    }

    @Test
    void shouldValidateUrlFormat() {
        assertThat(ValidatorUtils.isValidUrl("https://example.com")).isTrue();
        assertThat(ValidatorUtils.isValidUrl("not a url")).isFalse();
    }

    @Test
    void shouldValidateCreditCard() {
        assertThat(ValidatorUtils.isValidCreditCard("4532015112830366")).isTrue();
        assertThat(ValidatorUtils.isValidCreditCard("1234567890123456")).isFalse();
    }
}
```

### 具有时钟依赖的工具（罕见）

```java
@ExtendWith(MockitoExtension.class)
class DateUtilsTest {

    @Mock
    private Clock clock;

    @Test
    void shouldGetDateFromClock() {
        when(clock.instant()).thenReturn(Instant.parse("2024-01-15T10:00:00Z"));
        assertThat(DateUtils.today(clock)).isEqualTo(LocalDate.of(2024, 1, 15));
    }
}
```

## 最佳实践

- **专测纯函数** - 无副作用或状态依赖
- **覆盖常规路径和边界情况** - 空值、空字符串、空白、极端值
- **使用描述性测试名称** - `shouldReturnNullWhenInputIsNull`
- **使用 `@ParameterizedTest`** 用于多个相似输入（参考 `references/parameterized-tests.md`）
- **测试边界条件** - 最小/最大值、溢出、精度
- **避免模拟纯函数** - 仅模拟外部依赖如 Clock
- **保持测试独立** - 测试间无顺序依赖

## 限制和警告

- **不模拟静态方法**：仅在绝对必要时使用反射工具
- **纯函数要求**：状态性工具较难测试；优先使用不可变对象
- **浮点精度**：永不使用精确等式；使用 `isCloseTo(delta)`
- **空值处理一致性**：确定工具返回空值还是抛出异常；相应测试
- **线程安全**：静态工具必须线程安全；单独验证并发行为
- **不可变输入**：记录工具是否修改输入参数
- **边界情况参考**：参考 `references/edge-cases.md` 获取边界测试模式
