<!-- adk-managed-skill -->

# 应用 LDS 最佳实践

将 Lightning Data Service 指南应用于 Lightning Web 组件。三大支柱：**数据一致性**、**参照完整性**以及 **UIAPI 与 Apex**。重点关注 UI API 路径 — GraphQL 和上游数据需求分析由外部处理。

## 何时使用

- 审查组件的数据层以符合 LDS 规范（手写表单、字符串类型的字段名、未同步的 Apex + LDS、Apex 过度使用）。
- 在标准或自定义对象上实现 CRUD。
- 在 `getRecord`、`getRecords`、`createRecord`、`updateRecord`、`deleteRecord`、基础记录表单组件或 Apex 之间进行选择。
- 修复记录修改后的过时数据错误。
- 添加模式导入（`@salesforce/schema/...`）以替换硬编码的字段/对象名。

**不要**使用此技能用于：
- GraphQL 查询/变异生成 — 目前由外部处理。
- 上游数据需求发现 — 目前由外部处理。
- SLDS 类/设计令牌工作（使用 `design-systems-slds-apply`）。
- 可访问性、安全性或 RTL 审查 — 这些是单独的流程，使用各自的工具运行。

## 前置条件

- 组件路径。
- 理解组件的数据操作（读取/写入/两者）以及 Apex 是否已参与。
- 可以访问组织的模式以用于 `@salesforce/schema` 导入（设置 → 对象管理器 → `<对象>` → 详细信息 → API 名称；或者，当 GraphQL 服务读取时，从目标组织拉取的 SDL）。

## 知识库

- [references/lds-expert.md](references/lds-expert.md) — 权威的 LDS 知识（模式、适配器、缓存、变异流程）。
- [references/lds-data-consistency.md](references/lds-data-consistency.md) — 缓存失效、`refreshApex`、`notifyRecordUpdateAvailable`、线结果传播。
- [references/lds-referential-integrity.md](references/lds-referential-integrity.md) — `@salesforce/schema` 导入、字段常量、对象名解析及其通过重构的传播。

**每个适配器的 API 参考** — [references/adapter-apis.md](references/adapter-apis.md) 包含每个 UI API 适配器的语法/参数/返回/用法，按家族分组（`uiRecordApis`、`uiListsApis`、`uiRelatedListApis`、`uiObjectInfoApis`）。每个适配器是一个 `` # `<name>` `` 块；使用反引号搜索名称（例如 `` # `getRecord` ``）跳转到其条目。在连接适配器之前阅读此内容；不要凭记忆释义。

**类型目录** — [references/wire-adapter-types.md](references/wire-adapter-types.md) 包含适配器返回的每个类型（`Record`、`ObjectInfo`、`FieldValue` 等），按类别分组并以传统 MCP 工具使用的相同格式渲染。使用 `## <TypeName>` 搜索特定条目。

编辑代码前阅读适用的参考。

## 核心原则

1. 对于标准或自定义对象的 CRUD，优先使用 **LDS/UIAPI**。仅当业务逻辑或批量操作超出 LDS 能力时，才使用 Apex。
2. 在任何变异后，始终使用 `refreshApex(wiredResult)` **或** `notifyRecordUpdateAvailable([{ recordId }])` 保持渲染数据的新鲜。
3. 从 `@salesforce/schema` 导入对象和字段引用 — 而不是字符串字面量。这可以保护组件免受元数据重命名的影响。
4. 对于单记录 UI，优先使用基础记录表单组件（`lightning-record-form`、`lightning-record-edit-form`、`lightning-record-view-form`）。它们自带验证、SLDS 样式、可访问性和字段级安全。

## 审查清单

对每个问题回答 **是/否**。任何 **是** 都会触发重构。

### 1. 手写表单而不是基础组件
- 组件是否为单记录 CRUD 实现了自定义表单，而 `lightning-record-form`、`lightning-record-edit-form` 或 `lightning-record-view-form` 足以满足？
- 验证逻辑是否重复了基础记录表单组件提供的原生功能？
- 是否手动重新创建了标准 SLDS 样式，而不是利用基础组件中的样式？

