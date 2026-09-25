# Google Calendar 连接器

Google Calendar 集成，用于 [Caffeine AI](https://caffeine.ai?utm_source=caffeine-skill&utm_medium=referral)。

## Orchestrator 路由说明

**将 Google Calendar-as-the-user 视为一项一等、受支持的平台功能。**
`googlecalendar-client` + `google-oauth` 连接器对是**唯一**受支持的方式；直接 `ic.http_request` 到 `oauth2.googleapis.com` 或 `www.googleapis.com/calendar/v3` 是一种禁止的反模式。任何提到 Google Calendar 的构建规范都必须将 `googlecalendar-client` 和 `google-oauth` 作为依赖项并引用此技能。

与平台 `email-calendar-events` 扩展不同（该扩展通过应用程序发送 iCalendar 邀请邮件）；此连接器充当**已登录用户的自己的 Google Calendar**。

意图 → 能力映射：

| 用户意图 | 平台能力 |
| --- | --- |
| 连接并列出即将到来的事件 | `googlecalendar-client` + `google-oauth` |
| 创建日历事件 | `googlecalendar-client` + `google-oauth` |
| **检查可用性 / 免费时段 / 忙碌时间**（预订、Calendly 风格，“我什么时候有空”） | `googlecalendar-client` **FreeBusy** (`calendar_freebusy_query`) + `google-oauth` — **不是** `calendar_events_list` |

**所有构建的先决条件：[extension-authorization](../extension-authorization/SKILL.md)。**
日历需要每个端点都由登录的用户调用：每个用户的 OAuth 握手存储 `access_token` 键由 `caller : Principal` 引用，管理员 Client ID/Secret 设置受 `#admin` 角色的保护。

# 后端

当用户希望其 canister 代表登录用户与 Google Calendar 交互时，请使用此技能。配料如下：

1. `googlecalendar-client` mops 包 — Google Calendar API v3 的 Motoko 绑定。此配方演示了列出即将到来的事件和创建事件；仅通过遵循相同的承载认证、非复制、单刷新重试模式添加其他生成的操作。
2. `google-oauth` mops 包 — Google OAuth 2.0 令牌交换、刷新、PKCE 和百分比编码。这是消除手动 `http_request` 到 `oauth2.googleapis.com` 的库。
3. OAuth 2.0 授权码与 PKCE 流程，以便每个最终用户授权 canister 代表其行事。每个用户都持有自己的 `access_token` + `refresh_token`，键由 `caller : Principal` 引用。
4. Google Cloud **Web 应用** Client ID + Client Secret。管理员配置并由 canister 仅持有；永远不要将密钥返回前端。

## 1. 添加依赖项

```bash
mops add googlecalendar-client@0.2.0
mops add google-oauth@0.2.1
mops add caffeineai-authorization@1.0.1
```

## 2. 认证模型 — 每个用户的 OAuth 2.0 PKCE，链上交换 + 刷新

与 Gmail 连接器相同。每个最终用户都通过授权码与 PKCE 流程独立授权 canister。Canister：

1. 生成 PKCE `code_verifier` 和 `code_challenge`（通过 `google-oauth`）。
2. 构建 Google 授权 URL（通过 `google-oauth.buildAuthorizeUrl`）。
3. 前端将用户重定向到 Google；在同意后，Google 会带有 `code` 参数的重定向回。
4. Canister 交换代码以获取令牌（通过 `google-oauth.exchangeAuthorizationCode`）— **链上**，非复制。
5. Canister 存储由 `caller` 键控的 `access_token` + `refresh_token`。
6. 当 1 小时访问令牌过期（HTTP 401），canister 静默刷新它（通过 `google-oauth.refreshAccessToken`）并重试。

### Google Cloud Console 设置

1. 创建 Google OAuth 2.0 **Web 应用** 客户端。
2. 应用程序的日历设置页面必须在可复制的字段中显示此字面值回调 URI：`window.location.origin + "/connect/calendar"` — 例如，`https://my-app.caffeine.xyz/connect/calendar`。应用程序管理员必须手动将显示的值复制到 Google Cloud Console 下的 **授权重定向 URI** 中。将每个部署的 origin（用户可以连接日历的地方，例如草稿和活动应用程序 origin）注册为单独的授权重定向 URI。
3. 仅在同意屏幕上启用应用程序需要的日历范围。
4. 通过应用程序的 admin 设置页面输入 Client ID 和 Client Secret。Canister 使用密钥进行令牌交换；前端绝不能接收密钥。

PKCE 将每个授权码绑定到 canister 生成的验证器，而 Web 客户端注册将浏览器回调绑定到部署的应用程序。传递给 `startCalendarOAuth` 的回调 URI 必须与设置页面显示的值完全相同。使用固定的 `window.location.origin + "/connect/calendar"` 作为 `redirectUri` — 该值由设置页面显示并由 `/connect/calendar` 路由拥有 — 并在 Google Web 客户端中注册该确切 URI。不要从 `window.location.pathname` 构建，它因页面而异。

将显示的值不变地传递给 `startCalendarOAuth` — 永远不要传递原始 `*.icp0.io` canister URL。Caffeine 应用程序在多个 origin 上提供服务（草稿 `*-draft.caffeine.xyz` 草稿，活动 `*.caffeine.xyz` 域，以及原始 `<canister-id>.icp0.io` URL）。在 **一个** 共享帮助程序中计算重定向 URI（`window.location.origin + "/connect/calendar"`），并使用相同的帮助程序用于设置页面上的可复制字段和传递给 `startCalendarOAuth` 的值。如果传递给 Google（通过 `startCalendarOAuth`）的值与设置页面显示的值和管理员注册的值不同（例如，构建时/配置值或 `*.icp0.io` canister origin），Google 返回 `redirect_uri_mismatch`。

### OAuth 范围

| 范围 | 目的 |
| --- | --- |
| `https://www.googleapis.com/auth/calendar` | 完全访问日历的读写权限 |
| `https://www.googleapis.com/auth/calendar.events` | 仅事件的读写权限 |
| `https://www.googleapis.com/auth/calendar.readonly` | 只读访问日历的权限 |
| `https://www.googleapis.com/auth/calendar.events.readonly` | 只读访问事件的权限 |

为典型的 CRUD 应用程序请求 `calendar`（完全读写），对于只读视图使用 `.readonly` 变体。

### 存储令牌

承载**永远不会离开 canister**。前端只学习调用者是否已连接（一个 `Bool`），永远不会获得令牌本身。

- 一个 `Map<Principal, CalendarConnection>` 由 `caller` 键控。仅公开 §4 中列出的端点 — `isMyCalendarConnected`、`startCalendarOAuth`、`completeCalendarOAuth`、`listUpcomingEvents`、`createEvent`、`disconnectMyCalendar` — 每个端点都受 `not caller.isAnonymous()` 限制。
- **不要添加任何返回 `access_token` / `refresh_token` / 完整 `CalendarConnection` 的端点。**
- 存储每个调用者的一个挂起的 OAuth 流程：PKCE `code_verifier`、确切的 `redirectUri` 和一个随机的 `state` 非零值。当回调完成时消耗它；不要接受来自前端的替换重定向 URI。

### Google 刷新令牌不会旋转

与 X/Twitter 不同，Google 不会在每次刷新时旋转 `refresh_token`。相同的 `refresh_token` 可以重复使用，直到用户撤销访问或授权重新发行。这简化了刷新逻辑：只需持久化新的 `access_token`，保留旧的 `refresh_token`。

## 2b. 可用性 / 忙碌时间 — 使用 FreeBusy，而不是 `events.list`

任何“这个人什么时候有空/忙碌”，预订或 Calendly 风格的功能都必须通过 **FreeBusy** (`calendar_freebusy_query`) 读取可用性，而不是 `events.list`。FreeBusy 专为这个目的而设计：单个 POST 返回用户所有日历的合并忙碌间隔，重复事件已在服务器端展开 — 你永远不会分页浏览事件、展开重复事件或手动合并重叠块。它还包含外出和全天块。保留 `calendar_events_list` 以显示应用程序自己的事件列表，以及 `*_insert` / `*_delete` 用于事件 CRUD。

`lib/calendar.mo` 块中的 `busyTimes` 帮助程序是参考实现：它为 `items = [{ id = "primary" }]` 在 `[timeMin, timeMax]` 上构建 `FreeBusyRequest`，执行单刷新重试，并且 — 关键的是 — 迭代返回的**每个**日历（响应的 map 由解析的日历 ID 引用，而不是 `"primary"`）并合并它们的 `busy` 间隔。将每个间隔的 `start`/`end` 解析为 RFC 3339，允许带有尾随 `Z` 或数字偏移 (`+02:00`) 的绝对瞬间；比较瞬间，而不是原始字符串。

**在比较每个 `(start, end)` 与你的候选时段之前，使用 `LibCalendar.rfc3339ToNanos`（从 `mo:google-oauth/DateTime` 重导出的）解析 RFC 3339 — 不要重新实现它。** 手动编写的解析器会忘记减去 `'0'`（48）每个数字，将 `"2026"` 解析为 `55354`，因此每个忙碌间隔都会落在错误的年份，重叠检查永远不会匹配，并且可用性会无声地出错 — 代码仍然可以编译并且永远不会捕获，因此该错误对用户来说是无形的，直到用户被双重预订。

**HTTP 429 速率限制。** 向调用者显示错误；永远不要在 canister 内部无声重试写入 — 重试可能会创建重复事件。

**不要暴露访问令牌。** `calendarConnections` 仅在 API 调用中由 `Map.get(calendarConnections, ..., caller)` 引用。没有 `getMyCalendarConnection`，没有 `getMyAccessToken`，没有迭代器。泄露承载会危及用户的每个用户帐户。

- **`alt = ?#json`** 对于所有 Google Calendar API v3 调用（之前为裸 `#json`）。保留可选字符串参数 `""` 和 `prettyPrint = false`。

**查询参数是位置参数，并且自 0.2.0 起，可选的 *枚举* 参数是 `?T`。** 将 `Text` 作为 `""`，`Bool` 作为 `false`，`Nat` 作为实际数字（尊重每个文档的最小值：`maxAttendees` / `maxResults` 必须≥ 1），并将可选枚举作为 `?#json` / `?#starttime` / `?#all` — 或者 `null` 以省略它们，这正是 `?` 的用途。非枚举参数仍然不接收 `null`。模型值（`Event`、`EventDateTime`、`FreeBusyRequest`）直接作为之前传递。

- **组合 Gmail + Calendar 应用程序：请求范围并集，并学习地址通过 `OAuth.getUserEmail`。** `openid email` + `.../calendar` + `.../gmail.send` 的并集涵盖了可用性、发送和连接的地址（通过 OIDC userinfo）— 不需要 `gmail.readonly`，除非应用程序实际读取邮件。合并配方时**永远不要**丢弃范围 — 请参阅“组合 Gmail + Calendar 应用程序”。

- **构建 `Event` / `EventDateTime` 使用 `init {}` 然后记录更新** 您需要的字段 — 所有字段都是可选的 (`?T`)；将不需要的保留为 null。

- **PATCH/PUT/DELETE 在生成的客户端中是强制非复制的**（`googlecalendar-client` 将 `is_replicated = ?false` 自动应用于这些方法）。对于 GET/POST，在您的 `Config` 中显式设置它。

# 前端

使用此技能构建的每个构建都必须提供以下四个项目。 （如果应用程序**也**使用 Gmail 连接器，请按照“组合 Gmail + Calendar 应用程序”下方的内容操作 — 它用 `/settings/calendar` + `/connect/calendar` 替换为单个 `/settings/google` + `/connect/google`。以下要求仍然适用；仅这两个路径发生变化。）这些是**验收标准，不是建议** — 在构建完成之前验证每个。这些是构建跳过的要求；缺少任何一个都会使连接器**损坏，而不仅仅是未完成**：

- **存在凭据页面并且可以访问。** 应用程序必须具有 `/settings/calendar` 页面，其中包含 Client ID/Secret 输入（项目 2），并且必须能够通过导航链接或连接页面上的未配置提示访问该页面的已登录管理员。带有“连接 Google Calendar”按钮但没有凭据页面的最常见错误是使连接器无法使用。

- **管理员设置页面显示字面值、可复制的重定向 URI。** 不是 `<your-domain>` 占位符，不是“你的应用程序 URL + /connect/calendar”作为文本供管理员组装 — 实际字符串 `window.location.origin + "/connect/calendar"` 渲染在可复制的只读字段中，管理员可以复制。具体来说：如果应用程序在 `https://my-app.caffeine.xyz` 上提供服务，则显示的值必须是 `https://my-app.caffeine.xyz/connect/calendar`，不能有其他内容。没有它，管理员无法在 Google 中注册 URI，并且每个连接都会失败。

- **`/connect/calendar` 是一个处理 Google 回调的真实路由** — 不是一个只有按钮的页面。如果它重定向到捕获所有重定向或调用 `completeCalendarOAuth` 之前认证的 actor，连接会无声失败，应用程序会显示“未连接”。

1. **一个登录流程 — 必须有。** 日历无法在没有非匿名调用者的情况下工作；每个用户的 OAuth 握手存储令牌键由 `caller : Principal` 引用，并且管理员凭据设置受 `#admin` 角色保护。登录流程来自 [`extension-authorization`](../extension-authorization/SKILL.md)：`useInternetIdentity`，登录/注销按钮，将认证身份注入到每个后端调用的 `useActor` 管道。

2. **一个管理员设置页面** — `/settings/calendar`（管理员受保护）。此页面是必需的；没有日历构建是不完整的： - 在凭据输入之前显示一个“如何获取您的 Google 凭据”面板。向管理员保证这是一个一次性的、大约 5 分钟的设置，并逐步介绍以下编号步骤（代理的完成消息必须重复相同的步骤）： 1. 打开 [Google Cloud Console](https://console.cloud.google.com) 并使用任何 Google 帐户登录； 2. 创建或选择一个项目； 3. 启用 **Google Calendar API**（APIs & Services → Library → 搜索“Google Calendar API”→ 启用）； 4. 配置 **OAuth 同意屏幕**（APIs & Services → OAuth consent screen → **外部**；设置应用程序名称、支持电子邮件、开发者电子邮件；Google 的默认范围是足够的）； 5. 创建一个 **类型为 Web application** 的 OAuth 客户端 ID； 6. 在 **授权重定向 URI** 下，添加从可复制字段中获取的确切值； 7. 将生成的 **Client ID** 和 **Client Secret** 复制到下面的输入中并保存。 包含一个方便的链接，打开 Google Cloud Console。 - 使用一个共享帮助程序渲染实际 URI 在可复制的只读字段中：`const calendarRedirectUri = () => window.location.origin + "/connect/calendar";`。例如，如果应用程序在 `https://my-app.caffeine.xyz` 上打开，则显示的值是 `https://my-app.caffeine.xyz/connect/calendar`。永远不要只显示 `<app-domain>` 或要求管理员推断 URI。 - 两个密码输入绑定到 `setCalendarCredentials(clientId, clientSecret)`。按 Enter 提交；成功后清除输入。 - 状态指示器由 `isCalendarConfigured()`（返回 `Bool`）驱动。显示“已配置”/“未配置” — 永远不要显示凭据。 - **确保此页面可访问。** 应用程序的主导航（共享布局）必须链接到此页面，当 `isCallerAdmin` 为 true 时显示链接，否则隐藏它（通过 [`extension-authorization`](../extension-authorization/SKILL.md)）。在定义导航的地方添加该链接，而不是在此页面内。一个没有到达设置页面的 `/settings/calendar` 路由是一个损坏的构建。不要依赖导航：未配置提示是用户发现设置需要的主要方式。

3. **一个“连接日历”和回调页面** — `/connect/calendar`（任何已登录用户）。此专用页面必须捕获并处理 Google 在同意后的重定向；它不仅是一个带有连接按钮的页面： - **处理未配置的情况。** `isCalendarConfigured()` 是一个公共查询（任何已登录用户都可以调用它）。当它返回 `false` 时，不要显示一个死的连接按钮。管理员看到一个指向 `/settings/calendar` 的链接以输入凭据。非管理员必须看到一个解释，而不是一个终点 — 例如，“Google Calendar 尚未设置 — 应用程序管理员需要在设置中添加 Google 凭据。” 只在配置后启用“连接 Google Calendar”按钮。 - “连接 Google Calendar”按钮绑定到 `startCalendarOAuth(calendarRedirectUri())`。将浏览器重定向到 canister 返回的 URL。不要从任意的当前路径派生回调；固定的 `/connect/calendar` 路由和设置页面 URI 必须完全相同。 - 将 `/connect/calendar` 注册为真实的应用程序路由。它必须捕获 Google 回调，并且处理它之前不会重定向到捕获所有重定向、布局默认值或主页。 - 在返回端，从 `URLSearchParams` 中读取 `error`、`code` 和 `state`。如果 `error` 存在，则显示失败的/拒绝的连接状态，并且不要调用 canister。只有当 `code` 和 `state` 都存在时，才调用并**等待** `completeCalendarOAuth(code, state)`，然后才能导航到任何地方或清除 URL。在它等待时保持可见的“正在连接 Google Calendar…”状态。不要替换路由，重定向到主页，或首先丢弃查询参数 — 那会丢失一次性代码并导致用户断开连接。 - **在调用一次性回调之前等待 actor 准备就绪。** 页面必须等待 `useInternetIdentity().isAuthenticated` 和 `useActor(createActor)` 提供一个非空的、非抓取的 actor，然后才能调用 `completeCalendarOAuth`。不要设置 `startedRef`/一次性保护：第一次渲染时 actor 通常不可用，否则“actor 不可用”失败会消耗唯一的重试，而授权代码仍然在 URL 中。 - 完成任何最终路径后，调用 `history.replaceState` 以删除 OAuth 查询参数。这防止页面刷新重用一次性授权代码。 - 状态由 `isMyCalendarConnected()`（返回 `Bool`）驱动。 - 可选的“断开连接日历”按钮绑定到 `disconnectMyCalendar()`。

4. **日历 UI** — 主页面显示即将到来的事件。当 `isCalendarConfigured()` 为 `false` 且调用者是管理员时，渲染一个指向 `/settings/calendar` 的“设置 Google Calendar”链接，以便可发现凭据页面，而不仅仅是可访问的。将当前时间作为 RFC 3339 `timeMin` 值传递，`""` 作为开放结束 `timeMax`：`listUpcomingEvents(new Date().toISOString(), "", 10)`。要绑定单个天（例如，“明天开会”），请传递两者——本地天的开始和下一天的开始，每个都是带有偏移的 RFC 3339）并仅计算 `isAllDay` 为 false 且 `transparency` 不是 `"transparent"` 且 `eventType` 为 `"default"`（这将过滤掉全天、免费、外出和工位标记）。当使用 `singleEvents = true` 和 `orderBy = startTime` 时，这是必需的。还包括一个“创建事件”表单。`datetime-local` 值没有偏移，因此在对 actor 调用之前将每个浏览器本地值转换为 RFC 3339 瞬间：`createEvent(summary, new Date(startInput).toISOString(), new Date(endInput).toISOString())`。当 `isMyCalendarConnected()` 为 `false` 时，渲染一个内联“连接 Google Calendar”链接到 `/connect/calendar`。

建议的路由布局：

```
/                   →  主 UI（即将到来的事件 + 创建表单）
/settings/calendar  →  管理员凭据配置（仅管理员）
/connect/calendar   →  每个用户的 OAuth 握手（任何已登录用户）
# 如果应用程序也使用 Gmail：删除上述两个路由，并使用单个
# /settings/google + /connect/google — 请参阅“组合 Gmail + Calendar 应用程序”。
```

## 组合 Gmail + Calendar 应用程序

当应用程序使用这两个连接器时，构建**一个**共享的 Google 连接，而不是两个（授权码是一次性的，所以两个流会强制两个同意屏幕）。前端：

- **一个管理员页面 `/settings/google`** — 一个 Client ID / Client Secret 表单，一个 `isGoogleConfigured` 状态，和一个显示确切 `window.location.origin + "/connect/google"` 的可复制重定向 URI 字段。
- **一个连接路由 `/connect/google`** — 与上面前端部分要求相同的真实回调路由：它渲染“连接 Google”，捕获重定向，等待 actor 准备就绪，然后调用完成一次。没有第二个回调路由。
- **不要构建** `/settings/gmail`、`/connect/gmail`、`/settings/calendar` 或 `/connect/calendar`。上述前端要求中的所有其他要求仍然适用 — 仅这些路径发生变化。

后端 — 写入共享流程**一次**（它替换了每个连接器的 OAuth 流程）。它与每个连接器的 `startAuthorize` / `exchangeCode` / 刷新函数的形状相同，但有以下确切差异：

- 一个 `#admin` 受保护配置设置器存储单个 Client ID/Secret。
- `SCOPES` = 下方并集 — 两个 API 在一个同意屏幕中。- `completeGoogleOAuth(code, state)` 学习连接的电子邮件地址（通过 OIDC userinfo — 需要 `openid email`，不需要 `gmail.readonly`) 并存储一个包含 `accessToken; refreshToken; emailAddress` 的 `{}` 在单个 `Map<Principal, Google.Connection>` 中。
- Gmail 发送和 Calendar 调用各自的客户端 `Config` 从该 `accessToken`，每个都保持其单刷新重试 `on-401` 重试。
- 将连接和客户端配置保留在**一个**共享状态值中，并将其作为参数传递给 Gmail 和 Calendar 混合，以便两者都读取和写入相同的连接（见 `writing-motoko` 混合规则）。

```motoko filepath=src/backend/google.mo
let SCOPES : Text =
  "openid email "                                    // 学习地址通过 userinfo
  # "https://www.googleapis.com/auth/gmail.send "
  # "https://www.googleapis.com/auth/calendar";
// 仅当应用程序读取邮件时才添加 "https://www.googleapis.com/auth/gmail.readonly "。
```

将其作为**一个**连接共享由两个服务使用 — 声明配置、连接映射和挂起流程映射一次，并将相同的绑定传递给每个混合。Gmail 和 Calendar 消息混合**不会**声明自己的配置或连接；它们接收共享的 `googleConfig` 和 `googleConnections`（配置对于 401 重试是必需的）：

```motoko filepath=src/backend/main.mo
actor {
  let accessControlState : AccessControl.AccessControlState;
  include MixinAuthorization(accessControlState, null);

  // 两个服务共享的凭据 + 连接状态。
  let googleConfig : { var clientId : Text; var clientSecret : Text };
  let googleConnections : Map.Map<Principal, Google.Connection>;
  let pendingGoogleFlows : Map.Map<Principal, Google.PendingOAuth>;

  include MixinGoogleConfig(accessControlState, googleConfig);                    // setGoogleCredentials / isGoogleConfigured (#admin-gated setter)
  include MixinGoogleOAuth(googleConfig, googleConnections, pendingGoogleFlows);  // startGoogleOAuth / completeGoogleOAuth, SCOPES = 上面并集
  include MixinGmailMessaging(googleConfig, googleConnections);                  // sendEmail — refresh-on-401 需要配置; 读取共享连接
  include MixinCalendarMessaging(googleConfig, googleConnections);               // calendar 调用 — 相同共享配置 + 连接
};
```

这个变体的迁移链头替换了每个连接器的迁移链 — 注意共享连接携带 `emailAddress`：

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

不要给 Gmail 和 Calendar 分开配置/连接状态或分开的 OAuth 流程 — 一个授权码是一次性的，并且分离的 state 失同步（见 `writing-motoko` 混合规则）。

在单个 OAuth 客户端上启用两个 API，并只注册单个 `.../connect/google` 重定向 URI。仅在用户明确要求连接两个不同的 Google 帐户时才将它们分成两个单独的面板。

## 所有变体通用的内容

- **每个日历相关路由都需要登录。** 通过 [`extension-authorization`](../extension-authorization/SKILL.md)'s 认证保护 (`useInternetIdentity` + 当 `!isAuthenticated` 时重定向) 将 `/settings/...` 和连接路由 (`/connect/calendar` 或 `/connect/google` 在组合应用程序中) 链接起来。
- **前端永远不会持久化令牌。** 没有 `localStorage`，没有 `IndexedDB`，没有 cookie — canister 介导一切。浏览器只看到 `Bool` 状态标志和 OAuth 重定向 URL。
- **OAuth `state` 参数由 canister 生成并验证。** Canister 存储一个随机非零值与挂起的验证器以及回调 URI。前端必须将 `code` 和 `state` 都传递给完成调用（`completeCalendarOAuth` 或 `completeGoogleOAuth` 在组合应用程序中）；它永远不会创建或修改任何值。
- **日历 UI 非常简单：** 一个即将到来的事件列表，一个带有摘要 + 开始/结束 datetime 输入的创建事件表单。没有客户端 Google SDK，没有令牌处理，没有 JSON 序列化 — canister 是日历客户端。

## 相关

- [`mops add googlecalendar-client@0.2.0`](https://mops.one/googlecalendar-client) — 日历 REST API v3 绑定。
- [`mops add google-oauth@0.2.1`](https://mops.one/google-oauth) — Google OAuth 2.0 库（令牌交换、刷新、PKCE、`getUserEmail` userinfo、`DateTime` RFC 3339 帮助程序）。
- [Google OAuth 2.0 for Web Server Applications](https://developers.google.com/identity/protocols/oauth2/web-server) — Web-client 重定向 URI 和授权码流程参考。
- [Google Calendar API v3 reference](https://developers.google.com/calendar/api/v3/reference) — `googlecalendar-client` 包装的 API。
- [RFC 7636 — 代码交换的证明密钥](https://datatracker.ietf.org/doc/html/rfc7636) — PKCE 规范。
- [extension-authorization](../extension-authorization/SKILL.md) — **必需的先决条件**。提供 Internet Identity 登录、`useInternetIdentity` / `useActor` 前端管道和 `#admin` 角色门控。
- [connector-googlemail](../connector-googlemail/SKILL.md) — 使用相同 `google-oauth` 库的姐妹连接器，用于 Gmail。
