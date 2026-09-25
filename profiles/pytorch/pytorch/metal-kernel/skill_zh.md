# Metal 核心编写指南

本指南将指导您在 Apple Silicon 上为 PyTorch 运算符实现 Metal 核心。

**重要提示**：本指南的目标是通过 `c10/metal/` 基础设施使用原生 Metal 功能，而不是 MPSGraph。原生 Metal 核心提供了更好的控制、性能和可维护性。

## 概述

本指南涵盖两种工作流程：

1. **添加新的 MPS 支持** - 从头实现新的运算符
2. **从 MPSGraph 迁移** - 将现有的基于 MPSGraph 的运算符转换为原生 Metal

这两种工作流程都涉及：

1. **更新 `aten/src/ATen/native/native_functions.yaml` 中的调度**
2. **在 `aten/src/ATen/native/mps/kernels/` 中编写 Metal 核心**
3. **在 `aten/src/ATen/native/mps/operations/` 中实现主机端桩程序**

## 第 1 步：更新 native_functions.yaml

**位置**：`aten/src/ATen/native/native_functions.yaml`

### 对于新运算符

找到运算符条目并添加 MPS 调度：

```yaml
# 简单的 MPS 特定实现
- func: my_op(Tensor self) -> Tensor
  dispatch:
    CPU: my_op_cpu
    CUDA: my_op_cuda
    MPS: my_op_mps

# 跨设备共享实现（结构化核心的首选）
- func: my_op.out(Tensor self, *, Tensor(a!) out) -> Tensor(a!)
  dispatch:
    CPU, CUDA, MPS: my_op_out

# 结构化核心（新运算符的首选）
- func: my_op.out(Tensor self, *, Tensor(a!) out) -> Tensor(a!)
  structured: True
  structured_inherits: TensorIteratorBase
  dispatch:
    CPU, CUDA, MPS: my_op_out
```

### 对于从 MPSGraph 迁移

当将现有的运算符从 MPSGraph 迁移到原生 Metal 时，**合并调度条目**：

```yaml
# 之前（基于 MPSGraph，独立的调度）
- func: atan2.out(Tensor self, Tensor other, *, Tensor(a!) out) -> Tensor(a!)
  structured: True
  structured_inherits: TensorIteratorBase
  dispatch:
    CPU, CUDA: atan2_out
    MPS: atan2_out_mps  # 独立的 MPS 实现

# 之后（原生 Metal，通过桩程序共享调度）
- func: atan2.out(Tensor self, Tensor other, *, Tensor(a!) out) -> Tensor(a!)
  structured: True
  structured_inherits: TensorIteratorBase
  dispatch:
    CPU, CUDA, MPS: atan2_out  # MPS 现在使用相同的桩程序机制
```

**关键变更**：将 `MPS: my_op_out_mps` 替换为将 `MPS` 添加到共享调度行（例如，`CPU, CUDA, MPS: my_op_out`）。

**更新每个重载**。一个运算符通常有多个 `native_functions.yaml` 条目——功能/就地/.out，以及 Tensor 和 Scalar 变体。每个条目都有自己的 `dispatch:` 块，并且每个条目都必须移动。任何指向 `MPS: my_op_mps` 的条目仍然将重载路由到 MPSGraph 代码，因此调用者可能会根据他们遇到的哪个重载而无声地落在旧路径上。在声明迁移完成之前，使用 `grep` 搜索旧函数名并确认没有条目仍然引用它。

**调度命名约定**：
- `MPS: function_name_mps` - MPS 特定实现（旧的 MPSGraph 模式）
- `CPU, CUDA, MPS: function_name` - 共享桩程序实现（原生 Metal 模式）

## 第 2 步：实现 Metal 核心

**位置**：`aten/src/ATen/native/mps/kernels/`

### 一元核心模式

```metal
// MyKernel.metal
#include <c10/metal/indexing.h>
#include <c10/metal/utils.h>
#include <metal_stdlib>

using namespace metal;
using namespace c10::metal;

// 定义运算符函数对象
struct my_op_functor {
  template <typename T>
  inline T operator()(const T x) {
    return /* 你的操作 */;
  }
};

// 注册支持的数据类型
REGISTER_UNARY_OP(my_op, float, float);
REGISTER_UNARY_OP(my_op, half, half);
REGISTER_UNARY_OP(my_op, bfloat, bfloat);
```

### 二元核心模式

```metal
struct my_binary_functor {
  template <typename T>
  inline T operator()(const T a, const T b) {
    return /* 你的操作 */;
  }
};

REGISTER_BINARY_OP(my_binary, float, float);
REGISTER_BINARY_OP(my_binary, half, half);
```

