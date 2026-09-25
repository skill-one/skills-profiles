# omnistudio-epc-catalog-generate: CME EPC 产品和报价建模

专业的 Salesforce 行业 CME EPC 模型器，用于创建基于 Product2 的目录条目、分配可配置属性，并通过 Product Child Item 关系构建报价包。

此技能针对 DataPack 风格的元数据编写进行了优化。使用 `assets/` 中的规范模板集：

- `assets/product2-offer-template.json`
- `assets/attribute-assignment-template.json`
- `assets/product-child-item-template.json`
- `assets/pricebook-entries-template.json`
- `assets/price-list-entries-template.json`
- `assets/object-field-attributes-template.json`
- `assets/orchestration-scenarios-template.json`
- `assets/decomposition-relationships-template.json`
- `assets/compiled-attribute-overrides-template.json`
- `assets/override-definitions-template.json`
- `assets/parent-keys-template.json`

额外的打包示例位于 `assets/examples/` 下，按报价类型组织：

- `assets/examples/samsung-galaxy-s22-bundle/` — 报价包示例
- `assets/examples/business-internet-premium-fttc-simple-offer/` — 简单报价示例
- `assets/examples/business-internet-pro-vpl-simple-offer/` — 简单报价示例
- `assets/examples/static-ip-simple-offer/` — 简单报价示例

`examples/business-internet-plus-bundle/` 文件夹包含一个带逐步文本记录的生成报价包示例。

根 `assets/` 文件夹包含用于报价编写的规范基线模板集。

---

## 范围

- **在范围内**：创建和审查 EPC Product2 记录、Product Child Items、属性元数据、报价包、定价条目、分解和编排工件以及 DataPack JSON 有效负载
- **超出范围**：OmniScript/FlexCard/集成程序设计（使用 `omnistudio-omniscript-generate`、`omnistudio-flexcard-generate` 或 `omnistudio-integration-procedure-generate`）、Apex 业务逻辑实现（使用 `platform-apex-generate`）、部署管道故障排除（使用 `platform-metadata-deploy`）

---

## 快速参考

- **主要对象**：`Product2`（EPC 产品和报价记录）
- **属性数据**：`%vlocity_namespace%__AttributeMetadata__c`、`%vlocity_namespace%__AttributeDefaultValues__c` 和 `%vlocity_namespace%__AttributeAssignment__c`
- **报价包组合**：`%vlocity_namespace%__ProductChildItem__c`
- **报价标记**：`%vlocity_namespace%__SpecificationType__c = "Offer"` 和 `%vlocity_namespace%__SpecificationSubType__c = "Bundle"`
- **配套报价工件**：定价条目、报价列表条目、对象字段属性、编排场景、分解关系、编译属性覆盖、覆盖定义和父键

**评分**：6 个类别共 120 分。  
**阈值**：`>= 95` 可部署 | `70-94` 需要审查 | `< 70` 阻止并修复。

**术语表**：EPC = 企业产品目录 | CME = 通信、媒体和能源 | DataPack = Vlocity JSON 部署工件 | PCI = ProductChildItem

---

## 资产模板集

在创建报价有效负载时使用根 `assets/` 模板：

- `product2-offer-template.json`
- `attribute-assignment-template.json`
- `product-child-item-template.json`
- `pricebook-entries-template.json`
- `price-list-entries-template.json`
- `object-field-attributes-template.json`
- `orchestration-scenarios-template.json`
- `decomposition-relationships-template.json`
- `compiled-attribute-overrides-template.json`
- `override-definitions-template.json`
- `parent-keys-template.json`

对于额外的实际变体，使用 `assets/examples/` 下按示例组织的文件夹。

---

## 核心职责

1. **产品创建**：创建具有一致命名、生命周期日期、状态和分类字段的 EPC Product2 记录。
2. **属性建模**：定义基于类别的属性、默认值、有效值集、显示序列和必需标志。
3. **报价包建模**：使用 `%vlocity_namespace%__ProductChildItem__c` 记录和清晰的数量规则组合报价和子产品。
4. **配套元数据生成**：从相同的报价基线生成和同步所有相关报价文件（定价、对象字段属性、编排/分解、覆盖、父键）。
5. **DataPack 一致性**：在部署时保持记录源键、全局键、查找对象和命名空间字段内部一致性。

