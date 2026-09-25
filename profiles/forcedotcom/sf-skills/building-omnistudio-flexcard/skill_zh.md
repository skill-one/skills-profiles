# building-omnistudio-flexcard: OmniStudio FlexCard 创建与验证

专注于 Salesforce 行业 FlexCard UI 组件的 OmniStudio 专家工程师。生成可部署的 FlexCard 定义，通过声明式数据绑定、集成流程数据源、条件渲染和适当的 SLDS（Salesforce Lightning Design System）样式，以一目了然的方式显示信息。所有 FlexCard 都将根据 7 个类别的 **130 分评分标准**进行验证。

## 范围

- **在范围内**：创建和验证 OmniStudio FlexCard 定义（`OmniUiCard`）；配置集成流程数据源；设计卡片布局、状态和操作按钮；根据 130 分评分标准打分；部署和激活
- **超出范围**：构建 OmniScripts（使用 `building-omnistudio-omniscript`）、创建集成流程（使用 `building-omnistudio-integration-procedure`）、映射完整依赖树（使用 `analyzing-omnistudio-dependencies`）、将元数据部署到 org（使用 `deploying-metadata`）

---

## 核心职责

1. **FlexCard 编写**：设计和构建具有正确布局、状态和字段映射的 FlexCard 定义
2. **数据源绑定**：配置集成流程数据源，包括正确的字段映射和错误处理
3. **测试生成**：针对多种数据状态（已填充、空、错误、多记录）验证卡片
4. **文档编写**：生成可部署的文档，包括数据源血缘关系和操作映射

## 文档映射

| 需求 | 文档 | 描述 |
|------|----------|-------------|
| **最佳实践** | [references/best-practices.md](references/best-practices.md) | 布局模式、SLDS、可访问性、性能 |
| **数据绑定** | [references/data-binding-guide.md](references/data-binding-guide.md) | IP 源、字段映射、条件渲染 |

---

## 关键：编排顺序

FlexCard 位于 OmniStudio 堆栈的呈现层。在构建依赖于它们的 FlexCard 之前，确保上游组件已存在。

```
analyzing-omnistudio-dependencies → building-omnistudio-datamapper → building-omnistudio-integration-procedure → building-omnistudio-omniscript → building-omnistudio-flexcard (你在这里)
```

FlexCard 从集成流程中消费数据，并可以启动 OmniScript。首先构建数据层，然后构建呈现层。

---

## 关键洞察

| 洞察 | 详情 |
|---------|--------|
| **配置字段** | `OmniUiCard` 使用 `DataSourceConfig` 进行数据源绑定，使用 `PropertySetConfig` 进行卡片布局、状态和操作。Core 命名空间中的 `OmniUiCard` 上没有 `Definition` 字段。 |
| **数据源绑定** | 数据源绑定到集成流程以获取实时数据；IP 必须在 FlexCard 可以检索数据之前处于活动状态并已部署 |
| **子卡片嵌入** | FlexCard 可以将其他 FlexCard 嵌入为子卡片，从而实现具有共享或独立数据源的复合布局 |
| **启动 OmniScript** | FlexCard 可以通过操作按钮启动 OmniScript，将卡片数据源中的上下文数据传递给 OmniScript 的输入 |
| **设计器虚拟对象** | FlexCard 设计器使用 `OmniFlexCardView` 作为虚拟列表对象（`/lightning/o/OmniFlexCardView/home`），与存储卡片记录的 `OmniUiCard` sObject 分开。通过 API 创建的卡片可能不会出现在“最近查看”中，直到在设计中打开它们。 |

---

## 工作流（5 阶段模式）

### 阶段 1：需求收集

在构建之前，与利益相关者澄清以下内容：

| 问题 | 重要性 |
|----------|---------------|
| 卡片的目的是什么？ | 确定布局类型和数据密度 |
| 需要哪些数据源？ | 确定所需的集成流程 |
| 它在哪个对象上下文中运行？ | 确定记录级与列表级显示 |
| 卡片应暴露哪些操作？ | 驱动按钮/链接配置和 OmniScript 集成 |
| 哪种布局最适合用例？ | 单卡片、列表、选项卡或弹出 |
| 是否有条件显示规则？ | 基于数据值显示/隐藏的字段或部分 |

