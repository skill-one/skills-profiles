# ADK 前端集成

当用户询问有关构建连接到 Botpress ADK 机器人的前端应用程序时，请使用此技能。这涵盖了认证模式、类型安全的 API 调用、客户端配置以及集成生成的类型。

## 什么是 ADK 前端集成？

使用 Botpress ADK 构建机器人时，您通常需要一个与它交互的前端应用程序。此技能提供了经过生产环境测试的模式：

- **认证** - 基于 Cookie 的 PAT 存储，OAuth 流程
- **客户端管理** - Zustand 存储模式，用于客户端缓存和重用
- **类型生成** - 使用 ADK 生成的类型，实现完全的类型安全
- **动作调用** - 带有适当的错误处理和乐观更新的机器人动作调用

### 关键技术

- **@botpress/client** - Botpress API 的官方 TypeScript 客户端
- **三斜线引用** - TypeScript 用于导入生成类型的模式
- **React Query** - 用于突变和缓存管理（可选但推荐）
- **Zustand** - 用于客户端状态管理

---

## 何时使用此技能

当用户询问与前端相关的问题时，请激活此技能，例如：

### 认证问题

- "如何从前端认证 Botpress？"
- "什么是个人访问令牌（PAT）？"
- "我应该使用 Cookie 还是 localStorage 存储令牌？"
- "如何实现 OAuth 登录流程？"
- "如何根据认证保护路由？"
- "如何处理令牌过期？"

### 客户端设置问题

- "如何初始化 Botpress 客户端？"
- "管理多个客户端实例的最佳方法是什么？"
- "为什么使用客户端存储？"
- "如何创建工作区范围与机器人范围的客户端？"
- "普通客户端和 Zai 客户端有什么区别？"

### 类型生成问题

- "如何获取我机器人动作的类型？"
- "什么是三斜线引用？"
- "如何导入生成的类型？"
- "生成的 .adk 类型文件在哪里？"
- "如何保持机器人和前端之间的类型同步？"
- "为什么 TypeScript 找不到我的动作类型？"

### 调用动作问题

- "如何从前端调用机器人动作？"
- "client.callAction() 的语法是什么？"
- "调用动作时如何处理错误？"
- "如何实现乐观更新？"
- "如何链式调用多个动作？"
- "如何使用 React Query 与机器人动作？"

---

## 可用的文档

`./references/` 中的文档文件：

### 核心集成模式

- **authentication.md** - 完整的认证系统，包括 PAT、Cookie、OAuth 和路由保护
- **botpress-client.md** - 客户端初始化、Zustand 存储模式、Zai 客户端设置
- **calling-actions.md** - 类型安全的动作调用、突变、错误处理和乐观更新
- **type-generation.md** - 三斜线引用、生成的类型、保持类型安全

### 架构与设置

- **overview.md** - 架构概述、何时使用 ADK 前端、项目结构
- **project-setup.md** - Vite + React 框架、TypeScript 配置、环境设置
- **recommended-stack.md** - 推荐技术栈及其理由

### 数据与状态模式

- **service-layer.md** - 服务层模式，用于包装带类型的 API 调用
- **data-fetching.md** - TanStack Query 模式、突变、乐观更新
- **state-management.md** - Zustand 与 TanStack Query 的比较，何时使用每个
- **realtime-updates.md** - 轮询策略、间隔级别、性能考虑

---

## 如何回答前端问题

前端问题通常属于以下类别：

### 1. 认证实现

当用户询问有关认证时，参考 `authentication.md` 中的完整模式：

**关键概念：**

- Botpress Cloud 中的 PAT 生成
- 基于 Cookie 的存储（不是 localStorage）
- 使用 React Context API 的 AuthContext
- 通过 cli-login 的 OAuth 回调流程
- 使用 TanStack Router 的路由保护
- 从 Botpress API 和机器人表中获取用户资料

**响应模式：**

1. 解释认证策略（Cookie 与 localStorage）
2. 展示 AuthProvider 实现
3. 演示 OAuth 流程
4. 提供路由保护示例
5. 强调安全最佳实践

### 2. 客户端设置和管理

当用户询问有关客户端配置时，参考 `botpress-client.md`：

**关键概念：**

- 使用 apiUrl、workspaceId、token、botId 初始化客户端
- Zustand 存储用于客户端缓存
- 动态客户端键用于重用
- 工作区范围与机器人范围的客户端
- Zai 操作的扩展超时

**响应模式：**

1. 展示 clientsStore.ts 模式
2. 解释客户端缓存如何工作
3. 演示 getApiClient() 使用
4. 展示何时使用工作区与机器人范围的客户端
5. 解释 getZaiClient() 用于 AI 操作

### 3. 类型生成和导入

当用户询问有关类型时，参考 `type-generation.md`：

**关键概念：**

- ADK 在开发/构建期间在 `.adk/` 目录中生成类型
- 三斜线指令用于引用外部类型
- 生成的文件：action-types.d.ts、table-types.d.ts、workflow-types.d.ts
- 创建类型别名以使代码更清晰
- 使用 adk dev 保持类型同步

