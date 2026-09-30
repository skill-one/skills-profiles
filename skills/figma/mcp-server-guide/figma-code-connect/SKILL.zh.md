---
name: figma-code-connect
description: 创建和维护 Figma Code Connect 模板文件，用于将 Figma 组件映射到代码片段。当用户提及 Code Connect、Figma 组件映射、设计到代码的转换，或要求创建/更新 .figma.ts 或 .figma.js 文件时使用。
---

# 代码连接

## 概述

创建代码连接模板文件（`.figma.ts`），将 Figma 组件映射到代码片段。给定一个 Figma URL，按照以下步骤创建模板。

> **您只需编写 `.figma.ts` 模板文件——绝不能编写 `.figma.tsx`。** 此技能生成 *无解析器模板*：一个 `.figma.ts` 文件，其默认导出使用 `` figma.code`...` `` 标记模板。**不要**编写 `.figma.tsx` 文件，**不要**使用 `figma.connect()`——那是**基于解析器**的代码连接格式（以不同方式发布），并且是此技能的**错误工件**；以 `.figma.tsx` 编写的输出将被直接拒绝。如果组件已经存在 `.figma.tsx`，请保持其原样，并在旁边添加您的 `.figma.ts` 模板。一个功能强大的模型可能会倾向于从记忆中寻找更熟悉的 `.figma.tsx` / `figma.connect()` 模式——请抵制它；在这里，正确的输出始终是 **`.figma.ts` + `figma.code`**。

## 前置条件

- **必须连接 Figma MCP 服务器**——在继续之前，请验证 Figma MCP 工具（例如，`get_code_connect_suggestions`）是否可用。如果不可用，请指导用户启用 Figma MCP 服务器并重新启动他们的 MCP 客户端。
- **组件必须已发布**——代码连接仅适用于已发布到 Figma 团队库的组件。如果组件未发布，请告知用户并停止。
- **需要组织或企业计划**——代码连接在免费或专业计划上不可用。
- **URL 必须包含 `node-id`**——Figma URL 必须包含 `node-id` 查询参数。
- **TypeScript 类型**——对于 `.figma.ts` 文件中的编辑器自动完成和类型检查，必须将 `@figma/code-connect/figma-types` 添加到 `tsconfig.json` 中的 `types`：
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

用户提供的 URL 可能指向框架、实例或变体——不一定是指令集或独立组件。使用 MCP 工具 `get_code_connect_suggestions` 并提供：
- `fileKey` — 来自第 1 步
- `nodeId` — 来自第 1 步（冒号格式）
- `excludeMappingPrompt` — `true`（返回未映射组件的轻量级列表）

此工具识别选择中尚未具有代码连接映射的已发布组件。

**处理响应：**

- **"在此选择中未找到已发布的组件"** — 节点不包含已发布的组件。告知用户他们需要将组件发布到 Figma 团队库，然后停止。
- **"此选择中的所有组件实例均已通过代码连接连接"** — 一切都已映射。告知用户并停止。
- **正常响应包含组件列表** — 为每个返回的组件提取 `mainComponentNodeId`。使用这些解析的节点 ID（而不是 URL 中的原始 ID）进行后续所有步骤。如果返回多个组件（例如，用户选择了一个包含多个不同组件实例的框架），请对每个组件重复步骤 3–6。

## 第 3 步：获取组件属性

使用 MCP 工具 `get_context_for_code_connect` 并提供：
- `fileKey` — 来自第 1 步
- `nodeId` — 来自第 2 步的解析 `mainComponentNodeId`
- `clientFrameworks` — 根据 `figma.config.json` `parser` 字段确定（例如 `"react"` → `["react"]`）
- `clientLanguages` — 根据项目文件扩展名推断（例如 TypeScript 项目 → `["typescript"]`，JavaScript → `["javascript"]`）

对于多个组件，为每个节点 ID 调用该工具。

响应包含 Figma 组件的**属性定义**——注意每个属性的名字和类型：
- **TEXT** — 文本内容（标签、标题、占位符）
- **BOOLEAN** — 开关（显示/隐藏图标、禁用状态）
- **VARIANT** — 枚举选项（大小、变体、状态）
- **INSTANCE_SWAP** — 与特定组件绑定的可交换嵌套实例（图标、头像）
- **SLOT** — 可变内容区域（自由布局、混合子元素）；在模板中使用 `getSlot()`（与 INSTANCE_SWAP 不同）

保存此属性列表——您将在第 5 步中使用它来编写模板。

## 第 4 步：确定代码组件

如果用户未指定要连接的代码组件：

