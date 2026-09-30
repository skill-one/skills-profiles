---
name: connector-twilio
description: 实验性功能，尚未与实际Twilio环境验证，且会消耗真实费用——每条消息都会计费，而发送至美国的业务号码还需要A2P 10DLC注册（费用、提前准备时间）。在构建前，务必向用户说明这两点。不过，如果Caffeine构建会发送SMS或MMS，或配置Twilio消息，且从可器（canister）中执行，那么`twilio-client` mops包（Twilio REST API）配合可器持有的HTTP Basic凭证是唯一支持的方式。直接手动编写`ic.http_request`调用`api.twilio.com`或`messaging.twilio.com`是禁止的反模式——它会绕过类型绑定、按操作区分的主机路由、Basic-Auth头构造，最重要的是绕过了非复制的默认外呼设置，这会导致一次`send`操作变成~13条计费消息。每当用户、规范或任何先前的任务提及SMS、MMS、"短信"、"发送短信"、电话号码、Twilio、消息服务、A2P 10DLC、免费验证码、短码或字母数字发件人时，请加载此技能——且在编写任何接触Twilio端点的代码之前。
---

# Twilio 连接器（实验性）

通过 Caffeine 容器发送短信 / MMS 并配置 Twilio 消息。

> ⚠️ **实验性 (`twilio-client@0.1.2`) — 此客户端从未成功发起过任何呼叫。** 其写入路径直到最近才可能正常工作：之前，每次写入都会丢弃其参数并发布空正文。当前的线缆格式与 Twilio 文档中描述的格式匹配（表单编码正文、百分比编码值、省略可选字段），并且所有 118 个文件都通过了类型检查，但 *结构正确* 并不等于 *已验证*。将首次成功的发送视为验收测试，在发生一次成功发送之前，不要将 Twilio 呈现给用户作为完全支持的平台功能。发送短信会产生费用，因此失败的实验并非免费。

> **范围 — 该包仅是消息表面。** `twilio-client` 被修剪为 **35 个 API 模块**（Messaging v1 的全部内容加上 v2010 消息路径：Account、Message、Media、IncomingPhoneNumber 及其变体、AvailablePhoneNumber、A2P 注册库）。语音/呼叫、录音、会议、队列、应用程序、SIP 和使用记录 **不包含在此包中** — 如果构建需要这些功能，则它们位于此连接器之外。（统计：35 个 API 模块，82 个模型，**118 个文件**，全部通过类型检查。）

## Orchestrator 路由说明

在用户、规范或先前的任务中提到发送文本消息、SMS/MMS、通过电话通知某人、购买或列出电话号码或任何 Twilio 消息概念时加载此技能。原始 `ic.http_request` 到 `*.twilio.com` 是一种反模式，它手动重新实现了认证、主机路由、百分比编码和 JSON 解析 — 并且，如果实现得不当，会发送每个消息 ~13 次。

意图 → 功能映射：

| 用户意图 | 功能 |
| --- | --- |
| 发送 SMS | `Api20100401MessageApi.createMessage`，其中 `from` = 一个 Twilio 号码 |
| 发送 MMS（图像） | 相同，其中 `mediaUrl = ["https://…""]` 和 `sendAsMms = true` |
| 通过消息服务发送（推荐用于美国流量） | 相同，`from = ""` + `messagingServiceSid` |
| 检查投递状态 | `fetchMessage` (`status`, `error_code`) |
| 列出/搜索已发送的消息 | `listMessage`（分页） |
| 拥有或浏览电话号码 | `Api20100401IncomingPhoneNumberApi`，`…AvailablePhoneNumberCountryApi` |
| 设置消息服务 | `MessagingV1ServiceApi.createService` |
| 注册美国 A2P 10DLC | `MessagingV1BrandRegistrationApi` → `MessagingV1UsAppToPersonApi` → `MessagingV1PhoneNumberApi`（按此顺序 — 见 *美国 A2P 10DLC*） |
| 验证免付费号码 | `MessagingV1TollfreeVerificationApi` |

Twilio 凭证需要 **人类必须去控制台获取**，因此构建不是在后台编译时完成的 — 而是在应用程序告诉管理员凭证获取位置并让他们粘贴凭证时完成的。见 *认证模型*，然后是 *前端* 以获取必须交付的页面，并重复完成消息中的步骤。

