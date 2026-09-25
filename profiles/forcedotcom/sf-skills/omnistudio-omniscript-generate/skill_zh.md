# omnistudio-omniscript-generate：OmniStudio OmniScript 创建与验证

用于声明式、分步引导式数字体验的专家级 OmniScript 构建器。OmniScript 是 OmniStudio 中 Screen Flow 的类似物：多步骤、交互式流程，用于收集输入、编排服务器端逻辑（集成程序、DataRaptor），并将结果呈现给用户——所有这些都不需要代码。

## 快速参考

**评分**：跨越 6 个类别的 120 分。**阈值**：[通过] 90+（部署） | [审核] 67-89（审核） | [阻止] <67（阻止 - 需要修复）

---

## 范围

- **在范围内**：根据需求创建 OmniScript、元素选择和 PropertySetConfig 设计、依赖分析（集成程序、DataRaptor）、数据流跟踪、120 分验证评分、部署和激活
- **超出范围**：构建 FlexCard（使用 `omnistudio-flexcard-generate`）、直接创建集成程序（使用 `omnistudio-integration-procedure-generate`）、映射完整依赖树（使用 `omnistudio-dependencies-analyze`）、将元数据部署到组织（使用 `platform-metadata-deploy`）

---

## 必需输入

构建前收集这些信息：

| 输入 | 描述 | 默认值 |
|-------|-------------|---------|
| **类型** | 流程类别（例如，`ServiceRequest`、`Enrollment`） | 无 — 必需 |
| **子类型** | 具体变体（例如，`NewCase`、`UpdateAddress`） | 无 — 必需 |
| **语言** | OmniScript 的区域设置 | `English` |
| **目的** | 该 OmniScript 引导的业务流程 | 无 — 必需 |
| **目标组织** | 部署的组织别名 | 当前默认组织 |
| **数据源** | 需要查询或更新的对象/API | 从需求中识别 |

---

## 核心职责

1. **OmniScript 生成**：根据需求创建结构良好的 OmniScript，为每个步骤选择适当的元素类型
2. **元素设计**：为每个元素配置 PropertySetConfig JSON，确保正确的数据绑定、验证和条件逻辑
3. **依赖分析**：在部署前映射所有对集成程序、DataRaptor 和嵌入式 OmniScript 的引用
4. **数据流分析**：通过 OmniScript JSON 结构跟踪数据——从预填充通过用户输入到最终保存操作

---

## 关键提示：编排顺序

**omnistudio-dependencies-analyze → omnistudio-datamapper-generate → omnistudio-integration-procedure-generate → omnistudio-omniscript-generate → omnistudio-flexcard-generate**（您当前所在位置：omnistudio-omniscript-generate）

OmniScript 消费集成程序和 DataRaptor。首先构建这些。FlexCard 可能会启动 OmniScript——在构建 FlexCard 之后构建。使用 omnistudio-dependencies-analyze 在开始之前映射完整依赖树。

---

## 关键洞察

| 洞察 | 详细信息 |
|---------|---------|
| **类型/子类型/语言三元组** | 唯一标识 OmniScript。所有三个值都是必需的，并形成复合键。示例：类型=`ServiceRequest`，子类型=`NewCase`，语言=`English` |
| **PropertySetConfig** | 包含所有元素配置的 JSON 对象——布局、数据绑定、验证规则、条件可见性。这是实际逻辑所在的地方 |
| **核心命名空间** | OmniProcess，其中 `IsIntegrationProcedure = false`（等效于 `OmniProcessType='OmniScript'`）。元素是子 OmniProcessElement 记录 |
| **元素层次结构** | 元素使用 Level/Order 字段构建树结构。Level 0 = 步骤，Level 1+ = 步骤内的元素。Order 决定同一级别内的顺序 |
| **版本管理** | 可以存在多个版本；每个类型/子类型/语言三元组只有一个可以激活。通过 `IsActive` 字段激活 |
| **数据 JSON** | OmniScript 通过所有步骤传递单个 JSON 数据结构。元素通过合并字段语法从该共享 JSON 中读取和写入 |

---

## 工作流设计（5 阶段模式）

### 阶段 1：需求收集

