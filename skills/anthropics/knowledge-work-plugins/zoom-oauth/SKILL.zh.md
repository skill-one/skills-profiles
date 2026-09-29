---
name: zoom-oauth
description: 用于 Zoom 认证的参考技能。在路由到认证工作流时，选择应用程序凭据、授权类型、范围、令牌刷新行为或调试 Zoom OAuth 失败时使用。
---

# Zoom OAuth

Zoom 认证授权背景参考，以及令牌生命周期的行为。建议先使用 `setup-zoom-oauth`，然后使用此技能来获取精确的流程、范围和错误详情。

# Zoom OAuth

Zoom API 的认证和授权。

## 📖 完整文档

有关全面的指南、生产模式以及故障排除，请参阅**下方的集成索引部分**。

快速导航：
- **[5分钟运行手册](RUNBOOK.md)** - 深度调试前的预检
- **[OAuth 流程](concepts/oauth-flows.md)** - 使用哪个流程以及每个流程的工作方式
- **[令牌生命周期](concepts/token-lifecycle.md)** - 过期、刷新和撤销
- **[生产示例](examples/s2s-oauth-redis.md)** - Redis 缓存、MySQL 存储、自动刷新
- **[故障排除](troubleshooting/common-errors.md)** - 错误代码 4700-4741

## 前置条件

- 在 [Marketplace](https://marketplace.zoom.us/) 中创建的 Zoom 应用
- 客户ID和客户密钥
- 对于 S2S OAuth：账户ID

## 四种授权用例

| 用例 | 应用类型 | 授权类型 | 行业名称 |
|------|----------|------------|---------------|
| **账户授权** | 服务器到服务器 | `account_credentials` | 客户凭证授权、M2M、两脚OAuth |
| **用户授权** | 普通应用 | `authorization_code` | 授权码授权、三脚OAuth |
| **设备授权** | 普通应用 | `urn:ietf:params:oauth:grant-type:device_code` | 设备授权授权 (RFC 8628) |
| **客户端授权** | 普通应用 | `client_credentials` | 客户凭证授权 (聊天机器人范围) |

### 行业术语

| 术语 | 含义 |
|------|---------|
| **两脚OAuth** | 没有用户参与（客户端 ↔ 服务器） |
| **三脚OAuth** | 用户参与（用户 ↔ 客户端 ↔ 服务器） |
| **M2M** | 机器到机器（后端服务） |
| **公共客户端** | 不能保持秘密（移动端、SPA）→ 使用 PKCE |
| **秘密客户端** | 可以保持秘密（后端服务器） |
| **PKCE** | 代码交换证明密钥 (RFC 7636)，发音为 "pixy" |

### 我应该使用哪个流程？

```
                              ┌─────────────────────┐
                              │  你在构建什么？       │
                              │  (What are you      │
                              │  building?)         │
                              └──────────┬──────────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
                    ▼                    ▼                    ▼
          ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
          │  后端          │  │  为其他用户/账户  │  │  仅聊天机器人    │
          │  自动化        │  │  设计的应用      │  │  (团队聊天)    │
          │  (你的账户)    │  │                 │  │                 │
          └────────┬────────┘  └────────┬────────┘  └────────┬────────┘
                   │                    │                    │
                   ▼                    │                    ▼
          ┌─────────────────┐           │           ┌─────────────────┐
          │    账户        │           │           │     客户端      │
          │   (S2S OAuth)   │           │           │   (聊天机器人)    │
          └─────────────────┘           │           └─────────────────┘
                                        │
                                        ▼
                              ┌─────────────────────┐
                              │  设备是否有浏览器？   │
                              │  (Does device have   │
                              │  a browser?)         │
                              └──────────┬──────────┘
                                         │
                         ┌───────────────┴───────────────┐
                         │ 否                         是│
                         ▼                               ▼
          ┌─────────────────────────┐         ┌─────────────────┐
          │        设备           │         │      用户       │
          │     (设备流程)       │         │  (授权码)    │
          │                         │         │                 │
          │ 示例：               │         │ + 如果是公共客户端 │
          │ • 智能电视              │         │   则使用 PKCE     │
          │ • 会议SDK设备    │         │                 │
          └─────────────────────────┘         └─────────────────┘
```

---

## 账户授权（服务器到服务器 OAuth）

用于无需用户交互的后端自动化。

### 请求访问令牌

```bash
POST https://zoom.us/oauth/token?grant_type=account_credentials&account_id={ACCOUNT_ID}

Headers:
Authorization: Basic {Base64(ClientID:ClientSecret)}
```

### 响应

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600,
  "scope": "user:read:user:admin",
  "api_url": "https://api.zoom.us"
}
```

### 刷新

访问令牌在**1小时**后过期。没有单独的刷新流程 - 只需请求新令牌。

---

## 用户授权（授权码流程）

用于代表用户操作的应用。

### 第一步：重定向用户进行授权

```
https://zoom.us/oauth/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}
```

使用 `https://zoom.us/oauth/authorize` 进行同意，但使用 `https://zoom.us/oauth/token` 进行令牌交换。

