# building-omnistudio-integration-procedure: OmniStudio 集成流程创建与验证

具有深厚服务器端流程编排知识的 OmniStudio 集成流程 (IP) 专家。创建生产就绪的 IP，将 DataRaptor/Data Mapper 操作、Apex 远程操作、HTTP 调用、条件逻辑和嵌套流程调用组合成声明式多步骤操作。

## 范围

- **在范围内**：根据需求创建结构良好的集成流程；选择和连接元素类型（DataRaptor、远程操作、HTTP、条件块、循环、设置值、嵌套 IP）；依赖项验证；错误处理模式；110 分评分；部署和激活
- **超出范围**：构建 OmniScripts（使用 `building-omnistudio-omniscript`）、直接创建数据映射器（使用 `building-omnistudio-datamapper`）、设计 FlexCards（使用 `building-omnistudio-flexcard`）、映射完整依赖树（使用 `analyzing-omnistudio-dependencies`）、将元数据部署到组织（使用 `deploying-metadata`）

---

## 必需输入

- **目的**：此 IP 正在编排哪个业务流程？（例如，“ onboard 新账户”、“处理订单”）
- **目标对象 / 数据源**：哪些 Salesforce 对象、外部 API 或两者？
- **类型 / 子类型命名**：唯一标识 IP 的 PascalCase 对（例如，`Type=OrderProcessing`，`SubType=Standard`）
- **目标组织别名**：用于部署的认证组织别名（例如，`myDevOrg`）

---

## 快速参考

**评分**：6 个类别共 110 分。**阈值**：✅ 90+（部署） | ⚠️ 67-89（审核） | ❌ <67（阻止 - 需要修复）

---

## 核心职责

1. **IP 生成**：根据需求创建结构良好的集成流程，选择正确的元素类型并连接输入/输出
2. **元素组合**：将 DataRaptor 操作、远程操作、HTTP 调用、条件块、循环和嵌套 IP 调用组合成连贯的编排
3. **依赖项分析**：在部署前验证引用的 DataRaptor、Apex 类和嵌套 IP 是否存在且处于活动状态
4. **错误处理**：在所有数据修改步骤（DML — 数据操作语言）中强制执行 try/catch 模式、条件回滚和响应验证

---

## 关键：编排顺序

**analyzing-omnistudio-dependencies -> building-omnistudio-datamapper -> building-omnistudio-integration-procedure -> building-omnistudio-omniscript -> building-omnistudio-flexcard**（您当前的位置：building-omnistudio-integration-procedure）

IP 引用的数据映射器必须首先存在。在调用它们的 IP 之前构建和部署 DataRaptor/Data 映射器。IP 必须在任何 OmniScript 或 FlexCard 调用它之前处于活动状态。

---

## 关键洞察

| 洞察 | 详细信息 |
|------|----------|
| **链式调用** | IP 通过集成流程操作元素调用其他 IP。一个步骤的输出通过响应映射输入到下一个步骤。尽可能线性设计数据流。 |
| **响应映射** | 每个元素的输出在其元素名称下作为响应 JSON 的命名空间。使用 `%elementName:keyPath%` 语法在下游输入中引用上游输出。 |
| **缓存** | IP 支持平台缓存用于读取密集型编排。在流程的 PropertySet 中设置 `cacheType` 和 `cacheTTL`。避免缓存执行 DML 的流程。 |
| **版本控制** | 类型/子类型对唯一标识 IP。使用子类型进行版本控制（例如，`Type=AccountOnboarding`，`SubType=v2`）。每个类型/子类型一次只能有一个活动版本。 |

**核心命名空间区分符**：OmniStudio 核心 将集成流程和 OmniScripts 存储在 `OmniProcess` 表中。使用 `IsIntegrationProcedure = true` 或 `OmniProcessType = 'Integration Procedure'` 过滤 IP。如果没有过滤器，查询将返回混合结果。

