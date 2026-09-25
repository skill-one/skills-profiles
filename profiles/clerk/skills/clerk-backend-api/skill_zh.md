## 选项上下文

用户提示：$ARGUMENTS

## 关键：每次写入请求前必须执行的强制检查

在进行任何 POST / PATCH / PUT / DELETE 之前，您必须在响应中执行所有以下操作：

1. **检查 CLERK_SECRET_KEY** — 验证它是否已设置：
   ```bash
   echo $CLERK_SECRET_KEY | head -c 10
   ```
   如果为空，请停止并询问用户。没有有效的密钥不要继续。

2. **检查 CLERK_BAPI_SCOPES** — 运行：
   ```bash
   echo $CLERK_BAPI_SCOPES
   ```
   检查输出。如果范围缺失或不包括所需的写入权限，请告知用户：*"这是一个写入操作，您当前的权限可能不允许。重新运行并使用 --admin 跳过吗？"* 不要尝试请求并失败 — 先询问。

3. **对于 DELETE 请求：** 明确警告该操作是**不可逆的**，并列出将永久销毁的确切数据（用户记录、所有会话、所有成员资格、所有关联数据）。在进行下一步之前需要明确确认。此警告是**强制性的** — 永远不要跳过它。

4. **对于元数据操作：** 始终解释正在使用的元数据类型以及原因（见下方的元数据类型部分）。

---

## 快速路径：常见操作（直接使用，无需获取规范）

对于以下操作，跳过规范获取，并使用这些精确模板立即执行。根据用户上下文替换 `$CLERK_SECRET_KEY`、`$USER_ID`、`$ORG_ID`、`$EMAIL`。

### 创建组织 + 邀请成员（两步）

```bash
# 第一步 — 创建组织
ORG=$(curl -s -X POST "https://api.clerk.com/v1/organizations" \
  -H "Authorization: Bearer $CLERK_SECRET_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"Acme Corp\", \"created_by\": \"$USER_ID\"}")
echo "$ORG" | python3 -c "import sys,json; d=json.load(sys.stdin); print(json.dumps(d, indent=2))"

# 第二步 — 提取组织 ID
ORG_ID=$(echo "$ORG" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# 第三步 — 使用角色邀请成员
curl -s -X POST "https://api.clerk.com/v1/organizations/${ORG_ID}/invitations" \
  -H "Authorization: Bearer $CLERK_SECRET_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"email_address\": \"user@example.com\", \"role\": \"org:admin\"}" \
  | python3 -c "import sys,json; print(json.dumps(json.load(sys.stdin), indent=2))"
```

**角色：** 使用 `"org:admin"` 或 `"org:member"`（始终以 `org:` 开头）。

### SDK 对应（适用于 Next.js / TypeScript 项目使用 `@clerk/nextjs` 或 `@clerk/backend`）

```typescript
import { clerkClient } from '@clerk/nextjs/server'
// 或者如果直接使用 @clerk/backend：
// import { createClerkClient } from '@clerk/backend'
// const clerkClient = createClerkClient({ secretKey: process.env.CLERK_SECRET_KEY })

// 第一步：创建组织
const org = await clerkClient.organizations.createOrganization({
  name: 'Acme Corp',
  createdBy: userId,  // 必须的 — 创建组织的用户 ID
})

// 第二步：邀请成员到组织
const invitation = await clerkClient.organizations.createOrganizationInvitation({
  organizationId: org.id,
  emailAddress: 'user@example.com',
  role: 'org:admin',  // 或 'org:member'
})
```

### 更新用户元数据

**始终在使用哪种元数据之前解释三种元数据类型：**

| 类型 | 字段 | 可被谁读取 | 可被谁写入 | 用于 |
|------|-------|-------------|-------------|---------|
| 公开 | `public_metadata` | 客户端 + 服务器 | **服务器仅** | 前端读取的计划层级、角色、功能标志 |
| 私有 | `private_metadata` | **服务器仅** | **服务器仅** | Stripe ID、合规标志、内部标识符 |
| 不安全 | `unsafe_metadata` | 客户端 + 服务器 | 客户端 + 服务器 | 临时 UI 状态、入职步骤（客户端可写 — 避免敏感数据） |

**对于 `plan: 'pro'` 和 `onboarded: true` — 使用 `public_metadata`**（前端可读，服务器可写）：

