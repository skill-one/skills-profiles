# 序列打包技能

有关稳定的背景和推荐级别，请参阅：

- @docs/training/packed-sequences.md
- @skills/nemo-mbridge-perf-sequence-packing/card.yaml

## 启用方式

离线打包的SFT用于LLM微调：

```python
import math

from megatron.bridge.data.datasets.packed_sequence import PackedSequenceSpecs

cfg.train.micro_batch_size = 1
cfg.train.global_batch_size = 8
cfg.dataset.seq_length = 8192
cfg.model.seq_length = 8192
cfg.dataset.enable_offline_packing = True

cp_size = cfg.model.context_parallel_size
tp_size = cfg.model.tensor_model_parallel_size
cp_multiple = 2 * cp_size if cp_size > 1 else 1
sp_multiple = cp_size * tp_size if cfg.model.sequence_parallel and tp_size > 1 else 1
cfg.dataset.offline_packing_specs = PackedSequenceSpecs(
    packed_sequence_size=8192,
    pad_seq_to_mult=math.lcm(cp_multiple, sp_multiple),
)
```

### 选择离线打包长度

对于纯文本LLM SFT和PEFT验证，当模型上下文限制、内存和模型系列支持时，从8192个token的离线打包开始。
在优化器每步的等token槽位下基准测试打包长度：

```text
token_slots_per_step = packed_sequence_size * global_batch_size
```

例如，2K/GBS32、4K/GBS16和8K/GBS8每个都提供每步65,536个token槽位。更长的打包会聚合更多源示例到每个物理MBS1行中，并可以减少梯度累积和每步开销。它们还会增加激活内存，并可能暴露内核宽度限制，因此选择最适合的配置而不是假设更长就一定更快。

离线打包需要MBS1。需要`global_batch_size % data_parallel_size == 0`和`global_batch_size >= data_parallel_size`；因此8K/GBS8工作负载需要的DP不能大于8。保持`model.seq_length`、`dataset.seq_length`和`packed_sequence_size`相等，更改其中任何一个后使用新的打包数据输出根，并检查解析后的配置。

等token槽位不会使不同打包长度的数值相同：更长的目标会改变截断和打包成员资格。在替换验证证据之前重新运行有限损失、无跳过/NaN和收敛哨兵。

对于启用CP的微调：

```python
cfg.model.context_parallel_size = 2
cfg.model.calculate_per_token_loss = True
cfg.ddp.average_in_collective = False
```

使用相同的对齐公式用于SFT和PEFT。它为禁用SP的TP1/CP1产生1，为启用SP的TP4/CP1产生4。离线打包不会自动派生该值，因此需要显式固定并在拓扑更改后重新构建打包数据。

如果调度器或内核需要固定的最终token宽度：

```python
cfg.dataset.dataset_kwargs = {
    **(cfg.dataset.dataset_kwargs or {}),
    "pad_to_max_length": True,
}
```

选择`packed_sequence_size`以满足内核倍数。例如，需要128个token组合块的HybridEP需要宽度可被128整除。这与`pad_seq_to_mult`不同，后者用于对齐CP/SP的每个组成序列。

如果为这个打包路径启用了CUDA图，则需要固定token宽度，并且打包元数据也必须具有静态形状：

```python
cfg.dataset.offline_packing_specs.pad_cu_seqlens = True
cfg.dataset.dataset_kwargs["pad_to_max_length"] = True
```

**注意：** `pad_cu_seqlens = True`还要求打包数据集旁边有一个元数据JSON文件（在`src/megatron/bridge/data/datasets/sft.py`中断言）。省略元数据文件的定制打包数据集在数据集初始化时将触发断言。

批内打包用于GPT SFT和支持的VLM微调：

```python
cfg.dataset.enable_in_batch_packing = True
cfg.dataset.dataloader_type = "single"
cfg.train.micro_batch_size = 4
```

对于本地或物化的GPT-SFT JSONL，这会保留现有的mmap后端数据集并延迟执行分词。提示/补全(`GPTSFTDataset`)和聊天(`GPTSFTChatDataset`)都保留其损失掩码语义。使用`dataloader_type="single"`或`"cyclic"`，以便每个DataLoader yield是一个逻辑微批次；GPT-SFT批内打包不支持全局批次的`"batch"`数据加载器。

Energon在线打包用于Qwen-VL，它使用Energon的每个工作者的候选缓冲区，而不是将选择限制为一个组合器微批次：

```python
cfg.dataset.packing_buffer_size = 16
cfg.dataset.micro_batch_size = 1
cfg.train.micro_batch_size = 1
cfg.model.calculate_per_token_loss = True
cfg.ddp.average_in_collective = False
```

