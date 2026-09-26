# Phoenix CLI

## 调用方式

```bash
px <资源> <操作>                          # 如果全局安装
npx @arizeai/phoenix-cli <资源> <操作>    # 无需安装
```

CLI 使用单数资源命令和子命令，如 `list` 和 `get`：

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

上述每个 `delete` 命令都需要环境变量 `PHOENIX_CLI_DANGEROUSLY_ENABLE_DELETES=true`，并且除非使用 `-y`/`--yes` 参数，否则会提示确认。`px profile delete` 仅在本地执行，并且不需要环境变量的限制。如果没有设置环境变量，命令将不会删除任何内容。

## 设置

```bash
export PHOENIX_ENDPOINT=http://localhost:6006
export PHOENIX_PROJECT=my-project
export PHOENIX_API_KEY=your-api-key  # 如果启用了认证
```

`PHOENIX_ENDPOINT` 是 API 访问的基础 URL。它通常包含与 `PHOENIX_COLLECTOR_ENDPOINT` 相同的 URL；当仅设置收集器变量时，CLI 也会使用它进行 API 访问。

对于交互式本地使用，`px auth login` 会将 OAuth 会话存储在选定的配置文件中；该会话以登录用户的权限执行。当同时配置 API 密钥和 OAuth 令牌时，API 密钥优先级高于 OAuth 令牌。OAuth 访问令牌会自动刷新 REST、GraphQL 和 PXI 请求，并且旋转的令牌会持久化到选定的配置文件中。

在将内容管道传输到 `jq` 时，始终使用 `--format raw --no-progress`。

### `px setup` — 新手引导

`px setup` 将当前目录中的应用程序连接到 Phoenix 部署，并写入 `.env.phoenix`（模式 0600，git 忽略）。交互式流程适用于人类——它会提示、启动编码代理，并轮询跟踪。**从代理运行时，始终传递 `--no-input`：**

```bash
# 仅注册：连接 + .env.phoenix，不更改源代码。
px setup --no-input --endpoint http://localhost:6006 --project my-app --format raw
```

无头模式需要一个干净的 git 仓库，并且默认情况下在写入文件后停止——它不会更改源代码，除非您要求。如果启用了认证，还需要设置 `PHOENIX_API_KEY`。项目不需要存在——Phoenix 在第一次跟踪时创建它。缺少输入会以 `3` 退出，并带有精确的纠正措施；取消会以 `2` 退出。

要同时监控应用程序，请命名通道——无头模式没有提示选择通道的选项，因此 `--instrument` 需要 `--agent`：

```bash
px setup --no-input --instrument --agent claude --yolo --format raw
```

`--yolo` 很重要：后台代理没有终端来批准其编辑，因此如果没有它，运行将一直停滞，直到跟踪验证超时。`--language python` 会跳过代理的语言检测。`--docs-mcp` 将 Phoenix 文档 MCP 服务器连接到交接代理（`claude mcp add` 用于 claude，配置文件合并用于 cursor/opencode；codex 不支持）并跳过 `.px/docs` 下载——代理按需搜索文档；任何失败都会回退到下载。`--no-docs-mcp` 会抑制交互式提议。`--format raw` 会打印
`{"endpoint","project","files","instrumentation","tracesVerified","tracesUrl"}`
——检查 `tracesVerified`，它只有在 API 确认跟踪到达时才会设置，而不是当代理声称它完成时。

一个运行在没有任何跟踪的情况下超时退出 `6`，而不是 `0`：配置和编辑是真实的，但跟踪没有确认工作正常。将其视为报告失败，而不是成功——并且不要用交接代理自己的退出代码或摘要来代替裁决。没有 `--instrument` 的注册，并且在超时提示时人类回答“稍后验证”，都会退出 `0`。

对于仅注册的运行，`tracesVerified` 也是 `false`，因此它无法区分“无内容验证”和“未到达跟踪”。当您需要区分时，请读取 `verification`
(`verified` / `notVerified` / `deferred`，当没有要验证的内容时不存在)。

可重新运行的切片，因此已注册的仓库会跳过问题：

```bash
px setup instrument --agent claude   # 仅监控 + 验证
px setup skills                      # 安装 Phoenix 编码代理技能
```

### `px setup mcp` — 注册远程 MCP 服务器

