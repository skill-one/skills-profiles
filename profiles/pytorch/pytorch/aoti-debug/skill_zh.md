# AOTI 调试指南

这项技能有助于诊断和修复常见的 AOTInductor 问题。

## 错误模式路由

**检查错误信息并路由到相应的子指南：**

### Triton 索引越界
如果错误匹配此模式：
```
Assertion `index out of bounds: 0 <= tmpN < ksM` failed
```
**→ 跟随 `triton-index-out-of-bounds.md` 中的指南**

### 其他所有错误
继续执行下文中的部分。

---

## 第一步：始终检查设备和形状匹配

**对于任何 AOTI 错误（段错误、异常、崩溃、错误输出），始终首先检查以下内容：**

1. **编译设备 == 加载设备**：模型必须在与编译时相同的设备类型上加载
2. **输入设备匹配**：运行时输入必须在与编译模型相同的设备上
3. **输入形状匹配**：运行时输入形状必须与编译时使用的形状匹配（或满足动态形状约束）

```python
# 在编译期间 - 注意设备类型和形状
model = MyModel().eval()           # 哪个设备？CPU 或 .cuda()？
inp = torch.randn(2, 10)           # 哪个设备？什么形状？
compiled_so = torch._inductor.aot_compile(model, (inp,))

# 在加载期间 - 设备类型必须与编译时匹配
loaded = torch._export.aot_load(compiled_so, "???")  # 必须与上方的模型/输入设备匹配

# 在推理期间 - 设备和形状必须匹配
out = loaded(inp.to("???"))  # 必须与编译设备匹配，形状必须匹配
```

**如果其中任何一项不匹配，你将得到从段错误到异常到错误输出的各种错误。**

## 关键约束：设备类型匹配

**AOTI 要求编译和加载使用相同的设备类型。**

- 如果你 CUDA 编译，你必须 CUDA 加载（设备索引可以不同）
- 如果你 CPU 编译，你必须 CPU 加载
- 跨设备加载（例如，GPU 编译，CPU 加载）不受支持

## 常见错误模式

### 1. 设备不匹配段错误

**症状**：在 `aot_load()` 或模型执行期间发生段错误、异常或崩溃。

**示例错误信息**：
- `指定的指针位于主机内存上，并且未注册到任何 CUDA 设备`
- 在 AOTInductorModelBase 中加载常量时崩溃
- `期望输出张量具有设备 cuda:0，但得到的是 cpu`

**原因**：编译和加载设备类型不匹配（见“第一步”上述）。

**解决方案**：确保编译和加载使用相同的设备类型。如果 CPU 编译，则 CPU 加载。如果 CUDA 编译，则 CUDA 加载。

### 2. 运行时输入设备不匹配

**症状**：模型执行期间发生 RuntimeError。

**原因**：输入设备与编译设备不匹配（见“第一步”上述）。

**更好的调试**：使用 `AOTI_RUNTIME_CHECK_INPUTS=1` 获取更清晰的错误。此标志验证所有输入属性，包括设备类型、dtype、大小和 strides：
```bash
AOTI_RUNTIME_CHECK_INPUTS=1 python your_script.py
```

这将生成可操作的错误信息，例如：
```
Error: input_handles[0]: 设备类型不匹配，期望：0(cpu)，但得到：1(cuda)
```

## 调试 CUDA 非法内存访问 (IMA) 错误

如果你遇到 CUDA 非法内存访问错误，请遵循此系统方法：

### 第一步：基本检查

在深入挖掘之前，尝试使用这些调试标志：

```bash
AOTI_RUNTIME_CHECK_INPUTS=1
TORCHINDUCTOR_NAN_ASSERTS=1
```

这些标志在编译时（codegen 时）生效：

- `AOTI_RUNTIME_CHECK_INPUTS=1` 检查输入是否满足编译时使用的守卫
- `TORCHINDUCTOR_NAN_ASSERTS=1` 在每个内核之前和之后添加代码生成以检查 NaN

### 第二步：定位 CUDA IMA

CUDA IMA 错误可能是非确定性的。使用这些标志以确定性方式触发错误：

```bash
PYTORCH_NO_CUDA_MEMORY_CACHING=1
CUDA_LAUNCH_BLOCKING=1
```

这些标志在运行时生效：

- `PYTORCH_NO_CUDA_MEMORY_CACHING=1` 禁用 PyTorch 的缓存分配器，该分配器立即分配比需要的大得多的缓冲区。这通常是 CUDA IMA 错误非确定性的原因。
- `CUDA_LAUNCH_BLOCKING=1` 强制逐个启动内核。如果没有这个，你会得到“CUDA 内核错误可能异步报告”的警告，因为内核异步启动。

### 第三步：使用 AOTI 中间值调试器识别问题内核

使用 AOTI 中间值调试器定位问题内核：

```bash
AOT_INDUCTOR_DEBUG_INTERMEDIATE_VALUE_PRINTER=3
```

这将逐个在运行时打印内核。结合之前的标志，这显示了错误发生前启动了哪个内核。

要检查特定内核的输入：

```bash
AOT_INDUCTOR_FILTERED_KERNELS_TO_PRINT="triton_poi_fused_add_ge_logical_and_logical_or_lt_231,_add_position_embeddings_kernel_5" AOT_INDUCTOR_DEBUG_INTERMEDIATE_VALUE_PRINTER=2
```

如果内核的输入意外，请检查产生错误输入的内核。

## 其他调试工具

### 日志和跟踪

- **tlparse / TORCH_TRACE**：提供完整的输出代码和记录使用的守卫
- **TORCH_LOGS**：使用 `TORCH_LOGS="+inductor,output_code"` 查看更多 PT2 内部日志
- **TORCH_SHOW_CPP_STACKTRACES**：设置为 `1` 以查看更多 C++ 堆栈跟踪

### 常见问题来源

- **动态形状**：历史上是许多 IMA 的来源。在调试动态形状场景时请特别留意。
- **自定义操作**：特别是使用 C++ 实现且具有动态形状时。元函数可能需要 Symint 化。

## API 说明

### 已弃用 API
```python
torch._export.aot_compile()  # 已弃用
torch._export.aot_load()     # 已弃用
```

### 当前 API
```python
torch._inductor.aoti_compile_and_package()
torch._inductor.aoti_load_package()
```

新 API 将设备元数据存储在包中，因此 `aoti_load_package()` 自动使用正确的设备类型。你只能更改设备 *索引*（例如，cuda:0 vs cuda:1），不能更改设备 *类型*。

## 环境变量总结

| 变量 | 何时 | 目的 |
|------|------|------|
| `AOTI_RUNTIME_CHECK_INPUTS=1` | 编译时 | 验证输入匹配编译守卫 |
| `TORCHINDUCTOR_NAN_ASSERTS=1` | 编译时 | 在内核之前/之后检查 NaN |
| `PYTORCH_NO_CUDA_MEMORY_CACHING=1` | 运行时 | 使 IMA 错误确定性 |
| `CUDA_LAUNCH_BLOCKING=1` | 运行时 | 强制同步内核启动 |
| `AOT_INDUCTOR_DEBUG_INTERMEDIATE_VALUE_PRINTER=3` | 编译时 | 在运行时打印内核 |
| `TORCH_LOGS="+inductor,output_code"` | 运行时 | 查看PT2内部日志 |
| `TORCH_SHOW_CPP_STACKTRACES=1` | 运行时 | 显示 C++ 堆栈跟踪 |
