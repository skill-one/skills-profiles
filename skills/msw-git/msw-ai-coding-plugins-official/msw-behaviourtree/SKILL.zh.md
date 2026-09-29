---
name: msw-behaviourtree
description: 作者维护MSW的`.behaviourtree`文件端到端，并保持项目特定的编写规范（`.behaviourDocs/bt-spec.md`）。扫描每个`.codeblock`，其配对的`.mlua`扩展了`ActionNode`/`DecoratorNode`/`CompositeNode`，以构建一个紧凑的自定义动作/装饰器/组合UUID、属性键名和带版本标记的MODNativeType字符串的目录。然后生成完整的树：RootNode → 节点图、黑板变量、节点属性连接，并自我验证父子一致性。触发：'创建行为树'、'新建BT'、'添加行为树'、'BT节点图'、'비헤이비어 트리 만들어'、'.behaviourtree 생성'、'SequenceNode SelectorNode'、'黑板变量'、'definitionId codeblock'、'startNodeId'、'构建BT规范'、'刷新bt-spec'、'生成行为树目录'、'BT 스펙 생성'、'bt-spec.md 만들어'、'重新扫描BT节点'。
---

# MSW 行为树

MSW `.behaviourtree` 文件的端到端编写技能。拥有项目特定的编写规范 (`<项目根目录>/.behaviourDocs/bt-spec.md`) 以及树生成本身。固定的图规则和骨架文件位于此技能的 `references/` 目录中；每个项目的规范由此技能的本地 `scripts/build-spec.cjs` 脚本构建（或重新构建）。

---

## 🚦 执行顺序（请按此顺序执行）

### 0. 构建/刷新项目规范 (`bt-spec.md`)

规范是每个项目特定数据点的**事实来源**：每个自定义动作/装饰器/组合节点的 `definitionId`、`btNodeType`、可见的 `propertyKey` 名称，以及标记到此项目的 `CoreVersion` 的序列化 `Type.type` 字符串。

**何时（重新）构建：**

- 首次在一个项目中处理 BT（还没有 `.behaviourDocs/bt-spec.md`）。
- 在影响 BT 节点表面的任何更改之后：
  - 新增/重命名/删除的 `.codeblock`，其配对的 `.mlua` 扩展了 `ActionNode` / `DecoratorNode` / `CompositeNode`
  - 在这样的 `.mlua` 中添加/删除/重命名的 `property` 行
  - `Environment/config` 中的 `CoreVersion` 被提升（序列化的类型字符串带有版本标签）。
- 用户声称最近添加/更改了 BT 代码块或 `.mlua` 属性 — 过期的 UUID / 缺失的属性会静默地产生损坏的树。
- 下游验证（步骤 7）标记了 `definitionId`、`propertyKey` 或版本不匹配。

**如何运行** — 调用此技能的本地脚本：

```bash
node "scripts/build-spec.cjs" --projectRoot "<MSW 项目根目录>"
```

如果当前工作目录已经是 MSW 项目根目录，可以省略 `--projectRoot`。需要在 `PATH` 上有 Node.js（没有其他依赖项 — 纯粹使用 stdlib `fs`/`path`）。

可选覆盖（长标志，不区分大小写）：

| 标志 | 默认值 | 备注 |
|------|---------|-------|
| `--projectRoot` | 当前工作目录 | 要扫描的 MSW 项目根目录 |
| `--outputPath` | `<项目根目录>/.behaviourDocs/bt-spec.md` | 如果文件夹不存在，则会创建 |
| `--coreVersion` | 从 `<项目根目录>/Environment/config` (`CoreVersion` 字段) 读取 | 如果配置缺失，则需要 |

带有覆盖的示例：

```bash
node "scripts/build-spec.cjs" --projectRoot "C:/path/to/project" --coreVersion 26.7.0.0
```

如果 `Environment/config` 缺失且未传递 `--coreVersion`，则脚本会抛出错误 — 没有可回退的默认值。

**规范包含的内容：**

1. 项目元数据 — 项目根目录、`CoreVersion`、生成时间、发现的节点计数。
2. 组合节点 — 带有固定 `definitionId` / `btNodeType` 的内置名称，以及发现的自定义组合（`.mlua` 声明 `extends CompositeNode`）。
3. 自定义动作节点 — `Name`、`definitionId`、`btNodeType`、可见的属性名称。
4. 自定义装饰器节点 — 与动作节点形状相同。
5. 类型映射 — mlua 类型到序列化的 `MODNativeType.type` 以及 Blackboard `ObjectValue` 形状。

