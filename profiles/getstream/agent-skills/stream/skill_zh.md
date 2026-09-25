# Stream - 技能路由器 + 命令行界面

这个技能从用户的输入中挑选出相应的路径。构建（Web + 平台）和文档会分配到专门的子技能；**CLI 任务 - 查询数据、配置应用、引导设置、安装技能 - 在这里处理**（见下文 Stream CLI），因为 `getstream` CLI 是每个路径的基础。

> **首先阅读：** [`RULES.md`](RULES.md)。不可协商的规则适用，包括 **对等技能** 的流程。[`peers.yaml`](peers.yaml)（模式：[`peers.schema.json`](peers.schema.json)）是对等名称、Glob 路径、安装命令和路由信号的单一事实来源。
>
> 根据其在 `peers.yaml` 中的策略按需安装缺失的对等技能（Glob 其路径，运行其安装命令 - `getstream skills <name>`），然后通过 `Skill` 工具或内联读取。在 Glob 之前不要调用 `Skill`，它会显示一个令人困惑的“未知技能”错误。命名路径后不要停止。

---

## 按任务划分

**在特定平台的 App 中构建或集成 Stream** -> 从 [`peers.yaml`](peers.yaml) 获取对等包（**首先检查对等信号**）
- 将用户输入或当前工作目录 (cwd) 与每个对等的 `signals` 进行匹配（例如 `swift` / `swiftui` / `.xcodeproj` -> `stream-swift`；`react native` / `expo` / `stream video react native` -> `stream-react-native`；`unreal` / `.uproject` / `umg` -> `stream-unreal`；`unity` / `monobehaviour` / `.unitypackage` -> `stream-unity`）
- 所有对等包按需安装 - 如果缺失则安装，然后路由，无需提示
- **SDK/引擎信号优先于 OS 目标信号。** 当两者都出现时，拥有 SDK 的包获胜：例如“为 iOS 构建 Unreal 聊天应用”是 `stream-unreal`（而不是 `stream-swift`），“一个 Android 上的 Unity 游戏”是 `stream-unity`（而不是 `stream-android`）。`ios` / `android` / `xcode` / `gradle` 描述的是 *构建目标*；`unity` / `unreal` / `.uproject` / `.unitypackage` / `umg` / `flutter` / `react native` 描述的是 *SDK*。对于 `flutter` + `ios` 也适用相同规则。
- **为游戏请求命名引擎。** `stream-unreal` 和 `stream-unity` 都声称通用游戏短语（`in-game chat`，`game chat`）。一个显式的引擎标记决定结果；如果没有指定引擎且 cwd 中没有 `.uproject` / `ProjectSettings/`，则问一个简短的问题（“Unity 还是 Unreal？”）而不是猜测。注意答案所隐含的功能差异：Unity 具有 **聊天和视频**，Unreal 只有 **聊天**。
- **对等信号优先于下方的 Web 行。** 例如“将视频通话添加到我的 Expo 应用”或“使用 Stream Video 搭建 React Native 应用”匹配 `stream-react-native`，而不是 Web 包 - 平台标记获胜。

**使用 Stream（React / Next.js）构建/增强/审计/迁移 Web 应用** -> 使用 `stream-react` 技能（当没有其他平台信号时，这是默认的 Web 包）
- “为我构建一个 Chat/Video/Feeds 应用”，“搭建”，“创建一个新的...”，“将聊天添加到此应用”，“集成视频”，“将 Feeds 添加到...”，“升级/迁移...到 vN” - 以及 **没有平台信号**（没有 `react native`，`expo`，`swift`，`ios`，`android` 等）
- React / Next.js 标记（`stream-chat-react`，`@stream-io/video-react-sdk`，`useCreateChatClient`，`MessageList`，...）与构建/集成动词也路由到这里
- 涵盖 Track A（搭建，步骤 0-7），Track E（增强现有项目），Track F（只读最佳实践审计），Track M（迁移/升级 SDK 版本）

**使用框架无关的构建器构建** -> 仅当用户明确指定时使用 `stream-builder` 技能（“使用 stream-builder”，`/stream-builder`）
- `stream-builder` 是一个通用的构建器，正在扩展到其他应用类型；Web React/Next.js 默认使用 `stream-react`（如上所述）