将 Phoenix 远程 MCP 服务器 (`<endpoint>/mcp`) 连接到编码代理，以便它可以查询 Phoenix 数据。端点从 `--endpoint`、活动配置文件或 `PHOENIX_ENDPOINT` 推断。只有范围的命令提示（全局默认）然后代理；`--agent` 会跳过两个提示。

```bash
px setup mcp --agent codex --no-input --format raw
px setup mcp --agent claude --local            # 写入此仓库的 .mcp.json
```

代理：`claude`、`codex`、`gemini`、`cursor`、`opencode`、`vscode`。范围是 `--global`（默认）或 `--local`（仓库；Codex 仅全局）。认证默认为 OAuth（URL 配置，首次使用时浏览器登录）；传递 `--header "Name: value"`（可重复）以进行 API 密钥的 bearer 降级——对于 Codex，`Authorization: Bearer ${VAR}` 头会变成 `bearer_token_env_var`。`--format raw` 会打印 `{"endpoint","url","serverName","agent","scope","auth","file?"}`。

## 认证

```bash
px auth login                                 # 基于浏览器的 OAuth 登录
px auth login --no-browser                    # 打印用于 SSH/无头使用的 URL
px auth logout                                # 清除 OAuth 令牌；保留 API 密钥
px auth status                                # 检查连接和认证状态
px auth status --endpoint http://other:6006   # 检查特定端点
px auth status --profile staging              # 检查命名配置文件的连接
px auth status --format raw                   # 机器可读的凭证源
```

`auth status` 报告凭证源 (`flag`、`env`、`profile-key`、`oauth` 或 `none`)。OAuth 状态包括令牌过期时间。

当存储的凭证源是 `oauth` 并且认证探测失败时，`auth status` 会无凭证重试一次，并且仅报告服务器明确说明可以匿名访问的情况。这可以防止陈旧或过期的配置文件令牌被报告为对已从 OAuth 切换到匿名访问的部署的认证失败。

## 配置文件

命名配置文件允许您在多个 Phoenix 实例（本地、暂存、云）之间切换，而无需管理环境变量。配置文件存储在 `~/.px/settings.json`（或 `$XDG_CONFIG_HOME/px/settings.json`）。

配置优先级（从高到低）：CLI 标志 > 环境变量 > 活动配置文件 > 最接近的 `.env.phoenix` 文件 > 内置默认值。

CLI 还会发现当前工作目录或其上级最近的 `.env.phoenix` 文件（`px setup` 写入的相同文件）。凭证作为一组解析，因此进程 API 密钥永远不会与文件提供的头组合。设置 `PHOENIX_DISCOVER_CONFIG=false` 以禁用发现。

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

在任何命令上使用 `--profile <name>` 以针对特定配置文件，而不会更改活动配置文件：

```bash
px trace list --profile staging --limit 10 --format raw --no-progress | jq .
px auth status --profile prod
```

`px profile create` 选项：`--endpoint <url>`、`--project <name>`、`--api-key <key>`、`--header <key=value>`（可重复），`--activate`。

## 项目

```bash
px project list                                            # 列出所有项目（表格视图）
px project list --format raw --no-progress | jq '.[].name' # 项目名称作为 JSON
px project list --name-contains prod                       # 通过名称子字符串过滤（不区分大小写）
px project get my-project --format raw --no-progress       # 通过确切名称获取单个记录
px project get my-project --format raw --no-progress | jq -r '.id'  # 提取项目 ID
```

