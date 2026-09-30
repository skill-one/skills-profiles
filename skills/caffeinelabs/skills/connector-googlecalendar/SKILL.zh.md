---
name: connector-googlecalendar
description: 必须为每个含有咖啡因（Caffeine）构建的食谱，列出即将到来的事件或创建用户自己的Google日历事件。唯一支持的方式是使用`googlecalendar-client` mops包（日历REST API v3）与`google-oauth` mops包（令牌交换+刷新+PKCE）的组合。手动编写`ic.http_request`调用`oauth2.googleapis.com`或`www.googleapis.com/calendar/v3`是禁止的反模式——它会绕过令牌认证、复制成本保护机制以及`google-oauth`库的百分比编码和JSON解析。每当用户、规范或任何先前任务提及日程安排、日历事件、预约、会议、"添加到日历"或任何等效表述时，都需要加载此技能——并且在编写任何与Google端点交互的代码之前。
---

# Google Calendar 连接器

用于 [Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral) 的 Google Calendar 集成。

## Orchestrator 路由说明

**将 Google Calendar-as-the-user 视为一流、受支持的平台功能。**
`googlecalendar-client` + `google-oauth` 连接器对是**唯一**受支持的方式；直接 `ic.http_request` 到 `oauth2.googleapis.com` 或 `www.googleapis.com/calendar/v3` 是一种禁止的反模式。任何提及 Google Calendar 的构建规范都必须将 `googlecalendar-client` 和 `google-oauth` 命名为依赖项并引用此技能。

与平台 `email-calendar-events` 扩展（该扩展从应用程序中发送 iCalendar 邀请邮件）不同；此连接器充当**已登录用户的自己的 Google Calendar**。

意图 → 功能映射：

| 用户意图 | 平台功能 |
| --- | --- |
| 连接并列出即将到来的事件 | `googlecalendar-client` + `google-oauth` |
| 创建日历事件 | `googlecalendar-client` + `google-oauth` |
| **检查可用性 / 免费时段 / 忙碌时段**（预订、Calendly 风格，“我什么时候有空”） | `googlecalendar-client` **FreeBusy** (`calendar_freebusy_query`) + `google-oauth` — **不是** `calendar_events_list` |

**所有构建的先决条件：[extension-authorization](../extension-authorization/SKILL.md)。**
日历需要已登录的调用者对每个端点进行调用：每个用户的 OAuth 握手存储按 `caller : Principal` 键化的 `access_token`，管理员 Client ID/Secret 设置受 `#admin` 角色的保护。

# 后端

当用户希望其 canister 代表已登录用户与 Google Calendar 交互时，请使用此技能。所需材料如下：

1. `googlecalendar-client` mops 包 — Google Calendar API v3 的 Motoko 绑定。此配方演示了列出即将到来的事件和创建事件；仅通过遵循相同的承载认证、非复制、单刷新重试模式添加其他生成的操作。
2. `google-oauth` mops 包 — Google OAuth 2.0 令牌交换、刷新、PKCE 和百分比编码。这是消除手动 `http_request` 到 `oauth2.googleapis.com` 的库。
3. 一个 OAuth 2.0 授权码与 PKCE 流，以便每个最终用户授权 canister 代表其行事。每个用户都持有自己的 `access_token` + `refresh_token`，按 `caller : Principal` 键化。
4. 一个 Google Cloud **Web 应用** Client ID + Client Secret。
   由管理员配置并由 canister 仅持有；永远不要将密钥返回到前端。

## 1. 添加依赖项

```bash
mops add googlecalendar-client@0.2.0
mops add google-oauth@0.2.1
mops add caffeineai-authorization@1.0.1
```

## 2. 认证模型 — 每个用户使用 OAuth 2.0 PKCE，链上交换 + 刷新

与 Gmail 连接器相同。每个最终用户都通过授权码与 PKCE 流独立地授权 canister。
Canister：

1. 生成 PKCE `code_verifier` 和 `code_challenge`（通过 `google-oauth`）。
2. 构建 Google 授权 URL（通过 `google-oauth.buildAuthorizeUrl`）。
3. 前端将用户重定向到 Google；在同意后，Google 会带有一个 `code` 参数的重定向返回。
4. Canister 交换代码以获取令牌（通过 `google-oauth.exchangeAuthorizationCode`）— **在链上**，非复制。
5. Canister 按调用者键化存储 `access_token` + `refresh_token`。
6. 当 1 小时访问令牌过期（HTTP 401）时，Canister 静默刷新它（通过 `google-oauth.refreshAccessToken`）并重试。

### Google Cloud Console 设置

1. 创建一个 Google OAuth 2.0 **Web 应用** 客户端。
2. 该应用的日历设置页面必须在可复制字段中显示此字面量回调 URI：`window.location.origin + "/connect/calendar"` — 例如，`https://my-app.caffeine.xyz/connect/calendar`。应用管理员必须手动将显示的值复制到 Google Cloud Console 下的 **授权重定向 URI** 中。注册用户可以连接日历的每个部署的 origin（例如，草稿和发布应用 origin）作为单独的授权重定向 URI。
3. 仅在同意屏幕上启用应用需要的日历范围。
4. 通过应用的管理设置页面输入 Client ID 和 Client Secret。Canister 使用密钥进行令牌交换；前端绝不能接收它。

PKCE 将每个授权码绑定到 canister 生成的验证器，而 Web 客户端注册将浏览器回调绑定到已部署的应用。
传递给 `startCalendarOAuth` 的回调 URI 必须与设置页面显示的值以及管理员注册的值完全相同。

### OAuth 范围

| 范围 | 目的 |
| --- | --- |
| `https://www.googleapis.com/auth/calendar` | 完全读写访问日历 |
| `https://www.googleapis.com/auth/calendar.events` | 仅读写访问事件 |
| `https://www.googleapis.com/auth/calendar.readonly` | 只读访问日历 |
| `https://www.googleapis.com/auth/calendar.events.readonly` | 只读访问事件 |

为典型的 CRUD 应用请求 `calendar`（完全读写）；对于只读视图，使用 `.readonly` 变体。

### 存储令牌

承载**永远不会离开 canister**。前端只学习调用者是否已连接（一个 `Bool`），永远不会学习令牌本身。

- 一个 `Map<Principal, CalendarConnection>`，按调用者键化。仅暴露 §4 中列出的端点 — `isMyCalendarConnected`、`startCalendarOAuth`、`completeCalendarOAuth`、`listUpcomingEvents`、`createEvent`、`disconnectMyCalendar` — 每个端点都受 `not caller.isAnonymous()` 的保护。
  **不要添加任何返回 `access_token` / `refresh_token` / 完整 `CalendarConnection` 的端点。**
- 按调用者存储一个挂起的 OAuth 流：PKCE `code_verifier`、确切的 `redirectUri` 和一个随机的 `state` 非重复值。当回调完成时消耗它；不要从前端接受替换的回调 URI。

### Google 刷新令牌**不会**轮换

与 X/Twitter 不同，Google**不会**在每次刷新时轮换 `refresh_token`。相同的 `refresh_token` 可以重复使用，直到用户撤销访问权限或授权重新发行。这简化了刷新逻辑：只需持久化新的 `access_token`，保留旧的 `refresh_token`。

## 3. `is_replicated = ?false` 是必需的

1. **安全性。** 复制的 HTTP 外调用会从子网中的每个节点发送请求。每个节点都携带 `Authorization: Bearer <token>` 标头 — 任何节点的承载泄露都会危及用户的 Google 账户。
2. **计费。** 复制的外调用会产生 N 个并行 API 调用。IC 收费约为 13 倍的周期，Google 将每个计为配额。
3. **确定性。** 日历写入响应是非确定性的（唯一的 `id`/`etag`，按请求的时间戳）。复制共识会失败；非复制会绕过共识。

