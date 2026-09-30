---
name: vss-manage-video-io-storage
description: 用于调用 VIOS REST API（传感器列表、时间线、剪辑提取、快照、添加/删除传感器和流）。不用于 VLM 推理或搜索。
---

## 目的

管理 VIOS 和 NvStreamer API 操作，用于 VSS 视频输入/输出和存储工作流：传感器、流、上传、快照、片段、时间线和录制状态。

## 前置条件

- 可达 `$HOST_IP` 上的活动 VSS 部署（参见 `vss-deploy-profile` 和 `references/`）。
- 用于任何镜像拉取的 NGC 凭据在 `$NGC_CLI_API_KEY` 和 `$NVIDIA_API_KEY` 中。
- 调用者处可用 `curl`、`jq` 和 Docker。

## 说明

### VIOS 操作

调用 VIOS REST API 来管理相机/传感器、RTSP 流、录制、快照和存储。当被要求添加相机、添加 RTSP 流、列出传感器、显示配置的传感器/相机/流、检查流状态、获取快照、下载片段、上传视频文件或管理视频存储时使用。直接使用 curl 查询 VIOS API —— 不要导航 UI。

**上传路由规则：**
- 如果用户要求 "将 `<file>.mp4` 上传到 VIOS"、"上传视频文件"，或以其他方式将本地视频存储为 VIOS 文件支持的传感器，请使用直接 VIOS API：`PUT /vst/api/v1/storage/file/{filename}`，参考 [`references/api-reference.md`](references/api-reference.md) 第 8 节。
- 仅当用户明确需要实时/合成 RTSP 相机馈送、要求 NvStreamer 或要求检索 RTSP URL 时才使用 NvStreamer。
- 不要将 NvStreamer 上传 -> RTSP URL -> VIOS `/sensor/add` 的交接替换为普通的 VIOS MP4 上传请求。

**不要使用此技能进行：**
- VLM 推理或关于片段的临时视觉问答 — 使用 `vss-ask-video`。
- 跨存档的语义搜索，或为搜索摄取视频 — 使用 `vss-search-archive`。
- 录制片段的叙事摘要 — 使用 `vss-summarize-video`。
- 事件范围或警报窗口报告 — 使用 `vss-generate-video-report` 模式 B。
- 读取分析指标、事件或警报 — 使用 `vss-query-analytics`。

## 随此技能提供的参考合同

此技能捆绑了四个参考文件在 `references/` 下。阅读适用于您面前任务的文件：

