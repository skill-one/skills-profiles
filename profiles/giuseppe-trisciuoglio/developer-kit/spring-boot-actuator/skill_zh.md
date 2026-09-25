# Spring Boot Actuator 技能

## 概述
- 使用 Actuator 端点、探针和 Micrometer 集成，为 Spring Boot 服务提供生产就绪的观测能力。
- 标准化健康、指标和诊断配置，并将深度参考材料委托给 `references/`。
- 支持平台对安全操作、SLO 报告和事件诊断的要求。

## 何时使用
- 触发器：`启用 actuator 端点` – 为新创建或现有的 Spring Boot 服务启动 Actuator。
- 触发器：`安全管理端口` – 应用 Spring Security 策略来保护管理流量。
- 触发器：`配置健康探针` – 为编排器定义就绪和存活组。
- 触发器：`将指标导出到 prometheus` – 连接 Micrometer 注册表并调整指标暴露。
- 触发器：`调试 actuator 启动` – 在端点缺失或响应缓慢时检查条件评估和启动指标。

## 快速入门
```xml
<!-- Maven -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-actuator</artifactId>
</dependency>
```
```gradle
// Gradle
dependencies {
    implementation "org.springframework.boot:spring-boot-starter-actuator"
}
```
添加依赖项后，验证端点是否响应：
```bash
curl http://localhost:8080/actuator/health
curl http://localhost:8080/actuator/info
```

## 说明

### 1. 添加 Actuator 依赖项
在构建配置中包含 `spring-boot-starter-actuator`。
> **验证**：重启服务并确认 `/actuator/health` 和 `/actuator/info` 返回 `200 OK`。

### 2. 暴露所需端点
- 将 `management.endpoints.web.exposure.include` 设置为精确列表或 `"*"` 用于内部部署。
- 当默认的 `/actuator` 与路由冲突时，调整 `management.endpoints.web.base-path`（例如 `/management`）。
- 查看 `references/endpoint-reference.md` 中的详细端点语义。
> **验证**：`curl http://localhost:8080/actuator` 返回暴露的端点列表。

### 3. 保障管理流量安全
- 使用 `EndpointRequest.toAnyEndpoint()` 和基于角色的规则应用隔离的 `SecurityFilterChain`。
- 将 `management.server.port` 与防火墙控制或服务网格策略结合，仅供操作员访问。
- 仅在需要时将 `/actuator/health/**` 公开；否则强制执行身份验证。
> **验证**：对受保护端点的未身份验证请求返回 `401 Unauthorized`。

### 4. 配置健康探针
- 启用 `management.endpoint.health.probes.enabled=true` 用于 `/health/liveness` 和 `/health/readiness`。
- 通过 `management.endpoint.health.group.*` 分组指标以匹配平台预期。
- 通过扩展 `HealthIndicator` 或 `ReactiveHealthContributor` 实现自定义指标；示例实现见 `references/examples.md#custom-health-indicator`。
> **验证**：在提升到生产环境前，`/actuator/health/readiness` 返回 `UP` 并包含所有必需组件。

### 5. 发布指标和跟踪
- 通过 `management.metrics.export.*` 激活 Micrometer 导出器（Prometheus、OTLP、Wavefront、StatsD）。
- 应用 `MeterRegistryCustomizer` 豆以添加 `application`、`environment` 和业务标签用于可观察性关联。
- 使用 Spring Boot 3.2+ 时，通过 `server.observation.*` 配置暴露 HTTP 请求指标。
> **验证**：抓取 `/actuator/prometheus` 并确认所需指标（`http.server.requests`、`jvm.memory.used`）存在。

### 6. 启用诊断工具
- 在事件响应期间启用 `/actuator/startup`（Spring Boot 3.5+）和 `/actuator/conditions` 检查自动配置决策。
- 在启用 `/actuator/httpexchanges` 前注册 `HttpExchangeRepository`（例如 `InMemoryHttpExchangeRepository`）进行请求审计。
- 参考 `references/endpoint-reference.md` 了解端点行为和限制。
> **验证**：`/actuator/startup` 和 `/actuator/conditions` 返回有效的 JSON 负载。

## 示例

### 基础示例 – 安全暴露健康和 info
```yaml
management:
  endpoints:
    web:
      exposure:
        include: "health,info"
  endpoint:
    health:
      show-details: never
```

