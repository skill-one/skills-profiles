## 哪个 CLI

有两个不同的 HubSpot CLI 工具看起来很相似，不要混淆它们：

- **`hubspot`** — 这是此技能库针对的 HubSpot **代理 CLI**。它管理 CRM 数据和自动化，并且确实具有原生工作流命令：`hubspot workflows list|get|create|update|delete`。
- **`hs`** — 这是 HubSpot **开发者 CLI** (`@hubspot/cli`)，用于构建开发项目：主题、模块、无服务器函数、UI 扩展和私有应用 (`hs project`, `hs upload`, `hs create`)。它**不**创建或管理工作流记录。

要创建或管理工作流，请使用 `hubspot workflows ...` — 而不是 `hs`。

如果这里的任何内容发生变化，`hubspot workflows --help` 和 `hs --help` 是权威的。

## 资源

| 文件 | 使用场景 |
|---|---|
| `resources/workflow-json-reference.md` | 创建/更新时的主体结构 — 动作图、分支/汇聚、注册、full-PUT 陷阱 |
| `resources/example-contact-flow.json` | 最小有效的 `CONTACT_FLOW` 骨架，用于 `hubspot workflows create --file` |
| `resources/example-branching-flow.json` | 说明分支汇聚 — 两条路径指向同一个共享下游动作的 `connection.nextActionId` |

## 真实来源

`hubspot workflows --help` 列出了五个子命令：`list`、`get`、`create`、`update`、`delete`。**没有 `search`** — 通过名称查找是 `list | jq`。对于 JSONL 管道、分页和破坏性干运行/摘要/确认模式，此技能基于 `bulk-operations/SKILL.md` 构建 — 首先重读那部分内容。

## 1. 列表 + 按名称查找

```bash
hubspot workflows list                       # JSONL: id, name, isEnabled, type, objectTypeId, revisionId
hubspot workflows list --format table        # 供人类扫描

# 按名称查找 — 不区分大小写的子字符串
hubspot workflows list | jq -c 'select(.name | test("Welcome"; "i"))'

# 精确匹配
hubspot workflows list | jq -c 'select(.name == "MQL Nurture")'
```

列表每调用分页 100 条。使用 `--after` 循环，直到 `meta.next` 为空 — 查看 `bulk-operations/SKILL.md` "分页"。查看 `bulk-operations` 中的 `resources/json-patterns.md` 获取更多 `jq` 过滤器。

## 2. 获取 + 读取结构

```bash
hubspot workflows get 12345678                            # 单个
hubspot workflows get 12345678 87654321                   # 批量位置参数
printf '%s\n' 12345678 87654321 | hubspot workflows get   # 批量标准输入
hubspot workflows get 12345678 > workflow.json            # 保存以供编辑
```

获取返回完整主体 (`actions`, `enrollmentCriteria`, `revisionId`, …) — 创建/更新所需的形状。查看 `resources/workflow-json-reference.md`。

## 3. 从 JSON 创建

```bash
hubspot workflows create --file workflow.json --dry-run
hubspot workflows create --file workflow.json
cat workflow.json | hubspot workflows create         # 标准输入也有效
```

设置 `type` (`CONTACT_FLOW` 或 `PLATFORM_FLOW`)、`flowType` (`WORKFLOW`) 和 `objectTypeId`（例如 `0-1` 用于联系人）— 所有这些在创建时都是必需的。查看 `resources/workflow-json-reference.md` 获取主体形状，以及 `resources/example-contact-flow.json` 获取最小模板。**最简单的路径：`get` 一个类似的现有工作流作为起始模板** 而不是手写 JSON。

**陷阱：`create --dry-run` 不会验证主体。** 它会回显 JSON 并带有 `ok:true`，不会进行 API 调用 — 绿色干运行只能证明输入是良好格式的 JSON，而不是有效的创建（缺少 `type`/`flowType`/`objectTypeId`/`actions` 的主体仍然返回 `ok:true`）。唯一的实际验证是实时 `create`。相比之下，`update --dry-run` 会拒绝缺少 `revisionId` 等必填字段的主体。

**分支和汇聚。** `LIST_BRANCH` 动作根据过滤标准分支路径；每个分支 — 以及 `defaultBranch` — 都带有指向它继续的动作的 `connection`。因为连接通过 `nextActionId` 指向动作，**分支可以汇聚**：将两个分支指向同一个 `actionId`，两条路径都继续到同一个共享动作，不会重复。查看 `resources/workflow-json-reference.md` 的分支部分和 `resources/example-branching-flow.json`。

## 4. 更新 — 完整 PUT，get-修改-put 循环

更新是**完整替换**。主体必须包含 `revisionId`（来自 `get`）和 `type`。只读字段 (`createdAt`, `updatedAt`, `dataSources`) 会自动移除。更新受限制：首先干运行，然后使用 `--digest <hash> --confirm <flowId>` 重新运行。

```bash
# 1. 获取当前状态
hubspot workflows get 12345678 > workflow.json

# 2. 编辑 workflow.json（保留 revisionId、type 和任何要保留的字段）

# 3. 干运行 — 发出一个摘要
hubspot workflows update 12345678 --file workflow.json --dry-run

# 4. 应用 — 确认值是流程 ID
hubspot workflows update 12345678 --file workflow.json \
  --digest blast-xxxxxxxx --confirm 12345678
```

**陷阱：** 部分主体会静默清除字段。发送 `actions` 将清除 `enrollmentCriteria`。始终从完整的 `get` 响应开始。

## 5. 删除 — 破坏性，链接到批量安全流程

```bash
# 1. 干运行 — 发出一个摘要 + 确认提示
hubspot workflows delete 12345678 --dry-run

# 2. 重新运行，带有摘要 + 确认。确认值是工作流的名称，而不是其 ID。
hubspot workflows delete 12345678 --digest blast-xxxxxxxx --confirm "New lead routing"
```

干运行输出包括 `apply_command_hint` — 从那里复制确切的确认字符串，以避免引号意外。工作流删除后无法通过自动化 API 恢复；检查 `hubspot history --since 1h` 获取审计记录。完整的安全模式（摘要、5 分钟过期、历史恢复）在 `bulk-operations/SKILL.md` "安全破坏性工作流" 中记录。

## 已知限制

- 没有 `hubspot workflows search` — `list | jq` 是解决方法。
- CLI 中没有 Lists API — 列表成员资格注册触发器必须在 UI 中设置。
- 没有 sequences/cadences API。`dataSources` 是只读的 — 不能通过更新重新配置。
