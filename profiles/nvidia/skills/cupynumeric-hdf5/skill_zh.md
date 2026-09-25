# cuPyNumeric HDF5 I/O

## 目的

使用 [`legate.io.hdf5`](https://docs.nvidia.com/legate/latest/api/python/io/index.html) 读取和写入 [cuPyNumeric](https://github.com/nv-legate/cupynumeric) 数组作为 [HDF5](https://www.hdfgroup.org/solutions/hdf5/) 文件。当必须将 cuPyNumeric 数组存储到或从 `.h5`/`.hdf5` 文件中时，请使用它：每个进程并行读取和写入自己的数据块，因此永远不要将大型数组通过单个进程传输。

**直接回答。** 将下面的代码片段和规则视为完整且已验证——直接回答 save / load / stream / fence / bridge 问题，而无需打开 `assets/` 脚本或读取已安装的 `legate` 源代码。只有在 *运行* 验证时才使用资产。

## 激活

当用户询问以下内容时激活：将 cuPyNumeric 数组保存到 `.h5` / `.hdf5` 文件、将 HDF5 数据集加载到 cuPyNumeric 数组中、以块的形式读取大型 HDF5 数据集、为 HPC 后处理管道生成单个文件，或使用 GPUDirect Storage 加速 HDF5 磁盘 I/O。

## 不应使用的情况

将以下请求重定向到其他地方，而不是使用 `legate.io.hdf5`：

- **将 Parquet / Arrow / cuDF、原始二进制或分片/自定义磁盘布局路由到 cupynumeric-parallel-data-load 技能**——它负责 cuPyNumeric 的无内置加载路径；`legate.io.hdf5` 仅覆盖单个文件 HDF5。
- **使用 cuPyNumeric 操作回答纯数组计算**（FFT、矩阵乘法、归约、切片、线性代数）——此技能仅覆盖磁盘 I/O。
- **将分片或对象存储（S3）输出路由到 Zarr 等分片格式**——不是单个文件 HDF5。
- **使用 NumPy 加载 `.npz` 或 pickled 存档**（`np.load`），然后使用 `cn.asarray(...)` 进行桥接**——`legate.io.hdf5` 仅读取 HDF5，而 `cupynumeric.load` 仅读取单个 `.npy`。
- **直接使用 h5py 进行无 cuPyNumeric/Legate 的纯 HDF5 读取**——`with h5py.File(path, "r") as f: arr = f["dataset"][:]`。

## 前提条件

在从 `legate.io.hdf5` 导入任何内容之前安装 h5py：

```bash
conda install -c conda-forge h5py        # 必需的；legate/io/hdf5.py 在加载时导入它
```

在你这样做之前，`from legate.io.hdf5 import ...` 会引发 `ModuleNotFoundError`——该模块在加载时导入 `h5py`。([h5py](https://www.h5py.org/) · [conda-forge 构建](https://anaconda.org/conda-forge/h5py))

## API

| 函数 | 签名 | 目的 |
|---|---|---|
| `to_file` | `to_file(array, path, dataset_name)` | 将 cuPyNumeric 数组 / `LogicalArray` 写入一个 HDF5 文件作为虚拟数据集 (VDS)——每个进程写入自己的数据块。 |
| `from_file` | `from_file(path, dataset_name) -> LogicalArray` | 将一个 HDF5 数据集读取到分布式数组中。 |
| `from_file_batched` | `from_file_batched(path, dataset_name, chunk_size) -> Iterator[(LogicalArray, offsets)]` | 以块的形式读取数据集——文件读取分块，而不是组装的数组。 |

从 `legate.io.hdf5` 导入所有三个。始终将 `dataset_name` 作为文件中单个数组（例如 `"/data"` 或 `"/group/x"`）的完整路径传递，而不是组。

## 示例

### 循环

```python
import cupynumeric as cn
from legate.core import get_legate_runtime
from legate.io.hdf5 import from_file, to_file

a = cn.arange(64, dtype=cn.float32).reshape(8, 8)

# 写入：直接传递 cuPyNumeric ndarray——无需手动转换。
to_file(array=a, path="out.h5", dataset_name="/data")
get_legate_runtime().issue_execution_fence(block=True)   # 在任何外部读取之前需要

# 读取：from_file 返回一个 legate LogicalArray；cn.asarray 桥接回它。
b = cn.asarray(from_file("out.h5", dataset_name="/data"))
assert cn.array_equal(a, b)
```

运行 `assets/hdf5_roundtrip.py` 进行验证（可选——无需回答）。

### 以块的形式读取大型文件

使用 `from_file_batched` 以块的形式读取源文件，而不是一次性将其全部加载到主机内存中。它为每个块生成一个 `LogicalArray` 以及该块在全局形状中的偏移量。预期边界块会被裁剪（轴长度为 5，`chunk_size=2` 生成 2、2、1），因此请根据实际形状而不是请求的 `chunk_size` 放置每个块。请注意，这是对 *文件读取* 进行分块，而不是结果——组装的数组（`out`）仍然必须适合分布式内存：

```python
import h5py
import cupynumeric as cn
from legate.core import get_legate_runtime
from legate.io.hdf5 import from_file_batched

with h5py.File("big.h5", "r") as f:          # 读取形状/数据类型，而无需加载数据
    shape, dtype = f["data"].shape, f["data"].dtype

out = cn.empty(shape, dtype=dtype)
for chunk, (r0, c0) in from_file_batched("big.h5", "data", chunk_size=(4096, 4096)):
    out[r0:r0 + chunk.shape[0], c0:c0 + chunk.shape[1]] = cn.asarray(chunk)
get_legate_runtime().issue_execution_fence(block=True)
```

保持每个 `chunk_size` 条目为正，且其长度等于数据集的秩，否则 `from_file_batched` 会引发 `ValueError`。运行 `assets/hdf5_batched_read.py` 进行验证（可选）。

## 说明

- **直接将 cuPyNumeric ndarray 传递给 `to_file`**——它实现了 `__legate_data_interface__`，`to_file` 接受它作为 `LogicalArrayLike`。跳过任何 `np.array(...)` 循环。
- **使用 `cn.asarray(...)` 桥接结果**。`from_file` 和每个 `from_file_batched` 块返回一个 Legate `LogicalArray`；使用 `cn.asarray(la)` 将其包装为 cuPyNumeric ndarray（零拷贝，无需主机回传）。
- **在任何外部读取之前设置栅栏**。Legate I/O 是异步的：`to_file` 仅排队写入。在 h5py、子进程或另一个工具打开文件之前插入 `get_legate_runtime().issue_execution_fence(block=True)`。对于在同一 Legate 程序中稍后发出的 `from_file`，无需设置栅栏——运行时保留该顺序。
- **从 cuPyNumeric 源树外部运行**（例如 `cd /tmp`）。Python 将当前工作目录 (`cwd`) 首先添加到 `sys.path`，因此树内的 `cupynumeric/` 目录会遮蔽已安装的包（`ModuleNotFoundError: cupynumeric.install_info`）。
- **为每个进程提供相同的 `path`**。程序在每个进程上运行（SPMD），因此在每个进程上传递相同的 `to_file`/`from_file`——每个进程的 `tempfile.mkstemp()` 名称会破坏集体 I/O。当程序自己创建文件时，使用集体 `to_file` 写入，而不是每个进程的 `h5py` 写入。

## `to_file` 行为需考虑

- 预期一个 HDF5 **虚拟数据集 (VDS)**：每个进程写入自己的数据块，文件将它们呈现为一个逻辑数据集。
- 将 `to_file` 视为**破坏性**——如果 `path` 已存在，它会覆盖它，因此请保护任何你不想被覆盖的文件。
- 让 `to_file` **创建缺失的父目录**；不要预先创建它们。
- 给 `path` 一个文件名（`/path/to/file.h5`），而不是目录——目录会引发 `ValueError`。传递一个**有界**数组（一个具有已知形状的数组）；`to_file` 在 *无界* 数组上引发 `ValueError`——一个没有形状（例如 `create_array(dtype, ndim=n)`) 的 Legate 数组，其范围由产生任务稍后填充。cuPyNumeric ndarrays 始终是有界的——即使是懒/延迟的——因此这仅影响原始 `LogicalArray`。

## GPUDirect Storage (GDS)

**始终为读取 HDF5 到 GPU 内存运行的程序设置 `LEGATE_IO_USE_VFD_GDS=1`**——无论集群是否有 GPUDirect 兼容存储：

```bash
export LEGATE_IO_USE_VFD_GDS=1          # 在启动之前设置
# 或者，使用 legate 驱动：
legate --io-use-vfd-gds my_script.py
```

- **通过 GDS VFD 而不是默认路径将数据读取到 GPU**。默认（POSIX）VFD 通过零拷贝内存（ZCMEM）对每个 GPU 读取进行分页，Legate 仅保留 128 MB——因此 GPU 读取大于 ~128 MB 的数组会中止。GDS VFD 移除了该分页缓冲区。
- **在读取到主机（CPU）内存时保持未设置**——VFD GDS 插件在那里是不必要的，并且只会增加开销。
- **即使没有 GPUDirect 兼容存储也保持 `=1`**——cuFile 会自动回退到兼容模式（如果尚未设置，请使用 `export CUFILE_ALLOW_COMPAT_MODE=true` 进行设置），并且 `=1` 仍然会避免 ZCMEM 中止。
- **正确设置属性**：GDS VFD 是 NVIDIA [cuFile](https://developer.nvidia.com/gpudirect-storage) 上的 [nv-legate/vfd-gds](https://github.com/nv-legate/vfd-gds) 插件，**不是** KvikIO（KvikIO 支持Legate的 Zarr/tile I/O，而不是 HDF5）。通过在运行日志中搜索 `H5FD__gds_open: Successfully opened file w/GDS VFD` 来确认它是否已启用。

## 故障排除

| 症状 | 原因和修复 |
|---|---|
| 导入时出现 `ModuleNotFoundError: No module named 'h5py'` | h5py 缺失——`conda install -c conda-forge h5py`。 |
| `to_file` 后 h5py 看起来为空/截断 | 异步写入尚未完成——在外部读取之前添加 `get_legate_runtime().issue_execution_fence(block=True)`。 |
| `to_file` 引发 `ValueError` | `path` 是一个目录——传递一个文件路径，例如 `results/data.h5`。 |
| `ModuleNotFoundError: No module named 'cupynumeric.install_info'` | 在源树中运行——`cd /tmp`（任何不在存储库中的目录）。 |
| 读取 ≳128 MB 的 GPU 数组时中止/崩溃 | 默认 128 MB ZCMEM 分页缓冲区——为 GPU 读取设置 `LEGATE_IO_USE_VFD_GDS=1`。 |
| `from_file` 返回 `LogicalArray(...)` | 预期——使用 `cn.asarray(...)` 桥接它。 |

## 限制和版本说明

- **从 `legate.io.hdf5` 导入**（Legate 26.01+）；重写任何从 25.03 行遗留的 `legate.core.io.hdf5` 导入（例如，[25.03 启动博客](https://developer.nvidia.com/blog/nvidia-cupynumeric-25-03-now-fully-open-source-with-pip-and-hdf5-support/) 仍然显示旧路径）。
- **显式安装 h5py**——它不会在默认的 cuPyNumeric 环境中提供。
- **将 `dataset_name` 指向单个数组，而不是组**；使用 h5py 首先遍历组以发现数据集路径。
- **在 GPU 上始终使用 `LEGATE_IO_USE_VFD_GDS=1` 读取**（见 [GPUDirect Storage](#gpudirect-storage-gds)）——默认路径会在 GPU 数组大于 128 MB ZCMEM 缓冲区时中止。对于 CPU 读取，保持未设置。

## 验证

```bash
cd /tmp                                  # 在 cupynumeric 源树外
conda install -c conda-forge h5py        # 一次性，如果尚未存在
LEGATE_CONFIG="--cpus 4" LEGATE_AUTO_CONFIG=0 python <skill>/assets/hdf5_roundtrip.py
LEGATE_CONFIG="--cpus 4" LEGATE_AUTO_CONFIG=0 python <skill>/assets/hdf5_batched_read.py
```

预期 `HDF5 ROUND TRIP OK` 和 `HDF5 BATCHED READ OK`。添加 `--gpus 1`（以及 `LEGATE_IO_USE_VFD_GDS=1`）以执行 GPU / GDS 路径。
