# AIQ 研究技能

## 目的

使用此技能通过辅助脚本 `scripts/aiq.py` 调用本地运行的 NVIDIA AI-Q Blueprint 服务器。

使用此技能进行研究型请求，包括：

- "深入研究..."
- "AIQ 研究..."
- "研究..."
- "使用 AI-Q 回答..."
- "向 AI-Q 询问..."

不要使用此技能进行安装、部署、启动、停止、UI、CLI、Docker、Helm 或故障排除请求。这些属于 `aiq-deploy`。

## 前置条件

用户需要：

- 可用 Python 3.11+，通过 `python3` 命令访问。
- 一个可访问的本地或自托管 AI-Q Blueprint 后端。
- 当后端不在 `http://localhost:8000` 运行时，设置 `AIQ_SERVER_URL`；非本地值必须在发送任何查询之前由用户信任。
- 一个为该公共辅助脚本禁用了身份验证的后端配置，或为认证环境配置了单独的认证 AI-Q 技能。
- 从本地计算机到 AI-Q 后端 URL 的网络访问权限。
- 后端环境中配置的凭证，而不是在此技能中配置。此公共辅助脚本不会收集或管理 API 密钥。

辅助脚本没有第三方 Python 包依赖项；它使用 Python 标准库的 HTTP 模块。

## 说明

1.  解析目标后端 URL。
2.  在发送研究请求之前运行 `health`。
3.  如果没有可访问的后端，询问后端 URL 或转交给 `aiq-deploy`。
4.  在发送任何用户查询之前，声明将接收该查询的确切 AI-Q 后端 URL。对于非本地 URL，只有当用户明确确认当前对话中该 URL 是受信任的，才继续。
5.  当 AI-Q 返回作业 ID 时，轮询异步深入研究作业。
6.  带有引用和源 URL 完整地呈现返回的报告。
7.  在作业失败时停止，并显示返回的错误；不要自动重试。
8.  在呈现报告后，支持后续操作：回答关于它的提问（ask）或运行精炼研究（redo）使用相同的命令。

### 第 1 步 - 解析后端

当 `AIQ_SERVER_URL` 设置时使用它。否则尝试默认的本地后端：

```bash
python3 $SKILL_DIR/scripts/aiq.py health
```

预期输出：来自可访问 AI-Q 健康端点的 JSON。

如果 `health` 失败且没有设置明确的 `AIQ_SERVER_URL`，询问：

```text
我没有看到可访问的本地 AI-Q 后端。您是否已经有了要使用的 AI-Q 后端 URL，或者我应该部署本地 Skill 后端？
```

- 如果用户提供 URL，为后续的辅助脚本调用设置 `AIQ_SERVER_URL` 并重新运行 `health`。
- 如果用户希望本地部署，转交给 `aiq-deploy` 并保留原始研究请求。
- 如果可访问的后端返回 `401` 或 `403`，停止并解释此公共技能不管理身份验证。询问用户使用认证的 AI-Q 技能或为其环境配置身份验证。
- 如果 `health` 成功，但 `/chat` 或 `/v1/jobs/async/agents` 失败，报告后端是可访问的，但与公共研究流程不兼容，然后提供运行 `aiq-deploy` 验证。

### 第 2 步 - 发送路由的研究请求

在发送请求之前，声明解析的端点：

```text
我将此查询发送到 <AIQ_SERVER_URL>。在发送敏感信息之前，请确保此端点是受信任的。
```

不要通过查询文本发送凭证、cookies、bearer tokens 或秘密值。

运行：

```bash
python3 $SKILL_DIR/scripts/aiq.py chat "<USER_QUESTION>"
```

预期输出：

- 对于浅层或直接回答的正常 JSON 响应。
- 或包含 `{"status": "deep_research_running", "job_id": "<JOB_ID>"}` 的结构化 JSON，用于异步深入研究。

如果响应是正常 JSON，立即呈现结果。在没有 `job_id` 时不要强制轮询。

### 第 3 步 - 轮询异步作业

如果响应包含 `deep_research_running`，提取 `job_id` 并使用相同的绝对脚本路径轮询：

