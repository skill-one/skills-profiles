---
name: coralogix-docs
description: '使用 **`cx docs search`** 和 **`cx docs fetch`** 搜索并阅读官方 Coralogix 平台文档。

  当用户询问 Coralogix 功能如何工作、如何配置或使用 UI、设置集成（OpenTelemetry、代理、收集器、Webhook）、管理 API 密钥、在产品中探索跨度/跟踪/日志、配置警报/SLO/仪表板，或需要权威产品文档时使用——而不是实时租户遥测数据。'
---

# Coralogix 文档 (`cx docs search`, `cx docs fetch`)

这些命令读取 **官方 Coralogix 产品文档**，来源为 [coralogix.com/docs](https://coralogix.com/docs)。它们用于解答 **平台的工作原理** 以及 **如何配置或使用它**。它们**不会**查询您的租户的日志、追踪、指标或告警。

无需 Coralogix API 密钥。

## CLI 命令

| 命令 | 目的 |
|------|---------|
| `cx docs search <query>` | 通过关键词查找文档页面。返回编号标题 + 路径后缀。 |
| `cx docs fetch <suffix>` | 下载一个页面为 Markdown 格式。传递搜索结果中的后缀。 |

### 标志

| 标志 | 命令 | 描述 |
|------|----------|-------------|
| `--limit` | `search` | 最大结果数量，1–20（默认 5） |
| `-o json` / `-o toon` | both | 机器可读输出 |

### 示例

```bash
cx docs search "explore spans" --limit 5
cx docs search "OpenTelemetry traces"
cx docs fetch user-guides/data_exploration/spans/
cx docs search "API keys" -o json
```

## 何时使用这些命令

当用户需要时，使用 **`cx docs search`** + **`cx docs fetch`**：

| 主题 | 示例问题 |
|-------|-------------------|
| **UI / 工作流** | "如何在 Coralogix 中查看追踪？"，"探索追踪在哪里？" |
| **数据摄取 & 集成** | OpenTelemetry 设置，代理/收集器配置，Send Your Data API 密钥 |
| **平台功能** | 告警，SLO，仪表盘，增强，解析规则，保留策略 |
| **概念 & 架构** | 追踪如何工作，追踪-日志关联，数据模型 |
| **账户 & 访问** | API 密钥，SSO，角色，区域 |

当答案取决于当前 Coralogix 产品行为或 UI 导航时，**优先使用这些命令**，而不是猜测。

## 何时 **不** 使用这些命令

| 用户需求 | 使用替代方案 |
|-----------|-------------|
| **查询实时日志** | `cx logs` — [cx-telemetry-querying](../cx-telemetry-querying/SKILL.md) |
| **查询实时追踪** | `cx spans` — [cx-telemetry-querying](../cx-telemetry-querying/SKILL.md) |
| **DataPrime 语法 / 命令** | `cx dataprime list` / `cx dataprime show` — [cx-telemetry-querying](../cx-telemetry-querying/SKILL.md) |
| **租户中的告警 & 案例** | `cx alerts`, `cx cases` — [cx-alerts](../cx-alerts/SKILL.md), [cx-cases](../cx-cases/SKILL.md) |
| **指标 (PromQL)** | `cx metrics` — [cx-telemetry-querying](../cx-telemetry-querying/SKILL.md) |
| **在租户数据中查找字段路径** | `cx search-fields` |

## 标准工作流程

1. **`cx docs search`** 使用聚焦的查询（2–4 个关键词，非完整句子）。
2. 从结果中选择最相关的 **后缀**。
3. 对该后缀执行 **`cx docs fetch`**。
4. 从获取的内容中回答。仅在需要时才获取其他页面。

```
用户："如何在 Coralogix 网站上显示追踪？"

1. cx docs search "explore spans" --limit 5
2. cx docs fetch user-guides/data_exploration/spans/
3. 总结：Explore → 追踪数据集 → Spans/Traces/Flows 选项卡 → 下钻
```

## 小贴士

### `cx docs search`

- 使用 **2–4 个聚焦的术语**，而非完整句子。
- 如果没有匹配项，尝试同义词或更广泛的术语（例如 `"tracing"` 而非 `"distributed trace waterfall view"`）。
- 当第一页匹配项模糊时，增加 `--limit`。
- 结果使用 **`/docs/` 下的路径后缀**（非完整 URL）— 直接传递给 **`cx docs fetch`**。

### `cx docs fetch`

- 传递 **`cx docs search`** 的 **后缀**（例如 `user-guides/data_exploration/spans/`）。拒绝完整 URL。
- **一次 `cx docs fetch` 一个页面** — 首先选择最佳匹配项。

## 故障排除

| 问题 | 操作 |
|---------|--------|
| **没有搜索匹配项** | 放宽或重写查询；尝试功能名称 + 类别（例如 `"spans UI"`，`"OTel ingestion"`）。 |
| **获取的页面过于狭窄** | 搜索父主题或使用相关术语运行第二次搜索。 |
| **用户需要他们的实际数据** | 切换到 `cx logs`，`cx spans`，`cx metrics` 或告警 — 文档描述产品，而非租户内容。 |

## 相关

- **遥测查询：** [cx-telemetry-querying](../cx-telemetry-querying/SKILL.md)
- **告警：** [cx-alerts](../cx-alerts/SKILL.md)
- **仪表盘：** [cx-dashboards](../cx-dashboards/SKILL.md)
