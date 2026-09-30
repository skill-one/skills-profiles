---
name: phoenix-cli
description: 使用 Phoenix CLI 调试 LLM 应用。获取跟踪记录、跨度、会话，进行标注，分析错误，检查数据集，审查实验，查询标注配置，并使用 GraphQL API。用户从终端与 Phoenix 实例交互时，均可使用。
---

# Phoenix CLI

## 调用方式

```bash
px <资源> <操作>                          # 如果全局安装
npx @arizeai/phoenix-cli <资源> <操作>    # 无需安装
```

CLI 使用单数资源命令，并带有 `list` 和 `get` 等子命令：

```bash
px trace list
px trace get <trace-id>
px trace annotate <trace-id>
px trace add-note <trace-id>
px trace delete <trace-identifier>
px trace-annotations delete
px span list
px span annotate <span-id>
px span add-note <span-id>
px span delete <span-identifier>
px span-annotations delete
px session list
px session get <session-id>
px session annotate <session-id>
px session add-note <session-id>
px session delete <session-id>
px session-annotations delete
px dataset list
px dataset get <name>
px dataset delete <dataset-identifier>
px experiment list
px experiment get <id>
px experiment delete <experiment-id>
px prompt list
px prompt get <prompt-identifier>
px prompt delete <prompt-identifier>
px project list
px project get <name>
px project delete <project-identifier>
px annotation-config list
px annotation-config get <identifier>
px annotation-config create
px annotation-config update <identifier>
px annotation-config delete <id>
px auth login
px auth logout
px auth status
px profile list
px profile show [name]
px profile create <name>
px profile use <name>
px profile edit <name>
px profile delete <name>
px api graphql <query>
px docs fetch
px setup
px self update
```

上述所有 `delete` 命令都需要环境变量 `PHOENIX_CLI_DANGEROUSLY_ENABLE_DELETES=true`，否则会提示确认（除非使用 `-y`/`--yes` 参数）。`px profile delete` 仅在本地执行，且无需环境变量即可使用 `--yes` 参数。如果没有设置环境变量，命令将不会执行删除操作。

## 配置

```bash
export PHOENIX_ENDPOINT=http://localhost:6006
export PHOENIX_PROJECT=my-project
export PHOENIX_API_KEY=your-api-key  # 如果启用了认证
```

`PHOENIX_ENDPOINT` 是 API 访问的基础 URL。它通常与 `PHOENIX_COLLECTOR_ENDPOINT` 相同；如果只设置了收集器变量，CLI 也会使用它进行 API 访问。

对于交互式本地使用，`px auth login` 会将 OAuth 会话存储在选定的配置文件中；该会话将以登录用户的权限执行。当同时配置了 API 密钥和 OAuth 令牌时，API 密钥优先级更高。OAuth 访问令牌会自动刷新 REST、GraphQL 和 PXI 请求，并且旋转的令牌会持久化到选定的配置文件中。

在将输出管道传递给 `jq` 时，始终使用 `--format raw --no-progress`。

### `px setup` — 新手引导

`px setup` 将当前目录中的应用程序连接到 Phoenix 部署，并写入 `.env.phoenix`（模式 0600，git 忽略）。交互式流程是为人类设计的——它会提示、启动编码代理，并轮询跟踪。**从代理运行时，始终传递 `--no-input`：**

```bash
# 仅注册：连接 + .env.phoenix，无源代码更改。
px setup --no-input --endpoint http://localhost:6006 --project my-app --format raw
```

无头模式需要一个干净的 git 仓库，并且默认情况下在写入文件后停止——它不会修改源代码，除非你明确要求。如果启用了认证，还需要设置 `PHOENIX_API_KEY`。项目不需要存在——Phoenix 会在第一次跟踪时创建它。输入错误会退出 `3` 并提供精确的修复建议；取消会退出 `2`。

要同时监控应用程序，请命名通道——无头模式没有选择通道的提示，因此 `--instrument` 需要 `--agent`：

```bash
px setup --no-input --instrument --agent claude --yolo --format raw
```