**可选参数：**

| 参数 | 描述 |
|-----------|-------------|
| `state` | CSRF保护，通过流程保持状态 |
| `code_challenge` | 用于 PKCE（见下文） |
| `code_challenge_method` | `S256` 或 `plain` (默认：plain) |

### 第二步：用户授权

- 用户登录并授予权限
- 重定向到 `redirect_uri` 并附带授权码：
  ```
  https://example.com/?code={AUTHORIZATION_CODE}
  ```

### 第三步：用代码交换令牌

```bash
POST https://zoom.us/oauth/token?grant_type=authorization_code&code={CODE}&redirect_uri={REDIRECT_URI}

Headers:
Authorization: Basic {Base64(ClientID:ClientSecret)}
```

**使用 PKCE：** 添加 `code_verifier` 参数。

### 响应

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "refresh_token": "eyJ...",
  "expires_in": 3600,
  "scope": "user:read:user",
  "api_url": "https://api.zoom.us"
}
```

### 刷新令牌

```bash
POST https://zoom.us/oauth/token?grant_type=refresh_token&refresh_token={REFRESH_TOKEN}

Headers:
Authorization: Basic {Base64(ClientID:ClientSecret)}
```

- 访问令牌在**1小时**后过期
- 刷新令牌的有效期可能不同；某些基于用户的流程中，~90天是常见的。将其视为可配置的行为，依赖运行时错误和重新认证回退。
- 始终使用最新的刷新令牌进行下一个请求
- 如果刷新令牌过期，将用户重定向到授权URL以重新启动流程

### 用户级与账户级应用

| 类型 | 谁可以授权 | 范围访问 |
|------|-------------------|--------------|
| **用户级** | 任何个人用户 | 限制为自己 |
| **账户级** | 具有管理员权限的用户 | 账户范围访问（管理员范围） |

---

## 设备授权（设备流程）

用于没有浏览器的设备（例如，会议SDK应用）。

### 前置条件

在功能 > 嵌入 > 启用会议SDK中启用“在设备上使用应用”

### 第一步：请求设备代码

```bash
POST https://zoom.us/oauth/devicecode?client_id={CLIENT_ID}

Headers:
Authorization: Basic {Base64(ClientID:ClientSecret)}
```

### 响应

```json
{
  "device_code": "DEVICE_CODE",
  "user_code": "abcd1234",
  "verification_uri": "https://zoom.us/oauth_device",
  "verification_uri_complete": "https://zoom.us/oauth/device/complete/{CODE}",
  "expires_in": 900,
  "interval": 5
}
```

### 第二步：用户授权

直接用户到：
- `verification_uri` 并显示 `user_code` 以手动输入，OR
- `verification_uri_complete` (用户代码预填充)

用户登录并允许应用。

### 第三步：轮询获取令牌

在 `interval` (5秒) 的间隔内轮询，直到用户授权：

```bash
POST https://zoom.us/oauth/token?grant_type=urn:ietf:params:oauth:grant-type:device_code&device_code={DEVICE_CODE}

