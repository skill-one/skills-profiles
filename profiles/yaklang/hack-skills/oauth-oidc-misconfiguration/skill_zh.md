# 技能：OAuth 和 OIDC 配置错误 — 重定向、PKCE、作用域和令牌绑定

> **AI 加载指令**：当目标使用 OAuth 2.0 或 OpenID Connect，并且您需要一个专注于配置错误检查清单时使用此技能：重定向 URI 验证、状态和随机数处理、PKCE 强制执行、令牌受众和账户绑定错误。

## 1. 何时加载此技能

加载时：

- 应用程序支持 `使用 Google 登录`、GitHub、Microsoft、Okta 或其他身份提供者 (IdP)
- 您看到 `authorize`、`callback`、`redirect_uri`、`code`、`state`、`nonce` 或 `code_challenge`
- 移动或单页应用程序 (SPA) 客户端依赖 OAuth 或 OIDC 流

对于令牌加密和 JWT 头部滥用，也加载：

- [jwt oauth 令牌攻击](../jwt-oauth-token-attacks/SKILL.md)

## 2. 高价值配置错误检查

| 主题 | 检查内容 |
|---|---|
| `state` 处理 | 缺失、静态、可预测或未绑定到用户会话 |
| `redirect_uri` 验证 | 前缀匹配、开放重定向链、路径混淆、本地主机残留 |
| PKCE | 公共客户端缺失、代码验证器未强制执行、降级流程 |
| OIDC `nonce` | 缺失或在 ID 令牌返回时未验证 |
| 令牌受众和发行者 | 弱 `aud` / `iss` 检查、跨客户端令牌重用 |
| 账户绑定 | 回调将攻击者身份绑定到受害者会话 |
| 作用域处理 | 授予用户或客户端比应接收的更广泛的作用域 |

## 3. 快速排查

1. 映射完整流程：授权、回调、令牌交换、登出。
2. 使用修改后的 `state`、`nonce` 和 `redirect_uri` 重放回调流程。
3. 比较单页应用程序、移动和 Web 客户端以查找较弱验证。
4. 检查一个提供商账户是否可以重新绑定到另一个本地账户。

## 4. 相关路线

- CORS 或跨源令牌暴露：[cors 跨源配置错误](../cors-cross-origin-misconfiguration/SKILL.md)
- XML 联邦或企业 SSO：[saml sso 断言攻击](../saml-sso-assertion-attacks/SKILL.md)
- CSRF 重度登录或绑定错误：[csrf 跨站请求伪造](../csrf-cross-site-request-forgery/SKILL.md)
