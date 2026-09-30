---
name: tilegym-converting-cutile-to-triton
description: 将 cuTile GPU 内核（@ct.kernel）转换为 Triton（@triton.jit）。处理标准库内转换、调试（cudaErrorIllegalAddress、形状不匹配、数值不匹配），并将 cuTile 语法（ct.load/ct.store、ct.Constant、ct.launch）映射到 Triton 的等效功能。涵盖双内核布局标志（例如 transpose=True/False + 通过 META 自动调整网格），具体参考 translations/advanced-patterns.md。在将 cuTile 内核转换为 Triton、移植或翻译时，或调试现有 Triton 转换时使用。
---

# cuTile → Triton 转换

将 `@ct.kernel` 内核转换为 `@triton.jit`。API 映射：[参考资料/api-mapping.md](./references/api-mapping.md) (cuTile → Triton)。

*在此技能的 Markdown 中，Triton 启动语法 `kernel［grid］(…)` 使用 Unicode 括号，以便链接检查器不会将 `[grid](…)` 解析为超链接；在真实的 Triton 代码中使用普通 ASCII 括号。*

## 说明

遵循 [translations/workflow.md](./translations/workflow.md) 中的分阶段工作流程。每次转换都应经过 **分析 → 转换 → 验证 → 测试 → 基准测试**，并在继续下一步之前进行明确的关卡。当任务匹配特殊情况（错误、布局标志、性能）时，使用 [Workflow Selection](#workflow-selection) 中的文档。

0. **优化策略（性能敏感 / 注意事项）** — 如果操作是 **注意力、FMHA、滑动窗口、软帽或 GQA**（例如 Gemma `gemma_attention`），则在转换内部循环之前，请阅读 **[references/optimization-strategy.md](./references/optimization-strategy.md)**，然后应用 **[§4 Gemma FMHA 检查清单](./references/optimization-strategy.md#4-gemma-fmha--gemma_attention-conversion-checklist-mandatory]**。对于其他 GEMM/BMM/注意力相邻内核，在 TMA 完成后，仍然快速浏览该文件的 §2–§3。

1. **选择路径** — 现有的 TileGym 操作：`translations/workflow.md` 中的标准模式。如果 cuTile 源代码使用 `transpose` / `transpose_v`、双布局或 MLA 风格路径，则在编写 Triton 之前，请阅读 [translations/advanced-patterns.md](./translations/advanced-patterns.md)（两个内核 + `META` 网格，而不是一个内核 + `tl.trans`）。

2. **起飞前检查** — 在 cuTile 源代码上运行 [起飞前分析](#pre-flight-analysis-run-before-converting) 的 grep 命令。计算 `@ct.kernel` 定义的数量；注意与 TMA 相关的 `ct.load`/`ct.store`、`ct.launch`、`Constant` 和布局标志。

3. **读取映射** — 保持 [参考资料/api-mapping.md](./references/api-mapping.md) 打开，用于 cuTile → Triton API 对。对于运行时错误（非法地址、dtype、strides），请使用 [参考资料/debugging.md](./references/debugging.md)。

4. **转换** — 将 [转换检查清单](#conversion-checklist) 复制到待办事项列表中，并按顺序执行。结构和文件放置：[translations/file-structure.md](translations/file-structure.md)。**必须**：任何 **2D+ 块形** 的 tile 加载/存储都使用 `tl.make_tensor_descriptor`（TMA），而不是原始 `tl.load(ptr+offs, mask=…)` 用于完整 tiles—跳过这一点是最常见的导致大量回归的来源。主机端：Triton 括号启动 <code>kernel［grid］(args)</code> 使用元组或 `lambda META: (…)` 进行自动调优；没有 `ct.launch`。

5. **验证** — 检查新 Triton 模块的语法；运行与操作相关的 TileGym pytest 目标：`pytest tests/ops/test_<op>.py -k "triton" -vs`。在基准测试之前修复失败。

6. **基准测试** — 在性能测试中比较 Triton 与 cuTile。如果 Triton 显着更慢，请遵循 **性能分析 (Phase c2t-5)** 在 [translations/workflow.md](./translations/workflow.md) 和 [参考资料/optimizing-reference.md](./references/optimizing-reference.md) 中用于 GEMM/BMM/注意力；使用 [参考资料/optimization-strategy.md](./references/optimization-strategy.md) 作为有序检查清单。如果您看到 **10–50×** 的减速，请首先阅读该相同工作流程文件中的 **CRITICAL PERFORMANCE PATTERNS**。

**执行规则（必须）：**

- 在编辑内核代码之前创建和跟踪转换检查清单（例如 TodoWrite）；按顺序完成步骤—不要跳过起飞前或 TMA 决策。
- 对于 **注意力 / FMHA / Gemma / GQA / 软帽 / 滑动窗口**：阅读 [参考资料/optimization-strategy.md](./references/optimization-strategy.md) 并应用 **§4** 在将转换视为优化之前。
- 不要发送在 TMA 适用的情况下使用原始指针+掩码 2D+ tile 加载；记录任何有意例外。
- 如果测试或基准测试在关卡中失败，请停止并修复—在宣布转换完成之前不要堆叠未经验证的更改。

## 工作流程选择

- **现有的 TileGym 操作** → 标准模式：[translations/workflow.md](./translations/workflow.md)
- **错误** (`cudaErrorIllegalAddress`、形状不匹配、数值不匹配) → [参考资料/debugging.md](./references/debugging.md)
- **高级模式**（TMA、双布局标志 `transpose`、自动调优 + `META` 网格、Array.slice、ct.gather().item()) → **[translations/advanced-patterns.md](./translations/advanced-patterns.md)** (MLA 风格两个内核，避免 `transpose=False` 上的 3–15× 回归)。
- **性能**（Triton 内核比 cuTile 慢、自动调优、性能分析）→ [translations/workflow.md](./translations/workflow.md)（**性能分析 (Phase c2t-5)** 部分）
- **优化策略中心**（有序检查清单：高级模式 + optimizing-reference）→ **[参考资料/optimization-strategy.md](./references/optimization-strategy.md)** — 对于注意力/FMHA/Gemma，首先阅读；然后根据需要深入两个源文档
- **优化 GEMM/BMM/注意力**（在 TMA 之后，或 Triton 慢 10–20%）→ **[参考资料/optimizing-reference.md](./references/optimizing-reference.md)** — EVEN_K 快速路径、通过指针算术进行转置、网格布局、自动调优宽度、尾声子 tile；在转换期间和性能签核之前使用这些模式（在优化策略 §2–§3 中总结）
- **Gemma 注意力 / GQA FMHA 转换** → **[参考资料/optimization-strategy.md §4](./references/optimization-strategy.md#4-gemma-fmha--gemma_attention-conversion-checklist-mandatory)**
- **Blackwell 优化**（具有迭代算法、寄存器压力、循环展开的复杂内核）→ **[参考资料/optimizing-reference.md](./references/optimizing-reference.md) §9** — TMA 描述符、`loop_unroll_factor`、占用率自动调优、TMEM 友好的块大小、 slab 分配器、双路径内核设计
- **⚠️ 10-50x 回归**（转换后灾难性减速）→ **[translations/workflow.md](./translations/workflow.md)** — **CRITICAL PERFORMANCE PATTERNS (AVOID 10-50x REGRESSION)** 部分
- **⚠️ 仅在 `transpose=True` 上性能良好，在 `transpose=False` 上崩溃**（或相反）→ **[translations/advanced-patterns.md](./translations/advanced-patterns.md)** — §1 双布局标志；两个 `@triton.jit` 内核 + `grid = lambda META: (... META["BLOCK_H"] ...)`

## 起飞前分析（运行在转换之前）

```bash
# 计算 kernels（只有主内核获得 @triton.jit，辅助函数保持普通 def）
grep "@ct\.kernel" source.py | wc -l

# 检查需要特殊处理的模式
grep "ct\.transpose\|ct\.permute" source.py   # → 使用 tl.trans/tl.permute
grep "ct\.astype" source.py                    # → 使用 .to(dtype)
grep "ct\.load\|ct\.store" source.py          # → 2D+ 使用 TMA (tl.make_tensor_descriptor)，不是原始 tl.load(ptr+offs)
grep "ct\.launch" source.py                    # → 括号启动：内核，然后 [grid]，然后 (args)
grep "ct\.Constant\|ct\.ConstInt" source.py    # → tl.constexpr
grep "ct\.cdiv" source.py                      # → triton.cdiv (主机) 或 Python (a+b-1)//b
grep "ct\.bid\|ct\.num_blocks" source.py       # → tl.program_id/tl.num_programs
grep "1 << .*\.bit_length" source.py           # → 如果需要，使用 triton.next_power_of_2
grep "transpose\|transpose_v" source.py       # → 如果命中，请阅读 translations/advanced-patterns.md（双内核 + META 网格）
```

## 转换检查清单

复制此检查清单并跟踪进度：

```
转换进度：
 [ ] 步骤 0（注意力 / Gemma FMHA / GQA / 软帽 / 滑动窗口）：在内部循环的 Triton 之前，阅读 [参考资料/optimization-strategy.md](./references/optimization-strategy.md) 并应用 §4 检查清单
 [ ] 步骤 1：起飞前 — 运行上述 grep 命令，注意特殊模式和 2D+ 加载（→ TMA）
 [ ] 步骤 2：分析源 cuTile 内核（识别模式、形状、dtypes）
 [ ] 步骤 3：创建具有正确结构的 Triton 文件（见 translations/file-structure.md）
 [ ] 步骤 4：转换内核签名（tensor 参数 → 指针参数，Constant → constexpr）
 [ ] 步骤 4b：TMA（必须对于 2D+ 加载）— 对每个 2D+ tile 加载/存储使用 tl.make_tensor_descriptor；不要发送原始 tl.load(ptr+offs,mask) 用于块形访问（见 workflow.md § TMA 优化）
 [ ] 步骤 5：转换内核体（应用 Gotchas 表格下方 + API 映射）
 [ ] 步骤 6：转换主机包装器（网格元组/lambda，括号样式启动：内核，网格，然后参数；没有 ct.launch）；如果使用 TMA，调用 triton.set_allocator(alloc_fn)
 [ ] 步骤 7：验证 — 运行 pytest 或在 Triton 文件上语法检查
 [ ] 步骤 8：测试 — 运行 pytest，验证 X 通过 0 失败
 [ ] 步骤 9：如果测试失败 → 修复 → 重新验证 → 重新测试（循环直到绿色）
 [ ] 步骤 10：基准测试 — 运行性能测试，与 cuTile 比较（见 workflow.md § 性能分析）
 [ ] 步骤 10b：如果 GEMM/BMM/注意力且 Triton >20% 慢 → 走 [参考资料/optimization-strategy.md](./references/optimization-strategy.md) §2–§3 然后 [参考资料/optimizing-reference.md](./references/optimizing-reference.md) (EVEN_K, 转置, 网格, 自动调优, 尾声子 tile)，然后重新基准测试
 [ ] 步骤 10c：如果操作有 `transpose` / 布局标志 → 阅读 [translations/advanced-patterns.md](./translations/advanced-patterns.md)；验证每个布局的 **分离内核**（不是转置内核 + `tl.trans`）；**自动调优** 启动使用 `lambda META: (triton.cdiv(..., META["BLOCK_H"]), ...)` — 除非自动调优被禁用，否则不通过 `apply()` 使用固定的 `BLOCK_H`/`BLOCK_N`

转换后验证（对于 2D+ 加载必须使用 TMA）：
 [ ] TMA: 所有 2D+ tile 加载使用 tl.make_tensor_descriptor(...).load([...])；没有原始 ptr+mask 用于块形 2D+ 访问（否则 5x-20x 回归）
 [ ] 网格使用元组或 lambda（不是 cuTile 像的三元组）
 [ ] 如果 cuTile 操作使用 kernel_configs/autotune，则添加 Triton 自动调优（见 workflow § 性能分析）
 [ ] 主机网格在适当的地方使用 triton.cdiv（不是 (a+b-1)//b 仅）
 [ ] 指针/偏移索引：Triton 使用元素偏移（ptr + offs），而不是在 tl.load 中的块索引（或使用 TMA 描述符）
 [ ] ct.astype(x, dtype) → x.to(dtype) 在 Triton 中
 [ ] ct.mma(a, b, acc=acc) → tl.dot(a, b, acc)（Triton 中没有关键字）
 [ ] 可选/None 参数：Triton 允许在内核参数中使用 None（如果需要）（cuTile 要求 dummy+flag）
 [ ] 掩码应用时 BLOCK_SIZE > 实际维度（与 cuTile 相同）；使用 TMA 时，掩码通常可以移除以用于完整 tiles
 [ ] 约简除数使用实际大小，而不是 BLOCK_SIZE
 [ ] fp32/tf32：Triton 默认允许_tf32=True；如果需要，匹配 cuTile 行为（如果有显式 tf32 转换）
 [ ] 如果任何 2D+ 加载使用原始 ptr+mask（例外仅限）：记录为什么没有使用 TMA
 [ ] 添加 tl.assume() 对齐提示以用于 strides 和指针
```

## Gotchas（最常见的转换错误）{#gotchas-most-common-translation-errors}

将 `@ct.kernel` 转换为 `@triton.jit` 时经常导致中断或回归的模式表—*mma 累加器、类型转换、网格、TMA 使用、dtype 处理、布局标志、批处理矩阵乘法等。*

**参见：** [参考资料/gotchas.md](./references/gotchas.md) — 在编写 Triton 内核之前阅读此内容。

## 性能 Gotchas（10-50x 回归风险）{#performance-gotchas-10-50x-regression-risk}

**⚠️ 这些会导致灾难性减速。在基准测试之前检查。**

模式和它们的影响：TMA 与原始 ptr+mask（5-20×）、自动调优与固定 tile 大小（2-3×）、`broadcast_to + tl.dot`（10-50×）、`extract_slice` 链（2-5×），以及更多。

**参见：** [参考资料/performance-gotchas.md](./references/performance-gotchas.md) — 完全回归风险表。

**详细信息：** [translations/workflow.md](./translations/workflow.md) — **CRITICAL PERFORMANCE PATTERNS (AVOID 10-50x REGRESSION)** 部分。

完整 API 映射：[参考资料/api-mapping.md](./references/api-mapping.md)。

Triton 数学 dtype（erf/erfc/exp/log/sqrt）和“不要用 tanh 替换 erf”模式：[参考资料/debugging.md](./references/debugging.md) — **Triton Math Function Dtype Requirements (CRITICAL)** 部分。

## 优化策略（中心）

**文件：** [参考资料/optimization-strategy.md](./references/optimization-strategy.md)

总结了 **[translations/advanced-patterns.md](./translations/advanced-patterns.md)**（布局标志、双内核、自动调优+`META`、批处理启动、Blackwell 指针）和 **[参考资料/optimizing-reference.md](./references/optimizing-reference.md)**（TMA 后微优化、§9）到 **§1–§3** 加上 **必须的 §4 Gemma FMHA 检查清单**。

**规则：** 对于 **注意力 / FMHA / Gemma 风格** 的转换，在同一会话中打开 **optimization-strategy** 与 **workflow** — 不要单独依赖 TMA 进行性能签核。

## 参考资料 {#reference-documents}

从 cuTile → Triton 的角度阅读。核心文件位于此技能的 `` 下。

| 类别 | 文档 | 内容 |
|------|------|------|
| **策略** | **[optimization-strategy.md](./references/optimization-strategy.md)** | **有序中心：advanced-patterns + optimizing-reference；§4 Gemma FMHA 必须检查清单** |
| **工作流程** | [translations/workflow.md](translations/workflow.md) | 标准 c2t 转换（阶段 + 检查清单） |
| | [translations/file-structure.md](translations/file-structure.md) | 从 cuTile 转换时放置 Triton 文件的位置 |
| | **[translations/advanced-patterns.md](./translations/advanced-patterns.md)** | **双布局标志 (transpose)、自动调优 + `META` 网格、MLA 风格两个内核** |
| **API** | [api-mapping.md](./references/api-mapping.md) | cuTile → Triton 映射 |
| | [optimizing-reference.md](./references/optimizing-reference.md) | **GEMM/BMM/注意力优化**（EVEN_K、转置、网格、自动调优、尾声子 tile） |
| **Gotchas** | [gotchas.md](./references/gotchas.md) | **常见的 cuTile→Triton 转换错误**（mma、dtype、网格、TMA、布局标志） |
| | [performance-gotchas.md](./references/performance-gotchas.md) | **10-50× 回归风险表**（TMA 与 ptr+mask、broadcast_to、extract_slice 链、自动调优） |
| **测试 & 错误** | [参考资料/debugging.md](./references/debugging.md) | **Triton 运行时错误**（cudaErrorIllegalAddress、指针类型、stride overflow） |

## 示例

使用 **cutile_kernel.py 作为源** 和 **triton_kernel.py 作为目标**：

| 示例 | 目录 | 复杂度 |
|------|------|--------|
| 向量加 | [examples/01_vector_add/](examples/01_vector_add/) | 基本操作 |
| Softmax | [examples/02_softmax/](examples/02_softmax/) | 中级 |
| LayerNorm | [examples/03_layernorm/](examples/03_layernorm/) | 中级 |
| MatMul | [examples/04_matmul/](examples/04_matmul/) | 高级 |
| 注意力 | [examples/05_attention/](examples/05_attention/) | 高级 |

首先阅读 `cutile_kernel.py`，然后 `triton_kernel.py`，以查看反向映射。

## ⚠️ 必须完成检查清单（不要跳过）

**转换不完整，直到所有项目都被检查。复制并完成：**

```
必须完成的完成关卡：
 [ ] 1. 正确性：pytest 通过 0 失败
     命令：python -m pytest {test_path} -k "test_op and triton" -vs --tb=short
     关卡："X 通过，0 失败"

 [ ] 2. TMA 优化：所有 2D+ tile 加载使用 tl.make_tensor_descriptor
     验证：grep -n "tl.load.*mask" triton_file.py | wc -l  # 对于 2D+ 操作，应该为 0
     跳过 = 5-20x 性能回归

 [ ] 3. 性能测试：Triton 在 20% 以内于 cuTile 基线
     命令：python -m pytest {test_path} -k "test_perf" --print-record -v
     或：运行基准测试脚本：cd tests/benchmark && python bench_{op}.py
     关卡：Triton TFLOPS >= 0.8 * CuTile TFLOPS

 [ ] 4. 性能比较记录：
     记录结果：
     | 配置 | Triton (TFLOPS) | CuTile (TFLOPS) | 比率 |
     |------|-----------------|-----------------|------|
     | [填充] | [填充]          | [填充]          | [填充]|

转换完成：所有 4 个关卡通过？→ 是 / 否
```

**为什么这很重要：**
- 关卡 1 捕获功能错误
- 关卡 2 防止灾难性 5-20x 回归（最常见的错误）
- 关卡 3 验证优化是否有效
- 关卡 4 创建问责记录

**如果任何网关出现故障：** 修复并重新验证，然后才能宣布完成。
