---
name: documentation-and-adrs
description: 记录决策和文档。当您需要记录架构决策（ADR）或设计选择的理由、更改公共 API、发布功能，或需要记录未来工程师和代理需要理解代码库的背景信息时使用。
---

# 文档与架构决策记录（ADR）

## 概述

记录决策，而不仅仅是代码。最有价值的文档是捕捉到*为什么*——导致决策的背景、约束和权衡。代码展示*构建了什么*；文档解释*为什么这样构建*以及*考虑了哪些替代方案*。这种背景对于未来在代码库中工作的人类和代理至关重要。

## 何时使用

- 做出重要的架构决策
- 在竞争性方法之间进行选择
- 添加或更改公共 API
- 发布改变用户行为的特性
- 新团队成员（或代理）入职项目
- 当你发现自己反复解释同样的事情时

**不使用时：** 不要记录显而易见的代码。不要添加重述代码内容的注释。不要为一次性原型编写文档。

## 架构决策记录（ADR）

ADR 捕捉重要技术决策背后的推理。它们是你能编写的最高价值文档。

### 何时编写 ADR

- 选择框架、库或主要依赖项
- 设计数据模型或数据库模式
- 选择认证策略
- 确定 API 架构（REST vs. GraphQL vs. tRPC）
- 在构建工具、托管平台或基础设施之间进行选择
- 任何可能难以撤销的决策

### 首先匹配现有约定

在创建 ADR 之前，检查可用存储库上下文中的既定约定——现有的 ADR、项目说明以及与 ADR 相关的配置或工具（例如 `.adr-dir` 文件）。既定约定会覆盖以下默认值。匹配：

- **位置和格式** — 例如 `docs/adr/*.md`、`Documentation/Decisions/*.rst`、MADR 布局或 `adr-tools` 设置。匹配现有目录、文件扩展名和标记（Markdown vs reStructuredText）。
- **编号和命名** — 继续现有的序列和文件名模式（`ADR-004-Title.rst`、`0004-title.md`、…）；不要从 001 重新开始或引入第二种方案。
- **章节标题** — 重用项目的标题集，而不是强加此模板的。

如果可用证据存在冲突，应暴露冲突，而不是在沉默中引入另一种方案。只有在无法建立约定时，才应用以下默认值。

### ADR 模板

将 ADR 存储在 `docs/decisions/` 中，使用顺序编号（如果项目已经使用其他位置——见上文）：

```markdown
# ADR-001: 使用 PostgreSQL 作为主数据库

## 状态
已接受 | 被 ADR-XXX 覆盖 | 已弃用

## 日期
2025-01-15

## 背景
我们需要为任务管理应用程序的主数据库。关键要求：
- 关系数据模型（用户、任务、团队之间的关系）
- 任务状态变更的 ACID 事务
- 支持对任务内容进行全文搜索
- 提供托管托管（对于小型团队，有限的运维能力）

## 决策
使用 PostgreSQL 与 Prisma ORM。

## 考虑过的替代方案

### MongoDB
- 优点：灵活的架构，易于开始
- 缺点：我们的数据本质上是关系的；需要手动管理关系
- 已拒绝：在文档存储中存储关系数据会导致复杂的连接或数据重复

### SQLite
- 优点：无需配置，嵌入式，读取速度快
- 缺点：并发写入支持有限，生产环境中没有托管托管
- 已拒绝：不适合生产环境中的多用户 Web 应用程序

### MySQL
- 优点：成熟，广泛支持
- 缺点：PostgreSQL 对 JSON 支持更好，全文搜索和生态系统工具
- 已拒绝：PostgreSQL 更适合我们的功能要求

## 后果
- Prisma 提供类型安全的数据库访问和迁移管理
- 我们可以使用 PostgreSQL 的全文搜索，而不是添加 Elasticsearch
- 团队需要 PostgreSQL 知识（标准技能，低风险）
- 在托管服务上托管（Supabase、Neon 或 RDS）
```

### ADR 生命周期

```
PROPOSED → ACCEPTED → (SUPERSEDED or DEPRECATED)
```

- **不要删除旧的 ADR。** 它们捕获了历史背景。
- 当决策发生变化时，编写一个新的 ADR，该 ADR 引用并覆盖旧的 ADR。

## 内联文档

### 何时注释

注释*为什么*，而不是*什么*：

```typescript
// BAD: 重述代码
// Increment counter by 1
counter += 1;

// GOOD: 解释非显而易见的意图
// 率限使用滑动窗口——在窗口边界重置计数器，
// 而不是在固定时间表上重置，以防止在窗口边缘发生突发攻击
if (now - windowStart > WINDOW_SIZE_MS) {
  counter = 0;
  windowStart = now;
}
```