```bash
curl -s -X PATCH "https://api.clerk.com/v1/users/${USER_ID}" \
  -H "Authorization: Bearer $CLERK_SECRET_KEY" \
  -H "Content-Type: application/json" \
  -d '{"public_metadata": {"plan": "pro", "onboarded": true}}' \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Updated user {d[\"id\"]}: public_metadata={d.get(\"public_metadata\")}')"
```

**SDK 对应：**

```typescript
import { clerkClient } from '@clerk/nextjs/server'
// 或者：import { createClerkClient } from '@clerk/backend'

await clerkClient.users.updateUser(userId, {
  publicMetadata: { plan: 'pro', onboarded: true },   // 可被客户端读取，服务器仅可写
  // privateMetadata: { stripeId: 'cus_xxx' },         // 服务器仅可读和可写
  // unsafeMetadata: { step: 'welcome' },              // 客户端可写，避免敏感数据
})
```

**注意：** REST API 使用 `snake_case` (`public_metadata`)。SDK 使用 `camelCase` (`publicMetadata`)。

### 列出用户（最近 7 天）

```bash
curl -s "https://api.clerk.com/v1/users?limit=100&offset=0&order_by=-created_at&created_at=gt:$(date -d '7 days ago' +%s 2>/dev/null || date -v-7d +%s)000" \
  -H "Authorization: Bearer $CLERK_SECRET_KEY" \
  | python3 -c "
import sys, json
data = json.load(sys.stdin)
if isinstance(data, list):
    print(f'Found {len(data)} users:')
    for u in data:
        print(f'  {u[\"id\"]}: {u.get(\"email_addresses\", [{}])[0].get(\"email_address\", \"no email\")}')
else:
    print(json.dumps(data, indent=2))
"
```

### 删除用户（需要确认）

```bash
# 仅在用户明确确认后运行
curl -s -X DELETE "https://api.clerk.com/v1/users/${USER_ID}" \
  -H "Authorization: Bearer $CLERK_SECRET_KEY" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'Deleted: {d}')"
```

---

## Clerk 后端 API — 完整端点参考

基础 URL：`https://api.clerk.com/v1`
认证：每次请求都在 `Authorization: Bearer $CLERK_SECRET_KEY`。

### 用户

**列出用户**
```
GET /v1/users
查询参数：limit (最大 500，默认 10)，offset，order_by (+/-created_at, +/-updated_at, +/-email_address, +/-web3wallet, +/-first_name, +/-last_name, +/-phone_number, +/-username, +/-last_active_at, +/-last_sign_in_at)，email_address[]，phone_number[]，username[]，web3wallet[]，user_id[]，query，created_at (ISO 8601 范围：gt:TIMESTAMP 或 lt:TIMESTAMP 以 Unix ms 表示)
返回：用户对象数组
```

**获取用户**
```
GET /v1/users/{user_id}
返回：用户对象
```

**更新用户**
```
PATCH /v1/users/{user_id}
正文 (JSON, snake_case)：{ public_metadata, private_metadata, unsafe_metadata, first_name, last_name, username, ... }
```

**删除用户 — 不可逆**
```
DELETE /v1/users/{user_id}
销毁：用户记录、所有会话、所有成员资格、所有关联数据
返回：{ id, object, deleted: true }
```
始终警告用户这是永久性的，并在进行下一步之前确认。

### 组织

**创建组织**
```
POST /v1/organizations
正文：{ name: string, created_by: string (user_id)，public_metadata？，private_metadata？，max_allowed_memberships？ }
返回：组织对象，包含 { id, name, slug, ... }
```

**列出组织**
```
GET /v1/organizations
查询参数：limit，offset，query，order_by
```

**邀请成员**
```
POST /v1/organizations/{organization_id}/invitations
正文：{ email_address: string, role: string ("org:admin" 或 "org:member")，public_metadata？，private_metadata？ }
返回：组织邀请对象
```

---

## 如何执行请求

**始终使用直接 `curl` 命令执行请求。** 使用规范提取脚本 (`api-specs-context.sh`，`extract-tags.js`，`extract-endpoint-detail.sh`) 来发现端点，但实际 API 调用使用 `curl`。不要使用 `scripts/execute-request.sh` — 它是本地开发辅助工具，不是代理使用。

