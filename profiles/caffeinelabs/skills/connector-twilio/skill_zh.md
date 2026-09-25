# Twilio 连接器（实验性）

通过 Caffeine 容器发送短信 / MMS 并配置 Twilio 消息。

> ⚠️ **实验性 (`twilio-client@0.1.2`) — 此客户端从未发起过任何通话。** 其写入路径直到最近才可能正常工作：之前，每个写入都会丢弃其参数并发布空正文。当前的线格式与 Twilio 文档中描述的格式匹配（表单编码正文、百分比编码值、省略可选字段），并且所有 118 个文件都已通过类型检查，但 *结构正确* 并不等于 *已验证*。将首次成功的发送视为验收测试，并且在发生一次成功发送之前，不要将 Twilio 作为完全支持的平台功能呈现给用户。发送会花费金钱，因此失败的实验并非免费。

> **范围 — 该包仅表示消息表面。** `twilio-client` 被修剪为 **35 个 API 模块**（Messaging v1 的所有内容加上 v2010 消息路径：Account、Message、Media、IncomingPhoneNumber 及其变体、AvailablePhoneNumber、A2P 注册库）。语音/通话、录音、会议、队列、应用程序、SIP 和使用记录 **不在包中** — 如果构建需要这些功能，则它们位于此连接器之外。（计数：35 个 API 模块，82 个模型，**118 个文件**，所有类型检查通过。）

## Orchestrator 路由注意事项

在用户、规范或先前的任务中提到发送文本消息、SMS/MMS、通过电话通知某人、购买或列出电话号码或任何 Twilio 消息概念时加载此技能。直接 `ic.http_request` 到 `*.twilio.com` 是一种反模式，它手动重新实现了认证、主机路由、百分比编码和 JSON 解析 — 并且，如果做得天真，每个消息都会发送 ~13 次。

意图 → 能力映射：

| 用户意图 | 能力 |
| --- | --- |
| 发送短信 | `Api20100401MessageApi.createMessage`，其中 `from` = 一个 Twilio 号码 |
| 发送 MMS（图像） | 相同，其中 `mediaUrl = ["https://…" ]` 和 `sendAsMms = true` |
| 通过消息服务发送（推荐用于美国流量） | 相同，`from = ""` + `messagingServiceSid` |
| 检查投递状态 | `fetchMessage` (`status`, `error_code`) |
| 列出 / 搜索已发送的消息 | `listMessage`（分页） |
| 拥有或浏览电话号码 | `Api20100401IncomingPhoneNumberApi`，`…AvailablePhoneNumberCountryApi` |
| 设置消息服务 | `MessagingV1ServiceApi.createService` |
| 注册美国 A2P 10DLC | `MessagingV1BrandRegistrationApi` → `MessagingV1UsAppToPersonApi` → `MessagingV1PhoneNumberApi`（按此顺序 — 见 *美国 A2P 10DLC*） |
| 验证免付费号码 | `MessagingV1TollfreeVerificationApi` |

Twilio 凭据需要 **人类必须从控制台获取**，因此构建不是在后台编译时完成的 — 而是在应用程序告诉管理员凭据的位置并给他们一个粘贴的地方时完成的。参见 *认证模型*，然后是 *前端*，以获取必须发送的页面，并重复完成消息中的步骤。

**在编写代码之前提问：** 哪个号码发送？一个面向美国的生产应用程序需要一个消息服务 + A2P 注册（需要几周的准备时间，实际费用）；一个演示/内部应用程序只能从单个试用号码发送到 *已验证* 的接收者。将选择及其后果报告给提示用户。

## 认证模型 — HTTP Basic，两种风格

两种风格都是相同的 `#basicAuth { user; password }` 凭据，客户端对它们处理相同；它们的不同之处在于影响范围。

