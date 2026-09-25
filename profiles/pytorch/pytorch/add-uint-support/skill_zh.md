# 为运算符添加无符号整数（uint）支持

这项技能通过更新运算符的 AT_DISPATCH 宏，帮助为 PyTorch 运算符添加对无符号整数类型（uint16、uint32、uint64）的支持。

## 使用场景

在以下情况下使用这项技能：
- 为运算符添加 uint16、uint32 或 uint64 支持
- 用户提到“无符号类型”、“uint 支持”、“精简无符号类型”
- 在内核中启用 kUInt16、kUInt32、kUInt64 支持
- 处理需要扩展类型覆盖范围的运算符实现

## 快速参考

**向现有调度添加无符号类型：**
```cpp
// 之前
AT_DISPATCH_V2(dtype, "op", AT_WRAP([&]() {
  kernel<scalar_t>();
}), AT_EXPAND(AT_ALL_TYPES));

// 之后（方法 1：显式添加无符号类型）
AT_DISPATCH_V2(dtype, "op", AT_WRAP([&]() {
  kernel<scalar_t>();
}), AT_EXPAND(AT_ALL_TYPES), AT_EXPAND(AT_BAREBONES_UNSIGNED_TYPES));

// 之后（方法 2：如果存在 AT_INTEGRAL_TYPES，使用 V2 整数类型）
AT_DISPATCH_V2(dtype, "op", AT_WRAP([&]() {
  kernel<scalar_t>();
}), AT_EXPAND(AT_INTEGRAL_TYPES_V2), AT_EXPAND(AT_FLOATING_TYPES));
```

## 类型组参考

**无符号类型组：**
- `AT_BAREBONES_UNSIGNED_TYPES`：kUInt16、kUInt32、kUInt64
- `AT_INTEGRAL_TYPES_V2`：AT_INTEGRAL_TYPES + AT_BAREBONES_UNSIGNED_TYPES

**关系：**
```cpp
AT_INTEGRAL_TYPES          // kByte, kChar, kInt, kLong, kShort
AT_BAREBONES_UNSIGNED_TYPES  // kUInt16, kUInt32, kUInt64
AT_INTEGRAL_TYPES_V2       // INTEGRAL_TYPES + BAREBONES_UNSIGNED_TYPES
```

## 操作步骤

### 第 1 步：确定是否需要转换为 V2

检查文件是否使用 AT_DISPATCH_V2：

**如果使用旧的 AT_DISPATCH：**
- 首先使用 at-dispatch-v2 技能转换为 AT_DISPATCH_V2
- 然后继续添加 uint 支持

**如果已经使用 AT_DISPATCH_V2：**
- 直接进行第 2 步

### 第 2 步：分析当前的调度宏

识别当前使用的类型组：
```cpp
AT_DISPATCH_V2(dtype, "op", AT_WRAP([&]() {
  // body
}), AT_EXPAND(AT_ALL_TYPES), kHalf, kBFloat16);
    ^^^^^^^^^^^^^^^^^^^^^^^^^
    当前类型覆盖范围
```

常见模式：
- `AT_EXPAND(AT_ALL_TYPES)` → 包括 AT_INTEGRAL_TYPES + AT_FLOATING_TYPES
- `AT_EXPAND(AT_INTEGRAL_TYPES)` → 仅支持有符号整数
- `AT_EXPAND(AT_FLOATING_TYPES)` → 仅支持浮点类型

### 第 3 步：选择 uint 添加方法

两种方法：

**方法 1：显式添加 AT_BAREBONES_UNSIGNED_TYPES**
- 使用场景：当你希望明确添加 uint 支持
- 向类型列表中添加 `AT_EXPAND(AT_BAREBONES_UNSIGNED_TYPES)`

**方法 2：用 AT_INTEGRAL_TYPES_V2 替换 AT_INTEGRAL_TYPES**
- 使用场景：当调度已经使用 `AT_EXPAND(AT_INTEGRAL_TYPES)`
- 更简洁：用一个类型组替换其超集
- 仅在 AT_INTEGRAL_TYPES 存在时适用

### 第 4 步：应用转换

