# LiveAPI 服务技能

此技能提供生成 **LiveAPI 客户端服务类** 的说明，该客户端通过 WebSocket 连接到 Gemini Enterprise Live API。生成的客户端处理双向流、通过应用默认凭证 (ADC) 的令牌认证、透明会话恢复以及 `ClientMessage` / `ServerMessage` proto 交换。

该技能还会生成一个演示前端 + 后端服务，以便用户可以交互式地验证生成的客户端（文本、音频、视频、转录和中断处理）。

## 前置条件

在运行生成流程之前，确保主机上已提供以下内容：

-   一个启用了 Vertex AI / Gemini Enterprise Agent Platform API 的 Google Cloud 项目。
-   在运行生成的客户端的主机上配置了应用默认凭证：

    ```bash
    gcloud auth application-default login
    ```

-   用户提供的目标输出文件夹（例如 `/tmp/liveapi_out`），其中将写入生成的代码、环境和演示。**绝对不要**修改主机的系统 Python 环境。

-   用户选择的自定义实现语言（Python 是此技能的默认和参考语言）。

## 参考文件

`references/` 中的提供文件（**不要**将其视为独立的技能——它们按需加载）：

-   `client_server_messages.md`：Live API 使用的 `ClientMessage` /
    `ServerMessage` 模式的公共参考。
-   `client_server_messages.proto`：从 `client_server_messages.md` 生成的 proto 定义。
-   `session_manager.md`：描述如何在断开连接时正确处理会话、缓冲和恢复。

## 步骤

### 第 1 步：复制参考文件

将 `client_server_messages.md`、`client_server_messages.proto` 和
`session_manager.md` 从此技能的 `references/` 文件夹复制到用户的目標输出文件夹。这些文件成为生成客户端的真理来源。

### 第 2 步：与公共文档核对

检查从 `client_server_messages.md` 链接的公共文档。如果公共文档与复制的
`client_server_messages.md` / `client_server_messages.proto` 之间存在任何差异，请更新目标文件夹中的副本，以便生成的客户端与当前服务器合约编译和运行。

### 第 3 步：实现客户端类

使用用户选择的语言实现一个类，该类应：

-   导入本地 `client_server_messages.proto` 类型（`ClientMessage`、
    `ServerMessage`）。
-   打开到 Live API 端点的 WebSocket 连接。
-   提供异步方法，以便用户可以向/从模型发送和接收数据。

对于需要隔离运行时（例如 Python）的语言，在目标文件夹**内部**创建隔离环境（例如 `venv`），并生成一个 bash 脚本（例如 `setup.sh`），该脚本重新创建环境并安装依赖项。**绝对不要**安装到系统解释器或用户的全局 site-packages，并且**绝对不要**指示用户运行 `sudo pip install`。

#### 初始化参数

用户在构造时提供以下内容：

-   `project_id`
-   `location`
-   `model_id`
-   `config`：一个 `ClientMessage`，其中 `setup` 字段已填充。

#### 认证

通过应用默认凭证获取令牌，将其附加到 WebSocket 连接请求作为 `Authorization: Bearer <token>`，在过期前或过期时刷新令牌，并在每次重新连接时（包括 `go_away` 和意外的断开连接）重用刷新的令牌。**不要**将长生命周期的 API 密钥作为唯一的认证机制硬编码。

#### 公共异步 API

该类**必须**在发送之前接收 `setup_complete` `ServerMessage` 时暴露以下异步方法：

-   `send_realtime_data(data)`：发送实时输入。`data` 是一个包含 `realtime_input` 字段的 `ClientMessage`。
-   `send_client_content(data)`：发送非实时、回合制的内容，该内容有助于构建历史记录。`data` 是一个包含 `client_content` 字段的 `ClientMessage`。
-   `receive()`：从 WebSocket 流中解析 `ServerMessage` 实例。

不要作为主要 API 表面暴露同步阻塞变体。

### 第 4 步：编写测试文件

一旦实现了客户端，就生成一个测试文件，该文件初始化连接并执行发送 `text`、`audio` 和 `video` 数据以及接收响应的操作。询问用户运行测试所需的任何信息（项目、模型、媒体样本）。

### 第 5 步：生成 `how_to_run.md`