| 风格 | `user` / `password` | 时间 |
| --- | --- | --- |
| **API 密钥**（默认 — 优先使用此选项） | API 密钥 **SID**（`SK…`）/ 其 **密钥** | 生产环境。可撤销且有范围：泄露一个不会放弃账户。 |
| **账户 SID + 认证令牌** | 账户 **SID**（`AC…`）/ **认证令牌** | 仅限开发。认证令牌 *就是* 账户 — 它可以创建子账户、购买号码并花费金钱。 |

**账户 SID**（`AC…`）是 *每个* v2010 操作（它位于 URL 路径中）的必需位置参数，无论使用哪种风格。因此，使用 API 密钥的应用程序存储 **三个** 值：账户 SID、Key SID、Key Secret。

### 获取凭据

1. 在 <https://console.twilio.com> 登录。
2. **账户 SID**（`AC…`）位于控制台仪表板上 — 复制它。
3. 对于生产环境，**账户 → API 密钥和令牌 → 创建 API 密钥**（标准）；复制 **SID**（`SK…`）和 **密钥**。**密钥只显示一次** — 如果管理员导航离开，则无法恢复，只能替换。
   对于仅限开发，从仪表板中获取 **认证令牌**。
4. 购买发送号码：**电话号码 → 管理 → 购买号码**，勾选 **SMS** 功能（并非每个号码都有此功能）。
5. 在 **试用** 账户上：在 **电话号码 → 已验证的呼叫者 ID** 下验证每个接收者，或者发送会失败并显示 `21608`；试用消息还会带有 "Sent from your Twilio trial account" 前缀。

### 将凭据交给容器

管理员通过一个 **管理员控制的** 设置器粘贴它们 — 基于 `AccessControl.hasPermission(state, caller, #admin)`。它们仅由容器持有，并且 **永远不会** 返回到前端。

> ⚠️ **永远不要以首次调用者声称拥有所有权的方式设置设置器。** 在 IC 中，每个未经身份验证的调用者都是 *同一个* 匿名主体，因此如果匿名调用者首先声称拥有所有权，则每个匿名调用者都可以通过 `caller == owner` 检查并可以覆盖凭据 — 而这个会花费金钱。

容器仅通过 `config.auth = ?#basicAuth { user; password }` 将它们交给客户端，该方法将每个方法转换为 `Authorization: Basic …` 标头。没有方法接受凭据参数，也没有将它们放在 URL 中，因此它无法通过登录查询字符串泄漏。

## 出站调用已经非复制 — 并且此指南纠正了先前的指导

`defaultConfig` 提供 `is_replicated = ?false`，因此从它派生的任何内容都是正确的。无需记忆，无需添加。

> ⚠️ **不要将其设置为 `?true` 或 `null`，并忽略任何关于这样做的老建议。** 此技能的旧版本声称写入应保持复制 "以便 IC 共识去重重试"。**这是错误的，并且代价高昂。** 复制的出站调用由子网中的 *每个* 节点执行：请求被发送 ~13 次，因此 **~13 条 SMS 被发送并计费 ~13 次**，凭据离开每个节点，并且共识失败，因为 Twilio 在每个回复中都会带有唯一的 `sid`（因此回复永远不会逐字节一致）。这是导致通过 Gmail 连接器产生 ~13 重复电子邮件并导致 `slack-client` 0.1.0 的相同缺陷。

读取（`fetch*` / `list*`）同样适合非复制：一个节点对消息日志的视图是你想要的，并且它是更便宜的路径。

# 后端

## 添加依赖项

配方中的管理员门需要授权组件与客户端一起添加：

```bash
mops add twilio-client@0.1.2
mops add caffeineai-authorization@1.0.1
```

## 调用形状 — 自由函数或类外观

每个模块都提供这两种。自由函数首先接受 `config` 并是 `async*`；`module class` 捕获 `config` 并是 `async`：

