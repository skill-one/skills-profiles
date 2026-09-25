# ChatGPT 应用程序

## 概述

使用文档优先、示例优先的工作流程来构建 ChatGPT 应用程序 SDK 实现，然后生成遵循当前应用程序 SDK 和 MCP 应用程序桥接模式的代码。

使用此技能来生成：

- 主要的应用程序原型分类和存储库形状决策
- 工具计划（名称、模式、注释、输出）
- 上游起始点推荐（官方示例、ext-apps 示例或本地回退脚手架）
- MCP 服务器脚手架（资源注册、工具处理程序、元数据）
- 小部件脚手架（MCP 应用程序桥接优先，`window.openai` 兼容性/扩展次之）
- 可重用的 Node + `@modelcontextprotocol/ext-apps` 起始脚手架用于低依赖性回退
- 针对最小可工作存储库合同的有效性报告
- 本地开发和连接器设置步骤
- 当请求时，关于应用程序做什么的干系人摘要

## 强制文档优先工作流程

在构建或更改 ChatGPT 应用程序 SDK 应用程序时，始终首先使用 `$openai-docs`。

1. 调用 `$openai-docs`（首选）或直接调用 OpenAI 文档 MCP 服务器。
2. 在编写代码之前获取当前应用程序 SDK 文档，尤其是基线页面：
   - `apps-sdk/build/mcp-server`
   - `apps-sdk/build/chatgpt-ui`
   - `apps-sdk/build/examples`
   - `apps-sdk/plan/tools`
   - `apps-sdk/reference`
3. 在构建新应用程序或生成第一版实现时，获取 `apps-sdk/quickstart`，并在从零开始构建脚手架之前检查官方示例存储库/页面。
4. 在任务包括本地 ChatGPT 测试、托管或公共发布时，获取部署/提交文档：
   - `apps-sdk/deploy`
   - `apps-sdk/deploy/submission`
   - `apps-sdk/app-submission-guidelines`
5. 在解释设计选择或生成脚手架时，引用您使用的文档 URL。
6. 当它们不同时，优先考虑当前文档指南而不是旧的存储库模式，并明确指出兼容性别名。
7. 如果文档搜索超时或返回不良匹配，请通过 URL 直接获取规范的应用程序 SDK 页面并继续；不要让搜索失败阻止脚手架构建。

如果 `$openai-docs` 不可用，请使用：

- `mcp__openaiDeveloperDocs__search_openai_docs`
- `mcp__openaiDeveloperDocs__fetch_openai_doc`

阅读 `references/apps-sdk-docs-workflow.md` 以获取建议的文档查询和紧凑的检查清单。
阅读 `references/app-archetypes.md` 以在选择示例或脚手架之前将请求分类为少量支持的应用程序形状。
阅读 `references/repo-contract-and-validation.md` 以在生成或审查存储库时，确保输出保持在稳定的“可工作应用程序”合同内。
阅读 `references/search-fetch-standard.md` 当应用程序是连接器样式、数据仅、同步导向或旨在与公司知识或深入研究良好配合时。
阅读 `references/upstream-example-workflow.md` 当开始绿色字段应用程序或决定是否调整上游示例或使用本地回退脚手架时。
阅读 `references/window-openai-patterns.md` 当任务需要 ChatGPT 特定的小部件行为或当从使用特定 `app.*` 辅助函数的存储库示例进行翻译时。

## 提示指导

使用明确将此技能与 `$openai-docs` 配对的提示，以便生成的脚手架基于当前文档。

首选的提示模式：

- `使用 $chatgpt-apps 与 $openai-docs 来为 <用例> 构建一个具有 <TS/Python> MCP 服务器和 <React/vanilla> 小部件的 ChatGPT 应用程序。`
- `使用 $chatgpt-apps 与 $openai-docs 将最接近的官方应用程序 SDK 示例转换为用于 <用例> 的 ChatGPT 应用程序。`
- `使用 $chatgpt-apps 和 $openai-docs 将此应用程序 SDK 演示重构为具有工具注释、CSP 和 URI 版本化的生产就绪结构。`
- `使用 $chatgpt-apps 与 $openai-docs 首先计划工具，然后生成 MCP 服务器和小部件代码。`