Headers:
Authorization: Basic {Base64(ClientID:ClientSecret)}
```

### 响应

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "refresh_token": "eyJ...",
  "expires_in": 3599,
  "scope": "user:read:user user:read:token",
  "api_url": "https://api.zoom.us"
}
```

### 轮询响应

| 响应 | 含义 | 操作 |
|------|---------|--------|
| 返回令牌 | 用户已授权 | 存储令牌，完成 |
| `error: authorization_pending` | 用户尚未授权 | 继续在间隔内轮询 |
| `error: slow_down` | 轮询过快 | 将间隔增加5秒 |
| `error: expired_token` | 设备代码过期 (15分钟) | 从第一步重新启动流程 |
| `error: access_denied` | 用户拒绝授权 | 处理拒绝，不要重试 |

### 轮询实现

```javascript
async function pollForToken(deviceCode, interval) {
  while (true) {
    await sleep(interval * 1000);
    
    try {
      const response = await axios.post(
        `https://zoom.us/oauth/token?grant_type=urn:ietf:params:oauth:grant-type:device_code&device_code=${deviceCode}`,
        null,
        { headers: { 'Authorization': `Basic ${credentials}` } }
      );
      return response.data; // 成功 - 获取到令牌
    } catch (error) {
      const err = error.response?.data?.error;
      if (err === 'authorization_pending') continue;
      if (err === 'slow_down') { interval += 5; continue; }
      throw error; // expired_token 或 access_denied
    }
  }
}
```

### 刷新

与用户授权相同。如果刷新令牌过期，从第一步重新启动设备流程。

---

## 客户端授权（聊天机器人）

仅用于聊天机器人消息操作。

### 请求令牌

```bash
POST https://zoom.us/oauth/token?grant_type=client_credentials

Headers:
Authorization: Basic {Base64(ClientID:ClientSecret)}
```

### 响应

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600,
  "scope": "imchat:bot",
  "api_url": "https://api.zoom.us"
}
```

### 刷新

令牌在**1小时**后过期。没有刷新流程 - 只需请求新令牌。

---

## 使用访问令牌

### 调用 API

```bash
GET https://api.zoom.us/v2/users/me

Headers:
Authorization: Bearer {ACCESS_TOKEN}
```

### Me 上下文

将 `userID` 替换为 `me` 以针对令牌关联的用户：

| 端点 | 方法 |
|------|---------|
| `/v2/users/me` | GET, PATCH |
| `/v2/users/me/token` | GET |
| `/v2/users/me/meetings` | GET, POST |

---

## 撤销访问令牌

适用于所有授权类型。

```bash
POST https://zoom.us/oauth/revoke?token={ACCESS_TOKEN}

Headers:
Authorization: Basic {Base64(ClientID:ClientSecret)}
```

### 响应

```json
{
  "status": "success"
}
```

---

## PKCE（代码交换证明密钥）

用于不能安全存储秘密的公共客户端（移动应用、SPA、桌面应用）。

### 何时使用 PKCE

| 客户端类型 | 是否使用 PKCE | 原因 |
|-------------|-----------|-----|
| 移动应用 | **是** | 不能安全存储客户端密钥 |
| 单页应用 (SPA) | **是** | JavaScript 对用户可见 |
| 桌面应用 | **是** | 二进制可以被反编译 |
| 会议SDK (客户端侧) | **是** | 在用户的设备上运行 |
| 后端服务器 | 可选 | 可以存储秘密，但 PKCE 增加了安全性 |

### PKCE 工作原理

```
┌──────────┐                              ┌──────────┐                    ┌──────────┐
│  客户端  │                              │   Zoom   │                    │   Zoom   │
│   应用    │                              │  认证    │                    │  令牌    │
└────┬─────┘                              └────┬─────┘                    └────┬─────┘
     │                                         │                              │
     │ 1. 生成 code_verifier (随机)            │                              │
     │ 2. 创建 code_challenge = SHA256(verifier)                            │
     │                                         │                              │
     │ ─────── /authorize + code_challenge ──► │                              │
     │                                         │                              │
     │ ◄────── authorization_code ──────────── │                              │
     │                                         │                              │
     │ ─────────────── /token + code_verifier ─┼────────────────────────────► │
     │                                         │                              │
     │                                         │     验证：SHA256(verifier) │
     │                                         │            == challenge      │
     │                                         │                              │
     │ ◄───────────────────────────────────────┼─────── access_token ──────── │
     │                                         │                              │
```