GET 请求模板：
```bash
curl -s "https://api.clerk.com/v1${PATH}${QUERY_STRING}" \
  -H "Authorization: Bearer $CLERK_SECRET_KEY"
```

POST/PATCH 请求模板：
```bash
curl -s -X ${METHOD} "https://api.clerk.com/v1${PATH}" \
  -H "Authorization: Bearer $CLERK_SECRET_KEY" \
  -H "Content-Type: application/json" \
  -d '${BODY_JSON}'
```

DELETE 请求模板：
```bash
curl -s -X DELETE "https://api.clerk.com/v1${PATH}" \
  -H "Authorization: Bearer $CLERK_SECRET_KEY"
```

**获取响应后：** 清晰地解析并显示。使用 `python3 -c "import sys,json; data=json.load(sys.stdin); print(json.dumps(data, indent=2))"` 来美化 JSON。提取关键字段（id、email、name、等）并总结给用户。

---

## API 规范上下文

在进行 FAST PATH 之外的操作之前，通过运行以下命令获取可用规范版本和标签：
```bash
bash scripts/api-specs-context.sh
```

使用输出确定最新版本和可用标签。

**缓存：** 如果您在此对话中之前获取了规范上下文，不要再次获取。重用之前的版本和标签。

---

## 规则

- 对于常见操作（列出用户、创建组织、邀请、更新元数据、删除用户）：使用上面的 FAST PATH — 不要先获取规范。
- 始终忽略与 `platform` 相关的端点/模式。
- 始终在进行写入请求（POST/PUT/PATCH/DELETE）之前确认。
- 对于 DELETE 操作，始终警告用户该操作是**不可逆的**，并提及将丢失哪些数据（用户记录、会话、成员资格）。此警告是**强制性的** — 永远不要跳过它。
- 对于写入操作（POST/PUT/PATCH/DELETE），在尝试请求之前检查 `CLERK_BAPI_SCOPES`。如果缺失或不足，请先询问用户。不要尝试并失败 — 在执行前询问。此检查是**强制性的**。
- 对于元数据操作，始终解释三种类型（公开、私有、不安全），并推荐合适的类型。
- 分页：始终使用 `limit` + `offset`，并提及对于大型数据集结果可能会分页。
- 使用直接 curl 命令进行所有 API 调用 — 永远不要使用 `scripts/execute-request.sh`。

---

## 率限制和注意事项

### 率限制

| 环境 | 限制 |
|-------------|-------|
| 生产 | 1,000 请求 / 10 秒 |
| 开发 | 100 请求 / 10 秒 |
| 单个邀请 | 100 / 小时 |
| 批量邀请 | 25 / 小时 |
| 组织邀请 | 250 / 小时 |
| 前端 API 登录创建 | 5 / 10 秒 |
| 前端 API 登录尝试 | 3 / 10 秒 |
| 列出用户每页最大值 | 500 |

`currentUser()` 进行真实的 API 调用，这会消耗率限制。使用 `auth()` 仅获取会话声明 — 它从令牌中读取，无需 API 调用。

### 元数据覆盖（不是合并）

`updateUser({ publicMetadata: { role: 'admin' } })` 替换所有公开元数据，而不是合并。要添加字段而不丢失现有数据：先读取，展开，然后写入。

错误：
```typescript
await clerkClient.users.updateUser(userId, { publicMetadata: { newField: 'value' } })
```
这会删除所有其他 `publicMetadata` 字段。

正确：
```typescript
const user = await clerkClient.users.getUser(userId)
await clerkClient.users.updateUser(userId, {
  publicMetadata: { ...user.publicMetadata, newField: 'value' },
})
```

---

## 模式

