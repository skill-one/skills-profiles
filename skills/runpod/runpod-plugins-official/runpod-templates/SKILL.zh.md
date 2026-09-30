---
name: runpod-templates
description: Runpod 官方预制 Pod 模板（ComfyUI、PyTorch 等）：各镜像内置了哪些内容、使用哪些端口和路径、如何选择模板、如何固定版本，以及首次启动时哪些配置缺失。当任务描述为“在 Pod 上运行 <X>”且官方模板已涵盖该场景时，优先使用模板而非自建镜像；当用户需要协助或修复其正在运行的 Runpod 模板相关问题（无法启动、无法访问 UI、缺少模型、CUDA 参数错误、导入的工作流中 ComfyUI 元数据损坏等）时：从此处入手，再按需路由至对应流程。使用 runpodctl 或 runpod-mcp 进行部署；端到端的完整操作指南位于 runpod 路由器的黄金路径中。
---

# 官方 Runpod 模板

**优先选择官方模板，而不是自行构建镜像。** Runpod 维护着针对常见工作负载的预构建镜像；部署一个镜像只需创建并轮询，无需 SSH 安装步骤。这项技能是关于*这些镜像实际内容*的参考。它不管理基础设施 — 部署时请使用 **runpod-mcp**（如果已连接）或 **runpodctl**。

## 术语 — "模板" 与 Hub 的区别

有两个不同的产品共享 "Hub" 这个词，混淆它们会导致发现困难：

| 术语 | 它是什么 | 以何种形式运行 | 如何发现 |
| --- | --- | --- | --- |
| **Pod 模板**（此技能） | 一个保存的 Pod 配置 — 镜像 + 端口 + 磁盘 + 环境变量。官方模板出现在 Console **Hub 模板页面** (`console.runpod.io/hub/template/<id>`) 上 | 一个 **Pod** | `runpodctl template list --type official` / `template search` · REST `GET /v2/catalog/templates` |
| **Hub 仓库 / 列表** | 一个打包的 **无服务器工作进程**（例如 `runpod-workers/worker-comfyui`）带有处理程序，部署为端点 | **无服务器** | `runpodctl hub list` / `hub search` · MCP `list-hub-repos` / `deploy-hub-repo` |

同一个词，但目录是分离的：`hub search comfyui` 仅返回无服务器工作进程，而不会返回任何官方 ComfyUI **Pod** 模板，而 `template search` 不会返回任何 Hub 仓库。在 REST v2 目录中，Pod 与无服务器模板通过每个条目的 `serverless` 标志区分。

## "官方" 的含义以及如何查找它们

当模板报告 `isRunpod: true` 时，它就是 Runpod 维护的。搜索结果中的任何其他内容都是社区发布的：可用，但不受此技能支持，且版本没有保证。

```bash
runpodctl template list --type official   # 完整的官方集合（截至 2026-08-25 为 14 个）
runpodctl template search <name>          # 按名称查找；检查 isRunpod: true
runpodctl template get <template-id>      # 镜像、端口、portsConfig、磁盘 + 完整的 readme
```

`template get` 返回模板的 **readme** — 与镜像一起维护的描述，当它与此技能不一致时，这是权威答案。从这些命令中获取镜像标签、端口和环境变量，而不是从这些文件中获取：模板有自己的发布版本，移动速度比这个仓库更快。参考文件记录的是**形状和注意事项**，这是重新发现时最昂贵的部分。