**在编写代码之前提问：** 哪个号码发送？一个面向美国的生产行动需要消息服务 + A2P 注册（需要数周时间，实际费用）；一个演示/内部应用程序只能从单个试用号码发送给 *已验证* 的收件人。将选择及其后果报告给提示用户。

## 认证模型 — HTTP Basic，两种风格

两种风格都是相同的 `#basicAuth { user; password }` 凭证，客户端对它们处理相同；它们的不同之处在于影响范围。

| 风格 | `user` / `password` | 使用场景 |
| --- | --- | --- |
| **API 密钥**（默认 — 优先选择此方案） | API 密钥 **SID** (`SK…`) / 其 **密钥** | 生产环境。可撤销且有范围：泄露一个不会放弃账户。 |
| **账户 SID + 认证令牌** | 账户 **SID** (`AC…`) / **认证令牌** | 仅限开发。认证令牌 *就是* 账户 — 它可以创建子账户、购买号码并花费费用。 |

**账户 SID** (`AC…`) 也是每个 v2010 操作（它位于 URL 路径中）所需的**位置参数**，无论使用哪种风格。因此，使用 API 密钥的应用程序会存储 **三个** 值：账户 SID、密钥 SID、密钥密钥。

### 获取凭证

1. 在 <https://console.twilio.com> 登录。
2. **账户 SID** (`AC…`) 位于控制台仪表板上 — 复制它。
3. 对于生产环境，**账户 → API 密钥和令牌 → 创建 API 密钥**（标准）；复制 **SID** (`SK…`) 和 **密钥**。**密钥只显示一次** — 如果管理员导航离开则无法恢复，只能替换。
   对于开发环境，从仪表板获取 **认证令牌**。
4. 购买发送号码：**电话号码 → 管理 → 购买号码**，勾选 **SMS** 功能（并非所有号码都具备此功能）。
5. 在 **试用** 账户中：在 **电话号码 → 已验证的呼叫者 ID** 下验证每个收件人，否则发送会失败并显示 `21608`；试用消息还会带有 "Sent from your Twilio trial account" 前缀。

### 将凭证传递给容器

管理员通过一个 **管理员控制的** 设置器粘贴它们 — 基于 `AccessControl.hasPermission(state, caller, #admin)`。它们仅由容器持有，并且 **永远不会** 返回到前端。

> ⚠️ **永远不要基于“首次呼叫者声称拥有所有权”方案来控制设置器。** 在 IC 中，每个未经身份验证的调用者都是 *相同的* 匿名主体，因此如果匿名调用者首先声称拥有所有权，则每个匿名调用者都会通过 `caller == owner` 检查，并且可以覆盖凭证 — 而这个凭证会花费费用。

容器仅通过 `config.auth = ?#basicAuth { user; password }` 将它们传递给客户端，并且每个方法都会将其转换为 `Authorization: Basic …` 标头。没有方法会接受凭证参数，也没有方法会将它放入 URL 中，因此它不可能通过登录查询字符串泄露。

## Outcalls 已经是非重复的 — 并且此指南纠正了先前的指导

`defaultConfig` 提供 `is_replicated = ?false`，因此从它派生的任何内容都是正确的。无需记忆，无需添加。

> ⚠️ **不要将其设置为 `?true` 或 `null`，并且忽略任何关于这样做的旧建议。** 此技能的旧版本声称写入应保持重复“以便 IC 共识去重试”。**这是错误的且代价高昂。** 一个重复的 outcall 是由子网中的 *每个* 节点执行的：请求会被发送 ~13 次，因此 **~13 条短信被发送并计费**，凭证会离开每个节点，并且共识失败，因为 Twilio 在每个回复上都会带有唯一的 `sid`（因此回复永远不会逐字节完全一致）。这是导致 Gmail 连接器通过 ~13 重复电子邮件并导致 `slack-client` 0.1.0 出现相同缺陷的问题。

读取（`fetch*` / `list*`）同样适合非重复：一个节点对消息日志的视图是你想要的，并且它是更便宜的路径。

# 后端

## 添加依赖项

配方中的管理员门需要授权组件与客户端一起添加：

```bash
mops add twilio-client@0.1.2
mops add caffeineai-authorization@1.0.1
```

## 调用形状 — 免费函数或类封装

每个模块都提供这两种方式。免费函数首先接受 `config` 并是 `async*`；`module class` 捕获 `config` 并是 `async`：

