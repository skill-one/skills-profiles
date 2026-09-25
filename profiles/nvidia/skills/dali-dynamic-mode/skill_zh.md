# DALI 动态模式

## 目的

指导 AI 代理编写、审查和迁移使用 DALI 命令式动态模式 API `nvidia.dali.experimental.dynamic` (`ndd`) 的代码。

## 指令

- 将动态模式导入为 `nvidia.dali.experimental.dynamic as ndd`，并在普通 Python 中以直接 `ndd` 调用的方式编写代码；不要使用管道模式 API，例如 `Pipeline`、`@pipeline_def`、`pipe.build()` 或 `pipe.run()`。
- 将读者视为有状态对象：创建一次，跨多个时期重用，并将 `batch_size` 传递给 `next_epoch(...)`。
- 向随机操作传递显式的 `batch_size`；没有可继承的管道级批处理大小。
- 使用动态模式 API 约定：使用 `device="gpu"` 而不是管道模式的 `"mixed"`，使用 `Batch.tensors[...]` 进行样本选择，以及使用 `Batch.slice[...]` 进行每个样本的切片。
- 使用 `.torch()` 将张量或批处理转换为 PyTorch 张量。对于具有可变形状的批处理，使用 `pad=True`。

## 前置条件

- 要运行或验证代码，必须安装 NVIDIA DALI，并且动态模式可以导入为 `nvidia.dali.experimental.dynamic`。
- GPU 解码或 GPU 操作需要 CUDA 兼容的 DALI 构建，并且需要可用的 NVIDIA GPU/驱动程序。
- 框架转换示例需要安装目标框架，例如用于 `.torch()` 的 PyTorch。

## 简介

动态模式是 DALI 的命令式 Python API。它允许代码从正常的 Python 控制流中直接调用 DALI 操作符，而不是构建和运行管道图。

## 核心数据类型

### 张量 -- 单个样本

```python
t = ndd.tensor(data)           # 复制
t = ndd.as_tensor(data)        # 包装，如果可能则不复制
t.cpu()                        # 移动到 CPU
t.gpu()                        # 移动到 GPU
t.torch(copy=False)            # 转换为 PyTorch 张量，不复制（默认）
t[1:3]                         # 支持切片
np.asarray(t)                  # 通过 __array__ 的 NumPy（仅限 CPU）
```

支持 `__dlpack__`、`__cuda_array_interface__`、`__array__`、算术运算符。

### 批处理 -- 样本集合（支持可变形状）

```python
b = ndd.batch([arr1, arr2])    # 复制
b = ndd.as_batch(data)         # 包装，如果可能则不复制
```

**批处理没有 `__getitem__`** -- `batch[i]` 会引发 `TypeError`，因为索引是模糊的（样本选择与每个样本的切片）。请使用显式 API：

| 意图 | 方法 | 返回值 |
|------|------|-------|
| 获取样本 i | `batch.tensors[i]` | `Tensor` |
| 获取样本子集 | `batch.tensors[slice_or_list]` | `Batch` |
| 在每个样本内切片 | `batch.slice[...]` | `Batch`（相同的 batch_size） |
| 样本级切片 | `batch.slice[batch_of_indices]` | `Batch`（相同的 batch_size） |

`.tensors[]` 选择**哪些样本**。`.slice` 索引**每个样本内部**。

```python
xy = ndd.random.uniform(batch_size=16, range=[0, 1], shape=2)
crop_x = xy.slice[0]       # 批处理中的 16 个标量，每个样本的第一个元素
crop_y = xy.slice[1]       # 批处理中的 16 个标量，每个样本的第二个元素
sample_0 = xy.tensors[0]   # 张量，整个第一个样本 [x, y]
```

### 高级切片

`.slice[]` API 接受索引批处理，允许用户混合和匹配批处理和标量值，例如：

```python
imgs = ndd.imread(filenames)  # 一批图像，如果 `filenames` 是一个列表
sliced = imgs.slice[
    42 :  # 范围开始对所有样本广播
    ndd.batch(imgs.shape).slice[0] // 2  # 每个样本的范围结束（每个图像的一半）
]
```

