# Cargo CLI — 分段

分段是 Cargo 工作区的**受众层**：一个命名、保存的模型过滤器，回答“我指的是哪些记录？”所有下游操作——批量运行、触发播放、CSV 导出、变更流——都以分段（或分段形状的过滤器）作为输入。

> 参考 `references/response-shapes.md` 获取完整的 JSON 响应结构。
> 参考 `references/troubleshooting.md` 获取常见错误及其解决方法。
> 过滤条件类型和操作符位于 [`../cargo-orchestration/references/filter-syntax.md`](../cargo-orchestration/references/filter-syntax.md) —— 过滤器 JSON 的唯一权威来源。

## 初始化

已经登录 (`cargo-ai whoami` 返回工作区)？跳到下一节。

```bash
npm install -g @cargo-ai/cli            # 没有全局安装？为每个命令前缀 `npx @cargo-ai/cli`
cargo-ai login --email you@company.com  # 通过邮件验证，无需浏览器；首次使用时创建账户
                                        # 替代方案：--oauth (浏览器) · --token <api-token> (CI)
cargo-ai whoami                         # 在任何写入操作前确认活动工作区
```

每个命令都会将 JSON 打印到标准输出；失败时以非零状态码退出并打印 `{"errorMessage": "..."}`。创建运行或批次的操作是异步的——传递 `--wait-until-finished` 或轮询匹配的 `get`。当完整技能包安装后，[`../cargo/references/prerequisites.md`](../cargo/references/prerequisites.md) 会添加 CLI 版本固定、令牌作用域和管理员专用的界面。

## 关键概念

| 术语 | 定义 |
|---|---|
| **过滤器** | 一个针对模型列进行评估的 JSON 对象 (`{conjonction, groups[].conditions[]}`)。单独存在时是暂时的。 |
| **分段** | 一个带有名称、`modelUuid` 和 `slug` 保存的过滤器。具有 `uuid`、实时的 `recordsCount` 和历史记录。这是播放、批量处理和导出的参考。 |
| **变更** | 分段在两次同步之间的一个计算增量——有多少记录被 `added`、`updated`、`removed`、`unchanged`。这是“当有人进入这个受众时通知我”动作的基础。 |
| **跟踪列** | 列 (`--tracking-column-slugs`) 的子集，其值变化计为 `updated` 记录。没有它们，记录只注册为添加或删除。 |

**过滤器与分段——谨慎选择。** 一次性问题（“有多少公司员工数超过 100？”）需要使用内联过滤器进行 `segment fetch`，不保存对象。如果你要对其运行操作、调度或跟踪，需要一个真正的 `segment create` —— 因为只有保存的分段会产生变更。

## 先发现资源再创建

总是先列出再创建。工作区通常已经包含你即将复制的分段。

```bash
cargo-ai segmentation segment list                    # 所有分段 (uuid, name, slug, modelUuid, recordsCount)
cargo-ai storage model list                           # 找到分段必须目标的模型Uuid
cargo-ai storage column list --model-uuid <uuid>      # 过滤器条件引用的列 slugs
```

播放自动创建的分段命名为 `GENERATED_PLAY_SEGMENT` 并带有 `fromPlay: true` —— **切勿手动编辑或删除这些**；它们属于拥有它们的播放。

**在 UI 中检索：** 分段位于模型下 `app.getcargo.io/workspaces/<WORKSPACE_UUID>/models/<MODEL_UUID>`。从 `cargo-ai whoami` 获取 `<WORKSPACE_UUID>`。

## 快速参考

```bash
cargo-ai segmentation segment list
cargo-ai segmentation segment get <segment-uuid>
cargo-ai segmentation segment create --name "<name>" --model-uuid <uuid> --filter '<json>'
cargo-ai segmentation segment update --uuid <segment-uuid> --filter '<json>'
cargo-ai segmentation segment remove <segment-uuid>
cargo-ai segmentation segment fetch    --model-uuid <uuid> --filter '<json>' --limit 50
cargo-ai segmentation segment download --model-uuid <uuid> --filter '<json>'
cargo-ai segmentation change list  --segment-uuid <segment-uuid>
cargo-ai segmentation change fetch --uuid <change-uuid> --kinds added --limit 50
cargo-ai segmentation record fetch --model-uuid <uuid> --ids <id[,id…]>
```

## 构建过滤器

完整的条件目录——每个 `kind` (`string`, `number`, `date`, `boolean`, `array`, `relation`) 和每个操作符——位于 [`../cargo-orchestration/references/filter-syntax.md`](../cargo-orchestration/references/filter-syntax.md)。形状：

```json
{
  "conjonction": "and",
  "groups": [
    {
      "conjonction": "and",
      "conditions": [
        { "kind": "number", "columnSlug": "employee_count", "operator": "greaterThan", "value": 100 },
        { "kind": "string", "columnSlug": "email", "operator": "isNotEmpty" }
      ]
    }
  ]
}
```

> **`conjonction`，不是 `conjunction`。** 法语拼写是故意的，这是 CLI 中最昂贵的拼写错误：一个拼写错误的键不会报错——过滤器静默匹配无结果，你将得出数据为空的结论。在每次调用前用 Grep 搜索 JSON 中的 `conjunction`。

匹配所有记录的过滤器：`{"conjonction":"and","groups":[]}`。

## 在构建受众前确定规模

计数是免费的；对受众运行任何操作都需要付费。先确定规模，再决定。

