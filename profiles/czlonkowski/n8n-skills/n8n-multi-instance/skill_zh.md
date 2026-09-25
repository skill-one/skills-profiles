# 在 MCP 上使用多个 n8n 实例

当 `n8n_instances` 工具可用时，用户处于 **多实例模式**：一个 MCP 连接可以访问多个 n8n 实例（例如 `prod`、`staging` 或每个客户/团队一个）。其他 n8n 工具（`n8n_get_workflow`、`n8n_list_workflows`、`n8n_update_partial_workflow`、`n8n_manage_datatable`、`n8n_manage_credentials`、`n8n_executions`、`n8n_test_workflow`、…）都针对当前会话正在目标实例运行。没有每个调用实例参数：你只能通过切换来更改目标。目标错误实例会导致读取返回错误数据，写入出现在错误位置——通常 **没有错误**（唯一的例外是模糊凭证写入，它会失败；见下文）。所以请故意选择目标。

如果 `n8n_instances` 工具 **不存在**，则账户是单实例：忽略此技能并直接使用 n8n 工具。

## 黄金法则

六条规则。每条规则防止一类静默错误路由。

1. **先发现。** 在操作前调用 `n8n_instances({mode:"list"})`，以便知道实例名称以及哪个是 `current`。
2. **在非默认实例上工作前，按名称切换到目标**：`n8n_instances({mode:"switch", name:"<instance name>"})`。匹配不区分大小写。
3. **在自己的回合切换。** 不要将 `switch` 和依赖操作放在 **同一并行工具调用批次** 中。一批调用中的顺序没有保证，因此依赖调用可能在切换会话状态可见之前解析到 *上一个* 实例。切换，让它返回，*然后* 操作。
4. **在高风险操作前验证。** 在创建/更新/删除 **凭证**（以及在破坏性工作流编辑之前），立即确认 `current` 是你打算的实例——主要检查是 `n8n_instances({mode:"list"})`。系统只对 *模糊* 凭证情况失败关闭（规则 6）；显式切换到 **错误** 实例仍然会静默写入那里，所以这个检查由你负责。
5. **意外的 `NOT_FOUND` 几乎总是错误实例路由，而不是删除。** 不要重新创建对象。重新检查当前实例并重试（见恢复）。
6. 在 `INSTANCE_AMBIGUOUS` 上，在此会话上切换，然后重试。系统拒绝在此会话写入秘密，因为此会话从未自行选择目标。服从——在此处运行 `switch` 以确认实例，然后重试写入。不要绕过它或盲目重试。

## 核心工作流

```
1. n8n_instances({mode:"list"})                      # 查看 available[] + current + default
2. n8n_instances({mode:"switch", name:"prod"})       # 将此会话绑定到 "prod"
   → 返回 { previous, current }; 确认 current.name == "prod"
3. (执行你的工作) n8n_list_workflows / n8n_get_workflow / n8n_manage_datatable / ...
4. 在凭证写入或删除之前:
   n8n_instances({mode:"list"})  → 重新确认 current, THEN n8n_manage_credentials({action:"create", ...})
```

要切换到另一个实例，只需再次 `switch`。整个会话跟随切换。

## `n8n_instances` 工具

两种模式（`mode` 是必需的，并且经过枚举验证）：

- `{mode:"list"}` → `{ current, default, available }`，没有副作用。
  - `current` 和 `default` 各是一个实例 `{ id, name, url, isDefault }`（或 `null`）。
  - `available` 是每个实例，每个实例都有一个额外的 `isCurrent` 布尔值。按 **`name`** 匹配；永远不要硬编码 `id`。
- `{mode:"switch", name:"<name>"}` → `{ previous, current }`，并将此会话绑定到命名实例。`name` 不区分大小写。

### 错误封装（来自 `n8n_instances` 工具）

每个错误返回 `{ error: "<CODE>", message, … }`。你会实际遇到的错误：

