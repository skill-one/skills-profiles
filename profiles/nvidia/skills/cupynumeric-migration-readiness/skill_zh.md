# cuPyNumeric 迁移准备

## 目的

**在迁移之前使用此技能，而不是在迁移期间。** 回答一个问题：*用户现有的 NumPy API 哪些可以在 cuPyNumeric 上扩展，哪些需要重构，在它们投入工程师周进行移植之前？* 为了回答它：阅读源代码，根据其在 Legate/NVIDIA GPU 堆栈上的预期多 GPU 扩展性对每个 NumPy 习语进行分类，对照捆绑的 API 支持清单，并生成一个结构化的裁决，包含每个发现的推理和配方指针。

**这是一个静态的、只读的评估。** 使用 `Read`、`Grep` 和 `Grep` 检查用户的源代码。**不要**执行用户的代码、修改或写入文件，或打印环境变量或密钥。下面的 `legate` 和 cuPyNumeric Doctor 命令是建议用户运行的——不是此技能执行的操作。

如果此技能以前从未见过，请先查看 [`references/getting-started.md`](references/getting-started.md)。

## 何时使用此技能

当用户**即将**将 NumPy 代码迁移到 GPU 并询问它是否会在 cuPyNumeric/GPU 上扩展，是否应该迁移，哪些部分将受益，移植前必须更改什么，或者移植是否值得——或者提到预移植评估、扩展分析、习语分析、GPU 重构规划或识别 GPU 的 NumPy 反模式时使用。

**拒绝并重定向**当请求*不是*迁移前评估时：

