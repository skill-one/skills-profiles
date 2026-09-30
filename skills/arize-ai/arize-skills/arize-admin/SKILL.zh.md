---
name: arize-admin
description: 通过 ax CLI 管理 Arize 用户、组织、空间、项目、角色、角色绑定、资源限制和 API 密钥。用于企业管理员工作流程：邀请和解除用户入职、新团队入职、为 SAML/SSO 映射创建自定义角色、为用户分配角色、限制项目级访问，以及管理多租户架构的服务密钥。涵盖 ax 用户、ax 组织、ax 空间、ax 项目、ax 角色、ax 角色绑定和 ax API 密钥。
---

# Arize 管理技能

通过编程方式管理 Arize 用户、组织、空间、角色、权限和 API 密钥——企业访问控制的基础构建模块。

> **权限要求**：大多数操作需要 **org-admin** 或 **account-admin** 权限。如果命令返回 `403 Forbidden`，则表示经过身份验证的配置文件缺乏足够的权限。

> **破坏性操作规则**：删除、撤销、移除或不可逆修改资源的命令（`delete`、`revoke`、`remove-user`、`unrestrict`）在执行前需要 **明确用户确认**。当用户要求您执行其中一项操作时：
> 1. 精确总结将要发生的事情（例如，“这将删除用户 jane@example.com 并级联撤销其 API 密钥，并移除其所有组织/空间成员资格和角色绑定。”）
> 2. 要求用户确认（使用 `AskUserQuestion`）。
> 3. 只有在用户确认后，才使用 `--force` 运行命令以跳过 CLI 的交互式提示。

> 未经用户首先确认，切勿运行 `--force` 破坏性命令。

## 使用场景

- 邀请用户加入账户，将他们分配到组织和工作空间
- 通过一个命令注销用户并撤销其所有访问权限
- 新团队入职：创建工作空间、创建自定义角色、分配用户、生成服务密钥
- 为 SAML/SSO 属性映射创建自定义角色（需要稳定的角色 ID）
- 限制项目，以便只有明确绑定的用户才能访问
- 为 CI/CD 管道或多租户架构创建作用域服务密钥
- 旋转或撤销 API 密钥
- 在工作空间内创建或删除项目

## 预先问题

对于多步骤工作流，**在运行任何 `ax` 命令之前收集所有所需信息**。使用 `AskUserQuestion` 避免工作流中途来回沟通。先获取实时数据（例如组织列表），以便您能够展示真实选项，而不是要求用户回忆 ID。

### 新团队入职
1. 运行 `ax organizations list -o json` 获取可用组织名称。
2. 使用 `AskUserQuestion`（单次调用，最多 4 个问题）收集：
   - **哪个组织？** — 将列表中的组织名称作为选项呈现
   - **空间名称** — 新团队空间的名称
   - **团队成员** — 邀请的姓名和电子邮件（用户可以通过 "其他" 输入；如果还没有，请询问）
   - **服务密钥？** — 是否为 CI/CD 管道生成服务密钥

### 用户注销
在运行任何命令之前询问：
- **哪个用户？** — 电子邮件地址（然后使用 `ax users list --email` 查找）

### 限制项目
在运行任何命令之前询问：
- **哪个空间和项目？** — 查找项目的全局 ID
- **哪些用户获得明确访问权限？** — 要绑定到受限制项目的用户电子邮件

### 独立邀请用户
在运行任何命令之前询问：
- **姓名和电子邮件** — 每个要邀请的用户
- **角色** — `ADMIN`、`MEMBER` 或 `ANNOTATOR`（作为选项呈现；账户级别的用户创建没有 `READ_ONLY` 角色）
- **邀请模式** — `EMAIL_LINK`（默认）、`TEMPORARY_PASSWORD` 或 `NONE`

### 撤销或旋转 API 密钥
在运行任何命令之前询问：
- **哪个密钥？** — 运行 `ax api-keys list -o json` 并按名称和状态呈现选项；或询问 `KEY_ID`
- **撤销或旋转？** — `revoke` 立即使密钥失效；`refresh` 生成具有相同作用域的新密钥（零停机时间旋转）

