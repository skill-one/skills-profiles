---
name: k6-manage
description: 与 Grafana Cloud k6 (GCk6) 交互——管理负载测试、测试运行、脚本、项目、计划、环境变量、获取指标或日志，并在本地运行脚本——使用 `gcx` 命令行界面（或当 `gcx` 不可用时使用直接 curl）。每当用户提及 k6 云测试或运行、要求列出/编辑/创建/启动/中止 k6 负载测试、需要获取测试运行的日志或指标、管理 k6 项目限制或计划、在本地或通过 `k6 cloud run` 运行 k6 脚本，或需要针对 Grafana Cloud 堆栈调用任何 `/cloud/v6/`、`/cloud/v5/` 或 k6-app Loki 端点时，均应触发此技能。即使用户未明确提及“gcx”或“API”，如“我的 k6 测试为何失败”、“显示运行 X 的日志”、“提升项目 Y 的 VUh 限制”或“更新我的 k6 脚本”等表述也均适用。
---

# Grafana Cloud k6 — 交互参考

默认路径是 `gcx` 命令行工具。当未安装 gcx 时，这里提到的每个端点都可以通过直接 curl 对 k6 的公共主机进行访问——参见 §1.2 获取认证头和主机转换规则。其余部分由以下两个原则构成：

- **gcx 负责 Grafana 端的认证（当存在时）。** 它在每个调用中注入正确的头信息，因此您不应自行设置认证头。您唯一需要手动设置的头是 `X-K6TestRun-Id`，在 Loki 日志查询（§4）、浏览器截图/文件获取（§6）和 Tempo 追踪查询（§7）中——任何其他内容都会被覆盖或导致冲突。在 curl 模式下，认证头是手动设置的；参见 §1.2。
- **优先使用 `gcx k6 ...` 子命令。** 它们封装了常见路径，提供了更友好的易用性并处理分页。使用 `gcx help-tree k6`（进一步使用 `gcx help-tree k6 <subcommand>` 深入探索）来发现可用内容；仅在不存在适用于您需求的子命令时才回退到 `gcx api`。

---

## 1. 认证

### 1.1 使用 gcx（默认）

```bash
gcx login --context <ctx>                # 一次性 OAuth，浏览器流程
gcx --context <ctx> config check         # 预期 "✔ Connectivity: online"
```

一旦上下文登录，每个 `gcx api ...` 和 `gcx k6 ...` 调用都会继承其认证状态。如果调用返回 *"Invalid or expired token — run gcx login to refresh"*，则 OAuth 会话已过期——重新运行 `gcx login --context <ctx>`。

### 1.2 不使用 gcx — 直接 curl

首先检查 `command -v gcx`。如果它不存在，此技能中的每个端点仍然可以直接针对 k6 的公共主机进行访问——与 gcx 示例相比有三个变化：

- **认证头是手动设置的。** 在每个调用中设置两者：
  - `Authorization: Bearer <k6_token>`
  - `X-Stack-ID: <int>`
- **主机替换插件代理。**
  - REST (`/cloud/v6/...`, `/cloud/v5/...`, `/cloud-resources/v1/...`, `/insights/...`) → `https://api.k6.io`
  - 日志（Loki）和追踪（Tempo）→ `https://cloudlogs.k6.io`
- **没有 `/api/plugins/k6-app/resources/{cloud,logs,insights}` 前缀。** 删除它；gcx 示例中该前缀之后的所有内容都是真实的 k6 路径。§2 中的 `cloud/cloud/` 重复怪癖会合并为单个 `/cloud/`——第一个只是代理路由。

#### 获取凭证

不要猜测这些——每次会话一次提示用户获取：

1. **k6 API 令牌** — 长效的 bearer；当 gcx 配置时，`gcx k6 auth token` 会打印相同的值。
2. **Stack** — 要么是整数 **stack ID**（直接用于 `X-Stack-ID`），要么是 Grafana **stack URL**（例如 `https://myorg.grafana.net`）。如果用户提供 URL，使用 `GET /cloud/v6/auth` 一次解析为 ID，该 URL 在 `X-Stack-Url` 头中传递，并返回 `{stack_id, default_project_id}`：

   ```bash
   STACK_ID=$(curl -sS https://api.k6.io/cloud/v6/auth \
     -H "Authorization: Bearer $K6_TOKEN" \
     -H "X-Stack-Url: $STACK_URL" \
     | jq -r '.stack_id')
   ```

   为会话缓存解析的 ID——后续每个调用都需要它在 `X-Stack-ID` 中。 (注意：`/cloud/v6/auth` 是唯一接受 `X-Stack-Url` 而不是 `X-Stack-ID` 的端点——这是从“用户已知 URL”到“API 需要的 ID”的桥梁。)

#### 翻译速查表

| gcx 形式（插件代理）                                                                  | curl 形式（直接）                                                       |
|------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| `gcx api /api/plugins/k6-app/resources/cloud/cloud/v6/test_runs/123`                     | `curl https://api.k6.io/cloud/v6/test_runs/123 -H ...`                   |
| `gcx api /api/plugins/k6-app/resources/cloud/cloud/v5/test_runs/<id>/metrics`            | `curl https://api.k6.io/cloud/v5/test_runs/<id>/metrics -H ...`          |
| `gcx api /api/plugins/k6-app/resources/cloud/cloud-resources/v1/files/index`             | `curl https://api.k6.io/cloud-resources/v1/files/index -H ...`           |
| `gcx api /api/plugins/k6-app/resources/insights/insights/api/v1/testrun/<id>/executions` | `curl https://api.k6.io/insights/api/v1/testrun/<id>/executions -H ...`  |
| `gcx api /api/plugins/k6-app/resources/logs/api/v1/query_range?...`                      | `curl https://cloudlogs.k6.io/api/v1/query_range?... -H ...`             |
| `gcx api /api/plugins/k6-app/resources/logs/api/v1/tempo/api/search?...`                 | `curl https://cloudlogs.k6.io/api/v1/tempo/api/search?... -H ...`        |