UUID 来自项目中的真实 `.codeblock` 文件 — 规范永远不会凭空创建它们。`@HideFromInspector` 属性会自动过滤掉。固定的编写规则、文件骨架和验证清单位于此技能的 `references/` 目录中，而不是生成的规范中。

**（重新）构建后**，读取新写入的 `<项目根目录>/.behaviourDocs/bt-spec.md` 并继续执行下面的步骤。紧凑的规范有意仅列出属性名称；在构建 `nodeProperties` 时，从配对的 `.mlua` 文件中解析每个属性的 mlua 类型/默认值，然后使用 `bt-spec.md` §4 中的类型映射来获取 `propertyType.type`。

另外，请阅读 [`references/skeleton-minimal.json`](references/skeleton-minimal.json) 获取最小的有效树，[`references/skeleton-full.json`](references/skeleton-full.json) 获取带有所有可选字段填充的 Composite+Decorator+Action+Blackboard 示例，[`references/node-catalog.md`](references/node-catalog.md) 获取固定的图规则，以及项目中的任何现有 `.behaviourtree` 文件（`**/*.behaviourtree`）以模仿规范。将骨架中的 `{CORE_VERSION}` 替换为 `bt-spec.md` 中的 `CoreVersion` — 两者在顶层 **和** Blackboard 变量以及 `nodeProperties` 中的 `MOD.Core.*` 类型字符串中都必须匹配。

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

**自定义节点存在性检查（强制执行）：** 用户提到的每个自定义动作/装饰器/组合名称都必须出现在 `bt-spec.md` §1 / §2 / §3 中。如果引用的节点不在规范中，**停止**并询问用户 — 不要凭空创建 UUID，不要通过名称假设节点存在，也不要跳过重新运行步骤 0。

### 2. 创造 UUID

您需要：

- 一个用于文件的 UUID → 放入 `EntryKey` 和 `ContentProto.Json.id`（两者相同，两者都以 `behaviourtree://` 开头）。
- 每个 `Nodes` 中的节点（`nodeId`）都需要一个 UUID。

```bash
node -e "console.log(require('node:crypto').randomUUID())"
```

提前创造，写入到临时表格中，然后组装。不要将文件 UUID 作为 `nodeId` 重复使用。

### 3. 解析每个 `definitionId`

| 节点类别 | `definitionId` 值 | `btNodeType` |
|---------------|----------------------|--------------|
| 内置组合节点 (`SequenceNode`、`SelectorNode`、`ParallelNode`) | 与 `nodeName` 相同的字符串 | `1` |
| 自定义组合节点（`extends CompositeNode`） | 来自 `bt-spec.md` §1 的值 | `1` |
| 自定义动作节点 | 来自 `bt-spec.md` §2 的值 | `0` |
| 自定义装饰器节点 | 来自 `bt-spec.md` §3 的值 | `2` |

自定义节点的 UUID 来自 `bt-spec.md`（它从真实的 `.codeblock` 文件中读取它们）— 从来不是任何其他来源。

### 4. 构建 Blackboard

对于每个变量，逐字复制 `Type.type` 字符串和 `ObjectValue` 形状来自 `bt-spec.md` §4。版本标记的子字符串（`Version=<CoreVersion>`）必须完全匹配 — 一个拼写错误会静默地破坏反序列化。

`Variables` 是一个有序数组；每个条目：`{ Name, Type: { "$type": "MODNativeType", type: "<来自规范>" }, ObjectValue: <来自规范> }`。`ObjectValue` **不包括** `$type` 判别器（与 `.model` 文件中的 `Value` 不同）。

对于 `Component` / `ComponentRef`，`ComponentId` 是 `<实体-uuid>:<ComponentName>`（引擎组件）或 `<实体-uuid>:<脚本CodeblockUuid>:<ScriptComponentName>`（脚本组件）。模仿项目中的已序列化示例。

数值 `ObjectValue` 使用浮点字面量形式（`3.0`，而不是 `3`）。

> **运行时注意事项：** Blackboard 存储在入口的树中。如果稍后任何脚本调用 `AIComponent:SetRootNode(...)` 在该组件上，则入口树和此 Blackboard 都会被丢弃 — `BlackBoard` 读取 `nil`，`*Key` 属性停止解析。不要将运行时根交换与依赖 Blackboard 的树混合。

### 4.5 解析节点属性值