`project list` 接受 `--limit <n>`（每页获取的项目数量）和 `--name-contains <filter>`，后者在服务器端按不区分大小写的名称子字符串进行过滤。当您只知道项目名称的一部分时，请使用它而不是将 `list` 管道传输到 `grep`。

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
px trace add-note <trace-id> --text "需要跟进"
px trace add-note <trace-id> --text "需要跟进" --identifier "<coding-annotation-id>"  # 标记 + 在标识符上插入
px trace-annotations delete --identifier "<coding-annotation-id>" --all -y            # 删除与此编码注释标识符关联的所有注释
```

`px <实体>-annotations delete` 需要 `--all` 或 `--start-time` 和 `--end-time` 都存在，并在成功时发出 `{deleted: true, target, filter}`。

### 跟踪 JSON 结构

```
Trace
  traceId, status ("OK"|"ERROR"), duration (ms), startTime, endTime
  annotations[] (使用 --include-annotations，不包括注释)
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
px span list --last-n-minutes 60 --limit 50                # 上小时的 span
px span list --since 2025-01-15T00:00:00Z --limit 50       # 自某个时间戳以来的 span
px span list --since 2025-01-15T00:00:00Z --until 2025-01-16T00:00:00Z --limit 50  # 时间范围（until 是排他的）
px span list --span-kind LLM --limit 10                    # 仅 LLM span
px span list --status-code ERROR --limit 20                # 仅出错 span
px span list --name chat_completion --limit 10             # 通过 span 名称过滤
px span list --trace-id <id> --format raw --no-progress | jq .   # 所有与跟踪相关的 span
px span list --span-id <id> <id> --format raw --no-progress | jq .  # 通过 ID 获取特定 span（服务器 >= 19.6.0）
px span list --parent-id null --limit 10                   # 仅根 span
px span list --parent-id <span-id> --limit 10              # 仅 span 的子 span
px span list --include-annotations --limit 10              # 包括注释分数
px span list --include-notes --limit 10                    # 包括 span 注释
px span list --attribute llm.model_name:gpt-4 --limit 10  # 通过字符串属性过滤
px span list --attribute llm.token_count.total:500 --limit 10  # 通过数值属性过滤
px span list --attribute 'user.id:"12345"' --limit 10     # 强制对看起来像数值的值进行字符串匹配
px span list --attribute llm.model_name:gpt-4 --attribute session.id:abc --limit 10  # 多个过滤器 AND
px span list output.json --limit 100                       # 保存到 JSON 文件
px span list --format raw --no-progress | jq '.[] | select(.status_code == "ERROR")'
px span annotate <span-id> --name reviewer --label pass
px span annotate <span-id> --name checker --score 1 --annotator-kind CODE
px span annotate <span-id> --name reviewer --label pass --identifier "<coding-annotation-id>"  # 使用编码注释标识符标记
px span add-note <span-id> --text "由代理验证"
px span add-note <span-id> --text "由代理验证" --identifier "<coding-annotation-id>"  # 标记 + 在标识符上插入
px span-annotations delete --identifier "<coding-annotation-id>" --all -y           # 删除与此编码注释标识符关联的所有注释
```

### Span JSON 结构

```
Span
  name, span_kind ("LLM"|"CHAIN"|"TOOL"|"RETRIEVER"|"EMBEDDING"|"AGENT"|"RERANKER"|"GUARDRAIL"|"EVALUATOR"|"UNKNOWN")
  status_code ("OK"|"ERROR"|"UNSET"), status_message
  context.span_id, context.trace_id, parent_id
  start_time, end_time
  attributes
    input.value, output.value          — 原始输入/输出
    llm.model_name, llm.provider
    llm.token_count.prompt/completion/total
    llm.input_messages.{N}.message.role/content
    llm.output_messages.{N}.message.role/content
    llm.invocation_parameters          — JSON 字符串（温度等）
    exception.message                  — 如果 span 出错则设置
  annotations[] (使用 --include-annotations，不包括注释)
    name, result { score, label, explanation }
  notes[] (使用 --include-notes)
    name="note", result { explanation }
```

## Session

```bash
px session list --limit 10 --format raw --no-progress | jq .
px session list --order asc --format raw --no-progress | jq '.[].session_id'
px session list --include-annotations --include-notes --format raw --no-progress | jq '.[].notes'
px session get <session-id> --format raw | jq .
px session get <session-id> --include-annotations --format raw | jq '.session.annotations'
px session get <session-id> --include-notes --format raw | jq '.session.notes'
px session annotate <session-id> --name reviewer --label pass
px session annotate <session-id> --name reviewer --score 0.9 --format raw --no-progress
px session annotate <session-id> --name reviewer --label pass --identifier "<coding-annotation-id>"  # 使用编码注释标识符标记
px session add-note <session-id> --text "由代理验证"
px session add-note <session-id> --text "由代理验证" --identifier "<coding-annotation-id>"  # 标记 + 在标识符上插入
px session-annotations delete --identifier "<coding-annotation-id>" --all -y              # 删除与此编码注释标识符关联的所有注释
px session delete <session-id> -y                                                        # 需要 PHOENIX_CLI_DANGEROUSLY_ENABLE_DELETES=true
```

`session list` 没有过滤器标志。要按形状选择会话（错误计数、token 总数、工具使用、注释标签），请使用 GraphQL 中的会话过滤器表达式语言（见 [Session filter expressions](#session-filter-expressions)）。

### Session JSON 结构

```
SessionData
  id, session_id, project_id
  start_time, end_time
  token_count_prompt, token_count_completion, token_count_total  — 在会话中所有 LLM span 的累积值（int，默认 0）
  annotations[] (使用 --include-annotations，不包括注释)
    name, result { score, label, explanation }
  notes[] (使用 --include-notes)
    name="note", result { explanation }
  traces[]
    id, trace_id, start_time, end_time
