---
name: workflow-automation
description: 从 `hubspot` 代理 CLI 而不是 `hs` 开发者 CLI 中列出、检查、创建、更新和删除 HubSpot 工作流（v4 流程 API），经典 v3 基于联系人的工作流不在此范围内。
---

## 哪个 CLI

有两个不同的 HubSpot CLI 与之相似，容易混淆——不要弄混：

- **`hubspot`** — 此技能库针对的 HubSpot **代理 CLI**。它管理 CRM 数据和自动化，并且确实具有原生工作流命令：`hubspot workflows list|get|create|update|delete`。
- **`hs`** — HubSpot **开发者 CLI** (`@hubspot/cli`)，用于构建开发项目：主题、模块、无服务器函数、UI 扩展和私有应用 (`hs project`, `hs upload`, `hs create`)。它**不**创建或管理工作流记录。

要创建或管理工作流，请使用 `hubspot workflows ...` — 而不是 `hs`。

如果这里的任何内容发生变化，`hubspot workflows --help` 和 `hs --help` 是权威的。

## 资源

| 文件 | 使用时机 |
|---|---|
| `resources/workflow-json-reference.md` | 创建/更新时的主体形状 — 行动图、分支/汇聚、注册、全量 PUT 陷阱 |
| `resources/example-contact-flow.json` | 最小有效 `CONTACT_FLOW` 骨架，用于 `hubspot workflows create --file` |
| `resources/example-branching-flow.json` | 说明分支汇聚 — 两条路径指向共享下游动作的 `connection.nextActionId` |

## 真实来源

`hubspot workflows --help` 列出了五个子命令：`list`、`get`、`create`、`update`、`delete`。**没有 `search`** — 通过名称查找是 `list | jq`。对于 JSONL 管道、分页和破坏性干运行/摘要/确认模式，此技能基于 `bulk-operations/SKILL.md` 构建 — 首先重读那部分。

## 认证 — 需要服务密钥

**每个 `hubspot workflows` 命令都需要 `HUBSPOT_ACCESS_TOKEN`（服务密钥）。** 它们在 `hubspot auth login`（用户 OAuth）下都不起作用 — CLI 在一开始就拒绝它们，提示 `This endpoint does not support user-level OAuth tokens`。v4 流程 API 需要的 `automation` 权限对 CLI 的用户级 OAuth 应用不可用，因此在使用此技能的任何命令之前设置服务密钥：

```bash
export HUBSPOT_ACCESS_TOKEN=<服务密钥>   # 在 设置 → 集成 → 服务密钥 中创建
hubspot workflows list
```

## 1. 列出 + 按名称查找

```bash
hubspot workflows list                       # JSONL: id, name, isEnabled, type, objectTypeId, revisionId
hubspot workflows list --format table        # 供人类扫描

# 按名称查找 — 不区分大小写的子字符串
hubspot workflows list | jq -c 'select(.name | test("Welcome"; "i"))'

# 精确匹配
hubspot workflows list | jq -c 'select(.name == "MQL Nurture")'
```

列出仅读取 `/automation/v4/flows`。来自 `/automation/v3/workflows` 的经典基于联系的工作流不会被返回，因此空结果不一定表示缺少自动化范围。V4 结果每调用分页 100 条；使用 `--after` 循环，直到 `meta.next` 为空 — 见 `bulk-operations/SKILL.md` "分页"。有关更多 `jq` 过滤器，请参阅 `bulk-operations` 中的 `resources/json-patterns.md`。

## 2. 获取 + 读取形状

```bash
hubspot workflows get 12345678                            # 单个
hubspot workflows get 12345678 87654321                   # 批量位置参数
printf '%s\n' 12345678 87654321 | hubspot workflows get   # 批量标准输入
hubspot workflows get 12345678 > workflow.json            # 保存以供编辑
```

获取返回完整主体 (`actions`, `enrollmentCriteria`, `revisionId`, …) — 创建/更新所需的形状。参见 `resources/workflow-json-reference.md`。

## 3. 从 JSON 创建

```bash
hubspot workflows create --file workflow.json --dry-run
hubspot workflows create --file workflow.json
cat workflow.json | hubspot workflows create         # 标准输入也有效
```

