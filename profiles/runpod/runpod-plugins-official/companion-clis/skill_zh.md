# 伴随 CLIs

Runpod 通常需要四个 CLIs。每个 CLi 都有它自己的 **凭证 + 命令参考** 在 [`reference/`](reference/) 中 — 加上一个一次性的 `<cli>-setup.md` 用于安装（如果 CLi 未安装则不会打开）。只加载任务需要的那个，而不是全部四个。

如果请求以导入的 ComfyUI 工作流开始，且模型文件名缺少经过验证的 URL 或哈希，则路由到 runpod-templates 中的 [ComfyUI 模型修复指南](../runpod-templates/reference/comfyui-model-repair.md)。当已知道确切的 Hugging Face 仓库/文件，且任务仅仅是下载、缓存或烘焙该工件时，再返回这里。

| CLi | 用于 | 完整参考 |
|-----|-----------|----------------|
| `hf` (HuggingFace) | 从 Hub 下载模型以缓存/烘焙到镜像 | [reference/huggingface.md](reference/huggingface.md) |
| `gh` (GitHub) | 管理工作器仓库 + 切发布 (Hub 索引发布) | [reference/github.md](reference/github.md) |
| `docker` | 构建/验证/推送镜像到 Docker Hub 以供 Runpod 拉取 | [reference/docker.md](reference/docker.md) |
| `aws` (S3) | 通过 Runpod 的 S3 API 读写网络卷存储 | [reference/aws.md](reference/aws.md) |

每个在使用前都需要凭证。阅读每个工具的参考以获取认证步骤和命令；安装是一个单独的一次性 `<cli>-setup.md`。

这些 CLi 通常是大作业中的一步。整个作业的验证示例在 [runpod/golden-paths/README.md](../runpod/golden-paths/README.md) 中 — 烘焙与挂载模型 ([25](../runpod/golden-paths/25-bake-vs-mount/README.md))、构建最小镜像 ([22](../runpod/golden-paths/22-minimal-pod-image/README.md)) 或将数据移动到网络卷 ([07](../runpod/golden-paths/07-network-volume-handoff.md))。

这些是各自发布轨道上的第三方 CLi，所以 **`<cli> --help` 对标志和子命令具有权威性** — 这里的参考涵盖了 Runpod 特定的用法和陷阱，而不是工具的完整表面。在报告其中之一无法执行某操作之前，请先检查 `--help`。

## Windows: 首先安装 WSL2

如果你在 Windows 上，请先安装 WSL2 再继续 — 它提供了这些 CLi 目标的原生 Linux 环境。以管理员身份在 PowerShell 中运行，然后重启：

```powershell
wsl --install
```

之后打开 Ubuntu 应用以完成设置，然后遵循每个参考中的 **Linux** 说明。

## HuggingFace CLi

本地下载模型以便缓存，用于 Docker 构建/运行。认证和 `hf download` 配方：**[reference/huggingface.md](reference/huggingface.md)** (安装：[reference/huggingface-setup.md](reference/huggingface-setup.md))。

- 使用独立的 `hf` CLi，**不要** `pip install huggingface_hub`（那是语法不同的旧版 `huggingface-cli`）。
- 通过 `hf auth login` 进行认证，或 `export HF_TOKEN=hf_...`（环境变量优先于保存的令牌）。

## GitHub CLi

管理工作器仓库并切发布。认证和命令：**[reference/github.md](reference/github.md)** (安装 + SSH-key 设置：[reference/github-setup.md](reference/github-setup.md))。

- **Hub 索引的是发布，而不是提交** — 每次 Hub 列表更新都需要一个新的 `gh release create`。
- 一个 SSH key (`ssh-keygen -t ed25519`) 注册到 GitHub (`gh ssh-key add`) 和 HuggingFace（在浏览器中粘贴）。

## Docker

构建、验证并推送镜像到 Docker Hub。凭证和命令：**[reference/docker.md](reference/docker.md)** (安装：[reference/docker-setup.md](reference/docker-setup.md))。

- **始终使用 `--platform=linux/amd64` 构建** — Runpod 在 x86 Linux 上运行。
- **始终使用明确的语义标签；永远不要 `latest`** — `latest` 不跟踪最新的推送，所以工作器可能会静默地拉取错误的镜像。
- Docker Hub 认证使用 **个人访问令牌**，而不是你的密码。对于私有镜像，请在 Console → Container Registry Settings 中注册凭证一次。

## AWS CLI

通过 Runpod 的 S3 兼容 API 访问网络卷存储（桶名 = 网络卷 ID）。凭证、区域规则和命令：**[reference/aws.md](reference/aws.md)** (安装：[reference/aws-setup.md](reference/aws-setup.md))。

- Runpod 的 S3 API，**不是 AWS**：访问密钥 = Runpod **用户 ID** (`user_...`)，密钥 = S3 API 密钥 (`rps_...`)。
- **S3 API 密钥仅在控制台中创建。** 没有 `runpodctl`/REST/GraphQL 创建它们 — 如果它们不在 `~/.aws/credentials`/env 中且需要 S3 访问，**停止并要求用户** 生成它们（Settings > S3 API Keys）。
- 每个命令都需要 `--region DATACENTER --endpoint-url https://s3api-DATACENTER.runpod.io/` (数据中心 = 卷的 DC，不是 AWS 区域)。
- 对于大文件/多文件传输，需要可靠的恢复，请参阅 [reference/aws.md → 可选可恢复卷传输](reference/aws.md#optional-resumable-volume-transfers-community-tool)。
