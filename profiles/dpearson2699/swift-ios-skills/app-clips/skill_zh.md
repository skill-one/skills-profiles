# App Clips

构建轻量级、即时可用的 iOS 应用版本，用于专注的即时体验或演示。

## 内容

- [App Clip 目标设置](#app-clip-target-setup)
- [调用和体验路由](#invocation-and-experience-routing)
- [大小和能力决策](#size-and-capability-decisions)
- [数据、通知和位置](#data-notifications-and-location)
- [常见错误](#common-mistakes)
- [审核清单](#review-checklist)
- [参考资料](#references)

## App Clip 目标设置

App Clip 是与完整应用位于同一 Xcode 项目中的**独立目标**：

1. **文件 → 新建 → 目标 → App Clip** — Xcode 创建 App Clip 目标，将 **嵌入 App Clip** 构建阶段添加到完整应用目标，并建立关联授权。
2. App Clip 的 Bundle ID **必须** 以完整应用的 Bundle ID 为前缀：`com.example.MyApp.Clip`。
3. 在诊断归档、签名或 App Store Connect 失败时，验证原始授权键：
   - App Clip 目标：`com.apple.developer.on-demand-install-capable`
   - App Clip 目标父应用链接：`com.apple.developer.parent-application-identifiers`
   - 完整应用目标关联的 App Clip 链接：`com.apple.developer.associated-appclip-app-identifiers`

使用 Swift 包或共享源文件为两个目标编写代码。使用 `APPCLIP` 激活编译条件添加 App Clip 特定的编译分支，并避免将仅完整应用使用的框架链接到 App Clip 目标。

**验证检查点：** 归档两个目标并检查其归档授权。如果签名或验证失败，请更正上述三个原始键/目标分配并重新归档，直到两个目标都通过。

## 调用和体验路由

在实现调用 URL 路由、App Store Connect 体验、本地体验、Safari 智能应用横幅、QR/NFC/App Clip 代码、AASA 或关联域时，请阅读 [`references/routing-and-experiences.md`](references/routing-and-experiences.md)。

App Clips 接收 `NSUserActivityTypeBrowsingWeb` 活动。将调用路由器与完整应用共享，因为在安装后，完整应用将替换 App Clip 并接收未来的调用。

- SwiftUI：使用 `.onContinueUserActivity(NSUserActivityTypeBrowsingWeb)`。
- UIKit 冷启动：在 `scene(_:willConnectTo:options:)` 中检查 `connectionOptions.userActivities`。
- UIKit 延续：在 `scene(_:continue:)` 中处理实际的 `NSUserActivity`。
- `scene(_:willContinueUserActivityWithType:)` 仅提供提前通知，不提供 URL。

在 App Store Connect 中配置所需的默认 App Clip 体验。使用高级体验进行地图集成、位置关联、生产 App Clip 代码、按位置卡片和精确物理位置路由；演示 App Clip 代码可以使用短演示 App Clip 链接。

对于自定义 URL，在完整应用和 App Clip 目标上向关联域添加 `appclips:example.com`，并托管一个具有 App Clip 应用标识符的 AASA 文件。对于 Safari 横幅，使用 `app-id`、`app-clip-bundle-id` 和可选的 `app-clip-display=card`；不要依赖 `app-argument` 进行 App Clip 启动。

**验证检查点：** 使用 `_XCAppClipURL` 和本地体验测试每个 URL，修复路由/AASA/体验不匹配，并重复直到 App Clip 和安装的完整应用到达相同的目的地。

## 大小和能力决策

使用 [大小、能力和推广](references/size-capabilities-and-promotion.md) 作为可行性审查、大小层级和测量、后台资源、CloudKit、Live Activities、不受支持的功能和完整应用推广的权威清单。当任何这些主题在范围内时，请加载它。

在边界级别保留产品评审：说明大小依据、调用和下载适配、能力排除和转交目的地。仅在用户要求实现时添加实现 API。

## 数据、通知和位置

在实现 App Group/完整应用迁移、钥匙串或 Apple ID 登录转交、临时通知、通知重启路由或物理位置确认时，请阅读 [`references/data-handoff-notifications-location.md`](references/data-handoff-notifications-location.md)。

将 App Group 存储视为非秘密转交状态，而不是信任边界。参考拥有 iOS 15.4+ 单向钥匙串规则、Apple ID 登录验证、临时通知权限和重启路由以及物理位置确认（包括其所需的原始键和目标）。

## 常见错误

### 超出适用的 App Clip 大小限制

使用 [大小限制](references/size-capabilities-and-promotion.md#size-limits) 选择和测量适用的限制。

### 设计仅用于营销或网页视图为主的 App Clip

App Clips 应允许人们在不安装应用的情况下完成专注任务或完整演示。避免仅用于营销的剪辑、广告密集型流程、启动画面、阻止下载的启动、重复安装提示和网页视图为主的体验，这些体验作为网站会更好。

## 审核清单

在所有适用的门禁通过之前不要发布；修复失败并重新运行相同的门禁。

- [ ] 目标 ID、所有三个原始授权键和共享代码边界正确。
- [ ] 调用适用于 SwiftUI/UIKit 冷启动和延续，然后转交到完整应用。
- [ ] 关联域、AASA、App Store Connect 体验和本地调用测试通过。
- [ ] 大小、能力、UX、Live Activity 和推广决策通过 [可行性审查](references/size-capabilities-and-promotion.md#feasibility-review-template)。
- [ ] 数据、凭证、通知和位置流程通过详细的 [转交检查](references/data-handoff-notifications-location.md)。

## 参考资料

- [路由和体验](references/routing-and-experiences.md)
- [数据转交、通知和位置](references/data-handoff-notifications-location.md)
- [大小、能力和推广](references/size-capabilities-and-promotion.md)
- [App Clips 框架](https://sosumi.ai/documentation/appclip/)
- [使用 Xcode 创建 App Clip](https://sosumi.ai/documentation/appclip/creating-an-app-clip-with-xcode/)
- [配置 App Clip 体验](https://sosumi.ai/documentation/appclip/configuring-the-launch-experience-of-your-app-clip/)
- [响应调用](https://sosumi.ai/documentation/appclip/responding-to-invocations/)
- [选择正确的功能](https://sosumi.ai/documentation/appclip/choosing-the-right-functionality-for-your-app-clip/)
- [确认用户的物理位置](https://sosumi.ai/documentation/appclip/confirming-a-person-s-physical-location/)
- [在 App Clip 之间共享数据](https://sosumi.ai/documentation/appclip/sharing-data-between-your-app-clip-and-your-full-app/)
- [在 App Clips 中启用通知](https://sosumi.ai/documentation/appclip/enabling-notifications-in-app-clips/)
- [支持来自网站和信息应用的调用](https://sosumi.ai/documentation/appclip/supporting-invocations-from-your-website-and-the-messages-app/)
- [使用 App Clip 提供 Live Activities](https://sosumi.ai/documentation/appclip/offering-live-activities-with-your-app-clip/)
- [向 App Clip 用户推荐应用](https://sosumi.ai/documentation/appclip/recommending-your-app-to-app-clip-users/)
- [APActivationPayload](https://sosumi.ai/documentation/appclip/apactivationpayload/)
- [SKOverlay.AppClipConfiguration](https://sosumi.ai/documentation/storekit/skoverlay/appclipconfiguration/)
- [NSUserActivityTypeBrowsingWeb](https://sosumi.ai/documentation/foundation/nsuseractivitytypebrowsingweb/)
- [创建 App Clip 代码](https://sosumi.ai/documentation/appclip/creating-app-clip-codes/)
- [分发您的 App Clip](https://sosumi.ai/documentation/appclip/distributing-your-app-clip/)
- [App Clips HIG](https://sosumi.ai/design/human-interface-guidelines/app-clips/)
