---
name: connector-quickbooks
description: 每次用户要求容器在 QuickBooks Online (QBO) 中创建/读取/更新发票、客户、付款、项目或总账条目，发送发票电子邮件或运行 QuickBooks 查询时，请使用 `quickbooks-client` mops 包。该包通过出站 HTTPS 调用封装了位于 `https://quickbooks.api.intuit.com` 的 QuickBooks 在线会计 API v3。
---

# quickbooks-client

QuickBooks 在线会计 API v3（[QuickBooks Online Accounting API
v3](https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/account)）的 Motoko 绑定，包含经过筛选的 API 功能：**客户、发票、付款、项目、账户**。模式是从 Intuit 的官方 XSD 中转录的。所有 12 个操作都位于 `Apis/DefaultApi.mo` 中：
`saveCustomer`/`getCustomer`，`saveItem`/`getItem`，`saveAccount`/`getAccount`，`saveInvoice`/`getInvoice`/`sendInvoice`，`savePayment`/`getPayment`，以及 `query_`（尾随下划线 — `query` 是 Motoko 中的保留字）。

## 触发短语

在任何提及以下内容的请求中都使用此技能：QuickBooks、QBO、发票、向客户开账单、"发送发票"、"记录/接收付款"、"客户"、"会计"、"簿记"、"账户科目表"、"项目/产品/服务"、"与 QuickBooks 同步"。

**不在此范围内**：估算、账单、供应商、采购订单、贷项通知单和 QBO 实体集的其余部分 — 规范是手动筛选的，仅包含客户、发票、付款、项目和账户。如果请求需要其他功能，请直接说明，而不是将其映射到发票上；规范必须首先从 Intuit 的 XSD 中重新生成。

## QuickBooks 身份验证的工作原理（接线前阅读）

QBO 使用 **OAuth 2.0 授权码** — 没有静态 API 密钥。每个最终用户授权他们的 QuickBooks 公司；应用程序交换授权码以获取短期有效的 **访问令牌**（约 1 小时），并在调用时将其传递给客户端。在过期时，API 返回 HTTP 401 — 显示 `#Err("auth_expired")` 结果并离链重新验证。

每个调用都携带两个标识符：
- **`realmId`** — QuickBooks *公司 ID*，在 OAuth 握手期间获得。它是每个操作的第一个参数。
- **`minorversion`** — API 小版本（默认 `"75"`）；传递 `""` 以省略并使用账户默认值。

**令牌交换本身是一个链下调用**到 Intuit 的令牌端点，并需要应用程序的 **客户端密钥**。两个风险（与 googlemail 连接器相同）：
- **在交换时 `is_replicated = ?false`** — 令牌响应是非确定性的，因此复制的交换会在约 13 个副本中重复，并导致 IC 共识失败。
- **客户端密钥随导出的源代码泄漏** — Caffeine 可以将应用程序导出为 `.zip` 或公共 GitHub 存储库，并携带密钥。最小化作用域并在共享源代码时旋转。

跨升级持久化每个用户的刷新/会话令牌（稳定内存），以便重新部署不会强制重新验证。OAuth 作用域：`com.intuit.quickbooks.accounting`。

## 创建与更新与删除（重要的 QBO 语义）

- **创建和更新都使用 `save<Entity>` (POST) 操作。** 当正文包含实体的 `Id` **并且**当前 `SyncToken`（首先通过 `get<Entity>` 获取）时，它是 *更新*。设置 `sparse = ?true` 以进行部分更新。没有 `Id`/`SyncToken` 时，它是创建。
- **删除**（仅适用于交易 — `Invoice`，`Payment`）：调用 `saveInvoice` / `savePayment` 并设置 `operation = ?#delete` 以及包含 `Id` + `SyncToken` 的正文。`operation` 参数是 **可选的** (`?SaveInvoiceOperationParameter`)，不是裸变体。传递 **`null` 以进行正常创建或更新** — 客户端然后完全省略查询参数，这是 QBO 所需要的；规范说 "创建/更新时省略；'delete' 删除发票"。通常只需要 `?#delete`。名称列表实体
  (`Customer`，`Item`，`Account`) 是 **不可删除的** — 设置 `Active = ?false` 以停用（它们的 `save*` 操作不接受 `operation` 参数）。
