---
name: insforge
description: 在用 InsForge 或 @insforge/sdk 编写应用代码时，使用此功能：数据库 CRUD、认证、存储上传/存储 RLS、函数、OpenRouter AI、实时功能、邮件、Stripe 或 Razorpay 支付，或指向 S3 兼容工具（aws CLI、AWS SDKs、rclone、Terraform、boto3）至 InsForge 存储。在添加认证、获取数据、上传文件、使存储桶公开、添加结账、销售订阅或发送邮件等请求时触发。对于基础设施，SQL 迁移、CLI 命令或支付提供者设置，请使用 insforge-cli。
---

# InsForge 应用集成技能

本技能涵盖使用 `@insforge/sdk` 进行的 **客户端 SDK 集成**。对于后端基础设施操作（创建表格、检查架构、部署函数、密钥、管理存储桶、配置支付提供者密钥/目录、网站部署、定时任务和计划、日志等），请使用 **insforge-cli** 技能。

## 快速设置

### 1. 安装 SDK

```bash
npm install @insforge/sdk@latest
```

### 2. 设置环境变量

在使用 SDK 之前，在项目根目录中创建一个 `.env` 文件（或 `.env.local` 用于 Next.js），其中包含您的 InsForge URL 和 anon key。

#### 如何获取您的 URL 和 anon key

1. **确保项目已关联。** 检查项目根目录中是否存在 `.insforge/project.json`。
   - 使用 `npx -y @insforge/cli link` 为现有项目生成它，或使用 `npx -y @insforge/cli create` 为新项目生成它。

2. **通过 CLI 获取 anon key**：

   ```bash
   npx -y @insforge/cli secrets get ANON_KEY
   ```

3. **从 `.insforge/project.json` 中的 `oss_host` 字段获取 URL**（例如，`https://myapp.us-east.insforge.app`）。

4. **将两个值写入 `.env` 文件**，使用正确的框架前缀（见下表）。

> **重要提示**：使用 anon key 为用户范围的 SDK 客户端，包括 SSR。对于需要管理员/服务访问的特权服务器端应用代码，请使用 `createAdminClient({ apiKey })`；API key 是全权限管理员 key，相当于其他平台上的服务角色 key。

为您的框架使用正确的环境变量前缀和访问模式：

| 框架                     | `.env` 文件  | 变量                                                   | 访问模式                              |
| ----------------------------- | ------------ | ----------------------------------------------------------- | ------------------------------------------- |
| **Next.js**                   | `.env.local` | `NEXT_PUBLIC_INSFORGE_URL`, `NEXT_PUBLIC_INSFORGE_ANON_KEY` | `process.env.NEXT_PUBLIC_*`                 |
| **Vite** (React, Vue, Svelte) | `.env`       | `VITE_INSFORGE_URL`, `VITE_INSFORGE_ANON_KEY`               | `import.meta.env.VITE_*`                    |
| **Astro**                     | `.env`       | `PUBLIC_INSFORGE_URL`, `PUBLIC_INSFORGE_ANON_KEY`           | `import.meta.env.PUBLIC_*`                  |
| **SvelteKit**                 | `.env`       | `PUBLIC_INSFORGE_URL`, `PUBLIC_INSFORGE_ANON_KEY`           | `import { env } from '$env/dynamic/public'` |
| **Create React App**          | `.env`       | `REACT_APP_INSFORGE_URL`, `REACT_APP_INSFORGE_ANON_KEY`     | `process.env.REACT_APP_*`                   |
| **Node.js / Server**          | `.env`       | `INSFORGE_URL`, `INSFORGE_ANON_KEY`                         | `process.env.*`                             |

Next.js 的 `.env.local` 示例：

```bash
NEXT_PUBLIC_INSFORGE_URL=https://your-appkey.us-east.insforge.app
NEXT_PUBLIC_INSFORGE_ANON_KEY=eyJhbGciOiJIUzI1NiIs...
```

> **重要提示**：保持 `.env` 文件本地。将 `.env`、`.env.local` 和 `.env*.local` 添加到 `.gitignore` 中，并为文档化所需变量保留 `.env.example`。

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

对于需要项目管理员访问的可信服务器端代码：

```javascript
import { createAdminClient } from "@insforge/sdk";

const admin = createAdminClient({
  baseUrl: process.env.INSFORGE_URL,
  apiKey: process.env.INSFORGE_API_KEY,
});
```

