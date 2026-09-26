# 代码连接

## 概述

创建代码连接模板文件（`.figma.ts`），将 Figma 组件映射到代码片段。给定一个 Figma URL，按照以下步骤创建模板。

> **您只编写 `.figma.ts` 模板文件——绝不编写 `.figma.tsx`。** 此技能生成*无解析器模板*：一个 `.figma.ts` 文件，其默认导出使用 `` figma.code`...` `` 标记模板。**绝对不要**编写 `.figma.tsx` 文件，也**绝对不要**使用 `figma.connect()`——那是另一种**基于解析器**的代码连接格式（以不同方式发布），并且是**错误工件**；以 `.figma.tsx` 编写的输出将被直接拒绝。如果一个组件已经存在 `.figma.tsx`，请保留它并在旁边添加您的 `.figma.ts` 模板。一个功能强大的模型可能会试图从记忆中调用更熟悉的 `.figma.tsx` / `figma.connect()` 模式——请抵制它；在这里正确的输出始终是 `.figma.ts` + `figma.code`。

## 前提条件

- **必须连接 Figma MCP 服务器**——在继续之前，请验证 Figma MCP 工具（例如，`get_code_connect_suggestions`）是否可用。如果不可用，请指导用户启用 Figma MCP 服务器并重新启动他们的 MCP 客户端。
- **组件必须已发布**——代码连接仅适用于已发布到 Figma 团队库的组件。如果一个组件未发布，请通知用户并停止。
- **需要组织或企业计划**——代码连接不适用于免费或专业计划。
- **URL 必须包含 `node-id`**——Figma URL 必须包含 `node-id` 查询参数。
- **TypeScript 类型**——在 `.figma.ts` 文件中启用编辑器自动完成和类型检查，必须在 `tsconfig.json` 中的 `types` 中添加 `@figma/code-connect/figma-types`：
  ```json
  {
    "compilerOptions": {
      "types": ["@figma/code-connect/figma-types"]
    }
  }
  ```

## 第 1 步：解析 Figma URL

从 URL 中提取 `fileKey` 和 `nodeId`：

| URL 格式 | fileKey | nodeId |
|---|---|---|
| `figma.com/design/:fileKey/:name?node-id=X-Y` | `:fileKey` | `X-Y` → `X:Y` |
| `figma.com/file/:fileKey/:name?node-id=X-Y` | `:fileKey` | `X-Y` → `X:Y` |
| `figma.com/design/:fileKey/branch/:branchKey/:name` | 使用 `:branchKey` | 从 `node-id` 参数获取 |

始终将 `nodeId` 连字符转换为冒号：`1234-5678` → `1234:5678`。

**示例：**

给定：`https://www.figma.com/design/QiEF6w564ggoW8ftcLvdcu/MyDesignSystem?node-id=4185-3778`
- `fileKey` = `QiEF6w564ggoW8ftcLvdcu`
- `nodeId` = `4185-3778` → `4185:3778`

## 第 2 步：发现未映射的组件

用户可能提供一个指向框架、实例或变体的 URL——不一定是指向组件集或独立组件。调用 MCP 工具 `get_code_connect_suggestions`，使用：
- `fileKey` — 来自第 1 步
- `nodeId` — 来自第 1 步（冒号格式）
- `excludeMappingPrompt` — `true`（返回未映射组件的轻量级列表）

此工具识别选择中尚未具有代码连接映射的已发布组件。

**处理响应：**

- **"在此选择中未找到已发布的组件"** — 该节点不包含任何已发布的组件。通知用户他们需要将组件发布到 Figma 团队库中，然后停止。
- **"此选择中的所有组件实例均已通过代码连接连接"** — 一切都已映射。通知用户并停止。
- **正常响应包含组件列表** — 为返回的每个组件提取 `mainComponentNodeId`。使用这些解析的节点 ID（而不是来自 URL 的原始 ID）进行所有后续步骤。如果返回多个组件（例如，用户选择了一个包含多个不同组件实例的框架），请针对每个组件重复步骤 3–6。

## 第 3 步：获取组件属性

调用 MCP 工具 `get_context_for_code_connect`，使用：
- `fileKey` — 来自第 1 步
- `nodeId` — 来自第 2 步的解析 `mainComponentNodeId`
- `clientFrameworks` — 根据 `figma.config.json` `parser` 字段确定（例如 `"react"` → `["react"]`）
- `clientLanguages` — 根据项目文件扩展名推断（例如 TypeScript 项目 → `["typescript"]`，JavaScript → `["javascript"]`）