**方法 1 示例：**
```cpp
// 之前
AT_DISPATCH_V2(
    dtype,
    "min_values_cuda",
    AT_WRAP([&]() {
      kernel_impl<scalar_t>(iter);
    }),
    AT_EXPAND(AT_ALL_TYPES),
    kBFloat16, kHalf, kBool
);

// 之后（添加无符号类型）
AT_DISPATCH_V2(
    dtype,
    "min_values_cuda",
    AT_WRAP([&]() {
      kernel_impl<scalar_t>(iter);
    }),
    AT_EXPAND(AT_ALL_TYPES),
    AT_EXPAND(AT_BAREBONES_UNSIGNED_TYPES),
    kBFloat16, kHalf, kBool
);
```

**方法 2 示例：**
```cpp
// 之前
AT_DISPATCH_V2(
    dtype,
    "integral_op",
    AT_WRAP([&]() {
      kernel<scalar_t>();
    }),
    AT_EXPAND(AT_INTEGRAL_TYPES)
);

// 之后（用 V2 替换）
AT_DISPATCH_V2(
    dtype,
    "integral_op",
    AT_WRAP([&]() {
      kernel<scalar_t>();
    }),
    AT_EXPAND(AT_INTEGRAL_TYPES_V2)
);
```

### 第 5 步：处理 AT_ALL_TYPES 与单独的类型组

如果调度使用 `AT_EXPAND(AT_ALL_TYPES)`：
- `AT_ALL_TYPES` = `AT_INTEGRAL_TYPES` + `AT_FLOATING_TYPES`
- 添加 uint：向列表中添加 `AT_EXPAND(AT_BAREBONES_UNSIGNED_TYPES)`

如果调度分别列出 INTEGRAL 和 FLOATING：
```cpp
// 之前
AT_EXPAND(AT_INTEGRAL_TYPES), AT_EXPAND(AT_FLOATING_TYPES)

// 之后（推荐使用方法 2）
AT_EXPAND(AT_INTEGRAL_TYPES_V2), AT_EXPAND(AT_FLOATING_TYPES)
```

### 第 6 步：验证所有调度位置

检查文件中所有需要 uint 支持的调度宏：
- 一些运算符有多个调度位置（CPU、CUDA、不同函数）
- 在所有位置一致地应用转换
- 确保每个位置都获得相同的类型覆盖更新

### 第 7 步：验证更改

检查：
- [ ] 使用 AT_DISPATCH_V2 格式（不使用旧的 AT_DISPATCH）
- [ ] 通过两种方法之一添加无符号类型
- [ ] 文件中所有相关的调度位置都已更新
- [ ] 类型组使用 `AT_EXPAND()`
- [ ] 参数格式正确且逗号分隔

## 常见模式

### 模式 1：AT_ALL_TYPES + 额外类型

```cpp
// 之前
AT_DISPATCH_V2(dtype, "op", AT_WRAP([&]() {
  kernel<scalar_t>();
}), AT_EXPAND(AT_ALL_TYPES), kHalf, kBFloat16);

// 之后
AT_DISPATCH_V2(dtype, "op", AT_WRAP([&]() {
  kernel<scalar_t>();
}), AT_EXPAND(AT_ALL_TYPES), AT_EXPAND(AT_BAREBONES_UNSIGNED_TYPES), kHalf, kBFloat16);
```

### 模式 2：分离的 INTEGRAL + FLOATING

```cpp
// 之前
AT_DISPATCH_V2(dtype, "op", AT_WRAP([&]() {
  kernel<scalar_t>();
}), AT_EXPAND(AT_INTEGRAL_TYPES), AT_EXPAND(AT_FLOATING_TYPES));

// 之后
AT_DISPATCH_V2(dtype, "op", AT_WRAP([&]() {
  kernel<scalar_t>();
}), AT_EXPAND(AT_INTEGRAL_TYPES_V2), AT_EXPAND(AT_FLOATING_TYPES));
```

### 模式 3：旧的调度需要先转换为 V2

