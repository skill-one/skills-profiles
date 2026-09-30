---
name: stream
description: 流路由器用于聊天、视频、动态和内容审核。当用户想要使用流构建新应用、搭建项目、向现有应用添加聊天/视频/动态/内容审核功能、集成流、审核或迁移集成、为 Swift/SwiftUI/UIKit/iOS/Xcode/Android/Kotlin/React Native/Expo/Flutter 构建、查询流数据、列出频道、列出通话、显示被标记的消息、查找用户、运行 getstream CLI 命令、安装流 CLI、设置流、配置内容审核、搜索流 SDK 文档或查找流 React/iOS/Android/Node/Flutter/Unity SDK 方法时使用。根据任务将路由到正确的子技能。
---

# Stream - 技能路由器 + CLI

这个技能从用户的输入中挑选出相应的路径。构建（Web + 平台）和文档会分配到专门的子技能中；**CLI 任务 - 查询数据、配置应用、引导、安装技能 - 在这里处理**（见下文 Stream CLI 部分），因为 `getstream` CLI 是每个路径的基础。

> **首先阅读：** [`RULES.md`](RULES.md)。适用不可协商的规则，包括 **对等技能** 程序。[`peers.yaml`](peers.yaml)（模式：[`peers.schema.json`](peers.schema.json)）是对等名称、Glob 路径、安装命令和路由信号的单一事实来源。
>
> 根据其在 `peers.yaml` 中的策略按需安装缺失的对等技能（Glob 其路径，运行其安装命令 - `getstream skills <name>`），然后通过 `Skill` 工具调用或内联读取。在 Glob 之前不要调用 `Skill`，它会显示令人困惑的“未知技能”错误。命名路径后不要停止。

---

## 按任务划分

**在特定平台的 App 中构建或集成 Stream** -> 从 [`peers.yaml`](peers.yaml) 获取对等包（**首先检查对等信号**）
- 将用户输入或当前工作目录 (cwd) 与每个对等的 `signals` 进行匹配（例如 `swift` / `swiftui` / `.xcodeproj` -> `stream-swift`；`react native` / `expo` / `stream video react native` -> `stream-react-native`；`unreal` / `.uproject` / `umg` -> `stream-unreal`；`unity` / `monobehaviour` / `.unitypackage` -> `stream-unity`）
- 所有对等包按需安装 - 如果缺失则安装，然后路由，无需提示
- **SDK/引擎信号优先于 OS 目标信号。** 当两者都出现时，拥有 SDK 的包获胜：构建 iOS 的 Unreal 聊天应用是 `stream-unreal`（不是 `stream-swift`），Android 上的 Unity 游戏是 `stream-unity`（不是 `stream-android`）。`ios` / `android` / `xcode` / `gradle` 描述的是 *构建目标*；`unity` / `unreal` / `.uproject` / `.unitypackage` / `umg` / `flutter` / `react native` 描述的是 *SDK*。对于 `flutter` + `ios` 也适用相同规则。
- **为游戏请求命名引擎。** `stream-unreal` 和 `stream-unity` 都声称通用游戏短语（`in-game chat`，`game chat`）。显式的引擎标记决定结果；如果没有指定引擎标记且 cwd 中没有 `.uproject` / `ProjectSettings/`，则问一个简短的问题（“Unity 还是 Unreal？”）而不是猜测。注意答案所隐含的功能差异：Unity 具有 **聊天和视频**，Unreal 只有 **聊天**。
- **对等信号优先于下方的 Web 行。** 像请求“将视频通话添加到我的 Expo 应用”或“使用 Stream Video 搭建 React Native 应用”会匹配 `stream-react-native`，而不是 Web 包 - 平台标记获胜。

**使用 Stream（React / Next.js）构建/增强/审计/迁移 Web 应用** -> 使用 `stream-react` 技能（当没有其他平台信号时，这是默认的 Web 包）
- “为我构建一个 Chat/Video/Feeds 应用”，“搭建”，“创建一个新的...”，“将 Chat 添加到此应用”，“集成 Video”，“将 Feeds 添加到...”，“升级/迁移...到 vN” - 以及 **没有平台信号**（没有 `react native`，`expo`，`swift`，`ios`，`android` 等）
- React / Next.js 标记（`stream-chat-react`，`@stream-io/video-react-sdk`，`useCreateChatClient`，`MessageList`，...）与构建/集成动词也路由到这里
- 涵盖 Track A（搭建，步骤 0-7），Track E（增强现有项目），Track F（只读最佳实践审计），Track M（迁移/升级 SDK 版本）

**使用框架无关的构建器构建** -> 仅当用户明确指定使用时使用 `stream-builder` 技能（“使用 stream-builder”，`/stream-builder`）
- `stream-builder` 是一个通用的构建器，正在扩展到其他应用类型；Web React/Next.js 默认使用 `stream-react`（上文）

