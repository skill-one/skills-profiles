# 自动化：沙盒复制后配置生成

将客户的沙盒刷新/复制后操作指南（SOP）转换为结构化的 JSON 数组，供复制后自动化工具使用。每个条目都是一个声明性指令：要更新的 Salesforce 配置、涉及的字段、是否激活以及运行顺序。

## 停止——在编写任何 JSON 之前必须执行此操作

不要凭记忆编写输出。在编写文件之前，你必须打开并阅读 `assets/config_template.json`，并从其中复制每个操作的条目。每个输出条目都是这三个形状中的一种——五个顶层键，没有其他键，没有包装对象：

```json
[
  {
    "ConfigurationName": "OutboundMessages",
    "Label": "IR_Account_OBM_PROD",
    "Fields": { "EndpointUrl": "https://uat.example.com/services/account", "Object": "Account" },
    "IsActive": true,
    "ExecutionOrder": 1
  },
  {
    "ConfigurationName": "RemoteSiteSettings",
    "Label": "R12_Remote_Site",
    "Fields": { "RemoteSiteUrl": "https://uat.example.com" },
    "IsActive": true,
    "ExecutionOrder": 2
  },
  {
    "ConfigurationName": "ScheduledApex",
    "Label": "Nightly Data Sync",
    "Fields": { "ApexClassName": "NightlyDataSyncScheduler", "CronExpression": "0 0 2 * * ?", "JobName": "Nightly Data Sync" },
    "IsActive": true,
    "ExecutionOrder": 3
  }
]
```

- `ConfigurationName`：必须为 `OutboundMessages`、`RemoteSiteSettings` 或 `ScheduledApex`——永远不是 `Type`、`Name` 或 `Operation`。
- OBM `Fields`：`EndpointUrl` + `Object`（两者都必需）。RemoteSite `Fields`：仅 `RemoteSiteUrl`——永远不是 `Url`/`RemoteSiteURL`。ScheduledApex `Fields`：`ApexClassName` + `CronExpression` + `JobName`（三者都必需）。
- 顶层是一个 JSON 数组。没有 `steps`/`actions`/`records` 包装。没有 `<…>` 或 `REPLACE_WITH_…` 占位符会保留到输出中。

如果你宣布“我现在将编写……”而没有阅读模板和目录，请停止并先阅读它们——凭记忆猜测会产生错误的键并在运行时失败。

## 范围

- **在范围内**：以任何支持的格式（PDF、xlsx、csv、JSON、docx、Markdown、纯文本、粘贴的摘录或包含数据表的图像——例如，带有端点 URL 的 Outbound Messages 列表的截图）读取客户 SOP，识别复制后/刷新操作，将每个操作映射到支持的 `ConfigurationName`，发出规范 JSON 数组。
- **超出范围**：生成 Salesforce 元数据 XML（委托给 `generating-*` 技能）、部署任何内容到组织、运行复制后工具、推断或编造 SOP 中未提供的值——如果 SOP 没有为操作提供具体的 URL/值，则跳过该操作。

**每个发出的条目必须用客户源中的实际值填充所有字段。** 没有空字符串、没有 `null`、没有 `<from-backup>` / `TBD` / `TODO` 占位符。客户永远不会在输出中看到未填充的字段——如果找不到值，请跳过条目并在响应中显示它。见下一条相应的规则。

---

## 必须输入

生成之前收集或推断：

- **SOP 源（s）**：一个或多个路径（或粘贴的内容），格式为：
  PDF、xlsx、csv、JSON、docx、Markdown、纯文本或图像（.png/.jpg/.jpeg/.tiff/.bmp）。
  多个文件很常见——操作列表和端点表有时位于不同的文件中。读取用户提供的每个文件。
- **目标输出路径**：JSON 配置应写入的位置。默认为当前目录中的 `post-copy-config.json`，除非指定。
- **范围过滤器**（可选）：如果 SOP 涵盖多个环境（例如，fcQA、fcUAT、多个沙盒），请确认用户希望在输出中包含哪个子集。