在响应时，在编码之前请求或推断这些输入：

- 用例和主要用户流程
- 只读与可变工具
- 演示与生产目标
- 私有/内部使用与公共目录提交
- 后端语言和 UI 堆栈
- 认证要求
- 用于 CSP 允许列表的外部 API 域名
- 托管目标和本地开发方法
- 组织所有权/验证准备情况（用于提交任务）

## 在选择代码之前对应用程序进行分类

在选择示例、存储库形状或脚手架之前，将请求分类为一个主要原型，并声明它。

- `仅工具`
- `vanilla 小部件`
- `react 小部件`
- `交互式解耦`
- `提交就绪`

除非缺少的详细信息确实阻止，否则推断原型。使用原型来选择：

- 是否需要 UI
- 是否要保留分割的 `server/` + `web/` 布局
- 是否要优先考虑官方 OpenAI 示例、ext-apps 示例或本地回退脚手架
- 哪些验证检查最重要
- 是否 `search` 和 `fetch` 应该是默认的只读工具表面

阅读 `references/app-archetypes.md` 以获取决策标准。

## 默认起始点顺序

对于绿色字段应用程序，请按顺序优先考虑这些起始点：

1. **官方 OpenAI 示例** 当一个接近的示例已经匹配请求的堆栈或交互模式时。
2. **版本匹配的 `@modelcontextprotocol/ext-apps` 示例** 当用户需要一个较低级别或更可移植的 MCP 应用程序桥接/服务器布线时，或者当版本匹配的包模式比 ChatGPT 特定的美化更重要时。
3. **`scripts/scaffold_node_ext_apps.mjs`** 仅当没有接近的示例适合、用户想要一个微小的 Node + vanilla 起始器，或者网络访问/示例检索不受欢迎时。

如果存在一个接近的上游示例，则不要从头开始生成一个大的自定义脚手架。
复制最小的匹配示例，删除不相关的演示代码，然后将其修补到当前文档和用户请求。

## 构建工作流程

### 0. 对应用程序原型进行分类

在计划工具或选择起始点之前，选择一个主要原型。

- 优先选择一个主要原型，而不是混合几个。
- 如果请求很广泛，推断可以满足请求的最小原型。
- 仅当用户要求公共发布、目录提交或审查就绪部署时，才将 `submission-ready` 升级为 `submission-ready`。
- 在您的响应中指明选择的原型，以便用户可以在需要时早期更正它。

### 1. 在代码之前计划工具

根据用户意图定义工具表面区域。

- 每个工具使用一个作业。
- 编写以“使用此工具时...”行为提示开头的工具描述。
- 使输入明确且机器友好（枚举、必需字段、边界）。
- 决定每个工具是仅数据、仅渲染还是两者兼有。
- 准确设置注释（`readOnlyHint`、`destructiveHint`、`openWorldHint`；当为真时添加 `idempotentHint`）。
- 如果应用程序是连接器样式、数据仅、同步导向或旨在用于公司知识或深入研究，则默认使用标准的 `search` 和 `fetch` 工具，而不是发明自定义只读等效项。
- 对于教育/演示应用程序，请为每个工具优先考虑一个概念，以便模型可以干净地选择正确的示例。
- 按学习目标对演示工具进行分组：数据到小部件，小部件操作回到对话或工具，主机/布局环境信号，以及生命周期/流行为。

阅读 `references/search-fetch-standard.md` 当 `search` 和 `fetch` 可能相关时。

### 2. 选择应用程序架构

选择最简单的符合目标的结构。

- 使用**最小演示模式**进行快速原型、研讨会或概念验证。
- 使用**解耦数据/渲染模式**进行生产 UX，以便小部件不会在每次工具调用时重新渲染。

对于非平凡的应用程序，优先选择解耦模式：

