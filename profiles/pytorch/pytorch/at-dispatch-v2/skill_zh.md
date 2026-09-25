# AT_DISPATCH to AT_DISPATCH_V2 转换器

这个技能帮助将 PyTorch 的旧版 AT_DISPATCH 宏转换为新的 AT_DISPATCH_V2 格式，该格式定义在 `aten/src/ATen/Dispatch_v2.h` 中。

## 何时使用此技能

在以下情况下使用此技能：
- 将 AT_DISPATCH_* 宏转换为 AT_DISPATCH_V2
- 将 ATen 内核移植以使用新的调度 API
- 处理 `aten/src/ATen/native/` 中使用调度宏的文件
- 用户提到 "AT_DISPATCH"、"dispatch v2"、"Dispatch_v2.h" 或宏转换

## 快速参考

**旧格式：**
```cpp
AT_DISPATCH_ALL_TYPES_AND3(kBFloat16, kHalf, kBool, dtype, "kernel_name", [&]() {
  // lambda body
});
```

**新格式：**
```cpp
AT_DISPATCH_V2(dtype, "kernel_name", AT_WRAP([&]() {
  // lambda body
}), AT_EXPAND(AT_ALL_TYPES), kBFloat16, kHalf, kBool);
```

## 关键转换

1. **重新排序参数**：`scalar_type` 和 `name` 首先出现，然后是 lambda，然后是类型
2. **包装 lambda**：使用 `AT_WRAP(lambda)` 处理内部逗号
3. **展开类型组**：使用 `AT_EXPAND(AT_ALL_TYPES)` 而不是隐式展开
4. **列出单个类型**：在展开组后添加额外类型（kHalf, kBFloat16 等）
5. **添加包含**：在 Dispatch 包含附近添加 `#include <ATen/Dispatch_v2.h>`

## 说明

### 第 1 步：添加 Dispatch_v2.h 包含

在现有的 `#include <ATen/Dispatch.h>` 附近添加 v2 头文件：

```cpp
#include <ATen/Dispatch.h>
#include <ATen/Dispatch_v2.h>
```

暂时保留旧的 Dispatch.h 包含（其他代码可能还需要它）。

### 第 2 步：识别旧的调度模式

常见的转换模式：

- `AT_DISPATCH_ALL_TYPES_AND{2,3,4}(type1, type2, ..., scalar_type, name, lambda)`
- `AT_DISPATCH_FLOATING_TYPES_AND{2,3}(type1, type2, ..., scalar_type, name, lambda)`
- `AT_DISPATCH_ALL_TYPES_AND_COMPLEX_AND{2,3}(type1, ..., scalar_type, name, lambda)`
- `AT_DISPATCH_FLOATING_AND_COMPLEX_TYPES_AND{2,3}(type1, ..., scalar_type, name, lambda)`

### 第 3 步：将旧宏映射到类型组

识别与基本类型对应的类型组宏：

| 旧宏基础 | AT_DISPATCH_V2 类型组 |
|----------------|---------------------------|
| `ALL_TYPES` | `AT_EXPAND(AT_ALL_TYPES)` |
| `FLOATING_TYPES` | `AT_EXPAND(AT_FLOATING_TYPES)` |
| `INTEGRAL_TYPES` | `AT_EXPAND(AT_INTEGRAL_TYPES)` |
| `COMPLEX_TYPES` | `AT_EXPAND(AT_COMPLEX_TYPES)` |
| `ALL_TYPES_AND_COMPLEX` | `AT_EXPAND(AT_ALL_TYPES_AND_COMPLEX)` |

对于组合模式，使用多个 `AT_EXPAND()` 条目：
```cpp
// 旧：AT_DISPATCH_ALL_TYPES_AND_COMPLEX_AND2(...)
// 新：AT_EXPAND(AT_ALL_TYPES), AT_EXPAND(AT_COMPLEX_TYPES), type1, type2
```

### 第 4 步：提取单个类型

