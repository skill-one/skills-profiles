# 邮件 — 日历事件
[Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral) 的日历事件邮件扩展。

## 概述

此技能支持通过邮件组织活动/会议并发送 iCalendar 邀请。它为日历事件提供 CRUD 操作，并支持基于邮件的邀请发送。

# 后端

## 该组件用于通过邮件组织活动/会议并发送邀请

- 内部它会为每个与会者构建并附加一个 iCalendar 文件到邮件中
- 该组件目前还不支持接收与会者的回复

### 添加/更新/取消/删除/获取/列出日历事件

- 使用预构建模块 `mo:caffeineai-email-calendar-events/calendarEvents.mo`，该模块不可修改。

```mo:caffeineai-email-calendar-events/calendarEvents.mo
module {
  public type State = {
    var events : List.List<CalendarEvent>;
    var uidMap : Map.Map<Text, Nat>;
  };

  public func add(
    self : State,
    uid : Text,
    summary : Text,
    description : Text,
    location : Text,
    startTime : Nat64,
    endTime : Nat64,
    organizer : Mailbox,
    attendees : [Attendee]
  ) : ?CalendarEvent;

  public func update(
    self : State,
    uid : Text,
    summary : ?Text,
    description : ?Text,
    location : ?Text,
    startTime : ?Nat64,
    endTime : ?Nat64,
    organizer : ?Mailbox,
    attendees : ?[Attendee]
  ) : ?CalendarEvent;

  public func addAttendees(
    self : State,
    uid : Text,
    attendees : [Attendee]
  ) : ?CalendarEvent;

  public func removeAttendees(
    self : State,
    uid : Text,
    attendees : [Text]
  ) : ?CalendarEvent;

  public func cancel(self : State, uid : Text) : ?CalendarEvent;

  public func delete(self : State, uid : Text);

  public func get(self : State, uid : Text) : ?CalendarEvent;

  // 遍历所有从旧到新的日历事件
  public func iter(self : State) : Iter.Iter<CalendarEvent>;

  // 遍历所有从新到旧的日历事件
  public func reverse(self : State) : Iter.Iter<CalendarEvent>;
}
```

### 通过邮件向与会者发送日历事件邀请

- 该组件依赖于 [extension-email](../extension-email/SKILL.md) 组件来发送日历事件邮件。
- 使用 `sendCalendarEvent` 函数。

```mo:caffeineai-email/emailClient.mo
module {
  public type CalendarEvent = {
    uid : Text;
    sequence : Nat32;
    method : CalendarEventMethod;
    summary : Text;
    description : Text;
    location : Text;
    startTime : Nat64;
    endTime : Nat64;
    organizer : Mailbox;
    attendees : [Attendee];
  };

  public type CalendarEventMethod = {
    #request;
    #publish;
    #cancel;
  };

  public type Mailbox = {
    email : Text;
    name : ?Text;
  };

  public type Attendee = {
    who : Mailbox;
    role : CalendarEventRole;
  };

  public type CalendarEventRole = {
    #chair;
    #required;
    #optional;
    #notParticipating;
  };
  
  public type SendResult = {
    #ok;
    #err : Text;
  };

  public func sendCalendarEvent(fromUsername : Text, event : CalendarEvent) : async SendResult;
};
```

### 用于添加/更新/取消/删除/获取/列出日历事件并向其发送邮件邀请的应用示例