### 实现 (Node.js)

```javascript
const crypto = require('crypto');

function generatePKCE() {
  const verifier = crypto.randomBytes(32).toString('base64url');
  const challenge = crypto.createHash('sha256').update(verifier).digest('base64url');
  return { verifier, challenge };
}

const pkce = generatePKCE();

const authUrl = `https://zoom.us/oauth/authorize?` +
  `response_type=code&` +
  `client_id=${CLIENT_ID}&` +
  `redirect_uri=${REDIRECT_URI}&` +
  `code_challenge=${pkce.challenge}&` +
  `code_challenge_method=S256`;

// 在会话中存储 pkce.verifier 以供回调使用
```

### 使用 PKCE 交换令牌

```bash
POST https://zoom.us/oauth/token?grant_type=authorization_code&code={CODE}&redirect_uri={REDIRECT_URI}&code_verifier={VERIFIER}

Headers:
Authorization: Basic {Base64(ClientID:ClientSecret)}
```

---

## 撤销授权

当用户删除您的应用时，Zoom 会向您的撤销授权通知端点URL发送webhook。

### Webhook 事件

```json
{
  "event": "app_deauthorized",
  "event_ts": 1740439732278,
  "payload": {
    "account_id": "ACCOUNT_ID",
    "user_id": "USER_ID",
    "signature": "SIGNATURE",
    "deauthorization_time": "2019-06-17T13:52:28.632Z",
    "client_id": "CLIENT_ID"
  }
}
```

### 要求

- **收到此事件后删除所有关联用户数据**
- **验证webhook签名**（使用密钥令牌，2023年10月弃用的验证令牌）
- 仅公共应用接收撤销授权webhooks（不是私有/开发应用）

---

## 预授权流程

某些Zoom账户需要在用户授权应用之前由Marketplace管理员预先批准。

- 用户可以向其管理员请求预授权
- 账户级应用（管理员范围）需要适当的角色权限

---

## 活动应用通知器 (AAN)

会议中的功能，显示具有实时内容访问权限的应用。

- 显示图标 + 提示，包含应用信息、正在访问的内容类型、批准的账户
- 支持：Zoom客户端5.6.7+、会议SDK5.9.0+

---

## OAuth 范围

### 范围类型

| 类型 | 描述 | 适用于 |
|------|-------------|-----|
| **经典范围** | 遗留范围（用户、管理员、主级别） | 现有应用 |
| **粒度范围** | 新的细粒度范围，可选支持 | 新应用 |

### 经典范围

用于先前创建的应用。三个级别：
- **用户级**：访问单个用户的数据
- **管理员级**：账户范围访问，需要管理员角色
- **主级**：用于主子账户设置，需要账户所有者

完整列表：https://developers.zoom.us/docs/integrations/oauth-scopes/

### 粒度范围

用于新应用。格式：`<服务>:<操作>:<数据声明>:<访问>`

| 组件 | 值 |
|------|--------|
| **服务** | `meeting`, `webinar`, `user`, `recording`, 等 |
| **操作** | `read`, `write`, `update`, `delete` |
| **数据声明** | 数据类别（例如，`participants`, `settings`） |
| **访问** | 空的（用户），`admin`, `master` |

示例：`meeting:read:list_meetings:admin`

完整列表：https://developers.zoom.us/docs/integrations/oauth-scopes-granular/

### 可选范围

粒度作用域可以标记为 **可选** - 用户选择是否授予权限。

**基本授权**（使用构建流程默认值）：
```
https://zoom.us/oauth/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}
```

**高级授权**（每个请求自定义作用域）：
```
https://zoom.us/oauth/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope={required_scopes}&optional_scope={optional_scopes}
```

**包含先前授予权限的作用域**：
```
https://zoom.us/oauth/authorize?...&include_granted_scopes&scope={additional_scopes}
```

### 从经典迁移到粒度

1. 管理 > 选择应用 > 编辑
2. 作用域页面 > 开发选项卡 > 点击 **迁移**
3. 审查自动分配的粒度作用域，移除不必要的，标记可选的
4. 测试
5. 生产选项卡 > 点击 **迁移**

**注意**：
- 仅迁移或减少作用域时无需审查
- 现有用户令牌将继续使用经典作用域值，直到重新授权
- 新用户在迁移后获得粒度作用域

---

## 常见错误代码

| 代码 | 消息 | 解决方案 |
|------|---------|----------|
| 4700 | 令牌不能为空 | 检查 Authorization 头部是否有有效令牌 |
| 4702/4704 | 无效客户端 | 验证 Client ID 和 Client Secret |
| 4705 | 不支持的授权类型 | 使用：`account_credentials`，`authorization_code`，`urn:ietf:params:oauth:grant-type:device_code` 或 `client_credentials` |
| 4706 | 缺少客户端 ID 或密钥 | 在头部或请求参数中添加凭证 |
| 4709 | 重定向 URI 不匹配 | 确保重定向 URI 与应用配置完全一致（包括末尾斜杠） |
| 4711 | 刷新令牌无效 | 令牌作用域与客户端作用域不匹配 |
| 4717 | 应用已被禁用 | 联系 Zoom 支持 |
| 4733 | 代码已过期 | 授权代码在 5 分钟内过期 - 重新启动流程 |
| 4734 | 无效的授权代码 | 重新生成授权代码 |
| 4735 | 令牌所有者不存在 | 用户已从账户中移除 - 重新授权 |
| 4741 | 令牌已被撤销 | 使用最新授权中最新的令牌 |

参见 `references/oauth-errors.md` 获取完整错误列表。

---

## 快速参考

| 流程 | 授权类型 | 令牌过期 | 刷新 |
|------|------------|--------------|---------|
| 账户 (S2S) | `account_credentials` | 1 小时 | 请求新令牌 |
| 用户 | `authorization_code` | 1 小时 | 使用 refresh_token (90 天过期) |
| 设备 | `urn:ietf:params:oauth:grant-type:device_code` | 1 小时 | 使用 refresh_token (90 天过期) |
| 客户端 (聊天机器人) | `client_credentials` | 1 小时 | 请求新令牌 |

---

## 演示指导

如果你构建了一个 OAuth 演示应用，请在该演示项目自己的 README 或 `.env.example` 中记录其运行时基本 URL，而不是在这个共享技能中。

## 资源

- **OAuth 文档**：https://developers.zoom.us/docs/integrations/oauth/
- **S2S OAuth 文档**：https://developers.zoom.us/docs/internal-apps/s2s-oauth/
- **PKCE 博客**：https://developers.zoom.us/blog/pcke-oauth-with-postman-rest-api/
- **经典作用域**：https://developers.zoom.us/docs/integrations/oauth-scopes/
- **粒度作用域**：https://developers.zoom.us/docs/integrations/oauth-scopes-granular/

---

## 集成索引

_本节从 `SKILL.md` 迁移而来。_

## 快速入门路径

**如果你是 Zoom OAuth 的新手，请按此顺序操作：**

1. **首先运行预检** → [RUNBOOK.md](RUNBOOK.md)

2. **选择你的 OAuth 流** → [concepts/oauth-flows.md](concepts/oauth-flows.md)
   - 4 个流程：S2S（后端），用户（SaaS），设备（无浏览器），聊天机器人
   - 决策矩阵：哪个流程适合你的用例？

3. **理解令牌生命周期** → [concepts/token-lifecycle.md](concepts/token-lifecycle.md)
   - **关键**：令牌如何过期、刷新和撤销
   - 常见陷阱：刷新令牌轮换

4. **实现你的流程** → 跳转到示例：
   - 后端自动化 → [examples/s2s-oauth-redis.md](examples/s2s-oauth-redis.md)
   - SaaS 应用 → [examples/user-oauth-mysql.md](examples/user-oauth-mysql.md)
   - 移动/SPA → [examples/pkce-implementation.md](examples/pkce-implementation.md)
   - 设备（电视/自助服务终端）→ [examples/device-flow.md](examples/device-flow.md)

5. **修复重定向 URI 问题** → [troubleshooting/redirect-uri-issues.md](troubleshooting/redirect-uri-issues.md)
   - 最常见的 OAuth 错误：重定向 URI 不匹配

6. **实现令牌刷新** → [examples/token-refresh.md](examples/token-refresh.md)
   - 自动化中间件模式
   - 处理刷新令牌轮换

7. **排错错误** → [troubleshooting/common-errors.md](troubleshooting/common-errors.md)
   - 错误代码表（4700-4741 范围）
   - 快速诊断工作流

---

## 文档结构

```
oauth/
├── SKILL.md                           # 主技能概述
├── SKILL.md                           # 此文件 - 导航指南
│
├── concepts/                          # 核心 OAuth 概念
│   ├── oauth-flows.md                # 4 个流程：S2S，用户，设备，聊天机器人
│   ├── token-lifecycle.md            # 过期，刷新，撤销
│   ├── pkce.md                       # 公共客户端的 PKCE 安全
│   ├── scopes-architecture.md        # 经典与粒度作用域
│   └── state-parameter.md            # 使用 state 防止 CSRF
│
├── examples/                          # 完整可运行代码
│   ├── s2s-oauth-basic.md            # S2S OAuth 最小示例
│   ├── s2s-oauth-redis.md            # S2S OAuth 与 Redis 缓存（生产环境）
│   ├── user-oauth-basic.md           # 用户 OAuth 最小示例
│   ├── user-oauth-mysql.md           # 用户 OAuth 与 MySQL + 加密（生产环境）
│   ├── device-flow.md                # 设备授权流程
│   ├── pkce-implementation.md        # SPA/移动应用的 PKCE
│   └── token-refresh.md              # 自动刷新中间件模式
│
├── troubleshooting/                   # 问题解决指南
│   ├── common-errors.md              # 错误代码 4700-4741
│   ├── redirect-uri-issues.md        # 最常见的 OAuth 错误
│   ├── token-issues.md               # 过期，撤销，无效令牌
│   └── scope-issues.md               # 作用域不匹配错误
│
└── references/                        # 参考文档
    ├── oauth-errors.md                # 完整错误代码参考
    ├── classic-scopes.md              # 经典作用域参考
    └── granular-scopes.md             # 粒度作用域参考
