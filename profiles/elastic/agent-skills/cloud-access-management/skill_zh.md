# 云访问管理

管理 Elastic Cloud 组织及其 Serverless 项目的身份和访问权限：邀请用户、分配预定义或自定义角色，以及管理 Cloud API 密钥。

> **前提条件：** 此技能假定 **cloud-setup** 技能已经运行——`EC_API_KEY` 已在环境中设置，组织上下文已建立。如果缺少 `EC_API_KEY`，请指示代理先调用 **cloud-setup**。**不要**直接提示用户输入 API 密钥。

项目创建，请参阅 **cloud-create-project** 技能。对于第 2 天的项目操作（列出、更新、删除），请参阅 **cloud-manage-project**。对于 Elasticsearch 级别的角色管理（本地用户、角色映射、DLS/FLS），请参阅 **elasticsearch-authz** 技能。

有关详细的 API 端点和请求模式，请参阅 [references/api-reference.md](references/api-reference.md)。

## 待办事项

- 邀请用户加入组织并分配给他们 Serverless 项目角色
- 列出组织成员及其当前的角色分配
- 更新用户的角色（组织级或项目级）
- 将用户从组织中移除
- 创建具有作用域角色和过期时间的附加 Cloud API 密钥
- 创建一个 Cloud API 密钥，它还可以在 Serverless 项目上调用 Elasticsearch 和 Kibana API
- 列出和撤销 Cloud API 密钥
- 在 Serverless 项目内创建一个具有 ES 集群、索引和 Kibana 特权的自定义角色
- 使用 Cloud API 的 `application_roles` 为 Serverless 项目上的用户分配或移除自定义角色
- 将自然语言访问请求转换为邀请、角色和 API 密钥任务

## 前提条件和权限

| 项目                 | 描述                                                                                             |
| -------------------- | ------------------------------------------------------------------------------------------------------- |
| **EC_API_KEY**       | Cloud API 密钥（由 **cloud-setup** 设置）。所有操作都需要。                                    |
| **组织 ID**  | 使用 `GET /organizations` 自动发现。**不要**询问用户。                                 |
| **项目端点**        | Serverless 项目的 Elasticsearch 端点。仅自定义角色操作需要。                               |
| **ES 凭据**         | 项目上具有 `manage_security` 权限的 API 密钥或凭据。仅自定义角色操作需要。 |
| **组织所有者角色**   | 只有组织所有者才能创建和管理 Cloud API 密钥。API 密钥操作需要。         |

在执行任何操作之前，运行 `python3 skills/cloud/access-management/scripts/cloud_access.py list-members` 以验证 `EC_API_KEY` 是否有效并自动发现组织 ID。

### 操作级权限

对于 Elastic Cloud Serverless 中的常见访问管理操作，需要以下权限。

| 操作                          | 需要的权限                                            |
| ---------------------------------- | -------------------------------------------------------------- |
| 邀请 / 移除成员            | 组织所有者 (`organization-admin`)                      |
| 分配或移除角色             | 组织所有者 (`organization-admin`)                      |
| 创建 / 撤销 Cloud API 密钥     | 组织所有者 (`organization-admin`)                      |
| 列出成员、邀请或密钥         | 任何组织成员                                        |
| 创建 / 删除自定义角色       | `manage_security` 集群权限在项目 ES 端点上          |

此技能不执行单独的角色预检查。尝试请求的操作并让 API 强制执行授权。如果 API 返回授权错误（例如，`403 Forbidden`），请停止并要求用户验证提供的 API 密钥权限。

### 手动设置回退（当 cloud-setup 不可用时）

如果此技能独立安装且 `cloud-setup` 不可用，请在运行命令之前指示用户手动配置 Cloud 环境变量。**永远不要**提示用户在聊天中粘贴 API 密钥。

| 变量                | 需要    | 描述                                                                                       |
| ----------------------- | ----------- | ------------------------------------------------------------------------------------------------- |
| `EC_API_KEY`            | 是         | 具有组织所有者角色的 Elastic Cloud API 密钥。                                               |
| `EC_BASE_URL`           | 否          | Cloud API 基 URL（默认：`https://api.elastic-cloud.com`）。                                    |
| `ELASTICSEARCH_URL`     | 条件性    | Elasticsearch URL。仅自定义角色操作需要。                                      |
| `ELASTICSEARCH_API_KEY` | 条件性    | 具有 `manage_security` 权限的 Elasticsearch API 密钥。仅自定义角色操作需要。             |

