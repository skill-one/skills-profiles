# data360-prepare：数据云准备阶段

在用户需要**数据摄取和湖准备工作**时使用此技能：数据流、数据湖对象（DLO）、转换、文档AI、非结构化摄取，或从连接器设置到实时流的交接。

## 此技能负责任务的情况

当工作涉及以下内容时，使用 `data360-prepare`：
- `sf data360 data-stream *`
- `sf data360 dlo *`
- `sf data360 transform *`
- `sf data360 docai *`
- 选择数据如何进入数据云
- 源更新后重新运行或重新扫描摄取
- 连接器设置完成后准备基于摄取API的流

当用户处于以下情况时，将任务委托给其他技能：
- 仍在创建/测试源连接 → [data360-connect](../data360-connect/SKILL.md)
- 映射到DMO或设计IR/数据图 → [data360-harmonize](../data360-harmonize/SKILL.md)
- 查询已摄取数据 → [data360-query](../data360-query/SKILL.md)

---

## 首先收集必要的上下文

询问或推断：
- 目标组织别名
- 源连接名称
- 源对象/数据集/文档源
- 期望的流类型
- DLO命名预期
- 用户是创建、更新、运行还是删除流
- 源是CRM、数据库连接器、非结构化文件源还是摄取API馈送

---

## 核心操作规则

- 在运行数据云命令之前验证外部插件运行时。
- 在修改摄取资产之前运行共享就绪分类器：`node ../data360-orchestrate/scripts/diagnose-org.mjs -o <org> --phase prepare --json`。
- 优先在创建新的摄取资产之前检查现有流和DLO。
- 使用 `2>/dev/null` 抑制链接插件警告噪音，用于正常使用。
- 将DLO命名和字段命名视为数据云特定，而非CRM原生。
- 在创建流之前，确认每个数据集是否应被视为 `Profile`、`Engagement` 或 `Other`。
- 在处理非结构化源时，区分流级刷新与连接级重跑。
- 当初始流或非结构化资产创建受平台限制时，有意使用UI设置。
- 只有在摄取资产明显健康后，才交接给Harmonize。

---

## 推荐的工作流程

### 1. 为准备工作分类就绪状态
```bash
node ../data360-orchestrate/scripts/diagnose-org.mjs -o <org> --phase prepare --json
```

### 2. 检查现有摄取资产
```bash
sf data360 data-stream list -o <org> 2>/dev/null
sf data360 dlo list -o <org> 2>/dev/null
```

### 3. 在创建前确认流类别
使用以下规则建议类别：

| 类别 | 用于 | 典型要求 |
|---|---|---|
| `Profile` | 人/实体记录 | 主键 |
| `Engagement` | 基于时间的活动或交互 | 主键 + 事件时间字段 |
| `Other` | 参考数据/配置/支持数据集 | 主键 |

当源不明确时，明确询问用户数据集是否应被视为 `Profile`、`Engagement` 或 `Other`。

### 4. 有意创建或检查流
```bash
sf data360 data-stream get -o <org> --name <stream> 2>/dev/null
sf data360 data-stream create-from-object -o <org> --object Contact --connection SalesforceDotCom_Home 2>/dev/null
sf data360 data-stream create -o <org> -f stream.json 2>/dev/null
sf data360 data-stream run -o <org> --name <stream> 2>/dev/null
```

### 5. 检查DLO结构
```bash
sf data360 dlo get -o <org> --name Contact_Home__dll 2>/dev/null
```

### 6. 选择正确的刷新机制
使用与用户目标匹配的最小刷新范围：

```bash
sf data360 data-stream run -o <org> --name <stream> 2>/dev/null
sf data360 connection run-existing -o <org> --name <connection-id> 2>/dev/null
```

- `data-stream run` 最接近流级刷新或重新扫描。
- `connection run-existing` 在连接级运行，对于某些连接器工作流程可能有用，但它不是非结构化源流刷新的可靠替代方案。
- 对于非结构化文档连接器，当目标是重新扫描新添加或更改的文件时，优先使用 `data-stream run`。

### 7. 有意处理非结构化源
对于SharePoint风格的文档摄取，最小的非结构化DLO负载如下：

```json
{
  "name": "my_udlo",
  "label": "My UDLO",
  "category": "Directory_Table",
  "dataSource": {
    "sourceType": "SF_DRIVE",
    "directoryAndFilesDetails": [
      {
        "dirName": "SPUnstructuredDocument/<CONNECTION_ID>/<SITE_ID>",
        "fileName": "*"
      }
    ],
    "sourceConfig": {
      "reservedPrefix": "$dcf_content$"
    }
  }
}
```

当用户需要更丰富的端到端管道时，使用UI进行首次非结构化设置。UI路径可以预置额外的文档元数据字段和下游资产，而裸CLI DLO创建流程可能不会自动配置。

### 8. 使用本地摄取API示例进行send-data工作流
对于将记录推入数据云的外部系统：

1. 在 [data360-connect](../data360-connect/SKILL.md) 中创建连接器
2. 使用 `sf data360 connection schema-upsert` 上传架构
3. 在需要时在UI中创建流
4. 使用本地示例发送记录在 `examples/ingestion-api/`

```bash
cd examples/ingestion-api
cp .env.example .env
python3 send-data.py
```

关键细节：
- 认证是分阶段流程：JWT → Salesforce令牌 → 数据云令牌
- 摄取端点使用租户URL，而不是Salesforce实例URL
- `202` 表示有效载荷已接受处理，而不是记录立即可查询
- 验证失败通常出现在问题记录DLO家族中

### 9. 然后才进入harmonization
一旦流和DLO健康，交接给 [data360-harmonize](../data360-harmonize/SKILL.md)。

---

## 高信号常见问题

- CRM支持的流行为与完全自定义的连接器框架摄取不同。
- `sf data360 data-stream run` 和 `sf data360 connection run-existing` 不能互换；对于非结构化重扫描，优先使用流级刷新。
- `SFDC` 流在平台管理的计划上同步；`data-stream run` 不是CRM连接器刷新的通用控制路径。
- 某些外部数据库连接器可以通过API创建，而流创建仍需要UI流程或特定组织的浏览器自动化。不要承诺为每种连接器类型提供纯CLI流创建路径。
- SharePoint风格的初始非结构化设置在UI中可以比在最小CLI DLO创建流程中更丰富。
- 删除流也可能删除关联的DLO，除非删除模式另有说明。
- DLO字段命名与CRM字段命名不同，包括 `__c` → `_c` 转换。
- 使用数据云SQL查询DLO记录计数，而不是假设列表输出足够。
- `CdpDataStreams` 表示流模块对当前组织/用户受限；指导用户进行资源/权限审查，而不是盲目重试。

---

## 输出格式

```text
准备任务：<流 / DLO / 转换 / docai>
源：<连接器 + 对象>
目标组织：<别名>
工件：<流名称 / DLO名称 / JSON定义>
验证：<通过 / 部分通过 / 阻塞>
下一步：<harmonize或检索>
```

---

## 参考

- [examples/ingestion-api/README.md](examples/ingestion-api/README.md)
- [../data360-orchestrate/assets/definitions/data-stream.template.json](../data360-orchestrate/assets/definitions/data-stream.template.json)
- [../data360-orchestrate/references/plugin-setup.md](../data360-orchestrate/references/plugin-setup.md)
- [../data360-orchestrate/references/feature-readiness.md](../data360-orchestrate/references/feature-readiness.md)
