# 单元测试 `@Scheduled` 和 `@Async` 方法

## 概述

使用 JUnit 5 对 Spring 的 `@Scheduled` 和 `@Async` 方法进行单元测试的模式。测试 `CompletableFuture` 结果，使用 Awaitility 处理竞态条件，模拟计划任务执行，并验证错误处理——无需等待实际调度间隔。

## 使用场景

- 测试 `@Scheduled` 方法逻辑
- 测试 `@Async` 方法行为
- 验证 `CompletableFuture` 结果
- 测试异步错误处理
- 测试 cron 表达式逻辑而无需等待实际调度
- 验证线程池行为和执行次数
- 独立测试后台任务逻辑

## 指导步骤

1. **直接调用 `@Async` 方法**——绕过 Spring 的异步代理；在单元测试中注解无关紧要
2. **使用 `@Mock` 和 `@InjectMocks` 模拟依赖**（Mockito）
3. **等待完成**——使用 `CompletableFuture.get(timeout, unit)` 或 `await().atMost(...).untilAsserted(...)` 
4. **直接调用 `@Scheduled` 方法**——无需等待 cron/fixedRate；在单元测试中注解被忽略
5. **测试异常路径**——验证 `CompletableFuture.get()` 上的 `ExecutionException` 包装

**验证检查点：**
- 在 `CompletableFuture.get()` 后，断言返回值再验证模拟交互
- 如果抛出 `ExecutionException`，检查 `.getCause()` 以识别根本异常
- 如果 Awaitility 超时，增加 `atMost()` 持续时间或减少 `pollInterval()` 直到条件可达
- 在多次任务调用后，在 `verify()` 调用前断言执行次数

## 示例

关键模式——完整示例在 `references/examples.md` 中：

```java
// @Async: 直接调用，使用 CompletableFuture.get(timeout, unit) 等待
@Service
class EmailService {
  @Async
  public CompletableFuture<Boolean> sendEmailAsync(String to) {
    return CompletableFuture.supplyAsync(() -> true);
  }
}
@Test
void shouldReturnCompletedFuture() throws Exception {
  EmailService service = new EmailService();
  Boolean result = service.sendEmailAsync("test@example.com").get(5, TimeUnit.SECONDS);
  assertThat(result).isTrue();
}

// @Scheduled: 直接调用，模拟仓库
@Component
class DataRefreshTask {
  @InjectMocks private DataRepository dataRepository;
  @Scheduled(fixedDelay = 60000) public void refreshCache() { /* ... */ }
}
@Test
void shouldRefreshCache() {
  when(dataRepository.findAll()).thenReturn(List.of(new Data(1L, "item1")));
  dataRefreshTask.refreshCache();
  verify(dataRepository).findAll();
}

// Awaitility: 用于共享可变状态的竞态条件
@Test
void shouldProcessAllItems() {
  BackgroundWorker worker = new BackgroundWorker();
  worker.processItems(List.of("item1", "item2", "item3"));
  Awaitility.await()
    .atMost(Duration.ofSeconds(5))
    .pollInterval(Duration.ofMillis(100))
    .untilAsserted(() -> assertThat(worker.getProcessedCount()).isEqualTo(3));
}

// 模拟依赖和异常处理
@Test
void shouldHandleAsyncExceptionGracefully() {
  doThrow(new RuntimeException("Email failed")).when(emailService).send(any());
  CompletableFuture<String> result = service.notifyUserAsync("user123");
  assertThatThrownBy(result::get)
    .isInstanceOf(ExecutionException.class)
    .hasCauseInstanceOf(RuntimeException.class);
}
```

完整的 Maven/Gradle 依赖项、附加测试类和执行次数模式：见 `references/examples.md`。

## 最佳实践

- 始终在 `CompletableFuture.get()` 上设置**超时**以防止测试挂起
- **模拟所有依赖**——在单元测试中永不调用真实的外部服务
- 仅在处理竞态条件时使用 **Awaitility**；对于简单的异步方法优先直接调用
- 直接测试 `@Scheduled` **逻辑**——在单元测试中注解被忽略
- 在验证模拟交互前断言值；异步完成后**再**验证

## 常见陷阱

- 依赖 Spring 的异步执行器而不是直接调用方法
- `CompletableFuture.get()` 缺少超时
- 忘记测试异步方法中的异常传播
- 未模拟异步方法内部调用的依赖
- 等待实际 cron/fixedRate 时间而不是隔离测试逻辑

## 限制和警告

- **`@Async` 自调用**：在同一个类中从另一个方法调用 `@Async` 执行同步——Spring 代理被绕过
- **线程池排序**：`ThreadPoolTaskScheduler` 不保证执行顺序
- **CompletableFuture 链接**：中间阶段的异常可能被静默丢失——测试每个阶段
- **Awaitility 超时**：始终设置合理的 `atMost()`；无限等待挂起测试套件
- **无实际调度**：`@Scheduled` 在单元测试中被忽略——直接调用方法

## 参考

- [Spring `@Async` 文档](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/scheduling/annotation/Async.html)
- [Spring `@Scheduled` 文档](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/scheduling/annotation/Scheduled.html)
- [Awaitility 测试库](https://github.com/awaitility/awaitility)
- [CompletableFuture API](https://docs.oracle.com/javase/8/docs/api/java/util/concurrent/CompletableFuture.html)
- 代码示例：`references/examples.md`
