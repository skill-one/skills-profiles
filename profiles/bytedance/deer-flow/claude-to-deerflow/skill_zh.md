# DeerFlow 技能

通过其 HTTP API 与正在运行的 DeerFlow 实例进行通信。DeerFlow 是一个基于 LangGraph 构建的 AI 代理平台，用于协调用于研究、代码执行、网络浏览等子代理。

## 架构

DeerFlow 通过 Nginx 反向代理暴露两个 API 端面：

| 服务        | 直接端口 | 通过代理                        | 目的                          |
|-------------|----------|--------------------------------|------------------------------|
| Gateway API    | 8001     | `$DEERFLOW_GATEWAY_URL`          | REST 端点和嵌入式代理运行时 |
| LangGraph 兼容 API | 8001     | `$DEERFLOW_LANGGRAPH_URL`       | 代理线程、运行、流式传输   |

## 环境变量

所有 URL 都可以通过环境变量进行配置。**在发起任何请求之前，请阅读这些环境变量。**

| 变量                | 默认                                  | 描述                        |
|---------------------|--------------------------------------|-----------------------------|
| `DEERFLOW_URL`          | `http://localhost:2026`                  | 统一代理基础 URL             |
| `DEERFLOW_GATEWAY_URL`  | `${DEERFLOW_URL}`                        | Gateway API 基础（模型、技能、内存、上传） |
| `DEERFLOW_LANGGRAPH_URL`| `${DEERFLOW_URL}/api/langgraph`          | LangGraph API 基础（线程、运行） |

在发起 curl 调用时，始终按以下方式解析 URL：

```bash
# 从环境变量解析基础 URL（在发起任何 API 调用之前执行此操作）
DEERFLOW_URL="${DEERFLOW_URL:-http://localhost:2026}"
DEERFLOW_GATEWAY_URL="${DEERFLOW_GATEWAY_URL:-$DEERFLOW_URL}"
DEERFLOW_LANGGRAPH_URL="${DEERFLOW_LANGGRAPH_URL:-$DEERFLOW_URL/api/langgraph}"
```

## 可用操作

### 1. 健康检查

验证 DeerFlow 是否正在运行：

```bash
curl -s "$DEERFLOW_GATEWAY_URL/health"
```

### 2. 发送消息（流式传输）

这是主要操作。它创建一个线程并流式传输代理的响应。

**步骤 1：创建线程**

```bash
curl -s -X POST "$DEERFLOW_LANGGRAPH_URL/threads" \
  -H "Content-Type: application/json" \
  -d '{}'
```

响应：`{"thread_id": "<uuid>", ...}`

**步骤 2：流式传输运行**

```bash
curl -s -N -X POST "$DEERFLOW_LANGGRAPH_URL/threads/<thread_id>/runs/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_id": "lead_agent",
    "input": {
      "messages": [
        {
          "type": "human",
          "content": [{"type": "text", "text": "YOUR MESSAGE HERE"}]
        }
      ]
    },
    "stream_mode": ["values", "messages-tuple"],
    "stream_subgraphs": true,
    "config": {
      "recursion_limit": 1000
    },
    "context": {
      "thinking_enabled": true,
      "is_plan_mode": true,
      "subagent_enabled": true,
      "thread_id": "<thread_id>"
    }
  }'
```

响应是一个 SSE 流。每个事件具有以下格式：
```
event: <event_type>
data: <json_data>
```

关键事件类型：
- `metadata` — 运行元数据，包括 `run_id`
- `values` — 完整状态快照，包含 `messages` 数组
- `messages-tuple` — 增量消息更新（AI 文本片段、工具调用、工具结果）
- `end` — 流式传输完成

**上下文模式**（通过 `context` 设置）：
- 快速模式：`thinking_enabled: false, is_plan_mode: false, subagent_enabled: false`
- 标准模式：`thinking_enabled: true, is_plan_mode: false, subagent_enabled: false`
- 专业模式：`thinking_enabled: true, is_plan_mode: true, subagent_enabled: false`
- 超级模式：`thinking_enabled: true, is_plan_mode: true, subagent_enabled: true`

### 3. 继续对话

要发送后续消息，请重用步骤 2 中的 `thread_id` 并使用新消息再 POST 一个运行。

### 4. 列出模型

```bash
curl -s "$DEERFLOW_GATEWAY_URL/api/models"
```

返回：`{"models": [{"name": "...", "provider": "...", ...}, ...]}`

### 5. 列出技能

```bash
curl -s "$DEERFLOW_GATEWAY_URL/api/skills"
```

返回：`{"skills": [{"name": "...", "enabled": true, ...}, ...]}`

### 6. 启用/禁用技能

```bash
curl -s -X PUT "$DEERFLOW_GATEWAY_URL/api/skills/<skill_name>" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'
```

### 7. 列出代理

```bash
curl -s "$DEERFLOW_GATEWAY_URL/api/agents"
```

返回：`{"agents": [{"name": "...", ...}, ...]}`

### 8. 获取内存

```bash
curl -s "$DEERFLOW_GATEWAY_URL/api/memory"
```

返回用户上下文、事实和对话历史摘要。

### 9. 将文件上传到线程

```bash
curl -s -X POST "$DEERFLOW_GATEWAY_URL/api/threads/<thread_id>/uploads" \
  -F "files=@/path/to/file.pdf"
```

支持 PDF、PPTX、XLSX、DOCX — 自动转换为 Markdown。

### 10. 列出已上传文件

```bash
curl -s "$DEERFLOW_GATEWAY_URL/api/threads/<thread_id>/uploads/list"
```

### 11. 获取线程历史

```bash
curl -s "$DEERFLOW_LANGGRAPH_URL/threads/<thread_id>/history"
```

### 12. 列出线程

```bash
curl -s -X POST "$DEERFLOW_LANGGRAPH_URL/threads/search" \
  -H "Content-Type: application/json" \
  -d '{"limit": 20, "sort_by": "updated_at", "sort_order": "desc"}'
```

## 使用脚本

为发送消息并收集完整响应，请使用辅助脚本：

```bash
bash /path/to/skills/claude-to-deerflow/scripts/chat.sh "Your question here"
```

查看 `scripts/chat.sh` 了解实现。该脚本：
1. 检查健康状态
2. 创建线程
3. 流式传输运行并收集最终的 AI 响应
4. 打印结果

## 解析 SSE 输出

流返回 SSE 事件。要从 `values` 事件中提取最终的 AI 响应：
- 查找最后一个 `event: values` 块
- 解析其 `data` JSON
- `messages` 数组包含所有消息；最后一个 `type: "ai"` 的消息是响应
- 该消息的 `content` 字段是 AI 的文本回复

## 错误处理

- 如果健康检查失败，DeerFlow 未运行。通知用户需要启动它。
- 如果流返回错误事件，提取并显示错误消息。
- 常见问题：端口未打开、服务仍在启动中、配置错误。

## 小贴士

- 对于快速问题，使用快速模式（最快，无规划）。
- 对于研究任务，使用专业或超级模式（启用规划和子代理）。
- 您可以先上传文件，然后在消息中引用它们。
- 线程 ID 持久化 — 您可以稍后返回对话。
