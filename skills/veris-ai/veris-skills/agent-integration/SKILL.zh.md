---
name: agent-integration
description: 与 Veris 端到端集成原始客户代理仓库。安装或验证 veris-cli，登录，创建或复用 Veris 环境，分析仓库，生成或更新 `.veris/veris.yaml`、`.veris/Dockerfile.sandbox`、`.veris/.dockerignore`，配置运行时环境变量，并可通过 `veris env push` 完成操作。当仓库尚未设置 Veris，或现有的 `.veris/` 集成已过时需要刷新时使用。
---

从零开始将此代理仓库与 Veris 集成。

这项技能将一个“普通客户代理源代码仓库”转化为“Veris 就绪且可推送的仓库”。如果用户提供了一个代理仓库的路径，则使用该路径作为仓库根目录。否则，使用当前工作目录。

将任何现有的 `.veris/` 文件或旧的脚手架输出视为仅作为起始材料。使用此技能中当前捆绑的引用作为生成内容的真实来源。

## 核心框架：代理是常数，Veris 是测试平台

Veris 存在的目的是在现实条件下测试代理。代理是被测试的对象；Veris 是围绕它的框架。这种不对称性驱动了这项技能中的每一个决策：

- **代理在 Veris 和生产环境中的运行方式相同。** 如果代理在生产环境中对 Slack Web API 发送 HTTP 请求，那么在模拟中它也对 Veris Slack 模拟发送 HTTP 请求。如果它在生产环境中调用 CLI，那么在模拟中也调用 CLI。没有特殊的模拟代码路径。
- **所有集成工作都位于 `.veris/` 中。** `.veris/veris.yaml`、`.veris/Dockerfile.sandbox`、`.veris/config.yaml`、`.veris/.dockerignore` 是部署描述符——这是 Helm 图表或 `docker-compose.yaml` 对于此代理的等效物。它们描述了如何为这个环境设置代理。它们不包含属于代理内部的代理行为。
- **不要编写包装器、填充代码或“适配”代理以适应 Veris 的代码。** 一个包装 CLI 代理以暴露可调用的 Python 文件、一个将 Veris 的 actor 格式转换为代理原生格式的脚本、一个接受 Veris 特定参数的代理修补版本——所有这些都不正确。这意味着你最终测试的不是代理。
- **不要修改代理的源代码以使其在 Veris 中工作。** 如果代理假设 Veris 无法按原样满足的事情，那么这要么是 Veris 平台差距需要记录，要么是代理中存在真实问题，也会破坏生产环境。无论如何，修复工作都不应属于代理的源代码。
- **如果你发现自己需要编写包装器，请停止并将其视为一个发现。** 询问：代理的真实生产集成路径是什么？如果代理在生产环境中有一个 HTTP 服务器，请使用该服务器。如果它在生产环境中仅是 CLI，而 Veris 的 actor 无法驱动 CLI，请升级——这是一个 Veris 功能差距，而不是发明粘合剂的许可。
- **`.veris/` 文件中唯一合法的不是纯配置的文件是一个用于捆绑多个进程（例如，数据库与代理一起）的容器编排 `start.sh`**。 即使那样，它也是以原样启动和运行代理；它不会改变其行为。

不确定时：代理的作者应该能够阅读 `.veris/` 并将其识别为“Veris 的部署配置”，而不是“有人分支并修补了我的代理。”

### 传输桥是明确的例外

**传输桥** 在 actor 的通道格式（例如 `voice_ws` PCM16）和代理框架的原生传输（例如 LiveKit WebRTC、SIP 媒体、专有消息信封）之间进行转换，同时保留底层的有效载荷字节不变。它**不是**一个包装器。相同的形状存在于生产环境中，用于代理的其他产品表面——移动客户端、自助服务终端、IVR 供应商——因此桥接是真实的产品代码，而不是 Veris 特定的粘合剂。

允许桥接的情况：

