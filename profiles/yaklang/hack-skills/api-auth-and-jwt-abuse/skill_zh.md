# 技能：API 认证和 JWT 滥用 — 令牌信任、请求头技巧和速率限制

> **AI 加载指令**：当 API 依赖 JWT、携带令牌、API 密钥或弱请求身份信号时，使用此技能。关注令牌信任边界、声明滥用、请求头欺骗和速率限制绕过。

## 1. 令牌初步筛选

检查：

- `alg`、`kid`、`jku`、`x5u`
- 角色、组织、租户、范围或权限声明
- 发行人受众不匹配
- 移动端和 Web 令牌跨产品复用

## 2. 快速攻击选择

| 模式 | 首次测试 |
|---|---|
| 接受 `alg:none` | 带尾随点的未签名令牌 |
| RS256 混淆 | 使用公钥作为密钥切换到 HS256 |
| `kid` 查询信任 | `kid` 中的路径遍历或注入 |
| 远程密钥获取信任 | 攻击者控制的 `jku` 或 `x5u` |
| 弱密钥 | 使用目标词表进行离线破解 |

## 3. 隐藏字段和批量滥用

### 大量赋值字段选择

```text
role
isAdmin
admin
verified
plan
tier
permissions
org
owner
```

### 速率限制和批量滥用选择

```text
X-Forwarded-For: 1.2.3.4
X-Real-IP: 5.6.7.8
Forwarded: for=9.9.9.9
```

GraphQL 或 JSON 批量滥用候选：

- 登录变体的数组
- 使用不同 ID 的批量对象获取
- 请求中重复的密码重置或验证调用

## 4. 速率限制绕过系列

```text
X-Forwarded-For
X-Real-IP
Forwarded
User-Agent 旋转
路径大小写/斜杠变体
```

## 5. 下一步路由

- 对于 GraphQL 批量和隐藏参数：[graphql and hidden parameters](../graphql-and-hidden-parameters/SKILL.md)
- 对于默认凭证和暴力破解规划：[authentication bypass](../authbypass-authentication-flaws/SKILL.md)
- 对于 JWT 和 OAuth 深度：[jwt oauth token attacks](../jwt-oauth-token-attacks/SKILL.md)
- 对于浏览器和 SSO 流中的 OAuth 或 OIDC 配置缺陷：[oauth oidc misconfiguration](../oauth-oidc-misconfiguration/SKILL.md)
- 对于凭证浏览器读取和源信任缺陷：[cors cross origin misconfiguration](../cors-cross-origin-misconfiguration/SKILL.md)