```motoko filepath=src/backend/main.mo
import Runtime "mo:core/Runtime";
import Principal "mo:core/Principal";
import Map "mo:core/Map";
import Random "mo:core/Random";
import Set "mo:core/Set";
import Iter "mo:core/Iter";
import Option "mo:core/Option";
import Text "mo:core/Text";
import AccessControl "mo:caffeineai-authorization/access-control";
import MixinAuthorization "mo:caffeineai-authorization/MixinAuthorization";
import EmailClient "mo:caffeineai-email/emailClient";
import CalendarEvents "mo:caffeineai-email-calendar-events/calendarEvents";
import Uuid "mo:caffeineai-email-calendar-events/uuid";

actor {
  public type UserProfile = {
    name : Text;
    email : Text;
  };

  // 包含授权组件
  let accessControlState : AccessControl.AccessControlState;
  include MixinAuthorization(accessControlState, null);

  // 存储调用者 principal 到 UserProfile 的映射
  var userProfiles : Map.Map<Principal, UserProfile>;

  // 存储邮箱以进行唯一性检查
  var emails : Set.Set<Text>;

  // 存储日历事件
  let calendarEvents : CalendarEvents.State;

  public shared ({ caller }) func registerUser(name : Text, email : Text) : async () {
    // 检查用户是否已注册
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
      }
    );
    emails.add(email);
  };

  public shared ({ caller }) func addCalendarEvent(summary : Text, description : Text, location : Text, startTimeMs : Nat64, endTimeMs : Nat64) : async () {
    if (not (AccessControl.hasPermission(accessControlState, caller, #admin))) {
      Runtime.trap("Unauthorized: Only admins can add calendar events");
    };

    let organiser = userProfiles.get(caller)
      ?? Runtime.trap("Admin profile not found");

    let seed = await Random.blob();
    let uid = Uuid.generateV4(seed);

    if (
      calendarEvents.add(
        uid,
        summary,
        description,
        location,
        startTimeMs,
        endTimeMs,
        {
          name = ?organiser.name;
          email = organiser.email;
        },
        userProfiles.values().map(
          func({ name; email }) {
            {
              who = { name = ?name; email };
              role = #required;
            };
          }
        ).toArray()
      ).isNull()
    ) {
      Runtime.trap("Failed to add calendar event");
    };
  };

  public shared ({ caller }) func updateEventDetails(uid : Text, summary : ?Text, description : ?Text, location : ?Text, startTimeMs : ?Nat64, endTimeMs : ?Nat64) : async () {
    if (not (AccessControl.hasPermission(accessControlState, caller, #admin))) {
      Runtime.trap("Unauthorized: Only admins can update calendar events");
    };

    if (
      calendarEvents.update(
        uid,
        summary,
        description,
        location,
        startTimeMs,
        endTimeMs,
        null,
        null
      ).isNull()
    ) {
      Runtime.trap("Failed to update calendar event");
    };
  };

  public shared ({ caller }) func addEventAttendees(uid : Text, attendees : [EmailClient.Attendee]) : async () {
    if (not (AccessControl.hasPermission(accessControlState, caller, #admin))) {
      Runtime.trap("Unauthorized: Only admins can add calendar event attendees");
    };

    if (calendarEvents.addAttendees(uid, attendees).isNull()) {
      Runtime.trap("Failed to add attendees to calendar event");
    };
  };

  public shared ({ caller }) func removeEventAttendees(uid : Text, attendees : [Text]) : async () {
    if (not (AccessControl.hasPermission(accessControlState, caller, #admin))) {
      Runtime.trap("Unauthorized: Only admins can remove calendar event attendees");
    };

    if (calendarEvents.removeAttendees(uid, attendees).isNull()) {
      Runtime.trap("Failed to remove attendees from calendar event");
    };
  };

  public shared ({ caller }) func cancelEvent(uid : Text) : async () {
    if (not (AccessControl.hasPermission(accessControlState, caller, #admin))) {
      Runtime.trap("Unauthorized: Only admins can cancel calendar events");
    };

    if (calendarEvents.cancel(uid).isNull()) {
      Runtime.trap("Failed to cancel calendar event");
    };
  };

  public shared ({ caller }) func listEvents() : async [CalendarEvents.CalendarEvent] {
    if (not (AccessControl.hasPermission(accessControlState, caller, #admin))) {
      Runtime.trap("Unauthorized: Only admins can list calendar events");
    };

    calendarEvents.iter().toArray();
  };

  public shared ({ caller }) func deleteEvent(uid : Text) : async () {
    if (not (AccessControl.hasPermission(accessControlState, caller, #admin))) {
      Runtime.trap("Unauthorized: Only admins can delete calendar events");
    };

    calendarEvents.delete(uid);
  };

  public shared ({ caller }) func sendEventInvitation(uid : Text) : async () {
    if (not (AccessControl.hasPermission(accessControlState, caller, #admin))) {
      Runtime.trap("Unauthorized: Only admins can send calendar event invitations");
    };

    let event = calendarEvents.get(uid)
      ?? Runtime.trap("Calendar event not found");

    ignore await EmailClient.sendCalendarEvent(
      "no-reply",
      event
    );
  };
};
```

迁移链头部：

```motoko filepath=src/backend/migrations/00000000_000000.mo
import Map "mo:core/Map";
import Set "mo:core/Set";
import AccessControl "mo:caffeineai-authorization/access-control";
import CalendarEvents "mo:caffeineai-email-calendar-events/calendarEvents";

module {
  type UserProfile = {
    name : Text;
    email : Text;
  };

  type NewActor = {
    accessControlState : AccessControl.AccessControlState;
    var userProfiles : Map.Map<Principal, UserProfile>;
    var emails : Set.Set<Text>;
    calendarEvents : CalendarEvents.State;
  };

  public func migration(_old : {}) : NewActor {
    {
      accessControlState = AccessControl.initState();
      var userProfiles = Map.empty<Principal, UserProfile>();
      var emails = Set.empty<Text>();
      calendarEvents = CalendarEvents.new();
    };
  };
};
```
