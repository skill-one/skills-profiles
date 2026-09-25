# 邮件 — 营销
用于 [Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral) 的营销邮件扩展。

## 概述

此技能提供直接营销邮件支持，包括订阅者管理、基于主题的订阅以及自动退订链接。用户在接收营销邮件前必须验证邮箱地址。

# 后端

## 该组件用于发送直接营销邮件和管理营销主题的订阅者。

- 用户必须在接收该主题的营销邮件前验证邮箱地址 **且** 必须订阅该营销主题。
- 营销邮件必须包含退订链接，该链接将用户从指定主题中退订。
- 该组件依赖于 [extension-email-verification](../extension-email-verification/SKILL.md) 进行邮箱验证，请确保也检查该组件。

### 订阅用户到营销主题和管理订阅者列表

- 使用预置模块 `mo:caffeineai-email-marketing/subscribers.mo`，该模块不可修改。
- 营销邮件订阅者必须完全通过该订阅者模块处理。
- **不要** 在用户资料中也存储订阅状态

```mo:caffeineai-email-marketing/subscribers.mo
module {
  public type State = {
    var topics : Map.Map<Nat, TopicRecord>;
    var topicsByName : Map.Map<Text, Nat>;
  };

  // 通过名称添加新主题或获取已存在的主题。返回主题 ID。
  public func addTopic(state : State, name : Text) : Nat;

  // 重命名主题。如果新名称已存在主题或主题 ID 不存在，则返回 false。
  public func renameTopic(state : State, topicId : Nat, newName : Text) : Bool;

  // 删除主题。同时删除该主题下的所有订阅者。
  public func removeTopic(state : State, topicId : Nat);

  // 列出所有主题（ID，名称）。
  public func listTopics(state : State) : [Topic];

  // 通过名称获取主题 ID
  public func getTopicId(state : State, name : Text) : ?Nat;

  // 通过 ID 获取主题名称
  public func getTopicName(state : State, topicId : Nat) : ?Text;

  // 向主题添加订阅者。如果主题不存在，则返回 false
  public func add(state : State, topicId : Nat, email : Text) : Bool;

  // 从主题中删除订阅者
  public func remove(state : State, topicId : Nat, email : Text);

  // 从所有主题中删除订阅者
  public func removeFromAllTopics(state : State, email : Text);

  // 列出给定主题的所有订阅者及其验证状态。如果主题不存在，则返回 null。
  public func list(state : State, verifiedEmails : VerifiedEmails.State, topicId : Nat) : ?[(Text, Bool)];

  // 列出给定主题的所有已验证订阅者。如果主题不存在，则返回 null。
  public func verified(state : State, verifiedEmails : VerifiedEmails.State, topicId : Nat) : ?[Text];

  // 返回订阅者是否订阅了主题
  public func isSubscribed(state : State, topicId : Nat, email : Text) : Bool;

  // 列出订阅者订阅的所有主题。
  public func listTopicsForSubscriber(state : State, email : Text) : [Topic];

  // 返回给定主题的订阅者数量
  public func count(state : State, topicId : Nat) : Nat;

  // 返回给定主题的已验证订阅者数量
  public func verifiedCount(state : State, verifiedEmails : VerifiedEmails.State, topicId : Nat) : Nat;
};
```

### 处理退订链接

使用不可修改的预置模块 `caffeineai-email-marketing/unsubscribeMixin.mo`。

MixinEmailUnsubscribe 模块处理退订链接的调用，以从主题中退订邮箱地址。

```mo:caffeineai-email-marketing/unsubscribeMixin.mo
import MixinEmailUnsubscribe "mo:caffeineai-email-marketing/unsubscribeMixin";
```

### 从后端发送直接营销邮件

- 该组件依赖于 `email` 组件发送邮件地址。
- 使用 `sendMarketingEmail` 函数。
- 必须与 `subscribers.mo` 模块和 `unsubscribeMixin.mo` 模块一起使用。
- `recipients` 参数是邮件地址数组，其中每个邮件可以指定一个可选的替换名称/值对数组。
  - 这些替换允许为每个收件人个性化邮件内容。
  - 如果邮件正文包含双花括号中的替换名称，则会被替换为该收件人的替换值。
- 返回一个 `Result`，如果邮件发送成功则为 `#ok`，否则为 `#err(error)` 并附带错误文本。
- 确保如果 `htmlBody` 中不存在，则追加占位符文本 `{{UNSUBSCRIBE_URL}}`。系统将自动将其替换为每个收件人的特定退订 URL。

