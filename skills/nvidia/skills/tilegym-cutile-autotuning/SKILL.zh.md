---
name: tilegym-cutile-autotuning
description: 在添加、修改、优化或调试 CuTile 自动调优代码时使用。触发信号：代码中的 `exhaustive_search` / `replace_hints` / `hints_fn` / `cuda.tile.tune`，文件名中的 `autotune`，或自动调优 CuTile 内核的正确性问题/性能问题。涵盖内容：一次性调优/缓存/启动模式、针对不同架构的配置（sm80–sm120）、参数空间设计（瓦片大小、占用率、CTA 数量），以及 7 个常见陷阱及解决方案。
---

# CuTile 自动调优

使用 `exhaustive_search` API 以 tune-once/缓存/直接启动模式为 CuTile 内核添加自动调优功能。

## 说明

遵循决策树对内核进行分类，设计搜索空间，实现 tune-once/缓存/启动模式，并验证性能。

1. **分类** — 使用决策树确定搜索维度（仅占用率搜索 vs 全片搜索）
2. **设计搜索空间** — 从 `references/kernel-type-templates.md` 选择匹配模板；通过架构过滤器修剪最终代码中的配置数量≤30（定向探索探测可能暂时超过此限制——参见设计理念）
3. **实现** — 按照 Step-by-Step Workflow 添加 `exhaustive_search` + 缓存 + `ct.launch`；如有必要，使用 split-buffer 处理原地写入
4. **测试** — 启用自动调优运行正确性测试，并使用 `DISABLE_AUTOTUNE=1`
5. **验证** — 与固定最佳配置进行 A/B 基准测试；参见 `references/search-strategies.md`
6. **精简** — 修剪从未获胜的死重配置，目标为每个架构≤8个配置以最小化编译成本（步骤 10）

## 任务路由 — 跳转到您需要的内容

| 您试图做什么？ | 前往 |
|---|---|
| 为新内核添加自动调优（最常见） | 快速参考下方 → Workflow: 添加自动调优 → `references/kernel-type-templates.md`（按内核类型选择：T1=元素级，T2=原地，T3=矩阵乘法，T4=持久，T5=FMHA，T6=FP8，T7=分组 GEMM，T8=变长注意力，T9=双 GEMM 融合） |
| 调试：第一次运行后数据损坏/结果错误 | 陷阱 #1（原地内核） |
| 调试：自动调优耗时超过 5 分钟 | 陷阱 #2（编译超时） |
| 调试：搜索空间生成器返回零配置 | 首先检查陷阱 #5；同时检查架构过滤器、大小保护和 `num_ctas` 约束 |
| 优化现有自动调优配置 | Workflow: 优化现有配置 |

## 快速参考 — 仅占用率自动调优（Tune-Once/缓存/启动）

大多数 CuTile 内核（元素级、归约、LayerNorm）仅需占用率调优。复制此模式：

```python
from types import SimpleNamespace
from cuda.tile.tune import exhaustive_search
import cuda.tile as ct
import torch

def _my_autotune_configs():
    for occ in [1, 2, 4, 8]:
        yield SimpleNamespace(occupancy=occ)

# 模块级缓存：调优一次，之后快速启动
_autotune_cache = {}

def my_op(x, output):
    stream = torch.cuda.current_stream()
    NUM_SM = torch.cuda.get_device_properties(x.device).multi_processor_count

    # 缓存键：任何影响最佳配置的因素（使用 str() 表示设备）
    cache_key = (x.shape, x.dtype, str(x.device))

    if cache_key not in _autotune_cache:
        configs = list(_my_autotune_configs())
        result = exhaustive_search(
            configs,
            stream,
            grid_fn=lambda cfg: (min(NUM_SM * cfg.occupancy, M), 1, 1),
            kernel=my_kernel,
            args_fn=lambda cfg: (x, output, ...),
            hints_fn=lambda cfg: {"occupancy": cfg.occupancy},
        )
        best_cfg = result.best.config
        tuned_kernel = my_kernel.replace_hints(occupancy=best_cfg.occupancy)
        _autotune_cache[cache_key] = (best_cfg, tuned_kernel)  # 缓存两者

    cfg, tuned_kernel = _autotune_cache[cache_key]
    grid = (min(NUM_SM * cfg.occupancy, M), 1, 1)
    ct.launch(stream, grid, tuned_kernel, (x, output, ...))
```