`--yolo` 很重要：后台代理没有终端来批准其编辑，因此如果没有它，运行将一直停滞，直到跟踪验证超时。`--language python` 会跳过代理的语言检测。`--docs-mcp` 将 Phoenix 文档 MCP 服务器连接到交接代理（`claude mcp add` 用于 claude，配置文件合并用于 cursor/opencode；codex 不支持）并跳过 `.px/docs` 下载——代理按需搜索文档；任何失败都会回退到下载。`--no-docs-mcp` 会抑制交互式提议。`--format raw` 会打印
`{"endpoint","project","files","instrumentation","tracesVerified","tracesUrl"}`
——检查 `tracesVerified`，它只有在 API 确认跟踪到达时才会被设置，而不是代理声称完成时。

一个等待超时但没有跟踪的运行会退出 `6`，而不是 `0`：配置和编辑是真实的，但跟踪没有确认工作。将其视为报告失败，而不是成功——不要用交接代理自己的退出代码或摘要来代替结论。没有 `--instrument` 注册，并且在超时提示时人类回答“稍后验证”，两者都会退出 `0`。

对于仅注册的运行，`tracesVerified` 也是 `false`，因此它无法区分“无内容验证”和“未到达跟踪”。当需要区分时，请读取 `verification`
(`verified` / `notVerified` / `deferred`，当没有内容需要验证时不存在)。

可重运行的切片，因此已注册的仓库会跳过问题：

```bash
px setup instrument --agent claude   # 仅监控 + 验证
px setup skills                      # 安装 Phoenix 编码代理技能
```

### `px setup mcp` — 注册远程 MCP 服务器

将 Phoenix 远程 MCP 服务器（`<endpoint>/mcp`）连接到编码代理，以便它可以查询 Phoenix 数据。端点从 `--endpoint`、活动配置文件或 `PHOENIX_ENDPOINT` 推断。基本命令提示范围（全局默认）然后代理；`--agent` 跳过两者。

```bash
px setup mcp --agent codex --no-input --format raw
px setup mcp --agent claude --local            # 写入此仓库的 .mcp.json
```

代理：`claude`、`codex`、`gemini`、`cursor`、`opencode`、`vscode`。范围是 `--global`（默认）或 `--local`（仓库；Codex 仅全局）。认证默认为 OAuth（URL 配置，首次使用时浏览器登录）；传递 `--header "Name: value"`（可重复）以用于 API 密钥的 bearer 降级——对于 Codex，`Authorization: Bearer ${VAR}` 头会变成 `bearer_token_env_var`。`--format raw` 会打印 `{"endpoint","url","serverName","agent","scope","auth","file?"}`。

## 认证

```bash
px auth login                                 # 基于浏览器的 OAuth 登录
px auth login --no-browser                    # 打印用于 SSH/无头使用的 URL
px auth logout                                # 清除 OAuth 令牌；保留 API 密钥
px auth status                                # 检查连接和认证状态
px auth status --endpoint http://other:6006   # 检查特定端点
px auth status --profile staging              # 检查命名配置文件的连接
px auth status --format raw                   # 机器可读的凭证来源
```

`auth status` 报告凭证来源（`flag`、`env`、`profile-key`、`oauth` 或 `none`）。OAuth 状态包括令牌过期时间。

当存储的凭证来源是 `oauth` 并且认证探测失败时，`auth status` 会无凭证重试一次，并且只有在服务器明确说明访问是匿名的情况下才会报告匿名访问。这可以防止陈旧或过期的配置文件令牌被报告为对已从 OAuth 切换到匿名访问的部署的认证失败。

## 配置文件

命名配置文件允许您在多个 Phoenix 实例（本地、测试、云）之间切换，而无需管理环境变量。配置文件存储在 `~/.px/settings.json`（或 `$XDG_CONFIG_HOME/px/settings.json`）。

配置优先级（从高到低）：CLI 标志 > 环境变量 > 活动配置文件 > 最近的 `.env.phoenix` 文件 > 内置默认值。

CLI 还会在当前工作目录或其上级目录发现最近的 `.env.phoenix` 文件（`px setup` 写入的相同文件）。凭证作为一组解析，因此进程 API 密钥永远不会与文件提供的头组合。设置 `PHOENIX_DISCOVER_CONFIG=false` 以禁用发现。