在上述每个 `-H ...` 插槽中，发送认证头：
`-H "Authorization: Bearer $K6_TOKEN" -H "X-Stack-ID: $STACK_ID"`。

注意：
- gcx 留给你特定端点的头——日志、追踪和文件端点（§4、§6、§7）上的 `X-K6TestRun-Id`——仍然需要额外设置认证对。
- §2 中的 `gcx api` 标志怪癖（溢出封装、`--json field` 过滤、`-o` 用于输出格式）不适用于 curl。使用普通的 curl 标志：`-o file` 保存正文，`--data-binary @file` 用于 PUT 负载，`-w '%{http_code}'` 用于状态码等。
- 分页语义（`$orderby`、`$top`、`$skip`、`@nextLink` 来自 §3）是 v6 端点的属性，在 curl 上工作方式相同。服务器返回的 `@nextLink` URL 已经是绝对 `https://api.k6.io/...` URL——直接将其传递回 curl；不需要 §3 中的插件代理重塑。

---

## 2. `gcx api` 路径的构成方式

当不存在子命令时，回退到 `gcx api` 对 Grafana 插件代理路由进行访问：

- **REST API** (`/cloud/v6/`, `/cloud/v5/`) — 前缀为 `/api/plugins/k6-app/resources/cloud/<k6-path>`。
- **日志（Loki）** — 前缀为 `/api/plugins/k6-app/resources/logs/<loki-path>`。

| k6 路径                                   | gcx 调用                                                                    |
|-------------------------------------------|-----------------------------------------------------------------------------------|
| `/cloud/v6/test_runs/{id}`                | `gcx api /api/plugins/k6-app/resources/cloud/cloud/v6/test_runs/{id}`             |
| `/cloud/v5/test_runs/{id}/metrics`        | `gcx api /api/plugins/k6-app/resources/cloud/cloud/v5/test_runs/{id}/metrics`     |
| Loki `/api/v1/query_range?...`            | `gcx api /api/plugins/k6-app/resources/logs/api/v1/query_range?...`               |

注意每个 REST 路径中的 `cloud/cloud/` 重复——第一个 `cloud` 是代理路由，第二个是 k6 的 `/cloud/v{N}/` 命名空间。

### `gcx api` 标志怪癖

`gcx api` 不是 curl 的克隆——几个标志与 curl 的肌肉记忆不同：

- **响应正文** 写入标准输出。没有 `-o <file>` 标志保存正文；`-o` 选择输出格式（`json`、`yaml`、`agents`）。使用 shell 重定向（`> file`）或 `$(...)` 捕获代替。
- **请求正文** 使用 `-d <string>`、`-d @file` 或 `-d @-`（标准输入）。没有 `--data-binary`；`-d @file` 已经保留字节。
- **没有 jq 的字段选择**：`--json field1,field2,...` 只返回列出的字段，`--json list`（或 `--json '?'`）发现可用内容。对于浅层提取，通常比将内容管道到 jq 更干净。
- **标准错误噪音**：gcx 在大多数调用中向标准错误打印一行 `hint:`。将内容管道到 `jq` 应该使用 `2>/dev/null` 重定向以避免意外。
- **响应头** 不直接由 `gcx api` 暴露。当工作流中的某个分支取决于 `Content-Type`（例如 §5 中的脚本 GET）时，使用 `file <path>` 检查下载的正文。
- **大响应溢出到临时文件**，标准输出减少为包装封装。阈值是几十 KB，因此即使是中等大小的列表端点也会触发它。封装如下所示：
  ```json
  {"spilled_to":"/var/folders/.../gcx-results-<n>.json",
   "bytes":2365037,
   "preview_sample":["@nextLink","value"],
   "message":"Response too large for stdout..."}
  ```
  在此情况下，`json.loads(stdout).get('value', [])` 模式会静默返回空值——封装没有 `value` 键。两个可靠的修复方法：
  - **传递 `-o json`** 强制内联输出，无论大小如何（推荐用于解析正文的脚本）。代理模式的默认格式会触发溢出；`-o json` 会禁用它。
  - **或者检测封装并重新从溢出文件读取**：
    ```python
    d = json.loads(stdout)
    if 'spilled_to' in d:
        d = json.load(open(d['spilled_to']))
    ```
  两者都有效；`-o json` 更简洁。

- **Grafana 插件代理将 `Content-Type: multipart/...` 重写为 `application/json`。** `gcx api` 本身会正确转发您的 `-H "Content-Type: ..."` 标志（在 `--log-http-payload` 跟踪中可见），但上游插件代理在它们到达 k6 的 API 之前会将多部分内容类型重写为 JSON。净效果：需要多部分正文的端点——尤其是 `POST /cloud/v6/projects/{id}/load_tests` 用于测试创建，它接受 `name` + `script` 作为表单部分——无论您在 gcx 端设置了什么头，都会返回 `HTTP 415 "Unsupported media type \"application/json\""`。对于这些端点，回退到直接 curl 对 `api.k6.io`（§1.2）——`curl -F name=... -F script=@...` 为您构建多部分正文并绕过插件代理。其他内容类型值（例如 `application/octet-stream` 用于 §5 中的脚本更新 PUT）会通过代理未更改。