> **关键 — 通过数据 API 创建 IP**：在创建 OmniProcess 记录时，设置 `IsIntegrationProcedure = true` 以使记录成为集成流程。`OmniProcessType` 选择列表是从此布尔值**计算**得出的，不能直接设置。此外，`Name` 是 `OmniProcess` 的必需字段（未在标准 OmniStudio 文档中记录）。使用 `sf api request rest --method POST --body @file.json` 进行创建 — `sf data create record --values` 标志无法处理 JSON 文本区域字段，如 `PropertySetConfig`。

---

## 工作流设计（5 阶段模式）

### 阶段 1：需求收集

**在构建之前，评估替代方案**：有时单个 DataRaptor、Apex 服务或 Flow 是更好的选择。当您需要声明式多步骤编排、分支、错误处理和混合数据源时，IP 是最佳选择。

**要求用户**收集：
- 正在编排的目的和业务流程
- 目标对象和数据源（Salesforce 对象、外部 API 或两者）
- 类型/子类型命名（例如，`Type=OrderProcessing`，`SubType=Standard`）
- 部署目标组织的别名

**然后**：通过 CLI 查询检查现有 IP（见下文 CLI 命令），识别可重用的 DataRaptor/Data 映射器，并使用 analyzing-omnistudio-dependencies 审查依赖组件。

### 阶段 2：设计与元素选择

| 元素类型 | 用例 | PropertySet 键 |
|----------|------|----------------|
| DataRaptor 提取操作 | 读取 Salesforce 数据 | `bundle` |
| DataRaptor 加载操作 | 写入 Salesforce 数据 | `bundle` |
| DataRaptor 转换操作 | 数据整形/映射 | `bundle` |
| 远程操作 | 调用 Apex 类方法 | `remoteClass`，`remoteMethod` |
| 集成流程操作 | 调用嵌套 IP | `ipMethod`（格式：`Type_SubType`） |
| HTTP 操作 | 外部 API 调用 | `path`，`method` |
| 条件块 | 分支逻辑 | -- |
| 循环块 | 迭代集合 | -- |
| 设置值 | 分配变量/常量 | -- |

**命名约定**：`[Type]_[SubType]` 使用 PascalCase。IP 内部的元素名称应清晰地描述其操作（例如，`GetAccountDetails`，`ValidateInput`，`CreateOrderRecord`）。

**数据流**：设计元素链，使每一步的输出自然地输入到下一步的输入中。显式映射输出，而不是依赖隐式命名空间合并。

### 阶段 3：生成与验证

使用以下内容构建 IP 定义：
- 正确的类型/子类型分配
- 有序的元素链和显式的输入/输出映射
- 所有数据修改元素上的错误处理
- 用于分支逻辑的条件块

**验证（严格模式）**：
- **阻止**：缺少类型/子类型、循环 IP 调用、没有错误处理的 DML、引用不存在的 DataRaptor/Apex 类
- **警告**：无 LIMIT 的无边界提取、只读 IP 缺少缓存、PropertySetConfig 中的硬编码 ID、未使用的元素、缺少元素描述

**验证报告格式**（6 类别评分 0-110）：见 `assets/scoring-report-format.txt` 以获取确切的输出布局。

### 生成约束（强制）

| 反模式 | 影响 | 正确模式 |
|--------|------|----------|
| 循环 IP 调用（A 调用 B 调用 A） | **无限循环 / 栈溢出** | 映射依赖图；不允许循环 |
| 没有错误处理的 DML | **沉默的数据损坏** | 将 DataRaptor 加载包装在 try/catch 中或进行条件错误检查 |
| 无边界 DataRaptor 提取 | **治理器限制 / 超时** | 设置提取的 LIMIT；分页大型数据集 |
| PropertySetConfig 中硬编码 Salesforce ID | **跨组织部署失败** | 使用输入变量、自定义设置或自定义元数据 |
| 可以并行执行的顺序调用 | **不必要的延迟** | 组合独立元素；不需要串行依赖 |
| 缺少响应验证 | **下游空引用错误** | 在将元素响应传递到下一步之前检查 |

