# 机器学习领域

> **第 3 层：领域约束**

## 领域约束 → 设计影响

| 领域规则 | 设计约束 | Rust 影响 |
|-------------|-------------------|------------------|
| 大数据 | 高效内存 | 零拷贝、流式处理 |
| GPU 加速 | CUDA/Metal 支持 | candle, tch-rs |
| 模型可移植性 | 标准格式 | ONNX |
| 批处理 | 吞吐量优先于延迟 | 批量推理 |
| 数值精度 | 浮点数处理 | ndarray, 仔细处理 f32/f64 |
| 可重复性 | 确定性 | 基于种子的随机数、版本控制 |

---

## 关键约束

### 内存效率

```
规则：避免复制大型张量
原因：内存带宽是瓶颈
Rust：引用、视图、原地操作
```

### GPU 利用率

```
规则：批量操作以提升 GPU 效率
原因：每个内核启动的 GPU 开销
Rust：批量大小、异步数据加载
```

### 模型可移植性

```
规则：使用标准模型格式
原因：用 Python 训练，用 Rust 部署
Rust：通过 tract 或 candle 的 ONNX
```

---

## 向下追踪 ↓

从约束到设计（第 2 层）：

```
"需要高效的数据管道"
    ↓ m10-performance：流式处理、批处理
    ↓ polars：惰性求值

"需要 GPU 推理"
    ↓ m07-并发：异步数据加载
    ↓ candle/tch-rs：CUDA 后端

"需要模型加载"
    ↓ m12-生命周期：惰性初始化、缓存
    ↓ tract：ONNX 运行时
```

---

## 用例 → 框架

| 用例 | 推荐 | 原因 |
|----------|-------------|-----|
| 仅推理 | tract (ONNX) | 轻量级、可移植 |
| 训练 + 推理 | candle, burn | 纯 Rust、GPU |
| PyTorch 模型 | tch-rs | 直接绑定 |
| 数据管道 | polars | 快速、惰性求值 |

## 关键 Crate

| 目的 | Crate |
|---------|-------|
| 张量 | ndarray |
| ONNX 推理 | tract |
| 机器学习框架 | candle, burn |
| PyTorch 绑定 | tch-rs |
| 数据处理 | polars |
| 嵌入 | fastembed |

## 设计模式

| 模式 | 目的 | 实现 |
|---------|---------|----------------|
| 模型加载 | 一次性、重用 | `OnceLock<Model>` |
| 批处理 | 吞吐量 | 收集后处理 |
| 流式处理 | 大数据 | 基于迭代器 |
| GPU 异步 | 并行 | 数据加载与计算并行 |

## 代码模式：推理服务器

```rust
use std::sync::OnceLock;
use tract_onnx::prelude::*;

static MODEL: OnceLock<SimplePlan<TypedFact, Box<dyn TypedOp>, Graph<TypedFact, Box<dyn TypedOp>>>> = OnceLock::new();

fn get_model() -> &'static SimplePlan<...> {
    MODEL.get_or_init(|| {
        tract_onnx::onnx()
            .model_for_path("model.onnx")
            .unwrap()
            .into_optimized()
            .unwrap()
            .into_runnable()
            .unwrap()
    })
}

async fn predict(input: Vec<f32>) -> anyhow::Result<Vec<f32>> {
    let model = get_model();
    let input = tract_ndarray::arr1(&input).into_shape((1, input.len()))?;
    let result = model.run(tvec!(input.into()))?;
    Ok(result[0].to_array_view::<f32>()?.iter().copied().collect())
}
```

## 代码模式：批量推理

```rust
async fn batch_predict(inputs: Vec<Vec<f32>>, batch_size: usize) -> Vec<Vec<f32>> {
    let mut results = Vec::with_capacity(inputs.len());

    for batch in inputs.chunks(batch_size) {
        // 将输入堆叠为批量张量
        let batch_tensor = stack_inputs(batch);

        // 执行批量推理
        let batch_output = model.run(batch_tensor).await;

        // 解堆叠结果
        results.extend(unstack_outputs(batch_output));
    }

    results
}
```

---

## 常见错误

| 错误 | 领域违规 | 修复 |
|---------|-----------------|-----|
| 拷贝张量 | 内存浪费 | 使用视图 |
| 单次推理 | GPU 利用率低 | 批量处理 |
| 每次请求加载模型 | 慢 | 单例模式 |
| 同步数据加载 | GPU 空闲 | 异步管道 |

---

## 向第 1 层追踪

| 约束 | 第 2 层模式 | 第 1 层实现 |
|------------|-----------------|------------------------|
| 内存效率 | 零拷贝 | ndarray 视图 |
| 模型单例 | 惰性初始化 | OnceLock<Model> |
| 批处理 | 分块迭代 | chunks() + 并行 |
| GPU 异步 | 并发加载 | tokio::spawn + GPU |

---

## 相关技能

| 当... | 查看 |
|------|-----|
| 性能 | m10-performance |
| 惰性初始化 | m12-生命周期 |
| 异步模式 | m07-并发 |
| 内存效率 | m01-所有权 |
