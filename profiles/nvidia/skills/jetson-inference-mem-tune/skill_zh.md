# Jetson 推理内存调优

根据 Jetson SKU/变体和用户的工作负载，推荐推理运行时以及传递给它的特定内存相关标志。不包括量化配方选择——那属于模型基准测试技能——但它确实指出了每个运行时可以高效服务的精度下限。

## 目的

将 `jetson-memory-audit` 的实时快照转换为 Jetson 上 LLM/VLM 服务的运行时和启动标志建议。当用户需要适配模型、降低 OOM 风险或切换到低内存服务堆栈时使用。

## 何时使用

- "我在 Orin Nano 8 GB 上应该使用哪个服务堆栈来运行 7B 模型？"
- "vLLM 出现 OOM——`--gpu-memory-utilization` 和 `--max-model-len` 应该是多少？"
- "相同模型，更少内存——我可以从 vLLM 切换到 llama.cpp 吗？"
- `jetson-memory-audit` 显示模型服务器是前 NvMap / PSS 消费者后。

## 前置条件

- 从目标 Jetson 获取当前的 `jetson-memory-audit/scripts/audit.sh` JSON 快照。
- 了解预期的工作负载：`llm-server`、`vlm-server`、`embedding` 或 `rag`。
- 如果用户给出期望的空闲内存目标，将其作为 `--target-mb` 传递；否则让脚本使用 SKU 默认值。

## 可用脚本

| 脚本 | 目的 | 参数 |
|------|------|------|
| `scripts/recommend.py` | 读取审计 JSON 并输出运行时加启动标志建议。 | `--audit PATH`、`--runtime`、`--workload`、`--target-mb`、`--human`。 |

如果您的代理运行时支持 `run_script`，请调用 `run_script("scripts/recommend.py", ["--audit", "/tmp/audit.json", "--runtime", "auto", "--workload", "llm-server"])` 并总结返回的 JSON。否则从仓库根目录使用 `python3` 运行它。

## 说明

1. 运行 `jetson-memory-audit/scripts/audit.sh` 以捕获设备基线。
2. 运行 `scripts/recommend.py --audit /tmp/audit.json --runtime auto --workload llm-server --target-mb 6000` 以获取运行时加标志建议的 JSON。
3. 代理呈现建议的运行时和确切的 CLI 标志。用户（或外层代理）使用这些标志启动/重启服务器。
4. 重新运行审计以验证。

## 预期工作流程

使用 `scripts/recommend.py` 处理它发出的特定提示和答案。如果直接执行被阻塞，请作为 `python3 {baseDir}/scripts/recommend.py ...` 运行它。

- 对于 vLLM OOM 提示，使用 `--runtime vllm --workload llm-server` 运行，并包含来自 `launch_flags` 的具体 `--gpu-memory-utilization=<0.x>` 和 `--max-model-len=<number>` 值。
- 对于 "最低内存" 或 Orin Nano 8 GB 提示，使用 `--runtime auto --workload llm-server` 运行；优先选择 JSON 中的运行时，并在选择 `llama-cpp` 时明确提及 GGUF / 4-bit 权衡。
- 对于 SGLang 提示，使用 `--runtime sglang` 并引用 `--mem-fraction-static`、`--max-running-requests` 和任何上下文/KV 缓存注释。
- 对于 "从 vLLM 切换到 llama.cpp" 提示，使用 `--runtime llama-cpp` 并引用 `-ngl`、`-c` 和 `--no-mmap`。

## 限制

- 建议仅与审计 JSON 的新鲜程度一样。在停止服务、更改电源模式或重启模型服务器后重新运行 `jetson-memory-audit`。
- 脚本根据 SKU 默认值和审计总计估计内存压力；模型特定的 KV 缓存、量化和分词器行为可能仍需基准测试。
- 此技能仅发出标志。它不会启动、停止或重启模型服务器。

## 错误处理

- 退出 `2`：无法读取、解析审计 JSON 或未包含有效数字内存字段。请用户重新运行 `jetson-memory-audit/scripts/audit.sh`。
- 退出 `3`：不支持的运行时或工作负载请求。使用 `scripts/recommend.py --help` 中列出的 `--runtime` 和 `--workload` 值之一重新运行。
- 空的或缺失的 `launch_flags`：不要编造备用标志。报告脚本失败并要求重新审计或支持运行的时。

