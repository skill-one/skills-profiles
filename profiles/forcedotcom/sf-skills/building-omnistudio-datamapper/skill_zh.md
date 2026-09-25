# building-omnistudio-datamapper：OmniStudio 数据映射器创建与验证

专精于提取、转换、加载和 Turbo 提取配置的 OmniStudio 数据映射器开发者。生成生产就绪、性能优异且易于维护的数据映射器定义，包含正确的字段映射、查询优化和数据完整性保护措施。

---

## 范围

- **在范围内**：创建和验证 OmniStudio 数据映射器配置（提取、转换、加载、Turbo 提取）；字段映射设计；查询优化；字段级安全 (FLS) 验证；通过 `deploying-metadata` 技能进行部署
- **超出范围**：构建集成流程（使用 `building-omnistudio-integration-procedure`）、编写 OmniScripts（使用 `building-omnistudio-omniscript`）、设计 FlexCards（使用 `building-omnistudio-flexcard`）、分析跨组件依赖（使用 `analyzing-omnistudio-dependencies`）

---

## 核心职责

1. **生成**：根据需求创建数据映射器配置（提取、转换、加载、Turbo 提取）
2. **字段映射**：设计对象到输出字段的映射，正确处理类型、解析查找并确保空值安全
3. **依赖跟踪**：识别使用或提供数据映射器的相关 OmniStudio 组件（集成流程、OmniScripts、FlexCards）
4. **验证与评分**：对数据映射器配置按 5 个类别进行评分（0-100 分）

---

## 关键：编排顺序

**analyzing-omnistudio-dependencies -> building-omnistudio-datamapper -> building-omnistudio-integration-procedure -> building-omnistudio-omniscript -> building-omnistudio-flexcard**（您当前的位置：building-omnistudio-datamapper）

数据映射器是 OmniStudio 堆栈的数据访问层。它们必须在引用它们的集成流程或 OmniScripts 创建和部署之前创建和部署。首先使用 `analyzing-omnistudio-dependencies` 了解现有组件依赖关系。

---

## 关键洞察

| 洞察 | 详细信息 |
|------|----------|
| **提取与 Turbo 提取** | 提取使用标准 SOQL 并包含关系查询。Turbo 提取使用服务器端编译的查询，适用于读密集型、高容量场景（速度提升 10 倍以上）。Turbo 提取不支持公式字段、关联列表或写操作。 |
| **转换是内存中的** | 转换数据映射器完全在内存中运行，不涉及 DML 或 SOQL。它们在集成流程的步骤之间重塑数据结构。用于 JSON 到 JSON 的转换、字段重命名和数据展平。 |
| **加载 = DML** | 加载数据映射器执行插入、更新、Upsert 或删除操作。它们需要正确的 FLS 检查和错误处理。始终在生产环境中部署加载数据映射器之前验证字段级安全。 |
| **OmniDataTransform 元数据** | 数据映射器存储为 OmniDataTransform 和 OmniDataTransformItem 记录。使用这些元数据类型名称检索和部署，而不是使用遗留的 DataRaptor API 名称。 |

---

## 工作流（5 阶段模式）

### 阶段 1：需求收集

**询问用户** 收集以下内容：
- 数据映射器类型（提取、转换、加载、Turbo 提取）
- 目标 Salesforce 对象和字段
- 目标组织别名
- 消费组件（集成流程、OmniScript 或 FlexCard 的名称）
- 数据量预期（记录数、频率）

**然后**：
1. 检查现有数据映射器：`Glob: **/OmniDataTransform*`
2. 检查现有 OmniStudio 元数据：`Glob: **/omnistudio/**`
3. 创建任务列表

---

### 阶段 2：设计与类型选择

| 类型 | 用例 | 命名前缀 | 支持 DML | 支持 SOQL |
|------|------|----------|----------|----------|
| **提取** | 使用关系查询从一个或多个对象读取数据 | `DR_Extract_` | 否 | 是 |
| **Turbo 提取** | 高容量只读查询，服务器端编译 | `DR_TurboExtract_` | 否 | 是（编译） |
| **转换** | 在流程步骤之间进行内存中的数据重塑 | `DR_Transform_` | 否 | 否 |
| **加载** | 写入数据（插入、更新、Upsert、删除） | `DR_Load_` | 是 | 否 |

**命名格式**：`[前缀][对象]_[目的]` 使用帕斯卡大小写

**示例**：
- `DR_Extract_Account_Details` -- 提取 Account 并包含相关 Contacts
- `DR_TurboExtract_Case_List` -- 用于 FlexCard 的高容量 Case 列表
- `DR_Transform_Lead_Flatten` -- 展平嵌套的 Lead 数据结构
- `DR_Load_Opportunity_Create` -- 插入 Opportunity 记录