对于多个组件，针对每个节点 ID 调用该工具。

响应包含 Figma 组件的**属性定义**——注意每个属性的名字和类型：
- **TEXT** — 文本内容（标签、标题、占位符）
- **BOOLEAN** — 开关（显示/隐藏图标、禁用状态）
- **VARIANT** — 枚举选项（大小、变体、状态）
- **INSTANCE_SWAP** — 与特定组件绑定的可交换嵌套实例（图标、头像）
- **SLOT** — 可变内容区域（自由布局、混合子元素）；在模板中使用 `getSlot()`（与 INSTANCE_SWAP 不同）

保存此属性列表——您将在第 5 步中使用它来编写模板。

## 第 4 步：确定代码组件

如果用户没有指定要连接哪个代码组件：

1. 检查 `figma.config.json` 中的 `paths` 和 `importPaths` 以找到组件的位置。
2. 在代码库中搜索与 Figma 组件名称匹配的组件。如果 `figma.config.json` 没有指定路径，请检查常见目录（`src/components/`、`components/`、`lib/ui/`、`app/components/`）。
3. 读取候选文件，并将它们的属性接口与第 3 步中的 Figma 属性进行比较——查找匹配的变体类型、大小选项、布尔标志和插槽属性。
4. 如果有多个候选者匹配，选择与属性接口匹配最接近的那个，并向用户解释您的推理。
5. 如果找不到匹配项，请显示 2 个最接近的候选者，并要求用户确认或提供正确的路径。

**在继续到第 5 步之前，与用户确认。** 展示匹配项：找到的代码组件、其位置以及为什么匹配（属性对应关系、命名、目的）。

读取 `figma.config.json` 以获取导入路径别名——`importPaths` 部分将 glob 模式映射到导入规范，而 `paths` 部分将那些规范映射到目录。

读取代码组件的源代码以了解其属性接口——这有助于在第 5 步中将 Figma 属性映射到代码属性。

## 第 5 步：创建模板文件 (.figma.ts)

### 文件位置

将文件与现有的代码连接文件一起放置。检查 `figma.config.json` `include` 模式以找到正确的目录。**命名它 `ComponentName.figma.ts`——绝不命名 `ComponentName.figma.tsx`。** `.figma.tsx` 扩展名是基于解析器的格式；不要创建它或修改现有的文件。

### 模板结构

每个模板文件都遵循此结构：

```ts
// url=https://www.figma.com/file/{fileKey}/{fileName}?node-id={nodeId}
// source={代码组件的路径，来自第 4 步}
// component={代码组件的名称，来自第 4 步}
import figma from 'figma'
const instance = figma.selectedInstance

// 从 Figma 组件中提取属性（见属性映射下方）
// ...

export default {
  example: figma.code`<Component ... />`,       // 必须的：代码片段
  imports: ['import { Component } from "..."'], // 可选：导入语句
  id: 'component-name',                         // 必须的：唯一标识符
  metadata: {                                    // 可选
    nestable: true,                              // true = 在父组件中内联，false = 作为药丸显示
    props: {}                                    // 可访问父模板的数据
  }
}
```

### 属性映射

使用第 3 步中的属性列表提取值。对于每个 Figma 属性类型，使用相应的方法：

| Figma 属性类型 | 模板方法 | 使用场景 |
|---|---|---|
| TEXT | `instance.getString('Name')` | 标签、标题、占位符文本 |
| BOOLEAN | `instance.getBoolean('Name', { true: ..., false: ... })` | 切换显示/隐藏图标、条件属性 |
| VARIANT | `instance.getEnum('Name', { 'FigmaVal': 'codeVal' })` | 大小、变体、状态枚举 |
| INSTANCE_SWAP | `instance.getInstanceSwap('Name')` | 固定组件插槽的可交换实例（然后 `hasCodeConnect()` / `executeTemplate()`）- 不要与下面的 SLOT 属性混淆 |
| SLOT | `instance.getSlot('Name')` | 仅当 Figma 属性类型为 **SLOT** 时，才使用自由布局插槽内容 |
| (子层) | `instance.findInstance('LayerName')` | 您知道子层名称（没有组件属性） |
| (文本层) | `instance.findText('LayerName')` → `.textContent` | 从命名文本层获取文本内容 |
| (连接的实例) | `instance.findConnectedInstance('id')` | 您知道子组件的 Code Connect `id` |
| (连接的实例) | `instance.findConnectedInstances(fn)` | 您需要多个匹配过滤器的连接子项 |
| (层) | `instance.findLayers(fn)` | 您需要任何匹配过滤器的层（文本 + 实例） |

