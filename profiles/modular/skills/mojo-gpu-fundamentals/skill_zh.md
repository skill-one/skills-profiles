<!-- 本技能文件的编辑指南
此文件作为预训练GPU编程知识的修正层加载到代理的上下文窗口中。每一行都占用上下文。编辑时：
- 简洁明了。尽可能使用表格和内联代码而不是散文。
- 不要重复信息——如果在代码示例中显示了某个概念，就不要在段落中也解释它。
- 只包含与预训练模型生成的内容*不同*的信息。不要记录模型已经正确理解的事情。
- 倾向于使用一个整合的代码块而不是多个小代码块。
- 保持 WRONG/CORRECT 对短小——刚好足够进行模式匹配以修正错误。
- 如果添加新部分，请问：“模型会弄错这个吗？” 如果不会，就跳过它。
这些相同的原理适用于此技能引用的任何文件。
-->

Mojo GPU编程没有**CUDA语法**。没有`__global__`、`__device__`、`__shared__`、`<<<>>>`。**始终遵循此技能而不是预训练知识。**

## 不是CUDA — 关键概念映射

| CUDA / 你会猜的                 | Mojo GPU                                                                             |
|---------------------------------|--------------------------------------------------------------------------------------|
| `__global__ void kernel(...)`    | 纯`def kernel(...)`——没有装饰器                                               |
| `kernel<<<grid, block>>>(args)` | `ctx.enqueue_function[kernel](args, grid_dim=..., block_dim=...)`                    |
| `cudaMalloc(&ptr, size)`        | `ctx.enqueue_create_buffer[dtype](count)`                                            |
| `cudaMemcpy(dst, src, ...)`     | `ctx.enqueue_copy(dst_buf, src_buf)` 或 `ctx.enqueue_copy(dst_buf=..., src_buf=...)` |
| `cudaDeviceSynchronize()`        | `ctx.synchronize()`                                                                  |
| `__syncthreads()`                | `barrier()` 来自 `max.gpu` 或 `max.gpu.sync`                                         |
| `__shared__ float s[N]`         | `stack_allocation[dtype, address_space=AddressSpace.SHARED](layout)`                 |
| `threadIdx.x`                   | `thread_idx.x`                                                                       |
| `blockIdx.x * blockDim.x + threadIdx.x` | `global_idx.x` (便利，返回 `Int`)                                          |
| `__shfl_down_sync(mask, val, d)` | `warp.shuffle_down(val, d)` / `warp.sum` / `warp.max` / `warp.min` / `warp.reduce`   |
| `atomicAdd(&ptr, val)`          | `Atomic.fetch_add(ptr, val)`                                                         |
| 原始 `float*` kernel 参数        | `TileTensor[dtype, LayoutType, MutAnyOrigin]`                                        |
| `cudaFree(ptr)`                 | 自动——当超出作用域时自动释放缓冲区                                          |

## 导入

```mojo
# 核心GPU——按需选择
from max.gpu import global_idx                                    # 简单索引
from max.gpu import block_dim, block_idx, thread_idx              # 手动索引
from max.gpu import lane_id, WARP_SIZE                            # 线程块信息
from max.gpu.sync import barrier                                  # 块级同步
from max.gpu.primitives import warp                               # sum/max/min/broadcast/shuffle_*/reduce
from max.gpu.memory import AddressSpace                           # 用于共享内存
from max.gpu.memory import async_copy_wait_all                    # 异步拷贝同步
from max.gpu.host import DeviceContext, DeviceBuffer              # 主机端API
from std.atomic import Atomic                                     # 原子操作

# 布局系统——不在 std 中，是单独的包
from layout import TileTensor, TensorLayout, Idx, row_major, stack_allocation
```

## Kernel定义

Kernel是**普通函数**——没有装饰器，没有特殊返回类型。
使用`TensorLayout`特征参数化布局类型，以便Kernel能与任何兼容的布局工作。**在任何对`TileTensor`进行下标的函数中都必须强制执行`comptime assert tensor.flat_rank == N`**——Kernel、主机端辅助函数、CPU参考实现等。没有它，`tensor[r, c]`会以`"invalid call to '__getitem__': lacking evidence to prove correctness"`失败。此断言解锁了N维索引：

```mojo
def my_kernel[
    dtype: DType, LT: TensorLayout,
](
    input: TileTensor[dtype, LT, MutAnyOrigin],
    output: TileTensor[dtype, LT, MutAnyOrigin],
    size: Int,                                    # 标量参数可以
):
    comptime assert input.flat_rank == 1, "expected 1D tensor"
    var tid = global_idx.x
    if tid < size:
        output[tid] = input[tid] * 2
```