**构建前，评估替代方案**：OmniScript 适用于复杂、多步骤引导式流程。对于简单的单屏数据输入，请考虑 Screen Flow。对于无交互的数据显示，请考虑 FlexCard。

**要求用户收集**：
- **类型**：流程类别（例如，`ServiceRequest`、`Enrollment`、`ClaimSubmission`）
- **子类型**：具体变体（例如，`NewCase`、`UpdateAddress`、`FileAppeal`）
- **语言**：通常为 `English`，除非需要多语言支持
- **目的**：该 OmniScript 引导的业务流程
- **目标组织**：部署的组织别名
- **数据源**：需要查询或更新的对象/API

**然后**：检查现有 OmniScript 以避免重复，识别可重用的集成程序或 DataRaptor，并映射依赖链。

### 阶段 2：设计与元素选择

设计每个步骤并选择适合交互模式的元素类型。

#### 容器元素

| 元素类型 | 目的 | 关键配置 |
|-------------|---------|------------|
| **步骤** | 顶级容器，用于一组 UI 元素；每个步骤是向导中的页面 | `chartLabel`、`knowledgeOptions`、`show`（条件可见性） |
| **条件块** | 根据条件显示/隐藏一组元素 | `conditionType`、`show` 表达式 |
| **循环块** | 遍历数据列表并为每个项目渲染元素 | `loopData`（JSON 路径到数组） |
| **编辑块** | 表格数据的行内编辑容器 | `editFields`、`dataSource` |

#### 输入元素

| 元素类型 | 目的 | 关键配置 |
|-------------|---------|------------|
| **文本** | 单行文本输入 | `label`、`placeholder`、`pattern`（正则表达式验证） |
| **文本区域** | 多行文本输入 | `label`、`maxLength`、`rows` |
| **数字** | 带可选格式的数字输入 | `label`、`min`、`max`、`step`、`format` |
| **日期** | 日期选择器 | `label`、`dateFormat`、`minDate`、`maxDate` |
| **日期/时间** | 日期和时间选择器 | `label`、`dateFormat`、`timeFormat` |
| **复选框** | 布尔切换 | `label`、`defaultValue` |
| **单选按钮** | 单选按钮组 | `label`、`options`（静态或数据驱动） |
| **下拉选择** | 下拉选择 | `label`、`options`、`optionSource`（静态/数据） |
| **多选** | 多项选择 | `label`、`options`、`maxSelections` |
| **类型前缀** | 搜索/自动完成输入 | `label`、`dataSource`、`searchField`、`minCharacters` |
| **签名** | 签名捕获垫 | `label`、`penColor`、`backgroundColor` |
| **文件** | 文件上传 | `label`、`maxFileSize`、`allowedExtensions` |
| **货币** | 带区域设置格式的货币输入 | `label`、`currencyCode`、`min`、`max` |
| **电子邮件** | 带格式验证的电子邮件输入 | `label`、`placeholder` |
| **电话** | 带掩码的电话号码输入 | `label`、`mask`、`placeholder` |
| **URL** | 带格式验证的 URL 输入 | `label`、`placeholder` |
| **密码** | 掩码文本输入 | `label`、`minLength` |
| **范围** | 滑块输入 | `label`、`min`、`max`、`step` |
| **时间** | 时间选择器 | `label`、`timeFormat` |

#### 显示元素

| 元素类型 | 目的 | 关键配置 |
|-------------|---------|------------|
| **文本块** | 静态内容显示（支持 HTML） | `textContent`、`HTMLTemplateId` |
| **标题** | 区域标题 | `text`、`level`（h1-h6） |
| **聚合** | 计算摘要显示 | `aggregateExpression`、`format` |
| **披露** | 可展开/可折叠内容 | `label`、`defaultExpanded` |
| **图像** | 图像显示 | `imageURL`、`altText` |
| **图表** | 数据可视化 | `chartType`、`dataSource` |

#### 操作元素

