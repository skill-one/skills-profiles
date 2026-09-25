# InsForge 集成

本技能涵盖将第三方提供商与 InsForge 集成。目前支持两类：**认证提供商**（通过 JWT 声明实现 RLS）和**支付促进者**（x402 HTTP 支付协议）。每个提供商都在此目录下有自己的指南。

## 认证提供商

| 提供商 | 指南 | 使用场景 |
|--------|------|----------|
| [Clerk](references/clerk.md) | Clerk JWT 模板 + InsForge RLS | Clerk 通过 JWT 模板直接签署令牌 — 无需服务器端签署 |
| [Auth0](references/auth0.md) | Auth0 操作 + InsForge RLS | Auth0 使用登录后操作将声明嵌入访问令牌 |
| [WorkOS](references/workos.md) | WorkOS AuthKit + InsForge RLS | WorkOS AuthKit 中间件 + 使用 `jsonwebtoken` 的服务器端 JWT 签署 |
| [Kinde](references/kinde.md) | Kinde + InsForge RLS | Kinde 令牌定制用于 InsForge 集成 |
| [Stytch](references/stytch.md) | Stytch + InsForge RLS | Stytch 会话令牌用于 InsForge 集成 |
| [Better Auth](references/better-auth.md) | Better Auth + InsForge RLS | 在您的 InsForge Postgres 中自托管的认证 — 无第三方 SaaS，无每 MAU 成本 |

## 支付促进者

| 提供商 | 指南 | 使用场景 |
|--------|------|----------|
| [OKX x402](references/okx-x402.md) | OKX 作为 x402 促进者（X 层上的 USDG） | 按使用付费的 HTTP 端点链上结算，付款人无需支付 gas 费 |

## 常见模式

### 认证提供商
1. **提供商签署或签发包含用户 ID 的 JWT**
2. **JWT 通过 `accessToken` 在 `createClient()` 中传递给 InsForge**（已弃用的别名：`edgeFunctionToken`）
3. **InsForge 通过 SQL 中的 `auth.jwt()` 暴露声明**
4. **RLS 策略使用 `requesting_user_id()` 函数强制行级安全**

### 支付促进者（x402）
1. **服务器返回 `402 Payment Required`**，并在 `PAYMENT-REQUIRED` 标头中 base64 编码 JSON 挑战
2. **客户端使用稳定币的 EIP-712 域名签署 EIP-3009 授权**
3. **服务器将签署的负载转发到促进者的 `/verify` + `/settle` 端点**
4. **服务器在 InsForge 表中记录已结算的支付**，并使用实时触发器进行实时仪表板

## 选择提供商

**认证**
- **Clerk** — 设置最简单；JWT 模板处理签署，无需服务器代码
- **Auth0** — 灵活；使用登录后操作进行声明注入
- **WorkOS** — 企业级；AuthKit 中间件 + 服务器端 JWT 签署
- **Kinde** — 开发者友好；内置令牌定制
- **Stytch** — API 优先；基于会话的令牌流程
- **Better Auth** — 在您的 Postgres 中自托管；无 SaaS 供应商；您拥有用户表。通过连接字符串 + 一个小的桥接路由与 InsForge 的 Postgres 无缝配合。迁移后需要一次 `REVOKE` 以封存 PostgREST 暴露。

**支付促进者**
- **OKX x402** — 通过 X 层上的 USDG 实现链上按使用付费；付款人无需支付 gas 费

## 设置

1. 确定项目使用的提供商
2. 阅读上表中对应的参考指南
3. 按照提供商特定的设置步骤操作

## 使用示例

每个提供商指南都包含以下方面的完整代码示例：
- 提供商控制台配置（API 密钥、应用程序设置等）
- 服务器和客户端代码（认证的 JWT 工具；支付的促进者客户端 + 签署工具）
- 数据库设置（认证的 RLS；支付表 + 实时触发器）
- 环境变量设置

参考具体的 `references/<provider>.md` 文件获取完整示例。

## 最佳实践

**认证**
- 所有认证提供商的用户 ID 都是字符串（不是 UUID） — 始终使用 `TEXT` 列存储 `user_id`
- 使用 `requesting_user_id()` 而不是 `auth.uid()` 进行 RLS 策略
- 通过 `accessToken` 传递 JWT — 静态字符串，不是函数；对于短生命周期令牌（Clerk），在初始同用户登录后同步刷新 `client.setAccessToken(token, AuthChangeEvent.TOKEN_REFRESHED)`
- 始终通过 `npx -y @insforge/cli secrets get JWT_SECRET` 获取 JWT 密钥

**支付促进者（x402）**
- 始终检查结算后的数据库 `insert(...)` 结果 — 结算在插入运行之前链上转移资金；静默的 DB 失败会丢失记录
- 在 `tx_hash` 列添加 `UNIQUE` 以防止重试产生重复记录
- 验证 EIP-712 域名（`name`，`version`）与令牌合约的链上 `DOMAIN_SEPARATOR` — 错误值会产生 `Invalid Authority` 错误
- 使用 `MOCK_OKX_FACILITATOR` 环境标志进行本地开发，以便在不使用真实资金的情况下演练完整流程

## 常见错误

**认证**

| 错误 | 解决方案 |
|------|----------|
| 使用 `auth.uid()` 进行 RLS | 使用 `requesting_user_id()` — 第三方 ID 是字符串，不是 UUID |
| 使用 UUID 列存储 `user_id` | 使用 `TEXT` — 所有支持的提供商使用字符串格式 ID |
| 硬编码 JWT 密钥 | 始终通过 `npx -y @insforge/cli secrets get JWT_SECRET` 获取 |
| 缺少 `requesting_user_id()` 函数 | 必须在 RLS 策略生效前创建 |

**支付（x402）**

| 错误 | 解决方案 |
|------|----------|
| 使用 OKX 交易 API 密钥 | 在 `web3.okx.com/onchainos/dev-portal` 创建单独的 Web3 API 密钥 |
| EIP-712 域名值错误 | 阅读令牌合约的 `DOMAIN_SEPARATOR` — 对于 X 层上的 USDG 使用 `name: "Global Dollar"`，`version: "1"` |
| 忽略结算后的 DB 插入错误 | 始终解构 `{ error }` 并记录/处理 — 资金已经转移 |
| 生产环境中 `MOCK_OKX_FACILITATOR=true` | 模拟模式仅用于演示；它返回假的 tx 哈希并绕过验证 |
