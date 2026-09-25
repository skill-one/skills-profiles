# data360-query: 数据云检索阶段

当用户需要对数据云进行**查询、搜索和元数据洞察**时，使用此技能：同步SQL、分页SQL、异步查询工作流、表描述、向量搜索、混合搜索或搜索索引操作。

## 此技能负责任务的情况

当工作涉及以下内容时，使用 `data360-query`：
- `sf data360 query *`
- `sf data360 search-index *`
- `sf data360 metadata *`
- `sf data360 profile *` 或 `sf data360 insight *` 洞察
- 理解数据云SQL结果或查询形状

当用户处于以下情况时，将任务委托给其他技能：
- 仅编写标准CRM SOQL → [platform-soql-query](../platform-soql-query/SKILL.md)
- 设计细分或计算洞察资产 → [data360-segment](../data360-segment/SKILL.md)
- 分析STDM/会话跟踪/parquet遥测数据 → [agentforce-observe](../agentforce-observe/SKILL.md)

---

## 收集初始所需上下文

询问或推断：
- 目标组织别名
- 用户是否需要快速计数、中等结果集、大型导出、模式检查或语义搜索
- 如果已知，表/索引名称
- 任务是只读SQL还是搜索索引生命周期管理

---

## 核心操作规则

- 将数据云SQL视为独立的查询语言，而非SOQL。
- 在依赖查询/搜索界面之前，运行共享就绪分类器：`node ../data360-orchestrate/scripts/diagnose-org.mjs -o <org> --phase retrieve --json`。
- 在猜测列之前使用描述。
- 对于较大的结果集，优先选择 `sqlv2` 或异步查询流程。
- 仅在搜索索引生命周期健康时使用向量搜索或混合搜索。
- 将STDM/parquet/会话跟踪工作流排除在此技能家族之外。

---

## 推荐工作流程

### 1. 对检索工作分类就绪情况
```bash
node ../data360-orchestrate/scripts/diagnose-org.mjs -o <org> --phase retrieve --json
# 可选的查询平面探测，仅当有真实的表名时
node ../data360-orchestrate/scripts/diagnose-org.mjs -o <org> --phase retrieve --describe-table MyDMO__dlm --json
```

### 2. 选择最小的正确查询形状
```bash
sf data360 query sql -o <org> --sql 'SELECT COUNT(*) FROM "ssot__Individual__dlm"' 2>/dev/null
sf data360 query sqlv2 -o <org> --sql 'SELECT * FROM "ssot__Individual__dlm"' 2>/dev/null
sf data360 query async-create -o <org> --sql 'SELECT * FROM "ssot__Individual__dlm"' 2>/dev/null
```

### 3. 在猜测字段之前使用描述
```bash
sf data360 query describe -o <org> --table ssot__Individual__dlm 2>/dev/null
```

### 4. 仅在存在索引时使用向量或混合搜索
```bash
sf data360 search-index list -o <org> 2>/dev/null
sf data360 query vector -o <org> --index Knowledge_Index --query "reset password" --limit 5 2>/dev/null
sf data360 query hybrid -o <org> --index Knowledge_Index --query "reset password" --limit 5 2>/dev/null
sf data360 query hybrid -o <org> --index Insurance_Index --query "weather damage coverage" --prefilter "Type_of_Insurance__c='Home'" --limit 10 2>/dev/null
```

### 5. 创建索引时重用精选的搜索索引示例
使用该阶段拥有的示例，而不是从零开始编写JSON：
- `examples/search-indexes/vector-knowledge.json`
- `examples/search-indexes/hybrid-structured.json`

---

## 高信号注意事项

- 数据云SQL不是SOQL。
- 在SQL中应双引号表名。
- `sqlv2` 比临时OFFSET分页更适合中等结果集。
- 异步查询更适合大型结果。
- 搜索索引操作和向量/混合查询依赖于索引生命周期健康。
- 混合搜索可以使用 `--prefilter`，但仅限于在创建搜索索引时配置为可预过滤的字段。
- HNSW索引参数通常在创建时为只读；除非平台明确文档说明，否则保留 `userValues: []`。
- `query describe` 不是通用的租户探测；在确认更广泛的就绪情况后，仅在与已知DMO或DLO表一起运行。

---

## 输出格式

```text
检索任务：<sql / sqlv2 / async / describe / vector / search-index>
目标组织：<别名>
目标对象：<表或索引>
命令：<关键命令运行>
验证：<查询行数 / 模式 / 状态>
下一步：<细分 / 协调 / 跟进>
```

---

## 参考

- [examples/search-indexes/vector-knowledge.json](examples/search-indexes/vector-knowledge.json)
- [examples/search-indexes/hybrid-structured.json](examples/search-indexes/hybrid-structured.json)
- [../data360-orchestrate/assets/definitions/search-index.template.json](../data360-orchestrate/assets/definitions/search-index.template.json)
- [../data360-orchestrate/references/plugin-setup.md](../data360-orchestrate/references/plugin-setup.md)
- [../data360-orchestrate/references/feature-readiness.md](../data360-orchestrate/references/feature-readiness.md)
