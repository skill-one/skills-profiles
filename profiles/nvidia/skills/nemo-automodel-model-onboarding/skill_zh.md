# 向 NeMo AutoModel 添加模型支持

## 目的

本指南指导在 NeMo AutoModel 中实现新的模型架构。请按顺序遵循五个阶段。
<!-- NVSkills 签名刷新请求（PR #2998，2026-07-31）。 -->

## 说明

在回答入职问题时，请按以下顺序提供响应：

1. 根据 `config.json` 对架构进行分类。
2. 指出 `components/models/<name>/` 下确切的实现文件。
3. 确定注册表和可选的自定义配置更新。
4. 说明在使用完整检查点之前必须添加的验证测试。

对于概念性入职问题，请从本指南中回答，除非用户要求您编辑代码。提及模式文件名作为参考，然后给出直接清单。

使用直接动作动词：分类模型、命名文件、映射权重、注册类和添加测试。不要讨论分布式策略、启动器配置或通用配方编写，除非用户明确将其与入职新架构相关联。

## 示例

对于常见问题，使用这些紧凑的响应模式：

- 密集因果 LM：当 `architectures` 包含 `ForCausalLM` 类且专家字段（如 `num_local_experts`、`n_routed_experts` 或 `num_experts_per_tok`）不存在时，仅当其为密集时进行分类。创建 `components/models/<name>/model.py` 和 `__init__.py`；仅在需要检查点权重转换时添加 `state_dict_adapter.py`，仅在需要时添加 `config.py`。在 `_transformers/registry.py` 中注册 `MODEL_ARCH_MAPPING`，添加示例 YAML，并添加微型配置单元测试以及重写层的层等价性测试。
- MoE 检查点：在 `config.json` 中识别专家字段，参考 `moe-patterns.md`，单独映射路由器张量，保留路由专家索引顺序，映射路由专家、共享专家和门/上/下投影，添加适配器键映射测试和微型配置数值等价性测试，并且不要仅依赖 `from_pretrained()` 或静默张量重塑。
- VLM 入职：当 `architectures` 包含 `ForConditionalGeneration` 且存在 `vision_config` + `text_config` 时，仅当其为 VLM 时进行分类。参考 `vlm-patterns.md` 和现有的 VLM 实现如 `mistral4`、`kimivl` 或 `kimi_k25_vl`；检查文本主干、视觉塔、投影器和处理器假设，文本和视觉检查点兼容性（在需要时使用适配器映射），注册表注册，以及微型图像-文本测试，然后再使用完整检查点。不要将 VLM 入职视为纯因果 LM 路径或跳过处理器/图像测试。

对于 MoE 检查点和 VLM 问题，应用第 2.4 节和 2.5 节中的清单。

## 路由边界

仅当用户正在添加或修改模型架构支持时（模型文件、自定义层、状态字典适配器、Hugging Face 配置映射、注册表条目或模型能力标志）才使用此技能。

不要使用此技能来回答关于优化器、数据集、调度器、验证数据集或训练器连接的独立训练配方 YAML 问题，除非它们是入职新模型架构的一部分。这些问题属于 nemo-automodel-recipe-development 技能。

适用示例：

- "添加对新 Hugging Face 因果 LM 架构的支持。"
- "从 Hugging Face 检查点映射 MoE 路由器和专家权重。"
- "在 NeMo AutoModel 中注册新的模型类。"

不适用示例：

- "编写具有优化器和数据集部分的微调配方 YAML。"
- "选择 FSDP2、DDP、张量并行或上下文并行设置。"
- "配置 Slurm、SkyPilot、容器、挂载或启动调度。"

## 第 1 阶段：发现

在编写代码之前，收集有关目标模型的信息。

### 1.1 获取 HuggingFace config.json

从 HuggingFace Hub 下载模型的 `config.json`（或使用 `AutoConfig.from_pretrained`）。提取的关键字段：