---

### 阶段 3：生成与验证

**对于生成**：
1. 读取 `assets/omni-data-transform-extract.json`（提取）、`assets/omni-data-transform-transform.json`（转换）或 `assets/omni-data-transform-load.json`（加载）以获取 OmniDataTransform 记录模板
2. 读取 `assets/omni-data-transform-item.json` 以获取每个字段映射（OmniDataTransformItem）模板
3. 为提取类型配置查询过滤器、排序顺序和限制
4. 为加载类型设置查找映射和默认值
5. 验证所有映射字段的字段级安全

**对于审查**：
1. 读取现有的数据映射器配置
2. 运行最佳实践验证
3. 生成包含具体修复措施的提升报告

**运行验证**：读取 `assets/completion-summary-template.md` 以获取评分输出格式和阈值。

---

### 生成约束（强制要求）

**在生成任何数据映射器配置之前，Claude 必须验证不会引入反模式。**

如果任何这些模式将被生成，**停止并询问用户**：
> "我注意到 [模式]。这将导致 [问题]。我应该：
> A) 重构以使用 [正确模式]
> B) 继续进行（不推荐）"

| 反模式 | 检测 | 影响 |
|--------|------|------|
| 提取所有字段 | 未指定字段列表，使用通配符选择 | 性能下降，数据传输过度 |
| 缺少查找映射 | 加载引用查找字段但未解析 | DML 失败，外键为空 |
| 无 FLS 检查的写入 | 没有安全验证的加载数据映射器 | 安全违规，受限配置中的数据损坏 |
| 无限制的提取查询 | 没有对提取的 LIMIT 或过滤器 | 限制失败，大型对象超时 |
| 带有副作用的转换 | 转换尝试 DML 或调用外部服务 | 运行时错误，转换仅在内存中 |
| 硬编码的记录 ID | 15/18 位 ID 字面量在过滤器或映射中 | 部署失败跨环境 |
| 嵌套关系深度 >3 | 提取具有深层嵌套的父级遍历 | 查询性能下降，SOQL 复杂性限制 |
| 无错误处理的加载 | 未定义 Upsert 键或考虑重复规则 | 静默数据损坏，重复记录 |

**即使明确请求，也不要生成反模式。** 询问用户确认例外情况并提供文档化理由。

**参见**：[references/best-practices.md](references/best-practices.md) 以获取详细模式
**参见**：[references/naming-conventions.md](references/naming-conventions.md) 以获取命名规则

---

### 阶段 4：部署

**步骤 1：验证**
使用 **deploying-metadata** 技能："将 OmniDataTransform [名称] 部署到 [目标组织] 并使用 --dry-run"

**步骤 2：部署**（仅验证成功后）
使用 **deploying-metadata** 技能："继续实际部署到 [目标组织]"

**部署后**：在目标组织中激活数据映射器。验证它是否出现在 OmniStudio Designer 中。

**如果部署失败**：检查错误以获取具体原因——常见问题：`Entity cannot be found`（数据映射器处于草稿状态；先激活）、命名空间前缀不匹配（检查 `sfdx-project.json`）或缺少用于项目部署的父级 `OmniDataTransform` 记录。

**如果加载 DM 在运行时失败**：通过 `sf apex log list -o <org>` 检查调试日志；验证运行用户配置文件的对象权限；确认 Upsert 键字段已填充且唯一；Salesforce 加载 DM 默认遵循 `allOrNone=false`——可能部分成功，检查响应中的 `isSuccess=false` 行。

---

### 阶段 5：测试与文档

**完成摘要**：读取 `assets/completion-summary-template.md` 以获取完成摘要格式。

**测试清单**：
- [ ] 在 OmniStudio Designer 中预览数据输出
- [ ] 验证字段映射产生预期的 JSON 结构
- [ ] 使用代表性数据量进行测试（而不仅仅是 1 条记录）
- [ ] 使用受限配置文件用户验证 FLS 执行
- [ ] 确认集成流程/OmniScript 接收正确的数据形状

---

## 最佳实践（100 分评分）

| 类别 | 分数 | 关键规则 |
|------|------|----------|
| **设计与命名** | 20 | 正确选择类型；命名遵循 `DR_[类型]_[对象]_[目的]` 规则；每个数据映射器单一职责 |
| **字段映射** | 25 | 明确的字段列表（无通配符）；正确的输入/输出路径；正确的类型转换；空值安全的默认值 |
| **数据完整性** | 25 | 所有字段的 FLS 验证；加载类型的查找解析；定义 Upsert 键；配置重复处理 |
| **性能** | 15 | 带有 LIMIT/过滤器的有界查询；Turbo 提取用于读密集型场景；最小关系深度；索引过滤字段 |
| **文档** | 15 | OmniDataTransform 记录上的描述；字段映射的合理性文档；识别消费组件 |

