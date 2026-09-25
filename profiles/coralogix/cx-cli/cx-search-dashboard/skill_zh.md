# 仪表板搜索功能

使用此功能通过 `cx dashboards` CLI 命令进行语义或基于字段的搜索，以发现现有的 Coralogix 仪表板和组件。在创建新仪表板之前，始终先进行搜索以避免重复。

## CLI 命令

| 命令 | 用途 | 关键标志 |
|---|---|---|
| `cx dashboards search "<描述>"` | 通过自然语言描述查找仪表板 | `--limit` |
| `cx dashboards query-search --description "<文本>"` | 查找查询与描述匹配的组件 | `--limit` |
| `cx dashboards query-search --field "<字段路径>"` | 查找所有引用特定字段的组件 | `--limit` |
| `cx dashboards catalog -o json` | 列出所有仪表板 | - |
| `cx dashboards get <id> -o json` | 获取完整的仪表板定义 | - |

**输出格式：** 添加 `-o json` 或 `-o toon` 以获得机器可读的输出。

## 何时使用每个命令

| 目标 | 命令 |
|---|---|
| 检查是否已存在服务或主题的仪表板 | `cx dashboards search` |
| 查找查询涵盖您关心的主题的组件 | `cx dashboards query-search --description` |
| 查找查询引用特定字段路径的组件 | `cx dashboards query-search --field` |
| 浏览所有仪表板 | `cx dashboards catalog` |

## 示例

### 为服务查找仪表板

```bash
cx dashboards search "支付服务错误率"
cx dashboards search "kubernetes 节点 cpu"
```

### 查找查询涵盖主题的组件

```bash
cx dashboards query-search --description "http 5xx 错误率"
cx dashboards query-search --description "p99 延迟随时间变化"
```

### 查找所有引用字段的组件

```bash
cx dashboards query-search --field '$d.http.status_code'
cx dashboards query-search --field '$d.kubernetes.pod.name'
```

这会揭示已使用的查询模式——在添加新组件时重用现有方法很有用。

### 检查并克隆找到的仪表板

```bash
# 获取您找到的仪表板的完整 JSON
cx dashboards get <仪表板-id> -o json > dashboard.json
# 修改它，然后创建副本
cx dashboards create --from-file dashboard.json
```

## 关键原则

- **创建前先搜索** — 在构建新仪表板之前始终运行 `cx dashboards search` 以避免重复
- **使用字段搜索进行发现** — `cx dashboards query-search --field` 显示字段如何被查询，这是查找可重用 PromQL 或 DataPrime 模式的最快方式
- **描述搜索是模糊的** — 结果按相似度排序，而不是精确匹配；如果第一次搜索无结果，请尝试多种表述
- **使用 `cx dashboards get` 进行检查** — 找到相关仪表板或组件后，拉取其完整 JSON 以研究查询结构

## 相关功能

- **`cx-dashboards`** — 从头开始构建和部署新的 Coralogix 仪表板
- **`cx-telemetry-querying`** — 在搜索仪表板前发现存在的遥测字段和指标