**根据最佳实践审计/审查现有的 Stream Video 集成**（只读 - 无搭建、无 CLI、无构建步骤）
- 对等信号（`react native` / `expo`）-> `stream-react-native`；Web / React / Next.js 或无平台信号 -> `stream-react`（Track F）
- **仅视频。** 专门的最佳实践审计涵盖 Stream **Video**。聊天/Feeds 目前还没有专门的审计清单 - `stream-react` 会用基于文档的通用审查来处理这些请求，并提前说明。
- 触发：`audit/review my video integration`，`is my video app production-ready`？`what am I missing before launch`？
- 即使请求中包含“检查”，也会路由到这里 - 审计意图优先于下方的 CLI “检查 {anything}”路由

**构建或审查 Feeds v2 到 v3 同步映射** -> 使用 `stream-feeds-migration` 技能
- “我们需要什么映射？”，“设置我们的 v2 到 v3 迁移”，“审查我们的 v3sync 映射”，“为什么迁移后的活动丢失了文本/附件/评论？”
- 通过采样 v2 应用的自身活动和反应来生成 `mapping` 配置对象 - 它不会构建或更改应用
- 需要在环境中提供 **v2** 应用的 API 密钥和密钥；参见技能的步骤 1 和 [`RULES.md`](RULES.md) > **密钥**

**查询 Stream 数据或运行 CLI 命令** -> 在这里处理（见下文 **Stream CLI** 部分）
- “列出通话”，“显示频道”，“任何已标记”，“查找用户”，一个字面的 `getstream` 命令，或“安装 CLI” / “设置 stream”

**搜索 Stream SDK 文档** -> 使用 `stream-docs` 技能
- “文档”，“documentation”，显式的 SDK 标记（`Chat React`，`Video iOS`，`Feeds Node`，`Moderation`）
- “如何在 {framework} 中...”，“{hook/component/method} 如何工作？”，“{SDK 事物} 是什么？”
- 如果请求是“如何在 {framework} 中添加/构建/集成/搭建 {X}”并且 `{framework}` 匹配对等信号，则对等行会获胜

---

## 选择路径

按顺序扫描用户的输入以查找下述信号。分类器是确定性的 - 没有探测，没有获取，此阶段没有 CLI 检查。

| 用户输入中的信号 | 路由 |
|---|---|
| **升级/迁移已安装的 SDK**（构建/集成意图 - 在文档行之前匹配）：“升级/迁移/bump/update `stream-chat-react` 到 vN”，“迁移到新的 SDK 版本”，“bump 我的 Stream 版本” - 升级动词（`upgrade`/`migrate`/`bump`/`update`）+ Stream 包标记，**没有对等信号**。对等信号（`react native` / `expo` / 一个 `@stream-io/*-react-native-*` 标记）-> `stream-react-native`（它自己的迁移流程） | `stream-react` (Track M) |
| **审计/审查现有集成**（只读 - 在文档标记/SDK 标记行下方匹配）：“audit/review my video integration”，“audit my Chat React integration”，“review my Video React app”，“is my video app production-ready`？”，“what am I missing before launch`？” - 审计/审查意图**即使存在 SDK 标记（如 `Chat React` / `Video React`）**。对等信号（`react native` / `expo`）-> `stream-react-native`；Web / React / Next.js 或无平台信号 -> `stream-react`（Track F - 视频**有专门的清单**；聊天/Feeds 会得到基于文档的通用审查，并提前说明）。**在请求包含最佳实践/生产就绪审查而不是数据查询时，此行会优先于下方的 CLI “检查 {anything}”行** | 匹配的平台包（只读审计） |
| 显式的 SDK/框架标记：`Chat React`，`Video iOS`，`Feeds Node`，`Moderation` 等（带或不带版本），并且**没有构建/集成动词和没有审计/审查意图**（`upgrade`/`migrate`/`bump`/`update`被视为构建/集成动词 -> 上述迁移行；`audit/review` -> 审计行） | `stream-docs` |
| “文档”或“documentation”字（并且没有构建/集成动词） | `stream-docs` |
| “如何在 {framework} 中 {X}？”，“{hook/component/method} 如何工作？”，“{SDK 事物} 是什么？” - 并且**没有构建/集成动词**。如果请求是“如何在 {framework} 中添加/构建/集成/搭建 {X}”并且 `{framework}` 匹配对等信号，则对等行会获胜 | `stream-docs` |
| 操作动词 + Stream 名词：`list calls`，`show channels`，`any flagged`，`find users`，一个字面的 `getstream` 命令（`getstream api`，`getstream init`，`getstream login`，...），或“安装 CLI” / “设置 stream” | **Stream CLI** - 在下方处理 |
| **构建/集成意图 + 匹配 [`peers.yaml`](peers.yaml) 中对等 `signals` 的标记**（例如 `swift` / `.xcodeproj` -> `stream-swift`；`react native` / `expo` / `stream video react native` / `stream video rn` -> `stream-react-native`；`unreal` / `ue5` / `.uproject` / `umg` -> `stream-unreal`；`unity` / `monobehaviour` / `.unitypackage` / `il2cpp` -> `stream-unity`）。**当存在对等信号时，此行会优先于下方的 Web `stream-react` 行，并且当请求包含对等信号和构建/集成动词时，此行会优先于上方的文档如何行**。注意：`react native` / `react-native`（以及 `@stream-io/*-react-native-*` 标记）是 `stream-react-native` 信号，会优先于 Web `react` 默认 - 包括对于升级/迁移/更新请求，RN 包会自行处理 | 匹配的对等（如果缺失则按需安装） |
| **字面提及 `stream-builder` / `/stream-builder`**（框架无关的构建器） | `stream-builder` |
| “为我构建一个 ... 应用”，“搭建”，“创建一个新的 ...” + Stream 产品，或 React/Next.js 标记（`stream-chat-react`，`@stream-io/video-react-sdk`，`useCreateChatClient`，...）+ 构建集成动词，**并且没有对等信号** | `stream-react`（Web/Next.js，当没有平台信号时，这是默认的） |
| “将 Chat/Video/Feeds 添加到此应用”，“集成 Stream 到”，“升级/迁移 ... 到 vN” - 现有项目，**并且没有对等信号** | `stream-react`（Web/Next.js，当没有平台信号时，这是默认的） |
| 包裹在如何行中的操作动词（例如“如何列出我的通话？” - 文档 *或* CLI） | **问一个澄清问题** |

