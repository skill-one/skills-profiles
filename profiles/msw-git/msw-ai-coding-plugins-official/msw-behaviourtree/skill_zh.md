# MSW 行为树

用于 MSW `.behaviourtree` 文件的端到端编写技能。拥有**项目特定**的编写规范（`<项目根目录>/.behaviourDocs/bt-spec.md`）以及树生成本身。固定的图规则和骨架结构位于此技能的 `references/` 目录中；每个项目的规范由此技能的本地 `scripts/build-spec.cjs` 脚本（重新）构建。

---

## 🚦 执行顺序（请按此顺序执行）

### 0. 构建/刷新项目规范（`bt-spec.md`）

规范是**每个项目特定数据点的真实来源**：每个自定义动作/装饰器/组合节点的 `definitionId`、`btNodeType`、可见的 `propertyKey` 名称，以及标记到此项目 `CoreVersion` 的序列化 `Type.type` 字符串。

**何时（重新）构建：**

- 在项目中第一次处理 BT（还没有 `.behaviourDocs/bt-spec.md`）。
- 在任何影响 BT 节点表面的更改之后：
  - 新增/重命名/删除的 `.codeblock`，其配对的 `.mlua` 扩展了 `ActionNode` / `DecoratorNode` / `CompositeNode`
  - 在此类 `.mlua` 中添加/删除/重命名的 `property` 行
  - `Environment/config` 中的 `CoreVersion` 更新（序列化类型字符串是版本标记的）。
- 用户表示他们最近添加/更改了 BT 代码块或 `.mlua` 属性——过时的 UUID/缺失的属性会默默地产生损坏的树。
- 下游验证（步骤 7）标记了 `definitionId`、`propertyKey` 或版本不匹配。

**如何运行** — 调用此技能的本地脚本：

```bash
node "scripts/build-spec.cjs" --projectRoot "<MSW 项目根目录>"
```

如果当前工作目录已经是 MSW 项目根目录，可以省略 `--projectRoot`。需要在 `PATH` 上有 Node.js（没有其他依赖项——纯 stdlib `fs`/`path`）。

可选覆盖（长标志，不区分大小写）：

| 标志 | 默认值 | 备注 |
|------|---------|-------|
| `--projectRoot` | 当前工作目录 | 要扫描的 MSW 项目根目录 |
| `--outputPath` | `<项目根目录>/.behaviourDocs/bt-spec.md` | 如果缺失，将创建此文件夹 |
| `--coreVersion` | 从 `<项目根目录>/Environment/config`（`CoreVersion` 字段）读取 | 如果配置缺失，则需要 |

带有覆盖的示例：

```bash
node "scripts/build-spec.cjs" --projectRoot "C:/path/to/project" --coreVersion 26.7.0.0
```

如果 `Environment/config` 缺失且未传递 `--coreVersion`，脚本会抛出错误——没有回退默认值。

**规范包含的内容：**

1. 项目元数据——项目根目录、`CoreVersion`、生成时间、发现的节点计数。
2. 组合节点——内置名称具有固定的 `definitionId` / `btNodeType`，以及发现的自定义组合（`.mlua` 声明 `extends CompositeNode`）。
3. 自定义动作节点——`Name`、`definitionId`、`btNodeType`、可见的属性名称。
4. 自定义装饰器节点——与动作节点形状相同。
5. 类型映射——mlua 类型到序列化的 `MODNativeType.type` 字符串以及 Blackboard `ObjectValue` 形状。

UUID 来自项目中的真实 `.codeblock` 文件——规范永远不会凭空创造它们。`@HideFromInspector` 属性会自动过滤掉。固定的编写规则、文件骨架和验证清单位于此技能的 `references/` 目录中，而不是生成的规范中。

