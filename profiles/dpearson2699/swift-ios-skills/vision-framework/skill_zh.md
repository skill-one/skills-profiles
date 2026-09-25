# 视觉框架

使用设备端的计算机视觉检测图像和视频中的文本、人脸、条形码、物体和人体姿态。优先使用现代 iOS 18+ 的请求 API，仅在部署目标需要时加载遗留参考。

有关完整的代码模式和 [DataScannerViewController](references/visionkit-scanner.md) 集成，请参阅 [references/vision-requests.md](references/vision-requests.md)。

## 内容

- [两个 API 版本](#两个-api-版本)
- [请求模式（现代 API）](#请求模式现代-api)
- [文本识别（OCR）](#文本识别-ocr)
- [人脸检测](#人脸检测)
- [条形码检测](#条形码检测)
- [文档扫描（iOS 26+）](#文档扫描-ios-26)
- [图像分割](#图像分割)
- [物体跟踪](#物体跟踪)
- [其他请求类型](#其他请求类型)
- [Core ML 集成](#core-ml-集成)
- [VisionKit: DataScannerViewController](#visionkit-datascannerviewcontroller)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 两个 API 版本

Vision 有两个不同的 API 层。对于新代码，优先使用现代 API：
Swift 原生的请求类型加上 `try await request.perform(on:)`。将 `VN*`、
`VNImageRequestHandler`、`VNSequenceRequestHandler`、完成处理程序和遗留的 `CGRect` 辅助函数保留在显式的遗留回退部分或文件中。

| 方面 | 现代（iOS 18+） | 遗留 |
|---|---|---|
| 模式 | `let result = try await request.perform(on: image)` | `VNImageRequestHandler` + 完成处理程序 |
| 请求类型 | Swift 类型 — 结构和类 (`RecognizeTextRequest`, `DetectFaceRectanglesRequest`) | ObjC 类 (`VNRecognizeTextRequest`, `VNDetectFaceRectanglesRequest`) |
| 并发性 | 原生异步/等待 | 完成处理程序或同步 `perform` |
| 观察 | 带有类型返回值 | 将 `results` 从 `[Any]` 转换为 |
| 可用性 | iOS 18+ / macOS 15+ | iOS 11+ |

现代 API 使用 `ImageProcessingRequest` 协议。每种请求类型都有一个 `perform(on:orientation:)` 方法，该方法接受 `CGImage`、`CIImage`、`CVPixelBuffer`、`CMSampleBuffer`、`Data` 或 `URL`。大多数请求是结构；状态请求，例如 `GeneratePersonSegmentationRequest`、
`TrackObjectRequest`、`TrackRectangleRequest` 和 `DetectTrajectoriesRequest` 是最终类。

## 请求模式（现代 API）

所有现代 Vision 请求都遵循相同的模式：创建请求、调用 `perform(on:)` 并处理类型化的结果。

```swift
import Vision

func recognizeText(in image: CGImage) async throws -> [String] {
    var request = RecognizeTextRequest()
    request.recognitionLevel = .accurate
    request.recognitionLanguages = [Locale.Language(identifier: "en-US")]

    let observations = try await request.perform(on: image)
    return observations.compactMap { observation in
        observation.topCandidates(1).first?.string
    }
}
```

### 遗留模式（iOS 18 之前）

对于 iOS 18 之前的靶标，使用相应的 `VNRequest` 并配合 `VNImageRequestHandler` 或 `VNSequenceRequestHandler`。加载 [references/vision-requests.md](references/vision-requests.md) 以获取完整的遗留请求和处理程序模式。

## 文本识别（OCR）

### 现代：RecognizeTextRequest（iOS 18+）

```swift
var request = RecognizeTextRequest()
request.recognitionLevel = .accurate       // .fast 用于实时
request.recognitionLanguages = [
    Locale.Language(identifier: "en-US"),
    Locale.Language(identifier: "fr-FR"),
]
request.usesLanguageCorrection = true
request.customWords = ["SwiftUI", "Xcode"] // 特定领域的术语

let observations = try await request.perform(on: cgImage)
for observation in observations {
    guard let candidate = observation.topCandidates(1).first else { continue }
    let text = candidate.string
    let confidence = candidate.confidence  // 0.0 ... 1.0
    let bounds = observation.boundingBox   // NormalizedRect
}
```

### 遗留：VNRecognizeTextRequest

遗留请求使用字符串语言标识符，并在参考中使用处理程序模式；两个版本都支持准确和快速识别级别。

## 人脸检测

检测人脸矩形、地标（眼睛、鼻子、嘴巴）和捕获质量。

```swift
// 现代 API
let faceRequest = DetectFaceRectanglesRequest()
let faces = try await faceRequest.perform(on: cgImage)

for face in faces {
    let boundingBox = face.boundingBox   // NormalizedRect
    let roll = face.roll                 // Measurement<UnitAngle>
    let yaw = face.yaw                  // Measurement<UnitAngle>
}

// 地标（眼睛、鼻子、嘴巴轮廓）
var landmarkRequest = DetectFaceLandmarksRequest()
let landmarkFaces = try await landmarkRequest.perform(on: cgImage)
for face in landmarkFaces {
    let landmarks = face.landmarks
    let leftEye = landmarks?.leftEye.points
    let nose = landmarks?.nose.points
}
```

### 坐标系统

Vision 使用以左下角为原点的标准化坐标系。在显示之前将其转换为 UIKit（以左上角为原点）：

```swift
import Vision

func imageRectForDisplay(_ rect: NormalizedRect, imageSize: CGSize) -> CGRect {
    rect.toImageCoordinates(imageSize, origin: .upperLeft)
}
```

## 条形码检测

检测 1D 和 2D 条形码，包括 QR 码。

```swift
var request = DetectBarcodesRequest()
let symbologies: [BarcodeSymbology] = [.qr, .ean13, .code128, .pdf417]
request.symbologies = symbologies

let barcodes = try await request.perform(on: cgImage)
for barcode in barcodes {
    let payload = barcode.payloadString          // 解码内容
    let symbology = barcode.symbology            // .qr, .ean13, 等。
    let bounds = barcode.boundingBox             // NormalizedRect
}
```
首先类型注解本地值，然后单独分配请求属性。

## 文档扫描（iOS 26+）

`RecognizeDocumentsRequest` 提供结构化文档阅读，其布局理解超出基本 OCR。返回具有嵌套 `Container` 结构的 `DocumentObservation` 对象，用于段落、表格、列表和条形码。
目前，Vision 为每个图像返回一个文档观察对象。

```swift
var request = RecognizeDocumentsRequest()
let documents = try await request.perform(on: cgImage)

for observation in documents {
    let container = observation.document

    // 完整文本内容
    let fullText = container.text

    // 结构化访问段落
    for paragraph in container.paragraphs {
        let paragraphText = paragraph.text
    }

    // 表格和列表
    for table in container.tables { /* 结构化表格数据 */ }
    for list in container.lists { /* 结构化列表数据 */ }

    // 文档中检测到的嵌入式条形码
    for barcode in container.barcodes { /* 条形码数据 */ }

    // 如果检测到文档标题
    if let title = container.title { print(title) }
}
```

对于更简单的文档相机扫描，请使用 VisionKit 的
`VNDocumentCameraViewController`，它提供全屏相机 UI，具有自动捕获、透视校正和多页扫描功能。

## 图像分割

### 现代：GeneratePersonSegmentationRequest（iOS 18+）

```swift
var request = GeneratePersonSegmentationRequest()
request.qualityLevel = .accurate  // .balanced, .fast

let mask = try await request.perform(on: cgImage)
// mask 是一个 PixelBufferObservation，具有 pixelBuffer 属性
let maskBuffer = mask.pixelBuffer
// 使用 Core Image 应用掩码：CIFilter.blendWithMask()
```

### 遗留：VNGeneratePersonSegmentationRequest

对于较旧的靶标，`VNGeneratePersonSegmentationRequest` 通过第一个像素缓冲区观察值暴露其掩码；使用参考的处理程序和掩码组合配方。

质量级别：
- `.accurate` -- 最佳质量，最慢 (~1s)，全分辨率
- `.balanced` -- 良好质量，中等速度 (~100ms)，960x540
- `.fast` -- 最低质量，最快 (~10ms)，256x144，适合实时

### 实例分割（iOS 18+）

为每个人分离掩码，用于单独效果。

```swift
// 现代 API (iOS 18+)
let request = GeneratePersonInstanceMaskRequest()
let observation = try await request.perform(on: cgImage)
let indices = observation.allInstances

for index in indices {
    let mask = try observation.generateMask(for: IndexSet(integer: index))
    // mask 是一个 CVPixelBuffer，仅此人的可见
}
```

```swift
// 遗留 API (iOS 17+)
let request = VNGeneratePersonInstanceMaskRequest()
let handler = VNImageRequestHandler(cgImage: cgImage)
try handler.perform([request])

guard let result = request.results?.first else { return }
let indices = result.allInstances
for index in indices {
    let instanceMask = try result.generateMaskedImage(
        ofInstances: IndexSet(integer: index),
        from: handler,
        croppedToInstancesExtent: false
    )
}
```

有关掩码组合和 Core Image 过滤器集成模式，请参阅 [references/vision-requests.md](references/vision-requests.md)。

## 物体跟踪

### 现代：TrackObjectRequest（iOS 18+）

`TrackObjectRequest` 是一个状态请求，它跨帧维护跟踪上下文。

```swift
// 使用检测到的物体的边界框初始化
let initialObservation = DetectedObjectObservation(boundingBox: detectedBox)
let request = TrackObjectRequest(detectedObject: initialObservation)

for pixelBuffer in framePixelBuffers {
    let results = try await request.perform(on: pixelBuffer)
    if let tracked = results.first {
        let updatedBounds = tracked.boundingBox  // NormalizedRect
    }
}
```

现代 `TrackObjectRequest` 没有跟踪级别或质量级别。

### 遗留：VNTrackObjectRequest

对于较旧的靶标，使用 `VNTrackObjectRequest` 并配合一个保留的 `VNSequenceRequestHandler`，并将每个结果作为下一个输入观察值反馈。参考包含完整的循环。

## 其他请求类型

Vision 提供其他请求，在 [references/vision-requests.md](references/vision-requests.md) 中涵盖：

| 请求 | 目的 |
|---|---|
| `ClassifyImageRequest` | 对场景内容进行分类（户外、食物、动物等） |
| `GenerateAttentionBasedSaliencyImageRequest` | 单个 `SaliencyImageObservation`，用于观众关注的位置 |
| `GenerateObjectnessBasedSaliencyImageRequest` | 单个 `SaliencyImageObservation`，用于物体区域 |
| `GenerateForegroundInstanceMaskRequest` | 前景物体分割（非特定于人） |
| `DetectRectanglesRequest` | 检测矩形形状（文档、卡片、屏幕） |
| `DetectHorizonRequest` | 检测地平线角度，用于自动校正照片 |
| `DetectHumanBodyPoseRequest` | 检测身体关节（肩膀、肘部、膝盖） |
| `DetectHumanBodyPose3DRequest` | 3D 人体姿态估计 |
| `DetectHumanHandPoseRequest` | 检测手关节和手指位置 |
| `DetectAnimalBodyPoseRequest` | 检测动物身体关节位置 |
| `DetectFaceCaptureQualityRequest` | 人脸捕获质量评分（0–1），用于照片选择 |
| `TrackRectangleRequest` | 跨视频帧跟踪矩形物体 |
| `TrackOpticalFlowRequest` | 视频帧之间的光流 |
| `DetectTrajectoriesRequest` | 检测视频中的物体轨迹 |

上述所有现代请求类型都是 iOS 18+ / macOS 15+。

## Core ML 集成

通过 Vision 运行自定义 Core ML 模型，以进行自动图像预处理。

Vision 使用 `CoreMLRequest` 或 `VNCoreMLRequest` 运行已准备好的模型；
将转换、分析、打包和生命周期决策交给 `coreml`。

```swift
import CoreML
import Vision

// 现代 API (iOS 18+): CoreMLRequest 接受 CoreMLModelContainer。
let model = try MLModel(contentsOf: modelURL)
let container = try CoreMLModelContainer(model: model, featureProvider: nil)
let request = CoreMLRequest(model: container)
let results = try await request.perform(on: cgImage)

// 分类模型
if let classification = results.first as? ClassificationObservation {
    let label = classification.identifier
    let confidence = classification.confidence
}
```
`CoreMLModelContainer` 是 iOS 18+ Vision 的公共容器，用于 `CoreMLRequest`：加载 `MLModel`，使用 `CoreMLModelContainer(model:featureProvider:)` 包装它，然后将该容器传递给 `CoreMLRequest(model:)`。通过 Vision 审查 Core ML 时映射结果：分类器产生 `ClassificationObservation`，图像输出产生 `PixelBufferObservation`，通用预测器产生 `CoreMLFeatureValueObservation`。

```swift
// 遗留 API
let vnModel = try VNCoreMLModel(for: model)
let request = VNCoreMLRequest(model: vnModel) { request, error in
    guard let results = request.results as? [VNClassificationObservation] else { return }
    let topResult = results.first
}
let handler = VNImageRequestHandler(cgImage: cgImage)
try handler.perform([request])
```

## VisionKit: DataScannerViewController

`DataScannerViewController` 提供用于文本和条形码的实时相机扫描器；请参阅 [references/visionkit-scanner.md](references/visionkit-scanner.md)。VisionKit 使用
`VNBarcodeSymbology`；现代 `DetectBarcodesRequest` 使用 `BarcodeSymbology`。

### 快速入门

```swift
import AVFoundation
import Vision
import VisionKit

@MainActor
func presentScanner() async {
    // 在请求相机访问之前添加 NSCameraUsageDescription。
    guard await AVCaptureDevice.requestAccess(for: .video) else { return }
    guard DataScannerViewController.isSupported,
          DataScannerViewController.isAvailable else { return }

    let scannerSymbologies: [VNBarcodeSymbology] = [.qr, .ean13]
    let scanner = DataScannerViewController(
        recognizedDataTypes: [
            .text(languages: ["en"]),
            .barcode(symbologies: scannerSymbologies)
        ],
        qualityLevel: .balanced,
        recognizesMultipleItems: true,
        isHighFrameRateTrackingEnabled: true,
        isHighlightingEnabled: true
    )
    scanner.delegate = self
    present(scanner, animated: true) {
        // 在呈现后，在主线程上开始扫描。
        try? scanner.startScanning()
    }
}
```

### SwiftUI 集成

将 `DataScannerViewController` 包装在 `UIViewControllerRepresentable` 中，并在 `updateUIViewController` 中使用 `Task { @MainActor in try? controller.startScanning() }` 启动；请参阅 [references/visionkit-scanner.md](references/visionkit-scanner.md)。

## 常见错误

**不要**：对于新的 iOS 18+ 项目，使用遗留的 `VNImageRequestHandler` API。
**要**：使用现代 Swift 原生请求与 `perform(on:)` 和异步/等待。
**原因**：现代 API 提供类型安全、更好的 Swift 并发支持以及更清晰的错误处理。

**不要**：忘记在绘制边界框之前转换标准化坐标。
**要**：使用 `NormalizedRect.toImageCoordinates(_:origin:)` 对于现代观察值，或使用 `VNImageRectForNormalizedRect(_:_:_)` 对于遗留 `CGRect` 观察值。
**原因**：Vision 使用标准化坐标（0...1）并以左下角为原点；UIKit 使用点并以左上角为原点。

**不要**：在主线程上运行 Vision 请求。
**要**：在后台线程上执行请求或从分离的任务中异步/等待。
**原因**：图像分析是 CPU/GPU 密集型的，如果在主线程上运行，会阻塞 UI。

**不要**：对于实时相机馈电使用 `.accurate` 识别级别。
**要**：对于实时视频使用 `.fast`，对于静态图像或离线处理使用 `.accurate`。
**原因**：准确识别对于 30fps 视频来说太慢；快速识别以质量换取速度。

**不要**：将每个 Vision 观察值视为具有相同的属性。
**要**：在编写共享辅助程序之前，检查每种观察值类型是否具有边界框、置信度、有效载荷、掩码或角度字段。
**原因**：现代 Vision 返回强类型观察值，结果形状因请求而异。

**不要**：为每个视频帧重新创建状态跟踪请求。
**要**：保留相同的现代 `TrackObjectRequest` 实例，或使用 `VNSequenceRequestHandler` 与遗留跟踪请求。
**原因**：跟踪依赖于跨帧的时间上下文。

**不要**：当您只需要 QR 码时，请求所有条形码符号。
**要**：在请求中指定您需要的符号。
**原因**：较少的符号意味着更快的检测和更少的误报。

**不要**：假设 `DataScannerViewController` 在所有设备上都可用。
**要**：在呈现之前检查 `isSupported`（硬件）和 `isAvailable`（用户权限）。
**原因**：需要 A12+ 芯片；`isAvailable` 还检查相机访问授权。

## 审查清单

- [ ] 除非针对旧部署，否则使用现代 Vision API (iOS 18+)
- [ ] Vision 请求在主线程之外运行（异步/等待或后台队列）
- [ ] 在 UI 显示之前转换标准化坐标
- [ ] 应用置信度阈值以过滤低质量观察值
- [ ] 识别级别与使用案例匹配（`.fast` 用于视频，`.accurate` 用于静态图像）
- [ ] 当输入语言已知时，为文本识别设置语言提示
- [ ] 条形码符号仅限于仅需要那些
- [ ] 在呈现之前检查 `DataScannerViewController` 的可用性
- [ ] Info.plist 中包含 `NSCameraUsageDescription` 以用于 VisionKit
- [ ] 在呈现和扫描开始之前请求 VisionKit 相机访问
- [ ] 人体分割质量级别适合使用案例
- [ ] 在视频帧之间保留状态跟踪请求或 `VNSequenceRequestHandler`
- [ ] 错误处理涵盖请求失败和空结果

## 参考资料

- Vision 请求模式：[references/vision-requests.md](references/vision-requests.md)
- VisionKit 扫描器集成：[references/visionkit-scanner.md](references/visionkit-scanner.md)
- Apple 文档：[Vision](https://sosumi.ai/documentation/vision) |
  [VisionKit](https://sosumi.ai/documentation/visionkit) |
  [RecognizeTextRequest](https://sosumi.ai/documentation/vision/recognizetextrequest) |
  [DataScannerViewController](https://sosumi.ai/documentation/visionkit/datascannerviewcontroller) |
  [CoreMLRequest](https://sosumi.ai/documentation/vision/coremlrequest) |
  [CoreMLModelContainer](https://sosumi.ai/documentation/vision/coremlmodelcontainer)
