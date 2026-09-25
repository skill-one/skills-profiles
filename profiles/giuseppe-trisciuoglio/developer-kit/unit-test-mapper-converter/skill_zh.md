# 单元测试映射器和转换器

## 概述

提供用于单元测试 MapStruct 映射器和自定义转换器类的模式。涵盖字段映射准确性、空值处理、类型转换、嵌套对象转换、双向映射、枚举映射和部分更新。

## 使用场景

- 编写 MapStruct 映射器实现映射测试
- 测试自定义实体到 DTO 转换器和 Bean 映射
- 验证嵌套对象映射和集合转换

## 指令

### 1. 验证生成的映射器类
在测试前，验证生成的映射器类是否存在：
```bash
# Maven
ls target/generated-sources/

# Gradle
ls build/generated/sources/
```

**如果生成的类缺失：**
1. 运行 `mvn compile` (Maven) 或 `./gradlew compileJava` (Gradle)
2. 检查 MapStruct 注解处理器是否配置正确
3. 验证 `@Mapper` 接口是否在编译源集中

### 2. 测试空值处理
```java
assertThat(mapper.toDto(null)).isNull();
```
如果空值应返回空/默认值，请在映射器中配置 `nullValueMappingStrategy`。

**如果空值测试失败：**
1. 在 `@Mapper` 中添加 `nullValueMappingStrategy = NullValueMappingStrategy.RETURN_NULL`
2. 或使用 `nullValuePropertyMappingStrategy` 处理嵌套属性

### 3. 测试双向映射
```java
User restored = mapper.toEntity(mapper.toDto(original));
assertThat(restored).usingRecursiveComparison().isEqualTo(original);
```

**如果双向测试失败：**
1. 检查 `@Mapping` 注解中的字段名不匹配
2. 如果自动映射失败，请验证两个方向是否都明确映射
3. 使用 `unmappedTargetPolicy = ReportingPolicy.ERROR` 捕获缺失的映射

### 4. 测试嵌套对象映射
```java
assertThat(dto.getNested()).usingRecursiveComparison().isEqualTo(expected);
```

**如果嵌套测试失败：**
1. 确保嵌套映射器存在或通过 `uses = NestedMapper.class` 引用
2. 检查集合元素映射策略 `elementMappingStrategy`

### 5. 测试自定义表达式
`@Mapping(target = "field", expression = "java(...)")` 中的自定义表达式不会在编译时验证。

**如果表达式测试失败：**
1. 验证表达式语法和方法签名
2. 检查导入的类是否可以从表达式上下文中访问

### 6. 测试枚举映射
使用 `@ValueMapping` 进行枚举到枚举的转换。穷尽测试所有枚举值。

## 最佳实践

- 使用 `Mappers.getMapper()` 进行独立测试，使用 Spring 注入进行集成测试
- 使用 `usingRecursiveComparison()` 测试复杂嵌套结构
- 测试所有映射器方法，包括集合转换
- 验证所有可空源字段的空值处理
- 测试双向映射捕获实体→DTO 和 DTO→实体之间的不对称性
- 保持映射器测试专注于转换正确性，而非实现细节

## 限制和警告

- **编译时生成**：MapStruct 在编译时生成代码——在运行测试前验证生成的类是否存在
- **空值处理**：适当配置 `nullValueMappingStrategy` 和 `nullValuePropertyMappingStrategy`
- **表达式验证**：`@Mapping` 中的表达式不会在编译时验证——显式测试它们
- **循环依赖**：MapStruct 无法处理映射器之间的循环依赖
- **集合不可变性**：映射不可变集合可能需要特殊配置
- **日期/时间**：验证日期/时间对象是否正确跨时区映射

## 示例

包含导入的完整可执行测试：
```java
package com.example.mapper;

import org.junit.jupiter.api.Test;
import org.mapstruct.factory.Mappers;
import static org.assertj.core.api.Assertions.assertThat;

class UserMapperCompleteTest {
  private final UserMapper mapper = Mappers.getMapper(UserMapper.class);

  @Test
  void shouldMapUserToDto() {
    User user = new User(1L, "Alice", "alice@example.com", 25);
    UserDto dto = mapper.toDto(user);
    assertThat(dto)
      .isNotNull()
      .extracting(UserDto::getName, UserDto::getEmail)
      .containsExactly("Alice", "alice@example.com");
  }

  @Test
  void shouldMaintainRoundTrip() {
    User original = new User(1L, "Alice", "alice@example.com", 25);
    assertThat(mapper.toEntity(mapper.toDto(original)))
      .usingRecursiveComparison()
      .isEqualTo(original);
  }

  @Test
  void shouldHandleNullInput() {
    assertThat(mapper.toDto(null)).isNull();
  }
}
```

更多示例：`references/examples.md`
