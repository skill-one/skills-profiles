# Spring Boot Resilience4j 模式

## 概述

为 Spring Boot 3.x 提供故障容错模式（熔断器、重试、速率限制、限流器、时间限制、降级），包含配置和测试工作流。

## 使用场景

- 实现故障容错并防止级联故障
- 为服务调用添加熔断器、重试逻辑或速率限制
- 使用指数退避处理瞬时故障
- 保护服务免受过载和资源耗尽
- 组合多种模式实现全面容错

## 使用说明

### 1. 设置和依赖

将 Resilience4j 依赖添加到项目中。对于 Maven，添加到 `pom.xml`：

```xml
<dependency>
    <groupId>io.github.resilience4j</groupId>
    <artifactId>resilience4j-spring-boot3</artifactId>
    <version>2.2.0</version> // 使用最新稳定版本
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-aop</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```

对于 Gradle，添加到 `build.gradle`：

```gradle
implementation "io.github.resilience4j:resilience4j-spring-boot3:2.2.0"
implementation "org.springframework.boot:spring-boot-starter-aop"
implementation "org.springframework.boot:spring-boot-starter-actuator"
```

使用 `@EnableAspectJAutoProxy` 启用 AOP 注解处理（由 Spring Boot 自动配置）。

### 2. 熔断器模式

将 `@CircuitBreaker` 注解应用于调用外部服务的接口：

```java
@Service
public class PaymentService {
    private final RestTemplate restTemplate;

    public PaymentService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    @CircuitBreaker(name = "paymentService", fallbackMethod = "paymentFallback")
    public PaymentResponse processPayment(PaymentRequest request) {
        return restTemplate.postForObject("http://payment-api/process",
            request, PaymentResponse.class);
    }

    private PaymentResponse paymentFallback(PaymentRequest request, Exception ex) {
        return PaymentResponse.builder()
            .status("PENDING")
            .message("服务暂时不可用")
            .build();
    }
}
```

在 `application.yml` 中配置：

```yaml
resilience4j:
  circuitbreaker:
    configs:
      default:
        registerHealthIndicator: true
        slidingWindowSize: 10
        minimumNumberOfCalls: 5
        failureRateThreshold: 50
        waitDurationInOpenState: 10s
    instances:
      paymentService:
        baseConfig: default
```

参考 @references/configuration-reference.md 获取完整的熔断器配置选项。

### 3. 重试模式

使用 `@Retry` 注解处理瞬时故障：

```java
@Service
public class ProductService {
    private final RestTemplate restTemplate;

    public ProductService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    @Retry(name = "productService", fallbackMethod = "getProductFallback")
    public Product getProduct(Long productId) {
        return restTemplate.getForObject(
            "http://product-api/products/" + productId,
            Product.class);
    }

    private Product getProductFallback(Long productId, Exception ex) {
        return Product.builder()
            .id(productId)
            .name("不可用")
            .available(false)
            .build();
    }
}
```

在 `application.yml` 中配置重试：

```yaml
resilience4j:
  retry:
    configs:
      default:
        maxAttempts: 3
        waitDuration: 500ms
        enableExponentialBackoff: true
        exponentialBackoffMultiplier: 2
    instances:
      productService:
        baseConfig: default
        maxAttempts: 5
```

参考 @references/configuration-reference.md 获取重试异常配置。

### 4. 速率限制模式

使用 `@RateLimiter` 控制请求速率：

```java
@Service
public class NotificationService {
    private final EmailClient emailClient;

    public NotificationService(EmailClient emailClient) {
        this.emailClient = emailClient;
    }

    @RateLimiter(name = "notificationService",
        fallbackMethod = "rateLimitFallback")
    public void sendEmail(EmailRequest request) {
        emailClient.send(request);
    }

    private void rateLimitFallback(EmailRequest request, Exception ex) {
        throw new RateLimitExceededException(
            "请求过多。请稍后再试。");
    }
}
```

在 `application.yml` 中配置：

```yaml
resilience4j:
  ratelimiter:
    configs:
      default:
        registerHealthIndicator: true
        limitForPeriod: 10
        limitRefreshPeriod: 1s
        timeoutDuration: 500ms
    instances:
      notificationService:
        baseConfig: default
        limitForPeriod: 5
```

### 5. 限流器模式

