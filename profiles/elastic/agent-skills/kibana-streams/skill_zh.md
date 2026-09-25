# Kibana Streams

通过 Kibana Streams REST API 读取流元数据、设置和附件，并管理流生命周期（启用、禁用、重新同步）。流是 Kibana 中管理数据的一种实验性方法 —— 预期 API 和行为变化。本技能涵盖 **读取** 操作和 **生命周期**；创建、更新、删除、分支和其他变更操作可能在未来版本中添加。

有关详细端点和参数，请参阅 [references/streams-api-reference.md](references/streams-api-reference.md)。

## 使用场景

- 列出所有流或获取单个流的定义和元数据
- 读取流的摄取设置，或查询流的 ES|QL 定义
- 列出与流关联的附件（仪表板、规则、SLO）
- 启用、禁用或重新同步流

## 前提条件

| 项目               | 描述                                                               |
| ------------------ | ------------------------------------------------------------------------- |
| **Kibana URL**     | Kibana 端点（例如 `https://localhost:5601` 或云部署 URL）             |
| **身份验证**       | API 密钥或基本认证（参见 elasticsearch-authn 技能）                 |
| **权限**          | 读取操作需要 `read_stream`；生命周期 API 需要权限 `manage_stream`     |

在非默认空间中操作时，使用空间范围路径 `/s/{space_id}/api/streams`。对于角色配置（Kibana 功能权限和 Elasticsearch 级别权限），请参阅
[Streams required permissions](https://www.elastic.co/docs/solutions/observability/streams/streams#streams-required-permissions)。

## API 基础和请求头

- **基础路径：** `GET` 或 `POST` 到 `<kibana_url>/api/streams`（或空间路径 `/s/<space_id>/api/streams`）。
- **读取操作：** 通常不需要额外请求头；请遵循
  [官方 API 文档](https://www.elastic.co/docs/api/doc/kibana/group/endpoint-streams) 中每个端点的说明。
- **生命周期操作：** `POST /api/streams/_disable`、`_enable` 和 `_resync` 是变更操作 — 根据 Kibana 版本的要求发送 `kbn-xsrf: true`
  （或等效值）。

## 操作（读取 + 生命周期）

### 读取

| 操作                  | 方法 | 路径                                    |
| -------------------------- | ------ | --------------------------------------- |
| 获取流列表            | GET    | `/api/streams`                          |
| 获取单个流            | GET    | `/api/streams/{name}`                   |
| 获取摄取流设置        | GET    | `/api/streams/{name}/_ingest`           |
| 获取查询流设置        | GET    | `/api/streams/{name}/_query`            |
| 获取流附件            | GET    | `/api/streams/{streamName}/attachments` |

### 生命周期

| 操作       | 方法 | 路径                    |
| --------------- | ------ | ----------------------- |
| 禁用流      | POST   | `/api/streams/_disable` |
| 启用流      | POST   | `/api/streams/_enable`  |
| 重新同步流  | POST   | `/api/streams/_resync`  |

路径参数：`{name}` 和 `{streamName}` 是流标识符（相同值；API 文档使用这两个名称）。

## 生命周期和保留（摄取设置）

摄取设置 (`GET /api/streams/{name}/_ingest`) 暴露两个独立的生命周期区域：

- **流生命周期** (`ingest.lifecycle`) — 控制流数据的保留时间。使用
  `lifecycle.dsl.data_retention`（例如 `"30d"`）进行显式保留，或使用 `lifecycle.inherit` 用于子流。这是用户通常在询问“设置保留”、“更新保留”或“更改流的保留”时所指的内容。
- **失败存储生命周期** (`ingest.failure_store.lifecycle`) — 仅控制失败文档的保留（未成功处理的文档）。除非用户明确提到失败存储或失败文档保留，否则用户很少需要更改此设置。

当用户要求设置或更新保留时，应针对 **流** 的主生命周期 (`lifecycle.dsl.data_retention`)，而不是失败存储，除非他们明确询问失败存储或失败文档。

## 示例

### 列出流

```bash
curl -X GET "${KIBANA_URL}/api/streams" \
  -H "Authorization: ApiKey <base64-api-key>"
```

### 获取单个流

```bash
curl -X GET "${KIBANA_URL}/api/streams/my-stream" \
  -H "Authorization: ApiKey <base64-api-key>"
```

### 获取查询流设置

```bash
curl -X GET "${KIBANA_URL}/api/streams/my-stream/_query" \
  -H "Authorization: ApiKey <base64-api-key>"
```

### 获取流附件

```bash
# 附件（与流关联的仪表板、规则、SLO）
curl -X GET "${KIBANA_URL}/api/streams/my-stream/attachments" \
  -H "Authorization: ApiKey <base64-api-key>"
```

### 禁用、启用或重新同步流

```bash
# 禁用流（根据 API 文档的请求体）— 删除有线流数据；在继续操作前警告并确认
curl -X POST "${KIBANA_URL}/api/streams/_disable" \
  -H "Authorization: ApiKey <base64-api-key>" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -d '{}'

# 启用流
curl -X POST "${KIBANA_URL}/api/streams/_enable" \
  -H "Authorization: ApiKey <base64-api-key>" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -d '{}'

# 重新同步流
curl -X POST "${KIBANA_URL}/api/streams/_resync" \
  -H "Authorization: ApiKey <base64-api-key>" \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -d '{}'
```

检查 [Streams API 操作页面](https://www.elastic.co/docs/api/doc/kibana/group/endpoint-streams) 以获取请求/响应体（例如 \_disable/\_enable/\_resync 的请求体，如果需要）。

## 指南

- 当用户要求设置或更新 **保留** 时，假设他们指的是 **流** 的数据保留
  (`ingest.lifecycle` / `lifecycle.dsl.data_retention`)。除非他们明确询问失败存储或失败文档，否则不要仅更改失败存储保留。
- 其他变更操作（创建、更新、删除、分支、附件管理等）不受此技能支持。有关完整延迟操作列表，请参阅 [references/streams-api-reference.md](references/streams-api-reference.md)。
- **重大事件及其检测查询不在范围内。** 关于重大事件、SigEvents 或知识指标的请求属于专用重大事件技能，该技能使用 `platform.sig_events.*` Agent Builder 工具。`/api/streams/{name}/queries` 和 `/api/streams/{name}/significant_events` 端点已弃用，将在 Kibana 中移除 — 不要在此处使用它们。
- 不要将 **查询流** 与重大事件查询混淆。`/api/streams/{name}/_query` 是查询流的 ES|QL 定义（流类型，包括有线和经典）；它与检测查询无关。
- **禁用流可能导致有线流数据丢失。** 禁用 API 删除有线流数据（经典流数据保留）。在调用禁用之前，警告用户并确认他们了解风险（并且已备份或不再需要数据）。
- 当用户只需检查流状态时，优先使用读取操作；当他们需要启用、禁用或重新同步流时，使用生命周期 API。