**PyTorch 转换：**
- `batch.torch()` -- 适用于均匀形状；对于锯齿形批处理会引发错误
- `batch.torch(pad=True)` -- 将锯齿形批处理零填充到最大形状（用于可变长度的音频、检测框等）
- `batch.torch(copy=None)` 是默认值（如果可能则避免复制）
- 批处理没有 **`__dlpack__`** -- 首先使用 `ndd.as_tensor(batch)` 为 DLPack 消费者提供。`ndd.as_tensor` 也支持 `pad`。
- `Tensor.torch(copy=False)` 是默认值（不复制）

**迭代：** `for sample in batch:` 会生成张量。

## 读者

读者是**有状态对象** -- 创建一次，跨多个时期重用。这很重要，因为读者跟踪内部状态，如洗牌顺序和分片位置。

```python
reader = ndd.readers.File(file_root=image_dir, random_shuffle=True)

for epoch in range(num_epochs):
    for jpegs, labels in reader.next_epoch(batch_size=64):
        # jpegs, labels 是 Batch 对象
        ...
```

要点：
- 读者输出（jpegs、labels 等）是**CPU** 张量/批处理。标签通常保持在 CPU 上，直到你为你的框架转换它们（例如 `labels.torch().to(device)`）。
- 读者类是**PascalCase**：`ndd.readers.File(...)`、`ndd.readers.COCO(...)`、`ndd.readers.TFRecord(...)`
- `batch_size` 传递给 `next_epoch()`，而不是传递给读者构造函数
- `next_epoch(batch_size=N)` 生成 `Batch` 元组的元组；`next_epoch()` 不带 `batch_size` 会生成 `Tensor` 元组的元组
- 从 `next_epoch()` 返回的迭代器必须在使用 `next_epoch()` 之前完全消耗
- 一旦读者使用给定的 `batch_size`，就不能更改。类似地，在批处理模式下使用的读者不能切换到样本模式或反之亦然。

分布式训练的分片读取：
```python
reader = ndd.readers.File(
    file_root=image_dir,
    shard_id=rank, num_shards=world_size,
    stick_to_shard=True,
    pad_last_batch=True,
)
```

## 设备处理

- 设备是从输入**推断的** -- 如果任何输入在 GPU 上，则为 GPU
- 对于混合解码：使用 `device="gpu"`（**不是** `"mixed"`）。`"mixed"` 关键字是管道模式的概念，用于隐式 CPU 到 GPU 的传输；在动态模式下，传递 `device="gpu"` 会触发相同的硬件加速解码路径。
- 在传递给 GPU 模型之前不要调用 `.cpu()` -- `.torch()` 会直接给你 GPU 张量。`.cpu()` 仅当消费者需要主机内存（numpy、`__array__`）时才需要。
- DALI 和 PyTorch 之间的 CUDA 流同步是**通过 DLPack 自动进行的** -- 无需手动流管理。

## 执行模型

默认模式是 `eager` -- 在后台线程中异步执行，立即返回。

**大多数情况下不需要 `.evaluate()`。** 任何数据消耗（`.torch()`、`__dlpack__`、`__array__`、`.shape`、属性访问、迭代）会自动触发评估。

对于调试，切换到同步模式，以便错误在调用位置而不是异步队列中稍后出现：

```python
with ndd.EvalMode.sync_cpu:
    images = ndd.decoders.image(jpegs, device="gpu")
    images = ndd.resize(images, size=[224, 224])
    # 错误在这里出现，在失败的运算符的确切位置
```

模式（同步性递增）：`deferred` < `eager` < `sync_cpu` < `sync_full`

使用 `EvalMode.sync_full` 进行调试，而不是分散 `.evaluate()` 调用 -- 它更干净，可以一次性捕获所有问题。`sync_cpu` 通常足够，比 `sync_full` 轻量级。

## 线程配置

```python
ndd.set_num_threads(4)  # 启动时调用一次，如果需要覆盖默认值
```

控制 DALI 的内部工作线程用于 CPU 运算符。默认值为 CPU 亲和力计数或 `DALI_NUM_THREADS` 环境变量。与 Python 级别的线程无关。

