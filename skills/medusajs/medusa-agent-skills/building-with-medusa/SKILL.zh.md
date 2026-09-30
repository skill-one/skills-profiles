---
name: building-with-medusa
description: 在规划、研究或实施任何 Medusa 后端功能（自定义模块、API 路由、工作流、数据模型、模块链接、业务逻辑）时自动加载。在所有模式下（规划、实施、探索）的所有 Medusa 后端工作中都必需。包含 MCP 服务器不提供的架构模式、最佳实践和关键规则。
---

# Medusa 后端开发

Medusa 应用程序的全面后端开发指南。包含涵盖架构、类型安全、业务逻辑放置和常见陷阱的 6 个类别的模式。

## 何时应用

**对于任何后端开发任务，包括以下内容，请加载此技能：**
- 创建或修改自定义模块和数据模型
- 实现变异的流程
- 构建API路由（商店或管理后台）
- 定义实体之间的模块链接
- 编写业务逻辑或验证
- 跨模块查询数据
- 实现身份验证/授权

**在以下情况下也加载这些技能：**
- **building-admin-dashboard-customizations：** 构建管理界面（小部件、页面、表单）
- **building-storefronts：** 从商店调用后端API路由（SDK集成）

## 关键：按需加载参考文件

**以下快速参考不足以用于实现。** 在为该组件编写代码之前，您必须先加载相关的参考文件。

**根据您要实现的内容加载这些参考：**

- **创建模块？** → 首先必须加载 `reference/custom-modules.md`
- **创建流程？** → 首先必须加载 `reference/workflows.md`
- **创建API路由？** → 首先必须加载 `reference/api-routes.md`
- **创建模块链接？** → 首先必须加载 `reference/module-links.md`
- **查询数据？** → 首先必须加载 `reference/querying-data.md`
- **添加身份验证？** → 首先必须加载 `reference/authentication.md`

**最低要求：** 在实现之前，至少加载 1-2 个与您的特定任务相关的参考文件。

## 关键架构模式

**始终遵循此流程 - 不要跳过任何层：**

```
Module (数据模型 + CRUD操作)
  ↓ 用于
Workflow (业务逻辑 + 带回滚的变异)
  ↓ 执行
API Route (HTTP接口，验证中间件)
  ↓ 调用
Frontend (管理后台/商店通过SDK)
```

**关键约定：**
- 仅使用GET、POST、DELETE方法（从不使用PUT/PATCH）
- 所有变异都需要工作流
- 业务逻辑属于工作流步骤，而不是路由
- 使用 `query.graph()` 查询跨模块数据
- 使用 `query.index()`（索引模块）过滤跨不同模块的数据（通过链接）
- 模块链接保持模块之间的隔离

## 按优先级分类的规则类别

| 优先级 | 类别 | 影响 | 前缀 |
|----------|----------|--------|--------|
| 1 | 架构违规 | 关键 | `arch-` |
| 2 | 类型安全 | 关键 | `type-` |
| 3 | 业务逻辑放置 | 高 | `logic-` |
| 4 | 导入和代码组织 | 高 | `import-` |
| 5 | 数据访问模式 | 中等（包括关键的价格规则） | `data-` |
| 6 | 文件组织 | 中等 | `file-` |

## 快速参考

### 1. 架构违规（关键）

- `arch-workflow-required` - 使用工作流处理所有变异，不要从路由直接调用模块服务
- `arch-layer-bypass` - 不要跳过层（路由 → 没有工作流的服务）
- `arch-http-methods` - 仅使用GET、POST、DELETE（从不使用PUT/PATCH）
- `arch-module-isolation` - 使用模块链接，而不是直接跨模块服务调用
- `arch-query-config-fields` - 使用 `req.queryConfig` 时不要显式设置 `fields`

### 2. 类型安全（关键）

- `type-request-schema` - 使用 `req.validatedBody` 时，将Zod推断类型传递给 `MedusaRequest<T>`
- `type-authenticated-request` - 对于受保护的路由，使用 `AuthenticatedMedusaRequest`（而不是 `MedusaRequest`）
- `type-export-schema` - 从中间件导出Zod模式和推断类型
- `type-linkable-auto` - 不要向数据模型添加 `.linkable()`（自动添加）
- `type-module-name-camelcase` - 模块名称必须为camelCase，不要使用破折号（会导致运行时错误）

