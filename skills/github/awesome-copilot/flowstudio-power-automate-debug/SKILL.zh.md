---
name: flowstudio-power-automate-debug
description: 使用 FlowStudio MCP 服务器调试失败的 Power Automate 云流程。Graph API 仅显示顶层状态代码。此技能为您提供操作级别的输入和输出，以找到实际的根本原因。当被要求：调试流程、调查失败运行、此流程为何失败、检查操作输出、找到流程错误的根本原因、修复损坏的 Power Automate 流程、诊断超时、追踪 DynamicOperationRequestFailure、检查连接器认证错误、从运行中读取错误详情或排查表达式失败时，请加载此技能。需要 FlowStudio MCP 订阅 — 请参阅 https://mcp.flowstudio.app
---

# 使用 FlowStudio MCP 调试 Power Automate

通过 FlowStudio MCP 服务器，对失败的 Power Automate 云流进行逐步诊断的过程。

> **实际调试示例**：[子流中的表达式错误](https://github.com/ninihen1/power-automate-mcp-skills/blob/main/examples/fix-expression-error.md) |
> [数据输入，非流错误](https://github.com/ninihen1/power-automate-mcp-skills/blob/main/examples/data-not-flow.md) |
> [空值导致子流崩溃](https://github.com/ninihen1/power-automate-mcp-skills/blob/main/examples/null-child-flow.md)

**前提条件**：必须可以访问 FlowStudio MCP 服务器，并具有有效的 JWT。有关连接设置，请参阅 `flowstudio-power-automate-mcp` 技能。在 https://mcp.flowstudio.app 订阅。

---

## 真实数据源

> **始终首先调用 `list_skills` / `tool_search`** 来确认可用的工具名称和参数模式。工具名称和参数可能在服务器版本之间发生变化。
> 此技能涵盖响应形状、行为说明和诊断模式——这些都是工具模式无法告诉你的信息。如果本文档与 `tool_search` 或实际 API 响应不一致，则 API 优先。

---

## Python 辅助工具

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

ENV = "<environment-id>"   # 例如：Default-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

---

## 第 1 步 — 定位流

```python
result = mcp("list_live_flows", environmentName=ENV)
# 返回一个包装对象：{mode, flows, totalCount, error}
target = next(f for f in result["flows"] if "My Flow Name" in f["displayName"])
FLOW_ID = target["id"]   # 纯 UUID —— 直接作为 flowName 使用
print(FLOW_ID)
```

---

## 第 2 步 — 查找失败的运行

```python
runs = mcp("get_live_flow_runs", environmentName=ENV, flowName=FLOW_ID, top=5)
# 返回直接数组（最新优先）：
# [{"name": "08584296068667933411438594643CU15",
#   "status": "Failed",
#   "startTime": "2026-02-25T06:13:38.6910688Z",
#   "endTime": "2026-02-25T06:15:24.1995008Z",
#   "triggerName": "manual",
#   "error": {"code": "ActionFailed", "message": "An action failed..."}},
#  {"name": "...", "status": "Succeeded", "error": null, ...}]

for r in runs:
    print(r["name"], r["status"], r["startTime"])

RUN_ID = next(r["name"] for r in runs if r["status"] == "Failed")
```

---

## 第 3 步 — 获取顶层错误

> **关键**：`get_live_flow_run_error` 告诉你**哪个**操作失败了。
> `get_live_flow_run_action_outputs` 告诉你**为什么**。你必须调用**两者**。
> 不要单独停留在错误上——错误代码如 `ActionFailed`、`NotSpecified` 和 `InternalServerError` 是通用包装器。实际根本原因（错误字段、空值、HTTP 500 正文、堆栈跟踪）仅在操作的输入和输出中可见。

```python
err = mcp("get_live_flow_run_error",
    environmentName=ENV, flowName=FLOW_ID, runName=RUN_ID)
# 返回：
# {
#   "runName": "08584296068667933411438594643CU15",
#   "failedActions": [
#     {"actionName": "Apply_to_each_prepare_workers", "status": "Failed",
#      "error": {"code": "ActionFailed", "message": "An action failed..."},
#      "startTime": "...", "endTime": "..."},
#     {"actionName": "HTTP_find_AD_User_by_Name", "status": "Failed",
#      "code": "NotSpecified", "startTime": "...", "endTime": "..."}
#   ],
#   "allActions": [
#     {"actionName": "Apply_to_each", "status": "Skipped"},
#     {"actionName": "Compose_WeekEnd", "status": "Succeeded"},
#     ...
#   ]
# }

# failedActions 按外到内排序。根本原因是最后一个条目：
root = err["failedActions"][-1]
print(f"根本操作：{root['actionName']} → 代码：{root.get('code')}")

# allActions 显示每个操作的状态——用于识别被跳过的操作
# 查看 common-errors.md 解码错误代码。
```

---

## 第 4 步 — 检查失败操作的输入和输出

> **这是最重要的步骤。** `get_live_flow_run_error` 仅给你一个通用错误代码。实际错误详情——HTTP 状态代码、响应正文、堆栈跟踪、空值——存在于操作的运行时输入和输出中。**在识别出失败操作后立即检查它。**

```python
# 获取根本失败操作的完整输入和输出
root_action = err["failedActions"][-1]["actionName"]
detail = mcp("get_live_flow_run_action_outputs",
    environmentName=ENV,
    flowName=FLOW_ID,
    runName=RUN_ID,
    actionName=root_action)

if len(detail) > 1:
    print(f"{root_action} 返回了 {len(detail)} 次重复；检查迭代索引")
out = detail[0] if detail else {}
print(f"操作：{out.get('actionName')}")
print(f"状态：{out.get('status')}")

# 对于 HTTP 操作，真实错误在 outputs.body
if isinstance(out.get("outputs"), dict):
    status_code = out["outputs"].get("statusCode")
    body = out["outputs"].get("body", {})
    print(f"HTTP {status_code}")
    print(json.dumps(body, indent=2)[:500])

    # 错误正文通常是嵌套的 JSON 字符串——解析它们
    if isinstance(body, dict) and "error" in body:
        err_detail = body["error"]
        if isinstance(err_detail, str):
            err_detail = json.loads(err_detail)
        print(f"错误：{err_detail.get('message', err_detail)}")

# 对于表达式错误，错误在 error 字段
if out.get("error"):
    print(f"错误：{out['error']}")

# 也检查输入——它们显示使用的是表达式/URL/正文
if out.get("inputs"):
    print(f"输入：{json.dumps(out['inputs'], indent=2)[:500]}")
```

### 操作输出揭示的内容（错误代码无法揭示）

| `get_live_flow_run_error` 的错误代码 | `get_live_flow_run_action_outputs` 揭示的内容 |
|---|---|
| `ActionFailed` | 实际失败的嵌套操作及其 HTTP 响应 |
| `NotSpecified` | HTTP 状态代码 + 带有真实错误的响应正文 |
| `InternalServerError` | 服务器错误消息、堆栈跟踪或 API 错误 JSON |
| `InvalidTemplate` | 失败的确切表达式和空值/错误类型的值 |
| `BadRequest` | 发送了请求正文以及服务器拒绝它的原因 |

### Foreach 迭代

当 `actionName` 引用 foreach 内部的操作时，输出工具可以返回该操作的每个重复。每个项目可能包括 `repetitionIndexes`，其中包含循环名称和从零开始的 `itemIndex`。使用 `iterationIndex` 在找到可疑项目后检查一个迭代：

```python
all_reps = mcp("get_live_flow_run_action_outputs",
    environmentName=ENV,
    flowName=FLOW_ID,
    runName=RUN_ID,
    actionName=root_action)

for rep in all_reps[:10]:
    print(rep.get("repetitionIndexes"), rep.get("status"), rep.get("error"))

one_rep = mcp("get_live_flow_run_action_outputs",
    environmentName=ENV,
    flowName=FLOW_ID,
    runName=RUN_ID,
    actionName=root_action,
    iterationIndex=3)
```

### Evidence Compose Bookends

对于不确定的连接器工作，在风险操作之前添加 `Compose_*_Request`，在风险操作之后添加 `Compose_*_Result`，并允许结果操作在 `Succeeded` 和 `Failed` 上都出现。这为未来的调试提供了一个干净的负载快照，而无需重新部署。不要在这些书签中包含秘密或长二进制负载。

### 示例：返回 500 的 HTTP 操作

```
错误代码："InternalServerError" ← 这告诉你什么

操作输出揭示：
  HTTP 500
  正文：{"error": "Cannot read properties of undefined (reading 'toLowerCase')
    at getClientParamsFromConnectionString (storage.js:20)"}
  ← 这告诉你 Azure Function 因连接字符串未定义而崩溃
```

### 示例：空值上的表达式错误

```
错误代码："BadRequest" ← 通用

操作输出揭示：
  输入："body('HTTP_GetTokenFromStore')?['token']?['access_token']"
  输出：""   ← 空字符串，路径解析为 null
  ← 这告诉你响应形状已更改——token 在 body.access_token，而不是 body.token.access_token
```

---

## 第 5 步 — 读取流定义

```python
defn = mcp("get_live_flow", environmentName=ENV, flowName=FLOW_ID)
actions = defn["properties"]["definition"]["actions"]
print(list(actions.keys()))
```

在定义中找到失败的操作。检查其 `inputs` 表达式以了解它期望什么数据。

---

## 第 6 步 — 从失败处回溯

当失败操作的输入引用上游操作时，也要检查这些操作。通过链路向后跟踪，直到找到坏数据的来源：

```python
# 检查导致失败的多个操作
for action_name in [root_action, "Compose_WeekEnd", "HTTP_Get_Data"]:
    result = mcp("get_live_flow_run_action_outputs",
        environmentName=ENV,
        flowName=FLOW_ID,
        runName=RUN_ID,
        actionName=action_name)
    out = result[0] if result else {}
    print(f"\n--- {action_name} ({out.get('status')}) ---")
    print(f"输入：  {json.dumps(out.get('inputs', ''), indent=2)[:300]}")
    print(f"输出： {json.dumps(out.get('outputs', ''), indent=2)[:300]}")
```

> ⚠️ 数组处理操作的输出负载可能非常大。
> 始终切片（例如 `[:500]`）后再打印。

> **提示**：当不确定哪个操作产生了坏数据时，省略 `actionName` 以列出顶层操作。一旦你选择了一个 foreach 内部的操作，传递 `iterationIndex` 以避免将每个重复项拉入上下文中。

---

## 第 7 步 — 精确定位根本原因

### 表达式错误（例如 `split` 在 null 上）
如果错误提到 `InvalidTemplate` 或函数名称：
1. 在定义中找到该操作
2. 检查它读取的 upstream 操作/表达式
3. **检查该 upstream 操作的输出**以查找 null / 缺失字段

```python
# 示例：操作使用 split(item()?['Name'], ' ')
# → 源数据中的 null Name
result = mcp("get_live_flow_run_action_outputs", ..., actionName="Compose_Names")
if not result:
    print("没有返回 Compose_Names 的输出")
    names = []
else:
    names = result[0].get("outputs", {}).get("body") or []
nulls = [x for x in names if x.get("Name") is None]
print(f"{len(nulls)} 条记录 Name 为 null")
```

### 错误的字段路径
表达式 `triggerBody()?['fieldName']` 返回 null → `fieldName` 错误。
**检查触发器输出**以查看实际字段名称：
```python
result = mcp("get_live_flow_run_action_outputs", ..., actionName="<trigger-action-name>")
print(json.dumps(result[0].get("outputs"), indent=2)[:500])
```

### 返回错误的 HTTP 操作
错误代码说 `InternalServerError` 或 `NotSpecified` — **始终检查操作输出**以获取实际 HTTP 状态和响应正文：
```python
result = mcp("get_live_flow_run_action_outputs", ..., actionName="HTTP_Get_Data")
out = result[0]
print(f"HTTP {out['outputs']['statusCode']}")
print(json.dumps(out['outputs']['body'], indent=2)[:500])
```

### 连接/身份验证失败
查找 `ConnectionAuthorizationFailed` — 连接所有者必须与服务帐户运行流匹配。无法通过 API 修复；在 PA 设计器中修复。

### Outlook 用户选择器失败（`DynamicListValuesUndefinedOrInvalid`）
Outlook 操作如 `GetEmailsV3` 使用参数（`mailboxAddress`、`to`、`cc`、`from`），其下拉菜单由 `builtInOperation:AadGraph.GetUsers` 支持——它在 PA 列表枚举层已损坏，始终返回 `DynamicListValuesUndefinedOrInvalid`。这会在代理重建或修改 Outlook 操作时通过 `update_live_flow` 尝试解析用户通过动态选项时出现。**不要通过重试 AadGraph** 来修复它——改用 `shared_office365users.SearchUserV2`（返回相同的 AAD 用户形状）。使用 `describe_live_connector` 确认受影响的参数是否暴露了结构化的 `fallback`，然后针对 `shared_office365users.SearchUserV2` 而不是损坏的 AadGraph 操作调用 `get_live_dynamic_options`。对于动态字段模式而不是下拉选项，使用 `get_live_dynamic_properties` 并使用 `describe_live_connector` 返回的元数据。

---

## 第 8 步 — 应用修复

**对于表达式/数据问题**：
```python
defn = mcp("get_live_flow", environmentName=ENV, flowName=FLOW_ID)
acts = defn["properties"]["definition"]["actions"]

# 示例：修复对可能为 null 的 Name 的 split
acts["Compose_Names"]["inputs"] = \
    "@coalesce(item()?['Name'], 'Unknown')"

conn_refs = defn["properties"]["connectionReferences"]
result = mcp("update_live_flow",
    environmentName=ENV,
    flowName=FLOW_ID,
    definition=defn["properties"]["definition"],
    connectionReferences=conn_refs)

print(result.get("error"))  # None = 成功
```

> ⚠️ `update_live_flow` 始终返回一个 `error` 键。
> 值为 `null`（Python `None`）表示成功。

---

## 第 9 步 — 验证修复

> **使用 `resubmit_live_flow_run` 测试任何流——而不仅仅是 HTTP 触发器。**
> `resubmit_live_flow_run` 使用其原始触发器负载重放先前的运行。这对**每种触发类型**都有效：递归、SharePoint "当创建项目时"、"连接器 webhook"、"按钮触发器"和 HTTP 触发器。你**不需要**要求用户手动触发流或等待下一个计划运行。
>
> 只有在**全新且从未运行过的流**的情况下，`resubmit` 才不可用——它没有先前的运行可以重放。

```python
# 重放失败的运行——适用于任何触发类型
resubmit = mcp("resubmit_live_flow_run",
    environmentName=ENV, flowName=FLOW_ID, runName=RUN_ID)
print(resubmit)   # {"resubmitted": true, "triggerName": "..."}

# 等待 ~30 s 然后检查
import time; time.sleep(30)
new_runs = mcp("get_live_flow_runs", environmentName=ENV, flowName=FLOW_ID, top=3)
print(new_runs[0]["status"])   # Succeeded = 完成
```

### 何时使用重放 vs 触发

| 情景 | 使用 | 原因 |
|---|---|---|
| **在任意流上测试修复** | `resubmit_live_flow_run` | 重放导致失败的精确触发器负载——验证的最佳方式 |
| 递归/计划流 | `trigger_live_flow`（无 `body`） | 现在运行它，像门户的“运行流”按钮；重放重放过去运行的数据 |
| SharePoint / 连接器触发器 | `resubmit_live_flow_run` | 无法在不创建真实 SP 项目的情况下触发 |
| HTTP、按钮或 PowerApps 触发器具有**自定义**测试负载 | `trigger_live_flow` | 当你需要发送与原始运行不同的数据时 |
| 全新流，从未运行过 | `trigger_live_flow` | 没有先前的运行可以重放 |

### 使用自定义负载测试 HTTP、按钮和 PowerApps 流

对于具有 `Request` 触发器（HTTP 请求、手动按钮或 PowerApps）的流，当您需要发送**不同**的负载时，使用 `trigger_live_flow`。将触发器输入作为 `body` 传递给每种类型：

```python
# 首先检查触发器期望的内容——直接从流程定义中读取
defn = mcp("get_live_flow", environmentName=ENV, flowName=FLOW_ID)
triggers = defn["properties"]["definition"]["triggers"]
manual = next(iter(triggers.values()))   # 通常 HTTP 流中只有一个触发器
request_schema = manual.get("inputs", {}).get("schema")
print("期望的请求体模式:", request_schema)

# 响应模式位于 actions 块中的 Response 动作上
for name, act in defn["properties"]["definition"]["actions"].items():
    if act.get("type") == "Response":
        print(f"响应 {name}:", act.get("inputs", {}).get("schema"))

# 使用测试负载的触发器
result = mcp("trigger_live_flow",
    environmentName=ENV,
    flowName=FLOW_ID,
    body={"name": "测试用户", "value": 42})
print(f"状态: {result['responseStatus']}, 请求体: {result.get('responseBody')}")
print(f"类型: {result['triggerKind']}, 通过: {result['invocation']}, 运行: {result.get('runName')}")
if result.get("warning"):
    print(result["warning"])   # 你遗漏了必需的触发器输入

```

> `trigger_live_flow` 会自动处理 AAD 认证触发器。
> 适用于 `Request` 触发器（HTTP 请求、按钮、PowerApps）以及计划（周期性）流程，它会立即运行——没有 `body`，因为计划触发器不接受输入（会拒绝请求体）。自动连接器触发器仅从其源事件触发。

> Power Automate 不会强制执行触发器的 `required` 输入。如果你遗漏了某个输入，运行仍然会开始，该输入为空，结果会包含一个命名缺失键的 `warning`。如果这很重要，请取消运行并再次调用，提供完整的请求体。

> `runName` 仅在按钮和 PowerApps 运行时返回。对于 HTTP 触发器，请使用 `get_live_flow_runs` 查找运行记录。

> 通过浏览器扩展密钥，按钮和 PowerApps 触发器仅以空请求体运行。工具说明了这一点，并列出了绕过方法：重新提交过去的运行、在流程内部使用 `coalesce(triggerBody()?['x'], 'value')` 默认输入，或使用标准 API 密钥。

---

## 快速参考诊断决策树

| 症状 | 首选工具 | 然后始终调用 | 查找内容 |
|---|---|---|---|
| 流程显示为失败 | `get_live_flow_run_error` | 在失败动作上调用 `get_live_flow_run_action_outputs` | HTTP 状态 + 响应体中的 `outputs` |
| 错误代码是通用的（`ActionFailed`, `NotSpecified`） | — | `get_live_flow_run_action_outputs` | `outputs.body` 包含实际错误消息、堆栈跟踪或 API 错误 |
| HTTP 动作返回 500 | — | `get_live_flow_run_action_outputs` | `outputs.statusCode` + `outputs.body` 包含服务器错误详情 |
| 表达式崩溃 | — | 在先前的动作上调用 `get_live_flow_run_action_outputs` | 输出体中的 null / 错误类型的字段 |
| 流程从未启动 | `get_live_flow` | — | 检查 `properties.state` = "Started" |
| 动作返回错误数据 | `get_live_flow_run_action_outputs` | — | 实际输出体与预期对比 |
| 修复后仍然失败 | 重新提交后的 `get_live_flow_runs` | — | 新运行的 `status` 字段 |

> **规则：不要仅凭错误代码诊断。** `get_live_flow_run_error` 确定失败的动作用。`get_live_flow_run_action_outputs` 揭示实际原因。始终调用两者。

---

## 参考文件

- [common-errors.md](references/common-errors.md) — 错误代码、可能原因和修复方法
- [debug-workflow.md](references/debug-workflow.md) — 复杂失败的完整决策树

## 相关技能

- `flowstudio-power-automate-mcp` — 基础技能：连接设置、MCP 辅助工具、工具发现
- `flowstudio-power-automate-build` — 构建和部署新流程