**TEXT** — 直接获取字符串值：
```ts
const label = instance.getString('Label')
```

**VARIANT** — 将 Figma 枚举值映射到代码值：
```ts
const variant = instance.getEnum('Variant', {
  'Primary': 'primary',
  'Secondary': 'secondary',
})

const size = instance.getEnum('Size', {
  'Small': 'sm',
  'Medium': 'md',
  'Large': 'lg',
})
```

**BOOLEAN** — 简单布尔值或映射到值：
```ts
// 简单布尔值
const disabled = instance.getBoolean('Disabled')

// 映射到代码值（例如，当代码属性是枚举而不是布尔值时）
const size = instance.getBoolean('Show Label', { true: 'large', false: 'small' })
```

**在存在有效对应关系的地方将 Figma 属性映射到代码属性。** Figma 属性和代码属性不一定 1:1 匹配——某些 Figma 属性直接映射（通过名称，或通过上述 API 方法），其他属性没有代码等效项。存在映射时使用它；没有匹配项时则省略 Figma 属性。绝对不要发出代码组件的 `Props` 接口未出现的属性名称的属性。

### 完全的变体处理

当 VARIANT 属性有多个可能的值时，`getEnum` 映射**必须列出 `get_context_for_code_connect` 返回的所有值**。不要省略值——未映射的值会静默返回 `undefined`，导致输出损坏。

```ts
// 错误的——省略了 'Warning'，它将渲染为 undefined
const status = instance.getEnum('Status', {
  'Success': 'success',
  'Error': 'error',
})

// 正确的——映射了每个值
const status = instance.getEnum('Status', {
  'Success': 'success',
  'Error': 'error',
  'Warning': 'warning',
  'Info': 'info',
})
```

当**两个或多个 VARIANT 属性组合**产生不同的代码输出时，生成完全的条件分支。例如，2 个变体 × 2 个值 = 4 个分支：

```ts
const type = instance.getEnum('Type', { 'Filled': 'filled', 'Outlined': 'outlined' })
const status = instance.getEnum('Status', { 'Success': 'success', 'Error': 'error' })

let colorClass
if (type === 'filled' && status === 'success') {
  colorClass = 'bg-green-500 text-white'
} else if (type === 'filled' && status === 'error') {
  colorClass = 'bg-red-500 text-white'
} else if (type === 'outlined' && status === 'success') {
  colorClass = 'bg-transparent border-green-500'
} else if (type === 'outlined' && status === 'error') {
  colorClass = 'bg-transparent border-red-500'
}
```

如果组合产生**重复**的输出（例如，`Size` 不改变代码片段结构——它只是作为属性传递），每个变体只需一个 `getEnum` 映射即可——无需交叉乘积分支。

**INSTANCE_SWAP** — 访问可交换组件实例：
```ts
const icon = instance.getInstanceSwap('Icon')
let iconCode
if (icon && icon.type === 'INSTANCE') {
  iconCode = icon.executeTemplate().example
}
```

**SLOT** — 仅当第 3 步中报告的 Figma 组件属性类型为 `SLOT` 时，才使用 `getSlot()`。对于 **INSTANCE_SWAP** 属性，使用 `getInstanceSwap()`（返回 `InstanceHandle`）。`getSlot()` 返回结构化的插槽部分，不是实例——永远不要对其返回值调用 `executeTemplate()`。

- **签名：** `getSlot(propName: string): ResultSection[] | undefined`
```ts
// Figma 属性 "Content" 在组件属性中必须是类型 SLOT
const content = instance.getSlot('Content')

export default {
  example: figma.code`<Card>${content}</Card>`,
  // ...
}
```

### 标记模板中的插值

在标记模板中插值值时，使用正确的包装：
- **字符串值** (`getString`, `getEnum`, `textContent`): 用引号包裹 → `variant="${variant}"`
- **实例/部分值** (`executeTemplate().example`): 用花括号包裹 → `icon={${iconCode}}`
- **插槽部分** (`getSlot()` 结果 — `ResultSection[] | undefined`): 直接在 `` figma.code`...` `` 内插值（与嵌套片段部分形状相同），例如 `` figma.code`<Select>${content}</Select>` `` — 不要将其视为普通字符串
- **布尔纯属性**: 使用条件 → `${disabled ? 'disabled' : ''}`

