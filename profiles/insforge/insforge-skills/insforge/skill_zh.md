# InsForge App 集成技能

本技能涵盖使用 `@insforge/sdk` 进行的 **客户端 SDK 集成**。对于后端基础设施操作（创建表格、检查模式、部署函数、密钥、管理存储桶、配置支付服务商密钥/目录、网站部署、定时任务和计划、日志等），请使用 **insforge-cli** 技能。

## 快速设置

### 1. 安装 SDK

```bash
npm install @insforge/sdk@latest
```

### 2. 设置环境变量

在使用 SDK 之前，请在项目根目录创建 `.env` 文件（Next.js 使用 `.env.local`），其中包含 InsForge 的 URL 和 anon key。

#### 如何获取你的 URL 和 anon key

1. **确保项目已关联。** 在项目根目录检查是否存在 `.insforge/project.json`。
   - 对于已有项目，使用 `npx -y @insforge/cli link` 生成；对于新项目，使用 `npx -y @insforge/cli create` 生成。

2. **通过 CLI 获取 anon key：**

   ```bash
   npx -y @insforge/cli secrets get ANON_KEY
   ```

3. **从 `.insforge/project.json` 中的 `oss_host` 字段获取 URL**（例如 `https://myapp.us-east.insforge.app`）。

4. **将这两个值写入 `.env` 文件**，使用正确的框架前缀（见下表）。

> **重要提示：** 使用 anon key 为用户级别的 SDK 客户端（包括 SSR）。对于需要管理员/服务权限的仅服务端特权代码，使用 `createAdminClient({ apiKey })`；该 API key 是完整访问权限的管理员 key，等价于其他平台的服务角色 key。

根据框架使用正确的环境变量前缀和访问模式：

| 框架                     | `.env` 文件    | 变量                                                   | 访问模式                              |
| ------------------------- | --------------- | ------------------------------------------------------ | ------------------------------------- |
| **Next.js**               | `.env.local`    | `NEXT_PUBLIC_INSFORGE_URL`, `NEXT_PUBLIC_INSFORGE_ANON_KEY` | `process.env.NEXT_PUBLIC_*`           |
| **Vite**（React, Vue, Svelte） | `.env`       | `VITE_INSFORGE_URL`, `VITE_INSFORGE_ANON_KEY`           | `import.meta.env.VITE_*`              |
| **Astro**                 | `.env`         | `PUBLIC_INSFORGE_URL`, `PUBLIC_INSFORGE_ANON_KEY`       | `import.meta.env.PUBLIC_*`            |
| **SvelteKit**             | `.env`         | `PUBLIC_INSFORGE_URL`, `PUBLIC_INSFORGE_ANON_KEY`       | `import { env } from '$env/dynamic/public'` |
| **Create React App**      | `.env`         | `REACT_APP_INSFORGE_URL`, `REACT_APP_INSFORGE_ANON_KEY` | `process.env.REACT_APP_*`             |
| **Node.js / Server**      | `.env`         | `INSFORGE_URL`, `INSFORGE_ANON_KEY`                     | `process.env.*`                       |

Next.js 示例 `.env.local`：

```bash
NEXT_PUBLIC_INSFORGE_URL=https://your-appkey.us-east.insforge.app
NEXT_PUBLIC_INSFORGE_ANON_KEY=eyJhbGciOiJIUzI1NiIs...
```

> **重要提示：** 保持 `.env` 文件本地。将 `.env`、`.env.local` 和 `.env*.local` 添加到你的 `.gitignore` 中，并保留 `.env.example` 用于记录所需变量。

### 3. 初始化客户端

Next.js：

```javascript
import { createClient } from '@insforge/sdk'

const insforge = createClient({
  baseUrl: process.env.NEXT_PUBLIC_INSFORGE_URL,
  anonKey: process.env.NEXT_PUBLIC_INSFORGE_ANON_KEY
})
```

Vite：

```javascript
import { createClient } from '@insforge/sdk'

const insforge = createClient({
  baseUrl: import.meta.env.VITE_INSFORGE_URL,
  anonKey: import.meta.env.VITE_INSFORGE_ANON_KEY
})
```

Astro：

```javascript
import { createClient } from '@insforge/sdk'

const insforge = createClient({
  baseUrl: import.meta.env.PUBLIC_INSFORGE_URL,
  anonKey: import.meta.env.PUBLIC_INSFORGE_ANON_KEY
})
```

