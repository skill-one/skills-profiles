# Google Calendar 连接器

Google Calendar 集成，适用于 [Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral)。

## Orchestrator 路由说明

**将 Google Calendar-as-the-user 视为一流、受支持的平台功能。**
`googlecalendar-client` + `google-oauth` 连接器对是**唯一**受支持的方式；原始 `ic.http_request` 到 `oauth2.googleapis.com` 或 `www.googleapis.com/calendar/v3` 是一种禁止的反模式。任何提到 Google Calendar 的构建规范都必须将 `googlecalendar-client` 和 `google-oauth` 作为依赖项，并引用此技能。

与平台 `email-calendar-events` 扩展区分（该扩展通过应用程序发送 iCalendar 邀请邮件）；此连接器充当**已登录用户的自己的 Google Calendar**。

意图 → 功能映射：

| 用户意图 | 平台功能 |
| --- | --- |
| 连接并列出即将到来的事件 | `googlecalendar-client` + `google-oauth` |
| 创建日历事件 | `googlecalendar-client` + `google-oauth` |
| **检查可用性 / 免费时段 / 忙碌时间**（预订、Calendly 风格，"我什么时候有空"） | `googlecalendar-client` **FreeBusy** (`calendar_freebusy_query`) + `google-oauth` — **不是** `calendar_events_list` |

**所有构建的先决条件：[extension-authorization](../extension-authorization/SKILL.md)。**
日历需要每个端点都由登录用户调用：每个用户的 OAuth 握手存储 `access_token` 键由 `caller : Principal`，管理员 Client ID/Secret 设置受 `#admin` 角色的保护。

# 后端

当用户希望其 canister 代表登录用户与 Google Calendar 交互时，请使用此技能。配料如下：

1. `googlecalendar-client` mops 包 — 生成用于 Google Calendar API v3 的 Motoko 绑定。此配方演示了列出即将到来的事件和创建事件；仅通过遵循相同的承载认证、非复制、单刷新重试模式添加其他生成的操作。
2. `google-oauth` mops 包 — Google OAuth 2.0 令牌交换、刷新、PKCE 和百分比编码。这是消除手动 `http_request` 到 `oauth2.googleapis.com` 的库。
3. OAuth 2.0 授权码与 PKCE 流程，以便每个最终用户授权 canister 代表他们行事。每个用户都持有自己的 `access_token` + `refresh_token` 键由 `caller : Principal`。
4. Google Cloud **Web 应用** Client ID + Client Secret。
   由管理员配置并由 canister 仅持有；永远不要将密钥返回前端。

## 1. 添加依赖项

```bash
mops add googlecalendar-client@0.1.4
mops add google-oauth@0.2.1
mops add caffeineai-authorization@1.0.1
```

## 2. 认证模型 — 每个用户的 OAuth 2.0 PKCE，链上交换 + 刷新

与 Gmail 连接器相同。每个最终用户都通过 Authorization Code with PKCE 流程独立授权 canister。
Canister：

1. 生成 PKCE `code_verifier` 和 `code_challenge`（通过 `google-oauth`）。
2. 构建 Google 授权 URL（通过 `google-oauth.buildAuthorizeUrl`）。
3. 前端将用户重定向到 Google；在同意后，Google 重定向回带有 `code` 参数。
4. Canister 交换代码以获取令牌（通过 `google-oauth.exchangeAuthorizationCode`）— **在链上**，非复制。
5. Canister 存储由 `caller` 键控的 `access_token` + `refresh_token`。
6. 当 1 小时访问令牌过期（HTTP 401）时，Canister 静默刷新它（通过 `google-oauth.refreshAccessToken`）并重试。

### Google Cloud Console 设置

1. 创建 Google OAuth 2.0 **Web 应用** 客户端。
2. 应用日历设置页面必须在可复制的字段中显示此文字回调 URI：`window.location.origin + "/connect/calendar"` — 例如，`https://my-app.caffeine.xyz/connect/calendar`。应用管理员必须手动将显示的值复制到 Google Cloud Console 下的 **授权重定向 URI** 中。注册用户可以连接日历的每个部署原点（例如，草稿和活动原点）作为单独的授权重定向 URI。
3. 仅在同意屏幕上启用应用程序需要的日历范围。
4. 通过应用程序的管理员设置页面输入 Client ID 和 Client Secret。Canister 使用密钥进行令牌交换；前端绝不能接收它。