使用 `@Bulkhead` 隔离资源。同步方法使用 `type = SEMAPHORE`：

```java
@Service
public class ReportService {
    private final ReportGenerator reportGenerator;

    public ReportService(ReportGenerator reportGenerator) {
        this.reportGenerator = reportGenerator;
    }

    @Bulkhead(name = "reportService", type = Bulkhead.Type.SEMAPHORE)
    public Report generateReport(ReportRequest request) {
        return reportGenerator.generate(request);
    }
}
```

异步/CompletableFuture 方法使用 `type = THREADPOOL`：

```java
@Service
public class AnalyticsService {
    @Bulkhead(name = "analyticsService", type = Bulkhead.Type.THREADPOOL)
    public CompletableFuture<AnalyticsResult> runAnalytics(
            AnalyticsRequest request) {
        return CompletableFuture.supplyAsync(() ->
            analyticsEngine.analyze(request));
    }
}
```

在 `application.yml` 中配置：

```yaml
resilience4j:
  bulkhead:
    configs:
      default:
        maxConcurrentCalls: 10
        maxWaitDuration: 100ms
    instances:
      reportService:
        baseConfig: default
        maxConcurrentCalls: 5

  thread-pool-bulkhead:
    instances:
      analyticsService:
        maxThreadPoolSize: 8
```

### 6. 时间限制模式

使用 `@TimeLimiter` 对异步方法强制执行超时边界：

```java
@Service
public class SearchService {
    @TimeLimiter(name = "searchService", fallbackMethod = "searchFallback")
    public CompletableFuture<SearchResults> search(SearchQuery query) {
        return CompletableFuture.supplyAsync(() ->
            searchEngine.executeSearch(query));
    }

    private CompletableFuture<SearchResults> searchFallback(
            SearchQuery query, Exception ex) {
        return CompletableFuture.completedFuture(
            SearchResults.empty("搜索超时"));
    }
}
```

在 `application.yml` 中配置：

```yaml
resilience4j:
  timelimiter:
    configs:
      default:
        timeoutDuration: 2s
        cancelRunningFuture: true
    instances:
      searchService:
        baseConfig: default
        timeoutDuration: 3s
```

### 7. 组合多种模式

在单个方法上堆叠多种模式实现全面容错：

```java
@Service
public class OrderService {
    @CircuitBreaker(name = "orderService")
    @Retry(name = "orderService")
    @RateLimiter(name = "orderService")
    @Bulkhead(name = "orderService")
    public Order createOrder(OrderRequest request) {
        return orderClient.createOrder(request);
    }
}
```

执行顺序：重试 → 熔断器 → 速率限制器 → 限流器 → 方法

所有模式应引用相同命名的配置实例以保持一致性。

### 8. 异常处理和监控

使用 `@RestControllerAdvice` 创建全局异常处理器：

```java
@RestControllerAdvice
public class ResilienceExceptionHandler {

    @ExceptionHandler(CallNotPermittedException.class)
    @ResponseStatus(HttpStatus.SERVICE_UNAVAILABLE)
    public ErrorResponse handleCircuitOpen(CallNotPermittedException ex) {
        return new ErrorResponse("SERVICE_UNAVAILABLE",
            "服务当前不可用");
    }

    @ExceptionHandler(RequestNotPermitted.class)
    @ResponseStatus(HttpStatus.TOO_MANY_REQUESTS)
    public ErrorResponse handleRateLimited(RequestNotPermitted ex) {
        return new ErrorResponse("TOO_MANY_REQUESTS",
            "速率限制超出");
    }

    @ExceptionHandler(BulkheadFullException.class)
    @ResponseStatus(HttpStatus.SERVICE_UNAVAILABLE)
    public ErrorResponse handleBulkheadFull(BulkheadFullException ex) {
        return new ErrorResponse("CAPACITY_EXCEEDED",
            "服务已满载");
    }
}
```

在 `application.yml` 中启用 Actuator 端点监控容错模式：

```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,metrics,circuitbreakers,retries,ratelimiters
  endpoint:
    health:
      show-details: always
  health:
    circuitbreakers:
      enabled: true
    ratelimiters:
      enabled: true
```

访问监控端点：
- `GET /actuator/health` - 包含容错模式的整体健康状态
- `GET /actuator/circuitbreakers` - 熔断器状态
- `GET /actuator/metrics` - 自定义容错指标

