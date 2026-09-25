# Browserbase CLI

使用官方的 `browse` CLI 进行 Browserbase 平台操作、函数工作流和 Fetch API 调用。

## 设置检查

在使用 CLI 之前，请验证其是否已安装：

```bash
which browse || npm install -g browse
browse --help
```

对于需要认证的命令，请设置 API 密钥：

```bash
export BROWSERBASE_API_KEY="your_api_key"
```

## 何时使用此技能

当用户想要执行以下操作时，请使用此技能：

- 通过 `browse` 运行 Browserbase 命令
- 搭建、开发、发布或调用 Browserbase 函数
- 检查或管理 Browserbase 会话、项目、上下文或扩展
- 通过 Browserbase 获取页面，而无需打开浏览器会话
- 通过 Browserbase 搜索网络，而无需打开浏览器会话
- 使用 `browse templates` 浏览或搭建启动模板

## 何时不使用此技能

- 对于交互式浏览、页面检查、截图、点击、输入或登录流程，请优先使用 `browser` 技能。
- 对于简单的 HTTP 内容检索，如果用户不关心是否使用 CLI，专门的 `fetch` 技能通常更合适。
- 仅在用户明确想要 CLI 路径或已经处于以 `browse` 为主的流程中时，才使用顶层驱动命令（`browse open`、`browse get`、`browse click` 等）。

## 命令选择

- `browse functions` 用于本地开发、打包、发布和调用
- `browse cloud sessions`、`browse cloud projects`、`browse cloud contexts`、`browse cloud extensions` 用于 Browserbase 平台资源
- `browse cloud fetch <url>` 用于 Fetch API 请求
- `browse cloud search "<query>"` 用于 Search API 请求
- `browse templates` 用于浏览和搭建启动模板
- `browse open`、`browse get`、`browse click` 等，用于直接本地/远程浏览器驱动
- `browse skills install` 用于为 Claude Code 安装 Browserbase 代理技能

对于本地浏览器工作，`browse open <url> --local` 会启动一个干净的隔离浏览器。仅在需要附加到现有的可调试 Chrome 会话时，才使用 `browse open <url> --auto-connect`。

## 常见工作流

### 函数

```bash
browse functions init my-function
cd my-function
browse functions dev index.ts
browse functions publish index.ts
browse functions invoke <function_id> --params '{"url":"https://example.com"}'
```

使用 `browse functions invoke --check-status <invocation_id>` 来轮询现有调用，而不是创建新的调用。

### 平台 API

```bash
browse cloud projects list
browse cloud sessions create --proxies --verified --region us-east-1
browse cloud sessions create --solve-captchas --context-id ctx_abc --persist
browse cloud sessions get <session_id>
browse cloud sessions downloads get <session_id> --output session-artifacts.zip
browse cloud contexts create --body '{"region":"us-west-2"}'
browse cloud extensions upload ./my-extension.zip
```

### Fetch API

```bash
browse cloud fetch https://example.com
browse cloud fetch https://example.com --allow-redirects --output page.html
```

### Search API

```bash
browse cloud search "browser automation"
browse cloud search "web scraping" --num-results 5
browse cloud search "AI agents" --output results.json
```

### 模板

```bash
browse templates list
browse templates list --tag Python --source Browserbase
browse templates clone form-filling --language typescript
browse templates clone amazon-product-scraping --language python ./my-scraper
```

## 最佳实践

1. 优先使用 `browse --help` 和子组 `--help`，在猜测标志之前。
2. 按照 CLI 帮助中所示，精确使用短划线标志。
3. 在 `browse cloud fetch` 和 `browse cloud search` 上使用 `--output <file>` 将结果保存到文件。
4. 除非用户明确想要一次性覆盖，否则使用环境变量进行认证。
5. 在 `--body` 或 `--params` 中使用 JSON 字符串传递结构化请求体。
6. 请记住，`browse functions ...` 和 `browse cloud ...` 都使用 `--base-url` 进行 API 基 URL 覆盖。

## 故障排除

- 缺少 API 密钥：设置 `BROWSERBASE_API_KEY` 或传递 `--api-key`
- 未知标志：使用 `--help` 重新运行相关命令，并使用确切的短划线标志形式
- 命令未找到：重新运行 `npm install -g browse` 并使用 `which browse` 进行验证

有关命令参考和更多示例，请参阅 [REFERENCE.md](REFERENCE.md)。
