当用户提供一个 CLAUDE.md 文件（或要求您改进一个文件）时，请按照以下原则和结构进行重写。

## 核心问题

Claude Code 在每个 CLAUDE.md 文件中注入一个系统提醒，内容如下：

> "这个上下文可能与您的任务相关，也可能不相关。除非它与您的任务高度相关，否则您不应响应这个上下文。"

这意味着 Claude 会忽略它认为不相关的 CLAUDE.md 部分。如果当前任务不适用于的内容过多，Claude 可能会忽略所有内容，包括重要的部分。

## 解决方案：`<important if="condition">` 块

将条件相关的 CLAUDE.md 部分用 `<important if="condition">` XML 标签包裹。这利用了 Claude Code 自身系统提示中使用的相同 XML 标签模式，向模型提供了一个明确的关联信号，从而绕过“可能相关也可能不相关”的框架。

## 原则

### 1. 基础上下文保持简洁，领域指导被包裹

并非所有内容都应该放在 `<important if>` 块中。与几乎所有任务都相关的上下文——项目标识、项目地图、技术栈——应保留为文件顶部的纯 Markdown。这是代理始终需要的入门上下文。

特定领域的指导，仅对某些任务相关——测试模式、API 惯例、状态管理、i18n——应被包裹在 `<important if>` 块中，并带有针对性的条件。

经验法则：如果它与 90%+ 的任务相关，就保留为纯 Markdown。如果它仅与特定类型的工作相关，就将其包裹。

### 2. 条件必须具体且针对性

不好——过于宽泛的条件，匹配所有内容：
```
<important if="you are writing or modifying any code">
- 使用绝对导入
- 使用函数式组件
- 使用 camelCase 文件名
</important>
```

好——每条规则都有其自己的狭窄触发器：
```
<important if="you are adding or modifying imports">
- 使用 `@/` 绝对导入（参见 tsconfig.json 中的路径别名）
- 避免在路由文件之外使用默认导出
</important>

<important if="you are creating new components">
- 使用具有明确 prop 接口的函数式组件
</important>

<important if="you are creating new files or directories">
- 使用 camelCase 文件和目录名
</important>
```

### 3. 保持简洁，谨慎使用渐进式披露

不要拆分成需要代理进行工具调用才能发现的多个文件，除非额外的上下文非常冗长或复杂。

`<important if>` 块的整个目的就是所有内容都是内联的，但条件性加权——代理可以看到所有内容，但仅关注匹配的内容。

最好保持文件简洁。

### 4. 少即是多

- 前沿模型可以可靠地遵循几百条。Claude Code 的系统提示和工具已经使用了约 50 条。您的 CLAUDE.md 应尽可能精简。
- 删除任何可以被代码检查器、格式化器或预提交钩子强制执行的指令
- 删除代理可以从现有代码模式中发现的任何指令。大型语言模型是上下文学习者——如果您的代码库始终使用某种模式，代理在几次搜索后会遵循它。
- 删除代码片段。它们会过时并使文件膨胀。使用文件路径引用代替（例如，“参见 `src/utils/example.ts` 以获取该模式”）。

### 5. 保留所有命令

不要从原始文件中删除命令。命令表是基础参考——代理需要知道有哪些命令可用，即使有些命令使用频率较低。

## 输出结构

重写 CLAUDE.md 时，生成此结构：

```
# CLAUDE.md

[一行项目标识——它是什么，用什么构建的]

## 项目地图
[带有简短描述的目录列表]

<important if="you need to run commands to build, test, lint, or generate code">
[命令表——原始文件中的所有命令]
</important>

<important if="<特定触发器用于规则 1>">
[规则 1]
</important>

<important if="<特定触发器用于规则 2>">
[规则 2]
</important>

... 更多规则，每个规则有自己的块 ...

<important if="<特定触发器用于领域区域 1>">

[指导]

</important>

... 更多领域部分 ...
```

## 如何应用

当被要求改进现有的 CLAUDE.md 时：

1. **识别项目标识**——提取一个描述这是什么的单句。将其保留在文件顶部为纯 Markdown。
2. **提取目录地图**——保留为纯 Markdown（无 `<important if>` 包装）。这是基础上下文。
3. **提取技术栈**——如果存在，保留在顶部附近为纯 Markdown。精简为一两行。
4. **提取命令**——保留原始文件中的所有命令。用一个 `<important if>` 块包裹。
5. **拆分规则**——将任何规则列表拆分为具有特定条件的单独 `<important if>` 块。您可以分组规则，但永远不要在广义条件下分组不相关的规则。
6. **包裹领域部分**——测试、API 模式、状态管理、i18n 等，每个部分都有自己的块，描述何时需要该知识。
7. **删除代码检查器领域**——删除样式指南、格式化规则和任何可由工具强制执行的内容。建议用预推送或预提交钩子替代。
8. **删除代码片段**——用文件路径引用替代。
9. **删除模糊指令**——删除任何像“利用 X 代理”或“遵循最佳实践”这样不是具体且可操作的指令。