```mo:caffeineai-email/emailClient.mo
module {
  public type BroadcastEmailRecipient = {
    email : Text;
    substitutions : ?[(Text, Text)];
  };

  public type SendResult = {
    #ok;
    #err : Text;
  };

  public func sendMarketingEmail(
    topicId : Nat,
    fromUsername : Text,
    recipients : [BroadcastEmailRecipient],
    subject : Text,
    htmlBody : Text,
  ) : async SendResult;
};
```

### 示例用法：一个可以向由管理员管理的主题订阅用户发送营销邮件的应用

```motoko filepath=src/backend/main.mo
import Array "mo:core/Array";
import Runtime "mo:core/Runtime";
import Option "mo:core/Option";
import Principal "mo:core/Principal";
import Iter "mo:core/Iter";
import Map "mo:core/Map";
import Set "mo:core/Set";
import Text "mo:core/Text";
import AccessControl "mo:caffeineai-authorization/access-control";
import MixinAuthorization "mo:caffeineai-authorization/MixinAuthorization";
import EmailClient "mo:caffeineai-email/emailClient";
import MixinEmailUnsubscribe "mo:caffeineai-email-marketing/unsubscribeMixin";
import EmailSubscribers "mo:caffeineai-email-marketing/subscribers";
import MixinEmailVerification "mo:caffeineai-email-verification/verificationMixin";
import VerifiedEmails "mo:caffeineai-email-verification/verifiedEmails";

actor {
  public type UserProfile = {
    name : Text;
    email : Text;
  };

  // 包含授权组件
  let accessControlState : AccessControl.AccessControlState;
  include MixinAuthorization(accessControlState, null);

  // 存储调用者 principal 到 UserProfile 的映射
  let userProfiles : Map.Map<Principal, UserProfile>;

  // 存储邮箱以进行唯一性检查
  let emails : Set.Set<Text>;

  // 存储哪些邮箱已验证
  let verifiedEmails : VerifiedEmails.State;

  // 在此示例中，我们使用一个硬编码的主题。
  // 通常，管理员可以通过 CRUD 端点管理邮件订阅主题。
  transient let newsletterTopic = "Newsletter";

  // 按主题存储邮件订阅者
  let emailSubscribers : EmailSubscribers.State;

  // 包含此 mixin 以处理退订链接，该链接更新 EmailSubscribers 状态
  include MixinEmailUnsubscribe(emailSubscribers);

  // 包含此 mixin 以处理验证链接，该链接更新 VerifiedEmails 状态
  include MixinEmailVerification(verifiedEmails);

  func getUserInternal(caller : Principal) : UserProfile {
    userProfiles.get(caller) ?? Runtime.trap("User profile does not exist!");
  };

  public shared ({ caller }) func registerUser(name : Text, email : Text) : async () {
    // 检查用户是否已存在
    if (userProfiles.containsKey(caller)) {
      Runtime.trap("User already registered");
    };
    // 检查邮箱是否已被使用
    if (emails.contains(email)) {
      Runtime.trap("Email already taken");
    };
    // 添加用户记录
    userProfiles.add(
      caller,
      {
        name;
        email;
      },
    );
    emails.add(email);
    // 默认将用户订阅到 Newsletter 主题
    let topicId = EmailSubscribers.getTopicId(emailSubscribers, newsletterTopic)
      ?? Runtime.trap("Newsletter topic not found");
    ignore EmailSubscribers.add(emailSubscribers, topicId, email);
    // 发送验证邮件
    let result = await EmailClient.sendVerificationEmail(
      "no-reply",
      [email],
      "Welcome to Our Service",
      "Hello " # name # ",<br><br>Thank you for registering with our service.<br><br>Please <a href=\"{{VERIFICATION_URL}}\">click here</a> to verify your email address.<br><br>By clicking on the verification link you also agree to sign-up to the monthly Newsletter which you can unsubscribe from at any time.<br><br>Best regards,<br>The Team",
    );
    switch (result) {
      case (#ok) {};
      case (#err(error)) {
        Runtime.trap("Failed to send verification email: " # error);
      };
    };
  };

  public shared ({ caller }) func addTopic(name : Text) : async Nat {
    if (not (AccessControl.hasPermission(accessControlState, caller, #admin))) {
      Runtime.trap("Unauthorized: Only admins can add topics");
    };
    EmailSubscribers.addTopic(emailSubscribers, name);
  };

  public shared ({ caller }) func removeTopic(topicId : Nat) : async () {
    if (not (AccessControl.hasPermission(accessControlState, caller, #admin))) {
      Runtime.trap("Unauthorized: Only admins can remove topics");
    };
    EmailSubscribers.removeTopic(emailSubscribers, topicId);
  };

  public shared ({ caller }) func renameTopic(topicId : Nat, newName : Text) : async () {
    if (not (AccessControl.hasPermission(accessControlState, caller, #admin))) {
      Runtime.trap("Unauthorized: Only admins can rename topics");
    };
    let success = EmailSubscribers.renameTopic(emailSubscribers, topicId, newName);
    if (not success) {
      Runtime.trap("Failed to rename topic");
    };
  };

  public shared ({ caller }) func subscribeToTopic(topicId : Nat) : async () {
    let userProfile = getUserInternal(caller);
    ignore EmailSubscribers.add(emailSubscribers, topicId, userProfile.email);
  };

  public shared ({ caller }) func unsubscribeFromTopic(topicId : Nat) : async () {
    let userProfile = getUserInternal(caller);
    EmailSubscribers.remove(emailSubscribers, topicId, userProfile.email);
  };

  public shared ({ caller }) func sendMarketingEmail(topicId : Nat, subject : Text, htmlBody : Text) : async () {
    if (not (AccessControl.hasPermission(accessControlState, caller, #admin))) {
      Runtime.trap("Unauthorized: Only admins can send the newsletter");
    };
    // 获取已验证的订阅者邮件数组
    let recipientEmails = EmailSubscribers.verified(emailSubscribers, verifiedEmails, topicId)
      ?? Runtime.trap("No verified subscribers found for newsletter topic");
    if (recipientEmails.size() == 0) {
      Runtime.trap("No verified subscribers found for newsletter topic");
    };
    // 确保邮件正文包含退订链接占位符
    let finalHtmlBody = if (htmlBody.contains(#text "{{UNSUBSCRIBE_URL}}")) {
      htmlBody;
    } else {
      htmlBody # "<br><br>To unsubscribe <a href=\"{{UNSUBSCRIBE_URL}}\">click here</a>";
    };
    // 为每个收件人指定 NAME 替换以个性化邮件
    let recipients = recipientEmails.filterMap(
      func(email) {
        switch (userProfiles.values().find(func(user) { user.email == email })) {
          case (?user) { ?{ email; substitutions = ?[("NAME", user.name)] } };
          case (null) { null };
        };
      }
    );
    let result = await EmailClient.sendMarketingEmail(
      topicId,
      "no-reply",
      recipients,
      subject,
      finalHtmlBody,
    );
    switch (result) {
      case (#ok) {};
      case (#err(error)) {
        Runtime.trap("Failed to send newsletter: " # error);
      };
    };
  };

  public query ({ caller }) func listTopics() : async [EmailSubscribers.Topic] {
    EmailSubscribers.listTopics(emailSubscribers);
  };

  // 管理员函数，列出主题订阅者及其邮箱是否已验证
  public query ({ caller }) func listSubscribers(topicId : Nat) : async [(Text, Bool)] {
    if (not (AccessControl.hasPermission(accessControlState, caller, #admin))) {
      Runtime.trap("Unauthorized: Only admins can list topic subscribers");
    };
    EmailSubscribers.list(emailSubscribers, verifiedEmails, topicId).get([]);
  };

  public query ({ caller }) func isCallerSubscribedToTopic(topicId : Nat) : async Bool {
    let userProfile = getUserInternal(caller);
    EmailSubscribers.listTopicsForSubscriber(emailSubscribers, userProfile.email).find(
      func(topic) { topic.id == topicId }
    ).isSome();
  };

  public query ({ caller }) func isCallerEmailVerified() : async Bool {
    let userProfile = getUserInternal(caller);
    VerifiedEmails.contains(verifiedEmails, userProfile.email);
  };
};
```

迁移链头部 — `newsletterTopic` 是 `transient`，因此迁移会重复主题字面量而不是引用它：

```motoko filepath=src/backend/migrations/00000000_000000.mo
import Map "mo:core/Map";
import Set "mo:core/Set";
import AccessControl "mo:caffeineai-authorization/access-control";
import EmailSubscribers "mo:caffeineai-email-marketing/subscribers";
import VerifiedEmails "mo:caffeineai-email-verification/verifiedEmails";

module {
  type UserProfile = {
    name : Text;
    email : Text;
  };

  type NewActor = {
    accessControlState : AccessControl.AccessControlState;
    userProfiles : Map.Map<Principal, UserProfile>;
    emails : Set.Set<Text>;
    verifiedEmails : VerifiedEmails.State;
    emailSubscribers : EmailSubscribers.State;
  };

  public func migration(_old : {}) : NewActor {
    {
      accessControlState = AccessControl.initState();
      userProfiles = Map.empty<Principal, UserProfile>();
      emails = Set.empty<Text>();
      verifiedEmails = VerifiedEmails.new();
      emailSubscribers = EmailSubscribers.new(["Newsletter"]);
    };
  };
};
```
