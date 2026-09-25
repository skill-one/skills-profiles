# Python 代码节点（原生）

自 n8n 2.0 版本起，代码节点的 Python 运行为**原生 Python 任务运行器**（`language: "pythonNative"`）。旧的 Pyodide "Python (Beta)" 已消失，随之消失的是它所拥有的所有 n8n 辅助功能：`_input`、`_json`、`_node`、`_now`、`_today` 和 `_jmespath` 现在都会引发 `NameError`。从旧模板、论坛帖子或旧文档中复制代码通常会失效。

---

## JavaScript 优先——比以往更强

原生 Python 为您提供两个变量和纯 Python，默认情况下**没有导入**：没有 `json`、`datetime` 或 `re`。所有 n8n 特定的功能（`$('Node')`、`$jmespath`、Luxon、`this.helpers.httpRequest`、静态数据）都仅存在于 JavaScript 中。仅在用户明确要求时才使用 Python。即使在这种情况下，首先检查表达式、编辑字段或原生节点（Crypto、日期和时间、HTML、XML）是否可以完成工作。参见 **n8n-code-javascript** 和 **n8n-expression-syntax** 中的转换门禁。

---

## 快速入门

```python
# 对所有项目运行一次（默认模式）
return [
    {"json": {"name": it["json"]["name"], "revenue": it["json"]["revenue"]}}
    for it in _items
    if it["json"].get("active")
]
```

```python
# 对每个项目运行一次
row = _item["json"]
return {"json": {**row, "name_upper": (row.get("name") or "").upper()}}
```

节点配置：`{"language": "pythonNative", "mode": "runOnceForAllItems" | "runOnceForEachItem", "pythonCode": "..."}` 在 `n8n-nodes-base.code` 类型版本 2 上。

---

## 唯一的输入：`_items` 和 `_item`

| 模式 | 变量 | 形状 |
|---|---|---|
| 对所有项目运行一次 | `_items` | `list` 的纯字典 `{"json": {...}, "pairedItem": {...}}` |
| 对每个项目运行一次 | `_item` | 一个纯字典 `{"json": {...}, "pairedItem": {...}}` |

- 每个变量**仅在其自己的模式下存在**。在每项模式中的 `_items`（或在所有项模式中的 `_item`）会引发 `NameError`。
- **仅支持字典访问**。`it["json"]["name"]` 或 `it["json"].get("name")`。`it.json.name` 会引发 `AttributeError: 'dict' object has no attribute 'json'`。
- **没有其他节点**。没有 `_node` / `$('Node')` 等价物。如果您需要来自另一个分支的数据，请先使用合并节点，或在 JavaScript 中读取。
- **Webhook 负载**位于 `["body"]`：`_items[0]["json"].get("body", {}).get("email")`。
- **二进制数据**不在此范围内。在 JavaScript 中读取和写入二进制数据（见 **n8n-binary-and-data**）。
- **pairedItem**：返回 `_items` / `_item` 会保留它。当您构建新的字典并且下游使用 `$('Node').item` 时，向每个返回的项目添加 `"pairedItem": {"item": i}`。但这在原生 Python 中尚未验证，因此请在依赖它之前进行测试运行。
- 缺失键：优先使用 `.get(key, default)`。`row["missing"]` 会引发 `KeyError`。

遗留代码迁移表：

| 遗留（Pyodide） | 原生 |
|---|---|
| `_input.all()` | `_items` |
| `_input.first()["json"]` | `_items[0]["json"]`（先检查 `if _items`） |
| `_input.item` / `_json` | `_item` / `_item["json"]` |
| `_node["X"]` | 不可用：上游使用合并节点，或在 JavaScript 中使用 |
| `_now`, `_today` | 不可用：通过编辑字段传递 `{{ $now.toISO() }}`，或在 JavaScript 中使用 |
| `_jmespath(data, q)` | 不可用：在表达式中使用 `$jmespath`，或使用理解 |
| `item.json.field` | `item["json"]["field"]` |

---

## 导入：默认情况下被阻止

每个 `import`（标准库和第三方）在代码运行**之前**都会与允许列表进行检查。默认允许列表为空，因此即使 `import json` 也会拒绝整个节点：

```
检测到安全违规
第 1 行：不允许导入标准库模块 'json'。允许的标准库模块：无
```

- **n8n Cloud**：完全不允许导入。
- **自托管**：管理员可以在任务运行器配置中允许列表模块（见 **n8n-self-hosting** → `TASK_RUNNERS.md`）。因此，某些实例允许 `json`、`datetime` 和 `re`，而大多数不允许。
- **默认使用无导入代码**。如果导入确实有帮助，请先确认：一个单行测试节点 `import json` + `return [{"json": {"ok": True}}]`，或询问用户。永远不要假设。
- 没有导入：上游解析 JSON 字符串（在编辑字段中使用 `{{ JSON.parse($json.payload) }}`）。在表达式中进行日期计算（使用 Luxon 或 JS）。ISO-8601 字符串仍然作为纯字符串正确比较和排序。使用 Crypto 节点进行哈希。
- `requests`、`pandas` 和 `numpy` 除非管理员构建了自定义运行器镜像，否则永远不可用。使用 HTTP 请求节点进行 HTTP 请求。

---

## 沙盒限制（即使没有导入也会失败）

| 您编写 | 发生什么 | 使用替代方案 |
|---|---|---|
| `eval`、`exec`、`compile`、`open`、`input`、`type`、`getattr`、`setattr`、`hasattr`、`vars`、`dir`、`globals`、`locals`、`object`、`memoryview`、`breakpoint` | `NameError: name 'type' is not defined`（运行时） | `isinstance(x, dict)`；`key in d` / `d.get(key)` |
| `class Foo: ...` | `__build_class__ not found`（运行时） | 字典 + 函数 |
| `x.__class__`、`"{0.__class__}".format(x)`、`__import__("json")` | `Security violations detected`（整个节点在运行前被拒绝） | — |
| 函数内的 `global counter` | `NameError: name 'counter' is not defined`，因为您的代码在包装函数内运行 | `nonlocal counter` |

