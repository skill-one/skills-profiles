# LoRA & QLoRA配方

这项技能假设路由决策已经完成——`finetuning-method-selection`应该已经指向这里，因为数据形状是演示（SFT），而不是偏好对或可验证的奖励信号。以下是目前最佳实践配方，用于配置适配器本身：要针对哪些模块、如何调整秩和alpha的大小、使用什么学习率，以及何时QLoRA获得真正的空间，何时它只是增加风险。数据集准备和质量检查是另一个问题——请参阅`dataset-curation`。

**输入：**一个路由决策（通过LoRA/QLoRA的SFT）加上目标大小类别。
**输出格式：**一个经过验证的适配器配置——下面的关键字参数值，而不是自由形式的建议——当`llm-finetuning-training-engineer`生成可运行脚本时直接使用。

## 参考配方

参考配方是“无后悔的LoRA”（Thinking Machines/Schulman，2025-09），现已成为LoRA/QLoRA SFT的既定规范。

### 目标模块

针对所有线性模块，而不仅仅是注意力：

```python
target_modules = [
    "q_proj", "k_proj", "v_proj", "o_proj",   # 注意力
    "gate_proj", "up_proj", "down_proj",      # MLP——最重要
]
```

MLP层（`gate_proj`，`up_proj`，`down_proj`）最重要——仅针对注意力是旧的、较弱的传统。为了节省内存而删除模块是下面的故障模式，而不是有效的优化。

### Alpha和学习率

- **`lora_alpha = 2 * r`**是既定的规范（NeurIPS 2025“入侵维度”结果）。不要独立于秩微调alpha——每次都从秩中导出它。
- **LoRA学习率约为等效全微调LR的10倍。** 对于QLoRA特别地，**2e-4**是标准的起点。完整的超参数表和示例配置：`references/hyperparameters.md`。

### 按任务确定秩

秩是任务形状的，而不是单一的全局默认值：

| 任务 | 秩 |
|---|---|
| RL（GRPO/RLVR适配器） | 1-32 |
| 一般默认 | 16-32 |
| 大规模SFT | 最高约256 |

更高的秩并不总是更好——它提高记忆能力与提高泛化能力一样快。从与任务匹配的行开始，只有在较低秩在保留评估上明显欠拟合时才向上移动一行，而不是作为默认的保险。

### 有效批处理大小

保持**有效批处理大小小于32**。这个配方在该规模下经过验证——提高有效批处理大小是未经测试的外推，而不是免费的吞吐量优势。

## Unsloth默认值

Unsloth是此插件假设的默认快速路径的参考实现——除了消息形状的对话SFT与`assistant_only_loss=True`，其中Unsloth 2026.7.x的编译训练器根本没有消息形状的路径，并且普通的TRL逃生通道（`references/unsloth-trl-mapping.md`）是这种组合的默认值，而不是罕见回归的备用方案。它的开箱即用默认值，以及每个值设置的原因：

- **`lora_dropout=0`**——优化内核路径假设零dropout；设置非零值会放弃融合内核的速度提升。
- **`bias="none"`**——偏差项为适配器参数添加了可忽略的质量提升，在当前秩范围内。
- **`use_gradient_checkpointing="unsloth"`**——Unsloth的检查点变体，而不是vanilla HF检查点；比不检查点节省大约**30% VRAM**。
- **`optim="adamw_8bit"`**——8位AdamW减少了优化器状态内存，在LoRA/QLoRA适配器规模下对质量的影响可忽略不计。
- **`random_state`**固定——固定LoRA初始化以跨运行重现；将其视为任何其他种子，而不是可调的。

这些在`get_peft_model`调用中一起出现：

```python
model = FastLanguageModel.get_peft_model(
    model,
    r=32,
    target_modules=target_modules,
    lora_alpha=64,               # 2 * r
    lora_dropout=0,
    bias="none",
    use_gradient_checkpointing="unsloth",
    random_state=3407,
)
```

确切的关键字参数名称及其普通的TRL/PEFT等价物，以及一个包含`SFTConfig`的完整工作配置：`references/unsloth-trl-mapping.md`和`references/hyperparameters.md`。

## LoRA与QLoRA与全微调

| 情况 | 默认选择 |
|---|---|
| 根据演示调整行为 | LoRA |
| 基础模型在目标秩下无法放入bf16 | QLoRA |
| 注入密集的新领域知识 | 全微调（参见`finetuning-method-selection`） |
| 不确定哪一个 | LoRA——只有在内存迫使的情况下才升级到QLoRA |

- **QLoRA** = NF4量化的冻结基础权重 + BF16适配器。这是使65B类模型在48GB上可训练的东西——量化的基础是内存优势，而不是适配器本身。
- **全微调不是默认的。** 保留它用于注入密集知识，目标是改变模型在权重级别知道的内容，而不是调整行为。对于此技能范围内的一切，LoRA或QLoRA是起始假设。
- **在DGX Spark上，QLoRA可能在等效bf16 LoRA运行之前OOM**，即使QLoRA的稳态占用空间更小——bitsandbytes去量化缓冲区是瞬态的CUDA端分配，在加载期间会激增。QLoRA的OOM不是模型不合适的证明；`dgx-spark-ops`插件的`spark-memory-thermal-ops`技能涵盖了完整的OOM补救措施阶梯（bf16 LoRA是下一步要尝试的，而不是进一步的QLoRA缩小）。

## 故障模式

- **非BF16 GPU上的fp16发散。** 在没有可靠BF16支持的硬件上以fp16进行训练是已知的损失尖峰和静默发散的来源。强制`bf16=True`在硬件支持的地方；不要退回到fp16，好像它们是等效的。在选择数据类型之前检查硬件支持：

  ```bash
  python -c "import torch; print(torch.cuda.is_bf16_supported())"
  ```

- **在小数据集上秩太高导致过拟合。** 为“大规模SFT”（高达~256）选择的秩在数据集没有规模支持的情况下会记忆而不是泛化。根据上表中的秩任务匹配，而不是可用的最大数字。
- **为了节省内存而删除目标模块会以可忽略的节省为代价牺牲质量。** `gate_proj`/`up_proj`/`down_proj`上的适配器参数占总模型大小的一小部分——切割它们几乎不移动内存，但明显降低了质量。如果内存紧张，请先升级到QLoRA或减少秩/批处理/打包长度，然后再修剪目标模块。

这三个故障模式有一个共同的模式：它们看起来像训练循环错误（损失尖峰、平台期、记忆化），但实际上是与上述参考配方相矛盾的配置选择。在调试训练循环本身之前，请检查配置与此技能。

## 参考文献

- `references/hyperparameters.md`——按任务类型完整秩/alpha/LR表、rsLoRA笔记、批处理/打包交互，以及完整的Unsloth配置块。
- `references/unsloth-trl-mapping.md`——每个Unsloth关键字参数映射到其TRL/PEFT等价物、当前TRL API笔记，以及在何时退回到普通TRL的逃生通道规则。

相关技能：`finetuning-method-selection`路由到此处；`dataset-curation`涵盖了此技能不涉及的方面；`llm-finetuning-training-engineer`是此技能生成的配置的下游消费者。
