# Cargo CLI — 存储

数据层管理：检查和修改模型、数据集、列、关系、统一和记录，并对工作区存储运行 SQL 查询。

> 参考 `references/response-shapes.md` 获取完整的 JSON 响应结构。
> 参考 `references/troubleshooting.md` 获取常见错误及其解决方法。
> 参考 `references/examples/models.md` 获取模型 CRUD、DDL 检查和模式发现示例。
> 参考 `references/examples/datasets.md` 获取数据集列表和导航示例。
> 参考 `references/examples/columns.md` 获取列创建和管理示例。
> 参考 `references/examples/queries.md` 获取 `storage query execute` / `storage query download` SQL 示例（WHERE、聚合、连接、分页、导出）。
> 参考 `references/examples/ingest-webhook.md` 获取摄入（webhook 驱动）模型——推导 webhook URL 并 POST 记录。

## 初始化

已经登录 (`cargo-ai whoami` 返回工作区)？跳到下一节。

```bash
npm install -g @cargo-ai/cli            # 没有全局安装？为每个命令前缀 `npx @cargo-ai/cli`
cargo-ai login --email you@company.com  # 通过邮件验证，无需浏览器；首次使用时创建账户
                                        # 替代方案：--oauth（浏览器） · --token <api-token>（CI）
cargo-ai whoami                         # 在任何写入操作前确认活动工作区
```

每个命令都会将 JSON 打印到标准输出；失败时以非零状态退出并打印 `{"errorMessage": "..."}`。任何创建运行或批次的操作都是异步的——传递 `--wait-until-finished` 或轮询匹配的 `get`。当完整技能包安装完成后，[`../cargo/references/prerequisites.md`](../cargo/references/prerequisites.md) 会添加 CLI 版本固定、令牌范围和管理员专用的界面。

## 先发现资源

始终先列出再检查或修改。

```bash
cargo-ai storage dataset list              # 所有数据集（uuid，slug）
cargo-ai storage model list                # 所有模型（uuid，名称，slug，列，datasetUuid）
# `model list` 不带标志——改用过滤其输出：
cargo-ai storage model list | jq '[.models[] | select(.datasetUuid == "<uuid>")]' 
```

**在 UI 中获取：** 模型位于 `app.getcargo.io/workspaces/<WORKSPACE_UUID>/models/<MODEL_UUID>`。从 `cargo-ai whoami` 下的 `workspace.uuid` 获取 `<WORKSPACE_UUID>`。

## 快速参考

```bash
cargo-ai storage model list
cargo-ai storage model get <model-uuid>
cargo-ai storage model get-ddl <model-uuid>
cargo-ai storage dataset list
cargo-ai storage column list --model-uuid <uuid>
cargo-ai storage relationship list
cargo-ai storage record list --model-uuid <uuid>
cargo-ai storage query execute "SELECT * FROM default.companies LIMIT 10"
cargo-ai storage query download --query "SELECT * FROM default.companies"
```

## 模型

模型是工作区中的结构化表格（例如 Companies，Contacts）。

```bash
# 列出所有模型
cargo-ai storage model list

# 列出数据集中的模型——每个模型都包含 `datasetUuid`，且
# `model list` 没有自身的标志，所以客户端过滤
cargo-ai storage model list | jq '[.models[] | select(.datasetUuid == "<uuid>")]' 

# 获取单个模型（包括列）
cargo-ai storage model get <model-uuid>

# 获取 DDL（完整模式，表名和 SQL 方言）
cargo-ai storage model get-ddl <model-uuid>
# → 用于列发现和 SQL 方言（BigQuery vs Snowflake）在编写查询之前

# 创建模型
cargo-ai storage model create \
  --slug contacts \
  --name "Contacts" \
  --dataset-uuid <uuid> \
  --extractor-slug <extractor-slug> \
  --config '{}'

# 更新模型
cargo-ai storage model update --uuid <model-uuid> --name "New Name"

# 删除模型
cargo-ai storage model remove <model-uuid>
```

