# Elasticsearch 身份验证

使用已配置的任何支持的认证域对 Elasticsearch 集群进行身份验证。这项技能涵盖了所有内置域、凭证验证和完整的 API 密钥生命周期。

有关角色、用户、角色分配和角色映射的信息，请参阅 **elasticsearch-authz** 技能。

有关详细的 API 端点信息，请参阅 [参考资料/api-reference.md](references/api-reference.md)。

> **部署说明**：并非所有域在每种部署类型上都可用。有关自托管与 ECH（Elastic Cloud Hosted）与 Serverless 的详细信息，请参阅
> [部署兼容性](#deployment-compatibility)。

## 关键原则

- **切勿在聊天中请求凭证。** 不要要求用户粘贴密码、API 密钥、令牌或任何秘密信息到对话中。秘密信息不得出现在对话历史记录中。
- **始终使用环境变量。** 本技能中的所有代码示例都引用环境变量（例如
  `ELASTICSEARCH_PASSWORD`、`ELASTICSEARCH_API_KEY`）。当缺少必要的变量时，指导用户在项目根目录下的 `.env` 文件中设置它——切勿直接提示输入值。
- **优先选择 `.env` 而不是终端导出。** 代理可能在沙盒化的 Shell 会话中运行，不会继承用户终端环境。工作目录中的 `.env` 文件在所有执行上下文中都可靠。仅在用户明确偏好时才建议使用 `export` 作为后备方案。

## 需要完成的任务

- 使用用户名和密码（原生域）对集群进行身份验证
- 使用 API 密钥（令牌）连接
- 验证当前已认证的用户（`_authenticate`）
- 为部署选择正确的认证域
- 创建具有范围权限的 API 密钥用于自动化或服务访问
- 旋转或使现有 API 密钥失效
- 为 Elastic 堆栈组件设置服务账户令牌
- 在 PKI/TLS 设置后使用 PKI/相互 TLS 证书进行身份验证
- 使用配置的外部身份提供程序（SAML、OIDC、LDAP、AD、Kerberos）进行身份验证
- 代表其他用户授予 API 密钥

## 前提条件

| 项目                  | 描述                                                                                                                 |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| **Elasticsearch URL** | 集群端点（例如 `https://localhost:9200` 或云部署 URL）                                                  |
| **凭证**             | 取决于域——请参阅下方的说明                                                                                |
| **已配置的域**       | 身份验证域及其身份后端必须已预先配置（域链、IdP、LDAP/AD、Kerberos、PKI/TLS） |

如果缺少任何必要的值，请指导用户将其添加到项目根目录下的 `.env` 文件中。终端导出可能不会在单独的 Shell 会话中显示给代理——`.env` 文件是可靠默认值。**切勿要求用户将凭证粘贴到聊天中**——秘密信息不得出现在对话历史记录中。

## 认证域

Elasticsearch 按配置的顺序（**域链**）评估域。第一个能够认证请求的域将获胜。内部域由 Elasticsearch 管理；外部域委托给企业身份系统。

### 内部域

#### 原生（用户名和密码）

存储在专用 Elasticsearch 索引中的用户。交互式使用的最简单方法。通过 Kibana 或用户管理 API（请参阅 elasticsearch-authz 技能）进行管理。

```bash
curl -u "${ELASTICSEARCH_USERNAME}:${ELASTICSEARCH_PASSWORD}" "${ELASTICSEARCH_URL}/_security/_authenticate"
```

#### 文件

在每个集群节点上定义的扁平文件（`elasticsearch-users` CLI）。无论许可证状态如何始终处于活动状态，使其成为禁用付费域时的灾难恢复的回退方案。仅在自托管部署中可用。

```bash
curl -u "${FILE_USER}:${FILE_PASSWORD}" "${ELASTICSEARCH_URL}/_security/_authenticate"
```

### 外部域

#### LDAP

使用用户名和密码对外的 LDAP 目录进行身份验证。仅在自托管部署中可用——ECH 或 Serverless 上不可用。通常与角色映射结合使用，将 LDAP 组转换为 Elasticsearch 角色。

```bash
curl -u "${LDAP_USER}:${LDAP_PASSWORD}" "${ELASTICSEARCH_URL}/_security/_authenticate"
```

请求与原生相同——Elasticsearch 通过域链将其路由到 LDAP 域。

#### Active Directory

对 Active Directory 域进行身份验证。仅在自托管部署中可用——ECH 或 Serverless 上不可用。与 LDAP 类似，但使用 AD 特定的默认值（用户主体名称、`sAMAccountName`）。通常与角色映射结合使用进行 AD 组到角色的转换。

```bash
curl -u "${AD_USER}:${AD_PASSWORD}" "${ELASTICSEARCH_URL}/_security/_authenticate"
```

#### PKI（TLS 客户端证书）

使用在 TLS 握手期间呈现的 X.509 客户端证书进行身份验证。需要 PKI 域和 HTTP 层上的 TLS。在 ECH 上，PKI 支持有限——请检查部署设置。Serverless 上不可用。最适合相互 TLS 环境中的服务到服务通信。

```bash
curl --cert "${CLIENT_CERT}" --key "${CLIENT_KEY}" --cacert "${CA_CERT}" \
  "${ELASTICSEARCH_URL}/_security/_authenticate"
```

#### SAML

启用 SAML 2.0 Web 浏览器 SSO，主要用于 Kibana 身份验证。在自托管部署中，在 `elasticsearch.yml` 中配置。在 ECH 上，通过云部署设置 UI 配置。在 Serverless 上，SAML 在组织级别处理，不可按项目配置。标准 REST 客户端不可用——基于浏览器的重定向流程由 Kibana 处理。与 SAML 一起配置另一个域（例如原生或 API 密钥）用于程序化 API 访问。

#### OIDC（OpenID Connect）

启用 OpenID Connect SSO，主要用于 Kibana 身份验证。在自托管部署中，在 `elasticsearch.yml` 中配置。在 ECH 上，通过云部署设置 UI 配置。Serverless 上不可用。与 SAML 类似，它依赖于浏览器重定向，不适合直接 REST 客户端使用。对于 OIDC 旁边的程序化访问，请使用 API 密钥或原生用户。

自定义应用程序可以通过 `POST /_security/oidc/authenticate` 交换 OIDC 令牌以获取 Elasticsearch 访问令牌，但这需要实现完整的 OIDC 重定向流程。

#### JWT（JSON Web 令牌）

接受由外部身份提供程序发布的 JWT 作为令牌。在自托管部署中，在 `elasticsearch.yml` 中配置。在 ECH 上，通过云部署设置 UI 配置。Serverless 上不可用。支持两种令牌类型：

- **`id_token`**（默认）—— OpenID Connect ID 令牌，用于用户代表流程。
- **`access_token`**—— OAuth2 客户端凭证，用于应用程序身份流程。

```bash
curl -H "Authorization: Bearer ${JWT_TOKEN}" "${ELASTICSEARCH_URL}/_security/_authenticate"
```

每个 JWT 域处理一种令牌类型。如果需要 `id_token` 和 `access_token`，请配置单独的域。

#### Kerberos

使用 Kerberos 证书通过 SPNEGO 机制进行身份验证。仅在自托管部署中可用——ECH 或 Serverless 上不可用。需要可工作的 KDC 基础设施、正确的 DNS 和时间同步。

```bash
kinit "${KERBEROS_PRINCIPAL}"
curl --negotiate -u : "${ELASTICSEARCH_URL}/_security/_authenticate"
```

`--negotiate` 标志启用 SPNEGO。`-u :` 是 curl 所必需的，但用户名被忽略——`kinit` 中的主体被使用。需要 curl 7.49+ 并支持 GSS-API/SPNEGO。

### API 密钥

不是域，而是一种独特的认证机制。在 `Authorization` 头中传递 Base64 编码的 API 密钥。对于程序化和自动化访问的首选。

```bash
curl -H "Authorization: ApiKey ${ELASTICSEARCH_API_KEY}" "${ELASTICSEARCH_URL}/_security/_authenticate"
```

`ELASTICSEARCH_API_KEY` 是创建时返回的 `encoded` 值（`id:api_key` 的 Base64）。

### 验证身份验证

在执行任何管理操作之前始终验证凭证：

```bash
curl <auth_flags> "${ELASTICSEARCH_URL}/_security/_authenticate"
```

检查 `username`、`roles` 和 `authentication_realm.type` 以确认身份和方法：

| `authentication_realm.type` | 域            |
| --------------------------- | -------------- |
| `native`                    | 原生           |
| `file`                      | 文件           |
| `ldap`                      | LDAP          |
| `active_directory`          | Active Directory |
| `pki`                       | PKI            |
| `saml`                      | SAML          |
| `oidc`                      | OpenID Connect |
| `jwt`                       | JWT            |
| `kerberos`                  | Kerberos       |

对于 API 密钥，`authentication_type` 是 `"api_key"`（不是域类型）。

## 管理 API 密钥

### 创建 API 密钥

```bash
curl -X POST "${ELASTICSEARCH_URL}/_security/api_key" \
  <auth_flags> \
  -H "Content-Type: application/json" \
  -d '{
    "name": "'"${KEY_NAME}"'",
    "expiration": "30d",
    "role_descriptors": {
      "'"${ROLE_NAME}"'": {
        "cluster": [],
        "indices": [
          {
            "names": ["'"${INDEX_PATTERN}"'"],
            "privileges": ["read"]
          }
        ]
      }
    }
  }'
```

响应包含 `id`、`api_key` 和 `encoded`。安全地存储 `encoded`——它无法再次检索。

省略 `role_descriptors` 以继承认证用户当前权限的快照。

> **限制**：API 密钥**不能**创建具有权限的另一个 API 密钥。派生密钥将没有任何有效访问权限。改用用户凭证或 `POST /_security/api_key/grant` 进行程序化密钥创建。

### 获取和使 API 密钥失效

```bash
curl "${ELASTICSEARCH_URL}/_security/api_key?name=${KEY_NAME}" <auth_flags>
curl -X DELETE "${ELASTICSEARCH_URL}/_security/api_key" \
  <auth_flags> \
  -H "Content-Type: application/json" \
  -d '{"name": "'"${KEY_NAME}"'"}'
```

## 示例

### 创建具有范围的 API 密钥

**请求**："创建一个只能读取 `metrics-*` 的 API 密钥。"

```json
POST /_security/api_key
{
  "name": "metrics-reader-key",
  "expiration": "90d",
  "role_descriptors": {
    "metrics-reader": {
      "indices": [
        {
          "names": ["metrics-*"],
          "privileges": ["read", "view_index_metadata"]
        }
      ]
    }
  }
}
```

### 验证哪个域认证了用户

```json
GET /_security/_authenticate
```

```json
{
  "username": "joe",
  "authentication_realm": { "name": "ldap1", "type": "ldap" },
  "authentication_type": "realm"
}
```

### 使用 JWT 令牌进行身份验证

```bash
curl -H "Authorization: Bearer ${JWT_TOKEN}" "https://my-cluster:9200/_security/_authenticate"
```

确认响应显示 `authentication_realm.type` 为 `"jwt"`。

## 指南

### 选择认证方法

| 方法          | 最适合                                    | 权衡                                      |
| --------------- | ------------------------------------------- | ----------------------------------------------- |
| Native user     | 交互式使用，简单设置                      | 密码必须存储或提示输入                     |
| File user       | 灾难恢复，引导                          | 必须在每个节点上配置                      |
| API key         | 程序化访问，CI/CD，范围访问               | 创建后无法检索                          |
| LDAP / AD       | 企业目录集成                            | 需要访问目录服务器的网络连接             |
| PKI certificate | 服务到服务，相互 TLS 环境                | 需要PKI基础设施和PKI域                   |
| SAML            | 通过企业 IdP 的 Kibana SSO                | 仅浏览器；不适合 REST 客户端              |
| OIDC            | 通过 OpenID Connect 提供商的 Kibana SSO    | 仅浏览器；不适合 REST 客户端              |
| JWT             | 基于令牌的服务和用户身份验证              | 需要外部令牌颁发者和域配置               |
| Kerberos        | Windows/企业 Kerberos 环境                | 需要KDC、DNS、时间同步基础设施             |

对于自动化工作流，请优先选择 API 密钥——它们支持细粒度范围和独立的过期。对于 Kibana SSO，请使用 SAML 或 OIDC。对于企业目录集成，请使用 LDAP 或 AD 并配合角色映射（请参阅 elasticsearch-authz）。

### 避免使用超级用户凭证

切勿使用内置的 `elastic` 超级用户或任何 `superuser`-角色账户进行日常操作、自动化或应用程序访问。相反，创建一个仅具有任务所需权限的专用用户或 API 密钥。`elastic` 用户应仅用于初始集群设置和紧急恢复。

### 安全

- API 密钥**不能**创建具有权限的另一个 API 密钥。使用用户凭证或 `POST /_security/api_key/grant` 进行程序化密钥创建。
- 始终为 API 密钥设置 `expiration`。避免在生产中无限期使用密钥。
- 通过 `role_descriptors` 范围 API 密钥。切勿为自动化系统创建无范围密钥。
- 切勿在聊天中接收、回显或记录密码、API 密钥、令牌或任何凭证。指导用户直接在终端、环境变量或文件中管理秘密。
- 切勿在代码、脚本或版本控制中存储秘密。从环境变量加载。
- 使用 `GET /_security/_authenticate` 在执行管理操作前验证凭证。
- 在为原生用户生成密码时，使用至少 16 个字符混合大写字母、小写字母、数字和符号。切勿使用占位符值，如 `changeme` 或 `password123`。
- SAML 和 OIDC 仅用于浏览器 SSO。始终与原生、文件或 API 密钥域一起配置它们，以供 REST API 访问。

## 部署兼容性

并非所有认证域在每种部署类型上都可用。**自托管**集群支持所有域。
**Elastic Cloud Hosted (ECH)** 由 Elastic 管理，没有节点级访问权限。
**Serverless** 是完全管理的 SaaS。

| 域            | 自托管 | ECH                     | Serverless         |
| ---------------- | ------------ | ----------------------- | ------------------ |
| Native           | 是          | 是                     | 不可用            |
| File             | 是          | 不可用           | 不可用            |
| LDAP             | 是          | 不可用           | 不可用            |
| Active Directory | 是          | 不可用           | 不可用            |
| PKI              | 是          | 有限                 | 不可用            |
| SAML             | 是          | 是（部署配置） | 组织级别         |
| OIDC             | 是          | 是（部署配置） | 不可用            |
| JWT              | 是          | 是（部署配置） | 不可用            |
| Kerberos         | 是          | 不可用           | 不可用            |
| API keys         | 是          | 是                     | 是                |

**ECH 注意事项：**

- 没有节点访问权限，因此文件域和 `elasticsearch-users` CLI 不可用。
- LDAP、Active Directory 和 Kerberos 不能在 ECH 上配置。
- SAML、OIDC 和 JWT 可通过云部署设置 UI 配置。
- `elastic` 超级用户可用，但仍然应避免日常使用。

**Serverless 注意事项：**

- API 密钥是主要的认证方法。
- 原生用户不存在——用户在 Elastic Cloud 组织级别管理。
- SAML SSO 在组织级别配置，不是按项目配置。
