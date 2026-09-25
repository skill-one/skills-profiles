# Zoom AI Services Scribe

Zoom AI Services Scribe 的背景参考，涵盖：
- 同步单文件转写 (`POST /aiservices/scribe/transcribe`)
- 异步批量任务 (`/aiservices/scribe/jobs*`)
- 通过重复短文件上传实现的浏览器麦克风伪流
- webhook 驱动的批量状态更新
- 构建平台 JWT 生成和凭证处理

官方文档：
- https://developers.zoom.us/docs/ai-services/
- https://developers.zoom.us/docs/ai-services/scribe/
- https://developers.zoom.us/docs/api/ai-services/
- https://developers.zoom.us/api-hub/ai-services/methods/endpoints.json
- 快速入门示例：https://github.com/zoom/scribe-quickstart/

## 路由守卫

- 如果用户需要将**上传或存储的媒体转写为文本**，请首先路由到此。
- 如果用户需要**实时会议媒体**且无需基于文件的上传/批量任务，请路由到 [../rtms/SKILL.md](../rtms/SKILL.md)。
- 如果用户需要 AI Services 路径的 Zoom REST API 清单，请链式调用 [../rest-api/SKILL.md](../rest-api/SKILL.md)。
- 如果用户需要 webhook 签名模式或通用 HMAC 接收器加固，可选择链式调用 [../webhooks/SKILL.md](../webhooks/SKILL.md)。

## 快速链接

1. [concepts/auth-and-processing-modes.md](concepts/auth-and-processing-modes.md)
2. [scenarios/high-level-scenarios.md](scenarios/high-level-scenarios.md)
3. [examples/fast-mode-node.md](examples/fast-mode-node.md)
4. [examples/batch-webhook-pipeline.md](examples/batch-webhook-pipeline.md)
5. [references/api-reference.md](references/api-reference.md)
6. [references/environment-variables.md](references/environment-variables.md)
7. [references/samples-validation.md](references/samples-validation.md)
8. [references/versioning-and-drift.md](references/versioning-and-drift.md)
9. [troubleshooting/common-drift-and-breaks.md](troubleshooting/common-drift-and-breaks.md)
10. [RUNBOOK.md](RUNBOOK.md)

## 核心工作流

1. 获取构建平台凭证并生成 HS256 JWT。
2. 选择**快速模式**用于单个短文件或**批量模式**用于存储的存档/大型集合。
3. 提交转写请求。
4. 对于批量任务，轮询任务/文件状态或接收 webhook 通知。
5. 持久化并后处理转写 JSON。

## 托管的快速模式守卫

- 正式快速模式 API 限制为 `100 MB` 和 `2 小时`，但托管浏览器流程可能在上游响应返回之前超时。
- 当前部署样本观察：
  - ~17.2 MB MP4 在约 `26s` 内完成
  - ~38.6 MB MP4 在约 `26-37s` 内完成
  - ~59.2 MB MP4 在后端约 `32-34s` 完成
  - 一些 ~59.2 MB 的浏览器请求在前端显示为 `504`，而后端日志后来显示为 `200`
- 将前端 `504` 加上后端 `200` 视为浏览器/边缘超时的竞争，而不是自动转写失败。
- 对于托管 UI，优先使用异步请求/轮询包装器进行快速模式，而不是让浏览器保持打开状态等待完整的上游响应。
- 对于更大的或不那么可预测的媒体，即使文件仍在正式快速模式大小限制内，也优先选择批量模式。

## 浏览器麦克风模式

- `scribe` 没有公开文档化的实时流 API 界面。
- 如果您需要浏览器麦克风体验，请使用伪流：
  1. 捕获短片段的麦克风音频
  2. 通过异步快速模式包装器上传每个片段
  3. 轮询完成状态
  4. 按顺序追加片段转写
- 推荐的起始节奏：
  - 片段大小：`5 秒`
  - 可接受范围：`5-10 秒`
  - 在途片段请求：`2-3`
- 这是一种用于增量转写更新的实用 UI 模式，而不是 `rtms` 的替代方案。
- 将其视为回退演示模式，而不是首选的生产架构。
- 它增加了重复上传开销、片段边界漂移、浏览器编解码器/容器差异以及转写拼接复杂性。
- 如果用户需要实际实时流摄取、低延迟连续媒体或服务器推送媒体传输，请路由到 [../rtms/SKILL.md](../rtms/SKILL.md)。

## 端点界面

| 模式 | 方法 | 路径 | 用途 |
|------|--------|------|-----|
| 快速 | `POST` | `/aiservices/scribe/transcribe` | 单个文件同步转写 |
| 批量 | `POST` | `/aiservices/scribe/jobs` | 提交异步批量任务 |
| 批量 | `GET` | `/aiservices/scribe/jobs` | 列出任务 |
| 批量 | `GET` | `/aiservices/scribe/jobs/{jobId}` | 检查任务摘要/状态 |
| 批量 | `DELETE` | `/aiservices/scribe/jobs/{jobId}` | 取消排队/处理中的任务 |
| 批量 | `GET` | `/aiservices/scribe/jobs/{jobId}/files` | 检查每文件结果 |

## 高级场景

- 用户上传单个录音后的按需片段转写。
- 存储 S3 通话存档的批量转写。
- 将转写写入您数据库/搜索索引的 webhook 驱动 ETL 流程。
- 导出到您自有存储的 Zoom 管理录音的重新转写。
- 需要时间戳、频道分离和说话人提示的离线合规或 QA 工作流。

## 链式调用

- 存储 Zoom 录音 -> [../rest-api/SKILL.md](../rest-api/SKILL.md) + `scribe`
- webhook 验证加固 -> [../webhooks/SKILL.md](../webhooks/SKILL.md)
- 实时实时转写/媒体 -> [../rtms/SKILL.md](../rtms/SKILL.md)
- 跨产品路由 -> [../general/SKILL.md](../general/SKILL.md)

## 运维

- [RUNBOOK.md](RUNBOOK.md) - 5 分钟预检和调试清单。