根据 [选项上下文](#options-context) 中的用户提示确定活动模式：

| 模式 | 触发 | 行为 |
|------|---------|----------|
| `help` | 提示为空，或包含 `help` / `-h` / `--help` | 打印使用示例（步骤 0） |
| `browse` | 提示是 `tags`，或标签名称（例如 `Users`） | 列出所有标签或标签的端点 |
| `execute` | 特定端点（例如 `GET /users`）或自然语言操作（例如 "get user john_doe"） | 查找端点，执行请求 |
| `detail` | 端点 + `help` / `-h` / `--help`（例如 `GET /users help`） | 显示端点模式，不执行 |

---

## 你的任务

默认使用 [API 规范上下文](#api-specs-context) 中的**最新版本**。如果用户指定了不同版本（例如 `--version 2024-10-01`），则使用该版本。

确定活动模式，然后按照下面的适用步骤执行。

---

### 0. 打印使用

**模式：** `help` 仅 — 对于 `browse`、`execute` 和 `detail` 跳过。

将以下示例原封不动地打印给用户：

```
浏览
  /clerk-backend-api tags                         — 列出所有标签
  /clerk-backend-api Users                        — 浏览 Users 标签的端点
  /clerk-backend-api Users version 2025-11-10.yml — 使用不同版本浏览

执行
  /clerk-backend-api GET /users             — 获取所有用户
  /clerk-backend-api get user john_doe      — 自然语言也有效
  /clerk-backend-api POST /invitations      — 创建邀请

检查
  /clerk-backend-api GET /users help        — 显示端点模式而不执行
  /clerk-backend-api POST /invitations -h   — 查看请求/响应详细信息

选项
  --admin                            — 跳过分段限制，用于写入/删除
  --version [日期]，version [日期]   — 使用特定规范版本
  --help, -h, help                   — 检查端点而不是执行
```

到这里停止。

---

### 1. 获取标签

**模式：** `browse`（当提示是 `tags` 或未指定标签）— 对于 `help`、`execute` 和 `detail` 跳过。

如果使用非最新版本，获取该版本的标签：
```bash
curl -s https://raw.githubusercontent.com/clerk/openapi-specs/main/bapi/${version_name} | node scripts/extract-tags.js
```
否则，使用 [API 规范上下文](#api-specs-context) 中已有的**标签**。

将标签以表格形式分享，并提示用户选择查询。

---

### 2. 获取标签端点

**模式：** `browse`（当提供标签名称时）— 对于 `help`、`execute` 和 `detail` 跳过。

获取标识标签的所有端点：
```bash
curl -s https://raw.githubusercontent.com/clerk/openapi-specs/main/bapi/${version_name} | bash scripts/extract-tag-endpoints.sh "${tag_name}"
```

将结果（端点、模式、参数）与用户分享。

---

### 3. 获取端点详细信息

**模式：** `execute`、`detail` — 对于 `help` 和 `browse` 跳过。

对于 `execute` 模式中的自然语言提示，首先检查操作是否匹配上方的 FAST PATH 条目。如果匹配，跳过此步骤，并直接使用 FAST PATH 模板进入步骤 4。

对于其他端点，通过在上下文中搜索标签来识别匹配的端点。如果需要，获取标签端点以解析确切的路径和方法。

提取完整的端点定义：
```bash
curl -s https://raw.githubusercontent.com/clerk/openapi-specs/main/bapi/${version_name} | bash scripts/extract-endpoint-detail.sh "${path}" "${method}"
```
- `${path}` — 例如 `/users/{user_id}`
- `${method}` — 小写，例如 `get`

**`detail` 模式：** 与用户分享端点定义和模式。在这里停止。

**`execute` 模式：** 继续到步骤 4。

---

### 4. 执行请求

**模式：** `execute` 仅。

1. 运行上述 CRITICAL 部分的**强制检查**。
2. 从规范（步骤 3）或 FAST PATH 识别所需和可选参数。
3. 询问用户任何未提供的必需路径/查询/正文参数。
4. 构建并执行**直接 curl 命令**（见上方如何执行请求）。不要使用 `scripts/execute-request.sh`。
5. 解析 JSON 响应并清晰显示。提取并总结关键字段给用户。

**示例 — 列出用户并解析响应：**
```bash
RESPONSE=$(curl -s "https://api.clerk.com/v1/users?limit=10" \
  -H "Authorization: Bearer $CLERK_SECRET_KEY")
echo "$RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
if isinstance(data, list):
    print(f'Found {len(data)} users:')
    for u in data:
        print(f'  {u[\"id\"]}: {u.get(\"email_addresses\", [{}])[0].get(\"email_address\", \"no email\")}')
else:
    print(json.dumps(data, indent=2))
"
```

## 参见

- `clerk-setup` - 初始 Clerk 安装
- `clerk-orgs` - 通过 API 管理组织
- `clerk-webhooks` - 实时事件同步
