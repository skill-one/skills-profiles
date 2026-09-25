# 安全架构图生成器

**快速入门：** 定义信任边界 → 放置身份/加密/防火墙图标 → 通过访问流连接 → 分组为安全区域 → 使用 ` ```plantuml ` 标签包裹。

> ⚠️ **重要提示：** 始终使用 ` ```plantuml ` 或 ` ```puml ` 代码标签。绝对不要使用 ` ```text ` — 它将不会渲染为图表。

## 关键规则

- 每个图表以 `@startuml` 开头并以 `@enduml` 结尾
- 使用 `left to right direction` 定义访问流（用户 → 认证 → 授权 → 资源）
- 使用 `mxgraph.aws4.*` 标签语法表示安全服务图标
- 默认颜色会自动应用 — 你不需要指定 `fillColor` 或 `strokeColor`
- 使用 `rectangle "信任边界" { ... }` 定义安全区域
- 有向流使用 `-->`，审计/异步流使用 `..>`（虚线）

**完整标签参考：** 请参阅 [stencils/README.md](../uml/stencils/README.md) 了解 9500+ 可用图标。

## Mxgraph 标签语法

```
mxgraph.aws4.<icon> "标签" as <别名>
```

### 身份与访问标签

| 类别 | 标签 | 用途 |
|------|------|------|
| IAM | `identity_and_access_management`, `identity_access_management_iam_roles_anywhere` | 身份策略与角色 |
| SSO/目录 | `cognito`, `ad_connector`, `directory_service`, `cloud_directory` | 用户认证与联合 |
| STS | `sts`, `sts_alternate` | 临时安全凭证 |
| 组织 | `organizations`, `organizations_account`, `organizations_organizational_unit` | 多账户治理 |

### 加密与密钥标签

| 类别 | 标签 | 用途 |
|------|------|------|
| KMS | `key_management_service`, `key_management_service_external_key_store` | 密钥管理与加密 |
| 密钥库 | `secrets_manager` | 密钥轮换与存储 |
| 证书 | `certificate_manager`, `private_certificate_authority` | TLS 证书生命周期 |
| HSM | `cloudhsm` | 硬件安全模块 |
| 加密 | `encrypted_data` | 静态加密数据 |

### 网络安全标签

| 类别 | 标签 | 用途 |
|------|------|------|
| 防火墙 | `network_firewall`, `network_firewall_endpoints`, `firewall_manager` | 网络流量过滤 |
| WAF | `generic_firewall` | Web 应用防火墙 |
| 防护 | `shield`, `shield_shield_advanced`, `shield2` | DDoS 保护 |
| 安全组 | `security_group`, `group_security_group` | 实例级防火墙 |

### 威胁检测与合规标签

| 类别 | 标签 | 用途 |
|------|------|------|
| 检测 | `guardduty`, `detective`, `inspector` | 威胁检测与调查 |
| 数据保护 | `macie` | 敏感数据发现 |
| 合规 | `security_hub`, `security_hub_finding`, `audit_manager`, `config` | 合规状态与审计 |
| 日志 | `cloudtrail`, `cloudtrail_cloudtrail_lake`, `security_lake` | 审计追踪与日志聚合 |
| 治理 | `control_tower`, `organizations` | 多账户治理 |
| 事件 | `security_incident_response` | 事件管理 |

### 连接类型

| 语法 | 含义 | 用例 |
|------|------|------|
| `A --> B` | 实线箭头 | 认证流 / 访问请求 |
| `A ..> B` | 虚线箭头 | 审计事件 / 异步检测 |
| `A -- B` | 实线 | 信任关系 |
| `A --> B : "标签"` | 带标签的连接 | 描述协议或凭证 |

### 快速示例

```plantuml
@startuml
left to right direction
mxgraph.aws4.users "用户" as users
mxgraph.aws4.cognito "Cognito" as auth
mxgraph.aws4.identity_and_access_management "IAM" as iam

rectangle "受保护资源" {
  mxgraph.aws4.s3 "数据 (S3)" as s3
  mxgraph.aws4.encrypted_data "加密" as enc
}

users --> auth : "登录"
auth --> iam : "令牌"
iam --> s3
s3 --> enc
@enduml
```

## 安全架构类型

| 类型 | 用途 | 关键标签 | 示例 |
|------|------|----------|------|
| IAM & 认证 | 身份与认证 | `cognito`, `identity_and_access_management`, `sts` | [iam-authn.md](examples/iam-authn.md) |
| 加密管道 | 静态/传输中数据加密 | `key_management_service`, `certificate_manager`, `secrets_manager` | [encryption-pipeline.md](examples/encryption-pipeline.md) |
| 网络安全 | 边界防御与防火墙 | `network_firewall`, `shield`, `security_group` | [network-security.md](examples/network-security.md) |
| 威胁检测 | 自动化威胁响应 | `guardduty`, `detective`, `security_hub` | [threat-detection.md](examples/threat-detection.md) |
| 合规审计 | 治理与审计追踪 | `config`, `audit_manager`, `cloudtrail`, `security_lake` | [compliance-audit.md](examples/compliance-audit.md) |
| 零信任 | 零信任访问模型 | `cognito`, `identity_and_access_management`, `network_firewall` | [zero-trust.md](examples/zero-trust.md) |
| 数据保护 | 敏感数据分类 | `macie`, `encrypted_data`, `key_management_service` | [data-protection.md](examples/data-protection.md) |
| 多账户治理 | 组织级安全 | `organizations`, `control_tower`, `security_hub` | [multi-account-governance.md](examples/multi-account-governance.md) |
