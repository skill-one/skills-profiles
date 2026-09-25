# AdAttributionKit

为 iOS 17.4 及更高版本提供隐私保护广告归因。AdAttributionKit
允许广告网络在不暴露用户级数据的情况下测量转化（安装和再激活）。它支持 App Store 和替代市场，并与 SKAdNetwork 互操作。

归因流程中存在三个角色：广告网络（记录展示、接收回传）、发布应用（展示广告）和被推广应用（被推广的应用）。

## 目录

- [概述和隐私模型](#概述和隐私模型)
- [发布应用设置](#发布应用设置)
- [被推广应用设置](#被推广应用设置)
- [展示](#展示)
- [回传](#回传)
- [转化值](#转化值)
- [再激活](#再激活)
- [常见错误](#常见错误)
- [审核清单](#审核清单)
- [参考资料](#参考资料)

## 概述和隐私模型

AdAttributionKit 通过以下机制保护用户隐私：

- **群体匿名级别** -- 设备根据与广告关联的群体大小限制回传数据的粒度，范围从级别 0（最少数据）到级别 3（最多数据，包括发布者 ID 和国家代码）。
- **时间延迟回传** -- 回传在转化窗口关闭（第一个窗口）后 24-48 小时发送，或在第二个/第三个窗口后 24-144 小时发送。
- **无用户级标识符** -- 回传包含聚合来源标识符和转化值，不包含设备或用户 ID。
- **分层来源标识符** -- 2、3 或 4 位数的来源 ID，返回的位数取决于群体匿名级别。

在迁移和互操作性审核中，明确说明系统将 AdAttributionKit 和 SKAdNetwork 的展示一起评估，每个转化只有一个展示获胜，点击展示优于展示，点击展示中的时效性会打破平局，然后回退到最新的展示。

## 发布应用设置

发布应用展示来自已注册广告网络的广告。将每个广告网络的 ID 添加到应用的 Info.plist 中，以便其展示符合安装验证。

### 添加广告网络标识符

```xml
<key>AdNetworkIdentifiers</key>
<array>
    <string>example123.adattributionkit</string>
    <string>another456.adattributionkit</string>
</array>
```

广告网络 ID 必须是小写的。SKAdNetwork ID（以 `.skadnetwork` 结尾）也受支持——框架共享 ID。

### 显示 UIEventAttributionView

对于点击展示的自定义渲染广告，在每个可点击广告/控件上放置一个 `UIEventAttributionView`。它必须覆盖可点击区域，并保持在 `handleTap()` 成功之前会拦截触摸的视图之上。

```swift
import UIKit

let attributionView = UIEventAttributionView()
attributionView.frame = adContentView.bounds
attributionView.isUserInteractionEnabled = true
adContentView.addSubview(attributionView)
```

## 被推广应用设置

被推广应用是用户看到广告后安装或再激活的应用。它必须至少调用一次转化值更新，以开始回传转化窗口。

### 选择接收获胜回传副本

在顶层 `AdAttributionKit` Info.plist 字典下添加 `AttributionCopyEndpoint`，以便设备将获胜回传副本发送到您的服务器：

```xml
<key>AdAttributionKit</key>
<dict>
    <key>AttributionCopyEndpoint</key>
    <string>https://example.com</string>
</dict>
```

系统从 URL 中的可注册域派生众所周知的端点，忽略子域：

```
https://example.com/.well-known/appattribution/report-attribution/
```

配置您的服务器以在该路径上接受 HTTPS POST 请求。该域名必须具有有效的 SSL 证书。

### 选择接收再激活回传副本

在相同的 `AdAttributionKit` 字典中添加第二个键，以接收获胜的再激活回传副本：

```xml
<key>AdAttributionKit</key>
<dict>
    <key>AttributionCopyEndpoint</key>
    <string>https://example.com</string>
    <key>OptInForReengagementPostbackCopies</key>
    <true/>
</dict>
```

### 在首次启动时更新转化值

在首次启动后尽快调用转化值更新，以开始转化窗口：

```swift
import AdAttributionKit

func applicationDidFinishLaunching() async {
    do {
        try await Postback.updateConversionValue(0, lockPostback: false)
    } catch {
        print("Failed to set initial conversion value: \(error)")
    }
}
```

## 展示

广告网络使用 JWS（JSON Web Signature）创建已签名的展示。发布应用使用 `AppImpression` 来注册和处理这些展示。

### 从 JWS 创建展示

```swift
import AdAttributionKit

let impression = try await AppImpression(compactJWS: signedJWSString)
```

JWS 包含广告网络 ID、被推广项 ID、发布者项 ID、来源标识符、时间戳和可选的再激活资格标志。有关 JWS 生成详情，请参阅 [参考资料/adattributionkit-patterns.md](references/adattributionkit-patterns.md)。

### 检查设备支持

```swift
guard AppImpression.isSupported else {
    // 回退到替代广告展示
    return
}
```

### 展示式展示

当广告内容已显示并关闭时，记录一个展示式展示：

```swift
func handleAdViewed(impression: AppImpression) async {
    do {
        try await impression.handleView()
    } catch {
        print("Failed to record view-through impression: \(error)")
    }
}
```

对于长时展示，使用 `beginView()` 和 `endView()` 来跟踪展示时长：

```swift
try await impression.beginView()
// ... 广告保持可见 ...
try await impression.endView()
```

### 点击展示

在创建 `AppImpression` 后 15 分钟内响应广告点击，调用 `handleTap()`；否则请求新的展示。如果被推广应用未安装，系统将打开其 App Store 或市场页面。如果已安装，系统将直接启动它。

```swift
func handleAdTapped(impression: AppImpression) async {
    do {
        try await impression.handleTap()
    } catch {
        print("Failed to record click-through impression: \(error)")
    }
}
```

`UIEventAttributionView` 必须覆盖广告，以便 `handleTap()` 成功。

### StoreKit 渲染广告

将展示传递给 StoreKit 叠加或产品视图控制器 API。StoreKit 在显示 2 秒后自动记录展示式展示，并在点击时记录点击展示。

```swift
import StoreKit

let config = SKOverlay.AppConfiguration(appIdentifier: "1234567890",
                                         position: .bottom)
config.appImpression = impression
```

## 回传

回传是设备在转化事件后发送给广告网络（可选地发送给被推广应用开发者）的归因报告。

### 转化窗口

获胜的归因可以在转化窗口中产生多个回传；较低的数据级别和非获胜归因披露的数据较少。加载 [参考资料/adattributionkit-patterns.md](references/adattributionkit-patterns.md) 以获取当前窗口和延迟矩阵。

### 事件的时间窗口

归因资格窗口与转化/回传窗口不同。根据当前文档和参考资料配置和验证展示式、点击式、安装更新和再激活限制；不要混淆这两个概念。

### 早期锁定转化值

在窗口结束前锁定回传以最终确定转化值，并更快地接收回传：

```swift
try await Postback.updateConversionValue(
    42,
    coarseConversionValue: .high,
    lockPostback: true
)
```

锁定后，系统将忽略该转化窗口中的进一步更新。

### 按级别回传数据

随着系统分配的数据级别，披露程度增加。代码和分析必须容忍缺失的来源位数、细粒度/粗粒度转化值、发布者项 ID 和国家。参考资料拥有详细的级别矩阵。

## 转化值

### 细粒度值

细粒度值是 0...63（6 位）的整数。它们仅在第一个回传中可用，并且仅在级别 2 或更高时可用：

```swift
try await Postback.updateConversionValue(
    35,
    coarseConversionValue: .medium,
    lockPostback: false
)
```

### 粗粒度值

较低级别和第二个/第三个回传有三个级别：

```swift
// CoarseConversionValue 案例的值：.low、.medium、.high
try await Postback.updateConversionValue(
    10,
    coarseConversionValue: .high,
    lockPostback: false
)
```

### 通过转化类型更新（iOS 18+）

为安装和再激活回传分别设置转化值。在服务器 JSON 中，使用带连字符的 `"conversion-type": "re-engagement"`；Swift API 使用 `.reengagement` 而不带连字符。

```swift
let installUpdate = PostbackUpdate(
    fineConversionValue: 20,
    lockPostback: false,
    conversionTypes: [.install]
)
try await Postback.updateConversionValue(installUpdate)

let reengagementUpdate = PostbackUpdate(
    fineConversionValue: 12,
    lockPostback: false,
    conversionTypes: [.reengagement]
)
try await Postback.updateConversionValue(reengagementUpdate)
```

### 转化标签（iOS 18.4+）

使用转化标签在存在重叠转化窗口时选择性地更新特定回传：

```swift
let update = PostbackUpdate(
    fineConversionValue: 15,
    lockPostback: false,
    conversionTag: savedConversionTag,
    conversionTypes: [.reengagement]
)
try await Postback.updateConversionValue(update)
```

系统通过再激活 URL 的 `AdAttributionKitReengagementOpen` 查询参数传递转化标签。

## 再激活

再激活跟踪已安装被推广应用的用户，他们通过广告与应用互动以返回应用。

### 将展示标记为再激活资格

在生成展示时，将 JWS 负载中的 `eligible-for-re-engagement` 设置为 `true`。

### 使用 URL 处理再激活点击

传递系统在被推广应用中打开的通用链接：

```swift
let reengagementURL = URL(string: "https://example.com/promo/summer")!
try await impression.handleTap(reengagementURL: reengagementURL)
```

系统将 `AdAttributionKitReengagementOpen` 作为查询参数附加。被推广应用检查此参数以检测 AdAttributionKit 驱动的打开：

```swift
func handleUniversalLink(_ url: URL) {
    let components = URLComponents(url: url, resolvingAgainstBaseURL: false)
    let isReengagement = components?.queryItems?.contains(where: {
        $0.name == Postback.reengagementOpenURLParameter
    }) ?? false

    if isReengagement {
        // AdAttributionKit 通过再激活广告打开了此应用
    }
}
```

### 再激活限制

- 只有点击展示交互会创建再激活回传（展示式展示不会）。
- 设备强制执行每个应用的每月和每个设备的每年再激活限制。
- `AdAttributionKitReengagementOpen` 参数始终存在于 URL 中，即使系统没有创建回传。

## 常见错误

| 错误 | 修复 |
|---|---|
| 首次启动从未更新转化值 | 在预期窗口到期前调用标准的首次启动更新。 |
| 广告网络 ID 包含大写字符 | 使用确切的低级网络标识符。 |
| `handleTap()` 使用过时的展示或缺少当前的归因视图点击 | 用 `UIEventAttributionView` 覆盖广告，保持展示新鲜，并从验证的点击流程中调用。 |
| 点击错误被丢弃 | 明确处理过期展示和缺失视图的情况。 |
| 回传端点延迟或丢弃响应 | 接受、持久化/排队处理，并立即返回预期的成功。 |

## 审核清单

- [ ] 发布应用在 `AdNetworkIdentifiers` 中包含所有广告网络 ID（小写）
- [ ] 广告网络 ID 在发布应用的 Info.plist 和 JWS `kid` 之间匹配
- [ ] `UIEventAttributionView` 覆盖每个可点击的点击展示广告/控件
- [ ] 点击展示的 `AppImpression` 在 `handleTap()` 时不超过 15 分钟
- [ ] 被推广应用在首次启动时调用 `updateConversionValue`
- [ ] 服务器端点在众所周知的路径上接受有效的 SSL 证书的 HTTPS POST 请求
- [ ] 回传验证使用正确的 Apple 公共密钥
- [ ] 通过 `postback-identifier` 过滤重复回传
- [ ] 服务器对回传请求响应 HTTP 200
- [ ] 再激活 URL 是被推广应用的注册通用链接
- [ ] 转化值策略考虑了所有三个转化窗口
- [ ] 检查 `AppImpression.isSupported` 在尝试展示 API 之前

## 参考资料

- [参考资料/adattributionkit-patterns.md](references/adattributionkit-patterns.md)
  -- 回传验证、服务器处理、测试、SKAdNetwork 迁移、替代市场、归因规则配置
- [Apple: AdAttributionKit](https://sosumi.ai/documentation/adattributionkit)
- [Apple: 在您的应用中展示广告](https://sosumi.ai/documentation/adattributionkit/presenting-ads-in-your-app)
- [Apple: 接收广告归因和回传](https://sosumi.ai/documentation/adattributionkit/receiving-ad-attributions-and-postbacks)
- [Apple: 验证回传](https://sosumi.ai/documentation/adattributionkit/verifying-a-postback)
- [Apple: SKAdNetwork 互操作](https://sosumi.ai/documentation/adattributionkit/adattributionkit-skadnetwork-interoperability)
