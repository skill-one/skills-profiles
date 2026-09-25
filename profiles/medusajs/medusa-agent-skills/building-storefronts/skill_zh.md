# Medusa Storefront 开发

Medusa 用于构建 storefront 的前端集成指南。涵盖 SDK 使用、React Query 模式以及调用自定义 API 路由。

## 何时应用

**为任何 storefront 开发任务加载此技能，包括：**
- 从 storefront 调用自定义 Medusa API 路由
- 在前端应用程序中集成 Medusa SDK
- 使用 React Query 进行数据获取
- 实现带乐观更新的变异
- 错误处理和缓存失效

**当构建 storefront 调用的后端 API 路由时，也加载 building-with-medusa**

## 关键：按需加载参考文件

**下方的快速参考不足以实现功能。** 在编写 storefront 集成代码之前，你必须加载参考文件。

**在实现 storefront 功能时加载此参考：**

- **调用 API 路由？** → 必须先加载 `references/frontend-integration.md`
- **使用 SDK？** → 必须先加载 `references/frontend-integration.md`
- **实现 React Query？** → 必须先加载 `references/frontend-integration.md`

## 按优先级分类的规则类别

| 优先级 | 类别 | 影响 | 前缀 |
|----------|----------|--------|--------|
| 1 | SDK 使用 | 关键 | `sdk-` |
| 2 | React Query 模式 | 高 | `query-` |
| 3 | 数据显示 | 高（包括关键价格规则） | `display-` |
| 4 | 错误处理 | 中 | `error-` |

## 快速参考

### 1. SDK 使用（关键）

- `sdk-always-use` - **始终使用 Medusa JS SDK 进行所有 API 请求** - 永远不要使用常规的 fetch()
- `sdk-existing-methods` - 对于内置端点，使用现有的 SDK 方法 (`sdk.store.product.list()`, `sdk.admin.order.retrieve()`)
- `sdk-client-fetch` - 对于自定义 API 路由，使用 `sdk.client.fetch()`
- `sdk-required-headers` - SDK 自动添加所需的头部（商店的发布 API 密钥，管理员的认证）- 常规的 fetch() 缺少这些头部会导致错误
- `sdk-no-json-stringify` - **永远不要在 body 上使用 JSON.stringify()** - SDK 自动处理序列化
- `sdk-plain-objects` - 将普通 JavaScript 对象传递给 body，而不是字符串
- `sdk-locate-first` - 在使用 SDK 之前，始终定位项目中的 SDK 实例位置

### 2. React Query 模式（高）

- `query-use-query` - 使用 `useQuery` 进行 GET 请求（数据获取）
- `query-use-mutation` - 使用 `useMutation` 进行 POST/DELETE 请求（变异）
- `query-invalidate` - 在 `onSuccess` 中使查询失效，以在变异后刷新数据
- `query-keys-hierarchical` - 按层次结构构建查询键，以有效管理缓存
- `query-loading-states` - 始终处理 `isLoading`, `isPending`, `isError` 状态

### 3. 数据显示（高）

- `display-price-format` - **关键**：Medusa 存储的价格保持原样（$49.99 = 49.99，不是以分为单位）。直接显示它们 - 永远不要除以 100

### 4. 错误处理（中）

- `error-on-error` - 在变异中实现 `onError` 回调以处理失败
- `error-display` - 当变异失败时向用户显示错误消息
- `error-rollback` - 使用乐观更新并在错误时回滚，以获得更好的用户体验

## 关键 SDK 模式

**始终将普通对象传递给 SDK - 永远不要使用 JSON.stringify():**

```typescript
// ✅ 正确 - 普通对象
await sdk.client.fetch("/store/reviews", {
  method: "POST",
  body: {
    product_id: "prod_123",
    rating: 5,
  }
})

// ❌ 错误 - JSON.stringify() 会破坏请求
await sdk.client.fetch("/store/reviews", {
  method: "POST",
  body: JSON.stringify({  // ❌ 不要这样做！
    product_id: "prod_123",
    rating: 5,
  })
})
```

**为什么这很重要：**
- SDK 自动处理 JSON 序列化
- 使用 JSON.stringify() 会导致双重序列化并破坏请求
- 服务器无法解析 body

## 常见错误检查清单

在实现之前，验证你没有做这些：

**SDK 使用：**
- [ ] 使用常规的 fetch() 而不是 Medusa JS SDK（导致缺少头部错误）
- [ ] 不使用现有的 SDK 方法进行内置端点（例如，使用 sdk.client.fetch("/store/products") 而不是 sdk.store.product.list()）
- [ ] 在 body 参数上使用 JSON.stringify()
- [ ] 手动设置 Content-Type 头部（SDK 会添加它们）
- [ ] 硬编码 SDK 导入路径（先定位项目中的位置）
- [ ] 不使用 sdk.client.fetch() 进行自定义路由

**React Query：**
- [ ] 变异后不使查询失效
- [ ] 使用扁平查询键而不是层次结构
- [ ] 不处理加载和错误状态
- [ ] 忘记在变异期间禁用按钮（isPending）

**数据显示：**
- [ ] **关键**：在显示时除以 100（价格存储为原样：$49.99 = 49.99，不是以分为单位）

**错误处理：**
- [ ] 不实现 onError 回调
- [ ] 不向用户显示错误消息
- [ ] 不优雅地处理网络故障

## 如何使用

**要获取详细的模式和示例，加载参考文件：**

```
references/frontend-integration.md - SDK 使用、React Query 模式、API 集成
```

参考文件包含：
- 步步 SDK 集成模式
- 完整的 React Query 示例
- 正确与错误的代码示例
- 查询键最佳实践
- 乐观更新模式
- 错误处理策略

## 何时使用 MedusaDocs MCP 服务器

**为（主要来源）使用此技能：**
- 如何从 storefront 调用自定义 API 路由
- SDK 使用模式（sdk.client.fetch）
- React Query 集成模式
- 常见错误和反模式

**为（次要来源）使用 MedusaDocs MCP 服务器：**
- 内置 SDK 方法（sdk.admin.*, sdk.store.*）
- 官方 Medusa SDK API 参考
- 框架特定的配置选项

**为什么技能优先：**
- 技能包含关键模式，如“不要使用 JSON.stringify”，MCP 没有强调
- 技能显示正确与错误的模式；MCP 显示的是可能实现的功能
- 规划需要理解模式，而不仅仅是 API 参考

## 与后端的集成

**⚠️ 关键：始终使用 Medusa JS SDK - 永远不要使用常规的 fetch()**

当构建跨越后端和前端的特性时：

1. **后端（building-with-medusa 技能）：** 模块 → 工作流 → API 路由
2. **storefront（此技能）：** SDK → React Query → UI 组件
3. **连接：**
   - 内置端点：使用现有的 SDK 方法 (`sdk.store.product.list()`)
   - 自定义 API 路由：使用 `sdk.client.fetch("/store/my-route")`
   - **永远不要使用常规的 fetch()** - 缺少发布 API 密钥会导致错误

**为什么需要 SDK：**
- Store 路由需要 `x-publishable-api-key` 头部
- Admin 路由需要 `Authorization` 和会话头部
- SDK 自动处理所有所需的头部
- 没有头部的常规 fetch() → 认证/授权错误

参考 `building-with-medusa` 了解后端 API 路由模式。