---

## 调用规则（强制）

当提示意图匹配以下任一时，路由到此技能：

1. **创建产品报价包**：
   - 用户要求创建/构建/生成/建模 EPC 报价包。
   - 用户要求 Product2 报价设置与 Product Child Items。
   - 用户要求从模板/示例生成报价 DataPack JSON 工件。

2. **评分或审查现有产品报价包**：
   - 用户要求评分/评估/验证/审计现有 EPC 报价包。
   - 用户要求将 120 点评分标准应用于现有的 Product2/ProductChildItem (PCI)/属性有效负载。
   - 用户要求对报价元数据提出风险发现、质量差距或修复建议。

**指令优先级**：将这两个意图视为直接触发 `omnistudio-epc-catalog-generate` 的触发器，即使提示简短且未提及 EPC 的名称。

---

## 工作流（创建/审查）

### 阶段 0：先决条件

在进行之前，请验证：

1. Salesforce 行业组织，已启用 EPC
2. sf CLI 中的认证组织别名 — 运行 `sf org display --target-org <alias>` 以确认
3. 命名空间模型识别：`%vlocity_namespace%`、`vlocity_cmt` 或核心

如果任何先决条件未满足，请要求用户提供组织别名或命名空间，然后再继续。

---

### 阶段 1：识别目录意图

询问：

- 产品类型：**规范产品**或**报价包**
- 域分类法：系列、类型/子类型、分类路径和渠道
- 属性要求：必需/可选、picklist 值、默认值
- 报价包组合：子产品、数量约束、可选与必需
- 目标组织命名空间模型：`%vlocity_namespace%`、`vlocity_cmt` 或核心

**幂等性检查**：如果提供了 `ProductCode`，则在生成工件之前验证是否已存在匹配的 Product2：

```bash
sf data query --query "SELECT Id, Name, ProductCode FROM Product2 WHERE ProductCode = '<code>'" --target-org <alias>
```

如果找到匹配项，请要求用户确认这是净新记录还是对现有记录的更新，然后再继续。

### 阶段 1A：完整报价包的澄清问题（强制）

在生成新的报价包有效负载之前，询问澄清问题，直到所有必需的输入都已知。

必需澄清清单：

1. **报价身份**
   - 报价名称和 `ProductCode` 是什么？
   - 这是净新记录还是对现有 Product2 报价的更新？
2. **目录分类**
   - Family、Type/SubType 和渠道/销售上下文值是什么？
   - 是否应设置 `SpecificationType=Offer` 和 `SpecificationSubType=Bundle`？
3. **生命周期和可用性**
   - `EffectiveDate` 和 `SellingStartDate` 是什么？
   - 是否应在创建时将 `IsActive` 和 `%vlocity_namespace%__IsOrderable__c` 设置为 true？
4. **子产品组合**
   - 包含哪些子产品（每个的名称/代码）？
   - 对于每个子产品，必需/可选语义和序列顺序是什么？
5. **每个子产品的数量行为**
   - `MinQuantity`、`MaxQuantity` 和默认 `Quantity` 是什么？
   - 是否应强制执行每个行中的 `%vlocity_namespace%__MinMaxDefaultQty__c`？
6. **属性模型**
   - 哪些属性是必需的 vs 可选的？
   - 有效值、默认值、显示类型和显示序列是什么？
7. **定价和配套工件**
   - 现在是否应生成定价条目和报价列表条目？
   - 是否应在同一请求中包含编排/分解/覆盖/父键文件？
8. **命名空间和键**
   - 应使用哪种命名空间约定（`%vlocity_namespace%` vs `vlocity_cmt`）？
   - 是否有现有的全局键/源键要保留？

如果任何必需清单项未回答，则不要生成最终报价包文件；先问有针对性的后续问题。

### 阶段 2：构建 Product2 骨干

对于每个新的 EPC 记录，定义：

- `Name`
- `ProductCode`（唯一、稳定、与环境无关）
- `%vlocity_namespace%__GlobalKey__c`（稳定的 UUID 风格键）
- `%vlocity_namespace%__SpecificationType__c` 和 `%vlocity_namespace%__SpecificationSubType__c`
- `%vlocity_namespace%__Status__c` 和日期字段（`EffectiveDate`、`SellingStartDate`）
- `IsActive` 和 `%vlocity_namespace%__IsOrderable__c`

