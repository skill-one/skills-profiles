# EDOT Java 迁移

在做出更改之前，请阅读迁移指南：

- [迁移指南](https://www.elastic.co/docs/reference/opentelemetry/edot-sdks/java/migration)
- [EDOT Java 安装](https://www.elastic.co/docs/reference/opentelemetry/edot-sdks/java/setup)
- [EDOT Java 配置](https://www.elastic.co/docs/reference/opentelemetry/edot-sdks/java/configuration)

## 指南

1. 删除所有经典 APM 引用：`elastic-apm-agent.jar`、`elasticapm.properties`、所有 `ELASTIC_APM_*` 环境变量，以及任何 `co.elastic.apm` Maven/Gradle 依赖项
1. 使用 `elastic-otel-javaagent.jar`（从 [Maven Central](https://mvnrepository.com/artifact/co.elastic.otel/elastic-otel-javaagent/latest) 下载，不是 Maven/Gradle 编译依赖）
1. 通过 `-javaagent:/path/to/elastic-otel-javaagent.jar` 或 `JAVA_TOOL_OPTIONS="-javaagent:/path/to/elastic-otel-javaagent.jar"`附加——如果没有这个，代理将不会执行任何操作
1. 设置恰好三个必需的环境变量：
   - `OTEL_SERVICE_NAME`（替换 `ELASTIC_APM_SERVICE_NAME`）
   - `OTEL_EXPORTER_OTLP_ENDPOINT`——必须是**管理的 OTLP 端点**或**EDOT 收集器**的 URL。不要重用旧的 `ELASTIC_APM_SERVER_URL` 值。永远不要使用 APM Server URL（没有 `apm-server`，没有 `:8200`，没有 `/intake/v2/events`）
   - `OTEL_EXPORTER_OTLP_HEADERS`——`"Authorization=ApiKey <key>"`或`"Authorization=Bearer <token>"`（替换 `ELASTIC_APM_SECRET_TOKEN` / `API_KEY`）
1. 不要设置 `OTEL_TRACES_EXPORTER`、`OTEL_METRICS_EXPORTER` 或 `OTEL_LOGS_EXPORTER`——默认值已经是正确的
1. 在同一个 JVM 上永远不要同时运行经典 Elastic APM 代理和 EDOT 代理

## 示例

请参阅 [EDOT Java 迁移指南](https://www.elastic.co/docs/reference/opentelemetry/edot-sdks/java/migration) 获取完整示例。
