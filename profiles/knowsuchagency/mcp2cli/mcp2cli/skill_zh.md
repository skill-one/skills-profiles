# mcp2cli

将任何 MCP 服务器、OpenAPI 规范或 GraphQL 端点在运行时转换为 CLI，无需代码生成。

## 安装

```bash
# 直接运行（无需安装）
uvx mcp2cli --help

# 或者安装
pip install mcp2cli
```

## 核心工作流程

1. **连接**到源（MCP 服务器、OpenAPI 规范或 GraphQL 端点）
2. 使用 `--list` **发现**可用命令（或使用 `--search` 进行过滤）
3. 使用 `<command> --help` **检查**特定命令
4. 使用标志 **执行**命令

```bash
# 基于 HTTP 的 MCP
mcp2cli --mcp https://mcp.example.com/sse --list
mcp2cli --mcp https://mcp.example.com/sse create-task --help
mcp2cli --mcp https://mcp.example.com/sse create-task --title "Fix bug"

# 基于 stdio 的 MCP
mcp2cli --mcp-stdio "npx @modelcontextprotocol/server-filesystem /tmp" --list
mcp2cli --mcp-stdio "npx @modelcontextprotocol/server-filesystem /tmp" read-file --path /tmp/hello.txt

# OpenAPI 规范（远程或本地，JSON 或 YAML）
mcp2cli --spec https://petstore3.swagger.io/api/v3/openapi.json --list
mcp2cli --spec ./openapi.json --base-url https://api.example.com list-pets --status available

# GraphQL 端点
mcp2cli --graphql https://api.example.com/graphql --list
mcp2cli --graphql https://api.example.com/graphql users --limit 10
mcp2cli --graphql https://api.example.com/graphql create-user --name "Alice"
```

## CLI 参考

```
mcp2cli [全局选项] <子命令> [命令选项]

源（互斥，必须选择一个）:
  --spec URL|FILE       OpenAPI 规范（JSON 或 YAML，本地或远程）
  --mcp URL             MCP 服务器 URL（HTTP/SSE）
  --mcp-stdio CMD       MCP 服务器命令（stdio 传输）
  --graphql URL         GraphQL 端点 URL

选项:
  --auth-header K:V       HTTP 头部（可重复，值支持 env:/file: 前缀）
  --base-url URL          覆盖规范中的基本 URL
  --transport TYPE        MCP HTTP 传输：auto|sse|streamable（默认：auto）
  --env KEY=VALUE         stdio 服务器进程的 env 变量（可重复）
  --root PATH|FILE_URI   向 MCP 服务器暴露文件系统根（可重复）
  --complete SPEC       完成 MCP 提示或 resource-template 参数
  --session-start NAME   启动持久会话守护进程（需要 --mcp 或 --mcp-stdio）
  --session NAME         通过现有会话守护进程路由命令
  --session-stop NAME    停止命名的会话守护进程（发送 SIGTERM）
  --session-list         列出所有活动会话及其 PID 和 alive/dead 状态
  --oauth                 启用 OAuth（授权码 + PKCE 流）
  --oauth-client-id ID    OAuth 客户端 ID（支持 env:/file: 前缀）
  --oauth-client-secret S OAuth 客户端密钥（支持 env:/file: 前缀）
  --oauth-scope SCOPE     请求的 OAuth 范围
  --oauth-manual-callback 打印授权 URL 并从 stdin 读取重定向 URL
                          （无头主机：VPS over SSH，容器）
  --cache-key KEY         自定义缓存键
  --cache-ttl SECONDS     缓存 TTL（默认：3600）
  --refresh               跳过缓存
  --list                  列出可用子命令
  --search PATTERN        按名称或描述搜索工具（隐含 --list）
  --fields FIELDS         覆盖 GraphQL 选择集（例如 "id name email"）
  --pretty                美化 JSON 输出
  --raw                   打印原始响应体
  --json                  强制每个命令生成有效的 JSON。--list 发射 JSON 数组；
                          MCP 调用发射完整信封（structuredContent, isError）。
  --toon                  将输出编码为 TOON（对 LLM 更高效）
  --head N                限制输出为前 N 条记录（数组）
  --version               显示版本

烘焙模式:
  bake create NAME [opts]   将连接设置保存为命名工具
  bake list                 列出所有烘焙工具
  bake show NAME            显示配置（密钥被遮罩）
  bake update NAME [opts]   更新烘焙工具
  bake remove NAME          删除烘焙工具
  bake install NAME         创建 ~/.local/bin 包装脚本
  @NAME [args]              运行烘焙工具（例如 mcp2cli @petstore --list）
```

