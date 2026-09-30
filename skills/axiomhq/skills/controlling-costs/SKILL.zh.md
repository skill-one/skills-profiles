---
name: controlling-costs
description: 分析 Axiom 查询模式以查找未使用的数据，然后构建仪表板并监控以实现成本优化。在要求降低 Axiom 成本、查找未使用的列或字段值、识别数据浪费或跟踪摄取支出时使用。
---

# Axiom 成本控制

仪表盘、监控和浪费识别，用于 Axiom 使用优化。

## 开始前

1.  加载所需技能：
   ```
   skill: axiom-sre
   skill: building-dashboards
   ```

   building-dashboards 提供：`dashboard-list`，`dashboard-get`，`dashboard-create`，`dashboard-update`，`dashboard-delete`

2.  找到审计数据集。首先尝试 `axiom-audit`：
   ```apl
   ['axiom-audit']
   | where _time > ago(1h)
   | summarize count() by action
   | where action in ('usageCalculated', 'runAPLQueryCost')
   ```
   - 如果未找到 → 询问用户。常用名称：`axiom-audit-logs-view`，`audit-logs`
   - 如果找到但没有 `usageCalculated` 事件 → 错误的数据集，询问用户

3.  验证 `axiom-history` 访问权限（第 4 阶段所需）：
   ```apl
   ['axiom-history'] | where _time > ago(1h) | take 1
   ```
   如果未找到，第 4 阶段优化将无法工作。

4.  与用户确认：
   - 部署名称？
   - 审计数据集名称？
   - 合同每日 TB 限制？（第 3 阶段监控所需）

5.  在所有以下命令中替换 `<deployment>` 和 `<audit-dataset>`。

**提示：**
- 运行任何脚本时使用 `-h` 获取完整用法
- 不要将脚本输出管道到 `head` 或 `tail` — 会导致 SIGPIPE 错误
- 需要 `jq` 进行 JSON 解析
- 使用 axiom-sre 的 `axiom-query` 进行临时 APL，不要直接使用 CLI

## 应运行哪些阶段

| 用户请求               | 运行这些阶段     |
|------------------------|------------------|
| "降低成本" / "查找浪费" | 0 → 1 → 4        |
| "设置成本控制"         | 0 → 1 → 2 → 3    |
| "部署仪表盘"           | 0 → 2            |
| "创建监控"             | 0 → 3            |
| "检查漂移"             | 仅 0             |

---

## 第 0 阶段：检查现有设置

```bash
# 现有仪表盘？
dashboard-list <deployment> | grep -i cost

# 现有监控？
axiom-api <deployment> GET "/v2/monitors" | jq -r '.[] | select(.name | startswith("Cost Control:")) | "\(.id)\t\(.name)"'
```

如果找到，使用 `dashboard-get` 获取并与 `templates/dashboard.json` 进行比较以检查漂移。

---

## 第 1 阶段：发现

```bash
scripts/baseline-stats -d <deployment> -a <audit-dataset>
```

捕获每日摄取统计信息并生成 **分析队列**（第 4 阶段所需）。

---

## 第 2 阶段：仪表盘

```bash
scripts/deploy-dashboard -d <deployment> -a <audit-dataset>
```

创建包含：摄取趋势、消耗率、预测、浪费候选、顶级用户等内容的仪表盘。详情请参阅 `reference/dashboard-panels.md`。

---

## 第 3 阶段：监控

**需要合同。** 你必须有预检步骤 4 中的合同限制。

### 第 1 步：列出可用通知器

```bash
scripts/list-notifiers -d <deployment>
```

向用户展示列表并询问他们希望用于成本警报的通知器。
如果他们不想接收通知，则无需 `-n` 即可继续。

### 第 2 步：创建监控

```bash
scripts/create-monitors -d <deployment> -a <audit-dataset> -c <contract_tb> [-n <notifier_id>]
```

创建 3 个监控：

1. **总摄取警戒** — 当每日摄取 >1.2 倍合同 OR 7 天平均值增长 >15% 相对于基线时发出警报
2. **按数据集峰值** — 鲁棒的 z 分数检测，按数据集发出警报并归因
3. **查询成本峰值** — 带有 30 天基线、5 天排除间隙、基于持续性的门控（median_z > 3, p25_z > 2.5）