| 代码 | 当...时 | 该怎么做 |
|---|---|---|
| `UNKNOWN_INSTANCE` | `name` 匹配不到任何实例 | 从错误负载中的 `available` 列表中选择一个名称并重试。 |
| `NAME_REQUIRED` | `switch` 没有带 `name` | 带一个 `name` 重叫（错误在 `available` 中列出了有效的名称）。 |
| `MULTI_INSTANCE_DISABLED` | 多实例模式关闭 | 没有可切换的；直接使用 n8n 工具。用户可以在 n8n-mcp 仪表板中启用它。 |
| `NO_SESSION` | 请求既没有 MCP 会话 id **也没有**凭证 id | 选择无处放置。重新连接/初始化会话，然后切换。 |
| `UNKNOWN_MODE` | `mode` 不是 `list`/`switch` | 使用 `list` 或 `switch`。 |
| `INVALID_CONTEXT` | 服务器端元数据缺失 | 服务器错误，不是你的输入——报告它。 |

> 实例名称永远不会是 `default`、`current`、`list` 或 `switch`（保留），所以你永远不会看到以模式或字段命名的实例。

### `INSTANCE_AMBIGUOUS`（来自凭证写入路径，不是工具）

一个单独的、更高风险的错误。它 **不是** 由 `n8n_instances` 返回——当你在调用 `n8n_manage_credentials` 创建/更新/删除凭证时，如果目标实例是模糊的：此会话从未自行切换，而是继承了其他地方做出的切换（分叉/重新连接），指向一个 **非默认** 实例。为了避免将秘密写入错误实例，服务器 **阻止写入**（它永远不会到达 n8n，不会扣配额）并返回：

```json
{
  "error": "INSTANCE_AMBIGUOUS",
  "message": "… 发出此请求的会话自己从未切换到那里 … 在此会话上重新运行 n8n_instances({mode:\"switch\", name:\"…\"}) 以确认目标 …",
  "lastSelected": { "id": "…", "name": "…" },
  "default":      { "id": "…", "name": "…" }
}
```

**修复方法**：确定你实际想要的实例（`lastSelected` 是继承的切换，`default` 是账户默认），在此会话上运行 `n8n_instances({mode:"switch", name:"…"})`，然后重试写入。见规则 6。

## 目标行为（心智模型）

- `switch` **绑定此会话** 到所选实例。绑定 **持续到会话结束** 并在重新连接、空闲和后端部署期间存活（~24 小时，MCP 会话寿命）——你不需要在每次调用前重新切换。
- 其他会话/终端是 **独立的**：在此处切换不会移动它们。
- 一个会话一次只能针对 **一个实例**。没有每个调用实例参数；你只能通过 `switch` 更改目标。
- **读取和非凭证写入** 路由到当前选择的实例，静默——错误路由产生错误数据或 `NOT_FOUND`，而不是错误。
- **凭证写入是唯一受保护的情况**。它们路由方式相同，除了服务器对 *模糊* 状态失败关闭（会话从未切换，恢复到非默认实例）使用 `INSTANCE_AMBIGUOUS`（规则 6）。这是一个安全网，不是规则 4 的替代品：显式切换到错误实例仍然会写入那里。
- **如果你的所选实例被删除**（用户在会话中删除它），下一个调用会静默回退到你的 **默认** 实例——没有错误。所以默认数据出现在你期望另一个实例的地方看起来像“我的数据消失了。” 重新列出以查看你在哪里。

## 恢复剧本

| 症状 | 通常意味着什么 | 该怎么做 |
|---|---|---|
| 凭证创建/更新/删除上的 `INSTANCE_AMBIGUOUS` | 此会话从未自行切换；系统无法猜测要将秘密写入哪个实例 | 在此会话上运行 `n8n_instances({mode:"switch", name:"<target>"})`（错误的 `lastSelected` 和 `default` 会命名——选择你想要的那个），然后重试写入。不要盲目重试。 |
| 你知道的 **存在** 的工作流/数据表/凭证的 `NOT_FOUND` | 你指向了错误的实例——**不是**它被删除了 | `n8n_instances({mode:"list"})` → 检查 `current`。如果它不是你的目标，`switch` 并重试。**不要重新创建对象。** |
| 读取返回 **空或不熟悉** 的数据 | 错误实例读取，或静默回退到 `default` 后你的实例被删除 | `n8n_instances({mode:"list"})`，确认 `current`，如有必要则切换，重新读取再下结论。 |
| `switch` 上的 `UNKNOWN_INSTANCE` | `name` 是错误的（拼写错误，或你猜测） | 读取错误中的 `available` 名称并切换到其中一个。名称不区分大小写。 |
| `n8n_health_check` 报告你未预期的 `instanceName` | 此会话位于你认为是不同实例 | 切换到预期实例，然后继续。 |
| 在一个回合内重复错误路由 | 你将 `switch` 和依赖工作批量处理 | 将它们分开：单独切换，等待结果，然后一次一个逻辑步骤操作。 |