## 随机数生成器

两种方法（使用一种，不要同时使用）：

```python
# 方法 1：设置线程本地默认种子（简单，对大多数情况足够）
ndd.random.set_seed(42)
angles = ndd.random.uniform(batch_size=64, range=(-30, 30))

# 方法 2：显式 RNG 对象（更精细的控制，将 rng= 传递给每个操作）
rng = ndd.random.RNG(seed=42)
values = ndd.random.uniform(batch_size=64, range=[0, 1], shape=2, rng=rng)
```

当向随机操作传递 `rng=` 时，显式 RNG 会覆盖默认种子。线程本地：每个线程都有独立的随机状态。

随机操作在处理批处理时需要显式的 `batch_size` -- 没有可继承的管道级批处理大小。

## 检查点

动态模式没有**管道级检查点**。检查点聚合单个有状态对象的状态：读者和 `RNG` 实例。无状态操作（解码器、resize、rotate、normalize、...）不是检查点的一部分。

```python
ckpt = ndd.checkpoint.Checkpoint()
ckpt.register(reader, "my_reader")
ckpt.register(rng, "rng")

# ... 迭代一段时间 ...

ckpt.collect()                       # 快照注册的对象
ckpt.save("ckpt_{seq:04d}.json")     # 写入 ckpt_0000.json, ckpt_0001.json, ...
```

恢复是对称操作 -- 构建一个*新的*读者和 `RNG`，然后 `load` + `register`。加载的状态会在 `register` 时应用于每个对象：

```python
reader = ndd.readers.File(file_root=..., enable_checkpointing=True, name="my_reader")
rng = ndd.random.RNG()

ckpt = ndd.checkpoint.Checkpoint()
ckpt.load("ckpt_{seq:04d}.json")     # 选择最高序列号
ckpt.register(reader, "my_reader")   # 状态在这里应用
ckpt.register(rng, "rng")            # 同样

for batch in reader.next_epoch(batch_size=N):
    ...  # 在检查点迭代后生成下一个批处理
```

关键规则：

- **读者必须选择加入。** 构造时使用 `enable_checkpointing=True`。在未启用的情况下注册已经迭代的读者会引发 `RuntimeError`；如果读者尚未迭代，`register` 会使其逆序启用。
- **读者状态必须在第一次 `next_epoch` 调用之前应用。** 预取线程在第一次迭代时开始，快照队列在之后锁定。在已经迭代的读者上使用 `set_state`（或从加载的检查点中的 `register`）会引发 `RuntimeError`。
- **`enable_checkpointing=True` 与 `compile=True` 不兼容。** 在启用了检查点的读者上调用 `reader.next_epoch(..., compile=True)` 会引发 `NotImplementedError`。
- **命名注册更安全。** 匿名 `register(op)` 使用顺序键（`__op_0`、`__op_1`、...），因此保存和恢复之间的注册顺序必须匹配。类型标签可以捕获跨类型的交换，但不能交换兼容类型。优先使用 `register(op, name)`。
- **`ndd.checkpoint.current()`** 返回绑定到当前线程本地 `EvalContext` 的 `Checkpoint`。它在调用之间共享 -- 如果要为不相关的运行重用默认上下文，请调用 `ckpt.clear()`。
- **文件名模式：** `save`/`load` 接受一个带有单个 `{seq}` 占位符的 Python 格式字符串（例如 `"ckpt_{seq:04d}.json"`）。`save` 选择下一个空闲序列；`load` 选择磁盘上最高匹配的序列。
- **格式版本是严格的。** `deserialize` 会拒绝来自不同检查点格式版本的负载 -- 没有自动升级。
- **不是线程安全的。** 每个线程一个 `Checkpoint`。

手动 `get_state` / `set_state` 也可以直接在每个 `Reader` 和 `RNG` 上使用 -- `Checkpoint` 聚合器是构建在其之上的。仅在集成外部检查点系统时使用手动 API。

## 示例

### 图像分类管道

