# StoreKit 2 应用内购买和订阅

使用 StoreKit 2 实现应用内购买、订阅、付费墙和 StoreKit 测试。使用基于 Swift 的现代 `Product`、`Transaction`、`PurchaseAction`、`StoreView` 和 `SubscriptionStoreView` API。除非旧版操作系统支持需要，否则避免使用原始应用内购买 API (`SKProduct`、`SKPaymentQueue`)。

StoreKit 视图会自动发起购买。对于自定义控件，在 SwiftUI 中使用 `PurchaseAction`，在 UIKit/AppKit 中使用 `purchase(confirmIn:options:)`，在 watchOS 上使用 `product.purchase(options:)`。

## 目录

- [产品类型](#产品类型)
- [加载产品](#加载产品)
- [购买流程](#购买流程)
- [Transaction.updates 监听器](#transactionupdates-listener)
- [权限检查](#权限检查)
- [SubscriptionStoreView (iOS 17+)](#subscriptionstoreview-ios-17)
- [StoreView (iOS 17+)](#storeview-ios-17)
- [订阅状态检查](#订阅状态检查)
- [恢复购买](#恢复购买)
- [应用交易 (应用购买验证)](#app-transaction-app-purchase-verification)
- [购买选项](#购买选项)
- [SwiftUI 购买回调](#swiftui-purchase-callbacks)
- [常见错误](#常见错误)
- [审核清单](#审核清单)
- [参考资料](#参考资料)

## 产品类型

| 类型 | 枚举案例 | 行为 |
|---|---|---|
| **消耗品** | `.consumable` | 使用一次，可以重新购买（宝石、金币） |
| **非消耗品** | `.nonConsumable` | 购买一次永久（高级解锁） |
| **自动续订** | `.autoRenewable` | 周期性计费，自动续订 |
| **非续订** | `.nonRenewing` | 限时访问，无需自动续订 |

## 加载产品

将产品 ID 定义为常量。使用 `Product.products(for:)` 获取产品。

```swift
import StoreKit

enum ProductID {
    static let premium = "com.myapp.premium"
    static let gems100 = "com.myapp.gems100"
    static let monthlyPlan = "com.myapp.monthly"
    static let yearlyPlan = "com.myapp.yearly"
    static let all: [String] = [premium, gems100, monthlyPlan, yearlyPlan]
}

let products = try await Product.products(for: ProductID.all)
for product in products {
    print("\(product.displayName): \(product.displayPrice)")
}
```

## 购买流程

优先使用 StoreKit 视图实现标准付费墙，因为它们会自动发起购买、恢复购买并显示政策控件。对于自定义 SwiftUI 购买按钮，优先使用环境中的 `PurchaseAction`。对于 watchOS，使用直接 `product.purchase(options:)`；对于 UIKit 或 AppKit，使用 `purchase(confirmIn:options:)` 进行确认。始终处理每个 `PurchaseResult`，在访问前验证，持久化交付，然后完成。

```swift
@Environment(\.purchase) private var purchase

func purchaseProduct(_ product: Product) async throws {
    let result = try await purchase(product, options: [
        .appAccountToken(userAccountToken)
    ])
    switch result {
    case .success(let verification):
        let transaction = try checkVerified(verification)
        await deliverContent(for: transaction)
        await transaction.finish()
    case .userCancelled:
        break
    case .pending:
        // 询问购买或延迟批准：显示待处理界面，尚未解锁。
        showPendingApprovalMessage()
    @unknown default:
        break
    }
}

func checkVerified<T>(_ result: VerificationResult<T>) throws -> T {
    switch result {
    case .verified(let value): return value
    case .unverified(_, let error): throw error
    }
}
```

## Transaction.updates 监听器

在应用启动时开始，而不是在付费墙出现时。捕获来自其他设备的购买、家庭共享更改、续订、询问购买批准、退款、撤销和 Apple 启动后立即发出的未完成交易。保留任务以保持应用生命周期。

```swift
@main
struct MyApp: App {
    private let transactionListener: Task<Void, Never>

    init() {
        transactionListener = Self.listenForTransactions()
    }

    var body: some Scene {
        WindowGroup { ContentView() }
    }

    static func listenForTransactions() -> Task<Void, Never> {
        Task(priority: .background) {
            for await result in Transaction.updates {
                guard case .verified(let transaction) = result else { continue }
                await StoreManager.shared.updateEntitlements()
                await transaction.finish()
            }
        }
    }
}
```

## 权限检查

`Transaction.currentEntitlements` 发送非消耗品、活跃或宽限期自动续订订阅，以及最新的非续订订阅交易（包括已完成的）。它不包括消耗品和已退款或撤销的产品。单独跟踪消耗品的履行情况，并在授予访问权限之前应用应用的过期策略。

```swift
@Observable
@MainActor
class StoreManager {
    static let shared = StoreManager()
    var purchasedProductIDs: Set<String> = []
    var isPremium: Bool { purchasedProductIDs.contains(ProductID.premium) }

    func updateEntitlements() async {
        var purchased = Set<String>()
        for await result in Transaction.currentEntitlements {
            if case .verified(let transaction),
               transaction.revocationDate == nil {
                if transaction.productType == .nonRenewing,
                   transaction.expirationDate.map({ $0 <= .now }) ?? true {
                    continue
                }
                purchased.insert(transaction.productID)
            }
        }
        purchasedProductIDs = purchased
    }
}
```

### SwiftUI .currentEntitlementTask 修饰符

```swift
struct PremiumGatedView: View {
    @State private var state: EntitlementTaskState<VerificationResult<Transaction>?> = .loading

    var body: some View {
        Group {
            switch state {
            case .loading: ProgressView()
            case .failure: PaywallView()
            case .success(.some(.verified(let transaction))) where transaction.revocationDate == nil:
                PremiumContentView()
            case .success:
                PaywallView()
            }
        }
        .currentEntitlementTask(for: ProductID.premium) { state in
            self.state = state
        }
    }
}
```

## SubscriptionStoreView (iOS 17+)

内置 SwiftUI 视图，用于订阅付费墙。自动处理产品加载、购买 UI 和恢复购买。

```swift
SubscriptionStoreView(groupID: "YOUR_GROUP_ID")
    .subscriptionStoreControlStyle(.prominentPicker)
    .subscriptionStoreButtonLabel(.multiline)
    .storeButton(.visible, for: .restorePurchases)
    .storeButton(.visible, for: .redeemCode)
    .subscriptionStorePolicyDestination(url: termsURL, for: .termsOfService)
    .subscriptionStorePolicyDestination(url: privacyURL, for: .privacyPolicy)
    .onInAppPurchaseCompletion { product, result in
        if case .success(.success(.verified(let transaction))) = result {
            await deliverContent(for: transaction)
            await transaction.finish()
        }
    }
```

### 自定义营销内容

在 [SubscriptionStoreView 控制样式](references/storekit-advanced.md#subscriptionstoreview-control-styles) 中使用容器背景和标题图案。

### 分层布局

使用 `SubscriptionOptionGroup`、`SubscriptionOptionSection` 或 `SubscriptionPeriodGroupSet` 组织 iOS 18+ 选项；请参阅 [订阅组管理](references/storekit-advanced.md#subscription-group-management)。

## StoreView (iOS 17+)

使用本地化名称、价格和购买按钮对多个产品进行商品化。

```swift
StoreView(ids: [ProductID.gems100, ProductID.premium], prefersPromotionalIcon: true)
    .productViewStyle(.large)
    .storeButton(.visible, for: .restorePurchases)
    .onInAppPurchaseCompletion { product, result in
        if case .success(.success(.verified(let transaction))) = result {
            await deliverContent(for: transaction)
            await transaction.finish()
        }
    }
```

### 单个产品的 ProductView

```swift
ProductView(id: ProductID.premium) { iconPhase in
    switch iconPhase {
    case .success(let image): image.resizable().scaledToFit()
    case .loading: ProgressView()
    default: Image(systemName: "star.fill")
    }
}
.productViewStyle(.large)
```

## 订阅状态检查

```swift
func checkSubscriptionActive(groupID: String) async throws -> Bool {
    let statuses = try await Product.SubscriptionInfo.status(for: groupID)
    for status in statuses {
        guard case .verified = status.renewalInfo,
              case .verified = status.transaction else { continue }
        if status.state == .subscribed || status.state == .inGracePeriod {
            return true
        }
    }
    return false
}
```

### 续订状态

| 状态 | 含义 |
|---|---|
| `.subscribed` | 活跃订阅 |
| `.expired` | 订阅已过期 |
| `.inBillingRetryPeriod` | 支付失败，Apple 正在重试 |
| `.inGracePeriod` | 支付失败但在宽限期内继续访问 |
| `.revoked` | Apple 退款或撤销了订阅 |

## 恢复购买

StoreKit 2 通过 `Transaction.currentEntitlements` 处理恢复。添加恢复按钮或显式调用 `AppStore.sync()`。

```swift
func restorePurchases() async throws {
    try await AppStore.sync()
    await StoreManager.shared.updateEntitlements()
}
```

在商店视图中：`.storeButton(.visible, for: .restorePurchases)`

## 应用交易 (应用购买验证)

验证应用安装的合法性。用于业务模式更改或检测被篡改的安装（iOS 16+）。

```swift
func verifyAppPurchase() async {
    do {
        let result = try await AppTransaction.shared
        switch result {
        case .verified(let appTransaction):
            let originalVersion = appTransaction.originalAppVersion
            let purchaseDate = appTransaction.originalPurchaseDate
            // 迁移逻辑，针对在订阅模式之前付费的用户
        case .unverified:
            // 可能被篡改 -- 适当限制功能
            break
        }
    } catch { /* 无法检索应用交易 */ }
}
```

## 购买选项

```swift
// 应用账户令牌用于服务器端对账
try await product.purchase(options: [.appAccountToken(UUID())])

// 消耗品数量
try await product.purchase(options: [.quantity(5)])

// 在沙盒中模拟询问购买
try await product.purchase(options: [.simulatesAskToBuyInSandbox(true)])
```

## SwiftUI 购买回调

```swift
.onInAppPurchaseStart { product in
    await analytics.trackPurchaseStarted(product.id)
}
.onInAppPurchaseCompletion { product, result in
    if case .success(.success(.verified(let transaction))) = result {
        await deliverContent(for: transaction)
        await transaction.finish()
    }
}
.inAppPurchaseOptions { product in
    [.appAccountToken(userAccountToken)]
}
```

## 常见错误

### 1. 在应用启动时未启动 Transaction.updates

```swift
// 错误：没有监听器 -- 错过续订、退款、询问购买批准
@main struct MyApp: App {
    var body: some Scene { WindowGroup { ContentView() } }
}
// 正确：在 App 初始化中启动监听器（见 Transaction.updates 部分上述内容）
```

### 2. 忘记调用 transaction.finish()

```swift
// 错误：从未完成 -- 永久出现在未完成队列中
let transaction = try checkVerified(verification)
unlockFeature(transaction.productID)

// 正确：持久化交付后调用 finish。如果交付失败，则不要 yet finish。
let transaction = try checkVerified(verification)
try await recordDelivery(transaction)
await transaction.finish()
```

### 3. 忽略验证结果

```swift
// 错误：使用未验证的交易 -- 安全风险
let transaction = verification.unsafePayloadValue

// 正确：在使用前验证
let transaction = try checkVerified(verification)
```

### 4. 在新的 StoreKit 2 代码中使用原始应用内购买 API

```swift
// 避免：原始应用内购买 API
let request = SKProductsRequest(productIdentifiers: ["com.app.premium"])
SKPaymentQueue.default().add(payment)

// 优先：StoreKit 2
let products = try await Product.products(for: ["com.app.premium"])
let result = try await product.purchase()
```

### 5. 未检查 revocationDate

```swift
// 错误：授予已退款购买的访问权限
if case .verified(let transaction) = result {
    purchased.insert(transaction.productID)
}

// 正确：跳过已撤销的交易
if case .verified(let transaction) = result, transaction.revocationDate == nil {
    purchased.insert(transaction.productID)
}
```

### 6. 硬编码价格

```swift
// 错误：不适用于其他货币和地区
Text("Buy Premium for $4.99")

// 正确：从 Product 获取本地化价格
Text("Buy \(product.displayName) for \(product.displayPrice)")
```

### 7. 未处理 .pending 购买结果

```swift
// 错误：静默丢弃待处理的询问购买
default: break

// 正确：解释批准正在等待；仅在 Transaction.updates 后解锁
case .pending:
    showPendingApprovalMessage()
```

### 8. 仅在启动时检查权限

```swift
// 错误：检查一次，永不更新
func appDidFinish() { Task { await updateEntitlements() } }

// 正确：在 Transaction.updates 和返回前台时重新检查
// Transaction.updates 监听器处理会话中的更改。
// 还在内容视图中使用 .task { await storeManager.updateEntitlements() }
```

### 9. 缺少恢复购买按钮

```swift
// 错误：没有恢复选项 -- App Store 拒绝风险
SubscriptionStoreView(groupID: "group_id")

// 正确
SubscriptionStoreView(groupID: "group_id")
    .storeButton(.visible, for: .restorePurchases)
```

### 10. 没有政策链接的订阅视图

```swift
// 错误：没有条款或隐私政策
SubscriptionStoreView(groupID: "group_id")

// 正确
SubscriptionStoreView(groupID: "group_id")
    .subscriptionStorePolicyDestination(url: termsURL, for: .termsOfService)
    .subscriptionStorePolicyDestination(url: privacyURL, for: .privacyPolicy)
```

## 审核清单

- [ ] `Transaction.updates` 监听器在 App 初始化时启动
- [ ] 所有交易在授予访问权限前验证
- [ ] `transaction.finish()` 仅在持久化交付后调用
- [ ] 排除已撤销/退款的交易并更新权限状态
- [ ] `.pending` 结果显示询问购买/延迟批准的反馈
- [ ] 付费墙和商店视图中可见恢复购买按钮
- [ ] 订阅视图中有条款服务和隐私政策链接
- [ ] 使用 `product.displayPrice` 显示价格，永不硬编码
- [ ] 清晰显示订阅条款（价格、持续时间、续订）
- [ ] 免费试用后清晰显示后续定价
- [ ] 除非旧版操作系统支持需要，否则不使用原始应用内购买 API (`SKProduct`、`SKPaymentQueue`)
- [ ] 产品 ID 定义为常量，而不是分散的字符串
- [ ] StoreKit 测试涵盖促销优惠、召回、优惠代码、询问购买、续订、退款和撤销
- [ ] 在 Transaction.updates 和应用前台重新检查权限
- [ ] 服务器端验证如果适用，使用 `jwsRepresentation`
- [ ] 消耗品及时交付和完成
- [ ] 交易观察者类型和产品模型类型在跨并发边界共享时是 `Sendable`

## 参考资料

- 参考 [references/app-review-guidelines.md](references/app-review-guidelines.md) 获取 IAP 规则（指南 3.1.1）、订阅显示要求和防止拒绝。
- 参考 [references/storekit-advanced.md](references/storekit-advanced.md) 获取订阅控制样式、优惠管理、测试模式和高级订阅处理。
- 提交、隐私、元数据、截图和拒绝风险审核使用 `app-store-review`。
- 关键词、截图说明、排名和转化策略使用 `app-store-optimization`。
- 官方 Apple 文档：[选择 StoreKit API](https://sosumi.ai/documentation/storekit/choosing-a-storekit-api-for-in-app-purchases)、[Transaction.updates](https://sosumi.ai/documentation/storekit/transaction/updates)、[Transaction.currentEntitlements](https://sosumi.ai/documentation/storekit/transaction/currententitlements)、
  [SubscriptionStoreView](https://sosumi.ai/documentation/storekit/subscriptionstoreview) 和 [PurchaseAction](https://sosumi.ai/documentation/storekit/purchaseaction)。