```bash
px profile list                              # 列出所有配置文件（显示活动配置文件）
px profile show                              # 显示活动配置文件的设置
px profile show staging                      # 显示命名配置文件的设置
px profile create prod --endpoint https://app.phoenix.arize.com --api-key <key> --activate
px profile create local --endpoint http://localhost:6006 --project my-app
px profile use prod                          # 切换活动配置文件
px profile edit prod                         # 在 $EDITOR 中打开配置文件 JSON（保存时验证）
px profile delete prod --yes                 # 删除配置文件（--yes 跳过确认）
```

在任何命令上使用 `--profile <name>` 以针对特定配置文件，而无需更改活动配置文件：

```bash
px trace list --profile staging --limit 10 --format raw --no-progress | jq .
px auth status --profile prod
```

`px profile create` 选项：`--endpoint <url>`、`--project <name>`、`--api-key <key>`、`--header <key=value>`（可重复）、`--activate`。

## 项目

```bash
px project list                                            # 列出所有项目（表格视图）
px project list --format raw --no-progress | jq '.[].name' # 项目名称作为 JSON
px project list --name-contains prod                       # 按名称子字符串过滤（不区分大小写）
px project get my-project --format raw --no-progress       # 通过确切名称获取单个记录
px project get my-project --format raw --no-progress | jq -r '.id'  # 提取项目 ID
```

`project list` 接受 `--limit <n>`（每页获取的项目数）和
`--name-contains <filter>`，它在服务器端按不区分大小写的名称子字符串进行过滤。当您只知道项目名称的一部分时，使用它而不是将 `list` 管道传递给 `grep`。

`project get` 在名称不匹配时退出 `ExitCode.FAILURE`（1），并将 `StructuredError` `{error, code: "FAILURE", hint}` 写入 `stderr`，格式为 `--format json|raw`。

## 跟踪

```bash
px trace list --limit 20 --format raw --no-progress | jq .
px trace list --last-n-minutes 60 --limit 20 --format raw --no-progress | jq '.[] | select(.status == "ERROR")'
px trace list --since 2025-01-15T00:00:00Z --limit 50 --format raw --no-progress | jq .
px trace list --since 2025-01-15T00:00:00Z --until 2025-01-16T00:00:00Z --limit 50 --format raw --no-progress | jq .  # 时间范围（until 是排他的）
px trace list --format raw --no-progress | jq 'sort_by(-.duration) | .[0:5]'
px trace list --include-notes --format raw --no-progress | jq '.[].notes'
px trace get <trace-id> --format raw | jq .
px trace get <trace-id> --format raw | jq '.spans[] | select(.status_code != "OK")'
px trace get <trace-id> --include-notes --format raw | jq '.notes'
px trace annotate <trace-id> --name reviewer --label pass
px trace annotate <trace-id> --name reviewer --score 0.9 --format raw --no-progress
px trace annotate <trace-id> --name reviewer --label pass --identifier "<coding-annotation-id>"  # 使用编码注释标识符标记
px trace add-note <trace-id> --text "needs follow-up"
px trace add-note <trace-id> --text "needs follow-up" --identifier "<coding-annotation-id>"  # 标记 + 在标识符上更新
px trace-annotations delete --identifier "<coding-annotation-id>" --all -y            # 删除与此编码注释标识符相关的所有注释
```

`px <实体>-annotations delete` 需要 `--all` 或同时提供 `--start-time` 和 `--end-time`，并在成功时发出 `{deleted: true, target, filter}`。

### 跟踪 JSON 结构

