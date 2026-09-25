# Elasticsearch 授权

管理 Elasticsearch 基于角色的访问控制：本地用户、角色、角色分配和外部域的角色映射。

有关身份验证方法和 API 密钥管理，请参阅 **elasticsearch-authn** 技能。

有关详细的 API 端点，请参阅 [参考资料/api-reference.md](references/api-reference.md)。

> **部署说明**：功能可用性在自托管、ECH 和 Serverless 之间有所不同。有关详细信息，请参阅
> [部署兼容性](#deployment-compatibility)。

## 需要完成的任务

- 创建具有特定权限集的本地用户
- 定义具有最小权限索引和集群访问的自定义角色
- 将一个或多个角色分配给现有用户
- 创建具有 Kibana 功能或空间权限的角色
- 为外部域用户配置角色映射（SAML、LDAP、PKI）
- 动态地从用户属性（Mustache 模板）中派生角色分配
- 按用户或部门限制文档可见性（文档级安全）
- 对某些角色隐藏敏感字段（如 PII）（字段级安全）
- 使用模板化角色查询实现基于属性的访问控制（ABAC）
- 将自然语言的访问请求转换为用户、角色和角色映射任务

## 前提条件

| 项目                   | 描述                                                                |
| ---------------------- | -------------------------------------------------------------------------- |
| **Elasticsearch URL**  | 集群端点（例如 `https://localhost:9200` 或 Cloud 部署 URL）             |
| **Kibana URL**         | 仅在设置 Kibana 功能/空间权限时需要                               |
| **身份验证**     | 有效凭证（请参阅 elasticsearch-authn 技能）                      |
| **集群权限**     | 对于用户和角色管理操作，需要 `manage_security` 权限                 |

提示用户输入任何缺失的值。

## 解析访问请求

当用户用自然语言描述访问权限（例如 "创建一个对 `logs-*` 具有只读访问权限的用户"）时，在执行之前将请求分解为独立的任务。遵循以下工作流程：

### 第 1 步 — 识别组件

从提示中提取：

| 组件        | 需要回答的问题                                                        |
| ---------------- | ------------------------------------------------------------------------- |
| **谁**          | 新的本地用户、现有用户或外部域用户（LDAP、SAML 等）                     |
| **什么**         | 哪些索引、数据流或 Kibana 功能                           |
| **访问级别** | 读取、写入、管理或特定的权限集                                |
| **范围**        | 所有文档/字段，或按区域、部门、敏感性限制？   |
| **Kibana?**      | 请求中是否提及任何 Kibana 功能（仪表板、Discover 等）  |
| **部署?**  | 自托管、ECH 或 Serverless？Serverless 具有不同的用户模型。  |

### 第 2 步 — 检查现有角色

在创建新角色之前，检查是否已存在一个现有角色已经授予所需的访问权限：

```bash
curl "${ELASTICSEARCH_URL}/_security/role" <auth_flags>
```

如果存在匹配的角色，则跳过角色创建并重用它。

### 第 3 步 — 创建角色（如果需要）

根据请求派生角色名称和显示名称。使用 Elasticsearch API 用于纯索引/集群角色。如果涉及 Kibana 功能，请使用 Kibana API（请参阅 [选择正确的 API](#choosing-the-right-api)）。

### 第 4 步 — 创建或更新用户

| 场景                 | 操作                                                                                                                               |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| **新本地用户**      | 使用角色和强生成的密码创建用户。（仅限自托管 / ECH。）                                            |
| **现有本地用户**      | 获取当前角色，追加新角色，使用完整数组更新用户。（仅限自托管 / ECH。）                            |
| **外部域用户**  | 创建一个角色映射，将用户的域属性映射到角色。（仅限自托管 / ECH。）                               |
| **Serverless 用户**      | 使用 **cloud-access-management** 技能。首先分配预定义角色或创建自定义角色，然后通过 Cloud API 分配它。 |

### 示例分解

**提示:** "创建一个用户 `analyst`，对 `logs-*` 和 `metrics-*` 具有只读访问权限，并在 Kibana 中查看仪表板。"

1. 识别：新用户 `analyst`，索引 `logs-*`/`metrics-*`，仪表板，只读访问。
1. 检查角色：`GET /_security/role` — 无匹配。
1. 通过 Kibana API（涉及仪表板）创建角色：`logs-metrics-dashboard-viewer`。
1. 创建用户：`POST /_security/user/analyst`，`roles: ["logs-metrics-dashboard-viewer"]`。

如果请求不明确，请向用户确认每一步。

## 管理本地用户

> 本地用户管理适用于自托管和 ECH 部署。在 Serverless 上，用户在组织级别进行管理 — 跳过此部分。

### 创建用户

```bash
curl -X POST "${ELASTICSEARCH_URL}/_security/user/${USERNAME}" \
  <auth_flags> \
  -H "Content-Type: application/json" \
  -d '{
    "password": "'"${PASSWORD}"'",
    "roles": ["'"${ROLE_NAME}"'"],
    "full_name": "'"${FULL_NAME}"'",
    "email": "'"${EMAIL}"'",
    "enabled": true
  }'
```

### 更新用户

使用 `PUT /_security/user/${USERNAME}` 并指定要更改的字段。省略 `password` 以保留现有密码。

### 其他用户操作

```bash
curl -X POST "${ELASTICSEARCH_URL}/_security/user/${USERNAME}/_password" \
  <auth_flags> -H "Content-Type: application/json" \
  -d '{"password": "'"${NEW_PASSWORD}"'"}'
curl -X PUT "${ELASTICSEARCH_URL}/_security/user/${USERNAME}/_disable" <auth_flags>
curl -X PUT "${ELASTICSEARCH_URL}/_security/user/${USERNAME}/_enable" <auth_flags>
curl "${ELASTICSEARCH_URL}/_security/user/${USERNAME}" <auth_flags>
curl -X DELETE "${ELASTICSEARCH_URL}/_security/user/${USERNAME}" <auth_flags>
```

## 管理角色

### 选择正确的 API

当角色只需要 `cluster` 和 `indices` 权限时，使用 **Elasticsearch API** (`PUT /_security/role/{name}`)。这是默认值 — 不需要 Kibana 端点。

当角色包含任何 Kibana 功能或空间权限时，请使用 **Kibana 角色API** (`PUT /api/security/role/{name}`)。Elasticsearch API 无法设置 Kibana 功能授权、空间作用域或基本权限，因此如果用户提到 Kibana 功能（如 Discover、仪表板、地图、可视化、画布或任何其他 Kibana 应用程序），则需要 Kibana API。

如果 Kibana 端点不可用或 Kibana API 密钥身份验证失败，则回退到 Elasticsearch API 以设置 `cluster` 和 `indices` 部分，并警告用户 Kibana 权限可能无法设置。在放弃之前，请先提示用户 Kibana URL 或替代凭证。

### 创建或更新角色（Elasticsearch API）

仅当角色只有索引和集群权限时是默认选择：

```bash
curl -X PUT "${ELASTICSEARCH_URL}/_security/role/${ROLE_NAME}" \
  <auth_flags> \
  -H "Content-Type: application/json" \
  -d '{
    "description": "'"${ROLE_DISPLAY_NAME}"'",
    "cluster": [],
    "indices": [
      {
        "names": ["'"${INDEX_PATTERN}"'"],
        "privileges": ["read", "view_index_metadata"]
      }
    ]
  }'
```

### 创建或更新角色（Kibana API）

当角色包含 Kibana 功能或空间权限时需要：

```bash
curl -X PUT "${KIBANA_URL}/api/security/role/${ROLE_NAME}" \
  <auth_flags> \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "'"${ROLE_DISPLAY_NAME}"'",
    "elasticsearch": {
      "cluster": [],
      "indices": [
        {
          "names": ["'"${INDEX_PATTERN}"'"],
          "privileges": ["read", "view_index_metadata"]
        }
      ]
    },
    "kibana": [
      {
        "base": [],
        "feature": {
          "discover": ["read"],
          "dashboard": ["read"]
        },
        "spaces": ["*"]
      }
    ]
  }'
```

### 获取、列出和删除角色

```bash
curl "${ELASTICSEARCH_URL}/_security/role/${ROLE_NAME}" <auth_flags>
curl "${ELASTICSEARCH_URL}/_security/role" <auth_flags>
curl -X DELETE "${ELASTICSEARCH_URL}/_security/role/${ROLE_NAME}" <auth_flags>
```

## 文档级和字段级安全

角色可以在索引内的文档和字段级别进行限制，而不仅仅是索引级权限。

### 字段级安全（FLS）

限制角色可以查看哪些字段。使用 `grant` 白名单或 `except` 黑名单字段：

```bash
curl -X PUT "${ELASTICSEARCH_URL}/_security/role/pii-redacted-reader" \
  <auth_flags> \
  -H "Content-Type: application/json" \
  -d '{
    "description": "PII Redacted Reader",
    "indices": [
      {
        "names": ["customers-*"],
        "privileges": ["read"],
        "field_security": {
          "grant": ["*"],
          "except": ["ssn", "credit_card", "date_of_birth"]
        }
      }
    ]
  }'
```

具有此角色的用户可以看到所有字段，除了 PII 字段。FLS 在搜索、获取和聚合结果中强制执行。

### 文档级安全（DLS）

通过附加查询过滤器来限制角色可以查看哪些文档：

```bash
curl -X PUT "${ELASTICSEARCH_URL}/_security/role/emea-logs-reader" \
  <auth_flags> \
  -H "Content-Type: application/json" \
  -d '{
    "description": "EMEA Logs Reader",
    "indices": [
      {
        "names": ["logs-*"],
        "privileges": ["read"],
        "query": "{\"term\": {\"region\": \"emea\"}}"
      }
    ]
  }'
```

`query` 字段是一个包含查询 DSL 过滤器的 JSON 字符串。具有此角色的用户只能看到 `region` 等于 `emea` 的文档。

### 模板化 DLS 查询（ABAC）

DLS 查询支持 Mustache 模板，可以在查询时注入用户元数据，从而在 RBAC 之上实现基于属性的访问控制（ABAC）。将用户特定属性存储在用户的 `metadata` 字段中，然后在角色查询模板中使用 `{{_user.metadata.<key>}}` 引用它们。

```bash
curl -X PUT "${ELASTICSEARCH_URL}/_security/role/department-reader" \
  <auth_flags> \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Department Reader",
    "indices": [
      {
        "names": ["records-*"],
        "privileges": ["read"],
        "query": "{\"template\": {\"source\": \"{\\\"term\\\": {\\\"department\\\": \\\"{{_user.metadata.department}}\\\"}}\"}}"
      }
    ]
  }'
```

具有 `"metadata": {"department": "engineering"}` 的用户只能看到 `department` 等于 `engineering` 的文档。同一个角色适用于所有部门 — 无需为每个部门创建角色。

对于多值属性（例如，一组必需的程序），使用 `terms_set` 和 `minimum_should_match_field` 确保用户拥有文档中列出的所有必需属性。这可以启用复杂的 ABAC 策略 — 结合安全级别、程序列表和认证日期 — 使用单个角色。有关完整的 `terms_set` ABAC 示例，包括组合多条件策略和用户元数据设置，请参阅
[参考资料/api-reference.md](references/api-reference.md)。

### 结合 DLS 和 FLS

单个索引权限条目可以同时包含 `query`（DLS）和 `field_security`（FLS）。请参阅
[HR 部门示例](#restrict-hr-data-by-department-dls--fls) 以了解实际组合用例。

当用户拥有多个角色时，DLS 查询使用 OR 组合，FLS 授予使用联合。没有 DLS/FLS 的广泛角色可能会无意中扩大访问权限。在组合角色时，始终验证实际权限，并确保没有无限制的角色覆盖 DLS/FLS 意图。

## 分配角色给用户

> 仅限自托管和 ECH。在 Serverless 上，请使用 **cloud-access-management** 技能 — 请参阅
> [Serverless 用户访问](#serverless-user-access)。

使用新的 `roles` 数组更新用户：

```bash
curl -X PUT "${ELASTICSEARCH_URL}/_security/user/${USERNAME}" \
  <auth_flags> \
  -H "Content-Type: application/json" \
  -d '{
    "roles": ["role-a", "role-b"]
  }'
```

`roles` 数组**完全替换** — 包含用户应有的所有角色。在更新之前，请先获取用户以查看当前角色。

### 验证实际权限

角色或用户更新后，使用以下方式验证实际访问权限：

```bash
curl -X POST "${ELASTICSEARCH_URL}/_security/user/_has_privileges" \
  <auth_flags> \
  -H "Content-Type: application/json" \
  -d '{
    "cluster": ["monitor"],
    "index": [
      {
        "names": ["'"${INDEX_PATTERN}"'"],
        "privileges": ["read", "view_index_metadata"]
      }
    ]
  }'
```

## 管理角色映射

> 角色映射在 Serverless 上**不可用**（Elasticsearch API 和 Kibana UI 均被禁用）。请改用 **cloud-access-management** 技能 — 请参阅 [Serverless 用户访问](#serverless-user-access)。

角色映射根据属性规则将外部域用户（LDAP、AD、SAML、PKI）分配给角色。仅限自托管和 ECH。有关支持的规则运算符和资源字段，请参阅
[角色映射资源属性](https://www.elastic.co/docs/deploy-manage/users-roles/cluster-or-deployment-auth/role-mapping-resources)。

### 静态角色映射

```bash
curl -X PUT "${ELASTICSEARCH_URL}/_security/role_mapping/saml-default-access" \
  <auth_flags> \
  -H "Content-Type: application/json" \
  -d '{
    "roles": ["viewer"],
    "enabled": true,
    "rules": {
      "field": { "realm.name": "saml1" }
    }
  }'
```

### 基于 LDAP 组的映射

```bash
curl -X PUT "${ELASTICSEARCH_URL}/_security/role_mapping/ldap-admins" \
  <auth_flags> \
  -H "Content-Type: application/json" \
  -d '{
    "roles": ["superuser"],
    "enabled": true,
    "rules": {
      "all": [
        { "field": { "realm.name": "ldap1" } },
        { "field": { "groups": "cn=admins,ou=groups,dc=example,dc=com" } }
      ]
    }
  }'
```

### 使用 Mustache 模板进行动态角色分配

使用 `role_templates` 而不是 `roles` 从用户属性派生角色名称。必须启用脚本。

```bash
curl -X PUT "${ELASTICSEARCH_URL}/_security/role_mapping/ldap-group-roles" \
  <auth_flags> \
  -H "Content-Type: application/json" \
  -d '{
    "role_templates": [
      {
        "template": { "source": "{{#tojson}}groups{{/tojson}}" },
        "format": "json"
      }
    ],
    "enabled": true,
    "rules": {
      "field": { "realm.name": "ldap1" }
    }
  }'
```

请参阅 [参考资料/api-reference.md](references/api-reference.md) 以获取更多 Mustache 模式，包括从域用户名派生的角色和分层组访问。

### 获取、列出和删除角色映射

```bash
curl "${ELASTICSEARCH_URL}/_security/role_mapping/saml-default-access" <auth_flags>
curl "${ELASTICSEARCH_URL}/_security/role_mapping" <auth_flags>
curl -X DELETE "${ELASTICSEARCH_URL}/_security/role_mapping/saml-default-access" <auth_flags>
```

## Serverless 用户访问

在 Serverless 上，没有本地用户或角色映射。用户通过 Cloud 级别的角色分配获得项目访问权限。

- **预定义角色**（例如 `admin`、`developer`、`viewer`）涵盖了常见的访问模式。如果有一个适合，请直接通过 Cloud API 分配它 — 无需创建自定义角色。
- **自定义角色**在用户需要细粒度访问（特定索引、Kibana 功能、DLS/FLS）时需要。使用 Elasticsearch API 或 Kibana API（与自托管相同 — 请参阅
  [管理角色](#manage-roles)）创建自定义角色，然后通过 Cloud API 将其分配给用户，并附带一个预定义的基本角色。
- **Run-as** 权限在 Serverless 自定义角色中不可用。

使用 **cloud-access-management** 技能进行完整工作流程（邀请用户、分配角色、管理 Cloud API 密钥和验证访问）。此技能仅处理角色定义；cloud-access-management 处理用户分配。

## 示例

### 为日志创建只读用户

**请求:** "创建一个用户 `joe`，对 `logs-*` 具有只读访问权限。"

1. 通过 `PUT /_security/role/logs-reader` 创建角色，`"description": "Logs Reader"` 和
   `indices: [{ names: ["logs-*"], privileges: ["read", "view_index_metadata"] }]`。
1. 通过 `POST /_security/user/joe` 创建用户，`"roles": ["logs-reader"]` 和一个强生成的密码。

### 创建具有 Kibana 仪表板访问权限的角色

**请求:** "让用户读取 `logs-*` 并在 Kibana 中查看仪表板。"

使用 Kibana API (`PUT <KIBANA_URL>/api/security/role/logs-dashboard-viewer`)，使用 `elasticsearch.indices` 用于数据访问，并使用 `kibana[].feature` 用于在所有空间上对 Discover、仪表板和可视化进行读取访问。请参阅
[创建或更新角色（Kibana API）](#create-or-update-a-role-kibana-api) 以获取完整请求结构。

### 向现有用户添加角色

**请求:** "除了她当前的角色之外，再给 Alice 对 `apm-*` 的访问权限。"

1. `GET /_security/user/alice` — 响应显示 `"roles": ["viewer"]`。
1. 创建 `apm-reader` 角色，`indices: [{ names: ["apm-*"], privileges: ["read", "view_index_metadata"] }]`。
1. `PUT /_security/user/alice`，`"roles": ["viewer", "apm-reader"]`（包含所有角色）。

### 授予 Serverless 用户读写权限和 Kibana 仪表板

**请求:** "给 `alice@example.com` 对 `colors` 索引的读写访问权限，并让她使用仪表板和 Discover。"

1. 通过 Kibana API 创建自定义角色：`PUT <KIBANA_URL>/api/security/role/colors-rw-kibana`，`elasticsearch.indices` 对 `colors` 的 `read`、`write`、`view_index_metadata`，以及 `kibana[].feature` 对 `dashboard`、`discover`。
1. 使用 **cloud-access-management** 技能将用户分配给自定义角色 `colors-rw-kibana`。

### 按部门限制 HR 数据（DLS + FLS）

**请求:** "每个经理应该只看到他们自己部门的 HR 记录，并且 PII 字段应该被隐藏。"

1. 创建具有部门元数据的用户：`POST /_security/user/manager_a`，`"metadata": {"department": "engineering"}`。
1. 创建具有 DLS + FLS 的角色：

```json
PUT /_security/role/hr-department-viewer
{
  "description": "HR Department Viewer",
  "indices": [
    {
      "names": ["hr-*"],
      "privileges": ["read"],
      "field_security": { "grant": ["*"], "except": ["ssn", "salary", "date_of_birth"] },
      "query": "{\"template\": {\"source\": \"{\\\"term\\\": {\\\"department\\\": \\\"{{_user.metadata.department}}\\\"}}\"}}"
    }
  ]
}
```

同一个角色适用于所有部门 — 每个用户只看到他们部门的记录，并且 PII 字段被移除。

## 指南

### 最小权限原则

- 不要使用 `elastic` 超级用户进行日常操作。创建专门的最小权限角色，并将 `elastic` 保留用于初始设置和紧急恢复。
- 使用 `read` 和 `view_index_metadata` 进行只读数据访问。除非明确需要，否则 `cluster` 为空。
- 使用 DLS (`query`) 和 FLS (`field_security`) 限制索引内的访问。

### 仅命名权限

永远不要使用内部操作名称（例如 `indices:data/read/search`）。始终使用官方文档中记录的命名权限。优先使用细粒度权限（`manage_ingest_pipelines`、`monitor`）而不是广泛权限（`manage`、`all`）。请参阅
[参考资料/api-reference.md](references/api-reference.md) 以获取完整的权限参考表。

### 角色命名约定

- 使用短小写名称和连字符：`logs-reader`、`apm-data-viewer`、`metrics-writer`。
- 避免使用通用名称，如 `custom-role` 或 `new-role`。
- 将 `description` 设置为简短、人类可读的显示名称 — 不是长句。它在 Kibana UI 中显示为角色的标签。良好：`"Logs Reader"`、`"APM Data Viewer"`。不好：
  `"Read-only access to all logs-* indices for the operations team"`。

### 用户管理

- 默认情况下生成强密码：至少 16 个字符，混合大写字母、小写字母、数字和符号（例如 `X9k#mP2vL!qR7wZn`）。永远不要使用占位符值，如 `changeme` 或 `password123`。
- 优先禁用用户而不是删除用户以保留审计跟踪。
- 用户上的 `roles` 数组在更新时**完全替换**。修改之前请先获取当前角色。

### 角色映射最佳实践

- 使用静态 `roles` 进行简单的固定分配（例如，所有 SAML 用户都获得 `viewer`）。
- 仅当角色必须动态地从用户属性派生时，才使用 `role_templates` 和 Mustache。
- 结合 `all`、`any`、`field` 和 `except` 规则，无需重复映射即可表达复杂条件。
- 首先使用 `enabled: false` 测试新的映射，然后验证后再启用。

## 部署兼容性

请参阅 [参考资料/deployment-compatibility.md](references/deployment-compatibility.md) 以获取功能矩阵和有关自托管、ECH 和 Serverless 部署差异的详细说明。