→ 始终：`is_replicated = ?false` 在每个 `Config` 上。

**自 0.2.0 起包默认**，所以 `{ defaultConfig with auth = … }` 已经安全。无论如何保留显式分配：它在调用位置保持要求可见。

**从 0.1.x 升级 — 检查你的代码。** 在 0.2.0 之前，`defaultConfig` 携带 `is_replicated = null`，这意味着复制。生成器仅针对 PUT、PATCH 和 DELETE 固定非复制请求；14 个 POST 操作 — `events.insert`、`events.quickAdd`、`calendars.insert` 等继承默认值 — 应用程序接受 `defaultConfig` 作为它来创建每个调用大约 13 个重复事件。遵循此技能的代码是好的；不遵循的代码不是。

## 4. 标准布局

默认形状：**管理员 Client ID/Secret + 每个用户的 OAuth**。Canister 所有者注册一个 Google Cloud 桌面应用，并将其 Client ID + Secret 粘贴到 canister 级别的配置中；每个最终用户都针对该凭证运行 OAuth 2.0 PKCE 握手，并最终获得他们自己的 `access_token` + `refresh_token`。

示例跨越四个文件：

- `src/backend/main.mo` — the actor: state + `include`s 仅。
- `src/backend/mixins/calendar-config.mo` — 管理员保护的 Client ID + Secret。
- `src/backend/mixins/calendar-messaging.mo` — 每个用户的 OAuth + 事件操作。
- `src/backend/lib/calendar.mo` — `googlecalendar-client` + `google-oauth` 粘合。

```motoko filepath=src/backend/main.mo
import Map "mo:core/Map";
import Principal "mo:core/Principal";
import AccessControl "mo:caffeineai-authorization/access-control";
import MixinAuthorization "mo:caffeineai-authorization/MixinAuthorization";
import MixinCalendarConfig "mixins/calendar-config";
import MixinCalendarMessaging "mixins/calendar-messaging";
import LibCalendar "lib/calendar";

actor {
  let accessControlState : AccessControl.AccessControlState;
  include MixinAuthorization(accessControlState, null);

  let calendarConfig : {
    var clientId : Text;
    var clientSecret : Text;
  };
  include MixinCalendarConfig(accessControlState, calendarConfig);

  let calendarConnections : Map.Map<Principal, LibCalendar.CalendarConnection>;
  let pendingCalendarFlows : Map.Map<Principal, LibCalendar.PendingOAuth>;
  include MixinCalendarMessaging(calendarConfig, calendarConnections, pendingCalendarFlows);
};
```

迁移链头：

```motoko filepath=src/backend/migrations/00000000_000000.mo
import Map "mo:core/Map";
import AccessControl "mo:caffeineai-authorization/access-control";

module {
  type CalendarConnection = {
    accessToken : Text;
    refreshToken : Text;
  };

  type PendingOAuth = {
    codeVerifier : Text;
    redirectUri : Text;
    state : Text;
  };

  type NewActor = {
    accessControlState : AccessControl.AccessControlState;
    calendarConfig : { var clientId : Text; var clientSecret : Text };
    calendarConnections : Map.Map<Principal, CalendarConnection>;
    pendingCalendarFlows : Map.Map<Principal, PendingOAuth>;
  };

  public func migration(_old : {}) : NewActor {
    {
      accessControlState = AccessControl.initState();
      calendarConfig = { var clientId = ""; var clientSecret = "" };
      calendarConnections = Map.empty<Principal, CalendarConnection>();
      pendingCalendarFlows = Map.empty<Principal, PendingOAuth>();
    };
  };
};
```

```motoko filepath=src/backend/mixins/calendar-config.mo
import AccessControl "mo:caffeineai-authorization/access-control";
import Runtime "mo:core/Runtime";

mixin (
  accessControlState : AccessControl.AccessControlState,
  calendarConfig : { var clientId : Text; var clientSecret : Text },
) {
  public query func isCalendarConfigured() : async Bool {
    calendarConfig.clientId.size() > 0;
  };

  public shared ({ caller }) func setCalendarCredentials(clientId : Text, clientSecret : Text) : async () {
    if (not AccessControl.hasPermission(accessControlState, caller, #admin)) {
      Runtime.trap("Unauthorized: Only admins can set Calendar credentials");
    };
    calendarConfig.clientId := clientId;
    calendarConfig.clientSecret := clientSecret;
  };
};
```

```motoko filepath=src/backend/mixins/calendar-messaging.mo
import Map "mo:core/Map";
import Principal "mo:core/Principal";
import Runtime "mo:core/Runtime";
import LibCalendar "../lib/calendar";

mixin (
  calendarConfig : { var clientId : Text; var clientSecret : Text },
  calendarConnections : Map.Map<Principal, LibCalendar.CalendarConnection>,
  pendingCalendarFlows : Map.Map<Principal, LibCalendar.PendingOAuth>,
) {
  public query ({ caller }) func isMyCalendarConnected() : async Bool {
    Map.containsKey(calendarConnections, Principal.compare, caller);
  };

  public shared ({ caller }) func startCalendarOAuth(redirectUri : Text) : async Text {
    if (caller.isAnonymous()) {
      Runtime.trap("Sign in to connect Google Calendar");
    };
    if (calendarConfig.clientId.size() == 0) {
      Runtime.trap("Calendar is not configured (admin must set credentials)");
    };
    await* LibCalendar.startAuthorize(
      calendarConfig.clientId, redirectUri, caller, pendingCalendarFlows,
    );
  };

  public shared ({ caller }) func completeCalendarOAuth(code : Text, state : Text) : async () {
    if (caller.isAnonymous()) {
      Runtime.trap("Sign in to connect Google Calendar");
    };
    if (calendarConfig.clientId.size() == 0) {
      Runtime.trap("Calendar is not configured");
    };
    let ?pending = Map.get(pendingCalendarFlows, Principal.compare, caller) else {
      Runtime.trap("No pending OAuth flow — call startCalendarOAuth first");
    };
    if (state != pending.state) {
      Runtime.trap("OAuth state did not match the pending Calendar flow");
    };
    Map.remove(pendingCalendarFlows, Principal.compare, caller);
    let connection = await* LibCalendar.exchangeCode(
      calendarConfig.clientId, calendarConfig.clientSecret, code,
      pending.redirectUri, pending.codeVerifier,
    );
    Map.add(calendarConnections, Principal.compare, caller, connection);
  };

  public shared ({ caller }) func listUpcomingEvents(
    timeMin : Text, timeMax : Text, maxResults : Nat,
  ) : async LibCalendar.EventSummaryList {
    if (caller.isAnonymous()) {
      Runtime.trap("Sign in to list events");
    };
    let ?connection = Map.get(calendarConnections, Principal.compare, caller) else {
      Runtime.trap("Connect your Google Calendar first");
    };
    await* LibCalendar.listUpcomingEvents(
      calendarConfig.clientId, calendarConfig.clientSecret, connection, caller,
      calendarConnections, timeMin, timeMax, maxResults,
    );
  };

  public shared ({ caller }) func createEvent(
    summary : Text, startDateTime : Text, endDateTime : Text,
  ) : async Text {
    if (caller.isAnonymous()) {
      Runtime.trap("Sign in to create events");
    };
    let ?connection = Map.get(calendarConnections, Principal.compare, caller) else {
      Runtime.trap("Connect your Google Calendar first");
    };
    await* LibCalendar.createEvent(
      calendarConfig.clientId, calendarConfig.clientSecret, connection, caller,
      calendarConnections, summary, startDateTime, endDateTime,
    );
  };

  public shared ({ caller }) func disconnectMyCalendar() : async () {
    if (caller.isAnonymous()) {
      Runtime.trap("Sign in to disconnect");
    };
    Map.remove(calendarConnections, Principal.compare, caller);
  };
};
```

