审计代码以发现常见的安全漏洞，这些漏洞通常由 AI 代码生成引入。这些问题在“vibe-coded”应用程序中尤为普遍——这些项目借助 AI 快速构建，而安全基础则被忽略。

AI 助手始终会犯这些错误模式，导致实际的安全漏洞、被盗的 API 密钥和耗尽的计费账户。这项技能旨在在这些代码发布前捕获这些错误。

## 核心原则

永远不要信任客户端。每个价格、用户 ID、角色、订阅状态、功能标志和速率限制计数器都必须在服务器端进行验证或强制执行。如果它仅存在于浏览器、移动应用程序包或请求体中，攻击者就可以控制它。

## 审计流程

系统地检查代码库。对于每个步骤，仅当代码库使用该技术或模式时才加载相关的参考文件。跳过不相关的步骤。

1. **密钥与环境变量** — 搜索硬编码的 API 密钥、令牌或凭证。检查通过客户端环境变量前缀（`NEXT_PUBLIC_`、`VITE_`、`EXPO_PUBLIC_`）暴露的密钥。验证 `.env` 是否在 `.gitignore` 中。参见 `references/secrets-and-env.md`。

2. **数据库访问控制** — 检查 Supabase RLS 策略、Firebase 安全规则或 Convex 认证保护。这是 vibe-coded 应用程序中关键漏洞的首要来源。参见 `references/database-security.md`。

3. **认证与授权** — 验证 JWT 处理、中间件认证、Server Action 保护和会话管理。参见 `references/authentication.md`。

4. **速率限制与滥用预防** — 确保认证端点、AI 调用和昂贵操作具有速率限制。验证速率限制计数器不能被篡改。参见 `references/rate-limiting.md`。

5. **支付安全** — 检查客户端价格操纵、webhook 签名验证和订阅状态验证。参见 `references/payments.md`。

6. **移动安全** — 验证安全令牌存储、通过后端代理保护的 API 密钥和深度链接验证。参见 `references/mobile.md`。

7. **AI / LLM 集成** — 检查暴露的 AI API 密钥、缺失的使用限制、提示注入向量和不安全的输出渲染。参见 `references/ai-integration.md`。

8. **部署配置** — 验证生产设置、安全头、源映射暴露和环境分离。参见 `references/deployment.md`。

9. **数据访问与输入验证** — 检查 SQL 注入、ORM 误用和缺失的输入验证。参见 `references/data-access.md`。

如果进行部分审查或在特定区域生成代码，仅加载相关的参考文件。

## 核心指令

- 仅报告真实的安全问题。不要挑剔风格或非安全问题。
- 当存在多个问题时，按可利用性和实际影响进行优先级排序。
- 如果代码库不使用特定技术（例如，没有 Supabase），则完全跳过该部分。
- 在生成新代码时，主动参考相关的参考文件，以避免从一开始就引入漏洞。
- 如果发现关键问题（暴露的密钥、禁用 RLS、认证绕过），立即在响应顶部标记它——不要将其淹没在长列表中。

## 输出格式

按严重程度组织发现：**关键** → **高** → **中** → **低**。

对于每个问题：
1. 说明文件和相关的行号。
2. 命名漏洞。
3. 解释攻击者可以做什么（具体影响，而不是抽象风险）。
4. 显示修复前后的代码。

跳过没有问题的区域。最后以优先级总结结束。

### 示例输出

#### 关键

**`lib/supabase.ts:3` — 在客户端包中暴露了 Supabase `service_role` 密钥**

`service_role` 密钥绕过所有行级安全。任何人都可以从浏览器包中提取它，并读取、修改或删除数据库中的每一行。

```typescript
// Before
const supabase = createClient(url, process.env.NEXT_PUBLIC_SUPABASE_SERVICE_KEY!)

// After — 客户端使用匿名密钥；`service_role` 仅应存在于服务器端代码中
const supabase = createClient(url, process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!)
```

#### 高

**`app/api/checkout/route.ts:15` — 从客户端请求体中获取价格**

攻击者可以通过修改请求来设置任何价格（包括 $0.01）。价格必须在服务器端查找。

```typescript
// Before
const session = await stripe.checkout.sessions.create({
  line_items: [{ price_data: { unit_amount: req.body.price } }]
})

// After — 服务器端查找价格
const product = await db.products.findUnique({ where: { id: req.body.productId } })
const session = await stripe.checkout.sessions.create({
  line_items: [{ price: product.stripePriceId }]
})
```

### 总结

1. **暴露服务角色密钥（关键）：** 任何人都可以绕过所有数据库安全。立即旋转密钥并将其仅移动到服务器端。
2. **客户端控制价格（高）：** 攻击者可以以任何价格购买。使用服务器端价格查找。

## 生成代码时

这些规则也适用于主动预防。在编写涉及认证、支付、数据库访问、API 密钥或用户数据的代码之前，参考相关的参考文件以避免从一开始就引入漏洞。预防胜于检测。

## 参考

- `references/secrets-and-env.md` — API 密钥、令牌、环境变量配置和 `.gitignore` 规则。
- `references/database-security.md` — Supabase RLS、Firebase 安全规则和 Convex 认证模式。
- `references/authentication.md` — JWT 验证、中间件、Server Actions 和会话管理。
- `references/rate-limiting.md` — 速率限制策略和滥用预防。
- `references/payments.md` — Stripe 安全、webhook 验证和价格验证。
- `references/mobile.md` — React Native 和 Expo 安全：安全存储、API 代理、深度链接。
- `references/ai-integration.md` — LLM API 密钥保护、使用限制、提示注入和输出清理。
- `references/deployment.md` — 生产配置、安全头和环境分离。
- `references/data-access.md` — SQL 注入预防、ORM 安全性和输入验证。
