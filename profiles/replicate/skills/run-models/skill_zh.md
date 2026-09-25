## 文档

- 参考：<https://replicate.com/docs/llms.txt>
- OpenAPI 架构：<https://api.replicate.com/openapi.json>
- MCP 服务器：<https://mcp.replicate.com>
- 按模型文档：`https://replicate.com/{owner}/{model}/llms.txt`
- 请求文档页面时，若需 Markdown 格式响应，请设置 `Accept: text/markdown`。

## 工作流程

1. **选择合适的模型** - 通过 API 搜索或询问用户。
2. **获取模型元数据** - 通过 API 获取输入和输出架构。
3. **创建预测** - 向 /v1/predictions 发送 POST 请求。
4. **轮询结果** - 获取预测状态，直到状态为 "succeeded"。
5. **返回输出** - 通常为生成内容的 URL。

## 获取输出的三种方式

1. 创建预测，从响应中存储其 ID，并轮询直至完成。
2. 在创建预测时设置 `Prefer: wait` 头部，以获取阻塞同步响应。仅推荐用于非常快的模型。最长 60 秒。
3. 在创建预测时设置 HTTPS webhook URL，当预测完成时，Replicate 将向该 URL 发送 POST 请求。

## 指南

- 使用 `POST /v1/predictions` 端点，因为它支持官方和社区模型。
- 每个模型都有自己的 OpenAPI 架构。始终获取并检查模型架构，以确保设置有效的输入。即使流行模型也会更改其架构。
- 根据架构约束（`minimum`、`maximum`、`enum` 值）验证输入参数。不要生成违反这些约束的值。
- 不确定参数值时，使用模型的默认示例或省略可选参数。
- 除非有理由，否则不要设置可选输入。坚持必需输入，让模型的默认值来处理工作。
- 尽可能使用 HTTPS URL 作为文件输入。也可以发送 base64 编码的文件，但应避免使用。
- 并发启动多个预测。不要等待一个完成后再启动下一个。
- 输出文件 URL 在 1 小时后过期，因此如果需要保留它们，请使用 Cloudflare R2 等服务进行备份。
- Webhooks 是接收和存储预测输出的良好机制。

## 预测

- 预测会经历以下状态：`starting` -> `processing` -> `succeeded` / `failed` / `canceled`。
- 官方模型使用 `owner/name` 格式。社区模型需要 `owner/name:version_id`。
- `POST /v1/predictions` 端点处理这两种情况。

## Webhooks

- 在创建预测时设置 `webhook` 为 HTTPS URL。Replicate 在预测完成时发送完整的预测对象。
- 使用 `webhook_events_filter` 过滤事件：`start`、`output`、`logs`、`completed`。
- 使用 `Webhook-ID`、`Webhook-Timestamp` 和 `Webhook-Signature` 头部验证 webhook 签名。从 `GET /v1/webhooks/default/secret` 获取签名密钥。

## 预测生命周期

- 设置 `lifetime` 以自动取消运行时间过长的预测（例如 `30s`、`5m`、`1h`）。从创建时间开始计算。

## 流式传输

- 支持流式传输的语言模型会在响应中包含 `stream` URL。使用 SSE 接收增量输出。

## 文件处理

- 尽可能使用 HTTPS URL 作为文件输入。一个预测的输出 URL 可以直接作为文件输入传递给下一个模型。
- 输出文件 URL 在 1 小时后过期。如果需要保留它们，请立即下载并存储。

## 多模型工作流

- 通过将输出 URL 作为文件输入传递给下一个模型来串联模型。
- 并行启动所有独立的预测，然后收集结果。
- 输出 URL 有效期为 1 小时，足够用于管道步骤。
