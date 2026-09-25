# Chrome 扩展模式

## 严重规则

1. OAuth（Google、GitHub 等）和 SAML 不支持在弹出窗口或侧面板中使用——使用 `syncHost` 将认证委托给您的 Web 应用
2. 邮件链接（魔法链接）在弹出窗口中无效——当用户点击外部时，弹出窗口关闭并重置登录状态
3. 侧面板不会自动刷新认证状态——用户必须在 Web 应用中登录后关闭并重新打开侧面板
4. 服务工作者和内容脚本无法访问 Clerk React 钩子——使用 `createClerkClient()` 或消息传递
5. 扩展 URL 使用 `chrome-extension://` 而不是 `http://`——所有重定向 URL 必须使用 `chrome.runtime.getURL('.')`
6. 没有稳定的 CRX ID，每次重建都会破坏认证——在部署前在清单中配置 `key`
7. 由于源限制，内容脚本不能直接使用 Clerk——Clerk 强制执行严格的允许源
8. 必须在 Clerk 控制面板中禁用机器人保护——Cloudflare 机器人检测在扩展环境中不受支持

## 认证选项

| 方法 | 弹出窗口 | 侧面板 | syncHost（与 Web 应用） |
|------|----------|--------|------------------------|
| 邮件 + OTP | 是 | 是 | 是 |
| 邮件 + 链接 | 否 | 否 | 是 |
| 邮件 + 密码 | 是 | 是 | 是 |
| 用户名 + 密码 | 是 | 是 | 是 |
| SMS + OTP | 是 | 是 | 是 |
| OAuth（Google、GitHub 等） | **否** | **否** | **是** |
| SAML | **否** | **否** | **是** |
| Passkeys | 是 | 是 | 是 |
| Google One Tap | 否 | 否 | 是 |
| Web3 | 否 | 否 | 是 |

## 快速入门（Plasmo）

```bash
npx create-plasmo --with-tailwindcss --with-src my-extension
cd my-extension
npm install @clerk/chrome-extension
```

在 Clerk 控制面板下 Native 应用中启用 **Native API**。所有扩展集成都需要此功能。

`.env.development`:
```
PLASMO_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_FRONTEND_API=https://your-app.clerk.accounts.dev
```

`src/popup.tsx`:
```tsx
import { ClerkProvider, Show, SignInButton, SignUpButton, UserButton } from '@clerk/chrome-extension'

const PUBLISHABLE_KEY = process.env.PLASMO_PUBLIC_CLERK_PUBLISHABLE_KEY
const EXTENSION_URL = chrome.runtime.getURL('.')

if (!PUBLISHABLE_KEY) {
  throw new Error('Missing PLASMO_PUBLIC_CLERK_PUBLISHABLE_KEY')
}

function IndexPopup() {
  return (
    <ClerkProvider
      publishableKey={PUBLISHABLE_KEY}
      afterSignOutUrl={`${EXTENSION_URL}/popup.html`}
      signInFallbackRedirectUrl={`${EXTENSION_URL}/popup.html`}
      signUpFallbackRedirectUrl={`${EXTENSION_URL}/popup.html`}
    >
      <Show when="signed-out">
        <SignInButton mode="modal" />
        <SignUpButton mode="modal" />
      </Show>
      <Show when="signed-in">
        <UserButton />
      </Show>
    </ClerkProvider>
  )
}

export default IndexPopup
```

使用 `mode="modal"` 对于 `SignInButton`——导航到单独页面会破坏弹出窗口流程。

## syncHost -- 与 Web 应用同步认证

当您需要 OAuth、SAML 或希望扩展反映 Web 应用的登录状态时使用此功能。

**工作原理**：扩展通过 `host_permissions` 从您的 Web 应用域读取 Clerk 会话 Cookie。

**步骤 1 -- 环境变量**：

`.env.development`:
```
PLASMO_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_FRONTEND_API=https://your-app.clerk.accounts.dev
PLASMO_PUBLIC_CLERK_SYNC_HOST=http://localhost
```

`.env.production`:
```
PLASMO_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_...
CLERK_FRONTEND_API=https://clerk.your-domain.com
PLASMO_PUBLIC_CLERK_SYNC_HOST=https://clerk.your-domain.com
```

**步骤 2 -- 添加 `syncHost` 属性**：

