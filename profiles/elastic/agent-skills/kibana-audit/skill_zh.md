# Kibana 审计日志

通过 `kibana.yml` 启用和配置 Kibana 的审计日志。Kibana 审计日志涵盖了 Elasticsearch 不会看到的 应用层安全事件：保存对象的 CRUD（仪表板、可视化、索引模式、规则、案例）、登录/注销、会话过期、空间操作以及 Kibana 级别的 RBAC 执行。

有关 Elasticsearch 审计日志（身份验证失败、访问授权/拒绝、安全配置更改），请参阅 **elasticsearch-audit**。有关身份验证和 API 密钥管理，请参阅 **elasticsearch-authn**。有关角色和用户管理，请参阅 **elasticsearch-authz**。

有关详细的事件类型、架构和关联查询，请参阅
[references/api-reference.md](references/api-reference.md)。

> **部署说明：** Kibana 审计配置因部署类型而异。有关详细信息，请参阅
> [部署兼容性](#deployment-compatibility)。

## 需要完成的任务

- 启用或禁用 Kibana 审计日志
- 配置审计日志输出（滚动文件、控制台）
- 过滤掉噪音事件（例如 `saved_object_find`）
- 调查保存对象的访问或删除事件
- 跟踪 Kibana 登录/注销和会话活动
- 监控空间创建、修改和删除
- 通过 `trace.id` 将 Kibana 审计事件与 Elasticsearch 审计日志关联
- 将 Kibana 审计日志发送到 Elasticsearch 以进行统一查询

## 前置条件

| 项目                  | 描述                                                                    |
| --------------------- | ------------------------------------------------------------------------------ |
| **Kibana 访问权限**     | 对 `kibana.yml` 的文件系统访问权限（自管理）或 Cloud 控制台访问权限（ECH） |
| **许可证**           | 审计日志需要黄金、白金、企业或试用许可证                                  |
| **Elasticsearch URL** | 用于关联查询 `.security-audit-*` 的集群端点                             |

提示用户输入任何缺失的值。

## 启用 Kibana 审计日志

Kibana 审计在 `kibana.yml` 中静态配置（不是通过 API）。更改后需要重启 Kibana。

```yaml
xpack.security.audit.enabled: true
xpack.security.audit.appender:
  type: rolling-file
  fileName: /path/to/kibana/data/audit.log
  policy:
    type: time-interval
    interval: 24h
  strategy:
    type: numeric
    max: 10
```

要禁用，请将 `xpack.security.audit.enabled` 设置为 `false` 并重启 Kibana。

### Appender 类型

| 类型           | 描述                                             |
| -------------- | ------------------------------------------------------- |
| `rolling-file` | 按轮转策略写入文件。推荐。                         |
| `console`      | 写入 stdout。适用于容器化部署。                 |

## 事件类型

Kibana 审计事件使用 ECS 格式，与 ES 审计具有相同的核心字段（`event.action`、`event.outcome`、`user.name`、`trace.id`、`@timestamp`），并加上 Kibana 特定字段，如 `kibana.saved_object.type`、`kibana.saved_object.id` 和 `kibana.space_id`。

关键事件操作：

| 事件操作                       | 描述                                  | 类别       |
| ---------------------------------- | -------------------------------------------- | -------------- |
| `saved_object_create`              | 一个保存对象被创建                   | 数据库       |
| `saved_object_get`                 | 一个保存对象被读取                      | 数据库       |
| `saved_object_update`              | 一个保存对象被更新                   | 数据库       |
| `saved_object_delete`              | 一个保存对象被删除                   | 数据库       |
| `saved_object_find`                | 执行了保存对象搜索                  | 数据库       |
| `saved_object_open_point_in_time`  | 在保存对象上打开了 PIT            | 数据库       |
| `saved_object_close_point_in_time` | 在保存对象上关闭了 PIT            | 数据库       |
| `saved_object_resolve`             | 一个保存对象被解析（别名重定向） | 数据库       |
| `login`                            | 用户登录（成功或失败）                | 身份验证     |
| `logout`                           | 用户注销                            | 身份验证     |
| `session_cleanup`                  | 清理了过期的会话            | 身份验证     |
| `access_agreement_acknowledged`    | 用户接受了访问协议         | 身份验证     |
| `space_create`                     | 创建了 Kibana 空间                   | Web            |
| `space_update`                     | 更新了 Kibana 空间                   | Web            |
| `space_delete`                     | 删除了 Kibana 空间                   | Web            |
| `space_get`                        | 获取了 Kibana 空间                 | Web            |

有关完整事件架构，请参阅 [references/api-reference.md](references/api-reference.md)。

## 过滤策略

使用 `ignore_filters` 在 `kibana.yml` 中抑制噪音事件：

```yaml
xpack.security.audit.ignore_filters:
  - actions: [saved_object_find]
    categories: [database]
```

| 过滤字段 | 类型 | 描述                |
| ------------ | ---- | -------------------------- |
| `actions`    | list | 要忽略的事件操作    |
| `categories` | list | 要忽略的事件类别    |

如果事件与单个过滤条目中指定的所有字段都匹配，则该事件将被过滤掉。

## 与 Elasticsearch 审计日志关联

当 Kibana 代表用户向 Elasticsearch 发出请求时，两个系统都会记录相同的 `trace.id`（通过 `X-Opaque-Id` 标头传递）。这是跨两个审计日志关联事件的主要键。

> **前置条件：** 必须通过集群设置 API 启用 Elasticsearch 审计。有关设置说明、事件类型和 ES 特定过滤策略，请参阅 **elasticsearch-audit** 技能。

### 关联工作流程

1. 在 Kibana 审计日志中找到可疑事件。
2. 提取其 `trace.id` 值。
3. 在 ES 审计索引（`.security-audit-*`）中搜索所有具有相同 `trace.id` 的事件。
4. 查看合并的时间线，了解 Kibana 操作触发了哪些 ES 级别的操作。

**elasticsearch-audit** 技能还记录了从 ES 方面开始的工作流程——当从 ES 审计事件开始并查找原始的 Kibana 操作时，请使用它。

### 通过 trace ID 搜索 ES 审计

给定一个可疑的 Kibana 事件（例如保存对象的删除），提取其 `trace.id` 并搜索 ES 审计索引：

```bash
curl -X POST "${ELASTICSEARCH_URL}/.security-audit-*/_search" \
  <auth_flags> \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "bool": {
        "filter": [
          { "term": { "trace.id": "'"${TRACE_ID}"'" } },
          { "range": { "@timestamp": { "gte": "now-24h" } } }
        ]
      }
    },
    "sort": [{ "@timestamp": { "order": "asc" } }]
  }'
```

次要关联字段：`user.name`、`source.ip` 和 `@timestamp`（时间窗口连接）。

### 将 Kibana 审计日志发送到 Elasticsearch

要 alongside ES 审计事件查询 Kibana 审计事件，请使用 Filebeat 将 Kibana 审计日志文件发送到 Elasticsearch 索引：

```yaml
filebeat.inputs:
  - type: log
    paths: ["/path/to/kibana/data/audit.log"]
    json.keys_under_root: true
    json.add_error_key: true

output.elasticsearch:
  hosts: ["https://localhost:9200"]
  index: "kibana-audit-%{+yyyy.MM.dd}"
```

索引后，`.security-audit-*`（ES）和 `kibana-audit-*`（Kibana）可以使用 `trace.id` 过滤的多索引查询一起搜索。

## 示例

### 为合规性启用 Kibana 审计

**请求：** "启用 Kibana 审计日志并保留 10 个轮转日志文件。"

```yaml
xpack.security.audit.enabled: true
xpack.security.audit.appender:
  type: rolling-file
  fileName: /var/log/kibana/audit.log
  policy:
    type: time-interval
    interval: 24h
  strategy:
    type: numeric
    max: 10
```

应用更改后重启 Kibana。

### 调查已删除的仪表板

**请求：** "有人删除了一个仪表板。检查 Kibana 审计日志。"

在 Kibana 审计日志（或索引的 `kibana-audit-*` 数据）中搜索 `saved_object_delete` 事件，其中 `kibana.saved_object.type: dashboard`。提取 `trace.id` 并与 ES 审计索引进行交叉引用，以查看底层的 Elasticsearch 操作。

### 减少来自保存对象搜索的审计噪音

**请求：** "Kibana 审计日志因为持续的 `saved_object_find` 事件而太大。"

```yaml
xpack.security.audit.ignore_filters:
  - actions: [saved_object_find]
    categories: [database]
```

这将抑制高容量的读取操作，同时保留创建、更新和删除事件。

## 指南

### 始终与 Elasticsearch 审计一起启用

为了全面覆盖，请在 `kibana.yml` 和 Elasticsearch 中都启用审计。没有 Kibana 审计，保存对象的访问和 Kibana 登录事件将不可见。没有 ES 审计，集群级操作将不可见。有关 ES 端的设置，请参阅 **elasticsearch-audit** 技能。

### 使用 trace.id 进行关联

在调查 Kibana 事件时，始终提取 `trace.id` 并搜索 ES 审计索引（`.security-audit-*`）。这将揭示由单个 Kibana 操作触发的完整操作链。有关查询，请参阅上面的
[与 Elasticsearch 审计日志关联](#correlate-with-elasticsearch-audit-logs)。

### 过滤噪音读取事件

`saved_object_find` 在繁忙的 Kibana 实例上会产生非常高的容量。除非您需要审计读取访问，否则请抑制它。

### 将日志发送到 Elasticsearch 以进行统一查询

Kibana 审计日志默认写入文件。通过 Filebeat 将其发送到 Elasticsearch，以便与 ES 审计事件一起进行程序化查询。

### 合适地轮转和保留

配置滚动文件轮转以避免填满磁盘。典型的合规性保留期为 30-90 天。

## 部署兼容性

| 功能                  | 自管理 | ECH          | Serverless    |
| --------------------------- | ------------ | ------------ | ------------- |
| Kibana 审计 (`kibana.yml`) | 是          | 通过 Cloud UI | 不适用 |
| 滚动文件 Appender       | 是          | 通过 Cloud UI | 不适用 |
| 控制台 Appender            | 是          | 是          | 不适用 |
| 忽略过滤器              | 是          | 通过 Cloud UI | 不适用 |
| 通过 `trace.id` 关联    | 是          | 是          | 不适用 |
| 通过 Filebeat 发送到 ES     | 是          | 是          | 不适用 |

**ECH 注意：** Kibana 审计通过 Cloud 控制台的部署编辑页面启用。日志文件可通过 Cloud 控制台的部署日志访问。

**Serverless 注意：**

- 在 Serverless 上，Kibana 审计日志记录不是用户可配置的。安全事件由 Elastic 作为平台的一部分管理。
- 如果用户询问 Serverless 上的 Kibana 审计，请引导他们使用 Elastic Cloud 控制台或他们的帐户团队。