**响应模式：**

1. 解释 ADK 如何生成类型
2. 展示三斜线引用语法
3. 演示导入生成的类型
4. 提供创建类型别名的示例
5. 展示类型如何自动同步

### 4. 调用机器人动作

当用户询问有关调用动作时，参考 `calling-actions.md`：

**关键概念：**

- client.callAction() 签名
- 使用 BotActionDefinitions 的类型安全输入/输出
- 服务层模式用于可重用的动作调用
- 使用 useMutation 处理加载状态和错误
- 乐观更新以提供即时 UI 反馈
- 链式调用动作（顺序与并行）

**响应模式：**

1. 展示基本的 callAction() 语法
2. 演示类型安全的服務函数
3. 提供 useMutation 示例
4. 展示错误处理模式
5. 在相关情况下解释乐观更新

---

## 常见模式参考

### 认证流程

```typescript
// 1. Cookie 辅助函数
function setCookie(name: string, value: string, days = 365)
function getCookie(name: string): string | null
function deleteCookie(name: string)

// 2. AuthContext
interface AuthContextType {
  token: string | null
  isAuthenticated: boolean
  userProfile: UserProfile | null
  isLoadingProfile: boolean
  login: (token: string) => void
  logout: () => void
}

// 3. OAuth 流程
// 重定向：https://app.botpress.cloud/cli-login?redirect=...
// 回调：/auth/callback?pat=bp_pat_...
// 将 PAT 存储在 Cookie 中并导航到应用
```

### 客户端存储模式

```typescript
// stores/clientsStore.ts
const useClientsStore = create<ClientsState>()((set, get) => ({
  APIClients: {},
  getAPIClient: (props) => {
    const key = props?.botId ? `${props.workspaceId}-${props.botId}` : (props?.workspaceId ?? DEFAULT_API_CLIENT_KEY)

    const cached = get().APIClients[key]
    if (cached) return cached

    const newClient = new APIClient({
      apiUrl: API_BASE_URL,
      workspaceId: props?.workspaceId,
      token: getPat() ?? '',
      botId: props?.botId,
    })

    set((state) => ({
      APIClients: { ...state.APIClients, [key]: newClient },
    }))

    return newClient
  },
}))

export const getApiClient = (props?) => useClientsStore.getState().getAPIClient(props)
```

### 类型导入模式

```typescript
// types/index.ts
/// <reference path="../../../bot/.adk/action-types.d.ts" />
/// <reference path="../../../bot/.adk/table-types.d.ts" />

import type { BotActionDefinitions } from '@botpress/runtime/_types/actions'
import type { TableDefinitions } from '@botpress/runtime/_types/tables'

// 创建类型别名
export type SendMessageAction = BotActionDefinitions['sendMessage']
export type TicketTableRow = TableDefinitions['TicketsTable']['Output']
```

### 动作调用模式

```typescript
// services/bot-service.ts
export async function sendMessage(input: SendMessageAction['input']) {
  const client = getApiClient({ botId, workspaceId })
  const result = await client.callAction({
    type: 'sendMessage',
    input,
  })
  return result.output as SendMessageAction['output']
}

// 组件使用 useMutation
const { mutate: send, isPending } = useMutation({
  mutationFn: sendMessage,
  onSuccess: () => {
    toast.success('Message sent')
    queryClient.invalidateQueries({ queryKey: ['messages'] })
  },
  onError: (error) => {
    toast.error('Failed to send message')
  },
})
```

---

## 此技能回答的问题示例

### 初学者问题

- "如何将我的 React 应用连接到 Botpress 机器人？"
- "什么是个人访问令牌？"
- "我在哪里找到我的工作区 ID 和机器人 ID？"
- "如何安装 @botpress/client？"

### 认证问题

- "我应该如何存储认证令牌？"
- "如何实现登录/注销？"
- "如何保护认证路由？"
- "我应该使用 Cookie 还是 localStorage？"
- "如何处理 OAuth 回调？"

### 类型安全问题

- "如何获取 TypeScript 类型用于我的机器人？"
- "什么是三斜线引用？"
- "为什么 TypeScript 找不到我的动作类型？"
- "如何保持类型同步？"
- "生成的类型文件在哪里？"

### 实现问题

- "如何调用机器人动作？"
- "如何从前端查询机器人表？"
- "如何处理加载状态？"
- "如何实现乐观更新？"
- "如何链式调用多个动作？"

### 高级问题

- "如何从前端使用 Zai？"
- "工作区范围和机器人范围的客户端有什么区别？"
- "如何实现客户端缓存？"
- "如何处理令牌过期？"
- "如何实现重试逻辑？"

---

## 响应格式

回答时：

1. **首先简洁解释**（1-2 段）
2. **提供可工作的代码示例**来自参考
3. **包括文件参考**（例如，"从 authentication.md:60-85"）
4. **在相关情况下强调安全考虑**
5. **展示常见陷阱**以及如何避免
6. **链接到相关主题**进行深入探索

