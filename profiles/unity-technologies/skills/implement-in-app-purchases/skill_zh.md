# Unity 应用内购买

命名空间：`UnityEngine.Purchasing` | 安全性：`UnityEngine.Purchasing.Security`
包：`com.unity.purchasing`

**Unity IAP 有自己的初始化路径**，通过 `UnityIAPServices.StoreController()` → `store.Connect()`。它不需要 `UnityServices.InitializeAsync()`，但如果你的项目使用其他 UGS 服务，它们可以共存。如果存在分析功能并且调用了 `InitializeAsync()`，IAP 将自动发送交易事件。

## 开始之前

**始终先阅读 [参考资料/预检查.md](references/pre-check.md)。** 它会扫描项目中的第三方 IAP 包、原生 Google Billing 和现有的 Unity IAP 版本，然后路由到正确的路径。在路由解决之前，不要阅读任何其他参考资料文件或进行任何更改。

## 详细参考资料

- **项目扫描和路径路由（首先阅读）：** 查看 [参考资料/预检查.md](references/pre-check.md)
- **API 签名和代码示例：** 查看 [参考资料/api-notes.md](references/api-notes.md)
- **平台扩展（Apple、Google）：** 查看 [参考资料/platform-notes.md](references/platform-notes.md)
- **编辑 `IAPProductCatalog.json`（模式、十进制序列化、刷新）：** 查看 [参考资料/codeless-catalog.md](references/codeless-catalog.md)
- **v4 → v5 迁移：** 查看 [参考资料/migration-v4-to-v5.md](references/migration-v4-to-v5.md)
- **将原生 Google BillingClient 转换为 Unity IAP 5：** 查看 [参考资料/path-convert-native-google-billing.md](references/path-convert-native-google-billing.md)
- **将原生 iOS StoreKit 插件转换为 Unity IAP 5：** 查看 [参考资料/path-convert-native-storekit.md](references/path-convert-native-storekit.md)
- **将 Essential Kit 订阅转换为 Unity IAP 5：** 查看 [参考资料/convert-essentialkit.md](references/convert-essentialkit.md)
- **UniPay (FLOBUK) — 评估和指导：** 查看 [参考资料/convert-unipay.md](references/convert-unipay.md)
- **RevenueCat — 转换评估和指导：** 查看 [参考资料/convert-revenuecat.md](references/convert-revenuecat.md)
- **Adapty — 转换评估和指导：** 查看 [参考资料/convert-adapty.md](references/convert-adapty.md)
- **向没有现有 IAP 的项目添加 Unity IAP 5：** 查看 [参考资料/path-add-iap-to-new-project.md](references/path-add-iap-to-new-project.md)
- **实现 IAP D2C 功能（第三方支付提供者 — Stripe/Coda，需要 v5.4+）：** 查看 [参考资料/path-implement-iap-d2c.md](references/path-implement-iap-d2c.md)

按需阅读参考资料文件——只有在需要特定 API 签名、平台扩展详细信息或迁移映射时才阅读。

## 初始化流程

1. 通过 `UnityIAPServices.StoreController()` 获取 `StoreController`（或通过 `DefaultStore()`、`DefaultProduct()`、`DefaultPurchase()` 获取单个服务）
2. 在调用 `Connect()` **之前** 订阅**所有**所需事件（见下文所需事件订阅）
3. `await store.Connect()` 连接到平台商店
4. 在 `OnStoreConnected` 上，调用 `store.FetchProducts(List<ProductDefinition>)` 加载目录
5. 在 `OnProductsFetched` 上，产品准备好显示和购买

使用 `Awake()` 进行初始化——确保在其他的 `Start()` 方法之前 IAP 已准备就绪。

产品类型：`ProductType.Consumable`、`ProductType.NonConsumable`、`ProductType.Subscription`。

## 获取产品

将产品定义为 `List<ProductDefinition>` 并传递给 `store.FetchProducts()`。当产品 ID 在 Apple/Google 商店之间不同时，使用 `StoreSpecificIds`。对于复杂的目录，使用 `CatalogProvider` 来管理产品集和商店特定的 ID。

| 方法 | 行为 |
|---|---|
| `GetProducts()` | 返回**缓存的**产品列表（同步的，如果未调用 `FetchProducts` 则为过时） |
| `FetchProducts()` | 查询**商店**以获取最新的价格/可用性并更新缓存 |
| `GetProductById(id)` | 通过 ID 返回单个缓存的**产品** |

这些**不能**互换使用。始终在依赖 `GetProducts()` 之前调用 `FetchProducts()`。

## 两步购买流程

IAP v5 使用强制性的两步流程：**待处理 → 确认**。

1. `store.PurchaseProduct(product)` — 启动平台购买对话框
2. `OnPurchasePending` 触发——你收到一个 `PendingOrder`
3. 验证收据，向玩家授予内容
4. `store.ConfirmPurchase(pendingOrder)` — 完成交易
5. `OnPurchaseConfirmed` 触发——收到 `Order` 基类型；模式匹配 `ConfirmedOrder`（成功）与 `FailedOrder`（确认失败）

**在授予内容后，你必须调用 `ConfirmPurchase(pendingOrder)`。** 未确认的购买将在下次应用启动时重新交付，以防止丢失购买。

**去重：** `OnPurchasePending` 可能多次触发相同的购买（例如，在确认之前应用重新启动）。始终检查内容是否已授予。

**消耗品：** 确认的消耗品购买**不会**通过 `FetchPurchases` 返回。自己跟踪消耗品授予（例如，在 Cloud Save 或 Economy 中）。

**延迟购买：** `OnPurchaseDeferred` 触发 Ask-to-Buy（iOS）和 Google Play 延迟购买。不要授予内容——等待 `OnPurchasePending` 时批准。

