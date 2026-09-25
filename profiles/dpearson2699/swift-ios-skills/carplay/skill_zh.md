# CarPlay

为车辆显示屏构建具有类别权限、基于模板的 CarPlay 应用。
范围：Swift 6.3，iOS 26+。

有关包括完整导航会话、仪表板场景和高级模板组合的扩展模式，请参阅 [参考资料/carplay-patterns.md](references/carplay-patterns.md)。

范围边界：完整的 CarPlay 框架应用使用类别权限、`CPTemplateApplicationScene`、`CPTemplateApplicationSceneDelegate`、`CPInterfaceController` 和系统 `CPTemplate` 导航。CarPlay 可见的 WidgetKit 小部件和 ActivityKit Live Activities 是独立的系统体验；将它们的实现路由到这些领域，同时在此处保留 CarPlay 特定的验证。

## 内容

- [权限和设置](#权限和设置)
- [场景配置](#场景配置)
- [模板概述](#模板概述)
- [导航应用](#导航应用)
- [音频应用](#音频应用)
- [通信应用](#通信应用)
- [兴趣点应用](#兴趣点应用)
- [使用 CarPlay 模拟器进行测试](#使用-carplay-模拟器进行测试)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 权限和设置

从 [Apple 的 CarPlay 权限表单](https://developer.apple.com/contact/carplay) 请求特定类别的权限，接受补充协议，然后使用下面批准的类别密钥进行授权。

### 按类别划分的权限密钥

| 权限 | 类别 |
|---|---|
| `com.apple.developer.carplay-audio` | 音频 |
| `com.apple.developer.carplay-communication` | 通信 |
| `com.apple.developer.carplay-maps` | 导航 |
| `com.apple.developer.carplay-charging` | 电动汽车充电 |
| `com.apple.developer.carplay-parking` | 停车 |
| `com.apple.developer.carplay-quick-ordering` | 快速食品订购 |

### 项目配置

1. 在开发者门户的附加功能下更新 App ID。
2. 为更新的 App ID 生成新的授权文件。
3. 在 Xcode 中禁用自动签名并导入 CarPlay 授权文件。
4. 添加一个 `Entitlements.plist`，并将权限密钥设置为 `true`。
5. 将代码签名权限设置项设置为 `Entitlements.plist` 路径。

### 密钥类型

| 类型 | 角色 |
|---|---|
| `CPTemplateApplicationScene` | 用于 CarPlay 显示的 UIScene 子类 |
| `CPTemplateApplicationSceneDelegate` | 场景连接/断开生命周期 |
| `CPInterfaceController` | CarPlay 提供的控制器，用于设置根模板并推送、呈现或弹出模板 |
| `CPTemplate` | 所有 CarPlay 模板的抽象基类 |
| `CPSessionConfiguration` | 车辆显示屏限制和内容样式 |

## 场景配置

在 `Info.plist` 中声明 CarPlay 场景，并实现 `CPTemplateApplicationSceneDelegate` 以在 CarPlay 连接时响应。

### Info.plist 场景清单

```plist
<key>UIApplicationSceneManifest</key>
<dict>
    <key>UIApplicationSupportsMultipleScenes</key>
    <true/>
    <key>UISceneConfigurations</key>
    <dict>
        <key>CPTemplateApplicationSceneSessionRoleApplication</key>
        <array>
            <dict>
                <key>UISceneClassName</key>
                <string>CPTemplateApplicationScene</string>
                <key>UISceneConfigurationName</key>
                <string>CarPlaySceneConfiguration</string>
                <key>UISceneDelegateClassName</key>
                <string>$(PRODUCT_MODULE_NAME).CarPlaySceneDelegate</string>
            </dict>
        </array>
    </dict>
</dict>
```

### 场景代理（非导航）

非导航应用仅接收接口控制器。没有窗口。

```swift
import CarPlay

final class CarPlaySceneDelegate: UIResponder,
    CPTemplateApplicationSceneDelegate {

    var interfaceController: CPInterfaceController?

    func templateApplicationScene(
        _ templateApplicationScene: CPTemplateApplicationScene,
        didConnect interfaceController: CPInterfaceController
    ) {
        self.interfaceController = interfaceController
        interfaceController.setRootTemplate(buildRootTemplate(),
                                            animated: true, completion: nil)
    }

    func templateApplicationScene(
        _ templateApplicationScene: CPTemplateApplicationScene,
        didDisconnectInterfaceController interfaceController: CPInterfaceController
    ) {
        self.interfaceController = nil
    }
}
```

### 场景代理（导航）

导航应用同时接收接口控制器和 `CPWindow`。将窗口的根视图控制器设置为绘制地图内容。

```swift
func templateApplicationScene(
    _ templateApplicationScene: CPTemplateApplicationScene,
    didConnect interfaceController: CPInterfaceController,
    to window: CPWindow
) {
    self.interfaceController = interfaceController
    self.carWindow = window
    window.rootViewController = MapViewController()

    let mapTemplate = CPMapTemplate()
    mapTemplate.mapDelegate = self
    interfaceController.setRootTemplate(mapTemplate, animated: true,
                                        completion: nil)
}
```

## 模板概述

CarPlay 提供了一组固定的模板类型。应用提供内容；系统在车辆显示屏上渲染它。

### 通用模板

| 模板 | 目的 |
|---|---|
| `CPTabBarTemplate` | 具有标签页子模板的容器 |
| `CPListTemplate` | 可滚动的分节列表 |
| `CPGridTemplate` | 可点击的图标按钮网格（最多 8 个） |
| `CPInformationTemplate` | 带有最多 3 个操作的键值信息 |
| `CPAlertTemplate` | 带有最多 2 个操作的模态警报 |
| `CPActionSheetTemplate` | 模态操作表 |

### 特定类别的模板

| 模板 | 类别 |
|---|---|
| `CPMapTemplate` | 导航 -- 带导航栏的地图覆盖 |
| `CPSearchTemplate` | 导航 -- 目的地搜索 |
| `CPNowPlayingTemplate` | 音频 -- 共享正在播放屏幕 |
| `CPPointOfInterestTemplate` | 电动汽车充电 / 停车 / 食品 -- 兴趣点地图 |
| `CPContactTemplate` | 通信 -- 联系人卡片 |

### 导航层次结构

使用 `pushTemplate(_:animated:completion:)` 将模板添加到堆栈。使用 `presentTemplate(_:animated:completion:)` 进行模态显示。使用 `popTemplate(animated:completion:)` 返回。`CPTabBarTemplate` 必须设置为根——它不能被推送或呈现。

### CPTabBarTemplate

```swift
let browseTab = CPListTemplate(title: "浏览",
                               sections: [CPListSection(items: listItems)])
browseTab.tabImage = UIImage(systemName: "list.bullet")

let tabBar = CPTabBarTemplate(templates: [browseTab, settingsTab])
tabBar.delegate = self
interfaceController.setRootTemplate(tabBar, animated: true, completion: nil)
```

### CPListTemplate

```swift
let item = CPListItem(text: "收藏", detailText: "12 项")
item.handler = { selectedItem, completion in
    self.interfaceController?.pushTemplate(detailTemplate, animated: true,
                                           completion: nil)
    completion()
}

let section = CPListSection(items: [item], header: "库",
                            sectionIndexTitle: nil)
let listTemplate = CPListTemplate(title: "我的应用", sections: [section])
```

## 导航应用

导航应用使用 `com.apple.developer.carplay-maps`。它们是唯一接收 `CPWindow` 以绘制地图内容的类别。根模板必须是 `CPMapTemplate`。

### 旅程预览和路线选择

```swift
let routeChoice = CPRouteChoice(
    summaryVariants: ["最快路线", "快"],
    additionalInformationVariants: ["经州际公路 101"],
    selectionSummaryVariants: ["25 分钟"]
)
let trip = CPTrip(origin: origin, destination: destination,
                  routeChoices: [routeChoice])
mapTemplate.showTripPreviews([trip], textConfiguration: nil)
```

### 开始导航会话

```swift
extension CarPlaySceneDelegate: CPMapTemplateDelegate {
    func mapTemplate(_ mapTemplate: CPMapTemplate,
                     startedTrip trip: CPTrip,
                     using routeChoice: CPRouteChoice) {
        let session = mapTemplate.startNavigationSession(for: trip)
        session.pauseTrip(for: .loading, description: "计算路线...")

        let maneuver = CPManeuver()
        maneuver.instructionVariants = ["右转上 Main St"]
        maneuver.symbolImage = UIImage(systemName: "arrow.turn.up.right")
        session.upcomingManeuvers = [maneuver]

        let estimates = CPTravelEstimates(
            distanceRemaining: Measurement(value: 5.2, unit: .miles),
            timeRemaining: 900)
        session.updateEstimates(estimates, for: maneuver)
    }
}
```

### 地图按钮

```swift
let zoomIn = CPMapButton { _ in self.mapViewController.zoomIn() }
zoomIn.image = UIImage(systemName: "plus.magnifyingglass")
mapTemplate.mapButtons = [zoomIn, zoomOut]
```

### CPSearchTemplate

```swift
extension CarPlaySceneDelegate: CPSearchTemplateDelegate {
    func searchTemplate(_ searchTemplate: CPSearchTemplate,
                        updatedSearchText searchText: String,
                        completionHandler: @escaping ([CPListItem]) -> Void) {
        performSearch(query: searchText) { results in
            completionHandler(results.map {
                CPListItem(text: $0.name, detailText: $0.address)
            })
        }
    }

    func searchTemplate(_ searchTemplate: CPSearchTemplate,
                        selectedResult item: CPListItem,
                        completionHandler: @escaping () -> Void) {
        // 导航到选定的目的地
        completionHandler()
    }
}
```

## 音频应用

音频应用使用 `com.apple.developer.carplay-audio`。它们在列表中显示可浏览的内容，并使用 `CPNowPlayingTemplate` 进行播放控制。音频授权应用不可用 `CPInformationTemplate`。

### Now Playing Template

`CPNowPlayingTemplate` 是一个共享的单例。它从 `MPNowPlayingInfoCenter` 读取元数据。不要实例化一个新的。

```swift
let nowPlaying = CPNowPlayingTemplate.shared
nowPlaying.isUpNextButtonEnabled = true
nowPlaying.isAlbumArtistButtonEnabled = true
nowPlaying.updateNowPlayingButtons([
    CPNowPlayingShuffleButton { _ in self.toggleShuffle() },
    CPNowPlayingRepeatButton { _ in self.toggleRepeat() }
])
nowPlaying.add(self) // 注册为 CPNowPlayingTemplateObserver
```

### Siri 助手单元格

支持 `INPlayMediaIntent` 的音频应用可以显示一个助手单元格。通信应用使用 `INStartCallIntent` 并使用 `.startCall`。

```swift
let config = CPAssistantCellConfiguration(
    position: .top, visibility: .always, assistantAction: .playMedia)
let listTemplate = CPListTemplate(
    title: "播放列表",
    sections: [CPListSection(items: items)],
    assistantCellConfiguration: config)
```

## 通信应用

通信应用使用 `com.apple.developer.carplay-communication`。它们显示消息列表和联系人，并支持 `INStartCallIntent` 以进行 Siri 启发的呼叫。
`CPMessageListItem` 没有应用提供的选択处理器。当选中时，CarPlay 调用 Siri 组成、读取或回复行为，具体取决于项的电话/电子邮件、未读状态或现有的会话配置。

```swift
let leading = CPMessageListItemLeadingConfiguration(
    leadingItem: .star, leadingImage: nil, unread: true)
let trailing = CPMessageListItemTrailingConfiguration(
    trailingItem: .none, trailingImage: nil)

let message = CPMessageListItem(
    conversationIdentifier: "conv-123",
    text: "Jane",
    leadingConfiguration: leading,
    trailingConfiguration: trailing,
    detailText: "3 点会议",
    trailingText: "2:45 PM")

let messageList = CPListTemplate(title: "消息",
                                 sections: [CPListSection(items: [message])])
```

## 兴趣点应用

电动汽车充电、停车和食品订购应用使用 `CPPointOfInterestTemplate` 和 `CPInformationTemplate` 来显示位置和详细信息。
`CPPointOfInterestTemplate` 最多显示 12 个兴趣点。

### CPPointOfInterestTemplate

```swift
let poi = CPPointOfInterest(
    location: MKMapItem(placemark: MKPlacemark(
        coordinate: CLLocationCoordinate2D(latitude: 37.7749,
                                           longitude: -122.4194))),
    title: "SuperCharger Station", subtitle: "4 个可用",
    summary: "150 kW DC 快速充电",
    detailTitle: "SuperCharger Station", detailSubtitle: "$0.28/kWh",
    detailSummary: "24 小时营业",
    pinImage: UIImage(systemName: "bolt.fill"))

poi.primaryButton = CPTextButton(title: "导航",
                                 textStyle: .confirm) { _ in }

let poiTemplate = CPPointOfInterestTemplate(
    title: "附近的充电站", pointsOfInterest: [poi], selectedIndex: 0)
poiTemplate.pointOfInterestDelegate = self
```

### CPInformationTemplate

```swift
let infoTemplate = CPInformationTemplate(
    title: "订单摘要", layout: .leading,
    items: [
        CPInformationItem(title: "项目", detail: "Burrito Bowl"),
        CPInformationItem(title: "总计", detail: "$12.50")],
    actions: [
        CPTextButton(title: "下单", textStyle: .confirm) { _ in
            self.placeOrder() },
        CPTextButton(title: "取消", textStyle: .cancel) { _ in
            self.interfaceController?.popTemplate(animated: true,
                                                  completion: nil) }])
```

## 使用 CarPlay 模拟器进行测试

1. 在 Xcode 中使用 iOS 模拟器构建并运行。
2. 选择 I/O > 外部显示器 > CarPlay。

默认窗口：800x480 @2x。为导航应用启用额外选项：

```bash
defaults write com.apple.iphonesimulator CarPlayExtraOptions -bool YES
```

### 推荐的测试配置

| 配置 | 像素 | 缩放 |
|---|---|---|
| 最小 | 748 x 456 | @2x |
| 竖屏 | 768 x 1024 | @2x |
| 标准 | 800 x 480 | @2x |
| 高分辨率 | 1920 x 720 | @3x |

模拟器无法测试锁定 iPhone 行为、Siri、汽车收音机与音频共存或物理输入硬件（旋钮、触控板）。在可能的情况下，在真实的 CarPlay 兼容车辆或车载头单元上测试。设计主要的 CarPlay 流程，使其在 CarPlay 活跃时不需要 iPhone 输入。

## 常见错误

### 不要：使用错误的场景代理方法

导航应用必须实现 `templateApplicationScene(_:didConnect:to:)`（带 `CPWindow`）。非导航应用使用 `templateApplicationScene(_:didConnect:)`（无窗口）。使用错误的变体不会产生 CarPlay UI。

### 不要：在导航窗口中绘制自定义 UI

`CPWindow` 专用于地图内容。所有覆盖、警报和控制都必须使用 CarPlay 模板。

### 不要：推送或呈现 CPTabBarTemplate

`CPTabBarTemplate` 只能设置为根。推送或呈现它将失败。使用 `setRootTemplate(_:animated:completion:)`。

### 不要：实例化 CPNowPlayingTemplate

使用 `CPNowPlayingTemplate.shared`。创建新实例会导致问题。

### 不要：向 CPMessageListItem 添加处理器

`CPMessageListItem` 由 Siri 管理，与 `CPListItem` 不同。不要设置 `message.handler`；使用项配置和 `userInfo` 以提供上下文。

### 不要：将小部件视为 CarPlay 模板应用

CarPlay 可见的小部件和 Live Activities 属于 WidgetKit 和 ActivityKit。使用此技能为类别授权的 CarPlay 模板应用场景，并在汽车环境中验证这些表面。

### 不要：忽略车辆显示限制

检查 `CPSessionConfiguration.limitedUserInterfaces` 并尊重列表模板的 `maximumItemCount` / `maximumSectionCount`。

### 不要：忘记调用完成处理器

`CPListItem.handler` 必须在每条代码路径中调用其完成处理器。失败将使列表处于加载状态。

## 审查清单

- [ ] `Entitlements.plist` 中的 CarPlay 权限密钥正确
- [ ] `UIApplicationSupportsMultipleScenes` 设置为 `true`
- [ ] Info.plist 中的 `CPTemplateApplicationSceneSessionRoleApplication` 场景
- [ ] 场景代理类名与 `UISceneDelegateClassName` 匹配
- [ ] 使用正确的代理方法（带/不带 `CPWindow`）
- [ ] 在 `didConnect` 中设置根模板，然后返回
- [ ] 断开连接时清除接口控制器和窗口引用
- [ ] `CPTabBarTemplate` 仅用作根，从不推送
- [ ] 使用 `CPNowPlayingTemplate.shared`，而不是新实例
- [ ] 通信行使用没有自定义处理器的 `CPMessageListItem`
- [ ] WidgetKit/ActivityKit 表面路由到 CarPlay 模板应用代码之外
- [ ] 在填充列表之前检查 `maximumItemCount`/`maximumSectionCount`
- [ ] `CPListItem.handler` 在每条路径中调用完成
- [ ] 导航应用的 `CPWindow` 根视图控制器中包含地图内容
- [ ] iPhone 锁定时应用仍可运行
- [ ] 在最小、标准和高分辨率模拟器尺寸下进行测试
- [ ] 音频会话在非播放时停用

## 参考资料

- 扩展模式（仪表板、仪表板集群、完整导航流程、标签组合）：[参考资料/carplay-patterns.md](references/carplay-patterns.md)
- [CarPlay 框架](https://sosumi.ai/documentation/carplay)
- [CPTemplateApplicationSceneDelegate](https://sosumi.ai/documentation/carplay/cptemplateapplicationscenedelegate)
- [CPInterfaceController](https://sosumi.ai/documentation/carplay/cpinterfacecontroller)
- [CPMapTemplate](https://sosumi.ai/documentation/carplay/cpmaptemplate)
- [CPListTemplate](https://sosumi.ai/documentation/carplay/cplisttemplate)
- [CPNowPlayingTemplate](https://sosumi.ai/documentation/carplay/cpnowplayingtemplate)
- [CPPointOfInterestTemplate](https://sosumi.ai/documentation/carplay/cppointofinteresttemplate)
- [CPNavigationSession](https://sosumi.ai/documentation/carplay/cpnavigationsession)
- [请求 CarPlay 权限](https://sosumi.ai/documentation/carplay/requesting-carplay-entitlements)
- [在 CarPlay 中显示内容](https://sosumi.ai/documentation/carplay/displaying-content-in-carplay)
- [使用 CarPlay 模拟器](https://sosumi.ai/documentation/carplay/using-the-carplay-simulator)
- [CarPlay HIG](https://sosumi.ai/design/human-interface-guidelines/carplay)
