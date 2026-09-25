# Spring Boot REST API 规范

## 概述

Spring Boot 的 REST API 设计规范，涵盖 URL 设计、HTTP 方法、状态码、DTO、验证、错误处理、分页和安全头。

## 使用场景

- 创建 REST 端点和 API 路由
- 设计 DTO 和 API 合约
- 实现错误处理和验证
- 设置分页和过滤
- 配置安全头和 CORS
- 审查 REST API 架构

## 指南

### 构建 RESTful API 端点

遵循以下步骤创建设计良好的 REST API 端点：

1. **设计基于资源的 URL**
   - 使用复数名词作为资源名称
   - 遵循 REST 规范：GET /users, POST /users, PUT /users/{id}
   - 避免基于操作的 URL，如 /getUserList

2. **实现适当的 HTTP 方法**
   - GET：检索资源（安全、幂等）
   - POST：创建资源（非幂等）
   - PUT：替换整个资源（幂等）
   - PATCH：部分更新（非幂等）
   - DELETE：删除资源（幂等）

3. **使用适当的状态码**
   - 200 OK：成功的 GET/PUT/PATCH
   - 201 Created：成功的 POST 并包含 Location 头
   - 204 No Content：成功的 DELETE
   - 400 Bad Request：无效请求数据
   - 404 Not Found：资源不存在
   - 409 Conflict：重复资源
   - 500 Internal Server Error：意外错误

4. **创建请求/响应 DTO**
   - 将 API 合约与领域实体分离
   - 使用 Java 记录或 Lombok `@Data`/`@Value`
   - 应用 Jakarta 验证注解
   - 尽可能使 DTO 保持不可变

5. **实现验证**
   - 在 `@RequestBody` 参数上使用 `@Valid` 注解
   - 应用验证约束（`@NotBlank`, `@Email`, `@Size` 等）
   - 使用 `MethodArgumentNotValidException` 处理验证错误

6. **设置错误处理**
   - 使用 `@RestControllerAdvice` 进行全局异常处理
   - 返回标准化的错误响应，包含状态、错误、消息和时间戳
   - 使用 `ResponseStatusException` 表示特定的 HTTP 状态码

7. **配置分页**
   - 使用 Pageable 处理大型数据集
   - 包含页码、大小、排序参数
   - 返回包含总元素数、总页数等元数据

8. **添加安全头**
   - 配置 CORS 策略
   - 设置内容安全策略
   - 包含 X-Frame-Options, X-Content-Type-Options

**验证检查点：**
- 步骤 1-2 后：验证 URL 结构遵循 REST 规范（/users 而不是 /getUsers）
- 步骤 3 后：测试每个端点返回正确的状态码
- 步骤 4-5 后：在继续之前使用 curl 或 HTTPie 验证 DTO
- 步骤 6 后：确认错误响应匹配标准化格式

## 示例

### 基本 CRUD 控制器

```java
@RestController
@RequestMapping("/v1/users")
@RequiredArgsConstructor
@Slf4j
public class UserController {
    private final UserService userService;

    @GetMapping
    public ResponseEntity<Page<UserResponse>> getAllUsers(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int pageSize) {
        log.debug("Fetching users page {} size {}", page, pageSize);
        Page<UserResponse> users = userService.getAll(page, pageSize);
        return ResponseEntity.ok(users);
    }

    @GetMapping("/{id}")
    public ResponseEntity<UserResponse> getUserById(@PathVariable Long id) {
        return ResponseEntity.ok(userService.getById(id));
    }

    @PostMapping
    public ResponseEntity<UserResponse> createUser(@Valid @RequestBody CreateUserRequest request) {
        UserResponse created = userService.create(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }

    @PutMapping("/{id}")
    public ResponseEntity<UserResponse> updateUser(
            @PathVariable Long id,
            @Valid @RequestBody UpdateUserRequest request) {
        return ResponseEntity.ok(userService.update(id, request));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        userService.delete(id);
        return ResponseEntity.noContent().build();
    }
}
```

### 请求/响应 DTO

```java
// 请求 DTO
@Data
@NoArgsConstructor
@AllArgsConstructor
public class CreateUserRequest {
    @NotBlank(message = "用户名不能为空")
    private String name;

    @Email(message = "需要有效的邮箱")
    private String email;
}

// 响应 DTO
@Data
@NoArgsConstructor
@AllArgsConstructor
public class UserResponse {
    private Long id;
    private String name;
    private String email;
    private LocalDateTime createdAt;
}
```

### 全局异常处理器

```java
@RestControllerAdvice
@Slf4j
public class GlobalExceptionHandler {

    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<ErrorResponse> handleValidationException(
            MethodArgumentNotValidException ex, WebRequest request) {
        String errors = ex.getBindingResult().getFieldErrors().stream()
                .map(f -> f.getField() + ": " + f.getDefaultMessage())
                .collect(Collectors.joining(", "));

        ErrorResponse errorResponse = new ErrorResponse(
                HttpStatus.BAD_REQUEST.value(),
                "验证错误",
                "验证失败: " + errors,
                request.getDescription(false).replaceFirst("uri=", "")
        );
        return new ResponseEntity<>(errorResponse, HttpStatus.BAD_REQUEST);
    }

    @ExceptionHandler(ResponseStatusException.class)
    public ResponseEntity<ErrorResponse> handleResponseStatusException(
            ResponseStatusException ex, WebRequest request) {
        ErrorResponse error = new ErrorResponse(
            ex.getStatusCode().value(),
            ex.getStatusCode().toString(),
            ex.getReason(),
            request.getDescription(false).replaceFirst("uri=", "")
        );
        return new ResponseEntity<>(error, ex.getStatusCode());
    }
}
```

## 最佳实践

### 1. 使用构造器注入

```java
@Service
@RequiredArgsConstructor
public class UserService {
    private final UserRepository userRepository;
}
```

### 2. 优先使用不可变的 DTO（Java 记录或 `@Value`）

```java
public record UserResponse(Long id, String name, String email) {}
```

### 3. 实现适当的事务管理

```java
@Service
@Transactional
public class UserService {
    @Transactional(readOnly = true)
    public Optional<User> findById(Long id) { return userRepository.findById(id); }

    @Transactional
    public User create(User user) { return userRepository.save(user); }
}
```

## 约束和警告

1. **永远不要直接暴露实体** - 使用 DTO 将 API 合约与领域模型分离
2. **遵循 REST 规范** - 使用名词作为资源（/users）、正确的 HTTP 方法、复数名称、适当的状态码
3. **全局处理所有异常** - 使用 `@RestControllerAdvice`，永远不要让原始异常冒泡
4. **始终对大型结果集进行分页** - 防止性能问题和 DDoS 漏洞
5. **验证所有输入数据** - 在请求 DTO 上使用 Jakarta 验证注解
6. **永远不要暴露敏感数据** - 不要记录或暴露密码、令牌、个人身份信息

## 参考

- 参考 `references/` 目录获取全面的参考材料，包括 HTTP 状态码、Spring 注解和详细示例
- 参考 `developer-kit-java:spring-boot-code-review-expert` 代理获取代码审查指南
- 查看 `spring-boot-dependency-injection/SKILL.md` 获取依赖注入模式
- 查看 `../spring-boot-test-patterns/SKILL.md` 获取测试 REST API 的指南
