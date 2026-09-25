# Grafana Cloud 管理

> **文档**: https://grafana.com/docs/grafana-cloud/account-management.md

## 常见工作流程

### 创建新的堆栈

```bash
# 1. 通过 Cloud API 创建堆栈
curl -X POST https://grafana.com/api/instances \
  -H "Authorization: Bearer <grafana-com-api-key>" \
  -H "Content-Type: application/json" \
  -d '{"name": "my-new-stack", "slug": "my-new-stack", "region": "us-east-0", "plan": "grafana-cloud-free"}'

# 2. 验证堆栈可访问（轮询直到 200）
until curl -fs https://my-new-stack.grafana.net/api/health > /dev/null; do sleep 2; done

# 3. 创建管理员服务账户令牌（见 § 服务账户）

# 4. 测试令牌
curl https://my-new-stack.grafana.net/api/org -H "Authorization: Bearer <token>"
# 返回 200 + 组织 JSON → 令牌有效
```

### 团队入职

1. 通过 `POST /api/org/invites` 邀请用户（每个用户一个 curl — 见 [参考资料/api-reference.md § 堆栈 API](references/api-reference.md#stack-api--user--team--org-management)）
2. 通过 `POST /api/teams` 创建团队
3. 通过 `POST /api/teams/{teamId}/members` 添加每个用户
4. 为团队分配 RBAC 角色（见 [§ RBAC](#rbac)）
5. 验证：`GET /api/teams/{teamId}/members` 返回预期的用户列表

### 配置 SSO（Okta / SAML / GitHub）

1. 从 [参考资料/sso.md](references/sso.md) 选择提供者配置，放入 `grafana.ini`
2. 重启 Grafana
3. **始终在隐身窗口中验证后再宣布**：见 [参考资料/sso.md § 验证 SSO](references/sso.md#verifying-sso) 的 5 步验证 + 角色映射调试模式

### 删除堆栈（破坏性）

```bash
# 1. 通过 Cloud API 删除
curl -X DELETE https://grafana.com/api/instances/{id} \
  -H "Authorization: Bearer <grafana-com-api-key>"

# 2. 验证堆栈已删除（必须返回 404）
curl https://grafana.com/api/instances/{id} \
  -H "Authorization: Bearer <grafana-com-api-key>"
```

如果几秒后 GET 仍然返回 200，删除未生效 — 重新检查堆栈 ID 和 Cloud API 密钥。

## 组织和堆栈结构

```
Grafana Cloud 账户
└── 组织（计费单元）
    ├── 堆栈 1（生产）   → 专用 Grafana、Prometheus、Loki、Tempo URL
    ├── 堆栈 2（测试）
    └── 堆栈 3（开发）
```

- **组织**：顶级账户，包含计费、用户、API 密钥、堆栈
- **堆栈**：专用 Grafana + LGTM 实例，拥有自己的 URL 和凭证

## 用户角色

| 角色 | 范围 | 权限 |
|------|-------|-------------|
| **组织管理员** | 组织 | 管理 堆栈、用户、计费、API 密钥 |
| **管理员** | 堆栈 | 数据源、插件、用户、配置 |
| **编辑** | 堆栈 | 创建/编辑 仪表板、告警 |
| **查看者** | 堆栈 | 仪表板只读 |

## RBAC

在配置文件 YAML 中定义自定义角色 + 分配：

```yaml
# provisioning/access-control/roles.yaml
apiVersion: 1
roles:
  - name: TeamDashboardEditor
    description: 在团队文件夹内编辑仪表板
    permissions:
      - action: dashboards:read
        scope: folders:UID:team-folder
      - action: dashboards:write
        scope: folders:UID:team-folder
      - action: dashboards:create
        scope: folders:UID:team-folder
```

```yaml
# provisioning/access-control/assignments.yaml
apiVersion: 1
roleAssignments:
  - roleName: TeamDashboardEditor
    users:
      - alice@example.com
      - bob@example.com
    teams:
      - platform-team
```

提交 YAML 并重启 Grafana 后，验证角色已应用：`GET /api/access-control/roles | jq '.[] | select(.name=="TeamDashboardEditor")'`.

## 服务账户

服务账户是程序化访问（CI/CD、Terraform、代理）的推荐方式。

```bash
# 1. 创建服务账户
curl -X POST https://yourstack.grafana.net/api/serviceaccounts \
  -H "Authorization: Bearer <admin-token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "terraform-provisioner", "role": "Admin", "isDisabled": false}'

# 2. 为其创建令牌
curl -X POST https://yourstack.grafana.net/api/serviceaccounts/{id}/tokens \
  -H "Authorization: Bearer <admin-token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "ci-token", "secondsToLive": 0}'

# 3. 验证令牌是否有效（在无危害端点测试）
curl https://yourstack.grafana.net/api/org \
  -H "Authorization: Bearer <new-token>"
# 200 + 组织 JSON → 令牌有效。否则 → 重新检查步骤 1 中的角色分配。
```

配置等效（YAML，声明式）：

```yaml
# provisioning/access-control/service_accounts.yaml
apiVersion: 1
serviceAccounts:
  - name: alloy-writer
    orgId: 1
    role: Editor
    tokens:
      - name: alloy-token
```

## 参考资料

- [`references/sso.md`](references/sso.md) — OAuth / SAML / GitHub OAuth 配置 + 5 步 SSO 验证模式 + 常见故障模式
- [`references/terraform.md`](references/terraform.md) — Terraform 提供者配置 + 常见资源模式（团队、用户、文件夹、仪表板）+ 差异排查
- [`references/api-reference.md`](references/api-reference.md) — 完整 Cloud API + 堆栈 API 端点参考 + 审计日志查询