**根据最佳实践审计/审查现有的 Stream Video 集成**（只读 - 无搭建、无 CLI、无构建步骤）
- 对等信号（`react native` / `expo`）-> `stream-react-native`；Web / React / Next.js 或无平台信号 -> `stream-react`（Track F）
- **仅视频。** 专门的最佳实践审计涵盖 Stream **Video**。聊天/Feeds 目前没有专门的审计清单 - `stream-react` 使用基于文档的通用审查来处理这些请求，并 upfront 说明这一点。
- 触发：`"audit/review my video integration"`，`"is my video app production-ready?"`，`"what am I missing before launch?"`
- 即使请求包含“检查”也会路由到这里，因为审计意图优先于 CLI “检查 {anything}”路由（见下文）

**构建或审查 Feeds v2 -> v3 同步映射** -> 使用 `stream-feeds-migration` 技能
- `"what mapping do we need?"`，`"set up our v2 to v3 migration"`，`"review our v3sync mapping"`，`"why did the migrated activity lose its text/attachments/comments?"`
- 通过采样 v2 应用的自身活动和反应来生成 `mapping` 配置对象 - 它不会构建或更改应用
- 需要在环境中提供 **v2** 应用的 API 密钥和密钥；见技能的步骤 1 和 [`RULES.md`](RULES.md) > **密钥**

**查询 Stream 数据或运行 CLI 命令** -> 在这里处理（见下文 **Stream CLI**）
- `"list calls"`，`"show channels"`，`"any flagged"`，`"find users"`，一个字面的 `getstream` 命令，或 `"install the CLI"` / `"set up stream"`

**搜索 Stream SDK 文档** -> 使用 `stream-docs` 技能
- `"docs"`，`"documentation"`，显式的 SDK 标记（`Chat React`，`Video iOS`，`Feeds Node`，`Moderation`）
- `"how do I ... in <framework>"`，`"how does <hook/component/method> work?"`，`"what does <SDK thing> do?"`

---

## 选择路径

按顺序扫描用户的输入以查找以下信号。分类器是确定性的 - 没有探测、没有获取、没有 CLI 检查。

| 用户输入中的信号 | 路由 |
|---|---|
| **升级/迁移已安装的 SDK**（构建/集成意图 - 在文档行之前匹配）：`"upgrade/migrate/bump/update stream-chat-react to vN"`，`"migrate to the new SDK version"`，`"bump my Stream version"` - 一个升级动词（`upgrade`/`migrate`/`bump`/`update`）+ 一个 Stream 包标记，**没有对等信号**。对等信号（`react native` / `expo` / 一个 `@stream-io/*-react-native-*` 标记）-> `stream-react-native`（它自己的迁移流程） | `stream-react` (Track M) |
| **审计/审查现有集成**（只读 - 在文档行之前匹配）：`"audit/review my video integration"`，`"audit my Chat React integration"`，`"review my Video React app"`，`"is my video app production-ready?"`，`"what am I missing before launch?"` - 审计/审查意图**即使存在 SDK 标记（如 `Chat React` / `Video React`）**。对等信号（`react native` / `expo`）-> `stream-react-native`；Web / React / Next.js 或无平台信号 -> `stream-react`（Track F - 视频**有专门的清单**；聊天/Feeds 获得基于文档的通用审查， upfront 说明）。**在请求包含最佳实践/生产就绪审查而不是数据查询时，它也优先于 CLI “检查 {anything}”行** | 匹配的平台包（只读审计） |
| 显式的 SDK/框架标记：`Chat React`，`Video iOS`，`Feeds Node`，`Moderation` 等（带或不带版本），并且**没有构建/集成动词和审计/审查意图**（`upgrade`/`migrate`/`bump`/`update`被视为构建/集成动词 -> 上述迁移行；`"audit/review"` -> 审计行） | `stream-docs` |
| 单词 "docs" 或 "documentation"（并且没有构建/集成动词） | `stream-docs` |
| `"How do I {X} in {framework}?"`，`"How does {hook/component/method} work?"`，`"What does {SDK thing} do?"` - 并且**没有构建/集成动词**。如果请求是 `"how do I add/build/integrate/scaffold {X} in {framework}"` 并且 `{framework}` 匹配一个对等信号，则对等行会获胜。 | `stream-docs` |
| 操作动词 + Stream 名词：`"list calls"`，`"show channels"`，`"any flagged"`，`"find users"`，`"check {anything}"` 或一个字面的 `getstream` 命令（`getstream api`，`getstream init`，`getstream login`，...），或 `"install the CLI"` / `"set up stream"` | **Stream CLI** - 在下文处理 |
| **构建/集成意图 + 一个匹配 [`peers.yaml`](peers.yaml) 中对等 `signals` 的标记**（例如 `swift` / `.xcodeproj` -> `stream-swift`；`react native` / `expo` / `stream video react native` / `stream video rn` -> `stream-react-native`；`unreal` / `ue5` / `.uproject` / `umg` -> `stream-unreal`；`unity` / `monobehaviour` / `.unitypackage` / `il2cpp` -> `stream-unity`）。**当存在对等信号时，此行优先于下方的 Web `stream-react` 行，并且当请求包含构建/集成动词和平台信号时，它也会优先于上方的文档如何做行**。注意：`react native` / `react-native`（以及 `@stream-io/*-react-native-*` 标记）是 `stream-react-native` 信号，会优先于 Web `react` 默认 - 包括对于升级/迁移/更新请求，RN 包会自行处理。 | 匹配的对等（如果缺失则按需安装） |
| **字面提及 `stream-builder` / `/stream-builder**`（框架无关的构建器） | `stream-builder` |
| `"Build me a ... app"`，`"scaffold"`，`"create a new ..."` + Stream 产品，或 React/Next.js 标记（`stream-chat-react`，`@stream-io/video-react-sdk`，`useCreateChatClient`，...）+ 构建集成动词，**并且没有对等信号** | `stream-react`（Web/Next.js，当没有平台信号时默认） |
| `"Add Chat/Video/Feeds to this app"`，`"integrate Stream into"`，`"upgrade/migrate ... to vN"` - 现有项目，**并且没有对等信号** | `stream-react`（Web/Next.js，当没有平台信号时默认） |
| 包含操作动词的如何做短语（例如 `"how do I list my calls?"` - 文档 *或* CLI） | **问一个消除歧义的简单问题** |