---

## 3. 发现和调用端点

`gcx k6` 子命令（参见 `gcx help-tree k6`）涵盖了常见的读取操作。对于其他内容——变更、特殊读取、未作为子命令显示的端点——k6 Cloud API 表面很大且会随时间变化。与其依赖会过时的速查表，不如在请求时从 OpenAPI 规范中发现您需要的操作。

### 工作流程

1. **每次会话获取一次规范**（它很大；缓存到 `/tmp`）：

   ```bash
   gcx api /api/plugins/k6-app/resources/cloud/cloud/v6/openapi > /tmp/k6-openapi.json
   ```

2. **首先按 `operationId` + `description` 索引**——这会在您搜索时保持工作负载较小：

   ```bash
   jq '[.paths | to_entries[] | .key as $p | .value | to_entries[]
        | {path: $p, method: .key,
           operationId: .value.operationId,
           description: .value.description}]' /tmp/k6-openapi.json
   ```

   Grep 这项内容以查找您需要的操作（“abort”、“limits”、“schedule”、…）。

3. **拉取选定操作的完整模式**——参数、请求正文、响应——解析任何 `$ref` 指向：

   ```bash
   jq '.paths["<path>"]["<method>"]' /tmp/k6-openapi.json
   # 然后对于每个 "$ref": "#/components/schemas/Foo":
   jq '.components.schemas.Foo' /tmp/k6-openapi.json
   ```

4. **根据相同路径构建 `gcx api` 调用**，按 §2 前缀。认证由 gcx 注入——不要自行添加。

### 列表请求

当您调用的操作是列表端点时，默认按 **`created` 降序**（最新优先）并按 **20 分页**——都通过 OpenAPI 模式为该操作暴露的查询参数名称。名称不同（`ordering=-created`、`order_by=created.desc`、`sort=-created`、`limit=20`、`page_size=20`），这正是为什么在步骤 3 中从规范中发现它们很重要。最新优先意味着用户通常关心的条目会出现在第一页；页面大小为 20 可以保持响应足够小，以便在不消耗上下文的情况下进行总结。

#### 完全枚举：使用 `@nextLink` 分页

当您需要枚举 *所有* 行（而不仅仅是最新一页）时，v6 列表端点每个响应最多限制为 **1000 行**（默认 `$top`）并返回一个 `@nextLink` 字段指向下一页。**`gcx k6 runs list --limit 0` 不会自动跟随 `@nextLink`** 并默认按升序排序——对于具有 >1000 个历史运行的测试，它会静默返回 **最旧的** 1000，而不是最新的。实际效果：（第一/最后运行）从此输出中总结的内容可能非常过时（例如，一个已运行多年的每日计划测试将显示约 3 年前的 `last_run`）。使用 `gcx api` 对 v6 端点进行 `$orderby=created desc` 以获取最新优先切片，或循环 `@nextLink` 直到它不存在以进行完全枚举。

v6 列表端点暴露 OData 风格的查询参数：

| Param      | Purpose                                                              |
|------------|----------------------------------------------------------------------|
| `$orderby` | 排序——值必须是 `<field> <direction>`（例如 `created desc`）。允许的字段是操作特定的；`created` 是常见的。默认是升序。 |
| `$top`     | 页面大小，默认 1000（也是上限）                                      |
| `$skip`    | 偏移（`@nextLink` 已经编码了这个）                                   |
| `$count`   | 在响应中包含总数                                                   |

两个实用的默认值用于循环：`$orderby=created desc` 以确保第一页包含最新的运行（通常代理只关心这些），以及 `-o json` 以禁用溢出封装（参见 §2）以便跨页面保持解析的一致性。

```python
import json, subprocess, urllib.parse

CTX = "<stack>"
TEST_ID = "<test_id>"
PROXY = "/api/plugins/k6-app/resources/cloud"

all_runs = []
# 从最新开始；-o json 保持正文内联以进行干净的 json.loads()。
path = (
    f"{PROXY}/cloud/v6/load_tests/{TEST_ID}/test_runs"
    "?%24orderby=created%20desc&%24top=1000"
)
while path:
    r = subprocess.run(["gcx", "--context", CTX, "api", path, "-o", "json"],
                       capture_output=True, text=True, timeout=60)
    d = json.loads(r.stdout)
    all_runs.extend(d.get("value", []))
    nxt = d.get("@nextLink")
    if not nxt:
        path = None
        continue
    # @nextLink 作为绝对 http://api.k6.io/... URL 返回，OData 参数已编码（$skip, $top, $orderby）。将其路径+查询重塑为插件代理前缀：
    p = urllib.parse.urlparse(nxt)
    path = f"{PROXY}{p.path}" + (f"?{p.query}" if p.query else "")
```

对于任何返回 `@nextLink` 的 v6 列表端点，此模式都适用，而不仅仅是 `/test_runs`。如果您只需要几个最新的条目，在第一页后停止循环——使用 `$orderby=created desc`，该页面已经是最新的 1000。

### 指标

时间序列和聚合指标位于 **v5** API（`/cloud/v5/...`）上——Prometheus 风格的查询语义在 OData 风格的 URL 函数调用中（`query_range_k6(query='...',metric='...')`），而不是 v6 OpenAPI 捕获。完整的端点参考、选择器语法、按指标类型查询方法以及示例都在 [`references/metrics.md`](references/metrics.md) 中内联——在构建指标查询之前阅读它们。

