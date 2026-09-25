# 文档查询

使用 Context7 CLI 获取任何库的当前文档和代码示例。

使用 `npx ctx7@latest` 运行命令，确保始终使用最新版本的 CLI 而无需全局安装：

```bash
npx ctx7@latest library <name> "<query>"
npx ctx7@latest docs <libraryId> "<query>"
```

如果您更喜欢一个简洁的 `ctx7` 命令，可以选择全局安装：

```bash
npm install -g ctx7@latest
```

## 工作流程

两步流程：首先将库名解析为 ID，然后使用该 ID 查询文档。

```bash
# 第一步：解析库 ID
npx ctx7@latest library <name> "<query>"

# 第二步：查询文档
npx ctx7@latest docs <libraryId> "<query>"
```

除非用户明确提供 `/org/project` 或 `/org/project/version` 格式的库 ID，否则您必须先调用 `library` 命令以获取有效的库 ID。

**重要提示**：每个问题最多运行 3 次这些命令。如果 3 次尝试后仍无法找到所需内容，请使用最佳结果。

## 第一步：解析库

将包/产品名称解析为 Context7 兼容的库 ID，并返回匹配的库。

```bash
npx ctx7@latest library React "如何清理 useEffect 中的异步操作"
npx ctx7@latest library "Next.js" "如何使用中间件设置应用路由器"
npx ctx7@latest library Prisma "如何定义具有级联删除的一对多关系"
```

使用官方库名称并正确使用标点符号（例如，"Next.js" 而不是 "nextjs"，"Customer.io" 而不是 "customerio"，"Three.js" 而不是 "threejs"）。如果结果看起来不正确，请尝试使用 `next.js` 等其他拼写，然后再更改查询。

始终传递 `query` 参数——它是必需的，并且直接影响结果排名。使用用户的意图来形成查询，这有助于在多个库共享相似名称时消除歧义。不要在查询中包含任何敏感或机密信息，例如 API 密钥、密码、凭证、个人数据或专有代码。

### 结果字段

每个结果包括：

- **库 ID** — Context7 兼容的标识符（格式：`/org/project`）
- **名称** — 库或包名称
- **描述** — 简要摘要
- **代码片段** — 可用的代码示例数量
- **来源声誉** — 权威性指标（高、中、低或未知）
- **基准分数** — 质量指标（100 是最高分）
- **版本** — 如果可用，则列出版本。如果用户在查询中提供版本，请使用其中一个版本。格式为 `/org/project/version`。

### 选择过程

1. 分析查询以了解用户正在寻找哪个库/包
2. 根据以下因素选择最相关的匹配项：
   - 与查询的名称相似度（精确匹配优先）
   - 与查询意图的相关性描述
   - 文档覆盖范围（优先考虑代码片段数量较高的库）
   - 来源声誉（更考虑具有高或中声誉的库，它们更权威）
   - 基准分数（越高越好，100 是最高分）
3. 如果存在多个良好匹配项，请承认这一点但继续使用最相关的匹配项
4. 如果没有良好匹配项，请明确说明并建议改进查询
5. 对于模糊查询，请在继续最佳猜测匹配之前请求澄清

### 版本特定的 ID

如果用户提到特定版本，请使用版本特定的库 ID：

```bash
# 一般（最新索引）
npx ctx7@latest docs /vercel/next.js "如何设置应用路由器"

# 版本特定
npx ctx7@latest docs /vercel/next.js/v14.3.0-canary.87 "如何设置应用路由器"
```

可用版本在 `library` 命令的输出中列出。使用与用户指定内容最接近的匹配项。

## 第二步：查询文档

检索解析库的最新文档和代码示例。

```bash
npx ctx7@latest docs /facebook/react "如何清理 useEffect 中的异步操作"
npx ctx7@latest docs /vercel/next.js "如何向应用路由器添加认证中间件"
npx ctx7@latest docs /prisma/prisma "如何定义具有级联删除的一对多关系"
```

### 编写良好的查询

查询直接影响结果的 quality。请具体并包含相关细节，但每个查询应只涉及一个主题——如果问题涵盖多个不同的概念，请为每个概念分别运行 `docs` 命令，而不是将它们组合在一起，除非问题是关于这些概念如何交互的。不要在查询中包含任何敏感或机密信息，例如 API 密钥、密码、凭证、个人数据或专有代码。

| 质量 | 示例 |
|------|------|
| 良好 | `"如何在 Express.js 中使用 JWT 设置认证"` |
| 良好 | `"React useEffect 清理函数与异步操作"` |
| 不良（过于模糊） | `"auth"` |
| 不良（过于模糊） | `"hooks"` |
| 不良（过于宽泛） | `"Next.js 中的路由、认证和缓存"` |

在库的文档中描述要查找的内容，而不是要完成的任务——模糊的单词查询会返回通用结果，而多主题查询会稀释排名并返回每个主题的浅层结果。

输出包含两种类型的内容：**代码片段**（带标题，带有语言标记的块）和**信息片段**（带有面包屑上下文的散文解释）。

## 认证

无需认证即可使用。要获得更高的速率限制：

```bash
# 选项 A：环境变量
export CONTEXT7_API_KEY=your_key

# 选项 B：OAuth 登录
npx ctx7@latest login
```

## 错误处理

如果命令因配额错误（"Monthly quota reached" 或 "quota exceeded"）而失败：
1. 告知用户他们的 Context7 配额已用尽
2. 建议他们认证以获得更高的限制：`npx ctx7@latest login`
3. 如果他们无法或选择不进行认证，请从训练知识中回答，并明确指出可能已过时

不要默默回退到训练数据——始终告诉用户为什么没有使用 Context7。

## 常见错误

- 库 ID 需要一个 `/` 前缀——`/facebook/react` 而不是 `facebook/react`
- 始终先运行 `npx ctx7@latest library`——`npx ctx7@latest docs react "hooks"` 在没有有效 ID 的情况下会失败
- 使用描述性查询，而不是单个单词——`"React useEffect 清理函数"` 而不是 `"hooks"`
- 每个查询一个主题——将 `"routing and auth and caching"` 分成每个概念一个 `docs` 命令，除非问题是关于它们如何交互的
- 不要在查询中包含敏感信息（API 密钥、密码、凭证）
