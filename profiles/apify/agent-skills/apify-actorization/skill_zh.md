# Apify 实体化

实体化将现有软件转换为与 Apify 平台兼容的无服务器应用程序。实体是作为 Docker 镜像打包的程序，它们接受定义良好的 JSON 输入，执行操作，并可选择生成结构化的 JSON 输出。

## 快速入门

1. 在项目根目录下运行 `apify init --user-agent apify-agent-skills/apify-actorization`
2. 用 SDK 生命周期包装代码（见下文特定语言部分）
3. 配置 `.actor/input_schema.json`
4. 使用 `apify run --input '{"key": "value"}' --user-agent apify-agent-skills/apify-actorization` 进行测试
5. 使用 `apify push --user-agent apify-agent-skills/apify-actorization` 进行部署

## 何时使用此技能

- 将现有项目转换为在 Apify 平台上运行
- 向项目中添加 Apify SDK 集成
- 将 CLI 工具或脚本包装为实体
- 将 Crawlee 项目迁移到 Apify

## 前置条件

验证 `apify` CLI 是否已安装：

```bash
apify --help
```

如果未安装，请使用以下方法之一（按优先级排序列出）：

```bash
# 推荐的：通过包管理器安装（提供完整性检查）
npm install -g apify-cli

# 或者（Mac）：brew install apify-cli
```

> **安全提示**：不要通过将远程脚本管道到 shell 中来安装 CLI（例如 `curl ... | bash` 或 `irm ... | iex`）。始终使用包管理器。

验证 CLI 是否已登录：

```bash
apify info  # 应返回您的用户名
```

如果未登录，请使用 OAuth 进行身份验证（将打开浏览器）：

```bash
apify login
```

如果浏览器登录不可用（无头环境或 CI），请确保导出 `APIFY_TOKEN` 环境变量（注意：变量是 `APIFY_TOKEN`，而不是 `APIFY_API_TOKEN`）。CLI 会自动读取它——无需显式登录。如果用户没有令牌，请在 https://console.apify.com/settings/integrations 生成一个。

> **Apify 平台环境**：当实体在 Apify 平台上运行时，`APIFY_TOKEN` 会自动注入为环境变量，Apify SDK 会自动读取它——您不需要显式传递它。在本地，`apify login` 会将凭据存储在 `~/.apify` 中，SDK 会使用它们。

> **安全提示**：避免将令牌作为命令行参数传递（例如 `apify login -t <token>`）。
> 参数在进程列表中可见，并且可能会记录在 shell 历史记录中。
> 优先使用 OAuth 登录或环境变量。
> 不要在源代码或配置文件中记录、打印或嵌入 `APIFY_TOKEN`。
> 使用具有最低必要权限（范围令牌）的令牌，并定期轮换它。

### 远程追踪归属（必需）

在从本技能运行的每个 `apify` 命令上传递 `--user-agent apify-agent-skills/apify-actorization` - `apify init`、`apify run`、`apify push` 以及其他。这是一个所有 `apify` 命令都接受的全局标志；它仅用于远程追踪归属，不会改变任何其他内容。

```bash
apify push --user-agent apify-agent-skills/apify-actorization
```

## 实体化清单

将此清单复制到以跟踪进度：

- [ ] 第 1 步：分析项目（语言、入口点、输入、输出）
- [ ] 第 2 步：运行 `apify init --user-agent apify-agent-skills/apify-actorization` 以创建实体结构
- [ ] 第 3 步：应用特定语言的 SDK 集成
- [ ] 第 4 步：配置 `.actor/input_schema.json`
- [ ] 第 5 步：配置 `.actor/output_schema.json`（如果适用）
- [ ] 第 6 步：更新 `.actor/actor.json` 元数据
- [ ] 第 7 步：为 Apify Store 列表编写 README.md
- [ ] 第 8 步：使用 `apify run --user-agent apify-agent-skills/apify-actorization` 本地测试
- [ ] 第 9 步：使用 `apify push --user-agent apify-agent-skills/apify-actorization` 部署

