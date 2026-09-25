# Kibana Vega

使用 ES|QL 数据源创建和管理 Kibana 仪表板和 Vega 可视化。

## 概述

Vega 是一种声明式可视化语法，用于在 Kibana 中创建自定义图表。结合 ES|QL 查询，它能够实现超出标准 Kibana 图表的高度定制化可视化。

**重要版本要求**：此功能严格支持 **ES|QL 数据源**，并需要 **Serverless Kibana 或 9.4+（SNAPSHOT）版本**。它不会在旧版本上可靠运行，也无法与旧的 Lucene/KQL 数据源定义一起使用。

## 快速入门

### 环境配置

Kibana 连接通过环境变量进行配置。运行 `node scripts/kibana-vega.js test` 来验证连接。如果测试失败，建议用户这些设置选项，然后停止。在成功连接测试之前，不要尝试进一步探索。

#### 选项 1：Elastic Cloud（推荐用于生产）

```bash
export KIBANA_CLOUD_ID="deployment-name:base64encodedcloudid"
export KIBANA_API_KEY="base64encodedapikey"
```

#### 选项 2：带 API 密钥的直接 URL

```bash
export KIBANA_URL="https://your-kibana:5601"
export KIBANA_API_KEY="base64encodedapikey"
```

#### 选项 3：基本认证

```bash
export KIBANA_URL="https://your-kibana:5601"
export KIBANA_USERNAME="elastic"
export KIBANA_PASSWORD="changeme"
```

#### 选项 4：使用 start-local 进行本地开发

