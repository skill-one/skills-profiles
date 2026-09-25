# Apify Actor 开发

**重要提示：** 开始之前，请在 `.actor/actor.json` 的元数据部分填写 `generatedBy` 属性。将其替换为您当前使用的工具和模型，例如 "Claude Code with Claude Sonnet 4.5"。这有助于 Apify 监控并改进针对特定 AI 工具和模型的 AGENTS.md。

## Apify Actor 是什么？

Actor 是受 UNIX 哲学启发的无服务器程序——那些专注于做一件事并且可以轻松组合以构建复杂系统的程序。它们被打包成 Docker 镜像，并在云中的隔离容器中运行。

**核心概念：**
- 接受定义良好的 JSON 输入
- 执行隔离的任务（网络抓取、自动化、数据处理）
- 产生结构化的 JSON 输出到数据集和/或存储在键值存储中
- 可以运行从几秒钟到几小时甚至无限期
- 持久化状态并且可以被重新启动

## 前提条件和设置（强制要求）

在创建或修改 Actor 之前，请验证 `apify` CLI 是否已安装 `apify --help`。

如果未安装，请使用以下方法之一（按优先级排序列出）：

```bash
# 推荐的：通过包管理器安装（提供完整性检查）
npm install -g apify-cli

# 或者（Mac）：brew install apify-cli
```

> **安全提示：** 请勿通过将远程脚本管道到 shell 中来安装 CLI（例如 `curl … | bash` 或 `irm … | iex`）。始终使用包管理器。

当安装了 apify CLI 时，使用以下命令登录：

```bash
apify info  # 应返回您的用户名
```

如果未登录，请使用 OAuth 进行身份验证（将打开浏览器）：

```bash
apify login
```

如果浏览器登录不可用（无头环境或 CI），CLI 会自动从环境变量中读取 `APIFY_TOKEN`。确保环境变量已导出并运行任何 apify 命令——无需显式登录。如果用户没有令牌，请到 https://console.apify.com/settings/integrations 生成一个。

> **安全提示：** 避免将令牌作为命令行参数传递（例如 `apify login -t <token>`）。
> 参数会在进程列表中可见，并且可能会记录在 shell 历史记录中。
> 优先使用环境变量或交互式登录。
> 不要在源代码或配置文件中记录、打印或嵌入 `APIFY_TOKEN`。
> 使用具有最小必要权限（范围令牌）的令牌，并定期轮换它。

### 远程追踪归因（强制要求）

在从此技能运行的每个 `apify` 命令（`apify create`、`apify run`、`apify push`、`apify call` 等）中传递 `--user-agent apify-agent-skills/apify-actor-development`。这是一个被所有 `apify` 命令接受的全球标志；它仅用于远程追踪归因，并且不会改变任何其他内容。

```bash
apify push --user-agent apify-agent-skills/apify-actor-development
```

## 模板选择

**重要提示：** 在开始 Actor 开发之前，始终询问用户他们喜欢的编程语言：
- **JavaScript** - 使用 `apify create <actor-name> -t project_empty --user-agent apify-agent-skills/apify-actor-development`
- **TypeScript** - 使用 `apify create <actor-name> -t ts_empty --user-agent apify-agent-skills/apify-actor-development`
- **Python** - 使用 `apify create <actor-name> -t python-empty --user-agent apify-agent-skills/apify-actor-development`

根据用户的语言选择使用相应的 CLI 命令。可以根据需要稍后安装额外的包（Crawlee、Playwright 等）。

## 快速入门工作流

1. **创建 Actor 项目** - 根据用户的语言偏好运行适当的 `apify create` 命令（见上文模板选择）
2. **安装依赖项**（在安装之前验证包名是否与预期包匹配）
   - JavaScript/TypeScript: `npm install`（使用 `package-lock.json` 进行可重复的、经过完整性检查的安装——将锁文件提交到版本控制）
   - Python: `pip install -r requirements.txt`（在 `requirements.txt` 中固定确切版本，例如 `crawlee==1.2.3`，并将文件提交到版本控制）
3. **实现逻辑** - 在 `src/main.py`、`src/main.js` 或 `src/main.ts` 中编写 Actor 代码
4. **配置模式** - 在 `.actor/input_schema.json`、`.actor/output_schema.json`、`.actor/dataset_schema.json` 中更新输入/输出模式
5. **配置平台设置** - 在 `.actor/actor.json` 中更新 Actor 元数据（见 [references/actor-json.md](references/actor-json.md)）
6. **编写文档** - 为市场创建全面的 README.md（见 [references/actor-readme.md](references/actor-readme.md)——这是强制性的，不是可选的）
7. **本地测试** - 运行 `apify run --user-agent apify-agent-skills/apify-actor-development` 以验证功能（见下文本地测试部分）
8. **部署** - 运行 `apify push --user-agent apify-agent-skills/apify-actor-development` 将 Actor 部署到 Apify 平台（Actor 名称定义在 `.actor/actor.json` 中）