如果用户表示要“删除” API 密钥，请使用 `ax api-keys revoke` 使其失效。

## 概念

- **组织** — 账户内的命名分组（例如，每个业务单元一个）。空间存在于组织内。用户首先添加到账户，然后添加到组织，然后添加到空间。
- **空间** — 隔离跟踪、数据集和项目的工位。用户必须成为组织成员后，才能被添加到该组织内的空间。
- **角色** — 命名的权限集。预定义角色由系统管理。自定义角色由管理员创建。组织/空间成员资格的角色（`ADMIN`、`MEMBER`、`READ_ONLY`、`ANNOTATOR`）与用于 `ax role-bindings` 的自定义 RBAC 角色是分开的。
- **角色绑定** — 在特定资源（空间或项目）上为用户细粒度分配自定义角色。
- **资源限制** — 将项目标记为仅允许在该项目上有明确角色绑定的用户访问。任何更高层次级别（空间、组织、账户）绑定的角色都被排除在外。
- **API 密钥** — 要么是 *用户* 密钥（作为创建者身份验证，具有完整用户权限），要么是 *服务* 密钥（作用域为特定空间，用于自动化管道）。

## 前置条件

直接进行——运行您需要的 `ax` 命令。**不要**提前检查版本或配置文件。

如果 `ax` 命令失败：
- `command not found` 或版本错误 → 查看 [references/ax-setup.md](references/ax-setup.md)
- `401 Unauthorized` / 缺少 API 密钥 → 运行 `ax profiles show`；遵循 [references/ax-profiles.md](references/ax-profiles.md)
- `403 Forbidden` → 活动配置文件缺乏管理员权限；查看 [references/ax-profiles.md](references/ax-profiles.md)（**切勿**要求用户将管理员密钥粘贴到聊天中）
- **安全**：**切勿**读取 `.env` 文件或在文件系统中搜索凭证。使用 `ax profiles` 进行 Arize 凭证。**切勿**要求用户将秘密粘贴到聊天中。**切勿**回显、记录或显示原始 API 密钥值。对于缺失凭证，请查看 [references/ax-profiles.md](references/ax-profiles.md)。

> **OAuth 登录选项（v0.18.0+）**：用户可以通过基于浏览器的 OAuth PKCE 而不是 API 密钥进行身份验证，方法是运行 `ax auth login`（然后 `ax auth logout` 撤销）。如果用户询问关于身份验证的替代方案，请告知他们此选项——**切勿**自己运行 `ax auth login`，因为它会交互式地打开浏览器。

---

## 用户

用户必须存在于账户中，才能被添加到组织或空间。**账户级角色**：`ADMIN`、`MEMBER`、`ANNOTATOR`

```bash
ax users list                                  # 所有用户
ax users list --email "jane"                   # 子字符串过滤
ax users list --status active                  # 仅活动
ax users list -l 100 -o json                   # 分页，获取全局 ID

ax users get USER_ID

ax users create \
  --full-name "Jane Doe" \
  --email jane@example.com \
  --role MEMBER \
  --invite-mode EMAIL_LINK        # 或：NONE | TEMPORARY_PASSWORD

ax users update USER_ID --full-name "Jane Smith"
ax users update USER_ID --is-developer          # 授予开发者标志

ax users delete --id USER_ID --force   # ⚠ 首先确认——级联：组织/空间成员资格、API 密钥撤销、角色绑定
ax users delete --email jane@example.com --force   # 或通过 ID 而不是电子邮件解析

ax users resend-invitation USER_ID
ax users reset-password USER_ID
```

---

## 组织

**组织角色**：`ADMIN`、`MEMBER`、`READ_ONLY`、`ANNOTATOR`