**（重新）构建后**，读取新写入的 `<项目根目录>/.behaviourDocs/bt-spec.md` 并继续执行下面的步骤。紧凑的规范有意仅列出属性名称；在构建 `nodeProperties` 时，从配对的 `.mlua` 文件中解析每个属性的 mlua 类型/默认值，然后使用 `bt-spec.md` §4 中的类型映射来获取 `propertyType.type`。

另外，请阅读 [`references/skeleton-minimal.json`](references/skeleton-minimal.json) 以获取最小的有效树，[`references/skeleton-full.json`](references/skeleton-full.json) 以获取带有所有可选字段填充的 Composite+Decorator+Action+Blackboard 示例，[`references/node-catalog.md`](references/node-catalog.md) 以获取固定的图规则，以及项目中任何现有的 `.behaviourtree`（`**/*.behaviourtree`）以模仿约定。将 `{CORE_VERSION}` 替换为骨架中的 `CoreVersion`——在顶层**和** Blackboard 变量以及 `nodeProperties` 中的每个 `MOD.Core.*` 类型字符串中。

### 1. 从用户收集输入

通过上下文确认，或者在模糊的情况下通过 AskUserQuestion 询问：

| 项目 | 描述 | 示例 |
|------|-------------|---------|
| `name` | 树的显示名称 | `"PatrolAndChase"` |
| 保存路径 | `.behaviourtree` 位置（相对于项目根目录） | `RootDesk/MyDesk/PatrolAndChase.behaviourtree` |
| 树形状 | 预期的节点图（根组合 + 子节点） | `Sequence → [Chase, MoveTo]` |
| 自定义节点 | 树引用的动作/装饰器/组合代码块 | `Chase`、`MoveTo`、`Jump` |
| Blackboard 变量 | 变量名称 + 类型 + 初始值 | `TargetEntity: Entity`、`MoveSpeed: number = 10.0` |
| 节点属性 | 对于每个自定义节点，哪个属性映射到哪个 Blackboard 变量 | `Chase.TargetEntityKey = "TargetEntity"` |

**自定义节点存在性检查（强制）**：用户提到的每个自定义动作/装饰器/组合名称都必须出现在 `bt-spec.md` §1 / §2 / §3 中。如果引用的节点不在规范中，**停止**并询问用户——不要凭空创造 UUID，不要假设节点按名称存在，也不要跳过重新运行步骤 0。

### 2. 创造 UUID

您需要：

- 一个用于文件的 UUID → 放入 `EntryKey` 和 `ContentProto.Json.id`（两者相同，都以前缀 `behaviourtree://` 开头）。
- 每个 `Nodes` 中的节点（`nodeId`）需要一个 UUID。

```bash
node -e "console.log(require('node:crypto').randomUUID())"
```

提前创造，写入到临时表格中，然后组装。不要将文件 UUID 作为 `nodeId` 重复使用。

### 3. 解析每个 `definitionId`

| 节点类别 | `definitionId` 值 | `btNodeType` |
|---------------|----------------------|--------------|
| 内置组合（`SequenceNode`、`SelectorNode`、`ParallelNode`） | 与 `nodeName` 相同的字符串 | `1` |
| 自定义组合节点（`extends CompositeNode`） | 来自 `bt-spec.md` §1 的值 | `1` |
| 自定义动作节点 | 来自 `bt-spec.md` §2 的值 | `0` |
| 自定义装饰器节点 | 来自 `bt-spec.md` §3 的值 | `2` |

自定义节点的 UUID 来自 `bt-spec.md`（它从真实的 `.codeblock` 文件中读取它们）——从不依赖任何其他来源。

### 4. 构建 Blackboard

对于每个变量，逐字复制 `Type.type` 字符串和 `ObjectValue` 形状来自 `bt-spec.md` §4。版本标记的子字符串（`Version=<CoreVersion>`）必须完全匹配——一个拼写错误会默默地破坏反序列化。