- `architectures` -- 确定类名和注册键（例如，`"LlamaForCausalLM"`、`"Qwen3MoeForCausalLM"`、`"Mistral3ForConditionalGeneration"`）
- `model_type` -- 如果 HF 没有内置配置类，则用于在 `_CUSTOM_CONFIG_REGISTRATIONS` 中进行自定义配置注册
- `hidden_size`、`intermediate_size`、`num_hidden_layers`、`num_attention_heads`、`num_key_value_heads` -- 尺寸
- `vocab_size` -- 对于微型测试配置需要
- `tie_word_embeddings` -- 每个支持的检查点中保存的设置；不要从裸配置构造器推断它
- `hidden_act` -- 激活函数（例如，`"silu"` 对于 SwiGLU）

### 1.2 确定模型类型

| 类型 | 指示器 | 模式文件 |
|------|-----------|-------------|
| **密集 LLM** | `ForCausalLM` 在 architectures 中，没有专家字段 | [llm-patterns.md](./llm-patterns.md) |
| **MoE LLM** | `n_routed_experts`、`num_local_experts`、`num_experts_per_tok` 在 config 中 | [moe-patterns.md](./moe-patterns.md) |
| **VLM** | `ForConditionalGeneration` 在 architectures 中，具有 `vision_config` + `text_config` | [vlm-patterns.md](./vlm-patterns.md) |

### 1.3 检查现有类似架构

在 `components/models/` 中查找具有类似注意力或 MLP 模式的架构：

```
components/models/
  llama/           # 标准 GQA + SwiGLU，具有单独的 HF 兼容投影
  qwen2/           # 与 Llama 相同，但具有注意力偏差 + QKV 偏差
  baichuan/        # ALiBi 注意力变体
  deepseek_v3/     # MLA 注意力 + MoE（DeepSeek 风格的分组专家）
  mistral4/        # MLA + MoE + VLM（Pixtral 视觉）
  kimivl/          # DeepSeek-V3 主干 + MoonVit 视觉
  kimi_k25_vl/     # 更新后的 KimiVL，具有不同的投影器
  qwen3_moe/       # Qwen3 具有 MoE 层
  nemotron_v3/     # 混合 mamba-注意力
```

### 1.4 确定自定义组件

检查模型是否需要：

- **自定义注意力**：GQA（标准）、MLA（DeepSeek/Mistral4）、滑动窗口、双向
- **自定义 RoPE**：标准（Llama）、YaRN 缩放、NTK-aware、复数（DeepSeek）
- **自定义归一化**：RMSNorm（标准）、LayerNorm、不同的 eps 值
- **自定义 MLP**：SwiGLU（标准）、GeGLU、ReLU-squared、MoE 路由
- **自定义配置类**：仅当 HF `AutoConfig` 无法解析模型的 `config.json` 时需要（检查 `auto_map` 字段）

### 1.5 记录测试配置的维度

对于单元测试，创建一个微型配置。目标：参数量小于 1M。

```python
# 示例 Llama-like 模型的微型配置：
tiny_config = LlamaConfig(
    hidden_size=64,
    intermediate_size=128,
    num_hidden_layers=2,
    num_attention_heads=4,
    num_key_value_heads=2,
    vocab_size=256,
    max_position_embeddings=128,
)
```

---

## 第 2 阶段：实现

### 2.1 创建目录结构

```
components/models/<name>/
  __init__.py
  model.py
  state_dict_adapter.py # 仅当 HF 权重名称或张量布局需要转换时
  config.py            # 仅当 HF 配置不足时
  layers.py            # 仅用于 MoE / MLA / 其他非标准层
  rope_utils.py        # 仅用于自定义 RoPE
```

### 2.2 实现顺序

按依赖顺序实现文件：

