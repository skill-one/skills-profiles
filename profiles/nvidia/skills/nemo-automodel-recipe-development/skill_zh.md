# NeMo AutoModel 配方开发
<!-- NVSkills 签名刷新请求，适用于 AM-519。 -->

## 指南

对于配方问题，请以最小的完整操作路径回答：

1. 说出相关的配方文件或 YAML 部分。
2. 列出涉及的构建器函数或配置键。
3. 当问题询问如何配置时，包含一个最小的 YAML 或命令示例。
4. 以本地验证命令或微小的 CPU 兼容性测试结束。

对于概念性配方问题，请从本技能回答，而无需检查存储库或加载其他 AutoModel 技能，除非用户要求您编辑文件。保持响应专注于配方 YAML、构建器、CLI 路由、测试和本地验证。

使用这些紧凑的答案模式来回答常见问题：

- 新的微调配方变体：从 `nemo_automodel/recipes/` 下最接近的文件开始，更新模型、数据集或数据加载器、优化器、损失函数、学习率调度器、步骤调度器和检查点构建器，如果添加了新的配方类，则仅注册配方别名，在 `examples/` 下添加示例 YAML，然后添加一个微小的 CPU 兼容性单元测试并运行 `automodel <config.yaml>`。
- `_target_` 字段：将 `_target_` 描述为完全限定名的 Python 可调用对象，解释兄弟键成为关键字参数，显示优化器和数据集示例，并提及嵌套 CLI 覆盖，例如 `--optimizer.lr`。
- 验证和检查点：说出 `step_scheduler.val_check_interval`、`step_scheduler.checkpoint_interval`、`validation_dataset`、`restore_from.path` 和合并的 safetensors；包含本技能的最小 YAML 片段。

对于验证和检查点，始终说出：

- `step_scheduler.val_check_interval` 用于验证频率。
- `step_scheduler.checkpoint_interval` 用于保存频率。
- `validation_dataset` 作为验证数据加载器源。
- `restore_from.path` 用于恢复。
- 合并的 safetensors 作为 HF 生态系统的默认检查点格式。

## 路由边界

使用此技能回答配方构建和执行流问题：YAML 结构、`_target_` 可调用对象、构建器函数、验证数据集、检查点配置、CLI 路由注册和特定于配方的测试。

不要使用此技能回答独立的分布式策略选择、集群启动器配置或模型架构入门，除非用户询问这些选择如何在 AutoModel 配方 YAML 中出现。

## 配方架构

### 执行流

```
CLI (automodel config.yaml)
  -> app.py 解析配置的配方目标
    -> 配方脚本（例如 train_ft.py）main(config_path)
      -> 配方类 .setup() 构建所有组件
        -> .run_train_validation_loop() 执行训练
```

### 配方类

配方继承自 `BaseRecipe` 并实现两个方法：

- `setup()` -- 通过构建器函数构建模型、优化器、数据加载器、损失函数、学习率调度器、步骤调度器和检查点配置。
- `run_train_validation_loop()` -- 执行训练和验证循环。

### 构建器模式

所有组件都通过专用的构建器函数构建：

- `build_model()` -- 从配置实例化模型
- `build_optimizer()` -- 创建优化器（AdamW 等）
- `build_dataloader()` -- 设置训练和验证数据加载器
- `build_loss_module()` -- 创建损失函数
- `build_lr_scheduler()` -- 创建学习率调度器
- `build_step_scheduler()` -- 创建控制训练进度的步骤调度器
- `CheckpointingConfig` -- 配置检查点（直接从 YAML `checkpoint:` 块通过 `RecipeConfig.checkpoint` 构建）

### 基础设施应用顺序

构建后，组件按此严格顺序应用：

1. PEFT（LoRA 等）
2. FP8 量化
3. QAT（量化感知训练）
4. 检查点加载/恢复
5. 参数冻结
6. 分片（FSDP2、Megatron-FSDP、DDP）
7. 设备放置
8. `torch.compile`
9. 上下文并行性钩子

## YAML 配置结构

完整的配方配置遵循此结构：