### 测试和验证工作流

1. **熔断器**：调用失败端点 → 检查 `GET /actuator/circuitbreakers` 显示 `OPEN` → 等待 `waitDurationInOpenState` → 验证状态过渡到 `HALF_OPEN` → `CLOSED`

2. **重试**：启用 `resilience4j.retry.metrics.enabled: true` → 调用端点 → 验证 `retry.{instance}.successful-calls-with-retry-attempts` 指标增加

3. **速率限制**：发送超过 `limitForPeriod` 的请求 → 验证 429 状态 → 检查 `GET /actuator/ratelimiters` 显示 `LIMITED`

4. **限流器**：并发请求超过 `maxConcurrentCalls` 进行压力测试 → 验证超额请求立即失败并抛出 `BulkheadFullException`

5. **时间限制**：模拟超过 `timeoutDuration` 的异步延迟 → 验证超时后触发降级

参考 @references/testing-patterns.md 获取单元和集成测试策略。

## 最佳实践

- **提供降级方法**：确保优雅降级并提供有意义的响应
- **使用指数退避**：防止压垮恢复中的服务（`exponentialBackoffMultiplier: 2`）
- **设置适当阈值**：`failureRateThreshold` 在 50-70% 之间
- **使用构造器注入**：Resilience4j 依赖绝不能使用字段注入
- **启用健康指标**：所有模式设置 `registerHealthIndicator: true`
- **仅重试瞬时错误**：网络超时、5xx；跳过 4xx 和业务异常
- **根据负载调整限流器**：根据预期并发计算线程池和信号量大小
- **记录降级行为**：使降级逻辑清晰可预测

## 限制和警告

- 降级方法必须具有相同签名并可选添加异常参数
- 熔断器状态是实例级别的；多租户场景中确保正确的 Bean 作用域
- 重试操作必须是幂等的（可能执行多次）
- 不要使用熔断器处理必须完成的操作；使用超时替代
- 速率限制器可能导致线程阻塞；配置适当的等待时长
- 谨慎使用 `@Retry` 在非幂等操作上，如 POST 请求
- 使用线程池限流器高并发时注意内存使用

## 示例

### 熔断器：前 → 后

```java
// 前：无保护
public PaymentResponse processPayment(PaymentRequest request) {
    return restTemplate.postForObject("http://payment-api/process", request, PaymentResponse.class);
}

// 后：带降级的熔断器
@CircuitBreaker(name = "paymentService", fallbackMethod = "paymentFallback")
public PaymentResponse processPayment(PaymentRequest request) {
    return restTemplate.postForObject("http://payment-api/process", request, PaymentResponse.class);
}
private PaymentResponse paymentFallback(PaymentRequest request, Exception ex) {
    return PaymentResponse.builder().status("PENDING").message("服务暂时不可用").build();
}
```

### 重试带退避：前 → 后

```java
// 前：单次尝试
public Order getOrder(Long orderId) {
    return orderRepository.findById(orderId).orElseThrow(() -> new OrderNotFoundException(orderId));
}

// 后：带指数退避的重试
@Retry(name = "orderService", maxAttempts = 3, waitDuration = @WaitDuration(500L), fallbackMethod = "getOrderFallback")
public Order getOrder(Long orderId) {
    return orderRepository.findById(orderId).orElseThrow(() -> new OrderNotFoundException(orderId));
}
private Order getOrderFallback(Long orderId, Exception ex) { return Order.cachedOrder(orderId); }
```

### 速率限制：前 → 后

```java
// 前：无限制请求
@GetMapping("/api/data") public Data fetchData() { return dataService.process(); }

// 后：带速率限制
@RateLimiter(name = "dataService", fallbackMethod = "rateLimitFallback")
@GetMapping("/api/data") public Data fetchData() { return dataService.process(); }
private ResponseEntity<ErrorResponse> rateLimitFallback(Exception ex) {
    return ResponseEntity.status(429).body(new ErrorResponse("TOO_MANY_REQUESTS", "速率限制超出"));
}
```

**另见**：[配置参考](references/configuration-reference.md) · [测试模式](references/testing-patterns.md) · [示例](references/examples.md) · [Resilience4j 文档](https://resilience4j.readme.io/) · [Actuator 技能](../spring-boot-actuator/SKILL.md)
