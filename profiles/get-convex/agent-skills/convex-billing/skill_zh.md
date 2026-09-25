<!-- GENERATED from convex-agents content/capabilities/billing.json — do not edit by hand. -->

# 添加计费 / 支付

使用 @convex-dev/stripe 将 Stripe 集成到 Convex：一个结算操作、一个由组件注册的 httpAction webhook（自动进行签名验证）、订阅状态存储在组件的表中，以及通过查询进行服务器端门控。

## 工作流程

1.  安装组件：`npm install @convex-dev/stripe`。
2.  创建 `convex/convex.config.ts`：
   ```ts
   import { defineApp } from 'convex/server';
   import stripe from '@convex-dev/stripe/convex.config.js';
   const app = defineApp();
   app.use(stripe);
   export default app;
   ```
3.  将 Stripe 密钥存储在 Convex 环境中（使用 `env` 微型功能）：`STRIPE_SECRET_KEY`（sk_test_… / sk_live_…）和 `STRIPE_WEBHOOK_SECRET`（whsec_…）。
4.  创建 `convex/http.ts` 以注册 webhook 路由（组件会自动处理签名验证）：
   ```ts
   import { httpRouter } from 'convex/server';
   import { components } from './_generated/api';
   import { registerRoutes } from '@convex-dev/stripe';
   const http = httpRouter();
   registerRoutes(http, components.stripe, { webhookPath: '/stripe/webhook' });
   export default http;
   ```
5.  创建 `convex/billing.ts`，包含一个结算操作和一个订阅门控查询：
   ```ts
   import { action, query } from './_generated/server';
   import { components } from './_generated/api';
   import { StripeSubscriptions } from '@convex-dev/stripe';
   import { v } from 'convex/values';
   const stripeClient = new StripeSubscriptions(components.stripe, {});
   export const createSubscriptionCheckout = action({
     args: { priceId: v.string() },
     returns: v.object({ sessionId: v.string(), url: v.union(v.string(), v.null()) }),
     handler: async (ctx, args) => {
       const identity = await ctx.auth.getUserIdentity();
       if (!identity) throw new Error('未认证');
       const customer = await stripeClient.getOrCreateCustomer(ctx, { userId: identity.subject, email: identity.email, name: identity.name });
       return await stripeClient.createCheckoutSession(ctx, { priceId: args.priceId, customerId: customer.customerId, mode: 'subscription', successUrl: `${process.env.SITE_URL ?? 'http://localhost:3000'}/?success=true`, cancelUrl: `${process.env.SITE_URL ?? 'http://localhost:3000'}/?canceled=true`, subscriptionMetadata: { userId: identity.subject } });
     },
   });
   export const isSubscribed = query({
     args: {},
     returns: v.boolean(),
     handler: async (ctx) => {
       const identity = await ctx.auth.getUserIdentity();
       if (!identity) return false;
       const subscriptions = await ctx.runQuery(components.stripe.public.listSubscriptionsByUserId, { userId: identity.subject });
       return subscriptions.some((sub) => sub.status === 'active' || sub.status === 'trialing');
     },
   });
   ```
6.  运行 `npx convex dev --once` — 它将安装组件并推送函数。验证输出显示 `✔ 已安装组件 stripe.`。
7.  在 Stripe 控制台 → Webhooks：添加端点 `https://<部署>.convex.site/stripe/webhook`，订阅 `checkout.session.completed`、`customer.subscription.*`、`invoice.*`、`payment_intent.*`。将签名密钥复制为 `STRIPE_WEBHOOK_SECRET`。

## 规则

- 使用 @convex-dev/stripe（npm: @convex-dev/stripe@^0.1.4）— 它通过 `registerRoutes` 内部处理 webhook 签名验证；不要手动编写 `constructEvent` webhook。
- Stripe 密钥存储在 Convex 环境中（使用 `env` 微型功能）：`STRIPE_SECRET_KEY` 和 `STRIPE_WEBHOOK_SECRET`。
- 通过 `isSubscribed` 查询（读取组件表）在服务器存储的订阅状态上设置门控，而不是依赖客户端声明。
- `convex/convex.config.ts` 必须从 `@convex-dev/stripe/convex.config.js` 导入（而不是 .ts）— `.js` 扩展名是 Convex 打包器所必需的。