- **响应被包装**：`getCustomer` 返回 `CustomerResponse`，其中包含 `Customer` 字段（以及 `time`）；每个实体形状相同。`query_` 返回 `QueryResponse`，其 `QueryResponse` 字段按实体类型包含数组。操作是 `query_`，不是 `query`。
- **发票行和付款行是不同类型。** `Invoice.Line` 是 `[Line]`，其中 `DetailType` 是 **必需的**。`Payment.Line` 是 `[PaymentLine]` — `{Amount, LinkedTxn, …}`，**没有** `DetailType`，这是 Intuit 在付款应用于发票时实际发送的。它们在 0.2.0 之前是同一个共享类型，这导致每个付款响应都无法解码。

## 前端界面（两个页面）

像任何每个用户的 OAuth 连接器一样，应用程序需要 **两个** 界面：
- 一个 **由管理员授权的 Intuit 应用程序配置页面** — **客户端 ID** 和
  **客户端密钥**是全局可用的，由管理员设置一次；永远不要将客户端密钥暴露给普通用户。
- 一个 **每个用户的 OAuth 2.0 握手页面** — 每个用户连接他们自己的
  QuickBooks 公司（获得他们的 `realmId` + 令牌）；在 HTTP 401 时重新提示。

## 使用方法

```mo:quickbooks-client
import { saveInvoice; getInvoice; sendInvoice; saveCustomer }
  "mo:quickbooks-client/Apis/DefaultApi";
import Invoice "mo:quickbooks-client/Models/Invoice";
import { defaultConfig } "mo:quickbooks-client/Config";

let cfg = {
  defaultConfig with
    auth          = ?#bearer "<off-chain OAuth2 access token>";
    is_replicated = ?false;  // non-replicated: required for writes; reads too
};
let realmId = "<company id from OAuth handshake>";

// 构建一个发票：一条销售行，$100，项目 "1"，开给客户 "58"。
// 发票没有必填字段 → 初始化 {} 然后记录更新可选字段。
// 注意：DetailType 在行上是必需的，并且其变体是小写的。
let inv = {
  Invoice.init {} with
    CustomerRef = ?{ value = "58"; name = null };
    Line = ?[ {
      DetailType          = #salesitemlinedetail;   // required; lowercase variant
      Amount              = ?100.0;
      Description         = ?"Consulting";
      SalesItemLineDetail = ?{ ItemRef = ?{ value = "1"; name = null };
                               Qty = ?1.0; UnitPrice = ?100.0; TaxCodeRef = null; ServiceDate = null };
      Id = null; LineNum = null; LinkedTxn = null;
    } ];
};
// saveInvoice(config, realmId, invoice, minorversion, operation)
// `operation` 是可选的：null 省略它 — 创建/更新路径。
let created = await* saveInvoice(cfg, realmId, inv, "75", null);
// 将其发送给客户（config, realmId, invoiceId, sendTo, minorversion）：
// ignore await* sendInvoice(cfg, realmId, "<invoiceId>", "cust@example.com", "75");
```

## 注意事项

- **对于写入使用 `is_replicated = ?false`** (`save*`，`sendInvoice`，通过 `operation = ?#delete` 删除）。这些出调用是非幂等的，QBO 的响应是非确定性的；在复制模式下，每个副本都会发出请求 — 创建重复的发票/付款并导致 IC 共识失败。读取 (`get*`，`query_`) 也使用 `?false`（一个节点，约 13× 更便宜）。
- **更新需要一个新鲜的 `SyncToken`** — 总是先 `get<Entity>`，将它的 `SyncToken` 复制到正文，然后 `save<Entity>`。陈旧的令牌 → HTTP 400 ("stale object")。
- `minorversion` 默认为 `"75"`；传递 `""` 以省略。
- QBO 将错误作为 `ErrorResponse` 返回，其列表字段是 `Fault.Error_` — 注意尾随下划线，`Error` 是保留的 — 所以将 `Fault.Error_[0].Message` 显示给调用者；永远不要盲目重试写入。
- 沙盒与生产：将客户端主机指向 `sandbox-quickbooks.api.intuit.com` 以在开发期间使用 Intuit 沙盒公司（编辑 `Config` 中的服务器），并将 `quickbooks.api.intuit.com` 用于生产。
