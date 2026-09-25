# 身份验证与授权路由器

这是身份验证、会话和授权边界的路由入口。

使用它来决定在深入探究之前，问题是主要涉及登录机制、对象级授权、浏览器信任边界，还是身份协议（如 OAuth/JWT/SAML）。

## 使用场景

- 目标包括登录、注册、密码重置、双因素认证、会话、JWT、OAuth 或 SSO
- 你怀疑存在对象授权缺陷、跨租户访问、跨域读取、CSRF 或协议配置错误
- 你需要决定是先测试身份验证还是授权

## 技能图谱

- [身份验证绕过](../authbypass-authentication-flaws/SKILL.md)：登录绕过、密码重置、双因素认证、枚举、暴力破解防护
- [IDOR 破坏性对象授权](../idor-broken-object-authorization/SKILL.md)：IDOR、BOLA、BFLA、缺失对象权限
- [JWT OAuth 令牌攻击](../jwt-oauth-token-attacks/SKILL.md)：算法混淆、密钥信任问题、声明滥用、令牌伪造
- [OAuth OIDC 配置错误](../oauth-oidc-misconfiguration/SKILL.md)：重定向 URI、状态、随机数、PKCE、账户绑定
- [CSRF 跨站请求伪造](../csrf-cross-site-request-forgery/SKILL.md)：CSRF 令牌、SameSite、JSON CSRF、登录 CSRF
- [CORS 跨域配置错误](../cors-cross-origin-misconfiguration/SKILL.md)：反射 Origin、认证跨域读取、允许列表绕过
- [SAML SSO 断言攻击](../saml-sso-assertion-attacks/SKILL.md)：断言封装、签名验证、受众、ACS 边界

## 推荐流程

1. 首先确认身份验证模型和会话边界
2. 然后确认对象级和功能级授权
3. 然后转向令牌、跨域和协议细节
4. 如果存在企业联盟，继续 OAuth、OIDC 或 SAML 相关主题

## 相关类别

- [api-sec](../api-sec/SKILL.md)
- 默认凭证、用户名变体、单词列表尺寸和端口焦点均汇总在 [authbypass-authentication-flaws](../authbypass-authentication-flaws/SKILL.md)