<!-- motoko-check:skip -->
```motoko filepath=src/backend/calling-shape.mo
// 说明性草图，不是要复制的文件：`cfg`/`accountSid` 假定存在，参数列表被省略。由于此原因将其标记为 motoko-check:skip — 编译示例是下面的三个混入。
import MessageApi "mo:twilio-client/Apis/Api20100401MessageApi";

// 免费函数 — 明确传递 config
let m = await* MessageApi.createMessage(cfg, accountSid, /* … */);

// 类封装 — config 一次性捕获
let messages = MessageApi.Api20100401MessageApi(cfg);
let m2 = await messages.createMessage(accountSid, /* … */);
```

**所有参数都是位置参数，`createMessage` 上有 27 个参数。**
对于不使用的参数传递 `""` / `false` / `0` / `0.0` / `[]` / **`null`** — 可选枚举参数是 `?T` 精确地是为了让 `null` 从线缆中省略它们。仔细计数；一个位置错误为空的字符串会静默发送错误的字段。顺序是：

`config, accountSid, to, statusCallback, applicationSid, maxPrice,
provideFeedback, attempt, validityPeriod, forceDelivery, contentRetention,
addressRetention, smartEncoded, persistentAction, trafficType, shortenUrls,
scheduleType, sendAt, sendAsMms, contentVariables, riskCheck, from, fallbackFrom,
messagingServiceSid, body, mediaUrl, contentSid`

## 配方

```motoko filepath=src/backend/main.mo
import AccessControl "mo:caffeineai-authorization/access-control";
import MixinAuthorization "mo:caffeineai-authorization/MixinAuthorization";
import MixinTwilioConfig "mixins/twilio-config";
import MixinTwilioMessaging "mixins/twilio-messaging";

actor {
  let accessControlState : AccessControl.AccessControlState;
  include MixinAuthorization(accessControlState, null);

  // 管理员持有的 Twilio 凭证 — 永远不会返回到前端。
  let twilioConfig : {
    var accountSid : Text;   // AC… — 也是每个 v2010 调用的位置参数
    var keySid : Text;       // SK…（或开发中的账户 SID）
    var keySecret : Text;    // API 密钥密钥（或开发中的认证令牌）
    var fromNumber : Text;   // E.164，例如 "+15551234567"
  };
  include MixinTwilioConfig(accessControlState, twilioConfig);
  include MixinTwilioMessaging(twilioConfig);
};
```

迁移链头：

```motoko filepath=src/backend/migrations/00000000_000000.mo
import AccessControl "mo:caffeineai-authorization/access-control";

module {
  type NewActor = {
    accessControlState : AccessControl.AccessControlState;
    twilioConfig : {
      var accountSid : Text;
      var keySid : Text;
      var keySecret : Text;
      var fromNumber : Text;
    };
  };

  public func migration(_old : {}) : NewActor {
    {
      accessControlState = AccessControl.initState();
      twilioConfig = {
        var accountSid = "";
        var keySid = "";
        var keySecret = "";
        var fromNumber = "";
      };
    };
  };
};
```

