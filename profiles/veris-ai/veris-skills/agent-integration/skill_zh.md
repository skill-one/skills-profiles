将此代理仓库从零开始与 Veris 集成。

这项技能将一个仓库从“普通客户代理源”转变为“Veris 就绪且可推送”。如果用户提供了一个代理仓库的路径，则使用该路径作为仓库根目录。否则，使用当前工作目录。

将任何现有的 `.veris/` 文件或旧的脚手架输出视为仅是起始材料。使用此技能中当前捆绑的引用作为生成内容的真实来源。

## 核心框架：代理是常数，Veris 是测试框架

Veris 存在是为了在现实条件下测试代理。代理是被测试的对象；Veris 是围绕它的框架。这种不对称性驱动了此技能中的每个决策：

- **代理在 Veris 和生产环境中的运行方式相同。** 如果代理在生产环境中对 Slack Web API 发出 HTTP 请求，那么它在模拟中对 Veris Slack 模拟也发出 HTTP 请求。如果它在生产环境中调用 CLI，那么它在模拟中也调用 CLI。没有特殊的模拟代码路径。
- **所有集成工作都位于 `.veris/` 中。** `.veris/veris.yaml`、`.veris/Dockerfile.sandbox`、`.veris/config.yaml`、`.veris/.dockerignore` 是部署描述符——这是 Helm 图表或 `docker-compose.yaml` 对于此代理的等效物。它们描述了如何为这个环境设置代理。它们不包含属于代理内部的代理行为。
- **不要编写包装器、填充代码或“适配”代理以适应 Veris 的代码。** 一个包装 CLI 代理以暴露可调用的 Python 文件，一个将 Veris 的 actor 格式转换为代理原生格式的脚本，一个修补版本的代理，它接受 Veris 特定的参数——所有这些都是错误的形状。这意味着你最终测试的不是代理。
- **不要修改代理的源代码以使其在 Veris 中工作。** 如果代理假设 Veris 无法按原样满足的事情，那么这要么是一个需要记录的 Veris 平台差距，要么是代理中的一个真实问题，这个问题也会影响生产。无论如何，修复工作都不应属于代理的源代码。
- **如果你发现自己需要编写包装器，请停止并将其视为一个发现。** 询问：代理的真实生产集成路径是什么？如果代理在生产环境中有一个 HTTP 服务器，请使用它。如果它在生产环境中仅是 CLI，而 Veris 的 actor 无法驱动 CLI，请升级——这是一个 Veris 功能差距，而不是发明粘合剂的许可。
- **`.veris/` 文件中唯一合法的不是纯配置的文件是一个用于捆绑多个进程（例如，数据库与代理一起）的容器编排 `start.sh`。** 即使那样，它也是按原样启动和运行代理；它不会改变其行为。

当不确定时：代理的作者应该能够阅读 `.veris/` 并将其识别为“Veris 的部署配置”，而不是“有人分支并修补了我的代理。”

### 传输桥是明确的例外

一个**传输桥**在保持底层有效载荷字节不变的情况下，在 actor 的通道格式（例如 `voice_ws` PCM16）和代理框架的原生传输（例如 LiveKit WebRTC、SIP 媒体、专有消息信封）之间进行转换。它**不是**一个包装器。相同的形状存在于生产环境中，用于代理的其他产品表面——移动客户端、自助服务终端、IVR 供应商——因此桥接是真实的产品代码，而不是 Veris 特定的粘合剂。

允许桥接的情况：

- 代理的框架无法重新配置以直接说出 actor 的通道格式（例如，LiveKit Agents 是端到端的 WebRTC，没有原始-PCM16-WS 传输）。
- 桥接是纯传输转换：输入和输出相同的音频字节/相同的 JSON 有效载荷，没有任何语义重塑。（对于语音，代理的模型接收到的音频字节必须与 actor 发送的字节完全相同。对于文本，代理看到的消息有效载荷必须与 actor 发送的有效载荷完全相同。）
- 桥接作为生产代码存在于代理的仓库中（例如 `app/bridge.py`），并由代理自己的测试执行——而不是在 `.veris/` 中。它是代理的 `voice_ws`-on-WebRTC 产品表面；Veris 只是一个调用者。