### 阶段 2：设计与布局

在设计中之前，阅读 `references/best-practices.md` 以获取布局模式、SLDS 合规性、可访问性要求和性能指南。

#### 卡片布局选项

| 布局类型 | 用例 | 描述 |
|-------------|----------|-------------|
| **单卡片** | 记录摘要 | 一个卡片显示来自单个记录的字段 |
| **卡片列表** | 相关记录 | 绑定到数组数据源的重复卡片 |
| **选项卡卡片** | 多上下文 | 多个状态在一个卡片中显示为选项卡 |
| **弹出卡片** | 按需详情 | 从摘要卡片触发的可展开详情面板 |

#### 数据源配置

每个 FlexCard 数据源连接到集成流程（或其他源类型），并将响应字段映射到显示元素。

```
FlexCard → 数据源 (类型: IntegrationProcedure)
         → IP 名称 + 输入映射
         → 响应字段映射 → 卡片元素
```

- 使用 `{datasource.fieldName}` 合并语法将 IP 响应字段映射到卡片显示元素
- 配置输入参数以将记录上下文（例如，`{recordId}`）传递给 IP
- 当多个源为同一卡片提供数据时，设置数据源顺序

#### 操作按钮设计

| 操作类型 | 目的 | 配置 |
|-------------|---------|---------------|
| **启动 OmniScript** | 启动引导流程 | OmniScript 类型 + 子类型，传递上下文参数 |
| **导航** | 跳转到记录或 URL | 记录 ID 或带合并字段的 URL 模板 |
| **自定义操作** | 平台事件、LWC 等。 | 自定义操作处理程序与有效载荷映射 |

#### 条件可见性

- 基于数据值显示/隐藏字段，使用可见性条件
- 基于数据源结果显示/隐藏整个卡片状态
- 当数据源返回无记录时，显示空状态消息

### 阶段 3：生成与验证

在生成之前，阅读 `references/data-binding-guide.md` 以获取合并字段语法、数据源类型和多源协调指南。
在运行 130 分验证时，阅读 `references/scoring-rubric.md` 以获取所有 7 个评分类别的完整逐项分解。

1. 生成 FlexCard 定义 JSON
2. 验证所有数据源引用解析为活动的集成流程
3. 运行 130 分评分标准（见评分部分下方）
4. 验证合并字段语法与 IP 响应结构匹配
5. 检查所有交互元素的可访问性属性

### 阶段 4：部署

1. 确保所有上游集成流程已部署并处于活动状态
2. 运行干运行检查：使用 `deploying-metadata` 技能与 `--dry-run` 在提交之前运行
3. 部署 FlexCard 元数据（`OmniUiCard`）— `sf project deploy start` 可以安全地重新运行；它 upserts 现有记录
4. 在目标 org 中激活 FlexCard
5. 将 FlexCard 嵌入目标 Lightning 页面、OmniScript 或父 FlexCard
6. **如果部署失败**：检查错误输出以获取具体原因 — 常见问题：上游 IP 未部署（`Cannot find OmniIntegrationProcedure`）、缺少命名空间前缀（`Entity not found`），或 FlexCard 仍处于草稿状态（激活后再检索）

### 阶段 5：测试

针对每个 FlexCard 测试多个数据场景：

| 场景 | 需要验证 |
|----------|---------------|
| **填充数据** | 所有字段正确渲染，合并字段解析 |
| **空数据** | 显示友好的空状态消息，没有损坏的合并字段 |
| **错误状态** | 当 IP 返回错误或超时时优雅处理 |
| **多记录** | 卡片列表渲染正确数量的项，分页正常工作 |
| **操作按钮** | OmniScript 使用正确的预填充数据启动 |
| **条件字段** | 基于数据值正确切换可见性规则 |
| **移动端** | 卡片布局适应较小的视口宽度 |
| **长文本值** | 使用省略号截断，并提供弹出或工具提示以显示完整文本 |
| **大记录集** | 使用卡片列表并分页；限制初始加载为 10-25 条记录 |
| **空字段值** | 使用条件可见性隐藏空值字段，而不是显示空标签 |
| **混合数据新鲜度** | 当多个数据源具有不同的刷新率时，显示“最后更新”指示器 |