| 文件 | 目的 | 对象 |
|---|---|---|
| [`references/api-reference.md`](references/api-reference.md) | 完整的 VIOS REST API 参考（运行时合同）— 传感器管理、存储、快照、片段提取、WebRTC 实时/回放、RTSP 代理、录制器、服务配置和服务发现。**调用任何 VIOS API 操作时阅读此文件。** | 操作用户 + 此技能本身 |
| [`references/nvstreamer-api-reference.md`](references/nvstreamer-api-reference.md) | **NvStreamer REST API 参考** — 版本、传感器列表/信息/状态/流、三种上传方法（PUT v2 / PUT v1 / POST 多部分）带有 `nvstreamer-*` 自定义头、删除、快照（基于帧索引的实时、基于时间戳索引的存储）、存储信息、文件系统扫描。NvStreamer (`vss-vios-nvstreamer`，`launch_vst` 的流适配器变体）由启动 VIOS 的相同配置文件启动 — `dev-profile-alerts`、`dev-profile-lvs`、`dev-profile-search`、所有仓库配置文件。有关部署方面的信息，请参阅 `integrate-vios-service.md § Topology B`。**在作为合成 RTSP 服务器提供测试/示例视频、检索 NvStreamer 为文件生成的 RTSP URL 或驱动规范 NvStreamer → VIOS 交接时阅读此文件**（上传到 NvStreamer → 读取 RTSP URL → 通过 `/sensor/add` 将该 URL 注册到 VIOS）。 | 操作用户 + 编写上传 → RTSP URL → VIOS `/sensor/add` 流的技能作者 |
| [`references/integrate-vios-service.md`](references/integrate-vios-service.md) | **集成合同** — VIOS 如何插入其他 VSS 微服务。记录所需的同级服务（RT-VLM、ELK、Kafka、Redis、`sdr-controller` / SDRC）、`vss-build-vision-agent` 技能的步骤 4 消费的结构化 `component_services:` 块、集成输入/输出（Kafka 主题、REST 端点、文件路径）、环境变量、网络要求和已知集成限制（例如 `/url` 变体的双 `http://` 错误、VIOS + SDRC 打补丁要求）。**在编写与 VIOS 作为同级通信的技能、编写新的 VSS 部署或调试字幕管道布线时阅读此文件。** | 技能作者、部署作曲家、pair-file 维护者 |
| [`references/deploy-vios-service.md`](references/deploy-vios-service.md) | **部署合同** — 启动 VIOS 需要什么。记录容器镜像和标签 (`nvcr.io/nvidia/vss-core/vss-vios-*:3.2.0`)、GPU / CPU / 内存 / 存储要求、启动行为 + 健康检查调整、所需环境变量（特别是 `VST_INSTALL_ADDITIONAL_PACKAGES=true` 用于 libav apt 安装步骤，该步骤控制上传）、已知部署问题（卷漂移、libav 缺失、来自遗留容器的 502）、先决条件、干运行、验证部署和拆除命令。**在 VIOS 未运行且您（或您的调用者）需要单独部署它时阅读此文件，或在调试容器启动失败时，或在编写包装 VIOS 的部署技能时阅读此文件。** | 操作员、部署技能作者 |

## 部署先决条件 — VIOS 必须在运行

此技能主要是一个 API 客户端，并假设 VIOS 已经在 VST 入口（默认 `http://${HOST_IP}:30888`）上运行且可访问。它本身不部署 VIOS，但当 VIOS 不可达时，它会使用捆绑的部署运行手册 ([`references/deploy-vios-service.md`](references/deploy-vios-service.md)) 协调部署，或转交给完整的 `/vss-deploy-profile` 技能。在执行任何工作之前：

1. **探测 VIOS：**
   ```bash
   curl -sf --max-time 5 "http://${HOST_IP}:30888/vst/api/v1/sensor/version" >/dev/null
   ```

2. **如果探测失败，VIOS 未部署。** 提供两个前进路径：

   > *"VIOS 在 `http://${HOST_IP}:30888` 上不可达 — 当前没有部署。您有两个选项：*
   > *(a) 使用此技能捆绑的 [`references/deploy-vios-service.md`](references/deploy-vios-service.md) 运行手册单独启动 VIOS — 图像标签、环境变量（特别是 `VST_INSTALL_ADDITIONAL_PACKAGES=true`）、主机目录、NGC 登录、启动命令、健康检查循环和已知部署问题都在那里记录。如果您只需要 VIOS 本身（不需要 RT-VLM / ELK / 等）或如果您正在编写自定义配置文件，这是正确的路径。*
   > *(b) 通过 `/vss-deploy-profile` 技能部署包含 VIOS 的完整 VSS 配置文件 — `base`（推荐）、`lvs`、`search` 或 `alerts` 都会与其他组件一起启动 VIOS。如果您想要完整的 VSS 堆栈，这是正确的路径。*
   > *您想要哪一个？*

   - 如果用户选择 (a) → 逐步引导他们完成 `references/deploy-vios-service.md`。特别注意其 `§ 环境变量 — 上传到字幕路径所需的` 和 `§ 已知部署问题` 部分 — libav 缺失失败 (`VST_INSTALL_ADDITIONAL_PACKAGES=true`) 和卷漂移挂起 (`docker compose up --yes` 或 `docker volume rm` 首先处理) 是最常见的启动障碍。部署成功后，步骤 1 中的探测通过，返回这里。
   - 如果用户选择 (b) → 转交给 `/vss-deploy-profile -p <profile>`（默认 `base`）。成功后返回这里。
   - 如果用户拒绝两者 — **停止**。VIOS 操作需要 VST 后端处于活动状态；不要尝试编造响应或以降级模式进行。

   *预授权自主模式：* 如果您的调用者已授予明确预授权来部署先决条件（例如，请求说 "已预授权部署先决条件"，或您正在使用具有该权限的非交互式评估托盘），则跳过确认并优先选择路径 (a) — 通过此技能捆绑的 `references/deploy-vios-service.md` 单独启动 VIOS — 除非请求明确要求完整的 VSS 配置文件，在这种情况下，调用 `/vss-deploy-profile -p base`。

3. **如果探测通过，继续。** VIOS 已启动；可以安全地执行以下所有操作。

---

## 已知限制 — 之前部署遗留的容器

`GET /vst/api/v1/sensor/list` 和 `GET /vst/api/v1/sensor/<sensorId>/streams`
在早期部署遗留的 `*-smc` VST 容器幸存并赢得 `network_mode: host` 端口绑定竞赛时，在 `:30000` / `:30888` 上返回 **HTTP 502 Bad Gateway** 或过时结果。**补救措施：重新运行 `/vss-deploy-profile`** — 其步骤 0 拆除的 grep 清除完整的 `sensor-ms-*` / `vst-ingress-*` / `sdr-*` / `sdrc-*` / `rtspserver-ms-*` 集合。其他路径（`storage/file/*` 上传、`*/picture/url` 快照、`*/url` 片段提取）不受影响。完整故障模式目录、补救措施和当前路由合同（直接 vs SDRC；SDR/Envoy 在 PR #711 中已移除）在 `references/deploy-vios-service.md § 已知部署问题` 和 [问题 #151](https://github.com/NVIDIA-AI-Blueprints/video-search-and-summarization/issues/151) 中记录。

---

## 设置

**基本 URL：** `http://<VST_ENDPOINT>/vst/api/v1`

**端点解析：**
- 使用与活动 VSS 部署关联的 VIOS 端点。此端点表示从 VSS 代理的运行时上下文可访问的 VST 后端。
- 不要尝试通过 shell 命令、文件系统访问或静态配置文件发现主机、IP 或端口。
- 假设 VSS 部署上下文已经提供了正确的 VST 网络端点。

**可用性检查：**
- 在进行任何 API 调用之前，验证通过 VSS 部署端点是否可以访问 VST 后端：
  ```bash
  curl -sf --connect-timeout 5 http://<VST_ENDPOINT>/vst/api/v1/sensor/version
  ```
- 如果后端不可用（非零退出代码或连接错误），则优雅地失败并向用户报告错误。有关部署或停止分支的详细信息，请参阅上面的 **部署先决条件** 部分。

**备用方案：**
- 如果从上下文无法获取端点信息，请明确要求用户提供 VST 端点（主机/IP 和端口）。

**运行所有 curl 命令** — 不要指示用户手动运行命令。

**认证：** 可选。大多数部署不使用认证。如果返回 `401`，请重试 `-H "Authorization: Bearer <token>"` 并要求用户提供令牌。

**开始/结束时间处理：** 任何需要 `startTime`/`endTime` 的 API：
- 如果用户提供它们，则直接使用这些值。
- 如果用户未提供它们，则首先获取相关流的时线以找到有效的录制范围，然后从响应中选择适当的值再调用 API。永远不要编造时间戳。

**解析 sensorId / streamId：** 如果用户未提供 sensorId 或 streamId，则自动使用以下之一查找：
- `GET /sensor/list` — 列出所有传感器及其 `sensorId`
- `GET /sensor/{sensorId}/streams` — 列出特定传感器的流及其 `streamId`
- `GET /sensor/streams` — 列出所有传感器的所有流
- `GET /live/streams` — 列出所有活动的实时流
- `GET /replay/streams` — 列出所有可用的回放流

如果一个传感器只有一个流，`sensorId` 和 `streamId` 是相同的，并且可以互换使用。

---

## 服务映射

| 功能 | URL 前缀 | 权威参考 |
|---|---|---|
| 版本 / 健康检查 | `/vst/api/v1/sensor/version` | `references/api-reference.md` |
| 传感器列表 / 信息 / 状态 / 添加 / 删除 | `/vst/api/v1/sensor/` | `references/api-reference.md` |
| 传感器流 | `/vst/api/v1/sensor/streams`, `/vst/api/v1/sensor/{id}/streams` | `references/api-reference.md` |
| 网络扫描 | `/vst/api/v1/sensor/scan` | `references/api-reference.md` |
| 录制时线 | `/vst/api/v1/storage/` | `references/api-reference.md` |
| 视频片段下载 / URL | `/vst/api/v1/storage/` | `references/api-reference.md`（操作）+ `references/integrate-vios-service.md § 已知集成限制`（查找 8：`/url` 双 `http://` 错误 — 优先使用二进制直接端点） |
| 文件上传 / 删除 | `/vst/api/v1/storage/` | `references/api-reference.md`（PUT v2 + 遗留 v1 端点）+ `references/deploy-vios-service.md § 已知部署问题`（查找 9：libav 缺失失败模式） |
| 实时流 / 快照（图片） | `/vst/api/v1/live/` | `references/api-reference.md` |
| 回放流 / 历史快照 | `/vst/api/v1/replay/` | `references/api-reference.md`（操作）+ `references/integrate-vios-service.md § 已知集成限制`（查找 8） |
| **NvStreamer**：文件到 RTSP 重新发布器（上传、检索生成的 RTSP URL、文件系统扫描、帧快照） | `http://${HOST_IP}:${NVSTREAMER_HTTP_PORT:-31000}/vst/api/v1/` | `references/nvstreamer-api-reference.md`（流器端点是**独立的**，与 VIOS 网关不同 — 不同的端口，`type: "streamer"` 在 `/version` 上） |

---

## 操作

完整的 VIOS REST API 参考 — 传感器管理、存储、快照、片段提取、WebRTC 实时/回放、RTSP 代理、录制器、服务配置和服务发现 — 存在于 [`references/api-reference.md`](references/api-reference.md)。调用任何操作时阅读该文件。

当请求涉及将磁盘上的视频文件作为合成 RTSP 相机提供时（上传样本到 NvStreamer、检索自动生成的 RTSP URL、将该 URL 注册到 VIOS），请指向 NvStreamer 端点并遵循 [`references/nvstreamer-api-reference.md`](references/nvstreamer-api-reference.md) 的表面。NvStreamer 随任何使用它的 VIOS 配置文件自动启动；不要单独部署它。

对于有关 VIOS 如何与其他微服务交互或如何启动的问题，分别参考 [`references/integrate-vios-service.md`](references/integrate-vios-service.md) 和 [`references/deploy-vios-service.md`](references/deploy-vios-service.md)（有关每个文件涵盖的内容，请参阅上面的 **参考合同** 表）。

如果你在`/url`变体响应的`imageUrl`或`videoUrl`字段中看到双重的`http://`前缀，那便是发现8——在客户端移除前导`http://`或切换到二进制直接端点。

---

## 示例

示例操作提示：
- "列出活跃的VIOS传感器并显示它们的流状态。"
- "将此示例视频上传到VIOS并返回生成的流ID。"
- "从此传感器的录制时间线下载两秒钟的片段。"
- "使用NvStreamer上传文件并检索其生成的RTSP URL。"

## 限制

- VIOS操作需要一个可访问的VST后端；当健康探测失败时，停止或部署先决条件。
- 大多数部署不需要认证，但部署可以添加外部认证层。
- 示例中的容器路径使用`${VST_CONTAINER_ROOT}`作为容器内VST安装根目录的中性占位符。在使用路径示例之前，从活跃部署中解析它。
- 不要在日志或最终响应中打印API密钥、令牌或生成的凭证。

## 故障排除

- **错误**：健康探测失败。**原因**：VIOS未部署或端点错误。**解决方案**：遵循部署先决条件流程或请求正确的VST端点。
- **错误**：上传失败并显示`Failed to get media information`。**原因**：VIOS容器中未安装libav软件包。**解决方案**：设置`VST_INSTALL_ADDITIONAL_PACKAGES=true`并重新部署。
- **错误**：`/url`响应包含`http://http://...`。**原因**：已知的URL构造缺陷。**解决方案**：使用二进制直接端点或移除重复的前缀。

---

## 提示

- **jq**：所有JSON响应都会通过`jq .`进行管道处理以提高可读性。二进制响应（片段下载、快照）不会——它们使用`-o <file>`代替。
- **时间格式**：始终使用ISO 8601 UTC，例如`2026-04-10T10:30:00Z`或`2026-04-10T10:30:00.000Z`。
- **streamId头部**：直播/回放/录制端点需要`streamId`作为路径参数和请求头部——两者都要包含。
- **大片段**：使用二进制直接`/storage/file/<id>?...&container=mp4`端点与`-o clip.mp4`进行直接流式传输。`/url`封装变体存在发现8的双重`http://`缺陷——避免使用直到上游修复它或使用客户端前缀移除。
- **传感器与流ID**：`sensorId`标识一个摄像头；`streamId`标识该摄像头的一个特定视频流（一个传感器可以有一个主流和子流）。
- **识别传感器类型（RTSP与上传文件）**：调用`GET /sensor/<sensorId>/streams`并检查每个流的`url`字段。如果`url`以`rtsp://`开头，它是一个直播RTSP/IP摄像头流。如果`url`是文件路径（例如`"${VST_CONTAINER_ROOT}/streamer_videos/TruckAccident.mp4"`），它是一个上传的文件传感器。这决定了要使用的删除流程——参见第8节。
- **上传时间戳用于录制时间线**：当通过`PUT /vst/api/v1/storage/file/<filename>?timestamp=<iso>`上传文件时，`GET /storage/<streamId>/timelines`返回的时间线锚定在提供的时戳，而不是上传的墙上时间。后续快照/片段查询必须使用此范围内的时戳——首先获取时间线。参见`references/api-reference.md § 8`和`references/integrate-vios-service.md § 集成接口 > 输入 > 上传视频文件`以获取权威合同。
- **端点解析**：VST端点由VSS部署上下文提供。不要尝试手动IP/端口发现。如果不可用，请询问用户。所有curl示例使用`<VST_ENDPOINT>`作为占位符——在执行前替换解析的端点。