峰值监控使用 `notifyByGroup: true`，因此每个数据集都会触发单独的警报。

阈值推导详情请参阅 `reference/monitor-strategy.md`。

---

## 第 4 阶段：优化

### 获取分析队列

如果尚未执行，运行 `scripts/baseline-stats`。它输出一个优先级列表：

| 优先级 | 含义     |
|--------|----------|
| P0⛔   | 前 3 个按摄取 OR >10% 总量 — 强制执行 |
| P1     | 从未查询 — 强力候选 |
| P2     | 很少查询（Work/GB < 100）— 可能是浪费 |

**Work/GB** = 查询成本（GB·ms） / 摄取（GB）。越低 = 数据价值越低。

### 按顺序分析数据集

从上到下工作。对于每个数据集：

**第 1 步：列分析**
```bash
scripts/analyze-query-coverage -d <deployment> -D <dataset> -a <audit-dataset>
```

如果 0 查询 → 建议删除，移至下一个。

**第 2 步：字段值分析**

从建议列表中选择一个字段（通常是 `app`，`service` 或 `kubernetes.labels.app`）：
```bash
scripts/analyze-query-coverage -d <deployment> -D <dataset> -a <audit-dataset> -f <field>
```

注意高量但从未查询的值（⚠️ 标记）。

**第 3 步：处理空值**

如果 `(empty)` 占比 >5%，你必须使用替代字段（例如，`kubernetes.namespace_name`）进行深入分析。

**第 4 步：记录建议**

对于每个数据集，记录：名称、摄取量、Work/GB、顶级未查询值、操作（删除/SAMPLE/保留）、预计节省。

### 完成条件

所有 P0⛔ 和 P1 数据集分析完成。然后使用 `reference/analysis-report-template.md` 编写报告。

---

---

## 清理

```bash
# 删除监控
axiom-api <deployment> GET "/v2/monitors" | jq -r '.[] | select(.name | startswith("Cost Control:")) | "\(.id)\t\(.name)"'
axiom-api <deployment> DELETE "/v2/monitors/<id>"

# 删除仪表盘
dashboard-list <deployment> | grep -i cost
dashboard-delete <deployment> <id>
```

**注意：** 运行 `create-monitors` 两次会创建重复项。重新部署时如果需要，请先删除现有监控。

---

## 参考

### 审计数据集字段

| 字段               | 描述             |
|--------------------|------------------|
| `action`           | `usageCalculated` 或 `runAPLQueryCost` |
| `properties.hourly_ingest_bytes` | 每小时摄取字节数 |
| `properties.hourly_billable_query_gbms` | 每小时查询成本 |
| `properties.dataset` | 数据集名称       |
| `resource.id`      | 组织 ID         |
| `actor.email`      | 用户邮箱         |

### 常用字段（值分析）

| 数据集类型       | 主要字段       | 替代方案         |
|------------------|----------------|------------------|
| Kubernetes 日志   | `kubernetes.labels.app` | `kubernetes.namespace_name`，`kubernetes.container_name` |
| 应用日志         | `app` 或 `service` | `level`，`logger`，`component` |
| 基础设施         | `host`          | `region`，`instance` |
| 追踪             | `service.name`  | `span.kind`，`http.route` |

### 单位与转换

- 脚本使用 **TB/天**
- 仪表盘过滤器使用 **GB/月**

| 合同             | TB/天          | GB/月          |
|------------------|----------------|----------------|
| 5 PB/月          | 167            | 5,000,000      |
| 10 PB/月         | 333            | 10,000,000     |
| 15 PB/月         | 500            | 15,000,000     |

### 优化操作

| 信号             | 操作         |
|------------------|--------------|
| Work/GB = 0      | 删除或停止摄取 |
| 高量未查询值     | 样本或降低日志级别 |
| 系统命名空间中的空值 | 摄取时过滤或接受 |
| WoW 峰值         | 检查最近部署   |
