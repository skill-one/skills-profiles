# Spring Boot 缓存抽象

## 概述

Spring Boot 3.5+ 应用中启用缓存抽象的 6 步工作流，包括配置提供者（Caffeine、Redis、Ehcache）、注解服务方法以及验证行为。对读取操作应用 `@Cacheable`，对写入操作应用 `@CachePut`，对删除操作应用 `@CacheEvict`。配置 TTL/驱逐策略，并通过 Actuator 暴露指标。

## 何时使用

- 将 `@Cacheable`、`@CachePut` 或 `@CacheEvict` 添加到服务方法。
- 配置 Caffeine、Redis 或 Ehcache，并设置 TTL 和容量策略。
- 实现过期数据驱逐策略。
- 诊断缓存未命中或失效问题。
- 通过 Actuator 或 Micrometer 暴露命中/未命中指标。

## 说明

1. **添加依赖** — `spring-boot-starter-cache` 加上提供者：
   - Caffeine：`caffeine` 启动器
   - Redis：`spring-boot-starter-data-redis`
   - Ehcache：`ehcache` 启动器

2. **启用缓存** — 使用 `@EnableCaching` 注解 `@Configuration` 类，并定义 `CacheManager` Bean。

3. **注解方法** — 读取操作使用 `@Cacheable`，写入操作使用 `@CachePut`，删除操作使用 `@CacheEvict`。

4. **配置 TTL/驱逐** — 设置 `spring.cache.caffeine.spec`、`spring.cache.redis.time-to-live` 或 `spring.cache.ehcache.config`。

5. **构建键** — 在 `key` 属性中使用 SpEL；使用 `condition`/`unless` 进行选择性缓存。

6. **验证配置** — 运行集成测试以确认第二次调用时缓存命中；检查 `GET /actuator/caches` 以验证缓存管理器注册；查询 `GET /actuator/metrics/cache.gets` 获取命中/未命中比率。

## 示例

### 示例 1：基本 `@Cacheable` 使用

```java
@Service
@CacheConfig(cacheNames = "users")
class UserService {

    @Cacheable(key = "#id", unless = "#result == null")
    User findUser(Long id) { ... }
}
```

```
第一次调用 → 缓存未命中，调用仓库
第二次调用 → 缓存命中，跳过仓库
```

### 示例 2：使用 SpEL 的条件缓存

```java
@Cacheable(value = "products", key = "#id", condition = "#price > 100")
public Product getProduct(Long id, BigDecimal price) { ... }

// 仅缓存高价值产品
```

### 示例 3：缓存驱逐

```java
@CacheEvict(value = "users", key = "#id")
public void deleteUser(Long id) { ... }
```

对于渐进式场景（基本产品缓存、多级驱逐、Redis 集成），加载 [`references/cache-examples.md`](references/cache-examples.md)。

## 高级选项

- 使用 JCache 注解（`@CacheResult`、`@CacheRemove`）以支持 JSR-107 互操作性；避免在同一方法上混合 Spring 注解。
- 缓存反应式返回类型（`Mono`、`Flux`）或 `CompletableFuture` 值。
- 在通过 REST 暴露缓存响应时应用 HTTP `CacheControl` 头。
- 使用 `@Scheduled` 定期驱逐时间限制缓存。
- 创建 `CacheManagementService` 以编程方式调用 `cacheManager.getCache(name)`。

## 故障排除

在添加 `@Cacheable` 后如果缓存未命中仍然存在：

1. 验证 `@EnableCaching` 是否存在于 `@Configuration` 类上。
2. 确认方法是公共的，并且从类外部调用（Spring 使用代理；自我调用会绕过缓存）。
3. 验证 SpEL 键表达式是否正确解析。
4. 确认缓存管理器 Bean 是否注册为 `cacheManager` 或通过 `cacheManager = "myCacheManager"` 明确引用。

## 参考

- [`references/spring-framework-cache-docs.md`](references/spring-framework-cache-docs.md):
  Spring Framework Reference Guide 的精选摘录。
- [`references/spring-cache-doc-snippet.md`](references/spring-cache-doc-snippet.md):
  Spring 文档中的叙述性概述。
- [`references/cache-core-reference.md`](references/cache-core-reference.md):
  注解参数、依赖矩阵、属性目录。
- [`references/cache-examples.md`](references/cache-examples.md):
  带测试的端到端示例。

## 最佳实践

- 优先使用构造器注入和不可变 DTO 作为缓存条目。
- 按聚合（`users`、`orders`）分离缓存名称，简化驱逐操作。
- 仅在调试级别记录缓存命中/未命中；通过 Micrometer 推送指标。
- 根据数据过期容忍度调整 TTL；在代码中记录理由。
- 对存储 PII 或凭证的缓存进行加密或避免缓存。
- 将缓存驱逐与事务边界对齐，防止脏读。

## 限制和警告

- 避免缓存依赖开放持久化上下文的可变实体。
- 不要在同一方法上混合 Spring 缓存注解和 JCache 注解。
- 缓存跨服务实例时验证序列化兼容性。
- 监控内存占用，防止内存存储的 OOM。
- Caffeine + Redis 多级缓存需要发布/订阅失效通道。

## 相关技能

- [`../spring-boot-rest-api-standards`](../spring-boot-rest-api-standards/SKILL.md)
- [`../spring-boot-test-patterns`](../spring-boot-test-patterns/SKILL.md)
- [`../unit-test-caching`](../unit-test-caching/SKILL.md)