1. 检查 `figma.config.json` 中的 `paths` 和 `importPaths` 以找到组件的位置
2. 在代码库中搜索与 Figma 组件名称匹配的组件。如果 `figma.config.json` 未指定路径，请检查常见目录（`src/components/`、`components/`、`lib/ui/`、`app/components/`）
3. 读取候选文件并比较它们的 props 接口与第 3 步中的 Figma 属性——查找匹配的变体类型、大小选项、布尔标志和插槽属性
4. 如果有多个候选者匹配，选择与 props 接口最接近的一个，并向用户解释您的推理
5. 如果未找到匹配项，请显示 2 个最接近的候选者并要求用户确认或提供正确路径

**在继续到第 5 步之前与用户确认。** 展示匹配项：您找到的代码组件、其位置以及为什么匹配（props 对应、命名、目的）。

读取 `figma.config.json` 以获取导入路径别名——`importPaths` 部分将 glob 模式映射到导入规范，而 `paths` 部分将那些规范映射到目录。

读取代码组件的源代码以了解其 props 接口——这有助于在第 5 步中将 Figma 属性映射到代码 props。

## 第 5 步：创建模板文件（.figma.ts）

### 文件位置

将文件与现有的代码连接文件放在一起。检查 `figma.config.json` `include` 模式以找到正确的目录。**命名它 `ComponentName.figma.ts`——绝不能是 `ComponentName.figma.tsx`。** `.figma.tsx` 扩展名是基于解析器的格式；不要创建一个或修改现有的一个。

### 模板结构

每个模板文件遵循此结构：

```ts
// url=https://www.figma.com/file/{fileKey}/{fileName}?node-id={nodeId}
// source={从第 4 步获取的代码组件路径}
// component={从第 4 步获取的代码组件名称}
import figma from 'figma'
const instance = figma.selectedInstance

// 从 Figma 组件中提取属性（见属性映射下文）
// ...

export default {
  example: figma.code`<Component ... />`,       // 必须项：代码片段
  imports: ['import { Component } from "..."'], // 可选项：导入语句
  id: 'component-name',                         // 必须项：唯一标识符
  metadata: {                                    // 可选项
    nestable: true,                              // true = 在父级中内联，false = 作为药丸显示
    props: {}                                    // 父级模板可访问的数据
  }
}
```

### 属性映射

使用第 3 步的属性列表提取值。对于每个 Figma 属性类型，使用相应的方法：

| Figma 属性类型 | 模板方法 | 使用场景 |
|---|---|---|
| TEXT | `instance.getString('Name')` | 标签、标题、占位符文本 |
| BOOLEAN | `instance.getBoolean('Name', { true: ..., false: ... })` | 切换可见性、条件 props |
| VARIANT | `instance.getEnum('Name', { 'FigmaVal': 'codeVal' })` | 大小、变体、状态枚举 |
| INSTANCE_SWAP | `instance.getInstanceSwap('Name')` | 固定组件插槽的可交换实例（然后 `hasCodeConnect()` / `executeTemplate()`）- 不要与下面的 SLOT 属性混淆 |
| SLOT | `instance.getSlot('Name')` | 仅当 Figma 属性类型为 **SLOT** 时，获取自由布局插槽内容 |
| (子层) | `instance.findInstance('LayerName')` | 无组件属性的命名子实例 |
| (文本层) | `instance.findText('LayerName')` → `.textContent` | 从命名文本层获取文本内容 |

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

// 映射到代码值（例如，当代码 prop 是枚举而不是布尔值时）
const size = instance.getBoolean('Show Label', { true: 'large', false: 'small' })
```

**将 Figma 属性映射到代码 props，只要存在有效对应关系。** Figma 属性和代码 props 不总是 1:1 匹配——某些 Figma 属性直接映射（通过名称，或通过上述 API 方法），其他属性没有代码等效项。存在映射时使用它；否则忽略 Figma 属性，而不是发明代码 prop。绝不要发出代码组件的 `Props` 接口中未出现的属性名称的属性。

### 完全的变体处理

当 VARIANT 属性有多个可能值时，`getEnum` 映射**必须列出所有返回的值**，由 `get_context_for_code_connect` 返回。不要遗漏值——未映射的值会静默返回 `undefined`，导致输出损坏。

```ts
// 错误——遗漏了 'Warning'，它将渲染为 undefined
const status = instance.getEnum('Status', {
  'Success': 'success',
  'Error': 'error',
})

// 正确——映射了所有值
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

如果组合产生**重复**的输出（例如，`Size` 不改变片段结构——它只是作为 prop 传递），每个变体使用一个 `getEnum` 映射就足够了——不需要交叉乘积分支。