```python
import nvidia.dali.experimental.dynamic as ndd

reader = ndd.readers.File(file_root="/data/imagenet/train", random_shuffle=True)

for epoch in range(num_epochs):
    for jpegs, labels in reader.next_epoch(batch_size=64):
        images = ndd.decoders.image(jpegs, device="gpu")
        images = ndd.resize(images, size=[224, 224])
        images = ndd.crop_mirror_normalize(
            images,
            mean=[0.485 * 255, 0.456 * 255, 0.406 * 255],
            std=[0.229 * 255, 0.224 * 255, 0.225 * 255],
        )
        train_step(images.torch(), labels.torch())
```

## 常见错误

| 错误 | 正确 | 原因 |
|-------|-------|-----|
| `device="mixed"` | `device="gpu"` | `"mixed"` 仅适用于管道模式 |
| `batch[i]` | `batch.tensors[i]` | `Batch` 没有 `__getitem__` |
| `batch.tensors[0]` 用于每个样本的切片 | `batch.slice[0]` | `.tensors` 选择样本；`.slice` 在每个样本内切片 |
| 每个操作后 `.evaluate()` | 让消耗触发评估 | `.torch()`、`.shape` 等。会自动触发它 |
| GPU 模型之前 `.cpu()` | 直接 `.torch()` | 避免无用的 D2H + H2D 循环 |
| 每个时期重新创建读者 | `reader.next_epoch()` | 读者是有状态的 -- 创建一次，重用 |
| `ndd.readers.file(...)` | `ndd.readers.File(...)` | 读者类是 PascalCase |
| 从 `next_epoch()` 循环中 `break` | 消耗迭代器或创建新读者 | 迭代器必须在下一次 `next_epoch()` 之前完全消耗 |
| 向随机操作传递没有 `batch_size` | `ndd.random.uniform(batch_size=N, ...)` | 没有可继承的管道级批处理大小 |
| 在迭代后向构建而没有 `enable_checkpointing=True` 的读者注册以恢复 | 构造时传递 `enable_checkpointing=True`（或注册之前第一次迭代） | 后端不会保留快照，否则 |
| 拼写默认参数值 | 跳过默认参数值 | Python 端的开销非常高，尤其是当参数接受张量/批处理时。跳过参数使用快速路径，实际上传递哨兵值。 |

## 管道模式迁移

| 管道模式 | 动态模式 |
|--------------|--------------|
| `@pipeline_def` / `pipe.build()` / `pipe.run()` | 直接在循环中调用函数 |
| `fn.readers.file(...)` | `ndd.readers.File(...)`（PascalCase，有状态） |
| `fn.decoders.image(jpegs, device="mixed")` | `ndd.decoders.image(jpegs, device="gpu")` |
| `fn.op_name(...)` | `ndd.op_name(...)` |
| 管道级 `batch_size=64` | `reader.next_epoch(batch_size=64)` + 随机操作 `batch_size=64` |
| 管道级 `seed=42` | `ndd.random.set_seed(42)` 或 `ndd.random.RNG(seed=42)` |
| 管道级 `num_threads=4` | 启动时 `ndd.set_num_threads(4)` |
| `output.at(i)` | `batch.tensors[i]` |
| `output.as_cpu()` | `batch.cpu()` |
| `pipe.run()` 返回 `TensorList` 元组 | `reader.next_epoch(batch_size=N)` 生成 `Batch` 元组 |
| `Pipeline(..., enable_checkpointing=True)` + `pipe.checkpoint()` / `pipeline(checkpoint=...)` | `ndd.checkpoint.Checkpoint` + 每个对象的 `register` / `collect` / `save` / `load`；读者使用 `enable_checkpointing=True` 选择加入 |

## 限制

动态模式比管道模式更灵活，但性能可能稍差。为了获得最大吞吐量，请优先使用管道模式。

## 故障排除

- 如果错误在失败的调用之后出现，请在 `EvalMode.sync_cpu` 或 `EvalMode.sync_full` 下重新运行该块。
- 如果读者在多个时期中表现异常，请检查它是否创建一次，并且每个 `next_epoch()` 迭代器是否完全消耗。