## 模块参考

| 模块        | 集成指南                                            |
| ------------- | ------------------------------------------------------------ |
| **Database**  | [database/sdk-integration.md](database/sdk-integration.md)   |
| **Auth**      | [auth/sdk-integration.md](auth/sdk-integration.md)           |
| **Storage**   | [storage/sdk-integration.md](storage/sdk-integration.md)     |
| **Functions** | [functions/sdk-integration.md](functions/sdk-integration.md) |
| **AI**        | [ai/overview.md](ai/overview.md)                             |
| **Real-time** | [realtime/sdk-integration.md](realtime/sdk-integration.md)   |
| **Email**     | [email/sdk-integration.md](email/sdk-integration.md)         |
| **Payments: Stripe** | [payments/stripe.md](payments/stripe.md)             |
| **Payments: Razorpay** | [payments/razorpay.md](payments/razorpay.md)       |

### 每个模块涵盖的内容

| 模块        | 内容                                                                                                       |
| ------------- | ------------------------------------------------------------------------------------------------------------- |
| **Database**  | CRUD 操作、过滤器、分页、RPC 调用                                                               |
| **Auth**      | 注册/登录、OAuth、会话、个人资料、密码重置                                                         |
| **Storage**   | 上传、下载、删除文件；S3 兼容网关用于 CI / 备份工具；为存储桶编写 RLS 策略                         |
| **Functions** | 调用边缘函数                                                                                         |
| **AI**        | 通过 OpenRouter 进行聊天、图像、视频、音频、嵌入和模型发现 AI 调用                                           |
| **Email**     | 发送自定义事务性 HTML 邮件（欢迎、订阅、通知）                                    |
| **Payments: Stripe** | Stripe 结账会话、订阅和计费门户重定向                                  |
| **Payments: Razorpay** | Razorpay 订单、订阅、Checkout.js 和订阅管理                               |
| **Real-time** | 连接、订阅、发布事件、跟踪存在快照以及加入/离开的增量                       |

### 指南

| 指南                                                                                                          | 何时使用                                                                                                                                                                                                                                                                                                                                                                                            |
| -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [../insforge-cli/references/database/access-control.md](../insforge-cli/references/database/access-control.md) | 后端设置用于应用-表格访问控制——涵盖 RLS、无限递归预防、`SECURITY DEFINER` 模式、性能提示和常见的 InsForge 模式                                                                                                                                                                                                                            |
| [storage/s3-gateway.md](storage/s3-gateway.md)                                                                 | 当消费者是现有 S3 工具（aws CLI、AWS SDKs、rclone、Terraform、boto3）并且采用 `@insforge/sdk` 不切实际时，作为后备路径——涵盖端点/区域设置、访问密钥管理、路径样式寻址和支持的与不支持 S3 操作。**需要 InsForge 2.0.9+。** **优先使用 SDK** ([storage/sdk-integration.md](storage/sdk-integration.md)) 进行应用代码 |
| [storage/postgres-rls.md](storage/postgres-rls.md)                                                             | 为 `storage.objects` 编写 RLS 策略——所有者专有、公共读取、路径范围、团队共享，以及混合 REST + S3 存储桶的 `NULL uploaded_by` 例外                                                                                                                                                                                                                                          |
| [../insforge-cli/references/database/vector.md](../insforge-cli/references/database/vector.md)                 | 后端设置用于语义搜索、推荐或 RAG——涵盖 `vector` 扩展、架构/维度、距离运算符、HNSW/IVFFlat 索引和 RPC 相似性搜索                                                                                                                                                                                                                     |
| [ai/chat-completions.md](ai/chat-completions.md)                                                               | 通过 OpenRouter 进行文本生成、结构化答案和流式聊天                                                                                                                                                                                                                                                                                                                                 |
| [ai/image-generation.md](ai/image-generation.md)                                                               | 通过 OpenRouter 生成/编辑图像，然后持久存储在 InsForge 存储                                                                                                                                                                                                                                                                                                                  |
| [ai/video-generation.md](ai/video-generation.md)                                                               | 异步 OpenRouter 视频任务、状态轮询和存储生成的媒体                                                                                                                                                                                                                                                                                                                               |
| [ai/audio.md](ai/audio.md)                                                                                     | 语音转文本、文本转语音，以及将音频资产/文本存储与 InsForge                                                                                                                                                                                                                                                                                                                     |
| [ai/embeddings-and-rag.md](ai/embeddings-and-rag.md)                                                           | 通过 OpenRouter 生成嵌入，将它们存储在 pgvector，并设置基本的 RAG 管道                                                                                                                                                                                                                                                                                                             |
| [ai/models-list.md](ai/models-list.md)                                                                         | 发现 OpenRouter 模型 ID、模态、参数、定价和嵌入维度                                                                                                                                                                                                                                                                                                                                    |
| [payments](../insforge-cli/references/payments/overview.md)                                                    | 配置 Stripe/Razorpay 密钥、同步提供者目录、设置 webhook 并在应用集成前编写支付 RLS                                                                                                                                                                                                                                                                        |

