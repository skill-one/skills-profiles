# 使用 FlowStudio MCP 构建 & 部署 Power Automate 流

通过 FlowStudio MCP 服务器以编程方式逐步构建和部署 Power Automate 云流。

**前提条件**：必须可以访问 FlowStudio MCP 服务器并具有有效的 JWT。
有关连接设置，请参阅 `flowstudio-power-automate-mcp` 技能。
在 https://mcp.flowstudio.app 订阅

工作流：
1.  加载当前构建工具。
2.  检查是否存在现有流。
3.  解析连接引用。
4.  构建定义。
5.  部署。
6.  验证。
7.  测试。

---

## 真实情况来源

> **始终首先调用 `list_skills` / `tool_search`** 以确认可用的工具名称和参数模式。
> 工具名称和参数可能在服务器版本之间发生变化。
> 此技能涵盖响应形状、行为说明和构建模式——工具模式无法告诉你的事情。
> 如果本文档与 `tool_search` 或实际 API 响应不一致，则 API 优先。

---

## Python 助手

```python
import json, urllib.request

MCP_URL   = "https://mcp.flowstudio.app/mcp"
MCP_TOKEN = "<YOUR_JWT_TOKEN>"

def mcp(tool, **kwargs):
    payload = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                          "params": {"name": tool, "arguments": kwargs}}).encode()
    req = urllib.request.Request(MCP_URL, data=payload,
        headers={"x-api-key": MCP_TOKEN, "Content-Type": "application/json",
                 "User-Agent": "FlowStudio-MCP/1.0"})
    try:
        resp = urllib.request.urlopen(req, timeout=120)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"MCP HTTP {e.code}: {body[:200]}") from e
    raw = json.loads(resp.read())
    if "error" in raw:
        raise RuntimeError(f"MCP 错误: {json.dumps(raw['error'])}")
    return json.loads(raw["result"]["content"][0]["text"])

ENV = "<environment-id>"  # 例如 Default-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

---

## 0. 加载当前构建工具

对于全新的流，加载服务器的 `create-flow` 套件。对于编辑现有流，加载 `build-flow`。
这使代理与 MCP 服务器的当前模式保持一致，然后再构建 JSON。

```python
schemas = mcp("tool_search", query="skill:create-flow")
# 包括 list_live_environments, list_live_connections,
# describe_live_connector, get_live_dynamic_options, update_live_flow.
```

如果您需要套件之外的工具，请显式加载它：

```python
mcp("tool_search", query="select:get_live_dynamic_properties")
```

---

## 1. 安全检查：流是否已存在？

在构建之前始终查看以避免重复：

```python
results = mcp("list_live_flows",
    environmentName=ENV,
    mode="owner",
    search="My New Flow",
    top=20)

# list_live_flows 返回 { "flows": [...], "mode": "...", ... }
matches = [f for f in results["flows"]
           if "My New Flow".lower() in f["displayName"].lower()]

if len(matches) > 0:
    # 流存在——修改而不是创建
    FLOW_ID = matches[0]["id"]   # list_live_flows 中的纯 UUID
    print(f"现有流: {FLOW_ID}")
    defn = mcp("get_live_flow", environmentName=ENV, flowName=FLOW_ID)
else:
    print("未找到流——从头开始构建")
    FLOW_ID = None
```

对于非常大的环境，`list_live_flows` 可能会返回一个续接 URL。
将其作为 `continuationUrl` 与相同的 `mode` 一起传递以检索下一批。
仅在用户需要所有环境流并且 MCP 身份具有管理员权限时使用 `mode="admin"`。

---

## 2. 获取连接引用

每个连接器操作都需要一个指向流 `connectionReferences` 映射中键的 `connectionName`。
该键链接到环境中经过身份验证的连接。

> **强制要求**：您**必须**首先调用 `list_live_connections`——**不要**要求用户提供连接名称或 GUID。
> API 返回您需要的确切值。
> 只有当 API 确认所需连接缺失时，才提示用户。

### 2a — 查找活动连接

```python
conns = mcp("list_live_connections", environmentName=ENV)
active = [c for c in conns["connections"]
          if c["statuses"][0]["status"] == "Connected"]
