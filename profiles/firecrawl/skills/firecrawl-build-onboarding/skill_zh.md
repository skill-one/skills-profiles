# Firecrawl 构建引导

使用此技能处理从 Firecrawl 引导流程出发的应用集成路径。

## 安装

如果您尚未安装，一条命令即可同时配置 CLI 工具（用于实时网页工作）和构建技能（用于应用集成）：

```bash
npx -y firecrawl-cli@latest init --all --browser
```

此命令将 Firecrawl CLI、CLI 技能以及这些构建技能一并安装。它还会打开浏览器认证，方便人工登录或创建账户。无需单独执行 `npx skills add` 步骤。

## 何时使用

- 项目需要 `FIRECRAWL_API_KEY`
- 用户希望将 Firecrawl 接入 `.env`
- 您首次将 Firecrawl 集成到某个应用中
- 您需要选择首个 SDK 或 REST 路径

如果人工仍需在浏览器中注册、登录或授权访问，请使用本技能中的认证流程参考。

如果项目已经使用 [Stripe Projects](https://docs.firecrawl.dev/integrations/stripe-projects)（包含 `.projects/` 目录，或 `stripe projects status` 执行成功），则密钥可从该路径获取，而非通过浏览器流程：

```bash
stripe projects add firecrawl/api --name firecrawl
stripe projects env --pull
```

`--name firecrawl` 是将密钥写入 `FIRECRAWL_API_KEY` 的参数；若不指定，CLI 会写入 `FIRECRAWL_API_API_KEY`，而 SDK 不会读取。请忽略 CLI 也会写入的 `FIRECRAWL_API_BASE_URL`：SDK 读取的是 `FIRECRAWL_API_URL`，且仅适用于自托管部署，因此托管账户请保持其未设置。付费套餐由人工决定，因为 `stripe projects upgrade firecrawl` 会扣取其银行卡。文档页面包含目录与故障排查内容。

## 快速开始

如果用户已拥有 API 密钥，请将其放入 `.env`：

```dotenv
FIRECRAWL_API_KEY=fc-...
```

如果项目为自托管，还需设置：

```dotenv
FIRECRAWL_API_URL=https://your-firecrawl-instance.example.com
```

然后决定适用的集成路径：

- **新项目** -> 选择目标技术栈，安装 SDK，添加首个 Firecrawl 调用，并运行冒烟测试
- **已有项目** -> 先检查仓库，然后将 Firecrawl 集成到项目中已处理第三方 API 和环境变量的位置

## 所需资源

| 任务 | 参考 |
|---|---|
| **运行浏览器认证流程并保存 `FIRECRAWL_API_KEY`** | [references/auth-flow.md](references/auth-flow.md) |
| **通过 Stripe Projects 配置密钥** | [docs.firecrawl.dev/integrations/stripe-projects](https://docs.firecrawl.dev/integrations/stripe-projects) |
| **安装正确的 SDK** | [references/sdk-installation.md](references/sdk-installation.md) |
| **将凭据写入 `.env` 或项目配置** | [references/project-setup.md](references/project-setup.md) |
| **设置完成后选择合适的接口** | [firecrawl-build](../firecrawl-build/SKILL.md) |
| **本次任务需要实时网页工具** | CLI 技能已随上述命令安装完毕 |
| **从已知 URL 开始实现** | [firecrawl-build-scrape](../firecrawl-build-scrape/SKILL.md) |
| **从查询开始实现** | [firecrawl-build-search](../firecrawl-build-search/SKILL.md) |

## 文档（权威来源）

请为项目语言读取权威来源页面，以获取 SDK 使用方法、数据模式和示例：

- **Node / TypeScript**：[docs.firecrawl.dev/agent-source-of-truth/node](https://docs.firecrawl.dev/agent-source-of-truth/node)
- **Python**：[docs.firecrawl.dev/agent-source-of-truth/python](https://docs.firecrawl.dev/agent-source-of-truth/python)
- **Rust**：[docs.firecrawl.dev/agent-source-of-truth/rust](https://docs.firecrawl.dev/agent-source-of-truth/rust)
- **Java**：[docs.firecrawl.dev/agent-source-of-truth/java](https://docs.firecrawl.dev/agent-source-of-truth/java)
- **Elixir**：[docs.firecrawl.dev/agent-source-of-truth/elixir](https://docs.firecrawl.dev/agent-source-of-truth/elixir)
- **cURL / REST**：[docs.firecrawl.dev/agent-source-of-truth/curl](https://docs.firecrawl.dev/agent-source-of-truth/curl)

## 设置完成后

密钥就位后：

1. 判断这是一个新项目还是已有代码库
2. 询问在产品中 Firecrawl 应完成哪些功能
3. 选择与所需行为最匹配的最窄接口
4. 编写代码前，为项目语言读取权威来源页面
5. 在代码中添加 SDK 或 REST 调用
6. 运行冒烟测试，确保一次真实的 Firecrawl 请求成功
7. 使用本仓库中与接口相关的技能获取实现指导
8. 如果在当前任务期间还需要实时网页工具，CLI 技能已随上述命令安装完毕，请使用 `firecrawl/cli`
