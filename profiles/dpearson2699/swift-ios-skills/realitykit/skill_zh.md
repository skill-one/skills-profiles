# RealityKit

使用 RealityKit 在 iOS 上构建 AR 体验，用于渲染和 ARKit 用于世界跟踪。涵盖 `RealityView`、实体管理、射线投射、场景理解和基于手势的交互。目标 Swift 6.3 / iOS 26+。

## 目录

- [设置](#设置)
- [RealityView 基础](#realityview-basics)
- [加载和创建实体](#loading-and-creating-entities)
- [锚定和放置](#anchoring-and-placement)
- [射线投射](#raycasting)
- [手势和交互](#gestures-and-interaction)
- [场景理解](#scene-understanding)
- [常见错误](#common-mistakes)
- [审查清单](#review-checklist)
- [参考资料](#references)

## 设置

### 项目配置

1. 在 Info.plist 中添加 `NSCameraUsageDescription`
2. 在 iOS 上，`RealityViewCameraContent` 默认显示 AR 摄像头视图（iOS 18+、macOS 15+）；使用 `.virtual` 摄像头模式进行显式的非 AR 降级
3. 基本 AR 无需权限。如果 AR 是应用的核心，请添加 `arkit` 必须设备功能；否则使用 `isSupported` 封锁 AR UI。

### 设备要求

在显示 AR UI 之前，检查确切 AR 配置的 `isSupported` 值。

```swift
import ARKit

guard ARWorldTrackingConfiguration.isSupported else {
    showUnsupportedDeviceMessage()
    return
}
```

### 关键类型

| 类型 | 平台 | 角色 |
|---|---|---|
| `RealityView` | iOS 18+、visionOS 1+ | 包含 RealityKit 内容的 SwiftUI 视图 |
| `RealityViewCameraContent` | iOS 18+、macOS 15+ | 在 iOS 上通过 AR 摄像头视图显示的内容，在 macOS 上为非 AR |
| `Entity` | 所有 | 所有场景对象的基类 |
| `ModelEntity` | 所有 | 具有可见 3D 模型的实体 |
| `AnchorEntity` | 所有 | 将实体锚定到真实世界锚点 |

## RealityView 基础

`RealityView` 是 RealityKit 的 SwiftUI 入口点。
`RealityViewCameraContent` 是 iOS/macOS 内容类型。在 iOS 上，它默认使用 AR 摄像头视图，并且可以在需要时或当 AR/摄像头访问不可用时使用 `content.camera = .virtual` 进行非 AR 模式。

```swift
import ARKit
import SwiftUI
import RealityKit

struct ARExperienceView: View {
    var body: some View {
        RealityView { (content: RealityViewCameraContent) in
            if !ARWorldTrackingConfiguration.isSupported {
                content.camera = .virtual
            }

            let sphere = ModelEntity(
                mesh: .generateSphere(radius: 0.05),
                materials: [SimpleMaterial(
                    color: .blue,
                    isMetallic: true
                )]
            )
            sphere.position = [0, 0, -0.5]  // 50cm 在摄像头前方
            content.add(sphere)
        }
    }
}
```

### Make and Update 模式

使用 `update` 闭包响应 SwiftUI 状态变化：

```swift
struct PlacementView: View {
    @State private var modelColor: UIColor = .red

    var body: some View {
        RealityView { content in
            let box = ModelEntity(
                mesh: .generateBox(size: 0.1),
                materials: [SimpleMaterial(
                    color: .red,
                    isMetallic: false
                )]
            )
            box.name = "colorBox"
            box.position = [0, 0, -0.5]
            content.add(box)
        } update: { content in
            if let box = content.entities.first(
                where: { $0.name == "colorBox" }
            ) as? ModelEntity {
                box.model?.materials = [SimpleMaterial(
                    color: modelColor,
                    isMetallic: false
                )]
            }
        }

        Button("改变颜色") {
            modelColor = modelColor == .red ? .green : .red
        }
    }
}
```

## 加载和创建实体

### 从 USDZ 文件加载

异步加载 3D 模型以避免阻塞主线程：

```swift
RealityView { content in
    if let robot = try? await ModelEntity(named: "robot") {
        robot.position = [0, -0.2, -0.8]
        robot.scale = [0.01, 0.01, 0.01]
        content.add(robot)
    }
}
```

### 添加组件

实体使用 ECS（实体组件系统）架构。向实体添加组件以赋予其行为：

```swift
let box = ModelEntity(
    mesh: .generateBox(size: 0.1),
    materials: [SimpleMaterial(color: .red, isMetallic: false)]
)

// 使其响应物理效果
box.components.set(PhysicsBodyComponent(
    massProperties: .default,
    material: .default,
    mode: .dynamic
))

// 添加用于交互的碰撞形状
box.components.set(CollisionComponent(
    shapes: [.generateBox(size: [0.1, 0.1, 0.1])]
))

// 启用输入目标以用于手势
box.components.set(InputTargetComponent())
```

## 锚定和放置

### AnchorEntity

使用 `AnchorEntity` 将内容锚定到检测到的表面或世界位置：

```swift
RealityView { content in
    // 锚定到水平表面
    let floorAnchor = AnchorEntity(.plane(
        .horizontal,
        classification: .floor,
        minimumBounds: [0.2, 0.2]
    ))

    let model = ModelEntity(
        mesh: .generateBox(size: 0.1),
        materials: [SimpleMaterial(color: .orange, isMetallic: false)]
    )
    floorAnchor.addChild(model)
    content.add(floorAnchor)
}
```

### 锚定目标

| 目标 | 描述 |
|---|---|
| `.plane(.horizontal, ...)` | 水平表面（地板、桌子） |
| `.plane(.vertical, ...)` | 垂直表面（墙壁） |
| `.plane(.any, ...)` | 任何检测到的平面 |
| `.world(transform:)` | 固定世界空间位置 |

## 射线投射

将 RealityKit 场景查询与 ARKit 真实世界射线投射分开：

- `RealityViewCameraContent.ray(through:in:to:)` 返回 RealityKit 坐标空间中的相机射线。它将屏幕点投影到虚拟场景中；它不是检测到物理表面的证明。
- `RealityViewCameraContent.hitTest(point:in:query:mask:)` 击中由 `CollisionComponent` 形状使可击中的虚拟实体。使用这些形状进行实体选择和目标手势，而不是 ARKit 平面检测。
- 使用 `AnchorEntity(.plane(...))` 在检测到的平面上进行简单放置。
- 使用 ARKit `ARRaycastQuery` 加上 `ARSession.raycast(_:)` 当任务需要与真实世界表面进行一次性交点时，然后使用 `AnchorEntity(raycastResult:)` 进行锚定。

```swift
let results = session.raycast(query)
if let result = results.first {
    let anchor = AnchorEntity(raycastResult: result)
    anchor.addChild(model)
    content.add(anchor)
}
```

不要将实体击中测试视为 ARKit 表面射线投射的替代品。

## 手势和交互

对于基于手势的实体交互，添加 `CollisionComponent` 以使实体可击中，并添加 `InputTargetComponent` 以用于输入目标。

### 实体上的拖动手势

```swift
struct DraggableARView: View {
    var body: some View {
        RealityView { content in
            let box = ModelEntity(
                mesh: .generateBox(size: 0.1),
                materials: [SimpleMaterial(color: .blue, isMetallic: true)]
            )
            box.position = [0, 0, -0.5]
            box.components.set(CollisionComponent(
                shapes: [.generateBox(size: [0.1, 0.1, 0.1])]
            ))
            box.components.set(InputTargetComponent())
            box.name = "draggable"
            content.add(box)
        }
        .gesture(
            DragGesture()
                .targetedToAnyEntity()
                .onChanged { value in
                    let entity = value.entity
                    guard let parent = entity.parent else { return }
                    entity.position = value.convert(
                        value.location3D,
                        from: .local,
                        to: parent
                    )
                }
        )
    }
}
```

## 场景理解

### 每帧更新

订阅 `SceneEvents.Update` 以进行连续场景工作，而不是使用 SwiftUI 定时器驱动 RealityKit。保持订阅活跃并使用 `event.deltaTime`；参见 [实体动画](references/realitykit-patterns.md#entity-animations)。

### 平台边界

在 visionOS 上，ARKit 提供不同的 API 表面，具有 `ARKitSession`、`WorldTrackingProvider` 和 `PlaneDetectionProvider`。这些 visionOS 特定的类型在 iOS 上不可用。在 iOS 上，RealityKit 通过 `RealityViewCameraContent` 自动处理世界跟踪。

对于 iOS 架构或迁移说明，使用 `ARWorldTrackingConfiguration.isSupported` 封锁 AR，使用 `RealityViewCameraContent` 托管内容，并使用 `AnchorEntity` 放置 `Entity`/`ModelEntity` 构建场景。

**Handoffs:** `CollisionComponent` + `InputTargetComponent` 处理 RealityKit 交互；`AccessibilityComponent` 处理实体可访问性元数据；详细的 SwiftUI 手势和 VoiceOver/Switch Control 策略属于兄弟。

将现有的 `SCNView`/`SCNNode` 工作视为单独的 SceneKit 路径或显式迁移到 RealityKit，而不是混合场景图。

## 常见错误

### 不要：跳过 AR 功能检查

在显示 AR 之前，使用设置中的配置特定支持检查。当它失败时，显示非 AR 内容或显式的不可用状态。

### 不要：同步加载大型模型

在主线程上加载大型 USDZ 文件会导致帧下降和挂起。`RealityView` 的 `make` 闭包是 `async` —— 使用它。

```swift
// 错误——同步加载阻塞主线程
RealityView { content in
    let model = try! Entity.load(named: "large-scene")
    content.add(model)
}

// 正确——异步加载
RealityView { content in
    if let model = try? await ModelEntity(named: "large-scene") {
        content.add(model)
    }
}
```

### 不要：忘记交互实体的碰撞和输入目标组件

交互实体需要 [手势和交互](#gestures-and-interaction) 中所示的这两个组件；没有它们，点击和拖动会穿透。

### 不要：在更新闭包中创建新实体

`update` 闭包在每次 SwiftUI 状态变化时运行。在那里创建实体会在每次渲染传递中重复内容。

```swift
// 错误——在每次状态变化时重复实体
RealityView { content in
    // 空的
} update: { content in
    let sphere = ModelEntity(mesh: .generateSphere(radius: 0.05))
    content.add(sphere)  // 在每次更新时再次添加
}

// 正确——在 make 中创建，在 update 中修改
RealityView { content in
    let sphere = ModelEntity(mesh: .generateSphere(radius: 0.05))
    sphere.name = "mySphere"
    content.add(sphere)
} update: { content in
    if let sphere = content.entities.first(
        where: { $0.name == "mySphere" }
    ) as? ModelEntity {
        // 修改现有实体
        sphere.position.y = newYPosition
    }
}
```

### 不要：忽略相机权限

RealityKit 在 iOS 上需要相机访问。如果用户拒绝权限，视图会显示黑色屏幕，没有任何解释。

```swift
// 错误——没有权限处理
RealityView { content in
    // 如果相机被拒绝，则显示黑色屏幕
}

// 正确——检查并请求权限
struct ARContainerView: View {
    @State private var cameraAuthorized = false

    var body: some View {
        Group {
            if cameraAuthorized {
                RealityView { content in
                    // AR 内容
                }
            } else {
                ContentUnavailableView(
                    "Camera Access Required",
                    systemImage: "camera.fill",
                    description: Text("Enable camera in Settings to use AR.")
                )
            }
        }
        .task {
            let status = AVCaptureDevice.authorizationStatus(for: .video)
            if status == .authorized {
                cameraAuthorized = true
            } else if status == .notDetermined {
                cameraAuthorized = await AVCaptureDevice
                    .requestAccess(for: .video)
            }
        }
    }
}
```

## 审查清单

- [ ] Info.plist 中设置了 `NSCameraUsageDescription`
- [ ] 在显示 AR 视图之前检查了 AR 设备功能的支持
- [ ] 请求了相机权限并处理了拒绝，带有降级 UI
- [ ] 当 AR 是应用的核心时，添加了 `arkit` 必须设备功能
- [ ] 3D 模型在 `make` 闭包中异步加载
- [ ] 实体在 `make` 中创建，在 `update` 中修改（不在 `update` 中创建）
- [ ] 交互先决条件和兄弟手off遵循手势部分
- [ ] 实体击中测试、相机射线和 ARKit 表面射线投射遵循射线投射的区别
- [ ] 使用 `SceneEvents.Update` 订阅进行每帧逻辑（不是 SwiftUI 定时器）
- [ ] 大型场景使用 `ModelEntity(named:)` 异步加载，而不是 `Entity.load(named:)`
- [ ] 锚定实体针对用例的适当表面类型
- [ ] 实体设置了名称以在 `update` 闭包中查找

## 参考资料

- 阅读 [references/realitykit-patterns.md](references/realitykit-patterns.md) 以了解物理、动画、照明、ECS、可访问性和性能模式。
- [RealityKit 框架](https://sosumi.ai/documentation/realitykit)
- [RealityView](https://sosumi.ai/documentation/realitykit/realityview)
- [RealityViewCameraContent](https://sosumi.ai/documentation/realitykit/realityviewcameracontent)
- [RealityViewCamera](https://sosumi.ai/documentation/realitykit/realityviewcamera)
- [Entity](https://sosumi.ai/documentation/realitykit/entity)
- [ModelEntity](https://sosumi.ai/documentation/realitykit/modelentity)
- [AnchorEntity](https://sosumi.ai/documentation/realitykit/anchorentity)
- [ARKit 框架](https://sosumi.ai/documentation/arkit)
- [iOS 中的 ARKit](https://sosumi.ai/documentation/arkit/arkit-in-ios)
- [验证设备支持和用户权限](https://sosumi.ai/documentation/arkit/verifying-device-support-and-user-permission)
- [ARWorldTrackingConfiguration](https://sosumi.ai/documentation/arkit/arworldtrackingconfiguration)
- [ARRaycastQuery](https://sosumi.ai/documentation/arkit/arraycastquery)
- [ARSession.raycast(_:)](https://sosumi.ai/documentation/arkit/arsession/raycast(_:))
- [从文件加载实体](https://sosumi.ai/documentation/realitykit/loading-entities-from-a-file)