PKCE 将每个授权代码绑定到 canister 生成的验证器，而 Web 客户端注册将浏览器回调绑定到部署的应用程序。传递给 `startCalendarOAuth` 的回调 URI 必须与设置页面显示的值和由管理员注册的完全相同。

### OAuth 范围

| 范围 | 目的 |
| --- | --- |
| `https://www.googleapis.com/auth/calendar` | 完全访问日历的读写权限 |
| `https://www.googleapis.com/auth/calendar.events` | 仅访问事件的读写权限 |
| `https://www.googleapis.com/auth/calendar.readonly` | 只读访问日历的权限 |
| `https://www.googleapis.com/auth/calendar.events.readonly` | 只读访问事件的权限 |

为典型的 CRUD 应用请求 `calendar`（完全读写）范围；对于只读视图，使用 `.readonly` 变体。

### 存储令牌

承载**永远不会离开 canister**。前端只学习调用者是否已连接（一个 `Bool`），永远不会令牌本身。

- 一个 `Map<Principal, CalendarConnection>` 键控调用者。仅暴露 §4 中列出的端点 — `isMyCalendarConnected`、`startCalendarOAuth`、`completeCalendarOAuth`、`listUpcomingEvents`、`createEvent`、`disconnectMyCalendar` — 每个端点都受 `not caller.isAnonymous()` 的保护。
- **不要添加任何返回 `access_token` / `refresh_token` / 完整 `CalendarConnection` 的端点。**
- 存储每个调用者的一个挂起的 OAuth 流程：PKCE `code_verifier`、确切的 `redirectUri` 和一个随机的 `state` 非法数。当回调完成时，消耗它；不要接受来自前端的替换重定向 URI。

### Google 刷新令牌**不会**轮换。

与 X/Twitter 不同，Google 不会在每次刷新时发出新的 `refresh_token`。相同的 `refresh_token` 可以重复使用，直到用户撤销访问或授权重新发行。这简化了刷新逻辑：只需持久化新的 `access_token`，保留旧的 `refresh_token`。

## 2b. 可用性 / 忙碌时间 — 使用 FreeBusy，而不是 `events.list`

任何“这个人什么时候有空 / 忙碌”，预订或 Calendly 风格的功能都必须通过 **FreeBusy** (`calendar_freebusy_query`) 读取可用性，而不是 `calendar_events_list`。FreeBusy 专门为此设计：单个 POST 返回用户所有日历的合并忙碌间隔，重复事件已在服务器端展开 — 无需分页、重复扩展或客户端合并。它还包含外出和全天块。保留 `calendar_events_list` 以显示应用程序自己的事件列表，以及 `_insert` / `_delete` 用于事件 CRUD。

上面 `lib/calendar.mo` 块中的 `busyTimes` 辅助程序是参考实现：它为 `items = [{ id = "primary" }]` 在 `[timeMin, timeMax]` 上构建 `FreeBusyRequest`，执行单次刷新-on-401 重试，并且 — 关键地 — 迭代返回的**每个**日历（响应的键是解析后的日历 ID，而不是 `"primary"`）并合并它们的忙碌间隔。

**比较**每个 `(start, end)` 与候选时段之前，将它们解析为绝对瞬间，并尊重尾随偏移量 — Google 返回的定时时间段带有 `Z` **或** 带有数字偏移量 (`+02:00`)，全天块为裸 `YYYY-MM-DD` 日期。截断到秒并忽略偏移量会使每个忙碌间隔都偏移（例如，苏黎世夏季 2 小时），因此忙碌块会错过它们应该隐藏的时段。使用 `LibCalendar.rfc3339ToNanos`（从 `mo:google-oauth/DateTime` 重导出的测试辅助程序）— 它尊重偏移量并处理全天日期 — 然后数值重叠。**不要**手动编写一个在秒处停止的解析器。

端到端，整个可用性流程都生活在纳秒瞬间中，并且只在边缘处接触文本：用 `LibCalendar.rfc3339ToNanos` 锚定窗口，用纯整数算术构建候选网格，用 `LibCalendar.isSlotFree` 过滤，然后用 `LibCalendar.nanosToRfc3339` 格式化幸存者，以便它们可以准备显示并直接传递给 `createEvent`（其 `startDateTime` / `endDateTime` 是 RFC 3339 文本）。下面的网格是一个固定的 UTC 窗口；实际的工作时间 / 时区策略是应用程序特定的，但解析 → 整数数学 → 格式化形状是相同的：