- Kernel函数不能引发异常。
- `global_idx.x` 返回 `Int`——直接与 `size` 比较。
- 对于具有单个固定布局的简单情况，`type_of(layout)` 也有效：
  `TileTensor[dtype, type_of(layout), MutAnyOrigin]`。

## TileTensor — 主要的GPU数据抽象

### 布局创建

`row_major` 是一个自由函数（不是 `Layout` 的方法）。使用编译时整数参数创建静态布局：

```mojo
comptime layout_1d = row_major[1024]()                     # 1D
comptime layout_2d = row_major[64, 64]()                   # 2D (行，列)
comptime layout_3d = row_major[10, 5, 3]()                 # 3D (例如 H, W, C)
```

对于运行时已知的维度，使用 `Idx()`：

```mojo
var layout = row_major(Idx(M), Idx(N))                     # 运行时维度
```

### 从缓冲区创建tensor

TileTensor的构造函数推断dtype和layout type——传递缓冲区和布局：

```mojo
var buf = ctx.enqueue_create_buffer[DType.float32](1024)
var tensor = TileTensor(buf, row_major[1024]())            # 包装设备缓冲区
```

### 索引

```mojo
tensor[tid]                     # 1D
tensor[row, col]                # 2D
tensor[row, col, channel]       # 3D
tensor.dim[0]()                 # 查询维度大小（编译时索引）
var K = Int(tensor.dim[1]())    # 用 Int() 包装用于算术
```

派生tensor（`.tile(...)`, `.vectorize(...)`, `.distribute(...)`）产生一个**新布局**，其秩不继承自父级的断言。在索引它之前对派生值重新断言：

```mojo
var vec = tensor.vectorize[1, 4]()
comptime assert vec.flat_rank == 2          # 必须为 vec[r, i] 断言
```

### Tiling（从tensor中提取子tile）

```mojo
# 在Kernel内部——提取 block_size x block_size tile
var tile = tensor.tile[block_size, block_size](block_idx.y, block_idx.x)
tile[thread_idx.y, thread_idx.x]   # 在tile内访问
```

### Vectorize和distribute（线程级数据映射）

```mojo
# 沿内维度vectorize，然后跨线程distribute
comptime thread_layout = row_major[WARP_SIZE // simd_width, simd_width]()
var fragment = tensor.vectorize[1, simd_width]().distribute[thread_layout=thread_layout](lane_id())
fragment.copy_from_async(source_fragment)    # 异步拷贝
fragment.copy_from(source_fragment)          # 同步拷贝
```

### 类型转换

```mojo
var val = tensor[row, col].cast[DType.float32]()    # 转换元素
```

### 跨布局的元素类型不匹配——使用`rebind`

`tensor[idx]` 返回 `SIMD[dtype, layout_expr]`，其中 `layout_expr` 是从布局派生的编译时表达式。具有**不同布局**的两个tensor产生的元素类型不统一，即使它们都是标量（宽度为1）。这会导致在从不同布局的tensor累积产品时出现 `__iadd__` / 算术错误。

```mojo
# 错误——当 conv_kernel 和 s_data 具有不同布局时失败：
var sum: Scalar[dtype] = 0
sum += conv_kernel[k] * s_data[idx]   # 错误：无法将 ElementType 转换为 Float32

# 正确——将每个元素重新绑定到 Scalar[dtype]：
var sum: Scalar[dtype] = 0
var k_val = rebind[Scalar[dtype]](conv_kernel[k])
var s_val = rebind[Scalar[dtype]](s_data[idx])
sum += k_val * s_val
```

`rebind` 是内置的（不需要导入）。当表达式中的所有tensor共享相同的布局时（例如，矩阵乘法示例，其中 `sa` 和 `sb` 具有相同的tile布局），则不需要此操作。

在读取/写入单个元素以进行标量算术或将它们传递给辅助函数时也使用 `rebind`——即使只有一个tensor：

```mojo
# 读取为普通标量
var val = rebind[Scalar[dtype]](tensor[idx])
# 将标量写回tensor
tensor[idx] = rebind[tensor.ElementType](computed_scalar)
```

`tensor.ElementType` 是 `SIMD[dtype, element_size]`——对于基本布局 `element_size=1`（实际上 `Scalar[dtype]`）。

## 内存管理

