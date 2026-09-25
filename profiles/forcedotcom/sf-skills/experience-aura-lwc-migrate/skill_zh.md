<!-- adk-managed-skill -->

# 将 Aura 组件迁移到 LWC

使用基于产品需求文档（PRD）的工作流程，将现有的 Salesforce Aura 组件包迁移到 Lightning Web Component。通过八个专家视角（静态引用、数据、API 界面、插槽、样式、默认值、未知依赖项、冗余代码清理）分析 Aura 源代码，生成一个与框架无关的 PRD，并将其交给 LWC 编写技能进行验证，对照 Aura→LWC 完整性检查清单。

## 使用场景

- 将 Aura 组件包（`.cmp`、`.controller.js`、`.helper.js`、`.renderer.js`、`.css`、`.design`、`.evt`、`.intf`）迁移到 LWC。
- 从 Aura 源代码生成与框架无关的 PRD，以便兄弟团队实现等效的 LWC。
- 审计 Aura 组件，在 LWC 转换前需要显式映射的模式（方面、`aura:id` DOM 访问、`force:recordData`、应用程序事件）。

**不要**使用此技能用于：

- 从 Figma 或没有 Aura 源代码的 PRD 创建全新的 LWC（委托给 `experience-lwc-generate`）。
- 重构现有的 LWC（委托给 `experience-lwc-generate`）。
- 对已经使用此技能完成的转换进行事后完整性评分，或 Lightning Out Beta→2.0 主页迁移——目前没有检查入的技能涵盖这些情况。

## 前置条件

- Aura 组件包文件（最低要求：`.cmp`；通常还包括控制器 / 辅助函数 / CSS / 事件 / 接口）。
- 目标 LWC 路径（模块文件夹）——从 `sfdx-project.json` 的 `packageDirectories` 发现调用者的模块树（通常是一个 `lwc/<name>/` 子目录，位于列出的包路径之一下）。
- 对于解析器辅助依赖项查找（阶段 2，步骤 7）：调用者工作区中已安装 `@sfdc-internal/adk-knowledge` 包。如果不存在，该技能将缺失依赖项显示为未知，而不是失败。
- 了解项目的下游 LWC 编写流程——此技能将 PRD 交给该流程，但不会调用它。

## 核心原则

在每个阶段之前和期间应用 Aura→LWC 迁移原则：理解后再转换，优先考虑功能等价性而非结构等价性，利用原生 Web 标准，迭代迁移，彻底测试。架构差异（双向绑定→单向绑定、Aura 事件→DOM 事件、`aura:id`→`this.template.querySelector` 等）在 [references/aura-migration-guidelines.md](references/aura-migration-guidelines.md) 中记录。

## 知识库

- [references/aura-prd-framework.md](references/aura-prd-framework.md) — 从 Aura 组件起草框架无关 PRD 的 14 部分框架。
- [references/aura-migration-guidelines.md](references/aura-migration-guidelines.md) — 核心原则 + Aura 与 LWC 的架构差异 + 标记 / JS / 事件 / 生命周期转换表。
- [references/aura-reference-expert.md](references/aura-reference-expert.md) — 静态资源、全局值提供者、HTML→通用术语、URL、组件依赖项、`Aura.Action` 处理器。
- [references/aura-data-expert.md](references/aura-data-expert.md) — 数据需求、`force:recordData`、`lightning:recordViewForm`、Apex 控制器。
- [references/aura-api-expert.md](references/aura-api-expert.md) — API 界面：公共属性、方法、布局、组件事件、DOM 事件。
- [references/aura-slots-expert.md](references/aura-slots-expert.md) — 默认和命名插槽（Aura 方面 / `{!v.body}`→LWC 插槽）。
- [references/aura-style-expert.md](references/aura-style-expert.md) — CSS、SLDS、设计令牌、动态样式。
- [references/aura-values-expert.md](references/aura-values-expert.md) — 默认值和初始化模式。
- [references/aura-resolver-expert.md](references/aura-resolver-expert.md) — 通过 `@sfdc-internal/adk-knowledge` 包解析未知组件、事件、接口和库。
- [references/aura-redundant-code-expert.md](references/aura-redundant-code-expert.md) — 在 LWC 交接前从 PRD 中移除 Aura 特有的噪音（注释掉的标记/JS/CSS、遥测/仪器、未在其他地方使用的私有属性/方法）。
- WCAG 2.2 — Aura 范围内的可访问性审查者（SC 1.3.1 (ii) 表格、1.3.5 识别输入目的、3.2.1 聚焦、3.2.2 输入、3.3.2 标签或说明、4.1.2 名称 / 角色 / 值）计划在后续 PR 中作为单独的 `accessibility-code-review-aura` 技能发布；在此期间，阶段 3 将 WCAG 前言内联应用。
- [references/aura-to-lwc-completeness-checklist.md](references/aura-to-lwc-completeness-checklist.md) — 转换后验证评分标准。