### 示例响应结构

```
问题："如何在前端认证用户？"

回答：
推荐使用基于 Cookie 的 PAT 存储和 OAuth 流程。
以下是完整实现：

1. Cookie 辅助函数（authentication.md:89-111）
   [代码示例]

2. AuthContext 设置（authentication.md:64-76）
   [代码示例]

3. OAuth 流程（authentication.md:473-533）
   [代码示例]

关键安全考虑：
- 使用 SameSite=Lax 进行 CSRF 保护
- 生产环境中始终使用 HTTPS
- 永远不要将 PAT 记录到控制台
- 实现令牌过期处理

相关主题：
- 路由保护：authentication.md:369-467
- 用户资料获取：authentication.md:304-347
- 客户端初始化：botpress-client.md:29-51
```

---

## 必须参考的关键模式

回答问题时，始终对照文档验证这些模式：

### 1. 客户端管理

```typescript
// ✅ 正确 - 使用客户端存储
const client = getApiClient({ workspaceId, botId })

// ❌ 错误 - 每次创建新客户端
const client = new Client({ apiUrl, workspaceId, token, botId })
```

### 2. 类型导入

```typescript
// ✅ 正确 - 文件顶部使用三斜线
/// <reference path="../../../bot/.adk/action-types.d.ts" />
import type { BotActionDefinitions } from '@botpress/runtime/_types/actions'

// ❌ 错误 - 没有三斜线引用
import type { BotActionDefinitions } from '@botpress/runtime/_types/actions'
```

### 3. 动作调用

```typescript
// ✅ 正确 - 服务层带类型
export async function sendMessage(input: SendMessageAction['input']) {
  const client = getApiClient({ botId, workspaceId })
  const result = await client.callAction({ type: 'sendMessage', input })
  return result.output as SendMessageAction['output']
}

// ❌ 错误 - 组件中直接调用
const result = await client.callAction({ type: 'sendMessage', input: data })
```

### 4. 认证存储

```typescript
// ✅ 正确 - 带有 SameSite 的 Cookie
document.cookie = `token=${value};expires=${expires};path=/;SameSite=Lax`

// ❌ 错误 - 没有安全措施的 localStorage
localStorage.setItem('token', value)
```

---

## 强调的最佳实践

回答时，始终提及相关最佳实践：

### 安全

- 生产环境中始终使用 HTTPS
- 使用带 SameSite 保护 的 Cookie
- 永远不要记录 PAT 或令牌
- 实现令牌过期处理
- 可能时使用 HttpOnly Cookie（SSR）

### 类型安全

- 始终使用 ADK 生成的类型
- 创建类型别名以使代码更清晰
- 正确使用三斜线引用
- 使用 adk dev 保持类型同步
- 类型所有动作输入和输出

### 性能

- 使用 Zustand 存储缓存客户端
- 当不需要机器人操作时使用工作区范围的客户端
- 实现乐观更新以提供更好的用户体验
- 使用 React Query 进行缓存管理
- 并行运行独立动作

### 错误处理

- 始终处理 401（过期令牌）错误
- 提供用户错误反馈
- 实现对暂时性失败的重试逻辑
- 适当记录错误（永远不要记录令牌）
- 在异步操作期间显示加载状态

### 代码组织

- 使用服务层进行动作调用
- 在单个文件中集中类型
- 将认证逻辑放在上下文中
- 将客户端配置与使用分离
- 在组件中重用服务函数

---

## 常见问题排查

准备好帮助解决以下常见问题：

### "找不到模块 '@botpress/runtime/_types/actions'"

- 检查三斜线引用路径
- 验证 .adk/ 目录是否存在
- 重启 TypeScript 服务器
- 确保 adk dev/build 已运行

### "机器人更改后类型未更新"

- 重启 adk dev
- 删除 .adk/ 并重新构建
- 重启 TypeScript 服务器
- 检查机器人编译错误

### "重新加载后认证失败"

- 实现重新加载重试逻辑（authentication.md:191-220）
- 检查 Cookie 过期
- 验证是否正确检索令牌
- 检查 CORS 问题

### "长操作客户端超时"

- 使用 getZaiClient() 带有扩展超时，用于 AI 操作
- 不要使用普通客户端进行 Zai 操作
- 考虑将操作拆分为更小的部分

## 总结

此技能涵盖了 Botpress ADK 完整的前端集成故事：

**核心主题：**

1. 使用 PATs 和 Cookie 的认证
2. 使用 Zustand 的客户端管理
3. 使用三斜线引用的类型生成和导入
4. 带有完全类型安全的机器人动作调用

**何时使用：**

- 任何前端集成问题
- 认证和安全模式
- 类型安全和生成类型
- 客户端设置和配置
- 动作调用和错误处理

**关键原则：**
始终提供经过生产环境测试的模式，强调类型安全、安全和可维护性。