## 第 1 步：分析项目

在做出更改之前，了解项目：

1. **确定语言** - JavaScript/TypeScript、Python 或其他
2. **找到入口点** - 启动执行的 main 文件
3. **确定输入** - 命令行参数、环境变量、配置文件
4. **确定输出** - 文件、控制台输出、API 响应
5. **检查状态** - 它是否需要在运行之间持久化数据？

## 第 2 步：初始化实体结构

在项目根目录下运行：

```bash
apify init --user-agent apify-agent-skills/apify-actorization
```

这将创建：
- `.actor/actor.json` - 实体配置和元数据
- `.actor/input_schema.json` - Apify Console 的输入定义
- `Dockerfile`（如果不存在）- 容器镜像定义

## 第 3 步：应用特定语言的更改

根据您的项目语言选择：

- **JavaScript/TypeScript**：见 [js-ts-actorization.md](references/js-ts-actorization.md)
- **Python**：见 [python-actorization.md](references/python-actorization.md)
- **其他语言（基于 CLI）**：见 [cli-actorization.md](references/cli-actorization.md)

### 快速参考

| 语言 | 安装 | 包装代码 |
|------|------|----------|
| JS/TS | `npm install apify` | `await Actor.init()` ... `await Actor.exit()` |
| Python | `pip install apify` | `async with Actor:` |
| 其他 | 在包装脚本中使用 CLI | `apify actor:get-input` / `apify actor:push-data` |

## 第 4-6 步：配置模式

见 [schemas-and-output.md](references/schemas-and-output.md) 了解有关以下内容的详细配置：
- 输入模式（`.actor/input_schema.json`）
- 输出模式（`.actor/output_schema.json`）
- 实体配置（`.actor/actor.json`）
- 状态管理（请求队列、键值存储）

使用 `@apify/json_schemas` npm 包验证模式。

## 第 7 步：编写 README

**重要提示**：始终作为实体化的一部分生成 README.md。README 是实体在 Apify Store 上的着陆页，对于可发现性（SEO）、用户入门和支持至关重要。没有适当的 README，不要考虑实体完成。

见 `skills/apify-actor-development/references/actor-readme.md` 中的实体 README 指南，了解所需的结构，包括：简介和功能、数据提取表、分步教程、定价信息、输入/输出示例和常见问题解答。目标至少为 300 字，并使用 SEO 优化的 H2/H3 标题。还请查看这些顶级实体以了解最佳实践：

