# EDOT Python 代理

在做出更改之前，请阅读设置指南：

- [EDOT Python 设置](https://www.elastic.co/docs/reference/opentelemetry/edot-sdks/python/setup)
- [EDOT Python 配置](https://www.elastic.co/docs/reference/opentelemetry/edot-sdks/python/configuration)
- [OpenTelemetry Python 自动代理](https://opentelemetry.io/docs/zero-code/python/)

## 指南

1. 通过 pip 安装 `elastic-opentelemetry`（添加到 `requirements.txt` 或等效文件）
1. 在镜像构建期间运行 `edot-bootstrap --action=install` 以安装检测到的库的自动代理包
1. 用 `opentelemetry-instrument` 包裹应用程序入口点 — 例如 `opentelemetry-instrument gunicorn app:app` 或 `opentelemetry-instrument python app.py`。没有这个步骤，将不会收集任何遥测数据
1. 设置恰好三个必需的环境变量：
   - `OTEL_SERVICE_NAME`
   - `OTEL_EXPORTER_OTLP_ENDPOINT` — 必须是**管理的 OTLP 端点**或**EDOT 收集器**的 URL。绝对不要使用 APM 服务器 URL（没有 `apm-server`，没有 `:8200`，没有 `/intake/v2/events`）
   - `OTEL_EXPORTER_OTLP_HEADERS` — `"Authorization=ApiKey <key>"` 或 `"Authorization=Bearer <token>"`
1. 不要设置 `OTEL_TRACES_EXPORTER`、`OTEL_METRICS_EXPORTER` 或 `OTEL_LOGS_EXPORTER` — 默认值已经是正确的
1. 不要添加代码级别的 SDK 设置（没有 `TracerProvider`，没有 `configure_azure_monitor` 等）— `opentelemetry-instrument` 处理所有事情
1. 在同一个应用程序上永远不要同时运行经典的 `elastic-apm` 和 EDOT

## 示例

请参阅 [EDOT Python 设置指南](https://www.elastic.co/docs/reference/opentelemetry/edot-sdks/python/setup) 获取完整示例。
