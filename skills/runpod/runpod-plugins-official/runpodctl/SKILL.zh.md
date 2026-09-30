---
name: runpodctl
description: 用于从终端管理 GPU/CPU 工作负载的 Runpod CLI —— 支持Pod、无服务器端点、模板、网络卷、Hub部署、模型、SSH和文件传输（发送/接收）。适用于终端/CI脚本、Hub浏览/部署、SSH设置、`doctor`命令，或当Runpod MCP工具无法连接时使用。在支持MCP的会话中进行结构化工具调用时，请优先使用`runpod-mcp`。
---

# Runpodctl

管理 GPU 聚合、无服务器端点、模板、卷和模型。

## 安装

`curl -sSL https://cli.runpod.net | bash`（Linux/macOS，以及通过 WSL 的 Windows）或 `brew install runpod/runpodctl/runpodctl`。手动二进制文件和 Windows 以及 conda 步骤位于 [runpodctl README](https://github.com/runpod/runpodctl#install) 中，位于 `install.sh` 旁边。命令界面来自二进制文件 — `runpodctl <资源> <操作> --help` — 或生成的页面在 [`runpodctl/docs/`](https://github.com/runpod/runpodctl/tree/main/docs) 下。

> 旧的 runpodctl 构建（例如 `--model-reference` 在 v2.4.0 之前不存在）会静默缺少更新的标志/行为，并产生令人困惑的下游错误 — 并且 Homebrew 转发程序可能会严重落后。因此，在进行任何工作之前：
>
> - **更新到最新版本** — 检查 `runpodctl version`，然后运行 `runpodctl update`（或从 [最新发布](https://github.com/runpod/runpodctl/releases) 重新安装）。
> - **针对整个任务固定一个最近版本**。
> - **在任务中途不要在旧版本和新二进制文件之间切换**（这种切换是已知的故障）。
> - **验证一次** — `runpodctl version` 在你继续之前显示当前构建。

## 快速入门

```bash
runpodctl update                    # 首先：获取最新版本 — 旧版本会导致令人困惑的错误
runpodctl version                   # 在进行任何工作之前确认当前版本
export RUNPOD_API_KEY=your_key      # 非交互式认证（代理）— runpodctl 会读取此值
runpodctl doctor                    # 交互式首次设置（API 密钥 + SSH）— 供人类使用
runpodctl --help                    # 查看当前顶级命令
runpodctl pod create --help         # 在创建之前检查确切的当前标志
runpodctl gpu list                  # 查看可用的 GPU 类型
runpodctl datacenter list           # 每个数据中心 GPU 的可用性（用于将 GPU 与卷一起放置）
runpodctl hub search vllm           # 查找 hub 仓库
runpodctl serverless create --hub-id <id> --name "my-vllm"  # 从 hub 部署
runpodctl template search pytorch   # 查找模板
runpodctl pod create --template-id runpod-torch-v21 --gpu-id "NVIDIA GeForce RTX 4090"  # 从模板创建
runpodctl pod list                  # 列出你的聚合
```

> 认证：代理应该 `export RUNPOD_API_KEY=...`（非交互式）。`runpodctl
> doctor` 是交互式（提示）的，并且还设置了 SSH 密钥 — 适合人类的首次运行，不适用于脚本使用。

API 密钥：https://console.runpod.io/user/settings

## 实时帮助是权威的

实时 `runpodctl --help` 输出对于确切的标志、别名和命令语法是权威的。使用此技能来创建工作流程、决策规则、安全说明和常见示例。

```bash
runpodctl --help
runpodctl <资源> --help
runpodctl <资源> <操作> --help
```

在使用不熟悉的命令之前，请先检查实时帮助。不要依赖此技能作为详尽的标志参考。

**实时帮助不涵盖的内容：** 输出形状、错误代码和退出代码行为。`--help` 列出标志；它永远不会显示失败的样子。对于这些，使用 [reference/output-and-errors.md](reference/output-and-errors.md) — 并且当不确定时，**检查二进制文件**：故意运行错误的命令 (`runpodctl serverless get nope`) 并读取它发出的 JSON。每份文档都是快照，包括此技能；你面前的二进制文件优先。

## 输出和错误

数据是 **stdout 上的 JSON** (`--output=yaml` 是唯一的替代方案 — 没有表格格式；任何其他内容都会静默返回 JSON）。资源命令的失败是在 **stderr** 上返回单个扁平的 JSON 对象加上 **非零退出**：

```jsonc
{"error":"failed to get endpoint: endpoint not found","code":"not_found","status":404}
```

**基于 `code` 分支，而不是 `status` 或消息。** `status` 仅在失败通过非 2xx 响应到达时存在 — GraphQL 将缺少的资源报告为 HTTP 200 + null 数据，因此 `if status == 404` 会错过所有 GraphQL 未找到的情况。

| `code` | 应该做什么 |
| --- | --- |
| `network_error` | **使用退避重试** — 唯一表示“无法到达 API”的代码 |
| `rate_limited` `server_error` | **使用退避重试** — 来自 API 的 429/5xx |
| `usage_error` `cli_error` `bad_request` `not_found` `conflict` | 不要重试，修复输入 |
| `no_credentials` | 未设置密钥：`export RUNPOD_API_KEY=…` 或 `runpodctl doctor` |
| `unauthorized` `forbidden` | 已设置密钥，但错误/过期或权限不足 — 不要重试，不要重新提示缺少的密钥 |
| 任何其他内容 | 视为致命，原样显示 `error` — API 可以传递它自己的代码 |

**runpodctl 从不内部重试**；没有任何东西为你退避。

- **`not_found` 总是表示 API 缺少资源，而不是拼写错误的本地路径（那是 `cli_error`）。**
- **`cli_error` 是一个混合桶**：本地环境问题 *和* 调用错误 — 命令会自行验证（例如 `ssh remove-key` 而没有 `--name` 或 `--fingerprint`）。只有 cobra 强制的必需标志是 `usage_error`。
- **`usage_error`** = 未知命令/标志、参数错误、缺少 cobra 必需标志；使用文本跟随 JSON。运行时错误不再打印使用说明。
- **非空的 stderr 不表示失败** — 退化 `warning:` 和 `note:` 行在成功时也会发送到 stderr。基于退出代码，然后解析 stderr。

编码错误、无服务器 `urls` 对象和 GPU 定价都需要 **runpodctl ≥ v2.8.0**。旧二进制文件发出 `{"error":"…"}`，**没有 `code` 和没有 `status`** — 仍然是 JSON 形状，因此 `switch (err.code)` 静默得到 `undefined` 而不是大声失败。**基于 `code` 存在**，而不是 JSON-与纯文本；`runpodctl version` 对于此目的不可靠（纯文本，并且源构建报告占位符版本）。

完整代码表、仍然打印纯文本的界面（`exec`、遗留 `pod` 命令、`project`）以及环境变量表（包括 `RUNPOD_INVOKE_URL`）：
**[reference/output-and-errors.md](reference/output-and-errors.md)**。

## 决策规则

- 当用户想要一个已知的可部署应用或工作器（例如 vLLM、ComfyUI、Whisper 或 Runpod 维护的仓库）时使用 Hub。
  - **选择工作器**：优先选择 **第一方或广受欢迎、最近发布的** 工作器在 **广泛、高可用性的 GPU 池** 上。通过 `runpodctl hub list` 观察：`--owner runpod-workers`（第一方）、`--order-by releasedAt`/`updatedAt`（最新）、`--order-by deploys`/`stars`（采用）。不要将稀缺的大 GPU 层固定给不需要的小模型。
- **“活动工作器” = 最小工作器，而不是最大。** 如果用户要求“活动工作器”，他们指的是 `--workers-min 1`（始终保持一个工作器热着 → 无冷启动），**而不是** `--workers-max 1`（那只是上限）。一个热的最小 1 个工作器对于开发/迭代是理想的。
- ⚠️ **最小 1 个工作器会持续计费，即使空闲**（它会破坏零扩展）。当你在开发中设置 `--workers-min 1` 时，你**必须**在完成时将其改回 `--workers-min 0`（或删除端点） — 否则它会静默增加成本。
  - **需要 runpodctl ≥ v2.10.0。** 在旧二进制文件上 `--workers-min 0` 和 `--idle-timeout 0` 被**静默忽略**从更新请求中（`omitempty` 吃掉了零），因此重置看起来像它应用了，端点继续计费。检查 `runpodctl version`；在旧二进制文件上通过 `serverless get <id>` 确认，并回退到 `PATCH https://rest.runpod.io/v1/endpoints/<id>` 带有显式的 `{"workersMin":0}`。
- `serverless update` 没有 `--gpu-id` 标志。要更改现有端点的 GPU 池，请直接调用 `PATCH https://rest.runpod.io/v1/endpoints/<id>` 带有 `{"gpuTypeIds":[...]}`。
- **CPU 无服务器端点**：始终使用 `runpodctl serverless create --compute-type CPU` 创建它们 — **不是** MCP 服务器，其 v2 `create-endpoint` 需要 `gpuPoolIds` 并且没有 CPU 概念。**永远**不要使用公共控制 REST `POST https://rest.runpod.io/v1/endpoints` 带有 `"computeType":"CPU"` — 它会静默配置一个 **GPU** 端点（在 Serverless 命令部分下方有验证证据）。
- 当用户已经有一个模板 ID、想要可重用的镜像/配置默认值或需要比 Hub 更低级别的控制时使用模板。
- 当用户有一个特定的 Docker 镜像并且不需要保存模板时使用 `--image` 直接创建聚合。
- 使用无服务器来处理请求/响应推理 API 和可扩展工作器；使用聚合来处理交互式工作、笔记本、训练、调试或长时间运行的会话。
- 使用 CPU 聚合进行预处理、文件移动、轻量级脚本和非 CUDA 工作。当需要 CUDA、模型推理、训练或 GPU 内存时使用 GPU 聚合。
- 在创建 CPU 聚合时不传递 GPU 标志。检查 `runpodctl pod create --help` 以获取当前有效的标志集。
- **等待资源可用：使用 `--wait`，不要手动编写轮询循环**（v2.9.0+）。`create` 一旦资源被*调度*就返回，这就是为什么“正在运行”的聚合经常拒绝 ssh 并且新的端点 404。`pod create --wait` 返回端口 22 回答 ssh 标志时；`serverless create --wait` 返回 `/health` 报告就绪或运行的工作器时。超时或 ctrl-c 资源被**保留**，并且其 id 在错误对象的 `id` 字段中 — 读取它并清理，不要假设什么没有被创建（聚合按秒计费；没有运行工作者的端点不收费，但会在第一个请求时启动一个）。
- 在聚合上**启动一个服务**（Ollama、ComfyUI、一个开发服务器）？在创建时声明它的 `--ports` 和 `--env` **（不能在运行的聚合中添加，需要重置）**，然后遵循聚合开发循环（在 `runpod-usage` 技能中 `reference/pod-workflows.md`） — SSH 执行安装，绑定到 `0.0.0.0`，并轮询代理 URL 直到它回答。
- 对于 SSH，使用 `runpodctl pod get <pod-id>` 或 `runpodctl ssh info <pod-id>` 来检索连接详细信息。runpodctl 没有 `interactive-shell` 命令 — `ssh info` 返回连接命令 + 密钥，但不会连接。使用 `ssh user@host "command"` 自己通过 SSH 运行命令。
- 网络卷是位置敏感的。在附加卷之前检查数据中心可用性，并使用 `send` / `receive` 或 S3 兼容存储进行迁移。
- 测试后清理付费资源：删除无服务器端点、聚合和为验证创建的临时卷。
  - **创建时的成本保护**：使用 `--terminate-after`（删除聚合）；`--stop-after` 仅*停止*它，因此磁盘/卷继续计费。
  - **附加卷**：要删除网络卷，请先删除使用它的聚合。

### 无服务器事实（背景，不是规则）

- **零扩展计费**：无服务器端点通过 `--workers-min 0`（默认值）扩展到零 — 空闲时不计 GPU 费用，只有按请求-秒计费；这是请求/响应 API 的正确成本姿态。
- **损坏镜像迹象**：如果部署的工作器进入 `ready` 但工作停留在 `IN_QUEUE` 且 `inProgress: 0`，则镜像损坏/错误调度 — 修复方法是切换到不同的工作器，而不是等待它。
- **诊断它**：使用 `runpodctl serverless health <endpoint-id>`（v2.9.0+）读取工作器/工作计数，然后使用 `runpodctl serverless logs <endpoint-id>`（v2.10.0+）读取工作器实际打印的内容 — 不需要手动构建 curl。重复的 `system` “启动容器”行而没有 `container` 输出意味着容器在处理程序运行之前退出 — 工作随后停留在队列中，容量没有问题。

## 命令

以下是基本命令。**对于标志，询问二进制文件** — `runpodctl <资源> <操作> --help`，它按构造是当前的。[reference/command-reference.md](reference/command-reference.md) 包含 `--help` 无法回答的部分：标志成功时的含义、要信任的字段以及失败的样子。

### 聚合

```bash
runpodctl pod list                                   # 运行的聚合 (+ --all / --status / --since / --created-after)
runpodctl pod get <pod-id>                           # 详细信息，包括 SSH 信息 + 运行时状态
runpodctl pod create --template-id <id> --gpu-id "NVIDIA GeForce RTX 4090"   # 从模板创建
runpodctl pod create --image <img> --gpu-id "NVIDIA GeForce RTX 4090"        # 从镜像创建
runpodctl pod create --compute-type cpu --image ubuntu:22.04                 # CPU 聚合（小写的 `cpu`；无服务器使用 `CPU`）
runpodctl pod create --image <img> --gpu-id <id> --wait                      # 阻塞直到 ssh 回答，然后打印聚合 (v2.9.0+)
runpodctl pod {start|stop|restart|reset|update|delete} <pod-id>              # 生命周期（删除别名：rm/remove）
runpodctl pod logs <pod-id>                          # 最近容器+系统日志，json 行 (v2.10.0+)
runpodctl pod logs <pod-id> --follow                 # 保持流式传输，自行重新连接
runpodctl pod logs <pod-id> --since 30m --source system   # 平台视图：镜像拉取 / 创建 / 启动
```

**一个停滞的部署显示在 `--source system`** (v2.10.0+)：重复的拉取进度，或一个从未达到 `start` 的 `create container`。使用 `--source container` 来获取你工作负载自己的输出。每一行是一个 `{source,line,ts}` 对象，因此直接将其管道到 `jq`。

**决定聚合是否可用时不读取 `runtimeStatus`，而是读取 `desiredStatus`** (v2.9.0+)：`desiredStatus: RUNNING` 表示镜像仍在拉取。字段含义、原因标记和两个边缘（`--status` 仅过滤 `desiredStatus`；`unknown` = 查找失败，不是聚合宕机）→ [reference/command-reference.md](reference/command-reference.md#pod-status-fields)。

### Hub

浏览/搜索 Runpod Hub（精选的可部署仓库）。

```bash
runpodctl hub search vllm                            # 查找仓库 (+ hub list [--type/--category/--order-by/--owner])
runpodctl hub get <listing-id|owner/name>            # 仓库详细信息
```

### 无服务器（别名：sls）

```bash
runpodctl serverless list | get <endpoint-id> | delete <endpoint-id>
runpodctl serverless create --name "x" --template-id <id>       # 从模板创建
runpodctl serverless create --name "x" --hub-id <listing-id>    # 从 hub 创建 (+ --env KEY=VAL 来覆盖默认值)
runpodctl serverless create --hub-id <id> --gpu-id "NVIDIA GeForce RTX 4090" \
  --model-reference https://huggingface.co/<org>/<model>:main   # 附加并缓存一个 HF 模型（仅 GPU）
runpodctl serverless update <endpoint-id> --workers-max 5
runpodctl serverless create --template-id <id> --workers-min 1 --wait          # 阻塞直到一个工作器就绪 (v2.9.0+)
```

**调用 URL 随端点返回。** `create`/`get`/`list`/`update` 包括一个 `urls` 对象 (`run`, `runsync`, `health`)，因此一个新创建的端点无需第二次查找即可调用 — 读取它们而不是自己组装 URL。它们是从 `RUNPOD_INVOKE_URL`（默认 `https://api.runpod.ai/v2`）构建的，`RUNPOD_API_URL`/`RUNPOD_GRAPHQL_URL` **不会移动**：[reference/output-and-errors.md](reference/output-and-errors.md#serverless-invoke-urls)。

**读取工作器日志** (v2.10.0+) — 也是一流的，因此工作器输出不再需要 MCP 槽或手动构建 SSE 读取：

```bash
runpodctl serverless logs <endpoint-id>                       # 每个工作器的最近日志，json 行
runpodctl serverless logs <endpoint-id> --worker <worker-id>  # 只有一个工作器
runpodctl serverless logs <endpoint-id> --follow              # 在跟随期间选择新扩展的工作器
runpodctl serverless logs <endpoint-id> --since 1h --source system   # 为什么工作器不会启动
```

日志属于一个**工作器**，而不是端点，因此如果没有 `--worker`，它会一次性读取所有并标记每行 `workerId`。**崩溃循环迹象**：重复的 `system` “启动容器”行而没有 `container` 输出意味着容器在处理程序运行之前退出 — 工作随后停留在队列中，容量没有问题。

**调用端点** (v2.9.0+) — 一流的命令，因此代理不会手动构建 curl 请求或管理 bearer 令牌：

```bash
runpodctl serverless run <endpoint-id> --input '{"prompt":"hello"}'   # 提交并等待结果
runpodctl serverless run <endpoint-id> --input-file payload.json      # 相同，payload 来自文件 ("-" = 标准输入)
runpodctl serverless run <endpoint-id> --input '{}' --wait 15m        # 更长的预算（默认 5m）
runpodctl serverless run <endpoint-id> --input '{}' --no-wait         # 提交，打印排队中的任务，退出 0
runpodctl serverless status <endpoint-id> <job-id>                    # 检查之前提交的任务
runpodctl serverless health <endpoint-id>                             # 工作节点 + 任务计数
```

- **仅提交处理负载** — CLI 会将其包装为 `{"input": <your json>}`，所以
  复制整个 curl 封装会双重包装。
- **`timeout` 意味着 CLI 停止等待，而不是端点出错了。** 当消息
  指明 `serverless status` 命令时，任务仍在服务器端运行 — 请轮询它，**不要** 重新调用（那样会购买第二个任务）。

负载规则、stdout/stderr 分割、退出代码以及为什么 `/runsync` 从未被使用 →
[参考/命令参考.md](reference/command-reference.md#调用端点-serverless-run-v290)。

**从中心创建：** `--hub-id` 解析中心列表，提取构建镜像和配置（GPU ID、容器磁盘、环境变量），创建内联模板并部署。接受 SERVERLESS 和 POD 列表类型。GPU ID 和环境变量默认值来自中心配置，使用 `--gpu-id` 和 `--env` 覆盖。

**CPU serverless 端点**（上述决策规则中的始终/从不规则）：使用 `runpodctl serverless create --compute-type CPU` 创建（可选 `--instance-id`，例如 `cpu3g-4-16`）。公共 REST 必须不使用的验证证据：2026-07-14，`POST https://rest.runpod.io/v1/endpoints` 使用 `"computeType":"CPU"` 静默返回 GPU 端点（`gpuCount:1`，`cpuFlavorIds:null`），而 `runpodctl --compute-type CPU` 正确返回 `computeType:"CPU"` 并包含 `instanceIds:["cpu3g-4-16"]`。MCP 服务器在此处**不是**替代方案：其 v2 `create-endpoint` 需要 `gpuPoolIds`，而 v2 规范根本没有 `computeType`/`cpuFlavor` 字段（验证 2026-07-29）。公共控制 REST 仅限 v1（`rest.runpod.io/v2` 仅重定向到文档）。分离的**运行时/调用** API `https://api.runpod.ai/v2/<endpoint-id>/…`（健康/运行/运行同步/openai）是不同的 v2，工作正常 — 此处的 v1-v2 限制仅适用于**控制/管理** REST。

**模型缓存（`--model-reference`）：** 通过完整 URL 和引用将 Hugging Face 模型附加到端点，例如 `https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct:main`。Runpod 在标准 HF 缓存目录（`/runpod-volume/huggingface-cache/hub/`）主机端缓存它，因此工作节点直接加载它 — 无需烘焙，无卷。可重复；适用于 `--template-id`/`--hub-id`、GPU 仅、**runpodctl v2.4.0+**。完整机制以及它如何与烘焙 / 网络卷 / 模型存储库比较：**[参考/模型缓存.md](reference/model-caching.md)**。端到端工作：黄金路径 [20 — 模型缓存端点](../runpod/golden-paths/20-model-caching-endpoint.md)。

**多区域 / 高可用性（`--network-volume-ids`）：** 附加**多个**网络卷（每个数据中心一个），以便工作节点跨数据中心分布而不是固定在一个 —
`runpodctl serverless create --template-id <t> --network-volume-ids <v1>,<v2> --data-center-ids <dc1>,<dc2> …`。
**需要 runpodctl ≥ v2.4.0**（旧版本不支持多卷附加）。检查 `runpodctl version`；Homebrew tap 可能会滞后，因此优先考虑
[GitHub 发布](https://github.com/runpod/runpodctl/releases) 二进制文件。数据在卷之间**不会**自动同步 — 见黄金路径
[10 — 多区域 HA serverless](../runpod/golden-paths/10-multi-region-ha-serverless.md)。

对于确切的 serverless 标志，运行 `runpodctl serverless <action> --help`。

### 模板（别名：tpl）

```bash
runpodctl template search <q>                        # 查找 (+ 模板列表 [--type 官方/社区/用户, --all, --limit])
runpodctl template get <template-id>                 # 详情（README、环境、端口）
runpodctl template create --name "x" --image "img" [--serverless]
runpodctl template delete <template-id>
```

### 网络卷（别名：nv）

```bash
runpodctl network-volume list                         # 列出所有卷
runpodctl network-volume get <volume-id>              # 获取卷详情
runpodctl network-volume create --name "x" --size 100 --data-center-id "US-GA-1"  # 创建卷
runpodctl network-volume update <volume-id> --name "new"  # 更新卷
runpodctl network-volume delete <volume-id>           # 删除卷
```

对于确切的网络卷标志，运行 `runpodctl network-volume <action> --help`。

> **没有存储层标志。** `create` 分配数据中心的**默认**层 — 没有 `--type`。要获取**高性能**卷，使用控制台（⚡ 数据中心的切换开关）
> 或原始**v2 REST**调用（`POST https://v2-rest.runpod.io/v2/network-volumes` 使用
> `"type":"HIGH_PERFORMANCE"`）— 或 MCP `create-network-volume` 工具，它接受
> `volumeType` (`STANDARD` | `HIGH_PERFORMANCE`)。层在创建后不可变。启动详情：黄金路径 [21](../runpod/golden-paths/21-storage-tiers.md)。

### 模型（模型存储库）

`runpodctl model` 管理您的**Runpod 模型存储库** — 您自己的模型工件（上传一次，分发到工作节点；不像网络卷那样固定在数据中心）。这是什么，为什么/如何，从烘焙模型迁移，以及模型存储库与卷的比较：**[参考/模型缓存.md](reference/model-caching.md)**。

```bash
runpodctl model list                                  # 列出您的模型
runpodctl model list --all                            # 列出所有模型（不仅仅是您的）
runpodctl model list --name "llama"                   # 按名称筛选
runpodctl model list --provider "meta"                # 按提供者筛选
runpodctl model add --name "my-model" --model-path ./model   # 上传本地模型目录（多部分）
runpodctl model remove --name "my-model" --owner <owner>     # 删除模型
```

`model add` 支持上传会话、版本控制、元数据和私有源凭证 — 见实时 `runpodctl model add --help`。

### 信息 & SSH

```bash
runpodctl user                                       # 账户信息 + 余额（别名：me）
runpodctl gpu list                                   # 可用 GPU + $/小时 + 每个数据中心的库存 (+ --include-unavailable)
runpodctl datacenter list                            # 数据中心（别名：dc）
runpodctl ssh info <pod-id>                          # SSH 连接详情（命令 + 密钥；**不是**交互式会话）
```

**`gpu list` 包含定价和位置数据** — `securePricePerHr` /
`communityPricePerHr`（当该云不提供 GPU 时显式为 `null`）和 `dataCenterAvailability[]` 分解。在必须在一个特定数据中心调度创建时，请阅读分解，而不是仅查看顶层
`stockStatus`（它仅是跨数据中心的*最佳*状态），并通过 `--include-unavailable`，因为默认列表隐藏无库存 GPU，并且可能省略您想要的数据中心中的库存。价格是**按 pod 按需**的费率。形状、库存值词汇和 `"none"` 与省略键哨兵：
[参考/输出和错误.md](reference/output-and-errors.md#gpu定价和每个数据中心的可用性)。

`ssh info` 提供连接详情，而不是会话 — 如果交互式 SSH 不可用，请运行 `ssh user@host "command"`。**注册认证、`billing` 历史和 SSH 密钥管理** (`ssh add-key`/`remove-key`) 在 [参考/命令参考.md](reference/command-reference.md)。

### 文件传输

```bash
runpodctl send <path>                                # 打印一次性代码，然后阻塞，直到接收者连接
runpodctl receive <code>                             # 位置代码（没有 --code 标志）
```

加密/增量/压缩 — 不要预先 tar。**密钥注意事项：** 捕获 `send` stdout 的**第一行**（代码）作为它流式传输（后台 + tee），每个 `send` 都会铸造一个**新的**代码，两边的都必须退出 `0`。完整代理流程（通过 `ssh` 的 pod 推送 + `receive`）：[参考/命令参考.md](reference/command-reference.md#文件传输)。

### 实用工具

```bash
runpodctl doctor                                      # 诊断和修复 CLI 问题
runpodctl update                                      # 更新 CLI
runpodctl version                                     # 显示版本
runpodctl completion                                  # 自动检测 shell 并安装完成
```

## URL

### Pod URL

访问您的 pod 上的暴露端口：

```
https://<pod-id>-<port>.proxy.runpod.net
```

示例：`https://abc123xyz-8888.proxy.runpod.net`

### Serverless URL

优先使用 `runpodctl serverless run|status|health`（上述） — 相同 API，带有身份验证、验证和有界轮询处理。用于命令未涵盖的内容的原始 URL：流式传输、OpenAI 兼容路线，或用户 `curl` 的复制粘贴。

```
https://api.runpod.ai/v2/<endpoint-id>/run        # 异步请求
https://api.runpod.ai/v2/<endpoint-id>/runsync    # 同步请求
https://api.runpod.ai/v2/<endpoint-id>/health     # 健康检查
https://api.runpod.ai/v2/<endpoint-id>/status/<job-id>  # 任务状态
```

`serverless create`/`get`/`list`/`update` 已经返回 `run`/`runsync`/`health` 在一个
`urls` 对象中 — 优先使用这些而不是手动组装，因为非默认
`RUNPOD_INVOKE_URL` 会改变基础。只有 `status/<job-id>` 需要手动构建。

## 来源 & 文档

- CLI 源代码：https://github.com/runpod/runpodctl
- 发布（二进制文件）：https://github.com/runpod/runpodctl/releases
- 文档：https://docs.runpod.io/runpodctl/overview