conn_map = {c["connectorName"]: c["id"] for c in active}
```

对于已知的连接器，传递 `search` 以减少输出并获取可粘贴的 `connectionReferenceTemplate` 和 `hostTemplate` 值：

```python
sp_conns = mcp("list_live_connections",
    environmentName=ENV,
    search="shared_sharepointonline")
```

### 2b — 确定流需要哪些连接器

常见连接器 API 名称：SharePoint `shared_sharepointonline`，Outlook `shared_office365`，Teams `shared_teams`，Approvals `shared_approvals`，OneDrive `shared_onedriveforbusiness`，Excel `shared_excelonlinebusiness`，Dataverse `shared_commondataserviceforapps`，Forms `shared_microsoftforms`。

不需要连接器的流（例如 Recurrence + Compose + HTTP 仅），可以省略 `connectionReferences`。

### 2c — 如果连接缺失，指导用户

```python
connectors_needed = ["shared_sharepointonline", "shared_office365"]  # 根据流调整
missing = [c for c in connectors_needed if c not in conn_map]
if missing:
    # 停止：连接需要浏览器 OAuth 同意。
    # 要求用户在选定环境中创建缺失的连接器连接，然后重新运行 list_live_connections。
    raise Exception(f"缺失活动连接: {missing}")
```

### 2d — 构建连接引用块

```python
connection_references = {}
host_templates = {}
for connector in connectors_needed:
    c = next(c for c in active if c["connectorName"] == connector)
    connection_references[connector] = c.get("connectionReferenceTemplate") or {
        "connectionName": c["id"],   # list_live_connections 中的连接 ID
        "source": "Invoker",
        "id": f"/providers/Microsoft.PowerApps/apis/{connector}"
    }
    host_templates[connector] = c.get("hostTemplate") or {
        "connectionName": connector
    }
```

在 Step 3 动作 JSON 中，`inputs.host.connectionName` 必须是映射键，例如 `shared_teams`，而不是 GUID。
GUID 仅属于 `connectionReferences[connector].connectionName` 值内部。
如果现有流使用相同的连接器，您也可以从 `get_live_flow` 复制其 `properties.connectionReferences`。

---

## 3. 构建 流定义

构建定义对象。有关完整模式，请参阅 [flow-schema.md](references/flow-schema.md)；
有关这些动作模式参考（用于复制粘贴模板）：
- [action-patterns-core.md](references/action-patterns-core.md) — 变量、控制流、表达式
- [action-patterns-data.md](references/action-patterns-data.md) — 数组转换、HTTP、解析
- [action-patterns-connectors.md](references/action-patterns-connectors.md) — SharePoint、Outlook、Teams、Approvals

```python
definition = {
    "$schema": "https://schema.management.azure.com/providers/Microsoft.Logic/schemas/2016-06-01/workflowdefinition.json#",
    "contentVersion": "1.0.0.0",
    "triggers": { ... },   # see trigger-types.md / build-patterns.md
    "actions": { ... }     # see ACTION-PATTERNS-*.md / build-patterns.md
}
```

> 有关完整、可直接使用的流定义，请参阅 [build-patterns.md](references/build-patterns.md)，涵盖 Recurrence+SharePoint+Teams、HTTP 触发器等。

### 在猜测 JSON 之前发现连接器操作

对于基于连接器的触发器/操作，请优先使用实时连接器描述器而不是手动编写的形状。
它可以返回编写的提示、规范示例、变体键、输入/输出和动态元数据指针。

```python
# 当您知道用户的意图但不知道 API 时，跨连接器搜索。
matches = mcp("describe_live_connector",
    environmentName=ENV,
    search="发送电子邮件",
    top=5)