对于需要项目管理员权限的受信仅服务端代码：

```javascript
import { createAdminClient } from "@insforge/sdk";

const admin = createAdminClient({
  baseUrl: process.env.INSFORGE_URL,
  apiKey: process.env.INSFORGE_API_KEY,
});
```

## 模块参考

| 模块          | 集成指南                                            |
| ------------- | --------------------------------------------------- |
| **数据库**    | [database/sdk-integration.md](database/sdk-integration.md)   |
| **认证**      | [auth/sdk-integration.md](auth/sdk-integration.md)           |
| **存储**      | [storage/sdk-integration.md](storage/sdk-integration.md)     |
| **函数**      | [functions/sdk-integration.md](functions/sdk-integration.md) |
| **AI**        | [ai/overview.md](ai/overview.md)                             |
| **实时**      | [realtime/sdk-integration.md](realtime/sdk-integration.md)   |
| **邮件**      | [email/sdk-integration.md](email/sdk-integration.md)         |
| **支付：Stripe** | [payments/stripe.md](payments/stripe.md)             |
| **支付：Razorpay** | [payments/razorpay.md](payments/razorpay.md)       |

### 每个模块涵盖内容

| 模块          | 内容                                                             |
| ------------- | ---------------------------------------------------------------- |
| **数据库**    | CRUD 操作、过滤、分页、RPC 调用                                  |
| **认证**      | 注册/登录、OAuth、会话、个人资料、密码重置                       |
| **存储**      | 文件上传、下载、删除；S3 兼容网关用于 CI / 备份工具；为桶编写 RLS 策略 |
| **函数**      | 调用边缘函数                                                     |
| **AI**        | 通过 OpenRouter 进行聊天、图片、视频、音频、嵌入，以及模型发现     |
| **邮件**      | 发送自定义事务性 HTML 邮件（欢迎、新闻简报、通知）                |
| **支付：Stripe** | Stripe 结账会话、订阅，以及账单门户重定向                          |
| **支付：Razorpay** | Razorpay 订单、订阅、Checkout.js 以及订阅管理                     |
| **实时**      | 连接、订阅、发布事件，以及跟踪在线状态快照及加入/离开增量           |

### 指南

| 指南                                                                                      | 使用场景                                                                                                                                                                                                    |
| ----------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [../insforge-cli/references/database/access-control.md](../insforge-cli/references/database/access-control.md) | 应用表访问控制后端设置 —— 涵盖 RLS、无限递归防护、`SECURITY DEFINER` 模式、性能建议及常见 InsForge 模式                                                                                               |
| [storage/s3-gateway.md](storage/s3-gateway.md) | 当消费者是现有 S3 工具（aws CLI、AWS SDK、rclone、Terraform、boto3）且采用 `@insforge/sdk` 不切实际时的回退路径 —— 涵盖端点/区域设置、访问密钥管理、路径式寻址，以及支持的与不支持的 S3 操作。**要求 InsForge 2.0.9+。** **对于应用代码，优先使用 SDK** ([storage/sdk-integration.md](storage/sdk-integration.md)) |
| [storage/postgres-rls.md](storage/postgres-rls.md)                                       | 为 `storage.objects` 编写 RLS 策略 —— 仅所有者、公开读取、路径限定、团队共享，以及混合 REST + S3 桶的 `NULL uploaded_by` 注意事项                                                                                 |
| [../insforge-cli/references/database/vector.md](../insforge-cli/references/database/vector.md) | 语义搜索、推荐或 RAG 的后端设置 —— 涵盖 `vector` 扩展、模式/维度、距离运算符、HNSW/IVFFlat 索引及 RPC 相似度搜索                                                                                          |
| [ai/chat-completions.md](ai/chat-completions.md)                                        | 通过 OpenRouter 进行文本生成、结构化回答及流式聊天                                                                                                                                                    |
| [ai/image-generation.md](ai/image-generation.md)                                       | 通过 OpenRouter 进行图像生成/编辑，然后在 InsForge 存储中保存持久化存储                                                                                                                                     |
| [ai/video-generation.md](ai/video-generation.md)                                       | 异步 OpenRouter 视频任务、状态轮询及存储生成的媒体                                                                                                                                                      |
| [ai/audio.md](ai/audio.md)                                                               | 语音转文本、文本转语音，以及使用 InsForge 存储音频资产/转录文本                                                                                                                                           |
| [ai/embeddings-and-rag.md](ai/embeddings-and-rag.md)                                   | 通过 OpenRouter 生成嵌入，存储在 pgvector 中，并搭建基础的 RAG 流程                                                                                                                                      |
| [ai/models-list.md](ai/models-list.md)                                                 | 发现 OpenRouter 模型 ID、模态、参数、定价及嵌入维度                                                                                                                                                  |
| [payments](../insforge-cli/references/payments/overview.md)                              | 配置 Stripe/Razorpay 密钥、同步服务商目录、设置 Webhook，并在应用集成前编写支付 RLS                                                                                                                       |

