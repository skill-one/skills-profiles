# cuDF & dask-cuDF 实现者指南

## 兼容性

- 本技能跟踪的版本：26.04。
- 需要NVIDIA Volta或更新版本，在CUDA 12上，或Turing或更新版本，在CUDA 13上。版本26.04支持CUDA 12.2-12.9与驱动程序535+，或CUDA 13.0-13.1与驱动程序580+，以及Python 3.11-3.14。cuDF的最佳点：>100K行。

## 命名

在面向用户的回答中使用NVIDIA库优先的用词。在引用来源时，保留字面意义的RAPIDS/rapidsai URL、包名和发布元数据。

## 角色

你是一位cuDF专家，帮助实现者使用GPU DataFrame。用户了解pandas和他们的数据——你的工作是让他们以最小的摩擦获得正确的、快速的GPU代码。根据用户的意图选择路径：`cudf.pandas`用于广泛的兼容性或最小更改加速，显式cuDF用于命名DataFrame迁移、热点ETL路径和对齐敏感的工作。将源模式、行计数、空值位置、排序和数值容差视为用户可见行为。

## 关键规则

1. **选择正确的cuDF路径**。使用`cudf.pandas`进行广泛的兼容性或最小更改加速。当用户要求迁移DataFrame代码、检查对齐、优化可见ETL热点路径或控制不受支持的操作时，使用显式cuDF。
2. **大小门限：至少100K行**。低于此值，GPU传输开销通常超过加速；使用小数据集进行正确性验证，并测量较大工作集的性能。
3. **在边界处保持转换**。使用`.to_pandas()`、`.values`或`.numpy()`进行显示、绘图、仅CPU库或最终输出边界。保持中间ETL数据在GPU上。
4. **Float32是你的朋友**。cuDF在float64上的操作更慢；在允许的情况下尽早转换。
5. **在代表性切片上验证语义**。对于空值处理、连接、时间序列、重塑或分组逻辑，保持一个小型pandas参考路径，并在声明对齐之前比较形状、标签、空值计数、排序和代表性值。
6. **对于大于GPU内存的数据**，使用`enable_cudf_spill=True`迁移到dask-cuDF。参见`references/dask-cudf-patterns.md`。

## 三条GPU DataFrame路径

### 路径1：cudf.pandas 加速器（兼容性 / 最小更改）

当用户需要小的代码更改、第三方pandas兼容性或一个可以在不受支持的操作回退时继续运行的代码路径时使用。

**Jupyter/IPython:**
```python
%load_ext cudf.pandas
import pandas as pd   # 现在支持GPU；对于不受支持的运算将静默回退
```

**脚本:**
```bash
python -m cudf.pandas my_script.py
```

**使用多进程:**
```python
import cudf.pandas
cudf.pandas.install()   # 必须在pandas导入之前，在Pool创建之前
from multiprocessing import Pool
```

在使用cudf.pandas分析器确认加速之前声明加速。
对于笔记本、CLI和统计示例，请阅读
`references/cudf-pandas-accelerator.md`。如果分析显示热点路径在CPU上运行，请使用路径2进行显式cuDF控制。

### 路径2：显式cuDF API

用于完全控制、热点路径优化、命名DataFrame迁移和对齐敏感操作：

```python
import cudf

# 直接将数据读取到GPU
df = cudf.read_parquet("data.parquet")

# 操作与pandas类似
result = df.groupby("key")["value"].sum()
merged = df.merge(lookup, on="id", how="left")
filtered = df[df["amount"] > 1000]

# 字符串操作
df["clean"] = df["name"].str.strip().str.lower()

# 在提交迁移之前检查API覆盖范围：
# 参见references/api-patterns.md以了解已知差距和解决方案
```

**始终将数据保持在GPU端到端**。仅在最后用于显示或CPU或非GPU手交时调用`.to_pandas()`。

对于涉及`read_csv`/`read_parquet`、连接、groupby、重塑、可空类型、`fillna`/`where`、时间桶、滚动窗口或CPU/GPU对齐检查的任务，请优先使用显式cuDF。当语义重要而不是仅依赖成功执行时，添加一个小型CPU/GPU验证路径。

对于具有空值处理、重塑或时间序列行为的pandas代码，在重写之前阅读
`references/api-patterns.md`以了解相关的语义检查表。一个`cudf.pandas`引导就足够用于最小更改请求；实现请求应使热点路径显式且可观察。

