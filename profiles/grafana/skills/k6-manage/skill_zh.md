# Grafana Cloud k6 — 交互参考

默认路径是 `gcx` 命令行工具。如果未安装 `gcx`，则可以通过直接 curl 对 k6 的公共主机访问每个端点——有关身份验证标头和主机转换规则，请参阅 §1.2。其余部分由两个原则塑造：

- **gcx 拥有 Grafana 端的身份验证（如果存在）。** 它在每个调用中注入正确的标头，因此您不应自行设置身份验证标头。您唯一手动设置的标头是 `X-K6TestRun-Id`，用于 Loki 日志查询（§4）、浏览器屏幕截图/文件获取（§6）和 Tempo 跟踪查询（§7）——任何其他内容都会被覆盖或导致冲突。在 curl 模式下，身份验证标头是手动设置的；参见 §1.2。
- **首先使用 `gcx k6 ...` 子命令。** 它们用更友好的易用性包装了常用路径，并处理分页。使用 `gcx help-tree k6`（并使用 `gcx help-tree k6 <subcommand>` 进一步深入探索）；当没有适用于您需要的子命令时，才回退到 `gcx api`。

---

## 1. 身份验证

### 1.1 使用 gcx（默认）

```bash
gcx login --context <ctx>                # 一次性 OAuth，浏览器流程
gcx --context <ctx> config check         # 预期 "✔ 连接：在线"
```

一旦上下文登录，每个 `gcx api ...` 和 `gcx k6 ...` 调用都会继承其身份验证状态。如果调用返回 *"无效或过期的令牌——运行 gcx login 刷新"*，则 OAuth 会话已过期——重新运行 `gcx login --context <ctx>`。

### 1.2 没有 gcx — 直接 curl

首先检查 `command -v gcx`。如果它丢失了，则此技能中的每个端点仍然可以直接针对 k6 的公共主机——与 gcx 示例相比有三个变化：

- **身份验证标头是手动设置的。** 在每个调用中设置两者：
  - `Authorization: Bearer <k6_token>`
  - `X-Stack-ID: <int>`
- **主机替换了插件代理。**
  - REST (`/cloud/v6/...`, `/cloud/v5/...`, `/cloud-resources/v1/...`, `/insights/...`) → `https://api.k6.io`
  - 日志 (Loki) 和跟踪 (Tempo) → `https://cloudlogs.k6.io`
- **没有 `/api/plugins/k6-app/resources/{cloud,logs,insights}` 前缀。** 删除它；gcx 示例中该前缀之后的任何内容都是 k6 的实际路径。从 §2 中 `cloud/cloud/` 的双重怪癖折叠为单个 `/cloud/`——第一个只是代理路由。

#### 获取凭证

不要猜测这些——每次会话只提示用户一次：

1. **k6 API 令牌** — 长寿命的 bearer 令牌；当 gcx 配置时，`gcx k6 auth token` 将打印相同的值。
2. **Stack** — 要么是整数的 **stack ID**（直接用于 `X-Stack-ID`），要么是 Grafana 的 **stack URL**（例如 `https://myorg.grafana.net`）。如果用户提供 URL，请使用 `GET /cloud/v6/auth` 将其解析为 ID 一次，该端点接受 `X-Stack-Url` 标头并返回 `{stack_id, default_project_id}`：

```bash
STACK_ID=$(curl -sS https://api.k6.io/cloud/v6/auth \
  -H "Authorization: Bearer $K6_TOKEN" \
  -H "X-Stack-Url: $STACK_URL" \
  | jq -r '.stack_id')
```

会话中缓存解析的 ID——每个后续调用都需要在 `X-Stack-ID` 中提供（§1.2）。

#### 翻译速查表

| gcx 形式（插件代理）                                                                 | curl 形式（直接）                                                       |
|------------------------------------------------------------------------------------------|--------------------------------------------------------------------------|
| `gcx api /api/plugins/k6-app/resources/cloud/cloud/v6/test_runs/123`                     | `curl https://api.k6.io/cloud/v6/test_runs/123 -H ...`                   |
| `gcx api /api/plugins/k6-app/resources/cloud/cloud/v5/test_runs/<id>/metrics`            | `curl https://api.k6.io/cloud/v5/test_runs/<id>/metrics -H ...`          |
| `gcx api /api/plugins/k6-app/resources/cloud/cloud-resources/v1/files/index`             | `curl https://api.k6.io/cloud-resources/v1/files/index -H ...`           |
| `gcx api /api/plugins/k6-app/resources/insights/api/v1/testrun/<id>/executions` | `curl https://api.k6.io/insights/api/v1/testrun/<id>/executions -H ...`  |
| `gcx api /api/plugins/k6-app/resources/logs/api/v1/query_range?...`                      | `curl https://cloudlogs.k6.io/api/v1/query_range?... -H ...`             |
| `gcx api /api/plugins/k6-app/resources/logs/api/v1/tempo/api/search?...`                 | `curl https://cloudlogs.k6.io/api/v1/tempo/api/search?... -H ...`        |

在上述每个 `-H ...` 插槽中，发送两个身份验证标头：
`-H "Authorization: Bearer $K6_TOKEN" -H "X-Stack-ID: $STACK_ID"`。