### 2. 未导入引用
- 对象或字段 API 名称是否作为硬编码的字符串引用？
- 在模板中，是否直接通过表达式（如 `record.data.fields.Name.value`）访问字段值，而没有使用模式导入？
- JS 文件是否缺少任何 `@salesforce/schema` 导入，即使它与 Salesforce 字段交互？

### 3. 未同步地混合 Apex 和 LDS
- 组件是否通过 LDS 读取并通过 Apex 变异同一记录，而没有后续的缓存刷新？
- 是否通过 Apex 获取，但依赖 LDS 缓存显示，而没有在更新后同步？
- 多个数据源是否触及同一对象，而没有明确的刷新策略？

### 4. 过度使用 Apex
- 组件是否仅调用 Apex 来检索或更新单个记录，而 `getRecord`、`updateRecord` 或基础记录表单可以处理？
- 是否使用 Apex 来运行简单的 SOQL 查询，其字段可通过标准 LDS 线结果适配器获取？
- 是否存在自定义 Apex 方法用于基本 CRUD，而代码中没有出现 LDS/UIAPI 调用？

## 工作流

### 第 1 步 — 列出数据层

列出组件中的每个数据操作：

- 线结果适配器（`@wire(getRecord, …)`、`@wire(getRecords, …)`、`@wire(someApexMethod, …)`）。
- 命令式调用（`updateRecord`、`createRecord`、`deleteRecord`、Apex 命令式）。
- 读取与写入、目标对象、字段，以及写入后的刷新路径是否已连接。

### 第 2 步 — 运行四部分清单

按顺序走遍 §1–§4。对于每个部分，决定它是否适用于正在审查的组件，并在报告中记录结果。使用以下格式 — 每个部分必须出现一次，要么作为 **问题**（违规）列在 `## LDS 最佳实践` 下，要么作为 **合规** 条目列在 `## 已检查部分（无问题）` 下。最后以 `## 总结` 行列出计数和一段简短说明结束。

**报告格式：**

```markdown
## LDS 最佳实践

- §<N> <部分标题> — <文件>:<行号>
  问题： <具体错误，引用代码中的模式>
  修复： <纠正性更改，命名确切的导入/API>
  应用： <是 | 否>

## 已检查部分（无问题）

- §<N> <部分标题> — <文件>:<行号>
  状态：合规（无操作）。
  证据： <代码中的具体内容使本部分合规 — 引用行号、导入和使用的基线组件或模式令牌>

## 总结

- 找到 <X> 个问题；修复 <Y> 个；推迟 <Z> 个。
- <一段关于审查的简短说明 — 组件的功能、为什么标记的问题很重要，以及为什么合规部分合规。>
```

生成此报告的规则：

- §1–§4 中的每一个都必须出现在这两个块中的其中一个。不要因为合规而省略部分；在 `## 已检查部分（无问题）` 下记录证据。
- 在 `## LDS 最佳实践` 下，仅列出实际违规。如果没有违规，将第一行写为“未发现最佳实践问题”，然后移动每个部分到合规块。
- 引用正在审查的组件的具体文件路径和行号 — 不要使用通用引用。
- 不要添加 §1–§4 之外的额外部分；下游 a11y / RTL / 安全审查作为单独的工作流运行，并有自己的报告。

### 第 3 步 — 应用参照完整性修复

对于每个硬编码的 API 名称：

```javascript
import ACCOUNT_OBJECT from '@salesforce/schema/Account';
import NAME_FIELD from '@salesforce/schema/Account.Name';
import INDUSTRY_FIELD from '@salesforce/schema/Account.Industry';
```

在所有引用对象或字段的地方使用这些常量 — 线结果配置、`@wire` 字段数组、`getFieldValue(record, NAME_FIELD)` 调用，以及基础组件的 `object-api-name` / `fields` 属性。

完整规则：[references/lds-referential-integrity.md](references/lds-referential-integrity.md)。

### 第 4 步 — 应用数据一致性修复

- 在 **命令式** LDS 变异（`updateRecord`、`createRecord`、`deleteRecord`）后，发送刷新：
  ```javascript
  import { updateRecord, getRecord } from 'lightning/uiRecordApi';
  import { refreshApex } from '@salesforce/apex';

  async handleSave() {
      await updateRecord({ fields: { Id: this.recordId, Name: this.name } });
      await refreshApex(this.wiredRecord);
  }
  ```