`Variables` 是一个有序数组；每个条目：`{ Name, Type: { "$type": "MODNativeType", type: "<来自规范>" }, ObjectValue: <来自规范> }`。`ObjectValue` **不包括** `$type` 判别器（与 `.model` 文件中的 `Value` 不同）。

对于 `Component` / `ComponentRef`，`ComponentId` 是 `<entity-uuid>:<ComponentName>`（引擎组件）或 `<entity-uuid>:<scriptCodeblockUuid>:<ScriptComponentName>`（脚本组件）。模仿项目中现有的序列化示例。

数值 `ObjectValue` 使用浮点字面量形式（`3.0`，而不是 `3`）。

> **运行时注意事项**：Blackboard 存在于入口的树中。如果任何脚本稍后调用 `AIComponent:SetRootNode(...)` 在该组件上，则入口树和此 Blackboard 都会被丢弃——`BlackBoard` 读取 `nil`，`*Key` 属性停止解析。不要将运行时根交换与依赖 Blackboard 的树混合。

### 4.5 解析节点属性值

对于需要 `nodeProperties` 的每个自定义节点：

1. 确认 `propertyKey` 在 `bt-spec.md` §1 / §2 / §3 中对该节点存在。
2. 通过搜索项目下 `script <NodeName> extends ActionNode`、`extends DecoratorNode` 或 `extends CompositeNode` 找到配对的 `.mlua`。如果多个文件匹配，优先选择其兄弟 `.codeblock` 具有来自 `bt-spec.md` 的确切 `definitionId` UUID 的文件；如果仍然模糊，请询问用户。
3. 读取该 `.mlua` 中可见的 `property` 声明，忽略 `@HideFromInspector` 属性。这给出了 mlua 类型 和 默认值。
4. 仅当用户提供了值、行为需要非默认值，或者必须指向 Blackboard 变量的 `*Key` 属性时，才包含 `nodeProperties` 条目。可以安全地使用 `.mlua` 默认值而省略可选属性。
5. 对于 `*Key` 字符串属性，将 `propertyValue` 设置为 Blackboard 变量的名称。通过名称和 getter 使用推断变量时（`MoveSpeedKey` -> `MoveSpeed`，`TargetEntityKey` -> `TargetEntity`）。如果可能匹配多个 Blackboard 变量，请询问。
6. 对于字面量属性，使用用户提供的值。如果没有提供值并且 `.mlua` 默认值有意义，则省略属性，而不是序列化猜测的值。
7. 如果 `OnBehave` 检查属性为 `nil`、空字符串或无效枚举并且无法推断值，请在写入树之前询问用户。

`nodeProperties` 条目形状：

```json
{
  "propertyKey": "<属性名称>",
  "propertyType": { "$type": "MODNativeType", "type": "<来自规范>" },
  "propertyValue": <值>
}
```

### 5. 组装节点

硬图约束（在写入之前验证）：