| 元素类型 | 目的 | 关键配置 |
|-------------|---------|------------|
| **DataRaptor 提取操作** | 从 Salesforce 拉取数据 | `bundle`、`inputMap`、`outputMap` |
| **DataRaptor 加载操作** | 将数据推送到 Salesforce | `bundle`、`inputMap` |
| **集成程序操作** | 调用服务器端集成程序 | `ipMethod`（Type_SubType）、`inputMap`、`outputMap`、`remoteOptions` |
| **远程操作** | 调用 Apex @RemoteAction 或 REST | `remoteClass`、`remoteMethod`、`inputMap` |
| **导航操作** | 页面导航或重定向 | `targetType`、`targetId`、`URL` |
| **DocuSign 信封操作** | 触发 DocuSign 信封 | `templateId`、`recipientMap` |
| **电子邮件操作** | 发送电子邮件 | `emailTemplateId`、`recipientMap` |

#### 逻辑元素

| 元素类型 | 目的 | 关键配置 |
|-------------|---------|------------|
| **设置值** | 变量赋值和数据转换 | `elementValueMap`（键值对） |
| **验证** | 输入验证规则和自定义消息 | `validationFormula`、`errorMessage` |
| **公式** | 使用公式表达式计算值 | `expression`、`dataType` |
| **提交操作** | 收集数据的最终提交 | `postMessage`、`preTransformBundle`、`postTransformBundle` |

### 阶段 3：生成与验证

运行 `scripts/check-duplicate-omniscript.sh <Type> <SubType> <Language> <org>` 以验证是否存在重复的类型/子类型/语言。

**构建 OmniScript**：
1. 创建 OmniProcess 记录，包含类型、子类型、语言和 OmniProcessType='OmniScript'
2. 为每个步骤（Level=0）创建 OmniProcessElement 子记录
3. 为步骤内的每个元素（Level=1+）创建 OmniProcessElement 子记录（按 Order 字段排序）
4. 为每个元素配置 PropertySetConfig JSON
5. 将操作元素连接到其集成程序 / DataRaptor

**验证（严格模式）**：
- **阻止**：缺少类型/子类型/语言、循环 OmniScript 嵌入、损坏的 IP/DataRaptor 引用、缺少必需的 PropertySetConfig 字段
- **警告**：没有元素的步骤、没有验证的输入元素、操作上缺少错误处理、未使用的数据路径、元素嵌套过深（>4 级）

**验证报告格式**（6 类别评分 0-120）：
```yaml
分数：102/120 ---- 很好
-- 设计与结构：22/25 (88%)
-- 数据集成：18/20 (90%)
-- 错误处理：17/20 (85%)
-- 性能：18/20 (90%)
-- 用户体验：17/20 (85%)
-- 安全：10/15 (67%)
```

### 阶段 4：部署

1. **先决条件**：验证组织认证（`sf org display -o <org>`）。确认所有引用的 DataRaptor 和集成程序在目标组织中都是活动的。
2. 首先部署所有依赖项：DataRaptor、集成程序、引用的 OmniScript。
3. 运行 `scripts/deploy-omniscript.sh <Name> <Type> <SubType> <org>`——这将部署 OmniScript 并验证激活。如果部署失败，脚本将输出恢复说明（停用并删除部分记录，然后重试）。
4. 如果部署成功，则激活 OmniScript 版本（如果未自动激活）。

### 阶段 5：测试

使用各种数据场景走遍所有路径：
- **成功路径**：使用有效数据完成所有步骤，验证提交
- **验证测试**：在每个输入处提交无效数据，验证错误消息
- **条件测试**：执行所有条件块并验证显示/隐藏逻辑
- **数据预填充**：验证 DataRaptor 提取操作是否正确填充元素
- **稍后保存**：测试恢复功能（如果启用）
- **导航**：测试跨所有步骤的回退/前进/取消行为
- **错误场景**：模拟 IP/DataRaptor 失败，验证错误处理
- **嵌入式 OmniScript**：测试父 OmniScript 和子 OmniScript 之间的数据传递
- **批量数据**：使用 Loop Block 和 Type Ahead 元素中的大型数据集测试

---

## 规则 / 限制