### 中级示例 – 带自定义指标的就绪组
```java
@Component
public class PaymentsGatewayHealth implements HealthIndicator {

    private final PaymentsClient client;

    public PaymentsGatewayHealth(PaymentsClient client) {
        this.client = client;
    }

    @Override
    public Health health() {
        boolean reachable = client.ping();
        return reachable ? Health.up().withDetail("latencyMs", client.latency()).build()
                         : Health.down().withDetail("error", "Gateway timeout").build();
    }
}
```
```yaml
management:
  endpoint:
    health:
      probes:
        enabled: true
      group:
        readiness:
          include: "readinessState,db,paymentsGateway"
          show-details: always
```

### 高级示例 – 专用管理端口与 Prometheus 导出
```yaml
management:
  server:
    port: 9091
    ssl:
      enabled: true
  endpoints:
    web:
      exposure:
        include: "health,info,metrics,prometheus"
      base-path: "/management"
  metrics:
    export:
      prometheus:
        descriptions: true
        step: 30s
  endpoint:
    health:
      show-details: when-authorized
      roles: "ENDPOINT_ADMIN"
```
```java
@Configuration
public class ActuatorSecurityConfig {

    @Bean
    SecurityFilterChain actuatorChain(HttpSecurity http) throws Exception {
        http.securityMatcher(EndpointRequest.toAnyEndpoint())
            .authorizeHttpRequests(c -> c
                .requestMatchers(EndpointRequest.to("health")).permitAll()
                .anyRequest().hasRole("ENDPOINT_ADMIN"))
            .httpBasic(Customizer.withDefaults());
        return http.build();
    }
}
```
更多端到端示例见 `references/examples.md`。

## 最佳实践
- 保持 `SKILL.md` 简洁，依赖 `references/` 进行冗长文档以节省上下文。
- 应用最小权限原则：仅暴露所需端点并限制敏感端点。
- 通过特定于配置文件的 YAML 使用不可变配置以对齐环境。
- 单独监控 actuator 流量以检测抓取滥用或暴力破解尝试。
- 通过在 CI/CD 管道中脚本化 `curl` 探针来自动化回归检查。

## 限制和警告
- 避免在公共网络上暴露 `/actuator/env`、`/actuator/configprops`、`/actuator/logfile` 和 `/actuator/heapdump`。
- 除非绝对必要，否则不要发布会阻塞事件循环线程或超过 250 ms 的自定义健康指标。
- 确保Actuator指标导出器在支持的 Micrometer 注册表中运行；不支持的导出器需要自定义注册表豆。
- 保持与 Spring Boot 3.5.x 约定的兼容性；旧版本可能缺少探针和观测功能。
- 生产环境中切勿在未身份验证的情况下暴露 actuator 端点。
- 健康指标不应执行可能影响应用性能的昂贵操作。
- 对 `/actuator/beans` 和 `/actuator/mappings` 要谨慎，因为它们会暴露内部应用结构。

## 参考材料
- [端点快速参考](references/endpoint-reference.md)
- [实现示例](references/examples.md)
- [官方文档摘录](references/endpoint-reference.md)
- [使用 Actuator 进行审计](references/auditing.md)
- [Cloud Foundry 集成](references/cloud-foundry.md)
- [启用 Actuator 功能](references/enabling.md)
- [HTTP 请求记录](references/http-exchanges.md)
- [JMX 暴露](references/jmx.md)
- [监控和指标](references/monitoring.md)
- [日志配置](references/loggers.md)
- [指标导出器](references/metrics.md)
- [使用 Micrometer 的可观察性](references/observability.md)
- [进程和监控](references/process-monitoring.md)
- [跟踪](references/tracing.md)
- 脚本目录 (`scripts/`) 预留用于未来自动化；目前无运行时依赖。

## 验证清单
- 确认 `mvn spring-boot:run` 或 `./gradlew bootRun` 在 `/actuator`（或自定义基本路径）下暴露预期端点。
- 验证在提升到生产环境前，`/actuator/health/readiness` 返回 `UP` 并包含所有必需组件。
- 抓取 `/actuator/metrics` 或 `/actuator/prometheus` 确认所需指标（`http.server.requests`、`jvm.memory.used`）存在。
- 运行安全扫描以验证仅从可信网络外部可访问预期端口和端点。