```
Trace
  traceId, status ("OK"|"ERROR"), duration (ms), startTime, endTime
  annotations[] (使用 --include-annotations，不包括备注)
    name, result { score, label, explanation }
  notes[] (使用 --include-notes)
    name="note", result { explanation }
  rootSpan  — 顶层 span (parent_id: null)
  spans[]
    name, span_kind ("LLM"|"CHAIN"|"TOOL"|"RETRIEVER"|"EMBEDDING"|"AGENT"|"RERANKER"|"GUARDRAIL"|"EVALUATOR"|"UNKNOWN")
    status_code ("OK"|"ERROR"|"UNSET"), parent_id, context.span_id
    notes[] (使用 --include-notes)
      name="note", result { explanation }
    attributes
      input.value, output.value          — 原始输入/输出
      llm.model_name, llm.provider
      llm.token_count.prompt/completion/total
      llm.token_count.prompt_details.cache_read
      llm.token_count.completion_details.reasoning
      llm.input_messages.{N}.message.role/content
      llm.output_messages.{N}.message.role/content
      llm.invocation_parameters          — JSON 字符串（温度等）
      exception.message                  — 如果 span 出错则设置
```

## Span

```bash
px span list --limit 20                                    # 最近 span（表格视图）
px span list --last-n-minutes 60 --limit 50                # 上一小时内的 span
px span list --since 2025-01-15T00:00:00Z --limit 50       # 自某个时间戳以来的 span
px span list --since 2025-01-15T00:00:00Z --until 2025-01-16T00:00:00Z --limit 50  # 时间范围（until 是排他的）
px span list --span-kind LLM --limit 10                    # 仅 LLM span
px span list --status-code ERROR --limit 20                # 仅出错 span
px span list --name chat_completion --limit 10             # 按 span 名称过滤
px span list --trace-id <id> --format raw --no-progress | jq .   # 某个跟踪的所有 span
px span list --span-id <id> <id> --format raw --no-progress | jq .  # 通过 ID 获取特定 span（服务器 >= 19.6.0）
px span list --parent-id null --limit 10                   # 仅根 span
px span list --parent-id <span-id> --limit 10              # 仅某个 span 的子 span
px span list --include-annotations --limit 10              # 包括注释分数
px span list --include-notes --limit 10                    # 包括 span 备注
px span list --attribute llm.model_name:gpt-4 --limit 10  # 按字符串属性过滤
px span list --attribute llm.token_count.total:500 --limit 10  # 按数值属性过滤
px span list --attribute 'user.id:"12345"' --limit 10     # 强制对看起来像数字的值进行字符串匹配
px span list --attribute session.id:sess:abc:123 --limit 20  # 值中包含冒号是允许的（仅按第一个冒号分割）
px span list --attribute llm.model_name:gpt-4 --attribute session.id:abc --limit 10  # 多个过滤器 AND
px span list output.json --limit 100                       # 保存到 JSON 文件
px span list --format raw --no-progress | jq '.[] | select(.status_code == "ERROR")'
px span annotate <span-id> --name reviewer --label pass
px span annotate <span-id> --name checker --score 1 --annotator-kind CODE
px span annotate <span-id> --name reviewer --label pass --identifier "<coding-annotation-id>"  # 使用编码注释标识符标记
px span add-note <span-id> --text "verified by agent"
px span add-note <span-id> --text "verified by agent" --identifier "<coding-annotation-id>"  # 标记 + 在标识符上更新
px span-annotations delete --identifier "<coding-annotation-id>" --all -y           # 删除与此编码注释标识符相关的所有注释
```

`span list` 按 ingestion（最新优先）排序，而不是 `start_time`；它们在到达较晚的 span（回填、重播）时分离。要按 `start_time` 排序（服务器 >= 20.16.0），请调用 REST 并在 `next_cursor` 页面保持 `sort`/`order` 固定：

```bash
curl -s -H "Authorization: Bearer $PHOENIX_API_KEY" \
  "$PHOENIX_ENDPOINT/v1/projects/my-project/spans?sort=start_time&order=desc&limit=20"
```

### Span JSON 结构

