# Power Automate via FlowStudio MCP — 基础

这项技能是**管道层**。它为 AI 代理提供了一种可靠的方式来与 FlowStudio MCP 服务器进行通信，发现可用的工具，并干净地处理响应。实际的工作流说明位于四个专门技能中，所有这些技能都构建在这个基础之上。

> **真实的调试示例**：[子工作流中的表达式错误](https://github.com/ninihen1/power-automate-mcp-skills/blob/main/examples/fix-expression-error.md) |
> [数据输入，不是工作流错误](https://github.com/ninihen1/power-automate-mcp-skills/blob/main/examples/data-not-flow.md) |
> [空值导致子工作流崩溃](https://github.com/ninihen1/power-automate-mcp-skills/blob/main/examples/null-child-flow.md)

> **要求**：一个 [FlowStudio](https://mcp.flowstudio.app) MCP 订阅（或兼容的 Power Automate MCP 服务器）。您需要：
> - MCP 端点：`https://mcp.flowstudio.app/mcp`（所有订阅者相同）
> - API 密钥 / JWT 令牌（`x-api-key` 头部——**不是** Bearer）
> - 在 ChatGPT 或 claude.ai 中没有密钥：将 `https://mcp.flowstudio.app/mcp/oauth` 添加为连接器，并使用 Microsoft 登录——参见
>   [ChatGPT 漫游指南](https://learn.flowstudio.app/chatgpt-power-automate)
> - Power Platform 环境名称（例如 `Default-<tenant-guid>`）

---

## 何时使用哪个技能

技能按**使用意图**组织，而不是按它们调用的工具。多个技能会重用相同的底层工具——根据用户试图完成的事情来选择。

| 用户想要… | 加载这个技能 |
|---|---|
| 创建或更改工作流（新建、修改现有、修复错误、部署） | **`flowstudio-power-automate-build`** |
| 诊断工作流失败的原因（对失败运行进行根本原因分析） | **`flowstudio-power-automate-debug`** |
| 查看租户范围的工作流健康状况、失败率、资产清单 | **`flowstudio-power-automate-monitoring`** *(Pro+)* |
| 标记、审计、分类、评分或下线工作流 | **`flowstudio-power-automate-governance`** *(Pro+)* |
| 仅连接、设置认证、编写辅助程序、解析响应 | 这个技能（基础） |

**相同的工具，不同的视角。** `flowstudio-power-automate-build` 和 `flowstudio-power-automate-debug`
都调用 `update_live_flow`、`get_live_flow` 和运行错误工具——它们在*方向*（正向 vs 反向）和*意图*（组合 vs 诊断）上有所不同。
`flowstudio-power-automate-monitoring` 和 `flowstudio-power-automate-governance` 都调用存储工具——它们在*受众*（运维 vs 合规）和*结果*（读取健康 vs 写入元数据）上有所不同。不要试图记住“哪些工具属于哪个技能”；根据用户正在做什么来选择技能。

---

## 真实来源

| 优先级 | 来源 | 覆盖范围 |
|----------|--------|--------|
| 1 | **真实的 API 响应** | 总是信任服务器实际返回的内容 |
| 2 | **`tool_search` / `list_skills`** | 权威的工具模式、参数名称、类型、必需标志 |
| 3 | **技能文档和参考文件** | 工作流说明、响应形状、非明显行为 |

如果文档与真实的 API 响应不一致，API 赢。这个技能（或任何其他技能）中的工具模式可能落后于服务器——在调用最近未使用的工具之前，调用 `tool_search` 来确认当前的形状。

---

## 代理如何发现工具

FlowStudio MCP 服务器（v1.1.5+）公开了两个**非计费**的元工具，让代理仅加载与当前任务相关的工具。优先使用这些工具，而不是 `tools/list`（一次性加载 30 多个模式）或猜测工具名称。

| 元工具 | 调用时机 |
|---|---|
| `list_skills` | 冷启动——查看可用的包（`build-flow`、`create-flow`、`debug-flow`、`monitor-flow`、`discover`、`governance`）并选择一个 |
| `tool_search` with `query: "skill:<name>"` | 加载一个包的完整模式集（例如 `skill:debug-flow`） |
| `tool_search` with `query: "select:tool1,tool2"` | 通过名称加载特定工具（例如跨包链接时） |
| `tool_search` with `query: "<keywords>"` | 用户请求不明确时的自由文本搜索（例如 `"cancel run"`） |

服务器的 `tool_search` 包有意**比这个技能系列更窄**——它们是每个意图最可能需要的工具的入门包。一个工作流技能（例如 `flowstudio-power-automate-debug`）可能会拉取一个包，然后在工作流进行过程中再次调用 `tool_search` 以获取更多工具。

```python
# 冷启动——根据意图选择一个包
skills = mcp("list_skills", {})
# [{"name": "debug-flow", "description": "调查工作流失败的原因...",
#   "tools": ["get_live_flow_runs", "get_live_flow_run_error", ...]}, ...]

# 加载包的模式
debug_tools = mcp("tool_search", {"query": "skill:debug-flow"})
```

当前常见的包：

| 包 | 使用时机 |
|---|---|
| `create-flow` | 创建全新的工作流；包括环境/连接发现、连接器描述、动态选项和 `update_live_flow` |
| `build-flow` | 读取或修改现有工作流定义 |
| `debug-flow` | 调查失败的运行和操作级输入/输出 |
| `monitor-flow` | 启动/停止、触发、取消或重新提交运行 |
| `discover` | 枚举环境、工作流和连接 |
| `governance` | Pro+ 缓存存储标记、maker 审计和元数据更新 |

---

## 推荐语言：Python 或 Node.js

这个技能系列中的所有示例都使用**Python 与 `urllib.request`**
(stdlib——不需要 `pip install`)。**Node.js** 是一个同样有效的选择：
`fetch` 从 Node 18+ 开始是内置的，JSON 处理是原生的，异步/等待与 MCP 工具调用的请求-响应模式完美映射——使其成为已经在 JavaScript/TypeScript 堆栈中工作的团队的天然选择。

| 语言 | 判定 | 备注 |
|---|---|---|
| **Python** | 推荐 | 干净的 JSON 处理，没有转义问题，所有技能示例都使用它 |
| **Node.js (≥ 18)** | 推荐 | 原生的 `fetch` + `JSON.stringify`/`JSON.parse`；不需要额外包 |
| PowerShell | 避免用于工作流操作 | `ConvertTo-Json -Depth` 默默截断嵌套定义；引号和转义会破坏复杂负载。仅适用于快速连接性测试，但不适用于构建或更新工作流。 |
| cURL / Bash | 可能但脆弱 | 壳转义嵌套 JSON 容易出错；没有原生的 JSON 解析器 |

> **TL;DR — 使用下面的核心 MCP 辅助程序（Python 或 Node.js）。** 两者都处理 JSON-RPC 框架、认证和响应解析，在一个可重用的函数中。

---

## 核心MCP辅助程序（Python）

在所有后续操作中使用此辅助程序：

```python
import json, urllib.request

TOKEN = "<YOUR_JWT_TOKEN>"
MCP   = "https://mcp.flowstudio.app/mcp"

def mcp(tool, args, cid=1):
    payload = {"jsonrpc": "2.0", "method": "tools/call", "id": cid,
               "params": {"name": tool, "arguments": args}}
    req = urllib.request.Request(MCP, data=json.dumps(payload).encode(),
        headers={"x-api-key": TOKEN, "Content-Type": "application/json",
                 "User-Agent": "FlowStudio-MCP/1.0"})
    try:
        resp = urllib.request.urlopen(req, timeout=120)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"MCP HTTP {e.code}: {body[:200]}") from e
    raw = json.loads(resp.read())
    if "error" in raw:
        raise RuntimeError(f"MCP 错误: {json.dumps(raw['error'])}")
    text = raw["result"]["content"][0]["text"]
    return json.loads(text)
```

> **常见的认证错误：**
> - HTTP 401/403 → 令牌缺失、过期或格式错误。从 [mcp.flowstudio.app](https://mcp.flowstudio.app) 获取新的 JWT。
> - HTTP 400 → JSON-RPC 负载格式错误。检查 `Content-Type: application/json` 和正文结构。
> - `MCP 错误: {"code": -32602, ...}` → 工具参数错误或缺失。调用 `tool_search` with `select:<toolname>` 确认模式。

---

## 核心MCP辅助程序（Node.js）

Node.js 18+ 的等效辅助程序（内置 `fetch`——不需要包）：

```js
const TOKEN = "<YOUR_JWT_TOKEN>";
const MCP   = "https://mcp.flowstudio.app/mcp";

async function mcp(tool, args, cid = 1) {
  const payload = {
    jsonrpc: "2.0",
    method: "tools/call",
    id: cid,
    params: { name: tool, arguments: args },
  };
  const res = await fetch(MCP, {
    method: "POST",
    headers: {
      "x-api-key": TOKEN,
      "Content-Type": "application/json",
      "User-Agent": "FlowStudio-MCP/1.0",
    },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`MCP HTTP ${res.status}: ${body.slice(0, 200)}`);
  }
  const raw = await res.json();
  if (raw.error) throw new Error(`MCP 错误: ${JSON.stringify(raw.error)}`);
  return JSON.parse(raw.result.content[0].text);
}
```

> 需要 Node.js 18+。对于旧版本的 Node，用 `https.request` 从 stdlib 替换 `fetch` 或安装 `node-fetch`。

---

## 验证连接

一个 3 行的烟雾测试，确认令牌、端点和辅助程序都正常工作：

```python
skills = mcp("list_skills", {})
print(f"连接成功——{len(skills)} 个技能包可用：",
      [s["name"] for s in skills])
```

预期输出：

```text
连接成功——6 个技能包可用： ['build-flow', 'create-flow', 'debug-flow', 'monitor-flow', 'discover', 'governance']
```

如果失败，请参阅上面的**常见认证错误**说明。如果成功，请转交给与用户意图匹配的工作流技能。

---

## 处理过大的响应

一些 MCP 工具响应的大小足以使代理的上下文窗口溢出：

| 工具 | 典型大小 | 原因 |
|---|---|---|
| `describe_live_connector` | 100-600 KB | 连接器的完整 Swagger 规范 |
| `get_live_dynamic_properties` | 50-500 KB | 动态连接器字段模式，例如 SharePoint 列 |
| `get_live_flow_run_action_outputs` (无 `actionName`) | 50 KB – 几 MB | 顶层操作输出；在 foreach 中有一个操作，每个重复都会返回 |
| `get_live_flow` (大型工作流) | 50-500 KB | 深度嵌套的分支 |
| `list_live_flows` (大型租户) | 50-200 KB | 数百个工作流记录 |

### 当辅助程序溢出到文件

代理辅助程序（Claude Code、VS Code Copilot 等）将过大的响应保存到临时文件（例如 `tool-results/mcp-flowstudio-describe_live_connector-NNNN.txt`）
并返回路径而不是内联 JSON。文件是**双重包装**的——外层的 MCP 封装加上内部的 JSON 转义负载：

```text
[{"type":"text","text":"<JSON-转义负载>"}]
```

需要两次解析才能得到可用的对象：

```python
import json
with open(path) as f:
    raw = json.loads(f.read())
payload = json.loads(raw[0]["text"])
```

```powershell
$payload = ((Get-Content $path -Raw | ConvertFrom-Json)[0].text) | ConvertFrom-Json
```

### 常规经验法则

1. **提取，不要回显。** 提取您需要的特定字段（一个 `operationId`、一个操作的输出），并在推理之前丢弃其余部分。
2. **始终向 `get_live_flow_run_action_outputs` 传递 `actionName`。** 省略它将获取所有顶层操作。对于 foreach 中的操作，传递 `actionName` 而不传递 `iterationIndex` 可以返回该操作的每个重复。
3. **在会话内重用溢出文件。** 再次获取相同的连接器 Swagger 会花费 30 多秒并产生另一个溢出——缓存路径。
4. **不要直接在溢出文件中用 grep JSON 键。** 字符串在文件内是 JSON 转义的（`\"OperationId\":`），所以一个简单的 grep `"OperationId":` 将不会匹配。先解析，再过滤。
5. **向用户总结工具输出。** 回显 `name + state + trigger` 用于工作列表和 `actionName + status + code` 用于运行错误——不是原始 JSON，除非被要求。

```python
# 好——在连接器 Swagger 中钻取一个操作
conn = mcp("describe_live_connector", {"environmentName": ENV, "connectorName": "shared_sharepointonline"})
op = conn["properties"]["swagger"]["paths"]["/datasets/{dataset}/tables/{table}/items"]["get"]
print(op["operationId"], "—", op.get("summary"))

# 坏——将整个 500 KB 的 swagger 保留在上下文中
print(json.dumps(conn, indent=2))   # 不要这样做
```

---

## 认证和连接说明

| 字段 | 值 |
|---|---|
| 认证头部 | `x-api-key: <JWT>`——**不是** `Authorization: Bearer` |
| 令牌格式 | 普通的 JWT——不要剥离、修改或前缀它 |
| 超时 | 对于 `get_live_flow_run_action_outputs`（大型输出）使用 ≥ 120 s |
| 环境名称 | `Default-<tenant-guid>`（通过 `list_live_environments` 或 `list_live_flows` 响应找到） |

---

## 参考文件

- [MCP-BOOTSTRAP.md](references/MCP-BOOTSTRAP.md) — 端点、认证、请求/响应格式（先读这个）
- [tool-reference.md](references/tool-reference.md) — 响应形状和行为说明（参数在 `tool_search` 中）
- [action-types.md](references/action-types.md) — Power Automate 操作类型模式
- [connection-references.md](references/connection-references.md) — 连接器参考指南