```motoko filepath=src/backend/lib/calendar.mo
import Array "mo:core/Array";
import Error "mo:core/Error";
import Map "mo:core/Map";
import Nat64 "mo:core/Nat64";
import Principal "mo:core/Principal";
import PureMap "mo:core/pure/Map";
import Runtime "mo:core/Runtime";
import Text "mo:core/Text";
import OAuth "mo:google-oauth/OAuth";
import DateTime "mo:google-oauth/DateTime";
import { calendar_events_list; calendar_events_insert } "mo:googlecalendar-client/Apis/EventsApi";
import { calendar_freebusy_query } "mo:googlecalendar-client/Apis/FreebusyApi";
import { type Event; JSON = Event } "mo:googlecalendar-client/Models/Event";
import { type EventDateTime; JSON = EventDateTime } "mo:googlecalendar-client/Models/EventDateTime";
import { type Events; JSON = Events } "mo:googlecalendar-client/Models/Events";
import { type FreeBusyRequest; JSON = FreeBusyRequest } "mo:googlecalendar-client/Models/FreeBusyRequest";
import { type FreeBusyRequestItem; JSON = FreeBusyRequestItem } "mo:googlecalendar-client/Models/FreeBusyRequestItem";
import { type FreeBusyResponse } "mo:googlecalendar-client/Models/FreeBusyResponse";
import { defaultConfig; type Config } "mo:googlecalendar-client/Config";

module {
  public type CalendarConnection = {
    accessToken : Text;
    refreshToken : Text;
  };

  public type PendingOAuth = {
    codeVerifier : Text;
    redirectUri : Text;
    state : Text;
  };

  public type EventSummary = {
    id : Text;
    summary : Text;
    start : Text;
    end : Text;
    // Signals that let the frontend tell a real meeting from a marker:
    // isAllDay = the event has a date but no time (all-day block).
    // transparency = "transparent" (shows as free) or "opaque"/"" (busy).
    // eventType = "default" | "outOfOffice" | "focusTime" | "workingLocation".
    // To count/show only real meetings, keep timed, opaque, default events.
    isAllDay : Bool;
    transparency : Text;
    eventType : Text;
  };

  public type EventSummaryList = [EventSummary];

  let SCOPES : Text = "https://www.googleapis.com/auth/calendar";

  func configForToken(token : Text) : Config {
    {
      defaultConfig with
      auth = ?#bearer(token);
      is_replicated = ?false;
      max_response_bytes = ?Nat64.fromNat(2_000_000);
    };
  };

  func refreshIfNeeded(
    clientId : Text, clientSecret : Text, connection : CalendarConnection,
    caller : Principal, calendarConnections : Map.Map<Principal, CalendarConnection>,
    errorMsg : Text,
  ) : async* ?Text {
    if (not (errorMsg.contains(#text("401")) or errorMsg.contains(#text("Unauthorized")))) {
      Runtime.trap("Calendar API failed: " # errorMsg);
    };
    let refreshed = await OAuth.refreshAccessToken(clientId, clientSecret, connection.refreshToken);
    let newToken = accessTokenOf(refreshed, "Token refresh");
    Map.add(calendarConnections, Principal.compare, caller, {
      connection with accessToken = newToken;
    });
    ?newToken;
  };

  public func startAuthorize(
    clientId : Text, redirectUri : Text, caller : Principal,
    pendingFlows : Map.Map<Principal, PendingOAuth>,
  ) : async* Text {
    let codeVerifier = await OAuth.generateCodeVerifier();
    let state = await OAuth.generateCodeVerifier();
    Map.add(pendingFlows, Principal.compare, caller, {
      codeVerifier;
      redirectUri;
      state;
    });
    OAuth.buildAuthorizeUrl(clientId, redirectUri, SCOPES, state, OAuth.computeCodeChallenge(codeVerifier));
  };

  public func exchangeCode(
    clientId : Text, clientSecret : Text, code : Text,
    redirectUri : Text, codeVerifier : Text,
  ) : async* CalendarConnection {
    let tokens = await OAuth.exchangeAuthorizationCode(clientId, clientSecret, code, redirectUri, codeVerifier);
    let accessToken = accessTokenOf(tokens, "Token exchange");
    let refreshToken = tokens.refreshToken
      ?? Runtime.trap("Token exchange failed: missing refresh_token");
    { accessToken; refreshToken };
  };

  func accessTokenOf(tokens : OAuth.TokenResponse, operation : Text) : Text {
    switch (tokens.error) {
      case (?error) {
        let description = switch (tokens.errorDescription) {
          case (?value) ": " # value;
          case null "";
        };
        Runtime.trap(operation # " failed: " # error # description);
      };
      case null {};
    };
    tokens.accessToken ?? Runtime.trap(operation # " failed: missing access_token");
  };

  // Lists events in [timeMin, timeMax). Pass timeMax = "" for an open-ended
  // "everything from now" list; pass both to bound a single day/week (e.g.
  // timeMin = start-of-tomorrow, timeMax = start-of-day-after) so the count is
  // exact. Both are RFC 3339 strings; include an offset ("…Z" or "…+02:00").
  public func listUpcomingEvents(
    clientId : Text, clientSecret : Text, connection : CalendarConnection,
    caller : Principal, calendarConnections : Map.Map<Principal, CalendarConnection>,
    timeMin : Text, timeMax : Text, maxResults : Nat,
  ) : async* EventSummaryList {
    if (timeMin.size() == 0) {
      Runtime.trap("timeMin must be an RFC 3339 timestamp");
    };
    let events : Events = try {
      await* calendar_events_list(
        configForToken(connection.accessToken), "primary", ?#json,
        "", "", "", false, "", "",
        false, [], "", 10, maxResults, ?#starttime,
        "", [], "", [], false, false, true, "",
        timeMax, timeMin, "", "",
      );
    } catch e {
      let ?newToken = await* refreshIfNeeded(
        clientId, clientSecret, connection, caller, calendarConnections, e.message(),
      ) else Runtime.trap("Calendar API failed");
      await* calendar_events_list(
        configForToken(newToken), "primary", ?#json,
        "", "", "", false, "", "",
        false, [], "", 10, maxResults, ?#starttime,
        "", [], "", [], false, false, true, "",
        timeMax, timeMin, "", "",
      );
    };
    eventSummariesOf(events);
  };

  // Availability uses FreeBusy (POST + JSON body), NOT events.list: one call
  // returns the merged busy intervals across the user's calendars with recurring
  // events already expanded server-side — no paging, recurrence expansion, or
  // client-side merging. Returns the owner's busy intervals in [timeMin, timeMax]
  // as raw RFC 3339 (start, end) pairs; timeMin/timeMax are UTC "…Z" strings.
  // Single-refresh-on-401 retry.
  public func busyTimes(
    clientId : Text, clientSecret : Text, connection : CalendarConnection,
    caller : Principal, calendarConnections : Map.Map<Principal, CalendarConnection>,
    timeMin : Text, timeMax : Text,
  ) : async* [(Text, Text)] {
    let request : FreeBusyRequest = {
      FreeBusyRequest.init {} with
      timeMin = ?timeMin;
      timeMax = ?timeMax;
      items = ?[{ FreeBusyRequestItem.init {} with id = ?"primary" }];
    };
    let response : FreeBusyResponse = try {
      await* calendar_freebusy_query(
        configForToken(connection.accessToken), ?#json, "", "", "", false, "", "", request,
      );
    } catch e {
      let ?newToken = await* refreshIfNeeded(
        clientId, clientSecret, connection, caller, calendarConnections, e.message(),
      ) else Runtime.trap("Calendar API failed");
      await* calendar_freebusy_query(
        configForToken(newToken), ?#json, "", "", "", false, "", "", request,
      );
    };
    // The response map is keyed by the RESOLVED calendar id (the user's email),
    // NOT "primary". Iterate EVERY returned calendar and union its busy periods.
    var busy : [(Text, Text)] = [];
    switch (response.calendars) {
      case (?calendars) {
        for ((_id, cal) in calendars.entries()) {
          switch (cal.busy) {
            case (?periods) {
              for (p in periods.values()) {
                switch (p.start, p.end) {
                  case (?s, ?e) busy := Array.concat(busy, [(s, e)]);
                  case _ {};
                };
              };
            };
            case null {};
          };
        };
      };
      case null {};
    };
    busy;
  };

  // --- Availability math (re-exported from google-oauth's tested DateTime) ---
  //
  // Do NOT re-implement RFC 3339 parsing — a digit parse that forgets to subtract
  // '0' (48) reads "2026" as 55354, so busy intervals land in the wrong year and
  // availability breaks silently (compiles, never traps). These thin re-exports
  // let callers use `LibCalendar.isSlotFree` / `.rfc3339ToNanos` with no extra
  // import; the implementation lives in `mo:google-oauth/DateTime`.
  public func rfc3339ToNanos(s : Text) : Int = DateTime.rfc3339ToNanos(s);
  public func nanosToRfc3339(ns : Int) : Text = DateTime.nanosToRfc3339(ns);
  public func overlaps(aStart : Int, aEnd : Int, bStart : Int, bEnd : Int) : Bool =
    DateTime.overlaps(aStart, aEnd, bStart, bEnd);
  public func isSlotFree(slotStart : Int, slotEnd : Int, busy : [(Text, Text)]) : Bool =
    DateTime.isSlotFree(slotStart, slotEnd, busy);

  public func createEvent(
    clientId : Text, clientSecret : Text, connection : CalendarConnection,
    caller : Principal, calendarConnections : Map.Map<Principal, CalendarConnection>,
    summary : Text, startDateTime : Text, endDateTime : Text,
  ) : async* Text {
    let start : EventDateTime = { EventDateTime.init {} with dateTime = ?startDateTime };
    let end : EventDateTime = { EventDateTime.init {} with dateTime = ?endDateTime };
    let event : Event = { Event.init {} with
      summary = ?summary;
      start = ?start;
      end = ?end;
    };
    let created : Event = try {
      await* calendar_events_insert(
        configForToken(connection.accessToken), "primary", ?#json,
        "", "", "", false, "", "",
        0, 10, true, ?#all, false, event,
      );
    } catch e {
      let ?newToken = await* refreshIfNeeded(
        clientId, clientSecret, connection, caller, calendarConnections, e.message(),
      ) else Runtime.trap("Calendar API failed");
      await* calendar_events_insert(
        configForToken(newToken), "primary", ?#json,
        "", "", "", false, "", "",
        0, 10, true, ?#all, false, event,
      );
    };
    created.id ?? "";
  };

  func eventSummariesOf(events : Events) : EventSummaryList {
    let items = events.items ?? [];
    Array.map<Event, EventSummary>(items, func(e : Event) : EventSummary = {
      id = e.id ?? "";
      summary = e.summary ?? "(no title)";
      start = switch (e.start) {
        case (?dt) dt.dateTime ?? dt.date ?? "";
        case null "";
      };
      end = switch (e.end) {
        case (?dt) dt.dateTime ?? dt.date ?? "";
        case null "";
      };
      // All-day events carry `date` but no `dateTime`.
      isAllDay = switch (e.start) {
        case (?dt) switch (dt.dateTime) { case (?_) false; case null true };
        case null false;
      };
      transparency = e.transparency ?? "";
      eventType = e.eventType ?? "";
    });
  };
};
```