在任何恢复切换后，使用 `n8n_instances({mode:"list"})`（读取 `current`）作为主要信号进行合理性检查。`n8n_health_check` 也在 `details.instanceName` 下返回解析的实例，但在某些路径上（遗留/聊天）可能不存在，所以将其视为次要确认。

## 凭证操作（最高风险）

凭证包含实时秘密，错误路由的凭证写入会将秘密放在 **错误实例** 上。服务器自动保护 *模糊* 情况——如果此会话从未选择目标并继承了切换到非默认实例，写入会以 `INSTANCE_AMBIGUOUS`（规则 6）失败关闭，并且永远不会到达 n8n。但这个网很窄：在已切换会话上的凭证写入会到达切换到的任何实例，不会二次猜测。所以：

- **在 `n8n_manage_credentials` 立即之前验证 `current`** —— 在同一短序列中调用 `n8n_instances({mode:"list"})`，而不是 10 步之前，因为后续切换可能已经移动了你。
- 在 `INSTANCE_AMBIGUOUS` 上，在此会话上切换以确认目标，然后重试——不要绕过它。
- 凭证 **读取**（`action:"list"`/`"get"`/`"getSchema"`）不受限制，不会写入秘密，但错误实例上的读取返回错误模式或列表——所以如果结果看起来错误，仍然验证 `current`。
- 对于 `n8n_manage_credentials` 工具本身（CRUD 形状，`getSchema` 发现，永远不会将秘密内联到文本字段），见 `n8n-mcp-tools-expert`。

## 常见多实例任务：在实例间复制某物

要从实例 A 在实例 B 上重新创建凭证或工作流：

```
1. 切换到 A；读取源 (n8n_manage_credentials get / n8n_get_workflow)
2. 切换到 B   (它自己的调用——永远不会与下面的创建批量处理)
3. n8n_instances({mode:"list"})  → 确认 current == B
4. 在 B 上创建  (n8n_manage_credentials create / n8n_create_workflow)
```

按每个实例的步骤在自己的回合中执行；不要重叠 `switch → B` 与在 B 上创建调用（规则 3），并在凭证写入前在此会话上显式切换，以免模糊（规则 4 和 6）。

## 快速参考

- 查看实例 + 你在哪里：`n8n_instances({mode:"list"})` → `{ current, default, available }`
- 更改目标：`n8n_instances({mode:"switch", name:"<name>"})` — 它自己的回合，然后操作
- 确认目标：`list` 中的 `current`（主要）；`n8n_health_check` 中的 `details.instanceName`（次要，可能不存在）
- `UNKNOWN_INSTANCE` → 切换到错误中的 `available` 列表中的一个名称，然后重试
- `INSTANCE_AMBIGUOUS`（凭证写入）→ 在此会话上切换以确认目标，然后重试
- 意外的 `NOT_FOUND` → 验证实例，切换，重试；**不要重新创建**
- 在凭证写入前 → 重新 `list`，确认 `current`，然后写入（失败关闭仅覆盖模糊情况）

## 与其他技能的集成

- **n8n-mcp-tools-expert** — 拥有 `n8n_manage_credentials`（CRUD + `getSchema`）和秘密通过凭证系统而不是文本字段的规则。此技能在顶层添加了“哪个实例？”层。
- **using-n8n-mcp-skills** — 路由器；咨询它以确定给定构建步骤属于哪个技能。
