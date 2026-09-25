# EDOT Python 迁移指南

在做出更改之前，请阅读迁移指南：

- [迁移指南](https://www.elastic.co/docs/reference/opentelemetry/edot-sdks/python/migration)
- [EDOT Python 安装](https://www.elastic.co/docs/reference/opentelemetry/edot-sdks/python/setup)
- [EDOT Python 配置](https://www.elastic.co/docs/reference/opentelemetry/edot-sdks/python/configuration)

## 指南

1. 删除所有经典 APM 引用：从 `requirements` 中删除 `elastic-apm`，从应用程序代码中删除 `ElasticAPM(app)` / `elasticapm.contrib.*`，删除 `app.config['ELASTIC_APM']` 块，以及所有 `ELASTIC_APM_*` 环境变量
1. 通过 pip 安装 `elastic-opentelemetry`（添加到 `requirements.txt` 或等效文件）
1. 在镜像构建期间运行 `edot-bootstrap --action=install` 以安装检测到的库的自动仪器化包
1. 使用 `opentelemetry-instrument` 包裹应用程序入口点 — 例如 `opentelemetry-instrument gunicorn app:app`。没有这个，将不会收集任何遥测数据
1. 设置恰好三个必需的环境变量：
   - `OTEL_SERVICE_NAME`（替换 `ELASTIC_APM_SERVICE_NAME`）
   - `OTEL_EXPORTER_OTLP_ENDPOINT` — 必须是**管理的 OTLP 端点**或**EDOT 收集器**的 URL。不要重用旧的 `ELASTIC_APM_SERVER_URL` 值。永远不要使用 APM 服务器 URL（没有 `apm-server`，没有 `:8200`，没有 `/intake/v2/events`）
   - `OTEL_EXPORTER_OTLP_HEADERS` — `"Authorization=ApiKey <key>"` 或 `"Authorization=Bearer <token>"`（替换 `ELASTIC_APM_SECRET_TOKEN`）
1. 不要设置 `OTEL_TRACES_EXPORTER`、`OTEL_METRICS_EXPORTER` 或 `OTEL_LOGS_EXPORTER` — 默认值已经是正确的
1. 不要在同一个应用程序上同时运行经典的 `elastic-apm` 和 EDOT

## 示例

请参阅 [EDOT Python 迁移指南](https://www.elastic.co/docs/reference/opentelemetry/edot-sdks/python/migration) 获取完整示例。