- 代理的框架无法重新配置以直接使用 actor 的通道格式（例如，LiveKit Agents 是端到端的 WebRTC，没有原始 PCM16-WS 传输）。
- 桥接是纯传输转换：相同的音频字节 / 相同的 JSON 有效载荷输入输出，没有任何语义重塑。（对于语音，代理的模型接收到的音频字节必须与 actor 发送的字节完全相同。对于文本，代理看到的消息有效载荷必须与 actor 发送的有效载荷完全相同。）
- 桥接作为生产代码存在于代理的仓库中（例如 `app/bridge.py`），并由代理自己的测试执行——不在 `.veris/` 中。它是代理的 `voice_ws`-on-WebRTC 产品表面；Veris 只是一个调用者。

不允许桥接的情况：

- 它重塑代理看到的内容：重写消息、重组工具调用 JSON、标准化 STT 输出、将 Veris 特定的 actor 字段转换为代理的原生参数。这是一个包装器，并且上述不包装规则适用。
- 框架*可以*配置为使用 actor 的通道（例如，使用 `RawAudioFrameSerializer` for `voice_ws` 的 Pipecat、框架自己的 HTTP 插件 for `http` 等）。首先配置框架；只有在传输固定的情况下才桥接。

快速规则：“相同的字节，不同的网络格式” = 传输桥接（允许）。“不同的字节 / 不同的形状” = 包装器（不允许）。

