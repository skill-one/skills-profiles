# 训练 sentence-transformers 模型

**这个 SKILL.md 是一个路由器，而不是手册。** 它告诉你要为你的任务加载哪些参考和示例脚本。实际内容（推荐的损失函数、评估器、训练脚本结构、模型选择、训练参数调整、故障排除）都存在于 `references/` 和 `scripts/` 目录中。

**不要仅凭这个文件来编写训练脚本。** 打开每类生产模板 (`scripts/train_<type>_example.py`) 并将其复制作为你的起点。模板包含承重脚手架（自动批处理辅助函数、模型卡类、日志静默列表、`force=True`、`seed`、TF32、版本兼容的导入、命名评估器指标处理）这些是先前代理运行时在从合成片段中自行构建时反复遗漏的。

## 1. 确定模型类型

| 标签 | 类 | 功能 | 选择时机 |
|---|---|---|---|
| **[SentenceTransformer]** | `SentenceTransformer` (双编码器) | 将每个输入映射到一个固定维度的密集向量 | 检索、相似度、聚类、分类、释义挖掘、去重 |
| **[CrossEncoder]** | `CrossEncoder` (重排序器) | 联合评分 `(查询, 文章)` 对 | 两阶段检索（从双编码器重排序前100个）、对分类 |
| **[SparseEncoder]** | `SparseEncoder` (SPLADE) | 词汇表的稀疏向量 | 学习稀疏检索、倒排索引后端（Elasticsearch / OpenSearch / Lucene） |
| **[MultiVectorEncoder]** | `MultiVectorEncoder` (ColBERT) | 每个标记一个嵌入，使用 MaxSim 评分 | 晚交互检索、比双编码器更高的存储成本下的召回率提升、多模态（ColPali / ColQwen2） |

当请求不明确时的破局规则："嵌入模型" / "向量检索" / "相似度" → **[SentenceTransformer]**。"重排序" / "排序器" / "两阶段" → **[CrossEncoder]**。"SPLADE" / "稀疏" / "倒排索引" → **[SparseEncoder]**。"ColBERT" / "晚交互" / "多向量" / "MaxSim" / "ColPali" / "ColQwen" → **[MultiVectorEncoder]**。如果仍然不清楚，请询问。

## 2. 必须阅读的内容

**在编写任何代码之前完整阅读这些内容。不要根据感知的相关性进行筛选。**

### 每类：始终需要

**[SentenceTransformer]**
- `references/losses_sentence_transformer.md`：损失函数与数据形状的映射、MNRL系列对 `BatchSamplers.NO_DUPLICATES` 的要求、`Cached*` ↔ `gradient_checkpointing` 的不兼容性。
- `references/evaluators_sentence_transformer.md`：评估器与任务的映射、`metric_for_best_model` 键的构建（命名 vs 未命名）、每个评估器的 `primary_metric` 值。
- `references/model_architectures.md`：编码器 vs 解码器 vs 静态 vs Router 管道、池化规则（均值 / cls / 最后一个标记）、对于从头开始 MLM 基的自动均值池化行为。
- `scripts/train_sentence_transformer_example.py`：生产模板。复制这个作为你的起点。

**[CrossEncoder]**
- `references/losses_cross_encoder.md`：点式 / 对式 / 列式 / 蒸馏，`pos_weight` 推导、`activation_fn=Identity()` 对非 BCE 损失是强制的（否则会导致静默的评估-排名崩溃）。
- `references/evaluators_cross_encoder.md`：`CrossEncoderRerankingEvaluator` 配方、命名评估器键格式 `eval_{name}_{primary_metric}`。
- `scripts/train_cross_encoder_example.py`：生产模板。复制这个作为你的起点。

**[SparseEncoder]**
- `references/losses_sparse_encoder.md`：`SpladeLoss` 包装器要求、FLOPS 正则化权重、烟雾测试的活跃维度斜坡行为。
- `references/evaluators_sparse_encoder.md`：`SparseNanoBEIREvaluator`（仅英语）和领域内替代方案、`eval_{name}_{primary_metric}` 键格式。
- `scripts/train_sparse_encoder_example.py`：生产模板。复制这个作为你的起点。

**[MultiVectorEncoder]**
- `references/losses_multi_vector_encoder.md`：MaxSim 评分、每个评分模式下的缩放选择（`scale=1.0` for MaxSim，大致是 MeanMaxSim 的平均查询长度）、MNRL / CachedMNRL / MarginMSE / DistillKLDiv、XTR-vs-ColBERT 评分、CachedMNRL ↔ `gradient_checkpointing` 的不兼容性。
- `references/evaluators_multi_vector_encoder.md`：`MultiVectorNanoBEIREvaluator`（仅英语）和领域内替代方案、`eval_NanoBEIR_mean_maxsim_ndcg@10` 键格式、蒸馏评估的 spearman 变体。
- `scripts/train_multi_vector_encoder_example.py`：生产模板。复制这个作为你的起点。

### 跨任务：始终需要（无论任务类型）