```

---

## 按用例划分

### 我想在我的账户上自动化 Zoom 任务
1. [OAuth 流程](concepts/oauth-flows.md#server-to-server-s2s-oauth) - S2S OAuth 解释
2. [S2S OAuth Redis](examples/s2s-oauth-redis.md) - 带有 Redis 缓存的生产模式
3. [令牌生命周期](concepts/token-lifecycle.md) - 1 小时令牌，无需刷新

### 我想为其他 Zoom 用户构建 SaaS 应用
1. [OAuth 流程](concepts/oauth-flows.md#user-authorization-oauth) - 用户 OAuth 解释
2. [用户 OAuth MySQL](examples/user-oauth-mysql.md) - 带有加密的生产模式
3. [令牌刷新](examples/token-refresh.md) - 自动刷新中间件
4. [重定向 URI 问题](troubleshooting/redirect-uri-issues.md) - 修复最常见的错误

### 我想构建移动或 SPA 应用
1. [PKCE](concepts/pkce.md) - 为什么公共客户端需要 PKCE
2. [PKCE 实现](examples/pkce-implementation.md) - 完整代码示例
3. [状态参数](concepts/state-parameter.md) - CSRF 防护

### 我想为没有浏览器的设备（电视，自助服务终端）构建应用
1. [OAuth 流程](concepts/oauth-flows.md#device-authorization-flow) - 设备流程解释
2. [设备流程示例](examples/device-flow.md) - 完整轮询实现
3. [常见错误](troubleshooting/common-errors.md) - 设备特定错误

### 我正在构建 Team 聊天机器人
1. [OAuth 流程](concepts/oauth-flows.md#client-authorization-chatbot) - 聊天机器人流程解释
2. [S2S OAuth 基础](examples/s2s-oauth-basic.md) - 类似模式，不同授权类型
3. [作用域架构](concepts/scopes-architecture.md) - 聊天机器人特定作用域

### 我遇到重定向 URI 错误（4709）
1. [重定向 URI 问题](troubleshooting/redirect-uri-issues.md) - **从这里开始！**
2. [常见错误](troubleshooting/common-errors.md#4709-redirect-uri-mismatch) - 错误详情
3. [用户 OAuth 基础](examples/user-oauth-basic.md) - 查看正确模式

### 我遇到令牌错误（4700-4741）
1. [令牌问题](troubleshooting/token-issues.md) - 诊断工作流
2. [令牌生命周期](concepts/token-lifecycle.md) - 理解过期
3. [令牌刷新](examples/token-refresh.md) - 实现自动刷新
4. [常见错误](troubleshooting/common-errors.md) - 错误代码表

### 我遇到作用域错误（4711）
1. [作用域问题](troubleshooting/scope-issues.md) - 不匹配原因
2. [作用域架构](concepts/scopes-architecture.md) - 经典与粒度
3. [经典作用域](references/classic-scopes.md) - 完整作用域参考
4. [粒度作用域](references/granular-scopes.md) - 粒度作用域参考

### 我需要刷新令牌
1. [令牌生命周期](concepts/token-lifecycle.md#refresh-strategy) - 何时刷新
2. [令牌刷新](examples/token-refresh.md) - 中间件模式
3. [令牌问题](troubleshooting/token-issues.md#refresh-token-problems) - 常见错误

### 我想了解经典和粒度作用域的区别
1. [作用域架构](concepts/scopes-architecture.md) - **完整比较**
2. [经典作用域](references/classic-scopes.md) - `resource:level` 格式
3. [粒度作用域](references/granular-scopes.md) - `service:action:data_claim:access` 格式

### 我需要保护我的 OAuth 实现
1. [PKCE](concepts/pkce.md) - 公共客户端安全
2. [状态参数](concepts/state-parameter.md) - CSRF 防护
3. [用户 OAuth MySQL](examples/user-oauth-mysql.md#token-encryption) - 令牌加密存储

### 我想从 JWT 应用迁移到 S2S OAuth
1. [S2S OAuth Redis](examples/s2s-oauth-redis.md) - 现代替代方案
2. [令牌生命周期](concepts/token-lifecycle.md) - 不同的令牌行为

> **注意**：JWT 应用类型已于 2023 年 6 月弃用。迁移到 S2S OAuth 以实现服务器到服务器的自动化。

---

## 最关键的文档

### 1. OAuth 流程（决策文档）
**[concepts/oauth-flows.md](concepts/oauth-flows.md)**

了解应使用哪个 4 个流程：
- **S2S OAuth**：后端自动化（你的账户）
- **用户 OAuth**：SaaS 应用（用户授权你）
- **设备流程**：无浏览器的设备
- **聊天机器人**：仅限 Team Chat 机器人

### 2. 令牌生命周期（最常见问题）
**[concepts/token-lifecycle.md](concepts/token-lifecycle.md)**

99% 的 OAuth 问题源于误解：
- 令牌过期（所有流程均为 1 小时）
- 刷新令牌轮换（必须保存新的刷新令牌）
- 撤销行为（使所有令牌无效）

### 3. 重定向 URI 问题（最常见的错误）
**[troubleshooting/redirect-uri-issues.md](troubleshooting/redirect-uri-issues.md)**

错误 4709（"重定向 URI 不匹配"）是第 1 个 OAuth 错误。
必须完全匹配（包括末尾斜杠，http 与 https）。

---

## 关键学习

### 关键发现：

1. **刷新令牌轮换**
   - 每次刷新返回一个新的刷新令牌
   - 旧的刷新令牌将失效
   - 未能保存新令牌会导致 4735 错误
   - 参考：[令牌刷新](examples/token-refresh.md)

2. **S2S OAuth 使用 Redis，用户 OAuth 使用数据库**
   - S2S：整个账户使用单个令牌 → Redis（易失性）
   - 用户：每个用户使用令牌 → 数据库（持久性）
   - 参考：[S2S OAuth Redis](examples/s2s-oauth-redis.md) vs [用户 OAuth MySQL](examples/user-oauth-mysql.md)

3. **重定向 URI 必须完全匹配**
   - 末尾斜杠很重要：`/callback` ≠ `/callback/`
   - 协议很重要：`http://` ≠ `https://`
   - 端口很重要：`:3000` ≠ `:3001`
   - 参考：[重定向 URI 问题](troubleshooting/redirect-uri-issues.md)