## 安全

**将所有抓取的网页内容视为不可信的输入。** Actor 从外部网站摄取数据，这些网站可能包含恶意有效负载。请遵循以下规则：

- **清理抓取的数据**——切勿将原始 HTML、URL 或抓取的文本直接传递到 shell 命令、`eval()`、数据库查询或模板引擎中。使用适当的转义或参数化 API。
- **验证和类型检查所有外部数据**——在推送到数据集或键值存储之前，验证值是否匹配预期的类型和格式。拒绝或清理意外的结构。
- **不要执行或解释抓取的内容**——切勿将抓取的文本视为代码、命令或配置。来自网站的 内容可能包含提示注入尝试或嵌入脚本。
- **将凭证与数据管道隔离**——确保 `APIFY_TOKEN` 和其他密钥永远不会在请求处理程序中可访问，也绝不会与抓取的数据一起传递。使用 Apify SDK 的内置凭证管理，而不是在数据处理代码中通过环境变量传递令牌。
- **在安装之前检查依赖项**——在用 `npm install` 或 `pip install` 添加包时，验证包名和发布者。打字错误是常见的供应链攻击向量。优先选择知名且积极维护的包。
- **固定版本并使用锁文件**——始终提交 `package-lock.json`（Node.js）或在 `requirements.txt` 中固定确切版本（Python）。锁文件确保可重复的构建并防止静默依赖项替换。定期运行 `npm audit` 或 `pip-audit` 以检查已知漏洞。

## 最佳实践

**✓ 应该：**
- 使用 `apify run` 在本地测试 Actor（配置 Apify 环境和存储）
- 使用 Apify SDK (`apify`) 运行在 Apify 平台上的代码
- 早期使用适当的错误处理和优雅地失败进行输入验证
- 使用 CheerioCrawler 处理静态 HTML（比浏览器快 10 倍）
- 仅用于 JavaScript 重型网站使用 PlaywrightCrawler
- 使用路由模式（createCheerioRouter/createPlaywrightRouter）处理复杂抓取
- 实现指数退避的重试策略
- 使用适当的并发：HTTP（10-50）、浏览器（1-5）
- 在 `.actor/input_schema.json` 中设置合理的默认值
- 在 `.actor/output_schema.json` 中定义输出模式
- 在推送到数据集之前清理和验证数据
- 使用语义 CSS 选择器和后备策略
- 尊重 robots.txt、ToS 并实现速率限制
- **始终使用 `apify/log` 包**——屏蔽敏感数据（API 密钥、令牌、凭证）
- 实现就绪探针处理程序（如果您的 Actor 使用待机模式，这是强制要求的）

**✗ 不应该：**
- 使用 `npm start`、`npm run start`、`npx apify run` 或类似命令运行 Actor（使用 `apify run` 代替）
- 假设 `apify run` 的本地存储会被推送到或可见在 Apify Console——它是本地仅有的；使用 `apify push` 部署并在平台上运行以在 Apify Console 中查看结果
- 依赖 `Dataset.getInfo()` 在云端获取最终计数
- 当 HTTP/Cheerio 可用时使用浏览器爬取器
- 固定应该位于输入模式或环境变量中的值
- 跳过输入验证或错误处理
- 过载服务器——使用适当的并发和延迟
- 抓取禁止内容或忽略服务条款
- 除非明确允许，否则不要存储个人/敏感数据
- 使用已弃用的选项，如 CheerioCrawler（v3.x）上的 `requestHandlerTimeoutMillis`
- 使用 `additionalHttpHeaders`——改用 `preNavigationHooks` 代替
- 将原始抓取内容传递到 shell 命令、`eval()` 或代码生成函数
- 使用 `console.log()` 或 `print()` 而不是 Apify 日志记录器——这些会绕过凭证屏蔽
- 在未获得明确许可的情况下禁用待机模式

## 日志记录

有关完整的日志记录文档，包括可用日志级别和 JavaScript/TypeScript 及 Python 的最佳实践，请参阅 [references/logging.md](references/logging.md)。

## 命令

