# OpenClaw-RL 训练

> 技能由 [ara.so](https://ara.so) 提供 — 2026每日技能合集。

OpenClaw-RL 是一个完全异步的强化学习框架，它将实时的多轮对话转换为个性化AI代理的训练信号。它通过 [OpenClaw](https://openclaw.ai) 将自托管模型封装为兼容OpenAI的API，拦截对话，并在后台持续优化策略而不中断使用。它还支持适用于终端、GUI、SWE和工具调用代理的可扩展强化学习。

## 架构概述

四个独立的异步循环，彼此永不阻塞：
1. **代理服务** — 提供兼容OpenClaw的API服务策略
2. **策略收集** — 捕获多轮对话作为训练轨迹
3. **PRM/裁判评估** — 使用下一状态反馈评分回合（可选多数投票）
4. **策略训练** — 通过 [slime](https://github.com/THUDM/slime) 或 [Tinker](https://thinkingmachines.ai/tinker/) 进行GRPO/OPD/Combine训练

## 安装

```bash
git clone https://github.com/Gen-Verse/OpenClaw-RL
cd OpenClaw-RL

# 安装核心依赖
pip install -r requirements.txt

# 安装slime（训练后端）
cd slime && pip install -e . && cd ..

# 可选：安装SGLang以实现快速推理
pip install sglang
```

## 项目结构

```
OpenClaw-RL/
├── openclaw-rl/          # 二进制RL (GRPO) 方法
├── openclaw-opd/         # 在线策略蒸馏方法
├── openclaw-combine/     # 组合二进制RL + OPD
├── openclaw-test/        # 评估工具
├── terminal-rl/          # 跟踪2：终端代理RL
├── gui-rl/               # 跟踪2：GUI代理RL
├── swe-rl/               # 跟踪2：SWE代理RL
├── toolcall-rl/          # 跟踪2：工具调用代理RL
├── slime/                # 核心训练框架
└── openclaw/             # 运行时 / API服务器
```

## 三种学习范式

### 1. 二进制RL (GRPO)
一个过程奖励模型根据下一状态反馈评分每个回合。使用GRPO优势估计和PPO风格的剪裁代理损失。

### 2. 在线策略蒸馏 (OPD)
当下一状态揭示有用的后见之明时，一个裁判提取文本提示来增强提示，创建一个增强的教师。标记级别的对数概率差距成为方向性优势信号。

### 3. 组合方法（推荐）
合并二进制RL标量监督与OPD标记级别方向性信号。最强壮且最稳健的优化。

## 快速入门 — 个人代理（跟踪1）

### 二进制RL启动脚本

```bash
# openclaw-rl/run_qwen3_7b_openclaw_rl.sh
export MODEL_PATH=/path/to/qwen3-7b
export DATA_PATH=/path/to/conversation/data
export CKPT_SAVE_DIR=/path/to/checkpoints

bash openclaw-rl/run_qwen3_7b_openclaw_rl.sh
```

### OPD启动脚本

```bash
export MODEL_PATH=/path/to/qwen3-7b
export JUDGE_MODEL_PATH=/path/to/judge-model
export DATA_PATH=/path/to/conversation/data

bash openclaw-opd/run_qwen3_7b_openclaw_opd.sh
```

### 组合方法（一行）

```bash
# 使用二进制RL + OPD组合启动
bash openclaw-combine/run_qwen3_7b_openclaw_combine.sh
```

## 配置 — 关键环境变量

```bash
# 模型配置
export MODEL_PATH=/path/to/base/model
export JUDGE_MODEL_PATH=/path/to/judge/model   # 用于OPD
export PRM_MODEL_PATH=/path/to/prm/model       # 用于二进制RL

# 训练配置
export CKPT_SAVE_DIR=./checkpoints
export CKPT_ARGS="--save-interval 100 --save-dir $CKPT_SAVE_DIR"

# 策略收集配置
export ROLLOUT_ARGS="--rollout-batch-size 64 --num-rollouts-per-prompt 4"

# 优化器配置
export OPTIMIZER_ARGS="--lr 1e-6 --weight-decay 0.01 --adam-beta1 0.9 --adam-beta2 0.999"

# GPU分区（例如，8个GPU：4个用于训练，4个用于策略收集）
export TRAIN_GPUS="0,1,2,3"
export ROLLOUT_GPUS="4,5,6,7"

# LoRA（可选，减少GPU内存）
export LORA_ARGS="--lora-rank 64 --lora-alpha 128 --lora-dropout 0.05"
```

## LoRA训练

```bash
# 向任何启动脚本添加LoRA参数
export LORA_ARGS="--use-lora --lora-rank 64 --lora-alpha 128"

# 示例：LoRA二进制RL
bash openclaw-rl/run_qwen3_7b_lora_openclaw_rl.sh
```

## 自定义损失 / 策略收集函数（插件API）

slime框架提供了扩展点，而无需修改核心代码：

```bash
# 自定义损失函数
--custom-loss-function-path ./my_method/custom_loss.py

# 自定义策略收集函数  
--rollout-function-path ./my_method/custom_rollout.py

# 自定义生成函数
--custom-generate-function-path ./my_method/custom_generate.py

# 自定义奖励模型
--custom-rm-path ./my_method/custom_rm.py
```

### 自定义损失示例（TypeScript风格的配置，Python实现）

```python
# my_method/custom_loss.py
import torch
from typing import Dict, Any

def compute_loss(
    policy_logits: torch.Tensor,
    reference_logits: torch.Tensor,
    rewards: torch.Tensor,
    advantages: torch.Tensor,
    config: Dict[str, Any]
) -> torch.Tensor:
    """
    自定义GRPO风格损失，带剪裁代理目标。
    """
    # 策略与参考之间的对数比
    log_ratio = policy_logits - reference_logits
    ratio = torch.exp(log_ratio)
    
    clip_range = config.get("clip_range", 0.2)
    
    # PPO风格的剪裁目标
    clipped = torch.clamp(ratio, 1 - clip_range, 1 + clip_range)
    loss = -torch.min(ratio * advantages, clipped * advantages).mean()
    
    # KL惩罚
    kl_coeff = config.get("kl_coeff", 0.01)
    kl_penalty = kl_coeff * log_ratio.mean()
    
    return loss + kl_penalty
```

### 自定义奖励模型示例

```python
# my_method/custom_rm.py
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

class CustomPRM:
    def __init__(self, model_path: str):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_path, torch_dtype=torch.bfloat16
        )
        self.model.eval()

    def score(self, prompt: str, response: str, next_state: str) -> float:
        """
        给定提示、响应和下一状态反馈，评分一个回合。
        """
        combined = f"Prompt: {prompt}\nResponse: {response}\nOutcome: {next_state}"
        inputs = self.tokenizer(combined, return_tensors="pt", truncation=True, max_length=2048)
        
        with torch.no_grad():
            logits = self.model(**inputs).logits
        
        # 二进制奖励：正类概率
        return torch.softmax(logits, dim=-1)[0, 1].item()


def get_reward_model(config):
    return CustomPRM(config["prm_model_path"])
```

## 在Tinker上部署（云）

```bash
# 一行云部署 — 混合RL、OPD、二进制RL都支持
export TINKER_API_KEY=$TINKER_API_KEY
export TINKER_ENDPOINT=$TINKER_ENDPOINT

# 通过Ray提交任务
ray job submit --address $TINKER_ENDPOINT \
  --working-dir . \
  -- bash openclaw-combine/run_qwen3_7b_openclaw_combine.sh
```

## 跟踪2 — 通用代理RL

### 终端代理RL

```bash
export ENV_TYPE=terminal
export MAX_STEPS=20
export PARALLEL_ENVS=32   # 并行环境实例数量

bash terminal-rl/run_terminal_rl.sh
```

### GUI代理RL

```bash
export ENV_TYPE=gui
export SCREENSHOT_BACKEND=playwright   # 或selenium
export PARALLEL_ENVS=16

bash gui-rl/run_gui_rl.sh
```

### 工具调用代理RL

```bash
export ENV_TYPE=toolcall
export TOOLS_CONFIG=./toolcall-rl/tools_config.json
export PARALLEL_ENVS=64

bash toolcall-rl/run_toolcall_rl.sh
```

### SWE代理RL

```bash
export ENV_TYPE=swe
export SWE_BENCH_PATH=/path/to/swe-bench
export PARALLEL_ENVS=8   # SWE环境更重

bash swe-rl/run_swe_rl.sh
```

## 数据格式 — 对话轨迹

OpenClaw-RL自动分类API消息。自定义数据的手动格式：

```json
{
  "session_id": "user_session_abc123",
  "turns": [
    {
      "type": "main",
      "prompt": "帮我重构这个函数以使用async/await",
      "response": "这是重构版本：...",
      "next_state": "用户接受了更改，并说'完美，谢谢！'",
      "trainable": true
    },
    {
      "type": "side", 
      "prompt": "2+2等于多少？",
      "response": "4",
      "trainable": false
    }
  ]
}
```

- **`main`回合**：构成训练轨迹的多轮交互
- **`side`回合**：非训练系统/工具回合，排除在训练之外

## OpenClaw API服务器设置

```bash
# 启动兼容OpenClaw的API服务器，封装你的模型
export BASE_MODEL_PATH=/path/to/your/model
export OPENCLAW_PORT=8000
export OPENCLAW_HOST=0.0.0.0

# 使用SGLang后端（推荐，速度更快）
python -m openclaw.server \
  --model-path $BASE_MODEL_PATH \
  --port $OPENCLAW_PORT \
  --backend sglang \
  --enable-rl-intercept          # 启用对话捕获以用于RL
  --rl-buffer-dir ./rl_buffer    # 存储捕获轨迹的位置
```

```typescript
// 在TypeScript中将服务器用作兼容OpenAI的API
import OpenAI from "openai";

const client = new OpenAI({
  baseURL: "http://localhost:8000/v1",
  apiKey: process.env.OPENCLAW_API_KEY ?? "local",
});

const response = await client.chat.completions.create({
  model: "your-model-name",
  messages: [
    { role: "user", content: "帮我写一个排序算法" }
  ],
  stream: true,
});

for await (const chunk of response) {
  process.stdout.write(chunk.choices[0]?.delta?.content ?? "");
}
```

## 多数投票用于稳健的PRM评分

```bash
# 启用多数投票以实现更稳健的奖励估计
export MAJORITY_VOTE_N=5   # 每个回合的裁判调用次数
export MAJORITY_VOTE_THRESHOLD=0.6

# 添加到你的启动脚本参数：
--majority-vote-n $MAJORITY_VOTE_N \
--majority-vote-threshold $MAJORITY_VOTE_THRESHOLD
```

## 添加新方法（贡献模式）

```bash
# 1. 创建一个新的一级文件夹
mkdir my-new-method
cd my-new-method

# 2. 必要的文件
touch README.md                           # 记录是什么，如何，环境变量
touch run_qwen3_7b_my_method.sh          # 启动脚本
touch custom_loss.py                      # 如果需要自定义损失
touch custom_rollout.py                   # 如果需要自定义策略收集
```

```bash
# run_qwen3_7b_my_method.sh — 遵循现有约定
#!/bin/bash
set -e

MODEL_SIZE="7b"
MODEL_PATH=${MODEL_PATH:-/path/to/qwen3-7b}
CKPT_SAVE_DIR=${CKPT_SAVE_DIR:-./checkpoints/my-method}

CKPT_ARGS="--save-interval 50 --save-dir $CKPT_SAVE_DIR"
ROLLOUT_ARGS="--rollout-batch-size 32 --num-rollouts-per-prompt 4"
OPTIMIZER_ARGS="--lr 1e-6 --weight-decay 0.01"

ray job submit --working-dir .. -- \
  python slime/train.py \
    --model-path $MODEL_PATH \
    --custom-loss-function-path my-new-method/custom_loss.py \
    $CKPT_ARGS $ROLLOUT_ARGS $OPTIMIZER_ARGS
```

## 常见模式

### 监控训练进度

```bash
# 查看Ray仪表板
ray dashboard  # 在http://localhost:8265打开

# 监控检查点保存
watch -n 10 ls -la $CKPT_SAVE_DIR

# 流式传输训练日志
tail -f ./logs/training.log
```

### 从检查点恢复

```bash
export RESUME_CKPT=$CKPT_SAVE_DIR/checkpoint-500
# 添加到启动脚本：
--resume-from-checkpoint $RESUME_CKPT
```

### 评估训练好的检查点

```bash
bash openclaw-test/run_eval.sh \
  --model-path $CKPT_SAVE_DIR/checkpoint-latest \
  --eval-tasks "conversation,coding,tool-use"
```

## 故障排除

**在策略收集+训练期间GPU内存不足：**
```bash
# 使用LoRA减少内存占用
export LORA_ARGS="--use-lora --lora-rank 32"
# 或减少并行环境
export PARALLEL_ENVS=8
# 或使用卸载
--offload-optimizer-state
```

**异步循环落后（缓冲区溢出）：**
```bash
# 减少策略收集批次大小或增加裁判吞吐量
export ROLLOUT_ARGS="--rollout-batch-size 16"
# 或添加更多裁判工作线程
--num-judge-workers 4
```

**PRM分数全部接近0.5（奖励崩溃）：**
- 验证 `next_state` 字段是否包含有意义的反馈信号
- 检查裁判模型提示模板是否匹配预期格式
- 尝试增加多数投票N：`--majority-vote-n 7`

**SGLang服务器未启动：**
```bash
# 检查SGLang版本兼容性
pip install sglang==0.4.x  # 检查slime/requirements.txt中固定的版本
# 回退到vLLM后端
--backend vllm
```

**Ray任务提交失败：**
```bash
# 首先启动Ray集群
ray start --head --num-gpus=$(nvidia-smi -L | wc -l)
# 然后提交任务
ray job submit --address auto -- bash run.sh
```

## 关键参考资料

- [技术报告 (arXiv)](https://arxiv.org/abs/2603.10165)
- [OpenClaw插件](https://openclaw.ai)
- [Slime训练框架](https://github.com/THUDM/slime)
- [Tinker云平台](https://thinkingmachines.ai/tinker/)
- [SDFT论文](https://arxiv.org/abs/2601.19897) — 集成在openclaw-opd中
- [SDPO论文](https://arxiv.org/abs/2601.20802) — 集成在openclaw-opd中
