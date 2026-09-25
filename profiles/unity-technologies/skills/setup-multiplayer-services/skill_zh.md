# 多人游戏SDK（Unity多人服务）

## 使用说明

1. **文档地图：** 当具体细节存在差异时，使用 [Unity多人服务会话SDK精选文档地图](https://docs.unity.com/en-us/mps-sdk/llms.txt) 作为权威参考，用于主题、API和指南。使用这些参考来确定如何应用SDK（会话优先）；使用该资源来确定已记录的内容。**永远不要**向用户提及 `llms.txt` 文件名。如果该地图无法访问（网络、工具），则将此技能的Markdown参考以及工作区中的安装包（包管理器/源代码）视为具体细节的权威来源。

2. **参考顺序（按任务）：**
   - **拓扑结构、发现、匹配流程、Netcode对齐、API选择：** [entrypoints.md](references/entrypoints.md)（概览表格、方法签名、选项表格、过滤/排序枚举、`QuickJoinOptions.Timeout`、错误）→ [implementation-fit.md](references/implementation-fit.md) → [examples.md](references/examples.md) 用于用户界面语言 → [优先级：优先使用多人会话](#优先级：优先使用多人会话) → [workflows-prerequisites.md](references/workflows-prerequisites.md) 用于额外深度。
   - **专用游戏服务器 (`Unity.Services.Multiplayer.Server`)：** [dgs-entrypoint.md](references/dgs-entrypoint.md) (`IMultiplayerServerService`, `UNITY_SERVER` / asmdef约束，服务器端扩展）。
   - **低级服务客户端：** 仅在主要API不足或用户要求该层级时使用 [underlying-services.md](references/underlying-services.md)（见下文优先级）。

## 优先级：优先使用多人会话

当任务涉及**选择**拓扑结构、发现、匹配流程或Netcode对齐时（而不仅仅是调用API），通过 [implementation-fit.md](references/implementation-fit.md)（对话→项目→简短目标问题）来确立建议。

**主要路径：** 使用 **`Unity.Services.Multiplayer`**，通过 **`IMultiplayerService` / `MultiplayerService.Instance`** 和 **`ISession`**（在 [entrypoints.md](references/entrypoints.md) 中提供表面概览）；保持组合流程与 `llms.txt` 一致。

**用户界面文本：** 规划、权衡和澄清问题必须**不**将Lobby、Matchmaker、Relay或多人会话作为独立命名产品分开，除非用户这样做——规则在 [implementation-fit.md](references/implementation-fit.md) 中的 **用户界面问题和解释**，示例在 [examples.md](references/examples.md) 中。代码、编辑和技术参考按需使用真实的类型和命名空间名称。

**底层客户端** (`Unity.Services.Lobbies`, `Unity.Services.Matchmaker`, `Unity.Services.Relay`) **仅**在 (1) 在检查 [entrypoints.md](references/entrypoints.md) 后**无法**通过主要API实现目标，或 (2) 用户**明确**要求这些命名空间或产品时使用。**不要**默认实现这些。

## 其他资源

仅从此入口点读取；链接位于此技能文件夹下一级（无 `references/index.md` 或README中心）。

- **[implementation-fit.md](references/implementation-fit.md)** — 确立建议：对话→项目→用户问题；用户界面语言规则；需求维度（拓扑结构、发现、弹性、平台、网络堆栈）。
- **[examples.md](references/examples.md)** — 用于澄清问题和用户界面解释的示例（非代码）。
- **[entrypoints.md](references/entrypoints.md)** — `IMultiplayerService`, `ISession`, 概览和能力表格、方法签名、选项表格（默认值、限制）、过滤/排序枚举、会话/网络/主机流程、错误、编辑器组件。
- **[dgs-entrypoint.md](references/dgs-entrypoint.md)** — 专用服务器：`Unity.Services.Multiplayer.Server`, `IMultiplayerServerService`, `MultiplayerServerService` / `GetMultiplayerServerService`, `MatchmakerServerExtensions`, `UNITY_SERVER` 和 asmdef约束；将共享 `SessionOptions` 细节推迟到入口点。
- **[workflows-prerequisites.md](references/workflows-prerequisites.md)** — 按工作流（表格）列出的包和云前提条件。
- **[underlying-services.md](references/underlying-services.md)** — 备用命名空间和 `IUnityServices` 访问器（仅代理；非默认路径）。