```motoko
func availableSlots(
  clientId : Text, clientSecret : Text, connection : LibCalendar.CalendarConnection,
  caller : Principal, calendarConnections : Map.Map<Principal, LibCalendar.CalendarConnection>,
  windowStart : Text,   // 例如 "2026-07-21T09:00:00Z"
  slotCount : Nat,      // 要考虑的连续时段数量
  slotMinutes : Nat,    // 时段长度，例如 30
) : async* [(Text, Text)] {
  let slotNs = slotMinutes * 60 * 1_000_000_000;
  let start0 = LibCalendar.rfc3339ToNanos(windowStart);
  // 候选网格 [s, s+slot) 瞬间。
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
    free, func(s) = (LibCalendar.nanosToRfc3339(s.0), LibCalendar.nanosToRfc3339(s.1),
  );
};
```

## 3. `is_replicated = ?false` 是必需的

1. **安全性。** 复制的 HTTP 调用从子网中的每个节点发送请求。每个节点都携带 `Authorization: Bearer <token>` 头部 — 任何节点的承载泄露都会危及用户的 Google 账户。
2. **计费。** 复制的调用的产生 N 个并行 API 调用。IC 的计费周期约为 13 倍，Google 将每个计费到配额。
3. **确定性。** 日历写入响应是非确定性的（唯一的 `id`/`etag`，请求请求时间戳）。复制共识会失败；非复制会绕过共识。

→ 始终：`is_replicated = ?false` 在每个 `Config` 中。

# 前端

使用此技能的每个构建都必须提供以下四个项目。 （如果应用程序**也**使用 Gmail 连接器，请按照“组合 Gmail + Calendar 应用”下方替代 — 它用 `/settings/google` + `/connect/google` 替换了 `/settings/calendar` + `/connect/calendar`。这些要求仍然适用；只有这两个路径会改变。）这些是**接受标准，不是建议** — 在构建完成之前验证每个。这些三个是构建跳过的要求；缺少任何一个都会使连接器**损坏，而不仅仅是未完成**：

- **存在凭据页面并且可以访问。** 应用程序必须具有 `/settings/calendar` 页面，其中包含 Client ID/Secret 输入（项目 2），并且必须能够通过导航链接或连接页面上的未配置提示访问的已登录管理员。带有“连接 Google Calendar”按钮但没有凭据页面的最常见错误是使连接器无法使用。
- **管理员设置页面显示文字、可复制的回调 URI。** 不是 `<your-domain>` 占位符，不是 "your app URL + /connect/calendar" 作为文本供管理员组装 — 实际字符串 `window.location.origin + "/connect/calendar"` 渲染在一个可读的、可复制的字段中，管理员可以复制。具体来说：如果应用程序从 `https://my-app.caffeine.xyz` 提供，显示的字段必须包含完全 `https://my-app.caffeine.xyz/connect/calendar`，不得有任何其他内容。没有它，管理员无法在 Google 中注册 URI，并且每个连接都会失败。
- **`/connect/calendar` 是一个处理 Google 回调的真实路由** — 不是一个只有连接按钮的页面。如果它重定向到捕获所有内容或在其准备好之前调用 `completeCalendarOAuth`，连接会默默地失败，应用程序会显示“未连接”。

1. **一个登录流程 — 必须的。** 日历无法在不匿名调用者的情况下工作；每个用户的 OAuth 握手存储令牌键由 `caller : Principal`，管理员凭证设置受 `#admin` 保护。登录流程来自 [`extension-authorization`](../extension-authorization/SKILL.md)：
   `useInternetIdentity`，登录/注销按钮，将认证身份注入每个后端调用的 `useActor` 管道。