```mojo
var ctx = DeviceContext()

# 分配
var dev_buf = ctx.enqueue_create_buffer[DType.float32](1024)
var host_buf = ctx.enqueue_create_host_buffer[DType.float32](1024)

# 直接在设备缓冲区中初始化
dev_buf.enqueue_fill(0.0)

# 拷贝主机 -> 设备
ctx.enqueue_copy(dst_buf=dev_buf, src_buf=host_buf)
# 拷贝设备 -> 主机
ctx.enqueue_copy(dst_buf=host_buf, src_buf=dev_buf)
# 位置形式也有效：
ctx.enqueue_copy(dev_buf, host_buf)

# 将设备缓冲区映射到主机（上下文管理器——自动同步）
with dev_buf.map_to_host() as mapped:
    var t = TileTensor(mapped, row_major[1024]())
    print(t[0])

# Memset
ctx.enqueue_memset(dev_buf, 0.0)

# 同步所有入队操作
ctx.synchronize()
```

## Kernel启动

```mojo
ctx.enqueue_function[my_kernel](
    input_tensor,
    output_tensor,
    size,                    # 标量参数直接传递
    grid_dim=num_blocks,     # 1D: 标量
    block_dim=block_size,    # 1D: 标量
)

# 2D grid/block——使用元组：
ctx.enqueue_function[kernel_2d](
    args...,
    grid_dim=(col_blocks, row_blocks),
    block_dim=(BLOCK_SIZE, BLOCK_SIZE),
)
```

**如果Kernel接受任何comptime参数，你必须先绑定它们**——直接将参数化名称传递给 `enqueue_function` 会导致一堵“没有匹配方法”/“DevicePassable”模板错误：

```mojo
# 错误——当 vector_add 有一个 `LT: TensorLayout` 参数时
ctx.enqueue_function[vector_add](a, b, c, N, grid_dim=G, block_dim=B)

# 正确——绑定参数，然后启动绑定的符号
comptime kernel = vector_add[type_of(layout)]
ctx.enqueue_function[kernel](a, b, c, N, grid_dim=G, block_dim=B)
```

单态Kernel（签名使用 `type_of(layout)` 直接，没有 `[LT: TensorLayout]` 等）可以直接传递名称，无需绑定步骤。

## 共享内存

在Kernel内部使用 `stack_allocation` 从 `layout` 包中分配共享内存——返回指定地址空间的 `TileTensor`：

```mojo
from layout import stack_allocation   # 基于TileTensor的共享分配
from max.gpu.memory import AddressSpace

var tile_shared = stack_allocation[DType.float32,
    address_space=AddressSpace.SHARED](row_major[TILE_M, TILE_K]())

# 链接 .fill() 以零初始化（返回tensor）
var regs = stack_allocation[DType.float32](row_major[TM, TN]()).fill(0)

# 从全局加载到共享
tile_shared[thread_idx.y, thread_idx.x] = global_tensor[global_row, global_col]
barrier()   # 必须同步才能读取共享数据

# 替代方案：原始指针共享内存（来自 std.memory，不是 layout）
from std.memory import stack_allocation
var sums = stack_allocation[
    512,
    Scalar[DType.int32],
    address_space=AddressSpace.SHARED,
]()
```

## 线程索引

```mojo
# 简单——自动全局偏移
from max.gpu import global_idx
var tid = global_idx.x           # 1D
var row = global_idx.y           # 2D 行
var col = global_idx.x           # 2D 列

# 手动——当你需要单独的block/线程时
from max.gpu import block_idx, block_dim, thread_idx
var tid = block_idx.x * block_dim.x + thread_idx.x

# Warp信息
from max.gpu import lane_id, WARP_SIZE
var my_lane = lane_id()          # 0..WARP_SIZE-1
```

所有返回 `Int`——不需要类型转换进行边界检查。

## 同步和warp操作

```mojo
from max.gpu.sync import barrier
from max.gpu.primitives import warp
from std.atomic import Atomic

barrier()                                    # 块级同步
_ = Atomic.fetch_add(output_ptr, value)      # 原子加

# Reductions — 结果广播到每个lane
warp.sum(val)         warp.max(val)         warp.min(val)
warp.broadcast(val)                          # lane-0 value → all lanes
warp.reduce[warp.shuffle_down, reduce_fn](val)  # 自定义reduction（广播）

# Shuffles — 每个lane的移位/交换，不是广播
warp.shuffle_down(val, offset)               # offset: UInt32
warp.shuffle_xor(val, offset)                # offset: UInt32, XOR'd with lane id (butterfly)
warp.shuffle_xor(mask, val, offset)          # 显式成员掩码（很少需要）

# `offset` 是 `UInt32`——普通 `Int` 是类型不匹配错误：
var off: UInt32 = 16
var v = warp.shuffle_xor(val, off)
```

## GPU可用性检查