关键规则：
- **调优一次，缓存，直接启动** — `exhaustive_search` 仅在每次调用时运行；后续调用使用缓存的配置 + `ct.launch`，开销为零
- 对于原地内核，在搜索期间使用 split-buffer（分离输入/输出张量）
- 保持最终代码中≤30个配置（参见设计理念中的临时定向探测）
- `exhaustive_search` 需要一个 `Sequence`（列表/元组）— 使用 `list()` 转换生成器
- **搜索空间必须包含原始固定配置** — 这保证了自动调优永远不会使性能变差

**何时使用此模式**：内核具有固定块大小（不可调 tile 大小）。包括：元素级（SwiGLU、GeGLU）、归约（RMSNorm、LayerNorm）、RoPE，以及具有启发式块大小的持久内核（分组 GEMM）。

对于复杂内核（带 tile 大小的矩阵乘法、FMHA、FP8 带有 num_ctas），请阅读下方完整指南 + [`kernel-type-templates.md`](references/kernel-type-templates.md)。

> **⚠️ 三个陷阱几乎捕获所有人 — 提交前检查：**
> - **热路径上使用 `replace_hints`？** → 缓存配置和 `exhaustive_search` 的内核对象。每次调用 `replace_hints()` 都会重新编译（100–500× 更慢）→ 陷阱 #7
> - **原地内核**（写入输入张量？）→ 必须在搜索期间使用 split-buffer 模式 → 陷阱 #1
> - **搜索空间为空？** → 检查架构过滤器和 `num_ctas` 约束 → 陷阱 #5

> **最小覆盖率**：在 sm100+ 上，FMHA/矩阵乘法/变长搜索空间必须包含 `num_ctas=1` 和 `num_ctas=2`。对于核心维度（tile 大小、占用率），即使不确定哪个更好，也要保持至少 2 个不同值——让 `exhaustive_search` 决定。

> **何时停止调优**：平均加速比在 [0.98, 1.02] 之间意味着当前搜索空间没有帮助——但这并不意味着没有配置会帮助。在停止之前，请检查是否已覆盖此内核类型的键维度（参考 `references/kernel-type-templates.md`）。如果搜索空间已覆盖模板推荐维度，且最佳结果仍是噪声底部，则停止——进一步的微调不会有所帮助。如果关键维度缺失（例如，从未尝试双 GEMM 内核的 `num_ctas=2`），请扩展搜索空间而不是放弃。

> 一旦通过正确性测试，自动调优内核在固定配置基线之上显示加速比，**停止——不要重新运行以“确认”。** GPU 内核计时在调用之间波动 ±5–10 %，由于时钟缩放和 OS 调度；后续计时下降并不意味着代码错误。

> 要提高加速比，仅修改自动调优搜索空间（配置、tile 大小、占用率、num_ctas）。不要修改其他代码（Python 包装器、流管理等）以追求加速比——内核性能由配置选择决定，而不是主机端代码。

## 阅读指南

- **仅占用率内核**（元素级、归约、具有固定块大小的持久内核）：快速参考 + 陷阱检查清单就足够了——跳过 `references/` 文档。对于原地内核，也请阅读陷阱 #1。
- **复杂内核**（带可调 tile 大小的矩阵乘法、FMHA、FP8 带有 num_ctas）：快速参考 → 决策树 → API 参考 → Step-by-Step Workflow → 相关 `references/` 文档。

**5 步摘要**：分类内核 → 设计搜索空间（`[`parameter-space-design.md`](references/parameter-space-design.md)`）→ 使用模板实现（`[`kernel-type-templates.md`](references/kernel-type-templates.md)`）→ 使用 A/B 测试验证 → 检查陷阱检查清单。

