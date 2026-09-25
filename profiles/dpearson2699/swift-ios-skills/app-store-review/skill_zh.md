# App Store 审核准备

在提交前捕获 App Store 拒绝风险。将策略、SDK、隐私、权限、支付和元数据检查视为当前版本证据，而非持久事实。

## 内容

- [常见拒绝原因及避免方法](#常见拒绝原因及避免方法)
- [PrivacyInfo.xcprivacy -- 隐私声明要求](#privacynfoxcprivacy-隐私声明要求)
- [数据使用、共享和隐私政策（指南 5.1.2）](#数据使用共享和隐私政策指南-512)
- [应用内购买和 StoreKit 规则（指南 3.1.1）](#应用内购买和storekit规则指南-311)
- [HIG 合规性检查清单](# hig合规性检查清单)
- [应用追踪透明度（ATT）](#应用追踪透明度att)
- [欧盟数字市场法案（DMA）注意事项](#欧盟数字市场法案dma注意事项)
- [权限和功能](#权限和功能)
- [提交工作流程](#提交工作流程)
- [元数据最佳实践](#元数据最佳实践)
- [申诉流程](#申诉流程)
- [常见错误](#常见错误)
- [审核检查清单](#审核检查清单)
- [参考资料](#参考资料)

开始每个审核前，获取当前的 App Review 指南、即将生效的要求、截图规范、required-reason API 文档以及适用的商店/权限支付规则。记录每个版本障碍的检查日期和来源。然后归档构建并验证精确的提交版本，将障碍与清理分离，修复一类证据不匹配，并对重建的归档重新运行相同的检查。

对于关于关键词、截图标题、产品页面元数据或元数据拒绝风险的问题，从合规角度回答，并明确将关键词研究、排名策略、转化优化、截图排序和 A/B 测试委托给 `app-store-optimization`。将 App Review 元数据指南限制在准确性、字段限制、误导性内容风险和截图合规性。从 [当前版本要求](references/review-checklists.md#当前版本要求) 加载日期格式、截图和工具链事实。

对于完整的提交准备审核，将阻止上传/审核问题与普通清理分开。交叉检查隐私声明、App Store 隐私营养标签、隐私政策、ATT 状态、运行时网络行为和 SDK 行为；声明和观察到的行为必须一致。

### 阻止提交检查

在普通清理前将这些问题升级为障碍：

- 归档缺少当前的 Xcode 或平台 SDK 上传底线
- 未解决的隐私证据不匹配；与 [PrivacyInfo.xcprivacy 要求](#privacynfoxcprivacy-隐私声明要求) 进行协调
- 未能通过 [StoreKit 规则](#应用内购买和storekit规则指南-311) 的支付路径
- 缺少当前 App Store Connect 规范要求的截图集
- 审核访问失败指南 2.1 完整性证据以下

## 常见拒绝原因及避免方法

| 指南风险 | 版本证据 |
|---|---|
| 2.1 完整性 | 无占位符、损坏/空的流程、无法访问的仅硬件功能或无工作演示凭证和审核笔记的登录门禁。 |
| 2.3 元数据 | 应用名称、类别、描述、关键词和截图准确反映提交的二进制文件和实际 UI。 |
| 4.2 最小功能 | 应用提供比薄网站或系统行为的简单重复更有意义的应用特定价值。 |
| 2.5.1 软件要求 | 归档使用公共 API，并且不会下载在记录的例外之外改变已审核功能的代码。 |

根据当前指南和精确的归档进行验证；不要将版本或截图要求从旧版本检查清单中继承。

## PrivacyInfo.xcprivacy -- 隐私声明要求

当您的应用代码、可执行文件、动态库或第三方 SDK 使用 Apple 的 required-reason API 类别或声明收集数据/追踪行为时，需要隐私声明。

**参见：** [references/privacy-manifest.md](references/privacy-manifest.md) 获取完整结构、原因代码和检查清单。

### 摘要

- required-reason API 类别是文件时间戳、系统启动时间、磁盘空间、活动键盘和 UserDefaults；每个使用时都需要一个批准的原因代码。
- 在最终提交前，重新检查 Apple 当前的 required-reason API 文档，并且不要选择宽泛、方便或虚构的原因代码。
- required-reason API 声明属于包含使用 API 的代码的包；每个包含与声明相关的代码的应用目标、可执行文件、动态库、框架或 SDK 包都需要匹配的声明。
- 每个收集数据、使用 required-reason API、启用数据收集/追踪或联系追踪域的 SDK、可执行文件或动态库需要在包含该代码的包中进行声明关注；SDK 代码不能依赖主机应用的声明来报告 SDK 自己的使用情况。
- 声明必须与应用商店隐私营养标签、SDK 行为和应用呈现的功能相匹配。

## 数据使用、共享和隐私政策（指南 5.1.2）

- 隐私政策 URL 必须在 App Store Connect 中设置，并且在应用内可访问
- 隐私政策必须准确描述您收集的数据、如何使用这些数据以及与谁共享
- App Store 隐私营养标签必须与您的实际数据收集实践相匹配
- 隐私标签、隐私声明、SDK 披露和运行时行为应该讲述相同的故事

## 应用内购买和 StoreKit 规则（指南 3.1.1）

数字商品、功能、订阅、虚拟货币、广告移除和数字小费通常需要 IAP，除非当前指南例外、商店规则或批准的权限适用。实体商品和现实世界服务使用其普通支付流程。在购买前，显示价格、持续时间、续订/试用条款、计费频率和取消条款；验证产品分类、恢复、权限验证、延迟/中断购买和 Ask to Buy。加载 `storekit` 进行实现，并在标记路径合规前重新检查当前区域/外部链接规则。

## HIG 合规性检查清单

从 [review-checklists.md](references/review-checklists.md) 加载完整的 HIG 检查，包括导航、模态、小部件、系统功能、启动屏幕和空状态。

## 应用追踪透明度（ATT）

### ATT 适用情况

如果您的应用跨其他公司的应用或网站追踪用户，您必须：

1. 在任何跨应用或跨网站追踪发生之前，通过 `ATTrackingManager.requestTrackingAuthorization` 请求权限，包括追踪能力强的 SDK 行为
2. 尊重用户的选择——如果用户拒绝权限，则禁用跨应用和跨网站追踪
3. 不得将应用功能与追踪同意挂钩（“接受追踪或您无法使用此应用”会被拒绝）
4. 在 `NSUserTrackingUsageDescription` 中提供清晰的目的字符串，解释追踪的用途

### ATT 不适用情况

如果您不跨应用或网站追踪用户，则不要显示 ATT 提示。Apple 拒绝不必要的 ATT 提示。

### ATT 实现

```swift
import AppTrackingTransparency

@MainActor
func requestTrackingPermission() async {
    let status = await ATTrackingManager.requestTrackingAuthorization()
    switch status {
    case .authorized:
        // 启用追踪，使用追踪初始化广告 SDK
        break
    case .denied, .restricted:
        // 使用非个性化广告并禁用跨应用/跨网站追踪
        break
    case .notDetermined:
        // 不应该发生，请求后应优雅处理
        break
    @unknown default:
        break
    }
}
```

**时机：** 在应用活跃且用户有理由请求追踪的背景后请求 ATT 权限。不要在首次启动时立即显示提示，也不要将其与其他系统权限提示堆叠。

## 欧盟数字市场法案（DMA）注意事项

替代分发、浏览器引擎、签名和外部支付路径是区域和权限特定的。重新检查当前商店规则，并将不支持的路由视为障碍。

## 权限和功能

每个权限都需要一个活跃的功能、在适用时特定的使用描述，以及匹配的归档行为。使用 [权限和使用描述](references/review-checklists.md#权限和使用描述) 中的表格和有效属性列表示例。

## 提交工作流程

### 提交前步骤

1. **在 Xcode 中归档。** 产品 > 归档（需要分发签名身份）。验证归档在 Release 配置下构建无警告。
2. **上传到 App Store Connect。** 使用 Organizer 窗口（Distribute App > App Store Connect）或 `xcodebuild -exportArchive`。通过 `altool` 或 Transporter 的自动上传也有效。
3. **TestFlight 内部测试。** 构建在处理后的几分钟内即可供内部测试人员（您的团队）使用。在至少两个设备尺寸上走遍每个屏幕和流程。
4. **TestFlight 外部测试。** 外部组需要 Beta App Review 才能进行首次外部分发。使用此方法在完整提交前与真实用户验证。
5. **提交审核。** 在 App Store Connect 中，选择构建，填写所有元数据字段，附加截图，然后点击提交审核。审核时间各不相同；为拒绝、申诉和元数据修复预留缓冲时间。

### 加速审核请求

仅针对 Apple 文档的关键或时间敏感情况请求加速审核，并在 App Store Connect 的 Contact Us 表单中提供简洁的事实性理由。

### 分阶段发布

使用 [分阶段发布计划](references/review-checklists.md#分阶段发布计划) 进行发布百分比和 App Store Connect 控制。

## 元数据最佳实践

保持名称、副标题、关键词、截图和预览与提交的二进制文件和实际 UI 准确。不要使用价格、竞争对手术语或误导性声明。应用来自 [元数据合规性检查清单](references/review-checklists.md#元数据合规性检查清单) 的字段限制和媒体规则，并将研究、排名、转化、截图排序和 A/B 测试委托给 `app-store-optimization`。

## 申诉流程

在 App Store Connect 的 Resolution Center 中回复，并提供简洁的证据链：

- [ ] 将拒绝映射到引用的指南和精确的提交行为。
- [ ] 如果已修复，请识别精确的更改并重新提交；如果存在争议，请解释提交如何满足每个相关要求。
- [ ] 附加重新创建合规性所需的证据，例如工作演示凭证、截图或专注的视频演示。
- [ ] 如果交流仍未解决，通过 Resolution Center 或 App Store Contact 表单（App Review > Appeal）请求 App Review Board 升级，包括完整的提交历史和证据。

Board 的决定对该提交是最终决定；修改应用并重新提交仍然是可行的。

## 常见错误

1. **模糊的使用描述。** 指出使用数据的特定功能。
2. **将代码质量视为审核合规。** 并发性和事务正确性不能替代隐私、支付、元数据和权限证据。

## 审核检查清单

每次提交前快速检查（完整版本在 [references/review-checklists.md](references/review-checklists.md)）：

- [ ] 通过 [阻止提交检查](#阻止提交检查) 的指南 2.1 完整性和审核访问
- [ ] 应用名称和截图与二进制文件和当前发布要求匹配
- [ ] 隐私证据通过 [PrivacyInfo.xcprivacy 要求](#privacynfoxcprivacy-隐私声明要求)
- [ ] 隐私政策 URL 设置并在应用内可访问
- [ ] 支付路径通过 [StoreKit 规则](#应用内购买和storekit规则指南-311)
- [ ] 支持暗模式和动态类型；标准导航模式
- [ ] 归档和权限通过 [阻止提交检查](#阻止提交检查)
- [ ] ATT 行为通过 [ATT 标准](#应用追踪透明度att)

## 参考资料

- 审核检查清单：[references/review-checklists.md](references/review-checklists.md)
- 隐私声明指南：[references/privacy-manifest.md](references/privacy-manifest.md)
- Apple App Review 指南：https://developer.apple.com/app-store/review/guidelines/
- Apple 即将生效的 SDK 要求：https://developer.apple.com/news/upcoming-requirements/
- App Store Connect 截图规范：https://developer.apple.com/help/app-store-connect/reference/app-information/screenshot-specifications/
- Sosumi required-reason API 文档：https://sosumi.ai/documentation/bundleresources/describing-use-of-required-reason-api