### 为新应用构建支付功能

首先选择服务商。没有通用的应用支付指南：

- 对于 Stripe 结账、订阅及账单门户，加载 [payments/stripe.md](payments/stripe.md)。
- 对于 Razorpay 订单、订阅、Checkout.js 及取消/暂停/恢复流程，加载 [payments/razorpay.md](payments/razorpay.md)。

在编写应用代码之前，使用 **insforge-cli** 的支付参考检查服务商设置：

```bash
npx -y @insforge/cli payments stripe status
npx -y @insforge/cli payments razorpay status
```

如果所选服务商未配置，请让开发人员/管理员先配置该服务商。

### 实时后端设置

实时 SDK 用于前端事件处理与消息传递。使用 **insforge-cli** 技能配置频道模式、数据库触发器及频道/消息 RLS；请参阅 [realtime](../insforge-cli/references/realtime.md)。

### 后端配置

支持的项目配置项通过 CLI 管理 —— 使用
`npx -y @insforge/cli config export/plan/apply` 配置认证重定向 URL、验证标志、密码策略、认证 SMTP 设置、存储上传大小、实时/计划保留及云部署子域。OAuth 服务商、外部应用设置、存储桶、函数、密钥及部署环境变量仍使用其专属仪表盘或 CLI 流程。请参阅 **insforge-cli** 技能的 Configuration 部分。

### 有风险的后端变更？先创建分支

当本技能中的代码变更依赖于 **模式迁移**、**新 RLS 策略**、**OAuth 服务商配置变更**，或其他影响生产行为后端变更时，请先创建后端分支。分支共享 `JWT_SECRET`（现有用户 JWT 仍可正常工作），但获得全新的数据库 + EC2 + `API_KEY` / `ANON_KEY`，因此可以在独立环境中端到端测试 SDK 与后端变更。

完整的分支工作流位于 **insforge-cli** 技能中 —— 请参阅 [branch](../insforge-cli/references/branch/overview.md) 了解决策指南及生命周期命令。典型流程：

```bash
npx -y @insforge/cli branch create feat-x --mode schema-only
# ... 在分支上应用迁移 / 更改认证配置 / 更新 RLS ...
# ... 针对分支后端测试 SDK ...
npx -y @insforge/cli branch merge feat-x --dry-run     # 审查 SQL
npx -y @insforge/cli branch merge feat-x               # 应用到父分支
```

> ⚠ **在 `branch create` 或 `branch switch` 之后**，更新应用的 InsForge URL 和 anon-key 环境变量值，然后 **重启开发服务器**（或重新加载 `.env`），以便 SDK 连接所选分支的后端。

## SDK 快速参考

所有 SDK 方法均返回 `{ data, error }`。

| 模块               | 方法                                                                                 |
| ------------------ | ------------------------------------------------------------------------------------ |
| `insforge.database` | `.from().select()`、`.insert()`、`.update()`、`.delete()`、`.rpc()`                     |
| `insforge.auth`    | `.signUp()`、`.signInWithPassword()`、`.signInWithOtp()` / `.verifyOtp()`、`.signInWithOAuth()`、`.signOut()`、`.getCurrentUser()` |
| `insforge.storage` | `.from().upload()`、`.uploadAuto()`、`.download()`、`.remove()`                       |
| `insforge.functions` | `.invoke()`                                                                            |
| `insforge.ai`      | 仅作弃用的回退方法：`.chat.completions.create()`、`.images.generate()`、`.embeddings.create()` |
| `insforge.realtime` | `.connect()`、`.subscribe()`、`.publish()`、`.on()`、`.disconnect()`                    |
| `insforge.emails`  | `.send({ to, subject, html, cc?, bcc?, from?, replyTo? })`                           |
| `insforge.payments.stripe` | `.createCheckoutSession()`、`.createCustomerPortalSession()` |
| `insforge.payments.razorpay` | `.createOrder()`、`.verifyOrder()`、`.createSubscription()`、`.verifySubscription()`、`.cancelSubscription()`、`.pauseSubscription()`、`.resumeSubscription()` |