从 `AT_DISPATCH_*_AND2(type1, type2, ...)` 或 `AT_DISPATCH_*_AND3(type1, type2, type3, ...)` 中提取单个类型（type1, type2 等）。

这些成为类型组之后的尾随参数：
```cpp
AT_DISPATCH_V2(..., AT_EXPAND(AT_ALL_TYPES), kBFloat16, kHalf, kBool)
                                             ^^^^^^^^^^^^^^^^^^^^^^^^
                                             来自 AND3 的单个类型
```

### 第 5 步：转换为 AT_DISPATCH_V2

应用转换：

**模式：**
```cpp
AT_DISPATCH_V2(
  scalar_type,           // 1st: The dtype expression
  "name",                // 2nd: The debug string
  AT_WRAP(lambda),       // 3rd: The lambda wrapped in AT_WRAP
  type_groups,           // 4th+: Type groups with AT_EXPAND()
  individual_types       // Last: Individual types
)
```

**示例转换：**
```cpp
// BEFORE
AT_DISPATCH_ALL_TYPES_AND3(
    kBFloat16, kHalf, kBool,
    iter.dtype(),
    "min_values_cuda",
    [&]() {
      min_values_kernel_cuda_impl<scalar_t>(iter);
    }
);

// AFTER
AT_DISPATCH_V2(
    iter.dtype(),
    "min_values_cuda",
    AT_WRAP([&]() {
      min_values_kernel_cuda_impl<scalar_t>(iter);
    }),
    AT_EXPAND(AT_ALL_TYPES),
    kBFloat16, kHalf, kBool
);
```

### 第 6 步：处理多行 lambda

对于内部逗号或复杂表达式的 lambda，AT_WRAP 至关重要：

```cpp
AT_DISPATCH_V2(
    dtype,
    "complex_kernel",
    AT_WRAP([&]() {
      gpu_reduce_kernel<scalar_t, scalar_t>(
        iter,
        MinOps<scalar_t>{},
        thrust::pair<scalar_t, int64_t>(upper_bound(), 0)  // 逗号内部!
      );
    }),
    AT_EXPAND(AT_ALL_TYPES)
);
```

### 第 7 步：验证转换

检查：
- [ ] `AT_WRAP()` 包装了整个 lambda
- [ ] 类型组使用 `AT_EXPAND()`
- [ ] 单个类型没有 `AT_EXPAND()`（只是 `kBFloat16`，而不是 `AT_EXPAND(kBFloat16)`）
- [ ] 参数顺序是：scalar_type, name, lambda, types
- [ ] 添加了包含：`#include <ATen/Dispatch_v2.h>`

## 类型组参考

可用的类型组宏（使用 `AT_EXPAND()`）：

```cpp
AT_INTEGRAL_TYPES      // kByte, kChar, kInt, kLong, kShort
AT_FLOATING_TYPES      // kDouble, kFloat
AT_COMPLEX_TYPES       // kComplexDouble, kComplexFloat
AT_QINT_TYPES         // kQInt8, kQUInt8, kQInt32
AT_ALL_TYPES          // INTEGRAL_TYPES + FLOATING_TYPES
AT_ALL_TYPES_AND_COMPLEX  // ALL_TYPES + COMPLEX_TYPES
AT_INTEGRAL_TYPES_V2  // INTEGRAL_TYPES + unsigned types
AT_BAREBONES_UNSIGNED_TYPES  // kUInt16, kUInt32, kUInt64
AT_FLOAT8_TYPES       // Float8 variants
```

## 常见模式

### 模式：AT_DISPATCH_ALL_TYPES_AND2

```cpp
// Before
AT_DISPATCH_ALL_TYPES_AND2(kHalf, kBFloat16, dtype, "op", [&]() {
  kernel<scalar_t>(data);
});

// After
AT_DISPATCH_V2(dtype, "op", AT_WRAP([&]() {
  kernel<scalar_t>(data);
}), AT_EXPAND(AT_ALL_TYPES), kHalf, kBFloat16);
```

### 模式：AT_DISPATCH_FLOATING_TYPES_AND3

