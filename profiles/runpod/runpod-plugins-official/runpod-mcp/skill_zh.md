# Runpod MCP

Runpod MCP 服务器将 Runpod 的控制平面以结构化工具调用的形式暴露出来，因此支持 MCP 的代理可以无需使用 shell 即管理基础设施。它是 `runpodctl` 使用的相同 Runpod REST API —— 当其工具连接时（参数类型化、结构化错误、无需 shell 引号）请选择 MCP。

**对于多步骤任务，调用工具前请先阅读示例。** 工具调用很容易发出，也很容易以错误顺序发出 —— 已验证的端到端序列位于 [runpod/golden-paths/README.md](../runpod/golden-paths/README.md)（图像→模板→端点，Pod→卷→无服务器，多区域，自动扩展，监控）。这项技能涵盖了每个工具的作用；路径涵盖了执行顺序和成本。

## 连接

如果你也使用 runpodctl/flash，请使用 **你的 API 密钥作为 Bearer 头**连接托管服务器（这是 80% 的路径）：

```bash
claude mcp add --transport http runpod -s user https://mcp.getrunpod.io/ \
  --header "Authorization: Bearer $RUNPOD_API_KEY"
```

纯 **OAuth**（"使用 Runpod 登录"，通过 `npx @runpod/mcp-server@latest add`）仅适用于 MCP —— CLIs 保持未认证状态，因此仅用于纯 MCP 工作。本地 **stdio** 以子进程形式运行服务器并使用你的密钥。这些变体以及密钥与 OAuth 的权衡：**[reference/connect.md](reference/connect.md)**。连接后，重新连接客户端（在 Claude Code 中为 `/mcp`），以便加载工具。

**验证其是否运行中（在依赖 MCP 之前执行此操作）：** 在 Claude Code 中运行 `/mcp` —— `runpod` 应显示 **已连接**，而不是 *需要认证*（如果是后者，请先在那里登录；捆绑的插件服务器注册了 URL 但在认证前保持惰性）。通过请求 `list-endpoints` 确认真实调用是否正常工作。如果 `runpod` 工具完全不存在，则服务器未连接 —— （重新）运行上述安装，或回退到 **runpodctl** 完成此任务。

**检查服务器版本（它驱动的 REST API）：** MCP 的 `initialize` 握手返回 `serverInfo.version`。Claude Code 中的 `/mcp` 显示它，或直接探测托管服务器：

```bash
printf '%s\n' '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe","version":"0"}}}' \
| curl -s -X POST https://mcp.getrunpod.io/ -H "Content-Type: application/json" \
    -H "Accept: application/json, text/event-stream" -H "Authorization: Bearer $RUNPOD_API_KEY" -d @-
# → serverInfo.version 例如 "3.0.0 [RUNPOD_REST_VERSION=v2]"  (验证于 2026-07-29)
```

MCP 服务器内部驱动 Runpod 的 **REST v2**（`RUNPOD_REST_VERSION=v2`），因此大多数工具避免使用有问题的 **公共 `rest.runpod.io/v1`** 控制 API。两个值得了解的例外：Hub、public-endpoint 和 `set-endpoint-gpus` 工具通过 GraphQL（因此它们在任一 REST 版本下都有效），以及 **CPU 无服务器端点无法通过 MCP 创建** —— v2 完全没有 CPU-endpoint 概念（`create-endpoint` 需要 `gpuPoolIds`），因此对于这些情况使用 `runpodctl serverless create --compute-type CPU`。

**优先选择 MCP 或 `runpodctl` 而不是手动的 `rest.runpod.io/v1` 调用来创建端点。**

## 工具界面

按资源分类的结构化工具：

- **Pods** — 列出、获取、创建、更新、启动、停止、重启、删除、流式传输日志。
- **无服务器端点** — 列出、获取、创建、更新、删除；列出工作者；列出发布；流式传输工作者日志。
  - **日志不再仅限于 MCP 功能** —— runpodctl 在 v2.10.0 中增加了 `pod logs` 和 `serverless logs`。MCP 仍然返回已解析的、有界的帧，这在代理内部更容易处理；当仅使用 shell 或需要 `--follow` 时使用 CLI。作业 *输出* 流式传输（`stream-job`）仍然是 MCP 唯一的功能。
  - `create-endpoint` 接收 `endpointType: QUEUE`（默认）或 `LOAD_BALANCER` —— 参见黄金路径 14。路由类型在创建时固定；`update-endpoint` 无法更改它。
  - 从获取/列出回复的 `requestUrls` 中读取端点的调用 URL，而不是自行组装。
  - 要在现有端点上固定特定 GPU **SKU**，请使用 `set-endpoint-gpus`；`create-endpoint`/`update-endpoint` 仅暴露 `gpuPoolIds` 并且无法表达 SKU（`deploy-hub-repo` 可以在部署时通过 `gpuIds` 排除来固定一个）。