## 4b. 可用性 / 忙碌时间 — 使用 FreeBusy，而不是 events.list

任何“这个人什么时候有空/忙”，预订或 Calendly 风格的功能都必须通过 **FreeBusy** (`calendar_freebusy_query`) 读取可用性，而不是 `calendar_events_list`。FreeBusy 是专门为此目的设计的：单个 POST 返回用户所有日历的**合并忙碌时间段**，重复事件已在服务器端展开——你永远不会分页浏览事件、展开重复项或在客户端合并重叠块。它还包含了休息时间和全天块。将 `calendar_events_list` 保留用于显示应用程序自己的事件列表，以及 `_insert` / `_delete` 用于事件 CRUD。

`lib/calendar.mo` 块中的 `busyTimes` 辅助函数是参考实现：它为 `items = [{ id = "primary" }]` 在 `[timeMin, timeMax]` 上构建 `FreeBusyRequest`，执行单次 401 刷新重试，并且——关键的是——迭代返回的**每个**日历（响应的映射键是解析后的日历 ID，而不是 `"primary"`）并合并它们的忙碌时间段。

**在比较**每个 `(start, end)` 与候选时间段之前，将其解析为绝对时刻，同时尊重末尾的偏移量——Google 返回的时间段带有 `Z` **或** 数字偏移量 (`2026-07-21T14:00:00+02:00`)，全天块为裸 `YYYY-MM-DD` 日期。在秒处截断并忽略偏移量会使每个忙碌时间段偏移（例如，苏黎世的夏季偏移 2 小时），因此忙碌块会错过它们应该隐藏的时间段。使用 `LibCalendar.rfc3339ToNanos`（`mo:google-oauth/DateTime` 的测试重导出）——它尊重偏移量并处理全天日期——然后数值重叠。**不要**手动编写一个在秒处停止的解析器。

端到端，整个可用性流程都存在于纳秒时刻，并且仅在边缘处理文本：用 `LibCalendar.rfc3339ToNanos` 锚定窗口，用纯整数算术构建候选网格，用 `LibCalendar.isSlotFree` 过滤，然后将幸存者用 `LibCalendar.nanosToRfc3339` 格式化，以便它们可以准备显示并直接传递给 `createEvent`（其 `startDateTime` / `endDateTime` 是 RFC 3339 文本）。下方的网格是一个固定的 UTC 窗口；实际的工作时间/时区策略是应用程序特定的，但解析→整数数学→格式化的形状是相同的：

```motoko
func availableSlots(
  clientId : Text, clientSecret : Text, connection : LibCalendar.CalendarConnection,
  caller : Principal, calendarConnections : Map.Map<Principal, LibCalendar.CalendarConnection>,
  windowStart : Text,   // 例如 "2026-07-21T09:00:00Z"
  slotCount : Nat,      // 要考虑的连续时间段数量
  slotMinutes : Nat,    // 时间段长度，例如 30
) : async* [(Text, Text)] {
  let slotNs = slotMinutes * 60 * 1_000_000_000;
  let start0 = LibCalendar.rfc3339ToNanos(windowStart);
  // 候选网格 [s, s+slot) 时刻。
  let candidates = Array.tabulate<(Int, Int)>(slotCount, func(i) {
    let s = start0 + i * slotNs;
    (s, s + slotNs);
  });
  let windowEnd = start0 + slotCount * slotNs;
  let busy = await* LibCalendar.busyTimes(
    clientId, clientSecret, connection, caller, calendarConnections,
    windowStart, LibCalendar.nanosToRfc3339(windowEnd),
  );
  let free = Array.filter<(Int, Int)>(candidates, func(s) = LibCalendar.isSlotFree(s.0, s.1, busy));
  Array.map<(Int, Int), (Text, Text)>(
    free, func(s) = (LibCalendar.nanosToRfc3339(s.0), LibCalendar.nanosToRfc3339(s.1)),
  );
};
```