`packing_buffer_size`是唯一的原生打包选择器；将遗留的组合器和步骤拥有的打包标志保留为默认值。使用`vlm_step`。缓冲区大小计算每个工作者的准备候选样本数，而不是字节或打包token。由于准备好的图像/视频补丁张量会保留在主机内存中直到选择，因此对于高分辨率或视频数据从8-16开始，并在增加之前测量工作者RSS、第一批次延迟和桶填充。

此路径不会写入离线打包；源WebDataset分片保持不变。它支持MBS1的eager Qwen-VL，拒绝MTP、CUDA图、Qwen3-VL DistTrain和PP。请求的MoE专家并行通信重叠被警告禁用。标准eager `alltoall` EP在禁用重叠的情况下，在TP1/PP1/EP8下对Qwen3.6-35B-A3B具有功能覆盖；这不是性能证据。其他EP调度器接受固定宽度的原生打包，但目前还没有等效的运行时证据。Qwen-VL模型从逻辑和物理THD边界派生MoE填充掩码，因此固定宽度间隙不会进入辅助损失、z损失或专家偏差统计。当前MCore可能仍然调度填充位置；专家容量/token丢弃配置缺乏原生打包运行时覆盖。

长上下文基线：

```python
cfg.model.seq_length = 16384
cfg.dataset.seq_length = 16384
cfg.model.context_parallel_size = 2
```

## 代码锚点

LLM打包SFT配置表面：

```128:143:src/megatron/bridge/recipes/utils/dataset_utils.py
dataset_kwargs = {}
offline_packing_specs = None
if enable_offline_packing:
    dataset_kwargs["pad_to_max_length"] = True
    offline_packing_specs = PackedSequenceSpecs(packed_sequence_size=seq_length, pad_seq_to_mult=pad_seq_to_mult)

return _text_hf_dataset_config(
    source=HFDatasetSourceConfig(dataset_name="squad"),
    preprocessing=PromptCompletionSFTPreprocessingConfig(separator=" "),
    seq_length=seq_length,
    enable_offline_packing=enable_offline_packing,
    offline_packing_specs=offline_packing_specs,
    dataset_kwargs=dataset_kwargs,
    val_proportion=0.1,
    num_workers=1,
)
```

共享文本数据集辅助工具目前选择固定宽度打包。将其视为辅助工具默认值，而不是通用的离线打包运行时要求；当选择的调度器、内核或CUDA图路径需要静态宽度时保留它。

桥接验证：

```1220:1248:src/megatron/bridge/training/config.py
enable_in_batch_packing = getattr(self.dataset, "enable_in_batch_packing", False)
enable_offline_packing = getattr(self.dataset, "enable_offline_packing", False)
offline_packing_specs = getattr(self.dataset, "offline_packing_specs", None)

if enable_offline_packing and enable_in_batch_packing:
    raise ValueError("enable_offline_packing and enable_in_batch_packing are mutually exclusive.")
if enable_offline_packing and offline_packing_specs is None:
    raise ValueError("offline_packing_specs must be set when enable_offline_packing=True.")
...
if enable_in_batch_packing:
    ...
    cp_multiple = 2 * cp_size if cp_size > 1 else 1
    sp_multiple = cp_size * tp_size if has_sp and tp_size > 1 else 1
    self.dataset.in_batch_packing_pad_to_multiple_of = math.lcm(cp_multiple, sp_multiple)
```

```1400:1442:src/megatron/bridge/training/config.py
if self.model.context_parallel_size > 1:
    assert self.model.seq_length % (self.model.context_parallel_size * 2) == 0, ...
    if isinstance(self.dataset, FinetuningDatasetConfig):
        assert self.model.calculate_per_token_loss, ...
        assert not self.ddp.average_in_collective, ...
...
if enable_offline_packing and self.train.micro_batch_size > 1:
    raise ValueError(...)
...
if enable_in_batch_packing and self.train.micro_batch_size == 1:
    raise ValueError(...)
```

VLM提供者在批组合时使用的运行时：

```397:449:src/megatron/bridge/data/sequence_batching.py
def prepare_padded_or_packed_sequence_batch(
    batch,
    *,
    sequence_length,
    ...
    enable_in_batch_packing=False,
    in_batch_packing_pad_to_multiple_of=1,
    ...
):
    ...
    if enable_in_batch_packing:
        pack_right_padded_sequence_batch_to_mcore_thd(
            batch,
            sequence_length=sequence_length,
            pad_to_multiple_of=in_batch_packing_pad_to_multiple_of,
            ...
        )
        return
```