### 查找后代层

当您需要访问未作为组件属性暴露的子项时：

| 方法 | 使用场景 |
|---|---|
| `instance.getInstanceSwap('PropName')` | Figma 属性类型是 **INSTANCE_SWAP**（固定可交换的组件插槽） |
| `instance.getSlot('PropName')` | Figma 属性类型是 **SLOT**（自由内容区域） |
| `instance.findInstance('LayerName')` | 您知道子层名称（没有组件属性） |
| `instance.findText('LayerName')` → `.textContent` | 您需要从命名文本层获取文本内容 |
| `instance.findConnectedInstance('id')` | 您知道子组件的 Code Connect `id` |
| `instance.findConnectedInstances(fn)` | 您需要多个匹配过滤器的连接子项 |
| `instance.findLayers(fn)` | 您需要任何匹配过滤器的层（文本 + 实例） |

### 嵌套可配置实例

一个组件可能包含**未作为组件属性暴露**的子实例（没有 INSTANCE_SWAP），但它们仍然是**独立可配置**的——它们有自己的变体、属性或插槽。这些必须动态解析，而不是硬编码。

1. **检查子组件是否已经具有代码连接模板**——使用 `get_code_connect_suggestions` 或检查项目中的现有 `.figma.ts` 文件。
2. **如果不存在模板，为子组件创建一个**，以便它既可以独立渲染，也可以嵌套时正确渲染。
3. **从父组件引用子组件**，使用 `findInstance()` 或 `findConnectedInstance()`，然后调用 `executeTemplate()`。

```ts
// 父模板——Badge 子组件不是属性，但它可以配置
const badge = instance.findInstance('Status Badge')
let badgeCode
if (badge && badge.type === 'INSTANCE') {
  badgeCode = badge.executeTemplate().example
}

export default {
  example: figma.code`<Card>${badgeCode}</Card>`,
  // ...
}
```

这适用于图标、徽章、标签和任何其他可以自身配置的嵌套实例——始终连接它们并动态渲染，绝不硬编码其内容。

### 嵌套组件示例

对于多级嵌套组件或模板之间传递元数据，请参阅 [advanced-patterns.md](references/advanced-patterns.md)。

```ts
const icon = instance.getInstanceSwap('Icon')
let iconSnippet
if (icon && icon.type === 'INSTANCE') {
  iconSnippet = icon.executeTemplate().example
}

export default {
  example: figma.code`<Button ${iconSnippet ? figma.code`icon={${iconSnippet}}` : ''}>${label}</Button>`,
  // ...
}
```

### 条件属性

```ts
const variant = instance.getEnum('Variant', { 'Primary': 'primary', 'Secondary': 'secondary' })
const disabled = instance.getBoolean('Disabled')

export default {
  example: figma.code`
    <Button
      variant="${variant}"
      size="${size}"
      ${disabled ? 'disabled' : ''}
    >
      ${label}
    </Button>
  `,
  // ...
}
```

## 第 6 步：验证

读取 `.figma.ts` 文件并对照以下内容进行审查：

- **正确的文件类型和格式（首先检查此点）**——文件是 `ComponentName.figma.ts`（不是 `.figma.tsx`），其默认导出是一个使用 `` figma.code`...` `` 标记模板的无解析器模板。它**绝对不能**使用 `figma.connect()`（基于解析器的格式）。如果您编写了 `.figma.tsx` 或 `figma.connect()`，请丢弃它并重写为 `.figma.ts` `figma.code` 模板。
- **属性覆盖**——第 3 步中的每个 Figma 属性都应该在模板中得到处理。标记任何缺失的属性，并询问用户是否有意省略。
- **有效的、正确类型的代码**——所有发出的代码都必须是有效的，并且与代码组件的 `Props` 接口正确匹配。永远不要编造组件属性——如果一个 Figma 属性没有对应的代码属性，请省略它，而不是编造一个。
- **没有硬编码的子项**——验证每个 INSTANCE_SWAP 属性和子组件插槽都使用动态 API (`getInstanceSwap()`, `findInstance()`, `findConnectedInstance()` 等) 并调用 `executeTemplate()`。没有任何插槽应包含硬编码的组件内容。
- **规则和陷阱**——检查下面列出的常见错误（模板结果的字符串连接、不必要的 `hasCodeConnect()` 守卫、缺少 `type === 'INSTANCE'` 检查等）
- **插值包装**——字符串 (`getString`, `getEnum`, `textContent`) 用引号包裹，实例/部分值 (`executeTemplate().example`) 用花括号包裹，插槽部分 (`getSlot`) 作为片段部分在 `` figma.code`...` `` 内插值，布尔值使用条件

