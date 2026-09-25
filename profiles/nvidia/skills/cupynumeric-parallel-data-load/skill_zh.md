# 并行分片数据 -> cupynumeric 加载

**此技能存在的原因。** cupynumeric 映射了 NumPy 的数组 API，包括
`cupynumeric.load` 用于单个 `.npy` 文件。除此之外，文件 *加载* 生活
在 Legate 中，而不是 cupynumeric：

| 格式 | 内置加载器 |
|---|---|
| 单个 `.npy` | `cupynumeric.load(path)` (NumPy-API 对称性) |
| HDF5 (单个文件) | `legate.io.hdf5.from_file` / `from_file_batched` |
| 分片多文件 (任何格式)，Parquet/Arrow，原始二进制，自定义布局 | **没有内置加载器 — 此技能。** |

此技能展示了填充最后一行中空白的标准方法：
编写一个 Legate Python 任务，在任务体内调用所需格式的第三方读取器（`h5py`，`pyarrow`，`np.memmap`，...），并让 Legate 在 GPU / 节点之间分配读取。
对于具有内置加载器的格式，除非您需要在任务体内使用自定义加载器（基于 mmap 的加载器，特定于格式的解码器，侧车元数据，部分 / 分片读取），否则请优先使用它。

标准模式：**手动分区 + 手动任务启动，按机器大小而不是文件大小。** 只有轴 0 是分片的；尾随轴在每个瓦片内部一起运行。每个分片的行数可能跨文件不同（只有 `dtype` 和尾随轴必须匹配）；启动填充每个可用的处理器，而不管文件数量如何。

`.npy` 是示例，因为头信息在磁盘上携带形状和 dtype，但骨架适用于任何具有廉价范围/切片读取的格式（原始二进制，HDF5，Parquet/Arrow — 见下文“其他格式”）。参考实现：
[`assets/examples/parallel_npy_load.py`](assets/examples/parallel_npy_load.py)。

## 数据布局假设

此技能纯粹是关于 **加载** — 它假设数据已经以某种可预测、可索引的方式布置在共享文件系统上。
生成这些文件不在范围内（示例随附一个 `write` 子命令以方便使用，但真实用户会自带自己的）。

示例假设一种特定的布局：

- 一个包含名为 `shard_0000.npy`，`shard_0001.npy`，... 的目录，按连续整数序列（零填充宽度 4）命名。
- 所有分片共享相同的 `dtype` 和相同的尾随轴（`shape[1:]`）；**轴 0（每个分片的行数）可能跨文件不同** —
  该配方构建一个累积行偏移表，并在叶任务中读取每个文件的重叠切片。
- 目录对每个排名可见（多节点运行用于共享文件系统）。

示例的 `discover_layout()` 打印它发现的内容，并在布局错误时（缺少目录，没有分片，`dtype` / 尾随轴不匹配，或连续 `shard_NNNN.npy` 序列中的空白）以描述性错误硬失败。

如果您的数据位于不同的布局中 — 固定步长原始二进制，一个具有每个分片一个数据集的 HDF5 文件，目录树，... — 只有 glob 模式，每个文件的读取器（步骤 4 以下），和元数据发现（步骤 1 以下）会改变。分区和启动机制与布局无关。

## 何时使用

请参阅上面的格式表以进行路由决策（内置加载器与此技能）。除此之外，两个额外的线索表明此技能是正确的选择：

- 用并行每个 GPU 读取替换顺序 `np.concatenate([read(f) for f in files])`。
- 展示用户定义的 Legate Python 任务如何通过手动启动写入 cupynumeric 输出数组。

## 示例

以下路径是相对于此技能目录编写的（脚本位于 `assets/examples/parallel_npy_load.py`）。调整前缀以匹配您的技能安装位置（例如
`skills/cupynumeric-parallel-data-load/assets/...` 如果技能位于顶级 `skills/` 目录下）。

```bash
# 单节点，4 个 GPU。
legate --gpus 4 --fbmem 4000 --min-gpu-chunk 1 \
    assets/examples/parallel_npy_load.py \
    read --shard-dir /shared/scratch/demo
```

```bash
# 多节点，2 个节点 x 4 个 GPU（slurm），共享文件系统在 --shard-dir。
# 在排名 0 上生成分片一次，然后以任何规模重新运行 `read`。
legate --launcher srun --nodes 2 --cpus 1 \
    assets/examples/parallel_npy_load.py \
    write --shard-dir /shared/scratch/demo

legate --launcher srun --nodes 2 --ranks-per-node 4 \
    --gpus 4 --fbmem 4000 --min-gpu-chunk 1 \
    assets/examples/parallel_npy_load.py \
    read --shard-dir /shared/scratch/demo
```