> **注意：** 如果缺少 `EC_API_KEY`，或者用户还没有 Cloud API 密钥，请直接引导用户在 [Elastic Cloud API 密钥](https://cloud.elastic.co/account/keys) 处生成一个，然后使用以下步骤在本地配置它。

首选方法（代理友好）：在项目根目录中创建一个 `.env` 文件：

```bash
EC_API_KEY=your-api-key
EC_BASE_URL=https://api.elastic-cloud.com
# 仅当对项目 Elasticsearch 端点执行自定义角色操作时才需要：
# ELASTICSEARCH_URL=https://<project-id>.es.<region>.elastic-cloud.com
# ELASTICSEARCH_API_KEY=<your-es-manage-security-api-key>
```

所有 `cloud/*` 脚本都会自动加载工作目录中的 `.env`。

替代方法：在终端中直接导出：

```bash
export EC_API_KEY="<your-cloud-api-key>"
export EC_BASE_URL="https://api.elastic-cloud.com"
# 仅当对项目 Elasticsearch 端点执行自定义角色操作时才需要：
# export ELASTICSEARCH_URL="https://<project-id>.es.<region>.elastic-cloud.com"
# export ELASTICSEARCH_API_KEY="<your-es-manage-security-api-key>"
```

终端导出可能对在单独 shell 会话中运行的沙盒代理不可见，因此在使用代理时请优先使用 `.env`。

## 将访问请求分解

当用户用自然语言描述访问权限时（例如，“将 Alice 添加到我的搜索项目中作为开发者”），在执行之前将请求分解为独立的任务。

### 第 1 步 — 确定组件

| 组件        | 要回答的问题                                                  |
| ---------------- | ------------------------------------------------------------------- |
| **谁**          | 新组织成员（邀请）或现有成员（角色更新）？           |
| **什么**         | 哪些 Serverless 项目或组织级访问？                    |
| **访问级别** | 预定义角色（Admin/Developer/Viewer/Editor）或自定义角色？     |
| **API 密钥？**     | 请求是否还需要 Cloud API 密钥用于程序化访问？ |

### 第 2 步 — 检查是否预定义角色适用

参考下方的 [预定义角色表](#预定义角色)。优先使用预定义角色——只有在预定义角色无法提供所需粒度时才创建自定义角色。

### 第 3 步 — 检查现有状态

在创建或邀请之前，检查已存在的内容：

```bash
python3 skills/cloud/access-management/scripts/cloud_access.py list-members
python3 skills/cloud/access-management/scripts/cloud_access.py list-api-keys
```

如果用户已经是成员，则跳过邀请并更新他们的角色。

**对于 API 密钥请求**，只有组织所有者才能创建和管理 Cloud API 密钥。如果经过身份验证的用户没有 `organization-admin` 角色，API 密钥操作将因 403 错误而失败。检查 `list-api-keys` 返回的现有密钥。如果存在一个与相同目的或任务具有所需角色且剩余生命周期足够的活动密钥，则重用它而不是创建一个新的。当两个具有相同权限的密钥服务于不同目的（例如，两个独立的 CI 管道）时是合法的——但为同一任务创建第二个密钥是不必要的，并且会增加管理负担。

### 第 4 步 — 执行

从 `skills/cloud/access-management/scripts/cloud_access.py` 运行适当的命令。在执行之前，请与用户确认破坏性操作（移除成员、撤销密钥）。

### 第 5 步 — 验证

执行后，再次列出成员或密钥以确认更改已生效。

## 预定义角色

### 组织级角色

| 角色               | Cloud API `role_id`  | 描述                                |
| ------------------ | -------------------- | ------------------------------------------ |
| 组织所有者         | `organization-admin` | 对组织、部署、项目拥有完全管理权限 |
| 账单管理员      | `billing-admin`      | 仅管理账单详情                |

### Serverless 项目级角色

| 角色           | Cloud API `role_id` | 可用范围          | 描述                                          |
| -------------- | ------------------- | --------------------- | ---------------------------------------------------- |
| Admin          | `admin`             | Search, Obs, Security | 对项目进行完全管理，登录时为超级用户        |
| Developer      | `developer`         | Search only           | 创建索引、API 密钥、连接器、可视化        |
| Viewer         | `viewer`            | Search, Obs, Security | 对项目数据和功能进行只读访问        |
| Editor         | `editor`            | Obs, Security         | 配置项目功能，只读数据索引   |
| Tier 1 analyst | `t1_analyst`        | Security only         | 事件分类、一般读取、创建仪表板        |
| Tier 2 analyst | `t2_analyst`        | Security only         | 事件分类、开始调查、创建案例     |
| Tier 3 analyst | `t3_analyst`        | Security only         | 深入调查、规则、列表、响应操作   |
| SOC manager    | `soc_manager`       | Security only         | 事件、案例、端点策略、响应操作     |
| Rule author    | `rule_author`       | Security only         | 检测工程、规则创建                 |

项目级角色在邀请（`POST /organizations/{org_id}/invitations`）或使用角色分配更新（`POST /users/{user_id}/role_assignments`）时分配。有关 `role_assignments` JSON 模式的参考，请参阅 [references/api-reference.md](references/api-reference.md)，包括 `project` 范围。

## 自定义角色（Serverless）

当预定义角色缺乏所需粒度时，使用 Elasticsearch 安全 API 在 Serverless 项目内创建自定义角色，并通过 Cloud API 的 `application_roles` 字段将其分配给用户。

> **安全：** 在使用自定义角色时，**不要**单独分配预定义的 Cloud 角色。自定义角色隐式授予项目范围的 Cloud 访问权限。如果你还分配 `viewer`（或其他任何预定义角色）作为同一项目的单独 Cloud 角色分配，则用户在 SSO 到项目时将获得两个角色的**并集**——Viewer 堆栈角色比大多数自定义角色更广泛，将覆盖你打算的限制。

### 自定义角色分配的工作原理

- **预定义角色**（`viewer`、`developer`、`admin` 等）通过 Cloud API（`invite-user`、`assign-role`）分配。当用户 SSO 到项目时，他们将获得映射到其 Cloud 角色的堆栈角色（例如，Cloud `viewer` 映射到 `viewer` 堆栈角色）。
- **自定义角色** 通过 Elasticsearch 安全 API（`create-custom-role`）在项目内创建，并通过 Cloud API 的 `application_roles` 字段（`assign-custom-role`）分配。当设置 `application_roles` 时，用户在 SSO 到项目时将获得**仅**指定的自定义角色——不会获得其 Cloud 角色的默认堆栈角色。
- `assign-custom-role` 命令将 `role_id` 设置为项目类型的 Viewer 角色（`elasticsearch-viewer`、`observability-viewer` 或 `security-viewer`），并将 `application_roles` 设置为自定义角色名称。这确保用户可以在 Cloud 控制台看到并访问项目，但在项目内将获得自定义角色的限制权限。
- Cloud API 密钥也可以使用 `application_roles` 获得对 Serverless 项目的 Elasticsearch/Kibana API 访问。有关详细信息，请参阅下文 [Cloud API 密钥 — ES 和 Kibana API 访问](#cloud-api-keys--es-and-kibana-api-access)。

### 标准自定义角色入职流程

1. 在项目中创建自定义角色（`create-custom-role`）。
2. 如果用户还不是成员，则邀请他们加入组织（`invite-user`）。**不要**在邀请中包含项目角色分配——下一步的自定义角色分配将处理项目访问。
3. 将自定义角色分配给用户（`assign-custom-role --user-id ... --project-id ... --custom-role-name ...`）。
4. 使用 `list-members` 和 `list-roles` 进行验证。

### 创建自定义角色

```bash
python3 skills/cloud/access-management/scripts/cloud_access.py create-custom-role \
  --role-name marketing-analyst \
  --body '{"cluster":[],"indices":[{"names":["marketing-*"],"privileges":["read","view_index_metadata"]}]}'
```

这会调用项目 Elasticsearch 端点上的 `PUT /_security/role/{name}`。

### 命名约束

角色名称必须以字母或数字开头，并只能包含字母、数字、`_`、`-` 和 `.`。在 Serverless 中不可用 Run-as 权限。

### 何时使用自定义角色与预定义角色

| 场景                                   | 使用             |
| ------------------------------------------ | --------------- |
| 标准的 admin/developer/viewer 访问     | 预定义角色 |
| 对特定索引模式进行只读访问             | 自定义角色     |
| DLS 或 FLS 限制                    | 自定义角色     |
| Kibana 功能级访问控制        | 自定义角色     |

对于高级 DLS/FLS 模式（模板查询、ABAC），请参阅 **elasticsearch-authz** 技能。

## Cloud API 密钥 — ES 和 Kibana API 访问

Cloud API 密钥现在除了 Cloud API 外，还可以选择访问 Serverless 项目上的 Elasticsearch 和 Kibana API。这启用了一个用于控制平面（Cloud API）和数据平面（ES/Kibana API）操作的单一凭证——例如，一个创建项目通过 Cloud API 并然后通过 ES API 索引数据的 CI 管道。

### 工作原理

在创建时向密钥的 `role_assignments` 中添加 `application_roles`。此字段接受预定义角色名称（`admin`、`developer`、`viewer` 和解决方案特定角色，如 `t1_analyst`、`editor`）或通过 `PUT /_security/role/{name}` 在项目中创建的自定义角色名称。预定义角色在每个项目中默认可用。必须在每个应具有访问权限的项目中单独创建自定义角色——如果引用的自定义角色在一个项目中不存在，则密钥在该项目中将无声地获得无访问权限。

### 关键规则：无隐式继承

与用户不同，API 密钥**永远不会**从其 `role_id` 继承堆栈角色。如果 `application_roles` 被省略或为空，则密钥仅具有 Cloud API 访问权限。使用此类密钥调用 ES 或 Kibana 端点将返回 **403 Forbidden**。这是为了向后兼容——现有的没有 `application_roles` 的密钥将继续作为仅 Cloud API 密钥工作。

### 作用域模式

- **项目级作用域**（首选）——授予对特定项目或给定类型的所有项目的访问权限。使用 `role_assignments` 中的 `project` 键和每个条目上的 `application_roles`。**默认使用此模式**，除非用户明确需要跨项目访问。

- **组织级作用域**——授予组织中**所有当前和未来项目**的访问权限。使用 `role_assignments` 中的 `organization` 键和 `application_roles`。**这是最广泛的数据平面作用域。** 只有当密钥确实需要访问每个项目（例如，平台自动化或跨项目组织范围的搜索）时才使用。在创建具有 `application_roles` 的组织级密钥之前，始终与用户确认，因为它授予组织中可能尚不存在项目的 ES/Kibana 访问权限。

> **自定义角色和组织级访问：** 当在 `application_roles` 中使用自定义角色名称和组织级分配时，自定义角色必须在每个目标项目中存在。如果项目没有定义该自定义角色（通过 `PUT /_security/role/{name}`），则密钥将无声地获得对该项目的无访问权限——不会引发错误。对于组织级访问，请优先使用预定义角色（`admin`、`developer`、`viewer`），它们在每个项目中默认可用。如果您必须在多个项目中使用自定义角色，请确保在每个目标项目中首先创建该角色。

> **代理指导：** 当用户要求具有 ES/Kibana 访问的 API 密钥时，默认使用项目级分配。只有在用户明确需要跨所有项目访问时，才建议组织级 `application_roles`。在继续之前确认意图——组织级访问也适用于未来项目。如果用户指定了具有组织级访问的自定义角色名称，请警告他们必须在每个项目中单独定义该角色。

### 示例

**项目级密钥具有开发者 ES 访问**（使用 `--stack-access` 便利标志）：

```bash
python3 skills/cloud/access-management/scripts/cloud_access.py create-api-key \
  --description "CI pipeline - ES ingest" \
  --expiration 30d \
  --roles '{"project":{"elasticsearch":[{"role_id":"developer","organization_id":"$ORG_ID","all":true}]}}' \
  --stack-access developer
```

**组织级密钥具有管理员 ES 访问**（访问所有项目——谨慎使用）：

```bash
python3 skills/cloud/access-management/scripts/cloud_access.py create-api-key \
  --description "Platform automation" \
  --expiration 7d \
  --roles '{"organization":[{"role_id":"organization-admin","organization_id":"$ORG_ID"}]}' \
  --stack-access admin
```

**项目级密钥具有自定义角色**（原始 JSON）：

```bash
python3 skills/cloud/access-management/scripts/cloud_access.py create-api-key \
  --description "Marketing ETL" \
  --expiration 14d \
  --roles '{"project":{"elasticsearch":[{"role_id":"elasticsearch-viewer","organization_id":"$ORG_ID","all":false,"project_ids":["$PROJECT_ID"],"application_roles":["marketing-writer"]}]}}'
```

将 `$ORG_ID` 和 `$PROJECT_ID` 替换为实际的组织和项目 ID。使用 `list-members` 发现组织 ID。

> **常见错误：** 如果您的 API 密钥在调用 ES 或 Kibana 端点时收到 403，最可能的原因是缺少 `application_roles`。与用户不同，API 密钥必须具有明确的 `application_roles` 才能访问堆栈——`role_id` 单独是不够的。

## 示例

### 将用户作为 Viewer 邀请到搜索项目

**提示：** "将 `alice@example.com` 添加到我的搜索项目，并授予只读访问权限。"

```bash
python3 skills/cloud/access-management/scripts/cloud_access.py invite-user \
  --emails alice@example.com \
  --roles '{"project":{"elasticsearch":[{"role_id":"viewer","organization_id":"$ORG_ID","all":false,"project_ids":["$PROJECT_ID"]}]}}'
```

将 `$ORG_ID` 和 `$PROJECT_ID` 替换为实际 ID。当邀请被接受时，将分配 Viewer 角色。对于自定义角色访问，请在用户接受邀请后使用 `assign-custom-role`——不要将预定义角色分配与同一项目的自定义角色组合。

### 创建 CI/CD API 密钥

**提示：** "为我们的 CI 管道创建一个 API 密钥，它将在 30 天后过期，并具有对所有部署的编辑访问权限。"

```bash
python3 skills/cloud/access-management/scripts/cloud_access.py create-api-key \
  --description "CI/CD pipeline" \
  --expiration "30d" \
  --roles '{"deployment":[{"role_id":"deployment-editor","all":true}]}'
```

实际的密钥值写入一个安全的临时文件（权限 0600）。stdout JSON 包含一个 `_secret_file` 路径而不是原始密钥。告诉用户从该文件中检索密钥——它只显示一次。当 CI 管道不再需要此密钥时，使用 `delete-api-key` 撤销它，以避免未使用的密钥累积。

### 创建具有 ES 访问的 CI/CD API 密钥

**提示：** "为我们的 CI 管道创建一个 API 密钥，它可以将数据索引到我们的搜索项目中。"

```bash
python3 skills/cloud/access-management/scripts/cloud_access.py create-api-key \
  --description "CI pipeline - ES ingest" \
  --expiration 30d \
  --roles '{"project":{"elasticsearch":[{"role_id":"developer","organization_id":"$ORG_ID","all":true}]}}' \
  --stack-access developer
```

将 `$ORG_ID` 替换为实际的组织 ID。`--stack-access` 标志将 `application_roles: ["developer"]` 注入角色分配中，授予密钥在所有 Elasticsearch 项目上的开发者级 ES/Kibana API 访问。如果没有 `--stack-access`（或 JSON 中的显式 `application_roles`），则密钥将仅具有 Cloud API 访问权限，并在 ES/Kibana 调用时收到 403。

### 为营销数据创建自定义角色

**提示：** "创建一个角色，它将授予对 `marketing-*` 索引的只读访问权限在我的搜索项目中。"

```bash
python3 skills/cloud/access-management/scripts/cloud_access.py create-custom-role \
  --role-name marketing-reader \
  --body '{"cluster":[],"indices":[{"names":["marketing-*"],"privileges":["read","view_index_metadata"]}]}'
```

然后使用 `assign-custom-role` 命令将自定义角色分配给用户，该命令在 Cloud API 角色分配中设置 `application_roles`。

### 完整的自定义角色流程，用于只读仪表板

**提示：** "将 `bob@example.com` 添加到我的搜索项目，并授予只读仪表板访问权限。"

```bash
# 1) 在项目中创建自定义角色
python3 skills/cloud/access-management/scripts/cloud_access.py create-custom-role \
  --role-name dashboard-reader \
  --body '{"cluster":[],"indices":[],"applications":[{"application":"kibana-.kibana","privileges":["feature_dashboard.read"],"resources":["*"]}]}'

# 2) 邀请用户加入组织（不包含项目角色——自定义角色将处理访问）
python3 skills/cloud/access-management/scripts/cloud_access.py invite-user \
  --emails bob@example.com

# 3) 邀请接受后，使用 application_roles 分配自定义角色
python3 skills/cloud/access-management/scripts/cloud_access.py assign-custom-role \
  --user-id "$USER_ID" \
  --project-id "$PROJECT_ID" \
  --project-type elasticsearch \
  --custom-role-name dashboard-reader
```

用户将获得 Viewer 级别的 Cloud 访问权限（可以在控制台中看到项目），并在他们 SSO 到项目时**仅**获得 `dashboard-reader` 权限。不要为该项目也分配 `viewer` 作为单独的 Cloud 角色——这样做将授予更广泛的 Viewer 堆栈角色，并覆盖您打算的限制。

### 更新用户的 项目角色

**提示：** "将 Bob 提升为我们的可观察性项目的管理员。"

```bash
python3 skills/cloud/access-management/scripts/cloud_access.py assign-role \
  --user-id "$USER_ID" \
  --roles '{"project":{"observability":[{"role_id":"admin","organization_id":"$ORG_ID","all":false,"project_ids":["$PROJECT_ID"]}]}}'
```

将 `$USER_ID`、`$ORG_ID` 和 `$PROJECT_ID` 替换为实际值。使用 `list-members` 查找用户 ID。要移除角色分配，请使用具有相同 `--roles` 模式的 `remove-role-assignment`。

### 列出所有成员及其角色

**提示：** "显示我组织中有哪些人可以访问我的组织。"

```bash
python3 skills/cloud/access-management/scripts/cloud_access.py list-members
```

输出包括每个成员的用户 ID、电子邮件和分配的角色。

## 指南

- 如果 `EC_API_KEY` 未设置，不要提示用户——指示代理先调用 **cloud-setup**。
- 在执行任何操作之前，始终与用户确认破坏性操作（移除成员、撤销密钥）。
- 优先使用预定义角色而不是自定义角色，只要它们满足访问要求。
- 此处创建的 API 密钥是 CI/CD、作用域访问或团队成员的附加密钥。初始密钥由 **cloud-setup** 管理。
- **密钥永远不会打印到 stdout 或 stderr。** 脚本在 stdout 中将敏感字段（`key`、`token`、`invitation_token`）替换为 `REDACTED` 占位符，并将完整的未编辑响应写入权限为 0600（所有者只读）的临时文件。stdout JSON 包含一个 `_secret_file` 路径指向该文件。
- **永远不要尝试读取、提取或总结密钥文件的内容。** 如果用户要求密钥，请告诉他们打开 `_secret_file` 路径下的文件。用户检索密钥后，建议他们删除该文件。
- Cloud API 密钥在创建时继承角色，无法更新——撤销并重新创建以更改角色。
- **API 密钥卫生——最小化、作用域和过期：**
  - 在创建密钥之前，始终运行 `list-api-keys` 并检查是否已存在一个具有相同目的或任务的密钥，并且具有所需角色和足够的剩余生命周期。具有相同权限但服务于不同目的（例如，两个独立的 CI 管道）的密钥是合法的——目标是避免为同一任务创建冗余密钥。
  - 始终设置 `--expiration` 以匹配预期任务的生命周期。短期任务（CI 运行、一次性迁移）应使用短期密钥（例如，`1d`、`7d`）。
  - 任务完成后，提示用户使用 `delete-api-key` 撤销不再需要的任何密钥。这适用于短期和长期密钥。
  - 长期密钥（例如，监控管道）仍然应具有定义的过期时间，并应定期轮换而不是设置为永不过期。
- 每个组织最多支持 500 个活动 API 密钥。默认过期时间为 3 个月。
- 邀请默认过期时间为 72 小时。如果用户未接受，请重新发送。
- 对于 SAML SSO 配置，请参阅 [Elastic Cloud SAML 文档](https://www.elastic.co/docs/deploy-manage/users-roles/cloud-organization/configure-saml-authentication)。
- **自定义角色安全——不要过度分配：** 在使用 `assign-custom-role` 为同一项目时，**不要**为项目分配预定义的 Cloud 角色（例如，`viewer`）。自定义角色分配隐式授予 Viewer 级别的 Cloud 访问权限。在顶层添加预定义角色会扩大用户的项目权限，超出自定义角色打算的范围。
- 如果自定义角色存在但用户无法访问项目，请验证是否使用 `assign-custom-role` 分配了角色（它使用 Cloud API 中的 `application_roles`）。仅创建自定义角色不会授予项目访问权限——需要 Cloud API 分配。
- 对于网络级安全（流量过滤器、私有链接），请参阅 **cloud-network-security** 技能。
- 对于 ES 级别的角色管理，超出 Cloud 角色的（本地用户、DLS/FLS），请参阅 **elasticsearch-authz**。
