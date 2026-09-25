# Smartscape 迁移技能

此技能将 Dynatrace 传统和 Gen2 基于实体的 DQL 查询和查询模式迁移到基于 Smartscape 的等效查询。

在编写最终 DQL 之前，请先加载 **dt-dql-essentials** 技能，以便翻译后的查询也遵循当前的 DQL 语法规则。

此技能仅专注于面向 Smartscape 的 DQL 迁移。它不涵盖资产级别的迁移工作流。

## 查询目的分类

**从这里开始。** 正确的迁移策略取决于查询实际想要做什么——而不仅仅是它使用了哪些传统结构。

有三种不同的情况：

| # | 情况 | 传统反模式 | 迁移策略 |
| --- | --- | --- | --- |
| 1 | 基于实体条件的批量数据查询 | 在 timeseries、logs 或 metrics 查询的 `filter:` 中的 `classicEntitySelector(...)` 内联 | 首先解析实体条件为原始数据维度。Smartscape 是备用方案，不是默认方案。 |
| 2 | 使用实体子查询进行过滤的批量数据查询 | 在 `in [...]`、`lookup [...]` 或 `join [...]` 内部的 `fetch dt.entity.*` 来过滤外部批量数据查询 | 相同的维度优先策略。重写为原始维度过滤器或 `in [smartscapeNodes ...]` 子查询。 |
| 3 | 纯粹的实体列表查询 | 独立使用 `fetch dt.entity.*` 或作为主要结果源使用 | `smartscapeNodes` 是唯一有效的路径。不存在原始维度替代方案。 |

**决策：**

- **情况 1 或 2** — 加载 [references/mass-data-filtering-strategy.md](references/mass-data-filtering-strategy.md) 并完成 **所有步骤**，包括字段发现（步骤 2）和等效性验证（步骤 4）。不要跳过 `fieldsSnapshot` 门禁——它们决定了哪种方法是可行的。只有在需要实体类型映射或关系遍历来完成 Smartscape 子查询时，才回退到下面的迁移工作流。
- **情况 3** — 继续执行下面的迁移工作流和实体映射表。

> 注意：情况 3 有一个子情况，其中 `classicEntitySelector` 用于过滤 `fetch dt.entity.*` 返回的实体。这种情况很少见，遵循相同的 `smartscapeNodes` 路径——使用 [references/mass-data-filtering-strategy.md](references/mass-data-filtering-strategy.md) 步骤 1B 解析选择器条件，然后在 `smartscapeNodes` 中作为节点过滤器应用它们。

## 迁移工作流

对于 **情况 3**（纯粹的实体列表查询）以及在情况 1 和 2 中构建 Smartscape 子查询，请按以下顺序操作：

1. 识别传统输入模式：
   - `fetch dt.entity.*`
   - `classicEntitySelector(...)`
   - 关系字段访问，例如 `belongs_to[...]`、`runs[...]`、`instance_of[...]`
   - 使用 `dt.entity.*` 的信号或事件查询
2. 识别涉及的 传统实体类型。
3. 在下面的核心实体映射表中查找 Smartscape 替换。
4. 检查哪些传统 DQL 结构需要显式迁移。
5. 使用 Smartscape 基本结构重写查询：
   - `smartscapeNodes`
   - `smartscapeEdges`
   - `traverse`
   - `references`
   - `getNodeName()`
   - `getNodeField()`
6. 检查特殊情况、不支持的实体或 ID 假设。
7. 加载匹配的详细参考，针对特定的实体系列或迁移模式。

有关完整的迁移过程和输出预期，请加载 [references/migration-workflow.md](references/migration-workflow.md)。

## 核心实体映射表

首先使用此紧凑表格进行常见迁移。有关完整的映射集，请加载 [references/type-mappings.md](references/type-mappings.md)。

| 传统 / Gen2 实体 | Smartscape 字段 | Smartscape 节点类型 | 备注 |
| --- | --- | --- | --- |
| `dt.entity.host` | `dt.smartscape.host` | `HOST` | 标准主机映射 |
| `dt.entity.service` | `dt.smartscape.service` | `SERVICE` | 标准服务映射 |
| `dt.entity.process_group_instance` | `dt.smartscape.process` | `PROCESS` | 进程实例直接映射 |
| `dt.entity.container_group_instance` | `dt.smartscape.container` | `CONTAINER` | 容器组实例直接映射 |
| `dt.entity.kubernetes_cluster` | `dt.smartscape.k8s_cluster` | `K8S_CLUSTER` | Kubernetes 集群 |
| `dt.entity.kubernetes_node` | `dt.smartscape.k8s_node` | `K8S_NODE` | Kubernetes 节点 |
| `dt.entity.kubernetes_service` | `dt.smartscape.k8s_service` | `K8S_SERVICE` | Kubernetes 服务 |
| `dt.entity.cloud_application` | 多个工作负载字段 | 多个 Kubernetes 工作负载节点类型 | 映射到多个工作负载类型；加载云应用指南 |
| `dt.entity.cloud_application_instance` | `dt.smartscape.k8s_pod` | `K8S_POD` | 传统云应用实例变为 Pod |
| `dt.entity.cloud_application_namespace` | `dt.smartscape.k8s_namespace` | `K8S_NAMESPACE` | 命名空间映射 |
| `dt.entity.application` | `dt.smartscape.frontend` | `FRONTEND` | 前端应用映射 |
| `dt.entity.aws_lambda_function` | `dt.smartscape.aws.lambda_function` | `AWS_LAMBDA_FUNCTION` | 云函数实体映射 |