```bash
python3 $SKILL_DIR/scripts/aiq.py research_poll <JOB_ID>
```

预期输出：作业成功完成时的最终报告 JSON。

使用可用的运行时非阻塞或后台执行机制。如果选择的执行方法需要提升权限，请先请求用户明确批准，并解释原因。告诉用户深入研究正在后台运行。

### 第 4 步 - 在中断后恢复

如果轮询中断，作业在服务器端继续。使用：

```bash
python3 $SKILL_DIR/scripts/aiq.py status <JOB_ID>
python3 $SKILL_DIR/scripts/aiq.py report <JOB_ID>
python3 $SKILL_DIR/scripts/aiq.py research_poll <JOB_ID>
```

使用 `status` 检查作业状态和保存的工件。当作业已完成且您只需要最终输出时使用 `report`。使用 `research_poll` 继续等待完成。

最终报告可能引用生成的工件（图表、CSV）作为 `artifact://<id>` 链接。要将其作为本地文件材料化，运行 `python3 $SKILL_DIR/scripts/aiq.py artifacts <JOB_ID> --download-dir ./aiq-artifacts`；它下载每个工件并打印本地路径。不要期望报告本身包含 base64 图像数据。

对于自包含、可共享的报告，运行 `python3 $SKILL_DIR/scripts/aiq.py report <JOB_ID> --out-dir ./my-report`。它写入 `report.md` 以及一个 `artifacts/` 文件夹，并将每个 `artifact://<id>` 链接重写为匹配的本地文件，因此报告（包括图表）在任何 markdown 查看器中都能渲染，而无需运行后端。

### 第 5 步 - 呈现报告

当 `research_poll` 成功完成时，获取并呈现完整报告。保留引用和源 URL。如果作业状态是 `failed`、`failure` 或 `cancelled`，显示状态响应中的错误，并询问用户是否希望使用更窄的查询或不同方法重试。

### 第 6 步 - 后续操作：询问、编辑或重做报告

报告呈现后，用户通常希望深入研究或调整范围。
重用现有的后端流程——相同的认证边界、轮询和从步骤 1-5 的报告检索适用；没有单独的后续端点。

**询问**——关于已掌握报告的后续问题：

- 对于可以从您已有的报告中回答的问题，直接从其内容和引用回答；不要再次调用后端。
- 对于需要新调查的问题，发送一个包含从先前问题和报告所需上下文的全新请求到新的查询文本，然后呈现新结果：

  ```bash
  python3 $SKILL_DIR/scripts/aiq.py chat "<FOLLOW_UP_QUESTION> (context: <PRIOR_TOPIC>)"
  ```

  如果这返回 `deep_research_running` 作业 ID，使用 `research_poll` 按步骤 3 精确轮询它。

**编辑**——使用外观更改重写报告。此技能只能访问生成初始报告的数据。没有可用的工具：

```bash
python3 $SKILL_DIR/scripts/aiq.py report_edit <JOB_ID> "<EDIT_INSTRUCTIONS>"
```

**重做**——使用调整范围（更窄的查询、更正的问题或不同深度）重新运行研究：

```bash
python3 $SKILL_DIR/scripts/aiq.py research "<REFINED_QUERY>" [agent_type]
```

- 选择 `agent_type` 以匹配所需的深度（例如，使用深度代理进行彻底遍历，或 `shallow_researcher` 进行快速遍历）；如果不确定，可以使用 `agents` 列出选项。
- 将重做视为新作业：在发送之前再次声明目标端点（步骤 2），然后按步骤 3-5 轮询和呈现。

不要在后续查询文本中发送凭证或秘密值，并在每个后续答案中保留引用和源 URL。

## 版本兼容性

**重要提示：** 此技能设计用于 NVIDIA AI-Q Blueprint 版本 2.1.0。

语义版本兼容性规则：

```text
技能版本: X.Y.Z
Blueprint 或端点版本: A.B.C

兼容 IF:
1. A == X (主版本必须匹配)
2. B >= Y (次版本必须相等或更高)
3. C 可以是任何值 (补丁版本不影响兼容性)
```

示例：