```tsx
const SYNC_HOST = process.env.PLASMO_PUBLIC_CLERK_SYNC_HOST

<ClerkProvider
  publishableKey={PUBLISHABLE_KEY}
  syncHost={SYNC_HOST}
  afterSignOutUrl="/"
  routerPush={(to) => navigate(to)}
  routerReplace={(to) => navigate(to, { replace: true })}
>
```

**步骤 3 -- 在 `package.json` 中配置 `host_permissions`**：

```json
{
  "manifest": {
    "key": "$CRX_PUBLIC_KEY",
    "permissions": ["cookies", "storage"],
    "host_permissions": [
      "$PLASMO_PUBLIC_CLERK_SYNC_HOST/*",
      "$CLERK_FRONTEND_API/*"
    ]
  }
}
```

**步骤 4 -- 通过 Clerk API 将扩展 ID 添加到 Web 应用的允许源**：

```bash
curl -X PATCH https://api.clerk.com/v1/instance \
  -H "Authorization: Bearer YOUR_SECRET_KEY" \
  -H "Content-type: application/json" \
  -d '{"allowed_origins": ["chrome-extension://YOUR_EXTENSION_ID"]}'
```

**在使用 syncHost 时在弹出窗口中隐藏不支持的认证方法**：

```tsx
<SignIn
  appearance={{
    elements: {
      socialButtonsRoot: 'plasmo-hidden',
      dividerRow: 'plasmo-hidden',
    },
  }}
/>
```

完整指南：`references/sync-host.md`

## createClerkClient() 用于纯 JavaScript / 服务工作者

从 `@clerk/chrome-extension/client`（不是 `@clerk/chrome-extension`）导入。

**后台服务工作者** (`src/background/index.ts`):

```typescript
import { createClerkClient } from '@clerk/chrome-extension/client'

const publishableKey = process.env.PLASMO_PUBLIC_CLERK_PUBLISHABLE_KEY

async function getToken(): Promise<string | null> {
  const clerk = await createClerkClient({
    publishableKey,
    background: true,
  })
  if (!clerk.session) return null
  return await clerk.session.getToken()
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  getToken()
    .then((token) => sendResponse({ token }))
    .catch((error) => {
      console.error('[Background] Error:', JSON.stringify(error))
      sendResponse({ token: null })
    })
  return true
})
```

`background: true` 标志即使在弹出窗口/侧面板关闭时也能保持会话新鲜。没有它，令牌将在 60 秒后过期。

**使用纯 JavaScript 的弹出窗口** (`src/popup.ts`):

```typescript
import { createClerkClient } from '@clerk/chrome-extension/client'

const EXTENSION_URL = chrome.runtime.getURL('.')
const POPUP_URL = `${EXTENSION_URL}popup.html`

const clerk = createClerkClient({ publishableKey })

clerk.load({
  afterSignOutUrl: POPUP_URL,
  signInForceRedirectUrl: POPUP_URL,
  signUpForceRedirectUrl: POPUP_URL,
  allowedRedirectProtocols: ['chrome-extension:'],
}).then(() => {
  clerk.addListener(render)
  render()
})
```

完整指南：`references/create-clerk-client.md`

## 无头扩展（无弹出窗口，无侧面板）

适用于完全在后台运行并与 Web 应用同步的扩展。

使用 `syncHost` + `createClerkClient` 并设置 `background: true` 从 Web 应用的 Cookie 中读取认证状态。

```typescript
import { createClerkClient } from '@clerk/chrome-extension/client'

const publishableKey = process.env.PLASMO_PUBLIC_CLERK_PUBLISHABLE_KEY
const syncHost = process.env.PLASMO_PUBLIC_CLERK_SYNC_HOST

async function getAuthenticatedUser() {
  const clerk = await createClerkClient({
    publishableKey,
    syncHost,
    background: true,
  })
  return clerk.user
}
```

需要在 `package.json` 中为同步主机域配置 `host_permissions`。

完整指南：`references/headless-extension.md`

## 内容脚本

内容脚本在隔离的 JavaScript 世界中注入到网页中运行。**Clerk 不能直接使用**——源限制阻止了这一点。

使用消息传递从后台服务工作者请求认证状态：

