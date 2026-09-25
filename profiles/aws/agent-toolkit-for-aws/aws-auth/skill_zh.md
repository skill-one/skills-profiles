# AWS 认证 (Amazon Cognito)

使用 Amazon Cognito 和 Amplify 客户端认证库进行应用级别的用户认证和授权。当精度至关重要时，请根据官方 AWS 文档验证特定的限制、配额和精确的 API 形状；当它们冲突时，请相信文档而不是内存。

**推荐：** AWS MCP 服务器提供对在此技能中使用的 AWS API 的简化访问（Cognito 用户池/应用程序客户端/身份池设置、API Gateway 授权器）。如果它不可用，整个文档中显示的 AWS CLI 命令直接工作——该技能没有对 MCP 的硬依赖。

**不使用的情况：** Amplify Gen2 后端代码（`defineAuth`、`amplify/auth.ts`、`npx ampx`）；IAM 策略/角色/信任策略编写、STS 或 IAM 身份中心控制台 SSO；API Gateway 路由/集成设置或 Lambda 函数实现（此技能仅涵盖 Cognito/JWT 授权器配置和 Cognito Lambda 触发器的目的）。

## 用户池与身份池——首先选择哪一个

这些是经常被混淆的不同服务。大多数应用程序需要一个 **用户池**；只有当客户端必须直接调用 AWS 服务时，才添加 **身份池**。

| 您需要... | 使用 | 为什么 |
|-------------|-----|-----|
| 注册/登录、用户目录、签发 JWT | **用户池** | 它认证用户，并且是一个 OIDC IdP |
| 已登录的客户端使用 AWS 凭证直接调用 S3/DynamoDB 等 | **身份池** | 它通过 STS 交换令牌以获取临时 AWS 凭证 |
| 两者（登录，然后从浏览器/应用程序访问 AWS 资源） | 用户池 → 身份池 | 身份池将用户池视为其 IdP |

如果您的应用程序仅调用自己的后端/API，则您**不需要**身份池——将用户池令牌发送到您的 API。参见 [identity-pools.md](references/identity-pools.md)。

## 严重警告

**`update-user-pool-client` 和 `set-identity-pool-roles` 是完全替换，不是部分更新**：您省略的任何字段都会重置为其默认值——调用 `update-user-pool-client` 仅更改您想要更改的字段会无声地擦除 `ExplicitAuthFlows`、令牌有效性、`EnableTokenRevocation`、刷新令牌旋转和读写属性；`set-identity-pool-roles` 同样替换整个角色 + `RoleMappings` 结构。**始终使用读-改-写**：`describe-user-pool-client`（或 `get-identity-pool-roles`）首先，然后重新发送所有现有字段加上您的更改。在代理上下文中擦除是看不见的——调用成功，但只有在用户遇到缺失的流程时才会失败。参见 [managed-login-oauth.md](references/managed-login-oauth.md) 和 [identity-pools.md](references/identity-pools.md)。

**不要为新的应用程序使用隐式授权**：隐式授权（`response_type=token`）是遗留的，并在 URL 片段中返回令牌。使用 **授权码授权与 PKCE**（`response_type=code` + `code_challenge`）为 SPAs 和移动设备——公共客户端，无客户端密钥。参见 [managed-login-oauth.md](references/managed-login-oauth.md)。

**不要在高价值应用程序中在 localStorage 中存储刷新令牌**：`localStorage` 可被任何注入的脚本（XSS）读取。Amplify 客户端库默认为 `localStorage`；切换到 `cookieStorage`，保持刷新令牌生命周期短，并在应用程序客户端上启用**刷新令牌旋转** + **令牌撤销**。参见 [tokens-and-sessions.md](references/tokens-and-sessions.md)。

**访问令牌声明自定义需要一个付费功能计划**：预令牌生成触发器在入门级计划（V1）上自定义**ID 令牌**，但自定义**访问令牌**（V2/V3）需要一个**付费功能计划**——请检查 [Cognito 功能计划文档](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-sign-in-feature-plans.html) 当前哪个计划包含此功能，因为计划名称和包含项可能会更改。不要假设访问令牌声明在入门级计划上工作。参见 [lambda-triggers.md](references/lambda-triggers.md)。

**应用程序客户端密钥 + SPA = 失败的认证**：公共客户端（浏览器/移动设备）必须**没有客户端密钥**。如果设置了密钥，除非发送 `SECRET_HASH`，否则令牌调用会失败，而浏览器无法保护。仅为主机端（服务器端）客户端生成密钥。