**INSTANCE_SWAP** — 访问可交换组件实例：
```ts
const icon = instance.getInstanceSwap('Icon')
let iconCode
if (icon && icon.type === 'INSTANCE') {
  iconCode = icon.executeTemplate().example
}
```

**SLOT** — `getSlot(propName)` 仅在 Figma 组件属性（第 3 步报告）的类型为 **`SLOT`** 时有效。不要使用 `getSlot()` 为 **INSTANCE_SWAP** 属性（它们使用 `getInstanceSwap()`）。插槽是组件定义中的明确“内容区域”，而不是通用嵌套实例。

- **签名：** `getSlot(propName: string): ResultSection[] | undefined`
```ts
// Figma 属性 "Content" 在组件属性中必须是 SLOT 类型
const content = instance.getSlot('Content')

export default {
  example: figma.code`<Card>${content}</Card>`,
  // ...
}
```

### 标记模板中的插值

在标记模板中插值值时，使用正确的包装：
- **字符串值** (`getString`、`getEnum`、`textContent`)：用引号包裹 → `variant="${variant}"`
- **实例/部分值** (`executeTemplate().example`)：用大括号包裹 → `icon={${iconCode}}`
- **插槽部分** (`getSlot()` 结果 — `ResultSection[] | undefined`)：直接在 `` figma.code`...` `` 内插值（与嵌套片段部分形状相同），例如 `` figma.code`<Select>${content}</Select>` `` — 不要将其视为普通字符串
- **布尔裸 props**：使用条件 → `${disabled ? 'disabled' : ''}`

### 查找后代层

当您需要访问未作为组件属性暴露的子元素时：

| 方法 | 使用场景 |
|---|---|
| `instance.getInstanceSwap('PropName')` | Figma 属性类型为 **INSTANCE_SWAP**（固定可交换实例） |
| `instance.getSlot('PropName')` | Figma 属性类型为 **SLOT**（自由布局内容区域） |
| `instance.findInstance('LayerName')` | 您知道子层名称（无组件属性） |
| `instance.findText('LayerName')` → `.textContent` | 您需要从命名文本层获取文本内容 |
| `instance.findConnectedInstance('id')` | 您知道子元素的代码连接 `id` |
| `instance.findConnectedInstances(fn)` | 您需要匹配过滤器的多个连接子元素 |
| `instance.findLayers(fn)` | 您需要匹配任何过滤器匹配的层 |

### 嵌套可配置实例

组件可能包含**未作为组件属性暴露**的子实例（没有 INSTANCE_SWAP），但它们仍然是**独立可配置**的——它们有自己的变体、属性或插槽。必须动态解析，而不是硬编码。

1. **检查子实例是否已有代码连接模板**——使用 `get_code_connect_suggestions` 或检查项目中的现有 `.figma.ts` 文件。
2. **如果没有模板，为子实例创建一个**，以便它既可独立渲染也可嵌套正确渲染。
3. **从父级引用子实例**，使用 `findInstance()` 或 `findConnectedInstance()`，然后调用 `executeTemplate()`。

```ts
// 父级模板——Badge 子组件不是 prop，但它可配置
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

这适用于图标、徽章、标签和任何其他可独立配置的嵌套实例——始终连接它们并动态渲染，永远不要硬编码其内容。

### 嵌套组件示例

对于多级嵌套组件或模板之间传递元数据 prop，请参阅 [advanced-patterns.md](references/advanced-patterns.md)。

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

### 条件 props

```ts
const variant = instance.getEnum('Variant', { 'Primary': 'primary', 'Secondary': 'secondary' })
const disabled = instance.getBoolean('Disabled')