- `references/training_args.md`：`TrainingArguments` 调整、精度规则（加载 fp32 + autocast bf16/fp16，永远不要 `torch_dtype=bfloat16`）、`warmup_steps`（浮点数）vs 已弃用的 `warmup_ratio`、`save_steps` 必须是 `eval_steps` 的倍数以用于 `load_best_model_at_end`、调度器、HPO、追踪器、恢复、hub-push 变体。
- `references/dataset_formats.md`：列匹配规则（标签名自动检测、列顺序不名称）、重塑配方、硬负样本挖掘选项。
- `references/base_model_selection.md`：发现命令、每类模型的命名空间、ModernBERT系列 `max_seq_length=8192` 陷阱、`datasets >= 4` 脚本加载拒绝、非英语起点的快捷方式。
- `references/troubleshooting.md`：按症状索引的故障排除配方。每次运行时浏览每个部分的标题，即使是健康的运行。 "指标没有改进" 和 "Hub push 失败" 条目涵盖了频繁出现的错误，在它们触发之前识别它们比之后调试更便宜。

### 跨任务：适用时加载

- `references/hardware_guide.md`：VRAM 尺寸、多 GPU、FSDP / DeepSpeed、HF Jobs 风味。对于 >24GB 模型、多 GPU 或 HF Jobs 运行时需要。
- `references/hf_jobs_execution.md`：在 HF Jobs 上运行时需要。
- `references/prompts_and_instructions.md`：使用提示微调的基（E5、BGE、GTE、Qwen3-Embedding、Instructor、Nomic 等）或添加 `query: ` / `passage: ` 风格前缀时需要。

### 变体脚本（当任务匹配时打开）
- **[SentenceTransformer]** `scripts/train_sentence_transformer_<matryoshka|multi_dataset|with_lora|distillation|make_multilingual|static_embedding>_example.py`。
- **[CrossEncoder]** `scripts/train_cross_encoder_<distillation|listwise>_example.py`。
- **[SparseEncoder]** `scripts/train_sparse_encoder_distillation_example.py`。
- 硬负样本挖掘 CLI：`scripts/mine_hard_negatives.py`。

## 3. 默认值

仅当用户指定其他内容时才覆盖：
- **本地执行。** 只有当本地硬件无法容纳工作负载时才提议 HF Jobs。
- **单次运行。** 完成后，如果用户受益，建议进行实验（弱/边际判断、"看看你能推多高"的框架等）。迭代规则在 `references/training_args.md`（实验部分）。
- **运行结束时在公共 Hub 推送，用 try-except 包裹。** 在 HF Jobs（临时环境）上也启用训练器内推送 (`push_to_hub=True` + `hub_strategy="every_save"`）。详情在 `references/hf_jobs_execution.md`。

## 4. 生成脚本必须满足的约束

这些是不可协商的合同。实现存在于生产模板和参考中。不要重新发明。

- 在 `trainer.train()` **之前**捕获预训练评估器分数作为 `baseline_eval`。
- 发出一个运行结束行：`VERDICT: WIN|MARGINAL|REGRESSION | score=... | baseline=... | delta=...`。一个监视器会抓取这个。
- 静默 `httpx`、`httpcore`、`huggingface_hub`、`urllib3`、`filelock`、`fsspec` 为 WARNING（否则 HF 下载 URL 会淹没代理的上下文）。
- 将日志输出到 `logs/{RUN_NAME}.log`。
- 以 `try/except` 包裹 `model.push_to_hub(...)`。
- 在任何长运行之前进行烟雾测试 (`max_steps=1` + 微型数据集切片)。生产模板显示了一个常见模式 (`SMOKE_TEST` 环境变量)。
- **[CrossEncoder]** 包含 `EarlyStoppingCallback(patience>=3)`。CE 重排序器通常在训练中期达到峰值并回归。
- **[SparseEncoder]** 在判断行上记录 `query_active_dims` / `corpus_active_dims`。高 nDCG 与折叠稀疏性不是胜利。键以名称前缀返回（例如 `..._query_active_dims`）。使用后缀匹配来提取它们。查看 SPARSE 生产模板以获取确切模式。
- **[MultiVectorEncoder]** 将 `scale` 与任何 MNRL 系列损失的评分模式匹配：接近 `1.0` 用于未归一化的 MaxSim（不要从双编码器 MNRL 复制 `scale=20.0`），大致是长度归一化的 MeanMaxSim 的平均查询长度，因为每个分数都除以其查询的标记数。`XTRScores` 是一个仅用于训练的 `similarity_fct`：评估器会拒绝它，因此评估始终使用 MaxSim，包括对于 XTR 训练的模型。

## 5. 工作流程

1. 确定模型类型（§1）。如果模糊，请询问。
2. 加载该类型的 §2 必须阅读的文件。
3. 打开 `scripts/train_<type>_example.py` 并将其复制作为你的起点。
4. 替换 `MODEL_NAME`、`DATASET_NAME`、`RUN_NAME`、损失函数和评估器以匹配用户的任务。交叉检查损失/数据形状匹配与 `references/losses_<type>.md`。交叉检查 `metric_for_best_model` 键与 `references/evaluators_<type>.md`（命名评估器将键格式化为 `eval_{name}_{primary_metric}`）。
5. 烟雾测试 (`max_steps=1`)。
6. 运行。
7. 运行结束后，将内容追加到 `logs/experiments.md`，如果判断是弱/边际，请建议迭代。

## 先决条件

```bash
pip install "sentence-transformers[train]>=5.0"        # 添加 [train,image] / [audio] / [video] for [SentenceTransformer] 多模态
                                                       # [MultiVectorEncoder] 需要 >=6.0
pip install trackio                                    # 可选追踪器（或 wandb / tensorboard / mlflow）
hf auth login                                          # 或设置 HF_TOKEN 带写权限（用于 Hub push）
```

强烈推荐 GPU。CPU 仅适用于演示和 `[SentenceTransformer]` `StaticEmbedding`。