使用 `assets/product2-offer-template.json` 作为基线结构。

### 阶段 3：添加属性

当属性需要时：

1. 填充 `%vlocity_namespace%__AttributeMetadata__c` 类别和 `productAttributes` 记录。
2. 填充 `%vlocity_namespace%__AttributeDefaultValues__c` 以包含属性代码到默认值映射。
3. 创建 `%vlocity_namespace%__AttributeAssignment__c` 记录，包含：
   - 类别链接
   - 属性链接
   - UI 显示类型（下拉菜单等）
   - 有效值和默认标记

使用 `assets/attribute-assignment-template.json` 作为分配基线。

### 阶段 4：构建报价包

对于报价：

1. 将父 `Product2` 记录作为报价（`SpecificationType=Offer`，`SpecificationSubType=Bundle`）。
2. 创建根 `%vlocity_namespace%__ProductChildItem__c` 行（`IsRootProductChildItem=true`）。
3. 添加每个组件的子行，包含：
   - 父和子引用
   - 序列和行号
   - 最小/最大/默认数量行为（`MinMaxDefaultQty`、`MinQuantity`、`MaxQuantity`、`Quantity`）
4. 仅当行为与继承/默认行为不同时才使用覆盖行。

使用 `assets/product-child-item-template.json` 用于子关系结构。

对于完整的报价有效负载，还同步并包含：

- `assets/pricebook-entries-template.json`
- `assets/price-list-entries-template.json`
- `assets/object-field-attributes-template.json`
- `assets/orchestration-scenarios-template.json`
- `assets/decomposition-relationships-template.json`
- `assets/compiled-attribute-overrides-template.json`
- `assets/override-definitions-template.json`
- `assets/parent-keys-template.json`

### 阶段 4B：生成配套元数据文件

当用户要求生成报价时，一起生成/更新所有配套文件作为一个连贯的集合：

1. `pricebook-entries-template.json` 和 `price-list-entries-template.json`
   - 保持与父报价的 Product2 GlobalKey/ProductCode 引用一致。
2. `object-field-attributes-template.json`
   - 保持对象类引用和字段映射与相同的报价模型一致。
3. `orchestration-scenarios-template.json` 和 `decomposition-relationships-template.json`
   - 保持分解和编排工件与报价子项一致。
4. `compiled-attribute-overrides-template.json` 和 `override-definitions-template.json`
   - 保持覆盖键和引用与属性元数据和分配一致。
5. `parent-keys-template.json`
   - 保持父链接值与生成的工件键同步。

**强制规则**：除非用户明确要求有限文件范围，否则在请求完整报价有效负载时不要生成部分子集。

### 阶段 5：验证和交接

读取 `assets/completion-block-template.txt` 并填写每个字段以生成交接摘要块。

---

## 输出预期

对于完整的报价包请求，生成以下文件：

| 文件模式 | 内容 |
|---|---|
| `*_DataPack.json` | Product2 报价记录 |
| `*_AttributeAssignments.json` | 属性类别和分配有效负载 |
| `*_ProductChildItems.json` | 根和子 ProductChildItem (PCI) 行 |
| `*_PricebookEntries.json` | 标准和自定义定价条目 |
| `*_PriceListEntries.json` | 报价列表条目 |
| `*_ObjectFieldAttributes.json` | 对象字段映射 |
| `*_OrchestrationScenarios.json` | 编排元数据 |
| `*_DecompositionRelationships.json` | 分解元数据 |
| `*_CompiledAttributeOverrides.json` | 编译属性覆盖有效负载 |
| `*_OverrideDefinitions.json` | 覆盖定义有效负载 |
| `*_ParentKeys.json` | 父键链接 |

对于规范产品（非包）请求，只需要 DataPack、AttributeAssignments、PricebookEntries 和 PriceListEntries 文件。

如果任何文件生成失败，请立即停止。列出所有成功生成的文件，并指示用户在重试完整包之前删除部分集。不要生成其余文件，直到用户确认已删除部分集并可以开始新尝试。部分包会在 DataPack 导入时导致 GlobalKey 不匹配。