---

## 生成约束

在生成 FlexCard 定义时避免以下模式：

| 反模式 | 为什么不对 | 正确方法 |
|--------------|---------------|-----------------|
| 引用不存在的 IP 数据源 | 卡片在运行时无法加载数据 | 在绑定之前验证 IP 是否存在并处于活动状态 |
| 样式中硬编码颜色 | 破坏 SLDS 主题和暗黑模式 | 使用 SLDS 设计令牌和 CSS 自定义属性 |
| 缺少可访问性属性 | 未能符合 WCAG 合规性 | 添加 `aria-label`、`role` 和键盘处理程序 |
| 过度嵌套子卡片 | 深层嵌套导致性能下降 | 限制为 2 级嵌套；尽可能扁平化 |
| 忽略空状态 | 当数据源返回无记录时 UI 损坏 | 配置明确的空状态消息 |
| 硬编码记录 ID | 卡片跨环境损坏 | 使用合并字段和上下文驱动参数 |

---

## 评分标准（130 分）

所有 FlexCard 都将根据 7 个类别进行验证。**阈值**：✅ 90+（部署） | ⚠️ 67-89（审核） | ❌ <67（阻止 - 需要修复）

| 类别 | 分数 | 标准 |
|----------|--------|----------|
| **设计与布局** | 25 | 合适的布局类型、逻辑字段分组、响应式设计、一致间距、清晰的视觉层次 |
| **数据绑定** | 20 | 正确的 IP 引用、正确的合并字段语法、输入参数映射、多源协调 |
| **操作与导航** | 20 | 操作按钮配置正确、OmniScript 启动参数映射、导航目标有效、操作标签描述性 |
| **样式** | 20 | 使用 SLDS 令牌（无硬编码颜色）、一致的排版、正确使用卡片/瓦片模式、兼容暗黑模式 |
| **可访问性** | 15 | 交互元素上的 `aria-label`、键盘可导航的操作、足够的颜色对比度、屏幕阅读器友好的字段标签 |
| **测试** | 15 | 验证填充数据、空状态、错误状态、多记录场景和移动视口 |
| **性能** | 15 | 最小化数据源调用、限制子卡片嵌套（最多 2 级）、无冗余 IP 调用、非可见状态的懒加载 |

阅读 `references/scoring-rubric.md` 以获取所有 7 个类别的完整逐项分解。

---

## CLI 命令

阅读 `scripts/flexcard-commands.sh` 以获取所有 FlexCard CLI 命令（查询、检索、部署）。将 `<org>` 替换为您的 org 别名，将 `<Name>` 替换为 FlexCard API 名称。

---

## 数据源绑定

### FlexCard 数据源配置

`OmniUiCard` 上的 `DataSourceConfig` 字段包含 JSON 格式的数据源绑定。`PropertySetConfig` 字段包含卡片布局、状态和字段定义。

> **重要提示**：Core 命名空间中的 `OmniUiCard` 上没有 `Definition` 字段。使用 `DataSourceConfig` 进行数据源，使用 `PropertySetConfig` 进行布局。

阅读 `assets/omni-ui-card.json` 以获取完整的 OmniUiCard 记录模板，包括 `DataSourceConfig` JSON 结构。

### 数据源类型

| 类型 | `dataSource.type` | 使用场景 |
|------|-------------------|-------------|
| **集成流程** | `IntegrationProcedures`（复数，大写 P） | 主要模式；调用 IP 获取实时数据 |
| **SOQL** | `SOQL` | 直接查询（谨慎使用；优先使用 IP 进行抽象） |
| **Apex 远程** | `ApexRemote` | 调用自定义 Apex 类 |
| **REST** | `REST` | 通过命名凭证调用外部 API |
| **自定义** | `Custom` | 自定义数据提供者（直接传递 JSON 正文） |

### 从 IP 响应映射字段

使用合并字段语法将 IP 响应字段映射到卡片显示元素：

```
IP 响应:                    FlexCard 合并字段:
─────────────                   ─────────────────────
{ "Name": "Acme Corp" }   →    {Name}
{ "Account": {            →    {Account.Name}
    "Name": "Acme Corp"
  }
}
{ "records": [             →    {records[0].Name}  (单个)
    { "Name": "Acme" }          或使用卡片列表布局迭代
  ]
}
```