1. **config.py**（如果需要）-- 自定义 `PretrainedConfig` 子类
2. **rope_utils.py**（如果需要）-- RoPE 实现
3. **layers.py**（如果需要）-- 注意力、MLP、解码器块类
4. **model.py** -- 主 `ForCausalLM`（或 `ForConditionalGeneration`）类
5. **state_dict_adapter.py**（如果需要）-- HF 权重转换。将检查点 I/O 性能视为实现的一部分，并按第 2.6 节评估低内存 DCP 能力。
6. **__init__.py** -- 重新导出主模型类

参考模式文件以获取详细的实现指南：

- 密集 LLM：[llm-patterns.md](./llm-patterns.md)
- MoE：[moe-patterns.md](./moe-patterns.md)
- VLM：[vlm-patterns.md](./vlm-patterns.md)
- 能力和 fp32 精度：[capabilities-and-precision.md](./capabilities-and-precision.md)

大多数自定义模型需要 `state_dict_adapter.py` 进行 HF 权重转换。
仅当 HF 名称和张量布局在支持的后端/配置变体中已经匹配时才省略该文件和属性，例如 Llama、Qwen2 和 Qwen3。
权重绑定仍然是模型的责任（第 2.3 节）。

### 2.3 因果 LM 权重绑定

每个具有因果 `lm_head` 的注册模型类必须：

- 声明 `tie_word_embeddings_support: TieSupport` 为 `BOTH`、`TIED_ONLY` 或 `UNTIED_ONLY`。
- 在 `__init__` 的顶部调用 `reject_unsupported_tie_word_embeddings(type(self), config)`，使用原始配置，在解包 `text_config` 或 `thinker_config` 之前。

没有因果 LM 头的类可以明确豁免于注册测试。

从实现和实际支持的检查点配置中选择策略，而不是从裸配置构造器：

- `BOTH`：绑定和未绑定的配置都受支持。
- `TIED_ONLY`：仅支持绑定配置。
- `UNTIED_ONLY`：仅支持未绑定配置。

运行时辅助程序必须将 `TIED_ONLY` 和 `UNTIED_ONLY` 视为权威的，并且仅针对 `BOTH` 解析每个检查点的配置标志。所有当前的 `BOTH` VLM 都尊重外部的 `tie_word_embeddings` 标志，因此不要添加特定于模型的解析器，直到支持的 `BOTH` 模型实际需要另一个配置路径。

对于 `BOTH` 和 `TIED_ONLY`，始终声明 `_tied_weights_keys` 并实现 `tie_weights()`，使用实际的 `lm_head` 和输入嵌入 FQNs。不要依赖继承的 Hugging Face 绑定，并且在任何语言模型交换后重新绑定。

添加特定于策略的测试：

- `BOTH`：绑定别名；未绑定不别名。
- `TIED_ONLY`：绑定别名；未绑定被拒绝。
- `UNTIED_ONLY`：权重保持分离；绑定被拒绝。

不要绑定具有故意分离的头部、非对称词汇大小或不属于同一阶段的架构。

对于 `from_pretrained`，检查点保存的 `tie_word_embeddings` 值是权威的，即使对于 `BOTH`。`NeMoAuto*` 桥接器拒绝任何方向的翻转。一个模型拥有的 `from_pretrained` 跳过该桥接器必须调用 `reject_tie_word_embeddings_flip(checkpoint_config, requested_config, model_class_name)`。

### 2.4 MoE 状态字典适配器清单

对于 MoE 模型，验证所有权重。当它们的 HF 和原生布局不同时，适配器必须明确映射：

- 路由器权重，包括当 HF 模型具有门偏差或校正偏差张量时的门偏差或校正偏差张量。
- 专家权重，保留本地和路由专家之间的专家索引顺序。
- 门/上/下投影，包括组合或分组的投影布局。
- 当架构同时具有路由专家和共享专家时，将共享专家单独于路由专家。

添加测试，断言预期的键映射，并在尝试完整检查点之前使用微型配置运行数值等价性测试。

不要使用这些快捷方式：