```bash
# 1. 有多少记录匹配？——内联过滤器，不保存对象，返回 1 行
cargo-ai segmentation segment fetch \
  --model-uuid <uuid> \
  --filter '{"conjonction":"and","groups":[{"conjonction":"and","conditions":[
      {"kind":"number","columnSlug":"employee_count","operator":"greaterThan","value":100}]}]}' \
  --limit 1

# 2. 满意形状？将其保存为真正的受众。
cargo-ai segmentation segment create \
  --name "Mid-market accounts" \
  --model-uuid <uuid> \
  --filter '<same json>' \
  --column-slugs "name,domain,employee_count" \
  --tracking-column-slugs "employee_count,funding_stage"
```

`segment get <uuid>` 然后报告 `recordsCount` —— 权威的规模。在提议对分段进行付费运行前，引用该数字，而不是你自己的估计。

## 获取 vs 下载 vs 记录获取

| 命令 | 返回 | 用于 |
|---|---|---|
| `segment fetch --model-uuid --filter` | 记录内联为 JSON，分页 (`--fetching-limit`, `--fetching-offset`) | 检查少量行、计数、保存过滤器前预览 |
| `segment download --model-uuid --filter` | 完整数据集的签名 URL | 将整个受众交给用户或另一个工具——参考 [`../cargo-analytics/SKILL.md`](../cargo-analytics/SKILL.md) |
| `record fetch --model-uuid --ids <ids>` | 特定 ID 的记录 | 重新读取变更流刚告诉你的行 |

`segment fetch --sync` 在评估前刷新底层数据源；`--enrich` 返回连接/派生值。两者都需要时间，因此在检查规模时请禁用它们。

**切勿将大分段分页到对话中。** 使用 `--limit 3` 查看形状，然后 `download` 获取其余部分。

## 变更——增量流

每次分段同步时，Cargo 计算一个变更：成员如何变化。这是将静态列表转换为信号的东西。

```bash
# 这个分段有哪些增量？
cargo-ai segmentation change list --segment-uuid <segment-uuid>
# → { "changes": [ { "uuid", "totalRecordsCount", "addedRecordsCount",
#                    "updatedRecordsCount", "removedRecordsCount",
#                    "unchangedRecordsCount", "createdAt" } ] }

# 哪些记录实际进入该受众的增量中？
cargo-ai segmentation change fetch --uuid <change-uuid> --kinds added --limit 50
```

`--kinds` 在 `change fetch` 中是**必需的**，接受 `added`、`updated`、`removed` 或 `unchanged`（逗号分隔）。返回的行包含 `_kind`、`_id`、`_title` 和 `_time` 元数据列以及模型的自有列。

`updatedRecordsCount` 除非分段使用 `--tracking-column-slugs` 创建，否则始终为 `0` —— 跟踪列定义了“更新”的含义。在创建时设置它们，当分段用于监控动作时。

分段的最新的增量也内联在 `segment list` / `segment get` 作为 `lastChange`，因此“什么变化了？”的问题很少需要第二次调用。

## 谁使用分段

分段是输入，不是结果。一旦存在：

- **在其上运行操作** —— 跨所有成员批量连接操作或工作流：[`../cargo-orchestration/SKILL.md`](../cargo-orchestration/SKILL.md)。批量从分段中注册；抽样 10–20 条记录并明确批准后再注册整个受众。
- **在进入时触发播放** —— 触发器是分段的播放在记录进入时触发。播放触发器使用 `kind: "filter"` 并生成它们自己的 `GENERATED_PLAY_SEGMENT`；参考 [`../cargo-orchestration/references/examples/plays.md`](../cargo-orchestration/references/examples/plays.md)。
- **导出它** —— [`../cargo-analytics/SKILL.md`](../cargo-analytics/SKILL.md) (`segment download` 需要 `--model-uuid`，*不是* `--segment-uuid` —— 这是一个常见的 400 错误）。
- **监控它** —— 当受众为空、停滞或激增时发出警报：[`../cargo-observability/SKILL.md`](../cargo-observability/SKILL.md)。
- **作为 GTM 行动** —— 信号分段（工作变更、资金、技术意图）驱动 [`../cargo-gtm/SKILL.md`](../cargo-gtm/SKILL.md) 中的配方。
- **作为代码声明** —— 在 git 中应存在受众时，在 [`../cargo-project/SKILL.md`](../cargo-project/SKILL.md) 中使用 `defineSegment`。

## 注意事项

- **`conjonction`，绝不 `conjunction`** —— 静默无结果，无错误。
- **`segment download` 需要 `--model-uuid`，不是 `--segment-uuid`。** 过滤器随请求传递；分段 UUID 不是那里的有效输入。
- **`change fetch` 需要 `--uuid`（*变更* UUID）加上 `--kinds`。** 传递分段 UUID 返回 400。
- **`change list` 需要 `--segment-uuid`。** 调用它将返回 400，抱怨 `segmentUuid` 未定义。
- **`--help` 在 `change` 和 `record` 子命令上打印父命令的帮助** 而不是子命令的标志（CLI ≥ 1.0.48）。使用上面的快速参考；如果仍然有问题，请提交报告。
- **分段属于恰好一个模型。** 跨模型受众是关系 + 对连接列的过滤器，而不是两个分段。
- **`fromPlay: true` 分段由播放拥有。** 编辑一个会改变播放的目标；删除一个会破坏它。
- **`--limit` 在分段上限制成员**，它不是显示页大小——`--fetching-limit` 是页大小。

## 当 CLI 失败时

同一命令两次失败或行为与该技能矛盾时，请联系团队：

```bash
cargo-ai workspaceManagement report create \
  --title "<one-line summary>" \
  --description "<commands run, errorMessage verbatim, expected vs actual, UUIDs>"
```