如果用户提供清晰的 SOP 和目标，请立即生成，不要问不必要的问题。

---

## 工作流程

所有步骤都是顺序的。步骤 1–5（读取 SOP、目录、模板和模式）是**编写的前提条件**——你不能跳到编写步骤。如果你发现自己准备发出 JSON，而没有阅读 `assets/config_template.json` 和 `references/configuration_catalog.md`，请先回过头去阅读它们。

1. **定位并读取每个提供的 SOP 源**——读取 `references/source_format_handling.md` 以获取每种格式（PDF、xlsx、csv、JSON、docx、图像）的确切提取配方。大致上：
   - **PDF**：使用 `pypdf` 提取文本（文本层），如果文本层为空，则使用 `pytesseract` OCR 基于图像的页面。
   - **xlsx**：使用 `openpyxl` 读取每个工作表（`data_only=True`），扫描所有列，包括默认可见范围之外的列，检查单元格注释和嵌入媒体。
   - **csv / JSON / Markdown / 文本**：直接读取。
   - **docx**：使用 `python-docx` 提取段落和表格。
   - **图像**（.png/.jpg/...）：使用 `Read` 工具查看，然后决定图像是否包含数据（端点 URL 的表格、显示要捕获值的设置截图）或纯粹是说明性的（架构图、流程图）。仅从包含数据的图像中提取值。见 `references/source_format_handling.md` 中的图像处理规则。
   - 对于非常大的 SOP（>50 页 / >20 工作表），关注标题为“Post Refresh”、“Post-Copy”、“Post-Refresh Steps”、“Update …”或等效的章节或工作表。

2. **识别复制后操作**——读取 `references/sop_parsing_patterns.md` 以获取将文本指令（“更新 Outbound Message 端点 X 到 URL Y”）转换为结构化操作记录的启发式方法。

3. **将每个操作映射到 `ConfigurationName`**——加载 `references/configuration_catalog.md`。目录目前支持 `OutboundMessages`、`RemoteSiteSettings` 和 `ScheduledApex`。任何针对不同配置类型的操作都超出范围：跳过它并在响应中列出，以便用户以后扩展目录。

4. **读取 JSON 模板**——加载 `assets/config_template.json`。它显示了 `OutboundMessages` 条目、`RemoteSiteSettings` 条目和 `ScheduledApex` 条目的确切所需形状，带有 `<…>` 占位符槽。复制一个条目，将每个 `<…>` 槽替换为具体的 SOP 值，并保持确切的顶层键（`ConfigurationName`、`Label`、`Fields`、`IsActive`、`ExecutionOrder`）——永远不要将它们重命名为 `Type`、`Name`、`Operation` 等。永远不要发出仍然包含 `<…>` 占位符的条目；如果你无法填充一个槽，请跳过条目（见规则）。

5. **与模式验证**——加载 `assets/json_schema.json`。每个条目必须符合：`ConfigurationName` 是目录值之一，`Fields` 是对象，`IsActive` 是布尔值，`ExecutionOrder` 是正整数。

6. **按阶段分组条目，然后分配 `ExecutionOrder`**——`ExecutionOrder` 是阶段编号，不是每行计数器。可以并行运行的条目共享相同的值。不同的 `ConfigurationName` 类型通常获得不同的阶段；同一阶段内的所有条目共享其编号。见 `references/sop_parsing_patterns.md` 中的排序启发式方法。

7. **与示例比较**——在写入之前，验证输出形状是否与 `examples/sample_sop_to_config.json` 匹配。

8. **写入 JSON 文件**——发出格式化的 JSON（2 空格缩进）。

---

## 规则/约束