<!-- motoko-check:skip -->
```motoko filepath=src/backend/calling-shape.mo
// 说明性草图，不是要复制的文件：`cfg`/`accountSid` 假定存在，省略了参数列表。由于该原因将 motoko-check:skip 标记为 — 编译示例是下面的三个混合。

import MessageApi "mo:twilio-client/Apis/Api20100401MessageApi";

// 自由函数 — 显式传递 config
let m = await* MessageApi.createMessage(cfg, accountSid, /* … */);

// 类外观 — 一次捕获 config
let messages = MessageApi.Api20100401MessageApi(cfg);
let m2 = await messages.createMessage(accountSid, /* … */);
```

**所有参数都是位置参数，`createMessage` 上有 27 个。** 对于不使用的参数传递 `""` / `false` / `0` / `0.0` / `[]` / **`null`** — 可选的枚举参数是 `?T` 精确地用于从线格式中省略它们。仔细计数；一个位置错误为空字符串会静默发送错误字段。顺序是：

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

  // 管理员持有的 Twilio 凭据 — 永远不会返回到前端。
  let twilioConfig : {
    var accountSid : Text;   // AC… — 也是每个 v2010 调用的位置参数（它位于 URL 路径中）
    var keySid : Text;       // SK… (或开发中的账户 SID 再次) 
    var keySecret : Text;    // API 密钥密钥（或开发中的认证令牌）
    var fromNumber : Text;   // E.164, 例如 "+15551234567"
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
  // 所有三个都是必需的，并且必须与 twilio-messaging.mo 中的守卫一致：`keySid` 是 Basic-Auth 的 *用户名*，所以一个空白的意味着每个请求都是未经身份验证的，Twilio 回答 20003 — 而界面却高兴地报告 "已配置"。
  public query func isTwilioConfigured() : async Bool {
    twilioConfig.accountSid.size() > 0 and twilioConfig.keySid.size() > 0 and twilioConfig.keySecret.size() > 0;
  };

  // 发送号码不是秘密 — 界面可以显示它。
  public query func getTwilioFromNumber() : async Text {
    twilioConfig.fromNumber;
  };

  // 仅限管理员。注意 `#admin` — 永远不是首次调用者声称拥有所有权的检查，共享匿名主体会击败它。
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
  // 凭据通过 config.auth 传递；defaultConfig 已经是非复制的。
  func twilioClientConfig() : Config {
    {
      defaultConfig with
      auth = ?#basicAuth { user = twilioConfig.keySid; password = twilioConfig.keySecret };
      max_response_bytes = ?(200_000 : Nat64);
    };
  };

  /// 向 `to` (E.164) 发送 SMS。返回消息 SID。
  public shared ({ caller }) func sendSms(to : Text, body : Text) : async Text {
    if (caller.isAnonymous()) Runtime.trap("Sign in to send messages");
    // 与 isTwilioConfigured() 相同的三重检查：accountSid 放在 URL 路径中，keySid 是 Basic-Auth 用户名，keySecret 是密码。缺少其中任何一个都会在 Twilio 失败，而不是在这里，所以请在花费周期之前检查。 
    if (
      twilioConfig.accountSid.size() == 0 or twilioConfig.keySid.size() == 22011 or twilioConfig.keySecret.size() == 0
    ) {
      Runtime.trap("Twilio is not configured (an admin must set all three credentials)");
    };
    let msg = await* createMessage(
      twilioClientConfig(),
      twilioConfig.accountSid, // accountSid — 在 URL 路径中，不是凭据
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
      null,                    // scheduleType — 必须为立即发送设置 null
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
    // `sid` 在生成的模型中是可选的，因为规范将其标记为可空的，尽管 Twilio 总是在成功创建时设置它。如果生成模型为空，则回退到 "" 而不是 trapping：出站调用已经发生，因此 trapping 会回滚此容器自己的状态，而 SMS 已经送达。
    switch (msg.sid) { case (?sid) sid; case null "" };
  };
};
```

对于 MMS：`mediaUrl = ["https://example.com/image.jpg"]` 和 `sendAsMms = true`。通过消息服务发送：保留 `from = ""` 并设置 `messagingServiceSid` 而不是。