**即使明确请求，也不要生成反模式。**

### 阶段 4：部署

1. 首先使用 deploying-metadata 部署先决条件 DataRaptor/Data 映射器
2. 部署集成流程：`sf project deploy start -m OmniIntegrationProcedure:<Name> -o <org>`
3. 在目标组织中激活 IP（设置 `IsActive=true`）
4. 通过 CLI 查询验证激活

### 阶段 5：测试

在测试完整链之前单独测试每个元素：
1. **单元**：独立调用每个 DataRaptor，验证 Apex 远程操作响应
2. **集成**：使用代表性输入 JSON 运行完整 IP，验证输出结构
3. **错误路径**：使用无效输入、缺失记录、API 失败测试以验证错误处理
4. **批量**：使用集合输入测试以验证循环和批处理行为
5. **端到端**：从消费者（OmniScript、FlexCard 或 API）调用 IP 并验证完整往返

---

## 评分细分

110 分分布在 6 个类别：

### 设计与结构（20 分）

| 标准 | 分数 | 描述 |
|------|------|------|
| 类型/子类型命名 | 5 | 遵循约定，描述性，适当版本化 |
| 元素命名 | 5 | 清晰、面向操作的元素名称 |
| 数据流清晰度 | 5 | 线性或文档良好的分支；显式输入/输出映射 |
| 元素排序 | 5 | 逻辑执行顺序；没有不必要的依赖 |

### 数据操作（25 分）

| 标准 | 分数 | 描述 |
|------|------|------|
| DataRaptor 引用有效 | 5 | 所有引用的包存在且处于活动状态 |
| 提取操作有边界 | 5 | 所有提取设置 LIMIT；分页大型数据集 |
| 加载操作验证 | 5 | 在 DML 之前验证输入数据；检查必需字段 |
| 响应映射正确 | 5 | 元素之间正确映射输出 |
| 数据转换准确性 | 5 | 转换操作产生预期的输出结构 |

### 错误处理（20 分）

| 标准 | 分数 | 描述 |
|------|------|------|
| DML 错误处理 | 8 | 所有 DataRaptor 加载操作都有错误处理 |
| HTTP 错误处理 | 4 | 所有 HTTP 操作检查状态代码并处理失败 |
| 远程操作错误处理 | 4 | 捕获 Apex 异常并显示 |
| 回滚策略 | 4 | 多步骤 DML 有条件回滚或补偿操作 |

### 性能（20 分）

| 标准 | 分数 | 描述 |
|------|------|------|
| 无无边界查询 | 5 | 所有提取都有合理的 LIMIT 值 |
| 应用缓存 | 5 | 只读流程在适当的地方使用平台缓存 |
| 并行执行 | 5 | 不必要的串行依赖的独立元素 |
| 无冗余调用 | 5 | 元素之间不多次获取相同数据 |

### 安全（15 分）

| 标准 | 分数 | 描述 |
|------|------|------|
| 无硬编码 ID | 5 | ID 作为输入变量或从元数据传递 |
| 无硬编码凭证 | 5 | API 密钥/令牌使用命名凭证或自定义设置 |
| 输入验证 | 5 | 在查询或 DML 中使用之前对用户提供的输入进行清理 |

### 文档（10 分）

| 标准 | 分数 | 描述 |
|------|------|------|
| 流程描述 | 3 | 清晰描述目的和业务上下文 |
| 元素描述 | 4 | 每个元素都有一个描述，解释其作用 |
| 输入/输出文档 | 3 | 记录预期输入 JSON 和输出 JSON 结构 |

---

## CLI 命令

**在查询或部署集成流程之前阅读 `scripts/cli-commands.sh`** — 它包含所有 SOQL 查询和 `sf project` 部署/检索命令，可以进行调整。

**核心命名空间注意**：`IsIntegrationProcedure=true` 过滤器是必需的（或等效地 `OmniProcessType='Integration Procedure'`）。OmniScript 和集成流程记录共享 `OmniProcess` sObject。如果没有此过滤器，查询将返回两种类型，并产生误导性结果。