```
Span
  名称, span_kind ("LLM"|"CHAIN"|"TOOL"|"RETRIEVER"|"EMBEDDING"|"AGENT"|"RERANKER"|"GUARDRAIL"|"EVALUATOR"|"UNKNOWN")
  状态码 ("OK"|"ERROR"|"UNSET"), 状态消息
  上下文. span_id, 上下文.trace_id, 父span_id
  开始时间, 结束时间
  属性
    输入.value, 输出.value          — 原始输入/输出
    llm.model_name, llm.provider
    llm.token_count.prompt/completion/total
    llm.input_messages.{N}.message.role/content
    llm.output_messages.{N}.message.role/content
    llm.invocation_parameters          — JSON字符串（温度等参数）
    异常.message                  — 如果span出错则设置
  注释[] (使用--include-annotations, 排除note)
    名称, 结果 { 分数, 标签, 解释 }
  备注[] (使用--include-notes)
    名称="note", 结果 { 解释 }
```

## 会话

```bash
px 会话 列表 --limit 10 --format 原始 --无进度 | jq .
px 会话 列表 --order 升序 --format 原始 --无进度 | jq '.[].会话ID'
px 会话 列表 --包含注释 --包含备注 --format 原始 --无进度 | jq '.[].备注'
px 会话 获取 <会话ID> --format 原始 | jq .
px 会话 获取 <会话ID> --包含注释 --format 原始 | jq '.会话.注释'
px 会话 获取 <会话ID> --包含备注 --format 原始 | jq '.会话.备注'
px 会话 注释 <会话ID> --名称 审核者 --标签 通过
px 会话 注释 <会话ID> --名称 审核者 --分数 0.9 --format 原始 --无进度
px 会话 注释 <会话ID> --名称 审核者 --标签 通过 --标识符 "<编码注释ID>"  # 使用编码注释标识符标记
px 会话 添加备注 <会话ID> --文本 "由代理验证"
px 会话 添加备注 <会话ID> --文本 "由代理验证" --标识符 "<编码注释ID>"  # 标识符标记 + 插入
px 会话-注释 删除 --标识符 "<编码注释ID>" --全部 -y              # 删除与此编码注释标识符关联的所有注释
px 会话 删除 <会话ID> -y                                                        # 需要 PHOENIX_CLI_DANGEROUSLY_ENABLE_DELETES=true
```