## 5. 可用的 API 表面

### 0.2.0 对可选枚举参数是破坏性变更

可选枚举**查询**参数现在为 `?T` 而不是裸 `T`，以便 `null` 表示“从线中省略”——以前它们总是发送，这正是生成器可选参数规范化要解决的问题。传递此类参数的每个调用位置都需要一个 `?`：

```mo:googlecalendar-client
// 0.1.x
await* calendar_events_list(cfg, "primary", #json, …, #starttime, …);
// 0.2.0
await* calendar_events_list(cfg, "primary", ?#json, …, ?#starttime, …);
```

受影响的参数包括每个操作上的 `alt`，`events.list` 上的 `orderBy`，以及 `events.insert` / `events.update` / `events.delete` 上的 `sendUpdates`。非枚举参数未更改：空的 `Text` 和 `0` 仍然表示“省略”。下面的示例使用了新形式。

### 自 0.2.0 以来有两种调用风格

0.2.0 添加了 `src/Client.mo`，一个嵌套类封装，按日历的点操作 ID 分组操作，就像 googledrive 一样：

```mo:googlecalendar-client
import { Client } "mo:googlecalendar-client/Client";

let cal = Client({ defaultConfig with auth = ?#bearer accessToken });

// events.insert 需要 14 个参数；`alt` 和 `sendUpdates` 是可选枚举。
let created = await cal.events.insert(
  calendarId, ?#json, "", "", "", false, "", "",
  0, 1, false, null, false, event);

// 注意 `query_`，不是 `query`——`query` 是 Motoko 关键字，因此生成器会转义它。
let busy = await cal.freebusy.query_(?#json, "", "", "", false, "", "", request);
```

资源包括 `acl`、`calendarList`、`calendars`、`channels`、`colors`、`events`、`freebusy` 和 `settings`。

在选择风格时，需要了解以下两点：

- 外观（facade）在构造时绑定一次 `Config`，因此 `shared` 方法进行多个日历调用时不会在每个调用中传递它；
- 外观（facade）方法是 `async`，而扁平的 `Apis/*.mo` 自由函数是 `async*`。在 `async*` 辅助函数内部，外观（facade）添加了一个额外的 `await` 边界，因此 §4 中的混入布局保持在扁平形式。

外观（facade）是 **可叠加的** — 没有移除任何扁平的入口点 — 但这并不意味着 0.1.x 代码可以未经修改地编译：上面提到的可选枚举签名更改也适用于扁平函数。在升级时，无论使用哪种风格，都需要在这些调用位置添加 `?`。

### `google-oauth`（OAuth 2.0 机制）

| 函数 | 目的 |
| --- | --- |
| `OAuth.urlEncode(text)` | RFC 3986 百分号编码，用于表单体 |
| `OAuth.parseTokenResponse(text)` | 解析 Google 令牌端点 JSON |
| `OAuth.exchangeAuthorizationCode(...)` | 用授权码交换令牌 |
| `OAuth.refreshAccessToken(...)` | 刷新过期访问令牌 |
| `OAuth.generateCodeVerifier()` | 生成 PKCE `code_verifier`（链上随机性） |
| `OAuth.computeCodeChallenge(verifier)` | 计算 PKCE `code_challenge`（S256） |
| `OAuth.buildAuthorizeUrl(...)` | 构建Google OAuth 授权 URL |
| `OAuth.getUserEmail(accessToken)` | 通过 OIDC userinfo 获取连接的电子邮件（只需要 `openid email`） |

### 可用性数学（`LibCalendar` 重新导出的 `mo:google-oauth/DateTime`）

`lib/calendar.mo` 重新导出这些经过测试的辅助函数，因此可以像 `LibCalendar.*` 这样调用，无需额外的导入。时间是以自 Unix 纪元以来的绝对纳秒为单位的，与 `Time.now()` 匹配。

| 函数 | 目的 |
| --- | --- |
| `LibCalendar.rfc3339ToNanos(text)` | 偏移量感知的 RFC 3339 -> 纳秒（尊重 `Z` / `±HH:MM`，裸日期） |
| `LibCalendar.nanosToRfc3339(ns)` | 纳秒 -> UTC RFC 3339 文本（`…Z`），准备好用于 `createEvent` |
| `LibCalendar.overlaps(aStart, aEnd, bStart, bEnd)` | 半开区间重叠测试 |
| `LibCalendar.isSlotFree(slotStart, slotEnd, busy)` | 时间段没有每个 `(start, end)` RFC 3339 忙碌对 |

### `googlecalendar-client`（日历 REST API v3）

上述规范化的参与者有意仅实现即将到来的事件列表和事件创建；对于可用性/忙碌时间，请使用 §4b 中的 FreeBusy 辅助函数。对于另一个生成的操作，保持 `bearer` 认证和 `is_replicated = ?false`，然后应用与 `refreshIfNeeded` 相同的单次刷新重试模式。

生成的包还公开了：

| 函数 | 模块 | 目的 |
| --- | --- | --- |
| `calendar_events_list` | EventsApi | 列出日历上的事件 |
| `calendar_events_get` | EventsApi | 通过 ID 获取事件 |
| `calendar_events_insert` | EventsApi | 创建事件 |
| `calendar_events_update` | EventsApi | 更新事件（PUT） |
| `calendar_events_patch` | EventsApi | 补丁事件（PATCH） |
| `calendar_events_delete` | EventsApi | 删除事件 |
| `calendar_events_move` | EventsApi | 将事件移动到另一个日历 |
| `calendar_events_quickAdd` | EventsApi | 从文本创建事件（"午餐在中午"） |
| `calendar_events_instances` | EventsApi | 列出重复事件的单例 |
| `calendar_freebusy_query` | FreebusyApi | 检查跨日历的可用性/忙碌 |
| `calendar_calendarList_list` | CalendarListApi | 列出用户的日历 |
| `calendar_calendarList_get` | CalendarListApi | 获取日历列表条目 |
| `calendar_calendars_get` | CalendarsApi | 获取日历元数据 |
| `calendar_calendars_insert` | CalendarsApi | 创建次要日历 |

## 6. 周期和响应大小

`google-oauth` 库使用 `Call.httpRequest` 从 `mo:ic/Call`，它通过 `ic0.cost_http_request` 系统 API 自动计算并附加所需的精确周期。对于令牌交换或刷新调用，不需要手动周期预算。

对于 `googlecalendar-client` 调用，`defaultConfig.cycles = 30_000_000_000`（30B）。典型的列表/插入大约消耗 ~10–15B 周期。对于可能包含大型有效负载的事件列表读取，设置 `max_response_bytes = ?2_000_000`。

## 7. 会咬你的事情