| 约束 | 理由 |
|-----------|-----------|
| 输出是顶层 JSON 数组（不是带有包装键的对象） | 复制后工具直接消耗数组 |
| 每个条目都有五个必需键：`ConfigurationName`、`Label`、`Fields`、`IsActive`、`ExecutionOrder` | 工具在缺少键时快速失败；不接受部分条目 |
| `ConfigurationName` 是目录值之一 | 未知值会导致运行时映射器出错——不要在不更新目录的情况下发明新类型 |
| `Fields` 键是目标元数据上的实际 API 字段名 | 错误的键名意味着工具在运行时无法定位字段 |
| `Fields` 值是来自 SOP 的具体值（字面 URL、名称等） | 复制后工具按原样应用值；占位符在运行时不会解析 |
| 如果 SOP 命名了操作但没有提供具体值（URL 等），**完全跳过该条目**并其在响应中列出 | 生成没有实际值的条目会产生静默无操作或运行时部署错误 |
| 每个发出的条目中的每个字段都必须是从客户的 SOP 或补充工作表中获取的真实值。永远不要发出 `""`、`null` 或 `<from-backup>` / `TBD` / `TODO` 等占位符 | 客户直接消费 JSON——空/占位符字段会作为错误输出显示给他们，并且在运行时也会失败 |
| 在跳过 OBM / RemoteSite 由于缺少值之前，**搜索提供的所有工作表/文件**中的端点表，该表以该名称为键 | 客户 SOP 经常将操作列表和 URL 表分布在不同的工作表上（例如，Michelin UAT 刷新规划器在集成选项卡中列出 OBMs，但 URL 表位于 Evolution SFA 选项卡中） |
| 另一个字段已经捕获的信息**不会**在 `Fields` 中重复（例如，`RemoteSiteName` 存在于 `Label`，`IsActive` 存在于顶层——两者都不属于 `Fields`） | 重复键使条目模糊并浪费工具必须协调的字节 |
| 对于 `OutboundMessages`，`Fields` 必须包含 `EndpointUrl` 和 `Object`（目标 SObject——`Account`、`Contact`、`Asset`、`Lead` 等） | 相同的 `Label` 可以应用于多个 OBMs，它们仅实体不同；`Object` 在运行时消除歧义 |
| 对于 `RemoteSiteSettings`，URL 键必须拼写为 `RemoteSiteUrl`——永远不是 `Url`、`RemoteSiteURL`、`SiteUrl` 或 `EndpointUrl` | 复制后工具按确切 API 名称匹配字段；任何其他拼写都意味着它无法定位字段并在运行时静默无操作 |
| `ExecutionOrder` 是阶段编号——没有依赖关系的条目共享相同的值 | 复制后工具并行运行具有相同 `ExecutionOrder` 的所有条目；只需要在操作依赖另一个操作时进行排序 |
| `IsActive: false` 条目保留在输出中（不要删除它们） | 客户按环境切换它们；删除会丢失可追溯性 |
| 当 SOP 将操作标记为必需时，默认 `IsActive` 为 `true` | 大多数 SOP 步骤是必需的；显式选择退出是例外 |

### 规范条目形状

见上方 STOP 部分中显示的条目形状，或直接从 `assets/config_template.json` 复制。不要将五个顶层键（`ConfigurationName`、`Label`、`Fields`、`IsActive`、`ExecutionOrder`）重命名为 `Type`、`Name`、`Operation`、`apiName` 等，也不要将数组包装在带有 `steps` / `actions` / `records` 键的对象中。

---

## 注意事项

