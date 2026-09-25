# Nemotron Speech 功能

> **注意：** "Nemotron Speech" 是 NVIDIA 当前文档中称为 **Riva** / **Riva NIM** 的面向公众的名称。所有命令、容器镜像、gRPC API、Python 导入和文档 URL 仍然使用 **"Riva"** — 重命名仅限于品牌。不要重命名命令、镜像或文档 URL。
>
> **代理：** 当引导用户进行多步骤工作流程时，在展示每个步骤之前宣布每个步骤：**步骤 N/M — 步骤标题**（例如，**"步骤 1/4 — 部署容器"**）。

## 目的

NVIDIA Nemotron Speech (Riva) NIM 工作流程的单一入口点：语音识别 (ASR)、语音合成 (TTS) 和神经机器翻译 (NMT)。涵盖通过 build.nvidia.com 托管的云端推理、自托管 Docker 部署、ASR 客户端协议选择（gRPC、HTTP、WebSocket）、通过 `riva-build` 部署自定义 NeMo 模型、ASR 管道调整（语音活动检测 VAD、说话人分割、语言模型），以及先决条件 Docker / NGC / 驱动程序设置。

## 何时使用此功能

对于任何 Nemotron Speech / Riva NIM 任务 — 部署、测试、自定义模型构建、系统要求检查或跨 ASR / TTS / NMT 语音模式选择模型 — 都使用此功能。

## 工作流程

识别用户的任务类型，然后从 `references/` 加载相应的参考文件。参考文件包含每个工作流程的详细内容；此 SKILL.md 是一个路由表面。仅加载与当前任务相关的参考文件。

## 先决条件

- 对于 **自托管部署**：NVIDIA AI Enterprise (NVAIE) 授权，然后完成环境设置 — NVIDIA 驱动程序、Docker、容器工具包、NGC API 密钥、Riva Python 客户端。参见 [`references/setup.md`](references/setup.md)。
- 对于 **云端推理**：`pip install -U nvidia-riva-client` 并从 https://build.nvidia.com 获取有效的 `NVIDIA_API_KEY`。
- 将 `NVIDIA_API_KEY` 和 `NGC_API_KEY` 视为密钥：永远不要打印、粘贴、提交或记录实际的密钥值。优先使用 `--password-stdin` 进行 Docker 登录，并将持久密钥存储在凭证管理器或 `chmod 600` 环境文件中，而不是世界可读的 shell 启动文件。
- 对于 **自托管 Docker 模型缓存**：挂载在 `/opt/nim/.cache` 的主机目录必须对容器用户可写（NIM 容器内部以 `nvs:1000` 运行），而不仅仅是主机用户。在创建目录后运行 `sudo chown 1000:1000 $LOCAL_NIM_CACHE`，以便容器可以写入它。避免世界可写模式 — 它们允许任何本地用户替换缓存的模型工件。还避免在 docker run 中使用 `-u "$(id -u):$(id -g)"` — 容器内部的 `/opt/nim/workspace` 不可写给任意 UID。如果在模型下载期间看到 `I/O error Permission denied (os error 13)`，则主机目录所有权是问题。

## 说明