**引导排除。** `stream-docs` 仅运行 `getstream docs` - 没有 `getstream init`，没有项目检查。**只读/本地仅路径也会跳过引导：** 平台包的**审计**路径（例如 `stream-react` Track F）和**迁移**路径（例如 `stream-react` Track M）仅检查/编辑本地文件和实时文档 - 它们**不会**配置组织/应用或调用 `getstream api`，因此它们不需要 CLI 引导。只有**构建/集成**工作（搭建一个新应用，将产品添加到现有应用）会运行 `getstream init` 在执行实际工作之前。

**文档与平台包。** 一个关于 iOS/Android 等SDK符号的纯如何行或方法查找问题会保留在 `stream-docs` 中 - 不要为文档答案引入平台包。平台包（例如 `stream-swift`）用于*构建或集成* - 搭建项目，连接包，生成视图。

**React 框架范围。** `stream-react` 搭建（Track A）一个 **Next.js** 应用。对于在**非 Next.js** 的 React 项目上增强/审计/迁移（Vite，CRA，Remix，TanStack Start，等）`stream-react` 仍然拥有它 - Stream SDK 连接是相同的 - 但代理必须调整 Next.js 特定的部分：服务器端标记路由存在于项目的自己的后端（不是 Next.js 的 `/api` 路由），验证使用项目的构建命令（`npm run build`），而不是 `next build`。永远不要假设非 Next.js 项目上的 Next.js API。

**澄清问题。** 如果输入符合多个行（通常操作动词 + 如何行），问一个简短的问题并等待。在得到答案之前不要探测：

> 要我查找 SDK 方法（文档）还是通过 CLI 运行它？

得到答案后，就像用户直接给出了该信号一样进行路由。

**裸 `/stream` 无参数。** 渲染“快速导航”下的菜单**逐字**，然后等待：

> **Stream** - Chat - Video - Feeds - Moderation。告诉我你想要什么，或直接选择一个技能：
>
> **核心**
> - `/stream-react` - 使用 Stream 搭建、增强、审计或迁移 React / Next.js Web 应用（Web 的默认选择） - 例如 *"构建一个聊天应用"*
> - `/stream-docs` - 通过 `getstream docs` 查找 SDK 文档，带引用 - 例如 *"useChannel 如何工作？"*
> - `/stream-builder` - 框架无关的构建器（Web 默认为 `/stream-react`；仅当明确指定时选择此技能）
> - `/stream-feeds-migration` - 从您的应用的实时数据构建 v2 -> v3 Feeds 同步映射 - 例如 *"我们需要什么映射？"*
>
> **平台 SDKs**
> - `/stream-swift` - Swift - SwiftUI - UIKit - iOS
> - `/stream-android` - Android - Jetpack Compose - Kotlin
> - `/stream-react-native` - React Native - Expo
> - `/stream-flutter` - Flutter - Dart
> - `/stream-unity` - Unity 引擎 - C#（聊天 + 视频）
> - `/stream-unreal` - Unreal 引擎 - C++ - Blueprint（仅聊天）
>
> 或直接提问 - 查询数据或直接运行 `getstream` 命令：*"列出我的频道"*。对某个技能不熟悉？只需描述任务，我会自动安装正确的技能。

结束语是承重：输入未安装的斜杠命令会在路由器运行之前显示“未知技能”错误，因此自然语言描述是唯一无死路的路径 - 它会路由到这里，并且缺失的对等会根据 [`peers.yaml`](peers.yaml) 按需安装。保持此菜单与 `peers.yaml` 同步：每个在此处 Core 或 Platform SDKs 下出现的对等都会出现在这里，当添加新平台时，其条目会添加到 Platform SDKs 下。

---

## 交接

见前言：如果缺失则安装，通过 `Skill` 工具调用，不要停止。跨切规则在 [`RULES.md`](RULES.md) 中适用于每个子技能，包括 **跨路径后续操作**（提供，不要自动执行，跨路径边界的自然下一步操作）。

---

## 支持

如果用户询问支持或如何联系某人，请将他们引导至 [getstream.io/contact](https://getstream.io/contact/)。