在起草或增强相应 PRD 部分之前打开相关参考。

## 工作流程

此技能仅涵盖分析和 PRD 生成阶段。它**不**生成、编辑或验证 LWC 包、线适配器或测试。当此技能被调用时，以下阶段 1–3 是强制性的。阶段 4–5 描述推荐的下游编写流程——它们是调用者的信息性后续指导，**不**由此技能执行。

### 阶段 1 — 分析和起草 PRD

**目标**：生成一个包含 14 部分框架的每个部分的 YAML PRD 草稿。

1. 检查调用者提供的 Aura 组件包文件。提取组件名称、`.cmp` 元数据的 `access` 属性以及每个嵌入/引用的组件。
2. 应用 [references/aura-prd-framework.md](references/aura-prd-framework.md) 中的框架。在概述中明确声明 `access` 属性，并描述其影响（GLOBAL：跨命名空间公开；PRIVILEGED/PUBLIC：受限；等）。
3. 永远不要在 `unknowns` 部分列出主机组件本身——这会创建循环依赖。如果不存在有效未知项，请使用空数组。
4. 将草稿 PRD 保存到工作区（例如，`packages/skills/<skill>-workspace/<iteration>/PRD-draft.yaml`）。

**交付物**：覆盖 14 个部分的草稿 PRD（YAML）。

### 阶段 2 — 使用 Aura 专家视角增强 PRD

**目标**：使用八个 Aura 专家框架加固每个部分。

按顺序应用专家。每次遍历读取草稿 PRD 并就地重写相关部分。

1. **引用分析** — 应用 [references/aura-reference-expert.md](references/aura-reference-expert.md) 到 `staticReferences`、`componentCommunication` 和 `unknowns`。枚举每个 `$Resource`、`$ContentAsset`、`$Label`、`$Browser`、`$Locale`、`/lightning/*` 路由，以及 `c:*` / `force:*` / `lightning:*` 依赖项。蓝图绝不能直接包含 Aura 特有的字符串 `$ContentAsset`、`$Label`、`$Resource`、`$Browser` 或 `$Locale`；用意图描述替换每个。
2. **数据分析** — 应用 [references/aura-data-expert.md](references/aura-data-expert.md) 到 `dataRequirements`。蓝图 `dataRequirements` 不能包含 `force:recordData` 或 `lightning:recordViewForm`——记录底层记录、字段和对象 API 名称。将 `sObjectName`→`objectApiName`。捕获 Apex 控制器方法名称、输入参数和输出形状。
3. **API 分析** — 应用 [references/aura-api-expert.md](references/aura-api-expert.md) 到 `componentCommunication`、`interactions` 和 `staticReferences`。记录每个公共属性（类型、默认值和所有使用意图）、`<aura:method>` 声明、事件触发（`component.getEvent(...).fire()`）和对象类型回调属性（这些将成为 LWC 自定义事件）。
4. **插槽分析** — 应用 [references/aura-slots-expert.md](references/aura-slots-expert.md) 到 `contentRequirements`。将每个 `{!v.body}` / `{#v.body}` 转换为默认插槽条目（LWC 组件只能有一个默认插槽——捕获其存在条件），将每个 `<aura:attribute type="Aura.Component">` 或 `"Aura.Component[]"` 转换为命名插槽条目。
5. **样式分析** — 应用 [references/aura-style-expert.md](references/aura-style-expert.md) 到 `styling` 和 `dataRequirements`。将样式相关属性从 `dataRequirements` 移到 `styling`。记录 SLDS 钩子、自定义 CSS 和任何由 JS 驱动的动态样式。
6. **值分析** — 应用 [references/aura-values-expert.md](references/aura-values-expert.md) 到 `dataRequirements`。对于每个 Aura 属性，记录其默认值（类型 + 字面量；或命名空间 + 名称用于 `$Label` 引用）在 `what` 属性中。
7. **解析器分析** — 应用 [references/aura-resolver-expert.md](references/aura-resolver-expert.md) 到 `unknowns`。对于每个未知项，解析命名空间 + 名称，使用映射规则在 `node_modules/@sfdc-internal/adk-knowledge/dist/` 下查找相应文件，并要么内联解析内容，要么留下需要手动研究的注释。如果 `@sfdc-internal/adk-knowledge` 包未安装，请记录预期路径并保留未知项。
8. **冗余代码清理** — 应用 [references/aura-redundant-code-expert.md](references/aura-redundant-code-expert.md) 到 PRD。移除注释掉的标记/JS/CSS、遥测/仪器，以及未在其他地方使用的私有属性/方法——这些不会传递到 LWC。保持 PRD 的 JSON 形状完整；部分可能最终为空数组。生成一个简短报告，仅列出实际更改的项目。

