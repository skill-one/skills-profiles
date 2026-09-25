# 苹果平台上的设备端AI

关于选择、部署和优化设备端机器学习模型的指南。涵盖苹果基础模型、Core ML、MLX Swift和llama.cpp。

## 目录

- [框架选择路由器](#框架选择路由器)
- [苹果基础模型概述](#苹果基础模型概述)
- [Core ML概述](#core-ml-overview)
- [MLX Swift概述](#mlx-swift-overview)
- [多后端架构](#多后端架构)
- [性能最佳实践](#性能最佳实践)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考文献](#参考文献)

## 框架选择路由器

使用此决策树为您的用例选择合适的框架。

### 苹果基础模型

**使用场景：** 在iOS 26+ / macOS 26+设备上使用苹果智能（Apple Intelligence）进行文本生成、摘要、实体提取、结构化输出和简短对话。无需应用管理的API密钥、网络往返或模型托管；仍然处理系统模型资产就绪情况。

**最适合：**
- 使用`@Generable`类型生成文本或结构化数据
- 摘要、分类、内容标签
- 使用`Tool`协议进行工具增强生成
- 需要保证设备端隐私的应用

**不适合：** 复杂数学、代码生成、事实准确性任务，或针对iOS 26之前设备的应用。

### Core ML

**使用场景：** 在所有苹果平台上部署自定义训练的模型（视觉、NLP、音频）。使用coremltools将模型从PyTorch、TensorFlow或scikit-learn转换过来。

**最适合：**
- 图像分类、目标检测、分割
- 自定义NLP分类器、情感分析模型
- 通过SoundAnalysis集成的音频/语音模型
- 需要神经引擎优化的任何场景
- 需要量化、调色板化或剪枝的模型

### MLX Swift

**使用场景：** 在苹果硅（Apple Silicon）上运行特定的开源LLM（Llama、Mistral、Qwen、Gemma），以获得最大吞吐量。研究和原型设计。

**最适合：**
- 在苹果硅上最高持续token生成
- 从`mlx-community`运行Hugging Face模型
- 需要自动微分的研发
- 在Mac上进行微调工作流

### llama.cpp

**使用场景：** 使用GGUF模型格式进行跨平台LLM推理。需要广泛设备支持的生产行署。

**最适合：**
- GGUF量化模型（Q4_K_M、Q5_K_M、Q8_0）
- 跨平台应用（iOS + Android + 桌面）
- 与开源模型生态系统最大兼容性

### 快速参考

| 场景 | 框架 |
|---|---|
| 在苹果智能设备（iOS 26+）上进行文本生成 | 基础模型 |
| 来自设备端LLM的结构化输出 | 基础模型（`@Generable`） |
| 图像分类、目标检测 | Core ML |
| 来自PyTorch/TensorFlow的自定义模型 | Core ML + coremltools |
| 运行特定的开源LLM | MLX Swift或llama.cpp |
| 在苹果硅上最大吞吐量 | MLX Swift |
| 跨平台LLM推理 | llama.cpp |
| OCR和文本识别 | Vision框架 |
| 情感分析、NER、分词 | Natural Language框架 |
| 在设备上训练自定义分类器 | Create ML |

## 苹果基础模型概述

在苹果智能设备上使用系统语言模型进行短生成、摘要、标签、结构化输出和工具增强任务。在创建会话之前，对每个入口点进行门控：

```swift
import FoundationModels

switch SystemLanguageModel.default.availability {
case .available:
    guard SystemLanguageModel.default.supportsLocale(Locale.current) else {
        // 在生成之前使用区域设置回退
        break
    }
    // 继续使用模型
case .unavailable(.appleIntelligenceNotEnabled):
    // 引导用户在设置中启用苹果智能
case .unavailable(.modelNotReady):
    // 系统模型资产尚未就绪；显示加载状态
case .unavailable(.deviceNotEligible):
    // 设备无法运行苹果智能；使用回退
case .unavailable(let reason):
    // 未知或未来的不可用原因；使用回退并记录原因
}
```

然后创建会话并保持其共享上下文预算较小：

```swift
let session = LanguageModelSession {
    "你是一个有帮助的烹饪助手。"
}
session.prewarm()
let response = try await session.respond(to: "建议一个快速的意面食谱")
```

必要的护栏：

- 会话是有状态的，一次只接受一个请求；串行化访问，并在发出另一个响应之前检查`isResponding`。
- 指令、工具、模式、提示、文本记录和输出共享上下文窗口。只注册必要的工具，并保持模式紧凑。
- 使用`supportsLocale(_:)`解析区域设置；不要直接匹配语言列表。
- 将不受信任的用户内容放在提示中，永远不要放在指令中。系统护栏保持激活状态，因此请使用回退UI处理拒绝和其他生成错误。

当任务需要`@Generable`、`@Guide`、流式传输、工具定义、文本记录、生成选项、自定义适配器、提示设计或详细错误处理时，加载[基础模型参考](references/foundation-models.md)。

## Core ML概述

苹果用于部署训练模型的框架。自动调度到最佳计算单元（CPU、GPU或神经引擎）。

### 模型格式

| 格式 | 扩展名 | 使用场景 |
|---|---|---|
| `.mlpackage` | 目录（mlprogram） | 所有新模型（iOS 15+） |
| `.mlmodel` | 单个文件（neuralnetwork） | 仅限遗留（iOS 11-14） |
| `.mlmodelc` | 编译 | 预编译的，加载更快 |

始终为新工作使用mlprogram（`.mlpackage`）。

### 转换管道（coremltools）

```python
import coremltools as ct

# PyTorch转换（torch.jit.trace）
model.eval()  # 关键：始终在跟踪之前调用eval()
traced = torch.jit.trace(model, example_input)
mlmodel = ct.convert(
    traced,
    inputs=[ct.TensorType(shape=(1, 3, 224, 224), name="image")],
    minimum_deployment_target=ct.target.iOS18,
    convert_to='mlprogram',
)
mlmodel.save("Model.mlpackage")
```

### 验证、修复和重新转换

1. 在转换之前冻结代表性的源模型固定件和可接受的输出/任务容差。
2. 转换，然后通过源模型和Core ML模型运行相同的固定件。
3. 如果输出一致性或任务指标未达到容差，请检查形状、运算符、精度和预处理；修复转换并重新运行固定件。
4. 只有在未压缩的模型通过后才能压缩。每次压缩更改后重新验证准确性，并撤销或调整未达到阈值的更改。
5. 在物理目标设备上分析通过模型，然后重复，直到正确性、延迟、内存和包大小目标都通过。

### 与`coreml`的边界

这项技能拥有Python端的转换、压缩、分析和框架选择。使用同源的`coreml`技能进行Swift应用集成、预测API、运行时配置、Vision请求连接和详细模型加载。

> 参考[参考文献/coreml-conversion.md](references/coreml-conversion.md)以获取完整的转换管道，参考[参考文献/coreml-optimization.md](references/coreml-optimization.md)以获取优化技术。

## MLX Swift概述

苹果的Swift机器学习框架。通过统一内存架构在苹果硅上具有最高持续生成吞吐量。

### 加载和运行LLM

```swift
import MLX
import MLXLLM
import MLXLMCommon
import MLXLMHFAPI

let container = try await LLMModelFactory.shared.loadContainer(
    from: HubClient.default,
    using: TokenizersLoader(),
    configuration: .init(id: "mlx-community/Qwen3-4B-4bit")
)
let session = ChatSession(container)
print(try await session.respond(to: "你好"))
```

### 设备模型选择

| 设备 | RAM | 推荐模型 | RAM使用 |
|---|---|---|---|
| iPhone 12-14 | 4-6 GB | SmolLM2-135M或Qwen 2.5 0.5B | ~0.3 GB |
| iPhone 15 Pro+ | 8 GB | Gemma 3n E4B 4-bit | ~3.5 GB |
| Mac 8 GB | 8 GB | Llama 3.2 3B 4-bit | ~3 GB |
| Mac 16 GB+ | 16 GB+ | Mistral 7B 4-bit | ~6 GB |

### 内存管理

1. 在iOS上永远不要超过总RAM的60%
2. 设置MLX缓存限制：`Memory.cacheLimit = 512 * 1024 * 1024`
3. 在后台或内存压力时卸载MLX和llama.cpp模型；对于MLX，生成密集阶段后还调用`Memory.clearCache()`后
4. 使用"增加内存限制"权限进行更大的模型
5. 在物理苹果硅上验证MLX Swift和llama.cpp；模拟器无法执行依赖Metal的推理、内存或性能

> 参考[参考文献/mlx-swift.md](references/mlx-swift.md)以获取完整的MLX Swift模式和llama.cpp集成。

## 多后端架构

当应用需要多个AI后端（例如，基础模型+MLX回退）时：

```swift
func respond(to prompt: String) async throws -> String {
    if SystemLanguageModel.default.isAvailable {
        return try await foundationModelsRespond(prompt)
    } else if canLoadMLXModel() {
        return try await mlxRespond(prompt)
    } else {
        throw AIError.noBackendAvailable
    }
}
```

通过协调器角色串行化所有模型访问，以防止竞争：

```swift
actor ModelCoordinator {
    func withExclusiveAccess<T>(_ work: () async throws -> T) async rethrows -> T {
        try await work()
    }
}
```

对于自定义Core ML模型，在此处仅命名转换/优化交接：将Swift应用集成、模型加载、Vision连接和预测生命周期发送到`coreml`。除非产品明确选择非本地回退，否则将私密用户内容（如日记）保留在设备上。

## 性能最佳实践

1. 在调试器外运行以获取准确的基准（Xcode：Cmd-Opt-R，取消选中"调试可执行文件"）
2. 在用户交互之前调用`session.prewarm()`以用于基础模型
3. 将Core ML模型预编译为`.mlmodelc`以加快加载速度
4. 使用EnumeratedShapes而不是RangeDim以进行神经引擎优化
5. 使用4位调色板化以获得最佳的神经引擎内存/延迟收益
6. 将详细的Vision、Natural Language和Swift Core ML运行时集成交给同源的框架技能

## 常见错误

1. **没有可用性检查。** 在检查`SystemLanguageModel.default.availability`之前开始生成，导致不支持设备失败而不是回退UI。
2. **没有回退UI。** 在iOS 26之前或没有苹果智能的设备上什么也看不到。始终提供一个优雅的降级路径。
3. **超过上下文窗口。** token预算涵盖输入+输出。通过`tokenCount(for:)`监控使用情况，并在需要时进行总结。
4. **在单个会话上进行并发请求。** `LanguageModelSession`一次只支持一个请求。检查`session.isResponding`或串行化访问。
5. **指令中的不受信任内容。** 放在指令参数中的用户输入绕过了护栏边界。将用户内容放在提示中。
6. **跳过转换一致性检查。** 在固定的固定件上比较源和Core ML模型，然后修复并重新转换，然后再压缩或发货。
7. **在Core ML跟踪之前忘记`model.eval()`。PyTorch模型必须在跟踪之前处于eval模式。训练模式的伪影会破坏输出。
8. **使用neuralnetwork格式。** 始终使用`mlprogram`（.mlpackage）为新的Core ML模型。遗留的neuralnetwork格式已弃用。
9. **在iOS上超过60% RAM（MLX Swift）。** 大型模型会导致OOM杀死。
10. **信任MLX模拟器结果。** 在物理设备上验证依赖Metal的行为；模拟器只是一个UI/控制流冒烟测试。
11. **不清空MLX缓存。** 模型卸载与`Memory.clearCache()`配对。

## 审查清单

- [ ] 框架选择与用例和目标OS版本匹配
- [ ] 基础模型：在每次API调用之前检查可用性
- [ ] 基础模型：模型不可用时提供优雅的回退
- [ ] 基础模型：在用户交互之前调用预预热会话
- [ ] 基础模型：`@Generable`属性按逻辑生成顺序排列
- [ ] 基础模型：考虑token预算（检查`contextSize`）
- [ ] Core ML：模型格式是mlprogram（.mlpackage），适用于iOS 15+
- [ ] Core ML：源/Core ML一致性通过固定件和任务容差
- [ ] Core ML：压缩模型在物理目标上重新验证并分析
- [ ] MLX Swift：模型大小适合目标设备RAM
- [ ] MLX Swift：设置缓存限制，清除缓存，卸载模型
- [ ] 所有模型访问通过协调器角色串行化
- [ ] 并发：模型类型和工具实现是`Sendable`一致的或`@MainActor`隔离的
- [ ] 执行了物理设备测试（不是模拟器）

## 参考文献

- [基础模型API](references/foundation-models.md) -- LanguageModelSession, `@Generable`, 工具调用, 提示设计
- [Core ML转换](references/coreml-conversion.md) -- 从PyTorch、TensorFlow、其他框架转换模型
- [Core ML优化](references/coreml-optimization.md) -- 量化、调色板化、剪枝、性能调优
- [MLX Swift & llama.cpp](references/mlx-swift.md) -- MLX Swift模式，llama.cpp集成，内存管理