设置 `type` (`CONTACT_FLOW` 或 `PLATFORM_FLOW`)、`flowType` (`WORKFLOW`) 和 `objectTypeId`（例如，用于联系的是 `0-1`）— 所有这些在创建时都是必需的。有关主体形状，参见 `resources/workflow-json-reference.md`；有关最小模板，参见 `resources/example-contact-flow.json`。**最简单的路径：`get` 一个现有的类似工作流作为起始模板**，而不是手写 JSON。

**陷阱：`create --dry-run` 不会验证主体。** 它会回显 JSON 并带有 `ok:true`，不会进行 API 调用 — 绿色干运行仅证明输入是良好格式的 JSON，而不是有效的创建（缺少 `type`/`flowType`/`objectTypeId`/`actions` 的主体仍然返回 `ok:true`）。唯一的实际验证是实时 `create`。相比之下，`update --dry-run` 会拒绝缺少 `revisionId` 等必需字段的主体。

**分支和汇聚。** `LIST_BRANCH` 动作根据过滤标准分支路径；每个分支 — 以及 `defaultBranch` — 都会携带到它继续的动作的 `connection`。因为连接通过 `nextActionId` 指向动作，所以**分支可以汇聚**：将两个分支指向相同的 `actionId`，两条路径都继续到同一个共享动作，不会重复。参见 `resources/workflow-json-reference.md` 的分支部分和 `resources/example-branching-flow.json`。

## 4. 更新 — 全量 PUT，获取-修改-PUT 循环

更新是**全量替换**。主体必须包含 `revisionId`（来自 `get`）和 `type`。只读字段 (`createdAt`, `updatedAt`, `dataSources`) 会自动移除。更新受限制：首先干运行，然后使用 `--digest <hash> --confirm <flowId>` 重新运行。

```bash
# 1. 获取当前状态
hubspot workflows get 12345678 > workflow.json

# 2. 编辑 workflow.json（保留 revisionId、type 和任何要保留的字段）

# 3. 干运行 — 输出一个摘要
hubspot workflows update 12345678 --file workflow.json --dry-run

# 4. 应用 — 确认值是流程 ID
hubspot workflows update 12345678 --file workflow.json \
  --digest blast-xxxxxxxx --confirm 12345678
```

**陷阱：** 部分主体会静默清除字段。仅发送 `actions` 将清除 `enrollmentCriteria`。始终从完整的 `get` 响应开始。

## 5. 删除 — 破坏性，链接到批量安全流程

```bash
# 1. 干运行 — 输出一个摘要 + 确认提示
hubspot workflows delete 12345678 --dry-run

# 2. 重新运行，带有摘要 + 确认。确认值是工作流的名称，而不是其 ID。
hubspot workflows delete 12345678 --digest blast-xxxxxxxx --confirm "New lead routing"
```

干运行输出包括 `apply_command_hint` — 从那里复制确切的确认字符串，以避免引号意外。删除后无法通过自动化 API 恢复工作流；检查 `hubspot history --since 1h` 以获取审计记录。完整的（摘要、5 分钟过期、历史恢复）安全模式在 `bulk-operations/SKILL.md` 的 "Safe destructive workflow" 中有说明。

## 已知限制

- `list` 仅涵盖 v4 流程。来自 `/automation/v3/workflows` 的经典基于联系的工作流不会被返回。
- 没有 `hubspot workflows search` — `list | jq` 是解决方案。
- `hubspot segments` 提供 CRM 列表 (`list`, `get`, `create`, `update`, `update-filters`, `delete`, `restore`, `members-list` / `members-add` / `members-remove`)。列表成员注册触发器是工作流主体 (`enrollmentCriteria`) 的一部分，因此通过 `hubspot workflows create` / `update` 配置它们 — 使用 `hubspot segments list` / `get` 获取列表 ID，并从真实的 `workflows get` 复制 `enrollmentCriteria` 形状（参见 `resources/workflow-json-reference.md`）。无需 UI 步骤。
- Sales Hub 序列是工作流的独立表面：`hubspot sequences` 读取它们 (`list --user-id <id>`, `get <id> --user-id <id>`, `enrollments <contact_id>`)，但它是只读的 — 没有创建/更新/删除/注册，并且它不是 CRM 对象类型（Sales Hub Professional+，`automation.sequences.read` 权限）。工作流创建/更新/删除仍在 `hubspot workflows` 下。这个表面会增长；在假设 API 缺失之前，请重新检查 `hubspot --help` / `CHANGELOG.md`。
- `dataSources` 是只读的 — 不能通过更新重新配置。