对于需要 `nodeProperties` 的每个自定义节点：

1. 确认 `propertyKey` 在 `bt-spec.md` §1 / §2 / §3 中对该节点存在。
2. 通过在项目中搜索 `script <NodeName> extends ActionNode`、`extends DecoratorNode` 或 `extends CompositeNode` 下找到配对的 `.mlua`。如果多个文件匹配，优先选择其兄弟 `.codeblock` 具有来自 `bt-spec.md` 的确切 `definitionId` UUID 的文件；如果仍然模糊，询问用户。
3. 读取该 `.mlua` 中的可见 `property` 声明，忽略 `@HideFromInspector` 属性。这提供了 mlua 类型 和 默认值。
4. 仅当用户提供了值、行为需要非默认值，或者 `*Key` 属性必须指向 Blackboard 变量时，才包含 `nodeProperties` 条目。可以安全地使用 `.mlua` 默认值省略可选属性。
5. 对于 `*Key` 字符串属性，将 `propertyValue` 设置为 Blackboard 变量名称。通过名称和 getter 使用推断变量（`MoveSpeedKey` -> `MoveSpeed`，`TargetEntityKey` -> `TargetEntity`）。如果可能匹配多个 Blackboard 变量，询问。
6. 对于字面量属性，使用用户提供的值。如果没有提供值且 `.mlua` 默认值有意义，则省略属性，而不是序列化猜测的值。
7. 如果 `OnBehave` 检查属性为 `nil`、空字符串或无效枚举且无法推断值，则在写入树之前询问用户。

`nodeProperties` 条目形状：

```json
{
  "propertyKey": "<属性名称>",
  "propertyType": { "$type": "MODNativeType", "type": "<来自规范 §4>" },
  "propertyValue": <值>
}
```

### 5. 组装节点

硬图约束（在写入之前验证）：

- **根节点不是父节点。** 它不能有 `childNodes`。它仅存储 `startNodeId`，并且 `startNodeId` 指向 `Nodes` 中的**一个**节点。
- 如果树需要多个顶层行为，请使用一个组合作为单个 `startNodeId`，或者使用一个装饰器作为单个 `startNodeId`，其 `decoChildNodes` 包装一个组合或另一个装饰器链，该链最终包装一个组合。将多个行为放在该组合的 `childNodes` 下。
- `Nodes` 中恰好有一个节点的 `nodeParentId: ""`：由 `RootNode.startNodeId` 引用的节点。不要创建多个根级 Action/组合/装饰器节点。
- **组合** (`btNodeType: 1`) 是唯一可以拥有多个子节点的节点类别，通过 `childNodes`。
- **装饰器** (`btNodeType: 2`) 仅是恰好一个动作、组合或装饰器节点的包装/父节点。它也可以是另一个装饰器的子节点，因此装饰器到装饰器的链是有效的。它必须使用单数的 `decoChildNodes`（单个 `nodeId` 字符串）来指向该子节点；包装的子节点也必须在它的 `nodeParentId` 中记录装饰器的 ID。
- **应用于同一动作的装饰器必须链接 — 永远不要将它们作为兄弟扁平化。** 每个装饰器拥有恰好一个下游子树。如果两个或多个装饰器旨在门控/修改同一动作，请构建单个链 `Composite → ADeco → BDeco → CDeco → Action`，其中每个装饰器的 `decoChildNodes` 指向下一个装饰器（最后指向动作）。具体来说：**在指向单个动作的单个链中，没有两个装饰器可以共享相同的 `nodeParentId`** — 每个装饰器的父节点是前一个装饰器，只有最顶层的装饰器的父节点是组合。一个组合下的兄弟装饰器仍然有效，因为它们包装了*不同的*下游子树。 ✅ `Composite → ADeco → BDeco → CDeco → Action`（链 — 链中的每个装饰器都有一个唯一的父节点）。 ❌ `Composite → [ADeco→Action, BDeco→Action, CDeco→Action]`（动作重复以绕过链接）。 ❌ `Composite → [ADeco, BDeco, CDeco, Action]`（装饰器扁平化 — 它们不包装动作且实际上是无家可归的）。
- **动作** (`btNodeType: 0`) 是叶子节点 — 永远不会有子节点。

节点写入不变量：