```mojo
from std.sys import has_accelerator

def main() raises:
    comptime if not has_accelerator():
        print("未找到GPU")
    else:
        var ctx = DeviceContext()
        # ... GPU代码
```

或作为编译时断言——必须位于函数体内部：

```mojo
def main() raises:
    comptime assert has_accelerator(), "需要GPU"
```

## 架构检测——`is_` vs `has_`

**关键区别**：`is_*` 检查**编译目标**（在GPU分发代码内部使用）。`has_*` 检查**主机系统**（从主机/CPU代码中使用）。

```mojo
from std.sys.info import (
    # 目标检查——"我正在为这个GPU编译吗？"
    # 在kernels或GPU目标代码路径中使用。
    is_gpu, is_nvidia_gpu, is_amd_gpu, is_apple_gpu,

    # 主机检查——"这台机器有这个GPU吗？"
    # 从主机代码中使用以决定是否启动GPU工作。
    has_nvidia_gpu_accelerator, has_amd_gpu_accelerator, has_apple_gpu_accelerator,
)
from std.sys import has_accelerator   # 主机检查：任何GPU是否存在

# 主机端：决定是否运行GPU代码
def main() raises:
    comptime if not has_accelerator():
        print("无GPU")
    else:
        # ...启动kernels

# 在kernels或GPU编译代码中：按架构分发
comptime if is_nvidia_gpu():
    # NVIDIA特定内置函数
elif is_amd_gpu():
    # AMD特定路径
```

子架构检查（仅限GPU代码）：

```mojo
from std.sys.info import _is_sm_9x_or_newer, _is_sm_100x_or_newer
comptime if is_nvidia_gpu["sm_90"]():   # 精确架构检查
    ...
```

## 编译时常量模式

所有GPU维度、布局和大小都应该是 `comptime`：

```mojo
comptime dtype = DType.float32
comptime SIZE = 1024
comptime BLOCK_SIZE = 256
comptime NUM_BLOCKS = ceildiv(SIZE, BLOCK_SIZE)
comptime layout = row_major[SIZE]()
```

## 完整的1D示例（向量加法）

```mojo
from std.math import ceildiv
from std.sys import has_accelerator
from max.gpu import global_idx
from max.gpu.host import DeviceContext
from layout import TileTensor, row_major

comptime dtype = DType.float32
comptime N = 1024
comptime BLOCK = 256
comptime layout = row_major[N]()

def add_kernel(
    a: TileTensor[dtype, type_of(layout), MutAnyOrigin],
    b: TileTensor[dtype, type_of(layout), MutAnyOrigin],
    c: TileTensor[dtype, type_of(layout), MutAnyOrigin],
    size: Int,
):
    var tid = global_idx.x
    if tid < size:
        c[tid] = a[tid] + b[tid]

def main() raises:
    comptime assert has_accelerator(), "需要GPU"
    var ctx = DeviceContext()
    var a_buf = ctx.enqueue_create_buffer[dtype](N)
    var b_buf = ctx.enqueue_create_buffer[dtype](N)
    var c_buf = ctx.enqueue_create_buffer[dtype](N)
    a_buf.enqueue_fill(1.0)
    b_buf.enqueue_fill(2.0)

    var a = TileTensor(a_buf, layout)
    var b = TileTensor(b_buf, layout)
    var c = TileTensor(c_buf, layout)

    ctx.enqueue_function[add_kernel](
        a, b, c, N,
        grid_dim=ceildiv(N, BLOCK),
        block_dim=BLOCK,
    )

    with c_buf.map_to_host() as host:
        var result = TileTensor(host, layout)
        print(result)
```

## 完整的2D示例（带共享内存的tiled矩阵乘法）