- **迁移后性能/分析**（“已经移植了，为什么很慢？”）→ 指向 `legate --profile` 和上游 [分析](https://docs.nvidia.com/cupynumeric/latest/user/profiling_debugging.html) 漫游。
- **自定义 CUDA/内核编写**（“编写/优化一个 CUDA 内核”）

用户正在询问迁移的图/稀疏/机器学习/NLP 工作负载仍然**在范围内**：评估它并返回**不推荐**通过 Gate 4。这是一个裁决，不是拒绝。

## 说明

按顺序运行以下五个步骤。阅读用户的代码并进行语义推理；不要发出一次性散文裁决。

### 第 1 步 — 收集上下文

扫描代码之前获取。以下每个项目都有一个针对典型工作负载的默认值——当用户不提供具体信息时使用默认值；不要阻止提问。

- **源位置。** 当未给出路径时，默认为当前工作目录。
- **运行时近似热路径数组大小。** 默认为 3000 万到 5000 万个元素。将用户的数据（或此默认值）映射到 [Gate 2 级别](references/decision-framework.md#gate-2-problem-size)（每个 GPU 65K 的底部；10M+ 用于真实的单 GPU 加速；100M+ 用于多 GPU）。
- **目标硬件。** 默认为 1-4 个 GPU，单节点。在假设多节点之前进行确认。对于 CPU 仅运行，询问每个节点的 RAM 而不是 FBMEM。
- **主导计算模式。** 棋盘格/矩阵乘法/蒙特卡洛/归约/混合 SciPy。询问用户命名它；否则从第 3 步的代码中推断。

在评估顶部说明您应用的默认值，以便用户可以更正它们。如果一个值无法确定，请直白地说，并继续进行定性评估——不要编造上述默认值之外的数字。

### 第 2 步 — 加载 API 支持清单

读取 [`assets/api-support.md`](assets/api-support.md)，这是上游 NumPy 与 cuPyNumeric 对比表的提交快照。对于代码调用的每个 NumPy API，找到其行并读取开头的符号：

- `✓✓ numpy.X` — 已实现并在多 GPU 上工作（最佳路径）。
- `✓ numpy.X` — 已实现但仅单 GPU/CPU（多节点注意事项）。
- `🟡 numpy.X — <注释>` — 部分支持；阅读注释。
- `✗ numpy.X` — 在 cuPyNumeric 分布式路径上未实现。调用行为版本特定（某些不支持的 API 路由到主机 NumPy，其他引发异常）——无论如何，热路径使用都是迁移的障碍。不要向用户承诺静默回退到主机 NumPy。

如果 `Fetched:` 行超过 ~90 天，请刷新快照——见**可用脚本**部分。

### 第 3 步 — 语义读取代码

使用 `Read` 和 `Grep` 遍历用户的文件，并将每个数组数学区域分类到 [`references/idioms-that-scale.md`](references/idioms-that-scale.md) 和 [`references/idioms-that-block.md`](references/idioms-that-block.md)（完整的推理和 R 代码在那里）。语义读取，而不是正则表达式：在标记之前，确认 `arr` 追溯到 `cupynumeric` 数组（或 `np.*` 别名到它），并检查访问是否位于热循环内。应用这些规则：

- **标记元素循环**（`for i in range(n): arr[i] = ...`）为障碍；将具有向量化体的 epoch/step/file 循环视为良好——区分这两种情况。
- **标记标量同步**——在热循环中的 cuPyNumeric 数组上的 `.item()` / `float()` / `int()` / `bool()` / `complex()`（每迭代主机同步）；允许它在边界处。
- **标记归约条件**——`if`/`while` 覆盖数组归约（`while np.max(err) > tol:`）每迭代同步。
- **标记循环中的可提升分配**为可修复的低效。
- **在运行时代码中标记 `mpi4py`** 与 `cupynumeric` 一起分区/通信数组数据（[R108](references/idioms-that-block.md#r108)）——但首先确认它在热路径上发出 MPI 调用；忽略 README、构建脚本或替代启动器中的 grep 匹配。
- **标记 `reshape` / `asarray` / `flatten` 上的 `order=`** 为 [R109](references/idioms-that-block.md#r109)——始终如此，无论版本是否警告或静默无操作。
- **始终在 INFO 中引用 [R304](references/idioms-that-scale.md#r304)** 对于 `np.random.*` 在多 GPU 下：默认情况下无法跨 GPU 位相同重现（`--gpus N` / `LEGATE_GPUS` 是 [Legate 启动器参数](https://docs.nvidia.com/legate/latest/manual/usage/running.html)）。
- **标记数组上的 Python 内置函数**（`sum`/`max`/`min`/`any`/`iter(arr)`）——主机迭代回退（[R110](references/idioms-that-block.md#r110)；[上游最佳实践](https://nv-legate.github.io/cupynumeric/user/practices.html#use-numpy-s-functions-avoid-using-python-s-built-in-functions)）。允许 `len(arr)`（形状查找；优先 `arr.shape[0]` / `arr.size` 对于 0-d 安全）。
- **标记热循环中的 `cupy` 混合 `cupynumeric`**（[R111](references/idioms-that-block.md#r111)）；运行时不会共享 GPU 内存，因此每个跳转都通过主机 NumPy。
- **在 `assets/api-support.md` 中查找代码调用的每个 NumPy API**（符号图例在第 2 步中）。

对于深层“原因”，阅读 [`references/gpu-stack.md`](references/gpu-stack.md)（内存、SM、通信、调度）和 [`references/execution-model.md`](references/execution-model.md)（延迟执行、同步点、mapper）。

### 第 4 步 — 生成结构化评估

按此顺序交付报告。为每个发现引用 `file:line` 以便用户可以导航。

1. **裁决**——一句话——见下文“裁决框架”。
1. **什么可以工作（SCALES 发现）**——引用代表性行，以便用户看到导入交换后什么会加速。
1. **什么会阻塞（BLOCKS 发现）**——每个都与 [`idioms-that-block.md`](references/idioms-that-block.md) 和 [`refactor-recipes.md`](references/refactor-recipes.md) 中的配方相关联。
1. **什么可以修复（REFACTOR 发现）**——按配方分组；一个配方通常可以修复许多位置。
1. **兼容性/成本注释（INFO 发现）**——SciPy 边界、仅单设备 `linalg.qr/svd`、单转换 `fft.*`、大小阈值 `linalg.solve/cholesky`。
1. **API 支持差距**——清单中未实现或仅单 GPU 的 API。
1. **决策框架摘要**——来自 [`references/decision-framework.md`](references/decision-framework.md) 的门 1-6，标记为通过/失败/不确定。
1. **推荐的下一步**——首先应用哪些配方，是否先移植一个模块，以及何时涉及 cuPyNumeric Doctor。

**所有 8 个部分都必须出现**，即使裁决是 READY 或 NOT RECOMMENDED。在空标题下写一行 **“此代码无”** 或 **“n/a — 见裁决”**——**不要**省略标题；标题是报告评分的结构性合同。见 [`assets/sample_report.md`](assets/sample_report.md) 用于已处理的报告。

### 第 5 步 — 交由 cuPyNumeric Doctor 进行运行时验证

指导用户在应用配方后代码运行时运行 [cuPyNumeric Doctor](https://docs.nvidia.com/cupynumeric/latest/user/doctor.html)：

```bash
CUPYNUMERIC_DOCTOR=1 CUPYNUMERIC_DOCTOR_FORMAT=json CUPYNUMERIC_DOCTOR_FILENAME=doctor-report.json legate --gpus 1 main.py
```

cuPyNumeric Doctor 捕获源代码审查可能遗漏的内容（标量项访问、ndarray 迭代、高级索引、`nonzero` 误用、`mpi4py` 导入、视图上的原地操作）。在：”现在启用 cuPyNumeric Doctor 运行；以下是其在输出中要查找的内容。”

## 裁决框架

从*发现类型*定性分配裁决，而不是分数：

| 裁决 | 当... | 操作 |
|---|---|---|
| **READY** | 无 BLOCKS；少量/无 REFACTOR | 交换导入；基准测试 |
| **LIGHT REFACTOR** | 几个可由配方修复的模式（[R201](references/idioms-that-block.md#r201)–[R206](references/idioms-that-block.md#r206)），或一个或两个简单的 BLOCKS | 应用 1-3 个来自 [`refactor-recipes.md`](references/refactor-recipes.md) 的配方；重新检查到 READY |
| **SIGNIFICANT REFACTOR** | 热路径上的多个 BLOCKS，或任何 [R108](references/idioms-that-block.md#r108)（`mpi4py`）——重写，不是淘汰 | 真实项目；预算每个模块 1-3 个工程师周 |
| **NOT RECOMMENDED** | 只有两个失败：门 2（数组低于 65,536 底部）或门 4（错误的计算模式）。一堆 BLOCKS 不在这里落地 | 首先重构或使用不同的运行时 |

按顺序应用这些；第一个匹配者获胜：

1. **门 4 失败**（稀疏/图/机器学习/顺序/字符串）→ **NOT RECOMMENDED**。
1. **门 2 失败**（热路径数组 < 65,536 个元素/GPU，没有现实的批处理路径）→ **NOT RECOMMENDED**。
1. **任何 [R108](references/idioms-that-block.md#r108)（`mpi4py`）** → **SIGNIFICANT REFACTOR**（并行层重写是成本，不是淘汰）。
1. **多个 BLOCKS**（[R101](references/idioms-that-block.md#r101)–[R111](references/idioms-that-block.md#r111)）跨热路径 → **SIGNIFICANT REFACTOR**（计数不会超过这一点——每个 BLOCKS 都有一个记录的配方）。
1. **一个或两个可由配方修复的 BLOCKS**（例如 R101–R104 元素循环/同步）→ **LIGHT REFACTOR**。
1. **只有 REFACTOR 模式**（R201–R206）→ **LIGHT REFACTOR**；配方是机械的。
1. **无 BLOCKS，无 REFACTOR** → **READY**。
1. **清单中热路径上的 API 缺失** → 降低一个级别（SIGNIFICANT 保持 SIGNIFICANT，永远不会 NOT RECOMMENDED）。仅单 GPU 的 API 仅在多节点时重要。

**权衡发现*类型*，而不是它们的数量。** 热循环中的一个 R101 比十个 R001 更重要——它破坏了 R001 将提供的扩展性。相反，一堆 BLOCKS + R108 仍然是 SIGNIFICANT，而不是 NOT RECOMMENDED——层级衡量工程成本，而不是绝望。NOT RECOMMENDED 需要一个*大小*或*计算模式*失败。完整框架：[`references/decision-framework.md`](references/decision-framework.md)。

## 扩展与阻塞（一览）

- **SCALES**（保持不变）——向量化元素级，归约，矩阵乘法/einsum，`np.where`，每个 GPU 大型棋盘格切片 `arr[1:-1, 1:-1]`，`out=`，布尔掩码索引。
- **BLOCKS**（迁移前移除）——元素循环，`np.vectorize`，`for row in arr`，`.item()/.tolist()/bool(arr)` 在热循环中，循环中的归约 `if`/`while`，`arr[::2]`，`dtype=object`，`mpi4py`，`order=`，`min/max/sum(arr)`。
- **REFACTOR**（应用一个 [配方](references/refactor-recipes.md)) ——循环中分配，循环中 `x = x + y` 重新绑定，循环中 `vstack/hstack/concatenate`，`np.nonzero()` + 索引，`diag/flip/flatten` 的视图修改，热循环中的 `reshape`。
- **INFO**（成本注释，不是障碍）——SciPy 导入，仅单设备 `linalg.qr/svd`，单转换 `fft.*`，大小阈值 `linalg.solve/cholesky`。

完整分类在 [`idioms-that-scale.md`](references/idioms-that-scale.md) 和 [`idioms-that-block.md`](references/idioms-that-block.md) 中。静默忽略清单未列出的任何 API（上游表格的范围之外——标记它将是噪音）。

## 阅读顺序

规范、按顺序阅读的指南在 [`references/getting-started.md`](references/getting-started.md#must-read-references-in-order) 中——阅读一次以进行定向。

对于非平凡评估，必读的是 [`idioms-that-block.md`](references/idioms-that-block.md)、[`refactor-recipes.md`](references/refactor-recipes.md) 和 [`decision-framework.md`](references/decision-framework.md)；其余的（`[idioms-that-scale.md`](references/idioms-that-scale.md)、`[gpu-stack.md`](references/gpu-stack.md)、`[execution-model.md`](references/execution-model.md)、`[partitioning-and-balance.md`](references/partitioning-and-balance.md)、`[case-studies.md`](references/case-studies.md)）按需阅读。

## 限制

- **不运行 cuPyNumeric。** 无需运行时；这是预移植检查。实际加速测量发生在迁移后。
- **不自动生成重构代码。** 它识别要更改的内容并指向配方；用户（或后续代理）应用它们。
- **不分析工作负载。** 对于运行时测量使用 `legate.timing.time()` 和上游 [分析](https://docs.nvidia.com/cupynumeric/latest/user/profiling_debugging.html) 指南。
- **不取代判断。** 模式匹配遗漏了日志记录内部的隐式同步、隐藏 `.tolist()` 的装饰器、运行时数据依赖的分区不匹配。在边缘情况下，阅读源代码。

## 示例

捆绑的 `assets/examples/` 固定件的已处理评估（示例，不是模板）：

> **裁决：LIGHT REFACTOR。** `scales_well.py` 可以干净地转换；`needs_refactor.py` 需要一个分配提升；`blocks_scaling.py` 通过 `.item()` 每次迭代同步。
>
> **什么可以工作：** `scales_well.py:23-31`（棋盘格 R005），`:40-44`（归约 R002），`:18-22`（元素级 R001）。
> **什么会阻塞：** `blocks_scaling.py:51-58`（[R104](references/idioms-that-block.md#r104) — 热循环中的 `.item()`）→ [RR-sync](references/refactor-recipes.md#rr-sync)。
> **什么可以修复：** `needs_refactor.py:21-28`（[R201](references/idioms-that-block.md#r201) — 循环中分配）→ [RR-alloc](references/refactor-recipes.md#rr-alloc)。
> **下一步：** 应用配方；重新检查到 READY；在第一次真实运行时启用 `CUPYNUMERIC_DOCTOR=1`。

完整的已处理报告在 [`assets/sample_report.md`](assets/sample_report.md) 中。

## 权威上游参考

- **对比表**（`assets/api-support.md` 的来源）：https://docs.nvidia.com/cupynumeric/latest/api/comparison.html
- **最佳实践**、**Doctor**、**分析**、**与 NumPy 的差异**、**Legate 启动器**——在 https://docs.nvidia.com/cupynumeric/latest/ (`user/practices.html`、`user/doctor.html`、`user/profiling_debugging.html`、`user/differences.html`) 和 https://docs.nvidia.com/legate/latest/manual/usage/running.html
- **源代码**：https://github.com/nv-legate/cupynumeric

## 可用脚本

| 脚本 | 目的 | 参数 |
|---|---|---|
| `scripts/fetch_api_support.py` | 从上游对比表抓取到 `assets/api-support.md`。仅 Python 标准库；独立。源 URL 固定到 NVIDIA 文档对比页面的规范版本，不能覆盖。 | `--default-path`，`--from-file PATH`，`--out PATH`，`--print` |

用户运行此脚本来刷新清单（`python scripts/fetch_api_support.py --default-path`）。

## 捆绑的参考和资产

`references/` 文件在上述**必读阅读顺序**中枚举（R 代码范围：`idioms-that-scale.md` = R001–R007 / R301–R305；`idioms-that-block.md` = R101–R111 / R201–R206）。资产：`assets/api-support.md`（提交的 API 快照，在第 2 步中加载），`assets/sample_report.md` 和 `assets/examples/*.py`（已处理的报告和固定件）。

## 故障排除

| 症状 | 原因 | 修复 |
|---|---|---|
| `Fetched:` 行在清单中 > ~90 天 | 陈旧的快照 | 运行 `fetch_api_support.py --default-path`（用户运行） |
| 清单缺失或抓取器失败 | 上游 HTML 更改 | `WebFetch` [对比表](https://docs.nvidia.com/cupynumeric/latest/api/comparison.html) 以进行该评估 |
| 许多可修复的 BLOCKS 的 NOT RECOMMENDED | 应用启发式规则顺序错误 | 重新应用顺序：Gate 4 → Gate 2 → R108 → BLOCKS → REFACTOR；权衡*类型*，而不是数量 |
| 内核编写或迁移后分析 | 范围之外 | 拒绝并重定向（见“何时使用”）——无裁决 |