- 技能版本 2.1.0 与 Blueprint 版本 2.1.0 兼容。
- 技能版本 2.1.0 与 Blueprint 版本 2.2.0 兼容。
- 技能版本 2.1.0 与 Blueprint 版本 2.1.5 兼容。
- 技能版本 2.1.0 与 Blueprint 版本 3.0.0 不兼容。
- 技能版本 2.1.0 与 Blueprint 版本 2.0.0 不兼容。

如果您的 Blueprint 版本不兼容：

1. 检查是否有与您的 Blueprint 版本匹配的更新技能版本。
2. 使用与此技能兼容的 Blueprint 版本。
3. 只有在用户接受兼容性风险时才继续；API 路由或响应形状可能已更改。

## 可用脚本

| 脚本 | 目的 | 参数 |
|---|---|---|
| `scripts/aiq.py health` | 检查配置的服务器是否响应 | 无 |
| `scripts/aiq.py chat` | POST `/chat`；可能返回内联输出或深入研究作业 ID | `<query>` |
| `scripts/aiq.py agents` | 列出可用的异步代理类型 | 无 |
| `scripts/aiq.py submit` | 提交显式的异步作业 | `<query> [agent_type]` |
| `scripts/aiq.py research` | 提交异步作业，轮询并打印最终报告 JSON | `<query> [agent_type]` |
| `scripts/aiq.py research_poll` | 继续轮询现有异步作业 | `<job_id>` |
| `scripts/aiq.py status` | 获取作业状态加上 `/state` 工件 | `<job_id>` |
| `scripts/aiq.py state` | 仅获取事件存储工件 | `<job_id>` |
| `scripts/aiq.py report` | 获取最终报告；使用 `--out-dir DIR`，导出可移植的 `report.md` + `artifacts/` 文件夹，并将链接重写为本地文件 | `<job_id> [--out-dir DIR]` |
| `scripts/aiq.py report_edit` | 使用外观更改编辑完成的报告 | `<job_id> <edit_instructions>` |
| `scripts/aiq.py artifacts` | 列出持久工件；使用 `--download-dir DIR`，下载它们并打印本地路径 | `<job_id> [--download-dir DIR]` |
| `scripts/aiq.py stream` | 从作业流 SSE 事件 | `<job_id>` |
| `scripts/aiq.py cancel` | 取消正在运行的作业 | `<job_id>` |

当主机支持 `run_script()` 辅助脚本时，使用 `scripts/aiq.py` 和上述参数调用它。否则，运行等效的 shell 命令，例如 `python3 $SKILL_DIR/scripts/aiq.py health`。

## 环境变量

| 变量 | 是否必需 | 默认值 | 描述 |
|---|---:|---|---|
| `AIQ_SERVER_URL` | 否 | `http://localhost:8000` | 本地或自托管的 AI-Q 服务器基本 URL |

## 安全最佳实践

- 不要在 `AIQ_SERVER_URL` 中放置 API 密钥、bearer tokens、cookies 或基本认证凭证。
- 在 AI-Q 部署环境中存储后端凭证，而不是在此技能或命令示例中。
- 用户查询文本将传输到配置的 `AIQ_SERVER_URL`。在发送敏感或机密信息之前，确认端点是受信任的。
- 如果后端使用私有数据源，将返回的报告视为可能敏感。
- 不要从返回报告中截断引用或源 URL。

## 限制

- 此技能需要一个正在运行的 AI-Q 后端；它不会部署一个。
- 公共辅助脚本不管理认证令牌或 cookies。
- 远程 `AIQ_SERVER_URL` 端点可能会记录提示、响应和元数据。
- 如果后端返回 HTTP 500 或缺少异步代理，报告失败，而不是编造研究答案。

## 示例

### 示例 1：运行路由的聊天或研究请求

```bash
python3 $SKILL_DIR/scripts/aiq.py health
python3 $SKILL_DIR/scripts/aiq.py chat "比较本地 AI-Q 深入研究与标准网络搜索工作流程"
```

预期输出：

```text
<来自 AI-Q 的健康 JSON>
<JSON 聊天响应或 {"status": "deep_research_running", "job_id": "<JOB_ID>"}>
```