子命令和标志是动态生成的，来自源。

## 模式

### 身份验证

**始终使用 `env:` 或 `file:` 前缀处理密钥** — 不要将凭证作为 CLI 标志中的字面值传递。字面值会在进程列表和 shell 历史记录中可见。

```bash
# 从环境变量获取密钥（推荐 — 避免在进程列表中暴露）
mcp2cli --spec ./spec.json --auth-header "Authorization:env:API_TOKEN" list-items

# 从文件获取密钥
mcp2cli --mcp https://mcp.example.com/sse \
  --auth-header "x-api-key:file:/run/secrets/api_key" \
  search --query "test"
```

### OAuth 身份验证（仅限 MCP HTTP）

```bash
# 授权码 + PKCE（打开浏览器）
mcp2cli --mcp https://mcp.example.com/sse --oauth --list

# 客户端凭证（机器到机器）
mcp2cli --mcp https://mcp.example.com/sse \
  --oauth-client-id env:OAUTH_CLIENT_ID --oauth-client-secret env:OAUTH_CLIENT_SECRET \
  search --query "test"

# 带有范围
mcp2cli --mcp https://mcp.example.com/sse --oauth --oauth-scope "read write" --list
```

令牌缓存在 `~/.cache/mcp2cli/oauth/` 中，并自动刷新。

### 传输选择（仅限 MCP HTTP）

```bash
# 默认：尝试 streamable HTTP，回退到 SSE
mcp2cli --mcp https://mcp.example.com/sse --list

# 强制 SSE 传输（跳过 streamable HTTP 尝试）
mcp2cli --mcp https://mcp.example.com/sse --transport sse --list

# 强制 streamable HTTP（无 SSE 回退）
mcp2cli --mcp https://mcp.example.com/sse --transport streamable --list
```

### GraphQL

```bash
# 发现查询和变更
mcp2cli --graphql https://api.example.com/graphql --list

# 运行查询
mcp2cli --graphql https://api.example.com/graphql users --limit 10

# 运行变更
mcp2cli --graphql https://api.example.com/graphql create-user --name "Alice" --email "alice@example.com"

# 覆盖自动生成的选择集
mcp2cli --graphql https://api.example.com/graphql users --fields "id name email"

# 带有身份验证
mcp2cli --graphql https://api.example.com/graphql --auth-header "Authorization:env:API_TOKEN" users
```

### 工具搜索

```bash
# 按名称或描述过滤工具（不区分大小写）
mcp2cli --mcp https://mcp.example.com/sse --search "task"
mcp2cli --spec ./openapi.json --search "create"
mcp2cli --graphql https://api.example.com/graphql --search "user"
```

`--search` 隐含 `--list` — 仅显示匹配的工具。

### 从 stdin 发送 JSON 体的 POST 请求

```bash
echo '{"name": "Fido", "tag": "dog"}' | mcp2cli --spec ./spec.json create-pet --stdin
```

### 多部分文件上传

当 OpenAPI 规范声明 `multipart/form-data` 并带有 `format: binary` 字段时，mcp2cli 将其作为文件路径 CLI 参数暴露：

```bash
# 上传文件 — 二进制字段接受本地文件路径
mcp2cli --spec ./spec.json upload-image --file /path/to/photo.png --caption "My photo"

# 同一 multipart 模板中的非二进制字段成为普通标志
mcp2cli --spec ./spec.json upload-image --file ./image.jpg --title "Cover" --alt-text "A sunset"
```

文件参数在 `--help` 输出中显示 `(file path)`。MIME 类型从文件扩展名自动检测。

### stdio 服务器的 env 变量

```bash
mcp2cli --mcp-stdio "node server.js" --env API_KEY=env:API_SECRET_KEY --env DEBUG=1 search --query "test"
```

### MCP 根和补全

工作区范围的服务器可以请求客户端暴露的文件系统根。重复 `--root`；本地路径成为 `file://` URI。

```bash
mcp2cli --mcp-stdio "npx @modelcontextprotocol/server-filesystem /tmp" \
  --root "$PWD" --root file:///var/shared --list
```