## 恢复交易

`store.RestoreTransactions(callback)` 重新交付非消耗品和订阅购买。每个恢复的购买都会触发 `OnPurchasePending`。

在 iOS 上需要 Apple App Store 合规性——添加一个“恢复购买”按钮。

Apple 非续订订阅**不能**通过 `RestoreTransactions` 恢复。在服务器端跟踪这些。

## 收据验证

| 平台 | 方法 |
|---|---|
| **Google Play** | `CrossPlatformValidator` with `GooglePlayTangle.Data()` — 支持本地验证 |
| **Apple (StoreKit 2)** | 本地验证是**无操作**。使用 `order.Info.Apple?.jwsRepresentation` 进行服务器端验证 |

通过 Unity 编辑器中的 **Services > In-App Purchasing > Receipt Validation Obfuscator** 生成缠结数据。

## 授权检查

当你没有 `Order` 并想知道特定产品的状态时使用（替换 v4 的 `product.hasReceipt`）。如果你已经有了 `Order`，则检查其类型：`PendingOrder` 映射到 `EntitledUntilConsumed`（消耗品）或 `EntitledButNotFinished`（非消耗品/订阅），`ConfirmedOrder` 映射到 `FullyEntitled`。

调用 `store.CheckEntitlement(product)` 并处理 `store.OnCheckEntitlement`。检查 `entitlement.Status == EntitlementStatus.FullyEntitled`。

`EntitlementStatus` 值：`FullyEntitled`、`EntitledUntilConsumed`、`EntitledButNotFinished`、`NotEntitled`、`Unknown`。

## 获取现有购买

`store.FetchPurchases()` 从商店检索所有当前购买。在应用启动时很有用。

| 方法 | 行为 |
|---|---|
| `GetPurchases()` | 返回**缓存的**购买列表 |
| `FetchPurchases()` | 查询**商店**以获取当前购买并**覆盖**缓存的列表 |

`FetchPurchases()` 每次调用都会替换整个缓存的列表。仅重新获取非消耗品和订阅——确认的消耗品不会返回（见上文两步购买流程）。

## 订阅信息

订阅信息在 `IPurchasedProductInfo` 上，通过 `order.Info.PurchasedProductInfo` 访问——**不在 `CartItem` 上**（`CartItem` 仅包含 `Product` 和 `Quantity`）。

`IsSubscribed()` 返回 `Result` 枚举（`True`/`False`/`Unsupported`），**不是** `bool`。使用 `== Result.True` 进行空安全比较。

## 所需事件订阅

**始终订阅成功和失败事件。** 不订阅失败事件会生成运行时警告。

| 调用 | 成功事件 | 失败事件（必需） |
|---|---|---|
| `FetchProducts()` | `OnProductsFetched` | `OnProductsFetchFailed` |
| `FetchPurchases()` | `OnPurchasesFetched` | `OnPurchasesFetchFailed` |
| `Connect()` | `OnStoreConnected` | `OnStoreDisconnected` |
| `PurchaseProduct()` | `OnPurchasePending` | `OnPurchaseFailed` |
| `CheckEntitlement()` | `OnCheckEntitlement` | — |

**始终订阅 `OnPurchaseDeferred`**——触发 Ask-to-Buy（iOS）和 Google Play 延迟购买。不订阅会静默丢弃延迟购买。

在调用 `Connect()` **之前** 订阅事件——来自先前会话的待处理购买可能会立即触发。

## 失败描述属性名称

这些属性名称**不能**互换使用——使用错误会导致 CS1061：

| 类型 | 字段 | 属性 | 不 |
|---|---|---|---|
| `StoreConnectionFailureDescription` | `.message` | `.Message` | ~~`.reason`~~ |
| `ProductFetchFailed` | — | `.FailureReason`, `.FailedFetchProducts` | ~~`.Message`~~ |
| `FailedOrder` | — | `.FailureReason`, `.Details` | — |
| `PurchasesFetchFailureDescription` | `.message`, `.failureReason` | `.Message`, `.FailureReason` | — |

## 验证

在编写使用此包的代码后：
1. 验证项目能否无错误地编译。
2. 确认所有 API 调用与 [api-notes.md](references/api-notes.md) 中的 v5 签名匹配——**不要**使用 v4 遗留模式（`IStoreListener`、`UnityPurchasing.Initialize`、`ConfigurationBuilder`）。
3. 检查 api-notes.md 中的“抗幻觉：常见 v5 错误”表——**不要**使用 `OnStoreConnectionFailed`（使用 `OnStoreDisconnected`）、**不要**将回调传递给 `FetchProducts`/`FetchPurchases`（使用事件）、**不要**使用 `product.receipt`（使用 `order.Info.Receipt`）。
4. 确认在调用 `Connect()` **之前** 订阅了所有所需事件（见上表所需事件订阅）。
5. 验证两步购买流程：`OnPurchasePending` → 授予内容 → `ConfirmPurchase(pendingOrder)`。
6. 确认每个异步操作（`OnProductsFetched`/`OnProductsFetchFailed`、`OnStoreConnected`/`OnStoreDisconnected` 等）都订阅了成功和失败事件。
7. 如果处理订阅，验证 `IsSubscribed()` 与 `== Result.True` 比较，而不是转换为 `bool`。
8. 如果同一项目中同时存在更新文件和遗留版本，使用唯一命名空间（例如，添加 `.Updated` 后缀）以避免 CS0101/CS0111 编译错误。
9. 如果项目订阅了 `OnAuthAccountChanged`（v5.4+）：验证处理程序从零开始重新获取产品和购买——Unity IAP 在触发此事件之前会清除两个缓存。在处理程序内**不要**读取 `GetProducts()` 或 `GetPurchases()`。