注意：
- gcx 会留给你端点特定的标头——日志、跟踪和文件端点上的 `X-K6TestRun-Id`（§4、§6、§7）——仍然需要 *除了* 身份验证对 **auth pair**。
- §2 中的 `gcx api` 标头怪癖（溢出封装、`--json field` 过滤、`-o` 用于输出格式）不适用于 curl。使用普通的 curl 标头：`-o file` 保存正文，`--data-binary @file` 用于 PUT 负载，`-w '%{http_code}'` 用于状态代码，等等。
- 分页语义（`$orderby`, `$top`, `$skip`, `@nextLink` 从 §3）是 v6 端点的属性本身，并且通过 curl 完全相同。服务器返回的 `@nextLink` URL 已经是一个绝对 `https://api.k6.io/...` URL——直接将其传递回 curl 不变；§3 中的插件代理重塑不需要。

---

## 2. `gcx api` 路径的形状

如果没有子命令，回退到 `gcx api` 对 Grafana 插件代理路由：

- **REST API** (`/cloud/v6/`, `/cloud/v5/`) — 前缀为 `/api/plugins/k6-app/resources/cloud/<k6-path>`。
- **日志 (Loki)** — 前缀为 `/api/plugins/k6-app/resources/logs/<loki-path>`。

| k6 路径                                   | gcx 调用                                                                    |
|-------------------------------------------|-----------------------------------------------------------------------------------|
| `/cloud/v6/test_runs/{id}`                | `gcx api /api/plugins/k6-app/resources/cloud/cloud/v6/test_runs/{id}`             |
| `/cloud/v5/test_runs/{id}/metrics`        | `gcx api /api/plugins/k6-app/resources/cloud/cloud/v5/test_runs/{id}/metrics`     |
| Loki `/api/v1/query_range?...`            | `gcx api /api/plugins/k6-app/resources/logs/api/v1/query_range?...`               |

注意每个 REST 路径中的 `cloud/cloud/` 的双重怪癖——第一个 `cloud` 是代理路由，第二个是 k6 的 `/cloud/v{N}/` 命名空间。

### `gcx api` 标头怪癖

`gcx api` 不是一个 curl 克隆——几个标头与 curl 的记忆肌肉记忆不同：

- **响应正文** 写入标准输出。没有 `-o <file>` 标头保存正文；`-o` 选择输出格式 (`json`, `yaml`, `agents`)。使用 shell 重定向 (`> file`) 或 `$(...)` 捕获。
- **请求正文** 使用 `-d <string>`, `-d @file`, 或 `-d @-` (stdin)。没有 `--data-binary`；`-d @file` 已经保留字节。
- **没有 jq 的字段选择**：`--json field1,field2,...` 只返回列出的字段，并且 `--json list`（或 `--json '?'`）发现可用内容。通常比将内容管道到 jq 对于浅层提取更干净。
- **stderr 噪声**：gcx 在大多数调用中在 stderr 上打印一行 `hint:`。将内容管道到 `jq` 应该使用 `2>/dev/null` 重定向以避免意外。
- **响应标头** 不直接由 `gcx api` 暴露。当工作流程中的分支取决于 `Content-Type`（例如 §5 中的脚本 GET）时，使用 `file <path>` 检查下载的正文，而不是响应标头。

### 大响应溢出到临时文件

`gcx api` 不暴露响应标头（参见 §2），因此当分支在 §5 中取决于 `Content-Type`（例如脚本 GET）时，检查下载的正文使用 `file <path>` 而不是响应标头。

### 工作示例——在项目之间移动测试

```bash
gcx api /api/plugins/k6-app/resources/cloud/cloud/v6/test_runs/<test_id>/move \
  -X PUT \
  -H "Content-Type: application/json" \
  -d '{"project_id": <new_project_id>}'

# 验证——重新获取并检查 project_id 是否反映为新值。
# 不要相信 PUT 返回的错误；HTTP 204 与空正文是成功的形状，但 gcx api 不打印任何内容。
gcx --context <ctx> k6 load-tests get <test_id> -o json | jq '{id, name, project_id}'
```

此端点的 OpenAPI 描述是明确的：*"将负载测试移动到同一组织中的另一个项目。所有相应的测试运行也将移动到新项目。"* 您不需要单独迁移运行。

### 级联行为值得注意

- **删除负载测试将级联删除其计划。** 计划立即从 `/cloud/v6/schedules` 和 `/cloud/v6/load_tests/{id}/schedule` 中消失。不需要先运行 `gcx k6 schedules delete <load-test-id>` 作为防御性步骤。
- **删除包含正在运行的测试的项目会失败，返回 HTTP 409** （根据 OpenAPI 规范的 "无法删除包含正在运行的测试的项目"）。非运行的测试似乎会随着项目被删除，但如果您想在使用项目之前清点其内容，请使用 `GET /cloud/v6/projects/{id}/load_tests`（不使用 `gcx k6 load-tests list --project-id <id>`，后者不会过滤——参见 §10）。
- **移动测试会移动其运行和运行历史记录。** 计划附件也跟随测试（它由 `load_test_id` 键而不是项目键）。