```yaml
step_scheduler:
  max_steps: 1000
  num_epochs: 1
  grad_accumulation_steps: 4
  val_check_interval: 100
  checkpoint_interval: 500
  log_interval: 10

dist_env:
  master_addr: localhost
  master_port: 29500

rng:
  seed: 42

model:
  _target_: nemo_automodel.NeMoAutoModelForCausalLM.from_pretrained
  pretrained_model_name_or_path: meta-llama/Llama-3.2-1B
  dtype: float32
  # 传递给构造函数的其他模型 kwargs

compile:
  enabled: false
  backend: inductor

clip_grad_norm:
  max_norm: 1.0

distributed:
  strategy: fsdp2       # fsdp2 | megatron_fsdp | ddp
  dp_size: auto
  tp_size: 1
  cp_size: 1

loss_fn:
  _target_: torch.nn.CrossEntropyLoss

dataset:
  _target_: nemo_automodel.datasets.squad.SquadDataset
  tokenizer_name_or_path: meta-llama/Llama-3.2-1B
  max_seq_length: 2048

validation_dataset:
  _target_: nemo_automodel.datasets.squad.SquadDataset
  split: validation

packed_sequence:
  enabled: false

dataloader:
  batch_size: 4
  num_workers: 4
  pin_memory: true

optimizer:
  _target_: torch.optim.AdamW
  lr: 2.0e-5
  weight_decay: 0.01

lr_scheduler:
  _target_: nemo_automodel.schedulers.CosineAnnealingWarmup
  warmup_steps: 50
  min_lr: 1.0e-6
```

### 全参数训练精度

对于使用 `torch.optim.Adam`/`AdamW` 的新全参数训练，在 `NeMoAutoModel` 加载器上显式设置 `model.dtype: float32` 以获取 fp32 主权重和 Adam 瞬态。单独配置计算精度（FSDP2：`distributed.mp_policy`）。

PEFT、TE FusedAdam 和扩散需要单独的精度选择；请参阅 [混合精度指南](../../docs/guides/mixed-precision-training.mdx)。迁移现有配置时，验证内存、训练行为和检查点/恢复。

### `_target_` 模式

`_target_` 键指定一个完全限定名的 Python 可调用对象。该部分中的所有其余键都作为关键字参数传递：

```yaml
optimizer:
  _target_: torch.optim.AdamW   # 可调用对象
  lr: 2.0e-5                    # 关键字参数
  weight_decay: 0.01            # 关键字参数
```

这相当于：`torch.optim.AdamW(lr=2e-5, weight_decay=0.01)`。

### CLI 覆盖

任何配置值都可以从命令行覆盖：

```bash
automodel config.yaml \
  --optimizer.lr 1e-4 \
  --step_scheduler.max_steps 500 \
  --distributed.tp_size 2
```

## 示例

验证和检查点：

```yaml
step_scheduler:
  val_check_interval: 100
  checkpoint_interval: 500

validation_dataset:
  _target_: nemo_automodel.datasets.squad.SquadDataset
  split: validation

restore_from:
  path: /checkpoints/step-500
```

## 特定领域注意事项

### 大语言模型 (LLM)

- `nemo_automodel/recipes/llm/train_ft.py` 处理微调和预训练。区别在于配置（数据集、学习率等）。
- `nemo_automodel/recipes/llm/kd.py` 实现知识蒸馏，具有教师模型和学生模型。
- `nemo_automodel/recipes/llm/benchmark.py` 运行吞吐量和延迟基准。

### 视觉语言模型 (VLM)

- 使用 `NeMoAutoModelForImageTextToText` 而不是因果 LM 类。
- 配置包括 `processor` 部分，而不是独立的分词器。
- 配方位于 `nemo_automodel/recipes/vlm/finetune.py`。

### 扩散模型

- 使用 `NeMoAutoDiffusionPipeline`。
- 需要在配置中包含一个 `parallel_scheme` 字典来定义并行性。
- 仅支持 DDP 和 FSDP2 策略（不支持 Megatron-FSDP）。
- 配方位于 `nemo_automodel/recipes/diffusion/train.py`。

### 检索

