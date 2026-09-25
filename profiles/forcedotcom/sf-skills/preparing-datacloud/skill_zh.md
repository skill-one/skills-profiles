# preparing-datacloud: 数据云准备阶段

在用户需要**数据摄取和湖准备工作**时使用此技能：数据流、数据湖对象 (DLO)、转换、文档 AI、非结构化摄取，或从连接器设置到实时流的交接。

## 此技能负责任务的条件

当工作涉及以下内容时，使用 `preparing-datacloud`：
- `sf data360 data-stream *`
- `sf data360 dlo *`
- `sf data360 transform *`
- `sf data360 docai *`
- 选择数据如何进入数据云
- 源更新后重新运行或重新扫描摄取
- 连接器设置完成后准备 Ingestion API 支持的流

当用户处于以下情况时，将任务委托给其他技能：
- 仍在创建/测试源连接 → [connecting-datacloud](../connecting-datacloud/SKILL.md)
- 映射到 DMO 或设计 IR/数据图 → [harmonizing-datacloud](../harmonizing-datacloud/SKILL.md)
- 查询已摄取数据 → [retrieving-datacloud](../retrieving-datacloud/SKILL.md)

---

## 首先收集所需的上下文

询问或推断：
- 目标组织别名
- 源连接名称
- 源对象 / 数据集 / 文档源
- 期望的流类型
- DLO 命名预期
- 用户是在创建、更新、运行还是删除流
- 源是 CRM、数据库连接器、非结构化文件源还是 Ingestion API 提供程序

---

## 核心操作规则

- 运行数据云命令前，先验证外部插件运行时。
- 在修改摄取资产前运行共享就绪分类器：`node ../orchestrating-datacloud/scripts/diagnose-org.mjs -o <org> --phase prepare --json`。
- 优先在创建新的摄取资产前检查现有流和 DLO。
- 使用 `2>/dev/null` 抑制链接插件警告噪音，用于正常使用。
- 将 DLO 命名和字段命名视为数据云特定，而非 CRM 本地。
- 在创建流前，确认每个数据集是否应被视为 `Profile`、`Engagement` 或 `Other`。
- 在处理非结构化源时，区分流级刷新与连接级重跑。
- 当初始流或非结构化资产创建受平台限制时，有意使用 UI 设置。
- 只有在摄取资产明确健康后，才交接给 Harmonize。

---

## 推荐的工作流程

### 1. 为准备工作分类就绪状态
```bash
node ../orchestrating-datacloud/scripts/diagnose-org.mjs -o <org> --phase prepare --json
```

### 2. 检查现有摄取资产
```bash
sf data360 data-stream list -o <org> 2>/dev/null
sf data360 dlo list -o <org> 2>/dev/null
```

### 3. 创建前确认流类别
使用以下规则建议类别：

| 类别 | 用于 | 典型要求 |
|---|---|---|
| `Profile` | 人/实体记录 | 主键 |
| `Engagement` | 基于时间的活动或交互 | 主键 + 事件时间字段 |
| `Other` | 参考/配置/支持性数据集 | 主键 |

当源不明确时，明确询问用户数据集是否应被视为 `Profile`、`Engagement` 或 `Other`。

### 4. 有意创建或检查流
```bash
sf data360 data-stream get -o <org> --name <stream> 2>/dev/null
sf data360 data-stream create-from-object -o <org> --object Contact --connection SalesforceDotCom_Home 2>/dev/null
sf data360 data-stream create -o <org> -f stream.json 2>/dev/null
sf data360 data-stream run -o <org> --name <stream> 2>/dev/null
```

### 5. 检查 DLO 结构
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
- `connection run-existing` 在连接级运行，对某些连接器工作流程有用，但不是非结构化源流刷新的可靠替代方案。
- 对于非结构化文档连接器，当目标是重新扫描新添加或更改的文件时，优先使用 `data-stream run`。

### 7. 有意处理非结构化源
对于 SharePoint 风格的文档摄取，最小的非结构化 DLO 负载如下：

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
当用户需要更丰富的端到端管道时，使用 UI 进行首次非结构化设置。UI 路径可以预置额外的文档元数据字段和下游资产，而裸 CLI DLO 创建流程可能不会自动配置。

### 8. 使用本地 Ingestion API 示例进行 send-data 工作流
对于将记录推入数据云的外部系统：
1. 在 [connecting-datacloud](../connecting-datacloud/SKILL.md) 中创建连接器
2. 使用 `sf data360 connection schema-upsert` 上传架构
3. 在需要时在 UI 中创建流
4. 使用本地示例发送记录，位于 `examples/ingestion-api/`

```bash
cd examples/ingestion-api
cp .env.example .env
python3 send-data.py
```

关键细节：
- 认证是分阶段流程：JWT → Salesforce 令牌 → 数据云令牌
- 摄取端点使用租户 URL，而不是 Salesforce 实例 URL
- `202` 表示负载已接受处理，不代表记录立即可查询
- 验证失败通常出现在 Problem Records DLO 家族中

### 9. 然后进入 harmonization
一旦流和 DLO 健康，交接给 [harmonizing-datacloud](../harmonizing-datacloud/SKILL.md)。

---

## 高信号注意事项

- CRM 支持的流行为与完全自定义的连接器框架摄取不同。
- `sf data360 data-stream run` 和 `sf data360 connection run-existing` 不能互换；对于非结构化重扫描，优先使用流级刷新。
- `SFDC` 流在平台管理的计划上同步；`data-stream run` 不是 CRM 连接器刷新的通用控制路径。
- 某些外部数据库连接器可以通过 API 创建，而流创建仍需要 UI 流或组织特定的浏览器自动化。不要承诺为每种连接器类型提供纯 CLI 流创建路径。
- SharePoint 风格的初始非结构化设置在 UI 中可以比最小 CLI DLO 创建流程更丰富。
- 删除流也可能删除关联的 DLO，除非删除模式另有说明。
- DLO 字段命名与 CRM 字段命名不同，包括 `__c` → `_c` 转换。
- 使用数据云 SQL 查询 DLO 记录计数，而不是假设列表输出足够。
- `CdpDataStreams` 表示流模块对当前组织/用户受限；引导用户进行资源/权限审查，而不是盲目重试。

---

## 输出格式

```text
准备任务： <流 / DLO / 转换 / docai>
源： <连接器 + 对象>
目标组织： <别名>
工件： <流名称 / DLO 名称 / JSON 定义>
验证： <通过 / 部分通过 / 阻塞>
下一步： <harmonize 或 retrieve>
```

---

## 参考

- [README.md](README.md)
- [examples/ingestion-api/README.md](examples/ingestion-api/README.md)
- [../orchestrating-datacloud/assets/definitions/data-stream.template.json](../orchestrating-datacloud/assets/definitions/data-stream.template.json)
- [../orchestrating-datacloud/references/plugin-setup.md](../orchestrating-datacloud/references/plugin-setup.md)
- [../orchestrating-datacloud/references/feature-readiness.md](../orchestrating-datacloud/references/feature-readiness.md)