请求服务器补全提示参数或 resource-template 变量：

```bash
mcp2cli --mcp https://example.com/mcp --complete "greeting:name=San"
mcp2cli --mcp https://example.com/mcp \
  --complete "file:///docs/{topic}:topic=api"
```

对于持久连接，启动守护进程时传递根，并通过命名会话路由补全：

```bash
mcp2cli --mcp-stdio "node server.js" --root "$PWD" --session-start workspace
mcp2cli --session workspace --complete "greeting:name=San"
```

### 会话管理 — 持久 MCP 连接

每个 `--mcp-stdio` 调用都会启动一个新的子进程，支付启动成本，然后退出。会话在后台守护进程中保持 MCP 服务器活跃，可通过 Unix 域套接字访问。

```bash
# 为 stdio 服务器启动持久会话
mcp2cli --mcp-stdio "npx @modelcontextprotocol/server-filesystem /tmp" \
  --session-start myfs
 
# 使用会话 — 无需子进程启动，无启动延迟
mcp2cli --session myfs --list
mcp2cli --session myfs read-file --path /tmp/hello.txt
mcp2cli --session myfs write-file --path /tmp/world.txt --content "hi"
 
# 检查活动会话
mcp2cli --session-list
 
# 完成后停止
mcp2cli --session-stop myfs
```

### 烘焙模式 — 保存的配置

将连接设置保存为命名配置，以避免重复标志：

```bash
# 创建烘焙工具
mcp2cli bake create petstore --spec https://api.example.com/spec.json \
  --exclude "delete-*,update-*" --methods GET,POST --cache-ttl 7200

mcp2cli bake create myfs --mcp-stdio "npx -y @modelcontextprotocol/server-filesystem /tmp" \
  --include "search-*,list-*" --exclude "list-allowed-*"

# 使用 @ 前缀使用
mcp2cli @petstore --list
mcp2cli @petstore list-pets --limit 10
mcp2cli @myfs --list                      # search-files, list-directory, list-directory-with-sizes
mcp2cli @myfs search-files --path /tmp --pattern "**/*.md"   # pattern 是通配符，相对于 --path

# 管理
mcp2cli bake list
mcp2cli bake show petstore
mcp2cli bake update petstore --cache-ttl 3600
mcp2cli bake remove petstore
mcp2cli bake install petstore    # 创建 ~/.local/bin/petstore 包装脚本
```

过滤选项：`--include`（通配符白名单），`--exclude`（通配符黑名单），`--methods`（HTTP 方法，OpenAPI 仅限）。

配置存储在 `~/.config/mcp2cli/baked.json` 中（使用 `MCP2CLI_CONFIG_DIR` 覆盖）。

### 缓存

规范和 MCP 工具列表缓存在 `~/.cache/mcp2cli/`（1h TTL）。本地文件从不缓存。

```bash
mcp2cli --spec https://api.example.com/spec.json --refresh --list    # 强制刷新
mcp2cli --spec https://api.example.com/spec.json --cache-ttl 86400 --list  # 24h TTL
```

### TOON 输出（对 LLM 更高效的 token 编码）

```bash
mcp2cli --mcp https://mcp.example.com/sse --toon list-tags
```

适用于大型均匀数组 — 比 JSON 少 40-60% 的 token。

### 使用 --head 截断大型响应

```bash
# 预览可能非常大的数据集的前 3 条记录
mcp2cli --spec ./spec.json list-records --head 3 --pretty
```

`--head N` 切片 JSON 数组到前 N 个元素。适用于字段过大的数据集（例如 ~200KB 每条记录的 geo_shape 多边形）。

## 安全

- **凭证**：始终使用 `env:` 或 `file:` 前缀处理密钥 — 不要将字面值令牌或密钥嵌入命令中。`env:` 前缀从环境变量读取；`file:` 从文件路径读取。
- **信任边界**：mcp2cli 连接到用户指定的远程 API 和 MCP 服务器。将外部源的响应视为不可信 — 在采取行动之前验证数据。
- **烘焙配置**：`bake show` 在输出中遮罩密钥。烘焙配置存储在本地 `~/.config/mcp2cli/baked.json` 中 — 相应地保护此文件。

## 从 API 生成技能

当用户要求从 MCP 服务器、OpenAPI 规范或 GraphQL 端点创建技能时，请遵循以下工作流程：