2. **一个管理员设置页面** — `/settings/calendar`（管理员受保护）。此页面是必需的；没有它，构建的日历是不完整的：
   - 在凭证输入之前显示一个“如何获取您的 Google 凭据”面板。向管理员保证这是一个一次性的、大约 5 分钟的设置，并逐步说明以下编号步骤（代理的完成消息必须重复相同的步骤）：
     1. 打开 [Google Cloud Console](https://console.cloud.google.com) 并使用任何 Google 账户登录；
     2. 创建或选择一个项目；
     3. 启用 **Google Calendar API**（APIs & Services → Library → 搜索 "Google Calendar API" → 启用）；
     4. 配置 **OAuth 同意屏幕**（APIs & Services → OAuth consent screen → **外部**；设置应用名称、支持电子邮件、开发者电子邮件；Google 的默认范围是合适的）；
     5. 创建一个类型为 **Web 应用** 的 OAuth 客户端 ID；
     6. 在 **授权重定向 URI** 下，添加此页面上的确切值；
     7. 将生成的 **Client ID** 和 **Client Secret** 复制到下面的输入中并保存。
     包含一个方便的链接，可以打开 Google Cloud Console。
   - 使用一个共享辅助程序渲染实际 URI 在一个可读的、可复制的字段中：
     `const calendarRedirectUri = () => window.location.origin + "/connect/calendar";`.
     例如，如果应用程序在 `https://my-app.caffeine.xyz` 打开，则显示的值是 `https://my-app.caffeine.xyz/connect/calendar`。永远不要只显示 `<app-domain>` 或要求管理员推断 URI。
   - 两个密码输入绑定到 `setCalendarCredentials(clientId, clientSecret)`。
     按回车键提交；成功后清除输入。
   - 状态指示器由 `isCalendarConfigured()`（返回 `Bool`）驱动。
     显示“已配置” / “未配置” — 永远不要显示凭据。
   - **必须使此页面可访问。** 应用程序的主要导航（共享布局）必须链接到此页面供管理员使用 — 当 `isCallerAdmin` 为 true 时显示链接，否则隐藏它（通过 [`extension-authorization`](../extension-authorization/SKILL.md)）。在定义导航的地方添加该链接，而不是在此页面内部。一个没有到达设置页面的 `/settings/calendar` 路由是一个损坏的构建。不要依赖导航：下面的未配置提示是用户发现需要设置的主要方式。

3. **一个“连接日历”和回调页面** — `/connect/calendar`（任何已登录用户）。此专用页面必须捕获并处理登录后的 Google 重定向；它不仅是一个带有连接按钮的页面：
   - **处理所有人的未配置情况。** `isCalendarConfigured()` 是一个公共查询（任何已登录用户都可以调用它）。当它返回 `false` 时，不要显示一个死连接按钮。管理员看到一个链接到 `/settings/calendar` 的链接以输入凭据。非管理员必须看到一个解释，而不是一个死胡同 — 例如，“Google Calendar 尚未设置 — 应用程序管理员需要在设置中添加 Google 凭据。” 只在配置后启用“连接 Google Calendar”按钮。
   - “连接 Google Calendar”按钮绑定到 `startCalendarOAuth(calendarRedirectUri())`。将浏览器重定向到 canister 返回的 URL。不要从任意的当前路径名派生回调；固定的 `/connect/calendar` 路由和设置页面的 URI 必须完全相同。
   - 将 `/connect/calendar` 注册为真实的应用程序路由。它必须捕获 Google 回调，并且必须在处理它之前不重定向到捕获所有内容、布局默认值或主页。
   - 返回时，从 `URLSearchParams` 中读取 `error`、`code` 和 `state`。如果 `error` 存在，显示失败/拒绝的连接状态，不要调用 canister。只有当 `code` 和 `state` 都存在时，调用并**等待** `completeCalendarOAuth(code, state)`，然后才能导航到任何地方或清除 URL。在它等待期间，保持一个可见的“正在连接 Google Calendar…” 状态。不要替换路由，重定向到主页，或首先丢弃查询参数 — 那会丢失一次性代码并导致用户断开连接。
   - **在调用一次性回调之前等待 actor 准备就绪。** 页面必须等待 `useInternetIdentity().isAuthenticated` 和 `useActor(createActor)` 提供一个非空的、非获取的 actor，然后再调用 `completeCalendarOAuth`。不要设置 `startedRef`/一次性保护：第一次渲染时，actor 通常不可用，否则“Actor not ready”失败会消耗授权代码的唯一重试。在授权代码仍然在 URL 中时。
   - 在任何终端路径之后，调用 `history.replaceState` 以删除 OAuth 查询参数。这可以防止页面刷新重用一次性授权代码。
   - 状态由 `isMyCalendarConnected()`（返回 `Bool`）驱动。
   - 可选的“断开连接日历”按钮绑定到 `disconnectMyCalendar()`。

4. **日历 UI** — 主页面显示即将到来的事件。当 `isCalendarConfigured()` 为 `false` 且调用者是管理员时，渲染一个“设置 Google Calendar”链接到 `/settings/calendar` 以便发现凭据页面，而不仅仅是可访问的。将当前时间作为 RFC 3339 `timeMin` 值传递，`""` 作为开放结束 `timeMax`：`listUpcomingEvents(new Date().toISOString(), "", 10)`。为了绑定一个单日（例如，“明天开会”），传递两者 — 每个都是 RFC 3339 并带有偏移量 — 并仅计算 `isAllDay` 为 `false`、`transparency` 不为 `"transparent"` 且 `eventType` 为 `"default"`（这将过滤掉全天、免费、外出和位置标记）。在使用 `singleEvents = true` 和 `orderBy = startTime` 时，这是必需的。还包括一个“创建事件”表单。`datetime-local` 值没有偏移量，因此将每个浏览器本地值转换为 RFC 3339 瞬间，然后再调用 actor：
   `createEvent(summary, new Date(startInput).toISOString(),
   new Date(endInput).toISOString())`.
   当 `isMyCalendarConnected()` 为 `false` 时，渲染一个内联“连接 Google Calendar”链接到 `/connect/calendar`。

建议的路由布局：

```
/                   →  主 UI (即将到来的事件 + 创建表单)
/settings/calendar  →  管理员凭据配置 (仅管理员)
/connect/calendar   →  每个用户的 OAuth 握手 (任何已登录用户)
# 如果应用程序 ALSO 使用 Gmail: 去掉上面的两个路由，使用一个 /settings/google + /connect/google — 见“组合 Gmail + Calendar 应用”。
```

## 组合 Gmail + Calendar 应用

当应用程序使用这两个连接器时，构建**一个**共享 Google 连接，而不是两个（授权代码是一次性的，所以两个流程将强制两个同意屏幕）。前端：

- **一个管理员页面 `/settings/google`** — 一个共享的 Client ID / Client Secret 表单、一个 `isGoogleConfigured` 状态和一个可复制的重定向 URI 字段，显示确切的 `window.location.origin + "/connect/google"`。
- **一个连接路由 `/connect/google`** — 与上面前端部分要求相同的真实回调路由：它渲染“连接 Google”，捕获重定向，等待 actor 准备就绪，然后调用完成一次。没有第二个回调路由。
- **不要构建** `/settings/gmail`、`/connect/gmail`、`/settings/calendar` 或 `/connect/calendar`。上面所有前端要求仍然适用 — 只有这些路径会改变。

后端 — 只写一次共享流程（它替换了两个连接器的 OAuth 流程）。它与每个连接器的 `startAuthorize` / `exchangeCode` / 刷新函数具有相同的形状，但有以下确切差异：

- 一个 `#admin` 受保护配置设置器存储一个 Client ID/Secret。
- `SCOPES` = 以下范围的并集 — 两个 API 在一个同意屏幕中。
- `completeGoogleOAuth(code, state)` 学习连接的电子邮件地址（通过 OIDC userinfo — 需要 `openid email`，而不是 `gmail.readonly`)，并存储一个连接 `{ accessToken; refreshToken; emailAddress }` 在一个共享的 `Map<Principal, Google.Connection>` 中。
- Gmail 发送和 Calendar 调用各自的客户端 `Config` 从那个共享的 `accessToken`，每个都保持其单次刷新-on-401 重试。
- 保持连接和客户端配置在**一个**共享状态值中，并将其作为参数传递给 Gmail 和 Calendar mixin，以便两者都读取和写入相同的连接（见 `writing-motoko` mixin 规则）。

