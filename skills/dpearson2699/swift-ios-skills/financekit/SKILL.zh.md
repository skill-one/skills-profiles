---
name: financekit
description: 使用 FinanceKit 和 FinanceKitUI 访问符合条件的 Wallet 金融数据。适用于以下场景：查询交易或余额，读取 Apple Card、Apple Cash、储蓄或英国关联账户数据，请求金融数据授权，使用 TransactionPicker，启用 iOS 26 后台推送，以及保存和检查 Wallet 订单。
---

# FinanceKit

访问 Apple Wallet 中的符合条件的金融数据，包括美国 Apple Card、Apple Cash、储蓄以及英国连接账户数据。FinanceKit 提供设备本地访问账户、余额和交易的功能，并具有用户控制的授权。目标 Swift 6.3 / 当前 Apple 平台；查询 API 从 iOS/iPadOS 17.4 开始可用，`TransactionPicker` 从 iOS/iPadOS 18 开始可用，以及从 iOS/iPadOS 26 开始支持后台交付。

保持 FinanceKit 指南专注于金融数据访问、Wallet 订单存储/查询、TransactionPicker 和后台交付。将 Apple Pay 结账路由到 PassKit，将小部件 UI/时间线工作路由到 WidgetKit，并将 Wallet 订单跟踪电子邮件或 Apple Business Connect 优化工作移出此技能范围。

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
- [后台交付](#后台交付)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 设置和权限

### 要求

1. **受管理的权限** -- 通过 [FinanceKit 权限申请表](https://developer.apple.com/contact/request/financekit/) 向 Apple 申请 `com.apple.developer.financekit`。这是一个受管理的功能；Apple 会审核每个应用程序。
2. **组织级别的 Apple 开发者账户**（个人账户不符合资格）。
3. **账户持有人角色** -- 申请权限需要此角色。
4. **符合条件的 App Store 应用** -- 应用程序必须属于金融类别，通过美国或英国的 App Store 分发，并提供金融管理工具，例如净资产、支出或预算功能。
5. **按 bundle-ID 审批** -- Apple 将权限分配给已批准的 bundle ID；不要假设它自动适用于兄弟应用或扩展。
6. 如果应用程序直接或通过受监管机构提供金融产品，则必须允许客户将这些账户连接到 Apple Wallet 并与 FinanceKit 共享数据。

### 项目配置

1. 在 Apple 批准请求后，通过 Xcode 受管理的功能添加 FinanceKit 权限。
2. 向 Info.plist 添加 `NSFinancialDataUsageDescription` -- 此字符串在授权提示时向用户显示。
3. 对于 iOS 26 后台交付，将 FinanceKit 权限添加到应用程序和扩展目标，然后使用 App Groups 进行共享存储。

```xml
<key>NSFinancialDataUsageDescription</key>
<string>This app uses your financial data to track spending and provide budgeting insights.</string>
```

## 数据可用性

美国 FinanceKit 金融数据需要 iOS/iPadOS 17.4+，目前涵盖符合条件的 Apple Card、Apple Cash 和储蓄数据；Apple Card 家庭参与者和 Apple Cash 家庭儿童被排除在外。英国支持需要 iOS/iPadOS 18.4+，并使用支持机构的开放银行。订单 API 可单独于金融数据查询 API 提供。

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

数据可用性返回 `true` 并不保证设备上存在数据。数据访问也可能暂时受限（例如，Wallet 不可用，MDM 限制）。受限访问会抛出 `FinanceError.dataRestricted` 而不是终止。

## 授权

请求访问用户选择的金融账户的授权。系统会显示一个账户选择器，用户在其中选择要共享的账户以及要公开的最早交易日期。

```swift
let store = FinanceStore.shared

let status = try await store.requestAuthorization()
switch status {
case .authorized:    break  // 继续查询
case .denied:        break  // 用户拒绝
case .notDetermined: break  // 未做出有意义的选择
@unknown default:    break
}
```

### 检查当前状态

不提示即可查询当前授权状态：

```swift
let currentStatus = try await store.authorizationStatus()
```

一旦用户授予权限或拒绝，`requestAuthorization()` 将返回缓存的决策，而不会再次显示提示。用户可以在设置 > 隐私与安全 > 金融数据中更改访问权限。

## 查询账户

账户被建模为一个枚举，有两个情况：`.asset`（例如，Apple Cash、储蓄）和 `.liability`（例如，Apple Card 信用）。两者共享常见属性（`id`、`displayName`、`institutionName`、`currencyCode`），而负债账户会添加与信用相关的字段。

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
    print("Asset account, currency: \(asset.currencyCode)")
case .liability(let liability):
    if let limit = liability.creditInformation.creditLimit {
        print("Credit limit: \(limit.amount) \(limit.currencyCode)")
    }
}
```

## 账户余额

余额表示在某个时间点账户中的金额。`CurrentBalance` 是三种情况之一：`.available`（包括待处理）、`.booked`（仅已发布）或 `.availableAndBooked`。

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
let direction = transaction.creditDebitIndicator == .debit ? "spent" : "received"
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

使用基于 `AsyncSequence` 的历史记录 API 进行追赶同步、实时更新或可恢复同步。这些返回插入、更新和删除的项 ID 以及一个 `HistoryToken`。

```swift
func catchUpTransactions(for accountID: UUID) async throws {
    let history = store.transactionHistory(
        forAccountID: accountID,
        since: loadSavedToken(),
        isMonitoring: false  // 在保存的标记追赶后结束
    )

    for try await changes in history {
        removeLocalRecords(withIDs: changes.deleted)
        upsert(changes.inserted + changes.updated)
        saveToken(changes.newToken)
    }
}
```

### 历史标记持久化

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

如果保存的标记指向压缩的历史记录，框架会抛出 `FinanceError.historyTokenInvalid`。丢弃标记，然后立即为受影响的账户或余额流运行一次新的追赶查询，以便本地状态和替换标记被重建。仅对单独的实时监视器使用 `isMonitoring: true`。

### 账户和余额历史记录

```swift
let accountChanges = store.accountHistory(since: nil, isMonitoring: true)
let balanceChanges = store.accountBalanceHistory(forAccountID: accountID, since: nil, isMonitoring: true)
```

持续的预算同步应涵盖用户授权的数据模型：账户对象用于账户添加/删除，账户余额用于趋势和 Widget 状态，交易用于支出详情。为每个流或账户使用单独的历史标记，以便压缩标记仅强制重新同步受影响的流。

## 交易选择器

对于需要选择性和临时访问而不需要完全授权的应用程序，使用 FinanceKitUI 中的 `TransactionPicker`。访问不会被持久化 -- 交易将直接传递以供立即使用。

```swift
import FinanceKitUI

struct ExpenseImportView: View {
    @State private var selectedTransactions: [Transaction] = []

    var body: some View {
        if FinanceStore.isDataAvailable(.financialData) {
            TransactionPicker(selection: $selectedTransactions) {
                Label("Import Transactions", systemImage: "creditcard")
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
case .newerExisting: break // Wallet 中已有更新的版本
@unknown default:   break
}
```

### 检查是否存在订单

```swift
let orderID = FullyQualifiedOrderIdentifier(
    orderTypeIdentifier: "com.merchant.order",
    orderIdentifier: "ORDER-123"
)
let result = try await store.containsOrder(matching: orderID, updatedDate: lastKnownDate)
// result: .exists, .newerExists, .olderExists, 或 .notFound
```

### 添加订单到 Wallet 按钮 (FinanceKitUI)

```swift
import FinanceKitUI

AddOrderToWalletButton(signedArchive: orderData) { result in
    // result: .success(SaveOrderResult) 或 .failure(Error)
}
```

## 后台交付

iOS 26+ 支持后台交付扩展，可以在应用程序生命周期之外通知应用程序金融数据的变化。在主应用程序中进行的用户授权将继承到扩展中。两个目标都需要 FinanceKit 权限；使用 App Groups 在应用程序、扩展和相关小部件之间共享数据。

### 启用后台交付

这些注册方法是同步且非抛出的；不要写 `try` 或 `await`。

```swift
store.enableBackgroundDelivery(
    for: [.accounts, .accountBalances, .transactions],
    frequency: .daily
)
```

可用频率：`.hourly`、`.daily`、`.weekly`。这些是扩展启动时数据变化的预期最小间隔；更长的频率为扩展提供更大的处理窗口。

选择性地或完全禁用：

```swift
store.disableBackgroundDelivery(for: [.transactions])
store.disableAllBackgroundDelivery()
```

### 后台交付扩展

在 Xcode 中创建一个后台交付扩展目标（后台交付扩展模板）。直接在扩展类型上实现两个异步入口点，并在 `didReceiveData(for:)` 中仅保存必要的工作后返回。

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

使用上述规范交易历史记录循环，并在本地删除和 upsert 提交后仅持久化每个 `newToken`。为每个流/账户保留单独的标记；在无效标记错误的情况下，仅重新同步受影响的范围。

### 5. 误解负债账户的信用/借记

资产和负债账户都使用 `.debit` 表示支出。但 `.credit` 表示不同的事物：在资产账户上它表示收到的钱；在负债账户上它表示增加可用信用的付款或退款。有关完整解释表，请参阅 [参考资料/financekit-patterns.md](references/financekit-patterns.md)。

## 审查清单

- [ ] 在任何 API 调用之前检查 `FinanceStore.isDataAvailable(.financialData)`
- [ ] 检查应用资格：金融类别、美国或英国的 App Store iPhone 分发、财务管理功能集、组织账户、账户持有人请求
- [ ] 为应用捆绑 ID 请求并批准 `com.apple.developer.financekit` 授权
- [ ] 在 Info.plist 中设置 `NSFinancialDataUsageDescription`，并包含清晰、具体的信息
- [ ] 处理所有情况下的授权状态（`.authorized`、`.denied`、`.notDetermined`）
- [ ] 捕获并优雅地处理 `FinanceError.dataRestricted`
- [ ] 正确应用 `CreditDebitIndicator` 到金额（不将其视为有符号）
- [ ] 为可恢复查询持久化历史记录令牌
- [ ] 通过丢弃令牌并立即重新同步受影响的流来处理 `FinanceError.historyTokenInvalid`
- [ ] 持续同步计划涵盖已授权账户、余额和交易，而不仅仅是交易
- [ ] 当不需要实时更新时，长时间运行的查询使用 `isMonitoring: false`
- [ ] 在不需要完全授权时使用交易选择器
- [ ] 仅查询应用真正需要的数据
- [ ] 从历史记录更改中明确从本地账户、余额或交易存储中删除已删除的 ID
- [ ] 背景交付调用使用同步的 iOS 26 API，并且扩展与主应用位于同一 App Group 中
- [ ] 背景交付注册所有需要的数据类型：`.accounts`、`.accountBalances` 和/或 `.transactions`
- [ ] 将 FinanceKit 授权添加到应用和背景交付扩展目标
- [ ] 当用户撤销访问权限时删除金融数据

## 参考

- 扩展模式（谓词、排序、分页、货币格式化、背景更新）：[references/financekit-patterns.md](references/financekit-patterns.md)
- [开始使用 FinanceKit](https://developer.apple.com/financekit/)
- [FinanceKit 框架](https://sosumi.ai/documentation/financekit)
- [FinanceKitUI 框架](https://sosumi.ai/documentation/financekitui)
- [FinanceStore](https://sosumi.ai/documentation/financekit/financestore)
- [Transaction](https://sosumi.ai/documentation/financekit/transaction)
- [Account](https://sosumi.ai/documentation/financekit/account)
- [AccountBalance](https://sosumi.ai/documentation/financekit/accountbalance)
- [FinanceKit 授权](https://sosumi.ai/documentation/bundleresources/entitlements/com.apple.developer.financekit)
- [实现背景交付扩展](https://sosumi.ai/documentation/financekit/implementing-a-background-delivery-extension)
- [了解 FinanceKit (WWDC24)](https://sosumi.ai/videos/play/wwdc2024/2023/)
- [Apple Pay 新功能 (WWDC25)](https://sosumi.ai/videos/play/wwdc2025/201/)