- **`is_replicated = ?false`** — 见 §3。不可协商。
- **Google 刷新令牌不会轮换。** 与 X/Twitter 不同，Google 不会在每次刷新时发出新的 `refresh_token`。保留原始的 `refresh_token`，仅持久化新的 `access_token`。
- **访问令牌在 1 小时后过期。** `refreshIfNeeded` 辅助函数捕获 HTTP 401，通过 `google-oauth.refreshAccessToken` 静默刷新，并重试一次。如果刷新也失败，则显示“重新连接您的帐户”。
- **回调 URI 精确匹配。** 授权 URL 和重定向之间的每个字符（尾随斜杠、查询字符串、端口）必须匹配。否则，Google 会返回 `redirect_uri_mismatch`。使用固定的 `window.location.origin + "/connect/calendar"` 作为 `redirectUri` — 这是设置页面显示的相同值，也是 `/connect/calendar` 路由拥有的值 — 并在 Google Web 客户端上注册该精确 URI。不要从 `window.location.pathname` 构建，它因页面而异。
- **将显示的值不变地传递给 `startCalendarOAuth` — 永远不要传递原始的 `*.icp0.io` canister URL。** Caffeine 应用程序在多个原点提供服务（`*-draft.caffeine.xyz` 草稿、`*.caffeine.xyz` 活动域和原始的 `<canister-id>.icp0.io` URL）。在一个共享辅助函数中计算重定向 URI（`window.location.origin + "/connect/calendar"`），并使用相同的辅助函数，既用于设置页面上的可复制字段，也用于传递给 `startCalendarOAuth`。如果传递给 Google（通过 `startCalendarOAuth`）的值与设置页面显示的和管理员注册的值不同 — 例如，构建时/配置值或 `*.icp0.io` canister 原点 — Google 会返回 `redirect_uri_mismatch`。
- **RFC 3339 时间戳。** 日历使用 RFC 3339 字符串（`2026-07-10T15:00:00-07:00`）。对于全天事件，设置 `EventDateTime.date`（`YYYY-MM-DD`）而不是 `dateTime`。
- **`createEvent` 时间需要一个时区。** 传递给 `createEvent` 的 `dateTime` 必须包含 UTC 偏移（`…Z` 或 `…+02:00`）或您必须设置 `EventDateTime.timeZone`（IANA 名称，如 `"Europe/Zurich"`）。一个没有 `…Z` 或 `…+02:00` 的裸 `2026-07-10T15:00:00` 会被 Google 拒绝。最好发送一个偏移量限定字符串，以便事件在预期的墙上时间到达。
- **`calendarId = "primary"`** 引用经过身份验证用户的默认日历。命名/共享日历使用它们的日历 ID（类似电子邮件的地址）。
- **可用性 = FreeBusy，不是 `events.list`。** 对于“我有空/忙碌吗”使用 `calendar_freebusy_query`（§4b）：一个 POST 返回合并的忙碌间隔，并服务器端展开重复事件。从 `events.list` 重建可用性意味着分页、展开重复事件、手动合并重叠 — 容易出错，并且是“预订链接显示我空闲时我实际上在忙碌”的经典原因。
- **`maxAttendees` 和 `maxResults` 必须≥ 1。** Google 会用 HTTP 400 拒绝 `maxAttendees=0` / `maxResults=0`（文档中规定的最小值是 1）。`listUpcomingEvents` 和 `createEvent` 配方传递 `maxAttendees = 10`；在任何事件端点都不传递 `0`。
- **FreeBusy 响应按 *解析后的* 日历 ID 键控，而不是您查询的字符串。** 当您调用 `calendar_freebusy_query` 为 `"primary"` 时，Google 解析它并返回按真实日历 ID（用户的电子邮件地址）键控的 `calendars` 映射，**不是**字面值 `"primary"`。不要在响应中查找 `"primary"` — 那会找不到任何内容并使每个时间段看起来都是空闲的（一个常见的可用性错误）。相反，迭代响应返回的**每个**日历并联合它们的 `busy` 间隔，然后从候选时间段中减去这些。将每个间隔的 `start`/`end` 解析为 RFC 3339，允许尾随 `Z` 或数字偏移（`+02:00`）；比较瞬间，而不是原始字符串。
- **使用 `LibCalendar.rfc3339ToNanos`（重新导自 `mo:google-oauth/DateTime`）解析 RFC 3339 — 不要重新实现它。** 手动编写的解析器忘记每个数字减去 `'0'`（48），会将 `"2026"` 读取为 `55354`，因此每个忙碌间隔都会落在错误的年份，重叠检查永远不会匹配，可用性会无声地出错 — 代码仍然可以编译并且永远不会捕获，因此错误在用户双重预订之前是看不见的。使用经过测试的辅助函数。
- **HTTP 429 速率限制。** 向调用者显示错误；永远不要在 canister 内部静默重试写入 — 重试可能会创建重复事件。
- **不要暴露访问令牌。** `calendarConnections` 仅由 API 调用内的 `Map.get(calendarConnections, ..., caller)` 读取。没有 `getMyCalendarConnection`，没有 `getMyAccessToken`，没有迭代器。泄露的 bearer 是每个用户帐户的妥协。
- **所有 Calendar API v3 调用使用 `alt = ?#json`（在 0.2.0 之前是裸的 `#json`）。** 留下可选字符串参数 `""` 和 `prettyPrint = false`。
- **查询参数是位置性的，并且自 0.2.0 起，可选的 *枚举* 参数是 `?T`。** 将 `Text` 作为 `""`，`Bool` 作为 `false`，`Nat` 作为实际数字（尊重每个文档中规定的最小值：`maxAttendees` / `maxResults` 必须≥ 1），并将可选枚举作为 `?#json` / `?#starttime` / `?#all` — 或者 `null` 以省略它们，这就是 `?` 的作用。非枚举参数仍然不接受 `null`。模型值（`Event`、`EventDateTime`、`FreeBusyRequest`）直接传递，与之前相同。
- **组合 Gmail + Calendar 应用：请求作用域的并集，并通过 `OAuth.getUserEmail` 学习地址。** `openid email` + `.../calendar` + `.../gmail.send` 的并集覆盖可用性、发送和连接的地址（通过 OIDC userinfo） — 不需要 `gmail.readonly`，除非应用程序实际读取邮件。合并配方时永远不要丢弃作用域 — 见“组合 Gmail + Calendar 应用”。
- **使用 `init {}` 构建 `Event` / `EventDateTime`，然后记录更新** 您需要的字段 — 所有字段都是可选的（`?T`）；将其他字段保留为 null。
- **PATCH/PUT/DELETE 在生成的客户端中是强制非复制的**（`googlecalendar-client` 自动在这些方法上设置 `is_replicated = ?false`）。对于 GET/POST，在您的 `Config` 中显式设置它。

# 前端

使用此技能的每个构建必须提供以下四个项目。 （如果应用程序**还**使用 Gmail 连接器，请按照下面的“组合 Gmail + Calendar 应用”代替 — 它用 `/settings/calendar` + `/connect/calendar` 替换为 `/settings/google` + `/connect/google`。下面的要求仍然适用；只有两个路径会改变。）这些是**验收标准，不是建议** — 在构建完成前验证每个。这三个是构建跳过的要求，任何缺失都会使连接**损坏，而不仅仅是未完成**：

