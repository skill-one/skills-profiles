---
name: clerk-billing
description: 用于订阅管理的出纳计费 - 渲染 Clerk 的 PricingTable 和应用内结账抽屉，配置订阅计划、B2B 座位限制计划，使用 has() 配置功能权限，以及计费 Webhook。用于 SaaS 盈利、计划门禁、结账流程、试用、开票和订阅生命周期管理。
---

# 账单

> **停止，先决条件。** 在使用任何 `<PricingTable />`、`<CheckoutButton />`、`has({ plan })` 或 `has({ feature })` 之前，必须先启用账单功能。有两种路径：(1) [控制面板 → 账单 → 设置](https://dashboard.clerk.com/last-active?path=billing/settings)，或 (2) `clerk enable billing`（见下文“Agent-first：程序化账单配置”）。启用后会自动创建默认的 `free_user` / `free_org` 计划。开发实例可以使用共享的 Clerk 开发网关（无需 Stripe 账户）；生产环境需要 Stripe 账户仅用于支付处理。
>
> **注意**：账单 API 仍处于实验阶段。请固定 `@clerk/nextjs` 和 `clerk-js` 包版本。有关支持的版本表，请参阅 `clerk` 技能。

## 快速入门

1. **启用账单**，通过 [控制面板 → 账单 → 设置](https://dashboard.clerk.com/last-active?path=billing/settings) 或 `clerk enable billing`（见 Agent-first 部分）。跳过此步骤会在开发环境中抛出 `cannot_render_billing_disabled`，在生产环境中渲染为空。
2. **在相应的选项卡中创建计划**，[控制面板 → 账单 → 计划](https://dashboard.clerk.com/last-active?path=billing/plans)。两个选项卡，每个选项卡的作用域为 slugs，创建后不可移动：
   - **用户计划** → `<PricingTable />`（默认 `for="user"`)
   - **组织计划** → `<PricingTable for="organization" />`

   错误的选项卡是 `<PricingTable />` 为空的首要原因。计划存储在 Clerk 中；不会同步到 Stripe。
3. **在计划中添加功能**，在控制面板 → 账单 → 计划中打开计划，使用其功能部分。功能的作用域为每个计划，不是全局的。相同的 slugs 可以附加到多个计划；`has({ feature: 'export' })` 如果活动计划包含该 slugs 则匹配。
4. **渲染 `<PricingTable />**`（为 B2B 传递 `for="organization"`）。
5. **使用 `has({ plan })` 或 `has({ feature })` 从 `auth()` 进行访问控制**。
6. **处理账单 webhook** 以管理订阅生命周期。

## 控制面板快捷方式

| 操作 | URL |
|---|---|
| 启用账单 | `https://dashboard.clerk.com/last-active?path=billing/settings` |
| 创建/编辑计划 | `https://dashboard.clerk.com/last-active?path=billing/plans` |
| 成员资格模式（B2C + B2B 共存） | `https://dashboard.clerk.com/last-active?path=organizations-settings` |
| 编辑功能 | 计划 → 点击一个计划 → 功能部分（没有直接 URL） |

## Agent-first：程序化账单配置

完整的账单配置（启用开关、计划、功能、计划-功能附件）可以通过 PLAPI 编辑，而无需接触控制面板。适用于代理播种计划、跨实例复制配置或版本控制账单结构。

前提：项目已链接到 Clerk 应用（`clerk auth login` + `clerk link`，见 `clerk-cli`）。账单仅限账户——与组织不同，它不能在未占用的应用上启用；先声明应用。

### 通过 CLI 启用账单

```bash
clerk enable billing                # 两个目标（默认，自动创建 free_user + free_org 计划）
clerk enable billing --for org      # 仅组织
clerk enable billing --for user     # 仅用户
```

### 拉取当前账单配置

```bash
clerk config pull --keys billing > billing.json
```

这将把链接实例的当前账单配置（开关 + 计划 + 功能）写入 `billing.json`。

### 编辑并应用

编辑 `billing.json` 以添加/删除计划或功能，然后预览差异并应用：

```bash
clerk config patch --file billing.json --dry-run
clerk config patch --file billing.json
```

传递 `--instance prod` 以针对生产实例而不是开发实例。

### 原始 PATCH（完全控制）

对于一次性计划/功能更新而无需配置文件：

```bash
clerk api --platform PATCH /v1/platform/applications/<app_id>/instances/<ins_id>/config \
  -d '{"billing":{"plans":[{"slug":"pro","name":"Pro","amount":2000,"currency":"usd","payer_type":"user","is_recurring":true}],"features":[{"slug":"export","name":"Export"}]}}'
```

### 注意事项

- 这处理的是**账单配置**（开关 + 计划 + 功能目录）。**订阅生命周期**（用户选择计划、结账、续订、取消）仍然通过 `<PricingTable />` + 账单 webhook 流程，见 `clerk-webhooks` 技能了解生命周期事件。
- 顶级 `features` 映射操作和计划-功能附件（同步）通过 PLAPI 账单配置处理器完全支持。

## 你需要什么？

| 任务 | 参考 |
|------|-----------|
| `<PricingTable />` 属性、`<CheckoutButton />`、`<Show>` 账单模式 | references/billing-components.md |
| B2C 模式（单个用户订阅，`Membership optional` 先决条件） | references/b2c-patterns.md |
| B2B 模式（组织订阅、座位限制计划、管理员控制账单 UI） | references/b2b-patterns.md |
| webhook 事件目录、有效负载形状、处理器模板 | references/billing-webhooks.md |

## 参考

| 参考 | 描述 |
|-----------|-------------|
| `references/billing-components.md` | `<PricingTable />` 和订阅 UI |
| `references/b2c-patterns.md` | B2C 订阅账单模式 |
| `references/b2b-patterns.md` | 使用组织订阅和座位限制计划的 B2B 账单 |
| `references/billing-webhooks.md` | 订阅生命周期事件处理 |

## 文档

- [账单概述](https://clerk.com/docs/guides/billing/overview)
- [B2B SaaS 账单](https://clerk.com/docs/guides/billing/for-b2b)
- [B2C SaaS 账单](https://clerk.com/docs/guides/billing/for-b2c)
- [账单 webhook](https://clerk.com/docs/guides/development/webhooks/billing)

## 功能与计划：何时使用哪个

**当限制特定功能时使用 `has({ feature: 'slug' })`**，导出、分析、API 访问、审计日志。

**当限制层级时使用 `has({ plan: 'slug' })`**，显示专业版仪表板、检查组织订阅级别、将免费用户重定向。

| 场景 | 正确检查 |
|----------|---------------|
| 限制“导出 CSV”按钮 | `has({ feature: 'export' })` |
| 限制“分析”部分 | `has({ feature: 'analytics' })` |
| 限制 `/dashboard/pro` | `has({ plan: 'pro' })` |
| 检查组织是否有团队订阅 | `has({ plan: 'org:team' })` |
| 限制 SSO 配置 | `has({ feature: 'sso' })` |

当用户说“限制导出功能”或“限制分析”时，始终使用 `has({ feature })`。仅在门限是计划层级本身而不是其内部特定功能时使用 `has({ plan })`。

## 关键模式

### 1. 渲染定价表

使用单个组件向用户显示可用计划：

```tsx
import { PricingTable } from '@clerk/nextjs'

export default function PricingPage() {
	return (
		<main>
			<h1>选择一个计划</h1>
			<PricingTable />
		</main>
	)
}
```

`<PricingTable />` 会自动渲染控制面板中配置的所有计划。选择计划会打开 Clerk 的应用内结账抽屉。基本使用无需传递属性。为 B2B 传递 `for="organization"` 以渲染组织级别的计划而不是用户计划。

### 2. 服务器端检查功能授权

通过单个功能进行门限，这是限制特定功能的推荐方法：

```typescript
import { auth } from '@clerk/nextjs/server'

export default async function AnalyticsPage() {
	const { has } = await auth()

	const canViewAnalytics = has({ feature: 'analytics' })
	const canExport = has({ feature: 'export' })

	return (
		<div>
			{canViewAnalytics && <AnalyticsChart />}
			{canExport && <ExportButton />}
		</div>
	)
}
```

功能在控制面板 → 账单 → 功能中配置，并分配给计划。使用 `has({ feature })` 而不是 `has({ plan })` 来限制粒度功能，检查功能而不是计划。

### 3. 客户端端检查功能授权

使用 `useAuth()` 进行客户端功能门限。与服务器端检查结合使用以实现全面覆盖：

```tsx
'use client'
import { useAuth } from '@clerk/nextjs'

export function FeatureGatedUI() {
	const { has, isLoaded } = useAuth()
	if (!isLoaded) return null

	const canExport = has?.({ feature: 'export' })
	const canAnalytics = has?.({ feature: 'analytics' })

	return (
		<div>
			{canAnalytics && <AnalyticsSection />}
			{canExport ? <ExportButton /> : <UpgradeToExport />}
		</div>
	)
}
```

服务器组件使用 `auth()`，客户端组件使用 `useAuth()`。两者都支持 `has({ feature })` 和 `has({ plan })`。

### 4. 服务器端检查订阅计划

通过订阅计划门限访问（用于层级门限，不是单个功能）：

```typescript
import { auth } from '@clerk/nextjs/server'
import { redirect } from 'next/navigation'

export default async function ProDashboard() {
	const { has } = await auth()

	if (!has({ plan: 'pro' })) {
		redirect('/pricing')
	}

	return <ProFeatures />
}
```

### 5. 客户端端计划检查

使用 `useAuth()` 钩子进行客户端组件：

```tsx
'use client'
import { useAuth } from '@clerk/nextjs'

export function UpgradePrompt() {
	const { has } = useAuth()

	if (has?.({ plan: 'pro' })) {
		return null
	}

	return (
		<div>
			<p>升级到 Pro 以访问此功能</p>
			<a href="/pricing">查看计划</a>
		</div>
	)
}
```

### 6. B2B 基于座位的组织账单

组织计划可以携带**座位限制**（成员资格上限），Clerk 在邀请时强制执行。在组织端计划检查中使用 `org:` slugs 前缀（例如 `has({ plan: 'org:team' })`）以保持门限明确。使用 `<PricingTable for="organization" />` 渲染 B2B 定价页面，并使用 `<OrganizationProfile />` 进行组织账户账单 UI。

有关分层计划命名、座位限制不变量、管理员仅账单和 webhook 处理器的信息，请参阅 `references/b2b-patterns.md`。

### 7. 显示订阅状态

使用 `has({ plan })` 检查特定计划，或在客户端组件中使用 `useSubscription()` 获取完整订阅详细信息。不要直接从 `sessionClaims` 读取计划信息，这不是支持路径。

服务器组件，检查特定计划：

```typescript
import { auth } from '@clerk/nextjs/server'

export default async function AccountPage() {
	const { has } = await auth()

	const currentPlan = has({ plan: 'pro' })
		? 'pro'
		: has({ plan: 'starter' })
			? 'starter'
			: 'free'

	return (
		<div>
			<h2>当前计划</h2>
			<p>您正在使用 {currentPlan} 计划</p>
			{currentPlan === 'free' && <a href="/pricing">升级</a>}
		</div>
	)
}
```

客户端组件，通过 `useSubscription()` 获取完整订阅详细信息：

```tsx
'use client'
import { useSubscription } from '@clerk/nextjs/experimental'

export function SubscriptionDetails() {
	const { data: subscription, isLoading } = useSubscription()
	if (isLoading) return null
	if (!subscription) return <a href="/pricing">选择一个计划</a>

	return (
		<div>
			<p>状态：{subscription.status}</p>
			{subscription.nextPayment && (
				<p>下次付款：{subscription.nextPayment.date.toLocaleDateString()}</p>
			)}
		</div>
	)
}
```

> `useSubscription()` 仅用于显示。对于授权检查（门限内容或路由），始终使用 `has({ plan })` 或 `has({ feature })`。

### 8. 通过计划保护 API 路由

使用 `auth()` 门限 API 路由：

```typescript
import { auth } from '@clerk/nextjs/server'
import { NextResponse } from 'next/server'

export async function GET() {
	const { has } = await auth()

	if (!has({ plan: 'pro' })) {
		return NextResponse.json({ error: 'Pro 计划需要' }, { status: 403 })
	}

	return NextResponse.json({ data: '高级数据' })
}
```

### 9. 处理账单 webhook

> **Clerk 事件名称与 Stripe 事件名称不同。** Clerk 账单 webhook 使用点符号和驼峰命名，而不是 Stripe 的下划线格式。
>
> 没有 `subscription.canceled` 事件。取消在项目级别触发，作为 `subscriptionItem.canceled`。
>
> | 意图 | Stripe 事件名称 | Clerk 事件名称 |
> |--------|------------------|-----------------|
> | 订阅创建 | `customer.subscription.created` | `subscription.created` |
> | 订阅更新 | `customer.subscription.updated` | `subscription.updated` |
> | 订阅激活 | (无) | `subscription.active` |
> | 订阅过期 | (无) | `subscription.pastDue` |
> | 订阅项取消 | `customer.subscription.deleted` | `subscriptionItem.canceled` |
> | 订阅项过期 | `invoice.payment_failed` | `subscriptionItem.pastDue` |
> | 订阅项更新 | (无) | `subscriptionItem.updated` |
> | 订阅项激活 | (无) | `subscriptionItem.active` |
> | 订阅项即将续订 | (无) | `subscriptionItem.upcoming` |
> | 订阅项结束 | (无) | `subscriptionItem.ended` |
> | 订阅项放弃 | (无) | `subscriptionItem.abandoned` |
> | 订阅项过期 | (无) | `subscriptionItem.expired` |
> | 订阅项不完整 | (无) | `subscriptionItem.incomplete` |
> | 免费试用即将结束 | (无) | `subscriptionItem.freeTrialEnding` |
> | 付款尝试创建 | (无) | `paymentAttempt.created` |
> | 付款尝试更新 | (无) | `paymentAttempt.updated` |
>
> 在 `evt.type` 检查中始终使用 Clerk 的事件名称，绝不用 Stripe 的。

> **有效负载形状。** Clerk 账单 webhook 有效负载是嵌套的。订阅实体位于 `evt.data.payer` 下（字段：`user_id?`，`organization_id?`）。计划信息在每个项目下 `evt.data.items[i].plan.slug`。订阅 ID 简单是 `evt.data.id`。订阅项不携带 `subscription_id` 字段回参考，所以在 `subscriptionItem.*` 处理器中，您通过项目 ID (`evt.data.id`) 或通过付款者加计划识别记录。

最小处理器以锚定模式（从 `@clerk/nextjs/webhooks` 导入，验证，按 Clerk 事件名称分支）：

```typescript
import { verifyWebhook } from '@clerk/nextjs/webhooks'
import { NextRequest } from 'next/server'
import { db } from '@/lib/db'

export async function POST(req: NextRequest) {
	let evt
	try {
		evt = await verifyWebhook(req)
	} catch {
		return new Response('验证失败', { status: 400 })
	}

	if (evt.type === 'subscription.created') {
		const { id, payer, items, status } = evt.data
		const entityId = payer.organization_id ?? payer.user_id
		const plan = items[0]?.plan?.slug
		await db.subscriptions.upsert({
			where: { subscriptionId: id },
			create: { subscriptionId: id, entityId, plan, status },
			update: { entityId, plan, status },
		})
	}

	// 根据上表事件目录添加更多分支（subscription.updated，
	// subscriptionItem.canceled，subscriptionItem.pastDue，等）

	return new Response('OK', { status: 200 })
}
```

有关涵盖所有 15 个事件的完整模板、来自 `@clerk/backend` 的 TS 类型声明、`proxy.ts` 公共路由设置以及订阅状态值表，请参阅 `references/billing-webhooks.md`。

### 10. 升级/降级流程

让用户在应用内部管理他们的订阅：

```tsx
import { PricingTable } from '@clerk/nextjs'
import { auth } from '@clerk/nextjs/server'

export default async function BillingPage() {
	const { has } = await auth()
	const isPro = has({ plan: 'pro' })

	return (
		<div>
			<h1>账单</h1>
			{isPro ? (
				<div>
					<p>您正在使用 Pro 计划</p>
					<PricingTable />
				</div>
			) : (
				<div>
					<p>升级以访问高级功能</p>
					<PricingTable />
				</div>
			)}
		</div>
	)
}
```

`<PricingTable />` 对于已订阅用户会不同，它显示当前计划并允许升级或取消，所有通过 Clerk 的应用内结账抽屉。

## 计划和功能命名

计划 slugs 和功能 slugs 在 Clerk 控制面板 → 账单中定义。常见约定：

| 层级 | 计划 Slugs | 示例功能 |
|------|-----------|-----------------|
| 免费 | (无需检查计划) | 基础功能 |
| 启动 | `starter` | `analytics`，`api_access` |
| 专业 | `pro` | `analytics`，`export`，`team` |
| 企业 | `enterprise` | 所有功能 + `sso`，`audit_logs` |

使用与控制面板中定义相匹配的小写 slugs。

## B2B 与 B2C 账单

| 场景 | 订阅者 | 计划检查 |
|------|--------|---------|
| B2C SaaS | 个人用户 | 在用户会话中检查 `has({ plan: 'pro' })` |
| B2B SaaS | 组织 | 在组织会话中检查 `has({ plan: 'org:team' })` |
| 座位限制型 B2B | 组织 | 计划有座位上限；定价按计划而非按成员，为大型组织分层级计划 |

对于 B2B，确保用户有一个活跃的组织会话。`has()` 检查会评估活跃实体（用户或组织）。

## 结账流程

Clerk 会自动通过 `<PricingTable />` 和 `<CheckoutButton />` 渲染自己的结账抽屉。计划和定价存储在 Clerk 中。要从服务器操作触发结账，重定向到渲染 `<PricingTable />` 的页面：

```typescript
'use server'
import { redirect } from 'next/navigation'

export async function upgradeAction() {
	redirect('/pricing')
}
```

## 错误签名（快速诊断）

当你看到任何这些错误或症状时，修复几乎总是 Dashboard 开关，而不是代码更改。不要开始编辑组件。

| 错误/症状 | 根本原因 | 修复 |
|---|---|---|
| `Clerk: 🔒 <PricingTable/> 组件在禁用计费时无法渲染。`（代码：`cannot_render_billing_disabled`，仅开发人员可见） | 此实例未启用计费 | 在 [dashboard.clerk.com → 计费 → 设置](https://dashboard.clerk.com/last-active?path=billing/settings) 启用计费，或运行 `clerk enable billing`。 |
| `<PricingTable />` 渲染为空 | 无计划，或计划在错误的选项卡中（用户 vs 组织），或计费未启用 | 在匹配的选项卡中创建计划；为 B2B 传递 `for="organization"`；检查计费设置 |
| 用户无法在 B2C + B2B 应用中订阅个人计划 | 成员资格模式（自 2025-08-22 默认）禁用个人账户，已登录用户被强制进入 `choose-organization` 并永远不会进入个人订阅状态 | 如果需要个人 + 组织订阅共存：Dashboard → 组织设置 → *成员资格可选* |
| 找不到功能页面 | 功能按计划区分，非全局 | Dashboard → 计费 → 计划 → 点击计划 → 功能 |
| `has({ plan: 'pro' })` 在成功结账后始终返回 `false` | 会话令牌未刷新以包含新计划 | `await clerk.session?.reload()` 或导航以强制新会话 |
| `has({ plan: 'pro' })` 在任何订阅尝试之前返回 `false` | 计划 slug 不匹配（区分大小写），或计费未启用，或生产环境中的支付网关未连接 | 在 Dashboard → 计费 → 计划中验证 slug；确认计费 → 设置显示已启用 + 连接的网关 |
| `has({ permission: 'org:x:y' })` 返回 `false` 对于拥有该角色的用户 | 与该权限绑定的功能未包含在组织的活跃计划中 | 在 Dashboard → 计费 → 计划 → 功能中为计划添加功能 |
| Webhook 401 / 签名验证失败 | `CLERK_WEBHOOK_SIGNING_SECRET` 不匹配或路由受中间件保护 | 从 Dashboard → Webhooks 复制签名密钥；将 webhook 路由添加到 `createRouteMatcher(['/api/webhooks(.*)'])` |

## 计费门权限

当计费启用时，即使用户通过角色分配了权限，`has({ permission: 'org:posts:edit' })` 也会返回 `false`，如果与该权限关联的功能未包含在组织的活跃计划中。这是设计如此：功能级别的计费门权限。始终确保所需功能附加到 Dashboard → 计费 → 计划 → 功能中的计划。

## 参考文档

- `clerk-setup` - 初始 Clerk 安装
- `clerk-orgs` - B2B 组织（B2B 计费和座位限制计划所需）
- `clerk-webhooks` - Webhook 签名验证和路由