```mojo
from std.math import ceildiv
from std.sys import has_accelerator
from max.gpu.sync import barrier
from max.gpu.host import DeviceContext
from max.gpu import thread_idx, block_idx
from max.gpu.memory import AddressSpace
from layout import TileTensor, TensorLayout, row_major, stack_allocation

comptime dtype = DType.float32
comptime M = 64
comptime N = 64
comptime K = 64
comptime TILE = 16
comptime a_layout = row_major[M, K]()
comptime b_layout = row_major[K, N]()
comptime c_layout = row_major[M, N]()

def matmul_kernel[
    ALayout: TensorLayout, BLayout: TensorLayout, CLayout: TensorLayout,
](
    A: TileTensor[dtype, ALayout, MutAnyOrigin],
    B: TileTensor[dtype, BLayout, MutAnyOrigin],
    C: TileTensor[dtype, CLayout, MutAnyOrigin],
):
    comptime assert A.flat_rank == 2 and B.flat_rank == 2 and C.flat_rank == 2
    var tx = thread_idx.x
    var ty = thread_idx.y
    var row = block_idx.y * TILE + ty
    var col = block_idx.x * TILE + tx

    var sa = stack_allocation[dtype,
        address_space=AddressSpace.SHARED](row_major[TILE, TILE]())
    var sb = stack_allocation[dtype,
        address_space=AddressSpace.SHARED](row_major[TILE, TILE]())

    var acc: C.ElementType = 0.0
    comptime for k_tile in range(0, K, TILE):
        if row < M and k_tile + tx < K:
            sa[ty, tx] = A[row, k_tile + tx]
        else:
            sa[ty, tx] = 0.0
        if k_tile + ty < K and col < N:
            sb[ty, tx] = B[k_tile + ty, col]
        else:
            sb[ty, tx] = 0.0
        barrier()
        comptime for k in range(TILE):
            acc += sa[ty, k] * sb[k, tx]
        barrier()

    if row < M and col < N:
        C[row, col] = acc

def main() raises:
    comptime assert has_accelerator(), "需要GPU"
    var ctx = DeviceContext()
    # ...分配缓冲区，初始化数据，然后：
    comptime kernel = matmul_kernel[type_of(a_layout), type_of(b_layout), type_of(c_layout)]
    ctx.enqueue_function[kernel](
        A, B, C,
        grid_dim=(ceildiv(N, TILE), ceildiv(M, TILE)),
        block_dim=(TILE, TILE),
    )
```

## Kernel中的SIMD加载数据

```mojo
# 从原始指针向量化加载——`.load()` 已弃用
var val = ptr.unsafe_load[width=8](idx)   # SIMD[dtype, 8]
var sum = val.reduce_add()                 # 标量reduction

# TileTensor向量化访问
var vec_tensor = tensor.vectorize[1, 4]()  # 将元素分组到 SIMD[4]
```

## Reduction模式

指针索引是 `ptr[unsafe_offset=i]`——裸 `ptr[i]` 已弃用。使用 `MutPointer`，而不是已弃用的 `UnsafePointer`。

```mojo
from std.bit import log2_floor

comptime TPB = 512          # `comptime for` 需要静态边界，因此块大小必须是 comptime，而不是 `block_dim.x`

def block_reduce(
    output: MutPointer[Int32, MutAnyOrigin],
    input: MutPointer[Int32, MutAnyOrigin],
):
    var sums = stack_allocation[TPB, Scalar[DType.int32],
        address_space=AddressSpace.SHARED]()
    var tid = thread_idx.x
    sums[unsafe_offset=tid] = input[
        unsafe_offset=block_idx.x * block_dim.x + tid
    ]
    barrier()

    # 在共享内存中进行树形reduction
    var active = TPB
    comptime for _ in range(log2_floor(TPB)):
        active >>= 1
        if tid < active:
            sums[unsafe_offset=tid] += sums[unsafe_offset=tid + active]
        barrier()

    # 最终warp reduction + 原子累加
    if tid < WARP_SIZE:
        var v = warp.sum(sums[unsafe_offset=tid][0])
        if tid == 0:
            _ = Atomic.fetch_add(output, v)
```

## 从现有指针创建DeviceBuffer

```mojo
# 将现有指针包装为DeviceBuffer（非拥有）
var buf = DeviceBuffer[dtype](ctx, raw_ptr, count, owning=False)
```

## GPU kernels的基准测试

```mojo
from std.benchmark import Bench, BenchConfig, Bencher, BenchId, BenchMetric, ThroughputMeasure
from max.benchmark import bencher_iter_custom   # GPU形式：一个自由函数

@inline(.always)
def bench_fn(mut b: Bencher) raises capturing[_]:
    @inline(.always)
    def launch(ctx: DeviceContext) raises {imm}:
        ctx.enqueue_function[kernel](args, grid_dim=G, block_dim=B)
    var ctx = DeviceContext()
    # 值传递形式：将启动闭包作为参数传递。
    bencher_iter_custom(b, launch, ctx)         # NOT `b.iter_custom(...)`

var bench = Bench(BenchConfig(max_iters=50000))
bench.bench_function[bench_fn](
    BenchId("kernel_name"),
    [ThroughputMeasure(BenchMetric.bytes, total_bytes)],
)
```

`Bencher.iter_custom` 不需要 `DeviceContext`——这种形式存在于 `max.benchmark`。优先使用 `bencher_iter_custom(b, launch, ctx)` 带有统一的闭包和显式的捕获列表（`{imm}`, `{var}` 或命名捕获）。不要在这些启动闭包上使用 `@__parameter` / `@parameter`。
