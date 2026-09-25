# SonarQube MCP 集成

通过模型上下文协议（MCP）服务器直接利用 SonarQube 和 SonarCloud 的功能，以在代理工作流中强制执行代码质量、发现问题并运行预推送分析。

## 概述

此技能提供使用 [SonarQube MCP 服务器](https://github.com/SonarSource/sonarqube-mcp-server) 工具的说明和模式。它支持以下自动化工作流：

- 在合并或部署之前检查质量门禁状态
- 按严重程度和项目发现和分派问题
- 在提交前（左移）本地分析代码片段
- 了解具有完整文档的 SonarQube 规则

## 何时使用

当用户需要以下功能时，请使用此技能：

- 用户希望在合并 PR 之前检查项目是否通过其质量门禁
- 用户希望在一个或多个 SonarQube 项目中找到关键或阻止性问题
- 用户希望在推送到 CI 之前分析代码片段以发现问题
- 用户希望了解为什么特定的 Sonar 规则标记了他们的代码
- 用户要求预提交或预推送质量反馈

**触发短语：** "检查质量门禁"、"SonarQube 质量门禁"、"查找 Sonar 问题"、"搜索 Sonar 问题"、"使用 Sonar 分析代码"、"检查 Sonar 规则"、"Sonarcloud 问题"、"预推送 Sonar 检查"、"Sonar 预提交"

## 前提条件和设置

该插件包含一个 `.mcp.json` 文件，通过 Docker 自动启动 SonarQube MCP 服务器。在使用此技能之前，请设置所需的环境变量：

**SonarQube 服务器（远程或本地）：**
```bash
export SONARQUBE_TOKEN="squ_your_token"
export SONARQUBE_URL="https://sonarqube.mycompany.com"  # 或 http://host.docker.internal:9000 用于本地 Docker
```

**SonarCloud：**
```bash
export SONARQUBE_TOKEN="squ_your_token"
export SONARQUBE_ORG="your-org-key"   # SonarCloud 所需
# SONARQUBE_URL 不需要用于 SonarCloud
```

**要求：**
- Docker 必须已安装并正在运行
- `SONARQUBE_TOKEN` 始终是必需的
- `SONARQUBE_URL` 对于 SonarQube 服务器是必需的（对于本地实例使用 `host.docker.internal`）
- `SONARQUBE_ORG` 对于 SonarCloud 是必需的（省略 `SONARQUBE_URL`）

## 快速入门

1. 设置您的 SonarQube/SonarCloud 凭据：
   ```bash
   # SonarQube 服务器
   export SONARQUBE_TOKEN="squ_your_token"
   export SONARQUBE_URL="https://sonarqube.mycompany.com"

   # SonarCloud
   export SONARQUBE_TOKEN="squ_your_token"
   export SONARQUBE_ORG="your-org-key"
   ```

2. 验证 MCP 工具的可用性：
   - 工具名称遵循以下模式：`mcp__sonarqube-mcp__<工具名称>`

3. 如果 MCP 服务器启动失败，请检查：
   - Docker 正在运行
   - 环境变量已设置
   - 参考：[mcp/sonarqube on Docker Hub](https://hub.docker.com/r/mcp/sonarqube)

## 参考文档

- `references/metrics.md` — 常见的 SonarQube 指标及其含义
- `references/severity-levels.md` — Sonar 严重程度级别和影响类别
- `references/best-practices.md` — PR 检查和预提交分析的流程
- `references/llm-context.md` — LLM 代理的工具选择指南和参数映射

## 说明

### 第 1 步：确定所需的操作

确定用户需要什么操作：

| 用户意图 | 要使用的工具 |
|---|---|
| 检查项目是否通过质量门禁 | `get_project_quality_gate_status` |
| 在项目中查找关键问题 | `search_sonar_issues_in_projects` |
| 提交前分析代码 | `analyze_code_snippet` |
| 了解被标记的规则 | `show_rule` |
| 获取详细的项目指标 | `get_component_measures` |
| 将问题标记为误报 | `change_sonar_issue_status` |

如果用户的意图不明确，请在继续之前询问项目键和目标。

### 第 2 步：质量门禁监控

使用 `get_project_quality_gate_status` 来验证项目是否符合其质量标准。

**参数：**
- `projectKey` (字符串) — SonarQube/SonarCloud 中的项目键
- `pullRequest` (字符串, 可选) — 用于 PR 特定门禁检查的拉取请求 ID
- `analysisId` (字符串, 可选) — 特定的分析 ID

> 注意：此工具上没有 `branch` 参数。如果没有 `pullRequest` 或 `analysisId`，该工具将返回默认分支的质量门禁状态。

**模式 — 检查默认分支门禁：**

```json
{
  "name": "get_project_quality_gate_status",
  "arguments": {
    "projectKey": "my-application"
  }
}
```

**模式 — 在合并前检查 PR 门禁：**

```json
{
  "name": "get_project_quality_gate_status",
  "arguments": {
    "projectKey": "backend-service",
    "pullRequest": "456"
  }
}
```

**解释响应：**
- `status: "OK"` — 门禁通过，可以合并/部署
- `status: "ERROR"` — 门禁失败；检查 `conditions` 数组以获取失败的指标
- 每个条件显示：`metricKey`, `actualValue`, `errorThreshold`, `comparator`

有关更多指标键的信息，请参阅 `references/metrics.md`。

### 第 3 步：问题发现和分派

使用 `search_sonar_issues_in_projects` 来查找和优先处理问题。

**参数：**
- `projects` (数组, 可选) — 项目键列表；省略以搜索所有可访问的项目
- `severities` (数组, 可选) — 过滤器：`BLOCKER`, `HIGH`, `MEDIUM`, `LOW`, `INFO`
- `pullRequestId` (字符串, 可选) — 限制搜索到特定的 PR
- `p` (整数, 可选) — 页码（默认：1）
- `ps` (整数, 可选) — 页大小（默认：100，最大：500）

**模式 — 查找阻止和关键问题：**

```json
{
  "name": "search_sonar_issues_in_projects",
  "arguments": {
    "projects": ["my-backend", "my-frontend"],
    "severities": ["BLOCKER", "HIGH"],
    "p": 1,
    "ps": 50
  }
}
```

**模式 — 在 PR 中搜索问题：**

```json
{
  "name": "search_sonar_issues_in_projects",
  "arguments": {
    "projects": ["my-service"],
    "pullRequestId": "123",
    "severities": ["HIGH", "MEDIUM"],
    "p": 1,
    "ps": 100
  }
}
```

**使用 `change_sonar_issue_status` 管理问题：**

使用此功能将误报或接受的技术债务标记为：

```json
{
  "name": "change_sonar_issue_status",
  "arguments": {
    "key": "AY1234",
    "status": "falsepositive",
    "comment": "此模式在我们的上下文中是安全的，因为..."
  }
}
```

有效状态：`falsepositive`（不是真实问题）、`accept`（接受技术债务）、`reopen`（重置为打开）

> 始终在更改用户状态之前向用户展示问题列表。切勿在没有明确用户确认的情况下自动将问题标记为误报。

### 第 4 步：预推送分析（左移）

使用 `analyze_code_snippet` 在提交前对代码运行 SonarQube 分析。

**参数：**
- `projectKey` (字符串) — 用于上下文的项目键
- `fileContent` (字符串, **必需**) — 要分析的文件完整内容
- `language` (字符串, 可选) — 语言提示以获得更好的准确性
- `codeSnippet` (字符串, 可选) — 将结果限制在 `fileContent` 内的特定子范围

**支持的语言：** `javascript`, `typescript`, `python`, `java`, `go`, `php`, `cs`, `cpp`, `kotlin`, `ruby`, `scala`, `swift`

**模式 — 提交前分析 TypeScript 文件：**

```json
{
  "name": "analyze_code_snippet",
  "arguments": {
    "projectKey": "my-typescript-app",
    "fileContent": "async function fetchUser(id: string) {\n  const query = `SELECT * FROM users WHERE id = ${id}`;\n  return db.execute(query);\n}",
    "language": "typescript"
  }
}
```

**模式 — 分析 Python 文件：**

```json
{
  "name": "analyze_code_snippet",
  "arguments": {
    "projectKey": "my-python-service",
    "fileContent": "import pickle\n\ndef load_model(path):\n    with open(path, 'rb') as f:\n        return pickle.load(f)",
    "language": "python"
  }
}
```

**响应解释：**
- 每个问题包括：`ruleKey`, 严重程度, 干净代码属性, 影响类别, 行号, 快速修复的可用性
- 在提交前解决 `CRITICAL` 和 `HIGH` 严重程度的问题
- 使用 `show_rule` 并使用 `ruleKey` 值来解释任何不熟悉的规则

### 第 5 步：规则教育

使用 `show_rule` 了解为什么规则存在以及如何修复被标记的代码。

**参数：**
- `key` (字符串) — 规则键，格式为 `<语言>:<规则 ID>`（例如，`typescript:S1082`, `java:S2068`）

**模式 — 获取规则文档：**

```json
{
  "name": "show_rule",
  "arguments": {
    "key": "typescript:S1082"
  }
}
```

**响应包括：** 规则名称, 类型, 严重程度, 完整描述, 标签（例如，`cwe`, `owasp-a2`）, 语言, 修复工作量的估计, 非符合与符合的代码示例。

### 第 6 步：获取组件指标

使用 `get_component_measures` 获取项目、目录或文件的详细指标。

**参数：**
- `projectKey` (字符串) — SonarQube/SonarCloud 中的项目键
- `pullRequest` (字符串, 可选) — PR ID 用于 PR 范围内的指标
- `metricKeys` (数组) — 要检索的指标键列表

**常见指标键：** `coverage`, `bugs`, `vulnerabilities`, `code_smells`, `complexity`, `cognitive_complexity`, `ncloc`, `duplicated_lines_density`, `new_coverage`, `new_bugs`

**模式 — 项目健康仪表板：**

```json
{
  "name": "get_component_measures",
  "arguments": {
    "projectKey": "my-project-key",
    "metricKeys": ["coverage", "bugs", "vulnerabilities", "code_smells", "ncloc"]
  }
}
```

有关完整指标参考，请参阅 `references/metrics.md`。

### 第 7 步：向用户展示结果

在每次工具调用后：
- 以人类可读的形式总结发现结果
- 标记需要关注的问题（BLOCKER, HIGH 严重程度）
- 根据发现结果提出下一步操作
- 在采取修复措施（例如，更改问题状态、修改代码）之前等待用户确认

## 示例

### 示例 1：合并前质量门禁检查

**用户请求：** "检查项目 `backend-api` 在 PR #234 是否通过质量门禁"

```json
{
  "name": "get_project_quality_gate_status",
  "arguments": {
    "projectKey": "backend-api",
    "pullRequest": "234"
  }
}
```

**如果门禁失败：** 提取失败的条件，向用户展示，然后使用 `search_sonar_issues_in_projects` 按相同的 PR 过滤以显示实际问题。

### 示例 2：推送前左移分析

**用户请求：** "在我推送之前分析这个 Go 函数"

```json
{
  "name": "analyze_code_snippet",
  "arguments": {
    "projectKey": "my-go-service",
    "fileContent": "func handler(w http.ResponseWriter, r *http.Request) {\n  id := r.URL.Query().Get(\"id\")\n  query := fmt.Sprintf(\"SELECT * FROM orders WHERE id = %s\", id)\n  rows, _ := db.Query(query)\n  // ...\n}",
    "language": "go"
  }
}
```

展示结果 → 对于每个问题，可以选择调用 `show_rule` 并使用 `ruleKey` 值来解释如何修复。

### 示例 3：项目中分派阻止性问题

**用户请求：** "显示 `payment-service` 中的所有阻止性问题"

```json
{
  "name": "search_sonar_issues_in_projects",
  "arguments": {
    "projects": ["payment-service"],
    "severities": ["BLOCKER"],
    "p": 1,
    "ps": 50
  }
}
```

按类别（安全、可靠性、可维护性）分组结果并展示给用户。提供调用 `show_rule` 以解释不熟悉规则的选项。

## 最佳实践

1. **环境设置** — 每次会话设置一次凭据；MCP 服务器将自动获取它们
2. **始终在合并前检查质量门禁** — 将 `get_project_quality_gate_status` 作为任何 PR 审查工作流程的一部分运行
3. **在开发过程中左移安全问题** — 在 CI 中使用 `analyze_code_snippet` 而不是仅使用 CI
4. **按严重程度优先处理** — 首先解决 BLOCKER 和 HIGH 严重程度的问题；为 MEDIUM 和 LOW 记录决策
5. **使用 `show_rule` 解释不熟悉的键** — 在不了解其意图之前切勿忽略规则
6. **分页大型结果集** — 使用 `p` 和 `ps` 参数；处理多页响应以获得完整覆盖
7. **切勿自动更改问题状态** — 始终向用户展示问题并获取明确确认后再调用 `change_sonar_issue_status`
8. **提供语言提示** — 在 `analyze_code_snippet` 中指定 `language` 以获得更准确的分析

## 限制和警告

- MCP 服务器必须配置并正在运行；在使用前验证工具可用性
- `analyze_code_snippet` 独立分析代码片段 — 完整项目上下文可能会影响 CI 中的结果
- 问题状态更改（误报、不会修复）需要适当的 SonarQube 权限
- SonarCloud 和 SonarQube 服务器 API 大致兼容，但某些功能有所不同；检查 `references/llm-context.md`
- 分页是必需的，因为项目中有许多问题；检查响应中的 `paging.total` 和 `paging.pageSize` 以确定是否需要迭代更多页面
- 质量门禁状态反映上次完成的分析 — 如果代码已更改，请触发新的分析
