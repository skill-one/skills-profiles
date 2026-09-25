# 平台管理员技能

使用此技能管理 Coralogix 中的访问权限、身份验证和授权。它涵盖 API 密钥管理、角色和范围定义、用户管理、团队组以及 IP 访问限制。

---

## 破坏性操作安全

所有写操作（创建、更新、删除、设置 IDP、设置激活、设置状态）都需要交互式确认。CLI 将在执行前提示。要在脚本中跳过提示，请传递 `--yes`。

**重要提示：切勿在未经明确用户批准的情况下传递 `--yes`。** 在执行任何写操作之前：
1. 向用户描述确切的操作（将创建/修改/删除的内容）
2. 等待用户确认
3. 然后使用 `--yes` 执行

只读操作（列出、获取、搜索、系统、sp-params、send-data-keys）不需要确认，可以自由运行。

### 只读模式

使用 `--read-only`（或 `CX_READ_ONLY=1`）在 CLI 层面阻止所有写操作。这对于安全探索很有用——您可以查询任何 IAM 资源，而不用担心意外修改。

### 代理模式

在 AI 代理（Claude Code、Cursor、Codex 等）中运行时，cx 会自动检测代理环境，并在写操作上快速失败，而不是在 stdin 提示上挂起。错误信息指示您首先获取用户确认，然后重新运行 `--yes`。

---

## CLI 命令

### API 密钥

| 命令 | 目的 |
|---|---|
| `cx iam api-keys list` | 列出所有 API 密钥 |
| `cx iam api-keys get <id>` | 获取单个 API 密钥 |
| `cx iam api-keys create --from-file` | 创建 API 密钥 |
| `cx iam api-keys update --from-file <id>` | 更新 API 密钥 |
| `cx iam api-keys delete <id>` | 删除 API 密钥 |
| `cx iam api-keys send-data-keys` | 列出 send-data API 密钥 |
| `cx iam api-keys admin list` | 列出所有团队成员的密钥 |
| `cx iam api-keys admin delete --ids <id1> <id2>` | 批量删除密钥 |
| `cx iam api-keys admin set-status --ids <id1> --active true/false` | 激活/停用密钥 |

### 角色 & 范围

| 命令 | 目的 |
|---|---|
| `cx iam roles list` | 列出自定义角色 |
| `cx iam roles get <id>` | 获取角色定义 |
| `cx iam roles create --from-file` | 创建自定义角色 |
| `cx iam roles update --from-file <id>` | 更新自定义角色 |
| `cx iam roles delete <id>` | 删除自定义角色 |
| `cx iam roles system` | 列出系统（内置）角色 |
| `cx iam scopes list` | 列出所有范围 |
| `cx iam scopes get <id>` | 获取范围定义 |
| `cx iam scopes create --from-file` | 创建范围 |
| `cx iam scopes update --from-file` | 更新范围 |
| `cx iam scopes delete <id>` | 删除范围 |

### 用户 & 组

| 命令 | 目的 |
|---|---|
| `cx iam users search` | 搜索用户（可选 `--query`, `--status`） |
| `cx iam users get <user-id>` | 获取单个用户 |
| `cx iam users create --from-file` | 创建用户 |
| `cx iam users update --from-file` | 更新用户 |
| `cx iam users set-status --user-ids <id> --status ACTIVE/INACTIVE` | 激活/停用用户 |
| `cx iam groups list` | 列出所有团队组 |
| `cx iam groups get <id>` | 通过 ID 获取组 |
| `cx iam groups get-by-name <name>` | 通过名称获取组 |
| `cx iam groups users <group-id>` | 列出组中的用户 |
| `cx iam groups create --from-file` | 创建组 |
| `cx iam groups update --from-file <id>` | 更新组 |
| `cx iam groups delete <id>` | 删除组 |

### IP 访问

| 命令 | 目的 |
|---|---|
| `cx iam ip-access get` | 获取 IP 访问设置 |
| `cx iam ip-access create --from-file` | 创建 IP 访问规则 |
| `cx iam ip-access update --from-file` | 更新 IP 访问规则 |
| `cx iam ip-access delete` | 删除 IP 访问设置 |

所有命令支持 `-o json` 用于结构化输出和 `-p <profile>` 用于配置文件选择。

---

## 访问审计工作流

使用此工作流生成全面的访问报告：

### 第 1 步：列出所有用户

```bash
cx iam users search -o json
cx iam users search -o json | jq '[.[] | {id, name: .user_name, status, role_ids}]'
```

### 第 2 步：列出角色

```bash
cx iam roles list -o json
cx iam roles system -o json
```

交叉引用用户角色 ID 与角色定义，以了解权限。

### 第 3 步：列出组及成员关系

```bash
cx iam groups list -o json
cx iam groups list -o json | jq '[.[] | {id, name, member_count: (.members | length)}]'
```

对于每个组，检查成员：

```bash
cx iam groups users <group-id> -o json
```

### 第 4 步：盘点 API 密钥

```bash
cx iam api-keys list -o json
cx iam api-keys admin list -o json
cx iam api-keys send-data-keys -o json
```

识别旧或未使用的密钥：

```bash
cx iam api-keys list -o json | jq '[.[] | {id, name, created_at, active}] | sort_by(.created_at)'
```

### 第 5 步：检查 IP 限制

```bash
cx iam ip-access get -o json
```

### 第 6 步：交叉引用

生成摘要：哪些用户具有管理员角色，哪些 API 密钥已过时，哪些组具有广泛访问权限。

---

## API 密钥轮换

安全的密钥轮换工作流：

1. **列出当前密钥：** `cx iam api-keys list -o json`
2. **识别要轮换的密钥：** 按年龄或名称筛选
3. **创建替换密钥：** `cx iam api-keys create --from-file new-key.json --yes`（在用户批准后）
4. **将新密钥** 部署到所有使用旧密钥的系统
5. **验证新密钥** 在所有集成中是否正常工作
6. **删除旧密钥：** `cx iam api-keys delete <old-key-id> --yes`（在用户批准后）

> **警告：** 在替换密钥部署并验证之前，切勿删除 API 密钥。删除活动密钥会立即中断所有使用它的集成。

---

## 安全提示

> **删除 API 密钥** 会立即中断使用该密钥的任何集成。始终先创建替换密钥。

> **停用用户** (`cx iam users set-status --status INACTIVE`) 立即生效。用户将失去访问权限，没有宽限期。

> **删除 IP 访问规则** (`cx iam ip-access delete`) 会立即移除所有 IP 限制，可能暴露账户。

---

## 关键原则

- **修改前审计** - 在进行更改前运行完整的访问审计工作流
- **切勿在未创建替换的情况下删除密钥** - 创建新密钥 → 部署 → 验证 → 删除旧密钥
- **使用 `-o json` 生成结构化报告** - 启用 jq 过滤以进行精确的访问分析
- **跨环境审计使用多配置文件** - 使用 `-p <profile>` 或 `--all-profiles` 审计 staging + 生产
- **从现有模板创建** - `cx iam roles get <id> -o json > role.json` 在创建新角色之前

---

## 相关技能

- **`cx-cost-optimization`** - 查看哪些 API 密钥正在使用，以及它们是否仍然需要