```

## 数据集 / 实验 / 提示

```bash
px dataset list --format raw --no-progress | jq '.[].name'
px dataset get <name> --format raw | jq '.examples[] | {input, output: .expected_output}'
px dataset get <name> --split train --format raw | jq .    # 通过 split 过滤
px dataset get <name> --version <version-id> --format raw | jq .
px experiment list --dataset <name> --format raw --no-progress | jq '.[] | {id, name, failed_run_count}'
px experiment get <id> --format raw --no-progress | jq '.[] | select(.error != null) | {input, error}'
px prompt list --format raw --no-progress | jq '.[].name'
px prompt get <name> --format text --no-progress   # 纯文本，理想情况下用于将内容传输到 AI
```

## 注释配置

完整的 CRUD：`list`、`get`、`create`、`update`、`delete`。类型是 `CATEGORICAL`（标签 + 可选分数）、`CONTINUOUS`（数值范围）、`FREEFORM`（自由文本）。

```bash
px annotation-config list                                                # 所有配置（表格视图）
px annotation-config list --format raw --no-progress | jq -r '.[].name' # 配置名称作为 JSON
px annotation-config get response-quality --format raw --no-progress     # 通过名称或 ID 获取单个配置

# create — 分类（带分数的标签）、连续（数值范围）或自由形式（自由文本）
px annotation-config create --type CATEGORICAL --name response-quality --value good=1 --value bad=0
px annotation-config create --type CONTINUOUS --name confidence --lower-bound 0 --upper-bound 1
px annotation-config create --type FREEFORM --name reviewer-notes --description '自由形式的评论者反馈'

# update by name or ID — 仅更改您传递的字段；类型不可变
px annotation-config update response-quality --name answer-quality --optimization-direction MAXIMIZE
px annotation-config update response-quality --value good=1 --value acceptable=0.5 --value bad=0
px annotation-config update response-quality --description "更新" --format raw --no-progress | jq -r '.id'

# delete by ID — 需要 PHOENIX_CLI_DANGEROUSLY_ENABLE_DELETES=true；--yes 跳过提示
px annotation-config delete QW5ub3RhdGlvbkNvbmZpZzoxMjM= --yes
```

分类值在 `create` 和 `update` 中指定方式相同：可重复 `--value label[=score]`（分数可选），或单个 `--values '<json>'` 有效负载——互斥。`update` 会获取现有配置，合并您的标志，并通过 `PUT /v1/annotation_configs/{id}` 将完整正文写回；它至少需要一个字段标志。其他类型特定标志：`--lower-bound`/`--upper-bound`（CONTINUOUS/FREEFORM），`--threshold`（FREEFORM）。无效输入（错误的标志、类型不匹配、格式化的值）会以 `3` (`INVALID_ARGUMENT`) 退出，并在 `raw`/`json` 模式下在 `stderr` 输出 `{error, code, hint?}` JSON 封装。`get`/`create`/`update` 输出配置对象（`raw`/`json` 中的单个对象，不是数组）。

## GraphQL

用于上述命令未涵盖的临时查询。输出是 `{"data": {...}}`。

```bash
px api graphql '{ projectCount datasetCount promptCount evaluatorCount }'
px api graphql '{ projects { edges { node { name traceCount tokenCountTotal } } }' | jq '.data.projects.edges[].node'
px api graphql '{ datasets { edges { node { name exampleCount experimentCount } } }' | jq '.data.datasets.edges[].node'
px api graphql '{ evaluators { edges { node { name kind } } }' | jq '.data.evaluators.edges[].node'
# evaluator kind 值： "LLM" | "CODE" | "BUILTIN"
# CODE = 在沙盒中运行的服务器端代码评估器；BUILTIN = 预构建的服务器评估器

