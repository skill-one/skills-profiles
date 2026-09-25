# EDOT Java 代理

在做出更改之前，请阅读设置指南：

- [EDOT Java 设置](https://www.elastic.co/docs/reference/opentelemetry/edot-sdks/java/setup)
- [OpenTelemetry Java 代理](https://opentelemetry.io/docs/zero-code/java/agent/)
- [EDOT Java 配置](https://www.elastic.co/docs/reference/opentelemetry/edot-sdks/java/configuration)

## 指南

1. 使用 `elastic-otel-javaagent.jar`（从
   [Maven Central](https://mvnrepository.com/artifact/co.elastic.otel/elastic-otel-javaagent/latest) 下载，而不是 Maven/Gradle
   编译依赖）
1. 通过 `-javaagent:/path/to/elastic-otel-javaagent.jar` 或
   `JAVA_TOOL_OPTIONS="-javaagent:/path/to/elastic-otel-javaagent.jar"` 连接 — 如果没有这样做，代理将不会起作用
1. 设置恰好三个必需的环境变量：
   - `OTEL_SERVICE_NAME`
   - `OTEL_EXPORTER_OTLP_ENDPOINT` — 必须是 **管理的 OTLP 端点** 或 **EDOT 收集器** URL。切勿使用 APM
     服务器 URL（没有 `apm-server`，没有 `:8200`，没有 `/intake/v2/events`）
   - `OTEL_EXPORTER_OTLP_HEADERS` — `"Authorization=ApiKey <key>"` 或 `"Authorization=Bearer <token>"`
1. 请勿设置 `OTEL_TRACES_EXPORTER`、`OTEL_METRICS_EXPORTER` 或 `OTEL_LOGS_EXPORTER` — 默认值已经是正确的
1. 在同一 JVM 上切勿同时运行经典 Elastic APM 代理和 EDOT 代理

## 示例

请参阅 [EDOT Java 设置指南](https://www.elastic.co/docs/reference/opentelemetry/edot-sdks/java/setup) 获取完整的 Dockerfile 和 docker-compose 示例。