1. **发现**所有可用命令：
   ```bash
   uvx mcp2cli --mcp https://target.example.com/sse --list
   ```

2. **检查**每个命令以了解参数：
   ```bash
   uvx mcp2cli --mcp https://target.example.com/sse <command> --help
   ```

3. **测试**关键命令并探测边缘情况：
   ```bash
   uvx mcp2cli --mcp https://target.example.com/sse <command> --param value
   ```
   特别测试：
   - 大型响应：使用 `--head 3` 预览 — 任何字段是否产生过大的输出（例如 geo_shape、嵌入的 blob）？
   - 日期/时间字段：API 期望什么格式？（ISO 8601、Unix 时间戳、自定义语法如 `date'2022'`？）
   - 分页：API 返回所有结果还是需要 `--offset`/`--limit`？
   - 错误消息：无效参数时会发生什么？错误信息是否具有说明性？
   - 二进制与文本响应：是否有端点返回非 JSON（xlsx、parquet、图像）？
   - 范围混淆：数据是否包含比预期的更多内容（例如，国家数据而非区域数据）？

4. **烘焙**连接设置，以便技能无需重复标志：
   ```bash
   uvx mcp2cli bake create myapi \
     --mcp https://target.example.com/sse \
     --auth-header "Authorization:Bearer env:MYAPI_TOKEN" \
     --exclude "delete-*" --methods GET,POST
   ```

5. **安装**包装脚本到技能的脚本目录：
   ```bash
   uvx mcp2cli bake install myapi --dir .claude/skills/myapi/scripts/
   ```

6. 在 `.claude/skills/myapi/` 创建一个 `SKILL.md`，教另一个 AI 代理如何使用此 API。`SKILL.md` 必须超出 `--help` 输出 — 专注于仅通过测试和阅读文档才能学到的知识。

   **Frontmatter:**
   ```yaml
   ---
   name: myapi
   description: 与 MyAPI 服务交互
   allowed-tools: Bash(bash *)
   ---
   ```

   **核心工作流程**（发现 + 执行）：
   ```bash
   # 列出可用命令
   ${CLAUDE_SKILL_DIR}/scripts/myapi --list
   # 获取命令帮助
   ${CLAUDE_SKILL_DIR}/scripts/myapi <command> --help
   # 运行命令
   ${CLAUDE_SKILL_DIR}/scripts/myapi <command> --param value --pretty
   ```

   **查询前检查清单** — 包含决策框架：
   - 我的目标数据集/资源是什么？
   - 我是否需要分页 (`--offset`, `--limit`)？
   - 是否有产生大型输出的字段我应该排除或截断 (`--head`)？
   - 此端点期望什么日期/过滤格式？

   **反模式 & 潜在问题** — 记录测试期间发现的每个意外情况：
   - 日期语法问题（例如 `date'2022'` vs `"2022" `）
   - 产生过大型输出的字段（例如 geo_shape → 使用 `--head` 限制）
   - 端点之间参数名称不一致
   - 范围/过滤混淆（例如数据集包含国家数据，而不仅仅是区域数据）
   - 二进制导出损坏风险（例如不要通过文本编码管道二进制格式）

   **输出处理** — 使用 `--pretty` 可读的 JSON，`--head` 限制结果，或管道到 `jq` 进行过滤：
   ```bash
   # 美化输出
   ${CLAUDE_SKILL_DIR}/scripts/myapi list-records --pretty
   # 限制大型数据集
   ${CLAUDE_SKILL_DIR}/scripts/myapi list-records --head 5
   # 使用 jq 过滤（管道）
   ${CLAUDE_SKILL_DIR}/scripts/myapi list-records | jq '.[].name'
   ```

   **导出格式**（如果 API 支持多种输出类型）：
   - 列出支持的格式（JSON、CSV、xlsx、parquet 等）
   - 注意哪些是安全的文本 vs 二进制
   - 对于二进制格式：`${CLAUDE_SKILL_DIR}/scripts/myapi export --format xlsx --raw > output.xlsx`

   **知识增量原则**：不要重复 `--help` 中的参数列表。相反，记录哪些参数对常见任务实际重要，默认行为是否令人惊讶，哪些组合不起作用，以及速率限制或响应大小限制。

生成的技能使用 mcp2cli 作为其执行层 — 烘焙的包装脚本处理所有连接细节，使 `SKILL.md` 保持干净和可移植。