**阅读参考**：仅阅读与您的内核类型相关的参考——例如，对于 FMHA，请阅读 `references/kernel-type-templates.md` 中模板 5 的部分；对于硬件约束，仅阅读目标架构的部分。当有针对性的查找就足够时，避免通读所有参考。

## 设计理念

**自下而上构建一个小而精确的搜索空间——而不是修剪一个大空间。** CuTile 编译比 Triton 重得多（每个配置 ~0.5-1s），因此**最终代码**应包含≤30个配置。方法是：首先分类内核类型，然后为该类型和架构构建仅相关的配置。

**开发期间的定向探索**：如果初始模板配置的加速比 < 1.0，您可以通过 `bash + python3 -c` 运行一个*临时*较大的探测（30–100 个配置）来识别哪些维度重要——但这个探测必须是**定向的**，而不是盲目的笛卡尔积。使用内核类型分类来决定*哪些*维度要变化（例如，对于双 GEMM，探测 `num_ctas × 占用率` 而固定 tile 大小；对于 FMHA，探测 `TILE_M × num_ctas` 而固定 TILE_N）。一旦探测识别出获胜区域，请将最终代码的搜索空间锁定到≤8个顶级候选。**不要**将大型探测写入源文件——它是一个一次性诊断工具。

## 决策树：此内核需要哪些搜索维度？

所有内核都应该添加自动调优。问题不是*是否*要自动调优，而是*哪些*维度要搜索：

```
这是什么类型的内核？
├── 计算密集型（矩阵乘法、GEMM、FMHA）→ 它是否有多个可调维度（tile 大小）？
│   ├── 是 → 它是融合多 GEMM 内核吗（双 GEMM，例如 Linear+GLUAct）？
│   │   ├── 是 → 模板 9：低占用率（1–2），保守的 tiles（2× SHMEM/寄存器压力）
│   │   └── 否  → 全搜索：TILE_M × TILE_N × (TILE_K) × 占用率 × num_ctas
│   │             （参见 matmul/FMHA 模板在 kernel-type-templates.md）
│   └── 否  → 占用率搜索：[1, 2, 4, 8]
│             （参见上方快速参考）
├── 平衡（LayerNorm、计算+归约）→
│   占用率搜索：[1, 2, 4, 8]
│   预期收益：2-15%
└── 内存密集型（CE 损失、纯元素级）→
    占用率搜索：[1, 2, 4, 8]
    预期收益：0-15%（内核不同而异；调优后无成本）
```

**为什么内存密集型内核仅搜索占用率（不搜索 num_ctas 或 tile 大小）**：
- **`num_ctas` 没有收益**：`num_ctas > 1` 启用 TMA 多播，多个 CTA 在共享内存中共享 tile 数据（例如，矩阵乘法 A/B tiles 跨 CTA 重用）。内存密集型内核使用 `ct.gather`/`ct.scatter` 进行逐元素操作，没有 tile 重用——多 CTA 协作增加开销而没有数据共享收益。
- **Tile 大小是预先确定的**：内存密集型内核的 BLOCK_SIZE 由离线扫描确定（例如，B200 在 [256, 512, 1024, 2048, 4096, 8192] 上全局最优为 1024）。这是一个常数，不是运行时可调的。
- **占用率是唯一有效的旋钮**：更高的占用率允许 GPU 通过在内存请求停顿时切换到另一个 CTA 来隐藏内存延迟。

> **证据——CE 损失实验**：在交叉熵损失上的 12 配置搜索（占用率 × num_ctas）仅获得 2.5% 的收益（0.79x → 0.81x vs Triton）。`num_ctas` 维度没有贡献；结果因编译成本超过边际收益而被撤销。占用率仅（4 配置）在 3 倍更少的编译时间内实现了相同的结果。

> **关于内存密集型内核的注意**：添加占用率自动调优总是值得的，因为：
- Tune-once/缓存/启动模式在第一次调用后具有零运行时开销
- 搜索空间很小（4 配置，~2-4s 编译时间）
- 即使小的改进在规模上也有价值