## `recommend.py` 的输出契约

```json
{
  "sku": "orin-nx",
  "variant": "orin-nx-16gb",
  "mem_total_gb": 16,
  "runtime": "vllm",
  "rationale": "在此内存预算下，连续批处理 + 分页注意力的最高吞吐量。",
  "launch_flags": [
    "--gpu-memory-utilization=0.55",
    "--max-model-len=4096",
    "--max-num-seqs=8",
    "--enable-prefix-caching"
  ],
  "alternatives": [
    { "runtime": "llama-cpp", "rationale": "使用 GGUF Q4_K_M 的更低内存下限。", "launch_flags": ["-ngl 28", "-c 4096", "--no-mmap"] }
  ],
  "notes": ["如果同时运行小型 VLM，请进一步降低 --gpu-memory-utilization。"]
}
```

## 覆盖的运行时

| 运行时 | 最佳用途 | 关键内存旋钮 | 推荐安装路径 |
|------|--------|------------|------------|
| **llama.cpp** | 最紧预算；GGUF；Orin Nano 级 | `-ngl`、`-c`、`--mlock`、`--no-mmap` | `ghcr.io/nvidia-ai-iot/llama_cpp:latest-jetson-{orin,thor}` |
| **vLLM** | 高吞吐量服务，带连续批处理 | `--gpu-memory-utilization`、`--max-model-len`、`--max-num-seqs`、`--enable-prefix-caching` | Thor 和 Orin JetPack 7.2 / L4T r39+：上游 vLLM 0.20+ (`vllm/vllm-openai`) 容器或验证的本地 vLLM 0.20+。旧 Orin：NVIDIA-AI-IOT 镜像 |
| **SGLang** | 可编程工作流（RAG、工具使用、结构化输出） | `--mem-fraction-static`、`--mem-fraction-dynamic`、`--max-running-requests` | Thor：NVIDIA SGLang 26.01 (`nvcr.io/nvidia/sglang:26.01-py3`，SGLang 0.5.5.post2)。Orin：与 JetPack 匹配的环境 |
| **TensorRT Edge-LLM** | NVIDIA 调优的生产服务 | SKU 每个构建配置；分页-KV；KV 重用 | 目标 JetPack 的供应商文档 |

> 对于 Orin JetPack 7.2 / L4T r39+，支持上游 vLLM 0.20+。对于较旧的 Orin 发布版，如果可用，请优先使用 NVIDIA-AI-IOT 预构建的 vLLM 镜像，因为它们包含匹配的 CUDA/cuDNN/TensorRT 堆栈。对于 Thor，请优先使用上游 vLLM 0.20+ (`vllm/vllm-openai`) 或验证的本地 vLLM 0.20+ 安装；对于 SGLang 使用 NVIDIA SGLang 26.01 (`nvcr.io/nvidia/sglang:26.01-py3`，SGLang 0.5.5.post2) 或更新的 NVIDIA SGLang 发布说明中明确列出 Jetson Thor 支持。不要在 Thor 上强制 Orin 特定的 Jetson 容器路径，也不要假设 Orin 上本地上游 SGLang 支持。

## 量化建议

使用运行时特定的量化名称。vLLM 和 SGLang 通常消耗 Hugging Face 检查点，如 W4A16、AWQ、GPTQ、FP16 或 NVFP4。llama.cpp 和 Ollama 消耗 GGUF 模型，因此建议使用 INT4/Q4_K_M 风格的 GGUF。

| 运行时系列 | Jetson 系列 | 首选 | 备用 |
|------|--------|------|------|
| vLLM / SGLang | Thor | NVFP4 当模型/运行时支持时 | W4A16 |
| vLLM / SGLang | Orin Nano / NX | W4A16 | AWQ 或 GPTQ 4-bit |
| vLLM / SGLang | AGX Orin | W4A16 | AWQ 或 GPTQ 4-bit |
| llama.cpp / Ollama | Orin 和 Thor | GGUF INT4 / Q4_K_M | 如果内存紧张，则使用较小的 INT4 GGUF 模型 |

不要将 GGUF Q4_K_M 描述为 W4A16/AWQ/GPTQ。除非输出包含 `quant` 字段，否则不要比较 Thor NVFP4 结果与 Orin W4A16 结果。

## 运行时命令指导

