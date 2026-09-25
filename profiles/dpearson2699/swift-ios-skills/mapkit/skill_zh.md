# MapKit

使用 SwiftUI 构建 iOS 17+ 的基于地图和位置感知功能
使用 MapKit 和现代 CoreLocation 异步 API。使用 `Map` 与 `MapContentBuilder`
为视图，`CLLocationUpdate.liveUpdates()` 用于流式传输位置，以及
`CLMonitor` 用于地理围栏。

当您需要完整的地图设置、搜索、路线、Look Around、快照或 iOS 26 地点 API 时，请阅读 [参考资料/mapkit-patterns.md](references/mapkit-patterns.md)。当任务涉及位置更新生命周期、地理围栏、后台位置、测试或隐私密钥时，请阅读
[参考资料/mapkit-corelocation-patterns.md](references/mapkit-corelocation-patterns.md)。

## 目录

- [工作流](#workflow)
- [SwiftUI 地图视图 (iOS 17+)](#swiftui-map-view-ios-17)
- [CoreLocation 现代API](#corelocation-modern-api)
- [地理编码](#geocoding)
- [搜索](#search)
- [路线](#directions)
- [PlaceDescriptor (iOS 26+)](#placedescriptor-ios-26)
- [常见错误](#common-mistakes)
- [审查清单](#review-checklist)
- [参考资料](#references)

## 工作流

### 1. 添加带标记或注释的地图

1. 导入 `MapKit`。
2. 创建一个 `Map` 视图，并可选地绑定 `MapCameraPosition`。
3. 在 `MapContentBuilder` 闭包中添加 `Marker`，`Annotation`，`MapPolyline`，`MapPolygon` 或 `MapCircle`
   4. 使用 `.mapStyle()` 配置地图样式。
5. 使用 `.mapControls { }` 添加地图控件。
6. 使用 `selection:` 绑定处理选择。

### 2. 跟踪用户位置

1. 在 Info.plist 中添加 `NSLocationWhenInUseUsageDescription`。
2. 在 iOS 18+ 上，创建一个 `CLServiceSession` 来管理授权。
3. 在 `Task` 中迭代 `CLLocationUpdate.liveUpdates()`。
4. 在更新 UI 之前按距离或精度过滤更新。
5. 当不再需要位置跟踪时停止任务。

### 3. 搜索地点

1. 配置 `MKLocalSearchCompleter` 以获取自动完成建议。
2. 在设置查询之前至少延迟 300 毫秒来抑制用户输入。
3. 将选择的完成转换为 `MKLocalSearch.Request` 以获取完整结果。
4. 将结果显示为标记或列表。

### 4. 获取路线并在地图上显示路线

1. 使用源和目标 `MKMapItem` 创建一个 `MKDirections.Request`。
2. 设置 `transportType` (`.automobile`，`.walking`，`.transit`，`.cycling`)。
3. 等待 `MKDirections.calculate()`。
4. 使用 `MapPolyline(route.polyline)` 绘制路线。

### 5. 审查现有的地图/位置代码

在本文件的末尾运行审查清单。

## SwiftUI 地图视图 (iOS 17+)

```swift
import MapKit
import SwiftUI

struct PlaceMap: View {
    @State private var position: MapCameraPosition = .automatic

    var body: some View {
        Map(position: $position) {
            Marker("Apple Park", coordinate: applePark)
            Marker("Infinite Loop", systemImage: "building.2",
                   coordinate: infiniteLoop)
        }
        .mapStyle(.standard(elevation: .realistic))
        .mapControls {
            MapUserLocationButton()
            MapCompass()
            MapScaleView()
        }
    }
}
```

### 标记和注释

```swift
// 气球标记 -- 最简单的方法来定位位置
Marker("Cafe", systemImage: "cup.and.saucer.fill", coordinate: cafeCoord)
    .tint(.brown)

// 注释 -- 在坐标处自定义 SwiftUI 视图
Annotation("You", coordinate: userCoord, anchor: .bottom) {
    Image(systemName: "figure.wave")
        .padding(6)
        .background(.blue.gradient, in: .circle)
        .foregroundStyle(.white)
}
```

### 覆盖层：Polyline，Polygon，Circle

```swift
Map {
    // 从坐标创建 Polyline
    MapPolyline(coordinates: routeCoords)
        .stroke(.blue, lineWidth: 4)

    // Polygon (区域高亮)
    MapPolygon(coordinates: parkBoundary)
        .foregroundStyle(.green.opacity(0.3))
        .stroke(.green, lineWidth: 2)

    // Circle (围绕一个点的半径)
    MapCircle(center: storeCoord, radius: 500)
        .foregroundStyle(.red.opacity(0.15))
        .stroke(.red, lineWidth: 1)
}
```

### 相机位置

`MapCameraPosition` 控制地图显示的内容。将其绑定到允许用户交互和程序化移动相机。

```swift
// 将地图居中到某个区域
@State private var position: MapCameraPosition = .region(
    MKCoordinateRegion(
        center: CLLocationCoordinate2D(latitude: 37.334, longitude: -122.009),
        span: MKCoordinateSpan(latitudeDelta: 0.05, longitudeDelta: 0.05)
    )
)

// 跟踪用户位置
@State private var position: MapCameraPosition = .userLocation(fallback: .automatic)

// 特定的相机角度 (3D 视角)
@State private var position: MapCameraPosition = .camera(
    MapCamera(centerCoordinate: applePark, distance: 1000, heading: 90, pitch: 60)
)

// 帧定特定项目
position = .item(MKMapItem.forCurrentLocation())
position = .rect(MKMapRect(...))
```

### 地图样式

默认为 `.standard`；仅在功能需要时选择 `.imagery` 或 `.hybrid`，真实高度，交通和兴趣点过滤。
请参阅 [完整的地图视图设置](references/mapkit-patterns.md#complete-map-view-setup)。

### 地图交互模式

保持 `.all` 以获得交互式地图。仅当有意协调手势时才限制模式；使用 `[]` 以获得静态嵌入的地图。请参阅
[在列表或 ScrollView 中显示地图](references/mapkit-patterns.md#map-in-a-list-or-scrollview)。

### 地图选择

```swift
@State private var selectedMarker: MKMapItem?

Map(selection: $selectedMarker) {
    ForEach(places) { place in
        Marker(place.name, coordinate: place.coordinate)
            .tag(place.mapItem)     // 标签必须与选择类型匹配
    }
}
.onChange(of: selectedMarker) { _, newValue in
    guard let item = newValue else { return }
    // 对选择做出反应
}
```

## CoreLocation 现代API

### CLLocationUpdate.liveUpdates() (iOS 17+)

用单个异步序列替换 `CLLocationManagerDelegate` 回调。
每次迭代都会生成一个包含可选 `CLLocation` 的 `CLLocationUpdate`。
在 iOS 18+ 上，使用可见的降级路径处理诊断状态，例如拒绝授权，全局禁用位置服务，位置不可用和不足的可用条件。
存储任务，以便功能可以取消它，并在驱动地图 UI 或后台工作之前拒绝无效、不准确、过时或不实用的运动数据。

```swift
import CoreLocation

@MainActor
@Observable
final class LocationTracker {
    var currentLocation: CLLocation?
    private var updateTask: Task<Void, Never>?

    func startTracking() {
        updateTask = Task {
            do {
                let updates = CLLocationUpdate.liveUpdates()
                for try await update in updates {
                    guard let location = update.location else { continue }
                    // 按水平精度过滤
                    guard location.horizontalAccuracy >= 0,
                          location.horizontalAccuracy < 50 else { continue }
                    currentLocation = location
                }
            } catch is CancellationError {
                // 当跟踪停止时预期。
            } catch {
                currentLocation = nil
            }
        }
    }

    func stopTracking() {
        updateTask?.cancel()
        updateTask = nil
    }
}
```

### CLServiceSession (iOS 18+)

声明功能生命周期的授权要求。在需要位置服务时保持对会话的引用。

```swift
// 当使用授权时，具有完整精度偏好
let session = CLServiceSession(
    authorization: .whenInUse,
    fullAccuracyPurposeKey: "NearbySearchPurpose"
)
// 将 `session` 作为存储属性；完成时释放它。
```

在 iOS 18+ 上，`CLLocationUpdate.liveUpdates()` 和 `CLMonitor` 如果您没有显式创建，则隐式使用 `CLServiceSession`。当您需要 `.always` 授权或完整精度时显式创建一个。

### 授权流程

```swift
// Info.plist 键 (必需):
// NSLocationWhenInUseUsageDescription
// NSLocationAlwaysAndWhenInUseUsageDescription (仅当需要 .always 时)

// 检查授权并在拒绝时引导用户到设置
struct LocationPermissionView: View {
    @Environment(\.openURL) private var openURL

    var body: some View {
        ContentUnavailableView {
            Label("Location Access Denied", systemImage: "location.slash")
        } description: {
            Text("Enable location access in Settings to use this feature.")
        } actions: {
            Button("Open Settings") {
                if let url = URL(string: UIApplication.openSettingsURLString) {
                    openURL(url)
                }
            }
        }
    }
}
```

## 地理编码

### CLGeocoder (iOS 8+)

```swift
let geocoder = CLGeocoder()

// 正向地理编码：地址字符串 -> 坐标
let placemarks = try await geocoder.geocodeAddressString("1 Apple Park Way, Cupertino")
if let location = placemarks.first?.location {
    print(location.coordinate) // CLLocationCoordinate2D
}

// 反向地理编码：坐标 -> placemark
let location = CLLocation(latitude: 37.3349, longitude: -122.0090)
let placemarks = try await geocoder.reverseGeocodeLocation(location)
if let placemark = placemarks.first {
    let address = [placemark.name, placemark.locality, placemark.administrativeArea]
        .compactMap { $0 }
        .joined(separator: ", ")
}
```

### MKGeocodingRequest 和 MKReverseGeocodingRequest (iOS 26+)

新的 MapKit 本地地理编码，返回具有更丰富数据的 `MKMapItem` 和 `MKAddress` / `MKAddressRepresentations` 以进行灵活的地址格式化。

```swift
@available(iOS 26, *)
func reverseGeocode(location: CLLocation) async throws -> MKMapItem? {
    guard let request = MKReverseGeocodingRequest(location: location) else {
        return nil
    }
    let mapItems = try await request.mapItems
    return mapItems.first
}

@available(iOS 26, *)
func forwardGeocode(address: String) async throws -> [MKMapItem] {
    guard let request = MKGeocodingRequest(addressString: address) else { return [] }
    return try await request.mapItems
}
```

## 搜索

### MKLocalSearchCompleter (自动完成)

```swift
@Observable
final class SearchCompleter: NSObject, MKLocalSearchCompleterDelegate {
    var results: [MKLocalSearchCompletion] = []
    var query: String = "" { didSet { completer.queryFragment = query } }

    private let completer = MKLocalSearchCompleter()

    override init() {
        super.init()
        completer.delegate = self
        completer.resultTypes = [.address, .pointOfInterest]
    }

    func completerDidUpdateResults(_ completer: MKLocalSearchCompleter) {
        results = completer.results
    }

    func completer(_ completer: MKLocalSearchCompleter, didFailWithError error: Error) {
        results = []
    }
}
```

### MKLocalSearch (完整搜索)

```swift
func search(for completion: MKLocalSearchCompletion) async throws -> [MKMapItem] {
    let request = MKLocalSearch.Request(completion: completion)
    request.resultTypes = [.pointOfInterest, .address]
    let search = MKLocalSearch(request: request)
    let response = try await search.start()
    return response.mapItems
}

// 在区域内使用自然语言查询搜索
func searchNearby(query: String, region: MKCoordinateRegion) async throws -> [MKMapItem] {
    let request = MKLocalSearch.Request()
    request.naturalLanguageQuery = query
    request.region = region
    let search = MKLocalSearch(request: request)
    let response = try await search.start()
    return response.mapItems
}
```

## 路线

```swift
func getDirections(from source: MKMapItem, to destination: MKMapItem,
                   transport: MKDirectionsTransportType = .automobile) async throws -> MKRoute? {
    let request = MKDirections.Request()
    request.source = source
    request.destination = destination
    request.transportType = transport
    let directions = MKDirections(request: request)
    let response = try await directions.calculate()
    return response.routes.first
}
```

### 在地图上显示路线

```swift
@State private var route: MKRoute?

Map {
    if let route {
        MapPolyline(route.polyline)
            .stroke(.blue, lineWidth: 5)
    }
    Marker("Start", coordinate: startCoord)
    Marker("End", coordinate: endCoord)
}
.task {
    route = try? await getDirections(from: startItem, to: endItem)
}
```

### ETA 计算

```swift
func getETA(from source: MKMapItem, to destination: MKMapItem) async throws -> TimeInterval {
    let request = MKDirections.Request()
    request.source = source
    request.destination = destination
    let directions = MKDirections(request: request)
    let response = try await directions.calculateETA()
    return response.expectedTravelTime
}
```

### 骑行路线 (iOS 14+)

将请求的运输类型设置为 `.cycling`；请参阅完整的
[cycling route](references/mapkit-patterns.md#cycling-directions-ios-14) 示例。

## PlaceDescriptor (iOS 26+)

从坐标或地址创建丰富的地点引用，而无需 Place ID。需要 `import GeoToolbox`。

```swift
import GeoToolbox

@available(iOS 26, *)
func lookupPlace(name: String, coordinate: CLLocationCoordinate2D) async throws -> MKMapItem {
    let descriptor = PlaceDescriptor(
        representations: [.coordinate(coordinate)],
        commonName: name
    )
    let request = MKMapItemRequest(placeDescriptor: descriptor)
    return try await request.mapItem
}
```

## 常见错误

**不要：** 一开始就请求始终授权。
**要：** 从当使用授权开始。在 iOS 18+ 上，保持 `CLServiceSession`
为功能生命周期；仅当后台功能需要系统在终止后重新启动时才请求 `.always`。

**不要：** 在 iOS 17+ 上使用 `CLLocationManagerDelegate` 进行简单的位置获取。
**要：** 使用 `CLLocationUpdate.liveUpdates()` 异步流以获得更简洁的代码。

**不要：** 忽略 `CLLocationUpdate` 诊断，例如拒绝、全局拒绝或位置不可用。
**要：** 停止或降级功能，显示恢复 UI，例如设置指导，并保持搜索/手动流程可用。

**不要：** 在地图/视图消失后从非拥有的任务中运行 `liveUpdates()`。
**要：** 存储 `Task`，在功能停止时取消它，并过滤无效、不准确、过时或不可能的运动修复。

**不要：** 强制解包 `CLPlacemark` 属性——它们都是可选的。
**要：** 使用空合并：`placemark.locality ?? "Unknown"`。

**不要：** 在每个按键时触发 `MKLocalSearchCompleter` 查询。
**要：** 使用 `.task(id: searchText)` + `Task.sleep(for: .milliseconds(300))` 进行延迟。

**不要：** 当位置授权被拒绝时静默失败。
**要：** 检测 `.denied` 状态并显示带有设置深度链接的警报。

**不要：** 假设地理编码总是成功——处理空结果和网络错误。

## 审查清单

- [ ] Info.plist 包含 `NSLocationWhenInUseUsageDescription` 并有具体原因
- [ ] 授权拒绝使用设置深度链接处理
- [ ] `CLLocationUpdate` 任务在不需要时取消 (电池)
- [ ] 位置精度适用于用例
- [ ] 地图注释使用具有稳定 ID 的 `Identifiable` 数据
- [ ] 地理编码错误处理 (网络故障，无结果)
- [ ] 搜索完成器输入延迟
- [ ] `CLMonitor` 限制为 20 个条件，实例保持活跃
- [ ] 后台位置使用 `CLBackgroundActivitySession`
- [ ] 地图使用 VoiceOver 测试
- [ ] 地图注释视图模型和位置 UI 更新是 `@MainActor`-隔离的

## 参考资料

- [参考资料/mapkit-patterns.md](references/mapkit-patterns.md) — 地图设置，注释，搜索，路线，聚类，Look Around，快照。
- [参考资料/mapkit-corelocation-patterns.md](references/mapkit-corelocation-patterns.md) — CLLocationUpdate，CLMonitor，CLServiceSession，后台位置，测试。