- **凭据页面存在并可访问。** 应用程序必须具有 `/settings/calendar` 页面，其中包含 Client ID/Secret 输入（项目 2），并且必须有一个经过身份验证的管理员可以访问它 — 通过导航链接或在连接页面上的未配置提示。没有页面可以输入凭据的“连接 Google 日历”按钮是最常见的失败，并且使连接器无法使用。
- **管理员设置页面显示字面值、可复制的重定向 URI。** 不是 `<your-domain>` 占位符，不是“应用程序 URL + /connect/calendar”作为管理员要组装的文本 — 实际字符串 `window.location.origin + "/connect/calendar"` 渲染为管理员可以复制的只读字段。具体来说：如果应用程序从 `https://my-app.caffeine.xyz` 提供，显示的值是 `https://my-app.caffeine.xyz/connect/calendar`，并且没有其他内容。没有它，管理员无法在 Google 中注册 URI，并且每个连接都会失败。
- **`/connect/calendar` 是一个处理 Google 回调的真实路由 — 不是一个只有按钮的页面。** 如果它落入到捕获所有/主页重定向，或者在经过身份验证的参与者准备好之前调用 `completeCalendarOAuth`，连接会无声地失败，并且应用程序会显示“未连接”。

1. **一个登录流程 — 必须的。** 日历无法在没有非匿名调用者的情况下工作；每个用户的 OAuth 握手存储按 `caller : Principal` 键控的令牌，并且管理员凭据设置基于 `#admin`。登录流程来自 [`extension-authorization`](../extension-authorization/SKILL.md)：`useInternetIdentity`，登录/注销按钮，将经过身份验证的身份注入到每个后端调用的 `useActor` 管道。

