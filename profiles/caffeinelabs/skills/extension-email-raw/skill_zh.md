# 邮件 — 原始多收件人
用于 [Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral) 的原始多收件人邮件扩展。

## 概述

此技能添加了对发送具有多个 `to`、`cc` 和 `bcc` 收件人的邮件的支持。不适用于向多个用户发送服务邮件（收件人可以看到其他所有收件人）。

# 后端

## 此扩展用于发送支持多个 `to`、`cc` 和 `bcc` 地址的邮件。

- 此扩展不应用于向多个用户发送服务邮件，因为每个收件人都会看到所有其他收件人列出的信息，这通常会违反用户隐私。

### 发送邮件

- 此扩展依赖于 [extension-email](../extension-email/SKILL.md) 扩展来发送邮件。
- 使用 sendRawEmail 函数。
- 它返回一个 SendResult，如果邮件发送成功则为 #ok，否则为 #err(error) 并附带错误文本。
- 总收件人数量最多为 50 个
- 每个收件人收到的邮件内容相同

```mo:caffeineai-email/emailClient.mo
module {
  public type SendResult = {
    #ok;
    #err : Text;
  };

  public func sendRawEmail(
    fromUsername : Text,
    to : [Text],
    cc : [Text],
    bcc : [Text],
    subject : Text,
    htmlBody : Text,
  ) : async SendResult;
};
```

### 示例用法：向会议参与者发送邮件提醒。

```motoko filepath=src/backend/main.mo
import Runtime "mo:core/Runtime";
import EmailClient "mo:caffeineai-email/emailClient";

actor {
  public func sendMeetingReminder(
    meetingSubject : Text,
    meetingTime : Text,
    confirmedAttendeeEmails : [Text],
    tentativeAttendeeEmails : [Text],
  ) : async () {
    let result = await EmailClient.sendRawEmail(
      "no-reply",
      confirmedAttendeeEmails,
      tentativeAttendeeEmails,
      [],
      meetingSubject,
      "Reminder the meeting will start at " # meetingTime,
    );

    switch (result) {
      case (#ok) {};
      case (#err(error)) {
        Runtime.trap("Failed to send meeting reminder email: " # error);
      };
    };
  };
};
```
