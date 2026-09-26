# nanochat LLM 训练

> 技能由 [ara.so](https://ara.so) 提供 — 每日 2026 技能集合。

nanochat 是 Karpathy 开发的一个极简、可定制的 LLM 训练框架，可以在单个 GPU 节点上端到端训练 LLM。它涵盖了分词、预训练、SFT 微调、强化学习、评估（DCLM CORE 分数）、使用 KV 缓存的推理，以及类似 ChatGPT 的 Web 界面。一个单一的复杂度调节器（`--depth`）会自动配置所有其他超参数（宽度、注意力头数、学习率、训练时间、权重衰减），以实现计算最优的训练。你可以在 8×H100 节点上以约 48 美元的价格重现 GPT-2 的能力（2019 年约 43,000 美元），耗时约 2 小时。

## 安装

nanochat 使用 `uv` 进行依赖管理：

```bash
git clone https://github.com/karpathy/nanochat.git
cd nanochat
# 如有需要，安装 uv
curl -LsSf https://astral.sh/uv/install.sh | sh
# 创建虚拟环境并安装依赖
uv sync
source .venv/bin/activate
```

## 主要命令

### 完整 GPT-2 快速训练（8×H100 节点，约 2–3 小时，约 48 美元）

```bash
# 运行参考流程：数据下载、预训练、SFT、评估、聊天
bash runs/speedrun.sh
```

### 预训练（分布式）

```bash
OMP_NUM_THREADS=1 torchrun --standalone --nproc_per_node=8 -m scripts.base_train -- \
    --depth=26 \
    --run="d26_run" \
    --model-tag="d26"
```

### 预训练（单个 GPU）

```bash
python -m scripts.base_train -- \
    --depth=26 \
    --run="d26_single"
```

### 快速研究迭代（约 5 分钟，GPT-1 规模）

```bash
OMP_NUM_THREADS=1 torchrun --standalone --nproc_per_node=8 -m scripts.base_train -- \
    --depth=12 \
    --run="d12_exp" \
    --model-tag="d12" \
    --core-metric-every=999999 \
    --sample-every=-1 \
    --save-every=-1
```

### CPU / Apple Silicon（小型模型，约几分钟）

```bash
bash runs/runcpu.sh
```

### 提供 Chat UI

```bash
# 训练完成后
source .venv/bin/activate
python -m scripts.chat_web
# 访问 http://<你的服务器 IP>:8000/
```

### CLI 聊天

```bash
python -m scripts.chat_cli -p "hello"
```

### 缩放定律 / 短剧系列

```bash
bash runs/scaling_laws.sh   # 扫描深度以获取缩放定律数据
bash runs/miniseries.sh     # 训练完整的计算最优短剧系列
```

## 深度调节器

最重要的参数。其他所有参数都会自动推导：

| `--depth` | 大致模型规模 | 备注 |
|-----------|----------------|-------|
| 6–8 | 微型（玩具） | CPU/MPS 可行 |
| 12 | GPT-1 规模 | 8×H100 上约 5 分钟，非常适合研究迭代 |
| 16 | 中型 | 8×H100 上约 15 分钟 |
| 24–26 | GPT-2 规模 | 8×H100 上约 2 小时，约 48 美元 |

```bash
# 更小/更快的实验
python -m scripts.base_train -- --depth=12 --run="quick_test"

# 完整 GPT-2 等级
torchrun --standalone --nproc_per_node=8 -m scripts.base_train -- --depth=26 --run="gpt2_repro"
```

## 精度 / dtype 配置

nanochat 通过 `nanochat/common.py` 中的 `COMPUTE_DTYPE` 进行显式的 dtype 管理。不使用 `torch.amp.autocast`。

| 硬件 | 默认 | 覆盖 |
|----------|---------|---------|
| CUDA SM 80+ (A100, H100) | `bfloat16` | `NANOCHAT_DTYPE=float32` |
| CUDA SM < 80 (V100, T4) | `float32` | `NANOCHAT_DTYPE=float16` |
| CPU / MPS | `float32` | — |

```bash
# 强制推理使用 fp32
NANOCHAT_DTYPE=float32 python -m scripts.chat_cli -p "hello"

# 强制训练使用 bf16
NANOCHAT_DTYPE=bfloat16 torchrun --nproc_per_node=8 -m scripts.base_train

# float16 训练（自动启用 GradScaler）
NANOCHAT_DTYPE=float16 torchrun --nproc_per_node=8 -m scripts.base_train
```

**工作原理：** 权重以 fp32 存储（优化器精度），自定义 `Linear` 在前向传递中转换为 `COMPUTE_DTYPE`，嵌入直接以 `COMPUTE_DTYPE` 存储，以节省内存。

## 主要 Python 模块

```
nanochat/
├── gpt.py              # GPT nn.Module Transformer
├── engine.py           # 使用 KV 缓存的推理
├── dataloader.py       # 分词分布式数据加载器
├── dataset.py          # 预训练数据下载/读取工具
├── optim.py            # AdamW + Muon 优化器（1GPU 和分布式）
├── core_eval.py        # DCLM CORE 分数评估
├── loss_eval.py        # 每字节比特评估
├── checkpoint_manager.py  # 保存/加载检查点
├── common.py           # 工具，COMPUTE_DTYPE
├── execution.py        # LLM Python 代码执行工具
└── engine.py           # 高效 KV 缓存推理

scripts/
├── base_train.py       # 预训练入口
├── chat_web.py         # Web 聊天 UI 服务器
└── chat_cli.py         # CLI 聊天界面

runs/
├── speedrun.sh         # 参考完整流程（GPT-2 快速训练）
├── scaling_laws.sh     # 缩放定律扫描
├── miniseries.sh       # 完整计算最优短剧系列
└── runcpu.sh           # CPU/MPS 示例
```

## 实际代码示例

### 加载并在训练好的模型上运行推理

```python
import torch
from nanochat.gpt import GPT
from nanochat.engine import InferenceEngine
from nanochat.checkpoint_manager import CheckpointManager

# 加载检查点
ckpt_manager = CheckpointManager("checkpoints/d26")
model, config = ckpt_manager.load()
model.eval()

# 使用 KV 缓存运行推理
engine = InferenceEngine(model)
output = engine.generate(
    prompt="Once upon a time",
    max_new_tokens=200,
    temperature=0.8,
    top_p=0.95,
)
print(output)
```

### 带深度调节器的自定义训练脚本

```python
import subprocess

def train_model(depth: int, run_name: str, nproc: int = 8):
    """为给定深度启动计算最优的训练运行."""
    cmd = [
        "torchrun",
        "--standalone",
        f"--nproc_per_node={nproc}",
        "-m", "scripts.base_train",
        "--",
        f"--depth={depth}",
        f"--run={run_name}",
        f"--model-tag={run_name}",
    ]
    subprocess.run(cmd, env={"OMP_NUM_THREADS": "1", **__import__("os").environ})

# 快速研究迭代
train_model(depth=12, run_name="my_experiment_d12")

# 完整 GPT-2 等级
train_model(depth=26, run_name="my_gpt2_repro")
```

### 调整设备批大小以降低 VRAM

```bash
# 默认 device_batch_size=32 需要 ~80GB 每个 GPU 的 VRAM
# 为更小的 GPU 减少批大小（梯度累积处理其余部分）
torchrun --standalone --nproc_per_node=4 -m scripts.base_train -- \
    --depth=12 \
    --device_batch_size=16 \
    --run="low_vram_run"

# 更小
python -m scripts.base_train -- \
    --depth=8 \
    --device_batch_size=4 \
    --run="single_gpu_small"
```

### 在 wandb 中监控关键指标

```python
# nanochat 自动记录到 wandb。要监控的关键指标：
# - val_bpb: 验证损失（每字节比特）（与词汇量大小无关）
#   作为步骤、总训练时间、总训练 FLOPS 的函数
# - core_metric: DCLM CORE 分数（目标 > 0.2565 以超越 GPT-2）
# - train/mfu: 模型 FLOPS 利用率
# - train/tok_per_sec: 训练吞吐量

# 训练前通过环境变量设置 wandb 项目
import os
os.environ["WANDB_PROJECT"] = "my-nanochat-runs"
```

### 用于 SFT 人格的合成数据

```python
# dev/gen_synthetic_data.py — 生成身份/人格数据
# 然后按照指南将其混合到 SFT 阶段：
# https://github.com/karpathy/nanochat/discussions/139

# 示例：生成数据并指向 SFT
python dev/gen_synthetic_data.py --output data/identity_sft.jsonl
# 然后在你的 SFT 脚本配置中引用它
```

## 常见模式

### 研究迭代循环

```bash
# 1. 在 nanochat/ 中进行代码更改
# 2. 运行快速 d12 以验证
OMP_NUM_THREADS=1 torchrun --standalone --nproc_per_node=8 -m scripts.base_train -- \
    --depth=12 --run="test_my_change" \
    --core-metric-every=999999 --sample-every=-1 --save-every=-1
# 3. 检查 wandb：val_bpb 与步骤/时间/FLOPS
# 4. 如果有前景，测试 d16 或 d26
```

### FP8 训练（仅 H100，用于快速训练）

```bash
# FP8 用于速度训练以获得额外的加速
# 参考 runs/speedrun.sh 获取确切调用
bash runs/speedrun.sh
```

### 仅评估 CORE 分数

```bash
python -m nanochat.core_eval --checkpoint checkpoints/d26/latest
```

### 在 Lambda / 远程机器上运行

```bash
# 在训练后的远程机器上：
source .venv/bin/activate
python -m scripts.chat_web
# 通过：http://<公共 IP>:8000/
# 使用 `screen` 或 `tmux` 保持运行
screen -S nanochat
python -m scripts.chat_web
# Ctrl+A, D 以分离
```

## 故障排除

### OOM / VRAM 超出

```bash
# 减少 --device_batch_size (默认 32)
# 代码使用梯度累积以保持有效批大小
--device_batch_size=16   # 尝试 16, 8, 4, 2, 1
```

### 单个 GPU 慢 8 倍

这是预期的。省略 `torchrun` 并直接使用 `python -m scripts.base_train`。梯度累积会自动启动以保持等效总批大小。

### 在非 CUDA 硬件上运行

```bash
# MPS (Apple Silicon) 或 CPU — 使用 runcpu.sh 作为模板
bash runs/runcpu.sh
# 结果会较弱；这仅用于开发/调试
```

### float16 梯度下溢

```bash
# nanochat 在 NANOCHAT_DTYPE=float16 时自动启用 GradScaler
NANOCHAT_DTYPE=float16 torchrun --nproc_per_node=8 -m scripts.base_train -- --depth=12
# 注意：RL 脚本不支持 float16 (SFT 和 base_train 支持)
```

### V100 / T4 (SM < 80) — 没有 bf16

```bash
# 默认回退到 float32；可选使用 float16
NANOCHAT_DTYPE=float16 torchrun --nproc_per_node=8 -m scripts.base_train -- --depth=12
```

### Chat UI 无法访问

```bash
# 确保端口（默认 8000）在你的云提供商的防火墙/安全组中开放
# 使用公共 IP，而不是 localhost：
# http://<公共 IP>:8000/
```

## 资源

- **DeepWiki Q&A**: https://deepwiki.com/karpathy/nanochat
- **讨论**: https://github.com/karpathy/nanochat/discussions
- **Discord**: `#nanochat` 频道在 Karpathy 的 Discord 上
- **排行榜文档**: `dev/LEADERBOARD.md`
- **超越 GPT-2 指南**: https://github.com/karpathy/nanochat/discussions/481
- **短剧系列 v1**: https://github.com/karpathy/nanochat/discussions/420
- **添加能力指南**: https://github.com/karpathy/nanochat/discussions/164