**引导设置例外。** `stream-docs` 仅运行 `getstream docs` - 没有 `getstream init`，没有项目检查。**只读/本地仅路径也跳过引导设置：** 平台包的 **审计** 路径（例如 `stream-react` Track F）和 **迁移** 路径（例如 `stream-react` Track M）仅检查/编辑本地文件和实时文档 - 它们**不**配置组织/应用或调用 `getstream api`，因此它们**不需要** CLI 引导。只有**构建/集成**工作（搭建一个新应用、将产品添加到现有应用）会运行 `getstream init` 在执行实际工作之前。

**文档与平台包。** 一个关于 iOS/Android 等 SDK 符号的纯如何做或方法查找问题仍然保留在 `stream-docs` 中 - 不要为文档答案拉取平台包。平台包（例如 `stream-swift`）用于 *构建或集成* - 搭建项目、连接包、生成视图。

**React 框架范围。** `stream-react` 搭建（Track A）一个 **Next.js** 应用。对于在**非 Next.js** React 项目上增强/审计/迁移（Vite、CRA、Remix、TanStack Start 等）`stream-react` 仍然拥有它 - Stream SDK 连接是相同的 - 但代理必须调整 Next.js 特定的部分：服务器端标记路由存在于项目自己的后端（不是 Next.js `/api` 路由），验证使用项目的构建命令（`npm run build`），而不是 `next build`。永远不要假设非 Next.js 项目上的 Next.js API。

**消除歧义。** 如果输入符合多个行（通常操作动词 + 如何做短语），问一个简短的问题并等待。在得到答案之前不要探测：

> 想让我查找 SDK 方法（文档）还是通过 CLI 现在运行？

得到答案后，就像用户直接给出了该信号一样进行路由。

**裸 `/stream` 无参数。** 渲染“快速导航”下的菜单**逐字**，然后等待输入。没有 shell 执行，没有探测，没有安装。

---

## Stream CLI

