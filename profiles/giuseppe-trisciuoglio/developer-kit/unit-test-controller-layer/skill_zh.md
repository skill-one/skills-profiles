# 使用 MockMvc 进行 REST 控制器单元测试

## 概述

提供使用 MockMvc 对 `@RestController` 和 `@Controller` 类进行单元测试的模式。涵盖请求/响应处理、HTTP 状态码、请求参数绑定、验证、内容协商、响应头和模拟服务依赖的异常处理。

## 使用场景

用于：控制器测试、API 端点测试、Spring MVC 测试、模拟 HTTP 请求、Web 层端点单元测试、隔离验证 REST 控制器。

## 使用说明

1. **设置独立 MockMvc**：`MockMvcBuilders.standaloneSetup(controller)` 用于隔离测试
2. **模拟服务依赖**：使用 `@Mock` 对所有服务进行模拟，使用 `@InjectMocks` 对控制器进行注入
3. **测试 HTTP 方法**：使用正确的状态码测试 GET、POST、PUT、PATCH、DELETE
4. **验证响应**：使用 JsonPath 断言 JSON，使用内容匹配器验证正文
5. **测试验证**：发送无效输入，验证 400 状态码和错误详情
6. **测试错误**：验证 404、400、401、403、500 在适当条件下的表现
7. **验证头信息**：请求头（Authorization）和响应头
8. **测试内容协商**：不同的 Accept 和 Content-Type 头

### 验证工作流

```
运行测试 → 如果失败：添加 .andDo(print()) → 对比实际与预期 → 修正断言
```

## 示例

### Maven / Gradle 依赖

```xml
<dependency>
  <groupId>org.springframework.boot</groupId>
  <artifactId>spring-boot-starter-test</artifactId>
  <scope>test</scope>
</dependency>
```

### 基本模式：GET 端点

```java
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@ExtendWith(MockitoExtension.class)
class UserControllerTest {

  @Mock
  private UserService userService;

  @InjectMocks
  private UserController userController;

  private MockMvc mockMvc;

  @BeforeEach
  void setUp() {
    mockMvc = MockMvcBuilders.standaloneSetup(userController).build();
  }

  @Test
  void shouldReturnAllUsers() throws Exception {
    List<UserDto> users = List.of(new UserDto(1L, "Alice"), new UserDto(2L, "Bob"));
    when(userService.getAllUsers()).thenReturn(users);

    mockMvc.perform(get("/api/users"))
      .andExpect(status().isOk())
      .andExpect(jsonPath("$[0].id").value(1))
      .andExpect(jsonPath("$[0].name").value("Alice"));

    verify(userService, times(1)).getAllUsers();
  }

  @Test
  void shouldReturn404WhenUserNotFound() throws Exception {
    when(userService.getUserById(999L))
      .thenThrow(new UserNotFoundException("User not found"));

    mockMvc.perform(get("/api/users/999"))
      .andExpect(status().isNotFound());

    verify(userService).getUserById(999L);
  }
}
```

### POST：创建资源

```java
@Test
void shouldCreateUserAndReturn201() throws Exception {
  UserDto createdUser = new UserDto(1L, "Alice", "alice@example.com");
  when(userService.createUser(any())).thenReturn(createdUser);

  mockMvc.perform(post("/api/users")
      .contentType("application/json")
      .content("{\"name\":\"Alice\",\"email\":\"alice@example.com\"}"))
    .andExpect(status().isCreated())
    .andExpect(jsonPath("$.id").value(1))
    .andExpect(jsonPath("$.name").value("Alice"));

  verify(userService).createUser(any(UserCreateRequest.class));
}
```

### PUT：更新资源

```java
@Test
void shouldUpdateUserAndReturn200() throws Exception {
  UserDto updatedUser = new UserDto(1L, "Updated");
  when(userService.updateUser(eq(1L), any())).thenReturn(updatedUser);

  mockMvc.perform(put("/api/users/1")
      .contentType("application/json")
      .content("{\"name\":\"Updated\"}"))
    .andExpect(status().isOk())
    .andExpect(jsonPath("$.name").value("Updated"));

  verify(userService).updateUser(eq(1L), any());
}
```

### DELETE：删除资源

```java
@Test
void shouldDeleteUserAndReturn204() throws Exception {
  doNothing().when(userService).deleteUser(1L);

  mockMvc.perform(delete("/api/users/1"))
    .andExpect(status().isNoContent());

  verify(userService).deleteUser(1L);
}
```

### 查询参数

```java
@Test
void shouldFilterUsersByName() throws Exception {
  when(userService.searchUsers("Alice")).thenReturn(List.of(new UserDto(1L, "Alice")));

  mockMvc.perform(get("/api/users/search").param("name", "Alice"))
    .andExpect(status().isOk())
    .andExpect(jsonPath("$[0].name").value("Alice"));

  verify(userService).searchUsers("Alice");
}
```

### 路径变量

```java
@Test
void shouldGetUserByIdFromPath() throws Exception {
  when(userService.getUserById(123L)).thenReturn(new UserDto(123L, "Alice"));

  mockMvc.perform(get("/api/users/{id}", 123L))
    .andExpect(status().isOk())
    .andExpect(jsonPath("$.id").value(123));
}
```

### 验证错误 (400)

```java
@Test
void shouldReturn400WhenRequestBodyInvalid() throws Exception {
  mockMvc.perform(post("/api/users")
      .contentType("application/json")
      .content("{\"name\":\"\"}"))
    .andExpect(status().isBadRequest())
    .andExpect(jsonPath("$.errors").isArray());
}
```

### 响应头

```java
@Test
void shouldReturnCustomHeaders() throws Exception {
  when(userService.getAllUsers()).thenReturn(List.of());

  mockMvc.perform(get("/api/users"))
    .andExpect(status().isOk())
    .andExpect(header().exists("X-Total-Count"))
    .andExpect(header().string("X-Total-Count", "0"));
}
```

### Authorization 头

```java
@Test
void shouldRequireAuthorizationHeader() throws Exception {
  mockMvc.perform(get("/api/users"))
    .andExpect(status().isUnauthorized());

  mockMvc.perform(get("/api/users").header("Authorization", "Bearer token"))
    .andExpect(status().isOk());
}
```

### 内容协商

```java
@Test
void shouldReturnJsonWhenAcceptHeaderIsJson() throws Exception {
  when(userService.getUserById(1L)).thenReturn(new UserDto(1L, "Alice"));

  mockMvc.perform(get("/api/users/1").accept("application/json"))
    .andExpect(status().isOk())
    .andExpect(content().contentType("application/json"));
}
```

## 最佳实践

- 使用 `standaloneSetup()` 进行隔离的控制器测试
- 模拟服务层 — 控制器处理 HTTP，服务处理业务逻辑
- 验证模拟交互：`verify(service).method(args)`
- 测试成功路径和错误场景（404、400、500）
- 使用 `jsonPath()` 进行流畅的 JSON 断言
- 每个测试方法一个专注的断言

## 限制和警告

- 控制器测试仅验证 HTTP 处理 — 不完整请求流程
- `standaloneSetup()` 可能不支持 `@Validated` 而无完整上下文
- JsonPath 需要在响应正文中包含有效 JSON
- `@PreAuthorize`/`@Secured` 需要额外设置 — 考虑单独的安全测试
- 文件上传需要 `MockMultipartFile`

## 参考

- [Spring MockMvc 文档](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/test/web/servlet/MockMvc.html)
- [Spring 测试最佳实践](https://docs.spring.io/spring-boot/docs/current/reference/html/features.html#features.testing)
