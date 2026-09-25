# Runpod (路由器)

Runpod 技能的入口点。该技能本身不执行任何工作，它只是选择正确的路径并将任务转交给其他技能。对于多步骤或配置任务，请先查看[已完成的示例](#已完成的示例-黄金路径)，让匹配的技能来选择路径；否则请阅读匹配技能的 `SKILL.md` 文件。

## 路径

| 路径 | 用于 |
|---|---|
| **runpod-mcp** | 通过**结构化工具调用**管理基础设施（Pod、端点、作业、模板、卷、注册中心、目录、计费）——当 Runpod MCP 工具在此会话中连接时。 |
| **runpodctl** | 从**终端/CI脚本**管理相同的基础设施，以及仅 CLI 才能执行的操作：Hub 浏览/部署、`send`/`receive` 文件传输、SSH 密钥、`doctor` 设置、模型缓存。 |
| **flash** | **编写 Python 代码**，使其在 Runpod 无服务器环境中运行——`@remote`/`@Endpoint` 函数、`flash dev` 热重载、`flash deploy`。以代码优先，而非基础设施管理。 |
| **companion-clis** | **前提工件**：下载模型（`hf`）、构建/推送镜像（`docker`）、仓库/发布（`gh`）、通过 S3 将数据移动到网络卷（`aws`）。 |
| **runpod-usage** | **了解** Runpod 的工作原理后再采取行动——Pod 与无服务器、构建容器、存储、GPU 选择、注意事项。仅包含知识。 |
| **runpod-templates** | **官方预构建 Pod 模板**（ComfyUI、PyTorch、…）：是否有适用于此工作负载的模板，以及其镜像包含的内容——端口、路径、自动启动、就绪状态、首次启动时缺少的内容。参考 + 路由 Hub；通过 runpod-mcp/runpodctl 部署。 |
| **runpod-migrate** | **将现有代码**从 GraphQL API 或 REST v1 移动到 REST v2——列出哪些部分使用哪个版本，重写调用位置，标记破坏性变更。编辑用户的代码；不管理基础设施。 |

## 这些技能只是快照；工具才是权威来源

下方的每个路径都封装了其自身发布列车中发布的某项内容，并且移动速度比此仓库更快。因此，使用这些技能进行路由，但**从你面前的工具中获取功能和语法**：

| 路径 | 直接询问 |
|---|---|
| runpodctl | `runpodctl --help`、`runpodctl <资源> <操作> --help`、`runpodctl version`。对于失败模式，故意运行错误命令并阅读 JSON |
| runpod-mcp | 你的客户端工具列表（Claude Code 中的 `/mcp`）——每个工具都携带其自己的参数描述 |
| flash | `flash --help`，以及部署/开发输出 |
| companion-clis | 该 CLI 自身的 `--help`（`hf`、`gh`、`docker`、`aws`） |
| runpod-templates | `runpodctl template list --type official`、`template get <id>`（其 README 是权威的） |
| REST v2 | 活跃规范，位于 `https://api.runpod.io/v2/openapi.json` |

**永远不要在未经检查的情况下告诉用户某个工具无法完成某项操作。** 缺少功能是最可能过时的声明，读者没有理由重新验证——它已经过时两次（runpodctl v2.9.0 添加了 `serverless health`，v2.10.0 添加了 `pod logs`/`serverless logs`）。如果限制仍然存在，请指明该限制适用于哪个版本，而不是说“无法完成”。

## 首次运行——在首次基础设施操作前检查认证

基础设施任务（Pod、端点、作业、卷）需要一个可工作的控制平面——**Runpod MCP** 或 **runpodctl**。不要在任务中途发现未设置就绪：先检查，如果未设置，则帮助用户设置，而不是依赖部分回退方案。

**检查**（凭证解析顺序：`RUNPOD_API_KEY` 环境变量 → `.env` → `~/.runpod/config.toml`）：
```bash
runpodctl user            # 成功 ⇒ 已设置并有效的密钥
```
此外，在 Claude Code 中，`/mcp` 应显示 `runpod` **已连接**。

**规则：先获取密钥——不要默认使用 MCP OAuth。** 原因：一个 `RUNPOD_API_KEY` 可以解锁所有工具——它认证 **runpodctl + flash + 托管的 MCP**（作为 `--header "Authorization: Bearer $RUNPOD_API_KEY"`）。MCP 的“使用 Runpod 登录”OAuth 仅认证 **MCP 本身**——CLI 仍然被阻止，因此你在任何仅 CLI 任务（Hub、`send`/`receive`、SSH、`doctor`、模型缓存/模型仓库、CPU 端点）上会遇到障碍。⚠️ **仅 OAuth 是半设置。** 如果未设置，请停止并获取密钥，按以下顺序：
1. **`flash login`** — 浏览器 OAuth，将真实密钥保存到 `~/.runpod/config.toml`（runpodctl + flash 读取它；用于 MCP Bearer）。一步到位，解锁所有功能。仅限人类操作。
2. **`export RUNPOD_API_KEY=…`**（https://console.runpod.io/user/settings）— 同样解锁所有功能；最适合无头代理。
3. **MCP OAuth 仅**（`/mcp` → *登录*）——最后手段，仅 MCP 工作任务；CLI 保持未认证。

**然后：** 如果某个路径已经工作，请使用它——但如果 *仅* MCP 已 OAuth，则在任何仅 CLI 步骤之前仍需获取密钥。缺少 CLI？`curl -sSL https://cli.runpod.net | bash`（runpodctl） · `uv tool install runpod-flash`（flash） · `npx @runpod/mcp-server@latest add`（MCP）。完整设置：[`runpod-usage/reference/getting-started.md`](../runpod-usage/reference/getting-started.md)。

## 如何路由

**0. 是否已有完成的示例涵盖此内容？** 对于任何超出单次调用的任务，在选择路径前检查[黄金路径索引](#已完成的示例-黄金路径)——匹配的路径已命名路径、标志、顺序和陷阱，因此路由变为阅读而非重新推导。当以下任何情况为真时，请检查：
- 任务需要**多个资源**（图像 + 模板 + 端点、Pod + 卷、多区域、…）或**多个路径**
- 它**配置可计费内容**，或用户的请求形如 *"让 X 运行/部署/工作"*
- 它涉及**存储、网络、自动扩展、流式传输或调试实时资源**——这些领域中的非明显顺序是整个难点
- 你即将为其编写**多步骤计划**

对于单次读取或单次 CRUD 调用（“列出我的 Pod”、“停止 Pod X”、“有哪些 GPU 可用”）跳过步骤 0——直接跳到路径。**匹配的黄金路径优先于此路由器的路径表**：它在真实账户上经过端到端验证，因此当两者不一致时，请遵循路径并将差异视为值得报告的 Bug。

1. **概念性问题，或未做的设计选择**（无服务器与 Pod？哪个 GPU？烘焙模型还是挂载卷？）→ 首先阅读 **runpod-usage**，然后继续执行答案。
2. **在 Pod 上运行常见工作负载或修复模板 Pod**（“运行 ComfyUI / PyTorch 开发箱”、“无法启动”、“缺少模型”）→ **runpod-templates**——在计划任何安装前检查是否有官方预构建，并让它在修复中路由。
3. **在 Runpod GPU 上编写/迭代/发布自己的代码** → **flash**。
4. **生成工件**（下载模型、构建+推送镜像、创建仓库发布、将数据同步到卷）→ **companion-clis**。
5. **在 Runpod API 版本之间迁移现有代码**——“让我们迁移到 REST v2”，“这个仓库基于哪个 Runpod API？”，“升级会破坏什么？” → **runpod-migrate**。（调用 API 执行操作是不同的工作；那是下方的基础设施路径。）
6. **管理基础设施**（创建/列出/更新/删除 Pod、端点、模板、卷；列出 GPU/数据中心；运行无服务器作业；计费）：
   - 仅 CLI 拥有的功能——**Hub、`send`/`receive`、SSH 密钥、`doctor`、模型缓存** → **runpodctl**。
   - 否则，如果在此会话中 Runpod **MCP 工具已连接**（`create-pod`、`list-endpoints`、… 可用）→ **runpod-mcp**。
   - 否则（仅 Shell 代理，无 MCP）→ **runpodctl**。

### runpod-mcp 与 runpodctl（重叠）

两者都驱动相同的 Runpod API，因此在基础设施 CRUD 上重叠。按**功能优先，环境次之**选择：

- **MCP 在简单、结构化操作上胜出**——读取和基本 CRUD——当其工具已连接时（类型参数，无需 Shell 引用）。
- **当操作需要 MCP 缺少的功能时 runpodctl 接管**——即使 MCP 已连接——并且是仅 Shell 代理或用户希望可重复命令的唯一选项。

功能矩阵（根据操作选择首选路径）：

| 操作 | 首选路径 | 原因 |
|---|---|---|
| 列出/获取任何内容；启动/停止/重启/删除 Pod；端点、模板、卷、注册中心、目录、计费的基本 CRUD | **runpod-mcp**（如果已连接），否则 runpodctl | 简单结构化操作——MCP 是类型的且方便 |
| 创建一个**简单**的 Pod（一个图像 + 一个 GPU） | **runpod-mcp**（如果已连接），否则 runpodctl | 两者都处理 |
| 从模板创建 Pod 或创建**CPU** Pod | **runpod-mcp**（如果已连接），否则 runpodctl | MCP 的 create-pod 接收 `templateId`（v2 仅限）和 `computeType: "CPU"` |
| 创建具有**多 GPU 优先级列表**的 Pod，或**模板 + CPU 一起** | **runpodctl** | MCP 仅限于一个 GPU 类型，并拒绝为 CPU Pod 部署模板 |
| 从 Hub 部署 | **runpod-mcp**（如果已连接），否则 runpodctl | MCP 有 `list-hub-repos` + `deploy-hub-repo` |
| **文件传输**（`send`/`receive`）、**SSH** 密钥/信息、**`doctor`** 设置、**模型**缓存 | **runpodctl** | MCP 没有这些工具 |
| 调用无服务器作业（`run`/`runsync`/status/stream） | **runpod-mcp**（如果已连接），否则 runpodctl | 两者路径现在都有一流的作业命令（runpodctl `serverless run`/`status`/`health`，v2.9.0+）；MCP 是类型的，并且仅 MCP 流式传输作业的增量输出（`stream-job`） |
| 读取**Pod 或工作器日志** | **任意**——runpod-mcp（如果已连接），否则 runpodctl | 两者路径都读取：MCP `stream-pod-logs`/`stream-worker-logs` 返回解析的帧；runpodctl `pod logs`/`serverless logs` 发送 json 行和 `--follow`（v2.10.0+） |

经验法则：**对于简单操作默认使用 MCP，一旦操作需要 MCP 未暴露的标志/功能，就转交给 runpodctl。**

## 部署工作负载（黄金循环）

对于任何“在 Runpod 上运行 <X>”任务，请遵循 `runpod-usage/reference/development-loop.md` 中的**开发循环**：决定 Pod 与无服务器 → 配置 → 设置（仅从零开始时）→ 验证 → 交付 → 成本保护 + 清理。其中包含两条规则：

- **优先选择预构建模板 / Hub 工作器，而非从零开始构建图像**——官方 Pod 模板在 [`runpod-templates`](../runpod-templates/SKILL.md) 中索引。
- **交付前，使用来自 Pod/端点外部的真实请求验证工作负载**——“运行中”/“就绪”状态并不意味着它在服务。

它分支到两个子循环：

- **在 URL 上公开的服务**（Ollama、ComfyUI、开发箱）→
  [`runpod-usage/reference/pod-workflows.md`](../runpod-usage/reference/pod-workflows.md)
  （创建时端口 + 环境变量 + 卷，SSH 执行安装，绑定 `0.0.0.0`，轮询代理 URL）。在 runpodctl 路径中执行。
- **可扩展到零的请求/响应 API**（Whisper、推理）→
  [`runpod-usage/reference/endpoint-workflows.md`](../runpod-usage/reference/endpoint-workflows.md)
  （Hub 工作器与 flash 与自定义图像；调用 `/run`/`/runsync`；轮询作业状态）。

## 已完成的示例（黄金路径）

这是**路由的步骤 0**，不是附录。大约二十多个端到端场景（几乎所有**在真实账户上经过验证**）位于
[`./golden-paths/README.md`](./golden-paths/README.md)，包含真实命令和可复制观察输出——此外还有 Gotchas 和成本与清理部分，这部分重新发现成本很高。

**将任务与下方的一行匹配，并在计划或调用任何内容前打开该路径。** 部分匹配仍然值得打开：最接近路径的顺序和 Gotchas 通常即使模型、GPU 或区域不匹配时也能转移。只有在以下情况下才需要跳转到上方的路径表：此处没有接近的路径。

| 想要… | 黄金路径 |
|---|---|
| 在 Pod 上运行服务器（Ollama/ComfyUI） | [01](./golden-paths/01-ollama-pod.md)、[02](./golden-paths/02-comfyui-pod/README.md) |
| 部署无服务器模型端点（Hub / flash / 自定义图像） | [03](./golden-paths/03-whisper-endpoint/README.md)、[05](./golden-paths/05-model-to-endpoint-pipeline.md) |
| 未经烘焙或卷缓存（主机缓存）的服务 HuggingFace 模型 | [20 — 模型缓存（`--model-reference`）](./golden-paths/20-model-caching-endpoint.md) |
| 调用就绪的托管模型（无需部署） | [11 — 公共端点](./golden-paths/11-public-endpoints.md) |
| 微调，然后服务结果 | [04](./golden-paths/04-finetune-pod.md)、[08](./golden-paths/08-finetune-to-serverless.md) |
| 交互式开发箱（SSH / VS Code） | [06](./golden-paths/06-dev-pod.md) |
| 数据 Pod → 卷 → 无服务器 | [07](./golden-paths/07-network-volume-handoff.md) |
| **自定义无服务器（当 flash 不足时**）（双模式图像开发循环） | [09](./golden-paths/09-custom-serverless-dev-loop/README.md) |
| 为目标构建最小图像（Pod 与无服务器队列） | [22 (Pod)](./golden-paths/22-minimal-pod-image/README.md)、[23 (队列)](./golden-paths/23-minimal-queue-image/README.md)；概念在 [building-images](../runpod-usage/reference/building-images.md) |
| 决定将什么烘焙到图像中，还是挂载到网络卷 | [25 — 烘焙与挂载](./golden-paths/25-bake-vs-mount/README.md) |
| 选择网络卷的**存储层**（标准与高性能） | [21 — 存储层](./golden-paths/21-storage-tiers.md) |
| **高可用性/多区域**无服务器（多卷 + 数据同步） | [10](./golden-paths/10-multi-region-ha-serverless.md)、[19 (3 区域)](./golden-paths/19-three-region-same-file.md) |
| 逐步流式传输输出（`/stream`） | [12](./golden-paths/12-serverless-streaming.md) |
| 调整自动扩展 / 提高每个工作器的吞吐量 | [13 (自动扩展)](./golden-paths/13-autoscaling-tuning.md)、[18 (并发)](./golden-paths/18-concurrent-handler.md) |
| 负载均衡 / HTTP 服务器或 WebSocket 工作器 | [14 (负载均衡)](./golden-paths/14-load-balancing-endpoint.md)、[17 (WebSocket)](./golden-paths/17-serverless-websocket.md) |
| 完成作业时接收通知（推送，非轮询） | [16 — Webhooks](./golden-paths/16-serverless-webhooks.md) |
| 检查健康状态 / 调试失败的端点 | [15 — 监控与调试](./golden-paths/15-monitor-and-debug.md) |

## 多路径任务

顺序始终是 **理解 → 生成工件 → 管理基础设施 → 验证**，因为基础设施只能引用已存在的工件。将每一步保持在一条路径中，并在凭证边界处切换路径。

示例——“将 `openai/gpt-oss-20b` 部署到无服务器端点”：
1. **runpod-usage** — 无服务器与 Pod，20B 的 GPU 层级，烘焙与挂载与缓存。
2. **companion-clis** — `hf download …`，`docker build --platform=linux/amd64 …`，`docker push`。
3. **runpod-mcp** 或 **runpodctl** — 创建端点，引用图像 + GPU 池。
4. 相同的基础设施路径——调用端点 / 检查状态以验证。

## 认证

所有内容都是一键：**`RUNPOD_API_KEY`**（https://console.runpod.io/user/settings）。每个路径只是使该密钥可解析——`runpodctl doctor`，`flash login`，MCP 标准输入环境变量，或 MCP 托管的“使用 Runpod 登录”（OAuth，磁盘上无密钥）。
Companion CLIs 使用它们**自己的**凭证（HuggingFace 令牌，GitHub 认证，Docker Hub PAT，Runpod **S3** 密钥用于 `aws`）——不要用 `RUNPOD_API_KEY` 用于这些。