- 在缓存持有记录的 **Apex** 变异后，优先：
  ```javascript
  import { notifyRecordUpdateAvailable } from 'lightning/uiRecordApi';
  await notifyRecordUpdateAvailable([{ recordId: this.recordId }]);
  ```
- 保留线结果引用（`this.wiredRecord = result; return result.data;`），以便 `refreshApex` 可以定位它们。
- 基础表单组件会自动刷新；无需手动刷新。

完整规则：[references/lds-data-consistency.md](references/lds-data-consistency.md)。

### 第 5 步 — 在适用处替换 Apex 为 UIAPI

- 单记录读取 → `getRecord`（带 `fields` + 模式导入）。
- 单记录更新 → `updateRecord` 或 `lightning-record-edit-form`。
- 单记录创建 → `createRecord` 或带 `mode="edit"` 的 `lightning-record-form`。
- 关联记录读取 → `getRelatedListRecords`。
- 挑单值 → `getPicklistValues`。
- 对象元数据 → `getObjectInfo` / `getObjectInfos`。

不确定适配器形状时，使用反引号搜索适配器名称（例如 `` # `getRecord` ``） — 它包含权威的参数、返回值和用法。对于 `@salesforce/schema/<Object>.<Field>` 路径，在设置 → 对象管理器 → `<Object>` → 详细信息 → API 名称中确认确切的 API 名称。对于不熟悉的返回类型，使用反引号搜索 [references/wire-adapter-types.md](references/wire-adapter-types.md) 中的类型名。

### 第 6 步 — 验证

- 组件文件中不再有硬编码的 API 名称。
- 每个写入路径都有一个匹配的刷新路径（或使用基础表单组件内部处理）。
- 没有通过 Apex 和 UIAPI 重复读取同一记录。
- 现有的 Jest 测试通过；为刷新流程（`refreshApex` 调用一次）添加覆盖率。

## 跨参考

- 相关技能：
  - `experience-lwc-generate` — 当审查表明需要重新生成而不是修补组件时。
  - `design-systems-slds-apply` — 用于由 LDS 审查暴露的 SLDS 类/设计令牌清理。
- 邻近（目前由外部处理）：
  - GraphQL 查询/变异编写、上游数据需求分析，以及安全 / RTL / 可访问性审查流程作为单独的工作流，使用各自的工具运行。

## 示例

**优先使用基础组件**

```html
<template>
    <lightning-record-form
        record-id={recordId}
        object-api-name="Account"
        fields={fields}
        mode="edit"
        onsuccess={handleSuccess}>
    </lightning-record-form>
</template>
```

```javascript
import { LightningElement, api } from 'lwc';
import NAME_FIELD from '@salesforce/schema/Account.Name';
import INDUSTRY_FIELD from '@salesforce/schema/Account.Industry';

export default class AccountEditor extends LightningElement {
    @api recordId;
    fields = [NAME_FIELD, INDUSTRY_FIELD];

    handleSuccess() {
        this.dispatchEvent(new CustomEvent('saved'));
    }
}
```

**命令式更新与刷新**

```javascript
import { LightningElement, api, wire } from 'lwc';
import { getRecord, updateRecord } from 'lightning/uiRecordApi';
import { refreshApex } from '@salesforce/apex';
import ACCOUNT_NAME from '@salesforce/schema/Account.Name';

export default class RenameAccount extends LightningElement {
    @api recordId;
    wiredRecord;

    @wire(getRecord, { recordId: '$recordId', fields: [ACCOUNT_NAME] })
    wired(result) {
        this.wiredRecord = result;
    }

    async handleRename(event) {
        await updateRecord({ fields: { Id: this.recordId, Name: event.detail } });
        await refreshApex(this.wiredRecord);
    }
}
```

## 验证

- 使用反引号搜索 `@salesforce/schema/` 导入 — 它们应涵盖组件引用的每个字段/对象。
- 使用反引号搜索看起来像 API 名称的字符串字面量（`'Account'`、`'Name'`） — 组件文件中不应出现这些。
- 追踪每个变异调用到一个刷新调用（`refreshApex`、`notifyRecordUpdateAvailable` 或基础组件内部处理）。
- 确认仅在 UIAPI 无法满足要求时（批量、复杂连接、自定义逻辑）使用 Apex。