`会话 列表` 没有过滤标志。要按形状选择会话（错误计数、token总数、工具使用、注释标签），请使用GraphQL的会话过滤表达式语言（见[会话过滤表达式](#会话过滤表达式)）。

### 会话 JSON 结构

```
会话数据
  ID, 会话ID, 项目ID
  开始时间, 结束时间
  token_count_prompt, token_count_completion, token_count_total  — 会话中所有LLM spans的累积值（int, 默认0）
  注释[] (使用--include-annotations, 排除note)
    名称, 结果 { 分数, 标签, 解释 }
  备注[] (使用--include-notes)
    名称="note", 结果 { 解释 }
  追踪[]
    ID, 追踪ID, 开始时间, 结束时间
```

## 数据集 / 实验 / 提示

```bash
px 数据集 列表 --format 原始 --无进度 | jq '.[].名称'
px 数据集 获取 <名称> --format 原始 | jq '.示例[] | {输入, 输出: .预期输出}'
px 数据集 获取 <名称> --分割 训练 --format 原始 | jq .    # 按分割过滤
px 数据集 获取 <名称> --版本 <版本ID> --format 原始 | jq .
px 实验 列表 --数据集 <名称> --format 原始 --无进度 | jq '.[] | {ID, 名称, 失败运行计数}'
px 实验 获取 <ID> --format 原始 --无进度 | jq '.[] | select(.错误 != null) | {输入, 错误}'
px 提示 列表 --format 原始 --无进度 | jq '.[].名称'
px 提示 获取 <名称> --format 文本 --无进度   # 纯文本，适合管道到AI
```

## 注释配置

完整CRUD：`列表`, `获取`, `创建`, `更新`, `删除`。类型是 `CATEGORICAL`（标签 + 可选分数）、`CONTINUOUS`（数值范围）、`FREEFORM`（自由文本）。

```bash
px 注释配置 列表                                                # 所有配置（表格视图）
px 注释配置 列表 --format 原始 --无进度 | jq -r '.[].名称' # 配置名称作为JSON
px 注释配置 获取 response-quality --format 原始 --无进度     # 按名称或ID获取一个配置

# 创建 — 分类（带分数的标签）、连续（数值范围）、自由文本（自由文本）
px 注释配置 创建 --类型 CATEGORICAL --名称 response-quality --值 good=1 --值 bad=0
px 注释配置 创建 --类型 CONTINUOUS --名称 confidence --下限 0 --上限 1
px 注释配置 创建 --类型 FREEFORM --名称 reviewer-notes --描述 '自由文本审核者反馈'

# 更新按名称或ID — 只更改传递的字段；类型不可变
px 注释配置 更新 response-quality --名称 answer-quality --优化方向 MAXIMIZE
px 注释配置 更新 response-quality --值 good=1 --值 acceptable=0.5 --值 bad=0
px 注释配置 更新 response-quality --描述 "更新" --format 原始 --无进度 | jq -r '.ID'

# 删除按ID — 需要 PHOENIX_CLI_DANGEROUSLY_ENABLE_DELETES=true; --yes 跳过提示
px 注释配置 删除 QW5ub3RhdGlvbkNvbmZpZzoxMjM= --yes
```

分类值在 `创建` 和 `更新` 中指定方式相同：重复 `--值 标签[=分数]`（分数可选），或单个 `--值 '<json>'` 负载 — 互斥。`更新` 获取现有配置，合并标志，并通过 `PUT /v1/annotation_configs/{id}` 写回完整正文；它至少需要一个字段标志。其他类型特定标志：`--下限`/`--上限`（CONTINUOUS/FREEFORM）、`--阈值`（FREEFORM）。无效输入（错误标志、类型不匹配、格式化值）退出 `3` (`INVALID_ARGUMENT`) 并在 `原始`/`JSON` 模式下在stderr输出 `{错误, code, 提示?}` JSON包。`获取`/`创建`/`更新` 输出配置对象（`原始`/`JSON` 中单个对象，不是数组）。

## GraphQL

用于上述命令未涵盖的临时查询。输出是 `{"data": {...}}`。

```bash
px api graphql '{ 项目计数 数据集计数 提示计数 评估器计数 }'
px api graphql '{ 项目 { 边缘 { 节点 { 名称 追踪计数 token计数Total } } } }' | jq '.数据.项目.边缘[].节点'
px api graphql '{ 数据集 { 边缘 { 节点 { 名称 示例计数 实验计数 } } } }' | jq '.数据.数据集.边缘[].节点'
px api graphql '{ 评估器 { 边缘 { 节点 { 名称 种类 } } } }' | jq '.数据.评估器.边缘[].节点'
# 评估器种类值: "LLM" | "代码" | "内置"
# 代码 = 在沙盒中运行的server端代码评估器；内置 = 预构建的server端评估器

# 任何类型的内省
px api graphql '{ __type(name: "Project") { 字段 { 名称 类型 { 名称 } } } }' | jq '.数据.__type.字段[]'
```

关键根字段：`项目`, `getProjectByName(name:)`, `数据集`, `提示`, `评估器`, `项目计数`, `数据集计数`, `提示计数`, `评估器计数`, `查看者`。

`getProjectByName(name:)` 针对一个项目；`projects(first: 1)` 选择任意一个。没有 `traces` 连接：要列出追踪，查询 `spans` 使用 `filterCondition: "parent_span is None"`，这保留根追踪，与UI的追踪表相同。见[过滤表达式](#过滤表达式)下文。

### 过滤表达式

`spans`, `会话` 和项目聚合接受过滤条件：服务器端编译的Python布尔表达式。有三种语言，参数选择语言。在编写条件前阅读 [参考资料/filter-expressions.md](参考资料/filter-expressions.md)；它包含完整词汇、运算符和每种语言的编译示例。

| 参数 | 匹配 | 名称来自 |
| ---- | ---- | -------- |
| `filterCondition` | 单个spans | 参考中的完整表格 |
| `traceFilterCondition` | 整个traces | `traceFilterVocabulary` |
| `sessionFilterCondition` | 会话 | `sessionFilterVocabulary` |

**根spans。** 没有 `traces` 连接和根-span参数。`filterCondition: "parent_span is None"` 保留根spans，包括孤儿spans（其父从未收到），这是UI的追踪表运行的；`parent_id is None` 只保留没有父ID的spans。根span通常每个追踪一个，并且与过滤的其余部分组合：

```bash
px api graphql '{
  getProjectByName(name: "default") { spans(
    first: 20
    filterCondition: "parent_id is None and status_code == \"ERROR\""
    排序: { 列: 开始时间, 方向: desc }
  ) { 边缘 { 节点 { spanId 名称 延迟Ms } } } }
}' | jq '.数据.getProjectByName.spans.边缘[].节点'
```

**注释。** 访问器选择级别，错误级别匹配无：

| 访问器 | 匹配spans上的注释 | 由...编写 |
| ------ | ----------------- | -------- |
| `annotations["name"]` | span本身 | `px span 注释`, `px span 添加备注` |
| `trace_annotations["name"]` | span的父追踪 | `px trace 注释`, `px trace 添加备注` |
| `session_annotations["name"]` | 会话（仅会话过滤） | `px session 注释`, `px session 添加备注` |

```bash
px api graphql '{
  getProjectByName(name: "default") { spans(
    first: 20
    filterCondition: "parent_id is None and trace_annotations[\"quality\"].label == \"差\""
  ) { 边缘 { 节点 { spanId 名称 } } } }
}' | jq '.数据.getProjectByName.spans.边缘[].节点'
```

**追踪。** `traceFilterCondition` 保留匹配的追踪的spans，并与 `filterCondition` 组合：

```bash
px api graphql '{
  getProjectByName(name: "default") { spans(
    first: 20
    filterCondition: "parent_id is None"
    traceFilterCondition: "错误计数 > 0 and 延迟_ms > 1000"
  ) { 边缘 { 节点 { spanId 名称 延迟Ms } } } }
}' | jq '.数据.getProjectByName.spans.边缘[].节点'
```

**会话。** `px 会话 列表` 没有过滤标志，因此按形状选择会话通过GraphQL：

```bash
px api graphql '{
  项目(first: 1) { 边缘 { 节点 { 会话(
    first: 10
    会话过滤条件: "num_traces > 5 and any(span.status_code == \"ERROR\" for span in spans)"
  ) { 边缘 { 节点 { 会话ID numTraces numTracesWithError } } } } } }
}' | jq '.数据.项目.边缘[0].节点.会话.边缘[].节点'
```

**发现名称并验证。** 词汇表由编译器的绑定生成，因此它们始终与编译匹配：

```bash
px api graphql '{ 项目(first: 1) { 边缘 { 节点 { traceFilterVocabulary {
  名称 类型 类别 描述 迭代名称 } } } } }' \
  | jq '.数据.项目.边缘[0].节点.traceFilterVocabulary[] | {名称, 类型, 类别}'

px api graphql '{ 项目(first: 1) { 边缘 { 节点 {
  验证Span过滤条件(condition: "parent_id is None") { 是否有效 错误消息 }
  验证Trace过滤条件(condition: "错误计数 > 0") { 是否有效 错误消息 }
  验证会话过滤条件(condition: "num_traces > 5") { 是否有效 错误消息 }
} } } }'
```

接受两个级别的字段（例如 `Project.recordCount`），`sessionFilterCondition` 和 `filterCondition` 互斥。

## 文档

下载Phoenix文档markdown供本地使用，由编码代理使用。

```bash
px 文档 获取                                # 获取默认工作流文档到 .px/docs
px 文档 获取 --工作流 追踪             # 仅获取追踪文档
px 文档 获取 --工作流 追踪 --工作流 评估
px 文档 获取 --干运行                      # 预览将要下载的内容
px 文档 获取 --刷新                      # 清除 .px/docs 并重新下载
px 文档 获取 --输出目录 ./my-docs         # 自定义输出目录
```

关键选项：`--工作流`（可重复，值: `追踪`, `评估`, `数据集`, `提示`, `集成`, `SDK`, `自托管`, `全部`）、`--干运行`, `--刷新`, `--输出目录`（默认 `.px/docs`）、`--workers`（默认10）。