对于本地开发和测试，使用 [start-local](https://github.com/elastic/start-local) 通过 Docker 或 Podman 快速启动 Elasticsearch 和 Kibana：

```bash
curl -fsSL https://elastic.co/start-local | sh
```

安装完成后，Elasticsearch 运行在 `http://localhost:9200`，Kibana 运行在 `http://localhost:5601`。该脚本会为 `elastic` 用户生成一个随机密码，存储在创建的 `elastic-start-local` 文件夹中的 `.env` 文件中。

要为该功能配置环境变量，请源 `.env` 文件并导出连接设置：

```bash
source elastic-start-local/.env
export KIBANA_URL="$KB_LOCAL_URL"
export KIBANA_USERNAME="elastic"
export KIBANA_PASSWORD="$ES_LOCAL_PASSWORD"
```

然后运行 `node scripts/kibana-vega.js test` 来验证连接。

#### 可选：跳过 TLS 验证（仅限开发）

```bash
export KIBANA_INSECURE="true"
```

### 基本工作流程

```bash
# 测试连接
node scripts/kibana-vega.js test

# 直接从 stdin 创建可视化（无需中间文件）
echo '<json-spec>' | node scripts/kibana-vega.js visualizations create "My Chart" -

# 获取可视化规范以进行审查/修改
node scripts/kibana-vega.js visualizations get <vis-id>

# 从 stdin 更新可视化
echo '<json-spec>' | node scripts/kibana-vega.js visualizations update <vis-id> -

# 创建仪表板
node scripts/kibana-vega.js dashboards create "My Dashboard"

# 添加带网格位置的可视化
node scripts/kibana-vega.js dashboards add-panel <dashboard-id> <vis-id> --x 0 --y 0 --w 24 --h 15

# 从 stdin 应用完整布局
echo '<layout-json>' | node scripts/kibana-vega.js dashboards apply-layout <dashboard-id> -
```

**注意**：将文件参数设置为 `-` 以从 stdin 读取 JSON。这允许直接创建规范，无需中间文件。

### 带有 ES|QL 的最小 Vega 规范

**重要**：始终使用正确的 JSON 格式（而不是带三引号的 HJSON），以避免解析错误。

```json
{
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  "title": "My Chart",
  "autosize": { "type": "fit", "contains": "padding" },

  "config": {
    "axis": { "domainColor": "#444", "tickColor": "#444" },
    "view": { "stroke": null }
  },

  "data": {
    "url": {
      "%type%": "esql",
      "query": "FROM logs-* | STATS count = COUNT() BY status | RENAME status AS category"
    }
  },

  "mark": { "type": "bar", "color": "#6092C0" },
  "encoding": {
    "x": { "field": "category", "type": "nominal" },
    "y": { "field": "count", "type": "quantitative" }
  }
}
```

### ES|QL 数据源选项

| 属性                    | 描述                                |
| --------------------------- | ------------------------------------------ | --------- |
| `%type%: "esql"`            | 必须使用 ES                           | QL 解析器 |
| `%context%: true`           | 应用仪表板过滤器                    |
| `%timefield%: "@timestamp"` | 启用时间范围（使用 `?_tstart`/`?_tend`） |

## 示例

### stdin 示例

```bash
# 直接从 JSON 创建可视化
echo '{"$schema":"https://vega.github.io/schema/vega-lite/v6.json",...}' | \
  node scripts/kibana-vega.js visualizations create "My Chart" -

# 更新可视化
echo '{"$schema":...}' | node scripts/kibana-vega.js visualizations update <id> -

# 直接应用布局
echo '{"panels":[{"visualization":"<id>","x":0,"y":0,"w":24,"h":10}]}' | \
  node scripts/kibana-vega.js dashboards apply-layout <dash-id> -
```

## 仪表板布局设计

### 网格系统

Kibana 仪表板使用 **48 列网格**：

| 宽度   | 列数 | 用途                         |
| ------- | ------- | -------------------------------- |
| 全宽    | 48      | 时间线、热力图、宽图表         |
| 半宽    | 24      | 并列比较                     |
| 三分之一 | 16      | 三列布局                     |
| 四分之一 | 12      | KPI 指标、简短摘要             |

### 展开区域（关键）

**主要信息必须在不滚动的情况下可见。**

| 分辨率 | 可见高度 | 布局预算              |
| ---------- | -------------- | -------------------------- |
| 1080p      | ~30 单位      | 2 行：h:10 + h:12        |
| 1440p      | ~40 单位      | 3 行：h:12 + h:12 + h:12 |

**高度指南：**

- `h: 10` — 紧凑条形图（≤7 项），适合展开区域
- `h: 12-13` — 标准图表、时间线
- `h: 15+` — 详细视图，用于展开区域以下

### 布局模式：运营仪表板

```text
┌───────────────────────┬───────────────────────┐  y:0
│  当前状态 A      │  当前状态 B      │  h:10 (紧凑)
├───────────────────────┴───────────────────────┤  y:10
│         主要时间线                      │  h:12 (主要趋势)
├ ─ ─ ─ ─ ─ ─ ─ FOLD ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┤  y:22 (1080p 展开区域)
│         次要时间线                    │  h:12 (展开区域以下 OK)
├───────────────────────┬───────────────────────┤  y:34
│  互补 1      │  互补 2      │  h:10
└───────────────────────┴───────────────────────┘
```

### 创建布局

#### 选项 1：带位置添加面板

```bash
# 第 1 行：两个紧凑半宽图表（展开区域以上）
node scripts/kibana-vega.js dashboards add-panel $DASH $VIS1 --x 0 --y 0 --w 24 --h 10
node scripts/kibana-vega.js dashboards add-panel $DASH $VIS2 --x 24 --y 0 --w 24 --h 10

# 第 2 行：全宽时间线（展开区域以上）
node scripts/kibana-vega.js dashboards add-panel $DASH $VIS3 --x 0 --y 10 --w 48 --h 12

# 第 3 行：展开区域以下内容
node scripts/kibana-vega.js dashboards add-panel $DASH $VIS4 --x 0 --y 22 --w 48 --h 12
```

#### 选项 2：应用布局文件

创建 `layout.json`：

```json
{
  "title": "My Dashboard",
  "panels": [
    { "visualization": "<vis-id-1>", "x": 0, "y": 0, "w": 24, "h": 10 },
    { "visualization": "<vis-id-2>", "x": 24, "y": 0, "w": 24, "h": 10 },
    { "visualization": "<vis-id-3>", "x": 0, "y": 10, "w": 48, "h": 12 },
    { "visualization": "<vis-id-4>", "x": 0, "y": 22, "w": 48, "h": 12 }
  ]
}
```

应用它：

```bash
node scripts/kibana-vega.js dashboards apply-layout <dashboard-id> layout.json
```

### 设计检查清单

1. **展开区域**：顶部约 22 高度单位（1080p）的主要信息
2. **紧凑高度**：使用 h:10 对于条形图（≤7 项）
3. **优先级**：最重要的信息在左上角
4. **分组**：相关图表并排以便比较
5. **时间线**：全宽（w:48），h:12 用于紧凑
6. **展开区域以下**：互补/详细面板可以滚动

## 指南

1. **使用 JSON，而不是 HJSON 三引号** — `'''` 多行字符串会导致 Kibana 解析错误；使用带转义引号的单行查询 `\"`
2. **重命名点字段** — `room.name` 会破坏 Vega（解释为嵌套路径）；使用 ES|QL `RENAME room.name AS room`
3. **不要设置宽度和高度** — 使用 `autosize: { type: fit, contains: padding }`
4. **设置轴的 labelLimit** — 水平条形图标签会被截断；使用 `axis: { "labelLimit": 150 }`
5. **按值排序条形图** — 在 ES|QL 中预排序 `SORT field DESC`，并在编码中使用 `sort: null`（保留数据顺序）；避免在分层规范（条形图 + 文本标签）中使用 `sort: "-x"`，因为它会导致“冲突排序属性”警告
6. **时间轴：不旋转标签** — 使用 `axis: { "labelAngle": 0, "tickCount": 8 }`，让 Vega 自动格式化日期
7. **描述性标题替换轴标题** — 好的标题/副标题使轴标题变得多余；使用 `title: null` 在轴上
8. **谨慎使用颜色** — 颜色是一种宝贵的视觉属性；对于条形图使用单一默认颜色（`#6092C0`），其中位置已经编码了值；保留颜色编码用于分类区分（例如，时间序列中的多条线）
9. **暗色主题兼容性** — 始终包含配置以避免明亮的白色边框：

   ```json
   "config": {
     "axis": { "domainColor": "#444", "tickColor": "#444" },
     "view": { "stroke": null }
   }
   ```

## CLI 命令

```bash
# 仪表板
node scripts/kibana-vega.js dashboards list [search]
node scripts/kibana-vega.js dashboards get <id>
node scripts/kibana-vega.js dashboards create <title>
node scripts/kibana-vega.js dashboards delete <id>
node scripts/kibana-vega.js dashboards add-panel <dash-id> <vis-id> [--x N] [--y N] [--w N] [--h N]
node scripts/kibana-vega.js dashboards apply-layout <dash-id> <file|->

# 可视化（使用 - 代替文件进行 stdin）
node scripts/kibana-vega.js visualizations list [vega]
node scripts/kibana-vega.js visualizations get <id>
node scripts/kibana-vega.js visualizations create <title> <file|->
node scripts/kibana-vega.js visualizations update <id> <file|->
node scripts/kibana-vega.js visualizations delete <id>
```

## 完整文档

- [仪表板布局参考](references/dashboard-layout-reference.md) — 网格系统、布局模式、设计最佳实践
- [Vega-Lite 参考](references/vega-lite-reference.md) — 完整 Vega-Lite 语法、图表模式、最佳实践
- [Vega 中 ES|QL 参考](references/vega-esql-reference.md) — ES|QL 数据源配置、时间过滤、参数
- [示例规范](examples/) — 即用型图表模板

## 常见问题

| 错误                                  | 解决方案                                                                                             |
| -------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| "输入结束时解析对象"                  | 不要使用 HJSON `'''` 三引号；使用 JSON 带单行查询                               |
| 标签显示 "undefined"                | 重命名点字段：`RENAME room.name AS room`                                                     |
| 条形图不可见 / 未渲染                 | 移除复杂的 `scale.domain`，使用更简单的配色方案                                             |
| Y 轴标签被截断                | 在编码中添加 `axis: { "labelLimit": 150 }`                                                        |
| 面板垂直堆叠              | 使用 `--x --y --w --h` 选项或 `apply-layout` 命令                                              |
| "width/height 忽略"                 | 移除尺寸，使用 `autosize`                                                                    |
| 暗色主题下出现亮白色边框     | 添加 `config: { "view": { "stroke": null }, "axis": { "domainColor": "#444", "tickColor": "#444" } }` |
| "401 未授权"                     | 检查 KIBANA_USERNAME/PASSWORD                                                                       |
| "conflicting sort properties"          | 不要在分层规范中使用 `sort: "-x"`；在 ES\|QL 中预排序，并使用 `sort: null`                     |
| "404 未找到"                        | 验证仪表板/可视化 ID                                                                    |