**交付物**：应用了所有八个专家遍历的增强 PRD（YAML）。

### 阶段 3 — 可访问性遍历

**目标**：确保 PRD 的 `accessibility` 部分满足 WCAG 2.2 最低标准。

1. 将 WCAG 2.2 审查者内联应用于 Aura 源文件（`.cmp`、`.controller.js`、`.helper.js`、`.renderer.js`、`.css`）。涵盖 Aura 范围内的成功标准：1.3.1 (ii) 表格、1.3.5 识别输入目的、3.2.1 聚焦、3.2.2 输入、3.3.2 标签或说明、4.1.2 名称 / 角色 / 值。（当兄弟 `accessibility-code-review-aura` 技能在后续 PR 中发布时，将其交给它。）。
2. 将每个发现折叠到 PRD 的 `accessibility` 部分。对于每个要求，捕获它满足的 WCAG 成功标准以及建议的 LWC 实现方法（首选语义 HTML，仅在语义 HTML 无法实现相同结果时使用 ARIA）。
3. 仅引用直接破坏 WCAG 成功标准的违规行为。不要建议超出 WCAG 范围的改进。

**交付物**：具有可访问性部分，列出每个所需功能、它满足的 WCAG 成功标准以及 LWC 实现方法的 PRD。

### 阶段 4 — 下游编写（后续指导，不在此执行）

完成增强 PRD 后，调用者可以将它交给 LWC 编写工作流。此技能不执行任何编写。推荐的下游步骤：

- 将增强 PRD 作为设计输入传递给 `experience-lwc-generate`，替代 Figma / 书面规范输入。此技能不调用 `experience-lwc-generate`；调用者作为后续步骤触发它。
- 对于数据访问决策（UIAPI / GraphQL / Apex），调用者可以咨询专注于 LDS 的工作流程，将 PRD 的 `dataRequirements` 部分转换为具体的适配器。
- 对于 SLDS 样式决策，调用者可以咨询 SLDS 设计工作流程。

### 阶段 5 — 下游验证（后续指导，不在此执行）

LWC 编写完成后，调用者可以使用项目的标准测试和审查工作流程验证迁移的组件——Jest 覆盖率、可访问性 Jest、a11y / 安全 / RTL 审查、遥测、功能标志门控等。应用 [references/aura-to-lwc-completeness-checklist.md](references/aura-to-lwc-completeness-checklist.md) 作为完成 LWC 的最终评分遍历。

## 交叉引用

- `experience-lwc-generate` — 推荐的下游编写交接（非执行；调用者在此技能的 PRD 完成后触发它）。

## 验证（仅 PRD）

- 增强后的 PRD 覆盖所有 14 个框架部分，没有 `TODO` / 占位符条目。
- `dataRequirements` 不包含对 `force:recordData` 或 `lightning:recordViewForm` 的直接引用，也没有 `sObjectName` 键（重命名为 `objectApiName`）。
- `staticReferences` 和其他部分不包含原始 Aura 字符串，如 `$Resource`、`$Label`、`$ContentAsset`、`$Browser`、`$Locale`。
- 每个 `<aura:method>` 都出现在 `interactions` 中，并带有相应的触发器。
- 每个 `{!v.body}` / `{#v.body}` 都出现在 `contentRequirements` 中作为默认插槽（带有存在条件）。
- 每个 `<aura:attribute type="Aura.Component">` 都出现在 `contentRequirements` 中作为命名插槽。
- 每个未知项都通过 `@sfdc-internal/adk-knowledge` 包解析（或标记为手动要求，并尝试知识文件路径）。