### 日志

参见 §4。

---

## 4. 日志（通过 `gcx api` 的 Loki）

插件代理在 `/api/plugins/k6-app/resources/logs/` 下代理 Loki。您唯一需要手动提供的头是 `X-K6TestRun-Id`；gcx 处理认证。

```bash
RUN_ID="<run_id>"

# 将日志窗口范围限定在运行本身：`created` 表示开始，`ended` 表示结束。
# 如果 `ended` 为空，则运行仍在进行中——回退到 "now"。
# 仅当运行对象的时间戳不符合您正在调查的内容时，才使用更宽的硬编码窗口。
RUN=$(gcx api /api/plugins/k6-app/resources/cloud/cloud/v6/test_runs/$RUN_ID 2>/dev/null)
# k6 发射亚秒级精度（例如 "...:58.984041Z"）；jq 的 fromdateiso8601 仅接受整秒，
# 因此删除小数部分。
START=$(echo "$RUN" | jq -r '.created | sub("\\.[0-9]+Z$"; "Z") | fromdateiso8601')
END=$(echo "$RUN"   | jq -r 'if .ended then (.ended | sub("\\.[0-9]+Z$"; "Z") | fromdateiso8601) else (now | floor) end')

QUERY=$(printf '{test_run_id="%s"}' "$RUN_ID" | jq -sRr @uri)

# 将原始响应保存到 /tmp/——日志有效负载可能很大；内联流消耗上下文。
# 从文件中汇总，仅在需要时将 jq 应用于特定条目。
gcx api "/api/plugins/k6-app/resources/logs/api/v1/query_range?query=${QUERY}&direction=backward&start=${START}&end=${END}&limit=1000" \
  -H "X-K6TestRun-Id: $RUN_ID" 2>/dev/null > /tmp/run_${RUN_ID}_logs.json

# 紧凑的汇总——仅计数和流标签：
jq '{status, streams: (.data.result | length),
     total_entries: ([.data.result[].values | length] | add),
     stream_labels: [.data.result[].stream]}' /tmp/run_${RUN_ID}_logs.json
```

按需从 `/tmp/run_${RUN_ID}_logs.json` 拉取单个条目（例如 `jq '.data.result[].values[]' …`），而不是重新运行查询。

每个 LogQL 查询 **必须** 包含 `{test_run_id="<run_id>"}` 流选择器——插件代理按运行分区日志，并拒绝（或返回空结果）没有它的查询。在顶层选择器上添加其他过滤器：

- `{test_run_id="<run_id>"}` — 所有内容
- `{test_run_id="<run_id>"} | level=~"(error|warn)"` — 仅错误和警告
- `{test_run_id="<run_id>"} |= "specific text"` — 子字符串过滤器

方向和窗口提示：

- **将 `start`/`end` 限定在运行的 `created`/`ended` 字段**，而不是墙上时钟的“最后一小时”——否则查询会静默地忽略窗口之前的任何内容。唯一偏离的原因是您特意想要不同的间隔（例如周围上下文）。
- `direction=forward` 与 `start = run.created` 来查找第一个错误。
- `direction=backward` 与 `end = run.ended`（如果仍在运行则为 now）来查找最新输出。
- Loki 的保留期通常比 k6 的级联删除更久，因此已删除子运行日志可能仍会保留一段时间可查询。

---

## 5. 安全地编辑测试脚本

### 两个不同的脚本端点

有两个返回 k6 脚本体的 GET 端点，它们不可互换：

| 端点                                    | 它返回的内容                           | 使用时机                                            |
|---------------------------------------------|-------------------------------------------|--------------------------------------------------------|
| `/cloud/v6/load_tests/<test_id>/script`     | **当前** 负载测试脚本（可变；支持 PUT） | 编辑脚本；读取当前状态                              |
| `/cloud/v6/test_runs/<run_id>/script`       | 包含在特定运行中的脚本快照（只读）     | 调查过去运行实际执行的内容；跨版本比较              |

这两个端点可能会分道扬镳：如果负载测试脚本在运行完成后被编辑，该运行的快照将冻结在它执行的内容，而负载测试端点将提供新版本。包含快照的端点是只读的——您无法修改历史字节。

下面的安全编辑配方使用负载测试端点（可编辑的）。对于运行与运行的脚本差异（例如“最后一个通过运行和第一个失败运行之间脚本是否改变？”），获取两个运行的 `/test_runs/<id>/script` 并本地比较它们。

### 脚本体格式

脚本 GET 端点返回两种形状之一——在假设格式之前始终检测：

- **单个 js/ts 文件**。下面的配方直接处理此情况。
- **k6 tar 存档**（普通 tar 或 gzipped）。多文件项目捆绑（入口脚本 + 导入模块 + 资产）。要编辑：提取 JS 文件，修改它，然后使用 `k6 archive` 从修改后的 JS 重新构建存档。**不要**使用 `tar` 手动重新打包——存档包含 `metadata.json`，其中包含解析选项（项目 ID、阈值、场景），`k6 archive` 可以从脚本源正确重新生成。手动重新打包会保留过时的元数据并导致运行时错误（例如项目 ID 不匹配）。

  ```bash
  # 编辑 k6 tar 存档
  tar -xf /tmp/script_body -C /tmp/extracted/   # 提取
  # ... 修改 JS 文件 ...
  k6 archive /tmp/edited_script.js -O /tmp/new_archive.tar  # 重新构建
  ```