# 在复制示例定义之前描述特定操作。
op = mcp("describe_live_connector",
    environmentName=ENV,
    connectorName="shared_office365",
    operationId="SendEmailV2")
print(op.get("hint"))
```

当操作有多个编写的变体时，请求流需要的变体：

```python
teams_chat = mcp("describe_live_connector",
    environmentName=ENV,
    connectorName="shared_teams",
    operationId="PostMessageToConversation",
    variant="flowbot_chat")
```

当操作描述说参数具有动态选项或动态属性时，调用指示的下一个工具：

```python
sp_op = mcp("describe_live_connector",
    environmentName=ENV,
    connectorName="shared_sharepointonline",
    operationId="GetItems")

sites = mcp("get_live_dynamic_options",
    environmentName=ENV,
    connectorName="shared_sharepointonline",
    connectionName=conn_map["shared_sharepointonline"],
    operationId="GetItems",
    parameterName="dataset",
    dynamicMetadata=sp_op["dynamicParameters"]["dataset"])

fields = mcp("get_live_dynamic_properties",
    environmentName=ENV,
    connectorName="shared_sharepointonline",
    connectionName=conn_map["shared_sharepointonline"],
    operationId="GetItems",
    parameterName="item",
    parameters={"dataset": "<site-url>", "table": "<list-id>"},
    dynamicMetadata=sp_op["dynamicProperties"]["item"])
```

使用动态选项用于下拉 ID，例如 SharePoint 站点/列表和 Teams 团队/频道。
使用动态属性用于模式/字段形状，例如 SharePoint 列表项列。

---

## 4. 部署（创建或更新）

`update_live_flow` 使用单个工具处理创建和更新。

### 创建新流（无现有流）

省略 `flowName`——服务器将生成新的 GUID 并通过 PUT 创建：

```python
definition["description"] = "每周 SharePoint → Teams 通知流，由代理构建"

result = mcp("update_live_flow",
    environmentName=ENV,
    # flowName 省略 → 创建新流
    definition=definition,
    connectionReferences=connection_references,
    displayName="Overdue Invoice Notifications"
)

if result.get("error") is not None:
    print("创建失败:", result["error"])
else:
    # 捕获新流 ID 以供后续步骤使用
    FLOW_ID = result["created"]
    print(f"✅ 流创建: {FLOW_ID}")
```

### 更新现有流

提供 `flowName` 以 PATCH：

```python
definition["description"] = (
    "由代理更新于 " + __import__('datetime').datetime.utcnow().isoformat()
)

result = mcp("update_live_flow",
    environmentName=ENV,
    flowName=FLOW_ID,
    definition=definition,
    connectionReferences=connection_references,
    displayName="My Updated Flow"
)

if result.get("error") is not None:
    print("更新失败:", result["error"])
else:
    print("更新成功:", result)
```

> ⚠️ `update_live_flow` 始终返回 `error` 键。
> `null`（Python `None`）表示成功——不要将键的存在视为失败。
>
> ⚠️ 流描述位于 `definition["description"]`。当前服务器会追加 `#flowstudio-mcp` 以用于使用跟踪。
> 除非 `tool_search` 在活动模式中显示，否则不要传递顶级 `description` 参数。

### 常见部署错误

| 错误消息（包含） | 原因 | 解决方法 |
|---|---|---|
| `missing from connectionReferences` | 动作的 `host.connectionName` 引用映射中不存在的键 | 确保 `host.connectionName` 使用映射的**键**（例如 `shared_teams`），而不是原始 GUID |
| `ConnectionAuthorizationFailed` / 403 | 连接 GUID 属于另一个用户或未授权 | 重新运行 Step 2a 并使用当前 `x-api-key` 用户拥有的连接 |
| `InvalidTemplate` / `InvalidDefinition` | 定义 JSON 中的语法错误 | 检查 `runAfter` 链、表达式语法和动作类型拼写 |
| `ConnectionNotConfigured` | 连接器操作存在，但连接 GUID 无效或过期 | 重新检查 `list_live_connections` 以获取新的 GUID |