**不要批量 `admin-confirm-sign-up` 未确认的用户**：当用户卡在 `UNCONFIRMED` 状态时，优先选择 `resend-confirmation-code`，以便每个用户通过 `confirm-sign-up` 重新验证并证明电子邮件所有权（代码可能已过期或进入垃圾邮件）。`admin-confirm-sign-up` 会立即翻转状态，但会确认帐户**而无需验证电子邮件**——属性保持未验证，这在电子邮件驱动密码重置或帐户链接时很危险。将其保留为受信任/迁移帐户。参见 [troubleshooting.md](references/troubleshooting.md)。

## 快速导航

| 您想要... | 前往 |
|----------------|-------|
| 创建用户池、注册/登录、MFA、密码策略、应用程序客户端 | [user-pools.md](references/user-pools.md) |
| 添加托管 UI / 管理登录、OAuth 流程、社交或 SAML 登录、回调 URL、**自定义域名（ACM 在 us-east-1）** | [managed-login-oauth.md](references/managed-login-oauth.md) |
| 处理 ID/访问/刷新令牌、旋转、撤销、**会话终止（全局注销 vs 撤销 vs 禁用）** | [tokens-and-sessions.md](references/tokens-and-sessions.md) |
| 为客户端提供临时 AWS 凭证、访客访问、角色映射 | [identity-pools.md](references/identity-pools.md) |
| 使用 Cognito 令牌保护 API Gateway API（**并在后端强制执行自定义声明**） | [api-authorization.md](references/api-authorization.md) |
| 在应用程序负载均衡器（ALB `authenticate-cognito`）前面添加 Cognito 登录 | [api-authorization.md](references/api-authorization.md) |
| 机器对机器（客户端凭据）认证、资源服务器、自定义范围 | [managed-login-oauth.md](references/managed-login-oauth.md) |
| 创建用户池组并将用户添加到其中（`cognito:groups`、`Precedence`） | [user-pools.md](references/user-pools.md) |
| 自定义声明、自定义认证挑战流程、迁移用户、验证注册 | [lambda-triggers.md](references/lambda-triggers.md) |
| 添加 **密钥/WebAuthn** 登录（`USER_AUTH` 流程、`AllowedFirstAuthFactors`、WebAuthn 注册） | [passkeys.md](references/passkeys.md) |
| 配置 **威胁防护**——受损凭证阻止、自适应认证（基于风险的 MFA）、将日志发送到 CloudWatch | [threat-protection.md](references/threat-protection.md) |
| 某些东西出错了（重定向、令牌、MFA、CORS、社交登录） | [troubleshooting.md](references/troubleshooting.md) |

完整表格在 [troubleshooting.md](references/troubleshooting.md)。

## 常见工作流程

**"将注册和登录添加到我的 React 应用程序"** → 创建用户池 + 一个公共应用程序客户端（无密钥），启用托管 UI / 管理登录与授权码授权和 PKCE，连接 Amplify 客户端库。参见 [user-pools.md](references/user-pools.md) 和 [managed-login-oauth.md](references/managed-login-oauth.md)。

**"添加 Google / 社交登录"** → 在用户池上注册社交 IdP，映射属性，将提供程序添加到应用程序客户端和托管 UI。参见 [managed-login-oauth.md](references/managed-login-oauth.md)。

**"只有认证用户才能调用我的 API"** → HTTP API → JWT 授权器；REST API → Cognito 用户池授权器。参见 [api-authorization.md](references/api-authorization.md)。

**"登录后让浏览器上传到 S3"** → 用户池用于登录，然后是一个身份池来出售范围临时的凭证。参见 [identity-pools.md](references/identity-pools.md)。

## 故障排除

| 错误/症状 | 可能的原因 | 快速修复 |
|---------------|-------------|-----------|
| `redirect_mismatch` / 登录后重定向到错误 URL | 回调 URL 未注册，或方案/尾随斜杠/大小写不同 | 将确切的回调 URL（包括方案和路径）添加到应用程序客户端的允许回调 URL |
| 令牌调用失败，提示 "无法验证密钥哈希" | 在公共（SPA/移动）客户端上设置了客户端密钥 | 重新创建应用程序客户端，不带密钥，或者从机密客户端发送 `SECRET_HASH` |
| 用户从 API Gateway 获取 401，但令牌有效 | 错误的令牌类型或受众/发布者不匹配 | HTTP JWT 授权器：发布者 `https://cognito-idp.{region}.amazonaws.com/{userPoolId}`，受众 = 应用程序客户端 ID；发送授权器期望的令牌 |
| 调用托管 UI / 令牌端点时出现 CORS 错误 | 浏览器跨域调用 `/oauth2/token`，或您的 API 缺少 CORS | 使用 PKCE 进行代码交换；不要从浏览器代理令牌端点 |
| 社交登录用户 "已存在" / 属性冲突 | 跨提供程序相同的电子邮件创建单独的用户 | 启用属性映射 + 帐户链接；将电子邮件视为跨 IdP 非唯一 |