**阈值**：✅ 90+（部署） | ⚠️ 67-89（审查） | ❌ <67（阻止 - 需要修复）

---

## CLI 命令

### 查询现有数据映射器

```bash
sf data query -q "SELECT Id,Name,Type FROM OmniDataTransform LIMIT 200" -o <org>
```

### 查询数据映射器字段映射

```bash
sf data query -q "SELECT Id,Name,InputObjectName,OutputObjectName,LookupObjectName FROM OmniDataTransformItem WHERE OmniDataTransformationId='<id>' LIMIT 200" -o <org>
```

### 检索数据映射器元数据

```bash
sf project retrieve start -m OmniDataTransform:<Name> -o <org>
```

### 部署数据映射器元数据

```bash
sf project deploy start -m OmniDataTransform:<Name> -o <org>
```

---

## 输出预期

此技能生成的可交付成果：

- **OmniDataTransform 记录** — 主要数据映射器记录，从 `assets/omni-data-transform-*.json` 模板构建
- **OmniDataTransformItem 记录** — 每个映射字段一个，从 `assets/omni-data-transform-item.json` 模板构建
- **验证评分报告** — 5 个类别的 100 分评分（格式为 `assets/completion-summary-template.md`）
- **部署确认** — 数据映射器已激活并在 OmniStudio Designer 中可见

---

## 跨技能集成

| 从技能 | 到 building-omnistudio-datamapper | 当... |
|--------|------------------|------|
| analyzing-omnistudio-dependencies | -> building-omnistudio-datamapper | "在创建数据映射器之前分析依赖关系" |
| generating-custom-object / generating-custom-field | -> building-omnistudio-datamapper | "在映射之前描述目标对象字段" |
| querying-soql | -> building-omnistudio-datamapper | "验证提取查询逻辑" |

| 从 building-omnistudio-datamapper | 到技能 | 当... |
|--------------------|----------|------|
| building-omnistudio-datamapper | -> building-omnistudio-integration-procedure | "创建调用此数据映射器的集成流程" |
| building-omnistudio-datamapper | -> deploying-metadata | "将数据映射器部署到目标组织" |
| building-omnistudio-datamapper | -> building-omnistudio-omniscript | "将数据映射器输出连接到 OmniScript" |
| building-omnistudio-datamapper | -> building-omnistudio-flexcard | "在 FlexCard 中显示数据映射器提取结果" |

---

## 注意事项

| 问题 | 解决方案 |
|------|----------|
| 大数据量（>10K 记录） | 使用 Turbo 提取；通过集成流程添加分页；警告关于堆限制 |
| 多态查找字段 | 在映射中指定具体对象类型；分别测试每种类型 |
| 提取中的公式字段 | 标准提取支持公式字段；Turbo 提取不支持——回退到标准提取 |
| 跨对象加载（主从） | 首先插入父记录，然后在单独的加载步骤中插入子记录；使用集成流程编排顺序 |
| 命名空间前缀字段 | 在字段路径中包含命名空间前缀（例如，`ns__Field__c`）；验证前缀与目标组织匹配 |
| 多货币组织 | 明确映射 CurrencyIsoCode；不要依赖默认货币假设 |
| 记录类型依赖映射 | 在提取中按记录类型过滤；在加载中设置 RecordTypeId；记录哪些记录类型受支持 |
| 草稿数据映射器无法检索 | `sf project retrieve start -m OmniDataTransform:<Name>` 仅适用于激活的 DM；激活后再检索 |
| 外键字段名称错误 | `OmniDataTransformItem` 上的父级查找是 `OmniDataTransformationId`（全词 "Transformation"），而不是 `OmniDataTransformId` |

---

## 备注

- **元数据类型**：OmniDataTransform（不是 DataRaptor——遗留名称已弃用）
- **API 版本**：需要 OmniStudio 管理包或 Industries Cloud
- **评分**：如果分数 < 67 则阻止部署；阅读 `assets/completion-summary-template.md` 获取分数格式
- **Turbo 提取限制**：不支持公式字段、关联列表、聚合查询、多态字段
- **激活**：数据映射器必须在部署后激活才能从集成流程调用（参见 Gotchas 了解草稿检索行为）
- **通过 Data API 创建**：使用 `sf api request rest --method POST --body @file.json` 创建 OmniDataTransform 和 OmniDataTransformItem 记录。`sf data create record --values` 标志无法处理文本区域中的 JSON。先将 JSON 身体写入临时文件。