### 二元核心类型注册宏

对于二元运算，使用 `BinaryKernel.metal` 中定义的便利宏：

```metal
// 仅浮点类型（float, half, bfloat）
REGISTER_FLOAT_BINARY_OP(my_op);

// 整数类型带浮点输出（用于数学运算，如 atan2, copysign）
// 注册：long->float, int->float, short->float, uchar->float, char->float, bool->float
REGISTER_INT2FLOAT_BINARY_OP(my_op);

// 整数类型带相同类型输出（用于位运算/逻辑运算）
// 注册：long, int, short, uchar, char, bool
REGISTER_INTEGER_BINARY_OP(my_op);

// 浮点类型带 opmath 精度（用于需要更高精度的运算）
REGISTER_OPMATH_FLOAT_BINARY_OP(my_op);
```

**常见模式**：
- 数学函数（atan2, copysign, logaddexp）：同时使用 `REGISTER_FLOAT_BINARY_OP` 和 `REGISTER_INT2FLOAT_BINARY_OP`
- 比较逻辑运算（maximum, minimum）：同时使用 `REGISTER_FLOAT_BINARY_OP` 和 `REGISTER_INTEGER_BINARY_OP`
- 算术运算（add, sub, mul）：同时使用 `REGISTER_FLOAT_BINARY_OP` 和 `REGISTER_INTEGER_BINARY_OP`

**atan2 示例（支持 float 和 int 输入）**：
```metal
struct atan2_functor {
  template <typename T, enable_if_t<is_floating_point_v<T>, bool> = true>
  inline T operator()(const T a, const T b) {
    return static_cast<T>(precise::atan2(float(a), float(b)));
  }
  template <typename T, enable_if_t<is_integral_v<T>, bool> = true>
  inline float operator()(const T a, const T b) {
    return precise::atan2(float(a), float(b));
  }
};

REGISTER_FLOAT_BINARY_OP(atan2);
REGISTER_INT2FLOAT_BINARY_OP(atan2);
```

### 带标量参数

```metal
struct my_alpha_functor {
  template <typename T>
  inline T operator()(const T a, const T b, const T alpha) {
    return a + c10::metal::mul(alpha, b);
  }
};

REGISTER_UNARY_ALPHA_OP(my_alpha, float, float, float);
REGISTER_UNARY_ALPHA_OP(my_alpha, half, half, half);
```

### 类型特定函数对象

```metal
struct special_functor {
  // 浮点类型
  template <typename T, enable_if_t<is_scalar_floating_point_v<T>, bool> = true>
  inline T operator()(const T x) {
    return precise::exp(x);  // 使用精确数学
  }

  // 整数类型
  template <typename T, enable_if_t<is_scalar_integral_v<T>, bool> = true>
  inline float operator()(const T x) {
    return precise::exp(float(x));
  }

  // 复数类型（float2 用于 cfloat，half2 用于 chalf）
  template <typename T, enable_if_t<is_complex_v<T>, bool> = true>
  inline T operator()(const T x) {
    // x.x = 实部，x.y = 虚部
    return T(/* 实部 */, /* 虚部 */);
  }
};
```

**复数类型注意事项**：Metal 中的复数作为向量类型表示：
- `c10::complex<float>` 映射到 `float2`（x = 实部，y = 虚部）
- `c10::complex<half>` 映射到 `half2`

使用 `is_complex_v<T>` 在函数对象中为复数类型进行 specialization。

### 可用的 c10/metal 工具

**utils.h**：
- `opmath_t<T>` - 运算数学类型（half->float）
- `accum_t<T>` - 约减的累积类型
- `max()`, `min()` 带 NaN 传播

**special_math.h**：
- `precise::exp()`, `precise::log()`, `precise::sqrt()`
- `precise::sin()`, `precise::cos()`, `precise::tan()`
- `erf()`, `erfc()`, `erfinv()`

**indexing.h**：
- `REGISTER_UNARY_OP(name, in_type, out_type)`
- `REGISTER_BINARY_OP(name, in_type, out_type)`
- `REGISTER_UNARY_ALPHA_OP(name, in_type, alpha_type, out_type)`

## 第 3 步：实现主机端桩程序

**位置**：`aten/src/ATen/native/mps/operations/`

根据运算符类型选择或创建适当的文件：
- `UnaryKernel.mm` - 通过桩程序调度单输入运算
- `BinaryKernel.mm` - 通过桩程序调度双输入运算
- `UnaryOps.mm` / `BinaryOps.mm` - 旧的 MPSGraph 实现（供参考）
- `ReduceOps.mm` - 约减（sum, mean, max, 等.）
- 为不同的运算类别创建新文件