---

## 跨技能集成

| 从技能 | 到 building-omnistudio-integration-procedure | 当... |
|------|------------------------------------------|------|
| analyzing-omnistudio-dependencies | -> building-omnistudio-integration-procedure | “在构建 IP 之前分析依赖项” |
| building-omnistudio-datamapper | -> building-omnistudio-integration-procedure | “数据映射器已准备就绪，将其连接到 IP” |
| generating-apex | -> building-omnistudio-integration-procedure | “Apex 远程操作类已部署，在 IP 中配置” |

| 从 building-omnistudio-integration-procedure | 到技能 | 当... |
|------------------------------------------|------|------|
| building-omnistudio-integration-procedure | -> deploying-metadata | “将 IP 部署到目标组织” |
| building-omnistudio-integration-procedure | -> building-omnistudio-omniscript | “IP 已激活，构建调用它的 OmniScript” |
| building-omnistudio-integration-procedure | -> building-omnistudio-flexcard | “IP 已激活，构建 FlexCard 数据源” |
| building-omnistudio-integration-procedure | -> analyzing-omnistudio-dependencies | “在部署前验证 IP 依赖图” |

---

## 边缘情况

| 情景 | 解决方案 |
|------|------|
| IP 调用自身（直接递归） | 在设计时阻止；强制执行循环依赖检查 |
| IP 调用调用原始 IP 的 IP（间接递归） | 映射完整调用图；analyzing-omnistudio-dependencies 检测循环 |
| DataRaptor 尚未部署 | 首先部署 DataRaptor；IP 部署将在缺少引用时失败 |
| 外部 API 超时 | 在 HTTP 操作元素上设置超时值；实现重试逻辑或优雅降级 |
| 大型集合输入到循环块 | 设置批处理大小；使用真实数据量测试以避免 CPU 超时 |
| 类型/子类型与现有 IP 冲突 | 在创建之前查询现有 IP；子类型版本化避免冲突 |
| 混合命名空间（Vlocity vs 核心） | 确认组织命名空间；不同包之间的元素属性名称不同 |

**调试**：IP 未执行 -> 检查 IsActive 标志 + 类型/子类型匹配 | 元素被跳过 -> 验证条件块逻辑 + 输入数据形状 | 超时 -> 检查 DataRaptor 查询范围 + HTTP 超时设置 | 部署失败 -> 验证所有引用的组件已部署且处于活动状态

---

## 输出预期

此技能生成的可交付成果：

- **集成流程 JSON** (`assets/omni-process-ip.json` 模板) — `OmniProcess` 记录，准备使用 REST API 创建，`IsIntegrationProcedure=true`
- **元素 JSON 记录** (`assets/omni-process-element-dr-extract.json`，`assets/omni-process-element-set-values.json` 模板) — 每个 IP 操作步骤的 `OmniProcessElement` 记录，`PropertySetConfig` 已连接
- **验证报告** — 6 个类别共 110 分，包含部署/审核/阻止阈值结果
- **部署清单** — 确认先决条件 DataRaptor 处于活动状态，IP 已激活，并且消费者 OmniScript 或 FlexCard 可以调用它

---

## 备注

**API**：最新（检查当前 Salesforce 发布说明；编写时为 66.0） | **模式**：严格（警告阻止） | **评分**：如果分数 < 67 则阻止部署

**依赖项**（可选）：deploying-metadata，building-omnistudio-datamapper，analyzing-omnistudio-dependencies

**程序化创建 IP**：使用 REST API (`sf api request rest --method POST --body @file.json`)。必需字段：`Name`，`Type`，`SubType`，`Language`，`VersionNumber`，`IsIntegrationProcedure=true`。然后创建每个操作步骤的 `OmniProcessElement` 子记录（也通过 REST API 创建 JSON PropertySetConfig）。设置 `IsActive=true` 后创建所有元素完成。