`gcx api` 不暴露响应头（见 §2），因此通过 `file(1)` 检查下载的体来检测形状：

```bash
gcx api /api/plugins/k6-app/resources/cloud/cloud/v6/load_tests/$ID/script \
  > /tmp/script_body
file /tmp/script_body
# 预期输出（示例）：
#   ASCII text          → js/ts 源
#   POSIX tar archive   → k6 tar 捆绑
#   gzip compressed data → gzipped tar 捆绑
```

PUT 主体必须是原始脚本（或存档）字节 (`application/octet-stream`)。gcx 不变地将请求转发给 k6。

```bash
ID="<load_test_id>"

# 1. 拉取当前脚本（单文件 js/ts 情况）
gcx api /api/plugins/k6-app/resources/cloud/cloud/v6/load_tests/$ID/script \
  > /tmp/script_current.js

# 2. 备份
cp /tmp/script_current.js /tmp/script_backup_$(date +%s).js

# 3. 编辑 → /tmp/script_new.js

# 4. 本地仅解析的合理性检查
k6 inspect /tmp/script_new.js | head -20

# 5. 1 次迭代冒烟（编辑 IN-FILE；--iterations CLI 标志会破坏浏览器场景）
sed 's/iterations: [0-9]\+/iterations: 1/' /tmp/script_new.js > /tmp/script_1iter.js
k6 run --quiet /tmp/script_1iter.js   # 退出码 0 = 通过，99 = 阈值失败

# 6. PUT — Content-Type 必须是 application/octet-stream
gcx api /api/plugins/k6-app/resources/cloud/cloud/v6/load_tests/$ID/script \
  -X PUT \
  -H "Content-Type: application/octet-stream" \
  -d "@/tmp/script_new.js"

# 7. 通过重新获取和比较 sha256 来验证——两个哈希值**必须**匹配。
#    不要依赖 `updated` 时间戳；它不会在脚本 PUT 时递增。
gcx api /api/plugins/k6-app/resources/cloud/cloud/v6/load_tests/$ID/script \
  > /tmp/script_verify.js
shasum -a 256 /tmp/script_new.js /tmp/script_verify.js
```

如果 PUT 返回 415，请仔细检查 `-H "Content-Type: application/octet-stream"` 是否成功传递（某些 shell 引用错误可能会丢失它）。在调试时向 `gcx api` 传递 `-vvv` 以获取请求/响应跟踪。

---

## 6. 浏览器截图

浏览器模块运行将截图 PNG 写入每个运行的 S3 存储中——这是文件 API 当前暴露的唯一工件类型。它们不通过 `/cloud/v6/` 暴露；检索通过一个单独的 `cloud-resources/v1/files/` 插件路由的两步流程进行。两次调用都需要与日志查询（§4）相同的 `X-K6TestRun-Id` 头——gcx 仍然处理认证，但运行 ID 必须手动提供或端点会以 HTTP 422 拒绝。

```bash
RUN_ID="<run_id>"

# 1. 索引——此运行拥有的截图路径的 JSON 数组。如果运行没有拍摄（例如非浏览器测试，或未调用 page.screenshot() 的浏览器运行），则为空数组。
gcx api /api/plugins/k6-app/resources/cloud/cloud-resources/v1/files/index \
  -H "X-K6TestRun-Id: $RUN_ID" -o json 2>/dev/null > /tmp/files_${RUN_ID}.json

# 每个条目看起来像：
#   "7542817/files/screenshots/screenshots/login-success.png"
# 重复的 "screenshots/screenshots/" 段落是真实的，不是打字错误——将路径原样传递给步骤 2。

# 2. 请求您想要的文件的预签名下载 URL。请求正文必须是 JSON；Content-Type 很重要。
FILES=$(jq -c '[.[] | {name: .}]' /tmp/files_${RUN_ID}.json)
PAYLOAD=$(jq -nc --argjson files "$FILES" \
  '{service:"aws_s3", operation:"download", files:$files}')

gcx api /api/plugins/k6-app/resources/cloud/cloud-resources/v1/files/generate-pre-signed-url \
  -X POST \
  -H "X-K6TestRun-Id: $RUN_ID" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" -o json 2>/dev/null > /tmp/presigned_${RUN_ID}.json

# 3. 直接下载每个预签名 URL——它们是普通的 S3 GET，没有 gcx 和没有认证头（签名在 URL 中）。URL 有效期为 24 小时（X-Amz-Expires=86400）；如果它们过期，请重新运行步骤 2。
mkdir -p /tmp/run_${RUN_ID}_files
jq -r '.urls[] | [.name, .pre_signed_url] | @tsv' /tmp/presigned_${RUN_ID}.json |
  while IFS=$'\t' read -r NAME URL; do
    curl -sS -o "/tmp/run_${RUN_ID}_files/$(basename "$NAME")" "$URL"
  done
```

### 值得知道的笔记

- **在签名之前索引。** `generate-pre-signed-url` 不会验证文件是否存在——它会愉快地为任何键生成 URL，而 404 只在您尝试下载时才会出现（S3 返回 `<Error><Code>NoSuchKey</Code>...>`）。始终从 `files/index` 派生文件列表，而不是猜测路径形状。
- **批量签名请求。** `files` 是一个数组，因此一次 POST 请求所有您需要的 URL，而不是每个文件一个调用——相同的 24 小时有效期涵盖整个批次。
- **浏览器测试与协议测试。** 仅调用过 `page.screenshot()` 的运行才会在索引中具有条目；纯协议/HTTP 运行将返回 `[]`。不要假设索引非空。

