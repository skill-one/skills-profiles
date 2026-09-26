# llmfit 硬件模型匹配器

> 技能由 [ara.so](https://ara.so) 提供 — 2026每日技能集合。

llmfit 检测您的系统的 RAM、CPU 和 GPU，然后在质量、速度、适配度和上下文维度上对数百个 LLM 模型进行评分，告诉您哪些模型将在您的硬件上运行良好。它配备了交互式 TUI 和 CLI，支持多 GPU、MoE 架构、动态量化以及本地运行时提供者（Ollama、llama.cpp、MLX、Docker 模型运行器）。

---

## 安装

### macOS / Linux (Homebrew)
```sh
brew install llmfit
```

### 快速安装脚本
```sh
curl -fsSL https://llmfit.axjns.dev/install.sh | sh

# 无需 sudo，安装到 ~/.local/bin
curl -fsSL https://llmfit.axjns.dev/install.sh | sh -s -- --local
```

### Windows (Scoop)
```sh
scoop install llmfit
```

### Docker / Podman
```sh
docker run ghcr.io/alexsjones/llmfit

# 使用 jq 进行脚本
podman run ghcr.io/alexsjones/llmfit recommend --use-case coding | jq '.models[].name'
```

### 从源代码安装 (Rust)
```sh
git clone https://github.com/AlexsJones/llmfit.git
cd llmfit
cargo build --release
# 二进制文件位于 target/release/llmfit
```

---

## 核心概念

- **适配等级**: `perfect` (运行极佳), `good` (运行良好), `marginal` (运行但紧张), `too_tight` (无法运行)
- **评分维度**: 质量、速度（tok/s 估计）、适配度（内存余量）、上下文容量
- **运行模式**: GPU、CPU+GPU 卸载、CPU 仅、MoE
- **量化**: 自动选择最佳量化（例如 Q4_K_M、Q5_K_S、mlx-4bit）以适应您的硬件
- **提供者**: Ollama、llama.cpp、MLX、Docker 模型运行器

---

## 主要命令

### 启动交互式 TUI
```sh
llmfit
```

### CLI 表格输出
```sh
llmfit --cli
```

### 显示系统硬件检测
```sh
llmfit system
llmfit --json system   # JSON 输出
```

### 列出所有模型
```sh
llmfit list
```

### 搜索模型
```sh
llmfit search "llama 8b"
llmfit search "mistral"
llmfit search "qwen coding"
```

### 适配分析
```sh
# 所有可运行模型的适配度排名
llmfit fit

# 仅完美适配，前 5 个
llmfit fit --perfect -n 5

# JSON 输出
llmfit --json fit -n 10
```

### 模型详情
```sh
llmfit info "Mistral-7B"
llmfit info "Llama-3.1-70B"
```

### 推荐模型
```sh
# 前 5 个推荐（JSON 默认）
llmfit recommend --json --limit 5

# 按用途过滤：通用、编码、推理、聊天、多模态、嵌入
llmfit recommend --json --use-case coding --limit 3
llmfit recommend --json --use-case reasoning --limit 5
```

### 硬件规划（反转：我需要什么硬件？）
```sh
llmfit plan "Qwen/Qwen3-4B-MLX-4bit" --context 8192
llmfit plan "Qwen/Qwen3-4B-MLX-4bit" --context 8192 --quant mlx-4bit
llmfit plan "Qwen/Qwen3-4B-MLX-4bit" --context 8192 --target-tps 25 --json
llmfit plan "Qwen/Qwen2.5-Coder-0.5B-Instruct" --context 8192 --json
```

### REST API 服务器（用于集群调度）
```sh
llmfit serve
llmfit serve --host 0.0.0.0 --port 8787
```

---

## 硬件覆盖

当自动检测失败（虚拟机、损坏的 nvidia-smi、直通设置）时：

```sh
# 覆盖 GPU VRAM
llmfit --memory=32G
llmfit --memory=24G --cli
llmfit --memory=24G fit --perfect -n 5
llmfit --memory=24G recommend --json

# 兆字节
llmfit --memory=32000M

# 适用于任何子命令
llmfit --memory=16G info "Llama-3.1-70B"
```

接受的后缀：`G`/`GB`/`GiB`, `M`/`MB`/`MiB`, `T`/`TB`/`TiB`（不区分大小写）。

### 上下文长度限制
```sh
# 在 4K 上下文中估计内存适配
llmfit --max-context 4096 --cli

# 使用子命令
llmfit --max-context 8192 fit --perfect -n 5
llmfit --max-context 16384 recommend --json --limit 5

# 环境变量替代
export OLLAMA_CONTEXT_LENGTH=8192
llmfit recommend --json
```

---

## REST API 参考

启动服务器：
```sh
llmfit serve --host 0.0.0.0 --port 8787
```

### 端点

```sh
# 健康检查
curl http://localhost:8787/health

# 节点硬件信息
curl http://localhost:8787/api/v1/system

# 带过滤器的完整模型列表
curl "http://localhost:8787/api/v1/models?min_fit=marginal&runtime=llamacpp&sort=score&limit=20"

# 此节点的可运行模型（关键调度端点）
curl "http://localhost:8787/api/v1/models/top?limit=5&min_fit=good&use_case=coding"

# 按模型名称/提供者搜索
curl "http://localhost:8787/api/v1/models/Mistral?runtime=any"
```

### `/models` 和 `/models/top` 的查询参数

| 参数 | 值 | 描述 |
|---|---|---|
| `limit` / `n` | 整数 | 返回的最大行数 |
| `min_fit` | `perfect\|good\|marginal\|too_tight` | 最低适配等级 |
| `perfect` | `true\|false` | 强制仅完美 |
| `runtime` | `any\|mlx\|llamacpp` | 按运行时过滤 |
| `use_case` | `general\|coding\|reasoning\|chat\|multimodal\|embedding` | 用途过滤器 |
| `provider` | 字符串 | 提供者的子字符串匹配 |
| `search` | 字符串 | 跨名称/提供者/大小/用途的自由文本搜索 |
| `sort` | `score\|tps\|params\|mem\|ctx\|date\|use_case` | 排序列 |
| `include_too_tight` | `true\|false` | 包含不可运行的模型 |
| `max_context` | 整数 | 每个请求的上下文限制 |

---

## 脚本与自动化示例

### Bash: 获取前 3 个编码模型为 JSON
```bash
#!/bin/bash
# 获取适配完美的前 3 个编码模型
llmfit recommend --json --use-case coding --limit 3 | \
  jq -r '.models[] | "\(.name) (\(.score)) - \(.quantization)"'
```

### Bash: 检查特定模型是否适配
```bash
#!/bin/bash
MODEL="Mistral-7B"
RESULT=$(llmfit info "$MODEL" --json 2>/dev/null)
FIT=$(echo "$RESULT" | jq -r '.fit')
if [[ "$FIT" == "perfect" || "$FIT" == "good" ]]; then
  echo "$MODEL 将运行良好 (适配度: $FIT)"
else
  echo "$MODEL 可能运行不佳 (适配度: $FIT)"
fi
```

### Bash: 自动拉取前 Ollama 模型
```bash
#!/bin/bash
# 获取适配度最高的模型名称并使用 Ollama 拉取
TOP_MODEL=$(llmfit recommend --json --limit 1 | jq -r '.models[0].name')
echo "拉取: $TOP_MODEL"
ollama pull "$TOP_MODEL"
```

### Python: 查询 REST API
```python
import requests

BASE_URL = "http://localhost:8787"

def get_system_info():
    resp = requests.get(f"{BASE_URL}/api/v1/system")
    return resp.json()

def get_top_models(use_case="coding", limit=5, min_fit="good"):
    params = {
        "use_case": use_case,
        "limit": limit,
        "min_fit": min_fit,
        "sort": "score"
    }
    resp = requests.get(f"{BASE_URL}/api/v1/models/top", params=params)
    return resp.json()

def search_models(query, runtime="any"):
    resp = requests.get(
        f"{BASE_URL}/api/v1/models/{query}",
        params={"runtime": runtime}
    )
    return resp.json()

# 示例用法
system = get_system_info()
print(f"GPU: {system.get('gpu_name')} | VRAM: {system.get('vram_gb')}GB")

models = get_top_models(use_case="reasoning", limit=3)
for m in models.get("models", []):
    print(f"{m['name']}: score={m['score']}, fit={m['fit']}, quant={m['quantization']}")
```

### Python: 硬件感知模型选择器（用于代理）
```python
import subprocess
import json

def get_best_model_for_task(use_case: str, min_fit: str = "good") -> dict:
    """使用 llmfit 为给定任务选择最佳模型。"""
    result = subprocess.run(
        ["llmfit", "recommend", "--json", "--use-case", use_case, "--limit", "1"],
        capture_output=True,
        text=True
    )
    data = json.loads(result.stdout)
    models = data.get("models", [])
    return models[0] if models else None

def plan_hardware_requirements(model_name: str, context: int = 4096) -> dict:
    """获取运行特定模型的硬件要求。"""
    result = subprocess.run(
        ["llmfit", "plan", model_name, "--context", str(context), "--json"],
        capture_output=True,
        text=True
    )
    return json.loads(result.stdout)

# 选择最佳编码模型
best = get_best_model_for_task("coding")
if best:
    print(f"最佳编码模型: {best['name']}")
    print(f"  量化: {best['quantization']}")
    print(f"  估计 tok/s: {best['tps']}")
    print(f"  内存使用: {best['mem_pct']}%")

# 为特定模型规划硬件
plan = plan_hardware_requirements("Qwen/Qwen3-4B-MLX-4bit", context=8192)
print(f"所需最小 VRAM: {plan['hardware']['min_vram_gb']}GB")
print(f"推荐 VRAM: {plan['hardware']['recommended_vram_gb']}GB")
```

### Docker Compose: 节点调度模式
```yaml
version: "3.8"
services:
  llmfit-api:
    image: ghcr.io/alexsjones/llmfit
    command: serve --host 0.0.0.0 --port 8787
    ports:
      - "8787:8787"
    environment:
      - OLLAMA_CONTEXT_LENGTH=8192
    devices:
      - /dev/nvidia0:/dev/nvidia0  # GPU 直通
```

---

## TUI 键盘参考

| 键 | 动作 |
|---|---|
| `↑`/`↓` 或 `j`/`k` | 导航模型 |
| `/` | 搜索（名称、提供者、参数、用途） |
| `Esc`/`Enter` | 退出搜索 |
| `Ctrl-U` | 清除搜索 |
| `f` | 循环适配过滤器：全部 → 可运行 → 完美 → 良好 → 一般 |
| `a` | 循环可用性：全部 → GGUF 可用 → 已安装 |
| `s` | 循环排序：评分 → 参数 → 内存% → 上下文 → 日期 → 用途 |
| `t` | 循环颜色主题（自动保存） |
| `v` | 视觉模式（多选用于比较） |
| `V` | 选择模式（基于列的过滤） |
| `p` | 规划模式（此模型需要什么硬件？） |
| `P` | 提供者过滤弹出 |
| `U` | 用途过滤弹出 |
| `C` | 能力过滤弹出 |
| `m` | 标记模型用于比较 |
| `c` | 比较视图（标记与选中） |
| `d` | 下载模型（通过检测的运行时） |
| `r` | 从运行时刷新已安装模型 |
| `Enter` | 切换详情视图 |
| `g`/`G` | 跳到顶部/底部 |
| `q` | 退出 |

### 主题
`t` 循环：默认 → Dracula → Solarized → Nord → Monokai → Gruvbox  
主题保存到 `~/.config/llmfit/theme`

---

## GPU 检测详情

| GPU 提供商 | 检测方法 |
|---|---|
| NVIDIA | `nvidia-smi`（多 GPU，聚合 VRAM） |
| AMD | `rocm-smi` |
| Intel Arc | sysfs（独立） / `lspci`（集成） |
| Apple Silicon | `system_profiler`（统一内存 = VRAM） |
| Ascend | `npu-smi` |

---

## 常见模式

### "我的 16GB M2 Mac 可以运行什么？"
```sh
llmfit fit --perfect -n 10
# 或交互式
llmfit
# 按 'f' 过滤到完美适配
```

### "我有 3090（24GB VRAM），哪些编码模型适配？"
```sh
llmfit recommend --json --use-case coding | jq '.models[]'
# 或手动覆盖如果检测失败
llmfit --memory=24G recommend --json --use-case coding
```

### "Llama 70B 能在我的机器上运行吗？"
```sh
llmfit info "Llama-3.1-70B"
# 规划您需要的硬件
llmfit plan "Llama-3.1-70B" --context 4096 --json
```

### "只显示已安装在 Ollama 的模型"
```sh
llmfit
# 按 'a' 循环到已安装过滤器
# 或
llmfit fit -n 20  # 运行，在 TUI 中按 'i' 为已安装优先
```

### "脚本：找到最佳模型并启动 Ollama"
```bash
MODEL=$(llmfit recommend --json --limit 1 | jq -r '.models[0].name')
ollama serve &
ollama run "$MODEL"
```

### "API：轮询节点能力以供集群调度"
```bash
# 检查节点，获取前 3 个良好+模型用于推理
curl -s "http://node1:8787/api/v1/models/top?limit=3&min_fit=good&use_case=reasoning" | \
  jq '.models[].name'
```

---

## 故障排除

**GPU 未检测到 / 报告 VRAM 错误**
```sh
# 验证检测
llmfit system

# 手动覆盖
llmfit --memory=24G --cli
```

**`nvidia-smi` 未找到但您有 NVIDIA GPU**
```sh
# 安装 CUDA 工具包或 nvidia-utils，然后重试
# 或手动覆盖：
llmfit --memory=8G fit --perfect
```

**模型显示为 too_tight 但您有足够的 RAM**
```sh
# llmfit 可能使用上下文膨胀估计；限制上下文
llmfit --max-context 2048 fit --perfect -n 10
```

**REST API：测试端点**
```sh
# 启动服务器并运行验证套件
python3 scripts/test_api.py --spawn

# 测试正在运行的服务器
python3 scripts/test_api.py --base-url http://127.0.0.1:8787
```

**Apple Silicon：VRAM 显示为系统 RAM（预期）**
```sh
# 这是正确的 — Apple Silicon 使用统一内存
# llmfit 自动考虑这一点
llmfit system  # 应显示后端: Metal
```

**上下文长度环境变量**
```sh
export OLLAMA_CONTEXT_LENGTH=4096
llmfit recommend --json  # 使用 4096 作为上下文限制
```