没有布局标志 — 读取驱动器会遍历每个 `.npy` 头以恢复每个文件的行数，尾随形状，和 dtype，然后从可用处理器计数导出 `tile_rows`。

`--min-gpu-chunk 1` 只在每瓦片元素计数低于 Legate 对 GPU 启动的默认最小块大小时需要（例如，示例的默认值 — 总行数跨 4 个 GPU 分割，每个瓦片约为 `~1M` — 低于阈值，否则会被折叠到单个 GPU 上）。对于生产规模的数据集（每个瓦片数千万个元素或更大），您可以删除此标志并让 Legate 使用其默认值。将其提升到一个中等值（例如 `--min-gpu-chunk 1024`）是当每个瓦片足够大时，每个任务的开销比让 *每个* GPU 都有一个瓦片更重要。

## 说明

从 `.npy` 工作示例的五个步骤；只有步骤 1（解析格式头）和步骤 4（任务体内的每个文件读取器）是格式特定的。其他三个（分配目标，分区，栅栏）在格式之间重复使用 — 见“其他格式”以下用于交换点。

### 1. 从每个分片读取元数据

扫描目录并预览每个 `.npy` 头（`mmap_mode="r"` 仅读取头）。头信息包含每个分片的形状和 dtype，因此驱动器可以在从未加载数据的情况下恢复总行数，尾随形状，和累积行偏移表：

```python
paths = sorted(SHARD_DIR.glob("shard_*.npy"))

per_file_rows = []                       # 每个文件的轴 0 行数
trailing_shape = None                    # shape[1:], 必须跨文件匹配
dtype = None
for p in paths:
    hdr = np.load(p, mmap_mode="r")
    if trailing_shape is None:
        trailing_shape = tuple(hdr.shape[1:])
        dtype = hdr.dtype
    elif tuple(hdr.shape[1:]) != trailing_shape or hdr.dtype != dtype:
        raise RuntimeError(
            f"{p.name}: 尾随形状 / dtype 不匹配 "
            f"({hdr.shape[1:]}/{hdr.dtype} vs {trailing_shape}/{dtype})"
        )
    per_file_rows.append(int(hdr.shape[0]))

cum_rows = np.cumsum([0] + per_file_rows, dtype=np.int64)  # 长度 N+1
total_rows = int(cum_rows[-1])
```

上面的代码段强制执行跨文件匹配 `dtype` 和 `trailing_shape`（即 `shape[1:]`）。**每个分片的行数可以不同** — 累-行表处理这种情况。生产代码还应该验证名称形成连续的 `shard_0000.npy ... shard_NNNN.npy` 序列（为简洁起见，从代码段中省略；见 `worked example` 中的 `discover_layout()`）。发现仅依赖于磁盘格式本身暴露的内容（这里的 `.npy` 头，HDF5 的 `.shape` / `.dtype` 等）；任何侧车（清单，内容哈希）是单独的验证步骤。

### 2. 从元数据创建 cupynumeric 输出存储

总数组沿轴 0 扩展 `total_rows`；尾随轴来自 `trailing_shape` 不变。使用 `cn.empty` — 任务覆盖每个单元格，零初始化是浪费。

```python
import cupynumeric as cn

total_shape = (total_rows,) + trailing_shape
out = cn.empty(total_shape, dtype=dtype)
```

### 3. 按处理器数量瓦片存储

启动形状按 **可用处理器** 大小调整，而不是文件计数。选择 `tile_rows = ceil(total_rows / num_processors)` 并按该瓦片大小分区轴 0。尾随轴不会被分区（瓦片在那里跨越完整范围）。最后一个瓦片允许为短 — 这正是 `partition_by_tiling` 支持的 — 因此该配方不需要可除性约束。

```python
from legate.core import TaskTarget, get_legate_runtime
from legate.core.data_interface import as_logical_array

runtime = get_legate_runtime()
machine = runtime.get_machine()
num_processors = max(
    machine.count(TaskTarget.GPU),
    machine.count(TaskTarget.OMP),
    machine.count(TaskTarget.CPU),
    1,
)

tile_rows = max(1, (total_rows + num_processors - 1) // num_processors)
tile_shape = (tile_rows,) + trailing_shape
partition = as_logical_array(out).data.partition_by_tiling(tile_shape)

num_tasks = (total_rows + tile_rows - 1) // tile_rows  # 匹配分区瓦片计数
```

### 4. 定义叶任务并手动启动

`PATHS` 和 `CUM_ROWS`（步骤 1 中的文件路径和累积行偏移表）加上 `TILE_ROWS` 作为模块全局变量由驱动器在启动之前填充；控制复制在每个排名上运行驱动器，因此每个工作进程都看到相同的值。