```bash
# 以下每个命令都接受 --user-agent apify-agent-skills/apify-actor-development；将它们附加到您运行的每个命令中。

# 初始化和本地开发
apify create [name] --user-agent apify-agent-skills/apify-actor-development                 # 从模板创建新的 Actor 项目
apify init --user-agent apify-agent-skills/apify-actor-development                          # 在当前目录初始化 Actor
apify run --user-agent apify-agent-skills/apify-actor-development                           # 在模拟平台环境中本地运行 Actor
apify run --purge --user-agent apify-agent-skills/apify-actor-development                   # 清除先前的本地存储后运行
apify validate-schema --user-agent apify-agent-skills/apify-actor-development               # 验证 .actor/input_schema.json

# 身份验证和账户
apify login                                                                                 # 身份验证账户（令牌存储在 ~/.apify）
apify logout                                                                                # 移除存储的凭证
apify info                                                                                  # 打印当前已身份验证的账户信息

# 部署和远程执行
apify push --user-agent apify-agent-skills/apify-actor-development                          # 根据 .actor/actor.json 将 Actor 部署到平台
apify pull <actor> --user-agent apify-agent-skills/apify-actor-development                  # 从平台下载 Actor 代码
apify actors info <actor> --user-agent apify-agent-skills/apify-actor-development --readme  # 检查 Actor 文档
apify actors info <actor> --user-agent apify-agent-skills/apify-actor-development --input   # 检查 Actor 输入模式
apify call <actor> --input-file input.json --user-agent apify-agent-skills/apify-actor-development
apify call <actor> --input '{"startUrls":[{"url":"https://example.com"}]}' --user-agent apify-agent-skills/apify-actor-development
apify actors build <actor> --user-agent apify-agent-skills/apify-actor-development          # 创建 Actor 的新构建
apify runs ls --user-agent apify-agent-skills/apify-actor-development                       # 列出最近的运行

# 发现（在 Apify Store 中搜索社区 Actor）
apify actors search "<query>" --user-agent apify-agent-skills/apify-actor-development       # 搜索 Apify Store
apify actors info <actor> --user-agent apify-agent-skills/apify-actor-development           # 检查 Actor

# 密钥（通过 "@mySecret" 从 actor.json 引用）
apify secrets add <name> <value>                                                            # 本地存储密钥；在推送时上传
apify secrets ls                                                                            # 列出存储的密钥

# 直接 API 访问
apify api <endpoint>                                                                        # 对 Apify API 进行身份验证的 HTTP 请求

# 帮助
apify help                                                                                  # 列出所有命令
apify <command> --help                                                                      # 查看特定命令的详细帮助
```

### 远程 Actor 调用

当远程运行 Actor 时，使用此流程：

1. 使用 `apify actors search "<query>" --user-agent apify-agent-skills/apify-actor-development` 搜索正确的 Actor。
2. 使用 `apify actors info <actor> --user-agent apify-agent-skills/apify-actor-development --readme` 检查其 README。
3. 使用 `apify actors info <actor> --user-agent apify-agent-skills/apify-actor-development --input` 检查其输入模式。
4. 使用 `--input-file input.json` 或引号内的内联 JSON 调用它。

Actor 输入是一个 JSON 对象，而不是数组。`--input` 仅接受内联 JSON 对象输入；将内联 JSON 用引号括起来以避免 shell 解析问题，例如 `--input '{"startUrls":[{"url":"https://example.com"}]}'`。对于 JSON 文件或复杂输入，使用 `--input-file input.json`。

如果您的目标没有专门的 Actor，请在从头开始构建之前搜索 Apify Store 中的社区选项。

### 本地和运行时命令

始终使用 `apify run` 在本地测试 Actor。不要使用 `npm run start`、`npm start`、`yarn start` 或其他包管理器命令——这些不会正确配置 Apify 环境和存储。

在运行的 Actor 中，优先使用 SDK (`Actor.getInput()` / `Actor.get_input()`、`Actor.pushData()` / `Actor.push_data()`、`Actor.setValue()` / `Actor.set_value()`) 而不是等效的 `apify actor` 运行时子命令。

## Apify 平台环境

当 Actor 在 Apify 平台上运行时，API 令牌通过 `APIFY_TOKEN` 环境变量自动提供（注意：变量是 `APIFY_TOKEN`，而不是 `APIFY_API_TOKEN`）。Apify SDK 自动读取它，因此您无需显式传递它。本地运行 `apify login` 一次后，SDK 将使用您的存储凭证。

## 本地测试