### 输入参数映射

将上下文从托管页面传递到 IP 数据源：

| 上下文变量 | 来源 | 示例 |
|-----------------|--------|---------|
| `{recordId}` | 当前记录页面 | 传递给 IP 以查询相关数据 |
| `{userId}` | 运行用户 | 按当前用户过滤数据 |
| `{param.customKey}` | URL 参数或父卡片 | 从父 FlexCard 或 URL 传递 |

---

## 跨技能集成

| 技能 | 与 building-omnistudio-flexcard 的关系 |
|-------|---------------------------|
| **building-omnistudio-integration-procedure** | 构建 FlexCard 消费的数据源 IP |
| **building-omnistudio-omniscript** | 构建 FlexCard 操作按钮启动的 OmniScript |
| **building-omnistudio-datamapper** | 构建 OmniScript 在底层使用的 DataRaptors/DataMappers |
| **analyzing-omnistudio-dependencies** | 分析 FlexCards、IPs 和 OmniScripts 之间的依赖链 |
| **deploying-metadata** | 部署 FlexCard 元数据以及上游依赖项 |
| **generating-lwc-components** | 在 FlexCard 中嵌入的自定义 LWC 组件构建 |

---

## 注意事项

| 场景 | 处理 |
|----------|---------|
| **空数据** | 配置明确的空状态，显示友好的用户消息；不要显示“无数据”或空白卡片 |
| **错误状态** | 当 IP 数据源返回错误时显示有意义的错误消息；记录错误以供调试 |
| **移动端响应性** | 使用单列布局；避免水平滚动；在 320px 视口宽度下测试 |
| **长文本值** | 使用省略号截断，并提供弹出或工具提示以显示完整文本 |
| **大记录集** | 使用卡片列表并分页；限制初始加载为 10-25 条记录 |
| **空字段值** | 使用条件可见性隐藏空值字段，而不是显示空标签 |
| **混合数据新鲜度** | 当多个数据源具有不同的刷新率时，显示“最后更新”指示器 |

---

## FlexCard 与 LWC 决策指南

| 因素 | FlexCard | LWC |
|--------|----------|-----|
| **构建方法** | 声明式（拖放） | 代码（JS、HTML、CSS） |
| **数据绑定** | 集成流程合并字段 | Wire 服务、Apex、GraphQL |
| **最适合** | 一目了然的显示信息 | 复杂的交互式 UI |
| **测试** | 手动 + 数据状态验证 | Jest 单元测试 + 手动 |
| **定制** | 受 OmniStudio 框架限制 | 完全的平台灵活性 |
| **重用** | 作为子卡片嵌入 | 作为子组件导入 |
| **选择时机** | 标准卡片布局与 IP 数据 | 自定义行为、动画、复杂状态 |

---

## 依赖项

**必需**：具有 OmniStudio（ Industries Cloud）许可证的目标 org，`sf` CLI 认证
**对于数据源**：目标 org 中部署的活动集成流程
**对于操作**：目标 org 中部署的活动 OmniScripts（如果操作按钮启动 OmniScript）
**评分**：如果分数 < 67，则阻止部署

**幂等性**：`sf project deploy start` upserts 元数据 — 可以安全地重新运行而不会创建重复项。查询以确认当前状态：参见 `scripts/flexcard-commands.sh`。

**命名空间处理**：在受管理的包 org 中，元数据类型可能带有前缀（例如，`omnistudio__OmniUiCard`）。检查 `sfdx-project.json` 以获取命名空间。参见 `scripts/flexcard-commands.sh` 以获取命名空间部署命令。

**程序化创建 FlexCard**：使用 REST API（`sf api request rest --method POST --body @file.json`）。必需字段：`Name`、`VersionNumber`、`OmniUiCardType`（例如，`Child`）。设置 `DataSourceConfig`（JSON 字符串）以进行数据源绑定，设置 `PropertySetConfig`（JSON 字符串）以进行卡片布局。标志 `sf data create record --values` 无法处理 textarea 字段中的 JSON。创建后更新 `IsActive=true` 以激活。
