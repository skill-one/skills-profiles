# Core ML Swift 集成

在 iOS 应用中加载、配置和运行 Core ML 模型。这项技能涵盖了 Swift 方面：模型加载、预测、MLTensor、性能分析和部署。

> **范围边界**：Python 端的模型转换、优化（量化、调色板化、剪枝）和框架选择属于 `apple-on-device-ai` 技能。这项技能仅拥有 Swift 集成。

参见 [references/coreml-swift-integration.md](references/coreml-swift-integration.md) 以获取完整的代码模式，包括基于 actor 的缓存、批量推理、图像预处理和测试。

## 内容

- [加载模型](#加载模型)
- [模型配置](#模型配置)
- [进行预测](#进行预测)
- [MLTensor (iOS 18+)](#mltensor-ios-18)
- [使用 MLMultiArray](#使用-mlmultiarray)
- [图像预处理](#图像预处理)
- [多模型管道](#多模型管道)
- [Vision 集成](#vision集成)
- [性能分析](#性能分析)
- [模型部署](#模型部署)
- [内存管理](#内存管理)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 加载模型

### 自动生成的类

当您将 `.mlmodel` 或 `.mlpackage` 添加到应用目标时，Xcode 会生成一个具有类型化输入/输出的 Swift 类。尽可能使用此功能。

```swift
import CoreML

let config = MLModelConfiguration()
config.computeUnits = .all

let model = try MyImageClassifier(configuration: config)
```

### 手动加载

当模型在运行时下载或存储在包外时，从 URL 加载。

```swift
let modelURL = Bundle.main.url(
    forResource: "MyModel", withExtension: "mlmodelc"
)!
let model = try MLModel(contentsOf: modelURL, configuration: config)
```

### 异步加载 (iOS 15+)

在不阻塞主线程的情况下加载模型。对于大型模型，请优先使用此方法。

```swift
let model = try await MLModel.load(
    contentsOf: modelURL,
    configuration: config
)
```

### 运行时编译 (iOS 16+)

在设备上将 `.mlpackage` 或 `.mlmodel` 编译为 `.mlmodelc`。这对于从服务器下载的模型很有用。对每个模型版本执行一次，而不是每次启动时都执行。

```swift
let compiledURL = try await MLModel.compileModel(at: packageURL)
let model = try await MLModel.load(contentsOf: compiledURL, configuration: config)
```

缓存编译后的 URL —— 每次启动时重新编译是一个错误。将 `compiledURL` 复制到持久位置（例如，应用程序支持）。在审查运行时加载的模型时，请一起指出这两个事实：异步 `MLModel.compileModel(at:)` 是 iOS 16+，编译后的模型必须缓存，因此应用不会每次启动时都重新编译。

## 模型配置

`MLModelConfiguration` 控制计算单元、GPU 访问和模型参数。

### 计算单元决策表

| 值 | 使用 | 选择时机 |
|---|---|---|
| `.all` | CPU + GPU + 神经引擎 | 默认。让系统决定。 |
| `.cpuOnly` | CPU | 确定性测试、CPU 仅回退或分析后显示加速器策略、争用、热状态或能量预算是限制因素后的约束工作。 |
| `.cpuAndGPU` | CPU + GPU | 需要 GPU 但模型有 ANE 不支持的运算。 |
| `.cpuAndNeuralEngine` (iOS 16+) | CPU + 神经引擎 | 兼容模型的最佳能效。 |

```swift
let config = MLModelConfiguration()
config.computeUnits = .cpuAndNeuralEngine

// 分析后和政策审查后的约束工作的可选回退
config.computeUnits = .cpuOnly
```

### 配置属性

```swift
let config = MLModelConfiguration()
config.computeUnits = .all
config.allowLowPrecisionAccumulationOnGPU = true // 更快，精度略有损失
```

## 进行预测

### 使用自动生成的类

生成的类提供类型化的输入/输出结构。

```swift
let model = try MyImageClassifier(configuration: config)
let input = MyImageClassifierInput(image: pixelBuffer)
let output = try model.prediction(input: input)
print(output.classLabel)        // "golden_retriever"
print(output.classLabelProbs)   // ["golden_retriever": 0.95, ...]
```

### 使用 MLDictionaryFeatureProvider

当输入是动态的或在编译时未知时使用。

```swift
let inputFeatures = try MLDictionaryFeatureProvider(dictionary: [
    "image": MLFeatureValue(pixelBuffer: pixelBuffer),
    "confidence_threshold": MLFeatureValue(double: 0.5),
])
let output = try model.prediction(from: inputFeatures)
let label = output.featureValue(for: "classLabel")?.stringValue
```

### 异步工作流中的预测

`MLModel.prediction(...)` 是同步的。在异步管道中，保持模型加载异步，然后在非主线程的 actor 或任务中运行预测，而无需在预测调用中添加 `await`。

```swift
let output = try model.prediction(from: inputFeatures)
```

### 批量预测

一次处理多个输入以提高吞吐量。

```swift
let batchInputs = try MLArrayBatchProvider(array: inputs.map { input in
    try MLDictionaryFeatureProvider(dictionary: ["image": MLFeatureValue(pixelBuffer: input)])
})
let batchOutput = try model.predictions(fromBatch: batchInputs)
for i in 0..<batchOutput.count {
    let result = batchOutput.features(at: i)
    print(result.featureValue(for: "classLabel")?.stringValue ?? "unknown")
}
```

使用 `predictions(fromBatch:)` 进行批量处理而不需要显式 `MLPredictionOptions`。仅当传递 `MLBatchProvider` 和 `MLPredictionOptions` 时使用 `predictions(from:options:)`；`predictions(from:)` 单独使用不是无选项的批量 API。

在批量处理之前验证代表性的单个输入。然后验证批量输出计数/顺序、特征类型、域不变性和与单个输入结果的协议。失败时，在重新运行测试用例和物理设备分析之前，修复确定性输入、形状、模型或配置问题。

### 状态预测 (iOS 18+)

对于跨预测维护状态的模型（序列模型、LLMs、音频累加器），使用 `MLState`。创建状态一次，并将它传递给每个预测调用。

```swift
let state = model.makeState()

// 每个同步预测都会传递内部模型状态
for frame in audioFrames {
    let input = try MLDictionaryFeatureProvider(dictionary: [
        "audio_features": MLFeatureValue(multiArray: frame)
    ])
    let output = try model.prediction(from: input, using: state)
    let classification = output.featureValue(for: "label")?.stringValue
}
```

`MLState` 是 `Sendable`，但 `Sendable` 并不保证一个状态对并发推理是安全的。使用相同状态的预测必须序列化；在预测运行时不要读取或写入状态缓冲区。为每个独立的并发流调用 `model.makeState()`。如果您需要 `MLPredictionOptions`，iOS 18+ 也提供了异步 `prediction(from:using:options:)` 重载；仍然适用同一时间只有一个状态规则。

## MLTensor (iOS 18+)

`MLTensor` 是用于预/后处理的 Swift 原生多维数组。操作惰性执行——调用 `await tensor.shapedArray(of:)` 以生成结果。

```swift
import CoreML

// 创建
let tensor = MLTensor([1.0, 2.0, 3.0, 4.0])
let zeros = MLTensor(zeros: [3, 224, 224], scalarType: Float.self)

// 调整形状
let reshaped = tensor.reshaped(to: [2, 2])

// 数学运算
let softmaxed = tensor.softmax(alongAxis: -1)
let centered = tensor - tensor.mean()

// 与 MLShapedArray / MLMultiArray 互操作
let shaped = await tensor.shapedArray(of: Float.self)
let multiArray = try MLMultiArray(shaped)
let shapedAgain = MLShapedArray<Float>(multiArray)
```

不要为统计或桥接发明 `MLTensor` API。避免例如 `MLTensor(multiArray)`、`tensor.std()`、`tensor.standardDeviation()`、直接惰性缓冲区访问或同步提取的示例；在张量管道外或使用源确认的张量操作执行不支持的 DSP/统计。

## 使用 MLMultiArray

`MLMultiArray` 是非图像模型输入和输出的主要数据交换类型。当自动生成的类期望数组类型特征时使用它。

```swift
// 创建一个 3D 数组：[批量, 序列, 特征]
let array = try MLMultiArray(shape: [1, 128, 768], dataType: .float32)

// 写入值
for i in 0..<128 {
    array[[0, i, 0] as [NSNumber]] = NSNumber(value: Float(i))
}

// 读取值
let value = array[[0, 0, 0] as [NSNumber]].floatValue

let data: [Float] = [1.0, 2.0, 3.0]
let shaped = MLShapedArray(scalars: data, shape: [3])
let fromShaped = try MLMultiArray(shaped)
```

参见 [references/coreml-swift-integration.md](references/coreml-swift-integration.md) 以获取高级 MLMultiArray 模式，包括 NLP 分词和音频特征提取。

## 图像预处理

图像模型期望 `CVPixelBuffer` 输入。使用 `CGImage` 转换来自相机或照片库的照片。Vision 的 `VNCoreMLRequest` 会自动处理此操作；仅当直接 `MLModel` 预测时才需要手动转换。

加载 [图像预处理](references/coreml-swift-integration.md#image-preprocessing)
以获取完整的已检查 `CVPixelBuffer` 转换和额外的归一化或裁剪模式。

## 多模型管道

当预处理或后处理需要单独的模型时，链式模型。

```swift
// 顺序推理：预处理器 -> 主模型 -> 后处理器
let preprocessed = try preprocessor.prediction(from: rawInput)
let mainOutput = try mainModel.prediction(from: preprocessed)
let finalOutput = try postprocessor.prediction(from: mainOutput)
```

对于 Xcode 管理的管道，在 `.mlpackage` 中使用管道模型类型。每个子模型都在其最佳计算单元上运行。

## Vision 集成

使用 Vision 以自动图像预处理（调整大小、归一化、颜色空间、方向）运行 Core ML 图像模型。

### 现代：CoreMLRequest (iOS 18+)

```swift
import Vision
import CoreML

let model = try MLModel(contentsOf: modelURL, configuration: config)
let request = CoreMLRequest(model: .init(model))
let results = try await request.perform(on: cgImage)

if let classification = results.first as? ClassificationObservation {
    print("\(classification.identifier): \(classification.confidence)")
}
```

### 传统：VNCoreMLRequest

```swift
let vnModel = try VNCoreMLModel(for: model)
let request = VNCoreMLRequest(model: vnModel) { request, error in
    guard let results = request.results as? [VNRecognizedObjectObservation] else { return }
    for observation in results {
        let label = observation.labels.first?.identifier ?? "unknown"
        let confidence = observation.labels.first?.confidence ?? 0
        let boundingBox = observation.boundingBox // 归一化坐标
        print("\(label): \(confidence) at \(boundingBox)")
    }
}
request.imageCropAndScaleOption = .scaleFill

let handler = VNImageRequestHandler(cvPixelBuffer: pixelBuffer)
try handler.perform([request])
```

> 完整的 Vision 框架模式（文本识别、条形码检测、文档扫描），请参阅 `vision-framework` 技能。

## 性能分析

### MLComputePlan (iOS 17.4+)

在运行预测之前检查每个操作将使用哪个计算设备。加载 [MLComputePlan 详细使用](references/coreml-swift-integration.md#mlcomputeplan-detailed-usage-ios-174)
以进行模型结构遍历、设备使用和估计成本检查。

### Instruments

使用 Instruments 中的 **Core ML** 仪器模板来分析：
- 模型加载时间
- 预测延迟（每个操作的分解）
- 计算设备调度（每个操作的 CPU/GPU/ANE）
- 内存分配

在调试器外运行以获取准确结果（Xcode: Product > Profile）。

## 模型部署

捆绑小型离线关键模型。优先使用 Background Assets 捆绑新的大型或可更新的资源；仅对现有的 ODR 项目保留 On-Demand Resources。一次编译下载的源模型，持久化按版本存储的 `.mlmodelc`，并在最低支持物理设备上测试加载、首次/重复预测、生命周期转换和内存。加载
[部署模式](references/coreml-swift-integration.md) 以获取实现细节。

## 内存管理

- **后台卸载**：当应用进入后台时释放模型引用以释放 GPU/ANE 内存。在返回前台时重新加载。
- **共享模型实例**：从不从同一编译模型创建多个 `MLModel` 实例。使用 actor 提供共享访问。
- **监控内存压力**：大型模型（>100 MB）可能会触发内存警告。注册 `UIApplication.didReceiveMemoryWarningNotification` 并在压力下释放缓存的模型。

参见 [references/coreml-swift-integration.md](references/coreml-swift-integration.md) 以获取基于 actor 的模型管理器，具有生命周期感知加载和缓存淘汰。

## 常见错误

**不要**：在主线程上加载模型。
**要**：使用 `MLModel.load(contentsOf:configuration:)` 异步 API 或在后台 actor 上加载。
**原因**：大型模型可能需要几秒钟才能加载，冻结 UI。

**不要**：忽略输入和模型期望之间的 `MLFeatureValue` 类型不匹配。
**要**：精确匹配类型——使用 `MLFeatureValue(pixelBuffer:)` 进行图像，而不是原始数据。
**原因**：类型不匹配会导致神秘的运行时崩溃或无声的错误结果。

**不要**：为每个预测创建新的 `MLModel` 实例。
**要**：加载一次并重用。使用 actor 管理模型生命周期。
**原因**：模型加载分配大量内存和计算资源。

**不要**：忽略模型加载和预测的错误处理。
**要**：捕获错误并在模型失败时提供回退行为。
**原因**：模型可能无法在旧设备上加载或在资源受限时失败。

**不要**：假设所有操作都在神经引擎上运行。
**要**：使用 `MLComputePlan` (iOS 17.4+) 验证每个操作的设备调度。
**原因**：不支持的运算回退到 CPU，这可能会使管道瓶颈。

**不要**：在传递给 Vision + Core ML 之前手动处理图像。
**要**：使用 `CoreMLRequest` (iOS 18+) 或 `VNCoreMLRequest` (传统) 让 Vision 处理预处理。
**原因**：Vision 正确处理方向、缩放和像素格式转换。

## 审查清单

- [ ] 异步加载模型（不阻塞主线程）
- [ ] `MLModelConfiguration.computeUnits` 设置适当的使用场景
- [ ] 模型实例跨预测重用（不是每次重新创建）
- [ ] 当可用时使用自动生成的类（类型化输入/输出）
- [ ] 模型加载和预测失败的错误处理
- [ ] 如果在运行时编译模型，则持久缓存编译后的模型
- [ ] 图像输入使用 Vision 管道 (`CoreMLRequest` iOS 18+ 或 `VNCoreMLRequest`) 进行正确的预处理
- [ ] 检查 `MLComputePlan` 以验证计算设备调度 (iOS 17.4+)
- [ ] 使用批量预测处理多个输入
- [ ] 模型大小适合部署策略（捆绑、Background Assets、ODR）
- [ ] 在目标设备上测试内存（尤其是内存较少的旧设备）
- [ ] 在调试器外运行预测以进行准确的性能测量

## 参考资料

- 模式和代码：[references/coreml-swift-integration.md](references/coreml-swift-integration.md)
- 模型转换和优化（Python 端）：在 `apple-on-device-ai` 技能中涵盖
- Apple 文档：[Core ML](https://sosumi.ai/documentation/coreml) |
  [MLModel](https://sosumi.ai/documentation/coreml/mlmodel) |
  [MLTensor](https://sosumi.ai/documentation/coreml/mltensor) |
  [MLComputePlan](https://sosumi.ai/documentation/coreml/mlcomputeplan-1w21n) |
  [Background Assets](https://sosumi.ai/documentation/backgroundassets)
