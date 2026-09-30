---
name: cx-service-catalog
description: 使用 `cx service-catalog` CLI 查询 Coralogix 服务目录（APM v2 实体）——发现实体类型、列出已知实体、检查其架构，并拉取服务、数据库、操作、JVM 和 Kubernetes Pod 的聚合或时间序列数据。当用户询问“列出服务”、“有哪些实体类型”、“显示服务延迟”、“检查服务的错误率”、“哪些 Pod 使用了最多内存”、“数据库操作性能”、“JVM GC 停顿”、“服务随时间变化的健康状况”、“按延迟比较服务”、“此实体类型有哪些可用列”、“服务目录架构”，或希望探索 APM 实体及其指标时使用。
---

# 服务目录技能

使用此技能发现和查询**服务目录实体**——服务、数据库、操作、数据库操作、JVM、JVM GC、Kubernetes Pod 和事务——及其列式指标（延迟、错误率、健康度、资源使用情况等），通过 v2 服务目录 API。

## CLI 命令

| 命令 | 目的 | 关键标志 |
|---|---|---|
| `cx service-catalog entity-types` | 列出此账户有数据的实体类型 | - |
| `cx service-catalog schema <entity-type>` | 单个实体类型的列/标签模式 | - |
| `cx service-catalog entities <entity-type>` | 已知的单个类型实体（例如服务名称） | - |
| `cx service-catalog data <entity-type>` | 跨所有该类型实体的聚合列数据 | `--start`, `--end`, `--column`（必需，可重复）；`--group-by`, `--filter`, `--aggregation`, `--limit`, `--sort-column`, `--sort-order` |
| `cx service-catalog entity-data <entity-type> <entity-id>` | 单个命名实体的列数据（下钻） | `--start`, `--end`, `--column`（必需，可重复）；`--group-by`, `--filter`, `--aggregation` |

- 所有命令都是**只读**的，并支持 `-o json` / `-o toon` 用于结构化输出。
- **实体类型接受简写形式**：`service`, `database`, `operation`, `database-operation`, `jvm`, `jvm-gc`, `k8s-pod`, `transaction`（不区分大小写，使用连字符或下划线）。完整的 proto 名称 (`ENTITY_TYPE_K8S_POD`) 也有效。客户端会在发出任何请求之前拒绝未知值。
- `--start`/`--end` 接受 `now`, `now-1h`-风格的相对表达式，或 RFC3339 时间戳。
- `--column` 是**必需**且可重复的——首先使用 `cx service-catalog schema <entity-type>` 发现有效的列 ID；API 会拒绝未知的列。
- `--filter label=value1,value2` 是可重复的**跨不同标签**（按 AND 组合过滤）；使用逗号组合同一标签的多个值，而不是重复标志——重复标签会被客户端拒绝。
- `--aggregation` 是 `table`（与 `--limit`/`--sort-column`/`--sort-order` 结合时的默认行为）或 `timeseries`。**`--limit`, `--sort-column`, 和 `--sort-order` 仅适用于 `table`**——后端会静默忽略 `timeseries` 的这些标志，因此 CLI 会在前端拒绝这种组合，而不是发送标志被忽略的请求。
- `entity-data` 会为您对实体 ID 进行百分比编码——将其作为 `entities` 返回的值传递（例如 `checkout/api`），如果其中包含 `/` 则需要加引号。

## 检查工作流

四个步骤，只是因为每个步骤都为下一个步骤提供输入：
`entity-types` 提供有效的 `<entity-type>` 值，`schema` 提供有效的 `--column` ID，`entities` 提供用于下钻的 `entity-id`。

1. **发现存在的实体类型**——不要猜测，它们因账户而异：

   ```bash
   cx service-catalog entity-types -o json
   ```

2. **检查一个实体类型的模式**以找到有效的列 ID 和可过滤/可分组的标签：

   ```bash
   cx service-catalog schema service -o json
   ```

3. **列出的该类型已知实体**（例如服务名称）：

   ```bash
   cx service-catalog entities service -o json
   ```