如果任何内容看起来不确定，请参考 [api.md](references/api.md) 获取 API 详细信息，并参考 [advanced-patterns.md](references/advanced-patterns.md) 获取复杂的嵌套。

## 内联快速参考

### `instance.*` 方法

| 方法 | 签名 | 返回 |
|---|---|---|
| `getString` | `(propName: string)` | `string` |
| `getBoolean` | `(propName: string, mapping?: { true: any, false: any })` | `boolean \| any` |
| `getEnum` | `(propName: string, mapping: { [figmaVal]: codeVal })` | `any` |
| `getInstanceSwap` | `(propName: string)` | `InstanceHandle \| null` |
| `getSlot` | `(propName: string)` | `ResultSection[] \| undefined` |
| `getPropertyValue` | `(propName: string)` | `string \| boolean` |
| `findInstance` | `(layerName: string, opts?: SelectorOptions)` | `InstanceHandle \| ErrorHandle` |
| `findText` | `(layerName: string, opts?: SelectorOptions)` | `TextHandle \| ErrorHandle` |
| `findConnectedInstance` | `(codeConnectId: string, opts?: SelectorOptions)` | `InstanceHandle \| ErrorHandle` |
| `findConnectedInstances` | `(selector: (node) => boolean, opts?: SelectorOptions)` | `InstanceHandle[]` |
| `findLayers` | `(selector: (node) => boolean, opts?: SelectorOptions)` | `(InstanceHandle \| TextHandle)[]` |

### InstanceHandle 方法

| 方法 | 返回 |
|---|---|
| `hasCodeConnect()` | `boolean` |
| `executeTemplate()` | `{ example: ResultSection[], metadata: Metadata }` |
| `codeConnectId()` | `string \| null` |

### TextHandle 属性

| 属性 | 类型 |
|---|---|
| `.textContent` | `string` |
| `.name` | `string` |

### SelectorOptions

```ts
{ path?: string[], traverseInstances?: boolean }
```

- `traverseInstances: true` — 当目标位于另一个嵌套实例内部时需要。如果没有它，`findInstance`/`findText` 仅搜索当前实例自己的层，并在嵌套实例边界处停止。
- `path: string[]` — 当多个后代具有相同层名时消除歧义。列出必须出现在到达目标路径上的父层名称。

**示例：**

```ts
// 层级结构:
//   A > C (instance) > "mychild"
// "mychild" 位于嵌套实例 C 内部，因此 plain findInstance 返回 ErrorHandle.
instance.findInstance('mychild', { traverseInstances: true })

// 层级结构:
//   A > C (instance) > "mychild"
//   A > D (instance) > "mychild"
// 两个 "mychild" 层存在——使用路径选择 C 下的一个。
instance.findInstance('mychild', { traverseInstances: true, path: ['C'] })
```

**当从父模板中深入到嵌套实例时:** 只有当父代码组件（来自第 4 步）将嵌套层作为其属性值本身（例如 `<C show={<B />} />` — A 将 B 传递给 C）时才这样做。如果父组件只是组合 C 并在 C 内部渲染 B，请使用 `executeTemplate()` 解析 C，并让 C 自己的模板处理 B——不要在父级别重复 B 的渲染。

### 导出结构

```ts
export default {
  example: figma.code`...`,                      // 必须的: ResultSection[]
  id: 'component-name',                         // 必须的: string
  imports: ['import { X } from "..."'],          // 可选: string[]
  metadata: { nestable: true, props: {} }        // 可选
}
```

## 规则和陷阱

1. **绝对不要连接模板结果进行字符串拼接。** `executeTemplate().example` 是 `ResultSection[]` 对象，不是字符串。使用 `+` 或 `.join()` 会导致 `[object Object]`。始终在标记模板中插值：`` figma.code`${snippet1}${snippet2}` ``