⚠️ **`runpodctl hub ...` 不是查找 Pod 模板的方法** — 请参阅 [术语](#terms--template-vs-the-hub)。

要向用户提供一个 Console 链接，请使用 `https://console.runpod.io/hub/template/<template-id>`。

### REST v2 没有模板搜索 — 只有你自己过滤的切片

REST v2 没有模板的查询/搜索参数，因此每个“搜索”都是客户端对获取切片的过滤：

| 端点 | 参数 | 返回 |
| --- | --- | --- |
| `GET /v2/catalog/templates` | `source=official\|verified\|community`（默认 `official`） | 公共目录切片 |
| `GET /v2/templates` | 无 | 仅你拥有的模板 |
| `GET /v2/templates/{id}` | — | 一个模板，属于你或目录 |

**`official`（14）和 `verified`（3）是完全可枚举的；`community` 最多 100 个，明确不支持分页。** 超过限制的社区模板永远不会进入 API 可以返回的切片，而 `runpodctl template search` 读取相同的后端切片 — 所以它也没有超出限制的视图。如果用户提到一个你找不到的模板，请要求他们提供模板 ID，而不是得出它不存在的结论。

`isRunpod` 是一个 GraphQL/v1 字段，**没有 v2 等价项** — 在 v2 中，“官方”是你请求的 `source` 切片，而不是记录上的一个标志。

目录条目包含 **`allowedCudaVersions`**，这是选择相同模板的 CUDA 版本变体的可靠方法 — 与 `runpodctl pod create --min-cuda-version` 配合使用，而不是从 GPU 名称推断。

## 模板

| 工作负载 | 参考 | 部署指南 |
| --- | --- | --- |
| **ComfyUI** — URL 上的图像生成 UI | [`reference/comfyui.md`](reference/comfyui.md) | [黄金路径 02，变体 B](../runpod/golden-paths/02-comfyui-pod/variant-b-prebuilt.md) |
| **PyTorch** — 通用 GPU 基础 / 开发箱（2.1 → 2.9，包括集群 + ROCm 构建） | [`reference/pytorch.md`](reference/pytorch.md) | [黄金路径 06](../runpod/golden-paths/06-dev-pod.md) |
| **Ubuntu** — 精简的 20.04 / 22.04 / 24.04（**CPU** 类别） | TODO | — |
| **网络存储文件浏览器**（GPU + CPU） | TODO | [黄金路径 07](../runpod/golden-paths/07-network-volume-handoff.md) |

添加模板：在此处添加一个文件，并在上方添加一行。不要为每个模板创建一个新的技能 — 任务形状是相同的，并且每个注册的技能在每个会话中都消耗上下文。

## 如何使用模板参考

`reference/` 下每个文件按相同顺序回答相同问题，因此代理可以快速浏览到它需要的内容：

1. **身份** — 模板名称、ID、镜像、上游来源仓库。
2. **变体** — CUDA/架构/GPU 代际划分以及如何选择。
3. **端口和凭证** — 暴露的内容和任何默认登录。
4. **自动启动** — 启动时已运行的内容以及确切命令。
5. **路径** — 应用程序、其配置及其数据的位置（以及网络卷挂载如何改变）。
6. **就绪** — 第一次启动需要多长时间以及“实际提供服务”的确切信号。`Running` 永远不是信号。
7. **未包含的内容** — “启动”和“可用”之间的差距，以及如何通过编程而不是点击来关闭它。
8. **尺寸** — 容器磁盘和最小 VRAM。
9. **版本锁定** — 如何锁定一个已知良好的版本。

一个文件是例外：[`reference/comfyui-model-repair.md`](reference/comfyui-model-repair.md) 是一个**使用指南** — 一个 ComfyUI 工作流程修复程序，驱动着 [`scripts/`](scripts/) 中的脚本 — 不是 9 个问题的模板参考。

## 转向其他方向 — 此技能是枢纽，不是目的地

用户询问模板时，他们很少需要参考文件本身；他们需要的是部署、修复或替换模板。先到这里，识别出哪个，然后转交：

| 用户想要… | 发送他们到… |
| --- | --- |
| **部署** 模板端到端 | 上表中匹配的黄金路径 — 经过实时验证的运行，带有真实命令 |
| **修复** 无法服务的 Pod（“Running”但 URL 死亡，404/502） | 模板的参考文件，§就绪 — 然后 [`runpod-usage/reference/gotchas.md`](../runpod-usage/reference/gotchas.md) |
| **修复** ComfyUI 工作流程中模型无法下载的问题（缺少/损坏的模型元数据，导入的工作流程或 PNG） | [修复指南](reference/comfyui-model-repair.md) — 它驱动着 [`scripts/`](scripts/) 中的修复脚本。官方 ComfyUI 模板使用 ComfyUI-RunpodDirect，因此其自动下载路径适用 |
| **向正在运行的模板 Pod 添加模型 / 文件** | 模板的参考文件（§未包含的内容），或 `companion-clis` 用于通用的 Hugging Face 转移 |
| **定制** 超出模板自带的内容（固定版本、额外节点、更轻的镜像） | [`runpod-usage/reference/building-images.md`](../runpod-usage/reference/building-images.md) — 基于官方基础构建 |
| **无服务器工作进程**，而不是 Pod | 不是 Pod 模板 — 通过 `runpodctl` / `runpod-mcp` 的 Hub 工作进程 |

这里的参考文件回答的是*镜像中包含的内容*；它们永远不会重复一个指南或修复程序 — 它们指向所有者。