- 不要仅通过调用 `from_pretrained()` 来验证适配器。
- 不要在没有明确的映射原因的情况下接受缺少或额外的专家键。
- 不要更改 dtype、转置维度或重塑张量，除非 HF 和 NeMo 布局需要它并且测试证明转换是可逆的。
- 不要因为密集层测试通过而跳过路由器或共享专家测试。

### 2.5 VLM 入职清单

对于 VLM，确认 HF 配置具有 `vision_config` 和 `text_config`，并且 `architectures` 指向条件生成类。从最接近的 VLM 模式文件开始，通常是 [vlm-patterns.md](./vlm-patterns.md)，并与现有的实现（如 `mistral4`、`kimivl` 或 `kimi_k25_vl`）进行比较。

实现应明确涵盖：

- 文本主干、视觉塔、投影器和处理器或图像预处理假设。
- 文本和视觉模块的检查点兼容性，在需要时使用适配器映射。
- 在 `_transformers/registry.py` 中注册 `ForConditionalGeneration` 类。
- 微型测试，执行图像-文本输入并验证检查点加载/导出，以及在存在适配器时进行适配器往返。

### 2.6 检查点 I/O 性能

将检查点性能视为实现要求，而不是后期优化。对于每个新的或实质性更改的状态字典适配器，评估加载和任何受更改影响的保存或导出路径的延迟和峰值主机/设备内存。特别是：

- 避免在张量可以直接加载到最终模型存储或可以有限部分转换时进行完整检查点或模型大小的临时副本。
- 当一个排名只需要其分片时，保持分布式读取和转换排名本地；不要在每个排名上不必要的全局张量。
- 避免在模型大小的循环中重复张量合并、复制、完整堆垃圾收集、分片扫描或文件打开。
- 记录优化路径的代表性先/后延迟和峰值内存证据，包括模型、dtype、后端和拓扑。

每个适配器必须评估 `supports_low_memory_dcp_load`。仅在大多数检查点张量直接写入最终模型存储，并且每个剩余的分配转换对于报告支持的每个运行时变体都具有小的、有界的临时占用空间时，才设置 `_supports_low_memory_dcp_load = True`。当后端、拓扑、dtype、量化模式或模型选项需要模型大小的重建时，保持其为假。假值选择安全的回退；它并不意味着检查点加载不受支持。

需要聚焦的测试需要通过直接目的地写入哨兵值，证明最终模型存储更改，绑定任何分配转换，并验证不安全的运行时变体报告该功能为假。此存储测试也是正确性要求：假阳性可能导致适配器将临时张量视为就地加载并跳过重建真实参数。

### 2.7 注册到注册表

将模型添加到 `_transformers/registry.py` 中的 `MODEL_ARCH_MAPPING`：

```python
# 在 _transformers/registry.py 中
MODEL_ARCH_MAPPING = OrderedDict([
    # ... 现有条目 ...
    (
        "NewModelForCausalLM",
        ("nemo_automodel.components.models.new_model.model", "NewModelForCausalLM"),
    ),
])
```

如果模型具有具有 `auto_map` 的自定义配置类，则也在 `_CUSTOM_CONFIG_REGISTRATIONS` 中注册：

```python
_CUSTOM_CONFIG_REGISTRATIONS: Dict[str, Tuple[str, str]] = {
    # ... 现有条目 ...
    "new_model": ("nemo_automodel.components.models.new_model.configuration", "NewModelConfig"),
}
```

### 2.8 声明能力和对精度敏感的参数

每个在 `MODEL_ARCH_MAPPING` 中注册的类都必须声明并行能力，可以使用静态嵌套的 `ModelCapabilities` 数据类或变体感知的 `get_capabilities(cls, config)` 类方法。选择其中一种模式。能力应反映已端到端验证的配方 YAML。

如果模型具有对精度敏感的参数，如 Mamba `A_log` / `dt_bias`、MoE 逻辑门偏差、注意力汇合偏差或每个头的 `scale`，声明 `_keep_in_fp32_modules_strict`，以便分片将那些参数保留在 fp32 计算中。参见 [capabilities-and-precision.md](./capabilities-and-precision.md) 获取示例、变体分发规则和冻结子模块 dtype 指导。