```bash
ax organizations list
ax organizations list --name "platform"
ax organizations list -l 100 -o json

ax organizations get "Platform Team"

ax organizations create --name "Platform Team" --description "核心 ML 平台"

ax organizations update "Platform Team" --name "ML Platform" --description "更新"

# 添加用户（必须先存在于账户中）
ax organizations add-user "Platform Team" --user-id USER_ID --role MEMBER

# 移除用户（也会从所有子空间移除）—— ⚠ 首先确认
ax organizations remove-user "Platform Team" --user-id USER_ID --force

# 删除组织：⚠ 不可逆；删除组织及其所有资源（空间、项目、实验、数据集）
ax organizations delete "Platform Team" --force
```

---

## 空间

**空间角色**：`ADMIN`、`MEMBER`、`READ_ONLY`、`ANNOTATOR`

```bash
ax spaces list
ax spaces list --organization-id ORG_ID

ax spaces get "my-workspace"

# --organization-id 必须提供；从 ax organizations list -o json 获取 ORG_ID
ax spaces create --name "team-alpha" --organization-id ORG_ID

ax spaces update "team-alpha" --name "team-alpha-v2"

ax spaces delete "team-alpha" --force   # ⚠ 首先确认——不可逆；删除所有资源

# 用户必须先成为组织成员，才能被添加到空间
ax spaces add-user "team-alpha" --user-id USER_ID --role MEMBER
ax spaces remove-user "team-alpha" --user-id USER_ID --force   # ⚠ 首先确认
```

---

## 角色

用于与 `ax role-bindings` 一起使用的自定义 RBAC 角色。与组织/空间成员资格中更简单的 `ADMIN`/`MEMBER`/`READ_ONLY`/`ANNOTATOR` 角色是分开的。

```bash
ax roles list                          # 所有角色
ax roles list --is-custom -o json      # 自定义仅——获取稳定的 ID 用于 SAML 映射
ax roles list --is-predefined

ax roles get "Data Scientist"          # 检查权限

# --permissions 是逗号分隔的；更新时完全替换
ax roles create \
  --name "Data Scientist" \
  --permissions "PROJECT_READ,DATASET_CREATE,EXPERIMENT_CREATE" \
  --description "读取跟踪、创建数据集和实验"

ax roles update "Data Scientist" --permissions "PROJECT_READ,DATASET_CREATE,EXPERIMENT_CREATE,EVALUATOR_CREATE"

ax roles delete "Data Scientist" --force   # ⚠ 首先确认——预定义角色不能被删除
```

**查找可用权限**：在系统角色（例如 `Member`、`Admin`）上运行 `ax roles get <预定义角色> -o json` 以查看有效的权限名称。

---

## 角色绑定

在特定资源（空间或项目）上为用户细粒度分配自定义角色。

```bash
# 在空间级别分配
ax role-bindings create \
  --user-id USER_GLOBAL_ID \
  --role-id ROLE_GLOBAL_ID \
  --resource-type SPACE \
  --resource-id SPACE_GLOBAL_ID

# 在项目级别分配
ax role-bindings create \
  --user-id USER_GLOBAL_ID \
  --role-id ROLE_GLOBAL_ID \
  --resource-type PROJECT \
  --resource-id PROJECT_GLOBAL_ID

ax role-bindings get BINDING_ID
ax role-bindings update BINDING_ID --role-id NEW_ROLE_ID
ax role-bindings delete BINDING_ID --force   # ⚠ 首先确认

# 列出资源的绑定（必须提供 --resource-type）
ax role-bindings list --resource-type SPACE
ax role-bindings list --resource-type PROJECT --user-id USER_GLOBAL_ID -o json
```

幂等——如果用户在该资源上已经存在绑定，则退出而不报错。

---

## 资源限制

限制 **项目或仪表板**，以便只有在该资源上有明确角色绑定的用户才能访问。空间/组织级角色被排除在外。

```bash
ax resource-restrictions list                                          # 所有限制，分页
ax resource-restrictions list --resource-type DASHBOARD                # 过滤到一种资源类型（PROJECT 或 DASHBOARD）
ax resource-restrictions list --limit 50 --cursor PAGINATION_CURSOR    # 获取下一页

ax resource-restrictions restrict --resource-id PROJECT_OR_DASHBOARD_GLOBAL_ID     # 幂等
ax resource-restrictions unrestrict --resource-id PROJECT_OR_DASHBOARD_GLOBAL_ID --force   # ⚠ 首先确认

# 查找项目 ID
ax projects list -l 100 -o json --space "my-workspace"
```