# 任何类型的内省
px api graphql '{ __type(name: "Project") { fields { name type { name } } }' | jq '.data.__type.fields[]'
```

关键根字段：`projects`, `getProjectByName(name:)`, `datasets`, `prompts`, `evaluators`, `projectCount`, `datasetCount`, `promptCount`, `evaluatorCount`, `viewer`.

`getProjectByName(name:)` 针对一个项目；`projects(first: 1)` 随机选择一个。没有 `traces` 连接：要列出跟踪，请查询 `spans` 并使用 `filterCondition: "parent_span is None"`，这与 UI 的跟踪表格一样，保留根 span，因为 UI 的跟踪表格会这样做。见 [Filter expressions](#filter-expressions) 下方。

### 过滤表达式

`spans`, `sessions`, 和项目聚合接受过滤条件：Python 布尔表达式在服务器端编译。有三个语言，并且参数选择语言。在编写条件之前阅读
[references/filter-expressions.md](references/filter-expressions.md)；它包含完整的词汇、运算符和每个编译示例。

| 参数 | 匹配 | 名称来自 |
| ------ | ------- | --------------- |
| `filterCondition` | 单个 span | 参考中的排他性表格 |
| `traceFilterCondition` | 整个 traces | `traceFilterVocabulary` |
| `sessionFilterCondition` | 会话 | `sessionFilterVocabulary` |

**根 span.** 没有 `traces` 连接和根-span 参数。`filterCondition: "parent_span is None"` 保留根 span，包括其父 span 从未接收的孤儿，并且是 UI 的跟踪表格运行的；`parent_id is None` 仅保留没有父 id 的 span。根 span 通常每个跟踪一个，并且无论使用哪个子句，都可以与其他过滤器组合：

```bash
px api graphql '{
  getProjectByName(name: "default") { spans(
    first: 20
    filterCondition: "parent_id is None and status_code == \"ERROR\""
    sort: { col: startTime, dir: desc }
  ) { edges { node { spanId name latencyMs } } }
}' | jq '.data.getProjectByName.spans.edges[].node'
```

**注释.** 访问器选择级别，并且错误的级别匹配为空：

| 访问器 | 匹配 span 自身的注释 | 由 `px span annotate`, `px span add-note` 编写 |
| -------- | ---------------------- | ------------------------------------------ |
| `annotations["name"]` | span 本身 | `px span annotate`, `px span add-note` |
| `trace_annotations["name"]` | span 的父跟踪 | `px trace annotate`, `px trace add-note` |
| `session_annotations["name"]` | 会话（仅会话过滤器） | `px session annotate`, `px session add-note` |

```bash
px api graphql '{
  getProjectByName(name: "default") { spans(
    first: 20
    filterCondition: "parent_id is None and trace_annotations[\"quality\"].label == \"poor\""
  ) { edges { node { spanId name } } }
}' | jq '.data.getProjectByName.spans.edges[].node'
```

**Traces.** `traceFilterCondition` 保留匹配跟踪的 span，并与其他 `filterCondition` 组合：

```bash
px api graphql '{
  getProjectByName(name: "default") { spans(
    first: 20
    filterCondition: "parent_id is None"
    traceFilterCondition: "error_count > 1 and latency_ms > 1000"
  ) { edges { node { spanId name latencyMs } } }
}' | jq '.data.getProjectByName.spans.edges[].node'
```

**会话.** `px session list` 没有过滤器标志，因此按形状选择会话（错误计数、token 总数、工具使用、注释标签）会通过 GraphQL 进行：

```bash
px api graphql '{
  projects(first: 1) { edges { node { sessions(
    first: 10
    sessionFilterCondition: "num_traces > 5 and any(span.status_code == \"ERROR\" for span in spans)"
  ) { edges { node { sessionId numTraces numTracesWithError } } } }
}' | jq '.data.projects.edges[0].node.sessions.edges[].node'
```

**发现名称并验证.** 词汇表是根据编译器自己的绑定生成的，因此它们始终与编译匹配：

```bash
px api graphql '{ projects(first: 1) { edges { node { traceFilterVocabulary {
  name type category description iterableName } } }' \
  | jq '.data.projects.edges[0].node.traceFilterVocabulary[] | {name, type, category}'

px api graphql '{ projects(first: 2) { edges { node {
  validateSpanFilterCondition(condition: "parent_id is None") { isValid errorMessage }
  validateTraceFilterCondition(condition: "error_count > 1") { isValid errorMessage }
  validateSessionFilterCondition(condition: "num_traces > 5") { isValid errorMessage }
} } }'
```

在字段接受两个级别的值（例如 `Project.recordCount`）时，`sessionFilterCondition` 和 `filterCondition` 互斥。