- **根节点不是父节点。** 它不能有 `childNodes`。它仅存储 `startNodeId`，并且 `startNodeId` 指向 `Nodes` 中**恰好一个**节点。
- 如果树需要多个顶层行为，请使用一个组合作为单个 `startNodeId`，或者使用一个装饰器作为单个 `startNodeId`，其 `decoChildNodes` 包装一个组合或另一个装饰器链，该链最终包装一个组合。将多个行为放在该组合的 `childNodes` 下。
- `Nodes` 中**恰好一个**节点的 `nodeParentId` 为 `""`：由 `RootNode.startNodeId` 引用的节点。不要创建多个根级 Action/Composite/Decorator 节点。
- **组合**（`btNodeType: 1`）是唯一可以拥有多个子节点的节点类别通过 `childNodes`。
- **装饰器**（`btNodeType: 2`）仅是一个包装/父节点，用于**恰好一个**动作、组合或装饰器节点。它也可以是另一个装饰器的子节点，因此装饰器到装饰器的链是有效的。它必须使用单数的 `decoChildNodes`（单个 `nodeId` 字符串——`ChildNodeId` 是遗留变体；编辑器在往返过程中会删除它），该 ID 指向**恰好一个**动作、组合或装饰器子节点，其 `nodeParentId` 指向装饰器。装饰器到装饰器的父/子链是有效的，并且必须使用相同的 `decoChildNodes` ↔ `nodeParentId` 规则进行检查。
- **应用于同一动作的装饰器必须链接——永远不要扁平化为兄弟。** 每个装饰器拥有**恰好一个**下游子树。如果两个或多个装饰器旨在门控/修改同一动作，请构建单个链 `Composite → ADeco → BDeco → … → Action`，其中每个装饰器的 `decoChildNodes` 指向下一个装饰器（最后指向动作）。具体来说：**在通往单个动作的单个链中，没有两个装饰器可以共享相同的 `nodeParentId` 值**——每个装饰器的父节点是前一个装饰器，而不是已经出现在链中的另一个装饰器。同一链中的两个装饰器共享 `nodeParentId` 是无效的。（在单个组合下的兄弟装饰器仍然有效，当它们包装*不同的*下游子树时。）✅ `Composite → ADeco → BDeco → CDeco → Action`（链——链中的每个装饰器都有唯一的父节点）。❌ `Composite → [ADeco→Action, BDeco→Action, CDeco→Action]`（动作重复以绕过链接）。❌ `Composite → [ADeco, BDeco, CDeco, Action]`（装饰器扁平化——它们没有包装动作并且实际上是孤儿）。
- **动作**（`btNodeType: 0`）是叶子节点——永远不会拥有子节点。

节点写入不变量：