### 为新应用构建支付

首先选择提供者。没有通用的应用支付指南：

- 对于 Stripe 结账、订阅和计费门户，加载 [payments/stripe.md](payments/stripe.md)。
- 对于 Razorpay 订单、订阅、Checkout.js 和取消/暂停/恢复流程，加载 [payments/razorpay.md](payments/razorpay.md)。

在编写应用代码之前，使用 **insforge-cli** 支付参考检查提供者设置：

```bash
npx -y @insforge/cli payments stripe status
npx -y @insforge/cli payments razorpay status
```

如果选择的提供者未配置，请要求开发者/管理员首先配置该提供者。

### 实时后端设置

实时 SDK 用于前端事件处理和消息传递。使用 **insforge-cli** 技能配置频道模式、数据库触发器以及频道/消息 RLS；见 [realtime](../insforge-cli/references/realtime.md)。

### 后端配置

支持的 项目配置选项通过 CLI 管理——使用 `npx -y @insforge/cli config export/plan/apply` 配置身份验证重定向 URL、验证标志、密码策略、身份验证 SMTP 设置、存储上传大小、实时/计划保留和云部署子域。OAuth 提供者、外部应用设置、存储桶、函数、密钥和部署环境变量仍然使用其专门的仪表板或 CLI 流程。见 **insforge-cli** 技能的配置部分。

### 对于有风险的后端更改？首先使用分支

当此技能中的代码更改依赖于 **架构迁移**、**新的 RLS 策略**、**OAuth 提供者配置更改** 或任何其他影响生产行为的后端更改时，请首先创建后端分支。分支共享 `JWT_SECRET`（现有用户 JWT 继续有效），但获得新的数据库 + EC2 + `API_KEY` / `ANON_KEY`，因此您可以在隔离环境中端到端测试 SDK + 后端更改。

完整的分支工作流程存在于 **insforge-cli** 技能中——见 [branch](../insforge-cli/references/branch/overview.md) 以获取决策指南和工作流程命令。典型循环：

```bash
npx -y @insforge/cli branch create feat-x --mode schema-only
# ... 在分支上应用迁移 / 更改身份验证配置 / 更新 RLS ...
# ... 在分支后端测试 SDK ...
npx -y @insforge/cli branch merge feat-x --dry-run     # 审查 SQL
npx -y @insforge/cli branch merge feat-x               # 应用到父级
```

> ⚠ **在 `branch create` 或 `branch switch` 之后**，更新应用的 InsForge URL 和 anon-key 环境值，然后 **重启您的开发服务器**（或重新源 `.env`），以便 SDK 与选定的分支后端通信。

## SDK 快速参考

所有 SDK 方法返回 `{ data, error }`。

| 模块               | 方法                                                                                              |
| -------------------- | ---------------------------------------------------------------------------------------------------- |
| `insforge.database`  | `.from().select()`, `.insert()`, `.update()`, `.delete()`, `.rpc()`                                  |
| `insforge.auth`      | `.signUp()`, `.signInWithPassword()`, `.signInWithOtp()` / `.verifyOtp()`, `.signInWithOAuth()`, `.signOut()`, `.getCurrentUser()`        |
| `insforge.storage`   | `.from().upload()`, `.uploadAuto()`, `.download()`, `.remove()`                                      |
| `insforge.functions` | `.invoke()`                                                                                          |
| `insforge.ai`        | 已弃用，仅作为后备选项：`.chat.completions.create()`, `.images.generate()`, `.embeddings.create()` |
| `insforge.realtime`  | `.connect()`, `.subscribe()`, `.publish()`, `.on()`, `.disconnect()`                                 |
| `insforge.emails`    | `.send({ to, subject, html, cc?, bcc?, from?, replyTo? })`                                           |
| `insforge.payments.stripe` | `.createCheckoutSession()`, `.createCustomerPortalSession()` |
| `insforge.payments.razorpay` | `.createOrder()`, `.verifyOrder()`, `.createSubscription()`, `.verifySubscription()`, `.cancelSubscription()`, `.pauseSubscription()`, `.resumeSubscription()` |

