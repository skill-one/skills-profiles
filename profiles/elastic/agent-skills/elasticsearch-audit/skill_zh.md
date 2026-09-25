# Elasticsearch 审计日志

通过集群设置 API 启用和配置 Elasticsearch 的安全审计日志。审计日志记录安全事件，如身份验证尝试、访问授权和拒绝、角色更改和 API 密钥操作——这对于合规性和事件调查至关重要。

有关 Kibana 审计日志（保存对象访问、登录/注销、空间操作），请参阅 **kibana-audit**。有关身份验证和 API 密钥管理，请参阅 **elasticsearch-authn**。有关角色和用户管理，请参阅 **elasticsearch-authz**。有关诊断安全错误，请参阅 **elasticsearch-security-troubleshooting**。

有关详细的 API 端点和事件类型，请参阅 [参考资料/api-reference.md](references/api-reference.md)。

> **部署说明**：审计日志配置因部署类型而异。有关详细信息，请参阅 [部署兼容性](#deployment-compatibility)。

## 需要完成的任务

- 在集群上启用或禁用安全审计日志
- 选择要记录的安全事件（身份验证、访问、配置更改）
- 创建过滤器策略以减少审计日志噪音
- 查询审计日志以查找失败的身份验证尝试
- 调查未经授权的访问或权限提升事件
- 设置以合规性为中心的审计配置
- 从审计数据中检测暴力破解登录模式
- 将审计输出配置到索引以进行程序化查询

## 前提条件

| 项目                   | 描述                                                                |
| ---------------------- | -------------------------------------------------------------------------- |
| **Elasticsearch URL**  | 集群端点（例如 `https://localhost:9200` 或云部署 URL）                |
| **身份验证**     | 有效凭证（请参阅 elasticsearch-authn 技能）                      |
| **集群权限** | `manage` 集群权限以更新集群设置                      |
| **许可证**            | 审计日志需要黄金、白金、企业或试用许可证                              |

提示用户输入任何缺失的值。

## 启用审计日志

无需重启即可动态启用审计日志：

```bash
curl -X PUT "${ELASTICSEARCH_URL}/_cluster/settings" \
  <auth_flags> \
  -H "Content-Type: application/json" \
  -d '{
    "persistent": {
      "xpack.security.audit.enabled": true
    }
  }'
```

要禁用，请将 `xpack.security.audit.enabled` 设置为 `false`。验证当前状态：

```bash
curl "${ELASTICSEARCH_URL}/_cluster/settings?include_defaults=true&flat_settings=true" \
  <auth_flags> | jq '.defaults | with_entries(select(.key | startswith("xpack.security.audit")))'
```

## 审计输出

审计事件可以写入两个输出。两者可以同时启用。

| 输出      | 设置值 | 描述                                                    |
| ----------- | ------------- | -------------------------------------------------------------- |
| **logfile** | `logfile`     | 写入 `<ES_HOME>/logs/<cluster>_audit.json`。默认。     |
| **index**   | `index`       | 写入 `.security-audit-*` 索引。可通过 API 查询。 |

### 通过 API 配置输出

```bash
curl -X PUT "${ELASTICSEARCH_URL}/_cluster/settings" \
  <auth_flags> \
  -H "Content-Type: application/json" \
  -d '{
    "persistent": {
      "xpack.security.audit.enabled": true,
      "xpack.security.audit.outputs": ["index", "logfile"]
    }
  }'
```

`index` 输出对于程序化查询审计事件是必需的。`logfile` 输出对于通过 Filebeat 发送到外部 SIEM 工具非常有用。

> **注意**：在自管理的集群中，`xpack.security.audit.outputs` 可能需要在较旧版本（预 8.x）的 `elasticsearch.yml` 中设置静态值。在 8.x+ 版本中，请优先使用集群设置 API。

## 选择要记录的事件

控制要包含或排除的事件类型。默认情况下，当启用审计时，会记录所有事件。

### 仅包含特定事件

```bash
curl -X PUT "${ELASTICSEARCH_URL}/_cluster/settings" \
  <auth_flags> \
  -H "Content-Type: application/json" \
  -d '{
    "persistent": {
      "xpack.security.audit.logfile.events.include": [
        "authentication_failed",
        "access_denied",
        "access_granted",
        "anonymous_access_denied",
        "tampered_request",
        "run_as_denied",
        "connection_denied"
      ]
    }
  }'
```

### 排除噪音事件

```bash
curl -X PUT "${ELASTICSEARCH_URL}/_cluster/settings" \
  <auth_flags> \
  -H "Content-Type: application/json" \
  -d '{
    "persistent": {
      "xpack.security.audit.logfile.events.exclude": [
        "access_granted"
      ]
    }
  }'
```

排除 `access_granted` 可以显著减少繁忙集群中的日志量——当只关心失败时使用此方法。

### 事件类型参考

| 事件                     | 触发条件                                                 |
| ------------------------- | ---------------------------------------------------------- |
| `authentication_failed`   | 凭证被拒绝                                              |
| `authentication_success`  | 用户成功通过身份验证                            |
| `access_granted`          | 执行了授权操作                                         |
| `access_denied`           | 由于权限不足而拒绝操作                              |
| `anonymous_access_denied` | 拒绝了未经身份验证的请求                    |
| `tampered_request`        | 检测到请求被篡改                                    |
| `connection_granted`      | 节点加入集群（传输层）                            |
| `connection_denied`       | 拒绝了节点连接                             |
| `run_as_granted`          | 授权了 run-as 仿冒                              |
| `run_as_denied`           | 拒绝了 run-as 仿冒                              |
| `security_config_change`  | 更改了安全设置（角色、用户、API 密钥等） |

有关完整事件类型列表和字段详细信息，请参阅 [参考资料/api-reference.md](references/api-reference.md)。

## 过滤器策略

过滤器策略允许您通过用户、域、角色或索引来抑制特定的审计事件，而无需全局禁用事件类型。可以激活多个策略——只有当**没有任何**策略过滤掉事件时，事件才会被记录。

### 忽略系统和内部用户

```bash
curl -X PUT "${ELASTICSEARCH_URL}/_cluster/settings" \
  <auth_flags> \
  -H "Content-Type: application/json" \
  -d '{
    "persistent": {
      "xpack.security.audit.logfile.events.ignore_filters": {
        "system_users": {
          "users": ["_xpack_security", "_xpack", "elastic/fleet-server"],
          "realms": ["_service_account"]
        }
      }
    }
  }'
```

### 忽略特定索引上的健康检查流量

```bash
curl -X PUT "${ELASTICSEARCH_URL}/_cluster/settings" \
  <auth_flags> \
  -H "Content-Type: application/json" \
  -d '{
    "persistent": {
      "xpack.security.audit.logfile.events.ignore_filters": {
        "health_checks": {
          "users": ["monitoring-user"],
          "indices": [".monitoring-*"]
        }
      }
    }
  }'
```

### 过滤器策略字段

| 字段     | 类型          | 描述                                          |
| --------- | ------------- | ---------------------------------------------------- |
| `users`   | array[string] | 要排除的用户名（支持通配符）            |
| `realms`  | array[string] | 要排除的域名称                               |
| `roles`   | array[string] | 要排除的角色名称                                |
| `indices` | array[string] | 要排除的索引名称或模式（支持 `*`）    |
| `actions` | array[string] | 要排除的操作名称（例如 `indices:data/read/*`） |

如果事件与单个策略中指定的所有字段都匹配，则事件会被过滤掉。

### 移除过滤器策略

将策略设置为 `null`：

```bash
curl -X PUT "${ELASTICSEARCH_URL}/_cluster/settings" \
  <auth_flags> \
  -H "Content-Type: application/json" \
  -d '{
    "persistent": {
      "xpack.security.audit.logfile.events.ignore_filters.health_checks": null
    }
  }'
```

## 查询审计事件

当 `index` 输出启用时，审计事件存储在 `.security-audit-*` 索引中，并且可以查询。

### 搜索失败的身份验证尝试

```bash
curl -X POST "${ELASTICSEARCH_URL}/.security-audit-*/_search" \
  <auth_flags> \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "bool": {
        "filter": [
          { "term": { "event.action": "authentication_failed" } },
          { "range": { "@timestamp": { "gte": "now-24h" } } }
        ]
      }
    },
    "sort": [{ "@timestamp": { "order": "desc" } }],
    "size": 50
  }'
```

### 搜索特定索引上的访问拒绝事件

```bash
curl -X POST "${ELASTICSEARCH_URL}/.security-audit-*/_search" \
  <auth_flags> \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "bool": {
        "filter": [
          { "term": { "event.action": "access_denied" } },
          { "term": { "indices": "logs-*" } },
          { "range": { "@timestamp": { "gte": "now-7d" } } }
        ]
      }
    },
    "sort": [{ "@timestamp": { "order": "desc" } }],
    "size": 20
  }'
```

### 搜索安全配置更改

```bash
curl -X POST "${ELASTICSEARCH_URL}/.security-audit-*/_search" \
  <auth_flags> \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "bool": {
        "filter": [
          { "term": { "event.action": "security_config_change" } },
          { "range": { "@timestamp": { "gte": "now-7d" } } }
        ]
      }
    },
    "sort": [{ "@timestamp": { "order": "desc" } }],
    "size": 50
  }'
```

这将捕获角色创建/删除、用户更改、API 密钥操作和角色映射更新。

### 按类型统计事件并检测暴力破解模式

对 `event.action` 使用 `terms` 聚合（`size: 0`）以在时间窗口内按类型统计事件。要检测暴力破解尝试，请使用 `source.ip` 对 `authentication_failed` 事件进行聚合，并设置 `min_doc_count: 5`。有关完整的聚合查询示例，请参阅 [参考资料/api-reference.md](references/api-reference.md)。

## 与 Kibana 审计日志关联

Kibana 具有它自己的审计日志，涵盖了 Elasticsearch 未看到的应用层事件（保存对象 CRUD、Kibana 登录、空间操作）。当用户在 Kibana 中执行操作时，Kibana 会代表用户向 Elasticsearch 发出请求。两个系统都记录相同的 `trace.id`（通过 `X-Opaque-Id` 标头传递），这作为主要关联键。

> **前提条件**：必须单独在 `kibana.yml` 中启用 Kibana 审计。有关设置说明、事件类型和 Kibana 特定过滤器策略，请参阅 **kibana-audit** 技能。

### 查找由 Kibana 操作触发的 ES 审计事件

给定来自 Kibana 审计事件的 `trace.id`，搜索 ES 审计索引以查看底层的 Elasticsearch 操作：

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

### 按用户和时间窗口关联

当 `trace.id` 不可用时（例如直接 API 调用），则回退到用户 + 时间窗口关联：

```bash
curl -X POST "${ELASTICSEARCH_URL}/.security-audit-*/_search" \
  <auth_flags> \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "bool": {
        "filter": [
          { "term": { "user.name": "'"${USERNAME}"'" } },
          { "range": { "@timestamp": { "gte": "now-5m" } } }
        ]
      }
    },
    "sort": [{ "@timestamp": { "order": "asc" } }]
  }'
```

次要关联字段：`user.name`、`source.ip` 和 `@timestamp`。

### 统一查询

通过 Filebeat 将 Kibana 审计日志发送到 Elasticsearch（请参阅 **kibana-audit** 以获取 Filebeat 配置），以便可以一起在单个多索引查询中搜索 `.security-audit-*`（ES）和 `kibana-audit-*`（Kibana）索引，并按 `trace.id` 进行过滤。

## 示例

### 为合规性启用审计日志

**请求**："启用审计日志并记录所有失败的访问和身份验证事件。"

```bash
curl -X PUT "${ELASTICSEARCH_URL}/_cluster/settings" \
  <auth_flags> \
  -H "Content-Type: application/json" \
  -d '{
    "persistent": {
      "xpack.security.audit.enabled": true,
      "xpack.security.audit.logfile.events.include": [
        "authentication_failed",
        "access_denied",
        "anonymous_access_denied",
        "run_as_denied",
        "connection_denied",
        "tampered_request",
        "security_config_change"
      ]
    }
  }'
```

这将捕获所有拒绝和安全更改事件，同时排除高容量的成功事件。

### 调查疑似未经授权的访问尝试

**请求**："有人可能尝试访问 `secrets-*` 索引。检查审计日志。"

```bash
curl -X POST "${ELASTICSEARCH_URL}/.security-audit-*/_search" \
  <auth_flags> \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "bool": {
        "filter": [
          { "terms": { "event.action": ["access_denied", "authentication_failed"] } },
          { "wildcard": { "indices": "secrets-*" } },
          { "range": { "@timestamp": { "gte": "now-48h" } } }
        ]
      }
    },
    "sort": [{ "@timestamp": { "order": "desc" } }],
    "size": 100
  }'
```

在结果中查看 `user.name`、`source.ip` 和 `event.action` 以识别行为者和模式。

### 在繁忙的集群上减少审计噪音

**请求**："审计日志太大。过滤掉监控流量和成功的读取。"

从事件类型中排除 `access_granted`，然后添加监控用户和索引的过滤器策略。有关完整语法，请参阅 [过滤器策略](#filter-policies)。

## 指南

### 优先选择索引输出以进行程序化访问

启用 `index` 输出以使审计事件可查询。`logfile` 输出更适合通过 Filebeat 发送到外部 SIEM 工具，但无法通过 Elasticsearch API 查询。

### 先设置严格的，再扩展

从仅失败事件开始（`authentication_failed`、`access_denied`、`security_config_change`）。仅在需要时添加成功事件——它们会产生高流量。

### 使用过滤器策略而不是禁用事件

使用过滤器策略抑制特定用户或索引，而不是排除整个事件类型。

### 监控审计索引大小

设置 ILM 策略以滚动并删除旧的 `.security-audit-*` 索引。典型的保留期是 30-90 天。

### 启用 Kibana 审计以实现全面覆盖

对于应用层事件（保存对象访问、Kibana 登录、空间操作），请启用 Kibana 审计日志。有关设置，请参阅 **kibana-audit** 技能。使用 `trace.id` 进行关联——请参阅上述 [与 Kibana 审计日志关联](#correlate-with-kibana-audit-logs)。

### 避免使用超级用户凭证

使用具有 `manage` 权限的专用管理员用户或 API 密钥。仅将 `elastic` 保留用于紧急恢复。

## 部署兼容性

| 功能                           | 自管理 | ECH          | 无服务器    |
| ------------------------------------ | ------------ | ------------ | ------------- |
| ES 审计通过集群设置        | 是          | 是          | 不适用 |
| ES logfile 输出                    | 是          | 通过 Cloud UI | 不适用 |
| ES index 输出                      | 是          | 是          | 不适用 |
| 通过集群设置过滤策略            | 是          | 是          | 不适用 |
| 查询 `.security-audit-*`            | 是          | 是          | 不适用 |

**ECH 注意**：ES 审计通过集群设置 API 进行配置。logfile 输出可通过 Cloud 控制台的部署日志访问。index 输出与自管理版本相同。

**无服务器注意**：

- 在无服务器上，审计日志不是用户可配置的。安全事件作为平台的一部分由 Elastic 管理。
- 如果用户询问无服务器的审计，请引导他们使用 Elastic Cloud 控制台或他们的帐户团队。
