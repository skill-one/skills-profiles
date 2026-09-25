# EDOT .NET 迁移

在做出更改之前，请阅读迁移指南：

- [迁移指南](https://www.elastic.co/docs/reference/opentelemetry/edot-sdks/dotnet/migration)
- [EDOT .NET 安装](https://www.elastic.co/docs/reference/opentelemetry/edot-sdks/dotnet/setup)
- [EDOT .NET 配置](https://www.elastic.co/docs/reference/opentelemetry/edot-sdks/dotnet/configuration)

## 指南

1. 移除所有经典 APM 引用：`Elastic.Apm.*` NuGet 包（包括 `Elastic.Apm.NetCoreAll`）、`UseAllElasticApm()` / `AddAllElasticApm()` 调用、`appsettings.json` 中的 `ElasticApm` 部分，以及所有 `ELASTIC_APM_*` 环境变量
1. 添加 NuGet 包：`Elastic.OpenTelemetry` 和 `OpenTelemetry.Instrumentation.AspNetCore`（用于 ASP.NET Core 应用）
1. 在启动中注册 EDOT：在 `IHostApplicationBuilder` 上调用 `builder.AddElasticOpenTelemetry()`（在 `Program.cs` 或等效文件中）。没有这一步，将不会收集任何遥测数据
1. 设置三个必需的环境变量：
   - `OTEL_SERVICE_NAME`（替换 `ELASTIC_APM_SERVICE_NAME` / `ElasticApm:ServiceName`）
   - `OTEL_EXPORTER_OTLP_ENDPOINT` — 必须是 **管理的 OTLP 端点** 或 **EDOT 收集器** URL。不要重用旧的 `ELASTIC_APM_SERVER_URLS` 值。永远不要使用 APM 服务器 URL（没有 `apm-server`，没有 `:8200`，没有 `/intake/v2/events`）
   - `OTEL_EXPORTER_OTLP_HEADERS` — `"Authorization=ApiKey <key>"` 或 `"Authorization=Bearer <token>"`（替换 `ELASTIC_APM_SECRET_TOKEN`）
1. 不要设置 `OTEL_TRACES_EXPORTER`、`OTEL_METRICS_EXPORTER` 或 `OTEL_LOGS_EXPORTER` — 默认值已经是正确的
1. 在同一应用程序上永远不要同时运行经典 Elastic APM 代理 (`Elastic.Apm.*`) 和 EDOT

## 示例

请参阅 [EDOT .NET 迁移指南](https://www.elastic.co/docs/reference/opentelemetry/edot-sdks/dotnet/migration) 获取完整示例。
