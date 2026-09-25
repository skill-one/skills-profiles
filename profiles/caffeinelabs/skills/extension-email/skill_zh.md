# 邮件 — 服务/事务性
[Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral) 的服务/事务性邮件扩展。

## 概述

此技能为后端 canister 添加了发送服务性邮件和事务性邮件的支持。使用 `sendServiceEmail` 来发送订单确认、通知等一次性邮件。

# 后端

此组件用于发送服务/事务性邮件。

有一个预制模块 `mo:caffeineai-email/emailClient.mo`，该模块不能被修改。

- 使用 `sendServiceEmail` 函数。
- 每个收件人都会收到一个单独的邮件。
- 它返回一个 `SendResult`，如果邮件发送成功则为 `#ok`，否则为 `#err(error)` 并附带错误文本。

```mo:caffeineai-email/emailClient.mo
module {
  public type SendResult = {
    #ok;
    #err : Text;
  };

  public func sendServiceEmail(
    fromUsername : Text,
    recipients : [Text],
    subject : Text,
    htmlBody : Text,
  ) : async SendResult;
};
```

`sendServiceEmail` 的使用示例：

```motoko filepath=src/backend/main.mo
import Runtime "mo:core/Runtime";
import EmailClient "mo:caffeineai-email/emailClient";

actor {
  public func sendOrderConfirmationEmail(recipientEmailAddress : Text, username : Text, orderReference : Text) : async () {
    let result = await EmailClient.sendServiceEmail(
      "no-reply",
      [recipientEmailAddress],
      "Order " # orderReference # " confirmed",
      "Hello " # username # ",\nYour order " # orderReference # " has been confirmed. Your items will ship tomorrow.",
    );
    switch (result) {
      case (#ok) {};
      case (#err(error)) {
        Runtime.trap("Failed to send order confirmation email: " # error);
      };
    };
  };
};
```
