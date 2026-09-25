# 单元测试边界条件和边缘情况

## 概述

使用 JUnit 5 在 Java 中测试边界条件、角落情况和极限值的系统化模式。涵盖数值边界、字符串边缘情况、集合状态、浮点精度、日期/时间限制和“差一”场景。

## 何时使用

- 数值的最小/最大限制、空/空/空白输入
- 溢出/下溢验证、集合边界
- “差一”错误、浮点精度

## 说明

1. **识别边界**：列出数值限制（MIN_VALUE、MAX_VALUE、零）、字符串状态（空、空、空白）、集合大小（0、1、多个）
2. **应用参数化测试**：使用 `@ParameterizedTest` 与 `@ValueSource` 或 `@CsvSource` 用于多个边界值
3. **测试边界两侧**：覆盖每个边界以下、在、以上的值
4. **添加每个边界类别后运行测试** 以尽早发现问题
5. **验证浮点精度**：使用 `isCloseTo(expected, within(tolerance))` 与 AssertJ
6. **测试集合状态**：明确测试空（0）、单（1）和多个（>1）元素场景
7. **处理溢出/下溢**：使用 `Math.addExact()` 和 `Math.subtractExact()` 检测算术溢出
8. **测试日期/时间边缘**：验证闰年、月份边界、时区转换
9. **根据失败进行迭代**：当边界测试失败时，分析错误以发现未测试的边界；为发现的边缘条件添加测试用例

## 示例

需要：`junit-jupiter`、`junit-jupiter-params`、`assertj-core`。

## 整数边界测试

```java
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;
import static org.assertj.core.api.Assertions.assertThat;

class IntegerBoundaryTest {

  @ParameterizedTest
  @ValueSource(ints = {Integer.MIN_VALUE, Integer.MIN_VALUE + 1, 0, Integer.MAX_VALUE - 1, Integer.MAX_VALUE})
  void shouldHandleIntegerBoundaries(int value) {
    assertThat(value).isNotNull();
  }

  @Test
  void shouldDetectIntegerOverflow() {
    assertThatThrownBy(() -> Math.addExact(Integer.MAX_VALUE, 1))
      .isInstanceOf(ArithmeticException.class);
  }

  @Test
  void shouldDetectIntegerUnderflow() {
    assertThatThrownBy(() -> Math.subtractExact(Integer.MIN_VALUE, 1))
      .isInstanceOf(ArithmeticException.class);
  }

  @Test
  void shouldHandleZeroEdge() {
    int result = MathUtils.divide(0, 5);
    assertThat(result).isZero();

    assertThatThrownBy(() -> MathUtils.divide(5, 0))
      .isInstanceOf(ArithmeticException.class);
  }
}
```

## 字符串边界测试

```java
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

class StringBoundaryTest {

  @ParameterizedTest
  @ValueSource(strings = {"", " ", "  ", "\t", "\n"})
  void shouldRejectEmptyAndWhitespace(String input) {
    boolean result = StringUtils.isNotBlank(input);
    assertThat(result).isFalse();
  }

  @Test
  void shouldHandleNullString() {
    String result = StringUtils.trim(null);
    assertThat(result).isNull();
  }

  @Test
  void shouldHandleSingleCharacter() {
    assertThat(StringUtils.capitalize("a")).isEqualTo("A");
    assertThat(StringUtils.trim("x")).isEqualTo("x");
  }

  @Test
  void shouldHandleVeryLongString() {
    String longString = "x".repeat(1000000);

    assertThat(longString.length()).isEqualTo(1000000);
    assertThat(StringUtils.isNotBlank(longString)).isTrue();
  }
}
```

## 集合边界测试

```java
class CollectionBoundaryTest {

  @Test
  void shouldHandleEmptyList() {
    List<String> empty = List.of();

    assertThat(empty).isEmpty();
    assertThat(CollectionUtils.first(empty)).isNull();
    assertThat(CollectionUtils.count(empty)).isZero();
  }

  @Test
  void shouldHandleSingleElementList() {
    List<String> single = List.of("only");

    assertThat(single).hasSize(1);
    assertThat(CollectionUtils.first(single)).isEqualTo("only");
    assertThat(CollectionUtils.last(single)).isEqualTo("only");
  }

  @Test
  void shouldHandleLargeList() {
    List<Integer> large = new ArrayList<>();
    for (int i = 0; i < 100000; i++) {
      large.add(i);
    }

    assertThat(large).hasSize(100000);
    assertThat(CollectionUtils.first(large)).isZero();
    assertThat(CollectionUtils.last(large)).isEqualTo(99999);
  }

  @Test
  void shouldHandleNullInCollection() {
    List<String> withNull = new ArrayList<>(List.of("a", null, "c"));

    assertThat(withNull).contains(null);
    assertThat(CollectionUtils.filterNonNull(withNull)).hasSize(2);
  }
}
```

