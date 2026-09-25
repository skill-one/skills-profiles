# 单元测试安全与授权

## 概述

本技能提供了使用 `@PreAuthorize`、`@Secured`、`@RolesAllowed` 和自定义权限评估器的 Spring Security 授权逻辑单元测试模式。它涵盖了基于角色的访问控制 (RBAC)、基于表达式的授权、自定义权限评估器以及无需完整 Spring Security 上下文验证访问拒绝场景。

## 何时使用

在以下情况下使用此技能：
- 测试 `@PreAuthorize` 和 `@Secured` 方法级安全
- 测试基于角色的访问控制 (RBAC)
- 测试自定义权限评估器
- 验证访问拒绝场景
- 测试使用经过身份验证的主体的授权
- 需要无需完整 Spring Security 上下文即可快速进行授权测试

## 指令

按照以下步骤测试 Spring Security 授权：

### 1. 设置安全测试依赖项

将 spring-security-test 添加到您的测试依赖项中：

```xml
<dependency>
  <groupId>org.springframework.security</groupId>
  <artifactId>spring-security-test</artifactId>
  <scope>test</scope>
</dependency>
```

### 2. 在测试配置中启用方法安全

```java
@Configuration
@EnableMethodSecurity
class TestSecurityConfig { }
```

### 3. 使用 `@WithMockUser` 进行测试

```java
@Test
@WithMockUser(roles = "ADMIN")
void shouldAllowAdminAccess() {
  assertThatCode(() -> service.deleteUser(1L))
    .doesNotThrowAnyException();
}

@Test
@WithMockUser(roles = "USER")
void shouldDenyUserAccess() {
  assertThatThrownBy(() -> service.deleteUser(1L))
    .isInstanceOf(AccessDeniedException.class);
}
```

### 4. 测试自定义权限评估器

```java
@Test
void shouldGrantPermissionToOwner() {
  Authentication auth = new UsernamePasswordAuthenticationToken(
    "alice", null, List.of(new SimpleGrantedAuthority("ROLE_USER"))
  );
  Document doc = new Document(1L, "Test", new User("alice"));

  boolean result = evaluator.hasPermission(auth, doc, "WRITE");
  assertThat(result).isTrue();
}
```

### 5. 验证安全是否激活

如果测试意外通过，请添加此断言以验证安全是否生效：

```java
@Test
void shouldRejectUnauthorizedWhenSecurityEnabled() {
  assertThatThrownBy(() -> service.deleteUser(1L))
    .isInstanceOf(AccessDeniedException.class);
}
```

## 快速参考

| 注解 | 描述 | 示例 |
|------------|-------------|---------|
| `@PreAuthorize` | 调用前授权 | `@PreAuthorize("hasRole('ADMIN')")` |
| `@PostAuthorize` | 调用后授权 | `@PostAuthorize("returnObject.owner == authentication.name")` |
| `@Secured` | 简单基于角色的安全 | `@Secured("ROLE_ADMIN")` |
| `@RolesAllowed` | JSR-250 标准 | `@RolesAllowed({"ADMIN", "MANAGER"})` |
| `@WithMockUser` | 测试注解 | `@WithMockUser(roles = "ADMIN")` |

## 示例

### 基本的 `@PreAuthorize` 测试

```java
@Service
public class UserService {
  @PreAuthorize("hasRole('ADMIN')")
  public void deleteUser(Long userId) {
    // 删除逻辑
  }
}

// 测试
@Test
@WithMockUser(roles = "ADMIN")
void shouldAllowAdminToDeleteUser() {
  assertThatCode(() -> service.deleteUser(1L))
    .doesNotThrowAnyException();
}

@Test
@WithMockUser(roles = "USER")
void shouldDenyUserFromDeletingUser() {
  assertThatThrownBy(() -> service.deleteUser(1L))
    .isInstanceOf(AccessDeniedException.class);
}
```

### 基于表达式的安全测试

```java
@PreAuthorize("#userId == authentication.principal.id")
public UserProfile getUserProfile(Long userId) {
  // 获取个人资料
}

// 对于自定义主体属性，使用 @WithUserDetails 与自定义 UserDetailsService
@Test
@WithUserDetails("alice")
void shouldAllowUserToAccessOwnProfile() {
  assertThatCode(() -> service.getUserProfile(1L))
    .doesNotThrowAnyException();
}
```

> **验证提示**：如果安全测试意外通过，请验证测试配置中是否启用了 `@EnableMethodSecurity`——缺少注解会导致所有 `@PreAuthorize` 检查被静默绕过。

有关更多基本模式和复杂表达式及自定义评估器的信息，请参阅 [references/basic-testing.md](references/basic-testing.md) 和 [references/advanced-authorization.md](references/advanced-authorization.md)。

## 最佳实践

1. **使用 `@WithMockUser`** 设置经过身份验证的用户上下文
2. **测试每个安全规则的允许和拒绝情况**
3. **使用不同的角色进行测试** 以验证基于角色的决策
4. **全面测试基于表达式的安全**
5. **模拟外部依赖项**（权限评估器等）
6. **单独测试匿名访问** 与经过身份验证的访问
7. **在配置中使用 `@EnableGlobalMethodSecurity`** 进行方法级安全

## 常见陷阱

- 忘记在测试配置中启用方法安全
- 不测试允许和拒绝场景
- 测试框架代码而不是授权逻辑
- 测试中未处理 null 身份验证
- 不必要地混合身份验证和授权测试

## 限制和警告

- **方法安全需要代理**：`@PreAuthorize` 通过代理工作；直接方法调用会绕过安全
- **`@EnableGlobalMethodSecurity`**：必须启用才能使 `@PreAuthorize`、`@Secured` 工作
- **角色前缀**：Spring 会自动添加 "ROLE_" 前缀；使用 `hasRole('ADMIN')` 而不是 `hasRole('ROLE_ADMIN')`
- **身份验证上下文**：安全上下文是线程本地的；异步测试时要小心
- **`@WithMockUser` 限制**：创建简单的 Authentication；复杂的身份验证场景需要自定义设置
- **SpEL 表达式**：`@PreAuthorize` 中的复杂 SpEL 难以调试；彻底测试
- **性能影响**：方法安全会增加开销；在层边界考虑安全

## 参考

### 设置和配置
- **[references/setup.md](references/setup.md)** - Maven/Gradle 依赖项和安全配置

### 测试模式
- **[references/basic-testing.md](references/basic-testing.md)** - `@PreAuthorize`、`@Secured`、MockMvc 测试和参数化测试的基本模式

### 高级主题
- **[references/advanced-authorization.md](references/advanced-authorization.md)** - 基于表达式的授权、自定义权限评估器、SpEL 表达式

### 完整示例
- **[references/complete-examples.md](references/complete-examples.md)** - 展示从手动到声明式安全转换的示例