- 两种编码器模式：
  - **双编码器** (`nemo_automodel/recipes/retrieval/train_bi_encoder.py`)：分离查询和文档编码器，对比损失。
  - **交叉编码器** (`nemo_automodel/recipes/retrieval/train_cross_encoder.py`)：联合编码，分类头。
- 硬负采样：`nemo_automodel/recipes/retrieval/mine_hard_negatives.py`。

## 训练循环细节

每个 epoch 的训练循环结构如下：

```
for epoch in range(num_epochs):
    for batch_idx in range(batches_per_epoch):
        # --- 梯度累积内部循环 ---
        for micro_batch in micro_batches:
            if pipeline_parallel:
                schedule.step(micro_batch)    # PP 调度
            else:
                loss = model(micro_batch)     # 直接前向传播
                loss.backward()

        # --- 优化器步骤 ---
        scale_grads_and_clip_grad_norm(model, max_norm)
        optimizer.step()
        lr_scheduler.step()
        optimizer.zero_grad()

        # --- 记录 ---
        MetricsSample(step, epoch, loss, grad_norm, lr, mem, tps, mfu)

        # --- 验证（在配置的间隔处） ---
        if step % val_check_interval == 0:
            run_validation()

        # --- 检查点（在配置的间隔处） ---
        if step % checkpoint_interval == 0:
            save_checkpoint()
```

### StepScheduler

控制所有训练进度：总 epoch 数、总步骤数、梯度累积步骤数、验证间隔、检查点间隔和记录间隔。

### 梯度裁剪

通过 `scale_grads_and_clip_grad_norm()` 在反向传播后和优化器步骤前应用。由配置中的 `clip_grad_norm.max_norm` 控制。

### 上下文并行性

当 `cp_size > 1` 时，批次将跨上下文并行组使用 `make_cp_batch_and_ctx()` 分割。这必须在前向传播之前发生。

### MetricsSample

每个训练步骤生成一个 `MetricsSample`，包含以下字段：

- `step` -- 全局步骤计数
- `epoch` -- 当前 epoch
- `loss` -- 训练损失
- `grad_norm` -- 裁剪后的梯度范数
- `lr` -- 当前学习率
- `mem` -- GPU 内存使用
- `tps` -- 每秒 token 数
- `mfu` -- 模型 FLOPS 利用率

## 验证和检查点

### 验证

- 在 `step_scheduler.val_check_interval` 定义的时间间隔处运行。
- 使用从 `validation_dataset` 配置构建的验证数据加载器。
- 模型设置为评估模式；禁用梯度。

### 检查点

- 默认格式：合并的 safetensors，便于在 HF 生态系统中部署（始终优先于此而不是 DCP）。
- 检查点间隔由 `step_scheduler.checkpoint_interval` 控制。
- 通过指向检查点目录的 `restore_from` 配置键恢复训练。

```yaml
restore_from:
  path: /checkpoints/step-500
```

## 陷阱

| 问题 | 原因 | 解决方法 |
|---|---|---|
| 静默配置错误 | `_target_` 值中的拼写错误 | 类路径必须是一个有效的可导入的 Python 可调用对象。仔细检查模块路径和类名。 |
| 训练在第一步崩溃 | `global_batch_size` 不能被 `local_batch_size * dp_size * grad_accumulation_steps` 整除 | 确保所有维度上的批大小计算一致。 |
| 新配方无法通过 CLI 访问 | 配置缺少可解析的 `recipe` 目标 | 将配置的 `recipe` 键设置为可发现的配方类名或完全限定的 `_target_` 路径。 |
| 前向传播时形状不匹配 | 数据集 collate 函数输出与模型输入签名不匹配 | 验证 collate 函数是否返回模型期望的键和形状的张量。 |
| 内存不足 (OOM) 时验证 | 验证批次大小过大或未禁用梯度 | 将验证包装在 `torch.no_grad()` 中，并考虑使用较小的验证批次大小。 |
| 检查点恢复失败 | 检查点和配置之间的模型架构不匹配 | 确保模型配置与检查点完全匹配（层数、隐藏维度、词汇大小）。 |