4. **查询数据**——跨所有实体聚合，或针对单个实体范围。列 ID、过滤/分组标签和下面的实体 ID 都是占位符——始终用 `schema`/`entities` 返回的值替换有关实体类型的占位符，它们因账户和实体类型而异：

   ```bash
   cx service-catalog data <entity-type> --start now-1h --end now \
     --column <column-id> --column <column-id> -o json

   cx service-catalog entity-data <entity-type> <entity-id> --start now-1h --end now \
     --column <column-id> -o json
   ```

## 示例

下面的命令使用 `service` 和 `k8s-pod` 作为具体示例，但每个 `<column-id>`、`<filterable-label>`、`<groupable-label>` 和 `<entity-id>` 必须来自该实体类型自己的 `schema`/`entities` 输出——永远不要假设一个实体类型的列或标签存在于另一个实体类型中。

### 过去一小时按指标排名前 5 的实体

```bash
cx service-catalog schema service -o json  # 首先发现列 ID
cx service-catalog data service --start now-1h --end now \
  --column <column-id> --aggregation table \
  --sort-column <column-id> --sort-order desc --limit 5 -o json
```

### 过滤到单个标签值

```bash
cx service-catalog schema service -o json  # 首先发现可过滤标签
cx service-catalog data service --start now-1h --end now \
  --column <column-id> --column <column-id> \
  --filter <filterable-label>=<value> -o json
```

### 按标签分组

```bash
cx service-catalog schema service -o json  # 首先发现可分组标签
cx service-catalog data service --start now-1h --end now \
  --column <column-id> --group-by <groupable-label> -o json
```

### Kubernetes Pod 资源饱和度

```bash
cx service-catalog schema k8s-pod -o json  # 首先发现列 ID
cx service-catalog data k8s-pod --start now-1h --end now \
  --column <column-id> --column <column-id> --column <column-id> -o json
```

### 单个实体的延迟随时间变化

```bash
cx service-catalog entities service -o json  # 首先发现实体 ID
cx service-catalog entity-data service <entity-id> --start now-24h --end now \
  --column <column-id> --aggregation timeseries -o json
```

### 仅行数据

```bash
# 表格响应位于 .rows 下；时间序列位于 .series 下
cx service-catalog data service --start now-1h --end now \
  --column <column-id> -o json | jq '.rows'
```

## 关键原则

- **先发现后查询**——`entity-types` 和 `schema` 是廉价的，在花费一个 `data`/`entity-data` 调用猜测之前回答“这里有哪些有效的值”。
- **`--column` 值是按实体类型区分的**——对 `service` 有效的列可能不存在于 `k8s-pod` 中；在切换实体类型时始终重新检查 `schema`。
- **格式错误的响应是错误，而不是静默的空结果**——既不是值也不是错误的列会大声失败，而不是产生部分或空行，因此非零退出意味着调查，而不是“无数据”。
- **列级错误不是命令失败**——单个列可以以 `{"error": "..."}` 的形式返回，而其他行成功（例如，仅该列的查询超时）；在假设整个请求失败之前先检查每列。
- **`table` 与 `timeseries` 是互斥的结果形状**——`table` 响应是平铺的行，适合 `-o json | jq '.rows'`；`timeseries` 响应按系列嵌套数据点，最好以原始 JSON 的形式消费，而不是强行转换为表格。
- **使用 `-o json` 与 `jq` 进行过滤**；使用 `-o toon` 在代理上下文中进行标记高效的输出。
- **多配置分叉**适用于每个子命令——重复 `-p <profile>` 以跨账户比较相同的实体类型/数据；当给出多个时，行和系列会带有 `profile` 标签。

## 相关技能

- **`cx-infra`**——基础设施资源健康（主机、容器）是服务目录实体健康的不同概念；使用 `cx-infra` 进行主机/实例级监控，并使用此技能进行应用/服务级 APM 实体。
- **`cx-telemetry-querying`**——一旦从此技能的命令中显示服务或 Pod 名称，就切换到原始遥测：`cx logs "filter $l.subsystemname == '<service>'"` 或 `cx search-fields "<name>" -s value` 以查找相关的日志/跨度字段。将延迟或错误尖峰与底层日志/跨度相关联。
- **`cx-alerts`**——`cx alerts list --name "<service-name>"` 查找与此技能显示的服务匹配的告警定义。
- **`cx-dashboards`**——`cx dashboards search "<service-name> ..."` 查找围绕此处找到的服务构建的仪表板。