参考 [reference/infrastructure-patterns.md Pattern 9](reference/infrastructure-patterns.md#pattern-9-transport-bridge) 了解架构，参考 [reference/voice-channels.md](reference/voice-channels.md) 了解语音特定的应用。

### 向评分器报告客户端工具调用是一个受认可的例外（仅限语音代理）

这是唯一一个真正打破“没有 Veris 特定代码路径”规则的例外——这是故意的。它仅适用于**基于托管语音到语音平台的语音代理**（ElevenLabs Conversational AI、OpenAI Realtime、Gemini Live、Vapi 等等），其工具在代理进程中执行——作为**客户端工具**在供应商的 WebSocket 上往返，或作为 Vapi 风格的**服务器工具**，平台通过 HTTP POST 回到代理的 webhook。无论如何，调用永远不会到达语音转录。

为什么需要它：语音评分器从语音转录和代理报告的任何工具调用事件构建其跟踪。客户端工具永远不会到达转录，因此如果没有报告，评分器无法看到工具运行，并将真实操作（卡片冻结、替换）误报为幻觉。文本/HTTP 代理没有这个问题——它们的工具调用会自动捕获——所以这个例外仅限于语音。

修复方法：每次工具运行后，代理向沙盒引擎 POST 一个 `agent_tool_call` 事件，平台将其渲染到评分跟踪中。保持它严格最小化，使其保持为仪器，而不是包装器：

- **在模拟之外不执行无操作。** 基于 `SIMULATION_ID`（在生产中未设置→立即返回）。生产行为保持不变。
- **触发并忘记，软失败。** 短超时，吞掉错误，记录警告。报告失败绝不能中断调用或改变代理的输出。
- **观察，不要重塑。** 在真实工具运行后报告，将真实名称/参数/结果原样通过不变。它记录了发生的事情；它不会改变代理的行为或模型看到的内容。

仅为此客户端工具评分器的可见性、仅为此语音代理、并且仅为此最小化形状受认可——它不是通用填充代码的许可。确切的端点、事件模式和一个复制粘贴钩子在 [reference/voice-channels.md](reference/voice-channels.md#making-client-tool-calls-visible-to-the-grader) 中。

## 核心规则

- 在每个主要步骤之前解释你要做什么。
- 表面具有真实权衡的决定，并让用户选择。
- 引用仓库中的具体证据，当你对依赖项进行分类或决定如何集成代理时。
- 不要默默保留过时的 Veris 配置。将其迁移到当前首选的形状。
- 不要生成 `.env.simulation`。当前的运行时流程是 `agent.environment` 加上 `veris 环境变量设置`。
- 优先考虑当前的 `actor.channels` 模式和规范服务名称。除非用户明确要求兼容性，否则不要生成遗留的 `persona.modality`、`email_address` 或旧服务别名。
- 不要编写 Python 包装器、shell 填充代码或任何“适配器”代码，这些代码在 Veris 和代理之间进行转换。使用代理的真实生产接口。如果无法按原样实现，将其作为平台差距表面，而不是包装器机会。
- 在执行外部或不可逆操作之前询问：
  - 安装 `veris-cli`
  - 运行 `veris login`
  - 运行 `veris env create`
  - 使用 `veris env vars set` 设置环境变量
  - 使用 `veris env push` 推送

### 快速通道模式

如果用户说“全程执行”、“做所有事情”或以其他方式预先批准完整流程：

- 跳过中间检查点（Phase 2 结束、Phase 3 结束、Phase 4 结束）
- 仍然在执行决策时内联解释，以便用户可以跟踪
- 仍然在真正不可逆或外部操作之前停止并询问：`veris env create`、`veris env push`、`veris env vars set` 带有真实密钥
- 如果一个决策确实具有模糊的权衡（例如，捆绑与外部对于重型服务的权衡），即使在快速通道模式下也要暂停并询问
- 在结束时，呈现所有已做决策的汇总摘要

## 需要时阅读这些文件

- 对于当前服务名称和检测：[reference/service-mapping.md](reference/service-mapping.md)
- 对于环境覆盖和模拟凭证：[reference/env-var-overrides.md](reference/env-var-overrides.md)
- 对于可捆绑的本地基础设施：[reference/bundling-recipes.md](reference/bundling-recipes.md)
- 对于容器重构模式：[reference/infrastructure-patterns.md](reference/infrastructure-patterns.md)
- 对于语音代理（`voice_ws` 通道、框架选择、尾随静音、**向评分器报告客户端工具调用**）：[reference/voice-channels.md](reference/voice-channels.md)
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
| 6 | 配置运行时环境变量，验证并推送 |
| 7 | 使用单个场景 + 模拟进行冒烟验证 |

---

## 阶段 0：引导 Veris 工具和环境
[阶段 0/7]

告诉用户：“我将确保此仓库具有集成剩余工作所需的 Veris 工具和环境连接。”

### 0.1 验证仓库根目录

确认目录是一个代理仓库，而不仅仅是一个父文件夹。查找源代码、依赖项清单和应用程序入口点。

### 0.2 验证 `veris-cli`

检查 `veris` 是否已安装并正常工作。

如果未安装：
- 优先 `uv tool install veris-cli`
- 备用方案：`pip install veris-cli`

解释你使用的是哪个安装路径以及原因。

### 0.3 验证 Veris 身份验证

检查用户是否已经登录以及他们正在使用哪个配置文件/后端。

如果未身份验证：
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

`--self-serve` (`veris-cli >= 2.27.0`) 是此技能受众的正确模式：你正在自己编写 `.veris/`，并且环境应准备好立即用于 `veris env push`。如果没有它，`env create` 默认为管理设置模式，其中 Veris 团队为客户生成 `Dockerfile.sandbox` + `veris.yaml`，并且 `veris env push` 返回 `409: 运行 veris env submit 首先进行`，直到该设置完成。如果 `veris env create --help` 没有列出 `--self-serve`，请首先使用拥有 `veris` 的安装管理器（`uv tool upgrade veris-cli` 或 `pip install -U veris-cli`）升级 CLI。对于从已经使用 `--self-serve` 创建的环境恢复，请参阅 [phases/troubleshooting.md](phases/troubleshooting.md#veris-env-push-returns-409-managed-onboarding)。

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

告诉用户：“我将清单此仓库当前如何运行，它依赖什么，以及用户如何与之交互。”

### 1.1 现有的 Veris 状态

如果 `.veris/` 已经存在，首先读取所有现有的 Veris 文件。指出任何看起来过时或遗留的内容：
- `persona.modality`
- `email_address`
- 旧的服务名称，如 `crm`、`calendar`、`oracle`
- 缺少的 `.veris/config.yaml` 环境绑定
- 与当前文档冲突的假设

### 1.2 基础设施文件

读取并总结任何：
- `docker-compose.yml`、`docker-compose.yaml`、`compose.yml`
- `Dockerfile`、`Dockerfile.*`
- `Procfile`
- `supervisord.conf`、`supervisord.ini`
- `vercel.json`、`serverless.yml`、`netlify.toml`
- Kubernetes 清单

识别：
- 哪个进程是面向用户的代理
- 存在哪些其他服务
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
- 可选或仅调试

### 1.4 依赖项

读取仓库的语言/运行时的包清单，并识别：
- 包管理器
- 框架
- Python/Node 运行时假设
- 外部服务的 SDK

### 1.5 源代码入口点

找到处理用户传入工作的实际代码路径：
- 应用/服务器入口点
- 聊天/消息处理程序
- 配置/设置模块
- 请求路由
- 任何在用户对话期间重要的后台工作或 webhook 监听器

### 1.5a 平台托管代理（仅配置仓库）

如果仓库没有传统的应用程序入口点——没有 `main.py`、`app.py`、`server.js`、`index.ts`——检查它是否是**平台托管代理**：一个运行在已安装框架上的配置文件仓库（CrewAI、LangServe、AutoGen、Dify、n8n、Flowise 或类似）。

迹象：
- 主要文件是 YAML/JSON 配置、提示模板和工具定义
- `pyproject.toml` 或 `package.json` 将框架列为主要依赖项
- 没有实质性的应用程序逻辑，除了小的工具/钩子文件
- README 指令说“安装 [框架]，然后运行 [框架命令]”

如果是这种情况：
- 框架是运行时——它将在 Dockerfile 中安装，而不是从源代码构建
- 入口点是框架的 CLI 或服务器命令
- 参考在 `reference/infrastructure-patterns.md` 中的模式 8，了解完整的重构方法
- 如果在这些仓库上尝试 `pip install .`，注意源树编译错误

### 1.6 确定集成接口

这是关键的。确定模拟 actor 应该如何与代理交谈。

查找四类接口：

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
- 投票或 webhook 流程

**功能**
- 代理已作为其公共 API 的一部分公开的干净 Python 可调用项
- 代理自己的文档视为入口点的现有 `handle_message`-样式函数

不要通过包装 CLI 或服务器来发明一个函数接口。如果代理在生产中仅是 CLI，则集成是 CLI 驱动的——展示这一点并为其找到正确的 Veris 渠道，或将其记录为平台差距。只有当存储库已经作为其主要或记录的接口提供可调用项时，函数通道才是正确的。

如果网络模式和函数模式都可行，请使用存储库的真实产品接口。这就是在生产中运行的；这就是我们测试的。

告诉用户你发现了什么，并在继续之前确认最可能的集成路径。

进入第 2 步。

---

## 第 2 步：分析依赖项和服务策略
[第 2 步/7 步]

告诉用户：“我现在正在将每个依赖项分类为模拟、捆绑、外部或跳过。”

读取：
- [reference/service-mapping.md](reference/service-mapping.md)
- [reference/env-var-overrides.md](reference/env-var-overrides.md)
- [reference/bundling-recipes.md](reference/bundling-recipes.md)

对于每个依赖项，将其分类为以下之一：

1. **使用 Veris 进行模拟**
2. **在容器内捆绑**
3. **使用外部端点**
4. **完全跳过**
5. **需要讨论**
6. **允许真实出站**——代理必须能够连接到真实互联网（例如，网络搜索、URL 抓取、没有模拟的实时 API）。结果将在模拟运行之间是非确定性的。

### 分类规则

- 在做决定之前，始终阅读源代码。不要仅凭服务名称推断重要性。
- 当你决定某项内容可以跳过时，请提供证据。
- 当捆绑成本很重要时，尤其是在 Elasticsearch 或 LocalStack 等重型服务的情况下，展示捆绑成本。
- 当依赖项可以干净地映射到 Veris 时，优先使用模拟服务。
- 尽可能优先使用环境变量覆盖而不是代码更改。

### 特殊情况

**Postgres**
- 决定是使用 Veris `postgres` 还是外部数据库
- 如果使用 Veris `postgres`，请找到模式工件或迁移源，并确定最佳复制路径

**LLM 提供商**
- 不需要 Veris 服务入口
- LLM 代理会自动拦截支持的主机名

**电子邮件**
- 如果行为者使用电子邮件通道，请注意 Veris 电子邮件服务会自动注入

**身份验证辅助程序**
- Google/Microsoft/Atlassian/Intuit 身份验证辅助程序是平台级辅助程序，不是你应该通常手动添加的服务

**网络搜索和抓取**
- 如果代理调用搜索 API（Google、Bing、SerpAPI、Tavily、Brave Search、DuckDuckGo）或获取实时 URL，这些不能被模拟
- 分类为“允许真实出站”
- 警告用户：实时互联网调用会使模拟结果非确定性——相同的场景在不同的运行中可能会产生不同的输出
- 如果搜索是真正可选的（例如，当知识库没有答案时的回退），请考虑通过环境变量禁用它以进行确定性模拟

**真实互联网出站（一般）**
- 一些代理需要连接 Veris 无法模拟的任意外部端点（第三方服务的 webhook、实时数据源、没有 Veris 服务的公共 REST API）
- 这些也分类为“允许真实出站”
- Veris 容器默认允许非拦截域的出站互联网
- 向用户展示非确定性权衡

### 检查点

在进行依赖项分析之前，与用户一起走一遍。用户应该理解：
- 什么将被模拟
- 什么将被捆绑
- 什么保持外部
- 什么将被跳过
- 什么仍然需要决定

在继续之前等待批准。

继续进入第 3 步。

---

## 第 3 步：选择集成模式和容器架构
[第 3 步/7 步]

告诉用户：“我现在正在锁定代理如何在 Veris 容器中运行以及行为者如何与其通信。”

读取 [reference/infrastructure-patterns.md](reference/infrastructure-patterns.md)。

### 3.1 选择通道策略

选择以下之一：

- **HTTP**——当产品已经是 HTTP 聊天 API 时首选
- **WebSocket**——当实时状态化消息是核心时首选
- **电子邮件**——当产品是真正电子邮件驱动时首选
- **函数**——当存储库有一个干净的调用路径或应该被视为一次性请求/响应代理时首选

### 3.2 函数通道规则

如果你选择函数通道：
- 调用路径必须是代理存储库已经作为公共接口公开的内容（已记录、在它的 README 中引用，或否则是其合同的一部分）
- 不要创建一个包装文件，从 CLI 或服务器中凭空创建一个可调用项——如果存储库没有公开一个，函数就是错误的通道
- 在 `veris.yaml` 中省略 `agent.entry_point` 和 `agent.port`
- 如果可调用项是一次性且无状态的，请设置 `actor.config.MAX_TURNS: 1`

### 3.3 网络通道规则

如果你选择 HTTP / WS / 电子邮件：
- 确定确切请求和响应映射
- 确定启动命令
- 选择一个非保留端口
- 决定是否需要 `start.sh` 用于捆绑基础设施或多个进程

### 3.4 容器布局

确定：
- 什么将被复制到 `/agent`
- 哪些文件应该保持在镜像之外
- 是否需要一个 `start.sh` 来捆绑多个进程（这是容器编排，不是代理修改）

不要计划“哪些代码更改是必要的。” 目标是代理的零代码更改。如果环境变量覆盖不足以让代理按原样运行，那是一个发现——升级它而不是修补源代码。

### 检查点

解释：
- 行为者将如何与代理通信（使用代理的真实生产接口）
- 代理将如何在容器内启动（它的真实生产启动命令）
- 会复制哪些文件

如果你认为需要任何代理端代码更改，请在此处标记并停止。默认答案是零代码更改。如果你看不到没有一种方法可以前进，那可能是 Veris 平台差距，而不是集成步骤。

唯一的预先批准的例外：**客户端工具语音代理**（ElevenLabs 对话式 AI、OpenAI Realtime、Gemini Live、…）需要 `agent_tool_call` 报告挂钩，以便评分者可以看到它的工具——请参阅 [核心框架例外](#reporting-client-tool-calls-to-the-grader-is-a-sanctioned-exception-voice-agents-only) 和 [reference/voice-channels.md](reference/voice-channels.md#making-client-tool-calls-visible-to-the-grader)。这一个是可以预期的；添加它而无需升级。其他所有内容仍然在此处停止。

在继续之前等待批准。

---

## 第 4 步：生成 `.veris/veris.yaml`
[第 4 步/7 步]

告诉用户：“我现在正在生成当前首选模式的最终 Veris 配置。”

读取：
- [reference/veris-yaml-schema.md](reference/veris-yaml-schema.md)
- [templates/veris-yaml.md](templates/veris-yaml.md)

### 规则

- 使用 `actor.channels`，而不是 `persona.modality`
- 使用 `reference/service-mapping.md` 中的规范服务名称
- 使用 `agent_inbox`，而不是 `email_address`
- 仅在存在具体原因时设置 `actor.config.MAX_TURNS`，通常是一次性函数集成
- 除非用户明确要求高级调整，否则不要添加 `*_INTERVAL` 钮
- 将秘密保持在 `veris.yaml` 之外
- 将稳定的非秘密默认值放在 `agent.environment`
- 仅在需要扩展/组合时在 `agent.environment` 中使用 `${VAR}`；如果代理可以直接读取运行时环境变量，请优先使用 `veris env vars set` 设置它

### 通道特定规则

**HTTP / WS / 电子邮件**
- 包括 `agent.code_path`
- 包括 `agent.entry_point`
- 包括 `agent.port`

**函数**
- 包括 `agent.code_path`
- 省略 `agent.entry_point`
- 省略 `agent.port`
- 设置 `actor.channels[0].type: function`
- 设置 `callable: ...`

### 检查点

显示完整的 `veris.yaml`，解释各部分，并在写入或最终确定之前获得批准。

---

## 第 5 步：生成 `.veris/Dockerfile.sandbox` 和支持文件
[第 5 步/7 步]

告诉用户：“我现在正在生成镜像构建以及此集成所需的任何小型支持文件。”

读取：
- [templates/dockerfile-sandbox.md](templates/dockerfile-sandbox.md)
- [templates/start-sh.md](templates/start-sh.md)

### 5.1 Dockerfile 规则

- 以以下内容开始：

```dockerfile
ARG GVISOR_BASE
FROM ${GVISOR_BASE}
```

- 构建上下文是存储库根目录
- 在源代码之前复制依赖项清单
- 仅复制代理实际需要的文件
- 以 `WORKDIR /app` 结尾
- 不要将 `veris.yaml` 烘焙到镜像中

### 5.2 运行时说明

- 当前基础镜像已经包括 Python、`uv` 和 Node.js
- 仅在存储库确实需要时才安装额外的运行时或系统包
- 如果使用函数通道，您仍然正常打包代理代码和依赖项；您只是不启动网络服务器

### 5.3 支持文件

仅创建所需的文件：
- `start.sh` 用于捆绑多个进程（例如，数据库与代理一起）——这是容器编排，与 `docker-compose.yaml` 将会一样
- `.veris/.dockerignore` 更新，如果存储库有默认忽略文件遗漏的大目录

不要创建 Python“包装模块”，这些模块将代理作为可调用项公开，将 Veris 行为者调用转换为代理的本机格式，或以其他方式在行为者和代理之间插入自己。使用代理的真实接口。

### 5.4 代理无代码更改

代理在 Veris 中按其在生产中运行的方式运行。这意味着：
- 没有为了适应模拟而对源代码进行修补
- 没有“模拟模式”标志或 Veris 特定的分支
- 没有代理的本地修改的分支副本

如果你发现自己想要更改代理的源代码，请停止。要么：
- 更改可以表示为环境变量覆盖（然后以这种方式执行，通过 `agent.environment` 或 `veris env vars set`），要么
- 更改是代理中的一个真实问题（那么这是客户的责任来修复，并且也会影响生产），要么
- Veris 无法按原样容纳代理（那么这是一个平台差距——升级）

无关的重构显然是不允许的。

**唯一的批准源代码添加** 是语音代理的客户端工具报告挂钩（请参阅 [核心框架例外](#reporting-client-tool-calls-to-the-grader-is-a-sanctioned-exception-voice-agents-only)）。它是“无代码更改”的故意例外，而不是它的反例：它在模拟之外是无操作的，它永远不会改变代理的行为，并且它仅存在，以便评分者可以看到否则永远不会到达跟踪的客户端工具。为客户端工具语音代理添加它；不要将其推广到其他源编辑。

文件就绪后直接进入第 6 步。

---

## 第 6 步：配置运行时环境变量、验证并推送
[第 6 步/7 步]

告诉用户：“我现在正在将其转换为可推送的 Veris 环境。”

读取：
- [templates/env-vars.md](templates/env-vars.md)
- [phases/troubleshooting.md](phases/troubleshooting.md)

### 6.1 构建 env-var 计划

将环境变量分类为：

1. **稳定的非秘密默认值**→ 放在 `agent.environment`
2. **秘密/每个环境值**→ 使用 `veris env vars set` 设置
3. **本地仅便利值**→ 可选的根 `.env` 或 shell 导出，用于本地冒烟测试

不要创建 `.env.simulation`。

### 6.2 生成确切命令

生成用户需要的确切 `veris env vars set` 命令。

如果用户提供了实际值并希望您执行，请为他们运行命令。

**Shell 插值陷阱**：当运行 `veris env vars set KEY="$VAR" --secret` 并使用 shell 变量时，请先验证源变量是否实际设置（`printenv VAR` 或 `test -n "$VAR"`）。空值或未设置的变量会静默扩展为 `""`——CLI 会很高兴地保存一个空的秘密而没有错误，而代理将在运行时以令人困惑的身份验证/提供者错误而不是清晰的“缺少键”消息失败。

### 6.3 验证推送先决条件

推送之前，请验证：
- `veris` 已安装
- 身份验证/配置文件正常工作
- `.veris/config.yaml` 有一个环境 ID
- `.veris/veris.yaml` 存在
- `.veris/Dockerfile.sandbox` 存在

可选但鼓励：
- 在可能时运行本地 `docker build -f .veris/Dockerfile.sandbox .` 冒烟测试，以便快速捕获明显的损坏

### 6.4 推送

如果用户批准，运行：

```bash
veris env push
```

或者，如果用户想要一个明确的标签：

```bash
veris env push --tag <tag>
```

如果推送失败：
- 诊断失败的构建步骤
- 修复集成
- 重试

### 6.5 最终总结

总结：
- 创建或修改的文件
- 选择集成的模式
- 模拟、捆绑、外部或跳过的服务
- 设置的环境变量与用户保留的环境变量
- `veris env push` 是否成功以及创建了哪个标签

然后建议下一步命令：
- `veris scenarios create`
- `veris simulations create`

---

## 第 7 步：冒烟验证
[第 7 步/7 步]

告诉用户：“我将运行一个场景和一个模拟来验证端到端的集成是否正常工作。”

### 7.1 创建一个冒烟场景

```bash
veris scenarios create --num 1
```

目标是单个简短的交互，以锻炼代理的主要接口。

### 7.2 运行单个模拟

```bash
veris simulations create --scenario-set-id <id>
```

等待它完成。

### 7.3 检查结果

检查模拟以查看：

1. **代理以真实内容响应**——不是错误页面、空正文或异常跟踪
2. **模拟调用了模拟服务**——如果代理应该调用 Slack、Salesforce 等，请确认这些调用出现
3. **没有启动崩溃**——代理进程在持续时间内存活
4. **通道合同正确**——行为者的消息到达了代理，并且响应以预期的形状返回

### 7.4 诊断失败

如果冒烟测试失败：
- 检查代理容器日志以查找启动错误或缺少环境变量
- 验证 `actor.channels` 请求/响应映射与实际 API 形状匹配
- 确认模拟服务凭证和 DNS 别名正确
- 返回相关步骤进行修复并重新推送

### 7.5 签名
如果冒烟测试通过，总结：
- 行为者发送了什么以及代理响应了什么
- 哪些服务被锻炼
- 对集成已准备好进行完整场景生成的信心水平

然后建议完整场景生成 (`veris scenarios create --num N`) 和模拟作为下一步。

---

## 实用指南

### 优先考虑当前约定而不是过时的脚手架

如果 `veris env create` 搭建了看起来过时的占位符，请用此技能的当前首选形状覆盖它们。

### 对函数通道保持技能的诚实

仅在代理已经将其作为其公共接口的一部分公开可调用项时使用函数通道。不要因为看起来更简单而将网络产品强制到函数可调用项中，并且永远不要创建一个包装文件来凭空创建代理没有的可调用项。

### 对一次性代理保持技能的诚实

如果集成的代理显然是一次性/无状态的，请通过显式设置 `actor.config.MAX_TURNS: 1` 将这一点传达出来。

### 明确你未自动化的内容

如果登录、秘密或环境变量值仍然需要用户操作，请明确说明。目标是尽可能远，而不是隐藏障碍。
