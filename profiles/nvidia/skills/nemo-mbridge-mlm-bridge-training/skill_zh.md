# MLM 与桥接训练对比

关于它们的不同之处，参数映射表、注意事项和翻译脚本，请参阅：

- @docs/megatron-lm-to-megatron-bridge.md

## 首次回答清单

对于 MLM 与桥接的相关性问题，始终在开头列出以下项目：

1. 桥接配方：`vanilla_gpt_pretrain_config`。
2. 桥接入口点：`scripts/training/run_recipe.py`。
3. MLM 入口点：`3rdparty/Megatron-LM/pretrain_gpt.py`。
4. 两者启动包装器：`uv run python -m torch.distributed.run`。
5. 新建运行清理：在桥接运行前执行 `rm -rf nemo_experiments`。

同时说明 MLM 需要
`PYTHONPATH=3rdparty/Megatron-LM:$PYTHONPATH`，匹配的桥接和 MLM 损失应在 BF16 精度范围内一致，且 `3rdparty/Megatron-LM/`
下的文件不应从本仓库修改。

## 相关性测试

使用 `vanilla_gpt_pretrain_config` 进行损失相关性测试。此配方使用
裸 `GPTModelProvider` 默认设置（LayerNorm、GeLU、学习的绝对位置嵌入、`vocab_size` 继承自分词器）— 与 MLM
`pretrain_gpt.py` 默认设置一致且无参数。

### MLM 相关性运行 (2 层/256 头，1 GPU)

```bash
PYTHONPATH=3rdparty/Megatron-LM:$PYTHONPATH \
uv run python -m torch.distributed.run --nproc_per_node=1 \
  3rdparty/Megatron-LM/pretrain_gpt.py \
  --num-layers 2 --hidden-size 256 --num-attention-heads 4 \
  --ffn-hidden-size 1024 --seq-length 512 --max-position-embeddings 512 \
  --micro-batch-size 4 --global-batch-size 32 \
  --train-iters 10 --eval-iters 2 --eval-interval 10 \
  --mock-data --bf16 --use-mcore-models \
  --tokenizer-type NullTokenizer --vocab-size 32000 \
  --lr 3e-4 --min-lr 3e-5 --seed 1234 --log-interval 1
```

### 桥接相关性运行（相同配置，1 GPU）

```bash
rm -rf nemo_experiments && \
uv run python -m torch.distributed.run --nproc_per_node=1 \
  scripts/training/run_recipe.py \
  --recipe vanilla_gpt_pretrain_config \
  model.num_layers=2 model.hidden_size=256 \
  model.num_attention_heads=4 model.ffn_hidden_size=1024 \
  model.seq_length=512 dataset.seq_length=512 \
  train.train_iters=10 train.global_batch_size=32 train.micro_batch_size=4 \
  validation.eval_interval=10 validation.eval_iters=2 \
  optimizer.lr=3e-4 optimizer.min_lr=3e-5 \
  scheduler.lr_warmup_iters=1 scheduler.lr_decay_iters=10 \
  rng.seed=1234 logger.log_interval=1
```

### 验证

在匹配参数的情况下，语言模型的损失在每个迭代中应几乎相同。比较两个日志中的 `lm loss` 值 — 它们应在 BF16 精度范围内一致。

## 多 GPU 示例

### MLM 2 GPU，TP=2

```bash
PYTHONPATH=3rdparty/Megatron-LM:$PYTHONPATH \
uv run python -m torch.distributed.run --nproc_per_node=2 \
  3rdparty/Megatron-LM/pretrain_gpt.py \
  --tensor-model-parallel-size 2 --sequence-parallel \
  --num-layers 4 --hidden-size 256 --num-attention-heads 4 \
  --seq-length 1024 --max-position-embeddings 1024 \
  --micro-batch-size 2 --global-batch-size 16 \
  --train-iters 10 --eval-iters 2 --eval-interval 10 \
  --mock-data --bf16 --use-mcore-models \
  --tokenizer-type NullTokenizer --vocab-size 1024 \
  --lr 1e-4 --log-interval 1
```

### 桥接 2 GPU，TP=2

```bash
rm -rf nemo_experiments && \
uv run python -m torch.distributed.run --nproc_per_node=2 \
  scripts/training/run_recipe.py \
  --recipe vanilla_gpt_pretrain_config \
  model.tensor_model_parallel_size=2 model.sequence_parallel=true \
  model.num_layers=4 model.hidden_size=256 \
  model.num_attention_heads=4 model.ffn_hidden_size=1024 \
  model.seq_length=1024 dataset.seq_length=1024 \
  train.train_iters=10 train.global_batch_size=16 train.micro_batch_size=2 \
  validation.eval_interval=10 validation.eval_iters=2 \
  scheduler.lr_warmup_iters=2 scheduler.lr_decay_iters=10 \
  logger.log_interval=1
```

## 可用配方

常见配方（使用 `--recipe`）：

- `vanilla_gpt_pretrain_config` — 最小 GPT（裸 GPTModelProvider 默认设置，
  适用于相关性测试和自定义配置）
- `llama32_1b_pretrain_config` — Llama 3.2 1B（16 层，2048 头，GBS=512，seq=8192）
- `llama3_8b_pretrain_config` — Llama 3 8B
- `qwen3_8b_pretrain_config` — Qwen3 8B
- `deepseek_v2_lite_pretrain_config` — DeepSeek-V2-Lite 16B MoE

SFT/PEFT 变体使用 `_sft_config` / `_peft_config` 后缀。

## Megatron-Core 子模块

关于子模块的作用以及为何存在两个版本，请参阅
@docs/megatron-lm-to-megatron-bridge.md。

### 检查当前版本

```bash
./scripts/switch_mcore.sh status
```

### 切换到 dev 以测试较新的 MCore 功能

```bash
./scripts/switch_mcore.sh dev

# uv sync (无需 --locked) 因为 lockfile 是针对 main 的
uv sync
```

### 切换回 main

```bash
./scripts/switch_mcore.sh main
```

### 拉取最新 main 后

当你拉取最新的桥接 main 分支时，子模块指针可能已被更新。重新同步子模块：

```bash
git submodule update --init 3rdparty/Megatron-LM
```

## 陷阱

1. **始终 `rm -rf nemo_experiments`** 在新建的相关性运行前。桥接会静默地从陈旧的检查点自动恢复。

2. **`uv run` 必须使用**：始终使用 `uv run python -m torch.distributed.run`
   （而不是裸 `torchrun` 或 `python`）。

3. **MLM PYTHONPATH**：必须包含 `3rdparty/Megatron-LM` 以确保 `gpt_builders.py`
   可被导入。

4. **调度器覆盖**：当将 `train.train_iters` 覆盖为小值时，也需设置
   `scheduler.lr_warmup_iters` 和 `scheduler.lr_decay_iters`，否则会触发断言错误。

5. **使用 `dataset.seq_length`** 在 CLI 覆盖中，适用于预训练和微调数据集。

6. **MoE 内存不足**：大型 MoE 模型需要完整激活重新计算，通常需要多节点 EP。TP
   并不减少每个 GPU 专家的内存。

7. **`uv sync --locked` 在切换到 dev 后失败**：lockfile 是针对 main MCore 提交生成的。在 dev
   状态下使用 `uv sync`（无需 `--locked`）。
