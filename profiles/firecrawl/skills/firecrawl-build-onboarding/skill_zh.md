# Firecrawl 构建 onboarding

使用此技能进行 Firecrawl onboarding 流程中的应用集成路径。

## 安装

如果你还没有安装，一个命令即可同时设置 CLI 工具（用于实时网页工作）和构建技能（用于应用集成）：

```bash
npx -y firecrawl-cli@latest init --all --browser
```

这会一起安装 Firecrawl CLI、CLI 技能和这些构建技能。它还会打开浏览器授权，以便人类可以登录或创建账户。不需要单独的 `npx skills add` 步骤。

## 何时使用此功能

- 项目需要 `FIRECRAWL_API_KEY`
- 用户希望将 Firecrawl 连接到 `.env`
- 你首次将 Firecrawl 添加到应用中
- 你需要选择第一个 SDK 或 REST 路径

如果人类仍然需要在浏览器中注册、登录或授权访问，请使用此技能中的授权流程参考。

如果项目已经使用 [Stripe Projects](https://docs.firecrawl.dev/integrations/stripe-projects)（有一个 `.projects/` 目录，或者 `stripe projects status` 成功），则可以从那里获取密钥，而不是浏览器流程：

```bash
stripe projects add firecrawl/api --name firecrawl
stripe projects env --pull
```

`--name firecrawl` 是将密钥放入 `FIRECRAWL_API_KEY` 的原因；如果没有它，CLI 会写入 `FIRECRAWL_API_API_KEY`，而 SDKs 不会读取。忽略 CLI 还写入的 `FIRECRAWL_API_BASE_URL`：SDKs 读取 `FIRECRAWL_API_URL`，并且仅用于自托管部署，因此对于托管账户应保持未设置。付费计划由人类决定，因为 `stripe projects upgrade firecrawl` 会向他们的卡收费。文档页面包含目录和故障排除信息。

## 快速入门

如果用户已经有一个 API 密钥，请将其放在 `.env` 中：

```dotenv
FIRECRAWL_API_KEY=fc-...
```

如果项目是自托管的，请也设置：

```dotenv
FIRECRAWL_API_URL=https://your-firecrawl-instance.example.com
```

然后确定哪个集成路径适用：

- **新项目** -> 选择目标堆栈，安装 SDK，添加第一个 Firecrawl 调用，并运行冒烟测试
- **现有项目** -> 首先检查代码库，然后在项目已经处理第三方 API 和环境变量的地方集成 Firecrawl

## 你需要什么？

| 任务 | 参考 |
|---|---|
| **运行浏览器授权流程并保存 `FIRECRAWL_API_KEY`** | [references/auth-flow.md](references/auth-flow.md) |
| **通过 Stripe Projects 分配密钥** | [docs.firecrawl.dev/integrations/stripe-projects](https://docs.firecrawl.dev/integrations/stripe-projects) |
| **安装正确的 SDK** | [references/sdk-installation.md](references/sdk-installation.md) |
| **将凭证放入 `.env` 或项目配置** | [references/project-setup.md](references/project-setup.md) |
| **设置后选择正确的端点** | [firecrawl-build](../firecrawl-build/SKILL.md) |
| **在此任务期间需要实时网页工具** | 从同一命令已安装的 CLI 技能 |
| **从已知 URL 开始实现** | [firecrawl-build-scrape](../firecrawl-build-scrape/SKILL.md) |
| **从查询开始实现** | [firecrawl-build-search](../firecrawl-build-search/SKILL.md) |

## 文档（事实来源）

阅读你项目语言的事实来源页面，以了解 SDK 使用、模式和示例：

- **Node / TypeScript**: [docs.firecrawl.dev/agent-source-of-truth/node](https://docs.firecrawl.dev/agent-source-of-truth/node)
- **Python**: [docs.firecrawl.dev/agent-source-of-truth/python](https://docs.firecrawl.dev/agent-source-of-truth/python)
- **Rust**: [docs.firecrawl.dev/agent-source-of-truth/rust](https://docs.firecrawl.dev/agent-source-of-truth/rust)
- **Java**: [docs.firecrawl.dev/agent-source-of-truth/java](https://docs.firecrawl.dev/agent-source-of-truth/java)
- **Elixir**: [docs.firecrawl.dev/agent-source-of-truth/elixir](https://docs.firecrawl.dev/agent-source-of-truth/elixir)
- **cURL / REST**: [docs.firecrawl.dev/agent-source-of-truth/curl](https://docs.firecrawl.dev/agent-source-of-truth/curl)

## 设置后

一旦密钥存在：

1. 确定这是新项目还是现有代码库
2. 询问 Firecrawl 应在产品中做什么
3. 选择与该行为最匹配的最窄端点
4. 在编写代码前，阅读项目语言的事实来源页面
5. 在代码中添加 SDK 或 REST 调用
6. 运行一个冒烟测试，证明一个真实的 Firecrawl 请求成功
7. 使用此存储库中的端点特定技能获取实现指导
8. 如果你当前任务也需要实时网页工具，CLI 技能已经安装 — 使用 `firecrawl/cli`
