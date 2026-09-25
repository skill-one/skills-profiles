<!-- adk-managed-skill -->

# 生成 LDS 数据需求

运行一个三阶段分析师工作流程——需求澄清、API 名称验证、API 推荐——以便下游开发者能够无猜测地实现 Lightning Data Service (LDS) 解决方案。

## 使用场景

- PRD、Figma 评论或用户请求中提到了 Salesforce 数据，但对象/字段/操作模糊不清（“显示客户信息”、“更新记录”、“列出即将到来的活动”）。
- 在为新数据需求编写任何 `@wire`/Apex 代码之前，或在进行下游实现工作流程之前。
- 您继承了类似 `// TODO: 获取关联记录` 的 TODO，需要将其转换为精确规范。

**不使用此技能的情况：**

- 数据需求已经完全指定（对象 API 名称、字段 API 名称、操作类型、范围）。
- 组件根本没有接触 Salesforce 数据（仅 UI、外部 REST、本地状态）。

## 前置条件

- 自然语言需求（PRD 片段、用户请求或 TODO 评论）。
- 访问目标组织的 Setup → Object Manager 以确认自定义对象/字段 API 名称。
- 了解当前的 GraphQL / UI API / Apex 优先级顺序（当 GraphQL 可以满足读取时，顶部是 GraphQL）。

## 知识库

- [references/requirements-analysis.md](references/requirements-analysis.md) — 需求分析模式框架。
- [references/api-name-validation.md](references/api-name-validation.md) — 对象/字段 API 名称的精确模式。
- [references/api-recommendation.md](references/api-recommendation.md) — GraphQL → UI API → Apex 决策框架。
- [references/lds-expert.md](references/lds-expert.md) — 整体 LDS 模式和陷阱。
- [references/lds-data-consistency.md](references/lds-data-consistency.md) — 缓存和一致性保证。
- [references/lds-referential-integrity.md](references/lds-referential-integrity.md) — 父/子和关联记录规则。

## 工作流程

严格按顺序运行这三个步骤。除非调用者已经确认其输出，否则不要跳过步骤。

### 第 1 步 — 解析数据需求（需求分析模式）

**目标：** 在继续之前提取所有已知信息并暴露所有不确定性。

以以下内容开启每个对话：

> "我已经分析了您的数据需求：'<REQ>'。以下是我理解的内容以及我需要澄清的地方…"

应用来自 [references/requirements-analysis.md](references/requirements-analysis.md) 的四个操作：

1. **操作类型** — 是读取、创建、更新还是删除？模糊动词会立即触发澄清问题。确认方式：*"我已将其识别为 **<OP>** 操作。这是正确的吗？*"
2. **数据实体识别** — 标准对象（高置信度，继续）、疑似自定义对象（询问：*"这是一个自定义对象 `<Term>__c` 吗？确切的 API 名称是什么？"*）、或未知（从 Object Manager 获取 API 名称）。
3. **字段规范** — 将通用引用（`phone`、`address`、`name`、`status`）映射到具体的 API 名称。如果存在多个候选者，请枚举它们并询问。
4. **范围和上下文** — 单个记录与多个记录；用户触发与自动；预期量；实时与按需。

**步骤结束门禁。** 整合为：

```text
明确需求：[确认的事实]
需要澄清：[编号的 1.1–1.4 问题]
```

只有当所有问题都得到 ≥90% 的置信度回答时，才能继续。

### 第 2 步 — 验证 Salesforce API 名称（精确模式）

**目标：** 在编写任何代码之前，确保每个对象和字段 API 名称的 100% 准确性。

应用来自 [references/api-name-validation.md](references/api-name-validation.md) 的验证框架：

- **标准对象** — `Account`、`Contact`、`Lead`、`Opportunity`、`Case`、`User`、`Task`、`Event`、`Product2`、`Pricebook2`、`Order`、`OrderItem`、`Asset`、`Contract`、`Campaign` 立即通过。任何其他内容都会触发验证。
- **自定义对象** — 假设 `__c` 后缀是不正确的。询问：*"这是 `<Term>__c` 还是不同的自定义对象 API 名称？"* 指导用户到 Setup → Object Manager → <对象> → 详细信息 → API 名称。
- **标准字段** — 使用参考文件中的表格映射模糊引用。
- **自定义字段** — 需要确认 `__c` 后缀；区分大小写。

**确认模板：**

```text
对象 API 名称：<OBJECT>
字段 API 名称：<FIELD_LIST>
置信度级别：100% 验证
```

如果任何不确定性仍然存在，**停止**。发出未解决的验证请求和 Setup 导航说明。不要进入第 3 步或生成代码。

仅在调用者明确声明上游已经验证 API 名称，或需求完全不涉及记录时才跳过此步骤。在步骤 4 输出中记录跳过原因。