---

## 7. 浏览器跟踪（通过 `gcx api` 的 Tempo）

- **必须包含标题头。** 没有 `X-K6TestRun-Id` 头，`/search` 和 `/traces/<id>` 都会返回 HTTP 401。该标题头将查询范围限定在运行所属的租户内。
- **`start`/`end` 是 Unix 秒。** RFC3339 ISO 字符串会得到 HTTP 400 "无效的 start: strconv.ParseUint"。它们在技术上不是必需的——没有它们也可以进行搜索——但提供与运行的 `created`/`ended` 匹配的窗口（加上约 60 秒的缓冲区）可以使查询保持快速，并避免匹配共享相同场景名称的不相关的运行。
- **使用 TraceQL，而不是 LogQL。** `q` 参数使用 TraceQL——跨度谓词以 `span.<属性>` 的形式编写，并与 `&&` 结合。建议的查询筛选特定场景的迭代根跨度；通过删除 `test.scenario` 可以扩大范围，通过添加例如 `span.test.vu = 3 && span.test.iteration.number = 5` 可以缩小范围，以定位单个 VU 上的单个迭代。
- **场景名称来自运行。** 它们是运行对象上 `.options.scenarios` 的 *键*——`gcx api /api/plugins/k6-app/resources/cloud/cloud/v6/test_runs/$RUN_ID --json options 2>/dev/null | jq -r '.options.scenarios | keys[]'` 列出它们。默认场景的名称是 `default`；浏览器测试通常将其命名为 `ui`、`browser` 等。
- **OTLP 主体中的跨度 ID 是 base64 编码的。** 搜索响应中的 `traceID` 是十六进制（`/traces/<id>` 的形式接受）；OTLP 批次内部的 `traceId`/`spanId`/`parentSpanId` 字段是 base64 编码的字节。通过 `parentSpanId == spanId`（两者都是 base64）进行跨关联——无需解码。
- **有用的属性键** 在浏览器测试跨度上：`navigation.url`、`page.goto.url`、`screenshot.path`、`web_vital.name`、`web_vital.value`、`web_vital.rating`、`test.scenario`、`test.vu`、`test.iteration.number`、`k6.test_run_id`。这些都是值得在摘要中展示的属性；OTel 值信封是 `{stringValue|intValue|boolValue|doubleValue}`（上面的 jq `attrval` 帮助程序处理所有四种类型）。

---

## 8. 云洞察（运行审计结果）

Cloud Insights 对完成的测试运行启发式算法——检查高基数、WebVital 退化、缺失阈值、过载的负载生成器等——并通过单独的 `/resources/insights/` 插件路由（不是 `/cloud/v{N}/`）公开结果。gcx 仍然处理身份验证；不需要额外的标题头。

三个调用产生数据，代理有用的输出是跨其中两个调用的连接：

```bash
RUN_ID="<run_id>"
BASE="/api/plugins/k6-app/resources/insights/insights/api/v1/testrun/$RUN_ID"

# 1. 列出运行的执行，取最新的。响应是 { "executions": [ {id, version}, ... ] }——不是裸数组。选择最后一个条目；insights 重新运行会追加，最新的反映当前的审计/分数集。
EXEC_ID=$(gcx api "$BASE/executions" -o json 2>/dev/null \
  | jq -r '.executions[-1].id')

# 2. 审计定义（id、标题、描述、权重）。约 15 个条目。
gcx api "$BASE/executions/$EXEC_ID/audits" -o json 2>/dev/null \
  > /tmp/insights_audits_${RUN_ID}.json

# 3. 审计结果（audit_id、状态、分数、解释、操作）。
gcx api "$BASE/executions/$EXEC_ID/audits/results" -o json 2>/dev/null \
  > /tmp/insights_results_${RUN_ID}.json
```

两个响应使用相同的一级键——`audits`——但内容不同：步骤 2 是每个审计检查的目录，步骤 3 是该审计在此特定运行中找到的内容。通过 `result.audit_id == audit.id`（实践中是 1:1）进行跨连接。

### 连接到紧凑的、代理可读的摘要

原始审计 + 结果 JSON 大约是 10 KB。将两者都导入上下文只是为了读取每个审计的三行是浪费——在 `jq` 中执行连接并发出单个紧凑的块。下面的管道是推荐的形状：

```bash
jq -nr \
  --slurpfile a /tmp/insights_audits_${RUN_ID}.json \
  --slurpfile r /tmp/insights_results_${RUN_ID}.json '
  ($a[0].audits | INDEX(.id)) as $defs
  | $r[0].audits
  | map({
      title:         ($defs[.audit_id].title // "?"),
      description:   ($defs[.audit_id].description // ""),
      status:        .status,
      status_reason: .status_reason,
      score: (
        if .score == null            then "n/a"
        elif .score.type == "binary" then (if .score.value then "pass" else "fail" end)
        else (.score.value | tostring)
        end),
      explanation: (.explanation // "" | gsub("\n+"; " ") | .[0:300]),
      actions:     (.actions // [])
    })
  | .[]
  | "── \(.title) — score: \(.score)\(if .status == "failed" then " [audit did not run: \(.status_reason // "unknown")]" else "" end)\n  \(.description)\n  → \(.explanation)\(if (.actions|length) > 0 then "\n  actions:\n    - " + (.actions|join("\n    - ")) else "" end)\n"
'
```