- 将用户的任务匹配到一个参考文件，并仅加载该文件；参考文件很详细，因此渐进式披露可以保持上下文紧密。
- 将驱动程序、Docker、容器工具包和 NGC 的设置请求路由到 [`references/setup.md`](references/setup.md)。
- 将 GPU 兼容性、部署就绪和容器健康检查路由到 [`references/deployment-readiness-checks.md`](references/deployment-readiness-checks.md)。
- 将跨 ASR、TTS 和 NMT 的模型选择路由到 [`references/model-selection.md`](references/model-selection.md)。
- 将 Parakeet、Canary、Whisper 和 Nemotron ASR 流式传输的 ASR 部署或推理路由到 [`references/asr.md`](references/asr.md)。
- 将自定义训练的 NeMo ASR 部署（`.nemo` → RMIR → NIM）路由到 [`references/asr-custom.md`](references/asr-custom.md)。
- 将 VAD、说话人分割、语言模型和块大小的 ASR 管道配置路由到 [`references/pipelines.md`](references/pipelines.md)。
- 将 Magpie 的 TTS 部署或推理路由到 [`references/tts.md`](references/tts.md)。
- 将自定义或微调的 TTS 模型部署（`.nemo` → RMIR → NIM）路由到 [`references/tts-custom.md`](references/tts-custom.md)。
- 将 TTS 合成管道配置 — SSML、零样本语音克隆、应用现有的发音词典、音频编码、采样率、`custom_configuration` 键 — 路由到 [`references/tts-pipelines.md`](references/tts-pipelines.md)。*(对于发现和构建发音本身，使用 `tts-pronunciation.md`。)*
- 将 TTS 发音发现 — 查找、测试和应用特定单词或短语的 IPA 发音 — 路由到 [`references/tts-pronunciation.md`](references/tts-pronunciation.md)。
- 将 Riva Translate、语言对和 DNT 标签的 NMT 部署或推理路由到 [`references/nmt.md`](references/nmt.md)。

## 真实来源

对于每个版本的详细信息 — 当前模型目录、容器 ID、函数 ID、语音列表、VRAM 最小值、每个模型的功能支持 — **获取或打开标准的 NVIDIA 文档**，而不是依赖此 SKILL.md 或参考文件中的文本。每个参考文件都包含其自己的路由表到相关的文档页面。

顶级着陆页：

| 主题 | URL |
|---|---|
| ASR 支持矩阵 | https://docs.nvidia.com/nim/speech/latest/reference/support-matrix/asr.html |
| TTS 支持矩阵 | https://docs.nvidia.com/nim/speech/latest/reference/support-matrix/tts.html |
| NMT 支持矩阵 | https://docs.nvidia.com/nim/speech/latest/reference/support-matrix/nmt.html |
| 先决条件（驱动程序 / GPU / 操作系统） | https://docs.nvidia.com/nim/speech/latest/get-started/prerequisites.html |
| ASR 管道配置 | https://docs.nvidia.com/nim/speech/latest/asr/customization/pipeline-configuration.html |
| ASR 运行时自定义 | https://docs.nvidia.com/nim/speech/latest/asr/customization/customization.html |
| TTS 自定义部署（`.nemo` / `.riva`，`riva-build`，RMIR） | https://docs.nvidia.com/nim/speech/latest/tts/custom-deployment.html |
| TTS 请求时自定义（SSML、发音词典、`custom_configuration`） | https://docs.nvidia.com/nim/speech/latest/tts/customization.html |
| TTS 语音和情感风格 | https://docs.nvidia.com/nim/speech/latest/tts/voices.html |
| TTS 零样本语音克隆 | https://docs.nvidia.com/nim/speech/latest/tts/voice-cloning.html |
| TTS IPA 音素集 | https://docs.nvidia.com/nim/speech/latest/tts/phoneme-support.html |
| 云端函数 ID（每个模型） | `https://build.nvidia.com/<org>/<model>/api` |
| NGC 模型目录 | https://catalog.ngc.nvidia.com/models |

## 示例

**"部署 Parakeet ASR NIM"** → 加载 [`references/asr.md`](references/asr.md)，遵循选项 B（自托管），步骤 1–4。

**"使用 Magpie 合成语音"** → 加载 [`references/tts.md`](references/tts.md)，遵循选项 A（云端）或选项 B（自托管）。

**"将英语翻译成德语"** → 加载 [`references/nmt.md`](references/nmt.md)，遵循 4 步流程。

**"将我的微调 `.nemo` 转换为 NIM"** → 加载 [`references/asr-custom.md`](references/asr-custom.md) 用于 4 阶段管道，并加载 [`references/pipelines.md`](references/pipelines.md) 用于构建时配置。

