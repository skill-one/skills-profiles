# Zoom OAuth

Zoom 认证和令牌生命周期行为的背景参考。优先考虑 `setup-zoom-oauth`，然后使用此技能进行精确的流程、范围和错误详细信息。

# Zoom OAuth

Zoom API 的认证和授权。

## 📖 完整文档

有关全面指南、生产模式和故障排除，请参阅**下方的集成索引部分**。

快速导航：
- **[5分钟运行手册](RUNBOOK.md)** - 深度调试之前的预检
- **[OAuth 流程](concepts/oauth-flows.md)** - 使用哪个流程以及每个流程如何工作
- **[令牌生命周期](concepts/token-lifecycle.md)** - 过期、刷新和撤销
- **[生产示例](examples/s2s-oauth-redis.md)** - Redis 缓存、MySQL 存储、自动刷新
- **[故障排除](troubleshooting/common-errors.md)** - 错误代码 4700-4741

## 前提条件

- 在 [Marketplace](https://marketplace.zoom.us/) 中创建的 Zoom 应用
- 客户端 ID 和客户端密钥
- 对于 S2S OAuth：账户 ID

## 四种授权用例

| 用例 | 应用类型 | 授权类型 | 行业名称 |
|------|----------|------------|---------------|
| **账户授权** | 服务器到服务器 | `account_credentials` | 客户端凭证授权、M2M、两脚OAuth |
| **用户授权** | 一般 | `authorization_code` | 授权码授权、三脚OAuth |
| **设备授权** | 一般 | `urn:ietf:params:oauth:grant-type:device_code` | 设备授权授权 (RFC 8628) |
| **客户端授权** | 一般 | `client_credentials` | 客户端凭证授权 (聊天机器人范围) |

### 行业术语

| 术语 | 含义 |
|------|---------|
| **两脚OAuth** | 没有用户参与（客户端 ↔ 服务器） |
| **三脚OAuth** | 用户参与（用户 ↔ 客户端 ↔ 服务器） |
| **M2M** | 机器到机器（后端服务） |
| **公共客户端** | 不能保持秘密（移动设备、SPA）→ 使用 PKCE |
| **机密客户端** | 可以保持秘密（后端服务器） |
| **PKCE** | 代码交换证明密钥 (RFC 7636)，发音为 "pixy" |

### 我应该使用哪个流程？

```
                              ┌─────────────────────┐
                              │  你在构建什么？       │
                              │  (What are you       │
                              │  building?)          │
                              └──────────┬──────────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    │                    │                    │
                    ▼                    ▼                    ▼
          ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
          │  后端          │  │  为其他用户/账   │  │  仅聊天机器人    │
          │  自动化        │  │  户构建的应用    │  │  (团队聊天)    │
          │  (你的账户)    │  │                 │  │                 │
          └────────┬────────┘  └────────┬────────┘  └────────┬────────┘
                   │                    │                    │
                   ▼                    │                    ▼
          ┌─────────────────┐           │           ┌─────────────────┐
          │    账户        │           │           │     客户端      │
          │   (S2S OAuth)   │           │           │   (聊天机器人)     │
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
          │ 示例：               │         │ + 如果是公共客户端，则使用 PKCE       │
          │ • 智能电视              │         │                 │
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

访问令牌在 **1 小时** 后过期。没有单独的刷新流程 - 只需请求新令牌。

---

## 用户授权（授权码流程）

用于代表用户操作的应用。

### 第一步：将用户重定向到授权

```
https://zoom.us/oauth/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}
```

使用 `https://zoom.us/oauth/authorize` 进行同意，但使用 `https://zoom.us/oauth/token` 进行令牌交换。

**可选参数：**

| 参数 | 描述 |
|-----------|-------------|
| `state` | CSRF 保护，通过流程维护状态 |
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

- 访问令牌在 **1 小时** 后过期
- 刷新令牌的有效期可能不同；某些基于用户的流程约为 90 天。将其视为可配置的行为/功能，并依赖运行时错误+重新认证回退。
- 始终使用最新的刷新令牌进行下一个请求
- 如果刷新令牌过期，请将用户重定向到授权 URL 以重新启动流程

### 用户级与账户级应用的比较

| 类型 | 谁可以授权 | 范围访问 |
|------|-------------------|--------------|
| **用户级** | 任何单个用户 | 限制为自己 |
| **账户级** | 具有管理员权限的用户 | 账户范围访问（管理员范围） |

---

## 设备授权（设备流程）

用于没有浏览器的设备（例如，会议SDK应用）。

### 前提条件

在：功能 > 嵌入 > 启用会议SDK 中启用 "在设备上使用应用"

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
- `verification_uri` 并显示 `user_code` 以供手动输入，OR
- `verification_uri_complete`（用户代码预填充）

用户登录并允许应用。

### 第三步：轮询以获取令牌

在 `interval`（5 秒）轮询，直到用户授权：

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
|----------|---------|--------|
| 返回令牌 | 用户授权 | 存储令牌，完成 |
| `error: authorization_pending` | 用户尚未授权 | 继续轮询 at interval |
| `error: slow_down` | 轮询太快 | 将 interval 增加到 5 秒 |
| `error: expired_token` | 设备代码过期（15 分钟） | 重新启动流程从第一步 |
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

与用户授权相同。如果刷新令牌过期，则从第一步重新启动设备流程。

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

令牌在 **1 小时** 后过期。没有刷新流程 - 只需请求新令牌。

---

## 使用访问令牌

### 调用 API

```bash
GET https://api.zoom.us/v2/users/me

Headers:
Authorization: Bearer {ACCESS_TOKEN}
```

### Me 上下文

将 `userID` 替换为 `me` 以针对关联用户：

| 端点 | 方法 |
|----------|---------|
| `/v2/users/me` | GET, PATCH |
| `/v2/users/me/token` | GET |
| `/v2/users/me/meetings` | GET, POST |

---

## 注销访问令牌

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

用于无法安全存储秘密的公共客户端（移动应用、SPA、桌面应用）。

### 何时使用 PKCE

| 客户端类型 | 使用 PKCE? | 原因 |
|-------------|-----------|-----|
| 移动应用 | **是** | 不能安全存储客户端密钥 |
| 单页应用 (SPA) | **是** | JavaScript 对用户可见 |
| 桌面应用 | **是** | 二进制可以被反编译 |
| 会议SDK（客户端端） | **是** | 在用户的设备上运行 |
| 后端服务器 | 可选 | 可以存储秘密，但 PKCE 增加了安全性 |

### PKCE 如何工作

```
┌──────────┐                              ┌──────────┐                    ┌──────────┐
│  客户端  │                              │   Zoom   │                    │   Zoom   │
│   应用    │                              │  认证    │                    │  令牌    │
└────┬─────┘                              └────┬─────┘                    └────┬─────┘
     │                                         │                              │
     │ 1. 生成 code_verifier (随机)      │                              │
     │ 2. 创建 code_challenge = SHA256(verifier)                            │
     │                                         │                              │
     │ ─────── /authorize + code_challenge ──► │                              │
     │                                         │                              │
     │ ◄────── authorization_code ──────────── │                              │
     │                                         │                              │
     │ ─────────────── /token + code_verifier ─┼────────────────────────────► │
     │                                         │                              │
     │                                         │     验证: SHA256(verifier) │
     │                                         │            == challenge      │
     │                                         │                              │
     │ ◄───────────────────────────────────────┼─────── access_token ──────── │
     │                                         │                              │
```

### 实现（Node.js）

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

// 将 pkce.verifier 存储在会话中，以便在回调时使用
```

### 使用 PKCE 进行令牌交换

```bash
POST https://zoom.us/oauth/token?grant_type=authorization_code&code={CODE}&redirect_uri={REDIRECT_URI}&code_verifier={VERIFIER}

Headers:
Authorization: Basic {Base64(ClientID:ClientSecret)}
```

---

## 注销授权

当用户删除您的应用时，Zoom 会向您的注销通知端点 URL 发送 webhook。

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

- **删除所有关联用户数据** 在收到此事件后
- **验证 webhook 签名**（使用秘密令牌，验证令牌已于 2023 年 10 月弃用）
- 仅公共应用接收注销 webhook（不是私有/开发应用）

---

## 预授权流程

某些 Zoom 账户需要在 Marketplace 管理员预批准后才能使用应用。

- 用户可以向他们的管理员请求预授权
- 账户级应用（管理员范围）需要适当的角色权限

---

## 活动应用通知器 (AAN)

会议中的功能，显示具有实时访问内容的应用。

- 显示图标 + 提示，其中包含应用信息、正在访问的内容类型、批准的账户
- 支持：Zoom 客户端 5.6.7+、会议SDK 5.9.0+

---

## OAuth 范围

### 范围类型

| 类型 | 描述 | 用于 |
|------|-------------|-----|
| **经典范围** | 遗留范围 (用户、管理员、主级别) | 现有应用 |
| **粒度范围** | 新的细粒度范围，可选支持 | 新应用 |

### 经典范围

用于先前创建的应用。三个级别：
- **用户级**：访问单个用户的数据
- **管理员级**：账户范围访问，需要管理员角色
- **主级别**：用于主子账户设置，需要账户所有者

完整列表：https://developers.zoom.us/docs/integrations/oauth-scopes/

### 粒度范围

用于新应用。格式：`<服务>:<操作>:<数据声明>:<访问>`

| 组件 | 值 |
|-----------|--------|
| **服务** | `meeting`, `webinar`, `user`, `recording`, 等。 |
| **操作** | `read`, `write`, `update`, `delete` |
| **数据声明** | 数据类别 (例如，`participants`, `settings`) |
| **访问** | 空的 (用户), `admin`, `master` |

示例：`meeting:read:list_meetings:admin`

完整列表：https://developers.zoom.us/docs/integrations/oauth-scopes-granular/

### 可选范围

粒度范围可以标记为**可选** - 用户选择是否授予它们。

**基本授权**（使用 build 流程默认值）:
```
https://zoom.us/oauth/authorize?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}
```

**高级授权**（每个请求自定义范围）:
```
https://zoom.us/oauth/authorize?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope={required_scopes}&optional_scope={optional_scopes}
```

**包含先前授予的范围**:
```
https://zoom.us/oauth/authorize?...&include_granted_scopes&scope={additional_scopes}
```

### 从经典迁移到粒度

1. 管理 > 选择应用 > 编辑
2. 范围页面 > 开发选项卡 > 点击 **迁移**
3. 审查自动分配的粒度范围，删除不必要的，标记为可选
4. 测试
5. 生产选项卡 > 点击 **迁移**

**注意：**
- 如果只是迁移或减少范围，则不需要审查
- 现有用户令牌将继续使用经典范围值，直到重新授权
- 新用户在迁移后获得粒度范围

---

## 常见错误代码

| 代码 | 消息 | 解决方案 |
|------|---------|----------|
| 4700 | 令牌不能为空 | 检查 Authorization 头部是否包含有效令牌 |
| 4702/4704 | 无效客户端 | 验证 Client ID 和 Client Secret |
| 4705 | 授权类型不受支持 | 使用: `account_credentials`, `authorization_code`, `urn:ietf:params:oauth:grant-type:device_code`, 或 `client_credentials` |
| 4706 | 客户端 ID 或密钥缺失 | 将凭证添加到头部或请求参数 |
| 4709 | 重定向 URI 不匹配 | 确保重定向 URI 与应用配置完全匹配（包括尾部斜杠） |
| 4711 | 刷新令牌无效 | 令牌范围与客户端范围不匹配 |
| 4717 | 应用已被禁用 | 联系 Zoom 支持 |
| 4733 | 代码已过期 | 授权码在 5 分钟内过期 - 重新启动流程 |
| 4734 | 无效的授权码 | 重新生成授权码 |
| 4735 | 令牌的所有者不存在 | 用户已被从账户中删除 - 重新授权 |
| 4741 | 令牌已被撤销 | 使用最新的令牌（最新的授权） |

参见 `references/oauth-errors.md` 获取完整错误列表。

---

## 快速参考

| 流程 | 授权类型 | 令牌过期 | 刷新 |
|------|------------|--------------|---------|
| 账户 (S2S) | `account_credentials` | 1 小时 | 请求新令牌 |
| 用户 | `authorization_code` | 1 小时 | 使用 refresh_token (90 天有效期) |
| 设备 | `urn:ietf:params:oauth:grant-type:device_code` | 1 小时 | 使用 refresh_token (90 天有效期) |
| 客户端 (聊天机器人) | `client_credentials` | 1 小时 | 请求新令牌 |

---

## Demo 指导

如果你构建了一个 OAuth 示例应用，请在该示例项目的自己的 README 或 `.env.example` 中记录其运行时基本 URL，而不是在此共享技能中。

## 资源

- **OAuth 文档**: https://developers.zoom.us/docs/integrations/oauth/
- **S2S OAuth 文档**: https://developers.zoom.us/docs/internal-apps/s2s-oauth/
- **PKCE 博客**: https://developers.zoom.us/blog/pcke-oauth-with-postman-rest-api/
- **经典范围**: https://developers.zoom.us/docs/integrations/oauth-scopes/
- **粒度范围**: https://developers.zoom.us/docs/integrations/oauth-scopes-granular/

---

## 集成索引

_本节从 `SKILL.md` 迁移而来。_

## 快速入门路径

**如果你是 Zoom OAuth 的新手，请按照以下顺序操作：**

1. **首先进行预检** → [RUNBOOK.md](RUNBOOK.md)

2. **选择你的 OAuth 流程** → [concepts/oauth-flows.md]
   - 4 个流程：S2S (后端), 用户 (SaaS), 设备 (无浏览器), 聊天机器人
   - 决策矩阵：哪个流程适合你的用例？

3. **了解令牌生命周期** → [concepts/token-lifecycle.md]
   - **关键**：令牌如何过期、刷新和撤销
   - 常见陷阱：刷新令牌轮换

4. **实现你的流程** → 跳转到示例：
   - 后端自动化 → [examples/s2s-oauth-redis.md]
   - SaaS 应用 → [examples/user-oauth-mysql.md]
   - 移动设备/SPA → [examples/pkce-implementation.md]
   - 设备 (电视/机架) → [examples/device-flow.md]

5. **解决重定向 URI 问题** → [troubleshooting/redirect-uri-issues.md]
   - 最常见的 OAuth 错误：重定向 URI 不匹配

6. **实现令牌刷新** → [examples/token-refresh.md]
   - 自动化中间件模式
   - 处理刷新令牌轮换

7. **解决错误** → [troubleshooting/common-errors.md]
   - 错误代码表 (4700-4741 范围)
   - 快速诊断工作流程

---

## 文档结构

```
oauth/
├── SKILL.md                           # 主要技能概述
│
├── SKILL.md                           # 此文件 - 导航指南
│
├── concepts/                          # 核心 OAuth 概念
│   ├── oauth-flows.md                # 4 流程：S2S, 用户, 设备, 聊天机器人
│   ├── token-lifecycle.md            # 过期、刷新、撤销
│   ├── pkce.md                       # 公共客户端的安全
│   ├── scopes-architecture.md        # 经典与粒度范围的比较
│   └── state-parameter.md            # CSRF 保护与 state
│
├── examples/                          # 完整工作代码
│   ├── s2s-oauth-basic.md            # S2S OAuth 最小示例
│   ├── s2s-oauth-redis.md            # S2S OAuth 与 Redis 缓存 (生产)
│   ├── user-oauth-basic.md           # 用户 OAuth 最小示例
│   ├── user-oauth-mysql.md           # 用户 OAuth 与 MySQL + 加密 (生产)
│   ├── device-flow.md                # 设备流程
│   ├── pkce-implementation.md        # SPA/移动应用的 PKCE
│   └── token-refresh.md              # 自动刷新中间件模式
│
├── troubleshooting/                   # 问题解决指南
│   ├── common-errors.md              # 错误代码 4700-4741
│   ├── redirect-uri-issues.md        # 最常见的 OAuth 错误
│   ├── token-issues.md               # 令牌问题
│   └── scope-issues.md               # 范围问题
│
└── references/                        # 参考 文档
    ├── oauth-errors.md                # 完整错误代码参考
    ├── classic-scopes.md              # 经典范围参考
    └── granular-scopes.md             # 粒度范围参考
```

---

## 按用例划分

### 我想在我的自己的账户上自动化 Zoom 任务
1. [OAuth 流程](concepts/oauth-flows.md#server-to-server-s2s-oauth) - S2S OAuth 解释
2. [S2S OAuth Redis](examples/s2s-oauth-redis.md) - 生产模式
3. [令牌生命周期](concepts/token-lifecycle.md) - 1 小时令牌，无刷新

### 我想为其他 Zoom 用户构建 SaaS 应用
1. [OAuth 流程](concepts/oauth-flows.md#user-authorization-oauth) - 用户 OAuth 解释
2. [用户 OAuth MySQL](examples/user-oauth-mysql.md) - 生产模式
3. [令牌刷新](examples/token-refresh.md) - 自动刷新中间件
4. [重定向 URI 问题](troubleshooting/redirect-uri-issues.md) - 解决最常见的错误

### 我想构建移动设备或 SPA 应用
1. [PKCE](concepts/pkce.md) - 公共客户端需要 PKCE
2. [PKCE 实现](examples/pkce-implementation.md) - 完整代码示例
3. [State 参数](concepts/state-parameter.md) - CSRF 保护

### 我想为没有浏览器的设备构建应用（电视、机架）
1. [OAuth 流程](concepts/oauth-flows.md#device-authorization-flow) - 设备流程解释
2. [设备流程示例](examples/device-flow.md) - 完整轮询实现
3. [常见错误](troubleshooting/common-errors.md) - 设备特定错误

### 我想构建 Team Chat 机器人
1. [OAuth 流程](concepts/oauth-flows.md#client-authorization-chatbot) - 聊天机器人流程解释
2. [S2S OAuth 基本示例](examples/s2s-oauth-basic.md) - 类似模式，不同授权类型
3. [范围架构](concepts/scopes-architecture.md) - 聊天机器人特定范围

### 我遇到重定向 URI 错误（4709）
1. [重定向 URI 问题](troubleshooting/redirect-uri-issues.md) - **从这里开始!**
2. [常见错误](troubleshooting/common-errors.md#4709-redirect-uri-mismatch) - 错误详细信息
3. [用户 OAuth 基本示例](examples/user-oauth-basic.md) - 查看正确模式

### 我遇到令牌错误（4700-4741）
1. [令牌问题](troubleshooting/token-issues.md) - 诊断工作流程
2. [令牌生命周期](concepts/token-lifecycle.md) - 了解过期
3. [令牌刷新](examples/token-refresh.md) - 实现自动刷新
4. [常见错误](troubleshooting/common-errors.md) - 错误代码表

### 我如何保护我的 OAuth 应用？
→ [PKCE](concepts/pkce.md) + [State Parameter](concepts/state-parameter.md)

### 我如何实现自动刷新？
→ [Token Refresh](examples/token-refresh.md)

### 经典范围和粒度范围的区别是什么？
→ [Scopes Architecture](concepts/scopes-architecture.md)

### 哪个错误代码代表什么？
→ [Common Errors](troubleshooting/common-errors.md)

---

## 文档版本

基于 **Zoom OAuth API v2** (2024+)

**已弃用:** JWT 应用类型 (2023 年 6 月)

---

**快乐编码！**

记住：从 [OAuth Flows](concepts/oauth-flows.md) 开始，了解哪个流程适合你的用例！

## 环境变量

- 请参阅 [references/environment-variables.md](references/environment-variables.md) 以获取标准化的 `.env` 键以及每个值的位置。
