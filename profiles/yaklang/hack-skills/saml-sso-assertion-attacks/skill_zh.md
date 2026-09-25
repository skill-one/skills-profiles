# 技能：SAML 单点登录与断言攻击 — 签名验证、绑定和信任混淆

> **AI 加载指令**：当目标使用基于 SAML 的单点登录，并且您需要验证断言信任时使用此技能：签名覆盖范围、受众和接收者检查、ACS 处理、XML 解析弱点，以及 IdP/SP 混淆。

## 1. 何时加载此技能

加载时机：

- 企业单点登录使用 SAML 请求或响应
- 您看到 `SAMLRequest`、`SAMLResponse`、XML 断言或 ACS 端点
- 登录流程涉及外部 IdP 和浏览器 POST/重定向绑定

## 2. 高价值配置错误检查

| 主题 | 检查内容 |
|---|---|
| 签名验证 | 接受未签名的断言、错误节点签名、签名封装 |
| 受众和接收者 | 弱 `Audience`、`Recipient`、`Destination` 或 ACS 验证 |
| 发行人信任 | 接受错误 IdP 或多租户发行人混淆 |
| 重放和新鲜度 | 缺少 `InResponseTo`、弱 `NotBefore` / `NotOnOrAfter` 执行 |
| 账户映射 | 仅电子邮件绑定、大小写折叠、未验证的属性 |
| XML 解析行为 | 类似 XXE 的解析问题或 SAML 文档周围的 unsafe 转换 |

## 3. 快速排查

1. 捕获一个完整的登录往返过程。
2. 检查哪些 XML 节点被签名，以及哪些属性驱动账户绑定。
3. 比较 SP 发起和 IdP 发起的流程。
4. 测试重放、修改的属性和断言位置混淆。

## 4. 相关路线

- XML 解析攻击深度：[xxe xml 外部实体](../xxe-xml-external-entity/SKILL.md)
- OAuth 或 OIDC 单点登录替代方案：[oauth oidc 配置错误](../oauth-oidc-misconfiguration/SKILL.md)
- SSO 后的认证边界问题：[authbypass 认证缺陷](../authbypass-authentication-flaws/SKILL.md)