### 第 3 步 — 推荐 API（解决方案架构模式）

**目标：** 使用 [references/api-recommendation.md](references/api-recommendation.md) 中的决策框架选择正确的数据访问 API。

**优先级顺序（不可协商）：**

1. GraphQL 线路适配器（`lightning/graphql`）——读取的最佳选择。
2. UI API / LDS — CRUD 写入、元数据、布局、选择列表、简单读取。
3. Apex — 仅作为后备。

逐步执行六个决策子步骤：

1. 操作类型（读取/写入/混合）。
2. UI API 中的对象和字段支持。
3. 关系复杂性（单对象与多对象、父/子）。
4. 查询复杂性（过滤、排序、分页、聚合）。
5. 性能和可扩展性（往返次数、有效载荷大小）。
6. 特殊需求（元数据、原子事务、业务逻辑、提升权限）。

**推荐规则：**

- **GraphQL** 当读取支持的对象；多对象连接；分页/排序/过滤；聚合；最小化往返次数。
- **UI API** 当 CRUD 写入、元数据（选择列表、布局、对象信息）、`getRecordCreateDefaults` + `createRecord`、列表视图。
- **Apex** 当 UI API 不支持对象/字段；多记录原子事务；自定义业务逻辑；系统上下文权限。

使用“展示工作过程”模板——明确解释 *为什么不是 GraphQL* / *为什么不是 UI API* / *为什么不是 Apex*。

**交接：**

- 推荐 GraphQL → 在步骤 4 输出中记录查询形状（根对象、请求的字段、过滤器）；下游编写实际的 `lightning/graphql` 线路适配器是调用者的下一步。
- 推荐 UI API → 记录特定的 UI API 适配器（`getRecord`、`getRelatedListRecords`、`createRecord`、`updateRecord`、`getRecordCreateDefaults` 等）以及任何布局/选择列表先决条件。
- 推荐 Apex → 在步骤 4 输出中记录原因，并交接给项目的 Apex 工作流程。

### 第 4 步 — 发出 PRD 就绪的规范

生成一个调用者可以粘贴到 PRD 或组件文件头部的单个块：

```text
## 数据需求：<CLEAR_TITLE>

### 技术规范
- 主要对象：<OBJECT_API_NAME>
- 需要字段：<FIELD_API_NAMES>
- 关系：<关联对象或查找或无>
- 数据范围：<单个记录 | 多个记录 | 基于查询>
- 访问模式：<只读 | 读写 | 只写>
- 触发器：<用户操作 | 自动加载 | 反应式>

### 实现细节
- 推荐的 LDS API：<GRAPHQL | UI_API | APEX>
- 实现模式：<线路 | 命令式>
- 理由：<为什么选择这个 API，而不是其他 API>
- 下一步：<编写 GraphQL 线路适配器 | 编写 UI API 适配器调用 | 项目的 Apex 工作流程>
```

## 少样本模式

| 模糊请求 | 澄清问题 |
|-----------|--------------------|
| "获取联系人信息" | "哪些 `Contact` 字段具体？ (`Email`、`Phone`、`MailingAddress`、`Department`、…)" |
| "显示账户数据" | "需要哪些 `Account` 字段？ 我们显示单个记录还是列表？" |
| "自定义健身房记录" | "这是一个自定义对象 `Gym__c` 吗？ 您正在查找哪些特定字段？" |
| "更新记录" | "哪个对象？ 哪些字段？ 哪个记录（运行时 ID）？" |
| "所有客户信息" | "`Account` 或 `Contact`？ 哪些字段？ 单个记录还是查询？" |

## 验证检查清单

- [ ] 原始需求中的每个模糊术语都已解析为确认的 API 名称。
- [ ] 操作类型已确认（R / C / U / D）。
- [ ] 范围（单个与多个）和触发器（用户与自动）已记录。
- [ ] API 推荐针对所有三个选项（GraphQL / UI API / Apex）进行了解释。
- [ ] 具体的下游适配器名称已指明——无论是 `lightning/graphql`、`getRecord`、`createRecord` 等，还是项目的 Apex 工作流程。
- [ ] 如果步骤 2 被跳过，原因已记录在输出中。
- [ ] 规范块可以复制粘贴到 PRD。

## 交叉引用

- 技能：
  - 输出被 `experience-lwc-generate` 消费，用于将 `@wire` 适配器连接到组件。
- 下游编写步骤（目前不受技能约束）：
  - GraphQL 路径——调用者使用从目标组织拉取的模式编写 `lightning/graphql` 线路适配器。
  - UI API 路径——调用者连接推荐的 UI API 适配器（`getRecord`、`createRecord` 等）。