### 何时不注释

```typescript
// 不要注释自解释的代码
function calculateTotal(items: CartItem[]): number {
  return items.reduce((sum, item) => sum + item.price * item.quantity, 0);
}

// 不要为现在就应该做的事情留下 TODO 注释
// TODO: 添加错误处理  ← 现在就添加它

// 不要保留已注释的代码
// const oldImplementation = () => { ... }  ← 删除它，git 有历史记录
```

### 记录已知陷阱

```typescript
/**
 * 重要提示：必须在第一次渲染之前调用此函数。
 * 如果在 hydration 后调用，会导致无样式内容的闪烁，
 * 因为在 SSR 期间主题上下文不可用。
 *
 * 参考 ADR-003 了解完整的设计理由。
 */
export function initializeTheme(theme: Theme): void {
  // ...
}
```

## API 文档

对于公共 API（REST、GraphQL、库接口）：

### 与类型内联（TypeScript 首选）

```typescript
/**
 * 创建新任务。
 *
 * @param input - 任务创建数据（标题必需，描述可选）
 * @returns 创建的任务，包含服务器生成的 ID 和时间戳
 * @throws {ValidationError} 如果标题为空或超过 200 个字符
 * @throws {AuthenticationError} 如果用户未通过身份验证
 *
 * @example
 * const task = await createTask({ title: '购买杂货' });
 * console.log(task.id); // "task_abc123"
 */
export async function createTask(input: CreateTaskInput): Promise<Task> {
  // ...
}
```

### OpenAPI / Swagger 用于 REST API

```yaml
paths:
  /api/tasks:
    post:
      summary: 创建任务
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateTaskInput'
      responses:
        '201':
          description: 任务已创建
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Task'
        '422':
          description: 验证错误
```

## README 结构

每个项目都应该有一个 README，涵盖：

```markdown
# 项目名称

对这个项目做什么的简短描述。

## 快速入门
1. 克隆存储库
2. 安装依赖项：`npm install`
3. 设置环境：`cp .env.example .env`
4. 运行开发服务器：`npm run dev`

## 命令
| 命令 | 描述 |
|------|------|
| `npm run dev` | 启动开发服务器 |
| `npm test` | 运行测试 |
| `npm run build` | 生产构建 |
| `npm run lint` | 运行 linter |

## 架构
项目结构和关键设计决策的简要概述。
链接到 ADR 以获取详细信息。

## 贡献
如何贡献，编码标准，PR 流程。
```

## 更新日志维护

对于已发布的特性：

```markdown
# 更新日志

## [1.2.0] - 2025-01-20
### 添加
- 任务共享：用户可以与团队成员共享任务 (#123)
- 任务分配的电子邮件通知 (#124)

### 修复
- 快速点击创建按钮时出现重复任务 (#125)

### 更改
- 任务列表现在每页加载 50 个项目（原来是 20 个）以改善 UX (#126)
```

## 代理文档

对于 AI 代理上下文的特殊考虑：

- **CLAUDE.md / 规则文件** — 记录项目约定，以便代理遵循它们
- **规范文件** — 保持规范更新，以便代理构建正确的东西
- **ADR** — 帮助代理了解过去决策的原因（防止重新决策）
- **内联陷阱** — 防止代理落入已知陷阱

## 常见理由

| 理由 | 现实 |
|------|------|
| "代码自解释" | 代码展示*什么*。它不展示*为什么*，考虑了哪些替代方案，或适用哪些约束。 |
| "API 稳定后我们会写文档" | 当你记录 API 时，API 会更快地稳定。文档是设计的第一项测试。 |
| "没人读文档" | 代理会读。未来的工程师会读。你几个月后的自己会读。 |
| "ADR 是开销" | 10 分钟的 ADR 可以防止六个月后关于相同决策的 2 小时争论。 |
| "注释会过时" | *为什么*的注释是稳定的。*什么*的注释会过时——这就是为什么你只写前者。 |

## 警示标志

- 没有书面推理的架构决策
- 没有文档或类型的公共 API
- README 没有解释如何运行项目
- 而不是删除，保留已注释的代码
- 几周前就存在的 TODO 注释
- 在具有重要架构决策的项目中没有 ADR
- 文档重述代码而不是解释意图

## 验证

记录后：

- [ ] 所有重要的架构决策都有 ADR
- [ ] README 涵盖快速入门、命令和架构概述
- [ ] API 函数有参数和返回类型文档
- [ ] 在重要位置内联记录了已知陷阱
- [ ] 没有保留已注释的代码
- [ ] 规则文件（CLAUDE.md 等）是最新的且准确的