在目标文件夹中提供 `how_to_run.md`，其中记录了生成的类。包括完整示例，展示如何为每个支持的模式构建 `ClientMessage` 负载，如何发送它们，以及如何从模型接收数据。

### 第 6 步：生成演示前端 + 后端服务

创建脚本，将实现作为具有前端 UI 和后端服务（任何语言）的服务进行部署。该服务**必须**重用第 1 步中的 `ClientMessage` / `ServerMessage` proto 用于线缆流量。通过 UI，用户应该能够：

-   开始新的连接 / 关闭当前连接。
-   选择要使用的模型。
-   选择输入源（来自相机或屏幕的音频和/或视频）并将它们流式传输到模型。
-   向模型发送文本消息。
-   听到模型音频并看到交错模型和用户转录/对话历史记录。

在实现音频和转录播放时，请遵循 [Live API 最佳实践](https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/live-api/best-practices) 的指导。

#### 处理 `interrupt` 信号

当 `ServerMessage` 的 `server_content` 到达且 `interrupted: true` 时，UI 必须：

-   确保播放的音频及其对应的转录保持时间对齐。
-   立即停止当前播放的模型音频并停止向正在进行的转录气泡追加。
-   清除未播放的音频缓冲区和任何待处理的未渲染转录，以防止过时的内容渗入下一个回合。
-   为下一个用户和模型回合开始新的聊天气泡。

#### 处理转录 `finished` 信号

对于流式传输的 `input_transcription` / `output_transcription` 片段，在 `finished` 未设置时追加到当前活动的气泡，并在观察到 `finished` 时关闭该气泡并开始一个新气泡。将 `input_transcription` 文本路由到用户角色气泡，将 `output_transcription` 文本路由到模型角色气泡。

### 第 7 步：生成 `how_to_test_with_ui.md`

编写 `how_to_test_with_ui.md`，描述如何启动和使用演示服务。它**必须**包括：

-   启动后端服务的确切 shell 命令或脚本调用的命令。
-   启动前端 UI 的确切 shell 命令或脚本调用的命令。
-   用户应在浏览器中打开的主机名和端口（例如 `http://localhost:PORT`）。
-   如何启动会话、选择模型、选择输入源（麦克风、相机、屏幕）、发送文本消息以及观察 UI 中的模型音频和转录。

## 验证清单

在考虑生成完成之前，验证每个项目：

-   [ ] `client_server_messages.md`、`client_server_messages.proto` 和
    `session_manager.md` 被复制到目标文件夹。
-   [ ] 生成的客户端导入本地 proto 生成的 `ClientMessage`
    和 `ServerMessage` 类型。
-   [ ] 客户端连接到 Live API WebSocket 在
    `wss://{location}-aiplatform.googleapis.com/ws/google.cloud.aiplatform.v1beta1.LlmBidiService/BidiGenerateContent`
    （或 `wss://aiplatform.googleapis.com/...` 全局变体），并将 setup `model` 字段格式化为
    `projects/{project_id}/locations/{location}/publishers/google/models/{model_id}`。
-   [ ] 认证使用 ADC 提供的令牌作为 `Authorization:
    Bearer <token>` 发送，在过期前刷新，并在每次重新连接时重新附加。
-   [ ] 公共异步方法 `send_realtime_data`、`send_client_content` 和
    `receive` 存在，类型正确，并且受 `setup_complete` 控制。
-   [ ] 透明会话恢复已启用
    (`session_resumption.transparent = true`)，跟踪最新的 `new_handle`，发送消息索引从 1 开始，通过
    `last_consumed_client_message_index` 修剪缓冲区，并在重新连接时重播缓冲消息（包括在 `go_away` 和 WebSocket 关闭代码 1000 / 1006）。
-   [ ] 如果使用 python，目标文件夹内部存在隔离环境（例如 `venv`）加上 `setup.sh`
    和 `requirements.txt`（或等效文件）；未对系统或用户全局 Python 进行任何更改。
-   [ ] `how_to_run.md` 和 `how_to_test_with_ui.md` 存在，并且演示 UI 重用了相同的 `ClientMessage` / `ServerMessage` proto。
-   [ ] 中断处理和转录 `finished` 处理行为如上所述。
-   [ ] 客户端**不**针对 `generativelanguage.googleapis.com`，并且**不**通过查询字符串进行 API 密钥认证。