## 占用率选择指南

占用率控制每个 SM 同时运行的 CTA 数量。设计占用率搜索空间时以此作为起点：

| 占用率范围 | 最佳用途 | 示例内核 |
|-----------------|----------|-----------------|
| 1–4 | 计算密集型（重数学） | 复杂变换、矩阵乘法 |
| 4–8 | 平衡（GEMM、TMA） | 矩阵乘法、FMHA |
| 8–16 | 内存密集型（归约） | Softmax、LayerNorm |
| 16–32 | 非常轻（复制、转换） | 类型转换、元素级 |

使用这些范围来初始化您的搜索空间。对于占用率仅内核，`[1, 2, 4, 8]` 覆盖大多数情况——参见上方快速参考。

## exhaustive_search API 参考

有关完整的 `exhaustive_search` API 表面，请参阅 [references/api-reference.md](references/api-reference.md) — 当前签名、`TuningResult`、tune-once/缓存/启动模式、`replace_hints`、内核提示、`search_space` 设计和 `grid_fn` 模式。

## Step-by-Step Workflow

有关端到端工作流，请参阅 [references/workflow.md](references/workflow.md) — 添加自动调优到新内核、处理现有多架构配置、与 `torch.autograd.Function` 集成、跨后端配置传输（Triton → CuTile）以及优化现有配置。

## Pitfall Checklist

有关完整常见陷阱列表，请参阅 [references/pitfalls.md](references/pitfalls.md) — 原地数据损坏、编译超时、冷缓存性能偏差、NCU 分析干扰、`search_space` 生成器耗尽、FP8 精度损失以及热路径上 `replace_hints` 重新编译。

## 范围和边界

此技能仅涵盖自动调优配置：搜索空间设计、`exhaustive_search` 调用和结果处理、`kernel.replace_hints()` 应用调优提示、缓存逻辑（键设计、字典管理）、`ct.launch()` 使用调优内核、`DISABLE_AUTOTUNE` 回退路径。

**在范围内**（自动调优配置）：
- 搜索空间生成器函数
- `exhaustive_search()` 调用和结果处理
- `kernel.replace_hints()` 应用调优提示
- 缓存逻辑（键设计、字典管理）
- `ct.launch()` 使用调优内核
- `DISABLE_AUTOTUNE` 回退路径

**超出范围**（内核代码修改——不要进行这些更改）：
- 数学标志（flush_to_zero、rounding_mode）
- 性能提示（slice_hint、buffer_depth、copy_config）
- 内存访问模式（2D→1D gather/scatter 转换）
- 代码生成优化（safe_offs → padding_value）
- 算法更改（K-loop 分裂、负载平衡）

## 进一步优化建议

添加自动调优后，以下内核级优化可能带来额外收益。这些*不在本技能范围内*——将它们作为潜在下一步提给用户，但不要作为自动调优的一部分实现它们：

- **数学标志**：`flush_to_zero=True` + `rounding_mode=APPROX` 可以为 FMHA 类内核提供 34-72% 的改进（通过环境变量 `TILEIR_ENABLE_FTZ=1 TILEIR_ENABLE_APPROX=1` 或在内核代码中设置）。*因果链*：较大的 tiles 最初由于次正规处理开销而*降低*性能 18-43%；启用 FTZ+APPROX 挽救了这一点并反转结果为 +34-72%。因此，数学标志是*大 tile 配置有效*的 FMHA 类内核的*先决条件*。
- **性能提示**：`slice_hint`、`buffer_depth`、`copy_config` — 需要修改内核 IR 代码
- **内存访问模式**：使用 TMA 加载（`ct.load`）而不是 `ct.gather`；移除不必要的边界检查（`check_bounds=False` 当安全时）
- **代码生成质量**：使用 `padding_value` 参数而不是手动 `ct.where` 掩码；移除 `safe_offs`
- **算法重构**：K-loop 分裂、负载平衡、代数简化

## 与 Triton 自动调优的差异