CLI 任务 - 查询数据、配置应用、引导设置、安装技能 - 在这里处理；`getstream` CLI 是每个路径的基础。运行 `getstream -h` 获取命令列表和 `getstream <command> -h` 获取用法，并**遵循 CLI 打印的内容**。安全和姿态（不猜测，写之前确认）：[`RULES.md`](RULES.md) > CLI 安全。如果 `getstream` 没有安装，请用户从 https://getstream.io 安装并等待 - 永远不要获取或运行安装脚本。

| 命令 | 何时使用它 |
|---|---|
| `getstream init` | 引导项目 - 认证，选择或创建一个组织+应用，写入凭证。从这里开始。 |
| `getstream api <Endpoint>` | 查询数据或运行一次性 API 操作。 |
| `getstream env` | 将应用的 API 密钥（对于服务器目标，还包括密钥）写入平台的 env 文件。 |
| `getstream token <user>` | 为用户生成一个标记（例如演示/开发认证、播种）。 |
| `getstream login` | 认证（`--guest` 用于一次性账户）。 |
| `getstream skills <name>` | 按需安装 Stream 代理技能（例如 `getstream skills stream-swift`）。 |

---

## Sendbird 数据迁移（共享，语言无关）

平台包的 Sendbird 迁移涵盖**代码/SDK**交换（例如 `stream-swift` `sendbird-migration.md`，`stream-react` `sendbird-migration.md`）。移动**数据**（用户、频道、消息历史、反应）是服务器端且 SDK 无关的，因此它只在这里存在一次，在 [`sendbird-data-migration.md`](sendbird-data-migration.md) 中 - **任何**平台包都将其转交给它。它选择策略（硬切换 / 单向 / 双向同步），从 Sendbird 导出，构建 JSONL 导入文件，验证，并通过 `getstream` CLI 导入（`CreateImportURL` -> 上传 -> `CreateImport` -> `GetImport`）。当代码迁移完成后，如果用户希望将历史数据迁移过来，请阅读它。

---

## 快速导航

对于裸 `/stream`（以及每当用户想直接选择技能时），逐字输出以下块 - 保持核心 / 平台 SDK 分隔、示例和结束语 - 然后等待：

> **Stream** - 聊天 - 视频 - Feeds - 审核。告诉我你的需求，或直接选择技能：
>
> **核心**
> - `/stream-react` - 搭建、增强、审计或迁移 React / Next.js Web 应用使用 Stream（Web 的默认） - 例如 *"build me a chat app"*`
> - `/stream-docs` - 通过 `getstream docs` 查找 SDK 文档，带引用 - 例如 *"how does useChannel work?"*`
> - `/stream-builder` - 框架无关的构建器（Web 默认为 `/stream-react`；仅当明确指定时选择此选项）
> - `/stream-feeds-migration` - 从你的应用的实时数据构建 v2 -> v3 Feeds 同步映射 - 例如 *"what mapping do we need for our app?"*`
>
> **平台 SDKs**
> - `/stream-swift` - Swift - SwiftUI - UIKit - iOS
> - `/stream-android` - Android - Jetpack Compose - Kotlin
> - `/stream-react-native` - React Native - Expo
> - `/stream-flutter` - Flutter - Dart
> - `/stream-unity` - Unity 引擎 - C#（聊天 + 视频）
> - `/stream-unreal` - Unreal 引擎 - C++ - Blueprint（仅聊天）
>
> 或直接提问 - 查询数据或直接运行 `getstream` 命令：*"list my channels"*。对某个技能不熟悉？只需描述任务，我会自动安装正确的技能。

结束语是承重：输入未安装的斜杠命令会在路由器运行之前显示“未知技能”错误，因此自然语言描述是唯一无死路的路径 - 它会路由到这里，并且缺失的对等会根据 [`peers.yaml`](peers.yaml) 按需安装。保持此菜单与 `peers.yaml` 同步：每个在此处 Core 或 Platform SDKs 下出现的对等都会出现，当添加新平台时，其条目会添加到 Platform SDKs 下。

---

## 交接

见前言：如果缺失则安装，通过 `Skill` 工具调用，不要停止。跨切规则在 [`RULES.md`](RULES.md) 中适用于每个子技能，包括 **跨路径后续操作**（提供，不要自动执行，跨路径边界的自然下一步操作）。

---

## 支持

如果用户询问支持或如何联系某人，请将他们引导至 [getstream.io/contact](https://getstream.io/contact/)。