---

## 5. 验证部署

```python
check = mcp("get_live_flow", environmentName=ENV, flowName=FLOW_ID)

# 确认状态
print("状态:", check["properties"]["state"])  # 应该是 "Started"
# 如果状态是 "Stopped"，使用 set_live_flow_state——**不要**使用 update_live_flow
# mcp("set_live_flow_state", environmentName=ENV, flowName=FLOW_ID, state="Started")

# 确认我们添加的动作存在
acts = check["properties"]["definition"]["actions"]
print("动作:", list(acts.keys()))
```

---

## 6. 测试流

> **强制要求**：在触发任何测试运行之前，**必须要求用户确认**。
> 运行流会产生实际副作用——它可能会发送电子邮件、发布 Teams 消息、写入 SharePoint、启动审批或调用外部 API。
> 解释流将做什么，并在调用 `trigger_live_flow` 或 `resubmit_live_flow_run` 之前等待明确的批准。

### 已有先运行更新的流（任何触发类型）

> **首先使用 `resubmit_live_flow_run`。** 它适用于**所有**触发类型——Recurrence、SharePoint、连接器 webhook、Button 和 HTTP。
> 它重放原始触发负载。**不要**要求用户手动触发流或等待下一个计划运行。

```python
runs = mcp("get_live_flow_runs", environmentName=ENV, flowName=FLOW_ID, top=1)
if runs:
    # 适用于 Recurrence、SharePoint、连接器触发器——不仅仅是 HTTP
    result = mcp("resubmit_live_flow_run",
        environmentName=ENV, flowName=FLOW_ID, runName=runs[0]["name"])
    print(result)   # {"resubmitted": true, "triggerName": "..."}
```

### HTTP、Button 和 PowerApps 流——自定义测试负载

仅当您需要发送**不同**于原始运行的负载时，才使用 `trigger_live_flow`。
对于验证修复，`resubmit_live_flow_run` 更好，因为它使用导致失败的精确数据。

```python
defn = mcp("get_live_flow", environmentName=ENV, flowName=FLOW_ID)
triggers = defn["properties"]["definition"]["triggers"]
manual = next(iter(triggers.values()))
print("预期负载:", manual.get("inputs", {}).get("schema"))

result = mcp("trigger_live_flow",
    environmentName=ENV, flowName=FLOW_ID,
    body={"name": "Test", "value": 1})
print(f"状态: {result['responseStatus']}, 通过: {result['invocation']}")
print(result.get("warning"))   # 设置时缺少必需输入：运行仍然继续，使用 null
```

### 全新非 HTTP 流

全新的 **Recurrence** 流不需要任何解决方法：部署它，然后立即使用 `trigger_live_flow` 并不带 `body`——与门户的“运行流”按钮相同。
会拒绝 `body`；计划触发器不接受输入。

全新的 **连接器触发**流（SharePoint、webhooks）没有先运行，并且在没有真实源事件的情况下无法触发。
使用临时 HTTP 触发器部署，测试操作，然后切换到生产触发器：

```python
production_trigger = definition["triggers"]
definition["triggers"] = {
    "manual": {"type": "Request", "kind": "Http", "inputs": {"schema": {}}}
}
result = mcp("update_live_flow", environmentName=ENV,
    flowName=FLOW_ID,       # 如果创建新流则省略
    definition=definition, connectionReferences=connection_references,
    displayName="Overdue Invoice Notifications")
FLOW_ID = FLOW_ID or result["flowName"]

mcp("trigger_live_flow", environmentName=ENV, flowName=FLOW_ID,
    body={"sample": "payload"})
runs = mcp("get_live_flow_runs", environmentName=ENV, flowName=FLOW_ID, top=1)
if runs[0]["status"] == "Failed":
    err = mcp("get_live_flow_run_error",
        environmentName=ENV, flowName=FLOW_ID, runName=runs[0]["name"])
    raise Exception(err["failedActions"][-1])

definition["triggers"] = production_trigger
mcp("update_live_flow", environmentName=ENV, flowName=FLOW_ID,
    definition=definition, connectionReferences=connection_references)
```

