# 单元测试ExceptionHandler和ControllerAdvice

## 概述

本技能提供编写Spring Boot异常处理器单元测试的模式。它涵盖了使用MockMvc测试`@ExceptionHandler`方法，包括HTTP状态断言、JSON响应验证、字段级验证错误测试以及模拟处理器依赖。

## 使用场景

- 编写`@ExceptionHandler`方法的单元测试
- 测试`@ControllerAdvice`全局异常处理
- 验证REST API错误响应格式
- 在控制器测试中模拟异常
- 测试字段级验证错误响应
- 断言自定义错误负载和HTTP状态码

## 指令

1. **创建一个测试控制器**，抛出特定异常以触发每个`@ExceptionHandler`
2. 通过`MockMvcBuilders.standaloneSetup()`上的`setControllerAdvice()`注册`ControllerAdvice`
3. 使用`.andExpect(status().isXxx())`断言HTTP状态码
4. 使用`jsonPath("$.field")`匹配器验证错误响应字段
5. 通过发送无效负载并检查`MethodArgumentNotValidException`产生字段级详细信息来测试验证错误
6. 使用`.andDo(print())`调试失败——如果处理器未被调用，请验证是否调用了`setControllerAdvice()`且异常类型匹配

## 示例

### 异常处理器和错误DTO

```java
@ControllerAdvice
public class GlobalExceptionHandler {

  @ExceptionHandler(ResourceNotFoundException.class)
  @ResponseStatus(HttpStatus.NOT_FOUND)
  public ErrorResponse handleNotFound(ResourceNotFoundException ex) {
    return new ErrorResponse(404, "Not Found", ex.getMessage());
  }

  @ExceptionHandler(ValidationException.class)
  @ResponseStatus(HttpStatus.BAD_REQUEST)
  public ErrorResponse handleValidation(ValidationException ex) {
    return new ErrorResponse(400, "Bad Request", ex.getMessage());
  }

  @ExceptionHandler(MethodArgumentNotValidException.class)
  @ResponseStatus(HttpStatus.BAD_REQUEST)
  public ValidationErrorResponse handleMethodArgumentNotValid(MethodArgumentNotValidException ex) {
    Map<String, String> errors = new HashMap<>();
    ex.getBindingResult().getFieldErrors().forEach(e -> errors.put(e.getField(), e.getDefaultMessage()));
    return new ValidationErrorResponse(400, "Validation Failed", errors);
  }
}

public record ErrorResponse(int status, String error, String message) {}
public record ValidationErrorResponse(int status, String error, Map<String, String> errors) {}
```

### 单元测试

```java
@ExtendWith(MockitoExtension.class)
class GlobalExceptionHandlerTest {

  private MockMvc mockMvc;

  @BeforeEach
  void setUp() {
    GlobalExceptionHandler handler = new GlobalExceptionHandler();
    mockMvc = MockMvcBuilders.standaloneSetup(new TestController())
        .setControllerAdvice(handler)
        .build();
  }

  @Test
  void shouldReturn404WhenResourceNotFound() throws Exception {
    mockMvc.perform(get("/api/users/999"))
        .andExpect(status().isNotFound())
        .andExpect(jsonPath("$.status").value(404))
        .andExpect(jsonPath("$.error").value("Not Found"))
        .andExpect(jsonPath("$.message").value("User not found"));
  }

  @Test
  void shouldReturn400WithFieldErrorsOnValidationFailure() throws Exception {
    mockMvc.perform(post("/api/users")
        .contentType("application/json")
        .content("{\"name\":\"\",\"email\":\"invalid\"}"))
        .andExpect(status().isBadRequest())
        .andExpect(jsonPath("$.status").value(400))
        .andExpect(jsonPath("$.errors.name").value("must not be blank"))
        .andExpect(jsonPath("$.errors.email").value("must be a valid email"));
  }
}

@RestController
@RequestMapping("/api")
class TestController {
  @GetMapping("/users/{id}") public User getUser(@PathVariable Long id) {
    throw new ResourceNotFoundException("User not found");
  }
  @PostMapping("/users") public User createUser(@RequestBody @Valid User user) {
    throw new ValidationException("Validation failed");
  }
}
```

## 最佳实践

- 使用专用异常抛出独立测试每个`@ExceptionHandler`方法
- 通过`setControllerAdvice()`注册一个`@ControllerAdvice`实例——永远不要跳过
- 断言错误响应体中的所有字段，而不仅仅是HTTP状态码
- 对于验证错误，验证字段名称键和错误消息值
- 使用`MockMvcBuilders.standaloneSetup()`进行隔离的处理器测试，无需完整的Spring上下文
- 记录断言失败：将`.andDo(print())`链接到测试失败时打印请求/响应

## 常见陷阱

- 处理器未被调用：确保在构建器上调用`setControllerAdvice()`
- JsonPath不匹配：使用`.andDo(print())`检查实际响应结构
- 状态为200：处理器方法缺少`@ResponseStatus`
- 重复处理器：`@Order`控制优先级；更具体的异常类型优先
- 测试处理器逻辑而不是行为：模拟外部依赖，仅测试响应转换

## 限制和警告

- **`@ExceptionHandler`特异性**：更具体的异常类型优先匹配；`Exception.class`捕获所有未匹配类型
- **`@ResponseStatus`默认值**：没有`@ResponseStatus`或返回`ResponseEntity`，HTTP状态默认为200
- **全局与局部范围**：`@ControllerAdvice`中的`@ExceptionHandler`是全局的；在控制器中声明的是仅限于该控制器的局部
- **日志副作用**：记录的处理器应使用`verify(mockLogger).logXxx(...)`进行验证
- **本地化**：使用`MessageSource`时，测试不同的`Locale`值以确认消息解析
- **安全上下文**：`AuthorizationException`处理器可以访问`SecurityContextHolder`——测试上下文是否正确评估
