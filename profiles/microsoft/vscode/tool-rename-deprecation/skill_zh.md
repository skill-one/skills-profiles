# 工具重命名弃用

当工具或工具集的引用名称被更改时，**旧名称必须始终添加到弃用/遗留数组**中，以便现有的提示文件、工具配置和保存的引用能够继续正确解析。

## 使用场景

在**任何对内置工具或工具集注册代码的更改**上运行此技能以捕获回归问题：

- 重命名工具的 `toolReferenceName`
- 重命名工具集的 `referenceName`
- 将工具从一个工具集移动到另一个工具集（旧的 `toolSet/toolName` 路径成为遗留名称）
- 审查修改工具注册的 PR — 确认没有遗漏遗留名称

## 流程

### 第 1 步 — 确定发生了什么变更

确定您是在重命名**工具**还是**工具集**，以及它们在哪里注册：

| 实体 | 注册方式 | 需要重命名的名称字段 | 遗留数组 | 稳定 ID（绝对不能更改） |
|------|-------------|---------------------|-------------|-------------------------|
| 工具 (`IToolData`) | TypeScript | `toolReferenceName` | `legacyToolReferenceFullNames` | `id` |
| 工具（扩展） | `package.json` `languageModelTools` | `toolReferenceName` | `legacyToolReferenceFullNames` | `name`（变为 `id`） |
| 工具集 (`IToolSet`) | TypeScript | `referenceName` | `legacyFullNames` | `id` |
| 工具集（扩展） | `package.json` `languageModelToolSets` | `name` 或 `referenceName` | `legacyFullNames` | — |

**关键点：** 对于扩展贡献的工具，`package.json` 中的 `name` 字段映射到 `IToolData` 上的 `id`（参见 `languageModelToolsContribution.ts` 行 `id: rawTool.name`）。它也用于激活事件（`onLanguageModelTool:<name>`）。**绝对不要重命名 `name` 字段** — 只重命名 `toolReferenceName`。

### 第 2 步 — 将旧名称添加到遗留数组

**验证旧的 `toolReferenceName` 值是否出现在 `legacyToolReferenceFullNames` 中。** 不要假设它已经在那里 — 检查实际数组内容。如果旧名称已经列出（例如，来自先前的重命名），请确认它没有被移除。如果没有，请添加它。

**对于内部/内置工具**（TypeScript `IToolData`）：

```typescript
// 重命名前
export const MyToolData: IToolData = {
	id: 'myExtension.myTool',
	toolReferenceName: 'oldName',
	// ...
};

// 重命名后 — 保留旧名称
export const MyToolData: IToolData = {
	id: 'myExtension.myTool',
	toolReferenceName: 'newName',
	legacyToolReferenceFullNames: ['oldName'],
	// ...
};
```

如果该工具之前位于一个工具集中，请使用完整的 `toolSet/toolName` 形式：

```typescript
legacyToolReferenceFullNames: ['oldToolSet/oldToolName'],
```

如果多次重命名，**累积**所有先前的名称 — 绝对不要移除现有条目：

```typescript
legacyToolReferenceFullNames: ['firstOldName', 'secondOldName'],
```

**对于工具集**，在调用 `createToolSet` 时将旧名称添加到 `legacyFullNames` 选项：

```typescript
toolsService.createToolSet(source, id, 'newSetName', {
	legacyFullNames: ['oldSetName'],
});
```

**对于扩展贡献的工具**（`package.json`），仅重命名 `toolReferenceName` 并将旧值添加到 `legacyToolReferenceFullNames`。**不要重命名 `name` 字段：**

```jsonc
// 正确 — 仅 toolReferenceName 变更，name 保持稳定
{
	"name": "copilot_myTool",           // ← 保持此值不变
	"toolReferenceName": "newName",     // ← 已重命名
	"legacyToolReferenceFullNames": [
		"oldName"                       // ← 保留旧的 toolReferenceName
	]
}
```

### 第 3 步 — 检查所有使用工具名称的消费者

遗留名称必须**在所有通过引用名称查找工具的地方**得到尊重，而不仅仅是提示解析。主要消费者：

- **提示文件** — `getDeprecatedFullReferenceNames()` 将旧名称映射到当前名称，用于 `.prompt.md` 验证和代码操作
- **工具启用** — `getToolAliases()` / `getToolSetAliases()` 返回遗留名称，以便工具选择器和启用映射可以解析它们
- **自动批准配置** — `isToolEligibleForAutoApproval()` 检查 `legacyToolReferenceFullNames`（包括命名空间遗留名称后的段）与 `chat.tools.eligibleForAutoApproval` 设置
- **RunInTerminalTool** — 它有自己的本地自动批准检查，也会迭代 `LEGACY_TOOL_REFERENCE_FULL_NAMES`

重命名后，确认：
1. `.prompt.md` 文件中的 `#oldName` 仍然解析（显示无验证错误）
2. 引用旧名称的工具配置仍然激活该工具
3. 具有 `"chat.tools.eligibleForAutoApproval": { "oldName": false }` 的用户仍然受到该限制

### 第 4 步 — 更新引用（可选）