2. **一个管理员设置页面** — `/settings/calendar`（管理员门控）。此页面是必需的；没有它，日历构建是不完整的：
   - 在凭据输入之前显示一个“如何获取您的 Google 凭据”面板。向管理员保证这是一个一次性操作，大约需要 5 分钟设置，并逐步引导这些编号步骤（代理的完成消息必须重复相同的步骤）：
     1. 打开 [Google Cloud Console](https://console.cloud.google.com) 并使用任何 Google 帐户登录；
     2. 创建或选择一个项目；
     3. 启用 **Google Calendar API**（APIs & Services → Library → 搜索 "Google Calendar API" → 启用）；
     4. 配置 **OAuth consent screen**（APIs & Services → OAuth consent screen → **External**；设置应用名称、支持电子邮件、开发者电子邮件；Google 的默认作用域是合适的）；
     5. 创建一个类型为 **Web application** 的 **OAuth client ID**（APIs & Services → Credentials → Create Credentials → OAuth client ID）；
     6. 在 **Authorized redirect URIs** 下，添加此页面可复制字段中的确切值；
     7. 复制生成的 **Client ID** 和 **Client Secret** 并保存到下面的输入中。
     包含一个方便的链接，可以打开 Google Cloud Console。
   - 使用一个共享辅助函数将实际 URI 渲染为只读、可复制的字段：
     `const calendarRedirectUri = () => window.location.origin + "/connect/calendar";`。
     例如，如果应用程序在 `https://my-app.caffeine.xyz` 上打开，显示的值是 `https://my-app.caffeine.xyz/connect/calendar`。永远不要只显示 `<app-domain>` 或要求管理员推断 URI。
   - 两个绑定到 `setCalendarCredentials(clientId, clientSecret)` 的密码输入。
     按回车键提交；成功后清除输入。
   - 由 `isCalendarConfigured()`（返回 `Bool`）驱动的状态指示器。
     显示“已配置” / “未配置” — 永远不要显示凭据。
   - **使此页面可访问。** 应用程序的主导航（共享的 Layout）必须链接到此页面供管理员使用 — 当 `isCallerAdmin` 为 true 时显示该链接，否则隐藏它（通过
     [`extension-authorization`](../extension-authorization/SKILL.md)）。在定义导航的位置添加该链接，而不是在此页面内部。没有到达它的 `/settings/calendar` 路由是一个损坏的构建。不要依赖导航：未配置提示是用户发现需要设置的主要方式。

3. **“连接日历”页面和回调页面** — `/connect/calendar`（任何已登录用户）。此专用页面必须捕获和处理 Google 在同意后的重定向；它不仅是一个带有连接按钮的页面：
   - **处理所有人的未配置情况。** `isCalendarConfigured()` 是一个公共查询（任何已登录用户都可以调用它）。当它返回 `false` 时，不要显示一个无用的连接按钮。管理员会看到一个指向 `/settings/calendar` 的链接以输入凭据。非管理员必须看到一个说明，而不是一个死胡同——例如，“Google 日历尚未设置——应用程序管理员需要在设置中添加 Google 凭据。”仅在配置完成后启用“连接 Google 日历”按钮。
   - “连接 Google 日历”按钮绑定到 `startCalendarOAuth(calendarRedirectUri())`。将浏览器重定向到 canister 返回的 URL。不要从任意当前路径名派生回调；固定的 `/connect/calendar` 路由和设置页面的 URI 必须相同。
   - 将 `/connect/calendar` 注册为真正的应用程序路由。它必须捕获 Google 回调，并且在处理它之前不能重定向到通用重定向、布局默认值或主页。
   - 在返回途中，从 `URLSearchParams` 中读取 `error`、`code` 和 `state`。如果 `error` 存在，则显示连接失败/拒绝的状态，并且不要调用 canister。只有当 `code` 和 `state` 都存在时，才调用并**等待** `completeCalendarOAuth(code, state)`，然后再导航到任何地方或清除 URL。在它挂起时保持可见的“正在连接 Google 日历…”状态。不要首先替换路由、重定向到主页或丢弃查询参数——那样会丢失一次性代码并让用户断开连接。
   - **在调用一次性回调之前等待 actor 就绪。** 页面必须等待 `useInternetIdentity().isAuthenticated` 和 `useActor(createActor)` 提供非空、非获取的 actor，然后再调用 `completeCalendarOAuth`。在那之前不要设置 `startedRef`/一次性保护：第一次渲染时 actor 通常是不可用的，而“Actor 未就绪”失败否则会消耗唯一重试，而授权代码仍然在 URL 中。
   - 在任何最终路径之后，调用 `history.replaceState` 以移除 OAuth 查询参数。这可以防止页面刷新时重用一次性授权代码。
   - 状态由 `isMyCalendarConnected()`（返回 `Bool`）驱动。
   - 可选的“断开连接日历”按钮绑定到 `disconnectMyCalendar()`。

4. **日历 UI** — 主页面显示即将发生的事件。当 `isCalendarConfigured()` 为 `false` 且调用者是管理员时，渲染一个“设置 Google 日历”链接到 `/settings/calendar`，以便凭据页面可被发现，而不仅仅是可访问。将当前时间作为 RFC 3339 `timeMin` 值，`""` 作为开放式的 `timeMax`：`listUpcomingEvents(new Date().toISOString(), "", 10)`。要绑定单日（例如“明天的会议”），请传递两者——本地一天的开始和下一天的开始，每个都是 RFC 3339 并带有偏移——并且只计算 `isAllDay` 为 false 且 `transparency` 不是 `"transparent"` 且 `eventType` 为 `"default"` 的条目（这将过滤掉全天、空闲、外出和位置标记）。在使用 `singleEvents = true` 和 `orderBy = startTime` 时这是必需的。还包括一个“创建事件”表单。`datetime-local` 值没有偏移，因此在调用 actor 之前将每个浏览器本地值转换为 RFC 3339 瞬间：`createEvent(summary, new Date(startInput).toISOString(), new Date(endInput).toISOString())`。
   当 `isMyCalendarConnected()` 为 `false` 时，渲染一个内联“连接 Google 日历”链接到 `/connect/calendar`。

建议的路由布局：

```
/                   →  主 UI（即将发生的事件 + 创建表单）
/settings/calendar  →  管理员凭据配置（仅管理员）
/connect/calendar   →  按用户 OAuth 握手（任何已登录用户）
# 如果应用程序还使用 Gmail：删除上述两个路由，并使用单个
# /settings/google + /connect/google — 见“组合 Gmail + 日历应用程序”。
```

## 组合 Gmail + 日历应用程序

当应用程序使用两个连接器时，构建**一个**共享的 Google 连接，而不是两个（授权码是一次性的，所以两个流程将强制两个同意屏幕）。前端：

- **一个管理员页面 `/settings/google`** — 一个单一的 Client ID / Client Secret 表单、一个 `isGoogleConfigured` 状态和一个可复制的重定向 URI 字段，显示确切的 `window.location.origin + "/connect/google"`。
- **一个连接路由 `/connect/google`** — 与上述前端部分所需的相同真实回调路由：它渲染“连接 Google”，捕获重定向，等待 actor 就绪，然后调用完成一次。没有第二个回调路由。
- **不要构建** `/settings/gmail`、`/connect/gmail`、`/settings/calendar` 或 `/connect/calendar`。上述所有前端要求仍然适用——只有这些路径会更改。

后端——编写共享流程**一次**（它取代了每个连接器的 OAuth 流程）。它与每个连接器的 `startAuthorize` / `exchangeCode` / 刷新函数具有相同的形状，但有以下确切差异：

- 一个 `#admin`-门控的配置设置器存储单个 Client ID/Secret。
- `SCOPES` = 以下并集——两个 API 在一个同意中。
- `completeGoogleOAuth(code, state)` 通过 `OAuth.getUserEmail`（OIDC userinfo——只需要 `openid email`，不需要 `gmail.readonly`）学习连接的电子邮件地址，并将一个连接 `{ accessToken; refreshToken; emailAddress }` 存储在单个 `Map<Principal, GoogleConnection>` 中。
- Gmail 发送和日历调用各自构建**它们自己的**客户端 `Config` 从那个单一的 `accessToken`，每个都保持其单个 401 重试刷新。
- 将连接和客户端配置保存在**一个**共享状态值中，并将其作为参数传递给 Gmail 和日历混入，以便两者都读取和写入相同的连接（见 `writing-motoko` 混入规则）。

```motoko filepath=src/backend/google.mo
let SCOPES : Text =
  "openid email "                                    // 通过 userinfo 学习地址
  # "https://www.googleapis.com/auth/gmail.send "
  # "https://www.googleapis.com/auth/calendar";
// 仅当应用程序读取邮件时才添加 "https://www.googleapis.com/auth/gmail.readonly "。
```

将其作为**一个**由两个服务共享的连接进行连接——一次声明配置、连接映射和挂起流程映射，并将**相同的**绑定传递给每个混入。Gmail 和日历消息混入**不**声明它们自己的配置或连接；它们接收共享的 `googleConfig` 和 `googleConnections`（配置对于 401 重试刷新是必需的）：

```motoko filepath=src/backend/main.mo
actor {
  let accessControlState : AccessControl.AccessControlState;
  include MixinAuthorization(accessControlState, null);

  // 两个服务共享的单一凭据 + 连接状态。
  let googleConfig : { var clientId : Text; var clientSecret : Text };
  let googleConnections : Map.Map<Principal, Google.Connection>;
  let pendingGoogleFlows : Map.Map<Principal, Google.PendingOAuth>;

  include MixinGoogleConfig(accessControlState, googleConfig);                    // setGoogleCredentials / isGoogleConfigured (#admin-gated setter)
  include MixinGoogleOAuth(googleConfig, googleConnections, pendingGoogleFlows);  // startGoogleOAuth / completeGoogleOAuth, SCOPES = 上述并集
  include MixinGmailMessaging(googleConfig, googleConnections);                  // sendEmail — 401 重试需要配置；读取共享连接
  include MixinCalendarMessaging(googleConfig, googleConnections);               // 日历调用——相同的共享配置 + 连接
};
```

此变体的迁移链头取代了每个连接器的变体——注意共享连接携带 `emailAddress`：

<!-- motoko-check:skip -->
```motoko
import Map "mo:core/Map";
import AccessControl "mo:caffeineai-authorization/access-control";

module {
  type Connection = {
    accessToken : Text;
    refreshToken : Text;
    emailAddress : Text;
  };

  type PendingOAuth = {
    codeVerifier : Text;
    redirectUri : Text;
    state : Text;
  };

  type NewActor = {
    accessControlState : AccessControl.AccessControlState;
    googleConfig : { var clientId : Text; var clientSecret : Text };
    googleConnections : Map.Map<Principal, Connection>;
    pendingGoogleFlows : Map.Map<Principal, PendingOAuth>;
  };

  public func migration(_old : {}) : NewActor {
    {
      accessControlState = AccessControl.initState();
      googleConfig = { var clientId = ""; var clientSecret = "" };
      googleConnections = Map.empty<Principal, Connection>();
      pendingGoogleFlows = Map.empty<Principal, PendingOAuth>();
    };
  };
};
```

不要给 Gmail 和日历单独的配置/连接状态或单独的 OAuth 流程——一个授权码是一次性的，并且单独的状态会失同步（见 `writing-motoko` 混入规则）。

在单个 OAuth 客户端上启用两个 API，并仅注册单个 `.../connect/google` 重定向 URI。仅在用户明确要求连接两个不同的 Google 账户时才分成两个单独的面板。

## 所有变体通用的内容

- **登录是必需的**对于每个与日历相关的路由。将 `/settings/...` 和连接路由（`/connect/calendar`，或在组合应用程序中为 `/connect/google`）通过 [`extension-authorization`](../extension-authorization/SKILL.md) 的 auth 保护（`useInternetIdentity` + 当 `!isAuthenticated` 时重定向）。
- **前端从不持久化令牌。** 没有 `localStorage`，没有 `IndexedDB`，没有 cookie——canister 介导一切。浏览器只看到 `Bool` 状态标志和 OAuth 重定向 URL。
- **OAuth `state` 参数是由 canister 生成的并经过验证的。** Canister 存储一个随机的一次性数与挂起的验证器和回调 URI。前端必须将 `code` 和 `state` 都传递给完成调用（`completeCalendarOAuth`，或在组合应用程序中为 `completeGoogleOAuth`）；它从不创建或修改任何值。
- **日历 UI 很简单：** 一系列即将发生的事件，一个带有摘要 + 开始/结束 datetime 输入的创建事件表单。没有客户端 Google SDK，没有令牌处理，没有 JSON 序列化——canister 是日历客户端。

## 相关

- [`mops add googlecalendar-client@0.2.0`](https://mops.one/googlecalendar-client) — 日历 REST API v3 绑定。
- [`mops add google-oauth@0.2.1`](https://mops.one/google-oauth) — Google OAuth 2.0 库（令牌交换、刷新、PKCE、`getUserEmail` userinfo、`DateTime` RFC 3339 帮助程序）。
- [Google OAuth 2.0 for Web Server Applications](https://developers.google.com/identity/protocols/oauth2/web-server) — Web-client 重定向 URI 和授权码流程参考。
- [Google Calendar API v3 reference](https://developers.google.com/calendar/api/v3/reference) — `googlecalendar-client` 包装的内容。
- [RFC 7636 — Proof Key for Code Exchange](https://datatracker.ietf.org/doc/html/rfc7636) — PKCE 规范。
- [extension-authorization](../extension-authorization/SKILL.md) — **必需的先决条件**。提供 Internet Identity 登录、`useInternetIdentity` / `useActor` 前端管道，以及 `#admin` 角色门控。
- [connector-googlemail](../connector-googlemail/SKILL.md) — 使用相同 `google-oauth` 库的姐妹连接器用于 Gmail。