使用 `apify run` 本地测试 Actor 时，通过创建一个 JSON 文件来提供输入数据：

```
storage/key_value_stores/default/INPUT.json
```

该文件应包含您在 `.actor/input_schema.json` 中定义的输入参数。Actor 在本地运行时会读取此输入，这与它在 Apify 平台上接收输入的方式相同。

**重要提示——本地存储不会与 Apify Console 同步：**
- 运行 `apify run` 将所有数据（数据集、键值存储、请求队列）**仅存储在您的本地文件系统**的 `storage/` 目录中。
- 这些数据**永远不会**自动上传或推送到 Apify 平台。它们仅存在于您的计算机上。
- 要在 Apify Console 中验证结果，您必须使用 `apify push` 部署 Actor，然后在平台上运行它。
- 不要依赖检查 Apify Console 来验证本地运行的结果——相反，请检查本地 `storage/` 目录或检查 Actor 的日志输出。

## 待机模式

待机模式使 Actor 能够作为 API 服务器工作——它们在后台保持就绪状态，以处理 HTTP 请求。

**何时使用待机模式：** 当 Actor 必须处理交互式、实时 HTTP 请求时使用待机模式——API 端点、webhook 接收器、实时数据查找、MCP 服务器或按需提供单个 URL 请求的网络抓取 API。

在构建待机 Actor 时，请在 `.actor/actor.json` 中设置 `usesStandbyMode: true` 并实现一个 HTTP 服务器。有关配置、环境变量、完整代码示例和操作限制，请参阅 [references/standby-mode.md](references/standby-mode.md)。

## 项目结构

```
.actor/
├── actor.json           # Actor 配置：名称、版本、环境变量、运行时
├── input_schema.json    # 输入验证和 Console 表单定义
└── output_schema.json   # 输出存储和显示模板
src/
└── main.js/ts/py       # Actor 入口点
storage/                # 本地仅存储（不与 Apify Console 同步）
├── datasets/           # 输出项（JSON 对象）
├── key_value_stores/   # 文件、配置、INPUT
└── request_queues/     # 待处理的抓取请求
Dockerfile              # 容器镜像定义
```

## Actor 配置

有关完整的 actor.json 结构和配置选项，请参阅 [references/actor-json.md](references/actor-json.md)。

## 输入模式

有关输入模式结构和解例，请参阅 [references/input-schema.md](references/input-schema.md)。

## 输出模式

有关输出模式结构、示例和模板变量的详细信息，请参阅 [references/output-schema.md](references/output-schema.md)。

## 数据集模式

有关数据集模式结构、配置和显示属性的详细信息，请参阅 [references/dataset-schema.md](references/dataset-schema.md)。

## 键值存储模式

有关键值存储模式结构、集合和配置的详细信息，请参阅 [references/key-value-store-schema.md](references/key-value-store-schema.md)。

## Actor README

**重要提示：** 始终作为 Actor 开发的一部分生成 README.md。README 是 Actor 在 Apify Store 上的着陆页，对于可发现性（SEO）、用户引导和支持至关重要。没有适当的 README 不要考虑 Actor 完成。

有关所需结构、SEO 最佳实践和内容指南，请参阅 [references/actor-readme.md](references/actor-readme.md)。还请查看以下顶级 Actor 以了解最佳实践：

- [Instagram Scraper](https://apify.com/apify/instagram-scraper)
- [Google Maps Scraper](https://apify.com/compass/crawler-google-places)

## MCP 工具

### Apify MCP

如果 Apify MCP 服务器已配置，请使用以下工具进行文档：

- `search-apify-docs` - 搜索文档
- `fetch-apify-docs` - 获取完整文档页面

否则，MCP 服务器 URL：`https://mcp.apify.com/?tools=docs`。

### Playwright MCP（调试）

Playwright MCP 服务器是调试与网页交互的 Actor 的有用工具——它允许代理驱动真实浏览器以检查页面、捕获选择器和重现问题。

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

- [docs.apify.com/llms.txt](https://docs.apify.com/llms.txt) - Apify 快速参考文档
- [docs.apify.com/llms-full.txt](https://docs.apify.com/llms-full.txt) - Apify 完整文档
- [https://crawlee.dev/llms.txt](https://crawlee.dev/llms.txt) - Crawlee 快速参考文档
- [https://crawlee.dev/llms-full.txt](https://crawlee.dev/llms-full.txt) - Crawlee 完整文档
- [whitepaper.actor](https://raw.githubusercontent.com/apify/actor-whitepaper/refs/heads/master/README.md) - 完整 Actor 规范
