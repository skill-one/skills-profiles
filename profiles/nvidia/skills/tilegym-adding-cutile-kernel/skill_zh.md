# 将 cuTile 内核添加到 TileGym

为添加新的算子（例如，`my_op`）并使用 cuTile 后端提供端到端工作流程。

## 执行规则

**必须严格遵守以下规则：**
1. 在编写任何代码之前，使用 TodoWrite 创建以下检查清单
2. 按顺序执行步骤 — 不要跳过或合并步骤
3. 完成每个待办事项后标记为 `completed`，开始时标记为 `in_progress`
4. 如果某个步骤不适用（例如，没有 cuTile 实现），则标记为 `completed` 并添加注释，不要无声地跳过
5. 每个步骤必须导致文件写入或显式跳过决策 — 不能无声地遗漏

## 说明

必须从开始将此检查清单复制到 TodoWrite：

```
- [ ] 第 1 步：在 ops.py 中注册调度接口
- [ ] 第 2 步：实现 cuTile 后端
- [ ] 第 3 步：在 __init__.py (cutile) 中注册
- [ ] 第 4 步：添加测试
- [ ] 第 5 步：在 tests/benchmark 中添加基准测试
- [ ] 第 6 步：验证（运行 pytest + lint）
```

## 第 1 步：注册调度接口

**文件**：`src/tilegym/ops/ops.py`

添加一个 `@dispatch` 函数 — 这是所有后端的**唯一入口点**。

```python
@dispatch(
    "my_op",
)
def my_op(
    input: torch.Tensor,
    out: Optional[torch.Tensor] = None,
    **kwargs: Any,
):
    """
    my_op 的描述。

    Args:
        input: 输入张量
        out: 可选的预分配输出张量
        **kwargs: 后端特定配置的附加参数

    Returns:
        torch.Tensor
    """
    raise NotImplementedError(f"my_op 对于 {get_current_backend()} 未实现")
```

**关键规则：**
- 函数体仅抛出 `NotImplementedError`
- 包含 `**kwargs` 以用于后端特定参数

**参考**：查看 `src/tilegym/ops/ops.py` 中的现有算子（例如，`silu_and_mul`，`softmax`）

## 第 2 步：实现 cuTile 后端

**文件**：`src/tilegym/ops/cutile/my_op.py`

文件结构遵循此模板：

```python
import torch
import cuda.tile as ct

from tilegym.backend import register_impl


@ct.kernel
def my_op_kernel_ct(x, output, n_elements: ct.Constant[int], BLOCK_SIZE: ct.Constant[int]):
    bid = ct.bid(0)
    indices = bid * BLOCK_SIZE + ct.arange(0, BLOCK_SIZE)
    x_val = ct.gather(x, indices)
    # ... 计算 ...
    ct.scatter(output, indices, result)


@register_impl("my_op", backend="cutile")
def my_op(input: torch.Tensor, out: torch.Tensor = None, **kwargs) -> torch.Tensor:
    n = input.numel()
    if out is None:
        out = torch.empty_like(input)
    grid = ((n + 1023) // 1024,)
    ct.launch(stream, grid, kernel, (some args, ...))
    return out
```

**参考**：`src/tilegym/ops/cutile/silu_and_mul.py`

## 第 3 步：在 `__init__.py` (CRITICAL) 中注册

缺少此步骤意味着 cuTile 后端实现永远不会被加载。

**文件**：`src/tilegym/ops/cutile/__init__.py`

在 `if is_backend_available("cutile"):` 块中（按字母顺序）添加：

```python
from . import my_op
```

并在函数导入部分添加：

```python
from .my_op import my_op
```

并将 `"my_op"` 添加到 `__all__`。

## 第 4 步：添加测试

**文件**：`tests/ops/test_my_op.py`

**CRITICAL**：始终从 `tilegym.ops` 导入，**永远**不要从 `tilegym.ops.cutile.my_op` 导入。

```python
import pytest
import torch

from tilegym.backend import is_backend_available, set_backend
from .. import common

_backends = ["cutile"]


class Test_MY_OP(common.PyTestCase):
    @staticmethod
    def reference(input):
        """使用 PyTorch 的参考实现。"""
        return torch.some_reference(input)

    @pytest.mark.parametrize("shape, dtype", [
        ((1024,), torch.float16),
        ((1024, 512), torch.float32),
        ((64, 64, 64), torch.bfloat16),
    ])
    @pytest.mark.parametrize("backend", _backends)
    def test_op(self, shape, dtype, backend, arch):
        if backend == "cutile" and not is_backend_available("cutile"):
            pytest.skip("Cutile 后端不可用")
        try:
            set_backend(backend)
        except Exception as e:
            pytest.skip(f"后端不受支持：{e}")

        self.setUp()

        from tilegym.ops import my_op

        A = torch.randn(*shape, dtype=dtype, device="cuda")
        self.assertCorrectness(
            my_op, self.reference, {"input": A},
            atol=1e-3, rtol=1e-3,
        )
```