### 3. 业务逻辑放置（高）

- `logic-workflow-validation` - 将业务验证放在工作流步骤中，而不是API路由
- `logic-ownership-checks` - 在工作流中验证所有权/权限，而不是路由
- `logic-module-service` - 保持模块简单（仅CRUD），将逻辑放在工作流中

### 4. 导入和代码组织（高）

- `import-top-level` - 在文件顶部导入工作流/模块，不要在路由体中使用 `await import()`
- `import-static-only` - 使用静态导入所有依赖项
- `import-no-dynamic-routes` - 动态导入会增加开销并破坏类型检查
- `import-zod-framework` - 从 `@medusajs/framework/zod` 导入Zod，不要直接从 `zod` 导入。Medusa使用 **Zod v4**（自v2.14.0起）：使用 `z.email()`/`z.url()`/`z.uuid()` 而不是 `z.string().email()` 等，`.extend(other.shape)` 而不是 `.merge(other)`，`z.strictObject()`/`z.looseObject()` 而不是 `.strict()`/.passthrough()，`z.enum(MyEnum)` 而不是 `z.nativeEnum()`，以及 `z.record(z.string(), value)` 而不是 `z.record(value)`

### 5. 数据访问模式（中等）

- `data-price-format` - **关键**：价格在Medusa中按原样存储（49.99存储为49.99，而不是以分为单位）。保存或显示时不要乘以100或除以100
- `data-query-method` - 使用 `query.graph()` 检索数据；使用 `query.index()`（索引模块）过滤跨链接模块的数据
- `data-query-graph` - 使用 `query.graph()` 进行跨模块查询（使用点表示法，无需跨模块过滤）
- `data-query-index` - 当过滤分离模块中链接数据模型的属性时，使用 `query.index()` 或直接查询该实体
- `data-list-and-count` - 使用 `listAndCount` 进行单模块分页查询
- `data-linked-filtering` - `query.graph()` 无法过滤链接模块字段 - 使用 `query.index()` 或直接查询该实体
- `data-no-js-filter` - 不要在链接数据上使用JavaScript `.filter()`（使用数据库过滤器 `query.index()` 或直接查询链接实体）
- `data-same-module-ok` - 可以使用 `query.graph()` 过滤同模块关系（例如，product.variants）
- `data-auth-middleware` - 信任 `authenticate` 中间件，不要手动检查 `req.auth_context`

### 6. 文件组织（中等）

- `file-workflow-steps` - 推荐：在 `src/workflows/steps/[name].ts` 中创建步骤
- `file-workflow-composition` - 组合函数在 `src/workflows/[name].ts` 中
- `file-middleware-exports` - 从中间件文件导出模式和类型
- `file-links-directory` - 在 `src/links/[name].ts` 中定义模块链接

## 工作流组合规则

**工作流函数有关键约束：**

```typescript
// ✅ 正确
const myWorkflow = createWorkflow(
  "name",
  function (input) { // 普通函数，不是异步，不是箭头函数
    const result = myStep(input) // 无 await
    return new WorkflowResponse(result)
  }
)

// ❌ 错误
const myWorkflow = createWorkflow(
  "name",
  async (input) => { // ❌ 无异步，无箭头函数
    const result = await myStep(input) // ❌ 无 await
    if (input.condition) { /* ... */ } // ❌ 无条件语句
    return new WorkflowResponse(result)
  }
)
```

**约束：**
- 无 async/await（在加载时运行）
- 无箭头函数（使用 `function`）
- 无条件语句/三元运算符（使用 `when()`）
- 无变量操作（使用 `transform()`）
- 无日期创建（使用 `transform()`）
- 多个步骤调用需要 `.config({ name: "unique-name" })` 以避免冲突

## 常见错误检查清单

在实现之前，请验证您没有执行以下操作：

**架构：**
- [ ] 直接从API路由调用模块服务
- [ ] 使用PUT或PATCH方法
- [ ] 跳过工作流进行变异
- [ ] 使用 `req.queryConfig` 显式设置 `fields`
- [ ] 创建模块链接后跳过迁移