- 数据工具返回可重用的 `structuredContent`。
- 渲染工具附加 `_meta.ui.resourceUri` 和可选的 `_meta["openai/outputTemplate"]`。
- 渲染工具描述声明先决条件（例如，“先调用 `search`”）。

### 2a. 当一个适合时从上游示例开始

对于绿色字段工作，当它们接近请求的应用程序时，默认使用上游示例。

- 首先检查官方 OpenAI 示例，用于面向 ChatGPT 的应用程序、精制 UI 模式、React 组件、文件上传流程、模态流程或类似于文档示例的应用程序。
- 使用 `@modelcontextprotocol/ext-apps` 示例，当请求更接近原始 MCP 应用程序桥接/服务器布线时，或者当版本匹配的包模式比 ChatGPT 特定的美化更重要时。
- 选择最小的匹配示例，并仅复制相关文件；不要更改整个展示应用程序。
- 复制后，将示例与您获取的当前文档进行协调：工具名称/描述、注释、`_meta.ui.*`、CSP、URI 版本化以及本地运行说明。
- 在一句话中说明您选择的示例以及原因。

阅读 `references/upstream-example-workflow.md` 以获取选择和适应标准。

### 2b. 当低依赖性回退有助于时使用起始脚本

仅当用户想要一个快速的绿色字段 Node 起始器，并且 vanilla HTML 小部件可以接受，并且没有上游示例是更好的起始点时，使用 `scripts/scaffold_node_ext_apps.mjs`。

- 仅在获取当前文档后运行它，然后将生成的文件与您获取的文档进行协调。
- 如果您选择脚本而不是上游示例，请说明为什么回退对此请求更好。
- 当存在接近的官方示例时跳过它，当用户已经有一个现有的应用程序结构时跳过它，当他们需要一个非 Node 堆栈时跳过它，当他们明确想要首先使用 React 时跳过它，或者当他们只想计划/审查而不是代码时跳过它。
- 该脚本生成一个最小的 `@modelcontextprotocol/ext-apps` 服务器以及一个使用 MCP 应用程序桥接的 vanilla HTML 小部件。
- 生成的脚本将后续消息保留在标准的 `ui/message` 桥接上，并且仅使用 `window.openai` 用于可选的主机信号/扩展。
- 运行后，请修补生成的输出以匹配当前文档和用户请求：调整工具名称/描述、注释、资源元数据、URI 版本化以及 README/运行说明。

### 3. 构建 MCP 服务器

生成一个服务器，它：

- 注册一个带有 MCP 应用程序 UI MIME 类型（`text/html;profile=mcp-app`）或 SDK 常量（`RESOURCE_MIME_TYPE`）的 widget 资源/模板，当使用 `@modelcontextprotocol/ext-apps/server`
- 使用清晰名称、模式、标题和描述注册工具
- 故意返回 `structuredContent`（模型 + widget）、`content`（模型叙述）和 `_meta`（仅 widget 数据）
- 保持处理程序幂等或明确说明非幂等行为
- 在 ChatGPT 中有帮助时包含工具状态字符串（`openai/toolInvocation/*`）

保持 `structuredContent` 简洁。将大型或敏感的 widget 仅有效载荷移到 `_meta`。

### 4. 构建 Widget UI

首先使用 MCP 应用程序桥接以提高可移植性，然后添加 ChatGPT 特定的 `window.openai` API 当它们实质性改善 UX 时。

- 监听 `ui/notifications/tool-result`（JSON-RPC over `postMessage`）
- 从 `structuredContent` 渲染
- 使用 `tools/call` 进行组件发起的工具调用
- 仅当 UI 状态应改变模型看到的内容时，才使用 `ui/update-model-context`

使用 `window.openai` 进行兼容性和扩展（文件上传、模态、显示模式等），而不是作为新应用程序的唯一集成路径。

#### API 表面护栏