| 反模式 | 影响 | 正确模式 |
|--------------|--------|-----------------|
| 循环 OmniScript 嵌入 | **无限渲染循环** | 映射依赖树；如果 B 嵌入 A，则永不嵌入 A 在 B 中 |
| 无限 DataRaptor 提取 | **性能下降** | 添加过滤条件；限制返回记录 |
| 缺少输入验证 | **不良数据输入** | 添加验证元素或 `pattern`/`required` 在输入上 |
| 硬编码 Salesforce ID | **跨组织部署失败** | 使用合并字段或 Custom Settings/Metadata |
| 集成程序（IP）操作缺少错误处理 | **静默失败** | 在 PropertySetConfig 中配置 `showError`、`errorMessage` |
| Text Block 中的大型图像 | **页面加载缓慢** | 使用 Image 元素并优化 URL |
| 每个步骤元素过多 | **用户体验差** | 每个步骤限制为 7-10 个输入元素 |
| 缺少条件可见性 | **显示不相关的字段** | 使用 `show` 表达式隐藏不相关的元素 |

即使明确请求，也不要生成反模式。

---

## 评分：跨越 6 类别 120 分

### 设计与结构（25 分）

| 检查 | 分数 | 标准 |
|-------|--------|----------|
| 类型/子类型/语言设置正确 | 5 | 所有三个字段填充有意义的值 |
| 步骤组织 | 5 | 逻辑分组，每个步骤最多 7-10 个元素 |
| 元素命名 | 5 | 描述性名称遵循 `PascalCase` 惯例 |
| 条件逻辑 | 5 | 正确使用条件块和 `show` 表达式 |
| 版本管理 | 5 | 干净的版本历史记录，只有一个激活版本 |

### 数据集成（20 分）

| 检查 | 分数 | 标准 |
|-------|--------|----------|
| DataRaptor 引用有效 | 5 | 所有 Extract/Load bundles 存在且处于活动状态 |
| 集成程序引用有效 | 5 | 所有 IP 操作引用激活的 IP |
| 输入/输出映射正确 | 5 | 数据在元素和操作之间正确流动 |
| 数据预填充配置 | 5 | 初始数据在用户交互之前加载 |

### 错误处理（20 分）

| 检查 | 分数 | 标准 |
|-------|--------|----------|
| 操作元素具有错误处理 | 5 | 所有 IP/DR 操作配置了 `showError` |
| 用户友好的错误消息 | 5 | 清晰、可操作的错误文本 |
| 必需输入的验证 | 5 | 所有必需字段都有验证规则 |
| 定义回退行为 | 5 | 当数据源返回空时优雅地处理 |

### 性能（20 分）

| 检查 | 分数 | 标准 |
|-------|--------|----------|
| 无无界数据获取 | 5 | 所有 DataRaptor 提取都有过滤器/限制 |
| 配置了惰性加载 | 5 | 操作元素在步骤进入时触发，而不是 OmniScript 加载时 |
| 每个步骤的元素数量合理 | 5 | 没有步骤包含 >15 个元素 |
| 使用条件渲染 | 5 | 当元素不适用时隐藏元素（不仅仅是不可见） |

### 用户体验（20 分）

| 检查 | 分数 | 标准 |
|-------|--------|----------|
| 逻辑步骤流程 | 5 | 步骤遵循自然的任务进展 |
| 输入标签和帮助文本 | 5 | 所有输入都有清晰的标签和上下文帮助 |
| 导航控件 | 5 | 适当配置回退、下一步、取消、稍后保存 |
| 响应式布局 | 5 | 元素配置为支持移动设备和桌面断点 |

### 安全（15 分）

| 检查 | 分数 | 标准 |
|-------|--------|----------|
| 客户端 JSON 中无敏感数据 | 5 | 密码、SSN、令牌保存在服务器端 |
| IP 操作使用服务器端处理 | 5 | 敏感逻辑在集成程序中，而不是客户端 OmniScript |
| 尊重字段级访问权限 | 5 | 数据访问匹配用户配置文件/权限集 |

---

## CLI 命令

有关完整命令参考，请参阅 `scripts/cli-reference.sh`。常用命令：

```bash
# 列出激活的 OmniScript
sf data query -q "SELECT Id,Name,Type,SubType,Language,IsActive,VersionNumber FROM OmniProcess WHERE IsActive=true AND OmniProcessType='OmniScript' LIMIT 50" -o <org>

# 查询特定 OmniScript 的元素
sf data query -q "SELECT Id,Name,ElementType,Level,Order FROM OmniProcessElement WHERE OmniProcessId='<id>' ORDER BY Level,Order LIMIT 200" -o <org>

# 检查 OmniScript 版本
sf data query -q "SELECT Id,VersionNumber,IsActive,LastModifiedDate FROM OmniProcess WHERE Type='<Type>' AND SubType='<SubType>' AND OmniProcessType='OmniScript' ORDER BY VersionNumber DESC LIMIT 10" -o <org>
```

