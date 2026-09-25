# PassKit

接受 Apple Pay 支付实体商品、现实世界服务、捐赠以及符合条件的周期性付款，并将通行证添加到用户的钱包中。涵盖支付按钮、支付请求、授权、钱包通行证和商家配置。目标 Swift 6.3 / iOS 26+。

对于高级 Apple Pay 流程，一个 `PKPaymentRequest` 只能设置一种可选的高级请求类型：周期性、自动续订、延迟、Apple Pay 后续可用性或多令牌上下文。当结账需要多种模式时，使用单独的支付请求。

## 内容

- [设置](#设置)
- [显示 Apple Pay 按钮](#显示-apple-pay 按钮)
- [创建支付请求](#创建支付请求)
- [显示支付表单](#显示支付表单)
- [处理支付授权](#处理支付授权)
- [钱包通行证](#钱包通行证)
- [检查通行证库](#检查通行证库)
- [常见错误](#常见错误)
- [审查清单](#审查清单)
- [参考资料](#参考资料)

## 设置

### 项目配置

1. 在 Xcode 中启用 **Apple Pay** 功能
2. 在 Apple 开发者门户中创建一个商家 ID（格式：`merchant.com.example.app`）
3. 为您的商家 ID 生成并安装支付处理证书
4. 将商家 ID 添加到您的权限中

### 可用性检查

在显示 Apple Pay UI 之前，始终验证设备可以进行支付。如果您使用 `canMakePayments(usingNetworks:capabilities:)` 检查活动卡，Apple 的 HIG 希望无论您在哪里使用该检查，Apple Pay 都是一个主要、显眼的支付选项。

```swift
import PassKit

func canMakePayments() -> Bool {
    // 检查设备是否支持 Apple Pay
    guard PKPaymentAuthorizationController.canMakePayments() else {
        return false
    }
    // 检查用户是否支持您所支持的网络的卡
    return PKPaymentAuthorizationController.canMakePayments(
        usingNetworks: [.visa, .masterCard, .amex, .discover],
        capabilities: .threeDSecure
    )
}
```

## 显示 Apple Pay 按钮

### SwiftUI

在 SwiftUI 中使用内置的 `PayWithApplePayButton` 视图。对于任何标记为 Apple Pay 的控件，请使用 Apple 提供的按钮 API；自定义按钮不得包含 Apple Pay 标志或 "Apple Pay" 文本。

```swift
import SwiftUI
import PassKit

struct CheckoutView: View {
    var body: some View {
        PayWithApplePayButton(.buy) {
            startPayment()
        }
        .payWithApplePayButtonStyle(.black)
        .frame(height: 48)
        .padding()
    }
}
```

### UIKit

对于基于 UIKit 的界面，使用 `PKPaymentButton`。

```swift
let button = PKPaymentButton(
    paymentButtonType: .buy,
    paymentButtonStyle: .black
)
button.cornerRadius = 12
button.addTarget(self, action: #selector(startPayment), for: .touchUpInside)
```

**按钮类型：** `.plain`, `.buy`, `.setUp`, `.inStore`, `.donate`, `.checkout`, `.continue`, `.book`, `.subscribe`, `.reload`, `.addMoney`, `.topUp`, `.order`, `.rent`, `.support`, `.contribute`, `.tip`

## 创建支付请求

使用您的商家详细信息以及正在购买的商品构建 `PKPaymentRequest`。PassKit 金额 API 使用 `NSDecimalNumber`，而不是 `Double`。

```swift
func createPaymentRequest() -> PKPaymentRequest {
    let request = PKPaymentRequest()
    request.merchantIdentifier = "merchant.com.example.app"
    request.countryCode = "US"
    request.currencyCode = "USD"
    request.supportedNetworks = [.visa, .masterCard, .amex, .discover]
    request.merchantCapabilities = .threeDSecure

    request.paymentSummaryItems = [
        PKPaymentSummaryItem(
            label: "Widget",
            amount: NSDecimalNumber(string: "9.99")
        ),
        PKPaymentSummaryItem(
            label: "Shipping",
            amount: NSDecimalNumber(string: "4.99")
        ),
        PKPaymentSummaryItem(
            label: "My Store",
            amount: NSDecimalNumber(string: "14.98")
        ) // 总计
    ]

    return request
}
```

`paymentSummaryItems` 中的**最后一个项目**被视为总计，其标签显示在支付表单的支付行中。

### 请求运输和联系信息

仅请求处理订单所需联系字段，以定价、履行或合法处理订单。
在支付表单无法准确收集信息时，在 Apple Pay 按钮之前收集所需的产品选择、可选备注、每项商品的运输目的地和取货地点。

```swift
request.requiredShippingContactFields = [.postalAddress, .emailAddress, .name]
request.requiredBillingContactFields = [.postalAddress]

let standard = PKShippingMethod(
    label: "Standard",
    amount: NSDecimalNumber(string: "4.99")
)
standard.identifier = "standard"
standard.detail = "5-7 个工作日"

let express = PKShippingMethod(
    label: "Express",
    amount: NSDecimalNumber(string: "9.99")
)
express.identifier = "express"
express.detail = "1-2 个工作日"

request.shippingMethods = [standard, express]

request.shippingType = .shipping // .delivery, .storePickup, .servicePickup
```

### 支持的网络

| 网络 | 常量 |
|---|---|
| Visa | `.visa` |
| Mastercard | `.masterCard` |
| American Express | `.amex` |
| Discover | `.discover` |
| China UnionPay | `.chinaUnionPay` |
| JCB | `.JCB` |
| Maestro | `.maestro` |
| Electron | `.electron` |
| Interac | `.interac` |

使用 `PKPaymentRequest.availableNetworks()` 在运行时查询可用网络。

## 显示支付表单

使用 `PKPaymentAuthorizationController`（在 SwiftUI 和 UIKit 中都有效，无需视图控制器）。控制器的代理是弱引用的，因此请在表单的生命周期中保留控制器。

```swift
final class CheckoutCoordinator: NSObject {
    private var paymentController: PKPaymentAuthorizationController?

    @MainActor
    func startPayment() {
        let controller = PKPaymentAuthorizationController(
            paymentRequest: createPaymentRequest()
        )
        paymentController = controller
        controller.delegate = self
        controller.present { [weak self] presented in
            if !presented {
                self?.paymentController = nil
            }
        }
    }
}
```

## 处理支付授权

实现 `PKPaymentAuthorizationControllerDelegate` 以处理支付令牌。

```swift
extension CheckoutCoordinator: PKPaymentAuthorizationControllerDelegate {
    func paymentAuthorizationController(
        _ controller: PKPaymentAuthorizationController,
        didAuthorizePayment payment: PKPayment,
        handler completion: @escaping (PKPaymentAuthorizationResult) -> Void
    ) {
        // 将 payment.token.paymentData 发送到您的支付处理器
        Task {
            do {
                try await paymentService.process(payment.token)
                completion(PKPaymentAuthorizationResult(status: .success, errors: nil))
            } catch {
                completion(PKPaymentAuthorizationResult(status: .failure, errors: [error]))
            }
        }
    }

    func paymentAuthorizationControllerDidFinish(
        _ controller: PKPaymentAuthorizationController
    ) {
        controller.dismiss { [weak self] in
            self?.paymentController = nil
        }
    }
}
```

### 处理运输变更

```swift
func paymentAuthorizationController(
    _ controller: PKPaymentAuthorizationController,
    didSelectShippingMethod shippingMethod: PKShippingMethod,
    handler completion: @escaping (PKPaymentRequestShippingMethodUpdate) -> Void
) {
    let updatedItems = recalculateItems(with: shippingMethod)
    let update = PKPaymentRequestShippingMethodUpdate(paymentSummaryItems: updatedItems)
    completion(update)
}
```

## 钱包通行证

### 将通行证添加到钱包

加载已签名的 `.pkpass` 数据，验证设备可以添加通行证，然后在您希望用户在添加通行证之前查看通行证时，显示 `PKAddPassesViewController`。`PKPass(data:)` 期望已签名的通行证数据，并且可能会抛出无效数据或无效签名错误。在审查指南中明确命名 `invalid-data` 和 `invalid-signature` 失败，而不是在裸 `try?` 后面隐藏它们。

```swift
func addPassToWallet(data: Data) {
    guard PKAddPassesViewController.canAddPasses() else {
        return
    }

    do {
        let pass = try PKPass(data: data)
        guard let addController = PKAddPassesViewController(pass: pass) else {
            return
        }
        addController.delegate = self
        present(addController, animated: true)
    } catch {
        // 已签名的通行证数据无效或签名无法验证。
        showRecoverablePassError(error)
    }
}
```

### SwiftUI 钱包按钮

使用 `AddPassToWalletButton` 作为 SwiftUI 中 `PKAddPassButton` 的等效项。

```swift
import PassKit
import SwiftUI

struct AddPassButton: View {
    let passData: Data
    @State private var addedToWallet = false

    var body: some View {
        if PKAddPassesViewController.canAddPasses(),
           let pass = try? PKPass(data: passData) {
            AddPassToWalletButton([pass]) { added in
                addedToWallet = added
            }
            .addPassToWalletButtonStyle(.blackOutline)
            .frame(width: 250, height: 50)
        }
    }
}
```

## 检查通行证库

使用 `PKPassLibrary` 检查和管理用户已经拥有的通行证。在执行通行证库操作之前，检查 `PKPassLibrary.isPassLibraryAvailable()`，但使用 `PKAddPassesViewController.canAddPasses()` 来决定设备是否可以添加通行证。`passes()` 只返回您的应用程序可以通过其权限访问的通行证。当替换现有通行证时，检查 `replacePass(with:)` 的布尔结果并处理失败。对于已签名的通行证捆绑包构建、更新网络服务以及 `replacePass(with:)`，请参阅 [参考资料/wallet-passes.md](references/wallet-passes.md)。

```swift
let library = PKPassLibrary()

// 检查特定的通行证是否已在钱包中
let hasPass = library.containsPass(pass)

// 获取您的应用程序可以访问的通行证
let passes = library.passes()

// 检查通行证库是否可用
guard PKPassLibrary.isPassLibraryAvailable() else { return }
```

## 常见错误

### 不要：使用 StoreKit 支付实体商品

Apple Pay (PassKit) 用于 **实体商品、现实世界服务、捐赠和符合条件的周期性付款**。StoreKit 用于虚拟商品、应用程序功能和数字内容订阅。使用错误的框架会导致 App Review 拒绝。

### 不要：在多个地方硬编码商家 ID

```swift
// 错误：商家 ID 分散在整个代码库中
let request1 = PKPaymentRequest()
request1.merchantIdentifier = "merchant.com.example.app"
// ...其他地方：
let request2 = PKPaymentRequest()
request2.merchantIdentifier = "merchant.com.example.app" // 容易失去同步

// 正确：集中配置
enum PaymentConfig {
    static let merchantIdentifier = "merchant.com.example.app"
    static let countryCode = "US"
    static let currencyCode = "USD"
    static let supportedNetworks: [PKPaymentNetwork] = [.visa, .masterCard, .amex]
}
```

## 审查清单

- [ ] 在 Developer portal 中启用 Apple Pay 功能并配置商家 ID
- [ ] 生成并安装支付处理证书
- [ ] 在显示 Apple Pay 按钮之前检查 `canMakePayments(usingNetworks:)`
- [ ] 在检查活动卡可用性的地方，Apple Pay 是显眼的
- [ ] 在支付表单之前收集产品选择、可选详情和复杂的运输选择
- [ ] `paymentSummaryItems` 中的最后一个项目是总计，带有商家显示名称
- [ ] 支付摘要和令牌上下文金额使用 `NSDecimalNumber`
- [ ] 支付令牌发送到服务器进行处理（客户端永不解码）
- [ ] 在显示时保留 `PKPaymentAuthorizationController`，在完成时清除
- [ ] `paymentAuthorizationControllerDidFinish` 关闭控制器
- [ ] 运输方法变更通过委托回调重新计算总计
- [ ] StoreKit 用于虚拟商品/数字内容；Apple Pay 用于实体商品、服务、捐赠和符合条件的周期性付款
- [ ] 钱包通行证从已签名的 `.pkpass` 捆绑包加载
- [ ] `PKPass(data:)` 无效数据和无效签名失败被显示
- [ ] 使用 `PKPassLibrary.isPassLibraryAvailable()` 进行通行证操作，而不是添加通行证的能力
- [ ] 在添加通行证 UI 之前检查 `PKAddPassesViewController.canAddPasses()` 
- [ ] 替换通行证时检查 `PKPassLibrary.replacePass(with:)` 的布尔结果
- [ ] Apple Pay 按钮使用系统提供的 `PKPaymentButton` 或 `PayWithApplePayButton`
- [ ] 添加到钱包 UI 使用系统提供的 `PKAddPassButton`、`AddPassToWalletButton` 或 `PKAddPassesViewController`
- [ ] 在授权结果中处理错误状态（网络故障、被拒绝的卡）

## 参考资料

- 扩展模式（周期性/延迟付款、优惠券代码、多商家、通行证捆绑包、通行证更新）：[参考资料/wallet-passes.md](references/wallet-passes.md)
- [PassKit 框架](https://sosumi.ai/documentation/passkit)
- [PKPaymentRequest](https://sosumi.ai/documentation/passkit/pkpaymentrequest)
- [PKPaymentAuthorizationController](https://sosumi.ai/documentation/passkit/pkpaymentauthorizationcontroller)
- [PKPaymentButton](https://sosumi.ai/documentation/passkit/pkpaymentbutton)
- [PayWithApplePayButton](https://sosumi.ai/documentation/passkit/paywithapplepaybutton)
- [AddPassToWalletButton](https://sosumi.ai/documentation/passkit/addpasstowalletbutton)
- [PKPass](https://sosumi.ai/documentation/passkit/pkpass)
- [PKAddPassesViewController](https://sosumi.ai/documentation/passkit/pkaddpassesviewcontroller)
- [PKPassLibrary](https://sosumi.ai/documentation/passkit/pkpasslibrary)
- [PKPaymentNetwork](https://sosumi.ai/documentation/passkit/pkpaymentnetwork)
- [Apple Pay HIG](https://sosumi.ai/design/human-interface-guidelines/apple-pay)
