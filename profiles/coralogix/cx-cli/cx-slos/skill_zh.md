# SLO 管理技能

**SLO**（服务等级目标）为服务定义了一个可靠性目标——例如“28天内99.9%的请求成功”。使用此技能检查SLO定义，判断其是否健康，并管理其生命周期。

## 命令行指令

| 命令 | 目的 |
|---|---|
| `cx slos list` | 列出所有SLO定义 |
| `cx slos get <id>` | 通过ID获取单个SLO |
| `cx slos create --from-file <path>` | 从JSON定义创建SLO [需要 `--yes`] |
| `cx slos update --from-file <path>` | 用JSON替换SLO定义 [需要 `--yes`] |
| `cx slos delete <id>` | 删除SLO [需要 `--yes`] |

- 所有命令支持 `-o json` 以获取结构化输出，以及 `-p <profile>`（可重复）用于多配置分发。
- `create`/`update` 从 `--from-file <path>` 读取，或 `-` 表示标准输入（默认）。
- `create`、`update` 和 `delete` 是写操作，并在非交互式/代理模式下需要 `--yes`。

## SLO 定义

每个SLO显示的字段：

| 字段 | 含义 |
|---|---|
| `name` | 人类可读的SLO名称 |
| `description` | 可选描述 |
| `targetThresholdPercentage` | 目标值，例如 `99.9` |
| `sloType` | `SLO_TYPE_REQUEST`（基于请求）或 `SLO_TYPE_WINDOW`（基于窗口） |
| `sloTimeFrame` | 滚动窗口，例如 `SLO_TIME_FRAME_7_DAYS`、`SLO_TIME_FRAME_28_DAYS` |
| `productType` | SLO计算所依据的支柱，例如 `SLO_PRODUCT_TYPE_APM` |

## 监控SLO健康状态

```bash
# 所有SLO及其目标和窗口
cx slos list -o json | jq '[.[] | {name, targetThresholdPercentage, sloType, sloTimeFrame}]'

# 完整检查单个SLO
cx slos get <slo-id> -o json
```

将实时达成情况与 `targetThresholdPercentage` 进行比较，以判断SLO是否健康或正在消耗错误预算。**基于请求**的SLO测量有效事件的比例；**基于窗口**的SLO测量有效时间窗口的比例。在初步处理后，切换到 `cx-telemetry-querying` 技能，在日志、跟踪或指标中查找违规的根本原因。

## 创建和更新SLO

编写SLO最安全的方式是重新传递现有的SLO——从 `get` 返回的确切字段形状模板，而不是手写JSON：

```bash
# 从现有SLO模板，编辑后创建
cx slos get <existing-slo-id> -o json > slo.json
# 编辑 slo.json：更改名称、targetThresholdPercentage、sloType、sloTimeFrame 等
cx slos create --from-file slo.json --yes

# 替换现有定义
cx slos update --from-file slo.json --yes
```

`update` 和 `delete` 报告受影响的告警ID (`effectedSloAlertIds`)，因此请查看该列表——更改或删除SLO可能会禁用其关联的告警。

## 关键原则

- **检查达成情况与目标，而不仅仅是存在**——99.91%达成率对应99.9%目标的SLO几乎没有剩余错误预算，需要关注以避免违规。
- **重新传递定义**——从 `cx slos get` 模板创建/更新负载，而不是手写JSON，以保持API期望的确切字段形状。
- **`create`/`update`/`delete` 在代理/非交互式模式下需要 `--yes`**。
- **关注受影响的告警**——`update`/`delete` 返回 `effectedSloAlertIds`；删除SLO可能会静音其告警。
- **使用 `-p <profile>`（可重复）进行多配置分发**，以跨环境比较SLO。

## 相关技能

- **`cx-alerts`** — 当SLO错误预算消耗时触发的告警定义。
- **`cx-telemetry-querying`** — 调查SLO违规背后的日志、跟踪和指标。
- **`cx-cases`** — 将告警事件分组到服务中的案例。