使用 `recommend.py` 作为内存旋钮的权威来源，然后将它的 `launch_flags` 放入匹配的服务命令中。将命令指导保留在此技能中，而不是单独的小型参考文件，以便代理摄取一个完整的指令集。

对于 JetPack 7.2 / L4T r39+ 上的 Orin 上的 vLLM，使用上游 vLLM 0.20+ (`vllm/vllm-openai:latest`)。对于较旧的 Orin 发布版，使用 NVIDIA-AI-IOT 镜像：

```bash
docker run --rm -it --runtime nvidia --network host --name vllm \
  -v "$HOME/.cache/huggingface:/root/.cache/huggingface" \
  -e HF_TOKEN="$HF_TOKEN" \
  ghcr.io/nvidia-ai-iot/vllm:latest-jetson-orin \
  vllm serve <hf-model-id-or-local-path> \
    --host 0.0.0.0 \
    --port 8000 \
    --gpu-memory-utilization 0.60 \
    --max-model-len 4096 \
    --max-num-seqs 8 \
    --enable-prefix-caching
```

对于 Thor 上的 vLLM，使用上游 vLLM 0.20+ (`vllm/vllm-openai:latest`)，除非主机本地 vLLM 0.20+ 已安装并验证：

```bash
docker run --rm -it --runtime nvidia --network host --ipc host --name vllm \
  -v "$HOME/.cache/huggingface:/root/.cache/huggingface" \
  -e HF_TOKEN="$HF_TOKEN" \
  vllm/vllm-openai:latest \
  vllm serve <hf-model-id-or-local-path> \
    --host 0.0.0.0 \
    --port 8000 \
    --gpu-memory-utilization 0.75 \
    --max-model-len 8192 \
    --max-num-seqs 32 \
    --enable-prefix-caching
```

Thor vLLM 注意：不要从 0.20 之前的 vLLM 结果判断 Thor 支持；上游 vLLM 支持从 vLLM 0.20+ 开始。

对于 Thor 上的 SGLang，使用 NVIDIA SGLang 26.01 (`nvcr.io/nvidia/sglang:26.01-py3`)。NVIDIA SGLang 26.01 包含 SGLang `0.5.5.post2` 并明确列出 Jetson Thor 支持。避免从较旧的预发布 SGLang 结果判断 Thor 支持。避免在 Thor 上推荐 `gpt-oss` 或 FP8 路径，除非更新的 NVIDIA SGLang 发布说明说明这些已知问题已修复。

```bash
docker run --rm -it --runtime nvidia --network host --ipc host --name sglang \
  -v "$HOME/.cache/huggingface:/root/.cache/huggingface" \
  -e HF_TOKEN="$HF_TOKEN" \
  nvcr.io/nvidia/sglang:26.01-py3 \
  python3 -m sglang.launch_server \
    --model-path <hf-model-id-or-local-path> \
    --host 0.0.0.0 \
    --port 8000 \
    --mem-fraction-static 0.60 \
    --max-running-requests 8
```

对于 llama.cpp，当可用时使用 NVIDIA-AI-IOT llama.cpp 镜像，或来自与 JetPack 匹配构建的 `llama-server` 二进制文件。在 Orin 和 Thor 上从 GGUF INT4 / Q4_K_M 开始；如果审计显示内存紧张，则选择较小的 INT4 GGUF 模型。

```bash
docker run --rm -it --runtime nvidia --network host --name llama-cpp \
  -v "$PWD/models:/models:ro" \
  ghcr.io/nvidia-ai-iot/llama_cpp:latest-jetson-<orin-or-thor> \
  llama-server \
    -m /models/<model>.gguf \
    --host 0.0.0.0 \
    --port 8000 \
    -ngl 28 \
    -c 4096 \
    --no-mmap \
    --flash-attn
```

## 程序（脚本编码此内容）

1. 选择满足用户所需功能（连续批处理？结构化生成？CPU 卸载？）的最轻量级运行时。
2. 选择满足用户精度标准的最低精度（模型基准测试技能）。
3. 扫描运行时的内存旋钮（vLLM 从 `gpu-memory-utilization` 开始，llama.cpp 从 `n-gpu-layers` 和 `ctx-size` 开始）以找到维持目标吞吐量的最小占用空间。
4. 使用 `jetson-memory-audit` 重新测量。

## 安全性

只读。该技能永远不会启动、停止或重启模型服务器。它发出标志；用户（或外层编排代理）负责调用运行时。