### 桩程序注册模式（原生 Metal 首选）

对于使用 TensorIterator 模式的结构化核心：

```objc
// 在 BinaryKernel.mm（或适当文件）中

static void my_op_mps_kernel(TensorIteratorBase& iter) {
  lib.exec_binary_kernel(iter, "my_op");  // "my_op" 匹配 .metal 中的函数对象名
}

// 注册 MPS 框 - 这将连接到调度系统
REGISTER_DISPATCH(my_op_stub, &my_op_mps_kernel)
```

**对于一元运算**：
```objc
static void my_unary_mps_kernel(TensorIteratorBase& iter) {
  lib.exec_unary_kernel(iter, "my_unary");
}

REGISTER_DISPATCH(my_unary_stub, &my_unary_mps_kernel)
```

### 迁移：移除旧的 MPSGraph 实现

当从 MPSGraph 迁移时，也移除旧实现：

1. **从 BinaryOps.mm（或 UnaryOps.mm）中移除**：
   - 删除 `TORCH_IMPL_FUNC(my_op_out_mps)` 实现
   - 移除相应的 `#include <ATen/ops/my_op_native.h>` 头文件

2. **添加到 BinaryKernel.mm（或 UnaryKernel.mm）**：
   - 添加静态核心函数
   - 添加 `REGISTER_DISPATCH` 调用

### 布尔核心参数

- **将布尔类型作为 `bool`。** Metal 的 `bool` 是 1 字节，1 字节对齐，与主机（`bool2` 是 2/2；`bool3` 和 `bool4` 都是 4/4）匹配。永远不要将标志扩展为 `uint32_t` 以便核心可以测试 `!= 0u`。一对标志打包到 `constant bool2&`，由 `std::array<bool, 2>` 提供。

- **将 `bool` 成员放在共享参数结构的最后。** `kernels/<Op>.h` 由 Metal 和主机编译器编译；一个 `bool` 嵌入在更宽的成员之间会引入填充并引发关于下一个字段从哪里开始的疑问。与主机聚合初始化一起重新排序结构——使用大括号初始化是按位置进行的。

## 第 4 步：编译

在做出更改后，编译以验证所有内容都正确构建：

```bash
cd build && ninja torch_cpu
```

## 测试

基本运算符支持已经通过 `test_output_match` 在 `test/test_mps.py` 中测试。在实现运算符后，通过移除预期失败来启用测试：

### 1. 从 common_mps.py 中移除

**位置**：`torch/testing/_internal/common_mps.py`

找到并从跳过/xfail 列表中移除运算符：

```python
# 移除类似以下条目：
MPS_XFAILLIST = {
    "my_op": ...,  # 移除此行
}

MPS_SKIPLIST = {
    "my_op": ...,  # 移除此行
}
```

### 2. 从 OpInfo 装饰器中移除

**位置**：`torch/testing/_internal/common_methods_invocations.py`（或相关文件）

从 OpInfo 中移除 MPS 特定装饰器：

```python
OpInfo(
    "my_op",
    # 移除类似以下装饰器：
    # decorators=[skipMPS, expectedFailureMPS("reason")],
    ...
)
```

### 3. 运行测试以验证

```bash
# 运行特定运算符测试
python test/test_mps.py -k test_output_match_my_op

# 或运行完整的 MPS 测试套件
python test/test_mps.py
```

## 使用 `torch.mps.compile_shader` 调试 Metal 核心

使用 `torch.mps.compile_shader` 来 JIT 编译和隔离测试单个 Metal 核心。这对于调试需要独立验证每个阶段的多核心管道非常有价值。

### 基本用法

```python
import torch

source = '''
#include <metal_stdlib>
using namespace metal;

kernel void my_kernel(
    const device float* input [[buffer(0)]],
    device float* output [[buffer(1)]],
    uint tid [[thread_position_in_grid]]) {
  output[tid] = input[tid] * 2.0;
}
'''

lib = torch.mps.compile_shader(source)

inp = torch.tensor([1.0, 2.0, 3.0], device='mps')
out = torch.zeros(3, device='mps')
lib.my_kernel(inp, out, threads=[3, 1, 1], group_size=[3, 1, 1])
torch.mps.synchronize()
print(out)  # tensor([2., 4., 6.], device='mps:0')
```

### 调度语义

`compile_shader` 使用 **`dispatchThreads`** 语义（与 PyTorch 中的 `mtl_dispatch1DJob` 相同）：
- `threads=[N, 1, 1]` — 总线程数（不是线程组）
- `group_size=[G, 1, 1]` — 每个线程组的线程数