---

## 注意事项

| 问题 | 解决方案 |
|---|---|
| 属性默认值不在有效值列表中 | 确保默认值存在于 `values[]` 数组中 — 购物车在运行时将拒绝无效的默认值 |
| 缺少根 ProductChildItem 行 | 在缺少 `IsRootProductChildItem=true` 时报价包遍历中断 — 始终首先创建根行 |
| 一个有效负载中混合命名空间约定 | 选择一种命名空间样式（`%vlocity_namespace%` vs `vlocity_cmt`）并跨所有文件一致地应用它 |
| 同一属性类别中存在重复显示序列 | UI 排序冲突 — 使用间隔值（10、20、30）以允许未来插入而不会发生冲突 |
| `ProductCode` 包含环境后缀 | 破坏跨组织引用 — 删除 `_DEV`、`_UAT`、`_PROD` 后缀 |
| 配套文件使用不同的报价名称生成 | 键不匹配会破坏 DataPack 导入 — 从相同的基线报价名称和 GlobalKey 生成所有配套文件 |
| DataPack 导入失败并显示 `Key not found` 错误 | 查找对象引用指向目标组织中缺失的 GlobalKey — 在导入前验证所有配套文件中的 GlobalKey 一致性 |
| DataPack 导入静默回滚 | 在部署期间添加 `--verbose` 并检查日志以查找触发回滚的特定记录和字段 |
| 同一包中文件存在命名空间不匹配 | 在一个有效负载中混合 `%vlocity_namespace%` 和 `vlocity_cmt` 样式会导致字段解析失败 — 在整个有效负载中强制执行单一的命名空间样式 |

---

## 生成约束（强制）

如果出现任何反模式，请停止并要求确认后再继续。

| 反模式 | 为什么失败 | 必需的修正 |
|---|---|---|
| 缺少 `ProductCode` 或不稳定的代码值 | 破坏报价/购物车引用和包差异 | 使用确定的代码约定 |
| 在关系中硬编码组织特定 ID | 跨组织/环境失败 | 使用具有匹配键/全局键的查找对象 |
| 无根 PCI 行的报价包 | 运行时报价包遍历问题 | 添加根 `%vlocity_namespace%__ProductChildItem__c` |
| 属性默认值不在有效值中 | 无效的购物车配置默认值 | 确保默认值存在于允许的值集中 |
| 同一属性类别中存在重复显示序列 | UI 排序冲突 | 强制唯一和间隔序列值 |
| 标记为活动的报价包存在不完整的子引用 | 运行时破坏报价包 | 在激活前完成并验证子链接集 |
| 混合命名空间样式（snake_case、临时缩写） | 降低可维护性和可发现性 | 从参考文档中强制执行命名约定 |

---

## 评分模型（120 分）

阅读 `references/scoring-model.md` 了解完整的 6 类别评分标准及每个类别的标准。

| 类别 | 分数 |
|---|---|
| 目录身份和命名 | 20 |
| EPC 产品结构 | 20 |
| 属性建模 | 25 |
| 报价包组合 | 25 |
| DataPack 完整性 | 15 |
| 文档和交接 | 15 |
| **总计** | **120** |

---

## CLI 和验证命令

阅读 `scripts/cli-validation-commands.sh` 以获取 sf CLI 查询，用于检查和验证组织中的 EPC 工件。运行前将 `<org>` 替换为您的认证组织别名。

---

## 示例技能调用命令

阅读 `scripts/sample-invocations.sh` 以获取涵盖常见 EPC 建模任务的示例调用。如果不同，请将 `cursor-agent` 替换为您的本地代理命令包装器。

---

## 参考文件索引

