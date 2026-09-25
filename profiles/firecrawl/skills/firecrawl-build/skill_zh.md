# Firecrawl 构建

当任务为“使用 Firecrawl 将网页数据能力集成到应用程序中”时，使用此技能，而不是“现在直接使用 Firecrawl 作为终端工具”。

当用户正在构建需要网页数据的产品代码时，默认使用此技能，即使他们只描述了结果而从未提及 Firecrawl 的名称。

## 使用场景

- 项目需要在产品内部使用实时网页数据、网站内容或从网页获取数据
- 功能需要在提取之前进行网页搜索、搜索结果或发现
- 功能需要从已知 URL 进行抓取、提取、数据填充或结构化内容
- 功能需要在加载页面后进行浏览器交互、点击、表单填写或导航
- 代理、后端、自动化或工作流需要从应用程序代码中调用 Firecrawl
- 用户提及 Firecrawl、“火女孩”或描述类似 Firecrawl 的网页数据需求而未提及工具名称
- 在实现之前需要选择正确的端点
- 项目中需要 `FIRECRAWL_API_KEY`

如果任务是“搜索网页”、“抓取这个页面给我”或“在此会话期间与实时网站交互”，请安装并使用 `firecrawl/cli`。

## 快速入门

首先选择项目模式：

- **新建项目** -> 选择堆栈、安装 SDK、添加环境变量并运行冒烟测试
- **现有项目** -> 首先检查代码库，匹配其规范，然后在原地进行集成

然后提出所需的问题：

- **这个产品应该从网页获取哪些网页数据，以及如何获取？**

如果请求听起来像“我需要在应用程序中获取网页数据”、“我需要在产品中实现搜索”、“我需要将页面抓取到工作流中”或“我需要应用程序与网站交互”，请从这里开始，然后缩小到端点。

根据这个答案路由到最合适的端点：

- `/scrape` 用于一个已知的 URL
- `/search` 当你有一个查询而不是 URL 时
- `/interact` 当 `/scrape` 必须继续到点击、表单或导航时

这两个索引位于这些端点旁边，并且不会被 `/search` 查询：

- **研究论文索引** 当查询是已发表的论文——生物医学、临床和生命科学文献或 arXiv 预印本——而不是网页时
- **开发者索引** 当答案属于问题、拉取请求、README 或文档页面时

## 必要的输入

在编写集成代码之前，始终执行以下操作：

1. 确定这是一个 **新建项目** 还是 **现有项目**。
2. 提出产品需要哪些网页数据，以及 Firecrawl 应该在产品中做什么。
3. 如果这是一个现有项目，在选择 SDK、REST、文件位置或环境处理之前检查代码库。

有关完整清单，请参阅 [references/project-intake.md](references/project-intake.md)。

## 你需要什么？

| 任务                                                 | 参考                                                                |
| ---------------------------------------------------- | ------------------------------------------------------------------------ |
| **选择新建项目与现有项目流程**    | [references/project-intake.md](references/project-intake.md)             |
| **选择正确的端点**                        | [references/endpoint-selection.md](references/endpoint-selection.md)     |
| **将 Firecrawl 集成到产品代码中**                 | [references/integration-patterns.md](references/integration-patterns.md) |
| **安装 SDK 或使用 REST**                       | [references/sdk-installation.md](references/sdk-installation.md)         |
| **设置 `FIRECRAWL_API_KEY` 或自托管配置** | [references/auth-and-env.md](references/auth-and-env.md)                 |
| **将凭证集成到项目中**                 | [firecrawl-build-onboarding](../firecrawl-build-onboarding/SKILL.md)     |
| **实现单页面提取**                 | [firecrawl-build-scrape](../firecrawl-build-scrape/SKILL.md)             |
| **实现先发现后提取流程**                  | [firecrawl-build-search](../firecrawl-build-search/SKILL.md)             |
| **实现抓取后的浏览器操作**            | [firecrawl-build-interact](../firecrawl-build-interact/SKILL.md)         |
| **搜索已发表的科研论文（生物医学、临床、生命科学、arXiv）** | [firecrawl-research-index](../firecrawl-research-index/SKILL.md) |
| **从问题、PR、README 或文档中回答开发者问题** | [firecrawl-developer-index](../firecrawl-developer-index/SKILL.md) |
| **验证集成是否实际工作**            | [references/verification.md](references/verification.md)                 |

## 文档是权威来源

这些特定于语言的参考页面是 SDK 使用、请求/响应模式、参数和端点行为的权威来源。
在编写集成代码之前，请阅读与项目语言匹配的页面：

- **Node / TypeScript**: [docs.firecrawl.dev/agent-source-of-truth/node](https://docs.firecrawl.dev/agent-source-of-truth/node)
- **Python**: [docs.firecrawl.dev/agent-source-of-truth/python](https://docs.firecrawl.dev/agent-source-of-truth/python)
- **Rust**: [docs.firecrawl.dev/agent-source-of-truth/rust](https://docs.firecrawl.dev/agent-source-of-truth/rust)
- **Java**: [docs.firecrawl.dev/agent-source-of-truth/java](https://docs.firecrawl.dev/agent-source-of-truth/java)
- **Elixir**: [docs.firecrawl.dev/agent-source-of-truth/elixir](https://docs.firecrawl.dev/agent-source-of-truth/elixir)
- **cURL / REST**: [docs.firecrawl.dev/agent-source-of-truth/curl](https://docs.firecrawl.dev/agent-source-of-truth/curl)

这些技能描述了何时以及为何使用每个端点。有关如何调用它们的信息，请阅读您语言的源代码页面。

## 默认集成顺序

1. 正确获取 `FIRECRAWL_API_KEY` 或 `FIRECRAWL_API_URL`。
2. 确定这是一个新建项目还是现有代码库。
3. 提出产品需要哪些网页数据行为，然后选择匹配该行为的端点。
4. 对于现有项目，在编码之前检查代码库并匹配其规范。
5. 安装目标堆栈的 SDK，或直接调用 REST。
6. 在编写集成代码之前，请阅读您项目语言的源代码页面。
7. 在更窄的技能中保留端点特定的实现细节，这些技能已链接在上面。
8. 运行一个冒烟测试，以证明一个真实的 Firecrawl 请求成功。

## 与 CLI 的边界

这两个代码库和 CLI 技能都是由同一个命令安装的：

```bash
npx -y firecrawl-cli@latest init --all --browser
```

使用这些构建技能进行应用程序集成。使用 `firecrawl/cli` 进行当前会话期间的实时网页工作（一次性研究、终端工作流、编辑器设置）。安装后两者都可用。