export default {
  example: figma.code`
    <Button
      variant="${variant}"
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

- **正确文件类型和格式（请首先检查此点**）— 文件是 `ComponentName.figma.ts`（不是 `.figma.tsx`），其默认导出是一个无解析器的模板，使用 `` figma.code`...` `` 标记模板。它必须不使用 `figma.connect()`（基于解析器的格式）。如果你写了 `.figma.tsx` 或 `figma.connect()`，请丢弃它并重写为 `.figma.ts` `figma.code` 模板。
- **属性覆盖** — 第 3 步中的每个 Figma 属性都应该在模板中得到体现。标记任何缺失的属性，并询问用户是否有意省略。
- **有效、正确类型的代码** — 所有生成的代码必须有效且正确地与代码组件的 `Props` 接口匹配。不要编造组件属性 — 如果 Figma 属性没有对应的代码属性，则省略它而不是编造一个。
- **无硬编码的子元素** — 验证每个 INSTANCE_SWAP 属性和子组件插槽都使用动态 API (`getInstanceSwap()`、`findInstance()`、`findConnectedInstance()` 等) 与 `executeTemplate()`。没有插槽应包含硬编码的组件内容。
- **规则和陷阱** — 检查下面列出的常见错误（模板结果的字符串连接、不必要的 `hasCodeConnect()` 防护、缺少 `type === 'INSTANCE'` 检查等）
- **插值包装** — 用引号包裹的字符串 (`getString`、`getEnum`、`textContent`)，用大括号包裹的实例/部分值 (`executeTemplate().example`)，插槽部分 (`getSlot`) 作为片段部分在 `` figma.code`...` `` 内插值，布尔值使用条件语句

如果任何内容看起来不确定，请参考 [api.md](references/api.md) 获取 API 详细信息，并参考 [advanced-patterns.md](references/advanced-patterns.md) 获取复杂嵌套的说明。

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

- `traverseInstances: true` — 当目标位于另一个嵌套实例内部时需要。没有它，`findInstance`/`findText` 仅搜索当前实例自己的层，并在嵌套实例边界处停止。
- `path: string[]` — 当多个后代共享相同层名时用于消除歧义。列出必须出现在目标路径上的父层名。

**示例：**

```ts
// 层级结构：
//   A > C (实例) > "mychild"
// "mychild" 位于嵌套实例 C 内部，因此普通的 findInstance 返回 ErrorHandle。
instance.findInstance('mychild', { traverseInstances: true })

// 层级结构：
//   A > C (实例) > "mychild"
//   A > D (实例) > "mychild"
// 两个 "mychild" 层存在 — 使用路径选择 C 下面的那个。
instance.findInstance('mychild', { traverseInstances: true, path: ['C'] })
```

**何时从父模板深入到嵌套实例**：仅当父代码组件（来自第 4 步）本身将嵌套层作为属性值时（例如 `<C show={<B />} />` — A 将 B 传递给 C）。如果父组件只是组合 C 并在 C 内部渲染 B，则使用 `executeTemplate()` 解析 C 并让 C 自己的模板处理 B — 不要在父级别重复 B 的渲染。

### 导出结构

```ts
export default {
  example: figma.code`...`,                      // 必须的：ResultSection[]
  id: 'component-name',                         // 必须的：string
  imports: ['import { X } from "..."'],          // 可选的：string[]
  metadata: { nestable: true, props: {} }        // 可选的
}
```

## 规则和陷阱

1. **永远不要字符串连接模板结果。** `executeTemplate().example` 是一个 `ResultSection[]` 对象，不是字符串。使用 `+` 或 `.join()` 产生 `[object Object]`。始终在标记模板内插值：`` figma.code`${snippet1}${snippet2}` ``

2. **不要使用 `hasCodeConnect()` 防护。** 在 `type === 'INSTANCE'` 检查后，直接对任何实例调用 `executeTemplate()`。运行时会自动处理没有 Code Connect 的实例。

   ```ts
   // 错误 — hasCodeConnect() 门禁会丢弃非 CC 实例
   if (icon && icon.type === 'INSTANCE' && icon.hasCodeConnect()) {
     iconCode = icon.executeTemplate().example
   }

   // 正确 — 让运行时处理所有实例
   if (icon && icon.type === 'INSTANCE') {
     iconCode = icon.executeTemplate().example
   }
   ```

3. **在调用 `executeTemplate()` 前检查 `type === 'INSTANCE'`。** `findInstance()`、`findConnectedInstance()` 和 `findText()` 在失败时返回 `ErrorHandle`（真值，但不是真实的节点）— 不是 `null`。始终添加类型检查以避免崩溃：`if (child && child.type === 'INSTANCE') { ... }`

4. **在组件属性存在插槽时，优先使用 `getInstanceSwap()` 而不是 `findInstance()`。** `findInstance('Star Icon')` 在图标被重命名为不同名称时失效；`getInstanceSwap('Icon')` 无论插槽中的实例是什么，始终有效。

5. **仅当 Figma 属性类型为 `SLOT` 时使用 `getSlot()`。** 对于 **INSTANCE_SWAP** 属性，使用 `getInstanceSwap()`（返回 `InstanceHandle`）。`getSlot()` 返回结构化的插槽部分，不是实例 — 永远不要对其返回值调用 `executeTemplate()`。

6. **属性名区分大小写**，必须与 `get_context_for_code_connect` 返回的值完全匹配。

7. **正确处理多个模板数组。** 在迭代子元素时，将每个结果设置在不同的变量中并单独插值 — 不要使用 `.map().join()`：
   ```ts
   // 错误：
   items.map(n => n.executeTemplate().example).join('\n')

   // 正确 — 使用单独的变量：
   const child1 = items[0]?.executeTemplate().example
   const child2 = items[1]?.executeTemplate().example
   export default { example: figma.code`${child1}${child2}` }
   ```

7. **永远不要硬编码插槽或子元素内容。** 始终动态解析子实例 — 对于 INSTANCE_SWAP 属性使用 `getInstanceSwap()`，对于直接子元素使用 `findInstance()`/`findConnectedInstance()` — 并通过 `executeTemplate()` 渲染。永远不要从层名（例如 `<StarIcon />`）构建 JSX 或猜测导入路径。如果实例没有 Code Connect，则省略它 — 不要添加硬编码的回退。

   ```ts
   // 错误 — 从其层名硬编码图标
   example: figma.code`<Button icon={<StarIcon />}>Submit</Button>`

   // 正确 — 动态解析，适用于任何交换的图标
   const icon = instance.findInstance('Icon')
   let iconCode
   if (icon && icon.type === 'INSTANCE') {
     iconCode = icon.executeTemplate().example
   }
   example: figma.code`<Button${iconCode ? figma.code` icon={${iconCode}}` : ''}>...</Button>`
   ```

8. **尝试通过代码属性表示每个 Figma 属性。** 代码组件的 `Props` 接口（来自第 4 步）是属性名的权威列表。对于每个 Figma 属性，找出使用第 5 步的 API 方法（直接名称匹配、值转换或任何适合的方式）表示它的正确方法。如果根本没有适合的代码属性，则省略它 — 不要编造属性名。

## 完整示例

给定 URL: `https://figma.com/design/abc123/MyFile?node-id=42-100`

**第 1 步**：解析 URL。
- `fileKey` = `abc123`
- `nodeId` = `42-100` → `42:100`

**第 2 步**：调用 `get_code_connect_suggestions`，参数为 `fileKey: "abc123"`，`nodeId: "42:100"`，`excludeMappingPrompt: true`。
响应返回一个组件，其中 `mainComponentNodeId: "42:100"`。如果响应为空，停止并通知用户。如果返回多个组件，则重复第 3-6 步为每个组件执行。

**第 3 步**：调用 `get_context_for_code_connect`，参数为 `fileKey: "abc123"`，`nodeId: "42:100"`（来自第 2 步），`clientFrameworks: ["react"]`，`clientLanguages: ["typescript"]`。

响应包括属性：
- 标签 (TEXT)
- 变体 (VARIANT): 主要、次要
- 尺寸 (VARIANT): 小、中、大
- 禁用 (BOOLEAN)
- 是否有图标 (BOOLEAN)
- 图标 (INSTANCE_SWAP)

**第 4 步**：搜索代码库 → 找到 `Button` 组件。阅读其源代码以确认属性：`variant`、`size`、`disabled`、`icon`、`children`。导入路径：`"primitives"`。

**第 5 步**：创建 `src/figma/primitives/Button.figma.ts`：

```ts
// url=https://figma.com/design/abc123/MyFile?node-id=42-100
// source=src/components/Button.tsx
// component=Button
import figma from 'figma'
const instance = figma.selectedInstance

const label = instance.getString('Label')
const variant = instance.getEnum('Variant', {
  'Primary': 'primary',
  'Secondary': 'secondary',
})
const size = instance.getEnum('Size', {
  'Small': 'sm',
  'Medium': 'md',
  'Large': 'lg',
})
const disabled = instance.getBoolean('Disabled')
const hasIcon = instance.getBoolean('Has Icon')
const icon = hasIcon ? instance.getInstanceSwap('Icon') : null
let iconCode
if (icon && icon.type === 'INSTANCE') {
  iconCode = icon.executeTemplate().example
}

export default {
  example: figma.code`
    <Button
      variant="${variant}"
      size="${size}"
      ${disabled ? 'disabled' : ''}
      ${iconCode ? figma.code`icon={${iconCode}}` : ''}
    >
      ${label}
    </Button>
  `,
  imports: ['import { Button } from "primitives"'],
  id: 'button',
  metadata: { nestable: true }
}
```

**第 6 步**：读取文件以验证语法。

## 额外参考

对于高级模式（多级嵌套组件、`findConnectedInstances` 过滤、父/子模板之间的元数据属性传递）：

- [api.md](references/api.md) — 完整 Code Connect API 参考
- [advanced-patterns.md](references/advanced-patterns.md) — 高级嵌套、元数据属性和后代模式