**关键模式：**
- `_backends = ["cutile"]`
- `test_op`：使用 `set_backend(backend)` 并配合 try-except，调用 `self.setUp()`

**参考**：`tests/ops/test_silu_and_mul.py`

以下是常见错误。
```
1. 缺少 _backends 列表（在类内部）
2. test_op / test_op_xxx — 缺少 @pytest.mark.parametrize("backend", _backends)，backend 参数，以及 tilegym.is_backend_available / tilegym.set_backend 模式
```

## 第 5 步：在 tests/benchmark 中添加基准测试

**文件**：`tests/benchmark/bench_my_op.py`

**来自 benchmark_rules.md 的关键规则：**
- 通过 `tilegym.ops.my_op(a, b, ..., backend=backend)` 调用算子 — **不要**使用 `set_backend`。
- 定义 `ALL_BACKENDS`（至少包括 `cutile` 和 `torch`），使用 `get_supported_backends()` 进行过滤。
- 实现 `reference_my_op(...)` 并注册它：`register_impl("my_op", "torch")(reference_my_op)`。
- 使用 `create_benchmark_config()` 构建 `triton.testing.Benchmark` 配置（例如，按形状/dtype）。
- 在 `@triton.testing.perf_report([...])` 上 `bench_my_op(...)`；在基准测试函数内部：使用 `torch.testing.assert_close(fn(), ref(), ...)` 进行正确性检查，然后 `ms = triton.testing.do_bench(fn)`（或 `do_bench_cudagraph`），计算 GB/s 或 TFLOPS，并返回指标。
- 入口点：`if __name__ == "__main__": bench_my_op.run(print_data=True)`。

模板结构：

```python
import torch
import triton
import triton.testing

import tilegym
from tilegym.backend import is_backend_available, register_impl

ALL_BACKENDS = [
    ("cutile", "cuTile", ("orange", "-")) if is_backend_available("cutile") else None,
    ("torch", "PyTorch", ("green", "-")),
]

def get_supported_backends():
    return [p for p in ALL_BACKENDS if p is not None]

def reference_my_op(input: torch.Tensor, out: torch.Tensor = None, **kwargs):
    """使用 PyTorch 的参考实现。"""
    ...

register_impl("my_op", "torch")(reference_my_op)

def create_benchmark_config(datatype, ...):
    available_backends = get_supported_backends()
    if not available_backends:
        return None
    backends, names, styles = zip(*available_backends)
    return triton.testing.Benchmark(
        x_names=["M"],  # 或其他维度名称
        x_vals=[...],
        line_arg="backend",
        line_vals=list(backends),
        line_names=list(names),
        styles=list(styles),
        ylabel="GB/s",  # 或 TFLOPS
        plot_name="my-op-...",
        args={"datatype": datatype, ...},
    )

@triton.testing.perf_report([
    create_benchmark_config(datatype, ...)
    for datatype in [torch.float16, torch.float32]
    for ... in [...]
])
def bench_my_op(M, backend, datatype, ..., device="cuda"):
    x = torch.randn(..., dtype=datatype, device=device)

    fn = lambda: tilegym.ops.my_op(x, backend=backend)
    ref = lambda: reference_my_op(x)
    torch.testing.assert_close(fn(), ref(), rtol=1e-2, atol=1e-2)

    ms = triton.testing.do_bench(fn)  # 或 do_bench_cudagraph(fn)
    # 从 ms 和问题规模计算指标（例如，GB/s 或 TFLOPS）
    return metric

if __name__ == "__main__":
    bench_my_op.run(print_data=True)
```

**基准测试图名称**：必须包含 `-TFLOPS` 或 `-GBps` 后缀
  - 示例：`plot_name=f"persistent-layer-norm-M{num_rows}-{dtype_name}-GBps"`

## 第 6 步：验证

```bash
# 运行测试
pytest tests/ops/test_my_op.py -v

# 运行基准测试（可选）
python tests/benchmark/bench_my_op.py

# 代码风格检查
pre-commit run -a
```