- 每个 `nodeId` 在文件中是唯一的。
- 每个非根节点的 `nodeParentId` 指向一个真实的 `nodeId`，该 `nodeId` 是组合或装饰器。它永远不会指向 `RootNode`，因为 `RootNode` 不会作为节点在 `Nodes` 中表示。
- 如果一个节点的父节点是组合，则该组合必须在其 `childNodes` 中包含该节点 ID。
- 如果一个节点的父节点是装饰器，则该装饰器的 `decoChildNodes` 必须等于该节点的 `nodeId`。即使父节点和子节点都是装饰器，这也是有效的。
- 组合 `childNodes` ↔ 子节点 `nodeParentId` 是**双向一致的**。
- 动作节点省略 `childNodes`。装饰器节点省略 `childNodes` 并使用恰好一个 `decoChildNodes`（单个字符串 `nodeId`）代替。
- **永远不要写入 `probability`。** 编辑器在往返过程中会删除此字段，并且支持的组合（`SequenceNode`、`SelectorNode`、`ParallelNode`）不会消耗每个子节点的权重。项目中的较旧生成的树可能仍然在每个节点上携带 `"probability": 1.0`；在读取时将其视为遗留项，但在新节点上不要写入它。
- **装饰器节点（`btNodeType: 2`）省略 `nodePosition`。** 编辑器会自动相对于它包装的子节点定位装饰器，并且在保存时不会为它写入 `nodePosition` 字段。只有组合和动作包含 `nodePosition`。`RootNode` 块也携带自己的 `nodePosition`（与其起始节点分开）。- `RootNode.nodePosition`: `{ "x": 0.0, "y": 0.0 }`（固定锚点 — 永远不会移动）- 起始节点（深度 1，由 `startNodeId` 引用）: `{ "x": 0.0, "y": -200.0 }`- 起始节点的单个子节点（深度 2）: `{ "x": 0.0, "y": -400.0 }`- 起始节点的两个子节点（深度 2）: `{ "x": -100.0, "y": -400.0 }` 和 `{ "x": 100.0, "y": -400.0 }`- 每个附加级别: parent.y − 200`

编写 JSON 文件，然后运行此检查清单。具体要求如下：

- [ ] `EntryKey` 必须是 `behaviourtree://{uuid}`，且与 `ContentProto.Json.id` 完全一致。
- [ ] 顶层 `Id`、`GameId`、`Content` 必须为 `""`。`Usage`、`UseService`、`DynamicLoading` 必须为 `0`。`UsePublish` 必须为 `1`。`CoreVersion` 必须与项目 (`Environment/config`) 匹配。`StudioVersion` 必须是 `0.1.0.0`。`ContentType` 必须是 `x-mod/behaviourtree`。`ContentProto.Use` 必须是 `Json`。
- [ ] `RootNode` 没有子节点 (`childNodes`)；`RootNode.startNodeId` 必须与 `Nodes` 中完全匹配的一个 `nodeId` 相同；该起始节点必须具有 `nodeParentId: ""`；且没有其他节点具有 `nodeParentId: ""`。
- [ ] 每个 `nodeParentId` 必须是 `""` 或一个已存在的 `nodeId`。
- [ ] 所有 `nodeId` 值必须唯一。
- [ ] 对于每个 Composite，其 `childNodes` ID 集合必须等于其 `nodeParentId` 为该 Composite 的节点集合。
- [ ] 每个 Action 没有子节点 (`childNodes`)。每个 Decorator 没有子节点，且恰好有一个 `decoChildNodes`（单个 `nodeId` 字符串——`ChildNodeId` 是遗留变体；编辑器在往返过程中会移除它），该 ID 必须指向恰好一个 Action、Composite 或 Decorator 子节点，其 `nodeParentId` 指向该 Decorator。Decorator 之间的父子链是有效的，必须使用相同的 `decoChildNodes` ↔ `nodeParentId` 规则进行检查。
- [ ] **Decorator 链规则**：当多个 Decorator 应用于同一个 Action 时，它们会形成一个单一的链（`Composite → ADeco → BDeco → … → Action`）。通过逐个向上遍历 Action 到其包含的 Composite 来验证：在该路径上遇到的 Decorator 必须具有 *唯一* 的 `nodeParentId` 值（即每个 Decorator 的父节点是前一个 Decorator，而不是链中已出现的另一个 Decorator）。同一链中的两个 Decorator 共享 `nodeParentId` 是无效的。（在同一个 Composite 下作为兄弟节点包裹 *不同* 下游子树的情况是允许的——唯一性是针对链的，而不是全局的。）
- [ ] 没有节点序列化 `"probability"`。（遗留的 `1.0` 值可能在读取时出现，但永远不会被编写。）
- [ ] 每个 Composite 和 Action 必须携带对象形式的 `nodePosition` `{ "x": <num>, "y": <num> }`，使用浮点字面量——写入时不允许遗留的 `"(x.xxx, y.yyy)"` 字符串。**Decorator 节点完全不携带 `nodePosition`。**
- [ ] **起始节点不堆叠在 RootNode 锚点上。** `RootNode.nodePosition` 必须是 `{ "x": 0.0, "y": 0.0 }`，且 `startNodeId` 引用的节点必须满足 `y ≤ -200.0`（通常为 `{ "x": 0.0, "y": -200.0 }`）。如果起始节点是 Decorator（没有 `nodePosition`），则链中的第一个 Composite/Action 必须满足此偏移量。
- [ ] 没有节点序列化空数组——没有子节点的 Composite 会省略 `childNodes`；没有重写的节点会省略 `nodeProperties`。不要编写 `"childNodes": []` 或 `"nodeProperties": []`。
- [ ] 每个自定义节点的 `definitionId` 必须从 `bt-spec.md` 复制（永远不会凭空创造）。
- [ ] 每个 `nodeProperties[].propertyKey` 必须与该节点在 `bt-spec.md` 中的属性匹配。
- [ ] 每个 `*Key` 属性的 `propertyValue` 必须与 `Blackboard.Variables[].Name` 的正确类型匹配。
- [ ] 每个类型字符串必须从 `bt-spec.md` §4 原封不动地复制——带版本标签，易受拼写错误影响。
- [ ] **版本交叉检查**：每个 `MOD.Core.*` 类型字符串的 `Version=X.Y.Z.Z` 子字符串（在 `Blackboard.Variables[].Type.type` 和 `Nodes[].nodeProperties[].propertyType.type` 中）必须与文件顶层的 `CoreVersion` 相等。不匹配会静默地破坏反序列化——当 `bt-spec.md` 相对于项目的当前 `CoreVersion` 过时时常见。如果它们不同，**在编写前重新运行步骤 0**。 (`System.*` 类型使用不可变的 `Version=4.0.0.0`，并豁免。）
- [ ] JSON 解析：
  ```bash
  node -e "JSON.parse(require('node:fs').readFileSync(process.argv[1],'utf8'))" "<path>"
  ```

如果任何检查失败，请在报告完成前修复它。

---

## 📂 /consumed by this skill 中的文件

- [`scripts/build-spec.cjs`](scripts/build-spec.cjs) — 扫描项目并输出 `<ProjectRoot>/.behaviourDocs/bt-spec.md` 的 Node.js 脚本。在步骤 0 中调用。
- `<ProjectRoot>/.behaviourDocs/bt-spec.md` — 紧凑生成的目录。**事实来源**，用于节点名称、`definitionId`、`btNodeType`、属性名称和类型字符串。由上述脚本编写；被步骤 1–7 消费。
- [`references/skeleton-minimal.json`](references/skeleton-minimal.json) — 最小的有效树（空的 Blackboard，单个无子节点的 Composite 根节点）。
- [`references/skeleton-full.json`](references/skeleton-full.json) — Composite → Decorator → Action，带有 `nodeProperties`（字面量 + `Key`-后缀）和填充的 `Blackboard`。当树非空时，使用此形状作为参考。
- [`references/node-catalog.md`](references/node-catalog.md) — `btNodeType` 值的叙述性解释、有效图形状、`Key`-后缀约定以及规范构建器如何发现节点的说明（保留以供参考；运行时目录本身位于 `bt-spec.md` 中）。

---

## 🔁 现有文件的编辑工作流

1. 读取整个文件——切勿盲目编辑。UUID 和父子图必须保持一致。
2. 切勿更改文件的包装 UUID（`EntryKey` / `ContentProto.Json.id`）——外部引用会中断。
3. 添加节点：生成一个新的 `nodeId`，追加到 `Nodes`，更新父 Composite 的 `childNodes`，设置新节点的 `nodeParentId`。
4. 删除节点：从 `Nodes` 中删除，从任何 Composite 的 `childNodes` 中删除其 ID。如果它是 Composite，请决定是否重新父化或删除其子节点——切勿留下悬空的 `nodeParentId` 引用。
5. 如果编辑涉及可能自上次规范构建以来在项目中更改的自定义节点名称、属性或类型，请**首先重新运行步骤 0**。
6. 每次编辑后重新运行步骤 7 的验证检查清单。
