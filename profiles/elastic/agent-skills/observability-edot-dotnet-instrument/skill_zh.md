# EDOT .NET 仪器化

在做出更改之前，请阅读设置指南：

- [EDOT .NET 设置](https://www.elastic.co/docs/reference/opentelemetry/edot-sdks/dotnet/setup)
- [EDOT .NET 配置](https://www.elastic.co/docs/reference/opentelemetry/edot-sdks/dotnet/configuration)
- [OpenTelemetry .NET 仪器化](https://opentelemetry.io/docs/zero-code/net/)

## 指南

1. 添加 NuGet 包：`Elastic.OpenTelemetry` 和 `OpenTelemetry.Instrumentation.AspNetCore`（用于 ASP.NET Core 应用）
1. 在启动时注册 EDOT：在 `IHostApplicationBuilder` 上调用 `builder.AddElasticOpenTelemetry()`（在 `Program.cs`
   或等效文件中）。如果没有这样做，将不会收集任何遥测数据
1. 设置恰好三个必需的环境变量：
   - `OTEL_SERVICE_NAME`
   - `OTEL_EXPORTER_OTLP_ENDPOINT` — 必须是 **管理的 OTLP 端点** 或 **EDOT 收集器** URL。切勿使用 APM
     服务器 URL（没有 `apm-server`，没有 `:8200`，没有 `/intake/v2/events`）
   - `OTEL_EXPORTER_OTLP_HEADERS` — `"Authorization=ApiKey <key>"` 或 `"Authorization=Bearer <token>"`
1. 不要设置 `OTEL_TRACES_EXPORTER`、`OTEL_METRICS_EXPORTER` 或 `OTEL_LOGS_EXPORTER` — 默认值已经是正确的
1. 不要手动配置 `TracerProvider` 或 `MeterProvider` — `AddElasticOpenTelemetry()` 处理所有内容
1. 在同一应用程序上切勿同时运行经典 Elastic APM 代理 (`Elastic.Apm.*`) 和 EDOT

## 示例

请参阅 [EDOT .NET 设置指南](https://www.elastic.co/docs/reference/opentelemetry/edot-sdks/dotnet/setup) 获取完整示例。