**"部署自定义微调的 TTS 语音作为 NIM"** → 加载 [`references/tts-custom.md`](references/tts-custom.md) 用于 4 阶段管道。

**"使用 Magpie 进行零样本语音克隆"** → 加载 [`references/tts-pipelines.md`](references/tts-pipelines.md)。

**"在我的 TTS 请求中添加 SSML 强调标签"** → 加载 [`references/tts-pipelines.md`](references/tts-pipelines.md)。

**"'NVIDIA' 在我的 Magpie TTS 输出中听起来不正确 — 建议几个 IPA 选项进行测试"** → 加载 [`references/tts-pronunciation.md`](references/tts-pronunciation.md)，生成 IPA 候选者，合成变体，然后输出所有三种交付格式。

**"我如何修复 Riva TTS 中 'NIM' 的发音，使用 gRPC Python 中的自定义字典？"** → 加载 [`references/tts-pronunciation.md`](references/tts-pronunciation.md)，为 'NIM' 提出 IPA，显示线格式和 gRPC 演示。

**"我的 GPU 能运行这个吗？"** → 加载 [`references/deployment-readiness-checks.md`](references/deployment-readiness-checks.md) 并运行 6 步系统检查。

**"我应该使用哪个 Riva 模型？"** → 加载 [`references/model-selection.md`](references/model-selection.md)，应用决策框架，然后获取特定当前模型名称的支持矩阵。

## 命名和术语

- **功能品牌**：Nemotron Speech（面向公众的名称）。
- **保留内部命名**：命令（`riva-build`，`riva-deploy`，`riva_streaming_asr_client`），Python 客户端（`riva.client`），gRPC 命名空间（`nvidia.riva.asr.*`），容器注册表（`nvcr.io/nim/nvidia/*`），以及所有 NVIDIA 文档 URL 仍然使用 **"Riva"**。不要在代码、命令或文档中重命名这些。

## 故障排除

对于特定任务的运行时或语音模式问题，使用相关的参考文件（`references/<任务>.md`）。跨切问题检查：

- **容器未就绪** → [`references/deployment-readiness-checks.md`](references/deployment-readiness-checks.md)（系统检查 + 健康检查表）
- **健康检查失败** → [`references/deployment-readiness-checks.md`](references/deployment-readiness-checks.md)
- **从 `nvcr.io` 拉取 `docker pull` 返回 403** → [`references/setup.md`](references/setup.md)（步骤 5 — Docker 登录）
- **错误的基镜像 / 模型架构不匹配** → [`references/asr-custom.md`](references/asr-custom.md)（阶段 2 基镜像）
- **VRAM / GPU 兼容性** → [`references/deployment-readiness-checks.md`](references/deployment-readiness-checks.md)，然后在支持矩阵中验证

## 限制

- 仅限 x86_64 架构 — Windows 上的 WSL2 需要 Podman 并支持 NIM 的子集（参见 [`references/setup.md`](references/setup.md))
- 自托管部署需要 NVIDIA AI Enterprise 许可证
- 云端推理需要有效的 `NVIDIA_API_KEY` 和互联网访问
- 公共功能品牌是 **"Nemotron Speech"**；命令、容器镜像、Python 导入（`riva.client`）、gRPC 服务（`nvidia.riva.*`）和 NVIDIA 文档 URL 仍然使用 **"Riva"** — 遵循官方文档和目录进行命名，不要在命令或代码中重命名这些

## 下一步

- 验证硬件兼容性：[`references/deployment-readiness-checks.md`](references/deployment-readiness-checks.md)
- 设置环境：[`references/setup.md`](references/setup.md)
- 选择模型：[`references/model-selection.md`](references/model-selection.md)
- 部署：[`references/asr.md`](references/asr.md)，[`references/tts.md`](references/tts.md)，或 [`references/nmt.md`](references/nmt.md)
