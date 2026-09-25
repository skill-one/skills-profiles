# PhotoKit

面向 iOS 26+ 和 Swift 6.3 的照片选择、相机捕获、图像加载和媒体权限的现代模式。除非另有说明，否则这些模式向后兼容 iOS 16。有关完整的拾取器配方，请参阅 [references/photokit-patterns.md](references/photokit-patterns.md)，有关 AVCaptureSession 模式的信息，请参阅 [references/camera-capture.md](references/camera-capture.md)。

## 目录

- [PhotosPicker (SwiftUI, iOS 16+)](#photospicker-swiftui-ios-16)
- [隐私和权限](#privacy-and-permissions)
- [相机捕获基础](#camera-capture-basics)
- [图像加载和显示](#image-loading-and-display)
- [常见错误](#common-mistakes)
- [审查清单](#review-checklist)
- [参考资料](#references)

## PhotosPicker (SwiftUI, iOS 16+)

`PhotosPicker` 是 `UIImagePickerController` 的原生 SwiftUI 替代品。它在进程外运行，无需照片库权限即可浏览，并支持单选或多选以及媒体类型过滤。

### 单选

```swift
import SwiftUI
import PhotosUI

struct SinglePhotoPicker: View {
    @State private var selectedItem: PhotosPickerItem?
    @State private var selectedImage: Image?

    var body: some View {
        VStack {
            if let selectedImage {
                selectedImage
                    .resizable()
                    .scaledToFit()
                    .frame(maxHeight: 300)
            }

            PhotosPicker("选择照片", selection: $selectedItem, matching: .images)
        }
        .onChange(of: selectedItem) { _, newItem in
            Task {
                if let data = try? await newItem?.loadTransferable(type: Data.self),
                   let uiImage = UIImage(data: data) {
                    selectedImage = Image(uiImage: uiImage)
                }
            }
        }
    }
}
```

### 多选

```swift
struct MultiPhotoPicker: View {
    @State private var selectedItems: [PhotosPickerItem] = []
    @State private var selectedImages: [Image] = []

    var body: some View {
        VStack {
            ScrollView(.horizontal) {
                HStack {
                    ForEach(selectedImages.indices, id: \.self) { index in
                        selectedImages[index]
                            .resizable()
                            .scaledToFill()
                            .frame(width: 100, height: 100)
                            .clipShape(.rect(cornerRadius: 8))
                    }
                }
            }

            PhotosPicker(
                "选择照片",
                selection: $selectedItems,
                maxSelectionCount: 5,
                matching: .images
            )
        }
        .onChange(of: selectedItems) { _, newItems in
            Task {
                selectedImages = []
                for item in newItems {
                    if let data = try? await item.loadTransferable(type: Data.self),
                       let uiImage = UIImage(data: data) {
                        selectedImages.append(Image(uiImage: uiImage))
                    }
                }
            }
        }
    }
}
```

### 媒体类型过滤

使用 `PHPickerFilter` 组合以限制可选媒体：

```swift
// 仅图片
PhotosPicker(selection: $items, matching: .images)

// 仅视频
PhotosPicker(selection: $items, matching: .videos)

// 仅 Live Photos
PhotosPicker(selection: $items, matching: .livePhotos)

// 仅截图
PhotosPicker(selection: $items, matching: .screenshots)

// 图片和视频组合
PhotosPicker(selection: $items, matching: .any(of: [.images, .videos]))

// 图片排除截图
PhotosPicker(selection: $items, matching: .all(of: [.images, .not(.screenshots)]))
```

### 使用 Transferable 加载选定的项

`PhotosPickerItem` 通过 `loadTransferable(type:)` 异步加载内容。定义一个 `Transferable` 类型以自动解码：

```swift
struct PickedImage: Transferable {
    let data: Data
    let image: Image

    static var transferRepresentation: some TransferRepresentation {
        DataRepresentation(importedContentType: .image) { data in
            guard let uiImage = UIImage(data: data) else {
                throw TransferError.importFailed
            }
            return PickedImage(data: data, image: Image(uiImage: uiImage))
        }
    }
}

enum TransferError: Error {
    case importFailed
}

// 使用方法
if let picked = try? await item.loadTransferable(type: PickedImage.self) {
    selectedImage = picked.image
}
```

始终在 `Task` 中加载以避免阻塞主线程。处理 `nil` 返回和抛出的错误——用户可能选择了无法解码的格式。

## 隐私和权限

### 照片库访问级别

iOS 提供了两种照片库访问级别。当应用程序请求 `.readWrite` 访问权限时，系统会自动显示有限库拾取器——用户选择要共享的照片。

| 访问级别 | 描述 | Info.plist 键 |
|-------------|-------------|----------------|
| 仅添加 | 将照片写入库而不读取 | `NSPhotoLibraryAddUsageDescription` |
| 读写 | 全部或有限读取权限加上写入 | `NSPhotoLibraryUsageDescription` |

`PhotosPicker` 无需浏览权限——它在进程外运行，并且仅授予对选定项的访问权限。仅在需要读取整个库（例如自定义相册）或保存照片时请求明确权限。

### 检查和请求照片库权限

```swift
import Photos

func requestPhotoLibraryAccess() async -> PHAuthorizationStatus {
    let status = PHPhotoLibrary.authorizationStatus(for: .readWrite)

    switch status {
    case .notDetermined:
        return await PHPhotoLibrary.requestAuthorization(for: .readWrite)
    case .authorized, .limited:
        return status
    case .denied, .restricted:
        return status
    @unknown default:
        return status
    }
}
```

### 相机权限

将 `NSCameraUsageDescription` 添加到 Info.plist。在配置捕获会话之前检查和请求访问权限：

```swift
import AVFoundation

func requestCameraAccess() async -> Bool {
    let status = AVCaptureDevice.authorizationStatus(for: .video)

    switch status {
    case .notDetermined:
        return await AVCaptureDevice.requestAccess(for: .video)
    case .authorized:
        return true
    case .denied, .restricted:
        return false
    @unknown default:
        return false
    }
}
```

### 处理拒绝权限

当用户拒绝访问时，引导他们到设置。切勿重复提示或无声地隐藏功能。

```swift
struct PermissionDeniedView: View {
    let message: String
    @Environment(\.openURL) private var openURL

    var body: some View {
        ContentUnavailableView {
            Label("访问被拒绝", systemImage: "lock.shield")
        } description: {
            Text(message)
        } actions: {
            Button("打开设置") {
                if let url = URL(string: UIApplication.openSettingsURLString) {
                    openURL(url)
                }
            }
        }
    }
}
```

### 必要的 Info.plist 键

| 键 | 需要时 |
|-----|--------------|
| `NSPhotoLibraryUsageDescription` | 从库中读取照片 |
| `NSPhotoLibraryAddUsageDescription` | 将照片/视频保存到库 |
| `NSCameraUsageDescription` | 访问相机 |
| `NSMicrophoneUsageDescription` | 录制音频（带声音的视频） |

省略必要的键会导致在权限对话框出现时发生运行时崩溃。

## 相机捕获基础

在专用控制器中拥有每个捕获会话，并在相同的非主执行器上序列化配置、`startRunning()` 和 `stopRunning()`。切勿将主角色配置与分离的启动/停止任务混合：`beginConfiguration()`/`commitConfiguration()` 和会话状态更改不得竞争。可表示视图仅显示预览。

### 最小相机管理器

加载 [Camera Capture](references/camera-capture.md) 以获取序列化控制器模式、照片/视频代理、对焦、手电筒、方向和扫描。关键生命周期是：

1. 在会话配置事务外部请求访问。
2. 在捕获执行器上，调用 `beginConfiguration()` 并立即安装 `defer { commitConfiguration() }`，以便每个早期退出都平衡事务。
3. 仅在通过 `canAddInput`/`canAddOutput` 检查后添加输入和输出。
4. 在相同的执行器上启动或停止，然后在同步调用返回后仅在主角色上发布 UI 状态。
5. 在失败时，停止，恢复一个全新的会话实例，修复配置，并重新运行授权、后台/前台、中断和捕获检查。

### SwiftUI 中的相机预览

将 `AVCaptureVideoPreviewLayer` 包装在 `UIViewRepresentable` 中。覆盖 `layerClass` 以自动调整大小：

```swift
import SwiftUI
import AVFoundation

struct CameraPreview: UIViewRepresentable {
    let session: AVCaptureSession

    func makeUIView(context: Context) -> PreviewView {
        let view = PreviewView()
        view.previewLayer.session = session
        view.previewLayer.videoGravity = .resizeAspectFill
        return view
    }

    func updateUIView(_ uiView: PreviewView, context: Context) {
        if uiView.previewLayer.session !== session {
            uiView.previewLayer.session = session
        }
    }
}

final class PreviewView: UIView {
    override class var layerClass: AnyClass { AVCaptureVideoPreviewLayer.self }
    var previewLayer: AVCaptureVideoPreviewLayer { layer as! AVCaptureVideoPreviewLayer }
}
```

### 在视图中使用相机

```swift
struct CameraScreen: View {
    @State private var cameraManager = CameraManager()

    var body: some View {
        ZStack(alignment: .bottom) {
            CameraPreview(session: cameraManager.session)
                .ignoresSafeArea()

            Button {
                // 拍照——请参阅 references/camera-capture.md
            } label: {
                Circle()
                    .fill(.white)
                    .frame(width: 72, height: 72)
                    .overlay(Circle().stroke(.gray, lineWidth: 3))
            }
            .padding(.bottom)
        }
        .task {
            await cameraManager.configure()
            cameraManager.start()
        }
        .onDisappear {
            cameraManager.stop()
        }
    }
}
```

始终在 `onDisappear` 中调用 `stop()`。正在运行的捕获会话独占使用相机并消耗电池。

## 图像加载和显示

### 用于远程图像的 AsyncImage

```swift
AsyncImage(url: imageURL) { phase in
    switch phase {
    case .empty:
        ProgressView()
    case .success(let image):
        image
            .resizable()
            .scaledToFill()
    case .failure:
        Image(systemName: "photo")
            .foregroundStyle(.secondary)
    @unknown default:
        EmptyView()
    }
}
.frame(width: 200, height: 200)
.clipShape(.rect(cornerRadius: 12))
```

`AsyncImage` 不会跨视图重绘缓存图像。对于具有许多图像的生产应用程序，请使用专用图像加载库或基于 `URLCache` 的缓存。

### 对大型图像进行降采样

从库中加载全分辨率照片到显示大小的 `CGImage` 以避免内存峰值。一张 48MP 照片在未压缩的情况下可能消耗超过 200 MB。

```swift
import ImageIO
import UIKit

func downsample(data: Data, to pointSize: CGSize, scale: CGFloat = UITraitCollection.current.displayScale) -> UIImage? {
    let maxDimensionInPixels = max(pointSize.width, pointSize.height) * scale

    let options: [CFString: Any] = [
        kCGImageSourceCreateThumbnailFromImageAlways: true,
        kCGImageSourceShouldCacheImmediately: true,
        kCGImageSourceCreateThumbnailWithTransform: true,
        kCGImageSourceThumbnailMaxPixelSize: maxDimensionInPixels
    ]

    guard let source = CGImageSourceCreateWithData(data as CFData, nil),
          let cgImage = CGImageSourceCreateThumbnailAtIndex(source, 0, options as CFDictionary) else {
        return nil
    }

    return UIImage(cgImage: cgImage)
}
```

在将用户选择的照片显示在列表、网格或缩略图时始终使用此方法。将 `PhotosPickerItem` 的原始 `Data` 直接传递给降采样器，然后再创建 `UIImage`。

### 图像渲染模式

```swift
// 原始：按其原始颜色显示图像
Image("photo")
    .renderingMode(.original)

// 模板：将图像视为掩码，由前景样式着色
Image(systemName: "heart.fill")
    .renderingMode(.template)
    .foregroundStyle(.red)
```

使用 `.original` 用于照片和艺术品。使用 `.template` 用于应采用当前色调的图标。

## 常见错误

**不要** 使用 `UIImagePickerController` 进行照片选择。
**要** 使用 `PhotosPicker`（SwiftUI）或 `PHPickerViewController`（UIKit）。
*原因*：`UIImagePickerController` 是遗留 API，功能有限。`PhotosPicker` 在进程外运行，支持多选，并且无需库权限即可浏览。

**不要** 在只需要用户选择照片时请求完整照片库访问。
**要** 使用 `PhotosPicker`，它无需权限，或者请求 `.readWrite` 并让系统处理有限访问。
*原因*：对于大多数选择和使用工作流，完整访问是不必要的。系统有限的库拾取器尊重用户隐私，并且仍然授予对选定项的访问权限。

**不要** 将全分辨率图像加载到内存中以用于缩略图。
**要** 使用 `CGImageSource` 和 `kCGImageSourceThumbnailMaxPixelSize` 进行降采样。一张 48MP 照片在未压缩的情况下超过 200 MB。

**不要** 在加载 `PhotosPickerItem` 数据时阻塞主线程。
**要** 在 `Task` 中使用 `async loadTransferable(type:)`。

**不要** 在视图消失时忘记停止 `AVCaptureSession`。
**要** 在 `onDisappear` 或 `dismantleUIView` 中调用 `session.stopRunning()`。

**不要** 假设相机访问已授予而未检查。
**要** 检查 `AVCaptureDevice.authorizationStatus(for: .video)` 并处理 `.denied`/`.restricted`。

**不要** 在主线程上调用 `session.startRunning()`。
**要** 在拥有配置和停止操作的相同专用串行执行器上运行它。
*原因*：`startRunning()` 是一个同步阻塞调用，在硬件初始化时可能需要数百毫秒。

**不要** 在 `UIViewRepresentable` 中创建 `AVCaptureSession`。
**要** 在单独的 `@Observable` 模型中拥有会话。

## 审查清单

- [ ] 使用 `PhotosPicker` 而不是过时的 `UIImagePickerController`
- [ ] Info.plist 中的相机/照片库隐私描述
- [ ] 异步图像/视频加载的加载状态处理
- [ ] 在显示之前使用 `CGImageSource` 对大型图像进行降采样
- [ ] 相机会话在后台线程启动；在 `onDisappear` 中停止
- [ ] 权限拒绝通过设置深度链接处理
- [ ] `AVCaptureSession` 由模型拥有，而不是在 `UIViewRepresentable` 中创建
- [ ] 媒体资产类型和拾取器结果在并发边界之间是 `Sendable`

## 参考资料

- [references/photokit-patterns.md](references/photokit-patterns.md) — 拾取器模式、媒体加载、HEIC 处理
- [references/camera-capture.md](references/camera-capture.md) — AVCaptureSession、照片/视频捕获、二维码扫描
- [references/image-loading-caching.md](references/image-loading-caching.md) — AsyncImage、缓存、降采样
- [references/av-playback.md](references/av-playback.md) — AVPlayer、流式传输、音频
