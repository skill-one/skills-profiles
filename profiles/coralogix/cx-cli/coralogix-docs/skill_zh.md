# Coralogix 文档 (`cx docs search`, `cx docs fetch`)

这些命令从 [coralogix.com/docs](https://coralogix.com/docs) 读取 **官方 Coralogix 产品文档**。它们回答 **平台如何工作** 以及 **如何配置或使用它**。它们**不会**查询您的租户的日志、跟踪、指标或警报。

不需要 Coralogix API 密钥。

## CLI 命令

| 命令 | 目的 |
|------|---------|
| `cx docs search <query>` | 通过关键字查找文档页面。返回编号的标题 + 路径后缀。 |
| `cx docs fetch <suffix>` | 下载一个页面作为 Markdown。传递搜索后的后缀。 |

### 标志

| 标志 | 命令 | 描述 |
|------|----------|-------------|
| `--limit` | `search` | 最大结果数，1–20（默认 5） |
| `-o json` / `-o toon` | both | 机器可读输出 |

### 示例

```bash
cx docs search "explore spans" --limit 5
cx docs search "OpenTelemetry traces"
cx docs fetch user-guides/data_exploration/spans/
cx docs search "API keys" -o json
```

## 何时使用这些命令

当用户想要：

| 主题 | 示例问题 |
|-------|-------------------|
| **UI / 工作流** | "如何在 Coralogix 中查看跟踪？"，"探索跟踪在哪里？" |
| **数据摄取和集成** | OpenTelemetry 设置、代理/收集器配置、发送您的数据 API 密钥 |
| **平台功能** | 警报、SLO、仪表板、增强、解析规则、保留 |
| **概念和架构** | 跟踪如何工作、跟踪-日志关联、数据模型 |
| **账户和访问** | API 密钥、SSO、角色、区域 |

当答案取决于当前 Coralogix 产品行为或 UI 导航时，**优先使用这些命令**，而不是猜测。

## 何时**不**使用这些命令

| 用户需求 | 使用替代方案 |
|-----------|-------------|
| **查询实时日志** | `cx logs` — [cx-telemetry-querying](../cx-telemetry-querying/SKILL.md) |
| **查询实时跟踪** | `cx spans` — [cx-telemetry-querying](../cx-telemetry-querying/SKILL.md) |
| **DataPrime 语法 / 命令** | `cx dataprime list` / `cx dataprime show` — [cx-telemetry-querying](../cx-telemetry-querying/SKILL.md) |
| **租户中的警报和案例** | `cx alerts`, `cx cases` — [cx-alerts](../cx-alerts/SKILL.md), [cx-cases](../cx-cases/SKILL.md) |
| **指标（PromQL）** | `cx metrics` — [cx-telemetry-querying](../cx-telemetry-querying/SKILL.md) |
| **在租户数据中查找字段路径** | `cx search-fields` |

## 标准工作流程

1. **`cx docs search`** 使用一个聚焦的查询（2–4 个关键字，不是完整的句子）。
2. 从结果中选择最相关的 **后缀**。
3. 对该后缀执行 **`cx docs fetch`**。
4. 从获取的内容中回答。仅在需要时才获取附加页面。

```
用户："如何在 Coralogix 网站上显示跟踪？"

1. cx docs search "explore spans" --limit 5
2. cx docs fetch user-guides/data_exploration/spans/
3. 总结：探索 → 跟踪数据集 → 跟踪/跟踪/流标签 → 下钻
```

## 小贴士

### `cx docs search`

- 使用 **2–4 个聚焦的术语**，而不是完整的句子开始。
- 如果没有匹配项，尝试同义词或更广泛的术语（例如 `"tracing"` 而不是 `"distributed trace waterfall view"`）。
- 当第一页命中结果不明确时，增加 `--limit`。
- 结果使用 **`/docs/` 下的路径后缀**（不是完整的 URL）— 直接将其传递给 **`cx docs fetch`**。

### `cx docs fetch`

- 传递来自 **`cx docs search`** 的 **后缀**（例如 `user-guides/data_exploration/spans/`）。拒绝完整的 URL。
- **一次 `cx docs fetch` 一个页面** — 首先选择最佳匹配。

## 故障排除

| 问题 | 操作 |
|---------|--------|
| **没有搜索匹配项** | 放宽或重写查询；尝试功能名称 + 类别（例如 `"spans UI"`，`"OTel ingestion"`）。 |
| **获取的页面过于狭窄** | 搜索父主题或使用相关术语运行第二次搜索。 |
| **用户想要他们的实际数据** | 切换到 `cx logs`，`cx spans`，`cx metrics` 或警报 — 文档描述产品，而不是租户内容。 |

## 相关

- **遥测查询：** [cx-telemetry-querying](../cx-telemetry-querying/SKILL.md)
- **警报：** [cx-alerts](../cx-alerts/SKILL.md)
- **仪表板：** [cx-dashboards](../cx-dashboards/SKILL.md)