如果 AI-Q 返回作业 ID，继续使用 `research_poll`。

### 示例 2：恢复现有作业

```bash
python3 $SKILL_DIR/scripts/aiq.py status <JOB_ID>
python3 $SKILL_DIR/scripts/aiq.py research_poll <JOB_ID>
```

将 `<JOB_ID>` 替换为 AI-Q 返回的 UUID。预期输出：状态 JSON 后跟作业完成时的报告 JSON。如果作业失败，显示返回的状态，不要自动重试。

### 示例 3：使用精炼查询询问后续操作或重做

```bash
# 询问：需要新调查的后续问题，附带先前上下文。
python3 $SKILL_DIR/scripts/aiq.py chat "在成本方面如何比较？(上下文：本地 AI-Q 深入研究与网络搜索)"

# 重做：使用更窄的查询和显式深度重新运行研究。
python3 $SKILL_DIR/scripts/aiq.py research "AI-Q 深入研究单个工作站成本" shallow_researcher
```

预期输出：路由的聊天响应或新的 `deep_research_running` 作业 ID
使用 `research_poll` 轮询。保留引用和源 URL 完整地呈现后续答案。

## 参考

| 主题 | 文档 |
|---|---|
| 辅助脚本 | `scripts/aiq.py` |
| 部署和后端验证 | `../aiq-deploy/SKILL.md` |

## 常见问题

### 问题：没有可访问的后端

**症状：**

- `health` 因连接被拒绝而失败。
- 默认的 `http://localhost:8000` URL 没有响应。

**原因：**

- AI-Q 没有运行。
- AI-Q 在不同的主机或端口上运行。
- 本地防火墙或网络设置阻止了连接。

**解决方案：**

1. 询问用户是否已有现有的 AI-Q 后端 URL。
2. 如果他们提供，设置它并重新运行健康：
   ```bash
   export AIQ_SERVER_URL="http://localhost:<PORT>"
   python3 $SKILL_DIR/scripts/aiq.py health
   ```
3. 如果他们希望本地部署，转交给 `aiq-deploy` 并保留原始研究请求。

### 问题：后端需要身份验证

**症状：**

- 请求因 HTTP 401 或 HTTP 403 失败。
- 后端是可访问的，但拒绝 `/chat` 或异步作业调用。

**原因：**

- 后端部署时启用了身份验证。
- 公共辅助脚本不附加用户令牌或 cookies。

**解决方案：**

1. 停止并解释此公共技能不管理身份验证。
2. 询问用户使用认证的 AI-Q 技能或为其环境配置此公共本地工作流程。
3. 仅在解决认证边界后，重新运行 `health` 和原始查询。

### 问题：健康成功但研究路由失败

**症状：**

- `health` 返回成功。
- `/chat`、`/v1/jobs/async/agents` 或轮询命令失败。

**原因：**

- 后端没有使用 API 启用的 AI-Q 配置。
- 异步作业注册表在选定的后端中不可用。
- 后端版本与此技能不兼容。

**解决方案：**

1. 运行：
   ```bash
   python3 $SKILL_DIR/scripts/aiq.py agents
   ```
2. 如果代理不可用，报告兼容性失败并提议运行 `aiq-deploy` 验证。
3. 确认部署的 Blueprint 版本与技能版本 2.1.0 兼容。

### 问题：作业中断或似乎卡住

**症状：**

- 本地轮询中断。
- 作业仍然显示 `running`。
- 轮询输出显示 `running`，但返回了报告或取消说作业已经 `success`。

**原因：**

- 深入研究是异步的，并在服务器端继续。
- 本地轮询输出可能滞后于终端服务器状态。

**解决方案：**

1. 检查当前状态：
   ```bash
   python3 $SKILL_DIR/scripts/aiq.py status <JOB_ID>
   ```
2. 如果 `has_report: true` 或 `job_status.status: success`，获取报告：
   ```bash
   python3 $SKILL_DIR/scripts/aiq.py report <JOB_ID>
   ```
3. 如果作业仍在运行，继续轮询：
   ```bash
   python3 $SKILL_DIR/scripts/aiq.py research_poll <JOB_ID>
   ```