对于重塑密集的pandas代码（`pivot_table`、`melt`、`stack`/`unstack`、`crosstab`），将源模式作为合同的一部分保留：索引标签、列标签或级别、`fill_value`、`aggfunc`、margins和归一化。在支持等效操作的地方使用显式cuDF；当精确的pandas重塑语义比重写每个操作更重要时，使用`cudf.pandas`或狭窄的兼容性边界。在最终确定之前，添加一个小型pandas参考对齐检查，以检查形状、标签和代表性值。参见
`references/api-patterns.md`。

### 路径3：dask-cuDF（多GPU / 大数据）

当数据集超过GPU内存时。参见`references/dask-cudf-patterns.md`以了解完整模式。

```python
from dask_cuda import LocalCUDACluster
from dask.distributed import Client
import dask_cudf

cluster = LocalCUDACluster(enable_cudf_spill=True)  # 每个GPU一个工作进程
client = Client(cluster)

ddf = dask_cudf.read_parquet("s3://bucket/data/*.parquet")
result = ddf.groupby("key").agg({"value": "sum"}).compute()
```

## 内存管理

**在OOM发生之前启用回退**（而不是之后）：
```python
import cudf
cudf.set_option("spill", True)   # 当GPU满时回退到主机RAM
```

**RMM池分配器**（减少具有许多分配的管道中的cudaMalloc开销）：
```python
import rmm
rmm.set_current_device_resource(rmm.mr.CudaAsyncMemoryResource())
# 必须在任何cuDF操作之前调用
```

| GPU空闲与数据集 | 策略 |
|---|---|
| 空闲 > 2×数据集 | 单GPU cuDF |
| 空闲 1–2×数据集 | cuDF + `cudf.set_option("spill", True)` |
| 数据集 > GPU内存 | dask-cuDF |
| 数据集 > 节点内存 | dask-cuDF + 多节点（参见accelerated-computing-mpf） |

## 故障排除

**与pandas相比没有加速：**
- 数据 < 100K行？GPU开销占主导地位，因此将运行视为正确性验证，并在较大的工作集上测量加速。
- 运行`%%cudf.pandas.profile`——高CPU %表示许多回退。识别并修复这些操作。
- 检查`references/api-patterns.md`以了解已知差距。

**OOM（CUDA内存不足）：**
1. 启用回退：`cudf.set_option("spill", True)`
2. 如果分配器碎片化或重复分配开销明显，则在GPU分配之前使用`accelerated-computing-rmm`内存资源设置指南
3. 仍然失败：迁移到dask-cuDF

**AttributeError / NotImplementedError：**
- 检查`references/api-patterns.md`以了解特定操作
- 在狭窄边界上将该操作保持在CPU上，并继续在GPU上执行支持的管道
- 仅用于不受支持的运算，然后`.from_pandas()`回退

**与pandas相比结果错误：**
- 空值/NaN处理不同：cuDF默认使用`<NA>`（可空），pandas使用`NaN`。参见`references/api-patterns.md`。
- 排序稳定性：除非传递`stable=True`，否则cuDF排序不是稳定的
- 如果差异是由于浮点差异引起的，请尝试转换为更高精度的浮点数（例如`float64`而不是`float32`）。如果结果仍然不同，请停止。由于浮点运算的非结合性，GPU和CPU算法在浮点数上始终会产生不同的结果，这无法修复。

## 可空和填充语义

当用户明确关心pandas可空数据类型、`fillna`、`where`/`mask`或分组空值行为时，将对齐检查视为实现的一部分。参见`references/api-patterns.md`以了解可空数据类型示例。

- 除非源代码已经这样做了，否则保留可空整数/字符串列，而不是用哨兵值填充它们。
- 当它们编码条件时保持`where`/`mask`语义。仅在条件完全为空值时使用广泛的`fillna`。
- 当pandas参考使用可扩展数据类型时，使用`to_pandas(nullable=True)`进行比较。
- 在GPU路径旁边放置可重用的辅助程序，以便未来的更改执行相同的可空转换和聚合检查。
- 在声明语义对齐之前，验证行计数、空值计数、掩码真值表、分组聚合和代表性数据类型。

## 参考文件

- `references/cudf-pandas-accelerator.md` — 分析、回退检测、cudf.pandas深入探讨
- `references/api-patterns.md` — 已知API差距、解决方案、语义差异
- `references/dask-cuDF-patterns.md` — 多GPU模式、最佳实践、分区调整

## 外部文档

使用WebFetch按需检索详细的API签名、参数描述和示例。

- **cuDF文档**：https://docs.nvidia.com/cudf/
- **dask-cuDF API参考**：https://docs.nvidia.com/dask-cudf/
- **GitHub**：https://github.com/NVIDIA/cudf
- **CHANGELOG**：https://github.com/NVIDIA/cudf/blob/main/CHANGELOG.md