---

## 第 3 阶段：入职示例配置

此阶段仅用于添加一个最小的示例配置，以证明新入职的架构可以加载和运行。使用 nemo-automodel-recipe-development 进行通用配方编写或现有配方修改。

### 3.1 创建示例 YAML 配置

在 `examples/llm_finetune/<name>/`（或 `examples/vlm_finetune/<name>/`）下创建示例配置：

对于新的全参数 Adam/AdamW 示例，设置 `model.dtype: float32`。
参见 [训练精度](../nemo-automodel-recipe-development/SKILL.md#full-parameter-training-precision) 获取计算精度和其他训练模式。

```yaml
model:
  _target_: nemo_automodel.NeMoAutoModelForCausalLM.from_pretrained
  pretrained_model_name_or_path: <org>/<model-name>
  dtype: float32

trainer:
  max_steps: 100
  gradient_clip_val: 1.0
  accumulate_grad_batches: 1

# ... 数据、优化器配置 ...
```

### 3.2 验证模型加载

测试模型是否可以从 HuggingFace 检查点加载：

```python
from nemo_automodel import NeMoAutoModelForCausalLM

model = NeMoAutoModelForCausalLM.from_pretrained("<org>/<model-name>")
```

### 3.3 首先使用微型配置测试

在使用完整大小模型之前，使用微型配置（1-2 层，小隐藏维度）来尽早捕获形状不匹配。

## 第 4 阶段：测试

创建 `tests/unit_tests/models/<name>/` 并在加载完整检查点之前覆盖以下检查：

- 使用微型配置的前向形状烟雾测试。
- 状态字典适配器往返（如果存在）：`from_hf -> to_hf` 保留映射的名称、形状、dtype 和值。
- HF 加载/导出和原生保存/重新加载保留权重和绑定；参见 `tests/unit_tests/checkpoint/test_native_hf_state_dict.py`。
- 每个重写的注意力、MLP、归一化、RoPE 或 MoE 层的层等价性测试。使用配置中的模型 dtype、相同的种子权重、相同的输入和 dtype 适当的 `torch.allclose` 容差。
- 短功能测试，验证损失在几步训练中减少。

---

## 第 5 阶段：文档

### 5.1 更新模型覆盖页面

编辑 `docs/model-coverage/` 中的适当文件：
- LLM/MoE：`docs/model-coverage/llm/index.md`
- VLM：`docs/model-coverage/vlm/index.md`

添加一行模型名称、支持的功能（TP、PP、FSDP、LoRA、QLoRA）以及任何限制。

---

## 第 6 阶段：一致性测试

在实现和单元测试完成后，运行完整的一致性测试工作流程，以验证新模型在数值上与参考 HuggingFace 实现产生等效结果。

运行三个级别的比较：

1. 状态字典往返：加载参考 HuggingFace 检查点，将其转换为 NeMo AutoModel 布局，导出它，并验证所有映射的张量在预期容差内匹配参考的名称、形状、dtype 和值。
2. 组件级一致性：使用固定种子和相同 dtype，将重写的注意力、MLP、归一化、RoPE 和 MoE 组件与 HuggingFace 实现进行比较。
3. 端到端前向传递：在相同的标记化输入上运行完整的 NeMo AutoModel 和 HuggingFace 模型，并比较 logits、隐藏状态和损失。

不要跳过此阶段。即使通过单元测试，模型也可能由于细微的权重转换错误、后端差异或 RoPE 不匹配而在完整一致性比较中偏离 HF。

---

## 关键文件参考

| 文件 | 目的 |
|------|---------|
| `_transformers/registry.py` | `MODEL_ARCH_MAPPING` 和 `_CUSTOM_CONFIG_REGISTRATIONS` |
| `components/models/common/__init__.py` | 导出 `BackendConfig`、`HFCheckpointingMixin` 和后端构建实用程序 |
| `components/models/llama/model.py` | 具有单独的注意力和 MLP 投影的 HF 兼容权重 |
| `components/checkpoint/state_dict_adapter.py` | 可选的 `StateDictAdapter` 转换合同 |
| `components/models/common/hf_checkpointing_mixin.py` | 用于保存/加载的 `HFCheckpointingMixin` |
| `components/models/common/utils.py` | `BackendConfig`、`initialize_rms_norm_module`、`initialize_linear_module`、`get_rope_config` |
| `components/moe/config.py` | `MoEConfig` 数据类 |
| `components/moe/fsdp_mixin.py` | 用于分布式专家处理的 `MoEFSDPSyncMixin` |
| `components/moe/layers.py` | `MoE` 层，用于 MoE 块的 `MLP`（密集） |
| `components/moe/experts.py` | `GroupedExperts`、`GroupedExpertsDeepEP`、`GroupedExpertsTE` |

---

## 清单

- [ ] 获取并分析了 HuggingFace 的 `config.json`
- [ ] 确定了模型类型（密集 LLM / MoE / VLM）
- [ ] 确定了自定义组件（注意力、RoPE、归一化、MLP）
- [ ] 创建了 `components/models/<name>/` 目录
- [ ] 实现了 config.py（如果需要自定义配置）
- [ ] 实现了 layers.py（如果需要自定义层）
- [ ] 实现了 rope_utils.py（如果需要自定义 RoPE）
- [ ] 使用 `HFCheckpointingMixin` 实现了 model.py
- [ ] 如果需要，实现了 state_dict_adapter.py；评估了第 2.6 节中的检查点延迟和峰值内存
- [ ] 对于适配器，评估了 `supports_low_memory_dcp_load`；任何 opt-in 证明直接目的地可以到达模型存储，绑定分配转换，并报告不安全的运行时变体为假
- [ ] 使用 re-export 实现了 __init__.py
- [ ] 在 `_transformers/registry.py` 中的 `MODEL_ARCH_MAPPING` 中注册
- [ ] 注册了自定义配置（如果适用）在 `_CUSTOM_CONFIG_REGISTRATIONS` 中
- [ ] 声明了嵌套的 `ModelCapabilities` 数据类（静态）或 `get_capabilities(cls, config)` 类方法（变体分发，例如 ERNIE-4.5 MoE 与密集）
- [ ] 对于具有因果 `lm_head` 的每个类，声明了 `TieSupport` 并调用了构造器保护（或添加了明确的无头部豁免）--参见 §2.3
- [ ] 添加了特定于策略的别名和拒绝测试（`BOTH` / `TIED_ONLY`），以及 _tied_weights_keys 和 tie_weights，对于 `BOTH` / `TIED_ONLY`，以及政策特定的别名和拒绝测试 --参见 §2.3
- [ ] 任何模型拥有的 `from_pretrained` 跳过 `NeMoAuto*` 桥接器的，必须防御检查点翻转 --参见 §2.3
- [ ] 创建了示例 YAML 配置
- [ ] 验证了通过 `NeMoAutoModelForCausalLM.from_pretrained()` 加载模型
- [ ] 创建了单元测试（前向形状，状态字典往返）
- [ ] 为每个本质上为 fp32 的参数声明了 `_keep_in_fp32_modules_strict`（SSM `A_log`/`dt_bias`、Mamba `D` 当参考为 fp32 时、MoE 门偏差、注意力汇合偏差、`scale`，…）--参见 §2.8
- [ ] 为每个重写的层创建了层等价性测试（匹配模型 dtype）
- [ ] 创建了功能测试（训练损失减少）
- [ ] 更新了 docs/model-coverage 页面
- [ ] 运行了状态字典往返、组件一致性测试和端到端前向传递一致性检查
- [ ] 在模块底部设置了 `ModelClass = <Name>ForCausalLM`