触发器只是入口点；通过 HTTP 测试仍然执行相同的操作。
如果操作使用 `triggerBody()` 或 `triggerOutputs()`，请传递与生产触发器负载形状相似的 `body`。

---

## 注意事项

| 错误 | 后果 | 预防 |
|---|---|---|
| 缺失 `connectionReferences` 在部署 | 400 "Supply connectionReferences" | 始终首先调用 `list_live_connections` |
| `"operationOptions"` 缺失在 Foreach | 并行执行、写入时的竞争条件 | 始终添加 `"Sequential"` |
| `union(old_data, new_data)` | 旧值覆盖新（先胜） | 使用 `union(new_data, old_data)` |
| `split()` 在可能为空的字符串上 | `InvalidTemplate` 崩溃 | 用 `coalesce(field, '')` 包装 |
| 检查 `result["error"]` 存在 | 始终存在；`!= null` 为真错误 | 使用 `result.get("error") is not None` |
| 流部署但状态为 "Stopped" | 流不会按计划运行 | 调用 `set_live_flow_state` 并使用 `state: "Started"`——**不要**使用 `update_live_flow` 进行状态更改 |
| Teams "Chat with Flow bot" 接收者为对象 | 400 `GraphUserDetailNotFound` | 使用带尾随分号的纯字符串（见下文） |
| Copilot/Skills 流不在解决方案中 | Copilot Studio 可能不会将其发现为代理工具 | 部署后，调用 `add_live_flow_to_solution` 并使用目标 `solutionId` |
| Button/Skills 触发器用于 MCP 测试 | 即使缺少必需输入也会运行 | 在 `trigger_live_flow` `body` 中传递输入；在 `warning` 时，取消并重试完整 body |
| 连接器操作缺失 `metadata.operationMetadataId` | 设计器/仅运行 UI 可能表现不一致 | 保留现有 ID；为新的连接器操作添加稳定的 GUID |
| 占位符 Excel `scriptId` | 保存时动态验证失败 | 在部署前解析真实的 Office Script ID |
| SharePoint `PatchItem` 省略必需字段 | 即使字段未更改，保存也可能失败 | 回显未更改的必需字段，例如 `item/Title` |
| Copilot Studio 连接器调用草稿代理 | 连接器调用可能失败或命中陈旧行为 | 在测试/重提交流之前发布代理 |

### Teams `PostMessageToConversation` — 接收者格式

`body/recipient` 参数的格式取决于 `location` 值：

| Location | `body/recipient` 格式 | 示例 |
|---|---|---|
| **Chat with Flow bot** | 带尾随分号的纯电子邮件字符串 | `"user@contoso.com;"` |
| **Channel** | 具有 `groupId` 和 `channelId` 的对象 | `{"groupId": "...", "channelId": "..."}` |

> **常见错误**：传递 `{"to": "user@contoso.com"}` 用于 "Chat with Flow bot" 返回 400 `GraphUserDetailNotFound` 错误。
> API 期望纯字符串。

---

## 参考文件

- [flow-schema.md](references/flow-schema.md) — 完整流定义 JSON 模式
- [trigger-types.md](references/trigger-types.md) — 触发器类型模板
- [action-patterns-core.md](references/action-patterns-core.md) — 变量、控制流、表达式
- [action-patterns-data.md](references/action-patterns-data.md) — 数组转换、HTTP、解析
- [action-patterns-connectors.md](references/action-patterns-connectors.md) — SharePoint、Outlook、Teams、Approvals
- [build-patterns.md](references/build-patterns.md) — 完整流定义模板（Recurrence+SP+Teams、HTTP 触发器）

## 相关技能

- `flowstudio-power-automate-mcp` — 核心连接设置和工具参考
- `flowstudio-power-automate-debug` — 部署后调试失败流