| 文件 | 何时阅读 |
|------|-------------|
| `assets/product2-offer-template.json` | 阶段 2 — 每个 Product2 报价记录的基线结构 |
| `assets/attribute-assignment-template.json` | 阶段 3 — 属性分配结构 |
| `assets/product-child-item-template.json` | 阶段 4 — 根和子 PCI 行结构 |
| `assets/pricebook-entries-template.json` | 阶段 4B — 定价条目配套文件 |
| `assets/price-list-entries-template.json` | 阶段 4B — 报价列表条目配套文件 |
| `assets/object-field-attributes-template.json` | 阶段 4B — 对象字段映射配套文件 |
| `assets/orchestration-scenarios-template.json` | 阶段 4B — 编排场景配套文件 |
| `assets/decomposition-relationships-template.json` | 阶段 4B — 分解关系配套文件 |
| `assets/compiled-attribute-overrides-template.json` | 阶段 4B — 编译属性覆盖配套文件 |
| `assets/override-definitions-template.json` | 阶段 4B — 覆盖定义配套文件 |
| `assets/parent-keys-template.json` | 阶段 4B — 父键配套文件 |
| `assets/completion-block-template.txt` | 阶段 5 — 交接摘要块模板 |
| `assets/examples/samsung-galaxy-s22-bundle/` | 阶段 4 — 报价包示例；首先加载 `*_DataPack.json` 和 `*_ProductChildItems.json`，然后按需加载配套文件 |
| `assets/examples/business-internet-premium-fttc-simple-offer/` | 阶段 4 — 简单报价（FTTC）示例；首先加载 `*_DataPack.json` 和 `*_AttributeAssignments.json` |
| `assets/examples/business-internet-premium-fttc-simple-offer/Business-Internet-Premium-FTTC_RuleAssignments.json` | 阶段 4 — FTTC 报价规则分配示例；建模基于规则的属性约束时加载 |
| `assets/examples/business-internet-pro-vpl-simple-offer/` | 阶段 4 — 简单报价（Pro VPL）示例；首先加载 `*_DataPack.json` 和 `*_AttributeAssignments.json` |
| `assets/examples/static-ip-simple-offer/` | 阶段 4 — 简单报价（静态 IP）示例；首先加载 `*_DataPack.json` 和 `*_AttributeAssignments.json` |
| `examples/business-internet-plus-bundle/` | 阶段 4 — 生成的报价包示例，带逐步文本记录；首先加载 `TRANSCRIPT.md`，然后加载其中引用的特定 JSON 文件 |
| `references/epc-field-guide.md` | 阶段 2 & 3 — EPC 字段级指南和常见陷阱 |
| `references/naming-conventions.md` | 阶段 2 & 3 — 命名和键约定 |
| `references/scoring-model.md` | 阶段 5 — 完整 6 类别评分标准，包含每个类别的标准 |
| `scripts/cli-validation-commands.sh` | 阶段 5 — sf CLI 查询，用于验证组织中的 EPC 工件 |
| `scripts/sample-invocations.sh` | 启动时 — 参考 EPC 任务常见调用的示例调用 |

---

## 跨技能集成

| 从技能 | 到 `omnistudio-epc-catalog-generate` | 何时 |
|---|---|---|
| omnistudio-dependencies-analyze | -> omnistudio-epc-catalog-generate | 需要当前依赖和命名空间库存时 |
| platform-custom-object-generate / platform-custom-field-generate | -> omnistudio-epc-catalog-generate | 需要对象或字段就绪后才能进行 EPC 建模 |
| platform-soql-query | -> omnistudio-epc-catalog-generate | 需要现有目录查询分析 |

| 从 `omnistudio-epc-catalog-generate` | 到技能 | 何时 |
|---|---|---|
| omnistudio-epc-catalog-generate | -> omnistudio-omniscript-generate | 使用建模的目录配置引导式销售 UX |
| omnistudio-epc-catalog-generate | -> omnistudio-integration-procedure-generate | 构建服务器端编排以覆盖产品和定价有效负载 |
| omnistudio-epc-catalog-generate | -> platform-metadata-deploy | 部署验证的目录元数据 |

---

## 外部参考

本地参考：

- [references/epc-field-guide.md](references/epc-field-guide.md) — EPC 字段级指南和最小必需字段
- [references/naming-conventions.md](references/naming-conventions.md) — 产品、属性和报价的命名和键约定

---

## 备注

- 此技能有意为 DataPack 首先优化，并针对 `vlocity/Product2/...` 工件编写进行了优化。
- 保留模板中的 `%vlocity_namespace%` 占位符以保持可移植性。
- 优先创建可重用规范产品，然后通过子关系组装报价。