```typescript
// content.ts
async function getToken(): Promise<string | null> {
  return new Promise((resolve) => {
    chrome.runtime.sendMessage({ type: 'GET_TOKEN' }, (response) => {
      resolve(response?.token ?? null)
    })
  })
}

async function main() {
  const token = await getToken()
  if (!token) return
  // 使用令牌进行认证 API 调用
}

main()
```

完整指南：`references/content-scripts.md`

## 稳定的 CRX ID

没有固定的密钥，Chrome 在构建时从随机密钥派生 CRX ID。这每次重建都会旋转，破坏允许的源。

**选项 A -- Plasmo Itero（推荐）**：
1. 访问 [Plasmo Itero Generate Keypairs](https://itero.plasmo.com/ext/generate-keypairs)
2. 点击 "Generate KeyPairs"——安全保存私钥，复制公钥和 CRX ID

**选项 B -- OpenSSL**：
```bash
openssl genrsa -out key.pem 2048
# 使用 Plasmo Itero 将公钥转换为正确格式或提取
```

**`.env.chrome`**:
```
CRX_PUBLIC_KEY="<从 Itero 复制的公钥>"
```

**`package.json`**:
```json
{
  "manifest": {
    "key": "$CRX_PUBLIC_KEY",
    "permissions": ["cookies", "storage"],
    "host_permissions": [
      "http://localhost/*",
      "$CLERK_FRONTEND_API/*"
    ]
  }
}
```

在 Clerk 控制面板 > 允许源中添加 `chrome-extension://YOUR_STABLE_CRX_ID`。

## 令牌缓存（跨弹出窗口关闭持久化）

```tsx
const tokenCache = {
  async getToken(key: string) {
    const result = await chrome.storage.local.get(key)
    return result[key] ?? null
  },
  async saveToken(key: string, token: string) {
    await chrome.storage.local.set({ [key]: token })
  },
  async clearToken(key: string) {
    await chrome.storage.local.remove(key)
  },
}

<ClerkProvider publishableKey={PUBLISHABLE_KEY} tokenCache={tokenCache}>
```

| 存储类型 | 范围 | 清除时 |
|---|---|---|
| `chrome.storage.local` | 设备 | 卸载或手动清除 |
| `chrome.storage.session` | 会话 | 浏览器关闭 |
| `chrome.storage.sync` | 所有设备 | 卸载（大小限制，8KB） |
| `localStorage` | 弹出窗口仅 | 弹出窗口关闭——不要用于认证 |

## 常见陷阱

| 症状 | 原因 | 修复 |
|------|------|------|
| 登录时重定向循环 | ClerkProvider 属性中缺少 CRX URL | 设置 `afterSignOutUrl`，`signInFallbackRedirectUrl` |
| OAuth 按钮无效 | OAuth 不支持在弹出窗口中 | 使用 `syncHost` 委托给 Web 应用 |
| Web 应用登录后认证状态过时 | 未配置 `syncHost` | 添加 `syncHost` 属性 + `host_permissions` |
| Web 登录后侧面板显示未登录 | 已知限制 | 用户必须关闭并重新打开侧面板 |
| 后台在 60 秒后无法获取令牌 | 会话过期，没有后台刷新 | 使用 `createClerkClient({ background: true })` |
| 内容脚本无法访问 Clerk | 隔离世界 + 源限制 | 使用消息传递到后台服务工作者 |
| 重建后认证中断 | CRX ID 旋转 | 通过 `.env.chrome` 配置稳定密钥 |
| `PLASMO_PUBLIC_` 变量未定义 | 错误的环境文件 | 使用 `.env.development`，不要使用 `.env` |
| 机器人保护错误 | Cloudflare 在扩展中不受支持 | 在 Clerk 控制面板中禁用机器人保护 |
| 令牌缓存未持久化 | 在弹出窗口中使用 `localStorage` | 使用 `chrome.storage.local` 或传递 `tokenCache` 属性 |

## 计划要求

| 功能 | 计划 |
|------|------|
| 基本弹出窗口认证（邮件/密码、OTP） | 免费 |
| Passkeys | 免费 |
| syncHost | 需要 Pro（自定义域名） |
| 通过 syncHost 的 OAuth | Pro + Web 应用中配置 OAuth |
| 通过 syncHost 的 SAML | 企业 |
| 机器人保护 | 不适用——扩展必须禁用机器人保护 |

## 参见

- `clerk-setup` - 初始 Clerk 安装
- `clerk-custom-ui` - 自定义流程和外观