对于 15 个审计的运行，这将发出约 5 KB 的纯文本——标题、分数、一行描述、一行解释以及任何操作项。这对于代理推理测试的健康状况而无需重新读取任何 JSON 块就足够了。

### 值得知道的注意事项

- **`status` ≠ 判定。** `status: "succeeded"` 意味着 *审计执行了*。判定存在于 `score` 中（`binary` 真/假，或 `numeric` 0…1，其中 1 是最好的）。`status: "failed"` 意味着审计本身无法运行（通常 `status_reason: "missing data"`——例如，在非跟踪测试上的 HTTP Spans 审计）；`score` 字段不存在。将它们视为“无信号”，而不是失败。
- **分数阈值每个审计都不同。** 一个 `numeric` 0.94 可能对一个审计是好的，而对另一个审计是令人担忧的——没有全局截止线。`解释` 是权威的，说明分数的含义；原文展示它，而不是编造通过/失败规则。
- **`actions` 是可操作的。** 仅当审计有具体建议时才存在（例如，“减少 `url` 标签的基数…”）。在为尝试改进运行的用户总结运行时，优先考虑具有非空 `actions` 数组的审计。
- **选择最后一个执行，而不是第一个。** `.executions[]` 是按时间顺序排列的；重新运行会追加。旧的执行反映旧的审计逻辑，并且可能具有过时的结果。
- **Insights 是运行后分析。** 如果运行未完成（或从未产生足够的数据以计算洞察），执行列表可能为空——优雅地退出 `length == 0`。

---

## 9. 本地 k6 CLI（烟雾测试和 `k6 cloud run`）

本地 `k6` CLI 是在推送到云端之前进行解析检查和 1 迭代烟雾运行的正确工具：

```bash
k6 inspect script.js | head -20      # 仅解析的合理性
k6 run --quiet script.js             # 本地运行
```

对于 `k6 cloud run`（上传 + 在云端从您的笔记本电脑运行），使用从 gcx 拉取的令牌和堆栈 URL 进行 `k6 cloud login`——令牌来自 `gcx k6 auth token`，堆栈 URL 来自活动的 gcx 上下文的 `grafana.server` 字段：

```bash
TOKEN=$(gcx --context <ctx> k6 auth token)
STACK=$(gcx --context <ctx> config view --minify -o json | jq -r '.contexts[].grafana.server')
k6 cloud login --token "$TOKEN" --stack "$STACK"
k6 cloud run script.js
```

k6 的云配置（`~/.config/k6/cloud.json`）是单上下文的，因此每次切换 gcx 上下文时都需要重新运行 `k6 cloud login`——否则 `k6 cloud run` 将继续针对以前的堆栈。

退出代码：`0` 通过，`99` 阈值失败，其他任何 = 脚本/运行时错误。

---

## 10. 常见问题

| 症状                                                                              | 原因                                                                | 修复 |
|--------------------------------------------------------------------------------------|----------------------------------------------------------------------|-----|
| `401 "无效或过期的令牌——运行 gcx login 刷新"`                          | gcx OAuth 会话过期                                            | `gcx login --context <ctx>` |
| `403 / 404` 在看起来正确的路径上                                               | 忘记了 REST 端点的加倍 `cloud/cloud/`                          | 使用 `…/resources/cloud/cloud/v{N}/…` |
| `415 不支持的媒体类型` 在脚本 PUT 上                                             | 缺少 `-H "Content-Type: application/octet-stream"`                | 添加它；传递 `-vvv`（或 `--log-http-payload`）给 `gcx api` 以检查请求 |
| 脚本 PUT 返回 200 但不起作用                                                   | `updated` 时间戳在脚本更改时没有递增                           | 通过 sha256 GET（§5 步骤 7）进行验证 |
| 运行状态 `passed` 但检查失败                                                | 零观察阈值报告为通过；`check()` 单独永远不会失败运行             | 添加 `'checks{check:<name>}': ['rate==1.0']`；在 catch 块中，`check(null, {"script completed":()=>false})` 强制观察 |
| Loki 查询对于最近的运行返回空结果                                          | 缺少 `X-K6TestRun-Id` 标题                                      | 在日志查询中始终传递 `-H "X-K6TestRun-Id: <run_id>"` |
| `gcx k6 runs list --limit 0` 返回 **最旧的** 1000 行，而不是最新的        | 子命令不遵循 `@nextLink` 并默认按升序排列——对于 >1000 运行，你看到的开始是历史的开始，而不是最近的活动 | 使用 `gcx api` 并带有 `$orderby=created desc` 以获得最新优先切片，或使用 §3 中的完整 `@nextLink` 循环 |
| `gcx k6 load-tests update -f` 返回 `✔ Updated` 但更改没有生效                | v6 PATCH 模式外的字段被静默丢弃（`PatchLoadTestApiModel` 仅允许 `name`、`baseline_test_run_id`——`additionalProperties: false`）被静默丢弃。值得注意的是 `project_id` 不能以这种方式更新 | 对于项目移动使用专用的 `/move` 端点（§11）；对于其他突变，请交叉检查 OpenAPI 规范中的 PATCH 模式。始终重新 GET 以确认 |
| `gcx k6 load-tests list --project-id <id>` 返回所有项目的测试               | 标志被接受但从未过滤——`/cloud/v6/load_tests` 没有项目查询参数 | 使用 `GET /cloud/v6/projects/{id}/load_tests` 通过 `gcx api`，或使用 `select(.project_id == X)` 在 jq 中客户端过滤 |
| `HTTP 415 "不支持的媒体类型 \"application/json\""` 在通过 `gcx api` 的多部分 POST 上 | Grafana 插件代理在转发之前重写多部分 Content-Types 为 `application/json`（gcx 本身发送你设置的标题；代理删除它） | 回退到直接 curl 对 `api.k6.io`（§1.2）。影响测试创建（`POST /cloud/v6/projects/{id}/load_tests`）和任何其他多部分端点 |
| `401 Unauthorized` 调用 `api.k6.io` / `cloudlogs.k6.io` 直接（curl 模式）      | 缺少/错误的 `Authorization: Bearer …` 或 `X-Stack-ID` 标题       | 重新检查两个标题；通过 `/cloud/v6/auth`（§1.2）从堆栈 URL 解决 `X-Stack-ID` |
| `404` 调用 `api.k6.io/api/plugins/...`（curl 模式）                                | 错误地保留了插件代理的前缀                           | 删除 `/api/plugins/k6-app/resources/{cloud,logs,insights}`——参见 §1.2 |