完整表格在 [troubleshooting.md](references/troubleshooting.md)。

## 安全注意事项

- 公共客户端（SPA/移动设备）：**无客户端密钥**，授权码授权**带 PKCE**，请求最低权限范围。
- 启用 **MFA**（TOTP 或 SMS），一个强密码策略，并在可用时启用**高级安全 / 威胁防护**。
- 短访问令牌生命周期；启用**刷新令牌旋转**和**令牌撤销**；优先选择 `cookieStorage` 而不是 `localStorage`。
- 身份池：将认证 IAM 角色的范围严格限制；禁用未认证（访客）访问，除非需要。
- 每个受保护请求都对 JWT 进行验证（`iss`、`aud`/`client_id`、`token_use`、`exp`）。使用维护库，如 [`aws-jwt-verify`](https://github.com/awslabs/aws-jwt-verify)，而不是手工验证。
- 在应用程序的网页上设置安全标头：`Content-Security-Policy`（限制脚本源以减轻令牌窃取 XSS）、`Strict-Transport-Security`（HSTS）、`X-Frame-Options`/`frame-ancestors`（登录页面的点击劫持）、`X-Content-Type-Options: nosniff`。
- 启用日志记录和监控：CloudTrail 用于 Cognito API 事件（注册/登录/管理员），用户池威胁防护（自适应认证 + 事件记录），CloudWatch 警报用于失败的/限流的认证，以及 API Gateway 访问日志用于授权器决策。
- 所有 Cognito 和 API 端点仅支持 HTTPS/TLS；在 CloudWatch 日志组、用于 MFA/通知的 SNS 主题和任何身份池前端的上传桶上启用加密，使用客户管理的 KMS 密钥（并限制密钥访问）。
- 如果使用 SNS 进行 MFA/通知交付，请为主题启用服务器端加密（KMS），并保持短信/电子邮件消息内容限于收件人需要的——不要包含比消息要求更多的 PII。
- 参考：[Amazon Cognito 安全功能（用户池）](https://docs.aws.amazon.com/cognito/latest/developerguide/managing-security.html)、[Amazon Cognito 安全（顶层，包括身份池）](https://docs.aws.amazon.com/cognito/latest/developerguide/security.html) 和 [IAM/STS 最佳实践](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)。

## 当此技能沉默时，去哪里查找

当您需要此技能之外的深度——精确的参数形状、当前限制、边缘行为——请回退到权威的 AWS 来源，而不是猜测。指针比内容老化慢得多，因此即使技能没有增长，此地图也保持有用。

- **API 参考（精确参数、默认值、错误）：** [Cognito 用户池 API](https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/) 和 [Cognito 身份 API](https://docs.aws.amazon.com/cognitoidentity/latest/APIReference/)
- **开发者指南（概念、工作流程）：** [Amazon Cognito 开发者指南](https://docs.aws.amazon.com/cognito/latest/developerguide/)
- **配额、速率限制、会话 cookie 生命周期：** [Cognito 配额](https://docs.aws.amazon.com/cognito/latest/developerguide/limits.html)
- **功能计划 / 层级门控：** [Cognito 功能计划](https://docs.aws.amazon.com/cognito/latest/developerguide/cognito-sign-in-feature-plans.html)
- **定价：** [Amazon Cognito 定价](https://aws.amazon.com/cognito/pricing/)
- **CLI 参考：** [aws cognito-idp](https://docs.aws.amazon.com/cli/latest/reference/cognito-idp/) 和 [aws cognito-identity](https://docs.aws.amazon.com/cli/latest/reference/cognito-identity/)

## 此技能未涵盖的内容

- **Amplify Gen2 后端**（`defineAuth`、`amplify/auth.ts`、`npx ampx sandbox`）。
- **IAM 策略/角色/信任策略编写、STS、IAM 身份中心控制台 SSO。**
- **API Gateway 路由/集成设置和 Lambda 函数实现**（此技能仅涵盖 Cognito/JWT 授权器配置和 Cognito Lambda 触发器的目的）。
