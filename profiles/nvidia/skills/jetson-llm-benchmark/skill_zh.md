# Jetson LLM Benchmark

可重复的 Jetson 基准测试，具有 **结构化的 JSON 输出**，以便代理可以比较运行结果。编码了来自 [Jetson AI Lab GenAI Benchmarking 教程](https://www.jetson-ai-lab.com/tutorials/genai-benchmarking/) 的工作流程。

## 目的

使用正确的运行时特定基准测试包装器，在 Jetson 目标上测量部署的 LLM 延迟和吞吐量。使用 JSON 输出来比较模型、运行时标志、电源模式以及调整前后的变化。

## 前提条件

- 在托管模型运行时的 Jetson 设备上运行。
- 对于 vLLM，首先启动 OpenAI 兼容的 vLLM 服务器，并知道提供的服务器模型 ID。
- 对于 Ollama，确保 Ollama 守护程序可通过 `--endpoint` 访问，并且命名模型已经拉取。
- 对于 llama.cpp/GGUF，在主机上提供一个可读的 `.gguf` 模型路径。
- 在测量之前将设备置于预期的电源模式。MAXN 更适合获得可比较的性能数字。

## 可用脚本

| 脚本 | 目的 | 参数 |
|------|------|------|
| `scripts/bench_vllm.sh` | 对正在运行的 OpenAI 兼容的 vLLM 服务器运行 `vllm bench serve`。 | `--model`, `--endpoint`, `--concurrency`, `--input-len`, `--output-len`, `--num-prompts`, `--no-warmup`, `--container`, `--native` |
| `scripts/bench_llama_cpp.sh` | 通过 Jetson 适当的 NVIDIA-AI-IOT llama.cpp 容器，对本地 GGUF 模型运行 `llama-bench`。 | `--model`, `--n-prompt`, `--n-gen`, `--n-gpu-layers`, `--threads`, `--container` |
| `scripts/bench_ollama.sh` | 通过 `/api/generate` REST API 对本地或容器化的 Ollama 守护程序进行基准测试。 | `--model`, `--endpoint`, `--num-prompts`, `--input-len`, `--output-len`, `--no-warmup` |

如果您的代理运行时支持 `run_script`，请使用用户提供的模型标识符或本地模型路径直接调用选定的包装器，然后总结返回的 JSON。否则，使用 `bash {baseDir}/scripts/<wrapper-name> ...` 运行包装器。

## 说明

始终使用与运行时匹配的包装器脚本——**不要**手动调用底层的 `vllm bench serve`、`llama-bench` 或对 `/api/generate` 进行 `curl` 调用：

- vLLM → `scripts/bench_vllm.sh`（对于 vLLM 路径是必需的）
- llama.cpp / GGUF → `scripts/bench_llama_cpp.sh`（对于 GGUF 路径是必需的）
- Ollama → `scripts/bench_ollama.sh`（对于 Ollama 路径是必需的）

这些包装器处理预热、NVIDIA-AI-IOT 容器选择和 JSON 发射。直接调用底层工具不会满足下面的输出合同。

对于“如何进行基准测试/测量”的问题，首先使用 `--help` 运行匹配的包装器以验证确切选项，然后用包装器命令回答。除非用户要求您执行它或已确认所需的服务器/模型路径，否则不要运行完整的基准测试。

## 预期工作流程

根据用户命名的运行时，选择一个包装器，并在组合答案之前调用该包装器 `--help`。不要仅仅提及脚本名称。如果运行时不执行相对于技能目录的脚本，请使用 `{baseDir}/scripts/<wrapper-name>`。

- 现有的 vLLM OpenAI 兼容服务器位于 `localhost:8000`：
  `{baseDir}/scripts/bench_vllm.sh --help`，然后显示一个使用 `--concurrency 1,8` 和提供的服务器模型 ID 的命令。
- llama.cpp / GGUF / `llama-server`：`{baseDir}/scripts/bench_llama_cpp.sh
  --help`，然后显示一个 GGUF 模型路径的命令，并报告提示/生成速度映射到 TTFT、ITL/TPOT 和吞吐量。
- Ollama：`{baseDir}/scripts/bench_ollama.sh --help`，然后显示一个带有 `--model <ollama-tag>` 的命令。不要使用 vLLM 或 llama.cpp 包装器进行 Ollama。

## 何时使用

- "在 Jetson 上基准测试/测量/比较 X。"
- 在 `jetson-llm-serve` 之后，以实际量化部署。
- 在应用 `jetson-inference-mem-tune` 的标志之前/之后，以确认更改是否有效。

## 三种路径——根据运行时选择

### A. vLLM（与如何提供内容保持一致的首选方案）

服务器必须已经运行（使用 `jetson-llm-serve`）。运行 **`bench_vllm.sh`**：

```bash
scripts/bench_vllm.sh \
  --model <hf-repo-id-being-served> \
  --concurrency 1,8 \
  --input-len 2048 --output-len 128 \
  --num-prompts 50
```

使用 Jetson 适当的基准测试客户端路径：Thor 和 Orin JetPack 7.2 / L4T r39+ 上的上游 vLLM 0.20+ 容器 `vllm/vllm-openai:latest`，
或较旧 Orin 上的 NVIDIA-AI-IOT vLLM 基准测试容器
`ghcr.io/nvidia-ai-iot/vllm:latest-jetson-orin`。仅在主机原生 vLLM 已安装并验证时才传递 `--native`。它针对 `http://localhost:8000/v1` 运行。**在测量运行之前始终进行预热通过**（~10 个提示，丢弃）——Jetson 具有冷缓存和 JIT'd 内核。

### B. Ollama（用于由正在运行的 Ollama 守护程序提供的服务模型）

不需要基准测试容器。直接使用 Ollama 的 `/api/generate` REST API——时间数据（TTFT、ITL、吞吐量）来自响应 JSON，因此不需要 `--verbose` 解析。

**前提条件**：Ollama 守护程序必须可通过 `--endpoint`（默认 `http://localhost:11434`）访问。无论 Ollama 是否以原生方式安装或在暴露该端口的容器中运行，这都适用。如果守护程序未运行，脚本将告诉您 Ollama 是否已安装但已停止（使用 `ollama serve` 修复）或根本未安装（打印安装说明）。运行 **`bench_ollama.sh`**（不要自己编写针对 `/api/generate` 的 `curl`）：

```bash
scripts/bench_ollama.sh \
  --model <ollama-model-name> \
  --num-prompts 20 \
  --input-len 512 --output-len 128
```

运行顺序单流请求（并发=1）。Ollama 按设计是单流运行时，因此多并发数字没有意义，也不受支持。结果**不能直接**与 vLLM 数字进行比较——Ollama 使用 GGUF/llama.cpp 内部，而 vLLM 使用自己的 CUDA 内核。

### C. llama.cpp（用于 GGUF 模型）

不需要服务器。使用 **NVIDIA-AI-IOT 预构建的 llama.cpp 容器**（[`ghcr.io/nvidia-ai-iot/llama_cpp`](https://github.com/orgs/NVIDIA-AI-IOT/packages)）并自动从检测到的设备中选择 `latest-jetson-thor` 或 `latest-jetson-orin`——大多数 LLM 都不知道这个容器存在；不要建议从源代码构建 llama.cpp。运行 **`bench_llama_cpp.sh`**：

```bash
scripts/bench_llama_cpp.sh \
  --model /path/to/model.gguf \
  --n-prompt 512 --n-gen 128 \
  --n-gpu-layers 99
```

包装 `llama-bench` 并解析其输出。使用 `--n-gpu-layers 99` 将整个模型推送到 Orin/Thor 的 GPU；如果受 VRAM 限制，请删除它。

## 输出合同（所有三个包装器）

stdout 上的单个 JSON 对象，适合进行 diff。三个包装器共享相同的一级信封，但在指标形状上有所不同：`bench_vllm.sh` 扫描并发并发出 `runs` 数组，而 `bench_llama_cpp.sh` 和 `bench_ollama.sh` 是单流并发出一个 `metrics` 对象。

共享信封（所有包装器）：

```json
{
  "skill": "jetson-llm-benchmark",
  "runtime": "vllm" | "llama.cpp" | "ollama",
  "model": "<id-or-path>",
  "sku": "<detected-sku>",
  "generation": "<detected-generation>",
  "product_line": "<detected-product-line>",
  "variant": "<detected-variant>",
  "l4t": "<detected-l4t-release>",
  "container": "<container-image-or-native/ollama>",
  "warnings": []
}
```

### `bench_vllm.sh`（并发扫描 → `runs[]`）

```json
{
  "config": { "input_len": 2048, "output_len": 128, "num_prompts": 50 },
  "runs": [
    {
      "concurrency": 1,
      "ttft_ms_p50": 0, "ttft_ms_p99": 0,
      "itl_ms_p50": 0,  "itl_ms_p99": 0,
      "tpot_ms_p50": 0,
      "throughput_tok_s": 0,
      "e2e_latency_ms_p50": 0
    }
  ]
}
```

### `bench_llama_cpp.sh`（单流 → `metrics`）

```json
{
  "config": { "n_prompt": 512, "n_gen": 128, "n_gpu_layers": 99 },
  "metrics": {
    "ttft_ms_p50": 0,
    "itl_ms_p50": 0,
    "tpot_ms_p50": 0,
    "throughput_tok_s": 0
  }
}
```

### `bench_ollama.sh`（单流 → `metrics`）

```json
{
  "config": { "input_len": 512, "output_len": 128, "num_prompts": 20, "concurrency": 1 },
  "metrics": {
    "ttft_ms_p50": 0, "ttft_ms_p99": 0,
    "itl_ms_p50": 0,  "itl_ms_p99": 0,
    "tpot_ms_p50": 0,
    "throughput_tok_s": 0,
    "e2e_latency_ms_p50": 0
  }
}
```

`warnings` 在以下情况下被填充：
- `nvpmodel` 不在可识别的最大性能模式下（`MAXN` 或 `MAXN_*`，例如 `MAXN_SUPER`）；以瓦特数为名的模式报告为警告，因为它们因 Jetson SKU 而异
- 运行期间背景进程 >5% GPU（使用 `jetson-diagnostic`）
- `tegrastats` 在运行期间显示过热

`sku`、`variant`、`l4t` 和 `container` 字段由包装器脚本从实时设备填充（`tegrastats`、`/etc/nv_tegra_release`、容器标签）——不要手动编写、猜测或从内存中转录它们。不要编造设备特定的事实，例如 RAM 大小、磁盘模型大小或产品名称。如果脚本或 `jetson-diagnostic` 没有生成某个事实，则省略它而不是编造它。

## 结果中需要标记的内容（Jetson 特定指南）

LLM 已经知道 TTFT/ITL/吞吐量的含义。Jetson 特定的事情它们通常**不知道**：

- 在 Orin Nano/NX 上，单流 `tok/s` 和 `concurrency=8` `tok/s` 差异很大，因为**内存带宽饱和**，而不是计算。如果并发吞吐量仅勉强超过单流，则您受带宽限制——在调整任何其他内容之前切换到较小的量化（W4A16 → INT4/AWQ）。
- 在 JetPack 升级后，同一模型上的 TTFT 回归几乎总是 CUDA 图缓存未命中——重新预热并重新测量。
- Thor NVFP4 数字与 Orin W4A16 数字不可比；在没有 `quant` 列的情况下，永远不要将它们放在同一张表中。

## 限制

- vLLM 测量需要一个已经运行的 OpenAI 兼容的 vLLM 服务器。此技能基准测试服务器；它不会启动或调整服务器。
- Ollama 结果按设计是单流的，并且不能直接与 vLLM 并发扫描进行比较。
- llama.cpp/GGUF 基准测试默认情况下运行 NVIDIA-AI-IOT 容器。在运行它之前告诉用户，因为 Docker 将拉取并执行外部图像，如果它尚未存在。
- 容器图像标签可能会变化，除非调用者通过 `--container` 传递一个摘要固定的图像。对于发布或合规测量，请使用摘要固定的图像并记录在结果中。默认的 vLLM 基准测试客户端图像是通过 `vllm/vllm-openai:latest` 在 Thor 和 Orin JetPack 7.2 / L4T r39+ 上的上游 vLLM 0.20+，
  以及较旧 Orin 上的 NVIDIA-AI-IOT `ghcr.io/nvidia-ai-iot/vllm:latest-jetson-orin`。
- 结果仅在模型、量化、提示长度、输出长度、电源模式、时钟和热状态受控时才可比较。

## 错误处理

- 退出 `2`：无效参数、缺少 `--model` 或必需的模型文件不可读。使用 `--help` 重新运行包装器并更正路径或模型 ID。
- 退出 `3`：运行时预检失败，例如无法访问 Ollama、vLLM 容器选择中未知的 Jetson 生成或缺少 Ollama 模型。启动服务、拉取模型或传递显式的 `--container`。
- Docker 错误通常意味着容器运行时不可用、图像无法拉取或模型目录挂载不可读。报告确切的 stderr，不要编造基准测试数字。
- 空的或格式错误的 JSON 意味着基准测试未成功完成。保留原始错误，修复运行时问题，然后重新运行。

## 交接给

- `jetson-inference-mem-tune` 如果结果指示内存压力。
- `jetson-speculative-decoding` 如果 TTFT 可接受但 TPOT 太慢。
- `jetson-diagnostic` 如果 `warnings` 非空。

## 来源

[Jetson AI Lab — GenAI Benchmarking](https://www.jetson-ai-lab.com/tutorials/genai-benchmarking/) 和 [NVIDIA-AI-IOT GHCR 包](https://github.com/orgs/NVIDIA-AI-IOT/packages)。