- 一些示例将桥接包装在 `app` 对象中（例如，`@modelcontextprotocol/ext-apps/react`），并暴露辅助函数名称，如 `app.sendMessage()`、`app.callServerTool()`、`app.openLink()` 或主机获取方法。
- 将这些包装器视为实现细节或便利层，而不是默认情况下用于教学的规范公共 API。
- 对于面向 ChatGPT 的指导，优先考虑当前记录的表面：`window.openai.callTool(...)`、`window.openai.sendFollowUpMessage(...)`、`window.openai.openExternal(...)`、`window.openai.requestDisplayMode(...)`，以及直接的全局变量，如 `window.openai.theme`、`window.openai.locale`、`window.openai.displayMode`、`window.openai.toolInput`、`window.openai.toolOutput`、`window.openai.toolResponseMetadata` 和 `window.openai.widgetState`。
- 如果您从存储库示例中引用包装器辅助函数，请将它们映射回记录的 `window.openai` 或 MCP 应用程序桥接基本原理，并指出包装器不是规范 API 表面。
- 使用 `references/window-openai-patterns.md` 进行包装器到规范映射以及 React 辅助函数提取模式。

### 5. 添加资源元数据和安全性

故意在 widget 资源/模板上设置资源元数据：

- `_meta.ui.csp` 带有精确的 `connectDomains` 和 `resourceDomains`
- `_meta.ui.domain` 用于应用程序提交就绪部署
- `_meta.ui.prefersBorder`（或当需要时 OpenAI 兼容性别名）
- 可选的 `openai/widgetDescription` 以减少冗余叙述

除非 iframe 嵌入是产品的核心，否则避免 `frameDomains`。

### 5a. 强制最小可工作存储库合同

在考虑它完成之前，每个生成的存储库都应满足一个小而稳定的合同。

- 存储库形状匹配选择的原型。
- MCP 服务器和工具连接到可到达的 `/mcp` 端点。
- 工具具有清晰的描述、准确的注释和需要的 UI 元数据。
- 连接器样式、数据仅、同步导向和公司知识风格的应用程序在相关时使用标准的 `search` 和 `fetch` 工具形状。
- 当存在 UI 时，小部件正确使用 MCP 应用程序桥接。
- 存储库包含足够的脚本或命令，以便用户可以本地运行和检查它。
- 响应明确说明运行了哪些验证以及未运行哪些验证。

阅读 `references/repo-contract-and-validation.md` 以获取详细的检查清单和验证梯级。

### 6. 验证本地循环

针对最小可工作存储库合同进行验证，而不仅仅是“文件是否已创建”。

- 首先运行最低成本的检查：
  - 静态合同审查
  - 当可行时，语法或编译检查
  - 当可行时，本地 `/mcp` 健康检查
- 然后移动到运行时检查：
  - 在 MCP 检查器中验证工具描述符和小部件渲染
  - 通过 HTTPS 隧道在 ChatGPT 开发者模式下测试应用程序
  - 练习重试和重复工具调用以确认幂等行为
  - 检查主机事件和后续工具调用后的小部件更新
- 如果您只交付脚手架并且不安装依赖项，仍然运行低成本检查，并明确说明您未运行的内容。

阅读 `references/repo-contract-and-validation.md` 以获取验证梯级。

### 7. 在 ChatGPT 中连接和测试（开发者模式）

对于本地开发，包括明确的 ChatGPT 设置步骤（而不仅仅是代码/运行命令）。

- 在 `http://localhost:<port>/mcp` 本地运行 MCP 服务器
- 使用公共 HTTPS 隧道公开本地服务器（例如 `ngrok http <port>`）
- 使用隧道 HTTPS URL 加上 `/mcp` 路径从 ChatGPT 连接
- 在 ChatGPT 中，在 **设置 → 应用程序和连接器 → 高级设置** 下启用开发者模式
- 在 ChatGPT 应用程序设置中，为远程 MCP 服务器创建一个新应用程序并粘贴公共 MCP URL
- 告知用户在 MCP 工具/元数据更改后刷新应用程序，以便 ChatGPT 重新加载最新的描述符