```cpp
// 之前（需要先转换为 v2）
AT_DISPATCH_ALL_TYPES_AND2(kHalf, kBFloat16, dtype, "op", [&]() {
  kernel<scalar_t>();
});

// 转换为 v2 后
AT_DISPATCH_V2(dtype, "op", AT_WRAP([&]() {
  kernel<scalar_t>();
}), AT_EXPAND(AT_ALL_TYPES), kHalf, kBFloat16);

// 添加 uint 支持
AT_DISPATCH_V2(dtype, "op", AT_WRAP([&]() {
  kernel<scalar_t>();
}), AT_EXPAND(AT_ALL_TYPES), AT_EXPAND(AT_BAREBONES_UNSIGNED_TYPES), kHalf, kBFloat16);
```

## 多调度位置示例

对于包含多个函数的文件：

```cpp
void min_values_kernel_cuda(TensorIterator& iter) {
  AT_DISPATCH_V2(iter.dtype(), "min_values_cuda", AT_WRAP([&]() {
    impl<scalar_t>(iter);
  }), AT_EXPAND(AT_ALL_TYPES), AT_EXPAND(AT_BAREBONES_UNSIGNED_TYPES), kBFloat16, kHalf);
  //                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  //                           添加了 uint 支持
}

void min_launch_kernel(TensorIterator &iter) {
  AT_DISPATCH_V2(iter.input_dtype(), "min_cuda", AT_WRAP([&]() {
    gpu_reduce_kernel<scalar_t>(iter);
  }), AT_EXPAND(AT_ALL_TYPES), AT_EXPAND(AT_BAREBONES_UNSIGNED_TYPES), kBFloat16, kHalf);
  //                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  //                           这里也添加了 uint 支持
}
```

## 决策树

使用此决策树确定方法：

```
文件是否使用 AT_DISPATCH_V2?
├─ 否 → 首先使用 at-dispatch-v2 技能，然后继续
└─ 是
   └─ 是否使用 AT_EXPAND(AT_INTEGRAL_TYPES)?
      ├─ 是 → 用 AT_EXPAND(AT_INTEGRAL_TYPES_V2) 替换
      └─ 否 → 向类型列表中添加 AT_EXPAND(AT_BAREBONES_UNSIGNED_TYPES)
```

## 边缘情况

### 情况 1：仅调度浮点类型

如果运算符仅支持浮点类型，不要添加 uint 支持：

```cpp
// 保持原样 - 浮点类型运算符
AT_DISPATCH_V2(dtype, "float_op", AT_WRAP([&]() {
  kernel<scalar_t>();
}), AT_EXPAND(AT_FLOATING_TYPES), kHalf);
```

### 情况 2：存在复数类型

无符号类型可与复数类型一起使用：

```cpp
AT_DISPATCH_V2(dtype, "op", AT_WRAP([&]() {
  kernel<scalar_t>();
}), AT_EXPAND(AT_ALL_TYPES),
    AT_EXPAND(AT_BAREBONES_UNSIGNED_TYPES),
    AT_EXPAND(AT_COMPLEX_TYPES),
    kHalf, kBFloat16);
```

### 情况 3：已具有 uint 支持

检查是否已存在 uint 类型：
- 如果使用 `AT_INTEGRAL_TYPES_V2` → 已具有 uint 支持
- 如果列表中已包含 `AT_BAREBONES_UNSIGNED_TYPES` → 已具有 uint 支持
- 如果已存在 uint 支持，则跳过文件

## 工作流程

当被要求添加 uint 支持时：

1. 读取目标文件
2. 检查是否使用 AT_DISPATCH_V2：
   - 如果不使用 → 首先使用 at-dispatch-v2 技能
3. 识别所有调度宏位置
4. 对每个调度：
   - 分析当前类型组
   - 选择方法（添加 BAREBONES_UNSIGNED 或升级到 V2）
   - 使用编辑工具应用转换
5. 向用户展示更改
6. 解释修改内容

## 重要说明

- 始终检查是否需要 v2 转换
- 在文件的所有调度位置一致地应用更改
- 当适用时，方法 2（AT_INTEGRAL_TYPES_V2）更简洁
- 方法 1（显式 AT_BAREBONES_UNSIGNED_TYPES）更明确
- 无符号类型是：kUInt16、kUInt32、kUInt64（不是 kByte，它是 uint8）
- 某些运算符可能从语义上不支持无符号类型 - 需要判断

## 测试

添加 uint 支持后，运算符应接受 uint16、uint32 和 uint64 张量。用户负责功能测试。