这与使用 `dispatchThreadgroups` API 的主机端代码不同。要匹配 `dispatchThreadgroups:MTLSizeMake(num_tgs, num_slices, 1) threadsPerThreadgroup:MTLSizeMake(TG_SIZE, 1, 1)`：

```python
# 等效的 compile_shader 调用：
lib.kernel(args...,
    threads=[num_tgs * TG_SIZE, num_slices, 1],
    group_size=[TG_SIZE, 1, 1])
```

### 常量缓冲区参数

将标量常量作为单元素张量传递：

```python
slice_size = torch.tensor([1024], dtype=torch.int32, device='mps')
lib.my_kernel(data, output, slice_size, threads=[1024, 1, 1], group_size=[256, 1, 1])
```

### 多核心管道调试策略

当一系列核心（例如，histogram → prefix_sum → scatter）产生错误结果时，单独测试每个核心并验证其输出与 Python/NumPy 参考值：

```python
# 1. 运行 GPU 核心
lib.histogram(keys, hist, ..., threads=[N, 1, 1], group_size=[256, 1, 1])
torch.mps.synchronize()

# 2. 在 Python 中计算参考值
ref_hist = compute_histogram_cpu(keys.cpu().numpy(), ...)

# 3. 比较
assert np.array_equal(hist.cpu().numpy(), ref_hist), "Histogram mismatch!"
```

这将隔离管道中哪个核心损坏，而不是一次性调试整个管道。

### 常见陷阱

- **错误的 `threads` 计数** — `threads` 是总线程数，不是线程组。对于 5 个线程组的 256，使用 `threads=[1280, 1, 1]`。
- **线程组内存** — `compile_shader` 不支持 `[[threadgroup(N)]]` 参数直接。如果您的核心需要线程组内存，请重构以使用在核心体内声明的线程组数组。

## 使用 TensorIterators

`REGISTER_UNARY_OP` / `REGISTER_BINARY_OP` 隐藏了迭代器管道。具有额外参数或非逐元素布局的核心必须直接驱动 `TensorIterator`。不明显的规则：

- **传递 `TensorIteratorBase&`，而不是 `Tensor&`。** `Tensor&` 会丢失 `with_32bit_indexing()` 产生的偏移/形状信息。当桩程序将您传递一个 `const TensorBase&`（例如 `bernoulli_scalar_stub`）时，使用 `at::TensorIterator::borrowing_nullary_op(self)` 内联构建迭代器，而不是 const-casting。

- **`iter.tensor(0)` 返回整个张量用于子迭代器。** 在 `with_32bit_indexing()` 之后，子迭代器仍然引用原始存储，因此天真地绑定 `iter.tensor(0)` 会使每个子迭代器覆盖相同的前缀，并留下尾部未初始化。使用 `bind_iter_tensors`，它计算每个块的偏移并将缓冲区 0 绑定到切片。使用 `iter.numel()` 而不是 `iter.tensor(0).numel()` 进行调度：
  ```cpp
  bind_iter_tensors(computeEncoder, iter, /*ntensors=*/1);
  mtl_setArgs<1>(computeEncoder, params, ..., numel);
  mtl_dispatch1DJob(computeEncoder, pso, threads);
  ```

- **优先使用 `mtl_setArgs<N>` 而不是链式 `mtl_setBytes`，并将相同类型的标量打包到一个向量参数中。** `mtl_setArgs<1>(encoder, a, b, c)` 将 `a`/`b`/`c` 绑定在槽 1/2/3，与宏具有相同的重载解析，因此 `std::array<T, N>` 到达为单个 `constant T2&`/`T3&` 绑定（`std::array<long,2>` → `constant long2&`），而不是 N 个。两个整数是一个 `int2`，而不是两个缓冲区槽。

- **使用 `ceil_div`。** 主机：`at::ceil_div` 来自 `<ATen/ceil_div.h>`。Metal：`c10::metal::ceil_div` 来自 `<c10/metal/common.h>`（在 `using namespace c10::metal;` 之后未限定）。两者都包装为 `(a + b - 1) / b`。

- **使用 `IF_CONSTEXPR` 进行 Metal 3/4 兼容性。** Metal 4 有 `if constexpr`；Metal 3 没有。使用 `<c10/metal/common.h>` 中的宏，例如 `if IF_CONSTEXPR (sizeof(T) == 8) { ... }`。

