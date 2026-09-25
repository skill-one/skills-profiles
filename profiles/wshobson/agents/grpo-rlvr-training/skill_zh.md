# GRPO & RLVR 训练

这项技能假定 `finetuning-method-selection`
已经路由到这里，因为目标行为具有可验证的成功/失败信号——而不是演示（`lora-qlora-recipes`）或偏好对（`preference-optimization`）。以下内容是在 RL 是正确工具时，参考配方、强制奖励检查门控，以及当基础配方行为异常时如何选择 GRPO 变体的方法。

**输入：** 一个路由决策（通过 GRPO 的 RLVR）以及目标任务的验证器（代码执行器、测试套件、模式检查器或评分器）。
**输出格式：** 一个经过验证的 GRPO 配置——`references/grpo-memory.md` 中的参数值和 `references/reward-functions.md` 中的奖励函数，而不是自由形式的建议——`llm-finetuning-training-engineer`
直接消费的。

## 当 RL 适用时

GRPO+RLVR 只有在任务成功是**算法可检查**时才有效——单元测试通过、解析器接受输出、工具调用匹配预期模式、数学答案匹配真实值。如果评估输出需要人工判断或主观评分标准，那是一个评估套件和评分器校准问题——参见 `eval-harness-first`——而不是直接跳到 RL 的原因。

在启动 GRPO 运行之前，确认模型已经在目标任务上**有时**能够成功。RL 通过重新加权向已经成功的样本倾斜来增强现有能力；它不会从零开始安装能力。

- **模型即使在低温下多次采样也从未成功：** 差距在于格式或任务理解，而不是策略优化。首先路由回 SFT（`lora-qlora-recipes`），并且只有当基础成功率不为零时才返回到此技能。
- **模型有时成功，不一致：** 这是 GRPO 的理想场景——继续执行下面的配方。

整个插件的立规：**DPO 用于品味，GRPO 用于推理。** 如果信号是在两个可接受的输出之间的偏好，那是 `preference-optimization`，而不是这个技能。

## 配方

参考配方是 TRL 的 `GRPOTrainer`，支持 vLLM 生成：

```python
from trl import GRPOConfig, GRPOTrainer

grpo_args = GRPOConfig(
    output_dir="./outputs-grpo",
    use_vllm=True,
    vllm_mode="colocate",       # 单 GPU；"server" 用于多 GPU
    num_generations=8,          # 地板值——较少的样本会使相对基线饥饿
    learning_rate=5e-7,         # GRPO 的稳定范围
    beta=0.01,                  # 与参考策略的 KL 系数
    per_device_train_batch_size=8,
    gradient_accumulation_steps=4,
    bf16=True,
    logging_steps=10,
    seed=3407,
)

trainer = GRPOTrainer(
    model=SFT_CHECKPOINT,
    args=grpo_args,
    reward_funcs=[format_reward, correctness_reward],   # references/reward-functions.md
    train_dataset=prompts,       # 仅提示——GRPO 生成自己的补全
    processing_class=tokenizer,
)

trainer.train()
```

- **`vllm_mode="colocate"`** 在同一 GPU 上运行生成和训练——单 GPU 盒子的默认设置。
- **`vllm_mode="server"`** 指向单独的 vLLM 服务器进程，并且是多 GPU 路径——生成和训练不会争夺同一设备。
- **`num_generations` ≥ 8** 是地板值，而不是建议：GRPO 的优势估计是相对于组平均值，少于 8 个样本每个提示会产生噪声基线。
- **奖励是复合的**——格式奖励（输出是否解析/匹配所需结构）加上正确性奖励（答案是否验证）。结构良好但错误的答案和格式错误的答案不应得分相同；仅正确性会丢失该信号。
- **`learning_rate=5e-7`** 和 **`beta=0.01`** 是稳定的起点；只有在基础运行稳定且经过奖励检查（如下所述）后才能偏离。

此配方针对目标大小类的内存大小：`references/grpo-memory.md`。

## 检查规则

**在开始实际训练运行之前，对 50–100 个采样输出运行奖励函数并手动阅读结果。** 这是一个门控，而不是一次性的合理性检查。

如果奖励函数的判断与人工阅读的样本不一致，请首先修复奖励函数。对未经检查的奖励进行训练，或调整超参数以补偿其无声地评分错误内容，会导致运行奖励劫持：模型干净地向错误的目标优化，而这不会作为训练循环错误暴露出来。

此检查是 `/finetune` 的阶段 1 门控输入——在此处捕获损坏的奖励函数的相同 50–100 个样本阅读是该命令在允许 GRPO 简要继续之前检查的内容。

用于检查的完整奖励函数实现——精确匹配、模式验证、单元测试执行、长度惩罚包装和评分器作为奖励的模式：
`references/reward-functions.md`。

## 变体选择

上面的基础配方是默认值。只有在出现特定故障模式时才选择变体，而不是预先选择：

| 故障模式 | 变体 | 原因 |
|---|---|---|
| 熵崩溃 / 退化长思维链 | **DAPO** | 解耦剪裁边界并放宽 KL 惩罚，该惩罚过度正则化长推理轨迹上的探索 |
| 奖励或输出长度趋势上升，无论质量如何 | **Dr.GRPO** | 移除 GRPO 的长度归一化偏差，使奖励跟踪正确性，而不是完成长度 |
| 训练混合专家模型 | **GSPO** | 将重要性采样率移至序列级别，而不是每个标记——每个标记的比率在 MoE 路由上是不稳定的，因此 GSPO 在这里不是可选的，而是必需的 |

从普通的 GRPO 开始。观察特定症状——长 CoT 上的熵崩溃、长度奖励相关性或 MoE 不稳定性——然后才切换到上述匹配的变体。在基础配方实际显示故障模式之前，不要预先选择变体。

## VLM RL 仅作参考

视觉语言 RL 在 v1 版本中**不是由此插件执行的**——它在此处记录是为了背景，而不是可运行的路径。工具分散在 ms-swift 和 EasyR1 衍生的分叉中，还没有一个 TRL 命令，并且对 VLM 应用简单的文本 GRPO 倾向于通过优化文本推理轨迹而忽略图像来奖励劫持——模型学会听起来正确，而不会看输入。一个 VLM RL 运行是此技能支持配方之外的研发尖刺，而不是上述配方的变体。

## 参考

- `references/reward-functions.md` — 完整的 Python 奖励函数（精确匹配正确性、模式验证、单元测试执行、长度惩罚包装和评分器作为奖励的模式），在开始任何训练运行之前根据检查规则进行检查。
- `references/grpo-memory.md` — 目标大小类的内存大小、vLLM 睡眠模式和优化器状态策略、Unsloth 的长上下文 RL 分块，以及 DGX Spark 带宽对解码密集型滚动的注意事项。

相关技能：`finetuning-method-selection`
在存在可验证的成功/失败信号时路由到此处；`preference-optimization` 是用于偏好对而不是可验证奖励的兄弟技能；`eval-harness-first` 涵盖任何不是纯粹代码可检查的奖励的评分器校准。在 DGX Spark 上，如果安装了 `dgx-spark-ops` 插件，则委托给该插件的技能，以处理此技能的内存表未涵盖的内存/热管理缓解阶梯。
