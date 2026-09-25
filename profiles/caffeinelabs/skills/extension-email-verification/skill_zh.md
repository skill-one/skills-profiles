# 邮件 — 验证
邮件验证扩展程序，适用于 [Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral)。

## 概述

此技能通过点击验证链接添加邮箱地址验证功能。`MixinEmailVerification` 处理验证回调；`verifiedEmails` 跟踪已验证的地址。

# 后端

## 此组件用于向用户发送包含验证链接的邮件，用户点击链接即可证明其拥有该邮箱地址。

### 检查邮箱地址是否已验证

使用预制模块 `mo:caffeineai-email-verification/verifiedEmails.mo`，该模块不可修改。

```mo:caffeineai-email-verification/verifiedEmails.mo
module {
  public type State = {
    var verifiedEmails : Set.Set<Text>;
  };

  public func new() : State {
    {
      var verifiedEmails = Set.empty<Text>();
    };
  };

  public func contains(state : State, email : Text) : Bool;

  public func iter(state : State) : Iter.Iter<Text>;

  public func size(state : State) : Nat;
};
```

检查邮箱是否已验证时使用 `contains` 函数。**不要**尝试通过存储在用户资料中来独立跟踪邮箱验证状态。

### 处理验证链接

使用预制模块 `mo:caffeineai-email-verification/verificationMixin.mo`，该模块不可修改。

`MixinEmailVerification` 处理对验证链接的调用以验证邮箱地址。

```mo:caffeineai-email-verification/verificationMixin.mo
import MixinEmailVerification "mo:caffeineai-email-verification/verificationMixin";
```

### 向用户发送验证邮件

- 此扩展程序依赖于 [extension-email](../extension-email/SKILL.md) 发送邮件。
- 使用 `sendVerificationEmail` 函数。
- 它返回一个 `SendResult`，如果邮件发送成功则为 `#ok`，否则为 `#err(error)` 并附带错误文本。
- 每个收件人都会收到一个包含特定验证链接的独立邮件。
- `htmlBody` **必须**包含占位符文本 `{{VERIFICATION_URL}}`

```mo:caffeineai-email/emailClient.mo
module {
  public type SendResult = {
    #ok;
    #err : Text;
  };

  public func sendVerificationEmail(
    fromUsername : Text,
    recipients : [Text],
    subject : Text,
    htmlBody : Text,
  ) : async SendResult;
};
```

### 带有注册用户和检查用户是否已验证的端点的示例用法。

```motoko filepath=src/backend/main.mo
import Map "mo:core/Map";
import Runtime "mo:core/Runtime";
import Principal "mo:core/Principal";
import Text "mo:core/Text";
import EmailClient "mo:caffeineai-email/emailClient";
import MixinEmailVerification "mo:caffeineai-email-verification/verificationMixin";
import VerifiedEmails "mo:caffeineai-email-verification/verifiedEmails";

actor {
  // 存储已验证的邮箱
  let verifiedEmails : VerifiedEmails.State;

  // 用户资料存储
  let users : Map.Map<Principal, User>;

  // 邮箱到主键的映射，用于唯一性检查
  let emailToPrincipal : Map.Map<Text, Principal>;

  // 处理验证链接并更新 verifiedEmails 存储
  include MixinEmailVerification(verifiedEmails);

  type User = {
    name : Text;
    email : Text;
  };

  public shared ({ caller }) func registerUser(email : Text, name : Text) : async () {
    if (users.containsKey(caller)) {
      Runtime.trap("User already registered");
    };
    if (emailToPrincipal.containsKey(email)) {
      Runtime.trap("Email already registered");
    };

    let user : User = {
      name;
      email;
    };
    users.add(caller, user);
    emailToPrincipal.add(email, caller);
    let result = await EmailClient.sendVerificationEmail(
      "no-reply",
      [email],
      "Welcome to Our Service",
      "Hello " # name # ",<br><br>Thank you for registering with our service. Please <a href=\"{{VERIFICATION_URL}}\">click here</a> to verify your email address<br><br>Best regards,<br>The Team",
    );

    switch (result) {
      case (#ok) {};
      case (#err(error)) {
        Runtime.trap("Couldn't send verification email: " # error);
      };
    };
  };

  public shared ({ caller }) func isEmailVerified() : async Bool {
    let user = users.get(caller) ?? Runtime.trap("User not registered");
    VerifiedEmails.contains(verifiedEmails, user.email);
  };
};
```

迁移链头：

```motoko filepath=src/backend/migrations/00000000_000000.mo
import Map "mo:core/Map";
import VerifiedEmails "mo:caffeineai-email-verification/verifiedEmails";

module {
  type User = {
    name : Text;
    email : Text;
  };

  type NewActor = {
    verifiedEmails : VerifiedEmails.State;
    users : Map.Map<Principal, User>;
    emailToPrincipal : Map.Map<Text, Principal>;
  };

  public func migration(_old : {}) : NewActor {
    {
      verifiedEmails = VerifiedEmails.new();
      users = Map.empty<Principal, User>();
      emailToPrincipal = Map.empty<Text, Principal>();
    };
  };
};
```

# 前端

如果存在一个让管理员输入验证邮件内容的 UI，则必须指示邮件正文中包含占位符文本 `{{VERIFICATION_URL}}`。