## 示例

输入：
```markdown
# CLAUDE.md

这是一个 Turborepo 单一代码库中的 Express API 和 React 前端。

## 命令

| 命令 | 描述 |
|---|---|
| `turbo build` | 构建所有包 |
| `turbo test` | 运行所有测试 |
| `turbo lint` | 检查所有包 |
| `turbo dev` | 启动开发服务器 |
| `turbo storybook` | 启动 Storybook |
| `turbo db:generate` | 生成 Prisma 客户端 |
| `turbo db:migrate` | 运行数据库迁移 |
| `turbo analyze` | 打包分析器 |

## 项目结构

- `apps/api/` - Express REST API
- `apps/web/` - React SPA
- `packages/db/` - Prisma 模式和客户端
- `packages/ui/` - 共享组件库
- `packages/config/` - 共享配置

## 编码标准

- 使用命名导出
- 使用具有 TypeScript 接口的函数式组件
- 使用 camelCase 变量，PascalCase 组件
- 优先使用 `const` 而不是 `let`
- 始终使用严格相等 (`===`)
- 使用模板文字而不是字符串连接
- 为所有公共函数编写 JSDoc 注释
- 在 index.ts 文件中使用模块导出

## API 开发

- 所有路由都在 `apps/api/src/routes/` 中
- 使用 Zod 进行请求验证
- 使用 Prisma 进行数据库访问
- 错误响应遵循 RFC 7807 格式
- 通过 JWT 中间件进行身份验证

## 测试

- Jest + Supertest 用于 API 测试
- Vitest + Testing Library 用于前端
- 测试 fixtures 在 `__fixtures__/` 目录中
- 使用 `createTestClient()` 辅助函数进行 API 集成测试
- 使用 `prismaMock` 从 `packages/db/test` 模拟数据库

## 状态管理

- Zustand 用于全局客户端状态
- React Query 用于服务器状态
- URL 状态通过 `nuqs`
```

输出：
```markdown
# CLAUDE.md

Express API + React 前端在 Turborepo 单一代码库中。

## 项目地图

- `apps/api/` - Express REST API
- `apps/web/` - React SPA
- `packages/db/` - Prisma 模式和客户端
- `packages/ui/` - 共享组件库
- `packages/config/` - 共享配置

<important if="you need to run commands to build, test, lint, or generate code">

从仓库根目录使用 `turbo` 运行。

| 命令 | 它做什么 |
|---|---|
| `turbo build` | 构建所有包 |
| `turbo test` | 运行所有测试 |
| `turbo lint` | 检查所有包 |
| `turbo dev` | 启动开发服务器 |
| `turbo storybook` | 启动 Storybook |
| `turbo db:generate` | 在模式更改后重新生成 Prisma 客户端 |
| `turbo db:migrate` | 运行数据库迁移 |
| `turbo analyze` | 打包分析器 |
</important>

<important if="you are adding or modifying imports or exports">
- 使用命名导出（不使用默认导出）
</important>

<important if="you are creating new components">
- 使用具有 TypeScript 接口的函数式组件
</important>

<important if="you are adding or modifying API routes">

- 所有路由都在 `apps/api/src/routes/` 中
- 使用 Zod 进行请求验证
- 使用 Prisma 进行数据库访问
- 错误响应遵循 RFC 7807 格式
- 通过 JWT 中间件进行身份验证
</important>

<important if="you are writing or modifying tests">

- API: Jest + Supertest
- 前端: Vitest + Testing Library
- 测试 fixtures 在 `__fixtures__/` 目录中
- 使用 `createTestClient()` 辅助函数进行 API 集成测试
- 使用 `prismaMock` 从 `packages/db/test` 模拟数据库
</important>

<important if="you are working with state management, stores, or URL parameters">

- Zustand 用于全局客户端状态
- React Query 用于服务器状态
- URL 状态通过 `nuqs`
</important>
```

被删除的内容及其原因：
- camelCase/PascalCase、const vs let、严格相等、模板文字、JSDoc、模块导出——代码检查器和格式化器领域，或可从现有代码模式中发现
- 编码标准作为一个分组部分——按触发器条件拆分为目标块

未被删除的内容：
- 保留所有命令（包括 dev、storybook、analyze）
- 项目地图保留为纯 Markdown（基础上下文，与每个任务都相关）