- **作业（无服务器运行时）** — 运行、runsync、状态、流式传输、取消、重试、健康检查、清除队列。
- **Hub** — `list-hub-repos`（预构建无服务器工作者和 Pod 模板的公共目录：vLLM、ComfyUI、…）和 `deploy-hub-repo`，后者将仓库列出的发布作为端点部署 —— 与在 Hub 上点击部署相同。
- **公共端点** — `list-public-endpoints`：管理按使用付费模型 API（文本/图像/视频/音频）无需部署。使用返回的 `endpointId` 与 `run-endpoint`/`runsync-endpoint` 调用。
- **模板** — 列出、获取、创建、更新、删除。
- **网络卷** — 列出、获取、创建、更新、删除。`create-network-volume` 接收 `volumeType`（`STANDARD` | `HIGH_PERFORMANCE`）和 10–4096 GB 的大小；省略 `volumeType` 以获取数据中心的自定义级别。级别在创建后**不可变** —— `update-network-volume` 无法更改它。
- **容器注册器认证** — 列出、获取、创建、删除。任何注册器的用户名+密码；在创建 Pod/创建端点时传递生成的 id 作为 `containerRegistryAuthId`。
- **ECR 委托**（`list-`/`create-`/`delete-registry-delegation`）—— **仅限 AWS ECR**，v2 仅限，并且不存储凭证：你注册一个仓库 ARN，Runpod 获得范围限制的拉取访问权限。优先于存储用户名/密码用于 ECR。回复包含 `dockerRegistryUri` —— 那是部署时使用的镜像 URI。
- **目录** — 列出/获取 GPU 类型、列出/获取 CPU 类型、列出/获取数据中心。

> 上述工具列表是一张地图，不是合同。服务器是事实来源 —— `/mcp`（或你客户端的工具列表）显示连接的版本暴露的确切内容，并且每个工具都携带自己的参数描述。在假设功能存在或不存在之前，请先查看那里。

> 删除工具（`delete-template`、`delete-pod`、…）即使成功也可能返回 `isError: true` 并带有 "Unexpected end of JSON input" —— Runpod REST API 返回 204 No Content。不要将其视为失败；通过后续的 `get-`/`list-`（已删除资源会 404）进行确认。

## 使用 MCP 与 runpodctl

- 当工具连接**且**任务是基础设施 CRUD 或服务器无服务器作业调用时，请使用 **runpod-mcp**。将大型作业/日志输出限制到文件。
- **使用 runpodctl** 而不是：**`send`/`receive`** 文件传输、**SSH** 密钥管理、**`doctor`** 设置、**模型缓存** —— 或任何仅使用 shell 的代理，或当用户希望获得可重复的命令时。
- **将 Pod 创建交给 runpodctl** 用于 **多 GPU 优先级列表**（MCP 的 v2 `create-pod` 接收一个 GPU 类型；额外的 `gpuTypeIds` 在成功时被丢弃并带有 `_warning`），或用于 **模板+CPU** Pod 一起 —— `create-pod` 拒绝这种组合，因为模板部署仅限于 GPU 和 v2。单独使用每个都很好：`templateId`（v2 仅限，`imageName` 然后可选，并且你传递的每个字段都会替换模板的整个值而不是合并）或 `computeType: "CPU"`。
- **不在此路径上**：编写/部署你自己的 Python（→ flash）；下载模型或构建/推送镜像（→ companion-clis）。

对于概念（Pod 与无服务器、GPU 选择、存储），请阅读 `../runpod-usage/`。

## 源码与文档

- 服务器源码：https://github.com/runpod/runpod-mcp
- 包（npm）：https://www.npmjs.com/package/@runpod/mcp-server
- 托管端点：https://mcp.getrunpod.io/
- 文档：https://docs.runpod.io
