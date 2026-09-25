# connecting-datacloud: 数据云连接阶段

在用户需要**源连接工作**时使用此技能：连接器发现、连接元数据、连接测试、源对象浏览、连接器模式检查，或为外部源准备连接器特定设置有效负载。

## 此技能负责任务的条件

当工作涉及以下内容时，使用 `connecting-datacloud`：
- `sf data360 connection *`
- 连接器目录检查
- 连接创建、更新、测试或删除
- 浏览源对象、字段、数据库或模式
- 确定已使用的连接器类型
- 为 Snowflake、SharePoint 非结构化或 Ingestion API 源准备连接器定义

当用户处于以下情况时，将任务委托给其他技能：
- 创建数据流或 DLOs → [preparing-datacloud](../preparing-datacloud/SKILL.md)
- 创建 DMOs、映射、IR 规则集或数据图 → [harmonizing-datacloud](../harmonizing-datacloud/SKILL.md)
- 编写 Data Cloud SQL 或搜索索引工作流 → [retrieving-datacloud](../retrieving-datacloud/SKILL.md)

---

## 首先收集必要的上下文

询问或推断：
- 目标组织别名
- 连接器类型或源系统
- 用户是否只想检查或进行实时变更
- 如果已存在，请提供连接名称或 ID
- 凭据是否已在 CLI 外部配置
- 用户是否希望在连接设置后立即创建流
- 源是数据库、非结构化文档源还是 Ingestion API 提供程序

---

## 核心操作规则

- 首先验证插件运行时；参见 [../orchestrating-datacloud/references/plugin-setup.md](../orchestrating-datacloud/references/plugin-setup.md)。
- 在修改连接之前运行共享就绪分类器：`node ../orchestrating-datacloud/scripts/diagnose-org.mjs -o <org> --phase connect --json`。
- 在连接创建之前优先进行只读发现。
- 使用 `2>/dev/null` 抑制链接插件警告噪音，用于标准用法。
- 记住 `connection list` 需要 `--connector-type`。
- 对于 `connection test`，在通过名称解析非 Salesforce 连接时，请传递 `--connector-type`。
- 在不熟悉的组织中，首先从流中发现现有连接器类型。
- 在发明连接器特定凭据或参数之前，使用精选示例有效负载。
- 对于精选示例之外的连接器类型，在构建 JSON 之前，通过 REST 检查一个已知的良好 UI 创建的连接。
- 不要因为连接创建成功就承诺为每种连接器类型都进行基于 API 的流创建。

---

## 推荐的工作流程

### 1. 对连接工作就绪性进行分类
```bash
node ../orchestrating-datacloud/scripts/diagnose-org.mjs -o <org> --phase connect --json
```

### 2. 发现连接器类型
```bash
sf data360 connection connector-list -o <org> 2>/dev/null
sf data360 data-stream list -o <org> 2>/dev/null
```

### 3. 按类型检查连接
```bash
sf data360 connection list -o <org> --connector-type SalesforceDotCom 2>/dev/null
sf data360 connection list -o <org> --connector-type REDSHIFT 2>/dev/null
sf data360 connection list -o <org> --connector-type SNOWFLAKE 2>/dev/null
```

### 4. 检查特定连接或上传的模式
```bash
sf data360 connection get -o <org> --name <connection> 2>/dev/null
sf data360 connection objects -o <org> --name <connection> 2>/dev/null
sf data360 connection fields -o <org> --name <connection> 2>/dev/null
sf data360 connection schema-get -o <org> --name <connection-id> 2>/dev/null
```

### 5. 发现后仅测试或创建
```bash
sf data360 connection test -o <org> --name <connection> --connector-type <type> 2>/dev/null
sf data360 connection create -o <org> -f connection.json 2>/dev/null
```

### 6. 从外部连接的精选示例有效负载开始
在使用从零开始发明有效负载之前，使用此阶段拥有的示例：
- `examples/connections/heroku-postgres.json`
- `examples/connections/redshift.json`
- `examples/connections/sharepoint-unstructured.json`
- `examples/connections/snowflake-connection.json`
- `examples/connections/ingest-api-connection.json`
- `examples/connections/ingest-api-schema.json`

典型的 Ingestion API 设置流程：
```bash
sf data360 connection create -o <org> -f examples/connections/ingest-api-connection.json 2>/dev/null
sf data360 connection schema-upsert -o <org> --name <connector-id> -f examples/connections/ingest-api-schema.json 2>/dev/null
sf data360 connection schema-get -o <org> --name <connector-id> 2>/dev/null
```

### 7. 发现未知连接器类型的有效负载字段
在 UI 中创建一个，然后直接检查它：
```bash
sf api request rest "/services/data/v66.0/ssot/connections/<id>" -o <org>
```

---

## 高信号注意事项

- `connection list` 没有真正的全局“列出所有”模式；按连接器类型查询。
- 连接器目录名称和连接器连接器类型不总是相同的标签。
- `connection test` 在源不是默认 Salesforce 连接器时，可能需要 `--connector-type` 进行名称解析。
- 空连接列表通常意味着“已启用但尚未配置”，而不是“功能禁用”。
- Heroku Postgres、Redshift、Snowflake、SharePoint 非结构化以及 Ingestion API 都使用不同的凭据和参数形状；重用精选示例，而不是猜测。
- SharePoint 非结构化在 `credentials` 数组中使用 `clientId`、`clientSecret` 和 `tokenEndpoint`，并且不需要 `parameters` 数组。
- Snowflake 使用密钥对认证，通常可以通过 API 创建，但下游流创建仍然可以是 UI 唯一。
- Ingestion API 连接器设置不完整，直到 `connection schema-upsert` 上传了对象模式。
- 某些外部连接器凭据设置仍然取决于 UI 端配置或外部系统权限。

---

## 输出格式

```text
连接任务： <检查 / 创建 / 测试 / 更新>
连接器类型： <SalesforceDotCom / REDSHIFT / SNOWFLAKE / SPUnstructuredDocument / IngestApi / ...>
目标组织： <别名>
命令： <运行的关键命令>
验证： <通过 / 部分通过 / 阻止>
下一步： <准备阶段或连接器后续操作>
```

---

## 参考

- [README.md](README.md)
- [examples/connections/heroku-postgres.json](examples/connections/heroku-postgres.json)
- [examples/connections/redshift.json](examples/connections/redshift.json)
- [examples/connections/sharepoint-unstructured.json](examples/connections/sharepoint-unstructured.json)
- [examples/connections/snowflake-connection.json](examples/connections/snowflake-connection.json)
- [examples/connections/ingest-api-connection.json](examples/connections/ingest-api-connection.json)
- [examples/connections/ingest-api-schema.json](examples/connections/ingest-api-schema.json)
- [../orchestrating-datacloud/references/plugin-setup.md](../orchestrating-datacloud/references/plugin-setup.md)
- [../orchestrating-datacloud/references/feature-readiness.md](../orchestrating-datacloud/references/feature-readiness.md)
- [../orchestrating-datacloud/UPSTREAM.md](../orchestrating-datacloud/UPSTREAM.md)
