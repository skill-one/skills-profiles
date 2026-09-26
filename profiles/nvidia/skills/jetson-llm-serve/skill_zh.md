# Jetson LLM Serve

编码了 [Jetson AI Lab GenAI 教程](https://www.jetson-ai-lab.com/tutorials/genai-on-jetson-llms-vlms/)：在 Orin JetPack 7.2 / L4T r39+ 上使用上游 vLLM 0.20+ (`vllm/vllm-openai:latest`)；在较旧的 Orin 上选择 NVIDIA-AI-IOT 预构建的 vLLM 容器；在 Thor 上使用上游 vLLM 0.20+ 或经过验证的原生 vLLM 0.20+，并在请求 SGLang 时使用 NVIDIA SGLang 26.01 (`nvcr.io/nvidia/sglang:26.01-py3`, SGLang 0.5.5.post2)。设置 MAXN，使 Hugging Face 凭据/缓存可用，并启动一个兼容 OpenAI 的服务器。适用于 LLM 和 VLM。

## 目的

提供一个适用于 Jetson 的 LLM 或 VLM 服务配方，使用 vLLM 或 SGLang，包括运行时路径、启动命令、端点和验证步骤。

## 何时使用

- "在 Jetson 上运行/服务/托管此模型。"
- "启动一个可以从 Open WebUI / 我的应用中访问的 vLLM 服务器。"
- 在 `jetson-inference-mem-tune` 生成启动标志后，用户实际想要启动服务器时。

对于仅涉及配方的提问，从本文档中回答，而不要启动容器。仅在用户要求检查此设备或执行部署时才运行实时预检。

## 前置条件

- 在 Jetson 主机或具有对 Jetson GPU 运行的 Docker 访问权限的 Shell 上运行。
- 了解目标 Jetson 世代 (`thor` 或 `orin`) 和模型标识符或本地检查点路径。
- 仅当模型受保护/私有时才使用 `HF_TOKEN`；公共模型应省略令牌环境变量。
- 在不确定内存余量或启动标志时，首先使用 `jetson-inference-mem-tune`。

## 说明

对于配方问题，提供完整的启动配方，而不是尝试将 `jetson-llm-serve` 作为工具调用。完整的答案包括：

- 适用于 Jetson 的运行时路径：Thor 上的上游 vLLM 0.20+ (`vllm/vllm-openai:latest`) 或 NVIDIA SGLang 26.01 (`nvcr.io/nvidia/sglang:26.01-py3`, SGLang 0.5.5.post2)，Orin JetPack 7.2 / L4T r39+ 上的上游 vLLM 0.20+，较旧的 Orin 上的 NVIDIA-AI-IOT vLLM 容器。
- 用户命名的模型检查点 / Hugging Face 仓库。
- 带有 `--host 0.0.0.0 --port 8000` 的 `docker run` + 服务器命令草图。
- 兼容 OpenAI 的端点：`http://<jetson-ip>:8000/v1`。
- 验证步骤，例如 `curl http://localhost:8000/v1/models`。

对于 VLM 问题，明确说明 VLM 使用与 LLM 相同的 vLLM 服务流程，但使用不同的视觉语言检查点。在回答 VLM 提问时，不要省略 `vLLM` 或 Jetson 容器。

## 第 1 步 — 选择运行时路径（按 Jetson 系列）

在 Thor 上使用 vLLM，使用上游 vLLM 0.20+ (`vllm/vllm-openai:latest`) 或经过验证的原生 vLLM 0.20+ 安装。在 Orin JetPack 7.2 / L4T r39+ 上使用上游 vLLM 0.20+ (`vllm/vllm-openai:latest`)。在较旧的 Orin 发布版上使用 **NVIDIA-AI-IOT 预构建的 vLLM 镜像** ([软件包](https://github.com/orgs/NVIDIA-AI-IOT/packages))，因为它包含适用于该 JetPack 的正确 CUDA / cuDNN / TensorRT 堆栈。在 Thor 上，当用户请求 SGLang、RAG、工具使用或可编程服务时，使用 NVIDIA SGLang 26.01 (`nvcr.io/nvidia/sglang:26.01-py3`, SGLang 0.5.5.post2)；除非 JetPack 匹配的发布版明确支持，否则不建议在 Orin 上推荐原生上游 SGLang。

| Jetson 系列               | 运行时路径                                      |
|-----------------------------|---------------------------------------------------|
| Thor (T5000, T4000)         | 上游 vLLM 0.20+ (`vllm/vllm-openai:latest`) 或 NVIDIA SGLang 26.01 (`nvcr.io/nvidia/sglang:26.01-py3`, SGLang 0.5.5.post2) |
| AGX Orin / Orin NX / Nano   | Orin JetPack 7.2 / L4T r39+: 上游 vLLM 0.20+ (`vllm/vllm-openai:latest`)；较旧的 Orin: `ghcr.io/nvidia-ai-iot/vllm:latest-jetson-orin` |

要检测硅时代以用于镜像标签：

1. 源检测器，以便在您的 Shell 中保留导出：
   ```bash
   . skills/jetson-diagnostic/scripts/detect_jetson.sh
   ```
2. 检查 `JETSON_GENERATION` (`thor` 或 `orin`) 并从上表中选择匹配的运行时路径。
3. 使用 `JETSON_PRODUCT_LINE` 进行更细粒度的分类，例如 `thor-agx` 或 `orin-nano`；`JETSON_SKU` 保持为传统标识符。

当您需要在调用者中导出变量时，不要使用 `bash skills/jetson-diagnostic/scripts/detect_jetson.sh`；使用 `bash` 运行会在子 Shell 中使用。

## 第 2 步 — 设置 MAXN 功率模式

```bash
sudo nvpmodel -m 0 && sudo jetson_clocks
```

仅当用户明确要求功率受限运行时才跳过此步骤；否则，基准测试和服务数量将不一致。

## 第 3 步 — 运行服务器

在 Thor 上使用 vLLM，使用上游 vLLM 0.20+ (`vllm/vllm-openai:latest`) 或经过验证的原生 vLLM 0.20+ 安装：

```bash
docker run --rm -it --runtime nvidia --network host --ipc host --name vllm \
  -v "$HOME/.cache/huggingface:/root/.cache/huggingface" \
  -e HF_TOKEN="$HF_TOKEN" \
  vllm/vllm-openai:latest \
  vllm serve <hf-repo-id> \
    --host 0.0.0.0 --port 8000 \
    --max-model-len 8192 \
    --gpu-memory-utilization 0.75 \
    --tensor-parallel-size 1
```

在 Orin JetPack 7.2 / L4T r39+ 上使用上游 vLLM 0.20+ (`vllm/vllm-openai:latest`)。在较旧的 Orin 发布版上使用 NVIDIA-AI-IOT 容器：

```bash
docker run --rm -it --runtime nvidia --network host --name vllm \
  -v "$HOME/.cache/huggingface:/root/.cache/huggingface" \
  -e HF_TOKEN="$HF_TOKEN" \
  ghcr.io/nvidia-ai-iot/vllm:latest-jetson-orin \
  vllm serve <hf-repo-id> \
    --host 0.0.0.0 --port 8000 \
    --max-model-len 4096 \
    --gpu-memory-utilization 0.85 \
    --tensor-parallel-size 1
```

`HF_TOKEN` 仅当 Hugging Face 模型受保护/私有时才需要；对于不需要 Hub 身份验证的公共模型，请省略 `-e HF_TOKEN="$HF_TOKEN"` 行。将 `HF_TOKEN` 作为环境变量传递可能会通过 Docker 检视输出、进程元数据或共享系统上的日志暴露它。优先使用作用域最窄的令牌，在共享容器使用后旋转/撤销它，并在部署环境支持该模式时使用挂载的凭证文件或 Docker 密钥。

等待 `Application startup complete.` 服务器位于 `http://0.0.0.0:8000/v1`。

对于 Thor 上的 SGLang，使用 NVIDIA SGLang 26.01 (`nvcr.io/nvidia/sglang:26.01-py3`)，它打包了 SGLang 0.5.5.post2 并列出了 Jetson Thor 支持。不要根据较旧的预发布 SGLang 结果判断 Thor SGLang 支持：

```bash
docker run --rm -it --runtime nvidia --network host --ipc host --name sglang \
  -v "$HOME/.cache/huggingface:/root/.cache/huggingface" \
  -e HF_TOKEN="$HF_TOKEN" \
  nvcr.io/nvidia/sglang:26.01-py3 \
  python3 -m sglang.launch_server \
    --model-path <hf-repo-id> \
    --host 0.0.0.0 \
    --port 8000 \
    --mem-fraction-static 0.60 \
    --max-running-requests 8
```

当用户需要 RAG/工具使用工作流、结构化生成或 SGLang 特定调度时，使用 SGLang。对于普通的 高吞吐量 OpenAI 兼容服务，除非用户要求 SGLang，否则优先使用 vLLM。

### SKU 适当的默认值

| 旋钮                       | Orin Nano / NX | AGX Orin / Thor |
|----------------------------|----------------|-----------------|
| `--max-model-len`          | `4096`         | `8192`          |
| `--gpu-memory-utilization` | `0.85`         | `0.85`          |
| `--tensor-parallel-size`   | `1`            | `1`             |

如果服务器在启动时 OOM，将 `--gpu-memory-utilization` 降低 0.05 并重新启动（或运行 `jetson-inference-mem-tune` 以获取工作负载感知建议）。

## 量化偏好（比运行时更重要）

对于 vLLM 和 SGLang，根据 Jetson 系列选择检查点格式：

| Jetson 系列 | 首选 | 可接受的回退 |
|---------------|--------------|---------------------|
| Thor | **NVFP4** 当模型/运行时支持时 | W4A16 |
| Orin Nano / NX | **W4A16** | AWQ 或 GPTQ 4-bit |
| AGX Orin | **W4A16** | AWQ 或 GPTQ 4-bit |

对于 llama.cpp 和 `Ollama`，使用 GGUF 模型量化名称：在 Orin 和 Thor 上都推荐 **INT4 / Q4_K_M GGUF**，如果内存紧张，则选择较小的 INT4 GGUF 模型。不要将 GGUF Q4_K_M 称为 W4A16/AWQ/GPTQ 模型。NVFP4 是 Thor 首选，并针对支持它的运行时进行了优化。

## VLM 模式

VLMs 使用与 LLM 相同的流程：相同的容器、相同的 `vllm serve` 调用，但使用不同的视觉语言检查点。容器处理图像预处理。对于特定的 VLM 浏览器 UI，使用 [`live-vlm-webui`](https://github.com/orgs/NVIDIA-AI-IOT/packages) 容器；对于任何的通用聊天 UI，使用指向 `http://<jetson-ip>:8000/v1` 的 Open WebUI。

## 不要编造设备容量

在提供服务配方时，不要编造 RAM 总量、空闲内存值、模型大小、JetPack 版本或 SKU/变体名称。如果容量很重要，要么运行实时预检（当允许执行时），要么将任务交给 `jetson-inference-mem-tune` / `jetson-memory-audit`。如果实时数据不可用，请说明值未知，并提供保守默认值，而不是引用一个编造的数字。

## 预检清单（代理应在运行第 3 步之前验证）

- [ ] 在 Jetson 上 (`/proc/device-tree/model` 包含 `NVIDIA Jetson`)。
- [ ] `nvpmodel -q` 报告了识别的最大性能模式：`MAXN` 或 `MAXN_*`，例如 `MAXN_SUPER`。除非用户明确确认它们是此设备的预期基准模式，否则应将功耗命名的模式报告为警告。
- [ ] 在 Thor 上，在启动之前检查 MIG 是否启用 (`nvidia-smi -L` 和 `nvidia-smi mig -lgi`)。如果启用了 MIG，则警告 vLLM/SGLang 可能只看到 MIG 切片或没有 CUDA 设备。
- [ ] 在 Thor 上使用 MIG 或显示/摄像头争用，使用 `sudo lsof /dev/nvidia*` 检查 GPU 用户。显示管理器、`Xorg`/GNOME 或 `nvargus-daemon` 可能会保留 GPU 设备文件；除非用户明确批准，否则不要停止服务或更改 MIG 模式。
- [ ] 没有名为 `vllm` 的容器已经在运行 (`docker ps --format '{{.Names}}'`)；否则首先执行 `docker rm -f vllm`。
- [ ] Docker 暴露了 NVIDIA 运行时 (`docker info | grep -i 'runtimes.*nvidia'`)，或者启用了 GPU 的容器可以运行 `nvidia-smi`。
- [ ] `~/.cache/huggingface` 存在；如果模型受保护，则 `HF_TOKEN` 已设置。

## 限制

- 此技能提供服务命令和预检检查；它不会基准测试已部署的服务器。
- 容器标签（如 `latest`）是可变的。对于发布或合规部署，请固定摘要并记录在部署说明中。
- vLLM 和 SGLang 内存限制仍然取决于模型架构、量化、上下文长度和并发请求计数。当命令 OOM 或内存余量很重要时，使用 `jetson-inference-mem-tune`。
- Thor vLLM 需要上游 vLLM 0.20+ 或更新版本。较旧的上游 vLLM 镜像可能无法正确支持 Thor / SM 11.0。
- Thor SGLang 应使用 NVIDIA SGLang 26.01 或更新版本发布说明，明确列出 Jetson Thor 支持。NVIDIA SGLang 26.01 包含 SGLang 0.5.5.post2。
- 在 Thor 上，MIG、桌面显示或摄像头服务可以隐藏完整 GPU，供容器使用。此技能应检测并警告；禁用 MIG 或停止服务（如 `gdm3` 或 `nvargus-daemon`）需要明确用户批准。
- 在 Thor 上，仅在目标 JetPack 上已验证的原生 vLLM/SGLang 安装时才应使用。

## 交接给

- `jetson-llm-benchmark` 以实际测量已部署的服务器。
- `jetson-speculative-decoding` 以通过在上述 `vllm serve` 命令中附加 `--speculative-config '{...}'` 添加 EAGLE-3 / 草稿模型推测。
- `jetson-inference-mem-tune` 如果服务器 OOM 或受内存限制。

## 来源

[Jetson AI Lab — Jetson 上的 GenAI 简介：如何运行 LLMs 和 VLMs](https://www.jetson-ai-lab.com/tutorials/genai-on-jetson-llms-vlms/) 和 [NVIDIA-AI-IOT GHCR 软件包](https://github.com/orgs/NVIDIA-AI-IOT/packages)。