**类型安全：**
- [ ] 遗忘 `MedusaRequest<SchemaType>` 类型参数
- [ ] 对于受保护的路由，使用 `MedusaRequest` 而不是 `AuthenticatedMedusaRequest`
- [ ] 不从中间件导出Zod推断类型
- [ ] 向数据模型添加 `.linkable()`（自动添加）
- [ ] 模块名称使用破折号（必须为camelCase）

**业务逻辑：**
- [ ] 在API路由中验证业务规则
- [ ] 在路由中检查所有权，而不是工作流
- [ ] 中间件已应用时，手动检查 `req.auth_context?.actor_id`

**导入：**
- [ ] 在路由处理程序体中使用 `await import()`
- [ ] 使用动态导入工作流或模块

**数据访问：**
- [ ] **关键**：保存时乘以100，显示时除以100（价格按原样存储：$49.99 = 49.99）
- [ ] 使用 `query.graph()` 过滤链接模块字段（使用 `query.index()` 或直接查询另一侧）
- [ ] 对链接数据使用JavaScript `.filter()`（使用 `query.index()` 或直接查询链接实体）
- [ ] 不使用 `query.graph()` 进行跨模块数据检索
- [ ] 需要跨不同模块过滤时使用 `query.graph()`（使用 `query.index()` 而不是）

## 验证实现

**关键：完成实现后始终运行构建命令以捕获类型错误和运行时问题。**

### 何时验证
- 实现任何新功能后
- 修改模块、工作流或API路由后
- 标记任务完成前
- 主动进行，无需等待用户请求

### 如何运行构建

检测包管理器并运行相应的命令：

```bash
npm run build      # 或 pnpm build / yarn build
```

### 处理构建错误

如果构建失败：
1. 仔细阅读错误消息
2. 修复类型错误、导入问题和语法错误
3. 再次运行构建以验证修复
4. 构建成功之前不要标记实现为完成

**常见的构建错误：**
- 缺少导入或导出
- 类型不匹配（例如，缺少 `MedusaRequest<T>` 类型参数）
- 工作流组合不正确（异步函数、条件语句）

### 代码检查

自Medusa v2.16.0起，项目可以安装 `@medusajs/eslint-plugin`，它将捕获Medusa约定（API路由、订阅者、计划任务、管理后台自定义、模块模式）的违规行为，而类型检查无法捕获。

- 如果项目有 `eslint.config.*` 包含 `@medusajs/eslint-plugin`，**`medusa build` 和 `medusa develop` 默认运行代码检查并在代码检查错误时失败**。修复代码检查错误，而不是传递 `--no-lint`。
- 使用 `npx medusa lint` 显式运行代码检查（支持 `--fix` 和 `--quiet`）。在实现功能后运行，与构建一起运行。
- 如果项目没有ESLint配置，建议添加（`@medusajs/eslint-plugin`、`eslint` 和 `jiti` 作为开发依赖项，然后是一个导出 `defineConfig([...medusa.configs.recommended])` 的 `eslint.config.ts`）——但不要未经提示添加。

## 实现后的下一步 - 测试您的实现

**成功实现功能后，始终向用户提供以下下一步：**

### 1. 启动开发服务器

如果服务器尚未运行，请启动它：

```bash
npm run dev      # 或 pnpm dev / yarn dev
```

### 2. 访问管理后台

在浏览器中打开并导航到：
- **管理后台：** http://localhost:9000/app

使用您的管理员凭据登录以测试任何管理相关功能。

### 3. 测试API路由

如果您实现了自定义API路由，请列出它们供用户测试：

**管理路由（需要身份验证）：**
- `POST http://localhost:9000/admin/[your-route]` - 描述其功能
- `GET http://localhost:9000/admin/[your-route]` - 描述其功能

**商店路由（公开或客户身份验证）：**
- `POST http://localhost:9000/store/[your-route]` - 描述其功能
- `GET http://localhost:9000/store/[your-route]` - 描述其功能

