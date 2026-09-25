<!-- adk-managed-skill -->

# 使用 Lightning 基础组件

Lightning 基础组件 (LBC) 是 Salesforce 提供的 `lightning-*` 网络组件。此技能引导代理通过正确的决策序列，确保最终组件选择尽可能**具体**，并基于真实的 API 文档——而不是重新实现已存在的内容。

## 何时使用此技能

- 用户描述 UI 需求（"可搜索的下拉菜单"、"记录编辑表单"、"带页脚的模态框"）并询问哪个 `lightning-*` 组件适用。
- 用户即将构建原始组件（按钮组、组合框、提示消息）并且应该使用 LBC。
- 用户要求您审查 LWC 标记以解决 LBC 相关问题——特别是覆盖 SLDS 类或重新设计 LBC 内部。
- 用户需要特定 `lightning-*` 标签的权威属性/事件/插槽。

## 前置条件

- 了解您的组织使用的 LBC 命名空间（`lightning` 是默认的公共命名空间；某些平台暴露 `lightning-community` 或其他命名空间——用户的元文件将澄清）。
- 此技能为每个 Lightning 基础组件提供权威 API 文档，位于 [references/lightning-components.md](references/lightning-components.md)。每个组件都是一个 `# 组件 API 结构` 块；使用 `grep **Name:** <camelCaseName>`（例如 `**Name:** datatable`）查找其属性/方法/事件/插槽。阅读此文档而不是依赖缓存知识——LBC 在发展，参考是事实来源。

## 工作流程

### 第 1 步——首先阅读**整个**组件索引

打开 [lightning-component-index.md](references/lightning-component-index.md) 并扫描**所有**条目，然后再进行任何选择。这是非协商的：LBC 的价值来自选择最专业的组件，跳过扫描会导致用原始组件重新发明复合组件。

扫描时，编制一个**候选列表**——每个描述触及用例任何方面的组件。暂时不要过滤或排序。

### 第 2 步——根据功能缩小到最具体的匹配

扫描完成后：

- 对于用例中的每个功能，选择覆盖它的**最具体**组件。当专用组件覆盖端到端的场景时，优先选择专用复合组件（`lightning-record-form`、`lightning-tabset`、`lightning-datatable`）而不是通用原始组件（`lightning-input`、`lightning-button`）。
- 避免重复：如果 `lightning-record-form` 已经渲染记录字段，除非您明确覆盖行为，否则不要将其与 `lightning-input-field` 配对。

### 第 3 步——分享短列表并确认

将最终短列表展示给开发者，每个组件附上一行理由。在拉取完整 API 文档之前等待明确确认。这可以防止代理在开发者已经心理排除的组件上浪费上下文。

### 第 4 步——检索完整 API 文档

确认后，使用捆绑的辅助工具拉取精确的 API 块——这避免了在大型参考中临时使用 `grep`：

```bash
scripts/extract-component-docs.sh <camelCaseName> [<camelCaseName>...]
```

将 `lightning-<foo>` 标签转换为 camelCase（不带 `lightning-` 前缀）：

- `lightning-datatable` → `datatable`
- `lightning-record-edit-form` → `recordEditForm`
- `lightning-button-icon` → `buttonIcon`

每个返回的块具有相同的结构：**基本信息**（标签、命名空间、类型）、**属性**（名称、类型、默认值、描述）、**方法**、**事件**、**插槽**，以及（适用时）使用说明。此技能是关于**选择**组件；捆绑的参考是关于**连接**它们。

### 第 5 步——生成集成指南

使用每个组件的参考，引导开发者：

- 精确的 `<lightning-...>` 标签和所需属性。
- 绑定哪些事件（`onchange`、`oncommit`、`onsuccess`、…）以及事件负载包含什么。
- 填充任何插槽（标题、页脚、自定义内容）。
- 组件文档中的已知限制（例如 `lightning-record-form` 在编辑/查看模式下需要 `object-api-name` 和 `record-id`）。

### 第 6 步——遵守 LBC 样式规则

不要覆盖 LBC 内部的 SLDS 类。具体细节请参阅 [lbc-expert-guidance.md](references/lbc-expert-guidance.md)。常见问题：

- 在宿主组件的 CSS 中针对 `.slds-button` 或 `.slds-input` 以重新设计 LBC——LBC 运行在 shadow root 内，因此这些选择要么泄漏到兄弟组件，要么完全被剥离。改用组件文档中记录的样式钩（`--sds-c-button-*` 等）。
- 仅为了修改内部标记而包装 LBC。您不能——标记隐藏在 shadow root 后面。如果组件没有暴露您需要的插槽/属性，那是一个平台级差距，而不是重新设计工作。

## 示例

### 示例——"我需要一个带类型预览的多选组合框"

1. 逐个扫描组件索引。
2. 候选列表包括：`lightning-combobox`、`lightning-dual-listbox`、`lightning-record-picker`。
3. 短列表：`lightning-dual-listbox`（文档中的多选基础组件）。排除 `lightning-combobox`——其文档 API 是单选；它没有 `type="multi"`，也没有多选模式。标记 `lightning-record-picker` 仅在值是记录 ID 时适用。
4. 开发者确认 `lightning-dual-listbox`。
5. 运行 `scripts/extract-component-docs.sh dualListbox`。
6. 从块的属性/事件部分返回 `options`、`value`、`onchange` 负载和所需标签属性。

### 示例——"我要自己写一个模态框"

1. 扫描找到 `lightning-modal`、`lightning-modal-body`、`lightning-modal-footer`、`lightning-modal-header`。
2. 短列表是 4 个模态组件。
3. 确认。
4. 运行 `scripts/extract-component-docs.sh modal modalHeader modalBody modalFooter` → 完整的模态 API（如何扩展 `LightningModal`、静态 `.open()` 模式、插槽标题/正文/页脚）。
5. 引导开发者避免自己编写对话框。

## 验证清单

- [ ] 在任何选择之前扫描了完整组件索引（没有关键词搜索捷径）。
- [ ] 候选列表包括每个触及用例的组件。
- [ ] 最终短列表为每个功能选择**最具体**的组件。
- [ ] 在打开捆绑组件参考之前，开发者确认了短列表。
- [ ] 集成指南引用了真实 API 文档中的属性/事件/插槽（不是推断的）。
- [ ] 没有建议通过覆盖 SLDS 类来重新设计 LBC。

## 故障排除

- **使用 `grep **Name:** <name>` 返回无匹配**——名称错误，或参考使用不同的 camelCase。与组件索引核对（`lightning-record-form` → `recordForm`、`lightning-record-view-form` → `recordViewForm`、`lightning-button-icon` → `buttonIcon`）。
- **建议的组件没有您预期的属性**——相信真实 API 文档而不是记忆。LBC 在发展；缓存知识是错误的。
- **开发者抵制短列表**——不要跳过第 4 步。仍然检索开发者首选选择的文档，让他们看到实际的权衡。
- **开发者想重新设计 LBC 内部**——重定向到样式钩（请参阅 LBC 专家参考）。拒绝 shadow DOM 渗透是正确的答案。