纯 Python 中的其他内容均可正常工作（已验证）：理解、生成器、lambda、闭包、递归、`try`/`except`、f-字符串 / `.format()` / `%`、`sorted`/`min`/`max`/`sum`/`any`/`all`/`enumerate`/`zip`/`round`、集合、`isinstance`、`print()`（输出发送到浏览器控制台）。

---

## 返回形状（已验证）

在 n8n 2.38.5 上观察到。以下自动包装和传递行为未记录，可能在后续版本中更改。升级 n8n 后请重新进行测试运行以确认。

**对所有项目运行一次**

| 返回 | 结果 |
|---|---|
| `[{"json": {...}}, ...]` | 标准，N 个项目 |
| `[{...}, ...]`（纯字典） | 自动包装在 `json` 下，N 个项目 |
| `{"json": {...}}` 或一个纯字典 | 1 个项目 |
| `_items`（原地修改） | 带有您的更改传递 |
| `None` / 没有 `return` | 错误 `Cannot read properties of null (reading 'json')` |

**对每个项目运行一次**

| 返回 | 结果 |
|---|---|
| `{"json": {...}}`、一个纯字典或 `_item` | 1 个项目 |
| `None` | 项目被**丢弃**（内置过滤器） |
| 一个**列表** | 错误 `A 'json' property isn't a dictionary [item 0]` |

**输出时的值转换**：`tuple` 变为列表，`set` 变为字符串 `"{1, 2}"`，而 `datetime` 变为 `str(dt)`（`"2026-09-16 10:18:00.025792"`，不是 ISO）。显式转换（`sorted(s)`、`dt.isoformat()`）。

在所有项模式下优先使用显式的 `[{"json": ...}]`，在每个项模式下使用 `{"json": ...}`。自动包装有效，但显式形状使下一个读者更清楚地了解意图。

---

## 错误和 `onError`

纯 `raise ValueError("bad row")` 会以该消息失败节点。当节点具有 `onError` 继续模式时，三种失败类型的行为**不同**（已验证）：

| 失败 | `continueErrorOutput` | `continueRegularOutput` |
|---|---|---|
| 运行时异常（`raise`、`KeyError`、`NameError`、禁止的内置函数） | `{"error": "<message>"}` 在错误输出（`main[1]`）✅ | `{"error": "<message>"}` 在主输出 |
| 静态拒绝（`Security violations detected`：导入、双下划线） | 节点标记为失败，但**输入项目未更改**，从成功输出输出；`main[1]` 保持为空 | 输入项目未更改，在主输出 |
| 返回形状错误（每个项模式中的列表，所有项模式中的 `None`） | 相同：**未更改的输入在成功输出** | 相同 |

最后两种是静默数据陷阱：下游节点接收未处理的输入，就好像代码已运行一样，执行仍然显示成功。没有错误分支捕获它们。防止它们（除非确认，否则不导入）并正确的返回形状），并通过实际测试运行确认（见 **n8n-error-handling**）。

其他消息：

- `Python runner unavailable: Python 3 is missing from this system`：自托管实例没有 Python 任务运行器（标准镜像不包含）。这是一个基础设施问题，不是代码问题。见 **n8n-self-hosting** → `TASK_RUNNERS.md`。
- `validate_node` / `validate_workflow` 捕获一些 Python 错误（`import requests`、缺少 `return`、`return None`）。它们**不**捕获 `_input`/`_json`、点访问、禁止的标准库导入、双下划线访问或类。测试执行是唯一可靠的检查。

---

## 性能

每个 Python 代码节点大约需要 0.4 秒（运行器冷时大约 1 秒），明显比 JS 代码节点或表达式慢。在**对所有项目运行一次**模式下处理列表，而不是每个项目，并且不要链式连接多个小 Python 节点，一个就足够了。

---

## 检查清单

- [ ] 用户确实需要 Python。否则使用 JS、表达式或原生节点。
- [ ] 模式与变量匹配：`_items`（所有项目）/ `_item`（每个项目）。
- [ ] 仅字典访问。没有 `_input`、`_json`、`_node`、`_now` 或 `_jmespath`。
- [ ] 除非在本实例上确认允许列表，否则不使用 `import`。
- [ ] 不使用类、`type()`、`getattr`/`hasattr` 或双下划线。使用 `nonlocal` 而不是 `global`。
- [ ] 返回形状符合模式。集合和日期时间显式转换。
- [ ] 运行实际测试执行并检查输出项目（单独验证无法捕获上述陷阱）。

---

## 参考

- **[COMMON_PATTERNS.md](COMMON_PATTERNS.md)**：12 个无导入模式，每个模式都在实时 n8n 实例上验证（过滤、聚合、分组、去重、前 N、展平、验证、丢弃项目、文本报告、安全的嵌套访问、运行总计、ISO 时间戳）。

## 相关技能

- **n8n-code-javascript**：代码节点的默认设置，包含所有 n8n 辅助功能。
- **n8n-expression-syntax**：`$jmespath`、Luxon 和转换门禁，通常比任何代码节点都更适合。
- **n8n-code-tool**：AI-agent 自定义代码工具中的 Python（`_query`，返回字符串）。
- **n8n-error-handling**：连接错误输出；上述传递陷阱。
- **n8n-self-hosting**：启用 Python 任务运行器并允许列表模块。
