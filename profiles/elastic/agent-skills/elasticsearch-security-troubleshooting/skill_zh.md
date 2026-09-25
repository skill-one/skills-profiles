# Elasticsearch 安全故障排除

诊断和解决常见的 Elasticsearch 安全问题。这项技能提供了一个结构化的分级处理工作流程，用于处理身份验证失败、授权错误、TLS 问题、API 密钥问题、角色映射不匹配、Kibana 登录失败以及许可证到期锁定。

有关身份验证方法和 API 密钥管理，请参阅 **elasticsearch-authn** 技能。有关角色、用户和角色映射，请参阅 **elasticsearch-authz** 技能。有关许可证管理，请参阅 **elasticsearch-license** 技能。

有关诊断 API 端点，请参阅 [参考资料/api-reference.md](references/api-reference.md)。

> **部署说明：** 诊断 API 的可用性在自托管、ECH 和 Serverless 之间有所不同。有关详细信息，请参阅 [部署兼容性](#deployment-compatibility)。

## 需要完成的任务

- 诊断 HTTP 401 身份验证失败
- 诊断 HTTP 403 权限拒绝错误
- 排查 TLS/SSL 握手或证书错误
- 调查过期或无效的 API 密钥
- 调试不授予预期角色的角色映射
- 修复 Kibana 登录失败、重定向循环或 CORS 错误
- 从许可证到期锁定中恢复
- 确定用户为何无法访问特定索引

## 前提条件

| 项目                   | 描述                                                                |
| ---------------------- | -------------------------------------------------------------------------- |
| **Elasticsearch URL**  | 集群端点（例如 `https://localhost:9200` 或 Cloud 部署 URL）             |
| **身份验证**     | 任何有效的凭证——即使是最低级别的——以访问集群                |
| **集群权限** | `monitor` 用于只读诊断；`manage_security` 用于修复           |

提示用户输入任何缺失的值。如果用户完全无法进行身份验证，请从 [TLS 和证书错误](#tls-and-certificate-errors) 或 [许可证到期恢复](#license-expiry-recovery) 开始。

## 诊断工作流程

将症状路由到正确的部分：

| 症状                                        | 部分                                                       |
| ---------------------------------------------- | ------------------------------------------------------------- |
| HTTP 401, `authentication_exception`           | [身份验证失败](#authentication-failures-401)       |
| HTTP 403, `security_exception`, 访问被拒绝  | [授权失败](#authorization-failures-403)         |
| SSL/TLS 握手错误，证书被拒绝  | [TLS 和证书错误](#tls-and-certificate-errors)     |
| API 密钥被拒绝，过期或无效      | [API 密钥问题](#api-key-issues)                             |
| 角色映射不授予预期角色       | [角色映射问题](#role-mapping-issues)                   |
| Kibana 登录损坏，重定向循环，CORS 错误 | [Kibana 身份验证问题](#kibana-authentication-issues) |
| 所有用户被锁定，付费功能被禁用   | [许可证到期恢复](#license-expiry-recovery)           |

每个部分都遵循 **收集 - 诊断 - 解决** 的模式。

## 诊断工具包

在任何安全调查开始时使用这些 API：

```bash
curl <auth_flags> "${ELASTICSEARCH_URL}/_security/_authenticate"
```

确认身份、域和角色。如果这以 401 失败，问题在于身份验证。

```bash
curl <auth_flags> "${ELASTICSEARCH_URL}/_xpack"
```

确认安全是否启用 (`features.security.enabled`)。如果安全被禁用，所有安全 API 都会返回错误。

```bash
curl -X POST "${ELASTICSEARCH_URL}/_security/user/_has_privileges" \
  <auth_flags> \
  -H "Content-Type: application/json" \
  -d '{
    "index": [
      { "names": ["'"${INDEX_PATTERN}"'"], "privileges": ["read"] }
    ]
  }'
```

测试经过身份验证的用户是否持有特定权限，而无需 `manage_security`。

```bash
curl <auth_flags> "${ELASTICSEARCH_URL}/_license"
```

检查许可证类型和状态。过期的付费许可证会禁用付费域和功能。

## 身份验证失败 (401)

401 响应表示 Elasticsearch 无法验证调用者的身份。

### 收集

```bash
curl -v <auth_flags> "${ELASTICSEARCH_URL}/_security/_authenticate" 2>&1
```

`-v` 标志显示头和响应正文。查找：

- `WWW-Authenticate` 头——表示集群接受的认证方案。
- 响应正文中的 `authentication_exception`——`reason` 字段描述了什么失败。

### 诊断

| 症状                                            | 可能的原因                                    |
| -------------------------------------------------- | ----------------------------------------------- |
| `unable to authenticate user`                      | 用户名或密码错误                      |
| `unable to authenticate with provided credentials` | 凭证与链中的任何域都不匹配                 |
| `user is not enabled`                              | 本地用户帐户被禁用             |
| `token is expired`                                 | API 密钥或 bearer 令牌已过期             |
| 没有 `WWW-Authenticate` 头                       | 安全可能被禁用；检查 `GET /_xpack`   |

如果用户通过外部域（LDAP、AD、SAML、OIDC）进行身份验证，域链顺序很重要。Elasticsearch 按配置顺序尝试域，并在第一个匹配时停止。如果一个较高优先级的域在到达预期域之前拒绝凭证，身份验证就会失败。

### 解决

| 原因                   | 操作                                                                     |
| ----------------------- | -------------------------------------------------------------------------- |
| 错误凭证       | 验证用户名/密码或 API 密钥值。参见 **elasticsearch-authn**。    |
| 禁用用户           | `PUT /_security/user/{name}/_enable`。参见 **elasticsearch-authz**。         |
| 过期 API 密钥         | 创建一个新的 API 密钥。参见 [API 密钥问题](#api-key-issues)。               |
| 域链顺序       | 检查 `elasticsearch.yml` 域顺序（仅限自托管）。                 |
| 安全禁用       | 在 `elasticsearch.yml` 中启用 `xpack.security.enabled: true` 并重启。  |
| 过期后付费域 | 许可证过期——参见 [许可证到期恢复](#license-expiry-recovery)。 |

## 授权失败 (403)

403 响应表示用户已通过身份验证但缺乏所需的权限。

### 收集

测试操作所需的特定权限：

```bash
curl -X POST "${ELASTICSEARCH_URL}/_security/user/_has_privileges" \
  <auth_flags> \
  -H "Content-Type: application/json" \
  -d '{
    "index": [
      { "names": ["logs-*"], "privileges": ["read", "view_index_metadata"] }
    ],
    "cluster": ["monitor"]
  }'
```

响应包含 `has_all_requested` 布尔值和每个资源的细分。

还要检查用户的有效角色：

```bash
curl <auth_flags> "${ELASTICSEARCH_URL}/_security/_authenticate"
```

检查 `roles` 数组和 `authentication_realm` 以确认用户是你期望的那个。

### 诊断

| 症状                                   | 可能的原因                                           |
| ----------------------------------------- | ------------------------------------------------------ |
| `has_all_requested: false` for an index   | 角色缺少所需的索引权限           |
| `has_all_requested: false` for a cluster  | 角色缺少所需的集群权限         |
| 用户拥有的角色比预期的少        | 角色数组在最后一次更新时被替换（而不是合并）   |
| API 密钥返回 403 在之前允许的操作上 | API 密钥权限是快照——角色创建后的更改不会传播到现有密钥             |

### 解决

| 原因                     | 操作                                                                                   |
| ------------------------- | ---------------------------------------------------------------------------------------- |
| 缺少索引权限   | 将权限添加到角色或创建新角色。参见 **elasticsearch-authz**。         |
| 缺少集群权限 | 添加集群权限。参见 **elasticsearch-authz**。                                  |
| 更新时角色被替换  | 首先获取当前角色，然后使用完整的数组进行更新。参见 **elasticsearch-authz**。 |
| 过期的 API 密钥权限  | 使用更新后的 `role_descriptors` 创建新的 API 密钥。参见 **elasticsearch-authn**。       |

## TLS 和证书错误

TLS 错误阻止客户端完全建立连接。

### 收集

```bash
curl -v --cacert "${CA_CERT}" "https://${ELASTICSEARCH_HOST}:9200/" 2>&1 | head -30
```

查找：

- `SSL certificate problem: unable to get local issuer certificate` — CA 不可信。
- `SSL certificate problem: certificate has expired` — 证书已过期。
- `SSL: no alternative certificate subject name matches target host name` — 主机名不匹配。

对于更深入的检查（仅限自托管）：

```bash
openssl s_client -connect "${ELASTICSEARCH_HOST}:9200" -showcerts </dev/null 2>&1
```

这显示完整的证书链、过期日期和主题备用名称。

### 诊断

| 错误消息                                     | 可能的原因                                  |
| ------------------------------------------------- | --------------------------------------------- |
| `unable to get local issuer certificate`          | 缺少或错误的 CA 证书               |
| `certificate has expired`                         | 服务器或 CA 证书已过期          |
| `no alternative certificate subject name matches` | 证书 SAN 不包含主机名 |
| `self-signed certificate`                         | 自签名证书不在信任存储中       |
| `SSLHandshakeException` (Java 客户端)             | 信任存储缺少 CA 或密码错误   |

### 解决

| 原因               | 操作                                                                     |
| ------------------- | -------------------------------------------------------------------------- |
| 错误的 CA 证书       | 使用 `--cacert` 传递正确的 CA 或将其添加到系统信任存储。   |
| 过期的证书         | 使用 `elasticsearch-certutil` 重新生成证书（仅限自托管）。      |
| 主机名不匹配   | 使用正确的 SAN 条目重新生成证书。                   |
| 自签名证书    | 将 CA 证书分发给所有客户端或使用公开信任的 CA。        |
| 快速修复    | 使用 `curl -k` / `--insecure` 跳过验证。 **不适用于生产环境。** |

在 ECH 中，TLS 由 Elastic 管理——证书错误通常表示客户端未使用正确的 Cloud 端点 URL。在 Serverless 中，TLS 完全由 Elastic 管理，并且是透明的。

## API 密钥问题

### 收集

检索密钥的元数据：

```bash
curl "${ELASTICSEARCH_URL}/_security/api_key?name=${KEY_NAME}" <auth_flags>
```

检查响应中的 `expiration`、`invalidated` 和 `role_descriptors`。

### 诊断

| 症状                                   | 可能的原因                                                     |
| ----------------------------------------- | ---------------------------------------------------------------- |
| 使用密钥时返回 401                    | 密钥过期或失效                                       |
| 在应该允许的操作上返回 403  | 密钥创建时 `role_descriptors` 不充分             |
| 派生的密钥没有访问权限                 | API 密钥创建了另一个 API 密钥——派生密钥没有权限 |
| 密钥对某些索引有效但对其他索引无效 | `role_descriptors` 范围太窄                           |

### 解决

| 原因               | 操作                                                                                          |
| ------------------- | ----------------------------------------------------------------------------------------------- |
| 过期密钥         | 创建一个具有适当 `expiration` 的新密钥。参见 **elasticsearch-authn**。                    |
| 失效密钥     | 创建一个新密钥。失效的密钥无法恢复。                                                    |
| 错误的范围         | 创建一个具有正确 `role_descriptors` 的新密钥。参见 **elasticsearch-authn**。                  |
| 派生密钥问题 | 使用用户凭证执行 `POST /_security/api_key/grant`。参见 **elasticsearch-authn**。 |

## 角色映射问题

角色映射将角色授予来自外部域的用户。当它们静默失败时，用户通过身份验证但不会获得任何角色。

### 收集

```bash
curl <auth_flags> "${ELASTICSEARCH_URL}/_security/_authenticate"
```

注意 `username`、`authentication_realm.name` 和 `roles` 数组。

```bash
curl <auth_flags> "${ELASTICSEARCH_URL}/_security/role_mapping"
```

列出所有映射并检查它们的 `rules` 和 `enabled` 字段。

### 诊断

| 症状                                    | 可能的原因                                               |
| ------------------------------------------ | ---------------------------------------------------------- |
| 用户具有空的 `roles` 数组               | 没有匹配用户的属性的映射                               |
| 用户获得错误的角色                      | 不同的映射首先匹配或规则太宽泛                           |
| 映射存在但不起作用          | `enabled` 是 `false`                                       |
| Mustache 模板产生错误的角色名称 | 模板语法错误或意外的属性值        |

比较用户的 `authentication_realm.name` 和 `groups`（来自 `_authenticate`）与每个映射的 `rules` 以找到不匹配。

### 解决

| 原因            | 操作                                                                               |
| ---------------- | ------------------------------------------------------------------------------------ |
| 没有匹配的规则 | 更新映射规则以匹配用户的域和属性。                   |
| 映射禁用       | 在映射上设置 `"enabled": true`。                                                |
| 模板错误   | 使用已知属性值测试 Mustache 模板。参见 **elasticsearch-authz**。 |
| 规则太宽泛   | 添加 `all` / `except` 条件以缩小匹配。参见 **elasticsearch-authz**。    |

## Kibana 身份验证问题

### 缺少 `kbn-xsrf` 头

所有修改 Kibana API 请求都需要 `kbn-xsrf` 头：

```bash
curl -X PUT "${KIBANA_URL}/api/security/role/my-role" \
  <auth_flags> \
  -H "kbn-xsrf: true" \
  -H "Content-Type: application/json" \
  -d '{ ... }'
```

如果没有它，Kibana 会返回 `400 Bad Request` 并带有 `"Request must contain a kbn-xsrf header"`。

### SAML/OIDC 重定向循环

常见原因：

- `elasticsearch.yml` 中的 `xpack.security.authc.realms.saml.*.sp.acs` 或 `idp.metadata.path` 不正确。
- IdP 和 Elasticsearch 节点之间的时钟偏差（SAML 断言有一个有效期窗口）。
- Kibana 的 `server.publicBaseUrl` 与 SAML ACS URL 不匹配。

验证 SAML 域配置：

```bash
curl <auth_flags> "${ELASTICSEARCH_URL}/_security/_authenticate"
```

如果这返回通过非 SAML 域的有效用户，则 SAML 域本身没有被访问。检查域链顺序。

### Kibana 无法访问 Elasticsearch

Kibana 日志记录 `Unable to retrieve version information from Elasticsearch nodes`。验证 `kibana.yml` 中的 `elasticsearch.hosts` 设置指向可访问的端点，并且凭证（`elasticsearch.username` / `elasticsearch.password` 或 `elasticsearch.serviceAccountToken`）是有效的。

## 许可证到期恢复

当付费许可证过期时，集群进入 **安全关闭** 状态：付费域（SAML、LDAP、AD、PKI）停止工作，通过它们进行身份验证的用户被锁定。本地和文件域保持功能。

### 快速分级

```bash
curl <auth_flags> "${ELASTICSEARCH_URL}/_license"
```

如果 `license.status` 是 `"expired"`，请继续恢复。

### 恢复步骤

遵循 **elasticsearch-license** 技能中详细恢复工作流程。关键的第一步取决于部署类型：

| 部署   | 第一步                                                                |
| ------------ | ------------------------------------------------------------------------- |
| 自托管 | 使用基于文件的用户（`elasticsearch-users` CLI）或本地用户登录。 |
| ECH          | 联系 Elastic 支持或通过 Cloud 控制台续订。                   |
| Serverless   | 不适用——许可证由 Elastic 完全管理。                   |

## 示例

### 查询日志时用户收到 403

**症状：** “我在搜索 `logs-*` 时收到 403。”

1. 验证身份：

```bash
curl -u "joe:${PASSWORD}" "${ELASTICSEARCH_URL}/_security/_authenticate"
```

响应显示 `"roles": ["viewer"]`。

1. 测试权限：

```bash
curl -X POST "${ELASTICSEARCH_URL}/_security/user/_has_privileges" \
  -u "joe:${PASSWORD}" \
  -H "Content-Type: application/json" \
  -d '{"index": [{"names": ["logs-*"], "privileges": ["read"]}]}'
```

响应：`"has_all_requested": false`——`viewer` 角色不包括 `logs-*` 的 `read`。

1. 修复：创建 `logs-reader` 角色并将其分配给 Joe。参见 **elasticsearch-authz**。

### API 密钥停止工作

**症状：** “我的 API 密钥自昨天以来返回 401。”

1. 检查密钥：

```bash
curl -u "admin:${PASSWORD}" "${ELASTICSEARCH_URL}/_security/api_key?name=my-key"
```

响应显示 `"expiration": 1709251200000`——密钥已过期。

1. 修复：创建一个具有合适 `expiration` 的新 API 密钥。参见 **elasticsearch-authn**。

### SAML 登录重定向到错误页面

**症状：** “点击 Kibana 中的 SSO 按钮重定向到错误页面。”

1. 通过非 SAML 方法验证 SAML 域是否可访问：

```bash
curl -u "elastic:${PASSWORD}" "${ELASTICSEARCH_URL}/_security/_authenticate"
```

1. 验证 Elasticsearch 节点可访问 IdP 元数据 URL（仅限自托管）：

```bash
curl -s "${IDP_METADATA_URL}" | head -5
```

1. 检查时钟偏差——SAML 断言有时间敏感性。确保所有节点上都配置了 NTP。
1. 验证 `kibana.yml` 中的 `server.publicBaseUrl` 与 IdP 配置的 SAML ACS URL 匹配。

### 许可证过期后用户被锁定

**症状：** “没有人可以登录到 Kibana。我们使用 SAML。”

1. 检查许可证：

```bash
curl -u "admin:${PASSWORD}" "${ELASTICSEARCH_URL}/_license"
```

响应显示 `"status": "expired"`, `"type": "platinum"`。

1. 由于付费许可证过期，SAML 域被禁用。按照 **elasticsearch-license** 中的恢复步骤操作：
   使用基于文件或本地用户登录，然后上传续订的许可证或切换到基本版。

## 指南

### 总是先使用 `_authenticate`

作为第一个诊断步骤运行 `GET /_security/_authenticate`。它在一个调用中显示用户的身份、域、角色和身份验证类型。大多数问题都可以从这个响应中明显看出。

### 尽早检查许可证

在调查域或权限问题之前，使用 `GET /_license` 验证许可证是否激活。过期的付费许可证会禁用域和功能，产生类似于配置错误的症状。

### 在手动检查之前使用 `_has_privileges`

不要读取角色定义并在脑海中计算有效访问权限，而是使用 `POST /_security/user/_has_privileges` 直接测试特定权限。这样更快，并且考虑了角色组合、DLS 和 FLS。

### 避免使用超级用户凭证

绝对不要使用内置的 `elastic` 超级用户进行日常故障排除。创建一个具有 `manage_security` 权限的专用管理员用户或 API 密钥。仅将 `elastic` 用户保留用于初始设置和紧急恢复。

### 生产环境中不要绕过 TLS

使用 `curl -k` 或 `--insecure` 跳过证书验证并掩盖真实的 TLS 问题。仅在初始诊断时使用它，然后修复底层的证书问题。

## 部署兼容性

诊断工具和 API 的可用性在部署类型之间有所不同。

| 工具 / API                       | 自托管 | ECH           | Serverless    |
| -------------------------------- | ------------ | ------------- | ------------- |
| `_security/_authenticate`        | 是          | 是           | 是           |
| `_security/user/_has_privileges` | 是          | 是           | 有限       |
| `_xpack`                         | 是          | 是           | 受限       |
| `_license`                       | 是          | 是（只读）    | 不可用       |
| `_security/api_key` (GET)        | 是          | 是           | 是           |
| `_security/role_mapping`         | 是          | 是           | 是           |
| `elasticsearch-users` CLI        | 是          | 不可用       | 不可用       |
| `openssl s_client` on nodes      | 是          | 不可用       | 不可用       |
| Elasticsearch 日志               | 是          | 通过 Cloud UI  | 通过 Cloud UI  |

**ECH 注意：**

- 没有节点级访问权限，因此 `elasticsearch-users` CLI 和直接日志/证书检查不可用。
- TLS 由 Elastic 管理——证书错误通常表示端点 URL 不正确。
- 使用 Cloud 控制台进行日志检查和部署配置。

**Serverless 注意：**

- 许可证 API 未公开。许可证相关的锁定不会发生。
- 本地用户不存在——身份验证问题在组织级别处理。
- TLS 完全由 Elastic 管理，并且是透明的。