注意：一些文档/屏幕截图仍然使用旧的“连接器”术语。在提供逐步说明时，请优先考虑当前产品措辞（“应用程序”），同时承认两个标签。

### 8. 规划生产托管和部署

当用户要求部署或准备发布时，为 MCP 服务器（以及单独托管的 widget 资产）生成托管指南。

- 在一个稳定的公共 HTTPS 端点后托管（不是隧道）并具有可靠的 TLS
- 保留 `/mcp` 上的低延迟流行为
- 在库外配置密钥（环境变量/密钥管理器）
- 添加日志记录、请求延迟跟踪和工具调用的错误可见性
- 添加基本可观察性（CPU、内存、请求量）和故障排除路径
- 在提交之前在 ChatGPT 开发者模式下重新测试托管端点

### 9. 准备提交和发布（仅限公共应用程序）

仅当用户打算进行公共目录列表时，才包括这些步骤。

- 使用 `apps-sdk/deploy/submission` 进行提交流程，使用 `apps-sdk/app-submission-guidelines` 进行审查要求
- 将私有/内部应用程序保留在开发者模式下，而不是提交
- 在提交工作之前确认组织验证和 Owner 角色先决条件
- 确保MCP服务器使用公共生产端点（没有 localhost/测试URL）并配置提交就绪的CSP
- 准备提交工件：应用程序元数据、标志/屏幕截图、隐私政策 URL、支持联系、测试提示/响应、本地化信息
- 如果需要认证，请包括安全的演示凭证并端到端测试登录路径
- 在平台仪表板中提交审查，监控审查状态，仅在批准后发布

## 交互状态指导

当应用程序具有长时间存在的 widget 状态、重复交互或组件发起的工具调用（例如，游戏、棋盘、地图、仪表板、编辑器）时，阅读 `references/interactive-state-sync-patterns.md`。

使用它来选择模式：

- 状态快照加上单调事件标记（`stateVersion`、`resetCount` 等）
- 幂等重试安全处理程序
- `structuredContent` 与 `_meta` 分区
- MCP 应用程序桥接优先更新流程，可选 `window.openai` 兼容性
- 解耦数据/渲染工具架构，用于更复杂的交互式应用程序

## 输出预期

使用此技能来构建代码时，除非用户要求否则按此顺序生成输出：

- 对于直接脚手架请求，不要停留在计划：给出简要计划，然后立即创建文件。

1. 选择的主要应用程序原型及其原因
2. 工具计划和架构选择（最小与解耦）
3. 选择的上游起始点（官方示例、ext-apps 示例或本地回退脚手架）及其原因
4. 从 `$openai-docs` 使用的文档页面/URL
5. 要创建或修改的文件树
6. 实现（服务器 + widget）
7. 对最小可工作存储库合同的有效性验证
8. 本地运行/测试说明（包括隧道 + ChatGPT 开发者模式应用程序设置）
9. 部署/托管指南（如果请求或暗示）
10. 提交就绪检查清单（对于公共发布请求）
11. 风险、差距和后续改进

## 参考

- `references/app-archetypes.md` 用于将请求分类为少量支持的应用程序形状
- `references/apps-sdk-docs-workflow.md` 用于文档查询、页面目标以及代码生成检查清单
- `references/interactive-state-sync-patterns.md` 用于状态ful 或高度交互式 widget 应用程序的可用模式
- `references/repo-contract-and-validation.md` 用于最小可工作存储库合同和轻量级验证梯级
- `references/search-fetch-standard.md` 用于何时以及如何默认使用标准的 `search` 和 `fetch` 工具
- `references/upstream-example-workflow.md` 用于在官方示例、ext-apps 示例和本地回退脚手架之间进行选择
- `references/window-openai-patterns.md` 用于 ChatGPT 特定的扩展、包装器 API 翻译以及 React 辅助函数模式
- `scripts/scaffold_node_ext_apps.mjs` 用于一个最小的 Node + `@modelcontextprotocol/ext-apps` 回退起始脚手架