每个任务首先构建其消费者视图（GPU 上的 cupy / CPU/OMP 上的 numpy），然后从 `view.shape[0]` 读取瓦片的实际行数 — `PhysicalStore` 本身没有 `.shape` 属性，因此必须通过视图进行 — 计算其全局行范围从其启动坐标和该行数，二分 `cum_rows` 以获取重叠文件，并将每个重叠文件切片复制到匹配的目标切片。注册 CPU、OMP 和 GPU 变体，以便在任何地方运行相同的启动而不变；`ctx.get_variant_kind()` 选择与 `OutputStore` 所在位置匹配的消费者（`cp.from_dlpack(dst)` 用于 FBMEM，`np.asarray(dst)` 用于 SYSMEM）。cupy 仅在 GPU 分支中导入，因此任务体在没有 cupy 的机器上加载。

```python
import bisect
from legate.core import TaskContext, VariantCode
from legate.core.task import OutputStore, task

@task(variants=(VariantCode.CPU, VariantCode.OMP, VariantCode.GPU))
def load_tile(ctx: TaskContext, dst: OutputStore) -> None:
    t = ctx.task_index[0]                              # 瓦片索引 0..num_tasks-1

    variant = ctx.get_variant_kind()
    if variant == VariantCode.GPU:
        import cupy as cp                              # 懒加载：仅在 GPU 上
        view = cp.from_dlpack(dst)
    else:
        view = np.asarray(dst)                         # 零拷贝 numpy 视图

    tile_rows_actual = view.shape[0]                   # 最后一个瓦片可能短
    row_start = t * TILE_ROWS                          # 全局轴-0 开始
    row_end = row_start + tile_rows_actual

    # 找到文件索引的半开范围，它们重叠 [row_start, row_end)。
    first_file = bisect.bisect_right(CUM_ROWS, row_start) - 1
    last_file = bisect.bisect_right(CUM_ROWS, row_end - 1) - 1

    for f in range(first_file, last_file + 1):
        # 瓦片 [row_start, row_end) 与文件 [cum[f], cum[f+1]) 的交集。
        lo = max(row_start, int(CUM_ROWS[f]))
        hi = min(row_end, int(CUM_ROWS[f + 1]))
        file_lo = lo - int(CUM_ROWS[f])
        file_hi = hi - int(CUM_ROWS[f])
        dst_lo = lo - row_start
        dst_hi = hi - row_start
        chunk = np.ascontiguousarray(
            np.load(PATHS[f], mmap_mode="r")[file_lo:file_hi]
        )
        if variant == VariantCode.GPU:
            view[dst_lo:dst_hi].set(chunk)             # cudaMemcpyAsync H2D
        else:
            view[dst_lo:dst_hi] = chunk                # 零拷贝 numpy 写入

manual_task = runtime.create_manual_task(
    load_tile.library,
    load_tile.task_id,
    (num_tasks,),                                      # 启动域 == 瓦片计数
)
manual_task.add_output(partition)
manual_task.execute()
```

两个消费者都通过 `PhysicalStore` 的原生生产者（`__dlpack__` for cupy，`__array_interface__` for `np.asarray`） — 本地瓦片的零拷贝视图。二分成本是 `O(log num_shards)`，内部循环通常迭代 1–2 次（瓦片最多重叠几个文件）。

### 5. 栅栏和验证

```python
get_legate_runtime().issue_execution_fence(block=True)
```

## 硬约束

1. **所有分片必须共享 `dtype` 和尾随轴 (`shape[1:]`)。**
   该配方沿轴 0 堆叠分片；目标尾随轴来自 `trailing_shape`，发现步骤将其锁定为第一个文件的价值。每个分片的行数（`shape[0]`）可以自由不同 — 累积偏移表处理它们。示例拒绝任何 `dtype` 或尾随形状与第一个文件不同的分片，并附带描述性错误。

2. **选择与变体匹配的消费者。** `cp.from_dlpack`
   拒绝驻留在 SYSMEM 中的存储；`np.asarray` 静默返回驻留在 FBMEM 中的存储的宿主视图，您无法通过它写入。根据 `ctx.get_variant_kind()` 分发，以便每个变体使用其自己的消费者 — 见步骤 4。

3. **mmap 视图不总是 C 连续** — 在 `.set()` 或 numpy 原地写入之前，用 `np.ascontiguousarray(arr[file_lo:file_hi])` 包装每个每个文件切片。

4. **多节点：`SHARD_DIR` 必须位于共享文件系统上。** 每个工作进程（在每个排名上）通过路径打开分片；节点本地 `/tmp` 路径仅适用于单节点演示。

## 变体