## 重要提示

- **数据库插入需要数组格式**：`insert([{...}])`
- **带宽高效的读取**：指定列名并使用 `.limit()` 列出读取内容；切勿在间隔内轮询无限制的 `select()` —— 使用实时订阅（配合 `realtime.publish` 触发器）或轮询廉价有序探针代替。浪费查询形状是项目耗尽每月出口配额的首要原因。探针片段和完整规则：[database/sdk-integration.md](database/sdk-integration.md#bandwidth-efficient-reads)。
- **Next.js / SSR 认证**：使用 `@insforge/sdk/ssr` 辅助函数（`createBrowserClient`, `createServerClient`, `createAuthActions`, `createRefreshAuthRouter`）并在代理/中间件中导入 `updateSession` 从 `@insforge/sdk/ssr/middleware`。保持刷新令牌 httpOnly，在服务器上通过 `createAuthActions()` 运行认证突变，从服务器操作返回仅安全的应用数据，并让浏览器读取短期的访问令牌用于存储/实时。参见 [auth/ssr-integration.md](auth/ssr-integration.md)
- **存储**：为下载/删除操作将 `url` 和 `key` 都保存到数据库
- **函数调用 URL**：优先使用 `insforge.functions.invoke(slug)` —— SDK 负责路由构建。对于原始 HTTP：项目基础 URL 服务兼容路径 `/functions/{slug}`，而函数部署主机（例如 `*.function2.insforge.app`）在根路径 `/{slug}` 服务 slug
- **邮件投递**：认证邮件（注册验证、密码重置、魔法链接、邀请）在**所有计划**上发送。自定义邮件通过 `insforge.emails.send()` 在**所有付费计划**上发送。使用平台管理的投递路径；自定义发件人域在控制台配置。参见 [email/sdk-integration.md](email/sdk-integration.md)。
- **支付**：首先使用 `npx -y @insforge/cli payments <provider> ...` 配置提供者密钥/目录；前端代码使用提供者范围的 SDK 模块。
- **支付 RLS**：在支付 UI 之前，在提供者运行时表上添加特定应用的 RLS。Stripe 使用 `payments.stripe_checkout_sessions` 和 `payments.stripe_customer_portal_sessions`；Razorpay 使用 `payments.razorpay_orders` 和 `payments.razorpay_subscriptions`。持久化履行触发器在 `payments.webhook_events` 上，不在成功 URL、结账回调或 `payments.transactions` 上。
- **使用 Tailwind CSS v3.4**
- **部署前始终本地构建**：防止浪费构建资源并加快调试
- **SDK 包**：直接使用 `@insforge/sdk` 包含所有功能，包括认证。
- **部署**：在项目根目录中包含 `vercel.json` 用于 SPA 路由（React、React Router 应用）。`download-template` 工具会自动包含此文件。
- **分支处理高风险后端变更**：如果您的 SDK 代码依赖于新架构、RLS 策略或认证配置变更，请先通过 `npx -y @insforge/cli branch create` 创建分支 —— 参见 **insforge-cli** 技能的 [branch](../insforge-cli/references/branch/overview.md) 参考。在 `branch create` / `branch switch` 后，更新应用的 InsForge URL 和匿名密钥环境值，然后**重启开发服务器**。
- **遇到 InsForge 端的障碍？** 当 SDK、后端、文档或技能行为异常时——应该工作的 API 但报错（`--type bug`）、需要但不受支持的特性（`--type feature-request`）、与实际行为矛盾的文档（`--type bug --component docs` 配合 `--doc`/`--expected`）——请报告并继续使用替代方案：`npx -y @insforge/cli feedback --json --type <bug|feature-request|friction> --component <backend|sdk|cli|skills|docs> --title "..." --detail "..."`，为 SDK 问题添加 `--language <lang>`（无需登录；本地会脱敏 PII）。参见 **insforge-cli** 技能的反馈部分以获取完整标志集和情况→类型映射。切勿为您正在编写的应用代码问题提交反馈。
