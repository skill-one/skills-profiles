# FinanceKit

可以从 Apple Wallet 中访问符合条件的金融数据，包括美国 Apple Card、Apple Cash、储蓄以及英国连接账户数据。FinanceKit 提供设备本地访问账户、余额和交易的功能，并具有用户控制的授权。目标为 Swift 6.3 / 当前 Apple 平台；查询 API 从 iOS/iPadOS 17.4 开始可用，`TransactionPicker` 从 iOS/iPadOS 18 开始可用，背景交付从 iOS/iPadOS 26 开始可用。

将 FinanceKit 指南重点集中在金融数据访问、Wallet 订单存储/查询、TransactionPicker 和背景交付上。将 Apple Pay 结账路由到 PassKit，将小部件 UI/时间线工作路由到 WidgetKit，并将 Wallet 订单跟踪电子邮件或 Apple Business Connect 优化放在此技能之外。

## 目录

- [设置和权限](#设置和权限)
- [数据可用性](#数据可用性)
- [授权](#授权)
- [查询账户](#查询账户)
- [账户余额](#账户余额)
- [查询交易](#查询交易)
- [长时间运行的查询和历史记录](#长时间运行的查询和历史记录)
- [交易选择器](#交易选择器)
- [Wallet 订单](#wallet订单)
- [背景交付](#背景交付)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 设置和权限

### 要求

1. **受管理的权限** -- 通过 [FinanceKit 权限申请表](https://developer.apple.com/contact/request/financekit/) 向 Apple 申请 `com.apple.developer.financekit`。这是一个受管理的功能；Apple 会审核每个应用程序。
2. **组织级别的 Apple Developer 账户**（个人账户不符合条件）。
3. **账户持有人角色** -- 需要此角色来申请权限。
4. **符合条件的 App Store 应用** -- 应用程序必须属于金融类别，通过美国或英国的 App Store 发布，并提供金融管理工具，例如净资产、支出或预算功能。
5. **按 bundle-ID 审批** -- Apple 将权限分配给批准的 bundle ID；不要假设它自动适用于兄弟应用或扩展。
6. 如果应用程序直接或通过受监管机构提供金融产品，则必须允许客户将这些账户连接到 Apple Wallet 并与 FinanceKit 共享数据。

### 项目配置

1. 在 Apple 批准请求后，通过 Xcode 受管理的功能添加 FinanceKit 权限。
2. 向 Info.plist 添加 `NSFinancialDataUsageDescription` -- 此字符串在授权提示时向用户显示。
3. 对于 iOS 26 背景交付，将 FinanceKit 权限添加到应用程序和扩展目标，然后使用 App Groups 进行共享存储。

```xml
<key>NSFinancialDataUsageDescription</key>
<string>此应用程序使用您的金融数据来跟踪支出并提供预算洞察。</string>
```

## 数据可用性

美国 FinanceKit 金融数据需要 iOS/iPadOS 17.4+，目前涵盖符合条件的 Apple Card、Apple Cash 和储蓄数据；Apple Card 家庭参与者和 Apple Cash 家庭儿童被排除在外。英国支持需要 iOS/iPadOS 18.4+，并使用支持机构的开放银行。订单 API 可与金融数据查询 API 分开使用。

在执行任何 API 调用之前，检查设备是否支持 FinanceKit。此值在启动和 iOS 版本之间保持不变。

```swift
import FinanceKit

guard FinanceStore.isDataAvailable(.financialData) else {
    // FinanceKit 不可用 -- 不要调用任何其他金融数据 API。
    // 如果在不可用时调用，框架将终止应用程序。
    return
}
```

对于 Wallet 订单：

```swift
guard FinanceStore.isDataAvailable(.orders) else { return }
```

返回 `true` 的数据可用性并不能保证设备上存在数据。数据访问也可能暂时受限（例如，Wallet 不可用，MDM 限制）。受限访问会抛出 `FinanceError.dataRestricted` 而不是终止。

## 授权

请求访问用户选择的金融账户的授权。系统将显示一个账户选择器，用户可以在其中选择要共享的账户以及要暴露的最早交易日期。

```swift
let store = FinanceStore.shared

let status = try await store.requestAuthorization()
switch status {
case .authorized:    break  // 继续查询
case .denied:        break  // 用户拒绝
case .notDetermined: break  // 没有做出有意义的选择
@unknown default:    break
}
```

### 检查当前状态

不提示即可查询当前授权状态：

```swift
let currentStatus = try await store.authorizationStatus()
```

一旦用户授予权限或拒绝访问，`requestAuthorization()` 将返回缓存的决策，而不会再次显示提示。用户可以在“设置”>“隐私与安全”>“金融数据”中更改访问权限。

## 查询账户

账户被建模为一个枚举，有两个情况：`.asset`（例如，Apple Cash、储蓄）和 `.liability`（例如，Apple Card 信用）。两者共享常见属性（`id`、`displayName`、`institutionName`、`currencyCode`），而负债账户会添加信用特定字段。

```swift
func fetchAccounts() async throws -> [Account] {
    let query = AccountQuery(
        sortDescriptors: [SortDescriptor(\Account.displayName)],
        predicate: nil,
        limit: nil,
        offset: nil
    )

    return try await store.accounts(query: query)
}
```

### 处理账户类型

```swift
switch account {
case .asset(let asset):
    print("资产账户，货币：\(asset.currencyCode)")
case .liability(let liability):
    if let limit = liability.creditInformation.creditLimit {
        print("信用额度：\(limit.amount) \(limit.currencyCode)")
    }
}
```

## 账户余额

余额表示在某个时间点账户中的金额。`CurrentBalance` 是三种情况之一：`.available`（包括待处理）、`.booked`（仅已记录）或 `.availableAndBooked`。

```swift
func fetchBalances(for accountID: UUID) async throws -> [AccountBalance] {
    let predicate = #Predicate<AccountBalance> { balance in
        balance.accountID == accountID
    }

    let query = AccountBalanceQuery(
        sortDescriptors: [SortDescriptor(\AccountBalance.id)],
        predicate: predicate,
        limit: nil,
        offset: nil
    )

    return try await store.accountBalances(query: query)
}
```

### 读取余额金额

金额始终为正数小数。使用 `creditDebitIndicator` 确定符号：

```swift
func formatBalance(_ balance: Balance) -> String {
    let sign = balance.creditDebitIndicator == .debit ? "-" : ""
    return "\(sign)\(balance.amount.amount) \(balance.amount.currencyCode)"
}

// 从 CurrentBalance 枚举中提取：
switch balance.currentBalance {
case .available(let bal):       formatBalance(bal)
case .booked(let bal):          formatBalance(bal)
case .availableAndBooked(let available, _): formatBalance(available)
@unknown default: "Unknown"
}
```

## 查询交易

使用 `TransactionQuery` 并结合 Swift 断言、排序描述符、限制和偏移量。

```swift
let predicate = #Predicate<Transaction> { $0.accountID == accountID }

let query = TransactionQuery(
    sortDescriptors: [SortDescriptor(\Transaction.transactionDate, order: .reverse)],
    predicate: predicate,
    limit: 50,
    offset: nil
)

let transactions = try await store.transactions(query: query)
```

### 读取交易数据

```swift
let amount = transaction.transactionAmount
let direction = transaction.creditDebitIndicator == .debit ? "支出" : "收入"
print("\(transaction.transactionDescription): \(direction) \(amount.amount) \(amount.currencyCode)")
// merchantName, merchantCategoryCode, foreignCurrencyAmount 是可选的
```

### 内置断言辅助方法

FinanceKit 提供了用于常见过滤器的工厂方法：

```swift
// 按交易状态过滤
let bookedOnly = TransactionQuery.predicate(forStatuses: [.booked])

// 按交易类型过滤
let purchases = TransactionQuery.predicate(forTransactionTypes: [.pointOfSale, .directDebit])

// 按商户类别过滤
let groceries = TransactionQuery.predicate(forMerchantCategoryCodes: [
    MerchantCategoryCode(rawValue: 5411)  // 超市
])
```

有关交易字段表和更多查询模式，请参阅 [参考资料/financekit-patterns.md](references/financekit-patterns.md)。

## 长时间运行的查询和历史记录

使用基于 `AsyncSequence` 的历史记录 API 进行追赶同步、实时更新或可恢复同步。这些返回插入、更新和删除的项目 ID 以及一个 `HistoryToken`。

```swift
func catchUpTransactions(for accountID: UUID) async throws {
    let history = store.transactionHistory(
        forAccountID: accountID,
        since: loadSavedToken(),
        isMonitoring: false  // 保存令牌追赶后结束
    )

    for try await changes in history {
        removeLocalRecords(withIDs: changes.deleted)
        upsert(changes.inserted + changes.updated)
        saveToken(changes.newToken)
    }
}
```

### 历史令牌持久化

`HistoryToken` 符合 `Codable`。将其持久化以在不重新处理数据的情况下恢复查询：

```swift
func saveToken(_ token: FinanceStore.HistoryToken) {
    if let data = try? JSONEncoder().encode(token) {
        UserDefaults.standard.set(data, forKey: "financeHistoryToken")
    }
}

func loadSavedToken() -> FinanceStore.HistoryToken? {
    guard let data = UserDefaults.standard.data(forKey: "financeHistoryToken") else { return nil }
    return try? JSONDecoder().decode(FinanceStore.HistoryToken.self, from: data)
}
```

如果保存的令牌指向压缩的历史记录，框架将抛出 `FinanceError.historyTokenInvalid`。丢弃令牌，然后立即运行受影响账户或余额流的最新追赶查询，以便本地状态和替换令牌被重建。仅当有单独的实时监视器时，才使用 `isMonitoring: true`。

### 账户和余额历史记录

```swift
let accountChanges = store.accountHistory(since: nil, isMonitoring: true)
let balanceChanges = store.accountBalanceHistory(forAccountID: accountID, since: nil, isMonitoring: true)
```

持续的预算同步应涵盖用户授权的数据模型：账户对象用于账户的添加/删除，账户余额用于趋势和 Widget 状态，交易用于支出详情。为每个流或账户使用单独的历史令牌，以便压缩令牌仅强制重新同步受影响的流。

## 交易选择器

对于需要选择性和临时访问而不需要完全授权的应用程序，使用 FinanceKitUI 中的 `TransactionPicker`。访问权限不会持久化 -- 交易将直接传递以立即使用。

```swift
import FinanceKitUI

struct ExpenseImportView: View {
    @State private var selectedTransactions: [Transaction] = []

    var body: some View {
        if FinanceStore.isDataAvailable(.financialData) {
            TransactionPicker(selection: $selectedTransactions) {
                Label("导入交易", systemImage: "creditcard")
            }
        }
    }
}
```

## Wallet 订单

FinanceKit 支持保存和查询 Wallet 订单（例如，购买收据、运输跟踪）。

### 保存订单

```swift
let result = try await store.saveOrder(signedArchive: archiveData)
switch result {
case .added:        break  // 已保存
case .cancelled:    break  // 用户取消
case .newerExisting: break // 新版本已存在于 Wallet 中
@unknown default:   break
}
```

### 检查现有订单

```swift
let orderID = FullyQualifiedOrderIdentifier(
    orderTypeIdentifier: "com.merchant.order",
    orderIdentifier: "ORDER-123"
)
let result = try await store.containsOrder(matching: orderID, updatedDate: lastKnownDate)
// result: .exists, .newerExists, .olderExists, 或 .notFound
```

### 添加订单到 Wallet 按钮（FinanceKitUI）

```swift
import FinanceKitUI

AddOrderToWalletButton(signedArchive: orderData) { result in
    // result: .success(SaveOrderResult) 或 .failure(Error)
}
```

## 背景交付

iOS 26+ 支持背景交付扩展，可以在应用程序生命周期之外通知应用程序金融数据变化。在主应用程序中进行的用户授权将继承到扩展中。两个目标都需要 FinanceKit 权限；使用 App Groups 在应用程序、扩展和相关小部件之间共享数据。

### 启用背景交付

这些注册方法是同步且非抛出的；不要写 `try` 或 `await`。

```swift
store.enableBackgroundDelivery(
    for: [.accounts, .accountBalances, .transactions],
    frequency: .daily
)
```

可用频率：`.hourly`、`.daily`、`.weekly`。这些是扩展启动时数据变化之间的预期最小间隔；更长的频率为扩展提供更大的处理窗口。

选择性地或完全禁用：

```swift
store.disableBackgroundDelivery(for: [.transactions])
store.disableAllBackgroundDelivery()
```

### 背景交付扩展

在 Xcode 中创建一个背景交付扩展目标（背景交付扩展模板）。直接在扩展类型上实现两个异步入口点，并在 `didReceiveData(for:)` 中返回后仅保存必要的工作。

```swift
import FinanceKit

@main
struct MyFinanceExtension: BackgroundDeliveryExtension {
    func didReceiveData(for types: [FinanceStore.BackgroundDataType]) async {
        if types.contains(.transactions) {
            await processNewTransactions()
        }
        if types.contains(.accountBalances) {
            await updateBalanceCache()
        }
        if types.contains(.accounts) {
            await refreshAccountList()
        }
    }

    func willTerminate() async { await savePartialWork() }
}
```

## 常见错误

### 1. 在数据不可用时调用 API

不要这样做 -- 跳过可用性检查：
```swift
let store = FinanceStore.shared
let status = try await store.requestAuthorization() // 如果不可用则终止
```

应该这样做 -- 首先检查可用性：
```swift
guard FinanceStore.isDataAvailable(.financialData) else {
    showUnavailableMessage()
    return
}
let status = try await FinanceStore.shared.requestAuthorization()
```

### 2. 忽略信用/借记指示器

不要这样做 -- 将金额视为有符号值：
```swift
let spent = transaction.transactionAmount.amount // 始终为正
```

应该这样做 -- 应用指示器：
```swift
let amount = transaction.transactionAmount.amount
let signed = transaction.creditDebitIndicator == .debit ? -amount : amount
```

### 3. 不处理数据限制错误

不要这样做 -- 假设授权访问持续存在：
```swift
let transactions = try await store.transactions(query: query) // 如果 Wallet 受限则失败
```

应该这样做 -- 捕获 `FinanceError`：
```swift
do {
    let transactions = try await store.transactions(query: query)
} catch let error as FinanceError {
    if case .dataRestricted = error { showDataRestrictedMessage() }
}
```

### 4. 用快照替换可恢复历史记录

使用上述规范交易历史记录循环，并在本地删除和 upsert 提交后仅持久化每个 `newToken`。为每个流/账户保留单独的令牌；在无效令牌错误的情况下，仅重新同步受影响的范围。

### 5. 误解负债账户的信用/借记

资产和负债账户都使用 `.debit` 表示支出。但 `.credit` 意味着不同的事情：在资产账户上它表示收到的钱；在负债账户上它表示增加可用信用的付款或退款。有关完整解释表，请参阅 [参考资料/financekit-patterns.md](references/financekit-patterns.md)。

## 审查清单

- [ ] 在任何 API 调用之前检查 `FinanceStore.isDataAvailable(.financialData)`
- [ ] 检查应用资格：金融类别、美国或英国的 iPhone App Store 分发、金融管理功能集、组织账户、账户持有人请求
- [ ] 为应用程序 bundle ID 请求并批准 `com.apple.developer.financekit` 权限
- [ ] 在 Info.plist 中设置 `NSFinancialDataUsageDescription` 并提供清晰、具体的信息
- [ ] 处理所有情况的授权状态（`.authorized`、`.denied`、`.notDetermined`）
- [ ] 捕获并优雅处理 `FinanceError.dataRestricted`
- [ ] 正确应用 `CreditDebitIndicator` 到金额（不要将其视为有符号值）
- [ ] 为可恢复查询持久化历史令牌
- [ ] 处理 `FinanceError.historyTokenInvalid` 通过丢弃令牌并立即重新同步受影响的流
- [ ] 持续同步计划涵盖授权的账户、余额和交易，而不仅仅是交易
- [ ] 当不需要实时更新时，长时间运行的查询使用 `isMonitoring: false`
- [ ] 当不需要完全授权时，使用交易选择器
- [ ] 仅查询应用程序真正需要的数据
- [ ] 从历史记录变化中明确删除已删除的 ID，从本地账户、余额或交易存储中删除
- [ ] 背景交付调用使用同步的 iOS 26 API，并且扩展与主应用程序位于同一 App Group 中
- [ ] 背景交付注册每个需要的数据类型：`.accounts`、`.accountBalances` 和/或 `.transactions`
- [ ] 将 FinanceKit 权限添加到应用程序和背景交付扩展目标
- [ ] 当用户撤销访问权限时删除金融数据

## 参考资料

- 扩展模式（断言、排序、分页、货币格式化、背景更新）：[参考资料/financekit-patterns.md](references/financekit-patterns.md)
- [开始使用 FinanceKit](https://developer.apple.com/financekit/)
- [FinanceKit 框架](https://sosumi.ai/documentation/financekit)
- [FinanceKitUI 框架](https://sosumi.ai/documentation/financekitui)
- [FinanceStore](https://sosumi.ai/documentation/financekit/financestore)
- [Transaction](https://sosumi.ai/documentation/financekit/transaction)
- [Account](https://sosumi.ai/documentation/financekit/account)
- [AccountBalance](https://sosumi.ai/documentation/financekit/accountbalance)
- [FinanceKit 权限](https://sosumi.ai/documentation/bundleresources/entitlements/com.apple.developer.financekit)
- [实现背景交付扩展](https://sosumi.ai/documentation/financekit/implementing-a-background-delivery-extension)
- [了解 FinanceKit (WWDC24)](https://sosumi.ai/videos/play/wwdc2024/2023/)
- [Apple Pay 新功能 (WWDC25)](https://sosumi.ai/videos/play/wwdc2025/201/)