---

## 跨技能集成

| 从技能 | 到 omnistudio-omniscript-generate | 当...时 |
|------------|------------------|------|
| omnistudio-dependencies-analyze | -> omnistudio-omniscript-generate | "在构建 OmniScript 之前分析依赖项" |
| omnistudio-datamapper-generate | -> omnistudio-omniscript-generate | "DataRaptor 准备就绪，构建使用它的 OmniScript" |
| omnistudio-integration-procedure-generate | -> omnistudio-omniscript-generate | "IP 准备就绪，将其连接到 OmniScript 操作" |

| 从 omnistudio-omniscript-generate | 到技能 | 当...时 |
|--------------------|----------|------|
| omnistudio-omniscript-generate | -> omnistudio-flexcard-generate | "构建启动此 OmniScript 的 FlexCard" |
| omnistudio-omniscript-generate | -> platform-metadata-deploy | "将 OmniScript 部署到目标组织" |
| omnistudio-omniscript-generate | -> omnistudio-dependencies-analyze | "在部署前映射完整依赖树" |
| omnistudio-omniscript-generate | -> omnistudio-integration-procedure-generate | "此 OmniScript 操作需要新的 IP" |
| omnistudio-omniscript-generate | -> omnistudio-datamapper-generate | "为数据预填充需要 DataRaptor" |

---

## 注意事项

| 问题 | 解决方案 |
|-------|-----------|
| 多语言 OmniScript | 为每个语言创建单独的版本，具有共享的类型/子类型；使用翻译工作台翻译标签 |
| 嵌入式 OmniScript 数据传递 | 通过 `prefillJSON` 将父数据 JSON 键映射到子 OmniScript 输入；测试数据往返 |
| 大型 Loop Block 数据集 | 分页或限制 DataRaptor 结果；考虑在集成程序（IP）中实现服务器端过滤 |
| FlexCard 飞出中的 OmniScript | 确保 FlexCard 传递所需的上下文数据；测试飞出尺寸 |
| 社区/体验云部署 | 验证 OmniScript 组件在体验构建器中可用；检查访客用户权限 |
| 保存和恢复（稍后保存） | 配置 `saveNameTemplate`、`saveExpireInDays`；测试使用部分数据的恢复 |
| 版本冲突 | 激活旧版本之前停用新版本；对于相同类型/子类型/语言三元组，永远不要有两个激活版本 |
| OmniScript 中的自定义 LWC | 将 LWC 注册为 OmniScript 兼容；遵循 `omniscript-lwc` 命名空间惯例 |
| 命名空间组织 | 如果部署到受管理的 OmniStudio 软件包组织，请将捆绑名称和 API 名称以相应的命名空间为前缀（例如，`omnistudio__`） |
| `OmniProcessType` 在创建时不能设置 | `OmniProcessType` 是根据 `IsIntegrationProcedure`（对于 OmniScript 为 false）计算的；不要直接设置它 |

对于常见的运行时故障排除（元素未渲染、数据未预填充、IP 操作静默失败），请参阅 `references/best-practices.md` 第 8 节。

---

## 备注

**API**：66.0 | **模式**：严格（警告阻止） | **评分**：分数低于 67 则阻止部署

**必需的上游技能**：`omnistudio-datamapper-generate`、`omnistudio-integration-procedure-generate`

**可选技能**：`platform-metadata-deploy`、`omnistudio-flexcard-generate`、`omnistudio-dependencies-analyze`

**以编程方式创建 OmniScript**：使用 REST API (`sf api request rest --method POST --body @file.json`)。必需字段：`Name`、`Type`、`SubType`、`Language`、`VersionNumber`。OmniScript 默认为 `IsIntegrationProcedure=false`——不要直接设置 `OmniProcessType`（它会被计算）。`sf data create record --values` 标志无法处理像 `PropertySetConfig` 这样的 JSON 文本区域字段。通过 REST API 创建子 `OmniProcessElement` 记录以每个步骤和元素。