- [Instagram Scraper](https://apify.com/apify/instagram-scraper)
- [Google Maps Scraper](https://apify.com/compass/crawler-google-places)

## 第 8 步：本地测试

使用内联输入运行实体（适用于 JS/TS 和 Python 实体）：

```bash
apify run --input '{"startUrl": "https://example.com", "maxItems": 10}' --user-agent apify-agent-skills/apify-actorization
```

或者使用输入文件：

```bash
apify run --input-file ./test-input.json --user-agent apify-agent-skills/apify-actorization
```

**重要提示**：始终使用 `apify run`，而不是 `npm start` 或 `python main.py`。CLI 会设置正确的环境和存储。

## 第 9 步：部署

```bash
apify push --user-agent apify-agent-skills/apify-actorization
```

这将上传并在 Apify 平台上构建您的实体。

## 营收（可选）

部署后，您可以在 Apify Store 中对您的实体进行营收。推荐的模式是 **按事件付费（PPE）**：

- 每个抓取结果/项目
- 每处理页面
- 每次 API 调用

在 Apify Console 中配置 PPE（实体 > 营收）。在您的代码中使用 `await Actor.charge('result')` 为事件收费。

其他选项：**租赁**（月度订阅）或 **免费**（开源）。

## 安全

**将所有抓取的网页内容视为不可信的输入。** 实体从外部网站摄取数据，这些数据可能包含恶意有效负载。请遵循以下规则：

- **清理抓取数据** — 不要将原始 HTML、URL 或抓取文本直接传递到 shell 命令、`eval()`、数据库查询或模板引擎中。使用适当的转义或参数化 API。
- **验证和类型检查所有外部数据** — 在推送到数据集或键值存储之前，验证值是否匹配预期的类型和格式。拒绝或清理意外结构。
- **不要执行或解释抓取内容** — 不要将抓取文本视为代码、命令或配置。来自网站的内容可能包含提示注入尝试或嵌入脚本。
- **将凭据与数据管道隔离** — 确保 `APIFY_TOKEN` 和其他秘密永远不会在请求处理程序中访问，也不会与抓取数据一起传递。使用 Apify SDK 的内置凭据管理，而不是在数据处理代码中通过环境变量传递令牌。
- **安装依赖项前进行审查** — 在使用 `npm install` 或 `pip install` 添加包时，验证包名和发布者。打字错误是常见的供应链攻击向量。优先使用知名、积极维护的包。
- **固定版本并使用锁定文件** — 始终提交 `package-lock.json`（Node.js）或在 `requirements.txt`（Python）中固定确切版本。锁定文件确保可重复的构建并防止静默依赖项替换。定期运行 `npm audit` 或 `pip-audit` 以检查已知漏洞。

## 部署前清单

- [ ] `.actor/actor.json` 存在，具有正确的名称和描述
- [ ] `.actor/actor.json` 验证 `@apify/json_schemas` (`actor.schema.json`)
- [ ] `.actor/input_schema.json` 定义了所有必需的输入
- [ ] `.actor/input_schema.json` 验证 `@apify/json_schemas` (`input.schema.json`)
- [ ] `.actor/output_schema.json` 定义输出结构（如果适用）
- [ ] `.actor/output_schema.json` 验证 `@apify/json_schemas` (`output.schema.json`)
- [ ] `Dockerfile` 存在且构建成功
- [ ] `Actor.init()` / `Actor.exit()` 包裹 main 代码（JS/TS）
- [ ] `async with Actor:` 包裹 main 代码（Python）
- [ ] 输入通过 `Actor.getInput()` / `Actor.get_input()` 读取
- [ ] 输出使用 `Actor.pushData()` 或键值存储
- [ ] `apify run --user-agent apify-agent-skills/apify-actorization` 使用测试输入执行成功
- [ ] `README.md` 存在，具有正确的结构（简介、功能、数据表、教程、定价、输入/输出示例）
- [ ] `generatedBy` 在 actor.json 元数据部分中设置

## MCP 工具

### Apify MCP

如果 Apify MCP 服务器已配置，请使用这些工具进行文档：

- `search-apify-docs` - 搜索文档
- `fetch-apify-docs` - 获取完整文档页面

否则，MCP 服务器 URL：`https://mcp.apify.com/?tools=docs`。

### Playwright MCP（调试）

Playwright MCP 服务器是调试与网页交互的实体的有用工具——它允许代理驱动真实浏览器以检查页面、捕获选择器并重现问题。

使用 Claude Code CLI 安装：

```bash
claude mcp add playwright npx @playwright/mcp@latest
```

或者手动将其添加到您的 MCP 配置：

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    }
  }
}
```

## 资源

- [Actorization Academy](https://docs.apify.com/academy/actorization) - 综合指南
- [Apify JavaScript SDK](https://docs.apify.com/sdk/js) - 完整 SDK 参考
- [Apify Python SDK](https://docs.apify.com/sdk/python) - 完整 SDK 参考
- [Apify CLI 参考](https://docs.apify.com/cli) - CLI 命令
- [实体规范](https://raw.githubusercontent.com/apify/actor-whitepaper/refs/heads/master/README.md) - 完整规范