---

## API 密钥

> **作用域**：`ax api-keys list` 仅返回 **经过身份验证的用户** 拥有的密钥。对于组织级审计，请使用 Arize UI（设置 > API 密钥）。

```bash
ax api-keys list
ax api-keys list --key-type SERVICE --status ACTIVE -o json

# 用户密钥——作为创建者身份验证，继承其完整权限
ax api-keys create --name "CI pipeline" --expires-at "2027-01-01T00:00:00"

# 服务密钥——机器人用户通过 --assignments JSON 作用域到组织/空间
#（推荐用于 CI/CD 管道；从 `ax organizations list -o json` 获取 ORG_ID）
ax api-keys create-service-key \
  --name "team-alpha-traces" \
  --assignments '[{"org_id": "ORG_ID", "spaces": [{"space": "team-alpha"}]}]' \
  --expires-at "2027-01-01T00:00:00"

ax api-keys revoke KEY_ID --force   # ⚠ 首先确认——立即使密钥失效

# 零停机时间旋转——撤销旧密钥，生成具有相同作用域的新密钥
ax api-keys refresh KEY_ID
ax api-keys refresh KEY_ID --expires-at "2028-01-01T00:00:00"
```

> **原始密钥仅显示一次。** 立即将其保存到您的密钥管理器中。它无法再检索。

**`create-service-key` 标志：**

| 标志 | 是否必需 | 描述 |
|------|----------|-------------|
| `--name` | 是 | 密钥名称 |
| `--assignments` | 是 | 包含 org/space 分配的机器人用户的 JSON 数组（或指向 JSON 文件的路径）：`[{"org_id": "<id>", "role": "<org-role>", "spaces": [{"space": "<name-or-id>", "role": "<space-role>"}]}]`。在两个级别上 `role` 都是可选的——省略的角色在级别上默认为 `space=MEMBER`，`org=READ_ONLY`。自定义角色使用 `{"type": "CUSTOM", "id": "<role-id>"}`。 |
| `--account-role` | 否 | 机器人用户的账户级角色：`ADMIN`、`MEMBER` 或 `ANNOTATOR`（默认 `MEMBER`） |
| `--expires-at` | 否 | ISO 8601 过期日期 |
| `--description` | 否 | 可选描述 |

通过 `--assignments` 完全作用域 `create-service-key`，而不是通过单独的 `--space`/`--space-role`/`--org-role` 标志。

---

## 项目

项目存在于空间内，并包含跟踪、数据集和实验。

```bash
ax projects list --space SPACE
ax projects list --space SPACE --name "playground"   # 子字符串过滤
ax projects list --space SPACE -l 100 -o json        # 获取 base64 ID

ax projects get NAME_OR_ID --space SPACE

ax projects create --name "my-project" --space SPACE

ax projects update NAME_OR_ID --name "new-project-name" --space SPACE

ax projects delete NAME_OR_ID --space SPACE --force   # ⚠ 首先确认——删除所有跟踪和数据集
```

> **注意**：项目 ID（base64 字符串）由 `ax spans export`、`ax traces export` 和 `ax resource-restrictions` 使用。如果命令拒绝项目名称，请从 `ax projects list -o json` 查找 `id` 字段并使用该值。

---

## 企业工作流与故障排除

逐步工作流（入职团队、SAML/SSO 映射、项目限制、注销、多租户密钥）和故障排除表在 [references/REFERENCE.md](references/REFERENCE.md) 中。

---

## 相关技能

- **arize-instrumentation**：在空间准备好后，在 LLM 应用中设置跟踪。
- **arize-trace**：导出和检查管理空间内的跟踪。
- **arize-dataset**：在工作空间内创建和管理数据集。