### 均匀分片快速路径（每个文件一个任务）

当每个分片已经具有相同的 `(shape, dtype)` 并且您恰好有 `num_shards` 处理器可用时，cum-rows / 二分机制是开销。设置 `tile_rows = shard_shape[0]` 和
`num_tasks = num_shards`；然后分区有一个瓦片每个文件，每个任务读取一个文件从头到尾（没有二分，没有内部循环）。驱动器端的切换是一行代码：

```python
if all(r == per_file_rows[0] for r in per_file_rows) and num_shards == num_processors:
    tile_rows = per_file_rows[0]
else:
    tile_rows = max(1, (total_rows + num_processors - 1) // num_processors)
```

相同的 `load_tile` 任务体在两种模式下仍然有效 — 内部循环恰好每个任务迭代一次。不需要为快速路径提供单独的任务体。

### 过度分解以获得更好的负载平衡

默认 `tile_rows = ceil(total_rows / num_processors)` 给每个处理器一个瓦片。要过度分解一个因子 `K`（更小的瓦片，更多的点任务，更细粒度的队列），而不是除以 `K * num_processors`：

```python
tile_rows = max(1, (total_rows + K * num_processors - 1) // (K * num_processors))
```

`num_tasks = ceil(total_rows / tile_rows)` 然后扩展到大约 `K * num_processors`。相同的任务体仍然有效 — 二分落在更多每个文件的任务上。

### 其他格式

只有 `load_tile` 内部的每个文件读取器会改变。读取器的契约：给定一个文件路径和沿轴 0 的半开行范围
`[file_lo, file_hi)`，返回一个形状为 `(file_hi - file_lo,) + trailing_shape` 的 numpy 数组，它可以变为 C 连续。
需要廉价的范围/切片读取 — 仅支持“读取整个文件”的格式会破坏部分重叠情况（一个瓦片只覆盖一个文件的一部分）。

| 格式 | 叶任务内的读取器 |
|---|---|
| **`.npy`** (工作示例) | `host = np.ascontiguousarray(np.load(p, mmap_mode="r")[file_lo:file_hi])` |
| **原始二进制** (固定形状) | `arr = np.memmap(p, dtype=DTYPE, mode="r", shape=(rows_in_file, *trailing_shape)); host = np.ascontiguousarray(arr[file_lo:file_hi])` |
| **HDF5** | `with h5py.File(p, "r") as f: host = np.ascontiguousarray(f["data"][file_lo:file_hi])` |
| **Parquet / Arrow** | `tbl = pq.read_table(p, columns=..., use_threads=False).slice(file_lo, file_hi - file_lo); host = tbl.to_pandas().values` |

(对于每个格式的内置单调用加载器，请参阅此文件顶部“此技能存在的原因”表。)

发现步骤（步骤 1）解析每个格式的元数据：`.npy` / HDF5 / Parquet 都在磁盘上携带每个文件的行数 + dtype。
原始二进制没有 — 侧车或从文件大小导出。

## 常见陷阱

### `cn.asarray(dst)` 在叶任务中非法

在 `@task` 身体内部，任何 cupynumeric 操作都会触及顶层运行时 — `cn.asarray(store)`，切片分配 `cn_dst[s] = host_np` — 触发从错误上下文中调用 `create_index_space` 并导致 Legion 中止：

```
LEGION API USAGE EXCEPTION: Invalid task context passed to runtime call
create_index_space
```

修复：在叶任务内部使用**第三方**库（cupy / torch / numpy）消耗 DLPack 胶囊。`cn.asarray` 在驱动器中是好的，但在叶任务中不是。见 `examples/dlpack/leaf_task_interop.py` 以获取 torch 风格的修复程序。

### 任务内 `assert` 中止运行时

Legion 将 `@task` 中未抛出的异常视为合同违规并中止，除非任务注册了 `throws_exception()`。在启动之前在主机上进行健全性检查。

### 启动域必须与分区瓦片计数匹配

`create_manual_task(launch_shape=...)` 和 `partition_by_tiling(...)` 是独立的 — 运行时不捕获不匹配。较大的启动域 → 越界瓦片；较小 → 未写入瓦片。始终通过两个独立的 `ceil` 分割从相同的 `(total_rows, tile_rows)` 导出两者（直接按 `num_processors` 调整的启动域会当 `num_processors > total_rows` 时过度启动）：

```python
tile_rows = max(1, (total_rows + num_processors - 1) // num_processors)
num_tasks = (total_rows + tile_rows - 1) // tile_rows
partition = ...partition_by_tiling((tile_rows,) + trailing_shape)
runtime.create_manual_task(load_tile.library, load_tile.task_id, (num_tasks,))
```
