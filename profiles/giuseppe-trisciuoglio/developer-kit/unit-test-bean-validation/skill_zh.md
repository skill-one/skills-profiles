# Jakarta Bean Validation 单元测试

## 概述

本技能提供使用 JUnit 5 对 Jakarta Bean Validation 注解和自定义验证器进行单元测试的可执行模式。涵盖内置约束（`@NotNull`、`@Email`、`@Min`、`@Max`、`@Size`）、自定义 `@Constraint` 实现方案、跨字段验证和验证组。测试在隔离环境中运行，无需 Spring 上下文。

## 使用场景

- 编写 Jakarta Bean Validation 或 JSR-380 约束的单元测试
- 测试自定义 `@Constraint` 验证器和约束违反消息
- 测试 DTO 和请求对象中的 Bean 验证逻辑
- 验证跨字段验证（例如密码匹配）
- 测试使用验证组的条件验证
- 无需 Spring Boot 上下文的快速验证测试

## 使用说明

1. **添加依赖项**：将 `jakarta.validation-api` 和 `hibernate-validator` 添加到测试作用域
2. **创建基础测试类**：在 `@BeforeEach` 中使用 `Validation.buildDefaultValidatorFactory()` 一次性构建 `Validator`
3. **先测试有效情况**：验证对象在无违反情况下通过
4. **测试无效情况**：断言约束违反包含正确的属性路径和消息
5. **提取违反详情**：使用 `getPropertyPath()`、`getMessage()`、`getInvalidValue()` 获取
6. **测试自定义验证器**：参考 `references/custom-validators.md` 获取模式
7. **使用参数化测试**：使用 `@ParameterizedTest` 高效测试多个输入
8. **分组验证测试**：使用验证组进行条件规则测试（参考 `references/advanced-patterns.md`）

## 示例

### Maven 配置

```xml
<dependency>
  <groupId>jakarta.validation</groupId>
  <artifactId>jakarta.validation-api</artifactId>
</dependency>
<dependency>
  <groupId>org.hibernate.validator</groupId>
  <artifactId>hibernate-validator</artifactId>
  <scope>test</scope>
</dependency>
<dependency>
  <groupId>org.assertj</groupId>
  <artifactId>assertj-core</artifactId>
  <scope>test</scope>
</dependency>
```

### 常见测试配置

```java
import jakarta.validation.*;
import jakarta.validation.ConstraintViolation;
import jakarta.validation.path.Path;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.assertj.core.api.Assertions.assertThat;

class BaseValidationTest {
  protected Validator validator;

  @BeforeEach
  void setUpValidator() {
    validator = Validation.buildDefaultValidatorFactory().getValidator();
  }
}
```

### 测试基本约束

```java
class UserDtoTest extends BaseValidationTest {

  @Test
  void shouldPassValidationWithValidUser() {
    UserDto user = new UserDto("Alice", "alice@example.com", 25);
    assertThat(validator.validate(user)).isEmpty();
  }

  @Test
  void shouldFailWhenNameIsNull() {
    UserDto user = new UserDto(null, "alice@example.com", 25);
    assertThat(validator.validate(user))
      .extracting(ConstraintViolation::getMessage)
      .contains("must not be blank");
  }

  @Test
  void shouldFailWhenEmailIsInvalid() {
    UserDto user = new UserDto("Alice", "invalid-email", 25);
    Set<ConstraintViolation<UserDto>> violations = validator.validate(user);
    assertThat(violations)
      .extracting(ConstraintViolation::getPropertyPath)
      .extracting(Path::toString)
      .contains("email");
  }

  @Test
  void shouldFailWhenAgeIsBelowMinimum() {
    UserDto user = new UserDto("Alice", "alice@example.com", -1);
    assertThat(validator.validate(user))
      .extracting(ConstraintViolation::getMessage)
      .contains("must be greater than or equal to 0");
  }

  @Test
  void shouldFailWhenMultipleConstraintsViolated() {
    UserDto user = new UserDto(null, "invalid", -5);
    assertThat(validator.validate(user)).hasSize(3);
  }
}
```

### 测试自定义验证器

自定义约束模式参考 `references/custom-validators.md`：
- 创建 `@Constraint` 注解
- 实现 `ConstraintValidator`
- 跨字段验证（密码匹配）
- 状态无关验证器最佳实践

### 测试验证组

验证组和参数化测试参考 `references/advanced-patterns.md`：
- 定义验证组接口
- 使用 `groups` 参数进行条件验证
- `@ParameterizedTest` 与 `@ValueSource` 和 `@CsvSource` 结合使用
- 调试失败的验证测试

## 最佳实践

- **测试有效和无效情况**：每个约束都需要通过和失败的测试用例
- **断言违反详情**：验证属性路径、消息和约束类型
- **测试边界情况**：null、空字符串、空白、边界值
- **保持验证器状态无关**：自定义验证器不能维护状态
- **使用清晰消息**：约束消息应用户友好
- **分组相关测试**：扩展 `BaseValidationTest` 共享验证器配置
- **测试错误消息**：确保消息符合要求

## 常见陷阱

- 忘记测试 null 值（大多数约束默认忽略 null）
- 未验证约束违反中的属性路径
- 在服务/控制器级别而非单元级别进行验证测试
- 创建过于复杂的自定义验证器
- 必填字段与其他约束组合时缺少 `@NotNull`

## 约束和警告

- **null 处理**：大多数约束默认忽略 null — 使用 `@NotNull` 与其他约束组合实现必填字段
- **线程安全**：`Validator` 实例线程安全且可共享
- **消息本地化**：如需 i18n 需测试不同区域设置
- **级联验证**：在嵌套对象上使用 `@Valid` 进行递归验证
- **自定义验证器**：必须状态无关且对 null 返回 `true`
- **测试隔离**：验证单元测试不应依赖 Spring 上下文或数据库

## 故障排除

**ValidatorFactory 未找到**：确保 `jakarta.validation-api` 和 `hibernate-validator` 在测试类路径上。

**自定义验证器未调用**：验证 `@Constraint(validatedBy = YourValidator.class)` 注解是否正确。

**null 值通过验证**：这是预期行为 — 除非存在 `@NotNull`，否则约束会忽略 null。

**违反数量错误**：使用 `hasSize()` 验证确切数量，检查对象所有字段。

**属性路径错误**：确保字段而非 getter 有约束注解。

## 参考

- [Jakarta Bean Validation 规范](https://jakarta.ee/specifications/bean-validation/)
- [Hibernate Validator](https://hibernate.org/validator/)
- 自定义验证器和跨字段验证：`references/custom-validators.md`
- 验证组和参数化测试：`references/advanced-patterns.md`