主要差异：Triton 使用 `@triton.autotune` 装饰器与 `Config(...)` 对象；CuTile 使用 `exhaustive_search()` 与 `SimpleNamespace` 配置 + 分离缓存 + `ct.launch`。CuTile 没有 `num_warps`/`num_stages`（编译器决定）——只有 tile 大小 + 占用率 + `num_ctas`。CuTile 编译更重（最终代码中保持≤30个配置）。CuTile 缓存是用户管理的内存（没有自动持久化）。CuTile 将 `args_fn`（内核参数）与 `hints_fn`（编译器提示）分离。

## 参考文档

| 类别 | 文档 | 内容 |
|-------|-------|-------|
| **API 参考** | [`api-reference.md`](references/api-reference.md) | `exhaustive_search` 签名，`TuningResult`，单次调优/缓存/启动模式，`replace_hints`，内核提示，`search_space` 设计，`grid_fn` 模式 |
| **工作流** | [`workflow.md`](references/workflow.md) | 端到端工作流：向新内核添加自动调优，多架构配置，`torch.autograd.Function` 集成，Triton→CuTile 转换，优化现有配置 |
| **陷阱** | [`pitfalls.md`](references/pitfalls.md) | 常见陷阱：原地损坏，编译超时，冷缓存偏差，NCU 干扰，`search_space` 用尽，FP8 精度，`replace_hints` 重新编译 |
| **参数设计** | [`parameter-space-design.md`](references/parameter-space-design.md) | 按内核类型划分的参数空间，跨架构模式，`grid_fn` 模式，剪枝规则 |
| **搜索策略** | [`search-strategies.md`](references/search-strategies.md) | 搜索，A/B 测试方法，`DISABLE_AUTOTUNE` 模式 |
| **模板** | [`kernel-type-templates.md`](references/kernel-type-templates.md) | 8 种内核类型的复制粘贴自动调优模板 |
| **硬件** | [`hardware-constraints.md`](references/hardware-constraints.md) | 按架构划分的约束，块大小范围，`num_ctas` 规则，TMA 要求 |

## 代码参考

关键文件：`ops/cutile/matmul.py`（矩阵乘法自动调优），`ops/cutile/attention.py`（FMHA 自动调优），`suites/unsloth/cutile/ct_ops.py`（共享 `autotune_configs()` 占用率=[1,2,4,8]），`suites/unsloth/cutile/swiglu.py`（元素运算示例），`suites/unsloth/cutile/rope_embedding.py`（分块模式），`suites/unsloth/cutile/grouped_gemm.py`（持久 GEMM，仅占用率调优）。

## 实例分析

每个示例展示 **“前 → 后”** 模式：`fixed_launch.py`（硬编码 `ct.launch`）和 `autotuned_launch.py`（重构为单次调优/缓存/启动）。

| 目录 | 内核 | 自动调优模式 | 复杂度 | 关键教学点 |
|------|------|--------------|--------|-----------|
| [`assets/examples/01_rmsnorm_occupancy_only/`](assets/examples/01_rmsnorm_occupancy_only/) | RMSNorm（归约） | 仅占用率 `[1,2,4,8]` | 低 | 最常见模式 — 无块调优，仅查找最佳占用率。网格 = `NUM_SM * cfg.occupancy`。非原地。 |
| [`assets/examples/02_matmul_full_search/`](assets/examples/02_matmul_full_search/) | GEMM C=A@B | 全：`TILE_M/N/K` + `占用率` + `num_ctas`（sm90+） | 高 | 计算密集型内核，具有多个可调维度。`args_fn` 将块大小作为 `ct.Constant[int]` 传递。`grid_fn` 取决于 `cfg`。≤30 个配置。 |
| [`assets/examples/03_rope_inplace_splitbuffer/`](assets/examples/03_rope_inplace_splitbuffer/) | RoPE 嵌入（原地） | 仅占用率，带分块 | 中 | 原地内核在搜索期间必须使用分块以避免损坏。搜索写入缓存；最终 `ct.launch` 使用真实原地参数。 |
