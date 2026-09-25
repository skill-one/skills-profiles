# Hugging Face 本地模型

在 Hugging Face Hub 中搜索与 llama.cpp 兼容的 GGUF 仓库，选择合适的量化等级，并使用 `llama-cli` 或 `llama-server` 启动模型。

## 默认工作流程

1. 使用 `apps=llama.cpp` 在 Hub 中搜索。
2. 打开 `https://huggingface.co/<repo>?local-app=llama.cpp`。
3. 当可见时，优先选择 HF local-app 片段和量化推荐。
4. 使用 `https://huggingface.co/api/models/<repo>/tree/main?recursive=true` 确认确切的 `.gguf` 文件名。
5. 使用 `llama-cli -hf <repo>:<QUANT>` 或 `llama-server -hf <repo>:<QUANT>` 启动。
6. 当仓库使用自定义文件命名时，回退到 `--hf-repo` 加 `--hf-file`。
7. 仅当仓库未提供 GGUF 文件时，从 Transformers 权重进行转换。

## 快速入门

### 安装 llama.cpp

```bash
brew install llama.cpp
winget install llama.cpp
```

```bash
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
make
```

### 认证受限制的仓库

```bash
hf auth login
```

### 搜索 Hub

```text
https://huggingface.co/models?apps=llama.cpp&sort=trending
https://huggingface.co/models?search=Qwen3.6&apps=llama.cpp&sort=trending
https://huggingface.co/models?search=<term>&apps=llama.cpp&num_parameters=min:0,max:24B&sort=trending
```

### 直接从 Hub 运行

```bash
llama-cli -hf unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_M
llama-server -hf unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_M
```

### 运行确切的 GGUF 文件

```bash
llama-server \
    --hf-repo unsloth/Qwen3.6-35B-A3B-GGUF \
    --hf-file Qwen3.6-35B-A3B-UD-Q4_K_M.gguf \
    -c 4096
```

### 仅在无 GGUF 文件时转换

```bash
hf download <repo-without-gguf> --local-dir ./model-src
python convert_hf_to_gguf.py ./model-src \
    --outfile model-f16.gguf \
    --outtype f16
llama-quantize model-f16.gguf model-q4_k_m.gguf Q4_K_M
```

### 本地服务器冒烟测试

```bash
llama-server -hf unsloth/Qwen3.6-35B-A3B-GGUF:UD-Q4_K_M
```

```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer no-key" \
  -d '{
    "messages": [
      {"role": "user", "content": "Write a limerick about exception handling"}
    ]
  }'
```

## 量化选择

- 优先选择 HF 在 `?local-app=llama.cpp` 页面上标记为兼容的确切量化等级。
- 保留仓库原生标签，如 `UD-Q4_K_M`，而不是进行规范化。
- 默认为 `Q4_K_M`，除非仓库页面或硬件配置建议其他。
- 当内存允许时，优先选择 `Q5_K_M` 或 `Q6_K` 用于代码或技术工作负载。
- 考虑 `Q3_K_M`、`Q4_K_S` 或仓库特定的 `IQ` / `UD-*` 变体以节省更紧的 RAM 或 VRAM。
- 将 `mmproj-*.gguf` 文件视为投影权重，而不是主检查点。

## 加载参考

- 阅读 [hub-discovery.md](references/hub-discovery.md) 了解 URL 优先工作流程、模型搜索、树 API 提取和命令重建。
- 阅读 [quantization.md](references/quantization.md) 了解格式表、模型缩放、质量权衡和 `imatrix`。
- 阅读 [hardware.md](references/hardware.md) 了解 Metal、CUDA、ROCm 或 CPU 构建 和 加速细节。

## 资源

- llama.cpp: `https://github.com/ggml-org/llama.cpp`
- Hugging Face GGUF + llama.cpp 文档: `https://huggingface.co/docs/hub/gguf-llamacpp`
- Hugging Face 本地应用文档: `https://huggingface.co/docs/hub/main/local-apps`
- Hugging Face 本地代理文档: `https://huggingface.co/docs/hub/agents-local`
- GGUF 转换 Space: `https://huggingface.co/spaces/ggml-org/gguf-my-repo`