---

## 11. `update -f` 未涵盖的突变

`gcx k6 <资源> update -f` 遵循该资源的 v6 PATCH 模式。模式外的字段在 gcx 仍然打印 `✔ Updated <资源> <id>` 时被静默丢弃——参见 §10 行。几种常见的突变有 **专用的端点**，而 PATCH 路径将对此无操作。

| 突变                              | 端点                                              | 正文                          |
|---------------------------------------|-------------------------------------------------------|-------------------------------|
| 将测试移动到另一个项目          | `PUT /cloud/v6/load_tests/{id}/move`                  | `{"project_id": <int>}`       |
| 启动一个测试运行                      | `POST /cloud/v6/load_tests/{id}/start`                | `{}`（或运行选项）         |

**轮询已启动的运行：** 启动运行后，轮询 `GET /cloud/v6/test_runs/{id}`，直到 `status` 到达 `completed` 或 `aborted`。始终检查 `result` 字段与 `status`——`status: completed` 但 `result: error` 意味着配置或基础设施故障（不是阈值违规）。对于任何非 `passed` 结果，立即获取日志（§4）以显示错误，而不是等待用户报告它。

| 终止正在运行的测试                  | `POST /cloud/v6/test_runs/{id}/abort`                 | 空的                         |
| 设置/覆盖计划            | `POST /cloud/v6/load_tests/{id}/schedule`             | 计划正文（recurrence_rule 或 cron） |
| 激活/停用计划            | `POST /cloud/v6/schedules/{id}/{deactivate,activate}` | 空的                         |
| 创建负载测试（多部分的！）       | `POST /cloud/v6/projects/{id}/load_tests`             | 多部分：`name` + `script`  |
| 使运行持久化以超过保留期          | `POST /cloud/v6/test_runs/{id}/save`                  | 空的（与 `/unsave` 配对） |

`update -f` *确实* 可以工作的 PATCH 风格更新：

| 资源     | 可更新字段                                              |
|--------------|---------------------------------------------------------------|
| 负载测试    | `name`, `baseline_test_run_id`（按 `PatchLoadTestApiModel`）  |
| 项目      | `name` 仅（按 `PatchProjectApiModel`）                      |

两个模式都声明 `additionalProperties: false`——你放入清单中的任何其他字段在 PATCH 发送前都会被静默过滤掉，即使 gcx 仍然报告 `✔ Updated`。不要尝试通过 `update -f` 切换 `is_default` 或移动 `grafana_folder_uid`；它们在 v6 PATCH 上不可用于修改。

在假设字段可变之前，通过 OpenAPI 规范（§3 中的工作流）检查操作的请求模式。

### 工作示例——在项目之间移动测试

```bash
gcx api /api/plugins/k6-app/resources/cloud/cloud/v6/load_tests/<test_id>/move \
  -X PUT \
  -H "Content-Type: application/json" \
  -d '{"project_id": <new_project_id>}'

# 验证——重新 GET 并检查 `project_id` 反映了新值。
# 不要信任 PUT 的错误 absence；HTTP 204 与空正文是成功的形状，但 gcx api 什么也不打印。
gcx --context <ctx> k6 load-tests get <test_id> -o json | jq '{id, name, project_id}'
```

此端点的 OpenAPI 描述明确说明：*"将负载测试移动到同一组织中的不同项目。所有相应的测试运行也将移动到新项目。"* 你不需要单独迁移运行。

### 值得知道的级联行为

- **删除负载测试级联删除其计划。** 计划立即从 `/cloud/v6/schedules` 和 `/cloud/v6/load_tests/{id}/schedule` 中消失。不需要作为防御性步骤首先 `gcx k6 schedules delete <load-test-id>`。
- **删除项目时运行测试会失败，返回 HTTP 409** （根据 OpenAPI 规范，“不能删除正在运行的测试项目。”）。非运行测试似乎会随着项目一起删除，但如果你在删除它之前想清点项目的内容，请使用 `GET /cloud/v6/projects/{id}/load_tests`（不是 `gcx k6 load-tests list --project-id <id>`，它不过滤——参见 §10）。
- **移动测试会移动其运行和运行历史。** 计划附件也跟随测试（它按 `load_test_id` 键入，而不是按项目）。

### 验证规则的一般原则

这项技能中的常见模式是 *"gcx 确认成功，即使底层调用无操作"*。每次你修改状态时：

1. 记下你预期的更改（字段、计数、状态）。
2. 重新 GET 资源并确认更改已反映。
3. 如果没有，请检查是否需要专用的端点（本节）而不是 `update -f`。