## 浮点边界测试

```java
class FloatingPointBoundaryTest {

  @Test
  void shouldHandleFloatingPointPrecision() {
    double result = 0.1 + 0.2;
    assertThat(result).isCloseTo(0.3, within(0.0001));
  }

  @Test
  void shouldHandleSpecialFloatingPointValues() {
    assertThat(Double.POSITIVE_INFINITY).isGreaterThan(Double.MAX_VALUE);
    assertThat(Double.NEGATIVE_INFINITY).isLessThan(Double.MIN_VALUE);
    assertThat(Double.NaN).isNotEqualTo(Double.NaN);
  }

  @Test
  void shouldHandleZeroInDivision() {
    assertThat(1.0 / 0.0).isEqualTo(Double.POSITIVE_INFINITY);
    assertThat(-1.0 / 0.0).isEqualTo(Double.NEGATIVE_INFINITY);
    assertThat(0.0 / 0.0).isNaN();
  }
}
```

## 日期/时间边界测试

```java
class DateTimeBoundaryTest {

  @Test
  void shouldHandleMinAndMaxDates() {
    LocalDate min = LocalDate.MIN;
    LocalDate max = LocalDate.MAX;

    assertThat(min).isBefore(max);
    assertThat(DateUtils.isValid(min)).isTrue();
    assertThat(DateUtils.isValid(max)).isTrue();
  }

  @Test
  void shouldHandleLeapYearBoundary() {
    LocalDate leapYearEnd = LocalDate.of(2024, 2, 29);
    assertThat(leapYearEnd).isNotNull();
  }

  @Test
  void shouldRejectInvalidDateInNonLeapYear() {
    assertThatThrownBy(() -> LocalDate.of(2023, 2, 29))
      .isInstanceOf(DateTimeException.class);
  }
}
```

## 数组索引边界测试

```java
class ArrayBoundaryTest {

  @Test
  void shouldHandleFirstElementAccess() {
    int[] array = {1, 2, 3, 4, 5};
    assertThat(array[0]).isEqualTo(1);
  }

  @Test
  void shouldHandleLastElementAccess() {
    int[] array = {1, 2, 3, 4, 5};
    assertThat(array[array.length - 1]).isEqualTo(5);
  }

  @Test
  void shouldThrowOnNegativeIndex() {
    int[] array = {1, 2, 3};
    assertThatThrownBy(() -> array[-1])
      .isInstanceOf(ArrayIndexOutOfBoundsException.class);
  }

  @Test
  void shouldThrowOnOutOfBoundsIndex() {
    int[] array = {1, 2, 3};
    assertThatThrownBy(() -> array[10])
      .isInstanceOf(ArrayIndexOutOfBoundsException.class);
  }

  @Test
  void shouldHandleEmptyArray() {
    int[] empty = {};
    assertThat(empty.length).isZero();
    assertThatThrownBy(() -> empty[0])
      .isInstanceOf(ArrayIndexOutOfBoundsException.class);
  }
}
```

## 最佳实践

- **明确在边界处测试**：不要依赖随机测试
- **将空和空与有效输入分开** 测试
- **使用参数化测试** 用于多个边界情况
- **测试边界两侧**（以下、在、以上）
- **验证无效边界输入的错误消息**
- **记录为什么** 特定边界对你的领域很重要
- **对所有数值操作测试溢出/下溢**

## 限制和警告

- **整数溢出**：使用 `Math.addExact()` 检测静默溢出
- **浮点精度**：永远不要使用精确等式；始终使用基于容差的断言
- **NaN 行为**：`NaN != NaN`；使用 `Float.isNaN()` 或 `Double.isNaN()`
- **集合大小限制**：注意大型测试集合的内存使用情况
- **字符串编码**：使用 Unicode 字符进行国际化测试
- **日期/时间边界**：考虑时区转换和夏令时
- **数组索引**：始终测试索引 0、length-1 和越界

## 参考

- [Integer.MIN_VALUE/MAX_VALUE](https://docs.oracle.com/javase/8/docs/api/java/lang/Integer.html)
- [Double.MIN_VALUE/MAX_VALUE](https://docs.oracle.com/javase/8/docs/api/java/lang/Double.html)
- [AssertJ 浮点](https://assertj.github.io/assertj-core-features-highlight.html#assertions-on-numbers)
- [边界值分析](https://en.wikipedia.org/wiki/Boundary-value_analysis)
- [references/concurrent-testing.md](references/concurrent-testing.md) - 线程安全模式
- [references/parameterized-patterns.md](references/parameterized-patterns.md) - “差一”和参数化示例