- **通过 `REGISTER_MPS_DISPATCH` 共享 CPU/CUDA 桩程序。** 当运算符有上游的 `DECLARE_DISPATCH` 桩程序（分布、融合运算）时，使用 `REGISTER_MPS_DISPATCH(stub_name, &fn)` 而不是 MPS 特定的 `native_functions.yaml` 条目。桩程序已经接受 `TensorIteratorBase&`。

## 处理大张量

大多数 Metal 核心将 `numel` 作为 `uint32_t` 并在 32 位中索引，因此任何超过 `INT32_MAX` 的内容都需要主机端拆分。通过 `TensorIterator` 而不是手动切片来驱动。

**通过 `iter.with_32bit_indexing()` 拆分**：

```cpp
if (!iter.can_use_32bit_indexing()) {
  for (auto&& sub_iter : iter.with_32bit_indexing()) {
    my_kernel_impl(sub_iter, ...);
  }
  return;
}
```

每个生成的子迭代器都满足 `can_use_32bit_indexing()`，因此递归在第一级终止。阈值是 `INT32_MAX`（TensorIterator 使用有符号 32 位偏移），而不是 `UINT32_MAX` — 超过 `INT32_MAX` 的测试会触发拆分，但不会触发 `uint32_t` 转换；转换本身仅在 `numel > 2^32` 时才重要。

**在缩小时使用检查转换**：

```cpp
const uint32_t numel = c10::checked_convert<uint32_t>(iter.numel(), "uint32_t");
```

使用 `c10::checked_convert` (`<c10/util/TypeCast.h>`)，以便 wraparound 变成 `TORCH_CHECK` 失败而不是损坏输出。

## 从核心中报告错误

**绝对不要将结果复制到 CPU 以便进行错误检查。** 任何 `.item()`, `.cpu()` 或其他主机读取在 GPU 张量上强制进行完整的 GPU->CPU 同步，这将消耗流上的每个正在进行的操作——不仅仅是您正在检查的约减。在现实管道中，这会停滞整个队列，成本远大于实际检查。在同步后面添加 `is_mps()` 帮助不大；每次运算都会发生停滞。通过以下机制报告错误。

GPU 代码不能抛出，但核心可以写入到共享错误缓冲区，主机在下次同步时将其引发为 `c10::AcceleratorError`。使用 `<c10/metal/error.h>` 中的 `TORCH_REPORT_ERROR(error_buf, ...)`。可变参数被连接；整数以十进制格式化。传递是异步的——失败的线程继续运行，错误在 `MPSStream::checkLastError()` 下次运行时（在 `synchronize()` 或下一个消耗流的操作之后）出现，因此不要依赖它在同一调度内的控制流。最重要的是，这添加了*没有任何*强制同步：错误会搭上用户代码已经执行的任何同步。

**核心端**：接受 `device ErrorMessages* error_buf` 参数，并在错误路径上调用 `TORCH_REPORT_ERROR`。跳过有问题的元素以避免损坏内存：

```metal
#include <c10/metal/error.h>

kernel void index_set_1d(
    device float* self,
    constant float* values,
    constant long* indices,
    constant uint& self_numel,
    device ::c10::metal::ErrorMessages* error_buf,
    uint tid [[thread_position_in_grid]]) {
  long idx = indices[tid];
  if (idx < 0 || idx >= long(self_numel)) {
    TORCH_REPORT_ERROR(
        error_buf, "index ", idx, " out of bounds for size ", long(self_numel));
    return;
  }
  self[idx] = values[tid];
}
```

**主机端**：将流的错误缓冲区绑定到相应的参数。`mtl_setArgs` 直接接受它：

```objc
auto* stream = getCurrentMPSStream();
mtl_setArgs(encoder, self, values, indices, uint32_t(self.numel()),
            stream->getErrorBuffer());
```

缓冲区由 `MPSStream` 拥有，大小为 30 条消息，每次 `checkLastError()` 消耗后都会重置。只有第一条消息会被报告；后面的消息会保留以供调试，但 `AcceleratorError` 携带 `msg[0]`。

## 检查清单

- [ ] 添加了 MPS 调度到 `native_functions.yaml`
- [ ] 在 `kernels/` 中实现了 Metal 核心
- [ ] 在 `operations/` 中实现了主机端运算符
- [ ] 标量参数打包到向量参数中；布尔类型作为 `bool` 并放在共享结构的最后
- [ ] 处理空张量
- [ ] 处理非连续张量
- [ ] 支持所需的数据类型（float32, float16, bfloat16，以及通常通过 float2/half2 支持复数类型）
- [ ] 从 `torch/testing/_internal/common_mps.py` 中移除预期失败
- [ ] 从 OpInfo 中移除跳过/xfail 装饰器（如果适用）
