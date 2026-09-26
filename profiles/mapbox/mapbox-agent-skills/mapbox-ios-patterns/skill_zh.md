# Mapbox iOS 集成模式

官方集成模式，用于在 iOS 上使用 Swift、SwiftUI 和 UIKit 集成 Mapbox Maps SDK v11。

**在以下情况下使用此技能：**

- 安装和配置 iOS Mapbox Maps SDK
- 向地图添加标记和注释
- 显示用户位置并使用相机跟踪
- 向地图添加自定义数据（GeoJSON）
- 使用地图样式、相机或用户交互
- 处理功能交互和点击

**官方资源：**

- [iOS 地图指南](https://docs.mapbox.com/ios/maps/guides/)
- [API 参考](https://docs.mapbox.com/ios/maps/api-reference/)
- [示例应用](https://github.com/mapbox/mapbox-maps-ios/tree/main/Sources/Examples)

---

## 安装与设置

### 要求

- iOS 14+
- Xcode 15+
- Swift 5.9+
- 免费Mapbox账户

### 第 1 步：配置访问令牌

将您的公共令牌添加到 `Info.plist`：

```xml
<key>MBXAccessToken</key>
<string>pk.your_mapbox_token_here</string>
```

**获取令牌：** 登录 [mapbox.com](https://account.mapbox.com/access-tokens/)

### 第 2 步：添加 Swift 包依赖

1. **文件 → 添加包依赖**
2. **输入 URL：** `https://github.com/mapbox/mapbox-maps-ios.git`
3. **版本：** 从 `11.0.0` 选择“向上到下一个主版本”
4. **验证** 四个依赖项出现：MapboxCommon、MapboxCoreMaps、MapboxMaps、Turf

**替代方案：** CocoaPods 或直接下载（[安装指南](https://docs.mapbox.com/ios/maps/guides/install/))

---

## 地图初始化

### SwiftUI 模式

**基本地图：**

```swift
import SwiftUI
import MapboxMaps

struct ContentView: View {
    @State private var viewport: Viewport = .camera(
        center: CLLocationCoordinate2D(latitude: 37.7749, longitude: -122.4194),
        zoom: 12
    )

    var body: some View {
        Map(viewport: $viewport)
            .mapStyle(.standard)
    }
}
```

**带装饰：**

```swift
Map(viewport: $viewport)
    .mapStyle(.standard)
    .ornamentOptions(OrnamentOptions(
        scaleBar: .init(visibility: .visible),
        compass: .init(visibility: .adaptive),
        logo: .init(position: .bottomLeading)
    ))
```

### UIKit 模式

```swift
import UIKit
import MapboxMaps

class MapViewController: UIViewController {
    private var mapView: MapView!

    override func viewDidLoad() {
        super.viewDidLoad()

        let options = MapInitOptions(
            cameraOptions: CameraOptions(
                center: CLLocationCoordinate2D(latitude: 37.7749, longitude: -122.4194),
                zoom: 12
            )
        )

        mapView = MapView(frame: view.bounds, mapInitOptions: options)
        mapView.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        view.addSubview(mapView)

        mapView.mapboxMap.loadStyle(.standard)
    }
}
```

---

## 添加标记

SDK 提供三种放置地图上点的方法。选择最简单且适合您的方法。

**代理备注：** SwiftUI Mapbox 绘图不完整，至少需要一个注释（`Marker`、`PointAnnotation` 或 `MapViewAnnotation`）。不要发布一个没有图钉的 `Map { }`。

### 应该使用哪个 API？

| API                                                       | 在以下情况下使用                                                                                    | 平台       | 备注                                                                                                                                                                        |
| --------------------------------------------------------- | ---------------------------------------------------------------------------------------------- | --------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `Marker` (Markers API)                                    | 您需要一个默认图钉且没有自定义图像资源                                                             | SwiftUI only    | 无需图像资源。实验性 SPI — 需要 `@_spi(Experimental) import MapboxMaps`。最佳情况 < 100 个标记。                                                              |
| `PointAnnotation`                                         | 您有自定义图像并希望进行图层级别的放置                                                             | SwiftUI + UIKit | 由符号图层支持，因此它可以很好地扩展到数百个标记。接受任何 `UIImage`，`UIKit` 可以渲染。                                                                               |
| 视图注释（`ViewAnnotation` / `MapViewAnnotation`） | 您希望渲染一个完整的原生视图（卡片、徽章、动画内容）锚定到坐标 | SwiftUI + UIKit | SwiftUI 使用 `MapViewAnnotation`；UIKit 使用 `mapView.viewAnnotations` 与 `ViewAnnotation`。每个注释都是一个真实的视图——在规模上比 `PointAnnotation` 成本更高。 |

对于数百或数千个特征，使用样式图层（`SymbolLayer` 在 `GeoJSONSource` 上）而不是注释。

### Markers API（推荐用于简单情况，SwiftUI）

```swift
import SwiftUI
@_spi(Experimental) import MapboxMaps

struct ContentView: View {
    var body: some View {
        Map {
            Marker(coordinate: CLLocationCoordinate2D(latitude: 37.7749, longitude: -122.4194))
                .color(.red)
                .text("San Francisco")
        }
    }
}
```

从集合中获取多个标记：

```swift
Map {
    ForEvery(locations, id: \.id) { location in
        Marker(coordinate: location.coordinate)
            .color(.red)
            .text(location.name)
    }
}
```

> **扩展备注。** `Marker` 和 `PointAnnotation` 每个标记都会创建自己的视图或符号条目——直到大约 100 个标记都可以。对于更大的数据集（数百或数千个特征——与开放的 GeoJSON 源常见），将数据加载到 `GeoJSONSource` 中并使用 `SymbolLayer` 渲染。这可以扩展到数千个特征并启用聚类。

### PointAnnotation（自定义图像）

**SwiftUI：**

```swift
Map(viewport: $viewport) {
    PointAnnotation(coordinate: CLLocationCoordinate2D(latitude: 37.7749, longitude: -122.4194))
        .image(.init(image: UIImage(named: "marker")!, name: "marker"))
}
```

**UIKit：**

```swift
// 创建注释管理器（一次性，用于更新）
var pointAnnotationManager = mapView.annotations.makePointAnnotationManager()

// 创建标记
var annotation = PointAnnotation(coordinate: CLLocationCoordinate2D(latitude: 37.7749, longitude: -122.4194))
annotation.image = .init(image: UIImage(named: "marker")!, name: "marker")
annotation.iconAnchor = .bottom

// 添加到地图
pointAnnotationManager.annotations = [annotation]
```

**多个标记：**

```swift
let annotations = locations.map { coordinate in
    var annotation = PointAnnotation(coordinate: coordinate)
    annotation.image = .init(image: UIImage(named: "marker")!, name: "marker")
    return annotation
}

pointAnnotationManager.annotations = annotations
```

---

## 显示用户位置

**第 1 步：向 Info.plist 添加位置权限：**

```xml
<key>NSLocationWhenInUseUsageDescription</key>
<string>在地图上显示您的位置</string>
```

**第 2 步：请求权限并显示位置：**

```swift
import CoreLocation

// 请求权限
let locationManager = CLLocationManager()
locationManager.requestWhenInUseAuthorization()

// 显示用户位置指示器
mapView.location.options.puckType = .puck2D()
mapView.location.options.puckBearingEnabled = true
```

---

## 性能最佳实践

### 重用注释管理器

```swift
// ❌ 不要重复创建新的管理器
func updateMarkers() {
    let manager = mapView.annotations.makePointAnnotationManager()
    manager.annotations = markers
}

// ✅ 一次性创建，重用
let pointAnnotationManager: PointAnnotationManager

init() {
    pointAnnotationManager = mapView.annotations.makePointAnnotationManager()
}

func updateMarkers() {
    pointAnnotationManager.annotations = markers
}
```

### 批量更新注释

```swift
// ✅ 一次性更新所有
pointAnnotationManager.annotations = newAnnotations

// ❌ 不要逐个更新
for annotation in newAnnotations {
    pointAnnotationManager.annotations.append(annotation)
}
```

### 内存管理

```swift
// 在闭包中使用弱 self
mapView.gestures.onMapTap.observe { [weak self] context in
    self?.handleTap(context.coordinate)
}.store(in: &cancelables)

// 在 deinit 时清理
deinit {
    cancelables.forEach { $0.cancel() }
}
```

### 使用标准样式

```swift
// ✅ 标准样式经过优化并推荐使用
.mapStyle(.standard)

// 仅在需要特定用例时使用其他样式
.mapStyle(.standardSatellite) // 卫星图像
```

---

## 故障排除

### 地图未显示

**检查：**

1. ✅ Info.plist 中的 `MBXAccessToken`
2. ✅ 令牌有效（在 mapbox.com 上测试）
3. ✅ 导入了 MapboxMaps 框架
4. ✅ MapView 添加到视图层次结构
5. ✅ 设置了正确的框架/约束

### 样式未加载

```swift
mapView.mapboxMap.onStyleLoaded.observe { [weak self] _ in
    print("样式加载成功")
    // 在此处添加图层和源
}.store(in: &cancelables)
```

### 性能问题

- 使用 `.standard` 样式（推荐且经过优化）
- 限制视图中可见的注释
- 重用注释管理器
- 避免频繁重新加载样式
- 批量更新注释

---

## 参考文件

在需要更深入模式的情况下加载这些参考：

- **`references/annotations.md`** — 圆形、折线、多边形注释
- **`references/location-tracking.md`** — 相机跟随用户 + 获取当前位置
- **`references/custom-data.md`** — GeoJSON：线、多边形、点、更新/删除
- **`references/camera-styles.md`** — 相机控制 + 地图样式
- **`references/interactions.md`** — 功能集交互、自定义图层点击、长按、手势

---

## 其他资源

- [iOS 地图指南](https://docs.mapbox.com/ios/maps/guides/)
- [API 参考](https://docs.mapbox.com/ios/maps/api/11.18.1/documentation/mapboxmaps/)
- [交互指南](https://docs.mapbox.com/ios/maps/guides/user-interaction/Interactions/)
- [SwiftUI 用户指南](https://docs.mapbox.com/ios/maps/api/11.18.1/documentation/mapboxmaps/swiftui-user-guide)
- [示例应用](https://github.com/mapbox/mapbox-maps-ios/tree/main/Sources/Examples)
- [迁移指南（v10 → v11）](https://docs.mapbox.com/ios/maps/guides/migrate-to-v11/)