| 问题 | 解决方案 |
|-------|------------|
| SOP 步骤说“删除所有端点”而不是“更新 X 到 Y” | 发出一个条目，`ConfigurationName: "OutboundMessages"`，`Label` 描述删除目标，并在 `Fields` 中添加注释（`{"Action": "Delete"}`）；目录记录了 Delete 模式 |
| 相同的 `Label` 出现在多个环境中（fcQA + fcUAT） | 每个环境发出一个条目；后缀 `Label` 或使用 SOP 中出现的特定环境 `Label` |
| 对于 OutboundMessages，相同的 `Label` 可以合法地应用于多个条目，每个条目针对不同的 `Object`（例如，一个 OBM 对 `Account`，一个对 `Contact`）。 | 不要合并它们——每个对象发出一个条目。`Object` 值（从 OBM 名称推断，如 `IR_Account_OBM_PROD` → `Account`）是区分它们的，不是 `Label`。 |
| SOP 在单个表中组合了许多自定义 `Label` | 每行一个条目——不要合并成一个批量条目 |
| 操作针对目录外的设置（CustomLabels、ConnectedApps、NamedCredentials、SSO、CustomSettings、等） | 跳过操作，不要发明新的 `ConfigurationName`；在响应中列出每个跳过的操作，以便用户知道以后要添加到目录的内容 |
| SOP 包含刷新前步骤与刷新后步骤交错 | 过滤掉刷新前——只有刷新后 / 复制后操作才属于输出 |
| SOP 命名要更新的 Outbound Message / Remote Site 但未包含新 URL | 跳过条目。在响应中列出跳过的项目，以便用户可以提供 URL 或修改 SOP |
| SOP 在 URL 中包含密钥（例如，`https://USER:TOKEN@host/...`） | 原样嵌入它们——工具按原样消费值——但在响应中标记，以便用户知道 JSON 现在包含密钥，应相应存储/共享 |
| 用户的 SOP 是非英语或格式化严重（表格、调用卡） | 首先提取文本，规范化空白，然后解析——格式化残留物不需要保留到 JSON 中 |
| SOP 包含截图/图像。有些是说明性的（架构图、流程图、“这是设置屏幕的样子”示例），有些是数据承载的（真实的 Outbound Messages 列表的截图、捕获的 Remote Site 表）。 | 将说明性图像视为超出范围——不要从中提取值。对于数据承载图像（周围的文本引用“显示在下面的值”/“如截图所示”/真实的端点 URL），进行 OCR 并使用这些值。见 `references/source_format_handling.md` 中的启发式方法。 |
| SOP 作为多个文件提供（例如，PDF + 伴奏 xlsx + 截图文件夹），或值分布在选项卡/页面之间 | 在跳过任何条目前，读取所有提供的文件。操作列表和 URL 表通常位于不同的文件中——见上述关于多工作表来源的规则。 |

---

## 输出预期

交付物：
- 一个 JSON 文件（默认 `post-copy-config.json`），包含顶层复制后操作条目数组。
- 响应中的简短摘要：总条目数、每个 `ConfigurationName` 的计数、未映射到目录的操作、SOP 未包含具体值的操作。

输出文件结构符合 `assets/json_schema.json`。

---

## 跨技能集成

| 需要 | 委托给 |
|------|-------------|
| 生成实际的 Salesforce 元数据 XML（Custom Label / Named Credential / Remote Site / 等） | 匹配的 `generating-*` 技能 |
| 部署生成的元数据或运行复制后工具针对组织 | `deploying-metadata` 技能 |
| 将 SOP 与 UDD 中定义的实体进行比较 | `udd:research-entities` |

---

## 参考文件索引

| 文件 | 何时读取 |
|------|-------------|
| `assets/config_template.json` | 步骤 4——JSON 输出的起始结构 |
| `assets/json_schema.json` | 步骤 5——验证每个发出的条目 |
| `references/configuration_catalog.md` | 步骤 3——将 SOP 操作映射到 `ConfigurationName` 并获取规范字段键 |
| `references/sop_parsing_patterns.md` | 步骤 2 和步骤 6——从文本中提取操作的启发式方法以及排序 |
| `references/source_format_handling.md` | 步骤 1——每种输入格式（PDF / xlsx / csv / JSON / docx / 图像）的确切提取配方和数据承载与说明性图像的启发式方法 |
| `examples/sample_sop_to_config.json` | 步骤 7——验证输出形状是否与预期格式匹配 |
| `examples/sample_sop_excerpt.md` | 步骤 7——见一个产生了样本 JSON 的代表性 SOP 摘录 |