4. **公共客户端需要 PKCE**
   - 移动应用不能保存秘密
   - SPA 不能保存秘密
   - PKCE 防止授权代码拦截
   - 参考：[PKCE](concepts/pkce.md)

5. **状态参数防止 CSRF**
   - 在重定向前生成随机状态
   - 存储在会话中
   - 在回调时验证
   - 参考：[状态参数](concepts/state-parameter.md)

6. **令牌存储必须加密**
   - 永远不要以明文存储令牌
   - 使用 AES-256 最少
   - 参考：[用户 OAuth MySQL](examples/user-oauth-mysql.md#token-encryption)

7. **JWT 应用类型已弃用（2023 年 6 月）**
   - 不能创建新的 JWT 应用
   - 现有应用仍然有效，但最终将被淘汰
   - 迁移到 S2S OAuth 或用户 OAuth

8. **作用域级别决定授权要求**
   - 无后缀（用户级）：任何用户都可以授权
   - `:admin`：需要管理员角色
   - `:master`：需要账户所有者（多账户）
   - 参考：[作用域架构](concepts/scopes-architecture.md)

9. **授权代码在 5 分钟内过期**
   - 立即用代码交换令牌
   - 不要缓存授权代码
   - 参考：[令牌生命周期](concepts/token-lifecycle.md#authorization-code-expiration)

10. **设备流程需要轮询**
    - 以 `/devicecode` 返回的间隔轮询（通常为 5 秒）
    - 处理 `authorization_pending`，`slow_down`，`expired_token`
    - 参考：[设备流程](examples/device-flow.md)

---

## 快速参考

### “我应该使用哪个 OAuth 流？”
→ [OAuth 流程](concepts/oauth-flows.md)

### “重定向 URI 不匹配错误（4709）””
→ [重定向 URI 问题](troubleshooting/redirect-uri-issues.md)

### “令牌过期或无效”
→ [令牌问题](troubleshooting/token-issues.md)

### “刷新令牌无效（4735）””
→ [令牌刷新](examples/token-refresh.md) - 必须保存新的刷新令牌

### “作用域错误（4711）””
→ [作用域问题](troubleshooting/scope-issues.md)

### “如何保护我的 OAuth 应用？””
→ [PKCE](concepts/pkce.md) + [状态参数](concepts/state-parameter.md)

### “如何实现自动刷新？””
→ [令牌刷新](examples/token-refresh.md)

### “经典和粒度作用域的区别是什么？””
→ [作用域架构](concepts/scopes-architecture.md)

### “什么错误代码代表什么？””
→ [常见错误](troubleshooting/common-errors.md)

---

## 文档版本

基于 **Zoom OAuth API v2**（2024+）

**已弃用**：JWT 应用类型（2023 年 6 月）

---

**祝你编程愉快！**

记住：从 [OAuth 流程](concepts/oauth-flows.md) 开始，了解哪个流程适合你的用例！

## 环境变量

- 参考 [references/environment-variables.md](references/environment-variables.md) 获取标准化的 `.env` 键和每个值的位置。