GPT-SFT直接行打包：

```627:671:src/megatron/bridge/data/datasets/gpt_sft.py
def _collate_in_batch(self, batch):
    ...
    return build_mcore_thd_sequence_batch_from_rows(...)
```

打包THD运行时约束：

```94:108:src/megatron/bridge/training/gpt_step.py
if batch.get("cu_seqlens_q") is not None:
    cu_seqlens = batch.get("cu_seqlens_q_padded")
    if cu_seqlens is None:
        cu_seqlens = batch["cu_seqlens_q"]
    if cu_seqlens.dim() > 1 and cu_seqlens.size(0) != 1:
        raise ValueError("Packed THD batches expect micro-batch size 1 for context-parallel slicing (THD layout)")
    return cu_seqlens.squeeze()

cu_seqlens = batch["cu_seqlens"]
if cu_seqlens.dim() > 1 and cu_seqlens.size(0) != 1:
    raise ValueError("Packed THD batches expect micro-batch size 1 for context-parallel slicing (THD layout)")
```

## 陷阱

1. 离线打包SFT、运行时批内打包和Energon在线打包是不同的功能。离线和Energon打包使用物理MBS1；运行时批内打包使用大于一的MBS。
2. GPT-SFT批内打包需要`dataloader_type="single"`或`"cyclic"`；它不支持`"batch"`。
3. 当CP启用时，打包序列长度必须尊重`2 * context_parallel_size`的整除性。
4. 对于CP微调，需要`calculate_per_token_loss=True`和`ddp.average_in_collective=False`。
5. `pad_cu_seqlens=True`也需要`pad_to_max_length=True`。
6. 打包支持是模型系列特定的。`Qwen3-Next`、`GLM-4.5`和`Qwen3.5-VL`在不同路径中包含明确的排除选项。
7. MTP微调文档记录为与打包序列不兼容。
8. 合成填充行，包括通过`samples_mapping`重新映射的负索引，必须保留全零损失掩码。
9. `global_batch_size`必须可被数据并行大小整除且不小于数据并行大小，当离线打包使用MBS1时。
10. 从CP/TP/SP为SFT和PEFT派生`pad_seq_to_mult`；不要按工作负载类型硬编码不同的值。
11. `pad_to_max_length`控制最终打包宽度，并且取决于固定形状执行要求。
12. Energon `packing_buffer_size`是按工作者的，并且也会影响验证；全局/评估批次计数指的是物理打包而不是源对话。
13. 精确Energon加载器恢复需要未更改的分片/分割、DP世界大小、工作者计数、洗牌设置/种子、处理器、序列长度、拓扑和打包缓冲区大小。

## 验证

使用检查入的单元覆盖率：

```bash
uv run python -m pytest tests/unit_tests/training/utils/test_packed_seq_utils.py -v && \
uv run python -m pytest tests/unit_tests/training/test_config.py -k "packed_sequence or enable_in_batch_packing or offline_and_in_batch_packing_are_mutually_exclusive or context_parallel_seq_length_divisibility or context_parallel_finetuning_validations" -v && \
uv run python -m pytest tests/unit_tests/data/packing/test_in_batch.py -v && \
uv run python -m pytest tests/unit_tests/data/datasets/test_gpt_sft.py -k "in_batch_packing" -v && \
uv run python -m pytest tests/unit_tests/data/builders/test_gpt_sft_config.py -v && \
uv run python -m pytest tests/unit_tests/training/test_vlm_step.py -k "deferred_in_batch_packing or packed_metadata" -v && \
uv run python -m pytest tests/unit_tests/models/qwen_vl/data/test_energon.py tests/unit_tests/data/builders/test_energon_builder.py -v && \
uv run python -m pytest tests/unit_tests/tutorials/test_multimodal_data_tutorials.py -k "native_packing_loader" -v && \
uv run python -m pytest tests/unit_tests/data/datasets/test_packed_parquet.py -k "negative_index_zeroes_loss_mask" -v && \
uv run python -m pytest tests/unit_tests/data/datasets/test_sft.py -k "mapped_padding_rows_do_not_contribute_to_loss" -v
```

成功标准：

- 所有选中的测试通过
- 离线和批内配置验证保持互斥
- 打包元数据以MCore THD形式到达训练步骤
- GPT-SFT批内打包拒绝全局批次的`"batch"`数据加载器
- 原生Energon打包精确恢复挂起的组并刷新有限的临时缓冲区而不丢弃样本
- 映射的填充行不会导致损失