**使用cURL的示例：**
```bash
# 管理路由（需要身份验证）
curl -X POST http://localhost:9000/admin/reviews/123/approve \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  --cookie "connect.sid=YOUR_SESSION_COOKIE"

# 商店路由
curl -X POST http://localhost:9000/store/reviews \
  -H "Content-Type: application/json" \
  -d '{"product_id": "prod_123", "rating": 5, "comment": "Great product!"}'
```

### 4. 其他测试步骤

根据实现的内容，提及：
- **工作流：** 测试变异操作并验证错误时的回滚
- **订阅者：** 触发事件并检查日志以确认订阅者执行
- **计划任务：** 等待任务执行或检查日志以获取cron输出

### 提供下一步的格式

在实现后，始终以清晰、可操作的格式提供下一步：

```markdown
## 实现完成

[功能名称] 已成功实现。以下是测试方法：

### 启动开发服务器
[基于包管理器的服务器启动命令]

### 访问管理后台
在浏览器中打开 http://localhost:9000/app

### 测试API路由
我已添加以下路由：

**管理路由：**
- POST /admin/[route] - [描述]
- GET /admin/[route] - [描述]

**商店路由：**
- POST /store/[route] - [描述]

### 需要测试的内容
1. [具体测试用例1]
2. [具体测试用例2]
3. [具体测试用例3]
```

## 如何使用

**有关详细模式和示例，请加载参考文件：**

```
reference/custom-modules.md    - 创建带有数据模型的模块
reference/workflows.md          - 工作流创建和步骤模式
reference/api-routes.md         - API路由结构和验证
reference/module-links.md       - 跨模块链接实体
reference/querying-data.md      - 查询模式和过滤规则
reference/authentication.md     - 保护路由和访问用户
reference/error-handling.md     - MedusaError类型和模式
reference/scheduled-jobs.md     - Cron任务和周期性任务
reference/subscribers-and-events.md - 事件处理
reference/troubleshooting.md    - 常见错误和解决方案
```

每个参考文件包含：
- 分步实现检查清单
- 正确与错误的代码示例
- TypeScript模式和类型安全
- 常见陷阱和解决方案

## 与MedusaDocs MCP服务器的使用时机对比

**⚠️ 关键：规划实现时，应首先咨询此技能。**

**用于（主要来源）：**
- **规划** - 了解如何构建Medusa后端功能的结构
- **架构** - 模块 → 工作流 → API路由模式
- **最佳实践** - 正确与错误的代码模式
- **关键规则** - 不要做什么（常见错误和反模式）
- **实现模式** - 带有检查清单的分步指南

**用于MedusaDocs MCP服务器（次要来源）：**
- 具体方法签名（在您知道使用哪个方法后）
- 内置模块配置选项
- 官方类型定义
- 框架级配置详细信息

**为什么技能优先：**
- 技能包含主观指导和建议MCP没有的内容
- 技能展示规划所需的架构模式
- MCP是参考材料；技能是指导性指导

## 与前端应用程序的集成

**⚠️ 关键：前端应用程序必须使用Medusa JS SDK进行所有API请求**

在构建跨越后端和前端的功能时：

**对于管理后台：**
1. **后端（此技能）：** 模块 → 工作流 → API路由
2. **前端：** 加载 `building-admin-dashboard-customizations` 技能
3. **连接：**
   - 内置端点：使用现有的SDK方法（`sdk.admin.product.list()`）
   - 自定义API路由：使用 `sdk.client.fetch("/admin/my-route")`
   - **绝对不要使用常规的fetch()** - 缺少身份验证标头将导致错误

**对于商店：**
1. **后端（此技能）：** 模块 → 工作流 → API路由
2. **前端：** 加载 `building-storefronts` 技能
3. **连接：**
   - 内置端点：使用现有的SDK方法（`sdk.store.product.list()`）
   - 自定义API路由：使用 `sdk.client.fetch("/store/my-route")`
   - **绝对不要使用常规的fetch()** - 缺少发布API密钥将导致错误

**为什么需要 SDK：**
- 存储路由需要 `x-publishable-api-key` 头部
- 管理路由需要 `Authorization` 和会话头部
- SDK 自动处理所有必需的头部
- 无头部进行常规的 fetch() → 认证/授权错误

请参考相应的前端技能以了解完整的集成模式。