```cpp
// Before
AT_DISPATCH_FLOATING_TYPES_AND3(kHalf, kBFloat16, kFloat8_e4m3fn,
    tensor.scalar_type(), "float_op", [&] {
  process<scalar_t>(tensor);
});

// After
AT_DISPATCH_V2(tensor.scalar_type(), "float_op", AT_WRAP([&] {
  process<scalar_t>(tensor);
}), AT_EXPAND(AT_FLOATING_TYPES), kHalf, kBFloat16, kFloat8_e4m3fn);
```

### 模式：AT_DISPATCH_ALL_TYPES_AND_COMPLEX_AND2

```cpp
// Before
AT_DISPATCH_ALL_TYPES_AND_COMPLEX_AND2(
    kComplexHalf, kHalf,
    self.scalar_type(),
    "complex_op",
    [&] {
      result = compute<scalar_t>(self);
    }
);

// After
AT_DISPATCH_V2(
    self.scalar_type(),
    "complex_op",
    AT_WRAP([&] {
      result = compute<scalar_t>(self);
    }),
    AT_EXPAND(AT_ALL_TYPES),
    AT_EXPAND(AT_COMPLEX_TYPES),
    kComplexHalf,
    kHalf
);
```

## 边缘情况

### 案例 1：没有额外类型（罕见）

```cpp
// Before
AT_DISPATCH_ALL_TYPES(dtype, "op", [&]() { kernel<scalar_t>(); });

// After
AT_DISPATCH_V2(dtype, "op", AT_WRAP([&]() {
  kernel<scalar_t>();
}), AT_EXPAND(AT_ALL_TYPES));
```

### 案例 2：许多单个类型（AND4, AND5, 等）

```cpp
// Before
AT_DISPATCH_FLOATING_TYPES_AND4(kHalf, kBFloat16, kFloat8_e4m3fn, kFloat8_e5m2,
    dtype, "float8_op", [&]() { kernel<scalar_t>(); });

// After
AT_DISPATCH_V2(dtype, "float8_op", AT_WRAP([&]() {
  kernel<scalar_t>();
}), AT_EXPAND(AT_FLOATING_TYPES), kHalf, kBFloat16, kFloat8_e4m3fn, kFloat8_e5m2);
```

### 案例 3：没有捕获的 lambda

```cpp
// Before
AT_DISPATCH_ALL_TYPES_AND2(kHalf, kBool, dtype, "op", []() {
  static_kernel<scalar_t>();
});

// After
AT_DISPATCH_V2(dtype, "op", AT_WRAP([]() {
  static_kernel<scalar_t>();
}), AT_EXPAND(AT_ALL_TYPES), kHalf, kBool);
```

## AT_DISPATCH_V2 的优势

1. **宏名称中没有参数数量**：不需要不同的宏用于 AND2, AND3, AND4
2. **可组合的类型集**：使用 `AT_EXPAND()` 混合匹配类型组
3. **可扩展**：轻松添加更多类型而不会达到宏限制
4. **更清晰**：类型组是显式的，而不是隐式在宏名称中

## 重要说明

- 保留 `#include <ATen/Dispatch.h>` - 其他代码可能需要它
- `AT_WRAP()` 是强制性的 - 防止 lambda 中的逗号解析问题
- 类型组需要 `AT_EXPAND()`，单个类型不需要
- v2 API 在 `aten/src/ATen/Dispatch_v2.h` 中 - 参考它获取完整文档
- 查看头文件以了解用于重新生成宏实现的 Python 脚本

## 工作流程

当被要求转换 AT_DISPATCH 宏时：

1. 读取文件以识别所有 AT_DISPATCH 使用
2. 如果不存在，则添加 `#include <ATen/Dispatch_v2.h>`
3. 对于每个调度宏：
   - 识别模式并提取组件
   - 映射基本类型组
   - 提取单个类型
   - 构造 AT_DISPATCH_V2 调用
   - 使用编辑工具应用
4. 向用户显示完整的转换文件
5. 解释所做的更改

**不要**编译或测试代码 - 仅关注准确的转换。