- 每个 `nodeId` 在文件中是唯一的。
- 每个非根节点的 `nodeParentId` 指向一个真实的 `nodeId`，该 `nodeId` 是组合或装饰器。它永远不会指向 `RootNode`，因为 `RootNode` 没有在 `Nodes` 中表示为节点。
- 如果节点的父节点是组合，则该组合必须包含节点 ID 在 `childNodes` 中。
- 如果节点的父节点是装饰器，则该装饰器的 `decoChildNodes` 必须等于该节点的 `nodeId`。即使父节点和子节点都是装饰器，这也是有效的。
- 组合 `childNodes` ↔ 子节点的 `nodeParentId` 是**双向一致的**。
- 动作节点省略 `childNodes`。装饰器节点省略 `childNodes`，并使用**恰好一个** `decoChildNodes`（单个 `nodeId` 字符串——`ChildNodeId` 是遗留变体；编辑器在往返过程中会删除它），该 ID 指向**恰好一个**动作、组合或装饰器子节点，其 `nodeParentId` 指向装饰器。装饰器到装饰器的父/子链是有效的，并且必须使用相同的 `decoChildNodes` ↔ `nodeParentId` 规则进行检查。
- **装饰器链规则**：当多个装饰器应用于同一动作时，它们形成一个单链（`Composite → ADeco → BDeco → … → Action`）。通过向上遍历每个动作到其包含的组合来验证：沿该单一路径遇到的装饰器必须具有*唯一的* `nodeParentId` 值（即每个装饰器的父节点是前一个装饰器，永远不会是链中已经出现的另一个装饰器）。同一链中的两个装饰器共享 `nodeParentId` 是无效的。（在单个组合下的兄弟装饰器在它们包装*不同的*下游子树时仍然有效——唯一性是按链，而不是全局的。）
- 没有节点序列化 `"probability"`。（遗留 `1.0` 值可能在读取时出现，但永远不会编写。）
- 每个组合和动作都带有对象形式的 `nodePosition` `{ "x": <num>, "y": <num> }`，使用浮点字面量——写入时不会出现遗留的 `"(x.xxx, y.yyy)"` 字符串。**装饰器节点根本不携带 `nodePosition`。**
- **起始节点不与 RootNode 锚点堆叠。** `RootNode.nodePosition` 是 `{ "x": 0.0, "y": 0.0 }`，由 `startNodeId` 引用的节点具有 `y ≤ -200.0`（通常 `{ "x": 0.0, "y": -200.0 }`）。如果起始节点是装饰器（没有 `nodePosition`），则链中的第一个包装的 Composite/Action 必须满足此偏移量。
- 没有节点序列化空数组——没有子节点的组合省略 `childNodes`；没有覆盖的节点省略 `nodeProperties`。不要编写 `"childNodes": []` 或 `"nodeProperties": []`。
- 每个自定义节点的 `definitionId` 都是从 `bt-spec.md` 复制的（永远不会凭空创造）。
- 每个 `nodeProperties[].propertyKey` 与该节点的 `bt-spec.md` 中的属性匹配。
- 每个 `*Key` 属性的 `propertyValue` 与正确类型的 `Blackboard.Variables[].Name` 匹配。
- 每个类型字符串都逐字复制自 `bt-spec.md` §4——版本标记的，容易因拼写错误而破坏。
- **版本交叉检查**：每个 `MOD.Core.*` 类型字符串的 `Version=X.Y.Z.Z` 子字符串（在 `Blackboard.Variables[].Type.type` 和 `Nodes[].nodeProperties[].propertyType.type` 中）等于文件的顶层 `CoreVersion`。不匹配会默默地破坏反序列化——当 `bt-spec.md` 与项目的当前 `CoreVersion` 相对于过时时很常见。如果它们不同，**在写入之前重新运行步骤 0**。(`System.*` 类型使用不可变的 `Version=4.0.0.0` 并被豁免。）
- JSON 解析：
  ```bash
  node -e "JSON.parse(require('node:fs').readFileSync(process.argv[1],'utf8'))" "<路径>"
  ```

如果任何检查失败，请在报告完成之前修复它。

---

## 📂 此技能中的文件（被此技能消耗）

- [`scripts/build-spec.cjs`](scripts/build-spec.cjs) — 扫描项目并输出 `<项目根目录>/.behaviourDocs/bt-spec.md` 的 Node.js 脚本。在步骤 0 中调用。
- `<项目根目录>/.behaviourDocs/bt-spec.md` — 紧凑生成的目录。**真实来源**对于节点名称、`definitionId`、`btNodeType`、属性名称和类型字符串。由上面的脚本写入；被步骤 1–7 消耗。
- [`references/skeleton-minimal.json`](references/skeleton-minimal.json) — 最小的有效树（空 Blackboard，单个无子节点的 Composite 根）。
- [`references/skeleton-full.json`](references/skeleton-full.json) — Composite → Decorator → Action，带有 `nodeProperties`（字面量 + `Key`-后缀）和填充的 `Blackboard`。当树非空时，使用此形状参考。
- [`references/node-catalog.md`](references/node-catalog.md) — `btNodeType` 值、有效图形状、`Key`-后缀约定的说明，以及规范构建器如何发现节点（保留以供参考；运行时目录本身位于 `bt-spec.md` 中）。

---

## 🔁 编辑工作流（现有文件）

1. 读取整个文件——永远不要盲目编辑。UUID 和父/子图必须保持一致。
2. 永远不要更改文件的包装 UUID（`EntryKey` / `ContentProto.Json.id`）——外部引用会中断。
3. 添加节点：创造一个新鲜的 `nodeId`，追加到 `Nodes`，更新父组合的 `childNodes`，设置新节点的 `nodeParentId`。
4. 删除节点：从 `Nodes` 中删除，从任何组合的 `childNodes` 中删除其 ID。如果它是一个组合，请决定是否重新父节点或删除其子节点——永远不要留下悬空的 `nodeParentId` 引用。
5. 如果编辑涉及项目自上次构建规范以来可能已更改的自定义节点名称、属性或类型，请**首先重新运行步骤 0**。
6. 在每次编辑后重新运行步骤 7 的验证清单。