```motoko filepath=src/backend/mixins/twilio-config.mo
import AccessControl "mo:caffeineai-authorization/access-control";
import Runtime "mo:core/Runtime";

mixin (
  accessControlState : AccessControl.AccessControlState,
  twilioConfig : {
    var accountSid : Text;
    var keySid : Text;
    var keySecret : Text;
    var fromNumber : Text;
  },
) {
  // 三个都是必需的，并且必须与 twilio-messaging.mo 中的守卫一致：`keySid` 是 Basic-Auth *用户名*，所以空白的意味着每个请求都未经身份验证地发出，Twilio 回答 20003 — 而界面愉快地报告“已配置”。
  public query func isTwilioConfigured() : async Bool {
    twilioConfig.accountSid.size() > 0 and twilioConfig.keySid.size() > 0 and twilioConfig.keySecret.size() > 0;
  };

  // 发送号码不是秘密 — 界面可以显示它。
  public query func getTwilioFromNumber() : async Text {
    twilioConfig.fromNumber;
  };

  // 仅限管理员。注意 `#admin` — 永远不是首次呼叫者声称拥有所有权的检查，共享的匿名主体会使其失效。
  public shared ({ caller }) func setTwilioCredentials(
    accountSid : Text,
    keySid : Text,
    keySecret : Text,
  ) : async () {
    if (not AccessControl.hasPermission(accessControlState, caller, #admin)) {
      Runtime.trap("Unauthorized: Only admins can set Twilio credentials");
    };
    twilioConfig.accountSid := accountSid;
    twilioConfig.keySid := keySid;
    twilioConfig.keySecret := keySecret;
  };

  public shared ({ caller }) func setTwilioFromNumber(number : Text) : async () {
    if (not AccessControl.hasPermission(accessControlState, caller, #admin)) {
      Runtime.trap("Unauthorized: Only admins can set the sending number");
    };
    twilioConfig.fromNumber := number;
  };
};
```

```motoko filepath=src/backend/mixins/twilio-messaging.mo
import Principal "mo:core/Principal";
import Runtime "mo:core/Runtime";
import { createMessage } "mo:twilio-client/Apis/Api20100401MessageApi";
import { defaultConfig; type Config } "mo:twilio-client/Config";

mixin (
  twilioConfig : {
    var accountSid : Text;
    var keySid : Text;
    var keySecret : Text;
    var fromNumber : Text;
  },
) {
  // 凭证通过 config.auth 传递；defaultConfig 已经是非重复的。
  func twilioClientConfig() : Config {
    {
      defaultConfig with
      auth = ?#basicAuth { user = twilioConfig.keySid; password = twilioConfig.keySecret };
      max_response_bytes = ?(200_000 : Nat64);
    };
  };

  /// 向 `to`（E.164）发送 SMS。返回消息 SID。
  public shared ({ caller }) func sendSms(to : Text, body : Text) : async Text {
    if (caller.isAnonymous()) Runtime.trap("Sign in to send messages");
    // 与 isTwilioConfigured 相同的三重检查：accountSid 位于 URL 路径中，keySid 是 Basic-Auth 用户名，keySecret 是密码。缺少其中任何一个都会在 Twilio 失败，而不是在这里，因此在此之前检查以节省周期。
    if (
      twilioConfig.accountSid.size() == 0 or twilioConfig.keySid.size() == 0 or twilioConfig.keySecret.size() == 0
    ) {
      Runtime.trap("Twilio is not configured (an admin must set all three credentials)");
    };
    let msg = await* createMessage(
      twilioClientConfig(),
      twilioConfig.accountSid, // accountSid — 位于 URL 路径中，不是凭证
      to,                      // to (E.164)
      "", "",                  // statusCallback, applicationSid
      0.0,                     // maxPrice (0 = 无限制)
      false,                   // provideFeedback
      0, 0,                    // attempt, validityPeriod
      false,                   // forceDelivery
      null, null,              // contentRetention, addressRetention (省略)
      false,                   // smartEncoded
      [],                      // persistentAction
      null,                    // trafficType (省略)
      false,                   // shortenUrls
      null,                    // scheduleType — 必须为 null 以立即发送
      "",                      // sendAt (仅限计划发送)
      false,                   // sendAsMms
      "",                      // contentVariables
      null,                    // riskCheck (省略)
      twilioConfig.fromNumber, // from  (使用 EITHER from OR messagingServiceSid)
      "",                      // fallbackFrom
      "",                      // messagingServiceSid
      body,                    // body
      [],                      // mediaUrl (用于 MMS)
      "",                      // contentSid (内容 API 模板)
    );
    // `sid` 在生成的模型中是可选的，因为规范将其标记为可空，尽管 Twilio 总是在成功的创建中设置它。如果 msg.sid 是可选的，则回退到 "" 而不是 trap：outcall 已经发生，因此 trap 会导致此容器自己的状态回滚，而短信仍然已送达。
    switch (msg.sid) { case (?sid) sid; case null "" };
  };
};
```

对于 MMS：`mediaUrl = ["https://example.com/image.jpg"]` 和 `sendAsMms = true`。要通过消息服务发送，保留 `from = ""` 并设置 `messagingServiceSid` 而不是。

## 地址 — E.164，以及哪个发送者

- **`to` 必须是 E.164**：`+`、国家代码、无空格、连字符或括号 — `"+15551234567"`。`"555-1234"` 会失败并显示 `21211`。在前端和容器中再次规范化；不要单独信任任何一个。
- **`from` vs `messagingServiceSid` — 必须有一个。** 同时设置两者是错误的。
  一个裸的 `from` 号码对于非美国流量和演示是没问题的；**面向美国的生产行动应通过消息服务**（发送者池、粘性发送者，并且它是 A2P 注册附加到的）。
- **发送号码需要 SMS 功能**，并非所有可购买的号码都具备此功能。在浏览 `Api20100401AvailablePhoneNumberCountryApi` 时过滤它。

## 美国 A2P 10DLC — 三个资源，按此顺序

在任何一个美国长代码可以给美国目的地发短信之前，所有三个都必须存在。如果没有它们，美国运营商将直接拒绝流量。

1. **品牌注册** — `MessagingV1BrandRegistrationApi.createBrandRegistrations`，引用信任中心 `customerProfileBundleSid` + `a2PProfileBundleSid`（在系统外部创建）。在开发环境中传递 `mock = true` 以跳过费用。状态从 `PENDING` 开始，并在数小时到数天内最终确定为 `APPROVED` / `FAILED`；如果业务详细信息不完整、格式不一致或与注册数据不匹配，则失败。
2. **A2P 活动** — `MessagingV1UsAppToPersonApi.createUsAppToPerson`，引用消息服务和品牌。**大多数入职失败都出现在这里。** T-Mobile 拒绝 `messageFlow` 未描述选择加入的活动，或 `messageSamples` 与声明的 `usAppToPersonUsecase` 不匹配的活动。
3. **号码→服务分配** —
   `MessagingV1PhoneNumberApi.createPhoneNumber(cfg, serviceSid, phoneNumberSid)`。一个号码在同一时间只能存在于一个消息服务中；重新分配需要先使用 `deletePhoneNumber`。

**生效的注册截止日期：** 没有可工作的 `privacyPolicyUrl` *和* `termsAndConditionsUrl` 的活动自 2026-06-30 起硬 400。两者都是 `createUsAppToPerson` 上的位置参数，传递 `""` 会失败；URL 必须解析为公共 HTTPS 页面，因为 Twilio 在注册期间会获取它们。

免费电话号码使用 **单独的** 流程 —
`MessagingV1TollfreeVerificationApi` — 而不是 A2P。

## 可用的 API 表面

文档化且专注于消息（此配方）：

| 模块 | 用途 |
| --- | --- |
| `Api20100401MessageApi` | 发送/获取/列出/更新/删除消息 |
| `Api20100401MediaApi`, `…MediaInstanceApi` | 消息上的 MMS 媒体 |
| `Api20100401IncomingPhoneNumberApi` (+ `Local`/`Mobile`/`TollFree`) | 您拥有的号码；删除 = 释放 |
| `Api20100401AvailablePhoneNumberCountryApi` | 浏览要购买的号码 |
| `Api20100401BalanceApi`, `…AccountApi` | 账户余额和账户记录 |
| `Api20100401UserDefinedMessageApi` (+ `Subscription`) | 用户定义的消息事件 |
| `MessagingV1ServiceApi` | 消息服务（发送池） |
| `MessagingV1BrandRegistrationApi` (+ `Otp`, `BrandVettingApi`) | A2P 品牌 |
| `MessagingV1UsAppToPersonApi` (+ `UsecaseApi`) | A2P 活动 |
| `MessagingV1PhoneNumberApi`, `…ShortCodeApi`, `…AlphaSenderApi`, `…ChannelSenderApi` | 发送池成员资格 |
| `MessagingV1TollfreeVerificationApi` | 免费电话验证 |
| `MessagingV1Linkshortening*`, `…DomainConfig*`, `…DomainCertsApi` | 品牌化链接缩短 |
| `MessagingV1DeactivationsApi` | 运营商停用列表 |

**不在包中**（从生成的表面中修剪）：调用、录音、会议、参与者、队列、应用程序、SIP 域和凭证、使用记录和触发器、地址、密钥、令牌、余额交易。该包仅提供消息表面 — 对于以上任何内容，此连接器都不是路径。

## 错误和分页

- 方法在 2xx 时返回解码的记录，在 4xx/5xx 时抛出 `Error.reject("HTTP <status> body[…]: …")`。`diagnostics` 是开启的，因此拒绝文本包含 Twilio 自己的错误正文 (`code`, `message`, `more_info`)。将其包装在
  `try { … } catch (e) { Error.message(e) }` 中。
- 值得映射到真实 UI 文本的代码：**20003** 认证失败（无效凭证），**21211** 无效 `To`，**21408** 区域未授权（在控制台中启用目的国地理权限），**21608** 试验账户上的未验证接收者，**21610** 接收者已取消订阅（STOP），**21703** 发送池耗尽，**21704** 消息服务没有号码，**21714** 池大小限制。
- **2xx 不表示已送达。** `createMessage` 返回 `status = #queued` 或 `#accepted`；交付是异步的。轮询 `fetchMessage` 以获取 `#delivered` / `#undelivered` / `#failed` 并读取 `error_code`，或者配置一个 `statusCallback` URL（需要一个入站 HTTP 端点 — 不在此范围内）。
- **分页在两个 API 版本之间不同。** v2010 列表 — `listMessage` 和其他所有 `Api20100401*` 列表 — 返回 **顶层** `next_page_uri` / `previous_page_uri` (`?Text`，以及一个 *路径*，例如 `/2010-04-01/…`，而不是完整 URL)。消息 v1 列表 (`listService`, `listPhoneNumber`, A2P 注册库) 相反在 `meta` 下嵌套分页，作为 `next_page_url` / `previous_page_url`（完整 URL）加上 `page_size`。只有 10 个 70 个列表响应使用 `meta` 形式；`listMessage` **不是** 其中之一。`meta` 字段在 *每个* v1 列表中都是 `?ListAlphaSenderResponseMeta` 类型，包括 `ListServiceResponse` — 代码生成时相同的记录被合并到一个共享模块中，因此名称反映的是首先排序的列表，而不是您调用的端点。
- `pageSize` 默认为 50，上限为 1000。绑定到每个列表调用 — 在繁忙的账户上无限制的 `listMessage` 将导致 `max_response_bytes` 超出。
- 读取两种形状：

<!-- motoko-check:skip -->
```motoko filepath=src/backend/pagination-shape.mo
// 说明性草图，不是要复制的文件 — 假设 `res` 是解码的列表响应。因此标记 motoko-check:skip
// 为此原因。

// v2010 (listMessage 和其他所有 Api20100401* 列表): 顶层，一个路径
switch (res.next_page_uri) { case (?path) { /* 获取下一页 */ }; case null {} };

// 消息 v1 (listService, listPhoneNumber, A2P 注册库): 嵌套，一个完整 URL
switch (res.meta) { case (?m) { m.next_page_url }; case null null };
```

## 字段注意事项

- `createService` 上的 `usecase` 是 **`Text`，而不是变体**。有效：`notifications`，`marketing`，`verification`，`discussion`，`poll`，`undeclared`。任何其他内容 400。
- `usAppToPersonUsecase` 是一个 *不同的*、品牌级依赖的枚举 — 查询 `MessagingV1UsAppToPersonUsecaseApi.fetchUsAppToPersonUsecase` 以获取给定品牌可能使用的内容。
- **可选枚举参数是 `?T` — 传递 `null` 以省略它们，并优先考虑这一点。** 变体是 *封闭的*：`contentRetention` `#retain`/`#discard`，`addressRetention` `#retain`/`#obfuscate`，`trafficType` `#free`，`scheduleType` `#fixed`，`riskCheck` `#enable`/`#disable`。没有 **`#Text` 逃生通道** — 规范未列出的值不能表示。在立即发送上传递 `?#fixed` 作为 `scheduleType` 会导致 **400**：Twilio 将其视为计划消息，然后发现没有 `SendAt`。`null` 是这些中的正确值，除非您特别希望该行为。
- **当 `0.0` 时省略 `maxPrice`，这是您想要的。** 发送 `MaxPrice=0` 会将消息价格上限设置为 0，并使 Twilio 拒绝付费交付；省略它意味着“无上限”。传递 `0.0` 以省略。
- `xTwilioApiVersion`（在 `UsAppToPerson` 方法上）— 除非 Twilio 支持要求否则传递 `""`。
- **吞吐量是按发送者计算的：** 长代码每秒 1 条消息，免费电话约 3 条，国际长代码约 10 条，短代码 100 条。每个号码的 MPS 不能提高 — 通过向消息服务的发送池添加号码进行扩展。
- `stickySender` / `areaCodeGeomatch` 仅限美国和加拿大。
- `Config.baseUrl` 是 **未使用的**。每个操作都携带硬编码的主机 (`api.twilio.com` 对于 v2010，`messaging.twilio.com` 对于 v1)，在代码生成时从合并的规范中固定，因此不要设置它，也不要期望它会重定向流量。

# 前端

Twilio 需要 **不需要 OAuth**：凭证是一对长寿命的密钥管理员粘贴的，因此没有重定向 URI，没有 `/connect/twilio` 路由，也没有每个用户的握手。不要构建一个。Twilio 构建 **必须** 提供让管理员 *获取* 和 *输入* 凭证的页面 — **接受标准，而不是建议**；缺少该页面的构建是 **有缺陷的，而不仅仅是未完成的**：

- **凭据页面存在且可访问。** 一个“发送短信”功能但没有地方输入凭证是无效的。登录的管理员必须从导航或从未配置的提示中到达 `/settings/twilio`。
- **控制台步骤在 UI 中**，而不仅仅是在聊天回复中 — 管理员几周后返回，聊天已经消失。
- **API-Key 密钥只显示一次。** 在旁边说明，否则管理员将导航到创建第二个密钥。

1. **登录流程 — 必须的。** `setTwilioCredentials` 在 `#admin` 上门，因此应用程序需要非匿名调用者。从
   [`extension-authorization`](../extension-authorization/SKILL.md) 中获取登录、`useInternetIdentity` / `useActor` 接管和凭证设置者需要的 `#admin` 门。

2. **一个管理员设置页面** — `/settings/twilio`（管理员门）。必须：
   - 一个“如何获取您的 Twilio 凭据”面板 **在输入上方**，将其框定为一次性的 ~5 分钟设置，并带有以下编号步骤（完成消息必须逐字重复它们）：
     1. 在 <https://console.twilio.com> 登录；
     2. 从仪表板复制 **Account SID** (`AC…`)；
     3. **Account → API keys & tokens → Create API key**（Standard）；复制 **SID** (`SK…`) 和 **Secret** — *Secret 只显示一次*；
     4. **Phone Numbers → Manage → Buy a number** 使用 **SMS** 功能；
     5. 粘贴三个值以及下方的号码并保存；
     6. 在试验账户上，在 **Verified Caller IDs** 下验证每个接收者。
     包含一个方便的链接，可以打开 Twilio 控制台。
   - **三个输入**：Account SID（纯文本 — 不是秘密），Key SID，Key Secret（密码输入）。绑定到 `setTwilioCredentials`；成功后清除秘密；保持表单可重新提交，因为密钥会轮换。
   - **一个发送号码字段** 绑定到 `setTwilioFromNumber`，旁边有一个 E.164 示例 (`+15551234567`) 并进行客户端验证。
   - 状态由 `isTwilioConfigured()` (`Bool`) 驱动 — “已配置” / “未配置”。该谓词需要 **所有三个** 值，包括 Key SID：它是 Basic-Auth 用户名，因此空白意味着每个请求都是未身份验证的，而 Twilio 回答 `20003`，而页面声称已配置。**永远** 不要将秘密返回，即使掩码。发送号码可以显示 (`getTwilioFromNumber`)；它不是秘密。
   - **使页面可访问。** 共享布局导航在 `isCallerAdmin` 为 true 时必须链接到这里，否则隐藏它。在定义导航的地方添加链接，而不是在此页面内。

3. **空状态的提示。** 当 `isTwilioConfigured()` 为 `false` 时，永远不要渲染一个死的“发送”按钮：管理员会得到一个“设置 Twilio”链接到 `/settings/twilio`；非匿名非管理员会得到一个解释 — 例如。 "Texting 还未设置 — 管理员需要在设置中添加 Twilio 凭据。"

4. **翻译 Twilio 的错误。** 失败作为 *拒绝* 的调用到达，携带 Twilio 的 `code`。至少将这些映射到操作，而不是显示原始拒绝：
   - `20003` → "Twilio 凭据错误 — 管理员应重新粘贴它们"
   - `21211` → "该电话号码无效 — 使用 +15551234567 格式"
   - `21408` → "在该 Twilio 账户上未启用该国家的短信"
   - `21608` → "在试验账户上，接收者必须在 Twilio 中首先验证"
   - `21610` → "该号码已回复 STOP，不能发送"

5. **永远不要承诺交付。** 成功的调用意味着 *排队*，而不是已送达。相应地调整 UI（“消息已排队”）并在交付很重要的情况下显示从 `fetchMessage` 轮询的 `status`。

建议的路由布局：

```
/                 →  主 UI（任何登录用户；未配置时为空状态）
/settings/twilio  →  管理员凭据 + 发送号码（仅限管理员）
# 没有 /connect/twilio: Twilio 使用粘贴的长寿命凭据，而不是重定向流程。
```

## 作曲家必须告诉 Caffeine 用户的内容

应用程序在人类创建 Twilio 账户、购买号码并粘贴凭据之前不能发送任何内容 — 因此 **完成消息是交付的一部分，而不是它的总结**。它必须包含，按顺序：

1. **凭据是必需的，以及谁输入它们** — 一个管理员，在
   `/settings/twilio`，从登录后的导航中可以到达。
2. **从 *前端* 项目 2 中 **逐字** 的六个编号步骤**，包括 API-key **Secret 只显示一次**。
3. **Twilio 会产生费用** — 每条消息的定价加上每月号码费用，并且试验账户只能发送 **验证** 的号码，并且每个消息都以试验通知为前缀。
4. **对于美国目的地流量：A2P 10DLC 要求**，命名为几周的提前时间和额外费用，以及三个有序资源 — 否则用户将发送一个应用程序，它将无声地失败以到达美国电话。
5. **失败映射，每行一条**：`20003` → 重新粘贴凭据；`21211` → E.164 格式；`21408` → 启用目的地国家；`21608` → 试验验证接收者；`21610` → 接收者取消订阅。

不要将其压缩为“在设置中配置 Twilio”并不要用 Twilio 的文档链接代替。在此处使用与设置页面面板相同的措辞，以便两者不会漂移。

## 已知的限制

- **仅消息表面被提供。** 该包被修剪到消息路径；语音/录音/SIP/使用记录和其他内容不在其中。
- **入站消息不在范围内。** 接收 SMS，以及 `statusCallback` 交付收据，需要在 canister 上有一个入站 HTTP 端点 — 不同的组件，不是这个客户端。
- **二进制媒体无法上传。** `mediaUrl` 接收一个 *公共 URL* Twilio 获取；canister 无法通过此客户端 POST 图像字节。
- **没有 idempotency key。** Twilio 的消息 API 没有它，因此超时后的重试可能会发送两次。在应用程序级别（每个逻辑发送的稳定变量去重键）而不是盲目重试进行保护。非复制的默认值移除了 ~13× 放大，而不是重试语义。
- **丢失了一个字段。** `POST …/IncomingPhoneNumbers/{Sid}.json` 接受一个 `AccountSid` *表单* 字段（用于在子账户之间移动号码），而 `AccountSid` 也是其路径参数。生成器有一个用于两者的单一命名空间，因此表单副本被丢失，并且 **将号码转移到子账户无法通过此客户端实现**。其他所有端点均未受影响。
- **在此处尚未针对实时 Twilio 进行测试。** 线路格式至少在结构上是正确的 — 写入发送 `application/x-www-form-urlencoded` 正文，带有百分号编码的参数，这是 Twilio 所要求的 — 但没有调用被做出。将第一次成功的发送视为真正的接受测试。
- **规范版本：** 从 Twilio 发布的 OpenAPI 规范合并 `spec-merge`（消息 v1 + API v2010）生成，然后修剪到消息表面。不在这些规范中的 Twilio 功能在此处也不存在。

## 相关

- [`mops add twilio-client@0.1.2`](https://mops.one/twilio-client) — 生成的 Twilio REST 绑定（35 个消息模块）。
- [Twilio Messaging 文档](https://www.twilio.com/docs/messaging) — 此 API 包装的 API。
- [`chat`-free 快速入门：发送 SMS](https://www.twilio.com/docs/messaging/api/message-resource) — `Message` 资源，其字段和状态。
- [Twilio 错误代码](https://www.twilio.com/docs/api/errors) — 拒绝消息中显示的数字代码。
- [A2P 10DLC 概述](https://www.twilio.com/docs/messaging/compliance/a2p-10dlc) — 品牌、活动、号码分配。
- [API 密钥与认证令牌](https://www.twilio.com/docs/iam/api-keys) — 为什么生产使用 `SK…`。
- [extension-authorization](../extension-authorization/SKILL.md) — **必需的先决条件**。Internet Identity 登录，`useInternetIdentity` / `useActor` 接管，以及凭证设置者需要的 `#admin` 门。
