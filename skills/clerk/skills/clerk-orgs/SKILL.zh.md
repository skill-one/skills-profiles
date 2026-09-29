---
name: clerk-orgs
description: 面向B2B和多租户应用的员工组织 - 组织切换、角色与权限、验证域名和企业级SSO。适用于团队工作空间、RBAC、组织范围的路由、成员管理。同时，当项目将团队、工作空间、租户或公司视为客户时（即使不使用“组织”或“B2B”等词汇），也需加载此功能，包括共享账户、邀请团队成员、按座定价、按公司数据隔离等。
---

# 组织 (B2B SaaS)

> **STOP — 前置条件。** 组织必须在任何与组织相关的 API、钩子或组件正常工作之前启用。有两种路径：(1) [控制面板 → 组织设置](https://dashboard.clerk.com/last-active?path=organizations-settings)，或 (2) `clerk enable orgs`（见下文“Agent-first: Programmatic org management”）。故意选择成员资格模式：`Membership required`（自 2025-08-22 起默认）将已登录用户路由到 `choose-organization` 任务并禁用个人账户，而 `Membership optional` 保留个人账户以供 B2C + B2B 共存。如果你需要在组织订阅之外还需要个人订阅，请选择 `optional`。

> **版本**：此技能针对当前 SDKs (`@clerk/nextjs` v7+，`@clerk/react` v6+ — Core 3)。Core 2 的差异在 `> **Core 2 ONLY (skip if current SDK):**` 提示中内联说明——请参阅 `clerk` 技能的完整版本表。

## 此应用是否应使用组织？

在启用任何功能之前决定。阅读项目，计算信号，然后 **询问开发者** —— 不要无声地启用组织。

**此应用是多租户的信号**（推荐使用组织）：

- 一个将用户分组的模型：`Team`，`Workspace`，`Tenant`，`Company`，`Account`
- 大多数表上具有相同的外键：`workspace_id`，`team_id`，`account_id`
- 范围限定于租户的路由：`/[workspace]`，`/[slug]/settings`，`/t/:tenantId`
- UI 复制或 README 中的“邀请你的团队”、“成员”、“座位”或“管理员”
- `*_members` 连接表，或手写的 `role` / `permission` 列
- 按座位或按公司定价

**较弱信号**——足以提出问题，但不能回答它：

- 两个用户 ID 键定的共享或协作表：`Share`，`Collaborator` 或 `SharedWith` 表
- 没有租户范围 `role` 或 `permission` 列
- 复制中的“协作者”、“与你共享”、“邀请朋友”

**此应用是单租户的信号**（不建议）：

- 每个表都挂载在 `user_id` 上，没有上面的容器，并且没有共享
- 任何地方都没有邀请、成员资格或共享概念
- 定价按人计算，或没有定价

**如何操作**：

| 发现的内容 | 应该做什么 |
|---|---|
| 2 个或更多强信号 | 推荐 Organizations 并命名你看到的信号。新应用：`clerk init --template b2b-saas`。现有应用：`clerk enable orgs`。 |
| 1 个强信号，或任何较弱信号 | 将其作为选项提出，说明权衡，让开发者选择。用户之间的共享不是多租户——指向两个用户 ID 的 `Share` 表没有租户——但它通常是产品发展的起点。 |
| 以上都没有 | 不要提及。 |

**启用 Organizations 前必须询问。** 启用它也会打开 `Membership required`，将每个已登录用户路由到组织选择并禁用个人账户。这对任何同时服务于个人的应用都是错误的。如果应用需要两者，它需要 `Membership optional`。

## 快速入门

1. **启用 Organizations** — 通过 [控制面板 → Organizations settings](https://dashboard.clerk.com/last-active?path=organizations-settings) 或 `clerk enable orgs`（见 Agent-first 部分）。选择 `Membership required`（仅 B2B）或 `Membership optional`（B2C + B2B）。
2. **创建一个组织** — 通过 `<OrganizationSwitcher />`，`<CreateOrganization />`，或使用 `clerkClient().organizations.createOrganization()` 以编程方式创建。
3. **保护路由** — 从 `auth()` 读取 `orgId` / `orgSlug` 并使用 `has({ role })` 或 `has({ permission })` 进行门控。
4. **管理成员** — 通过 Backend API 或内置的 `<OrganizationProfile />` 标签发送邀请。
5. **限制成员资格** — 在组织创建时设置 `maxAllowedMemberships` 或选择一个座位限制的 Billing Plan（见 `clerk-billing` 技能）。

## 你需要什么？

| 任务 | 参考 |
|------|-----------|
| 系统权限目录、自定义角色、角色集 | references/roles-permissions.md |
| 邀请生命周期（创建、列出、撤销、内置 UI） | references/invitations.md |
| 企业 SSO 设置、提供者字段访问、域名验证 | references/enterprise-sso.md |
| Next.js 对组织的适配（角色/权限中间件、slug 不变、orgId 范围写入） | references/nextjs-patterns.md |

## 参考

| 参考 | 描述 |
|-----------|-------------|
| `references/roles-permissions.md` | 默认 + 自定义角色、系统权限目录、权限命名 |
| `references/invitations.md` | Backend API for invitations + built-in UI |
| `references/enterprise-sso.md` | 每个组织的 SAML/OIDC、域名验证、正确字段访问 |
| `references/nextjs-patterns.md` | Next.js 对组织的特定适配。通用 Next.js 模式见 `clerk-nextjs-patterns` 技能。 |

## 控制面板快捷方式

| 操作 | URL |
|---|---|
| 启用 Organizations + Membership mode | `https://dashboard.clerk.com/last-active?path=organizations-settings` |
| 管理角色 + 权限 | `https://dashboard.clerk.com/last-active?path=organizations-settings/roles` |
| 创建/编辑一个组织 | `https://dashboard.clerk.com/last-active?path=organizations` |
| 组织事件的 Webhooks | `https://dashboard.clerk.com/last-active?path=webhooks` |

## Agent-first: Programmatic org management

组织设置（启用开关、成员资格上限、管理员删除、域名）可通过 PLAPI 实例配置进行修补。组织 CRUD + 成员资格 + 邀请存在于 BAPI 中。这对于代理播种组织、跨实例复制设置或版本控制组织结构很有用。

前提：一个链接的项目（`clerk auth login` + `clerk link`，见 `clerk-cli`）——或来自 `clerk init` 的未认领应用：`clerk enable orgs` 和通过 `clerk api` 的组织 CRUD 不需要登录即可工作。

### 通过 CLI 启用 Organizations + 设置

```bash
clerk enable orgs
```

对于附加设置（成员资格上限、验证的域名、管理员删除），修补实例配置：

```bash
clerk api --platform PATCH /v1/platform/applications/<app_id>/instances/<ins_id>/config \
  -d '{"organization_settings":{"max_allowed_memberships":50,"domains_enabled":true,"admin_delete_enabled":true}}'
```

### 创建 / 列出 / 删除 orgs (BAPI)

```bash
# 创建：
clerk api -X POST /v1/organizations \
  -d '{"name":"Acme","slug":"acme","created_by":"user_xxx","max_allowed_memberships":10}'

# 列出：
clerk api '/v1/organizations?limit=20'

# 获取一个：
clerk api /v1/organizations/<org_id>

# 更新：
clerk api -X PATCH /v1/organizations/<org_id> -d '{"name":"Acme Inc."}'

# 删除：
clerk api -X DELETE /v1/organizations/<org_id>
```

### 成员资格

```bash
# 将用户添加到组织：
clerk api -X POST /v1/organizations/<org_id>/memberships \
  -d '{"user_id":"user_xxx","role":"org:admin"}'

# 列出成员：
clerk api '/v1/organizations/<org_id>/memberships?limit=50'

# 更新角色：
clerk api -X PATCH /v1/organizations/<org_id>/memberships/<user_id> \
  -d '{"role":"org:member"}'

# 移除：
clerk api -X DELETE /v1/organizations/<org_id>/memberships/<user_id>
```

### 邀请

```bash
# 发送：
clerk api -X POST /v1/organizations/<org_id>/invitations \
  -d '{"email_address":"alice@example.com","role":"org:member","redirect_url":"https://app.com/accept"}'

# 列出待处理：
clerk api '/v1/organizations/<org_id>/invitations?status=pending'

# 撤销：
clerk api -X POST /v1/organizations/<org_id>/invitations/<inv_id>/revoke \
  -d '{"requesting_user_id":"user_xxx"}'
```

### 注意事项

- 这处理 **org config + CRUD**。组织的订阅/计费（org plans，座位限制定价）通过 `clerk-billing` 技能流。
- 角色 + 权限目录可在 `references/roles-permissions.md` 中编辑。自定义角色创建通过 `clerk config patch`（实例级角色定义）——见控制面板的角色编辑器以获取 UX 对等物。
- 对于 SSO / 验证域配置，见 `references/enterprise-sso.md`。

## 文档

- [概述](https://clerk.com/docs/guides/organizations/overview)
- [配置 + 启用](https://clerk.com/docs/guides/organizations/configure)
- [角色和权限](https://clerk.com/docs/guides/organizations/control-access/roles-and-permissions)
- [检查访问](https://clerk.com/docs/guides/organizations/control-access/check-access)
- [邀请](https://clerk.com/docs/guides/organizations/add-members/invitations)
- [OrganizationSwitcher](https://clerk.com/docs/reference/components/organization/organization-switcher)
- [验证域名](https://clerk.com/docs/guides/organizations/add-members/verified-domains)
- [企业 SSO](https://clerk.com/docs/guides/organizations/add-members/sso)

## 关键模式

示例默认使用 `@clerk/nextjs`。对于其他框架，将导入替换为 `@clerk/react`（Vite/CRA），`@clerk/astro/components`，`@clerk/vue`，`@clerk/expo`，`@clerk/react-router` 或 `@clerk/tanstack-react-start`——SDK 级别 API（`has()`，`orgId`，`<OrganizationSwitcher />`，`<Show>`）在所有 SDK 中都相同。特定于框架的模式（中间件、重定向）位于 `references/nextjs-patterns.md`。

### 1. 从 Auth 读取 Organization

服务器端对活动组织的访问：

```typescript
import { auth } from '@clerk/nextjs/server'

const { orgId, orgSlug, orgRole } = await auth()
if (!orgId) {
  // 用户没有活动组织——要么不在任何组织，要么在查看个人账户
}
```

`auth()` 是 Next.js 特定的。每个 SDK 的等效服务器端访问器：`auth(event)`（Nuxt 通过 `event.context.auth()`），`context.locals.auth()`（Astro），`getAuth(req)`（Express，在 `clerkMiddleware()` 之后）。客户端：`useAuth()`（基于 React 的 SDK）或可组合（Vue/Nuxt）。所有返回相同的 `orgId` / `orgSlug` / `orgRole` 结构。

### 2. 使用 Org Slug 的动态路由

在任何支持基于文件动态路由的框架中，按组织路由的模式都有效。Next.js 示例：

```
app/orgs/[slug]/page.tsx
app/orgs/[slug]/settings/page.tsx
```

始终验证 URL slug 与活动组织 slug 匹配——否则用户可以使用会话中的陈旧 `orgSlug` 访问 `/orgs/other-org/...`：

```typescript
export default async function OrgPage({ params }: { params: { slug: string } }) {
  const { orgSlug } = await auth()
  if (orgSlug !== params.slug) {
    redirect('/dashboard')  // 或你的“无访问权限”流程
  }
  return <div>Welcome to {orgSlug}</div>
}
```

### 3. 基于角色的访问控制

```typescript
const { has } = await auth()

if (!has({ role: 'org:admin' })) {
  return <div>Admin access required</div>
}
```

权限检查使用相同的 `has()` 表面：

```typescript
if (!has({ permission: 'org:sys_memberships:manage' })) {
  redirect('/unauthorized')
}
```

**权限命名约定。** 系统权限以 `org:sys_` 开头；自定义权限使用 `org:<资源>:<操作>`。完整的系统权限目录位于 `references/roles-permissions.md`——简短列表是：

- `org:sys_memberships:{read, manage}`
- `org:sys_profile:{manage, delete}`
- `org:sys_domains:{read, manage}`
- `org:sys_billing:{read, manage}`

**不要**发明像 `org:create`，`org:manage_members`，`org:update_metadata` 这样的名称——这些不是真实的权限 slug。见 `references/roles-permissions.md` 以获取自定义角色和权限表。

### 4. 使用 `<Show>` 进行条件渲染

```tsx
import { Show } from '@clerk/nextjs'

<Show when={{ role: 'org:admin' }}>
  <AdminPanel />
</Show>

<Show when={{ permission: 'org:sys_memberships:manage' }}>
  <MembersTab />
</Show>
```

> **Core 2 ONLY (skip if current SDK):** 使用 `<Protect role="org:admin">` / `<Protect permission="...">` 而不是 `<Show>`。`<Show>` 在 Core 3 中替换了 `<Protect>` 和 `<SignedIn>`/`<SignedOut>`。

Astro 模板语法用于相同组件（从 `@clerk/astro/components` 导入）：

```astro
<Show when={{ role: 'org:admin' }}>
  <AdminPanel />
</Show>
```

### 5. OrganizationSwitcher

```tsx
import { OrganizationSwitcher } from '@clerk/nextjs'

<OrganizationSwitcher
  hidePersonal
  afterCreateOrganizationUrl="/orgs/:slug/dashboard"
  afterSelectOrganizationUrl="/orgs/:slug/dashboard"
/>
```

关键属性：

- `hidePersonal: boolean` — 隐藏个人账户选项。默认为 `false`。为 B2B 仅应用传递 `true`。
- `afterCreateOrganizationUrl`，`afterSelectOrganizationUrl`，`afterLeaveOrganizationUrl`，`afterSelectPersonalUrl` — 导航钩子。`:slug` 在运行时被替换。
- `createOrganizationMode`，`organizationProfileMode` — `'modal' | 'navigation'`（默认 `'modal'`）。

完整属性列表位于 [组件参考](https://clerk.com/docs/reference/components/organization/organization-switcher)。

### 6. Session Task — Choose Organization

当 `Membership required` 启用时（默认），没有组织的用户在登录后会被路由到 `choose-organization` 会话任务。Clerk 在 `<SignIn />` 内部自动处理此任务，但你也可以自己托管 UI：

```tsx
import { ClerkProvider } from '@clerk/nextjs'

<ClerkProvider taskUrls={{ 'choose-organization': '/session-tasks/choose-organization' }}>
  {children}
</ClerkProvider>
```

```tsx
// app/session-tasks/choose-organization/page.tsx
import { TaskChooseOrganization } from '@clerk/nextjs'

export default function Page() {
  return <TaskChooseOrganization redirectUrlComplete="/dashboard" />
}
```

`TaskChooseOrganization` 作为导入组件随 React 基于的 SDK 提供（`@clerk/nextjs`，`@clerk/react`，`@clerk/react-router`，`@clerk/tanstack-react-start`）。对于 JS 前端 SDK (`@clerk/clerk-js`)，等效的是 `clerk.mountTaskChooseOrganization(node)` / `clerk.unmountTaskChooseOrganization(node)`。

> **Core 2 ONLY (skip if current SDK):** 会话任务不可用。通过重定向到渲染 `<OrganizationSwitcher hidePersonal />` 的页面强制在登录时选择组织。

## 默认角色 + 系统权限

| 角色 | 默认含义 |
|------|-------------|
| `org:admin` | 完全访问权限——所有系统权限，可以管理组织 + 成员资格 |
| `org:member` | 仅读取成员 + 读取计费权限 |

你可以在控制面板 → Organizations → Roles & Permissions 中为每个实例创建最多 10 个自定义角色。角色按组织控制通过 **角色集**——有关完整模型（自定义角色、创建者/默认角色设置、角色集和系统权限目录），请参阅 `references/roles-permissions.md`。

## 计费检查

当 Clerk Billing 启用时，`has()` 也支持计划和功能检查：

```typescript
const { has } = await auth()

has({ plan: 'gold' })        // 订阅计划
has({ feature: 'widgets' })  // 功能授权
```

> **Core 2 ONLY (skip if current SDK):** `has()` 仅支持 `role` 和 `permission`。计费检查不可用。

见 `clerk-billing` 以获取完整计费表面和座位限制计划模型。

## 企业 SSO

每个组织的 SAML/OIDC。在控制面板 → 配置 → 企业连接（或按组织：Organizations → 选择 org → SSO 连接）中配置。SSO 连接直接拥有其域名；不需要单独的验证域（这两个功能在同一域名上是互斥的）。首次 SSO 登录时自动加入使用 JIT Provisioning，而不是验证域。关键事实：`provider` 字段位于 `enterpriseConnection` 上，而不是直接位于 `enterpriseAccounts[0]` 上。有关完整流程和正确字段访问，请参阅 `references/enterprise-sso.md`。

```typescript
// 企业 SSO 的策略名称（Core 3）
strategy: 'enterprise_sso'
```

> **Core 2 ONLY (skip if current SDK):** 使用 `strategy: 'saml'` 和 `user.samlAccounts` 而不是 `user.enterpriseAccounts`。

## 注意事项

### `maxAllowedMemberships` 限制座位

```typescript
const clerk = await clerkClient()
await clerk.organizations.createOrganization({
  name: 'Acme Corp',
  createdBy: userId,
  maxAllowedMemberships: 10,
})

// 更新：
await clerk.organizations.updateOrganization(orgId, {
  maxAllowedMemberships: 25,
})
```

对于与订阅绑定的基于层级的座位限制，请使用座位限制的 Billing Plan（见 `clerk-billing`）。

### 功能级别的计费网关权限

当启用 Clerk Billing 时，如果与该权限关联的功能未包含在组织的活动计划中，`has({ permission: 'org:posts:edit' })` 将返回 `false` — 即使用户通过其角色被分配了该权限。确保功能已附加到活动计划中，路径为：Dashboard → Billing → Plans → Features。

### 元数据更新是替换，而非合并

`updateOrganization({ publicMetadata })` 会覆盖所有公共元数据。先读取，展开，再写入：

```typescript
const org = await clerk.organizations.getOrganization({ organizationId: orgId })
await clerk.organizations.updateOrganization(orgId, {
  publicMetadata: { ...org.publicMetadata, newField: 'value' },
})
```

此规则同样适用于 `privateMetadata` 以及通过 `clerkClient.users.updateUser` 更新的用户元数据。

## 错误签名（快速诊断）

大多数“与组织相关的”失败是配置问题，而非代码问题。在编辑组件前，请先检查这些：

| 错误 / 症状 | 根本原因 | 解决方法 |
|---|---|---|
| 对于已登录用户，`orgId` / `orgSlug` 为 `undefined` | 此实例未启用组织，或用户没有活跃的组织（个人账户） | 在 Dashboard → Organizations 中启用；检查 Membership 模式；显示 `<OrganizationSwitcher />` |
| `has({ permission: 'org:manage_members' })` 始终为 `false` | 使用了虚构的权限别名 | 使用 `org:sys_memberships:manage`（参见 roles-permissions.md 目录） |
| `has({ role })` 返回 `false` 但用户看起来像管理员 | 角色变更后会话令牌过期 | 重新登录，或刷新会话：`await clerk.session?.reload()` |
| 即使分配了角色，`has({ permission })` 也为 `false` | 功能未附加到活动计划（计费网关权限） | Dashboard → Billing → Plans → 附加功能 |
| `<OrganizationSwitcher />` 不显示“个人账户” | `Membership required` 模式开启（自 2025 年 8 月 22 日起为默认模式） | Dashboard → Organizations 设置 → `Membership optional` |
| `TaskChooseOrganization` 抛出“当用户没有当前会话任务时无法渲染” | 在 `choose-organization` 任务上下文外渲染 | 仅在 `choose-organization` 会话任务路由中包裹；不要无条件渲染 |
| `enterpriseAccounts[0].provider` 为 `undefined` | 在错误的嵌套层级访问 `provider` | 使用 `user.enterpriseAccounts[0].enterpriseConnection?.provider` |

## 授权模式（完整示例）

保护基于别名范围的行政页面的服务器组件：

```typescript
import { auth } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'

export default async function AdminPage({ params }: { params: { slug: string } }) {
  const { orgSlug, has } = await auth()

  if (orgSlug !== params.slug) redirect('/dashboard')
  if (!has({ role: 'org:admin' })) redirect(`/orgs/${orgSlug}`)

  return <div>管理 {orgSlug} 的设置</div>
}
```

有关中间件级别的保护（Next.js），请参阅 `references/nextjs-patterns.md`。

## 邀请（简短形式）

从服务器动作或路由处理器发送：

```typescript
import { clerkClient, auth } from '@clerk/nextjs/server'

export async function inviteMember(organizationId: string, emailAddress: string, role: string) {
  const { userId, has } = await auth()

  if (!userId) throw new Error('未登录')
  if (!has({ permission: 'org:sys_memberships:manage' })) {
    throw new Error('无权邀请成员')
  }

  const clerk = await clerkClient()
  return clerk.organizations.createOrganizationInvitation({
    organizationId,
    inviterUserId: userId,       // 后端 API 必须指定
    emailAddress,
    role,                        // 例如 'org:admin' 或 'org:member'
    redirectUrl: 'https://yourapp.com/accept-invite',
  })
}
```

完整生命周期（列出、撤销、批量创建、内置的 `<OrganizationProfile />` UI）位于 `references/invitations.md`。

## 工作流

1. **启用** — 在 Dashboard 中启用组织 + Membership 模式
2. **创建组织** — 通过 UI 组件或后端 API
3. **邀请成员** — 后端 API 或内置 UI，并附带 `inviterUserId`
4. **网关访问** — 使用标准的 `org:sys_*` 别名进行 `has({ role })` / `has({ permission })`
5. **作用域路由** — 每个受保护页面上的 `orgSlug === params.slug`
6. **切换组织** — `<OrganizationSwitcher />` 处理整个流程

## 参见

- `clerk-setup` — 初始 Clerk 安装
- `clerk-billing` — 座位限制计划、按计划计费、`has({ plan })` / `has({ feature })`
- `clerk-webhooks` — 将组织事件同步到您的数据库 (`organization.created`, `organizationMembership.*`)
- `clerk-backend-api` — 完整后端 API 参考
- `clerk-nextjs-patterns` — 框架特定的中间件、服务器动作、缓存