```motoko filepath=src/backend/google.mo
let SCOPES : Text =
  "openid email "                                    // 通过 userinfo 学习地址
  # "https://www.googleapis.com/auth/gmail.send "
  # "https://www.googleapis.com/auth/calendar";
// 仅当应用程序读取邮件时才添加 "https://www.googleapis.com/auth/gmail.readonly "。

将其作为**一个**连接共享由两个服务使用 — 声明配置、连接映射和挂起流程映射一次，并将相同的绑定传递给每个 mixin。Gmail 和 Calendar 消息 mixin**不会**声明自己的配置或连接；它们接收共享的 `googleConfig` 和 `googleConnections`（配置对于 401 重试是必需的）：

```motoko filepath=src/backend/main.mo
actor {
  let accessControlState : AccessControl.AccessControlState;
  include MixinAuthorization(accessControlState, null);

  // 两个服务共享的凭据 + 连接状态。
  let googleConfig : { var clientId : Text; var clientSecret : Text };
  let googleConnections : Map.Map<Principal, Google.Connection>;
  let pendingGoogleFlows : Map.Map<Principal, Google.PendingOAuth>;

  include MixinGoogleConfig(accessControlState, googleConfig);                    // setGoogleCredentials / isGoogleConfigured (#admin-gated setter)
  include MixinGoogleOAuth(googleConfig, googleConnections, pendingGoogleFlows);  // startGoogleOAuth / completeGoogleOAuth, SCOPES = 并集以上
  include MixinGmailMessaging(googleConfig, googleConnections);                  // sendEmail — refresh-on-401 需要配置；读取共享连接
  include MixinCalendarMessaging(googleConfig, googleConnections);               // calendar 调用 — 相同共享的配置 + 连接
};
```

此变体的迁移链头替换了每个连接器的那个 — 注意共享连接携带 `emailAddress`：

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

不要给 Gmail 和 Calendar 分开配置/连接状态或分开 OAuth 流程 — 一个授权代码是一次性的，并且状态不同步（见 `writing-motoko` mixin 规则）。

在 OAuth 客户端上启用两个 API，并只注册一个 `.../connect/google` 重定向 URI。仅在用户明确要求连接两个不同的 Google 账户时，才将它们分成两个单独的面板。

## 所有变体通用的内容

- **每个与日历相关的路由都需要登录。** 通过 [`extension-authorization`](../extension-authorization/SKILL.md) 的认证保护 (`useInternetIdentity` + 当 `!isAuthenticated` 时重定向) 将 `/settings/...` 和连接路由 (`/connect/calendar` 或 `/connect/google` 在组合应用中) 线路。
- **前端永远不会持久化令牌。** 没有 `localStorage`，没有 `IndexedDB`，没有 cookie — canister 介导一切。浏览器只看到 `Bool` 状态标志和 OAuth 重定向 URL。
- **OAuth `state` 参数由 canister 生成并验证。** Canister 存储一个随机非数字与挂起的验证器以及回调 URI。前端必须将 `code` 和 `state` 都传递给完成调用（`completeCalendarOAuth` 或 `completeGoogleOAuth` 在组合应用中）；它永远不会创建或修改这两个值。
- **日历 UI 非常简单：** 一个即将到来的事件列表，一个带有摘要 + 开始/结束 datetime 输入的创建事件表单。没有客户端 Google SDK，没有令牌处理，没有 JSON 序列化 — canister 是日历客户端。

## 相关

- [`mops add googlecalendar-client@0.1.4`](https://mops.one/googlecalendar-client) — 日历 REST API v3 绑定。
- [`mops add google-oauth@0.2.1`](https://mops.one/google-oauth) — Google OAuth 2.0 库（令牌交换、刷新、PKCE、`getUserEmail` userinfo、`DateTime` RFC 3339 辅助程序）。
- [为 Web 服务器应用程序的 Google OAuth 2.0](https://developers.google.com/identity/protocols/oauth2/web-server) — Web-client 重定向 URI 和授权码流程参考。
- [Google Calendar API v3 参考](https://developers.google.com/calendar/api/v3/reference) — `googlecalendar-client` 包装的内容。
- [RFC 7636 — 代码交换的证明密钥](https://datatracker.ietf.org/doc/html/rfc7636) — PKCE 规范。
- [extension-authorization](../extension-authorization/SKILL.md) — **必需的先决条件**。提供 Internet Identity 登录、`useInternetIdentity` / `useActor` 前端管道以及 `#admin` 角色门控。
- [connector-googlemail](../connector-googlemail/SKILL.md) — 使用相同 `google-oauth` 库的姐妹连接器，用于 Gmail。