虽然遗留名称确保向后兼容，但更新第一方引用以使用新名称：
- 系统提示和内置 `.prompt.md` 文件
- 提及工具引用名称的文档和模型描述
- 直接引用旧名称的测试文件

## 关键文件

| 文件 | 包含内容 |
|------|-----------------|
| `src/vs/workbench/contrib/chat/common/tools/languageModelToolsService.ts` | `IToolData` 和 `IToolSet` 接口，包含遗留名称字段 |
| `src/vs/workbench/contrib/chat/browser/tools/languageModelToolsService.ts` | 解析逻辑：`getToolAliases`, `getToolSetAliases`, `getDeprecatedFullReferenceNames`, `isToolEligibleForAutoApproval` |
| `src/vs/workbench/contrib/chat/common/tools/languageModelToolsContribution.ts` | 扩展点模式、验证，以及关键的 `id: rawTool.name` 映射（行 ~274） |
| `src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/runInTerminalTool.ts` | 示例：一个具有本地自动批准检查（针对遗留名称）的工具 |

## 实际示例

- `runInTerminal` 工具：从 `runCommands/runInTerminal` 重命名为 → `legacyToolReferenceFullNames: ['runCommands/runInTerminal']`
- `todo` 工具：从 `todos` 重命名为 → `legacyToolReferenceFullNames: ['todos']`
- `getTaskOutput` 工具：从 `runTasks/getTaskOutput` 重命名为 → `legacyToolReferenceFullNames: ['runTasks/getTaskOutput']`

## 参考 PR

- [#277047](https://github.com/microsoft/vscode/pull/277047) — **设计 PR**：引入 `legacyToolReferenceFullNames` 和 `legacyFullNames`，构建了解析基础设施，并执行了第一批工具重命名。用作正确使用遗留名称重命名的模板。
- [#278506](https://github.com/microsoft/vscode/pull/278506) — **消费者端修复**：在 #277047 中的重命名后，`eligibleForAutoApproval` 设置没有检查遗留名称 — 限制旧名称的用户失去了该限制。说明为什么所有工具引用名称的消费者都必须考虑遗留名称。
- [vscode-copilot-chat#3810](https://github.com/microsoft/vscode-copilot-chat/pull/3810) — **错误示例**：重命名 `openSimpleBrowser` → `openIntegratedBrowser` 但也更改了 `name` 字段（稳定 ID）从 `copilot_openSimpleBrowser` → `copilot_openIntegratedBrowser`。`toolReferenceName` 向后兼容性只是巧合（旧名称碰巧已经在遗留数组中，来自先前的更改 — 它不是有意作为这次重命名添加的）。

## 回归检查

在触及工具注册的任何 PR 上运行此检查（TypeScript `IToolData`, `createToolSet` 或 `package.json` `languageModelTools`/`languageModelToolSets`）：

1. **在 diff 中搜索更改的 `toolReferenceName` 或 `referenceName` 值。** 对于每个更改，确认**前值**现在出现在 `legacyToolReferenceFullNames` 或 `legacyFullNames` 中。不要假设它已经在那里 — 查看实际数组。
2. **在 diff 中搜索扩展贡献工具的更改 `name` 字段。** `name` 字段是工具的稳定 `id` — 它**绝对不能**更改。如果它更改了，将其标记为错误。这会破坏激活事件、通过 ID 调用工具以及任何引用工具 `name` 的代码。
3. **验证没有从现有的遗留数组中移除条目。**
4. **如果工具在工具集之间移动**，确认旧的 `toolSet/toolName` 完整路径在遗留数组中。
5. **检查工具集成员列表**（`languageModelToolSets` 贡献中的 `tools` 数组）。如果工具的 `toolReferenceName` 更改了，引用旧名称的任何工具集 `tools` 数组应更新 — 但遗留解析系统会处理此问题，因此旧名称仍然有效。

## 反模式

- **更改扩展贡献工具的 `name` 字段** — `package.json` 中的 `name` 映射到 `IToolData` 上的 `id`（通过 `languageModelToolsContribution.ts` 中的 `id: rawTool.name`）。更改它会破坏激活事件（`onLanguageModelTool:<name>`）、任何通过 ID 引用工具的代码以及工具调用。只重命名 `toolReferenceName`，绝对不要重命名 `name`。（参见 [vscode-copilot-chat#3810](https://github.com/microsoft/vscode-copilot-chat/pull/3810) 其中 `name` 和 `toolReferenceName` 都被更改了。）
- **更改 TypeScript 注册工具的 `id` 字段** — 原理与上述相同。`id` 是一个稳定的内部标识符，绝对不能更改。
- **假设旧名称已经在遗留数组中** — 通过读取实际的 `legacyToolReferenceFullNames` 内容来验证，而不仅仅是检查该字段是否存在。遗留数组可能列出了来自更早重命名的名称，但不是当前正在更改的名称。
- **从遗留数组中移除旧名称** — 破坏现有的保存提示和用户配置。
- **完全忘记添加遗留名称** — 提示文件和工具配置将沉默地停止解析。
- **仅更新提示解析但未更新其他消费者** — 自动批准设置、工具启用映射和单个工具检查（如 `RunInTerminalTool`）都需要尊重遗留名称（参见 [#278506](https://github.com/microsoft/vscode/pull/278506)）。