**查询：** 使用 `cargo-ai storage query execute "<sql>"`（或 `storage query download --query "<sql>"` 用于完整导出）对存储运行 SQL。表引用为 `<datasetSlug>.<modelSlug>`（例如 `default.companies`）并在底层存储表下重写。见下文 [使用 SQL 查询](#query-with-sql)。

## 摄入模型（webhook 驱动）

一个提取器具有 `mode.kind === "ingest"`——`http.listenHook` 和
朋友——的模型是通过**推送**记录到 Cargo 来填充的。应用在模型设置屏幕上显示 "Webhook URL"；**没有 CLI 命令或 API 字段返回它**，但它是由 CLI 已经暴露的值组合而成的：

```
<baseUrl>/v1/models/<model-uuid>/records/ingest?token=<api-token>
```

```bash
MODEL_UUID=<model-uuid>
BASE=$(cargo-ai whoami | jq -r '.baseUrl')
TOKEN=$(cargo-ai workspaceManagement token list | jq -r '.tokens[0].token')
echo "$BASE/v1/models/$MODEL_UUID/records/ingest?token=$TOKEN"
```

首先检查提取器的模式——当它报告 `"autoIngest": true`（calendly，
smartlead，instantlyV2，heyReach，cargo signals）时，Cargo 会自行向提供者注册钩子，URL 必须**不**分发。完整流程、有效负载形状和限制：`references/examples/ingest-webhook.md`。

## 数据集

数据集是模型的逻辑分组。

```bash
# 列出所有数据集
cargo-ai storage dataset list

# 获取单个数据集
cargo-ai storage dataset get <dataset-uuid>
```

## 列

列定义模型的模式。

```bash
# 列出模型的列
cargo-ai storage column list --model-uuid <uuid>

# 创建列
cargo-ai storage column create \
  --model-uuid <uuid> \
  --column '{"slug":"my_column","type":"string","label":"My Column","kind":"custom"}'

# 更新列（传递完整的列对象——列由 slug 而非 UUID 标识）
cargo-ai storage column update \
  --model-uuid <uuid> \
  --column '{"slug":"my_column","type":"string","label":"Updated Label","kind":"custom"}'

# 删除列
cargo-ai storage column remove --model-uuid <uuid> --column-slug <slug>

# 重新排序列（移动到特定索引）
cargo-ai storage column reorder --model-uuid <uuid> --column-slug <slug> --to-index 2
```

列类型：`string`，`number`，`boolean`，`date`，`object`，`array`，`vector`，`any`。

列类型：`custom`（用户定义），`computed`（其他列的表达式），`metric`（从相关模型聚合），`lookup`（通过连接从相关模型拉取单个字段）。

## 预览你构建的内容

列列表不会告诉用户模型是否正确——行会。两个检查点（全局约定位于 [`../cargo/references/interaction.md`](../cargo/references/interaction.md) §4）：

**1. `model create` / `column create` 后立即——显示模式，不显示行。** 新模型为空；这里 `LIMIT 10` 返回空结果并被视为失败。改为以紧凑表格形式回显列（列，类型，将填充的内容）。

**2. 数据到达后——显示行。** 模型中写入后，预览它：

```bash
cargo-ai storage query execute \
  "SELECT * FROM <dataset-slug>.<model-slug> LIMIT 10"
```

显示约 10 行，仅包含有意义的列。存储查询是免费的，所以这几乎不成本——而且这是用户能实际看到他们构建内容的第一个时刻。当播放填充*新*列时，在记录的标识字段（`name`，`domain`）旁边预览该列，以便填充与未填充一目了然。

如果预览为空或所有为空时不应如此，这是一个发现——而不是报告写入成功。见 [`cargo-diagnostics`](../cargo-diagnostics/SKILL.md) 追踪原因。

## 关系

关系将模型连接在一起（例如 Contacts 属于 Companies）。它们由 CLI 编写，而不仅限于 UI。

`relationship list` 不带标志——它返回工作区中的每个关系。客户端过滤 `fromModelUuid` / `toModelUuid`。

```bash
cargo-ai storage relationship list
```

**`relationship set` 替换数据集的整个关系集。** 它接受一个数据集和其中应存在的完整列表：带有 `uuid` 的条目会更新，没有的会创建，而**任何现有关系其 `uuid` 未出现在负载中都会被删除**。向具有五个关系的数据集发送一个关系会删除其他四个。始终先 `list`，然后发送完整的数组并添加你的修改：

```bash
cargo-ai storage relationship set \
  --dataset-uuid <dataset-uuid> \
  --relationships '[
    {"uuid":"<existing-uuid>","fromModelUuid":"<contacts-uuid>","fromColumnSlug":"account_id","toModelUuid":"<companies-uuid>","toColumnSlug":"id","relation":"manyToOne"},
    {"fromModelUuid":"<deals-uuid>","fromColumnSlug":"company_id","toModelUuid":"<companies-uuid>","toColumnSlug":"id","relation":"manyToOne"}
  ]'
```

`relation` 是 `oneToOne`，`manyToOne` 或 `oneToMany`。两个模型必须存在于你传递的数据集中——关系永远不会跨越数据集，所以响应中的 `fromDatasetUuid` 和 `toDatasetUuid` 始终等于 `--dataset-uuid`。

失败原因：`datasetNotFound`；`invalidRelationships`（无法解析的列 slug 或模型 UUID，或重复——包括反向相同的对）；`modelNotCompatible`（见下文）。

**统一模型拒绝手动关系。** 在原生数据集中，统一模型的关系在同步期间生成，所以将其作为 `fromModelUuid` 或 `toModelUuid` 返回 `modelNotCompatible`。这些自动生成的行也排除了上述替换，所以 `set` 调用无法删除它们。

## 统一

统一是将来自多个源模型的记录合并为一个规范账户/联系人——并且它**可以通过 CLI 配置**，通过 `model update` 上的 `--unification`。传递 `null` 清除它。

```bash
# 连接器驱动：集成决定记录如何统一
cargo-ai storage model update --uuid <model-uuid> --unification '{"source":"integration"}'

# 自定义：你命名类型、匹配键，并可选地指定父级
cargo-ai storage model update --uuid <model-uuid> --unification '{
  "source": "custom",
  "type": "account",
  "uniqueColumns": [{"slug":"domain","reference":"domain"}],
  "selectedColumnSlugs": ["name","industry","employee_count"],
  "parent": {"kind":"model","columnSlug":"account_id","parentModelUuid":"<accounts-uuid>"}
}'
```

| 字段 | 适用范围 | 含义 |
|---|---|---|
| `source` | 两者 | `integration`（连接器定义）或 `custom` |
| `type` | 自定义 | `account`，`contact`，`accountEvent`，`contactEvent` |
| `uniqueColumns` | 自定义 | 匹配键——每个列 `{slug, reference}`。这是决定哪些行是同一实体的内容 |
| `selectedColumnSlugs` | 自定义 | 载入统一模型的列。全部省略 |
| `timeColumnSlug` | 自定义 | 事件时间戳——用于两种 `*Event` 类型 |
| `parent` | 自定义 | 将联系人/事件链接到其账户：`{"kind":"model","columnSlug":…,"parentModelUuid":…}` 或 `{"kind":"reference","columnSlug":…,"reference":…}` |
| `filter` | 自定义 | 限制哪些行统一的分割过滤器——与分段相同的 `conjonction` 形状 |

**编写配置不会重新计算任何内容。** 统一行由模型的同步运行重建，所以更新后跟随一个运行并轮询它：

```bash
cargo-ai storage run create --model-uuid <model-uuid>
cargo-ai storage run list --model-uuid <model-uuid>
```

从 `storage model get <uuid>` 获取当前配置 → `unification`（模型不统一时为 `null`）。运行完成后，使用 `storage query execute` 检查行数，再将其视为完成——过于狭窄的 `uniqueColumns` 会导致合并不足，过于宽泛的会导致不同实体合并，两者看起来都像成功运行。

## 记录

```bash
# 列出模型中的记录
cargo-ai storage record list --model-uuid <uuid>
```

对于高级记录查询（过滤、排序、分页），使用 `cargo-orchestration` 技能的 `segmentation segment fetch`。

## 使用 SQL 查询

使用 `storage query execute` 对工作区存储运行 SQL。表引用为 `<datasetSlug>.<modelSlug>`（例如 `default.companies`）并在底层存储表下重写——无需 DDL 查找表名。

```bash
cargo-ai storage query execute \
  "SELECT name, domain FROM default.companies LIMIT 10"
# → 成功时返回 { "rows": [...] }；失败时非零退出并返回 { "errorMessage": "..." } 
```

对于完整导出，使用 `storage query download`——它返回指向 CSV（默认）或 Parquet 文件的签名 URL：

```bash
cargo-ai storage query download \
  --query "SELECT name, domain, revenue FROM default.companies ORDER BY revenue DESC"

cargo-ai storage query download \
  --query "SELECT * FROM default.companies" --format parquet
```

从 `storage column list --model-uuid <uuid>` 获取列 slug（或运行 `storage model get-ddl <model-uuid>` 获取完整模式和 SQL 方言）。使用 SQL 中的 `LIMIT` / `OFFSET` 直接分页大型结果集。

见 `references/examples/queries.md` 获取 WHERE 子句、聚合、连接、日期查询、分页和错误时返回的失败形状。

## 帮助

每个命令支持 `--help`：

```bash
cargo-ai storage model list --help
cargo-ai storage column create --help
cargo-ai storage relationship set --help
cargo-ai storage query execute --help
cargo-ai storage query download --help
```
