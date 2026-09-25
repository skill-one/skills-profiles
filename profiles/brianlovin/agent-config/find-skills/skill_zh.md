# 查找技能

此技能可帮助您发现并安装来自开放代理技能生态系统的技能。

## 何时使用此技能

当用户：

- 询问“如何做X”，其中X可能是一个具有现有技能的常见任务
- 说“找一个用于X的技能”或“有没有用于X的技能”
- 询问“你能做X”，其中X是一个专业能力
- 表达对扩展代理能力的兴趣
- 想要搜索工具、模板或工作流
- 提到他们希望获得特定领域（设计、测试、部署等）的帮助时

## 什么是技能CLI？

技能CLI (`npx skills`) 是开放代理技能生态系统的包管理器。技能是模块化包，通过专业知识、工作流和工具扩展代理能力。

**主要命令：**

- `npx skills find [查询]` - 交互式搜索或通过关键字搜索技能
- `npx skills add <包>` - 从GitHub或其他来源安装技能
- `npx skills check` - 检查技能更新
- `npx skills update` - 更新所有已安装的技能

**浏览技能于：** https://skills.sh/

## 如何帮助用户查找技能

### 第一步：了解他们的需求

当用户请求帮助时，识别：

1. 领域（例如，React、测试、设计、部署）
2. 具体任务（例如，编写测试、创建动画、审查PR）
3. 这是否是一个足够常见的任务，以至于可能存在技能

### 第二步：搜索技能

使用相关查询运行查找命令：

```bash
npx skills find [查询]
```

例如：

- 用户询问“如何让我的React应用更快？” → `npx skills find react performance`
- 用户询问“你能帮我审查PR吗？” → `npx skills find pr review`
- 用户询问“我需要创建一个变更日志” → `npx skills find changelog`

该命令将返回类似以下结果：

```
使用 npx skills add <owner/repo@skill> 安装

vercel-labs/agent-skills@vercel-react-best-practices
└ https://skills.sh/vercel-labs/agent-skills/vercel-react-best-practices
```

### 第三步：向用户展示选项

当您找到相关技能时，向用户展示：

1. 技能名称及其功能
2. 他们可以运行的安装命令
3. 在skills.sh上了解更多信息的链接

示例回复：

```
我找到一个可能帮助的技能！"vercel-react-best-practices" 技能提供了来自Vercel工程的React和Next.js性能优化指南。

要安装它：
npx skills add vercel-labs/agent-skills@vercel-react-best-practices

了解更多：https://skills.sh/vercel-labs/agent-skills/vercel-react-best-practices
```

### 第四步：提供安装服务

如果用户想继续，您可以为他们安装技能：

```bash
npx skills add <owner/repo@skill> -g -y
```

`-g` 标志表示全局安装（用户级），`-y` 跳过确认提示。

## 常见技能类别

搜索时，考虑以下常见类别：

| 类别        | 示例查询                          |
| --------------- | ---------------------------------------- |
| 网页开发     | react, nextjs, typescript, css, tailwind |
| 测试         | testing, jest, playwright, e2e           |
| DevOps          | deploy, docker, kubernetes, ci-cd        |
| 文档         | docs, readme, changelog, api-docs        |
| 代码质量    | review, lint, refactor, best-practices   |
| 设计          | ui, ux, design-system, accessibility     |
| 生产力    | workflow, automation, git                |

## 高效搜索技巧

1. **使用具体关键字**："react testing" 比 "testing" 更好
2. **尝试替代术语**：如果 "deploy" 不起作用，尝试 "deployment" 或 "ci-cd"
3. **检查热门来源**：许多技能来自 `vercel-labs/agent-skills` 或 `ComposioHQ/awesome-claude-skills`

## 未找到技能时

如果未找到相关技能：

1. 承认未找到现有技能
2. 提供使用您的通用能力直接帮助执行任务的选项
3. 建议用户可以使用 `npx skills init` 创建自己的技能

示例：

```
我搜索了与 "xyz" 相关的技能，但没有找到匹配项。
我仍然可以直接帮助您完成此任务！您希望我继续吗？

如果这是一个您经常做的任务，您可以创建自己的技能：
npx skills init my-xyz-skill
```