2. **不要使用 `hasCodeConnect()` 守卫。** 在 `type === 'INSTANCE'` 检查后，直接调用 `executeTemplate()`。运行时将自动处理没有 Code Connect 的实例。

   ```ts
   // 错误的——hasCodeConnect() 门禁会丢弃非 CC 实例
   if (icon && icon.type === 'INSTANCE' && icon.hasCodeConnect()) {
     iconCode = icon.executeTemplate().example
   }

   // 正确的——让运行时处理所有实例
   if (icon && icon.type === 'INSTANCE') {
     iconCode = icon.executeTemplate().example
   }
   ```

3. **在调用 `executeTemplate()` 之前检查 `type === 'INSTANCE'`。`findInstance()`, `findConnectedInstance()`, 和 `findText()` 在失败时返回 `ErrorHandle`（真值，但不是真正的节点）——不是 `null`。始终添加类型检查以避免崩溃: `if (child && child.type === 'INSTANCE') { ... }`

4. **优先使用 `getInstanceSwap()` 考虑到 `findInstance()`** 当组件属性存在插槽时。`findInstance('Star Icon')` 在图标被交换到不同名称时中断；`getInstanceSwap('Icon')` 无论插槽中的实例是什么，始终有效。

5. **仅当 Figma 属性类型为 `SLOT` 时使用 `getSlot()`。对于 **INSTANCE_SWAP** 属性，使用 `getInstanceSwap()`（返回 `InstanceHandle`）。`getSlot()` 返回结构化的插槽部分，不是实例——永远不要对其返回值调用 `executeTemplate()`。

6. **属性名区分大小写** 必须与 `get_context_for_code_connect` 返回的完全匹配。

7. **正确处理多个模板数组。** 当迭代子项时，为每个结果设置单独的变量并单独插值——不要使用 `.map().join()`:
   ```ts
   // 错误的:
   items.map(n => n.executeTemplate().example).join('\n')

   // 正确的——使用单独的变量:
   const child1 = items[0]?.executeTemplate().example
   const child2 = items[1]?.executeTemplate().example
   export default { example: figma.code`${child1}${child2}` }
   ```

7. **绝对不要硬编码插槽或子项内容。** 始终动态解析子实例——使用 `getInstanceSwap()` 对于 INSTANCE_SWAP 属性，使用 `findInstance()`/`findConnectedInstance()` 对于直接子项——并通过 `executeTemplate()` 渲染。永远不要从层名称构建 JSX（例如 `<StarIcon />`）或猜测导入路径。如果一个实例没有 Code Connect，请省略它——不要添加硬编码的回退。

   ```ts
   // 错误的——从层名称硬编码图标
   example: figma.code`<Button icon={<StarIcon />}>Submit</Button>`

   // 正确的——动态解析，适用于任何交换的图标
   const icon = instance.findInstance('Icon')
   let iconCode
   if (icon && icon.type === 'INSTANCE') {
     iconCode = icon.executeTemplate().example
   }
   example: figma.code`<Button${iconCode ? figma.code` icon={${iconCode}}` : ''}>...</Button>`
   ```

8. **尝试通过代码属性表示每个 Figma 属性。** 代码组件的 `Props` 接口（来自第 4 步）是权威的属性名列表。对于每个 Figma 属性，使用第 5 步中的 API 方法确定如何表示它——直接名称匹配、值转换或任何适合的匹配。如果没有任何代码属性匹配，请省略它——不要编造属性名。

## 完整示例

给定 URL: `https://figma.com/design/abc123/MyFile?node-id=42-100`

**第 1 步:** 解析 URL。
- `fileKey` = `abc123`
- `nodeId` = `42-100` → `42:100`

**第 2 步:** 调用 `get_code_connect_suggestions` 使用 `fileKey: "abc123"`, `nodeId: "42:100"`, `excludeMappingPrompt: true`.
响应返回一个组件，`mainComponentNodeId: "42:100"`。如果响应为空，请停止并通知用户。如果返回多个组件，请针对每个重复步骤 3–6。

**第 3 步:** 调用 `get_context_for_code_connect` 使用 `fileKey: "abc123"`, `nodeId: "42:100"`（来自第 2 步），`clientFrameworks: ["react"]`, `clientLanguages: ["typescript"]`。

响应包括属性：
- Label (TEXT)
- Variant (VARIANT): Primary, Secondary
- Size (VARIANT): Small, Medium, Large
- Disabled (BOOLEAN)
- Has Icon (BOOLEAN)
- Icon (INSTANCE_SWAP)

**第  or**