不允许桥接的情况：

- 它重塑代理看到的内容：重写消息、重新结构化工具调用 JSON、规范化 STT 输出、将 Veris 特定的 actor 字段转换为代理的原生参数。这些都是错误的形状。它们意味着你最终测试的不是代理。
- 框架*可以*配置以说出 actor 的通道（例如，使用 `RawAudioFrameSerializer` for `voice_ws` 的 Pipecat，框架自己的 HTTP 插件 for `http` 等）。首先配置框架；只有在传输固定的情况下才桥接。

快速指南：“相同的字节，不同的网络格式” = 传输桥接（允许）。“不同的字节/不同的形状” = 包装器（不允许）。

参考 [reference/infrastructure-patterns.md Pattern 9](reference/infrastructure-patterns.md#pattern-9-transport-bridge) 了解架构和 [reference/voice-channels.md](reference/voice-channels.md) 了解语音特定的应用程序。

### 向评分器报告客户端工具调用是一个受认可的例外（仅限语音代理）

这是唯一一个真正打破“没有 Veris 特定代码路径”规则的例外——这是故意的。它仅适用于在托管语音到语音平台上构建的**语音代理**（ElevenLabs Conversational AI、OpenAI Realtime、Gemini Live、Vapi 等），其工具在代理进程中执行——作为**客户端工具**，它们在供应商的 WebSocket 上进行往返，或者作为 Vapi 风格的**服务器工具**，平台通过 HTTP 将其 POST 回代理的 webhook。无论如何，调用永远不会到达语音转录。

为什么需要它：语音评分器从语音转录加上代理报告的任何工具调用事件构建其跟踪。客户端工具永远不会到达转录，因此如果没有报告，评分器无法看到工具运行，并将真实操作（卡片冻结、替换）错误地标记为幻觉。文本/HTTP 代理没有这个问题——它们的工具调用会自动捕获——因此这个例外仅适用于语音代理。

修复方法：每次工具运行后，代理向沙盒引擎 POST 一个 `agent_tool_call` 事件，平台将其渲染到评分跟踪中。保持它严格最小化，使其保持为仪器，而不是包装器：

- **在模拟之外不执行无操作。** 基于 `SIMULATION_ID`（生产中未设置→立即返回）。生产行为保持不变。
- **立即执行，软失败。** 短暂超时，吞掉错误，记录警告。报告失败绝不能破坏调用或更改代理的输出。
- **观察，不要重塑。** 在真实工具运行后报告，将真实名称/参数/结果原封不动地传递过去。它记录了发生的事情；它不会改变代理的行为或模型看到的内容。

仅为此客户端工具评分器的可见性、仅为此语音代理、且仅为此最小化形状受认可——它不是一般粘合剂的许可。确切的端点、事件模式和一个复制粘贴钩子在 [reference/voice-channels.md](reference/voice-channels.md#making-client-tool-calls-visible-to-the-grader) 中。

## 核心规则

- 在每个主要步骤之前解释你要做什么。
- 揭示具有真实权衡的决定，并让用户选择。
- 引用仓库中的具体证据，当你对依赖项进行分类或决定如何集成代理时。
- 不要默默保留过时的 Veris 配置。将其迁移到当前首选的形状。
- 不要生成 `.env.simulation`。当前的运行时流程是 `agent.environment` 加上 `veris env vars set`。
- 优先使用当前的 `actor.channels` 模式和规范服务名称。除非用户明确要求兼容性，否则不要生成遗留的 `persona.modality`、`email_address` 或旧服务别名。
- 不要编写 Python 包装器、shell 粘合代码或任何在 Veris 和代理之间进行转换的“适配器”代码。使用代理的真实生产接口。如果这不可能按原样实现，将其作为平台差距提出，而不是作为包装器机会。
- 在执行外部或不可逆操作之前询问：
  - 安装 `veris-cli`
  - 运行 `veris login`
  - 运行 `veris env create`
  - 使用 `veris env vars set` 设置环境变量
  - 使用 `veris env push` 推送

### 快速通道模式

如果用户说“全程到底”、“做所有事情”或以其他方式预先批准完整流程：

- 跳过中间检查点（Phase 2 结束、Phase 3 结束、Phase 4 结束）
- 仍然在执行决策时 inline 解释，以便用户可以跟踪
- 仍然在执行真正不可逆或外部操作之前停止并询问：`veris env create`、`veris env push`、`veris env vars set` 带有真实密钥
- 如果一个决策具有真正模糊的权衡（例如，对于重型服务的捆绑与外部），即使在快速通道模式下也要暂停并询问
- 在结束时，提供所有已做决策的综合摘要

## 需要时阅读这些文件

- 对于当前服务名称和检测：[reference/service-mapping.md](reference/service-mapping.md)
- 对于环境覆盖和模拟凭证：[reference/env-var-overrides.md](reference/env-var-overrides.md)
- 对于可捆绑的本地基础设施：[reference/bundling-recipes.md](reference/bundling-recipes.md)
- 对于容器重构模式：[reference/infrastructure-patterns.md](reference/infrastructure-patterns.md)
- 对于语音代理（`voice_ws` 通道、框架选择、尾随静音、**向评分器报告客户端工具调用以使其可见**）：[reference/voice-channels.md](reference/voice-channels.md)
- 对于当前的 `veris.yaml` 结构：[reference/veris-yaml-schema.md](reference/veris-yaml-schema.md)
- 对于生成的配置示例：[templates/veris-yaml.md](templates/veris-yaml.md)
- 对于 Dockerfile 模式：[templates/dockerfile-sandbox.md](templates/dockerfile-sandbox.md)
- 对于运行时环境变量处理：[templates/env-vars.md](templates/env-vars.md)
- 对于多进程启动脚本：[templates/start-sh.md](templates/start-sh.md)
- 对于集成失败：[phases/troubleshooting.md](phases/troubleshooting.md)

## 工作流程概述

| 阶段 | 目标 |
| --- | --- |
| 0 | 引导 Veris 工具和环境 |
| 1 | 发现仓库和当前运行时 |
| 2 | 分析依赖项和服务策略 |
| 3 | 选择集成模式和容器架构 |
| 4 | 生成 `.veris/veris.yaml` |
| 5 | 生成 `.veris/Dockerfile.sandbox` 和支持文件 |
| 6 | 配置运行时环境变量，验证，并推送 |
| 7 | 烟雾验证 |

---

## 阶段 0：引导 Veris 工具和环境
[阶段 0/7]

告诉用户：“我将确保此仓库具有集成剩余工作所需的 Veris 工具和环境连接。”

### 0.1 验证仓库根目录

确认目录是一个代理仓库，而不仅仅是一个父文件夹。查找源代码、依赖项清单和应用入口点。

### 0.2 验证 `veris-cli`

检查 `veris` 是否已安装并正常工作。

如果未安装：
- 优先 `uv tool install veris-cli`
- 回退：`pip install veris-cli`

解释你使用哪个安装路径以及原因。

### 0.3 验证 Veris 身份验证

检查用户是否已经登录以及他们正在使用哪个配置文件/后端。

如果未通过身份验证：
- 推荐 `veris login` 进行浏览器身份验证
- 仅当用户明确偏好时才使用 API 密钥登录

在身份验证工作正常之前，不要继续到 `veris env push`。

### 0.4 验证或创建 `.veris/`

检查：
- `.veris/config.yaml`
- `.veris/veris.yaml`
- `.veris/Dockerfile.sandbox`
- `.veris/.dockerignore`

如果 `.veris/` 不存在，或者它存在但没有环境绑定：
1. 从仓库目录派生候选环境名称。
2. 向用户显示建议的名称。
3. 在批准后，运行 `veris env create --self-serve --name "<name>"`。

`--self-serve` (`veris-cli >= 2.27.0`) 是此技能受众的正确模式：你正在编写 `.veris/`，并且环境应准备好立即用于 `veris env push`。如果没有它，`env create` 默认为管理设置模式，Veris 团队为客户生成 `Dockerfile.sandbox` + `veris.yaml`，并且 `veris env push` 返回 `409: Run veris env submit first`，直到该设置完成。如果 `veris env create --help` 没有列出 `--self-serve`，请首先使用拥有 `veris` 的安装管理器（`uv tool upgrade veris-cli` 或 `pip install -U veris-cli`）升级 CLI。对于从已经使用 `--self-serve` 创建的环境恢复，请参阅 [phases/troubleshooting.md](phases/troubleshooting.md#veris-env-push-returns-409-managed-onboarding)。

解释 `veris env create` 为他们提供的内容：
- `.veris/veris.yaml` — Veris 模拟配置
- `.veris/Dockerfile.sandbox` — 图像构建定义
- `.veris/.dockerignore` — 构建上下文排除
- `.veris/config.yaml` — 此仓库的环境绑定

### 0.5 将脚手架视为占位符，而不是真相

生成的 `.veris/` 文件只是一个起点。它们可能使用旧的默认值或通用占位符。你有责任用此仓库的正确集成替换它们。

直接进入阶段 1。

---

## 阶段 1：发现仓库和当前运行时
[阶段 1/7]

告诉用户：“我将清点此仓库当前如何运行，它依赖什么，以及用户如何与之交互。”

### 1.1 现有的 Veris 状态

如果 `.veris/` 已经存在，首先读取所有现有的 Veris 文件。指出任何看起来过时或遗留的内容：
- `persona.modality`
- `email_address`
- 旧服务名称，如 `crm`、`calendar`、`oracle`
- 缺少的 `.veris/config.yaml` 环境绑定
- 与当前文档冲突的假设

### 1.2 基础设施文件

读取并总结任何：
- `docker-compose.yml`、`docker-compose.yaml`、`compose.yml`
- `Dockerfile`、`Dockerfile.*`
- `Procfile`
- `supervisord.conf`、`supervisord.ini`
- `vercel.json`、`serverless.yml`、`netlify.toml`
- Kubernetes 资源清单

识别：
- 哪个进程是面向用户的代理
- 其他服务存在
- 系统当前如何启动

### 1.3 环境和密钥

读取：
- `.env.example`、`.env.sample`、`.env.template`
- 配置/设置模块
- 密钥或保险库引用

收集代理读取的每个环境变量，并注意哪些是：
- 稳定的非密钥
- 密钥
- 服务端点
- 可选或仅用于调试

### 1.4 依赖项

读取仓库的语言/运行时的包清单，并识别：
- 包管理器
- 框架
- Python/Node 运行时假设
- 外部服务的 SDK

### 1.5 源代码入口点

找到处理传入用户工作的实际代码路径：
- 应用/服务器入口点
- 聊天/消息处理器
- 配置/设置模块
- 请求路由
- 任何在用户对话期间重要的后台工作或 webhook 监听器

### 1.5a 平台托管的代理（仅配置的仓库）

如果仓库没有传统的应用入口点——没有 `main.py`、`app.py`、`server.js`、`index.ts`——请检查它是否是一个**平台托管的代理**：一个运行在已安装框架上的配置文件仓库（CrewAI、LangServe、AutoGen、Dify、n8n、Flowise 或类似）。

迹象：
- 主要文件是 YAML/JSON 配置、提示模板和工具定义
- `pyproject.toml` 或 `package.json` 将框架列为主要依赖项
- 没有实质性的应用逻辑，除了小的工具/钩子文件
- README 指令说“安装 [框架]，然后运行 [框架命令]”

如果是这种情况：
- 框架是运行时——它将在 Dockerfile 中安装，而不是从源代码构建
- 入口点是框架的 CLI 或服务器命令
- 参考 `reference/infrastructure-patterns.md` 中的模式 8 了解完整的重构方法
- 如果你在这些仓库上尝试 `pip install .`，注意源树编译错误

### 1.6 确定集成接口

这是至关重要的。确定模拟的 actor 应该如何与代理通信。

寻找四类接口：

**HTTP**
- 聊天端点
- 请求/响应正文形状
- 会话或对话字段
- JSON 或 SSE 响应样式

**WebSocket**
- WS 路由
- 消息帧
- 会话处理

**电子邮件**
- 收件箱地址
- 抽取或 webhook 流程

**函数**
- 一个干净的 Python 可调用函数，代理作为其公共 API 的一部分已经暴露
- 代理自己的文档中视为入口点的现有 `handle_message`-风格函数

不要通过包装 CLI 或服务器来发明函数接口。如果代理在生产环境中仅是 CLI，那么集成是 CLI 驱动的——提出正确的 Veris 通道，或者将其记录为平台差距。函数通道仅在仓库已经提供可调用的作为其主要或文档化接口时才是正确的。

如果网络和函数模式都可行，使用仓库的真实产品接口。这就是在生产中运行的；这就是我们测试的。

告诉用户你发现了什么，并确认最可能的集成路径，然后再继续。

进入阶段 2。

---

## 阶段 2：分析依赖项和服务策略
[阶段 2/7]

告诉用户：“我现在将每个依赖项分类为模拟、捆绑、外部或跳过。”

读取：
- [reference/service-mapping.md](reference/service-mapping.md)
- [reference/env-var-overrides.md](reference/env-var-overrides.md)
- [reference/bundling-recipes.md](reference/bundling-recipes.md)

对于每个依赖项，将其分类为以下之一：

1. **使用 Veris 模拟**
2. **在容器内捆绑**
3. **使用外部端点**
4. **完全跳过**
5. **需要讨论**
6. **允许真实出站**——代理必须能够到达真实的互联网（例如，网络搜索、URL 抓取、实时 API 没有模拟）。结果将在模拟运行之间是非确定性的。

### 分类规则

- 在决定之前始终阅读源代码。不要仅凭服务名称推断重要性。
- 在决定某物可跳过时显示证据。
- 当捆绑成本很重要时，尤其是在 Elasticsearch 或 LocalStack 等重型服务的情况下，提出捆绑成本。
- 当依赖项可以干净地映射到 Veris 时，优先使用模拟服务。
- 优先使用环境变量覆盖而不是代码更改，如果可能的话。

### 特殊情况

**Postgres**
- 决定是使用 Veris `postgres` 还是外部数据库
- 如果使用 Veris `postgres`，找到模式工件或迁移源，并确定最佳的复制路径

**LLM 提供商**
- 不需要 Veris 服务条目
- LLM 代理会自动拦截支持的主机名

**电子邮件**
- 如果 actor 使用电子邮件通道，请注意 Veris 电子邮件服务会自动注入

**身份验证辅助工具**
- Google/Microsoft/Atlassian/Intuit 身份验证辅助工具是平台级别的辅助工具，不是你应该手动添加的服务

**网络搜索和抓取**
- 如果代理调用搜索 API（Google、Bing、SerpAPI、Tavily、Brave Search、DuckDuckGo）或获取实时 URL，则这些不能模拟
- 分类为“允许真实出站”
- 警告用户：实时互联网调用使模拟结果非确定性——相同的场景在不同的运行中可能产生不同的输出
- 如果搜索是真正可选的（例如，当知识库没有答案时使用备用方案），请考虑通过环境变量禁用它以进行确定性模拟

**真实互联网出站（一般）**
- 某些代理需要访问 Veris 无法模拟的任意外部端点（将第三方服务的 webhook、实时数据源、公共 REST API 没有 Veris 服务）
- 这些也分类为“允许真实出站”
- Veris 容器默认允许非拦截域的外出站互联网
- 向用户展示非确定性权衡

### 检查点

在继续之前与用户一起回顾你的依赖项分析。用户应该理解：
- 将被模拟的内容
- 将被捆绑的内容
- 将保持外部
- 将被跳过的内容
- 仍然需要决策的内容

在继续之前等待批准。

---

## 阶段 1：选择集成模式和容器架构
[阶段 1/7]

告诉用户：“我现在将锁定此代理在 Veris 容器中运行的方式以及 actor 将如何与它通信。”

读取 [reference/infrastructure-patterns.md](reference/infrastructure-patterns.md)。

### 3.1 选择通道策略

选择一个：

- **HTTP** — 当产品已经是 HTTP 聊天 API 时首选
- **WebSocket** — 当实时状态化消息是核心时首选
- **电子邮件** — 当产品是真正由电子邮件驱动的时首选
- **函数** — 当仓库已经暴露一个可调用的路径或应该被视为一次性请求/响应代理时首选

### 3.2 函数通道规则

如果你选择函数通道：

- 可调用路径必须是代理仓库已经将其作为公共接口暴露的（文档化、在 README 中引用，或否则是其合同的一部分）
- 不要创建一个包装文件来从 CLI 或服务器“发明”一个可调用的——如果仓库没有已经暴露一个可调用，函数是错误的通道
- 忽略 `agent.entry_point` 和 `agent.port` 在 `veris.yaml`
- 如果可调用是单次的且无状态的，设置 `actor.config.MAX_TURNS: 1`

### 3.3 网络通道规则

如果你选择 HTTP / WS / 电子邮件：

- 包括 `agent.code_path`
- 包括 `agent.entry_point`
- 包括 `agent.port`

**函数**

- 包括 `agent.code_path`
- 忽略 `agent.entry_point`
- 忽略 `agent.port`
- 设置 `actor.channels[0].type: function`
- 设置 `callable: ...`

### 检查点

显示完整的 `veris.yaml`，解释各个部分，并在写入或最终确定之前获得批准。

---

## 阶段 1：生成 `.veris/Dockerfile.sandbox` 和支持文件
[阶段 1：生成 `.veris/Dockerfile.sandbox` 和支持文件]

告诉用户：“我现在将生成此集成的图像构建和任何小的支持文件。”

读取：

- [templates/dockerfile-sandbox.md](templates/dockerfile-sandbox.md)
- [templates/start-sh.md](templates/start-sh.md)

### 1.1 Dockerfile 规则

- 以以下内容开始：

```dockerfile
ARG GVISOR_BASE
FROM ${GVISOR_BASE}
```

- 构建上下文是仓库根目录
- 在源代码之前复制依赖项清单
- 仅复制代理实际需要的文件
- 以 `WORKDIR /app` 结尾
- 不要将 `veris.yaml` 烘焙到图像中

### 1.2 运行时说明

- 当前的基图像已经包括 Python、`uv` 和 Node.js
- 仅当仓库真正需要时才安装额外的运行时或系统包
- 如果使用函数通道，你仍然正常打包代理代码和依赖项；你只是不启动网络服务器

### 1.3 支持文件

仅创建需要的：

- `start.sh` 用于捆绑多个进程（例如，数据库与代理一起）——这是容器编排，与 `docker-compose.yaml` 将会是的
- `.veris/.dockerignore` 更新如果仓库有大型目录默认忽略文件遗漏

不要创建 Python “包装模块”来暴露代理作为一个可调用的，将 Veris actor 调用转换为代理的原生格式，或以其他方式在 actor 和代理之间插入自己。使用代理的真实接口。

### 1.4 不修改代理的源代码

代理在 Veris 中按原样运行，这意味着：

- 没有对代理的源代码进行修补以使其在 Veris 中工作
- 没有“模拟模式”标志或 Veris 特定的分支
- 没有代理的分支副本，带有本地修改

如果你发现自己想要修改代理的源代码，请停止。要么：

- 可以作为环境变量覆盖表达的更改（然后以这种方式通过 `agent.environment` 或 `veris env vars set` 执行），要么
- 代理中的真实问题（然后这是客户的责任来修复，并且也会影响生产），要么
- Veris 无法按原样满足代理（然后这是一个平台差距——升级）

无关的重构显然是不允许的。

**唯一受认可的源添加** 是语音代理的客户端工具报告钩子（见 [核心框架例外](#reporting-client-tool-calls-to-the-grader-is-a-sanctioned-exception-voice-agents-only)）。它是“不修改”规则的故意例外，而不是它的反例：它在模拟之外不执行无操作，它永远不会改变代理的行为，并且它仅存在以便评分器可以看到客户端工具，这些工具否则永远不会到达跟踪。为客户端工具语音代理添加它；不要将其泛化到其他源编辑。

一旦文件就位，直接进入阶段 6。

---

## 阶段 1：配置运行时环境变量，验证，并推送
[阶段 1：配置运行时环境变量，验证，并推送]

告诉用户：“我现在将此转换为可推送的 Veris 环境。”

读取：

- [templates/env-vars.md](templates/env-vars.md)
- [phases/troubleshooting.md](phases/troubleshooting.md)

### 1.1 构建环境变量计划

将环境变量分类为：

1. **稳定的非密钥默认值** → 放入 `agent.environment`
2. **密钥/每个环境值** → 使用 `veris env vars set` 设置
3. **本地仅便利值** → 可选的根 `.env` 或 shell 导出，用于本地烟雾测试

不要创建 `.env.simulation`。

### 1.2 生成确切的命令

生成用户需要的确切的 `veris env vars set` 命令。

如果用户提供了实际值并希望您执行，请为他们运行命令。

**Shell 插值陷阱**：当使用 `veris env vars set KEY="$VAR" --secret` 与 shell 变量一起运行时，首先验证源变量是否实际设置 (`printenv VAR` 或 `test -n "$VAR"`). 空白或未设置的变量扩展为 `""`，无声地——CLI 将乐于保存空的密钥而没有错误，并且代理将在运行时遇到令人困惑的身份验证/提供者错误，而不是清晰的“缺少密钥”消息。

### 1.3 验证推送先决条件

推送之前，验证：

- `veris` 已安装
- auth/配置文件工作正常
- `.veris/config.yaml` 具有环境 ID
- `.veris/veris.yaml` 存在
- `.veris/Dockerfile.sandbox` 存在

可选但鼓励：

- 运行本地 `docker build -f .veris/Dockerfile.sandbox .` 烟雾测试，当这可能快速捕获明显的破坏时

### 1.4 推送

如果用户批准，运行：

```bash
veris env push
```

或使用显式标签如果用户想要一个：

```bash
veris env push --tag <tag>
```

如果推送失败：

- 诊断失败的构建步骤
- 修复集成
- 重试

### 1.5 最终摘要

总结：

- 创建或修改的文件
- 选择的集成模式
- 模拟、捆绑、外部或跳过的服务
- 设置的环境变量与用户设置的环境变量
- `veris env push` 是否成功以及创建的标签

然后建议下一步命令：

- `veris scenarios create`
- `veris simulations create`

---

## 阶段 1：烟雾验证
[阶段 1：烟雾验证]

告诉用户：“我将运行一个场景和一个模拟来验证集成端到端是否工作正常。”

### 1.1 创建一个烟雾场景

```bash
veris scenarios create --num 1
```

目标是执行代理的主要接口的一个简短交互。

### 1.2 运行一个模拟

```bash
veris simulations create --scenario-set-id <id>
```

等待它完成。

### 1.3 检查结果

检查模拟以：

1. **代理以真实内容响应**——不是错误页面、空正文或异常回溯
2. **模拟服务被调用**——如果代理应该调用 Slack、Salesforce 等，请确认这些调用出现在其中
3. **没有启动崩溃**——代理进程在整个过程中保持活动状态
4. **通道合同是正确的**——actor 的消息到达代理，并且响应以预期的形状返回

### 1.4 诊断失败

如果烟雾测试失败：

- 检查代理容器日志以查找启动错误或缺少环境变量
- 验证 `actor.channels` 请求/响应映射是否与实际 API 形状匹配
- 确认模拟服务凭证和 DNS 别名是正确的
- 返回相关阶段进行修复并重新推送

### 1.5 签署

如果烟雾测试通过，总结：

- 演示者发送的内容和代理的响应
- 练习了哪些服务
- 对集成准备就绪的信心水平

然后建议完整场景生成 (`veris scenarios create --num N`) 和模拟作为下一步步骤。

---

## 实用指南

### 优先使用当前约定而不是过时的脚手架

如果 `veris env create` 脚手架了看起来过时的占位符，用当前首选的形状覆盖它们。

### 保持技能对函数通道的诚实

仅在代理已经暴露一个可调用的作为其公共接口时使用函数通道。不要强迫一个网络产品进入函数可调用，仅仅因为它看起来更简单，并且永远不要创建一个包装文件来“发明”代理不存在的可调用函数。

### 保持技能对一次性代理的诚实

如果集成的代理明显是一次性的/无状态的，明确地将其传递通过，设置 `actor.config.MAX_TURNS: 1`。

### 明确你未自动化的内容

如果登录、密钥或环境变量值仍然需要用户操作，请明确说明。目标是尽可能远，而不是隐藏障碍物。
