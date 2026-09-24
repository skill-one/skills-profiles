# 查找技能

本技能帮助您从开放 Agent 技能生态系统中发现并安装技能。

## 何时使用本技能

当用户出现以下情况时，使用本技能：

- 询问“如何执行 X”，而 X 可能是已存在技能可完成的一些常见任务
- 表示“为 X 寻找技能”或“是否存在 X 的技能”
- 询问“你能执行 X 吗”，而 X 是特殊能力
- 对扩展 Agent 能力表现出兴趣
- 想要搜索工具、模板或工作流
- 提到他们需要特定领域（设计、测试、部署等）方面的帮助

## Skills CLI 是什么？

Skills CLI (`npx skills`) 是开放 Agent 技能生态系统的包管理器。技能是可模块化包，通过专门的知识、工作流和工具来扩展 Agent 的能力。

**主要命令：**

- `npx skills find [query] [--owner <owner>]` - 可交互或通过关键字搜索技能，可选限定在 GitHub 某个用户所有范围内
- `npx skills add <package>` - 从 GitHub 或其他来源安装技能
- `npx skills update` - 更新所有已安装的技能

**在以下网址浏览技能：** https://skills.sh/

## 如何帮助用户查找技能

### 第一步：理解需求

当用户寻求帮助时，请明确：

1. 领域（如 React、测试、设计、部署）
2. 具体任务（如编写测试、创建动画、审查 PR）
3. 该任务是否足够常见，以至于很可能存在对应的技能

### 第二步：首先查看排行榜

在执行 CLI 搜索之前，请查看 [skills.sh 排行榜](https://skills.sh/)，确认该领域是否已有知名的技能。排行榜按总安装量对技能进行排序，突出显示最受欢迎且经过验证的选项。

例如，网页开发领域的热门技能包括：
- `vercel-labs/agent-skills` — React、Next.js、网页设计（各 100K+ 次安装）
- `anthropics/skills` — 前端设计、文档处理（100K+ 次安装）

### 第三步：搜索技能

如果排行榜未涵盖用户的需求，请运行 find 命令：

```bash
npx skills find [query] [--owner <owner>]
```

例如：

- 用户询问“如何让我的 React 应用更快？” → `npx skills find react performance`
- 用户询问“你能帮我进行 PR 审查吗？” → `npx skills find pr review`
- 用户询问“我需要创建变更日志” → `npx skills find changelog`

### 第四步：推荐前验证质量

**不要仅根据搜索结果推荐技能。请务必验证：**

1. **安装数量** — 优先选择安装量达到 1K+ 的技能。对安装量低于 100 的技能保持谨慎。
2. **来源信誉** — 官方来源（`vercel-labs`、`anthropics`、`microsoft`）比未知作者更可靠。
3. **GitHub 星标数** — 检查来源仓库。来自星标数低于 100 的仓库的技能应持谨慎态度。

### 第五步：向用户呈现选项

当你找到相关技能时，请向用户呈现以下信息：

1. 技能名称及其功能
2. 安装数量及来源
3. 他们可以运行的安装命令
4. 指向 skills.sh 了解详情的链接

示例回复：

```
我发现了一个可能有所帮助的技能！"react-best-practices" 技能提供
React 和 Next.js 性能优化指南，源自 Vercel 工程团队。
（185K 次安装）

安装命令如下：
npx skills add vercel-labs/agent-skills@react-best-practices

了解更多信息： https://skills.sh/vercel-labs/agent-skills/react-best-practices
```

### 第六步：提供安装选项

如果用户希望继续，您可以为其安装该技能：

```bash
npx skills add <owner/repo@skill} -g -y
```

`-g` 标志用于全局安装（用户级），`-y` 标志用于跳过确认提示。

## 常见的技能类别

搜索时，请考虑以下常见类别：

表格

类别 | 示例查询
--- | ---
Web 开发 | react、nextjs、typescript、css、tailwind
测试 | testing、jest、playwright、e2e
DevOps | deploy、docker、kubernetes、ci-cd
文档 | docs、readme、changelog、api-docs
代码质量 | review、lint、refactor、best-practices
设计 | ui、ux、design-system、accessibility
生产力 | workflow、自动化、git

## 高效搜索的技巧

1. **使用具体关键词**："react testing" 比单纯的 "testing" 效果更好
2. **尝试替代术语**：如果 "deploy" 不奏效，可尝试 "deployment" 或 "ci-cd"
3. **检查热门来源**：许多技能来自 `vercel-labs/agent-skills` 或 `ComposioHQ/awesome-claude-skills`

## 当未找到技能时

如果不存在相关技能：

1. 指出未找到现有的技能
2. 提供利用您的通用能力直接协助完成该任务
3. 建议用户可以使用 `npx skills init` 创建自己的技能

示例：

```
我搜索了与 "xyz" 相关的技能，但未找到任何匹配结果。
我仍然可以直接帮助您完成此任务！您愿意让我继续进行吗？

如果这是您经常做的事情，您可以创建自己的技能：
npx skills init my-xyz-skill
```