## 迁移过程中需要检查的 DQL 结构

这些传统结构通常需要显式重写：

| 传统结构 | 典型的 Smartscape 替换 | 备注 |
| --- | --- | --- |
| `entityName(x)` | `name` 或 `getNodeName(x)` | 直接查询节点时优先使用 `name` |
| `entityAttr(x, "...")` | 直接节点字段或 `getNodeField(x, "...")` | 当可用时优先使用直接字段 |
| `classicEntitySelector(...)` | 节点过滤器加上 `traverse` | 从受限端开始；对于批量数据查询，请先查看 mass-data-filtering-strategy.md |
| 信号查询中的 `dt.entity.*` | `dt.smartscape.*` | 适用于 `by`、`filter`、`fieldsAdd`、`expand` 和相关子句 |
| `belongs_to[...]`、`runs[...]`、`instance_of[...]` | `traverse` 或 `references[...]` | `references` 仅适用于静态边 |
| 传统实体 ID 过滤器 | Smartscape `id` | 不要盲目重用传统 ID |
| `affected_entity_ids` 和 `affected_entity_types` | `smartscape.affected_entities` | 一个记录数组替换了两个并行的数组；每个记录都有 `id`、`type` 和 `name` |

有关详细的逐函数指南，请加载 [references/dql-function-migration.md](references/dql-function-migration.md)。

## 特殊情况

不要逐字翻译这些模式：

- **主机组** — 没有独立的 Smartscape 实体；使用 `HOST` 上的字段
- **进程组** — 没有独立的 Smartscape 实体；使用 `PROCESS` 上的字段
- **容器组** — 没有独立的 Smartscape 实体；如果需要，保留输出形状并使用占位符
- **传统 ID** — 传统实体 ID 不会自动传递到 Smartscape
- **计划的、缺失的或未计划的映射** — 在假设直接支持之前，请检查完整的映射表

在迁移这些模式之前，请加载 [references/special-cases.md](references/special-cases.md)。

## 实体导向指南

当迁移以特定实体系列为中心时，请加载匹配的详细指南：

- [references/entity-host.md](references/entity-host.md)
- [references/entity-service.md](references/entity-service.md)
- [references/entity-process.md](references/entity-process.md)
- [references/entity-container.md](references/entity-container.md)
- [references/entity-kubernetes.md](references/entity-kubernetes.md)
- [references/entity-cloud-application.md](references/entity-cloud-application.md)

每个指南解释：

- 传统实体代表什么
- Smartscape 替换是什么
- 通常哪些字段会变化
- 如何迁移关系
- 常见示例和陷阱

## 参考

- [references/README.md](references/README.md) — 参考索引和阅读指南
- [references/mass-data-filtering-strategy.md](references/mass-data-filtering-strategy.md) — **对于情况 1 和 2 从这里开始。** 强制步骤：解析条件、运行字段发现、选择方法、编写查询、验证等效性
- [references/auto-tagging-field-mapping.md](references/auto-tagging-field-mapping.md) — 将自动标记规则条件键映射到语义词典字段（批量数据和 Smartscape 节点属性）
- [references/entity-selector-predicates.md](references/entity-selector-predicates.md) — `classicEntitySelector` 表达式的完整谓词词汇表
- [references/migration-workflow.md](references/migration-workflow.md) — 端到端迁移过程和输出预期
- [references/type-mappings.md](references/type-mappings.md) — 完整的传统到 Smartscape 类型字段映射
- [references/dql-function-migration.md](references/dql-function-migration.md) — 如何迁移传统 DQL 函数和模式
- [references/relationship-mappings.md](references/relationship-mappings.md) — 有效的 Smartscape 边和遍历指南
- [references/special-cases.md](references/special-cases.md) — 非逐字和不支持的实体迁移
- [references/quick-reference.md](references/quick-reference.md) — 紧凑规则和陷阱
- [references/examples.md](references/examples.md) — 迁移前/后的示例