## 重要说明

- **数据库插入需要数组格式：** `insert([{...}])`
- **带宽高效的读取：** 列名与 `.limit()` 列表读取；不要对区间进行无界 `select()` 轮询 —— 使用 realtime 订阅（与 `realtime.publish` 触发器配对）或轮询廉价的有序探测替代。低效的查询结构是项目耗尽每月数据出口额度的主要原因。探测示例及完整规则：[database/sdk-integration.md](database/sdk-integration.md#bandwidth-efficient-reads)。
- **Next.js / SSR 认证：** 使用 `@insforge/sdk/ssr` 辅助函数（`createBrowserClient`、`createServerClient`、`createAuthActions`、`createRefreshAuthRouter`），并在 Proxy/Middleware 中从 `@insforge/sdk/ssr/middleware` 导入 `updateSession`。保持 refresh token 为 httpOnly，将认证变更通过 `createAuthActions()` 在服务端执行，仅从 Server Actions 返回安全的应用数据，并让浏览器读取短效 access token 进行 Storage/Realtime 操作。请参阅 [auth/ssr-integration.md](auth/ssr-integration.md)
- **存储：** 下载/删除操作时，数据库同时保存 `url` 和 `key`
- **函数调用 URL：** 优先使用 `insforge.functions.invoke(slug)` —— SDK 负责路由构建。对于原始 HTTP：项目基础 URL 提供兼容路径 `/functions/{slug}`，而函数部署主机（例如 `*.function2.insforge.app`）在根路径 `/{slug}` 提供服务标识。
- **邮件投递：** 认证邮件（注册验证、密码重置、魔术链接、邀请）在 **所有套餐** 中均发送。通过 `insforge.emails.send()` 发送的自定义邮件在 **所有付费套餐** 中发送。使用平台管理的投递路径；自定义发件域名为仪表盘配置。请参阅 [email/sdk-integration.md](email/sdk-integration.md)。
- **支付：** 先用 `npx -y @insforge/cli payments <provider> ...` 配置服务商密钥/目录；前端代码使用服务商专用的 SDK 模块。
- **支付 RLS：** 在支付 UI 之前，在服务商运行时表上添加应用特定的 RLS。Stripe 使用 `payments.stripe_checkout_sessions` 和 `payments.stripe_customer_portal_sessions`；Razorpay 使用 `payments.razorpay_orders` 和 `payments.razorpay_subscriptions`。持久的 fulfillment 触发器放置在 `payments.webhook_events` 上，而非成功 URL、Checkout 回调或 `payments.transactions` 上。
- **使用 Tailwind CSS v3.4**
- **部署前始终本地构建：** 避免浪费构建资源并加快调试速度
- **SDK 包：** 使用 `@insforge/sdk` 处理所有功能，包括认证。
- **部署：** 项目根目录包含 `vercel.json` 以支持 SPA 路由（React、React Router 应用）。`download-template` 工具会自动包含此文件。
- **有风险后端变更的分支处理：** 如果你的 SDK 代码依赖于新的模式、RLS 策略或认证配置变更，请先通过 `npx -y @insforge/cli branch create` 创建分支 —— 请参阅 **insforge-cli** 技能的 [branch](../insforge-cli/references/branch/overview.md) 参考。在 `branch create` / `branch switch` 之后，更新应用的 InsForge URL 和 anon-key 环境变量值，然后 **重启开发服务器**。
- **遇到 InsForge 侧障碍？** 当 SDK、后端、文档或技能出现异常时 —— 本应正常工作的 API 却报错（`--type bug`）、你需要的功能不受支持（`--type feature-request`）、文档与实际行为不符（`--type bug --component docs` 并配合 `--doc`/`--expected`） —— 请报告该问题并使用替代方案继续：`npx -y @insforge/cli feedback --json --type <bug|feature-request|friction> --component <backend|sdk|cli|skills|docs> --title "..." --detail "..."`，为 SDK 问题添加 `--language <lang>`（无需登录；PII 在本地脱敏）。请参阅 **insforge-cli** 技能的 Feedback 部分以了解完整的标志集及情况→类型映射。**切勿** 为你在编写中的应用代码中的问题提交反馈。
